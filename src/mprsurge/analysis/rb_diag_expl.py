"""8f3 exploratory diagnostics (DL-191). Pure helpers; labelled exploratory, no gate reads them."""
from __future__ import annotations

import math

import numpy as np

LABEL = "exploratory"
SET_A_DELTA0 = (1e-9, 1e-3)
REF_DELTA0 = 1e-6


def perturb_v(y, sign):
    """Copy of the start state with v (index 1) moved by one ulp, up for sign > 0, down for sign < 0."""
    y = np.array(y, dtype=float)
    y[1] = np.nextafter(y[1], np.inf if sign > 0 else -np.inf)
    return y


def predicted_shift_s(delta0, delta0_ref, mean_re_lambda_per_tau, tau_ms):
    """Onset shift (s, positive = later) if the onset were set by delta0 exp(I(t)) = threshold with Re lambda the growth rate:
    -ln(delta0 / delta0_ref) / mean Re lambda, converted from tau to s."""
    return -math.log(delta0 / delta0_ref) / mean_re_lambda_per_tau * tau_ms / 1000.0


def shift_ratio(observed_s, predicted_s):
    return observed_s / predicted_s if predicted_s else None


def pattern(ratios, lo=0.5, hi=1.5, none=0.25):
    """Words for a set of observed/predicted ratios: all within [lo, hi] -> follows the kick; all |ratio| below none -> does not follow the kick (sign may be opposite); else mixed.
    lo, hi and none are OUR reading thresholds for a description, not criteria (exploratory)."""
    r = [x for x in ratios if x is not None]
    if not r:
        return "no ratio"
    if all(lo <= x <= hi for x in r):
        return "onset moves with the kick as predicted"
    if all(abs(x) < none for x in r):
        return "onset does not follow the kick (|ratio| below 0.25; sign may be opposite)"
    return "in between"


def plateau_floor(env, t_s, t0=10.0, t1=48.0):
    """Pre-onset envelope floor over [t0, t1] s (10 to 48 s, inside the DL-189 plateau, clear of the kick tail at 6 s and the growth from 50 s): median, 99th percentile, and exact zeros."""
    m = (t_s >= t0) & (t_s <= t1)
    e = env[m]
    hi = np.flatnonzero(e > 1e-12)        # a burst above the roundoff plateau, if any (the p99 is contaminated by it)
    return {"median": float(np.median(e)), "p90": float(np.percentile(e, 90)), "p99": float(np.percentile(e, 99)), "n_zero": int((e == 0.0).sum()),
            "n": int(e.size), "n_above_1e-12": int(hi.size), "burst_t_s": None if hi.size == 0 else [float(t_s[m][hi[0]]), float(t_s[m][hi[-1]])],
            "burst_max": None if hi.size == 0 else float(e.max())}
