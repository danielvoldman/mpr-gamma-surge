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


def _k1_has_edge_on_local_grid(r, factor):
    # grid spacing divided by `factor` near the fold curve (Table 6.2 resolution rule), +-6 base cells around the point
    de, dJ = CELL[0] / factor, CELL[1] / factor
    eta, J = _k1_formula(r)
    eg = np.arange(np.floor(eta / de) * de - 6 * de, eta + 6 * de, de)
    Jg = np.arange(np.floor(J / dJ) * dJ - 6 * dJ, J + 6 * dJ, dJ)
    counts = np.array([[len(fixed_points(x, y, D_K1)) for y in Jg] for x in eg])
    edge = np.zeros_like(counts, dtype=bool)
    edge[:-1, :] |= counts[:-1, :] != counts[1:, :]
    edge[:, :-1] |= counts[:, :-1] != counts[:, 1:]
    ie, jj = np.nonzero(edge)
    return bool(((np.abs(eg[ie] - eta) <= CELL[0] + 1e-9) & (np.abs(Jg[jj] - J) <= CELL[1] + 1e-9)).any())


def test_k1_cusp_points_fail_at_the_base_spacing_and_pass_when_halved():
    # DL-078, DL-081: the criterion is unchanged (a count-change node within 0.05 x 0.1); only the local spacing is halved
    rs, _ = _k1_points_and_edges()
    cusp = [r for r in rs if abs(r - R_CUSP) < 0.05]
    assert len(cusp) == 2
    assert not any(_k1_has_edge_on_local_grid(r, 1) for r in cusp)
    assert all(_k1_has_edge_on_local_grid(r, 2) for r in cusp)


def test_k1_all_20_points_pass_on_the_a1_grid_with_halved_spacing_near_the_fold_curve():
    rs, _ = _k1_points_and_edges()
    assert all(_k1_has_edge_on_local_grid(r, 2) for r in rs)


def test_k1_points_away_from_the_cusp_have_a_count_change_edge_within_one_cell():
    # UNVERIFIED test-level: the base A1 spacing, points with |r - r_cusp| >= 0.05 (the 20 points are those of DL-064)
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


# --- A1 (MS2 step 2b): the grid analysis through the runner, plan 5.2 A1, DL-085 ---------------

import json
import sys
from pathlib import Path

from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import bifurcation as B
from mprsurge.models.fixed_points import classify_all as _classify_all


@pytest.fixture(scope="module")
def a1(tmp_path_factory):
    out = tmp_path_factory.mktemp("a1_out").as_posix()
    assert R.main(["--config", "configs/A1.yaml", "--set", f"output.dir={out}"]) == 0
    d = Path(out) / "A1"
    rec_path = next(d.glob("A1_0000_*.json"))
    return np.load(next(d.glob("A1_0000_*.npz"))), P.read_run_record(rec_path), d


def test_a1_runs_through_the_runner_with_a_record(a1):
    z, rec, d = a1
    assert rec["status"] == "ok" and rec["config"]["run"]["kind"] == "a1"
    assert rec["criteria_sha256"] == P.sha256_file(Path("configs/replication.yaml"))   # frozen yaml, DL-084
    assert rec["flags"]["refinement_widths_status"] == "UNVERIFIED"
    assert set(rec["outputs"]) >= {next(d.glob("A1_0000_*.npz")).name}


def test_a1_base_grid_is_241_by_201_on_the_plan_ranges(a1):
    z, _, _ = a1
    assert z["eta_over_Delta"].shape == (241,) and z["J_over_sqrtDelta"].shape == (201,)
    assert (z["eta_over_Delta"][0], z["eta_over_Delta"][-1]) == (-10.0, 2.0)
    assert (z["J_over_sqrtDelta"][0], z["J_over_sqrtDelta"][-1]) == (0.0, 20.0)
    assert z["n_roots"].shape == (241, 201) and z["label"].shape == (241, 201, 3)
    assert np.allclose(np.diff(z["eta_over_Delta"]), 0.05) and np.allclose(np.diff(z["J_over_sqrtDelta"]), 0.1)


def test_a1_refined_lattice_is_nested_and_at_half_spacing(a1):
    z, _, _ = a1
    assert np.allclose(np.diff(z["eta_fine"]), 0.025) and np.allclose(np.diff(z["J_fine"]), 0.05)
    assert np.array_equal(z["eta_fine"][::2], z["eta_over_Delta"]) and np.array_equal(z["J_fine"][::2], z["J_over_sqrtDelta"])
    ie, je, mask = z["refined_ie"], z["refined_je"], z["refined_mask"]
    assert mask[ie, je].all() and mask.sum() == len(ie)
    both_even = (ie % 2 == 0) & (je % 2 == 0)                    # refined nodes that are base nodes agree with the base grid
    assert both_even.sum() > 100
    assert np.array_equal(z["refined_n_roots"][both_even], z["n_roots"][ie[both_even] // 2, je[both_even] // 2])
    assert np.array_equal(z["refined_label"][both_even], z["label"][ie[both_even] // 2, je[both_even] // 2])
    assert 0 < mask.sum() < 0.2 * mask.size                       # refined only near the fold and the cusp


def test_a1_refined_region_is_the_band_around_the_fold_plus_the_cusp_box(a1):
    z, _, _ = a1
    eta_f, J_f, mask = z["eta_fine"], z["J_fine"], z["refined_mask"]
    for j in (300, 330, 380, 400):                                # fine rows with J > J_cusp
        for e in B.fold_etas(J_f[j]):
            near = np.abs(eta_f - e) <= 4 * 0.05 + 1e-9
            if near.any():
                assert mask[near, j].all()
    _, eta_c, J_c = B.cusp_point()
    box = (np.abs(eta_f[:, None] - eta_c) <= 0.5 + 1e-9) & (np.abs(J_f[None, :] - J_c) <= 1.0 + 1e-9)
    assert mask[box].all()
    ie, je = np.nonzero(mask)                                     # nothing outside the band and the box
    for i, j in zip(ie[::7], je[::7]):
        in_band = any(abs(eta_f[i] - e) <= 0.2 + 1e-9 for e in B.fold_etas(J_f[j]))
        assert in_band or box[i, j]
    assert not mask[0, 0] and not mask[-1, -1] and not mask[-1, 0]   # corners away from the fold stay base
    assert abs(z["cusp_r_eta_J"][0] - R_CUSP) < 1e-12


def test_a1_classification_matches_classify_all_at_sample_nodes(a1):
    z, _, _ = a1
    rng = np.random.default_rng(5)
    for _ in range(40):
        i, j = rng.integers(0, 241), rng.integers(0, 201)
        ref = _classify_all(z["eta_over_Delta"][i], z["J_over_sqrtDelta"][j], 1.0)
        assert z["n_roots"][i, j] == len(ref)
        assert [B.LABELS[c] for c in z["label"][i, j] if c] == [lab for _, lab, _ in ref]


def test_a1_k3_point_is_exactly_focus_node_saddle(a1):
    z, _, _ = a1
    assert list(z["k3_labels"]) == ["saddle", "stable_focus", "stable_node"] and bool(z["k3_pass"])


def test_a1_k1_base_18_of_20_and_half_spacing_20_of_20(a1):
    # DL-078 (base) and DL-081 (half); the criterion and the cell come from the frozen replication.yaml
    z, _, _ = a1
    assert z["k1_pass_base"].sum() == 18 and z["k1_pass_half"].all()
    assert not z["k1_pass_base"][[3, 4]].any()                    # the two points next to the cusp


def test_a1_k2_discriminant_sign_change_within_one_cell_of_the_formula(a1):
    z, _, _ = a1
    g = z["k2_in_grid"]
    assert g.sum() > 150 and z["k2_pass_base"][g].all() and not z["k2_pass_base"][~g].any()
    assert (z["k2_n_sign_changes_base"][g] == 1).all()
    assert z["k2_pass_half"].all() and len(z["k2_pass_half"]) > 100


def test_a1_c9_node_region_exists_and_needs_excitation(a1):
    z, _, _ = a1
    assert bool(z["c9_node_region_exists"]) and int(z["c9_node_count_nodes"]) > 0
    assert bool(z["c9_nodes_have_J_above_2pi2r"]) and float(z["c9_node_min_J"]) > 0


def test_a1_halving_check_is_recorded_not_tested(a1):
    # Table 6.2 / D31 (DL-085): stored along the fold and at the cusp; no pass/fail threshold here
    z, _, _ = a1
    assert z["halving_fold_shift_cells"].shape == (201, 2) and np.isfinite(z["halving_fold_shift_cells"]).sum() > 100
    names = list(z["halving_cusp_names"])
    assert {"J_shift_cells", "eta_shift_cells", "J_base", "J_half", "J_formula"} <= set(names)
    assert np.isfinite(z["halving_cusp_values"]).all()


def test_a1_driver_publishes_the_fixed_name(tmp_path):
    sys.path.insert(0, str(Path("scripts").resolve()))
    try:
        import run_A1
    finally:
        sys.path.pop(0)
    assert run_A1.main(["--set", "output.dir=" + (tmp_path / "o").as_posix()]) == 0
    d = tmp_path / "o" / "A1"
    pub = d / "a1_fixedpoints_2d.npz"
    rec = P.read_run_record(next(d.glob("A1_0000_*.json")))
    assert P.sha256_file(pub) == rec["outputs"][next(d.glob("A1_0000_*.npz")).name]


# --- DL-087: the A1 grid and the refinement widths are part of the hash and the record ----------

def test_a1_grid_and_widths_change_the_hash_and_other_kinds_are_unchanged(monkeypatch):
    from mprsurge import config as C
    a1_cfg = C.resolve_config(Path("configs/A1.yaml"))
    mf_cfg = C.resolve_config(Path("configs/base.yaml"))
    h_a1, h_mf = C.config_hash(a1_cfg), C.config_hash(mf_cfg)
    assert "a1_grid" in C.hash_view(a1_cfg) and "a1_grid" not in C.hash_view(mf_cfg)
    for key, new in (("band_cells", 5), ("box_cells", 11), ("n_eta", 242), ("n_J", 202),
                     ("eta_range", [-10.0, 3.0]), ("J_range", [0.0, 21.0])):
        with monkeypatch.context() as mp:
            mp.setitem(C.A1_GRID, key, new)
            assert C.config_hash(a1_cfg) != h_a1, key
            assert C.config_hash(mf_cfg) == h_mf, key
    assert C.config_hash(a1_cfg) == h_a1
    assert (B.N_ETA, B.N_J, B.BAND_CELLS, B.BOX_CELLS) == (C.A1_GRID["n_eta"], C.A1_GRID["n_J"],
                                                             C.A1_GRID["band_cells"], C.A1_GRID["box_cells"])


def test_a1_record_carries_the_grid_and_widths(a1):
    from mprsurge import config as C
    _, rec, _ = a1
    assert rec["flags"]["a1_grid"] == C.A1_GRID
