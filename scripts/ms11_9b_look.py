"""MS11 11g, POST HOC, EXPLORATORY, read only (DL-405 option (b), DL-406): the RB9(b) map-1 cells where two cycle-frequency estimators disagree on 'within 1/W'.

  .venv/Scripts/python.exe scripts/ms11_9b_look.py [--workers 6]

Reads stored map-1 records only. For each map-1 cell with a flagged episode (frozen classifier, onset to end) it computes the cycle frequency (a) from the unwrapped analytic phase
of the band-passed v between onset and end, over 2 pi, per second (the O5 description of the rules), and (b) from upward zero crossings of the band-passed v in the same window
(ms11_independent.cycle_frequency). It lists only the cells where the two estimators disagree on |f_pk - f_cycle| <= 1/W. Also the headline under both. No simulation, no gate, does not
re-run A11 or the independent check. Output: results/A11/post_hoc_9b_look/ms11_9b_map1_estimator_look.csv (labelled) and a summary json.
"""
import argparse
import csv
import json
import math
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy import signal

from mprsurge import config as C
from mprsurge.analysis import ms11_independent as I

ROOT = C.repo_root()
R = ROOT / "results"
LABEL = "POST HOC, EXPLORATORY, read only; feeds no gate (DL-405, DL-406)"


def hilbert_cycle_frequency(v, fs, t0, t1):
    z = signal.hilbert(I.bandpass(v, fs))
    ph = np.unwrap(np.angle(z))
    a, b = max(0, int(round(t0 * fs))), min(len(ph) - 1, int(round(t1 * fs)))
    return math.nan if b <= a else float((ph[b] - ph[a]) / (2 * np.pi) / ((b - a) / fs))


def one(path, thr):
    rec = I.load_record(path)
    c = I.classify(rec, thr)
    W = float(I.M.window_for_ramp(rec["T"])[0])
    out = {"cell": rec["name"], "has_episode": math.isfinite(c["onset"]), "fpk": c["fpk"], "W": W, "onset": c["onset"], "end": c["end"]}
    if out["has_episode"]:
        out["f_hilbert"] = hilbert_cycle_frequency(rec["v"], rec["fs"], c["onset"], c["end"])
        out["f_zc"], out["n_cross"] = I.cycle_frequency(rec["v"], rec["fs"], c["onset"], c["end"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    thr = I.frozen_thresholds()["threshold_abs"]
    base = {r["run"] for r in csv.DictReader(open(R / "ms9/9e/map1_classes.csv", newline="", encoding="utf-8"))}
    ps = [str(p) for p in I.json_files(R / "S7/S7_map1") if p.stem in base]
    hl = next(csv.DictReader(open(R / "ms9/9d/s5_headline_classes.csv", newline="", encoding="utf-8")))
    hp = str(R / "S5/ramp/S5ramp" / (hl["run"] + ".json"))
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(one, ps + [hp], [thr] * (len(ps) + 1), chunksize=4))
    head, cells = res[-1], [r for r in res[:-1] if r["has_episode"]]
    for r in cells + [head]:
        for k, f in (("hil", r["f_hilbert"]), ("zc", r["f_zc"])):
            r["d_" + k] = abs(r["fpk"] - f)
            r["margin_" + k] = r["d_" + k] - 1.0 / r["W"]          # <= 0 means within (inclusive)
            r["within_" + k] = (r["d_" + k] <= 1.0 / r["W"] + 1e-9)
    dis = [r for r in cells if r["within_hil"] != r["within_zc"]]
    out = ROOT / "results/A11/post_hoc_9b_look"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "ms11_9b_map1_estimator_look.csv", "w", newline="", encoding="utf-8") as f:
        f.write("# " + LABEL + "\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["cell", "f_pk_spectral_hz", "f_cycle_hilbert_hz", "f_cycle_zero_crossing_hz", "bound_1_over_W_hz", "diff_hilbert_hz", "diff_zc_hz", "margin_hilbert_hz", "margin_zc_hz", "within_hilbert", "within_zc"])
        for r in dis:
            w.writerow([r["cell"], r["fpk"], r["f_hilbert"], r["f_zc"], 1.0 / r["W"], r["d_hil"], r["d_zc"], r["margin_hil"], r["margin_zc"], r["within_hil"], r["within_zc"]])
    summ = {"label": LABEL, "n_with_episode": len(cells), "within_hilbert": sum(r["within_hil"] for r in cells), "within_zc": sum(r["within_zc"] for r in cells),
            "n_disagree": len(dis), "hilbert_in_zc_out": sum(r["within_hil"] and not r["within_zc"] for r in dis), "zc_in_hilbert_out": sum(r["within_zc"] and not r["within_hil"] for r in dis),
            "headline": {k: head[k] for k in ("cell", "fpk", "f_hilbert", "f_zc", "W", "d_hil", "d_zc", "within_hil", "within_zc")},
            "max_abs_estimator_difference_hz_all_cells": max(abs(r["f_hilbert"] - r["f_zc"]) for r in cells),
            "disagreeing_cells": [{k: r[k] for k in ("cell", "fpk", "f_hilbert", "f_zc", "margin_hil", "margin_zc")} for r in dis]}
    (out / "ms11_9b_map1_estimator_summary.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summ.items() if k != "disagreeing_cells"}, indent=1))
    for r in dis:
        print(f"{r['cell']}  f_pk {r['fpk']:.4f}  hil {r['f_hilbert']:.4f}  zc {r['f_zc']:.4f}  bound {1/r['W']:.4f}  margin_hil {r['margin_hil']:+.4f}  margin_zc {r['margin_zc']:+.4f}")


if __name__ == "__main__":
    main()
