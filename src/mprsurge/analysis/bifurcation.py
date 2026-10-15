"""A1: fixed points and stability of M2 on the (eta_bar, J) plane (plan 5.2 A1, 3.1).

Analysis only, no integration. Grid: Delta = 1, eta_bar/Delta in [-10, 2] (241 points) and
J/sqrt(Delta) in [0, 20] (201 points). Half spacing (0.025, 0.05) is added in a refined
region (DL-085; widths UNVERIFIED, the user's): a band of +-4 base cells in eta_bar along
the formula fold curve, and a box of +-10 base cells in eta_bar and J around the cusp.
The refined nodes lie on the half-spacing lattice (481 x 401), whose even-even nodes are
the base nodes, so the refined grid is nested in the base grid.

Formulas (MPR Fig. 1; K1, K2 of Table 7.1):
    fold:   (eta, J)_SN(r) = [-pi^2 r^2 - 3 D^2/(2 pi r)^2, 2 pi^2 r + D^2/(2 pi^2 r^3)]
    focus:  eta_f(J) = -(J/2 pi)^2 - (pi D/J)^2   (discriminant zero at r = J/(2 pi^2))
Cusp: dJ_SN/dr = 0 at r = (3 D^2/(4 pi^4))^(1/4).

`run_a1` is the runner task for run.kind = a1 (task(cfg, deadline) -> dict, see run.py).
"""
from __future__ import annotations

import time

import numpy as np
import yaml

from .. import config as C
from .. import provenance as P
from ..errors import RunTimeout
from ..models.fixed_points import classify_all

PI2 = np.pi ** 2

# A1 grid (plan 5.2 A1) and cell sizes (K1, K2 in replication.yaml use the same cell)
# (the values live in config.A1_GRID, which the config hash covers, DL-087)
N_ETA, N_J = C.A1_GRID["n_eta"], C.A1_GRID["n_J"]
ETA_RANGE, J_RANGE = tuple(C.A1_GRID["eta_range"]), tuple(C.A1_GRID["J_range"])
D_ETA, D_J = 0.05, 0.1                      # base spacing
# DL-085 refinement widths, in base cells. UNVERIFIED, the user's.
BAND_CELLS, BOX_CELLS = C.A1_GRID["band_cells"], C.A1_GRID["box_cells"]
MAX_ROOTS = 3
LABELS = ("none", "stable_node", "stable_focus", "unstable_node", "unstable_focus", "saddle")
CODE = {name: k for k, name in enumerate(LABELS)}
EDGE_TOL = 1e-9


# --- formulas ---------------------------------------------------------------------------------

def sn_curve_2d(r, Delta=1.0):
    """Fold (saddle-node) curve (eta_bar, J) parametrised by the rate r at the fold."""
    r = np.asarray(r, dtype=float)
    return (-PI2 * r**2 - 3.0 * Delta**2 / (2.0 * np.pi * r) ** 2,
            2.0 * PI2 * r + Delta**2 / (2.0 * PI2 * r**3))


def cusp_point(Delta=1.0):
    """(r, eta_bar, J) at the cusp of the fold curve (dJ_SN/dr = 0)."""
    r = (3.0 * Delta**2 / (4.0 * np.pi**4)) ** 0.25
    eta, J = sn_curve_2d(r, Delta)
    return float(r), float(eta), float(J)


def focus_boundary_2d(J, Delta=1.0):
    """eta_f(J): the node/focus boundary of the high-rate fixed point."""
    J = np.asarray(J, dtype=float)
    return -((J / (2.0 * np.pi)) ** 2) - (np.pi * Delta / J) ** 2


def fold_etas(J, Delta=1.0):
    """eta_bar values of the fold curve at this J (0 or 2 of them; J >= J_cusp)."""
    roots = np.roots([2.0 * PI2, -J, 0.0, 0.0, Delta**2 / (2.0 * PI2)])
    r = np.sort([z.real for z in roots if z.real > 0 and abs(z.imag) <= 1e-7 * abs(z)])
    return sn_curve_2d(np.array(r), Delta)[0] if len(r) else np.empty(0)


# --- grids ------------------------------------------------------------------------------------

def base_grid():
    return np.linspace(*ETA_RANGE, N_ETA), np.linspace(*J_RANGE, N_J)


def fine_grid():
    """Half-spacing lattice; entry 2k is base node k."""
    return np.linspace(*ETA_RANGE, 2 * N_ETA - 1), np.linspace(*J_RANGE, 2 * N_J - 1)


def refined_mask(eta_f, J_f, Delta=1.0, band_cells=BAND_CELLS, box_cells=BOX_CELLS):
    """Fine-lattice nodes in the refined region: the fold band union the cusp box (DL-085)."""
    mask = np.zeros((len(eta_f), len(J_f)), dtype=bool)
    for j, J in enumerate(J_f):
        for e in fold_etas(J, Delta):
            mask[:, j] |= np.abs(eta_f - e) <= band_cells * D_ETA + EDGE_TOL
    _, eta_c, J_c = cusp_point(Delta)
    box = (np.abs(eta_f[:, None] - eta_c) <= box_cells * D_ETA + EDGE_TOL) & \
          (np.abs(J_f[None, :] - J_c) <= box_cells * D_J + EDGE_TOL)
    return mask | box


# --- classification ---------------------------------------------------------------------------

def classify_point(eta, J, Delta=1.0):
    """(n_roots, r, v, label codes, discriminants), arrays padded to MAX_ROOTS."""
    r, v = np.full(MAX_ROOTS, np.nan), np.full(MAX_ROOTS, np.nan)
    code, disc = np.zeros(MAX_ROOTS, dtype=np.int8), np.full(MAX_ROOTS, np.nan)
    found = classify_all(eta, J, Delta)
    if len(found) > MAX_ROOTS:
        raise ValueError(f"{len(found)} positive roots at eta_bar={eta}, J={J}")
    for k, (y, label, ev) in enumerate(found):
        r[k], v[k], code[k] = y[0], y[1], CODE[label]
        disc[k] = (ev[0] - ev[1]) ** 2      # trace^2 - 4 det = (lambda1 - lambda2)^2, real: sign of the discriminant
    return len(found), r, v, code, disc.real


def classify_nodes(eta_nodes, J_nodes, Delta=1.0, deadline=None):
    """Classify (eta_nodes[k], J_nodes[k]) pairs; returns a dict of arrays with leading axis k."""
    n = len(eta_nodes)
    out = {"n_roots": np.zeros(n, dtype=np.int8), "r": np.full((n, MAX_ROOTS), np.nan),
           "v": np.full((n, MAX_ROOTS), np.nan), "label": np.zeros((n, MAX_ROOTS), dtype=np.int8),
           "disc": np.full((n, MAX_ROOTS), np.nan)}
    for k in range(n):
        if deadline is not None and k % 2048 == 0 and time.monotonic() > deadline:
            raise RunTimeout("wall-time limit reached in the A1 classification")
        out["n_roots"][k], out["r"][k], out["v"][k], out["label"][k], out["disc"][k] = \
            classify_point(eta_nodes[k], J_nodes[k], Delta)
    return out


# --- boundaries on a grid ---------------------------------------------------------------------

def count_change_nodes(counts, valid=None):
    """Boolean array: node whose root count differs from the next node in eta or in J.

    This is the K1 edge definition of DL-064 / DL-078 (the lower node of the pair). `valid`
    marks nodes that exist; a pair is compared only when both exist.
    """
    edge = np.zeros(counts.shape, dtype=bool)
    ok = np.ones(counts.shape, dtype=bool) if valid is None else valid
    edge[:-1, :] |= (counts[:-1, :] != counts[1:, :]) & ok[:-1, :] & ok[1:, :]
    edge[:, :-1] |= (counts[:, :-1] != counts[:, 1:]) & ok[:, :-1] & ok[:, 1:]
    return edge


def k1_points(Delta=1.0):
    """DL-064: 20 r values uniform on the r-interval where the formula point lies in the grid."""
    fine = np.linspace(0.05, 3.0, 200001)
    e, J = sn_curve_2d(fine, Delta)
    inside = (e >= ETA_RANGE[0]) & (e <= ETA_RANGE[1]) & (J >= J_RANGE[0]) & (J <= J_RANGE[1])
    idx = np.nonzero(inside)[0]
    if not np.all(inside[idx[0]:idx[-1] + 1]):
        raise ValueError("the K1 formula points inside the grid are not one r-interval")
    return np.linspace(fine[idx[0]], fine[idx[-1]], 20)


def _within_cell(eta_nodes, J_nodes, eta0, J0, cell):
    return (np.abs(eta_nodes - eta0) <= cell[0] + EDGE_TOL) & (np.abs(J_nodes - J0) <= cell[1] + EDGE_TOL)


def k1_check(r_values, eta_grid, J_grid, edge, cell, valid=None):
    """Per r: the nearest count-change node (offsets in base cells, eta and J) and pass.

    Pass = a count-change node within `cell` = (d_eta, d_J) of the formula point (frozen K1)."""
    ie, jj = np.nonzero(edge)
    n = len(r_values)
    d_eta, d_J, ok = np.full(n, np.nan), np.full(n, np.nan), np.zeros(n, dtype=bool)
    eta0, J0 = sn_curve_2d(r_values)
    for k in range(n):
        de = (eta_grid[ie] - eta0[k]) / D_ETA
        dj = (J_grid[jj] - J0[k]) / D_J
        ok[k] = bool(_within_cell(eta_grid[ie], J_grid[jj], eta0[k], J0[k], cell).any())
        m = np.argmin(np.maximum(np.abs(de), np.abs(dj)))
        d_eta[k], d_J[k] = de[m], dj[m]
    return ok, d_eta, d_J


def k2_check(J_rows, eta_grid, disc_high, cell, Delta=1.0):
    """K2 on rows of constant J: the sign of the discriminant of the highest-r root changes
    within `cell[0]` of eta_f(J). disc_high has shape (n_eta, n_rows)."""
    eta_f = focus_boundary_2d(J_rows, Delta)
    ok = np.zeros(len(J_rows), dtype=bool)
    off = np.full(len(J_rows), np.nan)
    nchg = np.zeros(len(J_rows), dtype=int)
    for j in range(len(J_rows)):
        s = np.sign(disc_high[:, j])
        i = np.nonzero(s[:-1] != s[1:])[0]
        nchg[j] = len(i)
        if len(i) == 0:
            continue
        dist = np.minimum(np.abs(eta_grid[i] - eta_f[j]), np.abs(eta_grid[i + 1] - eta_f[j]))
        m = np.argmin(dist)
        off[j] = (0.5 * (eta_grid[i[m]] + eta_grid[i[m] + 1]) - eta_f[j]) / D_ETA
        ok[j] = bool(dist[m] <= cell[0] + EDGE_TOL)
    return eta_f, ok, off, nchg


def _row_edges(counts_row, eta_row, valid_row):
    """Midpoints of eta intervals where the root count changes between two existing nodes."""
    i = np.nonzero((counts_row[:-1] != counts_row[1:]) & valid_row[:-1] & valid_row[1:])[0]
    return 0.5 * (eta_row[i] + eta_row[i + 1])


# --- the Table 6.2 halving record -------------------------------------------------------------

def halving_record(eta_b, J_b, n_b, eta_f, J_f, n_f, valid_f, Delta=1.0):
    """Boundary shift between base and half spacing, in base cells (Table 6.2, D31). Recorded only.

    Fold: on every base J row at or above the cusp, the count-change position in eta (midpoint of
    the node pair) of each of the two formula folds, from the base grid and from the half
    lattice row, shift = (base - half)/D_ETA; NaN where a fold is not resolved on either grid
    (the two folds in one cell, or outside the refined region).
    Cusp: the lowest J with three roots (bistable wedge tip) in the cusp box, and the eta of
    the nodes there, base against half; shifts in base cells.
    """
    rows = np.arange(N_J)
    fold_eta_b, fold_eta_h = np.full((N_J, 2), np.nan), np.full((N_J, 2), np.nan)
    formula = np.full((N_J, 2), np.nan)
    for j in rows:
        fe = np.sort(fold_etas(J_b[j], Delta))
        if len(fe) != 2:
            continue
        formula[j] = fe
        eb = _row_edges(n_b[:, j], eta_b, np.ones(N_ETA, dtype=bool))
        eh = _row_edges(n_f[:, 2 * j], eta_f, valid_f[:, 2 * j])
        for k in range(2):
            if fe[k] < ETA_RANGE[0] or fe[k] > ETA_RANGE[1]:
                continue
            for arr, src in ((fold_eta_b, eb), (fold_eta_h, eh)):
                near = src[np.abs(src - fe[k]) <= 2 * D_ETA]
                if len(near):
                    arr[j, k] = near[np.argmin(np.abs(near - fe[k]))]
    shift = (fold_eta_b - fold_eta_h) / D_ETA
    # cusp: wedge tip in the cusp box
    _, eta_c, J_c = cusp_point(Delta)
    tips = {}
    for tag, eg, Jg, cnt, val in (("base", eta_b, J_b, n_b, None), ("half", eta_f, J_f, n_f, valid_f)):
        box = (np.abs(eg[:, None] - eta_c) <= BOX_CELLS * D_ETA + EDGE_TOL) & \
              (np.abs(Jg[None, :] - J_c) <= BOX_CELLS * D_J + EDGE_TOL)
        three = box & (cnt == 3) & (True if val is None else val)
        if not three.any():
            tips[tag] = (np.nan, np.nan)
            continue
        jmin = np.nonzero(three.any(axis=0))[0][0]
        tips[tag] = (Jg[jmin], eg[three[:, jmin]].mean())
    cusp = {"J_base": tips["base"][0], "J_half": tips["half"][0],
            "eta_base": tips["base"][1], "eta_half": tips["half"][1],
            "J_formula": J_c, "eta_formula": eta_c,
            "J_shift_cells": (tips["base"][0] - tips["half"][0]) / D_J,
            "eta_shift_cells": (tips["base"][1] - tips["half"][1]) / D_ETA}
    return {"J": J_b, "formula_eta": formula, "eta_base": fold_eta_b, "eta_half": fold_eta_h,
            "shift_cells": shift}, cusp


# --- the task ---------------------------------------------------------------------------------

def _load_k_cells(cfg):
    path = C.repo_root() / cfg["replication"]["tolerances_file"]
    with open(path, "r", encoding="utf-8") as fh:
        rep = yaml.safe_load(fh)
    cell = lambda k: (float(rep[k]["cell"]["d_eta_bar"]), float(rep[k]["cell"]["d_J"]))
    return {"K1": cell("K1"), "K2": cell("K2"), "K3": rep["K3"]["point"]}, P.sha256_file(path)


def compute_a1(Delta=1.0, deadline=None, cells=None):
    """The whole A1 analysis; returns (arrays, summary). `cells` = {"K1": (de, dJ), "K2": ..., "K3": point}."""
    if Delta != 1.0:
        raise ValueError("A1 is defined at Delta = 1 (plan 5.2 A1)")
    cells = cells or {"K1": (D_ETA, D_J), "K2": (D_ETA, D_J),
                      "K3": {"eta_bar_over_Delta": -5.0, "J_over_sqrtDelta": 15.0}}
    eta_b, J_b = base_grid()
    eta_f, J_f = fine_grid()
    # nesting: the base grid is the even-even sub-lattice of the fine lattice (checked by the test too)
    if not (np.allclose(eta_f[::2], eta_b, rtol=0, atol=1e-12) and np.allclose(J_f[::2], J_b, rtol=0, atol=1e-12)):
        raise ValueError("half-spacing lattice does not contain the base grid")
    mask = refined_mask(eta_f, J_f, Delta)

    EB, JB = np.meshgrid(eta_b, J_b, indexing="ij")
    base = classify_nodes(EB.ravel(), JB.ravel(), Delta, deadline)
    shape2, shape3 = (N_ETA, N_J), (N_ETA, N_J, MAX_ROOTS)
    base = {k: (v.reshape(shape3) if v.ndim == 2 else v.reshape(shape2)) for k, v in base.items()}

    ie, je = np.nonzero(mask)
    ref = classify_nodes(eta_f[ie], J_f[je], Delta, deadline)
    n_f = np.zeros(mask.shape, dtype=np.int8)
    n_f[ie, je] = ref["n_roots"]

    # --- K1 at base and at half spacing
    r_k1 = k1_points(Delta)
    cell1 = cells["K1"]
    ok_b, de_b, dj_b = k1_check(r_k1, eta_b, J_b, count_change_nodes(base["n_roots"]), cell1)
    ok_h, de_h, dj_h = k1_check(r_k1, eta_f, J_f, count_change_nodes(n_f, mask), cell1)

    # --- K2: discriminant sign of the highest-r root along eta at each J row
    def highest(d):
        return d["disc"][..., :MAX_ROOTS][np.arange(len(d["n_roots"].ravel())).reshape(d["n_roots"].shape), :] \
            if False else np.take_along_axis(d["disc"], np.maximum(d["n_roots"][..., None].astype(int) - 1, 0), axis=-1)[..., 0]
    disc_b = highest(base)
    J_rows = J_b[1:]                                           # J = 0 has no eta_f
    eta_fk, ok2_b, off2_b, nchg_b = k2_check(J_rows, eta_b, disc_b[:, 1:], cells["K2"], Delta)
    in_grid = (eta_fk >= ETA_RANGE[0]) & (eta_fk <= ETA_RANGE[1])
    disc_h = np.full(mask.shape, np.nan)
    disc_h[ie, je] = highest(ref)
    k2_half_rows = np.array([j for j in range(1, len(J_f)) if mask[:, j].any()
                             and ETA_RANGE[0] <= focus_boundary_2d(J_f[j], Delta) <= ETA_RANGE[1]])
    # half spacing: the stretch of consecutive refined nodes around eta_f, per row
    ok2_h = np.zeros(len(k2_half_rows), dtype=bool)
    off2_h = np.full(len(k2_half_rows), np.nan)
    eta_f_h = focus_boundary_2d(J_f[k2_half_rows], Delta)
    for q, j in enumerate(k2_half_rows):
        col = disc_h[:, j]
        i = np.nonzero(~np.isnan(col[:-1]) & ~np.isnan(col[1:]) & (np.sign(col[:-1]) != np.sign(col[1:])))[0]
        if len(i):
            dist = np.minimum(np.abs(eta_f[i] - eta_f_h[q]), np.abs(eta_f[i + 1] - eta_f_h[q]))
            m = np.argmin(dist)
            if dist[m] <= 2 * D_ETA:
                off2_h[q] = (0.5 * (eta_f[i[m]] + eta_f[i[m] + 1]) - eta_f_h[q]) / (D_ETA / 2)
                ok2_h[q] = bool(dist[m] <= cells["K2"][0] + EDGE_TOL)
    # --- K3
    p3 = cells["K3"]
    i3 = int(np.argmin(np.abs(eta_b - p3["eta_bar_over_Delta"])))
    j3 = int(np.argmin(np.abs(J_b - p3["J_over_sqrtDelta"])))
    labels3 = sorted(LABELS[c] for c in base["label"][i3, j3] if c)
    k3_ok = labels3 == ["saddle", "stable_focus", "stable_node"]
    k3_refined = bool(mask[2 * i3, 2 * j3])

    # --- C9: does any node (stable or unstable) exist anywhere on the grid
    codes = base["label"]
    node_codes = (CODE["stable_node"], CODE["unstable_node"])
    is_node = np.isin(codes, node_codes)
    node_exists = bool(is_node.any())
    node_J_min = float(JB[is_node.any(axis=-1)].min()) if node_exists else np.nan
    # highest-r root a node (the branch that carries the ring)?
    top = np.take_along_axis(codes, np.maximum(base["n_roots"][..., None].astype(int) - 1, 0), axis=-1)[..., 0]
    node_on_top = bool(np.isin(top, node_codes).any())
    # a node needs J > 2 pi^2 r*: the discriminant is 8 r (J - 2 pi^2 r)
    node_needs_J = bool(np.all((JB[..., None] > 2 * PI2 * base["r"])[is_node]))

    halv, cusp = halving_record(eta_b, J_b, base["n_roots"], eta_f, J_f, n_f, mask, Delta)
    r_c, eta_c, J_c = cusp_point(Delta)

    arrays = {
        "eta_over_Delta": eta_b, "J_over_sqrtDelta": J_b,
        "n_roots": base["n_roots"], "r": base["r"], "v": base["v"],
        "label": base["label"], "disc": base["disc"],
        "label_names": np.array(LABELS),
        "eta_fine": eta_f, "J_fine": J_f, "refined_mask": mask,
        "refined_ie": ie.astype(np.int32), "refined_je": je.astype(np.int32),
        "refined_n_roots": ref["n_roots"], "refined_r": ref["r"], "refined_v": ref["v"],
        "refined_label": ref["label"], "refined_disc": ref["disc"],
        "refine_band_cells": np.array(BAND_CELLS), "refine_box_cells": np.array(BOX_CELLS),
        "cusp_r_eta_J": np.array([r_c, eta_c, J_c]),
        "halving_fold_J": halv["J"], "halving_fold_eta_formula": halv["formula_eta"],
        "halving_fold_eta_base": halv["eta_base"], "halving_fold_eta_half": halv["eta_half"],
        "halving_fold_shift_cells": halv["shift_cells"],
        "halving_cusp_names": np.array(list(cusp)), "halving_cusp_values": np.array(list(cusp.values()), dtype=float),
        "k1_r": r_k1, "k1_pass_base": ok_b, "k1_pass_half": ok_h,
        "k1_nearest_eta_cells_base": de_b, "k1_nearest_J_cells_base": dj_b,
        "k1_nearest_eta_cells_half": de_h, "k1_nearest_J_cells_half": dj_h,
        "k2_J": J_rows, "k2_eta_f": eta_fk, "k2_in_grid": in_grid,
        "k2_pass_base": ok2_b, "k2_offset_cells_base": off2_b, "k2_n_sign_changes_base": nchg_b,
        "k2_half_J": J_f[k2_half_rows], "k2_pass_half": ok2_h, "k2_offset_cells_half": off2_h,
        "k3_labels": np.array(labels3), "k3_pass": np.array(k3_ok), "k3_in_refined_region": np.array(k3_refined),
        "c9_node_region_exists": np.array(node_exists), "c9_node_count_nodes": np.array(int(is_node.sum())),
        "c9_node_min_J": np.array(node_J_min), "c9_node_on_highest_root": np.array(node_on_top),
        "c9_nodes_have_J_above_2pi2r": np.array(node_needs_J),
    }
    summary = {
        "n_base_nodes": int(N_ETA * N_J), "n_refined_nodes": int(mask.sum()),
        "k1_base": f"{int(ok_b.sum())}/20", "k1_half": f"{int(ok_h.sum())}/20",
        "k2_base": f"{int(ok2_b[in_grid].sum())}/{int(in_grid.sum())}",
        "k2_half": f"{int(ok2_h.sum())}/{len(ok2_h)} refined rows",
        "k3": "pass" if k3_ok else "fail", "c9_node_region_exists": node_exists,
        "refinement_widths": f"band +-{BAND_CELLS} cells, box +-{BOX_CELLS} cells (UNVERIFIED, DL-085)",
    }
    return arrays, summary


def run_a1(cfg, deadline):
    """Runner task for run.kind = a1."""
    cells, sha = _load_k_cells(cfg)
    arrays, summary = compute_a1(cfg["model"]["Delta"], deadline, cells)
    flags = {**summary, "a1_grid": dict(C.A1_GRID), "replication_yaml_sha256": sha, "refinement_widths_status": "UNVERIFIED"}
    msg = ("K1 base {k1_base} half {k1_half}; K2 base {k2_base} half {k2_half}; "
           "K3 {k3}; C9 node region {c9_node_region_exists}").format(**summary)
    return {"arrays": arrays, "message": msg, "flags": flags}
