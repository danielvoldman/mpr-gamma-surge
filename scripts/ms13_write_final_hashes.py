"""MS13 13t-11 (DL-699 P4): write docs/ms13_journal_final_hashes.txt, the final hash list of the 13 journal figures for the tags (read-only on figures/, results/ and the manifest; writes only that file).
For each figure: full SHA-256 of the main PNG, TIFF, PDF, short caption, full caption (or the single caption of FS2 to FS5), alt text, supplement and source-data CSV; the commit the build came from (provenance) and the
drawn-data digest. Then the draft files (docs/ms13_figure_manifest.csv rows of the eleven drafts, compared with the files) and the figure names with the mapping journal -> draft.   Usage: python scripts/ms13_write_final_hashes.py"""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDS = "F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5".split()
SINGLE = {"FS2", "FS3", "FS4", "FS5"}
DRAFT = {"F1": "F1", "F2": "F2", "F3": "F3", "F4a": "F4", "F4b": "F4", "F5": "F5", "F5c": "F5", "F6": "F6", "FS1": "FS1", "FS2": "FS2", "FS3": "FS3", "FS4": "FS4", "FS5": "FS5"}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    out = ["# MS13 13t journal figures: final hash list for the tags (full SHA-256, working copy; written by scripts/ms13_write_final_hashes.py after the recorded build of 13t-11)",
           "# Journal files are the MAIN versions; the drafts (figures/<ID>/) are AUDIT COPIES. The user decides the tags; nothing is tagged, pushed or uploaded.",
           "# F1 source data: the file as written (28 MB); the zipped form for the Zenodo record is made later."]
    commits = set()
    for fid in IDS:
        d = ROOT / "figures/journal" / fid
        s = ROOT / "figures/journal/supplement"
        prov = json.loads((d / f"{fid}_journal_provenance.json").read_text(encoding="utf-8"))
        commit = prov.get("commit") or prov.get("git", {}).get("commit") or str(prov)[:0]
        files = [("png", d / f"{fid}_journal.png"), ("tiff", d / f"{fid}_journal.tiff"), ("pdf", d / f"{fid}_journal.pdf")]
        if fid in SINGLE:
            files.append(("caption (single)", d / f"{fid}_journal_caption.txt"))
        else:
            files += [("caption short", d / f"{fid}_journal_caption.txt"), ("caption full", d / f"{fid}_journal_caption_full.txt")]
        files += [("alt text", s / f"{fid}_alt_text.txt"), ("supplement", s / f"{fid}_supplement.md"), ("source data csv", s / f"{fid}_source_data.csv")]
        dd = (d / f"{fid}_journal_drawn_data_sha256.txt").read_text(encoding="utf-8").split()[0]
        out += ["", f"## {fid} (journal main version; draft audit copy: {DRAFT[fid]})", f"built from commit: {commit}", f"drawn-data digest: {dd}"]
        commits.add(commit)
        for k, p in files:
            if not p.is_file():
                print("MISSING", p)
                return 1
            out.append(f"{sha(p)}  {k:18s} {p.relative_to(ROOT).as_posix()}")
    out += ["", "## Build commits found in the provenance records: " + ", ".join(sorted(commits)), "", "## The eleven draft files (audit copies; byte-identical to the manifest; docs/ms13_figure_manifest.csv)"]
    bad = 0
    with open(ROOT / "docs/ms13_figure_manifest.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["file"].startswith(f"figures/{r['figure']}/") and r["figure"] in set(DRAFT.values()):
                p = ROOT / r["file"]
                now = sha(p) if p.is_file() else "MISSING"
                bad += now != r["sha256"]
                out.append(f"{now}  {r['figure']:4s} {r['file']}" + ("" if now == r["sha256"] else "   DIFFERS FROM THE MANIFEST"))
    out += ["", f"## draft files differing from the manifest: {bad}", "",
            "## Figure names as used for the tags and the mapping (the user decides the tags; pattern of the pre-check: fig-<name>-v<n>)",
            "F1 <- draft F1; F2 <- draft F2; F3 <- draft F3; F4a, F4b <- draft F4 (journal split, K2); F5, F5c <- draft F5 (journal split, T1); F6 <- draft F6;",
            "FS1, FS2, FS3, FS4, FS5 <- drafts FS1 to FS5. Journal files are the main versions; drafts are audit copies."]
    (ROOT / "docs/ms13_journal_final_hashes.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print("wrote docs/ms13_journal_final_hashes.txt; draft files differing:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
