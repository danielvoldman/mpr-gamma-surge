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


def test_script_on_a_toy_network_cell_records_the_update_count_alone_and_in_workers(drv, tmp_path):
    assert drv.main(["--cell", "net_1e3", "--repeat", "2", "--out-dir", str(tmp_path), "--set", *TOY]) == 0
    t = json.loads((tmp_path / "net_1e3.json").read_text(encoding="utf-8"))["timing"]
    cfg = T.resolve_cell("configs/S5.yaml", "net_1e3", TOY)
    assert t["repeats_done"] == 2 and t["compile_warmup_s"] is not None
    assert t["updates"] == pytest.approx(1000 * T.tau_simulated(cfg) / 1e-3) == pytest.approx(T.network_updates(cfg))
    assert drv.main(["--cell", "net_1e3", "--workers", "2", "--repeat", "1", "--out-dir", str(tmp_path), "--set", *TOY]) == 0
    w = json.loads((tmp_path / "workers_2.json").read_text(encoding="utf-8"))["timing"]
    assert w["updates"] == t["updates"] and w["batches"][0]["distinct_pids"] == 2 and w["status"] == "ok"
    cells = T.load_cells(tmp_path, ["net_1e3"])                       # the alone loader carries the count to the predictor
    assert cells["net_1e3"]["updates"] == t["updates"]


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


# ---- 3e: families, extrapolation and the launch rule (toy table, hand calculation) ----

TOY_CELLS = {"a": {"wall_s": 100.0, "tau": 1000.0, "steps": 1e6}, "b": {"wall_s": 50.0, "tau": 500.0, "steps": None}}
TOY_SPEC = {"rule_factor": 1.5, "workers_cap_h": 24.0, "no_cell": [], "rows": [
    {"id": "mf", "allowance_s": 1000.0, "parts": [{"label": "x", "kind": "mf_tau", "tau": 20000.0, "cell": "a"},
                                                  {"label": "y", "kind": "heun", "steps": 4e6, "cell": "a"},
                                                  {"label": "z", "kind": "runs", "n": 6, "cell": "b"}]},
    {"id": "tight", "allowance_s": 10.0, "parts": [{"label": "x", "kind": "mf_tau", "tau": 1000.0, "cell": "a"}]},
    {"id": "gap", "allowance_s": 10.0, "parts": [{"label": "x", "kind": "mf_tau", "tau": 1.0, "cell": "nope"}]},
    {"id": "half", "allowance_s": 10.0, "partial": True, "missing": ["S1"], "parts": [{"label": "x", "kind": "runs", "n": 1, "cell": "b"}]},
    {"id": "one", "allowance_s": 90.0, "parts": [{"label": "a", "kind": "single", "cell": "a"}, {"label": "b", "kind": "single", "cell": "b"}]}]}


def test_prediction_equals_hand_calculation_and_rule_is_per_row():
    rows = {r["id"]: r for r in T.evaluate_rows(TOY_SPEC, TOY_CELLS, 2.0)}
    # (20000 x 0.1 + 4e6 x 1e-4 + 6 x 50) / 2 = (2000 + 400 + 300) / 2
    assert rows["mf"]["prediction_s"] == pytest.approx(1350.0) and rows["mf"]["verdict"] == "PASS"   # <= 1500
    assert rows["tight"]["prediction_s"] == pytest.approx(50.0) and rows["tight"]["verdict"] == "FAIL"   # > 15
    assert rows["half"]["verdict"] == "FAIL (partial)"
    assert rows["one"]["prediction_s"] == 100.0 and rows["one"]["verdict"] == "PASS"   # alone, not divided; 100 <= 135
    assert rows["one"]["parts"][1]["verdict"] == "PASS"


def test_family_without_a_cell_is_reported_not_predicted():
    rows = {r["id"]: r for r in T.evaluate_rows(TOY_SPEC, TOY_CELLS, 2.0)}
    assert rows["gap"]["prediction_s"] is None and rows["gap"]["verdict"].startswith("no timing cell")
    assert T.total_verdict(TOY_SPEC, list(rows.values()))["judged"] is False


def test_shipped_families_file_loads_and_covers_the_table_rows():
    spec = T.load_families()
    ids = [r["id"] for r in spec["rows"]]
    assert {"single_run", "sweeps_headline_rate", "sweeps_p5_rate", "map1", "map2", "s13"} <= set(ids)
    for r in spec["rows"]:
        assert ("allowance_h" in r) != ("allowance_s" in r) and r["parts"]
        for p in r["parts"]:
            for cell in T.part_cells(p):
                assert cell in T.CELLS


# ---- 5f: network rows (toy numbers, hand calculation) ----

NET_CELLS = {"n1": {"wall_s": 30.0, "tau": 3000.0, "steps": None, "updates": 3.0e9},       # 1e-8 s per update
             "n3": {"wall_s": 90.0, "tau": 3000.0, "steps": None, "updates": 6.0e9},       # 1.5e-8 s per update
             "mf": {"wall_s": 10.0, "tau": 100.0, "steps": None}}


def test_p2_updates_matches_the_resolved_path_and_the_hand_count():
    cfg = T.resolve_cell("configs/S5.yaml", "net_1e4")
    # discard 2 + baseline 5 + 1.25 x 10 + hold 10 = 29.5 s = 2950 tau, dt 1e-3, N 1e4
    assert T.tau_simulated(cfg) == pytest.approx(2950.0)
    assert T.network_updates(cfg) == pytest.approx(2.95e10)
    assert T.p2_updates(1e4, 10.0) == pytest.approx(T.network_updates(cfg))
    cfg120 = T.resolve_cell("configs/S5.yaml", "net_1e4", ["path.T_ramp_s=120"])      # the 1.25 factor is the path's
    assert T.p2_updates(1e4, 120.0) == pytest.approx(T.network_updates(cfg120))


def test_network_cells_resolve_to_the_network_kind_and_n():
    for cell, n in (("net_1e3", 1000), ("net_1e4", 10000), ("net_3e4", 30000)):
        c = T.resolve_cell("configs/S5.yaml", cell)
        assert c["run"]["kind"] == "network" and c["network"]["N"] == n and c["seeds"]["spawn_key"] == [0]
        assert (c["model"]["type"], c["network"]["dt_tau"], c["path"]["name"], c["path"]["T_ramp_s"]) == ("M3", 1e-3, "path_hypoxia", 10.0)


def test_network_prediction_arithmetic_on_toy_numbers():
    spec = {"rule_factor": 1.5, "workers_cap_h": 24.0, "no_cell": [], "rows": [
        {"id": "net", "allowance_s": 1000.0, "parts": [
            {"label": "a", "kind": "net", "updates": 2.0e10, "cell": "n1"},                 # 2e10 x 1e-8 = 200 s
            {"label": "b", "kind": "net", "updates": 2.0e10, "cell": ["n1", "n3"]},         # slowest rate: 300 s
            {"label": "c", "kind": "net_p2", "runs": [{"n": 2, "N": 1e4, "T_ramp_s": 10, "cell": "n1"}]}]}]}   # 2 x 2.95e10 x 1e-8 = 590 s
    r = T.evaluate_rows(spec, NET_CELLS, 10.0)[0]
    assert [p["seconds"] for p in r["parts"]] == pytest.approx([20.0, 30.0, 59.0])           # divided by 10 workers
    assert r["prediction_s"] == pytest.approx(109.0) and r["verdict"] == "PASS"
    r1 = T.evaluate_rows(spec, NET_CELLS, 1.0)[0]                                             # 1090 s alone against 1500
    assert r1["prediction_s"] == pytest.approx(1090.0) and r1["verdict"] == "PASS"
    assert T.evaluate_rows({**spec, "rows": [{**spec["rows"][0], "allowance_s": 700.0}]}, NET_CELLS, 1.0)[0]["verdict"] == "FAIL"   # 1090 > 1050
    gap = T.evaluate_rows(spec, {"n1": NET_CELLS["n1"]}, 10.0)[0]
    assert gap["prediction_s"] is None and gap["verdict"].startswith("no timing cell")
    nocount = T.evaluate_rows(spec, {"n1": NET_CELLS["n1"], "n3": NET_CELLS["mf"]}, 10.0)[0]
    assert nocount["verdict"].startswith("no timing cell")                                    # a cell without an update count


def test_total_verdict_excludes_flagged_rows_and_reports_bounds():
    spec = {"workers_cap_h": 1.0, "no_cell": [], "rows": [{"id": "x"}, {"id": "dup", "in_total": False}, {"id": "p"}]}
    rows = [{"id": "x", "prediction_s": 1800.0, "partial": False, "allowance_s": 100.0},
            {"id": "dup", "prediction_s": 9e9, "partial": False, "allowance_s": 1.0},
            {"id": "p", "prediction_s": 600.0, "partial": True, "allowance_s": 3000.0}]
    t = T.total_verdict(spec, rows)
    assert t["judged"] is False and t["gaps"] == ["p"]
    assert t["lower_bound_h"] == pytest.approx(2400 / 3600) and t["conservative_h"] == pytest.approx(4800 / 3600)
    assert t["fails_on_lower_bound"] is False and t["pass"] is False
    rows[2].update(partial=False)
    t = T.total_verdict(spec, rows)
    assert t["judged"] is True and t["total_h"] == pytest.approx(2400 / 3600) and t["pass"] is True


def test_shipped_network_rows_count_the_plan_figures():
    spec = T.load_families()
    rows = {r["id"]: r for r in spec["rows"]}
    assert not rows["single_run"].get("in_total", True) and not rows["sweeps_headline_rate"].get("in_total", True)
    # S9: 4 N x 10 seeds on P2 60 s: the plan's 4.0e12 updates
    s9 = sum(r["n"] * T.p2_updates(r["N"], r["T_ramp_s"]) for p in rows["network_s9"]["parts"] for r in p["runs"])
    assert s9 == pytest.approx(4.0e12, rel=0.02)
    # S8 + S10 + S12 NC1 + K8 + sigma: the plan's about 2.0e12 (ours includes S3 and 3 seeds on the map cells)
    net = rows["network_s8_s10_s12_k8_sigma"]["parts"]
    tot = sum(p["updates"] if p["kind"] == "net" else sum(r["n"] * T.p2_updates(r["N"], r["T_ramp_s"]) for r in p["runs"]) for p in net)
    assert 1.5e12 < tot < 3.0e12
