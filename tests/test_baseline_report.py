import numpy as np

from mprsurge import config as C
from mprsurge.analysis import baseline_report as B


def _white(n=5001, seed=1):
    return np.random.default_rng(seed).standard_normal(n)


def test_rho_white_noise_is_flat_spectrum_value():
    r = B.rho_row(_white(), 1000.0, 120.0)
    assert r["W_s"] == 2.0 and r["n_windows"] == 4
    assert abs(r["rho"] - 75.0 / 149.0) < 0.05          # flat 1 to 150 Hz spectrum: 0.50 (Table 2.1)
    assert abs(r["P_G"] / (r["P_G"] + r["P_nonG"]) - r["rho"]) < 0.05


def test_rho_short_window_for_fast_ramp():
    r = B.rho_row(_white(), 1000.0, 1.0)
    assert r["W_s"] == 0.2 and r["n_windows"] > 40


def test_rho_resonance_exceeds_half():
    t = np.arange(5001) / 1000.0
    v = np.sin(2 * np.pi * 40 * t) + 0.1 * _white()
    assert B.rho_row(v, 1000.0, 120.0)["rho"] > 0.9


def test_noise_envelope_threshold_and_cycles():
    t = np.arange(5001) / 1000.0
    v = np.where((t > 2) & (t < 3), 1.0, 0.0) * np.sin(2 * np.pi * 40 * t) + 0.01 * _white()
    r = B.noise_env_row(v, 1000.0, 0.5)
    assert r["all"]["any_above"] and 35 < r["all"]["longest_run_cycles"] < 41
    assert r["trim"]["env_max"] <= r["all"]["env_max"] + 1e-12
    low = B.noise_env_row(0.01 * _white(), 1000.0, 0.5)
    assert not low["all"]["any_above"] and low["all"]["longest_run_cycles"] == 0.0


def test_run_kind_registered():
    assert "a8base" in C.RUN_KINDS
