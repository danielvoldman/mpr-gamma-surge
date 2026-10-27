"""MS11 11g: SHA-256 of every MS11 result file, frozen list/config, evaluator, test and doc, and of the decision-log range DL-330 to DL-<last> (as hash_ms10_results.py, DL-329).

  .venv/Scripts/python.exe scripts/hash_ms11_results.py --dl-last 400

Writes docs/ms11_file_hashes.csv (group, path, bytes, sha256). The digest of a group, and of the whole table, is the SHA-256 of the sorted 'path<TAB>sha256' lines (the 9j and
10g convention). The decision-log range is one row: path 'docs/decision_log.md#DL-330..DL-<last>', its bytes and SHA-256 are those of the text from the heading of DL-330 up to
the line before the heading of DL-<last + 1> (LF line ends). Not in the table: docs/ms11_file_hashes.csv itself, docs/ms11_evidence.md, and the decision-log entries after DL-<last>
(they quote the SHA-256 of these two files).
"""
import argparse
import csv
import hashlib
import re
from concurrent.futures import ThreadPoolExecutor

from mprsurge import config as C
from mprsurge.analysis import ms10_eval as E10
from mprsurge.analysis import ms11_runlist as RL

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


def records():
    files = []
    for n in RL.ALL_LISTS:
        for r in RL.expand(n):
            j = ROOT / E10.record_path(r)
            files += [j, j.with_suffix(".npz"), j.with_name(j.stem + "_params.md")]
    for d in sorted((ROOT / "results/ms11").glob("launch_*")):
        files += [d / "manifest.csv", d / "run.log"]
    return files


def dl_range(last):
    text = (ROOT / "docs/decision_log.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    a = re.search(r"^## DL-330 ", text, re.M)
    b = re.search(rf"^## DL-{last + 1} ", text, re.M)
    if not a:
        raise SystemExit("DL-330 not found")
    seg = text[a.start(): b.start() if b else len(text)]
    if not re.search(rf"^## DL-{last} ", seg, re.M):
        raise SystemExit(f"DL-{last} not found in the range")
    return seg.encode("utf-8")


GROUPS = [
    ("MS11 records and launch journals (238 records x json, npz, params.md; manifest.csv and run.log of 5 lists)", records),
    ("A11 outputs (a11_robustness.csv, a11_evaluators.json, rb9a_unit_level.json, independent recomputation outputs)", lambda: tree("results/A11")),
    ("five list definitions", lambda: sorted((ROOT / "configs/ms11/lists").glob("MS11_*.yaml"))),
    ("configs/ms11 (list hashes, eval choices, run configs)", lambda: [q for q in tree("configs/ms11") if "lists" not in q.parts]),
    ("docs (ms11_plan, ms11_eval_rules, ms11_results, ms11_launch)", lambda: [ROOT / "docs" / n for n in ("ms11_plan.md", "ms11_eval_rules.md", "ms11_results.md", "ms11_launch.md")]),
    ("code (ms11_* modules, rb9a_unit, launcher, A11 script, independent check, hash script, timing script)",
     lambda: [q for q in tree("src/mprsurge/analysis") if q.name.startswith("ms11_")] + [ROOT / "src/mprsurge/analysis/rb9a_unit.py"]
     + [ROOT / "scripts" / n for n in ("run_ms11_list.py", "run_A11.py", "run_rb9a_unit.py", "ms11_independent_check.py", "ms11_9b_look.py", "hash_ms11_results.py", "run_timing_ms11.sh")]),
    ("tests (test_ms11_*, fabricate_ms11.py)", lambda: sorted((ROOT / "tests").glob("test_ms11_*.py")) + [ROOT / "tests/fabricate_ms11.py"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dl-last", type=int, required=True)
    a = ap.parse_args()
    rows, seen = [], set()
    digests = []
    with ThreadPoolExecutor(8) as ex:
        for g, fn in GROUPS:
            fs = [f for f in fn() if f not in seen]
            missing = [f for f in fs if not f.exists()]
            if missing:
                raise SystemExit(f"missing: {missing[:3]}")
            seen.update(fs)
            hs = list(ex.map(sha, fs))
            lines = [f"{f.relative_to(ROOT).as_posix()}\t{h}" for f, h in zip(fs, hs)]
            rows += [(g, f.relative_to(ROOT).as_posix(), f.stat().st_size, h) for f, h in zip(fs, hs)]
            digests.append((g, len(fs), sum(f.stat().st_size for f in fs), hashlib.sha256((NL.join(sorted(lines)) + NL).encode()).hexdigest()))
            print(f"{g}: {len(fs)} files, {digests[-1][2] / 1e6:.3f} MB, digest {digests[-1][3]}", flush=True)
    seg = dl_range(a.dl_last)
    g = f"decision-log range DL-330 to DL-{a.dl_last}"
    p = f"docs/decision_log.md#DL-330..DL-{a.dl_last}"
    rows.append((g, p, len(seg), hashlib.sha256(seg).hexdigest()))
    print(f"{g}: 1 row, {len(seg)} bytes, sha256 {rows[-1][3]}")
    with open(ROOT / "docs/ms11_file_hashes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator=NL)
        w.writerow(["group", "path", "bytes", "sha256"])
        w.writerows(rows)
    allines = sorted(f"{p}\t{h}" for _, p, _, h in rows)
    table_digest = hashlib.sha256((NL.join(allines) + NL).encode()).hexdigest()
    n_res = len(records())
    print(f"{len(rows)} rows ({n_res} MS11 result files); total bytes {sum(r[2] for r in rows)}; table digest {table_digest}; docs/ms11_file_hashes.csv sha256 {sha(ROOT / 'docs/ms11_file_hashes.csv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
