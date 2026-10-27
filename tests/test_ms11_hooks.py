"""MS11 11d recompute hooks of the 26 carried checks (DL-369). SYNTHETIC fixtures only: no stored MS8, MS9 or MS10 record or table is read, and no hook is run on a real record."""
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from mprsurge.analysis import ms11_eval as E
from mprsurge.analysis import ms11_eval_choices as EC
from mprsurge.analysis import ms11_hooks as HK
from mprsurge.analysis import ms10_eval as E10
from mprsurge.analysis import rb_eval as RB
from test_ms10_eval import CH as CH10
from test_ms10_eval import FR as FR10
from test_ms10_eval import REF as REF10
from test_ms10_eval import _fake, _s10

ROOT = Path(__file__).resolve().parents[1]
FILE = EC.load_file()
CH = FILE["choices"]
LOGGED = FILE["a11_logged"]
CRIT = yaml.safe_load((ROOT / "configs/robustness_criteria.yaml").read_text(encoding="utf-8"))
HFR = HK.frozen_hook_leaves(CRIT)

FV = {"floor_levels": [1.59e-9, 1.59e-6, 1.59e-3], "dt_ladder": [1e-3, 5e-4, 2.5e-4, 1e-4], "dt_default": 1e-3, "rb6_max": 0.05, "c_T_ramp_s": [56.23, 100.0, 177.8, 316.2],
      "d_T_ramp_s": [56.23, 100.0, 177.8, 316.2], "d_max_changes": 1, "delta0_ladder": [1e-9, 1e-6, 1e-3], "start_distances": [0.5, 1.5, 3.0], "solver_onset_ms": 1.0,
      "grid_step": 0.025, "a_onset_tol_text": "one A4 grid step", "rtol_ladder": [1e-8, 1e-10, 1e-12], "coverage_text": "0 to 2 of 13", "criteria_sha256": "x"}


# --- the synthetic MS8 table (columns of the A7 table that rb_eval reads) ------------------------------------------------------------------------

def _row(**kw):
    d = {"list": "S5", "mode": "D", "family": "p2_linear", "path": "P2", "profile": "linear", "start_distance": 1.5, "T_ramp_s": 120.0, "cls": "D-tr", "rtol": 1e-10, "delta0": 1e-6,
         "onset_s": 58.698, "onset_cross_s": 58.698, "onset_cross_minus_t_pred_s": 0.0, "t_pred_s": 58.7, "delay_eta": 0.07, "delay_eta_cross": 0.07, "eta_pred": 2.95,
         "eta_onset_cross": 2.96, "eta_onset": 2.96, "match_err_steps": 0.4, "match_err_steps_cls": 0.4, "eta_const_at_t_pred": False, "in_range": False, "I_min": 0.0,
         "d43_level": float("nan"), "heun_dt_tau": float("nan"), "seed": float("nan")}
    d.update(kw)
    return d


def ms8_df(a_within=False, head_in_range=False, floor_cross=(-0.00076, -0.0423, -0.105), floor_class=(-1.5, -1.5, -1.09), radau_cls="D-tr", radau_dt_ms=181.0,
           rel_fine=1.0, delta0_cls="D-tr", c_cls="D-tr"):
    rows = [_row(family="S5ramp", in_range=head_in_range, match_err_steps=0.5 if head_in_range else 65.95, I_min=-1122.5)]
    rows.append(_row(family="radau", solver="Radau", cls=radau_cls, onset_s=58.698 + radau_dt_ms / 1000.0, onset_cross_s=58.698 + radau_dt_ms / 1000.0, delay_eta=0.0714))
    rows += [_row(family="rtol", rtol=r, cls="D-tr") for r in (1e-8, 1e-12)]
    rows += [_row(family="delta0", delta0=d, cls=delta0_cls if d != 1e-6 else "D-tr") for d in (1e-9, 1e-3)]
    for T in FV["c_T_ramp_s"]:                                                  # RB3(c)/(d), RB5 start distances, P1 linear in range
        for fam, path, prof in (("p1_linear", "P1", "linear"), ("p1_sigmoid", "P1", "sigmoid"), ("p2_linear", "P2", "linear"), ("p2_sigmoid", "P2", "sigmoid"),
                                ("p5_linear", "P5", "linear"), ("p5_sigmoid", "P5", "sigmoid")):
            cls = c_cls if fam == "p2_linear" else "D-tr"
            rows.append(_row(family=fam, path=path, profile=prof, T_ramp_s=T, cls=cls))
        for sd in (0.5, 3.0):
            rows.append(_row(family="p1_start_distance", path="P1", profile="linear", start_distance=sd, T_ramp_s=T, cls="D-sus"))
    for k, (T, steps) in enumerate(((56.23, 1.2), (100.0, 4.4), (177.8, 33.1))):               # in-range runs: three testable
        rows.append(_row(family="p1_linear", path="P1", profile="linear", T_ramp_s=T, in_range=True, match_err_steps=0.5 if a_within else steps, cls="D-sus"))
    rows.append(_row(family="p1_linear", path="P1", profile="linear", T_ramp_s=316.2, in_range=True, eta_const_at_t_pred=True, match_err_steps=0.0, cls="D-sus"))
    for lv in range(3):
        for dt in FV["dt_ladder"]:
            for s in range(10):
                f = rel_fine if dt == 1e-4 else 1.0
                rows.append(_row(family=f"floor_l{lv}", d43_level=float(lv), heun_dt_tau=dt, seed=float(s), delay_eta=floor_class[lv] * f, delay_eta_cross=floor_cross[lv] * f, cls="S-abs"))
    rows.append(_row(family="p2_noise", mode="N", cls="S-rel", in_range=float("nan")))
    return pd.DataFrame(rows)


# --- the synthetic MS9 tables ------------------------------------------------------------------------------------------------------------

def s16_rows(oat_changed=0, lhs_changed=0):
    rows = [{"run": f"oat{k}", "group": "oat", "class": "D-none" if k < oat_changed else "D-tr", "status": "ok"} for k in range(14)]
    rows += [{"run": f"lhs{k}", "group": "lhs", "class": "D-none" if k < lhs_changed else "D-tr", "status": "ok"} for k in range(64)]
    return rows


def subgrid(n_agree=97, n_cells=225, tie_cells=0):
    out = []
    for c in range(n_cells):
        det = "D-tr"
        if c < n_agree:
            cl = ["S+"] * 10
        elif c < n_agree + tie_cells:
            cl = ["S+"] * 5 + ["NS"] * 5                  # a 5/5 tie counts as disagreement
        else:
            cl = ["NS"] * 10
        out += [{"i": c // 15, "j": c % 15, "seed": s, "class": k, "det": det} for s, k in enumerate(cl)]
    return out


def nc1(net_class="S+", supp_class="S-rel"):
    rows = [{"family": "NC1", "class": "D-none", "supplementary": False, "status": "ok"} for _ in range(13)]
    rows += [{"family": "NC1_cells", "class": "D-none", "supplementary": False, "status": "ok"} for _ in range(5)]
    rows += [{"family": "NC1_net", "class": net_class, "supplementary": False, "status": "ok"}]
    rows += [{"family": "NC1_supp", "class": supp_class, "supplementary": True, "status": "ok"} for _ in range(6)]
    return rows


class Ctx(HK.Context):
    """A synthetic context; every accessor returns the fixture handed to the constructor."""

    def __init__(self, **kw):
        self.d = {"ms8": {"df": ms8_df(), "fv": FV}, "s16": {"rows": s16_rows(), "nominal_class": "D-tr"}, "subgrid": subgrid(), "map1": ["D-tr"] * 760 + ["D-none"] * 140,
                  "nc1": nc1(), "ms10": ms10_logged_like(), "frozen": HFR}
        self.d.update(kw)

    def ms8(self): return self.d["ms8"]
    def s16(self): return self.d["s16"]
    def subgrid(self): return self.d["subgrid"]
    def map1_classes(self): return self.d["map1"]
    def nc1(self): return self.d["nc1"]
    def ms10(self): return self.d["ms10"]
    def frozen(self): return self.d["frozen"]


def ms10_logged_like(headline_ok=False, cells_agree=1, n_ok=True, sigma=0.0450, lorentzian=("S+", "S-sus", "S+")):
    """The real ms10_eval functions run on fake per-run dicts (the 10d fixtures), shaped like the logged MS10 outcome: RB1 headline FAIL, cells 1 of 4, N rule PASS, sigma NOT INSIDE, RB8 NOT EVALUABLE."""
    refs = {("head", 10.0): REF10, ("head", 120.0): REF10, ("head", 60.0): REF10, **{("cell", c): {"class": "D-tr", "onset_s": 20.0, "f_pk_hz": 50.0} for c in range(4)}}
    heads = [_fake("S+" if headline_ok else "NS", s, T_ramp=T, baseline_std_v=x, f=50.0 if headline_ok else float("nan"), on=20.0 if headline_ok else float("nan"))
             for T in (10.0, 120.0) for s, x in zip(range(3), (0.0385, 0.0388, 0.0391))]
    cells = [_fake("S+" if c < cells_agree else "NS", s, T_ramp=30.0, group=c) for c in range(4) for s in range(3)]
    n = 7 if n_ok else 6
    s9 = ([_fake("S+" if s < 7 else "NS", s, N=10000, f=50.5) for s in range(10)] + [_fake("S+" if s < n else "NS", s, N=30000, f=51.0) for s in range(10)]
          + [_fake("S+", s, N=1000) for s in range(10)] + [_fake("S+", s, N=3000) for s in range(10)])
    out = {"rb1_headline": E10.rb1_headline(heads, refs, [], CH10, FR10), "rb1_cells": E10.rb1_cells(cells, refs, [], {}, FR10), "N_sweep": E10.n_sweep(s9, REF10, [], CH10, FR10)}
    out["rb1"] = E10.rb1_overall(out["rb1_headline"], out["rb1_cells"], out["N_sweep"])
    out["sigma_check"] = E10.sigma_check(heads, dict(CH10, mf_baseline_std=sigma))
    out["rb8"] = E10.rb8(_s10(list(lorentzian), ["S+"] * 3, ["S+"] * 3), [], REF10, CH10, FR10)
    return out


def words(ctx):
    return {k: v["word"] for k, v in HK.run_hooks(ctx, CH).items()}


# --- the registry ----------------------------------------------------------------------------------------------------------------------

def test_there_are_26_hooks_one_per_carried_row_and_the_registry_check_passes():
    assert len(HK.HOOKS) == 26 == len(LOGGED)
    assert set(HK.HOOKS) == {f"{e['rb_id']}/{e['check_id']}" for e in LOGGED}
    HK.check_registry(LOGGED)
    with pytest.raises(HK.HookError, match="without a hook"):
        HK.check_registry(LOGGED[:-1])
    with pytest.raises(HK.HookError):
        HK.check_registry(LOGGED + [{"rb_id": "RB99", "check_id": "x"}])


def test_every_hook_names_its_origin_its_reads_and_what_it_shares_with_the_original_evaluation():
    for k, h in HK.HOOKS.items():
        assert h.origin in ("MS8", "MS9", "MS10", "frozen criteria") and h.reads and h.shares, k
        assert HK.SHARE_LOADER in h.shares, k                       # every hook reads the frozen thresholds through the criteria loader
    ms8 = [k for k, h in HK.HOOKS.items() if h.origin == "MS8"]
    ms9 = [k for k, h in HK.HOOKS.items() if h.origin == "MS9"]
    ms10 = [k for k, h in HK.HOOKS.items() if h.origin == "MS10"]
    assert (len(ms8), len(ms9), len(ms10)) == (14, 4, 7) and "RB8/m4_adaptation" not in ms8 + ms9 + ms10
    assert all(HK.SHARE_EVALUATOR in HK.HOOKS[k].shares for k in ms8)
    assert all(HK.SHARE_9I in HK.HOOKS[k].shares for k in ms10)
    assert not any(HK.SHARE_9I in HK.HOOKS[k].shares for k in ms8 + ms9)
    assert all(HK.SHARE_CLASSIFIER in HK.HOOKS[k].shares for k in ms8 + ms9 + ms10)


# --- MS8 hooks on the synthetic table ---------------------------------------------------------------------------------------------------

LOGGED_WORDS = {f"{e['rb_id']}/{e['check_id']}": e["logged_verdict"] for e in LOGGED}


def test_ms8_hooks_reproduce_the_logged_words_on_a_table_shaped_like_the_logged_outcome():
    w = words(Ctx())
    for k in HK.HOOKS:
        if k.startswith(("RB3/", "RB5/", "RB6/", "G6/")):
            assert w[k] == LOGGED_WORDS[k], (k, w[k], LOGGED_WORDS[k])


def test_ms8_hooks_change_when_the_stored_numbers_change():
    w = words(Ctx(ms8={"df": ms8_df(a_within=True, head_in_range=True, radau_dt_ms=0.5), "fv": FV}))
    assert w["RB3/a_inrange_runs"] == "MEETS" and w["RB3/a_headline"] == "MEETS" and w["RB6/solver_onset_headline"] == "MEETS"
    w = words(Ctx(ms8={"df": ms8_df(radau_cls="D-sus"), "fv": FV}))
    assert w["RB6/solver_class_headline"] == "DOES NOT MEET"
    w = words(Ctx(ms8={"df": ms8_df(rel_fine=1.2), "fv": FV}))
    assert w["RB6/heun_headline"] == "DOES NOT MEET"
    w = words(Ctx(ms8={"df": ms8_df(delta0_cls="D-none"), "fv": FV}))
    assert w["RB5/delta0_headline_class"] == "DOES NOT MEET"
    w = words(Ctx(ms8={"df": ms8_df(c_cls="D-none"), "fv": FV}))
    assert w["RB3/c_T_ramp_56_to_316"] == "DOES NOT MEET"
    w = words(Ctx(ms8={"df": ms8_df(floor_class=(-0.5, -1.0, -1.5)), "fv": FV}))
    assert w["RB3/b_classifier_onset"] == "MEETS"


def test_g6_is_passed_with_departures_only_while_every_failing_component_is_covered_by_a_logged_departure():
    assert words(Ctx())["G6/gate"] == "PASSED WITH DEPARTURES"
    clean = Ctx(ms8={"df": ms8_df(a_within=True, head_in_range=True, radau_dt_ms=0.5, floor_class=(-0.5, -1.0, -1.5)), "fv": FV})
    assert words(clean)["G6/gate"] == "PASSED"
    uncovered = Ctx(ms8={"df": ms8_df(radau_cls="D-sus"), "fv": FV})                     # solver class is not covered by any departure
    r = HK.run_hooks(uncovered, CH)["G6/gate"]
    assert r["word"] == "NOT PASSED" and r["status"] == "FAIL" and "RB6/solver_class_headline" in r["detail"]
    bad_heun = Ctx(ms8={"df": ms8_df(rel_fine=1.2), "fv": FV})
    assert words(bad_heun)["G6/gate"] == "NOT PASSED"


def test_the_g6_departure_register_matches_the_departures_named_in_the_yaml_row():
    g6 = next(e for e in LOGGED if e["rb_id"] == "G6")
    for k, dep in HK.G6_DEPARTURE_COVERS.items():
        assert dep in g6["departures"], (k, dep)
        assert k in HK.HOOKS


# --- MS9 hooks -------------------------------------------------------------------------------------------------------------------------

def test_ms9_hooks_reproduce_the_logged_words_on_tables_shaped_like_the_logged_outcome():
    w = words(Ctx())
    assert w["RB2/noisy_subgrid_agreement"] == "FAILED" and w["RB4/parameter_perturbation"] == "PASS" and w["G5/gate"] == "PASSED, continue" and w["G7/gate"] == "NOT PASSED"


def test_d24_subgrid_threshold_is_the_frozen_90_percent_with_ties_as_disagreement():
    r = HK.run_hooks(Ctx(subgrid=subgrid(n_agree=203)), CH)["RB2/noisy_subgrid_agreement"]
    assert r["word"] == "PASS" and "203 of 225" in r["detail"] and "203 needed" in r["detail"]
    assert words(Ctx(subgrid=subgrid(n_agree=202)))["RB2/noisy_subgrid_agreement"] == "FAILED"
    assert words(Ctx(subgrid=subgrid(n_agree=200, tie_cells=25)))["RB2/noisy_subgrid_agreement"] == "FAILED"         # 25 tie cells add no agreement


def test_rb4_counts_one_at_a_time_changes_and_hypercube_unchanged_from_the_frozen_leaves():
    assert words(Ctx(s16={"rows": s16_rows(oat_changed=2), "nominal_class": "D-tr"}))["RB4/parameter_perturbation"] == "PASS"
    assert words(Ctx(s16={"rows": s16_rows(oat_changed=3), "nominal_class": "D-tr"}))["RB4/parameter_perturbation"] == "FAIL"
    assert words(Ctx(s16={"rows": s16_rows(lhs_changed=12), "nominal_class": "D-tr"}))["RB4/parameter_perturbation"] == "PASS"       # 52 of 64 unchanged
    assert words(Ctx(s16={"rows": s16_rows(lhs_changed=13), "nominal_class": "D-tr"}))["RB4/parameter_perturbation"] == "FAIL"
    failed = s16_rows()
    failed[0]["status"] = "failed"
    failed[1]["status"] = "failed"
    failed[2]["status"] = "failed"
    assert words(Ctx(s16={"rows": failed, "nominal_class": "D-tr"}))["RB4/parameter_perturbation"] == "FAIL"                       # a failed run counts as changed
    assert words(Ctx(s16={"rows": s16_rows()[:-1], "nominal_class": "D-tr"}))["RB4/parameter_perturbation"] == "FAIL"               # 63 hypercube points: the design is incomplete


def test_g5_needs_3_percent_of_map1_cells_and_rb4():
    assert words(Ctx(map1=["D-tr"] * 27 + ["D-none"] * 873))["G5/gate"] == "PASSED, continue"
    assert words(Ctx(map1=["D-tr"] * 26 + ["D-none"] * 874))["G5/gate"] == "NOT PASSED"
    assert words(Ctx(s16={"rows": s16_rows(oat_changed=3), "nominal_class": "D-tr"}))["G5/gate"] == "NOT PASSED"


def test_g7_ignores_the_supplementary_runs_and_counts_the_network_run():
    assert words(Ctx(nc1=nc1(net_class="NS")))["G7/gate"] == "PASSED"                      # the supplementary S-rel runs feed no gate
    assert words(Ctx(nc1=nc1(net_class="S-abs")))["G7/gate"] == "NOT PASSED"
    mf = nc1(net_class="NS")
    mf[0]["class"] = "D-tr"
    assert words(Ctx(nc1=mf))["G7/gate"] == "NOT PASSED"
    assert words(Ctx(nc1=[]))["G7/gate"] == "NOT EVALUABLE"


# --- MS10 hooks and the frozen M4 leaf ------------------------------------------------------------------------------------------------------

def test_ms10_hooks_reproduce_the_logged_words_with_the_real_ms10_evaluators_on_fake_runs():
    w = words(Ctx())
    assert w["RB1/headline_10s"] == "FAIL" and w["RB1/headline_120s"] == "FAIL" and w["RB1/cells_30s"] == "FAIL" and w["RB1/n_rule_60s"] == "PASS" and w["RB1/overall"] == "FAIL"
    assert w["RB8/heterogeneity"] == "NOT EVALUABLE" and w["sigma_check/S8_baseline_std"] == "NOT INSIDE"


def test_ms10_hooks_follow_the_stored_evaluator_outputs():
    ok = words(Ctx(ms10=ms10_logged_like(headline_ok=True, cells_agree=4, sigma=0.0389, lorentzian=("S+", "S+", "S+"))))
    assert ok["RB1/headline_10s"] == "PASS" and ok["RB1/headline_120s"] == "PASS" and ok["RB1/cells_30s"] == "PASS" and ok["RB1/overall"] == "PASS"
    assert ok["sigma_check/S8_baseline_std"] == "PASS" and ok["RB8/heterogeneity"] == "PASS"
    bad_n = words(Ctx(ms10=ms10_logged_like(n_ok=False)))
    assert bad_n["RB1/n_rule_60s"] == "FAIL"


def test_an_incomplete_ms10_part_is_not_evaluable_with_the_word_kept_and_flagged():
    m = ms10_logged_like()
    m["rb1_cells"] = {**m["rb1_cells"], "verdict": "INCOMPLETE"}
    r = HK.run_hooks(Ctx(ms10=m), CH)["RB1/cells_30s"]
    assert r["word"] == "INCOMPLETE" and r["status"] == "NOT EVALUABLE" and "no entry in a11_logged_verdict_map" in r["detail"]


def test_the_m4_hook_reads_the_frozen_leaf_and_reports_open_while_it_has_no_value():
    assert HFR["rb8_m4_value"] is None and words(Ctx())["RB8/m4_adaptation"] == "OPEN"
    assert words(Ctx(frozen={**HFR, "rb8_m4_value": "written"}))["RB8/m4_adaptation"] == "NOT EVALUABLE"


def test_frozen_hook_leaves_come_from_the_frozen_file_not_from_typed_numbers():
    assert HFR["rb4_oat_max"] == 2 and HFR["rb4_oat_n"] == 14 and HFR["rb4_lhs_n"] == 64 and HFR["rb4_lhs_min_frac"] == 0.80
    assert HFR["g5_min_frac"] == 0.03 and HFR["rb2_subgrid_min"] == 0.90


# --- the hooks inside A11 ----------------------------------------------------------------------------------------------------------------

def test_a11_rows_carry_the_recomputed_word_the_match_flag_and_what_is_shared(tmp_path):
    rec = HK.run_hooks(Ctx(), CH)
    rows = E.assemble_rows({"recompute": rec}, LOGGED, E.frozen_leaves(CRIT), CH, input_commits="HEAD=x")
    assert len(rows) >= 26
    carried = [r for r in rows if f"{r['rb_id']}/{r['check_id']}" in HK.HOOKS]
    assert len(carried) == 26 and all(r["note"].startswith("recomputed from stored records") for r in carried)
    assert all("shares with the original" in r["note"] for r in carried)
    by = {(r["rb_id"], r["check_id"]): r for r in carried}
    assert all(r["recomputed_match"] == "yes" for r in carried), [k for k, r in by.items() if r["recomputed_match"] != "yes"]
    g6 = by[("G6", "gate")]
    assert g6["pass_or_fail"] == "PASS" and "G6-D1" in g6["note"] and "equals the logged word" in g6["note"]
    for key in (("RB1", "overall"), ("RB6", "solver_onset_headline"), ("RB2", "noisy_subgrid_agreement")):
        assert by[key]["pass_or_fail"] == "FAIL"                                          # failed checks stay FAIL


def test_a_difference_between_recomputed_and_logged_is_flagged_and_the_row_is_not_resolved():
    rec = HK.run_hooks(Ctx(subgrid=subgrid(n_agree=210)), CH)
    rows = E.assemble_rows({"recompute": rec}, LOGGED, E.frozen_leaves(CRIT), CH)
    r = next(x for x in rows if x["check_id"] == "noisy_subgrid_agreement")
    assert r["logged_verdict"] == "FAILED" and r["pass_or_fail"] == "PASS" and r["recomputed_match"] == "no" and "DIFFERS" in r["note"]


def test_a_hook_exception_propagates_and_nothing_is_skipped():
    class Broken(Ctx):
        def s16(self): raise RuntimeError("stored table unreadable")
    with pytest.raises(RuntimeError, match="unreadable"):
        HK.run_hooks(Broken(), CH)


def test_the_real_context_opens_nothing_on_construction(tmp_path):
    c = HK.RealContext(root=ROOT, results_root=tmp_path / "nothing_here")
    assert c.results_root == tmp_path / "nothing_here" and c._cache == {}
    assert c.res("results/ms9/9d/x.csv") == tmp_path / "nothing_here/ms9/9d/x.csv"
    with pytest.raises(FileNotFoundError):
        c.map1_classes()                                          # reading is lazy and fails loudly on a missing stored table
