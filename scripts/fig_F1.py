"""MS13 13l: build figure F1 (ramp protocol, mean-field and network r(t) and v(t) on the headline path, 300-neuron raster, spectrogram of v) from stored results.

  .venv/Scripts/python.exe scripts/fig_F1.py [--tag]

Reads only files under results/ (figures.F1_INPUTS: the stored A8 A_ref, the stored MS10 evaluation and the stored A11 table; the stored mean-field headline record, the six stored
network headline records and the series of the three 120 s ones), never simulates. The spectrogram is not stored: it is computed from the stored v by the frozen classifier routine
(analysis.surge_metrics.spectrogram_v) with the frozen settings. It writes figures/F1/ (F1.pdf, F1.png, F1_caption.txt, F1_drawn_data_sha256.txt, F1_params.csv, F1_provenance.json,
F1_nordlie.md) through plotting.figures.make_F1 and plotting.figprov. Without --tag the build is an untagged DRAFT (provenance draft = true). With --tag the clean-tree check runs
first and a dirty tree stops the build; a tag itself is never created here.
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures

DECLARED_INPUTS = figures.F1_INPUTS          # relative to results/; scripts/ms13_inputs.py INPUTS["F1"] must name the same files (test)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="store_true", help="tagged build: refuse a dirty tree (no tag is created)")
    a = ap.parse_args(argv)
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    out = figures.make_F1(tag_build=a.tag)
    print(json.dumps({"timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"],
                      "git": out["prov"]["git"], "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
