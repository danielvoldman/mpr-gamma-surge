"""S5 baseline-only cell lists and the s5base task (7d, DL-141). Grids are UNVERIFIED working defaults (DL-136 D-4)."""
import copy
import json

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import cells as CL

HEADLINE_ETA_START = 1.396046


@pytest.fixture(scope="module")
def small_spec():
    spec = CL.load_spec()
    spec["map1"]["Delta"]["n"] = 2
    spec["map1"]["tau_d_ms"]["n"] = 2
    spec["map2"]["J0"]["n"] = 2
    spec["map2"]["T_ramp_s"]["n"] = 3
    return spec


@pytest.fixture(scope="module")
def small_cells(small_spec):
    return CL.build_cells(small_spec)


def test_spec_counts_are_900_and_325_cells():
    spec = CL.load_spec()
    n1 = len(CL.axis(spec["map1"]["Delta"])) * len(CL.axis(spec["map1"]["tau_d_ms"]))
    n2 = len(CL.axis(spec["map2"]["J0"])) * len(CL.axis(spec["map2"]["T_ramp_s"]))
    assert (n1, n2, 1 + n1 + n2) == (900, 325, 1226)


def test_axes_spacing_and_ends():
    spec = CL.load_spec()
    D, td = CL.axis(spec["map1"]["Delta"]), CL.axis(spec["map1"]["tau_d_ms"])
    J, T = CL.axis(spec["map2"]["J0"]), CL.axis(spec["map2"]["T_ramp_s"])
    assert (D[0], D[-1]) == (0.01, 0.6) and np.allclose(np.diff(D), np.diff(D)[0])
    assert td[0] == pytest.approx(1.0) and td[-1] == pytest.approx(50.0) and np.allclose(np.diff(np.log(td)), np.diff(np.log(td))[0])
    assert (J[0], J[-1]) == (-40.0, -5.0) and np.allclose(np.diff(J), np.diff(J)[0])
    assert np.allclose(T, 10 ** (np.arange(13) / 4))                         # the S2 list
    assert all(any(abs(T - x) < 1e-9 * x) for x in (56.23413252, 100.0, 177.827941, 316.227766))   # RB3(c) values


def test_headline_cell_start_state(small_cells):
    h = small_cells[0]
    assert h["name"] == "headline" and h["hopf_found"]
    assert h["eta_H"] == pytest.approx(2.8960461989737856, abs=1e-12)
    assert h["eta_H"] == CL.headline_eta_H()
    assert h["eta_start"] == pytest.approx(HEADLINE_ETA_START, abs=1e-6)
    assert h["eta_peak"] == pytest.approx(4.896046, abs=1e-6)
    assert h["start"]["type"] == "stable_focus" and h["start"]["stable"]


def test_counts_and_kinds_small(small_cells):
    s = CL.summary(small_cells)
    assert [s["kinds"][k]["n"] for k in ("headline", "map1", "map2")] == [1, 4, 6]
    assert [c["index"] for c in small_cells] == list(range(11))


def test_no_hopf_cell_inherits_headline_values(small_cells):
    none = [c for c in small_cells if not c["hopf_found"]]
    assert none, "the corner Delta 0.6, tau_d 50 ms has no Hopf crossing"
    for c in none:
        assert c["eta_H"] == CL.headline_eta_H()
        assert c["eta_start"] == pytest.approx(HEADLINE_ETA_START, abs=1e-6)
        assert c["eta_peak"] == pytest.approx(4.896046, abs=1e-6)
        assert "type" in c["start"] and "stable" in c["start"]       # stability is recorded for every cell


def test_hopf_cell_start_is_eta_H_minus_1p5(small_cells):
    for c in small_cells:
        if c["hopf_found"]:
            assert c["eta_start"] == pytest.approx(c["eta_H"] - 1.5)
            assert c["eta_peak"] == pytest.approx(max(4.0, c["eta_H"] + 2.0))


def test_map2_cells_share_start_state_across_T_ramp(small_cells):
    m2 = [c for c in small_cells if c["kind"] == "map2"]
    by_J = {}
    for c in m2:
        by_J.setdefault(c["J0"], []).append(c)
    assert len(by_J) == 2 and all(len(v) == 3 for v in by_J.values())
    for v in by_J.values():
        assert len({(c["eta_start"], c["start"]["r"], c["start"]["v"]) for c in v}) == 1


def test_cell_list_hash_changes_with_the_grid(small_spec, small_cells):
    h0 = CL.cell_list_hash(small_cells)
    assert h0 == CL.cell_list_hash(CL.build_cells(small_spec))                    # stable
    spec2 = copy.deepcopy(small_spec)
    spec2["map1"]["Delta"]["hi"] = 0.5
    assert CL.cell_list_hash(CL.build_cells(spec2)) != h0
    spec3 = copy.deepcopy(small_spec)
    spec3["map2"]["T_ramp_s"]["n"] = 4
    assert CL.cell_list_hash(CL.build_cells(spec3)) != h0


def test_run_hash_changes_with_cell_and_seed_count(small_cells):
    cfgs = [C.resolve_config("configs/S5_baseline.yaml", CL.overrides(c)) for c in small_cells]
    assert len({C.config_hash(c) for c in cfgs}) == len(cfgs)
    assert cfgs[0]["path"]["eta_start"] == pytest.approx(HEADLINE_ETA_START, abs=1e-6)
    a = C.resolve_config("configs/S5_baseline.yaml", {"seeds.n_seeds": 3})
    b = C.resolve_config("configs/S5_baseline.yaml", {"seeds.n_seeds": 4})
    assert C.config_hash(a) != C.config_hash(b)


def _toy_cfg(**extra):
    ov = {"durations.baseline_s": 0.5, "path.t_on_s": 0.5, "durations.discard_s": 0.2, "seeds.n_seeds": 3, **extra}
    return C.resolve_config("configs/S5_baseline.yaml", ov)


def test_toy_run_writes_a_bundle_and_a_record(tmp_path):
    cfg = _toy_cfg()
    env = P.environment_info(with_julia=False)
    job = {"index": 0, "name": "toy", "hash12": C.short_hash(C.config_hash(cfg)), "cfg": cfg, "out_dir": str(tmp_path),
           "task": R.TASKS["s5base"], "env": env, "inputs": {}, "dry_run": False}
    res = R.execute_job(job)
    assert res["status"] == "ok", res["message"]
    z = np.load(tmp_path / "toy.npz")
    assert z["v"].shape == (3, 501) and z["r"].shape == (3, 501) and z["t_ms"].shape == (501,)
    assert z["t_ms"][0] == 0.0 and z["t_ms"][-1] == pytest.approx(500.0)
    assert np.all(np.isfinite(z["v"])) and not np.array_equal(z["v"][0], z["v"][1])    # seeds differ
    rec = json.loads((tmp_path / "toy.json").read_text(encoding="utf-8"))
    assert rec["status"] == "ok" and rec["config_hash"] == C.config_hash(cfg)
    assert rec["flags"]["seed_spawn_keys"] == [[7, 4, 0], [7, 4, 1], [7, 4, 2]]
    assert rec["flags"]["start"]["stable"] and rec["flags"]["start"]["complex_pair"]
    assert rec["flags"]["n_steps_per_seed"] == (200 + 500) * 100 and "git" in rec and "dirty" in rec["git"]


def test_toy_run_is_deterministic_and_seed_streams_do_not_depend_on_the_cell(tmp_path):
    a = R.resolve_task(R.TASKS["s5base"])(_toy_cfg())["arrays"]
    b = R.resolve_task(R.TASKS["s5base"])(_toy_cfg())["arrays"]
    assert np.array_equal(a["v"], b["v"])
    c = R.resolve_task(R.TASKS["s5base"])(_toy_cfg(**{"path.T_ramp_s": 10.0}))["arrays"]    # T_ramp is not used by the baseline
    assert np.array_equal(a["v"], c["v"])


def test_toy_seed_keys_avoid_the_calibration_keys():
    cfg = _toy_cfg()
    assert cfg["seeds"]["spawn_key"] == [7, 4]          # the calibration runs used [0] to [9]
    assert P.seed_from_key(cfg["seeds"]["root_seed"], [7, 4, 0]).generate_state(1)[0] != \
        P.seed_from_key(cfg["seeds"]["root_seed"], [0]).generate_state(1)[0]


def test_baseline_is_stationary_around_the_fixed_point():
    out = R.resolve_task(R.TASKS["s5base"])(_toy_cfg(**{"seeds.n_seeds": 2}))
    v = out["arrays"]["v"]
    v0 = out["arrays"]["y_start"][1]
    assert abs(v.mean() - v0) < 0.2 * abs(v0) + 0.1 and 0 < v.std() < 1.0


@pytest.mark.slow
def test_full_cell_list_is_900_plus_325_plus_headline():
    cells = CL.build_cells()
    s = CL.summary(cells)
    assert s["n_cells"] == 1226 and [s["kinds"][k]["n"] for k in ("headline", "map1", "map2")] == [1, 900, 325]
    assert cells[0]["eta_start"] == pytest.approx(HEADLINE_ETA_START, abs=1e-6)
    inherit = [c for c in cells if not c["hopf_found"]]
    assert inherit and all(c["eta_start"] == pytest.approx(HEADLINE_ETA_START, abs=1e-6) for c in inherit)
    assert len({c["name"] for c in cells}) == 1226
