"""A5 against S4 amplitude check and the K7 amplitude half (plan 5.2 A5, Table 7.1 K7, CP23; MS6 step 6e, DL-129).

Pure: no integration, no Julia. Rules are the pre-registered ones of DL-126 D-3 (UNVERIFIED defaults, not tuned):
the relative amplitude difference is of amplitude (not of A^2); points within one S4 step of eta_H are excluded;
K7 fits A^2 against tau_d - tau_d^(H) on points 0.1 to 1.0 ms above the Hopf point, passes if R^2 >= 0.99 and the
largest fit residual is under 2 percent of the largest A^2 in the window. The hysteresis tolerance is not in
DL-126; the 2 percent amplitude rule is used for it (DL-129, UNVERIFIED reading).
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

REL_TOL = 0.02            # CP23 / DL-126 D-3: relative difference of amplitude
FIT_WINDOW_MS = (0.1, 1.0)
R2_MIN = 0.99
RESID_TOL = 0.02          # of the largest A^2 in the window
_EPS = 1e-9


def interp_branch(param, amp, x):
    """PCHIP of a branch amplitude at x; NaN outside the branch range (as analysis.a5.at_param)."""
    order = np.argsort(param, kind="stable")
    p, a = np.asarray(param, float)[order], np.asarray(amp, float)[order]
    if len(np.unique(p)) != p.size:
        raise ValueError("branch parameter values are not unique")
    x = np.asarray(x, float)
    out = np.full(x.shape, np.nan)
    ok = (x >= p[0]) & (x <= p[-1])
    out[ok] = PchipInterpolator(p, a)(x[ok])
    return out


def rel_diff(s4_amp, a5_amp):
    """(S4 - A5) / A5, NaN where A5 is NaN or not positive."""
    s4_amp, a5_amp = np.asarray(s4_amp, float), np.asarray(a5_amp, float)
    ok = a5_amp > 0
    return np.where(ok, (s4_amp - a5_amp) / np.where(ok, a5_amp, 1.0), np.nan)


def near_mask(param, centre, step):
    """True for points within one S4 step of the Hopf point (CP23, DL-126 D-3)."""
    return np.abs(np.asarray(param, float) - centre) <= step + _EPS


def judge(param, s4_amp, a5_amp, excluded, tol=REL_TOL):
    """Max |relative difference| over the judged points (not excluded, A5 defined), which ones, verdict."""
    rd = rel_diff(s4_amp, a5_amp)
    judged = ~np.asarray(excluded, bool) & np.isfinite(rd)
    mx = float(np.max(np.abs(rd[judged]))) if judged.any() else float("nan")
    return {"rel_diff": rd, "judged": judged, "max_abs_rel_diff": mx,
            "pass": bool(judged.any() and mx < tol)}


def amplitude_fit(tau_d_ms, amp, hopf_ms, window=FIT_WINDOW_MS, r2_min=R2_MIN, resid_tol=RESID_TOL):
    """Least-squares line A^2 = slope * (tau_d - hopf) + intercept on the window points, with the DL-126 rules."""
    x = np.asarray(tau_d_ms, float) - hopf_ms
    m = (x >= window[0] - _EPS) & (x <= window[1] + _EPS)
    xs, y = x[m], np.asarray(amp, float)[m] ** 2
    if xs.size < 3:
        return {"n_points": int(xs.size), "pass": False}
    slope, icpt = np.polyfit(xs, y, 1)
    res = y - (slope * xs + icpt)
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - float(np.sum(res ** 2)) / ss_tot if ss_tot > 0 else float("nan")
    resid = float(np.max(np.abs(res)) / np.max(y))
    return {"n_points": int(xs.size), "slope": float(slope), "intercept": float(icpt), "r2": r2,
            "max_resid_frac": resid, "r2_pass": bool(r2 >= r2_min), "resid_pass": bool(resid < resid_tol),
            "pass": bool(r2 >= r2_min and resid < resid_tol), "x_ms": xs, "a2": y}


def hysteresis(amp_up, amp_down, tol=REL_TOL, min_amp=1e-3):
    """Largest relative up/down amplitude difference over points where either branch has amplitude above min_amp
    (1e-3, far above the 1e-6 kick; UNVERIFIED); flag if above tol."""
    u, d = np.asarray(amp_up, float), np.asarray(amp_down, float)
    ok = np.maximum(u, d) > min_amp
    rd = np.abs(d - u)[ok] / np.maximum(u, d)[ok]
    mx = float(rd.max()) if rd.size else float("nan")
    return {"max_rel_diff": mx, "flag": bool(mx > tol)}
