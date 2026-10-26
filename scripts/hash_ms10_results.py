"""MS10 10g: SHA-256 of every MS10 result file, frozen list/config, evaluator, test and doc (DL-329). Reads files, writes one CSV and prints group digests.

  .venv/Scripts/python.exe scripts/hash_ms10_results.py

Writes docs/ms10_file_hashes.csv (group, path, bytes, sha256). The digest of a group, and of the whole table, is the SHA-256 of the sorted 'path<TAB>sha256'
lines (the 9j convention). Not in the table: docs/ms10_file_hashes.csv itself, docs/ms10_g_evidence.md, docs/ms10_close.md (their SHA-256 are in the decision log).
"""
import csv
import hashlib
from concurrent.futures import ThreadPoolExecutor

from mprsurge import config as C

ROOT = C.repo_root()
NL = chr(10)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tree(rel):
    p = ROOT / rel
    return [p] if p.is_file() else sorted(q for q in p.rglob("*") if q.is_file() and "__pycache__" not in q.parts)


def from_table():
    with open(ROOT / "results/ms10/10f/file_hashes.csv", newline="", encoding="utf-8") as f:
        return [ROOT / r["path"] for r in csv.DictReader(f)]


GROUPS = [
    ("10f records and launch journals (103 records x json, npz, params.md; manifest.csv and run.log of 6 lists)", from_table),
    ("10f file-hash table", lambda: tree("results/ms10/10f/file_hashes.csv")),
    ("10f evaluation output", lambda: tree("results/ms10/eval")),
    ("companion mean-field records and journal (MF_COMPANION)", lambda: tree("results/S8/mf") + tree("results/ms10/launch_mf")),
    ("10b candidate table", lambda: tree("results/ms10/10b")),
    ("10a timing sample", lambda: tree("results/timing/ms10")),
    ("10g independent recomputation outputs", lambda: tree("results/ms10/10g")),
    ("configs/ms10 (frozen lists, cells, references, eval choices, run configs)", lambda: tree("configs/ms10")),
    ("code (ms10_* modules, qif_network.py, launcher, evaluators, writers, checks, scripts)",
     lambda: [q for q in tree("src/mprsurge/analysis") if q.name.startswith("ms10_")] + tree("src/mprsurge/qif_network.py")
     + [ROOT / "scripts" / n for n in ("run_ms10_list.py", "evaluate_ms10.py", "write_ms10_results.py", "ms10_independent_check.py", "hash_ms10_results.py",
                                       "inventory_ms10_10b.py", "predict_ms10_10c.py", "propose_ms10_10c.py", "run_timing_ms10.sh")]),
    ("tests (test_ms10_*)", lambda: sorted((ROOT / "tests").glob("test_ms10_*.py"))),
    ("docs (ms10_plan, ms10_eval_rules, ms10_results, 10b and 10c tables)", lambda: [ROOT / "docs" / n for n in ("ms10_plan.md", "ms10_eval_rules.md", "ms10_results.md", "ms10_10b_s8_candidates.csv", "ms10_10c_s8_proposals.csv")]),
]


def main():
    rows, seen, digests = [], set(), []
    with ThreadPoolExecutor(8) as ex:
        for g, fn in GROUPS:
            fs = [f for f in fn() if f not in seen]
            seen.update(fs)
            hs = list(ex.map(sha, fs))
            lines = [f"{f.relative_to(ROOT).as_posix()}\t{h}" for f, h in zip(fs, hs)]
            rows += [(g, f.relative_to(ROOT).as_posix(), f.stat().st_size, h) for f, h in zip(fs, hs)]
            digests.append((g, len(fs), sum(f.stat().st_size for f in fs), hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode()).hexdigest()))
            print(f"{g}: {len(fs)} files, {digests[-1][2] / 1e6:.3f} MB, digest {digests[-1][3]}", flush=True)
    with open(ROOT / "docs/ms10_file_hashes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["group", "path", "bytes", "sha256"])
        w.writerows(rows)
    allines = sorted(f"{p}\t{h}" for _, p, _, h in rows)
    table_digest = hashlib.sha256((NL.join(allines) + NL).encode()).hexdigest()
    print(f"{len(rows)} files; table digest {table_digest}; docs/ms10_file_hashes.csv sha256 {sha(ROOT / 'docs/ms10_file_hashes.csv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
