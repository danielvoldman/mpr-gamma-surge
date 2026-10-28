"""Caption helper (MS13 13c; docs/ms13_conventions.md section 5, M13-5).

Builds a caption from the same values that feed <ID>_params.csv (rows as given to figprov.write_params_csv; values written with
figprov.value_text, the function that writes the csv cell) and the spectrogram settings the figure script reads from the frozen criteria / run
config. Two fields are REQUIRED and have no default: the take-home message and the list of claim-limit IDs. A missing one raises CaptionError.
The helper never writes a message, never invents a claim limit, and never decides where a limit is shown: it prints exactly the IDs it is
given, and the figure script (per the build prompt) decides which IDs go to the caption and which to a strip. Part layout UNVERIFIED.
An empty claim-limit list counts as missing (UNVERIFIED reading of "REQUIRED list": a figure that truly has no limit needs a ruling).
"""
from __future__ import annotations

from dataclasses import dataclass

from . import style as S
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
    """'[panel] key=value' for each distinct (panel, key, value), in row order, joined by '; ' (value = the params.csv cell text)."""
    seen, parts = set(), []
    for r in rows:
        item = (r.get("panel", ""), r["key"], value_text(r["value"]))
        if item in seen:
            continue
        seen.add(item)
        parts.append((f"[{item[0]}] " if item[0] else "") + f"{item[1]}={item[2]}")
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
                  provenance_hash12=None, tag=None) -> Caption:
    """Caption text in the order of the template: take-home, parameters, spectrogram, symbols, claim limits, provenance pointer.

    take_home, claim_limit_ids: REQUIRED (default None, so leaving one out raises CaptionError, not TypeError). params_rows: the rows written to <ID>_params.csv (empty: part omitted). spectrogram: settings dict or None
    (part omitted). symbol_keys: keys of the style table whose marker is explained (an unknown key raises StyleError). provenance_hash12, tag: optional
    pointer (omitted when None).
    """
    take = _required_text(take_home, "take_home")
    limits = _required_ids(claim_limit_ids)
    p_str = parameter_string(params_rows)
    s_str = spectrogram_string(spectrogram) if spectrogram else ""
    parts = [f"{figure_id}. {take}"]
    if p_str:
        parts.append(f"Parameters: {p_str}.")
    if s_str:
        parts.append(f"Spectrogram: {s_str}.")
    if symbol_keys:
        parts.append("Symbols: " + "; ".join(f"{k} = {S.get(k).marker_name}" for k in symbol_keys) + ".")
    parts.append("Claim limits: " + ", ".join(limits) + ".")
    if provenance_hash12:
        parts.append(f"Provenance: {figure_id}_provenance.json hash12 {provenance_hash12}" + (f", tag {tag}" if tag else "") + ".")
    return Caption(" ".join(parts), p_str, s_str, limits)
