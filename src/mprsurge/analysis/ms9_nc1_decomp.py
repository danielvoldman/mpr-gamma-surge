"""MS9 9c: decomposition of one mode-N classifier decision on a STORED record (A8 review after the NC1 network S+; G7, A10).

Analysis only: nothing is integrated and no threshold or criterion changes. The functions re-run the frozen classifier
(surge_metrics.classify_mode_n, unchanged) and expose the quantities it computes internally: the spectrogram windows, the baseline
P_G, P_non-G and odds, the per-window ratios against the factor (D6), the episode and the D8 fit. Variants of the A8 sensitivity
(analysis.a8_sensitivity.VARIANTS) are run on the same record and are post-hoc: they feed no gate.

Conventions of the classifier that matter for reading the numbers (read from surge_metrics.classify_mode_n):
  * a window is "flagged" if odds = P_G / P_non-G >= factor x mean(odds over the baseline windows) (rel) or P_G >= factor x mean(P_G over
    the baseline windows) (abs), and its centre is at or after t_on;
  * an episode is a run of flagged windows (gaps shorter than one window merged) with duration = (windows in the run) x step and
    cycles = duration x mean(f_pk over the run's windows); onset is the CENTRE of the first window, end is the centre of the last window
    plus half a step; so end - onset = duration - step / 2 (and the data the windows touch span (windows - 1) x step + W).
"""
from __future__ import annotations

import numpy as np

from . import a8_sensitivity as A8S
from . import surge_metrics as M

FS = 1000.0


def window_table(v, t_on, T_ramp_s, a_ref, factor=M.FACTOR_REL, band=M.G_BAND, window=None, fs=FS):
    """Per-window quantities of the classifier (no decision): dict of arrays plus the baseline scalars."""
    W, step = window if window is not None else M.window_for_ramp(T_ramp_s)
    tc, p_g, p_tot, p_ng, fpk = M._window_series(np.asarray(v, float), fs, W, step, band)
    bm = M.baseline_windows(tc, W, t_on)
    if not bm.any():
        raise ValueError("baseline too short for one window")
    odds = p_g / p_ng
    base_pg, base_png, base_odds = float(np.mean(p_g[bm])), float(np.mean(p_ng[bm])), float(np.mean(odds[bm]))
    return {"W": W, "step": step, "tc": tc, "p_g": p_g, "p_ng": p_ng, "p_tot": p_tot, "fpk": fpk, "odds": odds, "baseline_mask": bm,
            "post_mask": tc >= t_on - 1e-9, "base_pg": base_pg, "base_png": base_png, "base_odds": base_odds,
            "abs_ratio": p_g / base_pg, "rel_ratio": odds / base_odds, "factor": factor}


def baseline_summary(wt) -> dict:
    bm = wt["baseline_mask"]
    out = {"n_windows": int(bm.sum()), "W_s": wt["W"], "step_s": wt["step"], "t_first_centre": float(wt["tc"][bm][0]),
           "t_last_centre": float(wt["tc"][bm][-1]), "base_pg": wt["base_pg"], "base_png": wt["base_png"], "base_odds": wt["base_odds"]}
    for k in ("p_g", "p_ng", "odds"):
        x = wt[k][bm]
        out[f"{k}_min"], out[f"{k}_max"] = float(x.min()), float(x.max())
        out[f"{k}_max_over_min"] = float(x.max() / x.min()) if x.min() > 0 else float("nan")
    return out


def episode_cycles(wt, a, b, fs=FS) -> dict:
    """The classifier's cycle and duration bookkeeping for the run of windows a..b (inclusive)."""
    step, W, tc, fpk = wt["step"], wt["W"], wt["tc"], wt["fpk"]
    n = b - a + 1
    return {"windows": int(n), "first_centre": float(tc[a]), "last_centre": float(tc[b]), "duration_s": n * step,
            "mean_fpk_hz": float(np.mean(fpk[a:b + 1])), "fpk_per_window_hz": [float(x) for x in fpk[a:b + 1]],
            "cycles": n * step * float(np.mean(fpk[a:b + 1])), "onset_s": float(tc[a]), "end_s": float(tc[b] + step / 2),
            "end_minus_onset_s": float(tc[b] + step / 2 - tc[a]), "data_first_s": float(tc[a] - W / 2), "data_last_s": float(tc[b] + W / 2)}


def phase_cycles(v, t0_s, t1_s, band=M.G_BAND, fs=FS) -> float:
    """Independent count (ours, for comparison only): change of the unwrapped band-passed analytic phase over [t0, t1] / 2 pi."""
    z = M._analytic(np.asarray(v, float), fs, band)
    ph = np.unwrap(np.angle(z))
    i0, i1 = int(round(t0_s * fs)), min(int(round(t1_s * fs)), ph.size - 1)
    return float((ph[i1] - ph[i0]) / (2 * np.pi))


def flagged_runs(wt, test: str, W_gap=None):
    """Runs (a, b) of flagged windows of 'rel' or 'abs' after t_on, merged as the classifier does."""
    ratio = wt["rel_ratio"] if test == "rel" else wt["abs_ratio"]
    fl = (ratio >= wt["factor"]) & wt["post_mask"]
    return [(int(a), int(b)) for a, b in M._merge_runs(M._runs(fl), wt["W"], wt["step"])]


def decompose(v, t_on, T_ramp_s, threshold, a_ref, fs=FS, variant="V0") -> dict:
    """Decision on one record under one A8 variant: class, episode, D8 fit, baseline summary, ratio extremes. V0 is the frozen classifier."""
    s = A8S.spec(variant)
    win = A8S.window_of(T_ramp_s, s["wmul"])
    thr = s["amin"] * a_ref
    wt = window_table(v, t_on, T_ramp_s, a_ref, factor=s["factor"], band=s["band"], window=win, fs=fs)
    res = M.classify_mode_n(np.asarray(v, float), fs, t_on, T_ramp_s, thr, factor_rel=s["factor"], factor_abs=s["factor"],
                            min_cycles=s["cycles"], band=s["band"], window=win)
    post = wt["post_mask"]
    out = {"variant": variant, "spec": {k: (list(x) if isinstance(x, tuple) else x) for k, x in s.items()}, "threshold": thr,
           "W_s": wt["W"], "class": res.cls, "reason": res.reason, "provisional": res.provisional or "",
           "baseline": baseline_summary(wt)}
    for key, ratio in (("rel", wt["rel_ratio"]), ("abs", wt["abs_ratio"])):
        j = int(np.argmax(np.where(post, ratio, -np.inf)))
        runs = flagged_runs(wt, key)
        out[key] = {"peak_ratio": float(ratio[j]), "peak_time_s": float(wt["tc"][j]), "peak_margin_over_factor": float(ratio[j] / wt["factor"]),
                    "n_flagged_windows": int(((ratio >= wt["factor"]) & post).sum()), "runs": runs,
                    "runs_time": [(float(wt["tc"][a]), float(wt["tc"][b])) for a, b in runs],
                    "episode": None}
        ep = res.rel if key == "rel" else res.abs
        if ep is not None:
            out[key]["episode"] = {k: getattr(ep, k) for k in ("onset_s", "end_s", "duration_s", "cycles", "terminated", "f_pk_hz", "peak_p_g", "peak_rho")}
    if res.episode is not None:
        ep = res.episode
        out["episode"] = {k: getattr(ep, k) for k in ("onset_s", "end_s", "duration_s", "cycles", "terminated", "f_pk_hz", "peak_p_g", "peak_rho")}
        # run of windows behind the first qualifying episode of the test that defined it
        key = "rel" if res.rel is ep else "abs"
        for a, b in flagged_runs(wt, key):
            c = episode_cycles(wt, a, b, fs)
            if abs(c["onset_s"] - ep.onset_s) < 1e-9:
                out["episode_windows"] = c
                break
    else:
        out["episode"] = None
    d = res.d8
    out["d8"] = None if d is None else {"damped": bool(d.damped), "rate_per_s": float(d.rate), "se_per_s": float(d.se), "n_samples": int(d.n),
                                         "cycles": float(d.cycles), "t_start_s": float(d.t_start)}
    out["_wt"] = wt
    return out


def peak_margins(dec) -> dict:
    """Per-run margins for the S12x table: peak ratios / factor, baseline spread, D8 fit."""
    return {"rel_peak_ratio": dec["rel"]["peak_ratio"], "rel_peak_margin": dec["rel"]["peak_margin_over_factor"],
            "abs_peak_ratio": dec["abs"]["peak_ratio"], "abs_peak_margin": dec["abs"]["peak_margin_over_factor"],
            "rel_flagged": dec["rel"]["n_flagged_windows"], "abs_flagged": dec["abs"]["n_flagged_windows"],
            "base_pg_max_over_min": dec["baseline"]["p_g_max_over_min"], "base_odds_max_over_min": dec["baseline"]["odds_max_over_min"]}
