"""8f: RB3, RB5, RB6 status numbers and the G6 inputs from the stored A7 table (plan Table 7.2, Table 11.2 G6; DL-181 to DL-185).

Analysis only: it reads results/A7/a7_ramp_metrics.parquet (stored data, no integration, no figure) and returns a dict. Every bound,
grid value and ladder is read from the frozen criteria (blob of the tag criteria-frozen, gate checked first); none is typed here.
It makes no G6 statement. Where the frozen file does not state a rule, every available reading is computed side by side and carries
the label UNVERIFIED; nothing here chooses between them. Two onsets are carried everywhere: "class" (the classifier episode onset,
column delay_eta, the A7 delay column) and "cross" (the raw first envelope crossing, column delay_eta_cross).

8f2 (DL-186): the reviewer's rulings are applied as labelled primary readings ("primary" keys, RULINGS_8F2); every other reading stays beside
them, labelled. No stored number changes. Rulings are clarifications of rules the frozen file does not state, not changes of a criterion.

Statuses: MEETS / DOES NOT MEET are against a bound the frozen file states; REPORTED where the frozen file asks for a report only;
NOT JUDGED where the frozen file says so; UNDETERMINED where the bound exists but a rule needed to apply it is not in the frozen file.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .. import criteria as CR

ONSETS = {"class": "delay_eta", "cross": "delay_eta_cross"}
ONSET_TIME = {"class": "onset_s", "cross": "onset_cross_s"}
FAMILIES_DET = ("p1_linear", "p1_sigmoid", "p2_linear", "p2_sigmoid", "p5_linear", "p5_sigmoid")
SURGE_MODE_D = ("D-tr",)
SURGE_MODE_N = ("S+", "S-rel", "S-abs")
PRIMARY_ONSET = "cross"        # ruling 1: raw first crossing of 0.1 x A_ref is the primary onset for RB3(b) and RB6 delays

RULINGS_8F2 = {
    "1": "RB3(b) and RB6 delays: the raw first-crossing onset (envelope first reaching 0.1 x A_ref) is primary (A7 defines the onset to compare as the time the amplitude reaches 0.1 x A_ref; RB3(a) names the threshold-crossing onset). The classifier-onset reading is kept, labelled, with its verdict. The paper reports both.",
    "2": "RB3(a): judge the testable in-range runs only; all must be within one A4 step (the plan gives no fraction). For runs where eta is constant at t_pred: time errors in seconds, no verdict.",
    "3": "P1 linear start distance 0.5 has 5 in-range T_ramp against the frozen statement '0 to 2 of 13' (that statement was reasoned at start distance 1.5).",
    "4": "RB6 DOP853 vs Radau: the frozen text is applied literally (a difference above 1 ms is a miss). Diagnosis first; any amendment is a new departure the user must agree.",
    "5": "RB3(c): the gating input is the headline path (P2 linear, noise-free) at 56.23, 100, 177.8, 316.2 s against the headline class. Readings A and B stay beside it as information.",
    "6": "RB3(d) and RB5: reported per path and per T_ramp. No pooled verdict.",
    "7": "RB6 Heun exact 0 is a limit of the 1 ms output grid, not extra evidence.",
    "8": "Floor-run delays are signed (negative = onset advance). The sign is kept everywhere.",
}


def frozen_values(root=None):
    """Bounds and grids from the frozen criteria (gate first)."""
    crit, info = CR.load_frozen_criteria(root)
    rb, d = crit["robustness"], crit["d43_and_numerics"]
    v = lambda x: x["value"]
    return {
        "criteria_sha256": info["sha256"],
        "grid_step": float(v(d["a4_eta_bar_grid_step"])), "a_onset_tol_text": v(rb["RB3"]["a_onset_tol"]),
        "c_T_ramp_s": [float(x) for x in v(rb["RB3"]["c_T_ramp_s"])],
        "d_T_ramp_s": [float(x) for x in v(rb["RB3"]["d_T_ramp_compared"])],
        "d_max_changes": int(v(rb["RB3"]["d_profile_max_class_changes"])),
        "delta0_ladder": [float(x) for x in v(rb["RB5"]["delta0_ladder"])],
        "start_distances": [float(x) for x in v(rb["RB5"]["start_distances"])],
        "rb6_max": float(v(rb["RB6"]["heun_delay_change_max"])), "dt_ladder": [float(x) for x in v(rb["RB6"]["heun_dt_ladder_tau"])],
        "dt_default": float(v(rb["RB6"]["heun_default_dt_tau"])), "solver_onset_ms": float(v(rb["RB6"]["solvers_agree_onset_ms"])),
        "rtol_ladder": [float(x) for x in v(rb["RB6"]["rtol_ladder"])],
        "floor_levels": [float(x) for x in v(d["sigma_floor_levels"])],
        "coverage_text": v(rb["RB3"]["a_range_reported_coverage"]),
    }


def _num(x):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else float(x)


def _near(series, value, rtol=2e-3):
    return np.isclose(series.astype(float), value, rtol=rtol, atol=0.0)


def at_T(df, T):
    return df[_near(df["T_ramp_s"], T)]


def _cls_at(df, family, T):
    r = at_T(df[df.family == family], T)
    return None if r.empty else str(r.iloc[0]["cls"])


# ---- medians ------------------------------------------------------------------------------------------------------
def median_pair(values):
    """(exclude, propagate, n_missing): the median of the finite values, the median with NaN propagated, and the NaN count."""
    a = np.asarray(values, dtype=float)
    miss = int(np.isnan(a).sum())
    exc = float(np.median(a[~np.isnan(a)])) if miss < a.size else float("nan")
    return exc, (float("nan") if miss else float(np.median(a))), miss


def strictly_decreasing(xs):
    xs = list(xs)
    if any(x is None or (isinstance(x, float) and math.isnan(x)) for x in xs):
        return None
    return bool(all(b < a for a, b in zip(xs, xs[1:])))


# ---- RB3(a) -------------------------------------------------------------------------------------------------------
def rb3a(df, fv):
    det = df[(df.list == "S5") & (df["mode"] == "D")]
    ir = det[det.in_range == True]            # noqa: E712 (pandas boolean)
    runs = []
    for _, r in ir.sort_values(["path", "profile", "start_distance", "T_ramp_s"]).iterrows():
        runs.append({
            "family": r.family, "path": r.path, "profile": r.profile, "start_distance": float(r.start_distance), "T_ramp_s": float(r.T_ramp_s),
            "class": r.cls, "eta_pred": _num(r.eta_pred), "eta_onset_cross": _num(r.eta_onset_cross), "eta_onset_class": _num(r.eta_onset),
            "match_err_steps_cross": _num(r.match_err_steps), "match_err_steps_class": _num(r.match_err_steps_cls),
            "eta_const_at_t_pred": bool(r.eta_const_at_t_pred), "within_one_step_cross": bool(r.match_err_steps <= 1.0),
            "eta_err_cross_signed": None if pd.isna(r.eta_onset_cross) else float(r.eta_onset_cross - r.eta_pred),
            "time_err_cross_s_signed": _num(r.onset_cross_minus_t_pred_s), "t_pred_s": _num(r.t_pred_s), "onset_cross_s": _num(r.onset_cross_s),
            "within_one_step_class": None if pd.isna(r.match_err_steps_cls) else bool(r.match_err_steps_cls <= 1.0)})
    testable = [x for x in runs if not x["eta_const_at_t_pred"]]
    grp = {}
    for x in runs:
        grp.setdefault((x["path"], x["profile"], x["start_distance"]), []).append(x["T_ramp_s"])
    primary = {"ruling": "2", "judged": "the testable in-range runs, onset = raw first crossing, tolerance one A4 grid step, all must be within",
               "n_judged": len(testable), "n_within_one_step": sum(x["within_one_step_cross"] for x in testable),
               "status": "MEETS" if all(x["within_one_step_cross"] for x in testable) else "DOES NOT MEET",
               "constant_eta_runs_no_verdict": [{"family": x["family"], "T_ramp_s": x["T_ramp_s"], "start_distance": x["start_distance"],
                                                 "time_err_cross_s_signed": x["time_err_cross_s_signed"], "eta_err_cross_signed": x["eta_err_cross_signed"],
                                                 "verdict": None} for x in runs if x["eta_const_at_t_pred"]]}
    allgrp = det.groupby(["path", "profile", "start_distance"]).size()
    coverage = []
    for (p, pr, sd), n_total in allgrp.items():
        n_in = len(grp.get((p, pr, float(sd)), []))
        coverage.append({"path": p, "profile": pr, "start_distance": float(sd), "n_T_ramp_runs": int(n_total), "n_in_range": n_in,
                         "in_range_T_ramp_s": sorted(grp.get((p, pr, float(sd)), [])), "above_2": n_in > 2})
    head = det[det.family == "S5ramp"].iloc[0]
    return {
        "n_in_range": len(runs), "primary": primary, "runs": runs,
        "tolerance_steps": 1.0, "tolerance_source": f"frozen RB3.a_onset_tol: {fv['a_onset_tol_text']}; A4 grid step {fv['grid_step']}",
        "n_testable": len(testable), "n_eta_const_trivial": len(runs) - len(testable),
        "pass_counts": {
            "testable_only_cross": [sum(x["within_one_step_cross"] for x in testable), len(testable)],
            "all_in_range_cross": [sum(x["within_one_step_cross"] for x in runs), len(runs)],
            "testable_only_class_where_onset_exists": [sum(bool(x["within_one_step_class"]) for x in testable if x["within_one_step_class"] is not None),
                                                       sum(x["within_one_step_class"] is not None for x in testable)],
            "all_in_range_class_where_onset_exists": [sum(bool(x["within_one_step_class"]) for x in runs if x["within_one_step_class"] is not None),
                                                      sum(x["within_one_step_class"] is not None for x in runs)]},
        "n_without_class_onset": sum(x["match_err_steps_class"] is None for x in runs),
        "coverage_by_path_profile_start_distance": coverage,
        "coverage_frozen_statement": fv["coverage_text"], "groups_above_2": [c for c in coverage if c["above_2"]],
        "headline": {"in_range": bool(head.in_range), "match_err_steps": _num(head.match_err_steps), "I_min": _num(head.I_min),
                     "status": "NOT JUDGED (frozen gate departure 3; rb3a_not_judged_at_headline)"},
        "s13_floor_runs_in_range": int((df[df.family.str.startswith("floor_")].in_range == True).sum()),  # noqa: E712
        "s5_noise_runs": {"n": int((df.family == "p2_noise").sum()), "in_range_na": int(df[df.family == "p2_noise"].in_range.isna().sum()),
                          "reason": "no_D43_floor_sigma_calibrated (ruling: no RB3(a) floor for S5 noise runs)"},
    }


# ---- RB3(b) and RB6 -----------------------------------------------------------------------------------------------
def floor_table(df, fv):
    """{(level, rung): {onset: delays by seed}} from the S13 floor runs; seeds sorted."""
    fl = df[df.family.str.startswith("floor_")]
    out = {}
    for lv in range(len(fv["floor_levels"])):
        for dt in fv["dt_ladder"]:
            sub = fl[(fl.d43_level == lv) & np.isclose(fl.heun_dt_tau, dt, rtol=1e-9)].sort_values("seed")
            out[(lv, dt)] = {k: sub[c].to_numpy(dtype=float) for k, c in ONSETS.items()} | {"seed": sub.seed.to_numpy(dtype=float),
                                                                                              "cls": list(sub.cls)}
    return out


def rb3b(df, fv):
    ft = floor_table(df, fv)
    res = {"rule": "frozen RB3.b_form: strict_decrease_of_median_delay_over_the_three_floor_levels (F-15), 10 seeds per level; "
                   "each level's median strictly lower than the one before; ties fail",
           "UNVERIFIED_alternatives": {
               "heun_rung": "the frozen file does not say which rung enters: all four are computed",
               "nan_in_median": "exclude = median of the seeds with an onset (the RB6 reading of the frozen file, with the count); propagate = a "
                                "seed without an onset makes the level median undefined"},
           "by_onset": {}}
    for on in ONSETS:
        per_rung = {}
        for dt in fv["dt_ladder"]:
            lv_rows = []
            for lv in range(len(fv["floor_levels"])):
                x = ft[(lv, dt)][on]
                e, p, miss = median_pair(x)
                lv_rows.append({"level": lv, "sigma_floor": fv["floor_levels"][lv], "n_seeds": int(x.size), "n_missing": miss,
                                "median_exclude": e, "median_propagate": p,
                                "min": float(np.nanmin(x)), "max": float(np.nanmax(x))})
            per_rung[repr(dt)] = {"levels": lv_rows,
                                  "strictly_decreasing_exclude": strictly_decreasing([r["median_exclude"] for r in lv_rows]),
                                  "strictly_decreasing_propagate": strictly_decreasing([r["median_propagate"] for r in lv_rows])}
        res["by_onset"][on] = per_rung
        vs = {per_rung[k]["strictly_decreasing_exclude"] for k in per_rung} | {per_rung[k]["strictly_decreasing_propagate"] for k in per_rung}
        res["by_onset"][on]["_verdicts_seen"] = sorted(str(s) for s in vs)
    res["status_by_onset"] = {on: _status_b(res["by_onset"][on]) for on in ONSETS}
    res["verdict_flips_between_onsets"] = res["status_by_onset"]["class"] != res["status_by_onset"]["cross"]
    res["primary"] = {"ruling": "1", "onset": PRIMARY_ONSET, "status": res["status_by_onset"][PRIMARY_ONSET],
                      "secondary": {"onset": "class", "status": res["status_by_onset"]["class"], "label": "classifier-onset reading, reported with its verdict"},
                      "delay_sign": "signed, negative = onset advance (ruling 8)"}
    return res


def _status_b(per_rung):
    rungs = [k for k in per_rung if not k.startswith("_")]
    vals = {per_rung[k]["strictly_decreasing_exclude"] for k in rungs} | {per_rung[k]["strictly_decreasing_propagate"] for k in rungs}
    return "MEETS" if vals == {True} else "DOES NOT MEET" if vals == {False} else "UNDETERMINED (readings differ)"


def rb6_heun(df, fv):
    ft = floor_table(df, fv)
    fine, dflt = min(fv["dt_ladder"]), fv["dt_default"]
    out = {"rule": "frozen RB6.statistic: |median(1e-4) - median(1e-3)| / median(1e-3) < heun_delay_change_max, same 10 seeds, per floor level "
                   "(which level is 'the headline floor' is not stated: all three are reported; UNVERIFIED)",
           "bound": fv["rb6_max"], "by_onset": {}}
    for on in ONSETS:
        rows = []
        for lv in range(len(fv["floor_levels"])):
            a, b = ft[(lv, dflt)][on], ft[(lv, fine)][on]
            ok = ~np.isnan(a) & ~np.isnan(b)
            e_a, p_a, m_a = median_pair(a)
            e_b, p_b, m_b = median_pair(b)
            rel_e = abs(e_b - e_a) / abs(e_a) if e_a else float("inf")
            rel_signed = (abs(e_b - e_a) / e_a) if e_a else float("inf")
            rel_same = (abs(median_pair(b[ok])[0] - median_pair(a[ok])[0]) / abs(median_pair(a[ok])[0])) if ok.any() and median_pair(a[ok])[0] else float("inf")
            per_seed = np.abs(b - a)
            rows.append({"level": lv, "sigma_floor": fv["floor_levels"][lv], "median_default": e_a, "median_finest": e_b,
                         "n_missing_default": m_a, "n_missing_finest": m_b, "rel_change": rel_e, "rel_change_signed_denominator": rel_signed,
                         "rel_change_same_seeds_only": rel_same, "propagate_defined": bool(not math.isnan(p_a) and not math.isnan(p_b)),
                         "max_abs_per_seed_difference_eta": float(np.nanmax(per_seed)), "n_seeds_identical_to_float": int((per_seed == 0).sum()),
                         "status": "MEETS" if rel_e < fv["rb6_max"] else "DOES NOT MEET"})
        out["by_onset"][on] = rows
    out["intermediate_rungs_rel_change_vs_default"] = {}
    for on in ONSETS:
        rr = {}
        for dt in fv["dt_ladder"][1:]:
            rr[repr(dt)] = [abs(median_pair(ft[(lv, dt)][on])[0] - median_pair(ft[(lv, dflt)][on])[0]) /
                            abs(median_pair(ft[(lv, dflt)][on])[0]) for lv in range(len(fv["floor_levels"]))]
        out["intermediate_rungs_rel_change_vs_default"][on] = rr
    out["status_by_onset"] = {on: ("MEETS" if all(r["status"] == "MEETS" for r in out["by_onset"][on]) else "DOES NOT MEET") for on in ONSETS}
    out["verdict_flips_between_onsets"] = out["status_by_onset"]["class"] != out["status_by_onset"]["cross"]
    out["primary"] = {"ruling": "1", "onset": PRIMARY_ONSET, "status": out["status_by_onset"][PRIMARY_ONSET],
                      "secondary": {"onset": "class", "status": out["status_by_onset"]["class"], "label": "classifier-onset reading"},
                      "note_ruling_7": "an exact 0 relative change is a limit of the 1 ms output grid, not extra evidence; see the resolution check (rb_diag)",
                      "delay_sign": "signed, negative = onset advance (ruling 8); rel_change uses |median_default| as denominator"}
    return out


def rb6_solvers(df, fv):
    h = df[df.family == "S5ramp"].iloc[0]
    rd = df[df.family == "radau"].iloc[0]
    rt = df[df.family == "rtol"].sort_values("rtol")
    ms = lambda c: (float(rd[c]) - float(h[c])) * 1000.0
    rtol_rows = [{"rtol": float(h.rtol), "cls": h.cls, "onset_s": float(h.onset_s), "onset_cross_s": float(h.onset_cross_s),
                  "delay_eta": float(h.delay_eta), "delay_eta_cross": float(h.delay_eta_cross), "source": "S5ramp headline"}]
    for _, r in rt.iterrows():
        rtol_rows.append({"rtol": float(r.rtol), "cls": r.cls, "onset_s": float(r.onset_s), "onset_cross_s": float(r.onset_cross_s),
                          "delay_eta": float(r.delay_eta), "delay_eta_cross": float(r.delay_eta_cross), "source": "S13 rtol"})
    rtol_rows.sort(key=lambda x: x["rtol"])
    r10 = next(x for x in rtol_rows if x["rtol"] == 1e-10)
    r12 = next(x for x in rtol_rows if x["rtol"] == 1e-12)
    out = {
        "rtol_ladder": rtol_rows,
        "rtol_1e-10_vs_1e-12": {"status": "REPORTED (not a pass test)", "delay_eta_difference": r12["delay_eta"] - r10["delay_eta"],
                                "delay_eta_cross_difference": r12["delay_eta_cross"] - r10["delay_eta_cross"],
                                "onset_difference_ms": (r12["onset_s"] - r10["onset_s"]) * 1000.0},
        "dop853_vs_radau": {"dop853_headline_cls": h.cls, "radau_cls": rd.cls, "class_agree": bool(h.cls == rd.cls),
                            "onset_class_dop853_s": float(h.onset_s), "onset_class_radau_s": float(rd.onset_s),
                            "onset_cross_dop853_s": float(h.onset_cross_s), "onset_cross_radau_s": float(rd.onset_cross_s),
                            "onset_diff_ms_class": ms("onset_s"), "onset_diff_ms_cross": ms("onset_cross_s"), "bound_ms": fv["solver_onset_ms"],
                            "delay_eta_dop853": float(h.delay_eta), "delay_eta_radau": float(rd.delay_eta),
                            "output_sample_interval_ms": 1.0},
    }
    d = out["dop853_vs_radau"]
    d["ruling_4"] = "frozen text applied literally: a difference above the bound is DOES NOT MEET; diagnosis in rb_diag; any amendment is a new departure for the user"
    d["status"] = ("MEETS" if d["class_agree"] and abs(d["onset_diff_ms_class"]) <= fv["solver_onset_ms"] and abs(d["onset_diff_ms_cross"]) <= fv["solver_onset_ms"]
                   else "DOES NOT MEET")
    return out


# ---- RB3(c), RB3(d) -----------------------------------------------------------------------------------------------
def rb3c(df, fv):
    head = df[df.family == "S5ramp"].iloc[0].cls
    res = {"rule": "frozen RB3.c_holds_means: same class as the headline (F-18); T_ramp 56.23, 100, 177.8, 316.2 s",
           "headline_class": head, "headline_family": "P2 linear 120 s, mode D, delta0 1e-6, DOP853 rtol 1e-10 (S5ramp)",
           "UNVERIFIED_alternatives": {
               "A_headline_all_paths": "every path and profile compared with the P2 linear headline class (literal frozen wording)",
               "B_self_consistent": "the four classes of one path and profile equal each other (the headline exists only on P2 linear)",
               "C_headline_path_only": "only P2 linear compared with the headline; P1, P2 sigmoid and P5 not judged"},
           "by_family": {}}
    for fam in FAMILIES_DET:
        cl = [_cls_at(df, fam, T) for T in fv["c_T_ramp_s"]]
        res["by_family"][fam] = {"T_ramp_s": fv["c_T_ramp_s"], "classes": cl, "A_all_equal_headline": bool(all(c == head for c in cl)),
                                 "B_all_four_equal": bool(len(set(cl)) == 1), "n_equal_headline": int(sum(c == head for c in cl))}
    res["C_P2_linear"] = res["by_family"]["p2_linear"]["A_all_equal_headline"]
    pl = res["by_family"]["p2_linear"]
    res["primary"] = {"ruling": "5", "gating_input": "P2 linear, noise-free (the headline path) at the four T_ramp against the headline class",
                      "T_ramp_s": pl["T_ramp_s"], "classes": pl["classes"], "n_equal_headline": pl["n_equal_headline"],
                      "status": "MEETS" if pl["A_all_equal_headline"] else "DOES NOT MEET", "A_and_B_below": "information only"}
    res["summary"] = {"A": {f: v["A_all_equal_headline"] for f, v in res["by_family"].items()},
                      "B": {f: v["B_all_four_equal"] for f, v in res["by_family"].items()}, "C": res["C_P2_linear"]}
    noise = {}
    for T in fv["c_T_ramp_s"]:
        r = at_T(df[df.family == "p2_noise"], T)
        noise[repr(T)] = dict(r.cls.value_counts().sort_index())
    res["mode_N_P2_linear_10_seeds_class_counts"] = {k: {a: int(b) for a, b in v.items()} for k, v in noise.items()}
    return res


def rb3d(df, fv):
    res = {"rule": "frozen RB3.d_profile_max_class_changes: linear vs sigmoid changes class at <= 1 of the four T_ramp (F-18); reported, not gated "
                   "(Table 11.2 G6)", "bound": fv["d_max_changes"],
           "UNVERIFIED": "how the three paths aggregate (per path, sum over paths, or P2 only) is not in the frozen file; per-path counts are given",
           "by_path": {}}
    for p, (lin, sig) in {"P1": ("p1_linear", "p1_sigmoid"), "P2": ("p2_linear", "p2_sigmoid"), "P5": ("p5_linear", "p5_sigmoid")}.items():
        cl_l = [_cls_at(df, lin, T) for T in fv["d_T_ramp_s"]]
        cl_s = [_cls_at(df, sig, T) for T in fv["d_T_ramp_s"]]
        n = sum(a != b for a, b in zip(cl_l, cl_s))
        res["by_path"][p] = {"T_ramp_s": fv["d_T_ramp_s"], "linear": cl_l, "sigmoid": cl_s, "n_class_changes": int(n), "within_bound": bool(n <= fv["d_max_changes"]),
                             "changed_at_T_ramp_s": [T for T, a, b in zip(fv["d_T_ramp_s"], cl_l, cl_s) if a != b]}
    res["status"] = "REPORTED per path and per T_ramp (ruling 6); no pooled verdict, no sum over paths"
    return res


# ---- RB5 ----------------------------------------------------------------------------------------------------------
def rb5(df, fv):
    h = df[df.family == "S5ramp"].iloc[0]
    d0 = {1e-6: h}
    for _, r in df[df.family == "delta0"].iterrows():
        d0[float(r.delta0)] = r
    rows = []
    for d in fv["delta0_ladder"]:
        r = next(v for k, v in d0.items() if math.isclose(k, d, rel_tol=1e-9))
        rows.append({"delta0": d, "cls": r.cls, "onset_s": _num(r.onset_s), "onset_cross_s": _num(r.onset_cross_s), "delay_eta": _num(r.delay_eta),
                     "delay_eta_cross": _num(r.delay_eta_cross)})
    base = rows[1]
    for r in rows:
        r["delay_eta_shift_vs_1e-6"] = None if r["delay_eta"] is None else r["delay_eta"] - base["delay_eta"]
        r["delay_eta_cross_shift_vs_1e-6"] = None if r["delay_eta_cross"] is None else r["delay_eta_cross"] - base["delay_eta_cross"]
    delta = {"ladder": rows, "class_unchanged": bool(len({r["cls"] for r in rows}) == 1), "status": None}
    delta["status"] = "MEETS" if delta["class_unchanged"] else "DOES NOT MEET"
    p1 = df[(df.path == "P1") & (df.profile == "linear") & (df.family.isin(["p1_linear", "p1_start_distance"]))]
    sd_rows = []
    for T in sorted(p1.T_ramp_s.unique()):
        cell = {"T_ramp_s": float(T), "by_start_distance": {}}
        sub = p1[_near(p1.T_ramp_s, T)]
        for sd in fv["start_distances"]:
            r = sub[np.isclose(sub.start_distance, sd, atol=1e-9)].iloc[0]
            cell["by_start_distance"][repr(sd)] = {"cls": r.cls, "delay_eta": _num(r.delay_eta), "delay_eta_cross": _num(r.delay_eta_cross)}
        cl = [v["cls"] for v in cell["by_start_distance"].values()]
        cell["class_unchanged"] = bool(len(set(cl)) == 1)
        base = cell["by_start_distance"]["1.5"]
        for v in cell["by_start_distance"].values():
            v["delay_eta_cross_shift_vs_1.5"] = None if v["delay_eta_cross"] is None or base["delay_eta_cross"] is None else v["delay_eta_cross"] - base["delay_eta_cross"]
        sd_rows.append(cell)
    sd = {"rows": sd_rows, "n_T_ramp": len(sd_rows), "n_class_changes": int(sum(not c["class_unchanged"] for c in sd_rows)),
          "T_ramp_with_change_s": [c["T_ramp_s"] for c in sd_rows if not c["class_unchanged"]],
          "UNVERIFIED": "how the 13 T_ramp aggregate into 'class unchanged' is not in the frozen file: per-T_ramp results are given",
          "status": "REPORTED per T_ramp (ruling 6); no pooled verdict"}
    return {"ruling": "6", "rule": "frozen RB5.criterion: class unchanged; delay shifts reported (G6 reports it, does not gate it)", "delta0_headline": delta,
            "start_distance_P1_linear": sd}


# ---- step 6: P2 surge-class counts --------------------------------------------------------------------------------
def p2_surge_counts(df, fv):
    lo, hi = min(fv["c_T_ramp_s"]), max(fv["c_T_ramp_s"])
    out = {"window_s": [lo, hi], "surge_classes": {"mode D": list(SURGE_MODE_D), "mode N": list(SURGE_MODE_N)}, "rows": {}}
    for tag, fam, surge in (("mode D, P2 linear", "p2_linear", SURGE_MODE_D), ("mode D, P2 sigmoid", "p2_sigmoid", SURGE_MODE_D),
                            ("mode N, P2 linear (10 seeds)", "p2_noise", SURGE_MODE_N)):
        sub = df[df.family == fam]
        per = []
        for T in sorted(sub.T_ramp_s.unique()):
            c = at_T(sub, T)
            vc = {k: int(v) for k, v in c.cls.value_counts().sort_index().items()}
            per.append({"T_ramp_s": float(T), "in_window": bool(lo * (1 - 2e-3) <= T <= hi * (1 + 2e-3)), "n": int(len(c)), "classes": vc,
                        "n_surge": int(c.cls.isin(surge).sum())})
        out["rows"][tag] = {"per_T_ramp": per,
                            "n_surge_inside_window": sum(r["n_surge"] for r in per if r["in_window"]), "n_runs_inside_window": sum(r["n"] for r in per if r["in_window"]),
                            "n_surge_outside_window": sum(r["n_surge"] for r in per if not r["in_window"]), "n_runs_outside_window": sum(r["n"] for r in per if not r["in_window"]),
                            "T_ramp_with_no_surge_run": [r["T_ramp_s"] for r in per if r["n_surge"] == 0]}
    return out


def no_t_pred(df):
    """Reason split of the runs with no t_pred (the evaluator itself is re-run in the driver, see run_rb_eval)."""
    n = df[df.t_pred_s.isna()]
    g = n.groupby(["family", "path", "profile", "T_ramp_s"]).size().reset_index(name="n")
    return {"n": int(len(n)), "by_path_profile": {f"{a}/{b}": int(c) for (a, b), c in n.groupby(["path", "profile"]).size().items()},
            "by_family_path_profile_T_ramp": g.to_dict("records"), "re_final_values": sorted({round(float(x), 6) for x in n.re_final})}


def no_t_pred_split(df, fi, records):
    """Reason code of every run with no t_pred, from a re-evaluation of the stored path (eigenvalues only, no integration):
    'integral_never_reaches_threshold' (finite along the path, max of I below ln(threshold/delta0), re_final <= 0 so the analytic
    extension does not reach it either), 'evaluator_failure' (exception or non-finite lambda or I), 'other'.
    records: {run_id: json path}. Grouped by family, path, profile and T_ramp."""
    import json
    from . import a7
    from . import entry_exit as EE
    out, cache = [], {}
    for _, r in df[df.t_pred_s.isna()].iterrows():
        cfg = json.loads(records[r.run_id].read_text(encoding="utf-8"))["config"]
        key = (r.path, r.profile, round(float(r.T_ramp_s), 9))
        if key not in cache:
            try:
                _, t, re, I = EE.path_gain(cfg, fi["grid_step"])
                cache[key] = (bool(np.isfinite(re).all() and np.isfinite(I).all()), float(np.max(I)), float(re[-1]), None)
            except Exception as exc:          # noqa: BLE001 (any evaluator failure is a finding, not an error)
                cache[key] = (False, float("nan"), float("nan"), f"{type(exc).__name__}: {exc}"[:120])
        finite, imax, refin, err = cache[key]
        need = math.log(fi["threshold"] / float(r.delta0))
        if err or not finite:
            reason = "evaluator_failure"
        elif imax < need and refin <= 0.0:
            reason = "integral_never_reaches_threshold"
        else:
            reason = "other"
        out.append({"family": r.family, "path": r.path, "profile": r.profile, "T_ramp_s": float(r.T_ramp_s), "reason": reason,
                    "I_max": imax, "ln_threshold_over_delta0": need, "re_final": refin, "error": err})
    o = pd.DataFrame(out)
    return {"n": len(o), "reason_counts": {k: int(v) for k, v in o.reason.value_counts().items()},
            "by_reason_path_profile": {f"{a}|{b}/{c}": int(n) for (a, b, c), n in o.groupby(["reason", "path", "profile"]).size().items()},
            "by_reason_path_profile_T_ramp": [{"reason": a, "path": b, "profile": c, "T_ramp_s": d, "n": int(len(g)), "I_max": float(g.I_max.iloc[0]),
                                               "ln_threshold_over_delta0": float(g.ln_threshold_over_delta0.iloc[0]), "re_final": float(g.re_final.iloc[0])}
                                              for (a, b, c, d), g in o.groupby(["reason", "path", "profile", "T_ramp_s"])]}


def evaluate(df, fv):
    return {"rulings_8f2": RULINGS_8F2, "frozen_inputs": fv, "no_t_pred": no_t_pred(df), "RB3a": rb3a(df, fv), "RB3b": rb3b(df, fv), "RB3c": rb3c(df, fv), "RB3d": rb3d(df, fv),
            "RB5": rb5(df, fv), "RB6_heun": rb6_heun(df, fv), "RB6_solvers": rb6_solvers(df, fv), "P2_surge_class_counts": p2_surge_counts(df, fv)}
