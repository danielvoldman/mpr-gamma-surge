"""8f5 analysis (DL-196 to DL-198): stored-data diagnosis of the deterministic pre-onset burst, and the bit-for-bit comparison of the clean-tree
re-run of the 8f3 Sets A and B (scripts/run_ms8_diag_rerun.py) with the first runs. Reads stored records only, integrates nothing, changes no rule.
Writes the NEW file results/A7/rb_diag_burst.json (no existing rb_eval or rb_diag file is touched) and a run record. EXPLORATORY; no G6 verdict.

Items (reviewer 8f5 step 3): a four stored headline-family runs; b noise-free P2 S5 runs; c noise-free P1 and P5 S5 runs; d S13 delta0 ladder;
e burst-seeded entry-exit for the headline; f the same for the 8f4 start-distance runs next to the headline. Step 4: re-run comparison.
Definitions: src/mprsurge/analysis/rb_diag_burst.py (burst = envelope above 1e-12; the rest is existing A7 / rb_diag code, unchanged).
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import ramps
from mprsurge.analysis import a7, rb_diag as D, rb_diag_burst as B, entry_exit as EE
from mprsurge.analysis import surge_metrics as M
from mprsurge.units import s_to_tau, tau_to_s

OUT_JSON = "results/A7/rb_diag_burst.json"
TABLE = "results/A7/a7_ramp_metrics.parquet"
HEAD = "results/S5/ramp/S5ramp/S5ramp_0000_240de3ef73be.json"
OBSERVED_RADAU_SHIFT_S = 0.181                    # DL-189 (stated by the reviewer); recomputed below from the stored onsets


def load(jp):
    rec = P.read_run_record(jp)
    with np.load(Path(jp).with_suffix(".npz")) as z:
        return rec, {k: z[k] for k in z.files}


def base_report(jp, thr):
    """Envelope, raw crossing, classified segments and breakpoints of one stored noise-free run."""
    rec, arr = load(jp)
    cfg = rec["config"]
    tau = cfg["model"]["tau_ms"]
    fs = 1000.0 / cfg["solver"]["dt_out_ms"]
    t_s = arr["t_ms"] / 1000.0
    env = M.envelope(arr["v"], fs, M.G_BAND)
    i_on = int(round(cfg["path"]["t_on_s"] * fs))
    hit = np.flatnonzero(env[i_on:] >= thr)
    ic = int(i_on + hit[0]) if hit.size else None
    onset = float(ic / fs) if ic is not None else None       # as a7.first_crossing
    path = ramps.make_path(cfg)
    bps = B.breakpoints_s(path, tau)
    segs = B.classify_segments(B.segments(env, t_s), onset if onset is not None else math.inf, bps)
    return {"rec": rec, "arr": arr, "cfg": cfg, "tau": tau, "fs": fs, "t_s": t_s, "env": env, "ic": ic, "onset": onset, "path": path, "bps": bps, "segs": segs}


def seg_view(s):
    return None if s is None else {k: s[k] for k in ("start_s", "end_s", "peak_s", "peak", "kind", "breakpoints_inside_s", "peak_minus_breakpoint_s")}


def kink_table(b):
    """Per breakpoint: the segment containing it (view) or None, the peak times T_ramp for a lone pre-onset burst; plus segments with no breakpoint inside."""
    T = float(b["cfg"]["path"]["T_ramp_s"])
    per = []
    for x in b["bps"]:
        sg = B.segment_at(b["segs"], x)
        lone = sg is not None and sg["kind"] == "pre" and len(sg["breakpoints_inside_s"]) == 1
        per.append({"breakpoint_s": x, "segment": seg_view(sg), "lone_pre_onset_burst": lone, "peak_times_T_ramp_s": sg["peak"] * T if lone else None})
    orphan = [seg_view(s) for s in b["segs"] if s["kind"] == "pre" and not s["breakpoints_inside_s"]]      # pre-onset bursts at no breakpoint
    return per, orphan


def family_rows(files, thr, parquet):
    """3b / 3c rows: one per stored run."""
    rows = []
    for jp in files:
        b = base_report(jp, thr)
        per, orphan = kink_table(b)
        p = b["cfg"]["path"]
        row = {"run_id": jp.stem, "family": jp.parent.name, "T_ramp_s": float(p["T_ramp_s"]), "profile": p["profile"], "t_on_s": float(p["t_on_s"]),
               "onset_cross_s": b["onset"], "growth_segment": seg_view(next((q for q in b["segs"] if q["kind"] == "growth"), None)), "breakpoints_s": b["bps"], "by_breakpoint": per, "pre_onset_segments_without_breakpoint": orphan}
        if p["name"] == "path_hypoxia":
            row["J_start_expected_s"] = float(p["t_on_s"] + p["J_lag_frac"] * p["T_ramp_s"])
        if parquet is not None and jp.stem in parquet.index:
            row["onset_matches_a7_table"] = bool(b["onset"] == parquet.loc[jp.stem, "onset_cross_s"]) if b["onset"] is not None else bool(np.isnan(parquet.loc[jp.stem, "onset_cross_s"]))
        rows.append(row)
    rows.sort(key=lambda r: (r["family"], r["T_ramp_s"]))
    return rows


def p2_run(jp, thr, h, cache, label):
    """3a / 3d / 3e / 3f record of one run of the P2 headline cell family."""
    b = base_report(jp, thr)
    cfg, tau, env, t_s, fs = b["cfg"], b["tau"], b["env"], b["t_s"], b["fs"]
    p = cfg["path"]
    t_on = float(p["t_on_s"])
    tJ = t_on + p["J_lag_frac"] * p["T_ramp_s"]
    ic, oc = b["ic"], b["onset"]
    per, orphan = kink_table(b)
    s_on, s_J = B.segment_at(b["segs"], t_on), B.segment_at(b["segs"], tJ)
    growth = next((s for s in b["segs"] if s["kind"] == "growth"), None)
    win = D.decade_window(env, ic, thr)
    g_tau = D.growth_rate_per_tau(t_s, env, win[0], win[1], tau)
    g_s = g_tau * 1000.0 / tau
    # floors by interval, no window chosen by hand: between the two bursts, and between the J burst and the growth segment
    def med(a, z):
        m = (t_s > a) & (t_s < z)
        return None if not m.any() else {"median": float(np.median(env[m])), "min": float(env[m].min()), "max": float(env[m].max()), "n": int(m.sum())}
    floors = {}
    if s_on and s_J and s_on["kind"] == "pre" and s_J["kind"] == "pre":
        floors["between_t_on_burst_and_J_burst"] = med(s_on["end_s"], s_J["start_s"])
    if s_J and s_J["kind"] == "pre" and growth:
        floors["between_J_burst_and_growth"] = med(s_J["end_s"], growth["start_s"])
    # seeds
    path, t, re, I = cache_gain(cfg, h, cache)
    eta_oc = float(b["arr"]["eta"][ic])
    preds = {}
    ee0 = EE.entry_exit(cfg, path, t, re, I, float(cfg["solver"]["delta0"]), thr, h)
    seeds = {"delta0_at_t_on": (t_on, float(cfg["solver"]["delta0"]), "A7 as built (delta0 exp(I) = threshold from t_on)")}
    for name, s, why in (("t_on_burst_peak", s_on, "t_on burst"), ("J_start_burst_peak", s_J, "J-ramp-start burst")):
        if s is None:
            seeds[name] = None
        elif s["kind"] != "pre":
            seeds[name] = ("not_separable", s["kind"], f"{why} lies in the {s['kind']} segment {s['start_s']:.3f} to {s['end_s']:.3f} s")
        elif len(s["breakpoints_inside_s"]) > 1:
            seeds[name] = ("not_separable", "merged", f"{why} merged with other breakpoints {s['breakpoints_inside_s']}")
        else:
            seeds[name] = (s["peak_s"], s["peak"], why)
    for name, sd in seeds.items():
        if sd is None or sd[0] == "not_separable":
            preds[name] = {"status": "no_seed" if sd is None else sd[1], "note": None if sd is None else sd[2]}
            continue
        ts, amp, why = sd
        pr = B.seed_prediction(cfg, path, t, re, I, ts, amp, thr, h)
        dI = B.net_gain(t, re, I, ts, oc, tau)
        need = B.log10_seed_needed(thr, dI)
        pr.update(status="ok", note=why, seed_time_s=ts, seed_amp=amp, onset_cross_s=oc, net_gain_seed_to_onset=dI,
                  log10_seed_needed_for_observed_onset=need, log10_seed_amp=math.log10(amp), decades_needed_above_seed=need - math.log10(amp))
        if pr["t_pred_s"] is not None:
            pr["onset_minus_t_pred_s"] = oc - pr["t_pred_s"]
            pr["A4_steps_eta"] = abs(eta_oc - pr["eta_pred"]) / h        # |eta at observed onset - eta at t_pred| / 0.025, as match_err_steps
            pr["observed_delay_eta_cross"] = eta_oc - p["eta_H"]
        preds[name] = pr
    return {"label": label, "run_id": jp.stem, "config_hash12": b["rec"]["config_hash12"], "solver": cfg["solver"]["method"], "rtol": cfg["solver"]["rtol"],
            "delta0": cfg["solver"]["delta0"], "start_distance": float(p["eta_H"] - p["eta_start"]), "T_ramp_s": float(p["T_ramp_s"]), "t_on_s": t_on,
            "J_start_s": tJ, "breakpoints_s": b["bps"], "onset_cross_s": oc, "eta_onset_cross": eta_oc, "delay_eta_cross": eta_oc - p["eta_H"],
            "growth_rate_per_s": g_s, "growth_window_s": [float(t_s[win[0]]), float(t_s[win[1]])], "segments": [seg_view(s) for s in b["segs"]],
            "t_on_burst": seg_view(s_on), "J_start_burst": seg_view(s_J), "growth_segment": seg_view(growth), "floors": floors,
            "segments_without_breakpoint": orphan, "seed_predictions": preds,
            "a7_t_pred_delta0_s": None if ee0["t_pred"] is None else float(tau_to_s(ee0["t_pred"], tau))}, b


def cache_gain(cfg, h, cache):
    key = json.dumps([cfg["path"], cfg["model"], cfg["durations"], h], sort_keys=True, default=str)
    if key not in cache:
        cache[key] = EE.path_gain(cfg, h)
    return cache[key]


def spread(vals):
    v = np.asarray(vals, float)
    return {"values": [float(x) for x in v], "max_minus_min": float(v.max() - v.min()), "max_rel_spread": float((v.max() - v.min()) / abs(v.mean())) if v.mean() else None}


def item_3a(recs):
    """recs: label -> record from p2_run. DOP853 trio = rtol 1e-8, 1e-10 (S5 headline), 1e-12; Radau 1e-10."""
    d = [recs[k] for k in ("dop853_rtol1e-8", "dop853_rtol1e-10", "dop853_rtol1e-12")]
    rad, ref = recs["radau_rtol1e-10"], recs["dop853_rtol1e-10"]
    out = {"runs": {k: {"onset_cross_s": r["onset_cross_s"], "t_on_burst": r["t_on_burst"], "J_start_burst": r["J_start_burst"],
                        "growth_segment_start_s": r["growth_segment"]["start_s"], "growth_rate_per_s": r["growth_rate_per_s"]} for k, r in recs.items()}}
    for nm in ("t_on_burst", "J_start_burst"):
        out[f"dop853_trio_{nm}"] = {"start_s": [r[nm]["start_s"] for r in d], "end_s": [r[nm]["end_s"] for r in d], "peak_s": [r[nm]["peak_s"] for r in d],
                                    "peak": spread([r[nm]["peak"] for r in d]), "times_identical": len({(r[nm]["start_s"], r[nm]["end_s"], r[nm]["peak_s"]) for r in d}) == 1}
        ratio = rad[nm]["peak"] / ref[nm]["peak"]
        out[f"radau_over_dop853_{nm}_peak"] = ratio
        out[f"radau_{nm}_times_equal_dop853"] = (rad[nm]["start_s"], rad[nm]["end_s"], rad[nm]["peak_s"]) == (ref[nm]["start_s"], ref[nm]["end_s"], ref[nm]["peak_s"])
    ratio = out["radau_over_dop853_J_start_burst_peak"]
    obs = rad["onset_cross_s"] - ref["onset_cross_s"]
    out["observed_radau_onset_shift_s"] = obs
    out["observed_matches_stated_181_ms"] = abs(obs - OBSERVED_RADAU_SHIFT_S) < 5e-4
    out["implied_shift_s_dop853_growth_rate"] = B.implied_onset_shift_s(ratio, ref["growth_rate_per_s"])
    out["implied_shift_s_radau_growth_rate"] = B.implied_onset_shift_s(ratio, rad["growth_rate_per_s"])
    out["implied_over_observed"] = out["implied_shift_s_dop853_growth_rate"] / obs
    out["seed_ratio_that_would_give_the_observed_shift"] = math.exp(-ref["growth_rate_per_s"] * obs)
    out["growth_segment_start_shift_radau_minus_dop853_s"] = rad["growth_segment"]["start_s"] - ref["growth_segment"]["start_s"]
    out["onset_dop853_trio_s"] = [r["onset_cross_s"] for r in d]
    return out


def rerun_compare(root, thr):
    rows = []
    for sub in ("setA", "setB"):
        for jp1 in sorted((root / "results/ms8_diag" / sub).glob("expl*.json")):
            jp2 = root / "results/ms8_diag_rerun" / sub / jp1.name
            r1, a1 = load(jp1)
            if not jp2.exists():
                rows.append({"run": jp1.name, "rerun_found": False})
                continue
            r2, a2 = load(jp2)
            same, per = B.bit_equal_arrays(a1, a2)
            cfg = r1["config"]
            fs = 1000.0 / cfg["solver"]["dt_out_ms"]
            o1, o2 = (a7.first_crossing(a["v"], fs, cfg["path"]["t_on_s"], thr) for a in (a1, a2))
            rows.append({"run": jp1.name, "rerun_found": True, "arrays_bit_equal": same, "per_array": per, "onset_first_s": o1, "onset_rerun_s": o2,
                         "onset_equal": o1 == o2, "config_hash_equal": r1["config_hash"] == r2["config_hash"], "y_start_equal": r1["flags"].get("y_start") == r2["flags"].get("y_start"),
                         "first": {"git_commit": r1["git"]["commit"], "git_dirty": r1["git"]["dirty"], "wall_time_s": r1.get("wall_time_s")},
                         "rerun": {"git_commit": r2["git"]["commit"], "git_dirty": r2["git"]["dirty"], "wall_time_s": r2.get("wall_time_s")}})
    return {"first_records": "results/ms8_diag/setA, setB: SUPERSEDED by the clean-tree re-run, kept on disk unchanged",
            "rerun_records": "results/ms8_diag_rerun/setA, setB", "runs": rows,
            "all_bit_equal": all(r.get("arrays_bit_equal") for r in rows) and len(rows) == 6, "all_rerun_clean": all(r["rerun"]["git_dirty"] is False for r in rows if r["rerun_found"]),
            "n_runs": len(rows)}


def main() -> int:
    t0 = time.time()
    root = C.repo_root()
    fi, _ = a7.frozen_inputs(root)
    thr, h = fi["threshold"], fi["grid_step"]
    env_info = P.environment_info(with_julia=False)
    df = pd.read_parquet(root / TABLE)
    pq = df[df.list == "S5"].set_index("run_id")
    out = {"label": B.LABEL, "reason": "post-hoc stored-data diagnosis after the 8f3 finding of a deterministic pre-onset burst (DL-193); outside S5, S13 and every rb_eval manifest; "
           "feeds no gate; no G6 verdict", "burst_level": B.BURST_LEVEL, "threshold": thr, "a4_grid_step": h, "input_table_sha256": P.sha256_file(root / TABLE)}
    cache = {}
    # 3a, 3d, 3e: the headline-family runs
    def rec1(fam, stem):
        c = [q for q in (root / "results/S13" / fam).glob(f"{stem}_*.json") if ".dry" not in q.name]
        assert len(c) == 1, (fam, stem, c)
        return c[0]

    recs = {}
    for lab, jp in (("dop853_rtol1e-10", root / HEAD), ("dop853_rtol1e-8", rec1("rtol", "rtol_0000")),
                    ("dop853_rtol1e-12", rec1("rtol", "rtol_0001")), ("radau_rtol1e-10", rec1("radau", "radau_0000")),
                    ("delta0_1e-9", rec1("delta0", "delta0_0000")), ("delta0_1e-3", rec1("delta0", "delta0_0001"))):
        assert not jp.name.endswith(".dry.json")
        recs[lab], _ = p2_run(jp, thr, h, cache, lab)
    recs["delta0_1e-6"] = recs["dop853_rtol1e-10"]
    out["item_3a"] = item_3a(recs)
    out["item_3d"] = {lab: {"delta0": recs[lab]["delta0"], "onset_cross_s": recs[lab]["onset_cross_s"], "t_on_burst": recs[lab]["t_on_burst"], "J_start_burst": recs[lab]["J_start_burst"]}
                      for lab in ("delta0_1e-9", "delta0_1e-6", "delta0_1e-3")}
    out["item_3e"] = recs["dop853_rtol1e-10"]
    out["item_3e_radau"] = recs["radau_rtol1e-10"]
    # 3f: start distance 0.5, 1.5 (headline), 3
    f = {"1.5": recs["dop853_rtol1e-10"]}
    for jp in sorted((root / "results/ms8_diag/startdist").glob("supp_*.json")):
        r, _b = p2_run(jp, thr, h, cache, "supplementary")
        f[repr(r["start_distance"])] = r
    out["item_3f"] = dict(sorted(f.items(), key=lambda kv: float(kv[0])))
    # 3b, 3c
    def files(fams):
        return [p for fam in fams for p in sorted((root / "results/S5/ramp" / fam).glob("*.json")) if ".dry" not in p.name]
    out["item_3b"] = family_rows(files(("p2_linear", "p2_sigmoid")), thr, pq)
    out["item_3c"] = family_rows(files(("p1_linear", "p1_sigmoid", "p5_linear", "p5_sigmoid")), thr, pq)
    out["item_3c_extra_p1_start_distance"] = family_rows(files(("p1_start_distance",)), thr, pq)
    # step 4
    out["rerun_8f3"] = rerun_compare(root, thr)
    p = root / OUT_JSON
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    cfg0 = C.resolve_config("configs/A7.yaml")
    P.write_run_record(P.make_run_record(cfg0, env_info, name="RBDIAGBURST_0000", status="ok", wall_time_s=time.time() - t0,
                                         outputs={"rb_diag_burst.json": P.sha256_file(p)}, flags={"label": B.LABEL}),
                       p.parent / f"RBDIAGBURST_0000_{C.short_hash(C.config_hash(cfg0))}.json")
    print("sha256", P.sha256_file(p), "git_dirty", env_info["git"]["dirty"], "rerun_all_bit_equal", out["rerun_8f3"]["all_bit_equal"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
