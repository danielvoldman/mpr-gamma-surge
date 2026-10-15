"""M3: the 3D mean field with a first-order synapse, in tau-units (plan 3.1).

    dr/dt = Delta/pi + 2 r v
    dv/dt = v^2 + eta_bar + J s + I - pi^2 r^2
    (tau_d/tau) ds/dt = -s + r

The 3D form is the tau = 1 case of the dimensional equations [reasoned, not
tested; A4 checks it]. tau_d_tau is tau_d/tau, dimensionless.
"""
from __future__ import annotations

import numpy as np

PI2 = np.pi ** 2


def rhs_3d(t, y, eta_bar, J, Delta, tau_d_tau, I=0.0):
    """Right-hand side [dr/dt, dv/dt, ds/dt] of M3. `t` is unused (solve_ivp signature)."""
    r, v, s = y
    return np.array([Delta / np.pi + 2.0 * r * v,
                     v * v + eta_bar + I + J * s - PI2 * r * r,
                     (r - s) / tau_d_tau])


def jacobian_3d(y, J, tau_d_tau):
    """Jacobian [[2v, 2r, 0], [-2 pi^2 r, 2v, J], [beta, 0, -beta]], beta = tau/tau_d (plan 5.2 A4)."""
    r, v, _s = y
    beta = 1.0 / tau_d_tau
    return np.array([[2.0 * v, 2.0 * r, 0.0],
                     [-2.0 * PI2 * r, 2.0 * v, J],
                     [beta, 0.0, -beta]])
