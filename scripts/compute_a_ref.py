"""7c driver (DL-139): A_ref from the stored S3 record at ref_devalle (median band-passed Hilbert envelope over whole
cycles, first and last 1 s dropped; DL-138 ruling). Reads results/S3 and results/A5, writes results/A8/a_ref/a_ref.json
and a run record. No model is integrated.
"""
import json
import sys

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a_ref as A

S3_NPZ = "results/S3/devalle/devalle_0000_9e49def91dfc.npz"
A5_JSON = "results/A5/A5_0000_506cf5745380.json"
A5_NPZ = "results/A5/a5_cycles.npz"
CONFIG = "configs/a_ref.yaml"


def main() -> int:
    root = C.repo_root()
    cfg = C.resolve_config(CONFIG)
    out_dir = root / cfg["output"]["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    env = P.environment_info(with_julia=False)
    a5 = json.loads((root / A5_JSON).read_text(encoding="utf-8"))["flags"]["points"]["devalle_ref"]
    period_s = a5["period_tau"] * cfg["model"]["tau_ms"] * 1e-3
    d = np.load(root / S3_NPZ)
    res = A.compute_a_ref(d["t_ms"] * 1e-3, d["v"], period_s, a5_ptp=a5["amplitude_v"])
    rec = {**res, "definition": A.DEFINITION, "threshold_factor": A.AMIN_FACTOR,
           "threshold_abs": A.threshold_abs(res["value"]),
           "source_record": S3_NPZ, "source_record_sha256": P.sha256_file(root / S3_NPZ),
           "period_source": A5_JSON, "period_source_sha256": P.sha256_file(root / A5_JSON),
           "a5_cycles_npz_sha256": P.sha256_file(root / A5_NPZ),
           "code_sha": env["git"]["commit"], "git_dirty": env["git"]["dirty"],
           "status": "UNVERIFIED reading, owner-ruled"}
    P.atomic_write_json(out_dir / "a_ref.json", rec)
    run = P.make_run_record(cfg, env, name="AREF_0000", status="ok",
                            flags={"A_ref": res["value"], "n_cycles": res["n_cycles"]},
                            inputs={S3_NPZ: rec["source_record_sha256"], A5_JSON: rec["period_source_sha256"]},
                            outputs={"a_ref.json": P.sha256_file(out_dir / "a_ref.json")})
    P.write_run_record(run, out_dir / f"AREF_0000_{C.short_hash(C.config_hash(cfg))}.json")
    print(f"A_ref={res['value']:.6f} cycles={res['n_cycles']} window={res['window_s']} "
          f"thr={rec['threshold_abs']:.6f} git.dirty={env['git']['dirty']}")
    for k, x in res["alternates"].items():
        print(f"  {k}: {x['value']:.6f} ({x['label']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
