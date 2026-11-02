"""MS13 13t (J8, J15 A): collision checker for the journal export. Works on the final matplotlib figure object at the export size; reads the rendered extents of the artists.

Objects tested (display space, pixels at the figure's dpi; the pad is the config's collision_pad_pt):
  texts      titles, axis labels, tick labels, in-axes texts and annotations (the text box only, not the arrow), legend texts, figure texts;
  legends    the legend box;
  artists    lines (segments, and markers with their size), scatter collections (marker extents), images and meshes (their data extent), patches (filled: the box;
             unfilled: the outline), annotation arrows (as lines), rasterized artists count as images;
  frames     the frame of every axes that has one, the figure edge.
Pair tests: text-text; text-artist; legend-artist; legend-text; text-frame (other axes, and own axes for in-axes texts); text and legend against the figure edge; clipped text
(clip_on and the box leaves its axes); marker-marker between different artists of one axes (also artists of the same name) and within one artist (a line of marks);
13t-1c (DL-563 S3, DL-564): marker-arrow (an annotation arrow patch, shaft and head, against a marker; the marker at the arrow's start vertex is the start circle and is not tested),
marker-line (a line against a marker of another artist, the width of the line counts), marker-tick (the segments of a LineCollection, the median and range ticks, against a marker),
marker-frame (a marker that crosses or comes within the pad of its axes frame) and marker-cell (a marker wider or taller than the cell of the mesh of its axes). A gap of at least the
pad is clear.
A hit is (kind, panel, a, b). An allow-list entry (AllowEntry) removes hits whose kind, panel and descriptors match; every entry carries a reason.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
from matplotlib.collections import LineCollection, PathCollection, QuadMesh
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
    ident: int = 0                 # id of the matplotlib artist (13t-1c: two artists of the same name are two artists)
    sub: str = ""                  # for kind "line": "line", "arrow" or "tick"
    lw_px: float = 0.0             # line width in pixels (a line, tick or arrow outline)
    start: np.ndarray | None = None   # the start vertex of an arrow (display)
    all_pts: np.ndarray | None = None  # marker centres before the clip to the axes (the frame test needs the partly visible ones)
    scatter: bool = False          # a PathCollection: its own points are not tested against each other (a dense scatter is the data)


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
        out.append(_Art(name, ax, "line", pts=pts, clip=clip, gid=ln.get_gid() or "", ident=id(ln), sub="line", lw_px=float(ln.get_linewidth()) * dpi / 72.0))
    if ln.get_marker() not in ("None", "none", "", " ", None):
        pm = pts[np.isfinite(pts).all(axis=1)]
        pall = pm
        if clip is not None:
            pm = pm[(pm[:, 0] >= clip.x0) & (pm[:, 0] <= clip.x1) & (pm[:, 1] >= clip.y0) & (pm[:, 1] <= clip.y1)]
        if len(pm):
            hw, hh = marker_half_extent(ln.get_marker(), float(ln.get_markersize()), float(ln.get_markeredgewidth()), dpi)
            out.append(_Art(name.replace("line:", "marks:"), ax, "marks", pts=pm, hw=hw, hh=hh, rasterized=bool(ln.get_rasterized()), gid=ln.get_gid() or "", ident=id(ln), all_pts=pall))
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
                polys = tr.transform_path(path).to_polygons(closed_only=False)
                lwp = float(t.arrow_patch.get_linewidth()) * dpi / 72.0
                tail = np.asarray(polys[0][0], float) if len(polys) and len(polys[0]) else None          # the first vertex of the arrow path is its tail (shrinkA is 0 in the figures)
                for poly in polys:
                    arts.append(_Art(f"arrow:{t.get_gid() or _short(t.get_text())}", ax, "line", pts=np.asarray(poly), clip=None, gid=t.get_gid() or "", ident=id(t), sub="arrow", lw_px=lwp, start=tail))
        for c in ax.collections:
            if not c.get_visible():
                continue
            if isinstance(c, LineCollection):                      # hlines, vlines: the median and range ticks are segments, not an image
                lwp = float(np.max(c.get_linewidth())) * dpi / 72.0 if len(c.get_linewidth()) else 0.0
                for seg in c.get_segments():
                    sp = c.get_transform().transform(np.asarray(seg, float))
                    arts.append(_Art(f"ticks:{c.get_gid() or c.get_label()}", ax, "line", pts=sp, clip=ax.bbox if c.get_clip_on() else None, gid=c.get_gid() or "", ident=id(c), sub="tick", lw_px=lwp))
                continue
            if isinstance(c, QuadMesh):                            # the cell size of a mesh, for the marker-cell test
                try:
                    co = np.asarray(c.get_coordinates(), float)
                    pxy = c.get_transform().transform(co.reshape(-1, 2)).reshape(co.shape)
                    cw = float(np.min(np.abs(np.diff(pxy[..., 0], axis=1))))
                    ch = float(np.min(np.abs(np.diff(pxy[..., 1], axis=0))))
                    arts.append(_Art(f"mesh:{c.get_gid() or 'QuadMesh'}", ax, "mesh", hw=cw, hh=ch, ident=id(c)))
                except Exception:
                    pass
            if isinstance(c, PathCollection) and not c.get_rasterized():
                off = c.get_offset_transform().transform(np.asarray(c.get_offsets(), float))
                sizes = np.asarray(c.get_sizes(), float)
                r = (np.sqrt(sizes.max() if sizes.size else 4.0) / 2.0) * dpi / 72.0
                pm = off[np.isfinite(off).all(axis=1)]
                pm = pm[(pm[:, 0] >= ax.bbox.x0) & (pm[:, 0] <= ax.bbox.x1) & (pm[:, 1] >= ax.bbox.y0) & (pm[:, 1] <= ax.bbox.y1)]
                if len(pm):
                    arts.append(_Art(f"marks:{c.get_gid() or c.get_label()}", ax, "marks", pts=pm, hw=r, hh=r, ident=id(c), all_pts=off[np.isfinite(off).all(axis=1)], scatter=True))
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
    # marker against marker: different artists of one axes (also artists of one name; rasterized marks too), with the pad; and within one artist (a line of marks)
    from scipy.spatial import cKDTree
    by_ax: dict = {}
    for a in arts:
        if a.kind == "marks":
            by_ax.setdefault(id(a.ax), []).append(a)

    def pan(ax_):
        return panel_letter(ax_, list(fig.axes).index(ax_))

    for group in by_ax.values():
        for i in range(len(group)):
            A = group[i]
            if not A.scatter and len(A.pts) > 1:                  # inside one line of marks: two centres closer than the two marks are wide plus the pad
                rx, ry = 2 * A.hw + pad, 2 * A.hh + pad
                tree = cKDTree(A.pts)
                for ia, ib in tree.query_pairs(max(rx, ry), p=np.inf):
                    dd = np.abs(A.pts[ia] - A.pts[ib])
                    if dd[0] < rx and dd[1] < ry:
                        hits.append(Hit("marker-marker", pan(A.ax), A.name, A.name + " (same artist)"))
                        break
            for j in range(i + 1, len(group)):
                B = group[j]
                if A.ident == B.ident:
                    continue
                tree = cKDTree(B.pts)
                rx, ry = A.hw + B.hw + pad, A.hh + B.hh + pad
                near = tree.query_ball_point(A.pts, max(rx, ry), p=np.inf)
                hit_ = False
                for pa, idx in zip(A.pts, near):
                    if len(idx):
                        dd = np.abs(B.pts[idx] - pa)
                        if ((dd[:, 0] < rx) & (dd[:, 1] < ry)).any():
                            hit_ = True
                            break
                if hit_:
                    hits.append(Hit("marker-marker", pan(A.ax), A.name, B.name))
    # marker against lines of other artists (separators, reference lines, curves), against annotation arrows and against the ticks of a LineCollection; the width of the line counts
    lines_by_ax: dict = {}
    for a in arts:
        if a.kind == "line":
            lines_by_ax.setdefault(id(a.ax), []).append(a)
    for gid_, group in by_ax.items():
        for M in group:
            for L in lines_by_ax.get(gid_, ()):
                if L.ident == M.ident:
                    continue
                kind = {"line": "marker-line", "arrow": "marker-arrow", "tick": "marker-tick"}[L.sub]
                lo = L.pts[np.isfinite(L.pts).all(axis=1)]
                if not len(lo):
                    continue
                reach_x, reach_y = M.hw + pad + L.lw_px / 2.0, M.hh + pad + L.lw_px / 2.0
                if len(lo) == 2 and (abs(lo[1, 1] - lo[0, 1]) < 1e-6 or abs(lo[1, 0] - lo[0, 0]) < 1e-6):          # an axis-parallel segment: its width counts across it, not along it (butt ends)
                    if abs(lo[1, 1] - lo[0, 1]) < 1e-6:
                        reach_x = M.hw + pad
                    else:
                        reach_y = M.hh + pad
                cand = M.pts[(M.pts[:, 0] >= lo[:, 0].min() - reach_x) & (M.pts[:, 0] <= lo[:, 0].max() + reach_x) & (M.pts[:, 1] >= lo[:, 1].min() - reach_y) & (M.pts[:, 1] <= lo[:, 1].max() + reach_y)]
                for c_ in cand[:4000]:
                    if L.sub == "arrow" and L.start is not None and abs(c_[0] - L.start[0]) <= M.hw + pad and abs(c_[1] - L.start[1]) <= M.hh + pad:
                        continue                                  # the start circle of an arrow sits on its tail
                    if segments_hit_box(L.pts, Bbox.from_extents(c_[0] - reach_x, c_[1] - reach_y, c_[0] + reach_x, c_[1] + reach_y), L.clip):
                        hits.append(Hit(kind, pan(M.ax), M.name, L.name))
                        break
    # marker against the frame of its own axes (a marker that crosses the frame, or comes within the pad of it)
    for gid_, group in by_ax.items():
        for M in group:
            fbox = M.ax.bbox
            pts = M.all_pts if M.all_pts is not None else M.pts
            for c_ in pts:
                if _frame_hit(Bbox.from_extents(c_[0] - M.hw, c_[1] - M.hh, c_[0] + M.hw, c_[1] + M.hh), fbox, pad):
                    hits.append(Hit("marker-frame", pan(M.ax), M.name, f"frame of panel {pan(M.ax)}"))
                    break
    # marker against its cell: a mark wider or taller than the cell of the mesh of its axes (less the pad)
    meshes: dict = {}
    for a in arts:
        if a.kind == "mesh":
            meshes[id(a.ax)] = a
    for gid_, group in by_ax.items():
        mesh = meshes.get(gid_)
        if mesh is None:
            continue
        for M in group:
            if 2 * M.hw + pad > mesh.hw + 1e-9 or 2 * M.hh + pad > mesh.hh + 1e-9:
                hits.append(Hit("marker-cell", pan(M.ax), M.name, f"cell of the mesh of panel {pan(M.ax)} ({mesh.hw:.1f} x {mesh.hh:.1f} px)"))
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
        AllowEntry("marker-arrow", "*", r"a6_hopf_point|slice Hopf points", r"arrow:",
                   "stored positions: the stored A6 Hopf point (eta_bar 2.896, Delta 0.3, tau_d 5 ms) lies on the path of P1, P2, P3 and P5 (eta_bar 1.396 to 4.896 at the same Delta and tau_d), and the arrows of P4a, P4b "
                   "and of the return of P5 pass within the width of its mark; the point and the arrows keep their stored positions"),
        AllowEntry("marker-line", "*", r"a6_hopf_point|slice Hopf points", r"A4 Hopf curve",
                   "stored position: the Hopf point of the 5 ms slice (the A6 headline Hopf point) lies on, or within the width of its mark of, the A4 Hopf curve, which is the curve of Hopf points; "
                   "A4 and A6 are separate stored records and no claim is made that they agree (caption); the mark keeps its stored position"),
    ),
    "F1": tuple(
        AllowEntry("marker-marker", pl, r"raw first crossing seed \d", r"raw first crossing seed \d",
                   "R3, R6: the three stored raw first-crossing times (50.170 to 50.924 s, not equal) overlap at the figure scale; they keep their stored positions and the key says that they overlap at this scale")
        for pl in ("d", "f")) + tuple(
        AllowEntry("marker-marker", pl, r"marks:", r"\(same artist\)",
                   "the spike raster of the stored spikes of the window: ticks overlap by design, the density of the ticks is the data (every stored spike of the window is drawn at its stored time and row)")
        for pl in ("j", "k")) + tuple(
        AllowEntry("marker-frame", pl, r"marks:", r"frame of panel",
                   "the spike raster: the stored spikes of the window lie on the first and last rows and times of the window, so ticks touch the frame; the window is the stored window, not shifted")
        for pl in ("j", "k")),
    "F5": (
        AllowEntry("marker-cell", "a", r"network symbols", r"cell of the mesh",
                   "the four network symbols are drawn larger than a 4 pt map cell by design (they mark a stored cell: matched to 1e-9 in (Delta, tau_d), numbered 1 to 4 as in (b)); they are outlined and carry the number of the cell"),
        AllowEntry("text-marker", "a", r"text '[1-4]'", r"network symbols",
                   "the number of a network cell is written inside its own network symbol (white halo, 8 pt bold); the text and the symbol are one label"),
        AllowEntry("text-image", "a", r"text '[1-4]'", r"image:",
                   "the number of a network cell lies inside its network symbol, which lies on the map cell it marks; the symbol covers the cell under the number")
    ) + tuple(
        AllowEntry("marker-cell", pl, r"marks:(d24|p1) ", r"cell of the mesh",
                   "DL-571 T10 (approved): the dark state mark of a subgrid cell (4.2 pt, 0.8 pt edge) is wider than its map-1 cell (3.0 pt) but inside the pitch of at least 6.0 pt "
                   "to the next subgrid cell, so no two marks touch; a mark of the cell size would be below 3 pt and unreadable")
        for pl in ("c", "d")),
    "F5c": tuple(
        AllowEntry("marker-line", pl, r"marks:(seed|control) N\d s\d", r"mean-field companion reference|stored minimum duration",
                   "stored value on the line (DL-571 T10): the line is the stored mean-field companion value (f_pk 49 Hz, onset 33.698 s) or the stored minimum duration (1000 ms, the classifier floor), "
                   "and a seed whose stored value is that value lies on it")
        for pl in ("b", "c", "d")),
}
