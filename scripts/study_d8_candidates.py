"""7g2 driver (DL-153, inserted by owner ruling): candidate fixes for the D8 estimator, synthetic data and stored records only.

Runs analysis.d8_study over the families F1 to F6 for all 54 candidates of analysis.d8_candidates and writes
results/A8/d8_cand/{d8cand.json, d8cand_summary.csv, d8cand_cells.csv, d8cand_lc.csv, d8cand_a8.csv,
d8cand_whitenoise.csv} and a run record. The plan estimator stays the default; nothing in surge_metrics is changed.
No model is integrated; the stored S3 record and a_ref.json are read.
"""
import csv
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from itertools import product

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a8_sensitivity as S8
from mprsurge.analysis import a_ref as AR
from mprsurge.analysis import d8_candidates as DC
from mprsurge.analysis import d8_study as D
from mprsurge.analysis import estimator_study as E
from mprsurge.analysis import surge_metrics as M

CONFIG = "configs/d8_cand.yaml"
N_DRAW = 200                                   # DL-136
F1_KEY = (7, 2)                                # the 7b stream: the plan estimator reproduces DL-137
S3_LC = "results/S3/devalle/devalle_0000_9e49def91dfc.npz"
A_REF_JSON = "results/A8/a_ref/a_ref.json"
CANDS = DC.all_candidates()
BY_ID = {c.id: c for c in CANDS}


def seqs(root, key, n):
    return np.random.SeedSequence(root, spawn_key=tuple(key)).spawn(n)


def cell_task(args):
    cell, seq, n = args
    return D.run_family([cell], [seq], n, CANDS)


def white_task(args):
    cid, sd, T, a_ref, n = args
    return (cid, sd, T), D.white_counts(BY_ID[cid], T, sd, a_ref, n)


def run_cells(ex, cells, sq, n=N_DRAW):
    out = {c.id: [] for c in CANDS}
    for part in ex.map(cell_task, [(c, q, n) for c, q in zip(cells, sq)]):
        for cid, rows in part.items():
            out[cid].extend(rows)
    return out


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="timing sample: 4 cells x 10 draws of F1, no outputs")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    root = C.repo_root()
    cfg = C.resolve_config(CONFIG)
    out_dir = root / (args.out_dir or cfg["output"]["dir"])
    env = P.environment_info(with_julia=False)
    t0 = time.perf_counter()
    rs = cfg["seeds"]["root_seed"]
    a_ref = AR.load_a_ref(root / A_REF_JSON)
    thr_abs = AR.threshold_abs(a_ref)
    workers = cfg["run"]["workers"]
    if args.sample:
        cells = E.scenarios()[8:12]
        with ProcessPoolExecutor(max_workers=1) as ex:
            run_cells(ex, cells, seqs(rs, F1_KEY, 57)[8:12], n=10)
        print(f"sample wall {time.perf_counter() - t0:.2f} s")
        return 0
    out_dir.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        # F1: the 7b scenarios, unchanged (DL-136 table)
        f1_cells = E.scenarios()
        f1 = run_cells(ex, f1_cells, seqs(rs, F1_KEY, len(f1_cells)))
        # F2: gradual onset
        f2_cells = D.f2_cells()
        f2 = run_cells(ex, f2_cells, seqs(rs, (7, 8, 2), len(f2_cells)))
    # F3: finding 1 (quiet start, nonzero end); F5 rings; draws
    f3 = D.zero_family(D.f3_signal, thr_abs, N_DRAW, np.random.SeedSequence(rs, spawn_key=(7, 8, 3)), CANDS, v_from=int(D.F3_T_ON * D.FS))
    f5a = D.zero_family(D.f5_ring5, E.THR, N_DRAW, np.random.SeedSequence(rs, spawn_key=(7, 8, 5, 1)), CANDS)
    f5b = D.zero_family(D.f5_ring15, E.THR, N_DRAW, np.random.SeedSequence(rs, spawn_key=(7, 8, 5, 2)), CANDS)
    # F4: stored limit cycle
    lc = np.load(root / S3_LC)["v"]
    f4 = D.lc_calls(lc, thr_abs, CANDS, sorted(set(D.LC_T_ON) | set(float(t) for t in D.LC_T_ON_GRID)))
    # F5 (c): class-level A8 ring cases
    cases = {c[0]: c for c in S8.synthetic_cases() if c[0] in D.A8_RING_CASES}
    f5c = {}
    for c in CANDS:
        d8 = M.PLAN_D8 if c.is_plan else DC.CandidateD8(c)
        for name, (_, mode, v, t_on, Ts) in cases.items():
            for T in Ts:
                f5c[(c.id, name, T)] = S8.classify(v, mode, t_on, T, a_ref, "V0", d8=d8)["cls"]
    # F6: white noise at the real window sizes, class level (all 54 candidates)
    jobs = [(c.id, sd, T, a_ref, D.WHITE_DRAWS) for c, sd, T in product(CANDS, D.WHITE_SD, D.WHITE_T_RAMP)]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        f6 = dict(ex.map(white_task, jobs, chunksize=8))

    # ---- summaries -------------------------------------------------------------------------------------------------
    summ, cell_rows, lc_rows, a8_rows = [], [], [], []
    for c in CANDS:
        cid = c.id
        v1, v2 = D.family_verdict(f1[cid]), D.family_verdict(f2[cid])
        v2_by_ramp = {rp: D.family_verdict([r for r in f2[cid] if r["ramp"] == rp]) for rp in D.RAMP_S}
        fd3 = D.damped_fraction(*f3[cid])
        lc_damped = {t: f4[cid][t][0] for t in D.LC_T_ON}
        grid_damped = sum(f4[cid][float(t)][0] for t in D.LC_T_ON_GRID)
        r5a, s5a = f5a[cid]
        r5b, s5b = f5b[cid]
        a_neg = float(np.mean(r5a < 0))
        a_dmp = D.damped_fraction(r5a, s5a)
        b_dmp = D.damped_fraction(r5b, s5b)
        b_10 = float(np.mean(np.abs(r5b + D.LAM15) <= 0.1 * D.LAM15))
        a8_items = {"ring5_growth_negative": a_neg >= E.MATCH_MIN, "ring15_damped": b_dmp >= E.MATCH_MIN}
        for (cc, name, T), cls in f5c.items():
            if cc == cid:
                a8_items[f"{name}@T{T:g}"] = cls in ("NS", "D-none")
        rec = {"candidate": cid, "edge": c.edge, "shift": c.shift, "minwin": c.minwin, "se": c.se,
               "f1_i_met": v1["i_met"], "f1_i_fail_n": v1["i_fail_n"], "f1_i_cells": v1["i_cells"],
               "f1_ii_met": v1["ii_met"], "f1_ii_fail_n": v1["ii_fail_n"], "f1_ii_cells": v1["ii_cells"],
               "f1_ii_max_false_damped": v1["ii_max_false_damped"], "f1_false_non_damped_mean": v1["false_non_damped_mean"],
               "f1_inflation_k_max": v1["inflation_k_max"], "f1_acceptance_met": bool(v1["i_met"] and v1["ii_met"]),
               "f2_i_fail_n": v2["i_fail_n"], "f2_ii_fail_n": v2["ii_fail_n"], "f2_cells": v2["i_cells"] + v2["ii_cells"],
               "f2_ramp0.1_i_fail_n": v2_by_ramp[0.1]["i_fail_n"], "f2_ramp0.1_ii_fail_n": v2_by_ramp[0.1]["ii_fail_n"],
               "f2_ramp0.5_i_fail_n": v2_by_ramp[0.5]["i_fail_n"], "f2_ramp0.5_ii_fail_n": v2_by_ramp[0.5]["ii_fail_n"],
               "f3_frac_damped": fd3, "f3_met": fd3 <= E.FALSE_DAMPED_MAX,
               "lc_damped_t0": lc_damped[0.0], "lc_damped_t1": lc_damped[1.0], "lc_damped_t3": lc_damped[3.0],
               "lc_grid_damped_of_17": grid_damped,
               "a8_ring5_frac_growth_negative": a_neg, "a8_ring5_frac_damped": a_dmp, "a8_ring15_frac_damped": b_dmp,
               "a8_ring15_frac_rate_within_10pct": b_10, "a8_items_failed": sum(not ok for ok in a8_items.values()),
               "a8_items": json.dumps(a8_items)}
        rec["f1_fail"] = v1["i_fail_n"] + v1["ii_fail_n"]
        rec["lc_fail"] = sum(lc_damped.values())
        rec["f3_fail"] = int(fd3 > E.FALSE_DAMPED_MAX)
        rec["a8_fail"] = rec["a8_items_failed"]
        rec["f2_fail"] = v2["i_fail_n"] + v2["ii_fail_n"]
        rec["f1_abs_bias"] = D.mean_abs_bias(f1[cid])
        summ.append(rec)
        for fam, rows in (("F1", f1[cid]), ("F2", f2[cid])):
            for r in rows:
                cell_rows.append({"candidate": cid, "family": fam, **r})
        for t, (dmp, rate, se) in f4[cid].items():
            lc_rows.append({"candidate": cid, "t_on_s": t, "damped": dmp, "rate": rate, "se": se})
        for k, ok in a8_items.items():
            a8_rows.append({"candidate": cid, "item": k, "pass": ok})
    order = sorted(range(len(summ)), key=lambda i: D.rank_key(summ[i]))
    for rank, i in enumerate(order, 1):
        summ[i]["rank"] = rank
    wrows = []
    for (cid, sd, T), res in f6.items():
        W, _ = M.window_for_ramp(T)
        cnt = res["counts"]
        wrows.append({"candidate": cid, "sd": sd, "T_ramp": T, "W_s": round(W, 3), "n": res["n"],
                      "non_NS": res["n"] - cnt.get("NS", 0), **{f"n_{k}": cnt.get(k, 0) for k in (*M.MODE_N_CLASSES, "failed")},
                      "d8_called": res["d8_called"], "d8_damped": res["d8_damped"]})
    wall = time.perf_counter() - t0
    top = [summ[i] for i in order[:10]]
    plan = next(r for r in summ if r["candidate"] == DC.PLAN.id)
    summary = {"n_draw": N_DRAW, "a_ref": a_ref, "threshold_abs": thr_abs, "plan": plan, "top10": top,
               "n_meeting_f1_acceptance": sum(r["f1_acceptance_met"] for r in summ),
               "f1_plan_failing_i": D.family_verdict(f1[DC.PLAN.id])["i_failing"][:40]}
    names = ("d8cand.json", "d8cand_summary.csv", "d8cand_cells.csv", "d8cand_lc.csv", "d8cand_a8.csv", "d8cand_whitenoise.csv")
    P.atomic_write_json(out_dir / names[0], summary)
    for name, rows in zip(names[1:], (summ, cell_rows, lc_rows, a8_rows, wrows)):
        with open(out_dir / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    rec = P.make_run_record(cfg, env, name="D8CAND_0000", status="ok", wall_time_s=wall,
                            flags={"n_meeting_f1_acceptance": summary["n_meeting_f1_acceptance"]},
                            inputs={"s3_limit_cycle": P.sha256_file(root / S3_LC), "a_ref": P.sha256_file(root / A_REF_JSON)},
                            outputs={n: P.sha256_file(out_dir / n) for n in names})
    P.write_run_record(rec, out_dir / f"D8CAND_0000_{C.short_hash(C.config_hash(cfg))}.json")
    print(f"candidates {len(summ)}; meeting F1 acceptance {summary['n_meeting_f1_acceptance']}; wall {wall:.1f} s git.dirty={env['git']['dirty']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
