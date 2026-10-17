"""7g driver (DL-148): entry-exit prediction, RB3(a) range and A4 grid-step evidence along P1, P2 and P5. No model is
integrated and no floor, grid step or ladder rung is chosen: floors, spacings and delta_0 are measurement grids.
Writes results/A4/a4_rb3a_range.csv (per path, profile, T_ramp, spacing, delta_0), results/A4/a4_rb3a_floor.csv (T_ramp
bound and the T_ramp values inside the range per floor candidate), results/A4/a4_rb3a_summary.json (grid test, noise map,
headline) and a run record in results/A4/rb3a. Quantities that use A_ref are labelled with the DL-138 reading (7h sign-off).
"""
import copy
import csv
import json
import sys

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a_ref as AR
from mprsurge.analysis import entry_exit as E
from mprsurge.units import tau_to_s

CONFIG = "configs/RB3a.yaml"
AREF_JSON = "results/A8/a_ref/a_ref.json"
PATHS = {"P1": "path_eta", "P2": "path_hypoxia", "P5": "path_updown"}
PROFILES = ("linear", "sigmoid")
T_RAMP_S = [float(x) for x in np.round(10 ** (np.arange(13) / 4.0), 10)]       # the 13 T_ramp values, 1 to 1000 s log
SPACINGS = (0.1, 0.05, 0.025, 0.0125, 0.00625)                                   # measurement grid; 0.025 = the working value
DELTA0 = (1e-9, 1e-6, 1e-3)                                                      # plan S13 ladder
FLOORS = tuple(10.0 ** -k for k in range(16, 2, -1))                             # 1e-16 ... 1e-3, a grid to read the bound from
HEADLINE = ("P2", "linear", 120.0)                                              # not on the 13-value list: run as an extra T_ramp
ALL_T = sorted(T_RAMP_S + [HEADLINE[2]])
H_WORK = 0.025
TAU_MS = 10.0


def sec(x):
    return None if x is None else tau_to_s(x, TAU_MS)


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    root = C.repo_root()
    cfg = C.resolve_config(CONFIG)
    out = root / cfg["output"]["dir"]
    out.mkdir(parents=True, exist_ok=True)
    env = P.environment_info(with_julia=False)
    a_ref = AR.load_a_ref(root / AREF_JSON)
    thr = 0.1 * a_ref
    rows, floor_rows = [], []
    for pk, pname in PATHS.items():
        for prof in PROFILES:
            for T in ALL_T:
                c = copy.deepcopy(cfg)
                c["path"].update(name=pname, profile=prof, T_ramp_s=T)
                for h in SPACINGS:
                    path, t, re, I = E.path_gain(c, h)
                    for d0 in DELTA0:
                        r = E.entry_exit(c, path, t, re, I, d0, thr, h)
                        rows.append({"path": pk, "profile": prof, "T_ramp_s": T, "h": h, "delta0": d0, "n_nodes": r["n_nodes"],
                                     "t_pred_s": sec(r["t_pred"]), "eta_on": r["eta_on"], "delay_eta": r["delay_eta"],
                                     "I_min": r["I_min"], "re_final": r["re_final"], "in_run": r["in_run"],
                                     "tol_step_s": sec(r["tol_step"]), "t_on_s": sec(r["t_on"])})
    write_csv(root / "results/A4/a4_rb3a_range.csv", rows)
    base = {(r["path"], r["profile"], r["T_ramp_s"], r["delta0"]): r for r in rows if r["h"] == H_WORK}
    for pk in PATHS:
        for prof in PROFILES:
            for d0 in DELTA0:
                for fl in FLOORS:
                    ins, tmax = [], []
                    for T in T_RAMP_S:
                        r = base[(pk, prof, T, d0)]
                        if r["t_pred_s"] is not None and E.inside_range(d0, r["I_min"], fl):
                            ins.append(T)
                        if r["t_pred_s"] is not None:
                            tmax.append(E.t_ramp_max(T, r["I_min"], d0, fl))
                    floor_rows.append({"path": pk, "profile": prof, "delta0": d0, "floor": fl, "n_inside_of_13": len(ins),
                                       "T_inside_s": " ".join(f"{x:.4g}" for x in ins),
                                       "T_max_s_min": min(tmax) if tmax else None, "T_max_s_max": max(tmax) if tmax else None})
    write_csv(root / "results/A4/a4_rb3a_floor.csv", floor_rows)
    # grid halving: |t_pred(h) - t_pred(h/2)| in units of the time of one step h at t_pred
    grid = []
    for key in sorted({(r["path"], r["profile"], r["T_ramp_s"], r["delta0"]) for r in rows}):
        by = {r["h"]: r for r in rows if (r["path"], r["profile"], r["T_ramp_s"], r["delta0"]) == key}
        for h, h2 in zip(SPACINGS[:-1], SPACINGS[1:]):
            a, b = by[h], by[h2]
            if a["t_pred_s"] is None or b["t_pred_s"] is None:
                continue
            dt = abs(a["t_pred_s"] - b["t_pred_s"])
            grid.append({"h": h, "dt_s": dt, "ratio": None if a["tol_step_s"] is None else dt / a["tol_step_s"]})
    ratios = {h: [g["ratio"] for g in grid if g["h"] == h and g["ratio"] is not None] for h in SPACINGS[:-1]}
    m = cfg["model"]
    tau_d_tau = m["tau_d_ms"] / m["tau_ms"]
    e0, eH = cfg["path"]["eta_start"], cfg["path"]["eta_H"]
    noise = [{"eta": e, "label": lab, "std_v_over_sigma": E.stationary_std_v(e, m["J"], m["Delta"], tau_d_tau)}
             for lab, e in (("start", e0), ("eta_H-1", eH - 1.0), ("eta_H-0.5", eH - 0.5), ("eta_H-0.25", eH - 0.25),
                            ("eta_H-0.1", eH - 0.1))]
    hl = base[(HEADLINE[0], HEADLINE[1], HEADLINE[2], 1e-6)]
    summ = {"label": "evidence only: no floor value, grid step or ladder rung is chosen (DL-148); A_ref reading (a) of DL-138/DL-139 "
                     "is for 7h sign-off; the A4 spacing 0.025 is the working value, UNVERIFIED",
            "a_ref": a_ref, "threshold": thr, "h_working": H_WORK, "spacings": list(SPACINGS), "delta0": list(DELTA0),
            "floors_grid": list(FLOORS), "T_ramp_s": T_RAMP_S, "T_ramp_extra_s": [HEADLINE[2]], "headline": {"case": list(HEADLINE), "delta0": 1e-6, **hl},
            "grid_halving_ratio_max_by_h": {str(h): (max(v) if v else None) for h, v in ratios.items()},
            "grid_halving_ratio_median_by_h": {str(h): (float(np.median(v)) if v else None) for h, v in ratios.items()},
            "grid_halving_ratio_n_by_h": {str(h): len(v) for h, v in ratios.items()},
            "stationary_std_v_over_sigma": noise}
    P.atomic_write_json(root / "results/A4/a4_rb3a_summary.json", summ)
    outputs = {n: P.sha256_file(root / "results/A4" / n) for n in ("a4_rb3a_range.csv", "a4_rb3a_floor.csv", "a4_rb3a_summary.json")}
    run = P.make_run_record(cfg, env, name="RB3A_0000", status="ok", inputs={AREF_JSON: P.sha256_file(root / AREF_JSON)},
                            outputs=outputs, flags={"n_range_rows": len(rows), "n_floor_rows": len(floor_rows)})
    P.write_run_record(run, out / f"RB3A_0000_{C.short_hash(C.config_hash(cfg))}.json")
    print(f"{len(rows)} range rows, {len(floor_rows)} floor rows, git.dirty={env['git']['dirty']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
