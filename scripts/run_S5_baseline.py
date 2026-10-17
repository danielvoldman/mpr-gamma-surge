"""S5 baseline-only driver (MS7 7d, DL-141; plan Table 6.2 S5): builds the cell list (analysis.cells, grids in
configs/S5_cells.yaml), resolves one run config per cell from configs/S5_baseline.yaml and runs the selected cells through
the runner (one task per cell, 10 seeds, one npz and one record per cell) into results/S5/baseline/.

  --dry-run          write results/S5/baseline/cell_list.json and cell_list.csv, resolve and hash every selected cell, print the
                     counts, start states and stability; integrate nothing, write no run record.
  --cells headline   (default) the headline cell only.   --cells all   every cell.   --cells 0,5,17   by list index.
  --workers N        spawn pool size (default 1).
  --out-dir DIR      write bundles, records and the cell list here instead of the config output.dir (7e timing sample, DL-142;
                     the run hash does not cover the output directory).
  A rerun skips cells whose record is complete (resumable); a cell that raises is recorded with status "failed".
"""
import argparse
import csv
import json
import logging
import sys
import time
from pathlib import Path

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge import simulate_mf as SM
from mprsurge.analysis import cells as CL

CONFIG = "configs/S5_baseline.yaml"


def select(cells: list[dict], arg: str) -> list[dict]:
    if arg == "headline":
        return cells[:1]
    if arg == "all":
        return cells
    return [cells[int(i)] for i in arg.split(",")]


def cell_config(cell: dict) -> dict:
    return C.resolve_config(CONFIG, CL.overrides(cell))


def write_cell_list(cells: list[dict], out_dir: Path, hashes: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = {"summary": CL.summary(cells), "spec_sha256": P.sha256_file(C.repo_root() / CL.CELLS_FILE),
           "config": CONFIG, "cells": [{**c, "hash12": hashes.get(c["index"])} for c in cells]}
    P.atomic_write_json(out_dir / "cell_list.json", doc)
    cols = ["index", "name", "kind", "J0", "Delta", "tau_d_ms", "T_ramp_s", "hopf_found", "eta_H", "eta_start", "eta_peak",
            "start_type", "start_stable", "start_re_max", "start_r", "start_v", "hash12"]
    with open(out_dir / "cell_list.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for c in doc["cells"]:
            st = c["start"]
            w.writerow([c["index"], c["name"], c["kind"], c["J0"], c["Delta"], c["tau_d_ms"], c["T_ramp_s"], c["hopf_found"],
                        c["eta_H"], c["eta_start"], c["eta_peak"], st["type"], st["stable"], st["re_max"], st["r"], st["v"],
                        c["hash12"]])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cells", default="headline")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    t0 = time.monotonic()
    cells = CL.build_cells()
    chosen = select(cells, args.cells)
    cfgs = {c["index"]: cell_config(c) for c in chosen}
    hashes = {i: C.short_hash(C.config_hash(cfg)) for i, cfg in cfgs.items()}
    out_dir = C.repo_root() / (args.out_dir or cfgs[chosen[0]["index"]]["output"]["dir"])
    write_cell_list(cells, out_dir, hashes)
    print(json.dumps(CL.summary(cells), indent=1))
    print(f"cell list {time.monotonic() - t0:.1f} s; selected {len(chosen)} cells")
    if args.dry_run:
        return 0
    env = P.environment_info()
    base = C.to_posix(C.repo_root() / CONFIG)
    inputs = {"configs/base.yaml": P.sha256_file(C.repo_root() / "configs/base.yaml"),
              base: P.sha256_file(C.repo_root() / CONFIG),
              CL.CELLS_FILE: P.sha256_file(C.repo_root() / CL.CELLS_FILE)}
    jobs = []
    for c in chosen:
        cfg = cfgs[c["index"]]
        cfg["sweep"] = {k: None for k in cfg["sweep"]}
        h12 = hashes[c["index"]]
        jobs.append({"index": c["index"], "name": f"S5base_{c['index']:04d}_{h12}", "hash12": h12, "cfg": cfg,
                     "out_dir": str(out_dir), "task": R.TASKS["s5base"], "env": env, "inputs": inputs, "dry_run": False})
    handlers = R._setup_logging(out_dir)
    try:
        SM.warm_up()
        results = R.run_jobs(jobs, args.workers, out_dir, handlers=handlers)
    finally:
        logging.getLogger(R.LOG_NAME).handlers.clear()
        for h in handlers:
            h.close()
    bad = [r for r in results if r["status"] not in ("ok", "skipped")]
    wall = time.monotonic() - t0
    print(f"{len(results)} cells, {len(bad)} not ok, wall {wall:.1f} s, git.dirty={env['git']['dirty']}")
    for r in results[:3]:
        print(f"  {r['name']} {r['status']} {r['wall_time_s']:.2f} s {r['message']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
