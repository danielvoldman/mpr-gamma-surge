"""7g F-11 analysis driver (DL-150): reads the constant-parameter hold run made by
`python -m mprsurge.run --config configs/F11.yaml` (results/F11/F11) and writes results/F11/f11_floor.json and a run record.
It integrates nothing. The value written is a candidate, UNVERIFIED, draft, not frozen.
"""
import glob
import json
import sys

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import solver_floor as SF


def main() -> int:
    root = C.repo_root()
    cfg = C.resolve_config("configs/F11.yaml")
    src = sorted(glob.glob(str(root / "results/F11/F11/F11_0000_*.npz")))
    if len(src) != 1:
        raise SystemExit(f"expected exactly one F11 npz, found {len(src)}")
    z = np.load(src[0])
    summ = SF.floor_summary(z["v"], z["r"], z["s"])
    summ.update(label="candidate noise-free solver floor, UNVERIFIED, draft, not frozen (DL-150); constant parameters, "
                      "delta_0 = 0, DOP853 rtol 1e-10 atol 1e-12, P2 start state, 165 s",
                candidate_floor_v=summ["dv_max"], source_npz=str(src[0]).replace(str(root), "").lstrip("\/"))
    P.atomic_write_json(root / "results/F11/f11_floor.json", summ)
    env = P.environment_info(with_julia=False)
    cfg["run"].update(id="F11FLOOR", kind="f11floor")
    run = P.make_run_record(cfg, env, name="F11FLOOR_0000", status="ok", inputs={"npz": P.sha256_file(src[0])},
                            outputs={"f11_floor.json": P.sha256_file(root / "results/F11/f11_floor.json")}, flags={})
    P.write_run_record(run, root / "results/F11" / f"F11FLOOR_0000_{C.short_hash(C.config_hash(cfg))}.json")
    print(json.dumps({k: summ[k] for k in ("n_samples", "dv_max", "dv_max_second_half", "dv_final", "dv_rms", "dr_max", "ds_max",
                                            "dv_max_over_eps_abs_v")}, indent=1), f"git.dirty={env['git']['dirty']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
