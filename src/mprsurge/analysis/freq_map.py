"""A6 frequency map and K10 recheck (plan 5.2 A6, Table 7.1 K8 and K10, CP23; MS6 step 6f, DL-131).

Pure: no Julia, no integration. Inputs are the frames from continuation.julia_io.load_a6 (cycle branches, one per slice of
a one-parameter continuation). Contours are the crossings of the cycle frequency with a level along each slice, joined over
the other plane coordinate; nothing is interpolated between slices. Tolerances here are working values (UNVERIFIED).
"""
from __future__ import annotations

import numpy as np

TAU_MS = 10.0
LEVELS_HZ = (25.0, 100.0)          # plan 5.2 A6 contours
K10_BAND_HZ = (5.0, 30.0)          # Table 7.1 K10
K10_BAND_SLACK = 0.10              # "+/- 10 percent"
K10_J_MAX_REL = 0.10               # "< 10 percent change over J from -40 to -5"
K10_MONO_TOL_HZ = 1e-6             # monotonicity tolerance on the interpolated grid (UNVERIFIED; A4 used 1e-9 on an exact grid)
K10_N_GRID = 64                    # same count as the A4 K10 line
BAND_G_HZ = (25.0, 100.0)          # K8 band, plan 7.1 (reasoned, not tested)


def branch(po, slice_id: str) -> dict:
    """Cycle branch of one slice, sorted by parameter, duplicate parameters dropped."""
    d = po[po["slice"] == slice_id].sort_values("param", kind="stable")
    d = d.drop_duplicates("param")
    return {k: d[k].to_numpy(dtype=float) for k in ("param", "frequency_hz", "amplitude_v")}


def freq_at(b: dict, x: float, col: str = "frequency_hz") -> float:
    """Linear interpolation of `col` on the branch at parameter x; NaN outside the branch range."""
    p = b["param"]
    if p.size < 2 or not (p[0] <= x <= p[-1]):
        return float("nan")
    return float(np.interp(x, p, b[col]))


def crossings(param, freq, level: float) -> list[float]:
    """Parameter values where freq crosses `level` (linear interpolation between consecutive points)."""
    p, f = np.asarray(param, float), np.asarray(freq, float) - level
    out = []
    for i in range(p.size - 1):
        if f[i] == 0.0:
            out.append(float(p[i]))
        elif f[i] * f[i + 1] < 0:
            out.append(float(p[i] - f[i] * (p[i + 1] - p[i]) / (f[i + 1] - f[i])))
    if p.size and f[-1] == 0.0:
        out.append(float(p[-1]))
    return out


def slice_summary(b: dict, levels=LEVELS_HZ) -> dict:
    """Frequency range, first branch point and crossings of the levels on one cycle branch."""
    f, p = b["frequency_hz"], b["param"]
    if f.size == 0:
        return {"n": 0}
    s = {"n": int(f.size), "param_first": float(p[0]), "param_last": float(p[-1]), "f_first": float(f[0]),
         "f_last": float(f[-1]), "f_min": float(f.min()), "f_max": float(f.max())}
    for lv in levels:
        c = crossings(p, f, lv)
        s[f"cross_{int(lv)}"] = c
    return s


def contour(slices: dict, levels=LEVELS_HZ) -> dict:
    """Contour points over one plane: `slices` maps the other coordinate (tau_d in ms, or J) to a branch dict.

    Returns, sorted by the other coordinate: other, hopf-side branch start (param_first), branch end (param_last), the first
    crossing of each level (NaN if none), the number of crossings, and f_first / f_max / f_min.
    """
    others = sorted(slices)
    out = {"other": np.array(others, float)}
    sums = [slice_summary(slices[o], levels) for o in others]
    for key in ("param_first", "param_last", "f_first", "f_min", "f_max", "n"):
        out[key] = np.array([s.get(key, np.nan) for s in sums], float)
    for lv in levels:
        c = [s.get(f"cross_{int(lv)}", []) for s in sums]
        out[f"c{int(lv)}"] = np.array([x[0] if x else np.nan for x in c], float)
        out[f"c{int(lv)}_count"] = np.array([len(x) for x in c], float)
    return out


# ---- K10 --------------------------------------------------------------------------------------------------------------

def rel_change(f) -> float:
    """(max - min) / mean over the finite values: the DL-115 / hopf.py definition of the J change."""
    f = np.asarray(f, float)
    f = f[np.isfinite(f)]
    if f.size < 2:
        return float("nan")
    return float((f.max() - f.min()) / f.mean())


def k10_tau_line(b: dict, tau_ms: float = TAU_MS, n: int = K10_N_GRID) -> dict:
    """Cycle frequency on an n-point grid over the oscillatory tau_d interval of one k10 branch (parameter = tau_d / tau)."""
    td = b["param"] * tau_ms
    grid = np.linspace(td[0], td[-1], n)
    f = np.interp(grid, td, b["frequency_hz"])
    a = np.interp(grid, td, b["amplitude_v"])
    df = np.diff(f)
    return {"tau_d_ms": grid, "freq_hz": f, "amp_v": a, "interval_ms": [float(td[0]), float(td[-1])],
            "freq_min": float(f.min()), "freq_max": float(f.max()), "max_increase_hz": float(max(df.max(), 0.0)),
            "monotone_decreasing": bool(np.all(df <= K10_MONO_TOL_HZ))}


def k10_band(fmin: float, fmax: float, band=K10_BAND_HZ, slack=K10_BAND_SLACK) -> bool:
    return bool(band[0] * (1 - slack) <= fmin and fmax <= band[1] * (1 + slack))


def k10_j_dependence(k10_branches: dict, linear: dict, tau_d_ms, j_max=K10_J_MAX_REL, tau_ms: float = TAU_MS) -> dict:
    """J change of the frequency at fixed tau_d, three readouts.

    k10_branches: J -> cycle branch dict (parameter tau_d / tau) at eta_bar = 1, Delta = 0.05.
    linear: tau_d_ms -> {"J": [...], "freq_hz": [...], "unstable": [...]}, the A4-type linear Im lambda at the same points.
    Readouts, each (max - min) / mean over J:
      linear_all       DL-115 definition: linear Im lambda at every J, stable-focus points included.
      linear_unstable  5k alternative (DL-124): the same, unstable points only.
      cycle            cycle frequency at the J values where a cycle exists at that tau_d (A5-type branch, Hopf to branch end);
                       the amplitude at each point is returned beside it.
    """
    out = {}
    for x in tau_d_ms:
        lin = linear[x]
        J, fl, un = np.asarray(lin["J"], float), np.asarray(lin["freq_hz"], float), np.asarray(lin["unstable"], bool)
        row = {"J": J.tolist(), "linear_freq_hz": fl.tolist(), "linear_is_unstable": un.tolist()}
        row["linear_all"] = {"rel_change": rel_change(fl), "n_J": int(np.isfinite(fl).sum())}
        row["linear_unstable"] = {"rel_change": rel_change(np.where(un, fl, np.nan)), "n_J": int(un.sum())}
        fc, ac = [], []
        for j in J:
            b = k10_branches.get(float(j))
            fc.append(freq_at(b, x / tau_ms) if b is not None else float("nan"))
            ac.append(freq_at(b, x / tau_ms, "amplitude_v") if b is not None else float("nan"))
        row["cycle_freq_hz"], row["cycle_amp_v"] = fc, ac
        row["cycle"] = {"rel_change": rel_change(fc), "n_J": int(np.isfinite(fc).sum()),
                        "J_without_cycle": [float(j) for j, f in zip(J, fc) if not np.isfinite(f)]}
        for k in ("linear_all", "linear_unstable", "cycle"):
            r = row[k]["rel_change"]
            row[k]["pass"] = bool(np.isfinite(r) and r < j_max)
        out[str(x)] = row
    return out


def linear_points(J_values, tau_d_ms, eta_bar: float, Delta: float, tau_ms: float = TAU_MS) -> dict:
    """Linear Im lambda (Hz) and instability at the K10 sweep points, from analysis.hopf (A4 code, DL-115)."""
    from .hopf import _hz, leading_mode
    out = {}
    for x in tau_d_ms:
        modes = [leading_mode(eta_bar, J, Delta, x / tau_ms) for J in J_values]
        out[x] = {"J": [float(j) for j in J_values], "freq_hz": [_hz(m["pair_im"], tau_ms) for m in modes],
                  "unstable": [bool(m["re_max"] > 0) for m in modes]}
    return out


# ---- assembly ---------------------------------------------------------------------------------------------------------

K10_J_VALUES = (-40.0, -30.0, -20.0, -10.0, -5.0)   # same J list as configs/A4_grids.yaml k10 (DL-115)
K10_TAU_D_MS = (8.0, 20.0, 40.0)                    # same tau_d values as DL-115
K10_REF = {"eta_bar": 1.0, "J": -20.0, "Delta": 0.05}   # ref_ceni (Table 3.2)
REF_DEVALLE = {"eta_bar": 4.0, "J": -21.0, "Delta": 0.3, "tau_d_ms": 5.0}


def _key(x: float) -> float:
    return round(float(x), 9)


def group_branches(julia: dict) -> dict:
    """{group: {other-key...}} from the slices' base parameters: eta_tau[Delta][tau_d_ms], eta_J[J], k10[J]."""
    po, g = julia["po"], {"eta_tau": {}, "eta_J": {}, "k10": {}}
    for sid, s in julia["slices"].items():
        bp = s["base_parameters"]
        b = branch(po, sid)
        if s["group"] == "eta_tau":
            g["eta_tau"].setdefault(_key(bp["Delta"]), {})[_key(bp["td"] * TAU_MS)] = (b, s)
        elif s["group"] == "eta_J":
            g["eta_J"][_key(bp["J"])] = (b, s)
        elif s["group"] == "k10":
            g["k10"][_key(bp["J"])] = (b, s)
    return g


def devalle_evidence(b: dict, s: dict, eta_H: float) -> dict:
    """Band G and the D40 evidence at ref_devalle (eta 4, J -21, Delta 0.3, tau_d 5 ms): frequency along the cycle branch."""
    eta_peak = max(4.0, eta_H + 2.0)
    p, f = b["param"], b["frequency_hz"]
    inside = (p >= eta_H - 1e-9) & (p <= eta_peak + 1e-9)
    grid = np.unique(np.concatenate([p[inside], [max(eta_H, p[0]), eta_peak]]))
    fg = np.interp(grid, p, f)
    f4 = freq_at(b, 4.0)
    return {"eta_H": eta_H, "eta_peak": eta_peak, "hopf_param_julia": s["hopf_param"], "f_at_eta_4": f4,
            "f_at_hopf_start": float(fg[0]), "f_at_eta_peak": float(fg[-1]), "f_min_region": float(fg.min()),
            "f_max_region": float(fg.max()), "f_linear_hopf_hz": s["hopf_frequency_hz"],
            "amp_at_eta_4": freq_at(b, 4.0, "amplitude_v"),
            "band_G_hz": list(BAND_G_HZ), "eta4_in_band": bool(BAND_G_HZ[0] <= f4 <= BAND_G_HZ[1]),
            "whole_region_ge_25": bool(fg.min() >= 25.0), "region_n_grid_points": int(grid.size)}


def build_a6(julia: dict, eta_H: float) -> tuple[dict, dict]:
    """(arrays for a6_freq_map.npz, summary dict). Pure analysis of the validated Julia slices."""
    g = group_branches(julia)
    arrays, summ = {}, {"levels_hz": list(LEVELS_HZ)}
    ids = list(julia["slices"])
    po = julia["po"]
    arrays["slice_ids"] = np.array(ids)
    arrays["slice_hopf_param"] = np.array([np.nan if julia["slices"][i]["hopf_param"] is None else julia["slices"][i]["hopf_param"]
                                           for i in ids], float)
    arrays["slice_n_hopf"] = np.array([julia["slices"][i]["n_hopf_points"] for i in ids], int)
    arrays["slice_status_ok"] = np.array([julia["slices"][i]["status"] == "ok" for i in ids], bool)
    idx = {i: k for k, i in enumerate(ids)}
    arrays["po_slice_index"] = po["slice"].map(idx).to_numpy(int)
    for col in ("param", "frequency_hz", "amplitude_v"):
        arrays[f"po_{col}"] = po[col].to_numpy(float)
    summ["slices"] = {i: {"group": s["group"], "status": s["status"], "error": s.get("error", ""), "hopf_param": s["hopf_param"],
                          "hopf_type": s["hopf_type"], "n_hopf_points": s["n_hopf_points"], "hopf_params_all": s["hopf_params_all"],
                          "n_po": s["n_po"], "po_param_max": s.get("po_param_max"), "wall_s": s["wall_s"],
                          "po_special_points": s["po_special_points"]} for i, s in julia["slices"].items()}
    # eta_bar-tau_d planes, one per Delta; eta_bar-J plane at tau_d 5 ms (Delta 0.3, UNVERIFIED: the plan names none)
    planes = {}
    for D, sl in g["eta_tau"].items():
        planes[f"eta_tau_D{D:g}"] = {k: v[0] for k, v in sl.items()}, {k: v[1] for k, v in sl.items()}
    planes["eta_J"] = {k: v[0] for k, v in g["eta_J"].items()}, {k: v[1] for k, v in g["eta_J"].items()}
    summ["planes"] = {}
    for name, (bs, ms) in planes.items():
        c = contour(bs)
        hopf = np.array([np.nan if ms[o]["hopf_param"] is None else ms[o]["hopf_param"] for o in c["other"]], float)
        for k, v in c.items():
            arrays[f"{name}_{k}"] = v
        arrays[f"{name}_hopf_eta"] = hopf
        arrays[f"{name}_n_hopf"] = np.array([ms[o]["n_hopf_points"] for o in c["other"]], float)
        summ["planes"][name] = {"other": c["other"].tolist(), "hopf_eta": hopf.tolist(),
                                "f_min": c["f_min"].tolist(), "f_max": c["f_max"].tolist(),
                                "c25": c["c25"].tolist(), "c100": c["c100"].tolist(),
                                "branch_end_eta": c["param_last"].tolist(),
                                "slices_without_cycle": [o for o in c["other"] if bs[o]["param"].size == 0]}
    # ref_devalle: band G and D40 evidence
    dvb, dvs = g["eta_tau"][_key(REF_DEVALLE["Delta"])][_key(REF_DEVALLE["tau_d_ms"])]
    summ["devalle"] = devalle_evidence(dvb, dvs, eta_H)
    # K10 recheck
    kb = {float(j): v[0] for j, v in g["k10"].items()}
    ref = kb[K10_REF["J"]]
    line = k10_tau_line(ref)
    arrays.update(k10_tau_d_ms=line["tau_d_ms"], k10_cycle_freq_hz=line["freq_hz"], k10_cycle_amp_v=line["amp_v"])
    lin = linear_points(K10_J_VALUES, K10_TAU_D_MS, K10_REF["eta_bar"], K10_REF["Delta"])
    jd = k10_j_dependence(kb, lin, K10_TAU_D_MS)
    band_ok = k10_band(line["freq_min"], line["freq_max"])
    summ["k10"] = {"ref": K10_REF, "interval_ms": line["interval_ms"], "freq_min": line["freq_min"], "freq_max": line["freq_max"],
                   "band_hz": list(K10_BAND_HZ), "band_slack": K10_BAND_SLACK, "in_band_with_slack": band_ok,
                   "monotone_decreasing": line["monotone_decreasing"], "max_increase_hz": line["max_increase_hz"],
                   "mono_tol_hz": K10_MONO_TOL_HZ, "branch_reaches_ms": float(ref["param"][-1] * TAU_MS),
                   "J_limit": K10_J_MAX_REL, "J_dependence": jd,
                   "sub_checks": {"band": band_ok, "monotone": line["monotone_decreasing"],
                                  **{f"J_{d}_{x:g}ms": jd[str(x)][d]["pass"] for x in K10_TAU_D_MS
                                     for d in ("linear_all", "linear_unstable", "cycle")}},
                   "blocking": False}
    summ["k10"]["pass_all"] = bool(all(summ["k10"]["sub_checks"].values()))
    return arrays, summ
