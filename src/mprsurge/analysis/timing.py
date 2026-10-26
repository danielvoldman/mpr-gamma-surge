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

CELLS = ("headline", "delta_0.01", "delta_0.6", "delta_0.01_td1", "delta_0.01_td50", "delta_0.6_td1", "delta_0.6_td50", "p5_1000", "radau_1e-12", "radau_1e-12_t10", "radau_1e-10_t10", "mode_n", "m2_ramp", "net_1e3", "net_3e3", "net_1e4", "net_3e4")


def cell_path(cell: str):
    """configs/timing/<cell>.yaml; the MS8 8a, MS9 9a and MS11 11a sample cells live one level down (configs/timing/ms8/, ms9/, ms11/)."""
    p = C.repo_root() / "configs" / "timing" / f"{cell}.yaml"
    for ms in ("ms8", "ms9", "ms11"):
        if not p.exists() and cell.startswith(ms + "_"):
            return C.repo_root() / "configs" / "timing" / ms / f"{cell}.yaml"
    return p


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
    if cfg["run"]["kind"] in ("mf_noisy", "network"):
        t_end += s_to_tau(cfg["durations"]["discard_s"], tau)
    return float(t_end)


def network_updates(cfg: dict) -> float:
    """Neuron-updates of one network run: N x (tau simulated incl. the discard) / dt (9.2 step 2)."""
    return float(cfg["network"]["N"]) * tau_simulated(cfg) / float(cfg["network"]["dt_tau"])


def p2_updates(N: float, T_ramp_s: float, tau_ms: float = 10.0, dt_tau: float = 1e-3, baseline_s: float = 5.0,
               hold_s: float = 10.0, discard_s: float = 2.0, ramp_factor: float = 1.25) -> float:
    """Neuron-updates of one network run on P2 (tests check the 1.25 against make_path): N x tau / dt with
    tau = discard + baseline + 1.25 T_ramp + hold, in seconds converted at tau_ms."""
    return float(N) * s_to_tau(discard_s + baseline_s + ramp_factor * T_ramp_s + hold_s, tau_ms) / dt_tau

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


# ---- 3e: run families, extrapolation and the launch rule (plan 9.2 steps 2 and 3) ----

def families_path() -> Path:
    return C.repo_root() / "configs" / "timing_families.yaml"


def load_families(path=None) -> dict:
    import yaml
    with open(path or families_path(), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def part_cells(part: dict) -> list:
    """Every timing cell a part reads (a name, a list of names, the map-1 corners, or the cells of net_p2 runs)."""
    out = []
    for c in [part.get("cell"), *[r["cell"] for r in part.get("runs", [])], *part.get("corners", {}).values()]:
        if c is not None:
            out += [c] if isinstance(c, str) else list(c)
    return out


def _update_cost(cells: dict, name: str) -> float:
    """Wall seconds per neuron-update of a network timing cell; KeyError (no cell) if the count is missing."""
    c = cells[name]
    if not c.get("updates"):
        raise KeyError(f"{name}: no neuron-update count")
    return c["wall_s"] / c["updates"]


def part_seconds(part: dict, cells: dict, divisor: float) -> float:
    """Wall time (s) of one part of a row. cells: {cell: {"wall_s", "tau", "steps"}} (per-run walls, tau simulated, solver steps).
    A part whose cell is missing raises KeyError: callers report "no timing cell", never a silent prediction."""
    kind = part["kind"]
    if kind == "mf_tau":
        c = cells[part["cell"]]
        return extrapolate([(part["tau"], s_per_tau(c["wall_s"], c["tau"]))], divisor)
    if kind == "heun":
        c = cells[part["cell"]]
        if not c.get("steps"):
            raise KeyError(f"{part['cell']}: no solver step count")
        return extrapolate([(part["steps"], c["wall_s"] / c["steps"])], divisor)
    if kind == "runs":
        return extrapolate([(part["n"], cells[part["cell"]]["wall_s"])], divisor)
    if kind == "net_p2":
        # runs: [{n, N, T_ramp_s, cell}]; cell is a name or a list of names (the slowest per-update rate is used)
        total = 0.0
        for r in part["runs"]:
            names = [r["cell"]] if isinstance(r["cell"], str) else list(r["cell"])
            rate = max(_update_cost(cells, nm) for nm in names)
            total += r["n"] * p2_updates(r["N"], r["T_ramp_s"]) * rate
        return total / divisor
    if kind == "net":
        # updates: neuron-updates counted directly, for runs that are not on P2 (S3 step, sigma baseline)
        names = [part["cell"]] if isinstance(part["cell"], str) else list(part["cell"])
        return extrapolate([(part["updates"], max(_update_cost(cells, nm) for nm in names))], divisor)
    if kind == "map1":
        measured = []
        for key, cell in part["corners"].items():
            d, t = (float(x) for x in key.split(","))
            measured.append((d, t, cells[cell]["wall_s"]))
        return weighted_family_estimate(measured, map_grid(), divisor)["total_s"]
    raise ValueError(f"unknown part kind {kind!r}")


def evaluate_rows(spec: dict, cells: dict, divisor: float, alone: dict | None = None) -> list:
    """Per-row prediction and launch verdict. The rule is prediction <= rule_factor x allowance (plan 9.2 step 3).
    'single' parts are judged alone (DL-103 (2)) from `alone` (default `cells`). A missing cell gives verdict
    "no timing cell". A row with partial: true is a lower bound, so its verdict carries "(partial)"."""
    factor = float(spec.get("rule_factor", 1.5))
    alone = cells if alone is None else alone
    out = []
    for row in spec["rows"]:
        allow = float(row["allowance_s"]) if "allowance_s" in row else float(row["allowance_h"]) * 3600.0
        limit = factor * allow
        res = {"id": row["id"], "s_ids": row.get("s_ids", []), "allowance_s": allow, "limit_s": limit,
               "partial": bool(row.get("partial")), "missing": row.get("missing", []), "parts": []}
        try:
            for part in row["parts"]:
                if part["kind"] == "single":
                    wall = alone[part["cell"]]["wall_s"]
                    res["parts"].append({"label": part["label"], "seconds": wall, "single": True,
                                         "verdict": "PASS" if wall <= limit else "FAIL"})
                else:
                    res["parts"].append({"label": part["label"], "seconds": part_seconds(part, cells, divisor)})
        except KeyError as e:
            res.update(prediction_s=None, verdict=f"no timing cell ({e.args[0]})")
            out.append(res)
            continue
        if any(p.get("single") for p in res["parts"]):
            res["prediction_s"] = max(p["seconds"] for p in res["parts"])
            res["verdict"] = "FAIL" if any(p["verdict"] == "FAIL" for p in res["parts"]) else "PASS"
        else:
            res["prediction_s"] = sum(p["seconds"] for p in res["parts"])
            res["verdict"] = "PASS" if res["prediction_s"] <= limit else "FAIL"
        if res["partial"]:
            res["verdict"] += " (partial)"
        out.append(res)
    return out


def total_verdict(spec: dict, rows: list) -> dict:
    """D36 cap. Rows with `in_total: false` (the single-run row, the duplicate headline-rate sweeps row) are left out.
    Lower bound = sum of the predictions. Conservative = the same with each partial row taken at max(prediction,
    Table 9.1 allowance), the allowance standing in for the run families without a count or cell. judged is True only
    when every row has a prediction and none is partial or lacks a cell; otherwise the cap is read off the bounds."""
    ids = {r["id"] for r in spec["rows"] if r.get("in_total", True)}
    used = [r for r in rows if r["id"] in ids]
    gaps = [r["id"] for r in used if r["prediction_s"] is None or r["partial"]]
    gaps += list(spec.get("no_cell", []))
    cap = float(spec["workers_cap_h"])
    low = sum(r["prediction_s"] or 0.0 for r in used) / 3600.0
    cons = sum(max(r["prediction_s"] or 0.0, r["allowance_s"]) if (r["partial"] or r["prediction_s"] is None) else r["prediction_s"]
               for r in used) / 3600.0
    out = {"judged": not gaps, "gaps": gaps, "total_h": low, "lower_bound_h": low, "conservative_h": cons, "cap_h": cap,
           "rows_in_total": sorted(ids)}
    out["pass"] = (low if not gaps else cons) <= cap
    out["fails_on_lower_bound"] = low > cap
    return out


def load_cells(results_dir, cells, workers=None, steps_dir=None) -> dict:
    """Per-cell walls from timing json. workers=None: <dir>/<cell>.json (median of the repeats, alone). workers=N:
    <dir>/<cell>/workers_N.json, per-run median pooled over all copies of all batches (DL-102). Solver steps come from
    <steps_dir>/<cell>.json (a count, independent of load). Cells without a file are left out."""
    import json
    out = {}
    for cell in cells:
        base = Path(results_dir)
        p = base / f"{cell}.json" if workers is None else base / cell / f"workers_{workers}.json"
        if not p.exists():
            continue
        t = json.loads(p.read_text(encoding="utf-8"))["timing"]
        if t.get("status") != "ok":
            continue
        wall = t["summary"]["median_s"] if workers is None else t["summary"]["per_run"]["median_s"]
        steps = None
        sp = Path(steps_dir or results_dir) / f"{cell}.json"
        if sp.exists():
            steps = json.loads(sp.read_text(encoding="utf-8"))["timing"].get("solver_count")
        out[cell] = {"wall_s": float(wall), "tau": float(t["tau_simulated"]), "steps": steps, "updates": t.get("updates")}
    return out


def format_report(rows: list, total: dict, label: str, divisor: float) -> str:
    def fmt(s):
        return "-" if s is None else (f"{s:.1f} s" if s < 600 else f"{s / 3600:.2f} h")
    lines = [f"Prediction ({label}); divisor {divisor:.2f}; launch rule: prediction <= 1.5 x Table 9.1 allowance", ""]
    for r in rows:
        ids = "/".join(r["s_ids"]) or "-"
        lines.append(f"{r['id']:22s} {ids:10s} prediction {fmt(r['prediction_s']):>9s}  allowance {fmt(r['allowance_s']):>9s}  "
                     f"limit {fmt(r['limit_s']):>9s}  {r['verdict']}")
        for p in r["parts"]:
            lines.append(f"    {p['label']:40s} {fmt(p['seconds']):>9s}" + (f"  {p['verdict']}" if "verdict" in p else ""))
        if r["partial"]:
            lines.append(f"    not extrapolated (no count or cell): {', '.join(r['missing'])}")
    lines.append("")
    if total["judged"]:
        lines.append(f"Total {total['total_h']:.2f} h against the D36 cap {total['cap_h']:g} h: {'PASS' if total['pass'] else 'FAIL'}")
    else:
        lines.append(f"Total, rows with counts only (lower bound): {total['lower_bound_h']:.2f} h; with each partial row at max(prediction, "
                     f"Table 9.1 allowance) (conservative): {total['conservative_h']:.2f} h; D36 cap {total['cap_h']:g} h.")
        lines.append("D36: " + ("FAIL on the lower bound" if total["fails_on_lower_bound"] else
                                ("PASS on the conservative figure" if total["pass"] else "lower bound within the cap, conservative figure above it")))
        lines.append("Rows partial or without a cell, or run families with no cell: " + ", ".join(total["gaps"]))
    return "\n".join(lines)


def predict_main(args) -> int:
    spec = load_families()
    names = sorted({c for r in spec["rows"] for p in r["parts"] for c in part_cells(p)})
    root = C.repo_root()
    alone_dir = root / (args.alone_dir or args.results_dir)
    cells = load_cells(root / args.results_dir, names, args.workers, alone_dir)
    alone = load_cells(alone_dir, names) if args.workers else cells
    counts = load_cells(root / "results" / "timing", names)      # solver step counts do not depend on load or session
    for cell, c in cells.items():
        if not c["steps"] and cell in counts:
            c["steps"] = counts[cell]["steps"]
    divisor = float(args.workers) if args.workers else args.speedup
    rows = evaluate_rows(spec, cells, divisor, alone)
    text = format_report(rows, total_verdict(spec, rows),
                         f"{args.results_dir}, " + (f"{args.workers} concurrent copies" if args.workers else "alone"), divisor)
    print(text)
    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    return 0


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
    ap.add_argument("--predict", action="store_true", help="3e: print and write the per-family prediction and launch verdict")
    ap.add_argument("--results-dir", default="results/timing", help="--predict: where the cell json are")
    ap.add_argument("--workers", type=int, default=None,
                    help="--predict: use <results-dir>/<cell>/workers_N.json (per-run median under N copies), divide by N; "
                         "default: alone values divided by --speedup")
    ap.add_argument("--speedup", type=float, default=1.0, help="--predict, alone basis: divisor (measured speed-up)")
    ap.add_argument("--alone-dir", default=None, help="--predict: dir with the alone cells (single-run row, step counts)")
    ap.add_argument("--out", default="results/timing/prediction.txt")
    args = ap.parse_args(argv)
    if args.predict:
        return predict_main(args)
    for cell in ([args.cell] if args.cell else CELLS):
        d = describe_cell(args.config, cell)
        print(f"{d['cell']:12s} {d['kind']:9s} {d['model']} {d['solver']:7s} rtol {d['rtol']:g} {d['path']:13s} "
              f"T_ramp {d['T_ramp_s']:g} s  tau simulated {d['tau_simulated']:,.0f}  eta path {d['eta_path_status']}  {d['hash12']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
