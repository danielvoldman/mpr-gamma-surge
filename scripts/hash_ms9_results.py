"""MS9 9j: SHA-256 of every MS9 result file, run list and table (DL-266). Reads files, writes one CSV and prints per-group digests.

  .venv/Scripts/python.exe scripts/hash_ms9_results.py

Groups: per-run records (json and npz, plus the *_params.md and dry-run files that sit beside them) under results/S12, S12x, S16, S6, S7,
D31; the launch journals and class tables under results/ms9 (the 9j folder excluded: it is written after this); the A7 (S6 part), A9, A10
tables; the MS9 run lists and cell files under configs/ms9. Writes results/ms9/9j/file_hashes.csv (path, bytes, sha256) and
results/ms9/9j/file_digests.txt (group, files, bytes, digest = SHA-256 of the sorted 'path<TAB>sha256' lines).
"""
import csv
import hashlib
import sys
from concurrent.futures import ThreadPoolExecutor

from mprsurge import config as C

ROOT = C.repo_root()
GROUPS = {
    "records S12 (NC1, NC2, NC3, supplementary)": ["results/S12"], "records S12x (exploratory)": ["results/S12x"],
    "records S16": ["results/S16"], "records S6": ["results/S6"], "records S7 (map 1, map 2, subgrid)": ["results/S7"],
    "records D31": ["results/D31"], "launch journals and class tables (results/ms9)": ["results/ms9"],
    "A7 (S6 part), A9, A10 tables": ["results/A7/a7_s6_metrics.parquet", "results/A9", "results/A10"],
    "run lists and cell files (configs/ms9)": ["configs/ms9"], "G3 facts text": ["docs/ms9_g3_facts.md"],
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def files_of(rel):
    p = ROOT / rel
    if p.is_file():
        return [p]
    return sorted(q for q in p.rglob("*") if q.is_file() and "ms9/9j" not in q.as_posix())


def main():
    rows, digests = [], []
    with ThreadPoolExecutor(8) as ex:
        for g, rels in GROUPS.items():
            fs = [f for r in rels for f in files_of(r)]
            hs = list(ex.map(sha, fs))
            lines = [f"{f.relative_to(ROOT).as_posix()}\t{h}" for f, h in zip(fs, hs)]
            rows += [(f.relative_to(ROOT).as_posix(), f.stat().st_size, h) for f, h in zip(fs, hs)]
            digests.append((g, len(fs), sum(f.stat().st_size for f in fs), hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode()).hexdigest()))
            print(f"{g}: {len(fs)} files, {digests[-1][2] / 1e9:.3f} GB, digest {digests[-1][3]}", flush=True)
    out = ROOT / "results/ms9/9j"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "file_hashes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["path", "bytes", "sha256"])
        w.writerows(rows)
    (out / "file_digests.txt").write_text("\n".join(f"{g}\t{n}\t{b}\t{d}" for g, n, b, d in digests) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(rows)} files hashed; file_hashes.csv sha256 {sha(out / 'file_hashes.csv')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
