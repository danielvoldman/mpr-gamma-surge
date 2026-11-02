"""MS13 13q: comparison step of the independent recomputation (docs/ms13_independent_plan.md). The only place that imports the figure data steps.

  .venv/Scripts/python.exe scripts/ms13_independent_compare.py            # compares, writes docs/ms13_independent_results.md and .csv, exit 1 if any row is not equal

Independent values: scripts/ms13_independent.py (own readers of the stored files). Drawn values: load_<ID> and prepare_<ID> of src/mprsurge/plotting/figures.py (nothing is drawn or
written by them). Printed values: the take-home constant <ID>_TAKE_HOME, a group of a regular expression of the row. Rules: integers, counts, class words and strings exact; a float
printed with k decimals is compared as the independent value rounded to k decimals (a number printed as a.be-n: to the digits printed); arrays and drawn floats with the row's
tolerance (None: exact; float: absolute; ('rel', x): relative; NaN equals NaN). A row whose regular expression finds no match, or whose drawn expression raises, is 'unresolved'
(a fault of this comparison, never counted as equal).
13t-1d (DL-571 T9, DL-572): a row with a journal pattern (`jprinted`, scripts/ms13_independent.py) is also searched in the JOURNAL caption of each of its target files
(figures/journal/<F1|F3|F5|F5c>/<ID>_journal_caption.txt, or --journal-dir); the independent value must reproduce the printed token to its digits, as for the draft. The journal rows are counted and
written separately from the draft rows (columns journal_*; a second table). A journal row that is not equal, or whose pattern finds nothing or whose caption is missing, is unresolved or not equal: exit 1.
"""
from __future__ import annotations

import csv
import math
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ms13_independent as IND  # noqa: E402

OUT_MD, OUT_CSV = "docs/ms13_independent_results.md", "docs/ms13_independent_results.csv"
COLUMNS = ("figure", "id", "quantity", "independent_value", "drawn_value", "printed_value", "source_of_drawn", "source_of_printed", "equal", "tolerance", "shared", "independent_source",
           "journal_files", "journal_pattern", "journal_printed_value", "journal_equal")
JOURNAL_FILES = ("F1", "F3", "F5", "F5c")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def same(a, b, tol) -> bool:
    if isinstance(a, dict) or isinstance(b, dict):
        return isinstance(a, dict) and isinstance(b, dict) and set(a) == set(b) and all(same(a[k], b[k], tol) for k in a)
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple, np.ndarray)):
        a, b = list(a), list(np.asarray(b).tolist() if isinstance(b, np.ndarray) else b)
        return len(a) == len(b) and all(same(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, str) or isinstance(b, str):
        return str(a) == str(b)
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, bool) or isinstance(b, bool):
        return bool(a) == bool(b)
    a, b = float(a), float(b)
    if math.isnan(a) or math.isnan(b):
        return math.isnan(a) and math.isnan(b)
    if tol is None:
        return a == b
    if isinstance(tol, tuple):
        return a == b or abs(a - b) <= tol[1] * max(abs(a), abs(b))
    return abs(a - b) <= tol


def printed_same(value, token: str) -> bool:
    """The independent value reproduces the printed token to the digits printed."""
    if isinstance(value, (list, tuple)):
        if len(value) != 1:
            return False
        value = value[0]
    if isinstance(value, str):
        return value == token
    if value is None:
        return False
    v = float(value)
    if "e" in token:
        mant = token.split("e")[0]
        nd = len(mant.split(".")[1]) if "." in mant else 0
        return f"{v:.{nd}e}" == f"{float(token):.{nd}e}"
    if "." in token:
        nd = len(token.split(".")[1])
        return round(v, nd) == float(token) or abs(v - float(token)) <= 0.5 * 10 ** (-nd) + 1e-12
    return v == float(int(token))


def drawn_sets(figures):
    from mprsurge.plotting import figures as FG, figprov as F
    from mprsurge import config as C
    out: dict = {}
    for fid in figures:
        raw = getattr(FG, f"load_{fid}")()
        if fid == "F1":
            crit, _ = F.K.load_frozen_criteria(C.repo_root())
            d = FG.prepare_F1(raw, crit)
        else:
            d = getattr(FG, f"prepare_{fid}")(raw)
        out[fid] = (d, _norm(getattr(FG, f"{fid}_TAKE_HOME")))
    return out


def journal_captions(base=None) -> dict:
    """{file id: whitespace-normalised journal caption text, or None if the file is absent} for F1, F3, F5 and F5c under figures/journal (or `base`)."""
    base = Path(base) if base is not None else ROOT / "figures" / "journal"
    out: dict = {}
    for f in JOURNAL_FILES:
        p = base / f / f"{f}_journal_caption.txt"
        out[f] = _norm(p.read_text(encoding="utf-8")) if p.is_file() else None
    return out


def compare_journal(r, journals) -> tuple:
    """(status, printed values, files) of the journal check of one row: 'n.a.' if the row has no journal pattern or no captions were given."""
    if r.get("jprinted") is None or journals is None:
        return "n.a.", "n.a.", ""
    status, vals = [], []
    files = list(r.get("jtargets") or (r["figure"],))
    for f in files:
        text = journals.get(f)
        if text is None:
            status.append("unresolved")
            vals.append(f"{f}: no caption")
            continue
        m = re.search(r["jprinted"][0], text)
        if m is None:
            status.append("unresolved")
            vals.append(f"{f}: no match")
            continue
        tok = m.group(r["jprinted"][1])
        vals.append(f"{f}: {tok}")
        status.append("yes" if printed_same(r["value"], tok) else "no")
    eq = "unresolved" if "unresolved" in status else ("no" if "no" in status else "yes")
    return eq, "; ".join(vals), ", ".join(files)


def compare(rows, drawn, journals=None) -> list:
    out = []
    for r in rows:
        d, text = drawn[r["figure"]]
        status, dv, pv = [], "n.a.", "n.a."
        if r["drawn"] is not None:
            try:
                dv = eval(r["drawn"], {"d": d, "np": np})
                status.append("yes" if same(r["value"], dv, r["tol"]) else "no")
            except Exception as exc:                       # an expression that cannot be evaluated is a fault of this step
                dv, status = f"ERROR {type(exc).__name__}: {exc}", status + ["unresolved"]
        if r["printed"] is not None:
            m = re.search(r["printed"][0], text)
            if m is None:
                pv, status = "no match", status + ["unresolved"]
            else:
                pv = m.group(r["printed"][1])
                status.append("yes" if printed_same(r["value"], pv) else "no")
        eq = "n.a." if not status else ("unresolved" if "unresolved" in status else ("no" if "no" in status else "yes"))
        jeq, jval, jfiles = compare_journal(r, journals)
        out.append({**r, "drawn_value": dv, "printed_value": pv, "equal": eq, "journal_equal": jeq, "journal_printed_value": jval, "journal_files": jfiles})
    return out


def write(results, per, seconds):
    def fmt(x):
        return "" if x is None else (repr(x) if isinstance(x, (list, tuple, float)) else str(x))
    with open(ROOT / OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNS)
        for r in results:
            w.writerow([r["figure"], r["id"], r["quantity"], fmt(r["value"]), fmt(r["drawn_value"]), fmt(r["printed_value"]), r["drawn"] or "n.a.",
                        (r["printed"][0] if r["printed"] else "n.a."), r["equal"], fmt(r["tol"]) or "exact", r["shared"] or "independent", r["source"],
                        r.get("journal_files", ""), (r["jprinted"][0] if r.get("jprinted") else "n.a."), r.get("journal_printed_value", "n.a."), r.get("journal_equal", "n.a.")])
    lines = ["# MS13 13q: independent recomputation (results)", "",
             "Generated by `scripts/ms13_independent_compare.py` from `scripts/ms13_independent.py` (stored records only) and the figure data steps (comparison only). Plan: `docs/ms13_independent_plan.md`.", "",
             f"Run time of the comparison: {seconds:.1f} s.", "", "| figure | quantities | shared | equal | not equal | unresolved | no comparison (n.a.) |", "|---|---|---|---|---|---|---|"]
    tot = [0] * 6
    for fid in IND.FIGURES:
        rs = [r for r in results if r["figure"] == fid]
        if not rs:
            continue
        v = [len(rs), sum(1 for r in rs if r["shared"]), sum(1 for r in rs if r["equal"] == "yes"), sum(1 for r in rs if r["equal"] == "no"),
             sum(1 for r in rs if r["equal"] == "unresolved"), sum(1 for r in rs if r["equal"] == "n.a.")]
        tot = [a + b for a, b in zip(tot, v)]
        lines.append(f"| {fid} | " + " | ".join(str(x) for x in v) + " |")
    lines.append("| all | " + " | ".join(str(x) for x in tot) + " |")
    jrows = [(r, f) for r in results if r.get("journal_equal", "n.a.") != "n.a." for f in r["journal_files"].split(", ")]
    lines += ["", "## Journal captions (13t-1d, DL-571 T9): journal rows, per journal file", "", "| journal file | quantities searched | equal | not equal | unresolved |", "|---|---|---|---|---|"]
    for f in JOURNAL_FILES:
        rs = [r for r, ff in jrows if ff == f]
        if rs:
            lines.append(f"| {f} | {len(rs)} | {sum(1 for r in rs if r['journal_equal'] == 'yes')} | {sum(1 for r in rs if r['journal_equal'] == 'no')} | {sum(1 for r in rs if r['journal_equal'] == 'unresolved')} |")
    bad = [r for r in results if r["equal"] in ("no", "unresolved")]
    lines += ["", "## Draft rows not equal or unresolved", ""]
    lines += [f"- {r['id']}: {r['quantity']}: independent {fmt(r['value'])}; drawn {fmt(r['drawn_value'])}; printed {fmt(r['printed_value'])} ({r['equal']})" for r in bad] or ["none"]
    jbad = [r for r in results if r.get("journal_equal", "n.a.") in ("no", "unresolved")]
    lines += ["", "## Journal rows not equal or unresolved", ""]
    lines += [f"- {r['id']}: {r['quantity']}: independent {fmt(r['value'])}; journal {fmt(r['journal_printed_value'])} ({r['journal_equal']})" for r in jbad] or ["none"]
    lines += ["", "Every row is in `docs/ms13_independent_results.csv` (columns: " + ", ".join(COLUMNS) + ")."]
    (ROOT / OUT_MD).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal-dir", default=None, help="folder with <ID>/<ID>_journal_caption.txt (default figures/journal)")
    a = ap.parse_args(argv)
    t0 = time.perf_counter()
    rows = IND.compute()
    figs = sorted({r["figure"] for r in rows}, key=IND.FIGURES.index)
    journals = journal_captions(a.journal_dir)
    results = compare(rows, drawn_sets(figs), journals)
    write(results, None, time.perf_counter() - t0)
    n_bad = sum(1 for r in results if r["equal"] in ("no", "unresolved"))
    jr = [r for r in results if r["journal_equal"] != "n.a."]
    jbad = [r for r in jr if r["journal_equal"] in ("no", "unresolved")]
    print(f"DRAFT rows: {len(results)} rows, {sum(1 for r in results if r['equal'] == 'yes')} equal, {sum(1 for r in results if r['equal'] == 'no')} not equal, "
          f"{sum(1 for r in results if r['equal'] == 'unresolved')} unresolved, {sum(1 for r in results if r['equal'] == 'n.a.')} without comparison")
    for f in JOURNAL_FILES:
        rs = [r for r in jr if f in r["journal_files"].split(", ")]
        print(f"JOURNAL rows {f}: {len(rs)} quantities searched in the {f} journal caption, {sum(1 for r in rs if r['journal_equal'] == 'yes')} equal, "
              f"{sum(1 for r in rs if r['journal_equal'] == 'no')} not equal, {sum(1 for r in rs if r['journal_equal'] == 'unresolved')} unresolved")
    for r in results:
        if r["equal"] in ("no", "unresolved"):
            print(" ", r["id"], "|", r["quantity"], "| indep", r["value"], "| drawn", r["drawn_value"], "| printed", r["printed_value"], "|", r["equal"])
    for r in jbad:
        print(" JOURNAL", r["id"], "|", r["quantity"], "| indep", r["value"], "| journal", r["journal_printed_value"], "|", r["journal_equal"])
    return 1 if (n_bad or jbad) else 0


if __name__ == "__main__":
    sys.exit(main())
