"""A5-vs-S4 and K7 amplitude checks on synthetic data (MS6 step 6e, DL-129)."""
import numpy as np

from mprsurge.analysis import cycle_check as cc


def test_known_linear_a2_gives_slope_and_r2():
    h = 4.0
    td = h + np.array([-0.2, 0.05, 0.15, 0.3, 0.5, 0.7, 0.9, 1.0, 1.5])
    amp = np.sqrt(np.maximum(0.0, 2.5 * (td - h)))
    f = cc.amplitude_fit(td, amp, h)
    assert f["n_points"] == 6                      # 0.15 to 1.0; -0.2, 0.05 and 1.5 outside the window
    assert np.isclose(f["slope"], 2.5) and np.isclose(f["intercept"], 0.0, atol=1e-12) and f["r2"] > 0.999999 and f["pass"]


def test_nonlinear_a2_fails():
    h = 4.0
    td = h + np.linspace(0.1, 1.0, 8)
    f = cc.amplitude_fit(td, np.sqrt((td - h) ** 3), h)
    assert not f["pass"]


def test_exclusion_boundary():
    p = np.array([2.6, 2.796, 2.896, 2.996, 3.096])
    m = cc.near_mask(p, 2.896, 0.1)
    assert m.tolist() == [False, True, True, True, False]


def test_judge_and_two_percent_rule():
    p = np.array([3.0, 4.0, 5.0])
    a5 = np.array([1.0, 2.0, 3.0])
    ok = cc.judge(p, a5 * 1.01, a5, np.zeros(3, bool))
    bad = cc.judge(p, a5 * np.array([1.0, 1.0, 1.03]), a5, np.zeros(3, bool))
    skip = cc.judge(p, a5 * np.array([1.0, 1.0, 1.03]), a5, np.array([False, False, True]))
    assert ok["pass"] and not bad["pass"] and skip["pass"] and skip["judged"].tolist() == [True, True, False]


def test_interp_nan_outside_and_exact_at_nodes():
    p, a = np.array([1.0, 2.0, 3.0]), np.array([1.0, 4.0, 9.0])
    y = cc.interp_branch(p, a, [0.5, 2.0, 3.5])
    assert np.isnan(y[0]) and y[1] == 4.0 and np.isnan(y[2])


def test_hysteresis_flag_fires_on_shifted_down_branch():
    up = np.array([0.0, 1.0, 2.0, 3.0])
    assert not cc.hysteresis(up, up + 1e-6)["flag"]
    assert cc.hysteresis(up, np.array([0.0, 1.0, 2.0, 3.0]) * 1.05)["flag"]
