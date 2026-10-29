"""MS13 13k: build figure F4 (delay, peak power, f_pk and duration against the ramp rate eps) from stored results.

  .venv/Scripts/python.exe scripts/fig_F4.py [--tag]

Reads only files under results/ (figures.F4_INPUTS: the stored A7 table, the stored A3 table, the stored A4 summary and the stored A11 table; and the JSON config of the
373 run records behind them, for the ramp rate eps and the parameter rows), never simulates and draws no series. It writes figures/F4/ (F4.pdf, F4.png, F4_caption.txt,
F4_drawn_data_sha256.txt, F4_params.csv, F4_provenance.json, F4_nordlie.md) through plotting.figures.make_F4 and plotting.figprov. Without --tag the build is
an untagged DRAFT (provenance draft = true). With --tag the clean-tree check runs first and a dirty tree stops the build; a tag itself is never created here.
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures

DECLARED_INPUTS = figures.F4_INPUTS          # relative to results/; scripts/ms13_inputs.py INPUTS["F4"] must name the same files (test)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="tagged build: refuse a dirty tree (no tag is created)")
    a = ap.parse_args(argv)
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    out = figures.make_F4(tag_build=a.tag)
    print(json.dumps({"timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"],
                      "git": out["prov"]["git"], "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
