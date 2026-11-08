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
POINTER = "All earlier failures and limits stand (listed in the supplement); details are in Supplement {fid}."

# V5: the technical terms and where their plain definition must stand: key -> (regex of the term, regex of its definition, note). The test (undefined_terms) finds the FIRST use of the term and requires the definition
# within DEF_BEFORE characters before it and DEF_AFTER after it (the definition clause follows the term at once, or, in one ruled opening sentence of F5 and F5c, in the next sentence). The definitions are the
# plain words of the ruling DL-593 V5, taken from the plan or from the Key of the full caption; a note says where a wording is not from either (UNVERIFIED).
DEF_BEFORE, DEF_AFTER = 80, 420
DEFS = {
    "surge": (r"\bsurge\b", r"transient rise of gamma-band power", ""),
    "S+": (r"(?<![\w-])S\+", r"S\+[^;]{0,12}absolute and relative", ""),
    "S-rel": (r"(?<![\w-])S-rel\b", r"S-rel[^;]{0,12}relative", ""),
    "S-abs": (r"(?<![\w-])S-abs\b", r"S-abs[^;]{0,12}absolute", ""),
    "S-sus": (r"(?<![\w-])S-sus\b", r"S-sus[^;]{0,22}(?:does not end|no end)", ""),
    "NS": (r"(?<![\w-])NS\b", r"NS[^;]{0,6}(?:no rise|none)", ""),
    "D-tr": (r"(?<![\w-])D-tr\b", r"D-tr[^;]{0,25}ends", ""),
    "D-none": (r"(?<![\w-])D-none\b", r"D-none[^;]{0,8}(?:none|no episode)", ""),
    "mean field": (r"\bmean field\b", r"model's equations for the average activity of the population", ""),
    "network": (r"\bnetwork\b", r"(?:simulated network of N|N simulated spiking neurons)", ""),
    "main example": (r"\bmain example\b", r"the run fixed before the analysis as the main case", ""),
    "P2": (r"\bP2\b", r"P2 \((?:the )?hypoxia-like[^)]{0,40}raised|P2 \(mean excitability raised", ""),
    "classifier": (r"\bclassifier\b", r"fixed before the analysis", ""),
    "Hopf point": (r"\bHopf point\b", r"where the resting state starts to oscillate", ""),
    "cycle frequency": (r"\bcycle frequency\b", r"cycle frequency \(the frequency of", ""),
    "spectral peak": (r"\bspectral peak\b", r"spectral peak \(the peak of the power spectrum", ""),
    "peak frequency": (r"[Pp]eak frequency\b", r"peak frequency[^.;)]{0,6}(?:\(|, )the peak of (?:its|the) power spectrum", ""),
    "slice": (r"\bslices?\b", r"slice \(one fixed tau_d", ""),
    "map cell": (r"\bmap cells?\b", r"map cells? \(one parameter pair of a (?:30 x 30 )?grid of mean-field runs", "derived from the full caption of F5; the plan has no sentence for it (UNVERIFIED wording)"),
    "noisy subgrid": (r"\b[Nn]oisy subgrid\b", r"[Nn]oisy subgrid \(map cells re-run with noise", ""),
    "ramp seed": (r"\bramp seeds?\b", r"ramp seeds? \(a simulated network run with the ramp", ""),
    "control": (r"(?<!negative )(?<!negative-)\bcontrols?\b", r"controls? \(the same network without the ramp", ""),
    "negative control": (r"\bnegative controls?\b", r"negative controls? is a run in which no surge is expected|negative controls? \(a run in which no surge is expected", "our plain definition (UNVERIFIED): the plan defines the first control only"),
    "onset": (r"\bonset\b", r"onset[^.;]{0,6}\(when", ""),
    "duration": (r"\bduration\b(?! of)(?<!ramp duration)", r"duration[^.;]{0,6}\(how long", "the ruling's 'first and last flags' is replaced by the full-caption wording 'flagged windows x step' (UNVERIFIED)"),
    "first crossing": (r"\bfirst crossings?\b", r"first crossings? of its detection threshold", "the plan does not say what the signal crosses: only 'first crossing of its detection threshold' is written (UNVERIFIED)"),
    "spectrogram": (r"\b[Ss]pectrograms?\b", r"[Ss]pectrograms? \(power against time and frequency", ""),
    "tie": (r"\bties?\b", r"no single majority class", "the plan has no sentence on ties; wording from the full caption (UNVERIFIED)"),
    "post hoc": (r"\bpost hoc\b", r"chosen after the results", ""),
    "90 percent rule": (r"\b90 percent rule\b", r"at least 90 percent of the", ""),
    "step-halving": (r"\bstep-halving\b", r"halving the numerical time step must change", ""),
    "frequency check": (r"\bfrequency check\b", r"must differ by at most 0\.5 Hz", ""),
    "M3": (r"\bM3\b", r"model M3 \(the mean-field model|M3 only \(the mean-field model", ""),
    "J": (r"(?<![\w])J(?![\w0])", r"coupling J|J \(coupling", ""),
    "eta_bar": (r"\beta_bar\b", r"eta_bar \(mean excitability|mean excitability eta_bar", ""),
    "Delta": (r"\bDelta\b", r"Delta \(heterogeneity|heterogeneity Delta|Delta, the heterogeneity", ""),
    "tau_d": (r"\btau_d\b", r"tau_d \(synaptic decay time|synaptic decay time tau_d", ""),
    "T_ramp": (r"\bT_ramp\b", r"T_ramp \(ramp duration|ramp duration T_ramp", ""),
    "P1": (r"\bP1\b", r"P1 \((?:eta_bar|mean excitability) ramped only", ""),
    "P3": (r"\bP3\b", r"P3 \(P2 plus a common drive", ""),
    "P5": (r"\bP5\b", r"P5 \((?:mean excitability |eta_bar )?up, then back", ""),
    "P4": (r"\bP4[ab]\b", r"P4a, P4b \(P2 with Delta|P4a and P4b \(P2 with Delta", ""),
    "J0": (r"\bJ0\b", r"coupling J0|J0 \(", ""),
}

# the limit clauses of the short captions: id of the ruled list -> plain clause; every number of a clause must be a number of PL.PLAIN_LIMITS[id] (test)
SHORT_LIMITS = {
    "G4-C3": "no-ramp network controls are classified into surge classes",
    "MS9(e)-1": "network surge classes at N = 1e4 are not evidence of a ramp-driven surge (control without a ramp flagged in 10 of 10 seeds, ramp runs 10 of 10)",
    "MS9(e)-2": "there is no claim that the regime map is robust to noise",          # DL-603 W1: 'regime map' (13t-1f had 'maps')
    "G4-C4": "the noise level sigma = 0.0624 is checked and not confirmed",
    "MS11-C2": "there is no claim of agreement in peak frequency or class between the network and the mean field",
    "MS11-C3": "the spectral and the cycle frequency differ by 4.39 Hz at the main example, and peak frequencies are the spectral peaks found by the classifier",
    "MS12-C1": "the surge result is stated for model M3 only",
    "G4-C2": "the surge result is stated for the mean field only, and there is no claim that it is robust to finite-size fluctuations",
    "MS9(e)-3": "failure label c is a flag, not a demonstrated cause (below 25 Hz; it marks a cell without a surge class whose frequency is below 25 Hz)",
    "MS9(e)-5": "every class that depends on the test for damped against non-damped oscillations is provisional",
    # 13t-8b (DL-671 L3): the F4a and F4b clauses (the same wording as jf4cap.F4A_LIMIT_EXTRA and F4B_LIMIT_EXTRA; every number is a number of the plain sentence)
    "G6-D1": "there is no claim that the onset follows the entry-exit prediction; the onset check is not validated (0 of 6 testable in-range runs within one step of the prediction)",
    "G6-D2": "the delay of the main example is taken from the runs with a noise floor, and the noise-free onset depends on the solver (58.698 s and 58.879 s, unexplained)",
    "G6-D3": "the delay under a noise floor is reported under both onset readings (the raw crossing meets, the classifier onset gives equal delays and does not meet)",
    "DL-163-D3": "the onset check is not judged at the main example (it covers 0 to 2 of the 13 ramp durations)",
    "MS11-C6": "the direction of the change of the delay with the floor level is unresolved at ramp durations of 10 s and 316 s",
    "MS11-C1": "the main-example class is kept in 7 of 10 seeds at the noise level sigma (8 are needed); the runs without a ramp reach 7 of 10",
}
# 13t-1g (DL-603 W1): the limits G4-C3 (F5, F5c), G4-C4 (F5) and MS11-C2 (F5c) that 13t-1f (DL-596) had left out only for the word limits are restored (the limits are raised instead); the lists are those of 13t-1e (cf92272)
SHORT_LIMIT_IDS = {"F1": ("G4-C3", "MS9(e)-1"), "F3": ("MS11-C3", "MS12-C1"), "F5": ("G4-C4", "MS9(e)-2", "G4-C3"), "F5c": ("G4-C3", "MS11-C2", "MS9(e)-1"),
                   "F2": ("MS12-C1", "G4-C2"), "F6": ("MS12-C1", "MS9(e)-1", "MS9(e)-3", "MS9(e)-5", "G4-C3", "G4-C4"), "FS1": (), "FS2": (), "FS3": (),
                   "F4a": ("MS12-C1", "MS9(e)-5", "G6-D1", "G6-D2", "G6-D3", "DL-163-D3", "MS11-C6"), "F4b": ("MS12-C1", "MS9(e)-2", "MS9(e)-5", "G4-C4", "MS11-C1", "MS11-C3")}      # 13t-8b (DL-671)

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
    "F2": {("RB1", "headline_10s"), ("RB1", "headline_120s"), ("RB1", "cells_30s"), ("RB1", "overall")},      # DL-628 C1: the red title of F2 (c) is the four RB1 rows
    "F6": {("G7", "gate")},
    "FS1": set(), "FS2": set(), "FS3": set(),                                                                # 13t-4: no failed row concerns FS1
    "F4a": {("RB3", "a_inrange_runs"), ("RB3", "b_classifier_onset"), ("RB6", "solver_onset_headline")},      # 13t-8b: the three rows the F4a panels draw
    "F4b": {("RB2", "noisy_subgrid_agreement"), ("RB2", "headline_class_kept_1.0_sigma")},
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
        # DL-604 W4(e): 'of the project' next to 'no' could read as 'the project has none'
        return f"No other failed check is about this figure; the project's other failed checks are listed in Supplement {fid}."
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
        cl = (extra or {}).get(i, clause)
        if cl:
            out.append(cl)
    return "Limits: " + "; ".join(out) + "."


def finish(fid: str, parts: list, max_words: int, full: str | None = None) -> str:
    text = " ".join(p.strip() for p in parts if p).replace("  ", " ")
    text = JC.plain_n(f"{fid}. {text}")
    bad = sorted({m.group(0) for m in JC.FORBIDDEN.finditer(text)} | {m.group(0) for m in ID_PATTERN.finditer(text)} | set(re.findall(r"\bstored\b", text)))
    if bad:
        raise JShortError(f"{fid}: the short caption holds forbidden words or codes: {bad}")
    if re.search(r"\brecorded\b", text) and "recorded" not in text.split("(")[0] and False:
        raise JShortError(f"{fid}: 'recorded' is used and not defined")
    if words(text) > max_words:
        raise JShortError(f"{fid}: the short caption has {words(text)} words, the limit is {max_words}")
    if full is not None:                                              # DL-603 W2: every number of the Parameters sentence is a number of the full caption's Parameters or settings paragraph
        miss = parameters_numbers_missing(text, full)
        if miss:
            raise JShortError(f"{fid}: numbers of the Parameters sentence that the full caption's Parameters or settings paragraphs do not hold: {miss}")
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
    seeds = (f"{s120} seeds agree at ramp durations of 10 s and 120 s (the 10 s ramp is not drawn here)" if s10 == s120
             else f"{s10} seeds agree at a ramp duration of 10 s (not drawn here) and {s120} at 120 s")
    return finish("F1", [
        "The mean field (the model's equations for the average activity of the population, noise-free) shows a surge (a transient rise of gamma-band power, 25 to 100 Hz) in the main example "
        "(the run fixed before the analysis as the main case), on the hypoxia-like path P2 (mean excitability raised and coupling J ramped to 0 after a delay); the network (the simulated network of N = 1e4 spiking neurons) does not reproduce it. "
        f"In the mean field the surge ends (class D-tr: an episode that ends); its power spectrum peaks at {d['ref_f_pk_hz']:.1f} Hz (not drawn). "
        f"The classifier (a rule fixed before the analysis) labels the network {d['cls120'][0]} (a rise that does not end) in all 3 random seeds; "
        f"its onset (when it first flags the gamma rise) is {d['onset120_s'][0]:.1f} s for the network and {d['ref_onset_s']:.3f} s for the mean field.",
        "By eye the network envelopes (the minimum to the maximum of a series in each pixel column) in (d) and (f) look similar to the mean-field ones in (c) and (e); the failed check concerns the class given by the fixed classifier, which labels all three network runs "
        f"{d['cls120'][0]} (no end), and no claim is made about the visual shape, either way.",
        "(a), (b) Mean excitability and coupling J (negative = inhibitory). (c), (e) Rate r and mean potential v of the mean field. "
        "(d), (f) The 3 network seeds (nearly coincident), same y axes as (c), (e); strip above: triangle = classifier onset, circle, plus, star = first crossing of its detection threshold, seeds 0, 1, 2. "
        "(g), (h) Spectrograms (power against time and frequency) of v; dashed lines: 25 and 100 Hz, the gamma band. "
        f"(i) Spike counts of seed 0 for {d['ras_n_rows']} of the 10,000 neurons (each row is one of the {d['ras_n_rows']} recorded neurons; the rows are not labelled; 1 s bins); an orange solid line and an orange dashed line mark the two windows shown in (j) and (k) (orange frames). (j), (k) The spikes of seed 0 (the same {d['ras_n_rows']} neurons as in (i); the rows are not labelled) in 1 s windows that start at the classifier onset (12.000 s) and at the mean-field onset (58.698 s).",
        # DL-603 W2: values copied from the Parameters and settings paragraphs of the full caption (numbers_missing is checked in finish); t_on is read as the ramp start (reviewer's wording, UNVERIFIED)
        "Parameters: model M3 (the mean-field model) with J = -21, heterogeneity Delta = 0.3, synaptic decay time tau_d = 5 ms and membrane time constant 10 ms; ramp duration 120 s, starting at 5 s; "
        "network N = 10,000; classifier window 2 s, step 1 s, gamma band 25 to 100 Hz; noise level sigma = 0.0624 (checked, not confirmed; its check failed).",
        f"Failed check (red titles): network against mean field (same class required): {seeds}, and {v['cells_30s']} map cells (one parameter pair of a grid of mean-field runs; not drawn here) agree.",
        further_sentence("F1", full),
        limit_clauses("F1", {"G4-C3": "no-ramp network controls (the same network without the ramp) are classified into surge classes",
                             "MS9(e)-1": "network surge classes at N = 1e4 are not evidence of a ramp-driven surge (control flagged in 10 of 10 seeds, ramp runs 10 of 10; other network runs, not drawn)"}),
        _pointer("F1")], max_words, full)


def band_end_short(c: dict) -> str:
    """DL-645 G1: the band-end sentence of the F3 SHORT caption, with the count of bands that end before eta_bar 8.0."""
    bands = c.get("bands")
    if not bands:
        raise JC.JCaptionError("F3: the band ends are not available (DL-645 G1)")
    n = sum(e < 8.0 for _, _, e in bands)
    return f"Each band ends at the last recorded eta_bar of its cycle branch; the reason is not recorded; {n} of the {len(bands)} bands end before eta_bar 8.0; the full list is in Supplement F3."


def f3_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int, full: str) -> str:
    spec, cyc, diff = c["rb9b"]
    n_cross = [int(np.sum(~np.isnan(np.asarray(d[f"D{D_}_c25_eta"], dtype=float)))) for D_ in c["deltas"]]
    n_sl = len(d["D0.3_tau_d_ms"])
    cross = ", ".join(str(x) for x in n_cross[:-1]) + " and " + str(n_cross[-1])
    return finish("F3", [
        "The frequency check (the two frequencies below must differ by at most 0.5 Hz) failed (red titles): in the main example (the run fixed before the analysis as the main case) the spectral peak (the peak of the power spectrum of the simulated signal) "
        f"is {spec:.1f} Hz and the cycle frequency (the frequency of the oscillation that starts at the Hopf point, where the resting state starts to oscillate) is {cyc:.3f} Hz; they differ by {diff:.3f} Hz "
        "(values from the analysis record listed in the supplement).",
        "(a)-(c) Cycle frequency (colour) against mean excitability eta_bar and synaptic decay time tau_d (ms, log axis) for heterogeneity Delta = 0.05, 0.1, 0.3. "
        "Each band is one slice (one fixed tau_d) from its Hopf point (black mark); a black bar marks where the cycle crosses 25 Hz (the lower edge of the gamma band, 25 to 100 Hz) and is absent where it never does "
        f"({cross} of {n_sl} slices have one, as recorded). {band_end_short(c)} In (c) the line is the Hopf curve, straight segments between recorded points; the grey open circle is the start of the paths "
        f"(eta_bar {d['P1_eta_start']:.3f}), the dark ring the Hopf point of the main example at tau_d {d['headline_tau_d_ms']:g} ms; (a) and (b) are the same frequency map at other Delta; the failed check was made at the main example in (c) and bears on them too.",
        "(d) Hopf curve against eta_bar and Delta (log axis), with the paths P1 (eta_bar ramped only), P2 (hypoxia-like: eta_bar raised, coupling J ramped to 0 after a delay), "
        "P3 (P2 plus a common drive) and P5 (up, then back), drawn as one arrow because their eta_bar, Delta and tau_d are equal; P4a, P4b (P2 with Delta multiplied by 1.5 or 2/3) are separate. The paths coincide in (c) and (d) because they differ in J, drive or time course, which these planes do not show. (e) One row per path leg (P5 has an up row and a return row).",
        # DL-603 W2: values copied from the Parameters paragraph of the full caption; the M3 gloss moved here from the limit clause (first use); no classifier or spectrogram is used (settings paragraph)
        "Parameters: model M3 (the mean-field model with rate, mean potential and a synaptic variable) with membrane time constant 10 ms and J = -21; Delta = 0.05, 0.1 and 0.3; "
        "tau_d = 1 to 50 ms (9 values); no classifier (a rule fixed before the analysis) or spectrogram (power against time and frequency) is used.",
        further_sentence("F3", full),
        limit_clauses("F3", {"MS11-C3": "the two frequencies differ by 4.39 Hz at the main example, and peak frequencies are spectral peaks",
                             "MS12-C1": "the gamma-band result is stated for model M3 only"}),
        _pointer("F3")], max_words, full)


F5_AGREE_RULE = ("a network cell agrees when all 3 seeds are in a surge class (S+: absolute and relative rise, ending; S-rel: relative only; S-abs: absolute only) where the mean field is D-tr, "
                 "or in NS (no rise) where it is D-none (our reading, not verified); S-sus (a rise that does not end) is not a surge class")          # DL-604 W4(b): S-sus is on the image and is defined here


def f5_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int, full: str) -> str:
    sub = d["sub_n"]
    pct = f"{100.0 * d['d24_n_agree'] / sub:.1f}"
    return finish("F5", [
        f"The surge result holds for the noise-free mean field only: the network disagrees with it at {d['cells_n_disagree']} of the 4 cells tested, and the noisy mean field agrees with the noise-free map in {d['d24_n_agree']} of {sub} cells "
        f"({pct} percent; {d['d24_needed']} cells, 90 percent, were needed). Surge: a transient rise of gamma-band power (25 to 100 Hz); mean field: the model's equations for the average activity of the population; "
        "network: N simulated spiking neurons.",
        "(a) Map 1: class of each map cell (one parameter pair of a 30 x 30 grid of mean-field runs in heterogeneity and synaptic decay time) at ramp duration 120 s: D-tr (an episode that ends) or D-none (none); "
        "the 4 network cells are numbered 1 to 4 here and in (b). "
        f"(b) Map class, matching mean-field run and network seed classes; {F5_AGREE_RULE}; cell 1 agrees. Network cells and matching run: ramp duration 30 s (map: 120 s); no equivalence is claimed. "
        # DL-604 W4(c): the tie clause in the words of the full caption ('majority class of 10 seeds', 'ties count as disagreements by the rule'); the plan has no sentence on ties, so 'no single majority class' is UNVERIFIED wording
        "(c) Noisy subgrid (map cells re-run with noise, 10 seeds each): agree (circle), disagree (cross) or tie (plus: no single majority class among the 10 seeds of the cell; it counts as a disagreement "
        "under the 90 percent rule: at least 90 percent of the cells must agree). "
        f"(d) The same cells re-scored by a rule chosen after the results (post hoc; no check; dashed frame): the same cells agree in {d['p1_n_agree']} of {sub} ({100.0 * d['p1_n_agree'] / sub:.1f} percent) under the re-scoring chosen after the results; it feeds no check; "
        "the blank lines through (c) and (d) are map cells that are not in the noisy subgrid. (e) Map 2: initial coupling J0 and ramp duration.",
        # DL-603 W2: values copied from the Parameters and settings paragraphs of the full caption (the classifier window depends on the ramp duration: 2 s and 1 s from 60 s up)
        "Parameters: model M3 (the mean-field model) with membrane time constant 10 ms and coupling J = -21; map 1: heterogeneity Delta 0.01 to 0.6 (30 values), synaptic decay time tau_d 1 to 50 ms (30 values), ramp duration 120 s; "
        "map 2: J0 -40 to -5 (25 values), 13 ramp durations, Delta 0.3, tau_d 5 ms; network cells: ramp duration 30 s; "
        "classifier (fixed before the analysis) window 2 s, step 1 s for ramp durations of 60 s or more (shorter ramps use a shorter window), gamma band 25 to 100 Hz; noise level sigma = 0.0624 (its check failed).",
        "Failed checks (red titles): network against mean field at the 4 cells (same class required) and the 90 percent rule.",
        further_sentence("F5", full),
        limit_clauses("F5", {"G4-C3": "no-ramp network controls (the same network without the ramp) are classified into surge classes"}),
        _pointer("F5")], max_words, full)


def f5c_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int, full: str) -> str:
    cn = JC.f5c_counts(c["per_n"])
    sus = [int(x) for x in np.sum(np.asarray(d["ctrl_class"]) == "S-sus", axis=1)]
    n_ns = int(np.sum(np.asarray(d["s9_class"])[list(d["n_values"]).index(10000)] == "NS"))
    ns_txt = "one ramp seed" if n_ns == 1 else f"{n_ns} ramp seeds"
    on = np.asarray(d["s9_onset_s"], dtype=float)
    n_on = int(np.sum(~np.isnan(on)))
    if n_on != int(np.sum(on < d["ref_onset_s"])):
        raise JShortError("F5c: a drawn ramp-seed onset is not earlier than the mean-field onset (DL-615 A5 stop)")
    onset_clause = f"all {n_on} drawn ramp-seed onsets ({np.nanmin(on):.1f} to {np.nanmax(on):.1f} s) are earlier than the mean-field onset ({d['ref_onset_s']:.3f} s)"
    con = np.asarray(d["ctrl_onset_s"], dtype=float)
    cls_all = np.concatenate([np.asarray(d["s9_class"]).ravel(), np.asarray(d["ctrl_class"]).ravel()])
    if np.any(cls_all == "S-rel") or np.asarray(d["ctrl_class"]).shape[1] != 3 or not np.isfinite(con).any():
        raise JShortError("F5c: a seed is S-rel, or the controls are not 3 per N (DL-628 C5 stop)")
    ctrl_clause = (f"no seed is S-rel; 3 control seeds per N is a small sample; the controls also flag onsets from {np.nanmin(con):.1f} to {np.nanmax(con):.1f} s, so onset is not a ramp-specific signal in this figure; "
                   "the plotted peak frequencies come from runs whose step-halving check failed, so they are not shown to be converged")
    labs = JC._and_list([f"{int(n):,}".replace(",", "") if int(n) < 10000 else f"{int(n):,}" for n in d["n_values"]])
    n_ctrl_pk = JC._and_list([str(int(np.sum(np.isfinite(np.asarray(d["ctrl_f_pk_hz"], dtype=float)[k])))) for k in range(len(d["n_values"]))])
    ctrl_drawn = f"Control seeds are drawn only where their value is defined: {n_ctrl_pk} of 3 at N = {labs} in (b) and (c), and none in (d)"
    return finish("F5c", [
        "Network classes do not reproduce the mean field (the mean-field classes are not drawn in this figure), and the step-halving check failed (halving the numerical time step must change the network peak frequency, the peak of its power spectrum, by less than 2 percent; its runs are not recorded, so not drawn). "
        "Network: N simulated spiking neurons; mean field: the model's equations for the average activity of the population. "
        "Surge classes (a surge is a transient rise of gamma-band power, 25 to 100 Hz) are S+ (absolute and relative rise, ending), S-rel (relative rise only) and S-abs (absolute rise only); "
        "S-sus (a rise that does not end) is not.",
        f"(a) Class of every seed against N (N = {labs}): ramp seeds (a simulated network run with the ramp, one per random seed; filled, 10 per N) and controls (the same network without the ramp; open, 3 per N). "
        f"Controls in a surge class: {JC._and_list([str(x) for x in cn['ctrl']])} of 3; controls in S-sus: {JC._and_list([str(x) for x in sus])} of 3. "
        "(b) Peak frequency, (c) onset (when the classifier, a rule fixed before the analysis, first flags the gamma rise) and (d) duration (how long it flags it; log axis); "
        "grey bar and tick: range and median of the ramp seeds; dotted line in (b), (c): the matching mean-field run; dashed line in (d): the smallest duration the classifier can give (recorded minimum, 1e3 ms). "
        f"{ctrl_drawn}. In (c), {onset_clause}. Failed check (red title of (b)): the step-halving check; a seed on the dotted line is not evidence of agreement (the check of this panel failed). {ctrl_clause[0].upper() + ctrl_clause[1:]}.",
        # DL-603 W2: values copied from the Parameters and settings paragraphs of the full caption
        f"Parameters: model M3 (the mean-field model) with membrane time constant 10 ms, coupling J = -21, heterogeneity Delta = 0.3 and synaptic decay time tau_d = 5 ms; ramp duration 60 s; "
        f"network size N = {labs}; classifier window 2 s, step 1 s, gamma band 25 to 100 Hz; noise level sigma = 0.0624 (checked, not confirmed; its check failed).",
        further_sentence("F5c", full),
        limit_clauses("F5c", {"MS9(e)-1": f"network surge classes at N = 1e4 are not evidence of a ramp-driven surge (the counts 'control flagged in 10 of 10 seeds, ramp runs 10 of 10' come from other network runs, not the controls drawn here; "
                                                       f"{ns_txt} at N = 1e4 is NS (no rise), so the drawn ramp seeds are not 10 of 10 in a surge class)"}),
        _pointer("F5c")], max_words, full)


# ---- checks shared by scripts/ms13_verify_export.py and the tests (DL-593 V5 to V8) --------------------------------------------------------------------------------------------------------------
LIMIT_KEYS = {"G4-C3": "no-ramp network controls", "MS9(e)-1": "network surge classes at N =", "MS9(e)-2": "no claim that the regime map is robust to noise", "G4-C4": "noise level sigma = 0.0624",
              "MS11-C2": "no claim of agreement in peak frequency", "MS11-C3": "differ by 4.39 Hz", "MS12-C1": "stated for model M3 only", "G4-C2": "stated for the mean field only", "MS9(e)-3": "is a flag, not a demonstrated cause",
              "MS9(e)-5": "is provisional", "G6-D1": "no claim that the onset follows the entry-exit prediction", "G6-D2": "the noise-free onset depends on the solver",
              "G6-D3": "reported under both onset readings", "DL-163-D3": "not judged at the main example", "MS11-C6": "is unresolved at ramp durations of 10 s and 316 s",
              "MS11-C1": "the runs without a ramp reach 7 of 10"}
NUM = re.compile(r"\d+(?:\.\d+)?")
def numbers_of(text: str) -> set:
    return set(NUM.findall(re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)))


def numbers_not_in_full(short: str, full: str) -> list:
    """DL-593 V8: the numbers of the short caption that the full caption does not have (thousands separators removed; the set is compared, so every number of the short caption, recorded value or definition, must occur in the full caption)."""
    return sorted(numbers_of(short) - numbers_of(full))


PARAM_RX = re.compile(r"Parameters: .*?\.(?=\s|$)")


def parameters_sentence(short: str) -> str:
    """DL-603 W2: the one 'Parameters:' sentence of a short caption (up to the first full stop that is followed by a space or the end; decimals do not end it); '' if absent."""
    m = PARAM_RX.search(short)
    return m.group(0) if m else ""


def full_settings_text(full: str) -> str:
    """DL-603 W2: the 'Parameters.' and the 'Classifier and spectrogram settings.' paragraphs of a FULL caption (the only source of the values of the short Parameters sentence)."""
    paras = [p for p in full.split("\n\n") if p.startswith("Parameters. ") or p.startswith("Classifier and spectrogram settings. ")]
    if len(paras) != 2:
        raise JShortError(f"the full caption has {len(paras)} of the 2 paragraphs 'Parameters.' and 'Classifier and spectrogram settings.'")
    return "\n\n".join(paras)


def parameters_numbers_missing(short: str, full: str) -> list:
    """DL-603 W2 test: the numbers of the short Parameters sentence that the Parameters and settings paragraphs of the full caption do not hold (empty list = all there; a missing sentence is reported)."""
    sent = parameters_sentence(short)
    if not sent:
        return ["no 'Parameters:' sentence"]
    return sorted(numbers_of(sent) - numbers_of(full_settings_text(full)))


def limits_missing(fid: str, short: str) -> list:
    sent = short[short.index("Limits: "):] if "Limits: " in short else ""
    return [i for i in SHORT_LIMIT_IDS[fid] if JC.plain_n(LIMIT_KEYS[i]) not in sent]
