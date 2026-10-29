"""MS13 13m: build figure F5 (surge/no-surge maps with network symbols and subgrid agreement; F5c: metrics against N) from stored results.

  .venv/Scripts/python.exe scripts/fig_F5.py [--tag]

Reads only files under results/ (figures.F5_INPUTS: the stored A9 tables v2 and subgrid agreement, the stored MS10 evaluation and record classes, the stored A11 table; the 12 stored S8 cell
records (config only); the stored S9 and S9_ctrl records and the mean-field origin records, read through the frozen MS10 evaluation call, one record at a time) and the frozen configs that
call opens. It never simulates. The per-seed f_pk, onset and duration of F5c are recomputed from the stored S9 and S9_ctrl series with the frozen classifier and must equal the stored classes
and the stored counts, minimum, median and maximum, else the build stops. It writes figures/F5/ (F5.pdf, F5.png, F5_caption.txt, F5_drawn_data_sha256.txt, F5_params.csv,
F5_provenance.json, F5_nordlie.md) through plotting.figures.make_F5 and plotting.figprov. Without --tag the build is an untagged DRAFT (provenance draft = true). With --tag the clean-tree
check runs first and a dirty tree stops the build; a tag itself is never created here.
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures

DECLARED_INPUTS = figures.F5_INPUTS          # relative to results/; scripts/ms13_inputs.py INPUTS["F5"] must name the same files (test)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="tagged build: refuse a dirty tree (no tag is created)")
    a = ap.parse_args(argv)
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    out = figures.make_F5(tag_build=a.tag)
    print(json.dumps({"timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"],
                      "git": out["prov"]["git"], "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
