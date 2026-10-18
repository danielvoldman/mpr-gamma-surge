"""8g: O12 data package for the P2-based S5 runs (stored data only; analysis only; no definition chosen, no verdict).

Per run (P2 linear and sigmoid noise-free at 13 T_ramp, the headline cell, the 130 mode-N runs): J_exit,run (surge_metrics.j_exit_metrics at
the classifier episode end), J_exit,static, the exit delay (run minus static, O14), the baseline rate r0 (mean r over the 5 s before t_on, the
collapse_time convention), r at J_exit,run, the minimum r after it, the mean r over the 1 s and the 5 s after it, the mean r from it to the end
of the run, the mean r over the last second of the run, and the D9 collapse time (first sample at or after t_on with r < 10 percent of r0,
surge_metrics.collapse_time) and the first such sample at or after J_exit,run.

J_exit,static: the plan defines it as the J at which the path leaves the A4 oscillatory region and gives no operational rule. Working reading,
UNVERIFIED: the J of the last crossing of Re lambda_max = 0 (from positive to non-positive) along the path, with lambda(eta(t), J(t)) the
leading eigenvalue of the M3 fixed point (entry_exit.leading_re, the code A4 and A7 use), located on the entry_exit node grid and refined by
bisection in t. A run counts as having a defined J_exit,run when the classifier returns an episode that terminated before the record end.
Writes results/A7/o12_data_package.json and .csv.
"""
from __future__ import annotations

import json
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import yaml
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mprsurge import ramps                                # noqa: E402
from mprsurge.analysis import entry_exit as EE            # noqa: E402
from mprsurge.analysis import surge_metrics as M          # noqa: E402
from mprsurge.units import tau_to_s                       # noqa: E402

FAMILIES = ("p2_linear", "p2_sigmoid", "S5ramp", "p2_noise")
OUT = ROOT / "results/A7"


def frozen_threshold():
    txt = subprocess.run(["git", "show", "criteria-frozen:configs/robustness_criteria.yaml"], cwd=ROOT, capture_output=True, check=True).stdout
    crit = yaml.safe_load(txt.decode("utf-8"))

    def find(o):
        if isinstance(o, dict):
            if "threshold_abs" in o:
                return o["threshold_abs"]["value"]
            for v in o.values():
                r = find(v)
                if r is not None:
                    return r
    return float(find(crit))


def grid_step():
    g = yaml.safe_load((ROOT / "configs/A4_grids.yaml").read_text(encoding="utf-8"))["grids"]["eta_bar"]
    return (g["hi"] - g["lo"]) / (g["n"] - 1)


def j_exit_static(cfg, h):
    """J (model units) of the last positive-to-non-positive crossing of the leading Re lambda along the path; None if there is none."""
    path, t, re, _ = EE.path_gain(cfg, h)
    m = cfg["model"]
    td = m["tau_d_ms"] / m["tau_ms"]
    idx = [k for k in range(len(re) - 1) if re[k] > 0.0 >= re[k + 1]]
    if not idx:
        return None, None
    k = idx[-1]
    f = lambda x: EE.leading_re(float(path.eta(x)), float(path.J(x)), m["Delta"], td)
    ts = brentq(f, t[k], t[k + 1], xtol=1e-9)
    return float(path.J(ts)), tau_to_s(ts, m["tau_ms"])


def one(args):
    jp, threshold = args
    jp = Path(jp)
    rec = json.loads(jp.read_text(encoding="utf-8"))
    cfg = rec["config"]
    with np.load(jp.with_suffix(".npz")) as z:
        t_ms, r, v, J = z["t_ms"], z["r"], z["v"], z["J"]
    p, noisy = cfg["path"], cfg["run"]["kind"] == "mf_noisy"
    fs = 1000.0 / cfg["solver"]["dt_out_ms"]
    t_s = t_ms / 1000.0
    res = (M.classify_mode_n if noisy else M.classify_mode_d)(v, fs, p["t_on_s"], p["T_ramp_s"], threshold)
    ep = res.episode
    i_on = int(round(p["t_on_s"] * fs))
    i_lo = max(0, int(round((p["t_on_s"] - M.BASELINE_S) * fs)))
    r0 = float(r[i_lo:i_on].mean())
    out = {"run_id": jp.stem, "family": jp.parent.name, "T_ramp_s": float(p["T_ramp_s"]), "profile": p["profile"], "mode": "N" if noisy else "D",
           "seed": int(cfg["seeds"]["spawn_key"][-1]) if noisy else None, "cls": res.cls, "t_on_s": float(p["t_on_s"]), "run_end_s": float(t_s[-1]),
           "episode": ep is not None, "terminated": None if ep is None else bool(ep.terminated), "r0": r0,
           "collapse_s_from_t_on": M.collapse_time(r, fs, p["t_on_s"]), "J_exit_run": None}
    if ep is None or not ep.terminated:
        return out
    te = ep.end_s
    jr, _, _ = M.j_exit_metrics(te, t_s, J, 0.0)
    out.update(end_s=float(te), J_exit_run=jr, r_at_exit=float(np.interp(te, t_s, r)))
    after = r[t_s >= te]
    out["r_min_after"] = float(after.min())
    for w in (1.0, 5.0):
        sel = (t_s >= te) & (t_s < te + w)
        out[f"r_mean_{int(w)}s"] = float(r[sel].mean()) if te + w <= t_s[-1] + 1.0 / fs else None
    out["r_mean_to_run_end"] = float(after.mean())
    out["r_mean_last_1s"] = float(r[t_s >= t_s[-1] - 1.0].mean())
    below = np.flatnonzero((r < M.COLLAPSE_FRACTION * r0) & (t_s >= te))
    out["collapse_s_after_exit"] = float(t_s[below[0]]) if below.size else None
    return out


def summarize(vals):
    a = np.asarray([x for x in vals if x is not None], float)
    return None if a.size == 0 else {"n": int(a.size), "min": float(a.min()), "median": float(np.median(a)), "max": float(a.max())}


def main():
    thr, h = frozen_threshold(), grid_step()
    files = []
    for fam in FAMILIES:
        base = ROOT / ("results/S5/ramp_noise" if fam == "p2_noise" else "results/S5/ramp") / fam
        files += [p for p in sorted(base.glob("*.json")) if not p.name.endswith(".dry.json")]
    with Pool(6) as pool:
        rows = pool.map(one, [(str(f), thr) for f in files], chunksize=2)
    static, cache = {}, {}
    for f, row in zip(files, rows):
        cfg = json.loads(f.read_text(encoding="utf-8"))["config"]
        key = (cfg["path"]["T_ramp_s"], cfg["path"]["profile"])
        if key not in cache:
            cache[key] = j_exit_static(cfg, h)
        row["J_exit_static"], row["t_exit_static_s"] = cache[key]
        row["exit_delay"] = None if row["J_exit_run"] is None or row["J_exit_static"] is None else row["J_exit_run"] - row["J_exit_static"]
    groups = {"noise-free linear": [x for x in rows if x["family"] == "p2_linear"], "noise-free sigmoid": [x for x in rows if x["family"] == "p2_sigmoid"],
              "headline": [x for x in rows if x["family"] == "S5ramp"], "mode N (130 runs)": [x for x in rows if x["family"] == "p2_noise"]}
    summary = {}
    for g, xs in groups.items():
        d = [x for x in xs if x["J_exit_run"] is not None]
        summary[g] = {"n_runs": len(xs), "n_episode": sum(x["episode"] for x in xs), "n_J_exit_run_defined": len(d),
                      "n_episode_not_terminated": sum(1 for x in xs if x["episode"] and not x["terminated"]),
                      "n_J_exit_static_defined_among_defined": sum(x["J_exit_static"] is not None for x in d),
                      "classes": {c: sum(x["cls"] == c for x in xs) for c in sorted({x["cls"] for x in xs})},
                      **{k: summarize([x.get(k) for x in d]) for k in ("J_exit_run", "J_exit_static", "exit_delay", "r0", "r_at_exit", "r_min_after", "r_mean_1s", "r_mean_5s",
                                                                       "r_mean_to_run_end", "r_mean_last_1s", "collapse_s_after_exit")},
                      "n_collapse_after_exit": sum(x.get("collapse_s_after_exit") is not None for x in d),
                      "n_collapse_from_t_on_any": sum(x["collapse_s_from_t_on"] is not None for x in xs)}
    (OUT / "o12_data_package.json").write_text(json.dumps({"label": "O12 data package, stored data, no definition chosen (UNVERIFIED)", "threshold": thr,
                                                           "A4_grid_step": h, "J_exit_static_reading": "last crossing of Re lambda_max = 0 along the path, UNVERIFIED",
                                                           "summary": summary, "runs": rows}, indent=1), encoding="utf-8")
    cols = ["run_id", "family", "T_ramp_s", "profile", "mode", "seed", "cls", "episode", "terminated", "J_exit_run", "J_exit_static", "exit_delay", "r0", "end_s",
            "r_at_exit", "r_min_after", "r_mean_1s", "r_mean_5s", "r_mean_to_run_end", "r_mean_last_1s", "collapse_s_from_t_on", "collapse_s_after_exit", "run_end_s"]
    with open(OUT / "o12_data_package.csv", "w", encoding="utf-8") as fh:
        fh.write(",".join(cols) + "\n")
        for x in rows:
            fh.write(",".join("" if x.get(c) is None else str(x.get(c)) for c in cols) + "\n")
    print(json.dumps(summary, indent=1))
    print("headline:", json.dumps(groups["headline"][0], indent=1))


if __name__ == "__main__":
    main()
