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
    assert r["by_path"]["P1"]["within_bound"] is False and r["sum_over_paths"] == 2


def test_p2_surge_counts_window_membership():
    rows = [{"family": "p2_linear", "T_ramp_s": T, "cls": "D-tr" if T > 2 else "D-none"} for T in (1.0, 10.0, 100.0, 1000.0)]
    out = R.p2_surge_counts(pd.DataFrame(rows), FV)["rows"]["mode D, P2 linear"]
    assert (out["n_surge_inside_window"], out["n_runs_inside_window"], out["n_surge_outside_window"], out["n_runs_outside_window"]) == (1, 1, 2, 3)
    assert out["T_ramp_with_no_surge_run"] == [1.0]
