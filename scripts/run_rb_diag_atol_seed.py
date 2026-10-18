"""8f6 analysis (DL-200, DL-201): (a) the two EXPLORATORY atol runs of the headline cell against the stored atol 1e-12 headline run; (b) the effective
seed against the ramp-kink burst, from stored data only. Reads stored records, integrates nothing, changes no rule. Writes the NEW file
results/A7/rb_diag_atol_seed.json (no existing rb_eval or rb_diag file is touched). EXPLORATORY; no G6 verdict.
Effective seed = 0.1 x A_ref x exp(-(I(t_c) - I(t_on))), I the existing entry_exit eigenvalue integral (the quantity behind the 8f2 offsets),
t_c the observed raw first crossing. Burst = envelope above 1e-12 (DL-196), via rb_diag_burst.
"""
import json
import math
import sys
import time

import numpy as np
import pandas as pd

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a7, rb_diag as D, rb_diag_burst as B, rb_diag_expl as X

sys.path.insert(0, str(C.repo_root() / "scripts"))
from run_rb_diag_burst import base_report, cache_gain, seg_view   # noqa: E402  (stored-data helpers of 8f5, unchanged)

OUT_JSON = "results/A7/rb_diag_atol_seed.json"
HEAD = "results/S5/ramp/S5ramp/S5ramp_0000_240de3ef73be.json"
DEFAULT_LAB = "1e-12"
A_REF = 2.176222


def atol_part(root, thr):
    runs = {DEFAULT_LAB: root / HEAD}
    for jp in sorted((root / "results/ms8_diag/atol").glob("explatol_*.json")):
        runs[jp.stem.split("_")[1]] = jp
    rows = {}
    for lab, jp in runs.items():
        b = base_report(jp, thr)
        cfg, p = b["cfg"], b["cfg"]["path"]
        tJ = p["t_on_s"] + p["J_lag_frac"] * p["T_ramp_s"]
        s_on, s_J = B.segment_at(b["segs"], p["t_on_s"]), B.segment_at(b["segs"], tJ)
        growth = next((s for s in b["segs"] if s["kind"] == "growth"), None)
        win = D.decade_window(b["env"], b["ic"], thr)
        g = D.growth_rate_per_tau(b["t_s"], b["env"], win[0], win[1], b["tau"]) * 1000.0 / b["tau"]
        eta_c = float(b["arr"]["eta"][b["ic"]])
        rows[lab] = {"run_id": jp.stem, "config_hash12": b["rec"]["config_hash12"], "atol": cfg["solver"]["atol"], "git_commit": b["rec"]["git"]["commit"],
                     "git_dirty": b["rec"]["git"]["dirty"], "label": b["rec"]["flags"].get("label"), "wall_time_s": b["rec"].get("wall_time_s"),
                     "onset_cross_s": b["onset"], "eta_onset_cross": eta_c, "delay_eta_cross": eta_c - p["eta_H"],
                     "floor_10_to_30s": X.plateau_floor(b["env"], b["t_s"], 10.0, 30.0), "t_on_burst": seg_view(s_on), "J_start_burst": seg_view(s_J),
                     "growth_segment": seg_view(growth), "growth_rate_per_s": g}
    ref = rows[DEFAULT_LAB]
    for lab, r in rows.items():
        r["onset_minus_default_ms"] = 1000.0 * (r["onset_cross_s"] - ref["onset_cross_s"])
        r["growth_start_minus_default_ms"] = 1000.0 * (r["growth_segment"]["start_s"] - ref["growth_segment"]["start_s"])
        for nm in ("t_on_burst", "J_start_burst"):
            r[f"{nm}_times_equal_default"] = all(r[nm][k] == ref[nm][k] for k in ("start_s", "end_s", "peak_s"))
            r[f"{nm}_peak_over_default"] = r[nm]["peak"] / ref[nm]["peak"]
    return {"runs": rows, "dop853_vs_radau_onset_difference_ms": 181.0,
            "note": "181 ms is the DL-189 / DL-198 DOP853-vs-Radau onset difference (58.879 - 58.698 s)"}


def seed_row(jp, thr, h, cache, tag):
    b = base_report(jp, thr)
    cfg, tau, p = b["cfg"], b["tau"], b["cfg"]["path"]
    t_on = float(p["t_on_s"])
    path, t, re, I = cache_gain(cfg, h, cache)
    oc = b["onset"]
    dI = B.net_gain(t, re, I, t_on, oc, tau)
    seed = B.effective_seed(thr, dI)
    s_on = B.segment_at(b["segs"], t_on)
    if s_on is None:
        burst, why = None, "no envelope above 1e-12 at t_on"
    elif s_on["kind"] != "pre":
        burst, why = None, f"t_on lies in the {s_on['kind']} segment {s_on['start_s']:.3f} to {s_on['end_s']:.3f} s"
    elif len(s_on["breakpoints_inside_s"]) > 1:
        burst, why = None, f"merged with other breakpoints {s_on['breakpoints_inside_s']}"
    else:
        burst, why = s_on, "lone pre-onset burst at t_on"
    return {"tag": tag, "run_id": jp.stem, "path": p["name"], "profile": p["profile"], "T_ramp_s": float(p["T_ramp_s"]), "delta0": cfg["solver"]["delta0"],
            "start_distance": float(p["eta_H"] - p["eta_start"]), "onset_cross_s": oc, "net_gain_t_on_to_onset": dI, "effective_seed": seed,
            "log10_effective_seed": math.log10(seed), "delta0_over_effective_seed": cfg["solver"]["delta0"] / seed,
            "burst_status": "separable" if burst else "not separable", "burst_note": why, "burst_peak": None if burst is None else burst["peak"],
            "burst_peak_s": None if burst is None else burst["peak_s"],
            "ratio_effective_seed_over_burst_peak": None if burst is None else seed / burst["peak"]}, b


def p5_prediction(root, thr, h, cache):
    """P5 linear T 1.778: burst-seeded prediction, burst amplitude EXTRAPOLATED from the lone t_on bursts of the other P5 linear runs."""
    files = [q for q in sorted((root / "results/S5/ramp/p5_linear").glob("*.json")) if ".dry" not in q.name]
    k, lag, target = [], [], None
    for jp in files:
        b = base_report(jp, thr)
        p = b["cfg"]["path"]
        T = float(p["T_ramp_s"])
        if abs(T - 1.778) < 0.01:
            target = (jp, b)
        s = B.segment_at(b["segs"], float(p["t_on_s"]))
        if s is not None and s["kind"] == "pre" and len(s["breakpoints_inside_s"]) == 1:
            k.append(s["peak"] * T)
            lag.append(s["peak_s"] - float(p["t_on_s"]))
    jp, b = target
    cfg, tau, p = b["cfg"], b["tau"], b["cfg"]["path"]
    T = float(p["T_ramp_s"])
    amp, ts = float(np.median(k)) / T, float(p["t_on_s"]) + float(np.median(lag))
    path, t, re, I = cache_gain(cfg, h, cache)
    pr = B.seed_prediction(cfg, path, t, re, I, ts, amp, thr, h)
    eta_c = float(b["arr"]["eta"][b["ic"]])
    s_on = B.segment_at(b["segs"], float(p["t_on_s"]))
    pr.update(run_id=jp.stem, T_ramp_s=T, seed_time_s=ts, seed_amp_extrapolated=amp,
              extrapolation="peak = median(peak x T_ramp over the separable lone t_on bursts of the other P5 linear runs) / T_ramp; time = t_on + median(peak lag); "
                            "a reasoned extrapolation, the burst itself is not separable at this T_ramp; UNVERIFIED",
              n_lone_bursts_used=len(k), peak_times_T_ramp_median=float(np.median(k)), peak_times_T_ramp_min_max=[float(min(k)), float(max(k))],
              lag_median_s=float(np.median(lag)),
              burst_separable_at_this_T=bool(s_on is not None and s_on["kind"] == "pre" and len(s_on["breakpoints_inside_s"]) == 1),
              onset_cross_observed_s=b["onset"], eta_onset_cross=eta_c,
              onset_minus_t_pred_s=None if pr["t_pred_s"] is None else b["onset"] - pr["t_pred_s"],
              A4_steps_eta=None if pr["eta_pred"] is None else abs(eta_c - pr["eta_pred"]) / h)
    ee0 = a7.predict(cfg, float(cfg["solver"]["delta0"]), thr, h, cache={})
    pr["a7_as_built_t_pred_s"] = None if ee0["t_pred"] is None else float(ee0["t_pred"] * tau / 1000.0)
    return pr


def main() -> int:
    t0 = time.time()
    root = C.repo_root()
    fi, _ = a7.frozen_inputs(root)
    thr, h = fi["threshold"], fi["grid_step"]
    assert math.isclose(thr, 0.1 * A_REF, rel_tol=1e-6), (thr, A_REF)
    env_info = P.environment_info(with_julia=False)
    out = {"label": B.LABEL, "reason": "post-hoc after DL-198; outside S5, S13 and every rb_eval manifest; feeds no gate; no G6 verdict. The atol values 1e-10 and "
           "1e-14 are the reviewer's diagnostic choices, NOT plan values.", "threshold": thr, "A_ref": A_REF, "a4_grid_step": h}
    out["atol"] = atol_part(root, thr)
    df = pd.read_parquet(root / "results/A7/a7_ramp_metrics.parquet")
    s5 = df[(df.list == "S5") & (df.in_range == True)]       # noqa: E712
    assert len(s5) == 9
    cache, rows = {}, []
    for _, a in s5.iterrows():
        r, b = seed_row(root / "results/S5/ramp" / a.family / f"{a.run_id}.json", thr, h, cache, "S5 in-range")
        r["onset_matches_a7_table"] = bool(b["onset"] == a.onset_cross_s)
        rows.append(r)
    sets = sorted((root / "results/ms8_diag_rerun/setA").glob("explA_*.json"))
    assert len(sets) == 4
    for jp in sets:
        r, b = seed_row(jp, thr, h, cache, "Set A (clean re-run)")
        r["record_git_dirty"] = b["rec"]["git"]["dirty"]
        rows.append(r)
    out["effective_seed"] = rows
    out["p5_linear_T1p778_burst_seeded"] = p5_prediction(root, thr, h, cache)
    p = root / OUT_JSON
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    cfg0 = C.resolve_config("configs/A7.yaml")
    P.write_run_record(P.make_run_record(cfg0, env_info, name="RBDIAGATOLSEED_0000", status="ok", wall_time_s=time.time() - t0,
                                         outputs={"rb_diag_atol_seed.json": P.sha256_file(p)}, flags={"label": B.LABEL}),
                       p.parent / f"RBDIAGATOLSEED_0000_{C.short_hash(C.config_hash(cfg0))}.json")
    print("sha256", P.sha256_file(p), "git_dirty", env_info["git"]["dirty"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
