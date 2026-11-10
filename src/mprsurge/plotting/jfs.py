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


def fs1_consts(d: dict, rows: list, a2: dict | None = None) -> dict:
    """The stored values that the FS1 captions state (parameter rows of the S1 and A1 records, the prepared data); with the A2 ring-map arrays `a2` also the test-point values (DL-717)."""
    pv = lambda k, p=None: JC.pv(rows, k, p)
    a1 = {r["key"]: r["value"] for r in rows if str(r.get("source_run_id", "")).startswith("A1_")}
    if a1.get("model.I_drive") is None or a1.get("path.I_amp") is None:
        raise JC.JCaptionError("FS1: the root-count grid record lists no input drive or amplitude (13t-7 H5: stop)")
    for p in ("d", "e"):
        if (float(pv("model.eta_bar", p)), float(pv("model.J", p)), float(pv("model.Delta", p))) != (float(d["k_eta"]), float(d["k_J"]), float(d["k_Delta"])):
            raise JC.JCaptionError(f"FS1: the record of panel ({p}) is not at the test point of the prepared data (13t-7 H5: stop)")
    c = {"map_I_drive": a1["model.I_drive"], "map_I_amp": a1["path.I_amp"], "d_I_drive": pv("model.I_drive", "d"), "tau": pv("model.tau_ms", "d"), "Delta": pv("model.Delta", "d"), "type": pv("model.type", "d"), "I_step": pv("path.I_amp", "d"), "I_sin": pv("path.I_amp", "e"), "period_s": pv("path.I_period_s", "e"),
            "eta_lo": float(d["eta"].min()), "eta_hi": float(d["eta"].max()), "n_eta": len(d["eta"]), "J_lo": float(d["J"].min()), "J_hi": float(d["J"].max()), "n_J": len(d["J"]),
            "n_checks": len(d["a0_target"]), "k_eta": d["k_eta"], "k_J": d["k_J"], "k_Delta": d["k_Delta"]}
    if a2 is not None:
        c["tp"] = fs1_testpoint(a2, d, c)
    return c


def fs1_testpoint(a2: dict, d: dict, c: dict) -> dict:
    """DL-717 (13x X1, X2): the test-point values of panel (c) (input current 0) and of the post-step focus of (d), and the distance of the test point from the grey region of (b), all read from the
    A2 ring-map arrays. Stops with a named error if a reading that the caption relies on does not hold."""
    eta, J = np.asarray(a2["eta_over_Delta"], dtype=float), np.asarray(a2["J_over_sqrtDelta"], dtype=float)
    x, y = c["k_eta"] / c["k_Delta"], c["k_J"] / np.sqrt(c["k_Delta"])
    i, j = np.flatnonzero(eta == x), np.flatnonzero(J == y)
    if i.size != 1 or j.size != 1:
        raise JC.JCaptionError("FS1: the test point is not a grid node of the ring map (13x X1: stop)")
    i, j = int(i[0]), int(j[0])
    foc = np.asarray(a2["ring_is_focus"], dtype=bool)
    if int(foc[i, j].sum()) != 1:
        raise JC.JCaptionError("FS1: the test-point node does not hold exactly one stable focus (13x X1: stop)")
    k = int(np.flatnonzero(foc[i, j])[0])
    if float(c["map_I_drive"]) != float(c["d_I_drive"]):
        raise JC.JCaptionError("FS1: the input current of the root-count record differs from the starting input of the step record (13x X1: stop)")
    lam, tau_s = complex(a2["k4_lambda"]), float(a2["tau_ms"]) / 1000.0
    if lam.imag != float(a2["k4_omega_lin"]) or abs(float(np.asarray(a2["k4_post_step_fixed_point"])[0]) - float(a2["k4_r_star"])) > 1e-12 or float(a2["k4_r_star"]) != d["k4_r_star"]:
        raise JC.JCaptionError("FS1: the stored eigenvalue or fixed point of the step disagrees with the stored fit fields (13x X1: stop)")
    has = foc.any(axis=2)
    ii, jj = np.nonzero(~has)
    di, dj = ii - i, jj - j
    m = int(np.argmin(di.astype(float) ** 2 + dj.astype(float) ** 2))
    d_eta, d_J = float(eta[1] - eta[0]), float(J[1] - J[0])
    return {"f_c": float(a2["ring_freq_hz"][i, j, k]), "cyc_c": float(a2["ring_cycles_per_efold"][i, j, k]), "r_c": float(a2["ring_r"][i, j, k]),
            "f_d": lam.imag / (2 * np.pi * tau_s), "cyc_d": lam.imag / (2 * np.pi * abs(lam.real)), "r_d": float(a2["k4_r_star"]),
            "near_di": int(di[m]), "near_dj": int(dj[m]), "near_eta": abs(int(di[m])) * d_eta, "near_J": abs(int(dj[m])) * d_J, "block7": bool(has[i - 3:i + 4, j - 3:j + 4].all())}


def _take(d: dict, c: dict) -> str:
    n4 = c["n_checks"] - 1
    if not (all(str(p) == "pass" for p in d["a0_pass"]) and d["k4_pass"] and d["k3_pass"]):
        raise JC.JCaptionError("FS1: a replication row does not read 'pass' in the stored table (the take-home wording needs it)")
    return (f"The comparison model M2 (kept as the damped-ring comparison) passes {n4} of its {c['n_checks']} replication checks on the recorded results, the {c['n_checks']}th (a sinusoidal-forcing check) passes only on our own reading, "
            f"with its check against the primary source deferred, and the version of the step test on a network of N simulated spiking neurons was not run (the coupling of an M2 network is unsourced). "
            f"The root-count boundary lies within one cell of the formula fold at half spacing for {d['k1_pass_half']} of {d['k1_n']} r values (not drawn), {d['k1_pass_base']} of {d['k1_n']} at base spacing "
            f"(not drawn; the two cusp points need half spacing); the test point ({c['k_eta']:g}, {c['k_J']:g}) has a saddle, a stable focus and a stable node (not drawn); and the fitted frequency and decay rate of the step response "
            f"differ from the linearised ones by {_e(d['k4_rel_err_frequency'])} and {_e(d['k4_rel_err_decay'])} relative. No stable focus on the grid is non-damped ({d['ring_n_nondamped']} of {d['ring_n_focus']}; the linearised rate has "
            f"standard error 0), and the largest cycles per e-fold inside the {d['band_hz'][0]:g} to {d['band_hz'][1]:g} Hz band is {d['ring_cyc_inG_max']:.1f}.")


def panel_values_sentence(c: dict) -> str:
    """13t-7 (DL-659 H5): the parameter values each panel is drawn at, from the recorded parameter rows, and that (c) and (d) differ; nothing is interpreted."""
    n = JC.num
    return (f"Parameter values by panel: (a) to (c) are drawn on the grid of the root-count run, whose record lists an input drive of {n(c['map_I_drive'])} and an input amplitude of {n(c['map_I_amp'])} "
            f"(the ring-map file itself stores no input current), with membrane time constant {n(c['tau'])} ms and Delta = 1 (the axes are scaled by Delta); (d) is drawn at eta_bar {c['k_eta']:g}, J {c['k_J']:g} and Delta {c['k_Delta']:g} "
            f"with the input current stepped from {n(c['d_I_drive'])} to {n(c['d_I_drive'] + c['I_step'])}; (e) is drawn at the same eta_bar, J and Delta with a sinusoidal input current of amplitude {n(c['I_sin'])} and period "
            f"{n(c['period_s'] * 1000)} ms. Panels (c) and (d) are drawn at different parameter values.")


def _tp(c: dict) -> dict:
    if "tp" not in c:
        raise JC.JCaptionError("FS1: the test-point values of the ring map were not read (13x X1: stop)")
    return c["tp"]


def _tp_c(c: dict, *, short: bool) -> str:
    """13x X1 (DL-716, DL-717): panel (c) at the test point is read with the input current at its starting value; numbers from the ring-map arrays."""
    t, n = _tp(c), JC.num
    return f"At the circled test point, read with the input current at {n(c['d_I_drive'])}, the stable focus has {t['f_c']:.2f} Hz and {t['cyc_c']:.2f} cycles per e-fold" + ("." if short else " (recorded).")


def _tp_d(c: dict, *, short: bool) -> str:
    """13x X1: after the step the system settles on a different stable focus; the (c) values at the test point do not describe this ringing."""
    t, n = _tp(c), JC.num
    return (f"After the step to {n(c['d_I_drive'] + c['I_step'])} the system settles on a different stable focus (firing rate {t['r_d']:.4f}, against {t['r_c']:.4f} at input {n(c['d_I_drive'])}); its oscillation, "
            f"computed from the equations near that focus, has {t['f_d']:.2f} Hz and {t['cyc_d']:.2f} cycles per e-fold, so the values of (c) at the test point do not describe this ringing.")


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
        f"outside the band; the largest value is {d['ring_cyc_inG_max']:.2f}. {_tp_c(c, short=False)}",
        f"(d) The recorded response of the firing rate r to a step of the input current from 0 to {n(c['I_step'])} at the test point; the run starts in the low state r = {d['k4_start_r']:.4f}; the axis is cut at 600 ms and the run goes on to "
        f"{d['K4_t_ms'].max():g} ms, ending at r = {d['k4_end_r']:.4f}; dashed line: the value of r at the focus ({d['k4_r_star']:.4f}); dash-dot lines: the window of the fit, {d['k4_t_start_tau']:g} to {d['k4_t_end_tau']:g} tau "
        f"({n(t0)} to {n(t1)} ms with tau = {n(c['tau'])} ms; our reading of the time mapping, not verified). The fitted frequency and decay rate differ from the linearised ones by {_e(d['k4_rel_err_frequency'])} and "
        f"{_e(d['k4_rel_err_decay'])} relative (allowed {d['k4_tol_frequency']:g}); {d['k4_cycles']:.1f} cycles of the tail enter the fit. {_tp_d(c, short=False)}",
        f"(e) The recorded response of r to a sinusoidal input current of amplitude {n(c['I_sin'])} and period {n(c['period_s'] * 1000)} ms at the same test point (top) and the input current (bottom). Its definition of a burst, its tolerance and "
        "its time mapping are our own readings (not verified), and the check against the primary source is deferred. No crossing is drawn.",
        "The network version of the step test has no panel because it was not run. The recorded runs of (d) and (e) exist as two copies with equal arrays; the copy named by the replication table is drawn. "
        "M2 is the comparison model: nothing here is a result for M3.",
    ])
    settings = f"No classifier or spectrogram is used in this figure; the band of {d['band_hz'][0]:g} to {d['band_hz'][1]:g} Hz is the gamma band of the classifier."
    params = (f"Recorded values (the complete list with the stored key names is in the supplement): model {c['type']} with membrane time constant {n(c['tau'])} ms and heterogeneity Delta = {n(c['Delta'])}; "
              f"the maps sweep eta_bar/Delta from {n(c['eta_lo'])} to {n(c['eta_hi'])} ({c['n_eta']} values) and J/sqrt(Delta) from {n(c['J_lo'])} to {n(c['J_hi'])} ({c['n_J']} values); the test point of (d) and (e) is eta_bar {c['k_eta']:g}, "
              f"J {c['k_J']:g}, Delta {c['k_Delta']:g}; the step of (d) has amplitude {n(c['I_step'])}; the sinusoid of (e) has amplitude {n(c['I_sin'])} and period {n(c['period_s'] * 1000)} ms ({n(c['period_s'])} s). " + panel_values_sentence(c))
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
        f"(c) Cycles per e-fold (decay of the amplitude by the factor e) where the focus frequency is in the {d['band_hz'][0]:g} to {d['band_hz'][1]:g} Hz band; largest {d['ring_cyc_inG_max']:.2f}. {_tp_c(c, short=True)} "
        f"(d) Recorded step response of the rate r at the test point; the fitted frequency and decay rate differ from the linearised ones by {_e(d['k4_rel_err_frequency'])} and {_e(d['k4_rel_err_decay'])} relative. {_tp_d(c, short=True)} "
        f"(e) Recorded response of r to a sinusoidal input current (amplitude {n(c['I_sin'])}, period {n(c['period_s'] * 1000)} ms), with the current below; the check behind it is our own reading, not verified, and its check against the primary source is deferred.",
        "No panel has a red title: no failed check is drawn here.",
        JS.further_sentence(FS1_ID, full),
        f"Parameters: model {c['type']} with membrane time constant {n(c['tau'])} ms and heterogeneity Delta = {n(c['Delta'])}; eta_bar/Delta from {n(c['eta_lo'])} to {n(c['eta_hi'])} ({c['n_eta']} values), "
        f"J/sqrt(Delta) from {n(c['J_lo'])} to {n(c['J_hi'])} ({c['n_J']} values); step amplitude {n(c['I_step'])}; sinusoid amplitude {n(c['I_sin'])}, period {n(c['period_s'] * 1000)} ms. " + panel_values_sentence(c),
        "Limits: M2 is the comparison model, so nothing in this figure is a result for model M3 (the mean-field model); the focus is damped by construction (the ring rate is the linearised rate, not a fit to simulated rings).",
        JS._pointer(FS1_ID)], max_words, full)
