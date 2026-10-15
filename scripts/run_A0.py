"""A0 driver: the replication table K1 to K5 (plan 5.2 A0, MS2 step 2e). Runs configs/A0.yaml through the
runner, then publishes the table at results/A0/a0_replication.csv.

Needs results/A1, results/A2 and results/S1 (K4 and K5 runs) from their drivers. Refuses if
configs/replication.yaml differs from the frozen SHA-256 (DL-084) or an upstream file differs from its run
record. Exit code 1 if any row fails.
"""
import sys

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import replication as RP

CONFIG = "configs/A0.yaml"
TARGET = "a0_replication.csv"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    code = R.main(["--config", CONFIG, *argv])
    if code != 0 or "--dry-run" in argv:
        return code
    plan = R.build_plan(CONFIG, [a for prev, a in zip([""] + argv, argv) if prev == "--set"])
    rec_path = P.find_complete(plan.out_dir, plan.cells[0]["cfg"])
    if rec_path is None:
        print("A0: no complete record", file=sys.stderr)
        return 1
    with np.load(rec_path.with_suffix(".npz")) as z:
        text = RP.csv_text({k: z[k] for k in z.files})
    P.atomic_write_bytes(plan.out_dir / TARGET, text.encode("utf-8"))
    print(f"A0: {C.to_posix(plan.out_dir / TARGET)} sha256 {P.sha256_file(plan.out_dir / TARGET)}")
    failed = P.read_run_record(rec_path)["flags"]["failed"]
    if failed:
        print(f"A0: FAILED rows: {', '.join(failed)}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
