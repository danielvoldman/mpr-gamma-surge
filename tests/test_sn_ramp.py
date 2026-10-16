"""A3 analysis module (MS4 4c): seeded synthetic trajectories; nothing integrates, nothing reads results/."""
import numpy as np
import pytest

from mprsurge.analysis import sn_ramp

FS = 1000.0
T = 30.0
ETA0, ETA1 = -6.743527161657844, -2.136134086195692
FOLD = -3.136134086195692
BAND = (25.0, 100.0)
TJ = 20.0


def _series(ring, seed=0, jump=True):
    rng = np.random.default_rng(seed)
    t = np.arange(0.0, T, 1 / FS)
    eta = ETA0 + (ETA1 - ETA0) * t / T
    v = 1e-5 * rng.standard_normal(t.size)
    if jump:
        on = t >= TJ
        tau = np.clip(t - TJ, 0, None)
        r = 0.1 + 0.9 * on + 0.02 * on * ring(tau)
        v = v + on * ring(tau)
    else:
        r = 0.1 + 0.9 / (1 + np.exp(-(t - TJ) / 3.0))      # smooth, a few seconds wide
    return t * 1e3, r, v, eta


def _ring(g, f=60.0):
    return lambda tau: np.exp(-g * tau) * np.sin(2 * np.pi * f * tau)


def test_known_jump_time_and_eta():
    t_ms, r, v, eta = _series(_ring(3.0))
    out = sn_ramp.analyse_trajectory(t_ms, r, v, eta, FOLD, BAND)
    assert out["jump"] and out["direction"] == 1
    assert out["t_jump_s"] == pytest.approx(TJ, abs=2e-3)
    assert out["eta_jump"] == pytest.approx(ETA0 + (ETA1 - ETA0) * TJ / T, abs=1e-3)
    assert out["offset"] == pytest.approx(out["eta_jump"] - FOLD)
    assert out["offset_steps"] == pytest.approx(out["offset"] / 0.05)


def test_five_cycle_damped_ring_is_damped():
    out = sn_ramp.analyse_trajectory(*_series(_ring(100.0)), FOLD, BAND)
    assert out["rate"] < 0 and out["ring_class"] == "damped"


def test_slowly_damped_ring_over_ten_cycles_is_damped():
    out = sn_ramp.analyse_trajectory(*_series(_ring(3.0)), FOLD, BAND)
    assert out["cycles_fit"] > 9.5            # the window reaches 10 cycles
    assert out["rate"] < 0 and out["ring_class"] == "damped"


def test_constant_amplitude_oscillation_is_non_damped():
    out = sn_ramp.analyse_trajectory(*_series(_ring(0.0)), FOLD, BAND)
    assert not out["rate"] < -2 * out["se"]
    assert out["ring_class"] == "non_damped"


def test_smooth_ramp_has_no_jump():
    out = sn_ramp.analyse_trajectory(*_series(None, jump=False), FOLD, BAND)
    assert not out["jump"] and out["ring_class"] == "no_jump"
    assert np.isnan(out["t_jump_s"]) and np.isnan(out["rate"])


def test_classify_ring_boundary():
    assert sn_ramp.classify_ring(-2.01, 1.0) == "damped"
    assert sn_ramp.classify_ring(-2.0, 1.0) == "non_damped"
    assert sn_ramp.classify_ring(np.nan, np.nan) == "undetermined"


def test_non_uniform_grid_rejected():
    t_ms, r, v, eta = _series(_ring(3.0))
    t_ms[100] += 0.3
    with pytest.raises(ValueError):
        sn_ramp.analyse_trajectory(t_ms, r, v, eta, FOLD, BAND)
