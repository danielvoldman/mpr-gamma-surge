"""Runner (plan 10.4, Table 10.1; DL-056, DL-068). Part 1 uses toy tasks (tests/toy_task.py);
part 2 (sub-step 1b-ii, at the end) uses the real run_mf and run_mf_noisy."""
import csv
import json
import logging
import os
import re
import subprocess
import sys
import time

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R


def write_cfg(tmp_path, sweep="x_name: model.Delta, x_values: [0.2, 0.3, 0.4]", extra="", out="out"):
    f = tmp_path / "T.yaml"
    f.write_text(f"run: {{id: T, kind: mf{extra}}}\n"
                 f"output: {{dir: \"{(tmp_path / out).as_posix()}\"}}\n"
                 f"sweep: {{{sweep}}}\n")
    return f


def out_dir(tmp_path, out="out"):
    return tmp_path / out / "T"


def records(d, dry=False):
    return {p.name: json.loads(p.read_text()) for p in sorted(d.glob("T_*.json"))
            if p.name.endswith(".dry.json") == dry}


@pytest.fixture
def toy(monkeypatch):
    monkeypatch.setitem(R.TASKS, "mf", "toy_task:run")


def manifest(d):
    with open(d / "manifest.csv", newline="") as fh:
        return list(csv.DictReader(fh))


# --- dry-run (MS1 done-when) ----------------------------------------------------------

def test_dry_run_writes_records_with_commit_and_integrates_nothing(tmp_path):
    f = write_cfg(tmp_path)
    assert R.main(["--config", str(f), "--dry-run"]) == 0
    d = out_dir(tmp_path)
    dry = sorted(d.glob("*.dry.json"))
    assert len(dry) == 3
    rec = json.loads(dry[0].read_text())
    assert rec["status"] == "dry_run" and rec["dry_run"] is True
    assert re.fullmatch(r"[0-9a-f]{40}", rec["git"]["commit"])
    assert rec["config_hash12"] in dry[0].name
    assert rec["flags"]["eta_path_status"] == "unresolved"   # a dry-run needs no eta path
    assert not list(d.glob("*.npz")) and not (d / "manifest.csv").exists()


def test_dry_run_via_python_dash_m(tmp_path):
    f = write_cfg(tmp_path)
    out = subprocess.run([sys.executable, "-m", "mprsurge.run", "--config", str(f), "--dry-run"],
                         capture_output=True, text=True, cwd=tmp_path, timeout=120)
    assert out.returncode == 0, out.stderr
    rec = json.loads(next(out_dir(tmp_path).glob("*.dry.json")).read_text())
    assert re.fullmatch(r"[0-9a-f]{40}", rec["git"]["commit"])


def test_dry_run_marks_already_complete(tmp_path, toy):
    f = write_cfg(tmp_path)
    assert R.main(["--config", str(f)]) == 0
    assert R.main(["--config", str(f), "--dry-run"]) == 0
    msgs = {r["message"] for r in records(out_dir(tmp_path), dry=True).values()}
    assert msgs == {"already complete"}


def test_config_error_returns_2(tmp_path, capsys):
    f = write_cfg(tmp_path, extra=", bogus: 1")
    assert R.main(["--config", str(f), "--dry-run"]) == 2
    assert "unknown key" in capsys.readouterr().err
    assert R.main(["--config", str(tmp_path / "missing.yaml"), "--dry-run"]) == 2


def test_real_run_without_task_module_is_reported(tmp_path, capsys):
    if R.importlib.util.find_spec("mprsurge.simulate_mf") is not None:
        pytest.skip("simulate_mf exists")
    assert R.main(["--config", str(write_cfg(tmp_path))]) == 2
    assert "not available" in capsys.readouterr().err


# --- plan expansion ------------------------------------------------------------------------

def test_sweep_product_hashes_and_overrides(tmp_path):
    f = write_cfg(tmp_path, sweep="x_name: model.Delta, x_values: [0.1, 0.2], "
                                  "y_name: model.J, y_values: [-20, -10, -5], "
                                  "T_ramp_values: [10, 120]")
    plan = R.build_plan(str(f), ["solver.rtol=1e-9"])
    assert len(plan.cells) == 2 * 3 * 2
    assert len({c["hash12"] for c in plan.cells}) == 12
    assert len({c["name"] for c in plan.cells}) == 12
    c0 = plan.cells[0]["cfg"]
    assert c0["sweep"] == {k: None for k in c0["sweep"]}
    ov = c0["_resolved_from"]["overrides"]
    assert ov["solver.rtol"] == "1e-9" and ov["model.Delta"] == 0.1 and ov["path.T_ramp_s"] == 10
    assert plan.family == "T" and plan.out_dir == tmp_path / "out" / "T"
    assert all(c["cfg"]["seeds"]["spawn_key"] is None for c in plan.cells)


def test_no_sweep_is_one_cell(tmp_path):
    f = write_cfg(tmp_path, sweep="x_name: null")
    assert len(R.build_plan(str(f)).cells) == 1


def test_bad_sweep_axes_raise(tmp_path):
    for sweep in ("x_name: model.Delta", "x_name: model.nope, x_values: [1]",
                  "x_name: path.eps, x_values: [1]",
                  "x_name: path.T_ramp_s, x_values: [1], T_ramp_values: [2]"):
        with pytest.raises(C.ConfigError):
            R.build_plan(str(write_cfg(tmp_path, sweep=sweep)))


def noisy_cfg(tmp_path, values, n_seeds=3):
    f = write_cfg(tmp_path, extra=", workers: 1", sweep=f"x_name: model.Delta, x_values: {values}")
    f.write_text(f.read_text().replace("kind: mf", "kind: mf_noisy") + f"seeds: {{n_seeds: {n_seeds}}}\n")
    return f


def test_noisy_runs_get_seed_children(tmp_path):
    plan = R.build_plan(str(noisy_cfg(tmp_path, "[0.2, 0.3]")))
    assert len(plan.cells) == 6
    assert len({c["hash12"] for c in plan.cells}) == 6
    keys = [c["cfg"]["seeds"]["spawn_key"] for c in plan.cells]
    assert keys == [[0], [1], [2], [0], [1], [2]]          # DL-069: spawn_key = [seed_index]


def test_same_seed_index_gives_same_key_in_every_cell_and_the_child_stream(tmp_path):
    plan = R.build_plan(str(noisy_cfg(tmp_path, "[0.2, 0.25, 0.3]", n_seeds=4)))
    by_seed = {}
    for c in plan.cells:
        by_seed.setdefault(c["cfg"]["seeds"]["spawn_key"][0], []).append(c)
    assert sorted(by_seed) == [0, 1, 2, 3] and all(len(v) == 3 for v in by_seed.values())
    root = plan.cells[0]["cfg"]["seeds"]["root_seed"]
    children = P.seed_sequence(root, 4)
    streams = set()
    for s, cells in by_seed.items():
        draws = {tuple(P.seed_from_key(root, c["cfg"]["seeds"]["spawn_key"]).generate_state(4)) for c in cells}
        assert draws == {tuple(children[s].generate_state(4))}   # equals SeedSequence(root).spawn(n_seeds)[s]
        streams |= draws
    assert len(streams) == 4                               # different seed indices differ


def test_inserting_a_sweep_value_or_a_seed_keeps_existing_hashes(tmp_path):
    def hashes(values, n_seeds=3):
        plan = R.build_plan(str(noisy_cfg(tmp_path, values, n_seeds)))
        return {(c["cfg"]["model"]["Delta"], c["cfg"]["seeds"]["spawn_key"][0]): c["hash12"] for c in plan.cells}
    before = hashes("[0.2, 0.3]")
    after = hashes("[0.2, 0.25, 0.3]")
    assert len(before) == 6 and len(after) == 9
    assert all(after[k] == h for k, h in before.items())
    grown = hashes("[0.2, 0.3]", n_seeds=5)
    assert len(grown) == 10 and all(grown[k] == h for k, h in before.items())


def test_deterministic_mf_has_null_spawn_key(tmp_path):
    plan = R.build_plan(str(write_cfg(tmp_path)))
    assert all(c["cfg"]["seeds"]["spawn_key"] is None for c in plan.cells)


def test_workers_flag_is_an_override(tmp_path):
    plan = R.build_plan(str(write_cfg(tmp_path)), workers=4)
    assert plan.cfg["run"]["workers"] == 4
    assert plan.cells[0]["cfg"]["_resolved_from"]["overrides"]["run.workers"] == 4


# --- running: toy task, in process --------------------------------------------------------------

def test_run_writes_outputs_manifest_and_skips_on_rerun(tmp_path, toy):
    f = write_cfg(tmp_path, extra=", wall_limit_s: 100")
    d = out_dir(tmp_path)
    assert R.main(["--config", str(f)]) == 0
    recs = records(d)
    assert len(recs) == 3 and {r["status"] for r in recs.values()} == {"ok"}
    for name, rec in recs.items():
        stem = name[:-5]
        assert set(rec["outputs"]) == {f"{stem}.npz", f"{stem}_params.md"}
        for fn, sha in rec["outputs"].items():
            assert R.P.sha256_file(d / fn) == sha
        with np.load(d / f"{stem}.npz") as z:
            assert np.allclose(z["v"], rec["config"]["model"]["Delta"] * np.arange(5.0))
        assert rec["flags"]["deadline_given"] is True and rec["wall_time_s"] >= 0
        assert "model.tau_ms" in (d / f"{stem}_params.md").read_text()
    assert (d / "run.log").exists() and not list(d.glob("*.tmp"))
    assert [r["status"] for r in manifest(d)] == ["ok"] * 3
    mtimes = {p.name: p.stat().st_mtime_ns for p in d.glob("*.npz")}
    assert R.main(["--config", str(f)]) == 0
    assert [r["status"] for r in manifest(d)][3:] == ["skipped"] * 3
    assert {p.name: p.stat().st_mtime_ns for p in d.glob("*.npz")} == mtimes


def test_failure_timeout_and_warning_are_recorded_and_retried(tmp_path, toy):
    f = write_cfg(tmp_path, sweep="x_name: model.Delta, x_values: [0.2, 0.99, 0.98, 0.97]")
    d = out_dir(tmp_path)
    assert R.main(["--config", str(f)]) == 1
    by_delta = {r["config"]["model"]["Delta"]: r for r in records(d).values()}
    assert by_delta[0.2]["status"] == "ok"
    bad = by_delta[0.99]
    assert bad["status"] == "failed" and "forced solver failure" in bad["message"]
    assert "RuntimeError" in bad["flags"]["traceback"] and bad["outputs"] == {}
    assert by_delta[0.98]["status"] == "timeout" and "forced timeout" in by_delta[0.98]["message"]
    assert by_delta[0.97]["status"] == "ok"
    assert any("forced warning" in w for w in by_delta[0.97]["warnings"])
    assert len(list(d.glob("*.npz"))) == 2
    assert R.main(["--config", str(f)]) == 1                   # failed/timeout cells are retried
    statuses = [r["status"] for r in manifest(d)][4:]
    assert sorted(statuses) == ["failed", "skipped", "skipped", "timeout"]


def test_resume_reruns_only_what_is_missing(tmp_path, toy):
    f = write_cfg(tmp_path)
    d = out_dir(tmp_path)
    R.main(["--config", str(f)])
    victim = sorted(d.glob("T_*.json"))[1]
    victim.unlink()
    R.main(["--config", str(f)])
    statuses = [r["status"] for r in manifest(d)][3:]
    assert sorted(statuses) == ["ok", "skipped", "skipped"]
    assert victim.exists()


def test_changed_setting_makes_a_new_result(tmp_path, toy):
    f = write_cfg(tmp_path)
    R.main(["--config", str(f)])
    R.main(["--config", str(f), "--set", "solver.rtol=1e-9"])
    assert len(list(out_dir(tmp_path).glob("*.npz"))) == 6


# --- running: spawn pool ----------------------------------------------------------------------------

def test_pool_workers_set_single_thread_env_and_match_in_process(tmp_path, monkeypatch):
    monkeypatch.setitem(R.TASKS, "mf", "toy_task:run_env")
    for k in R.THREAD_VARS:
        monkeypatch.delenv(k, raising=False)
    sweep = "x_name: model.Delta, x_values: [0.2, 0.3, 0.4, 0.5]"
    results = {}
    for workers in (1, 2):
        f = write_cfg(tmp_path, sweep=sweep, out=f"w{workers}")
        assert R.main(["--config", str(f), "--workers", str(workers)]) == 0
        d = out_dir(tmp_path, f"w{workers}")
        results[workers] = {p.name: dict(np.load(p)) for p in sorted(d.glob("*.npz"))}
    assert not any(k in os.environ for k in R.THREAD_VARS)          # parent env restored
    assert results[1].keys() == results[2].keys() and len(results[2]) == 4
    for name in results[2]:
        assert np.array_equal(results[1][name]["delta"], results[2][name]["delta"])
        assert np.array_equal(results[2][name]["threads"], [1.0, 1.0, 1.0])


def test_pool_survives_a_failing_cell(tmp_path, toy):
    f = write_cfg(tmp_path, sweep="x_name: model.Delta, x_values: [0.2, 0.99, 0.3, 0.98]")
    assert R.main(["--config", str(f), "--workers", "2"]) == 1
    d = out_dir(tmp_path)
    assert sorted(r["status"] for r in records(d).values()) == ["failed", "ok", "ok", "timeout"]
    assert sorted(r["status"] for r in manifest(d)) == ["failed", "ok", "ok", "timeout"]


# --- part 2: real tasks (1b-ii) ---------------------------------------------------------------------------

REAL = ("path: {name: path_eta, eta_start: 1.0, eta_peak: 4.0, T_ramp_s: 1.0, t_on_s: 0.5}\n"
        "durations: {hold_s: 0.5, discard_s: 0.5}\n")


def real_cfg(tmp_path, kind="mf", out="out", extra_run="", sweep=None, extra="", path_line=None):
    sweep = sweep or "x_name: model.Delta, x_values: [0.26, 0.28, 0.30, 0.32, 0.34, 0.36]"
    f = tmp_path / f"T_{out}.yaml"
    f.write_text(f"run: {{id: T, kind: {kind}{extra_run}}}\n"
                 f"output: {{dir: \"{(tmp_path / out).as_posix()}\"}}\n"
                 f"sweep: {{{sweep}}}\n{path_line or REAL}{extra}")
    return f


def load_all(d):
    return {p.name: dict(np.load(p)) for p in sorted(d.glob("*.npz"))}


@pytest.mark.parametrize("kind,extra", [("mf", ""),
                                        ("mf_noisy", "noise: {sigma: 0.05}\nseeds: {n_seeds: 3}\n")])
def test_workers_1_and_6_give_identical_results_with_the_real_tasks(tmp_path, kind, extra):
    sweep = "x_name: model.Delta, x_values: [0.28, 0.32]" if kind == "mf_noisy" else None
    res = {}
    for workers in (1, 6):
        f = real_cfg(tmp_path, kind=kind, out=f"w{workers}", sweep=sweep, extra=extra)
        assert R.main(["--config", str(f), "--workers", str(workers)]) == 0
        res[workers] = load_all(out_dir(tmp_path, f"w{workers}"))
    assert res[1].keys() == res[6].keys() and len(res[1]) == 6
    for name in res[1]:
        for key in res[1][name]:
            assert np.array_equal(res[1][name][key], res[6][name][key]), (name, key)
    recs = records(out_dir(tmp_path, "w6"))
    assert {r["status"] for r in recs.values()} == {"ok"}
    assert all(r["numba_cache_cleared"] is None for r in recs.values())


def test_forced_dop853_failure_is_retried_with_radau_and_flagged_in_the_record(tmp_path, monkeypatch):
    from mprsurge import simulate_mf as S
    real = S.solve_ivp

    def flaky(f, span, y0, *a, method="DOP853", **kw):
        if method == "DOP853":
            class Failed:
                status, message = -1, "forced failure"
            return Failed()
        return real(f, span, y0, *a, method=method, **kw)
    monkeypatch.setattr(S, "solve_ivp", flaky)
    f = real_cfg(tmp_path, sweep="x_name: model.Delta, x_values: [0.3]")
    assert R.main(["--config", str(f)]) == 0
    (rec,) = records(out_dir(tmp_path)).values()
    assert rec["status"] == "ok" and rec["flags"]["retried_with_radau"] is True
    assert rec["flags"]["solver"] == "Radau" and "forced failure" in rec["flags"]["first_failure"]
    assert "Radau" in rec["message"] and list(out_dir(tmp_path).glob("*.npz"))


@pytest.mark.parametrize("kind,extra,T_ramp", [
    ("mf", "", 120.0),                                                        # a long solve_ivp
    ("mf_noisy", "noise: {sigma: 0.05}\nseeds: {n_seeds: 1}\n", 1000.0)])     # a long jitted run
def test_wall_limit_gives_status_timeout_quickly(tmp_path, kind, extra, T_ramp):
    path_line = REAL.replace("T_ramp_s: 1.0", f"T_ramp_s: {T_ramp}")
    f = real_cfg(tmp_path, kind=kind, extra_run=", wall_limit_s: 0.5", extra=extra, path_line=path_line,
                 sweep="x_name: model.Delta, x_values: [0.3]")
    t0 = time.monotonic()
    assert R.main(["--config", str(f)]) == 1
    assert time.monotonic() - t0 < 30
    (rec,) = records(out_dir(tmp_path)).values()
    assert rec["status"] == "timeout" and "wall-time" in rec["message"] and rec["outputs"] == {}
    assert not list(out_dir(tmp_path).glob("*.npz"))


# --- heartbeat (ETA line) ----------------------------------------------------------------------------------------

class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


def _heartbeats(tmp_path, n, every, monkeypatch):
    monkeypatch.setitem(R.TASKS, "mf", "toy_task:run")
    sweep = f"x_name: model.Delta, x_values: [{', '.join(str(0.1 + 0.01 * k) for k in range(n))}]"
    plan = R.build_plan(str(write_cfg(tmp_path, sweep=sweep)))
    jobs = [{"index": c["index"], "name": c["name"], "hash12": c["hash12"], "cfg": c["cfg"],
             "out_dir": str(plan.out_dir), "task": R.TASKS["mf"], "env": P.environment_info(with_julia=False),
             "inputs": plan.inputs, "dry_run": False} for c in plan.cells]
    cap, log = _Capture(), logging.getLogger(R.LOG_NAME)
    old = (log.handlers[:], log.level, log.propagate)
    log.handlers[:], log.propagate = [cap], False
    log.setLevel(logging.INFO)
    try:
        R.run_jobs(jobs, 1, plan.out_dir, heartbeat_every=every)
    finally:
        log.handlers[:], log.level, log.propagate = old
    return [m for m in cap.lines if m.startswith("heartbeat")]


def test_heartbeat_reports_progress_and_eta_every_n_runs(tmp_path, monkeypatch):
    beats = _heartbeats(tmp_path, 7, 3, monkeypatch)
    assert len(beats) == 2                                          # after 3 and 6 of 7; not after the last
    assert re.fullmatch(r"heartbeat 3/7 done, elapsed \d+ s, ETA \d+ s", beats[0])
    assert beats[1].startswith("heartbeat 6/7")


def test_fewer_runs_than_the_interval_log_no_heartbeat_and_do_not_fail(tmp_path, monkeypatch):
    # With the default interval of 10, a sweep of fewer than 10 runs never reaches a heartbeat.
    assert _heartbeats(tmp_path, 4, 10, monkeypatch) == []
    assert _heartbeats(tmp_path, 1, 10, monkeypatch) == []
    assert len(_heartbeats(tmp_path, 4, 2, monkeypatch)) == 1       # 2 of 4; none after the last
