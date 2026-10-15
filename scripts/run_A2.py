"""A2 driver: M2 ring map and the K4-MF check (plan 5.2 A2). Runs configs/A2.yaml through the
runner, then publishes the result at the fixed name results/A2/a2_ring_map.npz.

Needs results/A1 (scripts/run_A1.py) and results/S1 (configs/S1.yaml through the runner).
"""
import sys
from pathlib import Path

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R

CONFIG = "configs/A2.yaml"
TARGET = "a2_ring_map.npz"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    code = R.main(["--config", CONFIG, *argv])
    if code != 0 or "--dry-run" in argv:
        return code
    plan = R.build_plan(CONFIG, [a for prev, a in zip([""] + argv, argv) if prev == "--set"])
    rec_path = P.find_complete(plan.out_dir, plan.cells[0]["cfg"])
    if rec_path is None:
        print("A2: no complete record", file=sys.stderr)
        return 1
    src = Path(rec_path).with_suffix(".npz")
    P.atomic_write_bytes(plan.out_dir / TARGET, src.read_bytes())
    sha = P.sha256_file(plan.out_dir / TARGET)
    assert sha == P.read_run_record(rec_path)["outputs"][src.name], "published copy differs from the recorded output"
    print(f"A2: {C.to_posix(plan.out_dir / TARGET)} sha256 {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
