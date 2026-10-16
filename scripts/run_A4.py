"""A4 driver (plan 5.2 A4; MS5 step 5c, DL-114): runs configs/A4.yaml through the runner, then publishes the result
at the fixed name results/A4/a4_hopf_curves.npz and prints the K7 to K11 verdicts from the run record.
Nothing is integrated: the numbers come from analysis/hopf.py (characteristic polynomial and brentq).
"""
import json
import sys
from pathlib import Path

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R

CONFIG = "configs/A4.yaml"
TARGET = "a4_hopf_curves.npz"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    code = R.main(["--config", CONFIG, *argv])
    if code != 0 or "--dry-run" in argv:
        return code
    plan = R.build_plan(CONFIG, [a for prev, a in zip([""] + argv, argv) if prev == "--set"])
    rec_path = P.find_complete(plan.out_dir, plan.cells[0]["cfg"])
    if rec_path is None:
        print("A4: no complete record", file=sys.stderr)
        return 1
    src = Path(rec_path).with_suffix(".npz")
    P.atomic_write_bytes(plan.out_dir / TARGET, src.read_bytes())
    sha = P.sha256_file(plan.out_dir / TARGET)
    rec = P.read_run_record(rec_path)
    assert sha == rec["outputs"][src.name], "published copy differs from the recorded output"
    print(f"A4: {C.to_posix(plan.out_dir / TARGET)} sha256 {sha}")
    print(json.dumps(rec["flags"]["verdicts"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
