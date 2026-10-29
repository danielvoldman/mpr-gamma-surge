"""MS13 13j: build figure F6 (failure reasons, negative controls, drive dissociation) from stored results.

  .venv/Scripts/python.exe scripts/fig_F6.py [--tag]

Reads only files under results/ (figures.F6_INPUTS: the stored A9, A10, A7 S6 and A11 tables, and three run records for the parameter rows), never simulates and draws no series. It writes figures/F6/ (F6.pdf, F6.png, F6_caption.txt,
F6_drawn_data_sha256.txt, F6_params.csv, F6_provenance.json, F6_nordlie.md) through plotting.figures.make_F6 and plotting.figprov. Without --tag the build is
an untagged DRAFT (provenance draft = true). With --tag the clean-tree check runs first and a dirty tree stops the build; a tag itself is never created here.
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures

DECLARED_INPUTS = figures.F6_INPUTS          # relative to results/; scripts/ms13_inputs.py INPUTS["F6"] must name the same files (test)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="tagged build: refuse a dirty tree (no tag is created)")
    a = ap.parse_args(argv)
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    out = figures.make_F6(tag_build=a.tag)
    print(json.dumps({"timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"],
                      "git": out["prov"]["git"], "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
