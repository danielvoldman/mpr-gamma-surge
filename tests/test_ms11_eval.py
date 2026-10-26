"""MS11 11c evaluators on SYNTHETIC fixtures only (DL-345 to DL-364). No MS11 record and no stored map series is read here."""
import copy
import csv
import json
from pathlib import Path

import numpy as np
import pytest
import yaml

from mprsurge import config as C
from mprsurge.analysis import a8_sensitivity as A8
from mprsurge.analysis import ms11_eval as E
from mprsurge.analysis import ms11_eval_choices as EC
from mprsurge.analysis import surge_metrics as M

ROOT = Path(__file__).resolve().parents[1]
FILE = EC.load_file()
CH = FILE["choices"]
CRIT = yaml.safe_load((ROOT / "configs/robustness_criteria.yaml").read_text(encoding="utf-8"))
FR = E.frozen_leaves(CRIT)


# --- frozen leaves, comparison rule (ruling 5) ------------------------------------------------------------------------

def test_frozen_leaves_are_the_plan_numbers_and_the_variant_list_equals_the_a8_list():
    assert (FR["rb2_k"], FR["rb2_n"]) == (8, 10)
    assert FR["net_fpk_max"] == 0.02 and FR["rb9a_tol"] == 0.005 and FR["rb9c_max"] == 0.05 and FR["rb10_max"] == 0.10 and FR["heun_max"] == 0.05
    v = FR["rb10_variations"]
    names = {f"band_{int(v['band_hz'][0])}_{int(v['band_hz'][1])}"} | {f"factors_{x:g}" for x in v["factors"]} | {f"amin_{x:g}" for x in v["amin_factor"]} \
        | {f"window_x{x:g}" for x in v["window_multiplier"]} | {f"cycles_{x}" for x in v["min_cycles"]}
    assert names == set(A8.VARIANTS) - {"V0"}


def test_boundary_case_1_within_is_inclusive_rb9a_value_equal_to_the_bound_passes():
    assert E.compare(0.005, "within", 0.005) and E.compare(0.004999, "within", 0.005) and not E.compare(0.005001, "within", 0.005)
    r = E.rb9a({"max_rel_diff": 0.005, "per_tau": {"10": {"max": 0.005}}}, FR, CH)
    assert r["status"] == E.PASS
    assert E.rb9a({"max_rel_diff": 0.0051}, FR, CH)["status"] == E.FAIL
    assert E.rb9a(None, FR, CH)["status"] == E.NE


def test_boundary_case_2_within_one_over_W_is_inclusive_rb9b():
    fs, W = 1000.0, 2.0
    t = np.arange(int(20 * fs)) / fs
    v = np.sin(2 * np.pi * 40.0 * t)
    f_cycle = E.cycle_frequency_hz(v, fs, 4.0, 16.0)
    assert f_cycle == pytest.approx(40.0, abs=0.05)
    ep = {"onset_s": 4.0, "end_s": 16.0, "f_pk_hz": f_cycle + 1.0 / W}              # difference exactly 1/W
    r = E.rb9b_row(v, fs, ep, W, CH)
    assert r["status"] == E.PASS and r["within"] is True
    ep2 = {**ep, "f_pk_hz": f_cycle + 1.0 / W + 0.01}
    assert E.rb9b_row(v, fs, ep2, W, CH)["status"] == E.FAIL
    assert E.rb9b_row(v, fs, None, W, CH)["status"] == E.NE


def test_boundary_case_3_strict_less_than_equality_fails_rb6_network_2_percent():
    assert not E.compare(0.02, "<", 0.02) and E.compare(0.0199, "<", 0.02) and not E.compare(0.02, ">", 0.02) and E.compare(0.02, ">=", 0.02)
    recs = {}
    for s, f2 in ((0, 51.0), (1, 50.5)):                                              # |51 - 50| / 50 = 0.02 exactly; 0.01
        recs[(100.0, 1e-3, s)] = _net_rec(50.0)
        recs[(100.0, 5e-4, s)] = _net_rec(f2)
    out = E.rb6_network(recs, FR, _ch(psd=False))
    rows = {r["seed"]: r for r in out["per_reading"]["classifier_episode_fpk"]["rows"]}
    assert rows[0]["status"] == E.FAIL and rows[0]["rel"] == pytest.approx(0.02) and rows[1]["status"] == E.PASS
    assert out["per_reading"]["classifier_episode_fpk"]["status"] == E.FAIL


def test_rb2_at_least_is_inclusive_8_of_10_passes_7_of_10_fails():
    def runs(kept, sigma, failed=0, T=120.0):
        out = [{"sigma_factor": sigma, "T_ramp_s": T, "seed": s, "class": "S-rel", "status": "ok"} for s in range(kept)]
        out += [{"sigma_factor": sigma, "T_ramp_s": T, "seed": kept + i, "class": M.FAILED, "status": "failed"} for i in range(failed)]
        out += [{"sigma_factor": sigma, "T_ramp_s": T, "seed": kept + failed + i, "class": "NS", "status": "ok"} for i in range(10 - kept - failed)]
        return out
    ok = E.rb2_s11(runs(8, 0.5) + runs(9, 1.0), [], FR, CH)
    assert ok["status"] == E.PASS
    bad = E.rb2_s11(runs(8, 0.5) + runs(7, 1.0), [], FR, CH)
    assert bad["status"] == E.FAIL and [g["status"] for g in bad["gate"]] == [E.PASS, E.FAIL]


# --- ruling 1: failed runs count as not kept, the denominator stays 10, the failures are reported -------------------------------

def test_failed_run_counts_as_not_kept_with_denominator_ten_and_is_reported():
    base = [{"sigma_factor": 0.5, "T_ramp_s": 120.0, "seed": s, "class": "S+", "status": "ok"} for s in range(8)]
    two_failed = base + [{"sigma_factor": 0.5, "T_ramp_s": 120.0, "seed": s, "class": M.FAILED, "status": "failed"} for s in (8, 9)]
    one_failed = base[:7] + [{"sigma_factor": 0.5, "T_ramp_s": 120.0, "seed": 7, "class": M.FAILED, "status": "failed"}] + [
        {"sigma_factor": 0.5, "T_ramp_s": 120.0, "seed": s, "class": "NS", "status": "ok"} for s in (8, 9)]
    sig1 = [{"sigma_factor": 1.0, "T_ramp_s": 120.0, "seed": s, "class": "S+", "status": "ok"} for s in range(10)]
    r = E.rb2_s11(two_failed + sig1, [], FR, CH)
    g = r["gate"][0]
    assert (g["kept"], g["failed"], g["denominator"], g["status"]) == (8, 2, 10, E.PASS) and r["failed_runs_total_gate_cells"] == 2
    r2 = E.rb2_s11(one_failed + sig1, [], FR, CH)
    assert (r2["gate"][0]["kept"], r2["gate"][0]["failed"], r2["gate"][0]["status"]) == (7, 1, E.FAIL)


def test_missing_record_makes_the_cell_not_evaluable_and_is_not_replaced():
    runs = [{"sigma_factor": 0.5, "T_ramp_s": 120.0, "seed": s, "class": "S+", "status": "ok"} for s in range(9)] + [
        {"sigma_factor": 0.5, "T_ramp_s": 120.0, "seed": 9, "missing": True}]
    sig1 = [{"sigma_factor": 1.0, "T_ramp_s": 120.0, "seed": s, "class": "S+", "status": "ok"} for s in range(10)]
    r = E.rb2_s11(runs + sig1, [], FR, CH)
    assert r["gate"][0]["status"] == E.NE and r["status"] == E.NE


def test_rb2_beside_gate_is_labelled_and_controls_are_post_hoc():
    runs = [{"sigma_factor": f, "T_ramp_s": T, "seed": s, "class": "S-rel", "status": "ok"} for f in (0.5, 1.0, 2.0) for T in (10.0, 30.0, 120.0, 300.0) for s in range(10)]
    ctrl = [{"sigma_factor": f, "T_ramp_s": 120.0, "seed": s, "class": "S-rel", "status": "ok"} for f in (0.5, 1.0, 2.0) for s in range(10)]
    r = E.rb2_s11(runs, ctrl, FR, CH, subgrid_logged=CH["rb2_subgrid"])
    two = [b for b in r["beside"] if b["sigma_factor"] == 2.0 and b["T_ramp_s"] == 120.0][0]
    assert "post hoc" in two["label"] and "sigma checked, not confirmed" in two["label"]
    assert all("short_window_limit" in b for b in r["beside"] if b["T_ramp_s"] in (10.0, 30.0))
    assert all("POST-HOC AMENDMENT" in c["label"] for c in r["controls"]) and len(r["controls"]) == 3
    assert [b["kept_S_plus_only"] for b in r["beside"]][0] == 0 and r["subgrid_carried_in"]["cells_agree"] == 97


# --- ruling 3: network f_pk, seed without an episode ------------------------------------------------------------------------------------

def _net_rec(f_pk, onset=20.0, end=30.0, v=None, no_episode=False):
    r = {"class": "NS" if no_episode else "S-rel", "f_pk_hz": float("nan") if no_episode else f_pk, "onset_s": float("nan") if no_episode else onset,
         "end_s": float("nan") if no_episode else end, "fs": 1000.0, "W_s": 1.0, "step_s": 0.5, "status": "ok"}
    if v is not None:
        r["v"] = v
    return r


def _ch(psd=True):
    ch = copy.deepcopy(CH)
    if not psd:
        ch["rb6_network_fpk_sources"] = ["classifier_episode_fpk"]
    return ch


def test_seed_without_an_episode_is_not_evaluable_listed_by_seed_and_neither_passes_nor_fails():
    recs = {}
    for s in range(3):
        recs[(100.0, 1e-3, s)] = _net_rec(50.0, no_episode=(s == 1))
        recs[(100.0, 5e-4, s)] = _net_rec(50.2)
    out = E.rb6_network(recs, FR, CH)
    pr = out["per_reading"]["classifier_episode_fpk"]
    assert pr["not_evaluable_seeds"] == [1] and pr["n_pass"] == 2 and pr["n_fail"] == 0 and pr["status"] == E.PASS
    row1 = [r for r in pr["rows"] if r["seed"] == 1][0]
    assert row1["status"] == E.NE and "no episode" in row1["reason"]


def test_all_seeds_without_an_episode_gives_not_evaluable_not_pass():
    recs = {(100.0, dt, s): _net_rec(50.0, no_episode=True) for s in range(3) for dt in (1e-3, 5e-4)}
    out = E.rb6_network(recs, FR, CH)
    assert out["status"] == E.NE and out["n_evaluated"] == 0


def test_dt_that_creates_or_removes_an_episode_is_reported_as_a_class_change():
    recs = {(100.0, 1e-3, 0): _net_rec(50.0), (100.0, 5e-4, 0): _net_rec(50.0, no_episode=True),            # removed
            (100.0, 1e-3, 1): _net_rec(50.0, no_episode=True), (100.0, 5e-4, 1): _net_rec(50.0),            # created
            (100.0, 1e-3, 2): _net_rec(50.0), (100.0, 5e-4, 2): _net_rec(50.1)}
    pr = E.rb6_network(recs, FR, _ch(psd=False))["per_reading"]["classifier_episode_fpk"]
    assert dict(pr["class_changes"]) == {0: "episode removed", 1: "episode created"}
    assert [r["status"] for r in pr["rows"]] == [E.NE, E.NE, E.PASS] and pr["status"] == E.PASS


def test_vp_comparison_and_other_rungs_are_information_not_tests():
    recs = {}
    for s in range(3):
        for vp, dt, f in ((100.0, 1e-3, 50.0), (100.0, 5e-4, 50.1), (100.0, 2.5e-4, 70.0), (100.0, 1e-4, 50.0), (200.0, 1e-3, 90.0), (200.0, 1e-4, 50.0)):
            recs[(vp, dt, s)] = _net_rec(f)
    out = E.rb6_network(recs, FR, _ch(psd=False))
    assert out["status"] == E.PASS and out["per_reading"]["classifier_episode_fpk"]["n_fail"] == 0            # the 70 Hz rung and the 90 Hz V_p 200 run do not fail the test
    assert all(r["status"] == E.REPORTED for r in out["vp_info"]) and "REPORTED ONLY" in out["vp_label"]
    assert any(r.get("rel", 0) > 0.02 for r in out["ladder_info"])
    assert out["class_claim"].startswith("none")


def test_psd_argmax_fpk_reads_the_peak_inside_the_episode_window_with_resolution_one_over_W():
    fs = 1000.0
    t = np.arange(int(40 * fs)) / fs
    v = np.sin(2 * np.pi * 40.0 * t) + 0.05 * np.random.default_rng(1).standard_normal(t.size)
    f = E.psd_argmax_fpk(v, fs, 1.0, 0.5, (10.0, 30.0))
    assert abs(f - 40.0) <= 1.0 and f == round(f)                              # bin spacing 1 / W = 1 Hz
    assert E.psd_argmax_fpk(v, fs, 1.0, 0.5, (100.0, 120.0)) is None
    recs = {(100.0, 1e-3, 0): _net_rec(40.0, v=v), (100.0, 5e-4, 0): _net_rec(40.0, v=v)}
    out = E.rb6_network(recs, FR, CH)
    assert out["per_reading"]["psd_argmax"]["status"] == E.PASS and out["status"] == E.PASS


# --- ruling 10: excluded cells, worst case, "depends on exclusions" ----------------------------------------------------------------------

def _rows(n_unchanged, n_changed, n_excluded, set_="map1"):
    r = [{"id": f"u{i}", "set": set_, "baseline": "D-tr", "variant": "D-tr", "status": "unchanged", "category_changed": False} for i in range(n_unchanged)]
    r += [{"id": f"c{i}", "set": set_, "baseline": "D-tr", "variant": "D-none", "status": "changed", "category_changed": True} for i in range(n_changed)]
    r += [{"id": f"x{i}", "set": set_, "baseline": "D-tr", "variant": "not_run", "status": "excluded", "category_changed": None} for i in range(n_excluded)]
    return r


def test_exclusions_that_change_the_verdict_are_flagged_depends_on_exclusions():
    res = E.change_fraction(_rows(86, 4, 10), FR["rb9c_max"], CH)             # 4 of 90 = 4.4 percent PASS; worst case 14 of 100 = 14 percent FAIL
    assert res["status"] == E.PASS and res["worst_status"] == E.FAIL and res["flag"] == "depends on exclusions"
    assert (res["n_evaluated"], res["n_excluded"], res["n_changed"]) == (90, 10, 4)
    assert res["fraction"] == pytest.approx(4 / 90) and res["worst_fraction"] == pytest.approx(14 / 100)
    assert "4 of 90 evaluated cells (10 excluded)" == res["denominator_statement"]


def test_exclusions_that_do_not_change_the_verdict_carry_no_flag_and_equality_is_at_most():
    res = E.change_fraction(_rows(95, 5, 0), 0.05, CH)                            # exactly 5 percent: "at most" is inclusive
    assert res["status"] == E.PASS and res["flag"] == ""
    res2 = E.change_fraction(_rows(90, 6, 0), 0.05, CH)
    assert res2["status"] == E.FAIL and res2["flag"] == ""
    assert E.change_fraction(_rows(0, 0, 5), 0.05, CH)["status"] == E.NE


def test_reclassify_excludes_not_run_and_counts_changes_with_a_fake_classifier():
    cells = [{"id": f"c{i}", "set": "map1", "mode": "D", "t_on": 5.0, "T_ramp_s": 120.0, "a_ref": 1.0, "baseline_class": "D-tr", "v": np.zeros(10)} for i in range(6)]
    cells[5]["baseline_class"] = "not_run"

    def fake(v, mode, t_on, T, a_ref, variant, inside_a4_region=None):
        return {"cls": {"band_30_120": "D-none"}.get(variant, "D-tr")} if variant != "window_x2" else {"cls": "not_run"}
    rows = E.reclassify(cells, "band_30_120", fake)
    assert [r["status"] for r in rows] == ["changed"] * 5 + ["excluded"]
    assert all(r["status"] == "excluded" for r in E.reclassify(cells, "window_x2", fake))
    assert [r["status"] for r in E.reclassify(cells, "cycles_5", fake)] == ["unchanged"] * 5 + ["excluded"]


def test_gate_cell_set_map1_carries_the_verdict_and_map2_and_subgrid_are_reported_beside():
    cells = []
    for s, n_bad in (("map1", 0), ("map2", 5), ("subgrid", 5)):
        for i in range(10):
            cells.append({"id": f"{s}{i}", "set": s, "mode": "D", "t_on": 5.0, "T_ramp_s": 120.0, "a_ref": 1.0, "baseline_class": "D-tr", "v": np.zeros(4), "bad": i < n_bad})
    bad = {c["id"] for c in cells if c["bad"]}
    ids = {id(c["v"]): c["id"] for c in cells}

    def classify(v, mode, t_on, T, a_ref, variant, inside_a4_region=None):
        return {"cls": "D-none" if variant == "band_30_120" and ids[id(v)] in bad else "D-tr"}
    tab = E.variant_table(cells, ["band_30_120"], classify, FR["rb9c_max"], CH)
    t = tab["band_30_120"]
    assert t["map1"]["status"] == E.PASS and t["map2"]["status"] == E.REPORTED and t["map2"]["status_if_gated"] == E.FAIL and t["subgrid"]["status"] == E.REPORTED
    c = E.rb9c(tab, CH)
    assert c["status"] == E.PASS and set(c["beside"]) == {"map2", "subgrid"}
    ch2 = copy.deepcopy(CH)
    ch2["gate_cell_set"] = "pooled_map1_map2"
    with pytest.raises(EC.MissingChoice):
        E.variant_table(cells, ["band_30_120"], classify, 0.05, ch2)


def test_rb10_needs_headline_unchanged_under_every_variant_and_the_map1_bound():
    def tab(frac_bad):
        return {v: {"map1": E.change_fraction(_rows(100 - frac_bad, frac_bad, 0), FR["rb10_max"], CH)} for v in A8.VARIANTS if v != "V0"}
    head_ok = {v: {"baseline": "D-tr", "variant_class": "D-tr"} for v in tab(0)}
    assert E.rb10(head_ok, tab(10), FR, CH)["status"] == E.PASS                                 # 10 percent: at most, inclusive
    assert E.rb10(head_ok, tab(11), FR, CH)["status"] == E.FAIL
    head_bad = {**head_ok, "cycles_20": {"baseline": "D-tr", "variant_class": "D-sus"}}
    r = E.rb10(head_bad, tab(0), FR, CH)
    assert r["status"] == E.FAIL and r["variants"]["cycles_20"]["headline"] == E.FAIL
    head_nr = {**head_ok, "window_x2": {"baseline": "D-tr", "variant_class": "not_run"}}
    r2 = E.rb10(head_nr, tab(0), FR, CH)
    assert r2["status"] == E.NE and set(r2["window_line_of_s13"]) == {"window_x0.5", "window_x2"}


def test_rb9b_headline_gates_and_map_cells_are_reported_as_a_fraction_only():
    fs, W = 1000.0, 2.0
    t = np.arange(int(20 * fs)) / fs
    v = np.sin(2 * np.pi * 40.0 * t)
    fc = E.cycle_frequency_hz(v, fs, 4.0, 16.0)
    head = {"v": v, "fs": fs, "W_s": W, "episode": {"onset_s": 4.0, "end_s": 16.0, "f_pk_hz": fc}}
    cells = [{"set": "map1", "v": v, "fs": fs, "W_s": W, "episode": {"onset_s": 4.0, "end_s": 16.0, "f_pk_hz": fc + d}} for d in (0.0, 0.2, 3.0)]
    cells.append({"set": "map1", "v": v, "fs": fs, "W_s": W, "episode": None})
    cells.append({"set": "map2", "v": None, "fs": fs, "W_s": W, "episode": {"onset_s": 1, "end_s": 2, "f_pk_hz": 40.0}})
    out = E.rb9b(head, cells, CH)
    assert out["status"] == E.PASS and out["cells_reported"]["map1"] == {"n": 3, "within": 2, "fraction": pytest.approx(2 / 3)} and "map2" not in out["cells_reported"]
    assert "no gate fraction" in out["cells_label"]


# --- ruling 11 and RB5 -------------------------------------------------------------------------------------------------------------------------

def test_floor_other_T_ramp_is_reported_only_in_the_rb3b_form():
    r = E.rb6_floor_other_T({"raw": {10.0: {0: [-0.001, -0.002], 1: [-0.04, -0.05], 2: [-0.1, -0.11]}, 316.2: {0: [-0.5, None], 1: [-0.5, -0.5], 2: [-0.6, -0.7]}}}, CH)
    assert r["status"] == E.REPORTED
    rows = {x["T_ramp_s"]: x for x in r["rows"]}
    assert rows[10.0]["direction"] == "strictly decreasing with floor level" and rows[10.0]["strict_decrease"]
    assert rows[316.2]["direction"] == "non-increasing with ties" and rows[316.2]["seeds_without_onset_by_level"][0] == 1
    assert "no scaling law" in r["label"] and "UNVERIFIED" in r["label"]


def test_rb5_delta0_class_unchanged_is_the_exact_label_and_delay_shift_is_reported():
    mk = lambda c, on: {"class": c, "onset_s": on, "delay_eta": on / 100}
    ok = E.rb5_delta0({10.0: {1e-9: mk("D-tr", 5.1), 1e-6: mk("D-tr", 5.0), 1e-3: mk("D-tr", 4.9)}}, CH)
    assert ok["status"] == E.PASS and ok["rows"][0]["onset_shift_s"] == pytest.approx(0.1)
    bad = E.rb5_delta0({10.0: {1e-9: mk("D-sus", 5.1), 1e-6: mk("D-tr", 5.0), 1e-3: mk("D-tr", 4.9)}}, CH)
    assert bad["status"] == E.FAIL
    assert E.rb5_delta0({10.0: {1e-9: None, 1e-6: mk("D-tr", 5.0)}}, CH)["rows"][0]["status"] == E.NE
    u = E.rb5_updown({1.0: "D-tr", 2.0: "D-none"}, "S4 note", CH)
    assert u["status"] == E.REPORTED and "no class" in u["s4_beside"]["label"]


# --- required fields: a null or absent field raises (ruling 14 and the 11b mechanism) ------------------------------------------------------------

def test_every_required_field_is_set_and_deleting_any_one_raises_missing_choice():
    assert EC.open_fields(CH) == [] and len(EC.check_all(CH)) == len(EC.REQUIRED)
    for name in EC.REQUIRED:
        ch = copy.deepcopy(CH)
        del ch[name]
        with pytest.raises(EC.MissingChoice):
            EC.choice(ch, name)
        with pytest.raises(EC.MissingChoice):
            EC.check_all(ch)
        ch2 = copy.deepcopy(CH)
        ch2[name] = None
        assert name in EC.open_fields(ch2)


@pytest.mark.parametrize("name,call", [
    ("rb2_failed_run_counts_as", lambda ch: E.rb2_s11([], [], FR, ch)),
    ("within_boundary", lambda ch: E.rb9a({"max_rel_diff": 0.0}, FR, ch)),
    ("rb9a_source", lambda ch: E.rb9a(None, FR, ch)),
    ("rb9b_comparison_window", lambda ch: E.rb9b_row(np.zeros(10), 1000.0, None, 1.0, ch)),
    ("rb9b_cells", lambda ch: E.rb9b({"v": np.zeros(10), "fs": 1000.0, "W_s": 1.0}, [], ch)),
    ("not_run_cells_count_as", lambda ch: E.change_fraction([], 0.05, ch)),
    ("gate_cell_set", lambda ch: E.rb9c({"band_30_120": {}}, ch)),
    ("s13_floor_other_T_ramp_form", lambda ch: E.rb6_floor_other_T({}, ch)),
    ("rb6_network_fpk_no_episode", lambda ch: E.rb6_network({}, FR, ch)),
    ("rb6_network_vp_comparison", lambda ch: E.rb6_network({}, FR, ch)),
    ("rb5_updown_source", lambda ch: E.rb5_updown({}, None, ch)),
    ("a11_logged_verdict_map", lambda ch: E.map_logged("PASS", ch)),
    ("a11_extra_columns", lambda ch: E.a11_columns(ch)),
])
def test_an_evaluator_raises_when_its_required_field_is_null(name, call):
    ch = copy.deepcopy(CH)
    ch[name] = None
    with pytest.raises(EC.MissingChoice):
        call(ch)
    del ch[name]
    with pytest.raises(EC.MissingChoice):
        call(ch)


# --- A11: verdict map, unmapped word, columns, failed checks kept ---------------------------------------------------------------------------------

def test_the_verdict_map_covers_the_users_words_and_every_logged_word_of_the_registry():
    m = E.verdict_map(CH)
    assert {m[w] for w in m} <= set(E.STATUS_WORDS)
    expect = {"PASS": "PASS", "FAIL": "FAIL", "DOES NOT MEET": "FAIL", "NOT EVALUABLE": "NOT EVALUABLE", "NOT INSIDE": "FAIL", "CONTINUE": "PASS", "NOT PASSED": "FAIL"}
    assert {w: m[w] for w in expect} == expect
    for e in FILE["a11_logged"]:
        assert E.map_logged(e["logged_verdict"], CH) in E.STATUS_WORDS


def test_an_unmapped_logged_word_raises():
    with pytest.raises(E.UnmappedVerdict):
        E.map_logged("PROBABLY FINE", CH)
    with pytest.raises(E.UnmappedVerdict):
        E.a11_row(CH, rb_id="RBX", check_id="c", source="s", label="pre-registered", logged_verdict="PROBABLY FINE")
    ch = copy.deepcopy(CH)
    ch["a11_logged_verdict_map"] = {**CH["a11_logged_verdict_map"], "ODD": "MAYBE"}
    with pytest.raises(E.UnmappedVerdict):
        E.verdict_map(ch)


def test_logged_words_are_verbatim_in_the_cited_documents():
    docs = "".join((ROOT / p).read_text(encoding="utf-8") for p in ("docs/decision_log.md", "docs/ms8_g6_evidence.md", "docs/ms8_close.md", "docs/ms9_close.md",
                                                                      "docs/ms10_results.md", "docs/ms10_close.md"))
    for e in FILE["a11_logged"]:
        assert e["logged_verdict"] in docs, e


def test_the_status_vocabulary_is_the_four_words_and_the_columns_are_the_ruled_ones():
    assert CH["a11_status_vocabulary"] == ["PASS", "FAIL", "NOT EVALUABLE", "REPORTED"] == list(E.STATUS_WORDS)
    cols = E.a11_columns(CH)
    assert cols[:4] == ["value", "threshold", "pass_or_fail", "input_commits"]
    assert {"rb_id", "check_id", "source", "logged_verdict", "recomputed_match", "n_evaluated", "label"} <= set(cols)


def test_assemble_rows_keeps_every_failed_check_with_the_logged_word_verbatim_and_does_not_drop_missing_evaluators(tmp_path):
    rows = E.assemble_rows({}, FILE["a11_logged"], FR, CH, input_commits="HEAD=x")
    by = {(r["rb_id"], r["check_id"]): r for r in rows}
    for key in (("RB1", "overall"), ("RB1", "headline_10s"), ("RB2", "noisy_subgrid_agreement"), ("RB6", "solver_onset_headline"), ("RB3", "b_classifier_onset")):
        assert by[key]["pass_or_fail"] == "FAIL" and by[key]["recomputed_match"] == "no"
    assert by[("RB2", "noisy_subgrid_agreement")]["logged_verdict"] == "FAILED"
    assert by[("RB8", "heterogeneity")]["pass_or_fail"] == "NOT EVALUABLE" and by[("RB8", "m4_adaptation")]["logged_verdict"] == "OPEN"
    ms11 = [r for r in rows if "evaluator output not supplied" in r["note"]]
    assert {r["rb_id"] for r in ms11} >= {"RB2", "RB5", "RB6", "RB9", "RB10"} and all(r["pass_or_fail"] == "NOT EVALUABLE" for r in ms11)
    assert all(r["pass_or_fail"] in E.STATUS_WORDS and r["label"] in ("pre-registered", "post hoc") for r in rows)
    E.write_a11_csv(rows, tmp_path / "a.csv", CH)
    got = list(csv.DictReader((tmp_path / "a.csv").open(encoding="utf-8")))
    assert len(got) == len(rows) and list(got[0]) == E.a11_columns(CH)


def test_assemble_rows_with_evaluator_outputs_and_a_matching_recompute_hook():
    runs = [{"sigma_factor": f, "T_ramp_s": 120.0, "seed": s, "class": "S+", "status": "ok"} for f in (0.5, 1.0) for s in range(10)]
    res = {"rb2": E.rb2_s11(runs, [], FR, CH), "recompute": {"RB4/parameter_perturbation": {"status": "PASS"}, "RB1/overall": {"status": "PASS"}}}
    rows = {(r["rb_id"], r["check_id"]): r for r in E.assemble_rows(res, FILE["a11_logged"], FR, CH)}
    assert rows[("RB4", "parameter_perturbation")]["recomputed_match"] == "yes"
    assert rows[("RB1", "overall")]["recomputed_match"] == "no" and rows[("RB1", "overall")]["pass_or_fail"] == "PASS" and rows[("RB1", "overall")]["logged_verdict"] == "FAIL"
    assert rows[("RB2", "headline_class_kept_0.5_sigma")]["pass_or_fail"] == "PASS" and rows[("RB2", "headline_class_kept_0.5_sigma")]["n_evaluated"] == 10


def test_ruled_values_of_the_fourteen_fields():
    assert CH["rb2_failed_run_counts_as"] == "not_kept" and CH["rb5_updown_source"] == "P5_with_S4_reported_beside" and CH["rb6_network_fpk_no_episode"] == "not_evaluable"
    assert CH["rb6_network_vp_comparison"] == "reported_only" and CH["within_boundary"] == "inclusive" and CH["rb9a_source"] == "unit_test_level"
    assert CH["rb9b_cells"] == "headline_gate_map_cells_reported" and CH["rb9b_comparison_window"] == "classifier_episode" and CH["gate_cell_set"] == "map1"
    assert CH["not_run_cells_count_as"] == "excluded_with_worst_case_flag" and CH["s13_floor_other_T_ramp_form"] == "rb3b_form_reported_only"
    assert CH["rb9d_runs"] == "separate_post_hoc_list"
    assert FILE["pending"]["rb9d_parameter_spec"]["status"] == "PENDING"


# --- readers on synthetic stored records -----------------------------------------------------------------------------------------------------------

def _write_record(tmp_path, name, v, dirty=False, status="ok", overrides=None):
    cfg = C.resolve_config(None, {"run.kind": "mf", **(overrides or {})})
    jp = tmp_path / f"{name}.json"
    jp.write_text(json.dumps({"name": name, "status": status, "config": cfg, "git": {"dirty": dirty, "commit": "abc"}, "dry_run": False}, default=str), encoding="utf-8")
    np.savez(jp.with_suffix(".npz"), v=v)
    return jp


def test_classify_stored_reads_a_synthetic_record_refuses_dirty_and_labels_failed(tmp_path):
    v = 1e-4 * np.random.default_rng(0).standard_normal(25000)
    fi = {"threshold": 0.2176, "a_ref": 2.176}
    out = E.classify_stored(_write_record(tmp_path, "ok", v), fi, with_v=True)
    assert out["class"] == "D-none" and out["mode"] == "D" and out["fs"] == 1000.0 and out["v"].shape == v.shape and out["missing"] is False
    with pytest.raises(E.EvalError):
        E.classify_stored(_write_record(tmp_path, "dirty", v, dirty=True), fi)
    failed = E.classify_stored(_write_record(tmp_path, "bad", v, status="failed"), fi)
    assert failed["class"] == M.FAILED


def test_collectors_build_the_evaluator_inputs_from_records():
    recs = [{"family": "S13_delta0", "T_ramp_s": 10.0, "delta0": 1e-9, "class": "D-tr"}, {"family": "S13_delta0", "T_ramp_s": 10.0, "delta0": 1e-3, "missing": True}]
    d = E.delta0_by_T(recs, {10.0: {"class": "D-tr"}})
    assert d[10.0][1e-6] == {"class": "D-tr"} and d[10.0][1e-9]["class"] == "D-tr" and d[10.0][1e-3] is None
    fl = [{"family": "S13_floor", "T_ramp_s": 10.0, "spawn_key": [11, 3, 0, l, s], "delay_eta_raw": -0.1 * l - s * 1e-3, "class": "D-tr"} for l in range(3) for s in range(2)]
    fb = E.floor_by_T(fl)
    assert sorted(fb[10.0]) == [0, 1, 2] and len(fb[10.0][1]) == 2
