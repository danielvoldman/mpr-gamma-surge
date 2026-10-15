"""Profiles, paths P1-P5 and breakpoints (plan 10.5, 4.4; DL-060)."""
import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import ramps as R
from mprsurge.units import s_to_tau

T_ON, T = s_to_tau(5.0), s_to_tau(120.0)


def cfg_for(name="path_hypoxia", **path_keys):
    ov = {"path.name": name, "path.eta_start": 1.0, "path.eta_peak": 4.0}
    ov.update({f"path.{k}": v for k, v in path_keys.items()})
    return C.resolve_config(None, ov)


@pytest.mark.parametrize("g", [R.profile_linear, R.profile_sigmoid])
def test_profile_endpoints_and_monotone(g):
    x = np.linspace(-0.5, 1.5, 2001)
    y = g(x)
    assert g(0.0) == pytest.approx(0.0, abs=1e-12) and g(1.0) == pytest.approx(1.0, abs=1e-12)
    assert np.all(np.diff(y) >= -1e-15)
    assert y.min() >= 0.0 and y.max() <= 1.0


def test_sigmoid_centre_half_is_symmetric():
    assert R.profile_sigmoid(0.5) == pytest.approx(0.5, abs=1e-12)              # centre 0.5 is UNSOURCED (DL-060)
    assert R.profile_sigmoid(0.25) + R.profile_sigmoid(0.75) == pytest.approx(1.0, abs=1e-12)


def test_p1_eta_runs_start_to_peak_over_t_ramp():
    c = cfg_for("path_eta")
    p = R.make_path(c)
    assert p.eta(0.0) == 1.0 and p.eta(T_ON) == 1.0 and p.eta(T_ON + T) == 4.0 and p.eta(T_ON + 5 * T) == 4.0
    assert p.eta(T_ON + T / 2) == pytest.approx(2.5)
    assert np.allclose(p.J(np.array([0.0, T_ON + T])), c["model"]["J"])        # J fixed on P1
    assert np.allclose(p.breakpoints, [T_ON, T_ON + T]) and p.t_ramp_end == T_ON + T


def test_p2_J_reaches_zero_at_t_on_plus_1p25_T_and_hold_starts_after():
    c = cfg_for("path_hypoxia")
    p = R.make_path(c)
    assert p.J(T_ON + 0.25 * T) == pytest.approx(c["path"]["J0"])
    assert p.J(T_ON + 1.25 * T) == 0.0 and p.J(T_ON + 1.25 * T - 1e-3 * T) != 0.0
    assert p.t_ramp_end == pytest.approx(T_ON + 1.25 * T)                       # the hold starts here (CP14)
    assert np.allclose(p.breakpoints, [T_ON, T_ON + 0.25 * T, T_ON + T, T_ON + 1.25 * T])
    jj = p.J(np.linspace(0, p.t_ramp_end, 500))                                 # the run covers the full J path
    assert jj[0] == c["path"]["J0"] and jj[-1] == 0.0 and np.all(np.diff(jj) >= -1e-12)


def test_breakpoints_are_the_corners_for_every_path():
    expect = {
        "path_eta": [0, 1],
        "path_hypoxia": [0, 0.25, 1, 1.25],
        "path_drive": [0, 0.1, 0.25, 0.4, 0.5, 1, 1.25],                        # rise 0.1, plateau 0.3, fall 0.1
        "path_delta_up": [0, 0.25, 1, 1.25],
        "path_delta_down": [0, 0.25, 1, 1.25],
        "path_updown": [0, 1, 2],
    }
    for name, fr in expect.items():
        extra = {"I_amp": 1.0} if name == "path_drive" else {}
        got = R.breakpoints(cfg_for(name, **extra))
        assert np.allclose(got, T_ON + np.array(fr) * T, rtol=0, atol=1e-9), name


def test_p3_trapezoid():
    p = R.make_path(cfg_for("path_drive", I_amp=2.0))
    assert p.I(T_ON) == 0.0 and p.I(T_ON + 0.1 * T) == pytest.approx(2.0)
    assert p.I(T_ON + 0.25 * T) == pytest.approx(2.0) and p.I(T_ON + 0.4 * T) == pytest.approx(2.0)
    assert p.I(T_ON + 0.45 * T) == pytest.approx(1.0) and p.I(T_ON + 0.5 * T) == pytest.approx(0.0, abs=1e-12)
    assert p.I(T_ON + 2 * T) == 0.0


def test_p4_delta_factor_and_p5_up_down():
    p = R.make_path(cfg_for("path_delta_up", Delta_factor=1.5))
    assert p.Delta(T_ON) == pytest.approx(0.3) and p.Delta(T_ON + T) == pytest.approx(0.45)
    p = R.make_path(cfg_for("path_delta_down", Delta_factor=2 / 3))
    assert p.Delta(T_ON + T) == pytest.approx(0.2)
    p = R.make_path(cfg_for("path_updown"))
    assert p.eta(T_ON + T) == 4.0 and p.eta(T_ON + 2 * T) == pytest.approx(1.0)
    assert p.eta(T_ON + 3 * T) == pytest.approx(1.0)
    assert p.t_ramp_end == pytest.approx(T_ON + 2 * T)                          # P5 doubles T_ramp (DL-060)
    assert np.allclose(p.J(np.array([0.0, T_ON + T])), -21.0)


def test_sigmoid_profile_applies_to_eta_and_unresolved_path_raises():
    p = R.make_path(cfg_for("path_eta", profile="sigmoid"))
    assert p.eta(T_ON) == pytest.approx(1.0) and p.eta(T_ON + T) == pytest.approx(4.0)
    assert p.eta(T_ON + T / 2) == pytest.approx(2.5)
    with pytest.raises(C.ConfigError):
        R.make_path(C.resolve_config(None, {"path.name": "path_eta"}))
