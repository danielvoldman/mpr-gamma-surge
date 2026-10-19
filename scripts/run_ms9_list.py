"""MS9 launcher (9b): run one or more MS9 lists through ONE worker pool (generalised from scripts/run_ms8_list.py, DL-173).

Drivers only integrate: the lists come from mprsurge.analysis.ms9_runlist (configs/ms9/ + overrides; the frozen-criteria gate applies),
jobs are ordered longest first (network runs by their update count, the other kinds by the runner's estimate) and handed to run.run_jobs.
Per-run outputs, names, hashes and records are those of `python -m mprsurge.run`; a restart skips complete runs (find_complete), so a
killed launch is resumed by running the same command again. `--cells A:B` takes a slice of the first selected list (in list order) for a
launch in parts; each invocation has its own journal (manifest.csv, run.log).

  python scripts/run_ms9_list.py --list NC1 --list SUPP_NC1_modeN --workers 10 --journal-dir results/ms9/launch_nc1 [--dry-run]

The launcher refuses to start on a dirty git tree unless --dry-run (every record must show git.dirty = false).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import ms9_runlist as RL
from mprsurge.analysis import timing as T

S_PER_NETWORK_UPDATE = 2.03e-9           # 9a sample under 10 copies (DL-211), used only to order jobs


def job_cost_s(cfg: dict) -> float:
    if cfg["run"]["kind"] == "network":
        return T.network_updates(cfg) * S_PER_NETWORK_UPDATE
    return R.estimated_cost_s(cfg)


def build_jobs(lists, cells=None, dry_run=False) -> list[dict]:
    env = P.environment_info()
    jobs: list[dict] = []
    for name in lists:
        rows = RL.expand(name)
        if cells is not None and name == lists[0]:
            rows = rows[cells[0]:cells[1]]
        for r in rows:
            jobs.append({"index": len(jobs), "list": name, "name": r["name"], "hash12": C.short_hash(r["hash"]), "cfg": r["cfg"],
                         "out_dir": str(C.repo_root() / r["out_dir"]), "task": R.TASKS[r["kind"]], "env": env, "inputs": r["inputs"],
                         "dry_run": dry_run})
    return jobs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="run_ms9_list")
    ap.add_argument("--list", dest="lists", action="append", required=True, choices=RL.ALL_LISTS)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--cells", default=None, metavar="A:B", help="slice [A, B) of the first --list, in list order (launch in parts)")
    ap.add_argument("--journal-dir", required=True, help="manifest.csv and run.log of this launch")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    cells = None
    if args.cells:
        a, _, b = args.cells.partition(":")
        cells = (int(a), int(b))
    if not args.dry_run and P.environment_info(with_julia=False)["git"].get("dirty"):
        print("git tree is dirty: commit first (records must show dirty = false)", file=sys.stderr)
        return 3
    jobs = build_jobs(args.lists, cells, args.dry_run)
    if not jobs:
        print("no jobs selected", file=sys.stderr)
        return 2
    jobs.sort(key=lambda j: -job_cost_s(j["cfg"]))             # stable: ties keep list order
    for k, j in enumerate(jobs):
        j["index"] = k
    journal = Path(args.journal_dir)
    journal = journal if journal.is_absolute() else C.repo_root() / journal
    handlers = R._setup_logging(None if args.dry_run else journal)
    log = R.logging.getLogger(R.LOG_NAME)
    try:
        log.info("%s: %d runs from %d families, workers %d%s", "+".join(args.lists), len(jobs), len({j["out_dir"] for j in jobs}), args.workers,
                 " (dry-run)" if args.dry_run else "")
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
