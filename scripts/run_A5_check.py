"""A5 against S4 check and K7 amplitude half (plan 5.2 A5, Table 7.1 K7, CP23; MS6 step 6e, DL-129).

Reads the saved results (A5 cycles, S4 mean-field and network summaries, S3 summaries); integrates nothing.
Writes results/A5/check/a5_check.{npz,json} and a run record. Rules as pre-registered in DL-126 D-3 and DL-129.
"""
import json
import sys

import numpy as np
import yaml

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import cycle_check as cc

POSTHOC_WINDOW_MS = (0.05, 0.3)    # post hoc near-Hopf window (owner example, DL-130), UNVERIFIED
S4_STEP = 0.1                     # eta_bar step of the S4 grid (DL-127)
NPZ = {"a5": "results/A5/a5_cycles.npz", "s4": "results/S4/s4_summary.npz", "net": "results/S4/s4_net_summary.npz",
       "s3": "results/S3/s3_mf_summary.json", "s3net": "results/S3/s3_net_summary.json"}


def load(root):
    return {k: (np.load(root / v) if v.endswith("npz") else json.loads((root / v).read_text())) for k, v in NPZ.items()}


def a5_vs_s4(d, eta_H):
    a5, s4 = d["a5"], d["s4"]
    out, arrays = {}, {}
    for key, hopf, excl_step in (("devalle", eta_H, S4_STEP), ("ceni", None, None)):
        up_dir = a5[f"{key}_direction_up"]
        pa, am = a5[f"{key}_param"], a5[f"{key}_amplitude_v"]
        if key == "ceni":
            pa = a5["ceni_tau_d_ms"]
        param, s4amp, up = s4[f"{key}_param"], s4[f"{key}_v_ptp"], s4[f"{key}_up"].astype(bool)
        ref = cc.interp_branch(pa[up_dir], am[up_dir], param)
        excl = cc.near_mask(param, hopf, excl_step) if hopf is not None else np.zeros(param.size, bool)
        res = {"up": [], "down": []}
        for name, sel in (("up", up), ("down", ~up)):
            j = cc.judge(param[sel], s4amp[sel], ref[sel], excl[sel])
            res[name] = {"max_abs_rel_diff": j["max_abs_rel_diff"], "n_judged": int(j["judged"].sum()),
                         "pass": j["pass"], "judged_params": param[sel][j["judged"]].tolist(),
                         "excluded": [{"param": float(p), "s4": float(a), "a5": float(r), "rel_diff": float(x)}
                                      for p, a, r, x in zip(param[sel][excl[sel]], s4amp[sel][excl[sel]],
                                                            ref[sel][excl[sel]], j["rel_diff"][excl[sel]])],
                         "no_a5_branch": param[sel][~np.isfinite(ref[sel])].tolist()}
            arrays[f"{key}_{name}_rel_diff"], arrays[f"{key}_{name}_judged"] = j["rel_diff"], j["judged"]
        arrays[f"{key}_a5_at_s4"], arrays[f"{key}_s4_v_ptp"], arrays[f"{key}_s4_param"] = ref, s4amp, param
        arrays[f"{key}_s4_up"], arrays[f"{key}_excluded"] = up, excl
        res["max_abs_rel_diff"] = max(res["up"]["max_abs_rel_diff"], res["down"]["max_abs_rel_diff"])
        res["pass"] = res["up"]["pass"] and res["down"]["pass"]
        res["r_ptp_s4_info"] = {"param": param.tolist(), "up": up.tolist(), "r_ptp": s4[f"{key}_r_ptp"].tolist()}
        out[key] = res
    return out, arrays


def k7(d):
    a5, s4, s3 = d["a5"], d["s4"], d["s3"]["cells"]["K7"]
    H = float(a5["ceni_hopf_tau_d_ms"][0])
    param, amp, up = s4["ceni_param"], s4["ceni_v_ptp"], s4["ceni_up"].astype(bool)
    out = {"hopf_ms": H, "window_ms": cc.FIT_WINDOW_MS}
    for name, sel in (("up", up), ("down", ~up)):
        f = cc.amplitude_fit(param[sel], amp[sel], H)
        out[f"s4_{name}"] = {k: v for k, v in f.items() if k not in ("x_ms", "a2")}
    pairs = {c: s4[f"ceni_pair_{c}"] for c in ("param", "v_ptp_up", "v_ptp_down")}
    out["hysteresis"] = cc.hysteresis(pairs["v_ptp_up"], pairs["v_ptp_down"])
    out["hysteresis"]["in_window_max_abs_diff"] = float(np.max(np.abs(pairs["v_ptp_up"] - pairs["v_ptp_down"])[
        (pairs["param"] - H > 0.1) & (pairs["param"] - H < 1.0 + 1e-9)]))
    # A5 branch on the same window: at the S4 window values, and at its own points in the window
    ud = a5["ceni_direction_up"]
    td, am = a5["ceni_tau_d_ms"][ud], a5["ceni_amplitude_v"][ud]
    f5 = cc.amplitude_fit(td, am, H)
    out["a5_own_points"] = {k: v for k, v in f5.items() if k not in ("x_ms", "a2")}
    win = param[up][(param[up] - H >= 0.1 - 1e-9) & (param[up] - H <= 1.0 + 1e-9)]
    f5i = cc.amplitude_fit(win, cc.interp_branch(td, am, win), H)
    out["a5_at_s4_window"] = {k: v for k, v in f5i.items() if k not in ("x_ms", "a2")}
    # POST HOC, exploratory (DL-130): narrower window near the Hopf point on A5's own points, no new simulation; cannot change the verdict
    ph = cc.amplitude_fit(td, am, H, window=POSTHOC_WINDOW_MS)
    out["posthoc_near_hopf"] = {"label": "POST HOC exploratory, not pre-registered", "window_ms": POSTHOC_WINDOW_MS,
                                **{k: v for k, v in ph.items() if k not in ("x_ms", "a2")}}
    out["slope_ratio_s4_up_over_a5_own"] = out["s4_up"]["slope"] / f5["slope"]
    cross = {}
    for t in ("4.95", "8.0"):
        a5v = float(cc.interp_branch(td, am, [float(t)])[0])
        s3v = s3[t]["v_ptp_mean"]
        cross[t] = {"a5": a5v, "s3_3d_mf": s3v, "rel_diff_s3_vs_a5": (s3v - a5v) / a5v,
                    "s3_mf_r_ptp": s3[t]["r_ptp_mean"], "s3_net_r_ptp_5g": d["s3net"]["cells"][f"ceni_{t.rstrip('0').rstrip('.')}ms"]["net"]["r_ptp"]}
    out["cross_check_3d_5g"] = cross
    return out


def net_info(d):
    n = d["net"]
    p, up = n["net_param"], n["net_up"].astype(bool)
    eta_H = float(d["a5"]["devalle_hopf_eta_bar"][0])
    rows = [{"param": float(p[i]), "up": bool(up[i]), "r_ptp_net": float(n["net_r_ptp"][i]), "r_ptp_mf": float(n["cmp_mf_r_ptp"][i]),
             "rel_r": float(n["cmp_rel_r_ptp"][i]), "v_ptp_net": float(n["net_v_ptp"][i]), "v_ptp_mf": float(n["cmp_mf_v_ptp"][i]),
             "rel_v": float(n["cmp_rel_v_ptp"][i])} for i in range(p.size)]
    below = p < eta_H - 0.1 - 1e-9
    above = p > eta_H + 0.1 + 1e-9
    far = p > eta_H + 0.2
    return {"rows": rows,
            "noise_floor_below_eta_H": {"n_steps": int(below.sum()), "r_ptp_min": float(n["net_r_ptp"][below].min()),
                                        "r_ptp_max": float(n["net_r_ptp"][below].max()), "r_ptp_mean": float(n["net_r_ptp"][below].mean()),
                                        "v_ptp_min": float(n["net_v_ptp"][below].min()), "v_ptp_max": float(n["net_v_ptp"][below].max())},
            "at_eta_H": [r for r in rows if abs(r["param"] - eta_H) < 1e-6],
            "max_abs_rel_r_above": float(np.nanmax(np.abs(n["cmp_rel_r_ptp"][above]))),
            "max_abs_rel_v_above": float(np.nanmax(np.abs(n["cmp_rel_v_ptp"][above]))),
            "max_abs_rel_v_far": float(np.nanmax(np.abs(n["cmp_rel_v_ptp"][far])))}


def main(argv=None) -> int:
    root = C.repo_root()
    d = load(root)
    eta_H = yaml.safe_load((root / "configs/path_A4.yaml").read_text(encoding="utf-8"))["path"]["eta_H"]
    cmp5, arrays = a5_vs_s4(d, eta_H)
    info = {"eta_H": eta_H, "a5_vs_s4": cmp5, "k7_amplitude": k7(d), "network_info": net_info(d), "rel_tol": cc.REL_TOL}
    out_dir = root / "results" / "A5" / "check"
    out_dir.mkdir(parents=True, exist_ok=True)
    P.atomic_save_npz(out_dir / "a5_check.npz", arrays)
    (out_dir / "a5_check.json").write_text(json.dumps(info, indent=1, default=float), encoding="utf-8")
    cfg = C.resolve_config("configs/A5.yaml")
    env = P.environment_info(with_julia=False)
    rec = P.make_run_record(cfg, env, name="A5check_0000", status="ok", wall_time_s=0.0, flags={"kind": "analysis_only"},
                            inputs={v: P.sha256_file(root / v) for v in NPZ.values()},
                            outputs={"a5_check.npz": P.sha256_file(out_dir / "a5_check.npz")})
    P.write_run_record(rec, out_dir / "A5check_0000.json")
    print(json.dumps({k: info[k] for k in ("a5_vs_s4", "k7_amplitude")}, indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
