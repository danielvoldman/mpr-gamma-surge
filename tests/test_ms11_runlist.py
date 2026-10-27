"""MS11 11b run lists (DL-344): counts, frozen hashes, seed keys, configuration identities and the launcher refusals. Nothing is launched or simulated."""
import copy
import importlib.util
import shutil
from pathlib import Path

import pytest

from mprsurge import config as C
from mprsurge import criteria as CR
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import ms10_runlist as RL10
from mprsurge.analysis import ms11_counts as MC
from mprsurge.analysis import ms11_eval_choices as EC
from mprsurge.analysis import ms11_runlist as RL

from test_criteria_draft import _key_prefixes_in_repo
from test_ms9_seed_keys import _related
from test_ms11_counts import EXISTING

ROOT = Path(__file__).resolve().parents[1]
GRID_T = (10.0, 316.22776601683796)


@pytest.fixture(scope="module")
def rows():
    return {n: RL.expand(n) for n in RL.ALL_LISTS}


def _ov(x):
    return {k: v for k, v in x["overrides"].items() if k not in ("run.id", "output.dir")}


def test_each_list_has_its_count_and_the_nominal_count_agrees(rows):
    assert {n: len(r) for n, r in rows.items()} == {"MS11_S11": 120, "MS11_CTRL": 30, "MS11_S13_MF": 68, "MS11_S13_NET": 18, "MS11_RB9D": 2}
    assert RL.nominal_counts() == RL.EXPECTED_COUNTS == {n: len(r) for n, r in rows.items()}
    assert sum(RL.EXPECTED_COUNTS.values()) == MC.RULED_TOTAL == 238 and sum(RL.EXPECTED_COUNTS[n] for n in RL.PREREG_LISTS) == 236
    assert {k: v["runs"] for k, v in MC.counts().items()} == {"S11": 120, "S11_control": 30, "S13_mf": 68, "S13_net": 18}


def test_the_counts_derive_from_the_definition_files():
    a, b, c, d = (RL.params(n) for n in RL.PREREG_LISTS)
    assert len(a["sigma_factors"]) * len(a["T_ramp_s"]) * a["n_seeds"] == 3 * 4 * 10
    assert len(b["sigma_factors"]) * b["n_seeds"] == 3 * 10 and b["T_ramp_s"] == 120.0
    assert len(c["T_ramp_s"]) * (2 + 2) + len(c["T_ramp_s"]) * 3 * c["floor"]["seeds"] == 8 + 60 and c["radau"]["runs"] == 0
    assert len(d["configurations"]) * d["n_seeds"] == 6 * 3 and [x["k"] for x in d["configurations"]] == list(range(6))


def test_frozen_hashes_equal_the_expanded_lists_and_the_definition_files(rows):
    froz = RL.frozen_hashes()
    for n, r in rows.items():
        assert froz[n]["sha256"] == RL.list_sha256(r), n
        assert froz[n]["keys_sha256"] == RL.keys_sha256(r), n
        assert froz[n]["runs"] == len(r)
        assert froz[n]["definition_sha256"] == RL.definition_sha256(n)
        assert not RL.duplicates(r), n
        assert len({x["name"] for x in r}) == len(r)
    assert not RL.is_draft()


def test_no_run_is_repeated_across_the_lists_and_the_s5_grid_runs_are_not_repeated(rows):
    allh = [x["hash"] for r in rows.values() for x in r]
    assert len(set(allh)) == len(allh) == 238
    for T_ in GRID_T:
        base = C.config_hash(C.resolve_config(ROOT / "configs/S5_ramp.yaml", {"path.T_ramp_s": T_}))
        assert base not in allh


def test_seed_keys_are_the_confirmed_ones_and_collide_with_no_existing_key(rows):
    keys = {tuple(k) for r in rows.values() for k in RL.seed_keys(r)}
    assert keys <= set(MC.proposed_seed_keys())
    used = {k for k in _key_prefixes_in_repo() if k[0] != 11} | set(EXISTING)
    for k in keys:
        assert all(not _related(k, u) for u in used), k
    assert len(keys) == 10 + 10 + 60 + 3                      # [11,1,s], [11,2,s], [11,3,t,l,s], [11,4,s]; [11,5,k,s] (network controls) are not used
    assert not any(k[:2] == (11, 5) for k in keys)
    # the S11 seed index is the same stream at every sigma and T_ramp (M11-1 (d)); the six network configurations of one s share the key
    s11 = [tuple(x["spawn_key"]) for x in rows["MS11_S11"]]
    assert sorted(set(s11)) == [(11, 1, s) for s in range(10)] and all(s11.count(k) == 12 for k in set(s11))
    net = [tuple(x["spawn_key"]) for x in rows["MS11_S13_NET"]]
    assert sorted(set(net)) == [(11, 4, s) for s in range(3)] and all(net.count(k) == 6 for k in set(net))


def test_s11_design(rows):
    r = rows["MS11_S11"]
    assert {x["cfg"]["run"]["kind"] for x in r} == {"mf_noisy"} and {x["cfg"]["path"]["name"] for x in r} == {"path_hypoxia"}
    assert sorted({x["cfg"]["noise"]["sigma_factor"] for x in r}) == [0.5, 1.0, 2.0] and sorted({x["T_ramp_s"] for x in r}) == [10.0, 30.0, 120.0, 300.0]
    assert {x["cfg"]["noise"]["sigma"] for x in r} == {0.0624} and {x["cfg"]["noise"]["dt_tau"] for x in r} == {1.0e-3}
    assert {x["cfg"]["path"]["profile"] for x in r} == {"linear"}


def test_controls_hold_the_start_state_at_the_headline(rows):
    r = rows["MS11_CTRL"]
    assert sorted({x["cfg"]["noise"]["sigma_factor"] for x in r}) == [0.5, 1.0, 2.0] and {x["T_ramp_s"] for x in r} == {120.0}
    for x in r:
        p = x["cfg"]["path"]
        assert p["eta_start"] == p["eta_peak"] == 1.3960461989737856 and p["J_end"] == p["J0"] == -21.0
    assert {x["family"] for x in r} == {"S11_ctrl"} and all(x["out_dir"].endswith("results/S11/S11_ctrl") for x in r)


def test_s13_mean_field_has_no_radau_and_every_run_differs_from_its_s5_grid_baseline_in_one_parameter_only(rows):
    r = rows["MS11_S13_MF"]
    assert all(x["cfg"]["solver"]["method"] != "Radau" for x in r)                  # DL-337: cut order step 1
    for T_ in GRID_T:
        base = C.config_hash(C.resolve_config(ROOT / "configs/S5_ramp.yaml", {"path.T_ramp_s": T_}))
        for fam, key, vals, back in (("S13_rtol", "solver.rtol", (1e-8, 1e-12), 1e-10), ("S13_delta0", "solver.delta0", (1e-9, 1e-3), 1e-6)):
            mine = [x for x in r if x["family"] == fam and x["T_ramp_s"] == T_]
            assert sorted(x["overrides"][key] for x in mine) == sorted(vals)
            for x in mine:
                assert C.config_hash(C.resolve_config(ROOT / x["config"], {**_ov(x), key: back})) == base
        fl = [x for x in r if x["family"] == "S13_floor" and x["T_ramp_s"] == T_]
        assert len(fl) == 30 and {x["cfg"]["noise"]["dt_tau"] for x in fl} == {1.0e-3} and {x["cfg"]["noise"]["coupling_dt_tau"] for x in fl} == {5.0e-5}
        assert sorted({x["cfg"]["noise"]["sigma"] for x in fl}) == [1.59e-9, 1.59e-6, 1.59e-3]
    assert sorted({tuple(x["spawn_key"])[2] for x in r if x["family"] == "S13_floor"}) == [0, 1]


def test_the_floor_runs_have_the_ms8_floor_configuration_apart_from_t_ramp_and_key(rows):
    x = next(y for y in rows["MS11_S13_MF"] if y["family"] == "S13_floor" and y["T_ramp_s"] == 10.0 and y["spawn_key"] == [11, 3, 0, 1, 4])
    mine = C.resolve_config(ROOT / x["config"], {**_ov(x), "path.T_ramp_s": 120.0, "seeds.spawn_key": [8, 2, 1, 4]})
    ms8 = C.resolve_config(ROOT / "configs/ms8/s13_floor_l1.yaml", {"path.T_ramp_s": 120.0, "seeds.spawn_key": [8, 2, 1, 4], "noise.dt_tau": 1.0e-3})
    assert C.config_hash(mine) == C.config_hash(ms8)


def test_the_network_runs_are_the_ms10_headline_10s_configuration_apart_from_dt_vp_and_key(rows):
    r = rows["MS11_S13_NET"]
    assert {(x["cfg"]["network"]["V_peak"], x["cfg"]["network"]["dt_tau"]) for x in r} == {(100.0, 1e-3), (100.0, 5e-4), (100.0, 2.5e-4), (100.0, 1e-4), (200.0, 1e-3), (200.0, 1e-4)}
    assert all(x["cfg"]["network"]["V_reset"] == -x["cfg"]["network"]["V_peak"] and x["cfg"]["network"]["N"] == 10000 and x["T_ramp_s"] == 10.0 for x in r)
    mine = next(x for x in r if x["cfg"]["network"]["dt_tau"] == 1e-3 and x["cfg"]["network"]["V_peak"] == 100.0 and x["spawn_key"] == [11, 4, 0])
    ms10 = C.resolve_config(ROOT / "configs/ms10/ms10_net.yaml", {**RL10._headline_ov(10.0), "seeds.spawn_key": [10, 1, 0]})
    other = copy.deepcopy(mine["cfg"])
    other["seeds"]["spawn_key"] = [10, 1, 0]
    assert C.config_hash(other) == C.config_hash(ms10)


def test_the_disk_estimate_is_positive_and_small_against_the_free_space(rows):
    est = {n: RL.disk_estimate_bytes(r) for n, r in rows.items()}
    assert all(v > 0 for v in est.values()) and sum(est.values()) < 20e9


# --- launcher refusals ------------------------------------------------------------------------------------------------------------------------------

class Launched(Exception):
    pass


def _launcher(monkeypatch, reasons):
    spec = importlib.util.spec_from_file_location("run_ms11_list", ROOT / "scripts" / "run_ms11_list.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    def tripwire(*a, **k):
        raise Launched("the launcher reached job building")
    monkeypatch.setattr(mod, "build_jobs", tripwire)
    monkeypatch.setattr(R, "run_jobs", tripwire)
    monkeypatch.setattr(RL, "check_launch", lambda names, disk_path=None: list(reasons))
    return mod


ARGS = ["--list", "MS11_CTRL", "--workers", "1", "--journal-dir", "results/ms11/launch_test_never_written"]


def test_the_launcher_refuses_when_check_launch_gives_a_reason_and_reaches_job_building_otherwise(monkeypatch, capsys):
    mod = _launcher(monkeypatch, ["git tree is dirty"])
    assert mod.main(ARGS) == 3 and "dirty" in capsys.readouterr().err
    assert not (ROOT / "results/ms11/launch_test_never_written").exists()
    mod = _launcher(monkeypatch, [])
    assert mod.main(["--list", "MS11_CTRL"]) == 2
    with pytest.raises(Launched):
        mod.main(ARGS)


def test_the_dry_run_is_list_only_prints_the_frozen_hash_and_the_refusals(monkeypatch, capsys):
    mod = _launcher(monkeypatch, ["something open"])
    assert mod.main(["--list", "MS11_CTRL", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert RL.frozen_hashes()["MS11_CTRL"]["sha256"] in out and "= frozen" in out and "REFUSED" in out and "something open" in out


def _clean_env(monkeypatch, dirty=False):
    monkeypatch.setattr(P, "environment_info", lambda with_julia=True: {"git": {"dirty": dirty, "commit": "x"}})
    monkeypatch.setattr(EC, "open_fields", lambda ch=None: [])


def test_check_launch_refuses_each_condition(monkeypatch):
    names = ("MS11_CTRL",)
    _clean_env(monkeypatch)
    assert RL.check_launch(names) == []                                     # all conditions met (the tag verifies, tree 'clean', no open field, hashes equal)
    _clean_env(monkeypatch, dirty=True)
    assert any("dirty" in w for w in RL.check_launch(names))
    _clean_env(monkeypatch)
    monkeypatch.setattr(EC, "open_fields", lambda ch=None: ["a", "b"])
    assert any("required evaluation fields still open (2)" in w for w in RL.check_launch(names))
    _clean_env(monkeypatch)
    froz = copy.deepcopy(RL.frozen_hashes())
    froz["MS11_CTRL"]["sha256"] = "0" * 64
    monkeypatch.setattr(RL, "frozen_hashes", lambda: froz)
    assert any("list SHA-256" in w for w in RL.check_launch(names))
    froz["MS11_CTRL"]["sha256"] = RL.list_sha256(RL.expand("MS11_CTRL"))
    froz["MS11_CTRL"]["keys_sha256"] = "1" * 64
    assert any("seed keys do not equal" in w for w in RL.check_launch(names))
    monkeypatch.undo()
    _clean_env(monkeypatch)
    monkeypatch.setattr(RL, "seed_keys", lambda rows_: [(12, 1, 0)])
    assert any("not in the confirmed key set" in w for w in RL.check_launch(names))
    monkeypatch.undo()
    _clean_env(monkeypatch)
    monkeypatch.setattr(shutil, "disk_usage", lambda p: type("U", (), {"free": 10})())
    assert any("free disk space" in w for w in RL.check_launch(names))
    monkeypatch.undo()
    _clean_env(monkeypatch)

    def bad(*a, **k):
        raise CR.CriteriaError("tag missing")
    monkeypatch.setattr(CR, "verify_frozen_criteria", bad)
    assert any(w.startswith("criteria loader") for w in RL.check_launch(names))


def test_check_launch_refuses_a_draft_data_file(monkeypatch):
    _clean_env(monkeypatch)
    st = RL.status()
    st[RL.definition_files()[0]] = "DRAFT"
    monkeypatch.setattr(RL, "status", lambda: st)
    assert any("not FROZEN" in w for w in RL.check_launch(("MS11_CTRL",)))


def test_the_shipped_eval_file_has_no_open_required_field_and_a_blanked_field_refuses_a_launch(monkeypatch):
    """11c (DL-345 to DL-364): all 14 fields of 11b are ruled, so the shipped file leaves none open; a field set back to null still refuses a real launch."""
    assert EC.open_fields() == []
    monkeypatch.setattr(P, "environment_info", lambda with_julia=True: {"git": {"dirty": False, "commit": "x"}})
    ch = copy.deepcopy(EC.load_choices())
    ch["within_boundary"] = None
    monkeypatch.setattr(EC, "load_choices", lambda path=None: ch)
    assert any("required evaluation fields still open" in w and "within_boundary" in w for w in RL.check_launch(("MS11_CTRL",)))
