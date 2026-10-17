"""7f sensitivity driver (DL-146): A8 sensitivity on synthetic signals, the stored S3 / S4 mode-D records, the 7e
baseline-only records (class-free measurements) and seeded white noise at the real window sizes; the reachability table
from the stored 7f baseline rho; results/A8/a8_aref.json from the stored A_ref file. No model is integrated and no
pass/fail number is applied. Every class that used the D8 call is provisional (D8 open, DL-137).
Writes results/A8/a8_sensitivity.csv and a8_aref.json; results/A8/sensitivity/{a8_sens_baseline_records.csv,
a8_reachability.csv, a8_whitenoise.csv, a8_sens_summary.json} and a run record.
"""
import csv
import glob
import json
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a8_sensitivity as S
from mprsurge.analysis import a_ref as AR
from mprsurge.analysis import baseline_report as B
from mprsurge.analysis import surge_metrics as M

CONFIG = "configs/A8_sensitivity.yaml"
IN_DIR = "results/S5/baseline"
AREF_JSON = "results/A8/a_ref/a_ref.json"
RHO_CSV = "results/A8/baseline/a8_baseline_rho.csv"
ENV_COMBOS = {"V0": ((25.0, 100.0), 0.1), "amin_0.05": ((25.0, 100.0), 0.05), "amin_0.2": ((25.0, 100.0), 0.2),
              "band_30_120": ((30.0, 120.0), 0.1)}
RHO_COMBOS = {"rho_V0": (S.DEFAULT["band"], 1.0), "rho_band_30_120": ((30.0, 120.0), 1.0),
              "rho_window_x0.5": (S.DEFAULT["band"], 0.5), "rho_window_x2": (S.DEFAULT["band"], 2.0)}
CLASS_COLS = ["dataset", "record", "mode", "T_ramp_s", "variant", "cls", "provisional", "d8_called", "d8_damped", "d8_rate",
              "d8_se", "f_pk_hz", "window_s", "note"]
A_REF = None


def _init(a_ref):
    global A_REF
    A_REF = a_ref


def cell_task(c):
    z = np.load(f"{IN_DIR}/S5base_{c['index']:04d}_{c['hash12']}.npz")
    rows = []
    for s in range(z["v"].shape[0]):
        v = z["v"][s]
        r = {"index": c["index"], "kind": c["kind"], "seed": s, "T_ramp_s": c["T_ramp_s"]}
        for tag, (band, wmul) in RHO_COMBOS.items():
            q = S.rho_variant(v, c["T_ramp_s"], band, wmul)
            r[tag], r["W_" + tag[4:]] = q["rho"], q["W_s"]
        for tag, (band, f) in ENV_COMBOS.items():
            e = B.noise_env_row(v, S.FS, f * A_REF, band=band)
            for t in ("all", "trim"):
                r[f"env_{tag}_{t}_any"] = e[t]["any_above"]
                r[f"env_{tag}_{t}_cycles"] = e[t]["longest_run_cycles"]
        rows.append(r)
    return rows


def white_task(args):
    T, variant, n, sd = args
    return args[:2], S.whitenoise_classes(T, variant, A_REF, n, sd)


def classify_rows(a_ref):
    rows = []

    def add(dataset, record, mode, v, t_on, T):
        for var in S.VARIANTS:
            rows.append({"dataset": dataset, "record": record, "mode": mode, "T_ramp_s": T, "variant": var,
                         **S.classify(v, mode, t_on, T, a_ref, var)})

    for cid, mode, v, t_on, Ts in S.synthetic_cases():
        for T in Ts:
            add("synthetic", cid, mode, v, t_on, T)
    for f in sorted(glob.glob("results/S3/devalle/devalle_000?_*.npz") + glob.glob("results/S3/ceni/ceni_000?_*.npz")):
        v = np.load(f)["v"][S.S3_SLICE[0]:S.S3_SLICE[1]]
        add("stored_S3", f.replace("\\", "/").split("/")[-1][:-4], "D", v, S.S3_T_ON, 120.0)
    for tag in ("devalle", "ceni"):
        z = np.load(glob.glob(f"results/S4/{tag}/{tag}_0000_*.npz")[0])
        for k, eta, v in S.s4_segments(z):
            add(f"stored_S4_{tag}", f"step{k:03d}_eta{eta:.4f}", "D", v, S.S4_T_ON, 120.0)
    return rows


def change_table(rows):
    base = {(r["dataset"], r["record"], r["T_ramp_s"]): r["cls"] for r in rows if r["variant"] == "V0"}
    out = {}
    for r in rows:
        if r["variant"] == "V0":
            continue
        g = out.setdefault((r["dataset"], r["mode"], r["variant"]), {"n": 0, "changed": 0, "not_run": 0, "transitions": {}})
        g["n"] += 1
        b = base[(r["dataset"], r["record"], r["T_ramp_s"])]
        if r["cls"] == "not_run":
            g["not_run"] += 1
        elif r["cls"] != b:
            g["changed"] += 1
            k = f"{b}->{r['cls']}"
            g["transitions"][k] = g["transitions"].get(k, 0) + 1
    return [{"dataset": k[0], "mode": k[1], "variant": k[2], **v} for k, v in sorted(out.items())]


def write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def aref_file(root):
    st = json.loads((root / AREF_JSON).read_text(encoding="utf-8"))
    alt = st["alternates"]
    return {"status": "UNVERIFIED reading, owner-ruled (DL-138, DL-139); this file restates the stored A_ref file, nothing is recomputed",
            "source_file": AREF_JSON, "source_sha256": P.sha256_file(root / AREF_JSON),
            "chosen": {"reading": "(a) median of the band-passed Hilbert envelope over whole cycles", "A_ref": st["value"],
                       "threshold_abs_0.1_x_A_ref": st["threshold_abs"]},
            "f1_numbers": {"(a) median envelope (chosen)": st["value"], "(b) half peak-to-peak": alt["half_ptp"]["value"],
                           "(c) literal peak-to-peak (A5 value)": alt["literal_ptp_a5"]["value"]},
            "other_alternates_stored": {k: alt[k]["value"] for k in ("mean", "max", "sqrt2_rms")},
            "note": "A_ref reading as a sensitivity item is not in the plan's A8 list or in DL-136 D-3; listed for 7h, not run"}


def main() -> int:
    root = C.repo_root()
    cfg = C.resolve_config(CONFIG)
    out = root / cfg["output"]["dir"]
    out.mkdir(parents=True, exist_ok=True)
    env = P.environment_info(with_julia=False)
    a_ref = AR.load_a_ref(root / AREF_JSON)
    wk = cfg["white"]
    P.atomic_write_json(root / "results/A8/a8_aref.json", aref_file(root))
    rows = classify_rows(a_ref)
    write_csv(root / "results/A8/a8_sensitivity.csv", rows, CLASS_COLS)
    doc = json.loads((root / IN_DIR / "cell_list.json").read_text(encoding="utf-8"))
    Ts = [float(x) for x in np.round(10 ** (np.arange(13) / 4.0), 10)]       # the S2 / map-2 T_ramp list
    Wd = {}
    for T in Ts:
        Wd.setdefault(M.window_for_ramp(T)[0], []).append(T)
    jobs = [(Tl[0], var, wk["n_draws"], wk["sd"]) for Tl in Wd.values() for var in S.VARIANTS]
    with ProcessPoolExecutor(cfg["run"]["workers"], initializer=_init, initargs=(a_ref,)) as ex:
        recs = [r for part in ex.map(cell_task, doc["cells"], chunksize=8) for r in part]
        white = dict(ex.map(white_task, jobs))
    write_csv(out / "a8_sens_baseline_records.csv", recs, list(recs[0]))
    rho_rows = []
    with open(root / RHO_CSV, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rho_rows.append({"index": int(r["index"]), "W_s": round(float(r["W_s"]), 9), "rho": float(r["rho"])})
    reach = S.reach_table(rho_rows)
    write_csv(out / "a8_reachability.csv", reach, list(reach[0]))
    wrows = []
    for W, Tl in Wd.items():
        for var in S.VARIANTS:
            cnt = white[(Tl[0], var)]
            for cls in M.MODE_N_CLASSES + (M.FAILED, "not_run"):
                wrows.append({"W_s": W, "T_ramp_s": " ".join(f"{x:.4g}" for x in Tl), "variant": var, "class": cls,
                              "count": cnt.get(cls, 0), "denominator": wk["n_draws"]})
    write_csv(out / "a8_whitenoise.csv", wrows, list(wrows[0]))
    summ = {"label": "report only, no pass/fail number; classes that used the D8 call are provisional (D8 open, DL-137)",
            "a_ref": a_ref, "n_class_rows": len(rows), "changes_vs_V0": change_table(rows),
            "n_baseline_records": len(recs), "reachability_levels": list(S.LEVELS), "white": wk,
            "white_windows": {str(W): Tl for W, Tl in Wd.items()}}
    P.atomic_write_json(out / "a8_sens_summary.json", summ)
    outputs = {n: P.sha256_file(out / n) for n in ("a8_sens_baseline_records.csv", "a8_reachability.csv", "a8_whitenoise.csv",
                                                   "a8_sens_summary.json")}
    outputs["a8_sensitivity.csv"] = P.sha256_file(root / "results/A8/a8_sensitivity.csv")
    outputs["a8_aref.json"] = P.sha256_file(root / "results/A8/a8_aref.json")
    inputs = {f"{IN_DIR}/cell_list.json": P.sha256_file(root / IN_DIR / "cell_list.json"), AREF_JSON: P.sha256_file(root / AREF_JSON),
              RHO_CSV: P.sha256_file(root / RHO_CSV)}
    run = P.make_run_record(cfg, env, name="A8sens_0000", status="ok", inputs=inputs, outputs=outputs,
                            flags={"n_class_rows": len(rows), "n_baseline_records": len(recs)})
    P.write_run_record(run, out / f"A8sens_0000_{C.short_hash(C.config_hash(cfg))}.json")
    print(f"{len(rows)} class rows, {len(recs)} baseline records, git.dirty={env['git']['dirty']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
