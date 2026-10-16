"""A3: one S2 trajectory through the M2 saddle-node (plan 5.2 A3, 4.3 G1, Table 2.1, D8; MS4 step 4c).

Analysis only: no integration, no plotting, nothing read from disk. Input is one stored S2 series
(t_ms, r, v and the ramp eta_bar on the same grid, as simulate_mf._output writes them) and the A1 fold
value, which is passed in and never recomputed here. Output: jump time, eta_bar at the jump, offset from
the fold, and the G1 envelope-growth fit with the ring class.

JUMP DEFINITION (UNVERIFIED; the plan does not define a jump, DL-108): sliding window of window_s
(default 0.1 s). The jump exists if the largest change of r over any such window, max |r(t + w) - r(t)|,
is at least frac (default 0.5) of the range of r over the record. A smooth quasi-static ramp changes
r by a small part of its range in 0.1 s, a saddle-node jump by most of it. Jump time = time of the
largest single-sample change |r[i+1] - r[i]| inside the winning window (t[i+1] is reported). eta_bar at
the jump = the ramp value at that time. The window, the fraction and the time convention are our choices.
The direction (sign of the change in r) is returned. If no window reaches the fraction: class "no_jump".

RING AND G1 (D8, Table 2.1): the fit signal is v, band-passed in G (default 25 to 100 Hz, DL-107 (b)).
M2 has no amplitude threshold (CP17), so the fit window starts at the first sample counted in G: the
post-jump record starts at the jump time, and surge_metrics.envelope_growth runs on it with threshold 0,
for the first n_cycles (10) of unwrapped phase or the record end. Class "damped" only if the fitted rate
is negative by more than 2 standard errors (rate < -2 se); "non_damped" otherwise; "undetermined" when
the fit has fewer than 3 samples. cycles_fit is the number of cycles the fit window spans.
Caveats inherited from surge_metrics: the plain OLS SE is too small (DL-062) and the step-onset filter
bias distorts the rate magnitude, not the sign (DL-073).
"""
from __future__ import annotations

import numpy as np

from .surge_metrics import envelope_growth

JUMP_WINDOW_S = 0.1       # UNVERIFIED (DL-108)
JUMP_FRAC = 0.5           # UNVERIFIED (DL-108)
A1_STEP = 0.05            # one A1 grid cell in eta_bar (DL-107 (a)); the caller may also pass 0.025


def _fs(t_s):
    dt = np.diff(t_s)
    if dt.size == 0 or not np.allclose(dt, dt[0], rtol=1e-6, atol=0.0):
        raise ValueError("the series must be on a uniform time grid")
    return 1.0 / dt[0]


def detect_jump(t_s, r, eta, window_s=JUMP_WINDOW_S, frac=JUMP_FRAC):
    """Jump of r (definition in the module docstring). Returns a dict: jump (bool), index, t_jump_s,
    eta_jump, direction (+1 up, -1 down, 0 if none), change_frac (largest window change / range of r)."""
    t_s, r, eta = (np.asarray(x, float) for x in (t_s, r, eta))
    out = {"jump": False, "index": -1, "t_jump_s": np.nan, "eta_jump": np.nan, "direction": 0,
           "change_frac": 0.0}
    w = max(1, int(round(window_s * _fs(t_s))))
    rng = r.max() - r.min()
    if r.size <= w or rng <= 0:
        return out
    win = r[w:] - r[:-w]
    k = int(np.argmax(np.abs(win)))
    out["change_frac"] = float(abs(win[k]) / rng)
    if out["change_frac"] < frac:
        return out
    step = np.diff(r[k:k + w + 1])
    i = k + int(np.argmax(np.abs(step))) + 1
    out.update(jump=True, index=i, t_jump_s=float(t_s[i]), eta_jump=float(eta[i]),
               direction=int(np.sign(win[k])))
    return out


def ring_growth(t_s, v, i0, band, n_cycles=10):
    """G1 envelope-growth fit of v from sample i0 (threshold 0: no amplitude threshold in M2, CP17)."""
    t_s = np.asarray(t_s, float)
    g = envelope_growth(np.asarray(v, float)[i0:], _fs(t_s), band, 0.0, n_cycles)
    g["t_start"] = float(t_s[i0]) + g["t_start"]
    return g


def classify_ring(rate, se):
    """D8: 'damped' only if rate is negative by more than 2 SE; else 'non_damped'."""
    if not (np.isfinite(rate) and np.isfinite(se)):
        return "undetermined"
    return "damped" if rate < -2.0 * se else "non_damped"


def analyse_trajectory(t_ms, r, v, eta, fold_eta, band=(25.0, 100.0), *, step=A1_STEP,
                       window_s=JUMP_WINDOW_S, frac=JUMP_FRAC, n_cycles=10):
    """One S2 trajectory -> dict with jump, t_jump_s, eta_jump, direction, offset (eta_jump - fold_eta),
    offset_steps (offset / step), step, rate, se, cycles_fit, n_fit, ring_class.
    ring_class is 'no_jump' when no jump is found (then the fit fields are nan)."""
    t_s = np.asarray(t_ms, float) * 1e-3
    j = detect_jump(t_s, r, eta, window_s, frac)
    out = {"jump": j["jump"], "t_jump_s": j["t_jump_s"], "eta_jump": j["eta_jump"],
           "direction": j["direction"], "change_frac": j["change_frac"], "fold_eta": float(fold_eta),
           "step": float(step), "offset": np.nan, "offset_steps": np.nan,
           "rate": np.nan, "se": np.nan, "cycles_fit": 0.0, "n_fit": 0, "ring_class": "no_jump"}
    if not j["jump"]:
        return out
    out["offset"] = j["eta_jump"] - float(fold_eta)
    out["offset_steps"] = out["offset"] / step
    g = ring_growth(t_s, v, j["index"], band, n_cycles)
    out.update(rate=g["rate"], se=g["se"], cycles_fit=g["cycles"], n_fit=g["n"],
               ring_class=classify_ring(g["rate"], g["se"]))
    return out
