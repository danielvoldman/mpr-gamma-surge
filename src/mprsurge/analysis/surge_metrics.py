"""Surge metrics, core (plan Table 2.1, 5.2 A8; DL-062). Analysis only: no integration, no plotting.

Core built at MS1: spectrogram_v, band_power, envelope, envelope_growth, count_cycles. Classes and metrics
added at MS7 7c (bottom of the file; DL-140). Times are in seconds, frequencies in Hz, signals sampled at
fs (1 kHz in the plan). The amplitude threshold is an argument: the one absolute 0.1 x A_ref from
analysis.a_ref (DL-139).

Edge note: the zero-phase filter and the Hilbert transform distort the first and last few filter
lengths of a record; callers discard or pad them (modes N and D already discard 2 s before t = 0).
"""
from __future__ import annotations

import numpy as np
from scipy import signal

FILTER_ORDER = 4          # DL-062 (zero-phase Butterworth band-pass, order 4)


def spectrogram_v(v, fs, window_s, step_s, t0=0.0):
    """Hann spectrogram of v: one-sided periodogram per window, linear detrend per window (Table 2.1).

    Returns (t, f, S): t the window centres (s, offset by t0), f in Hz, S the power spectral
    density, shape (len(f), len(t)). The step is rounded to whole samples.
    """
    v = np.asarray(v, float)
    nper = int(round(window_s * fs))
    step = max(1, int(round(step_s * fs)))
    if nper < 2 or nper > v.size or step > nper:
        raise ValueError("window must be at least 2 samples, fit in the record, and be at least the step")
    f, t, S = signal.spectrogram(v, fs=fs, window="hann", nperseg=nper, noverlap=nper - step,
                                 detrend="linear", scaling="density", mode="psd")
    return t + t0, f, S


def band_power(S, f, band):
    """Power in a band: the PSD bins with lo <= f < hi, summed and multiplied by the bin width (DL-062).

    S has frequency on axis 0 (as returned by spectrogram_v); returns one value per window.
    Whether the upper edge is inclusive is not sourced (UNVERIFIED); bins at an exact edge are rare.
    """
    f = np.asarray(f, float)
    lo, hi = band
    sel = (f >= lo) & (f < hi)
    return np.asarray(S)[sel].sum(axis=0) * (f[1] - f[0])


def _analytic(v, fs, band):
    sos = signal.butter(FILTER_ORDER, band, btype="bandpass", fs=fs, output="sos")
    return signal.hilbert(signal.sosfiltfilt(sos, np.asarray(v, float)))


def envelope(v, fs, band):
    """Hilbert envelope of v after a zero-phase Butterworth band-pass of the given band (DL-062)."""
    return np.abs(_analytic(v, fs, band))


def _runs_at_or_above(env, threshold):
    """(start, stop) index pairs, stop exclusive, of the runs where env >= threshold."""
    above = np.concatenate(([False], np.asarray(env) >= threshold, [False]))
    d = np.diff(above.astype(np.int8))
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


def count_cycles(v, fs, band, threshold):
    """Cycles in the longest run where the envelope is at or above threshold (DL-062).

    Cycles = change of the unwrapped analytic phase over the run / 2 pi. Returns 0.0 if the
    envelope never reaches the threshold. Merging runs separated by short gaps is a classifier
    rule and is not done here.
    """
    z = _analytic(v, fs, band)
    runs = _runs_at_or_above(np.abs(z), threshold)
    if not runs:
        return 0.0
    phase = np.unwrap(np.angle(z))
    return max((phase[b - 1] - phase[a]) / (2 * np.pi) for a, b in runs)


def envelope_growth(v, fs, band, threshold, n_cycles=10):
    """Growth rate of the envelope: OLS slope of ln(envelope) over the first n_cycles from the
    first threshold crossing (Table 2.1, D8; estimator DL-062).

    The fit window starts at the first sample with envelope >= threshold and ends after n_cycles
    of unwrapped phase, or where the envelope falls below the threshold or the record ends,
    whichever comes first. threshold = 0 starts at the first sample (as for K7, ms1_plan).
    Returns a dict: rate (1/s), se (plain OLS standard error of the slope, 1/s), n (samples fitted),
    cycles (cycles spanned by the window), t_start (s). rate and se are nan when fewer than 3
    samples are fitted or no sample reaches the threshold.

    CAVEAT (DL-062): the envelope is smooth and autocorrelated, so the plain OLS standard error is
    too small and "negative by more than 2 SE" declares damping too easily. Revisit at MS7.
    """
    z = _analytic(v, fs, band)
    env = np.abs(z)
    out = {"rate": np.nan, "se": np.nan, "n": 0, "cycles": 0.0, "t_start": np.nan}
    runs = _runs_at_or_above(env, threshold)
    if not runs:
        return out
    a, b = runs[0]
    phase = np.unwrap(np.angle(z))
    done = np.flatnonzero(phase[a:b] - phase[a] >= 2 * np.pi * n_cycles)
    stop = a + done[0] + 1 if done.size else b
    seg = np.log(env[a:stop])
    t = np.arange(a, stop) / fs
    out.update(n=stop - a, cycles=(phase[stop - 1] - phase[a]) / (2 * np.pi), t_start=a / fs)
    if stop - a < 3:
        return out
    tc = t - t.mean()
    sxx = np.sum(tc**2)
    rate = np.sum(tc * (seg - seg.mean())) / sxx
    resid = seg - seg.mean() - rate * tc
    out["rate"] = rate
    out["se"] = np.sqrt(np.sum(resid**2) / (seg.size - 2) / sxx)
    return out


# ---------------------------------------------------------------------------------------------------------------
# MS7 7c: classes and metrics (Table 2.1, A8, A9 label (f)). Analysis only.
#
# Only what Table 2.1 states is fixed here. Every definition the plan leaves open is either a field of
# `Conventions` (a named working convention, UNVERIFIED, listed for the 7h sign-off in DL-140) or is not
# implemented (broadband flag, post-surge rate). The damped / non-damped call (D8) is behind `D8Estimator`; the
# class logic only reads `.damped`, so a later ruling swaps the estimator without touching the classes.
# ---------------------------------------------------------------------------------------------------------------
from dataclasses import dataclass, field
from typing import Optional, Protocol

G_BAND = (25.0, 100.0)            # D2
TOTAL_BAND = (1.0, 150.0)         # D3
FACTOR_REL = 2.0                  # D6 (relative power test)
FACTOR_ABS = 2.0                  # D6 (absolute power test)
MIN_CYCLES = 10                   # D8
BASELINE_S = 5.0                  # D5 / CP14
COLLAPSE_FRACTION = 0.1           # D9
D8_SE_MULT = 2.0                  # D8: damped only if the rate is negative by more than 2 SE
D8_PROVISIONAL = "provisional (D8 open, DL-137)"
CONVENTION_LABEL = "working convention, UNVERIFIED, open for 7h sign-off (DL-140)"

MODE_N_CLASSES = ("S+", "S-rel", "S-abs", "S-sus", "NS")
MODE_D_CLASSES = ("D-tr", "D-sus", "D-none")
FAILED = "failed"                 # a failed run is labelled failed, not NS (A9, section 10.4)
SURGE_CLASSES = ("D-tr", "S+", "S-rel", "S-abs")
_EPS = 1e-9


def window_for_ramp(T_ramp_s):
    """(W, step) in s: W = 2, step 1 for T_ramp >= 60 s, else W = max(0.2, T_ramp / 30), step W / 2 (D4)."""
    if not (T_ramp_s > 0 and np.isfinite(T_ramp_s)):
        raise ValueError("T_ramp must be positive and finite")
    if T_ramp_s >= 60.0:
        return 2.0, 1.0
    w = max(0.2, T_ramp_s / 30.0)
    return w, w / 2.0


@dataclass(frozen=True)
class Conventions:
    """Classifier definitions the plan leaves open. The default is the plain reading, labelled CONVENTION_LABEL;
    nothing here is a ruling.

    onset: "centre" (centre of the first flagged window) or "start" (its start). Mode N only; the mode-D onset is
           the envelope crossing, which Table 2.1 defines.
    """
    onset: str = "centre"

    def __post_init__(self):
        if self.onset not in ("centre", "start"):
            raise ValueError("onset must be 'centre' or 'start'")


@dataclass(frozen=True)
class D8Result:
    damped: bool
    rate: float
    se: float
    n: int
    cycles: float
    t_start: float


class D8Estimator(Protocol):
    """The one interface the classes use for the damped / non-damped call. Replace the object, not the classes."""
    def __call__(self, v, fs, band, threshold) -> D8Result: ...


class PlanD8Estimator:
    """D8 as Table 2.1 words it: ln envelope fitted from the threshold crossing over the first 10 cycles (DL-062
    estimator: zero-phase Butterworth band-pass, plain OLS SE); damped only if the rate is negative by more than
    2 SE, otherwise non-damped (also when the fit is undefined). DL-062 and DL-073 caveats apply and DL-137 found
    the acceptance numbers not met, so every class that used it is provisional (D8 open, DL-137)."""
    label = D8_PROVISIONAL

    def __call__(self, v, fs, band, threshold) -> D8Result:
        g = envelope_growth(v, fs, band, threshold, n_cycles=MIN_CYCLES)
        damped = bool(g["rate"] < -D8_SE_MULT * g["se"])      # nan compares False: non-damped
        return D8Result(damped, g["rate"], g["se"], g["n"], g["cycles"], g["t_start"])


PLAN_D8 = PlanD8Estimator()


def is_surge_class(cls):
    """A surge class is D-tr in mode D, or S+, S-rel or S-abs in mode N (Table 2.1)."""
    return cls in SURGE_CLASSES


def classes_agree(cls_d, cls_n):
    """Noisy and deterministic runs agree when D-tr meets a surge class, D-sus meets S-sus, D-none meets NS."""
    if cls_d == "D-tr":
        return cls_n in ("S+", "S-rel", "S-abs")
    if cls_d == "D-sus":
        return cls_n == "S-sus"
    if cls_d == "D-none":
        return cls_n == "NS"
    return False


@dataclass(frozen=True)
class Episode:
    onset_s: float
    end_s: float
    duration_s: float
    cycles: float
    terminated: bool
    f_pk_hz: float
    peak_p_g: float
    peak_rho: float


@dataclass(frozen=True)
class ClassResult:
    cls: str
    mode: str
    episode: Optional[Episode] = None     # mode D: the episode; mode N: the earliest qualifying episode of either test
    rel: Optional[Episode] = None         # mode N only
    abs: Optional[Episode] = None         # mode N only
    d8: Optional[D8Result] = None         # None when no D8 call was needed
    reason: str = ""
    label_f: bool = False                 # A9 failure label (f), mode D only
    provisional: Optional[str] = None     # D8_PROVISIONAL when the class depended on the D8 call
    conventions: Conventions = field(default_factory=Conventions)
    broadband: Optional[bool] = None      # mode N S-abs only: the rise peaks outside G (O11, F-6); None for other classes
    rise_peak_hz: Optional[float] = None  # the frequency of that argmax (S-abs only)


def _finite(v):
    v = np.asarray(v, float)
    return v.ndim == 1 and v.size > 0 and bool(np.all(np.isfinite(v)))


def _window_series(v, fs, W, step, band=G_BAND, total=TOTAL_BAND):
    """Per-window centre, P_G, P_total, P_non-G, peak frequency in G (argmax of the PSD in G, resolution 1/W)."""
    tc, f, S = spectrogram_v(v, fs, W, step)
    p_g = band_power(S, f, band)
    p_tot = band_power(S, f, total)
    sel = (f >= band[0]) & (f < band[1])
    fpk = f[sel][np.argmax(np.asarray(S)[sel], axis=0)]
    return tc, p_g, p_tot, p_tot - p_g, fpk


def _runs(flags):
    flags = np.asarray(flags, bool)
    d = np.diff(np.concatenate(([0], flags.astype(np.int8), [0])))
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1))      # inclusive ends


def _merge_runs(runs, gap_limit_s, step_s):
    """Merge runs whose gap (unflagged windows x step) is shorter than gap_limit_s ('shorter than one window')."""
    out = []
    for a, b in runs:
        if out and (a - out[-1][1] - 1) * step_s < gap_limit_s - _EPS:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


def baseline_windows(tc, W, t_on, baseline_s=BASELINE_S):
    """Boolean mask of windows lying wholly inside [t_on - baseline_s, t_on] (Table 2.1 baseline)."""
    lo, hi = t_on - baseline_s, t_on
    return (tc - W / 2 >= lo - _EPS) & (tc + W / 2 <= hi + _EPS)


def baseline_rho(v, fs, t_on, T_ramp_s, baseline_s=BASELINE_S):
    """Baseline rho = P_G / P_total (total 1 to 150 Hz), mean over the baseline windows; reported, not a test.
    The mean over windows is a working convention (CONVENTION_LABEL)."""
    W, step = window_for_ramp(T_ramp_s)
    tc, p_g, p_tot, _, _ = _window_series(v, fs, W, step)
    m = baseline_windows(tc, W, t_on, baseline_s)
    if not m.any():
        raise ValueError("baseline too short for one window")
    return float(np.mean(p_g[m] / p_tot[m]))


def classify_mode_n(v, fs, t_on, T_ramp_s, threshold, d8: D8Estimator = PLAN_D8, conv: Conventions = Conventions(),
                    factor_rel=FACTOR_REL, factor_abs=FACTOR_ABS, min_cycles=MIN_CYCLES, band=G_BAND,
                    baseline_s=BASELINE_S, window=None):
    """Mode N class (Table 2.1): S+, S-rel, S-abs, S-sus or NS; non-finite input gives 'failed'.

    v starts at t = 0 (the 2 s discard is already removed). Relative test P_G/P_non-G >= factor_rel x its baseline
    value; absolute test P_G >= factor_abs x baseline P_G. A test's episode is a run of passing windows after t_on
    (windows with centre >= t_on), gaps shorter than one window merged, at least `min_cycles` cycles at the
    running peak frequency, and the run must be non-damped by `d8`. `threshold` is the single absolute
    0.1 x A_ref (D7) and is the only amplitude threshold the D8 fit uses (owner constraint; whether that is right
    in mode N is open, DL-140). The D8 fit runs once per record, on v from t_on. `window` overrides (W, step).
    O10 (ruled): S+ needs the relative and absolute episodes to share a flagged window; two qualifying episodes
    that do not overlap give the class of the earlier one. O11 (ruled, F-6): an S-abs result carries `broadband`
    (the rise peaks outside G) and `rise_peak_hz`; no new threshold.
    """
    if not _finite(v):
        return ClassResult(FAILED, "N", reason="non-finite input", conventions=conv)
    v = np.asarray(v, float)
    W, step = window if window is not None else window_for_ramp(T_ramp_s)
    tc, p_g, p_tot, p_ng, fpk = _window_series(v, fs, W, step, band)
    bm = baseline_windows(tc, W, t_on, baseline_s)
    if not bm.any():
        raise ValueError("baseline too short for one window")
    odds = p_g / p_ng
    post = tc >= t_on - _EPS
    flags = {"rel": (odds >= factor_rel * np.mean(odds[bm])) & post,
             "abs": (p_g >= factor_abs * np.mean(p_g[bm])) & post}
    d8_res = [None]

    def d8_call():
        if d8_res[0] is None:
            d8_res[0] = d8(v[int(round(t_on * fs)):], fs, band, threshold)
        return d8_res[0]

    def episode(fl):
        """(Episode, first window, last window) of the first qualifying run, or None."""
        for a, b in _merge_runs(_runs(fl), W, step):
            dur = (b - a + 1) * step
            cyc = dur * float(np.mean(fpk[a:b + 1]))
            if cyc < min_cycles:
                continue
            if d8_call().damped:
                return None
            j = a + int(np.argmax(p_g[a:b + 1]))
            on = tc[a] - (W / 2 if conv.onset == "start" else 0.0)
            ep = Episode(float(on), float(tc[b] + step / 2), dur, cyc,
                         (len(tc) - 1 - b) * step >= W - _EPS,
                         float(fpk[j]), float(p_g[j]), float(p_g[j] / p_tot[j]))
            return ep, a, b, j
        return None

    r_hit, a_hit = episode(flags["rel"]), episode(flags["abs"])
    rel, ab = (r_hit[0] if r_hit else None), (a_hit[0] if a_hit else None)
    found = [e for e in (rel, ab) if e is not None]
    reason = "" if found else "no qualifying episode"
    if any(not e.terminated for e in found):
        cls = "S-sus"
    elif rel and ab:
        # O10 (ruled): S+ needs the two episodes to share a window; otherwise the earlier one defines the class
        if max(r_hit[1], a_hit[1]) <= min(r_hit[2], a_hit[2]):
            cls = "S+"
        else:
            cls = "S-rel" if r_hit[1] <= a_hit[1] else "S-abs"
            reason = "relative and absolute episodes do not overlap in time (O10)"
    elif rel:
        cls = "S-rel"
    elif ab:
        cls = "S-abs"
    else:
        cls = "NS"
    broadband = rise_hz = None
    if cls == "S-abs":
        # O11 (ruled, F-6): broadband when the spectrogram argmax of the rise lies outside G; no new threshold.
        # Rise = peak-power window of the absolute episode minus the mean baseline spectrum, over the total band.
        _, f_all, S_all = spectrogram_v(v, fs, W, step)
        S_all = np.asarray(S_all)
        rise = S_all[:, a_hit[3]] - S_all[:, bm].mean(axis=1)
        tot = (f_all >= TOTAL_BAND[0]) & (f_all < TOTAL_BAND[1])
        rise_hz = float(f_all[tot][np.argmax(rise[tot])])
        broadband = not (band[0] <= rise_hz < band[1])
    first = min(found, key=lambda e: e.onset_s) if found else None
    return ClassResult(cls, "N", first, rel, ab, d8_res[0], reason, broadband=broadband, rise_peak_hz=rise_hz,
                       provisional=D8_PROVISIONAL if d8_res[0] is not None else None, conventions=conv)


def classify_mode_d(v, fs, t_on, T_ramp_s, threshold, d8: D8Estimator = PLAN_D8, min_cycles=MIN_CYCLES, band=G_BAND,
                    inside_a4_region=None, conv: Conventions = Conventions(), window=None):
    """Mode D class (Table 2.1): D-tr, D-sus or D-none; non-finite input gives 'failed'.

    Episode = run, after t_on, of the band-passed Hilbert envelope >= threshold (the single 0.1 x A_ref, D7), gaps
    shorter than one window (D4) merged, at least `min_cycles` cycles of unwrapped phase (the count_cycles measure),
    and the run non-damped by `d8` (fit once per record on v from t_on). The class follows the first qualifying
    episode: D-sus if no gap of one window or more follows it before the record ends, else D-tr. label_f (A9 label
    f) is set on D-none when inside_a4_region is True and the post-onset envelope never reaches the threshold.
    """
    if not _finite(v):
        return ClassResult(FAILED, "D", reason="non-finite input", conventions=conv)
    v = np.asarray(v, float)
    W, step = window if window is not None else window_for_ramp(T_ramp_s)
    z = _analytic(v, fs, band)
    env = np.abs(z)
    phase = np.unwrap(np.angle(z))
    i_on = int(round(t_on * fs))
    runs = [(a + i_on, b + i_on - 1) for a, b in _runs_at_or_above(env[i_on:], threshold)]     # inclusive ends
    gap = int(round(W * fs))
    merged = []
    for a, b in runs:
        if merged and a - merged[-1][1] - 1 < gap:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    d8_res = None
    ep = None
    reason = "envelope never reaches the threshold" if not runs else "no run of the minimum cycles"
    for a, b in merged:
        cyc = (phase[b] - phase[a]) / (2 * np.pi)
        if cyc < min_cycles:
            continue
        d8_res = d8(v[i_on:], fs, band, threshold)
        if d8_res.damped:
            reason = "damped (D8)"
            break
        tc, p_g, p_tot, _, fpk = _window_series(v, fs, W, step, band)
        idx = np.flatnonzero((tc + W / 2 > a / fs) & (tc - W / 2 < (b + 1) / fs))
        j = idx[np.argmax(p_g[idx])] if idx.size else int(np.argmin(np.abs(tc - (a + b) / 2 / fs)))
        ep = Episode(a / fs, b / fs, (b - a + 1) / fs, float(cyc), (len(v) - 1 - b) >= gap,
                     float(fpk[j]), float(p_g[j]), float(p_g[j] / p_tot[j]))
        break
    prov = D8_PROVISIONAL if d8_res is not None else None
    if ep is None:
        lf = bool(inside_a4_region) and not runs
        return ClassResult("D-none", "D", None, None, None, d8_res, reason, lf, prov, conv)
    return ClassResult("D-tr" if ep.terminated else "D-sus", "D", ep, None, None, d8_res, "", False, prov, conv)


def onset_delay(onset_s, t_grid, eta_grid, eta_H):
    """(eta_on, delay) = (eta(onset), eta_on - eta_H): the Table 2.1 delay metric, eta read by linear interpolation."""
    eta_on = float(np.interp(onset_s, t_grid, eta_grid))
    return eta_on, eta_on - float(eta_H)


def j_exit_metrics(end_s, t_grid, J_grid, J_exit_static):
    """(J_exit_run, J_exit_static, exit delay) on P2-based paths: J at the observed episode end, the static value
    from A4, and run minus static. The sign of 'their difference' is not stated in the plan (UNVERIFIED)."""
    j_run = float(np.interp(end_s, t_grid, J_grid))
    return j_run, float(J_exit_static), j_run - float(J_exit_static)


def collapse_time(r, fs, t_on, baseline_s=BASELINE_S, fraction=COLLAPSE_FRACTION):
    """First time at or after t_on with r < fraction x baseline r (D9, paths without a J ramp); None if never.
    Baseline r = mean of r over [t_on - baseline_s, t_on] (working convention, CONVENTION_LABEL)."""
    r = np.asarray(r, float)
    i_on = int(round(t_on * fs))
    i_lo = max(0, int(round((t_on - baseline_s) * fs)))
    if i_on <= i_lo:
        raise ValueError("no baseline samples before t_on")
    below = np.flatnonzero(r[i_on:] < fraction * r[i_lo:i_on].mean())
    return float((i_on + below[0]) / fs) if below.size else None
