"""8f2 diagnoses (DL-186): synthetic envelopes and tables with known answers; no stored result is read."""
import math

import numpy as np
import pytest

from mprsurge.analysis import rb_diag as D


def test_ols_slope_and_growth_rate_per_tau():
    t = np.arange(0.0, 2.0, 0.001)
    env = 1e-6 * np.exp(0.5 * t)
    assert D.ols_slope(t, np.log(env)) == pytest.approx(0.5)
    assert D.growth_rate_per_tau(t, env, 0, t.size - 1, 10.0) == pytest.approx(0.5 * 0.01)      # 1/s -> 1/tau at tau = 10 ms
    assert math.isnan(D.ols_slope([0.0, 1.0], [0.0, 1.0]))


def test_decade_window_starts_after_last_sample_below_threshold_over_ten():
    env = np.array([1e-9, 1e-3, 1e-2, 0.5e-1, 2e-1, 3e-1])
    assert D.decade_window(env, 5, 0.2)[0] == int(np.flatnonzero(env[:5] < 0.02)[-1]) + 1
    assert D.decade_window(np.array([1.0, 1.0, 1.0]), 2, 0.2) is None


def test_level_crossings_first_sample_at_or_above():
    t = np.arange(10) * 0.5
    env = np.array([0, 1e-9, 1e-7, 1e-5, 1e-3, 1e-1, 1.0, 1.0, 1.0, 1.0])
    out = D.level_crossings(env, t, 0, [1e-6, 1e-2, 2.0])
    assert out["1e-06"] == 1.5 and out["0.01"] == 2.5 and out["2.0"] is None


def test_gain_at_interpolates_and_extends_with_final_rate():
    t, re = np.array([0.0, 1.0, 2.0]), np.array([1.0, 1.0, 2.0])
    I = np.array([0.0, 1.0, 2.5])
    assert D.gain_at(t, re, I, 0.5) == pytest.approx(0.5) and D.gain_at(t, re, I, 4.0) == pytest.approx(2.5 + 2.0 * 2.0)


def test_rb6_resolution_row_bound_against_the_output_step():
    on = np.full(10, 58.0)
    r = D.rb6_resolution_row(0, 1e-9, 2.917e-5, -0.00076, -0.00076, on, on, 0.05)
    assert r["bound_in_output_steps"] == pytest.approx(0.05 * 0.00076 / 2.917e-5)
    assert r["bound_finer_than_one_step"] is False and r["smallest_nonzero_rel_change_one_step"] == pytest.approx(2.917e-5 / 0.00076)
    assert r["n_seeds_onset_identical"] == 10 and r["observed_rel_change"] == 0.0
    fine = D.rb6_resolution_row(0, 1e-9, 2.917e-5, -0.0005, -0.0005, on, on, 0.05)          # 5 percent of 5e-4 is below one 2.9e-5 step? no: 2.5e-5 < 2.9e-5
    assert fine["bound_finer_than_one_step"] is True and fine["bound_finer_than_half_step"] is False


def test_solver_pair_lags_log_amplitude_offset():
    a = {"growth_bands_above_plateau": [{"env_from": 1e-12, "env_to": 1e-6, "rate_per_tau": 0.05}], "level_crossing_times_s": {"1e-09": 10.0, "0.1": None}}
    b = {"level_crossing_times_s": {"1e-09": 10.2, "0.1": 11.0}}
    out = D.solver_pair_lags(a, b, 10.0)
    assert len(out) == 1 and out[0]["lag_ms"] == pytest.approx(200.0) and out[0]["implied_ln_amplitude_ratio"] == pytest.approx(0.05 * 20.0)
