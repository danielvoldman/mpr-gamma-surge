"""MS13 13q: independent recomputation of the take-home numbers and the main drawn quantities of F1 to F6 and FS1 to FS5 (docs/ms13_independent_plan.md).

  .venv/Scripts/python.exe scripts/ms13_independent.py            # prints the number of rows per figure; writes nothing

A SEPARATE code path: own readers of the stored files under results/ (json, numpy, csv, parquet); it imports nothing of mprsurge.plotting (no figures.py, figprov, claim_labels,
captions, style, nordlie and no figure data step). Shared frozen code, each use marked in the 'shared' field of the row it feeds: the frozen criteria loader and the frozen
surge classifier (mprsurge.analysis.a7.frozen_inputs, mprsurge.analysis.surge_metrics). compute() returns rows; it writes nothing. The comparison with the printed and drawn values
is scripts/ms13_independent_compare.py (the only place that may import the figure data steps).

A row: figure, id, quantity, value (int, float, str or list), tol (None = exact; a float = absolute; ('rel', x) = relative), shared ('' = independent; otherwise the reason),
source (stored file and key), printed (None, or (regex, group) applied to the figure's take-home text), drawn (None, or a Python expression over the figure's drawn dict d).
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

FIGURES = ("F1", "F2", "F3", "F4", "F5", "F6", "FS1", "FS2", "FS3", "FS4", "FS5")
SURGE = ("S+", "S-rel", "S-abs")                       # the frozen Table 2.1 surge classes (read from the stored class words; the set is the frozen one)
CLASSES = ("S+", "S-rel", "S-abs", "S-sus", "NS")
ROOT = Path(__file__).resolve().parents[1]


class Ctx:
    """Reads stored files from <root>/results; caches. root is replaceable (tests alter a copy)."""

    def __init__(self, root=None):
        self.root = Path(root) if root is not None else ROOT
        self.res = self.root / "results"
        self._c: dict = {}

    def json(self, rel):
        if ("j", rel) not in self._c:
            self._c[("j", rel)] = json.loads((self.res / rel).read_text(encoding="utf-8"))
        return self._c[("j", rel)]

    def npz(self, rel):
        if ("n", rel) not in self._c:
            with np.load(self.res / rel, allow_pickle=True) as z:
                self._c[("n", rel)] = {k: z[k] for k in z.files}
        return self._c[("n", rel)]

    def pq(self, rel):
        if ("p", rel) not in self._c:
            import pandas as pd
            self._c[("p", rel)] = pd.read_parquet(self.res / rel)
        return self._c[("p", rel)]

    def csv(self, rel, delimiter=","):
        if ("c", rel) not in self._c:
            with open(self.res / rel, newline="", encoding="utf-8") as fh:
                self._c[("c", rel)] = list(csv.DictReader(fh, delimiter=delimiter))
        return self._c[("c", rel)]


class Rows(list):
    def add(self, fig, id_, quantity, value, source, *, tol=None, shared="", printed=None, drawn=None):
        if isinstance(value, (np.integer,)):
            value = int(value)
        elif isinstance(value, (np.floating,)):
            value = float(value)
        elif isinstance(value, np.bool_):
            value = bool(value)
        elif isinstance(value, np.ndarray):
            value = value.tolist()
        self.append({"figure": fig, "id": f"{fig}.{id_}", "quantity": quantity, "value": value, "tol": tol, "shared": shared, "source": source, "printed": printed, "drawn": drawn})


def _tally(xs):
    out: dict = {}
    for x in xs:
        out[str(x)] = out.get(str(x), 0) + 1
    return out


def _a11(c: Ctx, rb, check):
    for r in c.csv("A11/a11_robustness.csv"):
        if r["rb_id"] == rb and r["check_id"] == check:
            return r
    raise KeyError(f"A11 row {rb}.{check}")


def _nums(text):
    import re
    return [int(x) for x in re.findall(r"\d+", text)]


# ---------------------------------------------------------------------------------------------------- F5
def f5(c: Ctx, R: Rows):
    a9 = c.pq("A9/a9_regime_map_v2.parquet")
    src = "A9/a9_regime_map_v2.parquet: map, class"
    m1, m2 = a9[a9["map"].astype(str) == "1"], a9[a9["map"].astype(str) == "2"]
    R.add("F5", "map1_cells", "cells of map 1", len(m1), src, printed=(r"of the (\d+) cells of map 1", 1), drawn="d['map1_n']")
    R.add("F5", "map1_surge", "D-tr cells of map 1", int((m1["class"] == "D-tr").sum()), src, printed=(r"fills (\d+) of the", 1), drawn="d['map1_n_surge']")
    R.add("F5", "map1_none", "D-none cells of map 1", int((m1["class"] == "D-none").sum()), src, printed=(r"D-none (\d+)\) and", 1), drawn="d['map1_n_none']")
    R.add("F5", "map1_pct", "percent D-tr in map 1", 100.0 * (m1["class"] == "D-tr").sum() / len(m1), src, printed=(r"\((\d+\.\d+)%, T_ramp", 1),
          drawn="100*d['map1_n_surge']/d['map1_n']")
    R.add("F5", "map1_T_ramp", "T_ramp of map 1 (single value)", sorted(set(m1["T_ramp_s"].astype(float))), src, printed=(r"T_ramp (\d+) s; D-none", 1), drawn="sorted(set(float(x) for x in [120.0]))")
    R.add("F5", "map2_cells", "cells of map 2", len(m2), src, printed=(r"and \d+ of the (\d+) cells of map 2", 1), drawn="d['map2_n']")
    R.add("F5", "map2_surge", "D-tr cells of map 2", int((m2["class"] == "D-tr").sum()), src, printed=(r"and (\d+) of the \d+ cells of map 2", 1), drawn="d['map2_n_surge']")
    R.add("F5", "map2_none", "D-none cells of map 2", int((m2["class"] == "D-none").sum()), src, printed=(r"map 2 \(D-none (\d+)\)", 1), drawn="d['map2_n_none']")
    R.add("F5", "headline_rows", "headline rows in the A9 table", int((a9["map"].astype(str) == "headline").sum()), src)
    R.add("F5", "a9_rows", "rows of the A9 table", len(a9), src)
    R.add("F5", "g5_threshold", "3 percent of the map-1 cells", 0.03 * len(m1), src, tol=1e-12, drawn="d['g5_threshold_cells']")
    R.add("F5", "g5_triggered", "map-1 surge cells below the G5 threshold", bool((m1["class"] == "D-tr").sum() < 0.03 * len(m1)), src, drawn="d['g5_triggered']")
    # the 25 x 13 and 30 x 30 grids
    R.add("F5", "map1_grid", "map-1 grid shape (i max + 1, j max + 1)", [int(m1["i"].max()) + 1, int(m1["j"].max()) + 1], src, drawn="list(d['map1_class'].shape)")
    R.add("F5", "map2_grid", "map-2 grid shape", [int(m2["i"].max()) + 1, int(m2["j"].max()) + 1], src, drawn="list(d['map2_class'].shape)")
    # subgrid
    sg = c.pq("A9/a9_subgrid_agreement.parquet")
    s2 = "A9/a9_subgrid_agreement.parquet"
    n = len(sg)
    ag = int(sg["d24_cell_agrees"].astype(bool).sum())
    R.add("F5", "sub_n", "subgrid cells", n, s2, printed=(r"of (\d+) cells agree", 1), drawn="d['sub_n']")
    R.add("F5", "d24_agree", "cells that agree by the D24 rule", ag, s2 + ": d24_cell_agrees", printed=(r"\((\d+) of \d+ cells agree", 1), drawn="d['d24_n_agree']")
    R.add("F5", "d24_pct", "percent of cells that agree by D24", 100.0 * ag / n, s2, printed=(r"cells agree = (\d+\.\d+)%", 1), drawn="100*d['d24_n_agree']/d['sub_n']")
    R.add("F5", "d24_needed", "cells needed for 90 percent of the subgrid", math.ceil(0.9 * n), s2, printed=(r"%, (\d+) needed", 1), drawn="d['d24_needed']")
    R.add("F5", "d24_tie", "D24 ties", int(sg["d24_tie"].astype(bool).sum()), s2 + ": d24_tie", drawn="d['d24_n_tie']")
    R.add("F5", "d24_disagree", "D24 disagreements that are not ties", int((~sg["d24_cell_agrees"].astype(bool) & ~sg["d24_tie"].astype(bool)).sum()), s2, drawn="d['d24_n_disagree']")
    # three Table 2.1 categories (reading ours): surge, S-sus, NS
    n_cat = 0
    for cnt_s, det in zip(sg["d24_ramp_class_counts"], sg["deterministic_class"]):
        cat: dict = {}
        for k, v in json.loads(cnt_s).items():
            kk = "surge" if k in SURGE else k
            cat[kk] = cat.get(kk, 0) + int(v)
        top = sorted(cat.values(), reverse=True)
        best = max(cat, key=cat.get)
        tie = len(top) > 1 and top[0] == top[1]
        n_cat += int((not tie) and best == ("surge" if det == "D-tr" else "NS"))
    R.add("F5", "d24_categories", "cells that agree on the three Table 2.1 categories", n_cat, s2 + ": d24_ramp_class_counts, deterministic_class", printed=(r"; (\d+) of \d+ on the three", 1),
          drawn="d['d24_n_agree_categories']")
    p1 = int(sg["p1_cell_agrees"].astype(bool).sum())
    R.add("F5", "p1_agree", "cells that agree by the post-hoc view P-1", p1, s2 + ": p1_cell_agrees", printed=(r"P-1 \((\d+) of \d+ = ", 1), drawn="d['p1_n_agree']")
    R.add("F5", "p1_pct", "percent of cells that agree by P-1", 100.0 * p1 / n, s2, printed=(r"P-1 \(\d+ of \d+ = (\d+\.\d+)%", 1), drawn="100*d['p1_n_agree']/d['sub_n']")
    R.add("F5", "p1_tie", "P-1 ties", int(sg["p1_tie"].astype(bool).sum()), s2, drawn="d['p1_n_tie']")
    R.add("F5", "p1_disagree", "P-1 disagreements that are not ties", int((~sg["p1_cell_agrees"].astype(bool) & ~sg["p1_tie"].astype(bool)).sum()), s2, drawn="d['p1_n_disagree']")
    # A11 table (the original evaluator's stored output: shared)
    sh = "stored A11 table (original evaluator output)"
    t = _a11(c, "RB4", "parameter_perturbation")["value"]
    q = _nums(t)
    R.add("F5", "rb4_changed", "RB4 cells changed (of 14)", q[0], "A11/a11_robustness.csv: RB4.parameter_perturbation value", shared=sh, printed=(r"RB4 passed \((\d+) of \d+ changed", 1))
    R.add("F5", "rb4_changed_den", "RB4 denominator (changed)", q[1], "A11/a11_robustness.csv: RB4.parameter_perturbation value", shared=sh, printed=(r"RB4 passed \(\d+ of (\d+) changed", 1))
    R.add("F5", "rb4_unchanged", "RB4 unchanged", q[2], "A11/a11_robustness.csv: RB4.parameter_perturbation value", shared=sh, printed=(r"changed, (\d+) of \d+ unchanged", 1))
    R.add("F5", "rb4_unchanged_den", "RB4 denominator (unchanged)", q[3], "A11/a11_robustness.csv: RB4.parameter_perturbation value", shared=sh, printed=(r"changed, \d+ of (\d+) unchanged", 1))
    qc = _nums(_a11(c, "RB1", "cells_30s")["value"])
    R.add("F5", "rb1_cells", "RB1 cells that agree (of 4)", qc[0], "A11/a11_robustness.csv: RB1.cells_30s value", shared=sh, printed=(r"RB1 cells (\d+) of", 1), drawn="d['cells_n_agree']")
    R.add("F5", "rb1_cells_den", "RB1 cells (denominator)", qc[1], "A11/a11_robustness.csv: RB1.cells_30s value", shared=sh, printed=(r"RB1 cells \d+ of (\d+)", 1))
    q2 = _nums(_a11(c, "RB2", "noisy_subgrid_agreement")["value"])
    R.add("F5", "rb2_agree", "RB2 subgrid cells that agree (A11 text)", q2[0], "A11/a11_robustness.csv: RB2.noisy_subgrid_agreement", shared=sh, drawn="d['d24_n_agree']")
    # network cells (S8 cell records: classes per seed from the stored per-record class table; the mean-field class is the evaluator's, shared)
    ev = c.json("ms10/eval/ms10_eval.json")
    cells = ev["rb1_cells"]["cells"]
    sh2 = "stored per-record classes and the mean-field class of the original evaluator"
    tsv = c.csv("ms10/10g/record_classes.tsv", "\t")
    s8 = [r for r in tsv if r["list"] == "S8" and r["T_ramp"] == "30.0"]
    by_group: dict = {}
    for r in s8:
        by_group.setdefault(int(r["group"]), []).append((int(r["seed"]), r["class"]))
    n_agree, ngr = 0, 0
    for g in sorted(by_group):
        refc = cells[str(g)]["ref"]["class"]
        cls = [x[1] for x in sorted(by_group[g])]
        ok = all((k in SURGE) == (refc == "D-tr") for k in cls) if refc == "D-tr" else all(k == "NS" or k == "S-sus" for k in cls)
        n_agree += int(ok)
        ngr += 1
    R.add("F5", "cells_n", "network cells (groups of S8 records at T_ramp 30 s)", ngr, "ms10/10g/record_classes.tsv: list S8, T_ramp 30", shared=sh2, drawn="len(d['cell_i'])")
    R.add("F5", "cells_agree", "cells in which all 3 seeds correspond to the mean-field class (our reading of Table 2.1)", n_agree, "ms10/10g/record_classes.tsv, ms10_eval.json:rb1_cells.ref.class", shared=sh2,
          drawn="d['cells_n_agree']")
    R.add("F5", "cells_disagree", "cells that disagree", ngr - n_agree, "same", shared=sh2, printed=(r"mean field at (\d+) of the 4", 1), drawn="d['cells_n_disagree']")
    R.add("F5", "cells_ev_agree", "cells that agree in ms10_eval.json:rb1_cells", int(ev["rb1_cells"]["n_agree"]), "ms10/eval/ms10_eval.json:rb1_cells.n_agree", shared=sh2)
    # N sweep: class tally per N, ramp seeds (S9) and no-ramp controls (C2_S9)
    for lst, key, dk in (("S9", "ramp", "s9_class"), ("C2_S9", "control", "ctrl_class")):
        for N in (1000, 3000, 10000, 30000):
            sub = [r["class"] for r in tsv if r["list"] == lst and int(r["N"]) == N]
            for cl in CLASSES:
                pr = None
                if lst == "S9" and (N, cl) == (3000, "S+"):
                    pr = (r"S\+ in (\d+) seeds at N = 3e3", 1)
                if lst == "S9" and (N, cl) == (10000, "NS"):
                    pr = (r"NS in (\d+) at N = 1e4", 1)
                R.add("F5", f"{key}_N{N}_{cl}", f"{key} seeds of class {cl} at N = {N}", sub.count(cl), "ms10/10g/record_classes.tsv: list, N, class", shared="stored class column", printed=pr,
                      drawn=f"int((d['{dk}'][{(1000, 3000, 10000, 30000).index(N)}] == '{cl}').sum())")
            R.add("F5", f"{key}_N{N}_n", f"{key} records at N = {N}", len(sub), "ms10/10g/record_classes.tsv", shared="stored class column", drawn=f"d['{dk}'].shape[1]")
    for N in (10000, 30000):
        n_s = sum(1 for r in tsv if r["list"] == "S9" and int(r["N"]) == N and r["class"] in SURGE)
        R.add("F5", f"nrule_{N}", f"S9 seeds in a surge class at N = {N}", n_s, "ms10/10g/record_classes.tsv", shared="stored class column", drawn=f"d['n_rule']['count_{'1e4' if N == 10000 else '3e4'}']")


# ---------------------------------------------------------------------------------------------------- F6
def f6(c: Ctx, R: Rows):
    a9 = c.pq("A9/a9_regime_map_v2.parquet")
    src = "A9/a9_regime_map_v2.parquet: map, class, failure_label"
    non = a9[a9["class"] == "D-none"]
    n1, n2 = int((non["map"].astype(str) == "1").sum()), int((non["map"].astype(str) == "2").sum())
    R.add("F6", "nonsurge_total", "non-surge cells of map 1 and map 2", n1 + n2, src, printed=(r"The (\d+) non-surge cells", 1), drawn="int(d['map_nonsurge'].sum())")
    R.add("F6", "nonsurge_map1", "non-surge cells of map 1", n1, src, printed=(r"map 1 \((\d+)\)", 1), drawn="int(d['map_nonsurge'][0])")
    R.add("F6", "nonsurge_map2", "non-surge cells of map 2", n2, src, printed=(r"map 2 \((\d+)\)", 1), drawn="int(d['map_nonsurge'][1])")
    lab = _tally(non["failure_label"])
    for k, pat in (("a", r"label a (\d+)"), ("c", r"c (\d+)"), ("f", r"f (\d+)"), ("g", r"g (\d+)"), ("h", r"h (\d+)\)")):
        R.add("F6", f"label_{k}", f"non-surge cells with primary failure label {k}", lab.get(k, 0), src + ": failure_label", printed=(pat.replace("label a", "primary label a") if k == "a" else pat, 1),
              drawn=f"int(d['label_primary'].sum(axis=0)['abcdefgh'.index('{k}')])")
    for m, mn in (("1", 0), ("2", 1)):
        sub = non[non["map"].astype(str) == m]
        R.add("F6", f"map{m}_labelled", f"labelled non-surge cells of map {m}", int(sub["failure_label"].notna().sum()), src, drawn=f"int(d['label_primary'][{mn}].sum())")
    ctl = c.csv("A10/a10_controls.csv")
    sa = "A10/a10_controls.csv: control, row_type, class"

    def cnt(ctrl, rt, cl=None, col="class"):
        return sum(1 for r in ctl if r["control"] == ctrl and r["row_type"] == rt and (cl is None or r[col] == cl))
    R.add("F6", "nc1_mf_none", "NC1 mean-field headline cells with class D-none", cnt("NC1", "mean_field_headline_cell", "D-none"), sa, printed=(r"NC1 is D-none at (\d+) of \d+ T_ramp", 1),
          drawn="sum(1 for x in d['nc1_mf_class'] if x == 'D-none')")
    R.add("F6", "nc1_mf_n", "NC1 mean-field headline cells", cnt("NC1", "mean_field_headline_cell"), sa, printed=(r"NC1 is D-none at \d+ of (\d+) T_ramp", 1), drawn="len(d['nc1_mf_class'])")
    R.add("F6", "nc1_cells_none", "NC1 map cells with class D-none", cnt("NC1", "map_cell", "D-none"), sa, printed=(r"and at the (\d+) map", 1), drawn="sum(1 for x in d['nc1_cells_class'] if x == 'D-none')")
    R.add("F6", "nc3_none", "NC3 T_ramp rows with class D-none", cnt("NC3", "per_T_ramp", "D-none"), sa, printed=(r"NC3 is D-none at (\d+) of \d+", 1), drawn="sum(1 for x in d['nc3_class'] if x == 'D-none')")
    R.add("F6", "nc3_n", "NC3 T_ramp rows", cnt("NC3", "per_T_ramp"), sa, printed=(r"NC3 is D-none at \d+ of (\d+)", 1), drawn="len(d['nc3_class'])")
    R.add("F6", "nc2_tr", "NC2 T_ramp rows with class D-tr (I = 0)", cnt("NC2", "per_T_ramp", "D-tr"), sa, printed=(r"NC2 is D-tr at (\d+) of \d+ T_ramp", 1), drawn="sum(1 for x in d['nc2_I0_class'] if x == 'D-tr')")
    R.add("F6", "nc2_tr_I1", "NC2 T_ramp rows with class D-tr (I = 1)", cnt("NC2", "per_T_ramp", "D-tr", col="class_I1"), sa, drawn="sum(1 for x in d['nc2_I1_class'] if x == 'D-tr')")
    R.add("F6", "nc2_n", "NC2 T_ramp rows", cnt("NC2", "per_T_ramp"), sa, printed=(r"NC2 is D-tr at \d+ of (\d+) T_ramp", 1), drawn="len(d['nc2_I0_class'])")
    net = [r for r in ctl if r["control"] == "NC1" and r["row_type"] == "network_run"]
    R.add("F6", "nc1_net_class", "class of the NC1 network run", net[0]["class"], sa, printed=(r"1 seed\) is (S\+)", 1), drawn="d['nc1_net_class']")
    R.add("F6", "nc1_net_rows", "NC1 network rows", len(net), sa, drawn="1")
    R.add("F6", "a10_rows", "rows of the A10 controls table", len(ctl), sa)
    s6 = c.pq("A7/a7_s6_metrics.parquet")
    pre = s6[s6["row_kind"] == "S6_pre_registered"]
    R.add("F6", "s6_prereg", "pre-registered S6 rows", len(pre), "A7/a7_s6_metrics.parquet: row_kind", printed=(r"All (\d+) pre-registered", 1), drawn="d['s6_n_prereg']")
    R.add("F6", "s6_prereg_Dtr", "pre-registered S6 rows of class D-tr", int((pre["class"] == "D-tr").sum()), "A7/a7_s6_metrics.parquet: class", shared="stored class column", drawn="20 if d['s6_prereg_all_Dtr'] else -1")
    R.add("F6", "s6_rows", "rows of the S6 table", len(s6), "A7/a7_s6_metrics.parquet")
    R.add("F6", "s6_P3", "pre-registered S6 rows of P3", int((pre["path_name"] == "path_drive").sum()), "A7/a7_s6_metrics.parquet: path_name")
    for p, pn in (("P4a", "path_delta_up"), ("P4b", "path_delta_down")):
        R.add("F6", f"s6_{p}", f"pre-registered S6 rows of {p}", int((pre["path_name"] == pn).sum()), "A7/a7_s6_metrics.parquet: path_name")
    R.add("F6", "s6_T", "T_ramp values of the S6 rows", sorted(set(pre["T_ramp_s"].astype(float))), "A7/a7_s6_metrics.parquet: T_ramp_s", tol=0.0, drawn="[float(x) for x in d['s6_T']]")


# ---------------------------------------------------------------------------------------------------- FS1
def fs1(c: Ctx, R: Rows):
    a1 = c.npz("A1/a1_fixedpoints_2d.npz")
    a2 = c.npz("A2/a2_ring_map.npz")
    R.add("FS1", "k1_n", "K1 r values", len(a1["k1_r"]), "A1/a1_fixedpoints_2d.npz: k1_r", printed=(r"for (\d+) of \d+ r values", 1), drawn="d['k1_n']")
    R.add("FS1", "k1_half", "K1 r values passed at half spacing", int(np.asarray(a1["k1_pass_half"]).astype(bool).sum()), "A1: k1_pass_half", printed=(r"for \d+ of (\d+) r values", 1), drawn="d['k1_pass_half']")
    R.add("FS1", "k1_base", "K1 r values passed at base spacing", int(np.asarray(a1["k1_pass_base"]).astype(bool).sum()), "A1: k1_pass_base", printed=(r"\((\d+) of \d+ at base", 1), drawn="d['k1_pass_base']")
    R.add("FS1", "grid_eta", "eta grid points", len(a1["eta_over_Delta"]), "A1: eta_over_Delta", drawn="len(d['eta'])")
    R.add("FS1", "grid_J", "J grid points", len(a1["J_over_sqrtDelta"]), "A1: J_over_sqrtDelta", drawn="len(d['J'])")
    cu = np.asarray(a1["cusp_r_eta_J"], float)
    R.add("FS1", "cusp_r", "cusp r", float(cu[0]), "A1: cusp_r_eta_J[0]", tol=("rel", 1e-12), drawn="d['cusp_r']")
    R.add("FS1", "cusp_eta", "cusp eta/Delta", float(cu[1]), "A1: cusp_r_eta_J[1]", tol=("rel", 1e-12), drawn="d['cusp_eta']")
    R.add("FS1", "cusp_J", "cusp J/sqrt(Delta)", float(cu[2]), "A1: cusp_r_eta_J[2]", tol=("rel", 1e-12), drawn="d['cusp_J']")
    nr = np.asarray(a1["n_roots"])
    R.add("FS1", "roots_shape", "n_roots grid shape", list(nr.shape), "A1: n_roots", drawn="list(d['n_roots_T'].shape)")
    R.add("FS1", "roots_max", "largest root count", int(nr.max()), "A1: n_roots", drawn="int(d['n_roots_T'].max())")
    foc = np.asarray(a2["ring_is_focus"]).astype(bool)
    ing = np.asarray(a2["ring_in_G"]).astype(bool)
    nd = np.asarray(a2["ring_g1_nondamped"]).astype(bool)
    R.add("FS1", "ring_focus", "stable foci on the A1 grid", int(foc.sum()), "A2/a2_ring_map.npz: ring_is_focus", printed=(r"\(0 of (\d+);", 1), drawn="d['ring_n_focus']")
    R.add("FS1", "ring_nondamped", "stable foci that are not damped", int((foc & nd).sum()), "A2: ring_is_focus, ring_g1_nondamped", printed=(r"non-damped \((\d+) of", 1), drawn="d['ring_n_nondamped']")
    R.add("FS1", "ring_inG", "stable foci inside the 25 to 100 Hz band", int((foc & ing).sum()), "A2: ring_is_focus, ring_in_G", drawn="d['ring_n_inG']")
    cy = np.asarray(a2["ring_cycles_per_efold"], float)
    R.add("FS1", "ring_cyc_max", "largest cycles per e-fold inside the band", float(np.nanmax(np.where(foc & ing, cy, np.nan))), "A2: ring_cycles_per_efold, ring_in_G", printed=(r"e-fold inside the 25 to 100 Hz band is (\d+\.\d+)", 1),
          tol=("rel", 1e-12), drawn="d['ring_cyc_inG_max']")
    fq = np.asarray(a2["ring_freq_hz"], float)
    R.add("FS1", "ring_freq_min", "smallest ring frequency over foci", float(np.nanmin(np.where(foc, fq, np.nan))), "A2: ring_freq_hz", tol=("rel", 1e-12), drawn="d['ring_freq_min']")
    R.add("FS1", "ring_freq_max", "largest ring frequency over foci", float(np.nanmax(np.where(foc, fq, np.nan))), "A2: ring_freq_hz", tol=("rel", 1e-12), drawn="d['ring_freq_max']")
    R.add("FS1", "k4_rel_freq", "K4 relative error of the frequency", abs(float(a2["k4_omega_fit"]) - float(a2["k4_omega_lin"])) / float(a2["k4_omega_lin"]), "A2: k4_omega_fit, k4_omega_lin",
          printed=(r"decay to (\d+\.\d+e-\d+)", 1), tol=("rel", 1e-9), drawn="d['k4_rel_err_frequency']")
    R.add("FS1", "k4_rel_decay", "K4 relative error of the decay", abs(float(a2["k4_decay_fit"]) - float(a2["k4_decay_lin"])) / float(a2["k4_decay_lin"]), "A2: k4_decay_fit, k4_decay_lin",
          printed=(r"frequency and decay to \d+\.\d+e-\d+ and (\d+\.\d+e-\d+)", 1), tol=("rel", 1e-9), drawn="d['k4_rel_err_decay']")
    rep = c.csv("A0/a0_replication.csv")
    R.add("FS1", "a0_rows", "rows of the A0 replication table", len(rep), "A0/a0_replication.csv", drawn="len(d['a0_target'])")
    R.add("FS1", "a0_pass", "A0 rows that pass", [r["pass"] for r in rep], "A0/a0_replication.csv: pass", drawn="[str(x) for x in d['a0_pass']]")
    k3 = [str(x) for x in np.asarray(a1.get("k3_labels", [])).tolist()] if "k3_labels" in a1 else None
    if k3 is not None:
        R.add("FS1", "k3_labels", "K3 labels at (-5, 15)", sorted(k3), "A1: k3_labels", drawn="sorted(d['k3_labels'].split(', '))")


# ---------------------------------------------------------------------------------------------------- F3
def f3(c: Ctx, R: Rows):
    npz = c.npz("A6/a6_freq_map.npz")
    s6 = c.json("A6/a6_summary.json")
    for D in ("0.05", "0.1", "0.3"):
        pre = f"eta_tau_D{D}_"
        fmax, fmin = np.asarray(npz[pre + "f_max"], float), np.asarray(npz[pre + "f_min"], float)
        c25, c100 = np.asarray(npz[pre + "c25_count"]), np.asarray(npz[pre + "c100_count"])
        R.add("F3", f"D{D}_slices", f"slices at Delta {D}", len(c25), "A6/a6_freq_map.npz: eta_tau_D*_c25_count", drawn=f"len(d['D{D}_tau_d_ms'])")
        R.add("F3", f"D{D}_c100", f"100 Hz crossings summed over the slices at Delta {D}", int(c100.sum()), "A6/a6_freq_map.npz: *_c100_count", drawn=f"int(np.sum(d['D{D}_c100_count']))")
        R.add("F3", f"D{D}_c25_slices", f"slices at Delta {D} with a 25 Hz crossing", int((c25 > 0).sum()), "A6/a6_freq_map.npz: *_c25_count", drawn=f"int((np.asarray(d['D{D}_c25_count']) > 0).sum())")
        R.add("F3", f"D{D}_fmax", f"largest cycle frequency at Delta {D} (Hz)", float(np.nanmax(fmax)), "A6/a6_freq_map.npz: *_f_max", tol=("rel", 1e-12), drawn=f"d['D{D}_f_max_hz']")
        td = [k for k in s6["slices"] if k.startswith(f"eta_tau_D{D}_")]
        cross = sorted(float(k.split("_td")[1]) for k, i in zip(sorted(td), range(len(td))) if c25[i] > 0) if False else None
    # tau_d of the slices (from the slice keys) with a crossing
    keys = list(s6["slices"])
    for D, thr in (("0.05", 3.0), ("0.1", 5.0), ("0.3", 13.0)):
        tds = sorted(float(k.split("_td")[1]) for k in keys if k.startswith(f"eta_tau_D{D}_"))
        c25 = np.asarray(npz[f"eta_tau_D{D}_c25_count"])
        other = np.asarray(npz[f"eta_tau_D{D}_other"], float)
        with_cross = sorted(float(o) for o, n in zip(other, c25) if n > 0)
        R.add("F3", f"D{D}_first_cross", f"smallest tau_d (ms) of a slice at Delta {D} with a 25 Hz crossing", with_cross[0] if with_cross else None, "A6/a6_freq_map.npz: eta_tau_D*_other, *_c25_count",
              printed=({"0.05": (r"Delta 0\.05 from tau_d (\d+) ms", 1), "0.1": (r"Delta 0\.1 from (\d+) ms", 1), "0.3": None}[D]), tol=1e-12)
        R.add("F3", f"D{D}_cross_list", f"tau_d (ms) of the slices at Delta {D} with a 25 Hz crossing", with_cross, "A6/a6_freq_map.npz", tol=1e-12,
              drawn=f"[float(x) for x, n in zip(d['D{D}_tau_d_ms'], d['D{D}_c25_count']) if n > 0]")
    allf = np.concatenate([np.asarray(npz[f"eta_tau_D{D}_f_max"], float) for D in ("0.05", "0.1", "0.3")])
    R.add("F3", "fmax_all", "largest cycle frequency over all slices (Hz)", float(np.nanmax(allf)), "A6/a6_freq_map.npz: eta_tau_D*_f_max", printed=(r"\(largest cycle frequency (\d+\.\d)", 1), tol=("rel", 1e-12), drawn="d['f_max_hz']")
    dv = s6["devalle"]
    R.add("F3", "ref_fmin", "cycle frequency at the start of the ref_devalle region (Hz)", dv["f_min_region"], "A6/a6_summary.json:devalle.f_min_region", printed=(r"cycle at ref_devalle at (\d+\.\d)", 1))
    R.add("F3", "ref_fmax", "cycle frequency at the end of the ref_devalle region (Hz)", dv["f_max_region"], "A6/a6_summary.json:devalle.f_max_region", printed=(r"to (\d+\.\d) Hz \(DL-131", 1))
    R.add("F3", "ref_etaH", "Hopf point of ref_devalle", dv["eta_H"], "A6/a6_summary.json:devalle.eta_H", tol=("rel", 1e-12), drawn="d['headline_hopf_eta']")
    # the path records
    paths = {"P1": "S5/ramp/p1_linear/p1_linear_0008_333859d6472b.json", "P2": "S5/ramp/S5ramp/S5ramp_0000_240de3ef73be.json", "P3": "S6/S6_P3/S6_P3_0006_5fb237a3d3fd.json",
             "P4a": "S6/S6_P4a/S6_P4a_0002_42415b96d00c.json", "P4b": "S6/S6_P4b/S6_P4b_0002_7be4a3067a9d.json", "P5": "S5/ramp/p5_linear/p5_linear_0008_da88da96d075.json"}
    for p, rel in paths.items():
        cfg = c.json(rel)["config"]["path"]
        R.add("F3", f"{p}_T_ramp", f"{p} T_ramp (s)", float(cfg["T_ramp_s"]), rel + ":config.path.T_ramp_s", tol=0.0, drawn=f"d['{p}_T_ramp_s']")
        R.add("F3", f"{p}_I_amp", f"{p} I_amp", float(cfg.get("I_amp", 0.0)), rel + ":config.path.I_amp", tol=0.0, drawn=f"d['{p}_I_amp']")
        R.add("F3", f"{p}_eta_peak", f"{p} eta peak", float(cfg["eta_peak"]), rel + ":config.path.eta_peak", tol=("rel", 1e-12), drawn=f"d['{p}_eta_peak']")
        R.add("F3", f"{p}_eta_start", f"{p} eta start", float(cfg["eta_start"]), rel + ":config.path.eta_start", tol=("rel", 1e-12), drawn=f"d['{p}_eta_start']")


# ---------------------------------------------------------------------------------------------------- F2
def f2(c: Ctx, R: Rows):
    a5 = c.npz("A5/a5_cycles.npz")
    a5j = c.json("A5/julia/a5.json")
    R.add("F2", "hopf_eta", "Hopf point at ref_devalle (A5 stored value)", float(a5["devalle_hopf_eta_bar"][0]), "A5/a5_cycles.npz: devalle_hopf_eta_bar", printed=(r"eta_bar (\d+\.\d+) in a supercritical", 1),
          tol=("rel", 1e-12), drawn="d['eta_H']")
    br = a5j["branches"]["devalle"]
    R.add("F2", "hopf_type", "Hopf type", br["hopf_type"], "A5/julia/a5.json:branches.devalle.hopf_type", drawn="d['hopf_type']")
    R.add("F2", "cycle_points", "cycle branch points (up + down)", len(a5["devalle_param"]), "A5/a5_cycles.npz: devalle_param", drawn="d['a5_cycle_count']")
    st = np.asarray(a5["devalle_stable"]).astype(bool)
    R.add("F2", "cycles_unstable", "unstable cycle points", int((~st).sum()), "A5/a5_cycles.npz: devalle_stable", printed=None, drawn="d['a5_cycle_unstable_count']")
    R.add("F2", "cycle_eta_max", "largest eta_bar of the cycle branch", float(np.max(a5["devalle_param"])), "A5/a5_cycles.npz: devalle_param", printed=(r"stable\s+cycles to eta_bar (\d+)", 1), tol=0.0, drawn="d['a5_eta_max']")
    R.add("F2", "fixed_points", "fixed-point branch points", len(a5["devalle_fixed_param"]), "A5/a5_cycles.npz: devalle_fixed_param", drawn="len(d['fixed_param'])")
    up = np.asarray(a5["devalle_direction_up"]).astype(bool)
    R.add("F2", "a5_up_n", "up-direction cycle points", int(up.sum()), "A5/a5_cycles.npz: devalle_direction_up", drawn="len(d['a5_up_param'])")
    R.add("F2", "a5_down_n", "down-direction cycle points", int((~up).sum()), "A5/a5_cycles.npz", drawn="len(d['a5_down_param'])")
    amp = np.asarray(a5["devalle_vmax"], float) - np.asarray(a5["devalle_vmin"], float)
    R.add("F2", "a5_amp_max", "largest cycle amplitude (vmax - vmin)", float(np.max(amp)), "A5/a5_cycles.npz: devalle_vmax, devalle_vmin", tol=("rel", 1e-9),
          drawn="float(max(np.max(d['a5_up_amp']), np.max(d['a5_down_amp'])))")
    # S4 mean-field sweep, up and down amplitude from the stored series
    s4 = c.npz("S4/devalle/devalle_0000_48a5a3bd19e9.npz")
    stp = np.asarray(s4["step"])
    v = np.asarray(s4["v"], float)
    sp = np.asarray(s4["step_param"], float)
    su = np.asarray(s4["step_up"]).astype(bool)
    R.add("F2", "s4_steps", "S4 mean-field steps (up + down)", len(sp), "S4/devalle/*.npz: step_param", drawn="len(d['mf_param'])")
    R.add("F2", "s4_series_n", "S4 mean-field series samples", len(v), "S4/devalle/*.npz: v")
    sm = c.npz("S4/s4_summary.npz")
    pair_p = np.asarray(sm["devalle_pair_param"], float)
    rel = np.asarray(sm["devalle_pair_v_ptp_rel_diff"], float)
    etaH = float(a5["devalle_hopf_eta_bar"][0])
    mask = pair_p >= etaH + 0.2 - 1e-9
    R.add("F2", "updown_max_rel", "largest up-down relative difference in the v amplitude from 0.2 above the Hopf point", float(np.nanmax(np.abs(rel[mask]))), "S4/s4_summary.npz: devalle_pair_*",
          printed=(r"\(largest up-down difference in the v amplitude (\d+\.\d+e-\d+)", 1), tol=("rel", 1e-9), drawn="d['mf_updown_max_abs_from_0p2']")
    chk = c.json("A5/check/a5_check.json")
    R.add("F2", "a5_vs_s4", "A5 against S4, largest relative difference (up)", chk["a5_vs_s4"]["devalle"]["up"]["max_abs_rel_diff"], "A5/check/a5_check.json:a5_vs_s4.devalle.up",
          printed=(r"S4 at most (\d+\.\d+e-\d+)", 1), tol=("rel", 1e-12), shared="stored check file of the original analysis")
    # network sweep
    ns = c.npz("S4/s4_net_summary.npz")
    npar = np.asarray(ns["net_param"], float)
    rv = np.asarray(ns["cmp_rel_v_ptp"], float)
    above = npar > 3.0 - 1e-9
    R.add("F2", "net_steps", "network sweep steps", len(npar), "S4/s4_net_summary.npz: net_param", drawn="len(d['net_param'])")
    R.add("F2", "net_rel_above_max", "largest relative difference (percent) above eta_bar 3.0", 100.0 * float(np.nanmax(rv[above])), "S4/s4_net_summary.npz: cmp_rel_v_ptp", printed=(r"by \+(\d+\.\d) to", 1),
          tol=("rel", 1e-9), drawn="100*d['cmp_rel_v_above_max']")
    R.add("F2", "net_rel_above_min", "smallest relative difference (percent) above eta_bar 3.0", 100.0 * float(np.nanmin(rv[above])), "S4/s4_net_summary.npz: cmp_rel_v_ptp", printed=(r"to (-\d+\.\d) percent above", 1),
          tol=("rel", 1e-9), drawn="100*d['cmp_rel_v_above_min']")
    nv = np.asarray(ns["net_v_ptp"], float)
    below = npar < etaH - 1e-9
    R.add("F2", "net_floor_n", "network steps below the Hopf point", int(below.sum()), "S4/s4_net_summary.npz", drawn="d['net_floor_steps']")
    R.add("F2", "net_floor_min", "smallest network v amplitude below the Hopf point", float(np.nanmin(nv[below])), "S4/s4_net_summary.npz: net_v_ptp", printed=(r"v amplitude (0\.\d+) to", 1), tol=("rel", 1e-9), drawn="d['net_floor_v_ptp_min']")
    R.add("F2", "net_floor_max", "largest network v amplitude below the Hopf point", float(np.nanmax(nv[below])), "S4/s4_net_summary.npz: net_v_ptp", printed=(r"v amplitude 0\.\d+ to (0\.\d+);", 1), tol=("rel", 1e-9), drawn="d['net_floor_v_ptp_max']")


FUNCS = {"F5": f5, "F6": f6, "FS1": fs1, "F3": f3, "F2": f2}


def compute(root=None, figures=None) -> list:
    c = Ctx(root)
    R = Rows()
    for fid in (figures or FIGURES):
        if fid in FUNCS:
            FUNCS[fid](c, R)
    return list(R)


def main() -> int:
    rows = compute()
    per: dict = {}
    for r in rows:
        per[r["figure"]] = per.get(r["figure"], 0) + 1
    for k in FIGURES:
        print(k, per.get(k, 0))
    print("total", len(rows), "shared", sum(1 for r in rows if r["shared"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
