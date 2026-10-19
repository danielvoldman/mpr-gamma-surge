"""MS9 9b: map-1 re-timing on a clean tree and the 9.2 arithmetic (DL-216; docs/ms9_plan.md "Rulings", plan 9.2, Table 9.1, D36).

Analysis only. The sample is one batch of 10 concurrent map-1 cells: a 3 x 3 stratified sample (Delta index {0, 15, 29} x tau_d index
{0, 15, 29}) plus the cell nearest the headline (14, 12), P2 at T_ramp 120 s, mode D. From the ten per-cell walls the map-1 wall is
predicted three ways: (1) the 9a weighted method (analysis.timing.weighted_family_estimate: piecewise-linear interpolation of the cell
wall in (log Delta, log tau_d) over the 900 grid cells); (2) linear interpolation of the cell wall over the 900 cells in grid-index space
from the 3 x 3 stratified sample only (the extra cell is then an out-of-sample check); (3) the worst case, all 900 cells at the slowest
measured wall. Wall = sum of cell walls / workers, bounded below by the longest cell. The launch rule (9.2 step 3) is prediction <= 1.5 x
the Table 9.1 allowance (4.1 h, limit 6.15 h) and the D36 total <= 24 h. UNVERIFIED: every figure is a prediction from a sample under load
as found.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .. import config as C
from . import ms9_counts as MC
from . import ms9_runlist as RL
from . import timing as T

STRATA = (0, 15, 29)
NEAR_HEADLINE = (14, 12)
SAMPLE = tuple((i, j) for i in STRATA for j in STRATA) + (NEAR_HEADLINE,)
ALLOWANCE_H = MC.ALLOWANCE_H["S7_map1"]
RULE = 1.5


def sample_cells() -> list[tuple[int, int]]:
    return list(SAMPLE)


def label(i: int, j: int) -> str:
    return f"m1_{i:02d}_{j:02d}"


def _cell_values(walls: dict) -> np.ndarray:
    """(900,) interpolated walls from the 3 x 3 stratified sample by linear interpolation in grid-index space."""
    from scipy.interpolate import RegularGridInterpolator
    Z = np.array([[walls[(i, j)] for j in STRATA] for i in STRATA], float)
    f = RegularGridInterpolator((np.array(STRATA, float), np.array(STRATA, float)), Z, method="linear")
    ii, jj = np.meshgrid(np.arange(30), np.arange(30), indexing="ij")
    return f(np.column_stack([ii.ravel(), jj.ravel()]).astype(float))


def _summ(per_cell: np.ndarray, workers: int) -> dict:
    total = float(per_cell.sum()) / workers
    longest = float(per_cell.max())
    return {"n_cells": int(per_cell.size), "sum_s": float(per_cell.sum()), "total_s": total, "longest_s": longest,
            "prediction_s": max(total, longest), "mean_s_per_run": float(per_cell.mean()), "min_s_per_run": float(per_cell.min()),
            "max_s_per_run": longest}


def map1_predictions(walls: dict, workers: int = 10) -> dict:
    """The three predictions from {(i, j): wall_s} of the ten sample cells; each with its 1.5 x verdict."""
    missing = [c for c in SAMPLE if c not in walls]
    if missing:
        raise ValueError(f"sample cells missing: {missing}")
    meas = [(RL.map1_cell(i, j)["Delta"], RL.map1_cell(i, j)["tau_d_ms"], walls[(i, j)]) for (i, j) in SAMPLE]
    w = T.weighted_family_estimate(meas, T.map_grid(), workers)
    out = {"weighted_9a_method": {"n_cells": 900, "sum_s": w["total_s"] * workers, "total_s": w["total_s"], "longest_s": w["max_s_per_run"],
                                  "prediction_s": max(w["total_s"], w["max_s_per_run"]), "mean_s_per_run": w["mean_s_per_run"],
                                  "min_s_per_run": w["min_s_per_run"], "max_s_per_run": w["max_s_per_run"]}}
    vals = _cell_values(walls)
    out["index_interpolation"] = _summ(vals, workers)
    k = NEAR_HEADLINE[0] * 30 + NEAR_HEADLINE[1]
    out["index_interpolation"]["check_cell_14_12"] = {"interpolated_s": float(vals[k]), "measured_s": float(walls[NEAR_HEADLINE]),
                                                      "ratio": float(vals[k] / walls[NEAR_HEADLINE])}
    out["worst_case"] = _summ(np.full(900, max(walls[c] for c in SAMPLE)), workers)
    lim = RULE * ALLOWANCE_H * 3600.0
    for v in out.values():
        v["allowance_s"], v["limit_s"] = ALLOWANCE_H * 3600.0, lim
        v["ratio_to_allowance"] = v["prediction_s"] / v["allowance_s"]
        v["verdict"] = "PASS" if v["prediction_s"] <= lim else "FAIL"
        v["over_one_hour"] = v["prediction_s"] > 3600.0
    return out


def load_walls(sample_dir, workers: int = 10) -> tuple[dict, dict]:
    """({(i, j): wall_s}, info) from the stored timing_cell records; info lists the git.dirty flag of every record."""
    d = Path(sample_dir)
    walls, dirty, status = {}, {}, {}
    for (i, j) in SAMPLE:
        recs = sorted(d.glob(f"{label(i, j)}_*.json"))
        if not recs:
            continue
        rec = json.loads(recs[0].read_text(encoding="utf-8"))
        status[label(i, j)] = rec["status"]
        dirty[label(i, j)] = rec["git"]["dirty"]
        if rec["status"] == "ok":
            walls[(i, j)] = float(rec["wall_time_s"])
    return walls, {"dirty": dirty, "status": status}


def load_9a(root=None, workers: int = 10):
    """The 9a sample cells (results/timing/ms9, git.dirty = true: timing only) and the earlier headline record."""
    root = Path(root) if root else C.repo_root()
    earlier = T.load_cells(root / "results/timing/a4", ("headline", "delta_0.01", "delta_0.6", "delta_0.01_td1", "delta_0.01_td50", "delta_0.6_td1",
                                                        "delta_0.6_td50"), workers)
    for c in ("delta_0.01_td1", "delta_0.01_td50", "delta_0.6_td1", "delta_0.6_td50", "delta_0.01", "delta_0.6"):
        if c not in earlier:
            earlier.update(T.load_cells(root / "results/timing/clean", (c,), workers))
    cells = T.load_cells(root / "results/timing/ms9", MC.SAMPLE_CELLS, workers)
    cells["headline"] = earlier.get("headline") or T.load_cells(root / "results/timing/ms8d", ("ms8_dop_1e-10_t120",), workers).get("ms8_dop_1e-10_t120")
    return cells, earlier


def d36_with(map1_prediction_s: float, rows_9a: list, s11_s: float, analysis_s: float = 0.0) -> dict:
    """D36 conservative total (hours) with the map-1 row replaced by `map1_prediction_s` and an analysis allowance added (UNVERIFIED sum)."""
    rows = [dict(r) for r in rows_9a]
    for r in rows:
        if r["id"] == "S7_map1":
            r["prediction_s"] = map1_prediction_s
    d = MC.d36_conservative(rows, s11_s)
    if analysis_s:
        d["items_h"]["classification + A9 labelling (estimate, UNVERIFIED)"] = analysis_s / 3600.0
        d["total_h"] += analysis_s / 3600.0
    return d


def fmt_s(s: float) -> str:
    return f"{s:.1f} s" if s < 600 else (f"{s / 60:.1f} min" if s < 7200 else f"{s / 3600:.2f} h")


def report(walls: dict, info: dict, workers: int = 10, analysis_s: float = 0.0, root=None) -> str:
    pred = map1_predictions(walls, workers)
    cells9a, earlier = load_9a(root, workers)
    rows = MC.predict(cells9a, earlier, workers)
    s11 = MC.s11_informational(cells9a, workers)
    lines = [f"MS9 9b map-1 re-timing, {workers} concurrent cells, P2 T_ramp 120 s mode D, per-cell walls (s):"]
    for (i, j) in SAMPLE:
        c = RL.map1_cell(i, j)
        lines.append(f"  ({i:2d},{j:2d}) Delta {c['Delta']:.5f} tau_d {c['tau_d_ms']:7.3f} ms  eta_H {c['eta_H']:.4f}  wall {walls.get((i, j), float('nan')):8.1f} s  "
                     f"git.dirty {info['dirty'].get(label(i, j))}  {info['status'].get(label(i, j))}")
    lines.append(f"  dirty flags: {sorted(set(map(str, info['dirty'].values())))}")
    lines.append("")
    for k, v in pred.items():
        lines.append(f"{k:22s} prediction {fmt_s(v['prediction_s']):>9s} (sum/workers {fmt_s(v['total_s'])}, longest cell {fmt_s(v['longest_s'])}, mean {v['mean_s_per_run']:.0f} s)  "
                     f"limit {fmt_s(v['limit_s'])}  {v['verdict']}  {v['ratio_to_allowance']:.2f} x allowance {fmt_s(v['allowance_s'])}  over one hour: {v['over_one_hour']}")
    ck = pred["index_interpolation"]["check_cell_14_12"]
    lines.append(f"index interpolation check at (14, 12): interpolated {ck['interpolated_s']:.1f} s, measured {ck['measured_s']:.1f} s (ratio {ck['ratio']:.3f})")
    lines.append("")
    lines.append("D36 conservative total (hours; mixed bases, UNVERIFIED), 24 h cap:")
    for k, v in pred.items():
        d = d36_with(v["prediction_s"], rows, s11, analysis_s)
        lines.append(f"  map-1 figure {k:22s} total {d['total_h']:6.2f} h  margin {d['cap_h'] - d['total_h']:5.2f} h")
    if analysis_s:
        lines.append(f"  (includes the classification + A9 estimate {fmt_s(analysis_s)})")
    return "\n".join(lines)
