"""Unit conversions (plan 3.3, Table 10.1). The RB9a dimensional-vs-nondimensional
run comparison needs an integrator and is added with simulate_mf (sub-step 1b-ii)."""
import math

import pytest

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
