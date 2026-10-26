"""MS10 10g: independent recomputation of the MS10 numbers in docs/ms10_results.md (DL-316 to DL-323). Analysis only: nothing is integrated, no run.

A separate code path. It reads the stored run records (<name>.json with <name>.npz), the stored mean-field references and the cell files directly. It does NOT
import analysis/ms10_eval.py, analysis/ms10_runlist.py, analysis/ms9_classify.py, scripts/evaluate_ms10.py, scripts/write_ms10_results.py or any evaluator.
The only analysis code it calls is: the frozen classifier (analysis.surge_metrics: classify_mode_d, classify_mode_n, window_for_ramp, envelope, G_BAND), the
frozen criteria loader (criteria.load_frozen_criteria, via analysis.a7.frozen_inputs for the threshold), the run-path definitions (ramps.make_path, units.s_to_tau;
used for eta(t) and J(t) only) and, for J_exit,static only, the 9i static-exit function (ms9_9i.j_exit_static_path; NOT independent, flagged in the report).
Record discovery, grouping, control matching, counting, tolerances, pooling, medians and verdict logic are written anew from docs/ms10_eval_rules.md and
configs/ms10/ms10_eval.yaml. Results are compared with the cells of the tables of docs/ms10_results.md, parsed as text.

  .venv/Scripts/python.exe scripts/ms10_independent_check.py [--frozen-constants]

Pass 1 (default) uses the references as recomputed from the stored records at full precision. Pass 2 (--frozen-constants, 10g) uses the frozen pre-registered
constants instead: sigma reference 0.039522 (E-10) and the headline f_pk and onset references of configs/ms10/mf_references.yaml (stored_class: 48.05 Hz and
10.604 s at 10 s, 49.0 Hz and 58.698 s at 120 s). Reports go to results/ms10/10g/independent_report.txt (pass 1) and independent_report_pass2.txt (pass 2).

Prints and writes results/ms10/10g/independent_report.txt (one line per item: MATCH or DIFFERENCE) and the per-record class table. Differences are reported, never fixed.
"""
import collections
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import yaml

from mprsurge import config as C
from mprsurge import ramps
from mprsurge import units
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import surge_metrics as M

ROOT = C.repo_root()
MD = (ROOT / "docs/ms10_results.md").read_text(encoding="utf-8")
SURGE = ("S+", "S-rel", "S-abs")
EPS = 1e-9
REPORT = []
FROZEN = "--frozen-constants" in sys.argv


def item(name, got, logged):
    ok = "MATCH" if got == logged else "DIFFERENCE"
    REPORT.append((ok, name, got, logged))
    print(f"{ok:10s} {name}: recomputed {got!r} | logged {logged!r}", flush=True)


def fmt(x, nd=4):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "undefined"
    return f"{x:.{nd}g}" if isinstance(x, (float, np.floating)) else str(x)


def cmp_cell(name, mine, cell):
    """Compare a recomputed value with a table cell of the markdown: the text must equal the .4g text; a differing last digit at a rounding boundary is flagged."""
    s = fmt(mine)
    if s == cell:
        item(name, s, cell)
        return
    try:
        a, b = float(mine), float(cell)
        if abs(a - b) <= 6e-4 * abs(b) + 1e-12:
            REPORT.append(("MATCH(rounding-boundary)", name, s, cell))
            print(f"MATCH(rb)  {name}: recomputed {s!r} | logged {cell!r}", flush=True)
            return
    except (TypeError, ValueError):
        pass
    item(name, s, cell)


def cls_str(d):
    return ", ".join(f"{k} {v}" for k, v in sorted(d.items())) or "-"


# --- markdown parsing -----------------------------------------------------------------------------------------

def section(title_start):
    parts = re.split(r"\n(?=## )", MD)
    for p in parts:
        if p.startswith(title_start):
            return p
    raise KeyError(title_start)


def tables(text):
    """List of tables (list of rows (list of cell strings)), header and separator rows removed."""
    out, cur = [], []
    for line in text.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            cur.append(cells)
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return [[r for r in t[2:]] for t in out]


# --- stored records ----------------------------------------------------------------------------------------------

def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def fs_of(cfg):
    return 1000.0 / (cfg["network"]["rate_bin_ms"] if cfg["run"]["kind"] == "network" else cfg["solver"]["dt_out_ms"])


def classify(cfg, v, threshold):
    p = cfg["path"]
    fs = fs_of(cfg)
    if cfg["run"]["kind"] == "mf":
        return M.classify_mode_d(v, fs, p["t_on_s"], p["T_ramp_s"], threshold)
    return M.classify_mode_n(v, fs, p["t_on_s"], p["T_ramp_s"], threshold)


def read_dir(d):
    out = []
    for jp in sorted(Path(d).glob("*.json")):
        if jp.name.endswith(".dry.json") or not jp.with_suffix(".npz").exists():
            continue
        out.append(jp)
    return out


def discover():
    """{list: [path]} from the family folders; the list of a record is its folder."""
    fam = {"S8": ["S8/S8_head", "S8/S8_cells"], "C2_S8": ["S8/S8_ctrl"], "S9": ["S9/S9"], "C2_S9": ["S9/S9_ctrl"], "S10": ["S10/S10"], "C2_S10": ["S10/S10_ctrl"]}
    return {k: [p for d in v for p in read_dir(ROOT / "results" / d)] for k, v in fam.items()}


def mf_row(jp, threshold):
    rec = load_json(jp)
    cfg = rec["config"]
    with np.load(Path(jp).with_suffix(".npz")) as z:
        v = z["v"]
    res = classify(cfg, v, threshold)
    ep = res.episode
    return {"cfg": cfg, "class": res.cls, "onset_s": float(ep.onset_s) if ep is not None else float("nan"),
            "f_pk_hz": float(ep.f_pk_hz) if ep is not None else float("nan"), "name": Path(jp).stem, "T": float(cfg["path"]["T_ramp_s"]),
            "Delta": cfg["model"]["Delta"], "tau_d": cfg["model"]["tau_d_ms"]}


def net_row(jp, threshold, want_metrics):
    rec = load_json(jp)
    cfg = rec["config"]
    key = list(cfg["seeds"]["spawn_key"])
    with np.load(Path(jp).with_suffix(".npz")) as z:
        v = z["v"]
        r = z["r"] if "r" in z.files else None
        t0 = float(z["t_ms"][0]) if "t_ms" in z.files else None
    p, nw = cfg["path"], cfg["network"]
    row = {"name": Path(jp).stem, "status": rec["status"], "dirty": rec["git"]["dirty"], "commit": rec["git"]["commit"], "key": key, "seed": key[-1],
           "group": key[2], "N": nw["N"], "het": nw["het_dist"], "T": float(p["T_ramp_s"]), "Delta": cfg["model"]["Delta"], "tau_d": cfg["model"]["tau_d_ms"],
           "cfg": cfg, "first_stamp_ms": t0, "wall": rec["wall_time_s"]}
    W, step = M.window_for_ramp(row["T"])
    row["W"], row["step"], row["bin_hz"] = float(W), float(step), 1.0 / float(W)
    row["base_std"] = float(np.std(np.asarray(v, float)[0:5000], ddof=1))
    res = classify(cfg, v, threshold)
    row["class"] = res.cls
    ep = res.episode
    row["ep"] = ep
    row["onset"] = float(ep.onset_s) if ep is not None else float("nan")
    row["f_pk"] = float(ep.f_pk_hz) if ep is not None else float("nan")
    env = M.envelope(np.asarray(v, float), fs_of(cfg), M.G_BAND)
    i_on = int(round(p["t_on_s"] * fs_of(cfg)))
    hit = np.flatnonzero(env[i_on:] >= threshold)
    row["raw_onset"] = float((hit[0] + i_on) / fs_of(cfg)) if hit.size else float("nan")
    if want_metrics:
        row["metrics"], row["undef"] = metrics_row(cfg, v, r, ep)
    return row


METRICS = ["onset_s", "eta_onset", "delay_eta", "duration_ms", "duration_cycles", "duration_frac_ramp", "peak_power_abs", "peak_power_rel", "f_pk_hz",
           "J_exit_run", "J_exit_static", "exit_delay", "r_post_1s", "r_post_5s"]
_STATIC = {}


def metrics_row(cfg, v, r, ep):
    nan = float("nan")
    m = {k: nan for k in METRICS}
    why = {}
    if ep is None:
        return m, {k: "no_episode" for k in METRICS}
    p, mod = cfg["path"], cfg["model"]
    fs = fs_of(cfg)
    t = np.arange(len(v)) / fs
    path = ramps.make_path(cfg)
    tau = units.s_to_tau(t, mod["tau_ms"])
    eta = np.broadcast_to(np.asarray(path.eta(tau), float), t.shape)
    J = np.broadcast_to(np.asarray(path.J(tau), float), t.shape)
    m["onset_s"] = float(ep.onset_s)
    m["eta_onset"] = float(np.interp(ep.onset_s, t, eta))
    m["delay_eta"] = m["eta_onset"] - float(p["eta_H"])
    m["duration_ms"] = 1000.0 * float(ep.duration_s)
    m["duration_cycles"] = float(ep.cycles)
    m["duration_frac_ramp"] = float(ep.duration_s) / float(p["T_ramp_s"])
    m["peak_power_abs"], m["peak_power_rel"], m["f_pk_hz"] = float(ep.peak_p_g), float(ep.peak_rho), float(ep.f_pk_hz)
    if p["name"] != "path_hypoxia":
        for k in ("J_exit_run", "J_exit_static", "exit_delay", "r_post_1s", "r_post_5s"):
            why[k] = "not_applicable_not_P2"
    else:
        from mprsurge.analysis import ms9_9i as N9           # NOT independent: the 9i static-exit function (J_exit,static only)
        key = json.dumps([p, mod], sort_keys=True, default=str)
        if key not in _STATIC:
            _STATIC[key] = N9.j_exit_static_path(cfg, A7.frozen_inputs()[0]["grid_step"])
        js, jwhy = _STATIC[key]
        if js is None:
            why["J_exit_static"] = jwhy
        else:
            m["J_exit_static"] = float(js)
        if not ep.terminated:
            for k in ("J_exit_run", "exit_delay", "r_post_1s", "r_post_5s"):
                why[k] = "episode_unterminated_at_run_end"
        else:
            m["J_exit_run"] = float(np.interp(ep.end_s, t, J))
            if js is None:
                why["exit_delay"] = "no_J_exit_static"
            else:
                m["exit_delay"] = m["J_exit_run"] - float(js)
            for w in (1.0, 5.0):
                k = f"r_post_{int(w)}s"
                if r is not None and ep.end_s + w <= t[-1] + 1.0 / fs:
                    sel = (t >= ep.end_s) & (t < ep.end_s + w)
                    m[k] = float(np.asarray(r)[sel].mean())
                else:
                    why[k] = "window_extends_past_run_end" if r is not None else "no_r_in_record"
    return m, {k: why.get(k, "undefined") for k in METRICS if not math.isfinite(m[k])}


# --- the rules, written anew -------------------------------------------------------------------------------------------

def corr_match(ref_cls, cls, posthoc=False):
    """Table 2.1 correspondence of a mean-field class to a network class; posthoc: S-rel not counted for D-tr."""
    if ref_cls == "D-tr":
        return cls in ("S+", "S-abs") if posthoc else cls in SURGE
    if ref_cls == "D-sus":
        return cls == "S-sus"
    if ref_cls == "D-none":
        return cls == "NS"
    return False


def level(cls):
    return "surge" if cls in SURGE else cls


def ctrl_key(r):
    return (r["N"], r["T"], r["het"], round(float(r["Delta"]), 12), round(float(r["tau_d"]), 12))


def ctrl_classes(ramp_row, ctrls):
    return dict(collections.Counter(c["class"] for c in ctrls if ctrl_key(c) == ctrl_key(ramp_row)))


def med_rng(xs):
    ok = [float(x) for x in xs if x is not None and math.isfinite(float(x))]
    return (len(ok), len(xs) - len(ok), float(np.median(ok)) if ok else float("nan"), min(ok) if ok else float("nan"), max(ok) if ok else float("nan"))


def main():
    thr = A7.frozen_inputs()[0]["threshold"]
    crit, info = __import__("mprsurge.criteria", fromlist=["x"]).load_frozen_criteria()
    rb1c, rb8c = crit["robustness"]["RB1"], crit["robustness"]["RB8"]
    kk = lambda t: tuple(int(x) for x in re.search(r"(\d+)\s+of\s+(\d+)", str(t)).groups())
    seeds_k, seeds_n = kk(rb1c["classes_agree_seeds"]["value"])
    cells_k, cells_n = kk(rb1c["classes_agree_cells"]["value"])
    ftol = float(rb1c["f_pk_rel_tol"]["value"])
    rb8_seeds = int(rb8c["gaussian_uniform_give_lorentzian_class_seeds"]["value"])
    print(f"criteria sha256 {info['sha256']}; threshold {thr}; RB1 seeds {seeds_k} of {seeds_n}, cells {cells_k} of {cells_n}, f_pk tol {ftol}, RB8 seeds {rb8_seeds}")
    item("criteria sha256", info["sha256"], "c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05")

    files = discover()
    item("records per list", {k: len(v) for k, v in files.items()}, {"S8": 18, "C2_S8": 18, "S9": 40, "C2_S9": 12, "S10": 9, "C2_S10": 6})
    item("records total", sum(len(v) for v in files.values()), 103)
    rows = {k: [net_row(p, thr, k in ("S8", "S9", "S10")) for p in v] for k, v in files.items()}
    allrows = [r for v in rows.values() for r in v]
    item("all status ok", all(r["status"] == "ok" for r in allrows), True)
    item("all git dirty false", all(r["dirty"] is False for r in allrows), True)
    item("commits", sorted({r["commit"][:7] for r in allrows}), ["324a8d8"])
    item("distinct names", len({r["name"] for r in allrows}), 103)
    item("first stamp = one bin (all records)", all(abs(r["first_stamp_ms"] - r["cfg"]["network"]["rate_bin_ms"]) < 1e-9 for r in allrows if r["first_stamp_ms"] is not None), True)
    ctrls = rows["C2_S8"] + rows["C2_S9"] + rows["C2_S10"]
    s8h = sorted([r for r in rows["S8"] if r["name"].startswith("S8_head")], key=lambda r: (r["T"], r["seed"]))
    s8c = [r for r in rows["S8"] if r["name"].startswith("S8_cells")]

    # mean-field references ---------------------------------------------------------------------------------
    refy = yaml.safe_load((ROOT / "configs/ms10/mf_references.yaml").read_text(encoding="utf-8"))["references"]
    head_ref = {}
    for ref in refy:
        jp = ROOT / [f for f in ref["files"] if f.endswith(".json")][0]
        row = raw = mf_row(jp, thr)
        sc = ref["stored_class"]
        if FROZEN:
            row = {**row, "f_pk_hz": float(sc["f_pk_hz"]), "onset_s": float(sc["onset_s"])}
        head_ref[float(ref["T_ramp_s"])] = row
        item(f"stored MF ref T={ref['T_ramp_s']}: class / onset / f_pk recomputed vs stored",
             (row["class"], round(raw["onset_s"], 3), round(raw["f_pk_hz"], 2)), (sc["class"], sc["onset_s"], sc["f_pk_hz"]))
    comp = [mf_row(p, thr) for p in read_dir(ROOT / "results/S8/mf/S8_mf_cells") + read_dir(ROOT / "results/S8/mf/S8_mf_head60")]
    item("companion MF records", len(comp), 5)
    head_dt = (round(float(s8h[0]["Delta"]), 12), round(float(s8h[0]["tau_d"]), 12))
    comp_head60 = [c for c in comp if abs(c["T"] - 60.0) < 1e-9 and (round(float(c["Delta"]), 12), round(float(c["tau_d"]), 12)) == head_dt]
    item("companion headline 60 s record found", len(comp_head60), 1)
    head_ref[60.0] = comp_head60[0]
    cells_yaml = yaml.safe_load((ROOT / "configs/ms10/s8_cells.yaml").read_text(encoding="utf-8"))["cells"]
    import csv
    cand = {(int(r["i"]), int(r["j"])): r["class"] for r in csv.DictReader(open(ROOT / "docs/ms10_10b_s8_candidates.csv", newline="", encoding="utf-8"))}
    cell_ref, cell_stored = {}, {}
    for e in cells_yaml:
        c = e["c"]
        mine = sorted({(round(float(r["Delta"]), 12), round(float(r["tau_d"]), 12)) for r in s8c if r["group"] == c})
        item(f"cell {c} one (Delta, tau_d) among its network records", len(mine), 1)
        cm = [x for x in comp if abs(x["T"] - 30.0) < 1e-9 and (round(float(x["Delta"]), 12), round(float(x["tau_d"]), 12)) == mine[0]]
        item(f"cell {c} companion record found", len(cm), 1)
        cell_ref[c] = cm[0]
        cell_stored[c] = cand[(int(e["i"]), int(e["j"]))]
    item("companion classes = stored 120 s classes", [cell_ref[c]["class"] for c in range(4)], [cell_stored[c] for c in range(4)])

    # per-record class table -------------------------------------------------------------------------------------
    lines = ["list\tname\tN\tshape\tT_ramp\tgroup\tseed\tclass"]
    for k, v in rows.items():
        for r in sorted(v, key=lambda r: (r["name"])):
            lines.append(f"{k}\t{r['name']}\t{r['N']}\t{r['het']}\t{r['T']}\t{r['group']}\t{r['seed']}\t{r['class']}")
    out = ROOT / "results/ms10/10g"
    out.mkdir(parents=True, exist_ok=True)
    (out / ("record_classes_pass2.tsv" if FROZEN else "record_classes.tsv")).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    # sigma check ---------------------------------------------------------------------------------------------------
    sg = section("## Sigma check")
    base = ROOT / "results/S5/baseline/S5base_0000_1fe2ceaa1659"
    with np.load(base.with_suffix(".npz")) as z:
        vb = z["v"]
    per = [float(np.std(vb[s, 0:5000], ddof=1)) for s in range(vb.shape[0])]
    ref_std = 0.039522 if FROZEN else float(np.mean(per))
    print(f"sigma reference used {ref_std!r} (recomputed {float(np.mean(per))!r})")
    item("sigma reference recomputed (6 decimals)", f"{float(np.mean(per)):.6f}", "0.039522")
    t0 = tables(sg)[0]
    s8h_sorted = sorted(s8h, key=lambda r: r["name"])
    item("sigma table names", [r["name"] for r in s8h_sorted], [row[0] for row in t0])
    for r, row in zip(s8h_sorted, t0):
        item(f"sigma baseline std {r['name']}", f"{r['base_std']:.6f}", row[1])
    vals = [r["base_std"] for r in s8h]
    lo, hi = min(vals), max(vals)
    m = re.search(r"Range ([\d.]+) to ([\d.]+), mean ([\d.]+)\. Distinct values overall: (\d+); .*?Position of the reference in the range ([\-\d.]+) .*?margin to the nearest end ([\-\d.]+)\. Reference / network mean = ([\d.]+)\. \*\*Verdict: ([^*]+)\.\*\*", sg, re.S)
    item("sigma range lo, hi, mean", (f"{lo:.6f}", f"{hi:.6f}", f"{np.mean(vals):.6f}"), (m.group(1), m.group(2), m.group(3)))
    item("sigma distinct values", len({round(x, 12) for x in vals}), int(m.group(4)))
    item("sigma position in range", f"{(ref_std-lo)/(hi-lo):.4f}", m.group(5))
    item("sigma margin to nearest end", f"{min(ref_std-lo, hi-ref_std):.6f}", m.group(6))
    item("sigma ref / network mean", f"{ref_std/np.mean(vals):.4f}", m.group(7))
    inside = lo <= round(ref_std, 6) <= hi
    inside_exact = lo <= ref_std <= hi
    item("sigma verdict (inside, inclusive)", "PASS" if inside_exact else "NOT INSIDE (limitation; sigma stays frozen)", m.group(8))
    item("sigma inside using the rounded reference 0.039522 too", inside, False)
    per_seed = {s: {round(r["base_std"], 12) for r in s8h if r["seed"] == s} for s in range(3)}
    item("baselines identical across 10 s and 120 s per seed", all(len(x) == 1 for x in per_seed.values()), True)

    # RB1 headline -----------------------------------------------------------------------------------------------------
    rb = section("## RB1")
    th, tsum, tcell = tables(rb)[0], tables(rb)[1], tables(rb)[2]
    passes = {}
    for row in th:
        T, seed = float(row[0]), int(row[1])
        r = next(x for x in s8h if x["T"] == T and x["seed"] == seed)
        ref = head_ref[T]
        cm, cm_ph = corr_match(ref["class"], r["class"]), corr_match(ref["class"], r["class"], True)
        f, rf = r["f_pk"], ref["f_pk_hz"]
        relerr = abs(f - rf) / rf if math.isfinite(f) else float("nan")
        f_ok = bool(math.isfinite(relerr) and relerr <= ftol + EPS)
        on, ron = r["onset"], ref["onset_s"]
        on_ok = bool(math.isfinite(on) and math.isfinite(ron) and abs(on - ron) <= r["step"] + EPS)
        ps = cm and f_ok and on_ok
        passes.setdefault(T, []).append((ps, cm and f_ok and on_ok and cm_ph))
        tag = f"RB1 head T={T:g} seed {seed}"
        item(tag + " class", r["class"], row[2])
        item(tag + " MF class", ref["class"], row[3])
        item(tag + " class match / without S-rel", (str(cm), str(cm_ph)), (row[4], row[5]))
        cmp_cell(tag + " f_pk", f, row[6])
        cmp_cell(tag + " MF f_pk", rf, row[7])
        cmp_cell(tag + " rel err", relerr, row[8])
        cmp_cell(tag + " diff bins", (f - rf) / r["bin_hz"], row[9].split(" ")[0])
        cmp_cell(tag + " bin Hz", r["bin_hz"], row[9].split("(")[1].rstrip(")"))
        item(tag + " f_pk ok", str(f_ok), row[10])
        cmp_cell(tag + " onset (classifier)", on, row[11])
        cmp_cell(tag + " MF onset", ron, row[12])
        cmp_cell(tag + " onset diff", on - ron, row[13])
        cmp_cell(tag + " step", r["step"], row[14])
        item(tag + " onset ok", str(on_ok), row[15])
        cmp_cell(tag + " raw-crossing onset", r["raw_onset"], row[16])
        item(tag + " pass", str(ps), row[17])
    for row in tsum:
        T = float(row[0])
        g = sorted([x for x in s8h if x["T"] == T], key=lambda x: x["seed"])
        n_pass = sum(1 for p, _ in passes[T] if p)
        n_ph = sum(1 for _, p in passes[T] if p)
        item(f"RB1 head T={T:g} seeds passing", f"{n_pass} of 3", row[1])
        item(f"RB1 head T={T:g} passing without S-rel", f"{n_ph} of 3", row[2])
        item(f"RB1 head T={T:g} C2 controls", cls_str(ctrl_classes(g[0], ctrls)), row[3])
        fm = float(np.median([x["f_pk"] for x in g]))
        om = float(np.median([x["onset"] for x in g]))
        ref = head_ref[T]
        fok = abs(fm - ref["f_pk_hz"]) / ref["f_pk_hz"] <= ftol + EPS
        ook = abs(om - ref["onset_s"]) <= g[0]["step"] + EPS
        allm = all(corr_match(ref["class"], x["class"]) for x in g)
        item(f"RB1 head T={T:g} post-hoc median reading", f"{fmt(fm)}, {fok} / {fmt(om)}, {ook} / {allm}", row[4])
        item(f"RB1 head T={T:g} verdict", "PASS" if n_pass >= seeds_k else "FAIL", row[5])
    head_verdict = {T: ("PASS" if sum(1 for p, _ in passes[T] if p) >= seeds_k else "FAIL") for T in passes}

    # RB1 cells --------------------------------------------------------------------------------------------------------
    agree = {}
    for row in tcell:
        c = int(row[0].split()[0])
        g = sorted([x for x in s8c if x["group"] == c], key=lambda x: x["seed"])
        ref = cell_ref[c]
        ms = [corr_match(ref["class"], x["class"]) for x in g]
        ms_ph = [corr_match(ref["class"], x["class"], True) for x in g]
        agree[c] = all(ms)
        tag = f"RB1 cell {c}"
        item(tag + " companion MF class", ref["class"], row[1])
        item(tag + " stored 120 s class", cell_stored[c], row[2])
        item(tag + " network classes", ", ".join(x["class"] for x in g), row[3])
        item(tag + " seeds matching / without S-rel", (f"{sum(ms)} of 3", f"{sum(ms_ph)} of 3"), (row[4], row[5]))
        item(tag + " C2 controls", cls_str(ctrl_classes(g[0], ctrls)), row[6])
        item(tag + " agrees", str(agree[c]), row[7])
    n_agree = sum(agree.values())
    n_ph = sum(all(corr_match(cell_ref[c]["class"], x["class"], True) for x in s8c if x["group"] == c) for c in range(4))
    m = re.search(r"Cells agreeing: (\d+) of (\d+) \(need (\d+)\); without S-rel \(post hoc\) (\d+)\. Cells part: \*\*(\w+)\*\*", rb)
    cells_verdict = "PASS" if n_agree >= cells_k else "FAIL"
    item("RB1 cells agreeing, of, need, post hoc, verdict", (n_agree, 4, cells_k, n_ph, cells_verdict), (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), m.group(5)))

    # S9 / N rule ---------------------------------------------------------------------------------------------------------
    s9 = sorted(rows["S9"], key=lambda r: (r["N"], r["seed"]))
    ref60 = head_ref[60.0]
    mm = re.search(r"companion class (\S+)\): N = 1e4: (\d+); N = 3e4: (\d+) \(without S-rel: (\d+) and (\d+)\)\. N = 3e4 no worse than 1e4: \*\*(\w+)\*\*", rb)
    cnt = {N: sum(corr_match(ref60["class"], r["class"]) for r in s9 if r["N"] == N) for N in (1000, 3000, 10000, 30000)}
    cnt_ph = {N: sum(corr_match(ref60["class"], r["class"], True) for r in s9 if r["N"] == N) for N in (10000, 30000)}
    nr = "PASS" if cnt[30000] >= cnt[10000] else "FAIL"
    item("N rule: class, 1e4, 3e4, post hoc 1e4, 3e4, verdict", (ref60["class"], cnt[10000], cnt[30000], cnt_ph[10000], cnt_ph[30000], nr),
         (mm.group(1).rstrip(")"), int(mm.group(2)), int(mm.group(3)), int(mm.group(4)), int(mm.group(5)), mm.group(6)))
    rb1_parts = (head_verdict[10.0], head_verdict[120.0], cells_verdict, nr)
    rb1_verdict = "PASS" if all(x == "PASS" for x in rb1_parts) else "FAIL"
    mv = re.search(r"Parts: headline (\{.*?\}), cells (\w+), N rule (\w+)\. \*\*RB1: (\w+)\*\*", rb)
    item("RB1 parts and verdict", (str({10.0: head_verdict[10.0], 120.0: head_verdict[120.0]}), cells_verdict, nr, rb1_verdict),
         (mv.group(1).replace("'10.0'", "10.0").replace("'120.0'", "120.0"), mv.group(2), mv.group(3), mv.group(4)))

    s9sec = section("## S9")
    t9a, t9b = tables(s9sec)[0], tables(s9sec)[1]
    for row in t9a:
        N = int(row[0])
        g = [r for r in s9 if r["N"] == N]
        tag = f"S9 N={N}"
        item(tag + " seeds", len(g), int(row[1]))
        item(tag + " classes", cls_str(collections.Counter(r["class"] for r in g)), row[2])
        item(tag + " surge seeds", sum(r["class"] in SURGE for r in g), int(row[3]))
        item(tag + " matching primary / without S-rel", f"{sum(corr_match(ref60['class'], r['class']) for r in g)} / {sum(corr_match(ref60['class'], r['class'], True) for r in g)}", row[4])
        fe = med_rng([abs(r["f_pk"] - ref60["f_pk_hz"]) / ref60["f_pk_hz"] if math.isfinite(r["f_pk"]) else float("nan") for r in g if math.isfinite(r["f_pk"])])
        oe = med_rng([abs(r["onset"] - ref60["onset_s"]) for r in g if math.isfinite(r["onset"])])
        item(tag + " f_pk rel err", f"{fmt(fe[2])} [{fmt(fe[3])}, {fmt(fe[4])}] (n {fe[0]})", row[5])
        item(tag + " onset abs err", f"{fmt(oe[2])} [{fmt(oe[3])}, {fmt(oe[4])}] (n {oe[0]})", row[6])
        item(tag + " C2 controls", cls_str(ctrl_classes(g[0], ctrls)), row[7])
    Ns = [1000, 3000, 10000, 30000]
    reasons = {N: collections.Counter() for N in Ns}
    for row in t9b:
        mname = row[0]
        for N, cell in zip(Ns, row[1:]):
            g = [r for r in s9 if r["N"] == N]
            n, nu, md, mn, mx = med_rng([r["metrics"][mname] for r in g])
            for r in g:
                if mname in r["undef"]:
                    reasons[N][f"{mname}: {r['undef'][mname]}"] += 1
            mine = f"{fmt(md)} [{fmt(mn)}, {fmt(mx)}]; {n}/{nu}" if n else f"-; 0/{nu}"
            if mine == cell:
                item(f"S9 metric {mname} N={N}", mine, cell)
            else:
                # tolerate last-digit rounding boundary only
                nums = lambda s: [float(x) for x in re.findall(r"-?\d+\.?\d*(?:e[+-]?\d+)?", s)]
                a, b = nums(mine), nums(cell)
                near = len(a) == len(b) and all(abs(x - y) <= 6e-4 * abs(y) + 1e-12 for x, y in zip(a, b)) and mine.split(";")[-1] == cell.split(";")[-1]
                if near:
                    REPORT.append(("MATCH(rounding-boundary)", f"S9 metric {mname} N={N}", mine, cell))
                    print(f"MATCH(rb)  S9 metric {mname} N={N}: {mine!r} | {cell!r}")
                else:
                    item(f"S9 metric {mname} N={N}", mine, cell)
    for N in Ns:
        mt = re.search(rf"Undefined reasons, N = {N}: (.*)\.\n", s9sec + "\n")
        logged = collections.Counter()
        if mt and mt.group(1) != "none":
            for part in mt.group(1).split("; "):
                k, _, v = part.rpartition(": ")
                logged[k] += int(v)
        item(f"S9 undefined reasons N={N}", dict(reasons[N]), dict(logged))
    # undefined counts independent of the metric table: unterminated and no-episode
    for N in Ns:
        g = [r for r in s9 if r["N"] == N]
        item(f"S9 N={N} (no episode, unterminated episode)", (sum(r["ep"] is None for r in g), sum(r["ep"] is not None and not r["ep"].terminated for r in g)),
             (reasons[N].get("onset_s: no_episode", 0), reasons[N].get("J_exit_run: episode_unterminated_at_run_end", 0)))

    # S10 / RB8 ------------------------------------------------------------------------------------------------------
    s10sec = section("## S10")
    t10 = tables(s10sec)[0]
    s10 = rows["S10"]
    for row in t10:
        r = next(x for x in s10 if x["het"] == row[0] and x["seed"] == int(row[1]))
        item(f"S10 {row[0]} seed {row[1]} class, level", (r["class"], level(r["class"])), (row[2], row[3]))
    lor = sorted([r for r in s10 if r["het"] == "lorentzian"], key=lambda r: r["seed"])
    lev = {level(r["class"]) for r in lor}
    ms = re.search(r"Lorentzian classes (\[.*?\]); C2 control classes beside the Lorentzian \(N = 1e4, 60 s\): (.*?); Lorentzian seeds in the mean-field-matching class: (\d+) of 3\. \*\*RB8 heterogeneity part: ([\w ]+)\*\*", s10sec)
    rb8_v = "NOT EVALUABLE" if len(lev) != 1 else None
    if rb8_v is None:
        hits = {sh: sum(level(r["class"]) == next(iter(lev)) for r in s10 if r["het"] == sh) for sh in ("gaussian", "uniform")}
        rb8_v = "PASS" if all(h >= rb8_seeds for h in hits.values()) else "FAIL"
    item("RB8 Lorentzian classes, controls, MF-matching seeds, verdict",
         (str([r["class"] for r in lor]), cls_str(ctrl_classes(lor[0], ctrls)), sum(corr_match(ref60["class"], r["class"]) for r in lor), rb8_v),
         (ms.group(1), ms.group(2), int(ms.group(3)), ms.group(4)))
    item("RB8 Gaussian and uniform classes", ({sh: [r["class"] for r in sorted(s10, key=lambda r: r["seed"]) if r["het"] == sh] for sh in ("gaussian", "uniform")}),
         {"gaussian": ["S-abs"] * 3, "uniform": ["S-abs"] * 3})

    # G4 --------------------------------------------------------------------------------------------------------------
    g4sec = section("## G4")
    t4 = tables(g4sec)[0]
    pools = {
        10000: {"S8:headline": [r for r in s8h if r["N"] == 10000], "S9": [r for r in rows["S9"] if r["N"] == 10000],
                "S10:lorentzian": [r for r in rows["S10"] if r["N"] == 10000 and r["het"] == "lorentzian"]},
        30000: {"S9": [r for r in rows["S9"] if r["N"] == 30000]}}
    pooled = {}
    for N, d in pools.items():
        allr = [r for v in d.values() for r in v]
        pooled[N] = (len(allr), sum(r["class"] in SURGE for r in allr), sum(r["class"] in ("S+", "S-abs") for r in allr))
    flat = []
    for N, d in pools.items():
        n, s, sp = pooled[N]
        flat.append((f"N = {N}", n, 0, s, sp, str(s == 0)))
        for k, v in d.items():
            flat.append((k, len(v), 0, sum(r["class"] in SURGE for r in v), sum(r["class"] in ("S+", "S-abs") for r in v), ""))
    for mine, row in zip(flat, t4):
        item(f"G4 row {mine[0]}", tuple(str(x) for x in mine), tuple(row))
    item("G4 rows", len(flat), len(t4))
    miss_both = all(pooled[N][1] == 0 for N in pooled)
    disagree = 4 - n_agree
    trig = rb1_verdict != "PASS" and (miss_both or disagree >= 2)
    mg = re.search(r"RB1: (\w+)\. Cells in disagreement, 2 or more: (\w+)\. G4 triggered: (\w+)\.", g4sec)
    item("G4 RB1, cells disagree >= 2, triggered", (rb1_verdict, str(disagree >= 2), str(trig)), (mg.group(1), mg.group(2), mg.group(3)))
    m1 = re.search(r"\(1\) Network misses the surge at N = 1e4 and 3e4 \(no pooled seed at that N in a surge class\): (\w+)", g4sec)
    m2 = re.search(r"\(2\) Disagreement in 2 or more of the 4 cells: (\w+)", g4sec)
    item("G4 text (1) misses, (2) cells", ("YES" if miss_both else "no", "YES" if disagree >= 2 else "no"), (m1.group(1), m2.group(1)))

    # summary ---------------------------------------------------------------------------------------------------------
    nd = sum(1 for r in REPORT if r[0] == "DIFFERENCE")
    nrb = sum(1 for r in REPORT if r[0].startswith("MATCH(rounding"))
    print(f"\n{len(REPORT)} items compared, {nd} DIFFERENCE, {nrb} rounding-boundary matches; 103 records classified (results/ms10/10g/record_classes.tsv)")
    with open(out / ("independent_report_pass2.txt" if FROZEN else "independent_report.txt"), "w", encoding="utf-8", newline="\n") as f:
        for ok, name, got, logged in REPORT:
            f.write(f"{ok}\t{name}\trecomputed={got!r}\tlogged={logged!r}\n")
        f.write(f"SUMMARY\t{len(REPORT)} items\t{nd} DIFFERENCE\t{nrb} rounding-boundary\n")
    return 0 if nd == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
