"""MS11 11a: run counts of docs/ms11_plan.md and the proposed seed keys (DL-332, DL-333; UNVERIFIED until confirmed). Nothing integrates.

The seed-key test is the collision test of tests/test_ms9_seed_keys.py and tests/test_ms10_counts.py: the existing keys are the authority, written out
below from the decision log (and also scanned in the repository), and the proposal must be equal to, or a prefix of, none of them."""
import pytest

from mprsurge.analysis import ms8_counts as M8
from mprsurge.analysis import ms11_counts as M

from test_criteria_draft import _key_prefixes_in_repo
from test_ms9_seed_keys import CALIBRATION, KNOWN, _related

# Every key named in the 11a prompt (calibration [0]-[9]; MS7, MS8, MS9, MS10), written out so the test does not depend on a scan finding them.
EXISTING = ([(s,) for s in range(10)]
            + [(7, 4, s) for s in range(10)] + [(7, 9), (7, 9, 0)] + [(7, 9, 1, k) for k in range(64)]
            + [(8, 1, s) for s in range(10)] + [(8, 2, l, s) for l in range(3) for s in range(10)]
            + [(9, 1, s) for s in range(10)] + [(9, 2, 0)] + [(9, 3, s) for s in range(10)] + [(9, 4, s) for s in range(10)]
            + [(9, 5, s) for s in range(9)] + [(9, 6, s) for s in range(10)] + [(9, 7, s) for s in range(10)]
            + [(10, 1, s) for s in range(3)] + [(10, 2, c, s) for c in range(4) for s in range(3)]
            + [(10, 3, n, s) for n in range(4) for s in range(10)] + [(10, 4, l, s) for l in range(3) for s in range(3)]
            + [(10, 5, k, s) for k in range(12) for s in range(3)])


def _in_use():
    scan = {k for k in _key_prefixes_in_repo() if k[0] != 11}      # the repository scan, minus this proposal's own prefix
    return scan | set(KNOWN) | set(EXISTING)


def test_the_proposed_keys_collide_with_no_existing_key():
    mine = M.proposed_seed_keys()
    used = _in_use()
    assert (10, 5, 11, 2) in used and (9, 6, 0) in used and (8, 2, 2, 9) in used and (7, 9, 1, 63) in used
    assert len(mine) == len(set(mine)) == 10 + 10 + 2 * 3 * 10 + 3 + 6 * 3 == 101
    assert all(k[0] == 11 for k in mine)
    for m in mine:
        assert m not in CALIBRATION
        for u in used:
            assert not _related(m, u), (m, u)


def test_the_collision_test_has_teeth():
    """A proposal that reuses an existing key, or sits under or over one, must be caught by the same comparison."""
    used = _in_use()
    for bad in [(10, 1, 0), (10, 5, 0, 0), (9, 6, 3), (8, 2, 1, 4), (7, 9, 1, 5), (7, 9), (3,), (10, 1), (8, 2), (7, 4, 2)]:
        assert any(_related(bad, u) for u in used), bad
    assert not any(_related((11, 1, 0), u) for u in used)


def test_the_proposed_prefixes_do_not_overlap_each_other():
    pre = list(M.SEED_KEY_PREFIXES.values())
    for i, a in enumerate(pre):
        for b in pre[i + 1:]:
            assert not _related(a, b), (a, b)


def test_no_config_script_or_test_uses_a_key_starting_with_11_yet():
    """The 11a timing cells use [0] only; the proposal enters no config before the reviewer confirms the keys."""
    assert all(k[0] != 11 for k in _key_prefixes_in_repo())


def test_s11_counts_are_sigma_times_t_ramp_times_seeds():
    r = M.s11_runs()
    assert len(r) == 3 * 4 * 10 == 120
    assert {x["sigma_factor"] for x in r} == {0.5, 1.0, 2.0} and sorted({x["T_ramp_s"] for x in r}) == [10.0, 30.0, 120.0, 300.0]
    assert all(x["mode"] == "N" and x["dt_tau"] == 1.0e-3 for x in r)
    # kept 5 + 1.25 T + 10 s plus the 2 s discard, 100 tau per s: 29.5 + 54.5 + 167 + 392 = 643 s per (sigma, seed)
    assert sum(x["tau"] for x in r) == pytest.approx(30 * 643 * 100)
    assert sum(M8.heun_steps(x) for x in r) == pytest.approx(1.929e9, rel=1e-3)


def test_control_scopes():
    assert len(M.control_runs("none_new")) == 0 and len(M.control_runs("headline_T120")) == 3 * 10
    assert len(M.control_runs("twin_every_T_ramp")) == 3 * 4 * 10
    with pytest.raises(ValueError):
        M.control_runs("x")


def test_s13_mean_field_remainder_counts():
    n = lambda fam, r: sum(1 for x in r if x["family"] == fam)
    r = M.s13_mf_runs()                                        # 11b ruling (DL-337): Radau only at the headline T_ramp (plan 9.3 step 1), so none is new; floor at the default rung
    assert n("S13_rtol", r) == 2 * 2 and n("S13_delta0", r) == 2 * 2 and n("S13_radau", r) == 0 and n("S13_floor", r) == 2 * 3 * 10
    assert len(r) == 4 + 4 + 0 + 60 == 68
    assert M.DEFAULTS["M11-4_radau"] == "headline_only_cut_1"
    # the plan's full scope (11a reading): Radau 1e-10 at 10 and 316 s and 1e-12 at 10 s = 3 runs, 71 in all; 10 s only = 2
    assert n("S13_radau", M.s13_mf_runs({"M11-4_radau": "t10_and_t316"})) == 3 and len(M.s13_mf_runs({"M11-4_radau": "t10_and_t316"})) == 71
    assert n("S13_radau", M.s13_mf_runs({"M11-4_radau": "t10_only"})) == 2
    r = M.s13_mf_runs({"M11-4_floor_at_10_316": "full_ladder"})
    assert n("S13_floor", r) == 2 * 3 * 4 * 10
    assert n("S13_floor", M.s13_mf_runs({"M11-4_floor_at_10_316": "none"})) == 0


def test_s13_network_counts_and_cost_units():
    cfg = M.net_configs()
    assert cfg == [(100.0, 1e-3), (100.0, 5e-4), (100.0, 2.5e-4), (100.0, 1e-4), (200.0, 1e-3), (200.0, 1e-4)]
    assert len(M.s13_net_runs()) == 6 * 3 and len(M.s13_net_runs({"M11-5_net_seeds": 1})) == 6
    assert len(M.s13_net_runs({"M11-5_net_controls": "per_configuration"})) == 6 * 3 * 2
    # the dt ladder costs 1 + 2 + 4 + 10 = 17 times the 1e-3 rung (plan Table 9.1), the V_p +-200 pair 1 + 10 more
    u = [M.net_updates(r) for r in M.s13_net_runs({"M11-5_net_seeds": 1})]
    assert sum(u[:4]) / u[0] == pytest.approx(17.0) and (u[4] + u[5]) / u[0] == pytest.approx(11.0)
    assert u[0] == pytest.approx(2.95e10)                      # 2,950 tau incl. the 2 s discard, as the MS10 10 s cell


def test_prediction_arithmetic_on_synthetic_cells():
    cells = {"ms11_s11_t300": {"wall_s": 39.2, "tau": 39200.0}, "ms11_floorc_l2_dt1e-3_t316": {"wall_s": 41.0, "tau": 41000.0},
             "ms11_floorc_l2_dt1e-4_t316": {"wall_s": 82.0, "tau": 41000.0}, "ms11_dop_1e-10_t316": {"wall_s": 400.0, "tau": 41000.0},
             "ms11_dop_1e-12_t316": {"wall_s": 500.0, "tau": 41000.0}, "net_1e4": {"wall_s": 57.0, "tau": 2950.0},
             **{k: {"wall_s": 57.0, "tau": 2950.0} for k in M.NET_CELL.values() if k != "net_1e4"},
             **{c: {"wall_s": 30.0, "tau": 2750.0} for c in M8.RTOL_CELLS.values()}}
    assert M.heun_s_per_step(cells) == pytest.approx(39.2 / 39.2e6)
    assert M.floor_wall_s(cells, 41000.0, 1e-3) == pytest.approx(41.0) and M.floor_wall_s(cells, 41000.0, 1e-4) == pytest.approx(82.0)
    P = M.predict(cells)
    assert P["ms11_s11"]["runs"] == 120 + 30 and P["ms11_s13"]["carried_ms8_s"] == 1578.8
    assert M.d36(3600.0)["on_top_h"] == pytest.approx(15.21) and M.d36(3600.0)["replaced_h"] == pytest.approx(14.21 - 1.0075 + 1.0)
    assert not M.d36(10 * 3600.0)["within_cap"]


def test_ruled_counts_11b_total_236():
    """DL-337: Radau cut to the headline T_ramp; 120 S11 + 30 controls + 68 S13 mean field + 18 S13 network = 236 (the 2 optional RB9(d) runs are in no list)."""
    c = M.counts()
    assert {k: v["runs"] for k, v in c.items()} == M.RULED_COUNTS == {"S11": 120, "S11_control": 30, "S13_mf": 68, "S13_net": 18}
    assert M.RULED_TOTAL == 236
