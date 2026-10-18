"""8f2 driver (DL-186): stored-data diagnoses for the rulings (RB6 grid resolution, RB3(a) per run, DOP853 against Radau).
Reads results/A7/a7_ramp_metrics.parquet and the stored records, integrates nothing, changes no rule, makes no G6 statement.
Writes results/A7/rb_diag_ms8.json and a run record."""
import json
import sys
import time

import numpy as np
import pandas as pd

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a7, rb_diag, rb_eval

CONFIG = "configs/A7.yaml"
TABLE = "results/A7/a7_ramp_metrics.parquet"
OUT_JSON = "results/A7/rb_diag_ms8.json"


def load(records, run_id):
    jp = records[run_id]
    cfg = json.loads(jp.read_text(encoding="utf-8"))["config"]
    with np.load(jp.with_suffix(".npz")) as z:
        return cfg, {k: z[k] for k in z.files}


def main() -> int:
    t0 = time.time()
    root = C.repo_root()
    cfg0 = C.resolve_config(CONFIG)
    fi, _ = a7.frozen_inputs(root)
    env_info = P.environment_info(with_julia=False)
    tab = root / TABLE
    df = pd.read_parquet(tab)
    if set(df.criteria_sha256) != {fi["criteria_sha256"]}:
        raise SystemExit("parquet was written under a different frozen file")
    fv = rb_eval.frozen_values(root)
    records = {jp.stem: jp for _, jp in a7.record_files(root)}
    thr, h = fi["threshold"], fi["grid_step"]
    out = {"labels": "diagnoses are ours (UNVERIFIED as rules); explanations in the report are [reasoned, not tested]", "input_table_sha256": P.sha256_file(tab)}

    # ---- RB6 resolution ----
    fl = df[df.family.str.startswith("floor_")]
    dflt, fine = fv["dt_default"], min(fv["dt_ladder"])
    res = {"onset_cross": [], "onset_class": []}
    for lv, sig in enumerate(fv["floor_levels"]):
        a = fl[(fl.d43_level == lv) & np.isclose(fl.heun_dt_tau, dflt, rtol=1e-9)].sort_values("seed")
        b = fl[(fl.d43_level == lv) & np.isclose(fl.heun_dt_tau, fine, rtol=1e-9)].sort_values("seed")
        cfg, arr = load(records, a.iloc[0].run_id)
        for key, on_col, dl_col in (("onset_cross", "onset_cross_s", "delay_eta_cross"), ("onset_class", "onset_s", "delay_eta")):
            i = int(round(float(a.iloc[0][on_col]) * 1000.0 / cfg["solver"]["dt_out_ms"]))
            step = float(arr["eta"][i + 1] - arr["eta"][i])
            row = rb_diag.rb6_resolution_row(lv, sig, step, float(np.median(a[dl_col])), float(np.median(b[dl_col])), a[on_col].to_numpy(), b[on_col].to_numpy(),
                                             fv["rb6_max"], cfg["solver"]["dt_out_ms"])
            res[key].append(row)
    out["rb6_resolution"] = res

    # ---- RB3(a) ----
    cache = {}
    runs = []
    ir = df[(df.list == "S5") & (df["mode"] == "D") & (df.in_range == True)].sort_values(["path", "profile", "start_distance", "T_ramp_s"])  # noqa: E712
    for _, r in ir.iterrows():
        cfg, arr = load(records, r.run_id)
        key = json.dumps([cfg["path"], cfg["model"], cfg["durations"]], sort_keys=True, default=str)
        if key not in cache:
            cache[key] = a7.EE.path_gain(cfg, h)
        runs.append(rb_diag.rb3a_run(cfg, arr, r.to_dict(), thr, h, pred=cache[key]))
    out["rb3a"] = runs

    # ---- Radau ----
    sol = []
    sel = pd.concat([df[df.family == "S5ramp"], df[df.family == "rtol"], df[df.family == "radau"]]).sort_values(["solver", "rtol"])
    for _, r in sel.iterrows():
        cfg, arr = load(records, r.run_id)
        key = json.dumps([cfg["path"], cfg["model"], cfg["durations"]], sort_keys=True, default=str)
        if key not in cache:
            cache[key] = a7.EE.path_gain(cfg, h)
        sol.append(rb_diag.solver_run(cfg, arr, r.to_dict(), thr, h, pred=cache[key]))
    out["solvers"] = sol
    ref = next(x for x in sol if x["run_id"].startswith("S5ramp"))
    tau_ms = float(cfg["model"]["tau_ms"])
    out["solver_lags_vs_dop853_1e-10"] = {x["run_id"]: rb_diag.solver_pair_lags(ref, x, tau_ms) for x in sol if x is not ref}

    out_p = root / OUT_JSON
    out_p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    run = P.make_run_record(cfg0, env_info, name="RBDIAG_0000", status="ok", wall_time_s=time.time() - t0, inputs={TABLE: out["input_table_sha256"]},
                            outputs={"rb_diag_ms8.json": P.sha256_file(out_p)}, flags={"criteria_sha256": fi["criteria_sha256"]})
    P.write_run_record(run, out_p.parent / f"RBDIAG_0000_{C.short_hash(C.config_hash(cfg0))}.json")
    print(f"json {P.sha256_file(out_p)}\ngit.dirty={env_info['git']['dirty']} {time.time() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
