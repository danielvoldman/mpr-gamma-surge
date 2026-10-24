"""MS10 10d: evaluator tests on SYNTHETIC fixtures only (no real network record is read; none exists at 10d).

Records are written to tmp_path from rows of the frozen run lists with synthetic v series (white noise, a 50 Hz burst); the evaluators are then driven
with fake per-run dicts for the counting logic. Every E-n choice used below is a TEST FIXTURE, not a choice of the project.
"""
import copy
import json

import numpy as np
import pytest

from mprsurge.analysis import a7 as A7
from mprsurge.analysis import ms10_eval as E
from mprsurge.analysis import ms10_runlist as RL
from mprsurge.analysis import surge_metrics as M

FI = A7.frozen_inputs()[0]
FR = E.frozen_rb1()
CH = {"network_onset_definition": "classifier_centre", "not_evaluable_counts_as": "not_met", "tolerance_boundary": "inclusive",
      "baseline_sample_convention": "half_open", "sigma_range_bounds": "inclusive", "s9_metrics": ["onset_s", "f_pk_hz", "baseline_std_v"],
      "rb8_comparator": "paired_by_seed_index", "rb8_class_equality": "exact_label", "g4_source_lists": ["S9"],
      "mf_baseline_std": 0.0389, "mf_baseline_std_source": "TEST FIXTURE"}
T = np.arange(92_000) / 1000.0


def _v(kind, seed=0):
    rng = np.random.default_rng(seed)
    noise = 0.04 * rng.standard_normal(T.size)
    if kind == "NS":
        return noise
    if kind == "sus":
        return noise + np.where(T > 20, 0.3, 0.0) * np.sin(2 * np.pi * 50 * T)
    if kind == "tr":
        return noise + np.where((T > 20) & (T < 40), 0.3, 0.0) * np.sin(2 * np.pi * 50 * T)
    raise ValueError(kind)


def _write(row, v, tmp_path, **over):
    row = dict(row, out_dir=str(tmp_path / row["family"]))
    d = tmp_path / row["family"]
    d.mkdir(parents=True, exist_ok=True)
    rec = {"config": row["cfg"], "config_hash": row["hash"], "name": row["name"], "criteria_sha256": FI["criteria_sha256"], "git": {"dirty": False, "commit": "x"},
           "dry_run": False, "status": "ok", "wall_time_s": 1.0}
    rec.update(over)
    (d / f"{row['name']}.json").write_text(json.dumps(rec), encoding="utf-8")
    np.savez(d / f"{row['name']}.npz", v=v)
    return row


def _row():
    return RL.expand("S10")[0]


# --- refusals -------------------------------------------------------------------------------------------------

def test_a_record_with_git_dirty_true_is_refused(tmp_path):
    row = _write(_row(), _v("NS"), tmp_path, git={"dirty": True, "commit": "x"})
    with pytest.raises(E.EvalRefused, match="dirty"):
        E.read_record(row, FI)


def test_a_record_without_a_dirty_flag_is_refused(tmp_path):
    row = _write(_row(), _v("NS"), tmp_path, git={"commit": "x"})
    with pytest.raises(E.EvalRefused, match="dirty"):
        E.read_record(row, FI)


def test_a_record_whose_config_hash_differs_from_the_frozen_list_is_refused(tmp_path):
    row = _write(_row(), _v("NS"), tmp_path, config_hash="0" * 64)
    with pytest.raises(E.EvalRefused, match="config hash"):
        E.read_record(row, FI)


def test_a_dry_run_record_or_a_foreign_criteria_hash_is_refused(tmp_path):
    with pytest.raises(E.EvalRefused, match="dry-run"):
        E.read_record(_write(_row(), _v("NS"), tmp_path, dry_run=True), FI)
    with pytest.raises(E.EvalRefused, match="criteria"):
        E.read_record(_write(_row(), _v("NS"), tmp_path, criteria_sha256="f" * 64), FI)


def test_draft_data_files_are_refused(monkeypatch):
    monkeypatch.setattr(RL, "is_draft", lambda: True)
    with pytest.raises(E.EvalRefused, match="DRAFT"):
        E.expected_rows(("S10",))


def test_an_unlisted_record_in_a_family_folder_is_refused(tmp_path, monkeypatch):
    rows = [dict(r, out_dir=str(tmp_path / "S10")) for r in RL.expand("S10")]
    for r in rows:
        _write(r, _v("NS"), tmp_path)
    stray = dict(rows[0], name="S10_0099_deadbeef0000")
    _write(stray, _v("NS"), tmp_path)
    monkeypatch.setattr(E, "expected_rows", lambda lists, require_frozen=True: {"S10": rows})
    with pytest.raises(E.EvalRefused, match="not rows of the frozen lists"):
        E.read_lists(("S10",), FI)


def test_a_missing_record_is_reported_not_replaced(tmp_path):
    r = E.read_record(dict(_row(), out_dir=str(tmp_path / "none")), FI)
    assert r["missing"] is True


# --- choices ---------------------------------------------------------------------------------------------------

def test_every_open_choice_is_null_in_the_shipped_config_and_errors_when_missing():
    ch = E.load_choices()
    assert all(v is None for v in ch.values())
    assert set(ch) == set(E.CHOICE_VALUES) | {"s9_metrics", "g4_source_lists", "mf_baseline_std", "mf_baseline_std_source"}
    for name in E.CHOICE_VALUES:
        with pytest.raises(E.MissingChoice):
            E.choice(ch, name)
    with pytest.raises(E.MissingChoice):
        E.choice({"tolerance_boundary": "maybe"}, "tolerance_boundary")


def test_evaluators_stop_on_a_missing_choice():
    rec = _fake("S-sus", 0)
    ref = {"class": "D-tr", "onset_s": 20.0, "f_pk_hz": 50.0}
    for fn in (lambda: E.onset_of(rec, {}), lambda: E.seed_assessment(rec, ref, {}, 0.05), lambda: E.sigma_check([rec], {}),
               lambda: E.rb8([], [], ref, {}, FR), lambda: E.g4_summary({}, {"verdict": "PASS"}, {}, {}),
               lambda: E.n_sweep([rec], ref, [], {"s9_metrics": None, "network_onset_definition": "classifier_centre"}, FR, metrics=True)):
        with pytest.raises(E.MissingChoice):
            fn()


# --- synthetic records through the frozen classifier ---------------------------------------------------------------

def test_synthetic_noise_burst_and_sustained_sine_are_read_as_ns_splus_and_ssus(tmp_path):
    out = {k: E.read_record(_write(RL.expand("S10")[i], _v(k, i), tmp_path), FI) for i, k in enumerate(("NS", "tr", "sus"))}
    assert out["NS"]["class"] == "NS" and out["tr"]["class"] == "S+" and out["sus"]["class"] == "S-sus"
    r = out["tr"]
    assert r["f_pk_hz"] == pytest.approx(50.0) and r["onset_classifier_centre_s"] == pytest.approx(20.0)
    assert r["onset_classifier_start_s"] == pytest.approx(19.0)         # W = 2 s at T_ramp 60 s
    assert r["onset_raw_crossing_s"] == pytest.approx(20.0, abs=0.05)
    assert r["W_s"] == 2.0 and r["step_s"] == 1.0 and r["bin_hz"] == 0.5
    v = _v("tr", 1)
    assert r["baseline_std_v_half_open"] == pytest.approx(np.std(v[0:5000], ddof=1))
    assert r["baseline_std_v_closed"] == pytest.approx(np.std(v[0:5001], ddof=1))
    assert np.isnan(out["NS"]["f_pk_hz"]) and np.isnan(out["NS"]["onset_classifier_centre_s"])


def test_a_failed_record_is_labelled_failed_and_never_matches(tmp_path):
    r = E.read_record(_write(_row(), _v("NS"), tmp_path, status="failed"), FI)
    assert r["class"] == M.FAILED and not E.matches("D-tr", r["class"]) and not E.matches("D-none", r["class"])


# --- counting logic on fake runs ---------------------------------------------------------------------------------------

def _fake(cls, seed, N=10000, f=50.0, on=20.0, T_ramp=60.0, het="lorentzian", group=None, cell=(0.3, 5.0), **kw):
    W, step = M.window_for_ramp(T_ramp)
    d = {"name": f"fake_{cls}_{N}_{seed}_{het}", "missing": False, "seed": seed, "class": cls, "surge": cls in M.SURGE_CLASSES, "f_pk_hz": f, "T_ramp_s": T_ramp,
         "onset_classifier_centre_s": on, "onset_classifier_start_s": on - W / 2, "onset_raw_crossing_s": on, "W_s": W, "step_s": step, "bin_hz": 1 / W,
         "N": N, "het_dist": het, "Delta": cell[0], "tau_d_ms": cell[1], "group": group, "baseline_std_v_half_open": 0.0388, "baseline_std_v_closed": 0.0388}
    d.update(kw)
    return d


REF = {"class": "D-tr", "onset_s": 20.0, "f_pk_hz": 50.0}


def test_f_pk_tolerance_is_five_percent_and_the_boundary_is_a_choice():
    ok = E.seed_assessment(_fake("S+", 0, f=52.5), REF, CH, 0.05)             # exactly 5 percent
    assert ok["f_pk_ok"] is True and ok["pass"]
    strict = E.seed_assessment(_fake("S+", 0, f=52.5), REF, dict(CH, tolerance_boundary="strict"), 0.05)
    assert strict["f_pk_ok"] is False and not strict["pass"]
    assert E.seed_assessment(_fake("S+", 0, f=52.6), REF, CH, 0.05)["f_pk_ok"] is False
    a = E.seed_assessment(_fake("S+", 0, f=48.0, T_ramp=10.0), REF, CH, 0.05)
    assert a["bin_hz"] == pytest.approx(3.0) and a["f_pk_diff_bins"] == pytest.approx(-2.0 / 3.0)       # W = 1/3 s: bin 3 Hz reported beside the test


def test_onset_tolerance_is_one_spectrogram_step():
    assert E.seed_assessment(_fake("S+", 0, on=21.0), REF, CH, 0.05)["onset_ok"] is True                     # step 1 s at T_ramp 60 s
    assert E.seed_assessment(_fake("S+", 0, on=21.2), REF, CH, 0.05)["onset_ok"] is False
    s10 = E.seed_assessment(_fake("S+", 0, on=20.2, T_ramp=10.0), REF, CH, 0.05)                              # step W/2 = 1/6 s at 10 s
    assert s10["step_s"] == pytest.approx(1 / 6) and s10["onset_ok"] is False
    raw = dict(CH, network_onset_definition="classifier_start")
    assert E.seed_assessment(_fake("S+", 0, on=21.0), REF, raw, 0.05)["onset_diff_s"] == pytest.approx(0.0)    # 21 - W/2 = 20


def test_correspondence_and_the_post_hoc_s_rel_reading():
    a = E.seed_assessment(_fake("S-rel", 0), REF, CH, 0.05)
    assert a["class_match"] and not a["class_match_posthoc"] and a["pass"] and not a["pass_srel_not_counted"]
    assert not E.seed_assessment(_fake("S-sus", 0), REF, CH, 0.05)["class_match"]           # D-tr meets S-sus: disagreement (R19)
    assert E.matches("D-none", "NS") and not E.matches("D-none", "S+")


def test_a_seed_without_f_pk_or_onset_follows_the_not_evaluable_choice():
    nan = _fake("S+", 0, f=float("nan"), on=float("nan"))
    assert E.seed_assessment(nan, REF, CH, 0.05)["pass"] is False
    assert E.seed_assessment(nan, REF, dict(CH, not_evaluable_counts_as="vacuous"), 0.05)["pass"] is True


def test_headline_needs_all_three_seeds_at_each_t_ramp():
    refs = {("head", 60.0): REF}
    recs = [_fake("S+", s) for s in range(3)]
    assert E.rb1_headline(recs, refs, [], CH, FR)[60.0]["verdict"] == "PASS"
    recs[2] = _fake("NS", 2, f=float("nan"), on=float("nan"))
    p = E.rb1_headline(recs, refs, [], CH, FR)[60.0]
    assert p["verdict"] == "FAIL" and p["pass_count"] == 2
    assert E.rb1_headline(recs[:2], refs, [], CH, FR)[60.0]["verdict"] == "INCOMPLETE"
    assert E.rb1_headline(recs, {}, [], CH, FR)[60.0]["verdict"] == "INCOMPLETE"


def test_posthoc_median_reading_is_labelled_and_separate():
    refs = {("head", 60.0): REF}
    recs = [_fake("S+", 0, f=50.0), _fake("S+", 1, f=50.0), _fake("S+", 2, f=60.0)]
    p = E.rb1_headline(recs, refs, [], CH, FR)[60.0]
    assert p["verdict"] == "FAIL" and p["posthoc_median"]["f_pk_ok"] is True and "no gate" in p["posthoc_median"]["label"]


def test_cells_need_all_three_seeds_in_the_class_and_three_of_four_cells():
    refs = {("cell", c): {"class": "D-tr" if c < 2 else "D-none", "onset_s": 20.0, "f_pk_hz": 50.0} for c in range(4)}
    good = {0: "S+", 1: "S-abs", 2: "NS", 3: "NS"}
    recs = [_fake(good[c], s, T_ramp=30.0, group=c) for c in range(4) for s in range(3)]
    r = E.rb1_cells(recs, refs, [], {c: "D-tr" for c in range(4)}, FR)
    assert r["verdict"] == "PASS" and r["n_agree"] == 4 and r["disagree"] == 0
    recs[3] = _fake("S-sus", 0, T_ramp=30.0, group=1)            # one seed of cell 1 out of class: cell 1 does not agree (R15), 3 of 4 remain
    r = E.rb1_cells(recs, refs, [], {}, FR)
    assert r["n_agree"] == 3 and r["verdict"] == "PASS" and r["disagree"] == 1
    recs[6] = _fake("S+", 0, T_ramp=30.0, group=2)               # cell 2 (D-none) with an S+ seed
    r = E.rb1_cells(recs, refs, [], {}, FR)
    assert r["n_agree"] == 2 and r["verdict"] == "FAIL" and r["disagree"] == 2
    assert E.rb1_cells(recs[:-1], refs, [], {}, FR)["verdict"] == "INCOMPLETE"


def test_n_rule_counts_seeds_in_the_matching_class_and_reports_errors():
    def grid(n10, n30):
        return ([_fake("S+" if s < n10 else "NS", s, N=10000, f=50.5) for s in range(10)] + [_fake("S+" if s < n30 else "NS", s, N=30000, f=51.0) for s in range(10)]
                + [_fake("S+", s, N=1000) for s in range(10)] + [_fake("S+", s, N=3000) for s in range(10)])
    assert E.n_sweep(grid(7, 7), REF, [], CH, FR)["no_worse"]["pass"] is True
    assert E.n_sweep(grid(7, 8), REF, [], CH, FR)["no_worse"]["pass"] is True
    bad = E.n_sweep(grid(7, 6), REF, [], CH, FR)
    assert bad["no_worse"]["pass"] is False and bad["by_N"][30000]["f_pk_rel_err"]["median"] == pytest.approx(0.02)
    short = grid(7, 7)
    del short[19]                                                                              # one N = 3e4 seed missing
    assert E.n_sweep(short, REF, [], CH, FR)["no_worse"]["pass"] is None             # incomplete: not a verdict
    m = E.n_sweep(grid(10, 10), REF, [], CH, FR, metrics=True)["by_N"][1000]["metrics"]
    assert set(m) == {"onset_s", "f_pk_hz", "baseline_std_v"} and m["f_pk_hz"]["median"] == 50.0 and m["f_pk_hz"]["n"] == 10


def test_controls_are_matched_by_configuration_and_reported_beside():
    ramp = _fake("S+", 0, N=10000)
    ctrl = [_fake("S-sus", s, N=10000) for s in range(3)] + [_fake("NS", s, N=3000) for s in range(3)]
    c = E.control_classes(ramp, ctrl)
    assert c["n"] == 3 and c["classes"] == {"S-sus": 3} and c["surge"] == 0


def test_sigma_check_range_bounds_and_sigma_is_never_changed():
    heads = [_fake("S+", s, baseline_std_v_half_open=x) for s, x in enumerate((0.0385, 0.0388, 0.0391, 0.0385, 0.0388, 0.0391))]
    r = E.sigma_check(heads, dict(CH, mf_baseline_std=0.0389))
    assert r["verdict"] == "PASS" and r["n_distinct_values"] == 3 and r["sigma_changed"] is False
    assert E.sigma_check(heads, dict(CH, mf_baseline_std=0.0391))["verdict"] == "PASS"
    assert E.sigma_check(heads, dict(CH, mf_baseline_std=0.0391, sigma_range_bounds="strict"))["verdict"].startswith("NOT INSIDE")
    out = E.sigma_check(heads, dict(CH, mf_baseline_std=0.045))
    assert out["verdict"].startswith("NOT INSIDE") and "sigma stays frozen" in out["verdict"]
    assert E.sigma_check(heads[:5] + [{"name": "x", "missing": True}], CH)["verdict"] == "INCOMPLETE"
    with pytest.raises(E.MissingChoice):
        E.sigma_check(heads, dict(CH, mf_baseline_std=None))


def _s10(l_cls, g_cls, u_cls):
    return ([_fake(c, s, het="lorentzian") for s, c in enumerate(l_cls)] + [_fake(c, s, het="gaussian") for s, c in enumerate(g_cls)]
            + [_fake(c, s, het="uniform") for s, c in enumerate(u_cls)])


def test_rb8_paired_and_modal_comparators():
    same = _s10(["S+"] * 3, ["S+"] * 3, ["S+"] * 3)
    assert E.rb8(same, [], REF, CH, FR)["verdict"] == "PASS"
    mixed = _s10(["S+", "S-sus", "S+"], ["S+", "S-sus", "S+"], ["S+", "S+", "S+"])
    r = E.rb8(mixed, [], REF, CH, FR)
    assert r["shapes"]["gaussian"]["verdict"] == "PASS" and r["shapes"]["uniform"]["verdict"] == "FAIL" and r["verdict"] == "FAIL"
    modal = E.rb8(mixed, [], REF, dict(CH, rb8_comparator="modal_lorentzian_class"), FR)
    assert modal["shapes"]["uniform"]["verdict"] == "PASS" and modal["shapes"]["gaussian"]["verdict"] == "FAIL"
    tie = _s10(["S+", "S-sus", "NS"], ["S+"] * 3, ["S+"] * 3)
    assert E.rb8(tie, [], REF, dict(CH, rb8_comparator="modal_lorentzian_class"), FR)["verdict"] == "UNDETERMINED"
    rel = _s10(["S+"] * 3, ["S-rel"] * 3, ["S-abs"] * 3)
    assert E.rb8(rel, [], REF, CH, FR)["verdict"] == "FAIL"
    assert E.rb8(rel, [], REF, dict(CH, rb8_class_equality="surge_correspondence"), FR)["verdict"] == "PASS"
    assert E.rb8(same[:5], [], REF, CH, FR)["verdict"] == "INCOMPLETE"


def test_g4_misses_means_no_seed_in_a_surge_class_and_carries_the_three_consequences():
    miss = [_fake("NS", s, N=N) for N in (10000, 30000) for s in range(10)]
    rb1 = {"verdict": "FAIL"}
    cells = {"disagree": 2}
    g = E.g4_summary({"S9": miss}, rb1, cells, CH)
    assert g["misses_both"] is True and g["cells_disagree_2_or_more"] is True and g["triggered"] is True
    assert len(g["text"]) == 5 and "finite-size" in g["text"][1] and "RB6" in g["text"][2] and "mean-field-only" in g["text"][3] and "report-only" in g["text"][4]
    hit = [_fake("NS", s, N=10000) for s in range(10)] + [_fake("S-abs" if s == 0 else "NS", s, N=30000) for s in range(10)]
    g = E.g4_summary({"S9": hit}, {"verdict": "PASS"}, {"disagree": 0}, CH)
    assert g["misses_by_N"][30000]["misses"] is False and g["misses_both"] is False and g["triggered"] is False
    none = E.g4_summary({"S9": []}, {"verdict": "INCOMPLETE"}, {"disagree": None}, CH)
    assert none["misses_both"] is None and none["triggered"] is None
    with pytest.raises(E.MissingChoice):
        E.g4_summary({}, rb1, cells, dict(CH, g4_source_lists=["S7"]))


def test_overall_rb1_is_incomplete_until_every_part_is_in():
    head = {10.0: {"verdict": "PASS"}, 120.0: {"verdict": "PASS"}}
    cells = {"verdict": "PASS"}
    assert E.rb1_overall(head, cells, {"no_worse": {"pass": True}})["verdict"] == "PASS"
    assert E.rb1_overall(head, cells, {"no_worse": {"pass": False}})["verdict"] == "FAIL"
    assert E.rb1_overall(head, {"verdict": "INCOMPLETE"}, {"no_worse": {"pass": True}})["verdict"] == "INCOMPLETE"


def test_end_to_end_s10_records_through_read_lists_and_rb8(tmp_path, monkeypatch):
    rows = {n: [dict(r, out_dir=str(tmp_path / n)) for r in RL.expand(n)] for n in ("S10", "C2_S10")}
    for n, rs in rows.items():
        for r in rs:
            _write(dict(r, family=n), _v("tr" if n == "S10" else "NS", 0), tmp_path)      # noise seed 0: S+ (some seeds of this burst are NS, a fixture fragility)
    for n, rs in rows.items():
        rows[n] = [dict(r, out_dir=str(tmp_path / n), family=n) for r in rs]
    monkeypatch.setattr(E, "expected_rows", lambda lists, require_frozen=True: {n: rows[n] for n in lists})
    by = E.read_lists(("S10", "C2_S10"), FI)
    assert {r["class"] for r in by["S10"]} == {"S+"} and {r["class"] for r in by["C2_S10"]} == {"NS"}
    r = E.rb8(by["S10"], by["C2_S10"], REF, CH, FR)
    assert r["verdict"] == "PASS" and r["shapes"]["gaussian"]["controls"]["classes"] == {"NS": 3}
