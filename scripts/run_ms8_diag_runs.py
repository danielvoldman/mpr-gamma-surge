"""8f3 driver (DL-191): two EXPLORATORY diagnostic run sets. Post-hoc, kept out of the S5 and S13 lists and out of every manifest used by
rb_eval; they feed no gate. Integrates only (analysis is scripts/run_rb_diag_exploratory.py).
  Set A: P1, start distance 0.5, linear, DOP853 rtol 1e-10, T_ramp 1 s and 10 s, delta0 1e-9 and 1e-3. Each config is the S5 cell config
         (configs/ms8/s5_p1_start_distance.yaml cells 0 and 4) with solver.delta0 changed and nothing else.
  Set B: headline cell (configs/S5_ramp.yaml: P2, ref_devalle, 120 s, linear, I = 0, DOP853 rtol 1e-10) with the start v moved by +1 ulp
         and -1 ulp through run_mf(cfg, y0=...). y0 is not a config key, so these two records carry the headline config hash; the
         flags (exploratory, perturbation, y_start) tell them apart, and they live in their own directory.
Outputs: results/ms8_diag/setA, results/ms8_diag/setB (git-ignored). Each record: config hash, git hash, flags.label = "exploratory".
"""
import copy
import sys
import time
from pathlib import Path

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import rb_diag_expl as X
from mprsurge.simulate_mf import run_mf

OUT = "results/ms8_diag"


def save(out, name, cfg, env, res, wall, extra):
    out.mkdir(parents=True, exist_ok=True)
    P.atomic_save_npz(out / f"{name}.npz", res["arrays"])
    flags = {**res["flags"], "label": X.LABEL, **extra}
    rec = P.make_run_record(cfg, env, name=name, status="ok", message=res["message"], wall_time_s=wall, flags=flags,
                            outputs={f"{name}.npz": P.sha256_file(out / f"{name}.npz")})
    P.write_run_record(rec, out / f"{name}.json")
    print(f"{name} hash12={rec['config_hash12']} wall={wall:.1f}s git={env['git']['commit'][:8]} dirty={env['git']['dirty']}", flush=True)


def main() -> int:
    root = C.repo_root()
    env = P.environment_info()
    plan = R.build_plan("configs/ms8/s5_p1_start_distance.yaml")
    cells = {c["index"]: c for c in plan.cells}
    for idx, T, h12 in ((0, 1.0, "db99ad2873e9"), (4, 10.0, "9696033c76cb")):
        c = cells[idx]
        p = c["cfg"]["path"]
        assert c["hash12"] == h12 and p["T_ramp_s"] == T and abs(p["eta_H"] - p["eta_start"] - 0.5) < 1e-12 and c["cfg"]["solver"]["delta0"] == 1e-6, c["name"]
        for d0 in X.SET_A_DELTA0:
            cfg = copy.deepcopy(c["cfg"])
            cfg["solver"]["delta0"] = d0
            name = f"explA_T{T:g}_d{d0:g}_{C.short_hash(C.config_hash(cfg))}"
            t0 = time.monotonic()
            res = run_mf(cfg)
            save(root / OUT / "setA", name, cfg, env, res, time.monotonic() - t0, {"set": "A", "s5_cell": c["name"], "s5_cell_hash": c["hash12"]})
    plan = R.build_plan("configs/S5_ramp.yaml")
    cfg = plan.cells[0]["cfg"]
    ref = next(Path(root / "results/S5/ramp").rglob(f"S5ramp_0000_{plan.cells[0]['hash12']}.json"))
    y_ref = np.array(P.read_run_record(ref)["flags"]["y_start"], dtype=float)
    for sign, tag in ((+1, "ulp_plus"), (-1, "ulp_minus")):
        y0 = X.perturb_v(y_ref, sign)
        t0 = time.monotonic()
        res = run_mf(cfg, y0=y0)
        save(root / OUT / "setB", f"explB_{tag}_{plan.cells[0]['hash12']}", cfg, env, res, time.monotonic() - t0,
             {"set": "B", "perturbation": f"v {sign:+d} ulp", "y_ref": y_ref.tolist(), "y0": y0.tolist(), "headline_record": ref.name})
    return 0


if __name__ == "__main__":
    sys.exit(main())
