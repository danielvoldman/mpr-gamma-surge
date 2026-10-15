"""Mode D: run_mf (plan 6.2, 10.4; DL-072)."""
import time

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import simulate_mf as S
from mprsurge.errors import RunTimeout
from mprsurge.models.fixed_points import stable_fixed_point
from mprsurge.units import hz_to_rate

SHORT = {"path.name": "path_eta", "path.eta_start": 1.0, "path.eta_peak": 4.0, "path.T_ramp_s": 1.0,
         "path.t_on_s": 0.5, "durations.hold_s": 0.5}


def cfg_d(**extra):
    return C.resolve_config(None, {**SHORT, **extra})


def test_start_is_the_stable_fixed_point_and_kick_is_at_t_on():
    cfg = cfg_d()
    res = S.run_mf(cfg)
    a = res["arrays"]
    r0, v0, s0 = stable_fixed_point(1.0, -21.0, 0.3, 0.0, "M3", 0.5)
    assert (a["r"][0], a["v"][0], a["s"][0]) == pytest.approx((r0, v0, s0), rel=1e-12)
    assert a["v"][499] == pytest.approx(v0, abs=1e-11)                       # still on the fixed point
    assert a["v"][500] - v0 == pytest.approx(cfg["solver"]["delta0"], abs=1e-9)   # delta0 on v at t_on
    assert res["flags"]["start"] == "stable_fixed_point" and not res["flags"]["retried_with_radau"]


def test_output_is_on_the_1ms_grid_with_the_full_duration():
    a = S.run_mf(cfg_d())["arrays"]
    assert np.allclose(np.diff(a["t_ms"]), 1.0, atol=1e-9) and a["t_ms"][0] == 0.0
    assert a["t_ms"][-1] == pytest.approx(2000.0)                   # t_on 0.5 + T_ramp 1 + hold 0.5 (s)
    assert a["eta"][0] == 1.0 and a["eta"][-1] == 4.0


def test_p2_runs_to_the_end_of_the_j_ramp_plus_hold():
    cfg = cfg_d(**{"path.name": "path_hypoxia", "path.eta_start": 2.0, "path.eta_peak": 4.0})
    a = S.run_mf(cfg)["arrays"]
    assert a["t_ms"][-1] == pytest.approx((0.5 + 1.25 * 1.0 + 0.5) * 1000.0)     # hold after 1.25 T_ramp (CP14)
    assert a["J"][0] == -21.0 and a["J"][-1] == 0.0


def test_y0_overrides_the_start_devalle_fig3_values():
    y0 = S.devalle_fig3_state("M3")
    assert y0 == (hz_to_rate(5.0), 0.0, hz_to_rate(5.0)) and y0[0] == pytest.approx(0.05)
    res = S.run_mf(cfg_d(), y0=y0)
    assert (res["arrays"]["r"][0], res["arrays"]["v"][0]) == (0.05, 0.0) and res["flags"]["start"] == "explicit"
    with pytest.raises(ValueError, match="shape"):
        S.run_mf(cfg_d(), y0=[0.05, 0.0])


def test_solve_ivp_gets_t_eval_and_never_dense_output(monkeypatch):
    seen = []
    real = S.solve_ivp

    def spy(*a, **kw):
        seen.append(kw)
        return real(*a, **kw)
    monkeypatch.setattr(S, "solve_ivp", spy)
    S.run_mf(cfg_d())
    assert len(seen) >= 3                                           # piecewise: t_on, ramp end, end
    assert all(kw["t_eval"] is not None and not kw.get("dense_output") for kw in seen)
    assert all(kw["method"] == "DOP853" and kw["max_step"] == 0.05 for kw in seen)


def test_piecewise_segments_split_at_breakpoints(monkeypatch):
    spans = []
    real = S.solve_ivp
    monkeypatch.setattr(S, "solve_ivp", lambda f, span, *a, **kw: spans.append(span) or real(f, span, *a, **kw))
    S.run_mf(cfg_d())
    assert [s[0] for s in spans] == pytest.approx([0.0, 50.0, 150.0]) and spans[-1][1] == pytest.approx(200.0)


def test_dop853_failure_gets_one_radau_retry_and_is_flagged(monkeypatch):
    real = S.solve_ivp
    calls = []

    def flaky(f, span, y0, *a, method="DOP853", **kw):
        calls.append(method)
        if method == "DOP853":
            class Failed:
                status, message = -1, "forced failure"
            return Failed()
        return real(f, span, y0, *a, method=method, **kw)
    monkeypatch.setattr(S, "solve_ivp", flaky)
    res = S.run_mf(cfg_d())
    assert calls[0] == "DOP853" and set(calls[1:]) == {"Radau"}
    f = res["flags"]
    assert f["retried_with_radau"] is True and "forced failure" in f["first_failure"] and f["solver"] == "Radau"
    assert "Radau" in res["message"] and np.all(np.isfinite(res["arrays"]["v"]))


def test_radau_failure_is_not_retried(monkeypatch):
    class Failed:
        status, message = -1, "forced failure"
    monkeypatch.setattr(S, "solve_ivp", lambda *a, **kw: Failed())
    with pytest.raises(S.SolverFailure):
        S.run_mf(cfg_d(**{"solver.method": "Radau"}))


def test_wall_limit_stops_a_long_solve_ivp_and_is_not_retried():
    cfg = cfg_d(**{"path.T_ramp_s": 120.0})                         # many seconds of DOP853
    t0 = time.monotonic()
    with pytest.raises(RunTimeout):
        S.run_mf(cfg, deadline=t0 + 0.3)
    assert time.monotonic() - t0 < 5.0
