"""MS11 evaluators (11c; docs/ms11_eval_rules.md, rulings DL-345 to DL-358): RB2 / S11 with the DL-251 controls, the open parts of RB5 and RB6, RB9 (a) to (d),
RB10 with the window x {0.5, 2} line of S13, and the A11 row builder.

Analysis only. Every function takes dicts or arrays of stored records and returns dicts; nothing integrates and nothing is plotted. Thresholds are read from the
frozen criteria (blob of the tag, `frozen_leaves`) and are never typed here; every evaluation choice is read with ms11_eval_choices.choice, so a null or absent
required field raises MissingChoice (nothing is defaulted). At 11c these functions are tested on synthetic fixtures only (tests/test_ms11_eval.py); they have not
been run on any MS11 record or on the stored map series.

Comparison rule (ruling 5, within_boundary): "within X" is inclusive (at most X); "<" and ">" are strict as the plan writes them; ">=" and "<=" are inclusive.
Status words of A11 (ruling 13): PASS, FAIL, NOT EVALUABLE, REPORTED.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np

from .. import config as C
from .. import criteria as CR
from . import ms11_eval_choices as EC
from . import surge_metrics as M

EPS = 1e-9
PASS, FAIL, NE, REPORTED = "PASS", "FAIL", "NOT EVALUABLE", "REPORTED"
STATUS_WORDS = (PASS, FAIL, NE, REPORTED)
SURGE_N = ("S+", "S-rel", "S-abs")
LABEL_SIGMA = "sigma checked, not confirmed (G4-C4)"
LABEL_PROVISIONAL = "provisional (D8 open, DL-137)"
LABEL_POSTHOC = "post hoc, feeds no gate"
LABEL_CONTROL = "POST-HOC AMENDMENT (DL-251)"
LABEL_RB9A_SCOPE = ("unit-level test: 1 s path_eta ramp (eta 1 to 4), tau 10 and 20 ms, not the headline path, no run record "
                    "(ruling 6, DL-351)")
LABEL_G4 = "G4-C1 to G4-C6 apply (network records)"


class EvalError(Exception):
    pass


class UnmappedVerdict(EvalError):
    """A logged verdict word has no entry in the a11_logged_verdict_map table of configs/ms11/ms11_eval.yaml."""


# --- frozen leaves, comparison rule ---------------------------------------------------------------------------------

def _frac(text) -> tuple[int, int]:
    m = re.search(r"(\d+)\s+of\s+(\d+)", str(text))
    if not m:
        raise EvalError(f"frozen criterion {text!r} is not of the form 'k of n'")
    return int(m.group(1)), int(m.group(2))


def frozen_leaves(crit: dict | None = None) -> dict:
    """The thresholds the MS11 evaluators use, read from the frozen criteria (crit is parsed from the tag's blob after the gate unless a dict is given for a test)."""
    sha = None
    if crit is None:
        crit, info = CR.load_frozen_criteria()
        sha = info["sha256"]
    R = crit["robustness"]
    k, n = _frac(R["RB2"]["headline_class_kept_min_seeds"]["value"])
    return {"criteria_sha256": sha, "rb2_k": k, "rb2_n": n, "rb2_sigma_factors": list(R["RB2"]["sigma_factors"]["value"]),
            "rb2_subgrid_min": float(R["RB2"]["noisy_subgrid_agreement_min"]["value"]),
            "heun_max": float(R["RB6"]["heun_delay_change_max"]["value"]), "solver_onset_ms": float(R["RB6"]["solvers_agree_onset_ms"]["value"]),
            "net_fpk_max": float(R["RB6"]["network_dt_f_pk_change_max"]["value"]), "net_dt": R["RB6"]["network_dt_for_f_pk_test"]["value"],
            "rb9a_tol": float(R["RB9"]["a_dimensional_vs_nondimensional_rel_tol"]["value"]),
            "rb9c_max": float(R["RB9"]["c_band_30_120_max_cell_class_change"]["value"]),
            "rb10_max": float(R["RB10"]["max_map_cell_class_change"]["value"]), "rb10_variations": R["RB10"]["variations"]["value"]}


def compare(x: float, op: str, bound: float) -> bool:
    """The plan's comparators (ruling 5). "within" and "<=" and ">=" are inclusive, "<" and ">" strict. NaN is False."""
    if x is None or not math.isfinite(float(x)):
        return False
    x = float(x)
    if op in ("within", "<="):
        return x <= bound + EPS
    if op == ">=":
        return x >= bound - EPS
    if op == "<":
        return x < bound - EPS
    if op == ">":
        return x > bound + EPS
    raise EvalError(f"unknown comparator {op!r}")


def _need(ch: dict, *names):
    """Read required fields (MissingChoice if one is null or absent) and return them."""
    out = [EC.choice(ch, n) for n in names]
    return out[0] if len(out) == 1 else out


def _fin(x) -> bool:
    return x is not None and math.isfinite(float(x))


def _med(xs):
    xs = [float(x) for x in xs if _fin(x)]
    return float(np.median(xs)) if xs else float("nan")


def verdict_of(n_pass: int, n_fail: int) -> str:
    return FAIL if n_fail > 0 else (PASS if n_pass > 0 else NE)


# --- RB2 / S11 (ruling 1; DL-336 2b) --------------------------------------------------------------------------------------

def _is_failed(r: dict) -> bool:
    return bool(r.get("missing")) or r.get("class") == M.FAILED or r.get("status", "ok") != "ok"


def rb2_s11(runs: list[dict], controls: list[dict], fr: dict, ch: dict, subgrid_logged: dict | None = None) -> dict:
    """RB2 on the S11 records. runs/controls: dicts with sigma_factor, T_ramp_s, seed, class (Table 2.1 mode N), status, missing.

    Gate: at the judged T_ramp, for each gated sigma factor, kept = the seed's class is in rb2_gate_class_set. A failed run counts as NOT kept and the denominator
    stays at the frozen n (rb2_failed_run_counts_as = not_kept, ruling 1); the number of failed runs is reported. A MISSING record makes that cell NOT EVALUABLE
    (never replaced). Pass: kept >= k of n (frozen, inclusive). Beside the gate (post hoc, no verdict): 2 sigma, other T_ramp, stricter readings, class table, controls."""
    _need(ch, "rb2_failed_run_counts_as", "within_boundary")
    gate_classes, gate_sig, T_j = _need(ch, "rb2_gate_class_set", "rb2_gate_sigma_factors", "rb2_judged_T_ramp_s")
    k, n = fr["rb2_k"], fr["rb2_n"]
    by = {}
    for r in runs:
        by.setdefault((float(r["sigma_factor"]), float(r["T_ramp_s"])), []).append(r)

    def counts(cell, classes):
        rs = cell
        return {"kept": sum(1 for r in rs if not _is_failed(r) and r["class"] in classes), "failed": sum(1 for r in rs if not r.get("missing") and _is_failed(r)),
                "missing": sum(1 for r in rs if r.get("missing")), "n_records": len(rs)}

    gate = []
    for f in gate_sig:
        cell = by.get((float(f), float(T_j)), [])
        c = counts(cell, gate_classes)
        incomplete = c["n_records"] != n or c["missing"] > 0
        st = NE if incomplete else (PASS if compare(c["kept"], ">=", k) else FAIL)
        gate.append({"sigma_factor": f, "T_ramp_s": T_j, **c, "denominator": n, "threshold": f">= {k} of {n}", "status": st,
                     "classes": dict(Counter(r["class"] for r in cell if not r.get("missing")))})
    status = NE if any(g["status"] == NE for g in gate) else (PASS if all(g["status"] == PASS for g in gate) else FAIL)
    beside = []
    for (f, T), cell in sorted(by.items()):
        row = {"sigma_factor": f, "T_ramp_s": T, "classes": dict(Counter(r["class"] for r in cell if not r.get("missing"))), "gated": (f in gate_sig and T == float(T_j))}
        row.update({"kept_primary": counts(cell, gate_classes)["kept"], "kept_S_plus_only": counts(cell, ("S+",))["kept"],
                    "kept_S_plus_or_S_abs": counts(cell, ("S+", "S-abs"))["kept"], "failed": counts(cell, gate_classes)["failed"]})
        row["label"] = LABEL_SIGMA + ("" if row["gated"] else "; " + LABEL_POSTHOC)
        if T in (10.0, 30.0):
            row["short_window_limit"] = "short-window false-surge rates per W apply (306, 400, 172, 24 of 500 at W = 0.2, 0.333, 0.593, 1.054 s)"
        beside.append(row)
    ctrl = {}
    for r in controls:
        ctrl.setdefault(float(r["sigma_factor"]), []).append(r)
    control_rows = [{"sigma_factor": f, "kept_primary": counts(cs, gate_classes)["kept"], "n_records": len(cs), "failed": counts(cs, gate_classes)["failed"],
                     "classes": dict(Counter(r["class"] for r in cs if not r.get("missing"))), "label": LABEL_CONTROL + "; feeds no gate; S-rel is not ramp evidence (DL-250)"}
                    for f, cs in sorted(ctrl.items())]
    return {"check": "RB2.headline_class_kept", "status": status, "gate": gate, "beside": beside, "controls": control_rows, "subgrid_carried_in": subgrid_logged,
            "failed_runs_total_gate_cells": sum(g["failed"] for g in gate), "label": LABEL_SIGMA, "n_evaluated": sum(g["n_records"] for g in gate)}


# --- RB5 (rulings 2 and delta0) ---------------------------------------------------------------------------------------

def rb5_delta0(by_T: dict, ch: dict) -> dict:
    """RB5 delta0 ladder at one or more T_ramp. by_T: {T_ramp: {delta0: record}} where the 1e-6 member is the S5 grid run (rb5_delta0_reference). Class unchanged =
    same exact Table 2.1 label as the 1e-6 member (UNVERIFIED reading of the plan's words). Delay and onset shifts are REPORTED, not tested."""
    _need(ch, "rb5_delta0_reference", "rb5_class_unchanged_means", "rb5_delay_shift")
    rows, n_pass, n_fail = [], 0, 0
    for T, d in sorted(by_T.items()):
        ref = d.get(1.0e-6)
        for d0, rec in sorted(d.items()):
            if d0 == 1.0e-6:
                continue
            if ref is None or rec is None or _is_failed(ref) or _is_failed(rec):
                rows.append({"T_ramp_s": T, "delta0": d0, "status": NE, "class": None if rec is None else rec.get("class")})
                continue
            same = rec["class"] == ref["class"]
            n_pass += same
            n_fail += not same
            rows.append({"T_ramp_s": T, "delta0": d0, "class": rec["class"], "ref_class": ref["class"], "status": PASS if same else FAIL,
                         "onset_shift_s": _sub(rec.get("onset_s"), ref.get("onset_s")), "delay_shift": _sub(rec.get("delay_eta"), ref.get("delay_eta"))})
    st = FAIL if n_fail else (PASS if n_pass and all(r["status"] == PASS for r in rows) else NE)
    return {"check": "RB5.delta0", "status": st, "rows": rows, "n_evaluated": n_pass + n_fail, "delay_shifts": "REPORTED, not tested (expected memory effect)"}


def _sub(a, b):
    return float(a) - float(b) if _fin(a) and _fin(b) else float("nan")


def rb5_updown(p5: dict, s4: dict | None, ch: dict) -> dict:
    """Ruling 2 (rb5_updown_source): P5 is the classified up-versus-down result; S4 is reported beside it, labelled "no class", as supporting amplitude evidence only.
    p5: {T_ramp: class} read from the stored P5 records. The plan gives no pass number beyond 'class unchanged'; none is invented: the row is REPORTED."""
    _need(ch, "rb5_updown_source")
    return {"check": "RB5.updown", "status": REPORTED, "p5_classes": dict(sorted(p5.items())), "n_evaluated": len(p5),
            "s4_beside": {"label": "no class (constant-parameter steps), supporting amplitude evidence only", "data": s4}}


# --- RB6 mean field ----------------------------------------------------------------------------------------------------

def rb6_rtol(by_T: dict, ch: dict) -> dict:
    """rtol ladder at T_ramp 10 s and 316.2278 s: onset and class against the 1e-10 member (the S5 grid run). Reported against rtol, not a pass test."""
    _need(ch, "rb6_rtol")
    rows = []
    for T, d in sorted(by_T.items()):
        ref = d.get(1.0e-10)
        for rt, rec in sorted(d.items()):
            if rt == 1.0e-10 or rec is None or ref is None:
                continue
            rows.append({"T_ramp_s": T, "rtol": rt, "class": rec["class"], "ref_class": ref["class"], "onset_diff_s": _sub(rec.get("onset_s"), ref.get("onset_s")),
                         "delay_diff": _sub(rec.get("delay_eta"), ref.get("delay_eta"))})
    return {"check": "RB6.rtol", "status": REPORTED, "rows": rows, "n_evaluated": len(rows)}


def rb6_floor_other_T(readings: dict, ch: dict) -> dict:
    """Floor levels at T_ramp 10 s and 316.2278 s (default rung only; the 5 percent Heun test cannot be formed there). Ruling 11: medians REPORTED ONLY, printed in the
    RB3(b) form: direction of change of the median delay with floor level; strict decrease is shown as a fact, no scaling law is entered (UNVERIFIED), no verdict.
    readings: {onset reading name: {T_ramp: {level_index: [delay or None per seed]}}} (the MS8 sheet gave RB3(b) under the raw crossing and the classifier onset)."""
    _need(ch, "rb6_floor_other_T_ramp", "s13_floor_other_T_ramp_form")
    rows = []
    for name, by_T in readings.items():
        for T, lv in sorted(by_T.items()):
            meds = {l: _med(ds) for l, ds in sorted(lv.items())}
            none = {l: sum(1 for x in ds if not _fin(x)) for l, ds in sorted(lv.items())}
            m = [meds[l] for l in sorted(meds)]
            if any(not math.isfinite(x) for x in m):
                direction = "undefined (a level has no onset)"
            elif all(b < a for a, b in zip(m, m[1:])):
                direction = "strictly decreasing with floor level"
            elif all(b > a for a, b in zip(m, m[1:])):
                direction = "strictly increasing with floor level"
            elif all(b <= a for a, b in zip(m, m[1:])):
                direction = "non-increasing with ties"
            else:
                direction = "not monotone"
            rows.append({"onset_reading": name, "T_ramp_s": T, "median_delay_by_level": meds, "seeds_without_onset_by_level": none, "direction": direction,
                         "strict_decrease": direction == "strictly decreasing with floor level"})
    return {"check": "RB6.floor_other_T_ramp", "status": REPORTED, "rows": rows, "n_evaluated": len(rows),
            "label": "reported only, RB3(b) form, no scaling law entered (UNVERIFIED); feeds no gate"}


# --- RB6 network (rulings 3 and 4) --------------------------------------------------------------------------------------

def psd_argmax_fpk(v, fs: float, W: float, step: float, span: tuple[float, float], band=M.G_BAND):
    """Reading (ii) of the network f_pk: mean over the spectrogram windows (Hann, W, detrend linear) whose centre lies in span of the PSD, argmax over the band;
    resolution 1/W, no interpolation (O6). None if no window centre lies in the span."""
    tc, f, S = M.spectrogram_v(np.asarray(v, float), fs, W, step)
    sel = (tc >= span[0] - EPS) & (tc <= span[1] + EPS)
    if not sel.any():
        return None
    band_sel = (f >= band[0]) & (f < band[1])
    return float(f[band_sel][np.argmax(np.asarray(S)[band_sel][:, sel].mean(axis=1))])


def _has_ep(r: dict) -> bool:
    return (not _is_failed(r)) and _fin(r.get("f_pk_hz")) and _fin(r.get("onset_s")) and _fin(r.get("end_s"))


def _pair(base: dict | None, other: dict | None, reading: str, fr: dict, bound_op: str = "<") -> dict:
    """One seed, one dt pair, one f_pk reading. Rulings 3: no episode at the base dt -> NOT EVALUABLE (neither pass nor fail); an episode created or removed by the
    change of dt is a class change, reported."""
    out = {"reading": reading}
    if base is None or other is None or base.get("missing") or other.get("missing"):
        return {**out, "status": NE, "reason": "record missing", "class_change": None}
    b_ep, o_ep = _has_ep(base), _has_ep(other)
    out["class_change"] = None
    if b_ep != o_ep:
        out["class_change"] = "episode created" if o_ep else "episode removed"
    if not b_ep:
        return {**out, "status": NE, "reason": "no episode at the base dt (no f_pk)"}
    if reading == "classifier_episode_fpk":
        f1 = float(base["f_pk_hz"])
        f2 = float(other["f_pk_hz"]) if o_ep else float("nan")
    else:
        span = (float(base["onset_s"]), float(base["end_s"]))
        if base.get("v") is None or other.get("v") is None:
            return {**out, "status": NE, "reason": "v not supplied"}
        f1 = psd_argmax_fpk(base["v"], base["fs"], base["W_s"], base["step_s"], span)
        f2 = psd_argmax_fpk(other["v"], other["fs"], other["W_s"], other["step_s"], span)
        if f1 is None or f2 is None:
            return {**out, "status": NE, "reason": "no spectrogram window inside the episode window"}
    if not (_fin(f1) and _fin(f2)):
        return {**out, "status": NE, "reason": "f_pk undefined at the other dt (" + (out["class_change"] or "no f_pk") + ")", "f1_hz": f1}
    rel = abs(f2 - f1) / f1
    return {**out, "f1_hz": f1, "f2_hz": f2, "diff_hz": f2 - f1, "diff_bins": (f2 - f1) * base["W_s"], "rel": rel,
            "status": (PASS if compare(rel, bound_op, fr["net_fpk_max"]) else FAIL), "reason": ""}


def rb6_network(recs: dict, fr: dict, ch: dict) -> dict:
    """RB6 network clause. recs: {(V_peak, dt_tau, seed): record}; a record carries class, f_pk_hz, onset_s, end_s (classifier episode; NaN if none), v, fs, W_s, step_s.

    Test: dt 1e-3 against 5e-4 at V_p 100 per seed, for each of the two f_pk readings, strictly less than the frozen 2 percent (the plan's "<"). A seed with no
    episode at dt 1e-3 is NOT EVALUABLE, listed by seed. Verdict per reading: FAIL if any evaluable seed fails, PASS if at least one passes and none fails, else NOT EVALUABLE
    (UNVERIFIED reading: all evaluable seeds must be inside). Other dt rungs and the V_p pairs are printed with their differences, as information, no test (ruling 4)."""
    _need(ch, "rb6_network_fpk_bound_boundary", "rb6_network_class_claim", "rb6_network_time_origin_check")
    srcs, _no_ep, vpc, seeds = _need(ch, "rb6_network_fpk_sources", "rb6_network_fpk_no_episode", "rb6_network_vp_comparison", "rb6_network_seeds")
    d_def, d_half = fr["net_dt"]["default_tau"], fr["net_dt"]["halved_tau"]
    seed_ids = sorted({k[2] for k in recs})
    gate_rows, per_reading = [], {}
    readings = [("classifier_episode_fpk" if x.startswith("classifier") else "psd_argmax") for x in srcs]
    for rd in readings:
        rows = [{"seed": s, **_pair(recs.get((100.0, d_def, s)), recs.get((100.0, d_half, s)), rd, fr)} for s in seed_ids]
        np_, nf = sum(r["status"] == PASS for r in rows), sum(r["status"] == FAIL for r in rows)
        per_reading[rd] = {"rows": rows, "n_pass": np_, "n_fail": nf, "not_evaluable_seeds": [r["seed"] for r in rows if r["status"] == NE],
                           "class_changes": [(r["seed"], r["class_change"]) for r in rows if r["class_change"]], "status": verdict_of(np_, nf)}
        gate_rows += rows
    sts = [v["status"] for v in per_reading.values()]
    status = FAIL if FAIL in sts else (PASS if all(s == PASS for s in sts) else NE)
    ladder = []
    for a, b in ((d_half, 2.5e-4), (2.5e-4, 1.0e-4)):
        for s in seed_ids:
            ladder.append({"seed": s, "dt_from": a, "dt_to": b, **_pair(recs.get((100.0, a, s)), recs.get((100.0, b, s)), "classifier_episode_fpk", fr)})
    vp = []
    for dt in (d_def, 1.0e-4):
        for s in seed_ids:
            p = _pair(recs.get((100.0, dt, s)), recs.get((200.0, dt, s)), "classifier_episode_fpk", fr)
            p["status"] = REPORTED if p["status"] in (PASS, FAIL) else p["status"]          # ruling 4: V_p comparison is information, not a test
            vp.append({"seed": s, "dt": dt, **p})
    classes = {str(k): r.get("class") for k, r in sorted(recs.items(), key=lambda kv: str(kv[0]))}
    return {"check": "RB6.network_fpk", "status": status, "per_reading": per_reading, "ladder_info": ladder, "vp_info": vp,
            "vp_label": "V_p +-100 vs +-200: REPORTED ONLY, no pass number in the plan; f_pk difference is information, not a test",
            "classes_information": classes, "class_claim": "none (G4-C3 stands)", "n_evaluated": sum(v["n_pass"] + v["n_fail"] for v in per_reading.values()),
            "label": LABEL_G4 + "; f_pk reading UNVERIFIED (M11-6)", "seeds_expected": seeds}


# --- RB9 (a) to (d) ----------------------------------------------------------------------------------------------------

def rb9a(unit: dict | None, fr: dict, ch: dict) -> dict:
    """RB9(a) from the stored unit-level result (scripts/run_rb9a_unit.py; ruling 6). unit: {max_rel_diff, per_tau, ...} or None if not stored.
    'within 0.5 percent' is inclusive (ruling 5). The scope limit is part of the result."""
    _need(ch, "rb9a_source", "within_boundary")
    if unit is None:
        return {"check": "RB9.a", "status": NE, "reason": "unit-level result file not stored", "label": LABEL_RB9A_SCOPE, "n_evaluated": 0}
    v = float(unit["max_rel_diff"])
    return {"check": "RB9.a", "status": PASS if compare(v, "within", fr["rb9a_tol"]) else FAIL, "value": v, "threshold": fr["rb9a_tol"], "per_tau": unit.get("per_tau"),
            "label": LABEL_RB9A_SCOPE, "n_evaluated": len(unit.get("per_tau") or [1])}


def cycle_frequency_hz(v, fs: float, onset_s: float, end_s: float, band=M.G_BAND) -> float:
    """Cycle frequency (O5): change of the unwrapped analytic phase of the band-passed v between onset and end of the classifier episode, over 2 pi, per second."""
    z = M._analytic(np.asarray(v, float), fs, band)
    phase = np.unwrap(np.angle(z))
    a = max(0, int(round(onset_s * fs)))
    b = min(len(phase) - 1, int(round(end_s * fs)))
    if b <= a:
        return float("nan")
    return float((phase[b] - phase[a]) / (2 * np.pi) / ((b - a) / fs))


def rb9b_row(v, fs: float, episode: dict | None, W_s: float, ch: dict) -> dict:
    """One run: spectral f_pk (the classifier output, resolution 1/W) against the cycle frequency over the classifier's flagged episode window (onset to end;
    rb9b_comparison_window). Within 1/W is inclusive (ruling 5). episode: dict with onset_s, end_s, f_pk_hz, or None (no flagged episode: not in the cell set)."""
    _need(ch, "rb9b_comparison_window", "within_boundary")
    if episode is None or not all(_fin(episode.get(k)) for k in ("onset_s", "end_s", "f_pk_hz")):
        return {"status": NE, "reason": "no flagged episode"}
    fc = cycle_frequency_hz(v, fs, episode["onset_s"], episode["end_s"])
    if not _fin(fc):
        return {"status": NE, "reason": "episode window shorter than one sample"}
    d = abs(float(episode["f_pk_hz"]) - fc)
    return {"f_spectral_hz": float(episode["f_pk_hz"]), "f_cycle_hz": fc, "diff_hz": d, "bound_hz": 1.0 / W_s, "diff_bins": d * W_s,
            "within": compare(d, "within", 1.0 / W_s), "status": PASS if compare(d, "within", 1.0 / W_s) else FAIL}


def rb9b(headline: dict, cells: list[dict], ch: dict) -> dict:
    """RB9(b). Gate: the headline run (ruling 7). Map 1 and map 2 cells that have a flagged episode and a stored v are REPORTED as the fraction within 1/W, with no gate
    fraction invented. headline/cells: dicts with v, fs, episode, W_s (cells also set)."""
    _need(ch, "rb9b_cells", "rb9b_comparison_window", "within_boundary")
    h = rb9b_row(headline["v"], headline["fs"], headline.get("episode"), headline["W_s"], ch)
    rep = {}
    for c in cells:
        if (c.get("v") is None and c.get("load") is None) or c.get("episode") is None:
            continue
        r = rb9b_row(c["v"] if c.get("v") is not None else c["load"](), c["fs"], c["episode"], c["W_s"], ch)
        if r["status"] in (PASS, FAIL):
            rep.setdefault(c["set"], []).append(r["within"])
    frac = {s: {"n": len(x), "within": int(sum(x)), "fraction": (sum(x) / len(x)) if x else float("nan")} for s, x in rep.items()}
    return {"check": "RB9.b", "status": h["status"], "headline": h, "cells_reported": frac, "n_evaluated": 1 if h["status"] in (PASS, FAIL) else 0,
            "cells_label": "REPORTED as a fraction; no gate fraction (ruling 7)"}


# --- RB9(c) and RB10: reclassification of stored series --------------------------------------------------------------------

CATEGORY = {"D-tr": "surge", "S+": "surge", "S-rel": "surge", "S-abs": "surge", "D-sus": "sustained", "S-sus": "sustained", "D-none": "quiet", "NS": "quiet"}


def category(cls: str) -> str | None:
    return CATEGORY.get(cls)


def reclassify(cells: list[dict], variant: str, classify_fn) -> list[dict]:
    """Apply one A8 variant to each cell's stored v. cells: dicts with id, set, mode, t_on, T_ramp_s, a_ref, baseline_class, and v or load() returning v.
    A cell is 'excluded' when the variant does not fit the record (class not_run) or the baseline class is not a class. Nothing is imputed."""
    out = []
    for c in cells:
        v = c["v"] if c.get("v") is not None else c["load"]()
        res = classify_fn(v, c["mode"], c["t_on"], c["T_ramp_s"], c["a_ref"], variant, inside_a4_region=c.get("inside_a4_region"))
        vc = res["cls"]
        base = c["baseline_class"]
        if vc in ("not_run", M.FAILED) or base in (None, "", "not_run", M.FAILED):
            st = "excluded"
        else:
            st = "changed" if vc != base else "unchanged"
        out.append({"id": c["id"], "set": c["set"], "baseline": base, "variant": vc, "status": st,
                    "category_changed": (category(vc) != category(base)) if st != "excluded" else None})
    return out


def change_fraction(rows: list[dict], bound: float, ch: dict) -> dict:
    """Fraction of cells that change class under one variant, rulings 5 and 10. Excluded cells (variant does not fit) are out of numerator and denominator; the verdict
    states the evaluated denominator; the worst case (every excluded cell counted as changed) is printed beside it, and if the two give different pass or fail results
    the verdict is flagged 'depends on exclusions'. 'At most' is inclusive."""
    _need(ch, "not_run_cells_count_as", "within_boundary")
    ev = [r for r in rows if r["status"] != "excluded"]
    ex = [r for r in rows if r["status"] == "excluded"]
    n_ev, n_ex, n_ch = len(ev), len(ex), sum(r["status"] == "changed" for r in ev)
    n_cat = sum(bool(r["category_changed"]) for r in ev)
    if n_ev == 0:
        return {"status": NE, "n_evaluated": 0, "n_excluded": n_ex, "n_changed": 0, "fraction": float("nan"), "worst_fraction": float("nan"), "flag": "", "bound": bound}
    frac = n_ch / n_ev
    worst = (n_ch + n_ex) / (n_ev + n_ex)
    ok_ev, ok_worst = compare(frac, "<=", bound), compare(worst, "<=", bound)
    flag = "depends on exclusions" if ok_ev != ok_worst else ""
    return {"status": PASS if ok_ev else FAIL, "n_evaluated": n_ev, "n_excluded": n_ex, "n_changed": n_ch, "fraction": frac, "worst_fraction": worst,
            "worst_status": PASS if ok_worst else FAIL, "flag": flag, "bound": bound, "n_category_changed": n_cat, "fraction_category": n_cat / n_ev,
            "denominator_statement": f"{n_ch} of {n_ev} evaluated cells ({n_ex} excluded)"}


def variant_table(cells: list[dict], variants: list[str], classify_fn, bound: float, ch: dict, verdict_set: str = "map1") -> dict:
    """Per variant and per cell set the change fraction. Only the verdict set (gate_cell_set, ruling 9) carries a status; other sets are REPORTED (no verdict)."""
    vset = _need(ch, "gate_cell_set")
    if vset != verdict_set:
        raise EvalError(f"gate_cell_set {vset!r} is not the set this table was built for ({verdict_set!r})")
    out = {}
    for var in variants:
        rows = reclassify(cells, var, classify_fn)
        per_set = {}
        for s in sorted({r["set"] for r in rows}):
            res = change_fraction([r for r in rows if r["set"] == s], bound, ch)
            if s != vset:
                res = {**res, "status_if_gated": res["status"], "status": REPORTED, "label": "beside the verdict set; feeds no verdict (ruling 9)"}
            per_set[s] = res
        out[var] = per_set
    return out


def rb9c(table: dict, ch: dict) -> dict:
    """RB9(c): band 30 to 120 Hz, at most the frozen 5 percent of cells change class; verdict set = gate_cell_set (map 1)."""
    vset = _need(ch, "gate_cell_set")
    r = table["band_30_120"][vset]
    return {"check": "RB9.c", **r, "set": vset, "beside": {s: v for s, v in table["band_30_120"].items() if s != vset}, "label": LABEL_PROVISIONAL}


def rb10(headline_rows: dict, table: dict, fr: dict, ch: dict) -> dict:
    """RB10: for each A8 variant the headline class is unchanged (headline_rows: {variant: {baseline, variant_class}}) and at most the frozen 10 percent of the map-1 cells
    change class. A variant that does not fit the headline record makes that variant NOT EVALUABLE. The window x {0.5, 2} line of S13 is the two window variants of this table."""
    _need(ch, "rb10_window_line_of_s13")
    vset = _need(ch, "gate_cell_set")
    per, sts = {}, []
    for var, ps in table.items():
        h = headline_rows.get(var)
        if h is None or h["variant_class"] in ("not_run", M.FAILED):
            hs = NE
        else:
            hs = PASS if h["variant_class"] == h["baseline"] else FAIL
        cs = ps[vset]["status"]
        st = FAIL if FAIL in (hs, cs) else (PASS if hs == cs == PASS else NE)
        per[var] = {"headline": hs, "map_cells": cs, "status": st, "fraction": ps[vset]["fraction"], "flag": ps[vset].get("flag", ""),
                    "n_evaluated": ps[vset]["n_evaluated"], "n_excluded": ps[vset]["n_excluded"], "worst_fraction": ps[vset].get("worst_fraction")}
        sts.append(st)
    status = FAIL if FAIL in sts else (PASS if sts and all(s == PASS for s in sts) else NE)
    win = {k: v for k, v in per.items() if k in ("window_x0.5", "window_x2")}
    return {"check": "RB10", "status": status, "variants": per, "window_line_of_s13": win, "set": vset, "label": LABEL_PROVISIONAL,
            "n_evaluated": min((p["n_evaluated"] for p in per.values()), default=0)}


# --- A11 ---------------------------------------------------------------------------------------------------------------------

BASE_COLUMNS = ("value", "threshold", "pass_or_fail", "input_commits")


def verdict_map(ch: dict) -> dict:
    m = EC.choice(ch, "a11_logged_verdict_map")
    bad = {k: v for k, v in m.items() if v not in STATUS_WORDS}
    if bad:
        raise UnmappedVerdict(f"a11_logged_verdict_map maps to words outside {STATUS_WORDS}: {bad}")
    return m


def map_logged(word: str, ch: dict) -> str:
    """A11 status word for one logged verdict word (verbatim lookup). A word with no entry raises UnmappedVerdict (ruling 13)."""
    m = verdict_map(ch)
    if word not in m:
        raise UnmappedVerdict(f"logged verdict word {word!r} has no entry in a11_logged_verdict_map ({EC.EVAL_FILE}); the reviewer adds it")
    return m[word]


def a11_columns(ch: dict) -> list[str]:
    extra = EC.choice(ch, "a11_extra_columns")
    return list(BASE_COLUMNS) + [c for c in extra if c not in BASE_COLUMNS]


def a11_row(ch: dict, *, rb_id: str, check_id: str, source: str, label: str, value="", threshold="", status: str | None = None, logged_verdict: str = "",
            n_evaluated="", input_commits="", note: str = "", recomputed: bool = False) -> dict:
    """One A11 row. Every logged word is mapped (UnmappedVerdict if not). recomputed_match: yes if the recomputed status equals the mapped logged status; no otherwise,
    including a check that was not recomputed or has no logged verdict yet (the note says which)."""
    logged_status = map_logged(logged_verdict, ch) if logged_verdict else ""
    st = status if status is not None else logged_status
    if st not in STATUS_WORDS:
        raise EvalError(f"{rb_id}/{check_id}: status {st!r} is not one of {STATUS_WORDS}")
    match = "yes" if (recomputed and logged_status and logged_status == st) else "no"
    row = {"rb_id": rb_id, "check_id": check_id, "value": value, "threshold": threshold, "pass_or_fail": st, "input_commits": input_commits, "source": source,
           "logged_verdict": logged_verdict, "recomputed_match": match, "n_evaluated": n_evaluated, "label": label, "note": note}
    cols = a11_columns(ch)
    missing = [c for c in cols if c not in row]
    if missing:
        raise EvalError(f"a11_extra_columns names columns the row builder does not fill: {missing}")
    return {c: row[c] for c in cols}


def write_a11_csv(rows: list[dict], path, ch: dict) -> None:
    import csv
    cols = a11_columns(ch)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r[c] for c in cols})


# --- A11 assembly ----------------------------------------------------------------------------------------------------------------

def load_logged(path=None) -> list[dict]:
    """The carried (MS8 to MS10) checks of configs/ms11/ms11_eval.yaml `a11_logged`: logged verdict word verbatim, source, label."""
    import yaml
    p = Path(path) if path else C.repo_root() / EC.EVAL_FILE
    return yaml.safe_load(p.read_text(encoding="utf-8"))["a11_logged"]


def _val(res: dict | None, key="status"):
    return "" if res is None else res.get(key, "")


def assemble_rows(results: dict, logged: list[dict], fr: dict, ch: dict, input_commits: str = "") -> list[dict]:
    """All A11 rows: the carried checks (logged verdict as logged, mapped; not recomputed at 11c: recomputed_match no, note says so) and the MS11 checks
    (recomputed from the evaluator outputs in `results`; no logged verdict yet, so recomputed_match is no and the note says so). A check whose evaluator output
    is absent is NOT EVALUABLE, never dropped. Failed checks stay in the table as FAIL."""
    rows: list[dict] = []
    for e in logged:
        hook = (results.get("recompute") or {}).get(f"{e['rb_id']}/{e['check_id']}")
        st = hook["status"] if hook else None
        rows.append(a11_row(ch, rb_id=e["rb_id"], check_id=e["check_id"], source=e["source"], label=e.get("label", "pre-registered"), value=e.get("value", ""),
                            threshold=e.get("threshold", ""), status=st, logged_verdict=e["logged_verdict"], n_evaluated=e.get("n_evaluated", ""),
                            input_commits=input_commits, recomputed=bool(hook),
                            note=("recomputed" if hook else "carried as logged; not recomputed at 11c (no hook registered)") + (("; " + e["note"]) if e.get("note") else "")))

    def ms11(rb, check, res, src, label="pre-registered", value="", threshold="", note="", status=None):
        if res is None and status is None:
            status, note = NE, "evaluator output not supplied" + (("; " + note) if note else "")
        rows.append(a11_row(ch, rb_id=rb, check_id=check, source=src, label=label, value=value, threshold=threshold,
                            status=status if status is not None else res["status"], n_evaluated=_val(res, "n_evaluated"), input_commits=input_commits,
                            note=("no logged verdict yet (first evaluation); " + note).strip("; ")))

    r2 = results.get("rb2")
    k, n = fr["rb2_k"], fr["rb2_n"]
    for i, f in enumerate((0.5, 1.0)):
        g = None if r2 is None else next((x for x in r2["gate"] if x["sigma_factor"] == f), None)
        ms11("RB2", f"headline_class_kept_{f}_sigma", None if g is None else {"status": g["status"], "n_evaluated": g["n_records"]}, "MS11 S11, DL-336 2b",
             value="" if g is None else f"{g['kept']} of {g['denominator']} ({g['failed']} failed)", threshold=f">= {k} of {n}", note=LABEL_SIGMA)
    ms11("RB2", "two_sigma_reported", r2, "MS11 S11; frozen: 2 sigma reported, no pass rule", status=REPORTED if r2 else None, note=LABEL_SIGMA + "; " + LABEL_POSTHOC)
    ms11("RB2", "stricter_readings", r2, "MS11 S11; DL-336 2b", label="post hoc", status=REPORTED if r2 else None, note=LABEL_POSTHOC)
    ms11("RB2", "dl251_controls", r2, "MS11_CTRL; DL-251", label="post hoc", status=REPORTED if r2 else None, note=LABEL_CONTROL)
    d5 = results.get("rb5_delta0")
    ms11("RB5", "delta0_T10_T316", d5, "MS11 S13 delta0; DL-336", threshold="same Table 2.1 label as the 1e-6 member")
    ms11("RB5", "updown", results.get("rb5_updown"), "P5 (S5, MS8) with S4 beside; ruling 2, DL-347", status=REPORTED if results.get("rb5_updown") else None, note="S4 labelled no class")
    ms11("RB6", "rtol_T10_T316", results.get("rb6_rtol"), "MS11 S13 rtol; plan: reported, not a pass test", status=REPORTED if results.get("rb6_rtol") else None)
    ms11("RB6", "floor_other_T_ramp", results.get("rb6_floor"), "MS11 S13 floor; ruling 11, DL-356", status=REPORTED if results.get("rb6_floor") else None,
         note="RB3(b) form, reported only, no scaling law (UNVERIFIED)")
    ms11("RB6", "network_fpk_halving_dt", results.get("rb6_network"), "MS11 S13 network; ruling 3, DL-348", threshold=f"< {fr['net_fpk_max']}", note=LABEL_G4)
    ms11("RB6", "network_vp_pm100_vs_pm200", results.get("rb6_network"), "MS11 S13 network; ruling 4, DL-349", status=REPORTED if results.get("rb6_network") else None,
         note="reported only, no pass number in the plan")
    ms11("RB9", "a_dimensional_vs_nondimensional", results.get("rb9a"), "unit-level test; ruling 6, DL-351", threshold=f"within {fr['rb9a_tol']}",
         value=_val(results.get("rb9a"), "value"), note=LABEL_RB9A_SCOPE)
    ms11("RB9", "b_spectral_vs_cycle_headline", results.get("rb9b"), "headline run; rulings 7 and 8, DL-352, DL-353", threshold="within 1/W")
    ms11("RB9", "b_map_cells_fraction", results.get("rb9b"), "map 1 and map 2 cells; ruling 7", status=REPORTED if results.get("rb9b") else None,
         note="reported as a fraction, no gate fraction")
    c = results.get("rb9c")
    ms11("RB9", "c_band_30_120_map1", c, "map 1; rulings 9 and 10, DL-354, DL-355", threshold=f"<= {fr['rb9c_max']}", value=_val(c, "fraction"),
         note=(c or {}).get("flag", "") or "")
    ms11("RB9", "d_tau_pm20", results.get("rb9d"), "ruling 12, DL-357 (STOPPED: parameter specification pending)", status=NE if results.get("rb9d") is None else None,
         note="runs not specified yet (item 12); reported only when run")
    r10 = results.get("rb10")
    ms11("RB10", "surge_definition_sensitivity_map1", r10, "headline and map 1; rulings 9 and 10", threshold=f"headline unchanged; <= {fr['rb10_max']}",
         note=(" ".join(sorted({v["flag"] for v in r10["variants"].values() if v["flag"]})) if r10 else ""))
    ms11("S13", "window_x0.5_x2", None if r10 is None else {"status": FAIL if any(v["status"] == FAIL for v in r10["window_line_of_s13"].values()) else (
        PASS if r10["window_line_of_s13"] and all(v["status"] == PASS for v in r10["window_line_of_s13"].values()) else NE), "n_evaluated": r10["n_evaluated"]},
         "S13 window line = RB10 window variants; M11-7", threshold=f"headline unchanged; <= {fr['rb10_max']}")
    return rows


# --- record readers (used by scripts/run_A11.py; tested on synthetic records only at 11c) --------------------------------------------------

def _eta_delay(cfg: dict, onset_s: float) -> tuple[float, float]:
    """eta at the onset and the delay eta_on - eta_H on the run's path (as ms10_eval.table21_fields)."""
    from .. import ramps
    from ..units import s_to_tau
    if not _fin(onset_s):
        return float("nan"), float("nan")
    path = ramps.make_path(cfg)
    tau = s_to_tau(np.array([onset_s]), cfg["model"]["tau_ms"])
    eta = float(np.broadcast_to(np.asarray(path.eta(tau), float), (1,))[0])
    return eta, eta - float(cfg["path"]["eta_H"])


def classify_stored(jp, fi: dict, with_v: bool = False) -> dict:
    """Class and episode fields of one stored record (json beside npz). Refuses a dirty or dry-run record. A record whose status is not ok is class `failed`."""
    from . import a7 as A7
    from . import ms9_classify as MCL
    jp = Path(jp)
    rec = json.loads(jp.read_text(encoding="utf-8"))
    git = rec.get("git") or {}
    if git.get("dirty") is not False or rec.get("dry_run"):
        raise EvalError(f"{jp.name}: dirty or dry-run record (git.dirty = {git.get('dirty')!r}); only dirty = false records are evaluated")
    cfg = rec["config"]
    mode = MCL.mode_of(cfg)
    T = float(cfg["path"]["T_ramp_s"])
    W, step = M.window_for_ramp(T)
    out = {"name": rec["name"], "mode": mode, "T_ramp_s": T, "W_s": float(W), "step_s": float(step), "status": rec["status"], "missing": False,
           "git_commit": git.get("commit"), "fs": MCL.fs_of(cfg)}
    key = cfg["seeds"].get("spawn_key")
    out["seed"] = int(key[-1]) if key else -1
    out["sigma_factor"] = float(cfg["noise"]["sigma_factor"]) if "noise" in cfg and "sigma_factor" in cfg["noise"] else None
    out["delta0"] = float(cfg["solver"]["delta0"]) if "solver" in cfg and "delta0" in cfg["solver"] else None
    out["rtol"] = float(cfg["solver"]["rtol"]) if "solver" in cfg and cfg["solver"].get("rtol") is not None else None
    if rec["status"] != "ok":
        return {**out, "class": M.FAILED, "reason": f"record status {rec['status']}"}
    with np.load(jp.with_suffix(".npz")) as z:
        v = z["v"]
    res, err = MCL.classify_array(mode, v, out["fs"], cfg["path"]["t_on_s"], T, fi["threshold"])
    out.update(MCL.row_from_result(res, err, mode, T))
    out["eta_onset"], out["delay_eta"] = _eta_delay(cfg, out["onset_s"])
    raw = A7.first_crossing(v, out["fs"], cfg["path"]["t_on_s"], fi["threshold"]) if mode == "D" else None
    out["onset_raw_s"] = float("nan") if raw is None else float(raw)
    out["eta_onset_raw"], out["delay_eta_raw"] = _eta_delay(cfg, out["onset_raw_s"])
    if with_v:
        out["v"] = v
    return out


def read_record(row: dict, fi: dict, with_v: bool = False) -> dict:
    """One record of a listed row of the frozen MS11 lists: the refusals of ms10_eval.check_record first (dirty flag, dry run, config hash, name, criteria SHA-256),
    then classify_stored. An absent file is {'missing': True} and is never replaced."""
    from . import ms10_eval as E10
    jp = E10.record_path(row)
    cfg0, key = row["cfg"], row["spawn_key"]
    base = {"name": row["name"], "family": row["family"], "list": row["list"], "seed": int(key[-1]) if key else -1, "T_ramp_s": float(cfg0["path"]["T_ramp_s"]),
            "sigma_factor": float(cfg0["noise"]["sigma_factor"]) if "noise" in cfg0 and "sigma_factor" in cfg0["noise"] else None,
            "spawn_key": key, "V_peak": cfg0.get("network", {}).get("V_peak"), "dt_tau": cfg0.get("network", {}).get("dt_tau"),
            "delta0": cfg0.get("solver", {}).get("delta0"), "rtol": cfg0.get("solver", {}).get("rtol")}
    if not jp.exists():
        return {**base, "missing": True}
    rec = json.loads(jp.read_text(encoding="utf-8"))
    E10.check_record(rec, row, fi["criteria_sha256"])
    return {**base, **classify_stored(jp, fi, with_v=with_v)}


def read_lists(fi: dict, names=None, with_v_for=("MS11_S13_NET",)) -> dict:
    """{list: [records in list order]} for the frozen MS11 lists. Refuses while any MS11 data file is not FROZEN, and refuses unlisted records in the family folders."""
    from . import ms10_eval as E10
    from . import ms11_runlist as RL11
    if RL11.is_draft():
        raise E10.EvalRefused(f"the MS11 data files are not FROZEN: {RL11.status()}")
    names = names or RL11.ALL_LISTS
    rows = {n: RL11.expand(n) for n in names}
    stray = E10.unlisted_records(rows)
    if stray:
        raise E10.EvalRefused(f"{len(stray)} record(s) in the family folders are not rows of the frozen lists, e.g. {stray[0]}")
    return {n: [read_record(r, fi, with_v=(n in with_v_for)) for r in rs] for n, rs in rows.items()}


def check_network_time_origin(rows_net: list[dict], mf_ref_json) -> list[dict]:
    """R27 as at MS10: the network rows' time origin against the stored 10 s mean-field record (same path clock, t_on and sample interval); a mismatch stops (EvalRefused)."""
    from . import ms10_eval as E10
    mf = E10.mf_origin_of_record(mf_ref_json)
    seen, out = set(), []
    for r in rows_net:
        cfg = r["cfg"]
        net = E10.origin_facts(cfg, float(cfg["network"]["rate_bin_ms"]))
        k = (net["t_on_s"], net["sample_ms"])
        if k not in seen:
            seen.add(k)
            out.append(E10.check_time_origin(net, mf, str(mf_ref_json)))
    return out


# --- collectors from records to evaluator inputs ---------------------------------------------------------------------------------------

def net_recs(records: list[dict]) -> dict:
    """{(V_peak, dt_tau, seed): record} for rb6_network."""
    return {(float(r["V_peak"]), float(r["dt_tau"]), r["seed"]): r for r in records}


def delta0_by_T(records: list[dict], grid_members: dict) -> dict:
    """{T_ramp: {delta0: record}} from the S13_delta0 records plus the S5 grid member (delta0 1e-6) per T_ramp: grid_members {T_ramp: record}."""
    out = {T: {1.0e-6: rec} for T, rec in grid_members.items()}
    for r in records:
        if r["family"] == "S13_delta0":
            out.setdefault(r["T_ramp_s"], {})[r["delta0"]] = None if r.get("missing") else r
    return out


def rtol_by_T(records: list[dict], grid_members: dict) -> dict:
    out = {T: {1.0e-10: rec} for T, rec in grid_members.items()}
    for r in records:
        if r["family"] == "S13_rtol":
            out.setdefault(r["T_ramp_s"], {})[r["rtol"]] = None if r.get("missing") else r
    return out


def floor_by_T(records: list[dict], key: str = "delay_eta_raw") -> dict:
    """{T_ramp: {level: [delay per seed or None]}} from the S13_floor records (the level is the fourth element of the spawn key [11, 3, t, l, s])."""
    out: dict = {}
    for r in records:
        if r["family"] != "S13_floor":
            continue
        level = int(r["spawn_key"][3])
        d = None if r.get("missing") or r.get("class") == M.FAILED else r.get(key)
        out.setdefault(r["T_ramp_s"], {}).setdefault(level, []).append(d if _fin(d) else None)
    return out


# --- stored map and headline series (loaders; the series are opened only by scripts/run_A11.py) ---------------------------------------------

def load_map_cells(csv_path, records_dir, set_name: str, a_ref: float, fi: dict, mode: str = "D") -> list[dict]:
    """Cell dicts for reclassify / rb9b from a stored class table (results/ms9/9e/map1_classes.csv, 9f/map2_classes.csv, 9f/subgrid_classes.csv) and the records
    beside it. v is loaded on demand (`load`), never held for all cells. The baseline class is the stored class of the table; the episode of the baseline
    classification (onset, end, f_pk) is read by `episode_of`."""
    import csv
    root = Path(records_dir)
    cells = []
    with Path(csv_path).open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            jp = root / f"{row['run']}.json"
            cfg = json.loads(jp.read_text(encoding="utf-8"))["config"]

            def load(jp=jp):
                with np.load(jp.with_suffix(".npz")) as z:
                    return z["v"]
            cells.append({"id": row["run"], "set": set_name, "mode": mode, "t_on": float(cfg["path"]["t_on_s"]), "T_ramp_s": float(cfg["path"]["T_ramp_s"]),
                          "a_ref": a_ref, "baseline_class": row["class"], "load": load, "fs": 1000.0 / cfg["solver"]["dt_out_ms"],
                          "W_s": M.window_for_ramp(float(cfg["path"]["T_ramp_s"]))[0]})
    return cells


def episode_of(cell: dict, fi: dict) -> dict | None:
    """The classifier's flagged episode of a cell (onset, end, f_pk) from the frozen classifier on the stored v; None if no episode or the window does not fit."""
    from . import ms9_classify as MCL
    res, _ = MCL.classify_array(cell["mode"], cell["load"](), cell["fs"], cell["t_on"], cell["T_ramp_s"], fi["threshold"])
    ep = None if res is None else res.episode
    return None if ep is None else {"onset_s": ep.onset_s, "end_s": ep.end_s, "f_pk_hz": ep.f_pk_hz}
