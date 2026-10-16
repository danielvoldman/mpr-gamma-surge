"""Timing driver and pure functions (MS3 step 3b, DL-094, DL-095). Toy cells of about 20 tau; no real timing."""
import importlib.util
import json

import pytest

from mprsurge import config as C
from mprsurge.analysis import timing as T

TOY = ["durations.baseline_s=0.05", "path.t_on_s=0.05", "durations.hold_s=0.05", "durations.discard_s=0.05",
       "path.T_ramp_s=0.1"]
SLOW_TOY = ["path.T_ramp_s=3.0"]            # a few thousand rhs calls, enough for the deadline check


@pytest.fixture(scope="module")
def drv():
    spec = importlib.util.spec_from_file_location("time_one_run", C.repo_root() / "scripts" / "time_one_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_summarise_repeats():
    s = T.summarise_repeats([3.0, 1.0, 2.0])
    assert (s["n"], s["min_s"], s["median_s"], s["max_s"], s["spread_s"]) == (3, 1.0, 2.0, 3.0, 2.0)
    assert s["spread_rel"] == pytest.approx(1.0) and s["stdev_s"] == pytest.approx(1.0)
    assert T.summarise_repeats([5.0])["stdev_s"] == 0.0
    with pytest.raises(ValueError):
        T.summarise_repeats([])


def test_s_per_tau_is_wall_over_tau():
    assert T.s_per_tau(33.0, 16500.0) == pytest.approx(0.002)
    with pytest.raises(ValueError):
        T.s_per_tau(1.0, 0.0)


def test_extrapolation_arithmetic_on_a_toy_table():
    mf = [(16500, 0.002), (201500, 0.003)]            # tau x s/tau
    heun = [(1.0e6, 2.0e-7), (3.0e6, 2.0e-7)]         # steps x s/step
    assert T.extrapolate(mf, 6) == pytest.approx((33.0 + 604.5) / 6)
    assert T.extrapolate(heun, 4) == pytest.approx(0.2)
    with pytest.raises(ValueError):
        T.extrapolate(mf, 0)


@pytest.mark.parametrize("cell", ["headline", "mode_n"])
def test_script_on_a_toy_cell_writes_a_timing_record(drv, tmp_path, cell):
    assert drv.main(["--cell", cell, "--repeat", "2", "--out-dir", str(tmp_path), "--set", *TOY]) == 0
    rec = json.loads((tmp_path / f"{cell}.json").read_text(encoding="utf-8"))
    assert rec["kind"] == "timing" and rec["status"] == "ok" and rec["cell"] == cell
    assert rec["flags"]["eta_path_status"] == "provisional"
    for key in ("commit", "dirty"):
        assert key in rec["git"]
    assert rec["packages"]["numpy"] and rec["os"] and rec["cpu"]["count"] and rec["config_hash"]
    t = rec["timing"]
    assert t["repeats_done"] == 2 and len(t["repeats"]) == 2 and t["limit_s"] == 3600.0
    assert t["tau_simulated"] == pytest.approx(T.tau_simulated(T.resolve_cell("configs/S5.yaml", cell, TOY)))
    assert t["median_s_per_tau"] == pytest.approx(t["summary"]["median_s"] / t["tau_simulated"])
    assert set(rec["machine_state"]) == {"before", "after"}
    if cell == "mode_n":
        assert t["compile_warmup_s"] is not None and t["solver_count_name"] == "n_steps"
        assert "UNVERIFIED" in rec["flags"]["sigma"]["status"]
    else:
        assert t["compile_warmup_s"] is None and t["solver_count_name"] == "nfev"


def test_limit_is_recorded_as_timeout_and_stops_the_repeats(drv, tmp_path):
    code = drv.main(["--cell", "headline", "--repeat", "3", "--limit-s", "1e-9", "--out-dir", str(tmp_path),
                     "--set", *TOY, *SLOW_TOY])
    rec = json.loads((tmp_path / "headline.json").read_text(encoding="utf-8"))
    assert code == 1 and rec["status"] == "timeout"
    assert rec["timing"]["repeats_done"] == 1 and rec["timing"]["repeats"][0]["status"] == "timeout"
    assert "summary" not in rec["timing"]


def test_failed_repeat_is_recorded_not_raised(drv, tmp_path):
    cfg = T.resolve_cell("configs/S5.yaml", "headline", TOY)
    cfg["solver"]["method"] = "NoSuchMethod"
    out = drv.time_cell(cfg, 3, 60.0, say=lambda m: None)
    assert out["status"] == "failed" and out["repeats_done"] == 1


def test_worker_summary_and_efficiency_arithmetic():
    b = [{"batch_wall_s": 100.0, "run_walls_s": [90.0, 100.0]}, {"batch_wall_s": 120.0, "run_walls_s": [110.0, 120.0]}]
    s = T.worker_summary(2, b)
    assert s["per_run"]["median_s"] == pytest.approx(105.0) and s["batch_wall"]["median_s"] == pytest.approx(110.0)
    assert s["throughput_runs_per_h"] == pytest.approx(2 * 3600 / 110.0)
    e = T.parallel_efficiency(s["throughput_runs_per_h"], 3600 / 100.0, 2)
    assert e["speedup"] == pytest.approx(100 / 55) and e["efficiency"] == pytest.approx(100 / 110)
    with pytest.raises(ValueError):
        T.worker_summary(2, [])


def test_worker_mode_runs_n_concurrent_copies_in_the_spawn_pool(drv, tmp_path):
    assert drv.main(["--cell", "headline", "--workers", "2", "--repeat", "2", "--out-dir", str(tmp_path), "--set", *TOY]) == 0
    rec = json.loads((tmp_path / "workers_2.json").read_text(encoding="utf-8"))
    assert rec["kind"] == "timing" and rec["status"] == "ok" and rec["timing"]["workers"] == 2
    t = rec["timing"]
    assert len(t["batches"]) == 2
    for b in t["batches"]:
        assert b["distinct_pids"] == 2 and len(b["copies"]) == 2 and all(c["status"] == "ok" for c in b["copies"])
        assert b["batch_wall_s"] >= max(b["run_walls_s"]) - 1e-6
    assert t["summary"]["throughput_runs_per_h"] == pytest.approx(2 * 3600 / t["summary"]["batch_wall"]["median_s"])
