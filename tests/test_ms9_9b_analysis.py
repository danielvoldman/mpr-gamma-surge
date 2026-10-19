"""MS9 9b: re-timing arithmetic, record classification and the preliminary A9 label rules (DL-216). Nothing integrates."""
import json

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a9
from mprsurge.analysis import ms9_classify as MCL
from mprsurge.analysis import ms9_retime as RT
from mprsurge.analysis import ms9_runlist as RL


# --- re-timing arithmetic ------------------------------------------------------------------------

def test_the_sample_is_a_3x3_stratified_sample_plus_the_cell_nearest_the_headline():
    s = RT.sample_cells()
    assert len(s) == 10 and len(set(s)) == 10 and s[-1] == (14, 12)
    assert {c for c in s[:9]} == {(i, j) for i in (0, 15, 29) for j in (0, 15, 29)}


def _walls(f):
    return {c: f(c) for c in RT.SAMPLE}


def test_a_flat_sample_gives_the_same_three_predictions():
    p = RT.map1_predictions(_walls(lambda c: 150.0), 10)
    for k in ("weighted_9a_method", "index_interpolation", "worst_case"):
        assert p[k]["total_s"] == pytest.approx(900 * 150.0 / 10) and p[k]["prediction_s"] == pytest.approx(13500.0)
        assert p[k]["verdict"] == "PASS" and p[k]["over_one_hour"]
    assert p["worst_case"]["limit_s"] == pytest.approx(1.5 * 4.1 * 3600.0)


def test_index_interpolation_is_exact_for_a_function_linear_in_the_indices():
    p = RT.map1_predictions(_walls(lambda c: 100.0 + 2.0 * c[0] + 3.0 * c[1]), 10)
    exact = sum(100.0 + 2.0 * i + 3.0 * j for i in range(30) for j in range(30))
    assert p["index_interpolation"]["sum_s"] == pytest.approx(exact)
    assert p["index_interpolation"]["check_cell_14_12"]["ratio"] == pytest.approx(1.0)


def test_worst_case_is_the_slowest_cell_everywhere_and_the_rule_is_1_5_times_the_allowance():
    w = _walls(lambda c: 200.0)
    w[(0, 0)] = 900.0
    p = RT.map1_predictions(w, 10)
    assert p["worst_case"]["sum_s"] == pytest.approx(900 * 900.0) and p["worst_case"]["prediction_s"] == pytest.approx(81000.0)
    assert p["worst_case"]["verdict"] == "FAIL" and p["weighted_9a_method"]["prediction_s"] < p["worst_case"]["prediction_s"]
    assert RT.ALLOWANCE_H == 4.1 and p["worst_case"]["limit_s"] == pytest.approx(6.15 * 3600.0)


def test_the_longest_cell_bounds_the_wall_below():
    p = RT.map1_predictions(_walls(lambda c: 300.0), 900)
    assert p["worst_case"]["prediction_s"] == pytest.approx(300.0)


def test_a_missing_sample_cell_is_refused():
    w = _walls(lambda c: 1.0)
    del w[(29, 29)]
    with pytest.raises(ValueError):
        RT.map1_predictions(w)


# --- classification of stored records ------------------------------------------------------------

FI = {"threshold": 0.217622}


def _burst(T=40.0, fs=1000.0, f=50.0, amp=1.0, burst=(10.0, 30.0)):
    t = np.arange(int(T * fs)) / fs
    v = np.full_like(t, -0.6)
    m = (t >= burst[0]) & (t < burst[1])
    v[m] += amp * np.sin(2 * np.pi * f * t[m])
    return v


def test_a_flat_trace_is_the_quiet_class_in_both_modes():
    v = np.full(40000, -0.6)
    rd, _ = MCL.classify_array("D", v, 1000.0, 5.0, 10.0, FI["threshold"])
    assert rd.cls == "D-none" and MCL.row_from_result(rd, "", "D", 10.0)["quiet"]


def test_a_strong_burst_is_not_quiet_and_a_nonfinite_record_is_failed():
    rd, _ = MCL.classify_array("D", _burst(), 1000.0, 5.0, 10.0, FI["threshold"])
    assert rd.cls in ("D-tr", "D-sus") and not MCL.row_from_result(rd, "", "D", 10.0)["quiet"]
    v = np.full(40000, -0.6)
    v[5] = np.nan
    rf, _ = MCL.classify_array("D", v, 1000.0, 5.0, 10.0, FI["threshold"])
    assert rf.cls == "failed" and not MCL.row_from_result(rf, "", "D", 10.0)["quiet"]


def _write_record(tmp_path, name, cfg_over, v, status="ok"):
    cfg = C.resolve_config(C.repo_root() / "configs/ms9/nc1.yaml", cfg_over)
    rec = P.make_run_record(cfg, P.environment_info(with_julia=False), name=name, status=status, wall_time_s=1.0)
    P.write_run_record(rec, tmp_path / f"{name}.json")
    np.savez(tmp_path / f"{name}.npz", v=v)
    return tmp_path / f"{name}.json"


def test_classify_record_reads_the_record_and_reports_failed_status(tmp_path):
    ov = {"path.eta_start": 1.396, "path.eta_peak": -2.104, "path.T_ramp_s": 10.0}
    row = MCL.classify_record(_write_record(tmp_path, "a", ov, np.full(20000, -0.6)), FI)
    assert row["class"] == "D-none" and row["quiet"] and row["mode"] == "D" and row["W_s"] > 0 and not row["supplementary"]
    row = MCL.classify_record(_write_record(tmp_path, "b", ov, np.full(20000, -0.6), status="failed"), FI)
    assert row["class"] == "failed" and not row["quiet"]


def test_stop_rule_set_and_supplementary_summary():
    def r(cls, sup=False, T=10.0, mode="N", fam="NC1"):
        return {"class": cls, "quiet": cls in ("NS", "D-none"), "supplementary": sup, "mode": mode, "T_ramp_s": T, "W_s": 0.5, "step_s": 0.25,
                "run": f"{fam}_{cls}", "family": fam, "Delta": 0.3, "tau_d_ms": 5.0, "reason": "", "status": "ok", "provisional": ""}
    rows = [r("D-none", mode="D"), r("D-sus", mode="D"), r("failed", mode="D"), r("S+", sup=True), r("NS", sup=True), r("NS", sup=True)]
    assert [x["class"] for x in MCL.unexpected(rows)] == ["D-sus", "failed"]            # supplementary rows never stop
    g = MCL.supplementary_per_window(rows)
    assert g[0]["n"] == 3 and g[0]["non_NS"] == 1 and g[0]["fraction_non_NS"] == pytest.approx(1 / 3)
    assert "STOP RULE" in MCL.nc1_report(rows)


# --- A9 label rules (preliminary) ----------------------------------------------------------------

H_OK = {"eta_bar": 3.0, "omega": 1.0, "f_hz": 40.0}


def test_labels_follow_the_order_and_record_all_that_apply():
    L = a9.labels("D-none", False, H_OK, 0.5, (1.0, 20.0), 0.3, 5.0, 1.0)         # 1 s x 40 Hz = 40 cycles: no label applies
    assert L == {"all": [], "primary": None}
    L = a9.labels("D-none", False, None, None, None, 0.3, 5.0, 0.0)
    assert L["all"] == ["a", "b"] and L["primary"] == "a"
    assert a9.labels("D-none", False, H_OK, 0.2, (1.0, 20.0), 0.3, 5.0, 1.0)["primary"] == "a"             # Delta above the largest with a Hopf point
    assert a9.labels("D-none", False, H_OK, 0.5, (1.0, 20.0), 0.3, 25.0, 1.0)["primary"] == "b"           # tau_d above the interval
    assert a9.labels("D-none", False, {**H_OK, "f_hz": 20.0}, 0.5, (1, 20), 0.3, 5.0, 100.0)["all"] == ["c"]
    assert a9.labels("D-none", False, H_OK, 0.5, (1, 20), 0.3, 5.0, 0.1)["all"] == ["d"]                   # 0.1 s x 40 Hz = 4 cycles
    assert a9.labels("D-sus", False, H_OK, 0.5, (1, 20), 0.3, 5.0, 1.0) == {"all": ["e"], "primary": "e"}
    assert a9.labels("D-none", True, H_OK, 0.5, (1, 20), 0.3, 5.0, 1.0) == {"all": ["f"], "primary": "f"}
    assert a9.labels("D-sus", True, None, 0.5, (1, 20), 0.3, 5.0, 0.0)["all"] == ["e", "f"]
    assert a9.labels("failed", False, H_OK, 0.5, (1, 20), 0.3, 5.0, 1.0) == {"all": ["failed"], "primary": "failed"}


def test_time_inside_the_region():
    assert a9.time_inside([0, 1, 2], [-1, 1, 1]) == pytest.approx(1.5)
    assert a9.time_inside([0, 1], [-1, -1]) == 0.0 and a9.time_inside([0, 2], [1, 1]) == 2.0
    assert a9.time_inside([0, 1, 2], [1, -1, -1]) == pytest.approx(0.5)


def test_hopf_tables_at_the_headline():
    h = a9.hopf_point(-21.0, 0.3, 5.0)
    assert h is not None and h["eta_bar"] == pytest.approx(2.8960461989737856, abs=1e-6) and 25.0 < h["f_hz"] < 200.0
