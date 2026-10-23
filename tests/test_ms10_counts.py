"""MS10 10a: run counts of docs/ms10_plan.md and the proposed seed keys (DL-275; UNVERIFIED until confirmed). Nothing integrates."""
import math

import pytest

from mprsurge.analysis import ms10_counts as M

from test_criteria_draft import _key_prefixes_in_repo
from test_ms9_seed_keys import CALIBRATION, KNOWN, _related

# The MS9 keys named in the decision log, written out so that the test does not depend on a scan finding them.
MS9_KEYS = ([(9, 1, s) for s in range(10)] + [(9, 2, 0)] + [(9, 3, s) for s in range(10)] + [(9, 4, s) for s in range(10)]
            + [(9, 5, s) for s in range(9)] + [(9, 6, s) for s in range(10)] + [(9, 7, s) for s in range(10)])


def test_p2_update_counts_match_the_5f_work_counts():
    assert M.updates(1e4, 10.0) == pytest.approx(2.95e10)            # 2,950 tau incl. the 2 s discard (DL-118)
    assert M.updates(1e4, 120.0) == pytest.approx(1.67e11)           # 16,700 tau
    assert M.updates(1e4, 60.0) == pytest.approx(9.2e10)
    assert M.updates(1e4, 30.0) == pytest.approx(5.45e10)


def test_run_counts_with_the_arithmetic_of_the_plan():
    assert M.n_runs(M.s9_runs()) == 4 * 10 == 40
    assert M.n_runs(M.s8_runs(3)) == 2 * 3 + 4 * 3 == 18 and M.n_runs(M.s8_runs(1)) == 10 and M.n_runs(M.s8_runs(10)) == 46
    assert M.n_runs(M.s10_runs(False)) == 3 * 3 == 9 and M.n_runs(M.s10_runs(True)) == 2 * 3 == 6
    assert M.total_updates(M.s9_runs()) == pytest.approx(10 * 9.2e6 * (1e3 + 3e3 + 1e4 + 3e4))      # 4.05e12 (plan Table 9.1: 4.0e12)
    assert M.total_updates(M.s8_runs(3)) == pytest.approx(1.2435e12)                                # DL-118: 1.24e12
    assert M.total_updates(M.s10_runs(False)) == pytest.approx(8.28e11)                             # DL-118: 8.3e11


def test_control_scopes_and_counts():
    assert len(M.control_configs()) == 12
    ramp = M.s8_runs(3) + M.s9_runs() + M.s10_runs(False)
    assert M.n_runs(M.control_runs("C0_none_new", 3, ramp)) == 0
    assert M.n_runs(M.control_runs("C1_headline_N1e4", 3, ramp)) == 3 * 3
    assert M.n_runs(M.control_runs("C1_headline_N1e4", 10, ramp)) == 30
    assert M.n_runs(M.control_runs("C2_every_configuration", 3, ramp)) == 12 * 3
    assert M.n_runs(M.control_runs("C2_every_configuration", 10, ramp)) == 120
    assert M.n_runs(M.control_runs("C3_twin_of_every_ramp_run", 3, ramp)) == M.n_runs(ramp) == 18 + 40 + 9
    with pytest.raises(ValueError):
        M.control_runs("x", 3, ramp)


def test_prediction_is_sum_over_workers_bounded_by_the_longest_run():
    rate = {n: 2e-9 for n in M.S9_N}
    p = M.predict_s(M.s9_runs(), rate, 10)
    assert p["sum_s"] == pytest.approx(M.total_updates(M.s9_runs()) * 2e-9)
    assert p["wall_s"] == pytest.approx(max(p["sum_s"] / 10, p["longest_s"]))
    assert math.isclose(p["longest_s"], 3e4 * 9.2e6 * 2e-9)


def test_launch_rule_and_d36_arithmetic():
    v = M.verdict(2700.0, M.ALLOWANCE_ROW_S)
    assert v["limit_s"] == 2700.0 and v["ok"] and not M.verdict(2701.0, M.ALLOWANCE_ROW_S)["ok"]
    assert M.verdict(600.0, M.ALLOWANCE_ROW_S)["ratio"] == pytest.approx(1 / 3)
    t = M.d36_totals(3600.0)
    assert t["on_top_h"] == pytest.approx(14.595) and t["replaced_h"] == pytest.approx(12.095) and t["within_cap"]
    assert not M.d36_totals(11 * 3600.0)["within_cap"]


def test_proposed_keys_are_unique_first_element_10_and_collide_with_nothing_in_use():
    mine = M.proposed_seed_keys()
    assert len(mine) == len(set(mine)) == 3 + 40 + 40 + 9 + 160 == 252
    assert all(k[0] == 10 for k in mine)
    used = _key_prefixes_in_repo() | set(KNOWN) | set(MS9_KEYS)
    assert (9, 6, 0) in used and (8, 1) in used          # the scan and the written-out lists see the earlier keys
    for m in mine:
        assert m not in CALIBRATION
        for u in used:
            assert not _related(m, u), (m, u)


def test_the_proposed_prefixes_do_not_overlap_each_other():
    pre = list(M.SEED_KEY_PREFIXES.values())
    for i, a in enumerate(pre):
        for b in pre[i + 1:]:
            assert not _related(a, b), (a, b)


def test_the_ms9_keys_written_out_here_equal_the_ms9_proposal():
    from mprsurge.analysis import ms9_counts as M9
    assert set(MS9_KEYS) == set(M9.proposed_seed_keys()) | set(M9.exploratory_seed_keys())


def test_the_collision_rule_has_teeth():
    assert _related((10, 3, 2, 4), (10, 3)) and not _related((10, 1, 0), (9, 1))
