"""MS9 9g report: M9-22 control (S12x_ctrl_mf) against the ramp subgrid, baseline-odds spread of the ramp subgrid runs, NC2 and NC3 tables, A9 g/h counts
(DL-242 to DL-248). Analysis only: integrates nothing, adds no label to the pre-registered scheme, feeds no gate. Facts only; no verdicts.

  report_ms9_9g.py [--out-dir results/ms9/9g]

Part 1 completion of the 9g launch (control 2,250 + NC2 13 + NC3 13): journal, records on disk, commit and git.dirty of every record.
Part 2 control: per-cell class counts; by deterministic class (map-1 class of the cell) the fraction of runs in NS, surge class (S+, S-rel, S-abs), S-sus,
        for the control and for the ramp subgrid runs; cells with >= 8 of 10 control seeds NS but the ramp runs not (two readings of "not", both printed).
Part 3 baseline spread of the 2,250 ramp subgrid runs: number of baseline windows and max/min of the baseline odds P_G / P_non-G (the quantity the
        relative test multiplies by 2.0), median, 90th percentile, fraction at or above 2.0.
Part 4 NC2 (I = 0: the S5 P2 linear mode-D runs, results/S5/ramp/p2_linear, not re-run; I = 1: results/S12/NC2) and NC3 (results/S12/NC3): class, onset,
        delay (eta at onset minus eta_H), duration per T_ramp.
Part 5 A9 descriptors g and h on map 1 and map 2 (post hoc, DL-244; a to f not renumbered): g = an A4 Hopf point exists at the cell's J0 (the map's own
        Delta, tau_d) and the path spends no time in the oscillatory region (time inside = 0); h = the episode is rejected by the damped (D8) clause.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from mprsurge import config as C
from mprsurge import ramps
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import a9 as A9
from mprsurge.analysis import ms9_classify as MCL
from mprsurge.analysis import ms9_runlist as RL
from mprsurge.analysis import surge_metrics as M
from mprsurge.units import s_to_tau


def sha(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def category(cls: str) -> str:
    """The three Table 2.1 categories for a mode-N class: surge (S+, S-rel, S-abs), S-sus, NS."""
    return "surge" if M.is_surge_class(cls) else cls


def fractions(classes: list[str]) -> dict:
    n = len(classes)
    c = collections.Counter(category(x) for x in classes)
    return {"n": n, "NS": c.get("NS", 0), "surge": c.get("surge", 0), "S-sus": c.get("S-sus", 0),
            "other": n - c.get("NS", 0) - c.get("surge", 0) - c.get("S-sus", 0)}


def pct(a: int, n: int) -> str:
    return f"{100 * a / n:6.2f}%" if n else "   n/a"


def baseline_stats(json_path) -> dict:
    """Baseline windows and max/min of the baseline odds P_G / P_non-G (classify_mode_n's own window series and baseline mask)."""
    jp = Path(json_path)
    rec = json.loads(jp.read_text(encoding="utf-8"))
    cfg = rec["config"]
    with np.load(jp.with_suffix(".npz")) as z:
        v = np.asarray(z["v"], float)
    W, step = M.window_for_ramp(float(cfg["path"]["T_ramp_s"]))
    tc, p_g, p_tot, p_ng, fpk = M._window_series(v, MCL.fs_of(cfg), W, step, M.G_BAND)
    bm = M.baseline_windows(tc, W, cfg["path"]["t_on_s"], M.BASELINE_S)
    odds = (p_g / p_ng)[bm]
    return {"run": jp.stem, "W_s": float(W), "n_baseline": int(bm.sum()), "odds_min": float(odds.min()), "odds_max": float(odds.max()),
            "ratio": float(odds.max() / odds.min())}


def eta_delay(cfg: dict, onset_s) -> float:
    """eta(onset) - eta_H on the run's own path (the Table 2.1 delay metric; eta evaluated at the onset, no grid interpolation)."""
    if onset_s is None or not np.isfinite(onset_s):
        return float("nan")
    path = ramps.make_path(cfg)
    return float(path.eta(s_to_tau(float(onset_s), cfg["model"]["tau_ms"]))) - float(cfg["path"]["eta_H"])      # the path's own eta at the onset


def fnum(x, f="{:.3f}") -> str:
    return "-" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f.format(x)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="report_ms9_9g")
    ap.add_argument("--out-dir", default="results/ms9/9g")
    ap.add_argument("--journal", default="results/ms9/launch_9g/manifest.csv")
    ap.add_argument("--map1-csv", default="results/ms9/9e/map1_classes.csv")
    ap.add_argument("--map2-csv", default="results/ms9/9f/map2_classes.csv")
    ap.add_argument("--sub-csv", default="results/ms9/9f/subgrid_classes.csv")
    args = ap.parse_args(argv)
    root = C.repo_root()
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    fi, gate = A7.frozen_inputs()
    h, thr, a_ref = fi["grid_step"], fi["threshold"], fi["a_ref"]
    print(f"criteria gate ok: tag {gate['tag']}, threshold {thr:.6f}, A_ref {a_ref:.6f}")

    # ---- part 1: completion ------------------------------------------------------------------------------------------------
    rows = read(root / args.journal)
    st = collections.Counter(r["status"] for r in rows)
    log = (root / args.journal).with_name("run.log").read_text(encoding="utf-8").splitlines()
    fin = [x.split("INFO ")[-1] for x in log if "finished:" in x]
    expected = {r["name"] for n in ("S12x_ctrl_mf", "NC2", "NC3") for r in RL.expand(n)}
    names = [r["name"] for r in rows]
    print(f"\nPART 1 completion: journal rows {len(rows)}, unique {len(set(names))}, status {dict(st)}; expected {len(expected)}; "
          f"missing {len(expected - set(names))}; not expected {len(set(names) - expected)}")
    print(f"launch lines ('runs from') {sum('runs from' in x for x in log)}; finished: {fin}")
    ctrl_recs = [(jp, json.loads(jp.read_text(encoding='utf-8'))) for jp in MCL.record_files(root / "results/S12x/S12x_ctrl_mf")]
    nc2_recs = [(jp, json.loads(jp.read_text(encoding="utf-8"))) for jp in MCL.record_files(root / "results/S12/NC2")]
    nc3_recs = [(jp, json.loads(jp.read_text(encoding="utf-8"))) for jp in MCL.record_files(root / "results/S12/NC3")]
    gits = collections.Counter((r["git"]["commit"][:7], r["git"]["dirty"], r["status"]) for _, r in ctrl_recs + nc2_recs + nc3_recs)
    print(f"records on disk: control {len(ctrl_recs)}, NC2 {len(nc2_recs)}, NC3 {len(nc3_recs)}; (commit, git.dirty, status): {dict(gits)}")
    if st.get("ok", 0) != len(expected) or len(ctrl_recs) != 2250 or len(nc2_recs) != 13 or len(nc3_recs) != 13:
        print("STOP: a run failed or is missing; no rerun, no further analysis")
        return 4

    cells1 = [c for c in RL.load_cells() if c["kind"] == "map1"]
    ij1 = {(round(c["Delta"], 12), round(c["tau_d_ms"], 12)): tuple(c["ij"]) for c in cells1}
    det = {(int(r["i"]), int(r["j"])): r["class"] for r in read(root / args.map1_csv)}

    # ---- part 2: control ---------------------------------------------------------------------------------------------------
    print("\nPART 2 control (M9-22; mean-field mode N, start state held; EXPLORATORY, feeds no gate)")
    ctrl = []
    for jp, rec in ctrl_recs:
        cfg = rec["config"]
        ij = ij1[(round(cfg["model"]["Delta"], 12), round(cfg["model"]["tau_d_ms"], 12))]
        r = MCL.classify_record(jp, fi)
        ctrl.append({"run": jp.stem, "i": ij[0], "j": ij[1], "seed": r["seed"], "class": r["class"], "det": det[ij], "W_s": r["W_s"],
                     "git_commit": rec["git"]["commit"], "git_dirty": rec["git"]["dirty"]})
    ctrl.sort(key=lambda r: (r["i"], r["j"], r["seed"]))
    write_csv(out_dir / "control_classes.csv", ctrl)
    ramp = read(root / args.sub_csv)
    print("input hashes: subgrid_classes.csv", sha(root / args.sub_csv)[:8], " map1_classes.csv", sha(root / args.map1_csv)[:8])
    print("class counts over", len(ctrl), "control runs:", dict(sorted(collections.Counter(r["class"] for r in ctrl).items())))
    cc, rc = collections.defaultdict(list), collections.defaultdict(list)
    for r in ctrl:
        cc[(r["i"], r["j"])].append(r["class"])
    for r in ramp:
        rc[(int(r["i"]), int(r["j"]))].append(r["class"])
    cells_out = []
    for c in sorted(cc):
        cells_out.append({"i": c[0], "j": c[1], "det": det[c], "n_control": len(cc[c]), "n_ramp": len(rc[c]),
                          "control_counts": json.dumps(dict(sorted(collections.Counter(cc[c]).items()))),
                          "ramp_counts": json.dumps(dict(sorted(collections.Counter(rc[c]).items()))),
                          "control_NS": sum(x == "NS" for x in cc[c]), "ramp_NS": sum(x == "NS" for x in rc[c])})
    write_csv(out_dir / "control_cells.csv", cells_out)
    print("cells", len(cc), "control seeds per cell", dict(collections.Counter(len(v) for v in cc.values())), "ramp seeds per cell",
          dict(collections.Counter(len(v) for v in rc.values())))
    print("\nfraction of runs by deterministic class (surge = S+, S-rel, S-abs):")
    print(f"  {'det':7s} {'cells':>5s} {'runs':>5s} | {'':8s}{'NS':>9s} {'surge':>9s} {'S-sus':>9s} {'other':>6s}")
    for d in ("D-tr", "D-none", "D-sus"):
        cs = [c for c in cc if det[c] == d]
        if not cs:
            continue
        for lab, src in (("control", cc), ("ramp", rc)):
            f = fractions([x for c in cs for x in src[c]])
            print(f"  {d:7s} {len(cs):5d} {f['n']:5d} | {lab:8s}{pct(f['NS'], f['n']):>9s} {pct(f['surge'], f['n']):>9s} {pct(f['S-sus'], f['n']):>9s} {f['other']:6d}"
                  f"   (counts NS {f['NS']}, surge {f['surge']}, S-sus {f['S-sus']})")
    ge8 = [c for c in cc if sum(x == "NS" for x in cc[c]) >= 8]
    a = [c for c in ge8 if sum(x == "NS" for x in rc[c]) < 8]
    b = [c for c in ge8 if sum(x == "NS" for x in rc[c]) == 0]
    print(f"\ncells with >= 8 of 10 control seeds NS: {len(ge8)} (by det: {dict(collections.Counter(det[c] for c in ge8))})")
    print(f"  of these, ramp runs not >= 8 of 10 NS: {len(a)} (by det {dict(collections.Counter(det[c] for c in a))}); "
          f"ramp runs with no NS run at all: {len(b)} (by det {dict(collections.Counter(det[c] for c in b))})")
    ge8r = [c for c in rc if sum(x == "NS" for x in rc[c]) >= 8]
    print(f"cells with >= 8 of 10 ramp seeds NS: {len(ge8r)}")

    # ---- part 3: baseline spread -------------------------------------------------------------------------------------------
    print("\nPART 3 baseline-odds spread of the ramp subgrid runs (max/min of P_G / P_non-G over the baseline windows)")
    bs = [baseline_stats(jp) for jp in MCL.record_files(root / "results/S7/S7_subgrid")]
    write_csv(out_dir / "ramp_baseline_spread.csv", sorted(bs, key=lambda r: r["run"]))
    nb = np.array([b["n_baseline"] for b in bs])
    ratio = np.array([b["ratio"] for b in bs])
    print(f"runs {len(bs)}; W {sorted({b['W_s'] for b in bs})} s; baseline windows per run: {dict(sorted(collections.Counter(nb.tolist()).items()))}")
    print(f"max/min ratio: median {np.median(ratio):.4f}, 90th percentile {np.percentile(ratio, 90):.4f}, min {ratio.min():.4f}, max {ratio.max():.4f}; "
          f"fraction >= 2.0: {np.mean(ratio >= 2.0):.4f} ({int(np.sum(ratio >= 2.0))} of {len(bs)})")

    # ---- part 4: NC2, NC3 --------------------------------------------------------------------------------------------------
    print("\nPART 4 NC2 and NC3 (mode D)")
    s5 = {}
    for jp in MCL.record_files(root / "results/S5/ramp/p2_linear"):
        rec = json.loads(jp.read_text(encoding="utf-8"))
        r = MCL.classify_record(jp, fi)
        s5[round(float(rec["config"]["path"]["T_ramp_s"]), 6)] = {**r, "delay": eta_delay(rec["config"], r["onset_s"]), "git": rec["git"]["commit"][:7]}
    nc2 = {}
    for jp, rec in nc2_recs:
        r = MCL.classify_record(jp, fi)
        nc2[round(float(rec["config"]["path"]["T_ramp_s"]), 6)] = {**r, "delay": eta_delay(rec["config"], r["onset_s"])}
    nc3 = {}
    for jp, rec in nc3_recs:
        r = MCL.classify_record(jp, fi)
        nc3[round(float(rec["config"]["path"]["T_ramp_s"]), 6)] = r
    Ts = sorted(nc2)
    print(f"T_ramp grid: NC2 {len(nc2)}, S5 P2 linear {len(s5)} (all 13 present: {all(t in s5 for t in Ts)}), NC3 {len(nc3)}")
    print(f"\nNC2 (I_amp 1) against I = 0 (S5 P2 linear)         | I = 0: class onset_s delay_eta duration_s | I = 1: class onset_s delay_eta duration_s")
    t_rows = []
    for t in Ts:
        a0, a1 = s5.get(t), nc2[t]
        print(f"  T_ramp {t:9.4f} s | I=0 {a0['class'] if a0 else '-':7s} {fnum(a0['onset_s']) if a0 else '-':>9s} {fnum(a0['delay']) if a0 else '-':>8s} "
              f"{fnum(a0['duration_s']) if a0 else '-':>9s} | I=1 {a1['class']:7s} {fnum(a1['onset_s']):>9s} {fnum(a1['delay']):>8s} {fnum(a1['duration_s']):>9s}")
        t_rows.append({"T_ramp_s": t, "I0_class": a0["class"] if a0 else "", "I0_onset_s": a0["onset_s"] if a0 else "", "I0_delay_eta": a0["delay"] if a0 else "",
                       "I0_duration_s": a0["duration_s"] if a0 else "", "I1_class": a1["class"], "I1_onset_s": a1["onset_s"], "I1_delay_eta": a1["delay"],
                       "I1_duration_s": a1["duration_s"], "I1_run": a1["run"], "I0_run": a0["run"] if a0 else ""})
    write_csv(out_dir / "nc2_table.csv", t_rows)
    print("\nNC3 (J from J0 to -40, linear, same T_ramp and t_on as the eta fall)")
    n3_rows = []
    for t in sorted(nc3):
        r = nc3[t]
        print(f"  T_ramp {t:9.4f} s | {r['class']:7s} reason: {r['reason'] or '-'}")
        n3_rows.append({"T_ramp_s": t, "class": r["class"], "reason": r["reason"], "run": r["run"]})
    write_csv(out_dir / "nc3_table.csv", n3_rows)
    print(f"NC2 classes: {dict(collections.Counter(nc2[t]['class'] for t in Ts))}; I = 0 classes: {dict(collections.Counter(s5[t]['class'] for t in Ts if t in s5))}; "
          f"NC3 classes: {dict(collections.Counter(r['class'] for r in nc3.values()))}")

    # ---- part 5: A9 g and h -----------------------------------------------------------------------------------------------
    print("\nPART 5 A9 descriptors g and h (post hoc; a to f not renumbered; DL-244)")
    out5 = []
    # map 1: stored table, cell J0 from the cell list, damped clause from the stored record
    m1 = read(root / args.map1_csv)
    cell_of = {tuple(c["ij"]): c for c in cells1}
    m1_rows = []
    for r in m1:
        ij = (int(r["i"]), int(r["j"]))
        c = cell_of[ij]
        row = {"map": 1, "key": f"{ij[0]},{ij[1]}", "class": r["class"], "surge": r["surge"] == "True", "labels_a_f": r["labels_all"],
               "primary_a_f": r["label_primary"], "time_inside_s": float(r["time_inside_s"])}
        hp = A9.hopf_point(float(c["J0"]), float(c["Delta"]), float(c["tau_d_ms"]), 10.0)
        row["hopf"] = hp is not None
        if not row["surge"]:
            rr = MCL.classify_record(root / "results/S7/S7_map1" / (r["run"] + ".json"), fi)
            row["reason"] = rr["reason"]
        else:
            row["reason"] = ""
        m1_rows.append(row)
    m2_rows = []
    for r in read(root / args.map2_csv):
        m2_rows.append({"map": 2, "key": f"{r['i']},{r['k']}", "class": r["class"], "surge": r["surge"] == "True", "labels_a_f": r["labels_all"],
                        "primary_a_f": r["label_primary"], "time_inside_s": float(r["time_inside_s"]), "hopf": r["hopf_f_hz"] != "", "reason": r["reason"]})
    for mp, rws in ((1, m1_rows), (2, m2_rows)):
        non = [x for x in rws if not x["surge"]]
        for x in non:
            x["g"] = bool(x["hopf"] and x["time_inside_s"] == 0.0)
            x["h"] = bool(x["class"] == "D-none" and x["reason"] == "damped (D8)")
        out5 += non
        g, hh = [x for x in non if x["g"]], [x for x in non if x["h"]]
        unl = [x for x in non if not x["labels_a_f"]]
        print(f"  map {mp}: non-surge cells {len(non)}; unlabelled under a to f {len(unl)}")
        print(f"    g (Hopf point at the cell's J0, no time in the oscillatory region): any-label {len(g)}; among the unlabelled {sum(x['g'] for x in unl)}")
        print(f"    h (rejected by the damped D8 clause): any-label {len(hh)}; among the unlabelled {sum(x['h'] for x in unl)}")
        print(f"    g and h together {sum(x['g'] and x['h'] for x in non)}; neither g nor h and unlabelled under a to f {sum((not x['g']) and (not x['h']) for x in unl)}")
        print(f"    g or h among cells with a to f labels: g {sum(x['g'] for x in non if x['labels_a_f'])}, h {sum(x['h'] for x in non if x['labels_a_f'])}")
        print(f"    reason counts of the non-surge cells: {dict(collections.Counter(x['reason'] or '-' for x in non))}")
    write_csv(out_dir / "a9_gh.csv", [{k: x[k] for k in ("map", "key", "class", "labels_a_f", "primary_a_f", "time_inside_s", "hopf", "reason", "g", "h")} for x in out5])
    print(f"\nwritten {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
