"""Caption helper (MS13 13c; docs/ms13_conventions.md section 5, M13-5).

Builds a caption from the same values that feed <ID>_params.csv (rows as given to figprov.write_params_csv; values written with
figprov.value_text, the function that writes the csv cell) and the spectrogram settings the figure script reads from the frozen criteria / run
config. Two fields are REQUIRED and have no default: the take-home message and the list of claim-limit IDs. A missing one raises CaptionError.
The helper never writes a message, never invents a claim limit, and never decides where a limit is shown: it prints exactly the IDs it is
given, and the figure script (per the build prompt) decides which IDs go to the caption and which to a strip. Part layout UNVERIFIED.
An empty claim-limit list counts as missing (UNVERIFIED reading of "REQUIRED list": a figure that truly has no limit needs a ruling).
13o (DL-494, DL-495): every claim limit is printed with its definition and DL numbers from the label table (R2), a limit can be carried as not applicable with
its reason (R5), and the parameters are grouped by key, with the full list referred to as the Nordlie table of the figure (R3).
"""
from __future__ import annotations

from dataclasses import dataclass

from . import style as S
from .claim_labels import CLAIM_LIMIT_LABELS
from .figprov import value_text


NOISE_SIGMA_TAG = " (checked, not confirmed, G4-C4)"          # G5 (13r-2)


class CaptionError(ValueError):
    """A required caption field is missing or empty; the message names the field."""


@dataclass(frozen=True)
class Caption:
    text: str
    parameter_string: str
    spectrogram_string: str
    claim_limits: tuple


def parameter_string(rows, swept=None) -> str:
    """Rows grouped by key, in order of first appearance (13o, R3): 'key=value' when every panel has the same value, else 'key=value [panel, ...], value [panel, ...]'
    (value = the params.csv cell text). A key repeated per panel or per seed with one value is printed once.
    13r-2 (DL-511 G5): swept = {key: values} prints that key as its swept range or list (sweep_text) followed by ", swept", whatever the rows hold; noise.sigma, wherever it is
    listed, carries "checked, not confirmed; G4-C4"."""
    swept = dict(swept or {})
    by_key: dict = {}
    for r in rows:
        vals = by_key.setdefault(r["key"], {})
        panels = vals.setdefault(value_text(r["value"]), [])
        p = r.get("panel", "")
        if p and p not in panels:
            panels.append(p)
    parts = []
    for key, vals in by_key.items():
        if key in swept:
            parts.append(f"{key}={sweep_text(swept[key])}, swept")
        elif len(vals) == 1:
            parts.append(f"{key}={next(iter(vals))}" + (NOISE_SIGMA_TAG if key == "noise.sigma" else ""))
        else:
            parts.append(f"{key}=" + ", ".join(f"{v} [{', '.join(ps)}]" if ps else v for v, ps in vals.items()) + (NOISE_SIGMA_TAG if key == "noise.sigma" else ""))
    unknown = sorted(set(swept) - set(by_key))
    if unknown:
        raise CaptionError(f"swept parameter(s) {unknown} are not among the parameter rows")
    return "; ".join(parts)


def spectrogram_string(settings: dict) -> str:
    """'key=value' per setting, sorted by key; the settings dict is read from the frozen criteria / config, never retyped here."""
    return "; ".join(f"{k}={value_text(v)}" for k, v in sorted(settings.items()))


def _required_text(value, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CaptionError(f"required caption field {name!r} is missing or empty; the helper does not write one")
    return value.strip()


def _required_ids(ids) -> tuple:
    if ids is None or isinstance(ids, str) or not hasattr(ids, "__iter__"):
        raise CaptionError("required caption field 'claim_limit_ids' is missing (a list of claim-limit IDs is required)")
    ids = tuple(ids)
    if not ids or not all(isinstance(i, str) and i.strip() for i in ids):
        raise CaptionError("required caption field 'claim_limit_ids' is empty or has a blank entry; the helper does not invent a limit")
    return tuple(i.strip() for i in ids)


def build_caption(figure_id: str, *, take_home=None, claim_limit_ids=None, params_rows=(), spectrogram=None, symbol_keys=(),
                  provenance_hash12=None, tag=None, notes=(), limit_labels=CLAIM_LIMIT_LABELS, not_applicable=None, class_key=None, classifier_line=None,
                  main_failures=(), swept=None) -> Caption:
    """Caption text in the order of the template: take-home, parameters, spectrogram, symbols, claim limits, provenance pointer.

    take_home, claim_limit_ids: REQUIRED (default None, so leaving one out raises CaptionError, not TypeError). params_rows: the rows written to <ID>_params.csv (empty: part omitted);
    printed grouped by key, followed by "The full parameter list is in the Nordlie table of <ID>." (13o, R3). spectrogram: settings dict or None
    (part omitted). symbol_keys: keys of the style table whose marker is explained (an unknown key raises StyleError). provenance_hash12, tag: optional
    pointer (omitted when None). notes: sentences the figure script writes about what is and is not drawn (13e, DL-453); placed after the symbols,
    printed as given, none added. limit_labels: a dict label -> (short form, DL numbers), by default claim_labels.CLAIM_LIMIT_LABELS (13o, R2: one format in every
    caption); each claim-limit ID is printed with its short form and DL numbers, and an ID missing from the dict raises CaptionError. not_applicable (13o, R5): None or a dict
    ID -> reason; such a limit is printed with ", not applicable here because <reason>" after its definition; every key must be one of claim_limit_ids.
    13r-2 (DL-511): class_key (G1; class_key_line(...)) and classifier_line (G8; classifier_line(crit)) are printed after the symbols, before the notes; main_failures (G3) are strings
    that must each occur in sentence 1 of take_home (up to the first ". "), else CaptionError; swept (G5) is passed to parameter_string.
    """
    take = _required_text(take_home, "take_home")
    limits = _required_ids(claim_limit_ids)
    na = dict(not_applicable or {})
    if set(na) - set(limits):
        raise CaptionError(f"not-applicable limit(s) {sorted(set(na) - set(limits))} are not in claim_limit_ids")
    first = take.split(". ")[0]
    absent = [f for f in main_failures if f not in first]
    if absent:
        raise CaptionError(f"main failure(s) {absent} are not in sentence 1 of the take-home message (G3)")
    p_str = parameter_string(params_rows, swept)
    s_str = spectrogram_string(spectrogram) if spectrogram else ""
    parts = [f"{figure_id}. {take}"]
    if p_str:
        parts.append(f"Parameters: {p_str}. The full parameter list is in the Nordlie table of {figure_id}.")
    if s_str:
        parts.append(f"Spectrogram: {s_str}.")
    if symbol_keys:
        parts.append("Symbols: " + "; ".join(f"{k} = {S.get(k).marker_name}" for k in symbol_keys) + ".")
    if class_key:
        parts.append(_required_text(class_key, "class_key"))
    if classifier_line:
        parts.append(_required_text(classifier_line, "classifier_line"))
    parts.extend(_required_text(n, "notes entry") for n in notes)
    missing = [i for i in limits if i not in limit_labels]
    if missing:
        raise CaptionError(f"claim-limit label(s) {missing} are not defined in the label table (docs/claim_limit_labels.md)")
    parts.append("Claim limits: " + "; ".join(f"{i}: {limit_labels[i][0]} ({', '.join(limit_labels[i][1])})"
                                              + (f", not applicable here because {_required_text(na[i], 'not_applicable reason')}" if i in na else "") for i in limits) + ".")
    if provenance_hash12:
        parts.append(f"Provenance: {figure_id}_provenance.json hash12 {provenance_hash12}" + (f", tag {tag}" if tag else "") + ".")
    return Caption(" ".join(parts), p_str, s_str, limits)


# ---- 13r-2 (DL-511 G1, G3, G4, G5, G7, G8, G11; DL-512): shared caption texts. Every text is quoted from the plan, the frozen criteria or a logged result; nothing is invented. ----

# G1: the class definitions of plan Table 2.1, row "Classes", quoted verbatim (tests/test_ms13_13r2.py reads docs/plan.md and requires these strings to occur in it).
TABLE_2_1_MODE_N = ('Mode N: S+ (absolute and relative, transient); S-rel (relative only); S-abs (absolute only; flagged "broadband" when the rise is not a band-limited peak, '
                    'with no new threshold); S-sus (no termination, either power test); NS (none).')
TABLE_2_1_MODE_D = "Mode D: D-tr (transient episode); D-sus (sustained, no termination); D-none (no episode)."
TABLE_2_1_SURGE = 'A "surge class" is D-tr in mode D, or S+, S-rel or S-abs in mode N.'
TABLE_2_1_AGREE = "Noisy and deterministic runs agree when D-tr meets a surge class, D-sus meets S-sus, and D-none meets NS"          # the plan cell has no final full stop
CLASS_KEY_SOURCE = "plan Table 2.1"


def class_key_line(modes: str = "ND", agree: bool = False) -> str:
    """G1: the one class-key line of a figure that draws classes: the definitions of the modes the figure uses, then the surge-class sentence (all verbatim from Table 2.1);
    agree=True adds the agreement sentence (figures that compare noisy and deterministic classes)."""
    if not modes or set(modes) - set("ND"):
        raise CaptionError(f"class_key_line: modes must be 'N', 'D' or 'ND', not {modes!r}")
    parts = []
    if "N" in modes:
        parts.append(TABLE_2_1_MODE_N)
    if "D" in modes:
        parts.append(TABLE_2_1_MODE_D)
    parts.append(TABLE_2_1_SURGE)
    if agree:
        parts.append(TABLE_2_1_AGREE + ".")
    return f"Class key ({CLASS_KEY_SOURCE}): " + " ".join(parts)


# G4: a drawn value at a cap, floor or boundary.
PINNED_UNDETERMINED = "pinned value, cause not determined (UNVERIFIED)"
# V2 (DL-512): the duration floor of the frozen classifier (criteria O2_episode_end and window_rule); stated once, used where durations of 1.0 s (1000 ms) are pinned.
DURATION_FLOOR_TEXT = ("floor of the frozen classifier: duration = flagged windows x step, so one window is the smallest duration, 1.0 s (1000 ms) for T_ramp >= 60 s "
                       "(criteria O2_episode_end, window_rule)")
# D2 (DL-511, DL-512 V1): the saturated classifier-onset delay, stated on F4 (j) and FS4.
D2_STATEMENT = ("classifier onset at or before the ramp start; the eta-based delay equals its minimum eta_start - eta_H (-1.5); the classifier-onset reading is saturated "
                "at these levels")
# V3 (DL-512): what a noise bar and its median count.
NOISE_BAR_TEXT = ("grey bar: minimum to maximum of the seeds with a value; dark mark: median of the seeds with a value (computed from the stored seed values); "
                  "the number above each bar is the number of seeds counted (of 10); a seed with no episode or no crossing is left out of both")
# V4 (DL-512): the wording clause for the MS9(e)-1 count.
FLAGGED_CLAUSE = "as worded in the MS9 limit; not the final classes drawn in (f)"
# G2 (DL-512): the explanation of "(n failed)" in an A11 value and the red-title definition.
FAILED_RUNS_NOTE = "(n failed) = failed runs among the seeds, counted as not kept (MS11 rule, DL-346)"
RED_TITLE_NOTE = "red title: the panel shows a FAIL"


def not_drawn(text: str) -> str:
    """G11: a number or statement that is in the caption but not on the figure."""
    return f"{text.rstrip()} (not drawn)"


def coincide_note(series, what: str = "stored values") -> str:
    """G7: the note for series whose stored values coincide (they keep their stored positions and are not offset)."""
    names = [str(s) for s in series]
    if len(names) < 2:
        raise CaptionError("coincide_note needs at least two series")
    return f"{', '.join(names[:-1])} and {names[-1]} coincide ({what} equal; drawn at their stored positions, not moved)"


def number_text(x) -> str:
    """G9: one number format for captions and labels: plain decimals from 1e-3 up to (not including) 1e5, otherwise a mantissa and exponent without sign or padding
    ('1e5', '2.5e-4'); never '1e+03'."""
    x = float(x)
    if x == 0.0 or 1e-3 <= abs(x) < 1e5:
        return f"{x:.6g}"
    mant, exp = f"{x:.5e}".split("e")
    return f"{float(mant):.6g}e{int(exp)}"


def sweep_text(values) -> str:
    """G5: a swept parameter as its range (a to b, n values) or, for five or fewer values, as the list; one number format (value_text)."""
    if any(isinstance(v, str) for v in values):                       # 13r-3b: a swept name list (paths, profiles) is printed as the list, in order of first appearance
        names = list(dict.fromkeys(str(v) for v in values))
        if not names:
            raise CaptionError("sweep_text: no values")
        return ", ".join(names)
    vs = sorted({float(v) for v in values})
    if not vs:
        raise CaptionError("sweep_text: no values")
    if len(vs) <= 5:
        return ", ".join(number_text(v) for v in vs)
    return f"{number_text(vs[0])} to {number_text(vs[-1])} ({len(vs)} values)"


def classifier_line(crit: dict) -> str:
    """G8: the frozen classifier and spectrogram settings in one caption line, read from the frozen criteria dict (never retyped)."""
    c = crit["classifier"]
    need = ("window_rule", "spectrogram_taper", "band_primary_hz", "total_band_hz", "min_cycles", "amin_factor")
    miss = [k for k in need if k not in c]
    if miss:
        raise CaptionError(f"classifier_line: the frozen criteria lack {miss}")
    return ("Classifier and spectrogram (frozen criteria): " + f"window {c['window_rule']['value']}; taper {c['spectrogram_taper']['value']}; "
            f"gamma band {' to '.join(number_text(v) for v in c['band_primary_hz']['value'])} Hz; total band {' to '.join(number_text(v) for v in c['total_band_hz']['value'])} Hz; "
            f"minimum {number_text(c['min_cycles']['value'])} cycles; threshold {number_text(c['amin_factor']['value'])} x A_ref (mode D).")
