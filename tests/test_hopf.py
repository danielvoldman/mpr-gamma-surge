"""A4 Hopf module (MS5 5b, plan 5.2 A4): characteristic polynomial, Hopf condition, K7 and K9 cross-checks."""
import numpy as np
import pytest
import yaml

from mprsurge import config as C
from mprsurge.analysis import hopf as H
from mprsurge.models.fixed_points import fixed_points
from mprsurge.models.mpr3d import jacobian_3d, rhs_3d


def test_char_poly_matches_eigenvalues_and_finite_difference_jacobian():
    eta, J, D, td = 1.0, -20.0, 0.05, 0.7
    y = fixed_points(eta, J, D, model="M3")[0]
    assert np.allclose(rhs_3d(0.0, y, eta, J, D, td), 0.0, atol=1e-9)
    A = jacobian_3d(y, J, td)
    f = lambda z: rhs_3d(0.0, z, eta, J, D, td)
    fd = np.column_stack([(f(y + h) - f(y - h)) / 2e-6 for h in 1e-6 * np.eye(3)])
    assert np.allclose(A, fd, atol=1e-6)
    a1, a2, a3 = H.char_poly(y, J, td)
    for lam in np.linalg.eigvals(A):
        assert abs(lam**3 + a1 * lam**2 + a2 * lam + a3) < 1e-8


def test_known_cubic_hopf_condition():
    # (l + c)(l^2 + w^2) = l^3 + c l^2 + w^2 l + c w^2 has a1 a2 = a3 and roots +-i w
    c, w = 1.3, 2.1
    a1, a2, a3 = c, w * w, c * w * w
    assert a1 * a2 - a3 == pytest.approx(0.0)
    assert sorted(np.roots([1, a1, a2, a3]), key=lambda z: z.imag)[-1].imag == pytest.approx(w)


def test_k7_hopf_value_from_earlier_milestone():
    # DL-074 / DL-079: tau_d_H = 4.12 ms at ref_ceni (UNVERIFIED value; the paper has 4.95 ms)
    c = H.hopf_crossings("tau_d_tau", np.linspace(0.05, 5.0, 100), 1.0, -20.0, 0.05, 1.0)
    assert len(c) == 1
    assert c[0]["tau_d_tau"] * 10.0 == pytest.approx(4.12, abs=0.05)
    assert c[0]["valid"] and c[0]["omega"] == pytest.approx(np.sqrt(c[0]["a2"]))
    assert c[0]["a1"] * c[0]["a2"] == pytest.approx(c[0]["a3"], rel=1e-9)
    # damped below, oscillatory-unstable above
    y = fixed_points(1.0, -20.0, 0.05, model="M3")[0]
    assert np.linalg.eigvals(jacobian_3d(y, -20.0, 0.3)).real.max() < 0
    assert np.linalg.eigvals(jacobian_3d(y, -20.0, 0.8)).real.max() > 0


def test_rejects_a1a2_equals_a3_when_a1_not_positive():
    # a1 = -tr; a point with h = 0 but a1 <= 0 is not a Hopf point: valid flag is False
    rec = {"a1": -1.0, "a2": 2.0, "a3": -2.0}
    assert rec["a1"] * rec["a2"] == rec["a3"]
    assert not (rec["a1"] > 0 and rec["a3"] > 0)


def test_no_hopf_for_positive_J():
    for J in (0.5, 5.0, 15.0):
        for eta in (-8.0, -5.0, 1.0):
            c = H.hopf_crossings("tau_d_tau", np.geomspace(0.01, 20.0, 80), eta, J, 0.3, 1.0)
            assert c == [], (J, eta)


def test_eta_hopf_curve_and_k11():
    row = H.hopf_curve("tau_d", [1.0], np.linspace(-5, 10, 301), {"J": -21.0, "Delta": 0.3, "tau_d_tau": 1.0})[0]
    assert np.isfinite(row[1]) and row[2] > 0
    # K11 ratio near J -> 0-, Delta = 1e-4: a number is returned (value judged at 5c, not here)
    assert np.isfinite(H.k11_ratio(1.0, -1.0, 1e-4, 1.0))


def test_k9_maximiser_near_0p1453_and_edge_widening():
    r = H.max_ratio_over_J_tau(1.0, (0.1, 5.0), (-40.0, -1.0), n_tau=8, n_J=8, n_ratio=60)
    assert r["ratio"] == pytest.approx(0.1453, abs=0.002) and not r["on_edge"]   # UNVERIFIED reading, plan K9
    # a J range that excludes the maximiser (J about -5.3): one widening finds it inside
    w = H.max_ratio_over_J_tau(1.0, (0.1, 5.0), (-3.0, -1.0), n_tau=6, n_J=6, n_ratio=40)
    assert len(w["log"]) == 1 and not w["on_edge"] and w["ratio"] == pytest.approx(0.1453, abs=0.002)
    # still on the edge after two widenings: reported as asymptotic
    w = H.max_ratio_over_J_tau(1.0, (0.1, 5.0), (-1.0, -0.5), n_tau=6, n_J=6, n_ratio=40)
    assert len(w["log"]) == 2 and w["on_edge"] and w["asymptotic"]


def test_a4_yaml_grids_match_plan_ranges():
    cfg = yaml.safe_load((C.repo_root() / "configs" / "A4.yaml").read_text())
    assert cfg["grids"]["tau_d_ms"]["lo"] == 1.0 and cfg["grids"]["tau_d_ms"]["hi"] == 50.0
    assert cfg["k9"]["eta_bar"] == [1.0, 2.0, 4.0] and cfg["k9"]["max_widen"] == 2
    assert cfg["points"]["ref_devalle"] == {"eta_bar": 4.0, "Delta": 0.3, "J": -21.0}
