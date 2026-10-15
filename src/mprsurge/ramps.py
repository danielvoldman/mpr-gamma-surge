"""Ramp profiles, parameter paths P1-P5 and their breakpoints (plan 4.4, DL-060).

Each ramped parameter follows p(t) = p_start + (p_end - p_start) g((t - t_on)/T).
Times inside this module are in tau units; `make_path` converts the config's seconds.

Readings (DL-060): the logistic centre is 0.5 (UNSOURCED: 4.4 gives k = 10 and the
rescaling but no centre); P5 lasts 2 T_ramp (up over T_ramp, then down over T_ramp).
Reading of 4.4 for P4a/P4b: Delta goes from model.Delta to model.Delta * Delta_factor
over T_ramp, Delta_factor set in the run config (1.5 or 2/3); the profile applies to
every ramped parameter; model.I_drive is added to the P3 trapezoid.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from . import config as C
from .units import s_to_tau


def profile_linear(x):
    """g(x) = x clipped to [0, 1]."""
    return np.clip(x, 0.0, 1.0)


def _logistic(z):
    return 1.0 / (1.0 + np.exp(-z))


def profile_sigmoid(x, k=10.0):
    """Logistic with slope k, centre 0.5, rescaled so g(0) = 0 and g(1) = 1; clipped outside [0, 1]."""
    lo, hi = _logistic(-k / 2.0), _logistic(k / 2.0)
    return (_logistic(k * (np.clip(x, 0.0, 1.0) - 0.5)) - lo) / (hi - lo)


def _profile(name, k):
    return profile_linear if name == "linear" else (lambda x: profile_sigmoid(x, k))


def ramp_param(t, p_start, p_end, t_on, T, g=profile_linear):
    """p(t) = p_start + (p_end - p_start) g((t - t_on)/T)."""
    return p_start + (p_end - p_start) * g((np.asarray(t, dtype=float) - t_on) / T)


@dataclass
class Path:
    """Time-dependent parameters of one run, in tau units. Callables accept scalars or arrays."""
    name: str
    eta: Callable
    J: Callable
    Delta: Callable
    I: Callable
    breakpoints: np.ndarray       # sorted corner times, tau
    t_on: float
    t_ramp_end: float             # last ramp ends here; the hold starts here (CP14)
    meta: dict = field(default_factory=dict)


def _trapezoid(t, t_on, T, amp, rise, plateau, fall):
    """Trapezoid from t_on: rise, plateau, fall as fractions of T (P3)."""
    x = (np.asarray(t, dtype=float) - t_on) / T
    up = np.clip(x / rise, 0.0, 1.0)
    down = np.clip((rise + plateau + fall - x) / fall, 0.0, 1.0)
    return amp * np.minimum(up, down)


def make_path(cfg: dict) -> Path:
    """Build the path named by cfg['path']['name'] from a resolved config.

    Raises ConfigError for an unresolved eta path (C.require_eta_path).
    """
    C.require_eta_path(cfg)
    m, p = cfg["model"], cfg["path"]
    tau = m["tau_ms"]
    T, t_on = s_to_tau(p["T_ramp_s"], tau), s_to_tau(p["t_on_s"], tau)
    g = _profile(p["profile"], p["sigmoid_k"])
    name = p["name"]
    e0, e1 = p["eta_start"], p["eta_peak"]
    I0 = m["I_drive"]

    def Jfixed(t):
        return np.full_like(np.asarray(t, dtype=float), m["J"])

    def Dfixed(t):
        return np.full_like(np.asarray(t, dtype=float), m["Delta"])

    def Ifixed(t):
        return np.full_like(np.asarray(t, dtype=float), I0)

    eta = lambda t: ramp_param(t, e0, e1, t_on, T, g)
    J, Delta, I = Jfixed, Dfixed, Ifixed
    corners = [t_on, t_on + T]
    t_end = t_on + T

    if name in ("path_hypoxia", "path_drive", "path_delta_up", "path_delta_down"):
        tJ, TJ = t_on + p["J_lag_frac"] * T, p["J_T_frac"] * T
        J = lambda t: ramp_param(t, p["J0"], p["J_end"], tJ, TJ, g)
        corners += [tJ, tJ + TJ]
        t_end = max(t_end, tJ + TJ)           # P2: t_on + 1.25 T_ramp
    if name == "path_drive":
        r_, pl, f_ = p["I_rise_frac"], p["I_plateau_frac"], p["I_fall_frac"]
        I = lambda t: I0 + _trapezoid(t, t_on, T, p["I_amp"], r_, pl, f_)
        corners += [t_on + r_ * T, t_on + (r_ + pl) * T, t_on + (r_ + pl + f_) * T]
        t_end = max(t_end, corners[-1])
    if name in ("path_delta_up", "path_delta_down"):
        Delta = lambda t: ramp_param(t, m["Delta"], m["Delta"] * p["Delta_factor"], t_on, T, g)
    if name == "path_updown":
        eta = lambda t: np.where(np.asarray(t, dtype=float) <= t_on + T,
                                 ramp_param(t, e0, e1, t_on, T, g),
                                 ramp_param(t, e1, e0, t_on + T, T, g))
        corners += [t_on + 2 * T]
        t_end = t_on + 2 * T
    bp = np.unique(np.array(corners, dtype=float))
    return Path(name, eta, J, Delta, I, bp, t_on, t_end, {"profile": p["profile"]})


def breakpoints(cfg: dict) -> np.ndarray:
    """Sorted corner times (tau) of the configured path; integrate piecewise between them (6.2)."""
    return make_path(cfg).breakpoints
