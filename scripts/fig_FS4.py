"""MS13 13i: build figure FS4 (numerics) from stored results.

  .venv/Scripts/python.exe scripts/fig_FS4.py [--tag]

Reads only files under results/ (figures.FS4_INPUTS: the stored A7 table with the MS8 S13 families, the stored A11 evaluator file and A11 table with the MS11 S13
rows, and two S13 run records for the parameter rows), never simulates and draws no series. It writes figures/FS4/ (FS4.pdf, FS4.png, FS4_caption.txt,
FS4_drawn_data_sha256.txt, FS4_params.csv, FS4_provenance.json, FS4_nordlie.md) through plotting.figures.make_FS4 and plotting.figprov. Without --tag the build is
an untagged DRAFT (provenance draft = true). With --tag the clean-tree check runs first and a dirty tree stops the build; a tag itself is never created here.
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures

DECLARED_INPUTS = figures.FS4_INPUTS          # relative to results/; scripts/ms13_inputs.py INPUTS["FS4"] must name the same files (test)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="tagged build: refuse a dirty tree (no tag is created)")
    a = ap.parse_args(argv)
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    out = figures.make_FS4(tag_build=a.tag)
    print(json.dumps({"timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"],
                      "git": out["prov"]["git"], "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
