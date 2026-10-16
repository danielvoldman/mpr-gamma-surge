"""A4: Hopf locus of M3 from the characteristic polynomial (plan 5.2 A4, 7.1 K7 to K9, K11).

Analysis only, no integration. The polynomial lambda^3 + a1 lambda^2 + a2 lambda + a3 is taken
numerically from the Jacobian (models.mpr3d.jacobian_3d, tau-units, beta = tau/tau_d); no closed
form of Ceni Eqs. 11-12 is used (the plan says that text may be garbled). Hopf where
h = a1 a2 - a3 = 0 with a1 > 0 and a3 > 0 [reasoned, not tested]; then a2 = omega^2 and
Im lambda = sqrt(a2) is the first frequency estimate, in 1/tau.

Fixed point: for J < 0 the quartic of fixed_points.py has exactly one positive root (Descartes:
one sign change), so the branch is unique. For J >= 0 several roots can exist; crossings are then
tracked branch by branch (same sorted index and same root count at both ends of a bracket).
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq, minimize

from ..models.fixed_points import fixed_points
from ..models.mpr3d import jacobian_3d

EDGE_FRAC = 0.01   # working definition of 'on the edge' (UNVERIFIED; the plan gives none)


def char_poly(y, J, tau_d_tau):
    """(a1, a2, a3) of lambda^3 + a1 lambda^2 + a2 lambda + a3 for the M3 Jacobian at y."""
    c = np.poly(jacobian_3d(y, J, tau_d_tau))
    return float(c[1]), float(c[2]), float(c[3])


def hopf_function(y, J, tau_d_tau):
    """h = a1 a2 - a3 at fixed point y."""
    a1, a2, a3 = char_poly(y, J, tau_d_tau)
    return a1 * a2 - a3


def hopf_point(y, J, tau_d_tau):
    """Record at a fixed point: r*, v*, a1..a3, omega = Im lambda (1/tau), valid = (a1, a2, a3 > 0)."""
    a1, a2, a3 = char_poly(y, J, tau_d_tau)
    return {"r": float(y[0]), "v": float(y[1]), "a1": a1, "a2": a2, "a3": a3,
            "omega": float(np.sqrt(a2)) if a2 > 0 else float("nan"),
            "valid": bool(a1 > 0 and a3 > 0 and a2 > 0)}


def _h_branch(k, eta_bar, J, Delta, tau_d_tau):
    fp = fixed_points(eta_bar, J, Delta, model="M3")
    return hopf_function(fp[k], J, tau_d_tau) if k < len(fp) else np.nan


def hopf_crossings(vary, grid, eta_bar, J, Delta, tau_d_tau):
    """Hopf points along one parameter: sign changes of h on `grid`, refined with brentq.

    vary: 'eta_bar' | 'tau_d_tau' | 'Delta' | 'J' (the matching fixed argument is ignored).
    Returns dicts holding the four parameters, the branch index and the hopf_point fields; only
    crossings with a1 > 0 and a3 > 0 at the root are kept (the A4 Hopf condition).
    """
    base = {"eta_bar": eta_bar, "J": J, "Delta": Delta, "tau_d_tau": tau_d_tau}

    def at(x):
        return {**base, vary: x}

    def hk(k, x):
        p = at(x)
        return _h_branch(k, p["eta_bar"], p["J"], p["Delta"], p["tau_d_tau"])

    grid = np.asarray(grid, float)
    counts = [len(fixed_points(**{"eta_bar": at(x)["eta_bar"], "J": at(x)["J"], "Delta": at(x)["Delta"]},
                               model="M3")) for x in grid]
    out = []
    for k in range(max(counts)):
        hv = [hk(k, x) if counts[i] > k else np.nan for i, x in enumerate(grid)]
        for i in range(len(grid) - 1):
            if counts[i] != counts[i + 1] or counts[i] <= k:
                continue                                  # root count changed (fold) or branch absent
            if hv[i] * hv[i + 1] > 0 or not (np.isfinite(hv[i]) and np.isfinite(hv[i + 1])):
                continue
            x = brentq(lambda t: hk(k, t), grid[i], grid[i + 1], xtol=1e-13, rtol=1e-13)
            p = at(x)
            y = fixed_points(p["eta_bar"], p["J"], p["Delta"], model="M3")[k]
            rec = hopf_point(y, p["J"], p["tau_d_tau"])
            if rec["a1"] > 0 and rec["a3"] > 0:
                out.append({**p, "branch": k, **rec})
    return sorted(out, key=lambda d: d[vary])


def lowest_eta_hopf(eta_grid, J, Delta, tau_d_tau):
    """eta_bar_H: the lowest Hopf crossing along eta_bar (D12, CP20), or None."""
    c = hopf_crossings("eta_bar", eta_grid, 0.0, J, Delta, tau_d_tau)
    return c[0] if c else None


def hopf_curve(plane, outer_grid, eta_grid, fixed):
    """Hopf locus in (eta_bar, X), X = tau_d | Delta | J: lowest eta_bar crossing for each X.

    `fixed` gives the other two of J, Delta, tau_d_tau. Returns rows (X, eta_bar_H, omega); NaN if none.
    """
    key = {"tau_d": "tau_d_tau", "Delta": "Delta", "J": "J"}[plane]
    rows = []
    for x in outer_grid:
        p = {**fixed, key: x}
        c = lowest_eta_hopf(eta_grid, p["J"], p["Delta"], p["tau_d_tau"])
        rows.append((x, c["eta_bar"] if c else np.nan, c["omega"] if c else np.nan))
    return np.array(rows)


def k11_ratio(eta_bar, J, Delta, tau_d_tau):
    """Im lambda / (2 pi r*) at (eta_bar, J, Delta, tau_d_tau), for K11 at a Hopf point."""
    y = fixed_points(eta_bar, J, Delta, model="M3")[0]
    return hopf_point(y, J, tau_d_tau)["omega"] / (2.0 * np.pi * y[0])


def max_ratio_over_J_tau(eta_bar, tau_d_tau_range, J_range, n_tau=16, n_J=16, n_ratio=120,
                         ratio_max=0.5, max_widen=2):
    """K9: the largest Delta/eta_bar on the Hopf curve, maximised over tau_d and J.

    For each (tau_d, J) the Hopf Delta is the largest root of h along Delta/eta_bar in
    (0, ratio_max]. A log-tau_d by J grid is searched, then refined with Nelder-Mead inside the
    ranges. If the maximiser lies on an edge, that range is widened (tau_d bounds by a factor 2 on
    each side, J lower bound by a factor 2) at most `max_widen` times; if it is still on an edge the
    result is flagged `asymptotic` (Table 7.1). J_range is (lo, hi) with lo < hi < 0.
    Returns: ratio, tau_d_tau, J, on_edge, asymptotic, the final ranges, and the widening `log`.
    """
    ratios = np.linspace(ratio_max / n_ratio, ratio_max, n_ratio)

    def best_ratio(tau_d_tau, J):
        c = hopf_crossings("Delta", ratios * eta_bar, eta_bar, J, 0.0, tau_d_tau)
        return max((d["Delta"] for d in c), default=0.0) / eta_bar

    lo_t, hi_t = tau_d_tau_range
    lo_J, hi_J = J_range
    log = []
    for attempt in range(max_widen + 1):
        taus = np.geomspace(lo_t, hi_t, n_tau)
        Js = np.linspace(lo_J, hi_J, n_J)
        z = np.array([[best_ratio(t, J) for J in Js] for t in taus])
        i, j = np.unravel_index(np.argmax(z), z.shape)
        t_best, J_best, z_best = float(taus[i]), float(Js[j]), float(z[i, j])
        if z_best > 0:
            def neg(x):
                if not (np.log(lo_t) <= x[0] <= np.log(hi_t) and lo_J <= x[1] <= hi_J):
                    return 1.0
                return -best_ratio(np.exp(x[0]), x[1])
            res = minimize(neg, [np.log(t_best), J_best], method="Nelder-Mead",
                           options={"xatol": 1e-6, "fatol": 1e-10})
            if -res.fun > z_best:
                t_best, J_best, z_best = float(np.exp(res.x[0])), float(res.x[1]), -float(res.fun)
        # on an edge if the refined maximiser is within EDGE_FRAC of a range bound (log scale for tau_d)
        ft = np.log(t_best / lo_t) / np.log(hi_t / lo_t)
        fJ = (J_best - lo_J) / (hi_J - lo_J)
        edge_t = ft < EDGE_FRAC or ft > 1 - EDGE_FRAC
        edge_J = fJ < EDGE_FRAC or fJ > 1 - EDGE_FRAC
        on_edge = bool(edge_t or edge_J)
        if not on_edge or attempt == max_widen:
            return {"ratio": z_best, "tau_d_tau": t_best, "J": J_best, "on_edge": on_edge,
                    "asymptotic": on_edge, "tau_d_tau_range": (lo_t, hi_t), "J_range": (lo_J, hi_J),
                    "log": log}
        if edge_t:
            lo_t, hi_t = lo_t / 2.0, hi_t * 2.0
        if edge_J:
            lo_J = lo_J * 2.0
        log.append({"attempt": attempt + 1, "tau_d_tau_range": (lo_t, hi_t), "J_range": (lo_J, hi_J)})
