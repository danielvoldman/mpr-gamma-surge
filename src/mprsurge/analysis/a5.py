"""A5 analysis (plan 5.2 A5; MS6 step 6b): turns the validated Julia branches into the A5 arrays and flags.

Pure: no Julia, no integration. Inputs are the frames from continuation.julia_io.load_a5 and the A4 Hopf points.
Amplitude is v max - v min over the cycle (peak to peak, our readout, UNVERIFIED). Tolerances here are working
values (UNVERIFIED), recorded in the run record flags.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

TAU_MS = 10.0                  # Table 3.2 (ref_ceni and ref_devalle)
HOPF_MATCH_RTOL = 1e-4         # Hopf from Julia vs A4, relative (UNVERIFIED continuation tolerance)
CRIT_PARAM_TOL = 1e-3          # cycles below the Hopf parameter by more than this mean subcritical (UNVERIFIED)
CENI_POINTS_MS = (4.95, 8.0)   # S3 ceni points compared at 6e (DL-116)
CRIT_EXCLUDE_NEAR = 1e-3       # up-branch special points this close to the Hopf are not "folds of cycles" (UNVERIFIED)


def up_branch(po):
    """Cycles continued away from the Hopf point, sorted by parameter (the direction with the supercritical branch)."""
    d = po[po["direction"] == "up"].sort_values("param", kind="stable")
    return d.reset_index(drop=True)


def at_param(po, param: float, col: str) -> float:
    """PCHIP interpolation of `col` on the up branch at `param`; NaN outside the branch range."""
    d = up_branch(po)
    x = d["param"].to_numpy()
    if not (x[0] <= param <= x[-1]) or len(np.unique(x)) != len(x):
        return float("nan")
    return float(PchipInterpolator(x, d[col].to_numpy(dtype=float))(param))


def criticality(po, hopf_param: float, hopf_type: str, special_points) -> dict:
    """Supercritical check (K7): package verdict, no cycle on the wrong side of the Hopf, and no fold of cycles.

    Cycles on both directions of the continuation must lie at parameter >= hopf_param - CRIT_PARAM_TOL (a subcritical
    Hopf has a cycle branch on the other side). Special points of the up direction that are not near the Hopf and are
    of type fold are folds of cycles; down-direction points are the turn-around at the Hopf and are not counted.
    """
    pmin = float(po["param"].min())
    folds = [sp for sp in special_points
             if sp["direction"] == "up" and sp["type"] == "fold" and abs(sp["param"] - hopf_param) > CRIT_EXCLUDE_NEAR]
    stable_up = up_branch(po)["stable"].astype(bool)
    return {"package_type": hopf_type, "cycle_param_min": pmin,
            "cycles_below_hopf": bool(pmin < hopf_param - CRIT_PARAM_TOL),
            "n_folds_of_cycles": len(folds), "folds_of_cycles": folds,
            "up_branch_stable_fraction": float(stable_up.mean()),
            "supercritical": bool(hopf_type == "SuperCritical" and pmin >= hopf_param - CRIT_PARAM_TOL and not folds)}


def build_a5(julia: dict, a4_ceni_hopf_tau_d_ms: float, a4_eta_H: float) -> tuple[dict, dict]:
    """(arrays for a5_cycles.npz, flags for the record). Branch arrays are prefixed ceni_ and devalle_."""
    rec = julia["record"]["branches"]
    arrays: dict = {}
    flags: dict = {}
    for name in ("ceni", "devalle"):
        po = julia["po"][name]
        arrays[f"{name}_direction_up"] = (po["direction"] == "up").to_numpy()
        for col in ("param", "vmax", "vmin", "amplitude_v", "period_tau", "frequency_hz"):
            arrays[f"{name}_{col}"] = po[col].to_numpy(dtype=float)
        arrays[f"{name}_stable"] = po["stable"].to_numpy(dtype=bool)
        arrays[f"{name}_fixed_param"] = julia["fixed"][name]["param"].to_numpy(dtype=float)
        arrays[f"{name}_fixed_stable"] = julia["fixed"][name]["stable"].to_numpy(dtype=bool)
        arrays[f"{name}_fixed_v"] = julia["fixed"][name]["v"].to_numpy(dtype=float)
        arrays[f"{name}_fixed_r"] = julia["fixed"][name]["r"].to_numpy(dtype=float)
    arrays["ceni_tau_d_ms"] = arrays["ceni_param"] * TAU_MS
    ceni, dev = rec["ceni"], rec["devalle"]
    arrays["ceni_hopf_tau_d_ms"] = np.array([ceni["hopf_param"] * TAU_MS])
    arrays["devalle_hopf_eta_bar"] = np.array([dev["hopf_param"]])
    crit_c = criticality(julia["po"]["ceni"], ceni["hopf_param"], ceni["hopf_type"], ceni["po_special_points"])
    crit_d = criticality(julia["po"]["devalle"], dev["hopf_param"], dev["hopf_type"], dev["po_special_points"])
    flags["criticality_ceni"] = crit_c
    flags["criticality_devalle"] = crit_d
    # Hopf points against A4
    d_c = abs(ceni["hopf_param"] * TAU_MS - a4_ceni_hopf_tau_d_ms) / a4_ceni_hopf_tau_d_ms
    d_d = abs(dev["hopf_param"] - a4_eta_H) / abs(a4_eta_H)
    flags["hopf_vs_a4"] = {"ceni_tau_d_ms": ceni["hopf_param"] * TAU_MS, "a4_ceni_tau_d_ms": a4_ceni_hopf_tau_d_ms,
                           "ceni_rel_diff": d_c, "devalle_eta_H": dev["hopf_param"], "a4_eta_H": a4_eta_H,
                           "devalle_rel_diff": d_d, "rtol": HOPF_MATCH_RTOL,
                           "match": bool(d_c <= HOPF_MATCH_RTOL and d_d <= HOPF_MATCH_RTOL)}
    flags["hopf"] = {"ceni_frequency_hz": ceni["hopf_frequency_hz"], "devalle_frequency_hz": dev["hopf_frequency_hz"],
                     "n_hopf_points": {"ceni": ceni["n_hopf_points"], "devalle": dev["n_hopf_points"]}}
    # Cycle values at the S3 comparison points and A_ref (ref_devalle: eta_bar 4, J -21, Delta 0.3, tau_d 5 ms)
    pts = {}
    for ms in CENI_POINTS_MS:
        p = ms / TAU_MS
        pts[f"ceni_{ms}ms"] = {c: at_param(julia["po"]["ceni"], p, c)
                               for c in ("vmax", "vmin", "amplitude_v", "period_tau", "frequency_hz")}
    eta_ref = 4.0
    pts["devalle_ref"] = {c: at_param(julia["po"]["devalle"], eta_ref, c)
                          for c in ("vmax", "vmin", "amplitude_v", "period_tau", "frequency_hz")}
    flags["points"] = pts
    a_ref = pts["devalle_ref"]["amplitude_v"]
    arrays["A_ref"] = np.array([a_ref])
    flags["A_ref"] = {"value": a_ref, "definition": "v max - v min over the cycle at ref_devalle (eta_bar 4, J -21, Delta 0.3, tau_d 5 ms); "
                      "peak to peak, UNVERIFIED readout", "frequency_hz": pts["devalle_ref"]["frequency_hz"]}
    return arrays, flags
