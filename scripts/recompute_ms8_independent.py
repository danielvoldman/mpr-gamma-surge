"""8g: independent recomputation of the key RB numbers from the raw stored records (analysis only; no simulation, no verdict).

Does NOT import rb_eval, rb_tables or a7 (and does not read the A7 parquet to compute anything). Inputs: the stored run records (json +
npz series under results/S5 and results/S13), analysis.surge_metrics (classifier, envelope, onset_delay), the A4 grid step from
configs/A4_grids.yaml, the frozen threshold and solver floor read from the tag blob of criteria-frozen, and, for item (e) only,
analysis.entry_exit (the eigenvalue integral that gives t_pred and eta_pred; it is not in the npz series and cannot be rebuilt from
surge_metrics). Compares each number with results/A7/rb_eval_ms8.json (and, as a cross-check, run by run with the stored parquet) and
writes results/A7/recompute_ms8_independent.json. A difference is listed with its size; nothing is judged here.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mprsurge.analysis import entry_exit as EE          # noqa: E402  (item (e) only)
from mprsurge.analysis import surge_metrics as M         # noqa: E402
from mprsurge.units import tau_to_s                      # noqa: E402

TAG = "criteria-frozen"
BASES = ("results/S5/ramp", "results/S5/ramp_noise", "results/S13")
OUT = ROOT / "results/A7/recompute_ms8_independent.json"


def frozen():
    txt = subprocess.run(["git", "show", f"{TAG}:configs/robustness_criteria.yaml"], cwd=ROOT, capture_output=True, check=True).stdout
    crit = yaml.safe_load(txt.decode("utf-8"))

    def find(o, key):
        if isinstance(o, dict):
            if key in o:
                v = o[key]
                return v["value"] if isinstance(v, dict) and "value" in v else v
            for v in o.values():
                r = find(v, key)
                if r is not None:
                    return r
        return None

    g = yaml.safe_load((ROOT / "configs/A4_grids.yaml").read_text(encoding="utf-8"))["grids"]["eta_bar"]
    return {"threshold": float(find(crit, "threshold_abs")), "solver_floor": float(find(crit, "solver_floor_noise_free_v")),
            "grid_step": (g["hi"] - g["lo"]) / (g["n"] - 1), "grid_step_frozen_value": float(find(crit, "a4_eta_bar_grid_step")),
            "c_T": [float(x) for x in find(crit, "c_T_ramp_s")], "dt_ladder": [float(x) for x in find(crit, "heun_dt_ladder_tau")],
            "dt_default": float(find(crit, "heun_default_dt_tau"))}


def records():
    out = []
    for b in BASES:
        for p in sorted((ROOT / b).rglob("*.json")):
            if not p.name.endswith(".dry.json"):
                out.append(p)
    return out


def one(args):
    """Per-record recomputation from the npz series. Returns a plain dict."""
    jp, threshold, h, floor = args
    jp = Path(jp)
    rec = json.loads(jp.read_text(encoding="utf-8"))
    cfg = rec["config"]
    with np.load(jp.with_suffix(".npz")) as z:
        t_ms, v, eta = z["t_ms"], z["v"], z["eta"]
    p, kind = cfg["path"], cfg["run"]["kind"]
    fs = 1000.0 / cfg["solver"]["dt_out_ms"]
    t_s = t_ms / 1000.0
    noisy = kind == "mf_noisy"
    res = (M.classify_mode_n if noisy else M.classify_mode_d)(v, fs, p["t_on_s"], p["T_ramp_s"], threshold)
    ep = res.episode
    out = {"run_id": jp.stem, "family": jp.parent.name, "path_name": p["name"], "profile": p["profile"], "T": float(p["T_ramp_s"]),
           "start_distance": float(p["eta_H"] - p["eta_start"]), "kind": kind, "delta0": float(cfg["solver"]["delta0"]),
           "rtol": None if noisy else float(cfg["solver"]["rtol"]), "method": cfg["solver"]["method"],
           "dt": float(cfg["noise"]["dt_tau"]) if noisy else None,
           "sigma": float(cfg["noise"]["sigma"] * cfg["noise"]["sigma_factor"]) if noisy else None,
           "seed": int(cfg["seeds"]["spawn_key"][-1]) if cfg["seeds"]["spawn_key"] is not None else None,
           "cls": res.cls, "onset_s": None if ep is None else ep.onset_s}
    if ep is not None:
        out["eta_onset"], out["delay"] = M.onset_delay(ep.onset_s, t_s, eta, p["eta_H"])
    else:
        out["eta_onset"] = out["delay"] = None
    env = M.envelope(v, fs, M.G_BAND)
    i_on = int(round(p["t_on_s"] * fs))
    hit = np.flatnonzero(env[i_on:] >= threshold)
    if hit.size:
        tc = float((i_on + hit[0]) / fs)
        out["onset_cross_s"] = tc
        out["eta_cross"], out["delay_cross"] = M.onset_delay(tc, t_s, eta, p["eta_H"])
    else:
        out["onset_cross_s"] = out["eta_cross"] = out["delay_cross"] = None
    return out


def predict_all(rows, threshold, h, floor):
    """Item (e): eta_pred, in-range flag and match error for the noise-free S5 ramps (entry_exit, cached per path)."""
    cache, res = {}, {}
    for r in rows:
        if r["kind"] != "mf" or not r["run_file"].startswith("results/S5/ramp/"):
            continue
        cfg = json.loads(Path(r["json"]).read_text(encoding="utf-8"))["config"]
        key = json.dumps([cfg["path"], cfg["model"], cfg["durations"]], sort_keys=True, default=str)
        if key not in cache:
            cache[key] = EE.path_gain(cfg, h)
        path, t, re, I = cache[key]
        pr = EE.entry_exit(cfg, path, t, re, I, r["delta0"], threshold, h)
        tp = pr["t_pred"]
        in_range = None if tp is None else bool(r["delta0"] * np.exp(pr["I_min"]) >= floor)
        res[r["run_id"]] = {"t_pred_s": None if tp is None else tau_to_s(tp, cfg["model"]["tau_ms"]), "eta_pred": pr["eta_on"], "in_range": in_range,
                            "eta_const": None if tp is None else bool(pr["tol_step"] is None), "I_min": pr["I_min"],
                            "err_steps": None if (tp is None or r["eta_cross"] is None) else abs(r["eta_cross"] - pr["eta_on"]) / h}
    return res


def near(a, b, rtol=2e-3):
    return bool(np.isclose(a, b, rtol=rtol, atol=0.0))


def median_exclude(x):
    x = np.asarray([np.nan if y is None else y for y in x], float)
    ok = x[~np.isnan(x)]
    return float(np.median(ok)) if ok.size else float("nan"), int(np.isnan(x).sum())


def main():
    fz = frozen()
    assert abs(fz["grid_step"] - fz["grid_step_frozen_value"]) < 1e-12, "A4 grid step in configs/A4_grids.yaml differs from the frozen value"
    h, thr, floor = fz["grid_step"], fz["threshold"], fz["solver_floor"]
    files = records()
    with Pool(6) as pool:
        rows = pool.map(one, [(str(f), thr, h, floor) for f in files], chunksize=2)
    for r, f in zip(rows, files):
        r["json"] = str(f)
        r["run_file"] = str(f.relative_to(ROOT)).replace("\\", "/")
    ev = json.loads((ROOT / "results/A7/rb_eval_ms8.json").read_text(encoding="utf-8"))
    cmp_rows = []                                              # (item, mine, stored, agree, note)

    def cmp(item, mine, stored, note=""):
        if mine is None or stored is None:
            agree = mine is None and stored is None
        elif isinstance(mine, float) or isinstance(stored, float):
            agree = bool(mine == stored) or (math.isnan(mine) and math.isnan(stored))
        else:
            agree = mine == stored
        diff = None if not isinstance(mine, float) or not isinstance(stored, float) or math.isnan(mine) else mine - stored
        cmp_rows.append({"item": item, "mine": mine, "stored": stored, "agree": bool(agree), "diff": diff, "note": note})

    by = {r["run_id"]: r for r in rows}
    fam = lambda f: [r for r in rows if r["family"] == f]
    # (a) headline, S13 rtol, delta0, Radau
    head = fam("S5ramp")[0]
    rt = ev["RB6_solvers"]["rtol_ladder"]
    mine_rt = sorted([head] + fam("rtol"), key=lambda r: r["rtol"])
    for m_, s_ in zip(mine_rt, rt):
        tag = f"(a) rtol {m_['rtol']:g} ({s_['source']})"
        for a, b in (("cls", "cls"), ("onset_s", "onset_s"), ("onset_cross_s", "onset_cross_s"), ("delay", "delay_eta"), ("delay_cross", "delay_eta_cross")):
            cmp(f"{tag} {a}", m_[a], s_[b])
    rd = fam("radau")[0]
    sv = ev["RB6_solvers"]["dop853_vs_radau"]
    for a, b, who in (("cls", "dop853_headline_cls", head), ("onset_s", "onset_class_dop853_s", head), ("onset_cross_s", "onset_cross_dop853_s", head),
                      ("delay", "delay_eta_dop853", head), ("cls", "radau_cls", rd), ("onset_s", "onset_class_radau_s", rd),
                      ("onset_cross_s", "onset_cross_radau_s", rd), ("delay", "delay_eta_radau", rd)):
        cmp(f"(a) {'Radau' if who is rd else 'DOP853'} {a}", who[a], sv[b])
    cmp("(a) onset diff Radau - DOP853 (ms, class)", (rd["onset_s"] - head["onset_s"]) * 1000.0, sv["onset_diff_ms_class"])
    cmp("(a) onset diff Radau - DOP853 (ms, cross)", (rd["onset_cross_s"] - head["onset_cross_s"]) * 1000.0, sv["onset_diff_ms_cross"])
    d0 = {1e-6: head} | {r["delta0"]: r for r in fam("delta0")}
    for row in ev["RB5"]["delta0_headline"]["ladder"]:
        m_ = next(v for k, v in d0.items() if math.isclose(k, row["delta0"], rel_tol=1e-9))
        for a, b in (("cls", "cls"), ("onset_s", "onset_s"), ("onset_cross_s", "onset_cross_s"), ("delay", "delay_eta"), ("delay_cross", "delay_eta_cross")):
            cmp(f"(a) delta0 {row['delta0']:g} {a}", m_[a], row[b])
    # (b), (c) floor ladder
    fl = [r for r in rows if r["family"].startswith("floor_")]
    sig = sorted({round(r["sigma"], 15) for r in fl})
    lvl = lambda r: sig.index(round(r["sigma"], 15))
    tab = {}
    for r in fl:
        tab.setdefault((lvl(r), next(d for d in fz["dt_ladder"] if math.isclose(d, r["dt"], rel_tol=1e-9))), []).append(r)
    for k in tab:
        tab[k].sort(key=lambda r: r["seed"])
    dflt, fine = fz["dt_default"], min(fz["dt_ladder"])
    for on, key, evk in (("cross", "delay_cross", "cross"), ("class", "delay", "class")):
        meds = []
        for L in range(3):
            e, miss = median_exclude([r[key] for r in tab[(L, dflt)]])
            meds.append(e)
            s = ev["RB3b"]["by_onset"][evk][repr(dflt)]["levels"][L]
            cmp(f"(b) {on} onset, default rung, level {L} median (exclude)", e, s["median_exclude"], f"missing {miss} of {len(tab[(L, dflt)])}")
            cmp(f"(b) {on} onset, default rung, level {L} n_missing", miss, s["n_missing"])
        dec = bool(all(b < a for a, b in zip(meds, meds[1:]))) if not any(math.isnan(x) for x in meds) else None
        cmp(f"(b) {on} onset, default rung, strictly decreasing (exclude)", dec,
            ev["RB3b"]["by_onset"][evk][repr(dflt)]["strictly_decreasing_exclude"])
        for L in range(3):
            a_, _ = median_exclude([r[key] for r in tab[(L, dflt)]])
            b_, _ = median_exclude([r[key] for r in tab[(L, fine)]])
            rel = abs(b_ - a_) / abs(a_)
            cmp(f"(c) {on} onset, Heun rel change 1e-4 vs 1e-3, level {L}", rel, ev["RB6_heun"]["by_onset"][evk][L]["rel_change"])
    # (d) RB3(c): P2 linear classes at the four T_ramp
    pc = ev["RB3c"]["primary"]
    for T, sc in zip(fz["c_T"], pc["classes"]):
        m_ = [r for r in fam("p2_linear") if near(r["T"], T)]
        cmp(f"(d) P2 linear class at T_ramp {T:g}", m_[0]["cls"] if len(m_) == 1 else f"{len(m_)} matches", sc)
    cmp("(d) headline class", head["cls"], ev["RB3c"]["headline_class"])
    for T in fz["c_T"]:
        cnt = {}
        for r in fam("p2_noise"):
            if near(r["T"], T):
                cnt[r["cls"]] = cnt.get(r["cls"], 0) + 1
        cmp(f"(d) mode N P2 linear class counts at T_ramp {T:g}", dict(sorted(cnt.items())), dict(sorted(ev["RB3c"]["mode_N_P2_linear_10_seeds_class_counts"][repr(T)].items())))
    # (e) RB3(a)
    pred = predict_all(rows, thr, h, floor)
    mine_ir = [dict(by[k], **v) for k, v in pred.items() if v["in_range"]]
    stored_ir = ev["RB3a"]["runs"]
    cmp("(e) number of in-range S5 runs", len(mine_ir), ev["RB3a"]["n_in_range"])
    errs = []
    for s in stored_ir:
        m_ = [r for r in mine_ir if r["family"] == s["family"] and near(r["T"], s["T_ramp_s"]) and math.isclose(r["start_distance"], s["start_distance"], abs_tol=1e-9)]
        if len(m_) != 1:
            cmp(f"(e) {s['family']} T {s['T_ramp_s']:g} sd {s['start_distance']:g} found", len(m_), 1)
            continue
        m_ = m_[0]
        tag = f"(e) {s['family']} T {s['T_ramp_s']:.4g} sd {s['start_distance']:g}"
        cmp(f"{tag} eta_const", m_["eta_const"], s["eta_const_at_t_pred"])
        cmp(f"{tag} error in A4 steps", m_["err_steps"], s["match_err_steps_cross"], "testable" if not m_["eta_const"] else "eta constant at t_pred")
        cmp(f"{tag} eta_pred", m_["eta_pred"], s["eta_pred"])
        errs.append({"run": tag, "testable": not m_["eta_const"], "err_steps": m_["err_steps"]})
    testable = [e for e in errs if e["testable"]]
    cmp("(e) testable runs", len(testable), ev["RB3a"]["n_testable"])
    cmp("(e) testable within one step", sum(e["err_steps"] <= 1.0 for e in testable), ev["RB3a"]["primary"]["n_within_one_step"])
    # (f) class counts per path and profile, S5 and S13
    counts = {}
    for r in rows:
        lst = "S13" if r["run_file"].startswith("results/S13") else "S5"
        pp = {"path_eta": "P1", "path_hypoxia": "P2", "path_updown": "P5"}[r["path_name"]]
        counts.setdefault(f"{lst} {r['family']} ({pp} {r['profile']}, {r['kind']})", {}).setdefault(r["cls"], 0)
        counts[f"{lst} {r['family']} ({pp} {r['profile']}, {r['kind']})"][r["cls"]] += 1
    import pandas as pd
    df = pd.read_parquet(ROOT / "results/A7/a7_ramp_metrics.parquet")
    for k, v in counts.items():
        fam_ = k.split()[1]
        lst = k.split()[0]
        sub = df[(df.family == fam_) & (df.list == lst)]
        cmp(f"(f) class counts {k}", dict(sorted(v.items())), {a: int(b) for a, b in sorted(sub.cls.value_counts().items())}, "stored = parquet cross-check")
    # P2 surge counts in json
    for tag, fam_ in (("mode D, P2 linear", "p2_linear"), ("mode D, P2 sigmoid", "p2_sigmoid"), ("mode N, P2 linear (10 seeds)", "p2_noise")):
        surge = ("D-tr",) if fam_ != "p2_noise" else ("S+", "S-rel", "S-abs")
        lo, hi = min(fz["c_T"]), max(fz["c_T"])
        inside = [r for r in fam(fam_) if lo * (1 - 2e-3) <= r["T"] <= hi * (1 + 2e-3)]
        outside = [r for r in fam(fam_) if r not in inside]
        s = ev["P2_surge_class_counts"]["rows"][tag]
        cmp(f"(f) {tag} surge runs inside 56-316 s", sum(r["cls"] in surge for r in inside), s["n_surge_inside_window"])
        cmp(f"(f) {tag} runs inside 56-316 s", len(inside), s["n_runs_inside_window"])
        cmp(f"(f) {tag} surge runs outside", sum(r["cls"] in surge for r in outside), s["n_surge_outside_window"])
        cmp(f"(f) {tag} runs outside", len(outside), s["n_runs_outside_window"])
    # run-level cross-check against the parquet
    bad = []
    for r in rows:
        q = df[df.run_id == r["run_id"]]
        if len(q) != 1:
            bad.append((r["run_id"], "not in parquet"))
            continue
        q = q.iloc[0]
        for a, b in (("cls", "cls"), ("onset_s", "onset_s"), ("onset_cross_s", "onset_cross_s"), ("delay", "delay_eta"), ("delay_cross", "delay_eta_cross")):
            x, y = r[a], q[b]
            same = (x is None and (y is None or pd.isna(y))) or (x is not None and not (isinstance(y, float) and pd.isna(y)) and x == y)
            if not same:
                bad.append((r["run_id"], a, x, None if (isinstance(y, float) and pd.isna(y)) else y))
    disagree = [c for c in cmp_rows if not c["agree"]]
    summary = {"n_records": len(rows), "n_comparisons": len(cmp_rows), "n_agree": len(cmp_rows) - len(disagree), "n_disagree": len(disagree),
               "run_level_crosscheck_vs_parquet": {"n_runs": len(rows), "n_fields": 5 * len(rows), "n_differences": len(bad), "differences": bad[:50]},
               "frozen_inputs_used": fz}
    OUT.write_text(json.dumps({"summary": summary, "comparisons": cmp_rows, "rb3a_testable_errors": errs, "class_counts": counts}, indent=1, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=1, default=str))
    for c in disagree:
        print("DIFF", c)
    print("(e) testable errors (A4 steps):", [(e["run"], round(e["err_steps"], 4)) for e in testable])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
