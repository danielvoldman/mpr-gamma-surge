"""MS4 step 4e: A3 check, fold cross-check (DL-108) and G1 metric with a shifted-window sensitivity.
Analysis only: reads results/A3/a3_sn_ramp.parquet, the stored S2 series and results/A1; integrates
nothing. Writes results/A3/a3_4e_check.csv (git-ignored) and prints the numbers for DL-110.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from mprsurge import config as C
from mprsurge.analysis import bifurcation as B
from mprsurge.analysis import sn_ramp as SN

ROOT = C.repo_root()
A3 = ROOT / "results" / "A3"
A1 = ROOT / "results" / "A1" / "a1_fixedpoints_2d.npz"
SHIFTS_MS = (2, 5, 10)      # window-start shifts after the jump sample (information only, DL-109 (c))
J, DELTA = 15.0, 1.0


def fold_cross_check():
    d = np.load(A1, allow_pickle=True)
    e, Jg, n = d["eta_over_Delta"], d["J_over_sqrtDelta"], d["n_roots"]
    j = int(np.argmin(abs(Jg - J)))
    col = n[:, j]
    edges = [(e[i], e[i + 1]) for i in np.flatnonzero(np.diff(col))]
    fe, fJ = d["eta_fine"], d["J_fine"]
    jj = int(np.argmin(abs(fJ - J)))
    s = d["refined_je"] == jj
    ie, nr = d["refined_ie"][s], d["refined_n_roots"][s]
    o = np.argsort(ie)
    ie, nr = ie[o], nr[o]
    fine = [(fe[ie[k]], fe[ie[k + 1]]) for k in np.flatnonzero((np.diff(nr) != 0) & (np.diff(ie) == 1))]
    formula = sorted(B.fold_etas(J, DELTA))
    rows = []
    for f, (a, b) in zip(formula, edges):
        rows.append({"fold_formula": f, "base_edge_lo": a, "base_edge_hi": b,
                     "inside_cell": a - 1e-9 <= f <= b + 1e-9,
                     "dist_to_nearer_edge": min(abs(f - a), abs(f - b)),
                     "dist_to_far_edge": max(abs(f - a), abs(f - b))})
    return pd.DataFrame(rows), fine, float(e[1] - e[0]), float(fe[1] - fe[0])


def main() -> int:
    pd.set_option("display.width", 250)
    df = pd.read_parquet(A3 / "a3_sn_ramp.parquet").sort_values("T_ramp_s").reset_index(drop=True)
    off = df["offset"].to_numpy()
    # 1. A3 check
    slow = df.iloc[-1]
    print(f"A3: slowest T_ramp {slow.T_ramp_s:g} s, eta_jump {slow.eta_jump:.6f}, fold {slow.fold_eta:.6f}, "
          f"offset {slow.offset:.6f} = {slow.offset/0.05:.4f} step(0.05) = {slow.offset/0.025:.4f} step(0.025)")
    print(f"  within 0.05: {abs(slow.offset) <= 0.05}   within 0.025 (info): {abs(slow.offset) <= 0.025}")
    print("  offsets:", np.array2string(off, precision=5))
    print("  strictly monotone falling with slower ramp:", bool(np.all(np.diff(off) < 0)))
    # 2. fold cross-check
    cc, fine, cell, fcell = fold_cross_check()
    print(cc.to_string())
    print("fine-lattice edges:", fine, "cell", cell, "fine cell", fcell)
    # 4. G1 table and sensitivity
    rows = []
    for _, r in df.iterrows():
        rec = json.loads((A3 / "S2" / f"{r.run}.json").read_text(encoding="utf-8"))
        d = np.load(A3 / "S2" / f"{r.run}.npz")
        t_s = d["t_ms"] * 1e-3
        j = SN.detect_jump(t_s, d["r"], d["eta"])
        row = {"T_ramp_s": r.T_ramp_s, "rate": r.rate, "se": r.se, "cycles": r.cycles_fit,
               "n": r.n_fit, "cls": r.ring_class}
        for sh in SHIFTS_MS:
            i0 = j["index"] + int(round(sh * 1e-3 * SN._fs(t_s)))
            g = SN.ring_growth(t_s, d["v"], i0, (25.0, 100.0), 10)
            row[f"rate_{sh}"], row[f"se_{sh}"] = g["rate"], g["se"]
            row[f"cyc_{sh}"] = g["cycles"]
            row[f"cls_{sh}"] = SN.classify_ring(g["rate"], g["se"])
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(A3 / "a3_4e_check.csv", index=False)
    print(out.round(3).to_string())
    for sh in SHIFTS_MS:
        same_sign = bool(np.all(np.sign(out[f"rate_{sh}"]) == np.sign(out["rate"])))
        same_cls = bool((out[f"cls_{sh}"] == out["cls"]).all())
        print(f"shift {sh} ms: sign agrees {same_sign}, damped call agrees {same_cls}, "
              f"rate range {out[f'rate_{sh}'].min():.2f} to {out[f'rate_{sh}'].max():.2f}, "
              f"max rate/SE {np.max(out[f'rate_{sh}']/out[f'se_{sh}']):.1f}, "
              f"cycles {out[f'cyc_{sh}'].min():.2f} to {out[f'cyc_{sh}'].max():.2f}")
    print("base: rate/SE range", (out.rate / out.se).min(), (out.rate / out.se).max(),
          "cycles", out.cycles.min(), out.cycles.max(), "classes", out.cls.unique())
    return 0


if __name__ == "__main__":
    sys.exit(main())
