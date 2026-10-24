"""MS10 10d/10e: evaluator tests on SYNTHETIC fixtures only (no real network record is read; none exists at 10e).

Records are written to tmp_path from rows of the frozen run lists with synthetic v series (white noise, a 50 Hz burst); the evaluators are then driven
with fake per-run dicts for the counting logic. CH below mirrors the choices ruled at 10e (R25 to R28) except where a test varies one field on purpose.
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
      "sigma_window": {"start_sample": 0, "stop_sample": 5000, "ddof": 1}, "sigma_range_bounds": "inclusive", "s9_metrics": ["onset_s", "f_pk_hz", "duration_ms"],
      "rb8_comparator": "common_lorentzian_class", "rb8_class_equality": "surge_correspondence",
      "g4_pools": {"10000": ["S8:headline", "S9", "S10:lorentzian"], "30000": ["S9"]},
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

def test_the_shipped_choices_are_the_ruled_ones_and_a_blanked_field_still_errors():
    ch = E.load_choices()
    assert set(ch) == set(E.CHOICE_VALUES) | {"sigma_window", "s9_metrics", "g4_pools", "mf_baseline_std", "mf_baseline_std_source"}
    assert ch["network_onset_definition"] == "classifier_centre" and ch["not_evaluable_counts_as"] == "not_met" and ch["tolerance_boundary"] == "inclusive"
    assert ch["sigma_range_bounds"] == "inclusive" and ch["rb8_comparator"] == "common_lorentzian_class" and ch["rb8_class_equality"] == "surge_correspondence"
    assert ch["sigma_window"] == {"start_sample": 0, "stop_sample": 5000, "ddof": 1} and ch["mf_baseline_std"] == 0.039522
    assert "2329991bbd6b1d1f05d677b1d41d62fd22037da1fa362f13993f92c7f2242e83" in ch["mf_baseline_std_source"] and "S5base_0000_1fe2ceaa1659" in ch["mf_baseline_std_source"]
    assert set(ch["s9_metrics"]) <= set(E.METRIC_NAMES) and ch["g4_pools"] == {"10000": ["S8:headline", "S9", "S10:lorentzian"], "30000": ["S9"]}
    for name in list(E.CHOICE_VALUES) + ["sigma_window", "s9_metrics", "g4_pools", "mf_baseline_std", "mf_baseline_std_source"]:     # blank each field in turn
        with pytest.raises(E.MissingChoice):
            E.choice(dict(ch, **{name: None}), name)
    with pytest.raises(E.MissingChoice):
        E.choice({"tolerance_boundary": "maybe"}, "tolerance_boundary")
    with pytest.raises(E.MissingChoice):
        E.choice({"network_onset_definition": "raw_crossing"}, "network_onset_definition")        # R27: the raw crossing is never the primary onset
    with pytest.raises(E.MissingChoice):
        E.sigma_window_of(dict(ch, sigma_window={"start_sample": 0, "stop_sample": 5001, "ddof": 1}))   # R28: one common window, nothing else


def test_evaluators_stop_on_a_blanked_choice():
    ch = E.load_choices()
    rec = _fake("S-sus", 0)
    ref = {"class": "D-tr", "onset_s": 20.0, "f_pk_hz": 50.0}
    heads = [_fake("S+", s) for s in range(6)]
    for name, fn in (("network_onset_definition", lambda c: E.onset_of(rec, c)), ("tolerance_boundary", lambda c: E.seed_assessment(rec, ref, c, 0.05)),
                     ("not_evaluable_counts_as", lambda c: E.seed_assessment(_fake("S+", 0, f=float("nan")), ref, c, 0.05)),
                     ("mf_baseline_std", lambda c: E.sigma_check(heads, c)), ("sigma_range_bounds", lambda c: E.sigma_check(heads, c)),
                     ("sigma_window", lambda c: E.sigma_check(heads, c)), ("rb8_comparator", lambda c: E.rb8([], [], ref, c, FR)),
                     ("rb8_class_equality", lambda c: E.rb8([], [], ref, c, FR)), ("g4_pools", lambda c: E.g4_summary({}, {"verdict": "PASS"}, {}, c)),
                     ("s9_metrics", lambda c: E.n_sweep([rec], ref, [], c, FR, metrics=True))):
        with pytest.raises(E.MissingChoice):
            fn(dict(ch, **{name: None}))
    with pytest.raises(E.MissingChoice):
        E.g4_summary({}, {"verdict": "PASS"}, {}, dict(ch, g4_pools={"10000": ["S9"]}))      # no entry for 3e4


# --- synthetic records through the frozen classifier ---------------------------------------------------------------

def test_synthetic_noise_burst_and_sustained_sine_are_read_as_ns_splus_and_ssus(tmp_path):
    out = {k: E.read_record(_write(RL.expand("S10")[i], _v(k, i), tmp_path), FI) for i, k in enumerate(("NS", "tr", "sus"))}
    assert out["NS"]["class"] == "NS" and out["tr"]["class"] == "S+" and out["sus"]["class"] == "S-sus"
    r = out["tr"]
    assert r["f_pk_hz"] == pytest.approx(50.0) and r["onset_classifier_centre_s"] == pytest.approx(20.0) and r["onset_s"] == r["onset_classifier_centre_s"]
    assert r["onset_raw_crossing_s"] == pytest.approx(20.0, abs=0.05)             # secondary, post hoc
    assert r["W_s"] == 2.0 and r["step_s"] == 1.0 and r["bin_hz"] == 0.5
    assert r["baseline_std_v"] == pytest.approx(np.std(_v("tr", 1)[0:5000], ddof=1))          # R28: samples [0, 5000), ddof 1
    assert "baseline_std_v_closed" not in r and "onset_classifier_start_s" not in r
    assert np.isnan(out["NS"]["f_pk_hz"]) and np.isnan(out["NS"]["onset_classifier_centre_s"])


def test_the_sigma_window_is_the_same_for_every_t_ramp_and_not_the_classifier_baseline(tmp_path):
    v = _v("NS", 3)
    a = E.read_record(_write(RL.expand("S10")[0], v, tmp_path), FI)
    assert a["baseline_std_v"] == E.sigma_baseline_std(v) == pytest.approx(np.std(v[:5000], ddof=1))
    assert E.sigma_baseline_std(v) != pytest.approx(np.std(v[:4842], ddof=1), rel=1e-12)       # the classifier's own baseline windows end earlier at 10 s
    with pytest.raises(E.EvalError):
        E.sigma_baseline_std(v[:4999])


def test_table21_fields_on_a_synthetic_p2_record(tmp_path):
    row = _write(RL.expand("S10")[1], _v("tr", 1), tmp_path)
    rec = E.read_record(row, FI, table21=True)
    assert rec["class"] == "S+" and rec["onset_s"] == pytest.approx(20.0)
    assert rec["duration_frac_ramp"] == pytest.approx(rec["duration_ms"] / 1000.0 / rec["T_ramp_s"])
    assert np.isfinite(rec["eta_onset"]) and rec["delay_eta"] == pytest.approx(rec["eta_onset"] - row["cfg"]["path"]["eta_H"])
    assert np.isfinite(rec["peak_power_abs"]) and np.isfinite(rec["peak_power_rel"]) and rec["peak_power_abs"] == rec["peak_p_g"]
    assert set(rec["undefined"]) <= set(E.TABLE21_METRICS)            # whatever is not defined is named with a reason, never imputed
    for k, why in rec["undefined"].items():
        assert np.isnan(rec[k]) and why
    ns = E.read_record(_write(RL.expand("S10")[0], _v("NS"), tmp_path), FI, table21=True)
    assert set(ns["undefined"]) == set(E.TABLE21_METRICS) and all(w == "no_episode" for w in ns["undefined"].values())


def test_a_failed_record_is_labelled_failed_and_never_matches(tmp_path):
    r = E.read_record(_write(_row(), _v("NS"), tmp_path, status="failed"), FI)
    assert r["class"] == M.FAILED and not E.matches("D-tr", r["class"]) and not E.matches("D-none", r["class"])


# --- counting logic on fake runs ---------------------------------------------------------------------------------------

def _fake(cls, seed, N=10000, f=50.0, on=20.0, T_ramp=60.0, het="lorentzian", group=None, cell=(0.3, 5.0), **kw):
    W, step = M.window_for_ramp(T_ramp)
    d = {"name": f"fake_{cls}_{N}_{seed}_{het}", "missing": False, "seed": seed, "class": cls, "surge": cls in M.SURGE_CLASSES, "f_pk_hz": f, "T_ramp_s": T_ramp,
         "onset_s": on, "onset_classifier_centre_s": on, "onset_raw_crossing_s": on, "W_s": W, "step_s": step, "bin_hz": 1 / W, "duration_ms": 4000.0,
         "N": N, "het_dist": het, "Delta": cell[0], "tau_d_ms": cell[1], "group": group, "baseline_std_v": 0.0388}
    d.update(kw)
    return d


REF = {"class": "D-tr", "onset_s": 20.0, "f_pk_hz": 50.0}


def test_f_pk_tolerance_is_five_percent_inclusive_and_margins_are_reported():
    ok = E.seed_assessment(_fake("S+", 0, f=52.5), REF, CH, 0.05)             # exactly 5 percent: inclusive (E-3)
    assert ok["f_pk_ok"] is True and ok["pass"] and ok["f_pk_margin"] == pytest.approx(0.0, abs=1e-12) and ok["f_pk_status"] == "ok"
    low = E.seed_assessment(_fake("S+", 0, f=47.5), REF, CH, 0.05)
    assert low["f_pk_ok"] is True and low["f_pk_margin"] == pytest.approx(0.0, abs=1e-12)
    strict = E.seed_assessment(_fake("S+", 0, f=52.5), REF, dict(CH, tolerance_boundary="strict"), 0.05)
    assert strict["f_pk_ok"] is False and not strict["pass"]
    assert E.seed_assessment(_fake("S+", 0, f=52.6), REF, CH, 0.05)["f_pk_ok"] is False
    assert E.seed_assessment(_fake("S+", 0, f=51.0), REF, CH, 0.05)["f_pk_margin"] == pytest.approx(0.03)
    a = E.seed_assessment(_fake("S+", 0, f=48.0, T_ramp=10.0), REF, CH, 0.05)
    assert a["bin_hz"] == pytest.approx(3.0) and a["f_pk_diff_bins"] == pytest.approx(-2.0 / 3.0)       # W = 1/3 s: bin 3 Hz reported beside the test


def test_onset_is_the_classifier_onset_within_one_spectrogram_step_inclusive():
    exact = E.seed_assessment(_fake("S+", 0, on=21.0), REF, CH, 0.05)                              # step 1 s at T_ramp 60 s: exactly one step passes
    assert exact["onset_ok"] is True and exact["onset_margin_s"] == pytest.approx(0.0, abs=1e-12) and exact["pass"]
    assert E.seed_assessment(_fake("S+", 0, on=19.0), REF, CH, 0.05)["onset_ok"] is True
    assert E.seed_assessment(_fake("S+", 0, on=21.0), REF, dict(CH, tolerance_boundary="strict"), 0.05)["onset_ok"] is False
    assert E.seed_assessment(_fake("S+", 0, on=21.2), REF, CH, 0.05)["onset_ok"] is False
    s10 = E.seed_assessment(_fake("S+", 0, on=20.2, T_ramp=10.0), REF, CH, 0.05)                              # step W/2 = 1/6 s at 10 s
    assert s10["step_s"] == pytest.approx(1 / 6) and s10["onset_ok"] is False and s10["onset_margin_s"] < 0
    assert E.seed_assessment(_fake("S+", 0, on=20.0 + 1 / 6, T_ramp=10.0), REF, CH, 0.05)["onset_ok"] is True      # exactly one 10 s step (floating point)


def test_the_raw_crossing_is_a_secondary_post_hoc_reading_that_feeds_no_gate():
    far_raw = E.seed_assessment(_fake("S+", 0, on=20.0, onset_raw_crossing_s=30.0), REF, CH, 0.05)
    assert far_raw["pass"] and far_raw["onset_raw_ok"] is False and far_raw["onset_raw_status"] == "ok" and "no gate" in far_raw["onset_raw_label"]
    undef_raw = E.seed_assessment(_fake("S+", 0, on=20.0, onset_raw_crossing_s=float("nan")), REF, CH, 0.05)
    assert undef_raw["pass"] and undef_raw["onset_raw_status"] == "undefined" and undef_raw["onset_raw_ok"] is None        # undefined allowed, no effect
    near_raw_far_cls = E.seed_assessment(_fake("S+", 0, on=25.0, onset_raw_crossing_s=20.0), REF, CH, 0.05)
    assert near_raw_far_cls["onset_ok"] is False and not near_raw_far_cls["pass"] and near_raw_far_cls["onset_raw_ok"] is True


def test_correspondence_and_the_post_hoc_s_rel_reading():
    a = E.seed_assessment(_fake("S-rel", 0), REF, CH, 0.05)
    assert a["class_match"] and not a["class_match_posthoc"] and a["pass"] and not a["pass_srel_not_counted"]
    assert not E.seed_assessment(_fake("S-sus", 0), REF, CH, 0.05)["class_match"]           # D-tr meets S-sus: disagreement (R19)
    assert E.matches("D-none", "NS") and not E.matches("D-none", "S+")


def test_a_seed_with_an_undefined_f_pk_or_onset_fails_that_test_and_is_reported_undefined():
    nan = float("nan")
    for kw, which in (({"f": nan}, "f_pk"), ({"on": nan}, "onset")):
        a = E.seed_assessment(_fake("S+", 0, **kw), REF, CH, 0.05)
        assert a["pass"] is False and a[f"{which}_status"] == "undefined" and a[f"{which}_ok"] is None and a[f"{which}_ok_policy"] is False
        other = "onset" if which == "f_pk" else "f_pk"
        assert a[f"{other}_status"] == "ok"
    both = E.seed_assessment(_fake("NS", 0, f=nan, on=nan), REF, CH, 0.05)
    assert both["pass"] is False and both["f_pk_status"] == both["onset_status"] == "undefined"
    assert E.seed_assessment(_fake("S+", 0, f=nan, on=nan), REF, dict(CH, not_evaluable_counts_as="vacuous"), 0.05)["pass"] is True        # the alternative is code, not the ruling
    ref_none = {"class": "D-none", "onset_s": None, "f_pk_hz": None}                     # nothing to compare: n/a, the class test carries it
    na = E.seed_assessment(_fake("NS", 0, f=nan, on=nan), ref_none, CH, 0.05)
    assert na["f_pk_status"] == na["onset_status"] == "n/a" and na["pass"] is True
    assert E.seed_assessment(_fake("S+", 0, f=nan, on=nan), ref_none, CH, 0.05)["pass"] is False


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
    g = grid(10, 10)
    g[0] = _fake("S+", 0, N=10000, f=float("nan"))
    g[20] = _fake("S+", 0, N=1000, duration_ms=float("nan"), undefined={"duration_ms": "episode_unterminated_at_run_end"})
    m = E.n_sweep(g, REF, [], CH, FR, metrics=True)
    assert set(m["by_N"][1000]["metrics"]) == {"onset_s", "f_pk_hz", "duration_ms"} and m["by_N"][1000]["metrics"]["f_pk_hz"]["median"] == 50.0
    dm = m["by_N"][1000]["metrics"]["duration_ms"]
    assert dm["n"] == 9 and dm["n_undefined"] == 1 and dm["median"] == 4000.0            # undefined entries counted, not imputed
    assert m["by_N"][1000]["metric_undefined_reasons"] == {"duration_ms: episode_unterminated_at_run_end": 1}
    assert m["by_N"][10000]["metrics"]["f_pk_hz"]["n"] == 9 and m["by_N"][10000]["metrics"]["f_pk_hz"]["n_undefined"] == 1


def test_controls_are_matched_by_configuration_and_reported_beside():
    ramp = _fake("S+", 0, N=10000)
    ctrl = [_fake("S-sus", s, N=10000) for s in range(3)] + [_fake("NS", s, N=3000) for s in range(3)]
    c = E.control_classes(ramp, ctrl)
    assert c["n"] == 3 and c["classes"] == {"S-sus": 3} and c["surge"] == 0


def test_sigma_check_range_bounds_are_inclusive_and_sigma_is_never_changed():
    heads = [_fake("S+", s % 3, T_ramp=10.0 if s < 3 else 120.0, baseline_std_v=x) for s, x in enumerate((0.0385, 0.0388, 0.0391, 0.0385, 0.0388, 0.0391))]
    r = E.sigma_check(heads, dict(CH, mf_baseline_std=0.0389))
    assert r["verdict"] == "PASS" and r["n_distinct_values"] == 3 and r["sigma_changed"] is False
    assert r["n_distinct_per_seed"] == {0: 1, 1: 1, 2: 1}                      # the T_ramp 10 s and 120 s baselines of a seed are identical in this fixture
    assert r["window"] == {"start_sample": 0, "stop_sample": 5000, "ddof": 1}
    assert r["position_in_range"] == pytest.approx((0.0389 - 0.0385) / 0.0006) and r["margin_to_nearest_end"] == pytest.approx(0.0002)
    assert E.sigma_check(heads, dict(CH, mf_baseline_std=0.0391))["verdict"] == "PASS"            # exactly the maximum
    assert E.sigma_check(heads, dict(CH, mf_baseline_std=0.0385))["verdict"] == "PASS"            # exactly the minimum
    assert E.sigma_check(heads, dict(CH, mf_baseline_std=0.0391, sigma_range_bounds="strict"))["verdict"].startswith("NOT INSIDE")
    assert E.sigma_check(heads, dict(CH, mf_baseline_std=0.0384))["verdict"].startswith("NOT INSIDE")
    out = E.sigma_check(heads, dict(CH, mf_baseline_std=0.045))
    assert out["verdict"].startswith("NOT INSIDE") and "sigma stays frozen" in out["verdict"]
    assert E.sigma_check(heads[:5] + [{"name": "x", "missing": True}], CH)["verdict"] == "INCOMPLETE"
    with pytest.raises(E.MissingChoice):
        E.sigma_check(heads, dict(CH, mf_baseline_std=None))


def test_sigma_check_counts_distinct_baselines_per_seed_and_overall():
    vals = (0.0385, 0.0388, 0.0391, 0.0386, 0.0388, 0.0391)               # seed 0 differs between the two T_ramp: reported, not assumed equal
    heads = [_fake("S+", s % 3, T_ramp=10.0 if s < 3 else 120.0, baseline_std_v=x) for s, x in enumerate(vals)]
    r = E.sigma_check(heads, dict(CH, mf_baseline_std=0.0389))
    assert r["n_distinct_values"] == 4 and r["n_distinct_per_seed"] == {0: 2, 1: 1, 2: 1}


def test_the_headline_baselines_of_one_seed_agree_when_the_pre_ramp_signal_is_the_same(tmp_path):
    # synthetic: the same v up to sample 5000 at T_ramp 10 s and 120 s (parameters constant before t_on) -> one distinct value per seed
    base = _v("NS", 5)
    recs = []
    for i, T_ramp in enumerate((10.0, 120.0)):
        v = base.copy()
        v[6000:] = _v("NS", 6 + i)[6000:]
        row = RL.expand("S10")[0]
        row = dict(row, name=f"{row['name']}_{i}")
        rec = E.read_record(_write(row, v, tmp_path, config_hash=row["hash"]), FI)
        recs.append(dict(rec, seed=0, T_ramp_s=T_ramp))
    assert recs[0]["baseline_std_v"] == recs[1]["baseline_std_v"]


def _s10(l_cls, g_cls, u_cls):
    return ([_fake(c, s, het="lorentzian") for s, c in enumerate(l_cls)] + [_fake(c, s, het="gaussian") for s, c in enumerate(g_cls)]
            + [_fake(c, s, het="uniform") for s, c in enumerate(u_cls)])


def test_rb8_compares_with_the_lorentzian_class_only_if_the_three_seeds_share_one_correspondence_class():
    same = _s10(["S+"] * 3, ["S+"] * 3, ["S+"] * 3)
    r = E.rb8(same, [], REF, CH, FR)
    assert r["verdict"] == "PASS" and r["common_level"] == "surge" and r["lorentzian_levels"] == ["surge"]
    mixed_labels = _s10(["S+", "S-rel", "S-abs"], ["S-abs", "S+", "S-rel"], ["S+", "S+", "S+"])      # E-8: one correspondence class, labels differ
    r = E.rb8(mixed_labels, [], REF, CH, FR)
    assert r["verdict"] == "PASS" and r["lorentzian_classes"] == ["S+", "S-rel", "S-abs"] and r["shapes"]["gaussian"]["classes"] == ["S-abs", "S+", "S-rel"]
    two_of_three = _s10(["S+"] * 3, ["S+", "S-sus", "S+"], ["S+"] * 3)
    r = E.rb8(two_of_three, [], REF, CH, FR)
    assert r["shapes"]["gaussian"]["hits"] == 2 and r["shapes"]["gaussian"]["verdict"] == "FAIL" and r["shapes"]["uniform"]["verdict"] == "PASS" and r["verdict"] == "FAIL"
    ns = _s10(["NS"] * 3, ["NS"] * 3, ["NS"] * 3)
    assert E.rb8(ns, [], REF, CH, FR)["verdict"] == "PASS"
    sus_vs_surge = _s10(["S-sus"] * 3, ["S+"] * 3, ["S-sus"] * 3)
    r = E.rb8(sus_vs_surge, [], REF, CH, FR)
    assert r["shapes"]["gaussian"]["verdict"] == "FAIL" and r["shapes"]["uniform"]["verdict"] == "PASS"
    rel = _s10(["S+"] * 3, ["S-rel"] * 3, ["S-abs"] * 3)
    r = E.rb8(rel, [], REF, CH, FR)
    assert r["verdict"] == "PASS" and r["shapes"]["gaussian"]["hits_srel_not_counted"] == 0 and r["shapes"]["uniform"]["hits_srel_not_counted"] == 3
    assert E.rb8(same[:5], [], REF, CH, FR)["verdict"] == "INCOMPLETE"


def test_rb8_is_not_evaluable_when_the_lorentzian_correspondence_classes_differ():
    mixed = _s10(["S+", "S-sus", "S+"], ["S+", "S-sus", "S+"], ["S+", "S+", "S+"])
    r = E.rb8(mixed, [], REF, CH, FR)
    assert r["verdict"] == "NOT EVALUABLE" and r["shapes"] == {} and "correspondence class" in r["reason"]
    t = r["per_seed_table"]
    assert [x["class"] for x in t["lorentzian"]] == ["S+", "S-sus", "S+"] and [x["level"] for x in t["lorentzian"]] == ["surge", "S-sus", "surge"]
    assert [x["class"] for x in t["gaussian"]] == ["S+", "S-sus", "S+"] and [x["class"] for x in t["uniform"]] == ["S+"] * 3
    tie = _s10(["S+", "S-sus", "NS"], ["S+"] * 3, ["S+"] * 3)
    assert E.rb8(tie, [], REF, CH, FR)["verdict"] == "NOT EVALUABLE"
    failed = _s10([M.FAILED] * 3, ["S+"] * 3, ["S+"] * 3)
    assert E.rb8(failed, [], REF, CH, FR)["verdict"] == "NOT EVALUABLE"


def _g4_pool_fixture(surge_in=None, missing_in=None):
    """Records of the three lists with the Lorentzian N = 1e4 pool (S8 headline, S9, S10), a Gaussian S10 run, an S8 cell run, and S9 at 3e4. surge_in: key of
    the one record that is made S+; missing_in: key of the one record that is made missing."""
    recs = {"S8": [_fake("NS", s, N=10000, name=f"S8_head_{s}") for s in range(6)] + [_fake("NS", s, N=10000, name=f"S8_cells_{s}", group=1) for s in range(12)],
            "S9": [_fake("NS", s, N=10000, name=f"S9_1e4_{s}") for s in range(10)] + [_fake("NS", s, N=30000, name=f"S9_3e4_{s}") for s in range(10)]
                  + [_fake("NS", s, N=1000, name=f"S9_1e3_{s}") for s in range(10)],
            "S10": [_fake("NS", s, N=10000, name=f"S10_l_{s}") for s in range(3)] + [_fake("NS", s, N=10000, het="gaussian", name=f"S10_g_{s}") for s in range(3)]}
    for lst, name in ((surge_in, "S+"), (missing_in, "missing")):
        if lst is None:
            continue
        L, i = lst
        r = recs[L][i]
        recs[L][i] = _fake("S+", r["seed"], N=r["N"], het=r["het_dist"], name=r["name"]) if name == "S+" else dict(r, missing=True)
    return recs


def test_g4_pools_the_lorentzian_records_at_each_n_and_misses_means_no_pooled_surge_seed():
    rb1, cells = {"verdict": "FAIL"}, {"disagree": 2}
    g = E.g4_summary(_g4_pool_fixture(), rb1, cells, CH)
    m = g["misses_by_N"]
    assert m[10000]["records"] == 6 + 10 + 3 and m[30000]["records"] == 10          # S8 headline 6 + S9 10 + S10 Lorentzian 3; S8 cells, Gaussian, 1e3 not pooled
    assert m[10000]["per_list"] == {"S8:headline": {"records": 6, "missing": 0, "surge_seeds": 0, "surge_seeds_srel_not_counted": 0},
                                    "S9": {"records": 10, "missing": 0, "surge_seeds": 0, "surge_seeds_srel_not_counted": 0},
                                    "S10:lorentzian": {"records": 3, "missing": 0, "surge_seeds": 0, "surge_seeds_srel_not_counted": 0}}
    assert g["misses_both"] is True and g["triggered"] is True
    assert len(g["text"]) == 5 and "finite-size" in g["text"][1] and "RB6" in g["text"][2] and "mean-field-only" in g["text"][3] and "report-only" in g["text"][4]
    for lst, i, N in (("S8", 0, 10000), ("S9", 3, 10000), ("S10", 1, 10000)):                    # one pooled seed in a surge class: no miss at 1e4
        g = E.g4_summary(_g4_pool_fixture(surge_in=(lst, i)), rb1, cells, CH)
        assert g["misses_by_N"][N]["misses"] is False and g["misses_by_N"][N]["per_list"][{"S8": "S8:headline", "S9": "S9", "S10": "S10:lorentzian"}[lst]]["surge_seeds"] == 1
        assert g["misses_both"] is False
    g = E.g4_summary(_g4_pool_fixture(surge_in=("S9", 10 + 2)), rb1, cells, CH)                    # S9 at 3e4: the 3e4 pool only
    assert g["misses_by_N"][30000]["misses"] is False and g["misses_by_N"][10000]["misses"] is True and g["misses_both"] is False
    for lst, i in (("S8", 8), ("S10", 4), ("S9", 20)):                                           # S8 cell run, Gaussian run, S9 at 1e3: not pooled
        assert E.g4_summary(_g4_pool_fixture(surge_in=(lst, i)), rb1, cells, CH)["misses_both"] is True
    assert E.g4_summary(_g4_pool_fixture(), {"verdict": "PASS"}, {"disagree": 0}, CH)["triggered"] is True        # (1) holds although RB1 passes in this made-up case: reported
    inc = E.g4_summary(_g4_pool_fixture(missing_in=("S9", 0)), rb1, cells, CH)
    assert inc["misses_by_N"][10000]["misses"] is None and inc["misses_both"] is None            # a missing record and no surge seed: not evaluable, never a miss
    inc = E.g4_summary(_g4_pool_fixture(surge_in=("S9", 1), missing_in=("S9", 0)), rb1, cells, CH)
    assert inc["misses_by_N"][10000]["misses"] is False
    none = E.g4_summary({"S9": []}, {"verdict": "INCOMPLETE"}, {"disagree": None}, CH)
    assert none["misses_both"] is None and none["triggered"] is None
    with pytest.raises(E.MissingChoice):
        E.g4_summary({}, rb1, cells, dict(CH, g4_pools={"10000": ["S7"], "30000": ["S9"]}))
    with pytest.raises(E.MissingChoice):
        E.g4_summary({}, rb1, cells, dict(CH, g4_pools={"10000": ["S9:gaussian"], "30000": ["S9"]}))
    hit = E.g4_summary(_g4_pool_fixture(surge_in=("S9", 12)), {"verdict": "PASS"}, {"disagree": 0}, CH)
    assert hit["misses_by_N"][30000]["misses"] is False and hit["misses_both"] is False and hit["triggered"] is False


# --- time origins (R27) ---------------------------------------------------------------------------------------------

def _origins():
    net = E.origin_facts(RL.expand("S10")[0]["cfg"], float(RL.expand("S10")[0]["cfg"]["network"]["rate_bin_ms"]))
    mf = E.origin_facts(RL.expand("MF_COMPANION")[0]["cfg"], 0.0)
    return net, mf


def test_time_origin_check_passes_for_the_frozen_configs_and_reports_the_stamp_offset():
    net, mf = _origins()
    assert net["path_time_of_sample0_ms"] == mf["path_time_of_sample0_ms"] == 0.0 and net["t_on_s"] == mf["t_on_s"] and net["sample_ms"] == mf["sample_ms"] == 1.0
    ok = E.check_time_origin(net, mf, "x")
    assert ok["shared"] is True and ok["stamp_offset_ms"] == 1.0 and net["stamp_is"] == "bin end" and mf["stamp_is"] == "instant"


@pytest.mark.parametrize("patch", [{"t_on_s": 6.0}, {"sample_ms": 2.0}, {"path_time_of_sample0_ms": 1000.0}, {"classifier_time_of_sample0_s": 2.0}])
def test_time_origin_check_stops_on_a_mismatch(patch):
    net, mf = _origins()
    with pytest.raises(E.EvalRefused, match="STOP"):
        E.check_time_origin(dict(net, **patch), mf, "x")


def test_a_network_record_whose_first_time_stamp_is_not_the_first_bin_end_stops_the_evaluation(tmp_path):
    row = _write(_row(), _v("NS"), tmp_path)
    d = tmp_path / row["family"]
    np.savez(d / f"{row['name']}.npz", v=_v("NS"), t_ms=np.arange(92_000) + 1.0)                      # as qif_network.run_network stamps it
    assert E.read_record(row, FI)["class"] == "NS"
    np.savez(d / f"{row['name']}.npz", v=_v("NS"), t_ms=np.arange(92_000) + 2000.0)                   # the 2 s discard not removed
    with pytest.raises(E.EvalRefused, match="STOP"):
        E.read_record(row, FI)


def test_read_lists_runs_the_time_origin_check_before_any_record_is_read(tmp_path, monkeypatch):
    rows = {"S10": [dict(r, out_dir=str(tmp_path / "S10")) for r in RL.expand("S10")]}
    monkeypatch.setattr(E, "expected_rows", lambda lists, require_frozen=True: {n: rows[n] for n in lists})
    seen = []

    def stop(rows_net, root=None):
        seen.append("origin")
        raise E.EvalRefused("STOP (R27) test")
    monkeypatch.setattr(E, "origin_check_all", stop)
    monkeypatch.setattr(E, "read_record", lambda *a, **k: seen.append("read"))
    with pytest.raises(E.EvalRefused, match="STOP"):
        E.read_lists(("S10",), FI)
    assert seen == ["origin"]


def test_the_frozen_network_configs_share_the_time_origin_of_every_stored_and_companion_mean_field_record():
    from mprsurge import config as C
    need = [C.repo_root() / f for ref in RL._read(RL.REFS_FILE)["references"] for f in ref["files"]] + [E.record_path(r) for r in RL.expand("MF_COMPANION")]
    if not all(p.exists() for p in need):
        pytest.skip("stored mean-field records are git-ignored and absent in this clone")
    rows = RL.expand("S8") + RL.expand("S9") + RL.expand("S10") + RL.expand("C2_S9")
    out = E.origin_check_all(rows)
    assert out and all(o["shared"] and o["stamp_offset_ms"] == 1.0 for o in out)


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
    monkeypatch.setattr(E, "origin_check_all", lambda rows_net, root=None: [])           # needs the real mean-field files (tested above)
    by = E.read_lists(("S10", "C2_S10"), FI, table21=True)
    assert {r["class"] for r in by["S10"]} == {"S+"} and {r["class"] for r in by["C2_S10"]} == {"NS"}
    assert "duration_ms" in by["S10"][0] and "duration_ms" not in by["C2_S10"][0]
    r = E.rb8(by["S10"], by["C2_S10"], REF, CH, FR)
    assert r["verdict"] == "PASS" and r["shapes"]["gaussian"]["controls"]["classes"] == {"NS": 3}
