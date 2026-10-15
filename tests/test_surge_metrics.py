"""Surge metrics, class-free core on synthetic signals (plan 5.2 A8, Table 10.1; DL-062).

Signals are seeded. Test-level tolerances are UNVERIFIED (the plan gives none) and are stated
where used. Classes, A_ref and the zero-baseline cases come at MS7.
"""
import numpy as np
import pytest
from scipy import signal

from mprsurge.analysis import surge_metrics as M

FS = 1000.0
BAND = (25.0, 100.0)
THR = 0.1


def rng():
    return np.random.default_rng(20261014)


def ring(f, lam, lead_s=0.0, total_s=4.0, noise=1e-4):
    """exp(-lam t) sin(2 pi f t) from lead_s, amplitude 1, zero before; seeded noise floor.

    A step onset (lead_s > 0) is smeared by the zero-phase filter over about 20 ms; the D8 fit
    window then starts inside that transient (DL-073).
    """
    t = np.arange(int(total_s * FS)) / FS
    tau = np.clip(t - lead_s, 0, None)
    v = np.where(t >= lead_s, np.exp(-lam * tau) * np.sin(2 * np.pi * f * tau), 0.0)
    return v + noise * rng().standard_normal(t.size)


def test_burst_on_off_within_one_step():
    t = np.arange(10 * FS) / FS
    v = np.where((t >= 4.0) & (t < 6.0), np.sin(2 * np.pi * 40 * t), 0.0) + 1e-3 * rng().standard_normal(t.size)
    step = 0.1
    tc, f, S = M.spectrogram_v(v, FS, 0.2, step)
    p = M.band_power(S, f, BAND)
    half = 0.5 * p.max()
    up = tc[np.flatnonzero(p >= half)[0]]
    down = tc[np.flatnonzero(p >= half)[-1]]
    # A Hann window centred on an edge has half its weight inside the burst, so the half-power
    # crossing sits on the edge to within one step.
    assert abs(up - 4.0) <= step and abs(down - 6.0) <= step


def test_chirp_peak_follows_instantaneous_frequency():
    t = np.arange(10 * FS) / FS
    v = signal.chirp(t, f0=20.0, t1=10.0, f1=80.0, method="linear") + 1e-3 * rng().standard_normal(t.size)
    tc, f, S = M.spectrogram_v(v, FS, 1.0, 0.5)
    f_pk = f[np.argmax(S, axis=0)]
    f_inst = 20.0 + 6.0 * tc
    ok = (tc > 1.0) & (tc < 9.0)
    assert np.max(np.abs(f_pk[ok] - f_inst[ok])) <= 3.0       # UNVERIFIED test-level: 1 Hz bins, 6 Hz smear


def test_five_cycle_ring_has_negative_growth_and_fewer_than_ten_cycles():
    lam = np.log(1.0 / THR) / (5 / 40.0)                       # envelope reaches THR after 5 cycles
    v = ring(40.0, lam)
    n = M.count_cycles(v, FS, BAND, THR)
    assert 4.0 < n < 6.0                                       # UNVERIFIED test-level
    g = M.envelope_growth(v, FS, BAND, THR)
    assert g["rate"] < 0 and g["cycles"] < 10


def test_slowly_damped_ring_has_more_than_ten_cycles_and_negative_growth():
    lam = np.log(1.0 / THR) / (15 / 40.0)                      # 15 cycles above THR
    v = ring(40.0, lam, lead_s=1.0)                            # D8 window: threshold crossing, first 10 cycles
    assert M.count_cycles(v, FS, BAND, THR) > 10
    g = M.envelope_growth(v, FS, BAND, THR)
    assert g["cycles"] == pytest.approx(10.0, abs=0.1)         # the fit uses the first 10 cycles
    assert g["rate"] < -2 * g["se"]                            # damped by the D8 rule


@pytest.mark.xfail(strict=True, reason="DL-073: step-onset filter bias, rate -3.4 against -6.1 per s (UNVERIFIED)")
def test_slowly_damped_ring_rate_matches_true_decay_after_step_onset():
    lam = np.log(1.0 / THR) / (15 / 40.0)
    g = M.envelope_growth(ring(40.0, lam, lead_s=1.0), FS, BAND, THR)
    assert g["rate"] == pytest.approx(-lam, rel=0.1)           # UNVERIFIED test-level


def test_pure_trend_has_no_cycles_and_no_gamma_power():
    t = np.arange(10 * FS) / FS
    v = 5.0 * t / 10.0 + 1e-3 * rng().standard_normal(t.size)
    assert M.envelope(v, FS, BAND).max() < THR
    assert M.count_cycles(v, FS, BAND, THR) == 0.0
    g = M.envelope_growth(v, FS, BAND, THR)
    assert g["n"] == 0 and np.isnan(g["rate"]) and np.isnan(g["se"])
    tc, f, S = M.spectrogram_v(v, FS, 1.0, 0.5)                # linear detrend removes the trend per window
    assert np.all(M.band_power(S, f, BAND) < 1e-3 * 25.0)      # far below a unit sine's band power (0.5)


def test_envelope_of_a_sine_is_its_amplitude():
    t = np.arange(4 * FS) / FS
    env = M.envelope(2.0 * np.sin(2 * np.pi * 40 * t), FS, BAND)
    assert np.allclose(env[500:-500], 2.0, rtol=1e-2)


def test_spectrogram_rejects_bad_window():
    with pytest.raises(ValueError):
        M.spectrogram_v(np.zeros(100), FS, 1.0, 0.5)
