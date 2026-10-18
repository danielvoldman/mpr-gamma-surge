"""8f4 driver (DL-194): two SUPPLEMENTARY runs of the headline path at start distance 0.5 and 3 (default 1.5 is the existing headline run).
Post-hoc, not in the pre-registered S5 list, kept out of S5, S13 and every manifest used by rb_eval; feeds no gate. Integrates only
(analysis is scripts/run_rb_diag_startdist.py). Configs: configs/ms8/supp_startdist_headline_d{0p5,3}.yaml = configs/S5_ramp.yaml plus
path.start_distance. Outputs: results/ms8_diag/startdist (git-ignored); each record carries flags.label = "supplementary".
"""
import sys
import time

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.simulate_mf import run_mf

LABEL = "supplementary"
OUT = "results/ms8_diag/startdist"
CONFIGS = (("d0p5", "configs/ms8/supp_startdist_headline_d0p5.yaml", 0.5), ("d3", "configs/ms8/supp_startdist_headline_d3.yaml", 3.0))


def main() -> int:
    root = C.repo_root()
    env = P.environment_info()
    out = root / OUT
    out.mkdir(parents=True, exist_ok=True)
    for tag, path, d in CONFIGS:
        plan = R.build_plan(path)
        assert len(plan.cells) == 1
        c = plan.cells[0]
        cfg = c["cfg"]
        p = cfg["path"]
        assert abs(p["eta_H"] - p["eta_start"] - d) < 1e-12 and p["T_ramp_s"] == 120.0 and p["name"] == "path_hypoxia" and cfg["solver"]["delta0"] == 1e-6
        name = f"supp_{tag}_{c['hash12']}"
        t0 = time.monotonic()
        res = run_mf(cfg)
        wall = time.monotonic() - t0
        P.atomic_save_npz(out / f"{name}.npz", res["arrays"])
        rec = P.make_run_record(cfg, env, name=name, status="ok", message=res["message"], wall_time_s=wall,
                                flags={**res["flags"], "label": LABEL, "start_distance": d}, outputs={f"{name}.npz": P.sha256_file(out / f"{name}.npz")})
        P.write_run_record(rec, out / f"{name}.json")
        print(f"{name} hash12={rec['config_hash12']} wall={wall:.1f}s git={env['git']['commit'][:8]} dirty={env['git']['dirty']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
