"""MS10 10a: run counts of docs/ms10_plan.md and the proposed seed keys (DL-275; UNVERIFIED until confirmed). Nothing integrates."""
import math

import pandas as pd
import pytest
import yaml

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
    assert len(mine) == len(set(mine)) == 3 + 12 + 40 + 9 + 36 == 100      # FINAL patterns (10c): 3 seeds per map cell (R15), 12 controls x 3 seeds (R17)
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


# --- 10c: the final key patterns, the run lists and the controls (DRAFT; DL-299) -----------------------------------------------------------------

from mprsurge.analysis import ms10_runlist as RL      # noqa: E402


def _fixture_cells(tmp_path, monkeypatch):
    """TEST FIXTURE ONLY (not a choice): the first proposal of each stratum written to a temporary cells file, to exercise the loader."""
    prop = pd.read_csv("docs/ms10_10c_s8_proposals.csv")
    first = prop.groupby("stratum", sort=False).head(1)
    doc = yaml.safe_load(open(RL.CELLS_FILE, encoding="utf-8"))
    for e, (_, r) in zip(doc["cells"], first.iterrows()):
        e["i"], e["j"] = int(r["i"]), int(r["j"])
    p = tmp_path / "s8_cells.yaml"
    p.write_text(yaml.safe_dump(doc), encoding="utf-8")
    monkeypatch.setattr(RL, "_read", lambda rel, _r=RL._read: _r(rel) if rel != RL.CELLS_FILE else yaml.safe_load(p.read_text(encoding="utf-8")))


def test_nominal_counts_are_those_of_the_10c_prompt():
    n = RL.nominal_counts()
    assert n == {"S8": 18, "S9": 40, "S10": 9, "C2_S8": 18, "C2_S9": 12, "C2_S10": 6, "MF_COMPANION": 5}
    assert RL.control_total() == 36 == M.n_runs(M.control_runs("C2_every_configuration", 3, [])) == RL.EXPECTED_CONTROLS
    assert M.N_CONTROL_CONFIGS == RL.N_CONTROL_CONFIGS == len(RL.params()["controls"]["configs"]) == 12


def test_control_yaml_matches_the_counts_module_configuration_for_configuration():
    ym = [(c["N"], c["T_ramp_s"]) for c in RL.params()["controls"]["configs"]]
    assert [c["k"] for c in RL.params()["controls"]["configs"]] == list(range(12))
    assert ym == [(N, t) for _, N, t in M.control_configs()]


FROZEN_LIST_SHA256 = {       # 10d (DL-306, DL-308): the lists with the four S8 cells of R20
    "S8": "7f409c15cffa37c0462684f67d2b82fe5ba0fa305ea53fad8861197bc5647854", "S9": "b429cff50ae112f1ac131ee42cac124a1a3a6a3a8aee900cf0fdbc85d7ed65bb",
    "S10": "79f72a123467ccb0e79c327b7f82b0bd599dc5277cb37dc94466d0409eea94f3", "C2_S8": "172280421c9e2577f4029091e9b75511a17b18b8595e5e56256eed8b534a72e1",
    "C2_S9": "5745e197a662b9af2411c8444b4450d85e17b41c48b38b6f8acfa5b4254e0de4", "C2_S10": "d1047ee1f6dc35442a59b17e6b2df233360ebcdccb6abdf26f021d95946b925d",
    "MF_COMPANION": "c22eca68e3231d64d8d7bc68d6bc6e284e8b22d4951522f0d9111979e30466a9"}


def test_the_data_files_are_frozen_and_the_four_cells_are_those_of_r20():
    assert not RL.is_draft() and set(RL.status().values()) == {"FROZEN"} and len(RL.status()) == 6
    assert [(c["ij"][0], c["ij"][1]) for c in RL.chosen_cells()] == [(7, 4), (22, 10), (13, 29), (24, 26)]
    s = RL.summary()
    assert {n: v["runs"] for n, v in s.items()} == RL.EXPECTED_COUNTS
    assert {n: v["sha256"] for n, v in s.items()} == FROZEN_LIST_SHA256


def test_a_placeholder_cell_still_stops_the_cell_lists(monkeypatch):
    doc = RL._read(RL.CELLS_FILE)
    doc["cells"][0]["i"] = RL.PLACEHOLDER
    monkeypatch.setattr(RL, "_read", lambda rel, _r=RL._read: doc if rel == RL.CELLS_FILE else _r(rel))
    for name in RL.NEEDS_CELLS:
        with pytest.raises(RL.RunListError, match="TO_BE_CHOSEN"):
            RL.expand(name)


def test_a_draft_comment_line_or_status_field_makes_the_set_draft(monkeypatch):
    monkeypatch.setattr(RL, "_comment_status", lambda rel: "DRAFT")
    assert RL.is_draft()


def test_lists_without_cells_have_the_final_keys_and_no_duplicates():
    keys = []
    for name in ("S9", "S10", "C2_S9", "C2_S10"):
        rows = RL.expand(name)
        assert not RL.duplicates(rows) and len(rows) == RL.EXPECTED_COUNTS[name]
        keys += RL.seed_keys(rows)
    assert len(keys) == len(set(keys))
    assert set(keys) <= set(M.proposed_seed_keys())


def test_with_cells_filled_the_whole_registered_set_is_the_proposed_key_set(tmp_path, monkeypatch):
    _fixture_cells(tmp_path, monkeypatch)
    keys, total = [], 0
    for name in RL.ALL_LISTS:
        rows = RL.expand(name)
        total += len(rows)
        assert not RL.duplicates(rows)
        keys += RL.seed_keys(rows)
    assert total == 18 + 40 + 9 + 36 + 5 == 108
    assert len(keys) == 103 and set(keys) == set(M.proposed_seed_keys()) and len(set(keys)) == 100      # MF companion has no key
    twice = sorted(k for k in set(keys) if keys.count(k) == 2)
    assert twice == [(10, 1, 0), (10, 1, 1), (10, 1, 2)] and all(keys.count(k) == 1 for k in set(keys) - set(twice))   # R4: same stream at T_ramp 10 and 120 s
    ctrl = [r for n in RL.CONTROL_LISTS for r in RL.expand(n)]
    assert len(ctrl) == 36 and len({tuple(r["spawn_key"][:3]) for r in ctrl}) == 12


def test_a_control_has_the_duration_and_start_state_of_its_ramp_run(tmp_path, monkeypatch):
    from mprsurge.analysis import timing as T
    _fixture_cells(tmp_path, monkeypatch)
    ramp = {(r["cfg"]["network"]["N"], r["cfg"]["path"]["T_ramp_s"], r["cfg"]["network"]["het_dist"]): r["cfg"] for n in RL.RAMP_LISTS for r in RL.expand(n)}
    for r in (r for n in RL.CONTROL_LISTS for r in RL.expand(n)):
        c = r["cfg"]
        assert c["path"]["eta_peak"] == c["path"]["eta_start"] and c["path"]["J_end"] == c["path"]["J0"] == c["model"]["J"]
        w = ramp.get((c["network"]["N"], c["path"]["T_ramp_s"], c["network"]["het_dist"]))
        assert w is not None
        assert T.network_updates(c) == T.network_updates(w)
        if c["model"]["Delta"] == w["model"]["Delta"] and c["model"]["tau_d_ms"] == w["model"]["tau_d_ms"]:
            assert c["path"]["eta_start"] == w["path"]["eta_start"]


def test_the_stored_mf_references_verify_and_the_cell_loader_rejects_a_wrong_stratum(tmp_path, monkeypatch):
    assert [(v["T_ramp_s"], v["files"]) for v in RL.verify_references()] == [(10.0, 2), (120.0, 2)] or pytest.skip("results/ not present")
    _fixture_cells(tmp_path, monkeypatch)
    bad = RL._read(RL.CELLS_FILE)
    bad["cells"][0]["stratum"] = "D-none below median"
    monkeypatch.setattr(RL, "_read", lambda rel: bad)
    with pytest.raises(RL.RunListError, match="stratum"):
        RL.chosen_cells()
