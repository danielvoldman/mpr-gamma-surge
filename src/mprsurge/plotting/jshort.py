"""MS13 13t-1e (DL-582 U3): the SHORT journal caption, the one for the manuscript, in plain language.

The FULL caption (jcaption.py: seven labelled paragraphs, check IDs, the ruled limits, the parameters and settings) goes to the supplement and the export manifest; this module builds the short
caption of the same figure from the same prepared data and the same stored tables. Rules (DL-582 U3 to U5): at most `caption.short_max_words` words (F1 `short_max_words_F1`; the limits are in
configs/journal_export.yaml, UNVERIFIED); no check ID, gate ID, step ID, plan, DL or milestone reference (the full caption and the supplement carry them); the order is the take-home with the main
failure in plain words, one sentence per panel, the sentence that explains each red title, every failed check that concerns the figure as one plain clause with its number where short, the claim
limits that are specific to the figure with the numbers of the ruled wording (SHORT_LIMITS: each clause is checked against plain.PLAIN_LIMITS), and the pointer to the supplement. The word 'stored' is
not used; where 'recorded' is used it is defined once in the same caption. Every number is read from the prepared data or a stored table; only the wording is typed here.
"""
from __future__ import annotations

import re

from . import captions as CAP
from . import jcaption as JC
from . import plain as PL

# a check ID, gate ID, rule ID or step ID in the sense of the plan (RB1, G7, D24, A4, S8, MS11 ...); the class names (S+, S-rel, S-abs, S-sus, NS, D-tr, D-sus, D-none), the paths P1 to P5 and M3 do not match
ID_PATTERN = re.compile(r"(?<![A-Za-z0-9_])(?:RB\d+(?:\([a-d]\))?|G\d+(?:-C\d)?|D\d+|A\d+|S\d+|MS\d+)(?![A-Za-z0-9_])")
RECORDED_DEF = "Recorded results are read from the saved result files of the analysis, not recalculated."
POINTER = "All earlier failures and limits stand; check names, the full limits, the values and the settings are in Supplement {fid}."

# the limit clauses of the short captions: id of the ruled list -> plain clause; every number of a clause must be a number of PL.PLAIN_LIMITS[id] (test)
SHORT_LIMITS = {
    "G4-C1": "the network does not reproduce the mean-field classes (0 of 3 seeds at T_ramp 10 s and 120 s; 1 of 4 cells)",
    "G4-C3": "no-ramp network controls are classified into surge classes",
    "MS9(e)-1": "network surge classes at N = 1e4 are not evidence of a ramp-driven surge (control without a ramp flagged in 10 of 10 seeds, ramp runs 10 of 10)",
    "MS9(e)-2": "there is no claim that the regime map is robust to noise",
    "G4-C4": "the noise level sigma = 0.0624 is checked and not confirmed",
    "MS11-C1": "the controls without a ramp reach the main-run class in 7 of 10 noisy seeds",
    "MS11-C2": "there is no claim of agreement in peak frequency or class between the network and the mean field",
    "MS11-C3": "the spectral and the cycle frequency differ by 4.39 Hz at the main run, and peak frequencies are the classifier's spectral peaks",
    "MS12-C1": "the surge result is stated for model M3 only",
    "RB9(b) FAIL (plan label)": "the spectral frequency differs from the cycle frequency by 4.391 Hz against the allowed 0.5 Hz",
}
SHORT_LIMIT_IDS = {
    "F1": ("G4-C3", "MS9(e)-1"),
    "F3": ("MS11-C3", "MS12-C1"),
    "F5": ("G4-C4", "MS9(e)-2", "G4-C3"),
    "F5c": ("G4-C3", "MS11-C2", "MS9(e)-1"),
}
# the plain clause of each failed check that a short caption names; {v} is filled from the stored row where the clause has a number
CHECK_CLAUSE = {
    ("RB1", "headline_10s"): "network against mean field at 10 s ({v})",
    ("RB1", "headline_120s"): "network against mean field at 120 s ({v})",
    ("RB1", "cells_30s"): "network against mean field in the map cells ({v} agree)",
    ("RB1", "overall"): "network against mean field overall",
    ("RB2", "noisy_subgrid_agreement"): "90 percent rule ({v})",
    ("RB2", "headline_class_kept_1.0_sigma"): "main-run class kept in {v} noisy seeds ({t} needed)",
    ("RB3", "a_inrange_runs"): "onset prediction ({v} runs)",
    ("RB3", "b_classifier_onset"): "delay under a noise floor",
    ("RB6", "network_fpk_halving_dt"): "step-halving check of the network peak frequency",
    ("RB6", "solver_onset_headline"): "two solvers' onsets differ by {v} (1 ms allowed)",
    ("RB9", "b_spectral_vs_cycle_headline"): "frequency check, spectral peak against cycle frequency",
    ("G7", "gate"): "negative-control check not passed (control path in class S+)",
    ("sigma_check", "S8_baseline_std"): "noise-level check",
}


class JShortError(ValueError):
    """A short caption is too long, holds a check ID or a forbidden word, or a number differs from the stored value."""


def words(text: str) -> int:
    return len(text.split())


def check_clause(a11: list, rb: str, ck: str) -> str:
    """One plain clause of a failed check, its number from the stored A11 row (a row that is not FAIL stops the build)."""
    rows = [r for r in a11 if r["rb_id"] == rb and r["check_id"] == ck]
    if len(rows) != 1 or rows[0].get("pass_or_fail", rows[0].get("status")) != "FAIL":
        raise JShortError(f"stored A11 table: {rb} {ck} is not a single FAIL row")
    v = re.sub(r"\s*\(.*", "", rows[0]["value"])
    if (rb, ck) == ("RB3", "a_inrange_runs"):
        v = re.match(r"\d+ of \d+", rows[0]["value"]).group(0)
    m = re.search(r"(\d+) of", rows[0]["threshold"])
    return CHECK_CLAUSE[(rb, ck)].format(v=v, t=m.group(1) if m else "")


def limit_clauses(fid: str) -> str:
    """The claim limits that are specific to the figure; a clause whose numbers are not in the ruled plain sentence stops the build."""
    out = []
    for i in SHORT_LIMIT_IDS[fid]:
        clause = SHORT_LIMITS[i]
        have = set(re.findall(r"\d+(?:\.\d+)?(?:e\d+)?", PL.PLAIN_LIMITS[i]))
        extra = set(re.findall(r"\d+(?:\.\d+)?(?:e\d+)?", clause)) - have
        if extra:
            raise JShortError(f"short limit {i}: numbers {sorted(extra)} are not in the ruled plain sentence")
        out.append(clause)
    return "Limits: " + "; ".join(out) + "."


def finish(fid: str, parts: list, max_words: int) -> str:
    text = " ".join(p.strip() for p in parts if p).replace("  ", " ")
    text = f"{fid}. {text}"
    bad = sorted({m.group(0) for m in JC.FORBIDDEN.finditer(text)} | {m.group(0) for m in ID_PATTERN.finditer(text)} | set(re.findall(r"\bstored\b", text)))
    if bad:
        raise JShortError(f"{fid}: the short caption holds forbidden words or codes: {bad}")
    if re.search(r"\brecorded\b", text) and RECORDED_DEF not in text:
        raise JShortError(f"{fid}: 'recorded' is used and not defined")
    if words(text) > max_words:
        raise JShortError(f"{fid}: the short caption has {words(text)} words, the limit is {max_words}")
    return text


def _pointer(fid: str) -> str:
    return POINTER.format(fid=fid)


def net_clause(a11: list) -> str:
    """One clause for the three failed RB1 rows (main run at 10 s and at 120 s, map cells), the numbers from the stored rows."""
    v = {ck: re.match(r"\d+ of \d+", next(r["value"] for r in a11 if r["rb_id"] == "RB1" and r["check_id"] == ck)).group(0) for ck in ("headline_10s", "headline_120s", "cells_30s")}
    for ck in v:
        check_clause(a11, "RB1", ck)                                   # each row must be a stored FAIL
    s = f"{v['headline_10s']} seeds at 10 s and {v['headline_120s']} at 120 s" if v["headline_10s"] != v["headline_120s"] else f"{v['headline_120s']} seeds at 10 s and at 120 s"
    return f"network against mean field ({s}; {v['cells_30s']} map cells agree)"


def f1_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int) -> str:
    failed = "; ".join([net_clause(a11)] + [check_clause(a11, rb, ck) for rb, ck in (("G7", "gate"), ("RB6", "network_fpk_halving_dt"), ("RB6", "solver_onset_headline"),
                                                                                  ("RB2", "headline_class_kept_1.0_sigma"), ("sigma_check", "S8_baseline_std"), ("RB3", "a_inrange_runs"),
                                                                                  ("RB3", "b_classifier_onset"))])
    return finish("F1", [
        f"The network (N = 1e4 neurons) does not reproduce the mean-field result of the main example run: none of its 3 seeds is in the mean-field class {d['ref_class']} (a transient surge; all are {d['cls120'][0]}, a surge without end), "
        "and the network-against-mean-field check failed.",
        f"The mean-field run is a surge with a spectral peak of {d['ref_f_pk_hz']:.1f} Hz and onset {d['ref_onset_s']:.3f} s; the network classifier onset is {d['onset120_s'][0]:.1f} s (no claim on the shape of the traces).",
        "(a), (b) Mean excitability and coupling J. (c), (e) Rate r and mean potential v of the mean field; (d), (f) the 3 network seeds, same scale, event times above "
        "(triangle: classifier onset; circle, plus, star: first crossings). (g), (h) Spectrograms of v. (i)-(k) Spike counts of seed 0 and spikes in two windows.",
        "The red titles of (d) and (f) mark the failed check of network against mean field.",
        f"Failed checks: {failed}.",
        limit_clauses("F1"),
        _pointer("F1")], max_words)


def f3_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int) -> str:
    spec, cyc, diff = c["rb9b"]
    return finish("F3", [
        f"The frequency check failed: at the main example run the spectral peak is {spec:.1f} Hz and the cycle frequency is {cyc:.3f} Hz, which differ by {diff:.3f} Hz against the allowed 0.5 Hz (values from the project log).",
        "(a)-(c) Limit-cycle frequency (colour, one bar) against mean excitability eta_bar and synaptic decay time tau_d (log axis) for heterogeneity Delta = 0.05, 0.1 and 0.3: one band per slice, black mark = Hopf point, "
        f"black bar = where the 25 Hz contour crosses the cycle; in (c) the line is the Hopf curve (straight segments between its {c['a4_points']} points), the arrow the combined path of P1, P2, P3 and P5, the ring the Hopf point of the main run.",
        "Ticks on the colour bar mark the two frequencies of the failed check.",
        f"(d) Hopf curve (straight segments between its {c['a4_points_d']} points) against eta_bar and Delta (log axis), with the paths. (e) One row per path, start to end in eta_bar.",
        "The red titles mark the failed frequency check.",
        limit_clauses("F3"),
        _pointer("F3")], max_words)


def f5_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int) -> str:
    sub = d["sub_n"]
    pct = f"{100.0 * d['d24_n_agree'] / sub:.1f}"
    failed = "; ".join([net_clause(a11)] + [check_clause(a11, rb, ck) for rb, ck in (("RB2", "noisy_subgrid_agreement"), ("RB2", "headline_class_kept_1.0_sigma"), ("RB6", "network_fpk_halving_dt"),
                                                                                  ("sigma_check", "S8_baseline_std"))])
    return finish("F5", [
        f"Mean field only: the network disagrees with the mean field at {d['cells_n_disagree']} of 4 map cells, and the noisy subgrid agrees in {d['d24_n_agree']} of {sub} cells ({pct} percent; "
        f"{d['d24_needed']} needed), so the 90 percent rule failed.",
        "(a) Map 1: class per cell in heterogeneity Delta and synaptic decay time tau_d, with the 4 network cells (hexagram: agrees, heptagon: disagrees). "
        "(b) These cells: map, mean-field, network classes. (c) Noisy subgrid: a cell agrees (circle), disagrees (cross) or ties (plus) with the noise-free one; (d) a post-hoc view of the same. "
        "(e) Map 2 in J0 (J at the path start) and ramp duration.",
        "Red titles: network against mean field in (a), (b); the 90 percent rule in (c).",
        f"Failed checks: {failed}.",
        limit_clauses("F5"),
        _pointer("F5")], max_words)


def f5c_short(d: dict, a11: list, strip_rows: list, c: dict, max_words: int) -> str:
    cn = JC.f5c_counts(c["per_n"])
    sep = JC._and_list(cn["with_surge"])
    return finish("F5c", [
        "Network classes do not reproduce the mean field, and the step-halving check of the network peak frequency failed.",
        f"For N = 1e3, 3e3, 1e4 and 3e4 (10 ramp seeds filled, 3 controls open): {cn['zero']}; the controls reach surge classes at N = {sep} ({cn['surge_text']}).",
        "(a) Class of every seed against N. (b) Peak frequency f_pk (dotted: mean field). (c) Onset time. (d) Duration (log axis). Grey bar and tick: minimum to maximum and median of the ramp seeds.",
        "The red title of (b) marks the failed step-halving check; the test is not drawn (its runs were not saved).",
        "Failed checks: step-halving check of the network peak frequency; noise-level check; network against mean field and the noisy subgrid (see F5).",
        limit_clauses("F5c"),
        _pointer("F5c")], max_words)
