"""MS13 13n: figure manifest and hash checker (read-only; DL-493).

  .venv/Scripts/python.exe scripts/ms13_check_hashes.py                   # check the files against docs/ms13_figure_manifest.csv and the decision log
  .venv/Scripts/python.exe scripts/ms13_check_hashes.py --write-manifest  # the only write: docs/ms13_figure_manifest.csv

The manifest has one row per figure output file (pdf, png, caption, drawn-data digest, params csv, provenance json, Nordlie md) and per figure script and test of
F1 to F6 and FS1 to FS5, plus the shared files (style.py, claim_labels.py, figures.py, docs/claim_limit_labels.md, scripts/ms13_inputs.py): figure, file, sha256, dl.
'dl' is the decision-log entry whose LAST logged hash for the file equals the sha256 (blank if none does).

A logged hash of a file is the 64-hex string that follows the file's path or base name in a decision-log entry (an optional 'working' or '(working copy)' between them);
the LAST logged hash is the one in the highest DL number (a later position within an entry wins). Hashes after '(LF-normalised ...)' are not read.
The check reports, per manifest row: MISSING (file absent), CHANGED (file hash differs from the manifest), UNLOGGED (the decision log has no hash for the file),
NOT-LAST-LOGGED (the manifest hash is not the last logged hash of the file), DL-MISMATCH (the dl column is not the entry of the last logged hash); and UNLISTED
(a file in a figure folder, or a figure script or test, that the manifest does not list). It fixes nothing. Exit code 0 only if nothing is reported.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path

FIGURES = ("F1", "F2", "F3", "F4", "F5", "F6", "FS1", "FS2", "FS3", "FS4", "FS5")
OUTPUT_SUFFIXES = (".pdf", ".png", "_caption.txt", "_drawn_data_sha256.txt", "_params.csv", "_provenance.json", "_nordlie.md")
SHARED = ("src/mprsurge/plotting/style.py", "src/mprsurge/plotting/claim_labels.py", "src/mprsurge/plotting/figures.py", "docs/claim_limit_labels.md",
          "scripts/ms13_inputs.py")
MANIFEST = "docs/ms13_figure_manifest.csv"
LOG = "docs/decision_log.md"
COLUMNS = ("figure", "file", "sha256", "dl")
NL = chr(10)


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def figure_files(fig: str) -> list[str]:
    return [f"figures/{fig}/{fig}{s}" for s in OUTPUT_SUFFIXES] + [f"scripts/fig_{fig}.py", f"tests/test_fig_{fig}.py"]


def expected_files() -> list[tuple[str, str]]:
    return [(fig, rel) for fig in FIGURES for rel in figure_files(fig)] + [("shared", rel) for rel in SHARED]


def parse_log(text: str) -> list[tuple[int, str]]:
    """[(DL number, entry text)] in file order."""
    parts = re.split(r"^## DL-(\d+) ", text.replace("\r\n", "\n"), flags=re.M)
    return [(int(parts[i]), parts[i + 1]) for i in range(1, len(parts), 2)]


def logged_hashes(entries, rel: str) -> list[tuple[int, str]]:
    """Every (DL number, hash) that the log gives for the file: the 64-hex string after its path or base name. Sorted by DL number, then by position in the entry."""
    base = rel.rsplit("/", 1)[-1]
    found = []
    for pos, (n, body) in enumerate(entries):
        hits = []
        for pat in {re.escape(rel), re.escape(base)}:
            rx = r"(?<![\w.])" + pat + r"(?:\s*\((?:working|LF)[^)]*\))?\s*(?:working(?: copy)?)?\s*[:=]?\s*([0-9a-f]{64})(?![0-9a-f])"
            hits += [(m.start(1), m.group(1)) for m in re.finditer(rx, body)]
        found += [(n, pos, p, h) for p, h in set(hits)]
    found.sort()
    return [(n, h) for n, _, _, h in found]


def last_logged(entries, rel: str):
    L = logged_hashes(entries, rel)
    return L[-1] if L else None


def build_manifest_rows(root: Path, log_text: str) -> list[dict]:
    entries = parse_log(log_text)
    rows = []
    for fig, rel in expected_files():
        p = root / rel
        sha = sha256_file(p) if p.is_file() else ""
        ll = last_logged(entries, rel)
        rows.append({"figure": fig, "file": rel, "sha256": sha, "dl": f"DL-{ll[0]:03d}" if ll and ll[1] == sha else ""})
    return rows


def read_manifest(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check(root: Path, log_text: str, manifest: list[dict]) -> list[str]:
    """Problem lines (empty list = everything matches). Read-only."""
    entries = parse_log(log_text)
    problems, listed = [], set()
    for r in manifest:
        rel, want = r["file"], r["sha256"]
        listed.add(rel)
        p = root / rel
        if not p.is_file():
            problems.append(f"MISSING {rel}")
            continue
        have = sha256_file(p)
        if have != want:
            problems.append(f"CHANGED {rel}: file {have}, manifest {want}")
        ll = last_logged(entries, rel)
        if ll is None:
            problems.append(f"UNLOGGED {rel}: the decision log gives no hash for this file (manifest {want})")
        elif ll[1] != want:
            problems.append(f"NOT-LAST-LOGGED {rel}: manifest {want}, last logged DL-{ll[0]:03d} {ll[1]}")
        elif r["dl"] != f"DL-{ll[0]:03d}":
            problems.append(f"DL-MISMATCH {rel}: manifest dl {r['dl']!r}, last logged hash is in DL-{ll[0]:03d}")
    want_rows = {rel for _, rel in expected_files()}
    for fig in FIGURES:
        d = root / "figures" / fig
        if d.is_dir():
            want_rows |= {f"figures/{fig}/{q.name}" for q in d.iterdir() if q.is_file()}
    for rel in sorted(want_rows - listed):
        problems.append(f"UNLISTED {rel}: not in the manifest")
    return problems


JOURNAL_IDS = ("F1", "F2", "F3", "F4a", "F4b", "F5", "F5c", "F6", "FS1", "FS2", "FS3", "FS4", "FS5")
JOURNAL_SUFFIXES = ("png", "tiff")


def journal_reference_problems(root: Path, log_text: str) -> list[str]:
    """13t-9 (DL-682 N6): the journal PNG and TIFF of a figure are compared with the hash that the LATEST decision-log entry gives for the file (the path followed by the full SHA-256); a file with no logged
    hash is not checked, and an older logged hash is not used (the PNG of F3 is not byte-reproducible between builds, so only the hash of the final build is the reference). Read-only."""
    entries = parse_log(log_text)
    problems = []
    logged = {}
    for fid in JOURNAL_IDS:
        for suf in JOURNAL_SUFFIXES:
            rel = f"figures/journal/{fid}/{fid}_journal.{suf}"
            ll = last_logged(entries, rel)
            if ll is not None:
                logged[rel] = ll
    latest = max((ll[0] for ll in logged.values()), default=None)           # only the files that the latest entry with journal hashes logs are checked: an older entry is not a reference
    for rel, ll in logged.items():
        if ll[0] == latest:
            p = root / rel
            if not p.is_file():
                problems.append(f"JOURNAL-MISSING {rel}: logged in DL-{ll[0]:03d} ({ll[1]})")
            elif sha256_file(p) != ll[1]:
                problems.append(f"JOURNAL-CHANGED {rel}: file {sha256_file(p)}, last logged DL-{ll[0]:03d} {ll[1]}")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-manifest", action="store_true", help="write docs/ms13_figure_manifest.csv (the only write)")
    ap.add_argument("--root", default=None)
    a = ap.parse_args(argv)
    root = Path(a.root) if a.root else Path(__file__).resolve().parents[1]
    log_text = (root / LOG).read_bytes().decode("utf-8")
    if a.write_manifest:
        rows = build_manifest_rows(root, log_text)
        with open(root / MANIFEST, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator=NL)
            w.writeheader()
            w.writerows(rows)
        print(f"{len(rows)} rows written to {MANIFEST}; {sum(1 for r in rows if not r['dl'])} without a matching logged hash")
    manifest = read_manifest(root / MANIFEST)
    problems = check(root, log_text, manifest) + journal_reference_problems(root, log_text)
    print(f"{len(manifest)} manifest rows, {len(problems)} problems")
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
