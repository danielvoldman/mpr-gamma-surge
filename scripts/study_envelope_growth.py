"""7b driver (DL-136): the DL-062/DL-073 estimator study on synthetic data. Runs surge_metrics.envelope_growth on seeded
signals through analysis.estimator_study and writes results/A8/est_study/{est_study.json, est_study_cells.csv} and a run record.
No model is integrated.
"""
import csv
import sys
import time

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import estimator_study as E
from mprsurge.analysis import surge_metrics as M

CONFIG = "configs/est_study.yaml"
N_DRAW = 200


def xfail_case():
    """The DL-073 case of test_surge_metrics: 40 Hz ring, 15 cycles above threshold, step onset at 1 s, noise 1e-4."""
    lam = float(np.log(1.0 / E.THR) / (15 / 40.0))
    t = np.arange(int(4.0 * E.FS)) / E.FS
    tau = np.clip(t - 1.0, 0, None)
    v = np.where(t >= 1.0, np.exp(-lam * tau) * np.sin(2 * np.pi * 40.0 * tau), 0.0)
    v = v + 1e-4 * np.random.default_rng(20261014).standard_normal(t.size)
    g = M.envelope_growth(v, E.FS, E.BAND, E.THR)
    return {"true_rate": -lam, "fitted_rate": float(g["rate"]), "se": float(g["se"]),
            "within_10_percent": bool(abs(g["rate"] + lam) <= 0.1 * lam)}


def main() -> int:
    root = C.repo_root()
    cfg = C.resolve_config(CONFIG)
    out_dir = root / cfg["output"]["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    env = P.environment_info(with_julia=False)
    t0 = time.perf_counter()
    cells = E.scenarios()
    seqs = np.random.SeedSequence(cfg["seeds"]["root_seed"], spawn_key=tuple(cfg["seeds"]["spawn_key"])).spawn(len(cells))
    rows = [E.summarize(c, *E.run_cell(c, N_DRAW, s)) for c, s in zip(cells, seqs)]
    ver = E.verdicts(rows)
    ver["xfail_case"] = xfail_case()
    wall = time.perf_counter() - t0
    P.atomic_write_json(out_dir / "est_study.json", {"verdicts": ver, "n_draw": N_DRAW, "floor": E.FLOOR})
    with open(out_dir / "est_study_cells.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    names = ("est_study.json", "est_study_cells.csv")
    rec = P.make_run_record(cfg, env, name="EST7B_0000", status="ok", wall_time_s=wall,
                            flags={k: ver[k] for k in ("i_met", "ii_met")}, inputs={},
                            outputs={n: P.sha256_file(out_dir / n) for n in names})
    P.write_run_record(rec, out_dir / f"EST7B_0000_{C.short_hash(C.config_hash(cfg))}.json")
    print(f"i_met={ver['i_met']} ii_met={ver['ii_met']} k_max={ver['inflation_k_max']:.2f} wall {wall:.1f} s git.dirty={env['git']['dirty']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
