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
_OCTAGON = ((0.4, 1.0), (1.0, 0.4), (1.0, -0.4), (0.4, -1.0), (-0.4, -1.0), (-1.0, -0.4), (-1.0, 0.4), (-0.4, 1.0), (0.4, 1.0))
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
_BAR = ((-1.0, -0.22), (1.0, -0.22), (1.0, 0.22), (-1.0, 0.22), (-1.0, -0.22))
DIAGRAM_MARKS = {
    "a5_cycle": DiagramMark("a5_cycle", "#111111", None, "line", "-", 0.0, 1.2, True),
    "a5_fixed_stable": DiagramMark("a5_fixed_stable", "#7a7a7a", None, "line", "-", 0.0, 2.2, True),
    "a5_fixed_unstable": DiagramMark("a5_fixed_unstable", "#7a7a7a", None, "line", "--", 0.0, 1.4, True),
    "hopf_point": DiagramMark("hopf_point", "#67001f", r"$\otimes$", "circled cross", ":", 10.0, 1.0, True),
    "s4_mf_up": DiagramMark("s4_mf_up", "#222222", 6, "caret up (up sweep)", "none", 3.5, 0.8, True),
    "s4_mf_down": DiagramMark("s4_mf_down", "#222222", 7, "caret down (down sweep)", "none", 3.5, 0.8, True),
    "s4_net_up": DiagramMark("s4_net_up", "#1f77b4", _SQUARE, "open square (up sweep)", "none", 6.0, 1.1, False),
    "s4_net_down": DiagramMark("s4_net_down", "#1f77b4", _DIAMOND, "open diamond (down sweep)", "none", 6.0, 1.1, False),
    # 13h, FS1 (M2 diagram, K4 and K5 traces, ring map). UNVERIFIED design choices, like every mark above.
    "m2_fold": DiagramMark("m2_fold", "#2b2b2b", None, "line", "-", 0.0, 1.0, True),
    "m2_cusp": DiagramMark("m2_cusp", "#8c510a", r"$\oplus$", "circled plus", "none", 9.0, 1.0, True),
    "m2_k_point": DiagramMark("m2_k_point", "#5d4037", r"$\odot$", "circled dot", "none", 9.0, 1.0, True),
    "s1_k4_trace": DiagramMark("s1_k4_trace", "#1f3a5f", None, "line", "-", 0.0, 0.9, True),
    "s1_k5_trace": DiagramMark("s1_k5_trace", "#0b6e4f", None, "line", "-", 0.0, 0.9, True),
    "s1_forcing": DiagramMark("s1_forcing", "#7a7a7a", None, "line", ":", 0.0, 0.9, True),
    "k4_window": DiagramMark("k4_window", "#a05a00", None, "line", "-.", 0.0, 0.8, True),
    "k4_r_star": DiagramMark("k4_r_star", "#7a7a7a", None, "line", "--", 0.0, 0.8, True),
    # 13h, FS2 (M3 validation K7 to K11). Marker glyphs are mathtext symbols (strings that no STYLE marker uses). UNVERIFIED design choices.
    "s3_mf": DiagramMark("s3_mf", "#222222", r"$\bullet$", "filled dot (mean field)", "-", 7.0, 1.0, True),
    "s3_net_1e4": DiagramMark("s3_net_1e4", "#1f77b4", r"$\circ$", "open circle (network N = 1e4)", "-", 7.0, 0.6, False),
    "s3_net_5e4": DiagramMark("s3_net_5e4", "#2a9d8f", r"$\diamond$", "open diamond (network N = 5e4)", "-", 7.0, 0.6, False),
    "k7_paper": DiagramMark("k7_paper", "#b35806", None, "line", "--", 0.0, 1.0, True),
    "tol_band": DiagramMark("tol_band", "#9a9a9a", None, "line", "--", 0.0, 0.7, True),
    "k9_pt": DiagramMark("k9_pt", "#4a148c", r"$\star$", "star outline (K9 ratio)", "none", 9.0, 1.0, True),
    "k11_pt": DiagramMark("k11_pt", "#006d77", r"$\ast$", "asterisk (K11 ratio)", "none", 8.0, 1.0, True),
    "k10_curve": DiagramMark("k10_curve", "#0b6e4f", None, "line", "-", 0.0, 1.2, True),
    "k10_j8": DiagramMark("k10_j8", "#8c6d1f", r"$\triangle$", "triangle up outline (8 ms)", "-", 7.0, 0.7, True),
    "k10_j20": DiagramMark("k10_j20", "#2f4f4f", r"$\boxdot$", "square with dot (20 ms)", "--", 7.0, 0.7, True),
    "k10_j40": DiagramMark("k10_j40", "#7b3f00", r"$\triangledown$", "triangle down outline (40 ms)", ":", 7.0, 0.7, True),
    # 13i, FS5 (classifier tests and sensitivity; frequency mapping). UNVERIFIED design choices. One mark per window W of the reachability panel (the windows of
    # the plan's T_ramp ladder, in increasing order), the two taus of RB9(a), the RB9(b) frequencies, the 1/tau expectation of RB9(d), a point for a stored
    # fraction and the 'not run' cell of the class matrix.
    "w_0": DiagramMark("w_0", "#440154", r"$\clubsuit$", "club (W 0.2 s)", "-", 7.0, 0.8, True),
    "w_1": DiagramMark("w_1", "#3b528b", r"$\spadesuit$", "spade (W 0.333 s)", "--", 7.0, 0.8, True),
    "w_2": DiagramMark("w_2", "#21918c", r"$\heartsuit$", "heart outline (W 0.593 s)", "-.", 7.0, 0.8, True),
    "w_3": DiagramMark("w_3", "#4c9a2a", r"$\diamondsuit$", "diamond suit outline (W 1.054 s)", ":", 7.0, 0.8, True),
    "w_4": DiagramMark("w_4", "#9c7a00", r"$\bowtie$", "bowtie (W 1.874 s)", (0, (5, 1, 1, 1, 1, 1)), 7.0, 0.8, True),
    "w_5": DiagramMark("w_5", "#5a5a00", r"$\dagger$", "dagger (W 2 s)", (0, (1, 3)), 7.0, 0.8, True),
    "rb9a_0": DiagramMark("rb9a_0", "#34495e", r"$\bullet$", "filled dot (tau 10 ms)", "none", 6.0, 1.0, True),
    "rb9a_1": DiagramMark("rb9a_1", "#a04000", r"$\circ$", "open circle (tau 20 ms)", "none", 6.0, 1.0, False),
    "fs5_spectral": DiagramMark("fs5_spectral", "#34495e", r"$\bullet$", "filled dot (spectral peak)", "none", 7.0, 1.0, True),
    "fs5_cycle": DiagramMark("fs5_cycle", "#a04000", r"$\diamond$", "diamond outline (cycle frequency)", "none", 7.0, 1.0, False),
    "fs5_expected": DiagramMark("fs5_expected", "#5d4037", r"$\ast$", "asterisk (headline x 10/tau)", "none", 7.0, 1.0, True),
    "fs5_pt": DiagramMark("fs5_pt", "#4a148c", r"$\star$", "star outline (stored fraction)", "none", 7.0, 1.0, True),
    "not_run": DiagramMark("not_run", "#555555", r"$\times$", "cross (not run)", "none", 4.0, 0.6, True),
    # 13i, FS4 (numerics). UNVERIFIED design choices. The raw first crossing is a small nabla on the class marker of the classifier onset; the D43 floor levels
    # are three vertex shapes; the three network seeds are their own digits (marker, colour and line style differ); the PSD-argmax reading is a circled dot.
    "fs4_cross": DiagramMark("fs4_cross", "#262626", r"$\nabla$", "nabla (raw first crossing)", "none", 4.5, 0.6, True),
    "fs4_l0": DiagramMark("fs4_l0", "#7a3b00", _SQUARE, "open square (floor level 0)", "none", 5.0, 1.0, False),
    "fs4_l1": DiagramMark("fs4_l1", "#005f73", _DIAMOND, "open diamond (floor level 1)", "none", 5.0, 1.0, False),
    "fs4_l2": DiagramMark("fs4_l2", "#6b2d5c", ((-1.0, -1.0), (1.0, -1.0), (0.0, 1.3), (-1.0, -1.0)), "open triangle (floor level 2)", "none", 5.0, 1.0, False),
    "fs4_s0": DiagramMark("fs4_s0", "#264653", r"$\mathbf{0}$", "digit 0 (network seed 0)", "-", 7.0, 0.8, True),
    "fs4_s1": DiagramMark("fs4_s1", "#9c4f00", r"$\mathbf{1}$", "digit 1 (network seed 1)", "--", 7.0, 0.8, True),
    "fs4_s2": DiagramMark("fs4_s2", "#5f0f40", r"$\mathbf{2}$", "digit 2 (network seed 2)", ":", 7.0, 0.8, True),
    "fs4_psd": DiagramMark("fs4_psd", "#333333", r"$\bigcirc$", "large open circle (PSD argmax reading)", "none", 10.0, 0.7, False),
    "fs4_vp100": DiagramMark("fs4_vp100", "#34495e", r"$\bullet$", "filled dot (V_p +-100)", "none", 6.0, 1.0, True),
    "fs4_vp200": DiagramMark("fs4_vp200", "#a04000", r"$\circ$", "open circle (V_p +-200)", "none", 6.0, 1.0, False),
    # 13k (DL-482), FS3: the stored median of a per-N range. Its own mark (a short horizontal bar across the range line); the star of 'fs5_pt' keeps its single
    # meaning (a stored fraction in FS5). UNVERIFIED design choice.
    "fs3_median": DiagramMark("fs3_median", "#4a148c", _BAR, "short horizontal bar (stored median)", "none", 9.0, 1.0, True),
    # 13k (DL-482, DL-483), F4 (ramp rate). UNVERIFIED design choices. The A4 prediction and the quasi-static reference are lines; a run inside the RB3(a) range
    # carries a large open octagon; the classifier-onset reading is a small double dagger (the raw crossing, the primary reading, is the path mark); the down-sweep offset
    # of P5 is a filled down triangle, its hysteresis width a dashed line; an RB6-FAIL result carries a boxed cross.
    "f4_pred": DiagramMark("f4_pred", "#6d4c00", None, "line", "-.", 0.0, 1.0, True),
    "f4_ref": DiagramMark("f4_ref", "#7a7a7a", None, "line", ":", 0.0, 1.0, True),
    "f4_inrange": DiagramMark("f4_inrange", "#1b1b1b", _OCTAGON, "large open octagon (inside the RB3(a) range)", "none", 11.0, 0.9, False),
    "f4_cls": DiagramMark("f4_cls", "#333333", r"$\ddagger$", "double dagger (classifier onset)", "none", 6.0, 0.7, True),
    "f4_down": DiagramMark("f4_down", "#5f4b8b", r"$\blacktriangledown$", "filled down triangle (P5 down-sweep offset)", "-", 6.0, 0.9, True),
    "f4_hyst": DiagramMark("f4_hyst", "#5f4b8b", None, "line", "--", 0.0, 1.0, True),
    "f4_fail": DiagramMark("f4_fail", "#7f0000", r"$\boxtimes$", "boxed cross (RB6 FAIL)", "none", 12.0, 1.0, True),
}

# 13h, FS1: fill of the A1 root-count map (one root, three roots) and the colour map of the A2 cycles per e-fold. The A2 ring frequency uses
# FREQUENCY_CMAP (one frequency colour map for every figure). UNVERIFIED design choices.
ROOT_COUNT_COLOURS = {1: "#e8eef4", 3: "#f3cfa6"}
CYCLES_CMAP = "cividis"
# 13i, FS5: fill of the class-change fraction matrix, and a hatch per class so that no class rests on colour alone in a stacked bar. UNVERIFIED design choices.
CHANGE_CMAP = "YlOrBr"
CLASS_HATCH = {"S+": "", "S-rel": "//", "S-abs": "xx", "S-sus": "..", "NS": "\\\\", "D-tr": "--", "D-sus": "++", "D-none": "oo"}

# 13k (DL-482): the plain colours, hatches and point sizes that FS3, F6 and F4 draw (edges, text, reference lines, bar fills, the F6 map greys). Not entries of STYLE
# (they are not classes, paths, controls or sources) and not marks, so the unique-marker table, the colour report and the diagram-mark colour test are unchanged. A figure
# asks for a key; an unknown key raises StyleError. Every value is an UNVERIFIED design choice. The numbers are the ones the 13j drafts drew with.
FIGURE_COLOURS = {
    "bar_edge": "#333333",       # edge of a bar or of a class point
    "bar_edge_dark": "#222222",  # edge of the F6 count bars
    "range_line": "#555555",     # a min-to-max range line, and the text of a control count
    "fail_text": "#7f0000",      # a title or status text that names a FAIL or a draft
    "text_dark": "#222222",      # a gate status that passed
    "gate_line": "#000000",      # the RB2 gate line
    "subgrid_bar": "#9ecae1",    # the bar of the stored subgrid count
    "label_box": "#ffffff",      # face of the box behind a number printed on a bar
    "open_fill": "#ffffff",      # fill of an open (any-label) bar
    "map1_fill": "#6a6a6a",      # F6 map 1 bars
    "map2_fill": "#b5b5b5",      # F6 map 2 bars
}
FIGURE_HATCHES = {"map1_any": "//", "map2_any": ".."}
POINT_SIZES = {"fs3_shape": 7.0, "f6_control": 6.5, "f6_network_run": 9.0, "f6_s6_line": 4.5, "f6_s6_line_large": 5.5,
               "f4_series": 4.2, "f4_series_small": 3.4, "f4_series_p5": 3.6, "f4_none": 4.0, "f4_seed_tick": 5.0, "f4_key": 7.0, "f4_m2": 5.0, "f4_floor_rungs": (9.0, 7.0, 5.0, 3.0)}
POINT_EDGE_WIDTH = {"class": 0.4, "class_large": 0.5}

# 13l, F1 (DL-485 onward). UNVERIFIED design choices, plain scalars (not entries of STYLE, FIGURE_COLOURS or DIAGRAM_MARKS, so the unique-mark table and the pinned key sets are unchanged):
# the colour map of the spectrogram power (a display transform, 10 log10 of the stored-routine PSD), the two raster marks (a pixel for the whole record, a tick for a one-second window)
# and the point sizes and line widths of the F1 drawing code.
SPECTROGRAM_CMAP = "magma"
RASTER_MARKS = {"full": ",", "zoom": "|"}
F1_SIZES = {"raster_zoom": 2.4, "onset": 5.0, "key": 7.0, "envelope_line": 0.45, "envelope_alpha": 0.3, "path_line": 1.0, "event_line": 0.7}


def figure_colour(key: str) -> str:
    """A plain figure colour (edge, text, reference line, fill); an unknown key raises StyleError (no silent default)."""
    try:
        return FIGURE_COLOURS[key]
    except KeyError:
        raise StyleError(f"no figure colour for key {key!r}; known: {', '.join(FIGURE_COLOURS)}") from None


def figure_hatch(key: str) -> str:
    """A hatch of an open bar; an unknown key raises StyleError."""
    try:
        return FIGURE_HATCHES[key]
    except KeyError:
        raise StyleError(f"no figure hatch for key {key!r}; known: {', '.join(FIGURE_HATCHES)}") from None


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

# 13m, F5 (DL-490 onward). UNVERIFIED design choices, plain scalars (not entries of STYLE, FIGURE_COLOURS or DIAGRAM_MARKS, so the unique-mark table and the pinned key sets are
# unchanged): the colours and marks of the three agreement states of a subgrid cell (agree, disagree, tie; the marks differ so that no state rests on colour alone), the frame of the
# post-hoc panel, and the point sizes and line widths of the F5 drawing code.
F5_COLOURS = {"agree": "#1b7837", "disagree": "#762a83", "tie": "#bf812d", "frame_posthoc": "#7f7f7f", "cell_edge": "#ffffff", "net_halo": "#ffffff"}
F5_STATE_MARKS = {"agree": "o", "disagree": "x", "tie": "+"}
F5_SIZES = {"map_mark": 2.0, "state_mark": 2.0, "net_symbol": 9.5, "net_halo_width": 3.6, "net_width": 1.3, "cell_edge_width": 0.15, "table_mark": 6.0, "seed_mark": 4.2,
            "control_mark_width": 0.9, "range_line": 0.9, "median_bar": 4.0, "ref_line": 0.8, "key_mark": 5.0}
