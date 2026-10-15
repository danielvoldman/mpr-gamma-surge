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


def test_headline_is_p2_ref_devalle_with_a_provisional_path():
    cfg = T.resolve_cell(S5, "headline")
    assert (cfg["path"]["name"], cfg["path"]["T_ramp_s"], cfg["path"]["profile"]) == ("path_hypoxia", 120.0, "linear")
    assert (cfg["model"]["type"], cfg["model"]["J"], cfg["model"]["Delta"], cfg["model"]["tau_d_ms"]) == ("M3", -21.0, 0.3, 5.0)
    assert (cfg["path"]["eta_start"], cfg["path"]["eta_peak"]) == (2.5, 6.0)
    assert cfg["path"]["eta_path_status"] == "provisional"
    assert cfg["model"]["I_drive"] == 0.0 and cfg["run"]["kind"] == "mf" and cfg["solver"]["method"] == "DOP853"
    assert T.tau_simulated(cfg) == pytest.approx(16500.0)           # 5 + 1.25 x 120 + 10 s (CP14)


def test_eta_path_values_change_the_hash():
    a = T.resolve_cell(S5, "headline")
    b = T.resolve_cell(S5, "headline", ["path.eta_peak=5.0"])
    assert C.config_hash(a) != C.config_hash(b)


@pytest.mark.parametrize("cell,Delta", [("delta_0.01", 0.01), ("delta_0.6", 0.6)])
def test_delta_cells_change_only_delta(cell, Delta):
    h, c = T.resolve_cell(S5, "headline"), T.resolve_cell(S5, cell)
    assert c["model"]["Delta"] == Delta
    for sec in ("path", "solver", "run", "durations"):
        assert c[sec] == h[sec]
    assert {k: v for k, v in c["model"].items() if k != "Delta"} == {k: v for k, v in h["model"].items() if k != "Delta"}


def test_p5_1000_lasts_5_plus_2000_plus_10_s():
    c = T.resolve_cell(S5, "p5_1000")
    assert c["path"]["name"] == "path_updown" and c["path"]["eta_path_status"] == "provisional"
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


def test_unknown_cell_is_refused():
    with pytest.raises(C.ConfigError):
        T.resolve_cell(S5, "nope")


def test_m2_ramp_starts_at_a_unique_stable_fixed_point():
    from mprsurge.models.fixed_points import classify_all
    c = T.resolve_cell(S5, "m2_ramp")
    for eta in (c["path"]["eta_start"], c["path"]["eta_peak"]):
        assert [l for _, l, _ in classify_all(eta, 15.0, 1.0, 0.0)].count("stable_node") + \
               [l for _, l, _ in classify_all(eta, 15.0, 1.0, 0.0)].count("stable_focus") == 1


def test_s5_dry_run_record_carries_the_provisional_status(tmp_path):
    from mprsurge import provenance as P
    from mprsurge import run as R
    assert R.main(["--config", S5, "--dry-run", "--set", f"output.dir={tmp_path.as_posix()}"]) == 0
    rec = P.read_run_record(next(tmp_path.rglob("*.json")))
    assert rec["config"]["path"]["eta_path_status"] == "provisional" and rec["config"]["path"]["eta_start"] == 2.5
