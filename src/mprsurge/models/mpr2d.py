"""M2: the 2D Montbrio-Pazo-Roxin mean field in tau-units (plan 3.1, MPR Eq. 12).

    dr/dt = Delta/pi + 2 r v
    dv/dt = v^2 + eta_bar + J r + I - pi^2 r^2

Time is in units of tau, r in 1/tau. J is signed (inhibition J < 0).
"""
from __future__ import annotations

import numpy as np

PI2 = np.pi ** 2


def rhs_2d(t, y, eta_bar, J, Delta, I=0.0):
    """Right-hand side [dr/dt, dv/dt] of M2 (s = r). `t` is unused (solve_ivp signature)."""
    r, v = y
    return np.array([Delta / np.pi + 2.0 * r * v,
                     v * v + eta_bar + I + J * r - PI2 * r * r])


def jacobian_2d(y, J):
    """Jacobian [[2v, 2r], [J - 2 pi^2 r, 2v]] (plan 5.2 A1)."""
    r, v = y
    return np.array([[2.0 * v, 2.0 * r],
                     [J - 2.0 * PI2 * r, 2.0 * v]])
