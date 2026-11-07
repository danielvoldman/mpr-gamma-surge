"""MS13 13t-4 (DL-636 E5, DL-637): the journal captions of the supplementary figures (FS1 in 13t-4), the FULL caption (seven labelled paragraphs, for the supplement) and the SHORT caption (for the
manuscript, at most `caption.short_max_words_<ID>` words).

Same rules as jcaption.py, jshort.py and jf26.py: plain words; no plan, milestone, DL number, step ID, key or code name; every number is read from the prepared data or the stored parameter rows,
only the wording is typed here. The take-home keeps the numbers and the order of the draft constant FS1_TAKE_HOME (the independent comparison finds the same numbers in it). Terms that no plan or
Key defines in plain words are listed in UNDEFINED_UNVERIFIED (written as they stand; reported to the reviewer).
"""
from __future__ import annotations

import numpy as np

from . import jcaption as JC
from . import jshort as JS

FS1_ID = "FS1"
UNDEFINED_UNVERIFIED = ("M2 (the comparison model; 'kept as the damped-ring comparison' is the ruled draft wording, DL-111)",
                        "fixed point, saddle, stable focus, stable node, e-fold (standard terms; the plain glosses in the Key are ours)",
                        "fold, cusp (the draft's formula positions; the plain glosses in the Key are ours)",
                        "'our own reading' for the check that the draft marks as our own reading with the source check deferred (ruled draft wording, DL-064, DL-082)")


def fs1_consts(d: dict, rows: list) -> dict:
    """The stored values that the FS1 captions state (parameter rows of the S1 and A1 records, the prepared data)."""
    pv = lambda k, p=None: JC.pv(rows, k, p)
    return {"tau": pv("model.tau_ms", "d"), "Delta": pv("model.Delta", "d"), "type": pv("model.type", "d"), "I_step": pv("path.I_amp", "d"), "I_sin": pv("path.I_amp", "e"), "period_s": pv("path.I_period_s", "e"),
            "eta_lo": float(d["eta"].min()), "eta_hi": float(d["eta"].max()), "n_eta": len(d["eta"]), "J_lo": float(d["J"].min()), "J_hi": float(d["J"].max()), "n_J": len(d["J"]),
            "n_checks": len(d["a0_target"]), "k_eta": d["k_eta"], "k_J": d["k_J"], "k_Delta": d["k_Delta"]}


def _take(d: dict, c: dict) -> str:
    n4 = c["n_checks"] - 1
    if not (all(str(p) == "pass" for p in d["a0_pass"]) and d["k4_pass"] and d["k3_pass"]):
        raise JC.JCaptionError("FS1: a replication row does not read 'pass' in the stored table (the take-home wording needs it)")
    return (f"The comparison model M2 (kept as the damped-ring comparison) passes {n4} of its {c['n_checks']} replication checks on the recorded results, the {c['n_checks']}th (a sinusoidal-forcing check) passes only on our own reading, "
            f"with its check against the primary source deferred, and the version of the step test on a network of N simulated spiking neurons was not run (the coupling of an M2 network is unsourced). "
            f"The root-count boundary lies within one cell of the formula fold at half spacing for {d['k1_pass_half']} of {d['k1_n']} r values (not drawn), {d['k1_pass_base']} of {d['k1_n']} at base spacing "
            f"(not drawn; the two cusp points need half spacing); the test point ({c['k_eta']:g}, {c['k_J']:g}) has a saddle, a stable focus and a stable node (not drawn); and the step response rings at the linearised "
            f"frequency and decays to {_e(d['k4_rel_err_frequency'])} and {_e(d['k4_rel_err_decay'])} relative. No stable focus on the grid is non-damped ({d['ring_n_nondamped']} of {d['ring_n_focus']}; the linearised rate has "
            f"standard error 0), and the largest cycles per e-fold inside the {d['band_hz'][0]:g} to {d['band_hz'][1]:g} Hz band is {d['ring_cyc_inG_max']:.1f}.")


def _e(x: float) -> str:
    m, e = f"{x:.1e}".split("e")
    return f"{m}e{int(e)}"


def fs1_caption(d: dict, rows: list, *, ids, c: dict) -> str:
    n = JC.num
    take = _take(d, c)
    t0, t1 = d["k4_t_start_ms"], d["k4_t_end_ms"]
    panels = " ".join([
        f"(a) The number of fixed points of the M2 model on the grid of eta_bar/Delta ({n(c['eta_lo'])} to {n(c['eta_hi'])}, {c['n_eta']} values) and J/sqrt(Delta) ({n(c['J_lo'])} to {n(c['J_hi'])}, {c['n_J']} values), one cell per grid node: "
        f"one (pale blue) or three (orange); black lines: the two branches of the fold given by a formula; circled plus: the cusp given by the formula (eta_bar/Delta {d['cusp_eta']:.3f}, J/sqrt(Delta) {d['cusp_J']:.3f}); "
        f"circled dot: the test point ({c['k_eta']:g}, {c['k_J']:g}). The refined half-spacing grid is not drawn. At the cusp the half-spacing result moves by {d['cusp_J_shift_cells']:.1f} J cells and "
        f"{abs(d['cusp_eta_shift_cells']):.1f} eta cells against the base grid (recorded; no claim that the requirement was met; the shift is not drawn).",
        f"(b) The frequency in Hz of the stable focus at each grid node ({d['ring_n_focus']} nodes; {d['ring_freq_min']:.2f} to {d['ring_freq_max']:.1f} Hz); grey: no stable focus. The ring rate is the linearised rate with standard "
        "error 0, not a fit to simulated rings, so every focus is damped by construction.",
        f"(c) The cycles per e-fold of the stable focus where its frequency lies in the {d['band_hz'][0]:g} to {d['band_hz'][1]:g} Hz band ({d['ring_n_inG']} of the {d['ring_n_focus']} nodes); grey: no stable focus, or its frequency "
        f"outside the band; the largest value is {d['ring_cyc_inG_max']:.2f}.",
        f"(d) The recorded response of the firing rate r to a step of the input current from 0 to {n(c['I_step'])} at the test point; the run starts in the low state r = {d['k4_start_r']:.4f}; the axis is cut at 600 ms and the run goes on to "
        f"{d['K4_t_ms'].max():g} ms, ending at r = {d['k4_end_r']:.4f}; dashed line: the value of r at the focus ({d['k4_r_star']:.4f}); dash-dot lines: the window of the fit, {d['k4_t_start_tau']:g} to {d['k4_t_end_tau']:g} tau "
        f"({n(t0)} to {n(t1)} ms with tau = {n(c['tau'])} ms; our reading of the time mapping, not verified). The fitted frequency and decay rate differ from the linearised ones by {_e(d['k4_rel_err_frequency'])} and "
        f"{_e(d['k4_rel_err_decay'])} relative (allowed {d['k4_tol_frequency']:g}); {d['k4_cycles']:.1f} cycles of the tail enter the fit.",
        f"(e) The recorded response of r to a sinusoidal input current of amplitude {n(c['I_sin'])} and period {n(c['period_s'] * 1000)} ms at the same test point (top) and the input current (bottom). Its definition of a burst, its tolerance and "
        "its time mapping are our own readings (not verified), and the check against the primary source is deferred. No crossing is drawn.",
        "The network version of the step test has no panel because it was not run. The recorded runs of (d) and (e) exist as two copies with equal arrays; the copy named by the replication table is drawn. "
        "M2 is the comparison model: nothing here is a result for M3.",
    ])
    settings = f"No classifier or spectrogram is used in this figure; the band of {d['band_hz'][0]:g} to {d['band_hz'][1]:g} Hz is the gamma band of the classifier."
    params = (f"Recorded values (the complete list with the stored key names is in the supplement): model {c['type']} with membrane time constant {n(c['tau'])} ms and heterogeneity Delta = {n(c['Delta'])}; "
              f"the maps sweep eta_bar/Delta from {n(c['eta_lo'])} to {n(c['eta_hi'])} ({c['n_eta']} values) and J/sqrt(Delta) from {n(c['J_lo'])} to {n(c['J_hi'])} ({c['n_J']} values); the test point of (d) and (e) is eta_bar {c['k_eta']:g}, "
              f"J {c['k_J']:g}, Delta {c['k_Delta']:g}; the step of (d) has amplitude {n(c['I_step'])}; the sinusoid of (e) has amplitude {n(c['I_sin'])} and period {n(c['period_s'] * 1000)} ms ({n(c['period_s'])} s).")
    failed = ("No row of the project's table of failed checks concerns this figure (our reading of where the checks apply; not verified). Two limits of the checks are stated instead of failures: the sinusoidal-forcing check passes only on "
              "our own reading of its burst definition, tolerance and time mapping, with the check against the primary source deferred, and the version of the step test on a network of N simulated spiking neurons was not run because "
              "the coupling of an M2 network is unsourced. No panel has a red title: no failed check is drawn here.")
    limits = JC.limits_paragraph(ids)
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        JC.key_symbols(rest, "eta", "Delta", "J", "tau", "r", "N"),
        "I = the input current; M2 = the comparison model, kept as the damped-ring comparison. A fixed point is a state in which r does not change; a stable focus is a fixed point that the system approaches with damped oscillations, a stable node one that "
        "it approaches without oscillation, and a saddle is unstable; the fold is where the number of fixed points changes and the cusp is where two fold branches meet; an e-fold is a decrease of the amplitude by the factor e (about 2.72), so the "
        "cycles per e-fold are the number of cycles over which the oscillation decays by that factor (glosses ours, not verified). Symbols on the image: circled dot = the test point; circled plus = the cusp; black lines = the fold branches.",
        "Replication check = a check of the M2 model against a published or derived result, run on the recorded results.", JC.key_words(rest)] if x)
    return JC.assemble(FS1_ID, take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)


def fs1_short(d: dict, c: dict, max_words: int, full: str) -> str:
    n = JC.num
    take = _take(d, c)
    return JS.finish(FS1_ID, [
        take,
        f"The maps use the mean excitability eta_bar and the coupling J scaled by the heterogeneity Delta (axes eta_bar/Delta and J/sqrt(Delta); the test point has eta_bar {c['k_eta']:g}, J {c['k_J']:g} and Delta {c['k_Delta']:g}).",
        f"(a) Number of fixed points (states in which r does not change) on the grid, one or three, with the fold (where their number changes) and the cusp from formulas. "
        f"(b) Frequency of the stable focus (damped oscillation) in Hz, {d['ring_freq_min']:.2f} to {d['ring_freq_max']:.1f}; grey: no focus. "
        f"(c) Cycles per e-fold (decay of the amplitude by the factor e) where the focus frequency is in the {d['band_hz'][0]:g} to {d['band_hz'][1]:g} Hz band; largest {d['ring_cyc_inG_max']:.2f}. "
        f"(d) Recorded step response of the rate r at the test point; the fitted frequency and decay rate differ from the linearised ones by {_e(d['k4_rel_err_frequency'])} and {_e(d['k4_rel_err_decay'])} relative. "
        f"(e) Recorded response of r to a sinusoidal input current (amplitude {n(c['I_sin'])}, period {n(c['period_s'] * 1000)} ms), with the current below; the check behind it is our own reading, not verified, and its check against the primary source is deferred.",
        "No panel has a red title: no failed check is drawn here.",
        JS.further_sentence(FS1_ID, full),
        f"Parameters: model {c['type']} with membrane time constant {n(c['tau'])} ms and heterogeneity Delta = {n(c['Delta'])}; eta_bar/Delta from {n(c['eta_lo'])} to {n(c['eta_hi'])} ({c['n_eta']} values), "
        f"J/sqrt(Delta) from {n(c['J_lo'])} to {n(c['J_hi'])} ({c['n_J']} values); step amplitude {n(c['I_step'])}; sinusoid amplitude {n(c['I_sin'])}, period {n(c['period_s'] * 1000)} ms.",
        "Limits: M2 is the comparison model, so nothing in this figure is a result for model M3 (the mean-field model); the focus is damped by construction (the ring rate is the linearised rate, not a fit to simulated rings).",
        JS._pointer(FS1_ID)], max_words, full)
