"""S2 config and dry run (MS4 step 4b, DL-107). Nothing integrates; outputs go to tmp_path."""
import importlib.util
import json

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import run as R
from mprsurge.analysis import bifurcation as B
from mprsurge.units import s_to_tau


@pytest.fixture(scope="module")
def drv():
    spec = importlib.util.spec_from_file_location("run_S2", C.repo_root() / "scripts" / "run_S2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sets(tmp_path):
    return ["--set", f"output.dir={(tmp_path / 'out').as_posix()}"]


def test_s2_resolves_with_the_ruled_setup():
    plan = R.build_plan("configs/S2.yaml")
    c = plan.cfg
    assert (c["run"]["id"], c["run"]["kind"], c["model"]["type"]) == ("S2", "mf", "M2")
    assert (c["model"]["J"], c["model"]["Delta"], c["model"]["tau_ms"], c["model"]["I_drive"]) == (15.0, 1.0, 10.0, 0.0)
    assert c["path"]["name"] == "path_eta" and c["path"]["profile"] == "linear" and c["path"]["eta_path_status"] == "explicit"
    assert (c["durations"]["baseline_s"], c["durations"]["hold_s"]) == (5.0, 10.0) and c["path"]["t_on_s"] == 5.0
    assert c["analysis"]["band_primary_hz"] == [25.0, 100.0]
    assert (c["solver"]["method"], c["solver"]["rtol"], c["solver"]["atol"], c["solver"]["max_step_tau"]) == ("DOP853", 1e-10, 1e-12, 0.05)
    assert c["solver"]["dt_out_ms"] == 1.0


def test_thirteen_log_spaced_ramps_from_1_to_1000_s():
    plan = R.build_plan("configs/S2.yaml")
    T = [x["cfg"]["path"]["T_ramp_s"] for x in plan.cells]
    assert len(T) == 13 and T[0] == 1.0 and T[-1] == 1000.0
    np.testing.assert_allclose(T, np.logspace(0, 3, 13), rtol=1e-8)
    assert len({x["hash12"] for x in plan.cells}) == 13


def test_eta_path_ends_one_beyond_each_a1_fold(drv):
    plan = R.build_plan("configs/S2.yaml")
    lo, up = drv.fold_values(plan.cfg)
    assert (lo, up) == pytest.approx((-5.743527161657844, -3.136134086195692), abs=1e-12)
    np.testing.assert_allclose(sorted(B.fold_etas(15.0, 1.0)), [lo, up], rtol=0, atol=0)
    assert plan.cfg["path"]["eta_start"] == pytest.approx(lo - 1, abs=1e-12)
    assert plan.cfg["path"]["eta_peak"] == pytest.approx(up + 1, abs=1e-12)
    drv.check_path(plan.cfg, lo, up)
    with pytest.raises(C.ConfigError):
        drv.check_path(plan.cfg, lo + 0.01, up)


def test_hash_changes_with_path_or_t_ramp():
    base = R.build_plan("configs/S2.yaml").cells
    moved = R.build_plan("configs/S2.yaml", ["path.eta_peak=-2.0"]).cells
    t = R.build_plan("configs/S2.yaml", ["sweep.T_ramp_values=[1.0, 2.0]"]).cells
    assert base[0]["hash12"] != moved[0]["hash12"]
    assert t[1]["hash12"] != base[1]["hash12"]


def test_breakpoints_of_every_cell(drv):
    for c in R.build_plan("configs/S2.yaml").cells:
        r = drv.check_breakpoints(c["cfg"])
        T = c["cfg"]["path"]["T_ramp_s"]
        assert r["t_on"] == pytest.approx(500.0)
        assert r["t_ramp_end"] == pytest.approx(s_to_tau(5.0 + T, 10.0))
        assert r["t_end"] == pytest.approx(s_to_tau(5.0 + T + 10.0, 10.0))


def test_dry_run_prints_folds_and_runs_and_writes_13_records(drv, tmp_path, capsys):
    assert drv.main(["--dry-run", *sets(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "-5.743527161657844" in out and "-3.1361340861956917" in out
    assert "S2 runs: 13" in out and "S2 total simulated: 247860 tau" in out and "1000.0000" in out
    dry = sorted((tmp_path / "out" / "S2").glob("*.dry.json"))
    assert len(dry) == 13
    rec = json.loads(dry[0].read_text())
    assert rec["status"] == "dry_run" and rec["dry_run"] is True
    assert not list((tmp_path / "out" / "S2").glob("*.npz"))          # nothing integrated


def test_dry_run_stops_on_an_eta_path_off_the_folds(drv, tmp_path, capsys):
    assert drv.main(["--dry-run", "--set", "path.eta_peak=-2.0", *sets(tmp_path)]) == 2
    assert "not (fold_low - 1, fold_up + 1)" in capsys.readouterr().err
