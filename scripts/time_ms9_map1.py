"""MS9 9b: re-time map 1 on a clean tree (DL-216). One batch of 10 concurrent map-1 cells, each timed on its own (integration call only):
the 3 x 3 stratified sample (Delta index {0, 15, 29} x tau_d index {0, 15, 29}) plus the cell nearest the headline (14, 12), P2 at
T_ramp 120 s, mode D, DOP853 rtol 1e-10, the configs of the committed run list S7_map1. The records and npz files are written after the
timer stops (outside the timed region) to results/timing/ms9b/map1/ (git-ignored); they are timing-only cells, not map results.

Refuses to run on a dirty tree: every record must show git.dirty = false (the 9a records did not). Then prints the predictions
(analysis.ms9_retime). Drivers only integrate; the arithmetic is in the analysis module.

  .venv/Scripts/python.exe scripts/time_ms9_map1.py [--workers 10] [--out-dir results/timing/ms9b/map1]
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
from pathlib import Path

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import timing_run as TR
from mprsurge.analysis import ms9_retime as RT
from mprsurge.analysis import ms9_runlist as RL

from time_one_run import machine_state


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="time_ms9_map1")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--out-dir", default="results/timing/ms9b/map1")
    ap.add_argument("--limit-s", type=float, default=3600.0)
    args = ap.parse_args(argv)
    env = P.environment_info()
    if env["git"]["dirty"] is not False:
        print(f"git tree is not clean (dirty = {env['git']['dirty']}): commit first", file=sys.stderr)
        return 3
    cells = RT.sample_cells()
    if len(cells) != args.workers:
        print(f"{len(cells)} sample cells for {args.workers} workers: the batch needs one worker per cell", file=sys.stderr)
        return 2
    rows = {r["index"]: r for r in RL.expand("S7_map1")}
    out = Path(args.out_dir)
    out = out if out.is_absolute() else C.repo_root() / out
    out.mkdir(parents=True, exist_ok=True)
    jobs = []
    for (i, j) in cells:
        r = rows[i * RL.MAP1_N + j]
        jobs.append({"cfg": r["cfg"], "name": f"{RT.label(i, j)}_{C.short_hash(r['hash'])}", "label": RT.label(i, j), "env": env,
                     "inputs": r["inputs"], "out_dir": str(out)})
    before = machine_state()
    print(f"batch of {len(jobs)} distinct map-1 cells, git {env['git']['commit'][:8]} dirty {env['git']['dirty']}", flush=True)
    batch = TR.run_distinct_batch(jobs, args.limit_s)
    after = machine_state()
    (out / "batch.json").write_text(json.dumps({"git": env["git"], "batch": batch, "machine_state": {"before": before, "after": after}},
                                               indent=1, default=str), encoding="utf-8")
    for c in batch["copies"]:
        print(f"  {c['label']}: {c['status']} {c['wall_s']:.1f} s dirty {c.get('git_dirty')}", flush=True)
    print(f"batch wall {batch['batch_wall_s']:.1f} s, start spread {batch['start_spread_s']:.2f} s, pids {batch['distinct_pids']}, status {batch['status']}")
    if batch["status"] != "ok":
        return 1
    walls, info = RT.load_walls(out)
    print(RT.report(walls, info, args.workers))
    return 0


if __name__ == "__main__":
    sys.exit(main())
