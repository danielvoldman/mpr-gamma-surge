"""MS13 13f: build figure F2 (one-parameter diagram along eta_bar at ref_devalle) from stored results.

  .venv/Scripts/python.exe scripts/fig_F2.py [--tag]

Reads only files under results/ (figures.F2_INPUTS: A5 cycles and record, S4 mean-field and network sweeps and their stored readouts, the A11 table), never
simulates, and writes figures/F2/ (F2.pdf, F2.png, F2_caption.txt, F2_drawn_data_sha256.txt, F2_params.csv, F2_provenance.json, F2_nordlie.md) through
plotting.figures.make_F2 and plotting.figprov. Without --tag the build is an untagged DRAFT (provenance draft = true). With --tag the clean-tree check runs
first and a dirty tree stops the build; a tag itself is never created here.
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures

DECLARED_INPUTS = figures.F2_INPUTS          # relative to results/; scripts/ms13_inputs.py INPUTS["F2"] must name the same files (test)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="tagged build: refuse a dirty tree (no tag is created)")
    a = ap.parse_args(argv)
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    out = figures.make_F2(tag_build=a.tag)
    print(json.dumps({"timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"],
                      "git": out["prov"]["git"], "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
