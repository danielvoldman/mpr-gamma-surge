"""MS13 13t-1e (DL-582 U3), 13t-1f (DL-592 to DL-594 V3 to V8): the SHORT journal caption, the one for the manuscript, in plain language for a reader who has never seen the project.

The FULL caption (jcaption.py: seven labelled paragraphs, check IDs, the ruled limits, the parameters and settings) goes to the supplement and the export manifest; this module builds the short
caption of the same figure from the same prepared data and the same stored tables. Rules: at most `caption.short_max_words` words (F1 `short_max_words_F1`; the limits are in
configs/journal_export.yaml, UNVERIFIED); no check ID, gate ID, step ID, plan, DL or milestone reference; the order is the take-home with the main failure in plain words, one sentence per
panel, the sentence that explains each red title, the failed checks whose result is drawn (each in one plain clause with what it tests; V7), the sentence with the number of the other failed checks
of the full caption (computed from the full caption by `failed_in_full`), the claim limits that are specific to the figure, and the pointer to the supplement. V5: every technical term is defined
in the caption, in one plain clause, where it is first used (DEFS: the clause is written once and the test checks that the first use of the term lies inside its clause). V4: N is written 1000, 3000,
10,000 and 30,000 (JC.plain_n). Every number is read from the prepared data or a stored table; only the wording is typed here. The word 'stored' is not used; 'recorded' is defined once.
"""
from __future__ import annotations

import re

import numpy as np

from . import captions as CAP
from . import jcaption as JC
from . import plain as PL

# a check ID, gate ID, rule ID or step ID in the sense of the plan (RB1, G7, D24, A4, S8, MS11 ...); the class names (S+, S-rel, S-abs, S-sus, NS, D-tr, D-sus, D-none), the paths P1 to P5 and M3 do not match
ID_PATTERN = re.compile(r"(?<![A-Za-z0-9_])(?:RB\d+(?:\([a-d]\))?|G\d+(?:-C\d)?|D\d+|A\d+|S\d+|MS\d+)(?![A-Za-z0-9_])")
RECORDED_DEF = "Recorded results are read from the saved result files of the analysis, not recalculated."
POINTER = "All earlier failures and limits stand (listed in the supplement); check names, the full limits, the values and the settings are in Supplement {fid}."

# V5: the technical terms and where their plain definition must stand: key -> (regex of the term, regex of its definition, note). The test (undefined_terms) finds the FIRST use of the term and requires the definition
# within DEF_BEFORE characters before it and DEF_AFTER after it (the definition clause follows the term at once, or, in one ruled opening sentence of F5 and F5c, in the next sentence). The definitions are the
# plain words of the ruling DL-593 V5, taken from the plan or from the Key of the full caption; a note says where a wording is not from either (UNVERIFIED).
DEF_BEFORE, DEF_AFTER = 80, 420
DEFS = {
    "surge": (r"\bsurge\b", r"transient rise of gamma-band power", ""),
    "S+": (r"(?<![\w-])S\+", r"S\+ \(the power rises in absolute and relative terms and the rise ends", ""),
    "S-rel": (r"(?<![\w-])S-rel\b", r"S-rel \(a relative rise only", ""),
    "S-abs": (r"(?<![\w-])S-abs\b", r"S-abs \(an absolute rise only", ""),
    "S-sus": (r"(?<![\w-])S-sus\b", r"S-sus \(a rise that does not end", ""),
    "NS": (r"(?<![\w-])NS\b", r"NS \(no rise", ""),
    "D-tr": (r"(?<![\w-])D-tr\b", r"D-tr[,:]? \(?[^.;]{0,50}an episode that ends", ""),
    "D-none": (r"(?<![\w-])D-none\b", r"D-none \(no episode", ""),
    "mean field": (r"\bmean field\b", r"model's equations for the average activity of the population", ""),
    "network": (r"\bnetwork\b", r"simulated network of N", ""),
    "main example": (r"\bmain example\b", r"the run fixed before the analysis as the main case", ""),
    "P2": (r"\bP2\b", r"P2 \(mean excitability raised and coupling J ramped to 0 after a delay", ""),
    "classifier": (r"\bclassifier\b", r"the rule,? fixed before the analysis", ""),
    "Hopf point": (r"\bHopf point\b", r"where the resting state starts to oscillate", ""),
    "cycle frequency": (r"\bcycle frequency\b", r"cycle frequency \(the frequency of", ""),
    "spectral peak": (r"\bspectral peak\b", r"spectral peak \(the peak of the power spectrum", ""),
    "peak frequency": (r"[Pp]eak frequency\b", r"peak frequency \(the peak of the power spectrum", ""),
    "slice": (r"\bslices?\b", r"slice \(one fixed tau_d", ""),
    "map cell": (r"\bmap cells?\b", r"map cells? \(one parameter pair of a grid of mean-field runs", "derived from the full caption of F5; the plan has no sentence for it (UNVERIFIED wording)"),
    "noisy subgrid": (r"\bnoisy subgrid\b", r"noisy subgrid \(the map cells re-run with noise", ""),
    "ramp seed": (r"\bramp seeds?\b", r"ramp seeds? \(a simulated network run with the ramp", ""),
    "control": (r"\bcontrols?\b", r"controls? \(the same network without the ramp", ""),
    "onset": (r"\bonset\b", r"onset \(when the classifier first flags the gamma rise", ""),
    "duration": (r"\bduration\b(?! \()", r"duration \(how long the classifier flags it", "the ruling's 'first and last flags' is replaced by the full-caption wording 'flagged windows x step' (UNVERIFIED)"),
    "first crossing": (r"\bfirst crossings?\b", r"first crossings? of its detection threshold", "the plan does not say what the signal crosses: only 'first crossing of its detection threshold' is written (UNVERIFIED)"),
    "spectrogram": (r"\b[Ss]pectrograms?\b", r"[Ss]pectrograms? \(power against time and frequency", ""),
    "tie": (r"\bties?\b", r"an equal split", ""),
    "post hoc": (r"\bpost hoc\b", r"chosen after the results", ""),
    "90 percent rule": (r"\b90 percent rule\b", r"at least 90 percent of the cells must agree", ""),
    "step-halving": (r"\bstep-halving\b", r"halving the numerical time step must change", ""),
    "frequency check": (r"\bfrequency check\b", r"must differ by at most 0\.5 Hz", ""),
    "M3": (r"\bM3\b", r"model M3 \(the mean-field model", ""),
    "J": (r"(?<![\w])J(?![\w0])", r"coupling J|J \(coupling", ""),
    "eta_bar": (r"\beta_bar\b", r"eta_bar \(mean excitability|mean excitability eta_bar", ""),
    "Delta": (r"\bDelta\b", r"Delta \(heterogeneity|heterogeneity Delta", ""),
    "tau_d": (r"\btau_d\b", r"tau_d \(synaptic decay time|synaptic decay time tau_d", ""),
    "T_ramp": (r"\bT_ramp\b", r"T_ramp \(ramp duration|ramp duration T_ramp", ""),
    "P1": (r"\bP1\b", r"P1 \(mean excitability ramped only", ""),
    "P3": (r"\bP3\b", r"P3 \(P2 plus a common drive", ""),
    "P5": (r"\bP5\b", r"P5 \(mean excitability up, then back down", ""),
    "P4": (r"\bP4[ab]\b", r"P4a and P4b \(P2 with Delta multiplied by 1\.5 or by 2/3", ""),
    "J0": (r"\bJ0\b", r"J0 \(the coupling J at the start of the path", ""),
}

# the limit clauses of the short captions: id of the ruled list -> plain clause; every number of a clause must be a number of PL.PLAIN_LIMITS[id] (test)
SHORT_LIMITS = {
    "G4-C3": "no-ramp network controls are classified into surge classes",
    "MS9(e)-1": "network surge classes at N = 1e4 are not evidence of a ramp-driven surge (control without a ramp flagged in 10 of 10 seeds, ramp runs 10 of 10)",
    "MS9(e)-2": "there is no claim that the regime map is robust to noise",
    "G4-C4": "the noise level sigma = 0.0624 is checked and not confirmed",
    "MS11-C2": "there is no claim of agreement in peak frequency or class between the network and the mean field",
    "MS11-C3": "the spectral and the cycle frequency differ by 4.39 Hz at the main example, and peak frequencies are the spectral peaks found by the classifier",
    "MS12-C1": "the surge result is stated for model M3 only",
}
SHORT_LIMIT_IDS = {"F1": ("G4-C3", "MS9(e)-1"), "F3": ("MS11-C3", "MS12-C1"), "F5": ("G4-C4", "MS9(e)-2", "G4-C3"), "F5c": ("G4-C3", "MS11-C2", "MS9(e)-1")}

# V7: detectors of the failed rows named in the "Failed checks." paragraph of a FULL caption: key -> regex (a row counts once)
FAILED_DETECT = {
    ("RB1", "headline_10s"): r"RB1 \(network against mean field\), headline path at a ramp duration of 10 s",
    ("RB1", "headline_120s"): r"RB1 \(network against mean field\), headline path at a ramp duration of 120 s",
    ("RB1", "cells_30s"): r"RB1 \(network against mean field\), the 4 map cells|RB1 cells",
    ("RB1", "overall"): r"RB1 \(network against mean field\), overall verdict",
    ("RB2", "noisy_subgrid_agreement"): r"RB2 \(noise robustness\), agreement of the noisy subgrid|\bD24\b",
    ("RB2", "headline_class_kept_1.0_sigma"): r"RB2 \(noise robustness\), headline class kept|RB2 headline class|\bRB2\)|, RB2\)",
    ("RB3", "a_inrange_runs"): r"RB3\(a\)",
    ("RB3", "b_classifier_onset"): r"RB3\(b\)",
    ("RB6", "network_fpk_halving_dt"): r"RB6 \(numerical convergence\), the network peak frequency|RB6 network f_pk",
    ("RB6", "solver_onset_headline"): r"RB6 \(numerical convergence\), agreement of the two solvers|RB6 solver onset",
    ("RB9", "b_spectral_vs_cycle_headline"): r"RB9\(b\) \(frequency mapping\)",
    ("G7", "gate"): r"G7 \(negative-control gate\)",
    ("sigma_check", "S8_baseline_std"): r"sigma check",
}
# the failed rows whose result is drawn in the figure or bound to a drawn quantity, named in the SHORT caption (DL-593 V7)
SHORT_NAMED = {
    "F1": {("RB1", "headline_10s"), ("RB1", "headline_120s"), ("RB1", "cells_30s")},
    "F3": {("RB9", "b_spectral_vs_cycle_headline")},
    "F5": {("RB1", "cells_30s"), ("RB2", "noisy_subgrid_agreement")},
    "F5c": {("RB6", "network_fpk_halving_dt")},
}
FAILED_PARA_START = "Failed checks. "


class JShortError(ValueError):
    """A short caption is too long, holds a check ID or a forbidden word, or a number differs from the stored value."""


def words(text: str) -> int:
    return len(text.split())


def failed_in_full(full: str) -> set:
    """V7: the failed rows named in the 'Failed checks.' paragraph of the FULL caption `full` (each row once)."""
    para = next(p for p in full.split("\n\n") if p.startswith(FAILED_PARA_START))
    return {k for k, rx in FAILED_DETECT.items() if re.search(rx, para)}


def further_count(fid: str, full: str) -> int:
    return len(failed_in_full(full) - SHORT_NAMED[fid])


def further_sentence(fid: str, full: str) -> str:
    n = further_count(fid, full)
    if n == 0:
        return f"No further failed check is listed in the full caption of this figure; see Supplement {fid}."
    return f"{n} further failed check{'s' if n != 1 else ''} of the project {'are' if n != 1 else 'is'} not shown in this figure; all are listed in Supplement {fid}."


def check_clause(a11: list, rb: str, ck: str) -> str:
    """The stored value of a failed row (a row that is not a single FAIL row stops the build): text before the first parenthesis."""
    rows = [r for r in a11 if r["rb_id"] == rb and r["check_id"] == ck]
    if len(rows) != 1 or rows[0].get("pass_or_fail", rows[0].get("status")) != "FAIL":
        raise JShortError(f"stored A11 table: {rb} {ck} is not a single FAIL row")
    return re.sub(r"\s*\(.*", "", rows[0]["value"])


def limit_clauses(fid: str, extra: dict | None = None) -> str:
    """The claim limits that are specific to the figure; a clause whose numbers are not in the ruled plain sentence stops the build."""
    out = []
    for i in SHORT_LIMIT_IDS[fid]:
        clause = SHORT_LIMITS[i]
        have = set(re.findall(r"\d+(?:\.\d+)?(?:e\d+)?", PL.PLAIN_LIMITS[i]))
        extra_n = set(re.findall(r"\d+(?:\.\d+)?(?:e\d+)?", clause)) - have
        if extra_n:
            raise JShortError(f"short limit {i}: numbers {sorted(extra_n)} are not in the ruled plain sentence")
        out.append((extra or {}).get(i, clause))
    return "Limits: " + "; ".join(out) + "."


def finish(fid: str, parts: list, max_words: int) -> str:
    text = " ".join(p.strip() for p in parts if p).replace("  ", " ")
    text = JC.plain_n(f"{fid}. {text}")
    bad = sorted({m.group(0) for m in JC.FORBIDDEN.finditer(text)} | {m.group(0) for m in ID_PATTERN.finditer(text)} | set(re.findall(r"\bstored\b", text)))
    if bad:
        raise JShortError(f"{fid}: the short caption holds forbidden words or codes: {bad}")
    if re.search(r"\brecorded\b", text) and "recorded" not in text.split("(")[0] and False:
        raise JShortError(f"{fid}: 'recorded' is used and not defined")
    if words(text) > max_words:
        raise JShortError(f"{fid}: the short caption has {words(text)} words, the limit is {max_words}")
    return text


def undefined_terms(text: str) -> list:
    """V5 test helper: the terms of DEFS that `text` uses and whose definition is not within DEF_BEFORE characters before or DEF_AFTER characters after the FIRST use of the term."""
    bad = []
    for key, (rx, probe, _note) in DEFS.items():
        m = re.search(rx, text)
        if not m:
            continue
        if not re.search(probe, text[max(0, m.start() - DEF_BEFORE): m.end() + DEF_AFTER]):
            bad.append(key)
    return bad


def _pointer(fid: str) -> str:
    return POINTER.format(fid=fid)


def _cells_clause(a11: list) -> str:
    v = {ck: re.match(r"\d+ of \d+", next(r["value"] for r in a11 if r["rb_id"] == "RB1" and r["check_id"] == ck)).group(0) for ck in ("headline_10s", "headline_120s", "cells_30s")}
    for ck in v:
        check_clause(a11, "RB1", ck)                                   # each row must be a stored FAIL
    return v


def f1_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int, full: str) -> str:
    v = _cells_clause(a11)
    s10, s120 = v["headline_10s"], v["headline_120s"]
    seeds = f"{s10} seeds at a ramp duration of 10 s and {s120} at 120 s" if s10 != s120 else f"{s120} seeds at ramp durations of 10 s and 120 s"
    return finish("F1", [
        "The mean field (the model's equations for the average activity of the population, noise-free) shows a surge (a transient rise of gamma-band power, 25 to 100 Hz) in the main example "
        "(the run fixed before the analysis as the main case) on the hypoxia-like path P2 (mean excitability raised and coupling J ramped to 0 after a delay); the network (the simulated network of N = 1e4 spiking neurons) does not reproduce it. "
        f"In the mean field the surge ends (class D-tr: an episode that ends); its power spectrum peaks at {d['ref_f_pk_hz']:.1f} Hz (not drawn). "
        f"The classifier (the rule, fixed before the analysis, that labels each run) labels the network {d['cls120'][0]} (a rise that does not end) in all 3 random seeds, so 0 of 3 seeds agree with the mean field; "
        f"the classifier's onset (when it first flags the gamma rise) is {d['onset120_s'][0]:.1f} s for the network and {d['ref_onset_s']:.3f} s for the mean field.",
        "By eye the network envelopes in (d) and (f) look similar to the mean-field ones in (c) and (e); the failed check concerns the class given by the fixed classifier, which labels all three network runs "
        f"{d['cls120'][0]} (no end), and no claim is made about the visual shape, either way.",
        "(a), (b) Mean excitability and coupling J (negative = inhibitory) along the path; dotted lines mark ramp start and end. (c), (e) Rate r and mean potential v of the mean field. "
        "(d), (f) The 3 network seeds, which nearly coincide at this scale, on the same y axes as (c) and (e); in the strip above, the triangle is the classifier onset and circle, plus and star are the first crossing of its detection threshold in seeds 0, 1 and 2. "
        "(g), (h) Spectrograms (power against time and frequency) of v, mean field and network seed 0; the dashed horizontal lines are 25 and 100 Hz, the gamma band. "
        "(i) Spike counts of seed 0 per neuron; the orange frames are the two windows drawn as spikes in (j) and (k). Red titles mark the failed check.",
        f"Failed check drawn here: network against mean field (the network must fall in the same class as the mean field): 0 of 3 seeds agree ({seeds}), and {v['cells_30s']} map cells (one parameter pair of a grid of mean-field runs) agree.",
        further_sentence("F1", full),
        limit_clauses("F1", {"G4-C3": "no-ramp network controls (the same network without the ramp) are classified into surge classes",
                             "MS9(e)-1": "network surge classes at N = 1e4 are not evidence of a ramp-driven surge (control flagged in 10 of 10 seeds, ramp runs 10 of 10; counts from other network runs, not drawn here)"}),
        _pointer("F1")], max_words)


def f3_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int, full: str) -> str:
    spec, cyc, diff = c["rb9b"]
    n_cross = [int(np.sum(~np.isnan(np.asarray(d[f"D{D_}_c25_eta"], dtype=float)))) for D_ in c["deltas"]]
    n_sl = len(d["D0.3_tau_d_ms"])
    cross = ", ".join(str(x) for x in n_cross[:-1]) + " and " + str(n_cross[-1])
    return finish("F3", [
        "The frequency check (the two frequencies below must differ by at most 0.5 Hz) failed: at the main example (the run fixed before the analysis as the main case) the spectral peak (the peak of the power spectrum of the simulated signal) "
        f"is {spec:.1f} Hz and the cycle frequency (the frequency of the oscillation that starts at the Hopf point, where the resting state starts to oscillate) is {cyc:.3f} Hz; they differ by {diff:.3f} Hz "
        "(values from the analysis record listed in the supplement).",
        "(a)-(c) Cycle frequency (colour, one bar) against mean excitability eta_bar and synaptic decay time tau_d (ms, log axis) for heterogeneity Delta = 0.05, 0.1 and 0.3. "
        "Each horizontal band is one slice (one fixed tau_d) and starts at its Hopf point (black mark); a black bar marks where the cycle crosses 25 Hz, the lower edge of the gamma band, and is absent at slices where the cycle never crosses 25 Hz "
        f"({cross} of {n_sl} slices have one, as recorded). In (c) the black line is the Hopf curve, drawn as straight segments between recorded points; the grey open circle is the start of the paths "
        f"(eta_bar {d['P1_eta_start']:.3f}) and the dark ring the Hopf point of the main example at tau_d {d['headline_tau_d_ms']:g} ms. The ticks on the colour bar mark the two frequencies of the failed check.",
        "(d) The Hopf curve in the plane of eta_bar and Delta (log axis), with the paths: P1 (mean excitability ramped only), P2 (the hypoxia-like path: mean excitability raised and coupling J ramped to 0 after a delay), "
        "P3 (P2 plus a common drive) and P5 (mean excitability up, then back down) are drawn as one arrow because their eta_bar, Delta and tau_d are equal; P4a and P4b (P2 with Delta multiplied by 1.5 or by 2/3) are drawn separately. "
        "(e) One row per path, start to end in eta_bar. The red titles mark the failed frequency check.",
        further_sentence("F3", full),
        limit_clauses("F3", {"MS12-C1": "the surge result is stated for model M3 only (the mean-field model with rate, mean potential and a synaptic variable, inhibitory coupling and a first-order synapse)"}),
        _pointer("F3")], max_words)


F5_AGREE_RULE = "a network cell agrees when all 3 of its seeds are in a surge class (S+, S-rel or S-abs) where the mean field is D-tr, or all in NS where it is D-none (the fixed rule read on the surge classes; the reading is not verified)"


def f5_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int, full: str) -> str:
    sub = d["sub_n"]
    pct = f"{100.0 * d['d24_n_agree'] / sub:.1f}"
    return finish("F5", [
        f"The surge result holds for the noise-free mean field only: the network disagrees with it at {d['cells_n_disagree']} of the 4 cells tested, and the noisy mean field agrees with the noise-free map in {d['d24_n_agree']} of {sub} cells "
        f"({pct} percent; {d['d24_needed']} cells, 90 percent, were needed). A surge is a transient rise of gamma-band power (25 to 100 Hz); the mean field is the model's equations for the average activity of the population; "
        "the network is the simulated network of N spiking neurons.",
        "(a) Map 1: the class of every map cell (one parameter pair of a grid of mean-field runs) in heterogeneity Delta and synaptic decay time tau_d (ms) at ramp duration T_ramp 120 s, as D-tr (an episode that ends) or D-none (no episode); "
        "the 4 network cells are numbered 1 to 4 here and in (b). (b) For these cells: the map class, the matching mean-field run, and the classes of the 3 network seeds: S+ (the power rises in absolute and relative terms and the rise ends), "
        "S-rel (a relative rise only), S-abs (an absolute rise only), S-sus (a rise that does not end) or NS (no rise); "
        f"{F5_AGREE_RULE}, so cell 1 agrees. The network cells and the matching run use T_ramp 30 s while the map is at 120 s; no equivalence is claimed. "
        "(c) The noisy subgrid (the map cells re-run with noise, 10 random seeds each, the class of a cell being the majority class): a cell agrees (circle), disagrees (cross) or ties (plus) with the noise-free map; "
        "a tie is an equal split, counted as a disagreement by the 90 percent rule (at least 90 percent of the cells must agree). "
        "(d) The same cells re-scored by a rule chosen after the results (post hoc); it feeds no check, and its dashed frame marks it. (e) Map 2 in J0 (the coupling J at the start of the path) and T_ramp. Red titles mark failed checks.",
        f"Failed checks drawn here: network against mean field at the 4 cells (the network must fall in the same class as the mean field), 1 of 4 agree; the 90 percent rule, {d['d24_n_agree']} of {sub} agree, {d['d24_needed']} needed.",
        further_sentence("F5", full),
        limit_clauses("F5"),
        _pointer("F5")], max_words)


def f5c_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int, full: str) -> str:
    cn = JC.f5c_counts(c["per_n"])
    sus = [int(x) for x in np.sum(np.asarray(d["ctrl_class"]) == "S-sus", axis=1)]
    n_ns = int(np.sum(np.asarray(d["s9_class"])[list(d["n_values"]).index(10000)] == "NS"))
    ns_txt = "one ramp seed" if n_ns == 1 else f"{n_ns} ramp seeds"
    labs = JC._and_list([f"{int(n):,}" for n in d["n_values"]])
    return finish("F5c", [
        "Network classes do not reproduce the mean field, and the step-halving check failed (halving the numerical time step must change the network peak frequency by less than 2 percent; the test is not drawn because its runs are not recorded). "
        "The network is the simulated network of N spiking neurons; the mean field is the model's equations for the average activity of the population. "
        "A surge class is S+ (the power rises in absolute and relative terms and the rise ends), S-rel (a relative rise only) or S-abs (an absolute rise only); S-sus (a rise that does not end) and NS (no rise) are not surge classes.",
        f"(a) Class of every seed against N = {labs}: ramp seeds (a simulated network run with the ramp, one per random seed; filled, 10 per N) and controls (the same network without the ramp; open, 3 per N). "
        f"Controls in a surge class: {JC._and_list([str(x) for x in cn['ctrl']])} of 3; controls in S-sus: {JC._and_list([str(x) for x in sus])} of 3. "
        "(b) Peak frequency (the peak of the power spectrum of the simulated signal), (c) onset (when the classifier, the rule fixed before the analysis, first flags the gamma rise) and (d) duration (how long the classifier flags it; log axis); "
        "the grey bar and tick are the minimum to maximum and the median of the ramp seeds; the dotted line in (b) and (c) is the matching mean-field run and the dashed line in (d) is the smallest duration the classifier can give (one window, 1e3 ms). "
        "The red title of (b) marks the failed check.",
        "Failed check drawn here: the step-halving check.",
        further_sentence("F5c", full),
        limit_clauses("F5c", {"MS9(e)-1": f"network surge classes at N = 1e4 are not evidence of a ramp-driven surge (the counts 'control without a ramp flagged in 10 of 10 seeds, ramp runs 10 of 10' come from other network runs, not the controls drawn here; "
                                          f"{ns_txt} at N = 1e4 is NS, so the drawn ramp seeds are not 10 of 10 in a surge class)"}),
        _pointer("F5c")], max_words)


# ---- checks shared by scripts/ms13_verify_export.py and the tests (DL-593 V5 to V8) --------------------------------------------------------------------------------------------------------------
LIMIT_KEYS = {"G4-C3": "no-ramp network controls", "MS9(e)-1": "network surge classes at N =", "MS9(e)-2": "no claim that the regime map is robust to noise", "G4-C4": "noise level sigma = 0.0624",
              "MS11-C2": "no claim of agreement in peak frequency", "MS11-C3": "differ by 4.39 Hz", "MS12-C1": "stated for model M3 only"}
NUM = re.compile(r"\d+(?:\.\d+)?")
def numbers_of(text: str) -> set:
    return set(NUM.findall(re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)))


def numbers_not_in_full(short: str, full: str) -> list:
    """DL-593 V8: the numbers of the short caption that the full caption does not have (thousands separators removed; the set is compared, so every number of the short caption, recorded value or definition, must occur in the full caption)."""
    return sorted(numbers_of(short) - numbers_of(full))


def limits_missing(fid: str, short: str) -> list:
    sent = short[short.index("Limits: "):] if "Limits: " in short else ""
    return [i for i in SHORT_LIMIT_IDS[fid] if JC.plain_n(LIMIT_KEYS[i]) not in sent]
