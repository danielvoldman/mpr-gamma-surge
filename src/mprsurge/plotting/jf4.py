"""MS13 13t-8 (DL-667 K1, K2): the journal export of F4 as two files, F4a and F4b, from the one drawing and data step of the draft (make_F4).

The draft F4 is 7.4 x 16.2 in with 12 panels and a key of 13 lines; it does not fit 6.3 x 8.0 in at 8 pt without touching, so the JOURNAL export splits it (pre-approved, K2; a departure from the plan's
single F4): F4a = the delay panels (draft (a) onset delay against ramp rate, (f) up and down ramp, (g) start state, (i) and (j) the D43 floor); F4b = the episode metrics and the noise band
(draft (b) to (e) peak power, peak frequency and duration, (h) the noise band on the delay, (k) and (l) the M2 ramp through the saddle-node). Layout only: every drawn value is the draft's; the
union of the arrays of the two files is the draft's data and each array has the draft's digest. Axes are placed in inches. The helpers of the draft drawing (series, rings, hold marks, foot bands,
noise bars) are the draft's own functions (figures._f4_*).
"""
from __future__ import annotations

import re

import numpy as np

from . import captions as CAP
from . import jcaption as JC
from . import journal as J
from . import plain as PL
from . import style as S
from .jf4cap import _NW, _fmt, _levels, a11_counts, classifier_facts, duration_facts, duration_floor_sentence, f4_consts, f4a_caption, f4a_short, f4b_caption, f4b_short

F4_PARTS = ("F4a", "F4b")
# journal panel -> draft panel (the mapping table of the supplements)
F4A_PANELS = {"a": "a", "b": "f", "c": "g", "d": "i", "e": "j"}
F4B_PANELS = {"a": "b", "b": "c", "c": "d", "d": "e", "e": "h", "f": "k", "g": "l"}
PANELS = {"F4a": F4A_PANELS, "F4b": F4B_PANELS}
HEIGHT = {"F4a": 8.0, "F4b": 8.0}
FAMS = (("p1_linear", "P1", "linear"), ("p1_sigmoid", "P1", "sigmoid"), ("p2_linear", "P2", "linear"), ("p2_sigmoid", "P2", "sigmoid"), ("p5_linear", "P5", "linear"), ("p5_sigmoid", "P5", "sigmoid"))
MINUS = "−"
XLAB = "Ramp rate (1/tau), log axis"
DELAY_LAB = "Delay: " + r"$\bar{\eta}$" + " at onset\n" + MINUS + " " + r"$\bar{\eta}$" + " at the Hopf point"
DELAY_SHORT = "Delay (" + r"$\bar{\eta}$" + " units)"
# columns of the two-column rows, in inches from the left edge: (left, width)
COL_L, COL_R = (0.80, 2.30), (3.62, 2.50)
WIDE = (0.80, 5.32)
# (top of the axes from the top edge, height) per journal panel, in inches; layout only
ROWS = {"F4a": {"a": (1.78, 1.45), "b": (3.88, 1.25), "c": (3.88, 1.25), "d": (5.78, 1.25), "e": (5.78, 1.25)},
        "F4b": {"a": (1.72, 1.0), "b": (1.72, 1.0), "c": (3.45, 1.0), "d": (3.45, 1.0), "e": (5.35, 0.8), "f": (6.82, 0.7), "g": (6.82, 0.7)}}
# 13t-8b: the three prediction lines differ in colour only in the draft; each path gets its own line style (P1 keeps the draft dash-dot, P2 dashed, P5 solid; matplotlib treats custom dash patterns as dashed), so that the colour is not the only difference
PRED_DASH = {"P2": "--", "P5": "-"}
KEY_BOX = {"F4a": (0.13, 0.12, 6.04, 1.40), "F4b": (0.13, 0.06, 6.04, 1.20)}

# ---- the array split (T1 style: the union of the two key lists is the draft's data; every entry has the draft's digest) -------------------------------------------------------------
_FAM_RE = re.compile(r"^(p1_linear|p1_sigmoid|p2_linear|p2_sigmoid|p5_linear|p5_sigmoid)_(.+)$")
_SD_RE = re.compile(r"^(sd05|sd30)_(.+)$")
SHARED_FAM = ("eps", "in_range", "eta_const", "cls")                                  # the ramp rate, the RB3(a) range flags and the class are used by the panels of both files
SHARED_OTHER = ("strip", "rb_status", "rb5_fail_rows", "n_in_range", "n_testable", "n_testable_within_one_step")
F4B_FAM = ("peak_power_abs", "peak_power_rel", "f_pk_hz", "duration_s", "T_ramp_s")           # (b) to (e) of the draft
F4B_SD = ("peak_power_abs", "f_pk_hz", "duration_s")                                  # held in the data of the start-state runs, drawn in no panel; kept with the metrics they belong to
F4B_OTHER = ("n_none_class",)


def part_of(key: str) -> tuple:
    """The journal files that draw or state the data entry `key`: ('F4a',), ('F4b',) or both."""
    if key in SHARED_OTHER:
        return F4_PARTS
    m = _FAM_RE.match(key)
    if m:
        name = m.group(2)
        if name in SHARED_FAM:
            return F4_PARTS
        return ("F4b",) if name in F4B_FAM else ("F4a",)
    m = _SD_RE.match(key)
    if m:
        name = m.group(2)
        if name in ("eps", "in_range", "eta_const", "cls"):
            return ("F4a",)
        return ("F4b",) if name in F4B_SD else ("F4a",)
    if key.startswith(("noise_", "a3_")) or key in F4B_OTHER:
        return ("F4b",)
    return ("F4a",)                                                                    # head_*, floor_*, hold_delay_max, n_hold, n_nocross, testable_match_steps


def journal_keys(fid: str, d: dict) -> list:
    return sorted(k for k in d if fid in part_of(k))


# ---- drawing --------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def _new(ax, n0: int, gid: str):
    """Give every line added to `ax` since the line count n0 the name `gid` (the collision checker names marks and lines from it)."""
    for ln in ax.lines[n0:]:
        if not ln.get_gid():
            ln.set_gid(gid)


def _axes(fig, part: str, letter: str, col, **kw):
    from .figures import _ax_in
    top, h = ROWS[part][letter]
    left, w = col
    ax = _ax_in(fig, left, top, w, h, **kw)
    return ax


def _title(ax, letter: str, text: str, fail: bool = False, pad: float | None = None):
    from .figures import _journal_title
    _journal_title(ax, letter, text, fail=fail)
    if pad is not None:
        ax.title.set_position((0.0, 1.0))
        ax.set_title(ax.get_title(loc="left"), loc="left", pad=pad, color=ax._left_title.get_color())      # the colour of the left title (red for a FAIL)


def _decimal_log(ax, axis: str = "x"):
    """Plain decimal tick labels on a log axis (0.0001, 0.001, 0.01 ...; W3: no superscript on an image) and no minor labels."""
    from matplotlib.ticker import FuncFormatter, NullFormatter

    def fmt(v, _pos):
        return f"{v:.10g}" if v >= 1 else f"{v:.6f}".rstrip("0")
    a = ax.xaxis if axis == "x" else ax.yaxis
    a.set_major_formatter(FuncFormatter(fmt))
    a.set_minor_formatter(NullFormatter())


def _band(ax, logy: bool = False):
    """The foot band of the draft (_f4_band) without its name on the panel: the name is in the key (a text on the shaded band would touch the band and the frame)."""
    from . import figures as FG
    lo, hi = ax.get_ylim()
    f = FG.F4_BAND_FRAC
    new_lo = lo / (hi / lo) ** (f / (1.0 - f)) if logy else lo - (hi - lo) * f / (1.0 - f)
    ax.set_ylim(new_lo, hi)
    ax.axhspan(new_lo, lo, color=S.FS_COLOURS["patch_edge"], alpha=0.14, lw=0, zorder=0)


def _tidy_x(ax, label: str | None = XLAB):
    ax.set_xscale("log")
    _decimal_log(ax)
    if label:
        ax.set_xlabel(label)


def _series(ax, FG, x, y, path, prof, ms, name):
    n0 = len(ax.lines)
    FG._f4_series(ax, x, y, path, prof, ms=ms)
    _new(ax, n0, f"series {path} {prof}{name}")


def _key_series_handles(FG, ms):
    from matplotlib.lines import Line2D
    out = []
    for fam, path, prof in FAMS:
        st = S.get(path)
        lin = prof == "linear"
        out.append(Line2D([], [], color=st.colour, ls=st.linestyle if lin else "--", lw=0.8, marker=st.marker, ms=ms, mfc=st.colour if lin else "none", mec=st.colour,
                          label=f"{path} {prof}" + ("" if lin else " (dashed, open marks)")))
    return out


def _key(fig, part: str, handles: list, labels: list, ncol: int = 2):
    from .figures import _ax_in
    kx = _ax_in(fig, *KEY_BOX[part])
    kx.axis("off")
    kx.set_gid("legend axes")
    lg = kx.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.0, 1.0), ncol=ncol, frameon=False, borderaxespad=0, labelspacing=0.25, handlelength=2.6, columnspacing=1.0)
    lg.set_in_layout(False)
    return kx


def draw_F4a(d: dict):
    """F4a: the delay panels (journal (a) to (e) = draft (a), (f), (g), (i), (j)); returns the figure."""
    from matplotlib.lines import Line2D
    from . import figures as FG
    fig, cfg = FG._journal_fig(HEIGHT["F4a"], constrained=False)
    pred, ref, cls_m = S.diagram_mark("f4_pred"), S.diagram_mark("f4_ref"), S.diagram_mark("f4_cls")
    dag = _dagger_outline()
    down, hyst, rg, md = S.diagram_mark("f4_down"), S.diagram_mark("f4_hyst"), S.diagram_mark("f4_inrange"), S.diagram_mark("fs3_median")
    red = S.figure_colour("fail_text")
    # key
    hs = _key_series_handles(FG, S.POINT_SIZES["f4_series"])
    hs += [Line2D([], [], color=pred.colour, ls=pred.linestyle, lw=pred.width), Line2D([], [], ls="none", marker=dag, ms=cls_m.size, mfc="none", mec=cls_m.colour, mew=DAGGER_EDGE),
           Line2D([], [], color=ref.colour, ls=ref.linestyle, lw=ref.width),
           Line2D([], [], ls="none", marker=rg.marker, ms=S.POINT_SIZES["f4_key"], mfc="none", mec=rg.colour, mew=rg.width),
           Line2D([], [], ls="none", marker=S.F4_MARKS["untestable"], ms=S.POINT_SIZES["f4_key"] * 0.8, mfc="none", mec=rg.colour, mew=rg.width),
           Line2D([], [], ls="none", marker=S.F4_MARKS["hold_marker"], ms=S.POINT_SIZES["f4_key"], mfc="none", mec=S.F4_MARKS["hold_colour"], mew=S.F4_MARKS["hold_width"]),
           Line2D([], [], ls="none", marker=S.F4_MARKS["nocross"], ms=S.POINT_SIZES["f4_none"] + 2.0, color=S.F4_MARKS["nocross_colour"]),
           Line2D([], [], ls="none", marker=S.F4_MARKS["fail_ring"], ms=S.POINT_SIZES["f4_key"], mfc="none", mec=red, mew=S.F4_MARKS["fail_ring_width"]),
           Line2D([], [], color=down.colour, ls="-", marker=down.marker, ms=down.size - 2.5, lw=0.8), Line2D([], [], color=hyst.colour, ls=hyst.linestyle, lw=hyst.width),
           Line2D([], [], ls="none", marker=S.diagram_mark("fs4_l0").marker, ms=S.POINT_SIZES["f4_key"], mfc="none", mec=S.diagram_mark("fs4_l0").colour, mew=0.6)]
    labs = [h.get_label() for h in hs[:6]] + [
        "Predicted onset, linear (line style by path)", "Classifier onset, second reading", "No delay: onset at the Hopf point (dotted)",
        "Octagon: in range, testable", "Diamond: in range, not testable", "Open square: onset during the hold",
        "Dash in the shaded foot band: no raw crossing", "Red ring: main example, solvers differ", "P5 down-ramp offset (triangles)", "P5 hysteresis width (dashed; dash-dot for sigmoid)",
        "Hollow marks in (d), (e): 10 seeds; dark: median"]
    _key(fig, "F4a", hs, labs)

    # (a) delay against ramp rate, raw crossing primary
    ax = _axes(fig, "F4a", "a", WIDE)
    for fam, path, prof in FAMS:
        x = d[f"{fam}_eps"]
        _series(ax, FG, x, d[f"{fam}_delay_eta_cross"], path, prof, S.POINT_SIZES["f4_series"], "")
        ok = ~np.isnan(d[f"{fam}_delay_eta"])
        n0 = len(ax.lines)
        ax.plot(x[ok], d[f"{fam}_delay_eta"][ok], ls="none", marker=dag, ms=cls_m.size, mfc="none", mec=cls_m.colour, mew=DAGGER_EDGE, zorder=4)      # 13t-10 (DL-691 O3): hollow, so the raw-crossing marks beneath stay visible; same size, same stored position
        _new(ax, n0, f"classifier onset {path} {prof}")
        n0 = len(ax.lines)
        FG._f4_ring(ax, x, d[f"{fam}_delay_eta_cross"], d[f"{fam}_in_range"], const=d[f"{fam}_eta_const"])
        _new(ax, n0, f"ring {path} {prof}")
        n0 = len(ax.lines)
        FG._f4_hold(ax, x, d[f"{fam}_delay_eta_cross"], d[f"{fam}_hold_cross"])
        FG._f4_hold(ax, x, d[f"{fam}_delay_eta"], d[f"{fam}_hold_cls"])
        _new(ax, n0, f"hold {path} {prof}")
        n0 = len(ax.lines)
        FG._f4_none_marks(ax, x, np.isnan(d[f"{fam}_delay_eta_cross"]), kind="crossing")
        _new(ax, n0, f"no crossing {path} {prof}")
        if prof == "linear":
            st = S.get(path)
            (ln,) = ax.plot(x, d[f"{fam}_delay_eta_pred"], color=st.colour, ls=PRED_DASH.get(path, pred.linestyle), lw=pred.width, zorder=2)
            ln.set_gid(f"prediction {path}")
    (ln,) = (ax.axhline(0.0, color=ref.colour, ls=ref.linestyle, lw=ref.width, zorder=1),)
    ln.set_gid("zero line")
    n0 = len(ax.lines)
    ax.plot([d["head_eps"]], [d["head_delay_eta_cross"]], ls="none", marker=S.F4_MARKS["fail_ring"], ms=S.F4_MARKS["fail_ring_size"], mfc="none", mec=red, mew=S.F4_MARKS["fail_ring_width"], zorder=6)
    _new(ax, n0, "red ring main example")
    ax.set_ylim(-0.25, 3.6)
    _band(ax)
    ax.text(0.01, 0.97, f"Prediction: {d['n_testable_within_one_step']} of {d['n_testable']} testable runs within one step\nSolvers: main example onset differs by {d['head_radau_minus_default_ms']:.0f} ms ({a11_counts(d['strip'])['bound_ms']:g} ms allowed)",
            transform=ax.transAxes, ha="left", va="top", color=red, weight="bold", zorder=8).set_gid("panel note")
    _tidy_x(ax)
    ax.set_ylabel(DELAY_LAB)
    _title(ax, "a", "Onset delay against ramp rate, no noise: prediction FAIL, solver FAIL", fail=True)

    # (b) up against down ramp: P5
    ax = _axes(fig, "F4a", "b", COL_L)
    for fam, path, prof in (("p5_linear", "P5", "linear"), ("p5_sigmoid", "P5", "sigmoid")):
        x = d[f"{fam}_eps"]
        _series(ax, FG, x, d[f"{fam}_delay_eta_cross"], path, prof, S.POINT_SIZES["f4_series_p5"], " up")
        n0 = len(ax.lines)
        ax.plot(x, d[f"{fam}_offset_minus_eta_H"], color=down.colour, ls="-" if prof == "linear" else ":", lw=0.8, marker=down.marker, ms=down.size - 1.5, zorder=3)
        _new(ax, n0, f"P5 down offset {prof}")
        n0 = len(ax.lines)
        ax.plot(x, d[f"{fam}_hysteresis_width"], color=hyst.colour, ls=hyst.linestyle if prof == "linear" else "-.", lw=hyst.width, zorder=2)
        _new(ax, n0, f"P5 hysteresis width {prof}")
        n0 = len(ax.lines)
        FG._f4_none_marks(ax, x, np.isnan(d[f"{fam}_delay_eta_cross"]), kind="crossing")
        _new(ax, n0, f"no crossing P5 {prof}")
    (ln,) = (ax.axhline(0.0, color=ref.colour, ls=ref.linestyle, lw=ref.width, zorder=1),)
    ln.set_gid("zero line")
    _band(ax)
    _tidy_x(ax)
    ax.set_ylabel(DELAY_SHORT)
    _title(ax, "b", "Up and down ramp (P5)")

    # (c) start state: P1 linear at three start distances
    ax = _axes(fig, "F4a", "c", COL_R)
    p1 = S.get("P1")
    for tag, ls_, fill in (("sd05", ":", "left"), ("p1_linear", "-", "full"), ("sd30", "--", "none")):
        x = d[f"{tag}_eps"]
        y = d[f"{tag}_delay_eta_cross"]
        n0 = len(ax.lines)
        ax.plot(x, y, color=p1.colour, ls=ls_, lw=0.8, marker=p1.marker, ms=S.POINT_SIZES["f4_series_p5"], fillstyle=fill, mec=p1.colour, mew=0.7, zorder=3)
        _new(ax, n0, f"series P1 start {tag}")
        n0 = len(ax.lines)
        FG._f4_ring(ax, x, y, d[f"{tag}_in_range"], const=d[f"{tag}_eta_const"])
        _new(ax, n0, f"ring start {tag}")
        n0 = len(ax.lines)
        FG._f4_hold(ax, x, y, d[f"{tag}_hold_cross"])
        _new(ax, n0, f"hold start {tag}")
        n0 = len(ax.lines)
        FG._f4_none_marks(ax, x, np.isnan(y), kind="crossing")
        _new(ax, n0, f"no crossing start {tag}")
    (ln,) = (ax.axhline(0.0, color=ref.colour, ls=ref.linestyle, lw=ref.width, zorder=1),)
    ln.set_gid("zero line")
    ax.text(0.02, 0.97, "Start distance:\n0.5 dotted, 1.5 solid, 3.0 dashed", transform=ax.transAxes, va="top", ha="left").set_gid("panel note")
    ax.set_ylim(-0.1, 2.45)
    _band(ax)
    _tidy_x(ax)
    ax.set_ylabel(DELAY_SHORT)
    _title(ax, "c", "Start state (P1 linear)")

    # (d), (e): the D43 floor at the main example, per level, 4 Heun steps x 10 seeds, both onset readings
    for letter, col, key, med, title, fail in (("d", COL_L, "floor_delay_cross", "floor_median_cross", "Floor, raw crossing", False),
                                               ("e", COL_R, "floor_delay_cls", "floor_median_cls", "Floor, classifier onset: FAIL", True)):
        ax = _axes(fig, "F4a", letter, col)
        for lvl in range(3):
            mk = S.diagram_mark(f"fs4_l{lvl}")
            for k, size in enumerate(S.POINT_SIZES["f4_floor_rungs"]):
                n0 = len(ax.lines)
                ax.plot([lvl] * 10, d[key][lvl][k], ls="none", marker=mk.marker, ms=size, mfc="none", mec=mk.colour, mew=0.6, zorder=3)
                _new(ax, n0, f"floor level {lvl} step {k}")
            n0 = len(ax.lines)
            ax.plot([lvl], [d[med][lvl]], ls="none", marker=md.marker, ms=md.size, color=S.F4_MARKS["median_colour"], mew=md.width, zorder=4)
            _new(ax, n0, f"median level {lvl}")
        ax.set_xticks(range(3), [CAP.number_text(float(f"{s_:.3g}")) + ("\n(main example)" if (lvl == 0 and not fail) else "") for lvl, s_ in enumerate(d["floor_sigma"])])
        ax.margins(y=0.15)
        ax.set_xlim(-0.5, 2.5)
        lo_, hi_ = ax.get_ylim()
        ax.set_xlabel(f"Floor level (noise floor sigma)\ny range {CAP.number_text(float(f'{lo_:.3g}'))} to {CAP.number_text(float(f'{hi_:.3g}'))}, own axis")
        ax.set_ylabel(DELAY_SHORT)
        if fail:
            ax.text(0.04, 0.6, "Delays tie at " + MINUS + "1.5 at the two\nlower levels: onset at the\nramp start (saturated)", transform=ax.transAxes, ha="left", va="center", color=red, weight="bold",
                    bbox=dict(boxstyle="square,pad=0.15", fc=S.HALO_COLOUR, ec="none", alpha=0.85)).set_gid("panel note")
        _title(ax, letter, title, fail=fail)
    J.finish(fig, cfg)
    return fig


def _neg(x: float) -> str:
    """One decimal with a true minus sign (13t-11 R3)."""
    return f"{x:.1f}".replace("-", MINUS)


_F4B_DURATION_LABEL = "Dotted line in (d): {dur_floor:g} s"        # 13t-11 (DL-699 R2): attempt 1 ('..., smallest duration for ramps of 60 s or more') ran past the right edge of the key; attempt 2 is the ruled fallback; the value is read, not typed


def _floor_facts(FG, d: dict) -> dict:
    """13t-11 (DL-699 R1, R2): the duration floor of (d) read from the recorded durations (and the window rule of the frozen criteria); the same facts as the caption."""
    from .. import config as _C
    crit, _ = FG.F.K.load_frozen_criteria(_C.repo_root())
    return duration_facts(d, classifier_facts(crit)["T_win"])


def draw_F4b(d: dict):
    """F4b: the episode metrics and the noise band (journal (a) to (g) = draft (b), (c), (d), (e), (h), (k), (l)); returns the figure."""
    from matplotlib.lines import Line2D
    from . import figures as FG
    from .figures import _ax_in
    fig, cfg = FG._journal_fig(HEIGHT["F4b"], constrained=False)
    ref, rg, md = S.diagram_mark("f4_ref"), S.diagram_mark("f4_inrange"), S.diagram_mark("fs3_median")
    nz = S.get("noise")
    red = S.figure_colour("fail_text")
    hs = _key_series_handles(FG, S.POINT_SIZES["f4_series_small"])
    hs += [Line2D([], [], color=nz.colour, lw=3.0), Line2D([], [], ls="none", marker=md.marker, ms=md.size, color=S.F4_MARKS["median_colour"], mew=md.width),
           Line2D([], [], ls="none", marker=rg.marker, ms=S.POINT_SIZES["f4_key"], mfc="none", mec=rg.colour, mew=rg.width),
           Line2D([], [], ls="none", marker=S.F4_MARKS["untestable"], ms=S.POINT_SIZES["f4_key"] * 0.8, mfc="none", mec=rg.colour, mew=rg.width),
           Line2D([], [], ls="none", marker=S.get("D-none").marker, ms=S.POINT_SIZES["f4_none"], color=S.get("D-none").colour, mec=S.figure_colour("bar_edge"), mew=0.3),
           Line2D([], [], color=S.figure_colour("range_line"), ls=":", lw=0.8), Line2D([], [], color=ref.colour, ls=ref.linestyle, lw=ref.width), Line2D([], [], color=S.FS_COLOURS["patch_edge"], lw=6, alpha=0.3)]
    labs = [h.get_label() for h in hs[:6]] + [
        "Grey bar: minimum to maximum of the 10 noisy seeds (P2)", "Dark mark: median of the seeds with a value",
        "Octagon: in range, testable", "Diamond: in range, not testable", "Foot mark: no episode (class D-none)",
        _F4B_DURATION_LABEL.format(**_floor_facts(FG, d)), "Dotted line in (e), (g): zero delay, zero rate", "Shaded foot band: no episode (a to d)"]
    _key(fig, "F4b", hs, labs)

    # (a) to (d): peak power (absolute, relative), peak frequency, duration; the noise bars are P2, mode N
    for letter, col, key, noisekey, title, yl, logy in (("a", COL_L, "peak_power_abs", "noise_peak_power_abs", "Peak power, absolute", "Peak power (absolute)", False),
                                                          ("b", COL_R, "peak_power_rel", "noise_peak_power_rel", "Peak power, relative", "Peak power (relative)", False),
                                                          ("c", COL_L, "f_pk_hz", "noise_f_pk_hz", "Peak frequency", "Peak frequency (Hz)", False),
                                                          ("d", COL_R, "duration_s", "noise_duration_s", "Duration", "Duration (s), log axis", True)):
        ax = _axes(fig, "F4b", letter, col)
        n0 = len(ax.lines)
        FG._f4_noise(ax, d, noisekey)
        _new(ax, n0, "noise seeds")
        for fam, path, prof in FAMS:
            _series(ax, FG, d[f"{fam}_eps"], d[f"{fam}_{key}"], path, prof, S.POINT_SIZES["f4_series_small"], "")
            n0 = len(ax.lines)
            FG._f4_ring(ax, d[f"{fam}_eps"], d[f"{fam}_{key}"], d[f"{fam}_in_range"], const=d[f"{fam}_eta_const"])
            _new(ax, n0, f"ring {path} {prof}")
            n0 = len(ax.lines)
            FG._f4_none_marks(ax, d[f"{fam}_eps"], np.isnan(d[f"{fam}_{key}"]), kind="episode")
            _new(ax, n0, f"no episode {path} {prof}")
        if logy:
            ax.set_yscale("log")
            (ln,) = (ax.axhline(1.0, color=S.figure_colour("range_line"), ls=":", lw=0.6, zorder=1),)
            ln.set_gid("one second line")
        if not logy:                                        # 13t-8b (DL-671 L2): display padding of the axis limit, so that the ring at the top value does not touch the frame (no value moved)
            lo_, hi_ = ax.get_ylim()
            ax.set_ylim(lo_, hi_ + (hi_ - lo_) * 0.07)
        _band(ax, logy)
        _tidy_x(ax, None if letter in ("a", "b") else XLAB)
        if logy:
            _decimal_log(ax, "y")
        ax.set_ylabel(yl)
        _title(ax, letter, title, pad=13.0)
    # (e) noise band on the delay
    ax = _axes(fig, "F4b", "e", WIDE)
    n0 = len(ax.lines)
    FG._f4_noise(ax, d, "noise_delay_eta_cross")
    _new(ax, n0, "noise seeds")
    _series(ax, FG, d["p2_linear_eps"], d["p2_linear_delay_eta_cross"], "P2", "linear", S.POINT_SIZES["f4_series_p5"], " no noise")
    (ln,) = (ax.axhline(0.0, color=ref.colour, ls=ref.linestyle, lw=ref.width, zorder=1),)
    ln.set_gid("zero line")
    k = a11_counts(d["strip"])
    ax.text(0.01, 0.97, f"Main-example class kept in {k['kept']} of {k['kept_n']} noisy seeds ({k['kept_need']} needed)\nNoisy subgrid: {k['sub_agree']} of {k['sub_cells']} cells agree ({k['sub_needed']} needed)", transform=ax.transAxes, ha="left", va="top", color=red, weight="bold").set_gid("panel note")
    _tidy_x(ax)
    ax.set_ylabel(DELAY_SHORT)
    ax.set_ylim(-1.15, 1.75)                                  # 13t-8b: display padding below, the lowest noise bar touched the frame
    _title(ax, "e", "Noise band on the delay, P2: noise robustness FAIL", fail=True, pad=13.0)
    # (f) and (g): M2 through the saddle-node (A3)
    mf = S.get("mean_field")
    ax = _axes(fig, "F4b", "f", COL_L)
    n0 = len(ax.lines)
    ax.plot(d["a3_eps"], d["a3_offset"], color=mf.colour, ls="-", lw=0.8, marker=mf.marker, ms=S.POINT_SIZES["f4_m2"], zorder=3)
    _new(ax, n0, "M2 jump offset")
    ax.set_yscale("log")
    _decimal_log(ax, "y")
    _tidy_x(ax)
    for setter, getter in ((ax.set_xlim, ax.get_xlim), (ax.set_ylim, ax.get_ylim)):      # 13t-8b: display padding of the limits (log axes: a factor), the last mark touched the frame; no value moved
        lo_, hi_ = getter()
        k_ = (hi_ / lo_) ** 0.06
        setter(lo_ / k_, hi_ * k_)
    ax.set_xticks([1e-4, 1e-3, 1e-2])                         # 13t-8b: the padded limit showed a tick label 0.1 that touched the y label of (g); the labelled ticks are the decades of the data
    ax.set_ylabel("Jump offset (" + r"$\bar{\eta}$" + "), log axis")
    _title(ax, "f", "M2 ramp: jump offset from the fold")
    ax = _axes(fig, "F4b", "g", COL_R)
    for x_, r_, s_ in zip(d["a3_eps"], d["a3_rate"], d["a3_se"]):
        (ln,) = ax.plot([x_, x_], [r_ - s_, r_ + s_], color=S.figure_colour("range_line"), lw=1.0, zorder=2)
        ln.set_gid("M2 rate error bar")
    n0 = len(ax.lines)
    ax.plot(d["a3_eps"], d["a3_rate"], color=mf.colour, ls="none", marker=mf.marker, ms=S.POINT_SIZES["f4_m2"], zorder=3)
    _new(ax, n0, "M2 ring rate")
    ax.set_ylim(-28.0, 1.5)
    (ln,) = (ax.axhline(0.0, color=ref.colour, ls=ref.linestyle, lw=ref.width, zorder=1),)
    ln.set_gid("zero line")
    _tidy_x(ax)
    ax.set_ylabel("Ring rate (1/s, " + "±" + "1 SE)")
    n_damped = sum(c == "damped" for c in d["a3_ring_class"])
    _title(ax, "g", f"M2 ring: damped at {n_damped} of 13")
    J.finish(fig, cfg)
    return fig


# ---- supplement data: source rows, alt text, the build (DL-667) ---------------------------------------------------------------------------------------------------------------------------

F4A_LIMITS = ("MS11-C7", "MS12-C1", "MS9(e)-5", "G6-D1", "G6-D2", "G6-D3", "DL-163-D1", "DL-163-D3", "DL-163-D4", "MS11-C6")
F4B_LIMITS = ("MS11-C7", "MS12-C1", "MS9(e)-2", "MS9(e)-5", "DL-163-D1", "DL-163-D2", "DL-163-D4", "G4-C4", "MS11-C1", "MS11-C3", "RB2 FAIL (plan label)", "D24 failed (plan label)")
LIMITS = {"F4a": F4A_LIMITS, "F4b": F4B_LIMITS}
# the stored FAIL rows each part draws or binds to a drawn quantity (the strip of the part)
F4A_STRIP = (("RB3", "a_inrange_runs"), ("RB3", "b_classifier_onset"), ("RB6", "solver_onset_headline"))
F4B_STRIP = (("RB2", "noisy_subgrid_agreement"), ("RB2", "headline_class_kept_1.0_sigma"))
STRIP_KEYS = {"F4a": F4A_STRIP, "F4b": F4B_STRIP}
MAIN_FAILURES = {"F4a": ("RB3(a)", "0 of 6", "RB6", "181 ms", "RB3(b)"), "F4b": ("RB2", "97 of 225", "7 of 10")}


def strip_rows_of(fid: str, d: dict) -> list:
    keys = STRIP_KEYS[fid]
    return [r for r in d["strip"] if (r["rb_id"], r["check_id"]) in keys]


def strip_lines_of(fid: str, d: dict) -> list:
    from .figures import strip_line
    return [strip_line(r) for r in strip_rows_of(fid, d)]


def FG_F4_DT():
    from .figures import F4_DT
    return F4_DT


def source_rows(fid: str, d: dict) -> list:
    from .figures import _src
    rows: list = []
    if fid == "F4a":
        for fam, path, prof in FAMS:
            nm = f"{path} {prof}"
            e = d[f"{fam}_eps"]
            _src(rows, "a", f"{nm}: delay, raw first crossing", e, d[f"{fam}_delay_eta_cross"])
            _src(rows, "a", f"{nm}: delay, classifier onset", e, d[f"{fam}_delay_eta"])
            if prof == "linear":
                _src(rows, "a", f"{nm}: predicted delay", e, d[f"{fam}_delay_eta_pred"])
            m = np.asarray(d[f"{fam}_in_range"], bool) & ~np.asarray(d[f"{fam}_eta_const"], bool)       # testable runs only: the error of an untestable run is not a result (13t-9 N3 item 3)
            _src(rows, "a", f"{nm}: error of the prediction in steps (testable runs in range)", np.asarray(e)[m], np.asarray(d[f"{fam}_match_err_steps"])[m])
            _src(rows, "a", f"{nm}: in range and constant eta at the predicted time (1 = untestable)", e, None, np.asarray(d[f"{fam}_eta_const"], float))
        _src(rows, "a", "main example: delay, raw first crossing", [d["head_eps"]], [d["head_delay_eta_cross"]])
        for fam, prof in (("p5_linear", "linear"), ("p5_sigmoid", "sigmoid")):
            e = d[f"{fam}_eps"]
            _src(rows, "b", f"P5 {prof}: up delay, raw first crossing", e, d[f"{fam}_delay_eta_cross"])
            _src(rows, "b", f"P5 {prof}: offset on the way down", e, d[f"{fam}_offset_minus_eta_H"])
            _src(rows, "b", f"P5 {prof}: hysteresis width", e, d[f"{fam}_hysteresis_width"])
        for tag, nm in (("sd05", "start distance 0.5"), ("p1_linear", "start distance 1.5"), ("sd30", "start distance 3.0")):
            _src(rows, "c", f"P1 linear, {nm}: delay, raw first crossing", d[f"{tag}_eps"], d[f"{tag}_delay_eta_cross"])
            if f"{tag}_match_err_steps" in d:
                m = np.asarray(d[f"{tag}_in_range"], bool) & ~np.asarray(d[f"{tag}_eta_const"], bool)
                if m.any():
                    _src(rows, "c", f"P1 linear, {nm}: error of the prediction in steps (testable runs in range)", np.asarray(d[f"{tag}_eps"])[m], np.asarray(d[f"{tag}_match_err_steps"])[m])
        for pn, key, med in (("d", "floor_delay_cross", "floor_median_cross"), ("e", "floor_delay_cls", "floor_median_cls")):
            for lvl in range(3):
                for k, dt in enumerate(FG_F4_DT()):
                    _src(rows, pn, f"floor level {lvl} (sigma {d['floor_sigma'][lvl]:.3g}), Heun step {dt:g} tau: delay of the 10 seeds", [lvl] * 10, d[key][lvl][k])
                _src(rows, pn, f"floor level {lvl}: median", [lvl], [d[med][lvl]])
        return rows
    for pn, key, nkey, nm in (("a", "peak_power_abs", "noise_peak_power_abs", "peak power, absolute"), ("b", "peak_power_rel", "noise_peak_power_rel", "peak power, relative"),
                              ("c", "f_pk_hz", "noise_f_pk_hz", "peak frequency (Hz)"), ("d", "duration_s", "noise_duration_s", "duration (s)")):
        for fam, path, prof in FAMS:
            _src(rows, pn, f"{path} {prof}: {nm}", d[f"{fam}_eps"], d[f"{fam}_{key}"])
        for j in range(10):
            _src(rows, pn, f"P2 noisy seed {j}: {nm}", d["noise_eps"], np.asarray(d[nkey])[:, j])
    for j in range(10):
        _src(rows, "e", f"P2 noisy seed {j}: delay, raw first crossing", d["noise_eps"], np.asarray(d["noise_delay_eta_cross"])[:, j])
    _src(rows, "e", "P2 linear, no noise: delay, raw first crossing", d["p2_linear_eps"], d["p2_linear_delay_eta_cross"])
    _src(rows, "f", "M2 ramp: jump offset from the fold", d["a3_eps"], d["a3_offset"])
    _src(rows, "g", "M2 ring: fitted rate (per s); value = standard error", d["a3_eps"], d["a3_rate"], d["a3_se"])
    return rows


def alt_text(fid: str, d: dict, c: dict) -> dict:
    n = JC.num
    if fid == "F4a":
        return {
            "a": (f"Delay of the onset against the ramp rate (logarithmic axis, {n(c['eps_lo'])} to {n(c['eps_hi'])}) for six series (P1, P2, P5, linear and sigmoid): delays from about {_neg(c['delay_lo'])} to {c['delay_hi']:.1f} (positive: the onset after the Hopf point; negative: before it), most of them rising "
                  f"with the ramp rate ({c['n_rising_with_rate']} of {c['n_series']} series are higher at the fastest ramp than at the slowest); octagon rings on the testable runs (their error numbers are not drawn; they are in the source data), diamond rings on {_NW[c['n_untest']]} untestable runs, a red ring on the main example, open squares on {_NW[d['n_hold']]} onsets during the hold, a band at the foot with {_NW[d['n_nocross']]} run without a crossing. "
                  f"The title is red: prediction FAIL, solver FAIL; a red note gives {d['n_testable_within_one_step']} of {d['n_testable']} testable runs within one step and the solver difference of {c['head_ms']:.0f} ms."),
            "b": "P5: the up delay, the offset on the way down (triangles, negative at the fast end) and the hysteresis width (dashed, dash-dot for the sigmoid profile) against the ramp rate, linear solid and sigmoid dotted; a dotted zero line.",
            "c": f"P1 linear at three start distances (0.5 dotted, 1.5 solid, 3.0 dashed): the delay against the ramp rate with octagon rings on the testable runs (their errors, {_fmt(min(c['sd5']))} to {_fmt(max(c['sd5']))} steps, are not drawn and are in the source data); a dotted zero line; a band at the foot.",
            "d": f"The floored delay at the main example for three noise-floor levels (0, 1, 2 on the x axis): ten seeds at four time steps drawn as concentric hollow circles, the medians are small negative numbers (about {c['med_cross'][0]:.4f}, {c['med_cross'][1]:.3f}, {c['med_cross'][2]:.3f}); a note points to the main example.",
            "e": f"The same runs read by the classifier onset: the delays tie at {c['tie']:g} at levels {_levels(c['tie_levels'])} and a higher value at level 2; the title is red (FAIL) and a red note says the delays tie at {c['tie']:g} at the {_NW[c['n_tie_levels']]} lower levels (saturated).",
        }
    return {
        "a": "Peak power (absolute) against the ramp rate for six noise-free series and a grey bar with a dark median mark for the ten noisy seeds of P2 at each of 13 ramp rates; the seed count is written above the panel; rings and foot marks as in F4a.",
        "b": "Peak power (relative) against the ramp rate, same marks as (a).",
        "c": "Peak frequency (Hz) against the ramp rate, same marks as (a); the axis does not start at zero.",
        "d": f"Duration (s, logarithmic axis) against the ramp rate with a dotted line at {c['dur_floor']:g} s ({duration_floor_sentence(c)}); medians at {c['dur_floor']:g} s are pinned by this floor.",
        "e": (f"The delay of the ten noisy seeds of P2 at each ramp rate (grey bars from minimum to maximum, dark medians; the medians are negative from T_ramp {n(c['t_neg'])} s on) beside the noise-free P2 line; the title is red (noise robustness FAIL) "
              f"and two red lines give {c['kept']} of {c['kept_n']} seeds ({c['kept_need']} needed) and {c['sub_agree']} of {c['sub_cells']} cells ({c['sub_needed']} needed)."),
        "f": f"The jump offset of the M2 ramp from the fold (logarithmic axis) against the ramp rate: it rises with the ramp rate, from {c['off_slow']:.4f} to {c['off_fast']:.3f} over {c['n_T']} ramp rates.",
        "g": f"The fitted ring rate of the M2 ramp against the ramp rate with one-standard-error bars: all values lie between {MINUS}{abs(c['rate_lo']):.1f} and {MINUS}{abs(c['rate_hi']):.1f} per s, below the dotted zero line (damped at {c['n_nonneg']} of {c['n_T']}).",
    }


def sections(fid: str, a11: list) -> tuple:
    """Supplement sections of the F4 journal files: the mapping of the draft panels, the stored FAIL rows, the stored names behind the plain words (and the departure from the single F4)."""
    from . import figures as FG
    inv = {v: k for k, v in PANELS[fid].items()}
    mapping = "; ".join(f"journal ({k}) = draft ({v})" for k, v in PANELS[fid].items())
    sib = "F4b" if fid == "F4a" else "F4a"
    mapping_text = (f"{fid} is one of the two JOURNAL files of the draft F4 (a departure from the plan's single F4, DL-667 K2: the draft is 7.4 x 16.2 in with 12 panels and does not fit 6.3 x 8.0 in at 8 pt without touching). "
                    f"The panels of {fid} are the draft panels as follows: {mapping}. The draft panels of {sib} are in {sib}. The union of the data arrays of {fid} and {sib} is the draft's data, each array with the draft's digest. "
                    "Which of the two files is tagged is the user's decision.")
    about = {"F4a": "The three rows RB3(a), RB3(b) and RB6 (solver) are about this figure; the RB2 rows are about F4b.",
             "F4b": "The two RB2 rows are about this figure; the RB3(a), RB3(b) and RB6 (solver) rows are about F4a."}[fid]
    return (("Mapping of the draft panels to the journal panels (DL-667 K2)", mapping_text), ("All FAIL rows of the stored A11 table (DL-667)", FG.JCAP.all_fail_rows_for(a11, about)),
            ("Stored names behind the plain words of the caption (DL-571 T8)", FG.CODE_NAMES_MD))


GLYPH_UNIT = 1.0           # scale of the glyph path (the marker is normalised afterwards; this is not a font size of drawn text)
DAGGER_EDGE = 0.3          # 13t-10 (DL-691 O3, second attempt): outline width in pt of the hollow double dagger (UNVERIFIED); the ruled size 6.0 pt and the stored positions are unchanged


def _dagger_outline():
    """The double dagger of the classifier onset as an outline marker (the glyph path of U+2021, centred, no fill when drawn with mfc='none'): the string marker $\ddagger$ is always filled by matplotlib (attempt 1)."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.markers import MarkerStyle
    from matplotlib.path import Path
    from matplotlib.textpath import TextPath
    tp = TextPath((0, 0), "‡", size=GLYPH_UNIT, prop=FontProperties(family="DejaVu Sans"))
    v = tp.vertices.copy()
    ctr = (v.max(axis=0) + v.min(axis=0)) / 2.0
    return MarkerStyle(Path(v - ctr, tp.codes))


def build(res=None, out_dir=None, *, root=None, script="scripts/fig_journal.py", tag_build: bool = False) -> dict:
    """The journal build of F4a and F4b from results/ (recorded results only): returns the dict of F4a with the dict of F4b under the key 'F4b'."""
    import dataclasses
    import time
    from pathlib import Path
    from .. import provenance as P
    from . import figures as FG
    root = Path(root) if root is not None else FG.repo_root()
    res = Path(res) if res is not None else root / "results"
    base = Path(out_dir) if out_dir is not None else root / "figures" / "journal"
    FG.F.require_buildable("F4")
    t = {"start": time.perf_counter()}
    raw = FG.load_F4(res)
    t["load"] = time.perf_counter()
    d = FG.prepare_F4(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for key, rec in raw["records"].items():
        for r in FG.make_param_table(rec["config"]):
            rows.append({**r, "panel": key, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    crit, _ = FG.F.K.load_frozen_criteria(root)
    cfg = J.load_config(root)
    c = f4_consts(d, rows, raw, raw["a11"], crit)
    drawn = FG.drawn_data_sha256(d)
    import matplotlib.pyplot as plt
    out: dict = {}
    for fid in F4_PARTS:
        ids = LIMITS[fid]
        cap = FG.CAP.build_caption("F4", take_home=FG.F4_TAKE_HOME, claim_limit_ids=ids, params_rows=[r for r in rows if r["key"] in FG.F4_CAPTION_KEYS], spectrogram=None, symbol_keys=(),
                                   notes=FG.f4_caption_notes(d), limit_labels=FG.CLAIM_LIMIT_LABELS, class_key=FG.CAP.class_key_line("ND", agree=True), classifier_line=FG.CAP.classifier_line(crit),
                                   main_failures=FG.F4_MAIN_FAILURES, swept={"path.T_ramp_s": d["p1_linear_T_ramp_s"], "path.name": ["path_eta", "path_hypoxia", "path_updown"], "path.profile": ["linear", "sigmoid"]})
        plain_md = PL.pairing_markdown(ids, None, cap.text)
        srows = strip_rows_of(fid, d)
        cap_fn, short_fn = (f4a_caption, f4a_short) if fid == "F4a" else (f4b_caption, f4b_short)
        jtext = cap_fn(d, raw["a11"], crit, rows, strip_rows=srows, ids=ids, c=c)
        short_text = short_fn(d, raw["a11"], srows, c, J.caption_limit(cfg, fid), jtext)
        folder = base / fid
        folder.mkdir(parents=True, exist_ok=True)
        stem = f"{fid}_journal"
        with plt.rc_context(J.rc_params(cfg)):
            fig = draw_F4a(d) if fid == "F4a" else draw_F4b(d)
            saved = J.save_all(fig, folder, stem, cfg)
        plt.close(fig)
        tt = dict(t)
        tt["draw"] = time.perf_counter()
        P.atomic_write_text(folder / f"{stem}_caption.txt", short_text + "\n")
        P.atomic_write_text(folder / f"{stem}_caption_full.txt", jtext + "\n")
        P.atomic_write_text(folder / f"{stem}_drawn_data_sha256.txt", drawn + "\n")
        warnings = [f"input record {k} ({rec['name']}) was written with git dirty = true" for k, rec in raw["records"].items() if (rec.get("git") or {}).get("dirty")]
        prov_kw = dict(script=script, inputs=[res / p for p in FG.F4_INPUTS] + [res / p for p in raw["record_files"]], params_rows=rows,
                       modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py", "src/mprsurge/plotting/jf4.py", "src/mprsurge/plotting/jf4cap.py",
                                "src/mprsurge/plotting/nordlie.py", "src/mprsurge/plotting/figprov.py"],
                       configs=["configs/base.yaml", "configs/S5_ramp.yaml"], claim_limits=cap.claim_limits,
                       input_tables=[{"path": res / FG.F4_INPUTS[0], "rows": len(raw["a7"])}, {"path": res / FG.F4_INPUTS[1], "rows": len(raw["a3"])}, {"path": res / FG.F4_INPUTS[3], "rows": len(raw["a11"])}],
                       spectrogram=None, tag_build=tag_build, root=root)
        out[fid] = FG._journal_tail(fid, folder, stem, saved, dataclasses.replace(cap, text=jtext), drawn, d, raw, prov_kw, warnings, strip=strip_lines_of(fid, d), footer=FG.F4_FOOTER, timing_t=tt,
                                    source_rows=source_rows(fid, d), alt=alt_text(fid, d, c), pointers=(), cfg=cfg, status_text="\n\n".join(FG.f4_status_lines(d)), plain_md=plain_md, prov_id="F4",
                                    extra_sections=sections(fid, raw["a11"]), strip_rows=srows)
    res_out = dict(out["F4a"])
    res_out["F4b"] = out["F4b"]
    return res_out
