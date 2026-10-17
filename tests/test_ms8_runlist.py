"""MS8 8b: the S5 ramp and S13 headline run lists, the seed-key prefix, the hash-preserving start distance, the gate and the dry run
(DL-169). Nothing integrates: the runner is only ever called with --dry-run, or build_plan."""
import json
from pathlib import Path

import numpy as np
import pytest
import yaml

from mprsurge import config as C
from mprsurge import criteria as K
from mprsurge import run as R
from mprsurge.analysis import ms8_counts as M
from mprsurge.analysis import ms8_runlist as L
from mprsurge.analysis import timing as T

from test_criteria_draft import _key_prefixes_in_repo
from test_criteria_loader import make_repo

# Pinned list hashes (DL-169): a changed config, sweep value, seed prefix or order changes them. Update only with a decision-log entry.
LIST_SHA256 = {"S5": "b446024899351b60dce1afb8dbe06cb433f74123097575def3b7fa7ad7f84a8a",
               "S13": "9117cc0edb8f886ac09b5a86275c94dd84660c209a6d2a9910672430a5cc9cc9"}
ALL_CONFIGS = [c for name in L.LISTS for c, _ in L.LISTS[name]]
FIXTURE = Path(__file__).parent / "fixtures" / "config_hash_baseline_pre_ms8b.json"


@pytest.fixture(scope="module")
def rows():
    return {name: L.expand(name) for name in L.LISTS}


# --- counts and hashes -------------------------------------------------------------------------

def test_counts_and_breakdown(rows):
    assert L.breakdown(rows["S5"]) == {"S5_grid": 78, "S5_start_distance": 26, "S5_headline": 1, "S5_noise": 130}
    assert len(rows["S5"]) == 235 and sum(r["kind"] == "mf" for r in rows["S5"]) == 105 and sum(r["kind"] == "mf_noisy" for r in rows["S5"]) == 130
    assert L.breakdown(rows["S13"]) == {"S13_rtol": 2, "S13_delta0": 2, "S13_radau": 1, "S13_floor": 120}
    assert len(rows["S13"]) == 125 and sum(r["kind"] == "mf_noisy" for r in rows["S13"]) == 120


def test_list_hashes_are_pinned_and_stable(rows):
    assert {n: L.list_sha256(r) for n, r in rows.items()} == LIST_SHA256
    assert L.list_sha256(L.expand("S5")) == L.list_sha256(rows["S5"])                 # deterministic
    assert L.list_sha256(rows["S5"][:-1]) != LIST_SHA256["S5"]


def test_no_run_appears_twice_and_the_headline_is_the_shared_run(rows):
    both = rows["S5"] + rows["S13"]
    assert L.duplicates(both) == [] and len({r["hash"] for r in both}) == len(both) == 360
    head = [r for r in rows["S5"] if r["family"] == "S5_headline"][0]["cfg"]
    # the S13 ladders' middle members are the headline run: DOP853, rtol 1e-10, delta0 1e-6, and it is in the S5 list only
    assert (head["solver"]["method"], head["solver"]["rtol"], head["solver"]["delta0"], head["path"]["T_ramp_s"]) == ("DOP853", 1e-10, 1e-6, 120.0)
    for r in rows["S13"]:
        if r["family"] == "S13_rtol":
            assert r["rtol"] in (1e-8, 1e-12) and r["delta0"] == 1e-6
        if r["family"] == "S13_delta0":
            assert r["delta0"] in (1e-9, 1e-3) and r["rtol"] == 1e-10


def test_counts_agree_with_the_8a_counts_module(rows):
    s = M.summarise(M.s5_mode_d_runs() + M.s5_mode_n_runs() + M.s13_headline_runs())
    by = L.breakdown(rows["S5"]) | L.breakdown(rows["S13"])
    assert {k: v["runs"] for k, v in s.items()} == by
    for fam, cfg_filter in (("S5_grid", None), ("S5_start_distance", None), ("S5_headline", None)):
        tau = sum(T.tau_simulated(r["cfg"]) for r in rows["S5"] if r["family"] == fam)
        assert tau == pytest.approx(s[fam]["tau"], rel=1e-9), fam
    steps = sum(T.tau_simulated(r["cfg"]) / r["cfg"]["noise"]["dt_tau"] for r in rows["S5"] if r["family"] == "S5_noise")
    assert steps == pytest.approx(s["S5_noise"]["heun_steps"], rel=1e-9) and steps == pytest.approx(3.0755e9, rel=1e-4)
    steps13 = sum(T.tau_simulated(r["cfg"]) / r["cfg"]["noise"]["dt_tau"] for r in rows["S13"] if r["family"] == "S13_floor")
    assert steps13 == pytest.approx(s["S13_floor"]["heun_steps"], rel=1e-9)


def test_t_ramp_values_are_the_s5_grid(rows):
    grid = M.t_ramp_grid()
    for cfg_path in [c for c in ALL_CONFIGS if "/s5_p" in c and "noise" not in c]:
        plan = R.build_plan(cfg_path)
        sd = plan.cfg["sweep"]["x_values"]
        Ts = sorted({c["cfg"]["path"]["T_ramp_s"] for c in plan.cells})
        assert np.allclose(Ts, grid, rtol=1e-12, atol=0), cfg_path
        assert len(plan.cells) == 13 * (2 if sd else 1)
    assert R.build_plan("configs/ms8/s5_p1_start_distance.yaml").cfg["sweep"]["x_values"] == [0.5, 3.0]
    assert {r["T_ramp_s"] for r in rows["S13"]} == {120.0} and {r["T_ramp_s"] for r in rows["S5"] if r["family"] == "S5_headline"} == {120.0}


def test_s13_values_equal_the_frozen_s13_yaml(rows):
    s13 = yaml.safe_load((C.repo_root() / "configs/S13.yaml").read_text(encoding="utf8"))
    plan = s13["stated_by_plan"], s13["ruled_by_owner_7g"]
    assert sorted(r["rtol"] for r in rows["S13"] if r["family"] == "S13_rtol") == sorted(set(plan[0]["rtol_ladder"]) - {1e-10})
    assert sorted(r["delta0"] for r in rows["S13"] if r["family"] == "S13_delta0") == sorted(set(plan[0]["delta0_ladder"]) - {1e-6})
    fl = [r for r in rows["S13"] if r["family"] == "S13_floor"]
    assert sorted({r["dt_tau"] for r in fl}) == sorted(plan[1]["heun_dt_ladder_tau"])
    assert sorted({r["sigma"] for r in fl}) == sorted(plan[1]["d43_floor_levels_sigma_floor"])
    assert {r["delta0"] for r in fl} == {1e-6}                                               # M-4 (i): the default delta0 at every level
    assert [r["solver"] for r in rows["S13"] if r["family"] == "S13_radau"] == ["Radau"] and [r["rtol"] for r in rows["S13"] if r["family"] == "S13_radau"] == [1e-10]
    # every rung is a whole multiple of the coupling step (F-14): 20, 10, 5, 2
    base = {r["coupling_dt_tau"] for r in fl}
    assert base == {5.0e-5} and [round(dt / 5.0e-5, 9) for dt in sorted(plan[1]["heun_dt_ladder_tau"], reverse=True)] == [20, 10, 5, 2]
    assert plan[1]["heun_ladder_coupled_brownian_increments"] is True
    assert all(r["rtol"] is not None for r in fl)


# --- hash view (M-7) ---------------------------------------------------------------------------

def test_null_start_distance_and_coupling_stay_out_of_the_hash_view():
    base = C.resolve_config("configs/S5.yaml")
    assert "start_distance" not in base["path"]
    h0 = C.config_hash(base)
    nul = C.resolve_config("configs/S5.yaml", {"path.start_distance": None, "noise.coupling_dt_tau": None})
    assert C.config_hash(nul) == h0
    assert "start_distance" not in C.hash_view(nul)["path"] and "coupling_dt_tau" not in C.hash_view(nul)["noise"]
    assert C.config_hash(C.resolve_config("configs/S5.yaml", {"path.start_distance": 3.0})) != h0
    assert C.config_hash(C.resolve_config("configs/S5.yaml", {"noise.coupling_dt_tau": 5e-5})) != h0


def test_every_stored_config_and_sweep_cell_keeps_its_hash():
    """Hashes of every configs/**/*.yaml and every sweep cell, taken at f991a9a before the 8b code (tests/fixtures)."""
    old = json.loads(FIXTURE.read_text(encoding="utf8"))
    checked = 0
    for rel, hashes in old.items():
        if isinstance(hashes, str):               # configs that are not run files (criteria, grids, cell lists) had no hash then either
            continue
        try:
            plan = R.build_plan(rel)
            now = [C.config_hash(c["cfg"]) for c in plan.cells]
        except C.ConfigError:
            now = [C.config_hash(C.resolve_config(C.repo_root() / rel))]
        assert now == hashes, rel
        checked += len(hashes)
    assert checked >= 140 and len(old) >= 60


# --- start distance (M-7, D12) -------------------------------------------------------------------

def test_start_distance_sets_eta_start_only():
    default = C.resolve_config("configs/ms8/s5_p1_linear.yaml")
    eta_H = default["path"]["eta_H"]
    assert default["path"]["eta_start"] == pytest.approx(eta_H - 1.5)
    for d in (0.5, 1.5, 3.0):
        c = C.resolve_config("configs/ms8/s5_p1_linear.yaml", {"path.start_distance": d})
        assert c["path"]["eta_start"] == pytest.approx(eta_H - d) and c["path"]["eta_peak"] == default["path"]["eta_peak"]
        assert c["path"]["eta_path_status"] == "A4"
        assert c["path"]["eps"] == pytest.approx((c["path"]["eta_peak"] - c["path"]["eta_start"]) / (c["path"]["T_ramp_s"] * 100.0))
    assert C.resolve_config("configs/ms8/s5_p1_linear.yaml", {"path.start_distance": 1.5})["path"]["eta_start"] == default["path"]["eta_start"]


def test_start_distance_needs_eta_H_and_no_explicit_start():
    with pytest.raises(C.ConfigError, match="start_distance"):
        C.resolve_config("configs/base.yaml", {"path.start_distance": 1.0})
    with pytest.raises(C.ConfigError):
        C.resolve_config("configs/ms8/s5_p1_linear.yaml", {"path.start_distance": 1.0, "path.eta_start": 1.0, "path.eta_peak": 4.0})
    with pytest.raises(C.ConfigError, match="> 0"):
        C.resolve_config("configs/ms8/s5_p1_linear.yaml", {"path.start_distance": -1.0})


def test_start_distance_cells_cover_the_two_new_distances_at_all_13_t_ramp(rows):
    sd = [r for r in rows["S5"] if r["family"] == "S5_start_distance"]
    assert sorted({r["start_distance"] for r in sd}) == [0.5, 3.0] and len(sd) == 26
    assert {(r["path"], r["profile"]) for r in sd} == {("path_eta", "linear")}
    eta_H = sd[0]["cfg"]["path"]["eta_H"]
    assert all(r["eta_start"] == pytest.approx(eta_H - r["start_distance"]) for r in sd)
    grid = [r for r in rows["S5"] if r["config"].endswith("s5_p1_linear.yaml")]
    assert len(grid) == 13 and all(r["start_distance"] is None for r in grid)               # the 1.5 run, reused


# --- the gate ----------------------------------------------------------------------------------

def test_every_new_config_names_the_frozen_file():
    for c in ALL_CONFIGS:
        assert K.is_frozen_criteria_path(C.resolve_config(c)["robustness"]["criteria_file"]), c


def test_runner_refuses_every_ms8_config_when_the_freeze_does_not_verify(monkeypatch):
    def refuse(*a, **k):
        raise K.CriteriaError("mismatch (test)")
    monkeypatch.setattr(K, "verify_frozen_criteria", refuse)
    for c in ALL_CONFIGS:
        with pytest.raises(K.CriteriaError):
            R.build_plan(c)
    assert R.main(["--config", "configs/ms8/s13_floor_l0.yaml", "--dry-run"]) == 2
    with pytest.raises(K.CriteriaError):
        L.write_manifest("unused")
    R.build_plan("configs/S5.yaml")             # a config that does not name the frozen file is not gated


def test_gate_refuses_an_edited_frozen_file_in_a_temp_repo(tmp_path):
    root = make_repo(tmp_path)
    cfg = C.resolve_config("configs/ms8/s13_floor_l0.yaml")
    assert K.require_frozen_for_config(cfg, root)["sha256"] == K.lf_sha256((root / K.CRITERIA_PATH).read_bytes())
    with open(root / K.CRITERIA_PATH, "a", encoding="utf8", newline="\n") as fh:
        fh.write("# edited after the freeze\n")
    with pytest.raises(K.CriteriaError, match="mismatch"):
        K.require_frozen_for_config(cfg, root)


# --- seed keys (M-8, M-9) ------------------------------------------------------------------------

def test_seed_keys_follow_m9_and_no_cell_uses_a_bare_seed_index(rows):
    noise = [r for r in rows["S5"] if r["family"] == "S5_noise"]
    assert sorted({tuple(r["spawn_key"]) for r in noise}) == [(8, 1, s) for s in range(10)] and len(noise) == 130
    for T_ in {r["T_ramp_s"] for r in noise}:                      # the same stream in every T_ramp cell
        assert sorted(tuple(r["spawn_key"]) for r in noise if r["T_ramp_s"] == T_) == [(8, 1, s) for s in range(10)]
    fl = [r for r in rows["S13"] if r["family"] == "S13_floor"]
    assert sorted({tuple(r["spawn_key"]) for r in fl}) == [(8, 2, l, s) for l in range(3) for s in range(10)]
    for l in range(3):
        for s in range(10):                                         # the four rungs of one (l, s) share the key and differ in dt only
            same = [r for r in fl if tuple(r["spawn_key"]) == (8, 2, l, s)]
            assert sorted(r["dt_tau"] for r in same) == [1e-4, 2.5e-4, 5e-4, 1e-3] and len({r["sigma"] for r in same}) == 1
    for r in rows["S5"] + rows["S13"]:
        assert r["spawn_key"] is None or (len(r["spawn_key"]) >= 3 and r["spawn_key"][0] == 8)
        assert (r["spawn_key"] is None) == (r["kind"] == "mf")


def test_ms8_keys_collide_with_no_key_used_in_the_repo(rows):
    mine = set(L.seed_keys(rows["S5"]) + L.seed_keys(rows["S13"]))
    assert mine == set(M.proposed_seed_keys()) and len(mine) == 10 + 30
    used = {u for u in _key_prefixes_in_repo() if u[0] != 8}
    assert (7, 4) in used and (7, 6, 1) in used and (7, 8, 5, 1) in used
    calibration = {(s,) for s in range(10)}
    ms8_prefixes = {u for u in _key_prefixes_in_repo() if u[0] == 8}
    assert ms8_prefixes == {(8, 1), (8, 2, 0), (8, 2, 1), (8, 2, 2)}            # the configs hold exactly the prefixes, nothing else
    for m in mine:
        assert m not in calibration
        assert m[:2] != (7, 9) and m[:2] != (7, 4) and m[:3] != (7, 4, 0)       # F-19 [7, 9]; the S5 baseline [7, 4, s]
        for u in used:
            if len(u) == 1:
                continue
            n = min(len(m), len(u))
            assert m[:n] != u[:n], (m, u)
    # the S5 baseline keys [7, 4, s] and the Latin hypercube prefix [7, 9] are still what they were
    for s in range(10):
        for u in ((7, 4, s), (7, 9)):
            assert not set(mine) & {u}


def _noisy_file(tmp_path, spawn_prefix, criteria, spawn_key=None):
    d = {"run": {"id": "t", "kind": "mf_noisy"}, "model": {"ref_point": "ref_devalle"}, "path": {"name": "path_hypoxia", "eta_H": 2.8960461989737856},
         "seeds": {"n_seeds": 3}}
    if spawn_prefix is not None:
        d["seeds"]["spawn_prefix"] = spawn_prefix
    if spawn_key is not None:
        d["seeds"]["spawn_key"] = spawn_key
    if criteria:
        d["robustness"] = {"criteria_file": K.CRITERIA_PATH}
    p = tmp_path / "t.yaml"
    p.write_text(yaml.safe_dump(d), encoding="utf8")
    return str(p)


def test_runner_prefix_and_the_bare_key_rule(tmp_path):
    plain = R.build_plan(_noisy_file(tmp_path, None, criteria=False))
    assert [c["cfg"]["seeds"]["spawn_key"] for c in plain.cells] == [[0], [1], [2]]          # calibration keys kept for old configs
    pref = R.build_plan(_noisy_file(tmp_path, [8, 5], criteria=False))
    assert [c["cfg"]["seeds"]["spawn_key"] for c in pref.cells] == [[8, 5, 0], [8, 5, 1], [8, 5, 2]]
    assert len({c["hash12"] for c in pref.cells}) == 3 and {c["hash12"] for c in pref.cells}.isdisjoint(c["hash12"] for c in plain.cells)
    timing_like = R.build_plan(_noisy_file(tmp_path, None, criteria=False, spawn_key=[0]))          # a timing cell's spawn_key [0] is still overwritten by [s]
    assert [c["cfg"]["seeds"]["spawn_key"] for c in timing_like.cells] == [[0], [1], [2]]
    with pytest.raises(C.ConfigError, match="spawn_prefix"):
        R.build_plan(_noisy_file(tmp_path, None, criteria=True))                       # a ramp-study config cannot use the bare key
    R.build_plan(_noisy_file(tmp_path, [8, 5], criteria=True))


# --- job order (M-12) ----------------------------------------------------------------------------

def test_longest_first_order_changes_the_submission_order_only():
    plan = R.build_plan("configs/ms8/s5_p5_sigmoid.yaml")
    jobs = [{"index": c["index"], "name": c["name"], "cfg": c["cfg"]} for c in plan.cells]
    ordered = R.longest_first(jobs)
    cost = [R.estimated_cost_s(j["cfg"]) for j in ordered]
    assert cost == sorted(cost, reverse=True) and ordered[0]["cfg"]["path"]["T_ramp_s"] == pytest.approx(1000.0)
    assert sorted(j["index"] for j in ordered) == [j["index"] for j in jobs] and {j["name"] for j in ordered} == {j["name"] for j in jobs}
    # plan order inside equal costs, and across families the 1000 s P5 runs lead the S5 list
    allj = [{"index": c["index"], "name": c["name"], "cfg": c["cfg"]} for cfg_path, _ in L.S5_CONFIGS for c in R.build_plan(cfg_path).cells]
    first = R.longest_first(allj)[:2]
    assert all(j["cfg"]["path"]["name"] == "path_updown" and j["cfg"]["path"]["T_ramp_s"] == pytest.approx(1000.0) for j in first)
    assert R.estimated_cost_s(R.build_plan("configs/ms8/s13_radau.yaml").cells[0]["cfg"]) > R.estimated_cost_s(R.build_plan("configs/S5_ramp.yaml").cells[0]["cfg"])


# --- dry run -------------------------------------------------------------------------------------

def test_dry_run_expands_both_lists_writes_records_and_the_manifest_and_integrates_nothing(tmp_path, monkeypatch):
    def no_run(*a, **k):
        raise AssertionError("a simulation was called in a dry run")
    monkeypatch.setattr(R, "resolve_task", no_run)
    n = 0
    for c in ALL_CONFIGS:
        out = tmp_path / Path(c).stem
        assert R.main(["--config", c, "--dry-run", "--set", f"output.dir={out.as_posix()}", "--longest-first"]) == 0
        recs = list(out.rglob("*.dry.json"))
        assert recs and not list(out.rglob("*.npz"))
        n += len(recs)
        rec = json.loads(recs[0].read_text(encoding="utf8"))
        assert rec["status"] == "dry_run" and rec["criteria_sha256"] == "c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05"
    assert n == 360
    s = L.write_manifest(tmp_path / "manifest")
    assert {k: v["sha256"] for k, v in s["lists"].items()} == LIST_SHA256 and s["lists"]["S5"]["runs"] == 235 and s["lists"]["S13"]["runs"] == 125
    assert s["gate"]["sha256"] == "c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05"
    for name, runs in (("S5", 235), ("S13", 125)):
        lines = (tmp_path / "manifest" / f"runlist_{name}.csv").read_text(encoding="utf8").strip().splitlines()
        assert len(lines) == runs + 1 and lines[0].startswith("list,family,config")
    assert (tmp_path / "manifest" / "ms8_runlists.json").exists()


# --- launch arithmetic (9.2) sees the coupled draws -------------------------------------------------

def test_launch_arithmetic_counts_the_coupled_draws_of_the_floor_runs(rows):
    assert M.COUPLING_DT_TAU == {r["coupling_dt_tau"] for r in rows["S13"] if r["family"] == "S13_floor"}.pop()
    floor = [r for r in M.s13_headline_runs() if r["family"] == "S13_floor"]
    assert len(floor) == 120 and all(M.coupled_draws(r) == pytest.approx(r["tau"] / 5.0e-5) for r in floor)
    assert floor[0]["tau"] / 5.0e-5 == pytest.approx(3.34e8, rel=1e-3)                  # the same count of normals at every rung
    assert M.coupled_draws(M.s5_mode_n_runs()[0]) == 0.0                                 # the S5 noise runs are not coupled
    assert [M.coupled_draw_s(r) > 0 for r in floor[:1]] == [True]
