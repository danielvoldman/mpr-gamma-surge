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


# --- A4 run (MS5 5c, DL-114): grids from configs/A4_grids.yaml, K7 to K11 values ----------------------------

A4_PARAMS_FILE = "configs/A4_grids.yaml"


def load_a4_params() -> dict:
    """The A4 grids and K-check protocol (configs/A4_grids.yaml); config.hash_view hashes this dict."""
    import yaml
    from .. import config as C
    with open(C.repo_root() / A4_PARAMS_FILE, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _grid(spec: dict) -> np.ndarray:
    f = np.geomspace if spec.get("spacing") == "log" else np.linspace
    return f(spec["lo"], spec["hi"], int(spec["n"]))


def leading_mode(eta_bar, J, Delta, tau_d_tau):
    """Fixed point (J < 0: unique) and its spectrum: max Re over all eigenvalues, and the complex pair's (Re, |Im|)."""
    y = fixed_points(eta_bar, J, Delta, model="M3")[0]
    ev = np.linalg.eigvals(jacobian_3d(y, J, tau_d_tau))
    cx = [e for e in ev if abs(e.imag) > 1e-12]
    pair = max(cx, key=lambda z: z.real) if cx else None
    return {"r": float(y[0]), "re_max": float(ev.real.max()),
            "pair_re": float(pair.real) if pair is not None else float("nan"),
            "pair_im": float(abs(pair.imag)) if pair is not None else float("nan")}


def _hz(omega_tau, tau_ms):
    return omega_tau / (2.0 * np.pi * tau_ms * 1e-3)


def compute_a4(P: dict, tau_ms: float, tau_d_ms: float, deadline=None):
    """All A4 quantities. P = load_a4_params(). Returns (arrays, summary). Analysis only, nothing integrated."""
    g, pts = P["grids"], P["points"]
    eg = _grid(g["eta_bar"])
    dv, ce = pts["ref_devalle"], pts["ref_ceni"]
    td = lambda ms: ms / tau_ms
    arrays, S = {}, {}

    # eta_H at ref_devalle (D12: the lowest Hopf crossing along eta_bar)
    c = lowest_eta_hopf(eg, dv["J"], dv["Delta"], td(tau_d_ms))
    S["eta_H"] = None if c is None else c["eta_bar"]
    S["eta_H_omega_tau"] = None if c is None else c["omega"]

    # Hopf curves in the three planes at ref_devalle (the other two parameters at their ref_devalle values)
    tds = _grid(g["tau_d_ms"])
    cur = hopf_curve("tau_d", tds / tau_ms, eg, {"J": dv["J"], "Delta": dv["Delta"], "tau_d_tau": 0.0})
    arrays.update(curve_tau_d_ms=tds, curve_tau_d_eta_H=cur[:, 1], curve_tau_d_omega=cur[:, 2])
    dls = _grid(g["Delta"])
    cur = hopf_curve("Delta", dls, eg, {"J": dv["J"], "Delta": 0.0, "tau_d_tau": td(tau_d_ms)})
    arrays.update(curve_Delta=dls, curve_Delta_eta_H=cur[:, 1], curve_Delta_omega=cur[:, 2])
    Js = _grid(g["J"])
    cur = hopf_curve("J", Js, eg, {"J": 0.0, "Delta": dv["Delta"], "tau_d_tau": td(tau_d_ms)})
    arrays.update(curve_J=Js, curve_J_eta_H=cur[:, 1], curve_J_omega=cur[:, 2])

    # K7 and K10 at ref_ceni: Hopf crossings along tau_d, stability at 3 and 8 ms
    line = _grid(g["tau_d_line"])
    cr = hopf_crossings("tau_d_tau", line / tau_ms, ce["eta_bar"], ce["J"], ce["Delta"], 0.0)
    arrays.update(ceni_hopf_tau_d_ms=np.array([d["tau_d_tau"] * tau_ms for d in cr]),
                  ceni_hopf_omega=np.array([d["omega"] for d in cr]))
    S["ceni_hopf_tau_d_ms"] = [float(d["tau_d_tau"] * tau_ms) for d in cr]
    mode = lambda ms: leading_mode(ce["eta_bar"], ce["J"], ce["Delta"], td(ms))
    S["ceni_3ms"], S["ceni_8ms"], S["ceni_4p95ms"] = mode(3.0), mode(8.0), mode(4.95)

    # K10: frequency over the oscillatory interval [tau_d_H, upper end or the end of the line]
    if cr:
        lo = cr[0]["tau_d_tau"] * tau_ms
        hi = cr[1]["tau_d_tau"] * tau_ms if len(cr) > 1 else float(line[-1])
        grid = np.linspace(lo, hi, int(P["k10"]["n_tau"]))
        modes = [leading_mode(ce["eta_bar"], ce["J"], ce["Delta"], td(x)) for x in grid]
        f = np.array([_hz(m["pair_im"], tau_ms) for m in modes])
        arrays.update(k10_tau_d_ms=grid, k10_freq_hz=f, k10_re_max=np.array([m["re_max"] for m in modes]))
        jt = {}
        for x in P["k10"]["tau_d_ms"]:
            if lo <= x <= hi:
                fj = [_hz(leading_mode(ce["eta_bar"], J, ce["Delta"], td(x))["pair_im"], tau_ms)
                      for J in P["k10"]["J_values"]]
                jt[str(x)] = {"freq_hz": [float(v) for v in fj],
                              "rel_change": float((np.nanmax(fj) - np.nanmin(fj)) / np.nanmean(fj))}
        S["k10"] = {"interval_ms": [float(lo), float(hi)], "upper_end_is_hopf": len(cr) > 1,
                    "freq_hz_min": float(np.nanmin(f)), "freq_hz_max": float(np.nanmax(f)),
                    "monotone_decreasing": bool(np.all(np.diff(f) <= 1e-9)),
                    "J_values": list(P["k10"]["J_values"]), "J_dependence": jt}
    else:
        S["k10"] = None

    # K8 at ref_devalle: spectrum at 5 and 50 ms, plus the Hopf crossings along tau_d
    dmode = lambda ms: leading_mode(dv["eta_bar"], dv["J"], dv["Delta"], td(ms))
    S["devalle_5ms"], S["devalle_50ms"] = dmode(5.0), dmode(50.0)
    S["devalle_5ms"]["freq_hz"] = float(_hz(S["devalle_5ms"]["pair_im"], tau_ms))
    S["devalle_hopf_tau_d_ms"] = [float(d["tau_d_tau"] * tau_ms) for d in
                                  hopf_crossings("tau_d_tau", line / tau_ms, dv["eta_bar"], dv["J"], dv["Delta"], 0.0)]

    # K9: no Hopf for J > 0
    jp = P["jpos"]
    found = []
    Jpos = _grid(jp["J"])
    for J in Jpos:
        for ms in jp["tau_d_ms"]:
            for D in jp["Delta"]:
                for d in hopf_crossings("eta_bar", eg, 0.0, float(J), D, td(ms)):
                    found.append({"J": float(J), "tau_d_ms": ms, "Delta": D, "eta_bar": d["eta_bar"]})
    S["jpos"] = {"n_cases": int(len(Jpos) * len(jp["tau_d_ms"]) * len(jp["Delta"])), "n_hopf": len(found),
                 "found": found[:10]}

    # K9: the largest Delta/eta_bar on the Hopf curve at eta_bar = 1, 2, 4
    k9, rows = P["k9"], []
    lo_t, hi_t = k9["tau_d_ms_range"]
    for e in k9["eta_bar"]:
        r = max_ratio_over_J_tau(e, (lo_t / tau_ms, hi_t / tau_ms), tuple(k9["J_range"]), n_tau=k9["n_tau"],
                                 n_J=k9["n_J"], n_ratio=k9["n_ratio"], ratio_max=k9["ratio_max"],
                                 max_widen=k9["max_widen"])
        rows.append({"eta_bar": e, "ratio": r["ratio"], "tau_d_ms": r["tau_d_tau"] * tau_ms, "J": r["J"],
                     "on_edge": r["on_edge"], "asymptotic": r["asymptotic"],
                     "tau_d_ms_range": [r["tau_d_tau_range"][0] * tau_ms, r["tau_d_tau_range"][1] * tau_ms],
                     "J_range": list(r["J_range"]),
                     "widening": [{"attempt": w["attempt"],
                                   "tau_d_ms_range": [w["tau_d_tau_range"][0] * tau_ms, w["tau_d_tau_range"][1] * tau_ms],
                                   "J_range": list(w["J_range"])} for w in r["log"]]})
    S["k9"] = rows
    arrays.update(k9_eta_bar=np.array([r["eta_bar"] for r in rows]), k9_ratio=np.array([r["ratio"] for r in rows]),
                  k9_tau_d_ms=np.array([r["tau_d_ms"] for r in rows]), k9_J=np.array([r["J"] for r in rows]),
                  k9_on_edge=np.array([r["on_edge"] for r in rows]))

    # K11: Im lambda / (2 pi r*) on the J -> 0- Hopf branch at Delta = 1e-4 (the crossing nearest J = 0-)
    k = P["k11"]
    absJ = np.geomspace(k["absJ"]["lo"], k["absJ"]["hi"], int(k["absJ"]["n"]))
    Jgrid = -absJ[::-1]
    rows = []
    for e in k["eta_bar"]:
        for ms in k["tau_d_ms"]:
            c = hopf_crossings("J", Jgrid, e, 0.0, k["Delta"], td(ms))
            if c:
                Jh = c[-1]["J"]
                rows.append({"eta_bar": e, "tau_d_ms": ms, "J_H": Jh, "ratio": k11_ratio(e, Jh, k["Delta"], td(ms))})
            else:
                rows.append({"eta_bar": e, "tau_d_ms": ms, "J_H": None, "ratio": None})
    S["k11"] = rows
    arrays.update(k11_eta_bar=np.array([r["eta_bar"] for r in rows]), k11_tau_d_ms=np.array([r["tau_d_ms"] for r in rows]),
                  k11_J_H=np.array([np.nan if r["J_H"] is None else r["J_H"] for r in rows]),
                  k11_ratio=np.array([np.nan if r["ratio"] is None else r["ratio"] for r in rows]))
    return arrays, S


def evaluate_a4(S: dict, rep: dict) -> dict:
    """Verdicts against Table 7.1 (replication.yaml) and the DL-113 rulings."""
    v = {}
    k7 = rep["K7"]
    hs = S["ceni_hopf_tau_d_ms"]
    h = hs[0] if hs else None
    stable3 = S["ceni_3ms"]["re_max"] < 0 and not np.isnan(S["ceni_3ms"]["pair_im"])
    unstable8 = S["ceni_8ms"]["re_max"] > 0
    v["K7"] = {"tau_d_H_ms": h, "frozen_ms": k7["tau_d_H_ms"], "frozen_tol_ms": k7["tau_d_H_tol_ms"],
               "paper_ms": k7["tau_d_H_paper_ms"],
               "diff_to_frozen_ms": None if h is None else h - k7["tau_d_H_ms"],
               "diff_to_paper_ms": None if h is None else h - k7["tau_d_H_paper_ms"],
               "stable_focus_at_3ms": bool(stable3), "unstable_at_8ms": bool(unstable8),
               "pass": bool(h is not None and abs(h - k7["tau_d_H_ms"]) <= k7["tau_d_H_tol_ms"] and stable3 and unstable8),
               "pass_vs_paper": bool(h is not None and abs(h - k7["tau_d_H_paper_ms"]) <= k7["tau_d_H_tol_ms"]),
               "amplitude_half": "not judged (deferred to MS6, DL-113)",
               "time_series_half": "not judged (S3, step 5d)"}
    d5, d50 = S["devalle_5ms"], S["devalle_50ms"]
    band = rep["K8"]["band_hz"]
    osc = bool(d5["re_max"] > 0 and not np.isnan(d5["pair_im"]))
    v["K8"] = {"unstable_with_complex_pair_at_5ms": osc, "stable_at_50ms": bool(d50["re_max"] < 0),
               "pass": bool(osc and d50["re_max"] < 0 and S["jpos"]["n_hopf"] == 0),
               "no_hopf_J_positive": S["jpos"]["n_hopf"] == 0,
               "linear_freq_hz_5ms": d5["freq_hz"], "band_hz": band,
               "band_ok": bool(band[0] <= d5["freq_hz"] <= band[1]), "band_blocking": False,
               "limit_cycle_half": "not judged (S3, step 5d)"}
    ks = S["k9"]
    ratios = [r["ratio"] for r in ks]
    spread = max(ratios) - min(ratios)
    tol = rep["K9"]["delta_c_tol"]
    v["K9"] = {"maxima": {str(r["eta_bar"]): r["ratio"] for r in ks}, "spread": spread, "spread_tol": tol,
               "ratio_scaling_ok": bool(spread <= tol), "delta_c": rep["K9"]["delta_c"],
               "max_matches_delta_c": bool(all(abs(x - rep["K9"]["delta_c"]) <= tol for x in ratios)),
               "any_asymptotic": bool(any(r["asymptotic"] for r in ks)),
               "pass": bool(spread <= tol and not any(r["asymptotic"] for r in ks))}
    k11 = rep["K11"]
    rr = [r["ratio"] for r in S["k11"] if r["ratio"] is not None]
    v["K11"] = {"n_branches": len(rr), "n_missing": len(S["k11"]) - len(rr),
                "max_abs_dev": max(abs(x - 1.0) for x in rr) if rr else None, "tol": k11["ratio_tol"],
                "pass": bool(rr and max(abs(x - 1.0) for x in rr) <= k11["ratio_tol"]), "blocking": False}
    k10 = S["k10"]
    if k10 is None:
        v["K10"] = {"pass": False, "note": "no oscillatory interval found", "blocking": False}
    else:
        b, lim = rep["K10"]["band_hz"], rep["K10"]["band_slack_rel"]
        in_band = bool(b[0] * (1 - lim) <= k10["freq_hz_min"] and k10["freq_hz_max"] <= b[1] * (1 + lim))
        jch = {k: x["rel_change"] for k, x in k10["J_dependence"].items()}
        jok = bool(jch) and all(x < rep["K10"]["J_change_max_rel"] for x in jch.values())
        v["K10"] = {"interval_ms": k10["interval_ms"], "freq_hz": [k10["freq_hz_min"], k10["freq_hz_max"]],
                    "in_band_with_slack": in_band, "monotone_decreasing": k10["monotone_decreasing"],
                    "J_rel_change": jch, "J_independent": jok,
                    "pass": bool(in_band and k10["monotone_decreasing"] and jok), "blocking": False}
    return v


def run_a4(cfg, deadline=None):
    """Runner task for run.kind = a4 (DL-114)."""
    import yaml
    from .. import config as C
    from .. import provenance as P
    params = load_a4_params()
    rep_path = C.repo_root() / cfg["robustness"]["criteria_file"]
    with open(rep_path, "r", encoding="utf-8") as fh:
        rep = yaml.safe_load(fh)
    arrays, S = compute_a4(params, cfg["model"]["tau_ms"], cfg["model"]["tau_d_ms"], deadline)
    verdicts = evaluate_a4(S, rep)
    flags = {"eta_H": S["eta_H"], "summary": S, "verdicts": verdicts,
             "replication_yaml_sha256": P.sha256_file(rep_path), "grid_status": "working values, UNVERIFIED"}
    msg = f"A4: eta_H {S['eta_H']}; " + ", ".join(f"{k} {'pass' if x['pass'] else 'fail'}" for k, x in verdicts.items())
    return {"arrays": arrays, "message": msg, "flags": flags}
