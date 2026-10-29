"""MS13 13j: build figure FS3 (finite size, heterogeneity shape, noise) from stored results.

  .venv/Scripts/python.exe scripts/fig_FS3.py [--tag]

Reads only files under results/ (figures.FS3_INPUTS: the stored MS10 evaluator output, the stored A11 evaluator file and A11 table, and three run records for the parameter rows), never simulates and draws no series. It writes figures/FS3/ (FS3.pdf, FS3.png, FS3_caption.txt,
FS3_drawn_data_sha256.txt, FS3_params.csv, FS3_provenance.json, FS3_nordlie.md) through plotting.figures.make_FS3 and plotting.figprov. Without --tag the build is
an untagged DRAFT (provenance draft = true). With --tag the clean-tree check runs first and a dirty tree stops the build; a tag itself is never created here.
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures

DECLARED_INPUTS = figures.FS3_INPUTS          # relative to results/; scripts/ms13_inputs.py INPUTS["FS3"] must name the same files (test)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="tagged build: refuse a dirty tree (no tag is created)")
    a = ap.parse_args(argv)
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    out = figures.make_FS3(tag_build=a.tag)
    print(json.dumps({"timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"],
                      "git": out["prov"]["git"], "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
