"""MS9 9d report: RB4 facts (S16) and the S6 table, from class tables written by scripts/classify_ms9.py (DL-228). Analysis only.

  report_ms9_9d.py --s16 CLASSES.csv --s5 CLASSES.csv [--s6 CLASSES.csv] --out-dir results/ms9/9d

RB4 (frozen, configs/robustness_criteria.yaml): nominal class = the S5 headline class (P2 linear, T_ramp 120 s, mode D). "Unchanged" = the same
class string; a run that failed counts as changed and is listed separately. Pass: at most 2 of the 14 one-at-a-time runs changed AND at least
52 of the 64 hypercube points unchanged. The numbers are pre-registered (M9-15); no new criterion here.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from mprsurge import config as C
from mprsurge.analysis import ms9_runlist as RL

OAT_MAX_CHANGED, LHS_MIN_UNCHANGED, LHS_N = 2, 52, 64
PARAM_KEYS = {"eta_start": "path.eta_start", "eta_peak": "path.eta_peak", "J0": "model.J", "Delta": "model.Delta",
              "tau_d_ms": "model.tau_d_ms", "J_lag_frac": "path.J_lag_frac", "J_T_frac": "path.J_T_frac"}


def read(path) -> list[dict]:
    p = Path(path)
    with open(p if p.is_absolute() else C.repo_root() / p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def nominal_class(s5_rows: list[dict]) -> tuple[str, dict]:
    r = [x for x in s5_rows if x["path_name"] == "path_hypoxia" and abs(float(x["T_ramp_s"]) - 120.0) < 1e-9 and x["mode"] == "D"]
    if len(r) != 1:
        raise SystemExit(f"expected one S5 P2 linear 120 s mode-D record, found {len(r)}")
    return r[0]["class"], r[0]


def oat_change(over: dict, nom: dict) -> tuple[str, str]:
    diff = [(k, over[v], nom[v]) for k, v in PARAM_KEYS.items() if abs(float(over[v]) - float(nom[v])) > 1e-12]
    if len(diff) != 1:
        raise SystemExit(f"one-at-a-time run changes {len(diff)} parameters: {diff}")
    k, v, v0 = diff[0]
    return k, ("+10%" if float(v) > float(v0) else "-10%")


def rb4(s16_rows: list[dict], nom_cls: str) -> tuple[dict, list[dict]]:
    meta = {r["name"]: r for r in read(Path(RL.RUNLIST_DIR) / "runlist_S16.csv")}
    nom = RL.nominal()
    nom_over = {PARAM_KEYS["eta_start"]: nom["eta_start"], PARAM_KEYS["eta_peak"]: nom["eta_peak"], PARAM_KEYS["J0"]: nom["J0"],
                PARAM_KEYS["Delta"]: nom["Delta"], PARAM_KEYS["tau_d_ms"]: nom["tau_d_ms"], PARAM_KEYS["J_lag_frac"]: nom["J_lag_frac"],
                PARAM_KEYS["J_T_frac"]: nom["J_T_frac"]}
    rows = []
    for r in s16_rows:
        m = meta[r["run"]]
        over = json.loads(m["overrides"])
        grp = "oat" if m["family"] == "S16_oat" else "lhs"
        param, direction = oat_change(over, nom_over) if grp == "oat" else ("", "")
        failed = r["class"] == "failed" or r["status"] != "ok"
        rows.append({"run": r["run"], "group": grp, "index": int(m["index"]), "parameter": param, "direction": direction, "class": r["class"],
                     "failed": failed, "changed": failed or r["class"] != nom_cls, "onset_s": r.get("onset_s", ""), "f_pk_hz": r.get("f_pk_hz", ""),
                     "duration_s": r.get("duration_s", "")})
    oat = [x for x in rows if x["group"] == "oat"]
    lhs = [x for x in rows if x["group"] == "lhs"]
    res = {"nominal_class": nom_cls, "n_oat": len(oat), "n_lhs": len(lhs), "oat_changed": sum(x["changed"] for x in oat),
           "oat_failed": sum(x["failed"] for x in oat), "lhs_unchanged": sum(not x["changed"] for x in lhs),
           "lhs_failed": sum(x["failed"] for x in lhs)}
    res["oat_pass"] = res["n_oat"] == 14 and res["oat_changed"] <= OAT_MAX_CHANGED
    res["lhs_pass"] = res["n_lhs"] == LHS_N and res["lhs_unchanged"] >= LHS_MIN_UNCHANGED
    res["rb4_pass"] = res["oat_pass"] and res["lhs_pass"]
    return res, rows


def fmt(x) -> str:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return "-"
    return "-" if v != v else f"{v:.4g}"


def s6_table(s6_rows, p2_rows, ref_rows) -> list[dict]:
    out = []
    for r in s6_rows:
        a = r["run"].split("_")[1]
        label = {"P3": f"P3 I_amp {json.loads(_over(r['run']))['path.I_amp']}", "P4a": "P4a", "P4b": "P4b"}[a]
        out.append((label, float(r["T_ramp_s"]), "pre-registered", r))
    for r in p2_rows:
        if r["path_name"] == "path_hypoxia" and r["mode"] == "D" and round(float(r["T_ramp_s"])) in (10, 120):
            out.append(("P2 (S5 linear)", float(r["T_ramp_s"]), "S5", r))
    for r in ref_rows:
        out.append(("P2 (supplementary ref)", float(r["T_ramp_s"]), "supplementary", r))
    return [{"path": a, "T_ramp_s": T, "source": s, "class": r["class"], "onset_s": r.get("onset_s", ""), "f_pk_hz": r.get("f_pk_hz", ""),
             "duration_s": r.get("duration_s", ""), "run": r["run"]} for a, T, s, r in sorted(out, key=lambda t: (t[0], t[1]))]


_META: dict = {}


def _over(name: str) -> str:
    if not _META:
        for f in ("runlist_S6.csv",):
            _META.update({r["name"]: r["overrides"] for r in read(Path(RL.RUNLIST_DIR) / f)})
    return _META[name]


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="report_ms9_9d")
    ap.add_argument("--s16", required=True)
    ap.add_argument("--s5", required=True, help="class table of results/S5/ramp/p2_linear")
    ap.add_argument("--s6", default=None, help="class table of results/S6 (pre-registered and supplementary)")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args(argv)
    out = Path(args.out_dir)
    out = out if out.is_absolute() else C.repo_root() / out
    out.mkdir(parents=True, exist_ok=True)
    s5 = read(args.s5)
    nom_cls, nom_row = nominal_class(s5)
    print(f"nominal (S5 headline, P2 linear, 120 s, mode D): class {nom_cls}, onset {fmt(nom_row.get('onset_s'))} s, f_pk {fmt(nom_row.get('f_pk_hz'))} Hz")
    res, rows = rb4(read(args.s16), nom_cls)
    write_csv(out / "rb4_runs.csv", rows)
    (out / "rb4_summary.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res))
    print("\nS16 class counts: " + ", ".join(f"{g} {c}={n}" for g in ("oat", "lhs") for c, n in
                                              sorted({(x['class']): sum(1 for y in rows if y['group'] == g and y['class'] == x['class']) for x in rows
                                                      if x['group'] == g}.items())))
    print("\nOne-at-a-time runs that changed (parameter, direction, class):")
    for x in rows:
        if x["group"] == "oat" and x["changed"]:
            print(f"  {x['run']}: {x['parameter']} {x['direction']} -> {x['class']}{' (FAILED)' if x['failed'] else ''}")
    print("Hypercube points that changed (index, class):")
    for x in rows:
        if x["group"] == "lhs" and x["changed"]:
            print(f"  {x['run']}: -> {x['class']}{' (FAILED)' if x['failed'] else ''}")
    if args.s6:
        s6 = read(args.s6)
        pre = [r for r in s6 if r["run"].startswith(("S6_P3", "S6_P4"))]
        ref = [r for r in s6 if r["run"].startswith("S6_P2ref")]
        tab = s6_table(pre, s5, ref)
        write_csv(out / "s6_table.csv", tab)
        print("\nS6 table (class, onset s, f_pk Hz, duration s):")
        for t in tab:
            print(f"  {t['path']:<24} {t['T_ramp_s']:>6g} s  {t['source']:<14} {t['class']:<8} onset {fmt(t['onset_s']):>8} f_pk {fmt(t['f_pk_hz']):>8} dur {fmt(t['duration_s']):>8}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
