"""7f driver (DL-144): baseline rho report and the O4 noise-envelope measurement on the 7e baseline-only records.
Reads results/S5/baseline (bundles, cell_list.json) and results/A8/a_ref/a_ref.json; writes results/A8/baseline/
a8_baseline_rho.csv (per cell and seed), a8_noise_envelope.csv (per cell and seed), a8_baseline_summary.json and a run
record. No model is integrated, no class is assigned, the D8 call is not used. No pass/fail number is applied.
"""
import csv
import json
import sys

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a_ref as AR
from mprsurge.analysis import baseline_report as B

CONFIG = "configs/A8.yaml"
IN_DIR = "results/S5/baseline"
AREF_JSON = "results/A8/a_ref/a_ref.json"
FS = 1000.0
ENV_KEYS = ("env_max", "env_q99", "env_median", "frac_above", "any_above", "longest_run_cycles")


def split_of(c):
    return {"stable_focus": "stable focus", "stable_node": "stable node"}[c["start"]["type"]]


def q(x, ps=(0, 5, 25, 50, 75, 95, 100)):
    return {f"p{p}": float(np.percentile(x, p)) for p in ps}


def rho_summary(rows):
    r = np.array([x["rho"] for x in rows])
    cells = {}
    for x in rows:
        cells.setdefault(x["index"], []).append(x["rho"])
    cm = np.array([np.mean(v) for v in cells.values()])
    cmax = np.array([np.max(v) for v in cells.values()])
    return {"n_records": int(r.size), "n_cells": len(cells), "rho_quantiles": q(r),
            "records_rho_ge_0.5": int((r >= B.RHO_LEVEL).sum()), "frac_records_rho_ge_0.5": float((r >= B.RHO_LEVEL).mean()),
            "cells_mean_rho_ge_0.5": int((cm >= B.RHO_LEVEL).sum()), "cells_any_seed_rho_ge_0.5": int((cmax >= B.RHO_LEVEL).sum()),
            "frac_cells_mean_rho_ge_0.5": float((cm >= B.RHO_LEVEL).mean())}


def env_summary(rows, tag):
    a = [x[tag] for x in rows]
    return {"n_records": len(a), "records_any_above": int(sum(x["any_above"] for x in a)),
            "records_ge_10_cycles_above": int(sum(x["longest_run_cycles"] >= 10 for x in a)),
            "mean_frac_samples_above": float(np.mean([x["frac_above"] for x in a])),
            "env_max_quantiles": q([x["env_max"] for x in a]), "env_q99_quantiles": q([x["env_q99"] for x in a]),
            "env_median_quantiles": q([x["env_median"] for x in a]),
            "longest_run_cycles_max": float(max(x["longest_run_cycles"] for x in a))}


def main() -> int:
    root = C.repo_root()
    cfg = C.resolve_config(CONFIG)
    out = root / cfg["output"]["dir"]
    out.mkdir(parents=True, exist_ok=True)
    env = P.environment_info(with_julia=False)
    doc = json.loads((root / IN_DIR / "cell_list.json").read_text(encoding="utf-8"))
    a_ref = AR.load_a_ref(root / AREF_JSON)
    thr = AR.threshold_abs(a_ref)
    rho_rows, env_rows = [], []
    for c in doc["cells"]:
        z = np.load(root / IN_DIR / f"S5base_{c['index']:04d}_{c['hash12']}.npz")
        for s in range(z["v"].shape[0]):
            v = z["v"][s]
            base = {"index": c["index"], "name": c["name"], "kind": c["kind"], "start_type": split_of(c),
                    "tau_d_ms": c["tau_d_ms"], "Delta": c["Delta"], "J0": c["J0"], "T_ramp_s": c["T_ramp_s"], "seed": s}
            rho_rows.append({**base, **B.rho_row(v, FS, c["T_ramp_s"], t_end=(v.size - 1) / FS)})
            env_rows.append({**base, **B.noise_env_row(v, FS, thr)})
    cols = ["index", "name", "kind", "start_type", "tau_d_ms", "Delta", "J0", "T_ramp_s", "seed", "W_s", "n_windows", "rho",
            "P_G", "P_nonG", "v_std"]
    with open(out / "a8_baseline_rho.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows({k: r[k] for k in cols} for r in rho_rows)
    head = ["index", "name", "kind", "start_type", "seed"]
    with open(out / "a8_noise_envelope.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(head + [f"{t}_{k}" for t in ("all", "trim") for k in ENV_KEYS])
        for r in env_rows:
            w.writerow([r[k] for k in head] + [r[t][k] for t in ("all", "trim") for k in ENV_KEYS])
    groups = {"all": lambda r: True, "stable focus": lambda r: r["start_type"] == "stable focus",
              "stable node": lambda r: r["start_type"] == "stable node", "headline": lambda r: r["kind"] == "headline",
              "map1": lambda r: r["kind"] == "map1", "map2": lambda r: r["kind"] == "map2"}
    summ = {"label_rho": "reporting split only (start type); no class, flag or criterion; rho is the mean over windows (O7), "
                         "window W from the cell's own T_ramp (D4), UNVERIFIED reading",
            "label_env": "O4 measurement, UNVERIFIED; threshold = 0.1 x A_ref, A_ref from results/A8/a_ref (DL-139); D8 not used",
            "a_ref": a_ref, "threshold": thr, "sigma_used": 0.0624,
            "rho": {g: rho_summary([r for r in rho_rows if f(r)]) for g, f in groups.items()},
            "noise_envelope": {g: {t: env_summary([r for r in env_rows if f(r)], t) for t in ("all", "trim")}
                               for g, f in groups.items()},
            "rho_by_W": {str(W): rho_summary([r for r in rho_rows if r["W_s"] == W]) for W in sorted({r["W_s"] for r in rho_rows})}}
    P.atomic_write_json(out / "a8_baseline_summary.json", summ)
    inputs = {f"{IN_DIR}/cell_list.json": P.sha256_file(root / IN_DIR / "cell_list.json"),
              AREF_JSON: P.sha256_file(root / AREF_JSON)}
    outputs = {n: P.sha256_file(out / n) for n in ("a8_baseline_rho.csv", "a8_noise_envelope.csv", "a8_baseline_summary.json")}
    run = P.make_run_record(cfg, env, name="A8base_0000", status="ok", inputs=inputs, outputs=outputs,
                            flags={"n_records": len(rho_rows), "threshold": thr})
    P.write_run_record(run, out / f"A8base_0000_{C.short_hash(C.config_hash(cfg))}.json")
    print(f"{len(rho_rows)} records, threshold {thr:.6f}, git.dirty={env['git']['dirty']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
