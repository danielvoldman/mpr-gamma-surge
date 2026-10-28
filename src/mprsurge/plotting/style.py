"""Fixed figure style table (MS13 13c; docs/ms13_conventions.md section 2, M13-2).

One colour, one marker and one line style per key, the same in every figure. Keys: the eight surge classes of plan Table 2.1 (the keys of
analysis.ms11_eval.CATEGORY), the paths P1 to P5 (P4a and P4b, which the plan names in S6 and F6, are their own keys), the controls NC1 to NC3, and
the sources (mean field, network where it agrees with the mean-field class, network where it does not, noise).

Everything in this file is a design choice, not a scientific parameter, and is UNVERIFIED: the plan gives no palette, no marker set, no font, no size
and no resolution (docs/ms13_plan.md M13-2, M13-14 (vii)). The hex values are placeholders chosen here, not taken from a published palette. The colour
simulation below uses 3x3 matrices and sRGB/CIELAB constants written from memory and not checked against a source (UNVERIFIED); it only REPORTS
differences, it has no pass line. Imports the standard library only, plus provenance (atomic write) inside write_colour_report; no simulation module, no matplotlib.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

UNVERIFIED = "UNVERIFIED"

# Placeholders until the journal is chosen (M13-14 (vii)); all UNVERIFIED.
FONT_FAMILY = "DejaVu Sans"
FONT_SIZE_PT = 8
PNG_DPI = 200
PLACEHOLDERS_STATUS = UNVERIFIED


class StyleError(KeyError):
    """A figure asked for a key that has no entry; there is no default style."""


@dataclass(frozen=True)
class Style:
    key: str
    family: str            # "class", "path", "control" or "source"
    colour: str            # hex, UNVERIFIED placeholder
    marker: str            # matplotlib marker code, unique over the whole table
    marker_name: str
    linestyle: str         # matplotlib line style; unique together with the marker


CLASS_KEYS = ("S+", "S-rel", "S-abs", "S-sus", "NS", "D-tr", "D-sus", "D-none")
PATH_KEYS = ("P1", "P2", "P3", "P4", "P4a", "P4b", "P5")
CONTROL_KEYS = ("NC1", "NC2", "NC3")
SOURCE_KEYS = ("mean_field", "network_agree", "network_disagree", "noise")

# key: (colour, marker, marker_name, linestyle)
_TABLE = {
    "class": {
        "S+": ("#b2182b", "o", "circle", "-"),
        "S-rel": ("#ef8a62", "s", "square", "-"),
        "S-abs": ("#e0b000", "^", "triangle up", "-"),
        "S-sus": ("#762a83", "v", "triangle down", "-"),
        "NS": ("#8c8c8c", "<", "triangle left", "-"),
        "D-tr": ("#2166ac", ">", "triangle right", "--"),
        "D-sus": ("#92c5de", "D", "diamond", "--"),
        "D-none": ("#1b7837", "d", "thin diamond", "--"),
    },
    "path": {
        "P1": ("#5e3c99", "p", "pentagon", "-"),
        "P2": ("#e66101", "h", "hexagon", "-"),
        "P3": ("#01665e", "H", "rotated hexagon", "-"),
        "P4": ("#c51b7d", "*", "star", "-"),
        "P4a": ("#f1b6da", "P", "plus (filled)", "--"),
        "P4b": ("#80cdc1", "X", "cross (filled)", "--"),
        "P5": ("#543005", "8", "octagon", "-."),
    },
    "control": {
        "NC1": ("#4d4d4d", "+", "plus", ":"),
        "NC2": ("#a6611a", "x", "cross", ":"),
        "NC3": ("#003c30", "1", "tri down", ":"),
    },
    "source": {
        "mean_field": ("#000000", "2", "tri up", "-"),
        "network_agree": ("#4575b4", "3", "tri left", "-."),
        "network_disagree": ("#d73027", "4", "tri right", "-."),
        "noise": ("#bdbdbd", "|", "vertical line", ":"),
    },
}

# Scalar colour map for frequencies and the contour marks (13e, DL-448): one fixed choice for every figure that shades by frequency or marks a
# frequency contour. Not entries of STYLE (they are not classes, paths, controls or sources), so the unique-marker table and the colour report are
# unchanged. UNVERIFIED design choices. FREQUENCY_CMAP is a matplotlib colour-map name (no matplotlib import here). A mark is drawn with a halo of
# HALO_COLOUR so it stays visible on the shading; the marker shapes differ from each other and from every marker in STYLE.
FREQUENCY_CMAP = "viridis"
HALO_COLOUR = "#ffffff"


@dataclass(frozen=True)
class ContourMark:
    hz: float
    marker: object         # matplotlib marker code or a vertex tuple
    marker_name: str
    colour: str
    size: float
    width: float           # width of the halo edge (HALO_COLOUR) around the filled mark


# 13g: the 25 Hz mark was a short horizontal bar, which lay along the slice line and was hard to see; it is now a tall narrow filled bar that crosses the
# slice line (vertex marker, so it shares no code with the '|' of the 'noise' key), with a white edge. UNVERIFIED design choice.
_TALL_BAR = ((-0.2, -1.0), (0.2, -1.0), (0.2, 1.0), (-0.2, 1.0), (-0.2, -1.0))
CONTOUR_MARKS = {
    "25hz": ContourMark(25.0, _TALL_BAR, "tall narrow bar across the slice line", "#1a1a1a", 13.0, 0.9),
    "100hz": ContourMark(100.0, ".", "point", "#7f0000", 6.0, 1.0),
}

# One-parameter diagram marks (13f, F2). Like the contour marks they are not entries of STYLE (they are not classes, paths, controls or sources),
# so the unique-marker table and the colour report are unchanged. The two sweep directions of a source differ in marker shape, not in colour alone.
# The network marks are NOT the 'network_agree' / 'network_disagree' keys: those mean a class agreement, and F2 has no classes and no agreement
# threshold (the plan gives none for the S4 network amplitudes). The mean-field marks are filled carets, the network marks open vertex shapes; both
# network shapes drawn on one point read as an eight-pointed star. UNVERIFIED design choices; marker None means a line without markers.
@dataclass(frozen=True)
class DiagramMark:
    key: str
    colour: str
    marker: object          # matplotlib marker code (a str or an int caret code) or None for a line
    marker_name: str
    linestyle: str
    size: float
    width: float
    filled: bool


# vertex markers (matplotlib reads a tuple of (x, y) points as a marker), so they share no code with the class/path/control/source markers
_SQUARE = ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0))
_DIAMOND = ((0.0, -1.4), (1.4, 0.0), (0.0, 1.4), (-1.4, 0.0), (0.0, -1.4))
DIAGRAM_MARKS = {
    "a5_cycle": DiagramMark("a5_cycle", "#111111", None, "line", "-", 0.0, 1.2, True),
    "a5_fixed_stable": DiagramMark("a5_fixed_stable", "#7a7a7a", None, "line", "-", 0.0, 2.2, True),
    "a5_fixed_unstable": DiagramMark("a5_fixed_unstable", "#7a7a7a", None, "line", "--", 0.0, 1.4, True),
    "hopf_point": DiagramMark("hopf_point", "#67001f", r"$\otimes$", "circled cross", ":", 10.0, 1.0, True),
    "s4_mf_up": DiagramMark("s4_mf_up", "#222222", 6, "caret up (up sweep)", "none", 3.5, 0.8, True),
    "s4_mf_down": DiagramMark("s4_mf_down", "#222222", 7, "caret down (down sweep)", "none", 3.5, 0.8, True),
    "s4_net_up": DiagramMark("s4_net_up", "#1f77b4", _SQUARE, "open square (up sweep)", "none", 6.0, 1.1, False),
    "s4_net_down": DiagramMark("s4_net_down", "#1f77b4", _DIAMOND, "open diamond (down sweep)", "none", 6.0, 1.1, False),
}


def diagram_mark(key: str) -> DiagramMark:
    """The mark of a one-parameter diagram element; an unknown key raises StyleError (no silent default)."""
    try:
        return DIAGRAM_MARKS[key]
    except KeyError:
        raise StyleError(f"no diagram mark for key {key!r}; known: {', '.join(DIAGRAM_MARKS)}") from None


STYLE: dict[str, Style] = {
    key: Style(key, family, *vals) for family, body in _TABLE.items() for key, vals in body.items()
}


def get(key: str) -> Style:
    """The style of a key; a key that is not in the table raises StyleError (no silent default)."""
    try:
        return STYLE[key]
    except KeyError:
        raise StyleError(f"no style for key {key!r}; known keys: {', '.join(STYLE)}") from None


def contour_mark(key: str) -> ContourMark:
    """The mark of a frequency contour ('25hz' or '100hz'); an unknown key raises StyleError (no silent default)."""
    try:
        return CONTOUR_MARKS[key]
    except KeyError:
        raise StyleError(f"no contour mark for key {key!r}; known keys: {', '.join(CONTOUR_MARKS)}") from None


def keys(family: str | None = None) -> list[str]:
    return [k for k, s in STYLE.items() if family is None or s.family == family]


# ---- colour-difference report (REPORT ONLY: no threshold, no pass line; the reviewer judges by eye) ----

# Linear-RGB simulation matrices for deuteranopia and protanopia (UNVERIFIED: written from memory, not checked against a source; each row sums to 1).
_SIM = {
    "deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
}
_RGB2XYZ = ((0.4124564, 0.3575761, 0.1804375), (0.2126729, 0.7151522, 0.0721750), (0.0193339, 0.1191920, 0.9503041))   # sRGB, D65 (UNVERIFIED)
_WHITE = (0.95047, 1.0, 1.08883)                                                                                       # D65 (UNVERIFIED)
VIEWS = ("normal", "deuteranopia", "protanopia", "greyscale")


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_linear(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(_lin(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


def _mul(m, v):
    return tuple(sum(m[i][j] * v[j] for j in range(3)) for i in range(3))


def _lab(xyz) -> tuple[float, float, float]:
    f = lambda t: t ** (1 / 3) if t > (6 / 29) ** 3 else t / (3 * (6 / 29) ** 2) + 4 / 29
    fx, fy, fz = (f(xyz[i] / _WHITE[i]) for i in range(3))
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def lab_of(hex_colour: str, view: str = "normal") -> tuple[float, float, float]:
    """CIELAB (D65) of a colour as seen in `view`. Greyscale: the luminance Y of the colour, as a neutral grey."""
    rgb = hex_to_linear(hex_colour)
    if view == "greyscale":
        y = _mul(_RGB2XYZ, rgb)[1]
        return _lab((_WHITE[0] * y, y, _WHITE[2] * y))
    if view in _SIM:
        rgb = tuple(min(1.0, max(0.0, c)) for c in _mul(_SIM[view], rgb))
    elif view != "normal":
        raise StyleError(f"unknown view {view!r}; known: {', '.join(VIEWS)}")
    return _lab(_mul(_RGB2XYZ, rgb))


def delta_e(a: str, b: str, view: str = "normal") -> float:
    """CIE76 colour difference between two hex colours in `view` (Euclidean distance in CIELAB; a stated, UNVERIFIED choice of measure)."""
    la, lb = lab_of(a, view), lab_of(b, view)
    return sum((x - y) ** 2 for x, y in zip(la, lb)) ** 0.5


REPORT_COLUMNS = ("key_a", "key_b", "same_family", *(f"dE76_{v}" for v in VIEWS))


def colour_report_rows() -> list[dict]:
    """Every pair of keys with its difference in each view. Values are numbers to be looked at; nothing is compared with a limit."""
    out = []
    for a, b in combinations(STYLE, 2):
        row = {"key_a": a, "key_b": b, "same_family": STYLE[a].family == STYLE[b].family}
        for v in VIEWS:
            row[f"dE76_{v}"] = round(delta_e(STYLE[a].colour, STYLE[b].colour, v), 3)
        out.append(row)
    return out


def colour_report_csv(rows: list[dict] | None = None) -> str:
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=REPORT_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(colour_report_rows() if rows is None else rows)
    return buf.getvalue()


def colour_report_summary(rows: list[dict] | None = None, n_lowest: int = 3) -> str:
    """Text: per view and family, the smallest differences. No pass or fail wording; the reviewer judges."""
    rows = colour_report_rows() if rows is None else rows
    lines = ["Colour-difference report (CIE76 dE in CIELAB). REPORT ONLY, no pass line, UNVERIFIED simulation constants and measure.",
             f"Placeholders flagged {UNVERIFIED}: colours, markers, line styles, font {FONT_FAMILY} {FONT_SIZE_PT} pt, PNG {PNG_DPI} dpi."]
    for fam in ("class", "path+control", "source"):
        fams = {"class": ("class",), "path+control": ("path", "control"), "source": ("source",)}[fam]
        inside = [r for r in rows if STYLE[r["key_a"]].family in fams and STYLE[r["key_b"]].family in fams]
        for v in VIEWS:
            low = sorted(inside, key=lambda r: r[f"dE76_{v}"])[:n_lowest]
            lines.append(f"{fam:13s} {v:13s} smallest: " + "; ".join(f"{r['key_a']}/{r['key_b']} {r[f'dE76_{v}']}" for r in low))
    return "\n".join(lines) + "\n"


def write_colour_report(directory) -> tuple[Path, Path]:
    """Write colour_report.csv (all pairs) and colour_report.txt (summary) into `directory`; returns both paths."""
    from ..provenance import atomic_write_text
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    rows = colour_report_rows()
    c, t = d / "colour_report.csv", d / "colour_report.txt"
    atomic_write_text(c, colour_report_csv(rows))
    atomic_write_text(t, colour_report_summary(rows))
    return c, t
