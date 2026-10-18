"""8f6 driver (DL-200): two EXPLORATORY runs of the headline cell at solver.atol 1e-10 and 1e-14 (default 1e-12 is the existing headline run).
The two atol values are the reviewer's diagnostic choices, NOT plan values. Post-hoc, not in the pre-registered S5 list, kept out of S5, S13 and
every manifest used by rb_eval; feeds no gate. Integrates only (analysis is scripts/run_rb_diag_atol_seed.py). Configs:
configs/ms8/expl_atol_{1e-10,1e-14}.yaml = configs/S5_ramp.yaml plus solver.atol. Outputs: results/ms8_diag/atol (git-ignored);
each record carries flags.label = "exploratory".
"""
import sys
import time

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.simulate_mf import run_mf

LABEL = "exploratory"
OUT = "results/ms8_diag/atol"
CONFIGS = (("1e-10", "configs/ms8/expl_atol_1e-10.yaml", 1e-10), ("1e-14", "configs/ms8/expl_atol_1e-14.yaml", 1e-14))


def main() -> int:
    root = C.repo_root()
    env = P.environment_info()
    out = root / OUT
    out.mkdir(parents=True, exist_ok=True)
    for tag, path, atol in CONFIGS:
        plan = R.build_plan(path)
        assert len(plan.cells) == 1
        c = plan.cells[0]
        cfg = c["cfg"]
        p, s = cfg["path"], cfg["solver"]
        assert p["T_ramp_s"] == 120.0 and p["name"] == "path_hypoxia" and p["profile"] == "linear" and s["delta0"] == 1e-6
        assert s["method"] == "DOP853" and s["rtol"] == 1e-10 and s["atol"] == atol
        name = f"explatol_{tag}_{c['hash12']}"
        t0 = time.monotonic()
        res = run_mf(cfg)
        wall = time.monotonic() - t0
        P.atomic_save_npz(out / f"{name}.npz", res["arrays"])
        rec = P.make_run_record(cfg, env, name=name, status="ok", message=res["message"], wall_time_s=wall,
                                flags={**res["flags"], "label": LABEL, "atol": atol}, outputs={f"{name}.npz": P.sha256_file(out / f"{name}.npz")})
        P.write_run_record(rec, out / f"{name}.json")
        print(f"{name} hash12={rec['config_hash12']} wall={wall:.1f}s git={env['git']['commit'][:8]} dirty={env['git']['dirty']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
