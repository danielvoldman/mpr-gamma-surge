"""A1 driver: M2 fixed points and stability (plan 5.2 A1). Runs configs/A1.yaml through the
runner, then publishes the result at the fixed name results/A1/a1_fixedpoints_2d.npz.

The copy is byte-identical to the runner's output A1_0000_<hash12>.npz, whose SHA-256 is in the
run record next to it.
"""
import sys
from pathlib import Path

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R

CONFIG = "configs/A1.yaml"
TARGET = "a1_fixedpoints_2d.npz"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    code = R.main(["--config", CONFIG, *argv])
    if code != 0 or "--dry-run" in argv:
        return code
    plan = R.build_plan(CONFIG, [a for prev, a in zip([""] + argv, argv) if prev == "--set"])
    cell = plan.cells[0]
    rec_path = P.find_complete(plan.out_dir, cell["cfg"])
    if rec_path is None:
        print("A1: no complete record", file=sys.stderr)
        return 1
    src = Path(rec_path).with_suffix(".npz")
    P.atomic_write_bytes(plan.out_dir / TARGET, src.read_bytes())
    sha = P.sha256_file(plan.out_dir / TARGET)
    assert sha == P.read_run_record(rec_path)["outputs"][src.name], "published copy differs from the recorded output"
    print(f"A1: {C.to_posix(plan.out_dir / TARGET)} sha256 {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
