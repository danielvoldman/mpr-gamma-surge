"""MS13 13t: build the journal export of a figure (DL-545 J5, DL-546) from stored results.

  .venv/Scripts/python.exe scripts/fig_journal.py F1 [F3 F5 ...]

Calls plotting.figures.make_<ID>(mode="journal") for each ID: the same data steps and drawing code as the draft, the journal settings of configs/journal_export.yaml. Reads only
files under results/ (and the frozen criteria and configs), never simulates. Writes figures/journal/<ID>/ (<ID>_journal.pdf, .png, .tiff, .eps where they build cleanly,
<ID>_journal_caption.txt, <ID>_journal_provenance.json, <ID>_params.csv, <ID>_journal_drawn_data_sha256.txt) and figures/journal/supplement/ (<ID>_supplement.md,
<ID>_source_data.csv, <ID>_alt_text.txt). Without --tag (alias --release) the build is an untagged DRAFT (provenance draft = true) and may run on a dirty tree. With --tag the clean-tree check (scripts/check_clean_tree.py) runs
first and a dirty tree stops the build before anything is written; on a clean tree the provenance says draft = false (MS15a 19, DL-738 D3, DL-739). No tag is created and nothing is
uploaded. The draft figures in figures/<ID>/ are not touched.
13t-1 builds F1, F3 and F5 only (J7); 13t-1d (DL-571 T1) builds F5 and F5c together: F5c is the second journal file of make_F5 (draft panels (f) to (i)).
"""
import argparse
import json
import subprocess
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import figures, journal

PILOT = ("F1", "F2", "F3", "F4a", "F4b", "F5", "F5c", "F6", "FS1", "FS2", "FS3", "FS4", "FS5")      # 13t-8b (DL-671): F4a, F4b; 13t-7 (DL-659): FS2, FS3; 13t-1: F1, F3, F5, F5c; 13t-2 (DL-616): F2 and F6; 13t-4 (DL-637): FS1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+", help="figure IDs (13t-1: F1, F3, F5)")
    ap.add_argument("--tag", "--release", dest="tag", action="store_true",
                    help="release build: refuse a dirty tree (clean-tree check first); provenance draft = false on a clean tree (no tag is created)")
    a = ap.parse_args(argv)
    bad = [i for i in a.ids if i not in PILOT]
    if bad:
        print(f"not built in 13t-1 (J7: F1, F3 and F5 only): {bad}", file=sys.stderr)
        return 2
    root = repo_root()
    if a.tag:
        rc = subprocess.run([sys.executable, str(root / "scripts" / "check_clean_tree.py")]).returncode
        if rc != 0:
            return rc
    ids = list(dict.fromkeys({"F5c": "F5", "F4a": "F4", "F4b": "F4"}.get(i, i) for i in a.ids))     # F5 and F5c are built together by make_F5, F4a and F4b by make_F4
    for fid in ids:
        out = getattr(figures, f"make_{fid}")(mode="journal", root=root, tag_build=a.tag)
        if fid == "F5":
            pairs = (("F5", out), ("F5c", out["F5c"]))
        elif fid == "F4":
            pairs = (("F4a", out), ("F4b", out["F4b"]))
        else:
            pairs = ((fid, out),)
        for name, o in pairs:
            print(json.dumps({"figure": name, "timing_s": o["timing_s"], "drawn_sha256": o["drawn_sha256"], "draft": o["prov"]["draft"], "git": o["prov"]["git"],
                              "paths": [str(p) for p in o["paths"]]}, indent=1, default=str))
    print("export manifest:", journal.write_export_manifest(root / "figures" / "journal"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
