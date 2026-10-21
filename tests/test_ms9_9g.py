"""MS9 9g: the M9-22 control list (S12x_ctrl_mf): 225 subgrid cells x 10 seeds, mode N, start state held by configuration alone, key [9, 7, s]. Nothing integrates."""
import pytest

from mprsurge import config as C
from mprsurge.analysis import ms9_counts as M
from mprsurge.analysis import ms9_runlist as RL

from test_criteria_draft import _key_prefixes_in_repo
from test_ms9_seed_keys import CALIBRATION, KNOWN, _related


@pytest.fixture(scope="module")
def ctrl():
    return RL.expand("S12x_ctrl_mf")


@pytest.fixture(scope="module")
def sub():
    return RL.expand("S7_subgrid")


def test_the_control_is_exploratory_and_outside_every_other_list(ctrl):
    assert "S12x_ctrl_mf" in RL.ALL_LISTS and "S12x_ctrl_mf" not in RL.PRE_REGISTERED + RL.SUPPLEMENTARY + RL.EXPLORATORY
    assert len(ctrl) == 2250 and all(not r["pre_registered"] for r in ctrl)
    assert len({r["hash"] for r in ctrl}) == 2250
    other = {r["hash"] for n in RL.PRE_REGISTERED + RL.SUPPLEMENTARY + RL.EXPLORATORY for r in RL.expand(n)}
    assert not {r["hash"] for r in ctrl} & other


def test_key_9_7_s_collides_with_nothing():
    mine = [k for k in M.exploratory_seed_keys() if k[:2] == (9, 7)]
    assert mine == [(9, 7, s) for s in range(10)]
    others = [k for k in M.proposed_seed_keys() + M.exploratory_seed_keys() if k not in mine] + sorted(_key_prefixes_in_repo() | set(KNOWN))
    for k in mine:
        assert k not in CALIBRATION
        for u in others:
            assert not _related(k, u), (k, u)


def test_the_control_is_the_subgrid_with_the_start_state_held(ctrl, sub):
    assert len(ctrl) == len(sub)
    for a, b in zip(ctrl, sub):                     # same cell order, same seed order, same stream per (cell, seed)
        assert a["spawn_key"][2] == b["spawn_key"][2] and a["spawn_key"][:2] == [9, 7]
        ca, cb = a["cfg"], b["cfg"]
        assert a["kind"] == b["kind"] == "mf_noisy" and ca["path"]["name"] == cb["path"]["name"] == "path_hypoxia"
        for k in ("T_ramp_s", "t_on_s", "J_lag_frac", "J_T_frac", "J0", "profile"):
            assert ca["path"][k] == cb["path"][k]
        for k in ("Delta", "tau_d_ms", "J"):
            assert ca["model"][k] == cb["model"][k]
        assert ca["path"]["eta_peak"] == ca["path"]["eta_start"] == cb["path"]["eta_start"] and ca["path"]["J_end"] == ca["path"]["J0"]
        assert ca["noise"] == cb["noise"] and ca["durations"] == cb["durations"] and ca["solver"] == cb["solver"]


def test_the_control_path_is_constant():
    import numpy as np
    from mprsurge import ramps
    r = RL.expand("S12x_ctrl_mf")[7]["cfg"]
    p = ramps.make_path(r)
    t = np.linspace(0, p.t_ramp_end * 1.2, 50)
    assert np.ptp(p.eta(t)) == 0 and np.ptp(p.J(t)) == 0 and np.ptp(p.Delta(t)) == 0


# --- report script helpers (scripts/report_ms9_9g.py) ---------------------------------------------------------------
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("report_ms9_9g", ROOT / "scripts" / "report_ms9_9g.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def test_fractions_use_the_three_table_2_1_categories():
    f = R.fractions(["NS", "S+", "S-rel", "S-abs", "S-sus", "S-sus", "NS", "NS"])
    assert f == {"n": 8, "NS": 3, "surge": 3, "S-sus": 2, "other": 0}
    assert R.fractions(["failed", "NS"])["other"] == 1


def test_eta_delay_is_eta_at_onset_minus_eta_h_on_the_runs_own_path():
    import json
    jp = ROOT / "results/S5/ramp/p2_linear/p2_linear_0000_daf4ac49ab2e.json"
    if not jp.exists():
        pytest.skip("S5 results not present")
    cfg = json.loads(jp.read_text(encoding="utf-8"))["config"]
    p = cfg["path"]
    assert abs(R.eta_delay(cfg, p["t_on_s"]) - (p["eta_start"] - p["eta_H"])) < 1e-9       # at t_on eta = eta_start
    assert R.eta_delay(cfg, float("nan")) != R.eta_delay(cfg, float("nan"))                 # nan stays nan


def test_baseline_stats_on_a_stored_subgrid_record():
    recs = sorted((ROOT / "results/S7/S7_subgrid").glob("*.json"))
    recs = [r for r in recs if not r.name.endswith(".dry.json")]
    if not recs:
        pytest.skip("subgrid results not present")
    b = R.baseline_stats(recs[0])
    assert b["W_s"] == 2.0 and b["n_baseline"] >= 1 and b["ratio"] >= 1.0 and b["odds_min"] > 0
