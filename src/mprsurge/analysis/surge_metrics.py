"""Surge metrics, core (plan Table 2.1, 5.2 A8; DL-062). Analysis only: no integration, no plotting.

Class-free subset built at MS1: spectrogram_v, band_power, envelope, envelope_growth, count_cycles.
Classes, relative power, A_ref and the sensitivity runs come at MS7. Times are in seconds, frequencies
in Hz, signals sampled at fs (1 kHz in the plan). The threshold is an argument; the plan's value
(0.1 x A_ref) needs A_ref, which exists only from MS6/MS7.

Edge note: the zero-phase filter and the Hilbert transform distort the first and last few filter
lengths of a record; callers discard or pad them (modes N and D already discard 2 s before t = 0).
"""
from __future__ import annotations

import numpy as np
from scipy import signal

FILTER_ORDER = 4          # DL-062 (zero-phase Butterworth band-pass, order 4)


def spectrogram_v(v, fs, window_s, step_s, t0=0.0):
    """Hann spectrogram of v: one-sided periodogram per window, linear detrend per window (Table 2.1).

    Returns (t, f, S): t the window centres (s, offset by t0), f in Hz, S the power spectral
    density, shape (len(f), len(t)). The step is rounded to whole samples.
    """
    v = np.asarray(v, float)
    nper = int(round(window_s * fs))
    step = max(1, int(round(step_s * fs)))
    if nper < 2 or nper > v.size or step > nper:
        raise ValueError("window must be at least 2 samples, fit in the record, and be at least the step")
    f, t, S = signal.spectrogram(v, fs=fs, window="hann", nperseg=nper, noverlap=nper - step,
                                 detrend="linear", scaling="density", mode="psd")
    return t + t0, f, S


def band_power(S, f, band):
    """Power in a band: the PSD bins with lo <= f < hi, summed and multiplied by the bin width (DL-062).

    S has frequency on axis 0 (as returned by spectrogram_v); returns one value per window.
    Whether the upper edge is inclusive is not sourced (UNVERIFIED); bins at an exact edge are rare.
    """
    f = np.asarray(f, float)
    lo, hi = band
    sel = (f >= lo) & (f < hi)
    return np.asarray(S)[sel].sum(axis=0) * (f[1] - f[0])


def _analytic(v, fs, band):
    sos = signal.butter(FILTER_ORDER, band, btype="bandpass", fs=fs, output="sos")
    return signal.hilbert(signal.sosfiltfilt(sos, np.asarray(v, float)))


def envelope(v, fs, band):
    """Hilbert envelope of v after a zero-phase Butterworth band-pass of the given band (DL-062)."""
    return np.abs(_analytic(v, fs, band))


def _runs_at_or_above(env, threshold):
    """(start, stop) index pairs, stop exclusive, of the runs where env >= threshold."""
    above = np.concatenate(([False], np.asarray(env) >= threshold, [False]))
    d = np.diff(above.astype(np.int8))
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


def count_cycles(v, fs, band, threshold):
    """Cycles in the longest run where the envelope is at or above threshold (DL-062).

    Cycles = change of the unwrapped analytic phase over the run / 2 pi. Returns 0.0 if the
    envelope never reaches the threshold. Merging runs separated by short gaps is a classifier
    rule and is not done here.
    """
    z = _analytic(v, fs, band)
    runs = _runs_at_or_above(np.abs(z), threshold)
    if not runs:
        return 0.0
    phase = np.unwrap(np.angle(z))
    return max((phase[b - 1] - phase[a]) / (2 * np.pi) for a, b in runs)


def envelope_growth(v, fs, band, threshold, n_cycles=10):
    """Growth rate of the envelope: OLS slope of ln(envelope) over the first n_cycles from the
    first threshold crossing (Table 2.1, D8; estimator DL-062).

    The fit window starts at the first sample with envelope >= threshold and ends after n_cycles
    of unwrapped phase, or where the envelope falls below the threshold or the record ends,
    whichever comes first. threshold = 0 starts at the first sample (as for K7, ms1_plan).
    Returns a dict: rate (1/s), se (plain OLS standard error of the slope, 1/s), n (samples fitted),
    cycles (cycles spanned by the window), t_start (s). rate and se are nan when fewer than 3
    samples are fitted or no sample reaches the threshold.

    CAVEAT (DL-062): the envelope is smooth and autocorrelated, so the plain OLS standard error is
    too small and "negative by more than 2 SE" declares damping too easily. Revisit at MS7.
    """
    z = _analytic(v, fs, band)
    env = np.abs(z)
    out = {"rate": np.nan, "se": np.nan, "n": 0, "cycles": 0.0, "t_start": np.nan}
    runs = _runs_at_or_above(env, threshold)
    if not runs:
        return out
    a, b = runs[0]
    phase = np.unwrap(np.angle(z))
    done = np.flatnonzero(phase[a:b] - phase[a] >= 2 * np.pi * n_cycles)
    stop = a + done[0] + 1 if done.size else b
    seg = np.log(env[a:stop])
    t = np.arange(a, stop) / fs
    out.update(n=stop - a, cycles=(phase[stop - 1] - phase[a]) / (2 * np.pi), t_start=a / fs)
    if stop - a < 3:
        return out
    tc = t - t.mean()
    sxx = np.sum(tc**2)
    rate = np.sum(tc * (seg - seg.mean())) / sxx
    resid = seg - seg.mean() - rate * tc
    out["rate"] = rate
    out["se"] = np.sqrt(np.sum(resid**2) / (seg.size - 2) / sxx)
    return out
