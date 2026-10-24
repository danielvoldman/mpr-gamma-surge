"""MS10 10d/10e: evaluate the stored MS10 records (RB1, sigma check, S9, S10/RB8, G4). Analysis only: nothing is integrated, nothing is written but tables.

  .venv/Scripts/python.exe scripts/evaluate_ms10.py --out results/ms10/eval [--choices configs/ms10/ms10_eval.yaml]

Reads the frozen run lists (refuses while any MS10 data file is DRAFT), the records of each row (refuses a dirty record, a dry run, a hash that differs from
the list, an unlisted record in a family folder), applies the frozen criteria (gate first) and prints/writes the evaluation. A choice the plan and the rulings
leave open (E-n, docs/ms10_eval_rules.md) is read from the choices file (ruled at 10e, R25 to R28); if it is null the part that needs it stops with
MissingChoice. Before any network record is read the R27 time-origin check runs and stops (EvalRefused) on a mismatch. No verdict beyond the frozen counts is
made. Missing records are reported, never replaced.
"""
import argparse
import json
import sys
from pathlib import Path

from mprsurge import config as C
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import ms10_eval as E
from mprsurge.analysis import ms10_runlist as RL


def _part(name, fn, errors):
    try:
        return fn()
    except E.MissingChoice as exc:
        errors[name] = f"MissingChoice: {exc}"
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="evaluate_ms10")
    ap.add_argument("--out", required=True)
    ap.add_argument("--choices", default=None)
    args = ap.parse_args(argv)
    fi, gate = A7.frozen_inputs()
    fr = E.frozen_rb1()
    ch = E.load_choices(args.choices)
    lists = ("S8", "S9", "S10", "C2_S8", "C2_S9", "C2_S10")
    by = E.read_lists(lists, fi, table21=True)
    refs = E.mf_references(fi)
    controls = [r for n in RL.CONTROL_LISTS for r in by[n]]
    s8h = [r for r in by["S8"] if r["name"].startswith("S8_head")]
    s8c = [r for r in by["S8"] if r["name"].startswith("S8_cells")]
    errors: dict = {}
    res: dict = {"criteria_gate": gate["sha256"], "time_origin": [{k: o[k] for k in ("label", "shared", "stamp_offset_ms")} for o in E.origin_check_all(
        [r for n in lists for r in RL.expand(n)])], "missing": {n: sum(1 for r in v if r.get("missing")) for n, v in by.items()}}
    res["rb1_headline"] = _part("rb1_headline", lambda: E.rb1_headline(s8h, refs, controls, ch, fr), errors)
    res["rb1_cells"] = E.rb1_cells(s8c, refs, controls, E.stored_120s_classes(), fr)
    res["N_sweep"] = _part("N_sweep", lambda: E.n_sweep(by["S9"], refs.get(("head", 60.0)), controls, ch, fr, metrics=True), errors)
    if res["rb1_headline"] is not None and res["N_sweep"] is not None:
        res["rb1"] = E.rb1_overall(res["rb1_headline"], res["rb1_cells"], res["N_sweep"])
        res["g4"] = _part("g4", lambda: E.g4_summary(by, res["rb1"], res["rb1_cells"], ch), errors)
    res["sigma_check"] = _part("sigma_check", lambda: E.sigma_check(s8h, ch), errors)
    res["rb8"] = _part("rb8", lambda: E.rb8(by["S10"], controls, refs.get(("head", 60.0)), ch, fr), errors)
    res["errors"] = errors
    out = Path(args.out)
    out = out if out.is_absolute() else C.repo_root() / out
    out.mkdir(parents=True, exist_ok=True)
    (out / "ms10_eval.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k in ("missing", "errors")}, indent=1))
    if res.get("g4"):
        print("\n".join(res["g4"]["text"]))
    return 3 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
