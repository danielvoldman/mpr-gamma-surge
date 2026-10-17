"""A_ref and the absolute amplitude threshold (plan Table 2.1 D7; DL-136 D-1; DL-138 ruling, closed in DL-139). Analysis only.

Definition (owner ruling on DL-138, reading (a)): A_ref is the median of the band-passed Hilbert envelope of v
(band 25 to 100 Hz, zero-phase Butterworth order 4, the detector's own envelope: surge_metrics.envelope) over WHOLE
CYCLES of the stored S3 record at ref_devalle.

Whole cycles, defined here: the record is first trimmed by TRIM_S at each end, [t_first + TRIM_S, t_last - TRIM_S].
The period P is the stored A5 value at ref_devalle (period_tau x tau_ms). The window starts at the trimmed start and
spans n = floor(trimmed length / P) periods; it holds the samples with t_start <= t < t_start + n P (half-open).
The envelope is computed on the whole untrimmed record (so the edges see the filter's full context) and only then
cut to the window. The result is one number; 0.1 x A_ref is one absolute threshold for every cell and path (D7).

The alternates (mean, maximum, sqrt(2) x RMS, half peak-to-peak, the literal A5 peak-to-peak) are computed on the
same window and stored beside it, labelled "alternate, not used". They are kept for the A8 sensitivity item (7h
sign-off) and are never the threshold. All numeric choices here beyond the ruling (the half-open window, rounding of
the window end) are ours, UNVERIFIED.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from . import surge_metrics as M

BAND = (25.0, 100.0)       # the detector's primary band (configs/base.yaml analysis.band_primary_hz)
TRIM_S = 1.0               # first and last 1 s dropped (owner ruling on DL-138)
AMIN_FACTOR = 0.1          # Table 2.1 / D7: threshold = 0.1 x A_ref
STATISTIC = "median"
ALT_LABEL = "alternate, not used"
DEFINITION = ("median of the band-passed Hilbert envelope of v (25-100 Hz, zero-phase Butterworth order 4, "
              "surge_metrics.envelope) over whole cycles of the stored S3 record at ref_devalle; whole cycles = "
              "floor(trimmed length / period) periods from the trimmed start, half-open window; period = stored A5 "
              "value; first and last 1 s dropped (DL-138 ruling, reading (a))")


def whole_cycle_window(t_s, period_s: float, trim_s: float = TRIM_S, extra_cycles: int = 0):
    """(i0, i1, n_cycles): sample slice [i0, i1) holding n whole periods inside [t[0]+trim, t[-1]-trim].

    extra_cycles drops that many further whole periods at each end (used by the invariance test)."""
    t = np.asarray(t_s, float)
    if not (period_s > 0 and math.isfinite(period_s)):
        raise ValueError("period_s must be positive and finite")
    t0 = t[0] + trim_s + extra_cycles * period_s
    avail = (t[-1] - trim_s) - t0 - extra_cycles * period_s
    n = int(math.floor(avail / period_s + 1e-9))
    if n < 1:
        raise ValueError("record too short for one whole cycle after trimming")
    eps = 1e-9
    i0 = int(np.searchsorted(t, t0 - eps, side="left"))
    i1 = int(np.searchsorted(t, t0 + n * period_s - eps, side="left"))
    return i0, i1, n


def compute_a_ref(t_s, v, period_s: float, a5_ptp: float | None = None, band=BAND, trim_s: float = TRIM_S,
                  extra_cycles: int = 0) -> dict:
    """A_ref (median envelope) and the labelled alternates on one record. fs is taken from t_s."""
    t = np.asarray(t_s, float)
    v = np.asarray(v, float)
    fs = 1.0 / float(t[1] - t[0])
    i0, i1, n = whole_cycle_window(t, period_s, trim_s, extra_cycles)
    env = M.envelope(v, fs, band)[i0:i1]
    seg = v[i0:i1]
    alt = {"mean": float(env.mean()), "max": float(env.max()),
           "sqrt2_rms": float(math.sqrt(2.0) * np.sqrt(np.mean((seg - seg.mean()) ** 2))),
           "half_ptp": float(0.5 * np.ptp(seg))}
    if a5_ptp is not None:
        alt["literal_ptp_a5"] = float(a5_ptp)
    return {"value": float(np.median(env)), "statistic": STATISTIC, "n_cycles": n, "n_samples": i1 - i0,
            "window_s": [float(t[i0]), float(t[i1 - 1])], "period_s": float(period_s), "trim_s": float(trim_s),
            "band_hz": list(band), "filter": f"Butterworth order {M.FILTER_ORDER}, zero-phase (sosfiltfilt), Hilbert",
            "extra_cycles_dropped": int(extra_cycles),
            "alternates": {k: {"value": x, "label": ALT_LABEL} for k, x in alt.items()}}


def threshold_abs(a_ref: float, factor: float = AMIN_FACTOR) -> float:
    """The one absolute amplitude threshold, 0.1 x A_ref (D7). Takes no cell, path or run argument."""
    return float(factor * a_ref)


def load_a_ref(path) -> float:
    """A_ref from the stored file written by scripts/compute_a_ref.py (results/A8/a_ref/a_ref.json)."""
    with open(Path(path), "r", encoding="utf-8") as fh:
        rec = json.load(fh)
    if rec.get("statistic") != STATISTIC:
        raise ValueError("stored A_ref is not the median-envelope definition")
    return float(rec["value"])
