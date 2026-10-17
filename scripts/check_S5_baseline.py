"""Verify the S5 baseline-only run (MS7 7e, DL-142). Reads results/S5/baseline/ and checks only; integrates nothing.

Checks: record count and status per cell (failed / missing listed, never read as NS), git.dirty false in every record,
seed spawn keys [7, 4, s] for s = 0..n-1 and the seed count, the start state (r, v) against cell_list.json (the 7d list),
the cell-list SHA-256 against the one in the record inputs, bit-identity of the 13 T_ramp duplicates of each map-2 J0
(v, r, y_start), and per cell the stationarity of the kept baseline (reported, not judged). Exit 1 on any hard mismatch.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P

EXPECT_HASH = "8e67bbd2b366e86ffee59e732dd79824bdce82c73c477436cb3b1689b0a328d9"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", default="results/S5/baseline")
    args = ap.parse_args(argv)
    d = C.repo_root() / args.dir
    doc = json.loads((d / "cell_list.json").read_text(encoding="utf-8"))
    cells = doc["cells"]
    n_seeds = 10
    if doc["summary"]["cell_list_sha256"] != EXPECT_HASH or len(cells) != 1226:
        print(f"PROBLEM cell-list hash {doc['summary']['cell_list_sha256']} or count {len(cells)} differs from DL-141")
        return 1
    problems, status_count = [], {}
    n_records = n_dirty = n_runs = 0
    stat = []                      # per cell: max over seeds of |first-half mean - second-half mean| / std, and |mean - fixed point| / std
    by_j0 = {}
    for c in cells:
        name = f"S5base_{c['index']:04d}_{c['hash12']}"
        rp = d / f"{name}.json"
        if not rp.exists():
            status_count["missing"] = status_count.get("missing", 0) + 1
            problems.append(f"{name}: no record")
            continue
        rec = json.loads(rp.read_text(encoding="utf-8"))
        n_records += 1
        status_count[rec["status"]] = status_count.get(rec["status"], 0) + 1
        if rec["status"] != "ok":
            problems.append(f"{name}: status {rec['status']}: {rec['message']}")
            continue
        if rec["git"]["dirty"] is not False:
            n_dirty += 1
            problems.append(f"{name}: git.dirty = {rec['git']['dirty']}")
        fl = rec["flags"]
        if fl["seed_spawn_keys"] != [[7, 4, s] for s in range(n_seeds)] or fl["n_seeds"] != n_seeds:
            problems.append(f"{name}: seed spawn keys {fl['seed_spawn_keys']}")
        if rec["inputs"].get("configs/S5_cells.yaml") != doc["spec_sha256"]:
            problems.append(f"{name}: cell-spec hash differs from the cell list")
        z = np.load(d / f"{name}.npz")
        v, r, ys = z["v"], z["r"], z["y_start"]
        if v.shape != (n_seeds, 5001) or r.shape != v.shape:
            problems.append(f"{name}: array shape {v.shape}")
            continue
        n_runs += v.shape[0]
        st = c["start"]
        if not (np.isclose(ys[0], st["r"], rtol=1e-9, atol=0) and np.isclose(ys[1], st["v"], rtol=1e-9, atol=0)):
            problems.append(f"{name}: start state {ys[:2]} differs from the 7d list ({st['r']}, {st['v']})")
        h = v.shape[1] // 2
        sd = v.std(axis=1, ddof=1)
        stat.append((c["index"], float(np.max(np.abs(v[:, :h].mean(1) - v[:, h:].mean(1)) / sd)),
                     float(np.max(np.abs(v.mean(1) - ys[1]) / sd))))
        if c["kind"] == "map2":
            by_j0.setdefault(c["J0"], []).append((name, v, r, ys))
    dup_bad = 0
    for j0, g in sorted(by_j0.items()):
        ref = g[0]
        for nm, v, r, ys in g[1:]:
            if not (np.array_equal(v, ref[1]) and np.array_equal(r, ref[2]) and np.array_equal(ys, ref[3])):
                dup_bad += 1
                problems.append(f"duplicate mismatch at J0 {j0}: {nm} vs {ref[0]}")
    print(f"cells in list {len(cells)}; records {n_records}; status {status_count}; ok runs (cell x seed) {n_runs}")
    print(f"dirty records {n_dirty}; map-2 J0 groups {len(by_j0)} (sizes {sorted({len(g) for g in by_j0.values()})}); "
          f"duplicate mismatches {dup_bad}")
    sha = P.sha256_file(d / "cell_list.json")
    print(f"cell_list.json sha256 {sha[:12]}; spec sha256 {doc['spec_sha256'][:12]}; summary {doc['summary'].get('cell_list_sha256', '?')}")
    if stat:
        a = np.array([s[1:] for s in stat])
        print("stationarity (report only): half-mean difference / std per seed, max over seeds: "
              f"median over cells {np.median(a[:, 0]):.3f}, max {a[:, 0].max():.3f} (cell {stat[int(a[:, 0].argmax())][0]}); "
              f"|mean - fixed point| / std: median {np.median(a[:, 1]):.3f}, max {a[:, 1].max():.3f} "
              f"(cell {stat[int(a[:, 1].argmax())][0]})")
    for p in problems[:40]:
        print("PROBLEM", p)
    print(f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
