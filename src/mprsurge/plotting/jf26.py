"""MS13 13t-2 (DL-616 B3): the journal captions of F2 and F6, the FULL caption (seven labelled paragraphs, for the supplement) and the SHORT caption (for the manuscript, at most `caption.short_max_words_<ID>` words).

Same rules as jcaption.py and jshort.py (plain words; no plan, milestone, DL number, step ID, key or code name; every number is read from the prepared data, a stored table or the stored parameter rows;
only the wording is typed here; a number that the stored data do not give is not written). The check helpers of jshort.py (failed_in_full, further_sentence, finish, limit_clauses, undefined_terms, ...)
are shared. The terms that no plan or full-caption Key defines in plain words are listed in UNDEFINED_UNVERIFIED (written as they stand; reported to the reviewer).
"""
from __future__ import annotations

import re

import numpy as np

from . import captions as CAP
from . import jcaption as JC
from . import jshort as JS
from . import plain as PL

F2_ID, F6_ID = "F2", "F6"
FS3_ORDER = ("S+", "S-rel", "S-abs", "S-sus", "NS")                       # the order of the stored class counts (figures.FS3_CLASSES)
# plain words of the F6 failure labels (figures.F6J_LABEL_WORDS; the full wording of the stored short forms is in the supplement)
UNDEFINED_UNVERIFIED = ("sweep (the ruled F2 take-home does not define it; wording from the stored settings: eta_bar stepped up and then down)", "supercritical (plan wording: the squared amplitude grows linearly from the Hopf point, no hysteresis)",
                        "negative control (plan section 2.4 wording is for the first control only; the plain definition of 'a run in which no surge is expected' is ours)", "non-surge cell, failure label (ours; from the stored label table)",
                        "regime map (a grid of mean-field runs; ours)", "limit cycle (a steady, repeating oscillation; ours, 13t-4 E4)")


def _e3(x: float) -> str:
    """1.16e-3 style (one decimal, exponent without zero padding), as the ruled take-home writes small relative differences."""
    m, e = f"{x:.1e}".split("e")
    return f"{m}e{int(e)}"


def _pct(x: float) -> str:
    return f"{100.0 * x:+.1f}"


# ---- F2 --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def f2_consts(d: dict, rows: list, take_home: str) -> dict:
    m = re.search(r"A5 against S4 at most (\d+\.\d+e-\d+)", take_home)
    if m is None:
        raise JC.JCaptionError("F2: the ruled take-home no longer holds the A5 against S4 difference")
    pv = lambda k, p=None: JC.pv(rows, k, p)
    return {"a5_vs_s4": m.group(1), "mf_n": int(pv("s4.n_points", "S4_mf")), "step_s": pv("s4.step_s", "S4_mf"), "read_s": pv("s4.read_s", "S4_mf"),
            "n_net": len(pv("s4.indices", "S4_net")), "p_lo": float(d["mf_param"].min()), "p_hi": float(d["mf_param"].max()), "net_lo": float(np.min(d["net_param"])), "net_hi": float(np.max(d["net_param"])), "above": d["eta_H"] + 0.1,
            "tau": pv("model.tau_ms"), "J": pv("model.J"), "Delta": pv("model.Delta"), "tau_d": pv("model.tau_d_ms"), "N": int(pv("network.N")), "type": pv("model.type")}


def f2_facts(d: dict) -> dict:
    """13t-3 C3 (b) (DL-628): two facts read from the arrays that the draft prints nowhere: the largest difference between the network up and down sweeps in the v amplitude (value and eta_bar; over all
    steps and above eta_bar 3.0) and the v amplitudes at the Hopf point (network and mean field, up and down sweeps)."""
    p, up, vp = np.asarray(d["net_param"], float), np.asarray(d["net_up"]) == 1.0, np.asarray(d["net_v_ptp"], float)
    pairs = [(float(p[i]), float(vp[i]), float(vp[j])) for i in np.where(up)[0] for j in np.where(~up)[0] if abs(p[i] - p[j]) < 1e-6]
    if len(pairs) != int(up.sum()):
        raise JC.JCaptionError("F2: the network up and down sweeps do not pair step by step")
    big = max(pairs, key=lambda x: abs(x[2] - x[1]))
    big3 = max((x for x in pairs if x[0] > 3.0), key=lambda x: abs(x[2] - x[1]))
    h = [x for x in pairs if abs(x[0] - d["eta_H"]) < 1e-6]
    mp, mu, mv = np.asarray(d["mf_param"], float), np.asarray(d["mf_up"]) == 1.0, np.asarray(d["mf_v_ptp"], float)
    k = np.where(np.abs(mp - d["eta_H"]) < 1e-6)[0]
    mf_up, mf_dn = [float(mv[i]) for i in k if mu[i]], [float(mv[i]) for i in k if not mu[i]]
    if len(h) != 1 or len(mf_up) != 1 or len(mf_dn) != 1:
        raise JC.JCaptionError("F2: the Hopf point is not a step of both sweeps")
    return {"big": big, "big3": big3, "hopf_net": (h[0][1], h[0][2]), "hopf_mf": (mf_up[0], mf_dn[0])}


def f2_sentence_updown(d: dict) -> str:
    f = f2_facts(d)
    return (f"The largest difference between the network up and down sweeps in the v amplitude is {abs(f['big'][2] - f['big'][1]):.3f} ({f['big'][1]:.3f} up, {f['big'][2]:.3f} down) at eta_bar {f['big'][0]:.3f}; "
            f"above eta_bar 3.0 it is {abs(f['big3'][2] - f['big3'][1]):.3f} at eta_bar {f['big3'][0]:.3f}.")


def f2_sentence_hopf(d: dict, rest: bool = True) -> str:
    """rest=False (the short caption, 13t-4 E4: repeated prose removed): the 'does not rest' clause is already in sentence 2 of the short caption."""
    f = f2_facts(d)
    s = (f"At the Hopf point the network v amplitude is {f['hopf_net'][0]:.2f} (up sweep) and {f['hopf_net'][1]:.2f} (down sweep) against {f['hopf_mf'][0]:.2f} and {f['hopf_mf'][1]:.2f} for the mean field "
         f"(the steps within 0.1 of the Hopf point are still relaxing)")
    return s + (f"; below the Hopf point the network does not rest (v amplitude {d['net_floor_v_ptp_min']:.2f} to {d['net_floor_v_ptp_max']:.2f})." if rest else ".")


def f2_sentence1(d: dict) -> str:
    """13t-4 E1 (DL-636): sentence 1 of the journal captions of F2 (short and full). DEPARTURE from the ruled draft wording 'does not follow the mean-field branch closely' (F2_TAKE_HOME, DL-128, DL-129),
    which the recorded values contradict; the draft constant is not changed. The number is read from the arrays (cmp_rel_v_above_max); the sentence is the one ruled in DL-636."""
    top = 100.0 * float(d["cmp_rel_v_above_max"])
    if f"{top:.1f}" != "13.2":
        raise JC.JCaptionError(f"F2: the largest relative difference is {top:.1f} percent, not the 13.2 of the ruling (DL-636 E1: stop)")
    return f"Above the Hopf point the network amplitude lies close to the mean-field branch in (a) and (b) and differs from it by up to {top:.1f} percent in (c)."


F2_RED_NOTE = ("the network and mean-field classes disagree elsewhere (the check failed); this panel compares amplitudes only")                  # 13t-3 C1 (DL-628): the note of the image, in the caption


def f2_caption(d: dict, a11: list, rows: list, *, strip_rows: list, ids, c: dict) -> str:
    n = JC.num
    up_down = _e3(d["mf_updown_max_abs_from_0p2"])
    take = (f"{f2_sentence1(d)} The network's v amplitude differs from the mean field's by {_pct(d['cmp_rel_v_above_max'])} to {_pct(d['cmp_rel_v_above_min'])} percent above eta_bar 3.0 "
            "(the network's v is the mean V of the neurons that are not refractory, a different definition of v; information only, no criterion is applied), and below the Hopf point the network does not rest "
            f"(v amplitude {d['net_floor_v_ptp_min']:.2f} to {d['net_floor_v_ptp_max']:.2f}; {d['net_floor_steps']} steps). At the reference validation point the limit cycle of the mean field appears at eta_bar {d['eta_H']:.3f} in a "
            f"{d['hopf_type'].lower()} Hopf bifurcation (the squared amplitude grows linearly from the Hopf point, with no hysteresis), with no fold of cycles and stable cycles to eta_bar {d['a5_eta_max']:g}. "
            f"The quasi-static mean-field sweeps up and down lie on that branch with no hysteresis loop from 0.2 above the Hopf point (largest up-down difference in the v amplitude {up_down} relative, recorded; "
            f"the continuation against the sweeps differs by at most {c['a5_vs_s4']}, not drawn).")
    turn = ", ".join(f"{p['param']:.4f}" for p in d["a5_special_points"])
    panels = " ".join([
        "(a) Fixed point (grey line: solid where stable, dashed where unstable) and maximum and minimum of v on the stable limit cycle (black lines) against eta_bar; the dotted line is the Hopf point, the circled cross its mark "
        "(its v is interpolated linearly between the recorded fixed points, derived); the shaded band marks the steps within 0.1 of the Hopf point, where the 2 s step is still relaxing. "
        f"Mean-field sweep symbols: filled triangle for the up sweep, hollow smaller caret for the down sweep ({c['mf_n']} steps each way); network sweep symbols: open square (up) and open diamond (down), "
        f"{c['n_net']} steps each way, one run (one seed), no error bars. A sweep: eta_bar is raised step by step, then lowered again; each step lasts {n(c['step_s'])} s and the symbols show the maximum and minimum of v over its last {n(c['read_s'])} s.",
        f"(b) The v amplitude (maximum minus minimum): the cycle (black line) and the same symbols; the mean-field up and down sweeps coincide (largest difference {up_down} relative from 0.2 above the Hopf point, recorded), "
        "which is why the down sweep is drawn hollow and smaller. " + f2_sentence_updown(d) + " " + f2_sentence_hopf(d),
        f"(c) The recorded relative difference of the network's v amplitude from the mean field's, (network - mean field) / mean field, drawn above eta_bar {c['above']:.3f} only (the Hopf point plus 0.1; nearer to the Hopf point "
        f"the mean-field amplitude is about 0 or still relaxing, so the difference is not a measure; the largest recorded value below the Hopf point minus 0.1 is {CAP.number_text(float(format(d['cmp_rel_v_below_max_abs'], '.2g')))}, not drawn); "
        f"above it the v amplitude differs by {_pct(d['cmp_rel_v_above_max'])} to {_pct(d['cmp_rel_v_above_min'])} percent and the r amplitude by {_pct(d['cmp_rel_r_above_max'])} to {_pct(d['cmp_rel_r_above_min'])} percent (r amplitude: recorded, not drawn). "
        f"Below the Hopf point the network does not rest ({d['net_floor_steps']} steps: v amplitude {d['net_floor_v_ptp_min']:.2f} to {d['net_floor_v_ptp_max']:.2f}, r amplitude {d['net_floor_r_ptp_min']:.3f} to {d['net_floor_r_ptp_max']:.3f}, not drawn). "
        f"The continuation has an entry labelled fold at eta_bar {turn} (not drawn); it is the turn-around of the continuation next to the Hopf point, not a fold of cycles. "
        "Nothing in this figure is a frequency or a spectral peak.",
    ])
    settings = "No classifier or spectrogram is used in this figure; the gamma band is 25 to 100 Hz."
    params = (f"Recorded values (the complete list with the stored key names is in the supplement): model {c['type']} with membrane time constant {n(c['tau'])} ms, J = {n(c['J'])}, Delta = {n(c['Delta'])} and synaptic decay time tau_d = {n(c['tau_d'])} ms "
              f"(the reference validation point); the swept parameter is eta_bar, from {c['p_lo']:.3f} to {c['p_hi']:.3f} in {c['mf_n']} steps up and {c['mf_n']} steps down (mean field) and {c['n_net']} of them each way (network, {c['net_lo']:.3f} to {c['net_hi']:.3f}); "
              f"each step lasts {n(c['step_s'])} s and v is read over the last {n(c['read_s'])} s; network size N = {c['N']:,}.")
    failed = ("Shown, not dropped (the full list with value, threshold and source is in the supplement): " + "; ".join(JC.failed_line(r) for r in strip_rows)
              + ". " + JC.title_sentence(F2_ID) + " The four RB1 checks compare the classes of the network and the mean-field runs (the same class is required) and failed; " + F2_RED_NOTE + ". Panels (a) and (b) have no red title. "
              "The four RB1 rows are listed here because the figure draws network symbols (our reading of where the check applies, not verified).")
    limits = JC.limits_paragraph(ids) + " The network values are single runs (one seed) and are drawn without error bars; no agreement criterion is applied to them, so the network symbols have one shape per sweep direction."
    limits = limits + " " + JC.limit_scope(ids)
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        JC.key_symbols(rest, "eta", "Delta", "J", "tau_d", "r", "v", "N", "M3"),
        "Hopf point = the value of eta_bar at which the resting state starts to oscillate. Sweep = eta_bar is raised step by step, then lowered again.",
        "Symbols: black line = stable limit cycle; grey line = fixed point; dotted line = Hopf point; filled triangle = mean-field up sweep; hollow caret = mean-field down sweep; open square = network up sweep; open diamond = network down sweep.",
        "Checks: X.", JC.key_words(rest)] if x)
    text = JC.assemble(F2_ID, take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)
    return text.replace("Checks: X.", "Checks: " + JC.defined_checks(text) + ".")


def f2_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int, full: str) -> str:
    up_down = _e3(d["mf_updown_max_abs_from_0p2"])
    n = JC.num
    return JS.finish(F2_ID, [
        f"{f2_sentence1(d)} The Hopf point is where the resting state starts to oscillate. The network is the simulated network of N = 10,000 spiking neurons and the mean field is the model's equations for the average activity of the population; "
        f"the amplitude is that of v (the mean membrane potential; the network's v is the mean over the neurons that are not refractory, a different definition), differing by {_pct(d['cmp_rel_v_above_max'])} to {_pct(d['cmp_rel_v_above_min'])} percent above a mean excitability eta_bar of 3.0. "
        f"Below the Hopf point the network does not rest (v amplitude {d['net_floor_v_ptp_min']:.2f} to {d['net_floor_v_ptp_max']:.2f}). "
        f"In the mean field the limit cycle (a steady, repeating oscillation) appears at the Hopf point, eta_bar {d['eta_H']:.3f}, in a supercritical bifurcation (the oscillation grows smoothly from zero, with no jump and no hysteresis) and is stable to eta_bar {d['a5_eta_max']:g}.",
        "(a) Fixed point (grey) and maximum and minimum of v on the stable cycle (black) against eta_bar, with the Hopf point (dotted line and circled cross) and the sweeps (in a sweep eta_bar is raised step by step, then lowered again; "
        f"{c['mf_n']} steps each way for the mean field, {c['n_net']} for the network, each step lasting {n(c['step_s'])} s; the symbols are in the key of the image). "
        f"(b) The v amplitude (maximum minus minimum); the mean-field up and down sweeps coincide (largest difference {up_down} relative from 0.2 above the Hopf point). {f2_sentence_updown(d)} {f2_sentence_hopf(d, rest=False)} "
        f"(c) The relative difference of the network's v amplitude from the mean field's, above eta_bar {c['above']:.3f} only (nearer to the Hopf point the shaded steps are still relaxing).",
        "Failed check (red title of (c)): network against mean field (the same class is required), checked at the main example (the run fixed before the analysis as the main case) for ramp durations of 10 s and 120 s, "
        "at 4 map cells (one parameter pair of a grid of mean-field runs) and overall; all four checks failed. They compare classes, which this figure does not draw, so " + F2_RED_NOTE + ". Panels (a) and (b) have no red title.",
        JS.further_sentence(F2_ID, full),
        f"Parameters: model M3 (the mean-field model) with membrane time constant {n(c['tau'])} ms, coupling J = {n(c['J'])}, heterogeneity Delta = {n(c['Delta'])} and synaptic decay time tau_d = {n(c['tau_d'])} ms; "
        f"the mean excitability eta_bar is swept from {c['p_lo']:.3f} to {c['p_hi']:.3f} in {c['mf_n']} steps each way, each step {n(c['step_s'])} s; network N = {c['N']:,}, {c['n_net']} of the steps each way ({c['net_lo']:.3f} to {c['net_hi']:.3f}).",
        JS.limit_clauses(F2_ID, {"MS12-C1": "the surge result (a surge is a transient rise of gamma-band power, 25 to 100 Hz) is stated for model M3 only and stated for the mean field only (not for the network), "
                                           "and there is no claim that it is robust to finite-size fluctuations",
                                 "G4-C2": ""}).replace(
            "Limits: ", "Limits: the network curves are single runs (one seed) without error bars and no agreement criterion is applied to the amplitude comparison (information only); ", 1),
        JS._pointer(F2_ID)], max_words, full)


# ---- F6 --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def f6_consts(d: dict, raw: dict, rows: list) -> dict:
    net = raw["records"]["S12_NC1_net"]["config"]
    cells = raw["a10"][(raw["a10"]["control"] == "NC1") & (raw["a10"]["row_type"] == "map_cell")]
    cnt = d["nc1_modeN_count"]
    k = FS3_ORDER.index("S-rel")
    srel = [(float(t), int(cc[k]), int(nn)) for t, cc, nn in zip(d["nc_T"], cnt, d["nc1_modeN_n"]) if cc[k] > 0]
    other = [(float(t), [(FS3_ORDER[i], int(x)) for i, x in enumerate(cc) if x > 0 and i != int(np.argmax(cc))]) for t, cc in zip(d["nc_T"], cnt)]
    return {"N": int(net["network"]["N"]), "Delta": float(net["model"]["Delta"]), "tau_d": float(net["model"]["tau_d_ms"]), "T_ramp": float(net["path"]["T_ramp_s"]), "sigma": JC.pv(rows, "noise.sigma"),
            "type": JC.pv(rows, "model.type"), "cells": [(float(a), float(b)) for a, b in zip(cells["Delta"], cells["tau_d_ms"])], "srel": srel, "n_runs": int(d["nc1_modeN_n"].sum()),
            "t_lo": float(d["nc_T"].min()), "t_hi": float(d["nc_T"].max()), "n_T": len(d["nc_T"]), "amps": (0.5, 1.0, 2.0), "other": other}


def f6_facts(d: dict) -> dict:
    """13t-3 C4 (e), (f) (DL-628): the counts of the points of (d) and (e) and the peak frequencies that coincide, read from the arrays; a different result than the ruling states stops the build."""
    onset = np.asarray(d["s6_onset_s"], float)
    n_all, n_pre = int(onset.size), int(d["s6_n_prereg"])
    if (n_pre, n_all - n_pre) != (20, 4):
        raise JC.JCaptionError(f"F6: the points of (d) and (e) are {n_pre} pre-registered and {n_all - n_pre} comparator runs, not 20 and 4 (DL-628 C4 e: stop)")
    lab = [x[2] for x in __import__("mprsurge.plotting.figures", fromlist=["F6_S6_ROWS"]).F6_S6_ROWS]
    fp = np.asarray(d["s6_f_pk_hz"], float)
    same = [lab.index(x) for x in ("P3, I_amp 0.5", "P3, I_amp 1", "P4b", "P2 (comparators)")]
    if not all(np.array_equal(fp[same[0]], fp[i]) for i in same[1:]):
        raise JC.JCaptionError("F6: the recorded peak frequencies of P3 (drive 0.5 and 1), P4b and the P2 comparators are not identical (DL-628 C4 f: stop)")
    vals = [f"{x:.3f}".rstrip("0").rstrip(".") for x in fp[same[0]]]
    if vals != ["48.048", "49", "49", "49.5"]:
        raise JC.JCaptionError(f"F6: the identical peak frequencies are {vals}, not 48.048, 49, 49 and 49.5 Hz (DL-628 C4 f: stop)")
    n2 = sum(1 for x in list(d["nc2_I0_class"]) + list(d["nc2_I1_class"]) if x == "D-tr")
    if n2 != 2 * len(d["nc2_I0_class"]):
        raise JC.JCaptionError("F6: negative control 2 is not D-tr at every ramp duration (DL-628 C4 d: stop)")
    return {"n_all": n_all, "n_pre": n_pre, "n_cmp": n_all - n_pre, "fpk": vals}


def f6_sentence_points(d: dict) -> str:
    f = f6_facts(d)
    return (f"The {f['n_all']} points drawn in (d) and (e) are the {f['n_pre']} pre-registered runs and {f['n_cmp']} P2 comparator runs. In (e) the recorded peak frequencies of P3 (drive 0.5 and 1), P4b and the P2 comparators "
            f"are identical ({', '.join(f['fpk'][:-1])} and {f['fpk'][-1]} Hz), so those lines overlap.")


def _f6_rows_none(d: dict) -> int:
    return sum(1 for x in d["nc1_mf_class"] if x == "D-none")


def _tlist(ts) -> str:
    return JC._and_list([f"{t:g}" for t in ts])


def f6_caption(d: dict, a11: list, crit: dict, rows: list, *, strip_rows: list, ids, not_applicable, c: dict) -> str:
    n = JC.num
    lp = d["label_primary"].sum(axis=0)
    lab = ", ".join(f"{L} {int(x)}" for L, x in zip(("a", "b", "c", "d", "e", "f", "g", "h"), lp) if x > 0)
    n13 = len(d["nc1_mf_class"])
    s_rel_n = int(sum(x[1] for x in c["srel"]))
    take = (f"G7 NOT PASSED (1 network seed, S+): the one network run of the first negative control (network size N = {c['N']:,}, noisy mode, ramp duration {n(c['T_ramp'])} s, 1 seed) is in class {d['nc1_net_class']} "
            f"(provisional) where no surge class is expected ({d['nc1_net_expected']}). The {int(d['map_nonsurge'].sum())} non-surge cells of map 1 ({int(d['map_nonsurge'][0])}) and map 2 ({int(d['map_nonsurge'][1])}) each carry a failure label "
            f"(primary label {lab}); the labels are our operational rules and label c is a flag, not a demonstrated cause. The mean-field first negative control is D-none at {_f6_rows_none(d)} of {n13} ramp durations T_ramp and at the "
            f"{sum(1 for x in d['nc1_cells_class'] if x == 'D-none')} map cells, the third negative control is D-none at {sum(1 for x in d['nc3_class'] if x == 'D-none')} of {len(d['nc3_class'])}, and the second negative control is D-tr at "
            f"{sum(1 for x in d['nc2_I0_class'] if x == 'D-tr')} of {len(d['nc2_I0_class'])} ramp durations with the drive off and with the drive on; the network run is {d['nc1_net_class']} (provisional), so the negative-control gate G7 is NOT PASSED. "
            f"All {d['s6_n_prereg']} pre-registered runs (P3 at drive amplitudes 0.5, 1 and 2, P4a and P4b at T_ramp 10, 30, 120 and 300 s) are D-tr, so the surge is not confined to P3.")
    panels = " ".join([
        f"(a) For the {int(d['map_nonsurge'].sum())} non-surge cells of the two regime maps (a regime map is a grid of mean-field runs; a cell is one parameter pair), the number of cells with each failure label a to h: the primary label "
        "(the first that applies, in the order a to f, then g and h; filled bars) and every label that applies (hatched bars), for map 1 and map 2; the words of the labels are listed under the panel; a cell of class D-tr carries no label "
        f"(D-tr cells: map 1 {int(d['map_surge'][0])}, map 2 {int(d['map_surge'][1])}).",
        f"(b) The class of each negative control at each of {n13} ramp durations T_ramp ({n(c['t_lo'])} to {n(c['t_hi'])} s): the first negative control as a noise-free mean-field run (expected D-none) and as a mean field with noise, {c['n_runs'] // n13} seeds "
        "per T_ramp (expected NS; the mark is the most common class and the text gives the seeds in another class), the second negative control with the drive off (I = 0) and on (I = 1; the expected class is not stated), and the third negative control "
        f"(exploratory; the expected class is not stated). The noisy first negative control has S-rel in {s_rel_n} of {c['n_runs']} runs (at T_ramp {_tlist([t for t, _, _ in c['srel']])} s); these runs are not counted for the gate "
        "(supplementary), and whether the gate should read them is not verified. Negative control 2 (the full path with the common drive off and on) is D-tr at every ramp duration in the mean field (13 of 13 with the drive off and 13 of 13 with it on).",
        f"(c) The first negative control at the {len(c['cells'])} map cells of the mean field (Delta, tau_d in ms as in the tick labels: " + "; ".join(f"{a:g}, {b:g}" for a, b in c["cells"]) + f"; class D-none at all {len(c['cells'])}) and, in its own column, "
        f"the one network run (N = {c['N']:,}, Delta {n(c['Delta'])}, tau_d {n(c['tau_d'])} ms, ramp duration {n(c['T_ramp'])} s): class {d['nc1_net_class']}, red because the gate failed.",
        "(d), (e) The recorded onset and peak frequency of the P3 runs (drive amplitude 0.5, 1 and 2), P4a, P4b and the P2 comparators at T_ramp 10, 30, 120 and 300 s; every drawn class is D-tr (the small mark on each point). " + f6_sentence_points(d) + " "
        "The P2 line joins the comparators at 10 and 120 s (filled) and the references at 30 and 300 s (open). Rows with identical recorded values coincide and are drawn at their recorded positions, told apart by their marks: in (e) "
        "the peak frequencies of P3 (drive 0.5 and 1), P4b and P2 are equal. No comparison of the regions of P2 and P3 is drawn.",
        "The boundary of the regime map and the exit extension of the episode rule to P3 and P4 are not drawn. The failures and the non-surge regimes are drawn at the same weight as the surge cells.",
    ])
    settings = JC.settings_line(crit)
    params = (f"Recorded values (the complete list with the stored key names is in the supplement): model {c['type']}; the network run of the first negative control: network size N = {c['N']:,}, Delta = {n(c['Delta'])}, synaptic decay time "
              f"tau_d = {n(c['tau_d'])} ms, hypoxia-like path with the mean excitability falling, ramp duration {n(c['T_ramp'])} s, no common drive; {JC.sigma_text(a11, c['sigma'])}; ramp durations T_ramp {n(c['t_lo'])} to {n(c['t_hi'])} s ({n13} values, swept) "
              "and drive amplitudes 0.5, 1 and 2 (swept); the map cells have their own Delta and tau_d as in the tick labels of (c).")
    failed = ("Shown, not dropped (the full list with value, threshold and source is in the supplement): " + "; ".join(JC.failed_line(r) for r in strip_rows) + ". " + JC.title_sentence(F6_ID)
              + " The failed result is the class S+ of the one network run, drawn as the red circle of (c); the stored table gives no value or threshold for the gate row.")
    ids = tuple(ids) + (() if "G4-C4" in ids else ("G4-C4",))                          # 13t-3 C4 (g): the ruled sigma limit, journal captions only
    limits = JC.limits_paragraph(ids, not_applicable, na_text=PL.NOT_APPLICABLE_PLAIN_F6) + " " + JC.limit_scope(ids)
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        JC.key_symbols(rest, "Delta", "tau_d", "T_ramp", "N", "M3"),
        "P2 = the hypoxia-like path: eta_bar ramped up, with J ramped to 0 after a delay; P3 = P2 plus a common drive; P4a and P4b = P2 with Delta multiplied by 1.5 (P4a) or by 2/3 (P4b) over the ramp. "
        "A negative control is a run in which no surge is expected: the first = the hypoxia path with the mean excitability falling by the same amount, with coupling, heterogeneity and synaptic decay fixed and no common drive; "
        "the second = the full path with the common drive off or on (no expected class is stated); the third = inhibition raised while the mean excitability falls (exploratory; no expected class is stated).",
        "Failure labels of a non-surge cell (the stored short forms): a = Delta above critical; b = tau_d outside the window; c = a flag, not a demonstrated cause; d = ramp too fast for 10 cycles; e = no exit (D-sus or S-sus); "
        "f = amplitude below the fixed threshold; g = Hopf point with no time inside; h = rejected by the damped-oscillation test.",
        "Marks: diamond = D-none, left triangle = NS, right triangle = D-tr, circle = S+. Filled bars = primary label; hatched bars = every label that applies.",
        "Checks: X.", JC.class_key(), JC.key_words(rest)] if x)
    text = JC.assemble(F6_ID, take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)
    return text.replace("Checks: X.", "Checks: " + JC.defined_checks(text) + ".")


F6_LIMIT_EXTRA = {"MS9(e)-3": "failure label c (a cell without a surge class whose frequency is below 25 Hz) is a flag, not a demonstrated cause",
                  "MS9(e)-5": "every class that depends on the test for damped against non-damped oscillations is provisional",
                  "MS9(e)-1": "network surge classes at N = 1e4 are not evidence of a ramp-driven surge (control flagged in 10 of 10 seeds, ramp runs 10 of 10; other network runs, not drawn)",
                  "G4-C3": "no-ramp network controls (the same network without the ramp) are classified into surge classes"}


def f6_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int, full: str) -> str:
    n = JC.num
    n13 = len(d["nc1_mf_class"])
    s_rel_n = int(sum(x[1] for x in c["srel"]))
    return JS.finish(F6_ID, [
        "The negative-control check failed (red title of (c)): the network run (the simulated network of N = 10,000 spiking neurons, 1 seed) of the first negative control "
        "(a negative control is a run in which no surge is expected: here the hypoxia-like path with the mean excitability falling by the same amount) is in class S+ "
        f"(absolute and relative rise, ending: a surge, a transient rise of gamma-band power, 25 to 100 Hz) where {d['nc1_net_expected']} (no rise) is expected.",
        f"(a) Number of the {int(d['map_nonsurge'].sum())} non-surge map cells (one parameter pair of a grid of mean-field runs, in two maps; non-surge: not D-tr, an episode that ends) with each failure label a to h "
        "(the labels are listed in the key below the bars); filled bars: the primary label (the first that applies); hatched and dotted bars: every label that applies. "
        f"(b) Class of each negative control against the ramp duration T_ramp at {n13} values: negative control 1 without and with noise (10 seeds; text: other-class seeds, S-rel in {s_rel_n} of {c['n_runs']} runs; "
        "S-rel: relative rise only; NS: no rise, the noisy-run counterpart of D-none (no episode)), negative control 2 (the full path with the drive off and on) and negative control 3 (inhibition raised while the mean excitability falls; exploratory). "
        "In the mean field (the model's equations for the average activity of the population), negative control 2 is D-tr at every ramp duration; the failed check is the one on negative control 1 (network S+). "
        f"(c) The first negative control at the {len(c['cells'])} map cells (all D-none, no episode) and as the network run (red S+). "
        "(d), (e) Onset (when the classifier, a rule fixed before the analysis, first flags the gamma rise) and peak frequency (the peak of the power spectrum) of P2 (the hypoxia-like path: mean excitability raised, "
        "coupling J ramped to 0 after a delay), P3 (P2 plus a common drive, amplitude 0.5, 1, 2), P4a and P4b (P2 with Delta, the heterogeneity, multiplied by 1.5 or 2/3) at T_ramp 10, 30, 120 and 300 s (120 s points: right of tick 100); "
        f"all are D-tr. {f6_sentence_points(d)}",
        JS.further_sentence(F6_ID, full),
        f"Parameters: model M3 (the mean-field model); network run N = {c['N']:,}, heterogeneity Delta = {n(c['Delta'])}, synaptic decay time tau_d = {n(c['tau_d'])} ms, ramp duration {n(c['T_ramp'])} s; "
        "classifier window 2 s, step 1 s for ramp durations of 60 s or more (shorter ramps use a shorter window), gamma band 25 to 100 Hz; noise level sigma = 0.0624.",
        JS.limit_clauses(F6_ID, {**F6_LIMIT_EXTRA, "G4-C4": "the noise level sigma = 0.0624 is checked and not confirmed (its check failed; the noisy rows of (b) use it)"}),
        JS._pointer(F6_ID)], max_words, full)
