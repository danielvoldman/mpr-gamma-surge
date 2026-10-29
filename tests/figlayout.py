"""MS13 13i: layout checks shared by the figure tests (display-space geometry read from the drawn artists; nothing is simulated or read from results/).

A legend or a text box must not cover a plotted line or marker of its own axes: a line is covered if any of its points lies inside the box or any of its segments
crosses the box. Patches and images (shaded bands, maps) are background and are not tested. Tolerance: exact geometry in display pixels at the figure's dpi."""
import numpy as np
from matplotlib.transforms import Bbox


def _segments_cross(pts, vm, box: Bbox) -> bool:
    """True if a segment between two consecutive points that the axes shows crosses the box (Liang-Barsky clipping, exact geometry)."""
    for (x0, y0), (x1, y1), a, b in zip(pts[:-1], pts[1:], vm[:-1], vm[1:]):
        if not (a and b):
            continue
        dx, dy, t0, t1 = x1 - x0, y1 - y0, 0.0, 1.0
        for p, q in ((-dx, x0 - box.x0), (dx, box.x1 - x0), (-dy, y0 - box.y0), (dy, box.y1 - y0)):
            if p == 0.0:
                if q < 0.0:
                    t0, t1 = 1.0, 0.0
                    break
            else:
                r = q / p
                if p < 0.0:
                    t0 = max(t0, r)
                else:
                    t1 = min(t1, r)
        if t0 <= t1:
            return True
    return False


def _line_hits(ax, bbox: Bbox) -> list:
    hits = []
    for ln in ax.lines:
        if not ln.get_visible():
            continue
        xy = np.asarray(ln.get_xydata(), dtype=float)
        if xy.size == 0:
            continue
        pts = ln.get_transform().transform(xy)
        pts = pts[np.isfinite(pts).all(axis=1)]
        if len(pts) == 0:
            continue
        ab = ax.bbox
        m = 0.5 * float(ln.get_markersize()) * ax.figure.dpi / 72.0 if ln.get_marker() not in ("None", "none", "", None) else 0.0       # marker half size in pixels
        bbox = Bbox.from_extents(bbox.x0 - m, bbox.y0 - m, bbox.x1 + m, bbox.y1 + m)
        vm = (pts[:, 0] >= ab.x0) & (pts[:, 0] <= ab.x1) & (pts[:, 1] >= ab.y0) & (pts[:, 1] <= ab.y1)
        vis = pts[vm]                                                                                         # only what the axes shows
        inside = len(vis) > 0 and ((vis[:, 0] >= bbox.x0) & (vis[:, 0] <= bbox.x1) & (vis[:, 1] >= bbox.y0) & (vis[:, 1] <= bbox.y1)).any()
        crosses = len(pts) > 1 and ln.get_linestyle() not in ("None", "none", "") and _segments_cross(pts, vm, bbox)
        if inside or crosses:
            hits.append(ln)
    return hits


def legend_line_hits(fig) -> list:
    """[(axes title, line label)] for every line of an axes that lies under that axes' legend box."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    out = []
    for ax in fig.axes:
        leg = ax.get_legend()
        if leg is None:
            continue
        bb = leg.get_window_extent(rend)
        out += [(ax.get_title(), ln.get_label()) for ln in _line_hits(ax, bb)]
    return out


def text_line_hits(fig, ax, prefix: str) -> list:
    """Labels of the lines of `ax` that cross the box of any text of `ax` that starts with `prefix`."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    out = []
    for t in ax.texts:
        if t.get_text().startswith(prefix):
            out += [ln.get_label() for ln in _line_hits(ax, t.get_window_extent(rend))]
    return out


def clipped_texts(fig) -> list:
    """Texts (titles, axis labels, annotations, legend texts) whose box leaves the figure canvas, or a text drawn at or below the bottom edge of its axes without being a tick label."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    fb = fig.bbox
    out = []
    for ax in fig.axes:
        items = [ax.title, ax._left_title, ax._right_title, ax.xaxis.label, ax.yaxis.label] + list(ax.texts)
        if ax.get_legend() is not None:
            items += list(ax.get_legend().get_texts())
        for t in items:
            if not t.get_text():
                continue
            b = t.get_window_extent(rend)
            if b.x0 < fb.x0 - 0.5 or b.x1 > fb.x1 + 0.5 or b.y0 < fb.y0 - 0.5 or b.y1 > fb.y1 + 0.5:
                out.append(t.get_text()[:40])
    return out


def texts_below_axes(fig, ax, prefix: str) -> list:
    """Texts of `ax` starting with `prefix` whose box extends below the axes frame."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    return [t.get_text()[:30] for t in ax.texts if t.get_text().startswith(prefix) and t.get_window_extent(rend).y0 < ax.bbox.y0]
