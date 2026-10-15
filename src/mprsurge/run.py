"""Runner: python -m mprsurge.run --config <yaml> [--set k=v] [--workers N] [--dry-run].

Plan 6.1, 6.6, 10.3, 10.4. Drivers only integrate: this module expands a config
into cells, runs a task per cell (in a spawn pool for workers > 1), and writes
results atomically, keyed by config hash (readings in DL-056, DL-068).

A task is "module:function", called as task(cfg, deadline) with the cell's resolved
config (a plain dict) and a time.monotonic() deadline or None. It returns a dict
{"arrays": {name: ndarray}, "message": str, "flags": dict} and may raise RunTimeout.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import importlib
import itertools
import logging
import logging.handlers
import multiprocessing as mp
import os
import sys
import time
import traceback
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import config as C
from . import provenance as P
from .params import make_param_table, param_table_markdown

TASKS = {"mf": "mprsurge.simulate_mf:run_mf", "mf_noisy": "mprsurge.simulate_mf:run_mf_noisy"}
THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMBA_NUM_THREADS")
LOG_NAME = "mprsurge.run"


class RunTimeout(Exception):
    """Raised by a task that passes its wall-time deadline (status timeout)."""


# --- plan: config -> cells ---------------------------------------------------------

@dataclass
class Plan:
    cfg: dict               # resolved config before sweep expansion
    cells: list[dict]       # {"index", "name", "hash12", "cfg"}
    family: str
    out_dir: Path
    inputs: dict            # POSIX path -> SHA-256


def _config_path(arg: str) -> Path:
    """Relative config paths resolve from the repository root, then from the cwd."""
    p = Path(arg)
    if p.is_absolute():
        found = p if p.is_file() else None
    else:
        found = next((q for q in (C.repo_root() / p, Path.cwd() / p) if q.is_file()), None)
    if found is None:
        raise C.ConfigError(f"config file not found: {arg}")
    return found


def _axes(cfg: dict) -> list[tuple[str, list]]:
    sw = cfg["sweep"]
    axes = []
    for nk, vk in (("x_name", "x_values"), ("y_name", "y_values")):
        if (sw[nk] is None) != (sw[vk] is None):
            raise C.ConfigError(f"sweep.{nk} and sweep.{vk} must be given together")
        if sw[nk] is not None:
            axes.append((sw[nk], list(sw[vk])))
    if sw["T_ramp_values"] is not None:
        axes.append(("path.T_ramp_s", list(sw["T_ramp_values"])))
    names = [n for n, _ in axes]
    for n in names:
        section, _, key = n.partition(".")
        spec = C.SCHEMA.get(section, {}).get(key)
        if spec is None or spec.derived or section == "sweep":
            raise C.ConfigError(f"sweep axis {n!r} is not a sweepable section.key")
    if len(set(names)) != len(names):
        raise C.ConfigError(f"sweep axes repeat a key: {names}")
    return axes


def build_plan(config_arg: str, sets=(), workers: int | None = None) -> Plan:
    """Resolve the config and expand its sweep (and seeds, for mf_noisy) into cells.

    Axes: sweep.x, sweep.y (dotted section.key names) and sweep.T_ramp_values; cells
    are their product. For run.kind = mf_noisy each cell is repeated seeds.n_seeds
    times. A run with seed index s (0 to n_seeds-1) gets seeds.spawn_key = [s], the child
    SeedSequence(root_seed).spawn(n_seeds)[s], so the same seed index gives the same
    stream in every sweep cell (DL-069, DL-070); deterministic runs keep spawn_key null.
    """
    path = _config_path(config_arg)
    ov = dict(C.parse_override(s) for s in sets)
    if workers is not None:
        ov["run.workers"] = workers
    cfg0 = C.resolve_config(path, ov)
    axes = _axes(cfg0)
    noisy = cfg0["run"]["kind"] == "mf_noisy"
    combos = list(itertools.product(*[v for _, v in axes])) or [()]
    runs = [(combo, s) for combo in combos for s in range(cfg0["seeds"]["n_seeds"] if noisy else 1)]
    family = cfg0["run"]["id"] or path.stem
    out_root = Path(cfg0["output"]["dir"])
    out_dir = (out_root if out_root.is_absolute() else C.repo_root() / out_root) / family
    cells = []
    for k, (combo, seed) in enumerate(runs):
        cell_ov = dict(ov)
        cell_ov.update({n: v for (n, _), v in zip(axes, combo)})
        if noisy:
            cell_ov["seeds.spawn_key"] = [seed]
        cell = C.resolve_config(path, cell_ov)
        cell["sweep"] = {key: None for key in cell["sweep"]}
        h12 = C.short_hash(C.config_hash(cell))
        cells.append({"index": k, "name": f"{family}_{k:04d}_{h12}", "hash12": h12, "cfg": cell})
    inputs = {cfg0["_resolved_from"]["base"]: P.sha256_file(C.repo_root() / cfg0["_resolved_from"]["base"]),
              C.to_posix(path): P.sha256_file(path)}
    return Plan(cfg0, cells, family, out_dir, inputs)


# --- executing one cell ------------------------------------------------------------------

def resolve_task(ref: str):
    mod, _, func = ref.partition(":")
    return getattr(importlib.import_module(mod), func)


def execute_job(job: dict) -> dict:
    """Run (or skip, or dry-run) one cell; returns a small plain summary.

    The record is written last, so an ok record implies its outputs exist.
    """
    cfg, name, env = job["cfg"], job["name"], job["env"]
    out = Path(job["out_dir"])
    log = logging.getLogger(LOG_NAME)
    t0 = time.monotonic()
    summary = {"index": job["index"], "name": name, "hash12": job["hash12"]}

    if job["dry_run"]:
        done = P.find_complete(out, cfg) is not None
        rec = P.make_run_record(cfg, env, name=name, status=P.DRY_STATUS, inputs=job["inputs"],
                                dry_run=True, message="already complete" if done else "would run",
                                wall_time_s=0.0,
                                flags={"eta_path_status": cfg["path"]["eta_path_status"]})
        P.write_run_record(rec, out / f"{name}.dry.json")
        return {**summary, "status": P.DRY_STATUS, "wall_time_s": 0.0, "message": rec["message"]}

    if P.find_complete(out, cfg) is not None:
        return {**summary, "status": "skipped", "wall_time_s": 0.0, "message": "already complete"}

    log.info("start %s", name)
    limit = cfg["run"]["wall_limit_s"]
    deadline = None if limit is None else t0 + limit
    status, message, arrays, flags = "ok", "", None, {}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            res = resolve_task(job["task"])(cfg, deadline)
            arrays, message, flags = res.get("arrays"), res.get("message", ""), dict(res.get("flags", {}))
            if not arrays or not all(isinstance(a, np.ndarray) for a in arrays.values()):
                raise TypeError("task must return a non-empty dict of numpy arrays under 'arrays'")
        except RunTimeout as exc:
            status, message = "timeout", str(exc) or "wall-time limit reached"
        except Exception as exc:  # a failed cell is recorded, never crashes the pool
            status, message = "failed", f"{type(exc).__name__}: {exc}"
            flags["traceback"] = traceback.format_exc(limit=8)
    outputs = {}
    if status == "ok":
        P.atomic_save_npz(out / f"{name}.npz", arrays)
        P.atomic_write_text(out / f"{name}_params.md",
                            param_table_markdown(make_param_table(cfg)))
        outputs = {f"{name}.npz": P.sha256_file(out / f"{name}.npz"),
                   f"{name}_params.md": P.sha256_file(out / f"{name}_params.md")}
    wall = time.monotonic() - t0
    rec = P.make_run_record(cfg, env, name=name, status=status, message=message, wall_time_s=wall,
                            warnings=[f"{w.category.__name__}: {w.message}" for w in caught],
                            flags=flags, inputs=job["inputs"], outputs=outputs)
    P.write_run_record(rec, out / f"{name}.json")
    log.info("done %s status=%s wall=%.2fs", name, status, wall)
    return {**summary, "status": status, "wall_time_s": wall, "message": message}


# --- pool ---------------------------------------------------------------------------------------

@contextlib.contextmanager
def single_thread_env():
    """Set the thread variables before workers spawn, so BLAS and Numba read them at import."""
    old = {k: os.environ.get(k) for k in THREAD_VARS}
    os.environ.update({k: "1" for k in THREAD_VARS})
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _init_worker(log_queue) -> None:
    """Pool initializer (section 10.4): one thread per library; logs go to the parent."""
    for k in THREAD_VARS:
        os.environ[k] = "1"
    logger = logging.getLogger(LOG_NAME)
    logger.handlers[:] = [logging.handlers.QueueHandler(log_queue)]
    logger.setLevel(logging.INFO)
    logger.propagate = False


def _append_manifest(out_dir: Path, result: dict) -> None:
    path = out_dir / "manifest.csv"
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["index", "name", "hash12", "status", "wall_time_s", "message"])
        w.writerow([result["index"], result["name"], result["hash12"], result["status"],
                    f"{result['wall_time_s']:.3f}", result["message"].replace("\n", " ")])


def run_jobs(jobs: list[dict], workers: int, out_dir: Path, heartbeat_every: int = 10,
             journal: bool = True, handlers=()) -> list[dict]:
    """Execute jobs; workers == 1 runs in-process, otherwise in a spawn pool.

    handlers: parent logging handlers that also receive the workers' records.
    """
    log = logging.getLogger(LOG_NAME)
    results: list[dict] = []
    t0, n = time.monotonic(), len(jobs)

    def take(result):
        results.append(result)
        if journal:
            _append_manifest(out_dir, result)
        k = len(results)
        if k % heartbeat_every == 0 and k < n:
            el = time.monotonic() - t0
            log.info("heartbeat %d/%d done, elapsed %.0f s, ETA %.0f s", k, n, el, el / k * (n - k))

    if workers <= 1 or n <= 1:
        for j in jobs:
            take(execute_job(j))
    else:
        ctx = mp.get_context("spawn")
        queue = ctx.Queue()
        listener = logging.handlers.QueueListener(queue, *handlers, respect_handler_level=True)
        listener.start()
        try:
            with single_thread_env(), ctx.Pool(min(workers, n), initializer=_init_worker,
                                               initargs=(queue,)) as pool:
                for result in pool.imap_unordered(execute_job, jobs, chunksize=1):
                    take(result)
        finally:
            listener.stop()
    return sorted(results, key=lambda r: r["index"])


# --- command line -------------------------------------------------------------------------------

def _setup_logging(out_dir: Path | None) -> list[logging.Handler]:
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(out_dir / "run.log", encoding="utf-8"))
    log = logging.getLogger(LOG_NAME)
    log.handlers[:] = handlers
    log.setLevel(logging.INFO)
    log.propagate = False
    for h in handlers:
        h.setFormatter(fmt)
    return handlers


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m mprsurge.run", description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True, help="run YAML (relative paths: repository root first)")
    ap.add_argument("--set", dest="sets", action="append", default=[], metavar="section.key=value")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="resolve, hash and write a run record per cell; integrate nothing")
    args = ap.parse_args(argv)
    try:
        plan = build_plan(args.config, args.sets, args.workers)
    except C.ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 2

    handlers = _setup_logging(None if args.dry_run else plan.out_dir)
    try:
        return _execute(plan, args.dry_run, handlers)
    finally:  # release the run.log file handle (Windows locks it)
        logging.getLogger(LOG_NAME).handlers.clear()
        for h in handlers:
            h.close()


def _execute(plan: Plan, dry_run: bool, handlers) -> int:
    log = logging.getLogger(LOG_NAME)
    workers = plan.cfg["run"]["workers"]
    env = P.environment_info()
    task = TASKS[plan.cfg["run"]["kind"]]
    jobs = [{"index": c["index"], "name": c["name"], "hash12": c["hash12"], "cfg": c["cfg"],
             "out_dir": str(plan.out_dir), "task": task, "env": env, "inputs": plan.inputs,
             "dry_run": dry_run} for c in plan.cells]
    log.info("%s: %d cells, kind %s, workers %d%s", plan.family, len(jobs),
             plan.cfg["run"]["kind"], workers, " (dry-run)" if dry_run else "")
    if not dry_run:
        try:
            mod = importlib.import_module(task.partition(":")[0])
        except ModuleNotFoundError as exc:
            print(f"task module {task.partition(':')[0]!r} is not available yet: {exc}",
                  file=sys.stderr)
            return 2
        getattr(mod, "warm_up", lambda: None)()  # warm the Numba cache in the parent
    results = run_jobs(jobs, workers, plan.out_dir, journal=not dry_run, handlers=handlers)
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    log.info("finished: %s", ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    return 1 if counts.get("failed") or counts.get("timeout") else 0


if __name__ == "__main__":  # required on Windows: workers are spawned (section 6.1)
    sys.exit(main())
