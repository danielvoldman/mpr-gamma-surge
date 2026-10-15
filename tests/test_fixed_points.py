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


D_K1 = 1.0
ETA_G = np.linspace(-10.0, 2.0, 241)                          # A1 grid, D = 1 (plan 5.2 A1)
J_G = np.linspace(0.0, 20.0, 201)
CELL = (0.05, 0.1)
R_CUSP = (3.0 / (4.0 * np.pi**4)) ** 0.25                     # dJ_SN/dr = 0: the cusp of the fold curve


def _k1_formula(r):
    # (eta, J)_SN = [-pi^2 r^2 - 3 D^2/(2 pi r)^2, 2 pi^2 r + D^2/(2 pi^2 r^3)] (MPR Fig. 1)
    return (-np.pi**2 * r**2 - 3 * D_K1**2 / (2 * np.pi * r) ** 2,
            2 * np.pi**2 * r + D_K1**2 / (2 * np.pi**2 * r**3))


def _k1_points_and_edges():
    # DL-064: 20 r values uniform on the r-interval where the formula point lies inside the A1 grid
    fine = np.linspace(0.05, 3.0, 200001)
    e, J = _k1_formula(fine)
    inside = (e >= ETA_G[0]) & (e <= ETA_G[-1]) & (J >= J_G[0]) & (J <= J_G[-1])
    r_lo, r_hi = fine[inside][0], fine[inside][-1]
    assert np.all(inside[(fine >= r_lo) & (fine <= r_hi)])      # one interval
    counts = np.array([[len(fixed_points(x, y, D_K1)) for y in J_G] for x in ETA_G])
    edge = np.zeros_like(counts, dtype=bool)                   # grid nodes whose root count differs from the next node
    edge[:-1, :] |= counts[:-1, :] != counts[1:, :]
    edge[:, :-1] |= counts[:, :-1] != counts[:, 1:]
    return np.linspace(r_lo, r_hi, 20), np.nonzero(edge)


def _k1_has_edge_within_a_cell(r, ie, jj):
    eta, J = _k1_formula(r)
    return bool(((np.abs(ETA_G[ie] - eta) <= CELL[0] + 1e-9) & (np.abs(J_G[jj] - J) <= CELL[1] + 1e-9)).any())


def test_k1_formula_points_are_double_roots():
    rs, _ = _k1_points_and_edges()
    for r in rs:
        eta, J = _k1_formula(r)
        assert abs(quartic(r, eta, J, D_K1)) < 1e-9
        assert abs(-4 * np.pi**2 * r**3 + 3 * J * r**2 + 2 * eta * r) < 1e-9


@pytest.mark.xfail(strict=True, reason="DL-078: near the cusp the fold-to-fold gap is below one A1 cell (UNVERIFIED)")
def test_k1_all_20_points_have_a_count_change_edge_within_one_cell():
    rs, (ie, jj) = _k1_points_and_edges()
    assert all(_k1_has_edge_within_a_cell(r, ie, jj) for r in rs)


def test_k1_points_away_from_the_cusp_have_a_count_change_edge_within_one_cell():
    # UNVERIFIED test-level: points with |r - r_cusp| >= 0.05 (the 20 points are those of DL-064)
    rs, (ie, jj) = _k1_points_and_edges()
    far = [r for r in rs if abs(r - R_CUSP) >= 0.05]
    assert len(far) >= 17
    for r in far:
        assert _k1_has_edge_within_a_cell(r, ie, jj), f"no count-change edge near the K1 point at r = {r:.4f}"


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
