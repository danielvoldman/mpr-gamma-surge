"""MS9 9b: run lists, configs, rulings M9-1 to M9-21 as code (DL-213 to DL-215). Nothing integrates."""
import csv
import json
from pathlib import Path

import numpy as np
import pytest
import yaml

from mprsurge import config as C
from mprsurge import criteria as CR
from mprsurge.analysis import cells as CE
from mprsurge.analysis import ms9_counts as M
from mprsurge.analysis import ms9_runlist as RL

ROOT = C.repo_root()
LISTS_DIR = ROOT / RL.RUNLIST_DIR
SMALL = ("NC1", "NC2", "NC3", "S6", "S16", "SUPP_P2ref", "SUPP_NC1_modeN")


@pytest.fixture(scope="module")
def manifest():
    return json.loads((LISTS_DIR / "ms9_runlists.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def small():
    return {n: RL.expand(n) for n in SMALL}


def test_the_cell_list_is_the_frozen_one():
    cells = RL.load_cells()                                   # raises if the hash differs
    assert len(cells) == 1 + 900 + 325
    crit = yaml.safe_load((ROOT / "configs/robustness_criteria.yaml").read_text(encoding="utf-8"))
    assert RL.FROZEN_CELL_LIST_SHA256 in json.dumps(crit)
    assert CE.cell_list_hash(list(cells)) == RL.FROZEN_CELL_LIST_SHA256 == "8e67bbd2b366e86ffee59e732dd79824bdce82c73c477436cb3b1689b0a328d9"


@pytest.mark.slow
def test_the_cell_file_equals_a_rebuild_from_the_hopf_scan(tmp_path):
    p = tmp_path / "cells.csv"
    assert RL.build_cells_file(p) == RL.FROZEN_CELL_LIST_SHA256
    assert p.read_text(encoding="utf-8") == (ROOT / RL.CELLS_FILE).read_text(encoding="utf-8")


def test_counts_are_3618_and_equal_ms9_counts(manifest):
    L = manifest["lists"]
    assert manifest["pre_registered_total"] == 3618 and manifest["supplementary_total"] == 132
    f = M.all_runs()
    assert L["S6"]["runs"] == len(f["S6"]) == 20
    assert L["S7_map1"]["runs"] == len(f["S7_map1"]) == 900 and L["S7_map2"]["runs"] == len(f["S7_map2"]) == 325
    assert L["S7_subgrid"]["runs"] == len(f["S7_noisy"]) == 2250 and L["S16"]["runs"] == len(f["S16"]) == 78
    assert L["NC1"]["runs"] + L["NC2"]["runs"] + L["NC3"]["runs"] == len(f["S12"]) + len(f["S12_net"]) == 45
    assert L["NC1"]["by_family"] == {"NC1": 13, "NC1_cells": 5, "NC1_net": 1}
    assert sum(v["runs"] for n, v in L.items() if n in RL.PRE_REGISTERED) == 3618
    assert {n for n, v in L.items() if not v["pre_registered"]} == set(RL.SUPPLEMENTARY)
    assert L["SUPP_P2ref"]["runs"] == 2 and L["SUPP_NC1_modeN"]["runs"] == 13 * 10


def test_pre_registered_and_supplementary_lists_are_separate(small):
    pre = {r["hash"] for n in ("NC1", "NC2", "NC3", "S6", "S16") for r in small[n]}
    for n in RL.SUPPLEMENTARY:
        assert not any(r["pre_registered"] for r in small[n])
        assert not ({r["hash"] for r in small[n]} & pre)
        assert all("supp" in r["out_dir"] for r in small[n])           # their own output directories
    assert all(r["pre_registered"] for n in ("NC1", "NC2", "NC3", "S6", "S16") for r in small[n])


def test_the_only_repeated_run_across_the_pre_registered_lists_is_s6_p3_i1_at_10_s_equal_nc2(small):
    seen: dict[str, list] = {}
    for n in ("NC1", "NC2", "NC3", "S6", "S16"):
        for r in small[n]:
            seen.setdefault(r["hash"], []).append(r["name"])
    dup = [v for v in seen.values() if len(v) > 1]
    assert len(dup) == 1 and {x.split("_")[0] for x in dup[0]} == {"S6", "NC2"}


def test_nc1_m9_1_eta_falls_by_the_cells_own_amount(small):
    cells = RL.load_cells()
    rows = small["NC1"]
    assert [r["T_ramp_s"] for r in rows[:13]] == RL.GRID13 and all(r["T_ramp_s"] == 120.0 for r in rows[13:])
    h = cells[0]
    for r in rows[:13]:
        p, m = r["cfg"]["path"], r["cfg"]["model"]
        assert r["path"] == "path_eta" and r["kind"] == "mf" and m["I_drive"] == 0.0 and p["I_amp"] == 0.0
        assert p["eta_start"] == h["eta_start"] == pytest.approx(1.3960461989737856)
        assert p["eta_start"] - p["eta_peak"] == pytest.approx(h["eta_peak"] - h["eta_start"]) and p["eta_peak"] < p["eta_start"]
        assert (m["J"], m["Delta"], m["tau_d_ms"]) == (-21.0, 0.3, 5.0) and p["t_on_s"] == 5.0 and p["profile"] == "linear"
    for r, (i, j) in zip(rows[13:18], RL.NC1_MAP_CELLS):
        c = cells[1 + i * 30 + j]
        p, m = r["cfg"]["path"], r["cfg"]["model"]
        assert (m["Delta"], m["tau_d_ms"]) == (c["Delta"], c["tau_d_ms"]) and m["J"] == -21.0
        assert p["eta_start"] == c["eta_start"] and p["eta_start"] - p["eta_peak"] == pytest.approx(c["eta_peak"] - c["eta_start"])
    # no-Hopf cells use the D12 fallback (the headline eta_H) through the cell file itself
    for c in cells:
        if not c["hopf_found"]:
            assert c["eta_H"] == CE.headline_eta_H()


def test_nc1_cells_are_the_four_corners_and_the_cell_nearest_the_headline():
    assert RL.NC1_MAP_CELLS == ((0, 0), (0, 29), (29, 0), (29, 29), (14, 12))
    d = np.linspace(0.01, 0.6, 30)
    t = np.geomspace(1.0, 50.0, 30)
    dist = np.hypot((d[:, None] - 0.3) / (0.6 - 0.01), (np.log(t)[None, :] - np.log(5.0)) / (np.log(50.0) - 0.0))
    assert np.unravel_index(np.argmin(dist), dist.shape) == (14, 12)
    c = RL.map1_cell(14, 12)
    assert c["Delta"] == pytest.approx(0.29483, abs=5e-6) and c["tau_d_ms"] == pytest.approx(5.0469, abs=5e-5)


def test_nc1_network_run(small):
    r = small["NC1"][-1]
    assert r["family"] == "NC1_net" and r["kind"] == "network" and r["cfg"]["network"]["N"] == 10000 and r["T_ramp_s"] == 120.0
    assert r["spawn_key"] == [9, 2, 0] and r["cfg"]["seeds"]["spawn_key"] == [9, 2, 0]


def test_nc2_m9_2_and_nc3_m9_3(small):
    for r in small["NC2"]:
        p = r["cfg"]["path"]
        assert r["path"] == "path_drive" and p["I_amp"] == 1.0 and p["eta_H"] == pytest.approx(2.8960461989737856)
    assert [r["T_ramp_s"] for r in small["NC2"]] == RL.GRID13
    for r in small["NC3"]:
        p = r["cfg"]["path"]
        assert r["path"] == "path_hypoxia" and p["J0"] == -21.0 and p["J_end"] == -40.0 and p["J_lag_frac"] == 0.0 and p["J_T_frac"] == 1.0
        assert p["eta_start"] > p["eta_peak"]                                  # eta falls as in NC1
        from mprsurge import ramps
        path = ramps.make_path(r["cfg"])
        T = r["T_ramp_s"] / 0.01
        assert path.t_ramp_end == pytest.approx(path.t_on + T)                 # J and eta end together at t_on + T_ramp
        assert float(path.J(path.t_ramp_end)) == pytest.approx(-40.0) and float(path.J(path.t_on)) == pytest.approx(-21.0)


def test_s6_m9_8_m9_9(small):
    rows = small["S6"]
    assert len(rows) == 20
    p3 = [r for r in rows if r["family"] == "S6_P3"]
    assert sorted({r["cfg"]["path"]["I_amp"] for r in p3}) == [0.5, 1.0, 2.0] and {r["T_ramp_s"] for r in rows} == {10.0, 30.0, 120.0, 300.0}
    assert {r["cfg"]["path"]["Delta_factor"] for r in rows if r["family"] == "S6_P4a"} == {1.5}
    assert [r["cfg"]["path"]["Delta_factor"] for r in rows if r["family"] == "S6_P4b"] == pytest.approx([2.0 / 3.0] * 4)
    assert all(r["cfg"]["path"]["profile"] == "linear" and r["cfg"]["model"]["Delta"] == 0.3 for r in rows)
    ref = small["SUPP_P2ref"]
    assert [r["T_ramp_s"] for r in ref] == [30.0, 300.0] and all(r["path"] == "path_hypoxia" and r["cfg"]["path"]["I_amp"] == 0.0 for r in ref)


def test_subgrid_m9_10():
    idx = RL.subgrid_indices()
    assert idx == [0, 2, 4, 6, 8, 10, 12, 15, 17, 19, 21, 23, 25, 27, 29] == [int(x) for x in M.subgrid_indices()]
    assert len(RL.subgrid_indices_sha256()) == 64


def test_subgrid_run_list_m9_10_m9_14():
    rows = []
    with open(LISTS_DIR / "runlist_S7_subgrid.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2250 and {r["kind"] for r in rows} == {"mf_noisy"} and {float(r["T_ramp_s"]) for r in rows} == {120.0}
    keys = {tuple(json.loads(r["spawn_key"])) for r in rows}
    assert keys == {(9, 1, s) for s in range(10)}
    cells = {(json.loads(r["overrides"])["model.Delta"], json.loads(r["overrides"])["model.tau_d_ms"]) for r in rows}
    assert len(cells) == 225
    map1 = {(RL.map1_cell(i, j)["Delta"], RL.map1_cell(i, j)["tau_d_ms"]) for i in range(30) for j in range(30)}
    assert cells <= map1                                                         # every subgrid cell is a map-1 cell


def test_supplementary_nc1_mode_n_m9_4(small):
    rows = small["SUPP_NC1_modeN"]
    assert len(rows) == 130 and {r["kind"] for r in rows} == {"mf_noisy"}
    assert {tuple(r["spawn_key"]) for r in rows} == {(9, 4, s) for s in range(10)}
    assert [r["T_ramp_s"] for r in rows[::10]] == RL.GRID13
    assert all(r["cfg"]["path"]["eta_start"] > r["cfg"]["path"]["eta_peak"] and r["cfg"]["noise"]["sigma"] == 0.0624 for r in rows)
    keys = {tuple(r["spawn_key"]) for n in SMALL for r in small[n] if r["spawn_key"]}
    assert (9, 4, 0) in keys and not any(k[:2] == (9, 3) for k in keys)           # [9, 3, s] stays reserved and unused


def test_s16_m9_11(small):
    rows = small["S16"]
    oat, lhs = rows[:14], rows[14:]
    assert len(oat) == 14 and len(lhs) == 64
    nom = RL.nominal()
    assert nom["eta_start"] == pytest.approx(1.396046, abs=1e-6) and nom["eta_peak"] == pytest.approx(4.896046, abs=1e-6)
    k = 0
    for p in RL.RB4_PARAMETERS:
        for s in (-1, 1):
            cfg = oat[k]["cfg"]
            got = {"eta_start": cfg["path"]["eta_start"], "eta_peak": cfg["path"]["eta_peak"], "J0": cfg["path"]["J0"], "Delta": cfg["model"]["Delta"],
                   "tau_d_ms": cfg["model"]["tau_d_ms"], "J_lag_frac": cfg["path"]["J_lag_frac"], "J_T_frac": cfg["path"]["J_T_frac"]}
            for q in RL.RB4_PARAMETERS:
                want = nom[q] * (1.0 + 0.1 * s) if q == p else nom[q]
                assert got[q] == pytest.approx(want, rel=1e-12), (p, s, q)
            assert cfg["model"]["J"] == cfg["path"]["J0"]
            k += 1
    # eta_start and eta_peak stay at the nominal values when Delta, tau_d or J0 is perturbed (hold)
    for r in oat[4:10]:
        assert r["cfg"]["path"]["eta_start"] == pytest.approx(nom["eta_start"]) and r["cfg"]["path"]["eta_peak"] == pytest.approx(nom["eta_peak"])
    assert [r["spawn_key"] for r in lhs] == [[7, 9, 1, i] for i in range(64)]
    assert all(r["spawn_key"] is None for r in oat)


def test_lhs_design_is_reproducible_stratified_and_in_the_box():
    X = RL.lhs_design()
    assert X.shape == (64, 7) and np.array_equal(X, RL.lhs_design())
    nom = np.array([RL.nominal()[p] for p in RL.RB4_PARAMETERS])
    f = X / nom
    assert f.min() >= 0.9 - 1e-12 and f.max() <= 1.1 + 1e-12
    for col in range(7):                                                       # one point per stratum of width 1/64 in every column
        assert sorted(np.floor((f[:, col] - 0.9) / 0.2 * 64).astype(int)) == list(range(64))
    saved = np.loadtxt(LISTS_DIR / "s16_lhs_design.csv", delimiter=",", skiprows=1)[:, 1:]
    assert np.array_equal(saved, X)


@pytest.mark.parametrize("cfgfile", sorted(p.name for p in (ROOT / "configs/ms9").glob("*.yaml")))
def test_every_ms9_config_names_the_frozen_criteria_and_passes_the_loader_gate(cfgfile):
    d = yaml.safe_load((ROOT / "configs/ms9" / cfgfile).read_text(encoding="utf-8"))
    assert d["robustness"]["criteria_file"] == "configs/robustness_criteria.yaml"
    assert "seeds" not in d                                                    # keys come from the run list
    cfg = C.resolve_config(ROOT / "configs/ms9" / cfgfile)
    CR.require_frozen_for_config(cfg)
    assert CR.is_frozen_criteria_path(cfg["robustness"]["criteria_file"])


@pytest.mark.parametrize("name", SMALL)
def test_committed_run_lists_equal_a_regeneration(name, small, manifest):
    rows = small[name]
    assert RL.list_sha256(rows) == manifest["lists"][name]["sha256"]
    with open(LISTS_DIR / f"runlist_{name}.csv", newline="", encoding="utf-8") as fh:
        saved = list(csv.DictReader(fh))
    assert [r["hash"] for r in saved] == [r["hash"] for r in rows] and [r["name"] for r in saved] == [r["name"] for r in rows]


@pytest.mark.slow
@pytest.mark.parametrize("name", ("S7_map1", "S7_map2", "S7_subgrid"))
def test_committed_map_run_lists_equal_a_regeneration(name, manifest):
    rows = RL.expand(name)
    assert RL.list_sha256(rows) == manifest["lists"][name]["sha256"] and not RL.duplicates(rows)


def test_every_seed_key_in_the_lists_is_proposed_or_settled(small):
    allowed = set(M.proposed_seed_keys()) | {(7, 9, 1, k) for k in range(64)}
    for n in SMALL:
        for r in small[n]:
            if r["spawn_key"] is not None:
                assert tuple(r["spawn_key"]) in allowed
    assert len({tuple(r["spawn_key"]) for r in small["SUPP_NC1_modeN"]}) == 10
