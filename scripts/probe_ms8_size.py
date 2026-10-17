"""MS8 8a size and memory probe (DL-167): integrates three short sample cells once in this process, in memory, and records the
compressed size of the npz the runner would write (np.savez_compressed, as provenance.atomic_save_npz) and the process peak
working set. Nothing is written but results/timing/ms8/size_probe.json. A timing/size sample for the 9.2 prediction, not an S5 run.

Driver: integrates, no analysis. Windows only (peak working set from psapi).
"""
import ctypes
import io
import json
import os
import sys
import time
from ctypes import wintypes
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge import simulate_mf as S
from mprsurge.analysis import timing as T

CELLS = (("ms8_p5_sig_t56", []), ("ms8_p2_lin_t56", []), ("mode_n", ["seeds.spawn_key=[0]"]))


class _PMC(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


def mem() -> tuple[int, int]:
    """(current, peak) working set of this process in bytes."""
    k = ctypes.WinDLL("psapi", use_last_error=True)
    k.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PMC), wintypes.DWORD]
    h = ctypes.WinDLL("kernel32").GetCurrentProcess
    h.restype = wintypes.HANDLE
    pmc = _PMC(); pmc.cb = ctypes.sizeof(_PMC)
    assert k.GetProcessMemoryInfo(h(), ctypes.byref(pmc), pmc.cb)
    return int(pmc.WorkingSetSize), int(pmc.PeakWorkingSetSize)


def main() -> int:
    out = {"cells": {}, "git": P.git_info(), "note": "in-process, one run per cell, peak working set is a process high-water mark"}
    S.warm_up()
    for cell, sets in CELLS:
        cfg = T.resolve_cell("configs/S5.yaml", cell, sets)
        task = R.resolve_task(R.TASKS[cfg["run"]["kind"]])
        cur0, peak0 = mem()
        t0 = time.perf_counter()
        res = task(cfg, None)
        wall = time.perf_counter() - t0
        cur1, peak1 = mem()
        arrays = res["arrays"]
        buf = io.BytesIO()
        np.savez_compressed(buf, **arrays)
        n = int(len(next(iter(arrays.values()))))
        raw = sum(a.nbytes for a in arrays.values())
        out["cells"][cell] = {"kind": cfg["run"]["kind"], "samples": n, "arrays": len(arrays), "raw_bytes": raw,
                              "npz_bytes": len(buf.getvalue()), "compression": len(buf.getvalue()) / raw,
                              "wall_s": wall, "ws_before": cur0, "ws_after": cur1, "peak_before": peak0, "peak_after": peak1,
                              "peak_increase_per_sample_bytes": (peak1 - cur0) / n,
                              "peak_increase_over_raw": (peak1 - cur0) / raw}
        print(cell, out["cells"][cell], flush=True)
        del res, arrays, buf
    d = Path(C.repo_root()) / "results" / "timing" / "ms8"
    d.mkdir(parents=True, exist_ok=True)
    P.atomic_write_json(d / "size_probe.json", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
