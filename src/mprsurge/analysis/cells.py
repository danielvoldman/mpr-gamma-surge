"""S5 baseline-only cell lists (7d; DL-136 D-4, plan Table 6.2 S5, CP20, D12). Analysis only, nothing integrated.

The headline cell, the map-1 cells (Delta x tau_d, P2, T_ramp 120 s) and the map-2 cells (J0 x T_ramp, Delta 0.3, tau_d 5 ms).
Grids come from configs/S5_cells.yaml: Delta linear, tau_d log, J0 linear, T_ramp log (working defaults, UNVERIFIED,
owner-ruled in DL-136 D-4). For each cell: eta_H is the lowest Hopf crossing along eta_bar (analysis.hopf) at the cell's
(J0, Delta, tau_d); a cell with no crossing inherits the headline eta_H (CP20), so it gets the headline eta_start 1.396046.
The start state is the fixed point at eta_start = eta_H - 1.5 (D12); its stability and type are recorded for every cell.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np
import yaml

from .. import config as C
from ..models.fixed_points import fixed_points
from ..models.mpr3d import jacobian_3d
from . import hopf

CELLS_FILE = "configs/S5_cells.yaml"
PATH_A4_FILE = "configs/path_A4.yaml"


def load_spec() -> dict:
    with open(C.repo_root() / CELLS_FILE, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def headline_eta_H() -> float:
    """The A4 eta_H at ref_devalle (DL-115), as layered into the headline run (configs/path_A4.yaml)."""
    with open(C.repo_root() / PATH_A4_FILE, "r", encoding="utf-8") as fh:
        return float(yaml.safe_load(fh)["path"]["eta_H"])


def axis(spec: dict) -> np.ndarray:
    """One grid axis: lo, hi inclusive, n points, linear or log."""
    f = np.geomspace if spec.get("spacing") == "log" else np.linspace
    return f(float(spec["lo"]), float(spec["hi"]), int(spec["n"]))


def start_state(eta_start: float, J: float, Delta: float, tau_d_tau: float) -> dict:
    """Fixed point at the path start and its stability record (J < 0: one fixed point).

    type: stable_focus, stable_node, unstable_focus, unstable_node or saddle (3 eigenvalues of the M3 Jacobian).
    """
    fp = fixed_points(eta_start, J, Delta, model="M3")
    if len(fp) != 1:
        raise ValueError(f"{len(fp)} fixed points at eta_bar={eta_start}, J={J}, Delta={Delta}: the baseline needs one")
    ev = np.linalg.eigvals(jacobian_3d(fp[0], J, tau_d_tau))
    focus = bool(np.any(np.abs(ev.imag) > 1e-12))
    if np.all(ev.real < 0):
        kind = "stable_focus" if focus else "stable_node"
    elif np.all(ev.real > 0):
        kind = "unstable_focus" if focus else "unstable_node"
    else:
        kind = "saddle" if not focus else "unstable_focus"     # a complex pair with Re > 0 and a real root of either sign
    return {"r": float(fp[0][0]), "v": float(fp[0][1]), "s": float(fp[0][2]), "type": kind,
            "stable": bool(np.all(ev.real < 0)), "re_max": float(ev.real.max()), "n_fixed_points": 1}


def _cell(index, name, kind, ij, J0, Delta, tau_d_ms, T_ramp_s, tau_ms, eg, eta_H_head, cache) -> dict:
    key = (round(J0, 12), round(Delta, 12), round(tau_d_ms, 12))
    if key not in cache:
        cache[key] = hopf.lowest_eta_hopf(eg, J0, Delta, tau_d_ms / tau_ms)
    c = cache[key]
    found = c is not None
    eta_H = float(c["eta_bar"]) if found else eta_H_head
    eta_start = eta_H - C.ETA_START_OFFSET
    st = start_state(eta_start, J0, Delta, tau_d_ms / tau_ms)
    return {"index": index, "name": name, "kind": kind, "ij": list(ij), "J0": float(J0), "Delta": float(Delta),
            "tau_d_ms": float(tau_d_ms), "T_ramp_s": float(T_ramp_s), "hopf_found": found, "eta_H": eta_H,
            "eta_start": eta_start, "eta_peak": max(C.ETA_PEAK_FLOOR, eta_H + C.ETA_PEAK_OFFSET), "start": st}


def build_cells(spec: dict | None = None, tau_ms: float = 10.0) -> list[dict]:
    """The full cell list: headline (index 0), map 1 (Delta outer, tau_d inner), map 2 (J0 outer, T_ramp inner)."""
    spec = spec or load_spec()
    eg = hopf._grid(hopf.load_a4_params()["grids"]["eta_bar"])
    eta_H_head = headline_eta_H()
    h, m1, m2 = spec["headline"], spec["map1"], spec["map2"]
    cache: dict = {}
    cells = [_cell(0, "headline", "headline", (0, 0), h["J0"], h["Delta"], h["tau_d_ms"], h["T_ramp_s"], tau_ms, eg,
                   eta_H_head, cache)]
    for i, D in enumerate(axis(m1["Delta"])):
        for j, td in enumerate(axis(m1["tau_d_ms"])):
            cells.append(_cell(len(cells), f"m1_{i:02d}_{j:02d}", "map1", (i, j), m1["J0"], D, td, m1["T_ramp_s"],
                               tau_ms, eg, eta_H_head, cache))
    for k, J0 in enumerate(axis(m2["J0"])):
        for l, T in enumerate(axis(m2["T_ramp_s"])):
            cells.append(_cell(len(cells), f"m2_{k:02d}_{l:02d}", "map2", (k, l), J0, m2["Delta"], m2["tau_d_ms"], T,
                               tau_ms, eg, eta_H_head, cache))
    return cells


def overrides(cell: dict) -> dict:
    """resolve_config overrides for one cell (P2, constant before t_on; eta_H sets eta_start and eta_peak, D12)."""
    return {"model.Delta": cell["Delta"], "model.tau_d_ms": cell["tau_d_ms"], "model.J": cell["J0"],
            "path.J0": cell["J0"], "path.T_ramp_s": cell["T_ramp_s"], "path.eta_H": cell["eta_H"]}


def cell_list_hash(cells: list[dict]) -> str:
    """SHA-256 of the canonical JSON of the cell parameters (not the index names): changes with any grid change."""
    keys = ("kind", "J0", "Delta", "tau_d_ms", "T_ramp_s", "eta_H", "eta_start")
    return hashlib.sha256(C.canonical_json([[c[k] for k in keys] for c in cells]).encode("utf-8")).hexdigest()


def summary(cells: list[dict]) -> dict:
    """Counts and start-state statistics, per kind and overall."""
    out = {"n_cells": len(cells), "cell_list_sha256": cell_list_hash(cells), "kinds": {}}
    for kind in ("headline", "map1", "map2"):
        sel = [c for c in cells if c["kind"] == kind]
        types: dict[str, int] = {}
        for c in sel:
            types[c["start"]["type"]] = types.get(c["start"]["type"], 0) + 1
        out["kinds"][kind] = {"n": len(sel), "hopf_found": sum(c["hopf_found"] for c in sel),
                              "no_hopf": sum(not c["hopf_found"] for c in sel), "start_types": types,
                              "start_not_stable": sum(not c["start"]["stable"] for c in sel)}
    return out
