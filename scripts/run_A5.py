"""A5 driver (plan 5.2 A5, 9.1; MS6 step 6b): runs the Julia continuation by hand (a5_cycles.jl, BifurcationKit pinned in
environment/julia), validates its CSV + JSON with julia_io, and writes results/A5/a5_cycles.npz and a run record.
Nothing is integrated here: the arrays come from the Julia branches through analysis.a5.
  --reuse  skip Julia and read the existing results/A5/julia (for re-validation only).
"""
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import yaml

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a5
from mprsurge.analysis.continuation import julia_io

CONFIG = "configs/A5.yaml"
JL = "src/mprsurge/analysis/continuation/a5_cycles.jl"
A4_NPZ = "results/A4/a4_hopf_curves.npz"
PATH_A4 = "configs/path_A4.yaml"
TARGET = "a5_cycles.npz"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    root = C.repo_root()
    cfg = C.resolve_config(CONFIG)
    out_dir = root / cfg["output"]["dir"]
    jdir = out_dir / "julia"
    out_dir.mkdir(parents=True, exist_ok=True)
    env = P.environment_info()
    t0 = time.perf_counter()
    if "--reuse" not in argv:
        if jdir.exists():
            shutil.rmtree(jdir)
        exe = shutil.which("julia")
        if exe is None:
            print("A5: julia not found", file=sys.stderr)
            return 1
        res = subprocess.run([exe, f"--project={root / 'environment' / 'julia'}", str(root / JL), str(jdir)], cwd=root)
        if res.returncode != 0:
            print(f"A5: julia exited {res.returncode}", file=sys.stderr)
            return 1
    wall = time.perf_counter() - t0
    julia = julia_io.load_a5(jdir)
    a4 = np.load(root / A4_NPZ)
    eta_H = yaml.safe_load((root / PATH_A4).read_text(encoding="utf-8"))["path"]["eta_H"]
    arrays, flags = a5.build_a5(julia, float(a4["ceni_hopf_tau_d_ms"][0]), float(eta_H))
    flags["julia_dirty"] = julia["record"]["dirty"]
    flags["julia_timings_s"] = julia["record"]["timings_s"]
    P.atomic_save_npz(out_dir / TARGET, arrays)
    sha = P.sha256_file(out_dir / TARGET)
    inputs = {JL: P.sha256_file(root / JL), A4_NPZ: P.sha256_file(root / A4_NPZ), PATH_A4: P.sha256_file(root / PATH_A4)}
    rec = P.make_run_record(cfg, env, name="A5_0000", status="ok", wall_time_s=wall, flags=flags,
                            inputs=inputs, outputs={TARGET: sha})
    rec_path = out_dir / f"A5_0000_{C.short_hash(C.config_hash(cfg))}.json"
    P.write_run_record(rec, rec_path)
    print(f"A5: {C.to_posix(out_dir / TARGET)} sha256 {sha}; wall {wall:.1f} s; record {C.to_posix(rec_path)} git.dirty={env['git']['dirty']}")
    for k in ("criticality_ceni", "criticality_devalle", "hopf_vs_a4", "points", "A_ref"):
        print(k, flags[k])
    return 0


if __name__ == "__main__":
    sys.exit(main())
