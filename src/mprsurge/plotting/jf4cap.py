"""MS13 13t-8 (DL-667 K1, K2): the journal captions of F4a and F4b, the FULL caption (seven labelled paragraphs, for the supplement) and the SHORT caption (for the manuscript).

Same rules as jcaption.py, jshort.py and jf26.py: plain words; no plan, milestone, DL number, step ID, key or code name in the short caption; every number is read from the prepared data, a stored table or
the stored parameter rows (only the wording is typed here); a number that the stored data do not give is not written. A reading that differs from the ruled expectation stops the build (f4_facts).
The check helpers of jshort.py (failed_in_full, further_sentence, finish, limit_clauses) are shared. Terms that no plan or full-caption Key defines in plain words are listed in UNDEFINED_UNVERIFIED.
"""
from __future__ import annotations

import numpy as np

from . import jcaption as JC
from . import jshort as JS
from . import plain as PL

MINUS = "−"
UNDEFINED_UNVERIFIED = ("start distance (the record gives the values 0.5, 1.5 and 3.0 and no unit or definition of the term)",
                        "hold (the part of the run after the ramp has reached its peak; our wording, 13o)",
                        "quasi-static reference (the plan's wording is for the delay column: onset at eta_H)",
                        "M2 (the comparison model; wording from the FS1 caption)")


def _fmt(x: float) -> str:
    return f"{x:.1f}"


def f4_facts(d: dict) -> dict:
    """The readings that the captions state; a result that differs from the ruled expectation stops the build (JCaptionError)."""
    fam_names = ("p1_linear", "p1_sigmoid", "p2_linear", "p2_sigmoid", "p5_linear", "p5_sigmoid")
    if (d["n_in_range"], d["n_testable"], d["n_testable_within_one_step"]) != (9, 6, 0):
        raise JC.JCaptionError(f"F4: in-range, testable, within one step are {(d['n_in_range'], d['n_testable'], d['n_testable_within_one_step'])}, not (9, 6, 0)")
    steps = [float(x) for x in d["testable_match_steps"]]
    if [round(x, 1) for x in steps] != [4.4, 7.6, 12.7, 20.6, 25.1, 33.1]:
        raise JC.JCaptionError(f"F4: the testable match errors are {steps}, not 4.4, 7.6, 12.7, 20.6, 25.1, 33.1")
    if round(d["head_radau_minus_default_ms"]) != 181:
        raise JC.JCaptionError("F4: the solver difference at the main example is not 181 ms")
    med_cls = [float(x) for x in d["floor_median_cls"]]
    if not (med_cls[0] == -1.5 and med_cls[1] == -1.5 and med_cls[2] > -1.5):
        raise JC.JCaptionError(f"F4: the classifier-onset medians of the floor levels are {med_cls}, not -1.5, -1.5 and a higher value")
    if not d["floor_dt_identical"]:
        raise JC.JCaptionError("F4: the floored delays differ between the four Heun steps")
    nm = np.nanmedian(np.asarray(d["noise_delay_eta_cross"], float), axis=1)
    neg_from = next(i for i in range(len(nm)) if np.all(nm[i:] < 0))
    t_neg = float(np.asarray(d["noise_T_ramp_s"], float)[neg_from, 0])
    if abs(t_neg - 5.62341325) > 1e-6:
        raise JC.JCaptionError(f"F4: the noisy median delay is negative from T_ramp {t_neg}, not from 5.62 s")
    n_seeds = [int(np.isfinite(np.asarray(r, float)).sum()) for r in d["noise_delay_eta_cross"]]
    if set(n_seeds) != {10}:
        raise JC.JCaptionError("F4: the noisy delay does not have 10 seeds with a value at every ramp duration")
    off = np.asarray(d["a3_offset"], float)
    if set(d["a3_ring_class"]) != {"damped"}:
        raise JC.JCaptionError("F4: the M2 ring class is not damped at every ramp duration")
    n_none6 = int(sum(sum(1 for c in d[f"{f}_cls"] if c == "D-none") for f in fam_names))
    sd5 = sorted((float(x) for x in np.asarray(d["sd05_match_err_steps"], float)[np.asarray(d["sd05_in_range"], bool) & ~np.asarray(d["sd05_eta_const"], bool)]), reverse=True)
    p5 = [float(x) for x in np.asarray(d["p5_linear_match_err_steps"], float)[np.asarray(d["p5_linear_in_range"], bool) & ~np.asarray(d["p5_linear_eta_const"], bool)]]
    if [round(x, 1) for x in sd5] != [33.1, 20.6, 12.7, 7.6, 4.4] or [round(x, 1) for x in p5] != [25.1]:
        raise JC.JCaptionError("F4: the testable runs are not the five start-distance runs and one P5 run of the ruled reading (DL-525)")
    if d["n_hold"] != 8 or d["n_nocross"] != 1:
        raise JC.JCaptionError(f"F4: hold marks {d['n_hold']} and runs without a crossing {d['n_nocross']} are not 8 and 1")
    return {"steps": steps, "sd5": sd5, "p5": p5, "t_neg": t_neg, "off_hi": float(off.max()), "off_lo": float(off.min()), "rate_lo": float(np.min(d["a3_rate"])), "rate_hi": float(np.max(d["a3_rate"])),
            "n_none6": n_none6, "n_untest": int(d["n_in_range"] - d["n_testable"]), "eps_lo": float(np.min(d["p1_linear_eps"])), "eps_hi": float(np.max(d["p1_linear_eps"])),
            "T_lo": float(np.min(d["p1_linear_T_ramp_s"])), "T_hi": float(np.max(d["p1_linear_T_ramp_s"])), "n_T": len(d["p1_linear_T_ramp_s"]), "head_ms": float(d["head_radau_minus_default_ms"]),
            "head_a": float(d["head_onset_cross_s"]), "head_b": float(d["head_radau_onset_cross_s"]), "t_pred": float(d["head_t_pred_s"]), "floor": [float(x) for x in d["floor_sigma"]],
            "med_cross": [float(x) for x in d["floor_median_cross"]], "n_nonneg": int(sum(1 for c in d["a3_ring_class"] if c == "damped"))}


def f4_consts(d: dict, rows: list) -> dict:
    return {**f4_facts(d), "sigma": JC.pv(rows, "noise.sigma", "S5_noise"), "delta0": JC.pv(rows, "solver.delta0"), "rtol": JC.pv(rows, "solver.rtol"), "type": JC.pv(rows, "model.type"),
            "scheme": JC.pv(rows, "noise.scheme")}


def _coincide(d: dict) -> str:
    from . import figures as FG
    eq = FG.f4_equal_runs(d, "delay_eta_cross")
    rd = FG.f4_reading_equal(d)
    return ("Recorded raw-crossing values that coincide are drawn at their recorded positions: " + "; ".join(f"{a} = {b} at {n} of 13 ramp durations" for a, b, n in eq)
            + ". The classifier-onset reading equals the raw reading at " + "; ".join(f"{n} of 13 ({a})" for a, n in rd) + ".")


def _fmt_list(xs) -> str:
    xs = [_fmt(x) for x in xs]
    return ", ".join(xs[:-1]) + " and " + xs[-1]


_RAMP = ("the ramp rate, the change of the mean excitability eta_bar over the whole ramp divided by the ramp duration T_ramp, with time in units of tau (the membrane time constant)")
_DELAY = ("the delay of the onset, the value of eta_bar at the onset minus its value eta_H at the Hopf point (negative: the onset comes before the Hopf point)")


# ---- F4a -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def f4a_caption(d: dict, a11: list, crit: dict, rows: list, *, strip_rows: list, ids, c: dict) -> str:
    n = JC.num
    nT = c["n_T"]
    take = (f"The onset of the surge does not follow the entry-exit prediction, and the checks on it FAILED: the RB3(a) onset check (0 of {d['n_testable']} testable in-range runs within one step of the prediction), "
            f"the RB6 solver check (the two solvers differ by {c['head_ms']:.0f} ms at the main example, against 1 ms allowed), and the RB3(b) delay under a noise floor DOES NOT MEET under the classifier-onset reading "
            f"(the delays tie at {MINUS}1.5 at two of the three floor levels). The gate G6 was ruled PASSED WITH DEPARTURES (the departures are the claim limits below). "
            f"The main example (T_ramp 120 s, no noise) has its onset at {n(c['head_a'])} s, far before the predicted entry at {c['t_pred']:.1f} s.")
    panels = " ".join([
        f"(a) {JC.cap1(_DELAY)}, against {_RAMP}, for the noise-free mean-field runs (mode D) of the paths P1, P2 and P5, each with the linear profile (solid line, filled marks) and the sigmoid profile (dashed line, open marks), "
        f"at {nT} ramp durations from {n(c['T_lo'])} to {n(c['T_hi'])} s. The onset is the first crossing of the envelope of v at 0.1 x A_ref (the raw first crossing; the primary reading); the onset of the classifier's episode "
        "(the second reading) is the small double dagger. The lines without marks (dash-dot for P1, dashed for P2, solid for P5) are the entry-exit prediction as recorded, drawn for the linear profiles where the predicted entry lies in the run. "
        f"An octagon ring marks a run inside the range of the onset check that is testable; the recorded error of the run in steps of the prediction grid (one step is the spacing of the eta_bar grid of the prediction) is not drawn on the ring and is in the source data, and the {d['n_testable']} testable "
        f"runs have errors {_fmt_list(c['steps'])} steps (25.1 here, P5 linear; the other five in (c)); a diamond ring marks the {c['n_untest']} in-range runs that are not testable (eta_bar is constant at the predicted time). "
        f"The red ring marks the main example, where the two solvers give the onsets {n(c['head_a'])} s and {n(c['head_b'])} s, {c['head_ms']:.0f} ms apart against 1 ms allowed; this run is not used as evidence. "
        f"The one run with no raw crossing is drawn in the band at the foot of the axes, not dropped. An open square marks the {d['n_hold']} drawn delays whose onset lies after the end of the ramp on P1 or P2 (an onset during the hold, "
        f"when eta_bar stays at its peak); there the delay equals eta_peak {MINUS} eta_H = {d['hold_delay_max']:g} (our reading of the recorded values, not verified; no logged ruling discusses it). P5 has no hold: it turns down after the ramp. "
        "The dotted zero line is the quasi-static reference by the definition of the delay (onset at eta_H); no quasi-static onset is computed here. " + _coincide(d),
        f"(b) For P5 (up and down ramp) at the {nT} ramp durations: the up delay (raw crossing), the offset on the way down (eta_bar at the onset of the down ramp minus eta_H; triangles) and the hysteresis width, as recorded; "
        "solid for the linear profile, dotted for the sigmoid profile.",
        f"(c) The delay of P1 linear at the start distances 0.5 (dotted), 1.5 (solid; the P1 linear series of (a)) and 3.0 (dashed); the start distance is a parameter of the start state. The octagon rings of the start distance 0.5 mark runs with the errors "
        f"{_fmt_list(c['sd5'])} steps; these numbers are not drawn on the image and are in the source data.",
        f"(d), (e) The delay at the main example (T_ramp 120 s) in runs with a very small added noise (the noise floor; standard deviation {JC.pv(rows, 'noise.sigma', 'S13_floor')} at level 0, {n(c['floor'][1])} at level 1 and {n(c['floor'][2])} at level 2), "
        "integrated with a fixed-step Heun scheme at four step sizes (1e-3, 5e-4, 2.5e-4 and 1e-4 tau), 10 seeds each, under the raw crossing (d) and under the classifier onset (e). The four step sizes are drawn as concentric hollow marks, "
        "because their values are identical (the floored delay does not depend on the step at the 1 ms output grid); the dark mark is the median of the 10 seeds. "
        f"The medians of (d) are {MINUS}0.000760, {MINUS}0.0423 and {MINUS}0.1051 at levels 0, 1 and 2 (the level-0 value is the delay of the main example), and in (e) the delays tie at {MINUS}1.5 at levels 0 and 1: the classifier-onset reading is saturated "
        f"(all 84 such delays have the onset at the ramp start, 5.0 s; the delay equals its minimum eta_start {MINUS} eta_H = {MINUS}1.5). The y axes of (d) and (e) differ and the range of each is stated under it. "
        "The delays are signed, on the 1 ms output grid. Every class that depends on the test for damped against non-damped oscillations is provisional.",
        "The peak power, peak frequency, duration, noise band and the M2 ramp are in F4b.",
    ])
    settings = JC.settings_line(crit)
    params = (f"Recorded values (the complete list with the stored key names is in the supplement): model {c['type']} at the reference parameter set named in the supplement; paths P1, P2 and P5 with the linear and the sigmoid profile; "
              f"ramp durations T_ramp {n(c['T_lo'])} to {n(c['T_hi'])} s ({nT} values, swept) and, at the main example, T_ramp 120 s; initial perturbation delta0 = {n(c['delta0'])} on v; solver relative tolerance {n(c['rtol'])} "
              f"(the solver is named in the supplement); noise floor levels {', '.join(n(x) for x in c['floor'])} with the {c['scheme']} scheme; no other noise in this figure.")
    failed = ("Shown, not dropped (the full list with value, threshold and source is in the supplement): " + "; ".join(JC.failed_line(r) for r in strip_rows) + ". " + JC.title_sentence("F4a")
              + " The noise-robustness FAILs (RB2) are listed with F4b.")
    limits = JC.limits_paragraph(ids, None) + " " + JC.limit_scope(ids)
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        JC.key_symbols(rest, "eta", "T_ramp", "tau", "modes"),
        "eta_H = the Hopf point value of eta_bar along the path. P1, P2 and P5 = the ramp paths: P1 and P2 ramp eta_bar up (P2 = the hypoxia-like path, with J ramped to 0 after a delay), P5 ramps eta_bar up and then down. "
        "F4b = the other figure of this paper that holds the peak power, peak frequency, duration, noise band and the M2 ramp.",
        JC.class_key(), "Checks: X.", JC.key_words(rest)] if x)
    text = JC.assemble("F4a", take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)
    return text.replace("Checks: X.", "Checks: " + JC.defined_checks(text) + ".")


F4A_LIMIT_EXTRA = {"G6-D1": "there is no claim that the onset follows the entry-exit prediction; the onset check is not validated (0 of 6 testable in-range runs within one step)",
                   "G6-D2": "the delay of the main example is taken from the runs with a noise floor, and the noise-free onset depends on the solver (58.698 s and 58.879 s, unexplained)",
                   "G6-D3": "the delay under a noise floor is reported under both onset readings (the raw crossing meets, the classifier onset gives equal delays and does not meet)",
                   "DL-163-D3": "the onset check is not judged at the main example (it covers 0 to 2 of the 13 ramp durations)",
                   "MS11-C6": "the direction of the change of the delay with the floor level is unresolved at ramp durations of 10 s and 316 s"}


def f4a_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int, full: str) -> str:
    n = JC.num
    return JS.finish("F4a", [
        "The onset (when the classifier, a rule fixed before the analysis, first flags the gamma rise) of the surge (a transient rise of gamma-band power, 25 to 100 Hz) does not follow the entry-exit prediction "
        "(the time at which the integral of the real part of the eigenvalue of the linearised model, taken from the start of the ramp, returns to zero), and the checks on it failed (red titles of (a) and (e)): "
        f"none of the {d['n_testable']} testable runs lies within one step of the prediction, the two numerical solvers differ by {c['head_ms']:.0f} ms at the main example (the run fixed before the analysis as the main case; "
        "1 ms allowed), and the delay under a noise floor does not meet its check under the classifier-onset reading.",
        "Mean field: the model's equations for the average activity of the population; mode D: noise-free; ramp: eta_bar (mean excitability) is changed from its start to its peak over the ramp duration T_ramp; "
        "Hopf point (where the resting state starts to oscillate).",
        f"(a) The delay of the onset (eta_bar at the onset minus eta_bar at the Hopf point; negative: the onset comes before the Hopf point) against the ramp rate (the change of eta_bar over the ramp divided by T_ramp, in units of tau, the membrane time constant) "
        f"for the paths P1 (eta_bar ramped only), P2 (hypoxia-like: mean excitability raised and coupling J ramped to 0 after a delay) and P5 (eta_bar up, then back down), linear (solid) and sigmoid (dashed) profile, "
        f"at {c['n_T']} ramp durations from {n(c['T_lo'])} to {n(c['T_hi'])} s: "
        "the raw first crossing of its detection threshold (the envelope at 0.1 times a reference amplitude; primary), the classifier's onset (second reading; double dagger), the prediction (line style by path) "
        "and rings for the runs inside the range of the onset check "
        f"(octagon: testable, errors {_fmt_list(c['steps'])} steps, in the source data; diamond: not testable, {c['n_untest']} runs). "
        f"The red ring: the main example (T_ramp 120 s), not used as evidence. Open squares: onset during the hold, when eta_bar stays at its peak (our reading, not verified). "
        "(b) P5: up delay, offset on the way down, hysteresis width. (c) P1 linear at start distances 0.5, 1.5 and 3.0. "
        f"(d), (e) The delay at the main example with a very small added noise (the noise floor), three levels, 10 seeds, four time steps drawn as concentric marks (equal values), dark mark: median; "
        f"the classifier-onset delays are equal at {MINUS}1.5 at the two lower levels.",
        JS.further_sentence("F4a", full),
        "Parameters: model M3 (the mean-field model); ramp durations 1 to 1000 s (13 values) and 120 s at the main example; initial perturbation 1e-6; solver relative tolerance 1e-10; "
        "classifier window 2 s, step 1 s for ramp durations of 60 s or more, gamma band 25 to 100 Hz, minimum 10 cycles.",
        JS.limit_clauses("F4a", F4A_LIMIT_EXTRA),
        JS._pointer("F4a")], max_words, full)


# ---- F4b -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def f4b_caption(d: dict, a11: list, crit: dict, rows: list, *, strip_rows: list, ids, c: dict) -> str:
    n = JC.num
    nT = c["n_T"]
    take = (f"The noise-robustness checks FAILED: RB2 (the noisy subgrid agrees with the noise-free map in 97 of 225 cells, 43.1 percent, against 203 needed) and RB2 (the main-example class is kept in 7 of 10 noisy seeds at the noise level "
            f"sigma = {n(c['sigma'])}, against 8 needed), and the classes of the noisy runs are mixed; with noise the median delay of the 10 seeds is negative from T_ramp {n(c['t_neg'])} s on. "
            f"The M2 ramp through the saddle-node is damped at all {c['n_T']} ramp durations and its jump offset from the fold falls from {n(round(c['off_hi'], 3))} to {n(round(c['off_lo'], 4))}.")
    panels = " ".join([
        f"(a) to (d) The peak power (absolute (a), relative (b)), the peak frequency (c) and the duration of the episode (d, logarithmic axis) of the same noise-free runs as in F4a (a) (six series: P1, P2 and P5, linear and sigmoid profile, {nT} ramp durations "
        f"from {n(c['T_lo'])} to {n(c['T_hi'])} s), against {_RAMP}. The 10 noisy seeds of P2 (mode N, sigma = {n(c['sigma'])}, checked and not confirmed) at each ramp rate are a grey bar from the minimum to the maximum of the seeds with a value and a dark median mark; "
        "the number above each panel's top edge is the number of seeds counted at each ramp rate (of 10); a seed with no episode or no crossing is left out of the bar and the median; nothing is smoothed or offset. "
        f"Octagon and diamond rings mark the runs inside the range of the onset check as in F4a (a). Runs with no episode (class D-none) are drawn at the foot of the panel, not dropped ({c['n_none6']} of the 78 runs of the six series; the table holds {d['n_none_class']} D-none runs in all). "
        "The peak frequency f_pk is the classifier's spectral peak. The dotted line at 1 s in (d) is the smallest duration the classifier can give (one window times the step, 1.0 s for ramp durations of 60 s or more); medians at 1.0 s are pinned by this floor, not a result. "
        "The y axes of (b) and (c) do not start at zero.",
        f"(e) The delay (as in F4a (a)) of the 10 noisy seeds of P2 with the linear profile, as grey bars and median marks, beside the noise-free P2 line; the dotted line is zero. The red title is the noise-robustness FAIL; "
        "the red lines state its two results (the main-example class kept in 7 of 10 seeds, 8 needed; 97 of 225 noisy subgrid cells agree, 203 needed), which are class counts and not drawn as marks. "
        "The classes of the noisy seeds are mixed (S+, S-rel, S-abs, S-sus and NS occur).",
        f"(f) The M2 ramp through the saddle-node (M2 = the comparison model with a damped ring; from the recorded table of the M2 saddle-node ramps): the jump offset from the fold in eta_bar (logarithmic axis) against the ramp rate "
        f"({nT} values from {n(c['eps_lo'])} to {n(c['eps_hi'])}); it falls from {n(round(c['off_hi'], 3))} to {n(round(c['off_lo'], 4))}; no scaling law is claimed. "
        f"(g) The fitted rate of the ring after the jump (per s, with {chr(0xb1)}1 standard error) against the ramp rate: between {MINUS}25.7 and {MINUS}24.3 per s, so the ring is damped at {c['n_nonneg']} of {nT}; the dotted zero line marks a non-damped ring. "
        "The static map of the rings of M2 has no ramp and is not drawn here.",
        "The delay panels, the onset prediction and the noise-floor runs are in F4a.",
    ])
    settings = JC.settings_line(crit)
    params = (f"Recorded values (the complete list with the stored key names is in the supplement): model {c['type']} at the reference parameter set named in the supplement; paths P1, P2 and P5 with the linear and the sigmoid profile; "
              f"ramp durations T_ramp {n(c['T_lo'])} to {n(c['T_hi'])} s ({nT} values, swept); initial perturbation delta0 = {n(c['delta0'])} on v; solver relative tolerance {n(c['rtol'])} (the solver is named in the supplement); "
              f"noisy runs: P2 linear, mode N, {c['scheme']} scheme, 10 seeds per ramp duration, {JC.sigma_text(a11, c['sigma'])}.")
    failed = ("Shown, not dropped (the full list with value, threshold and source is in the supplement): " + "; ".join(JC.failed_line(r) for r in strip_rows) + ". " + JC.title_sentence("F4b")
              + " The sigma check also FAILED (stored status in Parameters). The onset-prediction, solver and noise-floor FAILs (RB3(a), RB6, RB3(b)) are listed with F4a.")
    limits = JC.limits_paragraph(ids, None) + " " + JC.limit_scope(ids)
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        JC.key_symbols(rest, "eta", "T_ramp", "tau", "f_pk", "modes", "M3"),
        "P1, P2 and P5 = the ramp paths: P1 and P2 ramp eta_bar up (P2 = the hypoxia-like path, with J ramped to 0 after a delay), P5 ramps eta_bar up and then down. "
        "F4a = the other figure of this paper that holds the delay panels, the onset prediction and the noise-floor runs.",
        JC.class_key(), "Checks: X.", JC.key_words(rest)] if x)
    text = JC.assemble("F4b", take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)
    return text.replace("Checks: X.", "Checks: " + JC.defined_checks(text) + ".")


F4B_LIMIT_EXTRA = {"MS11-C1": "the main-example class is kept in 7 of 10 seeds at the noise level sigma (8 are needed); the runs without a ramp reach 7 of 10",
                   "MS11-C3": "the spectral peak (the peak of the power spectrum of the simulated signal) and the cycle frequency (the frequency of the oscillation that starts at the Hopf point) differ by 4.39 Hz at the main example, "
                              "and peak frequencies are the spectral peaks found by the classifier"}


def f4b_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int, full: str) -> str:
    n = JC.num
    return JS.finish("F4b", [
        "The noise-robustness checks failed (red title of (e)): with the noise level sigma = " + n(c["sigma"]) + " the main example (the run fixed before the analysis as the main case) keeps its surge class "
        "(a surge is a transient rise of gamma-band power, 25 to 100 Hz) in 7 of 10 noisy seeds (8 needed), and the 90 percent rule (at least 90 percent of the map cells (one parameter pair of a grid of mean-field runs) "
        "re-run with noise must agree with the noise-free map) fails: 97 of 225 of these cells agree, 43.1 percent (203 needed); the classes of the noisy runs are mixed, "
        f"and the median delay of the 10 seeds is negative from T_ramp {n(c['t_neg'])} s on.",
        "Mean field: the model's equations for the average activity of the population; noisy runs: mode N; noise-free: mode D; the ramp duration T_ramp is the time over which eta_bar (mean excitability) is changed; "
        "Hopf point (where the resting state starts to oscillate).",
        f"(a) to (d) Peak power (absolute, relative), peak frequency (the peak of the power spectrum, found by the classifier, a rule fixed before the analysis) and duration (how long the episode lasts: flagged windows x step; log axis) "
        f"of the six noise-free series (paths P1 (eta_bar ramped only), P2 (hypoxia-like: mean excitability raised and coupling J ramped to 0 after a delay) and P5 (eta_bar up, then back down); linear and sigmoid profile) "
        f"at {c['n_T']} ramp durations from {n(c['T_lo'])} to {n(c['T_hi'])} s, against the ramp rate (the change of eta_bar over the ramp divided by the ramp duration, in units of tau, the membrane time constant), "
        "with the 10 noisy seeds of P2 as a grey bar (minimum to maximum) and a dark median mark; the number above each panel is the number of seeds counted; "
        "rings: runs inside the range of the onset (when the classifier first flags the gamma rise) check (octagon: testable; diamond: not testable); foot marks: runs with no episode. "
        "The dotted line at 1 s in (d) is the smallest duration the classifier can give, so medians at 1.0 s are pinned. "
        "(e) The delay (eta_bar at the onset minus eta_bar at the Hopf point) of the noisy seeds beside the noise-free P2 line; the red lines give the two failed results. "
        f"(f) The M2 ramp through the saddle-node (M2: the comparison model): the jump offset from the fold falls from {n(round(c['off_hi'], 3))} to {n(round(c['off_lo'], 4))}; no scaling law is claimed. "
        f"(g) The fitted ring rate is negative, between {MINUS}25.7 and {MINUS}24.3 per s, so the ring is damped at {c['n_nonneg']} of {c['n_T']}.",
        JS.further_sentence("F4b", full),
        "Parameters: model M3 (the mean-field model); ramp durations 1 to 1000 s (13 values); noisy runs: P2 linear, 10 seeds per ramp duration, noise level sigma = 0.0624 (checked, not confirmed; its check failed); "
        "initial perturbation 1e-6; solver relative tolerance 1e-10; classifier window 2 s, step 1 s for ramp durations of 60 s or more, gamma band 25 to 100 Hz, minimum 10 cycles.",
        JS.limit_clauses("F4b", F4B_LIMIT_EXTRA),
        JS._pointer("F4b")], max_words, full)
