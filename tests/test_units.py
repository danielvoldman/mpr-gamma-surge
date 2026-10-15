"""Unit conversions (plan 3.3, Table 10.1) and the RB9a dimensional-vs-nondimensional run check."""
import math

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from mprsurge import config as C
from mprsurge import simulate_mf as S
from mprsurge import units


def test_tau_to_ms_at_ten_ms():
    assert units.tau_to_ms(1.0) == pytest.approx(10.0, rel=1e-12)
    assert units.tau_to_ms(2.5, tau_ms=10.0) == pytest.approx(25.0, rel=1e-12)


def test_frequency_and_rate_to_hz_is_100_per_tau():
    assert units.freq_to_hz(0.4) == pytest.approx(40.0, rel=1e-12)
    assert units.rate_to_hz(0.05) == pytest.approx(5.0, rel=1e-12)


def test_conversions_scale_with_tau_ms():
    assert units.freq_to_hz(1.0, tau_ms=20.0) == pytest.approx(50.0, rel=1e-12)
    assert units.tau_to_ms(1.0, tau_ms=20.0) == pytest.approx(20.0, rel=1e-12)


def test_one_minute_is_6000_tau():
    assert units.s_to_tau(60.0) == pytest.approx(6000.0, rel=1e-12)
    assert units.s_to_tau(165.0) == pytest.approx(16500.0, rel=1e-12)  # headline P2 run


@pytest.mark.parametrize("x", [0.0, 1e-3, 0.37, 12.5])
def test_round_trips(x):
    assert units.ms_to_tau(units.tau_to_ms(x)) == pytest.approx(x, rel=1e-12, abs=1e-15)
    assert units.tau_to_s(units.s_to_tau(x)) == pytest.approx(x, rel=1e-12, abs=1e-15)
    assert units.hz_to_freq(units.freq_to_hz(x)) == pytest.approx(x, rel=1e-12, abs=1e-15)
    assert units.hz_to_rate(units.rate_to_hz(x)) == pytest.approx(x, rel=1e-12, abs=1e-15)


def test_period_and_frequency_consistent():
    # a 40 Hz oscillation has a 25 ms period = 2.5 tau
    f_tau = units.hz_to_freq(40.0)
    assert math.isclose(1.0 / f_tau, 2.5, rel_tol=1e-12)
    assert math.isclose(units.tau_to_ms(1.0 / f_tau), 25.0, rel_tol=1e-12)


@pytest.mark.parametrize("tau_ms", [10.0, 20.0])
def test_rb9a_dimensional_and_nondimensional_runs_agree_within_half_a_percent(tau_ms):
    # Plan 6.5/Table 7.2 RB9(a): within 0.5%. The dimensional form is plan 3.1 (t in ms, r in 1/ms):
    #   tau dr/dt = Delta/(pi tau) + 2 r v;  tau dv/dt = v^2 + eta + J tau s + I - (pi tau r)^2;
    #   tau_d ds/dt = -s + r.  Same start state and delta0 at t_on. Metric: max |difference| over
    # the run divided by the max |value| of that variable (r*tau compared with the tau-unit r).
    cfg = C.resolve_config(None, {"model.tau_ms": tau_ms, "path.name": "path_eta", "path.eta_start": 1.0,
                                  "path.eta_peak": 4.0, "path.T_ramp_s": 1.0, "path.t_on_s": 0.5,
                                  "durations.hold_s": 0.5})
    res = S.run_mf(cfg)["arrays"]
    m, p = cfg["model"], cfg["path"]
    tau, tau_d = tau_ms, m["tau_d_ms"]
    t_on, T = p["t_on_s"] * 1e3, p["T_ramp_s"] * 1e3
    eta = lambda t: p["eta_start"] + (p["eta_peak"] - p["eta_start"]) * min(max((t - t_on) / T, 0.0), 1.0)

    def f(t, y):
        r, v, s = y
        return [(m["Delta"] / (np.pi * tau) + 2 * r * v) / tau,
                (v * v + eta(t) + m["J"] * tau * s + m["I_drive"] - (np.pi * tau * r) ** 2) / tau,
                (r - s) / tau_d]
    from mprsurge.models.fixed_points import stable_fixed_point
    r0, v0, s0 = stable_fixed_point(p["eta_start"], m["J"], m["Delta"], m["I_drive"], "M3",
                                    units.ms_to_tau(tau_d, tau))
    y = [r0 / tau, v0, s0 / tau]
    t_end = res["t_ms"][-1]
    t_all, Y = [], []
    for a, b in ((0.0, t_on), (t_on, t_on + T), (t_on + T, t_end)):
        if a == t_on:
            y[1] += cfg["solver"]["delta0"]
        grid = res["t_ms"][(res["t_ms"] >= a - 1e-9) & (res["t_ms"] < b - 1e-9)]
        if b == t_end:
            grid = res["t_ms"][res["t_ms"] >= a - 1e-9]
        sol = solve_ivp(f, (a, b), y, method="DOP853", rtol=1e-10, atol=1e-13, t_eval=np.append(grid, b)
                        if b != t_end else grid, max_step=0.5 * tau)
        n = len(grid)
        t_all.append(grid)
        Y.append(sol.y[:, :n])
        y = list(sol.y[:, -1])
    Yd = np.concatenate(Y, axis=1)
    assert np.concatenate(t_all).shape == res["t_ms"].shape
    for dim, nd in ((Yd[0] * tau, res["r"]), (Yd[1], res["v"]), (Yd[2] * tau, res["s"])):
        assert np.max(np.abs(dim - nd)) / np.max(np.abs(nd)) < 0.005
