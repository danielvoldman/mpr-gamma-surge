"""Timing cells for the feasibility gate (plan 9.2; MS3 step 3a, DL-094, DL-095).

Analysis only: resolves a named timing cell and reports what it would simulate. Nothing integrates.
A cell is configs/timing/<cell>.yaml, layered on the S5 run file (base.yaml, then S5.yaml, then the cell).
"""
from __future__ import annotations

import copy
import statistics
from pathlib import Path

from .. import config as C
from ..ramps import make_path
from ..units import s_to_tau

CELLS = ("headline", "delta_0.01", "delta_0.6", "delta_0.01_td1", "delta_0.01_td50", "delta_0.6_td1", "delta_0.6_td50", "p5_1000", "radau_1e-12", "radau_1e-12_t10", "radau_1e-10_t10", "mode_n", "m2_ramp")


def cell_path(cell: str):
    return C.repo_root() / "configs" / "timing" / f"{cell}.yaml"


def resolve_cell(config_arg: str, cell: str, overrides=()) -> dict:
    """Resolved config of `cell`: the run file `config_arg` (S5.yaml), the cell file over it, then overrides."""
    path = cell_path(cell)
    if not path.exists():
        raise C.ConfigError(f"timing cell {cell!r}: {C.to_posix(path)} does not exist")
    run_path = Path(config_arg)
    base = C.load_config(run_path if run_path.is_absolute() else C.repo_root() / run_path)
    layer = C.load_config(path)
    return C.resolve_config(C._deep_merge(copy.deepcopy(base), layer), overrides)


def tau_simulated(cfg: dict) -> float:
    """Simulated time in tau: ramp end plus hold (6.2, CP14); mode N adds the discard before t = 0."""
    tau = cfg["model"]["tau_ms"]
    t_end = make_path(cfg).t_ramp_end + s_to_tau(cfg["durations"]["hold_s"], tau)
    if cfg["run"]["kind"] == "mf_noisy":
        t_end += s_to_tau(cfg["durations"]["discard_s"], tau)
    return float(t_end)


def summarise_repeats(walls) -> dict:
    """Min, median, max and spread of the wall times of the repeats (seconds). Spread = max - min."""
    w = [float(x) for x in walls]
    if not w:
        raise ValueError("no repeats to summarise")
    med = statistics.median(w)
    return {"n": len(w), "min_s": min(w), "median_s": med, "max_s": max(w), "spread_s": max(w) - min(w),
            "spread_rel": (max(w) - min(w)) / med if med > 0 else float("nan"),
            "stdev_s": statistics.stdev(w) if len(w) > 1 else 0.0}


def s_per_tau(wall_s: float, tau: float) -> float:
    """Seconds of wall time per tau simulated."""
    if tau <= 0:
        raise ValueError("tau simulated must be positive")
    return float(wall_s) / float(tau)


def extrapolate(rows, workers: int) -> float:
    """Wall time (s) of a run family: sum of work x cost per unit of work, divided by workers (9.2 step 2).

    rows: (work, cost_per_work) pairs; work is tau simulated with s/tau (mean field) or steps with s/step (Heun).
    Arithmetic only; the families themselves are 3e.
    """
    if workers < 1:
        raise ValueError("workers must be >= 1")
    return sum(float(n) * float(c) for n, c in rows) / workers


def worker_summary(n: int, batches) -> dict:
    """Throughput of N concurrent copies (3d). batches: [{"batch_wall_s", "run_walls_s": [per-copy wall]}], one per repeat.
    Per-run median is over all copies of all batches; throughput = n runs per median batch wall, in runs per hour."""
    if n < 1 or not batches:
        raise ValueError("need n >= 1 and at least one batch")
    runs = [w for b in batches for w in b["run_walls_s"]]
    batch = summarise_repeats([b["batch_wall_s"] for b in batches])
    return {"n": n, "batches": len(batches), "per_run": summarise_repeats(runs), "batch_wall": batch,
            "throughput_runs_per_h": n * 3600.0 / batch["median_s"]}


def parallel_efficiency(throughput_n: float, throughput_1: float, n: int) -> dict:
    """Speed-up and efficiency of N workers against one: speed-up = throughput_n / throughput_1, efficiency = speed-up / n."""
    sp = throughput_n / throughput_1
    return {"speedup": sp, "efficiency": sp / n}


def map_grid(n_delta: int = 30, n_taud: int = 30, delta=(0.01, 0.6), taud_ms=(1.0, 50.0)):
    """Map 1 grid (S7): Delta linear (spacing not stated in the plan, UNVERIFIED), tau_d log. Array (n, 2) of (Delta, tau_d_ms)."""
    import numpy as np
    d = np.linspace(delta[0], delta[1], n_delta)
    t = np.geomspace(taud_ms[0], taud_ms[1], n_taud)
    return np.array([(a, b) for a in d for b in t])


def weighted_family_estimate(measured, grid, workers: int) -> dict:
    """Wall time of a map family from measured cells (DL-100): cost per grid cell is interpolated piecewise linearly
    (Delaunay) in (log Delta, log tau_d) on `measured` = [(Delta, tau_d_ms, s_per_run)]; no extrapolation (a grid cell
    outside the hull of the measured cells raises). Returns total (s, divided by workers), per-run min, mean, max."""
    import numpy as np
    from scipy.interpolate import LinearNDInterpolator
    if workers < 1:
        raise ValueError("workers must be >= 1")
    m = np.asarray(measured, float)
    g = np.asarray(grid, float)
    f = LinearNDInterpolator(np.log(m[:, :2]), m[:, 2])
    c = f(np.log(g))
    if np.isnan(c).any():
        raise ValueError("grid cells outside the hull of the measured cells")
    return {"n_cells": len(g), "total_s": float(c.sum()) / workers, "mean_s_per_run": float(c.mean()),
            "min_s_per_run": float(c.min()), "max_s_per_run": float(c.max())}


def describe_cell(config_arg: str, cell: str) -> dict:
    cfg = resolve_cell(config_arg, cell)
    return {"cell": cell, "kind": cfg["run"]["kind"], "model": cfg["model"]["type"], "solver": cfg["solver"]["method"],
            "rtol": cfg["solver"]["rtol"], "path": cfg["path"]["name"], "T_ramp_s": cfg["path"]["T_ramp_s"],
            "eta_path_status": cfg["path"]["eta_path_status"], "tau_simulated": tau_simulated(cfg),
            "hash12": C.short_hash(C.config_hash(cfg))}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="python -m mprsurge.analysis.timing",
                                 description="print every timing cell with its tau simulated and eta path status")
    ap.add_argument("--config", default="configs/S5.yaml")
    ap.add_argument("--cell", default=None)
    args = ap.parse_args(argv)
    for cell in ([args.cell] if args.cell else CELLS):
        d = describe_cell(args.config, cell)
        print(f"{d['cell']:12s} {d['kind']:9s} {d['model']} {d['solver']:7s} rtol {d['rtol']:g} {d['path']:13s} "
              f"T_ramp {d['T_ramp_s']:g} s  tau simulated {d['tau_simulated']:,.0f}  eta path {d['eta_path_status']}  {d['hash12']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
