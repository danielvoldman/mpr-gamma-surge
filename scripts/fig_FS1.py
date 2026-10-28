"""MS13 13h: build figure FS1 (M2 diagram, K4 and K5 traces, ring map) from stored results.

  .venv/Scripts/python.exe scripts/fig_FS1.py [--tag]

Reads only files under results/ (figures.FS1_INPUTS: A1 fixed points, A2 ring map, A0 table, the four S1 records and the A1 and A2 run records), never
simulates, and writes figures/FS1/ (FS1.pdf, FS1.png, FS1_caption.txt, FS1_drawn_data_sha256.txt, FS1_params.csv, FS1_provenance.json, FS1_nordlie.md) through
plotting.figures.make_FS1 and plotting.figprov. Without --tag the build is an untagged DRAFT (provenance draft = true). With --tag the clean-tree check runs
first and a dirty tree stops the build; a tag itself is never created here.
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures

DECLARED_INPUTS = figures.FS1_INPUTS          # relative to results/; scripts/ms13_inputs.py INPUTS["FS1"] must name the same files (test)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="tagged build: refuse a dirty tree (no tag is created)")
    a = ap.parse_args(argv)
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    out = figures.make_FS1(tag_build=a.tag)
    print(json.dumps({"timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"],
                      "git": out["prov"]["git"], "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
