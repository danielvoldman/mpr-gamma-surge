"""M3 right-hand side and Jacobian (plan 10.5). The K7 Hopf value is checked in test_replication."""
import numpy as np
from scipy.integrate import solve_ivp

from mprsurge.models.fixed_points import fixed_points
from mprsurge.models.mpr2d import rhs_2d
from mprsurge.models.mpr3d import jacobian_3d, rhs_3d

M3_POINTS = [(4.0, -21.0, 0.3, 0.5, 0.0), (1.0, -20.0, 0.05, 0.495, 0.0), (-5.0, 15.0, 1.0, 1.0, 0.0),
             (4.0, -21.0, 0.3, 5.0, 1.0)]  # eta, J, Delta, tau_d/tau, I


def test_rhs_vanishes_at_fixed_points_with_s_equal_r():
    for eta, J, D, tdt, I in M3_POINTS:
        for r, v, s in fixed_points(eta, J, D, I, model="M3"):
            assert s == r
            assert np.allclose(rhs_3d(0.0, [r, v, s], eta, J, D, tdt, I), 0.0, atol=1e-9)  # atol 1e-9
            assert np.isclose(v, -D / (2 * np.pi * r), rtol=1e-12)


def test_jacobian_matches_central_differences():
    rng = np.random.default_rng(1)
    for _ in range(20):
        y = rng.uniform([0.05, -2.0, 0.0], [1.5, 1.0, 1.5])
        eta, J, D = rng.uniform(-6, 4), rng.uniform(-30, 20), rng.uniform(0.05, 1)
        I, tdt = rng.uniform(0, 2), rng.uniform(0.1, 5)
        h = 1e-6
        fd = np.column_stack([(rhs_3d(0, y + h * e, eta, J, D, tdt, I) - rhs_3d(0, y - h * e, eta, J, D, tdt, I)) / (2 * h)
                              for e in np.eye(3)])
        assert np.allclose(jacobian_3d(y, J, tdt), fd, rtol=1e-6, atol=1e-5)     # 1e-6 rel / 1e-5 abs (central difference)


def test_m3_with_tiny_tau_d_tracks_m2():
    # tau_d = 1e-3 tau (stiff: Radau). Short run from a displaced state. Tolerance 1e-2 absolute on r and v,
    # about 1.6x the observed 6e-3 (DL-061; chosen after seeing the value), plus a convergence check:
    # the error at tau_d = 1e-4 is below a fifth of that at 1e-3 (first order in tau_d).
    eta, J, D = -5.0, 15.0, 1.0
    r0, v0 = fixed_points(eta, J, D)[-1]
    y2 = [r0 + 0.2, v0 - 0.1]
    t = np.linspace(0, 8, 81)
    m2 = solve_ivp(rhs_2d, (0, 8), y2, args=(eta, J, D), method="Radau", rtol=1e-9, atol=1e-11, t_eval=t)

    def err(tau_d):
        m3 = solve_ivp(rhs_3d, (0, 8), y2 + [y2[0]], args=(eta, J, D, tau_d), method="Radau",
                       rtol=1e-9, atol=1e-11, t_eval=t)
        assert m3.success
        return np.max(np.abs(m3.y[:2] - m2.y))

    e3, e4 = err(1e-3), err(1e-4)
    assert m2.success and e3 < 1e-2 and e4 < e3 / 5
