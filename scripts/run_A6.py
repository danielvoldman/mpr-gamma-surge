"""A6 driver (plan 5.2 A6, 9.1; MS6 step 6f): runs the Julia slice continuations by hand (a6_freq.jl, BifurcationKit pinned in
environment/julia), validates the CSV + JSON with julia_io, and writes results/A6/a6_freq_map.npz, a6_summary.json and a run record.
Nothing is integrated here: frequencies come from the Julia cycle branches through analysis.freq_map.
  --reuse  skip Julia and read the existing results/A6/julia (for re-validation only).
"""
import json
import shutil
import subprocess
import sys
import time

import yaml

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import freq_map
from mprsurge.analysis.continuation import julia_io

CONFIG = "configs/A6.yaml"
JL = "src/mprsurge/analysis/continuation/a6_freq.jl"
PATH_A4 = "configs/path_A4.yaml"
TARGET = "a6_freq_map.npz"


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
            print("A6: julia not found", file=sys.stderr)
            return 1
        res = subprocess.run([exe, f"--project={root / 'environment' / 'julia'}", str(root / JL), str(jdir)], cwd=root)
        if res.returncode != 0:
            print(f"A6: julia exited {res.returncode}", file=sys.stderr)
            return 1
    wall = time.perf_counter() - t0
    julia = julia_io.load_a6(jdir)
    eta_H = float(yaml.safe_load((root / PATH_A4).read_text(encoding="utf-8"))["path"]["eta_H"])
    arrays, summ = freq_map.build_a6(julia, eta_H)
    summ["julia_dirty"] = julia["record"]["dirty"]
    summ["julia_timings_s"] = julia["record"]["timings_s"]
    P.atomic_save_npz(out_dir / TARGET, arrays)
    (out_dir / "a6_summary.json").write_text(json.dumps(summ, indent=1, default=float), encoding="utf-8")
    sha = P.sha256_file(out_dir / TARGET)
    inputs = {JL: P.sha256_file(root / JL), PATH_A4: P.sha256_file(root / PATH_A4)}
    rec = P.make_run_record(cfg, env, name="A6_0000", status="ok", wall_time_s=wall, flags={k: summ[k] for k in ("k10", "devalle")},
                            inputs=inputs, outputs={TARGET: sha, "a6_summary.json": P.sha256_file(out_dir / "a6_summary.json")})
    rec_path = out_dir / f"A6_0000_{C.short_hash(C.config_hash(cfg))}.json"
    P.write_run_record(rec, rec_path)
    print(f"A6: {C.to_posix(out_dir / TARGET)} sha256 {sha}; wall {wall:.1f} s; record {C.to_posix(rec_path)} git.dirty={env['git']['dirty']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
