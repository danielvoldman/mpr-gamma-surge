"""A11 (plan section 7.2, Table 9.1: stored series only, no re-simulation): evaluate the MS11 checks and write results/A11/a11_robustness.csv.

  .venv/Scripts/python.exe scripts/run_A11.py --check-only            # gates and required fields only; opens no record
  .venv/Scripts/python.exe scripts/run_A11.py [--out results/A11] [--skip-subgrid] [--no-hooks]
  .venv/Scripts/python.exe scripts/run_A11.py --results-root <dir> --no-hooks --out <dir>/A11     # FABRICATED-record test of the code path only (11d)

Reads, in this order: the frozen criteria (gate first; thresholds come from the tag's blob), the required evaluation fields of configs/ms11/ms11_eval.yaml (a null or
absent field raises MissingChoice and the script stops), the frozen MS11 run lists and their records (refusals of ms11_eval.read_lists: not FROZEN, unlisted record, dirty
flag, dry run, hash or name differing from the list, criteria SHA-256), the R27 time-origin check for the network records, the S5 grid members (the 1e-6 and 1e-10
members of the S13 ladders), the stored map and headline series (RB9(b), RB9(c), RB10, the window x {0.5, 2} line) and the stored RB9(a) unit-level result.
Writes the table with the columns of ruling 14 and a JSON of the evaluator outputs. Drivers only integrate, analysis modules only analyse: nothing is integrated here.
Carried checks of MS8 to MS10 (26) are listed with the verdict word as logged, mapped by a11_logged_verdict_map, and RECOMPUTED by the hooks of analysis/ms11_hooks.py from the stored
records (A11 mode recompute_and_compare); a difference is flagged in the note column. --no-hooks leaves them carried (used only by the fabricated-record test).
--results-root redirects the `results/` prefix of every path read (fabricated-record test only; the real run omits it).
At 11d this script has NOT been run on any real record (tests use synthetic and FABRICATED records only; the fabricated records are deleted and never evaluated as results).
"""
import argparse
import json
import sys
from pathlib import Path

from mprsurge import config as C
from mprsurge import criteria as CR
from mprsurge import provenance as P
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import a8_sensitivity as A8
from mprsurge.analysis import ms11_eval as E
from mprsurge.analysis import ms11_eval_choices as EC
from mprsurge.analysis import ms11_runlist as RL

ROOT = C.repo_root()
RES_ROOT = ROOT / "results"            # redirected by --results-root in main()
VARIANTS = [v for v in A8.VARIANTS if v != "V0"]
MAP1 = ("results/ms9/9e/map1_classes.csv", "results/S7/S7_map1")
MAP2 = ("results/ms9/9f/map2_classes.csv", "results/S7/S7_map2")
SUBGRID = ("results/ms9/9f/subgrid_classes.csv", "results/S7/S7_subgrid")
HEADLINE_CLASSES = "results/ms9/9d/s5_headline_classes.csv"
RB9A_FILE = "results/A11/rb9a_unit_level.json"
S5_GRID = {"10": "p2_linear_0004_4f4756348cd8", "316": "p2_linear_0010_2ec39c34e678"}       # DL-338


def _res(rel: str) -> Path:
    """A path given with the `results/` prefix, under the results root (the repository's results/ unless --results-root)."""
    rel = rel.replace("\\", "/")
    return RES_ROOT / rel[len("results/"):] if rel.startswith("results/") else ROOT / rel


def _one(pattern: str) -> Path:
    base = _res(pattern)
    hits = sorted(base.parent.glob(base.name))
    if len(hits) != 1:
        raise SystemExit(f"expected one file for {pattern}, found {len(hits)}")
    return hits[0]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="run_A11")
    ap.add_argument("--out", default="results/A11")
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--skip-subgrid", action="store_true")
    ap.add_argument("--no-hooks", action="store_true", help="do not run the recompute hooks of the 26 carried checks (fabricated-record test)")
    ap.add_argument("--results-root", default=None, help="read the records and tables from here instead of <repo>/results (fabricated-record test only)")
    a = ap.parse_args(argv)
    global RES_ROOT
    if a.results_root:
        RES_ROOT = Path(a.results_root).resolve()
    fr = E.frozen_leaves()                                   # criteria gate first
    fi, gate = A7.frozen_inputs()
    ch = EC.load_choices()
    EC.check_all(ch)                                         # MissingChoice if any required field is null or absent
    E.verdict_map(ch)
    logged = E.load_logged()
    for e in logged:
        E.map_logged(e["logged_verdict"], ch)                # UnmappedVerdict for a word with no entry
    from mprsurge.analysis import ms11_hooks as HK
    HK.check_registry(logged)                                # a carried row without a hook (or a hook without a row) stops the script
    if RL.is_draft():
        raise SystemExit(f"MS11 data files not FROZEN: {RL.status()}")
    print(json.dumps({"criteria_sha256": gate["sha256"], "tag_commit": gate["commit"], "required_fields": len(EC.REQUIRED), "open_fields": EC.open_fields(ch),
                      "logged_checks": len(logged), "hooks": len(HK.HOOKS), "pending": list(EC.PENDING)}, indent=1))
    if a.check_only:
        return 0
    git = P.git_info()
    if git["dirty"] is not False:
        raise SystemExit("git tree is dirty: commit first")

    by = E.read_lists(fi, results_root=RES_ROOT if a.results_root else None)
    missing = {n: sum(1 for r in v if r.get("missing")) for n, v in by.items()}
    E.check_network_time_origin(RL.expand("MS11_S13_NET"), _one(f"results/S5/ramp/p2_linear/{S5_GRID['10']}.json"))
    grid = {T: E.classify_stored(_one(f"results/S5/ramp/p2_linear/{name}.json"), fi) for T, name in ((10.0, S5_GRID["10"]), (316.22776601683796, S5_GRID["316"]))}
    mf = by["MS11_S13_MF"]
    res: dict = {}
    res["rb2"] = E.rb2_s11(by["MS11_S11"], by["MS11_CTRL"], fr, ch, subgrid_logged=ch["rb2_subgrid"])
    res["rb5_delta0"] = E.rb5_delta0(E.delta0_by_T(mf, grid), ch)
    p5 = {r["T_ramp_s"]: r["class"] for r in (E.classify_stored(p, fi) for p in sorted(_res("results/S5/ramp/p5_linear").glob("*.json")) if not p.name.endswith(".dry.json"))}
    res["rb5_updown"] = E.rb5_updown(p5, "S4 up/down branch agreement at ref_devalle, quasi-static (MS6, DL-127, DL-128); no class", ch)
    res["rb6_rtol"] = E.rb6_rtol(E.rtol_by_T(mf, grid), ch)
    res["rb6_floor"] = E.rb6_floor_other_T({"raw_first_crossing": E.floor_by_T(mf, "delay_eta_raw"), "classifier_onset": E.floor_by_T(mf, "delay_eta")}, ch)
    res["rb6_network"] = E.rb6_network(E.net_recs(by["MS11_S13_NET"]), fr, ch)
    rb9a_p = _res(RB9A_FILE)
    res["rb9a"] = E.rb9a(json.loads(rb9a_p.read_text(encoding="utf-8")) if rb9a_p.exists() else None, fr, ch)

    # stored series: headline, map 1, map 2 (mode D), noisy subgrid (mode N, reported only)
    import csv
    hl = next(csv.DictReader(_res(HEADLINE_CLASSES).open(newline="", encoding="utf-8")))
    hl_json = _one(f"results/S5/ramp/S5ramp/{hl['run']}.json")
    head = E.classify_stored(hl_json, fi, with_v=True)
    head_ep = {k: float(hl[k]) for k in ("onset_s", "end_s", "f_pk_hz")} if hl["class"] != "D-none" else None
    sets = [("map1", *MAP1, "D"), ("map2", *MAP2, "D")] + ([] if a.skip_subgrid else [("subgrid", *SUBGRID, "N")])
    cells = []
    for name, csv_p, dir_p, mode in sets:
        cells += E.load_map_cells(_res(csv_p), _res(dir_p), name, fi["a_ref"], fi, mode)
    b_cells = []
    for c in cells:
        if c["set"] in ("map1", "map2"):
            ep = E.episode_of(c, fi)
            if ep is not None:
                b_cells.append({"set": c["set"], "load": c["load"], "fs": c["fs"], "W_s": c["W_s"], "episode": ep})
    res["rb9b"] = E.rb9b({"v": head["v"], "fs": head["fs"], "episode": head_ep, "W_s": head["W_s"]}, b_cells, ch)
    table = E.variant_table(cells, VARIANTS, A8.classify, fr["rb10_max"], ch)
    res["rb9c"] = E.rb9c(E.variant_table(cells, ["band_30_120"], A8.classify, fr["rb9c_max"], ch), ch)
    head_rows = {v: {"baseline": hl["class"], "variant_class": A8.classify(head["v"], "D", 5.0, head["T_ramp_s"], fi["a_ref"], v)["cls"]} for v in VARIANTS}
    res["rb10"] = E.rb10(head_rows, table, fr, ch)
    # RB9(d), reported only: the two tau runs (MS11_RB9D, Reading A, DL-367) beside the stored 10 ms headline
    res["rb9d"] = E.rb9d({r["tau_ms"]: r for r in by["MS11_RB9D"]}, head, ch)
    if not a.no_hooks:                                        # the 26 carried checks, recomputed from the stored records and compared with the logged words
        res["recompute"] = HK.run_hooks(HK.RealContext(results_root=RES_ROOT if a.results_root else None), ch)

    commits = "; ".join([f"HEAD={git['commit']}", f"criteria-frozen={gate['commit']}"])
    rows = E.assemble_rows(res, logged, fr, ch, input_commits=commits)
    out = Path(a.out)
    out = out if out.is_absolute() else ROOT / out
    E.write_a11_csv(rows, out / "a11_robustness.csv", ch)
    (out / "a11_evaluators.json").write_text(json.dumps({"missing_records": missing, "evaluators": res}, indent=1, default=lambda o: None if hasattr(o, "shape") else str(o)),
                                             encoding="utf-8")
    print(f"wrote {out / 'a11_robustness.csv'} ({len(rows)} rows); missing records {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
