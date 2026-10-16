"""Timed single run and the concurrent-copies batch (plan 9.2 steps 1 and 2; MS3 steps 3b and 3d).

Driver side: this integrates. `run_once` is the timed repeat of scripts/time_one_run.py. `run_batch` runs N
copies of one config at once through the runner's spawn pool and initialiser (run.py pattern: thread variables
set to 1, workers get plain dicts), each copy timed on its own. A barrier releases the copies together, so
every copy runs while the others do. Summaries and arithmetic live in mprsurge.analysis.timing.
"""
from __future__ import annotations

import multiprocessing as mp
import os
import time
import traceback

from . import run as R

BARRIER_TIMEOUT_S = 900.0
_barrier = None


def run_once(cfg: dict, limit_s: float) -> dict:
    """One timed repeat: wall time of the integration call, status, step count where the solver reports it."""
    task = R.resolve_task(R.TASKS[cfg["run"]["kind"]])
    t0 = time.perf_counter()
    deadline = time.monotonic() + limit_s
    status, message, flags = "ok", "", {}
    try:
        res = task(cfg, deadline)
        message, flags = res.get("message", ""), dict(res.get("flags", {}))
    except R.RunTimeout as exc:
        status, message = "timeout", str(exc) or "wall-time limit reached"
    except Exception as exc:                      # recorded, not hidden; solver settings are not changed
        status, message = "failed", f"{type(exc).__name__}: {exc}"
        flags["traceback"] = traceback.format_exc(limit=8)
    wall = time.perf_counter() - t0
    return {"status": status, "wall_s": wall, "message": message, "nfev": flags.get("nfev"),
            "n_steps": flags.get("n_steps"), "retried_with_radau": flags.get("retried_with_radau"),
            "traceback": flags.get("traceback")}


def _init(log_queue, barrier) -> None:
    global _barrier
    R._init_worker(log_queue)
    _barrier = barrier


def _copy(job: dict) -> dict:
    """One copy in a worker: wait for all copies, then time the run (plain dict in, plain dict out)."""
    if job["warm_up"]:
        from . import simulate_mf as S
        S.warm_up()
    _barrier.wait(BARRIER_TIMEOUT_S)
    t_start = time.time()
    r = run_once(job["cfg"], job["limit_s"])
    r.update(pid=os.getpid(), copy=job["copy"], t_start=t_start, t_end=time.time())
    return r


def run_batch(cfg: dict, n: int, limit_s: float) -> dict:
    """N identical copies at once. batch_wall_s runs from the barrier release to the last copy finishing;
    pool_wall_s also includes spawning the pool (reported, not used for throughput)."""
    ctx = mp.get_context("spawn")
    queue, barrier = ctx.Queue(), ctx.Barrier(n)
    jobs = [{"cfg": cfg, "limit_s": limit_s, "copy": i, "warm_up": cfg["run"]["kind"] == "mf_noisy"} for i in range(n)]
    p0 = time.perf_counter()
    with R.single_thread_env(), ctx.Pool(n, initializer=_init, initargs=(queue, barrier)) as pool:
        copies = pool.map_async(_copy, jobs, chunksize=1).get()
    pool_wall = time.perf_counter() - p0
    t0, t1 = min(c["t_start"] for c in copies), max(c["t_end"] for c in copies)
    return {"n": n, "copies": copies, "batch_wall_s": t1 - t0, "start_spread_s": max(c["t_start"] for c in copies) - t0,
            "pool_wall_s": pool_wall, "distinct_pids": len({c["pid"] for c in copies}),
            "status": "ok" if all(c["status"] == "ok" for c in copies) else "not ok"}
