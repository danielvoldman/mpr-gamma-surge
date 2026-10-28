"""MS13 13h: build figure FS2 (M3 validation K7 to K11) from stored results.

  .venv/Scripts/python.exe scripts/fig_FS2.py [--tag]

Reads only files under results/ (figures.FS2_INPUTS: A4, A5, A6 files and records, the S3 summaries and records), never
simulates, and writes figures/FS2/ (FS2.pdf, FS2.png, FS2_caption.txt, FS2_drawn_data_sha256.txt, FS2_params.csv, FS2_provenance.json, FS2_nordlie.md) through
plotting.figures.make_FS2 and plotting.figprov. Without --tag the build is an untagged DRAFT (provenance draft = true). With --tag the clean-tree check runs
first and a dirty tree stops the build; a tag itself is never created here.
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures

DECLARED_INPUTS = figures.FS2_INPUTS          # relative to results/; scripts/ms13_inputs.py INPUTS["FS2"] must name the same files (test)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="tagged build: refuse a dirty tree (no tag is created)")
    a = ap.parse_args(argv)
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    out = figures.make_FS2(tag_build=a.tag)
    print(json.dumps({"timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"],
                      "git": out["prov"]["git"], "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
