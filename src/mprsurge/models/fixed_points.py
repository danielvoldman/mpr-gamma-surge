"""Fixed points of M2 and M3 from one routine (plan 5.2, opening paragraph).

Substituting v* = -Delta/(2 pi r*) into dv/dt = 0 gives
    -pi^2 r^4 + J r^3 + (eta_bar + I) r^2 + Delta^2/(4 pi^2) = 0,
solved with numpy.roots for positive real r. In M3, s* = r*.
"""
from __future__ import annotations

import numpy as np

from .mpr2d import jacobian_2d
from .mpr3d import jacobian_3d

PI2 = np.pi ** 2
IMAG_TOL = 1e-7  # |Im r| below this (relative to |r|) counts as a real root


class FixedPointError(ValueError):
    """Raised when the stable-root rule (DL-053) finds zero or several stable roots."""


def quartic(r, eta_bar, J, Delta, I=0.0):
    return -PI2 * r**4 + J * r**3 + (eta_bar + I) * r**2 + Delta**2 / (4.0 * PI2)


def fixed_points(eta_bar, J, Delta, I=0.0, model="M2", tau_d_tau=None):
    """Positive-r fixed points, sorted by r: array (n, 2) of (r, v) for M2, (n, 3) of (r, v, s) for M3."""
    roots = np.roots([-PI2, J, eta_bar + I, 0.0, Delta**2 / (4.0 * PI2)])
    r = np.sort([z.real for z in roots if z.real > 0 and abs(z.imag) <= IMAG_TOL * abs(z)])
    v = -Delta / (2.0 * np.pi * r)
    return np.column_stack([r, v]) if model == "M2" else np.column_stack([r, v, r])


def jacobian_at(y, J, model="M2", tau_d_tau=None):
    return jacobian_2d(y, J) if model == "M2" else jacobian_3d(y, J, tau_d_tau)


def classify_fixed_point(eigvals, model="M2"):
    """Label from the Jacobian eigenvalues.

    M2: stable_node, stable_focus, unstable_node, unstable_focus, saddle.
    M3: stable, saddle (mixed signs), unstable. (The label set is a coding choice.)
    """
    ev = np.asarray(eigvals)
    re = ev.real
    if model == "M2":
        focus = bool(np.any(ev.imag != 0.0))
        if np.all(re < 0):
            return "stable_focus" if focus else "stable_node"
        if np.all(re > 0):
            return "unstable_focus" if focus else "unstable_node"
        return "saddle"
    return "stable" if np.all(re < 0) else "unstable" if np.all(re > 0) else "saddle"


def classify_all(eta_bar, J, Delta, I=0.0, model="M2", tau_d_tau=None):
    """List of (fixed point, label, eigenvalues) for every positive root."""
    out = []
    for y in fixed_points(eta_bar, J, Delta, I, model, tau_d_tau):
        ev = np.linalg.eigvals(jacobian_at(y, J, model, tau_d_tau))
        out.append((y, classify_fixed_point(ev, model), ev))
    return out


def stable_fixed_point(eta_bar, J, Delta, I=0.0, model="M2", tau_d_tau=None):
    """The start state of a run (DL-053): the one stable root, else FixedPointError."""
    stable = [y for y, label, _ in classify_all(eta_bar, J, Delta, I, model, tau_d_tau)
              if label.startswith("stable")]
    if len(stable) != 1:
        raise FixedPointError(f"expected exactly one stable fixed point, found {len(stable)} "
                              f"at eta_bar={eta_bar}, J={J}, Delta={Delta}, I={I}")
    return stable[0]
