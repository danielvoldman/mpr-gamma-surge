"""MS13 13w W1 (DL-712): build FS5 ONCE from the committed code into another directory and compare it with docs/ms13_journal_final_hashes.txt.

  .venv/Scripts/python.exe scripts/ms13_13w_fs5_rebuild.py <out_base_dir>

Calls plotting.figures.make_FS5(mode="journal", out_dir=<out_base_dir>/FS5): the stored results only (results/A8, A6, A11 and the two test files FS5 reads as text), no simulation,
no other figure. The builder writes the figure files to <out_base_dir>/FS5 and the supplement files to <out_base_dir>/supplement (sup = out.parent / "supplement"); nothing is
written under figures/ of the repository. Prints the full SHA-256 of the new PNG, TIFF, PDF, caption, alt text, supplement, source-data CSV and the drawn-data digest next to the
value in docs/ms13_journal_final_hashes.txt (section FS5), and a unified diff of the caption and the supplement if they differ. It patches nothing. Exit code 0 if every compared
file is equal, 1 if only the caption, supplement, alt text or source data differ, 2 if the PNG, TIFF, PDF or the digest differ.
"""
import difflib
import hashlib
import re
import sys
from pathlib import Path

from mprsurge.config import repo_root
from mprsurge.plotting import figures


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 64
    base = Path(argv[0]).resolve()
    root = repo_root()
    if base == (root / "figures" / "journal").resolve() or (root / "figures").resolve() in base.parents or base == (root / "figures").resolve():
        print("refusing to write under figures/ of the repository", file=sys.stderr)
        return 64
    out = figures.make_FS5(mode="journal", out_dir=base / "FS5", root=root)
    print(f"timing_s {out['timing_s']}  git {out['prov']['git']}")
    # the committed list, section FS5
    text = (root / "docs" / "ms13_journal_final_hashes.txt").read_text(encoding="utf-8")
    sec = re.search(r"^## FS5 .*?(?=^## )", text, re.M | re.S).group(0)
    want, digest_want = {}, None
    for line in sec.splitlines():
        m = re.match(r"^([0-9a-f]{64})\s+(.*?)\s+(figures/\S+)$", line)
        if m:
            want[Path(m.group(3)).name] = (m.group(3), m.group(1))
        m = re.match(r"^drawn-data digest: ([0-9a-f]{64})$", line)
        if m:
            digest_want = m.group(1)
    new_files = {p.name: p for p in base.rglob("*") if p.is_file()}
    rows, worst = [], 0
    for name, (rel, h_want) in want.items():
        p = new_files.get(name)
        if p is None:
            rows.append((name, "MISSING", h_want, ""))
            worst = max(worst, 2)
            continue
        h_new = sha(p)
        ok = h_new == h_want
        rows.append((name, "equal" if ok else "DIFFERENT", h_want, h_new))
        if not ok:
            worst = max(worst, 2 if name.endswith((".png", ".tiff", ".pdf")) else 1)
    ok = out["drawn_sha256"] == digest_want
    rows.append(("drawn-data digest", "equal" if ok else "DIFFERENT", digest_want, out["drawn_sha256"]))
    if not ok:
        worst = 2
    for name, state, hw, hn in rows:
        print(f"{state:9s} {name}\n    committed list {hw}\n    new build      {hn}")
    for name in ("FS5_journal_caption.txt", "FS5_supplement.md"):
        rel, h_want = want[name]
        p = new_files[name]
        if sha(p) != h_want:
            old = (root / rel).read_text(encoding="utf-8").splitlines()
            new = p.read_text(encoding="utf-8").splitlines()
            print(f"--- diff {name} (committed working copy -> new build; new file kept at {p})")
            for ln in difflib.unified_diff(old, new, "committed", "new build", lineterm="", n=0):
                print(ln[:1500])
    print(f"exit {worst}")
    return worst


if __name__ == "__main__":
    sys.exit(main())
