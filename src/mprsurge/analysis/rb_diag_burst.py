"""8f5 stored-data diagnosis of the deterministic pre-onset burst (DL-196 to DL-198). Pure helpers; EXPLORATORY, no gate reads them.

A "burst" is a contiguous run of samples of the 25 to 100 Hz band-pass Hilbert envelope (surge_metrics.envelope, the one the raw crossing uses)
above BURST_LEVEL = 1e-12 (the level the reviewer named). A burst is "pre-onset" if it ends before the raw first crossing of the threshold; the
segment that contains the crossing is the growth segment. A path breakpoint (ramps.Path.breakpoints, the corners the integrator restarts at)
"has a burst" if a pre-onset segment contains it. No window width is assumed: association is containment in the segment.
The burst-seeded prediction reuses entry_exit (leading Re lambda at the fixed point of M3 at (eta(t), J(t)), trapezoid in I) unchanged and only
moves the seed: amplitude A at time t_seed, then A exp(I(t) - I(t_seed)) = threshold.
"""
from __future__ import annotations

import math

import numpy as np

from . import entry_exit as EE
from ..units import s_to_tau, tau_to_s

LABEL = "exploratory"
BURST_LEVEL = 1e-12


def segments(env, t_s, level=BURST_LEVEL):
    """Contiguous runs of env > level: list of dicts (start_s, end_s, peak_s, peak, n)."""
    m = np.asarray(env) > level
    d = np.diff(np.concatenate([[0], m.astype(int), [0]]))
    out = []
    for a, b in zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1):
        k = a + int(np.argmax(env[a:b + 1]))
        out.append({"start_s": float(t_s[a]), "end_s": float(t_s[b]), "peak_s": float(t_s[k]), "peak": float(env[k]), "n": int(b - a + 1)})
    return out


def breakpoints_s(path, tau_ms):
    """Corner times of the path in seconds."""
    return [float(tau_to_s(b, tau_ms)) for b in path.breakpoints]


def classify_segments(segs, onset_s, bps_s):
    """Each segment gets: kind 'growth' if it contains the onset crossing, 'pre' if it ends before it, 'post' otherwise; breakpoints it contains;
    peak offset to each of them (peak_s - b)."""
    out = []
    for s in segs:
        kind = "growth" if s["start_s"] <= onset_s <= s["end_s"] else ("pre" if s["end_s"] < onset_s else "post")
        inside = [b for b in bps_s if s["start_s"] <= b <= s["end_s"]]
        out.append({**s, "kind": kind, "breakpoints_inside_s": inside, "peak_minus_breakpoint_s": [s["peak_s"] - b for b in inside]})
    return out


def segment_at(classified, b):
    """The classified segment containing breakpoint time b (first), or None."""
    for s in classified:
        if s["start_s"] <= b <= s["end_s"]:
            return s
    return None


def implied_onset_shift_s(ratio, growth_rate_per_s):
    """Onset shift (s, positive = later) if the seed amplitude were multiplied by ratio and the envelope grew at growth_rate_per_s: -ln(ratio) / rate."""
    return -math.log(ratio) / growth_rate_per_s


def net_gain(t, re, I, t_from_s, t_to_s, tau_ms):
    """I(t_to) - I(t_from) on the entry_exit node arrays (t in tau), linear in I between nodes, constant final Re lambda after the last node."""
    def at(tq):
        return float(I[-1] + re[-1] * (tq - t[-1])) if tq > t[-1] else float(np.interp(tq, t, I))
    return at(s_to_tau(t_to_s, tau_ms)) - at(s_to_tau(t_from_s, tau_ms))


def log10_seed_needed(threshold, dI):
    """log10 of the amplitude at the seed time that grows to the threshold given net gain dI: log10(threshold) - dI / ln 10."""
    return math.log10(threshold) - dI / math.log(10.0)


def seed_prediction(cfg, path, t, re, I, t_seed_s, amp, threshold, h):
    """Entry-exit prediction with seed amplitude amp at time t_seed_s (s): first t after t_seed with amp exp(I(t) - I(t_seed)) = threshold.

    Returns dict: t_pred_s (None if never), eta_pred, delay_eta (eta_pred - eta_H), in_run, eta_const_at_t_pred. Times of the node arrays are tau."""
    tau_ms = cfg["model"]["tau_ms"]
    ts = s_to_tau(t_seed_s, tau_ms)
    keep = t > ts
    tt = np.concatenate([[ts], t[keep]])
    ii = np.concatenate([[float(np.interp(ts, t, I))], I[keep]])
    rr = np.concatenate([[float(np.interp(ts, t, re))], re[keep]])
    ii = ii - ii[0]
    tp, _ = EE.t_pred_from(tt, rr, ii, amp, threshold)
    if tp is None:
        return {"t_pred_s": None, "eta_pred": None, "delay_eta": None, "in_run": False, "eta_const_at_t_pred": None}
    eta_pred = float(path.eta(tp))
    hold_end = path.t_ramp_end + s_to_tau(cfg["durations"]["hold_s"], tau_ms)
    d = 1e-3 * path.t_ramp_end
    rate = abs(float(path.eta(tp + d)) - float(path.eta(tp - d))) / (2.0 * d)
    return {"t_pred_s": float(tau_to_s(tp, tau_ms)), "eta_pred": eta_pred, "delay_eta": eta_pred - cfg["path"]["eta_H"], "in_run": bool(tp <= hold_end),
            "eta_const_at_t_pred": bool(rate <= 1e-12)}


def effective_seed(threshold, dI):
    """Seed amplitude at t_on that reaches the threshold at the observed crossing given net gain dI = I(t_c) - I(t_on): threshold exp(-dI).
    With threshold = 0.1 A_ref this is 0.1 x A_ref x exp(-integral of Re lambda from t_on to t_c)."""
    return threshold * math.exp(-dI)


def bit_equal_arrays(a, b):
    """Per-key np.array_equal of two npz dicts; (all equal, {key: bool}); keys must be the same set."""
    if set(a) != set(b):
        return False, {"keys_differ": True}
    per = {k: bool(np.array_equal(a[k], b[k])) for k in sorted(a)}
    return all(per.values()), per
