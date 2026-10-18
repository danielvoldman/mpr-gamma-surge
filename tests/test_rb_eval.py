"""8f RB3 / RB5 / RB6 evaluators (DL-181 to DL-185). Synthetic table, known answers; no stored result is read."""
import math

import numpy as np
import pandas as pd
import pytest

from mprsurge.analysis import rb_eval as R

FV = {"floor_levels": [1.59e-9, 1.59e-6, 1.59e-3], "dt_ladder": [1e-3, 5e-4, 2.5e-4, 1e-4], "dt_default": 1e-3, "rb6_max": 0.05,
      "c_T_ramp_s": [56.23, 100.0, 177.8, 316.2], "d_T_ramp_s": [56.23, 100.0, 177.8, 316.2], "d_max_changes": 1}


def floor_df(delays, cross=None, rel_fine=1.0):
    """delays[level] = value for all 10 seeds of that level at every rung; the finest rung is scaled by rel_fine."""
    rows = []
    for lv, d in enumerate(delays):
        for dt in FV["dt_ladder"]:
            for s in range(10):
                x = d * (rel_fine if dt == 1e-4 else 1.0)
                rows.append({"family": f"floor_l{lv}", "d43_level": float(lv), "heun_dt_tau": dt, "seed": float(s), "delay_eta": x,
                             "delay_eta_cross": x if cross is None else cross[lv], "cls": "S-abs"})
    return pd.DataFrame(rows)


def test_median_pair_and_strict_decrease():
    e, p, m = R.median_pair([1.0, float("nan"), 3.0])
    assert (e, m) == (2.0, 1) and math.isnan(p)
    assert R.strictly_decreasing([-1.0, -2.0, -3.0]) is True
    assert R.strictly_decreasing([-1.0, -1.0, -3.0]) is False        # a tie fails (F-15)
    assert R.strictly_decreasing([-1.0, float("nan"), -3.0]) is None


def test_rb3b_verdict_flips_between_onsets():
    df = floor_df([-1.5, -1.5, -1.0], cross=[-0.001, -0.04, -0.1])
    r = R.rb3b(df, FV)
    assert r["status_by_onset"] == {"class": "DOES NOT MEET", "cross": "MEETS"} and r["verdict_flips_between_onsets"]


def test_rb6_relative_change_against_bound():
    ok = R.rb6_heun(floor_df([-1.0, -2.0, -3.0], rel_fine=1.04), FV)
    assert all(x["status"] == "MEETS" for x in ok["by_onset"]["class"]) and ok["by_onset"]["class"][0]["rel_change"] == pytest.approx(0.04)
    bad = R.rb6_heun(floor_df([-1.0, -2.0, -3.0], rel_fine=1.06), FV)
    assert bad["status_by_onset"]["class"] == "DOES NOT MEET"


def test_rb3d_counts_class_changes_per_path():
    rows = []
    for fam, cls in (("p1_linear", ["D-sus", "D-sus", "D-sus", "D-none"]), ("p1_sigmoid", ["D-none", "D-sus", "D-none", "D-none"]), ("p2_linear", ["D-tr"] * 4),
                     ("p2_sigmoid", ["D-tr"] * 4), ("p5_linear", ["D-tr"] * 4), ("p5_sigmoid", ["D-tr"] * 4)):
        rows += [{"family": fam, "T_ramp_s": T, "cls": c} for T, c in zip(FV["d_T_ramp_s"], cls)]
    r = R.rb3d(pd.DataFrame(rows), FV)
    assert {p: v["n_class_changes"] for p, v in r["by_path"].items()} == {"P1": 2, "P2": 0, "P5": 0}
    assert r["by_path"]["P1"]["within_bound"] is False and "sum_over_paths" not in r
    assert r["by_path"]["P1"]["changed_at_T_ramp_s"] == [56.23, 177.8]


def test_p2_surge_counts_window_membership():
    rows = [{"family": "p2_linear", "T_ramp_s": T, "cls": "D-tr" if T > 2 else "D-none"} for T in (1.0, 10.0, 100.0, 1000.0)]
    out = R.p2_surge_counts(pd.DataFrame(rows), FV)["rows"]["mode D, P2 linear"]
    assert (out["n_surge_inside_window"], out["n_runs_inside_window"], out["n_surge_outside_window"], out["n_runs_outside_window"]) == (1, 1, 2, 3)
    assert out["T_ramp_with_no_surge_run"] == [1.0]


def test_primary_readings_follow_rulings():
    r = R.rb3b(floor_df([-1.5, -1.5, -1.0], cross=[-0.001, -0.04, -0.1]), FV)
    assert r["primary"]["onset"] == "cross" and r["primary"]["status"] == "MEETS" and r["primary"]["secondary"]["status"] == "DOES NOT MEET"
    h = R.rb6_heun(floor_df([-1.0, -2.0, -3.0]), FV)
    assert h["primary"]["onset"] == "cross" and h["primary"]["status"] == "MEETS"
    assert R.RULINGS_8F2.keys() == {str(i) for i in range(1, 9)}


def test_rb3a_primary_judges_testable_only_and_keeps_signed_time_errors():
    rows = [{"list": "S5", "mode": "D", "in_range": True, "family": "p1_linear", "path": "P1", "profile": "linear", "start_distance": 1.5, "T_ramp_s": T,
             "cls": "D-sus", "eta_pred": 1.0, "eta_onset_cross": 1.0 + e, "eta_onset": float("nan"), "match_err_steps": abs(e) / 0.025,
             "match_err_steps_cls": float("nan"), "eta_const_at_t_pred": c, "onset_cross_minus_t_pred_s": ts, "t_pred_s": 10.0, "onset_cross_s": 10.0 + ts}
            for T, e, c, ts in ((1.0, 0.01, False, -0.5), (2.0, 0.0, True, 3.0), (3.0, 0.05, False, 0.7))]
    rows.append({"list": "S5", "mode": "D", "in_range": False, "family": "S5ramp", "path": "P2", "profile": "linear", "start_distance": 1.5, "T_ramp_s": 120.0,
                 "cls": "D-tr", "eta_pred": 1.0, "eta_onset_cross": 1.0, "eta_onset": 1.0, "match_err_steps": 0.0, "match_err_steps_cls": 0.0, "eta_const_at_t_pred": False,
                 "onset_cross_minus_t_pred_s": 0.0, "t_pred_s": 1.0, "onset_cross_s": 1.0, "I_min": 0.0})
    df = pd.DataFrame(rows)
    fv = FV | {"grid_step": 0.025, "a_onset_tol_text": "one step", "coverage_text": "0 to 2 of 13"}
    a = R.rb3a(df, fv)["primary"]
    assert (a["n_judged"], a["n_within_one_step"], a["status"]) == (2, 1, "DOES NOT MEET")
    assert a["constant_eta_runs_no_verdict"][0]["time_err_cross_s_signed"] == 3.0 and a["constant_eta_runs_no_verdict"][0]["verdict"] is None
