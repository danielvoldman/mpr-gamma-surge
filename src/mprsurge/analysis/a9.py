"""A9 failure labels (a) to (f) for cells without a surge class (plan 5.2 A9; ruling M9-12, M9-13; DL-214, DL-216).

PRELIMINARY at 9b: written so that the cost of the labelling can be timed (the analysis part of the D36 check); 9j adds the
regime-map table, the overlays and the checks, and may change nothing here without a decision-log entry. Analysis only.

Rules (M9-12, from A4 and plan numbers only; every reading below is UNVERIFIED where marked):
  (a) Delta above the largest Delta of the map-1 Delta axis with an A4 Hopf point at the cell's (J0, tau_d). None found: (a) applies.
  (b) tau_d outside the interval [min, max] of the map-1 tau_d axis values with an A4 Hopf point at the cell's (J0, Delta). None: (b) applies.
  (c) the A4 Hopf frequency (Im lambda) at the cell's own Hopf point is below 25 Hz (Hz = omega / (2 pi tau); needs a Hopf point).
  (d) time inside the oscillatory region x that frequency is below 10 cycles (needs time inside > 0 and a Hopf point).
  (e) class D-sus or S-sus.
  (f) the classifier's label_f: D-none, the path enters the region (M9-13), and the post-onset envelope never reaches the threshold.
All labels that apply are recorded; the primary label is the first in the order a to f. A failed run is labelled 'failed', not NS.
The A4-region test (M9-13) is: the leading Re lambda along the run's own path is positive somewhere in [t_on, end] (entry_exit.path_gain,
nodes from the A4 grid step); the time inside is the trapezoid-interpolated time with Re lambda > 0.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from .. import config as C
from . import entry_exit as EE
from . import hopf

ORDER = ("a", "b", "c", "d", "e", "f")
F_MIN_HZ = 25.0
MIN_CYCLES = 10.0


@lru_cache(maxsize=1)
def _eta_grid():
    return hopf._grid(hopf.load_a4_params()["grids"]["eta_bar"])


@lru_cache(maxsize=None)
def hopf_point(J0: float, Delta: float, tau_d_ms: float, tau_ms: float = 10.0):
    """The lowest A4 Hopf crossing along eta_bar at (J0, Delta, tau_d), or None: {eta_bar, omega (rad per tau), f_hz}."""
    c = hopf.lowest_eta_hopf(_eta_grid(), J0, Delta, tau_d_ms / tau_ms)
    if c is None:
        return None
    return {"eta_bar": float(c["eta_bar"]), "omega": float(c["omega"]), "f_hz": float(hopf._hz(c["omega"], tau_ms))}


def delta_max(J0: float, tau_d_ms: float, delta_axis, tau_ms: float = 10.0):
    """Largest axis Delta with a Hopf point at (J0, tau_d), or None."""
    ok = [d for d in delta_axis if hopf_point(float(J0), float(d), float(tau_d_ms), tau_ms) is not None]
    return max(ok) if ok else None


def taud_interval(J0: float, Delta: float, taud_axis, tau_ms: float = 10.0):
    """(min, max) of the axis tau_d with a Hopf point at (J0, Delta), or None."""
    ok = [t for t in taud_axis if hopf_point(float(J0), float(Delta), float(t), tau_ms) is not None]
    return (min(ok), max(ok)) if ok else None


def time_inside(t, re) -> float:
    """Time (same unit as t) with re > 0, the trapezoid with a linear zero crossing inside a node interval."""
    t, re = np.asarray(t, float), np.asarray(re, float)
    tot = 0.0
    for k in range(len(t) - 1):
        a, b, dt = re[k], re[k + 1], t[k + 1] - t[k]
        if a > 0 and b > 0:
            tot += dt
        elif a > 0 >= b:
            tot += dt * a / (a - b)
        elif b > 0 >= a:
            tot += dt * b / (b - a)
    return float(tot)


def path_region(cfg: dict, h: float):
    """(inside A4 region?, time inside in s) along the run's own path (M9-13)."""
    path, t, re, _ = EE.path_gain(cfg, h)
    tau = cfg["model"]["tau_ms"] * 1e-3
    return bool(np.any(re > 0.0)), time_inside(t, re) * tau


def labels(cls: str, label_f: bool, hopf_here, delta_max_here, taud_int, Delta: float, tau_d_ms: float, t_inside_s: float) -> dict:
    """Pure rule table. hopf_here: hopf_point() of the cell or None; delta_max_here: delta_max() or None; taud_int: taud_interval() or None."""
    if cls == "failed":
        return {"all": ["failed"], "primary": "failed"}
    got = {
        "a": delta_max_here is None or Delta > delta_max_here,
        "b": taud_int is None or not (taud_int[0] <= tau_d_ms <= taud_int[1]),
        "c": hopf_here is not None and hopf_here["f_hz"] < F_MIN_HZ,
        "d": hopf_here is not None and t_inside_s > 0.0 and t_inside_s * hopf_here["f_hz"] < MIN_CYCLES,
        "e": cls in ("D-sus", "S-sus"),
        "f": bool(label_f),
    }
    ap = [k for k in ORDER if got[k]]
    return {"all": ap, "primary": ap[0] if ap else None}


def label_cell(cfg: dict, cls: str, label_f: bool, delta_axis, taud_axis, h: float) -> dict:
    """Labels of one run with the A4 tables (cached). `label_f` must come from a classifier call made with inside_a4_region from path_region."""
    m, p = cfg["model"], cfg["path"]
    J0, D, td = float(p["J0"]), float(m["Delta"]), float(m["tau_d_ms"])
    inside, t_in = path_region(cfg, h)
    out = labels(cls, label_f, hopf_point(J0, D, td, m["tau_ms"]), delta_max(J0, td, delta_axis, m["tau_ms"]),
                 taud_interval(J0, D, taud_axis, m["tau_ms"]), D, td, t_in)
    out.update(inside_a4_region=inside, time_inside_s=t_in)
    return out
