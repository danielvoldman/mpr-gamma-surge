"""MS13 13i: build figure FS5 (classifier tests and sensitivity; frequency mapping) from stored results.

  .venv/Scripts/python.exe scripts/fig_FS5.py [--tag]

Reads only files under results/ (figures.FS5_INPUTS: the A8 sensitivity, reachability, white-noise and baseline files, the A11 table and evaluator file, the RB9(a)
unit-level file, the A6 map and summary, the two A8 run records) and, as text that is parsed and never run, the two classifier test files named in
figures.FS5_TEST_FILES. It never simulates. It writes figures/FS5/ (FS5.pdf, FS5.png, FS5_caption.txt, FS5_drawn_data_sha256.txt, FS5_params.csv,
FS5_provenance.json, FS5_nordlie.md) through plotting.figures.make_FS5 and plotting.figprov. Without --tag the build is an untagged DRAFT (provenance draft = true).
With --tag the clean-tree check runs first and a dirty tree stops the build; a tag itself is never created here.
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures

DECLARED_INPUTS = figures.FS5_INPUTS          # relative to results/; scripts/ms13_inputs.py INPUTS["FS5"] must name the same files (test)
DECLARED_TEST_FILES = figures.FS5_TEST_FILES  # relative to the repository root; read as text, never run


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="tagged build: refuse a dirty tree (no tag is created)")
    a = ap.parse_args(argv)
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    out = figures.make_FS5(tag_build=a.tag)
    print(json.dumps({"timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"],
                      "git": out["prov"]["git"], "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
