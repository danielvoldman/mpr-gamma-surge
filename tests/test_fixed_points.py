"""Quartic roots, classification, the DL-053 rule, K1 and K2 on coarse grids (plan 10.5, 3.1, 5.2 A1)."""
import numpy as np
import pytest
from scipy.optimize import brentq

from mprsurge.models.fixed_points import (FixedPointError, classify_all, classify_fixed_point,
                                          fixed_points, quartic, stable_fixed_point)


def brute_force_roots(eta, J, D, I=0.0):
    """Sign changes of the quartic on a fine log grid, refined with brentq."""
    r = np.geomspace(1e-4, 20.0, 40001)
    f = quartic(r, eta, J, D, I)
    idx = np.where(np.sign(f[:-1]) * np.sign(f[1:]) < 0)[0]
    return np.array([brentq(quartic, r[i], r[i + 1], args=(eta, J, D, I), xtol=1e-14) for i in idx])


def test_quartic_roots_match_brute_force_bracketing():
    rng = np.random.default_rng(2)
    n_multi = 0
    for _ in range(300):
        eta, J, D, I = rng.uniform(-10, 4), rng.uniform(-25, 25), rng.uniform(0.05, 1.0), rng.uniform(0, 1.5)
        got = fixed_points(eta, J, D, I)[:, 0]
        ref = brute_force_roots(eta, J, D, I)
        assert len(got) == len(ref), (eta, J, D, I)
        assert np.allclose(got, ref, rtol=1e-6, atol=1e-8)                      # rtol 1e-6
        n_multi += len(got) == 3
    assert n_multi > 10                                                         # the sample reaches the bistable wedge


def test_k3_has_focus_node_and_saddle():
    labels = sorted(lab for _, lab, _ in classify_all(-5.0, 15.0, 1.0))
    assert labels == ["saddle", "stable_focus", "stable_node"]


def test_classify_labels():
    assert classify_fixed_point(np.array([-1 + 2j, -1 - 2j])) == "stable_focus"
    assert classify_fixed_point(np.array([-1.0, -2.0])) == "stable_node"
    assert classify_fixed_point(np.array([1.0, -2.0])) == "saddle"
    assert classify_fixed_point(np.array([1 + 1j, 1 - 1j])) == "unstable_focus"
    assert classify_fixed_point(np.array([-1.0, -2.0, -3.0]), "M3") == "stable"


def test_dl053_stable_root_rule():
    r, v = stable_fixed_point(-8.0, 5.0, 1.0)                                   # one root, stable
    assert r > 0 and v < 0
    with pytest.raises(FixedPointError):                                        # K3: two stable roots
        stable_fixed_point(-5.0, 15.0, 1.0)


def test_m3_stable_point_shape():
    # tau_d = 50 ms (tau_d/tau = 5): no oscillation at ref_devalle (K8), so the root is stable
    y = stable_fixed_point(4.0, -21.0, 0.3, model="M3", tau_d_tau=5.0)
    assert y.shape == (3,) and y[2] == y[0]
    with pytest.raises(FixedPointError):                   # tau_d = 5 ms: the root is unstable (gamma regime, K8)
        stable_fixed_point(4.0, -21.0, 0.3, model="M3", tau_d_tau=0.5)


def test_k1_saddle_node_curve_on_a_coarse_grid():
    # K1: (eta, J)_SN = [-pi^2 r^2 - 3 D^2/(2 pi r)^2, 2 pi^2 r + D^2/(2 pi^2 r^3)]  (MPR Fig. 1)
    D = 1.0
    for r in np.linspace(0.25, 1.2, 20):
        eta = -np.pi**2 * r**2 - 3 * D**2 / (2 * np.pi * r) ** 2
        J = 2 * np.pi**2 * r + D**2 / (2 * np.pi**2 * r**3)
        # the quartic and its derivative vanish at r: a double root
        assert abs(quartic(r, eta, J, D)) < 1e-9
        assert abs(-4 * np.pi**2 * r**3 + 3 * J * r**2 + 2 * eta * r) < 1e-9
    # coarse (eta, J) grid: at fixed J, the eta grid edge (step 0.05) where the positive-root count changes
    # lies within one cell of each formula point. Points: r solves 2 pi^2 r^4 - J r^3 + D^2/(2 pi^2) = 0.
    step = 0.05
    for J in (10.0, 12.0, 15.0, 18.0):                       # above the cusp (J about 7.8 at D = 1)
        rs = [z.real for z in np.roots([2 * np.pi**2, -J, 0.0, 0.0, D**2 / (2 * np.pi**2)])
              if z.real > 0 and abs(z.imag) < 1e-9]
        eta_sn = sorted(-np.pi**2 * r**2 - 3 * D**2 / (2 * np.pi * r) ** 2 for r in rs)
        grid = np.arange(-12.0, 2.0, step)
        counts = np.array([len(fixed_points(e, J, D)) for e in grid])
        edges = grid[1:][counts[1:] != counts[:-1]]        # first grid point after each change
        assert len(edges) == len(eta_sn) >= 1
        for e_grid, e_formula in zip(edges, eta_sn):
            assert 0 <= e_grid - e_formula <= step + 1e-9


def test_k2_node_focus_boundary_on_a_coarse_grid():
    # K2: eta_f = -(J/2pi)^2 - (pi D/J)^2; focus to its right. Scan eta upward in steps of 0.05 (the A1 cell)
    D, step = 1.0, 0.05
    for J in (2.0, 5.0, 10.0, 15.0, 20.0):
        eta_f = -((J / (2 * np.pi)) ** 2) - (np.pi * D / J) ** 2
        r_c = J / (2 * np.pi**2)                                                # eigenvalue discriminant is zero here
        assert abs(quartic(r_c, eta_f, J, D)) < 1e-9
        first = None
        for eta in np.arange(eta_f - 1.0, eta_f + 1.0, step):
            st = [lab for _, lab, _ in classify_all(eta, J, D) if lab.startswith("stable")]
            if st and st[-1] == "stable_focus":
                first = eta
                break
        assert first is not None and abs(first - eta_f) <= step + 1e-9
