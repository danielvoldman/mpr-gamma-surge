"""MS9 9c: S12x exploratory lists, seed keys [9, 5, s] and [9, 6, s], and the decomposition of a classifier decision. Nothing integrates."""
import csv
import json

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import ramps
from mprsurge.analysis import ms9_counts as M
from mprsurge.analysis import ms9_nc1_decomp as DC
from mprsurge.analysis import ms9_runlist as RL
from mprsurge.analysis import surge_metrics as SM

from test_criteria_draft import _key_prefixes_in_repo
from test_ms9_seed_keys import CALIBRATION, KNOWN, _related

LISTS_DIR = C.repo_root() / RL.RUNLIST_DIR


def test_exploratory_keys_collide_with_nothing_in_use_or_proposed():
    mine = M.exploratory_seed_keys()
    assert len(mine) == len(set(mine)) == 19 and (9, 5, 8) in mine and (9, 5, 9) not in mine and (9, 6, 9) in mine
    others = M.proposed_seed_keys() + sorted(_key_prefixes_in_repo() | set(KNOWN))
    for k in mine:
        assert k not in CALIBRATION
        for u in others:
            if u in mine:
                continue
            assert not _related(k, u), (k, u)
    assert (9, 2, 0) not in mine                     # the original NC1 network seed is the 10th and keeps its own key


def test_exploratory_prefixes_do_not_overlap_the_others():
    pre = list(M.SEED_KEY_PREFIXES.values())
    assert (9, 5) in pre and (9, 6) in pre
    for i, a in enumerate(pre):
        for b in pre[i + 1:]:
            assert not _related(a, b), (a, b)


@pytest.fixture(scope="module")
def lists():
    return {n: RL.expand(n) for n in RL.EXPLORATORY}


def test_the_s12x_lists_are_exploratory_and_outside_the_counts(lists):
    assert [len(lists[n]) for n in RL.EXPLORATORY] == [9, 10]
    assert all(not r["pre_registered"] for rows in lists.values() for r in rows)
    assert not set(RL.EXPLORATORY) & set(RL.PRE_REGISTERED + RL.SUPPLEMENTARY)
    pre = {r["hash"] for n in RL.PRE_REGISTERED + RL.SUPPLEMENTARY if n not in ("S7_map1", "S7_map2", "S7_subgrid") for r in RL.expand(n)}
    mine = [r["hash"] for rows in lists.values() for r in rows]
    assert len(set(mine)) == 19 and not set(mine) & pre
    manifest = json.loads((LISTS_DIR / "ms9_runlists.json").read_text(encoding="utf-8"))
    assert manifest["pre_registered_total"] == 3618 and manifest["supplementary_total"] == 132 and set(manifest["lists"]) == set(RL.PRE_REGISTERED + RL.SUPPLEMENTARY)


def test_the_s12x_keys_and_outputs(lists):
    assert [r["spawn_key"] for r in lists["S12x_NC1_net"]] == [[9, 5, s] for s in range(9)]
    assert [r["spawn_key"] for r in lists["S12x_const_net"]] == [[9, 6, s] for s in range(10)]
    assert all(r["kind"] == "network" and "results/S12x/" in r["out_dir"].replace("\\", "/") for rows in lists.values() for r in rows)
    assert all(r["cfg"]["network"]["N"] == 10000 and r["cfg"]["path"]["T_ramp_s"] == 120.0 for rows in lists.values() for r in rows)


def test_the_ramp_list_is_the_nc1_network_run_at_other_seeds(lists):
    nc1 = [r for r in RL.expand("NC1") if r["family"] == "NC1_net"][0]["cfg"]
    for r in lists["S12x_NC1_net"]:
        a, b = dict(r["cfg"]), dict(nc1)
        for d in (a, b):
            d.pop("seeds"), d.pop("run"), d.pop("output"), d.pop("_resolved_from", None)
        assert a == b


def test_the_const_list_holds_the_start_state_by_configuration_alone(lists):
    for r in lists["S12x_const_net"]:
        cfg = r["cfg"]
        assert cfg["path"]["eta_start"] == cfg["path"]["eta_peak"] == pytest.approx(1.3960461989737856)
        p = ramps.make_path(cfg)
        t = np.linspace(0.0, p.t_ramp_end + 1000.0, 400)
        assert np.ptp(p.eta(t)) == 0.0 and np.ptp(p.J(t)) == 0.0 and np.ptp(p.Delta(t)) == 0.0 and np.ptp(p.I(t)) == 0.0
        assert p.eta(t)[0] == pytest.approx(1.3960461989737856) and cfg["model"]["J"] == -21.0 and cfg["model"]["Delta"] == 0.3


def test_the_committed_s12x_csvs_equal_a_regeneration(lists, tmp_path):
    RL.write_manifest(out_dir=tmp_path, names=RL.EXPLORATORY, json_name="ms9_s12x_runlists.json")
    for n in RL.EXPLORATORY:
        assert (tmp_path / f"runlist_{n}.csv").read_text(encoding="utf-8") == (LISTS_DIR / f"runlist_{n}.csv").read_text(encoding="utf-8")
    assert (tmp_path / "ms9_s12x_runlists.json").read_text(encoding="utf-8").replace("\r\n", "\n") == (LISTS_DIR / "ms9_s12x_runlists.json").read_text(encoding="utf-8").replace("\r\n", "\n")


# --- decomposition -------------------------------------------------------------------------------

def _signal(burst=True, seed=3):
    rng = np.random.default_rng(seed)
    n = 60000
    t = np.arange(n) / 1000.0
    v = 0.04 * rng.standard_normal(n)
    if burst:
        g = ((t > 20) & (t < 26)) * np.sin(np.pi * (t - 20) / 6) ** 2
        v = v + 0.5 * g * np.sin(2 * np.pi * 42.0 * t)
    return v


def test_decomposition_v0_equals_the_frozen_classifier():
    v = _signal()
    thr = 0.2176
    res = SM.classify_mode_n(v, 1000.0, 10.0, 30.0, thr)
    d = DC.decompose(v, 10.0, 30.0, thr, thr / 0.1)
    assert d["class"] == res.cls and res.cls != "NS"
    assert d["episode"]["onset_s"] == res.episode.onset_s and d["episode"]["cycles"] == res.episode.cycles
    assert d["d8"]["t_start_s"] == res.d8.t_start


def test_episode_bookkeeping_identities():
    v = _signal()
    d = DC.decompose(v, 10.0, 30.0, 0.2176, 2.176)
    ew, ep, wt = d["episode_windows"], d["episode"], d["_wt"]
    assert ew["duration_s"] == ep["duration_s"] == ew["windows"] * wt["step"]
    assert ew["cycles"] == pytest.approx(ep["cycles"]) and ew["onset_s"] == ep["onset_s"] and ew["end_s"] == ep["end_s"]
    assert ew["end_minus_onset_s"] == pytest.approx(ew["duration_s"] - wt["step"] / 2)
    b = d["baseline"]
    assert b["n_windows"] == int(wt["baseline_mask"].sum()) and b["p_g_max_over_min"] >= 1.0


def test_variants_run_and_the_default_is_unchanged():
    from mprsurge.analysis import a8_sensitivity as A8S
    v = _signal(burst=False)
    out = {k: DC.decompose(v, 10.0, 30.0, 0.2176, 2.176, variant=k)["class"] for k in A8S.VARIANTS}
    assert set(out) == set(A8S.VARIANTS) and out["V0"] == SM.classify_mode_n(v, 1000.0, 10.0, 30.0, 0.2176).cls
