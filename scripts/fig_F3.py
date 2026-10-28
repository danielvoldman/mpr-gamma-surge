"""MS13 13d: build figure F3 ((eta, tau_d) and (eta, Delta) planes) from stored results.

  .venv/Scripts/python.exe scripts/fig_F3.py [--tag]

Reads only files under results/ (the list below), never simulates, and writes figures/F3/ (F3.pdf, F3.png, F3_caption.txt, F3_drawn_data_sha256.txt,
F3_params.csv, F3_provenance.json, F3_nordlie.md) through plotting.figures.make_F3 and plotting.figprov. Without --tag the build is an untagged
DRAFT (provenance draft = true). With --tag the clean-tree check runs first and a dirty tree stops the build; a tag itself is never created here.
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures

DECLARED_INPUTS = figures.F3_INPUTS          # relative to results/; scripts/ms13_inputs.py INPUTS["F3"] must name the same files (test row 12)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="tagged build: refuse a dirty tree (no tag is created)")
    a = ap.parse_args(argv)
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    out = figures.make_F3(tag_build=a.tag)
    print(json.dumps({"timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"],
                      "git": out["prov"]["git"], "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
