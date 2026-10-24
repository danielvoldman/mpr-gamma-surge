"""MS10 10b: candidate S8 map cells from stored records (DL-279). Reads stored map-1 / D31 records only; integrates nothing, chooses nothing.

  .venv/Scripts/python.exe scripts/inventory_ms10_10b.py [--out-dir results/ms10/10b]

Per map-1 cell (J0 = -21, T_ramp 120 s, P2, mode D, stored): class, onset, f_pk, A9 labels, Hopf frequency, eta_H, eta_start = eta_H - 1.5,
baseline mean rate (Hz, first 5 s) and mean v of the stored record, and the stored mode-N subgrid result (10 seeds, sigma 0.0624, T_ramp 120 s) where the cell is in the 15 x 15 subgrid, and the Euclidean distance (original map-1 cell units, node (i, j) at (i, j))
from the cell to the nearest D31 refined boundary half-edge midpoint (boundary definition of report_ms9_9h.py, UNVERIFIED reading ours).
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd

from mprsurge import config as C

ROOT = C.repo_root()


def load_9h():
    spec = importlib.util.spec_from_file_location("report_ms9_9h", ROOT / "scripts/report_ms9_9h.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def baseline(run_id: str, tau_ms: float = 10.0) -> tuple[float, float]:
    z = np.load(ROOT / "results/S7/S7_map1" / f"{run_id}.npz")
    k = z["t_ms"] <= 5000.0
    return float(z["r"][k].mean() * 1000.0 / tau_ms), float(z["v"][k].mean())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="results/ms10/10b")
    out = ROOT / ap.parse_args(argv).out_dir
    out.mkdir(parents=True, exist_ok=True)
    R = load_9h()
    m1 = pd.read_parquet(ROOT / "results/A9/a9_regime_map_v2.parquet")
    m1 = m1[m1["map"].astype(str).str.contains("1")].copy()
    coarse = {(int(r.i), int(r.j)): r["class"] for _, r in m1.iterrows()}
    d31 = pd.read_csv(ROOT / "results/ms9/9h/d31_classes.csv")
    fine = {(2 * i, 2 * j): c for (i, j), c in coarse.items()}
    fine.update({(int(r.p), int(r.q)): r["class"] for _, r in d31.iterrows()})
    fm = [R.mid(e) for e in R.edges(fine, 1)]
    cm = [R.mid(e) for e in R.edges({(2 * i, 2 * j): c for (i, j), c in coarse.items()}, 2)]
    sub = pd.read_csv(ROOT / "results/ms9/9f/subgrid_cells.csv").set_index(["i", "j"])
    rows = []
    for _, r in m1.iterrows():
        sg = sub.loc[(int(r.i), int(r.j))] if (int(r.i), int(r.j)) in sub.index else None
        pos = (float(r.i), float(r.j))
        b = baseline(r.run_id)
        rows.append({"i": int(r.i), "j": int(r.j), "Delta": r.Delta, "tau_d_ms": r.tau_d_ms, "class": r["class"], "onset_s": r.onset_s, "f_pk_hz": r.f_pk_hz,
                     "hopf_found": bool(r.hopf_found), "hopf_f_hz": r.hopf_f_hz, "eta_H": r.eta_H, "eta_start": r.eta_H - 1.5,
                     "inside_a4_region": r.inside_a4_region, "time_inside_s": r.time_inside_s, "labels": r.failure_labels_all, "struct_flags": r.struct_flags,
                     "base_rate_hz": b[0], "base_v": b[1], "dist_refined": min(R.dist(pos, f) for f in fm), "dist_coarse": min(R.dist(pos, c) for c in cm),
                     "subgrid_modeN_modal": None if sg is None else sg.modal, "subgrid_modeN_counts": None if sg is None else sg.counts,
                     "run_id": r.run_id})
    with open(out / "s8_candidates_all.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} cells, {len(fm)} refined half-edges, {len(cm)} coarse edges -> {out / 's8_candidates_all.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
