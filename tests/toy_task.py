"""Toy tasks for test_runner. Importable by name in spawned workers (tests/ is on sys.path).

Behaviour is chosen by model.Delta so that every sweep cell has its own hash:
0.99 raises (failed), 0.98 raises RunTimeout, 0.97 emits a warning.
"""
import os
import warnings

import numpy as np

from mprsurge.run import RunTimeout


def run(cfg, deadline):
    delta = cfg["model"]["Delta"]
    if delta == 0.99:
        raise RuntimeError("forced solver failure")
    if delta == 0.98:
        raise RunTimeout("forced timeout")
    if delta == 0.97:
        warnings.warn("forced warning", RuntimeWarning)
    t = np.arange(5, dtype=float)
    return {"arrays": {"v": delta * t, "J": np.array([cfg["model"]["J"]])},
            "message": "toy", "flags": {"deadline_given": deadline is not None}}


def run_env(cfg, deadline):
    keys = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMBA_NUM_THREADS")
    vals = np.array([float(os.environ.get(k, "nan")) for k in keys])
    return {"arrays": {"threads": vals, "delta": np.array([cfg["model"]["Delta"]])}}
