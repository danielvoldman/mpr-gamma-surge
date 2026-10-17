"""Candidate fixes for the D8 damped / non-damped estimator (MS7 7g2, inserted by owner ruling; DL-153).

STUDY MODULE. Nothing here is a live code path: surge_metrics.PlanD8Estimator stays the default and its wording
(fit from the threshold crossing over the first 10 cycles, damped only if the rate is negative by more than 2 SE)
is not changed. A candidate plugs into the classifier only through the D8Estimator interface, inside the study.

Every candidate is UNVERIFIED (the Technical Plan defines none of them). Four independent choices:

  edge   how the periodic-Hilbert wrap (DL-140 finding 1) is removed, without changing the band or the filter:
         "none"  the plan: filter and Hilbert on the record as given (periodic);
         "zero"  zero-pad both ends by PAD_S before the filter and the Hilbert transform, crop afterwards;
         "odd"   odd reflection about the end values, PAD_S each end, then crop (continuous at the junction).
  shift  fit start: SHIFT_PERIODS lower-band-edge periods (1 / band[0] each, 40 ms at 25 Hz) after the threshold
         crossing (0 = the plan); the 10-cycle window is counted from the shifted start.
  minwin minimum-window rule: a window spanning fewer than MINWIN_CYCLES cycles gives no call (nan, so
         non-damped by the plan's own nan convention); 0 = the plan.
  se     "plain"  the plan's OLS standard error of the slope;
         "ar1"    plain SE times sqrt((1 + phi) / (1 - phi)), phi the lag-1 autocorrelation of the OLS residuals
                  (effective sample size n (1 - phi) / (1 + phi), clipped phi in [0, PHI_MAX]);
         "cycle"  one envelope sample per cycle (first sample at each 2 pi of unwrapped phase from the window start),
                  slope and plain OLS SE on those samples (at least 3).

Not tested, because each needs a free parameter the plan does not give: Newey-West (lag), block bootstrap (block
length). Listed in DL-153.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np
from scipy import signal

from . import surge_metrics as M

PAD_S = 1.0               # edge padding, ours (the A_ref edge convention of 1 s, DL-139)
SHIFT_LEVELS = (0, 1, 2)  # lower-band-edge periods after the crossing
MINWIN_LEVELS = (0.0, 5.0)  # cycles; 5 is the plan's own short-ring length (A8 5-cycle ring, RB10 min_cycles)
EDGES = ("none", "zero", "odd")
SES = ("plain", "ar1", "cycle")
PHI_MAX = 0.999


@dataclass(frozen=True)
class Candidate:
    edge: str = "none"
    shift: int = 0
    minwin: float = 0.0
    se: str = "plain"

    @property
    def id(self):
        return f"E{self.edge[0]}-S{self.shift}-M{int(self.minwin)}-{self.se}"

    @property
    def is_plan(self):
        return self == PLAN


PLAN = Candidate()


def all_candidates():
    """The full grid (3 x 3 x 2 x 3 = 54), the plan first."""
    return [Candidate(e, s, m, se) for e, s, m, se in itertools.product(EDGES, SHIFT_LEVELS, MINWIN_LEVELS, SES)]


def single_factor_candidates():
    """The plan plus every candidate that differs from it in exactly one choice (7 + plan)."""
    return [c for c in all_candidates() if sum([c.edge != "none", c.shift != 0, c.minwin != 0.0, c.se != "plain"]) <= 1]


def analytic(v, fs, band, edge="none"):
    """Analytic signal of the zero-phase band-passed v (the pipeline's band and filter), with the chosen edge treatment."""
    v = np.asarray(v, float)
    if edge == "none":
        return M._analytic(v, fs, band)
    p = int(round(PAD_S * fs))
    if edge == "zero":
        vp = np.pad(v, p, mode="constant")
    elif edge == "odd":
        vp = np.pad(v, p, mode="reflect", reflect_type="odd")
    else:
        raise ValueError("edge must be none, zero or odd")
    return M._analytic(vp, fs, band)[p:-p]


def _ols(t, y):
    tc = t - t.mean()
    sxx = np.sum(tc**2)
    rate = np.sum(tc * (y - y.mean())) / sxx
    resid = y - y.mean() - rate * tc
    se = np.sqrt(np.sum(resid**2) / (y.size - 2) / sxx)
    return rate, se, resid


def window(z, fs, band, threshold, shift, n_cycles=M.MIN_CYCLES):
    """(env, phase, a, stop) of the fit window or None: first run at or above the threshold, start moved `shift`
    lower-band-edge periods later, ending after n_cycles of unwrapped phase from the new start or at the run end."""
    env = np.abs(z)
    runs = M._runs_at_or_above(env, threshold)
    if not runs:
        return None
    a, b = runs[0]
    a = a + int(np.ceil(shift * fs / band[0] - 1e-9))
    if a >= b:
        return None
    phase = np.unwrap(np.angle(z))
    done = np.flatnonzero(phase[a:b] - phase[a] >= 2 * np.pi * n_cycles)
    stop = a + done[0] + 1 if done.size else b
    return env, phase, a, stop


def fit_window(z, fs, band, threshold, shift, minwin, se_kinds=SES):
    """Rate, SE (per kind) and cycles of one window. Returns {se_kind: (rate, se, cycles)}; nan where undefined.
    Undefined (nan, hence non-damped) when fewer than 3 samples are fitted or the window spans fewer than minwin cycles."""
    nan = (np.nan, np.nan, 0.0)
    w = window(z, fs, band, threshold, shift)
    if w is None:
        return {k: nan for k in se_kinds}
    env, phase, a, stop = w
    cyc = float((phase[stop - 1] - phase[a]) / (2 * np.pi))
    out = {k: (np.nan, np.nan, cyc) for k in se_kinds}
    if stop - a < 3 or cyc < minwin:
        return out
    t = np.arange(a, stop) / fs
    y = np.log(env[a:stop])
    rate, se, resid = _ols(t, y)
    if "plain" in out:
        out["plain"] = (rate, se, cyc)
    if "ar1" in out:
        den = np.sum(resid**2)
        phi = float(np.sum(resid[1:] * resid[:-1]) / den) if den > 0 else 0.0
        phi = min(max(phi, 0.0), PHI_MAX)
        out["ar1"] = (rate, se * np.sqrt((1 + phi) / (1 - phi)), cyc)
    if "cycle" in out:
        k = np.floor((phase[a:stop] - phase[a]) / (2 * np.pi)).astype(int)
        first = np.flatnonzero(np.diff(np.concatenate(([-1], k))) > 0)       # first sample of each cycle index
        if first.size >= 3:
            r2, s2, _ = _ols(t[first], y[first])
            out["cycle"] = (r2, s2, cyc)
    return out


def fit_all(v, fs, band, threshold, cands):
    """{candidate id: (rate, se, cycles)} for a list of candidates, sharing the analytic signal and the windows."""
    res = {}
    zs = {}
    wins = {}
    for c in cands:
        if c.edge not in zs:
            zs[c.edge] = analytic(v, fs, band, c.edge)
        key = (c.edge, c.shift, c.minwin)
        if key not in wins:
            wins[key] = fit_window(zs[c.edge], fs, band, threshold, c.shift, c.minwin)
        res[c.id] = wins[key][c.se]
    return res


class CandidateD8:
    """A candidate behind the D8Estimator interface (call(v, fs, band, threshold) -> D8Result)."""

    def __init__(self, cand: Candidate):
        self.cand = cand
        self.label = f"D8 candidate {cand.id} (study, UNVERIFIED)"

    def __call__(self, v, fs, band, threshold):
        c = self.cand
        z = analytic(v, fs, band, c.edge)
        w = window(z, fs, band, threshold, c.shift)
        rate, se, cyc = fit_window(z, fs, band, threshold, c.shift, c.minwin, (c.se,))[c.se]
        n = 0 if w is None else w[3] - w[2]
        t0 = float("nan") if w is None else w[2] / fs
        damped = bool(rate < -M.D8_SE_MULT * se)          # nan compares False: non-damped
        return M.D8Result(damped, float(rate), float(se), int(n), float(cyc), t0)
