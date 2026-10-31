"""MS13 13t-1c (DL-563 S4, DL-565): the journal caption in plain words.

The draft caption is built by the same builder as before (captions.build_caption) and keeps its ruled wording, its DL numbers and its ruling codes; nothing in the drafts or in the ruled
texts (claim_labels.CLAIM_LIMIT_LABELS, the take-home messages) is changed. For the JOURNAL caption this module (1) replaces the claim-limit sentence by one plain sentence per limit
(PLAIN_LIMITS: the same meaning and the same numbers), (2) rewrites the few coded phrases of the body text (PHRASES), (3) removes the decision-log numbers, (4) defines every check, gate,
step and record ID that is still in the text once, in one sentence (DEFINITIONS, names from plan Table 7.2, Table 11.2 and the section 5 and 12 tables), and (5) stops the build if a ruling
code is left (FORBIDDEN). The pairs (plain sentence, ruled text with its DL numbers and codes) are written to the supplement sheet, with the full ruled caption.
"""
from __future__ import annotations

import re

from .claim_labels import CLAIM_LIMIT_LABELS


class PlainError(ValueError):
    """The plain-language caption still holds a ruling code, or a claim limit has no plain sentence."""


# One plain sentence per claim limit: same meaning, same numbers as the ruled short form (claim_labels), never weaker. The ruled text and its DL numbers go to the supplement.
PLAIN_LIMITS = {
    "MS11-C7": "All earlier failures and limits stand: the failure of check RB1 (network against mean field), gate G7 not passed, the failure of the D24 rule, the six limits set when gate G4 "
               "(network against mean field) was triggered, and the limits ruled at milestone 9 (the regime maps and their failure labels).",
    "MS12-C1": "The surge result is stated for model M3 only; there is no claim about the models M4 or M3a and M3b, and the parts of check RB8 that concern M4 and adaptation have no result.",
    "MS9(e)-1": "Surge classes found in network records at N = 1e4 are not evidence of a ramp-driven surge: the network control without a ramp was flagged in 10 of 10 seeds, and the ramp runs in 10 of 10.",
    "MS9(e)-2": "There is no claim that the regime map is robust to noise, and the class S-rel is not counted as evidence of a ramp in the noisy mode (mode N).",
    "MS9(e)-3": "Label (c) of the failure labels (drawn in F6) is a flag, not a demonstrated cause.",
    "MS9(e)-4": "The failure-label check covers 1,056 of the 1,057 surge-class cells.",
    "MS9(e)-5": "Every class that depends on the test for damped against non-damped oscillations is provisional.",
    "MS9(e)-6": "The boundary definition and the extension of the episode-exit rule to the paths P3 and P4 are our own.",
    "DL-163-D1": "The plan's estimator for damped against non-damped oscillations fails 2 of 8 ring items of its own test; the classes that depend on it are provisional.",
    "DL-163-D2": "The baseline is taken as zero, including for noise-free inputs.",
    "G4-C1": "The network at N = 1e4 and 3e4 does not reproduce the mean-field classes (0 of 3 seeds at T_ramp 10 s and 120 s; 1 of 4 cells).",
    "G4-C2": "The surge result is stated for the mean field only; there is no claim that it is robust to finite-size fluctuations.",
    "G4-C3": "No-ramp network controls are classified into surge classes.",
    "G4-C4": "The noise level sigma = 0.0624 is checked and not confirmed; the noisy mean-field runs are labelled as such.",
    "MS11-C1": "The headline class is kept in 7 of 10 seeds at the noise level sigma (8 are needed); the controls without a ramp reach 7 of 10.",
    "MS11-C2": "There is no claim of agreement in peak frequency or in class between the network and the mean field (the RB6 check of the network peak frequency failed).",
    "MS11-C3": "The spectral frequency and the cycle frequency differ by 4.39 Hz at the headline (RB9(b) failed); peak frequencies are the classifier's spectral peaks.",
    "RB1 FAIL (plan label)": "RB1 failed: the headline at 10 s failed, the headline at 120 s failed, and the network agrees at 1 of 4 cells.",
    "RB2 FAIL (plan label)": "RB2 failed: the headline class is kept in 7 of 10 seeds at the noise level sigma, and the noisy subgrid agrees at 97 of 225 cells.",
    "D24 failed (plan label)": "The D24 rule failed: subgrid agreement is 43.1 percent on the raw classes.",
    "G7 not passed (plan label)": "Gate G7 was not passed: the network run of the negative control (the path along which the mean excitability falls by the same amount) is in class S+.",
    "RB9(b) FAIL (plan label)": "RB9(b) failed: the spectral frequency differs from the cycle frequency by 4.391 Hz against the allowed 0.5 Hz.",
}
NOT_APPLICABLE_PLAIN = "not applicable here because no failure label is drawn in F5 (F6 draws them)"

# Definitions of the IDs that may remain in a plain caption (names from plan Table 7.2, Table 11.2 and the tables of sections 5 and 12). A caption defines the ones it uses, once.
DEFINITIONS = (
    ("RB1", "RB1 = network against mean field"),
    ("RB2", "RB2 = noise robustness"),
    ("RB3(b)", "RB3(b) = ramp rate, part (b), the delay under a noise floor"),
    ("RB4", "RB4 = parameter perturbation"),
    ("RB6", "RB6 = numerical convergence"),
    ("RB8", "RB8 = model variants"),
    ("RB9(b)", "RB9(b) = frequency mapping, part (b), spectral against cycle frequency"),
    ("G2", "G2 = the gate for no gamma transient"),
    ("G4", "G4 = the gate for network against mean field"),
    ("G5", "G5 = the fine-tuning gate"),
    ("G7", "G7 = the negative-control gate"),
    ("D24", "D24 = the rule that at least 90% of the cells of the noisy subgrid agree with the noise-free class"),
    ("S8", "S8 = the stored network overlay runs (headline path at N = 1e4, and four map cells)"),
    ("S9", "S9 = the stored finite-size sweep of network runs"),
    ("A4", "A4 = the stored record of fixed points and Hopf curves (a4_hopf_curves)"),
    ("A6", "A6 = the stored frequency-map record (a6_freq_map)"),
    ("A9", "A9 = the regime-map and failure-reason step"),
    ("A11", "A11 = the stored table of the robustness checks"),
    ("f_pk", "f_pk = the classifier's spectral peak frequency"),
    ("UNVERIFIED", "UNVERIFIED = a value, reading or choice that is not confirmed against a source"),
    ("P-1", "P-1 = a post-hoc view that counts the ramp-linked classes S+, S-abs and S-sus as matching D-tr and the other classes as matching D-none (it feeds no gate)"),
)

# Coded phrases of the body text, replaced before the decision-log numbers are removed. (old, new); an old text that does not occur is skipped (the texts are shared by three figures).
PHRASES = (
    ("(MS11-C2; RB6 network f_pk FAIL, FS4)", "(the RB6 check of the network f_pk failed, see FS4)"),
    ("the claim limits G4-C1 and G4-C3 apply to (d) and (f) (full text below)", "the claim limits on the network against the mean field and on the no-ramp controls apply to (d) and (f) (full text below)"),
    ("(claim limit G4-C1)", "(claim limit: the network does not reproduce the mean-field classes)"),
    ("(DL-228: the NC1 network is S+)", "(the network run of the negative control, the path along which the mean excitability falls by the same amount, is in class S+)"),
    ("(checked, not confirmed, G4-C4)", "(checked, not confirmed)"),
    ("checked and not confirmed, G4-C4)", "checked and not confirmed)"),
    ("in S9 at N", "in the finite-size sweep S9 at N"),
    ("N = 1e4 is the only N of the S8 headline (the 3e4 records belong to S9 and are not drawn here)",
     "N = 1e4 is the only N of the headline network runs (S8; the 3e4 records belong to the finite-size sweep S9 and are not drawn here)"),
    ("the marks are stored values (ms10_eval, DL-319)", "the marks are stored values (the stored evaluation of milestone 10)"),
    ("A_ref (reading a) is ", "The classifier's reference amplitude A_ref (reading a) is "),
    (" (A8). Peak frequencies are the classifier's spectral peaks (MS11-C3). Every D8-dependent class is provisional (D8 open).",
     ". Peak frequencies are the classifier's spectral peaks. Every class that depends on the test for damped against non-damped oscillations is provisional (that test is still open)."),
    ("and D8 is undefined in mode N and filters nothing (DL-230), so every D8-dependent class is provisional (DL-163, DL-208)",
     "and the test for damped against non-damped oscillations is undefined in mode N and filters nothing, so every class that depends on it is provisional"),
    ("The words of claim limit MS9(e)-1 (control flagged 10 of 10 seeds; ramp 10 of 10) are as worded in the MS9 limit; not the final classes drawn in (f)",
     "The counts in the limit on network-record surge classes (control flagged 10 of 10 seeds; ramp 10 of 10) are as worded when the limit was ruled and are not the final classes drawn in (f)"),
    ("(S9_ctrl, 3 seeds each)", "(the S9 controls, 3 seeds each)"),
    ("of the MS10 evaluation", "of the evaluation of milestone 10"),
    ("as the MS10 evaluation", "as the evaluation of milestone 10"),
    ("of the stored MS10 evaluation", "of the stored evaluation of milestone 10"),
    ("counted as not kept (MS11 rule, DL-346)", "counted as not kept (rule of the evaluation of milestone 11)"),
    ("our reading, UNVERIFIED as in DL-242", "our reading, UNVERIFIED"),
    ("A9 failure labels are not drawn here (F6)", "The failure labels of the regime-map step (A9) are not drawn here (F6)"),
    ("no A9 failure label is drawn", "no failure label is drawn"),
    ("P3 is drawn for I_amp 1 only", "P3 is drawn for a drive amplitude of 1 only"),
    ("drive, eta part, I_amp ", "drive, eta part, drive amplitude "),
    ("threshold within 1/W)", "threshold: within the inverse of the window length)"),
    ("DL-131 states that the 25 Hz contour crosses the cycle branch of the A6 slices where it occurs, and DL-133 states that no G2 trigger fires and the project stays on M3 (judged on the DL-132 readings); neither entry states an outcome for this Table 8.1 rule itself",
     "The project log records that the 25 Hz contour crosses the cycle branch of the A6 slices where it occurs and that no G2 trigger fires, so the project stays on M3; it does not state an outcome for this Table 8.1 rule itself"),
    ("this Table 8.1 rule itself, so reading", "this Table 8.1 rule itself, so reading"),
)
# a coded parenthetical that only repeats the statement it follows: removed (the claim-limit paragraph carries the full limit)
DELETE = ("(G4-C1)", "(G4-C2)", "(G4-C3)", "(MS11-C2)", "(MS11-C3)", "(MS9(e)-2)", ", G4-C1)", ", G4-C3)")

FORBIDDEN = re.compile(r"DL-\d+|G4-C\d|MS\d+\(e\)-\d|MS\d+-C\d|MS12|\bD8\b|\bA8\b|\bNC1\b|\bMF\b|I_amp|1/W|ms10_eval|\bMS(?:9|10|11)\b")


def scrub_dl(text: str) -> str:
    """Remove every decision-log number with its separator, then the empty brackets and dangling separators it leaves."""
    t = text
    t = re.sub(r"\s*[,;]\s*DL-\d+(?:-D\d)?(?:\s+to\s+DL-\d+)?", "", t)                    # ', DL-319'
    t = re.sub(r"\(\s*DL-\d+(?:-D\d)?(?:\s+to\s+DL-\d+)?\s*[,;]\s*", "(", t)               # '(DL-319, x'
    t = re.sub(r"\s*\(\s*DL-\d+(?:-D\d)?(?:\s+to\s+DL-\d+)?\s*\)", "", t)                  # ' (DL-319)'
    t = re.sub(r"\bDL-\d+(?:-D\d)?(?:\s+to\s+DL-\d+)?\s*[,;]\s*", "", t)
    t = re.sub(r"\s*\(\s*[,;]?\s*\)", "", t)
    t = re.sub(r"\(\s*[,;]\s*", "(", t)
    t = re.sub(r"\s+([,;.)])", r"\1", t)
    t = re.sub(r"\(\s+", "(", t)
    t = re.sub(r"[ ]{2,}", " ", t)
    return t


def plain_fragment(text: str) -> str:
    """A piece of draft caption text as it reads in the journal caption (coded phrases rewritten, decision-log numbers and repeated codes removed)."""
    body = text
    for old, new in PHRASES:
        body = body.replace(old, new)
    body = scrub_dl(body)
    for d in DELETE:
        body = body.replace(" " + d, "").replace(d, "")
    return scrub_dl(body)


def plain_limit_text(ids, not_applicable=None) -> str:
    na = dict(not_applicable or {})
    missing = [i for i in ids if i not in PLAIN_LIMITS]
    if missing:
        raise PlainError(f"claim limit(s) {missing} have no plain sentence in plain.PLAIN_LIMITS")
    out = []
    for i in ids:
        s = PLAIN_LIMITS[i].rstrip(".")
        if i in na:
            s += f"; {NOT_APPLICABLE_PLAIN}"
        out.append(s + ".")
    return " ".join(out)


def pairs(ids, not_applicable=None) -> list:
    """[(id, plain sentence, ruled text, DL numbers)] for the supplement table; the ruled text is the short form of claim_labels as printed in the draft caption."""
    na = dict(not_applicable or {})
    rows = []
    for i in ids:
        short, dls = CLAIM_LIMIT_LABELS[i]
        ruled = f"{i}: {short} ({', '.join(dls)})" + (f", not applicable here because {na[i]}" if i in na else "")
        rows.append((i, PLAIN_LIMITS[i] + (f" ({NOT_APPLICABLE_PLAIN})" if i in na else ""), ruled, ", ".join(dls)))
    return rows


def pairing_markdown(ids, not_applicable=None, ruled_caption: str = "") -> str:
    rows = pairs(ids, not_applicable)
    lines = ["| claim limit (ruled ID) | plain sentence in the journal caption | ruled text (verbatim, with DL numbers and codes) | DL numbers |", "|---|---|---|---|"]
    lines += [f"| {i} | {p} | {r} | {d} |" for i, p, r, d in rows]
    if ruled_caption:
        lines += ["", "Full ruled caption text of the draft builder (verbatim, with the DL numbers and codes that the journal caption leaves out):", "", ruled_caption]
    return "\n".join(lines)


def definitions_sentence(text: str) -> str:
    used = [d for key, d in DEFINITIONS if re.search(r"(?<![\w-])" + re.escape(key) + r"(?![\w])", text)]
    return ("IDs used in this caption: " + "; ".join(used) + ".") if used else ""


def to_plain(text: str, ids, not_applicable=None) -> str:
    """The journal caption text: the draft caption `text` with the claim-limit sentence in plain words, the coded phrases rewritten, the decision-log numbers removed and the remaining IDs defined.
    Raises PlainError if a ruling code is left."""
    head, sep, _tail = text.rpartition("Claim limits: ")
    if not sep:
        raise PlainError("the draft caption has no 'Claim limits: ' sentence")
    body = plain_fragment(head)
    pointer = "Claim limits that change how a panel reads (pointers drawn on the draft figure): "
    if pointer in body:                                                 # the journal figure has no pointers on the image: the sentence is rebuilt from the plain limits of the pointers
        pre, _, post = body.partition(pointer)
        panels = post.split(": ", 1)[0]
        ptr_ids = re.findall(r"(?:^|: |; )(G4-C\d|MS9\(e\)-\d): ", post)
        missing = [i for i in ptr_ids if i not in ids]
        if not ptr_ids or missing:
            raise PlainError(f"the pointer sentence names limits {ptr_ids} that are not all in the claim-limit list {missing}")
        body = pre + f"Claim limits that change how {'panels' if ',' in panels else 'panel'} {panels} read: " + plain_limit_text(ptr_ids)
    body = re.sub(r"[ ]{2,}", " ", body).strip()
    plain_tail = "Claim limits: " + plain_limit_text(ids, not_applicable)
    out = body + " " + plain_tail
    defs = definitions_sentence(out)
    if defs:
        out = body + " " + defs + " " + plain_tail
    bad = sorted({m.group(0) for m in FORBIDDEN.finditer(out)})
    if bad:
        raise PlainError(f"the plain caption still holds ruling codes: {bad}")
    return out
