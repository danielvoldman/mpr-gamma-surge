"""8f5 driver (DL-196): clean-tree re-run of the 8f3 Sets A and B, exactly as scripts/run_ms8_diag_runs.py (same code path, same configs), written to a
NEW directory so that the first records (results/ms8_diag/setA, setB; git dirty = true) stay on disk as superseded. Integrates only; the
bit-for-bit comparison is in scripts/run_rb_diag_burst.py. Refuses to start if the tree is dirty or the target directory already has files."""
import sys

import run_ms8_diag_runs as D
from mprsurge import config as C
from mprsurge import provenance as P

OUT = "results/ms8_diag_rerun"


def main() -> int:
    env = P.environment_info()
    if env["git"]["dirty"]:
        print("tree is dirty: commit first (the re-run exists to record git dirty = false)")
        return 2
    target = C.repo_root() / OUT
    if target.exists() and any(target.rglob("*")):
        print(f"{target} is not empty: refusing to overwrite")
        return 2
    D.OUT = OUT
    return D.main()


if __name__ == "__main__":
    sys.exit(main())
