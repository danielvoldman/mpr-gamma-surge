"""M2 right-hand side and Jacobian (plan 10.5). Tolerances are stated per assertion (DL-061)."""
import numpy as np
from scipy.integrate import solve_ivp

from mprsurge.models.fixed_points import fixed_points
from mprsurge.models.mpr2d import jacobian_2d, rhs_2d

POINTS = [(-5.0, 15.0, 1.0, 0.0), (-5.0, 15.0, 1.0, 3.0), (1.0, 5.0, 0.3, 0.0), (4.0, -21.0, 0.3, 0.0)]


def test_rhs_vanishes_at_fixed_points_and_vstar_formula():
    for eta, J, D, I in POINTS:
        fps = fixed_points(eta, J, D, I)
        assert len(fps) >= 1
        for r, v in fps:
            assert np.allclose(rhs_2d(0.0, [r, v], eta, J, D, I), 0.0, atol=1e-9)  # atol 1e-9
            assert np.isclose(v, -D / (2 * np.pi * r), rtol=1e-12)                 # v* = -Delta/(2 pi r*)


def test_jacobian_matches_central_differences():
    rng = np.random.default_rng(0)
    for _ in range(20):
        y = rng.uniform([0.05, -2.0], [1.5, 1.0])
        eta, J, D, I = rng.uniform(-6, 4), rng.uniform(-20, 20), rng.uniform(0.05, 1), rng.uniform(0, 2)
        h = 1e-6
        fd = np.column_stack([(rhs_2d(0, y + h * e, eta, J, D, I) - rhs_2d(0, y - h * e, eta, J, D, I)) / (2 * h)
                              for e in np.eye(2)])
        assert np.allclose(jacobian_2d(y, J), fd, rtol=1e-6, atol=1e-6)            # 1e-6 (central difference)


def test_linear_eigenvalues_match_formula():
    # lambda = 2 v* +- sqrt(2 r* (J - 2 pi^2 r*)) (plan 3.1)
    for eta, J, D, I in POINTS:
        for r, v in fixed_points(eta, J, D, I):
            disc = 2 * r * (J - 2 * np.pi**2 * r)
            lam = 2 * v + np.sqrt(complex(disc)) * np.array([1, -1])
            got = np.linalg.eigvals(jacobian_2d([r, v], J))
            assert np.allclose(np.sort_complex(got), np.sort_complex(lam), rtol=1e-9, atol=1e-9)


def test_r_stays_positive():
    # dr/dt = Delta/pi at r = 0, and a run started at r = 0 leaves it upward
    assert np.isclose(rhs_2d(0.0, [0.0, -1.3], -5.0, 15.0, 1.0)[0], 1.0 / np.pi, rtol=1e-12)
    sol = solve_ivp(rhs_2d, (0, 20), [0.0, -3.0], args=(-5.0, 15.0, 1.0), rtol=1e-9, atol=1e-12)
    assert sol.success and sol.y[0].min() >= 0.0
