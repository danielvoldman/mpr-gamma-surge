"""8f3 analysis (DL-191): EXPLORATORY report of the Set A and Set B diagnostic runs (scripts/run_ms8_diag_runs.py). Reads stored records only.
Writes results/A7/rb_diag_exploratory.json (new file; rb_diag_ms8.json and rb_eval_ms8.json are not touched) and a run record. No verdict."""
import json
import sys
import time

import numpy as np
import pandas as pd

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a7, rb_diag, rb_diag_expl as X
from mprsurge.analysis import surge_metrics as M

OUT_JSON = "results/A7/rb_diag_exploratory.json"
TABLE = "results/A7/a7_ramp_metrics.parquet"
KEEP = ("run_id", "config_hash12", "git_commit", "delta0", "T_ramp_s", "start_distance", "onset_cross_s", "eta_onset_cross", "t_pred_s", "t_on_s")


def load(jp):
    rec = P.read_run_record(jp)
    with np.load(jp.with_suffix(".npz")) as z:
        return rec, {k: z[k] for k in z.files}


def main() -> int:
    t0 = time.time()
    root = C.repo_root()
    fi, _ = a7.frozen_inputs(root)
    thr, h = fi["threshold"], fi["grid_step"]
    env_info = P.environment_info(with_julia=False)
    df = pd.read_parquet(root / TABLE)
    cache = {}
    out = {"label": X.LABEL, "reason": "post-hoc diagnostics after the 8f2 findings; outside S5, S13 and every rb_eval manifest; feed no gate; no G6 verdict",
           "input_table_sha256": P.sha256_file(root / TABLE), "threshold": thr}

    def row(jp):
        r = a7.run_row(jp, fi, "EXPL", cache)
        return {k: (None if isinstance(r[k], float) and np.isnan(r[k]) else r[k]) for k in KEEP}, r

    # ---- Set A ----
    A = []
    for T in (1.0, 10.0):
        refs = df[(df.list == "S5") & (df.family == "p1_start_distance") & np.isclose(df.T_ramp_s, T) & np.isclose(df.start_distance, 0.5)]
        assert len(refs) == 1
        ref_jp = next((root / "results/S5/ramp/p1_start_distance").glob(f"{refs.iloc[0].run_id}.json"))
        rrec, rarr = load(ref_jp)
        rrow = refs.iloc[0].to_dict()
        d = rb_diag.rb3a_run(rrec["config"], rarr, rrow, thr, h)
        mre, tau_ms = d["mean_re_lambda_over_window"], rrec["config"]["model"]["tau_ms"]
        entries = [{"role": "reference S5 run", "delta0": 1e-6, "onset_cross_s": float(rrow["onset_cross_s"]), "eta_onset_cross": float(rrow["eta_onset_cross"]),
                    "run_id": rrow["run_id"], "config_hash12": rrow["config_hash12"], "growth_window_s": d["growth_window_s"], "mean_re_lambda_per_tau": mre,
                    "growth_rate_per_tau": d["growth_rate_per_tau"]}]
        for d0 in X.SET_A_DELTA0:
            jp = next((root / "results/ms8_diag/setA").glob(f"explA_T{T:g}_d{d0:g}_*.json"))
            rec, _arr = load(jp)
            k, r = row(jp)
            assert rec["flags"]["label"] == X.LABEL
            obs = k["onset_cross_s"] - float(rrow["onset_cross_s"])
            pred = X.predicted_shift_s(d0, X.REF_DELTA0, mre, tau_ms)
            entries.append({**k, "role": "exploratory", "config_hash": rec["config_hash"], "git_dirty": rec["git"].get("dirty"), "obs_shift_s": obs, "pred_shift_s": pred,
                            "ratio_obs_over_pred": X.shift_ratio(obs, pred), "t_on_s": float(r["t_on_s"])})
        A.append({"T_ramp_s": T, "start_distance": 0.5, "runs": entries})
    out["setA"] = A
    out["setA_pattern"] = X.pattern([e["ratio_obs_over_pred"] for blk in A for e in blk["runs"] if e["role"] == "exploratory"])
    out["setA_pattern_label"] = "exploratory reading; thresholds for the words are ours (0.5 to 1.5 follows the kick, |ratio| below 0.25 does not follow)"

    # ---- Set B ----
    B = []
    ref_jp = next(p for p in (root / "results/S5/ramp").rglob("S5ramp_0000_*.json") if not p.name.endswith(".dry.json"))
    cands = [("unperturbed (stored S5 headline run)", ref_jp)] + [(f"v {s} ulp", next((root / "results/ms8_diag/setB").glob(f"explB_{t}_*.json")))
                                                               for s, t in (("+1", "ulp_plus"), ("-1", "ulp_minus"))]
    for lab, jp in cands:
        rec, arr = load(jp)
        k, r = row(jp)
        fs = 1000.0 / rec["config"]["solver"]["dt_out_ms"]
        env = M.envelope(arr["v"], fs, M.G_BAND)
        B.append({"which": lab, **k, "config_hash": rec["config_hash"], "git_dirty": rec["git"].get("dirty"), "y_start": rec["flags"].get("y_start"),
                  "floor_10_to_48s": X.plateau_floor(env, arr["t_ms"] / 1000.0)})
    ons = [b["onset_cross_s"] for b in B]
    out["setB"] = B
    out["setB_spread_ms"] = (max(ons) - min(ons)) * 1000.0
    out["setB_dop853_vs_radau_ms"] = 181.0
    out["setB_dop853_vs_radau_source"] = "DL-189 (onset 58.698 s against 58.879 s)"
    p = root / OUT_JSON
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    cfg0 = C.resolve_config("configs/A7.yaml")
    P.write_run_record(P.make_run_record(cfg0, env_info, name="RBDIAGEXPL_0000", status="ok", wall_time_s=time.time() - t0,
                                         outputs={"rb_diag_exploratory.json": P.sha256_file(p)}, flags={"label": X.LABEL}),
                       p.parent / f"RBDIAGEXPL_0000_{C.short_hash(C.config_hash(cfg0))}.json")
    print(json.dumps({k: out[k] for k in ("setA_pattern", "setB_spread_ms")}), "\njson", P.sha256_file(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
