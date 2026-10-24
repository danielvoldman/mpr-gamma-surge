"""MS10 launcher (10c, DRAFT): run one or more MS10 lists through ONE worker pool (same pattern as scripts/run_ms9_list.py, DL-173).

Drivers only integrate: the lists come from mprsurge.analysis.ms10_runlist (configs/ms10/ + overrides; the frozen-criteria gate applies), jobs are
ordered longest first (network runs by their update count, the mean-field runs by the runner's estimate) and handed to run.run_jobs. Per-run outputs,
names, hashes and records are those of `python -m mprsurge.run`; a restart skips complete runs (find_complete), so a killed launch is resumed by running
the same command again. Each invocation has its own journal (manifest.csv, run.log).

  python scripts/run_ms10_list.py --list S10 --list C2_S10 --workers 10 --journal-dir results/ms10/launch_s10 [--dry-run]

--dry-run is LIST ONLY: it builds the lists, prints the run count and the list SHA-256 of each (or UNRESOLVED while the S8 cells are TO_BE_CHOSEN) and
the longest-first head, and exits; no job is built for the pool and nothing is written. A real launch is refused while any MS10 data file says status
DRAFT, on a dirty git tree, and while any cell is TO_BE_CHOSEN. The reviewer launches; Claude Code does not.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import ms10_runlist as RL
from mprsurge.analysis import timing as T

S_PER_NETWORK_UPDATE = 2.03e-9           # 9a sample under 10 copies (DL-211), used only to order jobs


def job_cost_s(cfg: dict) -> float:
    if cfg["run"]["kind"] == "network":
        return T.network_updates(cfg) * S_PER_NETWORK_UPDATE
    return R.estimated_cost_s(cfg)


def build_jobs(lists, dry_run=False) -> list[dict]:
    env = P.environment_info()
    jobs: list[dict] = []
    for name in lists:
        for r in RL.expand(name):
            jobs.append({"index": len(jobs), "list": name, "name": r["name"], "hash12": C.short_hash(r["hash"]), "cfg": r["cfg"],
                         "out_dir": str(C.repo_root() / r["out_dir"]), "task": R.TASKS[r["kind"]], "env": env, "inputs": r["inputs"],
                         "dry_run": dry_run})
    return jobs


def list_only(lists) -> int:
    """Dry run: counts and list SHA-256 for each selected list, nothing built for the pool."""
    summ = RL.summary(tuple(lists))
    for name, v in summ.items():
        sha = v["sha256"] if v["sha256"] else f"UNRESOLVED ({RL.PLACEHOLDER})"
        print(f"{name:13s} {v['runs']:4d} runs  list SHA-256 {sha}  families {v['by_family']}")
    print(f"total {sum(v['runs'] for v in summ.values())} runs; status {RL.status()}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="run_ms10_list")
    ap.add_argument("--list", dest="lists", action="append", required=True, choices=RL.ALL_LISTS)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--journal-dir", default=None, help="manifest.csv and run.log of this launch (required unless --dry-run)")
    ap.add_argument("--dry-run", action="store_true", help="list only: counts and list SHA-256, no simulation, nothing written")
    args = ap.parse_args(argv)
    if args.dry_run:
        return list_only(args.lists)
    if not args.journal_dir:
        print("--journal-dir is required for a launch", file=sys.stderr)
        return 2
    if RL.is_draft():
        print(f"the MS10 data files are DRAFT (not frozen): {RL.status()}", file=sys.stderr)
        return 4
    if P.environment_info(with_julia=False)["git"].get("dirty"):
        print("git tree is dirty: commit first (records must show dirty = false)", file=sys.stderr)
        return 3
    jobs = build_jobs(args.lists)                      # raises RunListError while a cell is TO_BE_CHOSEN
    if not jobs:
        print("no jobs selected", file=sys.stderr)
        return 2
    jobs.sort(key=lambda j: -job_cost_s(j["cfg"]))             # stable: ties keep list order
    for k, j in enumerate(jobs):
        j["index"] = k
    journal = Path(args.journal_dir)
    journal = journal if journal.is_absolute() else C.repo_root() / journal
    handlers = R._setup_logging(journal)
    log = R.logging.getLogger(R.LOG_NAME)
    try:
        log.info("%s: %d runs from %d families, workers %d", "+".join(args.lists), len(jobs), len({j["out_dir"] for j in jobs}), args.workers)
        for task in sorted({j["task"] for j in jobs}):
            getattr(R.importlib.import_module(task.partition(":")[0]), "warm_up", lambda: None)()
        t0 = time.monotonic()
        results = R.run_jobs(jobs, args.workers, journal, journal=True, handlers=handlers)
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
