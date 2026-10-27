"""MS11 11d (DL-366 to DL-376): the verdict table (ruling 2c), RB9(d) Reading A (ruling 2b), the MS11_RB9D list. SYNTHETIC data only; no record is read."""
import copy
import math
from pathlib import Path

import pytest

from mprsurge import config as C
from mprsurge.analysis import ms11_counts as MC
from mprsurge.analysis import ms11_eval as E
from mprsurge.analysis import ms11_eval_choices as EC
from mprsurge.analysis import ms11_runlist as RL

ROOT = Path(__file__).resolve().parents[1]
FILE = EC.load_file()
CH = FILE["choices"]
FR = E.frozen_leaves()


# --- ruling 2c: CONTINUE -> REPORTED; PASSED WITH DEPARTURES -> PASS only with the departures named in the note column ---------------------------------------------

def test_continue_maps_to_reported_not_pass_and_no_carried_row_uses_the_word_continue():
    assert E.map_logged("CONTINUE", CH) == E.REPORTED
    row = E.a11_row(CH, rb_id="X", check_id="y", source="s", label="pre-registered", logged_verdict="CONTINUE", recomputed=True)
    assert row["pass_or_fail"] == "REPORTED" and row["recomputed_match"] == "yes"
    assert "CONTINUE" not in [e["logged_verdict"] for e in FILE["a11_logged"]]      # the G5 row carries the close's word "PASSED, continue" (11e, DL-377: REPORTED)


def test_passed_with_departures_is_pass_only_with_the_departures_named_in_the_note_column():
    g6 = next(e for e in FILE["a11_logged"] if e["rb_id"] == "G6")
    assert g6["logged_verdict"] == "PASSED WITH DEPARTURES" and {"G6-D1", "G6-D2", "G6-D3"} <= set(g6["departures"])
    row = E.a11_row(CH, rb_id="G6", check_id="gate", source=g6["source"], label="pre-registered", logged_verdict=g6["logged_verdict"], departures=g6["departures"])
    assert row["pass_or_fail"] == "PASS"
    for d in g6["departures"]:
        assert d in row["note"], d
    with pytest.raises(E.EvalError, match="departures"):                              # PASS is refused without the departures
        E.a11_row(CH, rb_id="G6", check_id="gate", source="s", label="pre-registered", logged_verdict="PASSED WITH DEPARTURES")
    with pytest.raises(E.EvalError, match="not in a11_pass_with_departures_words"):    # departures on any other word are refused
        E.a11_row(CH, rb_id="G5", check_id="gate", source="s", label="pre-registered", logged_verdict="PASSED", departures=["G6-D1"])


def test_assemble_rows_names_the_g6_departures_in_the_note_column():
    rows = E.assemble_rows({}, FILE["a11_logged"], FR, CH, input_commits="HEAD=x")
    g6 = next(r for r in rows if r["rb_id"] == "G6")
    assert g6["pass_or_fail"] == "PASS" and g6["logged_verdict"] == "PASSED WITH DEPARTURES"
    assert all(d in g6["note"] for d in ("G6-D1", "G6-D2", "G6-D3", "gate departure 1", "gate departure 4"))
    bad = [dict(e) for e in FILE["a11_logged"]]
    next(e for e in bad if e["rb_id"] == "G6").pop("departures")
    with pytest.raises(E.EvalError):
        E.assemble_rows({}, bad, FR, CH)


def test_the_unchanged_words_of_ruling_2c_stay():
    assert E.map_logged("NOT INSIDE", CH) == "FAIL" and E.map_logged("OPEN", CH) == "NOT EVALUABLE" and E.map_logged("NOT JUDGED", CH) == "NOT EVALUABLE"


def test_a_recomputed_difference_is_flagged_in_the_note_and_never_resolved():
    hook = {"word": "MEETS", "status": "PASS", "reads": "synthetic", "shares": ["criteria loader"], "detail": "x"}
    rows = E.assemble_rows({"recompute": {"RB6/solver_onset_headline": hook}}, FILE["a11_logged"], FR, CH)
    r = next(r for r in rows if r["check_id"] == "solver_onset_headline")
    assert r["logged_verdict"] == "DOES NOT MEET" and r["pass_or_fail"] == "PASS" and r["recomputed_match"] == "no"
    assert "DIFFERS" in r["note"] and "'MEETS'" in r["note"] and "'DOES NOT MEET'" in r["note"]


def test_the_full_verdict_table_has_every_logged_word_and_only_the_four_status_words():
    m = E.verdict_map(CH)
    assert set(m.values()) <= set(E.STATUS_WORDS) and len(m) == 17
    assert {w for w, s in m.items() if s == "REPORTED"} == {"REPORTED", "CONTINUE", "PASSED, continue"}      # 11e (DL-377)


def test_passed_continue_maps_to_reported_and_every_other_mapping_is_the_11d_table():
    """11e ruling (DL-377): "PASSED, continue" -> REPORTED (was PASS). The other 16 entries are the 11d table, written out here word by word."""
    expect = {"PASS": "PASS", "FAIL": "FAIL", "FAILED": "FAIL", "MEETS": "PASS", "DOES NOT MEET": "FAIL", "NOT EVALUABLE": "NOT EVALUABLE", "NOT INSIDE": "FAIL",
              "NOT JUDGED": "NOT EVALUABLE", "NO VERDICT": "NOT EVALUABLE", "NOT IN MS8 RUNS": "NOT EVALUABLE", "OPEN": "NOT EVALUABLE", "REPORTED": "REPORTED", "PASSED": "PASS",
              "PASSED, continue": "REPORTED", "CONTINUE": "REPORTED", "PASSED WITH DEPARTURES": "PASS", "NOT PASSED": "FAIL"}
    assert E.verdict_map(CH) == expect
    assert E.map_logged("PASSED, continue", CH) == E.REPORTED
    g5 = next(e for e in FILE["a11_logged"] if e["rb_id"] == "G5")
    assert g5["logged_verdict"] == "PASSED, continue"
    row = E.a11_row(CH, rb_id="G5", check_id="gate", source="s", label="pre-registered", logged_verdict="PASSED, continue", recomputed=True)
    assert row["pass_or_fail"] == E.REPORTED


# --- ruling 2b: RB9(d), Reading A, reported only --------------------------------------------------------------------------------------------------------------

def _rec(cls, f, **kw):
    return {"class": cls, "f_pk_hz": f, "onset_s": 58.7, "eta_onset": 2.97, "duration_s": 40.0, "peak_p_g": 0.3, "peak_rho": 0.9, "J_exit_run": -3.0, "status": "ok",
            "terminated": True, **kw}


def test_rb9d_spec_is_reading_a_in_the_yaml():
    s = CH["rb9d_parameter_spec"]
    assert s["reading"] == "A" and s["changed"] == {"model.tau_ms": [8.0, 12.0]} and s["mode"] == "D" and s["held"]["model.tau_d_ms"] == 5.0
    assert s["held"]["durations"] == "in_seconds" and s["held"]["eta_numbers"] == "held_not_rederived"
    assert "mixes the tau effect with the path missing a shifted Hopf point" in s["statements"]["confounding"] and "reasoned, not tested" in s["statements"]["frequency_scaling"]
    assert s["reported"] == list(E.RB9D_FIELDS)


def test_rb9d_reports_each_run_beside_the_headline_with_no_pass_test():
    head = _rec("D-tr", 36.0)
    r = E.rb9d({8.0: _rec("D-tr", 45.0), 12.0: _rec("D-none", float("nan"), onset_s=float("nan"))}, head, CH)
    assert r["status"] == E.REPORTED and r["n_evaluated"] == 2
    a, b = r["rows"]
    assert a["f_pk_per_tau"] == pytest.approx(45.0 * 0.008) and a["class_changed_vs_headline"] is False and a["f_pk_ratio_expected_10_over_tau"] == pytest.approx(1.25)
    assert b["class_changed_vs_headline"] is True and all(k in a for k in E.RB9D_FIELDS)
    assert r["headline_10ms"]["f_pk_hz"] == 36.0
    assert "mixes the tau effect with the path missing a shifted Hopf point" in r["caveat"] and "[reasoned, not tested]" in r["caveat"] and "mode D" in r["mode"]
    assert {x["status"] for x in r["rows"]} == {"REPORTED"}


def test_rb9d_missing_record_or_headline_is_not_evaluable_and_nothing_replaces_it():
    head = _rec("D-tr", 36.0)
    assert E.rb9d({8.0: _rec("D-tr", 45.0), 12.0: {"missing": True}}, head, CH)["status"] == E.NE
    assert E.rb9d({}, head, CH)["status"] == E.NE
    assert E.rb9d({8.0: _rec("D-tr", 45.0), 12.0: _rec("D-tr", 30.0)}, None, CH)["status"] == E.NE


def test_rb9d_failed_run_is_reported_as_failed_not_dropped():
    r = E.rb9d({8.0: _rec("failed", float("nan"), status="failed"), 12.0: _rec("D-tr", 30.0)}, _rec("D-tr", 36.0), CH)
    assert r["status"] == E.REPORTED and r["rows"][0]["failed"] is True and r["rows"][0]["class"] == "failed"


def test_a11_rb9d_row_is_not_evaluable_without_runs_and_reported_with_them():
    rows = E.assemble_rows({}, FILE["a11_logged"], FR, CH)
    r = next(x for x in rows if x["check_id"] == "d_tau_pm20")
    assert r["pass_or_fail"] == "NOT EVALUABLE" and r["label"] == "post hoc" and "reasoned, not tested" in r["note"]
    d = E.rb9d({8.0: _rec("D-tr", 45.0), 12.0: _rec("D-tr", 30.0)}, _rec("D-tr", 36.0), CH)
    r2 = next(x for x in E.assemble_rows({"rb9d": d}, FILE["a11_logged"], FR, CH) if x["check_id"] == "d_tau_pm20")
    assert r2["pass_or_fail"] == "REPORTED" and "tau 8 ms" in r2["value"] and r2["threshold"] == "reported only, no pass test"


def test_j_exit_run_is_the_path_J_at_the_episode_end_on_p2_and_nan_elsewhere():
    cfg = RL.expand("MS11_RB9D")[1]["cfg"]                       # tau 12 ms
    j = E.j_exit_run(cfg, 100.0, 170000, 1000.0)
    assert -22.0 < j < 0.0
    assert math.isnan(E.j_exit_run(cfg, float("nan"), 170000, 1000.0))
    cfg2 = copy.deepcopy(cfg)
    cfg2["path"]["name"] = "path_eta"
    assert math.isnan(E.j_exit_run(cfg2, 100.0, 170000, 1000.0))


# --- the MS11_RB9D list ---------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def rb9d_rows():
    return RL.expand("MS11_RB9D")


def test_the_rb9d_list_has_two_deterministic_runs_with_no_seed_key(rb9d_rows):
    assert len(rb9d_rows) == 2 and RL.EXPECTED_COUNTS["MS11_RB9D"] == 2
    for r in rb9d_rows:
        assert r["kind"] == "mf" and r["spawn_key"] is None and r["cfg"]["seeds"]["spawn_key"] is None and r["pre_registered"] is False
    assert RL.seed_keys(rb9d_rows) == []                          # the key family [11, ...] is untouched
    assert "MS11_RB9D" in RL.POSTHOC_LISTS and "MS11_RB9D" not in RL.PREREG_LISTS


def test_reading_a_only_tau_ms_changes_and_everything_else_is_the_stored_headline(rb9d_rows):
    head = C.resolve_config(ROOT / "configs/S5_ramp.yaml", {"path.T_ramp_s": 120.0})          # the stored headline S5ramp_0000_240de3ef73be
    assert C.short_hash(C.config_hash(head)) == "240de3ef73be"
    for r, tau in zip(rb9d_rows, (8.0, 12.0)):
        c = r["cfg"]
        assert c["model"]["tau_ms"] == tau and c["model"]["tau_d_ms"] == head["model"]["tau_d_ms"] == 5.0
        assert c["solver"] == head["solver"] and c["run"]["kind"] == head["run"]["kind"] == "mf"
        for k in ("T_ramp_s", "t_on_s", "eta_H", "eta_start", "eta_peak", "J0", "J_end", "name", "profile"):
            assert c["path"][k] == head["path"][k], k                                           # durations in seconds, eta numbers held
        assert c["path"]["eps"] == pytest.approx(3.5 / (120.0 / (tau / 1000.0)))                # derived slope: only through the longer or shorter ramp in tau units
        for blk in ("noise", "durations", "analysis"):
            if blk in head:
                assert c[blk] == head[blk], blk
        assert c["model"]["Delta"] == head["model"]["Delta"] and c["model"]["J"] == head["model"]["J"] and c["model"]["I_drive"] == head["model"]["I_drive"]


def test_the_rb9d_spec_in_the_yaml_matches_the_list_definition_file():
    p = RL.params("MS11_RB9D")
    s = CH["rb9d_parameter_spec"]
    assert p["tau_ms"] == s["changed"]["model.tau_ms"] and p["T_ramp_s"] == 120.0 and p["status"] == "FROZEN"


def test_the_four_pre_registered_lists_are_unchanged_by_the_new_list():
    froz = RL.frozen_hashes()
    old = {"MS11_S11": "51e747698e081925199f9f6a8902f6bbaa5bc937d9eedd4d986707257a99672d", "MS11_CTRL": "c9cedaac39f3236cea8cb2172232c3f963f284a1a41dfb1eb8b8e7cbb6a49537",
           "MS11_S13_MF": "b7be5147f9f58c2646d334e2afabaf786431511cca13ef6a3b5deb7491bf320a", "MS11_S13_NET": "9bc9283c2d5f2cd295c8c8e26d11154ebfbe4f83f7932eb8208f24815d1b702f"}
    for n, h in old.items():
        assert froz[n]["sha256"] == h and RL.list_sha256(RL.expand(n)) == h, n
    assert sum(RL.EXPECTED_COUNTS[n] for n in RL.PREREG_LISTS) == 236
    assert froz["MS11_RB9D"]["sha256"] == RL.list_sha256(RL.expand("MS11_RB9D")) and froz["MS11_RB9D"]["runs"] == 2
    assert froz["MS11_RB9D"]["definition_sha256"] == RL.definition_sha256("MS11_RB9D")


def test_rb9d_runs_are_not_a_repeat_of_any_other_run():
    allh = [x["hash"] for n in RL.ALL_LISTS for x in RL.expand(n)]
    assert len(set(allh)) == len(allh) == 238
    head = C.config_hash(C.resolve_config(ROOT / "configs/S5_ramp.yaml", {"path.T_ramp_s": 120.0}))
    assert head not in allh


def test_the_rb9d_list_is_in_the_launcher_and_check_launch_knows_it():
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_ms11_list", ROOT / "scripts/run_ms11_list.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    jobs = mod.build_jobs(["MS11_RB9D"], dry_run=True)
    assert len(jobs) == 2 and all(j["dry_run"] for j in jobs) and mod.RL.ALL_LISTS[-1] == "MS11_RB9D"
    assert MC.RULED_TOTAL == 238


def test_eta_delay_is_nan_not_an_error_for_the_control_config_which_has_no_eta_H():
    """Found by the fabricated-record test (DL-373): MS11_CTRL rows have path.eta_H = None, and the delay against eta_H is undefined for a constant-parameter run."""
    ctrl = RL.expand("MS11_CTRL")[0]["cfg"]
    assert ctrl["path"]["eta_H"] is None
    eta, delay = E._eta_delay(ctrl, 41.0)
    assert math.isfinite(eta) and math.isnan(delay)
    mf = RL.expand("MS11_S11")[0]["cfg"]
    eta2, delay2 = E._eta_delay(mf, 41.0)
    assert delay2 == pytest.approx(eta2 - mf["path"]["eta_H"])
