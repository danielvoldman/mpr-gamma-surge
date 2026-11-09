"""MS13 13v (DL-703 V3, DL-705): replace the wrong 'not run' clause of panel (a) in the recorded FS5 caption and in the copy of that caption in the FS5 supplement, without a build.

  .venv/Scripts/python.exe scripts/ms13_13v_fs5_caption_fix.py [--dry-run]

Reads results/A8/a8_sensitivity.csv (counts of the cells: synthetic rows x variants, 'not run' records in the synthetic block and in all blocks), builds the new clause with
plotting.jfs5.not_run_clause (the same function the FS5 builder now uses), replaces the one old clause in figures/journal/FS5/FS5_journal_caption.txt and
figures/journal/supplement/FS5_supplement.md (exactly one occurrence each, else it stops and writes nothing), and prints the old and new SHA-256 of both files. The image, the PNG, TIFF, PDF,
the alt text and the source data are not touched.
"""
import csv
import hashlib
import sys

from mprsurge.config import repo_root
from mprsurge.plotting import jfs5

OLD = "one mark per cell, class names as in the Key, and 'not run' where the variant's window does not fit"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main(argv=None) -> int:
    dry = "--dry-run" in (argv if argv is not None else sys.argv[1:])
    root = repo_root()
    with open(root / "results/A8/a8_sensitivity.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    variants = {r["variant"] for r in rows}
    syn = {(r["record"], r["T_ramp_s"]) for r in rows if r["dataset"] == "synthetic"}
    n_cells = len(syn) * len(variants)
    nr_a = sum(1 for r in rows if r["dataset"] == "synthetic" and r["cls"] == "not_run")
    nr_c = sum(1 for r in rows if r["cls"] == "not_run")
    new = jfs5.not_run_clause(n_cells, nr_a, nr_c)
    print(f"cells in (a): {n_cells}; not run in (a): {nr_a}; not run in all groups: {nr_c}")
    print("new clause:", new)
    files = [root / "figures/journal/FS5/FS5_journal_caption.txt", root / "figures/journal/supplement/FS5_supplement.md"]
    texts = {}
    for f in files:
        b = f.read_bytes()
        t = b.decode("utf-8")
        if t.count(OLD) != 1:
            print(f"STOP: {f} has {t.count(OLD)} occurrences of the old clause", file=sys.stderr)
            return 2
        texts[f] = (sha(b), t.replace(OLD, new))
    for f, (old_h, t) in texts.items():
        nb = t.encode("utf-8")
        print(f"{f.relative_to(root).as_posix()}  old {old_h}  new {sha(nb)}")
        if not dry:
            f.write_bytes(nb)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
