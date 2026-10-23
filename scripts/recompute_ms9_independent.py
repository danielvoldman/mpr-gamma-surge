"""MS9 9j: independent recomputation of the logged MS9 numbers (DL-262 to DL-266). Analysis only: nothing is integrated.

A separate code path. It reads the stored run records (<name>.json with <name>.npz), the launch journals (manifest.csv, run.log) and the
cell and run lists directly. It imports NO function from scripts/report_ms9_9d/9e/9f/9g/9h/9i.py, from analysis/ms9_classify.py or
from analysis/ms9_9i.py. The only analysis code it calls is the frozen classifier (analysis.surge_metrics.classify_mode_d / classify_mode_n,
unchanged) and the criteria gate with the frozen threshold (analysis.a7.frozen_inputs). Class tables, subgrid agreement, P-1, the control
fractions and the D31 boundary are re-derived here from the plain definitions in the decision log (DL-243, DL-254, DL-255), written anew.

  .venv/Scripts/python.exe scripts/recompute_ms9_independent.py [--workers 8]

Prints and writes results/ms9/9j/recompute_report.txt: one line per item, value recomputed, value logged, MATCH or DIFFERENCE. Differences
are reported, never fixed.
"""
import argparse
import collections
import json
import math
import re
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

from mprsurge import config as C
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import surge_metrics as M

ROOT = C.repo_root()
RES = ROOT / "results"
SURGE = ("S+", "S-rel", "S-abs")


def records(d):
    d = Path(d)
    return sorted(p for p in d.rglob("*.json") if not p.name.endswith(".dry.json") and p.with_suffix(".npz").exists())


def load(jp):
    return json.loads(Path(jp).read_text(encoding="utf-8"))


def classify_one(args):
    jp, threshold = args
    rec = load(jp)
    cfg = rec["config"]
    p = cfg["path"]
    kind = cfg["run"]["kind"]
    out = {"name": Path(jp).stem, "dir": Path(jp).parent.name, "status": rec["status"], "wall": rec["wall_time_s"], "dirty": rec["git"]["dirty"],
           "T": float(p["T_ramp_s"]), "Delta": cfg["model"]["Delta"], "tau_d": cfg["model"]["tau_d_ms"],
           "key": list(cfg["seeds"]["spawn_key"]) if cfg["seeds"]["spawn_key"] is not None else None}
    if rec["status"] != "ok":
        out["cls"] = "failed"
        return out
    with np.load(Path(jp).with_suffix(".npz")) as z:
        v = z["v"]
    if not np.all(np.isfinite(v)):
        out["cls"] = "failed"
        return out
    fs = 1000.0 / (cfg["network"]["rate_bin_ms"] if kind == "network" else cfg["solver"]["dt_out_ms"])
    try:
        if kind == "mf":
            res = M.classify_mode_d(v, fs, p["t_on_s"], p["T_ramp_s"], threshold)
        else:
            res = M.classify_mode_n(v, fs, p["t_on_s"], p["T_ramp_s"], threshold)
        out["cls"] = res.cls
    except ValueError:
        out["cls"] = "failed"
    return out


def classify_dir(pool, d, threshold):
    return pool.map(classify_one, [(p, threshold) for p in records(d)], chunksize=4)


REPORT = []


def item(name, got, logged):
    ok = "MATCH" if got == logged else "DIFFERENCE"
    REPORT.append((name, got, logged, ok))
    print(f"{ok:10s} {name}: recomputed {got!r} | logged {logged!r}", flush=True)


def counts(rows):
    return dict(collections.Counter(r["cls"] for r in rows))


def finished_line(log):
    m = None
    for line in Path(log).read_text(encoding="utf-8").splitlines():
        mm = re.search(r"finished: (\d+) ok, wall ([0-9.]+) s", line)
        if mm:
            m = (int(mm.group(1)), float(mm.group(2)))
    return m


def sg(x):
    """T_ramp to 4 significant digits, the form the decision log uses (17.78, 177.8, ...)."""
    return float(f"{x:.4g}")


def key_of(x, nd=10):
    return round(float(x), nd)


def agree_cells(det, runs, cats):
    """runs: {(i,j): [class per seed]}; det: {(i,j): D class}. cats: dict class -> category. Returns (cells agreeing, ties, per-run agreeing).
    The cell class is the modal category over the seeds; a tie for the mode counts as disagreement."""
    agree = ties = per_run = 0
    for c, cl in runs.items():
        cnt = collections.Counter(cats[x] for x in cl)
        top = max(cnt.values())
        modes = [k for k, v in cnt.items() if v == top]
        per_run += sum(1 for x in cl if cats[x] == det[c])
        if len(modes) > 1:
            ties += 1
        elif modes[0] == det[c]:
            agree += 1
    return agree, ties, per_run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    t0 = time.time()
    fi, gate = A7.frozen_inputs(ROOT)
    thr = fi["threshold"]
    rec9i = [p for p in (RES / "ms9/9i").glob("MS9_9i_*.json")]
    thr_9i = load(rec9i[0])["flags"]["threshold"]
    print(f"criteria gate ok (tag {gate['tag']}, {gate['sha256'][:8]}); threshold {thr} ; run record of 9i gives {thr_9i}")
    item("frozen threshold equals the threshold in the 9i run record", thr, thr_9i)

    with Pool(a.workers) as pool:
        fam = {}
        dirs = {"NC1": RES / "S12/NC1", "NC1_cells": RES / "S12/NC1_cells", "NC1_net": RES / "S12/NC1_net",
                "NC1_supp": RES / "S12/supp/NC1_modeN", "NC2": RES / "S12/NC2", "NC3": RES / "S12/NC3",
                "S16_oat": RES / "S16/S16_oat", "S16_lhs": RES / "S16/S16_lhs",
                "S6_P3": RES / "S6/S6_P3", "S6_P4a": RES / "S6/S6_P4a", "S6_P4b": RES / "S6/S6_P4b", "S6_P2ref": RES / "S6/supp/S6_P2ref",
                "map1": RES / "S7/S7_map1", "map2": RES / "S7/S7_map2", "subgrid": RES / "S7/S7_subgrid",
                "control": RES / "S12x/S12x_ctrl_mf", "D31": RES / "D31/D31_half", "S5_p2_linear": RES / "S5/ramp/p2_linear",
                "S5_headline": RES / "S5/ramp/S5ramp", "S12x_NC1_net": RES / "S12x/S12x_NC1_net", "S12x_const_net": RES / "S12x/S12x_const_net"}
        for k, d in dirs.items():
            fam[k] = classify_dir(pool, d, thr)
            print(f"classified {k}: {len(fam[k])} records ({time.time() - t0:.0f} s)", flush=True)

    # ---- 1. run counts, walls, git state -----------------------------------------------------------------------------
    print("\n== run counts and walls per family")
    expect_n = {"NC1": 13, "NC1_cells": 5, "NC1_net": 1, "NC1_supp": 130, "NC2": 13, "NC3": 13, "S16_oat": 14, "S16_lhs": 64, "S6_P3": 12,
                "S6_P4a": 4, "S6_P4b": 4, "S6_P2ref": 2, "map1": 900, "map2": 325, "subgrid": 2250, "control": 2250, "D31": 178,
                "S5_p2_linear": 13, "S5_headline": 1}
    for k, n in expect_n.items():
        item(f"records ok in {k}", sum(1 for r in fam[k] if r["status"] == "ok"), n)
    launches = {"launch_nc1": ("NC1", "NC1_cells", "NC1_net", "NC1_supp"), "launch_s16_s6": ("S16_oat", "S16_lhs", "S6_P3", "S6_P4a", "S6_P4b", "S6_P2ref"),
                "launch_map1": ("map1",), "launch_map2_subgrid": ("map2", "subgrid"), "launch_9g": ("control", "NC2", "NC3"), "launch_9h": ("D31",),
                "launch_s12x": ("S12x_NC1_net", "S12x_const_net")}
    logged_launch = {"launch_nc1": (149, 597.5), "launch_s16_s6": (100, 1734.4), "launch_map1": (900, 14755.0), "launch_map2_subgrid": (2575, 7648.8),
                     "launch_9g": (2276, 1432.8), "launch_9h": (178, 2740.7), "launch_s12x": (19, 524.3)}
    walls = {}
    for L, fams in launches.items():
        man = pd.read_csv(RES / f"ms9/{L}/manifest.csv")
        n_ok_man = int((man["status"] == "ok").sum())
        fin = finished_line(RES / f"ms9/{L}/run.log")
        n_rec = sum(len(fam[f]) for f in fams)
        item(f"{L}: records on disk / manifest rows ok / journal 'finished' (ok count, wall s)", (n_rec, n_ok_man, fin), (logged_launch[L][0], logged_launch[L][0], logged_launch[L]))
        walls[L] = fin[1]
        item(f"{L}: records with git.dirty False", sum(1 for f in fams for r in fam[f] if r["dirty"] is False), n_rec)
        print(f"           {L}: sum of per-run walls {sum(r['wall'] for f in fams for r in fam[f]):.0f} s; launch wall {fin[1]:.1f} s = {fin[1] / 60:.2f} min = {fin[1] / 3600:.3f} h")
    item("NC1 family wall (min, 2 d.p.)", round(walls["launch_nc1"] / 60, 2), 9.96)
    item("S16 + S6 wall (min, 1 d.p.)", round(walls["launch_s16_s6"] / 60, 1), 28.9)
    item("map 1 wall (h, 2 d.p.)", round(walls["launch_map1"] / 3600, 2), 4.10)
    item("map 2 + subgrid wall (h, 2 d.p.)", round(walls["launch_map2_subgrid"] / 3600, 2), 2.12)
    item("9g wall (min, 1 d.p.)", round(walls["launch_9g"] / 60, 1), 23.9)
    item("9h wall (min, 1 d.p.)", round(walls["launch_9h"] / 60, 1), 45.7)

    # ---- 2. map 1 / G5 -------------------------------------------------------------------------------------------------
    print("\n== map 1, G5")
    m1 = {}
    dax = sorted({key_of(r["Delta"]) for r in fam["map1"]})
    tax = sorted({key_of(r["tau_d"]) for r in fam["map1"]})
    item("map 1 axes (Delta values, tau_d values)", (len(dax), len(tax)), (30, 30))
    for r in fam["map1"]:
        m1[(dax.index(key_of(r["Delta"])), tax.index(key_of(r["tau_d"])))] = r["cls"]
    item("map 1 cells mapped", len(m1), 900)
    c1 = collections.Counter(m1.values())
    item("map 1 class counts", dict(c1), {"D-tr": 760, "D-none": 140})
    item("G5: surge-class cells of 900 (threshold 27 = 3%)", (c1["D-tr"], 900, math.ceil(0.03 * 900)), (760, 900, 27))

    # ---- 3. RB4 --------------------------------------------------------------------------------------------------------
    print("\n== RB4")
    nominal = fam["S5_headline"][0]["cls"]
    item("RB4 nominal class (S5 headline run S5ramp_0000_240de3ef73be)", (fam["S5_headline"][0]["name"], nominal), ("S5ramp_0000_240de3ef73be", "D-tr"))
    oat_changed = sum(1 for r in fam["S16_oat"] if r["cls"] != nominal)
    lhs_same = sum(1 for r in fam["S16_lhs"] if r["cls"] == nominal)
    item("RB4 one-at-a-time changed (of 14); limit 2", (oat_changed, len(fam["S16_oat"])), (0, 14))
    item("RB4 hypercube unchanged (of 64); needed 52", (lhs_same, len(fam["S16_lhs"])), (64, 64))
    item("RB4 failed runs", sum(1 for r in fam["S16_oat"] + fam["S16_lhs"] if r["cls"] == "failed"), 0)

    # ---- 4. NC1 --------------------------------------------------------------------------------------------------------
    print("\n== NC1")
    nc1_mf = counts(fam["NC1"] + fam["NC1_cells"])
    item("NC1 mean field (13 T_ramp + 5 cells): class counts", nc1_mf, {"D-none": 18})
    item("NC1 mean field T_ramp values", sorted(sg(r["T"]) for r in fam["NC1"]),
         [1.0, 1.778, 3.162, 5.623, 10.0, 17.78, 31.62, 56.23, 100.0, 177.8, 316.2, 562.3, 1000.0])
    item("NC1 network run class", counts(fam["NC1_net"]), {"S+": 1})
    sup = fam["NC1_supp"]
    non = [r for r in sup if r["cls"] != "NS"]
    item("NC1 supplementary mode N: non-NS runs of 130", (len(non), len(sup)), (6, 130))
    item("NC1 supplementary non-NS classes", counts(non), {"S-rel": 6})
    perT = collections.OrderedDict()
    for T in sorted({sg(r["T"]) for r in sup}):
        g = [r for r in sup if sg(r["T"]) == T]
        perT[T] = (sum(1 for r in g if r["cls"] != "NS"), len(g))
    wlog = {1.0: 0, 1.778: 0, 3.162: 0, 5.623: 0, 10.0: 1, 17.78: 0, 31.62: 0, 56.23: 0, 100.0: 0, 177.8: 1, 316.2: 1, 562.3: 1, 1000.0: 2}
    item("NC1 supplementary non-NS per T_ramp (n = 10 each)", {T: v[0] for T, v in perT.items()}, wlog)
    item("NC1 supplementary seeds per T_ramp", sorted({v[1] for v in perT.values()}), [10])

    # ---- 5. NC2, NC3, S6 ------------------------------------------------------------------------------------------------
    print("\n== NC2, NC3, S6")
    item("NC2 (I = 1) class counts", counts(fam["NC2"]), {"D-tr": 13})
    item("NC2 I = 0 arm (S5 P2 linear mode D) class counts", counts(fam["S5_p2_linear"]), {"D-tr": 13})
    item("NC3 class counts", counts(fam["NC3"]), {"D-none": 13})
    s6 = fam["S6_P3"] + fam["S6_P4a"] + fam["S6_P4b"]
    item("S6 pre-registered 20 runs class counts", counts(s6), {"D-tr": 20})
    item("S6 supplementary P2 references class counts", counts(fam["S6_P2ref"]), {"D-tr": 2})

    # ---- 6. map 2, subgrid, D24, P-1 -----------------------------------------------------------------------------------
    print("\n== map 2, subgrid, D24, P-1")
    item("map 2 class counts", counts(fam["map2"]), {"D-tr": 296, "D-none": 29})
    item("subgrid class counts", counts(fam["subgrid"]), {"S+": 475, "S-rel": 378, "S-abs": 507, "S-sus": 829, "NS": 61})
    det_name = {"D-tr": "surge", "D-sus": "S-sus", "D-none": "NS"}
    det = {c: det_name[m1[c]] for c in m1}
    sub = collections.defaultdict(list)
    for r in fam["subgrid"]:
        sub[(dax.index(key_of(r["Delta"])), tax.index(key_of(r["tau_d"])))].append(r["cls"])
    item("subgrid cells, runs per cell", (len(sub), sorted({len(v) for v in sub.values()})), (225, [10]))
    item("subgrid seed keys are [9, 1, s], s = 0..9", sorted({tuple(r["key"]) for r in fam["subgrid"]}), [(9, 1, s) for s in range(10)])
    dc = collections.Counter(m1[c] for c in sub)
    item("subgrid deterministic classes", dict(dc), {"D-tr": 188, "D-none": 37})
    raw_cat = {k: k for k in ("S+", "S-rel", "S-abs", "S-sus", "NS")}
    # raw reading (DL-242): the modal single class; it agrees if that class belongs to the deterministic class's Table 2.1 set
    agree_raw = ties_raw = 0
    for c, cl in sub.items():
        cnt = collections.Counter(cl)
        top = max(cnt.values())
        modes = [k for k, v in cnt.items() if v == top]
        if len(modes) > 1:
            ties_raw += 1
        elif {"D-tr": modes[0] in SURGE, "D-none": modes[0] == "NS", "D-sus": modes[0] == "S-sus"}[m1[c]]:
            agree_raw += 1
    item("D24 raw classes: cells agreeing (225 cells; 203 needed), ties", (agree_raw, ties_raw), (97, 24))
    cat3 = {"S+": "surge", "S-rel": "surge", "S-abs": "surge", "S-sus": "S-sus", "NS": "NS"}
    ag3, ti3, pr3 = agree_cells(det, sub, cat3)
    item("D24 three categories: cells agreeing, per-run agreeing (of 2250)", (ag3, pr3), (118, 1119))
    ge8 = sum(1 for c, cl in sub.items() if sum(1 for x in cl if cat3[x] == det[c]) >= 8)
    item("cells with at least 8 of 10 seeds agreeing", ge8, 84)
    item("per-run agreement (%, 1 d.p.)", round(100 * pr3 / 2250, 1), 49.7)
    pone = {"S+": "ramp", "S-abs": "ramp", "S-sus": "ramp", "S-rel": "other", "NS": "other"}
    pdet = {c: ("ramp" if m1[c] == "D-tr" else "other") for c in m1}
    ag1, ti1, pr1 = agree_cells(pdet, sub, pone)
    item("P-1: cells agreeing, ties, per-run agreeing", (ag1, ti1, pr1), (173, 16, 1591))
    d_tr_cells = [c for c in sub if m1[c] == "D-tr"]
    d_no_cells = [c for c in sub if m1[c] == "D-none"]
    a_tr, _, _ = agree_cells({c: pdet[c] for c in d_tr_cells}, {c: sub[c] for c in d_tr_cells}, pone)
    a_no, _, _ = agree_cells({c: pdet[c] for c in d_no_cells}, {c: sub[c] for c in d_no_cells}, pone)
    item("P-1 by deterministic class: D-tr cells agreeing of 188, D-none of 37", (a_tr, a_no), (171, 2))
    item("P-1 cells needed (90% of 225, rounded up)", math.ceil(0.9 * 225), 203)

    # ---- 7. control -----------------------------------------------------------------------------------------------------
    print("\n== control (M9-22)")
    item("control class counts", counts(fam["control"]), {"NS": 1104, "S+": 28, "S-abs": 21, "S-rel": 1095, "S-sus": 2})
    ctrl = collections.defaultdict(list)
    for r in fam["control"]:
        ctrl[(dax.index(key_of(r["Delta"])), tax.index(key_of(r["tau_d"])))].append(r["cls"])
    item("control cells, runs per cell", (len(ctrl), sorted({len(v) for v in ctrl.values()})), (225, [10]))
    item("control cells equal the subgrid cells", set(ctrl) == set(sub), True)
    for nm, grp in (("D-tr", d_tr_cells), ("D-none", d_no_cells)):
        for tag, src in (("control", ctrl), ("ramp subgrid", sub)):
            cl = [x for c in grp for x in src[c]]
            n = len(cl)
            f = (round(100 * sum(1 for x in cl if x == "NS") / n, 2), round(100 * sum(1 for x in cl if x in SURGE) / n, 2), round(100 * sum(1 for x in cl if x == "S-sus") / n, 2))
            logged = {("D-tr", "control"): (53.46, 46.44, 0.11), ("D-tr", "ramp subgrid"): (2.50, 58.78, 38.72),
                      ("D-none", "control"): (26.76, 73.24, 0.00), ("D-none", "ramp subgrid"): (3.78, 68.92, 27.30)}[(nm, tag)]
            item(f"{nm} cells, {tag}: percent NS / surge / S-sus", f, logged)
            rl = round(100 * sum(1 for x in cl if pone[x] == "ramp") / n, 2)
            item(f"{nm} cells, {tag}: percent ramp-linked (S+, S-abs, S-sus)", rl, {("D-tr", "control"): 1.12, ("D-tr", "ramp subgrid"): 80.64,
                                                                                 ("D-none", "control"): 8.11, ("D-none", "ramp subgrid"): 79.73}[(nm, tag)])
    allc = [x for cl in ctrl.values() for x in cl]
    allr = [x for cl in sub.values() for x in cl]
    pct = lambda L, k: 100.0 * sum(1 for x in L if x == k) / len(L)
    item("DL-250 control rates S+ / S-abs / S-sus (percent, 1 d.p.)", tuple(round(pct(allc, k), 1) for k in ("S+", "S-abs", "S-sus")), (1.2, 0.9, 0.1))
    item("DL-250 ramp rates S+ / S-abs / S-sus (percent, as logged: 21, 22.5, 37)", (round(pct(allr, "S+")), round(pct(allr, "S-abs"), 1), round(pct(allr, "S-sus"))), (21, 22.5, 37))
    ge8c = [c for c, cl in ctrl.items() if sum(1 for x in cl if x == "NS") >= 8]
    item("control cells with at least 8 of 10 seeds NS; all D-tr", (len(ge8c), all(m1[c] == "D-tr" for c in ge8c)), (12, True))

    # ---- 8. D31 ---------------------------------------------------------------------------------------------------------
    print("\n== D31")
    d31 = fam["D31"]
    item("D31 nodes, class counts", counts(d31), {"D-tr": 112, "D-none": 66})
    lat = pd.read_csv(ROOT / "configs/ms9/runlists/cells_d31.csv")
    look = {(key_of(r.Delta, 12), key_of(r.tau_d_ms, 12)): (int(r.p), int(r.q)) for r in lat.itertuples()}
    node = {(2 * i, 2 * j): c for (i, j), c in m1.items()}
    miss = 0
    for r in d31:
        k = (key_of(r["Delta"], 12), key_of(r["tau_d"], 12))
        if k not in look:
            miss += 1
            continue
        node[look[k]] = r["cls"]
    item("D31 records matched to a lattice node by their own Delta and tau_d", (len(d31) - miss, miss), (178, 0))
    coarse = []
    for (i, j), c in m1.items():
        for di, dj in ((1, 0), (0, 1)):
            n2 = (i + di, j + dj)
            if n2 in m1 and m1[n2] != c:
                coarse.append(((i + n2[0]) / 2.0, (j + n2[1]) / 2.0, (i, j), n2))
    item("D31 coarse boundary edges", len(coarse), 46)
    half = []
    for (p, q), c in node.items():
        for dp, dq in ((1, 0), (0, 1)):
            n2 = (p + dp, q + dq)
            if n2 in node and node[n2] != c:
                half.append(((p + n2[0]) / 4.0, (q + n2[1]) / 4.0))
    item("D31 refined half-edges", len(half), 85)
    cells_touch = collections.defaultdict(float)
    for (mi, mj, c1_, c2_) in coarse:
        d = min(math.hypot(mi - h[0], mj - h[1]) for h in half)
        for cc in (c1_, c2_):
            cells_touch[cc] = max(cells_touch[cc], d)
    item("D31 boundary-touching cells; those with every coarse edge within 1 cell", (len(cells_touch), sum(1 for v in cells_touch.values() if v < 1.0)), (62, 62))
    item("D31 per-cell maximum distance (set of values, 4 d.p.)", sorted({round(v, 4) for v in cells_touch.values()}), [0.25])
    far = max(min(math.hypot(h[0] - c[0], h[1] - c[1]) for c in coarse) for h in half)
    item("D31 largest distance of a refined half-edge to the nearest coarse edge midpoint (4 d.p.)", round(far, 4), 0.9014)
    item("D31 mixed 2 x 2 blocks", sum(1 for i in range(29) for j in range(29) if len({m1[(i, j)], m1[(i + 1, j)], m1[(i, j + 1)], m1[(i + 1, j + 1)]}) > 1), 45)

    n_diff = sum(1 for r in REPORT if r[3] == "DIFFERENCE")
    summary = f"\n{len(REPORT)} items, {len(REPORT) - n_diff} MATCH, {n_diff} DIFFERENCE ({time.time() - t0:.0f} s)"
    print(summary)
    out = ROOT / "results/ms9/9j"
    out.mkdir(parents=True, exist_ok=True)
    lines = [f"{ok}\t{name}\trecomputed={got!r}\tlogged={logged!r}" for name, got, logged, ok in REPORT]
    (out / "recompute_report.txt").write_text("\n".join(lines) + summary + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
