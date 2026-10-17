"""scripts/run_ms8_list.py (MS8 8c, DL-173): one pool over the whole list; same cells and hashes as the per-config runner."""
import importlib.util
from pathlib import Path

from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import ms8_runlist as RL

ROOT = Path(__file__).resolve().parents[1]


def _launcher():
    spec = importlib.util.spec_from_file_location("run_ms8_list", ROOT / "scripts" / "run_ms8_list.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _all_jobs():
    env = P.environment_info()
    jobs = []
    for config, _ in RL.LISTS["S5"]:
        sets = ["output.dir=results/S5/ramp"] if config == "configs/S5_ramp.yaml" else []
        jobs += R.jobs_for(R.build_plan(config, sets, 10), env, True)
    return jobs


def test_pooled_jobs_are_the_235_cells_of_the_list_with_unchanged_hashes():
    jobs = _all_jobs()
    rows = RL.expand("S5")
    assert len(jobs) == len(rows) == 235
    assert sorted(j["hash12"] for j in jobs) == sorted(r["hash"][:12] for r in rows)


def test_headline_output_override_leaves_the_config_hash_unchanged():
    a = R.build_plan("configs/S5_ramp.yaml").cells[0]
    b = R.build_plan("configs/S5_ramp.yaml", ["output.dir=results/S5/ramp"]).cells[0]
    assert a["hash12"] == b["hash12"] and a["name"] == b["name"]


def test_longest_first_starts_with_the_p5_1000_s_runs_and_keeps_all_jobs():
    jobs = R.longest_first(_all_jobs())
    assert len(jobs) == 235
    assert jobs[0]["cfg"]["path"]["name"] == "path_updown" and jobs[0]["cfg"]["path"]["T_ramp_s"] == 1000.0
    costs = [R.estimated_cost_s(j["cfg"]) for j in jobs]
    assert costs == sorted(costs, reverse=True)


def test_launcher_module_imports():
    assert callable(_launcher().main)
