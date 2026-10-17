"""F-11 (7g, DL-150): noise-free solver error floor from a constant-parameter hold run.

Analysis only. The record is a mode D run (DOP853) started at the exact stable fixed point with every parameter
constant and delta_0 = 0, so any departure from the start state is solver or round-off error. The equivalent
amplitude is in v units, the unit of delta_0 (delta_0 is added on v, 6.2): the largest |v(t) - v(0)| over the run.
"""
from __future__ import annotations

import numpy as np


def floor_summary(v, r, s, discard_samples: int = 0) -> dict:
    """Departures of v, r, s from their first sample. The candidate floor is max |v - v[0]| over the whole record.

    Also reported (not candidates): the same maximum over the second half, the final value, the RMS, and the
    largest departure of r and s. All are absolute, in model units.
    """
    v, r, s = (np.asarray(x, dtype=float) for x in (v, r, s))
    if not (v.shape == r.shape == s.shape) or v.ndim != 1 or v.size < 4:
        raise ValueError("v, r, s must be 1-d arrays of equal length >= 4")
    if not np.all(np.isfinite(v)) or not np.all(np.isfinite(r)) or not np.all(np.isfinite(s)):
        raise ValueError("non-finite samples")
    dv = np.abs(v[discard_samples:] - v[0])
    half = dv[dv.size // 2:]
    return {"n_samples": int(v.size), "v_start": float(v[0]),
            "dv_max": float(dv.max()), "dv_max_second_half": float(half.max()), "dv_final": float(dv[-1]),
            "dv_rms": float(np.sqrt(np.mean(dv ** 2))),
            "dr_max": float(np.abs(r - r[0]).max()), "ds_max": float(np.abs(s - s[0]).max()),
            "eps_times_abs_v": float(np.finfo(float).eps * abs(v[0])),
            "dv_max_over_eps_abs_v": float(dv.max() / (np.finfo(float).eps * abs(v[0])))}
