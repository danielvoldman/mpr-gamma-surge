"""MS13 13q: independent recomputation of the take-home numbers and the main drawn quantities of F1 to F6 and FS1 to FS5 (docs/ms13_independent_plan.md).

  .venv/Scripts/python.exe scripts/ms13_independent.py            # prints the number of rows per figure; writes nothing

A SEPARATE code path: own readers of the stored files under results/ (json, numpy, csv, parquet); it imports nothing of mprsurge.plotting (no figures.py, figprov, claim_labels,
captions, style, nordlie and no figure data step). Shared frozen code, each use marked in the 'shared' field of the row it feeds: the frozen criteria loader and the frozen
surge classifier (mprsurge.analysis.a7.frozen_inputs, mprsurge.analysis.surge_metrics). compute() returns rows; it writes nothing. The comparison with the printed and drawn values
is scripts/ms13_independent_compare.py (the only place that may import the figure data steps).

A row: figure, id, quantity, value (int, float, str or list), tol (None = exact; a float = absolute; ('rel', x) = relative), shared ('' = independent; otherwise the reason),
source (stored file and key), printed (None, or (regex, group) applied to the figure's take-home text), drawn (None, or a Python expression over the figure's drawn dict d).
13t-1d (DL-571 T9, DL-572): jprinted (None, or (regex, group) applied to the JOURNAL caption of each file in jtargets; default the figure's own journal file): the same quantity as it is
printed in the journal caption. Every row of F1, F3 and F5 that has a `printed` pattern must have a journal pattern (JOURNAL below, or jprinted); the journal rows are reported separately.
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

    def __init__(self, root=None, series_res=None):
        self.root = Path(root) if root is not None else ROOT
        self.res = self.root / "results"
        self.series_res = Path(series_res) if series_res is not None else self.res          # where the large run-record series (S9 npz) are read from; a test points it at the real results
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
    def add(self, fig, id_, quantity, value, source, *, tol=None, shared="", printed=None, drawn=None, jprinted=None, jtargets=None, sprinted=None, stargets=None):
        if isinstance(value, (np.integer,)):
            value = int(value)
        elif isinstance(value, (np.floating,)):
            value = float(value)
        elif isinstance(value, np.bool_):
            value = bool(value)
        elif isinstance(value, np.ndarray):
            value = value.tolist()
        self.append({"figure": fig, "id": f"{fig}.{id_}", "quantity": quantity, "value": value, "tol": tol, "shared": shared, "source": source, "printed": printed, "drawn": drawn,
                     "jprinted": jprinted, "jtargets": tuple(jtargets) if jtargets else None, "sprinted": sprinted, "stargets": tuple(stargets) if stargets else None})


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
    f5c(c, R)



def f5c(c: Ctx, R: Rows):
    """F5c: per-seed class, f_pk, onset and duration of the S9 and S9_ctrl records, recomputed from the stored v by the FROZEN classifier (shared), then min, median and max per N."""
    import glob
    from mprsurge.analysis import a7 as A7
    from mprsurge.analysis import surge_metrics as SM
    fi, _gate = A7.frozen_inputs(ROOT)
    sh = "frozen classifier (surge_metrics.classify_mode_n) and the frozen threshold"
    tsv = {r["name"]: r["class"] for r in c.csv("ms10/10g/record_classes.tsv", "	")}
    ev = c.json("ms10/eval/ms10_eval.json")["N_sweep"]["by_N"]
    Ns = (1000, 3000, 10000, 30000)
    for key, folder, dk, arrs in (("ramp", "S9/S9", "s9", ("s9_class", "s9_f_pk_hz", "s9_onset_s", "s9_duration_ms")), ("control", "S9/S9_ctrl", "ctrl", ("ctrl_class", "ctrl_f_pk_hz", "ctrl_onset_s", None))):
        per: dict = {N: [] for N in Ns}
        for pth in sorted(glob.glob(str(c.series_res / folder / "*.json"))):
            if pth.endswith(".dry.json"):
                continue
            j = json.loads(Path(pth).read_text(encoding="utf-8"))
            cfg = j["config"]
            with np.load(Path(pth).with_suffix(".npz")) as z:
                v = z["v"]
            res = SM.classify_mode_n(v, 1000.0 / float(cfg["network"]["rate_bin_ms"]), float(cfg["path"]["t_on_s"]), float(cfg["path"]["T_ramp_s"]), fi["threshold"])
            ep = res.episode
            per[int(cfg["network"]["N"])].append({"name": Path(pth).stem, "cls": res.cls, "f": float(ep.f_pk_hz) if ep is not None else float("nan"),
                                                 "on": float(ep.onset_s) if ep is not None else float("nan"), "du": 1000.0 * float(ep.duration_s) if ep is not None else float("nan")})
        for i, N in enumerate(Ns):
            rs = per[N]
            R.add("F5", f"c_{key}_N{N}_n", f"{key} records read at N = {N}", len(rs), f"results/{folder}/*.json,npz", shared=sh, drawn=f"d['{arrs[0]}'].shape[1]")
            R.add("F5", f"c_{key}_N{N}_class_matches_stored", f"{key} records at N = {N} whose reclassified class equals the stored class column", sum(1 for r in rs if r["cls"] == tsv.get(r["name"])),
                  "frozen classifier on the stored v against ms10/10g/record_classes.tsv", shared=sh, drawn=f"d['{arrs[0]}'].shape[1]")
            R.add("F5", f"c_{key}_N{N}_classes", f"{key} reclassified class words at N = {N}, sorted", sorted(r["cls"] for r in rs), "frozen classifier on the stored v", shared=sh, drawn=f"sorted(str(x) for x in d['{arrs[0]}'][{i}])")
            for nm, k_, ak in (("f_pk_hz", "f", arrs[1]), ("onset_s", "on", arrs[2]), ("duration_ms", "du", arrs[3])):
                if ak is None:
                    continue
                vals = np.sort(np.array([r[k_] for r in rs], float)).tolist()
                R.add("F5", f"c_{key}_N{N}_{nm}", f"{key} {nm} per seed at N = {N}, sorted", vals, "frozen classifier on the stored v", shared=sh, tol=("rel", 1e-12), drawn=f"[float(x) for x in np.sort(d['{ak}'][{i}])]")
                fin = [x for x in vals if x == x]
                if key == "ramp" and fin:
                    st = ev[str(N)]["metrics"][nm]
                    R.add("F5", f"c_{key}_N{N}_{nm}_med_min_max", f"{key} {nm} at N = {N}: median, min, max over the defined seeds", [float(np.median(fin)), min(fin), max(fin)],
                          "frozen classifier; stored: ms10_eval.json:N_sweep", shared=sh, tol=("rel", 1e-12), drawn=f"[{st['median']!r}, {st['min']!r}, {st['max']!r}]")


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
    R.add("FS1", "k1_base", "K1 r values passed at base spacing", int(np.asarray(a1["k1_pass_base"]).astype(bool).sum()), "A1: k1_pass_base", printed=(r", (\d+) of \d+ at base", 1), drawn="d['k1_pass_base']")
    R.add("FS1", "grid_eta", "eta grid points", len(a1["eta_over_Delta"]), "A1: eta_over_Delta", drawn="len(d['eta'])")
    R.add("FS1", "grid_J", "J grid points", len(a1["J_over_sqrtDelta"]), "A1: J_over_sqrtDelta", drawn="len(d['J'])")
    cu = np.asarray(a1["cusp_r_eta_J"], float)
    R.add("FS1", "cusp_r", "cusp r", float(cu[0]), "A1: cusp_r_eta_J[0]", tol=("rel", 1e-12), drawn="d['cusp_r']")
    R.add("FS1", "cusp_eta", "cusp eta/Delta", float(cu[1]), "A1: cusp_r_eta_J[1]", tol=("rel", 1e-12), drawn="d['cusp_eta']")
    R.add("FS1", "cusp_J", "cusp J/sqrt(Delta)", float(cu[2]), "A1: cusp_r_eta_J[2]", tol=("rel", 1e-12), drawn="d['cusp_J']")
    nr = np.asarray(a1["n_roots"])
    R.add("FS1", "roots_shape", "n_roots grid shape (eta, J)", list(nr.shape), "A1: n_roots", drawn="list(d['n_roots_T'].shape)[::-1]")
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
          printed=(r"decays? to (\d+\.\d+e-\d+)", 1), tol=("rel", 1e-9), drawn="d['k4_rel_err_frequency']")
    R.add("FS1", "k4_rel_decay", "K4 relative error of the decay", abs(float(a2["k4_decay_fit"]) - float(a2["k4_decay_lin"])) / float(a2["k4_decay_lin"]), "A2: k4_decay_fit, k4_decay_lin",
          printed=(r"frequency and decays? to \d+\.\d+e-\d+ and (\d+\.\d+e-\d+)", 1), tol=("rel", 1e-9), drawn="d['k4_rel_err_decay']")
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
    R.add("F3", "ref_etaH", "Hopf point of ref_devalle (continuation value)", dv["hopf_param_julia"], "A6/a6_summary.json:devalle.hopf_param_julia", tol=("rel", 1e-12), drawn="d['headline_hopf_eta']")
    R.add("F3", "ref_etaH_nominal", "nominal Hopf point of the paths", dv["eta_H"], "A6/a6_summary.json:devalle.eta_H", tol=("rel", 1e-12), drawn="d['P2_eta_H']")
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
    below = npar < etaH - 0.1                                  # DL-129: steps within 0.1 of eta_H are not judged (the step at the Hopf point itself is not 'below')
    R.add("F2", "net_floor_n", "network steps more than 0.1 below the Hopf point", int(below.sum()), "S4/s4_net_summary.npz", drawn="d['net_floor_steps']")
    R.add("F2", "net_floor_min", "smallest network v amplitude below the Hopf point", float(np.nanmin(nv[below])), "S4/s4_net_summary.npz: net_v_ptp", printed=(r"v amplitude (0\.\d+) to", 1), tol=("rel", 1e-9), drawn="d['net_floor_v_ptp_min']")
    R.add("F2", "net_floor_max", "largest network v amplitude below the Hopf point", float(np.nanmax(nv[below])), "S4/s4_net_summary.npz: net_v_ptp", printed=(r"v amplitude 0\.\d+ to (0\.\d+);", 1), tol=("rel", 1e-9), drawn="d['net_floor_v_ptp_max']")


# ---------------------------------------------------------------------------------------------------- F4
def f4(c: Ctx, R: Rows):
    a7 = c.pq("A7/a7_ramp_metrics.parquet")
    s = "A7/a7_ramp_metrics.parquet"
    R.add("F4", "a7_rows", "rows of the A7 table", len(a7), s)
    for f_, n_ in sorted(_tally(a7["family"]).items()):
        R.add("F4", f"rows_{f_}", f"A7 rows of family {f_}", n_, s + ": family")
    md = a7[a7["mode"] == "D"]
    inr = md[md["in_range"].fillna(False).astype(bool)]
    test = inr[~inr["eta_const_at_t_pred"].fillna(False).astype(bool)]
    steps = [float(x) for x in test["match_err_steps"]]
    R.add("F4", "n_in_range", "mode-D runs inside the RB3(a) range", len(inr), s + ": in_range", drawn="d['n_in_range']")
    R.add("F4", "n_testable", "testable in-range runs", len(test), s + ": eta_const_at_t_pred", printed=(r"0 of (\d+) testable", 1), drawn="d['n_testable']")
    R.add("F4", "n_within", "testable runs within one A4 step", sum(1 for x in steps if x <= 1.0), s + ": match_err_steps", printed=(r"(\d+) of \d+ testable", 1), drawn="d['n_testable_within_one_step']")
    R.add("F4", "n_const", "in-range runs with eta constant at the predicted time", len(inr) - len(test), s, printed=(r"(\d+) more in-range runs", 1))
    R.add("F4", "steps_sorted", "match errors in steps, sorted", sorted(steps), s + ": match_err_steps", tol=("rel", 1e-12), drawn="[float(x) for x in d['testable_match_steps']]")
    printed_steps = [r"are (\d+\.\d), \d+\.\d, \d+\.\d, \d+\.\d, \d+\.\d and \d+\.\d A4 steps", r"\d+\.\d, (\d+\.\d), \d+\.\d, \d+\.\d, \d+\.\d and \d+\.\d A4 steps",
                     r"\d+\.\d, \d+\.\d, (\d+\.\d), \d+\.\d, \d+\.\d and \d+\.\d A4 steps", r"\d+\.\d, \d+\.\d, \d+\.\d, (\d+\.\d), \d+\.\d and \d+\.\d A4 steps",
                     r"\d+\.\d, \d+\.\d, \d+\.\d, \d+\.\d, (\d+\.\d) and \d+\.\d A4 steps", r"\d+\.\d, \d+\.\d, \d+\.\d, \d+\.\d, \d+\.\d and (\d+\.\d) A4 steps"]
    for i, x in enumerate(steps[:6]):
        R.add("F4", f"step_{i}", f"match error in steps of testable run {i} (table order)", x, s + ": match_err_steps", tol=0.05, printed=(printed_steps[i], 1))
    R.add("F4", "n_nocross", "mode-D runs without a raw crossing", int(md["delay_eta_cross"].isna().sum()), s + ": delay_eta_cross", drawn="d['n_nocross']")
    R.add("F4", "n_none", "mode-D runs of class D-none", int((md["cls"] == "D-none").sum()), s + ": cls", shared="stored class column", drawn="d['n_none_class']")
    h = a7[a7["family"] == "S5ramp"].iloc[0]
    rd = a7[a7["family"] == "radau"].iloc[0]
    R.add("F4", "head_onset", "noise-free headline onset (s)", float(h["onset_s"]), s + ": S5ramp.onset_s", printed=(r"headline onset \((\d+\.\d+) s\)", 1), drawn="d['head_onset_s']", tol=("rel", 1e-12))
    R.add("F4", "head_pred", "predicted entry time (s)", float(h["t_pred_s"]), s + ": S5ramp.t_pred_s", printed=(r"predicted entry \((\d+\.\d) s\)", 1), drawn="d['head_t_pred_s']", tol=("rel", 1e-12))
    R.add("F4", "head_dop", "headline onset, DOP853 (raw crossing, s)", float(h["onset_cross_s"]), s + ": S5ramp.onset_cross_s", printed=(r"DOP853 (\d+\.\d+) s", 1), drawn="d['head_onset_cross_s']", tol=("rel", 1e-12))
    R.add("F4", "head_radau", "headline onset, Radau (raw crossing, s)", float(rd["onset_cross_s"]), s + ": radau.onset_cross_s", printed=(r"Radau (\d+\.\d+) s", 1), drawn="d['head_radau_onset_cross_s']", tol=("rel", 1e-12))
    R.add("F4", "radau_ms", "Radau minus DOP853 (ms)", round((float(rd["onset_cross_s"]) - float(h["onset_cross_s"])) * 1000.0, 6), s, printed=(r"(\d+) ms against the 1 ms bound", 1), drawn="d['head_radau_minus_default_ms']", tol=1e-6)
    R.add("F4", "head_delay_pred", "predicted delay in eta units", float(h["delay_eta_pred"]), s + ": S5ramp.delay_eta_pred", tol=("rel", 1e-12), drawn="d['head_delay_eta_pred']")
    levels = []
    idents = []
    for lvl, f_ in enumerate(("floor_l0", "floor_l1", "floor_l2")):
        sub = a7[a7["family"] == f_]
        dt0 = sub[np.isclose(sub["heun_dt_tau"].astype(float), 1e-3, rtol=0, atol=0)]
        levels.append((float(np.median(dt0["delay_eta_cross"].astype(float))), float(np.median(dt0["delay_eta"].astype(float)))))
        base, ident = None, True
        for dt in (1e-3, 5e-4, 2.5e-4, 1e-4):
            sd = sub[np.isclose(sub["heun_dt_tau"].astype(float), dt, rtol=0, atol=0)].sort_values("seed")["delay_eta_cross"].astype(float).to_numpy()
            base = sd if base is None else base
            ident &= bool(np.array_equal(base, sd, equal_nan=True))
        idents.append(ident)
        R.add("F4", f"floor{lvl}_dt_identical", f"floor level {lvl}: raw-crossing delays equal at the four Heun dt", ident, s + ": heun_dt_tau, delay_eta_cross")
    R.add("F4", "floor_dt_identical", "raw-crossing delays equal at all four dt for all levels", all(idents), s, drawn="d['floor_dt_identical']")
    pr = [r"(-0\.000760)", r"(-0\.0423)", r"(-0\.1051) in eta"]
    for i, (mc, ml) in enumerate(levels):
        R.add("F4", f"floor{i}_median_cross", f"median raw-crossing delay at floor level {i}", mc, s, printed=(pr[i], 1), tol=("rel", 1e-12), drawn=f"float(d['floor_median_cross'][{i}])")
        R.add("F4", f"floor{i}_median_cls", f"median classifier-onset delay at floor level {i}", ml, s, tol=("rel", 1e-12), shared="stored delay from the frozen classifier onset",
              printed=((r"tie at (-1\.5) at", 1) if i < 2 else None), drawn=f"float(d['floor_median_cls'][{i}])")
    nz = a7[a7["family"] == "p2_noise"]
    R.add("F4", "noise_rows", "noisy ramp runs (13 T_ramp x 10 seeds)", len(nz), s + ": p2_noise", drawn="int(np.size(d['noise_delay_eta_cross']))")
    R.add("F4", "noise_sigma", "noise sigma", float(nz["sigma"].iloc[0]), s + ": p2_noise.sigma", printed=(r"sigma (0\.\d+),", 1), tol=("rel", 1e-12))
    med = nz.groupby("T_ramp_s")["delay_eta_cross"].apply(lambda x: float(np.nanmedian(x.astype(float)))).sort_index()
    ts = list(med.index)
    first = None
    for i in range(len(ts)):
        if all(med.iloc[j] < 0 for j in range(i, len(ts))):
            first = ts[i]
            break
    R.add("F4", "noise_median_negative_from", "smallest T_ramp from which the median raw-crossing delay stays negative (s)", first, s + ": p2_noise.delay_eta_cross", printed=(r"negative from T_ramp (\d+\.\d+) s", 1))
    R.add("F4", "noise_T_ramps", "T_ramp values of the noisy runs", len(ts), s, drawn="len(d['noise_eps'])")
    a3 = c.pq("A3/a3_sn_ramp.parquet").sort_values("T_ramp_s")
    R.add("F4", "m2_rows", "M2 saddle-node ramp runs", len(a3), "A3/a3_sn_ramp.parquet", printed=(r"damped at all (\d+) T_ramp", 1), drawn="len(d['a3_eps'])")
    R.add("F4", "m2_damped", "M2 runs with ring class damped", int((a3["ring_class"] == "damped").sum()), "A3/a3_sn_ramp.parquet: ring_class", shared="stored class column", drawn="sum(1 for x in d['a3_ring_class'] if x == 'damped')")
    m2_eps = [float(c.json(f"A3/S2/{run}.json")["config"]["path"]["eps"]) for run in a3["run"]]           # 13t-9 (DL-680 N1): the ramp rate of each stored M2 run record, read here independently of the draft loader
    R.add("F4", "m2_eps_lo", "smallest ramp rate of the 13 M2 ramp runs (stored run records of the A3 table)", min(m2_eps), "A3/S2/<run>.json: config.path.eps", tol=("rel", 1e-3))
    R.add("F4", "m2_eps_hi", "largest ramp rate of the 13 M2 ramp runs (stored run records of the A3 table)", max(m2_eps), "A3/S2/<run>.json: config.path.eps", tol=("rel", 1e-3))
    R.add("F4", "m2_offset_first", "jump offset from the fold at the smallest T_ramp", float(a3["offset"].iloc[0]), "A3/a3_sn_ramp.parquet: offset", printed=(r"falls from (\d+\.\d+) to", 1))
    R.add("F4", "m2_offset_last", "jump offset from the fold at the largest T_ramp", float(a3["offset"].iloc[-1]), "A3/a3_sn_ramp.parquet: offset", printed=(r"to (\d+\.\d+) \(DL-109", 1))
    for f_ in ("p1_linear", "p1_sigmoid", "p2_linear", "p2_sigmoid", "p5_linear", "p5_sigmoid"):
        sub = a7[a7["family"] == f_].sort_values("T_ramp_s")
        for col in ("delay_eta_cross", "f_pk_hz", "peak_power_abs", "duration_s"):
            R.add("F4", f"{f_}_{col}", f"{col} of {f_} sorted by T_ramp", [float(x) for x in sub[col].astype(float)], s, tol=("rel", 1e-12),
                  drawn=f"[float(x) for x in d['{f_}_{col}'][np.argsort(d['{f_}_T_ramp_s'])]]")


def a7_onset(c: Ctx):
    return float(c.pq("A7/a7_ramp_metrics.parquet").query("family == 'S5ramp'")["onset_s"].iloc[0])


# ---------------------------------------------------------------------------------------------------- F1
def f1(c: Ctx, R: Rows):
    import glob
    rec = "S5/ramp/S5ramp/S5ramp_0000_240de3ef73be"
    z = c.npz(rec + ".npz")
    R.add("F1", "mf_n", "samples of the mean-field headline record", len(z["t_ms"]), rec + ".npz: t_ms", drawn="d['mf_n']")
    for k, nm in (("r_min", "r"), ("r_max", "r"), ("v_min", "v"), ("v_max", "v")):
        fn = np.min if k.endswith("min") else np.max
        R.add("F1", f"mf_{k}", f"{k.split('_')[1]} of {nm} (mean field)", float(fn(z[nm])), rec + f".npz: {nm}", tol=("rel", 1e-12), drawn=f"d['mf_{k}']")
    R.add("F1", "eta_start", "eta at the first sample", float(z["eta"][0]), rec + ".npz: eta", tol=("rel", 1e-12), drawn="d['path_eta_start']")
    R.add("F1", "eta_peak", "largest eta", float(np.max(z["eta"])), rec + ".npz: eta", tol=("rel", 1e-12), drawn="d['path_eta_peak']")
    R.add("F1", "J_start", "J at the first sample", float(z["J"][0]), rec + ".npz: J", tol=("rel", 1e-12), drawn="d['path_J0']")
    R.add("F1", "J_end", "J at the last sample", float(z["J"][-1]), rec + ".npz: J", tol=("rel", 1e-12), drawn="d['path_J_end']")
    cfg = c.json(rec + ".json")["config"]["path"]
    R.add("F1", "t_on", "ramp start t_on (s)", float(cfg["t_on_s"]), rec + ".json:config.path.t_on_s", tol=0.0, drawn="d['path_t_on_s']")
    R.add("F1", "T_ramp", "T_ramp (s)", float(cfg["T_ramp_s"]), rec + ".json:config.path.T_ramp_s", tol=0.0, printed=(r"T_ramp (\d+) s\)", 1), drawn="d['path_T_ramp_s']")
    net = []
    for p in sorted(glob.glob(str(c.res / "S8" / "S8_head" / "*.json"))):
        j = json.loads(Path(p).read_text(encoding="utf-8"))
        net.append((float(j["config"]["path"]["T_ramp_s"]), int(j["seed"]["spawn_key"][-1]), Path(p).stem))
    R.add("F1", "net_records", "stored S8 headline records", len(net), "S8/S8_head/*.json", drawn="6")
    n120 = sorted((s_, n_) for t_, s_, n_ in net if t_ == 120.0)
    for k, (sd, nm) in enumerate(n120):
        zz = c.npz(f"S8/S8_head/{nm}.npz")
        R.add("F1", f"net{k}_n", f"samples of the 120 s network record, seed {sd}", len(zz["r"]), f"S8/S8_head/{nm}.npz: r", drawn=f"d['net{k}_n']")
        for nmv, fn, lab in (("r", np.min, "min"), ("r", np.max, "max"), ("v", np.min, "min"), ("v", np.max, "max")):
            R.add("F1", f"net{k}_{nmv}_{lab}", f"{lab} of {nmv}, network seed {sd}", float(fn(zz[nmv])), f"S8/S8_head/{nm}.npz: {nmv}", tol=("rel", 1e-12), drawn=f"d['net{k}_{nmv}_{lab}']")
    if n120:
        zz = c.npz(f"S8/S8_head/{n120[0][1]}.npz")
        R.add("F1", "ras_spikes", "spikes of the 300 drawn neurons (seed 0)", len(zz["raster_t_ms"]), "raster_t_ms", drawn="len(d['ras_t_s'])")
        R.add("F1", "ras_rows", "drawn neurons", len(zz["raster_j"]), "raster_j", drawn="d['ras_n_rows']")
        R.add("F1", "ras_active", "drawn neurons that spike at least once", len(np.unique(zz["raster_neuron"])), "raster_neuron", drawn="d['ras_n_active_rows']")
    ev = c.json("ms10/eval/ms10_eval.json")["rb1_headline"]
    sh = "stored class and metrics of the original evaluator"
    s120, s10 = ev["120.0"]["seeds"], ev["10.0"]["seeds"]
    mfo = a7_onset(c)
    R.add("F1", "cls120", "classes of the three 120 s network seeds", [x["class"] for x in s120], "ms10_eval.json:rb1_headline.120.0.seeds", shared=sh, drawn="list(d['cls120'])")
    R.add("F1", "n_ssus120", "120 s seeds of class S-sus", sum(1 for x in s120 if x["class"] == "S-sus"), "same", shared=sh, printed=(r"\(all (\d+) are S-sus", 1))
    R.add("F1", "onset120", "classifier onsets of the 120 s seeds (s)", [float(x["onset_s"]) for x in s120], "same", shared=sh, tol=0.0, drawn="[float(x) for x in d['onset120_s']]")
    R.add("F1", "onset120_text", "common classifier onset of the 120 s seeds (s)", sorted(set(float(x["onset_s"]) for x in s120))[0], "same", shared=sh, printed=(r"classifier onset (\d+\.\d) s", 1))
    R.add("F1", "onset_gap", "mean-field onset minus the network classifier onset (s)", mfo - float(s120[0]["onset_s"]), "A7 S5ramp.onset_s minus ms10_eval.json", shared=sh, printed=(r"\((\d+\.\d) s before the mean-field", 1), tol=1e-9)
    for k, x in enumerate(s120):
        R.add("F1", f"fpk120_{k}", f"f_pk of the 120 s seed {k} (Hz)", float(x["f_pk_hz"]), "ms10_eval.json:rb1_headline.120.0.seeds", shared=sh, tol=0.0, printed=(r"f_pk values (\d+\.\d), (\d+\.\d) and (\d+\.\d) Hz", k + 1),
              drawn=f"float(d['fpk120_hz'][{k}])")
    R.add("F1", "cls10", "classes of the three 10 s network seeds", [x["class"] for x in s10], "ms10_eval.json:rb1_headline.10.0.seeds", shared=sh, drawn="list(d['cls10'])")
    for k in range(3):
        R.add("F1", f"cls10_{k}", f"class of 10 s seed {k}", s10[k]["class"], "same", shared=sh, printed=(r"the 3 seeds are (S-\w+), (S-\w+) and (S-\w+) \(", k + 1))
    for T in ("120.0", "10.0"):
        R.add("F1", f"pass_{T}", f"seeds that pass RB1 at T_ramp {T}", int(ev[T]["pass_count"]), f"ms10_eval.json:rb1_headline.{T}.pass_count", shared=sh)
    R.add("F1", "pass_text", "seeds that pass at each T_ramp (A11 text)", _nums(_a11(c, "RB1", "headline_10s")["value"])[0], "A11 RB1.headline_10s", shared="stored A11 table", printed=(r"S-rel and S-sus \((\d+) of 3 seeds match", 1))
    R.add("F1", "ctrl120", "classes of the 120 s no-ramp controls", ev["120.0"]["controls"]["classes"], "ms10_eval.json:rb1_headline.120.0.controls", shared=sh, drawn="d['ctrl120']")
    R.add("F1", "ctrl10", "classes of the 10 s no-ramp controls", ev["10.0"]["controls"]["classes"], "ms10_eval.json:rb1_headline.10.0.controls", shared=sh, drawn="d['ctrl10']")
    R.add("F1", "ref_class", "mean-field reference class", ev["120.0"]["ref"]["class"], "ms10_eval.json:rb1_headline.120.0.ref", shared=sh, drawn="d['ref_class']")
    a7 = c.pq("A7/a7_ramp_metrics.parquet")
    R.add("F1", "ref_fpk", "mean-field spectral peak (Hz), A7 table", float(a7[a7["family"] == "S5ramp"]["f_pk_hz"].iloc[0]), "A7/a7_ramp_metrics.parquet: S5ramp.f_pk_hz", printed=(r"spectral peak of (\d+\.\d) Hz", 1), drawn="d['ref_f_pk_hz']", tol=0.0)
    R.add("F1", "ref_onset", "mean-field onset (s), A7 table", mfo, "A7/a7_ramp_metrics.parquet: S5ramp.onset_s", printed=(r"and onset (\d+\.\d+) s", 1), drawn="d['ref_onset_s']", tol=("rel", 1e-12))
    R.add("F1", "a_ref", "A_ref", float(c.json("A8/a8_aref.json")["chosen"]["A_ref"]), "A8/a8_aref.json:chosen.A_ref", tol=("rel", 1e-12), drawn="d['a_ref']")
    R.add("F1", "rb1_verdict", "RB1 verdict", _a11(c, "RB1", "overall")["pass_or_fail"], "A11 RB1.overall", shared="stored A11 table", drawn="d['rb1_verdict']")
    from mprsurge.analysis import surge_metrics as SM
    fs = 1000.0 / float(c.json(rec + ".json")["config"]["solver"]["dt_out_ms"])
    t, f, S = SM.spectrogram_v(z["v"], fs, 2.0, 1.0)
    R.add("F1", "spec_windows", "windows of the mean-field spectrogram (W 2 s, step 1 s)", len(t), "frozen surge_metrics.spectrogram_v on the stored v", shared="frozen spectrogram routine", drawn="len(d['spec_t_s'])")


# ---------------------------------------------------------------------------------------------------- FS2
def fs2(c: Ctx, R: Rows):
    a4 = c.npz("A4/a4_hopf_curves.npz")
    a5 = c.npz("A5/a5_cycles.npz")
    chk = c.json("A5/check/a5_check.json")
    a6 = c.json("A6/a6_summary.json")
    sh = "stored check file of the original analysis"
    R.add("FS2", "hopf_a4", "Hopf tau_d of ceni from the A4 curves (ms)", float(a4["ceni_hopf_tau_d_ms"][0]), "A4/a4_hopf_curves.npz: ceni_hopf_tau_d_ms", printed=(r"tau_d (\d+\.\d+) ms, not", 1), tol=("rel", 1e-12), drawn="d['hopf_a4_ms']")
    R.add("FS2", "hopf_a5", "Hopf tau_d of ceni from the A5 branch (ms)", float(a5["ceni_hopf_tau_d_ms"][0]) if "ceni_hopf_tau_d_ms" in a5 else float("nan"), "A5/a5_cycles.npz: ceni_hopf_tau_d_ms", tol=("rel", 1e-9), drawn="d['hopf_a5_ms']")
    R.add("FS2", "hopf_check", "Hopf tau_d in the K7 check file (ms)", chk["k7_amplitude"]["hopf_ms"], "A5/check/a5_check.json:k7_amplitude.hopf_ms", tol=("rel", 1e-12), drawn="d['hopf_check_ms']", shared=sh)
    R.add("FS2", "k9_max", "largest Delta/eta_bar (K9)", float(np.max(a4["k9_ratio"])), "A4/a4_hopf_curves.npz: k9_ratio", printed=(r"Delta/eta_bar (0\.\d+) at eta_bar", 1), tol=("rel", 1e-12), drawn="float(np.max(d['k9_ratio']))")
    R.add("FS2", "k9_eta", "eta_bar of the K9 rows", [float(x) for x in a4["k9_eta_bar"]], "A4: k9_eta_bar", tol=0.0, drawn="[float(x) for x in d['k9_eta_bar']]")
    R.add("FS2", "k11_dev", "largest deviation of Im lambda/(2 pi r*) from 1 (K11)", float(np.max(np.abs(np.asarray(a4["k11_ratio"], float) - 1.0))), "A4: k11_ratio", printed=(r"deviation from 1 (\d\.\de-\d)", 1),
          tol=("rel", 1e-12), drawn="d['k11_max_dev']")
    R.add("FS2", "k11_n", "K11 rows", len(a4["k11_ratio"]), "A4: k11_ratio", drawn="len(d['k11_ratio'])")
    for J, pat in (("8.0", r"frequency is (\d+\.\d), "), ("20.0", r"frequency is \d+\.\d, (\d+\.\d) and"), ("40.0", r"and (\d+\.\d) percent at 8")):
        fr = np.asarray(a6["k10"]["J_dependence"][J]["linear_freq_hz"], float)
        R.add("FS2", f"k10_{J}", f"relative change of the linear frequency with J at tau_d {J} ms (percent)", 100.0 * float((fr.max() - fr.min()) / fr.mean()), "A6/a6_summary.json:k10.J_dependence.*.linear_freq_hz",
              printed=(pat, 1), tol=("rel", 1e-9), drawn=f"100*d['k10_rel_change_{J}']")
    sn = c.json("S3/s3_net_summary.json")["K8"]
    R.add("FS2", "k8_rel", "K8 network frequency relative to the mean field (percent, absolute)", 100.0 * abs((sn["f_net_hz"] - sn["f_mf_hz"]) / sn["f_mf_hz"]), "S3/s3_net_summary.json:K8", printed=(r"within (0\.\d+) percent", 1),
          tol=("rel", 1e-9), drawn="-100*d['k8_net_rel_diff']")
    R.add("FS2", "k8_tol", "K8 tolerance (percent)", 100.0 * float(sn["tol"]), "S3/s3_net_summary.json:K8.tol", printed=(r"tolerance (\d+) percent;", 1), drawn="100*d['k8_net_tol']", tol=1e-9)
    R.add("FS2", "k7_resid", "K7 largest residual of the amplitude-squared line (percent)", 100.0 * chk["k7_amplitude"]["s4_up"]["max_resid_frac"], "A5/check/a5_check.json:k7_amplitude.s4_up", shared=sh,
          printed=(r"residual rule,? \(?(\d+\.\d+) against", 1), tol=("rel", 1e-9), drawn="100*d['fit_s4_up_max_resid_frac']")
    R.add("FS2", "k7_bound", "K7 residual bound (percent)", 100.0 * float(chk["rel_tol"]), "A5/check/a5_check.json:rel_tol", printed=(r"against (\d+) percent", 1), shared=sh, tol=1e-9)
    R.add("FS2", "k7_fit_points", "K7 fit points (S4 up)", int(chk["k7_amplitude"]["s4_up"]["n_points"]), "A5/check/a5_check.json", shared=sh, drawn="int(d['fit_s4_up_n_points'])")


# ---------------------------------------------------------------------------------------------------- FS3
def fs3(c: Ctx, R: Rows):
    tsv = c.csv("ms10/10g/record_classes.tsv", "\t")
    sh = "stored class column of the original evaluator"
    pats = [r"in (\d+), \d+, \d+ and \d+ of 10 seeds", r"in \d+, (\d+), \d+ and \d+ of 10 seeds", r"in \d+, \d+, (\d+) and \d+ of 10 seeds", r"in \d+, \d+, \d+ and (\d+) of 10 seeds"]
    cpat = {3000: r"\((\d+) of 3 at 3e3", 10000: r"(\d+) of 3 at 1e4"}
    for i, N in enumerate((1000, 3000, 10000, 30000)):
        cl = [r["class"] for r in tsv if r["list"] == "S9" and int(r["N"]) == N]
        R.add("FS3", f"s9_surge_N{N}", f"S9 seeds in a surge class at N = {N}", sum(1 for x in cl if x in SURGE), "ms10/10g/record_classes.tsv", shared=sh, drawn=f"int(d['s9_surge'][{i}])", printed=(pats[i], 1))
        R.add("FS3", f"s9_n_N{N}", f"S9 records at N = {N}", len(cl), "ms10/10g/record_classes.tsv", shared=sh, drawn=f"int(d['s9_seeds'][{i}])")
        for k, kl in enumerate(CLASSES):
            R.add("FS3", f"s9_N{N}_{kl}", f"S9 seeds of class {kl} at N = {N}", cl.count(kl), "ms10/10g/record_classes.tsv", shared=sh, drawn=f"int(d['s9_count'][{i}][{k}])")
        cc = [r["class"] for r in tsv if r["list"] == "C2_S9" and int(r["N"]) == N]
        R.add("FS3", f"ctrl_surge_N{N}", f"no-ramp controls in a surge class at N = {N}", sum(1 for x in cc if x in SURGE), "ms10/10g/record_classes.tsv", shared=sh, drawn=f"int(d['s9_ctrl_surge'][{i}])",
              printed=((cpat[N], 1) if N in cpat else None))
        R.add("FS3", f"ctrl_n_N{N}", f"no-ramp control records at N = {N}", len(cc), "ms10/10g/record_classes.tsv", shared=sh, drawn=f"int(d['s9_ctrl_n'][{i}])")
    n4 = sum(1 for r in tsv if r["list"] == "S9" and int(r["N"]) == 10000 and r["class"] in SURGE)
    n3 = sum(1 for r in tsv if r["list"] == "S9" and int(r["N"]) == 30000 and r["class"] in SURGE)
    R.add("FS3", "nrule_1e4", "S9 surge seeds at N = 1e4 (N rule)", n4, "ms10/10g/record_classes.tsv", shared=sh, printed=(r"against (\d+) at 1e4", 1), drawn="d['nrule_count_1e4']")
    R.add("FS3", "nrule_3e4", "S9 surge seeds at N = 3e4 (N rule)", n3, "ms10/10g/record_classes.tsv", shared=sh, printed=(r"passes \((\d+) seeds at 3e4", 1), drawn="d['nrule_count_3e4']")
    for shape in ("gaussian", "uniform"):
        cl = [r["class"] for r in tsv if r["list"] == "S10" and r["shape"] == shape]
        R.add("FS3", f"s10_{shape}_sabs", f"S10 {shape} seeds of class S-abs", cl.count("S-abs"), "ms10/10g/record_classes.tsv", shared=sh, printed=((r"Gaussian and uniform give S-abs in (\d+) of 3", 1) if shape == "gaussian" else None))
    lo = [x["class"] for x in sorted((r for r in tsv if r["list"] == "S10" and r["shape"] == "lorentzian"), key=lambda r: int(r["seed"]))]
    for k in range(3):
        R.add("FS3", f"s10_lor_{k}", f"S10 Lorentzian seed {k} class", lo[k], "ms10/10g/record_classes.tsv", shared=sh, printed=(r"Lorentzian seeds give (S-\w+), (S-\w+), (S-\w+), so", k + 1))
    ev = c.json("A11/a11_evaluators.json")["evaluators"]["rb2"]
    sh2 = "stored A11 evaluator output (rb2)"
    gate = {g["sigma_factor"]: g for g in ev["gate"]}
    R.add("FS3", "s11_kept_05", "S11 seeds that keep the headline class at 0.5 sigma", gate[0.5]["kept"], "A11/a11_evaluators.json:rb2.gate", shared=sh2, printed=(r"kept in (\d+) of 10 seeds at 0\.5 sigma", 1), drawn="int(d['gate_kept'][0])")
    R.add("FS3", "s11_kept_10", "S11 seeds that keep the headline class at sigma", gate[1.0]["kept"], "A11/a11_evaluators.json:rb2.gate", shared=sh2, printed=(r"and (\d+) of 10 at sigma \(FAIL\)", 1), drawn="int(d['gate_kept'][1])")
    for g in ev["controls"]:
        R.add("FS3", f"s11_ctrl_{g['sigma_factor']}", f"constant-parameter controls that reach the primary reading at sigma factor {g['sigma_factor']}", g["kept_primary"], "A11/a11_evaluators.json:rb2.controls", shared=sh2,
              printed=((r"controls reach (\d+) of 10 at every sigma", 1) if g["sigma_factor"] == 0.5 else None))
    sg = c.pq("A9/a9_subgrid_agreement.parquet")
    R.add("FS3", "subgrid_agree", "subgrid cells that agree (D24)", int(sg["d24_cell_agrees"].astype(bool).sum()), "A9/a9_subgrid_agreement.parquet", printed=(r"in (\d+) of 225 cells against", 1), drawn="d['subgrid_agree']")
    R.add("FS3", "subgrid_cells", "subgrid cells", len(sg), "A9/a9_subgrid_agreement.parquet", printed=(r"in \d+ of (\d+) cells against", 1), drawn="d['subgrid_cells']")
    R.add("FS3", "subgrid_needed", "subgrid cells needed", math.ceil(0.9 * len(sg)), "A9/a9_subgrid_agreement.parquet", printed=(r"cells against (\d+) needed", 1), drawn="d['subgrid_needed']")
    R.add("FS3", "rb8_verdict", "RB8 verdict", c.json("ms10/eval/ms10_eval.json")["rb8"]["verdict"], "ms10_eval.json:rb8.verdict", shared="stored evaluator output", drawn="d['rb8_verdict']")


# ---------------------------------------------------------------------------------------------------- FS4
def fs4(c: Ctx, R: Rows):
    a7 = c.pq("A7/a7_ramp_metrics.parquet")
    s = "A7/a7_ramp_metrics.parquet"
    head = a7[a7["family"].isin(["S5ramp", "delta0", "rtol", "radau"])]
    R.add("FS4", "head_rows", "headline numerics rows (S5ramp, delta0 x 2, rtol x 2, radau)", len(head), s + ": family", drawn="len(d['head_class'])")
    R.add("FS4", "head_Dtr", "headline numerics rows of class D-tr", int((head["cls"] == "D-tr").sum()), s + ": cls", shared="stored class column", drawn="sum(1 for x in d['head_class'] if x == 'D-tr')")
    on = head[head["family"] != "radau"]["onset_cross_s"].astype(float)
    base_on = float(head[head["family"] == "S5ramp"]["onset_cross_s"].iloc[0])
    R.add("FS4", "onset_common", "raw-crossing onset of the five non-Radau rows (s), largest spread", float(on.max() - on.min()), s, tol=0.0)
    R.add("FS4", "onset_default", "raw-crossing onset, default settings (s)", base_on, s, printed=(r"onset is (\d+\.\d+) s everywhere", 1), tol=("rel", 1e-12))
    rad = float(head[head["family"] == "radau"]["onset_cross_s"].iloc[0])
    R.add("FS4", "onset_radau", "Radau raw-crossing onset (s)", rad, s, printed=(r"Radau gives onset (\d+\.\d+) s", 1), tol=("rel", 1e-12))
    R.add("FS4", "radau_ms", "Radau minus default (ms)", round((rad - base_on) * 1000.0, 6), s, printed=(r"(\d+) ms against the 1 ms bound", 1), drawn="d['head_radau_minus_default_ms']", tol=1e-6)
    for lvl in ("floor_l0", "floor_l1", "floor_l2"):
        sub = a7[a7["family"] == lvl]
        base, same_ = None, True
        for dt in (1e-3, 5e-4, 2.5e-4, 1e-4):
            v = sub[np.isclose(sub["heun_dt_tau"].astype(float), dt, rtol=0, atol=0)].sort_values("seed")["delay_eta_cross"].astype(float).to_numpy()
            base = v if base is None else base
            same_ &= bool(np.array_equal(base, v, equal_nan=True))
        R.add("FS4", f"{lvl}_dt_same", f"{lvl}: floored delay unchanged across the four Heun dt", same_, s)
    ev = c.json("A11/a11_evaluators.json")["evaluators"]
    sh = "stored A11 evaluator output (rb6_network)"
    pr = ev["rb6_network"]["per_reading"]
    ce = pr["classifier_episode_fpk"]
    rel = [abs(float(r["rel"])) for r in ce["rows"] if r.get("rel") is not None]
    R.add("FS4", "net_ce_pass", "seeds that pass the classifier-episode f_pk bound", int(ce["n_pass"]), "A11/a11_evaluators.json:rb6_network", shared=sh, printed=(r"(\d+) of 3 seeds pass[;)]", 1), drawn="d['net_ce_n_pass']")
    psd_key = [k for k in pr if k != "classifier_episode_fpk"][0]
    R.add("FS4", "net_psd_pass", "seeds that pass the PSD-argmax f_pk bound", int(pr[psd_key]["n_pass"]), "A11/a11_evaluators.json:rb6_network", shared=sh, printed=(r"passes in (\d+) of 3", 1), drawn="d['net_psd_n_pass']")
    R.add("FS4", "net_rel_min", "smallest classifier-episode f_pk change (percent, rounded)", int(round(100 * min(rel))), "A11/a11_evaluators.json:rb6_network", shared=sh, printed=(r"by (\d+) to \d+ percent against", 1))
    R.add("FS4", "net_rel_max", "largest classifier-episode f_pk change (percent, rounded)", int(round(100 * max(rel))), "A11/a11_evaluators.json:rb6_network", shared=sh, printed=(r"by \d+ to (\d+) percent against", 1))
    R.add("FS4", "net_status", "RB6 network row status", ev["rb6_network"]["status"], "A11/a11_evaluators.json:rb6_network", shared=sh, drawn="d['net_status']")
    d5 = ev["rb5_delta0"]["rows"]
    R.add("FS4", "rb5_delta0_rows", "rows of the RB5 delta0 evaluation", len(d5), "A11/a11_evaluators.json:rb5_delta0", shared=sh)
    R.add("FS4", "rb5_delta0_Dtr", "RB5 delta0 rows of class D-tr", sum(1 for r in d5 if r["class"] == "D-tr"), "A11/a11_evaluators.json:rb5_delta0", shared=sh)
    R.add("FS4", "rb5_delta0_shift", "RB5 delta0 largest absolute onset shift (s)", max(abs(float(r["onset_shift_s"])) for r in d5), "A11/a11_evaluators.json:rb5_delta0", shared=sh, tol=0.0)


# ---------------------------------------------------------------------------------------------------- FS5
def fs5(c: Ctx, R: Rows):
    s8 = c.csv("A8/a8_sensitivity.csv")
    s = "A8/a8_sensitivity.csv"
    syn = {r["record"] for r in s8 if r["dataset"] == "synthetic"}
    variants = sorted({r["variant"] for r in s8})
    R.add("FS5", "rows", "stored classifications", len(s8), s)
    R.add("FS5", "synthetic_cases", "synthetic cases", len(syn), s + ": dataset, record", printed=(r"on (\d+) synthetic cases", 1))
    R.add("FS5", "variants", "variants of the classifier (V0 and the changed ones)", len(variants), s + ": variant", drawn="len(d['variants'])")
    wn = c.csv("A8/sensitivity/a8_whitenoise.csv")
    Ws = sorted({float(r["W_s"]) for r in wn})
    wp = [r"(\d+), \d+, \d+ and \d+ of 500", r"\d+, (\d+), \d+ and \d+ of 500", r"\d+, \d+, (\d+) and \d+ of 500", r"\d+, \d+, \d+ and (\d+) of 500"]
    for k, W in enumerate(Ws):
        rows_ = [r for r in wn if float(r["W_s"]) == W and r["variant"] == "V0"]
        den = int(rows_[0]["denominator"])
        ns = sum(int(r["count"]) for r in rows_ if r["class"] == "NS")
        R.add("FS5", f"white_nonNS_W{W:.3f}", f"white-noise records not NS at W = {W:.3f} s (variant V0)", den - ns, "A8/sensitivity/a8_whitenoise.csv", drawn=f"int(d['white_nonNS'][{k}])", printed=((wp[k], 1) if k < 4 else None))
        R.add("FS5", f"white_den_W{W:.3f}", f"white-noise records at W = {W:.3f} s", den, "A8/sensitivity/a8_whitenoise.csv", drawn=f"int(d['white_den'][{k}])")
    ev = c.json("A11/a11_evaluators.json")["evaluators"]
    sh = "stored A11 evaluator output"
    rb10 = ev["rb10"]["variants"]
    R.add("FS5", "rb10_worst", "largest fraction of map-1 cells that change class under a variant (percent)", 100.0 * max(float(v["worst_fraction"]) for v in rb10.values()), "A11/a11_evaluators.json:rb10", shared=sh,
          printed=(r"at most (\d+\.\d+) percent of the 900", 1), tol=0.005)
    R.add("FS5", "rb10_cells", "map-1 cells evaluated for RB10", int(max(v["n_evaluated"] for v in rb10.values())), "A11/a11_evaluators.json:rb10", shared=sh, printed=(r"of the (\d+) map-1 cells", 1), drawn="d['rb10_n_cells']")
    R.add("FS5", "rb10_variants", "variants evaluated for RB10", len(rb10), "A11/a11_evaluators.json:rb10", shared=sh, drawn="len(d['rb10_variant'])")
    R.add("FS5", "rb10_headline_all_pass", "headline class unchanged under all variants", all(v["headline"] == "PASS" for v in rb10.values()), "A11/a11_evaluators.json:rb10", shared=sh, drawn="d['rb10_headline_all_pass']")
    ru = c.json("A11/rb9a_unit_level.json")
    R.add("FS5", "rb9a_value", "RB9(a) unit-level largest relative difference", float(ru["max_rel_diff"]), "A11/rb9a_unit_level.json:max_rel_diff", printed=(r"\((\d\.\de-\d) against", 1), tol=("rel", 1e-12), drawn="d['rb9a_value']")
    R.add("FS5", "rb9a_tol", "RB9(a) frozen tolerance", float(ru["tolerance_frozen"]), "A11/rb9a_unit_level.json:tolerance_frozen", printed=(r"against (0\.\d+);", 1), tol=0.0, drawn="d['rb9a_tol']")
    c9 = ev["rb9c"]
    R.add("FS5", "rb9c_changed", "RB9(c) map-1 cells changed", int(c9["n_changed"]), "A11/a11_evaluators.json:rb9c", shared=sh, printed=(r"RB9\(c\) passes \((\d+) of", 1))
    R.add("FS5", "rb9c_cells", "RB9(c) map-1 cells evaluated", int(c9["n_evaluated"]), "A11/a11_evaluators.json:rb9c", shared=sh, printed=(r"RB9\(c\) passes \(\d+ of (\d+) cells", 1))
    a9 = c.pq("A9/a9_regime_map_v2.parquet")
    hl = a9[a9["headline_marker"].fillna(False).astype(bool)].iloc[0]
    R.add("FS5", "rb9b_spectral", "spectral peak of the headline (Hz), A9 table", float(hl["f_pk_hz"]), "A9/a9_regime_map_v2.parquet: headline row f_pk_hz", printed=(r"\((\d+\.\d) Hz spectral peak", 1), tol=0.0, drawn="d['rb9b_f_spectral']")
    rec = "S5/ramp/S5ramp/S5ramp_0000_240de3ef73be"
    h7 = c.pq("A7/a7_ramp_metrics.parquet").query("family == 'S5ramp'").iloc[0]
    from mprsurge.analysis import surge_metrics as SM
    fs = 1000.0 / float(c.json(rec + ".json")["config"]["solver"]["dt_out_ms"])
    ph = np.unwrap(np.angle(SM._analytic(np.asarray(c.npz(rec + ".npz")["v"], float), fs, SM.G_BAND)))
    a_, b_ = max(0, int(round(float(h7["onset_s"]) * fs))), min(len(ph) - 1, int(round(float(h7["end_s"]) * fs)))
    fc = float((ph[b_] - ph[a_]) / (2 * np.pi) / ((b_ - a_) / fs))
    shf = "frozen band-pass analytic signal (surge_metrics._analytic, band G)"
    R.add("FS5", "rb9b_cycle", "cycle frequency over the flagged episode of the headline (Hz)", fc, "S5ramp .npz v, A7 S5ramp onset_s and end_s; phase change of the analytic signal", shared=shf, printed=(r"against a (\d+\.\d+) Hz cycle", 1),
          tol=("rel", 1e-9), drawn="d['rb9b_f_cycle']")
    R.add("FS5", "rb9b_diff", "spectral peak minus cycle frequency (Hz)", abs(float(hl["f_pk_hz"]) - fc), "same", shared=shf, printed=(r"frequency, (\d+\.\d+) Hz against 1/W", 1), tol=("rel", 1e-9), drawn="d['rb9b_diff']")
    R.add("FS5", "rb9b_bound", "RB9(b) bound 1/W (Hz), W = 2 s", 1.0 / 2.0, "frozen window W = 2 s for T_ramp 120 s", shared="frozen window rule", printed=(r"against 1/W = (0\.\d+) Hz", 1), drawn="d['rb9b_bound']", tol=0.0)
    R.add("FS5", "map1_surge_cells", "map-1 D-tr cells", int(((a9["map"].astype(str) == "1") & (a9["class"] == "D-tr")).sum()), "A9 table", drawn="d['rb9b_map1_n']")
    R.add("FS5", "map2_surge_cells", "map-2 D-tr cells", int(((a9["map"].astype(str) == "2") & (a9["class"] == "D-tr")).sum()), "A9 table", drawn="d['rb9b_map2_n']")


FUNCS = {"F1": f1, "F2": f2, "F3": f3, "F4": f4, "F5": f5, "F6": f6, "FS1": fs1, "FS2": fs2, "FS3": fs3, "FS4": fs4, "FS5": fs5}


# ---------------------------------------------------------------------------------------------------- journal captions (13t-1d, DL-571 T9, DL-572)
JOURNAL_FIGURES = ("F1", "F2", "F3", "F4a", "F4b", "F5", "F5c", "F6", "FS1", "FS2", "FS3", "FS4", "FS5")             # the journal files whose captions are searched (F5c is the second file of the F5 build)
SIGMA_NOTE = r"mean-field baseline std ([0-9.]+) against the network range ([0-9.]+) to ([0-9.]+)"
# Patterns of the JOURNAL caption that differ from the draft pattern (`printed`) because the plain journal wording differs; the numbers sought are the same, the values are the stored ones,
# nothing is loosened. A row of F1, F3 or F5 with a `printed` pattern and no entry here is searched in the journal caption with its draft pattern.
JOURNAL_OVERRIDE = {
    "F1.onset120_text": (r"classifier onset is (\d+\.\d) s", 1),
    "F3.ref_fmin": (r"cycle at the reference validation point at (\d+\.\d) to", 1),
    "F3.ref_fmax": (r"cycle at the reference validation point at \d+\.\d to (\d+\.\d) Hz", 1),
    "F5.d24_needed": (r"%, (\d+) cells needed", 1),
    "F5.ramp_N3000_S+": (r"S\+ in (\d+) seeds at N = 3000", 1),            # DL-592 V4: the captions write 3000 and 10,000, not 3e3 and 1e4 (same numbers)
    "F5.ramp_N10000_NS": (r"NS in (\d+) at N = 10,000", 1),
    # 13t-2 (DL-616 B4): F2 and F6; the numbers sought are the same, the wording is plain (no NC1, no step names)
    "F2.a5_vs_s4": (r"differs by at most (\d+\.\d+e-\d+)", 1),
    "F6.nc1_mf_none": (r"mean-field first negative control is D-none at (\d+) of \d+ ramp", 1),
    "F6.nc1_mf_n": (r"mean-field first negative control is D-none at \d+ of (\d+) ramp", 1),
    "F6.nc3_none": (r"third negative control is D-none at (\d+) of \d+", 1),
    "F6.nc3_n": (r"third negative control is D-none at \d+ of (\d+)", 1),
    "F6.nc2_tr": (r"second negative control is D-tr at (\d+) of \d+ ramp", 1),
    "F6.nc2_n": (r"second negative control is D-tr at \d+ of (\d+) ramp", 1),
    "F6.nc1_net_class": (r"is in class (S\+)", 1),
    # 13t-6 (DL-651 H2): FS2 one caption in plain words; the numbers sought are the same stored values
    "FS2.k9_max": (r"Hopf curve \((0\.\d+) at eta_bar", 1),
    "FS2.k11_dev": (r"largest deviation from 1: (0\.\d+)\)", 1),
    "FS2.k10_8.0": (r"the frequency changes by (\d+\.\d), ", 1),
    "FS2.k10_20.0": (r"the frequency changes by \d+\.\d, (\d+\.\d) and", 1),
    "FS2.k10_40.0": (r"and (\d+\.\d) percent at tau_d 8", 1),
    "FS2.k8_tol": (r"tolerance (\d+) percent\)", 1),
    # 13t-6 (DL-651 H2): FS3 one caption; N written 3000, 10,000 and 30,000 (DL-592 V4), the same stored numbers
    "FS1.k4_rel_freq": (r"differ from the linearised ones by (\d+\.\d+e-\d+) and", 1),       # 13t-8b (K5): the take-home and the (d) sentence say the same
    "FS1.k4_rel_decay": (r"differ from the linearised ones by \d+\.\d+e-\d+ and (\d+\.\d+e-\d+)", 1),
    "FS3.ctrl_surge_N3000": (r"\((\d+) of 3 at 3000", 1),
    "FS3.ctrl_surge_N10000": (r"(\d+) of 3 at 10,000", 1),
    "FS3.nrule_1e4": (r"against (\d+) at 10,000", 1),
    "FS3.nrule_3e4": (r"passes \((\d+) seeds at 30,000", 1),
    "FS3.s11_ctrl_0.5": (r"constant parameters reach (\d+) of 10 at every sigma", 1),
    "FS3.subgrid_agree": (r"in (\d+) of 225 cells \(", 1),
    "FS3.subgrid_cells": (r"in \d+ of (\d+) cells \(", 1),
    "FS3.subgrid_needed": (r"percent\) against (\d+) needed", 1),
    "FS3.s11_kept_10": (r"and (\d+) of 10 at sigma \(", 1),
    "FS2.k7_resid": (r"leaves a residual of (\d+\.\d+) percent against", 1),
    # 13t-9 (DL-681 N4): FS4 one caption in plain words; the numbers sought are the same stored values
    "FS4.onset_radau": (r"and (\d+\.\d+) s, \d+ ms apart", 1),
    "FS4.radau_ms": (r"(\d+) ms apart against", 1),
    "FS4.net_rel_min": (r"by (\d+) to \d+ percent when", 1),
    "FS4.net_rel_max": (r"by \d+ to (\d+) percent when", 1),
    # 13t-9 (DL-681 N4): FS5 one caption; the band check is named in plain words
    "FS5.rb9b_spectral": (r"is at (\d+\.\d) Hz and the cycle", 1),
    "FS5.rb9b_cycle": (r"oscillate\) is (\d+\.\d+) Hz, a difference", 1),
    "FS5.rb9b_diff": (r"a difference of (\d+\.\d+) Hz against", 1),
    "FS5.rb9b_bound": (r"allowed 1/W = (0\.\d+) Hz", 1),
    "FS5.rb9c_changed": (r"band check passes \((\d+) of", 1),
    "FS5.rb9c_cells": (r"band check passes \(\d+ of (\d+) cells", 1),
}
JOURNAL_TARGETS = {"F5.rb1_cells": ("F5", "F5c"), "F5.rb1_cells_den": ("F5", "F5c"), "F5.cells_disagree": ("F5", "F5c"), "F5.ramp_N3000_S+": ("F5", "F5c"), "F5.ramp_N10000_NS": ("F5", "F5c")}


def journal_rows(c: Ctx, R: Rows, figures) -> None:
    """Rows that exist only in the journal captions (T2: the stored sigma check and RB3(a) rows; T7: the RB9(b) frequencies and the stored points of the A4 curve; T4: the sentence 1 of F5) and the
    journal pattern of every row of F1, F3, F5 that has a draft pattern. Values come from the stored files (own readers)."""
    import re
    a11 = c.csv("A11/a11_robustness.csv")
    sig = next(r for r in a11 if r["rb_id"] == "sigma_check" and r["check_id"] == "S8_baseline_std")
    m = re.search(SIGMA_NOTE.replace(r"([0-9.]+) to ([0-9.]+)", r"\[([0-9.eE+-]+), ([0-9.eE+-]+)\]"), sig["note"])
    sh = "stored A11 table (original evaluator output)"
    src = "A11/a11_robustness.csv: sigma_check.S8_baseline_std note, pass_or_fail, logged_verdict"
    rb3 = next(r for r in a11 if r["rb_id"] == "RB3" and r["check_id"] == "a_inrange_runs")
    q = _nums(rb3["value"])
    for fig, targets in (("F1", ("F1",)), ("F5", ("F5", "F5c"))):
        if fig not in figures:
            continue
        R.add(fig, "sigma_mf_std", "mean-field baseline std of the sigma check", float(m.group(1)), src, shared=sh, jprinted=(SIGMA_NOTE, 1), jtargets=targets)
        R.add(fig, "sigma_net_lo", "lower end of the network baseline std range", float(m.group(2)), src, shared=sh, jprinted=(SIGMA_NOTE, 2), jtargets=targets)
        R.add(fig, "sigma_net_hi", "upper end of the network baseline std range", float(m.group(3)), src, shared=sh, jprinted=(SIGMA_NOTE, 3), jtargets=targets)
        R.add(fig, "sigma_status", "status of the sigma check", sig["pass_or_fail"], src, shared=sh, jprinted=(r"sigma check on the baseline standard deviation: (\w+), logged verdict", 1), jtargets=targets)
        R.add(fig, "sigma_verdict", "logged verdict of the sigma check", sig["logged_verdict"], src, shared=sh, jprinted=(r"logged verdict ([A-Z ]+?);", 1), jtargets=targets)
    if "F1" in figures:
        R.add("F1", "rb3a_n", "RB3(a) testable in-range runs that match", q[0], "A11/a11_robustness.csv: RB3.a_inrange_runs value", shared=sh,
              jprinted=(r"RB3\(a\) onset prediction on the testable in-range runs \((\d+) of \d+\)", 1))
        R.add("F1", "rb3a_den", "RB3(a) testable in-range runs", q[1], "A11/a11_robustness.csv: RB3.a_inrange_runs value", shared=sh,
              jprinted=(r"RB3\(a\) onset prediction on the testable in-range runs \(\d+ of (\d+)\)", 1))
    if "F3" in figures:
        ev = c.json("A11/a11_evaluators.json")["evaluators"]["rb9b"]["headline"]
        s9 = "A11/a11_evaluators.json:evaluators.rb9b.headline"
        sh2 = "stored evaluator output (A11)"
        R.add("F3", "rb9b_spectral", "RB9(b) spectral frequency at the headline (Hz)", ev["f_spectral_hz"], s9, shared=sh2, tol=0.0,
              jprinted=(r"spectral peak is (\d+\.\d) Hz and the cycle frequency is", 1))
        R.add("F3", "rb9b_cycle", "RB9(b) cycle frequency at the headline (Hz)", ev["f_cycle_hz"], s9, shared=sh2, tol=("rel", 1e-12), jprinted=(r"the cycle frequency is (\d+\.\d+) Hz", 1))
        R.add("F3", "rb9b_diff", "RB9(b) difference spectral minus cycle (Hz)", ev["diff_hz"], s9, shared=sh2, tol=("rel", 1e-12), jprinted=(r"headline: (\d+\.\d+) Hz against 0\.5 Hz", 1))
        R.add("F3", "rb9b_bound", "RB9(b) bound (Hz)", ev["bound_hz"], s9, shared=sh2, tol=0.0, jprinted=(r"Hz against (\d+\.\d) Hz\)", 1))
        a4 = c.npz("A4/a4_hopf_curves.npz")
        R.add("F3", "a4_points", "stored points of the A4 Hopf curve in (eta_bar, tau_d)", len(a4["curve_tau_d_ms"]), "A4/a4_hopf_curves.npz: curve_tau_d_ms",
              jprinted=(r"straight segments between its (\d+) stored points", 1))
    if "F5" in figures:
        sg = c.pq("A9/a9_subgrid_agreement.parquet")
        n, ag = len(sg), int(sg["d24_cell_agrees"].astype(bool).sum())
        pat = (r"noisy subgrid agrees in (\d+) of (\d+) cells \((\d+\.\d) percent; (\d+) cells needed\)")
        for k, (nm, val, qty) in enumerate((("s1_agree", ag, "cells that agree (sentence 1)"), ("s1_sub_n", n, "subgrid cells (sentence 1)"), ("s1_pct", 100.0 * ag / n, "percent that agree (sentence 1)"),
                                            ("s1_needed", math.ceil(0.9 * n), "cells needed (sentence 1)")), start=1):
            R.add("F5", nm, qty, val, "A9/a9_subgrid_agreement.parquet: d24_cell_agrees", printed=(pat, k), jprinted=(pat, k), jtargets=("F5",))
    for r in R:
        if r["figure"] in ("F1", "F2", "F3", "F5", "F6", "FS1", "FS2", "FS3", "FS4", "FS5") and r["figure"] in figures and r["jprinted"] is None and r["printed"] is not None:
            r["jprinted"] = JOURNAL_OVERRIDE.get(r["id"], r["printed"])
            r["jtargets"] = JOURNAL_TARGETS.get(r["id"], (r["figure"],))
        if r["jprinted"] is not None and r["jtargets"] is None:
            r["jtargets"] = (r["figure"],)
    f4_text_patterns(R, figures)


# 13t-8b (DL-671): the F4a and F4b captions. Each F4 row that a caption states gets a pattern of the plain journal wording (full caption: jprinted; short caption: sprinted) and its target file; the numbers
# sought are the same stored values, nothing is loosened. The minus sign of the journal captions is U+2212 (compare.printed_same reads it as a minus).
_F4_SKIP = r"\d+\.\d(?:, | and )"
F4_J = {
    "F4.n_testable": ((r"0 of (\d+) testable in-range runs", 1), ("F4a",), (r"none of the (\d+) testable runs", 1)),
    "F4.n_within": ((r"(\d+) of \d+ testable in-range runs within one step", 1), ("F4a",), None),
    "F4.n_const": ((r"diamond ring marks the (\d+) in-range runs that are not testable", 1), ("F4a",), (r"diamond: not testable, (\d+) runs", 1)),
    "F4.head_onset": ((r"has its onset at (\d+\.\d+) s", 1), ("F4a",), None),
    "F4.head_pred": ((r"predicted entry at (\d+\.\d) s", 1), ("F4a",), None),
    "F4.head_dop": ((r"the two solvers give the onsets (\d+\.\d+) s and", 1), ("F4a",), (r"solver \((\d+\.\d+) s and", 1)),
    "F4.head_radau": ((r"the two solvers give the onsets \d+\.\d+ s and (\d+\.\d+) s", 1), ("F4a",), (r"s and (\d+\.\d+) s, unexplained", 1)),
    "F4.radau_ms": ((r"differ by (\d+) ms at the main example", 1), ("F4a",), (r"differ by (\d+) ms at the main example", 1)),
    "F4.floor0_median_cross": ((r"The medians of \(d\) are (−0\.000760)", 1), ("F4a",), None),
    "F4.floor1_median_cross": ((r"The medians of \(d\) are −0\.000760, (−0\.0423)", 1), ("F4a",), None),
    "F4.floor2_median_cross": ((r"The medians of \(d\) are −0\.000760, −0\.0423 and (−0\.1051)", 1), ("F4a",), None),
    "F4.floor0_median_cls": ((r"tie at (−1\.5) at", 1), ("F4a",), (r"delays are equal at (−1\.5) at", 1)),
    "F4.floor1_median_cls": ((r"tie at (−1\.5) at levels 0 and 1", 1), ("F4a",), None),
    "F4.noise_sigma": ((r"sigma = (0\.\d+),", 1), ("F4b",), (r"sigma = (0\.\d+) the main example", 1)),
    "F4.noise_median_negative_from": ((r"negative from T_ramp (\d+\.\d+) s", 1), ("F4b",), (r"negative from T_ramp (\d+\.\d+) s", 1)),
    "F4.m2_rows": ((r"damped at all (\d+) ramp durations", 1), ("F4b",), None),
    "F4.m2_damped": ((r"so the ring is damped at (\d+) of \d+", 1), ("F4b",), (r"\(negative: damped\) at (\d+) of \d+", 1)),          # 13t-9: the short caption says (negative: damped) at 13 of 13 ramp durations
    "F4.m2_eps_lo": ((r"values from (\d+\.\d+e-\d+) to", 1), ("F4b",), None),          # 13t-9 (DL-680 N1): the M2 ramp-rate range of (f), in the full caption only
    "F4.m2_eps_hi": ((r"values from \d+\.\d+e-\d+ to (\d+\.\d+),", 1), ("F4b",), None),
    "F4.m2_offset_first": ((r"falls from (\d+\.\d+) to", 1), ("F4b",), (r"falls from (\d+\.\d+) to", 1)),
    "F4.m2_offset_last": ((r"falls from \d+\.\d+ to (\d+\.\d+)", 1), ("F4b",), (r"falls from \d+\.\d+ to (\d+\.\d+)", 1)),
}


def f4_text_patterns(R, figures) -> None:
    if "F4" not in figures:
        return
    steps = sorted(next(r["value"] for r in R if r["id"] == "F4.steps_sorted"))
    for r in R:
        if r["id"] in F4_J:
            j, tg, sh = F4_J[r["id"]]
            r["jprinted"], r["jtargets"] = j, tg
            if sh is not None:
                r["sprinted"], r["stargets"] = sh, tg
        elif r["id"].startswith("F4.step_"):
            i = int(r["id"].split("_")[1])
            x = float(r["value"])
            k = min(range(len(steps)), key=lambda m: abs(steps[m] - x))          # the rank of this value among the six, the captions list them in ascending order
            skip = _F4_SKIP * k
            r["jprinted"], r["jtargets"] = (r"runs have errors " + skip + r"(\d+\.\d)", 1), ("F4a",)
            r["sprinted"], r["stargets"] = (r"predicted time; errors " + skip + r"(\d+\.\d)", 1), ("F4a",)          # 13t-9: the short caption defines testable before the errors (same numbers)


# ---------------------------------------------------------------------------------------------------- short journal captions (13t-1e, DL-582 U3 d)
# Patterns of the SHORT caption (the one for the manuscript): every quantity found in a short caption is searched with a pattern of its own wording; the independent value must reproduce the printed
# token to its digits. Existing rows get their short pattern here; rows that exist only for the short caption are added in short_rows. Short rows are counted and reported separately.
SHORT_OVERRIDE = {
    "FS1.k4_rel_freq": (r"differ from the linearised ones by (\d+\.\d+e-\d+) and", 1),
    "FS1.k4_rel_decay": (r"differ from the linearised ones by \d+\.\d+e-\d+ and (\d+\.\d+e-\d+)", 1),
    "F1.ref_fpk": (r"power spectrum peaks at (\d+\.\d) Hz", 1),
    "F1.ref_onset": (r"and (\d+\.\d+) s for the mean field", 1),
    "F1.onset120_text": (r"first flags the gamma rise\) is (\d+\.\d) s for the network", 1),
    "F3.rb9b_spectral": (r"spectral peak \(the peak of the power spectrum of the simulated signal\) is (\d+\.\d) Hz", 1),
    "F3.rb9b_cycle": (r"where the resting state starts to oscillate\) is (\d+\.\d+) Hz", 1),
    "F3.rb9b_diff": (r"they differ by (\d+\.\d+) Hz", 1),
    "F3.rb9b_bound": (r"must differ by at most (\d+\.\d) Hz", 1),
    "F5.cells_disagree": (r"the network disagrees with it at (\d+) of the 4 cells tested", 1),
    # 13t-2 (DL-616 B4): the short captions of F2 and F6 (same numbers, the wording of the short caption)
    "F2.hopf_eta": (r"Hopf point, eta_bar (\d+\.\d+), in a supercritical", 1),
    "F2.cycle_eta_max": (r"is stable to eta_bar (\d+)", 1),
    "F2.updown_max_rel": (r"largest difference (\d+\.\d+e-\d+) relative", 1),
    "F2.net_rel_above_max": (r"(?:differs from the mean field's by|differing by) \+(\d+\.\d) to", 1),       # 13t-4 (DL-636 E1): the short caption now says 'differing by +13.2 to -2.5 percent'; the same number
    "F2.net_rel_above_min": (r"to (-\d+\.\d) percent above", 1),
    "F2.net_floor_min": (r"v amplitude (0\.\d+) to", 1),
    "F2.net_floor_max": (r"v amplitude 0\.\d+ to (0\.\d+)\)", 1),
    "F6.nonsurge_total": (r"Number of the (\d+) non-surge map cells", 1),
    "F6.s6_prereg": (r"(?:including all|the) (\d+) pre-registered runs", 1),       # DL-628 C4 (e): the short caption now says 'the 20 pre-registered runs and 4 P2 comparator runs'; the number is the same
    "F6.nc1_net_class": (r"is in class (S\+)", 1),
}
SHORT_S1 = r"noisy mean field agrees with the noise-free map in (\d+) of (\d+) cells \((\d+\.\d) percent; (\d+) cells, 90 percent, were needed\)"
# DL-593 V6, V7: the F1 short caption states the RB1 counts once ('0 of 3 seeds agree (0 of 3 seeds at ramp durations of 10 s and 120 s), and 1 of 4 map cells ... agree'); the F5 short caption states the cells count
SHORT_NET = r"(\d+) of (\d+) seeds agree at ramp durations of 10 s and 120 s(?: \(the 10 s ramp is not drawn here\))?, and (\d+) of (\d+) map cells"       # DL-628 C5: the parenthesis was added; the numbers are those of before


def short_rows(c: Ctx, R: Rows, figures) -> None:
    """Rows of the short captions (DL-582 U3 d; patterns rewritten for the wording of DL-593 V5 to V7, the same numbers, nothing loosened): the short pattern of the rows that exist, and the rows that only
    the short caption holds (the RB1 counts, the per-N counts of the no-ramp controls in a surge class and in S-sus). Values come from the stored files (own readers). The rows of the RB2 class-kept
    count and of the RB6 solver difference are no longer in a short caption (DL-593 V7: only failed checks whose result is drawn are named there); the full-caption rows stay."""
    a11_sh = "stored A11 table (original evaluator output)"
    src = "A11/a11_robustness.csv"
    q10, q120, qc = (_nums(_a11(c, "RB1", ck)["value"]) for ck in ("headline_10s", "headline_120s", "cells_30s"))
    if "F1" in figures:
        for nm, q, k in (("rb1_10s_n", q10[0], 1), ("rb1_120s_n", q120[0], 1), ("rb1_seeds_den", q120[1], 2), ("rb1_cells_n_short", qc[0], 3), ("rb1_cells_den_short", qc[1], 4)):
            R.add("F1", nm, f"RB1 count in the short caption ({nm})", q, f"{src}: RB1 headline_10s, headline_120s, cells_30s value", shared=a11_sh, sprinted=(SHORT_NET, k), stargets=("F1",))
    sig = c.json("S8/S8_head/S8_head_0003_7dfd3c05b40c.json")["solver"]["noise"]["sigma"]
    for fig, targets in (("F1", ("F1",)), ("F5", ("F5", "F5c"))):
        if fig in figures:
            R.add(fig, "noise_sigma", "noise level sigma (stored record config)", sig, "S8/S8_head/S8_head_0003_7dfd3c05b40c.json: solver.noise.sigma", shared="stored record config",
                  jprinted=(r"noise level sigma = (0\.\d+) \(checked", 1), jtargets=targets)
    if "F3" in figures:
        a4 = c.npz("A4/a4_hopf_curves.npz")
        R.add("F3", "a4_points_d", "points of the Hopf curve in (eta_bar, Delta)", len(a4["curve_Delta"]), "A4/a4_hopf_curves.npz: curve_Delta",
              jprinted=(r"between its (\d+) stored points, next to", 1))
        R.add("F3", "a4_points_c_in_d", "points of the Hopf curve in (eta_bar, tau_d) as stated beside the (d) curve", len(a4["curve_tau_d_ms"]), "A4/a4_hopf_curves.npz: curve_tau_d_ms",
              jprinted=(r"next to the (\d+) stored points of the curve in \(c\)", 1))
        # V6: the F3 short caption says how many slices have a 25 Hz bar ('7, 6 and 3 of 9 slices'); counted from the stored frequency map by the own reader (slices with a stored 25 Hz crossing count > 0)
        fm = c.npz("A6/a6_freq_map.npz")
        for i, D in enumerate(("0.05", "0.1", "0.3")):
            n = int(np.sum(np.asarray(fm[f"eta_tau_D{D}_c25_count"]) > 0))
            R.add("F3", f"c25_slices_D{D}", f"slices with a 25 Hz crossing at Delta {D}", n, "A6/a6_freq_map.npz: eta_tau_D*_c25_count (> 0)", shared="stored frequency map",
                  sprinted=(r"\((\d+), (\d+) and (\d+) of \d+ slices have one", i + 1), stargets=("F3",))
    if "F5" in figures:
        tsv = c.csv("ms10/10g/record_classes.tsv", "\t")
        order = ("S+", "S-rel", "S-abs", "S-sus", "NS")
        ns = (1000, 3000, 10000, 30000)
        by = {N: [r["class"] for r in tsv if r["list"] == "C2_S9" and int(r["N"]) == N] for N in ns}
        ramp = {N: [r["class"] for r in tsv if r["list"] == "S9" and int(r["N"]) == N] for N in ns}
        with_surge = [N for N in ns if sum(1 for x in by[N] if x in SURGE) > 0]
        sh = "stored class column"
        for k, N in enumerate(with_surge, start=1):
            n = sum(1 for x in by[N] if x in SURGE)
            skip = r"\d+(?:, | and )" * (k - 1)
            R.add("F5", f"ctrl_surge_N{N}", f"no-ramp controls in a surge class at N = {N}", n, "ms10/10g/record_classes.tsv: list C2_S9, N, class", shared=sh,
                  jprinted=(r"reach surge classes \(S\+, S-rel or S-abs\) at N = [^(]*\(" + skip + r"(\d+)", 1), jtargets=("F5c",))
        for i, N in enumerate(ns):                     # the F5c short caption: 'Controls in a surge class: 0, 2, 1 and 1 of 3; controls in S-sus: 0, 0, 2 and 2 of 3'
            skip = r"\d+(?:, | and )" * i
            R.add("F5", f"ctrl_surge_short_N{N}", f"no-ramp controls in a surge class at N = {N} (short caption list)", sum(1 for x in by[N] if x in SURGE), "ms10/10g/record_classes.tsv: list C2_S9, N, class", shared=sh,
                  sprinted=(r"Controls in a surge class: " + skip + r"(\d+)", 1), stargets=("F5c",))
            R.add("F5", f"ctrl_sus_short_N{N}", f"no-ramp controls in S-sus at N = {N} (short caption list)", sum(1 for x in by[N] if x == "S-sus"), "ms10/10g/record_classes.tsv: list C2_S9, N, class", shared=sh,
                  sprinted=(r"controls in S-sus: " + skip + r"(\d+)", 1), stargets=("F5c",))
        zero = [N for N in ns if sum(1 for x in by[N] if x in SURGE) == 0]
        for N in zero[:1]:
            lab = {1000: "1000", 3000: "3000", 10000: "10,000", 30000: "30,000"}[N]
            R.add("F5", f"ctrl_zero_N{N}", f"no-ramp controls that are NS at N = {N}", sum(1 for x in by[N] if x == "NS"), "ms10/10g/record_classes.tsv: list C2_S9, N, class", shared=sh,
                  jprinted=(rf"at N = {lab} the (\d+) controls are NS", 1), jtargets=("F5c",))
            names = " or ".join(x for x in order if x in ramp[N])
            R.add("F5", f"ramp_zero_N{N}", f"classes of the ramp seeds at N = {N}", names, "ms10/10g/record_classes.tsv: list S9, N, class", shared=sh,
                  jprinted=(r"the ramp seeds are ([A-Za-z+-]+ or [A-Za-z+-]+)", 1), jtargets=("F5c",))
        for k, nm in enumerate(("s1_agree", "s1_sub_n", "s1_pct", "s1_needed"), start=1):
            for r in R:
                if r["id"] == f"F5.{nm}":
                    r["sprinted"], r["stargets"] = (SHORT_S1, k), ("F5",)
    if "F6" in figures:                                  # 13t-2: the noisy first negative control has S-rel in 6 of 130 runs (stored class counts of the mode-N rows)
        mn = [r for r in c.csv("A10/a10_controls.csv") if r["control"] == "NC1" and r["row_type"] == "mode_N_summary_per_window"]
        srel = sum(json.loads(r["class_counts"]).get("S-rel", 0) for r in mn)
        tot = sum(int(float(r["n_seeds"])) for r in mn)
        R.add("F6", "srel_runs", "runs of the noisy first negative control in S-rel (mode-N rows)", srel, "A10/a10_controls.csv: NC1 mode_N_summary_per_window class_counts", shared="stored class counts",
              jprinted=(r"S-rel in (\d+) of \d+ runs", 1), jtargets=("F6",), sprinted=(r"S-rel in (\d+) of \d+ runs", 1), stargets=("F6",))
        R.add("F6", "srel_total", "runs of the noisy first negative control (mode-N rows)", tot, "A10/a10_controls.csv: NC1 mode_N_summary_per_window n_seeds", shared="stored class counts",
              jprinted=(r"S-rel in \d+ of (\d+) runs", 1), jtargets=("F6",), sprinted=(r"S-rel in \d+ of (\d+) runs", 1), stargets=("F6",))
    for r in R:                                         # 13t-4 (DL-637): the FS1 short caption states the take-home numbers in the words of the draft constant, so the draft pattern finds them (same numbers, nothing loosened)
        if r["figure"] == "FS1" and "FS1" in figures and r["printed"] is not None and r["sprinted"] is None:
            r["sprinted"], r["stargets"] = r["printed"], ("FS1",)
    for r in R:
        if r["id"] in SHORT_OVERRIDE and r["figure"] in figures:
            r["sprinted"] = SHORT_OVERRIDE[r["id"]]
            r["stargets"] = (r["figure"],)


def compute(root=None, figures=None, series_res=None) -> list:
    c = Ctx(root, series_res)
    R = Rows()
    figs = tuple(figures or FIGURES)
    for fid in figs:
        if fid in FUNCS:
            FUNCS[fid](c, R)
    journal_rows(c, R, figs)
    short_rows(c, R, figs)
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
