"""Estimator study for DL-062 and DL-073 (MS7 7b; pre-registration in DL-136). Analysis of synthetic data only.

Signals are seeded; the fit is the pipeline's own surge_metrics.envelope_growth. Truth for a ring is the
exponential rate of its envelope. All settings are ours or owner-chosen (UNVERIFIED), fixed in DL-136.
"""
from __future__ import annotations

import numpy as np

from . import surge_metrics as M

FS = 1000.0
BAND = (25.0, 100.0)
THR = 0.1
TOTAL_S = 4.0
F_RING = 40.0
LEAD_STEP_S = 1.0
GROW_CAP_S = 0.5         # growth saturates after this time from onset (a limit cycle); the fit window ends by 0.3 s
FLOOR = 2.0              # per s, DL-136
MATCH_MIN = 0.95         # DL-136 (i)
FALSE_DAMPED_MAX = 0.05  # DL-136 (ii)
Z2_BW_HZ = 3.0           # AR(2) bandwidth, ours
Z2_THR_REL = 0.5         # threshold as a fraction of the mean envelope, ours
COVER_Q = 0.9545         # nominal coverage of 2 SE
RATES = (-25.0, -12.0, -6.0, -3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0, 6.0, 12.0)


def ring(rng, rate, onset, noise):
    """A0 exp(rate tau) (growth capped at GROW_CAP_S) sin(2 pi f tau + phase) from the onset (zero before), plus white noise."""
    lead = LEAD_STEP_S if onset == "step" else 0.0
    t = np.arange(int(TOTAL_S * FS)) / FS
    tau = np.clip(t - lead, 0.0, None)
    a0 = 5 * THR * np.exp(0.3 * max(-rate, 0.0))
    ph = rng.uniform(0, 2 * np.pi)
    v = np.where(t >= lead, a0 * np.exp(rate * np.minimum(tau, GROW_CAP_S) if rate > 0 else rate * tau) * np.sin(2 * np.pi * F_RING * tau + ph), 0.0)
    return v + noise * rng.standard_normal(t.size)


def ar2_record(rng):
    """Stationary narrow-band AR(2) record scaled so the mean band-passed envelope is 1."""
    n = int(TOTAL_S * FS)
    burn = 4000
    rho = np.exp(-np.pi * Z2_BW_HZ / FS)
    a1, a2 = 2 * rho * np.cos(2 * np.pi * F_RING / FS), -rho**2
    e = rng.standard_normal(n + burn)
    x = np.zeros(n + burn)
    for k in range(2, n + burn):
        x[k] = a1 * x[k - 1] + a2 * x[k - 2] + e[k]
    x = x[burn:]
    return x / M.envelope(x, FS, BAND).mean()


def fit(v, thr=THR):
    g = M.envelope_growth(v, FS, BAND, thr)
    return g["rate"], g["se"], g["cycles"]


def scenarios():
    """Cell list: dicts with kind, rate, onset, noise, group ('zero' for zero true growth)."""
    out = []
    for onset in ("start", "step"):
        for noise in (0.005, 0.02):
            for r in RATES:
                out.append(dict(kind="ring", rate=r, onset=onset, noise=noise, group="zero" if r == 0.0 else "ring"))
    out.append(dict(kind="ar2", rate=0.0, onset="start", noise=0.0, group="zero"))
    return out


def run_cell(cell, n_draw, seq):
    """n_draw fits for one cell; seq is the cell's SeedSequence. Returns arrays rate, se, cycles."""
    rate, se, cyc = (np.full(n_draw, np.nan) for _ in range(3))
    for i, child in enumerate(seq.spawn(n_draw)):
        rng = np.random.default_rng(child)
        if cell["kind"] == "ring":
            rate[i], se[i], cyc[i] = fit(ring(rng, cell["rate"], cell["onset"], cell["noise"]))
        else:
            rate[i], se[i], cyc[i] = fit(ar2_record(rng), Z2_THR_REL)
    return rate, se, cyc


def summarize(cell, rate, se, cyc):
    ok = np.isfinite(rate) & np.isfinite(se) & (se > 0)
    r, s = rate[ok], se[ok]
    true = cell["rate"]
    damped = r < -2 * s
    err = r - true
    d = {**cell, "n": int(ok.sum()), "n_draw": int(rate.size),
         "bias": float(err.mean()), "bias_rel": float(err.mean() / true) if true != 0 else None,
         "sd": float(err.std(ddof=1)), "se_median": float(np.median(s)),
         "coverage_2se": float(np.mean(np.abs(err) <= 2 * s)),
         "ratio_q": float(np.quantile(np.abs(err) / s, COVER_Q)),
         "frac_damped": float(damped.mean()), "cycles_median": float(np.median(cyc[ok])),
         "frac_full_window": float(np.mean(cyc[ok] >= 9.9))}
    d["match"] = None if abs(true) < FLOOR else float(np.mean(damped == (true < 0)))
    d["false_damped"] = float(damped.mean()) if true == 0 else None
    d["false_non_damped"] = float(1 - damped.mean()) if true <= -FLOOR else None
    return d


def verdicts(rows):
    """Acceptance (i), (ii) and the inflation factors (iii) of DL-136 over the summarized cells."""
    above = [r for r in rows if r["match"] is not None]
    zero = [r for r in rows if r["false_damped"] is not None]
    i_fail = [(r["kind"], r["rate"], r["onset"], r["noise"], r["match"]) for r in above if r["match"] < MATCH_MIN]
    ii_fail = [(r["kind"], r["onset"], r["noise"], r["false_damped"]) for r in zero if r["false_damped"] > FALSE_DAMPED_MAX]
    by = {}
    for r in rows:
        by.setdefault(f"{r['kind']}/{r['onset']}", []).append(r["ratio_q"])
    ks = {k: float(np.max(v)) for k, v in by.items()}
    return {"i_met": not i_fail, "i_cells": len(above), "i_failing": i_fail,
            "ii_met": not ii_fail, "ii_cells": len(zero), "ii_failing": ii_fail,
            "ii_max_false_damped": max(r["false_damped"] for r in zero),
            "false_non_damped_max": max((r["false_non_damped"] for r in rows if r["false_non_damped"] is not None), default=None),
            "inflation_k_max_by_group": ks, "inflation_k_max": max(ks.values())}
