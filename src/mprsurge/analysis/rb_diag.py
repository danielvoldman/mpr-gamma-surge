"""8f2: stored-data diagnoses behind the reviewer's rulings (DL-186). Analysis only: reads stored records, integrates nothing, changes no rule.

  rb6_resolution : the 1 ms output grid in eta units against the 5 percent RB6 bound, per floor level (ruling 7).
  rb3a_diagnosis : per in-range run, eta and time errors, the A4 step in seconds, onset against t_pred, the envelope growth rate near the onset
                   against Re lambda of the A4 fixed point at the same (eta, J), the predicted amplitude at the observed crossing, and the
                   distance of (v, r) from the quasi-static fixed point at t_on, t_pred and the crossing.
  radau_diagnosis: onset, delay and the pre-onset envelope trajectory of the DOP853 runs (rtol 1e-8, 1e-10, 1e-12) and the Radau run.

Definitions here are ours (UNVERIFIED as rules; they are diagnostics, not criteria): the growth rate is the OLS slope of ln(envelope) over the
samples between the last time the envelope was below threshold / 10 and the first crossing (one decade), converted to 1/tau. The envelope is
surge_metrics.envelope (25 to 100 Hz band-pass, Hilbert), the one the raw crossing uses. Explanations offered in the report are [reasoned, not tested].
"""
from __future__ import annotations

import math

import numpy as np

from . import entry_exit as EE
from . import surge_metrics as M
from ..models.fixed_points import fixed_points
from ..units import s_to_tau, tau_to_s


# ---- RB6 grid resolution (ruling 7) -------------------------------------------------------------------------------
def rb6_resolution_row(level, sigma_floor, step_eta, med_default, med_finest, onset_default, onset_finest, bound, dt_out_ms=1.0):
    """Resolution of the RB6 statistic at one floor level. step_eta: eta change over one output sample at the onset (signed value ignored).
    med_*: median delays (eta units); onset_*: per-seed onset times (s), same seeds, same order."""
    step = abs(float(step_eta))
    a, b = np.asarray(onset_default, float), np.asarray(onset_finest, float)
    d = np.abs(b - a)
    den = abs(float(med_default))
    rel_obs = abs(float(med_finest) - float(med_default)) / den if den else float("inf")
    return {
        "level": level, "sigma_floor": sigma_floor, "output_step_ms": dt_out_ms, "eta_per_output_step": step,
        "median_delay_default": float(med_default), "median_delay_finest": float(med_finest), "abs_median_delay_denominator": den,
        "bound": bound, "bound_in_eta": bound * den, "bound_in_output_steps": bound * den / step if step else float("inf"),
        "bound_in_ms": bound * den / step * dt_out_ms if step else float("inf"),
        "smallest_nonzero_rel_change_one_step": step / den if den else float("inf"),
        "smallest_nonzero_rel_change_half_step": 0.5 * step / den if den else float("inf"),
        "note_half_step": "the median of 10 seeds is the mean of the two middle seeds, so one seed moving one sample moves the median by half a sample",
        "bound_finer_than_one_step": bool(bound * den < step),
        "bound_finer_than_half_step": bool(bound * den < 0.5 * step),
        "max_abs_onset_diff_ms": float(np.nanmax(d) * 1000.0), "median_abs_onset_diff_ms": float(np.nanmedian(d) * 1000.0),
        "n_seeds_onset_identical": int((d == 0).sum()), "n_seeds": int(d.size), "observed_rel_change": rel_obs,
    }


# ---- envelope pieces ----------------------------------------------------------------------------------------------
def ols_slope(t, y):
    """OLS slope of y against t; nan for fewer than 3 points."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    if t.size < 3:
        return float("nan")
    tc = t - t.mean()
    return float((tc * (y - y.mean())).sum() / (tc * tc).sum())


def decade_window(env, i_cross, thr, factor=10.0):
    """(i0, i1) with i1 = i_cross and i0 - 1 the last index before i_cross at which env < thr / factor; None if none."""
    below = np.flatnonzero(env[:i_cross] < thr / factor)
    return None if below.size == 0 else (int(below[-1]) + 1, int(i_cross))


def growth_rate_per_tau(t_s, env, i0, i1, tau_ms):
    """Slope of ln(env) over samples i0..i1 inclusive, in 1/tau (t_s in seconds)."""
    return ols_slope(t_s[i0:i1 + 1], np.log(env[i0:i1 + 1])) * tau_ms / 1000.0


def level_crossings(env, t_s, i_from, levels):
    """First time (s) at or after sample i_from at which env >= level, per level (None if never)."""
    out = {}
    for L in levels:
        hit = np.flatnonzero(env[i_from:] >= L)
        out[repr(float(L))] = None if hit.size == 0 else float(t_s[i_from + hit[0]])
    return out


def gain_at(t, re, I, tq):
    """I at time tq (tau) from the node arrays, extended with the constant final Re lambda after the last node."""
    return float(I[-1] + re[-1] * (tq - t[-1])) if tq > t[-1] else float(np.interp(tq, t, I))


def fp_distance(cfg, arr, i):
    """|v - v*|, |r - r*| of the stored state at sample i from the stable quasi-static fixed point of M3 at the stored (eta, J, Delta)."""
    r_s, v_s, _ = fixed_points(float(arr["eta"][i]), float(arr["J"][i]), float(arr["Delta"][i]), model="M3")[0]
    return {"abs_dv": abs(float(arr["v"][i]) - float(v_s)), "abs_dr": abs(float(arr["r"][i]) - float(r_s)), "v_fp": float(v_s), "r_fp": float(r_s)}


def mean_re_lambda(cfg, arr, i0, i1, n=25):
    """Mean of the leading Re lambda at the stored (eta, J) over n samples between i0 and i1 (1/tau), and its value at i1."""
    m = cfg["model"]
    tdt = m["tau_d_ms"] / m["tau_ms"]
    idx = np.unique(np.linspace(i0, i1, n).astype(int))
    vals = [EE.leading_re(float(arr["eta"][i]), float(arr["J"][i]), float(arr["Delta"][i]), tdt) for i in idx]
    return float(np.mean(vals)), float(vals[-1])


# ---- RB3(a) -------------------------------------------------------------------------------------------------------
def rb3a_run(cfg, arr, row, thr, h, pred=None):
    """Diagnosis of one in-range run. row: the A7 row (dict-like); pred: (path, t, re, I) of entry_exit.path_gain, computed if None."""
    tau_ms = cfg["model"]["tau_ms"]
    fs = 1000.0 / cfg["solver"]["dt_out_ms"]
    t_s = arr["t_ms"] / 1000.0
    env = M.envelope(arr["v"], fs, M.G_BAND)
    path, t, re, I = pred or EE.path_gain(cfg, h)
    tc, tp, ton = float(row["onset_cross_s"]), float(row["t_pred_s"]), float(row["t_on_s"])
    i_c, i_p, i_on = (int(round(x * fs)) for x in (tc, tp, ton))
    i_p = min(i_p, len(t_s) - 1)
    ee = EE.entry_exit(cfg, path, t, re, I, float(row["delta0"]), thr, h)
    tol_tau = ee["tol_step"]
    out = {
        "run_id": row["run_id"], "family": row["family"], "start_distance": float(row["start_distance"]), "T_ramp_s": float(row["T_ramp_s"]),
        "eta_const_at_t_pred": bool(row["eta_const_at_t_pred"]),
        "eta_pred": float(row["eta_pred"]), "eta_onset_cross": float(row["eta_onset_cross"]),
        "eta_err_signed": float(row["eta_onset_cross"] - row["eta_pred"]), "err_steps": float(row["match_err_steps"]),
        "t_pred_s": tp, "onset_cross_s": tc, "time_err_s_signed": tc - tp, "onset_vs_t_pred": "earlier" if tc < tp else "later" if tc > tp else "equal",
        "A4_step_in_s_at_t_pred": None if tol_tau is None else float(tau_to_s(tol_tau, tau_ms)),
        "eta_rate_per_s_at_t_pred": None if tol_tau is None else h / float(tau_to_s(tol_tau, tau_ms)),
    }
    win = decade_window(env, i_c, thr)
    if win is None or win[1] - win[0] < 2:
        out.update(growth_window_s=None, growth_rate_per_tau=None, n_window=0)
    else:
        g = growth_rate_per_tau(t_s, env, win[0], win[1], tau_ms)
        mre, re_c = mean_re_lambda(cfg, arr, win[0], win[1])
        out.update(growth_window_s=[float(t_s[win[0]]), float(t_s[win[1]])], n_window=int(win[1] - win[0] + 1), growth_rate_per_tau=g,
                   mean_re_lambda_over_window=mre, re_lambda_at_crossing=re_c, growth_over_mean_re_lambda=g / mre if mre else None)
    tdt = cfg["model"]["tau_d_ms"] / cfg["model"]["tau_ms"]
    out["re_lambda_at_t_pred_eta"] = EE.leading_re(float(arr["eta"][i_p]), float(arr["J"][i_p]), float(arr["Delta"][i_p]), tdt)
    # predicted amplitude at the observed crossing (delta0 exp(I(t_c))) against the threshold the envelope actually reached
    Ic = gain_at(t, re, I, s_to_tau(tc, tau_ms))
    amp = float(row["delta0"]) * math.exp(Ic)
    out.update(I_at_cross=Ic, pred_amplitude_at_cross=amp, threshold=thr, ln_threshold_over_pred_amp=math.log(thr / amp),
               implied_time_shift_s=None if out.get("growth_rate_per_tau") in (None, 0) else float(tau_to_s(math.log(thr / amp) / out["growth_rate_per_tau"], tau_ms)))
    out["state_vs_quasi_static_fp"] = {k: fp_distance(cfg, arr, i) for k, i in (("t_on", i_on), ("t_pred", i_p), ("t_cross", i_c))}
    out["envelope_at"] = {"t_on": float(env[i_on]), "t_pred": float(env[i_p]), "t_cross": float(env[i_c])}
    return out


# ---- Radau --------------------------------------------------------------------------------------------------------
def solver_run(cfg, arr, row, thr, h, bands=4, above_plateau=100.0, pred=None):
    """Onset, delay and the pre-onset envelope trajectory of one noise-free run.

    The stored v is float64 and sits near -0.59, so its resolution is about 1e-16 and the band-pass envelope of v has a floor near 1e-15 once the
    kicked amplitude has decayed below it: the 'plateau' (median and 99th percentile of the envelope from t_on + 1 s to the midpoint of t_on and the
    crossing) is reported instead of a minimum that is a rounding artefact (the raw minimum, which may be exactly 0, is reported too). Growth is
    fitted only above above_plateau x plateau_p99, in bands of equal ln(envelope) up to the threshold."""
    fs = 1000.0 / cfg["solver"]["dt_out_ms"]
    t_s = arr["t_ms"] / 1000.0
    env = M.envelope(arr["v"], fs, M.G_BAND)
    tau_ms = cfg["model"]["tau_ms"]
    i_on, i_c = int(round(float(row["t_on_s"]) * fs)), int(round(float(row["onset_cross_s"]) * fs))
    seg = env[i_on:i_c + 1]
    i_min = i_on + int(np.argmin(seg))
    i_p0, i_p1 = i_on + int(round(1.0 * fs)), i_on + (i_c - i_on) // 2
    plat = env[i_p0:i_p1 + 1]
    p99 = float(np.percentile(plat, 99))
    lo_env = above_plateau * p99
    below = np.flatnonzero(env[i_p0:i_c] < lo_env)
    i_g = i_p0 + int(below[-1]) + 1 if below.size else i_p0
    edges = np.linspace(math.log(lo_env), math.log(thr), bands + 1)
    lenv = np.log(np.maximum(env[i_g:i_c + 1], 1e-300))
    grow = []
    for b in range(bands):
        sel = np.flatnonzero((lenv >= edges[b]) & (lenv <= edges[b + 1]))
        if sel.size < 3:
            grow.append(None)
            continue
        a0, a1 = i_g + int(sel[0]), i_g + int(sel[-1])
        mre, _ = mean_re_lambda(cfg, arr, a0, a1)
        grow.append({"env_from": float(math.exp(edges[b])), "env_to": float(math.exp(edges[b + 1])), "t_from_s": float(t_s[a0]), "t_to_s": float(t_s[a1]),
                     "n": int(a1 - a0 + 1), "rate_per_tau": growth_rate_per_tau(t_s, env, a0, a1, tau_ms), "mean_re_lambda": mre})
    path, t, re, I = pred or EE.path_gain(cfg, h)
    k_min = int(np.argmin(I))
    levels = [10.0 ** e for e in range(int(math.ceil(math.log10(lo_env))), 0)] + [thr]
    vmax = float(np.abs(arr["v"][i_on:i_c + 1]).max())
    eps = float(np.finfo(arr["v"].dtype).eps)
    return {
        "run_id": row["run_id"], "solver": row["solver"], "rtol": float(row["rtol"]), "cls": row["cls"],
        "onset_class_s": float(row["onset_s"]), "onset_cross_s": float(row["onset_cross_s"]), "delay_eta_class": float(row["delay_eta"]),
        "delay_eta_cross": float(row["delay_eta_cross"]), "t_pred_s": float(row["t_pred_s"]), "onset_cross_minus_t_pred_s": float(row["onset_cross_s"] - row["t_pred_s"]),
        "env_min_raw": float(env[i_min]), "t_env_min_raw_s": float(t_s[i_min]), "n_exact_zero_samples_pre_onset": int((seg == 0).sum()),
        "plateau_window_s": [float(t_s[i_p0]), float(t_s[i_p1])], "plateau_median": float(np.median(plat)), "plateau_p99": p99,
        "env_at_t_on": float(env[i_on]), "env_at_t_on_plus_0p5s": float(env[i_on + int(0.5 * fs)]),
        "pred_amp_min_delta0_exp_Imin": float(row["delta0"]) * math.exp(float(row["I_min"])), "I_min": float(row["I_min"]),
        "pred_t_of_I_min_s": float(tau_to_s(t[k_min], tau_ms)),
        "growth_bands_above_plateau": grow, "level_crossing_times_s": level_crossings(env, t_s, i_g, levels),
        "v_dtype": str(arr["v"].dtype), "v_eps_relative": eps, "v_abs_max_pre_onset": vmax, "v_resolution_abs": eps * vmax, "plateau_median_over_v_resolution": float(np.median(plat) / (eps * vmax)),
    }


def solver_pair_lags(a, b, tau_ms):
    """Time lag (ms) of run b behind run a at each shared envelope level, and the log-amplitude offset it implies if the local growth rate is the
    band rate of a (lag x rate, in tau): ln(amplitude_a / amplitude_b) at the same time. a, b: solver_run outputs. Diagnostic only."""
    out = []
    rates = {}
    for g in a["growth_bands_above_plateau"]:
        if g:
            rates[(g["env_from"], g["env_to"])] = g["rate_per_tau"]
    for lv, ta in a["level_crossing_times_s"].items():
        tb = b["level_crossing_times_s"].get(lv)
        if ta is None or tb is None:
            continue
        rate = next((r for (lo, hi), r in rates.items() if lo <= float(lv) <= hi * (1 + 1e-9)), None)
        lag_s = tb - ta
        out.append({"level": float(lv), "lag_ms": lag_s * 1000.0, "band_rate_per_tau_a": rate,
                    "implied_ln_amplitude_ratio": None if rate is None else rate * lag_s * 1000.0 / tau_ms})
    return out
