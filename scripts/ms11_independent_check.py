"""MS11 11g: independent recomputation of the 18 MS11 rows of results/A11/a11_robustness.csv from the stored records (no simulation, no diagnostic).

  .venv/Scripts/python.exe scripts/ms11_independent_check.py [--workers 6] [--out results/A11/independent]

Written from docs/ms11_eval_rules.md and the plan text; the analysis code is src/mprsurge/analysis/ms11_independent.py. It does not import run_A11.py, ms11_eval.py or
ms11_hooks.py. It reads the A11 OUTPUT files (csv and json) only to compare. Agreement = identical status words and identical counts; every float is listed with its
difference and none is judged. On any disagreement or error the script reports and exits 2; it patches nothing.
"""
import argparse
import ast
import csv
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from mprsurge import config as C
from mprsurge.analysis import ms11_independent as I
from mprsurge.analysis import a8_sensitivity as A8
from mprsurge.analysis import surge_metrics as M

ROOT = C.repo_root()
R = ROOT / "results"
MS11_COMMIT = "d29268f73943c75383b1be942d57d0f6afe01b81"
SIGMAS = (0.5, 1.0, 2.0)
TS = (10.0, 30.0, 120.0, 300.0)
T_OTHER = (10.0, 316.22776601683796)

NOTES = {
    "RB2": "classes: frozen classifier (shared) on the raw v read by my own reader; kept counts, thresholds, status: own code",
    "RB5": "classes: frozen classifier (shared); label equality and onset/delay shifts: own code from the stored onset and the stored eta series",
    "RB6rtol": "classes: frozen classifier (shared); onset and delay differences: own subtraction",
    "RB6floor": "classifier-onset reading: frozen classifier (shared) + own delay (stored eta series) and median; raw-crossing reading: not defined for the mode N floor runs (DL-402), nothing computed, only the A11 word compared",
    "RB6net": "reading (i): frozen classifier episode f_pk (shared); reading (ii): method taken from original behaviour (DL-401), arithmetic independent (own spectrogram call on the raw v); bound, pair and verdict logic: own",
    "RB9a": "NOT independent: re-reads results/A11/rb9a_unit_level.json written by rb9a_unit.py; only the max and the inclusive comparison are mine",
    "RB9b": "cycle frequency: own zero-crossing code from the raw v (independent); episode window and spectral f_pk: frozen classifier (shared)",
    "RB9c": "variant classes: frozen A8 variant classifier (shared) applied by my reader to the raw map-1 v; baseline from the stored map1_classes.csv; counting and fractions: own",
    "RB9d": "classes and f_pk, onset, eta at onset: frozen classifier (shared) + own eta read from the stored series; ratios own",
    "RB10": "variant classes: frozen A8 variant classifier (shared) on the raw map-1 and headline v; counting, fractions and verdict: own",
    "S13": "as RB10 (the window line is the window variants of the RB10 computation)",
}


class Cmp:
    """Collects (row, name, mine, theirs, kind) comparisons. 'count' kinds (ints, strings, status words) must be identical; 'float' kinds are listed with their difference."""
    def __init__(self):
        self.items = []

    def count(self, row, name, mine, theirs):
        self.items.append({"row": row, "name": name, "mine": mine, "a11": theirs, "kind": "count",
                           "ok": mine == theirs or (isinstance(mine, float) and isinstance(theirs, float) and math.isnan(mine) and math.isnan(theirs))})

    def real(self, row, name, mine, theirs):
        m, t = (float("nan") if x is None else float(x) for x in (mine, theirs))
        both_nan = math.isnan(m) and math.isnan(t)
        self.items.append({"row": row, "name": name, "mine": m, "a11": t, "kind": "float", "ok": True, "diff": 0.0 if both_nan else (m - t)})


def pool_map(fn, args, workers):
    with ProcessPoolExecutor(workers) as ex:
        return list(ex.map(fn, *zip(*args), chunksize=4))


def by(recs, **kw):
    out = [r for r in recs if all(r.get(k) == v for k, v in kw.items())]
    return sorted(out, key=lambda r: r["seed"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ms11_independent_check")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default="results/A11/independent")
    a = ap.parse_args(argv)
    th = I.frozen_thresholds()                                 # criteria gate first
    thr, a_ref = th["threshold_abs"], th["a_ref"]
    print(f"criteria gate ok: tag commit {th['commit']}, sha256 {th['sha256']}, threshold {thr}, a_ref {a_ref}", flush=True)
    a11 = {(r["rb_id"], r["check_id"]): r for r in csv.DictReader(open(R / "A11/a11_robustness.csv", newline="", encoding="utf-8"))}
    ev = json.loads((R / "A11/a11_evaluators.json").read_text(encoding="utf-8"))["evaluators"]
    cmp, rows = Cmp(), []

    def row(rb, check, status, note, extra=None):
        rows.append({"rb_id": rb, "check_id": check, "independent_status": status, "a11_status": a11[(rb, check)]["pass_or_fail"], "independence": note})

    # ---- gather and classify all MS11 records (frozen classifier on the raw v) ----
    def paths(d, commit=MS11_COMMIT):
        out = []
        for p in I.json_files(R / d):
            if json.loads(p.read_text(encoding="utf-8"))["git"]["commit"] == commit:
                out.append(str(p))
        return out
    P = {"s11": paths("S11/S11"), "ctrl": paths("S11/S11_ctrl"), "floor": paths("S13/ms11/S13_floor"), "d0": paths("S13/ms11/S13_delta0"),
         "rt": paths("S13/ms11/S13_rtol"), "net": paths("S13/ms11/S13_net"), "rb9d": paths("RB9D/RB9D")}
    expect = {"s11": 120, "ctrl": 30, "floor": 60, "d0": 4, "rt": 4, "net": 18, "rb9d": 2}
    for k, n in expect.items():
        if len(P[k]) != n:
            raise SystemExit(f"{k}: expected {n} records of commit {MS11_COMMIT[:7]}, found {len(P[k])}")
    p5 = [str(p) for p in I.json_files(R / "S5/ramp/p5_linear")]
    grid_all = {}
    for p in I.json_files(R / "S5/ramp/p2_linear"):
        c = json.loads(p.read_text(encoding="utf-8"))["config"]
        if c["solver"].get("delta0") == 1e-6 and c["solver"].get("rtol") == 1e-10 and any(math.isclose(float(c["path"]["T_ramp_s"]), t) for t in T_OTHER):
            grid_all.setdefault(round(float(c["path"]["T_ramp_s"]), 4), []).append(str(p))
    if sorted(len(v) for v in grid_all.values()) != [1, 1]:
        raise SystemExit(f"S5 grid members for T_ramp 10 and 316.2278: {grid_all}")
    grid_paths = [v[0] for v in grid_all.values()]
    hl = next(csv.DictReader(open(R / "ms9/9d/s5_headline_classes.csv", newline="", encoding="utf-8")))
    hl_path = str(R / "S5/ramp/S5ramp" / (hl["run"] + ".json"))
    jobs = [p for k in ("s11", "ctrl", "d0", "rt", "net", "rb9d", "floor") for p in P[k]] + p5 + grid_paths + [hl_path]
    res = pool_map(I.analyse_record, [(p, thr) for p in jobs], a.workers)
    allr = dict(zip(jobs, res))
    G = lambda k: [allr[p] for p in P[k]]            # noqa: E731
    for r in res:
        if r["status"] != "ok":
            print("record not ok:", r["name"], r["status"])
    print(f"classified {len(res)} records", flush=True)

    # ---- RB2: kept counts (rows 27 to 31) ----
    s11 = G("s11")
    KEPT = {"primary": I.SURGE_N, "s_plus_only": ("S+",), "s_plus_or_abs": ("S+", "S-abs")}
    g = {(e["sigma_factor"], e["T_ramp_s"]): e for e in ev["rb2"]["gate"]}
    for sf, name in ((0.5, "headline_class_kept_0.5_sigma"), (1.0, "headline_class_kept_1.0_sigma")):
        recs = by(s11, sigma_factor=sf, T=120.0)
        kept = I.count_kept([r["cls"] for r in recs], KEPT["primary"])
        failed = sum(1 for r in recs if r["cls"] == "failed")
        st = I.rb2_status(kept, th["rb2_k"])
        e = g[(sf, 120.0)]
        row("RB2", name, st, NOTES["RB2"])
        cmp.count(name, "kept", kept, e["kept"]); cmp.count(name, "failed", failed, e["failed"]); cmp.count(name, "n_records", len(recs), e["n_records"])
        cmp.count(name, "classes", I.class_counts([r["cls"] for r in recs]), e["classes"]); cmp.count(name, "status", st, e["status"])
    beside = {(e["sigma_factor"], e["T_ramp_s"]): e for e in ev["rb2"]["beside"]}
    for name, keymap in (("two_sigma_reported", {"kept_primary": "primary"}), ("stricter_readings", {"kept_S_plus_only": "s_plus_only", "kept_S_plus_or_S_abs": "s_plus_or_abs"})):
        for sf in SIGMAS:
            for T in TS:
                recs = by(s11, sigma_factor=sf, T=T)
                cls = [r["cls"] for r in recs]
                e = beside.get((sf, T)) or g.get((sf, T))
                if e is None:
                    cmp.count(name, f"s{sf}_T{T}_present_in_a11", False, True)
                    continue
                for k, kind in keymap.items():
                    if k in e:
                        cmp.count(name, f"s{sf}_T{T}_{k}", I.count_kept(cls, KEPT[kind]), e[k])
                if name == "two_sigma_reported":
                    cmp.count(name, f"s{sf}_T{T}_classes", I.class_counts(cls), e["classes"]); cmp.count(name, f"s{sf}_T{T}_failed", sum(c == "failed" for c in cls), e["failed"])
        row("RB2", name, "REPORTED", NOTES["RB2"])
    for e in ev["rb2"]["controls"]:
        recs = by(G("ctrl"), sigma_factor=e["sigma_factor"])
        cls = [r["cls"] for r in recs]
        cmp.count("dl251_controls", f"s{e['sigma_factor']}_kept", I.count_kept(cls), e["kept_primary"]); cmp.count("dl251_controls", f"s{e['sigma_factor']}_classes", I.class_counts(cls), e["classes"])
    row("RB2", "dl251_controls", "REPORTED", NOTES["RB2"])

    # ---- RB5 delta0, P5, RB6 rtol (rows 32 to 34) ----
    ref = {round(allr[p]["T"], 4): allr[p] for p in grid_paths}
    d0rows = {(r["T_ramp_s"], r["delta0"]): r for r in ev["rb5_delta0"]["rows"]}
    unchanged = 0
    for r in sorted(G("d0"), key=lambda x: (x["T"], x["delta0"])):
        rf = ref[round(r["T"], 4)]
        unchanged += int(r["cls"] == rf["cls"])
        e = d0rows[(r["T"], r["delta0"])]
        k = f"T{r['T']:.4f}_d0{r['delta0']:g}"
        cmp.count("delta0_T10_T316", k + "_class", r["cls"], e["class"]); cmp.count("delta0_T10_T316", k + "_ref_class", rf["cls"], e["ref_class"])
        cmp.real("delta0_T10_T316", k + "_onset_shift_s", r["onset"] - rf["onset"], e["onset_shift_s"]); cmp.real("delta0_T10_T316", k + "_delay_shift", r["delay"] - rf["delay"], e["delay_shift"])
    st = "PASS" if unchanged == len(G("d0")) == 4 else "FAIL"
    row("RB5", "delta0_T10_T316", st, NOTES["RB5"]); cmp.count("delta0_T10_T316", "n_unchanged", unchanged, sum(1 for e in ev["rb5_delta0"]["rows"] if e["status"] == "PASS"))
    cmp.count("delta0_T10_T316", "status", st, ev["rb5_delta0"]["status"])
    p5c = {allr[p]["T"]: allr[p]["cls"] for p in p5}
    cmp.count("updown", "n_p5", len(p5c), len(ev["rb5_updown"]["p5_classes"]))
    for T, c in ev["rb5_updown"]["p5_classes"].items():
        cmp.count("updown", f"T{float(T):.4f}", p5c.get(float(T)), c)
    row("RB5", "updown", "REPORTED", NOTES["RB5"])
    rtrows = {(r["T_ramp_s"], r["rtol"]): r for r in ev["rb6_rtol"]["rows"]}
    for r in sorted(G("rt"), key=lambda x: (x["T"], x["rtol"])):
        rf = ref[round(r["T"], 4)]
        e = rtrows[(r["T"], r["rtol"])]
        k = f"T{r['T']:.4f}_rtol{r['rtol']:g}"
        cmp.count("rtol_T10_T316", k + "_class", r["cls"], e["class"]); cmp.count("rtol_T10_T316", k + "_ref_class", rf["cls"], e["ref_class"])
        cmp.real("rtol_T10_T316", k + "_onset_diff_s", r["onset"] - rf["onset"], e["onset_diff_s"]); cmp.real("rtol_T10_T316", k + "_delay_diff", r["delay"] - rf["delay"], e["delay_diff"])
    row("RB6", "rtol_T10_T316", "REPORTED", NOTES["RB6rtol"])

    # ---- RB6 floor medians (row 35) ----
    fl = G("floor")
    levels = sorted({r["sigma"] for r in fl})
    if len(levels) != 3:
        raise SystemExit(f"floor levels: {levels}")
    fr = {(e["onset_reading"], e["T_ramp_s"]): e for e in ev["rb6_floor"]["rows"]}
    for T in T_OTHER:
        meds, nos = [], []
        for lv in levels:
            vals = [r["delay"] for r in fl if r["sigma"] == lv and math.isclose(r["T"], T)]
            meds.append(I.median_of(vals)); nos.append(sum(not math.isfinite(x) for x in vals))
        e = fr[("classifier_onset", T)]
        k = f"classifier_onset_T{T:.4f}"
        for i in range(3):
            cmp.real("floor_other_T_ramp", f"{k}_median_level{i}", meds[i], e["median_delay_by_level"][str(i)])
            cmp.count("floor_other_T_ramp", f"{k}_seeds_without_onset_level{i}", nos[i], e["seeds_without_onset_by_level"][str(i)])
        cmp.count("floor_other_T_ramp", f"{k}_direction", I.direction_word(meds).split(" ")[0], e["direction"].split(" ")[0])
        # the raw-crossing onset is defined only for mode D records (DL-402, DL-403): the floor runs are mode N, so no median exists; nothing is computed, only the A11 word is compared
        cmp.count("floor_other_T_ramp", f"raw_first_crossing_T{T:.4f}_direction", "undefined", fr[("raw_first_crossing", T)]["direction"].split(" ")[0])
        assert all(r["mode"] == "N" for r in fl)
    row("RB6", "floor_other_T_ramp", "REPORTED", NOTES["RB6floor"])

    # ---- RB6 network (rows 36 and 37) ----
    net = {}
    for p in P["net"]:
        r = allr[p]
        rec = I.load_record(p)
        net[(r["V_peak"], r["dt_tau"], r["seed"])] = {**r, "v": rec["v"], "fs": rec["fs"]}
    seeds = sorted({k[2] for k in net})
    def fk(v, dt, s):
        return net[(v, dt, s)]["fpk"]
    def psd(v, dt, s):
        base = net[(v, 1e-3, s)]
        if not math.isfinite(base["onset"]):
            return math.nan
        r = net[(v, dt, s)]
        return I.overlap_window_psd_argmax(r["v"], r["fs"], base["onset"], base["end"], r["T"])
    pr = ev["rb6_network"]["per_reading"]
    verdicts = []
    for reading, getter, jk in (("classifier_episode_fpk", fk, "classifier_episode_fpk"), ("psd_argmax", psd, "psd_argmax")):
        pairs = []
        for s in seeds:
            p = I.fpk_pair(getter(100.0, 1e-3, s), getter(100.0, 5e-4, s), th["net_fpk"])
            pairs.append(p)
            e = next(x for x in pr[jk]["rows"] if x["seed"] == s)
            cmp.real("network_fpk", f"{reading}_seed{s}_f1", getter(100.0, 1e-3, s), e["f1_hz"]); cmp.real("network_fpk", f"{reading}_seed{s}_f2", getter(100.0, 5e-4, s), e["f2_hz"])
            cmp.real("network_fpk", f"{reading}_seed{s}_rel", p["rel"], e["rel"]); cmp.count("network_fpk", f"{reading}_seed{s}_status", p["status"], e["status"])
        v = I.reading_verdict(pairs)
        verdicts.append(v)
        cmp.count("network_fpk", f"{reading}_n_pass", sum(p["status"] == "PASS" for p in pairs), pr[jk]["n_pass"])
        cmp.count("network_fpk", f"{reading}_n_fail", sum(p["status"] == "FAIL" for p in pairs), pr[jk]["n_fail"])
        cmp.count("network_fpk", f"{reading}_verdict", v, pr[jk]["status"])
    nv = I.network_verdict(verdicts)
    cmp.count("network_fpk", "row_status", nv, ev["rb6_network"]["status"])
    for e in ev["rb6_network"]["ladder_info"]:
        f1, f2 = fk(100.0, e["dt_from"], e["seed"]), fk(100.0, e["dt_to"], e["seed"])
        cmp.real("network_fpk", f"ladder_seed{e['seed']}_{e['dt_from']:g}_{e['dt_to']:g}_f1", f1, e["f1_hz"]); cmp.real("network_fpk", f"ladder_seed{e['seed']}_{e['dt_from']:g}_{e['dt_to']:g}_rel", I.fpk_pair(f1, f2, th["net_fpk"])["rel"], e["rel"])
    row("RB6", "network_fpk_halving_dt", nv, NOTES["RB6net"])
    for e in ev["rb6_network"]["vp_info"]:
        f1, f2 = fk(100.0, e["dt"], e["seed"]), fk(200.0, e["dt"], e["seed"])
        cmp.real("network_vp", f"seed{e['seed']}_dt{e['dt']:g}_f1", f1, e["f1_hz"]); cmp.real("network_vp", f"seed{e['seed']}_dt{e['dt']:g}_f2", f2, e["f2_hz"])
    cmp.count("network_vp", "n_pairs", len(ev["rb6_network"]["vp_info"]), len(seeds) * 2)
    row("RB6", "network_vp_pm100_vs_pm200", "REPORTED", NOTES["RB6net"])
    for k, c in ev["rb6_network"]["classes_information"].items():
        key = ast.literal_eval(k) if isinstance(k, str) else k          # the A11 json writes the tuple keys as strings
        cmp.count("network_fpk", f"class_{k}", net[key]["cls"], c)

    # ---- RB9(a) (row 38) ----
    u = json.loads((R / "A11/rb9a_unit_level.json").read_text(encoding="utf-8"))
    mx = max(d["max"] for d in u["per_tau"].values())
    st = "PASS" if I.le(mx, th["rb9a"]) else "FAIL"
    row("RB9", "a_dimensional_vs_nondimensional", st, NOTES["RB9a"]); cmp.real("rb9a", "max_rel_diff", mx, ev["rb9a"]["value"]); cmp.count("rb9a", "status", st, ev["rb9a"]["status"])

    # ---- RB9(b) headline (row 39) ----
    h = allr[hl_path]
    hrec = I.load_record(hl_path)
    W = M.window_for_ramp(h["T"])[0]
    cyc, ncross = I.cycle_frequency(hrec["v"], hrec["fs"], h["onset"], h["end"])
    diff = abs(h["fpk"] - cyc)
    st = "PASS" if I.le(diff, 1.0 / W) else "FAIL"
    e = ev["rb9b"]["headline"]
    row("RB9", "b_spectral_vs_cycle_headline", st, NOTES["RB9b"])
    cmp.real("rb9b_headline", "f_spectral_hz", h["fpk"], e["f_spectral_hz"]); cmp.real("rb9b_headline", "f_cycle_hz", cyc, e["f_cycle_hz"]); cmp.real("rb9b_headline", "diff_hz", diff, e["diff_hz"])
    cmp.real("rb9b_headline", "bound_hz", 1.0 / W, e["bound_hz"]); cmp.count("rb9b_headline", "status", st, e["status"])
    cmp.real("rb9b_headline", "stored_csv_f_pk_vs_classifier", float(hl["f_pk_hz"]), h["fpk"]); cmp.real("rb9b_headline", "stored_csv_onset_vs_classifier", float(hl["onset_s"]), h["onset"])

    # ---- map cells (rows 40, 41, 43, 44) ----
    def cells(folder, base_csv):
        base = {r["run"]: r["class"] for r in csv.DictReader(open(base_csv, newline="", encoding="utf-8"))}
        ps = [p for p in I.json_files(folder) if p.stem in base]
        return ps, base
    VAR = tuple(v for v in ("band_30_120", "factors_1.5", "factors_4", "amin_0.05", "amin_0.2", "window_x0.5", "window_x2", "cycles_5", "cycles_20"))
    m1p, m1b = cells(R / "S7/S7_map1", R / "ms9/9e/map1_classes.csv")
    m2p, m2b = cells(R / "S7/S7_map2", R / "ms9/9f/map2_classes.csv")
    print(f"map 1: {len(m1p)} cells, map 2: {len(m2p)} cells; classifying (this is the long step)", flush=True)
    m1 = pool_map(I.analyse_cell, [(str(p), thr, a_ref, VAR) for p in m1p], a.workers)
    m2 = pool_map(I.analyse_cell, [(str(p), thr, a_ref, ()) for p in m2p], a.workers)
    cmp.count("cells", "n_map1", len(m1), 900); cmp.count("cells", "n_map2", len(m2), 325)
    cmp.count("cells", "map1_my_baseline_vs_stored_disagreements", sum(c["cls"] != m1b[c["run"]] for c in m1), 0)
    cmp.count("cells", "map2_my_baseline_vs_stored_disagreements", sum(c["cls"] != m2b[c["run"]] for c in m2), 0)
    for name, cs in (("map1", m1), ("map2", m2)):
        epi = [c for c in cs if math.isfinite(c["onset"])]
        within = sum(1 for c in epi if math.isfinite(c["cyc"]) and I.le(abs(c["fpk"] - c["cyc"]), 1.0 / c["W"]))
        e = ev["rb9b"]["cells_reported"][name]
        cmp.count("rb9b_cells", f"{name}_n_with_episode", len(epi), e["n"]); cmp.count("rb9b_cells", f"{name}_within", within, e["within"])
        cmp.real("rb9b_cells", f"{name}_fraction", within / len(epi) if epi else math.nan, e["fraction"])
    row("RB9", "b_map_cells_fraction", "REPORTED", NOTES["RB9b"])
    base1 = [m1b[c["run"]] for c in m1]
    fr = {v: I.changed_fraction(base1, [c["variants"][v] for c in m1]) for v in VAR}
    f9 = fr["band_30_120"]
    st = I.map_fraction_status(f9, th["rb9c"])
    e = ev["rb9c"]
    row("RB9", "c_band_30_120_map1", st, NOTES["RB9c"])
    cmp.count("rb9c", "n_changed", f9["changed"], e["n_changed"]); cmp.count("rb9c", "n_evaluated", f9["n"], e["n_evaluated"]); cmp.count("rb9c", "n_excluded", f9["excluded"], e["n_excluded"])
    cmp.real("rb9c", "fraction", f9["fraction"], e["fraction"]); cmp.count("rb9c", "status", st, e["status"])
    # headline under the nine variants
    head_unchanged = {}
    for v in VAR:
        head_unchanged[v] = (A8.classify(hrec["v"], hrec["mode"], hrec["t_on"], hrec["T"], a_ref, v)["cls"] == hl["class"])
    def line(vs):
        sts = {}
        for v in vs:
            f = fr[v]
            sts[v] = "PASS" if head_unchanged[v] and I.map_fraction_status(f, th["rb10"]) == "PASS" else "FAIL"
        return sts
    for v, s in line(VAR).items():
        e = ev["rb10"]["variants"][v]
        cmp.count("rb10", f"{v}_headline_unchanged", head_unchanged[v], e["headline"] == "PASS"); cmp.count("rb10", f"{v}_status", s, e["status"])
        cmp.real("rb10", f"{v}_fraction", fr[v]["fraction"], e["fraction"]); cmp.count("rb10", f"{v}_n_evaluated", fr[v]["n"], e["n_evaluated"]); cmp.count("rb10", f"{v}_n_excluded", fr[v]["excluded"], e["n_excluded"])
    st10 = "PASS" if all(s == "PASS" for s in line(VAR).values()) else "FAIL"
    row("RB10", "surge_definition_sensitivity_map1", st10, NOTES["RB10"]); cmp.count("rb10", "status", st10, ev["rb10"]["status"])
    stw = "PASS" if all(s == "PASS" for s in line(("window_x0.5", "window_x2")).values()) else "FAIL"
    row("S13", "window_x0.5_x2", stw, NOTES["S13"])
    for v in ("window_x0.5", "window_x2"):
        e = ev["rb10"]["window_line_of_s13"][v]
        cmp.real("window_line", f"{v}_fraction", fr[v]["fraction"], e["fraction"]); cmp.count("window_line", f"{v}_status", line((v,))[v], e["status"])

    # ---- RB9(d) (row 42) ----
    hd = ev["rb9d"]["headline_10ms"]
    cmp.count("rb9d", "headline_class", h["cls"], hd["class"]); cmp.real("rb9d", "headline_f_pk_hz", h["fpk"], hd["f_pk_hz"]); cmp.real("rb9d", "headline_onset_s", h["onset"], hd["onset_s"])
    for r in sorted(G("rb9d"), key=lambda x: x["tau_ms"]):
        e = next(x for x in ev["rb9d"]["rows"] if x["tau_ms"] == r["tau_ms"])
        k = f"tau{r['tau_ms']:g}"
        cmp.count("rb9d", k + "_class", r["cls"], e["class"]); cmp.count("rb9d", k + "_class_changed_vs_headline", r["cls"] != h["cls"], e["class_changed_vs_headline"])
        cmp.real("rb9d", k + "_f_pk_hz", r["fpk"], e["f_pk_hz"]); cmp.real("rb9d", k + "_f_pk_per_tau", r["fpk"] * r["tau_ms"] / 1000.0, e["f_pk_per_tau"]); cmp.real("rb9d", k + "_onset_s", r["onset"], e["onset_s"])
        cmp.real("rb9d", k + "_duration_s", r["end"] - r["onset"], e["duration_s"]); cmp.real("rb9d", k + "_f_pk_ratio", r["fpk"] / h["fpk"], e["f_pk_ratio_to_headline"])
    row("RB9", "d_tau_pm20", "REPORTED", NOTES["RB9d"])

    # ---- compare, write, report ----
    rowname = {("RB2", "headline_class_kept_0.5_sigma"): "headline_class_kept_0.5_sigma", ("RB2", "headline_class_kept_1.0_sigma"): "headline_class_kept_1.0_sigma",
               ("RB2", "two_sigma_reported"): "two_sigma_reported", ("RB2", "stricter_readings"): "stricter_readings", ("RB2", "dl251_controls"): "dl251_controls",
               ("RB5", "delta0_T10_T316"): "delta0_T10_T316", ("RB5", "updown"): "updown", ("RB6", "rtol_T10_T316"): "rtol_T10_T316", ("RB6", "floor_other_T_ramp"): "floor_other_T_ramp",
               ("RB6", "network_fpk_halving_dt"): "network_fpk", ("RB6", "network_vp_pm100_vs_pm200"): "network_vp", ("RB9", "a_dimensional_vs_nondimensional"): "rb9a",
               ("RB9", "b_spectral_vs_cycle_headline"): "rb9b_headline", ("RB9", "b_map_cells_fraction"): "rb9b_cells", ("RB9", "c_band_30_120_map1"): "rb9c", ("RB9", "d_tau_pm20"): "rb9d",
               ("RB10", "surge_definition_sensitivity_map1"): "rb10", ("S13", "window_x0.5_x2"): "window_line"}
    n_bad = 0
    out = Path(a.out)
    out = out if out.is_absolute() else ROOT / out
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    for r in rows:
        tag = rowname[(r["rb_id"], r["check_id"])]
        its = [i for i in cmp.items if i["row"] == tag or (tag == "network_fpk" and i["row"] == "network_fpk") or (tag == "rb9b_cells" and i["row"] == "cells")]
        if tag == "rb9b_cells":
            its = [i for i in cmp.items if i["row"] in ("rb9b_cells", "cells")]
        if tag == "rb10":
            its = [i for i in cmp.items if i["row"] == "rb10"]
        counts = [i for i in its if i["kind"] == "count"]
        floats = [i for i in its if i["kind"] == "float"]
        bad = [i for i in counts if not i["ok"]]
        status_ok = r["independent_status"] == r["a11_status"]
        ok = status_ok and not bad
        n_bad += int(not ok)
        fd = [abs(i["diff"]) for i in floats if math.isfinite(i["diff"])]
        summary.append({**r, "status_match": "yes" if status_ok else "no", "n_count_items": len(counts), "n_count_mismatch": len(bad), "n_float_items": len(floats),
                        "max_abs_float_diff": max(fd) if fd else 0.0, "match": "yes" if ok else "no"})
    with open(out / "ms11_independent_rows.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(summary)
    with open(out / "ms11_independent_items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["row", "name", "kind", "independent", "a11", "diff", "ok"])
        for i in cmp.items:
            w.writerow([i["row"], i["name"], i["kind"], i["mine"], i["a11"], i.get("diff", ""), i["ok"]])
    (out / "ms11_independent_cells.json").write_text(json.dumps({"map1_variant_fractions": fr, "headline_unchanged": head_unchanged, "criteria": th,
                                                                 "map1_cyc_nan": sum(1 for c in m1 if math.isfinite(c["onset"]) and not math.isfinite(c["cyc"])),
                                                                 "map2_cyc_nan": sum(1 for c in m2 if math.isfinite(c["onset"]) and not math.isfinite(c["cyc"])),
                                                                 "headline_n_crossings": ncross}, indent=1, default=str), encoding="utf-8")
    for s in summary:
        print(f"{s['match']:3s} {s['rb_id']:5s} {s['check_id']:38s} independent {s['independent_status']:13s} A11 {s['a11_status']:13s} counts {s['n_count_items'] - s['n_count_mismatch']}/{s['n_count_items']} floats {s['n_float_items']} max|d| {s['max_abs_float_diff']:.3g}")
    for i in cmp.items:
        if i["kind"] == "count" and not i["ok"]:
            print("COUNT MISMATCH", i["row"], i["name"], "independent", i["mine"], "A11", i["a11"])
    print(f"rows matching {sum(s['match'] == 'yes' for s in summary)} of {len(summary)}; wrote {out}")
    return 0 if n_bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
