"""MS13 13t (J8, J15 A): collision checker for the journal export. Works on the final matplotlib figure object at the export size; reads the rendered extents of the artists.

Objects tested (display space, pixels at the figure's dpi; the pad is the config's collision_pad_pt):
  texts      titles, axis labels, tick labels, in-axes texts and annotations (the text box only, not the arrow), legend texts, figure texts;
  legends    the legend box;
  artists    lines (segments, and markers with their size), scatter collections (marker extents), images and meshes (their data extent), patches (filled: the box;
             unfilled: the outline), annotation arrows (as lines), rasterized artists count as images;
  frames     the frame of every axes that has one, the figure edge.
Pair tests: text-text; text-artist; legend-artist; legend-text; text-frame (other axes, and own axes for in-axes texts); text and legend against the figure edge; clipped text
(clip_on and the box leaves its axes); marker-marker between different non-rasterized artists of one axes.
A hit is (kind, panel, a, b). An allow-list entry (AllowEntry) removes hits whose kind, panel and descriptors match; every entry carries a reason.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
from matplotlib.collections import PathCollection, QuadMesh
from matplotlib.image import AxesImage
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch
from matplotlib.text import Annotation, Text
from matplotlib.transforms import Bbox

LETTER = re.compile(r"^\(([a-z])\)")


@dataclass(frozen=True)
class Hit:
    kind: str
    panel: str
    a: str
    b: str

    def __str__(self) -> str:
        return f"[{self.kind}] panel {self.panel}: {self.a}  <->  {self.b}"


@dataclass(frozen=True)
class AllowEntry:
    kind: str                 # a Hit kind, or "*"
    panel: str                # panel letter, or "*"
    a: str                    # regular expression searched in Hit.a
    b: str                    # regular expression searched in Hit.b
    reason: str               # why the overlap is intended (required)

    def matches(self, h: Hit) -> bool:
        return (self.kind in ("*", h.kind) and self.panel in ("*", h.panel) and re.search(self.a, h.a) is not None and re.search(self.b, h.b) is not None) or \
               (self.kind in ("*", h.kind) and self.panel in ("*", h.panel) and re.search(self.a, h.b) is not None and re.search(self.b, h.a) is not None)


def panel_letter(ax, index: int) -> str:
    gid = ax.get_gid() or ""
    if gid.startswith("panel:"):
        return gid[6:]
    for title in (ax.get_title(loc="left"), ax.get_title()):
        m = LETTER.match(title or "")
        if m:
            return m.group(1)
    return f"ax{index}"


def _short(t: str, n: int = 36) -> str:
    return t.replace("\n", " ")[:n]


def text_box(t: Text, rend) -> Bbox:
    return Text.get_window_extent(t, rend)            # the text only (an Annotation's own method would add the arrow)


def _inflate(b: Bbox, d: float) -> Bbox:
    return Bbox.from_extents(b.x0 - d, b.y0 - d, b.x1 + d, b.y1 + d)


def _overlap(a: Bbox, b: Bbox) -> bool:
    return a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1


def _contains(outer: Bbox, inner: Bbox) -> bool:
    return outer.x0 <= inner.x0 and outer.y0 <= inner.y0 and outer.x1 >= inner.x1 and outer.y1 >= inner.y1


def segments_hit_box(pts: np.ndarray, box: Bbox, clip: Bbox | None) -> bool:
    """True if a polyline (display points, NaN rows break it) passes through `box`; when `clip` is given only the part of the line inside `clip` counts."""
    if len(pts) < 2:
        return False
    p0, p1 = pts[:-1], pts[1:]
    ok = np.isfinite(p0).all(axis=1) & np.isfinite(p1).all(axis=1)
    p0, p1 = p0[ok], p1[ok]
    if len(p0) == 0:
        return False
    d = p1 - p0
    t0 = np.zeros(len(p0))
    t1 = np.ones(len(p0))
    alive = np.ones(len(p0), bool)
    for pcoef, q in ((-d[:, 0], p0[:, 0] - box.x0), (d[:, 0], box.x1 - p0[:, 0]), (-d[:, 1], p0[:, 1] - box.y0), (d[:, 1], box.y1 - p0[:, 1])):
        zero = pcoef == 0
        alive &= ~(zero & (q < 0))
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.where(zero, 0.0, q / np.where(zero, 1.0, pcoef))
        neg = (pcoef < 0) & ~zero
        pos = (pcoef > 0) & ~zero
        t0 = np.where(neg, np.maximum(t0, r), t0)
        t1 = np.where(pos, np.minimum(t1, r), t1)
    alive &= t0 <= t1
    if not alive.any():
        return False
    if clip is None:
        return True
    mid = p0[alive] + d[alive] * ((t0[alive] + t1[alive]) / 2.0)[:, None]
    return bool(((mid[:, 0] >= clip.x0) & (mid[:, 0] <= clip.x1) & (mid[:, 1] >= clip.y0) & (mid[:, 1] <= clip.y1)).any())


@dataclass
class _Art:
    name: str
    ax: object
    kind: str                      # "line", "marks", "image", "patch_filled", "patch_edge", "container"
    box: Bbox | None = None        # image, patches
    pts: np.ndarray | None = None  # line vertices or marker centres (display)
    hw: float = 0.0                # marker half width in px
    hh: float = 0.0                # marker half height in px
    clip: Bbox | None = None
    rasterized: bool = False
    gid: str = ""


def marker_half_extent(marker, size_pt: float, edge_pt: float, dpi: float) -> tuple[float, float]:
    """(half width, half height) in pixels of a marker of `size_pt` (the marker path's own extent, so a tall narrow bar is narrow)."""
    from matplotlib.markers import MarkerStyle
    ms = marker if isinstance(marker, MarkerStyle) else MarkerStyle(marker)
    try:
        path, tr = ms.get_path(), ms.get_transform()
        ext = tr.transform_path(path).get_extents()
        hw, hh = max(abs(ext.x0), abs(ext.x1)), max(abs(ext.y0), abs(ext.y1))
    except Exception:
        hw = hh = 0.5
    k = size_pt * dpi / 72.0
    e = 0.5 * edge_pt * dpi / 72.0
    return hw * k + e, hh * k + e


def _line_art(ln: Line2D, ax, dpi: float, panel: str) -> list[_Art]:
    xy = np.asarray(ln.get_xydata(), float)
    if xy.size == 0:
        return []
    pts = ln.get_transform().transform(xy)
    out = []
    name = f"line:{ln.get_gid() or ln.get_label()}"
    clip = ax.bbox if ln.get_clip_on() else None
    if ln.get_linestyle() not in ("None", "none", "", " ") and ln.get_linewidth() > 0:
        out.append(_Art(name, ax, "line", pts=pts, clip=clip, gid=ln.get_gid() or ""))
    if ln.get_marker() not in ("None", "none", "", " ", None):
        pm = pts[np.isfinite(pts).all(axis=1)]
        if clip is not None:
            pm = pm[(pm[:, 0] >= clip.x0) & (pm[:, 0] <= clip.x1) & (pm[:, 1] >= clip.y0) & (pm[:, 1] <= clip.y1)]
        if len(pm):
            hw, hh = marker_half_extent(ln.get_marker(), float(ln.get_markersize()), float(ln.get_markeredgewidth()), dpi)
            out.append(_Art(name.replace("line:", "marks:"), ax, "marks", pts=pm, hw=hw, hh=hh, rasterized=bool(ln.get_rasterized()), gid=ln.get_gid() or ""))
    return out


def _collect(fig, rend) -> tuple[list, list, list, list]:
    """texts [(Text, owner_ax|None, role, panel)], legends [(Legend, ax, panel)], artists [_Art], frames [(ax, Bbox, panel)]."""
    dpi = fig.dpi
    texts, legends, arts, frames = [], [], [], []
    for i, ax in enumerate(fig.axes):
        panel = panel_letter(ax, i)
        if ax.get_frame_on() and ax.axison:
            frames.append((ax, ax.bbox, panel))
        for role, t in (("title", ax._left_title), ("title", ax.title), ("title", ax._right_title), ("xlabel", ax.xaxis.label), ("ylabel", ax.yaxis.label)):
            if t.get_text() and t.get_visible():
                texts.append((t, ax, role, panel))
        if ax.axison:
            for axis, which in ((ax.xaxis, 0), (ax.yaxis, 1)):
                lo, hi = sorted(axis.get_view_interval())
                for ticks in (axis.get_major_ticks(), axis.get_minor_ticks()):
                    for tk in ticks:
                        t = tk.label1
                        if t.get_text() and t.get_visible() and tk.get_loc() is not None and lo - 1e-9 * abs(hi - lo) <= tk.get_loc() <= hi + 1e-9 * abs(hi - lo):
                            texts.append((t, ax, "tick", panel))
        for t in ax.texts:
            if t.get_text() and t.get_visible():
                texts.append((t, ax, "text", panel))
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            legends.append((leg, ax, panel))
            for t in leg.get_texts():
                if t.get_text():
                    texts.append((t, ax, "legend", panel))
        for ln in ax.lines:
            if ln.get_visible():
                arts += _line_art(ln, ax, dpi, panel)
        for t in ax.texts:                                         # annotation arrows are lines
            if isinstance(t, Annotation) and t.arrow_patch is not None and t.get_visible():
                path = t.arrow_patch.get_path()
                tr = t.arrow_patch.get_transform()
                for poly in tr.transform_path(path).to_polygons(closed_only=False):
                    arts.append(_Art(f"arrow:{t.get_gid() or _short(t.get_text())}", ax, "line", pts=np.asarray(poly), clip=None, gid=t.get_gid() or ""))
        for c in ax.collections:
            if not c.get_visible():
                continue
            if isinstance(c, PathCollection) and not c.get_rasterized():
                off = c.get_offset_transform().transform(np.asarray(c.get_offsets(), float))
                sizes = np.asarray(c.get_sizes(), float)
                r = (np.sqrt(sizes.max() if sizes.size else 4.0) / 2.0) * dpi / 72.0
                pm = off[np.isfinite(off).all(axis=1)]
                pm = pm[(pm[:, 0] >= ax.bbox.x0) & (pm[:, 0] <= ax.bbox.x1) & (pm[:, 1] >= ax.bbox.y0) & (pm[:, 1] <= ax.bbox.y1)]
                if len(pm):
                    arts.append(_Art(f"marks:{c.get_gid() or c.get_label()}", ax, "marks", pts=pm, hw=r, hh=r))
            else:
                try:
                    dl = c.get_datalim(ax.transData)
                    box = Bbox.intersection(ax.transData.transform_bbox(dl), ax.bbox) if np.isfinite(dl.extents).all() else ax.bbox
                except Exception:
                    box = ax.bbox
                if box is not None:
                    arts.append(_Art(f"image:{c.get_gid() or type(c).__name__}", ax, "image", box=box, rasterized=True))
        for im in ax.images:
            if im.get_visible():
                arts.append(_Art(f"image:{im.get_gid() or 'AxesImage'}", ax, "image", box=im.get_window_extent(rend), rasterized=True))
        for p in ax.patches:
            if not p.get_visible():
                continue
            box = p.get_window_extent(rend)
            gid = p.get_gid() or ""
            filled = p.get_fill() and p.get_facecolor()[3] > 0
            if gid.startswith("container:") or isinstance(p, FancyBboxPatch):          # a box that holds text (schematic boxes): the text must lie wholly inside it
                arts.append(_Art(f"container:{gid}", ax, "container", box=box, gid=gid))
            elif filled:
                arts.append(_Art(f"patch:{gid or type(p).__name__}", ax, "patch_filled", box=box, gid=gid))
            else:
                arts.append(_Art(f"outline:{gid or type(p).__name__}", ax, "patch_edge", box=box, gid=gid))
    for t in fig.texts:
        if t.get_text() and t.get_visible():
            texts.append((t, None, "fig", "fig"))
    return texts, legends, arts, frames


def _frame_hit(box: Bbox, fb: Bbox, pad: float) -> bool:
    """The box crosses or touches the outline of the frame rectangle `fb` (neither wholly inside nor wholly outside it, or within pad of an edge)."""
    outer = _inflate(fb, pad)
    inner = Bbox.from_extents(fb.x0 + pad, fb.y0 + pad, fb.x1 - pad, fb.y1 - pad)
    if not _overlap(box, outer):
        return False
    return not (_contains(inner, box))


def check(fig, *, pad_pt: float = 0.5, allow=()) -> tuple[list[Hit], list[tuple[Hit, str]]]:
    """Run every test on `fig`. Returns (hits not allowed, [(hit, reason)] allowed)."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    pad = pad_pt * fig.dpi / 72.0
    texts, legends, arts, frames = _collect(fig, rend)
    tb = [(t, own, role, pan, _inflate(text_box(t, rend), pad / 2.0)) for t, own, role, pan in texts]
    hits: list[Hit] = []

    def name_t(t):
        return f"text '{_short(t.get_text())}'"

    # text against text
    for i in range(len(tb)):
        for j in range(i + 1, len(tb)):
            if _overlap(tb[i][4], tb[j][4]):
                hits.append(Hit("text-text", tb[i][3] if tb[i][3] != "fig" else tb[j][3], name_t(tb[i][0]), name_t(tb[j][0])))
    # text against artists
    for t, own, role, pan, box in tb:
        for a in arts:
            if role == "legend" and a.ax is own:
                continue                                             # a legend text is tested through its legend box below
            if a.kind == "line":
                if _overlap(box, a.ax.bbox) is False and a.clip is not None:
                    continue
                if segments_hit_box(a.pts, box, a.clip):
                    hits.append(Hit("text-line", pan, name_t(t), a.name))
            elif a.kind == "marks":
                inb = (a.pts[:, 0] >= box.x0 - a.hw) & (a.pts[:, 0] <= box.x1 + a.hw) & (a.pts[:, 1] >= box.y0 - a.hh) & (a.pts[:, 1] <= box.y1 + a.hh)
                if inb.any():
                    hits.append(Hit("text-marker", pan, name_t(t), a.name))
            elif a.kind == "image":
                if _overlap(box, a.box):
                    hits.append(Hit("text-image", pan, name_t(t), a.name))
            elif a.kind == "patch_filled":
                if _overlap(box, a.box):
                    hits.append(Hit("text-patch", pan, name_t(t), a.name))
            elif a.kind == "patch_edge":
                if _overlap(box, a.box) and not _contains(a.box, box) and not _contains(box, a.box):
                    hits.append(Hit("text-outline", pan, name_t(t), a.name))
            elif a.kind == "container":
                if _overlap(box, a.box) and not _contains(a.box, box):
                    hits.append(Hit("text-container-edge", pan, name_t(t), a.name))
    # text against frames and the figure edge, and clipped text
    fb = fig.bbox
    for t, own, role, pan, box in tb:
        for ax, fbox, fpan in frames:
            if ax is own and role in ("title", "xlabel", "ylabel", "tick"):
                continue
            if role == "legend" and ax is own:
                continue
            if _frame_hit(box, fbox, pad):
                if _overlap(box, fbox) or True:
                    hits.append(Hit("text-frame", pan, name_t(t), f"frame of panel {fpan}"))
        if box.x0 < fb.x0 + pad or box.x1 > fb.x1 - pad or box.y0 < fb.y0 + pad or box.y1 > fb.y1 - pad:
            hits.append(Hit("text-figure-edge", pan, name_t(t), "figure edge"))
        if role == "text" and own is not None and not isinstance(t, Annotation) and t.get_clip_on() and not _contains(own.bbox, box):        # an annotation is drawn unclipped (annotation_clip)
            hits.append(Hit("text-clipped", pan, name_t(t), f"axes of panel {pan}"))
    # legends
    for leg, ax, pan in legends:
        lb = _inflate(leg.get_window_extent(rend), pad / 2.0)
        lname = f"legend of panel {pan}"
        for a in arts:
            if a.kind == "line" and segments_hit_box(a.pts, lb, a.clip):
                hits.append(Hit("legend-line", pan, lname, a.name))
            elif a.kind == "marks":
                if ((a.pts[:, 0] >= lb.x0 - a.hw) & (a.pts[:, 0] <= lb.x1 + a.hw) & (a.pts[:, 1] >= lb.y0 - a.hh) & (a.pts[:, 1] <= lb.y1 + a.hh)).any():
                    hits.append(Hit("legend-marker", pan, lname, a.name))
            elif a.kind in ("image", "patch_filled") and _overlap(lb, a.box):
                hits.append(Hit("legend-" + a.kind.split("_")[0], pan, lname, a.name))
        own_texts = {id(x) for x in leg.get_texts()}
        for t, own, role, pan2, box in tb:
            if id(t) not in own_texts and _overlap(lb, box):
                hits.append(Hit("legend-text", pan, lname, name_t(t)))
        if lb.x0 < fb.x0 or lb.x1 > fb.x1 or lb.y0 < fb.y0 or lb.y1 > fb.y1:
            hits.append(Hit("legend-figure-edge", pan, lname, "figure edge"))
        for ax2, fbox, fpan in frames:
            if _frame_hit(lb, fbox, pad) and _overlap(lb, fbox) and (ax2 is ax or not _contains(fbox, lb) or True):
                if ax2 is ax and leg.get_frame_on() is False and _contains(Bbox.from_extents(fbox.x0 + pad, fbox.y0 + pad, fbox.x1 - pad, fbox.y1 - pad), lb):
                    continue
                if ax2 is not ax and not _overlap(lb, fbox):
                    continue
                hits.append(Hit("legend-frame", pan, lname, f"frame of panel {fpan}"))
    # marker against marker (different, non-rasterized artists of one axes)
    from scipy.spatial import cKDTree
    by_ax: dict = {}
    for a in arts:
        if a.kind == "marks" and not a.rasterized:
            by_ax.setdefault(id(a.ax), []).append(a)
    for group in by_ax.values():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                A, B = group[i], group[j]
                if A.name == B.name:
                    continue
                tree = cKDTree(B.pts)
                rx, ry = A.hw + B.hw, A.hh + B.hh
                near = tree.query_ball_point(A.pts, max(rx, ry), p=np.inf)
                hit_ = False
                for pa, idx in zip(A.pts, near):
                    if len(idx):
                        dd = np.abs(B.pts[idx] - pa)
                        if ((dd[:, 0] < rx) & (dd[:, 1] < ry)).any():
                            hit_ = True
                            break
                if hit_:
                    ax_ = A.ax
                    hits.append(Hit("marker-marker", panel_letter(ax_, list(fig.axes).index(ax_)), A.name, B.name))
    # one hit per distinct (kind, panel, a, b)
    seen, uniq = set(), []
    for h in hits:
        k = (h.kind, h.panel, h.a, h.b)
        if k not in seen:
            seen.add(k)
            uniq.append(h)
    bad, ok = [], []
    for h in uniq:
        e = next((x for x in allow if x.matches(h)), None)
        if e is None:
            bad.append(h)
        else:
            ok.append((h, e.reason))
    return bad, ok


def letters_in_order(fig, row_tol_in: float = 0.15) -> tuple[bool, list[str]]:
    """Panel letters (from the left titles) read top to bottom, left to right; True when they are a, b, c, ... without a gap or swap. Returns (ok, the letters in reading order)."""
    items = []
    for ax in fig.axes:
        m = LETTER.match(ax.get_title(loc="left") or "")
        if m:
            bb = ax.get_position()
            items.append((m.group(1), 1.0 - bb.y1, bb.x0))
    tol = row_tol_in / fig.get_figheight()
    items.sort(key=lambda r: (round(r[1] / tol), r[2]))
    seq = [i[0] for i in items]
    return seq == [chr(ord("a") + k) for k in range(len(seq))], seq


# ---- the allow-list of the journal builds (J8): an overlap that is intended, with the reason. Every entry is logged and goes to the reviewer for approval. ----
JOURNAL_ALLOW = {
    "F3": (
        AllowEntry("marker-marker", "c", r"slice Hopf points", r"a6_hopf_point",
                   "the A6 headline Hopf point is the Hopf point of the 5 ms slice of the Delta 0.3 panel (the same stored eta_bar); one stored point drawn twice, a tri-up inside a ring, not moved"),
        AllowEntry("marker-marker", "a", r"slice Hopf points", r"25 Hz crossings",
                   "stored positions: the Hopf point and the 25 Hz crossing of one slice are closer in eta_bar than the two marks are wide; positions are data and are not moved"),
        AllowEntry("marker-marker", "b", r"slice Hopf points", r"25 Hz crossings",
                   "stored positions: the Hopf point and the 25 Hz crossing of one slice are closer in eta_bar than the two marks are wide; positions are data and are not moved"),
    ),
    "F1": tuple(
        AllowEntry("marker-marker", pl, r"raw first crossing seed \d", r"raw first crossing seed \d",
                   "G7: the three stored raw first-crossing times lie within about 0.01 in of each other at the panel scale; they keep their stored positions and the key says the 3 seeds coincide")
        for pl in ("d", "f")),
    "F5": (),
}
