"""MS13 13t-1d (DL-571 T8): the journal caption as short labelled paragraphs, written for a reader who has never seen the project.

The draft caption is built as before (captions.build_caption) and keeps its ruled wording, its decision-log numbers and its ruling codes; nothing in the drafts or in the ruled texts is
changed. The JOURNAL caption is built here, from the same prepared data and the stored tables, in seven paragraphs: the take-home (sentence 1 names the main failure), one sentence per
panel, key and abbreviations, classifier and spectrogram settings, parameters, failed checks, limits. It has no reference to the plan, a milestone, a table number, a decision-log
number, a step ID (S8, A4, A6, A9, A11 ...) or a code or key name; those go to the supplement sheet (plain.pairing_markdown and the parameter table). Every number is read from the
prepared data or from a stored table; only the wording is typed here. Checks that a caption is clean: FORBIDDEN (below), tests/test_ms13_13t.py.
"""
from __future__ import annotations

import re

import numpy as np

from . import captions as CAP

LABELS = ("Panels.", "Key and abbreviations.", "Classifier and spectrogram settings.", "Parameters.", "Failed checks.", "Limits.")

# words and codes that must not occur in a journal caption (DL-571 T8 (b), (c)); the check is case-sensitive except where noted
FORBIDDEN = re.compile(r"\bthe plan\b|\bplan\b|\bPlan\b|\bmilestone\b|\bMilestone\b|\bTable \d|DL-\d+|\bS(?:\d+)\b|\bA(?:\d+)\b|\bMS\d+|\bG\d-[CD]\d|\bDL\b|\b[a-z]+\.[a-z_]+\.[a-z_]+\b|"
                       r"\bpath_[a-z]+\b|\bref_[a-z]+\b|\bDOP853\b|\b[a-z]+\.[a-z_]*tau_d_ms\b|\bseeds\.root_seed\b|\bmodel\.[A-Za-z_]+\b|\bsolver\.[a-z_]+\b|\bnetwork\.[a-z_]+\b|\bnoise\.[a-z_]+\b|"
                       r"\bUNVERIFIED\b|\bms10_eval\b|\bNC1\b|\bD8\b")


PLAIN_N = {"1e3": "1000", "3e3": "3000", "1e4": "10,000", "3e4": "30,000"}


def plain_n(text: str) -> str:
    """DL-592 V4: the network sizes are written 1000, 3000, 10,000 and 30,000 in every caption (only the notation changes, not a number)."""
    return re.sub(r"(?<![\w.+-])(1e3|3e3|1e4|3e4)(?![\w])", lambda m: PLAIN_N[m.group(1)], text)


class JCaptionError(ValueError):
    """The journal caption holds a forbidden word or code, or a stored value differs from the value that the wording needs."""


def assemble(fig_id: str, *, take_home: str, panels: str, key: str, settings: str, parameters: str, failed: str, limits: str) -> str:
    """The seven paragraphs, separated by a blank line: '<ID>. <take-home>', then one labelled paragraph each (LABELS)."""
    paras = [f"{fig_id}. {take_home.strip()}", f"Panels. {panels.strip()}", f"Key and abbreviations. {key.strip()}", f"Classifier and spectrogram settings. {settings.strip()}",
             f"Parameters. {parameters.strip()}", f"Failed checks. {failed.strip()}", f"Limits. {limits.strip()}"]
    text = plain_n("\n\n".join(paras))
    bad = sorted({m.group(0) for m in FORBIDDEN.finditer(text)})
    if bad:
        raise JCaptionError(f"{fig_id}: the journal caption holds forbidden words or codes: {bad}")
    return text


def paragraphs(text: str) -> list:
    return text.split("\n\n")


# ---- plain names of the checks (plan Table 7.2 names the robustness checks; the names of the individual rows are those of the stored table, in words) ----------------------------------

CHECK_NAMES = {
    ("RB1", "headline_10s"): "RB1 (network against mean field), headline path at a ramp duration of 10 s",
    ("RB1", "headline_120s"): "RB1 (network against mean field), headline path at a ramp duration of 120 s",
    ("RB1", "cells_30s"): "RB1 (network against mean field), the 4 map cells at a ramp duration of 30 s",
    ("RB1", "overall"): "RB1 (network against mean field), overall verdict",
    ("RB2", "noisy_subgrid_agreement"): "RB2 (noise robustness), agreement of the noisy subgrid with the noise-free map (rule D24)",
    ("RB2", "headline_class_kept_1.0_sigma"): "RB2 (noise robustness), headline class kept at the noise level sigma",
    ("RB3", "a_inrange_runs"): "RB3(a) (ramp rate), the onset prediction on the testable in-range runs",
    ("RB3", "b_classifier_onset"): "RB3(b) (ramp rate), the delay under a noise floor, classifier onset reading",
    ("RB6", "network_fpk_halving_dt"): "RB6 (numerical convergence), the network peak frequency f_pk when the step is halved",
    ("RB6", "solver_onset_headline"): "RB6 (numerical convergence), agreement of the two solvers on the headline onset",
    ("RB9", "b_spectral_vs_cycle_headline"): "RB9(b) (frequency mapping), spectral frequency against cycle frequency at the headline",
    ("G7", "gate"): "G7 (negative-control gate)",
    ("sigma_check", "S8_baseline_std"): "sigma check (baseline standard deviation of the headline network runs)",
}
BLANK_WHY = {("RB1", "overall"): "value blank in the stored table: it is the verdict over its three parts (headline, cells, ramp-duration rule), which are in the note column of the stored table; no single threshold"}


def failed_line(r: dict) -> str:
    """One failed check in plain words, from a stored A11 row (keys rb_id, check_id, status, value, threshold): '<name>: <status> (<value>; threshold <threshold>)'. A blank value or threshold is said to be blank."""
    key = (r["rb_id"], r["check_id"])
    name = CHECK_NAMES[key]
    why = BLANK_WHY.get(key)
    if why:
        return f"{name}: {r['status']} ({why})"
    val = r["value"] or "value blank in the stored table"
    thr = f"threshold {r['threshold'].replace('1/W', 'the inverse of the window length')}" if r["threshold"] else "threshold blank in the stored table"
    gloss = " (n failed = failed runs among the seeds, counted as not kept)" if "failed)" in str(r["value"]) else ""
    return f"{name}: {r['status']} ({val}; {thr}){gloss}"


SIGMA_NOTE = re.compile(r"mean-field baseline std ([0-9.]+) against the network range \[([0-9.eE+-]+), ([0-9.eE+-]+)\]")


def sigma_status(a11: list) -> dict:
    """DL-571 T2: the stored status of the sigma check, read from the stored A11 table (rb_id sigma_check, check_id S8_baseline_std); a row that is not FAIL / NOT INSIDE or a note without the three numbers stops the build."""
    rows = [r for r in a11 if r["rb_id"] == "sigma_check" and r["check_id"] == "S8_baseline_std"]
    if len(rows) != 1:
        raise JCaptionError(f"stored A11 table: {len(rows)} rows for sigma_check S8_baseline_std")
    r = rows[0]
    m = SIGMA_NOTE.search(r["note"])
    if r["pass_or_fail"] != "FAIL" or r["logged_verdict"] != "NOT INSIDE" or m is None:
        raise JCaptionError(f"stored sigma_check row is {r['pass_or_fail']!r} / {r['logged_verdict']!r}, note {r['note']!r}: STOP and report")
    return {"status": r["pass_or_fail"], "verdict": r["logged_verdict"], "mf_std": float(m.group(1)), "lo": float(m.group(2)), "hi": float(m.group(3)), "row": r}


def sigma_text(a11: list, value) -> str:
    """DL-571 T2: 'noise level sigma = <stored value> (checked, not confirmed; sigma check on the baseline standard deviation: FAIL, logged verdict NOT INSIDE; <the three stored numbers>)'."""
    s = sigma_status(a11)
    return (f"noise level sigma = {CAP.number_text(value)} (checked, not confirmed; sigma check on the baseline standard deviation: {s['status']}, logged verdict {s['verdict']}; mean-field baseline std {s['mf_std']:.6f} "
            f"against the network range {s['lo']:.6f} to {s['hi']:.6f})")


def rb3a_value(a11: list) -> str:
    rows = [r for r in a11 if r["rb_id"] == "RB3" and r["check_id"] == "a_inrange_runs"]
    if len(rows) != 1 or rows[0]["pass_or_fail"] != "FAIL":
        raise JCaptionError("stored A11 table: RB3 a_inrange_runs is not a single FAIL row")
    m = re.match(r"(\d+) of (\d+) testable in-range runs", rows[0]["value"])
    if m is None:
        raise JCaptionError(f"RB3 a_inrange_runs value {rows[0]['value']!r}")
    return f"{m.group(1)} of {m.group(2)}"


def all_fail_rows(a11: list) -> str:
    """DL-604 W4(e): Markdown table of EVERY row of the stored A11 table with the status FAIL (verbatim: step IDs and ruling codes included; read-only), for the F3 supplement, which the F3 short caption names as the place
    of the project's other failed checks. Rows with another status (NOT EVALUABLE) are not failed checks and are not listed here."""
    out = ["| row (rb_id check_id) | status | logged verdict | value | threshold | stored note | decision-log source |", "|---|---|---|---|---|---|---|"]
    n = 0
    for r in a11:
        if r["pass_or_fail"] == "FAIL":
            n += 1
            out.append(f"| {r['rb_id']} {r['check_id']} | {r['pass_or_fail']} | {r['logged_verdict']} | {r['value'] or 'blank'} | {r['threshold'] or 'blank'} | {r['note']} | {r['source']} |".replace("\n", " "))
    out += ["", f"{n} FAIL rows in the stored A11 table (results/A11/a11_robustness.csv), all are checks of the project, not recomputed. Only the frequency check (RB9(b)) is about this figure; "
            "its stored value is blank, and the values 49.0 Hz, 44.609 Hz and 4.391 Hz come from the decision log (DL-388)."]
    return "\n".join(out)


def all_fail_rows_for(a11: list, about: str) -> str:
    """DL-616 B3: the Markdown table of EVERY row of the stored A11 table with the status FAIL (as all_fail_rows, read-only), for the supplement of a figure whose short caption points to it; `about` says which of the rows concern the figure."""
    out = ["| row (rb_id check_id) | status | logged verdict | value | threshold | stored note | decision-log source |", "|---|---|---|---|---|---|---|"]
    n = 0
    for r in a11:
        if r["pass_or_fail"] == "FAIL":
            n += 1
            out.append(f"| {r['rb_id']} {r['check_id']} | {r['pass_or_fail']} | {r['logged_verdict']} | {r['value'] or 'blank'} | {r['threshold'] or 'blank'} | {r['note']} | {r['source']} |".replace("\n", " "))
    out += ["", f"{n} FAIL rows in the stored A11 table (results/A11/a11_robustness.csv), all are checks of the project, not recomputed. {about}"]
    return "\n".join(out)


def supplement_rows(a11: list) -> str:
    """Markdown for the supplement sheet (DL-571 T2): the two stored FAIL rows that the status strips do not list, verbatim from the stored A11 table (step IDs and ruling codes included)."""
    out = ["| row (rb_id check_id) | status | logged verdict | value | threshold | stored note | decision-log source |", "|---|---|---|---|---|---|---|"]
    for rb, ck in (("sigma_check", "S8_baseline_std"), ("RB3", "a_inrange_runs")):
        rows = [r for r in a11 if r["rb_id"] == rb and r["check_id"] == ck]
        if len(rows) != 1:
            raise JCaptionError(f"stored A11 table: {len(rows)} rows for {rb} {ck}")
        r = rows[0]
        out.append(f"| {rb} {ck} | {r['pass_or_fail']} | {r['logged_verdict']} | {r['value'] or 'blank'} | {r['threshold'] or 'blank'} | {r['note']} | {r['source']} |")
    out += ["", "Verbatim form of the sigma status as ruled (DL-571 T2): 'sigma check (S8 baseline std): FAIL, logged verdict NOT INSIDE (mean-field baseline std 0.039522 against the network range 0.037989 to 0.038920)'; "
            "the ruled wording 'checked, not confirmed (G4-C4)' stands beside it."]
    return "\n".join(out)


# ---- common key texts ----------------------------------------------------------------------------------------------------------------------------------------------------------------

def class_key() -> str:
    """The class definitions of the surge definition, verbatim (G1), without the source label: the classes describe the gamma-band (25 to 100 Hz) power of the signal."""
    return ("Classes (they describe the power of the signal in the gamma band, 25 to 100 Hz): " + CAP.TABLE_2_1_MODE_N + " " + CAP.TABLE_2_1_MODE_D + " " + CAP.TABLE_2_1_SURGE + " "
            + CAP.TABLE_2_1_AGREE + ".")


SYMBOLS = {
    "eta": "eta_bar = mean excitability",
    "Delta": "Delta = heterogeneity half-width",
    "J": "J = signed coupling (negative: inhibitory)",
    "tau_d": "tau_d = synaptic decay time",
    "tau": "tau = membrane time constant",
    "r": "r = population firing rate",
    "v": "v = mean membrane potential (model units)",
    "t_on": "t_on = time at which the ramp starts",
    "T_ramp": "T_ramp = ramp duration",
    "N": "N = number of neurons of the network",
    "PSD": "PSD = power spectral density",
    "M3": "M3 = the mean-field model with rate r, mean potential v and a synaptic variable, inhibitory coupling (J < 0) and a first-order synapse, read as an inhibition-dominated local circuit",
    "modes": "mode D = the noise-free (deterministic) mean field, mode N = the noisy runs",
    "W": "W = the window length of the classifier",
    "f_pk": "f_pk = the classifier's spectral peak frequency",
    "NC1": "the first negative control = the hypoxia path with the mean excitability falling by the same amount, with coupling, heterogeneity and synaptic decay fixed and no common drive",
}

CHECK_IDS = {
    "RB1": "RB1 = network against mean field",
    "RB2": "RB2 = noise robustness",
    "RB3": "RB3 = ramp rate (part (a): the onset prediction on the testable in-range runs; part (b): the delay under a noise floor)",
    "RB4": "RB4 = parameter perturbation",
    "RB6": "RB6 = numerical convergence",
    "RB8": "RB8 = model variants",
    "RB9": "RB9(b) = frequency mapping, part (b): spectral against cycle frequency",
    "G4": "G4 = the gate for network against mean field",
    "G5": "G5 = the fine-tuning gate",
    "G7": "G7 = the negative-control gate",
    "D24": "D24 = the rule that at least 90% of the cells of the noisy subgrid agree with the noise-free class",
    "P-1": "P-1 = a post-hoc view that counts the ramp-linked classes S+, S-abs and S-sus as matching D-tr and the other classes as matching D-none (it feeds no gate)",
}


def defined_checks(text: str) -> str:
    """The definitions of the check, gate and rule IDs that occur in `text` (the other paragraphs of the caption), once each."""
    used = []
    for k, v in CHECK_IDS.items():
        pat = {"RB9": r"RB9\(b\)", "RB3": r"RB3"}.get(k, re.escape(k))
        if re.search(r"(?<![\w-])" + pat + r"(?![\w])", text):
            used.append(v)
    return "; ".join(used)


# ---- DL-581 U2, DL-582 U5, U6: the Key keeps only the terms that the same caption uses; words defined once; the plain titles of the image; the scope of two limit statements ---------------

SYM_TERMS = {"eta": r"eta_bar", "Delta": r"\bDelta\b", "J": r"\bJ\b", "tau_d": r"\btau_d\b", "tau": r"\btau\b", "r": r"\br\(t\)|\br\b", "v": r"\bv\(t\)|\bv\b", "t_on": r"\bt_on\b",
             "T_ramp": r"\bT_ramp\b", "N": r"\bN\b", "PSD": r"\bPSD\b", "M3": r"\bM3\b", "modes": r"\bmode [DN]\b", "W": r"\bW\b", "f_pk": r"\bf_pk\b", "NC1": r"\bnegative control\b"}

# U5: words defined once in the Key of the FULL caption, in plain words; an entry is included only if its term is used elsewhere in the same caption
WORD_ENTRIES = (
    (r"\bstored\b", "Stored (in plain words: recorded) = read from the saved result files of the analysis, not recalculated for this figure; a value that is recomputed here is said so where it occurs."),
    (r"\bheadline\b", "Headline = the main example run (the hypoxia-like path with a ramp duration of 120 s)."),
    (r"\bsigma\b", "Sigma = the amplitude of the additive white noise on v in the noisy mean-field runs, stated as phenomenological and calibrated so that the baseline standard deviation of v matches "
                   "that of one network baseline run at N = 1e4."),
)


# the other Key entries that exist only if their term is used in the same caption (DL-582 U5): name -> (term regex, text)
EXTRA_ENTRIES = {
    "eta_H": (r"\beta_H\b", "eta_H = the lowest Hopf crossing of eta_bar along the path."),
    "P2": (r"\bP2\b", "P2 = the hypoxia-like path: eta_bar ramped up, with J ramped to 0 after a delay."),
    "F4": (r"\bF4\b|\bFS4\b", "F4 and FS4 = other figures of this paper."),
    "NC1": (r"negative.control", "The first negative control, the subject of G7, is the hypoxia path with the mean excitability falling by the same amount, with coupling, heterogeneity and synaptic decay fixed and no common drive."),
    "J0": (r"\bJ0\b", "J0 = the J at which the path starts (map 2)."),
    "ij": (r"\bi and j\b|\bcell index\b", "i and j = the row and column index of a map-1 cell."),
    "F5c_F6": (r"\bF5c\b|\bF6\b", "F5c and F6 = other figures of this paper."),
}


def key_unused_terms(text: str) -> list:
    """DL-582 U5 test: the Key entries (symbols, M3 and the modes, words, the extra entries) whose definition is in the Key paragraph of the full caption `text` but whose term the other paragraphs do not use."""
    paras = text.split("\n\n")
    key = next(p for p in paras if p.startswith("Key and abbreviations. "))
    rest = "\n\n".join(p for p in paras if p is not key)
    low = key.lower()
    out = []
    for k, defin in SYMBOLS.items():
        if k in SYM_TERMS and defin.lower() in low and not re.search(SYM_TERMS[k], rest):
            out.append(k)
    for pat, defin in WORD_ENTRIES:
        if defin in key and not re.search(pat, rest):
            out.append(pat)
    for k, (pat, defin) in EXTRA_ENTRIES.items():
        if defin in key and not re.search(pat, rest):
            out.append(k)
    return out


def key_symbols(rest: str, *keys) -> str:
    """'Symbols: ...' for the symbols of `keys` that `rest` (the other paragraphs of the caption) uses, M3 and the modes as their own sentences; '' if none."""
    sy = [SYMBOLS[k] for k in keys if k not in ("M3", "modes") and re.search(SYM_TERMS[k], rest)]
    out = ["Symbols: " + "; ".join(sy) + "."] if sy else []
    for k in ("M3", "modes"):
        if k in keys and re.search(SYM_TERMS[k], rest):
            out.append(cap1(SYMBOLS[k]) + ".")
    return " ".join(out)


def key_words(rest: str) -> str:
    return " ".join(t for pat, t in WORD_ENTRIES if re.search(pat, rest))


def key_extra(rest: str, entries) -> str:
    """entries: (term regex, text); the text is kept if the term occurs in `rest`."""
    return " ".join(t for pat, t in entries if re.search(pat, rest))


# U2: the plain titles of the images and the check each one is shown for: (panels, plain title, check ID, what the check is)
TITLE_MAP = {
    "F1": (("(d) and (f)", "network vs mean field: FAIL", "RB1", "network against mean field"),),
    "F3": (("(a), (b) and (c)", "frequency check: FAIL", "RB9(b)", "spectral against cycle frequency at the headline"),),
    "F5": (("(a)", "network vs mean field, cells: FAIL", "RB1", "network against mean field, the 4 map cells"), ("(b)", "network vs mean field FAIL", "RB1", "network against mean field, the 4 map cells"),
           ("(c)", "90 percent agreement rule: FAILED", "D24", "the rule that at least 90% of the cells of the noisy subgrid agree with the noise-free class")),
    "F5c": (("(b)", "step-halving check: FAIL", "RB6", "numerical convergence, the network f_pk when the step is halved"),),
    "F2": (("(c)", "Network vs mean field: FAIL", "RB1", "network against mean field: the same class is required at the main example for ramp durations of 10 s and 120 s, at the 4 map cells and overall"),),     # DL-628 C1 (DL-616 had no red title on F2)
    "FS2": (("(b)", "Amplitude squared: FAIL", "K7 amplitude residual", "the straight-line fit of the squared amplitude of the cycle against tau_d over the pre-set window must leave a residual of at most 2 percent"),
            ("(l)", "Frequency against J: FAIL", "K10 J dependence", "the frequency of the linearised model must change by at most 10 percent over the J range at tau_d 8, 20 and 40 ms (single source, not verified)")),
    "FS1": (),                                                                       # 13t-4: no red title and no failed row (DL-637)
    "F6": (("(c)", "Negative-control check: FAIL", "G7", "the negative-control gate: the network run of the first negative control must not be in a surge class"),),
}
WORD_MAP = {"F3": (("continuation", "A4", "the analysis step named \"M3 fixed points and Hopf curves\""), ("frequency-map", "A6", "the analysis step named \"M3 frequency map\""))}


def title_sentence(fid: str) -> str:
    """The sentence of the 'Failed checks' paragraph that maps the plain titles to the check IDs ('shown in the title as ...')."""
    return "Red titles show a FAIL (a failed check concerns the panel). " + " ".join(f"The check {cid} ({what}) is shown in the title of {panels} as '{plain}'." for panels, plain, cid, what in TITLE_MAP[fid])


def mapping_markdown(fid: str) -> str:
    """The supplement table: plain title or word on the image, panels, check or step ID, what it is."""
    lines = ["| plain text on the image | panels | check or step ID | what it is |", "|---|---|---|---|"]
    lines += [f"| {plain} | {panels} | {cid} | {what} |" for panels, plain, cid, what in TITLE_MAP[fid]]
    lines += [f"| {w} | legend | {sid} | {what} |" for w, sid, what in WORD_MAP.get(fid, ())]
    return "\n".join(lines)


# U6 (d): the counts of two ruled limit sentences refer to runs that none of the figures draws; the scope is in plain words (sources: the decision log DL-227, DL-229 and DL-251, DL-394)
LIMIT_SCOPE = {
    "MS9(e)-1": ("Scope of the counts 'flagged in 10 of 10 seeds' and 'the ramp runs in 10 of 10': they come from the exploratory network runs of the negative-control step at N = 1e4 with 10 seeds each "
                 "(the negative-control path along which the mean excitability falls, and the same network held at constant parameters without a ramp); those runs are not drawn here."),
    "MS11-C1": ("Scope of the count 'the controls without a ramp reach 7 of 10': it comes from the noisy mean-field runs with constant parameters at the start state of the headline, 10 seeds at each "
                "noise level; those runs are not network runs and are not drawn here."),
}


def limit_scope(ids) -> str:
    return " ".join(LIMIT_SCOPE[i] for i in ids if i in LIMIT_SCOPE)


MODE_N_SURGE = ("S+", "S-rel", "S-abs")          # the surge classes of mode N (the surge-definition key, G1)


# ---- shared builders ---------------------------------------------------------------------------------------------------------------------------------------------------------------

def num(x, nd=None) -> str:
    return CAP.number_text(x) if nd is None else f"{float(x):.{nd}f}"


def settings_line(crit: dict, *, spectrogram: dict | None = None, extra: str = "") -> str:
    """The classifier and spectrogram settings in words, read from the frozen criteria (never retyped) and the spectrogram settings of the figure."""
    line = CAP.classifier_line(crit).split(": ", 1)[1]
    s = "Fixed before the analysis and read from the stored settings: " + line.replace("T_ramp", "the ramp duration T_ramp")
    s += (" A_ref is the limit-cycle amplitude of v at the reference validation point (eta_bar 4, J = -21, Delta 0.3, tau_d 5 ms), used as one fixed absolute threshold for every cell and path of mode D.")
    if spectrogram:
        sp = spectrogram
        s += (f" Spectrogram of v: {sp['taper']} window of {num(sp['window_s'])} s with a step of {num(sp['step_s'])} s, {sp['detrend']} detrend per window, {sp['scaling']}, sampled at {num(sp['fs_hz'])} Hz; "
              f"total band {num(sp['total_band_hz'][0])} to {num(sp['total_band_hz'][1])} Hz, primary (gamma) band {num(sp['band_primary_hz'][0])} to {num(sp['band_primary_hz'][1])} Hz; "
              "the routine is the classifier's own (named in the supplement).")
    return s + extra


def limits_paragraph(ids, not_applicable=None, pointer: str = "", na_text: str | None = None) -> str:
    from . import plain as PL
    return (pointer + " " if pointer else "") + "Claim limits: " + PL.plain_limit_text(ids, not_applicable, na_text)


def pv(rows: list, key: str, panel: str | None = None):
    """The stored value of a parameter row (the first panel that has it, or the named panel)."""
    for r in rows:
        if r["key"] == key and (panel is None or r.get("panel") == panel):
            return r["value"]
    raise JCaptionError(f"parameter {key!r} not among the rows")


def sym(*keys) -> str:
    return "; ".join(SYMBOLS[k] for k in keys)


def cap1(s: str) -> str:
    return s[0].upper() + s[1:]


# ---- F1 --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def f1_caption(d: dict, a11: list, crit: dict, rows: list, *, strip_rows: list, ids, c: dict) -> str:
    """The journal caption of F1. c: typed or computed constants of figures.py that the text needs (columns, zoom length, raster counts, net line, edge-band text, extra control classes)."""
    gap = d["ref_onset_s"] - d["onset120_s"][0]
    r0, r1 = min(d["raw120_s"]), max(d["raw120_s"])
    sp = d["spec_settings"]
    t_on, t_end = d["path_t_on_s"], d["path_t_on_s"] + d["path_T_ramp_s"]
    j0 = t_on + d["path_J_lag_frac"] * d["path_T_ramp_s"]
    j1 = j0 + d["path_J_T_frac"] * d["path_T_ramp_s"]
    rb3a = rb3a_value(a11)
    r6 = next(r for r in a11 if r["rb_id"] == "RB6" and r["check_id"] == "solver_onset_headline")
    r2 = next(r for r in a11 if r["rb_id"] == "RB2" and r["check_id"] == "headline_class_kept_1.0_sigma")
    same_onset = len(set(d["onset120_s"])) == 1
    s10 = d["cls10"]
    ctrl10 = ", ".join(f"{k} {v}" for k, v in d["ctrl10"].items())
    n120 = next(iter(d["ctrl120"].values()))
    take = (f"The network (N = 1e4 neurons) does not reproduce the mean-field class at the headline: 0 of 3 seeds match the mean-field class {d['ref_class']} (all 3 are {d['cls120'][0]}; check RB1 FAILED). "
            f"The stored mean-field headline run (hypoxia-like path P2, ramp duration T_ramp {num(d['path_T_ramp_s'])} s) is a surge of class {d['ref_class']} with a spectral peak of {d['ref_f_pk_hz']:.1f} Hz and onset "
            f"{d['ref_onset_s']:.3f} s; the peak is above 25 Hz, so the pre-stated check that a peak below 25 Hz would trigger a new choice of the headline did not fire. "
            f"The raw first crossings of the network are at {r0:.3f} to {r1:.3f} s against the mean-field onset {d['ref_onset_s']:.3f} s, and its classifier onset is {d['onset120_s'][0]:.1f} s ({gap:.1f} s before the mean-field onset), "
            "so by the classes fixed before the runs the network does not reproduce the mean-field class (no claim is made about the visual shape of the traces, either way); "
            f"the network f_pk values {d['fpk120_hz'][0]:.1f}, {d['fpk120_hz'][1]:.1f} and {d['fpk120_hz'][2]:.1f} Hz are not a claim of agreement (the RB6 check of the network f_pk FAILED). "
            f"At T_ramp 10 s the 3 seeds are {s10[0]}, {s10[1]} and {s10[2]} (0 of 3 seeds match; not drawn). Network runs without a ramp reach the surge classes {ctrl10} at the 10 s headline, "
            f"{c['ctrl_extra']} (not drawn); the 120 s headline controls are {d['cls120'][0]} {n120} of 3 (not drawn). Network classes under the fixed criteria therefore cannot separate ramp-driven from non-ramp records. "
            "RB1 failed (headline 10 s, headline 120 s, cells 1 of 4) and gate G4 was triggered because the network disagrees with the mean field in 2 or more of the 4 map cells (3 of 4 disagree); the consequence is a rerun of the "
            "numerical-convergence check RB6 and reporting the affected results as mean-field-only. G4 is report-only and the surge result is stated for the mean field only.")
    panels = " ".join([
        "The schematic above (a) is our layout of the labels of the model description; it carries no equation and no value (not verified as a drawing).",
        f"(a) The stored mean excitability eta_bar(t) of the headline run, with the stored values {d['path_eta_start']:.3f} (start), {d['path_eta_H']:.3f} (eta_H) and {d['path_eta_peak']:.3f} (peak) as dotted horizontal lines, "
        f"the ramp start t_on = {num(t_on)} s and the ramp end {num(t_end)} s as dotted vertical lines (label \"ramp start and end\"), and the mean-field onset {d['ref_onset_s']:.3f} s as a dash-dotted line.",
        f"(b) The stored coupling J(t) from {num(d['path_J0'])} to {num(d['path_J_end'])}, with the start and end of the J ramp ({num(j0)} s and {num(j1)} s) as dashed vertical lines (label \"J ramp start and end\"); "
        "these two times are derived from the stored ramp fractions and are not stored as times.",
        f"(c) and (e) r(t) and v(t) of the stored mean-field headline run; (d) and (f) r(t) and v(t) of the three stored network runs (N = 1e4, T_ramp {num(d['path_T_ramp_s'])} s, seeds 0, 1 and 2) on the same y range as (c) and (e): "
        "all three stored seeds are drawn and none is chosen, and N = 1e4 is the only N of the headline network runs (the 3e4 runs belong to the finite-size runs and are not drawn here).",
        f"Each series is a min-to-max envelope per pixel column ({c['columns']} blocks of whole samples; a display decimation that is not verified as a rule): the extremes of every block and of the whole series are the stored extremes, nothing is smoothed or offset.",
        f"In (d) and (f) the red title shows FAIL and the in-panel line reads 'network class {d['cls120'][0]}; mean field {d['ref_class']}' (the stored result: {c['net_line']}); a strip above the axes marks the stored network classifier onset ({d['onset120_s'][0]:.1f} s, "
        f"{'equal in the three seeds, so the three seeds coincide there' if same_onset else 'per seed'}) and the three raw first crossings (circle, plus and star for seeds 0, 1 and 2; {', '.join(f'{x:.3f}' for x in d['raw120_s'])} s), "
        f"which differ and overlap at this scale (stored values {r0:.3f} to {r1:.3f} s); the height in the strip carries no value, and the mean-field onset is the dash-dotted line.",
        f"(g) and (h) Spectrograms of the stored v of the mean-field run and of network seed 0, computed here by the classifier's own routine with the settings below (not stored, no new setting); rows from 0 to {num(sp['total_band_hz'][1])} Hz are drawn, "
        f"as 10 log10 PSD (dB) on one colour range for both panels, from {d['spec_shared_db_range'][0]:.2f} dB (the minimum of the network panel) to {d['spec_shared_db_range'][1]:.2f} dB (the larger of the two maxima); "
        f"the stored mean-field range is {d['spec_db_range']['mf'][0]:.2f} to {d['spec_db_range']['mf'][1]:.2f} dB, so {d['spec_mf_below_shared'][0]} of {d['spec_mf_below_shared'][1]} mean-field cells lie below the shared minimum "
        "and are drawn in its lowest colour (arrow on the colour bar; their values are in the source data), because a range that covers both would flatten the network panel (a display choice); "
        "the dashed lines at 25 and 100 Hz are the edges of the primary band, and the window time axis is the classifier's (sample i at i/fs).",
        c["edge_bands"],
        f"(i) For the {d['ras_n_rows']} stored neurons of seed 0, the number of stored spikes per neuron in each {num(d['ras_count_bin_s'])} s bin from 0 s, computed from the stored spikes (rows are the stored neurons in increasing neuron index; "
        f"every count is exact, nothing is smoothed, and the counts sum to the {c['n_spikes']} stored spikes; {d['ras_n_active_rows']} of the {d['ras_n_rows']} rows spike); the colour range runs from 0 to {c['top']:g} spikes "
        f"({c['percentile']:g}th percentile of the counts), and the {c['n_above']} of {c['n_cells']} cells above it (up to {c['max_count']}) take the top colour (arrow on the colour bar; a display choice); "
        "the two windows of (j) and (k) are framed (j solid, k dashed; each frame is as wide as its 1 s window, so on the 165 s axis it looks like a bar).",
        f"(j) and (k) The stored spikes of seed 0 in windows of {c['zoom']:g} s that start at the stored network classifier onset ({d['zoom_windows_s'][0][0]:.3f} s) and at the stored mean-field onset ({d['zoom_windows_s'][1][0]:.3f} s); "
        f"the rows are the neurons of (i), in the same order, and carry no tick labels; the y limit is padded by {c['pad_rows']} rows on each side (display only, no spike is moved).",
    ])
    sigma = sigma_text(a11, pv(rows, "noise.sigma"))
    params = (f"Stored values (the complete list with the stored key names is in the supplement): model {pv(rows, 'model.type')} with membrane time constant {num(pv(rows, 'model.tau_ms'))} ms, J = {num(pv(rows, 'model.J'))}, "
              f"Delta = {num(pv(rows, 'model.Delta'))} and synaptic decay time tau_d = {num(pv(rows, 'model.tau_d_ms'))} ms; ramp: the hypoxia-like path P2 with a {pv(rows, 'path.profile')} profile, T_ramp = {num(pv(rows, 'path.T_ramp_s'))} s, "
              f"t_on = {num(pv(rows, 'path.t_on_s'))} s, eta_bar from {pv(rows, 'path.eta_start'):.3f} to {pv(rows, 'path.eta_peak'):.3f} (eta_H = {pv(rows, 'path.eta_H'):.3f}) and J from {num(pv(rows, 'path.J0'))} to {num(pv(rows, 'path.J_end'))}; "
              f"network of N = {num(pv(rows, 'network.N'))} neurons with {pv(rows, 'network.het_dist').capitalize()} heterogeneity, {pv(rows, 'network.n_raster')} neurons in the raster and a spike rate in {num(pv(rows, 'network.rate_bin_ms'))} ms bins; "
              f"{sigma}; root random seed {pv(rows, 'seeds.root_seed')}; output step {num(pv(rows, 'solver.dt_out_ms'))} ms; the ODE solver is named in the supplement.")
    ss = sigma_status(a11)
    failed = ("Shown, not dropped (the full list with value, threshold and source is in the supplement): " + "; ".join(failed_line(r) for r in strip_rows) + ". "
              f"Two further stored FAIL rows are not in the status strip of this figure: the sigma check ({ss['status']}, logged verdict {ss['verdict']}) and RB3(a) ({rb3a} testable in-range runs match). "
              f"Other failed checks on the headline path are shown elsewhere: the RB2 headline class (kept in {r2['value'].split(' (')[0]} seeds at the noise level sigma; threshold {r2['threshold']}), the RB3(a) onset prediction on the testable in-range runs ({rb3a}) "
              f"and the RB3(b) classifier onset in F4, and the RB6 solver onset ({r6['value']} against {r6['threshold']}) in F4 and FS4. " + title_sentence("F1") + " The title of (d) and (f) is red because those panels draw the failed result (the class of the network seeds).")
    limits = limits_paragraph(ids, None, pointer="Claim limits that change how panels (d) and (f) read: the network does not reproduce the mean-field classes, and no-ramp network controls are classified into surge classes.")
    limits = limits + " " + limit_scope(ids)
    settings = settings_line(crit, spectrogram=sp)
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        key_symbols(rest, "eta", "Delta", "J", "tau_d", "tau", "r", "v", "t_on", "T_ramp", "N", "PSD", "W", "f_pk", "M3", "modes"),
        key_extra(rest, [EXTRA_ENTRIES[k] for k in ("eta_H", "P2", "F4")]),
        class_key(), "Checks: X.",
        key_extra(rest, [EXTRA_ENTRIES["NC1"]]),
        key_words(rest)] if x)
    text = assemble("F1", take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)
    return text.replace("Checks: X.", "Checks: " + defined_checks(text) + ".")


# ---- F3 --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def band_end_sentence(c: dict) -> str:
    """DL-645 G1: the band-end clause of the F3 FULL caption, written from the recorded band ends (c['bands'] = [(Delta, tau_d ms, end)])."""
    bands = c.get("bands")
    if not bands:
        raise JCaptionError("F3: the band ends are not available (DL-645 G1)")
    short = [(D, t, e) for D, t, e in bands if e < 8.0]
    lst = "; ".join(f"Delta {D}, tau_d {t:g} ms: {e:.2f}" for D, t, e in short)
    return (f"Each band ends at the last recorded eta_bar of its cycle branch; the reason is not recorded. {len(short)} of the {len(bands)} bands end before eta_bar 8.0 (heterogeneity Delta, tau_d, end value): {lst}. "
            "All other bands end at 8.0.")


def f3_caption(d: dict, a11: list, crit: dict, rows: list, *, strip_rows: list, ids, c: dict) -> str:
    """The journal caption of F3. c: constants of figures.py: deltas, path order, overlap note, tau_d range text, RB9(b) frequencies (spectral, cycle, difference)."""
    deltas = c["deltas"]
    t_ramp = sorted({d[f"{k}_T_ramp_s"] for k in c["path_order"]})
    sl = d["D0.3_tau_d_ms"]
    first = {}
    for D in deltas:
        cr = d[f"D{D}_c25_eta"]
        t = d[f"D{D}_tau_d_ms"]
        ok = [i for i in range(len(t)) if cr[i] == cr[i]]
        first[D] = (len(ok), [t[i] for i in ok])
    spec, cyc, diff = c["rb9b"]
    take = (f"RB9(b) FAILED (spectral against cycle frequency at the headline: {diff:.3f} Hz against 0.5 Hz), so the frequency shading is a limit-cycle frequency with no confirmed match to the spectral peak: at the headline the classifier's "
            f"spectral peak is {spec:.1f} Hz and the cycle frequency is {cyc:.3f} Hz, and the shading shows the cycle frequency at J = {num(d['a4_curve_J'])}, so it does not contain the spectral value. "
            f"On the slices of the frequency map the 100 Hz contour does not occur for eta_bar 0 to 8 (largest cycle frequency {d['f_max_hz']:.1f} Hz), and the 25 Hz contour crosses the cycle branch only on some slices "
            f"({c['cross_text']}), with the cycle at the reference validation point at {c['ref_range'][0]:.1f} to {c['ref_range'][1]:.1f} Hz. "
            "The project's pre-stated check for this figure is that a 25 Hz contour outside the oscillatory region would trigger gate G2 (a switch to another model); the project log records that the 25 Hz contour crosses the cycle branch "
            "on the slices where it occurs and that G2 did not fire, so the project stays on M3; it states no outcome for this check itself, so reading the crossings on the branch as \"not outside the oscillatory region, no G2\" is our reading and is not verified.")
    hl_eta, hl_tau = d["headline_hopf_eta"], d["headline_tau_d_ms"]
    panel = []
    for j, D in enumerate(deltas):
        n, ts = first[D]
        extra = ""
        if f"{d['a4_curve_Delta']:g}" == D:
            extra = (f" Panel (c) also shows the Hopf curve of the continuation at Delta {num(d['a4_curve_Delta'])}, J {num(d['a4_curve_J'])} (black line; this curve, the stored result of the analysis step \"M3 fixed points and Hopf curves\", is drawn as straight segments between its {c['a4_points']} stored points), "
                     f"the combined path arrow of {c['combined']} (a thin line from eta_bar {d['P1_eta_start']:.3f} to {d['P1_eta_peak']:.3f} at tau_d {num(d['P1_tau_d_ms'])} ms, open circle at the start, arrowhead at the end) "
                     f"and the Hopf point of the frequency map at its headline value (hollow ring, eta_bar {hl_eta:.3f}, tau_d {num(hl_tau)} ms), which is the Hopf point of the tau_d {num(hl_tau)} ms slice of this panel: one stored point drawn twice and not moved.")
        if j == 0:
            lead = (f"(a) Limit-cycle frequency (colour, one scale from {d['f_min_hz']:.1f} to {d['f_max_hz']:.1f} Hz for (a) to (c); largest here {d[f'D{D}_f_max_hz']:.1f} Hz) in the (eta_bar, tau_d) plane for Delta = {D}: one horizontal "
                    f"band per stored slice (tau_d {c['tau_range']}, {len(sl)} values, logarithmic axis; nothing is interpolated between slices), each starting at its Hopf point (black mark with a white outline), "
                    "and a tall black bar at the slices where the 25 Hz contour crosses the cycle branch")
        else:
            lead = f"({'abc'[j]}) The same for Delta = {D} (largest cycle frequency here {d[f'D{D}_f_max_hz']:.1f} Hz): the 25 Hz contour crosses the cycle branch"
        panel.append(lead + f" at {n} of {len(sl)} slices" + (f" (tau_d {', '.join(f'{x:g}' for x in ts)} ms)" if n else "") + f"; the title is red because the shading carries the RB9(b) FAIL.{extra}")
    panel.append(f"(d) The (eta_bar, Delta) plane (logarithmic Delta axis): the Hopf curve of the continuation only (drawn as straight segments between its {c['a4_points_d']} stored points, next to the {c['a4_points']} stored points "
                 f"of the curve in (c)), because the frequency map stores no Delta slices; the combined path arrow lies at Delta {num(d['P1_Delta'])}, "
                 f"P4a leaves it upward to Delta {d['P4a_Delta_end_derived']:.3g} and P4b downward to Delta {d['P4b_Delta_end_derived']:.3g} (both end Delta values are derived: stored Delta times stored Delta factor), and the Hopf point of the frequency map is at eta_bar {hl_eta:.3f}.")
    panel.append("(e) The path strip: one row per path leg (P1, P2, P3, P4a, P4b, P5 up and P5 return), each from its stored start to its stored end in eta_bar; the rows are labels, not a parameter axis, and the ramp duration of each stored record is in its row label.")
    panel.append(band_end_sentence(c))
    panel.append(f"Arrows show the stored linear-profile path values (T_ramp {', '.join(f'{x:g}' for x in t_ramp)} s; the path values are identical at every stored T_ramp); P3 is drawn for a drive amplitude of {num(d['P3_I_amp'])} only, and the J ramp of P2 and P3 is not drawn. "
                 + c["shared"] + " " + c["overlap"] + " " + c["arrow_note"])
    settings = ("No classifier or spectrogram is used in this figure; the 25 Hz and 100 Hz contours are the edges of the gamma band of the classifier (25 to 100 Hz). Colour and contours show the limit-cycle frequency of the continuation, "
                "not the classifier's spectral peak, and there is no interpolation between slices.")
    params = (f"Stored values (the complete list with the stored key names is in the supplement): model {pv(rows, 'model.type')} with membrane time constant {num(pv(rows, 'model.tau_ms'))} ms and J = {num(pv(rows, 'model.J'))} "
              f"(the frequency map is at this fixed J; its J slices are not drawn); Delta = {', '.join(deltas)} and synaptic decay time tau_d = {c['tau_range']} ({len(sl)} values), swept; the reference validation point is "
              "(eta_bar 4, J = -21, Delta 0.3, tau_d 5 ms). Only the parameters that define the plotted slices and the regime are listed.")
    failed = ("Shown, not dropped (the full list with value, threshold and source is in the supplement): " + "; ".join(failed_line(r) for r in strip_rows)
              + f". The stored table gives no value for this row; the values are those of the project log: spectral {spec:.1f} Hz, cycle {cyc:.3f} Hz, difference {diff:.3f} Hz against the allowed 0.5 Hz (the inverse of the 2 s window). "
              + title_sentence("F3") + " (a) and (b) are the same frequency map at other Delta; the failed check was made at the main example in (c) and bears on them too. The panels draw the cycle frequency and the failed check compares it with the spectral peak, so the two frequencies are marked on the one shared colour bar "
              "(a tick at the cycle frequency, a tick at the spectral peak, and their difference).")
    limits = limits_paragraph(ids) + " " + limit_scope(ids)
    panels = " ".join(panel)
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        key_symbols(rest, "eta", "Delta", "J", "tau_d", "T_ramp", "M3"),
        "P1 = the path that ramps eta_bar only; P2 = the hypoxia-like path (eta_bar ramped up, with J ramped to 0 after a delay); P3 = P2 plus a common drive; P4a and P4b = P2 with Delta multiplied by 1.5 (P4a) or by 2/3 (P4b) over the ramp; "
        "P5 = eta_bar up, then down, J fixed.",
        "Marks: a black mark with a white outline = the Hopf point of a slice; a tall black bar = the 25 Hz crossing of a slice; the black line = the Hopf curve of the continuation; the hollow ring = the Hopf point of the frequency map at the headline; "
        "the thin dark arrow = the combined path of P1, P2, P3 and P5; the two ticks on the colour bar = the cycle frequency and the spectral peak of the failed frequency check.",
        "Checks: X; G2 = the gate for no gamma transient (a switch to another model).",
        "Stored sources: the Hopf curve (called 'continuation' in the legend) is the result of the analysis step \"M3 fixed points and Hopf curves\" and the limit-cycle frequencies (called 'frequency-map' in the legend) are the result of the analysis step "
        "\"M3 frequency map\" (step names as written in the project's analysis specification).",
        "The classifier's spectral peak is the peak frequency of its spectrogram; the cycle frequency is the frequency of the limit cycle found by continuation. The tau_d and Delta axes are logarithmic (tick labels are plain numbers).",
        key_words(rest)] if x)
    text = assemble("F3", take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)
    return text.replace("Checks: X;", "Checks: " + defined_checks(text) + ";")


# ---- F5 and F5c ------------------------------------------------------------------------------------------------------------------------------------------------------------------

F5_SENTENCE_1 = "Mean field only; network disagrees at 3 of 4 cells; noisy subgrid agrees in 97 of 225 cells (43.1 percent; 203 cells needed)"


def _pct(a, b) -> str:
    return f"{100.0 * a / b:.1f}"


def f5_caption(d: dict, a11: list, crit: dict, rows: list, *, strip_rows: list, ids, not_applicable, c: dict) -> str:
    """The journal caption of F5 (draft panels (a) to (e)). c: sentences and constants of figures.py (take-home sentence 1, cell note, spacing, rule text)."""
    sub = d["sub_n"]
    take = (f"{c['sentence_1']}. In mode D (the noise-free mean field) the surge class D-tr fills {d['map1_n_surge']} of the {d['map1_n']} cells of map 1 ({_pct(d['map1_n_surge'], d['map1_n'])}%, T_ramp 120 s; D-none {d['map1_n_none']}) and "
            f"{d['map2_n_surge']} of the {d['map2_n']} cells of map 2 (D-none {d['map2_n_none']}), so a surge class is not confined to a few cells and the fine-tuning gate G5 continues; RB4 passed (0 of 14 changed, 64 of 64 unchanged). "
            f"The map statements are for mode D and make no claim that the regime map is robust to noise: on the {sub}-cell noisy subgrid the fixed rule D24 FAILED ({d['d24_n_agree']} of {sub} cells agree = {_pct(d['d24_n_agree'], sub)}%, {d['d24_needed']} cells needed; "
            f"{d['d24_n_agree_categories']} of {sub} on the three surge-definition categories, our reading), and the post-hoc view P-1 ({d['p1_n_agree']} of {sub} = {_pct(d['p1_n_agree'], sub)}%) feeds no gate. "
            f"The network at N = 1e4 disagrees with the mean field at {d['cells_n_disagree']} of the 4 map cells (T_ramp 30 s; RB1 cells {d['cells_n_agree']} of 4; gate G4 triggered). Per-seed results against N are in F5c: "
            "the 10 ramp seeds per N fall in S-sus and S-abs (S+ in 6 seeds at N = 3e3, NS in 1 at N = 1e4), and the no-ramp controls also reach surge classes, so network classes do not separate ramp-driven from non-ramp records.")
    panels = " ".join([
        f"(a) Map 1: the stored class (mode D) of every cell of a 30 x 30 map in (Delta, tau_d) at the ramp duration T_ramp 120 s ({d['map1_n_surge']} D-tr, {d['map1_n_none']} D-none; colour, with D-none also hatched), cell by cell as stored, "
        "with cell indices on the axes and the stored parameter values as tick labels (nothing is interpolated, smoothed or offset, and every non-surge cell is drawn at the same weight as a surge cell); the four network cells are numbered symbols "
        "(hexagram: the network agrees with the mean field, heptagon: it disagrees), each on the map-1 cell with the same (Delta, tau_d), matched to 1e-9; the title is red because the cell comparison RB1 FAILED, and the in-panel line gives the take-home.",
        f"(b) For the 4 network cells: the map class (T_ramp 120 s), the stored mean-field companion class at T_ramp 30 s (its own run) and the three network classes (seeds 0, 1, 2), then the agree or disagree symbol of (a) (the class marks are those of the class key under (d) and of F5c); "
        "the network was run at T_ramp 30 s and the map is at T_ramp 120 s, so both are drawn and no equivalence is claimed.",
        f"(c) The {sub}-cell noisy subgrid under the fixed rule D24, which FAILED ({d['d24_n_agree']} of {sub} cells agree = {_pct(d['d24_n_agree'], sub)}%, {d['d24_needed']} cells needed; {d['d24_n_tie']} ties count as disagreements by the rule); every subgrid cell is the "
        f"mode-N majority class of 10 seeds at the noise level sigma = {num(pv(rows, 'noise.sigma'))}, checked and not confirmed (sigma check: {sigma_status(a11)['status']}, logged verdict {sigma_status(a11)['verdict']}; see Parameters); "
        f"a dark mark in each cell (open circle: the cell agrees, cross: it disagrees, plus: a tie) is the mark of the key, and {c['spacing']}.",
        f"(d) The same subgrid as the post-hoc view P-1 ({d['p1_n_agree']} of {sub} = {_pct(d['p1_n_agree'], sub)}%, {d['p1_n_tie']} ties), which feeds no gate, in its own dashed frame beside (c), at the same size.",
        f"(e) Map 2: the stored class (mode D) of every cell of a 25 x 13 map in (J0, T_ramp) at Delta 0.3 and tau_d 5 ms ({d['map2_n_surge']} D-tr, {d['map2_n_none']} D-none), drawn as (a); map 2 has no network runs.",
        "The cells of (a) and (e) carry no class mark (a 3 pt mark did not fit the D-none cell of (a), which is 4.1 pt high, and the cells of (e) are 2.3 pt high): the class of a cell is its colour and, for D-none, its hatch, and the class of every cell is in the source data of the supplement. "
        "The dark marks of (c) and (d) are 4.2 pt wide inside a pitch of at least 6 pt, so no two marks touch although a mark is wider than its 3 pt map cell. Per-seed results against N (class, f_pk, onset and duration) are in F5c.",
        c["cells_note"],
    ])
    sig = sigma_text(a11, pv(rows, "noise.sigma"))
    params = (f"Stored values (the complete list with the stored key names is in the supplement): model {pv(rows, 'model.type')} with membrane time constant {num(pv(rows, 'model.tau_ms'))} ms and J = {num(pv(rows, 'model.J'))}; "
              f"map 1 at Delta 0.01 to 0.6 (30 values) and tau_d 1 to 50 ms (30 values, log), T_ramp 120 s; map 2 at J0 -40 to -5 (25 values) and T_ramp (13 values), Delta 0.3, tau_d 5 ms; hypoxia-like path P2 with a linear profile; "
              f"network cells at T_ramp 30 s and the N sweep at T_ramp 60 s (N = 1e3, 3e3, 1e4, 3e4 for F5c) with {pv(rows, 'network.het_dist').capitalize()} heterogeneity; {sig}; root random seed {pv(rows, 'seeds.root_seed')}; "
              "the ODE solver is named in the supplement.")
    failed = ("Shown, not dropped (the full list with value, threshold and source is in the supplement): " + "; ".join(failed_line(r) for r in strip_rows)
              + f". The sigma check also FAILED (stored status in Parameters). " + title_sentence("F5") + f" {c['f5c_pointer']}")
    limits = limits_paragraph(ids, not_applicable, pointer="") + " " + limit_scope(ids)
    settings = settings_line(crit)
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        key_symbols(rest, "Delta", "tau_d", "J", "T_ramp", "N", "f_pk", "M3", "modes"),
        key_extra(rest, [EXTRA_ENTRIES[k] for k in ("J0", "ij", "F5c_F6")]),
        class_key(), "Checks: X.",
        "The rule for the network cells (RB1): a cell agrees only if 3 of 3 seeds match the mean-field companion class; RB1 needs at least 3 of 4 cells; agreement is read on the surge-definition categories (D-tr meets S+, S-rel or S-abs; D-none meets NS), our reading, not verified.",
        key_words(rest)] if x)
    text_wo = assemble("F5", take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)
    return text_wo.replace("Checks: X.", "Checks: " + defined_checks(text_wo) + ".")


def _or_list(names) -> str:
    names = list(names)
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " or " + names[-1]


def _and_list(items) -> str:
    items = [str(x) for x in items]
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def f5c_counts(per_n: list) -> dict:
    """DL-582 U6 (c): per N, how many of the 10 ramp seeds and of the 3 no-ramp controls are in a surge class (S+, S-rel, S-abs), computed from the figure arrays (figures._f5_jconst). Returns the phrases
    the take-home, the panel sentence and the short caption use; the phrase for an N without a control in a surge class lists the classes that the drawn controls and ramp seeds have."""
    labels = [p["label"] for p in per_n]
    ctrl = [p["ctrl_surge"] for p in per_n]
    ramp = [p["ramp_surge"] for p in per_n]
    with_surge = [p["label"] for p in per_n if p["ctrl_surge"] > 0]
    without = [p for p in per_n if p["ctrl_surge"] == 0]
    zero = "; ".join(f"at N = {p['label']} the {p['ctrl_n']} controls are {_or_list(p['ctrl_classes'])} and the ramp seeds are {_or_list(p['ramp_classes'])}" for p in without)
    surge_n = [p["ctrl_surge"] for p in per_n if p["ctrl_surge"] > 0]
    return {"labels": labels, "ctrl": ctrl, "ramp": ramp, "with_surge": with_surge, "zero": zero, "surge_text": f"{_and_list(surge_n)} of 3",
            "ctrl_text": f"{_and_list(ctrl)} of 3 at N = {_and_list(labels)}", "sus_text": f"{_and_list([p['ctrl_sus'] for p in per_n])} of 3 at N = {_and_list(labels)}", "ramp_text": f"{_and_list(ramp)} of 10 at N = {_and_list(labels)}"}


def f5c_caption(d: dict, a11: list, crit: dict, rows: list, *, strip_rows: list, ids, not_applicable, c: dict) -> str:
    """The journal caption of F5c (draft panels (f) to (i))."""
    sig = sigma_text(a11, pv(rows, "noise.sigma"))
    cn = f5c_counts(c["per_n"])
    take = ("The RB6 network f_pk check FAILED (numerical convergence: halving the step must change the network f_pk by less than 2 percent), and the per-N results show that network classes do not reproduce the mean field: "
            "against N = 1e3, 3e3, 1e4 and 3e4 the 10 ramp seeds per N fall in S-sus and S-abs (S+ in 6 seeds at N = 3e3, NS in 1 at N = 1e4), and the no-ramp controls reach surge classes (S+, S-rel or S-abs) "
            f"at N = {_and_list(cn['with_surge'])} ({cn['surge_text']})" + (f", while {cn['zero']}" if cn["zero"] else "") + ". "
            f"The network at N = 1e4 disagrees with the mean field at {d['cells_n_disagree']} of the 4 map cells (RB1 cells {d['cells_n_agree']} of 4; gate G4 triggered), and the mean-field results of F5 (maps, noisy subgrid) are for mode D only. "
            "No claim of f_pk or class agreement between the network and the mean field is made.")
    panels = " ".join([
        "(a) The class of every seed against N (the 40 network runs at T_ramp 60 s: N = 1e3, 3e3, 1e4, 3e4 with 10 seeds each, filled marks; the 12 no-ramp control runs, 3 per N, open marks); the class is the stored class, "
        "and a seed's x position is its slot in the N group (ramp seeds 0 to 9, then control seeds 0 to 2), a layout that carries no value.",
        f"In a surge class (S+, S-rel or S-abs), counted from the drawn classes: the ramp seeds {cn['ramp_text']}; the no-ramp controls {cn['ctrl_text']}; the no-ramp controls in S-sus (not a surge class): {cn['sus_text']}.",
        "(b) f_pk of every seed with a defined value against N (the title is red because the RB6 network f_pk check FAILED): the dotted line is the stored mean-field companion value at T_ramp 60 s; the grey bar is the stored minimum to maximum of the ramp seeds and the wide tick the stored median (these three marks are in the key above (a)).",
        f"(c) The onset of every seed with a defined value against N, with the stored mean-field companion onset {d['ref_onset_s']:.3f} s as a dotted line; {c['onset_sentence']} "
        f"The no-ramp controls also flag onsets, from {float(np.nanmin(np.asarray(d['ctrl_onset_s'], float))):.1f} to {float(np.nanmax(np.asarray(d['ctrl_onset_s'], float))):.1f} s, so onset is not a ramp-specific signal in this figure.",
        f"(d) The duration of every ramp seed with a defined value against N (logarithmic axis; the controls were evaluated without the duration, so there are no control points): {c['duration_sentence']}",
        "The per-seed f_pk, onset and duration are recomputed from the stored series with the classifier's own routine, called as in the stored evaluation and with no new setting, and are labelled so; the recomputed classes equal the stored classes, "
        "and the recomputed counts, minimum, median and maximum equal the stored values (a build test; a difference stops the build); this is a logged exception to the rule that figures read stored tables first, and it is not verified as a rule. "
        f"Seeds whose metric is undefined are not drawn; {c['undefined_note']}",
        "The maps, the network cells and the noisy subgrid are in F5.",
    ])
    params = (f"Stored values (the complete list with the stored key names is in the supplement): model {pv(rows, 'model.type')} with membrane time constant {num(pv(rows, 'model.tau_ms'))} ms, J = {num(pv(rows, 'model.J'))}, "
              f"Delta = {num(pv(rows, 'model.Delta', 's9_N1e4_seed0'))} and synaptic decay time tau_d = {num(pv(rows, 'model.tau_d_ms', 's9_N1e4_seed0'))} ms; hypoxia-like path P2 with a linear profile, T_ramp = {num(pv(rows, 'path.T_ramp_s', 's9_N1e4_seed0'))} s; "
              f"network size N = 1e3, 3e3, 1e4, 3e4 (swept) with {pv(rows, 'network.het_dist').capitalize()} heterogeneity; {sig}; root random seed {pv(rows, 'seeds.root_seed')}; the ODE solver is named in the supplement.")
    failed = ("Shown, not dropped (the full list with value, threshold and source is in the supplement): " + "; ".join(failed_line(r) for r in strip_rows)
              + ". The sigma check also FAILED (stored status in Parameters). " + title_sentence("F5c") + " The test itself (halving the step) is not drawn because its runs are not stored; a plain line in panel (b) says so. The F5 caption lists the other FAILs of the figure (RB1 cells, D24, RB2).")
    limits = limits_paragraph(ids, not_applicable, pointer="Claim limits that change how panel (a) reads: no-ramp network controls are classified into surge classes, and there is no claim that the regime map is robust to noise.")
    limits = limits + " " + limit_scope(ids)
    settings = settings_line(crit)
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        key_symbols(rest, "tau_d", "N", "f_pk", "T_ramp", "modes"),
        "Filled marks = ramp seeds (10 per N); open marks = no-ramp control seeds (3 per N). F5 = the other figure of this paper that holds the maps, the network cells and the noisy subgrid.",
        class_key(), "Checks: X.", key_words(rest)] if x)
    text_wo = assemble("F5c", take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)
    return text_wo.replace("Checks: X.", "Checks: " + defined_checks(text_wo) + ".")
