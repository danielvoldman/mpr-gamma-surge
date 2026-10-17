"""Baseline-only report on the S5 baseline records (MS7 7f, DL-144). Analysis only: reads arrays, integrates nothing.

Two per-record measurements, both on the 7e records (v, 1 kHz, 5001 samples, the 2 s discard already removed):
  rho_row        baseline rho = P_G / P_total as surge_metrics.baseline_rho defines it (mean over the windows wholly inside
                 the record; window W and step from the cell's own T_ramp by D4), with the mean P_G and P_non-G over the
                 same windows. The record is read as the 5 s baseline, t_on = record end. Reported, not a test (F-7).
  noise_env_row  the mode-N noise envelope against the single amplitude threshold 0.1 x A_ref (open definition O4, DL-140):
                 band-passed Hilbert envelope (surge_metrics.envelope, 25 to 100 Hz) of the record, whole record and with
                 the first and last TRIM_S dropped after filtering (the A_ref convention). The D8 call is not used.
The grouping of results is a reporting split only: no class, flag or criterion is added.
"""
from __future__ import annotations

import numpy as np

from . import surge_metrics as M

TRIM_S = 1.0            # the A_ref trim (DL-138), used only for the "trimmed" noise-envelope variant; ours, UNVERIFIED
RHO_LEVEL = 0.5         # Table 2.1: "a rho ratio cannot reach 2 when baseline rho >= 0.5" (F-7)


def rho_row(v, fs, T_ramp_s, t_end=None):
    """Mean baseline rho, P_G and P_non-G over the windows of the cell's own D4 window, for one record."""
    v = np.asarray(v, float)
    t_end = (v.size - 1) / fs if t_end is None else t_end
    W, step = M.window_for_ramp(T_ramp_s)
    tc, p_g, p_tot, p_ng, _ = M._window_series(v, fs, W, step)
    m = M.baseline_windows(tc, W, t_end)
    if not m.any():
        raise ValueError("record too short for one window")
    return {"W_s": float(W), "n_windows": int(m.sum()), "rho": float(np.mean(p_g[m] / p_tot[m])),
            "P_G": float(np.mean(p_g[m])), "P_nonG": float(np.mean(p_ng[m])), "v_std": float(np.std(v, ddof=1))}


def _cycles_in(z_abs, phase, threshold, a, b):
    """Cycles (phase change / 2 pi) of the longest run of samples a..b-1 at or above threshold; 0 if none."""
    runs = M._runs_at_or_above(z_abs[a:b], threshold)
    if not runs:
        return 0.0
    return float(max((phase[a + e - 1] - phase[a + s]) / (2 * np.pi) for s, e in runs))


def noise_env_row(v, fs, threshold, band=M.G_BAND, trim_s=TRIM_S):
    """Envelope statistics against `threshold`, whole record and trimmed. Cycles are those of the longest run at or above."""
    z = M._analytic(v, fs, band)
    za = np.abs(z)
    ph = np.unwrap(np.angle(z))
    n = za.size
    k = int(round(trim_s * fs))
    out = {}
    for tag, (a, b) in (("all", (0, n)), ("trim", (k, n - k))):
        e = za[a:b]
        out[tag] = {"env_max": float(e.max()), "env_q99": float(np.quantile(e, 0.99)),
                    "env_median": float(np.median(e)), "frac_above": float(np.mean(e >= threshold)),
                    "any_above": bool(np.any(e >= threshold)),
                    "longest_run_cycles": _cycles_in(za, ph, threshold, a, b)}
    return out
