"""MS8 launcher (8c): run a whole MS8 list (S5 or S13) through ONE worker pool (DL-173).

Drivers only integrate: this script expands every config of the list with run.build_plan (so the frozen-criteria gate and the
seed-key rules apply), pools all cells, orders them longest first (M-12, DL-103 (1)) and hands them to run.run_jobs. One
invocation per config would put a barrier at the end of each config and break the 9.2 arithmetic (DL-172), which assumes one pool.
Per-cell outputs, names, hashes and records are those of `python -m mprsurge.run`; a restart skips complete runs.

  python scripts/run_ms8_list.py --list S5 --workers 10 --longest-first \
      --set configs/S5_ramp.yaml:output.dir=results/S5/ramp [--only p2_noise] [--limit-per-config 1] [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import ms8_runlist as RL


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="run_ms8_list")
    ap.add_argument("--list", required=True, choices=sorted(RL.LISTS))
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--longest-first", action="store_true")
    ap.add_argument("--set", dest="sets", action="append", default=[], metavar="CONFIG:section.key=value",
                    help="override for one config of the list (e.g. configs/S5_ramp.yaml:output.dir=results/S5/ramp)")
    ap.add_argument("--only", action="append", default=[], metavar="RUN_ID", help="smoke test: only configs with this run id")
    ap.add_argument("--cells", default=None, metavar="I,J,..", help="smoke test: only cells with these indices (within each selected config)")
    ap.add_argument("--journal-dir", default="results/ms8/launch", help="manifest.csv and run.log of the pooled launch")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    per_config: dict[str, list[str]] = {}
    for item in args.sets:
        cfg_path, _, ov = item.partition(":")
        per_config.setdefault(cfg_path, []).append(ov)
    keep = None if args.cells is None else {int(x) for x in args.cells.split(",")}

    jobs: list[dict] = []
    env = P.environment_info()
    for config, _family in RL.LISTS[args.list]:
        plan = R.build_plan(config, per_config.get(config, []), args.workers)
        if args.only and plan.family not in args.only:
            continue
        for j in R.jobs_for(plan, env, args.dry_run):
            if keep is None or j["index"] in keep:
                jobs.append(j)
    if not jobs:
        print("no jobs selected", file=sys.stderr)
        return 2
    if args.longest_first:
        jobs = R.longest_first(jobs)
    journal = Path(args.journal_dir)
    journal = journal if journal.is_absolute() else C.repo_root() / journal
    handlers = R._setup_logging(None if args.dry_run else journal)
    log = R.logging.getLogger(R.LOG_NAME)
    try:
        log.info("%s: %d cells from %d configs, workers %d%s", args.list, len(jobs), len({j["out_dir"] for j in jobs}),
                 args.workers, " (dry-run)" if args.dry_run else "")
        if not args.dry_run:
            for task in sorted({j["task"] for j in jobs}):
                getattr(R.importlib.import_module(task.partition(":")[0]), "warm_up", lambda: None)()
        t0 = time.monotonic()
        results = R.run_jobs(jobs, args.workers, journal, journal=not args.dry_run, handlers=handlers)
        counts: dict[str, int] = {}
        for r in results:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        log.info("finished: %s, wall %.1f s", ", ".join(f"{v} {k}" for k, v in sorted(counts.items())), time.monotonic() - t0)
        return 1 if counts.get("failed") or counts.get("timeout") else 0
    finally:
        R.logging.getLogger(R.LOG_NAME).handlers.clear()
        for h in handlers:
            h.close()


if __name__ == "__main__":  # required on Windows: workers are spawned
    sys.exit(main())
