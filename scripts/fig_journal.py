"""MS13 13t: build the journal export of a figure (DL-545 J5, DL-546) from stored results.

  .venv/Scripts/python.exe scripts/fig_journal.py F1 [F3 F5 ...]

Calls plotting.figures.make_<ID>(mode="journal") for each ID: the same data steps and drawing code as the draft, the journal settings of configs/journal_export.yaml. Reads only
files under results/ (and the frozen criteria and configs), never simulates. Writes figures/journal/<ID>/ (<ID>_journal.pdf, .png, .tiff, .eps where they build cleanly,
<ID>_journal_caption.txt, <ID>_journal_provenance.json, <ID>_params.csv, <ID>_journal_drawn_data_sha256.txt) and figures/journal/supplement/ (<ID>_supplement.md,
<ID>_source_data.csv, <ID>_alt_text.txt). The build is an untagged DRAFT (provenance draft = true). No tag is created and nothing is uploaded. The draft figures in figures/<ID>/ are not touched.
13t-1 builds F1, F3 and F5 only (J7).
"""
import argparse
import json
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures, journal

PILOT = ("F1", "F3", "F5")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+", help="figure IDs (13t-1: F1, F3, F5)")
    a = ap.parse_args(argv)
    bad = [i for i in a.ids if i not in PILOT]
    if bad:
        print(f"not built in 13t-1 (J7: F1, F3 and F5 only): {bad}", file=sys.stderr)
        return 2
    root = repo_root()
    for fid in a.ids:
        out = getattr(figures, f"make_{fid}")(mode="journal", root=root)
        print(json.dumps({"figure": fid, "timing_s": out["timing_s"], "drawn_sha256": out["drawn_sha256"], "draft": out["prov"]["draft"], "git": out["prov"]["git"],
                          "paths": [str(p) for p in out["paths"]]}, indent=1, default=str))
    print("export manifest:", journal.write_export_manifest(root / "figures" / "journal"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
