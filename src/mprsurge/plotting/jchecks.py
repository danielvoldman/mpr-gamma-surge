"""MS13 13t (DL-545 J4, J8, J13, J14; DL-546): the checks that scripts/ms13_verify_export.py and tests/test_ms13_13t.py run on a journal figure object and its exported files.

Colour conversions use pillow's ImageCms (littlecms), an installed package; no matrix is written here. No package that simulates colour-vision deficiency is installed, so there is
no such check (reported by the verifier as STOP). The PDF is read as bytes (zlib streams and object text) because no PDF-reading package is installed. The thresholds are the
UNVERIFIED values of configs/journal_export.yaml; the 0.05 constant of the contrast ratio is the one of the WCAG 2.x definition (UNVERIFIED here, from memory of the definition).
"""
from __future__ import annotations

import re
import zlib
from itertools import combinations
from pathlib import Path

import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.colors import to_hex, to_rgb
from matplotlib.lines import Line2D
from matplotlib.text import Annotation, Text

# ---- text, lines, colour maps ----


def text_sizes(fig, min_pt: float) -> list[str]:
    """Texts (with a string) whose font size is below min_pt."""
    return [f"{t.get_text()[:30]!r} {t.get_fontsize():g} pt" for t in fig.findobj(Text) if t.get_text() and t.get_visible() and t.get_fontsize() < min_pt - 1e-9]


def line_widths(fig, min_pt: float) -> list[str]:
    """Visible lines, patch outlines and spines drawn thinner than min_pt (a line width of zero means 'not drawn')."""
    from matplotlib.patches import Patch
    bad = []
    for ln in fig.findobj(Line2D):
        if ln.get_visible() and ln.get_linestyle() not in ("None", "none", "", " ") and 0 < ln.get_linewidth() < min_pt - 1e-9:
            bad.append(f"line {ln.get_gid() or ln.get_label()} {ln.get_linewidth():g} pt")
    for p in fig.findobj(Patch):
        if p.get_visible() and p.get_edgecolor()[3] > 0 and 0 < p.get_linewidth() < min_pt - 1e-9:
            bad.append(f"patch {p.get_gid() or type(p).__name__} {p.get_linewidth():g} pt")
    for ax in fig.axes:
        for sp in ax.spines.values():
            if sp.get_visible() and 0 < sp.get_linewidth() < min_pt - 1e-9:
                bad.append(f"spine {sp.get_linewidth():g} pt")
    return bad


def cmap_report(fig, cfg: dict) -> tuple[list[str], list[str]]:
    """(names of the continuous colour maps used, offenders). A colour map is allowed if its name without a trailing '_r' is in allowed_cmaps; a ListedColormap built from a
    list of colours ('from_list') is a categorical fill (classes, states), not a continuous scale, and is listed as 'categorical'."""
    allowed, forbidden = set(cfg["colour"]["allowed_cmaps"]), set(cfg["colour"]["forbidden_cmaps"])
    names, bad = [], []
    for sm in fig.findobj(lambda a: isinstance(a, ScalarMappable)):
        cm = sm.get_cmap()
        nm = cm.name
        import matplotlib
        if nm not in matplotlib.colormaps:                         # a ListedColormap built from a list of colours: a categorical fill, not a continuous scale
            names.append("categorical")
            continue
        base = nm[:-2] if nm.endswith("_r") else nm
        names.append(nm)
        if base in forbidden or base not in allowed:
            bad.append(nm)
    return sorted(set(names)), sorted(set(bad))


# ---- non-colour distinction ----

def _series(fig) -> list[dict]:
    """Drawn series of every axes: lines (colour, marker, line style, fill) and annotation arrows (colour, line style, and the marker of the start mark with the same gid suffix)."""
    out = []
    for i, ax in enumerate(fig.axes):
        starts = {ln.get_gid()[6:]: ln for ln in ax.lines if (ln.get_gid() or "").startswith("start:")}
        for ln in ax.lines:
            if not ln.get_visible() or len(ln.get_xdata()) == 0 or (ln.get_gid() or "").startswith("start:"):
                continue
            mk = ln.get_marker() if ln.get_marker() not in ("None", "none", "", " ", None) else "none"
            ls = ln.get_linestyle() if ln.get_linestyle() not in ("None", "none", "", " ") else "none"
            out.append({"ax": i, "name": ln.get_gid() or ln.get_label(), "colour": to_hex(ln.get_color() if mk == "none" else ln.get_markerfacecolor() if ln.get_markerfacecolor() not in ("none", None) else ln.get_markeredgecolor()),
                        "sig": (str(mk), str(ls), ln.get_fillstyle())})
        for t in ax.texts:
            if isinstance(t, Annotation) and t.arrow_patch is not None and t.get_gid():
                gid = t.get_gid()
                if not gid.startswith("arrow:"):
                    continue
                st = starts.get(gid[6:])
                mk = str(st.get_marker()) if st is not None else "none"
                out.append({"ax": i, "name": gid, "colour": to_hex(t.arrow_patch.get_edgecolor()), "sig": (mk, str(t.arrow_patch.get_linestyle()), "arrow")})
    return out


def non_colour_violations(fig) -> list[str]:
    """Pairs of series in one axes that differ in colour only (same marker, same line style, same fill style)."""
    bad = []
    for i, ax in enumerate(fig.axes):
        ser = [s for s in _series(fig) if s["ax"] == i]
        for a, b in combinations(ser, 2):
            if a["colour"] != b["colour"] and a["sig"] == b["sig"]:
                bad.append(f"axes {i}: {a['name']} and {b['name']} differ in colour only")
    return sorted(set(bad))


# ---- lightness and contrast through ImageCms ----

_T = {}


def _transform(target: str):
    if target not in _T:
        from PIL import ImageCms
        _T[target] = ImageCms.buildTransform(ImageCms.createProfile("sRGB"), ImageCms.createProfile(target), "RGB", "LAB" if target == "LAB" else "RGB")
    return _T[target]


def lightness(colour) -> float:
    """CIELAB L* of a colour (0 to 100) through littlecms (ImageCms): sRGB profile to the LAB profile."""
    from PIL import Image, ImageCms
    r, g, b = (int(round(255 * c)) for c in to_rgb(colour))
    im = Image.new("RGB", (1, 1), (r, g, b))
    lab = ImageCms.applyTransform(im, _transform("LAB"))
    return float(lab.getpixel((0, 0))[0]) * 100.0 / 255.0


def luminance(colour) -> float:
    """Relative luminance Y (0 to 1) from L* (Y = ((L* + 16) / 116)^3 above the small-value limit; the CIE relation between L* and Y)."""
    L = lightness(colour)
    return ((L + 16.0) / 116.0) ** 3 if L > 8.0 else L / 903.3


def contrast_ratio(fg, bg) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def close_in_lightness(fig, min_diff: float) -> list[str]:
    """Series colours of one axes whose L* differ by less than min_diff (the greyscale report). Informative: such a pair must also differ in a non-colour attribute (non_colour_violations)."""
    out = []
    for i, ax in enumerate(fig.axes):
        cols = {s["colour"] for s in _series(fig) if s["ax"] == i}
        for a, b in combinations(sorted(cols), 2):
            d = abs(lightness(a) - lightness(b))
            if d < min_diff:
                out.append(f"axes {i}: {a} and {b} (L* difference {d:.1f})")
    return out


def _hue_class(colour) -> str:
    import colorsys
    h, s, v = colorsys.rgb_to_hsv(*to_rgb(colour))
    if s < 0.25 or v < 0.15:
        return "neutral"
    h *= 360.0
    if h < 25 or h > 335:
        return "red"
    if 75 <= h <= 165:
        return "green"
    return "other"


def red_green_pairs(fig, min_diff: float) -> list[str]:
    """A red and a green series colour in one axes whose lightness differs by less than min_diff."""
    out = []
    for i, ax in enumerate(fig.axes):
        cols = {s["colour"] for s in _series(fig) if s["ax"] == i}
        for a, b in combinations(sorted(cols), 2):
            if {_hue_class(a), _hue_class(b)} == {"red", "green"} and abs(lightness(a) - lightness(b)) < min_diff:
                out.append(f"axes {i}: {a} and {b}")
    return out


def text_contrast(fig, min_ratio: float, face_of_gid: dict | None = None) -> list[str]:
    """Texts whose colour against its background (white, or the face colour of its schematic box) is below min_ratio."""
    bad = []
    for t in fig.findobj(Text):
        if not t.get_text() or not t.get_visible():
            continue
        gid = t.get_gid() or ""
        bg = "#ffffff"
        if gid.startswith("schematic:") and face_of_gid:
            bg = face_of_gid.get(gid.split(":")[1], bg)
        r = contrast_ratio(t.get_color(), bg)
        if r < min_ratio:
            bad.append(f"{t.get_text()[:30]!r} {r:.2f}")
    return bad


IMAGE_FORBIDDEN = (re.compile(r"DRAFT", re.I), re.compile(r"\bDL-\d+"), re.compile(r"provenance", re.I), re.compile(r"as ruled", re.I), re.compile(r"untagged", re.I),
                   re.compile(r"UNVERIFIED"), re.compile(r"hash12"), re.compile(r"\bG10\b"))


def image_text_violations(fig) -> list[str]:
    """Texts on the image that carry draft marks, decision-log numbers or provenance text (J2). A figure number or caption inside the file is not tested here."""
    out = []
    for t in fig.findobj(Text):
        s = t.get_text()
        if s and any(p.search(s) for p in IMAGE_FORBIDDEN):
            out.append(s[:40])
    return out


# ---- exported files ----

def pdf_report(path) -> dict:
    """Read a PDF as bytes: the page box (pt), the font object subtypes, whether a Type 3 font occurs, the number of font descriptors and embedded TrueType font files, the base font
    names and the sizes of the font-size operators (Tf) in the content streams."""
    b = Path(path).read_bytes()
    box = re.search(rb"/MediaBox\s*\[\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s*\]", b)
    sizes = set()
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", b, re.S):
        try:
            s = zlib.decompress(m.group(1))
        except zlib.error:
            continue
        sizes.update(float(x) for x in re.findall(rb"/\w+\s+([\d.]+)\s+Tf", s))
    return {"mediabox": tuple(float(x) for x in box.groups()) if box else None, "type3": b"/Type3" in b, "descriptors": len(re.findall(rb"/Type\s*/FontDescriptor", b)),
            "fontfile2": len(re.findall(rb"/FontFile2", b)), "fontfile3": len(re.findall(rb"/FontFile3", b)), "basefonts": sorted({m.decode("latin1") for m in re.findall(rb"/BaseFont\s*/([\w+\-]+)", b)}),
            "tf_sizes": sorted(sizes), "bytes": len(b)}


def tiff_report(path) -> dict:
    from PIL import Image
    im = Image.open(path)
    return {"mode": im.mode, "compression": im.info.get("compression"), "dpi": tuple(round(x) for x in im.info.get("dpi", (0, 0))), "size": im.size}


def bad_file_names(folder, pattern: str) -> list[str]:
    rx = re.compile(pattern)
    return [str(p.relative_to(folder)) for p in Path(folder).rglob("*") if p.is_file() and not rx.match(p.name)]


def case_mismatches(names, folder) -> list[str]:
    """Names (relative to folder) that exist only with a different letter case on disk."""
    folder = Path(folder)
    out = []
    for n in names:
        p = folder / n
        listing = {q.name for q in p.parent.iterdir()} if p.parent.is_dir() else set()
        if p.name not in listing:
            out.append(n)
    return out
