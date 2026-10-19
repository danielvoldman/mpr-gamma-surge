"""MS9 9b: time the classifier and the A9 labelling on stored records and extrapolate to all 3,618 runs at 10 workers (DL-216). UNVERIFIED.

Analysis only (nothing is integrated). Inputs are stored records of earlier steps: one map-1 cell (mode D, P2, T_ramp 120 s, 165,001
samples; default results/timing/ms9b/map1/m1_14_12_*.json) and one mode-N record (default: the supplementary NC1 mode-N run nearest 100 s;
a different path and 117 s long, so its time is scaled by the number of samples to the 167 s subgrid run). Measured: file load; classify_mode_d;
classify_mode_n; the A9 labelling of the map cell cold (A4 tables built for its column and row) and warm (tables cached); the cost of one
A4 Hopf scan; the number of distinct Hopf scans the A9 tables need over map 1 and map 2.
Extrapolation: classifications of the 1,367 mode-D runs and 2,251 mode-N runs (2,250 subgrid + the network run) at the measured costs,
A9 labels for the 1,225 map cells at the warm cost, plus the one-off Hopf tables; sum of CPU seconds divided by 10 workers (the tables are
built once, not divided).

  .venv/Scripts/python.exe scripts/time_ms9_analysis.py [--map-record JSON] [--noisy-record JSON] [--repeat 3]
"""
import argparse
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np

from mprsurge import config as C
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import a9
from mprsurge.analysis import ms9_classify as MCL
from mprsurge.analysis import ms9_runlist as RL

N_MODE_D, N_MODE_N, N_CELLS = 3618 - 2250 - 1, 2250 + 1, 900 + 325


def med(f, n):
    ts = []
    for _ in range(n):
        t = time.perf_counter()
        f()
        ts.append(time.perf_counter() - t)
    return statistics.median(ts)


def distinct_hopf_scans() -> int:
    """(J0, Delta, tau_d) combinations the A9 rules (a), (b), (c) need over map 1 and map 2 (Delta axis and tau_d axis of map 1)."""
    cells = RL.load_cells()
    d_axis = sorted({c["Delta"] for c in cells if c["kind"] == "map1"})
    t_axis = sorted({c["tau_d_ms"] for c in cells if c["kind"] == "map1"})
    keys = set()
    for c in cells[1:]:
        keys.add((c["J0"], c["Delta"], c["tau_d_ms"]))
        keys.update((c["J0"], d, c["tau_d_ms"]) for d in d_axis)
        keys.update((c["J0"], c["Delta"], t) for t in t_axis)
    return len(keys)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="time_ms9_analysis")
    ap.add_argument("--map-record", default=None)
    ap.add_argument("--noisy-record", default=None)
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--out", default="results/timing/ms9b/analysis_timing.json")
    args = ap.parse_args(argv)
    root = C.repo_root()
    fi, _ = A7.frozen_inputs()
    mrec = Path(args.map_record) if args.map_record else sorted((root / "results/timing/ms9b/map1").glob("m1_14_12_*.json"))[0]
    rec = json.loads(mrec.read_text(encoding="utf-8"))
    cfg = rec["config"]
    out = {"map_record": str(mrec), "map_git_dirty": rec["git"]["dirty"]}
    v = np.load(mrec.with_suffix(".npz"))["v"]
    out["map_samples"] = int(v.size)
    out["load_s"] = med(lambda: np.load(mrec.with_suffix(".npz"))["v"], args.repeat)
    p = cfg["path"]
    out["classify_mode_d_s"] = med(lambda: MCL.classify_array("D", v, 1000.0, p["t_on_s"], p["T_ramp_s"], fi["threshold"], True), args.repeat)
    res, _ = MCL.classify_array("D", v, 1000.0, p["t_on_s"], p["T_ramp_s"], fi["threshold"], True)
    out["class_of_map_record"] = res.cls
    cells = RL.load_cells()
    d_axis = sorted({c["Delta"] for c in cells if c["kind"] == "map1"})
    t_axis = sorted({c["tau_d_ms"] for c in cells if c["kind"] == "map1"})
    h = fi["grid_step"]
    t = time.perf_counter()
    lab = a9.label_cell(cfg, res.cls, res.label_f, d_axis, t_axis, h)
    out["a9_cold_s"] = time.perf_counter() - t
    out["a9_warm_s"] = med(lambda: a9.label_cell(cfg, res.cls, res.label_f, d_axis, t_axis, h), args.repeat)
    out["a9_labels"] = lab
    ts = []
    for k in range(10):
        t = time.perf_counter()
        a9.hopf_point(-21.0, 0.011 + 0.0123 * k, 2.1 + 0.37 * k)
        ts.append(time.perf_counter() - t)
    out["hopf_scan_s"] = statistics.median(ts)
    out["distinct_hopf_scans"] = distinct_hopf_scans()
    out["hopf_tables_s"] = out["distinct_hopf_scans"] * out["hopf_scan_s"]
    nrec = Path(args.noisy_record) if args.noisy_record else None
    if nrec is None:
        c = [q for q in sorted((root / "results/S12/supp").rglob("NC1_modeN_*.json")) if not q.name.endswith(".dry.json")]
        nrec = min(c, key=lambda q: abs(json.loads(q.read_text(encoding="utf-8"))["config"]["path"]["T_ramp_s"] - 100.0)) if c else None
    if nrec is not None:
        ncfg = json.loads(nrec.read_text(encoding="utf-8"))["config"]
        vn = np.load(nrec.with_suffix(".npz"))["v"]
        pn = ncfg["path"]
        out["noisy_record"], out["noisy_samples"], out["noisy_T_ramp_s"] = str(nrec), int(vn.size), pn["T_ramp_s"]
        out["classify_mode_n_s"] = med(lambda: MCL.classify_array("N", vn, 1000.0, pn["t_on_s"], pn["T_ramp_s"], fi["threshold"]), args.repeat)
        out["classify_mode_n_scaled_to_167s_s"] = out["classify_mode_n_s"] * 167001.0 / vn.size
    cd = out["classify_mode_d_s"] + out["load_s"]
    cn = out.get("classify_mode_n_scaled_to_167s_s")
    cpu = N_MODE_D * cd + (N_MODE_N * (cn + out["load_s"]) if cn is not None else 0.0) + N_CELLS * out["a9_warm_s"]
    out["extrapolation"] = {"n_mode_d": N_MODE_D, "n_mode_n": N_MODE_N, "n_a9_cells": N_CELLS, "cpu_s": cpu, "pooled_10_workers_s": cpu / 10.0,
                            "hopf_tables_once_s": out["hopf_tables_s"], "total_s": cpu / 10.0 + out["hopf_tables_s"],
                            "mode_n_measured": cn is not None, "label": "UNVERIFIED: one record per kind, extrapolated linearly"}
    o = Path(args.out)
    o = o if o.is_absolute() else root / o
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    for k, v_ in out.items():
        print(f"{k}: {v_}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
