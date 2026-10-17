"""Timing cells (MS3 step 3a, DL-094, DL-095): resolution, provisional eta path, durations, M2 ramp. Nothing integrates."""
import pytest

from mprsurge import config as C
from mprsurge import ramps as R
from mprsurge.analysis import bifurcation as B
from mprsurge.analysis import timing as T
from mprsurge.units import s_to_tau

S5 = "configs/S5.yaml"


def test_every_cell_file_exists_and_the_list_matches():
    files = sorted(p.stem for p in (C.repo_root() / "configs" / "timing").glob("*.yaml"))
    assert files == sorted(T.CELLS)


def test_headline_is_p2_ref_devalle_with_an_A4_path():
    cfg = T.resolve_cell(S5, "headline")
    assert (cfg["path"]["name"], cfg["path"]["T_ramp_s"], cfg["path"]["profile"]) == ("path_hypoxia", 120.0, "linear")
    assert (cfg["model"]["type"], cfg["model"]["J"], cfg["model"]["Delta"], cfg["model"]["tau_d_ms"]) == ("M3", -21.0, 0.3, 5.0)
    assert (cfg["path"]["eta_start"], cfg["path"]["eta_peak"]) == pytest.approx((1.396046, 4.896046), abs=1e-6)   # the DL-098 values
    assert cfg["path"]["eta_path_status"] == "A4"
    assert cfg["model"]["I_drive"] == 0.0 and cfg["run"]["kind"] == "mf" and cfg["solver"]["method"] == "DOP853"
    assert T.tau_simulated(cfg) == pytest.approx(16500.0)           # 5 + 1.25 x 120 + 10 s (CP14)


def test_eta_path_values_change_the_hash():
    a = T.resolve_cell(S5, "headline")
    b = T.resolve_cell(S5, "headline", ["path.eta_H=3.0"])
    assert C.config_hash(a) != C.config_hash(b)


@pytest.mark.parametrize("cell,Delta", [("delta_0.01", 0.01), ("delta_0.6", 0.6)])
def test_delta_cells_change_only_delta(cell, Delta):
    h, c = T.resolve_cell(S5, "headline"), T.resolve_cell(S5, cell)
    assert c["model"]["Delta"] == Delta
    for sec in ("solver", "run", "durations"):
        assert c[sec] == h[sec]
    assert {k: v for k, v in c["path"].items() if k not in ("eta_H", "eta_start", "eta_peak", "eps")} ==         {k: v for k, v in h["path"].items() if k not in ("eta_H", "eta_start", "eta_peak", "eps")}   # own D12 path per Delta (DL-098)
    assert {k: v for k, v in c["model"].items() if k != "Delta"} == {k: v for k, v in h["model"].items() if k != "Delta"}


def test_p5_1000_lasts_5_plus_2000_plus_10_s():
    c = T.resolve_cell(S5, "p5_1000")
    assert c["path"]["name"] == "path_updown" and c["path"]["eta_path_status"] == "A4"
    assert T.tau_simulated(c) == pytest.approx(s_to_tau(5 + 2 * 1000 + 10, 10.0)) == pytest.approx(201500.0)


def test_radau_cell_and_mode_n_cell():
    r = T.resolve_cell(S5, "radau_1e-12")
    assert (r["solver"]["method"], r["solver"]["rtol"], r["run"]["kind"]) == ("Radau", 1e-12, "mf")
    n = T.resolve_cell(S5, "mode_n")
    assert n["run"]["kind"] == "mf_noisy" and n["noise"]["sigma"] == 1e-3 and n["noise"]["dt_tau"] == 1e-3
    assert T.tau_simulated(n) == pytest.approx(16700.0)             # 2 s discard + 165 s


def test_m2_ramp_is_path_eta_with_model_m2_between_the_folds_pm_1():
    c = T.resolve_cell(S5, "m2_ramp")
    assert (c["model"]["type"], c["model"]["J"], c["model"]["Delta"], c["path"]["name"]) == ("M2", 15.0, 1.0, "path_eta")
    lo, hi = sorted(B.fold_etas(15.0, 1.0))
    assert c["path"]["eta_start"] == pytest.approx(lo - 1.0, abs=1e-12) and c["path"]["eta_peak"] == pytest.approx(hi + 1.0, abs=1e-12)
    assert c["path"]["eta_path_status"] == "explicit"
    path = R.make_path(c)                                            # an existing path kind: no new code needed
    assert path.eta(path.t_on) == pytest.approx(c["path"]["eta_start"])
    assert path.eta(path.t_ramp_end) == pytest.approx(c["path"]["eta_peak"])
    assert float(path.J(0.0)) == 15.0 and float(path.Delta(0.0)) == 1.0
    assert T.tau_simulated(c) == pytest.approx(s_to_tau(5 + 1000 + 10, 10.0))


def test_t10_radau_cells_and_plan_rule_delta_paths():
    for cell, rtol in (("radau_1e-12_t10", 1e-12), ("radau_1e-10_t10", 1e-10)):
        c = T.resolve_cell(S5, cell)
        assert (c["solver"]["method"], c["solver"]["rtol"], c["path"]["T_ramp_s"]) == ("Radau", rtol, 10.0)
        assert T.tau_simulated(c) == pytest.approx(s_to_tau(5 + 12.5 + 10, 10.0))
    # D12 with eta_H from the scan (DL-098); the cells carry the A4 eta_H since 5i (DL-122): eta_start = eta_H - 1.5, eta_peak = max(4, eta_H + 2)
    for cell, eta_H in (("delta_0.01", 0.393453), ("headline", 2.896046), ("delta_0.6", 4.774430)):
        c = T.resolve_cell(S5, cell)
        assert c["path"]["eta_start"] == pytest.approx(eta_H - 1.5, abs=1e-6)
        assert c["path"]["eta_peak"] == pytest.approx(max(4.0, eta_H + 2.0), abs=1e-6)
        assert c["path"]["eta_path_status"] == "A4"


def test_scanned_eta_H_is_where_the_stable_root_loses_stability():
    from mprsurge.models.fixed_points import classify_all
    for Delta, eta_H in ((0.01, 0.393453), (0.3, 2.896046), (0.6, 4.774430)):
        below = [l for _, l, _ in classify_all(eta_H - 1e-3, -21.0, Delta, 0.0, "M3", 0.5)]
        above = [l for _, l, _ in classify_all(eta_H + 1e-3, -21.0, Delta, 0.0, "M3", 0.5)]
        assert below == ["stable"] and "stable" not in above


def test_unknown_cell_is_refused():
    with pytest.raises(C.ConfigError):
        T.resolve_cell(S5, "nope")


def test_m2_ramp_starts_at_a_unique_stable_fixed_point():
    from mprsurge.models.fixed_points import classify_all
    c = T.resolve_cell(S5, "m2_ramp")
    for eta in (c["path"]["eta_start"], c["path"]["eta_peak"]):
        assert [l for _, l, _ in classify_all(eta, 15.0, 1.0, 0.0)].count("stable_node") + \
               [l for _, l, _ in classify_all(eta, 15.0, 1.0, 0.0)].count("stable_focus") == 1


def test_s5_dry_run_record_carries_the_A4_status(tmp_path):
    from mprsurge import provenance as P
    from mprsurge import run as R
    assert R.main(["--config", S5, "--dry-run", "--set", f"output.dir={tmp_path.as_posix()}"]) == 0
    rec = P.read_run_record(next(tmp_path.rglob("*.json")))
    assert rec["config"]["path"]["eta_path_status"] == "A4" and rec["config"]["path"]["eta_start"] == pytest.approx(1.396046, abs=1e-6)


def test_corner_cells_and_weighted_family_estimate():
    from mprsurge.models.fixed_points import classify_all
    for cell, Delta, td in (("delta_0.01_td1", 0.01, 1.0), ("delta_0.01_td50", 0.01, 50.0),
                            ("delta_0.6_td1", 0.6, 1.0), ("delta_0.6_td50", 0.6, 50.0)):
        c = T.resolve_cell(S5, cell)
        assert (c["model"]["Delta"], c["model"]["tau_d_ms"], c["path"]["T_ramp_s"]) == (Delta, td, 120.0)
        assert c["path"]["eta_path_status"] == "A4"
        for eta in (c["path"]["eta_start"], c["path"]["eta_peak"]):          # both ends have the stable root (the run can start)
            assert [l for _, l, _ in classify_all(eta, -21.0, Delta, 0.0, "M3", td / 10.0)].count("stable") <= 1
        assert [l for _, l, _ in classify_all(c["path"]["eta_start"], -21.0, Delta, 0.0, "M3", td / 10.0)] == ["stable"]
    # toy: constant cost over the corners gives cost x cells / workers; the grid is 30 x 30
    grid = T.map_grid()
    assert grid.shape == (900, 2) and grid[0].tolist() == [0.01, 1.0] and grid[-1].tolist() == pytest.approx([0.6, 50.0])
    corners = [(0.01, 1, 100.0), (0.01, 50, 100.0), (0.6, 1, 100.0), (0.6, 50, 100.0)]
    est = T.weighted_family_estimate(corners, grid, 6)
    assert est["total_s"] == pytest.approx(900 * 100.0 / 6)
    with pytest.raises(ValueError):
        T.weighted_family_estimate(corners, [(0.7, 5.0)], 6)


def test_cell_paths_equal_the_d12_rule_from_the_a4_eta_H():
    """5i (DL-122): each cell's eta_H is the A4 value (hopf.lowest_eta_hopf on the A4 eta_bar grid), not a scan."""
    from mprsurge.analysis import hopf
    P = hopf.load_a4_params()
    grid = hopf._grid(P["grids"]["eta_bar"])
    for cell in ("headline", "delta_0.01", "delta_0.6", "delta_0.01_td1", "delta_0.01_td50", "delta_0.6_td1"):
        c = T.resolve_cell(S5, cell)
        hop = hopf.lowest_eta_hopf(grid, c["model"]["J"], c["model"]["Delta"], c["model"]["tau_d_ms"] / c["model"]["tau_ms"])
        assert c["path"]["eta_path_status"] == "A4" and c["path"]["eta_H"] == pytest.approx(hop["eta_bar"], abs=1e-12)
        assert c["path"]["eta_start"] == pytest.approx(hop["eta_bar"] - 1.5, abs=1e-12)
        assert c["path"]["eta_peak"] == pytest.approx(max(4.0, hop["eta_bar"] + 2.0), abs=1e-12)
    # no Hopf crossing at Delta 0.6, tau_d 50 ms: the corner keeps the headline path (CP20, DL-100)
    c = T.resolve_cell(S5, "delta_0.6_td50")
    assert hopf.lowest_eta_hopf(grid, -21.0, 0.6, 5.0) is None
    h = T.resolve_cell(S5, "headline")
    assert (c["path"]["eta_start"], c["path"]["eta_peak"]) == (h["path"]["eta_start"], h["path"]["eta_peak"])
    assert T.resolve_cell(S5, "m2_ramp")["path"]["eta_path_status"] == "explicit"
