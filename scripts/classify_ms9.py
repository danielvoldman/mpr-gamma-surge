"""MS9 9b: classify stored MS9 records and write the class table (DL-216). Analysis only: nothing is integrated.

  .venv/Scripts/python.exe scripts/classify_ms9.py --root results/S12 --out results/ms9/nc1_classes.csv --report nc1

--root may be repeated. The table has one row per run (analysis.ms9_classify.classify_record: frozen classifier, frozen threshold, failed runs
labelled failed). --report nc1 prints the NC1 tables of the 9b step and the stop-rule set; the exit code is 4 if a pre-registered NC1 run is
not D-none (mode D) / NS (mode N) - that is the stop rule: report, run no diagnostics, the A8 review (G7) comes to the reviewer first.
"""
import argparse
import csv
import sys
import time
from pathlib import Path

from mprsurge import config as C
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import ms9_classify as MCL


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="classify_ms9")
    ap.add_argument("--root", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--report", choices=("nc1",), default=None)
    args = ap.parse_args(argv)
    fi, gate = A7.frozen_inputs()
    print(f"criteria gate ok: tag {gate['tag']}, threshold {fi['threshold']:.6f} (0.1 x A_ref {fi['a_ref']:.6f})")
    t0 = time.perf_counter()
    rows = []
    for root in args.root:
        p = Path(root)
        rows += MCL.classify_tree(p if p.is_absolute() else C.repo_root() / p, fi)
    wall = time.perf_counter() - t0
    out = Path(args.out)
    out = out if out.is_absolute() else C.repo_root() / out
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = sorted({k for r in rows for k in r})
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} records classified in {wall:.1f} s -> {out}")
    if args.report == "nc1":
        print(MCL.nc1_report(rows))
        return 4 if MCL.unexpected(rows) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
