"""Study of candidate D8 fixes (MS7 7g2, inserted by owner ruling; design and numbers fixed in DL-153 before the run).

Analysis of synthetic data and stored records only. Reuses the 7b generators (estimator_study.ring, ar2_record) and
the DL-136 acceptance functions unchanged; the plan estimator stays the default everywhere else.
Truth is the exponential rate of the ring envelope; the pre-registered numbers are those of DL-136, not relaxed:
(i) sign match >= 95 percent in every cell with |true rate| >= 2 per s; (ii) false "damped" <= 5 percent in every
zero-growth cell; (iii) bias, 2-SE coverage and the inflation factor are reported.
"""
from __future__ import annotations

import numpy as np

from . import a8_sensitivity as S8
from . import d8_candidates as DC
from . import estimator_study as E
from . import surge_metrics as M

FS = E.FS
BAND = E.BAND
RAMP_S = (0.1, 0.5)               # gradual-onset ramp lengths (raised cosine), ours, UNVERIFIED
F3_AMP, F3_NOISE, F3_T_ON, F3_TOTAL = 1.5, 1e-4, 1.0, 14.0     # finding 1 case (as D_sustained40_amp1.5 of DL-146)
F3_ON = 2.0                       # quiet until 2 s, 0.5 s rise, nonzero to the record end
LC_T_ON = (0.0, 1.0, 3.0)         # stored ref_devalle limit cycle, the DL-140 finding 2 cases
LC_T_ON_GRID = tuple(np.arange(0.0, 4.01, 0.25))
LAM5 = float(np.log(1.0 / E.THR) / (5 / 40.0))        # test_surge_metrics five-cycle ring
LAM15 = float(np.log(1.0 / E.THR) / (15 / 40.0))      # slowly damped ring (the DL-073 case)
WHITE_SD = (0.04, 0.2, 0.45)      # 0.04 = DL-147; 0.2 and 0.45 make the band envelope cross 0.2176 (ours)
WHITE_T_RAMP = (3.16, 10.0, 17.78, 31.62, 56.23, 100.0)    # W = 0.2, 0.333, 0.593, 1.054, 1.874, 2.0 s
WHITE_DRAWS = 500
A8_RING_CASES = ("D_ring_slow_-3", "D_ring_fast_-25", "N_ring_slow_-3", "N_ring_fast_-25")


# ---- families of cells ---------------------------------------------------------------------------------------------
def ring_ramp(rng, rate, ramp_s, noise):
    """E.ring with step lead 1 s and a raised-cosine amplitude gate of length ramp_s from the onset (gradual onset)."""
    t = np.arange(int(E.TOTAL_S * FS)) / FS
    tau = np.clip(t - E.LEAD_STEP_S, 0.0, None)
    a0 = 5 * E.THR * np.exp(0.3 * max(-rate, 0.0))
    ph = rng.uniform(0, 2 * np.pi)
    gate = 0.5 * (1 - np.cos(np.pi * np.clip(tau / ramp_s, 0, 1)))
    grow = np.exp(rate * np.minimum(tau, E.GROW_CAP_S) if rate > 0 else rate * tau)
    v = np.where(t >= E.LEAD_STEP_S, a0 * grow * gate * np.sin(2 * np.pi * E.F_RING * tau + ph), 0.0)
    return v + noise * rng.standard_normal(t.size)


def f2_cells():
    out = []
    for ramp in RAMP_S:
        for noise in (0.005, 0.02):
            for r in E.RATES:
                out.append(dict(kind="ring", rate=r, onset=f"ramp{ramp:g}", ramp=ramp, noise=noise, group="zero" if r == 0.0 else "ring"))
    return out


def f3_signal(rng):
    td = np.arange(int(F3_TOTAL * FS)) / FS
    ph = rng.uniform(0, 2 * np.pi)
    return F3_NOISE * rng.standard_normal(td.size) + F3_AMP * S8._gate(td, F3_ON, 1e9) * np.sin(2 * np.pi * 40 * td + ph)


def f5_ring5(rng):
    """test_surge_metrics five-cycle ring: exp(-lam t) sin(2 pi 40 t) from the record start, noise 1e-4, 4 s."""
    t = np.arange(int(4.0 * FS)) / FS
    return np.exp(-LAM5 * t) * np.sin(2 * np.pi * 40 * t + rng.uniform(0, 2 * np.pi)) + 1e-4 * rng.standard_normal(t.size)


def f5_ring15(rng):
    """The DL-073 case: 15 cycles above threshold, step onset at 1 s, noise 1e-4, 4 s."""
    t = np.arange(int(4.0 * FS)) / FS
    tau = np.clip(t - 1.0, 0, None)
    v = np.where(t >= 1.0, np.exp(-LAM15 * tau) * np.sin(2 * np.pi * 40 * tau + rng.uniform(0, 2 * np.pi)), 0.0)
    return v + 1e-4 * rng.standard_normal(t.size)


# ---- running a family for all candidates -----------------------------------------------------------------------------
def run_cell_all(gen, n_draw, seq, cands, thr):
    """{cand id: (rate, se, cycles) arrays of n_draw} for one cell; gen(rng) -> record; same record for every candidate."""
    out = {c.id: tuple(np.full(n_draw, np.nan) for _ in range(3)) for c in cands}
    for i, child in enumerate(seq.spawn(n_draw)):
        v = gen(np.random.default_rng(child))
        for cid, (r, s, cy) in DC.fit_all(v, FS, BAND, thr, cands).items():
            out[cid][0][i], out[cid][1][i], out[cid][2][i] = r, s, cy
    return out


def gen_for_cell(cell):
    if cell["kind"] == "ar2":
        return E.ar2_record, E.Z2_THR_REL
    if cell["onset"].startswith("ramp"):
        return (lambda rng: ring_ramp(rng, cell["rate"], cell["ramp"], cell["noise"])), E.THR
    return (lambda rng: E.ring(rng, cell["rate"], cell["onset"], cell["noise"])), E.THR


def summarize_c(cell, rate, se, cyc):
    """E.summarize with one change: a draw whose fit is undefined (nan: no crossing, fewer than 3 samples, or the
    minimum-window rule) counts as a non-damped call over all n_draw draws, the plan's nan convention, instead of
    being dropped. Bias, coverage and the inflation ratio use the defined fits only (n_defined reported)."""
    ok = np.isfinite(rate) & np.isfinite(se) & (se > 0)
    damped_all = np.where(ok, rate < -M.D8_SE_MULT * np.where(ok, se, 1.0), False)
    r, s = rate[ok], se[ok]
    true = cell["rate"]
    err = r - true
    n_ok = int(ok.sum())
    d = {**cell, "n": n_ok, "n_draw": int(rate.size)}
    if n_ok > 2:
        d.update(bias=float(err.mean()), bias_rel=float(err.mean() / true) if true != 0 else None,
                 sd=float(err.std(ddof=1)), se_median=float(np.median(s)),
                 coverage_2se=float(np.mean(np.abs(err) <= 2 * s)),
                 ratio_q=float(np.quantile(np.abs(err) / s, E.COVER_Q)),
                 cycles_median=float(np.median(cyc[ok])), frac_full_window=float(np.mean(cyc[ok] >= 9.9)))
    else:
        d.update(bias=float("nan"), bias_rel=None, sd=float("nan"), se_median=float("nan"), coverage_2se=float("nan"),
                 ratio_q=float("nan"), cycles_median=float("nan"), frac_full_window=float("nan"))
    d["frac_damped"] = float(damped_all.mean())
    d["match"] = None if abs(true) < E.FLOOR else float(np.mean(damped_all == (true < 0)))
    d["false_damped"] = float(damped_all.mean()) if true == 0 else None
    d["false_non_damped"] = float(1 - damped_all.mean()) if true <= -E.FLOOR else None
    return d


def run_family(cells, seqs, n_draw, cands):
    """Summary rows per candidate: {cand id: [summarize_c(...) row per cell]}."""
    rows = {c.id: [] for c in cands}
    for cell, seq in zip(cells, seqs):
        gen, thr = gen_for_cell(cell)
        res = run_cell_all(gen, n_draw, seq, cands, thr)
        for cid, (r, s, cy) in res.items():
            rows[cid].append(summarize_c(cell, r, s, cy))
    return rows


def zero_family(gen, thr, n_draw, seq, cands, v_from=0):
    """Draws of a single zero-growth or fixed-truth record family. Returns {cand id: (frac_damped, rate, se arrays)}."""
    out = {c.id: [np.full(n_draw, np.nan) for _ in range(2)] for c in cands}
    for i, child in enumerate(seq.spawn(n_draw)):
        v = gen(np.random.default_rng(child))[v_from:]
        for cid, (r, s, _) in DC.fit_all(v, FS, BAND, thr, cands).items():
            out[cid][0][i], out[cid][1][i] = r, s
    return out


def damped_fraction(rate, se):
    """Fraction of draws called damped (nan fits count as non-damped, the plan's convention)."""
    return float(np.mean(rate < -M.D8_SE_MULT * se))


# ---- stored limit cycle ------------------------------------------------------------------------------------------------
def lc_calls(v, thr, cands, t_ons):
    """{cand id: {t_on: (damped, rate, se)}} on the stored record, v from t_on (as classify_mode_d calls D8)."""
    out = {c.id: {} for c in cands}
    for t_on in t_ons:
        seg = np.asarray(v, float)[int(round(t_on * FS)):]
        for cid, (r, s, _) in DC.fit_all(seg, FS, BAND, thr, cands).items():
            out[cid][float(t_on)] = (bool(r < -M.D8_SE_MULT * s), float(r), float(s))
    return out


# ---- acceptance and ranking ---------------------------------------------------------------------------------------------
def family_verdict(rows):
    """DL-136 (i)/(ii)/(iii) on a family's rows (same rules as estimator_study.verdicts, nan-safe) plus failing-cell counts."""
    above = [r for r in rows if r["match"] is not None]
    zero = [r for r in rows if r["false_damped"] is not None]
    i_fail = [(r["kind"], r["rate"], r["onset"], r["noise"], r["match"]) for r in above if r["match"] < E.MATCH_MIN]
    ii_fail = [(r["kind"], r["onset"], r["noise"], r["false_damped"]) for r in zero if r["false_damped"] > E.FALSE_DAMPED_MAX]
    ks = {}
    for r in rows:
        if np.isfinite(r["ratio_q"]):
            key = f"{r['kind']}/{r['onset']}"
            ks[key] = max(ks.get(key, 0.0), r["ratio_q"])
    fnd = [r["false_non_damped"] for r in rows if r["false_non_damped"] is not None]
    return {"i_met": not i_fail, "i_cells": len(above), "i_fail_n": len(i_fail), "i_failing": i_fail,
            "ii_met": not ii_fail, "ii_cells": len(zero), "ii_fail_n": len(ii_fail), "ii_failing": ii_fail,
            "ii_max_false_damped": max((r["false_damped"] for r in zero), default=None),
            "false_non_damped_max": max(fnd, default=None),
            "false_non_damped_mean": float(np.mean(fnd)) if fnd else None,
            "inflation_k_max_by_group": ks, "inflation_k_max": max(ks.values(), default=None)}


def rank_key(rec):
    """Lexicographic ranking, fixed in DL-153 (lower is better): F1 failing cells ((i) + (ii)); stored limit cycle
    damped calls at t_on 0, 1, 3; finding-1 failures (fraction damped above 5 percent counts 1); A8 ring failures;
    F2 failing cells; F1 mean absolute bias on damped-ring cells."""
    return (rec["f1_fail"], rec["lc_fail"], rec["f3_fail"], rec["a8_fail"], rec["f2_fail"], rec["f1_abs_bias"])


def mean_abs_bias(rows):
    b = [abs(r["bias"]) for r in rows if r["kind"] == "ring" and r["rate"] <= -E.FLOOR]
    return float(np.mean(b)) if b else float("nan")


# ---- white noise at the real window sizes, class level ------------------------------------------------------------------------
def white_counts(cand, T_ramp_s, sd, a_ref, n_draws=WHITE_DRAWS):
    """Mode-N class counts over n_draws white-noise records (as DL-147), D8 = the candidate; also how often D8 was
    called and how often it said damped. Same draws as DL-147 at sd 0.04 (common random numbers)."""
    d8 = M.PLAN_D8 if cand.is_plan else DC.CandidateD8(cand)
    counts, called, damped = {}, 0, 0
    for k in range(n_draws):
        r = S8.classify(S8.white_record(k, sd), "N", S8.WHITE_BASE_S, T_ramp_s, a_ref, "V0", d8=d8)
        counts[r["cls"]] = counts.get(r["cls"], 0) + 1
        called += bool(r["d8_called"])
        damped += bool(r["d8_called"] and r["d8_damped"])
    return {"counts": counts, "d8_called": called, "d8_damped": damped, "n": n_draws}
