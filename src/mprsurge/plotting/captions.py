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


class CaptionError(ValueError):
    """A required caption field is missing or empty; the message names the field."""


@dataclass(frozen=True)
class Caption:
    text: str
    parameter_string: str
    spectrogram_string: str
    claim_limits: tuple


def parameter_string(rows) -> str:
    """Rows grouped by key, in order of first appearance (13o, R3): 'key=value' when every panel has the same value, else 'key=value [panel, ...], value [panel, ...]'
    (value = the params.csv cell text). A key repeated per panel or per seed with one value is printed once."""
    by_key: dict = {}
    for r in rows:
        vals = by_key.setdefault(r["key"], {})
        panels = vals.setdefault(value_text(r["value"]), [])
        p = r.get("panel", "")
        if p and p not in panels:
            panels.append(p)
    parts = []
    for key, vals in by_key.items():
        if len(vals) == 1:
            parts.append(f"{key}={next(iter(vals))}")
        else:
            parts.append(f"{key}=" + ", ".join(f"{v} [{', '.join(ps)}]" if ps else v for v, ps in vals.items()))
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
                  provenance_hash12=None, tag=None, notes=(), limit_labels=CLAIM_LIMIT_LABELS, not_applicable=None) -> Caption:
    """Caption text in the order of the template: take-home, parameters, spectrogram, symbols, claim limits, provenance pointer.

    take_home, claim_limit_ids: REQUIRED (default None, so leaving one out raises CaptionError, not TypeError). params_rows: the rows written to <ID>_params.csv (empty: part omitted);
    printed grouped by key, followed by "The full parameter list is in the Nordlie table of <ID>." (13o, R3). spectrogram: settings dict or None
    (part omitted). symbol_keys: keys of the style table whose marker is explained (an unknown key raises StyleError). provenance_hash12, tag: optional
    pointer (omitted when None). notes: sentences the figure script writes about what is and is not drawn (13e, DL-453); placed after the symbols,
    printed as given, none added. limit_labels: a dict label -> (short form, DL numbers), by default claim_labels.CLAIM_LIMIT_LABELS (13o, R2: one format in every
    caption); each claim-limit ID is printed with its short form and DL numbers, and an ID missing from the dict raises CaptionError. not_applicable (13o, R5): None or a dict
    ID -> reason; such a limit is printed with ", not applicable here because <reason>" after its definition; every key must be one of claim_limit_ids.
    """
    take = _required_text(take_home, "take_home")
    limits = _required_ids(claim_limit_ids)
    na = dict(not_applicable or {})
    if set(na) - set(limits):
        raise CaptionError(f"not-applicable limit(s) {sorted(set(na) - set(limits))} are not in claim_limit_ids")
    p_str = parameter_string(params_rows)
    s_str = spectrogram_string(spectrogram) if spectrogram else ""
    parts = [f"{figure_id}. {take}"]
    if p_str:
        parts.append(f"Parameters: {p_str}. The full parameter list is in the Nordlie table of {figure_id}.")
    if s_str:
        parts.append(f"Spectrogram: {s_str}.")
    if symbol_keys:
        parts.append("Symbols: " + "; ".join(f"{k} = {S.get(k).marker_name}" for k in symbol_keys) + ".")
    parts.extend(_required_text(n, "notes entry") for n in notes)
    missing = [i for i in limits if i not in limit_labels]
    if missing:
        raise CaptionError(f"claim-limit label(s) {missing} are not defined in the label table (docs/claim_limit_labels.md)")
    parts.append("Claim limits: " + "; ".join(f"{i}: {limit_labels[i][0]} ({', '.join(limit_labels[i][1])})"
                                              + (f", not applicable here because {_required_text(na[i], 'not_applicable reason')}" if i in na else "") for i in limits) + ".")
    if provenance_hash12:
        parts.append(f"Provenance: {figure_id}_provenance.json hash12 {provenance_hash12}" + (f", tag {tag}" if tag else "") + ".")
    return Caption(" ".join(parts), p_str, s_str, limits)
