"""S3 mean-field driver (plan 6.2 S3; MS5 step 5d, DL-116): hands configs/S3_ceni.yaml (K7 cells) and
configs/S3.yaml (K8 cells) to the runner, then reads the series back with analysis.s3 and writes
results/S3/s3_mf_summary.json. The network runs are step 5g. --dry-run only resolves and writes dry records.
"""
import json
import sys
import time

import numpy as np

from mprsurge import config as C
from mprsurge import run as R
from mprsurge.analysis import s3

CONFIGS = ("configs/S3_ceni.yaml", "configs/S3.yaml")


def read_cells(config: str) -> dict:
    """tau_d_ms -> (cfg, arrays) of the completed cells of one config."""
    plan = R.build_plan(config)
    out = {}
    for c in plan.cells:
        with np.load(plan.out_dir / f"{c['name']}.npz") as z:
            out[c["cfg"]["model"]["tau_d_ms"]] = (c["cfg"], {k: z[k] for k in z.files}, c["name"])
    return out


def summarise() -> dict:
    ceni, dev = read_cells(CONFIGS[0]), read_cells(CONFIGS[1])
    delta0 = next(iter(ceni.values()))[0]["solver"]["delta0"]
    ev = {k: {tau_d: s3.evaluate_cell(a["t_ms"], a["r"], a["v"], delta0) | {"cell": name}
              for tau_d, (_, a, name) in cells.items()} for k, cells in (("K7", ceni), ("K8", dev))}
    return {"delta0": delta0, "cells": ev, "K7": s3.judge_k7(ev["K7"], delta0), "K8": s3.judge_k8(ev["K8"], delta0)}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    t0, rc = time.monotonic(), 0
    for cfg in CONFIGS:
        rc = max(rc, R.main(["--config", cfg, *argv]))
    if rc or "--dry-run" in argv:
        return rc
    summary = summarise()
    summary["wall_time_s"] = time.monotonic() - t0
    path = C.repo_root() / "results" / "S3" / "s3_mf_summary.json"
    path.write_text(json.dumps(summary, indent=1, default=float), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("K7", "K8", "wall_time_s")}, indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
