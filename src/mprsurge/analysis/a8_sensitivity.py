"""A8 sensitivity, MS7 (DL-146). Analysis only: classifies stored and synthetic arrays, integrates nothing.

Variants (plan A8, RB10, ms7_plan 7f row): band 30 to 120 Hz; factors 1.5 and 4 (relative and absolute together);
A_min factor 0.05 and 0.2; window x 0.5 and x 2 (step = W / 2); minimum cycles 5 and 20. V0 is the default.
Data (DL-136 D-3): seeded synthetic signals, the 7e baseline-only records, stored S3 / S4 mode-D records, and seeded
white noise at the real window sizes (option D of DL-144). No M3 ramp record, no new simulation. Every class that
went through the D8 call is provisional (D8 open, DL-137); the D8 call itself is the plan estimator, unchanged.
No acceptance number is applied: the plan gives none for these data (RB10's 10 percent is a map-cell test for A11).
"""
from __future__ import annotations

import numpy as np

from . import surge_metrics as M

FS = 1000.0
SIGMA_SYN = 0.02                     # white-noise sd of the mode-N synthetic cases (as tests/test_surge_classes.py `mixed`)
P_G_FRACTION = 75.0 / 500.0          # share of white-noise variance in 25 to 100 Hz (one-sided 0 to 500 Hz); ours
RATIOS_N = (1.3, 1.8, 2.5, 3.5, 6.0)  # target P_G(burst) / P_G(baseline); straddle 1.5, 2 and 4
AMPS_D = (0.07, 0.15, 0.3, 0.6, 1.5)  # mode-D burst amplitudes; straddle 0.05, 0.1, 0.2 x A_ref = 0.109, 0.218, 0.435
LEVELS = (0.25, 1.0 / 3.0, 0.5, 2.0 / 3.0, 0.75)   # reachability levels, see reach_table
WHITE_SD = 0.04                      # headline baseline v std 0.0376 to 0.0417 (DL-141); ours
WHITE_BASE_S, WHITE_TEST_S = 5.0, 20.0

DEFAULT = {"band": M.G_BAND, "factor": 2.0, "amin": 0.1, "wmul": 1.0, "cycles": 10}
VARIANTS = {"V0": {}, "band_30_120": {"band": (30.0, 120.0)}, "factors_1.5": {"factor": 1.5}, "factors_4": {"factor": 4.0},
            "amin_0.05": {"amin": 0.05}, "amin_0.2": {"amin": 0.2}, "window_x0.5": {"wmul": 0.5}, "window_x2": {"wmul": 2.0},
            "cycles_5": {"cycles": 5}, "cycles_20": {"cycles": 20}}


def spec(variant):
    return {**DEFAULT, **VARIANTS[variant]}


def rng_for(*key, root=20261008):
    return np.random.default_rng(np.random.SeedSequence(entropy=root, spawn_key=tuple(key)))


def window_of(T_ramp_s, wmul):
    W, _ = M.window_for_ramp(T_ramp_s)
    W *= wmul
    return W, W / 2.0


def classify(v, mode, t_on, T_ramp_s, a_ref, variant, d8=M.PLAN_D8, inside_a4_region=None):
    """One classification under a variant. Returns a flat dict; cls 'not_run' if the window does not fit the record."""
    s = spec(variant)
    win = window_of(T_ramp_s, s["wmul"])
    thr = s["amin"] * a_ref
    try:
        if mode == "N":
            r = M.classify_mode_n(v, FS, t_on, T_ramp_s, thr, d8=d8, factor_rel=s["factor"], factor_abs=s["factor"],
                                  min_cycles=s["cycles"], band=s["band"], window=win)
        else:
            r = M.classify_mode_d(v, FS, t_on, T_ramp_s, thr, d8=d8, min_cycles=s["cycles"], band=s["band"],
                                  inside_a4_region=inside_a4_region, window=win)
    except ValueError as e:
        return {"cls": "not_run", "note": str(e)[:80], "provisional": "", "d8_called": False, "d8_damped": "",
                "d8_rate": "", "d8_se": "", "f_pk_hz": "", "window_s": win[0]}
    d = r.d8
    ep = r.episode
    return {"cls": r.cls, "note": r.reason, "provisional": r.provisional or "", "d8_called": d is not None,
            "d8_damped": "" if d is None else d.damped, "d8_rate": "" if d is None else d.rate,
            "d8_se": "" if d is None else d.se, "f_pk_hz": "" if ep is None else ep.f_pk_hz, "window_s": win[0]}


# ---- synthetic set (i) ---------------------------------------------------------------------------------------------
def _t(total):
    return np.arange(int(round(total * FS))) / FS


def _gate(t, on, off, rise=0.5):
    return np.clip((t - on) / rise, 0, 1) * np.clip((off - t) / rise, 0, 1)


def _ring(t, on, f, rate, amp):
    return np.where(t >= on, amp * np.exp(rate * (t - on)) * np.sin(2 * np.pi * f * (t - on)), 0.0)


def synthetic_cases():
    """[(case_id, mode, v, t_on, T_ramps)] seeded. Mode N: 40 s, t_on 10 s, white noise sd 0.02, events 12 to 20 s.
    Mode D: 14 s, t_on 1 s, noise 1e-4, events 2 to 8 s. Amplitudes of the mode-N ladder come from the white-noise
    arithmetic P_G(noise) = 0.15 sigma^2 (ours, UNVERIFIED): a = sqrt(2 (ratio - 1) P_G)."""
    out = []
    tn = _t(40.0)
    pg0 = P_G_FRACTION * SIGMA_SYN**2

    def noise_n(k):
        return SIGMA_SYN * rng_for(7, 6, 1, k).standard_normal(tn.size)

    k = 0
    for ratio in RATIOS_N:
        a = float(np.sqrt(2.0 * (ratio - 1.0) * pg0))
        out.append((f"N_burst40_ratio{ratio}", "N", noise_n(k) + a * _gate(tn, 12, 20) * np.sin(2 * np.pi * 40 * tn), 10.0, (120.0, 3.0)))
        k += 1
    a6 = float(np.sqrt(2.0 * 5.0 * pg0))
    out.append(("N_sustained40_ratio6", "N", noise_n(k) + a6 * _gate(tn, 12, 1e9) * np.sin(2 * np.pi * 40 * tn), 10.0, (120.0, 3.0))); k += 1
    ph = 2 * np.pi * (20.0 * (tn - 12) + 0.5 * (60.0 - 20.0) / 8.0 * (tn - 12) ** 2)
    out.append(("N_chirp20_60_ratio6", "N", noise_n(k) + a6 * _gate(tn, 12, 20) * np.sin(ph), 10.0, (120.0, 3.0))); k += 1
    out.append(("N_ring_fast_-25", "N", noise_n(k) + 20 * a6 * _ring(tn, 12, 40.0, -25.0, 1.0), 10.0, (120.0, 3.0))); k += 1
    out.append(("N_ring_slow_-3", "N", noise_n(k) + 20 * a6 * _ring(tn, 12, 40.0, -3.0, 1.0), 10.0, (120.0, 3.0))); k += 1
    out.append(("N_trend", "N", noise_n(k) + 0.5 * np.clip((tn - 12) / 8.0, 0, 1), 10.0, (120.0, 3.0))); k += 1
    for f in (27.0, 110.0):
        out.append((f"N_burst{f:g}_ratio6", "N", noise_n(k) + a6 * _gate(tn, 12, 20) * np.sin(2 * np.pi * f * tn), 10.0, (120.0, 3.0))); k += 1
    out.append(("N_null", "N", noise_n(k), 10.0, (120.0, 3.0)))
    td = _t(14.0)

    def noise_d(k):
        return 1e-4 * rng_for(7, 6, 3, k).standard_normal(td.size)

    k = 0
    for a in AMPS_D:
        out.append((f"D_burst40_amp{a}", "D", noise_d(k) + a * _gate(td, 2, 8) * np.sin(2 * np.pi * 40 * td), 1.0, (120.0,))); k += 1
    out.append(("D_sustained40_amp1.5", "D", noise_d(k) + 1.5 * _gate(td, 2, 1e9) * np.sin(2 * np.pi * 40 * td), 1.0, (120.0,))); k += 1
    ph = 2 * np.pi * (20.0 * (td - 2) + 0.5 * (60.0 - 20.0) / 6.0 * (td - 2) ** 2)
    out.append(("D_chirp20_60_amp1.5", "D", noise_d(k) + 1.5 * _gate(td, 2, 8) * np.sin(ph), 1.0, (120.0,))); k += 1
    out.append(("D_ring_fast_-25", "D", noise_d(k) + _ring(td, 2, 40.0, -25.0, 3.0), 1.0, (120.0,))); k += 1
    out.append(("D_ring_slow_-3", "D", noise_d(k) + _ring(td, 2, 40.0, -3.0, 3.0), 1.0, (120.0,))); k += 1
    out.append(("D_trend", "D", noise_d(k) + 0.5 * np.clip((td - 2) / 6.0, 0, 1), 1.0, (120.0,))); k += 1
    for f in (27.0, 110.0):
        out.append((f"D_burst{f:g}_amp1.5", "D", noise_d(k) + 1.5 * _gate(td, 2, 8) * np.sin(2 * np.pi * f * td), 1.0, (120.0,))); k += 1
    out.append(("D_null", "D", noise_d(k), 1.0, (120.0,)))
    return out


# ---- stored mode-D records (iii) -----------------------------------------------------------------------------------
S3_SLICE = (2000, 8000)     # settled part 2 to 8 s, t_on = 1.0 s (the 7c stored-record convention, DL-140 finding 3); ours
S3_T_ON = 1.0
S4_T_ON = 0.0               # each S4 segment is one constant-parameter hold after a step; v from the step, t_on = segment start; ours


def s4_segments(z):
    """[(step_index, eta, v)] one per constant-parameter hold of a stored S4 record (the `step` array)."""
    step = np.asarray(z["step"])
    v = np.asarray(z["v"], float)
    out = []
    for k in np.unique(step):
        m = step == k
        out.append((int(k), float(np.asarray(z["param"])[m][0]), v[m]))
    return out


# ---- baseline-only records (ii): class-free measurements -----------------------------------------------------------
def rho_variant(v, T_ramp_s, band, wmul, t_end=None):
    """Baseline rho as baseline_report.rho_row, with G band and window multiplier as variants. Record = 5 s baseline."""
    v = np.asarray(v, float)
    t_end = (v.size - 1) / FS if t_end is None else t_end
    W, step = window_of(T_ramp_s, wmul)
    tc, p_g, p_tot, _, _ = M._window_series(v, FS, W, step, band)
    m = M.baseline_windows(tc, W, t_end)
    if not m.any():
        return {"W_s": W, "n_windows": 0, "rho": float("nan")}
    return {"W_s": W, "n_windows": int(m.sum()), "rho": float(np.mean(p_g[m] / p_tot[m]))}


def reach_table(rows):
    """rows: dicts with index, W_s, rho (one per cell and seed; the stored 7f baseline rho). Per W: records and cells at or
    above each level in LEVELS. Cell value = mean rho over its seeds (as DL-145); 'any' = at least one seed.
    Reading: a rho ratio ratio-times the baseline cannot exceed 1/rho0, so it cannot reach f when rho0 >= 1/f
    (Table 2.1 wording; 0.5 at f = 2 is the plan's number, 0.667 at 1.5 and 0.25 at 4 are our arithmetic, UNVERIFIED).
    The levels 1/3 and 0.75 are 1 - 1/f at f = 1.5 and 4 (the form given in the step instruction), kept so both
    readings can be seen. The surge test itself is on odds P_G / P_non-G (CP18), which has no upper bound (F-7)."""
    by_w = {}
    for r in rows:
        by_w.setdefault(r["W_s"], {}).setdefault(r["index"], []).append(r["rho"])
    out = []
    for W in sorted(by_w):
        cells = by_w[W]
        rec = np.array([x for v in cells.values() for x in v])
        cm = np.array([np.mean(v) for v in cells.values()])
        cx = np.array([np.max(v) for v in cells.values()])
        for lv in LEVELS:
            out.append({"W_s": W, "level": lv, "n_cells": len(cells), "cells_mean_ge": int((cm >= lv).sum()),
                        "cells_any_seed_ge": int((cx >= lv).sum()), "n_records": int(rec.size),
                        "records_ge": int((rec >= lv).sum())})
    return out


# ---- white noise at the real window sizes (option D, DL-144) --------------------------------------------------------
def white_record(k, sd=WHITE_SD):
    """Draw k of seeded white noise, baseline + test span in one continuous record (no join). Same draw for every
    variant and T_ramp (common random numbers); spawn_key (7, 6, 2, k)."""
    n = int(round((WHITE_BASE_S + WHITE_TEST_S) * FS))
    return sd * rng_for(7, 6, 2, k).standard_normal(n)


def whitenoise_classes(T_ramp_s, variant, a_ref, n_draws, sd=WHITE_SD):
    """Counts of mode-N classes over n_draws white-noise records (t_on = 5 s, D8 = plan estimator, provisional)."""
    counts = {}
    for k in range(n_draws):
        c = classify(white_record(k, sd), "N", WHITE_BASE_S, T_ramp_s, a_ref, variant)["cls"]
        counts[c] = counts.get(c, 0) + 1
    return counts
