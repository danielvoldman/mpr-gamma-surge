"""G0 part 1, K1 to K5 on reduced grids (plan Table 10.1 test_replication; MS2 step 2e, DL-091). Slow.

Each target is recomputed here from the library on a reduced grid or a single run, with the tolerances read from
the frozen configs/replication.yaml (SHA-256 checked first, DL-084). K7 to K11 belong to MS5 and are not here.
The last test checks the A0 table written by scripts/run_A0.py.
"""
import numpy as np
import pytest
import yaml
from scipy.integrate import solve_ivp

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import bifurcation as B
from mprsurge.analysis import replication as RP
from mprsurge.analysis import ring as RG
from mprsurge.models.fixed_points import classify_all
from mprsurge.models.mpr2d import rhs_2d

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def rep():
    path = C.repo_root() / "configs/replication.yaml"
    assert P.sha256_file(path) == RP.FROZEN_SHA256
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def test_k1_twenty_r_values_pass_on_local_grids_at_half_spacing_near_the_fold(rep):
    cell = (rep["K1"]["cell"]["d_eta_bar"], rep["K1"]["cell"]["d_J"])
    rs = B.k1_points()
    assert len(rs) == rep["K1"]["n_r"] == 20
    eta0, J0 = B.sn_curve_2d(rs)
    de, dJ = B.D_ETA / 2, B.D_J / 2
    for k, r in enumerate(rs):
        eg = np.arange(np.floor(eta0[k] / de) * de - 6 * B.D_ETA, eta0[k] + 6 * B.D_ETA, de)
        Jg = np.arange(np.floor(J0[k] / dJ) * dJ - 6 * B.D_J, J0[k] + 6 * B.D_J, dJ)
        EG, JG = np.meshgrid(eg, Jg, indexing="ij")
        n = B.classify_nodes(EG.ravel(), JG.ravel())["n_roots"].reshape(EG.shape)
        ok, _, _ = B.k1_check(np.array([r]), eg, Jg, B.count_change_nodes(n), cell)
        assert ok[0], f"K1 fails at r = {r:.4f}"


def test_k2_discriminant_changes_sign_within_one_cell_of_eta_f_on_reduced_rows(rep):
    cell = (rep["K2"]["cell"]["d_eta_bar"], rep["K2"]["cell"]["d_J"])
    J_rows = np.array([2.0, 5.0, 10.0, 15.0, 19.0])     # eta_f(J) inside the A1 eta range (J <= 19.8, DL-086)
    eta_g = np.arange(-10.0, 2.0 + 1e-9, B.D_ETA)
    pts = [[B.classify_point(e, J) for J in J_rows] for e in eta_g]
    disc = np.array([[p[4][p[0] - 1] for p in row] for row in pts])       # highest-r root (DL-086 4)
    _, ok, _, nchg = B.k2_check(J_rows, eta_g, disc, cell)
    assert ok.all() and (nchg == 1).all()


def test_k3_exactly_a_focus_a_node_and_a_saddle(rep):
    pt = rep["K3"]["point"]
    labels = sorted(lab for _, lab, _ in classify_all(pt["eta_bar_over_Delta"], pt["J_over_sqrtDelta"], 1.0))
    assert labels == ["saddle", "stable_focus", "stable_node"]


def test_k4_mf_frequency_and_decay_within_tolerance(rep):
    mf = rep["K4"]["mean_field"]
    eta, J, D, I = -5.0, 15.0, 1.0, 3.0
    y0 = [y for y, lab, _ in classify_all(eta, J, D, 0.0) if lab == "stable_node"][0]
    t = np.arange(0, 60.0001, 0.1)
    sol = solve_ivp(lambda tt, y: rhs_2d(tt, y, eta, J, D, I), (0, 60), y0, method="DOP853", t_eval=t,
                    rtol=1e-10, atol=1e-12)
    y_star, lam = RG.post_step_focus(eta, J, D, I)
    k = RG.k4_mf_check(t, sol.y[0], y_star[0], lam, mf["tail_fit_fraction"], mf["tolerance_frequency_rel"],
                       mf["tolerance_decay_rel"], C.A2_WINDOW["t_end_tau"])
    assert k["pass"] and k["rel_err_frequency"] <= mf["tolerance_frequency_rel"]
    assert k["rel_err_decay"] <= mf["tolerance_decay_rel"]


def test_k5_one_burst_per_period_with_period_40(rep):
    k5 = rep["K5"]
    pt = k5["point"]
    mid, _, _ = RP.k5_mid(pt["eta_bar"], pt["J"], pt["Delta"])
    dt = 0.1
    t = np.arange(0.0, (k5["transient_periods"] + k5["checked_periods"]) * k5["period"] + dt / 2, dt)
    w = k5["forcing"]["omega"]
    sol = solve_ivp(lambda tt, y: rhs_2d(tt, y, pt["eta_bar"], pt["J"], pt["Delta"], k5["forcing"]["I0"] * np.sin(w * tt)),
                    [0, t[-1]], _low_state(pt), method="DOP853", rtol=1e-10, atol=1e-12, t_eval=t)
    res = RP.k5_check(t, sol.y[0], mid, k5["period"], k5["transient_periods"], k5["checked_periods"], k5["period_tol"])
    assert res["pass"], res


def _low_state(pt):
    return np.asarray([y for y, lab, _ in classify_all(pt["eta_bar"], pt["J"], pt["Delta"], 0.0)
                       if lab == "stable_node"][0], float)


def test_a0_table_has_one_passing_row_per_target_and_the_frozen_hash():
    from mprsurge import run as R
    plan = R.build_plan("configs/A0.yaml")
    rec_path = P.find_complete(plan.out_dir, plan.cells[0]["cfg"])
    assert rec_path is not None, "run scripts/run_A0.py"
    rec = P.read_run_record(rec_path)
    assert rec["criteria_sha256"] == RP.FROZEN_SHA256 and rec["status"] == "ok"
    with np.load(rec_path.with_suffix(".npz")) as z:
        arrays = {k: z[k] for k in z.files}
    assert list(arrays["col_target"]) == ["K1", "K2", "K3", "K4-MF", "K5"] and arrays["col_pass"].all()
