"""Figure builders (MS13; plan section 10.1: plotting/figures.py, make_F1 ... make_FS6). make_F1 to make_F6 and make_FS1 to make_FS5 exist; make_FS6 refuses (MS12-C1).

A figure builder reads stored results under results/ (never simulates, never writes under results/), draws, and writes the figure, <ID>_provenance.json
and <ID>_params.csv into figures/<ID>/ through figprov. The step order is fixed: load_<ID> (files -> arrays), prepare_<ID> (pure: arrays -> the drawn
data), draw (matplotlib), then caption, provenance and the Nordlie table. The drawn data of prepare_<ID> is what test row 9 hashes.

Layout is a design choice, UNVERIFIED (docs/ms13_conventions.md). Colours, marks, sizes and the text style are style.py keys (13c onward; 13o, DL-494 R1 and R4: one text
style for every figure, applied by _style_text). Take-home messages, claim-limit lists and strips are ruled for every figure (RULED_DL; 13p, DL-500 R13);
captions print every claim limit with its definition (13o, R2) and group the parameters by key (R3).
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from pathlib import Path

import numpy as np

from ..analysis import surge_metrics as M
from ..config import repo_root
from ..params import make_param_table
from . import captions as CAP
from .claim_labels import A9_LABELS, CLAIM_LIMIT_LABELS
from . import figprov as F
from . import nordlie as N
from . import style as S

# ---- F3 declarations -------------------------------------------------------------------------------------------------------------------------------
# Paths relative to results/. The registry scripts/ms13_inputs.py INPUTS["F3"] must name the same files (test row 12).
F3_INPUTS = (
    "A4/a4_hopf_curves.npz",
    "A6/a6_freq_map.npz",
    "A6/a6_summary.json",
    "A4/A4_0000_4ece63ed731f.json",         # run record: source of the A4 rows of F3_params.csv
    "A6/A6_0000_daa85487fd0a.json",         # run record: source of the A6 rows of F3_params.csv
    "A11/a11_robustness.csv",               # stored A11 table: the FAIL-row strip is read from it, not recomputed
    # one run record per path (13e, DL-447): the only stored source of the resolved path values (config.path, config.model)
    "S5/ramp/p1_linear/p1_linear_0008_333859d6472b.json",       # P1, linear, T_ramp 100 s (no 120 s record exists for P1)
    "S5/ramp/S5ramp/S5ramp_0000_240de3ef73be.json",             # P2, linear, T_ramp 120 s (the headline record)
    "S6/S6_P3/S6_P3_0006_5fb237a3d3fd.json",                    # P3, linear, T_ramp 120 s, I_amp 1 (the default amplitude, DL-015)
    "S6/S6_P4a/S6_P4a_0002_42415b96d00c.json",                  # P4a, linear, T_ramp 120 s
    "S6/S6_P4b/S6_P4b_0002_7be4a3067a9d.json",                  # P4b, linear, T_ramp 120 s
    "S5/ramp/p5_linear/p5_linear_0008_da88da96d075.json",       # P5, linear, T_ramp 100 s
)
F3_RECORDS = {"A4": "A4/A4_0000_4ece63ed731f.json", "A6": "A6/A6_0000_daa85487fd0a.json"}
F3_PATH_RECORDS = dict(zip(("P1", "P2", "P3", "P4a", "P4b", "P5"), F3_INPUTS[6:]))
# config.path.name of each path (plan section 4.4); a record whose name differs is refused
PATH_NAMES = {"P1": "path_eta", "P2": "path_hypoxia", "P3": "path_drive", "P4a": "path_delta_up", "P4b": "path_delta_down", "P5": "path_updown"}
# Number of eta legs a path name defines (plan 4.4: P5 is "eta up over T_ramp, then down over T_ramp"); the record stores only the name, so the legs follow
# from it, and the tests check them against the stored eta trace next to the record (13e, DL-452).
LEGS = {"path_updown": 2}
# RB ids whose Table 7.2 "Where" column names F3 (plan.md line 852: RB9 -> "FS5; F3"). Reading of the table: UNVERIFIED.
FIGURE_RB = {"F3": ("RB9",)}
# DL-388 gives the RB9(b) numbers that the stored A11 table leaves blank (value column empty for that row).
STRIP_NOTE = {"b_spectral_vs_cycle_headline": "4.391 Hz against 0.5 Hz (DL-388)"}
DELTAS = ("0.05", "0.1", "0.3")             # the A6 eta-tau slices (DL-131)
LEVELS_HZ = (25.0, 100.0)                   # read back from a6_summary.json and checked

# Accepted by the reviewer (13e prompt, DL-453); every statement is from a logged result (DL-131, DL-132) and is checked against the stored A6 arrays
# by tests/test_fig_F3.py (counts and ranges) where the array holds it.
F3_TAKE_HOME = (
    "On the A6 slices the 100 Hz contour does not occur for eta_bar 0 to 8 (largest cycle frequency 73.7 Hz), and the 25 Hz "
    "contour crosses the cycle branch only on some slices (Delta 0.05 from tau_d 3 ms, Delta 0.1 from 5 ms, Delta 0.3 only at 13, 22 and 36 ms; "
    "DL-131), with the cycle at ref_devalle at 32.0 to 39.7 Hz (DL-131, DL-132)."
)
# MS11-C7 (every figure), MS12-C1 (F1 to F6), MS11-C3 (frequencies; docs/ms13_plan.md section 5). The RB9(b) FAIL row (DL-388) is in the FAIL strip of the
# figure, read from the stored A11 table. G6-D1: not listed, the arrows carry no predicted entry (DL-455; the ruled exception of DL-494 R5). 13o (DL-494 R5, DL-495): the plan
# label RB9(b) FAIL, which the plan's section 5 table lists for F3, is carried with its definition.
F3_CLAIM_LIMITS = ("MS11-C7", "MS12-C1", "MS11-C3", "RB9(b) FAIL (plan label)")
# keys of the A4 and A6 run records that define the plotted slices and the regime; the full list stays in F3_params.csv and the Nordlie table
CAPTION_KEYS = ("model.type", "model.ref_point", "model.tau_ms", "model.J")

_SLICE = re.compile(r"^eta_tau_D([0-9.]+)_td([0-9.]+)$")

# 13p (DL-500 R13, DL-501): every take-home, claim-limit list and strip is ruled; the footer and the strip heading name the ruling entries of each figure
# (the entries that accepted its take-home, limits and strip; DL-494 where R5 changed or ruled on its list; DL-500 for R13 itself). The DRAFT note stays while untagged.
RULED_DL = {"F1": ("DL-488", "DL-494", "DL-500"), "F2": ("DL-464", "DL-494", "DL-500"), "F3": ("DL-453", "DL-457", "DL-494", "DL-500"),
            "F4": ("DL-485", "DL-494", "DL-500"), "F5": ("DL-492", "DL-494", "DL-500"), "F6": ("DL-482", "DL-494", "DL-500"), "FS1": ("DL-472", "DL-494", "DL-500"),
            "FS2": ("DL-472", "DL-500"), "FS3": ("DL-482", "DL-485", "DL-494", "DL-500"), "FS4": ("DL-477", "DL-494", "DL-500"), "FS5": ("DL-477", "DL-494", "DL-500")}


def draft_footer(fig_id: str, head: str = "DRAFT", extra: str = "") -> str:
    return (f"{head}: untagged build. Layout, marks, colours and panel choices are UNVERIFIED (style.py); take-home and claim limits as ruled "
            f"({', '.join(RULED_DL[fig_id])})." + (f" {extra}" if extra else ""))


def strip_heading(fig_id: str) -> str:
    return f"FAIL rows of the stored A11 table that touch {fig_id} (as ruled: {', '.join(RULED_DL[fig_id])}):"


FOOTER = draft_footer("F3", head="DRAFT v3")


class DataError(F.FigureError):
    """A stored array does not have the shape or content the figure needs."""


def results_dir() -> Path:
    return repo_root() / "results"


# ---- load / prepare (the data step of test row 9) ------------------------------------------------------------------------------------------------

def load_F3(res=None) -> dict:
    """Open the files of F3_INPUTS under `res` (default results/) and return their content. Opens nothing else."""
    res = Path(res) if res is not None else results_dir()
    for rel in F3_INPUTS:
        if not (res / rel).is_file():
            raise F.MissingInputError(f"input file not found: {res / rel}")
    try:
        with np.load(res / F3_INPUTS[0], allow_pickle=False) as z:
            a4 = {k: z[k] for k in z.files}
        with np.load(res / F3_INPUTS[1], allow_pickle=False) as z:
            a6 = {k: z[k] for k in z.files}
        summary = json.loads((res / F3_INPUTS[2]).read_text(encoding="utf-8"))
        records = {k: json.loads((res / rel).read_text(encoding="utf-8")) for k, rel in F3_RECORDS.items()}
        paths = {k: json.loads((res / rel).read_text(encoding="utf-8")) for k, rel in F3_PATH_RECORDS.items()}
        with open(res / F3_INPUTS[5], newline="", encoding="utf-8") as fh:
            a11 = list(csv.DictReader(fh))
    except (OSError, ValueError, KeyError) as exc:
        raise F.MissingInputError(f"an F3 input cannot be read: {exc}") from exc
    return {"a4": a4, "a6": a6, "summary": summary, "records": records, "paths": paths, "a11": a11}


def prepare_F3(raw: dict) -> dict:
    """Pure: stored content -> the arrays and numbers that are drawn. Keys are flat names; values are float arrays, ints or strings."""
    a4, a6, summary = raw["a4"], raw["a6"], raw["summary"]
    if tuple(summary["levels_hz"]) != LEVELS_HZ:
        raise DataError(f"a6_summary levels_hz {summary['levels_hz']} is not {list(LEVELS_HZ)}")
    ids = [str(s) for s in a6["slice_ids"]]
    d: dict = {}
    for D in DELTAS:
        taus = np.asarray(a6[f"eta_tau_D{D}_other"], dtype=float)
        c25 = np.asarray(a6[f"eta_tau_D{D}_c25"], dtype=float)
        d[f"D{D}_tau_d_ms"] = taus
        d[f"D{D}_hopf_eta"] = np.array([a6["slice_hopf_param"][ids.index(f"eta_tau_D{D}_td{t:.1f}")] for t in taus])
        d[f"D{D}_c25_eta"] = c25
        d[f"D{D}_c25_count"] = np.asarray(a6[f"eta_tau_D{D}_c25_count"], dtype=float)
        d[f"D{D}_c100_count"] = np.asarray(a6[f"eta_tau_D{D}_c100_count"], dtype=float)
        eta, tau, f = [], [], []
        for i, t in enumerate(taus):
            k = ids.index(f"eta_tau_D{D}_td{t:.1f}")
            m = a6["po_slice_index"] == k
            eta.append(a6["po_param"][m])
            f.append(a6["po_frequency_hz"][m])
            tau.append(np.full(int(m.sum()), t))
        d[f"D{D}_po_eta"], d[f"D{D}_po_tau_d_ms"], d[f"D{D}_po_f_hz"] = (np.concatenate(x) for x in (eta, tau, f))
    d["f_min_hz"] = min(float(d[f"D{D}_po_f_hz"].min()) for D in DELTAS)
    d["f_max_hz"] = max(float(d[f"D{D}_po_f_hz"].max()) for D in DELTAS)
    d["a4_tau_d_ms"], d["a4_tau_d_eta_H"] = (np.asarray(a4[k], dtype=float) for k in ("curve_tau_d_ms", "curve_tau_d_eta_H"))
    d["a4_Delta"], d["a4_Delta_eta_H"] = (np.asarray(a4[k], dtype=float) for k in ("curve_Delta", "curve_Delta_eta_H"))
    ok = np.isfinite(d["a4_Delta_eta_H"])
    d["a4_Delta"], d["a4_Delta_eta_H"] = d["a4_Delta"][ok], d["a4_Delta_eta_H"][ok]
    # A4 curve parameters and the A6 headline point are read from the run records, never assumed (13e, DL-449)
    m4, m6 = raw["records"]["A4"]["config"]["model"], raw["records"]["A6"]["config"]["model"]
    d["a4_curve_Delta"], d["a4_curve_J"], d["a4_curve_tau_d_ms"] = float(m4["Delta"]), float(m4["J"]), float(m4["tau_d_ms"])
    d["headline_Delta"], d["headline_tau_d_ms"] = float(m6["Delta"]), float(m6["tau_d_ms"])
    if str(d["a4_curve_Delta"]) not in DELTAS or d["headline_Delta"] != d["a4_curve_Delta"]:
        raise DataError(f"A4 record Delta {d['a4_curve_Delta']} and A6 record Delta {d['headline_Delta']} are not a drawn slice Delta")
    d["headline_hopf_eta"] = float(d["D0.3_hopf_eta"][list(d["D0.3_tau_d_ms"]).index(5.0)])
    # agreement of the A4 tau_d curve with the A6 Hopf points at Delta 0.3 (log-tau interpolation); a number to look at, not a test
    d["a4_vs_a6_hopf_max_abs"] = float(np.max(np.abs(np.interp(np.log(d["D0.3_tau_d_ms"]), np.log(d["a4_tau_d_ms"]), d["a4_tau_d_eta_H"]) - d["D0.3_hopf_eta"])))
    d["c100_total_crossings"] = int(sum(d[f"D{D}_c100_count"].sum() for D in DELTAS))
    for D in DELTAS:
        d[f"D{D}_f_max_hz"] = float(d[f"D{D}_po_f_hz"].max())
    # path arrows: the resolved config.path values of the stored run records (13e, DL-452); nothing is retyped, nothing comes from the D12 rule
    for k, rec in raw["paths"].items():
        p, m = rec["config"]["path"], rec["config"]["model"]
        if p["name"] != PATH_NAMES[k] or p["profile"] != "linear" or rec["status"] != "ok":
            raise DataError(f"path record of {k}: name {p['name']!r}, profile {p['profile']!r}, status {rec['status']!r} are not the expected linear {PATH_NAMES[k]!r} ok record")
        for name in ("eta_start", "eta_peak", "eta_H", "T_ramp_s", "I_amp", "Delta_factor"):
            d[f"{k}_{name}"] = float(p[name])
        d[f"{k}_tau_d_ms"], d[f"{k}_Delta"] = float(m["tau_d_ms"]), float(m["Delta"])
        d[f"{k}_Delta_end_derived"] = d[f"{k}_Delta"] * d[f"{k}_Delta_factor"]          # derived in the script, labelled so in the caption
        d[f"{k}_legs"] = LEGS.get(p["name"], 1)
    d["strip"] = [{"rb_id": r["rb_id"], "check_id": r["check_id"], "value": r["value"], "threshold": r["threshold"], "status": r["pass_or_fail"]}
                  for r in raw["a11"] if r["rb_id"] in FIGURE_RB["F3"] and r["pass_or_fail"] == "FAIL"]
    return d


def drawn_data_sha256(d: dict) -> str:
    """SHA-256 over the drawn data (name, dtype, shape and bytes of each array; JSON text of every other value), keys sorted."""
    h = hashlib.sha256()
    for k in sorted(d):
        v = d[k]
        h.update(k.encode())
        if isinstance(v, np.ndarray):
            h.update(f"{v.dtype}{v.shape}".encode())
            h.update(np.ascontiguousarray(v).tobytes())
        else:
            h.update(json.dumps(v, sort_keys=True).encode())
    return h.hexdigest()


# ---- draw ------------------------------------------------------------------------------------------------------------------------------------------

def _style_text(fig, draft_text: str = ""):
    """13o (DL-494 R4): one text style for every figure, from style.py. Every panel title is moved to the left and gets the panel-title size (its colour is kept); axis
    labels, tick labels and legend texts get their role sizes; the DRAFT note is written at the bottom left of the canvas in a band the layout keeps free."""
    T = S.TEXT_SIZES
    for ax in fig.axes:
        centre = ax.get_title(loc="center")
        if centre:
            colour = ax.title.get_color()
            ax.set_title("", loc="center")
            ax.set_title(centre, loc=S.TITLE_LOC, color=colour)
        ax._left_title.set_fontsize(T["panel_title"])
        ax.xaxis.label.set_fontsize(T["axis_label"])
        ax.yaxis.label.set_fontsize(T["axis_label"])
        ax.tick_params(labelsize=T["tick"])
        lg = ax.get_legend()
        if lg is not None:
            for t in lg.get_texts():
                t.set_fontsize(T["legend"])
    if draft_text:
        b = S.DRAFT_NOTE["band"]
        fig.get_layout_engine().set(rect=(0.0, b, 1.0, 1.0 - b))
        t = fig.text(S.DRAFT_NOTE["x"], S.DRAFT_NOTE["y"], draft_text, fontsize=T["footer"], color=S.figure_colour("fail_text"), ha="left", va="bottom")
        t.set_gid("draft_note")
    return fig



PATH_ORDER = ("P1", "P2", "P3", "P4a", "P4b", "P5")
# How each path is drawn where several paths share one stored position (v3, 13g): no vertical offset, every arrow sits at its stored coordinates;
# the paths are nested by line width, transparency, start-marker size and head size (widest and faintest at the back). Design choices, UNVERIFIED.
# key: (line width pt, alpha, start-marker size pt, head scale)
PATH_DRAW = {"P1": (6.0, 0.35, 10.0, 10.0), "P2": (4.2, 0.55, 8.0, 8.5), "P3": (2.8, 0.80, 6.2, 7.0), "P4a": (1.1, 1.0, 5.0, 7.0), "P4b": (1.1, 1.0, 5.0, 7.0),
             "P5": (1.3, 1.0, 4.0, 5.0)}
PATH_Z = {"P1": 5, "P2": 6, "P3": 7, "P4a": 8, "P4b": 8, "P5": 9}
HOPF_Z = 12                                                      # the A6 Hopf point of the headline slice is drawn on top of every arrow
STRIP_ROWS = (("P1", 0), ("P2", 0), ("P3", 0), ("P4a", 0), ("P4b", 0), ("P5", 0), ("P5", 1))        # (path, leg): the strip has one row per arrow


def note_100hz(d: dict, D: str) -> str:
    """The 100 Hz statement of a panel, in words, from the stored arrays (counts and the largest cycle frequency of that slice set)."""
    n = int(d[f"D{D}_c100_count"].sum())
    if n == 0:
        return f"no 100 Hz contour in range, maximum {d[f'D{D}_f_max_hz']:.1f} Hz"
    return f"100 Hz contour: {n} crossings"


def shared_position_sentence(d: dict) -> str:
    """Caption sentence on the paths that share a stored position; the numbers are the stored ones, the grouping is computed."""
    groups: dict = {}
    for k in PATH_ORDER:
        if d[f"{k}_Delta_end_derived"] != d[f"{k}_Delta"]:
            continue                                   # P4a and P4b leave the shared position in Delta; they are drawn as their own diagonals
        groups.setdefault((d[f"{k}_eta_start"], d[f"{k}_eta_peak"], d[f"{k}_Delta"], d[f"{k}_tau_d_ms"]), []).append(k)
    shared = [(key, g) for key, g in groups.items() if len(g) > 1]
    if not shared:
        return "Every arrow is drawn at its stored position."
    (e0, e1, dl, td), g = shared[0]
    names = ", ".join(g[:-1]) + " and " + g[-1]
    return (f"Every arrow is drawn at its stored position and no shift is applied: {names} start at the same eta_bar {e0:.3f}, peak at {e1:.3f} and sit at "
            f"Delta {dl:g}, tau_d {td:g} ms, so they lie on top of each other and are told apart by line width, transparency and marker size; "
            "the path strip lists every arrow on its own row, and its rows are labels, not a parameter axis.")


def _arrow(ax, x0, x1, y0, y1, k, gid):
    """One path arrow in data coordinates (annotation with the stored start and end) plus its start marker. No transform shift."""
    st = S.get(k)
    lw, alpha, msz, head = PATH_DRAW[k]
    ann = ax.annotate("", xy=(x1, y1), xytext=(x0, y0), xycoords="data", textcoords="data", zorder=PATH_Z[k],
                      arrowprops=dict(arrowstyle="-|>", color=st.colour, lw=lw, ls=st.linestyle, alpha=alpha, shrinkA=0, shrinkB=0, mutation_scale=head))
    ann.set_gid(f"arrow:{gid}")
    (mk,) = ax.plot([x0], [y0], ls="none", marker=st.marker, ms=msz, color=st.colour, mec=S.HALO_COLOUR, mew=0.5, alpha=max(alpha, 0.6),
                    zorder=PATH_Z[k] + 0.5, clip_on=False)
    mk.set_gid(f"start:{gid}")


def _draw_paths(ax, d: dict, *, plane: str, y0: float):
    """Arrows of P1, P2, P3 and P5 (up and return) at the stored y0, in data coordinates; in the Delta plane also the diagonal P4a and P4b."""
    for k in ("P1", "P2", "P3", "P5"):
        for leg in range(int(d[f"{k}_legs"])):
            a, b = d[f"{k}_eta_start"], d[f"{k}_eta_peak"]
            x0, x1 = (a, b) if leg == 0 else (b, a)
            _arrow(ax, x0, x1, y0, y0, k, f"{plane}:{k}:{leg}")
    if plane == "Delta":
        for k in ("P4a", "P4b"):
            _arrow(ax, d[f"{k}_eta_start"], d[f"{k}_eta_peak"], d[f"{k}_Delta"], d[f"{k}_Delta_end_derived"], k, f"{plane}:{k}:0")


def _draw_strip(ax, d: dict):
    """Path strip aligned to the eta axis: one row per arrow, x = the stored eta_bar, y = row number (a label, not a parameter)."""
    names = {"P1": "P1 eta ramp", "P2": "P2 hypoxia", "P3": "P3 drive", "P4a": "P4a Delta up", "P4b": "P4b Delta down", "P5": "P5 up"}
    labels = []
    for i, (k, leg) in enumerate(STRIP_ROWS):
        a, b = d[f"{k}_eta_start"], d[f"{k}_eta_peak"]
        x0, x1 = (a, b) if leg == 0 else (b, a)
        st = S.get(k)
        ann = ax.annotate("", xy=(x1, i), xytext=(x0, i), xycoords="data", textcoords="data", zorder=5,
                          arrowprops=dict(arrowstyle="-|>", color=st.colour, lw=S.F3_MARKS["strip_arrow_width"], ls=st.linestyle, shrinkA=0, shrinkB=0,
                                          mutation_scale=S.F3_MARKS["strip_head"]))
        ann.set_gid(f"arrow:strip:{k}:{leg}")
        (mk,) = ax.plot([x0], [i], ls="none", marker=st.marker, ms=S.F3_MARKS["strip_start_size"], color=st.colour, mec=S.HALO_COLOUR, mew=0.4, zorder=6, clip_on=False)
        mk.set_gid(f"start:strip:{k}:{leg}")
        labels.append((names[k] if leg == 0 else "P5 return") + f" ({d[f'{k}_T_ramp_s']:g} s)")
    ax.set_ylim(len(STRIP_ROWS) - 0.5, -0.5)
    ax.set_yticks(range(len(STRIP_ROWS)), labels)
    ax.tick_params(axis="x", labelbottom=False, length=2)
    ax.tick_params(axis="y", length=2)
    ax.set_title("path strip: one row per arrow, rows are labels", loc=S.TITLE_LOC)


def _draw_F3(d: dict, draft: bool, strip_lines: list[str]):
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    mf, hp = S.get("mean_field"), S.diagram_mark("hopf_point")
    m25 = S.contour_mark("25hz")
    fig = plt.figure(figsize=(7.4, 8.9), constrained_layout=True)
    gs = fig.add_gridspec(4, 4, width_ratios=[1, 1, 1, 0.05], height_ratios=[1.45, 1.05, 1.55, 0.5])
    vmin, vmax = d["f_min_hz"], d["f_max_hz"]
    sc = None
    a4_D = f"{d['a4_curve_Delta']:g}"

    def hopf_mark(ax, y):
        # 13o (DL-494 R11): smaller than the 13g mark and without the white halo, so the 5 ms slice line under it stays visible
        (h,) = ax.plot([d["headline_hopf_eta"]], [y], ls="none", marker=hp.marker, ms=S.F3_MARKS["a6_hopf_size"], mew=S.F3_MARKS["a6_hopf_width"], color=hp.colour,
                       mec=hp.colour, zorder=HOPF_Z)
        h.set_gid("a6_hopf_point")

    for j, D in enumerate(DELTAS):
        ax = fig.add_subplot(gs[0, j])
        sc = ax.scatter(d[f"D{D}_po_eta"], d[f"D{D}_po_tau_d_ms"], c=d[f"D{D}_po_f_hz"], s=S.F3_MARKS["cycle_size"], marker=S.F3_MARKS["cycle_marker"], linewidths=0, cmap=S.FREQUENCY_CMAP,
                        vmin=vmin, vmax=vmax, rasterized=True)
        ax.plot(d[f"D{D}_hopf_eta"], d[f"D{D}_tau_d_ms"], ls="none", marker=mf.marker, ms=S.F3_MARKS["slice_hopf_size"], color=mf.colour)
        c = np.isfinite(d[f"D{D}_c25_eta"])
        ax.plot(d[f"D{D}_c25_eta"][c], d[f"D{D}_tau_d_ms"][c], ls="none", marker=m25.marker, ms=m25.size, mew=m25.width, color=m25.colour,
                mec=S.HALO_COLOUR, zorder=4)
        if D == a4_D:
            ax.plot(d["a4_tau_d_eta_H"], d["a4_tau_d_ms"], ls=mf.linestyle, color=mf.colour, lw=1.0)
            _draw_paths(ax, d, plane="tau_d", y0=d["P1_tau_d_ms"])
            hopf_mark(ax, d["headline_tau_d_ms"])
        ax.set_yscale("log")
        ax.set_xlabel(r"$\bar\eta$")
        ax.set_ylabel(r"$\tau_d$ (ms)" if j == 0 else "")
        ax.set_title(rf"({'abc'[j]}) $\Delta$ = {D}" + "\n" + note_100hz(d, D).replace(", maximum", ",\nmaximum"), loc=S.TITLE_LOC)
        ax.set_xlim(0, 8)
    cb = fig.colorbar(sc, cax=fig.add_subplot(gs[0, 3]))
    cb.set_label("limit-cycle frequency (Hz)")
    axd = fig.add_subplot(gs[2, 0:2])
    axd.plot(d["a4_Delta_eta_H"], d["a4_Delta"], ls=mf.linestyle, color=mf.colour, lw=1.0)
    _draw_paths(axd, d, plane="Delta", y0=d["P1_Delta"])
    hopf_mark(axd, d["headline_Delta"])
    ends = [d[f"{k}_Delta_end_derived"] for k in ("P4a", "P4b")]
    axd.set_yscale("log")
    axd.set_xlim(0, 8)
    axd.set_ylim(min(d["a4_Delta"].min(), *ends) * 0.8, max(d["a4_Delta"].max(), *ends) * 1.25)
    axd.set_xlabel(r"$\bar\eta$")
    axd.set_ylabel(r"$\Delta$")
    axd.set_title(r"(d) ($\bar\eta$, $\Delta$): Hopf curve and paths", loc=S.TITLE_LOC)
    axs = fig.add_subplot(gs[1, 0:2], sharex=axd)
    _draw_strip(axs, d)
    axt = fig.add_subplot(gs[1:3, 2:4])
    axt.axis("off")

    def wrap(s):
        return "\n".join(textwrap.wrap(s, 44))

    handles = [Line2D([], [], ls="none", marker=mf.marker, ms=S.F3_MARKS["slice_hopf_size"], color=mf.colour, label="Hopf point of an A6 slice"),
               Line2D([], [], ls="none", marker=m25.marker, ms=m25.size - 2, mew=m25.width, color=m25.colour, mec=S.HALO_COLOUR, label="25 Hz crossing of an A6 slice"),
               Line2D([], [], ls=mf.linestyle, color=mf.colour, lw=1.0,
                      label=wrap(f"Hopf curve (A4 record: Delta {d['a4_curve_Delta']:g}, J {d['a4_curve_J']:g}, tau_d {d['a4_curve_tau_d_ms']:g} ms)")),
               Line2D([], [], ls="none", marker=hp.marker, ms=S.F3_MARKS["a6_hopf_size"], mew=S.F3_MARKS["a6_hopf_width"], color=hp.colour,
                      label=wrap(f"A6 Hopf point, Delta {d['headline_Delta']:g}, tau_d {d['headline_tau_d_ms']:g} ms (not the A4 curve)"))]
    names = {"P1": "eta ramp", "P2": "hypoxia, eta part", "P3": f"drive, eta part, I_amp {d['P3_I_amp']:g}", "P4a": "Delta up", "P4b": "Delta down",
             "P5": "eta up, then return"}
    for k in PATH_ORDER:
        st = S.get(k)
        handles.append(Line2D([], [], ls=st.linestyle, marker=st.marker, ms=S.F3_MARKS["key_path_size"], lw=2, color=st.colour, label=wrap(f"{k} {names[k]} (T_ramp {d[f'{k}_T_ramp_s']:g} s)")))
    leg = axt.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=S.TEXT_SIZES["legend"], ncol=1, frameon=False, borderaxespad=0, labelspacing=0.55)
    leg.set_in_layout(False)
    axb = fig.add_subplot(gs[3, :])
    axb.axis("off")
    t1 = axb.text(0.0, 1.0, "FAIL rows of the stored A11 table that touch F3 (not recomputed):", va="top", fontsize=S.TEXT_SIZES["status"], weight="bold")
    t2 = axb.text(0.0, 0.8, "\n".join(strip_lines) if strip_lines else "none", va="top", fontsize=S.TEXT_SIZES["status"])
    t3 = axb.text(0.0, 0.42, "Not drawn: (eta, Delta) frequency shading (A6 has no Delta slices), the J plane, the J ramp of P2 and P3, the sigmoid and "
                  "start-distance variants.", va="top", fontsize=S.TEXT_SIZES["status"])
    for t in (t1, t2, t3):
        t.set_in_layout(False)
    return _style_text(fig, FOOTER if draft else "")


def _params_rows(raw: dict) -> list[dict]:
    rows = []
    for panel, rec in raw["records"].items():
        for r in make_param_table(rec["config"]):
            rows.append({**r, "panel": panel, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    return rows


def strip_lines(d: dict) -> list[str]:
    out = []
    for r in d["strip"]:
        val = r["value"] if r["value"] else "value blank in the table"
        note = STRIP_NOTE.get(r["check_id"], "")
        thr = f"threshold {r['threshold']}" if r["threshold"] else "threshold blank in the table"
        out.append(f"{r['rb_id']} {r['check_id']}: {r['status']} ({val}; {thr})" + (f"; {note}" if note else ""))
    return out


def caption_notes(d: dict) -> tuple:
    """Sentences about what is and is not drawn (13e, DL-453). Values come from the prepared data; only the wording is typed here."""
    t_ramp = sorted({d[f"{k}_T_ramp_s"] for k in PATH_ORDER})
    if d["c100_total_crossings"] == 0:
        hz100 = f"No 100 Hz contour in range on any slice; the largest cycle frequency is {d['f_max_hz']:.1f} Hz."
    else:
        hz100 = f"{d['c100_total_crossings']} crossings of the 100 Hz contour."
    return (
        "Colour and contours show the limit-cycle frequency of the continuation (A6), not the classifier's spectral peak; there is no interpolation between slices.",
        hz100,
        "Panels (a) to (c) are the A6 (eta, tau_d) slices; panel (d) shows the Hopf curve only, because A6 stores no Delta slices (UNVERIFIED reading of Table 8.1).",
        f"The A4 curve and the A6 Hopf points are separate markers (A4 record: Delta {d['a4_curve_Delta']:g}, J {d['a4_curve_J']:g}); no claim that they agree.",
        (f"Arrows show the stored linear-profile path values (T_ramp {', '.join(f'{x:g}' for x in t_ramp)} s; the path values are identical at every stored "
         f"T_ramp). P3 is drawn for I_amp {d['P3_I_amp']:g} only. The J ramp of P2 and P3 is not drawn. The end Delta of P4a and P4b is derived (stored Delta "
         "times stored Delta_factor). " + shared_position_sentence(d)),
        "Only the parameters that define the plotted slices and the regime are listed.",
    )


def make_F3(res=None, out_dir=None, *, tag_build: bool = False, take_home=F3_TAKE_HOME, claim_limit_ids=F3_CLAIM_LIMITS,
            script="scripts/fig_F3.py", root=None) -> dict:
    """Build F3 from results/. Returns {'prov', 'paths', 'timing_s', 'drawn_sha256'}. tag_build=True needs a clean tree (figprov)."""
    F.require_buildable("F3")
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "F3"
    t = {"start": time.perf_counter()}
    raw = load_F3(res)
    t["load"] = time.perf_counter()
    d = prepare_F3(raw)
    t["prepare"] = time.perf_counter()
    rows = _params_rows(raw)
    cap = CAP.build_caption("F3", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=[r for r in rows if r["key"] in CAPTION_KEYS],
                            spectrogram=None, symbol_keys=PATH_ORDER + ("mean_field",), notes=caption_notes(d))
    import matplotlib.pyplot as plt
    fig = _draw_F3(d, draft=not tag_build, strip_lines=strip_lines(d))
    out.mkdir(parents=True, exist_ok=True)
    pdf, png = out / "F3.pdf", out / "F3.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=S.PNG_DPI)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    cap_path, dig_path = out / "F3_caption.txt", out / "F3_drawn_data_sha256.txt"
    from .. import provenance as P
    drawn = drawn_data_sha256(d)
    P.atomic_write_text(cap_path, cap.text + "\n")
    P.atomic_write_text(dig_path, drawn + "\n")
    warnings = []
    for k, rec in {**raw["records"], **raw["paths"]}.items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true (DL-124: a clean-tree rerun gave identical arrays)")
    warnings.append(f"A4 tau_d curve (record Delta {d['a4_curve_Delta']:g}, J {d['a4_curve_J']:g}) against the A6 Hopf points at Delta {d['headline_Delta']:g}: "
                    f"max |difference| {d['a4_vs_a6_hopf_max_abs']:.3e}, read as interpolation error of the 30-point A4 grid (UNVERIFIED); drawn as separate markers")
    prov = F.write_figure_provenance(
        "F3", script=script, inputs=[res / p for p in F3_INPUTS], outputs=[pdf, png, cap_path, dig_path], params_rows=rows,
        modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py",
                 "src/mprsurge/plotting/nordlie.py", "src/mprsurge/plotting/figprov.py"],
        configs=["configs/A4_grids.yaml", "configs/A6.yaml"], claim_limits=cap.claim_limits, spectrogram=None, tag_build=tag_build,
        out_dir=out, root=root, warnings=warnings, wall_time_s=time.perf_counter() - t["start"])
    nordlie_path = out / "F3_nordlie.md"
    N.write_nordlie(out / "F3_params.csv", out / "F3_provenance.json", nordlie_path, root=root)
    t["end"] = time.perf_counter()
    timing = {"load_s": t["load"] - t["start"], "prepare_s": t["prepare"] - t["load"], "draw_s": t["draw"] - t["prepare"],
              "provenance_and_nordlie_s": t["end"] - t["draw"], "total_s": t["end"] - t["start"]}
    return {"prov": prov, "paths": [pdf, png, cap_path, dig_path, out / "F3_params.csv", out / "F3_provenance.json", nordlie_path],
            "timing_s": timing, "drawn_sha256": drawn, "caption": cap.text}


# ---- F2 (13f) --------------------------------------------------------------------------------------------------------------------------------------
# Paths relative to results/. The registry scripts/ms13_inputs.py INPUTS["F2"] must name the same files (the S4 records as json plus their npz; test).
F2_INPUTS = (
    "A5/a5_cycles.npz",                                      # devalle branch: cycle max/min, stable flags, fixed points, Hopf eta_bar (DL-126)
    "A5/julia/a5.json",                                      # Hopf type and the 'fold' turn-around entry (DL-126)
    "A5/A5_0000_506cf5745380.json",                          # run record: source of the A5 rows of F2_params.csv
    "S4/devalle/devalle_0000_48a5a3bd19e9.json",             # S4 mean-field sweep record (61 steps up then down; DL-127)
    "S4/devalle/devalle_0000_48a5a3bd19e9.npz",              # its series (v, step): read-window max and min are taken here
    "S4/net/net_0000_38692898ae60.json",                     # S4 network sweep record (15 steps up then down; DL-128)
    "S4/net/net_0000_38692898ae60.npz",
    "S4/s4_summary.npz",                                     # stored per-step readouts, mean field (v_ptp checked against the series)
    "S4/s4_net_summary.npz",                                 # stored per-step readouts, network, and the stored network-against-mean-field differences
    "A11/a11_robustness.csv",                                # stored A11 table: the FAIL-row strip is read from it, not recomputed
)
F2_RECORDS = {"A5": F2_INPUTS[2], "S4_mf": F2_INPUTS[3], "S4_net": F2_INPUTS[5]}
F2_STRIP_RB = ("RB1",)       # network against mean field. UNVERIFIED reading: Table 7.2 'Where' names F2 for no RB id; RB1 is listed because F2 draws network symbols
F2_JUDGED_ABOVE = 0.1        # DL-129 (D-3, CP23): steps within 0.1 of eta_H are excluded from the amplitude comparison; the relative difference is drawn above it only
F2_CAPTION_KEYS = ("model.type", "model.ref_point", "model.tau_ms", "model.tau_d_ms", "model.J", "model.Delta", "network.N", "s4.param", "s4.step_s", "s4.read_s",
                   "s4.n_points", "s4.indices")

# Accepted as proposed by the reviewer (13g prompt, DL-460); every statement is from a logged result (DL numbers in the text) and the numbers are checked
# against the stored arrays by tests/test_fig_F2.py.
F2_TAKE_HOME = (
    "At ref_devalle the limit cycle appears at eta_bar 2.896 in a supercritical Hopf bifurcation, with no fold of cycles and stable "
    "cycles to eta_bar 8 (A5; DL-126). The quasi-static mean-field sweeps up and down (S4) lie on that branch with no hysteresis loop from 0.2 above the "
    "Hopf point (largest up-down difference in the v amplitude 1.2e-3 relative, stored arrays; A5 against S4 at most 1.84e-3, DL-129). The N = 1e4 network "
    "sweep follows the branch less closely: its v amplitude differs from the mean field by +13.2 to -2.5 percent above eta_bar 3.0 (a different "
    "definition of v; information only, no criterion; DL-128, DL-129), and below the Hopf point it does not rest (v amplitude 0.22 to 0.31; DL-128)."
)
# Ruled in the 13g prompt: MS11-C7 (every figure), MS12-C1 (F1 to F6, as ruled for F3, DL-453), G4-C2 (network symbols are drawn; the table lists F1, F5 and
# FS3 for G4-C1 to C3 and does not list F2: UNVERIFIED reading). MS11-C3 and G6-D1 are left out (no frequency, no onset drawn).
F2_CLAIM_LIMITS = ("MS11-C7", "MS12-C1", "G4-C2")
F2_FOOTER = draft_footer("F2", head="DRAFT v2", extra="G4-C2 and the RB1 FAIL-row list are UNVERIFIED readings.")


def load_F2(res=None) -> dict:
    """Open the files of F2_INPUTS under `res` (default results/) and return their content. Opens nothing else."""
    res = Path(res) if res is not None else results_dir()
    for rel in F2_INPUTS:
        if not (res / rel).is_file():
            raise F.MissingInputError(f"input file not found: {res / rel}")
    try:
        with np.load(res / F2_INPUTS[0], allow_pickle=False) as z:
            a5 = {k: z[k] for k in z.files}
        a5json = json.loads((res / F2_INPUTS[1]).read_text(encoding="utf-8"))
        records = {k: json.loads((res / rel).read_text(encoding="utf-8")) for k, rel in F2_RECORDS.items()}
        series = {}
        for key, rel in (("mf", F2_INPUTS[4]), ("net", F2_INPUTS[6])):
            with np.load(res / rel, allow_pickle=False) as z:
                series[key] = {k: z[k] for k in ("t_ms", "v", "step", "step_param", "step_up")}
        with np.load(res / F2_INPUTS[7], allow_pickle=False) as z:
            summ_mf = {k: z[k] for k in z.files}
        with np.load(res / F2_INPUTS[8], allow_pickle=False) as z:
            summ_net = {k: z[k] for k in z.files}
        with open(res / F2_INPUTS[9], newline="", encoding="utf-8") as fh:
            a11 = list(csv.DictReader(fh))
    except (OSError, ValueError, KeyError) as exc:
        raise F.MissingInputError(f"an F2 input cannot be read: {exc}") from exc
    return {"a5": a5, "a5json": a5json, "records": records, "series": series, "summ_mf": summ_mf, "summ_net": summ_net, "a11": a11}


def _read_window_extrema(s: dict, read_s: float):
    """Per step: maximum and minimum of v over the read window (the last `read_s` seconds, the rule of analysis.s4.step_table)."""
    t, v, k = s["t_ms"], s["v"], s["step"]
    n = int(s["step_param"].size)
    vmax, vmin = np.full(n, np.nan), np.full(n, np.nan)
    for i in range(n):
        m = k == i
        ti, vi = t[m], v[m]
        vi = vi[ti >= ti[-1] - 1e3 * read_s - 1e-9]
        vmax[i], vmin[i] = vi.max(), vi.min()
    return vmax, vmin


def prepare_F2(raw: dict) -> dict:
    """Pure: stored content -> the arrays and numbers that are drawn. Keys are flat names; values are float arrays, ints, bools or strings."""
    a5, js = raw["a5"], raw["a5json"]
    d: dict = {}
    branch = js["branches"]["devalle"]
    d["eta_H"] = float(a5["devalle_hopf_eta_bar"][0])
    if d["eta_H"] != float(branch["hopf_param"]):
        raise DataError(f"A5 npz Hopf eta_bar {d['eta_H']!r} is not the a5.json value {branch['hopf_param']!r}")
    d["hopf_type"], d["hopf_frequency_hz"] = str(branch["hopf_type"]), float(branch["hopf_frequency_hz"])
    d["a5_special_points"] = [{"type": p["type"], "param": float(p["param"]), "direction": p["direction"]} for p in branch["po_special_points"]]
    d["a5_cycle_unstable_count"] = int((~a5["devalle_stable"]).sum())
    if d["a5_cycle_unstable_count"]:
        raise DataError(f"{d['a5_cycle_unstable_count']} unstable cycle points in the A5 devalle branch: the draft draws stable cycles only")
    up = a5["devalle_direction_up"].astype(bool)
    for name, m in (("up", up), ("down", ~up)):
        d[f"a5_{name}_param"] = np.asarray(a5["devalle_param"][m], dtype=float)
        d[f"a5_{name}_vmax"] = np.asarray(a5["devalle_vmax"][m], dtype=float)
        d[f"a5_{name}_vmin"] = np.asarray(a5["devalle_vmin"][m], dtype=float)
        d[f"a5_{name}_amp"] = np.asarray(a5["devalle_amplitude_v"][m], dtype=float)
    d["a5_eta_max"], d["a5_cycle_count"] = float(a5["devalle_param"].max()), int(a5["devalle_param"].size)
    fp = np.asarray(a5["devalle_fixed_param"], dtype=float)
    d["fixed_param"], d["fixed_v"] = fp, np.asarray(a5["devalle_fixed_v"], dtype=float)
    d["fixed_stable"] = np.asarray(a5["devalle_fixed_stable"], dtype=bool).astype(float)
    d["hopf_v_interp"] = float(np.interp(d["eta_H"], fp, d["fixed_v"]))             # derived: the fixed-point v at eta_H, linear between stored points
    d["A_ref"] = float(a5["A_ref"][0])
    # S4: the read-window extrema come from the stored series; the stored per-step v_ptp is the check
    for key, summ, rec_name, pre in (("mf", raw["summ_mf"], "S4_mf", "devalle"), ("net", raw["summ_net"], "S4_net", "net")):
        s, rd = raw["series"][key], float(raw["records"][rec_name]["config"]["s4"]["read_s"])
        vmax, vmin = _read_window_extrema(s, rd)
        p = np.asarray(s["step_param"], dtype=float)
        if not np.array_equal(p, np.asarray(summ[f"{pre}_param"], dtype=float)):
            raise DataError(f"S4 {key}: the step parameters of the series and of the stored summary differ")
        ptp = np.asarray(summ[f"{pre}_v_ptp"], dtype=float)
        gap = float(np.max(np.abs((vmax - vmin) - ptp)))
        if gap > 1e-12:
            raise DataError(f"S4 {key}: read-window max - min differs from the stored v_ptp by {gap:.3e}")
        d[f"{key}_param"], d[f"{key}_up"] = p, np.asarray(s["step_up"], dtype=bool).astype(float)
        d[f"{key}_vmax"], d[f"{key}_vmin"], d[f"{key}_v_ptp"] = vmax, vmin, ptp
        d[f"{key}_r_ptp"] = np.asarray(summ[f"{pre}_r_ptp"], dtype=float)
        d[f"{key}_ptp_check_max_abs"] = gap
    net = raw["summ_net"]
    d["cmp_mf_v_ptp"] = np.asarray(net["cmp_mf_v_ptp"], dtype=float)
    d["cmp_rel_v_ptp"], d["cmp_rel_r_ptp"] = (np.asarray(net[k], dtype=float) for k in ("cmp_rel_v_ptp", "cmp_rel_r_ptp"))
    above = d["net_param"] > d["eta_H"] + F2_JUDGED_ABOVE
    below = d["net_param"] < d["eta_H"] - F2_JUDGED_ABOVE
    d["net_above_mask"] = above.astype(float)
    d["cmp_rel_v_above_min"], d["cmp_rel_v_above_max"] = float(d["cmp_rel_v_ptp"][above].min()), float(d["cmp_rel_v_ptp"][above].max())
    d["cmp_rel_r_above_min"], d["cmp_rel_r_above_max"] = float(d["cmp_rel_r_ptp"][above].min()), float(d["cmp_rel_r_ptp"][above].max())
    d["net_floor_steps"] = int(below.sum())
    d["net_floor_v_ptp_min"], d["net_floor_v_ptp_max"] = float(d["net_v_ptp"][below].min()), float(d["net_v_ptp"][below].max())
    d["net_floor_r_ptp_min"], d["net_floor_r_ptp_max"] = float(d["net_r_ptp"][below].min()), float(d["net_r_ptp"][below].max())
    d["cmp_rel_v_below_max_abs"] = float(np.nanmax(np.abs(d["cmp_rel_v_ptp"][below])))
    # mean-field up-down difference of the stored v_ptp, from 0.2 above the Hopf point (the stored pair arrays)
    pp, rr = np.asarray(raw["summ_mf"]["devalle_pair_param"], dtype=float), np.asarray(raw["summ_mf"]["devalle_pair_v_ptp_rel_diff"], dtype=float)
    d["mf_updown_max_abs_from_0p2"] = float(np.nanmax(np.abs(rr[pp >= d["eta_H"] + 0.2 - 1e-6])))
    d["strip"] = [{"rb_id": r["rb_id"], "check_id": r["check_id"], "value": r["value"], "threshold": r["threshold"], "status": r["pass_or_fail"]}
                  for r in raw["a11"] if r["rb_id"] in F2_STRIP_RB and r["pass_or_fail"] == "FAIL"]
    return d


def _vline_hopf(ax, d: dict):
    hp = S.diagram_mark("hopf_point")
    ax.axvline(d["eta_H"], color=hp.colour, ls=hp.linestyle, lw=hp.width, zorder=1)


def _s4_points(ax, d: dict, key: str, ycol: str, kind: str, *, label: str | None = None, mask=None):
    """The step symbols of one source ('mf' or 'net'), up and down sweeps with their own marks."""
    for direction in ("up", "down"):
        m = d[f"{key}_up"] == (1.0 if direction == "up" else 0.0)
        if mask is not None:
            m = m & mask
        st = S.diagram_mark(f"s4_{kind}_{direction}")
        # 13o (DL-494 R12): the network symbols are drawn smaller than their 13f size so the A5 line under them stays visible
        size, width = (S.F2_MARKS["net_size"], S.F2_MARKS["net_width"]) if kind == "net" else (st.size, st.width)
        ax.plot(d[f"{key}_param"][m], d[ycol][m], ls="none", marker=st.marker, ms=size, mew=width, mfc=st.colour if st.filled else "none",
                mec=st.colour, color=st.colour, zorder=5 if kind == "net" else 4, clip_on=False,
                label=(f"{label}, {direction} sweep" if label else None))


def _draw_F2(d: dict, draft: bool, strip_lines: list[str]):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    cyc, fs, fu, hp = S.diagram_mark("a5_cycle"), S.diagram_mark("a5_fixed_stable"), S.diagram_mark("a5_fixed_unstable"), S.diagram_mark("hopf_point")
    fig = plt.figure(figsize=(7.4, 8.6), constrained_layout=True)
    gs = fig.add_gridspec(4, 1, height_ratios=[1.7, 1.15, 0.95, 1.05])
    xlim = (0.0, 8.0)
    # (a) cycle maximum and minimum of v
    ax = fig.add_subplot(gs[0])
    st = d["fixed_stable"] == 1.0
    for m, mk, lab in ((st, fs, "A5 fixed point, stable"), (~st, fu, "A5 fixed point, unstable")):
        seg = np.where(m, d["fixed_v"], np.nan)
        ax.plot(d["fixed_param"], seg, color=mk.colour, ls=mk.linestyle, lw=mk.width, label=lab, zorder=2)
    for name in ("up", "down"):
        for ycol in ("vmax", "vmin"):
            ax.plot(d[f"a5_{name}_param"], d[f"a5_{name}_{ycol}"], color=cyc.colour, lw=cyc.width, zorder=3,
                    label="A5 stable cycle maximum and minimum of v" if (name, ycol) == ("up", "vmax") else None)
    _vline_hopf(ax, d)
    ax.plot([d["eta_H"]], [d["hopf_v_interp"]], ls="none", marker=hp.marker, ms=hp.size, color=hp.colour, mew=hp.width, zorder=6,
            label=f"Hopf point, eta_bar {d['eta_H']:.3f} ({d['hopf_type']})")
    for key, kind, lab in (("mf", "mf", "S4 mean field"), ("net", "net", "S4 network N = 1e4")):
        _s4_points(ax, d, key, f"{key}_vmax", kind, label=f"{lab}: max and min of v")
        _s4_points(ax, d, key, f"{key}_vmin", kind)
    ax.set_xlim(*xlim)
    ax.set_ylabel("v")
    ax.set_title(r"(a) $\bar\eta$ diagram at ref_devalle: fixed point and cycle maximum and minimum of v", loc=S.TITLE_LOC)
    # (b) amplitude
    ax2 = fig.add_subplot(gs[1], sharex=ax)
    for name in ("up", "down"):
        ax2.plot(d[f"a5_{name}_param"], d[f"a5_{name}_amp"], color=cyc.colour, lw=cyc.width, zorder=3)
    _vline_hopf(ax2, d)
    _s4_points(ax2, d, "mf", "mf_v_ptp", "mf")
    _s4_points(ax2, d, "net", "net_v_ptp", "net")
    ax2.set_ylabel("v amplitude (max - min)")
    ax2.set_title("(b) amplitude: A5 cycles, S4 mean field and S4 network, stored values", loc=S.TITLE_LOC)
    # (c) stored relative difference, network against mean field
    ax3 = fig.add_subplot(gs[2], sharex=ax)
    above = d["net_above_mask"] == 1.0
    ax3.axhline(0.0, color=S.F2_MARKS["zero_line"], lw=S.F2_MARKS["zero_line_width"], zorder=1)
    _vline_hopf(ax3, d)
    _s4_points(ax3, d, "net", "cmp_rel_v_ptp", "net", mask=above)
    ax3.set_xlim(*xlim)
    v = d["cmp_rel_v_ptp"][above]
    lo, hi = min(float(v.min()), 0.0), max(float(v.max()), 0.0)
    ax3.set_ylim(lo - 0.12 * (hi - lo), hi + 0.12 * (hi - lo))
    ax3.set_ylabel("(network - MF) / MF")
    ax3.set_xlabel(r"$\bar\eta$")
    ax3.set_title(r"(c) stored relative difference of the v amplitude, drawn above $\bar\eta_H$ + 0.1 only", loc=S.TITLE_LOC)
    ax3.text(0.99, 0.97, "not drawn at and below eta_H: the mean-field amplitude there is ~0 or still\nrelaxing, so the stored relative difference is not a measure (largest |stored value|\n"
             f"below eta_H - 0.1: {d['cmp_rel_v_below_max_abs']:.2g}). Network below eta_H: no rest, v amplitude\n"
             f"{d['net_floor_v_ptp_min']:.2f} to {d['net_floor_v_ptp_max']:.2f} (panel b).", transform=ax3.transAxes, fontsize=S.TEXT_SIZES["small"], va="top", ha="right")
    # legend and strip
    axl = fig.add_subplot(gs[3])
    axl.axis("off")
    h, l = ax.get_legend_handles_labels()
    axl.legend(h, l, loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=S.TEXT_SIZES["legend"], ncol=2, frameon=False, borderaxespad=0)
    axl.text(0.0, 0.40, "FAIL rows of the stored A11 table that touch F2 through the network symbols (not recomputed; UNVERIFIED reading):",
             va="top", fontsize=S.TEXT_SIZES["status"], weight="bold")
    axl.text(0.0, 0.33, "\n".join(strip_lines) if strip_lines else "none", va="top", fontsize=S.TEXT_SIZES["status"])
    return _style_text(fig, F2_FOOTER if draft else "")


def f2_caption_notes(d: dict) -> tuple:
    """Sentences about what is and is not drawn (13f). Values come from the prepared data; only the wording is typed here."""
    turn = ", ".join(f"{p['param']:.4f}" for p in d["a5_special_points"])
    return (
        "Plotted: the voltage variable v and its maximum and minimum (panel a) and its amplitude max - min (panel b). Nothing in this figure is a frequency or a spectral peak.",
        "A5 cycles are the continuation from the Hopf point; the up and the down continuation retrace one branch, and the entry labelled fold at the turn-around next to "
        f"the Hopf point ({turn}) is that turn-around, not a fold of cycles (DL-126). The v of the Hopf marker is interpolated linearly between the stored fixed points (derived).",
        f"S4 symbols are the maximum and minimum of v over the last 1 s of each 2 s step ({d['mf_param'].size} mean-field steps, {d['net_param'].size} network steps); "
        "their difference equals the stored v amplitude of S4 to 1e-12. Steps within 0.1 of eta_H are drawn: there the 2 s step is still relaxing (DL-127), and no "
        "amplitude comparison is made.",
        "Network v is the mean V of non-refractory neurons within the cut, not the mean-field v (DL-128); the network values are single runs (one seed) and are drawn "
        "without error bars. No agreement criterion is applied to them (none is in the plan), so network symbols have one shape per sweep direction.",
        f"Panel (c) draws the stored relative differences above eta_H + 0.1; there the v amplitude differs by {100 * d['cmp_rel_v_above_min']:+.1f} to "
        f"{100 * d['cmp_rel_v_above_max']:+.1f} percent and the r amplitude by {100 * d['cmp_rel_r_above_min']:+.1f} to {100 * d['cmp_rel_r_above_max']:+.1f} percent (stored). "
        f"Below eta_H the network does not rest ({d['net_floor_steps']} steps: v amplitude {d['net_floor_v_ptp_min']:.2f} to {d['net_floor_v_ptp_max']:.2f}, r amplitude "
        f"{d['net_floor_r_ptp_min']:.3f} to {d['net_floor_r_ptp_max']:.3f}).",
        "In the params table model.eta_bar is the base value of each record; the swept parameter is s4.param. The claim-limit list was ruled in 13g; the placement of G4-C2 on F2 and the choice of the four RB1 rows for the FAIL-row list are UNVERIFIED readings of the plan.",
    )


def make_F2(res=None, out_dir=None, *, tag_build: bool = False, take_home=F2_TAKE_HOME, claim_limit_ids=F2_CLAIM_LIMITS,
            script="scripts/fig_F2.py", root=None) -> dict:
    """Build F2 from results/. Returns {'prov', 'paths', 'timing_s', 'drawn_sha256', 'caption'}. tag_build=True needs a clean tree (figprov)."""
    F.require_buildable("F2")
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "F2"
    t = {"start": time.perf_counter()}
    raw = load_F2(res)
    t["load"] = time.perf_counter()
    d = prepare_F2(raw)
    t["prepare"] = time.perf_counter()
    rows = _params_rows(raw)
    cap = CAP.build_caption("F2", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=[r for r in rows if r["key"] in F2_CAPTION_KEYS],
                            spectrogram=None, symbol_keys=(), notes=f2_caption_notes(d))
    import matplotlib.pyplot as plt
    fig = _draw_F2(d, draft=not tag_build, strip_lines=strip_lines(d))
    out.mkdir(parents=True, exist_ok=True)
    pdf, png = out / "F2.pdf", out / "F2.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=S.PNG_DPI)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    cap_path, dig_path = out / "F2_caption.txt", out / "F2_drawn_data_sha256.txt"
    from .. import provenance as P
    drawn = drawn_data_sha256(d)
    P.atomic_write_text(cap_path, cap.text + "\n")
    P.atomic_write_text(dig_path, drawn + "\n")
    warnings = []
    for k, rec in raw["records"].items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true")
    prov = F.write_figure_provenance(
        "F2", script=script, inputs=[res / p for p in F2_INPUTS], outputs=[pdf, png, cap_path, dig_path], params_rows=rows,
        modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py",
                 "src/mprsurge/plotting/nordlie.py", "src/mprsurge/plotting/figprov.py"],
        configs=["configs/S4.yaml", "configs/S4_net.yaml", "configs/A5.yaml"], claim_limits=cap.claim_limits, spectrogram=None, tag_build=tag_build,
        out_dir=out, root=root, warnings=warnings, wall_time_s=time.perf_counter() - t["start"])
    nordlie_path = out / "F2_nordlie.md"
    N.write_nordlie(out / "F2_params.csv", out / "F2_provenance.json", nordlie_path, root=root)
    t["end"] = time.perf_counter()
    timing = {"load_s": t["load"] - t["start"], "prepare_s": t["prepare"] - t["load"], "draw_s": t["draw"] - t["prepare"],
              "provenance_and_nordlie_s": t["end"] - t["draw"], "total_s": t["end"] - t["start"]}
    return {"prov": prov, "paths": [pdf, png, cap_path, dig_path, out / "F2_params.csv", out / "F2_provenance.json", nordlie_path],
            "timing_s": timing, "drawn_sha256": drawn, "caption": cap.text}


# ---- FS1 (13h) -------------------------------------------------------------------------------------------------------------------------------------
# Paths relative to results/. The registry scripts/ms13_inputs.py INPUTS["FS1"] must name the same files (the four S1 records as json plus their npz; test).
# S1 holds two copies of each run (15 Oct and 17 Oct, same arrays); the A0 table cites the 15 Oct ones (K4 2bffa787ba51, K5 ee3bd60993e0). All four are
# opened and the copies are checked equal to the cited records, so a differing copy stops the build.
FS1_INPUTS = (
    "A1/a1_fixedpoints_2d.npz",                              # M2 root count, fold formula positions, cusp, K1 to K3 (DL-086)
    "A2/a2_ring_map.npz",                                    # ring frequency, cycles per e-fold, K4 fit and linearisation (DL-089)
    "A0/a0_replication.csv",                                 # K1 to K5 table (DL-091)
    "S1/S1_0000_2bffa787ba51.json", "S1/S1_0000_2bffa787ba51.npz",        # K4 step, the record the A0 table cites
    "S1/S1_0000_c2d0a2f953a5.json", "S1/S1_0000_c2d0a2f953a5.npz",        # K4 step, later copy
    "S1/S1_0000_ee3bd60993e0.json", "S1/S1_0000_ee3bd60993e0.npz",        # K5 sinusoid, the record the A0 table cites
    "S1/S1_0000_a2f4befc74ad.json", "S1/S1_0000_a2f4befc74ad.npz",        # K5 sinusoid, later copy
    "A1/A1_0000_695d1f3d53a7.json",                          # run record: source of the A1 rows of FS1_params.csv
    "A2/A2_0000_ac3c1fb033cc.json",                          # run record: source of the A2 rows of FS1_params.csv
)
FS1_RECORDS = {"S1_K4": FS1_INPUTS[3], "S1_K5": FS1_INPUTS[7], "A1": FS1_INPUTS[11], "A2": FS1_INPUTS[12]}
FS1_CAPTION_KEYS = ("model.type", "model.J", "model.Delta", "model.eta_bar", "model.tau_ms", "path.name", "path.I_amp", "path.I_period_s", "solver.rtol")
FS1_STRIP_RB = ()            # Table 7.2 'Where' names FS1 for no RB check (UNVERIFIED reading): no A11 row touches FS1, so the A11 table is not opened
FS1_K4NET = "K4-net: not run, M2 network coupling unsourced (open item 1, T51); non-blocking (DL-113). No source was supplied (DL-119)."
FS1_K5 = "K5 (DL-064, DL-082): own reading, UNVERIFIED, deferred (unchanged; docs/ms11_close.md). The K5 trace is the stored S1 run."

# Ruled (RULED_DL, 13p R13); first proposed for the reviewer's ruling (13h prompt, item 3); every statement is from a logged result (DL numbers in the text) and the numbers are checked
# against the stored arrays by tests/test_fig_FS1.py.
FS1_TAKE_HOME = (
    "The M2 model, kept as the damped-ring comparison (DL-111), passes the replication checks K1 to K4 on the stored A1, A2 and S1 results "
    "(DL-086, DL-089, DL-091): the root-count boundary lies within one cell of the formula fold at half spacing for 20 of 20 r values (18 of 20 at base spacing; "
    "the two cusp points need half spacing), (-5, 15) has a saddle, a stable focus and a stable node, and the K4 step response rings at the linearised "
    "frequency and decay to 2.1e-4 and 6.1e-3 relative. K5 passes only on our own UNVERIFIED reading and its source check is deferred, and K4-net was not run "
    "(unsourced coupling; DL-119). No stable focus on the A1 grid is non-damped (0 of 25727; the linearised rate has standard error 0, DL-092), and the largest "
    "cycles per e-fold inside the 25 to 100 Hz band is 5.1 (DL-089)."
)
# Ruled (RULED_DL, 13p R13): MS11-C7 is the only limit in docs/ms13_plan.md section 5 that lists FS1 ('every figure'). MS12-C1 lists F1 to F6 and FS6, not FS1; no other
# limit of the table names FS1 (listed, not decided).
FS1_CLAIM_LIMITS = ("MS11-C7",)
FS1_FOOTER = draft_footer("FS1")


def load_FS1(res=None) -> dict:
    """Open the files of FS1_INPUTS under `res` (default results/) and return their content. Opens nothing else."""
    res = Path(res) if res is not None else results_dir()
    for rel in FS1_INPUTS:
        if not (res / rel).is_file():
            raise F.MissingInputError(f"input file not found: {res / rel}")
    try:
        with np.load(res / FS1_INPUTS[0], allow_pickle=False) as z:
            a1 = {k: z[k] for k in z.files}
        with np.load(res / FS1_INPUTS[1], allow_pickle=False) as z:
            a2 = {k: z[k] for k in z.files}
        with open(res / FS1_INPUTS[2], newline="", encoding="utf-8") as fh:
            a0 = list(csv.DictReader(fh))
        records = {k: json.loads((res / rel).read_text(encoding="utf-8")) for k, rel in FS1_RECORDS.items()}
        series = {}                      # [cited record's series, later copy's series]
        for key, cited, copy in (("S1_K4", FS1_INPUTS[4], FS1_INPUTS[6]), ("S1_K5", FS1_INPUTS[8], FS1_INPUTS[10])):
            series[key] = []
            for rel in (cited, copy):
                with np.load(res / rel, allow_pickle=False) as z:
                    series[key].append({k: z[k] for k in z.files})
        copies = {k: json.loads((res / rel).read_text(encoding="utf-8")) for k, rel in (("S1_K4_copy", FS1_INPUTS[5]), ("S1_K5_copy", FS1_INPUTS[9]))}
    except (OSError, ValueError, KeyError) as exc:
        raise F.MissingInputError(f"an FS1 input cannot be read: {exc}") from exc
    return {"a1": a1, "a2": a2, "a0": a0, "records": records, "series": series, "copies": copies}


def _single_slot(values, mask, name: str):
    """The value of the one slot per node where `mask` holds, NaN where none (A1/A2 keep up to three root slots per node)."""
    if int(mask.sum(axis=2).max()) > 1:
        raise DataError(f"{name}: more than one slot per node is flagged")
    return np.where(mask.any(axis=2), np.where(mask, values, 0.0).sum(axis=2), np.nan)


def prepare_FS1(raw: dict) -> dict:
    """Pure: stored content -> the arrays and numbers that are drawn. Keys are flat names; values are float arrays, ints, bools or strings."""
    a1, a2 = raw["a1"], raw["a2"]
    d: dict = {}
    if not (np.array_equal(a1["eta_over_Delta"], a2["eta_over_Delta"]) and np.array_equal(a1["J_over_sqrtDelta"], a2["J_over_sqrtDelta"])):
        raise DataError("the A1 and A2 grids differ")
    d["eta"], d["J"] = np.asarray(a1["eta_over_Delta"], dtype=float), np.asarray(a1["J_over_sqrtDelta"], dtype=float)
    d["n_roots_T"] = np.asarray(a1["n_roots"], dtype=float).T                         # (J, eta) for pcolormesh
    d["fold_J"] = np.asarray(a1["halving_fold_J"], dtype=float)
    d["fold_eta_a"], d["fold_eta_b"] = (np.asarray(a1["halving_fold_eta_formula"][:, i], dtype=float) for i in (0, 1))
    d["cusp_r"], d["cusp_eta"], d["cusp_J"] = (float(x) for x in a1["cusp_r_eta_J"])
    hv = dict(zip((str(x) for x in a1["halving_cusp_names"]), (float(x) for x in a1["halving_cusp_values"])))
    d["cusp_J_shift_cells"], d["cusp_eta_shift_cells"] = hv["J_shift_cells"], hv["eta_shift_cells"]
    d["k1_n"], d["k1_pass_base"], d["k1_pass_half"] = int(a1["k1_pass_base"].size), int(a1["k1_pass_base"].sum()), int(a1["k1_pass_half"].sum())
    d["k3_labels"] = ", ".join(str(x) for x in a1["k3_labels"])
    d["k3_pass"] = bool(a1["k3_pass"])
    # ring map: the stable-focus slot of each node; frequency everywhere, cycles per e-fold everywhere, and the band flag
    foc = a2["ring_is_focus"].astype(bool)
    d["ring_freq_T"] = _single_slot(a2["ring_freq_hz"], foc, "ring_is_focus").T
    d["ring_cyc_T"] = _single_slot(a2["ring_cycles_per_efold"], foc, "ring_is_focus").T
    d["ring_inG_T"] = _single_slot(a2["ring_in_G"].astype(float), foc, "ring_is_focus").T
    d["ring_n_focus"] = int(foc.sum())
    d["ring_n_inG"] = int((a2["ring_in_G"].astype(bool) & foc).sum())
    d["ring_n_nondamped"] = int((a2["ring_g1_nondamped"].astype(bool) & foc).sum())
    d["ring_freq_min"], d["ring_freq_max"] = float(np.nanmin(d["ring_freq_T"])), float(np.nanmax(d["ring_freq_T"]))
    inG = d["ring_inG_T"] == 1.0
    d["ring_cyc_inG_max"] = float(d["ring_cyc_T"][inG].max())
    d["ring_cyc_inG_T"] = np.where(inG, d["ring_cyc_T"], np.nan)
    d["band_hz"] = np.asarray(a2["band_primary_hz"], dtype=float)
    d["tau_ms"] = float(a2["tau_ms"])
    for k in ("omega_fit", "omega_lin", "decay_fit", "decay_lin", "rel_err_frequency", "rel_err_decay", "tol_frequency", "tol_decay", "r_star", "jump", "cycles", "rms",
              "t_start_tau", "t_end_tau"):
        d[f"k4_{k}"] = float(a2[f"k4_{k}"])
    d["k4_pass"] = bool(a2["k4_pass"])
    # S1: the cited record is drawn; its later copy must have equal arrays
    for key, rec_name in (("K4", "S1_K4"), ("K5", "S1_K5")):
        s_cited, s_copy = raw["series"][rec_name][0], raw["series"][rec_name][1]
        for k in s_cited:
            if not np.array_equal(s_cited[k], s_copy[k]):
                raise DataError(f"S1 {key}: the later copy differs from the cited record in '{k}'")
        d[f"{key}_t_ms"], d[f"{key}_r"], d[f"{key}_I"] = (np.asarray(s_cited[k], dtype=float) for k in ("t_ms", "r", "I"))
        for k in ("eta", "J", "Delta"):
            if np.ptp(s_cited[k]) != 0.0:
                raise DataError(f"S1 {key}: '{k}' is not constant")
    expect = {"S1_K4": "I_step", "S1_K5": "I_sin"}
    for rec_name, name in expect.items():
        if raw["records"][rec_name]["config"]["path"]["name"] != name:
            raise DataError(f"{rec_name}: path.name is {raw['records'][rec_name]['config']['path']['name']!r}, expected {name!r}")
    s4 = raw["series"]["S1_K4"][0]
    d["k_eta"], d["k_J"], d["k_Delta"] = float(s4["eta"][0]), float(s4["J"][0]), float(s4["Delta"][0])
    d["k4_start_r"], d["k4_end_r"] = float(s4["r"][0]), float(s4["r"][-1])
    d["k4_t_start_ms"], d["k4_t_end_ms"] = d["k4_t_start_tau"] * d["tau_ms"], d["k4_t_end_tau"] * d["tau_ms"]
    d["a0_target"] = [r["target"] for r in raw["a0"]]
    d["a0_pass"] = [r["pass"] for r in raw["a0"]]
    d["a0_measured"] = [r["measured"] for r in raw["a0"]]
    d["a0_tolerance"] = [r["tolerance"] for r in raw["a0"]]
    return d


def _draw_FS1(d: dict, draft: bool):
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import transforms
    from matplotlib.colors import ListedColormap
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    T = S.TEXT_SIZES
    fold, cusp, kpt = S.diagram_mark("m2_fold"), S.diagram_mark("m2_cusp"), S.diagram_mark("m2_k_point")
    k4t, k5t, frc = S.diagram_mark("s1_k4_trace"), S.diagram_mark("s1_k5_trace"), S.diagram_mark("s1_forcing")
    win, rst = S.diagram_mark("k4_window"), S.diagram_mark("k4_r_star")
    fig = plt.figure(figsize=(7.4, 9.0), constrained_layout=True)
    gs = fig.add_gridspec(5, 2, height_ratios=[1.5, 1.5, *S.FS_LAYOUT["fs1_k5_ratios"], 0.95])
    xl, yl = r"$\bar\eta/\Delta$", r"$J/\sqrt{\Delta}$"
    eta, J = d["eta"], d["J"]
    ext = dict(shading="nearest", rasterized=True)

    def mark_k(ax):
        ax.plot([d["k_eta"] / d["k_Delta"]], [d["k_J"] / np.sqrt(d["k_Delta"])], ls="none", marker=kpt.marker, ms=kpt.size, color=kpt.colour, mew=kpt.width, zorder=6,
                label=f"K3 to K5 point ({d['k_eta'] / d['k_Delta']:g}, {d['k_J'] / np.sqrt(d['k_Delta']):g})")

    # (a) root count with the formula fold positions and the cusp
    ax = fig.add_subplot(gs[0, 0])
    cm = ListedColormap([S.ROOT_COUNT_COLOURS[1], S.ROOT_COUNT_COLOURS[3]])
    ax.pcolormesh(eta, J, d["n_roots_T"], cmap=cm, vmin=1, vmax=3, **ext)
    for col, lab in (("fold_eta_a", "fold formula (A1), two branches"), ("fold_eta_b", None)):
        ax.plot(d[col], d["fold_J"], color=fold.colour, lw=fold.width, ls=fold.linestyle, label=lab, zorder=3)
    ax.plot([d["cusp_eta"]], [d["cusp_J"]], ls="none", marker=cusp.marker, ms=cusp.size, color=cusp.colour, mew=cusp.width, zorder=5,
            label=f"cusp, formula ({d['cusp_eta']:.3f}, {d['cusp_J']:.3f})")
    mark_k(ax)
    from matplotlib.patches import Patch
    h, l = ax.get_legend_handles_labels()
    h = [Patch(fc=S.ROOT_COUNT_COLOURS[1], ec=S.FS_COLOURS["patch_edge"], lw=0.5), Patch(fc=S.ROOT_COUNT_COLOURS[3], ec=S.FS_COLOURS["patch_edge"], lw=0.5)] + h
    l = ["1 root (A1 grid node)", "3 roots (A1 grid node)"] + l
    ax.legend(h, l, loc="lower left", fontsize=T["legend"], frameon=True, framealpha=0.95, borderaxespad=0.3)
    ax.set_xlim(eta.min(), eta.max())
    ax.set_ylim(J.min(), J.max())
    ax.set_xlabel(xl)
    ax.set_ylabel(yl)
    ax.set_title("(a) M2 fixed points: number of roots (A1, base grid)", loc=S.TITLE_LOC)
    # (b) ring frequency of the stable focus
    axb = fig.add_subplot(gs[0, 1], sharex=ax, sharey=ax)
    m = axb.pcolormesh(eta, J, d["ring_freq_T"], cmap=S.FREQUENCY_CMAP, **ext)
    axb.set_facecolor(S.FS_COLOURS["no_data"])
    mark_k(axb)
    fig.colorbar(m, ax=axb, pad=0.02, fraction=0.06).set_label("ring frequency (Hz, tau = %g ms)" % d["tau_ms"])
    axb.set_xlabel(xl)
    axb.set_title("(b) A2 ring map: frequency of the stable focus", loc=S.TITLE_LOC)
    # (c) cycles per e-fold in the band
    axc = fig.add_subplot(gs[1, 0], sharex=ax, sharey=ax)
    axc.set_facecolor(S.FS_COLOURS["no_data"])
    mc = axc.pcolormesh(eta, J, d["ring_cyc_inG_T"], cmap=S.CYCLES_CMAP, **ext)
    mark_k(axc)
    fig.colorbar(mc, ax=axc, pad=0.02, fraction=0.06).set_label("cycles per e-fold")
    axc.set_xlabel(xl)
    axc.text(0.0, -0.27, "grey: stable focus outside the band, or no focus." + "\n" + f"{d['ring_n_nondamped']} of {d['ring_n_focus']} foci are non-damped.",
             transform=axc.transAxes, fontsize=T["note"], va="top", ha="left")
    axc.set_ylabel(yl)
    axc.set_title("(c) A2 ring map: cycles per e-fold, 25 to 100 Hz band", loc=S.TITLE_LOC)
    # (d) K4 step response; 13p (R14): the number block is centred between the two fit-window lines, in a box
    axd = fig.add_subplot(gs[1, 1])
    axd.plot(d["K4_t_ms"], d["K4_r"], color=k4t.colour, lw=k4t.width, ls=k4t.linestyle, label="S1 K4 r(t), stored", zorder=3)
    axd.axhline(d["k4_r_star"], color=rst.colour, lw=rst.width, ls=rst.linestyle, label=f"focus r* = {d['k4_r_star']:.4f} (A2)", zorder=2)
    for x, lab in ((d["k4_t_start_ms"], "fit window start"), (d["k4_t_end_ms"], "fit window end")):
        axd.axvline(x, color=win.colour, lw=win.width, ls=win.linestyle, label=f"{lab} {x:g} ms", zorder=1)
    axd.set_xlim(0.0, 600.0)
    axd.set_xlabel("t (ms)")
    axd.set_ylabel("r")
    axd.set_title("(d) K4: step I = 0 to 3 at (-5, 15); axis cut at 600 ms", loc=S.TITLE_LOC)
    axd.legend(loc="upper right", bbox_to_anchor=(0.66, 1.0), fontsize=T["legend"], frameon=True, framealpha=0.95)      # between the two window lines
    tr = transforms.blended_transform_factory(axd.transData, axd.transAxes)
    axd.text(0.5 * (d["k4_t_start_ms"] + d["k4_t_end_ms"]), 0.40,
             f"fit: omega {d['k4_omega_fit']:.4f}\n     decay {d['k4_decay_fit']:.5f} per tau\nlinearised: omega {d['k4_omega_lin']:.4f}\n     decay {d['k4_decay_lin']:.5f}\n"
             f"rel. err. {d['k4_rel_err_frequency']:.2g} (freq.)\n     {d['k4_rel_err_decay']:.2g} (decay)\ntolerance {d['k4_tol_frequency']:g}; {'pass' if d['k4_pass'] else 'FAIL'}\n"
             f"{d['k4_cycles']:.1f} tail cycles", transform=tr, fontsize=T["small"], va="top", ha="center", multialignment="left", zorder=5,
             bbox=dict(boxstyle="square,pad=0.3", fc=S.FS_COLOURS["box_face"], ec=S.FS_COLOURS["patch_edge"], lw=0.4)).set_gid("k4_numbers")
    # (e) K5 sinusoid: r(t) above, the forcing I(t) in its own panel below on the same time axis (13p, R14)
    axe = fig.add_subplot(gs[2, :])
    axe.plot(d["K5_t_ms"], d["K5_r"], color=k5t.colour, lw=k5t.width, ls=k5t.linestyle, label="S1 K5: r(t), stored series", zorder=3)
    axe.set_xlim(d["K5_t_ms"].min(), d["K5_t_ms"].max())
    axe.set_ylabel("r")
    axe.set_ylim(0.0, 4.8)                       # headroom: the legend sits above the r peaks
    axe.tick_params(labelbottom=False)
    axe.set_title("(e) K5 sinusoidal forcing: own reading, UNVERIFIED, source check deferred (DL-064, DL-082)", loc=S.TITLE_LOC)
    axe2 = fig.add_subplot(gs[3, :], sharex=axe)
    axe2.plot(d["K5_t_ms"], d["K5_I"], color=frc.colour, lw=frc.width, ls=frc.linestyle, label="forcing I(t), stored", zorder=1)
    axe2.set_ylabel("forcing I", color=frc.colour)
    axe2.tick_params(axis="y", colors=frc.colour)
    axe2.spines["left"].set_color(frc.colour)
    axe2.set_ylim(-3.9, 3.9)
    axe2.set_xlabel("t (ms)")
    h1, l1 = axe.get_legend_handles_labels()
    h2, l2 = axe2.get_legend_handles_labels()
    axe.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=T["legend"], frameon=True, framealpha=0.95, ncol=2)
    # (f) A0 table and status lines
    axf = fig.add_subplot(gs[4, :])
    axf.axis("off")
    lines = ["(f) Stored A0 replication table (K1 to K5; every row passes on definitions marked UNVERIFIED in the table):"]
    for t, p, mm, tol in zip(d["a0_target"], d["a0_pass"], d["a0_measured"], d["a0_tolerance"]):
        lines += textwrap.wrap(f"{t}: {p}. {mm}. Criterion: {tol}.", width=150, subsequent_indent="    ")
    lines += ["", FS1_K5, FS1_K4NET, "FAIL rows of the stored A11 table that touch FS1: none (Table 7.2 names no RB check for FS1; UNVERIFIED reading)."]
    axf.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=T["status"], linespacing=1.25)
    return _style_text(fig, FS1_FOOTER if draft else "")


def fs1_caption_notes(d: dict) -> tuple:
    """Sentences about what is and is not drawn (13h). Values come from the prepared data; only the wording is typed here."""
    return (
        "Panel (a) shows the stored A1 root count on the base grid (241 by 201 nodes, one cell per node) and the stored positions of the fold formula and the cusp; the "
        f"refined half-spacing lattice is not drawn. At the cusp the half-spacing result moves by {d['cusp_J_shift_cells']:.1f} J cells and {abs(d['cusp_eta_shift_cells']):.1f} eta "
        "cells against the base grid (stored; DL-086 records this, it does not claim it met). Axes are eta_bar/Delta and J/sqrt(Delta); the K points are at Delta = 1.",
        f"Panels (b) and (c) show the A2 ring map: the frequency (Hz) and the cycles per e-fold of the stable focus at each node ({d['ring_n_focus']} nodes; {d['ring_n_inG']} with the ring "
        f"frequency in the 25 to 100 Hz band). The ring rate is the linearised rate with standard error 0, not a fit to simulated rings, so every focus is damped by construction "
        f"(DL-089, DL-092). Panel (c) is drawn only where the ring frequency lies in the band; its largest value is {d['ring_cyc_inG_max']:.2f}.",
        f"Panel (d) is the stored S1 K4 run (DOP853, 1 ms output, start in the low state r = {d['k4_start_r']:.4f}); the x axis is cut at 600 ms and the run goes on to "
        f"{d['K4_t_ms'].max():g} ms, ending at r = {d['k4_end_r']:.4f}. The fit window is {d['k4_t_start_tau']:g} to {d['k4_t_end_tau']:g} tau (tau = {d['tau_ms']:g} ms, UNVERIFIED mapping, DL-082); the fit and linearisation numbers are the stored A2 values.",
        "Panel (e) is the stored S1 K5 run; its burst definition, tolerance and time mapping are our own readings (UNVERIFIED, DL-082), and the check against the primary source is deferred. No crossing is drawn.",
        "K4-net was not run and has no panel (the M2 network coupling is unsourced; DL-119). The S1 records exist as two copies (15 and 17 Oct) with equal arrays; the copy cited by the A0 table is drawn.",
        "M2 is the comparison model (DL-111): nothing here is a result for M3.",
    )


def make_FS1(res=None, out_dir=None, *, tag_build: bool = False, take_home=FS1_TAKE_HOME, claim_limit_ids=FS1_CLAIM_LIMITS,
             script="scripts/fig_FS1.py", root=None) -> dict:
    """Build FS1 from results/. Returns {'prov', 'paths', 'timing_s', 'drawn_sha256', 'caption'}. tag_build=True needs a clean tree (figprov)."""
    F.require_buildable("FS1")
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "FS1"
    t = {"start": time.perf_counter()}
    raw = load_FS1(res)
    t["load"] = time.perf_counter()
    d = prepare_FS1(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for panel, key in (("a-c", "A1"), ("a-c", "A2"), ("d", "S1_K4"), ("e", "S1_K5")):
        rec = raw["records"][key]
        for r in make_param_table(rec["config"]):
            rows.append({**r, "panel": panel, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    cap = CAP.build_caption("FS1", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=[r for r in rows if r["key"] in FS1_CAPTION_KEYS],
                            spectrogram=None, symbol_keys=(), notes=fs1_caption_notes(d))
    import matplotlib.pyplot as plt
    fig = _draw_FS1(d, draft=not tag_build)
    out.mkdir(parents=True, exist_ok=True)
    pdf, png = out / "FS1.pdf", out / "FS1.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=S.PNG_DPI)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    cap_path, dig_path = out / "FS1_caption.txt", out / "FS1_drawn_data_sha256.txt"
    from .. import provenance as P
    drawn = drawn_data_sha256(d)
    P.atomic_write_text(cap_path, cap.text + "\n")
    P.atomic_write_text(dig_path, drawn + "\n")
    warnings = []
    for k, rec in {**raw["records"], **raw["copies"]}.items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true")
    prov = F.write_figure_provenance(
        "FS1", script=script, inputs=[res / p for p in FS1_INPUTS], outputs=[pdf, png, cap_path, dig_path], params_rows=rows,
        modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py",
                 "src/mprsurge/plotting/nordlie.py", "src/mprsurge/plotting/figprov.py"],
        configs=["configs/A1.yaml", "configs/A2.yaml", "configs/S1.yaml"], claim_limits=cap.claim_limits, spectrogram=None, tag_build=tag_build,
        out_dir=out, root=root, warnings=warnings, wall_time_s=time.perf_counter() - t["start"])
    nordlie_path = out / "FS1_nordlie.md"
    N.write_nordlie(out / "FS1_params.csv", out / "FS1_provenance.json", nordlie_path, root=root)
    t["end"] = time.perf_counter()
    timing = {"load_s": t["load"] - t["start"], "prepare_s": t["prepare"] - t["load"], "draw_s": t["draw"] - t["prepare"],
              "provenance_and_nordlie_s": t["end"] - t["draw"], "total_s": t["end"] - t["start"]}
    return {"prov": prov, "paths": [pdf, png, cap_path, dig_path, out / "FS1_params.csv", out / "FS1_provenance.json", nordlie_path],
            "timing_s": timing, "drawn_sha256": drawn, "caption": cap.text}


# ---- FS2 (13h) -------------------------------------------------------------------------------------------------------------------------------------
# Paths relative to results/. The registry scripts/ms13_inputs.py INPUTS["FS2"] must name the same files (the S3 records as json plus their npz; test).
_S3_MF = {("ceni", "3.0"): "ceni_0000_0de955d7d683", ("ceni", "4.95"): "ceni_0001_52277c9529ac", ("ceni", "8.0"): "ceni_0002_032f8992d047",
          ("devalle", "5.0"): "devalle_0000_9e49def91dfc", ("devalle", "50.0"): "devalle_0001_9a3f46a18b44"}
_S3_NET = {"ceni_3ms": "net_ceni/net_ceni_0000_3f4561d07a32", "ceni_4.95ms": "net_ceni/net_ceni_0001_1d7353d4b3fc", "ceni_8ms": "net_ceni/net_ceni_0002_73624487461f",
           "devalle_5ms": "net_devalle/net_devalle_0000_82a8c8cca980", "devalle_50ms": "net_devalle/net_devalle_0001_0bdf9ad62b84", "k8_5e4_5ms": "net_k8/net_k8_0000_6d90ef8de3c5"}
FS2_INPUTS = (
    "A4/a4_hopf_curves.npz",                                 # ceni Hopf tau_d, K9, K10 and K11 arrays (DL-115)
    "A5/a5_cycles.npz",                                      # ceni cycle branch (DL-126)
    "A6/a6_freq_map.npz",                                    # ref_devalle slice, checked against the stored A6 summary (DL-131)
    "A6/a6_summary.json",                                     # K10 J dependence and the ref_devalle cycle frequency (DL-131)
    "S3/s3_mf_summary.json",                                 # S3 mean-field readouts (DL-116)
    "S3/s3_net_summary.json",                                # S3 network readouts and network-against-mean-field differences (DL-119)
    "A5/check/a5_check.json",                                # stored K7 amplitude fits and hysteresis (DL-129, DL-130)
    "A4/A4_0000_4ece63ed731f.json", "A5/A5_0000_506cf5745380.json", "A6/A6_0000_daa85487fd0a.json",       # run records: source of the FS2 parameter rows
) + tuple(f"S3/{('ceni' if k[0] == 'ceni' else 'devalle')}/{v}.{ext}" for k, v in _S3_MF.items() for ext in ("json", "npz")) \
  + tuple(f"S3/{v}.{ext}" for v in _S3_NET.values() for ext in ("json", "npz"))
FS2_FILES = {"a4": FS2_INPUTS[0], "a5": FS2_INPUTS[1], "a6npz": FS2_INPUTS[2], "a6": FS2_INPUTS[3], "s3mf": FS2_INPUTS[4], "s3net": FS2_INPUTS[5], "a5check": FS2_INPUTS[6]}
FS2_RECORDS = {"A4": FS2_INPUTS[7], "A5": FS2_INPUTS[8], "A6": FS2_INPUTS[9],
               "S3_mf_ceni": f"S3/ceni/{_S3_MF[('ceni', '8.0')]}.json", "S3_mf_devalle": f"S3/devalle/{_S3_MF[('devalle', '5.0')]}.json",
               "S3_net_ceni": f"S3/{_S3_NET['ceni_8ms']}.json", "S3_net_devalle": f"S3/{_S3_NET['devalle_5ms']}.json", "S3_net_k8": f"S3/{_S3_NET['k8_5e4_5ms']}.json"}
FS2_CAPTION_KEYS = ("model.type", "model.ref_point", "model.tau_ms", "model.J", "model.Delta", "model.eta_bar", "network.N", "durations.hold_s")
FS2_TRACE_MS = 400.0         # the traces show the last 400 ms of each stored 10 s series (axis choice; the series are stored in full)
FS2_K9 = (0.1453, 0.002)     # plan Table 7.1 K9: the largest Delta/eta_bar is 0.1453 +- 0.002
FS2_K11 = 0.01               # plan Table 7.1 K11: Im lambda / (2 pi r*) = 1 +- 0.01
FS2_K8_TOL = 0.05            # plan Table 7.1 K8: network peak within 5 percent
FS2_K7_PAPER_MS = 4.95       # the paper's value (plan Table 7.1 K7); the S3 cell at 4.95 ms is the stored run at that value

# Ruled (RULED_DL, 13p R13); first proposed for the reviewer's ruling (13h prompt, item 3); every statement is from a logged result (DL numbers in the text) and the numbers are checked
# against the stored arrays by tests/test_fig_FS2.py. FS2 reports K7, K9, K10 and K11 as they stand, failures included.
FS2_TAKE_HOME = (
    "The M3 mean field reproduces the K8 existence checks (limit cycle at tau_d 5 ms, fixed point at 50 ms; the N = 5e4 network peak is within 0.09 "
    "percent of the mean field, tolerance 5 percent; DL-116, DL-119), K9 (largest Delta/eta_bar 0.14531 at eta_bar 1, 2 and 4; DL-115) and K11 (largest deviation from 1 "
    "7.1e-4; DL-115). It does not reproduce K7 as stated: the Hopf point is at tau_d 4.12 ms, not 4.95 ms (a recorded departure, DL-074, DL-076, DL-079), and the "
    "amplitude-squared line misses its residual rule (2.42 against 2 percent; a REPORTED FAILURE, DL-129, DL-130). K10 is not reproduced as worded: the J dependence of the "
    "frequency is 13.4, 25.0 and 42.2 percent at 8, 20 and 40 ms against the 10 percent limit (DL-131, DL-132; single source, UNVERIFIED)."
)
# Ruled (RULED_DL, 13p R13): MS11-C7 is the only limit in docs/ms13_plan.md section 5 that lists FS2 ('every figure'); no other limit of the table names FS2 (listed, not decided).
FS2_CLAIM_LIMITS = ("MS11-C7",)
FS2_FOOTER = draft_footer("FS2")


def load_FS2(res=None) -> dict:
    """Open the files of FS2_INPUTS under `res` (default results/) and return their content. Opens nothing else."""
    res = Path(res) if res is not None else results_dir()
    for rel in FS2_INPUTS:
        if not (res / rel).is_file():
            raise F.MissingInputError(f"input file not found: {res / rel}")
    try:
        def npz(rel, keys=None):
            with np.load(res / rel, allow_pickle=False) as z:
                return {k: z[k] for k in (keys or z.files)}
        def js(rel):
            return json.loads((res / rel).read_text(encoding="utf-8"))
        out = {"a4": npz(FS2_FILES["a4"]), "a5": npz(FS2_FILES["a5"]), "a6npz": npz(FS2_FILES["a6npz"], ("slice_ids", "po_slice_index", "po_param", "po_frequency_hz")),
               "a6": js(FS2_FILES["a6"]), "s3mf": js(FS2_FILES["s3mf"]), "s3net": js(FS2_FILES["s3net"]), "a5check": js(FS2_FILES["a5check"]),
               "records": {k: js(rel) for k, rel in FS2_RECORDS.items()}, "mf": {}, "net": {}}
        for (ref, tau), stem in _S3_MF.items():
            out["mf"][(ref, tau)] = {"series": npz(f"S3/{ref}/{stem}.npz", ("t_ms", "r", "v")), "record": js(f"S3/{ref}/{stem}.json")}
        for key, stem in _S3_NET.items():
            out["net"][key] = {"series": npz(f"S3/{stem}.npz", ("t_ms", "r", "v")), "record": js(f"S3/{stem}.json")}
    except (OSError, ValueError, KeyError) as exc:
        raise F.MissingInputError(f"an FS2 input cannot be read: {exc}") from exc
    return out


def prepare_FS2(raw: dict) -> dict:
    """Pure: stored content -> the arrays and numbers that are drawn. Keys are flat names; values are float arrays, ints, bools or strings."""
    a4, a5, a6, s3m, s3n, chk = raw["a4"], raw["a5"], raw["a6"], raw["s3mf"], raw["s3net"], raw["a5check"]
    d: dict = {}
    # K7: A5 ceni cycle branch and Hopf points
    if not bool(a5["ceni_stable"].all()):
        raise DataError("an unstable cycle point in the A5 ceni branch: the draft draws stable cycles only")
    up = a5["ceni_direction_up"].astype(bool)
    for name, m in (("up", up), ("down", ~up)):
        d[f"a5c_{name}_tau_d"] = np.asarray(a5["ceni_tau_d_ms"][m], dtype=float)
        d[f"a5c_{name}_amp"] = np.asarray(a5["ceni_amplitude_v"][m], dtype=float)
    d["hopf_a4_ms"], d["hopf_a5_ms"] = float(a4["ceni_hopf_tau_d_ms"][0]), float(a5["ceni_hopf_tau_d_ms"][0])
    d["hopf_check_ms"] = float(chk["k7_amplitude"]["hopf_ms"])
    # S3 mean-field values
    cells_mf = s3m["cells"]
    d["k7_tau"] = np.array([3.0, 4.95, 8.0])
    d["k7_mf_vptp"] = np.array([float(cells_mf["K7"][k]["v_ptp_mean"]) for k in ("3.0", "4.95", "8.0")])
    d["k7_mf_hold_dev"] = np.array([float(cells_mf["K7"][k]["hold_dev"]) for k in ("3.0", "4.95", "8.0")])
    d["k7_mf_decays"] = np.array([float(bool(cells_mf["K7"][k]["decays"])) for k in ("3.0", "4.95", "8.0")])
    d["k8_tau"] = np.array([5.0, 50.0])
    d["k8_mf_vptp"] = np.array([float(cells_mf["K8"][k]["v_ptp_mean"]) for k in ("5.0", "50.0")])
    d["k8_mf_decays"] = np.array([float(bool(cells_mf["K8"][k]["decays"])) for k in ("5.0", "50.0")])
    d["k8_mf_f_fft"] = float(cells_mf["K8"]["5.0"]["f_fft_hz"])
    d["k7_summary_pass"], d["k8_summary_pass"] = bool(s3m["K7"]["pass"]), bool(s3m["K8"]["pass"])
    # K7 amplitude half: stored fits
    k7 = chk["k7_amplitude"]
    d["fit_hopf_ms"] = float(k7["hopf_ms"])
    d["fit_window_ms"] = np.asarray(k7["window_ms"], dtype=float)
    for name in ("s4_up", "posthoc_near_hopf"):
        for k in ("slope", "intercept", "r2", "max_resid_frac", "n_points"):
            d[f"fit_{name}_{k}"] = float(k7[name][k])
        d[f"fit_{name}_resid_pass"] = bool(k7[name]["resid_pass"])
    d["fit_posthoc_window_ms"] = np.asarray(k7["posthoc_near_hopf"]["window_ms"], dtype=float)
    d["fit_hysteresis_max_rel_diff"] = float(k7["hysteresis"]["max_rel_diff"])
    d["fit_rel_tol"] = float(chk["rel_tol"]) if np.isscalar(chk["rel_tol"]) else float("nan")
    # network cells in the stored order, differences as stored
    names = list(s3n["cells"])
    d["net_cells"] = names
    for q in ("f_rel_diff", "r_mean_rel_diff", "r_fit_ptp_rel_diff"):
        d[f"net_{q}"] = np.array([np.nan if s3n["cells"][n]["diff"][q] is None else float(s3n["cells"][n]["diff"][q]) for n in names])
    d["net_f_net_hz"] = np.array([np.nan if s3n["cells"][n]["diff"]["f_net_hz"] is None else float(s3n["cells"][n]["diff"]["f_net_hz"]) for n in names])
    d["net_f_mf_hz"] = np.array([np.nan if s3n["cells"][n]["diff"]["f_mf_hz"] is None else float(s3n["cells"][n]["diff"]["f_mf_hz"]) for n in names])
    d["net_N"] = np.array([float(s3n["cells"][n]["N"]) for n in names])
    d["k8_net_rel_diff"], d["k8_net_tol"], d["k8_net_pass"] = float(s3n["K8"]["rel_diff"]), float(s3n["K8"]["tol"]), bool(s3n["K8"]["pass"])
    if d["k8_net_tol"] != FS2_K8_TOL:
        raise DataError(f"the stored K8 network tolerance {d['k8_net_tol']!r} is not the plan's {FS2_K8_TOL!r}")
    # A6: the ref_devalle cycle frequency at eta_bar 4 is the stored summary value; the stored slice reproduces it
    ids = [str(x) for x in raw["a6npz"]["slice_ids"]]
    m = raw["a6npz"]["po_slice_index"] == ids.index("eta_tau_D0.3_td5.0")
    d["k8_a6_f_eta4"] = float(a6["devalle"]["f_at_eta_4"])
    if float(np.interp(4.0, raw["a6npz"]["po_param"][m], raw["a6npz"]["po_frequency_hz"][m])) != d["k8_a6_f_eta4"]:
        raise DataError("the A6 slice does not reproduce the stored A6 summary frequency at eta_bar 4")
    # traces: the last FS2_TRACE_MS of each stored series
    for key, src in [(f"mf_{ref}_{tau}", raw["mf"][(ref, tau)]) for (ref, tau) in _S3_MF] + [(f"net_{k}", raw["net"][k]) for k in _S3_NET]:
        t, r = np.asarray(src["series"]["t_ms"], dtype=float), np.asarray(src["series"]["r"], dtype=float)
        sel = t >= t[-1] - FS2_TRACE_MS - 1e-9
        d[f"tr_{key}_t"], d[f"tr_{key}_r"] = t[sel], r[sel]
    for (ref, tau), src in raw["mf"].items():
        if abs(float(src["record"]["config"]["model"]["tau_d_ms"]) - float(tau)) > 0:
            raise DataError(f"S3 mean-field record {ref} {tau}: model.tau_d_ms differs")
    # K9, K10, K11
    for k in ("eta_bar", "ratio", "tau_d_ms", "J"):
        d[f"k9_{k}"] = np.asarray(a4[f"k9_{k}"], dtype=float)
    d["k9_on_edge"] = int(a4["k9_on_edge"].sum())
    d["k10_tau_d"], d["k10_freq"] = np.asarray(a4["k10_tau_d_ms"], dtype=float), np.asarray(a4["k10_freq_hz"], dtype=float)
    k10 = a6["k10"]
    d["k10_band_hz"], d["k10_band_slack"], d["k10_j_limit"] = np.asarray(k10["band_hz"], dtype=float), float(k10["band_slack"]), float(k10["J_limit"])
    d["k10_pass_all"] = bool(k10["pass_all"])
    for tau in ("8.0", "20.0", "40.0"):
        jd = k10["J_dependence"][tau]
        d[f"k10_J_{tau}"] = np.asarray(jd["J"], dtype=float)
        d[f"k10_lin_{tau}"] = np.asarray(jd["linear_freq_hz"], dtype=float)
        d[f"k10_unstable_{tau}"] = np.asarray(jd["linear_is_unstable"], dtype=bool).astype(float)
        d[f"k10_rel_change_{tau}"] = float(jd["linear_all"]["rel_change"])
        d[f"k10_cycle_f_{tau}"] = np.array([np.nan if x is None else float(x) for x in jd["cycle_freq_hz"]])
    d["k11_ratio"], d["k11_J_H"], d["k11_eta_bar"] = (np.asarray(a4[k], dtype=float) for k in ("k11_ratio", "k11_J_H", "k11_eta_bar"))
    d["k11_max_dev"] = float(np.max(np.abs(d["k11_ratio"] - 1.0)))
    return d


def _fs2_trace(ax, d: dict, series: list, title: str):
    for key, mark in series:
        st = S.diagram_mark(mark)
        ax.plot(d[f"tr_{key}_t"], d[f"tr_{key}_r"], color=st.colour, lw=st.width, ls=st.linestyle, zorder=3 if mark == "s3_mf" else 2)
    ax.set_title(title, loc=S.TITLE_LOC)


def coincident_marks(ax, line, size_pt: float) -> int:
    """13p (DL-500 R15): how many marks of `line` lie, in the drawn panel, closer than one mark size (points) to another mark of the same line. A display fact of the
    current layout, not a property of the stored values (the rule is ours, UNVERIFIED). Call after the figure has been drawn."""
    fig = ax.figure
    xy = ax.transData.transform(np.column_stack([line.get_xdata(), line.get_ydata()])) * 72.0 / fig.dpi
    near = np.zeros(len(xy), dtype=bool)
    for i in range(len(xy)):
        dist = np.hypot(*(xy - xy[i]).T)
        dist[i] = np.inf
        near[i] = bool((dist < size_pt).any())
    return int(near.sum())


def _draw_FS2(d: dict, draft: bool):
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    T = S.TEXT_SIZES
    cyc, hp = S.diagram_mark("a5_cycle"), S.diagram_mark("hopf_point")
    mf, n1, n5 = S.diagram_mark("s3_mf"), S.diagram_mark("s3_net_1e4"), S.diagram_mark("s3_net_5e4")
    paper, tol = S.diagram_mark("k7_paper"), S.diagram_mark("tol_band")
    fig = plt.figure(figsize=(7.4, 11.2), constrained_layout=True)
    gs = fig.add_gridspec(5, 6, height_ratios=[1.35, 0.95, 1.25, 1.25, 0.95])
    # (a) K7: v amplitude of the A5 ceni branch and the S3 mean-field runs
    ax = fig.add_subplot(gs[0, 0:3])
    for name in ("up", "down"):
        ax.plot(d[f"a5c_{name}_tau_d"], d[f"a5c_{name}_amp"], color=cyc.colour, lw=cyc.width, zorder=3, label="A5 stable cycle, v amplitude" if name == "up" else None)
    ax.axvline(d["hopf_a4_ms"], color=hp.colour, ls=hp.linestyle, lw=hp.width, label=f"Hopf, A4: {d['hopf_a4_ms']:.4f} ms", zorder=1)
    ax.axvline(FS2_K7_PAPER_MS, color=paper.colour, ls=paper.linestyle, lw=paper.width, label=f"paper value {FS2_K7_PAPER_MS:g} ms (not reproduced)", zorder=1)
    ax.plot(d["k7_tau"], d["k7_mf_vptp"], ls="none", marker=mf.marker, ms=mf.size, color=mf.colour, zorder=5, label="S3 mean field, v peak-to-peak (3, 4.95, 8 ms)")
    ax.set_xlabel(r"$\tau_d$ (ms)")
    ax.set_ylabel("v amplitude")
    ax.set_xlim(2.5, 10.5)
    ax.set_title("(a) K7: ref_ceni amplitude of v against tau_d", loc=S.TITLE_LOC)
    ax.legend(loc="lower right", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # (b) K7 amplitude half: A^2 against tau_d with the stored fits
    axb = fig.add_subplot(gs[0, 3:6])
    for name in ("up", "down"):
        axb.plot(d[f"a5c_{name}_tau_d"], d[f"a5c_{name}_amp"] ** 2, color=cyc.colour, lw=cyc.width, zorder=3, label="A5 cycle, amplitude squared" if name == "up" else None)
    h = d["fit_hopf_ms"]
    w = d["fit_window_ms"]
    x = np.array([h + w[0], h + w[1]])
    axb.plot(x, d["fit_s4_up_slope"] * (x - h) + d["fit_s4_up_intercept"], color=paper.colour, lw=1.6, ls="-", zorder=4,
             label=f"stored fit, S4 up, window {w[0]:g} to {w[1]:g} ms\nabove Hopf: R2 {d['fit_s4_up_r2']:.5f}, residual {100 * d['fit_s4_up_max_resid_frac']:.2f} percent")
    pw = d["fit_posthoc_window_ms"]
    xp = np.array([h + pw[0], h + pw[1]])
    axb.plot(xp, d["fit_posthoc_near_hopf_slope"] * (xp - h) + d["fit_posthoc_near_hopf_intercept"], color=tol.colour, lw=1.6, ls="-", zorder=4,
             label=f"POST HOC fit (exploratory), window {pw[0]:g} to {pw[1]:g} ms\nabove Hopf: residual {100 * d['fit_posthoc_near_hopf_max_resid_frac']:.2f} percent")
    axb.axvline(h, color=hp.colour, ls=hp.linestyle, lw=hp.width, zorder=1)
    axb.set_xlim(h - 0.1, 6.0)
    axb.set_ylim(0.0, 11.0)                         # headroom: the legend sits right of the Hopf line and above the A5 branch (its largest value in the window is 6.8)
    axb.set_xlabel(r"$\tau_d$ (ms); axis cut at 6 ms, the A5 branch runs to 10 ms")
    axb.set_ylabel("v amplitude squared")
    axb.set_title("(b) K7 amplitude half: REPORTED FAILURE (residual)", loc=S.TITLE_LOC)
    axb.legend(loc="upper right", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # (c) traces
    sub = gs[1, :].subgridspec(2, 5, wspace=0.28, height_ratios=[0.16, 1.0])
    axl = fig.add_subplot(sub[0, :])                    # key of the line colours of (c) to (g)
    axl.axis("off")
    from matplotlib.lines import Line2D
    axl.legend([Line2D([], [], color=m.colour, lw=m.width) for m in (mf, n1, n5)],
               ["mean field", "network N = 1e4 (all panels)", "network N = 5e4 (devalle 5 ms only)"], loc="center", ncol=3, fontsize=T["legend"], frameon=False)
    specs = [("ceni 3 ms", [("mf_ceni_3.0", "s3_mf"), ("net_ceni_3ms", "s3_net_1e4")]), ("ceni 4.95 ms", [("mf_ceni_4.95", "s3_mf"), ("net_ceni_4.95ms", "s3_net_1e4")]),
             ("ceni 8 ms", [("mf_ceni_8.0", "s3_mf"), ("net_ceni_8ms", "s3_net_1e4")]),
             ("devalle 5 ms", [("mf_devalle_5.0", "s3_mf"), ("net_devalle_5ms", "s3_net_1e4"), ("net_k8_5e4_5ms", "s3_net_5e4")]),
             ("devalle 50 ms", [("mf_devalle_50.0", "s3_mf"), ("net_devalle_50ms", "s3_net_1e4")])]
    for i, (title, series) in enumerate(specs):
        axt = fig.add_subplot(sub[1, i])
        _fs2_trace(axt, d, series, f"({'cdefg'[i]}) {title}")
        axt.set_xlabel("t (ms)")
        if i == 0:
            axt.set_ylabel("r (1/tau), last 400 ms")
    # (h) frequency and differences, network against mean field (stored)
    axd = fig.add_subplot(gs[2, 0:2])
    names = d["net_cells"]
    xs = np.arange(len(names), dtype=float)
    for q, glyph, lab in (("f_rel_diff", "d_freq", "peak frequency"), ("r_mean_rel_diff", "d_mean", "r mean"), ("r_fit_ptp_rel_diff", "d_ptp", "fitted r amplitude")):
        axd.plot(xs, 100 * d[f"net_{q}"], ls="none", marker=S.FS2_DIFF_MARKS[glyph], ms=S.FS_SIZES["fs2_diff"], color=S.FS_COLOURS["mark_dark"], label=lab, zorder=4)
    axd.axhline(100 * FS2_K8_TOL, color=tol.colour, ls=tol.linestyle, lw=tol.width, label="K8 tolerance, 5 percent (frequency)")
    axd.axhline(-100 * FS2_K8_TOL, color=tol.colour, ls=tol.linestyle, lw=tol.width)
    axd.axhline(0.0, color=S.FS_COLOURS["patch_edge"], lw=0.5, zorder=1)
    axd.set_xticks(xs)
    axd.set_xticklabels([n.replace("_", " ").replace("k8 5e4 5ms", "devalle 5ms N 5e4") for n in names], rotation=40, ha="right")
    axd.set_ylim(-7.0, 31.0)                     # headroom: the legend sits above the largest stored difference (18.3 percent, fitted amplitude at ceni 4.95 ms)
    axd.set_ylabel("(network - MF) / MF (percent)")
    axd.set_title("(h) S3 network against mean field", loc=S.TITLE_LOC)
    axd.legend(loc="upper left", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # (i) K9
    axe = fig.add_subplot(gs[2, 2:4])
    k9 = S.diagram_mark("k9_pt")
    axe.plot(d["k9_eta_bar"], d["k9_ratio"], ls="none", marker=k9.marker, ms=k9.size, color=k9.colour, zorder=4, label="largest Delta/eta_bar (A4)")
    axe.axhspan(FS2_K9[0] - FS2_K9[1], FS2_K9[0] + FS2_K9[1], color=tol.colour, alpha=0.3, lw=0, label="plan 0.1453 +- 0.002")
    axe.set_xticks(d["k9_eta_bar"])
    axe.set_ylim(FS2_K9[0] - 3 * FS2_K9[1], FS2_K9[0] + 3 * FS2_K9[1])      # the plan band is +-0.002: three band widths either side, so the band is a band
    axe.set_xlim(0.5, 4.5)
    axe.set_xlabel(r"$\bar\eta$")
    axe.set_ylabel(r"$\Delta/\bar\eta$")
    axe.set_title("(i) K9 ratio scaling", loc=S.TITLE_LOC)
    axe.legend(loc="lower right", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # (j) K11
    axk = fig.add_subplot(gs[2, 4:6])
    k11 = S.diagram_mark("k11_pt")
    axk.plot(-d["k11_J_H"], d["k11_ratio"], ls="none", marker=k11.marker, ms=k11.size, color=k11.colour, zorder=4, label="Im lambda / (2 pi r*), 20 branches (A4)")
    for sgn in (-1, 1):
        axk.axhline(1.0 + sgn * FS2_K11, color=tol.colour, ls=tol.linestyle, lw=tol.width, label="plan: 1 +- 0.01" if sgn == -1 else None)
    axk.set_xscale("log")
    axk.set_xticks([5e-4, 1e-3, 2e-3, 5e-3])
    axk.set_xticklabels(["5e-4", "1e-3", "2e-3", "5e-3"])
    axk.minorticks_off()
    axk.set_ylim(0.980, 1.014)
    axk.set_xlabel("-J at the Hopf point")
    axk.set_ylabel("ratio")
    axk.set_title("(j) K11, Delta = 1e-4", loc=S.TITLE_LOC)
    axk.legend(loc="lower left", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # (k) K10 frequency against tau_d
    axf = fig.add_subplot(gs[3, 0:3])
    k10 = S.diagram_mark("k10_curve")
    axf.plot(d["k10_tau_d"], d["k10_freq"], color=k10.colour, lw=k10.width, label="A4 linear frequency, eta_bar 1, J -20 (64 points)", zorder=3)
    lo, hi = d["k10_band_hz"]
    sl = d["k10_band_slack"]
    for yv, lab in ((lo * (1 - sl), "plan band 5 to 30 Hz, +-10 percent"), (hi * (1 + sl), None)):
        axf.axhline(yv, color=tol.colour, ls=tol.linestyle, lw=tol.width, label=lab)
    axf.set_xlabel(r"$\tau_d$ (ms)")
    axf.set_ylabel("frequency (Hz)")
    axf.set_title("(k) K10 frequency against tau_d (band and monotone parts)", loc=S.TITLE_LOC)
    axf.legend(loc="center right", bbox_to_anchor=(1.0, 0.68), fontsize=T["legend"], frameon=True, framealpha=0.95)
    # (l) K10 J dependence: stored linear frequency
    axg = fig.add_subplot(gs[3, 3:6])
    for tau, key in (("8.0", "k10_j8"), ("20.0", "k10_j20"), ("40.0", "k10_j40")):
        st = S.diagram_mark(key)
        axg.plot(d[f"k10_J_{tau}"], d[f"k10_lin_{tau}"], color=st.colour, ls=st.linestyle, lw=0.7, marker=st.marker, ms=st.size, zorder=3,
                 label=f"tau_d {float(tau):g} ms: change {100 * d[f'k10_rel_change_{tau}']:.1f} percent (limit {100 * d['k10_j_limit']:.0f})")
    axg.set_xlabel("J")
    axg.set_ylabel("linear Im lambda frequency (Hz)")
    axg.set_title("(l) K10 J dependence: NOT reproduced as worded", loc=S.TITLE_LOC)
    axg.set_ylim(top=25.0)                       # headroom: the legend sits above the first marker of the 8 ms line
    axg.legend(loc="upper left", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # status block
    axs = fig.add_subplot(gs[4, :])
    axs.axis("off")
    lines = ["Status of each check, from the stored values (a failure is shown, not dropped):"]
    for text in fs2_status_lines(d):
        lines += textwrap.wrap(text, width=150, subsequent_indent="    ")
    axs.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=T["status"], linespacing=1.25)
    fig = _style_text(fig, FS2_FOOTER if draft else "")
    # (j) 13p (DL-500 R15): the asterisks stay at their stored positions; the count of marks that overlap at the drawn size is printed (after the layout is final)
    fig.canvas.draw()
    pts = axk.get_lines()[0]
    n_co = coincident_marks(axk, pts, S.FS_SIZES["fs2_coincide_mark"])
    n_all = len(pts.get_xdata())
    distinct = len(set(zip(np.asarray(pts.get_xdata()).tolist(), np.asarray(pts.get_ydata()).tolist()))) == n_all
    axk.text(0.98, 0.80, f"{n_co} of {n_all} coincide at the drawn size\n(" + ("stored values all differ" if distinct else "some stored values are equal") + ")",
             transform=axk.transAxes, ha="right", va="top", fontsize=T["small"], color=S.figure_colour("text_dark")).set_gid("coincide_note")
    return fig


def fs2_status_lines(d: dict) -> list[str]:
    return [
        f"K7 Hopf: tau_d {d['hopf_a4_ms']:.4f} ms (A4; A5 {d['hopf_a5_ms']:.4f}) against the paper's {FS2_K7_PAPER_MS:g} ms; not reproduced, kept as a recorded departure (DL-074, DL-076, DL-079).",
        f"K7 time series: v decays at 3 ms (final v amplitude {d['k7_mf_vptp'][0]:g}) and holds at 8 ms (window deviation {d['k7_mf_hold_dev'][2]:.2g}, limit 0.02): pass (S3 summary).",
        f"K7 amplitude half: R2 {d['fit_s4_up_r2']:.5f} pass; residual {100 * d['fit_s4_up_max_resid_frac']:.2f} percent against 2 percent FAIL (REPORTED FAILURE, DL-129); up-down difference {d['fit_hysteresis_max_rel_diff']:.1e} pass. "
        "The post hoc fit is exploratory, not pre-registered (DL-130).",
        f"K8: limit cycle at 5 ms (v amplitude {d['k8_mf_vptp'][0]:.3f}), fixed point at 50 ms; mean-field peak {d['k8_mf_f_fft']:.2f} Hz, A6 cycle frequency at eta_bar 4 {d['k8_a6_f_eta4']:.2f} Hz; network (N = 5e4) {100 * d['k8_net_rel_diff']:+.2f} percent against the 5 percent tolerance: pass.",
        f"K9: largest ratio {d['k9_ratio'].max():.5f}, spread {d['k9_ratio'].max() - d['k9_ratio'].min():.1e}; {d['k9_on_edge']} maximisers on an edge. K11: largest deviation from 1 {d['k11_max_dev']:.1e} (tolerance {FS2_K11:g}). Both pass.",
        f"K10 (non-blocking, single source, UNVERIFIED): band and monotone parts pass; the J dependence is {100 * d['k10_rel_change_8.0']:.1f}, {100 * d['k10_rel_change_20.0']:.1f} and {100 * d['k10_rel_change_40.0']:.1f} percent against {100 * d['k10_j_limit']:.0f}: not passed as worded (DL-131, DL-132).",
        "K4-net: not run, M2 network coupling unsourced (open item 1, T51); non-blocking (DL-113). No source was supplied (DL-119).",
        "FAIL rows of the stored A11 table that touch FS2: none (Table 7.2 names no RB check for FS2; UNVERIFIED reading).",
    ]


def fs2_caption_notes(d: dict) -> tuple:
    """Sentences about what is and is not drawn (13h). Values come from the prepared data; only the wording is typed here."""
    return (
        "Panels (a) and (b) draw the A5 stable ceni cycle branch (v amplitude and its square), the A4 Hopf point, and the S3 mean-field runs at 3, 4.95 and 8 ms. The two fit lines in (b) "
        "are drawn from the stored slope and intercept of the K7 amplitude check (A5 check file); the line from the pre-registered window misses the residual rule, and the "
        "near-Hopf line is a POST HOC exploratory fit (DL-130).",
        "Panels (c) to (g) are the stored S3 r(t) series, last 400 ms of the 10 s runs (the series run to 10 s, mean field at 1 ms output, network at 1 ms bins). Network runs are single "
        "seeds; the network r has a different noise character from the mean field, and the network start differs (DL-119). No smoothing or interpolation is applied.",
        "Panel (h) draws the stored differences (network minus mean field over mean field); only the K8 frequency has a criterion (5 percent); the amplitude and mean differences are "
        "information (DL-119, DL-129). The 3 ms and 50 ms cells have no mean-field oscillation, so their differences are undefined and not drawn.",
        "Panels (i) and (j) are the stored K9 and K11 arrays of the A4 run, with the plan's tolerance bands. Panels (k) and (l) are the K10 readouts: (k) the A4 linear frequency against tau_d, "
        "(l) the stored linear frequency at J of -40, -30, -20, -10 and -5 for three tau_d; the linear frequency is not a cycle frequency (DL-131).",
        "The A6 frequency map file is opened for one check only (the ref_devalle slice reproduces the stored cycle frequency at eta_bar 4); no frequency map is drawn. S3 cells of the K8 N = 5e4 run have a single seed.",
        "K7, K9 to K11 are single-source checks (CP1, CP11); K10 is UNVERIFIED single source.",
    )


def make_FS2(res=None, out_dir=None, *, tag_build: bool = False, take_home=FS2_TAKE_HOME, claim_limit_ids=FS2_CLAIM_LIMITS,
             script="scripts/fig_FS2.py", root=None) -> dict:
    """Build FS2 from results/. Returns {'prov', 'paths', 'timing_s', 'drawn_sha256', 'caption'}. tag_build=True needs a clean tree (figprov)."""
    F.require_buildable("FS2")
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "FS2"
    t = {"start": time.perf_counter()}
    raw = load_FS2(res)
    t["load"] = time.perf_counter()
    d = prepare_FS2(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for panel, key in (("a,b,i-l", "A4"), ("a,b", "A5"), ("k,l", "A6"), ("a,c-e", "S3_mf_ceni"), ("f,g", "S3_mf_devalle"), ("c-e,h", "S3_net_ceni"), ("f,h", "S3_net_devalle"), ("f,h", "S3_net_k8")):
        rec = raw["records"][key]
        for r in make_param_table(rec["config"]):
            rows.append({**r, "panel": panel, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    cap = CAP.build_caption("FS2", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=[r for r in rows if r["key"] in FS2_CAPTION_KEYS],
                            spectrogram=None, symbol_keys=(), notes=fs2_caption_notes(d))
    import matplotlib.pyplot as plt
    fig = _draw_FS2(d, draft=not tag_build)
    out.mkdir(parents=True, exist_ok=True)
    pdf, png = out / "FS2.pdf", out / "FS2.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=S.PNG_DPI)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    cap_path, dig_path = out / "FS2_caption.txt", out / "FS2_drawn_data_sha256.txt"
    from .. import provenance as P
    drawn = drawn_data_sha256(d)
    P.atomic_write_text(cap_path, cap.text + "\n")
    P.atomic_write_text(dig_path, drawn + "\n")
    warnings = []
    for k, rec in raw["records"].items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true")
    prov = F.write_figure_provenance(
        "FS2", script=script, inputs=[res / p for p in FS2_INPUTS], outputs=[pdf, png, cap_path, dig_path], params_rows=rows,
        modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py",
                 "src/mprsurge/plotting/nordlie.py", "src/mprsurge/plotting/figprov.py"],
        configs=["configs/A4_grids.yaml", "configs/A5.yaml", "configs/A6.yaml", "configs/S3.yaml", "configs/S3_ceni.yaml", "configs/S3_net_ceni.yaml",
                 "configs/S3_net_devalle.yaml", "configs/S3_net_k8.yaml"], claim_limits=cap.claim_limits, spectrogram=None, tag_build=tag_build,
        out_dir=out, root=root, warnings=warnings, wall_time_s=time.perf_counter() - t["start"])
    nordlie_path = out / "FS2_nordlie.md"
    N.write_nordlie(out / "FS2_params.csv", out / "FS2_provenance.json", nordlie_path, root=root)
    t["end"] = time.perf_counter()
    timing = {"load_s": t["load"] - t["start"], "prepare_s": t["prepare"] - t["load"], "draw_s": t["draw"] - t["prepare"],
              "provenance_and_nordlie_s": t["end"] - t["draw"], "total_s": t["end"] - t["start"]}
    return {"prov": prov, "paths": [pdf, png, cap_path, dig_path, out / "FS2_params.csv", out / "FS2_provenance.json", nordlie_path],
            "timing_s": timing, "drawn_sha256": drawn, "caption": cap.text}

# ---- FS5 (13i) -------------------------------------------------------------------------------------------------------------------------------------
# Paths relative to results/ (the two test files are relative to the repository root and are read as text, parsed, never run: plan 13a section 4, FS5 inputs).
# The registry scripts/ms13_inputs.py INPUTS["FS5"] must name the same files (test).
FS5_INPUTS = (
    "A8/a8_sensitivity.csv",                                 # 1,880 stored classifications: 10 variants of the A8 classifier on synthetic and stored records (DL-147)
    "A8/baseline/a8_baseline_summary.json",                  # noise envelope counts of the 7e baseline records (DL-145, DL-147)
    "A8/sensitivity/a8_reachability.csv",                    # share of cells with baseline rho at or above a level, per window (DL-147 (5))
    "A8/sensitivity/a8_whitenoise.csv",                      # white-noise records per window and variant by class (DL-147 (6); added at 13i)
    "A8/sensitivity/a8_sens_summary.json",                   # stored class changes against V0: the counts of panel (c) are checked against it (added at 13i)
    "A11/a11_robustness.csv",                                # stored A11 table: RB9 and RB10 status rows and the FAIL-row strip
    "A11/a11_evaluators.json",                               # stored RB9 and RB10 numbers that the A11 table leaves blank (added at 13i)
    "A11/rb9a_unit_level.json",                              # RB9(a) unit-level result (DL-351, DL-365)
    "A6/a6_freq_map.npz",                                    # opened for one check only (DL-430 input; UNVERIFIED reading); no A6 frequency map is drawn
    "A6/a6_summary.json",                                    # the stored value that check compares with (added at 13i)
    "A8/sensitivity/A8sens_0000_64d37749bae1.json",          # run record: source of the A8 sensitivity rows of FS5_params.csv (added at 13i)
    "A8/baseline/A8base_0000_e2dbc529d19d.json",             # run record: source of the A8 baseline rows of FS5_params.csv (added at 13i)
)
FS5_TEST_FILES = ("tests/test_surge_metrics.py", "tests/test_surge_classes.py")
FS5_RECORDS = {"A8_sensitivity": FS5_INPUTS[10], "A8_baseline": FS5_INPUTS[11]}
FS5_STRIP_RB = ("RB9", "RB10")          # Table 7.2 'Where' names FS5 for RB9 ("FS5; F3") and RB10 ("FS5") (plan.md lines 852 and 853)
FS5_CAPTION_KEYS = ("model.type", "model.ref_point", "model.tau_ms", "analysis.band_primary_hz", "analysis.window_rule", "analysis.amin_factor",
                    "analysis.rel_factor", "analysis.abs_factor", "analysis.min_cycles", "noise.sigma")
FS5_GROUPS = (("stored_S3", "D"), ("stored_S4_ceni", "D"), ("stored_S4_devalle", "D"), ("synthetic", "N"), ("synthetic", "D"))
FS5_GROUP_LABELS = ("S3 mean field (mode D)", "S4 ceni holds (D)", "S4 devalle holds (D)", "synthetic mode N", "synthetic mode D")
FS5_RB10_BOUND = 0.1                    # plan Table 7.2 RB10: <= 10 percent of map cells change class (the A11 row threshold text names it)
FS5_RB9A_TOL = 0.005                    # plan Table 7.2 RB9(a): within 0.5 percent (read back from the stored evaluator file and checked)
FS5_RB9C_BOUND = 0.05                   # plan Table 7.2 RB9(c): <= 5 percent of cells (read back and checked)
FS5_WHITE_CLASSES = ("S+", "S-rel", "S-abs", "S-sus", "NS")

# Ruled (RULED_DL, 13p R13); first proposed for the reviewer's ruling (13i prompt, item B3); every statement is from a logged result (DL numbers in the text) and the numbers are checked
# against the stored arrays by tests/test_fig_FS5.py.
FS5_TAKE_HOME = (
    "The surge classifier, with its D8 call provisional, was run on 26 synthetic cases and on stored mean-field records under nine "
    "variants (A8; DL-147): which classes change is drawn per variant. The plan's D8 estimator fails 2 of the plan's 8 A8 ring items (DL-161, DL-163), and short "
    "windows give false surges: 306, 400, 172 and 24 of 500 white-noise records are not NS at W = 0.2, 0.333, 0.593 and 1.054 s (DL-147, DL-163). RB10 passes "
    "(headline class unchanged under all nine variants; at most 1.67 percent of the 900 map-1 cells change class against the 10 percent bound; DL-388). "
    "RB9(a) passes at unit level (1.2e-8 against 0.005; DL-351, DL-388), RB9(c) passes (14 of 900 cells), RB9(b) FAILS (49.0 Hz spectral peak against a "
    "44.609 Hz cycle frequency, 4.391 Hz against 1/W = 0.5 Hz; DL-388), and RB9(d) is reported only."
)
# Ruled (RULED_DL, 13p R13): the limits of docs/ms13_plan.md section 5 whose right-hand column lists FS5 (MS9 (e)-5, DL-163 departures 1, 2 and 4, MS11-C3, MS11-C4, MS11-C7,
# MS11-C9); MS12-C1 lists F1 to F6 and FS6, not FS5. The RB9(b) FAIL row (DL-388) is in the FAIL-row strip. Listed, not decided.
FS5_CLAIM_LIMITS = ("MS11-C7", "MS9(e)-5", "DL-163-D1", "DL-163-D2", "DL-163-D4", "MS11-C3", "MS11-C4", "MS11-C9", "RB9(b) FAIL (plan label)")      # 13p (DL-494 R5): plan label added
FS5_FOOTER = draft_footer("FS5")


def load_FS5(res=None, root=None) -> dict:
    """Open the files of FS5_INPUTS under `res` (default results/) and the two test files under the repository root as text. Opens nothing else."""
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    for rel in FS5_INPUTS:
        if not (res / rel).is_file():
            raise F.MissingInputError(f"input file not found: {res / rel}")
    for rel in FS5_TEST_FILES:
        if not (root / rel).is_file():
            raise F.MissingInputError(f"input file not found: {root / rel}")

    def rows(rel):
        with open(res / rel, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    def js(rel):
        return json.loads((res / rel).read_text(encoding="utf-8"))

    try:
        with np.load(res / "A6/a6_freq_map.npz", allow_pickle=False) as z:
            a6 = {k: z[k] for k in ("slice_ids", "po_slice_index", "po_param", "po_frequency_hz")}
        return {"a8": rows(FS5_INPUTS[0]), "baseline": js(FS5_INPUTS[1]), "reach": rows(FS5_INPUTS[2]), "white": rows(FS5_INPUTS[3]), "sens": js(FS5_INPUTS[4]),
                "a11": rows(FS5_INPUTS[5]), "evaluators": js(FS5_INPUTS[6]), "rb9a": js(FS5_INPUTS[7]), "a6": a6, "a6_summary": js(FS5_INPUTS[9]),
                "records": {k: js(rel) for k, rel in FS5_RECORDS.items()},
                "tests": {rel: (root / rel).read_text(encoding="utf-8") for rel in FS5_TEST_FILES}}
    except (OSError, ValueError, KeyError) as exc:
        raise F.MissingInputError(f"an FS5 input cannot be read: {exc}") from exc


def _test_cases(source: str) -> list[dict]:
    """The test functions of a test module as a list of cases: name, strict-xfail flag and reason (read from the decorators; nothing is run)."""
    import ast
    tree = ast.parse(source)
    alias = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Call):
            alias[n.targets[0].id] = n.value

    def xfail_call(dec):
        if isinstance(dec, ast.Name):
            dec = alias.get(dec.id)
        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == "xfail":
            return dec
        return None

    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and not n.name.startswith("test_"):
            # a helper that sets an xfail mark on individual parameters (marks=[alias]): listed as a parameter-level mark
            used = {m.id for m in ast.walk(n) if isinstance(m, ast.Name) and m.id in alias and xfail_call(m) is not None}
            for a in sorted(used):
                kw = {k.arg: k.value for k in alias[a].keywords}
                out.append({"name": f"{n.name} (xfail mark on parameters)", "xfail": True, "strict": bool(kw["strict"].value) if "strict" in kw else False,
                            "reason": kw["reason"].value if "reason" in kw and isinstance(kw["reason"], ast.Constant) else "", "line": n.lineno, "helper": True})
        if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"):
            xf = next((c for c in (xfail_call(d) for d in n.decorator_list) if c is not None), None)
            kw = {k.arg: k.value for k in xf.keywords} if xf is not None else {}
            strict = bool(kw["strict"].value) if "strict" in kw and isinstance(kw["strict"], ast.Constant) else False
            reason = kw["reason"].value if "reason" in kw and isinstance(kw["reason"], ast.Constant) else ""
            out.append({"name": n.name, "xfail": xf is not None, "strict": strict, "reason": reason, "line": n.lineno})
    return sorted(out, key=lambda c: c["line"])


def prepare_FS5(raw: dict) -> dict:
    """Pure: stored content -> the arrays and numbers that are drawn. Keys are flat names; values are arrays, ints, floats, bools, strings or lists of strings."""
    d: dict = {}
    classes = S.CLASS_KEYS + ("not_run",)
    a8 = raw["a8"]
    if len(a8) != 1880:
        raise DataError(f"a8_sensitivity.csv has {len(a8)} rows, not the 1,880 of DL-147")
    variants = []
    for r in a8:
        if r["variant"] not in variants:
            variants.append(r["variant"])
    if variants[0] != "V0" or len(variants) != 10:
        raise DataError(f"unexpected variants {variants}")
    d["variants"] = variants
    cls = {}                                                      # (dataset, mode, record, T_ramp_s, variant) -> class
    window = {}
    for r in a8:
        if r["cls"] not in classes:
            raise DataError(f"unknown class {r['cls']!r} in a8_sensitivity.csv")
        cls[(r["dataset"], r["mode"], r["record"], r["T_ramp_s"], r["variant"])] = r["cls"]
        if r["variant"] == "V0":
            window[(r["dataset"], r["mode"], r["record"], r["T_ramp_s"])] = r["window_s"]
    # (a) synthetic classes: one row per (record, T_ramp), one column per variant, in the stored order
    syn = [k for k in window if k[0] == "synthetic"]
    if len(syn) != 39 or any((*k, v) not in cls for k in syn for v in variants):
        raise DataError("the synthetic block is not 39 rows by 10 variants")
    d["syn_code"] = np.array([[classes.index(cls[(*k, v)]) for v in variants] for k in syn], dtype=float)
    d["syn_label"] = [f"{k[2]} | {float(k[3]):g} s | W {float(window[k]):g}" for k in syn]
    d["syn_mode"] = [k[1] for k in syn]
    d["class_order"] = list(classes)
    # (c) class changes against V0 per group and variant; checked against the stored a8_sens_summary.json
    n_g = np.zeros(len(FS5_GROUPS))
    chg = np.zeros((len(FS5_GROUPS), len(variants) - 1))
    nrun = np.zeros_like(chg)
    stored = {(e["dataset"], e["mode"], e["variant"]): e for e in raw["sens"]["changes_vs_V0"]}
    for gi, (ds, mode) in enumerate(FS5_GROUPS):
        keys = [k for k in window if k[0] == ds and k[1] == mode]
        n_g[gi] = len(keys)
        for vi, v in enumerate(variants[1:]):
            c = sum(1 for k in keys if cls[(*k, v)] != cls[(*k, "V0")] and cls[(*k, v)] != "not_run")
            nr = sum(1 for k in keys if cls[(*k, v)] == "not_run")
            e = stored[(ds, mode, v)]
            if (c, nr, len(keys)) != (e["changed"], e["not_run"], e["n"]):
                raise DataError(f"class changes of {ds} {mode} {v}: csv gives {(c, nr, len(keys))}, a8_sens_summary.json gives {(e['changed'], e['not_run'], e['n'])}")
            chg[gi, vi], nrun[gi, vi] = c, nr
    d["chg_n"], d["chg_changed"], d["chg_not_run"] = n_g, chg, nrun
    # (d) reachability: share of cells whose mean-over-seeds baseline rho is at or above the level, per window
    reach = raw["reach"]
    ws = sorted({float(r["W_s"]) for r in reach})
    levels = sorted({float(r["level"]) for r in reach})
    d["reach_W"], d["reach_level"] = np.array(ws), np.array(levels)
    share = np.full((len(ws), len(levels)), np.nan)
    ncell = np.zeros(len(ws))
    for r in reach:
        i, j = ws.index(float(r["W_s"])), levels.index(float(r["level"]))
        share[i, j] = float(r["cells_mean_ge"]) / float(r["n_cells"])
        ncell[i] = float(r["n_cells"])
    d["reach_share"], d["reach_n_cells"] = share, ncell
    # (e) white noise at V0: count per class per window out of the stored denominator
    wn = [r for r in raw["white"] if r["variant"] == "V0"]
    wws = sorted({float(r["W_s"]) for r in wn})
    allc = FS5_WHITE_CLASSES + ("failed", "not_run")
    cnt = np.zeros((len(wws), len(allc)))
    den = np.zeros(len(wws))
    for r in wn:
        i = wws.index(float(r["W_s"]))
        cnt[i, allc.index(r["class"])] = float(r["count"])
        den[i] = float(r["denominator"])
    if not np.array_equal(cnt.sum(axis=1), den):
        raise DataError("white-noise V0 counts do not sum to the stored denominator")
    d["white_W"], d["white_count"], d["white_den"] = np.array(wws), cnt, den
    d["white_nonNS"] = cnt[:, [0, 1, 2, 3]].sum(axis=1)
    # (f) RB10 and (g) RB9 from the stored evaluator file, with the A11 table statuses checked against it
    ev = raw["evaluators"]["evaluators"]
    status = {(r["rb_id"], r["check_id"]): r["pass_or_fail"] for r in raw["a11"]}
    want = {("RB9", "a_dimensional_vs_nondimensional"): ev["rb9a"]["status"], ("RB9", "b_spectral_vs_cycle_headline"): ev["rb9b"]["status"],
            ("RB9", "c_band_30_120_map1"): ev["rb9c"]["status"], ("RB9", "d_tau_pm20"): ev["rb9d"]["status"], ("RB10", "surge_definition_sensitivity_map1"): ev["rb10"]["status"]}
    for k, v in want.items():
        if status.get(k) != v:
            raise DataError(f"A11 table status {status.get(k)!r} of {k} differs from the evaluator file {v!r}")
    d["rb_status"] = [f"{k[0]} {k[1]}: {v}" for k, v in want.items()]
    r10 = ev["rb10"]["variants"]
    d["rb10_variant"] = list(r10)
    d["rb10_fraction"] = np.array([float(r10[v]["fraction"]) for v in r10])
    d["rb10_headline_all_pass"] = all(r10[v]["headline"] == "PASS" for v in r10)
    d["rb10_n_cells"] = int(next(iter(r10.values()))["n_evaluated"])
    if ev["rb9a"]["threshold"] != FS5_RB9A_TOL or ev["rb9c"]["bound"] != FS5_RB9C_BOUND:
        raise DataError("a stored RB9 bound differs from the plan value")
    if abs(raw["rb9a"]["tolerance_frozen"] - FS5_RB9A_TOL) > 0 or raw["rb9a"]["per_tau"] != ev["rb9a"]["per_tau"]:
        raise DataError("rb9a_unit_level.json and the evaluator file differ")
    taus = sorted(ev["rb9a"]["per_tau"], key=float)
    d["rb9a_tau_ms"] = np.array([float(t) for t in taus])
    d["rb9a_diff"] = np.array([[ev["rb9a"]["per_tau"][t][q] for q in ("r", "v", "s")] for t in taus])
    d["rb9a_value"], d["rb9a_tol"] = float(ev["rb9a"]["value"]), float(ev["rb9a"]["threshold"])
    hb = ev["rb9b"]["headline"]
    d["rb9b_f_spectral"], d["rb9b_f_cycle"], d["rb9b_diff"], d["rb9b_bound"] = (float(hb[k]) for k in ("f_spectral_hz", "f_cycle_hz", "diff_hz", "bound_hz"))
    d["rb9b_within"] = bool(hb["within"])
    cr = ev["rb9b"]["cells_reported"]
    d["rb9b_map1_within"], d["rb9b_map1_n"], d["rb9b_map2_within"], d["rb9b_map2_n"] = int(cr["map1"]["within"]), int(cr["map1"]["n"]), int(cr["map2"]["within"]), int(cr["map2"]["n"])
    c9 = ev["rb9c"]
    d["rb9c_bound"] = float(c9["bound"])
    d["rb9c_set"] = ["map 1 (verdict)", "map 2 (beside)", "subgrid (beside)"]
    d["rb9c_changed"] = np.array([c9["n_changed"], c9["beside"]["map2"]["n_changed"], c9["beside"]["subgrid"]["n_changed"]], dtype=float)
    d["rb9c_n"] = np.array([c9["n_evaluated"], c9["beside"]["map2"]["n_evaluated"], c9["beside"]["subgrid"]["n_evaluated"]], dtype=float)
    d9 = ev["rb9d"]
    rows_d = sorted([d9["headline_10ms"]] + [{k: r[k] for k in ("tau_ms", "class", "f_pk_hz")} for r in d9["rows"]], key=lambda r: r["tau_ms"])
    d["rb9d_tau_ms"] = np.array([r["tau_ms"] for r in rows_d])
    d["rb9d_f_pk"] = np.array([r["f_pk_hz"] for r in rows_d])
    d["rb9d_class"] = [r["class"] for r in rows_d]
    d["rb9d_expected_ratio"] = np.array([{r["tau_ms"]: r["f_pk_ratio_expected_10_over_tau"] for r in d9["rows"]}.get(r["tau_ms"], 1.0) for r in rows_d])
    d["rb9d_headline_f"] = float(d9["headline_10ms"]["f_pk_hz"])
    # the A6 file is opened for one check: the ref_devalle slice reproduces the stored summary frequency at eta_bar 4 (as at FS2)
    a6 = raw["a6"]
    ids = [str(x) for x in a6["slice_ids"]]
    m = a6["po_slice_index"] == ids.index("eta_tau_D0.3_td5.0")
    d["a6_f_eta4"] = float(raw["a6_summary"]["devalle"]["f_at_eta_4"])
    if float(np.interp(4.0, a6["po_param"][m], a6["po_frequency_hz"][m])) != d["a6_f_eta4"]:
        raise DataError("the A6 slice does not reproduce the stored A6 summary frequency at eta_bar 4")
    # stored noise-envelope counts of the baseline records (O4; DL-147 (4))
    env = raw["baseline"]["noise_envelope"]["all"]["all"]
    d["env_n_records"], d["env_any_above"], d["a_ref"] = int(env["n_records"]), int(env["records_any_above"]), float(raw["baseline"]["a_ref"])
    # the stored test cases, read as a list
    d["tests_file"], d["tests_n"], d["tests_xfail_name"], d["tests_xfail_reason"] = [], [], [], []
    for rel in FS5_TEST_FILES:
        cases = _test_cases(raw["tests"][rel])
        d["tests_file"].append(rel)
        d["tests_n"].append(sum(1 for c in cases if not c.get("helper")))
        for c in cases:
            if c["xfail"]:
                if not c["strict"]:
                    raise DataError(f"{rel}::{c['name']} carries a non-strict xfail")
                d["tests_xfail_name"].append(f"{Path(rel).stem.replace('test_', '')}::{c['name'].replace('test_', '', 1)}")
                d["tests_xfail_reason"].append(c["reason"])
    d["strip"] = [{"rb_id": r["rb_id"], "check_id": r["check_id"], "value": r["value"], "threshold": r["threshold"], "status": r["pass_or_fail"]}
                  for r in raw["a11"] if r["rb_id"] in FS5_STRIP_RB and r["pass_or_fail"] == "FAIL"]
    return d


def fs5_strip_lines(d: dict) -> list[str]:
    """FAIL rows of the stored A11 table that touch FS5. The numbers a blank 'value' cell leaves out are read from the stored evaluator file."""
    out = []
    for r in d["strip"]:
        thr = f"threshold {r['threshold']}" if r["threshold"] else "threshold blank in the table"
        extra = ""
        if (r["rb_id"], r["check_id"]) == ("RB9", "b_spectral_vs_cycle_headline"):
            extra = (f"; stored evaluator: {d['rb9b_f_spectral']:.1f} Hz spectral against {d['rb9b_f_cycle']:.3f} Hz cycle, difference {d['rb9b_diff']:.3f} Hz "
                     f"against {d['rb9b_bound']:g} Hz")
        out.append(f"{r['rb_id']} {r['check_id']}: {r['status']} ({thr}{extra})")
    return out


def _fs5_wrap_name(text: str, width: int) -> list[str]:
    """A long test name breaks after an underscore, never inside a word; the continuation is indented."""
    out = []
    ln = text
    while len(ln) > width and "_" in ln[:width]:
        cut = ln[:width].rindex("_") + 1
        out.append(ln[:cut])
        ln = "    " + ln[cut:]
    return out + [ln]


def _draw_FS5(d: dict, draft: bool):
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, Rectangle
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    T = S.TEXT_SIZES
    edge = S.figure_colour("bar_edge")
    fig = plt.figure(figsize=(7.4, 14.4), constrained_layout=True)
    gs = fig.add_gridspec(5, 6, height_ratios=[4.3, 1.9, 1.9, 2.0, 1.25])
    classes = d["class_order"]
    var = d["variants"]
    # row 0: (a) and a wider (b) column (13p, R18: the test-name list is readable)
    top = gs[0, :].subgridspec(1, 2, width_ratios=list(S.FS_LAYOUT["fs5_row0_ratios"]))
    # (a) synthetic classes under the ten variants: one marker per cell, shape and colour from the class table
    ax = fig.add_subplot(top[0, 0])
    nrow = len(d["syn_label"])
    ys = np.arange(nrow, dtype=float)
    for ci, name in enumerate(classes):
        sel = d["syn_code"] == ci
        if not sel.any():
            continue
        yy, xx = np.nonzero(sel)
        if name == "not_run":
            mk = S.diagram_mark("not_run")
            ax.plot(xx, yy, ls="none", marker=mk.marker, ms=mk.size, color=mk.colour, mew=mk.width, label="not run (window does not fit)", zorder=4)
        else:
            st = S.get(name)
            ax.plot(xx, yy, ls="none", marker=st.marker, ms=S.FS_SIZES["fs5_class"], color=st.colour, mec=edge, mew=0.25, label=f"{name} ({int(sel.sum())})", zorder=4)
    n_rows_n = d["syn_mode"].count("N")
    ax.axhline(n_rows_n - 0.5, color=S.FS_COLOURS["patch_edge"], lw=0.6, zorder=1)
    ax.set_ylim(nrow - 0.5, -0.5)
    ax.set_xlim(-0.6, len(var) - 0.4)
    ax.set_xticks(range(len(var)), var, rotation=40, ha="right")
    ax.set_yticks(ys, d["syn_label"])
    ax.tick_params(length=2)
    ax.set_title("(a) A8 synthetic cases: class under each variant (mode N above the line, D below)", loc=S.TITLE_LOC)
    h_a, l_a = ax.get_legend_handles_labels()
    # (b) the stored test cases, read as a list
    axb = fig.add_subplot(top[0, 1])
    axb.axis("off")
    wrap = S.FS_LAYOUT["fs5_b_wrap"]
    lines = ["(b) from test source text, not from results/"] + textwrap.wrap("The stored synthetic tests, read as a list (never run here):", width=wrap)
    lines += [f"{Path(f).name}: {n} test functions" for f, n in zip(d["tests_file"], d["tests_n"])]
    lines += textwrap.wrap(f"{len(d['tests_xfail_name'])} strict-xfail marks (expected failures), on functions or on parameters:", width=wrap)
    for nm, rs in zip(d["tests_xfail_name"], d["tests_xfail_reason"]):
        lines += _fs5_wrap_name(f"- {nm}:", wrap)
        lines += textwrap.wrap(rs, width=wrap, initial_indent="    ", subsequent_indent="    ")
    axb.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=T["note"], linespacing=1.2)
    axb.legend(h_a, l_a, loc="lower left", ncol=3, fontsize=T["legend"], frameon=True, framealpha=0.95, title="class (cells)", title_fontsize=T["legend"])
    # (c) class changes against V0
    axc = fig.add_subplot(gs[1, 0:4])
    frac = d["chg_changed"] / d["chg_n"][:, None]
    axc.pcolormesh(np.arange(frac.shape[1] + 1) - 0.5, np.arange(frac.shape[0] + 1) - 0.5, frac, cmap=S.CHANGE_CMAP, vmin=0.0, vmax=1.0, shading="flat",
                   edgecolor=S.FS_COLOURS["cell_edge"], lw=0.6)
    for i in range(frac.shape[0]):
        for j in range(frac.shape[1]):
            nr = int(d["chg_not_run"][i, j])
            axc.text(j, i, f"{int(d['chg_changed'][i, j])}/{int(d['chg_n'][i])}" + (f"\n{nr} not run" if nr else ""), ha="center", va="center", fontsize=T["small"],
                     color=S.FS_COLOURS["text_on_light"] if frac[i, j] < S.FS5_TEXT_DARK_ABOVE else S.FS_COLOURS["text_on_dark"])
    axc.set_xticks(range(frac.shape[1]), var[1:], rotation=40, ha="right")
    axc.set_yticks(range(frac.shape[0]), FS5_GROUP_LABELS)
    axc.set_ylim(frac.shape[0] - 0.5, -0.5)
    axc.set_title("(c) class changes against V0: records changed / records (shade: fraction, 0 to 1)", loc=S.TITLE_LOC)
    # (d) reachability of the rho levels. 13p (R18): the window marks are vertex polygons (style keys w_0 to w_5), no card-suit glyphs
    axd = fig.add_subplot(gs[1, 4:6])
    for i, w in enumerate(d["reach_W"]):
        mk = S.diagram_mark(f"w_{i}")
        axd.plot(d["reach_level"], d["reach_share"][i], color=mk.colour, ls=mk.linestyle, lw=0.8, marker=mk.marker, ms=mk.size, mfc=mk.colour if mk.filled else "none",
                 mew=mk.width, zorder=3, label=f"W {w:.3g} s ({int(d['reach_n_cells'][i])} cells)")
    axd.set_xlabel("baseline rho level")
    axd.set_ylabel("share of cells at or above")
    axd.set_ylim(0.0, 1.05)
    axd.set_title("(d) baseline rho reachability", loc=S.TITLE_LOC)
    axd.legend(loc="lower left", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # (e) white noise at V0
    axe = fig.add_subplot(gs[2, 0:3])
    bottom = np.zeros(len(d["white_W"]))
    xw = np.arange(len(d["white_W"]), dtype=float)
    legend_h = []
    for ci, name in enumerate(FS5_WHITE_CLASSES):
        st = S.get(name)
        h = d["white_count"][:, ci] / d["white_den"]
        for x_, b_, h_ in zip(xw, bottom, h):         # Rectangles, not Axes.bar: bar rounds the height in the last bit ((b + h) - b), the stored share must be drawn exactly
            axe.add_patch(Rectangle((x_ - 0.35, b_), 0.7, h_, fc=st.colour, ec=edge, lw=0.3, hatch=S.CLASS_HATCH[name], zorder=3))
        legend_h.append(Patch(fc=st.colour, ec=edge, lw=0.3, hatch=S.CLASS_HATCH[name], label=name))
        for x_, b_, h_, c_ in zip(xw, bottom, h, d["white_count"][:, ci]):
            if h_ >= 0.07:
                axe.text(x_, b_ + h_ / 2, f"{int(c_)}", ha="center", va="center", fontsize=T["small"],
                         bbox=dict(boxstyle="square,pad=0.1", fc=S.figure_colour("label_box"), ec="none", alpha=0.8), zorder=5)
        bottom = bottom + h
    for x_, n_, den in zip(xw, d["white_nonNS"], d["white_den"]):
        axe.text(x_, 1.015, f"{int(n_)}", ha="center", va="bottom", fontsize=T["status"], fontweight="bold")
    axe.set_xticks(xw, [f"{w:.3g}" for w in d["white_W"]])
    axe.set_ylim(0.0, 1.42)
    axe.set_xlabel("window W (s)")
    axe.set_ylabel("share of 500 white-noise records")
    axe.set_title("(e) white noise through the classifier (V0); bold: records not NS", loc=S.TITLE_LOC)
    axe.set_xlim(-0.6, len(xw) - 0.4)
    axe.legend(handles=legend_h, loc="upper center", ncol=5, fontsize=T["legend"], frameon=True, framealpha=0.95, handletextpad=0.3, columnspacing=0.8)
    # (f) RB10
    axf = fig.add_subplot(gs[2, 3:6])
    mk10 = S.diagram_mark("fs5_pt")
    yv = np.arange(len(d["rb10_variant"]), dtype=float)
    axf.plot(d["rb10_fraction"], yv, ls="none", marker=mk10.marker, ms=mk10.size, color=mk10.colour, mew=mk10.width, zorder=4, label=f"map-1 cells that change class (of {d['rb10_n_cells']})")
    tol = S.diagram_mark("tol_band")
    axf.axvline(FS5_RB10_BOUND, color=tol.colour, ls=tol.linestyle, lw=tol.width + 0.3, label="plan bound 0.10", zorder=2)
    axf.set_yticks(yv, d["rb10_variant"])
    axf.set_ylim(len(yv) - 0.5, -0.5)
    axf.set_xlim(-0.005, 0.30)
    axf.set_xlabel("fraction of map-1 cells that change class")
    axf.set_title("(f) RB10: " + ("headline class unchanged, nine variants" if d["rb10_headline_all_pass"] else "headline class changed under a variant"), loc=S.TITLE_LOC)
    axf.legend(loc="lower right", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # (g) RB9, frequency mapping: four small panels of the stored values
    sub = gs[3, :].subgridspec(1, 4, wspace=0.3, width_ratios=list(S.FS_LAYOUT["fs5_g_ratios"]))
    pt = S.diagram_mark("fs5_pt")
    a1 = fig.add_subplot(sub[0, 0])
    for i, tau in enumerate(d["rb9a_tau_ms"]):
        mk = S.diagram_mark(f"rb9a_{i}")
        a1.plot([0, 1, 2], d["rb9a_diff"][i], ls="none", marker=mk.marker, ms=mk.size, color=mk.colour, zorder=4, label=f"tau {tau:g} ms")
    a1.axhline(d["rb9a_tol"], color=tol.colour, ls=tol.linestyle, lw=tol.width + 0.3, label="bound 0.005", zorder=2)
    a1.set_yscale("log")
    a1.set_ylim(1e-10, 3e-2)
    a1.set_xlim(-0.5, 2.5)
    a1.set_xticks([0, 1, 2], ["r*tau", "v", "s*tau"])
    a1.set_title("(g1) RB9(a) PASS\nunit level", loc=S.TITLE_LOC)
    a1.legend(loc="center", bbox_to_anchor=(0.5, 0.62), fontsize=T["legend"], frameon=True, framealpha=0.95)
    a1.set_ylabel("relative difference")
    a2 = fig.add_subplot(sub[0, 1])
    sp, cy = S.diagram_mark("fs5_spectral"), S.diagram_mark("fs5_cycle")
    a2.plot([0], [d["rb9b_f_spectral"]], ls="none", marker=sp.marker, ms=sp.size, color=sp.colour, zorder=4, label="spectral peak")
    a2.errorbar([1], [d["rb9b_f_cycle"]], yerr=[d["rb9b_bound"]], ls="none", marker=cy.marker, ms=cy.size, color=cy.colour, capsize=3, lw=1.0, zorder=4, label="cycle freq. +- 1/W")
    a2.set_xlim(-0.6, 1.6)
    a2.set_ylim(38.0, 51.0)
    a2.set_xticks([0, 1], ["spectral", "cycle"], rotation=30, ha="right")
    a2.set_title("(g2) RB9(b) " + ("PASS" if d["rb9b_within"] else "FAIL") + "\nheadline", loc=S.TITLE_LOC)
    a2.set_ylabel("frequency (Hz)")
    a2.text(0.5, 0.08, f"diff {d['rb9b_diff']:.3f} Hz > {d['rb9b_bound']:g} Hz\nmap 1: {d['rb9b_map1_within']}/{d['rb9b_map1_n']} in\nmap 2: {d['rb9b_map2_within']}/{d['rb9b_map2_n']} in",
            transform=a2.transAxes, ha="center", va="bottom", fontsize=T["small"], bbox=dict(boxstyle="square,pad=0.2", fc=S.FS_COLOURS["box_face"], ec=S.FS_COLOURS["patch_edge"], lw=0.4))
    # (g3) 13p (R18): the verdict is judged on map 1; map 2 and the subgrid are reported, not judged (an open ring and a label mark them; the stored points stay line 0)
    a3 = fig.add_subplot(sub[0, 2])
    xs3 = np.arange(3, dtype=float)
    fr3 = d["rb9c_changed"] / d["rb9c_n"]
    a3.plot(xs3, fr3, ls="none", marker=pt.marker, ms=pt.size, color=pt.colour, mew=pt.width, zorder=4)
    a3.axhline(d["rb9c_bound"], color=tol.colour, ls=tol.linestyle, lw=tol.width + 0.3, label="bound 0.05 (map 1)", zorder=2)
    a3.plot(xs3[1:], fr3[1:], ls="none", marker=S.FS5_REPORTED["marker"], ms=S.FS_SIZES["fs5_reported_ring"], mfc="none", mec=S.FS5_REPORTED["colour"],
            mew=S.FS5_REPORTED["width"], zorder=3, label="reported, not judged", gid="rb9c_reported")
    a3.set_xticks(xs3, ["map 1", "map 2", "subgrid"], rotation=30, ha="right")
    a3.set_xlim(-0.5, 2.5)
    a3.set_ylim(-0.09, 0.78)
    a3.set_title("(g3) RB9(c) PASS, judged on map 1;\nband 30 to 120 Hz", loc=S.TITLE_LOC)
    a3.set_ylabel("fraction of cells that change class")
    a3.legend(loc="upper left", fontsize=T["legend"], frameon=True, framealpha=0.95)
    for x_, c_, n_ in zip(xs3, d["rb9c_changed"], d["rb9c_n"]):
        hi = c_ / n_ > 0.2
        a3.text(x_ - (0.25 if hi else 0.0), c_ / n_ + (0.0 if hi else 0.06), f"{int(c_)}/{int(n_)}" + ("" if x_ == 0 else "\n(reported)"), ha="right" if hi else "center",
                va="center" if hi else "bottom", fontsize=T["small"])
    a4 = fig.add_subplot(sub[0, 3])
    for i, (tau, f, c) in enumerate(zip(d["rb9d_tau_ms"], d["rb9d_f_pk"], d["rb9d_class"])):
        st = S.get(c)
        a4.plot([tau], [f], ls="none", marker=st.marker, ms=S.FS_SIZES["fs5_class_g4"], color=st.colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], zorder=4, label=f"{c}" if i == 0 else None)
    ex = S.diagram_mark("fs5_expected")
    a4.plot(d["rb9d_tau_ms"], d["rb9d_headline_f"] * d["rb9d_expected_ratio"], ls="none", marker=ex.marker, ms=ex.size, color=ex.colour, zorder=3, label="headline x 10/tau")
    a4.set_xticks(d["rb9d_tau_ms"], [f"{t:g}" for t in d["rb9d_tau_ms"]])
    a4.set_xlim(7.0, 13.0)
    a4.set_ylim(38.0, 82.0)
    a4.set_xlabel("tau (ms)")
    a4.set_title("(g4) RB9(d)\nreported only", loc=S.TITLE_LOC)
    a4.set_ylabel("peak frequency (Hz)")
    a4.legend(loc="upper center", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # status block
    axs = fig.add_subplot(gs[4, :])
    axs.axis("off")
    lines = ["Stored status of the RB9 and RB10 rows (A11 table; a failure is shown, not dropped):"] + ["    " + s for s in d["rb_status"]]
    lines += ["FAIL rows of the stored A11 table that touch FS5: " + ("none" if not d["strip"] else "")] + ["    " + s for s in fs5_strip_lines(d)]
    lines = [ln for t_ in lines for ln in textwrap.wrap(t_, width=135, subsequent_indent="        ")]
    for s in (f"Noise envelope (O4): {d['env_any_above']} of {d['env_n_records']} baseline records have a sample at or above 0.1 x A_ref (A_ref {d['a_ref']:.6f}; DL-147 (4)).",
              "A6 frequency map: opened for one check (the ref_devalle slice reproduces the stored summary frequency at eta_bar 4); no A6 frequency map is drawn (the DL-430 reading of the "
              "frequency-mapping panel is UNVERIFIED: the RB9 numbers are the stored A11 evaluator values).",
              "Panel (a) classes are the stored A8 classifications, D8 call provisional (DL-137); (b) lists test functions and their strict-xfail marks from the test files."):
        lines += textwrap.wrap(s, width=135, subsequent_indent="    ")
    axs.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=T["status"], linespacing=1.25)
    return _style_text(fig, FS5_FOOTER if draft else "")


def fs5_caption_notes(d: dict) -> tuple:
    """Sentences about what is and is not drawn (13i). Values come from the prepared data; only the wording is typed here."""
    n_chg = int(d["chg_changed"].sum())
    return (
        f"Panel (a) draws every stored classification of the 26 synthetic cases (39 rows: mode N at T_ramp 120 s and 3 s, mode D at 120 s) under V0 and the nine variants; "
        "the class is the stored one and the D8 call is provisional (DL-137). The expected class of each case is not stored and is not drawn; the strict-xfail marks of the test files are listed in (b). Panel (b) is from test source text, not from results/: the two test files are read as text, never run, and are listed among the inputs of the provenance record.",
        f"Panel (c) counts, per group and variant, the records whose class differs from V0 ({n_chg} changes over all groups and variants; checked against the stored A8 sensitivity summary); "
        "records the window x2 variant could not run are counted as not run, not as unchanged.",
        "Panel (d) is the stored reachability table: the share of cells whose mean-over-seeds baseline rho is at or above each level, per window (UNVERIFIED arithmetic, DL-146; the plan's "
        "four numbers do not follow one formula, so both forms are stored and the 1/f levels are drawn).",
        "Panel (e) is the stored white-noise table at V0: records per class out of 500 per window; white noise has no resonance, so these are rates of the class logic and not predictions for M3 noise (DL-147).",
        "Panels (f) and (g) are the stored RB10 and RB9 values from the A11 evaluator file; the A11 table leaves the RB9(b) value blank, so its numbers are read from the evaluator file. "
        "In (g2), 'in' counts the map cells whose spectral and cycle frequencies agree within 1/W (reported as a fraction, no gate fraction; DL-352). "
        "RB9(a) is a unit-level test on a 1 s eta ramp, not the headline path (DL-351); RB9(d) is post hoc and feeds no gate (DL-367). The headline path is not drawn here.",
        "The frequency-mapping panel reading (A8 plus A6 plus the RB9 rows) is an UNVERIFIED assumption beyond the plan (DL-430).",
    )


def make_FS5(res=None, out_dir=None, *, tag_build: bool = False, take_home=FS5_TAKE_HOME, claim_limit_ids=FS5_CLAIM_LIMITS,
             script="scripts/fig_FS5.py", root=None) -> dict:
    """Build FS5 from results/ (and the two test files, read as text). Returns {'prov', 'paths', 'timing_s', 'drawn_sha256', 'caption'}."""
    F.require_buildable("FS5")
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "FS5"
    t = {"start": time.perf_counter()}
    raw = load_FS5(res, root)
    t["load"] = time.perf_counter()
    d = prepare_FS5(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for key, rec in raw["records"].items():
        for r in make_param_table(rec["config"]):
            rows.append({**r, "panel": key, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    cap = CAP.build_caption("FS5", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=[r for r in rows if r["key"] in FS5_CAPTION_KEYS and r["panel"] == "A8_sensitivity"],
                            spectrogram=None, symbol_keys=(), notes=fs5_caption_notes(d), limit_labels=CLAIM_LIMIT_LABELS)
    import matplotlib.pyplot as plt
    fig = _draw_FS5(d, draft=not tag_build)
    out.mkdir(parents=True, exist_ok=True)
    pdf, png = out / "FS5.pdf", out / "FS5.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=S.PNG_DPI)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    cap_path, dig_path = out / "FS5_caption.txt", out / "FS5_drawn_data_sha256.txt"
    from .. import provenance as P
    drawn = drawn_data_sha256(d)
    P.atomic_write_text(cap_path, cap.text + "\n")
    P.atomic_write_text(dig_path, drawn + "\n")
    warnings = []
    for k, rec in raw["records"].items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true")
    prov = F.write_figure_provenance(
        "FS5", script=script, inputs=[res / p for p in FS5_INPUTS] + [root / p for p in FS5_TEST_FILES], outputs=[pdf, png, cap_path, dig_path], params_rows=rows,
        modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py",
                 "src/mprsurge/plotting/nordlie.py", "src/mprsurge/plotting/figprov.py"],
        configs=["configs/A8_sensitivity.yaml"], claim_limits=cap.claim_limits, spectrogram=None, tag_build=tag_build,
        out_dir=out, root=root, warnings=warnings, wall_time_s=time.perf_counter() - t["start"])
    nordlie_path = out / "FS5_nordlie.md"
    N.write_nordlie(out / "FS5_params.csv", out / "FS5_provenance.json", nordlie_path, root=root)
    t["end"] = time.perf_counter()
    timing = {"load_s": t["load"] - t["start"], "prepare_s": t["prepare"] - t["load"], "draw_s": t["draw"] - t["prepare"],
              "provenance_and_nordlie_s": t["end"] - t["draw"], "total_s": t["end"] - t["start"]}
    return {"prov": prov, "paths": [pdf, png, cap_path, dig_path, out / "FS5_params.csv", out / "FS5_provenance.json", nordlie_path],
            "timing_s": timing, "drawn_sha256": drawn, "caption": cap.text}

# ---- FS4 (13i) -------------------------------------------------------------------------------------------------------------------------------------
# Paths relative to results/. Tables first (docs/ms13_conventions.md M13-12): the stored A7 table holds the MS8 S13 records (delta0, rtol, Radau, the D43 floor
# levels with the Heun dt ladder), the stored A11 evaluator file holds the MS11 S13 rows (delta0 and rtol at 10 s and 316.2278 s, floor at those T_ramp, the network
# dt ladder and V_p). No series is drawn. The registry scripts/ms13_inputs.py INPUTS["FS4"] must name the same files (test).
FS4_INPUTS = (
    "A7/a7_ramp_metrics.parquet",                            # 360 rows; the S13 families S5ramp, delta0, rtol, radau, floor_l0 to floor_l2 are read (DL-183, DL-184, DL-189, DL-190)
    "A11/a11_evaluators.json",                               # stored RB5 and RB6 evaluator rows of MS11 (DL-387)
    "A11/a11_robustness.csv",                                # stored A11 table: the FAIL-row strip and the status check
    "S13/delta0/delta0_0000_b90cc76204e0.json",              # run record of an MS8 S13 run (source of the mean-field rows of FS4_params.csv)
    "S13/ms11/S13_net/S13_net_0000_c83b859499d9.json",       # run record of an MS11 S13 network run (source of the network rows of FS4_params.csv)
)
FS4_RECORDS = {"S13_MS8_delta0": FS4_INPUTS[3], "S13_MS11_network": FS4_INPUTS[4]}
FS4_STRIP_RB = ("RB5", "RB6")          # Table 7.2 'Where' names FS4 for RB5 ("Main F4; FS4") and RB6 ("FS4") (plan.md lines 848 and 849)
FS4_CAPTION_KEYS = ("model.type", "model.ref_point", "path.name", "path.T_ramp_s", "solver.method", "solver.rtol", "solver.delta0", "noise.scheme", "network.N", "analysis.window_s")
FS4_RB6_FPK_BOUND = 0.02               # plan Table 7.2 RB6: halving dt changes f_pk by < 2 percent (the A11 row threshold text '< 0.02' is checked)
FS4_RB6_SOLVER_BOUND_MS = 1.0          # plan Table 7.2 RB6: solvers agree on class with onset within 1 ms (the A11 row threshold text '1 ms' is checked)
FS4_DT = (1e-3, 5e-4, 2.5e-4, 1e-4)    # the network dt ladder, in units of tau (plan S13)
FS4_HEAD_ROWS = (("S5ramp", None, "default: delta0 1e-6, rtol 1e-10"), ("delta0", 1e-9, "delta0 1e-9"), ("delta0", 1e-3, "delta0 1e-3"), ("rtol", 1e-8, "rtol 1e-8"),
                 ("rtol", 1e-12, "rtol 1e-12"), ("radau", None, "Radau, rtol 1e-10"))

# Ruled (RULED_DL, 13p R13); first proposed for the reviewer's ruling (13i prompt, item B3); every statement is from a logged result (DL numbers in the text) and the numbers are checked against
# the stored tables by tests/test_fig_FS4.py.
FS4_TAKE_HOME = (
    "At the headline (P2, ref_devalle, T_ramp 120 s, noise-free) the class is D-tr under every setting tried: delta0 1e-9, 1e-6 and 1e-3, "
    "rtol 1e-8, 1e-10 and 1e-12, and DOP853 against Radau. The onset is 58.698 s everywhere except under Radau, which gives 58.879 s: 181 ms against the 1 ms bound, "
    "so the RB6 solver clause FAILS and is unexplained (DL-184, DL-189, DL-208). The Heun dt ladder 1e-3 to 1e-4 tau leaves the floored delay unchanged at the 1 ms "
    "output grid (DL-184, DL-190). At T_ramp 10 s and 316.2278 s the class is D-tr under delta0 and rtol with zero onset shift (DL-387). The network f_pk is not stable "
    "under halving dt: the classifier-episode f_pk changes by 5 to 43 percent against the 2 percent bound (0 of 3 seeds pass) and the PSD-argmax reading passes in 2 "
    "of 3, so the RB6 network row FAILS (DL-387, DL-394). Results that rest on the network f_pk are shown labelled FAIL and are not used as evidence."
)
# Ruled (RULED_DL, 13p R13): the limits of docs/ms13_plan.md section 5 whose right-hand column lists FS4 (MS9 (e)-5, G6-D2, G6-D3, G4-C6, MS11-C2, MS11-C5, MS11-C6, MS11-C7, MS11-C8);
# MS12-C1 lists F1 to F6 and FS6, not FS4. The RB6 FAIL rows (DL-387) are in the FAIL-row strip. Listed, not decided.
FS4_CLAIM_LIMITS = ("MS11-C7", "MS9(e)-5", "G6-D2", "G6-D3", "G4-C6", "MS11-C2", "MS11-C5", "MS11-C6", "MS11-C8", "RB6 FAIL (plan label)")      # 13p (DL-494 R5): plan label added
FS4_FOOTER = draft_footer("FS4")


def load_FS4(res=None) -> dict:
    """Open the files of FS4_INPUTS under `res` (default results/) and return their content. Opens nothing else."""
    res = Path(res) if res is not None else results_dir()
    for rel in FS4_INPUTS:
        if not (res / rel).is_file():
            raise F.MissingInputError(f"input file not found: {res / rel}")
    try:
        import pandas as pd
        a7 = pd.read_parquet(res / FS4_INPUTS[0])
        with open(res / FS4_INPUTS[2], newline="", encoding="utf-8") as fh:
            a11 = list(csv.DictReader(fh))
        return {"a7": a7, "evaluators": json.loads((res / FS4_INPUTS[1]).read_text(encoding="utf-8")), "a11": a11,
                "records": {k: json.loads((res / rel).read_text(encoding="utf-8")) for k, rel in FS4_RECORDS.items()}}
    except (OSError, ValueError, KeyError, ImportError) as exc:
        raise F.MissingInputError(f"an FS4 input cannot be read: {exc}") from exc


def prepare_FS4(raw: dict) -> dict:
    """Pure: stored content -> the arrays and numbers that are drawn. Keys are flat names; values are arrays, ints, floats, bools, strings or lists of strings."""
    a7, ev = raw["a7"], raw["evaluators"]["evaluators"]
    d: dict = {}
    # (a) headline numerics at T_ramp 120 s (MS8 S13 records in the A7 table)
    onset, cross, cls, lab = [], [], [], []
    for fam, val, label in FS4_HEAD_ROWS:
        sub = a7[a7["family"] == fam]
        if fam == "delta0":
            sub = sub[np.isclose(sub["delta0"].astype(float), val, rtol=0, atol=0)]
        elif fam == "rtol":
            sub = sub[np.isclose(sub["rtol"].astype(float), val, rtol=0, atol=0)]
        if len(sub) != 1 or float(sub["T_ramp_s"].iloc[0]) != 120.0:
            raise DataError(f"A7 table: family {fam} value {val}: {len(sub)} rows, expected one at T_ramp 120 s")
        onset.append(float(sub["onset_s"].iloc[0]))
        cross.append(float(sub["onset_cross_s"].iloc[0]))
        cls.append(str(sub["cls"].iloc[0]))
        lab.append(label)
    d["head_label"], d["head_class"] = lab, cls
    d["head_onset_s"], d["head_onset_cross_s"] = np.array(onset), np.array(cross)
    d["head_radau_minus_default_ms"] = round((onset[-1] - onset[0]) * 1000.0, 6)
    if round(d["head_radau_minus_default_ms"]) != 181 or any(c != "D-tr" for c in cls):
        raise DataError(f"headline numerics: Radau minus default {d['head_radau_minus_default_ms']} ms (DL-184 says 181), classes {cls}")
    # (b) MS11 delta0 and rtol at T_ramp 10 s and 316.2278 s (stored evaluator rows)
    r5, r6 = ev["rb5_delta0"]["rows"], ev["rb6_rtol"]["rows"]
    d["ms11_T"] = np.array([10.0, 316.22776601683796])
    cols = [("delta0", 1e-9), ("delta0", 1e-3), ("rtol", 1e-12), ("rtol", 1e-8)]
    d["ms11_col_label"] = [f"{k} {v:g}" for k, v in cols]
    cl = np.empty((2, 4), dtype=object)
    sh = np.zeros((2, 4))
    for j, (k, v) in enumerate(cols):
        for i, T in enumerate(d["ms11_T"]):
            rows = [r for r in (r5 if k == "delta0" else r6) if r["T_ramp_s"] == T and r[k] == v]
            if len(rows) != 1:
                raise DataError(f"evaluator rows for {k} {v} at T_ramp {T}: {len(rows)}")
            cl[i, j] = rows[0]["class"]
            sh[i, j] = float(rows[0]["onset_shift_s"] if k == "delta0" else rows[0]["onset_diff_s"])
    d["ms11_class"], d["ms11_onset_shift_s"] = cl.tolist(), sh
    # (c) the D43 floor with the Heun dt ladder at T_ramp 120 s, both onset readings (A7 table)
    levels = (0, 1, 2)
    dts = np.array(sorted({float(x) for x in a7.loc[a7["family"] == "floor_l0", "heun_dt_tau"]}))
    d["floor_dt"] = dts
    for L in levels:
        sub = a7[a7["family"] == f"floor_l{L}"]
        for q, col in (("cross", "delay_eta_cross"), ("class", "delay_eta")):
            arr = np.full((len(dts), 10), np.nan)
            for i, dt in enumerate(dts):
                s_ = sub[np.isclose(sub["heun_dt_tau"].astype(float), dt, rtol=0, atol=0)].sort_values("seed")
                if len(s_) != 10:
                    raise DataError(f"floor level {L} dt {dt}: {len(s_)} seeds, expected 10")
                arr[i] = s_[col].to_numpy(dtype=float)
            d[f"floor_l{L}_{q}_delay"] = arr
    # (d) floor medians at T_ramp 10 s and 316.2278 s (stored evaluator rows, RB3(b) form, reported only)
    fr = {(r["onset_reading"], r["T_ramp_s"]): r for r in ev["rb6_floor"]["rows"]}
    d["floorT_median"] = np.array([[fr[("classifier_onset", T)]["median_delay_by_level"][str(L)] for L in levels] for T in d["ms11_T"]])
    d["floorT_raw_noonset_seeds"] = np.array([[fr[("raw_first_crossing", T)]["seeds_without_onset_by_level"][str(L)] for L in levels] for T in d["ms11_T"]], dtype=float)
    d["floorT_direction"] = [fr[("classifier_onset", T)]["direction"] for T in d["ms11_T"]]
    # (e) network f_pk against dt, per seed (stored evaluator rows); the chain of rungs is checked: f2 of one halving is f1 of the next
    net = ev["rb6_network"]
    ce = net["per_reading"]["classifier_episode_fpk"]["rows"]
    lad = [r for r in net["ladder_info"] if r["reading"] == "classifier_episode_fpk"]
    f = np.full((3, 4), np.nan)
    rel = np.full((3, 3), np.nan)
    for r in ce:
        f[r["seed"], 0], f[r["seed"], 1], rel[r["seed"], 0] = r["f1_hz"], r["f2_hz"], r["rel"]
    for r in lad:
        k = {(0.0005, 0.00025): 1, (0.00025, 0.0001): 2}[(r["dt_from"], r["dt_to"])]
        if f[r["seed"], k] != r["f1_hz"]:
            raise DataError(f"network ladder: seed {r['seed']} f_pk at the rung {r['dt_from']} differs between two stored rows")
        f[r["seed"], k + 1], rel[r["seed"], k] = r["f2_hz"], r["rel"]
    d["net_dt"], d["net_f_pk_hz"], d["net_rel_change"] = np.array(FS4_DT), f, rel
    d["net_ce_n_pass"], d["net_psd_n_pass"] = int(net["per_reading"]["classifier_episode_fpk"]["n_pass"]), int(net["per_reading"]["psd_argmax"]["n_pass"])
    d["net_psd_f_pk_hz"] = np.array([[r["f1_hz"], r["f2_hz"]] for r in net["per_reading"]["psd_argmax"]["rows"]])
    d["net_psd_rel_change"] = np.array([r["rel"] for r in net["per_reading"]["psd_argmax"]["rows"]])
    d["net_status"] = net["status"]
    # (f) network classes by dt and V_p (information only) and the V_p comparison (reported only)
    keys = sorted(net["classes_information"], key=lambda k: (-float(k.strip("()").split(",")[0]), -float(k.strip("()").split(",")[1]), int(k.strip("()").split(",")[2])))
    rowsvp = sorted({(float(k.strip("()").split(",")[0]), float(k.strip("()").split(",")[1])) for k in keys}, key=lambda t: (-t[0], -t[1]))
    d["netcls_row"] = [f"V_p {v:g}, dt {dt:g}" for v, dt in rowsvp]
    d["netcls_class"] = [[net["classes_information"][f"({v}, {dt}, {s})"] for s in range(3)] for v, dt in rowsvp]
    d["vp_dt"] = np.array([r["dt"] for r in net["vp_info"]])
    d["vp_seed"] = np.array([r["seed"] for r in net["vp_info"]], dtype=float)
    d["vp_f100_hz"], d["vp_f200_hz"] = np.array([r["f1_hz"] for r in net["vp_info"]]), np.array([r["f2_hz"] for r in net["vp_info"]])
    # statuses of the A11 table against the evaluator file, and the thresholds the figure draws
    st = {(r["rb_id"], r["check_id"]): r for r in raw["a11"]}
    if st[("RB6", "network_fpk_halving_dt")]["pass_or_fail"] != net["status"] or st[("RB6", "network_fpk_halving_dt")]["threshold"] != f"< {FS4_RB6_FPK_BOUND:g}":
        raise DataError("A11 row network_fpk_halving_dt differs from the evaluator file or the plan bound")
    if st[("RB6", "solver_onset_headline")]["pass_or_fail"] != "FAIL" or st[("RB6", "solver_onset_headline")]["threshold"] != f"{FS4_RB6_SOLVER_BOUND_MS:g} ms":
        raise DataError("A11 row solver_onset_headline differs from the stored FAIL or the plan bound")
    if st[("RB5", "delta0_T10_T316")]["pass_or_fail"] != ev["rb5_delta0"]["status"]:
        raise DataError("A11 row delta0_T10_T316 differs from the evaluator file")
    d["rb_status"] = [f"{r['rb_id']} {r['check_id']}: {r['pass_or_fail']}" for r in raw["a11"] if r["rb_id"] in FS4_STRIP_RB]
    d["strip"] = [{"rb_id": r["rb_id"], "check_id": r["check_id"], "value": r["value"], "threshold": r["threshold"], "status": r["pass_or_fail"]}
                  for r in raw["a11"] if r["rb_id"] in FS4_STRIP_RB and r["pass_or_fail"] == "FAIL"]
    d["a7_rows_read"] = int(sum(len(a7[a7["family"] == f_]) for f_ in ("S5ramp", "delta0", "rtol", "radau", "floor_l0", "floor_l1", "floor_l2")))
    return d


def fs4_strip_lines(d: dict) -> list[str]:
    """FAIL rows of the stored A11 table that touch FS4; the numbers a blank 'value' cell leaves out are read from the stored evaluator file."""
    out = []
    for r in d["strip"]:
        val = r["value"] if r["value"] else "value blank in the table"
        extra = ""
        if r["check_id"] == "network_fpk_halving_dt":
            extra = f"; stored evaluator: classifier-episode f_pk {d['net_ce_n_pass']} of 3 seeds pass, PSD argmax {d['net_psd_n_pass']} of 3 pass"
        out.append(f"{r['rb_id']} {r['check_id']}: {r['status']} ({val}; threshold {r['threshold']}{extra}) - results that rest on it are not used as evidence")
    return out


def _draw_FS4(d: dict, draft: bool):
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    T = S.TEXT_SIZES
    fig = plt.figure(figsize=(7.4, 12.6), constrained_layout=True)
    gs = fig.add_gridspec(5, 6, height_ratios=list(S.FS_LAYOUT["fs4_row_ratios"]))
    tol = S.diagram_mark("tol_band")
    fcl = S.diagram_mark("fs4_cross")
    edge = S.figure_colour("bar_edge")
    # (a) headline numerics: one row per setting, the stored classifier onset (class marker) and the raw first crossing (small cross)
    ax = fig.add_subplot(gs[0, 0:4])
    n = len(d["head_label"])
    for i in range(n):
        st = S.get(d["head_class"][i])
        ax.plot([d["head_onset_s"][i]], [i], ls="none", marker=st.marker, ms=S.FS_SIZES["fs4_class"], color=st.colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], zorder=4,
                label=f"{d['head_class'][i]} (classifier onset)" if i == 0 else None)
        ax.plot([d["head_onset_cross_s"][i]], [i], ls="none", marker=fcl.marker, ms=fcl.size, color=fcl.colour, mew=fcl.width, zorder=5, label="raw first crossing" if i == 0 else None)
    ax.set_yticks(range(n), d["head_label"])
    ax.set_ylim(n - 0.5, -0.5)
    ax.set_xlim(58.65, 58.93)
    ax.set_xlabel("onset (s)")
    ax.set_title("(a) headline, T_ramp 120 s: onset under each numerical setting", loc=S.TITLE_LOC)
    ax.text(0.99, 0.42, f"RB6 solver clause: FAIL\nRadau - default = {d['head_radau_minus_default_ms']:g} ms\nagainst the 1 ms bound", transform=ax.transAxes, ha="right", va="center",
            fontsize=T["note"], color=S.figure_colour("fail_text"), bbox=dict(boxstyle="square,pad=0.25", fc=S.FS_COLOURS["box_face"], ec=S.figure_colour("fail_text"), lw=0.5))
    ax.legend(loc="upper right", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # (b) MS11 delta0 and rtol at T_ramp 10 s and 316.2278 s
    axb = fig.add_subplot(gs[0, 4:6])
    for j in range(4):
        for i in range(2):
            st = S.get(d["ms11_class"][i][j])
            axb.plot([j], [i], ls="none", marker=st.marker, ms=S.FS_SIZES["fs4_class_b"], color=st.colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], zorder=4)
            axb.text(j, i + 0.32, f"shift {d['ms11_onset_shift_s'][i, j]:g} s", ha="center", va="center", fontsize=T["small"])
    axb.set_xticks(range(4), d["ms11_col_label"], rotation=35, ha="right")
    axb.set_yticks(range(2), [f"T_ramp {t:g} s" for t in d["ms11_T"]])
    axb.set_ylim(1.6, -0.5)
    axb.set_xlim(-0.6, 3.6)
    axb.set_title("(b) MS11: class, onset shift", loc=S.TITLE_LOC)
    # (c) floors: delay against the Heun dt, both onset readings
    for col, (q, ttl) in enumerate((("cross", "(c) D43 floor, raw first crossing"), ("class", "(c2) D43 floor, classifier onset"))):
        axc = fig.add_subplot(gs[1, col * 2:col * 2 + 2])
        for L in (0, 1, 2):
            mk = S.diagram_mark(f"fs4_l{L}")
            arr = d[f"floor_l{L}_{q}_delay"]
            for i, dt in enumerate(d["floor_dt"]):
                axc.plot([dt] * arr.shape[1], arr[i], ls="none", marker=mk.marker, ms=mk.size, color=mk.colour, mew=mk.width, zorder=3, label=f"level {L}" if i == 0 else None)
        axc.set_xscale("log")
        axc.set_xlabel("Heun dt (tau)")
        axc.set_ylabel("delay (eta_bar)" if col == 0 else "")
        axc.set_title(ttl, loc=S.TITLE_LOC)
        axc.set_ylim((-0.125, 0.055) if q == "cross" else (-1.64, -0.62))       # headroom: the legend row sits above the highest points
        axc.legend(loc="upper center", ncol=3, fontsize=T["legend"], frameon=True, framealpha=0.95, handletextpad=0.2, columnspacing=0.8)
    # (d) floor medians at the other T_ramp (reported only)
    axd = fig.add_subplot(gs[1, 4:6])
    for i, T_ in enumerate(d["ms11_T"]):
        mk = S.diagram_mark(f"w_{i}")
        axd.plot([0, 1, 2], d["floorT_median"][i], ls="-" if i == 0 else "--", lw=0.8, marker=mk.marker, ms=S.FS_SIZES["fs4_floor_T"], color=mk.colour,
                 mfc=mk.colour if mk.filled else "none", mew=mk.width, zorder=3, label=f"T_ramp {T_:g} s: {d['floorT_direction'][i]}")
    axd.set_xticks([0, 1, 2], ["level 0", "level 1", "level 2"])
    axd.set_xlim(-0.4, 2.4)
    axd.set_ylim(-1.95, -0.55)
    axd.set_ylabel("median delay, classifier onset")
    axd.set_title("(d) floor, 10 s and 316 s", loc=S.TITLE_LOC)
    axd.legend(loc="lower center", fontsize=T["legend"], frameon=True, framealpha=0.95)
    lo_, hi_ = int(d["floorT_raw_noonset_seeds"].min()), int(d["floorT_raw_noonset_seeds"].max())
    axd.text(0.5, 0.97, "raw crossing: no onset in " + (f"{lo_}" if lo_ == hi_ else f"{lo_} to {hi_}") + " of 10 seeds", transform=axd.transAxes, ha="center", va="top", fontsize=T["small"])
    # (e) network f_pk against dt per seed: FAIL. 13p (R17): each seed is a filled vertex shape of its own (fs4_s0 to fs4_s2), named in the legend
    axe = fig.add_subplot(gs[2, 0:3])
    psd = S.diagram_mark("fs4_psd")
    for s_ in range(3):
        mk = S.diagram_mark(f"fs4_s{s_}")
        axe.plot(d["net_dt"], d["net_f_pk_hz"][s_], color=mk.colour, ls=mk.linestyle, lw=0.8, marker=mk.marker, ms=mk.size, mew=mk.width, zorder=3, label=f"seed {s_}")
        axe.plot(d["net_dt"][:2], d["net_psd_f_pk_hz"][s_], ls="none", marker=psd.marker, ms=psd.size, color=mk.colour, mew=psd.width, zorder=4, label="open: PSD argmax" if s_ == 0 else None)
    axe.set_xscale("log")
    axe.invert_xaxis()
    axe.set_xlabel("network dt (tau), decreasing")
    axe.set_ylabel("f_pk (Hz)")
    axe.set_title("(e) network f_pk against dt: RB6 " + d["net_status"] + " (not used as evidence)", loc=S.TITLE_LOC, color=S.figure_colour("fail_text"))
    axe.set_ylim(40.0, 125.0)
    axe.legend(loc="upper center", ncol=4, fontsize=T["legend"], frameon=True, framealpha=0.95, handletextpad=0.3, columnspacing=1.0, markerscale=0.8, handlelength=2.0)
    # (f) relative change of f_pk per halving of dt against the 2 percent bound
    axf = fig.add_subplot(gs[2, 3:6])
    for s_ in range(3):
        mk = S.diagram_mark(f"fs4_s{s_}")
        axf.plot([0, 1, 2], d["net_rel_change"][s_], ls="none", marker=mk.marker, ms=mk.size, color=mk.colour, mew=mk.width, zorder=3, label=f"seed {s_}")
    axf.axhline(FS4_RB6_FPK_BOUND, color=tol.colour, ls=tol.linestyle, lw=tol.width + 0.3, label="bound 0.02", zorder=2)
    axf.set_xticks([0, 1, 2], ["1e-3 to 5e-4", "5e-4 to 2.5e-4", "2.5e-4 to 1e-4"])
    axf.set_xlim(-0.5, 2.5)
    axf.set_ylim(-0.03, 0.78)
    axf.set_ylabel("relative change of f_pk")
    axf.set_title("(f) classifier-episode f_pk per halving of dt", loc=S.TITLE_LOC)
    axf.legend(loc="upper left", fontsize=T["legend"], frameon=True, framealpha=0.95, labelspacing=0.5)
    # (g) network classes by V_p, dt and seed (information only). 13p (R17): a lower row and tighter limits (compact)
    axg = fig.add_subplot(gs[3, 0:3])
    for i, row in enumerate(d["netcls_class"]):
        for s_, c in enumerate(row):
            st = S.get(c)
            axg.plot([s_], [i], ls="none", marker=st.marker, ms=S.FS_SIZES["fs4_class"], color=st.colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], zorder=4)
            axg.text(s_ + 0.16, i, c, va="center", fontsize=T["small"])
    axg.set_yticks(range(len(d["netcls_row"])), d["netcls_row"])
    axg.set_xticks(range(3), ["seed 0", "seed 1", "seed 2"])
    axg.set_xlim(-0.35, 2.65)
    axg.set_ylim(len(d["netcls_row"]) - 0.6, -0.4)
    axg.set_title("(g) network class by dt and V_p: information only (G4-C3 stands)", loc=S.TITLE_LOC)
    # (h) V_p comparison, reported only
    axh = fig.add_subplot(gs[3, 3:6])
    v1, v2 = S.diagram_mark("fs4_vp100"), S.diagram_mark("fs4_vp200")
    xx = np.arange(len(d["vp_seed"]), dtype=float)
    axh.plot(xx, d["vp_f100_hz"], ls="none", marker=v1.marker, ms=v1.size, color=v1.colour, zorder=3, label="V_p +-100")
    axh.plot(xx, d["vp_f200_hz"], ls="none", marker=v2.marker, ms=v2.size, color=v2.colour, mew=v2.width, zorder=4, label="V_p +-200")
    axh.set_xticks(xx, [f"{dt:g}\ns{int(s)}".replace("\\n", "\n") for dt, s in zip(d["vp_dt"], d["vp_seed"])])
    axh.set_ylim(40.0, 118.0)
    axh.set_xlim(-0.5, len(xx) - 0.5)
    axh.set_ylabel("f_pk (Hz)")
    axh.set_title("(h) V_p +-100 against +-200 (reported only)", loc=S.TITLE_LOC)
    axh.legend(loc="upper left", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # status block
    axs = fig.add_subplot(gs[4, :])
    axs.axis("off")
    lines = ["Stored status of the RB5 and RB6 rows (A11 table; a failure is shown, not dropped):"] + ["    " + s for s in d["rb_status"]]
    lines += ["FAIL rows of the stored A11 table that touch FS4:"] + ["    " + s for s in fs4_strip_lines(d)]
    for s in (f"Panels (a), (c) and (c2) are rows of the stored A7 table ({d['a7_rows_read']} rows read); (b), (d), (e), (f), (g) and (h) are rows of the stored A11 evaluator file. No series is drawn.",
              "Panels (a) to (d) are noise-free or floored mean-field runs; (e) to (h) are network runs at N = 1e4, 3 seeds, one T_ramp (G4-C1 to G4-C6 apply; the f_pk reading is UNVERIFIED, M11-6)."):
        lines += textwrap.wrap(s, width=135, subsequent_indent="    ")
    lines = [ln for t_ in lines for ln in textwrap.wrap(t_, width=135, subsequent_indent="        ")]
    axs.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=T["status"], linespacing=1.25)
    return _style_text(fig, FS4_FOOTER if draft else "")


def fs4_caption_notes(d: dict) -> tuple:
    """Sentences about what is and is not drawn (13i). Values come from the prepared data; only the wording is typed here."""
    return (
        "Panel (a) draws, for the six stored MS8 headline runs (P2, ref_devalle, T_ramp 120 s, noise-free), the classifier onset with the class marker and the raw first crossing "
        "as a small cross; the two onsets are equal in every run, so the cross lies on the marker. The solver rows are DOP853 (default rtol 1e-10) and Radau (rtol 1e-10); the "
        "Radau comparison covers T_ramp 120 s only (MS11-C5). The cause of the 181 ms is not known (UNVERIFIED).",
        "Panel (b) is the stored MS11 result for delta0 and rtol at T_ramp 10 s and 316.2278 s (class and onset shift in seconds at the 1 ms output grid).",
        "Panels (c) and (c2) draw the stored delay of every D43-floored run (levels 0 to 2, 10 seeds, Heun dt 1e-3 to 1e-4 tau) under both onset readings, as in G6-D3; the delay is the same at "
        "every dt, as the stored table has it (a statement at the 1 ms output resolution, DL-184, DL-190), so the points of one level lie on one another. Panel (d) is reported only (DL-356).",
        "Panels (e) and (f) draw the stored network f_pk at each dt rung and its relative change per halving; (f) uses the classifier-episode reading, and the PSD-argmax reading of the "
        "first halving is drawn as open marks in (e). The 5 to 43 percent of the take-home is the first halving, 1e-3 to 5e-4 tau, of (f); the later halvings are drawn as stored. RB6 network FAILS under both readings (0 of 3 and 2 of 3 seeds pass; the row is FAIL if any evaluable seed fails, DL-348). "
        "Network f_pk results are labelled FAIL and are not used as evidence. Panel (g) and (h) are information only (DL-349).",
        "The network classes in (g) are not evidence of a ramp-driven surge (G4-C3); one seed per cell.",
    )


def make_FS4(res=None, out_dir=None, *, tag_build: bool = False, take_home=FS4_TAKE_HOME, claim_limit_ids=FS4_CLAIM_LIMITS,
             script="scripts/fig_FS4.py", root=None) -> dict:
    """Build FS4 from results/. Returns {'prov', 'paths', 'timing_s', 'drawn_sha256', 'caption'}. tag_build=True needs a clean tree (figprov)."""
    F.require_buildable("FS4")
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "FS4"
    t = {"start": time.perf_counter()}
    raw = load_FS4(res)
    t["load"] = time.perf_counter()
    d = prepare_FS4(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for key, rec in raw["records"].items():
        for r in make_param_table(rec["config"]):
            rows.append({**r, "panel": key, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    cap = CAP.build_caption("FS4", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=[r for r in rows if r["key"] in FS4_CAPTION_KEYS],
                            spectrogram=None, symbol_keys=(), notes=fs4_caption_notes(d), limit_labels=CLAIM_LIMIT_LABELS)
    import matplotlib.pyplot as plt
    fig = _draw_FS4(d, draft=not tag_build)
    out.mkdir(parents=True, exist_ok=True)
    pdf, png = out / "FS4.pdf", out / "FS4.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=S.PNG_DPI)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    cap_path, dig_path = out / "FS4_caption.txt", out / "FS4_drawn_data_sha256.txt"
    from .. import provenance as P
    drawn = drawn_data_sha256(d)
    P.atomic_write_text(cap_path, cap.text + "\n")
    P.atomic_write_text(dig_path, drawn + "\n")
    warnings = []
    for k, rec in raw["records"].items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true")
    prov = F.write_figure_provenance(
        "FS4", script=script, inputs=[res / p for p in FS4_INPUTS], outputs=[pdf, png, cap_path, dig_path], params_rows=rows,
        modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py",
                 "src/mprsurge/plotting/nordlie.py", "src/mprsurge/plotting/figprov.py"],
        configs=["configs/S13.yaml"], claim_limits=cap.claim_limits, input_tables=[{"path": res / FS4_INPUTS[0], "rows": int(len(raw["a7"]))},
                                                                                     {"path": res / FS4_INPUTS[2], "rows": len(raw["a11"])}],
        spectrogram=None, tag_build=tag_build, out_dir=out, root=root, warnings=warnings, wall_time_s=time.perf_counter() - t["start"])
    nordlie_path = out / "FS4_nordlie.md"
    N.write_nordlie(out / "FS4_params.csv", out / "FS4_provenance.json", nordlie_path, root=root)
    t["end"] = time.perf_counter()
    timing = {"load_s": t["load"] - t["start"], "prepare_s": t["prepare"] - t["load"], "draw_s": t["draw"] - t["prepare"],
              "provenance_and_nordlie_s": t["end"] - t["draw"], "total_s": t["end"] - t["start"]}
    return {"prov": prov, "paths": [pdf, png, cap_path, dig_path, out / "FS4_params.csv", out / "FS4_provenance.json", nordlie_path],
            "timing_s": timing, "drawn_sha256": drawn, "caption": cap.text}


# ---- FS3 (13j) -------------------------------------------------------------------------------------------------------------------------------------
# Paths relative to results/. Tables first (docs/ms13_conventions.md M13-12): the stored MS10 evaluator output holds the S9 finite-size classes per N with the no-ramp
# controls and the S10 per-seed shape table (DL-320, DL-321, DL-322); the stored A11 evaluator file holds the S11 noise classes per sigma and T_ramp, the DL-251
# controls and the subgrid numbers carried in (DL-336, DL-387, DL-242); the stored A11 table holds the status rows. No series is opened. Three run records give the
# parameter rows. The registry scripts/ms13_inputs.py INPUTS["FS3"] must name the same files (test).
FS3_INPUTS = (
    "ms10/eval/ms10_eval.json",                       # stored MS10 evaluation: N_sweep (S9, with controls), rb8 (S10 per-seed table), rb1 parts
    "A11/a11_evaluators.json",                        # stored MS11 evaluation: rb2 (S11 gate, beside, controls, subgrid carried in)
    "A11/a11_robustness.csv",                         # stored A11 table: status rows and the FAIL-row strip
    "S9/S9/S9_0000_963e33e3f38a.json",                # run record of an S9 run (parameter rows)
    "S10/S10/S10_0000_8a0cdc4a874d.json",             # run record of an S10 run (parameter rows)
    "S11/S11/S11_0000_bc949a08437f.json",             # run record of an S11 run (parameter rows)
)
FS3_RECORDS = {"S9": FS3_INPUTS[3], "S10": FS3_INPUTS[4], "S11": FS3_INPUTS[5]}
FS3_STRIP_RB = ("RB1", "RB2")                         # FAIL rows that touch FS3: RB2 (Table 7.2 names FS3) and RB1, because FS3 draws the S9 N-sweep records (DL-482 ruling 2; UNVERIFIED reading, as for F2); RB8 heterogeneity is NOT EVALUABLE, not a FAIL row
FS3_STATUS_RB = ("RB1", "RB2", "RB8")                 # status lines of the stored table; RB1 is listed because its N rule is the S9 comparison drawn in (a)
FS3_CAPTION_KEYS = ("model.type", "model.ref_point", "path.name", "path.T_ramp_s", "network.N", "network.het_dist", "noise.sigma", "noise.sigma_factor")
FS3_CLASSES = ("S+", "S-rel", "S-abs", "S-sus", "NS")           # S+, S-rel and S-abs are the frozen Table 2.1 surge classes (DL-336)
FS3_SURGE = ("S+", "S-rel", "S-abs")
FS3_SHAPES = ("lorentzian", "gaussian", "uniform")
FS3_N = (1000, 3000, 10000, 30000)
FS3_SIGMA = (0.5, 1.0, 2.0)
FS3_T = (10.0, 30.0, 120.0, 300.0)
FS3_RB2_KEPT_NEEDED = 8                                         # plan Table 7.2 RB2: headline class kept in >= 8 of 10 seeds

# Ruled (RULED_DL, 13p R13); first proposed for the reviewer's ruling (13j prompt, item B3); every statement is from a logged result (DL numbers in the text) and the numbers are checked against
# the stored tables by tests/test_fig_FS3.py.
FS3_TAKE_HOME = (
    "Finite size (S9, P2, T_ramp 60 s, 10 seeds per N; mean-field class D-tr): the network gives a surge class in 4, 7, 2 and 5 of 10 seeds at "
    "N = 1e3, 3e3, 1e4 and 3e4; the RB1 N rule passes (5 seeds at 3e4 against 2 at 1e4), but no-ramp controls also reach surge classes (2 of 3 at 3e3, 1 of 3 at 1e4 and "
    "at 3e4), so the network classes do not separate ramp-driven from non-ramp records (DL-320, DL-321, DL-325). Heterogeneity shape (S10, N = 1e4, 3 seeds): Gaussian and "
    "uniform give S-abs in 3 of 3 seeds each and the Lorentzian seeds give S-sus, S-abs, S-sus, so RB8 is NOT EVALUABLE and no claim about shape robustness is made "
    "(DL-322, DL-325). Noise (S11, T_ramp 120 s, 10 seeds): the headline class is kept in 8 of 10 seeds at 0.5 sigma (PASS) and 7 of 10 at sigma (FAIL), and "
    "constant-parameter controls reach 7 of 10 at every sigma; the noisy subgrid agrees in 97 of 225 cells against 203 needed (D24 failed) (DL-242, DL-336, DL-387, DL-394)."
)
# Ruled (RULED_DL, 13p R13): the limits of docs/ms13_plan.md section 5 whose right-hand column lists FS3, in the label table of docs/claim_limit_labels.md (MS9(e)-1, MS9(e)-2, MS9(e)-5,
# DL-163-D4, G4-C1 to G4-C5, MS11-C1, MS11-C2, MS11-C7); the plan labels "RB2 FAIL" and "D24 failed" are written in plain words with their DL numbers in the take-home and
# the strip. MS12-C1 lists F1 to F6 and FS6, not FS3. Listed, not decided.
FS3_CLAIM_LIMITS = ("MS11-C7", "MS9(e)-1", "MS9(e)-2", "MS9(e)-5", "DL-163-D4", "G4-C1", "G4-C2", "G4-C3", "G4-C4", "G4-C5", "MS11-C1", "MS11-C2",
                    "RB2 FAIL (plan label)", "D24 failed (plan label)")      # 13p (DL-494 R5, DL-501): the two plan labels the section 5 table lists for FS3
FS3_FOOTER = draft_footer("FS3")


def load_FS3(res=None) -> dict:
    """Open the files of FS3_INPUTS under `res` (default results/) and return their content. Opens nothing else."""
    res = Path(res) if res is not None else results_dir()
    for rel in FS3_INPUTS:
        if not (res / rel).is_file():
            raise F.MissingInputError(f"input file not found: {res / rel}")
    try:
        with open(res / FS3_INPUTS[2], newline="", encoding="utf-8") as fh:
            a11 = list(csv.DictReader(fh))
        return {"ms10": json.loads((res / FS3_INPUTS[0]).read_text(encoding="utf-8")), "evaluators": json.loads((res / FS3_INPUTS[1]).read_text(encoding="utf-8")),
                "a11": a11, "records": {k: json.loads((res / rel).read_text(encoding="utf-8")) for k, rel in FS3_RECORDS.items()}}
    except (OSError, ValueError, KeyError) as exc:
        raise F.MissingInputError(f"an FS3 input cannot be read: {exc}") from exc


def _fs3_counts(classes: dict, where: str) -> np.ndarray:
    unknown = set(classes) - set(FS3_CLASSES)
    if unknown:
        raise DataError(f"{where}: classes {sorted(unknown)} are not in {FS3_CLASSES}")
    return np.array([int(classes.get(c, 0)) for c in FS3_CLASSES])


def _fs3_surge_count(c: np.ndarray) -> int:
    return int(c[[FS3_CLASSES.index(k) for k in FS3_SURGE]].sum())


def prepare_FS3(raw: dict) -> dict:
    """Pure: stored content -> the arrays and numbers that are drawn. Keys are flat names; values are arrays, ints, floats, bools, strings or lists of strings."""
    ms10, ev = raw["ms10"], raw["evaluators"]["evaluators"]["rb2"]
    d: dict = {}
    # (a), (b), (c) S9 finite size: classes per N with the no-ramp controls, f_pk and onset errors against the mean field
    by_n = ms10["N_sweep"]["by_N"]
    if sorted(int(k) for k in by_n) != list(FS3_N):
        raise DataError(f"MS10 N sweep: N values {sorted(by_n)}, expected {FS3_N}")
    d["N"] = np.array(FS3_N)
    cnt, ctl, sur, ctl_sur, ctl_n, seeds = [], [], [], [], [], []
    fmin, fmed, fmax, fn, omin, omed, omax = [], [], [], [], [], [], []
    for n in FS3_N:
        r = by_n[str(n)]
        c = _fs3_counts(r["classes"], f"S9 N {n}")
        cc = _fs3_counts(r["controls"]["classes"], f"S9 controls N {n}")
        if int(c.sum()) != int(r["seeds_present"]) or int(cc.sum()) != int(r["controls"]["n"]):
            raise DataError(f"S9 N {n}: class counts {c.tolist()} / {cc.tolist()} do not sum to the stored seed counts")
        if _fs3_surge_count(c) != int(r["surge_seeds"]) or _fs3_surge_count(cc) != int(r["controls"]["surge"]):
            raise DataError(f"S9 N {n}: surge-class counts disagree with the stored surge_seeds")
        cnt.append(c)
        ctl.append(cc)
        sur.append(int(r["surge_seeds"]))
        ctl_sur.append(int(r["controls"]["surge"]))
        ctl_n.append(int(r["controls"]["n"]))
        seeds.append(int(r["seeds_present"]))
        fe, oe = r["f_pk_rel_err"], r["onset_abs_err_s"]
        fmin.append(float(fe["min"]))
        fmed.append(float(fe["median"]))
        fmax.append(float(fe["max"]))
        fn.append(int(fe["n"]))
        omin.append(float(oe["min"]))
        omed.append(float(oe["median"]))
        omax.append(float(oe["max"]))
    d["s9_count"], d["s9_ctrl_count"] = np.array(cnt), np.array(ctl)
    d["s9_surge"], d["s9_ctrl_surge"], d["s9_ctrl_n"], d["s9_seeds"] = np.array(sur), np.array(ctl_sur), np.array(ctl_n), np.array(seeds)
    d["s9_fpk_err_min"], d["s9_fpk_err_median"], d["s9_fpk_err_max"], d["s9_fpk_err_n"] = np.array(fmin), np.array(fmed), np.array(fmax), np.array(fn)
    d["s9_onset_err_min"], d["s9_onset_err_median"], d["s9_onset_err_max"] = np.array(omin), np.array(omed), np.array(omax)
    d["mf_ref_class"] = str(ms10["N_sweep"]["ref"]["class"])
    d["mf_ref_f_pk_hz"], d["mf_ref_onset_s"] = float(ms10["N_sweep"]["ref"]["f_pk_hz"]), float(ms10["N_sweep"]["ref"]["onset_s"])
    nr = ms10["N_sweep"]["no_worse"]
    d["nrule_count_1e4"], d["nrule_count_3e4"], d["nrule_pass"] = int(nr["count_1e4"]), int(nr["count_3e4"]), bool(nr["pass"])
    if d["nrule_count_1e4"] != int(d["s9_surge"][2]) or d["nrule_count_3e4"] != int(d["s9_surge"][3]):
        raise DataError("RB1 N rule counts disagree with the surge seeds of the stored N sweep")
    # (d) S10 heterogeneity shape: the stored per-seed table
    rb8 = ms10["rb8"]
    if sorted(rb8["per_seed_table"]) != sorted(FS3_SHAPES):
        raise DataError(f"RB8 per-seed table: shapes {sorted(rb8['per_seed_table'])}")
    sc = []
    for sh in FS3_SHAPES:
        rows = sorted(rb8["per_seed_table"][sh], key=lambda r: r["seed"])
        if [r["seed"] for r in rows] != [0, 1, 2]:
            raise DataError(f"RB8 per-seed table, {sh}: seeds {[r['seed'] for r in rows]}")
        sc.append([r["class"] for r in rows])
    d["shape_class"] = sc
    d["shape_ctrl_n"] = int(rb8["lorentzian_controls"]["n"])
    d["shape_ctrl_counts"] = _fs3_counts(rb8["lorentzian_controls"]["classes"], "S10 Lorentzian controls")
    d["rb8_verdict"], d["rb8_reason"] = str(rb8["verdict"]), str(rb8["reason"])
    if d["rb8_verdict"] != "NOT EVALUABLE":
        raise DataError(f"RB8 heterogeneity verdict {d['rb8_verdict']!r} (DL-322 says NOT EVALUABLE)")
    # (e), (f) S11 noise: classes per sigma factor and T_ramp (gate at 120 s), DL-251 controls
    beside = {(float(b["sigma_factor"]), float(b["T_ramp_s"])): b for b in ev["beside"]}
    if sorted(beside) != sorted((s, t) for s in FS3_SIGMA for t in FS3_T):
        raise DataError(f"RB2 beside rows: {sorted(beside)}")
    cnt, kept, gated = [], [], []
    d["noise_sigma"] = np.array([s for s in FS3_SIGMA for t in FS3_T])
    d["noise_T"] = np.array([t for s in FS3_SIGMA for t in FS3_T])
    for s in FS3_SIGMA:
        for t in FS3_T:
            b = beside[(s, t)]
            c = _fs3_counts(b["classes"], f"RB2 sigma {s} T {t}")
            k = _fs3_surge_count(c)
            if k != int(b["kept_primary"]) or int(c.sum()) != 10:
                raise DataError(f"RB2 sigma {s} T {t}: stored kept_primary {b['kept_primary']} against the surge-class count {k} of {int(c.sum())}")
            cnt.append(c)
            kept.append(k)
            gated.append(bool(b["gated"]))
    d["noise_count"], d["noise_kept"], d["noise_gated"] = np.array(cnt), np.array(kept), np.array(gated)
    gate = {float(g["sigma_factor"]): g for g in ev["gate"]}
    d["gate_status"] = [str(gate[s]["status"]) for s in (0.5, 1.0)]
    d["gate_kept"] = np.array([int(gate[s]["kept"]) for s in (0.5, 1.0)])
    if [int(k) for k in d["gate_kept"]] != [int(d["noise_kept"][i]) for i in (2, 6)] or str(ev["status"]) != "FAIL":
        raise DataError("RB2 gate rows disagree with the beside rows or the stored status")
    ctl = {float(c["sigma_factor"]): c for c in ev["controls"]}
    d["noise_ctrl_count"] = np.array([_fs3_counts(ctl[s]["classes"], f"RB2 controls sigma {s}") for s in FS3_SIGMA])
    d["noise_ctrl_kept"] = np.array([int(ctl[s]["kept_primary"]) for s in FS3_SIGMA])
    # (g) the noisy subgrid, carried in from MS9 (not re-evaluated)
    sg = ev["subgrid_carried_in"]
    d["subgrid_agree"], d["subgrid_cells"], d["subgrid_needed"] = int(sg["cells_agree"]), int(sg["cells"]), int(sg["cells_needed"])
    d["subgrid_status"] = str(sg["d24"])
    # status rows and the FAIL-row strip from the stored A11 table
    rows = [r for r in raw["a11"] if r["rb_id"] in FS3_STATUS_RB]
    d["rb_status"] = [f"{r['rb_id']} {r['check_id']}: {r['pass_or_fail']}" for r in rows]
    d["strip"] = [{"rb_id": r["rb_id"], "check_id": r["check_id"], "status": r["pass_or_fail"], "value": r["value"], "threshold": r["threshold"]}
                  for r in raw["a11"] if r["rb_id"] in FS3_STRIP_RB and r["pass_or_fail"] == "FAIL"]
    row = {r["check_id"]: r for r in raw["a11"] if r["rb_id"] == "RB2"}
    if row["headline_class_kept_0.5_sigma"]["pass_or_fail"] != d["gate_status"][0] or row["headline_class_kept_1.0_sigma"]["pass_or_fail"] != d["gate_status"][1]:
        raise DataError("A11 table RB2 gate rows disagree with the stored evaluator file")
    if row["noisy_subgrid_agreement"]["pass_or_fail"] != "FAIL" or d["subgrid_status"] != "FAILED":
        raise DataError("RB2 subgrid row is not FAIL / FAILED as logged (DL-242)")
    if not [r for r in raw["a11"] if r["rb_id"] == "RB8" and r["check_id"] == "heterogeneity" and r["pass_or_fail"] == "NOT EVALUABLE"]:
        raise DataError("A11 table: RB8 heterogeneity is not NOT EVALUABLE (DL-322)")
    return d


def fs3_strip_lines(d: dict) -> list[str]:
    return [f"{r['rb_id']} {r['check_id']}: {r['status']} ({r['value'] or 'value blank in the table'}; threshold {r['threshold'] or 'blank'}) - shown, not dropped" for r in d["strip"]]


def _fs3_label_y(b_: float, h_: float, avoid) -> float:
    """13p (DL-500 R16): the y of a count label inside its segment [b_, b_ + h_]: the middle, unless that lies within S.FS3_GATE_CLEAR of a gate line at `avoid`
    (None: no gate on this bar); then the middle of the larger part of the segment on either side of the line (the upper part on a tie)."""
    y = b_ + h_ / 2
    if avoid is None or abs(y - avoid) >= S.FS3_GATE_CLEAR or not (b_ < avoid < b_ + h_):
        return y
    lower, upper = avoid - b_, b_ + h_ - avoid
    return b_ + lower / 2 if lower > upper else avoid + upper / 2


def _fs3_stack(ax, xs, counts, den, width=0.7, label_min=0.09, avoid=None):
    """Stacked class bars as Rectangles (the stored share is drawn exactly); returns legend handles. avoid: per bar the y of a gate line the count labels keep clear of, or None."""
    from matplotlib.patches import Patch, Rectangle
    bottom = np.zeros(len(xs))
    avoid = [None] * len(xs) if avoid is None else list(avoid)
    handles = []
    for ci, name in enumerate(FS3_CLASSES):
        st = S.get(name)
        h = counts[:, ci] / np.asarray(den, dtype=float).reshape(-1)
        for x_, b_, h_ in zip(xs, bottom, h):
            if h_ > 0:
                ax.add_patch(Rectangle((x_ - width / 2, b_), width, h_, fc=st.colour, ec=S.figure_colour("bar_edge"), lw=0.3, hatch=S.CLASS_HATCH[name], zorder=3))
        handles.append(Patch(fc=st.colour, ec=S.figure_colour("bar_edge"), lw=0.3, hatch=S.CLASS_HATCH[name], label=name))
        for x_, b_, h_, c_, a_ in zip(xs, bottom, h, counts[:, ci], avoid):
            if h_ >= label_min:
                t = ax.text(x_, _fs3_label_y(b_, h_, a_), f"{int(c_)}", ha="center", va="center", fontsize=S.TEXT_SIZES["small"],
                            bbox=dict(boxstyle="square,pad=0.1", fc=S.figure_colour("label_box"), ec="none", alpha=0.8), zorder=5)
                t.set_gid("count_label")
        bottom = bottom + h
    return handles


def _draw_FS3(d: dict, draft: bool):
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    T = S.TEXT_SIZES
    fig = plt.figure(figsize=(7.4, 12.6), constrained_layout=True)
    gs = fig.add_gridspec(4, 6, height_ratios=[2.2, 1.7, 2.3, 2.5])
    tol = S.diagram_mark("tol_band")
    pt = S.diagram_mark("fs3_median")
    # (a) S9: classes per N (10 seeds) beside the no-ramp controls (3), equal weight
    ax = fig.add_subplot(gs[0, 0:4])
    xs = np.arange(4, dtype=float)
    h_a = _fs3_stack(ax, xs - 0.2, d["s9_count"], d["s9_seeds"][:, None].astype(float), width=0.36)
    _fs3_stack(ax, xs + 0.2, d["s9_ctrl_count"], d["s9_ctrl_n"][:, None].astype(float), width=0.36, label_min=0.2)
    for x_, s_, n_, cs, cn in zip(xs, d["s9_surge"], d["s9_seeds"], d["s9_ctrl_surge"], d["s9_ctrl_n"]):
        ax.text(x_ - 0.2, 1.02, f"{int(s_)}/{int(n_)}", ha="center", va="bottom", fontsize=T["status"], fontweight="bold")
        ax.text(x_ + 0.2, 1.02, f"{int(cs)}/{int(cn)}", ha="center", va="bottom", fontsize=T["status"], fontweight="bold", color=S.figure_colour("range_line"))
    ax.set_xticks(np.concatenate([xs - 0.2, xs + 0.2]), [f"ramp\nN {int(n_):g}" for n_ in d["N"]] + [f"no-ramp\nN {int(n_):g}" for n_ in d["N"]])
    ax.set_xlim(-0.6, 3.6)
    ax.set_ylim(0.0, 1.3)
    ax.set_ylabel("share of seeds")
    ax.set_title("(a) S9 (60 s): class per N; bold = surge classes", loc=S.TITLE_LOC)
    ax.legend(handles=h_a, loc="upper left", ncol=5, fontsize=T["legend"], frameon=True, framealpha=0.95, handlelength=1.4, columnspacing=0.8)
    # (b) f_pk relative error against the mean field per N
    axb = fig.add_subplot(gs[0, 4:6])
    for x_, lo, md, hi in zip(xs, d["s9_fpk_err_min"], d["s9_fpk_err_median"], d["s9_fpk_err_max"]):
        axb.plot([x_, x_], [lo, hi], color=S.figure_colour("range_line"), lw=1.0, zorder=2)
        axb.plot([x_], [md], ls="none", marker=pt.marker, ms=pt.size, color=pt.colour, mew=pt.width, zorder=4)
    axb.set_xticks(xs, [f"{int(n_):g}" for n_ in d["N"]])
    axb.set_xlim(-0.5, 3.5)
    axb.set_ylim(-0.04, 0.46)
    axb.set_xlabel("N")
    axb.set_ylabel("f_pk relative error")
    axb.set_title("(b) f_pk error vs MF", loc=S.TITLE_LOC)
    # (c) onset error against the mean field per N
    axc = fig.add_subplot(gs[1, 0:3])
    for x_, lo, md, hi in zip(xs, d["s9_onset_err_min"], d["s9_onset_err_median"], d["s9_onset_err_max"]):
        axc.plot([x_, x_], [lo, hi], color=S.figure_colour("range_line"), lw=1.0, zorder=2)
        axc.plot([x_], [md], ls="none", marker=pt.marker, ms=pt.size, color=pt.colour, mew=pt.width, zorder=4)
    axc.set_xticks(xs, [f"{int(n_):g}" for n_ in d["N"]])
    axc.set_xlim(-0.5, 3.5)
    axc.set_ylim(0.0, 31.0)
    axc.set_xlabel("N")
    axc.set_ylabel("onset error (s)")
    axc.set_title("(c) S9 onset error vs MF", loc=S.TITLE_LOC)
    # (d) S10 shape: the stored per-seed classes; RB8 NOT EVALUABLE
    axd = fig.add_subplot(gs[1, 3:6])
    for i in range(3):
        for j in range(3):
            st = S.get(d["shape_class"][i][j])
            axd.plot([j], [i], ls="none", marker=st.marker, ms=S.POINT_SIZES["fs3_shape"], color=st.colour, mec=S.figure_colour("bar_edge"), mew=S.POINT_EDGE_WIDTH["class"], zorder=4)
            axd.text(j + 0.2, i, d["shape_class"][i][j], va="center", fontsize=T["small"])
    nz = [c for c, k in zip(FS3_CLASSES, d["shape_ctrl_counts"]) for _ in range(int(k))]
    for j, c in enumerate(nz):
        st = S.get(c)
        axd.plot([j], [3.0], ls="none", marker=st.marker, ms=S.POINT_SIZES["fs3_shape"], color=st.colour, mec=S.figure_colour("bar_edge"), mew=S.POINT_EDGE_WIDTH["class"], zorder=4)
        axd.text(j + 0.2, 3.0, c, va="center", fontsize=T["small"])
    axd.set_yticks(range(4), list(FS3_SHAPES) + ["lorentzian, no-ramp (counts)"])
    axd.set_xticks(range(3), ["seed 0", "seed 1", "seed 2"])
    axd.set_xlim(-0.5, 2.9)
    axd.set_ylim(3.6, -0.5)
    axd.set_title("(d) S10 shape: RB8 " + d["rb8_verdict"], loc=S.TITLE_LOC, color=S.figure_colour("fail_text"))
    # (e) S11 noise: classes per sigma factor and T_ramp; the 120 s bars are the RB2 gate. 13p (R16): no count label lies on the dashed gate line
    axe = fig.add_subplot(gs[2, 0:4])
    xe = np.arange(12, dtype=float) + np.repeat(np.arange(3), 4) * 0.5
    gate_y = FS3_RB2_KEPT_NEEDED / 10.0
    _fs3_stack(axe, xe, d["noise_count"], np.full((12, 1), 10.0), width=0.8, label_min=0.12, avoid=[gate_y if g else None for g in d["noise_gated"]])
    for x_, k, g in zip(xe, d["noise_kept"], d["noise_gated"]):
        axe.text(x_, 1.02, f"{int(k)}", ha="center", va="bottom", fontsize=T["status"], fontweight="bold")
        if g:
            axe.text(x_, 1.1, d["gate_status"][0 if x_ < 4 else 1], ha="center", va="bottom", fontsize=T["status"], fontweight="bold",
                     color=S.figure_colour("fail_text") if (x_ > 4) else S.figure_colour("text_dark"))
            axe.plot([x_ - 0.4, x_ + 0.4], [gate_y] * 2, color=S.figure_colour("gate_line"), ls=tol.linestyle, lw=tol.width + 0.4, zorder=6, gid="rb2_gate")
    axe.set_xticks(xe, [f"{t:g}\nx{s_:g}" for t, s_ in zip(d["noise_T"], d["noise_sigma"])])
    axe.set_xlabel("T_ramp (s) and sigma factor")
    axe.set_ylim(0.0, 1.26)
    axe.set_xlim(-0.6, float(xe[-1]) + 0.6)
    axe.set_ylabel("share of 10 seeds")
    axe.set_title("(e) S11 noise: classes; dashed = RB2 gate (>= 8 of 10)", loc=S.TITLE_LOC, color=S.figure_colour("fail_text"))
    # (f) the DL-251 constant-parameter controls
    axf = fig.add_subplot(gs[2, 4:6])
    xf = np.arange(3, dtype=float)
    _fs3_stack(axf, xf, d["noise_ctrl_count"], np.full((3, 1), 10.0), width=0.7, label_min=0.12)
    for x_, k in zip(xf, d["noise_ctrl_kept"]):
        axf.text(x_, 1.02, f"{int(k)}", ha="center", va="bottom", fontsize=T["status"], fontweight="bold")
    axf.set_xticks(xf, [f"x {s_:g}" for s_ in FS3_SIGMA])
    axf.set_xlim(-0.6, 2.6)
    axf.set_ylim(0.0, 1.14)
    axf.set_xlabel("sigma factor")
    axf.set_title("(f) no-ramp controls", loc=S.TITLE_LOC)
    # (g) the noisy subgrid, carried in from MS9
    axg = fig.add_subplot(gs[3, 0:2])
    axg.add_patch(Rectangle((-0.3, 0), 0.6, d["subgrid_agree"], fc=S.figure_colour("subgrid_bar"), ec=S.figure_colour("bar_edge"), lw=0.4, zorder=3))
    axg.axhline(d["subgrid_needed"], color=tol.colour, ls=tol.linestyle, lw=tol.width + 0.3, label="needed (D24, 90 percent)", zorder=2)
    axg.text(0.0, d["subgrid_agree"] / 2, f"{d['subgrid_agree']} of {d['subgrid_cells']}", ha="center", va="center", fontsize=T["note"],
             bbox=dict(boxstyle="square,pad=0.15", fc=S.figure_colour("label_box"), ec="none", alpha=0.85), zorder=5)
    axg.set_xlim(-0.8, 0.8)
    axg.set_ylim(0, d["subgrid_cells"] * 1.25)
    axg.set_xticks([0], ["cells that agree"])
    axg.set_ylabel(f"cells (of {d['subgrid_cells']})")
    axg.set_title("(g) noisy subgrid: " + d["subgrid_status"], loc=S.TITLE_LOC, color=S.figure_colour("fail_text"))
    axg.legend(loc="upper right", fontsize=T["legend"], frameon=True, framealpha=0.95)
    # status block
    axs = fig.add_subplot(gs[3, 2:6])
    axs.axis("off")
    lines = ["Stored status of the RB1, RB2 and RB8 rows (A11 table; a failure is shown, not dropped):"] + ["    " + s for s in d["rb_status"]]
    lines += ["FAIL rows of the stored A11 table that touch FS3:"] + ["    " + s for s in fs3_strip_lines(d)]
    lines += ["Panels (a) to (d) are network runs (N = 1e4 unless N is varied) at T_ramp 60 s; (e) and (f) are mean-field runs with noise (S11, DL-336). All panels are rows of the "
              "stored MS10 evaluator file and the stored A11 files; no series is drawn. A surge class here is S+, S-rel or S-abs (frozen Table 2.1; S-rel is not ramp evidence in mode N, MS9(e)-2)."]
    lines = [ln for t_ in lines for ln in textwrap.wrap(t_, width=88, subsequent_indent="        ")]
    axs.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=T["status"], linespacing=1.25)
    return _style_text(fig, FS3_FOOTER if draft else "")


def fs3_caption_notes(d: dict) -> tuple:
    """Sentences about what is and is not drawn (13j). Values come from the prepared data; only the wording is typed here."""
    return (
        "Panel (a) draws, per N, the stored classes of the 10 S9 ramp seeds (P2, T_ramp 60 s, mean-field class " + d["mf_ref_class"] + ") beside the 3 no-ramp control records; the bold number above "
        "each bar is the count of surge classes (S+, S-rel, S-abs). The RB1 N rule (surge seeds at N = 3e4 no fewer than at 1e4: " + f"{d['nrule_count_3e4']} against {d['nrule_count_1e4']}" + ") is met; the "
        "network classes at N = 1e4 and 3e4 do not reproduce the mean-field classes (G4-C1) and the controls reach surge classes (G4-C3). Panels (b) and (c) are the stored min, median and max "
        "of the f_pk relative error and of the absolute onset error against the mean-field companion, per N (seeds with an undefined value are not counted: " + ", ".join(str(int(x)) for x in d["s9_fpk_err_n"]) + " seeds in (b)).",
        "Panel (d) is the stored per-seed class table of the three heterogeneity shapes (S10, N = 1e4, P2, T_ramp 60 s); the Lorentzian seeds do not share one Table 2.1 correspondence class, "
        "so RB8 (heterogeneity part) is NOT EVALUABLE and no verdict is drawn (DL-322; G4-C5: no claim about heterogeneity-shape robustness); the Lorentzian no-ramp controls are listed by class count, not by seed, "
        "and the other S10 control records cannot be identified from the stored tables and are not drawn.",
        "Panels (e) and (f) are the stored RB2 class counts of S11 per sigma factor (0.5, 1, 2 times sigma = 0.0624, checked and not confirmed, G4-C4) and T_ramp; the bars at T_ramp 120 s with a dashed "
        "line are the gate (kept in at least 8 of 10 seeds at 0.5 sigma and sigma; 2 sigma is reported only); the no-ramp controls of (f) are the post-hoc amendment of DL-251 and feed no gate. "
        "Panel (g) is the subgrid agreement carried in from MS9 and not re-evaluated here (D24 failed, DL-242). The FAIL rows listed are the RB2 rows and, because panels (a) to (c) draw the S9 N-sweep records, the RB1 rows "
        "(UNVERIFIED reading); they are shown, not dropped. "
    )


def make_FS3(res=None, out_dir=None, *, tag_build: bool = False, take_home=FS3_TAKE_HOME, claim_limit_ids=FS3_CLAIM_LIMITS,
             script="scripts/fig_FS3.py", root=None) -> dict:
    """Build FS3 from results/. Returns {'prov', 'paths', 'timing_s', 'drawn_sha256', 'caption'}. tag_build=True needs a clean tree (figprov)."""
    F.require_buildable("FS3")
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "FS3"
    t = {"start": time.perf_counter()}
    raw = load_FS3(res)
    t["load"] = time.perf_counter()
    d = prepare_FS3(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for key, rec in raw["records"].items():
        for r in make_param_table(rec["config"]):
            rows.append({**r, "panel": key, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    cap = CAP.build_caption("FS3", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=[r for r in rows if r["key"] in FS3_CAPTION_KEYS],
                            spectrogram=None, symbol_keys=(), notes=fs3_caption_notes(d), limit_labels=CLAIM_LIMIT_LABELS)
    import matplotlib.pyplot as plt
    fig = _draw_FS3(d, draft=not tag_build)
    out.mkdir(parents=True, exist_ok=True)
    pdf, png = out / "FS3.pdf", out / "FS3.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=S.PNG_DPI)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    cap_path, dig_path = out / "FS3_caption.txt", out / "FS3_drawn_data_sha256.txt"
    from .. import provenance as P
    drawn = drawn_data_sha256(d)
    P.atomic_write_text(cap_path, cap.text + "\n")
    P.atomic_write_text(dig_path, drawn + "\n")
    warnings = []
    for k, rec in raw["records"].items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true")
    prov = F.write_figure_provenance(
        "FS3", script=script, inputs=[res / p for p in FS3_INPUTS], outputs=[pdf, png, cap_path, dig_path], params_rows=rows,
        modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py",
                 "src/mprsurge/plotting/nordlie.py", "src/mprsurge/plotting/figprov.py"],
        configs=["configs/base.yaml", "configs/ms10/ms10_net.yaml", "configs/ms11/ms11_mfn.yaml"], claim_limits=cap.claim_limits,
        input_tables=[{"path": res / FS3_INPUTS[2], "rows": len(raw["a11"])}],
        spectrogram=None, tag_build=tag_build, out_dir=out, root=root, warnings=warnings, wall_time_s=time.perf_counter() - t["start"])
    nordlie_path = out / "FS3_nordlie.md"
    N.write_nordlie(out / "FS3_params.csv", out / "FS3_provenance.json", nordlie_path, root=root)
    t["end"] = time.perf_counter()
    timing = {"load_s": t["load"] - t["start"], "prepare_s": t["prepare"] - t["load"], "draw_s": t["draw"] - t["prepare"],
              "provenance_and_nordlie_s": t["end"] - t["draw"], "total_s": t["end"] - t["start"]}
    return {"prov": prov, "paths": [pdf, png, cap_path, dig_path, out / "FS3_params.csv", out / "FS3_provenance.json", nordlie_path],
            "timing_s": timing, "drawn_sha256": drawn, "caption": cap.text}


# ---- F6 (13j) --------------------------------------------------------------------------------------------------------------------------------------
# Paths relative to results/. Tables first (docs/ms13_conventions.md M13-12): the stored A9 table v2 holds the failure labels a to h per map cell, the stored A10 table the
# negative controls NC1 to NC3 per T_ramp (the NC1 map cells and the NC1 network run included), the stored A7 S6 table the P3, P4a and P4b rows (with the P2 comparators),
# the stored A11 table the status rows. No series is opened and no example trace is drawn. Three run records give the parameter rows. The registry
# scripts/ms13_inputs.py INPUTS["F6"] must name the same files (test).
F6_INPUTS = (
    "A9/a9_regime_map_v2.parquet",                    # 1,226 rows: map 1 (900), map 2 (325), the headline row; failure_label, failure_labels_all (DL-243, DL-244, DL-249, DL-265)
    "A10/a10_controls.csv",                           # 58 rows: NC1 (mean-field headline cell 13, mode-N summary 13, map cells 5, network run 1), NC2 13, NC3 13 (DL-252)
    "A7/a7_s6_metrics.parquet",                       # 24 rows: S6 P3 (12), P4a (4), P4b (4), the P2 comparators (4) (DL-235)
    "A11/a11_robustness.csv",                         # stored A11 table: status rows and the FAIL-row strip
    "S6/S6_P3/S6_P3_0000_7570e8b706d0.json",          # run record of an S6 P3 run (parameter rows)
    "S12/NC1/NC1_0000_8b0cbcd28f18.json",             # run record of an NC1 mean-field run (parameter rows)
    "S12/NC1_net/NC1_net_0000_1a8cb131785a.json",     # run record of the NC1 network run (parameter rows)
)
F6_RECORDS = {"S6_P3": F6_INPUTS[4], "S12_NC1": F6_INPUTS[5], "S12_NC1_net": F6_INPUTS[6]}
F6_STRIP_RB = ("G7",)                                 # FAIL rows of the stored A11 table that touch F6: G7 (NC1 network S+). Table 7.2 names F6 for RB7, which has no A11 row (UNVERIFIED reading)
F6_CAPTION_KEYS = ("model.type", "model.ref_point", "path.name", "path.T_ramp_s", "network.N", "model.I_drive", "noise.sigma")
F6_LABELS = ("a", "b", "c", "d", "e", "f", "g", "h")
# wording of the labels: the short forms listed in docs/claim_limit_labels.md (second table, DL-482), each beside its verbatim source; label (c) is shown as the MS9(e)-3 short form
F6_LABEL_WORDS = {k: v[0] for k, v in A9_LABELS.items()}
F6_T = tuple(float(x) for x in (1.0, 1.7782794100389228, 3.1622776601683795, 5.623413251903491, 10.0, 17.78279410038923, 31.622776601683793, 56.23413251903491, 100.0,
                                177.82794100389228, 316.22776601683796, 562.341325190349, 1000.0))
F6_S6_T = (10.0, 30.0, 120.0, 300.0)
F6_S6_ROWS = (("P3", 0.5, "P3, I_amp 0.5"), ("P3", 1.0, "P3, I_amp 1"), ("P3", 2.0, "P3, I_amp 2"), ("P4a", None, "P4a"), ("P4b", None, "P4b"), ("P2", None, "P2 (comparators)"))

# Ruled (RULED_DL, 13p R13); first proposed for the reviewer's ruling (13j prompt, item B3); every statement is from a logged result (DL numbers in the text) and the numbers are checked against
# the stored tables by tests/test_fig_F6.py.
F6_TAKE_HOME = (
    "The 169 non-surge cells of map 1 (140) and map 2 (29) each carry an A9 failure label (primary label a 48, c 32, f 24, g 64, h 1); the labels are our "
    "operational rules and label (c) is a flag, not a demonstrated cause (DL-244, DL-249, DL-270). The mean-field negative control NC1 is D-none at 13 of 13 T_ramp and at the 5 map "
    "cells, NC3 is D-none at 13 of 13, and NC2 is D-tr at 13 of 13 T_ramp with I = 0 and with I = 1 (DL-221, DL-252); the NC1 network run (N = 1e4, mode N, 120 s, 1 seed) is S+ "
    "(provisional), so G7 is NOT PASSED (DL-220, DL-221, DL-228). All 20 pre-registered S6 rows (P3 at I_amp 0.5, 1 and 2, P4a and P4b at T_ramp 10, 30, 120 and 300 s) are D-tr, so "
    "a surge is not found under P3 only (DL-235)."
)
# Ruled (RULED_DL, 13p R13): the limits of docs/ms13_plan.md section 5 whose right-hand column lists F6, in the label table of docs/claim_limit_labels.md (MS9(e)-1, MS9(e)-3 to MS9(e)-6, DL-163-D1,
# DL-163-D2, G4-C3, MS11-C7, MS12-C1). 13o (DL-494 R5, DL-495): the plan label G7 not passed is carried with its definition, and MS9(e)-6 is carried as not applicable
# (the R5 pattern). Listed, not decided.
F6_CLAIM_LIMITS = ("MS11-C7", "MS12-C1", "MS9(e)-1", "MS9(e)-3", "MS9(e)-4", "MS9(e)-5", "MS9(e)-6", "DL-163-D1", "DL-163-D2", "G4-C3", "G7 not passed (plan label)")
F6_NOT_APPLICABLE = {"MS9(e)-6": "neither the D31 boundary nor J_exit,static, the exit extension of P3 and P4, is drawn"}
F6_FOOTER = draft_footer("F6")


def load_F6(res=None) -> dict:
    """Open the files of F6_INPUTS under `res` (default results/) and return their content. Opens nothing else."""
    res = Path(res) if res is not None else results_dir()
    for rel in F6_INPUTS:
        if not (res / rel).is_file():
            raise F.MissingInputError(f"input file not found: {res / rel}")
    try:
        import pandas as pd
        with open(res / F6_INPUTS[3], newline="", encoding="utf-8") as fh:
            a11 = list(csv.DictReader(fh))
        return {"a9": pd.read_parquet(res / F6_INPUTS[0]), "a10": pd.read_csv(res / F6_INPUTS[1]), "s6": pd.read_parquet(res / F6_INPUTS[2]), "a11": a11,
                "records": {k: json.loads((res / rel).read_text(encoding="utf-8")) for k, rel in F6_RECORDS.items()}}
    except (OSError, ValueError, KeyError, ImportError) as exc:
        raise F.MissingInputError(f"an F6 input cannot be read: {exc}") from exc


def prepare_F6(raw: dict) -> dict:
    """Pure: stored content -> the arrays and numbers that are drawn. Keys are flat names; values are arrays, ints, floats, bools, strings or lists of strings."""
    a9, a10, s6 = raw["a9"], raw["a10"], raw["s6"]
    d: dict = {}
    # (a) A9 failure labels, primary and any-label counts, per map; surge-class cells carry no label
    if len(a9) != 1226 or sorted(a9["map"].astype(str).unique()) != ["1", "2", "headline"]:
        raise DataError(f"A9 table v2: {len(a9)} rows, maps {sorted(a9['map'].astype(str).unique())}")
    if bool(a9["unlabelled_a_h"].any()):
        raise DataError("A9 table v2: a cell is unlabelled under a to h (DL-249 says none)")
    prim, anyl, surge, nons = [], [], [], []
    for m in ("1", "2"):
        sub = a9[a9["map"].astype(str) == m]
        sg = sub[sub["class"] == "D-tr"]
        ns = sub[sub["class"] != "D-tr"]
        if (sg["failure_label"] != "").any():
            raise DataError(f"A9 map {m}: a surge-class cell carries a failure label")
        if (ns["failure_label"] == "").any():
            raise DataError(f"A9 map {m}: a non-surge cell has no failure label")
        prim.append([int((ns["failure_label"] == L).sum()) for L in F6_LABELS])
        anyl.append([int(ns["failure_labels_all"].astype(str).apply(lambda s, L=L: L in s.split(",")).sum()) for L in F6_LABELS])
        surge.append(int(len(sg)))
        nons.append(int(len(ns)))
        if sum(prim[-1]) != nons[-1]:
            raise DataError(f"A9 map {m}: primary label counts {prim[-1]} do not sum to the {nons[-1]} non-surge cells")
    d["label_primary"], d["label_any"] = np.array(prim), np.array(anyl)
    d["map_surge"], d["map_nonsurge"] = np.array(surge), np.array(nons)
    # (b) NC1 to NC3 against T_ramp
    mf = a10[(a10["control"] == "NC1") & (a10["row_type"] == "mean_field_headline_cell")].sort_values("T_ramp_s")
    mn = a10[(a10["control"] == "NC1") & (a10["row_type"] == "mode_N_summary_per_window")].sort_values("T_ramp_s")
    n2 = a10[(a10["control"] == "NC2") & (a10["row_type"] == "per_T_ramp") & (~a10["supplementary"].astype(bool))].sort_values("T_ramp_s")
    n3 = a10[(a10["control"] == "NC3") & (a10["row_type"] == "per_T_ramp")].sort_values("T_ramp_s")
    for name, t in (("NC1 mean field", mf), ("NC1 mode N", mn), ("NC2", n2), ("NC3", n3)):
        if not np.allclose(t["T_ramp_s"].to_numpy(float), np.array(F6_T), rtol=1e-6, atol=0):
            raise DataError(f"A10 {name}: T_ramp values {t['T_ramp_s'].tolist()}")
    d["nc_T"] = np.array(F6_T)
    d["nc1_mf_class"] = [str(x) for x in mf["class"]]
    d["nc2_I0_class"], d["nc2_I1_class"] = [str(x) for x in n2["class"]], [str(x) for x in n2["class_I1"]]
    d["nc3_class"] = [str(x) for x in n3["class"]]
    d["nc1_modeN_count"] = np.array([_fs3_counts(json.loads(s), "NC1 mode N") for s in mn["class_counts"]])
    d["nc1_modeN_window_s"] = mn["W_s"].to_numpy(float)
    d["nc1_modeN_n"] = mn["n_seeds"].to_numpy(float).astype(int)
    if d["nc1_modeN_count"].sum(axis=1).tolist() != d["nc1_modeN_n"].tolist():
        raise DataError("A10 NC1 mode N: class counts do not sum to the seed counts")
    cells = a10[(a10["control"] == "NC1") & (a10["row_type"] == "map_cell")]
    d["nc1_cells_class"] = [str(x) for x in cells["class"]]
    net = a10[(a10["control"] == "NC1") & (a10["row_type"] == "network_run")]
    if len(net) != 1:
        raise DataError(f"A10 NC1 network run: {len(net)} rows")
    d["nc1_net_class"], d["nc1_net_expected"] = str(net["class"].iloc[0]), str(net["expected_class"].iloc[0])
    d["nc1_net_as_expected"], d["nc1_net_provisional"], d["g7_status"] = bool(net["as_expected"].iloc[0]), str(net["provisional"].iloc[0]), str(net["g7_status"].iloc[0])
    if d["nc1_net_class"] != "S+" or d["nc1_net_as_expected"] or not d["g7_status"].startswith("not passed"):
        raise DataError(f"A10 NC1 network run: class {d['nc1_net_class']}, as_expected {d['nc1_net_as_expected']}, G7 {d['g7_status']!r} (DL-220, DL-228 say S+, not as expected, not passed)")
    # (d), (e) S6 and the P2 comparators against T_ramp
    on, fp, cl = [], [], []
    for path, amp, _lab in F6_S6_ROWS:
        if path == "P3":
            sub = s6[(s6["family"] == "S6_P3") & (s6["I_amp"].astype(float) == amp)]
        elif path == "P4a":
            sub = s6[s6["family"] == "S6_P4a"]
        elif path == "P4b":
            sub = s6[s6["family"] == "S6_P4b"]
        else:
            sub = s6[s6["family"].isin(["S6_P2ref", "p2_linear", "S5ramp"])]
        sub = sub.sort_values("T_ramp_s")
        if sub["T_ramp_s"].tolist() != list(F6_S6_T):
            raise DataError(f"A7 S6 table, {path} {amp}: T_ramp values {sub['T_ramp_s'].tolist()}")
        on.append(sub["onset_s"].to_numpy(float))
        fp.append(sub["f_pk_hz"].to_numpy(float))
        cl.append([str(x) for x in sub["class"]])
    d["s6_label"] = [r[2] for r in F6_S6_ROWS]
    d["s6_T"] = np.array(F6_S6_T)
    d["s6_onset_s"], d["s6_f_pk_hz"], d["s6_class"] = np.array(on), np.array(fp), cl
    d["s6_n_prereg"] = int((s6["row_kind"] == "S6_pre_registered").sum())
    d["s6_prereg_all_Dtr"] = bool((s6.loc[s6["row_kind"] == "S6_pre_registered", "class"] == "D-tr").all())
    # status rows and the FAIL-row strip from the stored A11 table
    d["rb_status"] = [f"{r['rb_id']} {r['check_id']}: {r['pass_or_fail']}" for r in raw["a11"] if r["rb_id"] in ("G7",)]
    d["strip"] = [{"rb_id": r["rb_id"], "check_id": r["check_id"], "status": r["pass_or_fail"], "value": r["value"], "threshold": r["threshold"], "source": r["source"]}
                  for r in raw["a11"] if r["rb_id"] in F6_STRIP_RB and r["pass_or_fail"] == "FAIL"]
    d["rb7_rows"] = int(sum(1 for r in raw["a11"] if r["rb_id"] == "RB7"))
    if not d["strip"]:
        raise DataError("A11 table: the G7 row is not FAIL (DL-228 says NOT PASSED)")
    return d


def f6_column_labels(raw: dict) -> dict:
    """13o (DL-494 R10): the tick labels of panel (c), read from the stored A10 rows and the stored NC1 network record. The network run gets its own column at its
    stored condition (reference point, Delta, tau_d, path, T_ramp, N); the A10 network row must name the same Delta, tau_d and T_ramp as the record."""
    a10 = raw["a10"]
    cells = a10[(a10["control"] == "NC1") & (a10["row_type"] == "map_cell")]
    net = a10[(a10["control"] == "NC1") & (a10["row_type"] == "network_run")]
    c = raw["records"]["S12_NC1_net"]["config"]
    m, pth = c["model"], c["path"]
    if len(net) != 1 or float(net["Delta"].iloc[0]) != float(m["Delta"]) or float(net["tau_d_ms"].iloc[0]) != float(m["tau_d_ms"]) \
            or float(net["T_ramp_s"].iloc[0]) != float(pth["T_ramp_s"]):
        raise DataError("A10 NC1 network row and the stored NC1 network record name different conditions")
    return {"cells": [f"Delta {float(D):.3g}\ntau_d {float(t):.3g} ms" for D, t in zip(cells["Delta"], cells["tau_d_ms"])],
            "network": f"network run, N = {int(c['network']['N'])}\n{m['ref_point']}: Delta {float(m['Delta']):g}, tau_d {float(m['tau_d_ms']):g} ms\n"
                       f"{pth['name']}, T_ramp {float(pth['T_ramp_s']):g} s"}


def _coincident_rows(rows) -> list:
    """Groups (two or more) of drawn rows whose stored values are identical (R10: drawn at their stored positions, told apart by marks, and named in a note)."""
    groups: list = []
    for i, r in enumerate(rows):
        for g in groups:
            if np.array_equal(np.asarray(rows[g[0]], float), np.asarray(r, float), equal_nan=True):
                g.append(i)
                break
        else:
            groups.append([i])
    return [g for g in groups if len(g) > 1]


def f6_strip_lines(d: dict) -> list[str]:
    return [f"{r['rb_id']} {r['check_id']}: {r['status']} (NC1 network run S+; {r['source']}) - shown, not dropped" for r in d["strip"]]


def _draw_F6(d: dict, draft: bool, columns: dict | None = None):
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    fig = plt.figure(figsize=(7.4, 10.2), constrained_layout=True)
    gs = fig.add_gridspec(4, 6, height_ratios=[2.3, 2.3, 2.2, 1.1])
    # (a) A9 failure labels on the non-surge cells: primary (filled) and any-label (open) counts per label, map 1 and map 2
    ax = fig.add_subplot(gs[0, 0:6])
    xs = np.arange(len(F6_LABELS), dtype=float)
    w = 0.19
    for k, (m, off, fc) in enumerate((("map 1", -1.5 * w, S.figure_colour("map1_fill")), ("map 2", -0.5 * w, S.figure_colour("map2_fill")))):
        for x_, c in zip(xs, d["label_primary"][k]):
            ax.add_patch(Rectangle((x_ + off - w / 2, 0), w, c, fc=fc, ec=S.figure_colour("bar_edge_dark"), lw=0.4, zorder=3))
            ax.text(x_ + off, c + 1.2, f"{int(c)}", ha="center", va="bottom", fontsize=S.TEXT_SIZES["small"])
    for k, (m, off) in enumerate((("map 1", 0.5 * w), ("map 2", 1.5 * w))):
        for x_, c in zip(xs, d["label_any"][k]):
            ax.add_patch(Rectangle((x_ + off - w / 2, 0), w, c, fc=S.figure_colour("open_fill"), ec=S.figure_colour("bar_edge_dark"), lw=0.8, hatch=S.figure_hatch("map1_any" if k == 0 else "map2_any"), zorder=3))
            ax.text(x_ + off, c + 1.2, f"{int(c)}", ha="center", va="bottom", fontsize=S.TEXT_SIZES["small"])
    ax.set_xticks(xs, [f"{L}: {F6_LABEL_WORDS[L]}" for L in F6_LABELS], rotation=18, ha="right")
    ax.set_xlim(-0.6, len(F6_LABELS) - 0.4)
    ax.set_ylim(0, 92)
    ax.set_ylabel("non-surge cells")
    ax.set_title(f"(a) A9 failure labels on the {int(d['map_nonsurge'].sum())} non-surge cells (surge-class D-tr cells: map 1 {int(d['map_surge'][0])}, map 2 {int(d['map_surge'][1])}, no label)", loc=S.TITLE_LOC)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=S.figure_colour("map1_fill"), ec=S.figure_colour("bar_edge_dark"), lw=0.4, label="map 1, primary"), Patch(fc=S.figure_colour("map2_fill"), ec=S.figure_colour("bar_edge_dark"), lw=0.4, label="map 2, primary"),
                       Patch(fc=S.figure_colour("open_fill"), ec=S.figure_colour("bar_edge_dark"), lw=0.8, hatch=S.figure_hatch("map1_any"), label="map 1, any label"), Patch(fc=S.figure_colour("open_fill"), ec=S.figure_colour("bar_edge_dark"), lw=0.8, hatch=S.figure_hatch("map2_any"), label="map 2, any label")],
              loc="upper left", ncol=4, fontsize=S.TEXT_SIZES["legend"], frameon=True, framealpha=0.95)
    # (b) negative controls against T_ramp
    axb = fig.add_subplot(gs[1, 0:6])
    rows = [("NC1 mean field", d["nc1_mf_class"]), ("NC1 mode N (10 seeds)", None), ("NC2, I = 0", d["nc2_I0_class"]), ("NC2, I = 1", d["nc2_I1_class"]), ("NC3", d["nc3_class"])]
    for i, (lab, cls) in enumerate(rows):
        for j in range(13):
            if cls is None:
                cc = d["nc1_modeN_count"][j]
                top = FS3_CLASSES[int(np.argmax(cc))]
                st = S.get(top)
                axb.plot([j], [i], ls="none", marker=st.marker, ms=S.POINT_SIZES["f6_control"], color=st.colour, mec=S.figure_colour("bar_edge"), mew=S.POINT_EDGE_WIDTH["class"], zorder=4)
                rest = [f"{c} {int(k)}" for c, k in zip(FS3_CLASSES, cc) if k > 0 and c != top]
                if rest:
                    axb.text(j, i + 0.34, "\n".join(rest), ha="center", va="top", fontsize=S.TEXT_SIZES["small"])
            else:
                st = S.get(cls[j])
                axb.plot([j], [i], ls="none", marker=st.marker, ms=S.POINT_SIZES["f6_control"], color=st.colour, mec=S.figure_colour("bar_edge"), mew=S.POINT_EDGE_WIDTH["class"], zorder=4)
    axb.set_yticks(range(5), [r[0] for r in rows])
    axb.set_xticks(range(13), [f"{t:.3g}" for t in d["nc_T"]])
    axb.set_xlabel("T_ramp (s)")
    axb.set_ylim(4.75, -0.5)
    axb.set_xlim(-0.6, 12.6)
    axb.set_title("(b) negative controls NC1 to NC3 against T_ramp (classes; mode-N rows show the modal class and the other classes as counts)", loc=S.TITLE_LOC)
    # (c) NC1 at the 5 map cells and the NC1 network run; 13o (DL-494 R10): the network run has its own column at its stored condition, not the column of a map cell
    axc = fig.add_subplot(gs[2, 0:2])
    cols = columns or {"cells": [f"cell {j + 1}" for j in range(len(d["nc1_cells_class"]))], "network": "network run\n(condition not given)"}
    for j, c in enumerate(d["nc1_cells_class"]):
        st = S.get(c)
        axc.plot([j], [0], ls="none", marker=st.marker, ms=S.POINT_SIZES["f6_control"], color=st.colour, mec=S.figure_colour("bar_edge"), mew=S.POINT_EDGE_WIDTH["class"], zorder=4)
    x_net = len(d["nc1_cells_class"]) + 0.6
    axc.axvline(x_net - 0.8, color=S.F6_MARKS["separator"], lw=S.F6_MARKS["line_width"], ls=":", zorder=1)
    st = S.get(d["nc1_net_class"])
    axc.plot([x_net], [0], ls="none", marker=st.marker, ms=S.POINT_SIZES["f6_network_run"], color=st.colour, mec=S.figure_colour("bar_edge"), mew=S.POINT_EDGE_WIDTH["class_large"], zorder=4)
    axc.text(x_net, 0.42, f"{d['nc1_net_class']} (expected\n{d['nc1_net_expected']}): G7\nNOT PASSED", ha="center", va="top", fontsize=S.TEXT_SIZES["small"], color=S.figure_colour("fail_text"))
    axc.set_yticks([0], ["stored class"])
    axc.set_xticks(list(range(len(cols["cells"]))) + [x_net], cols["cells"] + [cols["network"]], rotation=90)
    axc.set_xlim(-0.6, x_net + 0.9)
    axc.set_ylim(1.3, -0.6)
    axc.set_title("(c) NC1: 5 map cells (mean field) | network run", loc=S.TITLE_LOC, color=S.figure_colour("fail_text"))
    # (d), (e) S6 and the P2 comparators against T_ramp; 13o (DL-494 R10): the three P3 amplitudes are concentric marks (fill and size), P4b is drawn larger than P2, so rows with
    # identical stored values stay visible at their stored positions; a note names every group of identical rows
    for col, key, ttl, yl in ((2, "s6_onset_s", "(d) onset, P3, P4a, P4b, P2", "onset (s)"), (4, "s6_f_pk_hz", "(e) f_pk", "f_pk (Hz)")):
        axd = fig.add_subplot(gs[2, col:col + 2])
        for i, (path, amp, lab) in enumerate(F6_S6_ROWS):
            st = S.get(path)
            if path == "P3":
                fill, size = S.F6_MARKS["p3_fill"][amp], S.F6_MARKS["p3_size"][amp]
            else:
                fill, size = "full", S.F6_MARKS["p4b_size"] if path == "P4b" else S.POINT_SIZES["f6_s6_line"]
            axd.plot(d["s6_T"], d[key][i], color=st.colour, ls=st.linestyle, lw=S.F6_MARKS["line_width"], marker=st.marker, ms=size, fillstyle=fill, mec=st.colour, zorder=3, label=lab)
        axd.set_xscale("log")
        if key == "s6_onset_s":
            axd.set_yscale("log")
        axd.set_xlabel("T_ramp (s)")
        axd.set_ylabel(yl)
        axd.set_title(ttl, loc=S.TITLE_LOC)
        groups = _coincident_rows(list(d[key]))
        if groups:
            names = [ln for g in groups for ln in textwrap.wrap(" = ".join(F6_S6_ROWS[i][2] for i in g), 40, subsequent_indent="  ")]
            axd.text(0.02, 0.98, "coincide (identical stored values):\n" + "\n".join(names), transform=axd.transAxes, ha="left", va="top",
                     fontsize=S.TEXT_SIZES["small"])
        if key == "s6_onset_s":
            axd.legend(loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=2, fontsize=S.TEXT_SIZES["legend"], frameon=False)
        else:
            axd.set_ylim(36.0, 60.0)
    # status block
    axs = fig.add_subplot(gs[3, :])
    axs.axis("off")
    lines = ["Stored status rows of the A11 table that touch F6 (a failure is shown, not dropped):"] + ["    " + s for s in d["rb_status"]]
    lines += ["FAIL rows of the stored A11 table that touch F6:"] + ["    " + s for s in f6_strip_lines(d)]
    lines += [f"RB7 (Table 7.2 names F6) has {d['rb7_rows']} rows in the stored A11 table; nothing is drawn for it (UNVERIFIED reading)."]
    lines += ["Panels are rows of the stored A9 table v2, A10 table and A7 S6 table; no series is drawn. The S6 and comparator classes are D-tr in all " + f"{len(d['s6_class']) * len(F6_S6_T)}" +
              " rows drawn (provisional, D8 open, DL-137). The P2 line joins the S5 comparators (10 s, 120 s) and the supplementary S6 P2 references (30 s, 300 s)."]
    lines = [ln for t_ in lines for ln in textwrap.wrap(t_, width=135, subsequent_indent="        ")]
    axs.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=S.TEXT_SIZES["status"], linespacing=1.25)
    return _style_text(fig, F6_FOOTER if draft else "")


def f6_caption_notes(d: dict) -> tuple:
    """Sentences about what is and is not drawn (13j). Values come from the prepared data; only the wording is typed here."""
    return (
        "Panel (a) counts, on the non-surge cells of the two regime maps, the primary A9 failure label (the first that applies in the order a to f, then g and h; filled bars) and every "
        "label that applies (open bars); a surge-class (D-tr) cell carries no label. The tick texts are the short forms listed in the claim-limit label table beside their verbatim sources; the labels are our operational "
        "rules on the plan's words (M9-12, DL-244), and label (c) is shown as \"a flag, not a demonstrated cause\" (MS9(e)-3; it uses the A4 Hopf frequency, not the episode frequency, DL-270).",
        "Panel (b) draws the stored class of each negative control at each of 13 T_ramp: NC1 (mean-field headline cell, and the mode-N records with 10 seeds each, whose classes are "
        "shown as the modal class and counts), NC2 (the I = 0 arm is the stored S5 P2 linear run, the I = 1 arm is P3 with I_amp 1, DL-246, DL-252) and NC3 (exploratory, feeds no gate). "
        "Panel (c) draws NC1 at the 5 map cells (mean field; each column names the stored Delta and tau_d of its cell) and, in its own column at the condition stored in its "
        "record (the reference point, Delta and tau_d, path and T_ramp; not the column of a map cell), the one NC1 network run, which is S+ (provisional, D8 open, DL-137) and not "
        "the expected NS, so G7 is NOT PASSED (DL-228). "
        "Panels (d) and (e) draw the stored onset and f_pk of the P3, P4a and P4b rows and of the P2 comparators at T_ramp 10, 30, 120 and 300 s; every drawn class is D-tr. "
        "Rows with identical stored values are drawn at their stored positions, told apart by their marks (the three P3 amplitudes as concentric marks of different fill and "
        "size, P4b larger than P2), and each panel names them in a note (coincide). "
        "RB7 (Table 7.2 names F6) has no row in the A11 table, so the FAIL-row strip holds the G7 gate row only. J_exit,static, the extension of P3 and P4 (MS9(e)-6), is not drawn. "
        "The failures and the non-surge regimes are drawn at the same weight as the surge cells.",
    )


def make_F6(res=None, out_dir=None, *, tag_build: bool = False, take_home=F6_TAKE_HOME, claim_limit_ids=F6_CLAIM_LIMITS,
            script="scripts/fig_F6.py", root=None) -> dict:
    """Build F6 from results/. Returns {'prov', 'paths', 'timing_s', 'drawn_sha256', 'caption'}. tag_build=True needs a clean tree (figprov)."""
    F.require_buildable("F6")
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "F6"
    t = {"start": time.perf_counter()}
    raw = load_F6(res)
    t["load"] = time.perf_counter()
    d = prepare_F6(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for key, rec in raw["records"].items():
        for r in make_param_table(rec["config"]):
            rows.append({**r, "panel": key, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    cap = CAP.build_caption("F6", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=[r for r in rows if r["key"] in F6_CAPTION_KEYS],
                            spectrogram=None, symbol_keys=(), notes=f6_caption_notes(d), not_applicable=F6_NOT_APPLICABLE)
    import matplotlib.pyplot as plt
    fig = _draw_F6(d, draft=not tag_build, columns=f6_column_labels(raw))
    out.mkdir(parents=True, exist_ok=True)
    pdf, png = out / "F6.pdf", out / "F6.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=S.PNG_DPI)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    cap_path, dig_path = out / "F6_caption.txt", out / "F6_drawn_data_sha256.txt"
    from .. import provenance as P
    drawn = drawn_data_sha256(d)
    P.atomic_write_text(cap_path, cap.text + "\n")
    P.atomic_write_text(dig_path, drawn + "\n")
    warnings = []
    for k, rec in raw["records"].items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true")
    prov = F.write_figure_provenance(
        "F6", script=script, inputs=[res / p for p in F6_INPUTS], outputs=[pdf, png, cap_path, dig_path], params_rows=rows,
        modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py",
                 "src/mprsurge/plotting/nordlie.py", "src/mprsurge/plotting/figprov.py"],
        configs=["configs/base.yaml", "configs/ms9/s6_p3.yaml", "configs/ms9/nc1.yaml", "configs/ms9/nc1_net.yaml"], claim_limits=cap.claim_limits,
        input_tables=[{"path": res / F6_INPUTS[0], "rows": int(len(raw["a9"]))}, {"path": res / F6_INPUTS[1], "rows": int(len(raw["a10"]))},
                      {"path": res / F6_INPUTS[2], "rows": int(len(raw["s6"]))}, {"path": res / F6_INPUTS[3], "rows": len(raw["a11"])}],
        spectrogram=None, tag_build=tag_build, out_dir=out, root=root, warnings=warnings, wall_time_s=time.perf_counter() - t["start"])
    nordlie_path = out / "F6_nordlie.md"
    N.write_nordlie(out / "F6_params.csv", out / "F6_provenance.json", nordlie_path, root=root)
    t["end"] = time.perf_counter()
    timing = {"load_s": t["load"] - t["start"], "prepare_s": t["prepare"] - t["load"], "draw_s": t["draw"] - t["prepare"],
              "provenance_and_nordlie_s": t["end"] - t["draw"], "total_s": t["end"] - t["start"]}
    return {"prov": prov, "paths": [pdf, png, cap_path, dig_path, out / "F6_params.csv", out / "F6_provenance.json", nordlie_path],
            "timing_s": timing, "drawn_sha256": drawn, "caption": cap.text}


# ---- F4 (13k) -------------------------------------------------------------------------------------------------------------------------------------
# Paths relative to results/. Tables first (docs/ms13_conventions.md M13-12): the stored A7 table holds the onsets (raw first crossing and classifier episode), the signed
# delays, the A4 entry-exit prediction (t_pred, delay_eta_pred, in_range) and the surge metrics of every S5 and S13 run (360 rows); the stored A3 table holds the M2
# saddle-node ramp (jump offset, ring class, ring rate); the stored A4 summary cross-checks the headline prediction; the stored A11 table holds the status rows and the
# FAIL-row strip. The run records are opened for their JSON config only (the ramp rate eps; the parameter rows); no series (.npz) is opened and no example trace is drawn.
# The M2 ring panel is read from A3 (the ring class and ring rate of each ramp), not from the A2 ring map, which is a static map over (eta/Delta, J/sqrt(Delta)) with no ramp
# (DL-483). The registry scripts/ms13_inputs.py INPUTS["F4"] must name the same files (test).
F4_INPUTS = (
    "A7/a7_ramp_metrics.parquet",                     # 360 rows: S5 (235) and S13 (125) families (DL-180, DL-181, DL-182, DL-186)
    "A3/a3_sn_ramp.parquet",                          # 13 rows: the M2 saddle-node ramps and their ring class (DL-109, DL-110)
    "A4/a4_rb3a_summary.json",                        # A4 entry-exit summary: headline prediction (cross-check), h_working
    "A11/a11_robustness.csv",                         # stored A11 table: status rows and the FAIL-row strip
)
F4_RECORD_DIRS = {"S5": "S5/ramp", "S5_noise": "S5/ramp_noise/p2_noise", "S13": "S13", "A3": "A3/S2"}
F4_RECORD_COUNTS = {"S5": 105, "S5_noise": 130, "S13": 125, "A3": 13}
F4_PARAM_ROWS = (("S5_headline", "S5ramp"), ("S5_noise", "p2_noise"), ("S13_floor", "floor_l0"))
F4_FAMILIES = (("p1_linear", "P1", "linear"), ("p1_sigmoid", "P1", "sigmoid"), ("p2_linear", "P2", "linear"), ("p2_sigmoid", "P2", "sigmoid"),
               ("p5_linear", "P5", "linear"), ("p5_sigmoid", "P5", "sigmoid"))
F4_S13 = ("delta0", "floor_l0", "floor_l1", "floor_l2", "radau", "rtol")
F4_DT = (1e-3, 5e-4, 2.5e-4, 1e-4)      # the Heun dt ladder, in units of tau (plan S13)
F4_STRIP = (("RB2", "noisy_subgrid_agreement"), ("RB2", "headline_class_kept_1.0_sigma"), ("RB3", "a_inrange_runs"), ("RB3", "b_classifier_onset"), ("RB6", "solver_onset_headline"))
F4_STATUS_RB = ("RB2", "RB3", "RB5", "RB6")
F4_CAPTION_KEYS = ("model.type", "model.ref_point", "path.name", "path.profile", "path.T_ramp_s", "solver.method", "solver.rtol", "solver.delta0", "noise.scheme", "noise.sigma")
F4_METRICS = ("T_ramp_s", "delay_eta_cross", "delay_eta", "delay_eta_pred", "peak_power_abs", "peak_power_rel", "f_pk_hz", "duration_s", "match_err_steps")

# Ruled (RULED_DL, 13p R13); first proposed for the reviewer's ruling (13k prompt, item B3); every statement is from a logged result (DL numbers in the text) and the numbers are checked against the
# stored tables by tests/test_fig_F4.py.
F4_TAKE_HOME = (
    "Onsets do not follow the A4 entry-exit prediction on the runs inside the RB3(a) range: 0 of 6 testable in-range runs are within one A4 step "
    "(33.1, 20.6, 12.7, 7.6, 4.4 and 25.1 steps; 3 more in-range runs have eta constant at the predicted time), and the noise-free headline onset (58.698 s) lies far "
    "before the predicted entry (115.2 s), so G6 was ruled PASSED WITH DEPARTURES (DL-188, DL-208). The noise-free onset is solver-dependent (DOP853 58.698 s, Radau 58.879 s, "
    "181 ms against the 1 ms bound: RB6 solver clause FAIL, unexplained) and the floored delay does not depend on the Heun step at the 1 ms output grid (DL-189, DL-190). "
    "Under the raw first-crossing reading the D43-floored delays of the headline fall with the floor level (-0.000760, -0.0423 and -0.1051 in eta units); under the "
    "classifier-onset reading they tie at -1.5 at the two lower levels and RB3(b) DOES NOT MEET (DL-182, DL-186, DL-208). With noise (sigma 0.0624, checked and not "
    "confirmed, DL-325) the median raw-crossing delay of the 10 seeds is negative from T_ramp 5.62 s on and the classes are mixed (A7 table, DL-180; RB2 FAIL, DL-387, DL-394). The M2 ramp through the saddle-node "
    "is damped at all 13 T_ramp and its jump offset from the fold falls from 0.346 to 0.0034 (DL-109, DL-110)."
)
# Ruled (RULED_DL, 13p R13): the limits of docs/ms13_plan.md section 5 whose right-hand column lists F4 and that are defined in docs/claim_limit_labels.md; G6-D1 and DL-163 departure 3 (DL-163-D3)
# were added to that table in 13l (DL-485 ruling); the plan labels RB2 FAIL and
# D24 failed were written in plain words with their DL numbers; 13o (DL-494 R2, R5): they are carried with their definitions. Listed, not decided.
F4_CLAIM_LIMITS = ("MS11-C7", "MS12-C1", "MS9(e)-2", "MS9(e)-5", "G6-D1", "G6-D2", "G6-D3", "DL-163-D1", "DL-163-D2", "DL-163-D3", "DL-163-D4", "G4-C4", "MS11-C1", "MS11-C3", "MS11-C6",
                   "RB2 FAIL (plan label)", "D24 failed (plan label)")
# 13o (DL-494 R8): paths whose eta holds eta_peak after t_on + T_ramp (ramps.py; P5, path_updown, turns down instead and has no hold)
F4_HOLD_PATHS = ("path_eta", "path_hypoxia")
F4_FOOTER = draft_footer("F4")


def _f4_record_path(row_family: str, run_id: str) -> str:
    if row_family == "p2_noise":
        return f"{F4_RECORD_DIRS['S5_noise']}/{run_id}.json"
    if row_family in F4_S13:
        return f"{F4_RECORD_DIRS['S13']}/{row_family}/{run_id}.json"
    return f"{F4_RECORD_DIRS['S5']}/{row_family}/{run_id}.json"


def f4_record_files(a7, a3) -> list[str]:
    """Paths (relative to results/) of every run record whose config is read: one per A7 row and one per A3 row."""
    return [_f4_record_path(f, r) for f, r in zip(a7["family"], a7["run_id"])] + [f"{F4_RECORD_DIRS['A3']}/{r}.json" for r in a3["run"]]


def load_F4(res=None) -> dict:
    """Open the files of F4_INPUTS and the run-record configs under `res` (default results/) and return their content. Opens nothing else."""
    res = Path(res) if res is not None else results_dir()
    for rel in F4_INPUTS:
        if not (res / rel).is_file():
            raise F.MissingInputError(f"input file not found: {res / rel}")
    try:
        import pandas as pd
        a7 = pd.read_parquet(res / F4_INPUTS[0])
        a3 = pd.read_parquet(res / F4_INPUTS[1])
        with open(res / F4_INPUTS[3], newline="", encoding="utf-8") as fh:
            a11 = list(csv.DictReader(fh))
        files = f4_record_files(a7, a3)
        eps, records, names, ramp = {}, {}, {}, {}
        for rel in files:
            if not (res / rel).is_file():
                raise F.MissingInputError(f"run record not found: {res / rel}")
            rec = json.loads((res / rel).read_text(encoding="utf-8"))
            path = rec["config"]["path"]
            eps[rec["name"]] = (float(path["eps"]), float(path["T_ramp_s"]))
            ramp[rec["name"]] = (float(path["t_on_s"]), float(path["eta_peak"]), str(path["name"]))
            names[rel] = rec["name"]
            for key, fam in F4_PARAM_ROWS:
                if rel == _f4_record_path(fam, rec["name"]) and key not in records:
                    records[key] = rec
        return {"a7": a7, "a3": a3, "a4": json.loads((res / F4_INPUTS[2]).read_text(encoding="utf-8")), "a11": a11, "eps": eps, "records": records,
                "record_files": files, "ramp": ramp}
    except (OSError, ValueError, KeyError, ImportError) as exc:
        raise F.MissingInputError(f"an F4 input cannot be read: {exc}") from exc


def _f4_arr(sub, col):
    return sub[col].astype(float).to_numpy()


def prepare_F4(raw: dict) -> dict:
    """Pure: stored content -> the arrays and numbers that are drawn. Keys are flat names; values are arrays, ints, floats, bools, strings or lists of strings."""
    a7, a3, a4 = raw["a7"].copy(), raw["a3"].copy(), raw["a4"]
    eps = raw["eps"]
    miss = [r for r in a7["run_id"] if r not in eps]
    if miss or len(a7) != 360:
        raise DataError(f"A7 table: {len(a7)} rows, {len(miss)} without a run record config (expected 360 and 0)")
    a7["eps"] = [eps[r][0] for r in a7["run_id"]]
    if any(abs(eps[r][1] - T) > 1e-9 for r, T in zip(a7["run_id"], a7["T_ramp_s"])):
        raise DataError("A7 table: T_ramp_s disagrees with the run-record config")
    d: dict = {}
    # 13o (DL-494 R8): a drawn delay whose stored onset lies after t_on + T_ramp on a path with a hold (the ramp has reached eta_peak) is an onset during the hold; there
    # the eta-based delay equals its maximum eta_peak - eta_H. Checked both ways on the stored values: a hold onset must sit at the maximum and no other onset may reach it.
    ramp = raw["ramp"]

    def hold_flags(sub, onset_col, delay_col):
        flags = []
        for run, T, on, dl, eh in zip(sub["run_id"], sub["T_ramp_s"].astype(float), sub[onset_col].astype(float), sub[delay_col].astype(float), sub["eta_H"].astype(float)):
            t_on, peak, name = ramp[run]
            top = peak - eh
            hold = bool(name in F4_HOLD_PATHS and np.isfinite(on) and on > t_on + T)
            if hold and abs(dl - top) > 1e-9:
                raise DataError(f"A7 table: {run} has its onset in the hold but a delay {dl!r} that is not eta_peak - eta_H {top!r}")
            if name in F4_HOLD_PATHS and not hold and np.isfinite(dl) and abs(dl - top) <= 1e-9:
                raise DataError(f"A7 table: {run} has the delay eta_peak - eta_H but its onset {on!r} lies before the end of the ramp")
            flags.append(hold)
        return np.array(flags, dtype=bool)

    hold_top = {round(ramp[r][1] - float(e), 12) for r, e in zip(a7["run_id"], a7["eta_H"]) if ramp[r][2] in F4_HOLD_PATHS}
    if len(hold_top) != 1:
        raise DataError(f"A7 table: eta_peak - eta_H is not one value on the paths with a hold: {sorted(hold_top)}")
    d["hold_delay_max"] = float(hold_top.pop())
    # (a) to (g): the six mode-D families, 13 T_ramp each, sorted by T_ramp
    for fam, path, prof in F4_FAMILIES:
        sub = a7[a7["family"] == fam].sort_values("T_ramp_s")
        if len(sub) != 13:
            raise DataError(f"A7 table: family {fam} has {len(sub)} rows, expected 13")
        d[f"{fam}_eps"] = sub["eps"].to_numpy(dtype=float)
        for c in F4_METRICS:
            d[f"{fam}_{c}"] = _f4_arr(sub, c)
        d[f"{fam}_in_range"] = sub["in_range"].fillna(False).astype(bool).to_numpy()
        d[f"{fam}_cls"] = [str(c) for c in sub["cls"]]
        d[f"{fam}_hold_cross"], d[f"{fam}_hold_cls"] = hold_flags(sub, "onset_cross_s", "delay_eta_cross"), hold_flags(sub, "onset_s", "delay_eta")
        if path == "P5":
            for c in ("offset_minus_eta_H", "hysteresis_width"):
                d[f"{fam}_{c}"] = _f4_arr(sub, c)
    # start state: P1 linear at start distances 0.5 and 3.0 (the 1.5 series is p1_linear)
    for tag, sd in (("sd05", 0.5), ("sd30", 3.0)):
        sub = a7[(a7["family"] == "p1_start_distance") & (a7["start_distance"] == sd)].sort_values("T_ramp_s")
        if len(sub) != 13:
            raise DataError(f"A7 table: p1_start_distance at {sd} has {len(sub)} rows, expected 13")
        d[f"{tag}_eps"] = sub["eps"].to_numpy(dtype=float)
        for c in ("delay_eta_cross", "delay_eta_pred", "peak_power_abs", "f_pk_hz", "duration_s"):
            d[f"{tag}_{c}"] = _f4_arr(sub, c)
        d[f"{tag}_in_range"] = sub["in_range"].fillna(False).astype(bool).to_numpy()
        d[f"{tag}_cls"] = [str(c) for c in sub["cls"]]
        d[f"{tag}_hold_cross"] = hold_flags(sub, "onset_cross_s", "delay_eta_cross")
    # noise band: p2_noise, 13 T_ramp x 10 seeds, sigma 0.0624 (checked, not confirmed; G4-C4), mode N
    sub = a7[a7["family"] == "p2_noise"].sort_values(["T_ramp_s", "seed"])
    if len(sub) != 130 or sorted(sub["seed"].unique().tolist()) != [float(s) for s in range(10)] or set(sub["sigma"]) != {0.0624}:
        raise DataError("A7 table: p2_noise is not 13 T_ramp x 10 seeds at sigma 0.0624")
    d["noise_eps"] = sub["eps"].to_numpy(dtype=float).reshape(13, 10)[:, 0]
    if not (sub["eps"].to_numpy(dtype=float).reshape(13, 10) == d["noise_eps"][:, None]).all():
        raise DataError("A7 table: p2_noise eps differs between seeds of one T_ramp")
    for c in ("T_ramp_s", "delay_eta_cross", "delay_eta", "peak_power_abs", "peak_power_rel", "f_pk_hz", "duration_s"):
        d[f"noise_{c}"] = _f4_arr(sub, c).reshape(13, 10)
    d["noise_cls"] = [[str(c) for c in sub["cls"].to_numpy().reshape(13, 10)[i]] for i in range(13)]
    # D43 floors at the headline (T_ramp 120 s): 3 levels x 4 Heun dt x 10 seeds (mode N)
    fd, fc, fs = [], [], []
    for lvl, fam in enumerate(("floor_l0", "floor_l1", "floor_l2")):
        sub = a7[a7["family"] == fam]
        if len(sub) != 40 or set(sub["T_ramp_s"]) != {120.0}:
            raise DataError(f"A7 table: family {fam} is not 40 runs at T_ramp 120 s")
        rows_d, rows_c = [], []
        for dt in F4_DT:
            s2 = sub[np.isclose(sub["heun_dt_tau"].astype(float), dt, rtol=0, atol=0)].sort_values("seed")
            if len(s2) != 10:
                raise DataError(f"A7 table: {fam} at dt {dt}: {len(s2)} rows, expected 10")
            rows_d.append(_f4_arr(s2, "delay_eta_cross"))
            rows_c.append(_f4_arr(s2, "delay_eta"))
        fd.append(rows_d)
        fc.append(rows_c)
        fs.append(float(sub["floor"].iloc[0]))
        if lvl == 0:
            d["floor_eps"] = float(sub["eps"].iloc[0])
        elif float(sub["eps"].iloc[0]) != d["floor_eps"]:
            raise DataError("A7 table: floor families differ in eps")
    d["floor_delay_cross"], d["floor_delay_cls"], d["floor_sigma"] = np.array(fd), np.array(fc), np.array(fs)
    d["floor_median_cross"] = np.median(d["floor_delay_cross"][:, 0, :], axis=1)
    d["floor_median_cls"] = np.median(d["floor_delay_cls"][:, 0, :], axis=1)
    d["floor_dt_identical"] = bool((d["floor_delay_cross"] == d["floor_delay_cross"][:, :1, :]).all())
    # headline row and the solver clause
    h = a7[a7["family"] == "S5ramp"]
    r = a7[a7["family"] == "radau"]
    if len(h) != 1 or len(r) != 1:
        raise DataError("A7 table: the headline (S5ramp) or Radau row is missing")
    d["head_eps"] = float(h["eps"].iloc[0])
    for c in ("onset_cross_s", "delay_eta_cross", "delay_eta_pred", "t_pred_s", "delay_eta", "onset_s"):
        d[f"head_{c}"] = float(h[c].iloc[0])
    d["head_radau_onset_cross_s"] = float(r["onset_cross_s"].iloc[0])
    d["head_radau_minus_default_ms"] = round((d["head_radau_onset_cross_s"] - d["head_onset_cross_s"]) * 1000.0, 6)
    hl = a4["headline"]
    if abs(d["head_delay_eta_pred"] - hl["delay_eta"]) > 1e-6 or abs(d["head_t_pred_s"] - hl["t_pred_s"]) > 1e-6:
        raise DataError("A7 headline prediction disagrees with the stored A4 summary")
    if round(d["head_radau_minus_default_ms"]) != 181:
        raise DataError(f"headline: Radau minus DOP853 {d['head_radau_minus_default_ms']} ms (DL-189 says 181)")
    # RB3(a): the runs inside the range and the testable ones (eta not constant at the predicted time)
    md = a7[a7["mode"] == "D"]
    inr = md[md["in_range"].fillna(False).astype(bool)]
    test = inr[~inr["eta_const_at_t_pred"].astype(bool)]
    d["n_in_range"], d["n_testable"] = int(len(inr)), int(len(test))
    d["n_testable_within_one_step"] = int((test["match_err_steps"].astype(float) <= 1.0).sum())
    d["testable_match_steps"] = np.sort(test["match_err_steps"].astype(float).to_numpy())
    d["n_nocross"] = int(md["delay_eta_cross"].isna().sum())
    d["n_none_class"] = int((md["cls"] == "D-none").sum())
    d["n_hold"] = int(sum(int(d[f"{f}_hold_cross"].sum()) + int(d[f"{f}_hold_cls"].sum()) for f, _p, _q in F4_FAMILIES) + sum(int(d[f"{t}_hold_cross"].sum()) for t in ("sd05", "sd30")))
    # A3: the M2 ramp through the saddle-node (ring class and ring rate)
    a3 = a3.sort_values("T_ramp_s")
    if len(a3) != 13 or (a3["status"] != "ok").any():
        raise DataError("A3 table: not 13 ok rows")
    d["a3_eps"] = np.array([eps[r][0] for r in a3["run"]])
    for c in ("T_ramp_s", "offset", "offset_steps", "rate", "se", "cycles_fit", "eta_jump", "fold_eta"):
        d[f"a3_{c}"] = _f4_arr(a3, c)
    d["a3_ring_class"] = [str(c) for c in a3["ring_class"]]
    # A11: status rows and the FAIL-row strip
    rows = [x for x in raw["a11"] if x["rb_id"] in F4_STATUS_RB]
    d["rb_status"] = [f"{x['rb_id']} {x['check_id']}: {x['pass_or_fail']}" for x in rows]
    by = {(x["rb_id"], x["check_id"]): x for x in raw["a11"]}
    d["strip"] = []
    for key in F4_STRIP:
        if key not in by or by[key]["pass_or_fail"] != "FAIL":
            raise DataError(f"A11 table: {key} is not a FAIL row (strip rows are FAIL rows as logged)")
        x = by[key]
        d["strip"].append({"rb_id": x["rb_id"], "check_id": x["check_id"], "status": x["pass_or_fail"], "value": x["value"], "threshold": x["threshold"]})
    d["rb5_fail_rows"] = int(sum(1 for x in raw["a11"] if x["rb_id"] == "RB5" and x["pass_or_fail"] == "FAIL"))
    if d["rb5_fail_rows"] != 0 or not by[("RB3", "a_inrange_runs")]["value"].startswith(f"{d['n_testable_within_one_step']} of {d['n_testable']} testable"):
        raise DataError("A11 table: RB3(a) or RB5 rows disagree with the A7 table")
    return d
def f4_strip_lines(d: dict) -> list[str]:
    return [f"{r['rb_id']} {r['check_id']}: {r['status']} ({r['value'] or 'value blank in the table'}; threshold {r['threshold'] or 'blank'}) - shown, not dropped" for r in d["strip"]]


def _f4_series(ax, x, y, path: str, profile: str, *, ms: float = S.POINT_SIZES["f4_series"], z: int = 3):
    """One path-and-profile series: the path colour and marker; a dashed line and an open marker for the sigmoid profile. NaN breaks the line (no interpolation)."""
    st = S.get(path)
    lin = profile == "linear"
    ax.plot(x, y, color=st.colour, ls=st.linestyle if lin else "--", lw=0.8, marker=st.marker, ms=ms, mfc=st.colour if lin else "none", mec=st.colour, mew=0.7, zorder=z)


def _f4_none_marks(ax, x, mask):
    """Runs with no value to draw (D-none, or no raw crossing) are drawn at the bottom of the axes with the D-none class marker, not dropped."""
    if mask.any():
        st = S.get("D-none")
        ax.plot(np.asarray(x)[mask], [0.025] * int(mask.sum()), ls="none", marker=st.marker, ms=S.POINT_SIZES["f4_none"], color=st.colour, mec=S.figure_colour("bar_edge"), mew=0.3,
                transform=ax.get_xaxis_transform(), clip_on=False, zorder=6)


def _f4_ring(ax, x, y, mask):
    rg = S.diagram_mark("f4_inrange")
    if mask.any():
        ax.plot(np.asarray(x)[mask], np.asarray(y)[mask], ls="none", marker=rg.marker, ms=rg.size, mfc="none", mec=rg.colour, mew=rg.width, zorder=5)


def _f4_hold(ax, x, y, mask):
    """13o (DL-494 R8): a delay whose stored onset lies in the hold (the delay equals eta_peak - eta_H there) carries its own mark, an open square."""
    m = np.asarray(mask, bool)
    if m.any():
        ax.plot(np.asarray(x)[m], np.asarray(y)[m], ls="none", marker=S.F4_MARKS["hold_marker"], ms=S.F4_MARKS["hold_size"], mfc="none", mec=S.F4_MARKS["hold_colour"],
                mew=S.F4_MARKS["hold_width"], zorder=5)


def _f4_noise(ax, d: dict, key: str):
    """The 10 mode-N seeds at each of the 13 T_ramp: the stored values as ticks, the stored min to max as a bar, the median as the median mark. No smoothing, no offsets."""
    nz, md = S.get("noise"), S.diagram_mark("fs3_median")
    v = d[key]
    for x_, col in zip(d["noise_eps"], v):
        ax.plot([x_, x_], [np.nanmin(col), np.nanmax(col)], color=nz.colour, lw=3.0, solid_capstyle="butt", zorder=1)
        ax.plot([x_] * len(col), col, ls="none", marker=nz.marker, ms=S.POINT_SIZES["f4_seed_tick"], color=S.figure_colour("range_line"), mew=0.5, zorder=2)
        ax.plot([x_], [np.nanmedian(col)], ls="none", marker=md.marker, ms=md.size, color=S.F4_MARKS["median_colour"], mew=md.width, zorder=4)


def _draw_F4(d: dict, draft: bool):
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    fig = plt.figure(figsize=(7.4, 15.4), constrained_layout=True)
    gs = fig.add_gridspec(7, 6, height_ratios=[1.25, 2.4, 2.25, 2.25, 1.9, 1.6, 2.2])          # 13o (DL-494 R8): more room for (b) to (e)
    pred, ref, cls_m, fail = S.diagram_mark("f4_pred"), S.diagram_mark("f4_ref"), S.diagram_mark("f4_cls"), S.diagram_mark("f4_fail")
    down, hyst, rg, md = S.diagram_mark("f4_down"), S.diagram_mark("f4_hyst"), S.diagram_mark("f4_inrange"), S.diagram_mark("fs3_median")
    edge = S.figure_colour("bar_edge")

    def tidy(ax, title, ylabel, xlabel=True, red=False):
        ax.set_xscale("log")
        ax.set_title(title, loc=S.TITLE_LOC, color=S.figure_colour("fail_text") if red else S.figure_colour("text_dark"))
        ax.set_ylabel(ylabel)
        if xlabel:
            ax.set_xlabel("eps (ramp rate, 1/tau)")

    # key row
    kx = fig.add_subplot(gs[0, :])
    kx.axis("off")
    hs = []
    for fam, path, prof in F4_FAMILIES:
        st = S.get(path)
        lin = prof == "linear"
        hs.append(Line2D([], [], color=st.colour, ls=st.linestyle if lin else "--", lw=0.8, marker=st.marker, ms=S.POINT_SIZES["f4_series"], mfc=st.colour if lin else "none", mec=st.colour, label=f"{path} {prof}"))
    hs += [Line2D([], [], color=pred.colour, ls=pred.linestyle, lw=pred.width, label="A4 entry-exit prediction (stored; linear profiles)"),
           Line2D([], [], ls="none", marker=rg.marker, ms=S.POINT_SIZES["f4_key"], mfc="none", mec=rg.colour, mew=rg.width, label="inside the RB3(a) range (judged); outside: reported, not judged"),
           Line2D([], [], ls="none", marker=cls_m.marker, ms=cls_m.size, color=cls_m.colour, label="classifier-onset reading (secondary); raw crossing = path mark (primary)"),
           Line2D([], [], color=ref.colour, ls=ref.linestyle, lw=ref.width, label="quasi-static reference: onset at eta_H (delay 0)"),
           Line2D([], [], ls="none", marker=S.get("D-none").marker, ms=S.POINT_SIZES["f4_none"], color=S.get("D-none").colour, mec=edge, mew=0.3, label="no raw crossing / no episode (D-none), at the axis foot"),
           Line2D([], [], color=S.get("noise").colour, lw=3.0, label="noise: stored min to max of 10 seeds (sigma 0.0624, checked, not confirmed)"),
           Line2D([], [], ls="none", marker=md.marker, ms=md.size, color=S.F4_MARKS["median_colour"], mew=md.width, label="stored median of the seeds"),
           Line2D([], [], ls="none", marker=S.F4_MARKS["hold_marker"], ms=S.POINT_SIZES["f4_key"], mfc="none", mec=S.F4_MARKS["hold_colour"], mew=S.F4_MARKS["hold_width"],
                  label=f"onset during the hold: delay = eta_peak - eta_H ({d['hold_delay_max']:.3g})"),
           Line2D([], [], ls="none", marker=fail.marker, ms=S.POINT_SIZES["f4_key"], color=fail.colour, label="RB6 FAIL: not used as evidence")]
    kx.legend(handles=hs, loc="center", ncol=3, fontsize=S.TEXT_SIZES["legend"], frameon=False, handlelength=2.2, columnspacing=1.2, labelspacing=0.5)

    # (a) delay against eps, signed, raw crossing primary
    ax = fig.add_subplot(gs[1, :])
    for fam, path, prof in F4_FAMILIES:
        x = d[f"{fam}_eps"]
        _f4_series(ax, x, d[f"{fam}_delay_eta_cross"], path, prof)
        ok = ~np.isnan(d[f"{fam}_delay_eta"])
        ax.plot(x[ok], d[f"{fam}_delay_eta"][ok], ls="none", marker=cls_m.marker, ms=cls_m.size, color=cls_m.colour, mew=cls_m.width, zorder=4)
        _f4_ring(ax, x, d[f"{fam}_delay_eta_cross"], d[f"{fam}_in_range"])
        _f4_hold(ax, x, d[f"{fam}_delay_eta_cross"], d[f"{fam}_hold_cross"])
        _f4_hold(ax, x, d[f"{fam}_delay_eta"], d[f"{fam}_hold_cls"])
        _f4_none_marks(ax, x, np.isnan(d[f"{fam}_delay_eta_cross"]))
        if prof == "linear":
            st = S.get(path)
            ax.plot(x, d[f"{fam}_delay_eta_pred"], color=st.colour, ls=pred.linestyle, lw=pred.width, zorder=2)
    ax.axhline(0.0, color=ref.colour, ls=ref.linestyle, lw=ref.width, zorder=1)
    ax.plot([d["head_eps"]], [d["head_delay_eta_cross"]], ls="none", marker=fail.marker, ms=fail.size, color=fail.colour, mew=fail.width, zorder=6)
    ax.annotate("headline (T_ramp 120 s, noise-free): RB6 solver clause FAIL", xy=(d["head_eps"], d["head_delay_eta_cross"]), xytext=(d["head_eps"], 2.3), fontsize=S.TEXT_SIZES["small"],
                color=S.figure_colour("fail_text"), ha="center", va="bottom", arrowprops=dict(arrowstyle="-", lw=0.5, color=S.figure_colour("fail_text")))
    ax.set_ylim(-0.25, 2.6)
    tidy(ax, "(a) delay against ramp rate (signed): raw first crossing, noise-free (mode D)", "delay (eta - eta_H)")

    # (b) to (e): peak power (absolute, relative), f_pk, duration
    for pos, key, noisekey, title, yl, logy in ((gs[2, 0:2], "peak_power_abs", "noise_peak_power_abs", "(b) peak power, absolute", "peak power (abs)", False),
                                                  (gs[2, 2:4], "peak_power_rel", "noise_peak_power_rel", "(c) peak power, relative", "peak power (rel)", False),
                                                  (gs[2, 4:6], "f_pk_hz", "noise_f_pk_hz", "(d) f_pk", "f_pk (Hz)", False),
                                                  (gs[3, 0:2], "duration_s", "noise_duration_s", "(e) duration", "duration (s)", True)):
        ax = fig.add_subplot(pos)
        _f4_noise(ax, d, noisekey)
        for fam, path, prof in F4_FAMILIES:
            _f4_series(ax, d[f"{fam}_eps"], d[f"{fam}_{key}"], path, prof, ms=S.POINT_SIZES["f4_series_small"])
            _f4_ring(ax, d[f"{fam}_eps"], d[f"{fam}_{key}"], d[f"{fam}_in_range"])
            _f4_none_marks(ax, d[f"{fam}_eps"], np.isnan(d[f"{fam}_{key}"]))
        if logy:
            ax.set_yscale("log")
        tidy(ax, title, yl)

    # (f) up against down ramp: P5
    ax = fig.add_subplot(gs[3, 2:4])
    for fam, path, prof in (("p5_linear", "P5", "linear"), ("p5_sigmoid", "P5", "sigmoid")):
        x = d[f"{fam}_eps"]
        _f4_series(ax, x, d[f"{fam}_delay_eta_cross"], path, prof, ms=S.POINT_SIZES["f4_series_p5"])
        ax.plot(x, d[f"{fam}_offset_minus_eta_H"], color=down.colour, ls="-" if prof == "linear" else ":", lw=0.8, marker=down.marker, ms=down.size - 1.5, zorder=3)
        ax.plot(x, d[f"{fam}_hysteresis_width"], color=hyst.colour, ls=hyst.linestyle if prof == "linear" else ":", lw=hyst.width, zorder=2)
        _f4_none_marks(ax, x, np.isnan(d[f"{fam}_delay_eta_cross"]))
    ax.axhline(0.0, color=ref.colour, ls=ref.linestyle, lw=ref.width, zorder=1)
    tidy(ax, "(f) up and down (P5): up delay, down offset, width", "eta - eta_H")

    # (g) start state: P1 linear at three start distances (1.5 is the p1_linear series)
    ax = fig.add_subplot(gs[3, 4:6])
    p1 = S.get("P1")
    for tag, lab, ls, fill in (("sd05", "0.5", ":", "left"), ("p1_linear", "1.5", "-", "full"), ("sd30", "3.0", "--", "none")):
        x = d[f"{tag}_eps"]
        y = d[f"{tag}_delay_eta_cross"]
        ax.plot(x, y, color=p1.colour, ls=ls, lw=0.8, marker=p1.marker, ms=S.POINT_SIZES["f4_series_p5"], fillstyle=fill, mec=p1.colour, mew=0.7, zorder=3)
        _f4_ring(ax, x, y, d[f"{tag}_in_range"])
        _f4_hold(ax, x, y, d[f"{tag}_hold_cross"])
        _f4_none_marks(ax, x, np.isnan(y))
    ax.axhline(0.0, color=ref.colour, ls=ref.linestyle, lw=ref.width, zorder=1)
    ax.text(0.02, 0.97, "start distance: 0.5 dotted, 1.5 solid, 3.0 dashed", transform=ax.transAxes, fontsize=S.TEXT_SIZES["small"], va="top", ha="left")
    ax.set_ylim(-0.1, 2.45)
    tidy(ax, "(g) start state (P1 linear)", "delay (eta - eta_H)")

    # (h) noise band on the delay
    ax = fig.add_subplot(gs[4, 0:2])
    _f4_noise(ax, d, "noise_delay_eta_cross")
    _f4_series(ax, d["p2_linear_eps"], d["p2_linear_delay_eta_cross"], "P2", "linear", ms=S.POINT_SIZES["f4_series_p5"])
    ax.axhline(0.0, color=ref.colour, ls=ref.linestyle, lw=ref.width, zorder=1)
    tidy(ax, "(h) noise band, P2, mode N: RB2 FAIL", "delay (eta - eta_H)", red=True)

    # (i) and (j): the D43 floor at the headline, per level, 4 Heun rungs x 10 seeds, both onset readings
    for pos, key, med, title in ((gs[4, 2:4], "floor_delay_cross", "floor_median_cross", "(i) D43 floor, raw crossing (primary)"),
                                 (gs[4, 4:6], "floor_delay_cls", "floor_median_cls", "(j) D43 floor, classifier onset")):      # 13o (DL-494 R8): (j) as wide as (i)
        ax = fig.add_subplot(pos)
        for lvl in range(3):
            mk = S.diagram_mark(f"fs4_l{lvl}")
            for k, size in enumerate(S.POINT_SIZES["f4_floor_rungs"]):      # the four Heun rungs, 1e-3 to 1e-4 tau, drawn concentric (their values are identical)
                ax.plot([lvl] * 10, d[key][lvl][k], ls="none", marker=mk.marker, ms=size, mfc="none", mec=mk.colour, mew=0.6, zorder=3)
            ax.plot([lvl], [d[med][lvl]], ls="none", marker=md.marker, ms=md.size, color=S.F4_MARKS["median_colour"], mew=md.width, zorder=4)
        ax.set_xticks(range(3), [f"{s_:.3g}" for s_ in d["floor_sigma"]])
        ax.set_xlim(-0.5, 2.5)
        ax.set_xlabel("floor sigma (D43 level 0, 1, 2)")
        ax.set_title(title, loc=S.TITLE_LOC, color=S.figure_colour("fail_text") if key == "floor_delay_cls" else S.figure_colour("text_dark"))
        ax.set_ylabel("delay (eta - eta_H)")

    # (k) and (l): M2 through the saddle-node (A3)
    mf = S.get("mean_field")
    ax = fig.add_subplot(gs[5, 0:3])
    ax.plot(d["a3_eps"], d["a3_offset"], color=mf.colour, ls="-", lw=0.8, marker=mf.marker, ms=S.POINT_SIZES["f4_m2"], zorder=3)
    ax.set_yscale("log")
    tidy(ax, "(k) M2 ramp through the saddle-node: jump offset from the fold", "offset (eta)")
    ax = fig.add_subplot(gs[5, 3:6])
    for x_, r_, s_ in zip(d["a3_eps"], d["a3_rate"], d["a3_se"]):
        ax.plot([x_, x_], [r_ - s_, r_ + s_], color=S.figure_colour("range_line"), lw=1.0, zorder=2)
    ax.plot(d["a3_eps"], d["a3_rate"], color=mf.colour, ls="none", marker=mf.marker, ms=S.POINT_SIZES["f4_m2"], zorder=3)
    ax.set_ylim(-28.0, -20.0)
    tidy(ax, f"(l) M2 ring: fitted rate (per s, +-1 SE); class {d['a3_ring_class'][0]} at {sum(c == 'damped' for c in d['a3_ring_class'])} of 13", "ring rate (1/s)")

    # status block
    axs = fig.add_subplot(gs[6, :])
    axs.axis("off")
    lines = [ln for t_ in f4_status_lines(d) for ln in textwrap.wrap(t_, width=150, subsequent_indent="        ")]
    axs.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=S.TEXT_SIZES["status"], linespacing=1.25)
    return _style_text(fig, F4_FOOTER if draft else "")


def f4_status_lines(d: dict) -> list[str]:
    by_rb: dict = {}
    for s_ in d["rb_status"]:
        by_rb.setdefault(s_.split(" ")[0], []).append(s_.split(" ", 1)[1])
    lines = ["Stored status of the RB2, RB3, RB5 and RB6 rows of the A11 table (a failure is shown, not dropped):"] + [f"    {k}: " + "; ".join(v) for k, v in by_rb.items()]
    lines += [strip_heading("F4")] + ["    " + s for s in f4_strip_lines(d)]
    lines += [f"RB3(a): {d['n_in_range']} runs inside the range, {d['n_testable']} testable, {d['n_testable_within_one_step']} within one A4 step (match error in steps: "
              + ", ".join(f"{x:.1f}" for x in d["testable_match_steps"]) + "); runs outside the range are reported, not judged. RB5 has no FAIL row."]
    lines += [f"{d['n_nocross']} run has no raw crossing and {d['n_none_class']} mode-D runs are D-none (no episode metrics); they are drawn at the axis foot, not dropped."]
    return lines


def f4_caption_notes(d: dict) -> tuple:
    """Sentences about what is and is not drawn (13k). Values come from the prepared data; only the wording is typed here."""
    return (
        "Panel (a) draws the delay eta - eta_H of the onset, signed (negative = onset before eta_H), against the ramp rate eps = (eta_peak - eta_start)/T_ramp, for the noise-free mean-field "
        "runs (mode D, DOP853) of P1, P2 and P5 with the linear and the sigmoid profile at 13 T_ramp. The onset reading is the raw first crossing of the envelope at 0.1 x A_ref "
        "(primary, DL-186 clarification 1); the classifier-episode onset is the small double dagger (secondary; RB3(b) is reported under both readings, G6-D3, DL-208). The dash-dot lines "
        "are the A4 entry-exit prediction as stored in the A7 table, drawn where the predicted entry lies in the run; a ring marks a run inside the RB3(a) range, which is judged "
        "on the testable runs only (DL-186 clarification 2): " + f"{d['n_testable_within_one_step']} of {d['n_testable']}" + " are within one A4 step, so the onset does not follow the prediction "
        "(claim limit G6-D1, defined in the claim-limit list); runs outside the range are reported, not judged, and RB3(a) is not judged at the headline "
        "(DL-163-D3). The dotted zero line is the quasi-static reference by the definition of the delay column (onset at eta_H); no quasi-static onset is computed here. The headline "
        "(T_ramp 120 s) carries the RB6 solver clause FAIL (DOP853 58.698 s, Radau 58.879 s, 181 ms against 1 ms, DL-189) and is not used as evidence (G6-D2). "
        f"An open square marks the {d['n_hold']} drawn delays in panels (a) and (g) whose stored onset lies after t_on + T_ramp on P1 or P2: onset during the hold; the eta-based "
        f"delay equals its maximum eta_peak - eta_H there ({d['hold_delay_max']:.3g}; UNVERIFIED reading of the stored values, no decision-log entry discusses it). P5 has no hold: "
        "its onsets after t_on + T_ramp lie on the way down and stay below that maximum.",
        "Panels (b) to (e) draw the stored peak power (absolute and relative), f_pk and duration of the same runs; the grey bars are the stored minimum to maximum of the 10 mode-N seeds at "
        "sigma 0.0624 (checked, not confirmed, G4-C4), the dark bar marks their stored median; nothing is smoothed or offset. Runs with no episode (D-none) and the one run with no raw crossing are "
        "drawn at the foot of the axes, not dropped. f_pk is the classifier's spectral peak (MS11-C3). Panel (f) draws, for P5, the up delay, the offset on the way down (eta_off - eta_H) "
        "and the hysteresis width as stored; panel (g) the P1 linear delay at the start distances 0.5, 1.5 and 3.0. Panel (h) repeats the delay for the noisy runs beside the noise-free P2 "
        "line; the RB2 gate FAILED (7 of 10 seeds keep the headline class, MS11-C1; noisy subgrid 97 of 225, D24 failed, DL-242), so no claim of robustness to noise is made.",
        "Panels (i) and (j) draw the D43-floored runs at the headline (levels 0, 1, 2; 10 seeds; four Heun steps 1e-3 to 1e-4 tau drawn as concentric marks, which coincide at the 1 ms "
        "output grid, DL-190) under the raw crossing and under the classifier onset; the median of the seeds is the bar. The delays are signed (DL-186 clarification 8). Panels (k) and (l) "
        "are the M2 ramp through the saddle-node from the A3 table (the ring class and the fitted ring rate); the A2 ring map is a static map with no ramp and is not drawn here. "
        "Delays are on the 1 ms output grid. Every D8-dependent class is provisional (D8 open).",
    )


def make_F4(res=None, out_dir=None, *, tag_build: bool = False, take_home=F4_TAKE_HOME, claim_limit_ids=F4_CLAIM_LIMITS,
            script="scripts/fig_F4.py", root=None) -> dict:
    """Build F4 from results/. Returns {'prov', 'paths', 'timing_s', 'drawn_sha256', 'caption'}. tag_build=True needs a clean tree (figprov)."""
    F.require_buildable("F4")
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "F4"
    t = {"start": time.perf_counter()}
    raw = load_F4(res)
    t["load"] = time.perf_counter()
    d = prepare_F4(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for key, rec in raw["records"].items():
        for r in make_param_table(rec["config"]):
            rows.append({**r, "panel": key, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    cap = CAP.build_caption("F4", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=[r for r in rows if r["key"] in F4_CAPTION_KEYS],
                            spectrogram=None, symbol_keys=(), notes=f4_caption_notes(d), limit_labels=CLAIM_LIMIT_LABELS)
    import matplotlib.pyplot as plt
    fig = _draw_F4(d, draft=not tag_build)
    out.mkdir(parents=True, exist_ok=True)
    pdf, png = out / "F4.pdf", out / "F4.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=S.PNG_DPI)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    cap_path, dig_path = out / "F4_caption.txt", out / "F4_drawn_data_sha256.txt"
    from .. import provenance as P
    drawn = drawn_data_sha256(d)
    P.atomic_write_text(cap_path, cap.text + "\n")
    P.atomic_write_text(dig_path, drawn + "\n")
    warnings = []
    for k, rec in raw["records"].items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true")
    prov = F.write_figure_provenance(
        "F4", script=script, inputs=[res / p for p in F4_INPUTS] + [res / p for p in raw["record_files"]], outputs=[pdf, png, cap_path, dig_path], params_rows=rows,
        modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py",
                 "src/mprsurge/plotting/nordlie.py", "src/mprsurge/plotting/figprov.py"],
        configs=["configs/base.yaml", "configs/S5_ramp.yaml"], claim_limits=cap.claim_limits,
        input_tables=[{"path": res / F4_INPUTS[0], "rows": len(raw["a7"])}, {"path": res / F4_INPUTS[1], "rows": len(raw["a3"])}, {"path": res / F4_INPUTS[3], "rows": len(raw["a11"])}],
        spectrogram=None, tag_build=tag_build, out_dir=out, root=root, warnings=warnings, wall_time_s=time.perf_counter() - t["start"])
    nordlie_path = out / "F4_nordlie.md"
    N.write_nordlie(out / "F4_params.csv", out / "F4_provenance.json", nordlie_path, root=root)
    t["end"] = time.perf_counter()
    timing = {"load_s": t["load"] - t["start"], "prepare_s": t["prepare"] - t["load"], "draw_s": t["draw"] - t["prepare"],
              "provenance_and_nordlie_s": t["end"] - t["draw"], "total_s": t["end"] - t["start"]}
    return {"prov": prov, "paths": [pdf, png, cap_path, dig_path, out / "F4_params.csv", out / "F4_provenance.json", nordlie_path],
            "timing_s": timing, "drawn_sha256": drawn, "caption": cap.text}


# ---- F1 (13l): schematic and ramp protocol; mean-field and network r(t), v(t) on the headline path; 300-neuron raster; spectrogram of v ---------------------------
# Paths relative to results/. scripts/ms13_inputs.py INPUTS["F1"] must name the same files (test). Registry change of 13l (DL-486): the A8 sensitivity table and the S8 mean-field
# companion (head60, T_ramp 60 s) are not read (F1 draws no A_ref-based series and no 60 s run); ms10_eval.json and the A11 table are added (stored classes, onsets and the strip).
F1_MF_RECORD = "S5/ramp/S5ramp/S5ramp_0000_240de3ef73be"          # P2, ref_devalle, T_ramp 120 s: the mean-field headline (docs/ms8_close.md)
F1_NET_DIR = "S8/S8_head"                                         # network headline: T_ramp 10 s and 120 s x 3 seeds, N = 1e4 (MS10 10f, DL-317)
F1_NET_COUNT = 6
F1_INPUTS = (
    "A8/a8_aref.json",                                            # A_ref (reading a), stated in the caption only
    "ms10/eval/ms10_eval.json",                                   # stored classes, classifier and raw-crossing onsets, f_pk and control classes of the S8 headline (DL-319)
    "A11/a11_robustness.csv",                                     # stored A11 table: the FAIL-row strip
)
F1_T_RAMP = 120.0
F1_COLUMNS = 1300                                                 # blocks of a decimated series (about the drawn width of a time panel in pixels at the PNG resolution)
F1_ZOOM_S = 1.0                                                   # length of the two raster windows
F1_STRIP = (("RB1", "headline_10s"), ("RB1", "headline_120s"), ("RB1", "cells_30s"), ("RB1", "overall"), ("G7", "gate"))
F1_CAPTION_KEYS = ("model.type", "model.ref_point", "model.J", "model.Delta", "model.tau_ms", "model.tau_d_ms", "path.name", "path.profile", "path.T_ramp_s", "path.t_on_s",
                   "path.eta_start", "path.eta_H", "path.eta_peak", "path.J0", "path.J_end", "network.N", "network.het_dist", "network.n_raster", "network.rate_bin_ms",
                   "solver.method", "solver.dt_out_ms", "noise.sigma", "seeds.root_seed")
F1_SEED_KEYS = ("fs4_s0", "fs4_s1", "fs4_s2")                     # the three network seeds keep the colours and line styles they have in FS4

# Ruled (RULED_DL, 13p R13); first proposed for the reviewer's ruling (13l prompt, item B3); every statement is from a logged result (DL numbers in the text) and the numbers are checked against the stored
# ms10_eval.json and the stored records by tests/test_fig_F1.py.
F1_TAKE_HOME = (
    "At the headline (P2, ref_devalle, T_ramp 120 s) the stored mean-field record is a surge of class D-tr with a spectral peak of 49.0 Hz and onset 58.698 s "
    "(DL-319); the peak is far above 25 Hz, so the plan's second F1 trigger did not occur. The network at N = 1e4 does not reproduce this class: all 3 stored seeds are S-sus (3 of 3; DL-319, DL-323) with "
    "classifier onset 12.0 s (46.7 s before the mean-field onset) and f_pk 49.0, 48.5 and 49.0 Hz; at T_ramp 10 s the 3 seeds are S-abs, S-rel and S-sus (0 of 3 seeds at each "
    "T_ramp, RB1 headline FAIL, DL-319). The network controls without a ramp reach the surge classes S-abs and S-rel at the 10 s headline, S+ in S9 at N = 3e3 and 1e4 and at map cell "
    "(24,26) (DL-325); the 120 s headline controls are S-sus 3 of 3 (DL-319, DL-323). Network classes under the frozen criteria therefore cannot separate ramp-driven from non-ramp "
    "records (G4-C3, DL-229, DL-231). RB1 failed (headline 10 s, "
    "headline 120 s, cells 1 of 4), G4 was triggered through consequence (2) and is report-only; the surge result is stated for the mean field only (DL-320, DL-323, DL-325)."
)
# Ruled (RULED_DL, 13p R13): the limits of docs/ms13_plan.md section 5 whose right-hand column lists F1 and that are defined in docs/claim_limit_labels.md. The plan labels RB1 FAIL (DL-319, DL-320)
# and G7 not passed (DL-228) were written in plain words; 13o (DL-494 R2, R5; DL-495): both are carried with their definitions (RB1 FAIL added to the label table). Listed, not decided.
F1_CLAIM_LIMITS = ("MS11-C7", "MS12-C1", "MS9(e)-1", "MS9(e)-5", "DL-163-D1", "G4-C1", "G4-C2", "G4-C3", "MS11-C2", "MS11-C3", "RB1 FAIL (plan label)", "G7 not passed (plan label)")
# 13o (DL-494 R7): panel (i) is a spike-count image, counts per stored neuron per bin of this length (display aggregation, UNVERIFIED; the count is exact, nothing is smoothed)
F1_COUNT_BIN_S = 1.0
# 13o (DL-494 R6): the model schematic, built from the 10 elements of docs/ms13_f1_schematic_proposal.md. Every label is a verbatim string of docs/plan.md (a test checks it); a row
# of several labels is drawn joined by F1_SCHEMATIC_SEP. No equation and no value is drawn (the values stay in panels (a) and (b), from the stored record). The boxes, their
# placement and the arrows are our layout (UNVERIFIED). Each entry: (box key, heading, rows).
F1_SCHEMATIC_SEP = ": "
F1_SCHEMATIC = (
    ("ramp", "ramp protocol", (("P2 (path_hypoxia)",), ("η̄ (eta_bar)",), ("J (J)",), ("t_on",), ("T_ramp (T_ramp_s)", "Ramp duration"),
                               ("I (I_drive)", "Common (non-local) drive"))),
    ("model", "M3", (("All-to-all coupling, quenched Lorentzian heterogeneity, N → ∞",), ("a common input",),
                     ("M3 is read as an inhibition-dominated (ING) local circuit",), ("η̄ (eta_bar)", "Mean excitability"), ("Δ (Delta)", "Heterogeneity half-width"),
                     ("J (J)", "Signed coupling"), ("τ_d (tau_d_ms)", "Synaptic decay (M3)"), ("Inhibitory + first-order synapse (ING)",),
                     ("τ (tau_ms)", "Membrane time constant"))),
    ("mf", "mean field", (("r, v, s", "Rate, mean potential, synapse"),)),
    ("net", "network", (("N (N)", "Network size"), ("raster",))),
    ("out", "outputs", (("mean-field and network r(t), v(t) on the headline path",), ("spectrogram of v",))),
)
# box positions in axes fractions (x0, y0, x1, y1) and the arrows between boxes: our layout, UNVERIFIED
F1_SCHEMATIC_BOXES = {"ramp": (0.0, 0.05, 0.2, 0.95), "model": (0.235, 0.0, 0.585, 1.0), "mf": (0.62, 0.55, 0.81, 0.97), "net": (0.62, 0.03, 0.81, 0.45),
                      "out": (0.835, 0.2, 1.0, 0.8)}
F1_SCHEMATIC_WRAP = {"ramp": 30, "model": 66, "mf": 32, "net": 32, "out": 29}       # characters per drawn line; a row is wrapped at spaces only, so its words stay verbatim


def f1_count_range(d: dict) -> tuple:
    """13o (DL-494 R7): the colour range of the count image, 0 to the stored-count percentile S.F1_RASTER['top_percentile'] (one neuron reaches far above the rest and would
    leave the image blank); the counts above it are drawn in the top colour and counted here. Display choice, UNVERIFIED; the drawn counts are the exact counts."""
    top = float(np.percentile(d["ras_count"], S.F1_RASTER["top_percentile"]))
    return top, int((d["ras_count"] > top).sum()), int(d["ras_count"].size)
F1_SCHEMATIC_ARROWS = (("ramp", "model"), ("model", "mf"), ("model", "net"), ("mf", "out"), ("net", "out"))
F1_FOOTER = draft_footer("F1")


def envelope_minmax(x, y, n_cols: int):
    """Display decimation of a drawn series (13l ruling, UNVERIFIED): the record is cut into n_cols contiguous blocks of whole samples; each block gives (centre time, minimum, maximum),
    so the extremes of every block and of the whole series are the stored extremes (no smoothing, no resampling)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = y.size
    if x.size != n or n < n_cols or n_cols < 1:
        raise DataError(f"envelope: {n} samples cannot be cut into {n_cols} blocks")
    edges = np.linspace(0, n, n_cols + 1).astype(np.int64)
    starts, ends = edges[:-1], edges[1:] - 1
    return (x[starts] + x[ends]) / 2.0, np.minimum.reduceat(y, starts), np.maximum.reduceat(y, starts)


def _f1_record(res: Path, stem: str) -> dict:
    p = res / (stem + ".json")
    if not p.is_file() or not p.with_suffix(".npz").is_file():
        raise F.MissingInputError(f"run record not found: {p} (json and npz)")
    return json.loads(p.read_text(encoding="utf-8"))


def load_F1(res=None) -> dict:
    """Open the files of F1_INPUTS, the stored mean-field headline record, the six stored network headline records (json) and the npz series of the three 120 s records
    (t_ms, r, v; the raster of seed 0 only) under `res` (default results/). Opens nothing else."""
    res = Path(res) if res is not None else results_dir()
    for rel in F1_INPUTS:
        if not (res / rel).is_file():
            raise F.MissingInputError(f"input file not found: {res / rel}")
    try:
        mf_rec = _f1_record(res, F1_MF_RECORD)
        heads = sorted(p for p in (res / F1_NET_DIR).glob("*.json") if not p.name.endswith(".dry.json"))
        if len(heads) != F1_NET_COUNT:
            raise DataError(f"F1: {len(heads)} network headline records found, {F1_NET_COUNT} expected")
        net = []
        for p in heads:
            rec = json.loads(p.read_text(encoding="utf-8"))
            net.append({"rel": p.relative_to(res).as_posix(), "rec": rec, "T": float(rec["config"]["path"]["T_ramp_s"]), "seed": int(rec["config"]["seeds"]["spawn_key"][-1])})
        sel = sorted((n for n in net if n["T"] == F1_T_RAMP), key=lambda n: n["seed"])
        out = {"mf_rec": mf_rec, "mf_rel": F1_MF_RECORD + ".json", "net_all": net, "net": sel}
        with np.load(res / (F1_MF_RECORD + ".npz")) as z:
            out["mf"] = {k: z[k].copy() for k in ("t_ms", "r", "v", "eta", "J")}
        for i, n in enumerate(sel):
            with np.load((res / n["rel"]).with_suffix(".npz")) as z:
                n["npz"] = {k: z[k].copy() for k in ("t_ms", "r", "v")}
                if i == 0:
                    n["npz"].update({k: z[k].copy() for k in ("raster_t_ms", "raster_neuron", "raster_j")})
        out["a8"] = json.loads((res / F1_INPUTS[0]).read_text(encoding="utf-8"))
        out["ev"] = json.loads((res / F1_INPUTS[1]).read_text(encoding="utf-8"))
        with open(res / F1_INPUTS[2], newline="", encoding="utf-8") as fh:
            out["a11"] = list(csv.DictReader(fh))
        out["record_files"] = [out["mf_rel"], out["mf_rel"][:-5] + ".npz"] + [n["rel"] for n in net] + [n["rel"][:-5] + ".npz" for n in sel]
        return out
    except (OSError, ValueError, KeyError, ImportError) as exc:
        raise F.MissingInputError(f"an F1 input cannot be read: {exc}") from exc


def f1_spectrogram_settings(crit: dict, T_ramp_s: float, fs: float) -> dict:
    """The settings of the spectrogram, all from the frozen criteria and the frozen routine (nothing new): W and step from window_for_ramp (D4), the taper and the bands from the
    criteria file; detrend and scaling are those of analysis.surge_metrics.spectrogram_v (linear, power spectral density)."""
    W, step = M.window_for_ramp(T_ramp_s)
    c = crit["classifier"]
    return {"routine": "analysis.surge_metrics.spectrogram_v on the stored v (computed here, not stored)", "window_s": float(W), "step_s": float(step), "taper": c["spectrogram_taper"]["value"],
            "detrend": "linear", "scaling": "density (one-sided PSD)", "fs_hz": float(fs), "frequency_step_hz": 1.0 / float(W), "time_origin": "sample i at i/fs, window centres",
            "band_primary_hz": [float(x) for x in c["band_primary_hz"]["value"]], "total_band_hz": [float(x) for x in c["total_band_hz"]["value"]]}


def prepare_F1(raw: dict, crit: dict) -> dict:
    """Pure: the drawn data of F1 (decimated envelopes, the stored path, the computed spectrograms, the raster, the stored classes and the strip)."""
    d: dict = {}
    mf_cfg, mf = raw["mf_rec"]["config"], raw["mf"]
    if raw["mf_rec"]["status"] != "ok" or mf_cfg["run"]["kind"] != "mf" or float(mf_cfg["path"]["T_ramp_s"]) != F1_T_RAMP or mf_cfg["path"]["name"] != PATH_NAMES["P2"]:
        raise DataError("F1: the mean-field record is not the stored P2 headline at T_ramp 120 s")
    if len(raw["net"]) != 3 or [n["seed"] for n in raw["net"]] != [0, 1, 2] or sum(1 for n in raw["net_all"] if n["T"] == 10.0) != 3:
        raise DataError("F1: the network headline must be 3 seeds at 120 s and 3 at 10 s")
    for n in raw["net"]:
        c = n["rec"]["config"]
        if n["rec"]["status"] != "ok" or c["run"]["kind"] != "network" or c["network"]["N"] != 10000:
            raise DataError(f"F1: network record {n['rel']} is not an ok N = 1e4 network record")
        for k in ("eta_start", "eta_peak", "eta_H", "t_on_s", "T_ramp_s", "J0", "J_end", "J_lag_frac", "name", "profile"):
            if c["path"][k] != mf_cfg["path"][k]:
                raise DataError(f"F1: path value {k} differs between the mean-field record and {n['rel']}")
    fs = 1000.0 / float(mf_cfg["solver"]["dt_out_ms"])
    if any(1000.0 / float(n["rec"]["config"]["network"]["rate_bin_ms"]) != fs for n in raw["net"]):
        raise DataError("F1: the mean-field output step and the network rate bin differ")
    p = mf_cfg["path"]
    for k in ("eta_start", "eta_H", "eta_peak", "t_on_s", "T_ramp_s", "J0", "J_end"):
        d["path_" + k] = float(p[k])
    d["path_name"], d["path_profile"] = p["name"], p["profile"]
    t = mf["t_ms"] / 1000.0
    d["path_t_s"], d["path_eta"], d["path_J"] = t, mf["eta"], mf["J"]
    if not (np.isclose(mf["eta"][0], p["eta_start"]) and np.isclose(mf["eta"][-1], p["eta_peak"])):
        raise DataError("F1: the stored eta trace does not start at eta_start and end at eta_peak")
    for name, x, arr in [("mf", t, mf)] + [(f"net{i}", n["npz"]["t_ms"] / 1000.0, n["npz"]) for i, n in enumerate(raw["net"])]:
        d[f"{name}_n"] = int(x.size)
        for q in ("r", "v"):
            xc, lo, hi = envelope_minmax(x, arr[q], F1_COLUMNS)
            d[f"{name}_{q}_x"], d[f"{name}_{q}_lo"], d[f"{name}_{q}_hi"] = xc, lo, hi
            d[f"{name}_{q}_min"], d[f"{name}_{q}_max"] = float(np.min(arr[q])), float(np.max(arr[q]))
    # spectrograms of the stored v by the frozen routine (nothing simulated, no new setting)
    d["spec_settings"] = f1_spectrogram_settings(crit, F1_T_RAMP, fs)
    W, step = d["spec_settings"]["window_s"], d["spec_settings"]["step_s"]
    n0 = raw["net"][0]["npz"]
    for name, v in (("mf", mf["v"]), ("net0", n0["v"])):
        tc, f, S_ = M.spectrogram_v(v, fs, W, step)
        sel = f <= d["spec_settings"]["total_band_hz"][1]
        db = 10.0 * np.log10(S_[sel])
        if not np.isfinite(db).all():
            raise DataError(f"F1: spectrogram of {name} has a non-positive power value; the display transform is undefined")
        d["spec_t_s"], d["spec_f_hz"] = tc, f[sel]
        d[f"spec_{name}_db"] = db
    d["spec_db_range"] = {n: [float(d[f"spec_{n}_db"].min()), float(d[f"spec_{n}_db"].max())] for n in ("mf", "net0")}
    # one colour range for both spectrograms (13m ruling, UNVERIFIED display choice): from the network minimum to the larger maximum; mean-field cells below it take the lowest colour
    d["spec_shared_db_range"] = [d["spec_db_range"]["net0"][0], max(d["spec_db_range"]["mf"][1], d["spec_db_range"]["net0"][1])]
    d["spec_mf_below_shared"] = [int((d["spec_mf_db"] < d["spec_shared_db_range"][0]).sum()), int(d["spec_mf_db"].size)]
    # raster of seed 0: the 300 stored neurons as rows 0 to 299 in the order of raster_j
    rj, rn = n0["raster_j"], n0["raster_neuron"]
    if rj.size != int(raw["net"][0]["rec"]["config"]["network"]["n_raster"]) or not (np.diff(rj) > 0).all():
        raise DataError("F1: raster_j is not 300 increasing neuron indices")
    rank = np.searchsorted(rj, rn)
    if not (rj[np.minimum(rank, rj.size - 1)] == rn).all():
        raise DataError("F1: a raster spike belongs to a neuron that is not in raster_j")
    d["ras_t_s"], d["ras_row"], d["ras_n_rows"] = n0["raster_t_ms"] / 1000.0, rank.astype(np.int32), int(rj.size)
    d["ras_n_active_rows"] = int(np.unique(rank).size)
    # 13o (DL-494 R7): spike counts per stored neuron per F1_COUNT_BIN_S bin, from the stored spikes (exact integers; the bins cover the whole stored network record)
    t_end_net = float(n0["t_ms"][-1]) / 1000.0
    n_bins = int(np.ceil(max(t_end_net, float(d["ras_t_s"].max())) / F1_COUNT_BIN_S))
    edges = np.arange(n_bins + 1, dtype=float) * F1_COUNT_BIN_S
    col = np.minimum((d["ras_t_s"] // F1_COUNT_BIN_S).astype(np.int64), n_bins - 1)
    if (d["ras_t_s"] < 0).any():
        raise DataError("F1: a stored spike time is negative")
    count = np.zeros((d["ras_n_rows"], n_bins), dtype=np.int64)
    np.add.at(count, (d["ras_row"].astype(np.int64), col), 1)
    if int(count.sum()) != int(d["ras_t_s"].size):
        raise DataError(f"F1: the spike counts sum to {int(count.sum())}, the stored raster has {int(d['ras_t_s'].size)} spikes")
    d["ras_count"], d["ras_count_edges_s"], d["ras_count_bin_s"] = count, edges, float(F1_COUNT_BIN_S)
    # stored classes (ms10_eval.json: DL-319), checked against the records
    ev = raw["ev"]["rb1_headline"]
    h120, h10 = ev["120.0"], ev["10.0"]
    if h120["ref"]["name"] != Path(raw["mf_rel"]).stem or h120["seeds_present"] != 3 or h10["seeds_present"] != 3:
        raise DataError("F1: ms10_eval.json does not refer to the stored headline records")
    for n, s_ in zip(raw["net"], h120["seeds"]):
        if s_["name"] != n["rec"]["name"] or s_["seed"] != n["seed"]:
            raise DataError(f"F1: ms10_eval.json seed {s_['seed']} does not match record {n['rel']}")
    d["ref_class"], d["ref_onset_s"], d["ref_f_pk_hz"] = h120["ref"]["class"], float(h120["ref"]["onset_s"]), float(h120["ref"]["f_pk_hz"])
    d["cls120"], d["onset120_s"] = [s_["class"] for s_ in h120["seeds"]], [float(s_["onset_s"]) for s_ in h120["seeds"]]
    d["raw120_s"], d["fpk120_hz"] = [float(s_["onset_raw_s"]) for s_ in h120["seeds"]], [float(s_["f_pk_hz"]) for s_ in h120["seeds"]]
    d["cls10"], d["ctrl120"], d["ctrl10"] = [s_["class"] for s_ in h10["seeds"]], dict(h120["controls"]["classes"]), dict(h10["controls"]["classes"])
    d["g4_triggered"], d["rb1_verdict"] = bool(raw["ev"]["g4"]["triggered"]), raw["ev"]["rb1"]["verdict"]
    d["a_ref"] = float(raw["a8"]["chosen"]["A_ref"])
    d["zoom_windows_s"] = [[d["onset120_s"][0], d["onset120_s"][0] + F1_ZOOM_S], [d["ref_onset_s"], d["ref_onset_s"] + F1_ZOOM_S]]
    by = {(x["rb_id"], x["check_id"]): x for x in raw["a11"]}
    d["strip"] = []
    for key in F1_STRIP:
        if key not in by or by[key]["pass_or_fail"] != "FAIL":
            raise DataError(f"A11 table: {key} is not a FAIL row (strip rows are FAIL rows as logged)")
        x = by[key]
        d["strip"].append({"rb_id": x["rb_id"], "check_id": x["check_id"], "status": x["pass_or_fail"], "value": x["value"], "threshold": x["threshold"]})
    return d


def f1_strip_lines(d: dict) -> list[str]:
    return [f"{r['rb_id']} {r['check_id']}: {r['status']} ({r['value'] or 'value blank in the table'}; threshold {r['threshold'] or 'blank'}) - shown, not dropped" for r in d["strip"]]


def f1_status_lines(d: dict) -> list[str]:
    lines = [f"Stored classes (ms10_eval, DL-319): mean-field headline {d['ref_class']} (onset {d['ref_onset_s']:.3f} s, f_pk {d['ref_f_pk_hz']:.1f} Hz). Network N = 1e4, T_ramp 120 s, "
             f"seeds 0 to 2: {', '.join(d['cls120'])}; classifier onset {', '.join(f'{x:.3f}' for x in d['onset120_s'])} s; raw first crossing {', '.join(f'{x:.3f}' for x in d['raw120_s'])} s "
             f"(post hoc, feeds no gate); f_pk {', '.join(f'{x:.2f}' for x in d['fpk120_hz'])} Hz. T_ramp 10 s (not drawn): {', '.join(d['cls10'])}.",
             f"No-ramp network controls (stored classes, DL-319, not drawn): 120 s {d['ctrl120']}; 10 s {d['ctrl10']} (G4-C3). G4 triggered: {d['g4_triggered']}; RB1 {d['rb1_verdict']}.",
             strip_heading("F1")] + ["    " + s for s in f1_strip_lines(d)]
    return lines


def _f1_onset_marks(ax, d: dict, *, network: bool):
    """The stored onsets as marks in the headroom of a time panel (axes fraction on y): the mean-field D-tr onset as a vertical dashed line on every panel; on the network panels the
    stored S-sus classifier onset (marker of the class) and the three raw first crossings (nabla in the seed colours)."""
    from matplotlib import transforms
    tr = transforms.blended_transform_factory(ax.transData, ax.transAxes)
    dtr = S.get(d["ref_class"])
    ax.axvline(d["ref_onset_s"], color=dtr.colour, ls=dtr.linestyle, lw=S.F1_SIZES["event_line"], zorder=1)
    if network:
        for cls_, x in sorted(set(zip(d["cls120"], d["onset120_s"]))):
            st = S.get(cls_)
            ax.plot([x], [0.93], transform=tr, ls="none", marker=st.marker, ms=S.F1_SIZES["onset"], color=st.colour, mec=S.figure_colour("bar_edge"), mew=S.POINT_EDGE_WIDTH["class"],
                    clip_on=False, zorder=6)
        nab = S.diagram_mark("fs4_cross")
        for key, x in zip(F1_SEED_KEYS, d["raw120_s"]):
            ax.plot([x], [0.93], transform=tr, ls="none", marker=nab.marker, ms=S.F1_SIZES["onset"], color=S.diagram_mark(key).colour, mew=nab.width, clip_on=False, zorder=6)
        # 13o (DL-494 R7): the three raw first crossings stay at their stored positions; at the panel scale they lie on top of each other, which the note says
        ax.text(min(d["raw120_s"]) - 1.0, 0.8, f"3 seeds coincide ({min(d['raw120_s']):.3f} to {max(d['raw120_s']):.3f} s)", transform=tr, ha="right", va="center",
                fontsize=S.TEXT_SIZES["small"], color=S.figure_colour("text_dark"))


def _f1_env(ax, xc, lo, hi, colour, ls, fill=True):
    if fill:
        ax.fill_between(xc, lo, hi, color=colour, alpha=S.F1_SIZES["envelope_alpha"], lw=0, zorder=2)
    for y in (lo, hi):
        ax.plot(xc, y, color=colour, ls=ls, lw=S.F1_SIZES["envelope_line"], zorder=3)


def _draw_F1(d: dict, draft: bool):
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import FancyBboxPatch, Rectangle
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    fig = plt.figure(figsize=(7.4, 16.6), constrained_layout=True)
    gs = fig.add_gridspec(12, 4, height_ratios=[1.9, 0.8, 1.35, 0.8, 1.05, 1.05, 1.05, 1.05, 1.35, 1.35, 1.7, 1.5], width_ratios=[2, 1, 1, 0.1])
    mf, dtr = S.get("mean_field"), S.get(d["ref_class"])
    p2, edge, hl = S.get("P2"), S.figure_colour("bar_edge"), S.figure_colour("range_line")
    seeds = [S.diagram_mark(k) for k in F1_SEED_KEYS]
    T_END = float(d["path_t_s"][-1])

    def tidy(ax, title, ylabel, xlabel=False, red=False):
        ax.set_title(title, loc=S.TITLE_LOC, color=S.figure_colour("fail_text") if red else S.figure_colour("text_dark"))
        ax.set_ylabel(ylabel)
        if xlabel:
            ax.set_xlabel("path time (s)")

    # model schematic (13o, DL-494 R6): verbatim plan labels in boxes, our layout; no equation, no value
    sx = fig.add_subplot(gs[0, 0:4])
    sx.axis("off")
    sx.set_xlim(0, 1)
    sx.set_ylim(0, 1)
    SC = S.F1_SCHEMATIC
    faces = {"ramp": SC["ramp_face"], "net": SC["net_face"]}
    for key, head, rows in F1_SCHEMATIC:
        x0, y0, x1, y1 = F1_SCHEMATIC_BOXES[key]
        sx.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0.004,rounding_size=0.01", fc=faces.get(key, SC["box_face"]), ec=SC["box_edge"],
                                    lw=SC["edge_width"], transform=sx.transAxes, zorder=1))
        lines = [ln for r in rows for ln in textwrap.wrap(F1_SCHEMATIC_SEP.join(r), F1_SCHEMATIC_WRAP[key], break_long_words=False, break_on_hyphens=False)]
        sx.text(x0 + 0.008, y1 - 0.04, head, transform=sx.transAxes, ha="left", va="top", fontsize=S.TEXT_SIZES["schematic_head"], weight="bold", zorder=3, gid=f"schematic:{key}:head")
        sx.text(x0 + 0.008, y1 - 0.17, "\n".join(lines), transform=sx.transAxes, ha="left", va="top", fontsize=S.TEXT_SIZES["schematic"], linespacing=1.35, zorder=3,
                gid=f"schematic:{key}:rows")
    for a_, b_ in F1_SCHEMATIC_ARROWS:
        xa0, ya0, xa1, ya1 = F1_SCHEMATIC_BOXES[a_]
        xb0, yb0, xb1, yb1 = F1_SCHEMATIC_BOXES[b_]
        sx.annotate("", xy=(xb0, (yb0 + yb1) / 2), xytext=(xa1, (ya0 + ya1) / 2), xycoords="axes fraction", textcoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", color=SC["arrow"], lw=SC["arrow_width"], shrinkA=1, shrinkB=1), zorder=2)
    sx.set_title("model schematic: labels as written in the plan, layout ours (no equation, no value; the values are in (a) and (b))", loc=S.TITLE_LOC)

    # key row
    kx = fig.add_subplot(gs[1, 0:3])
    kx.axis("off")
    hs = [Line2D([], [], color=mf.colour, lw=3.0, alpha=0.55, label="mean field (stored record, min to max per pixel column)")]
    hs += [Line2D([], [], color=m.colour, ls=m.linestyle, lw=1.0, label=f"network N = 1e4, seed {i} (T_ramp 120 s)") for i, m in enumerate(seeds)]
    hs += [Line2D([], [], color=dtr.colour, ls=dtr.linestyle, lw=1.0, label=f"mean-field stored onset ({d['ref_class']}, {d['ref_onset_s']:.3f} s)"),
           Line2D([], [], ls="none", marker=S.get("S-sus").marker, ms=S.F1_SIZES["key"], color=S.get("S-sus").colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"],
                  label=f"network stored classifier onset ({d['cls120'][0]}, {d['onset120_s'][0]:.1f} s, all seeds)"),
           Line2D([], [], ls="none", marker=S.diagram_mark("fs4_cross").marker, ms=S.F1_SIZES["key"], color=edge, label="network raw first crossing (post hoc), seed colour"),
]
    kx.legend(handles=hs, loc="center", ncol=2, fontsize=S.TEXT_SIZES["legend"], frameon=False, handlelength=2.4, columnspacing=1.6, labelspacing=0.6)

    # (a) protocol from the stored path: eta(t) and J(t)
    ax = fig.add_subplot(gs[2, 0:3])
    ax.plot(d["path_t_s"], d["path_eta"], color=p2.colour, ls=p2.linestyle, lw=S.F1_SIZES["path_line"], zorder=3)
    t_end_ramp = d["path_t_on_s"] + d["path_T_ramp_s"]
    for y_ in (d["path_eta_start"], d["path_eta_H"], d["path_eta_peak"]):
        ax.axhline(y_, color=hl, ls=":", lw=S.F1_SIZES["event_line"], zorder=1)
    for x_ in (d["path_t_on_s"], t_end_ramp):
        ax.axvline(x_, color=hl, ls=":", lw=S.F1_SIZES["event_line"], zorder=1)
    ax.axvline(d["ref_onset_s"], color=dtr.colour, ls=dtr.linestyle, lw=S.F1_SIZES["event_line"], zorder=1)
    ax.set_xlim(0, T_END)
    ax.set_ylim(d["path_eta_start"] - 0.4, d["path_eta_peak"] + 1.2)
    for y_, txt in ((d["path_eta_start"], f"eta_start {d['path_eta_start']:.4f}"), (d["path_eta_H"], f"eta_H {d['path_eta_H']:.4f}"), (d["path_eta_peak"], f"eta_peak {d['path_eta_peak']:.4f}")):
        ax.text(T_END * 0.995, y_ + 0.08, txt, ha="right", va="bottom", fontsize=S.TEXT_SIZES["small"], color=S.figure_colour("text_dark"), zorder=5)
    ax.text(d["path_t_on_s"] + 0.8, d["path_eta_peak"] + 0.75, f"t_on = {d['path_t_on_s']:g} s", ha="left", va="center", fontsize=S.TEXT_SIZES["small"], color=S.figure_colour("text_dark"))
    ax.text(t_end_ramp - 0.8, d["path_eta_peak"] + 0.75, f"end of ramp = t_on + T_ramp = {t_end_ramp:g} s", ha="right", va="center", fontsize=S.TEXT_SIZES["small"], color=S.figure_colour("text_dark"))
    tidy(ax, f"(a) ramp protocol of the headline path ({d['path_name']}, {d['path_profile']}, T_ramp {d['path_T_ramp_s']:g} s): eta(t) as stored", "eta")
    ax.tick_params(labelbottom=False)
    ax = fig.add_subplot(gs[3, 0:3], sharex=ax)
    ax.plot(d["path_t_s"], d["path_J"], color=S.get("P3").colour, ls="-", lw=S.F1_SIZES["path_line"], zorder=3)
    for x_ in (d["path_t_on_s"], t_end_ramp):
        ax.axvline(x_, color=hl, ls=":", lw=S.F1_SIZES["event_line"], zorder=1)
    ax.set_ylim(d["path_J0"] - 3.0, d["path_J_end"] + 3.0)
    tidy(ax, f"(b) J(t) as stored (J0 {d['path_J0']:g} to J_end {d['path_J_end']:g}); Delta, I constant (stored)", "J")
    ax.tick_params(labelbottom=False)

    # (c) to (f) r(t) and v(t): mean field above network, same y range per quantity
    for row, (q, qn) in enumerate((("r", "r"), ("v", "v"))):
        lo_all = min(d[f"{n}_{q}_min"] for n in ("mf", "net0", "net1", "net2"))
        hi_all = max(d[f"{n}_{q}_max"] for n in ("mf", "net0", "net1", "net2"))
        rng = hi_all - lo_all
        ylim = (lo_all - 0.04 * rng, hi_all + 0.20 * rng)
        a1 = fig.add_subplot(gs[4 + 2 * row, 0:3], sharex=ax)
        _f1_env(a1, d[f"mf_{q}_x"], d[f"mf_{q}_lo"], d[f"mf_{q}_hi"], mf.colour, "-")
        _f1_onset_marks(a1, d, network=False)
        a1.set_ylim(*ylim)
        tidy(a1, f"({'ce'[row]}) {qn}(t), mean field (stored record)", f"{qn} (stored)")
        a1.tick_params(labelbottom=False)
        a2 = fig.add_subplot(gs[5 + 2 * row, 0:3], sharex=ax)
        for i, m in enumerate(seeds):
            _f1_env(a2, d[f"net{i}_{q}_x"], d[f"net{i}_{q}_lo"], d[f"net{i}_{q}_hi"], m.colour, m.linestyle, fill=False)
        _f1_onset_marks(a2, d, network=True)
        a2.set_ylim(*ylim)
        tidy(a2, f"({'df'[row]}) {qn}(t), network N = 1e4, seeds 0 to 2 (same y range as the mean field)", f"{qn} (stored)")
        a2.tick_params(labelbottom=False)
    # (g), (h) spectrograms of the stored v (frozen routine)
    sp = d["spec_settings"]
    for k, (name, ttl) in enumerate((("mf", "(g) spectrogram of v, mean field"), ("net0", "(h) spectrogram of v, network seed 0"))):
        a = fig.add_subplot(gs[8 + k, 0:3], sharex=ax)
        im = a.pcolormesh(d["spec_t_s"], d["spec_f_hz"], d[f"spec_{name}_db"], shading="nearest", cmap=S.SPECTROGRAM_CMAP, vmin=d["spec_shared_db_range"][0], vmax=d["spec_shared_db_range"][1], rasterized=True)
        for b in sp["band_primary_hz"]:
            a.axhline(b, color=S.HALO_COLOUR, ls="--", lw=S.F1_SIZES["event_line"], zorder=4)
        a.set_yticks(sorted({0.0, *sp["band_primary_hz"], sp["total_band_hz"][1], 50.0, 75.0, 125.0}))
        if k == 1:
            cb = fig.colorbar(im, cax=fig.add_subplot(gs[8:10, 3]), extend="min")
            cb.set_label("10 log10 PSD (one range for (g) and (h))")
        a.axvline(d["ref_onset_s"], color=dtr.colour, ls=dtr.linestyle, lw=S.F1_SIZES["event_line"], zorder=4)
        a.set_ylim(0, sp["total_band_hz"][1])
        tidy(a, ttl + f" (W {sp['window_s']:g} s, step {sp['step_s']:g} s, {sp['taper']}; shared dB range)", "frequency (Hz)", xlabel=(k == 1))
    # (i) spike counts of seed 0 (13o, DL-494 R7: counts per stored neuron per bin, exact, no smoothing), (j) and (k) the stored spikes of two 1 s windows, marked on (i)
    tick = S.RASTER_MARKS["zoom"]
    specs = ((gs[10, 0], f"(i) spike count per stored neuron per {d['ras_count_bin_s']:g} s, seed 0", None),
             (gs[10, 1], f"(j) {d['zoom_windows_s'][0][0]:.3f} to {d['zoom_windows_s'][0][1]:.3f} s", d["zoom_windows_s"][0]),
             (gs[10, 2], f"(k) {d['zoom_windows_s'][1][0]:.3f} to {d['zoom_windows_s'][1][1]:.3f} s", d["zoom_windows_s"][1]))
    first_r = None
    for pos, ttl, win in specs:
        a = fig.add_subplot(pos, sharey=first_r) if first_r is not None else fig.add_subplot(pos)
        first_r = first_r if first_r is not None else a
        if win is None:
            e = d["ras_count_edges_s"]
            top, n_above, _n = f1_count_range(d)
            im = a.pcolormesh(e, np.arange(d["ras_n_rows"] + 1) - 0.5, d["ras_count"], cmap=S.RASTER_COUNT_CMAP, vmin=0, vmax=top, shading="flat", rasterized=True)
            cb = fig.colorbar(im, cax=fig.add_subplot(gs[10, 3]), extend="max")
            cb.set_label(f"spikes per {d['ras_count_bin_s']:g} s (top colour: {top:g} and more)")
            for lab, w in zip("jk", d["zoom_windows_s"]):
                a.add_patch(Rectangle((w[0], -0.5), w[1] - w[0], d["ras_n_rows"], fill=False, ec=S.F1_RASTER["window_frame"], lw=S.F1_RASTER["window_width"], zorder=4))
                a.text(w[1] + 1.0, d["ras_n_rows"] - 3, f"({lab})", ha="left", va="top", fontsize=S.TEXT_SIZES["small"], color=S.F1_RASTER["window_frame"], zorder=5)
            a.set_xlim(0, T_END)
            a.set_ylabel("stored neuron (row)")
        else:
            m = (d["ras_t_s"] >= win[0]) & (d["ras_t_s"] <= win[1])
            a.plot(d["ras_t_s"][m], d["ras_row"][m], ls="none", marker=tick, ms=S.F1_SIZES["raster_zoom"], color=edge, mew=S.F1_SIZES["raster_zoom_width"])
            a.set_xlim(*win)
            a.tick_params(labelleft=False)
        a.set_ylim(-0.5 if win is None else -1, d["ras_n_rows"] - 0.5 if win is None else d["ras_n_rows"])
        tidy(a, ttl, "stored neuron (row)" if win is None else "", xlabel=True)
    # status block
    axs = fig.add_subplot(gs[11, 0:3])
    axs.axis("off")
    lines = [ln for t_ in f1_status_lines(d) for ln in textwrap.wrap(t_, width=150, subsequent_indent="        ")]
    axs.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=S.TEXT_SIZES["status"], linespacing=1.25)
    return _style_text(fig, F1_FOOTER if draft else "")


def f1_caption_notes(d: dict) -> tuple:
    """Sentences about what is and is not drawn (13l). Values come from the prepared data; only the wording is typed here."""
    sp = d["spec_settings"]
    return (
        "Panels (a) and (b) draw the ramp protocol of the stored headline record (P2, " + d["path_name"] + ", " + d["path_profile"] + ", T_ramp " + f"{d['path_T_ramp_s']:g}" + " s): eta(t) and J(t) are the "
        "stored arrays, and t_on, the end of the ramp and eta_start, eta_H and eta_peak are the stored path values (read from the record, not retyped); the headline is the T_ramp 120 s path, "
        "so the network records of T_ramp 10 s are not drawn (their stored classes are in the status block).",
        "Panels (c) to (f) draw r(t) and v(t) of the stored mean-field record and of the three stored network records at N = 1e4, T_ramp 120 s, seeds 0, 1 and 2, on the same y range per quantity: "
        "all three stored seeds are drawn and none is chosen, and N = 1e4 is the only N of the S8 headline (the 3e4 records belong to S9 and are not drawn here). Each series is a min-to-max "
        "envelope per pixel column (" + f"{F1_COLUMNS}" + " blocks of whole samples; display decimation, UNVERIFIED rule): the extremes of every block and of the whole series are the stored "
        "extremes, nothing is smoothed or offset. The network does not reproduce the mean-field class at the headline (claim limit G4-C1): the marks are stored values (ms10_eval, DL-319): "
        "the mean-field onset (" + d["ref_class"] + f", {d['ref_onset_s']:.3f} s), the network classifier onset ({d['cls120'][0]}, {d['onset120_s'][0]:.1f} s in all three seeds) and the "
        "network raw first crossings (post hoc, feeding no gate), which differ from the mean-field onset and are not hidden; the three raw crossings are drawn at their stored times "
        f"({', '.join(f'{x:.3f}' for x in d['raw120_s'])} s), which lie on top of each other at the panel scale, and a note says that the 3 seeds coincide. Network classes cannot separate ramp-driven from non-ramp "
        "records (G4-C3, DL-325): the no-ramp network controls reach the surge classes " + ", ".join(f"{k} {v}" for k, v in d["ctrl10"].items()) + " at the 10 s headline (stored, DL-319), S+ in S9 at N = 3e3 and 1e4 and at "
        "map cell (24,26) (DL-325; not drawn here); the stored controls of the 120 s headline are " + ", ".join(f"{k} {v}" for k, v in d["ctrl120"].items()) + " (DL-319, DL-323), the class of the three ramp seeds there. "
        "Only seed 0 is drawn in the raster and the network spectrogram; seeds 1 and 2 are not drawn there. "
        "RB1 FAILED (headline 10 s, headline 120 s, cells 1 of 4; DL-319, DL-320) and G7 is not passed (DL-228: the NC1 network is S+); G4 was triggered and is report-only (DL-323).",
        "Panels (g) and (h) are NOT stored: they are computed from the stored v of the mean-field record and of network seed 0 by the frozen classifier routine "
        "analysis.surge_metrics.spectrogram_v with the frozen settings printed above (no new setting; UNVERIFIED reading of the script rule that a figure script never simulates). Only the "
        f"rows from 0 to {sp['total_band_hz'][1]:g} Hz (the total band) are drawn; the power is shown as 10 log10 PSD on ONE colour range for both panels, from " + f"{d['spec_shared_db_range'][0]:.2f} dB (the minimum of the network panel) to {d['spec_shared_db_range'][1]:.2f} dB "
        f"(the larger of the two maxima). The stored mean-field range is {d['spec_db_range']['mf'][0]:.2f} to {d['spec_db_range']['mf'][1]:.2f} dB, so {d['spec_mf_below_shared'][0]} of "
        f"{d['spec_mf_below_shared'][1]} mean-field cells lie below the shared minimum and are drawn in its lowest colour (arrow on the colour bar; their values are in the drawn data); a range that "
        "covers both would flatten the network panel (display choice, UNVERIFIED). The dashed lines are the edges of the primary band. The window time axis is the classifier's (sample i at i/fs); the stored network time stamp is the end of the 1 ms bin. "
        f"Panel (i) draws, for the 300 stored neurons of seed 0, the number of stored spikes per neuron in each {d['ras_count_bin_s']:g} s bin from 0 s, computed from the stored spikes "
        f"(display aggregation, UNVERIFIED; every count is exact, nothing is smoothed, and the counts sum to the {int(d['ras_count'].sum())} stored spikes; {d['ras_n_active_rows']} of the "
        f"{d['ras_n_rows']} rows spike); the colour range runs from 0 to {f1_count_range(d)[0]:g} spikes, the {S.F1_RASTER['top_percentile']:g}th percentile of the counts, and the "
        f"{f1_count_range(d)[1]} of {f1_count_range(d)[2]} cells above it (up to {int(d['ras_count'].max())}) take the top colour (arrow on the colour bar; display choice, UNVERIFIED); panels (j) and (k) draw the spikes as stored in windows of {F1_ZOOM_S:g} s that start at the stored network classifier onset and at the stored "
        "mean-field onset, and the two windows are framed on (i). The schematic above (a) is our layout of labels written in the plan (UNVERIFIED as a drawing); it carries no equation "
        "and no value. A_ref (reading a) is " + f"{d['a_ref']:.6f}" + " (A8). Peak frequencies are the classifier's spectral peaks (MS11-C3). "
        "Every D8-dependent class is provisional (D8 open).",
    )


def make_F1(res=None, out_dir=None, *, tag_build: bool = False, take_home=F1_TAKE_HOME, claim_limit_ids=F1_CLAIM_LIMITS,
            script="scripts/fig_F1.py", root=None) -> dict:
    """Build F1 from results/. Returns {'prov', 'paths', 'timing_s', 'drawn_sha256', 'caption'}. tag_build=True needs a clean tree (figprov)."""
    F.require_buildable("F1")
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "F1"
    t = {"start": time.perf_counter()}
    raw = load_F1(res)
    t["load"] = time.perf_counter()
    crit, _ = F.K.load_frozen_criteria(root)
    d = prepare_F1(raw, crit)
    t["prepare"] = time.perf_counter()
    rows = []
    recs = {"mf_headline": raw["mf_rec"], **{f"net_120s_seed{n['seed']}": n["rec"] for n in raw["net"]}}
    for key, rec in recs.items():
        for r in make_param_table(rec["config"]):
            rows.append({**r, "panel": key, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    cap = CAP.build_caption("F1", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=[r for r in rows if r["key"] in F1_CAPTION_KEYS],
                            spectrogram=d["spec_settings"], symbol_keys=(), notes=f1_caption_notes(d), limit_labels=CLAIM_LIMIT_LABELS)
    import matplotlib.pyplot as plt
    fig = _draw_F1(d, draft=not tag_build)
    out.mkdir(parents=True, exist_ok=True)
    pdf, png = out / "F1.pdf", out / "F1.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=S.PNG_DPI)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    cap_path, dig_path = out / "F1_caption.txt", out / "F1_drawn_data_sha256.txt"
    from .. import provenance as P
    drawn = drawn_data_sha256(d)
    P.atomic_write_text(cap_path, cap.text + "\n")
    P.atomic_write_text(dig_path, drawn + "\n")
    warnings = []
    for k, rec in recs.items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true")
    prov = F.write_figure_provenance(
        "F1", script=script, inputs=[res / p for p in F1_INPUTS] + [res / p for p in raw["record_files"]], outputs=[pdf, png, cap_path, dig_path], params_rows=rows,
        modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py", "src/mprsurge/plotting/nordlie.py",
                 "src/mprsurge/plotting/figprov.py", "src/mprsurge/analysis/surge_metrics.py"],
        configs=["configs/base.yaml", "configs/S5_ramp.yaml", "configs/ms10/ms10_net.yaml", "configs/robustness_criteria.yaml"], claim_limits=cap.claim_limits,
        input_tables=[{"path": res / F1_INPUTS[2], "rows": len(raw["a11"])}], spectrogram=d["spec_settings"], tag_build=tag_build, out_dir=out, root=root, warnings=warnings,
        wall_time_s=time.perf_counter() - t["start"])
    nordlie_path = out / "F1_nordlie.md"
    N.write_nordlie(out / "F1_params.csv", out / "F1_provenance.json", nordlie_path, root=root)
    t["end"] = time.perf_counter()
    timing = {"load_s": t["load"] - t["start"], "prepare_s": t["prepare"] - t["load"], "draw_s": t["draw"] - t["prepare"],
              "provenance_and_nordlie_s": t["end"] - t["draw"], "total_s": t["end"] - t["start"]}
    return {"prov": prov, "paths": [pdf, png, cap_path, dig_path, out / "F1_params.csv", out / "F1_provenance.json", nordlie_path],
            "timing_s": timing, "drawn_sha256": drawn, "caption": cap.text}


# ---- F5 (13m) -------------------------------------------------------------------------------------------------------------------------------------
# Paths relative to results/. Tables first (docs/ms13_conventions.md M13-12): the maps, the subgrid agreement, the network cells and the class points come from stored tables and
# are drawn as stored. A logged exception (DL-490, UNVERIFIED): the per-seed metric points of F5c (f_pk, onset, duration) are RECOMPUTED from the stored S9 and S9_ctrl series
# with the frozen classifier, by the same call the MS10 evaluation used (analysis.ms10_eval.read_lists with the frozen run lists, the frozen criteria and table21 = True), one
# record at a time; the recomputed per-seed classes must equal the stored ones and the recomputed counts, min, median and max must equal the stored ones of ms10_eval.json
# (exact), else the data step stops with a DataError (stop rule). No S7 series is opened. scripts/ms13_inputs.py INPUTS["F5"] must name the same files (test).
F5_INPUTS = (
    "A9/a9_regime_map_v2.parquet",                    # 1,226 rows: map 1 (900), map 2 (325), headline (1); class per cell (DL-243, DL-244, DL-249, DL-260)
    "A9/a9_subgrid_agreement.parquet",                # 225 rows: D24 and P-1 agreement per subgrid cell (DL-242, DL-255)
    "ms10/eval/ms10_eval.json",                       # RB1 cells (4 cells, per-seed network classes, 30 s mean-field companion), N sweep (stored counts, min, median, max), G4
    "ms10/10g/record_classes.tsv",                    # per-record class of the S8 cells, S9 and S9_ctrl records (103 rows)
    "A11/a11_robustness.csv",                         # stored A11 table: status rows and the FAIL-row strip
)
F5_CELL_DIR, F5_CELL_COUNT = "S8/S8_cells", 12
F5_S9_DIR, F5_S9_COUNT = "S9/S9", 40
F5_CTRL_DIR, F5_CTRL_COUNT = "S9/S9_ctrl", 12
F5_ORIGIN_RECORDS = (                                 # mean-field records whose t_ms the frozen evaluation call reads for the R27 time-origin check (json and npz)
    "S5/ramp/S5ramp/S5ramp_0000_240de3ef73be", "S5/ramp/p2_linear/p2_linear_0004_4f4756348cd8", "S8/mf/S8_mf_head60/S8_mf_head60_0000_0080d385accd",
    "S8/mf/S8_mf_cells/S8_mf_cells_0000_081b77a5f999", "S8/mf/S8_mf_cells/S8_mf_cells_0001_908ef5a1c420", "S8/mf/S8_mf_cells/S8_mf_cells_0002_8cf8eb1029e6",
    "S8/mf/S8_mf_cells/S8_mf_cells_0003_1474ff58c0a4",
)
# files outside results/ that the frozen evaluation call opens (run lists, frozen configs, the S8 candidate table); the data-step test allows exactly these directories
F5_FROZEN_CONFIG_READS = ("configs", "docs/ms10_10b_s8_candidates.csv")
F5_N = (1000, 3000, 10000, 30000)
F5_SEEDS, F5_CTRL_SEEDS = 10, 3
F5_NET_CLASSES = ("S+", "S-rel", "S-abs", "S-sus", "NS")
F5_MAP_CLASSES = ("D-tr", "D-none")
F5_METRICS = (("f_pk_hz", "f_pk (Hz)"), ("onset_s", "onset (s)"), ("duration_ms", "duration (ms)"))
F5_CONTROL_METRICS = ("f_pk_hz", "onset_s")           # the evaluation read the controls without the Table 2.1 fields: no duration (S9_ctrl)
F5_STRIP = (("RB1", "headline_10s"), ("RB1", "headline_120s"), ("RB1", "cells_30s"), ("RB1", "overall"), ("RB2", "noisy_subgrid_agreement"), ("RB2", "headline_class_kept_1.0_sigma"))
F5_STATUS = (("RB4", "parameter_perturbation"), ("RB1", "n_rule_60s"))
F5_CAPTION_KEYS = ("model.type", "model.ref_point", "model.J", "model.Delta", "model.tau_ms", "model.tau_d_ms", "path.name", "path.profile", "path.T_ramp_s", "path.eta_H",
                   "network.N", "network.het_dist", "solver.method", "noise.sigma", "seeds.root_seed")
F5_SLOT = 17.0                                        # x width of one N group on the F5c axes: 10 ramp seeds, a gap, 3 control seeds (a layout slot, carries no value)
F5_CTRL_X0 = 11.0
F5_FOOTER = draft_footer("F5")

# Ruled (RULED_DL, 13p R13); first proposed for the reviewer's ruling (13m prompt, step 3); every statement is from a logged result (DL numbers in the text) and the numbers are checked against the stored tables
# by tests/test_fig_F5.py.
F5_TAKE_HOME = (
    "In mode D (noise-free mean field) the surge class D-tr fills 760 of the 900 cells of map 1 (84.4%, T_ramp 120 s; D-none 140) and 296 of the 325 cells of "
    "map 2 (D-none 29), so a surge class is not confined to a few cells and G5 continues; RB4 passed (0 of 14 changed, 64 of 64 unchanged) (DL-235, DL-237, DL-258, DL-260). The map "
    "statements are mode D and make no claim that the regime map is robust to noise: on the 225-cell noisy subgrid the frozen D24 rule FAILED (97 of 225 cells agree = 43.1%, 203 "
    "needed; 118 of 225 on the three Table 2.1 categories, our reading), and the post-hoc view P-1 (173 of 225 = 76.9%) feeds no gate (DL-242, DL-255). The network at N = 1e4 "
    "disagrees with the mean field at 3 of the 4 map cells (T_ramp 30 s; RB1 cells 1 of 4; G4 triggered; DL-320, DL-323, DL-325). Against N = 1e3, 3e3, 1e4 and 3e4 the 10 ramp "
    "seeds per N fall in S-sus and S-abs (S+ in 6 seeds at N = 3e3, NS in 1 at N = 1e4), and the no-ramp controls also reach surge classes, so network classes do not separate "
    "ramp-driven from non-ramp records (DL-321, DL-325, G4-C3)."
)
# Ruled (RULED_DL, 13p R13): the limits of docs/ms13_plan.md section 5 whose right-hand column lists F5 and that are defined in docs/claim_limit_labels.md (17 labels). The plan labels RB1 FAIL, RB2
# FAIL and D24 failed are written in plain words with their DL numbers in the take-home, the caption and the strip. MS9(e)-3 and MS9(e)-4 are listed for F5 by the plan although F5
# draws no A9 failure label (F6 does); they are kept because the plan's table lists them. Listed, not decided. 13o (DL-494 R2, R5, R9; DL-495): the plan labels RB1 FAIL, RB2 FAIL
# and D24 failed are carried with their definitions, and MS9(e)-3 and MS9(e)-4 are carried as not applicable (no A9 failure label is drawn).
F5_CLAIM_LIMITS = ("MS11-C7", "MS12-C1", "MS9(e)-1", "MS9(e)-2", "MS9(e)-3", "MS9(e)-4", "MS9(e)-5", "MS9(e)-6", "DL-163-D1", "DL-163-D2", "G4-C1", "G4-C2", "G4-C3", "G4-C4",
                   "MS11-C1", "MS11-C2", "MS11-C3", "RB1 FAIL (plan label)", "RB2 FAIL (plan label)", "D24 failed (plan label)")
F5_NOT_APPLICABLE = {"MS9(e)-3": "no A9 failure label is drawn in F5 (F6 draws them)", "MS9(e)-4": "no A9 failure label is drawn in F5 (F6 draws them)"}


def _f5_files(res: Path, rels) -> list[Path]:
    return [res / f"{r}.json" for r in rels] + [res / f"{r}.npz" for r in rels]


def f5_record_files(res: Path, names: dict) -> list[Path]:
    """Every stored record file the data step opens: the S8 cell json (config), the S9 and S9_ctrl json and npz, the mean-field origin records (json and npz)."""
    out = [res / F5_CELL_DIR / f"{n}.json" for n in names["cells"]]
    for d, key in ((F5_S9_DIR, "s9"), (F5_CTRL_DIR, "ctrl")):
        out += _f5_files(res, [f"{d}/{n}" for n in names[key]])
    return out + _f5_files(res, F5_ORIGIN_RECORDS)


def load_F5(res=None) -> dict:
    """Open the stored tables of F5_INPUTS, the 12 S8 cell records (json) and, through the frozen MS10 evaluation call, the S9 and S9_ctrl series one record at a time.
    Returns the content; nothing is simulated and nothing under results/ is written."""
    res = Path(res) if res is not None else results_dir()
    for rel in F5_INPUTS:
        if not (res / rel).is_file():
            raise F.MissingInputError(f"input file not found: {res / rel}")
    try:
        import pandas as pd
        from ..analysis import a7 as A7
        from ..analysis import ms10_eval as E
        out: dict = {"a9": pd.read_parquet(res / F5_INPUTS[0]), "sub": pd.read_parquet(res / F5_INPUTS[1]), "ev": json.loads((res / F5_INPUTS[2]).read_text(encoding="utf-8"))}
        with open(res / F5_INPUTS[3], newline="", encoding="utf-8") as fh:
            out["tsv"] = list(csv.DictReader(fh, delimiter="\t"))
        with open(res / F5_INPUTS[4], newline="", encoding="utf-8") as fh:
            out["a11"] = list(csv.DictReader(fh))
        cells = sorted((res / F5_CELL_DIR).glob("*.json"))
        out["cell_recs"] = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in cells if not p.name.endswith(".dry.json")}
        fi, gate = A7.frozen_inputs()
        out["ch"], out["gate"] = E.load_choices(None), gate
        by = E.read_lists(("S9", "C2_S9"), fi, table21=True)       # the call of scripts/evaluate_ms10.py, restricted to the two lists F5c draws; one record in memory at a time
        out["s9"], out["ctrl"] = by["S9"], by["C2_S9"]
        out["names"] = {"cells": sorted(out["cell_recs"]), "s9": sorted(r["name"] for r in out["s9"]), "ctrl": sorted(r["name"] for r in out["ctrl"])}
        out["record_files"] = f5_record_files(res, out["names"])
        out["E"] = E
        return out
    except (OSError, ValueError, KeyError, ImportError) as exc:
        raise F.MissingInputError(f"an F5 input cannot be read: {exc}") from exc


def _f5_grid(sub, row_col: str, col_col: str, n_rows: int, n_cols: int, name: str):
    """(class array [row, col], row axis values, column axis values) of a complete map; the axis values must be constant along the other index."""
    if len(sub) != n_rows * n_cols or sorted(sub["i"].unique().tolist()) != list(range(n_rows)) or sorted(sub["j"].unique().tolist()) != list(range(n_cols)):
        raise DataError(f"A9 {name}: {len(sub)} rows, not a complete {n_rows} x {n_cols} grid")
    cls = np.empty((n_rows, n_cols), dtype="<U8")
    rows_v, cols_v = np.full(n_rows, np.nan), np.full(n_cols, np.nan)
    for _, r in sub.iterrows():
        i, j = int(r["i"]), int(r["j"])
        cls[i, j] = str(r["class"])
        for arr, k, v in ((rows_v, i, float(r[row_col])), (cols_v, j, float(r[col_col]))):
            if np.isnan(arr[k]):
                arr[k] = v
            elif arr[k] != v:
                raise DataError(f"A9 {name}: the axis value of index {k} is not constant ({arr[k]} and {v})")
    if not set(np.unique(cls)) <= set(F5_MAP_CLASSES):
        raise DataError(f"A9 {name}: classes {sorted(set(np.unique(cls)))} are not D-tr and D-none")
    return cls, rows_v, cols_v


def _f5_state(agree, tie) -> np.ndarray:
    """0 agree, 1 disagree (not a tie), 2 tie (a tie is a disagreement by the D24 rule; it is its own state here so that no tie is hidden among the disagreements)."""
    agree, tie = np.asarray(agree, bool), np.asarray(tie, bool)
    if (agree & tie).any():
        raise DataError("a subgrid cell is both agree and tie")
    return np.where(agree, 0, np.where(tie, 2, 1)).astype(np.int8)


def _f5_med(E, xs) -> dict:
    return E._med_range(xs)


def prepare_F5(raw: dict) -> dict:
    """Pure: stored content -> the arrays and numbers that are drawn. Keys are flat names. Stops (DataError) if a recomputed value differs from a stored one."""
    d: dict = {}
    a9, ev, E = raw["a9"], raw["ev"], raw["E"]
    if len(a9) != 1226 or sorted(a9["map"].astype(str).unique()) != ["1", "2", "headline"]:
        raise DataError(f"A9 table v2: {len(a9)} rows, maps {sorted(a9['map'].astype(str).unique())}")
    m1, m2 = a9[a9["map"].astype(str) == "1"], a9[a9["map"].astype(str) == "2"]
    d["map1_class"], d["map1_Delta"], d["map1_tau_d_ms"] = _f5_grid(m1, "Delta", "tau_d_ms", 30, 30, "map 1")
    d["map2_class"], d["map2_J0"], d["map2_T_ramp_s"] = _f5_grid(m2, "J0", "T_ramp_s", 25, 13, "map 2")
    if set(m1["T_ramp_s"]) != {120.0} or set(m2["Delta"]) != {0.3} or set(m2["tau_d_ms"]) != {5.0}:
        raise DataError("A9 maps: map 1 is not at T_ramp 120 s, or map 2 is not at Delta 0.3 and tau_d 5 ms")
    for k, c in (("map1", d["map1_class"]), ("map2", d["map2_class"])):
        d[f"{k}_n"] = int(c.size)
        d[f"{k}_n_surge"] = int((c == "D-tr").sum())
        d[f"{k}_n_none"] = int((c == "D-none").sum())
    d["g5_threshold_cells"] = 0.03 * d["map1_n"]
    d["g5_triggered"] = bool(d["map1_n_surge"] < d["g5_threshold_cells"])
    # subgrid agreement: D24 (frozen, FAILED) and P-1 (post hoc)
    sub = raw["sub"].sort_values(["i", "j"]).reset_index(drop=True)
    if len(sub) != 225 or sub[["i", "j"]].drop_duplicates().shape[0] != 225:
        raise DataError(f"A9 subgrid table: {len(sub)} rows")
    if set(sub["d24_frozen_status"]) != {"FAILED (DL-242)"} or set(sub["p1_status"]) != {"post hoc, feeds no gate (DL-255)"}:
        raise DataError("A9 subgrid table: the status columns are not 'FAILED (DL-242)' and 'post hoc, feeds no gate (DL-255)'")
    for i_, j_, c_ in zip(sub["i"], sub["j"], sub["map1_class"]):
        if d["map1_class"][int(i_), int(j_)] != c_ or d["map1_class"][int(i_), int(j_)] != sub.loc[(sub["i"] == i_) & (sub["j"] == j_), "deterministic_class"].iloc[0]:
            raise DataError(f"A9 subgrid cell ({i_}, {j_}): the stored map-1 class differs from the map")
    d["sub_i"], d["sub_j"] = sub["i"].to_numpy(np.int64), sub["j"].to_numpy(np.int64)
    d["d24_state"], d["p1_state"] = _f5_state(sub["d24_cell_agrees"], sub["d24_tie"]), _f5_state(sub["p1_cell_agrees"], sub["p1_tie"])
    for k in ("d24", "p1"):
        d[f"{k}_n_agree"], d[f"{k}_n_disagree"], d[f"{k}_n_tie"] = (int((d[f"{k}_state"] == s).sum()) for s in (0, 1, 2))
    d["sub_n"] = int(len(sub))
    d["d24_needed"] = 203                                   # 90 percent of 225 (the stored A11 threshold text names it; checked below)
    cat = lambda c: "surge" if c in ("S+", "S-rel", "S-abs") else c          # the three Table 2.1 categories: surge, S-sus, NS (reading ours, UNVERIFIED, DL-242)
    n_cat = 0
    for _, r in sub.iterrows():
        cnt: dict = {}
        for k, v in json.loads(r["d24_ramp_class_counts"]).items():
            cnt[cat(k)] = cnt.get(cat(k), 0) + int(v)
        top = sorted(cnt.items(), key=lambda kv: -kv[1])
        tie = len(top) > 1 and top[0][1] == top[1][1]
        n_cat += int(not tie and top[0][0] == ("surge" if r["deterministic_class"] == "D-tr" else "NS"))
    d["d24_n_agree_categories"] = n_cat
    # the 4 network cells: the stored RB1 cell comparison, matched to map-1 cells by (Delta, tau_d)
    cells_ev = ev["rb1_cells"]["cells"]
    by_cell: dict = {}
    for name, rec in raw["cell_recs"].items():
        c = rec["config"]
        by_cell.setdefault((float(c["model"]["Delta"]), float(c["model"]["tau_d_ms"]), float(c["path"]["T_ramp_s"])), []).append(name)
    if len(by_cell) != 4 or any(len(v) != 3 for v in by_cell.values()):
        raise DataError(f"S8 cell records: {len(by_cell)} cells, {[len(v) for v in by_cell.values()]} records each")
    tsv = {r["name"]: r for r in raw["tsv"] if r["list"] == "S8"}
    ci, cj, cD, ctau, cT, cmap, cmf, cmfon, cnet, cagree = [], [], [], [], [], [], [], [], [], []
    for g in range(4):
        ce = cells_ev[str(g)]
        found = []
        for (D, t, T), names in by_cell.items():
            seeds = sorted(names, key=lambda n: int(tsv[n]["seed"]))
            if [tsv[n]["class"] for n in seeds] == ce["classes"] and all(int(tsv[n]["group"]) == g for n in seeds):
                found.append((D, t, T, seeds))
        if len(found) != 1:
            raise DataError(f"RB1 cell {g}: {len(found)} S8 cell record groups carry its stored classes")
        D, t, T, seeds = found[0]
        hit = np.argwhere((np.abs(d["map1_Delta"][:, None] - D) < 1e-9) & (np.abs(d["map1_tau_d_ms"][None, :] - t) < 1e-9))
        if len(hit) != 1:
            raise DataError(f"RB1 cell {g}: Delta {D}, tau_d {t} match {len(hit)} map-1 cells (tolerance 1e-9)")
        i_, j_ = int(hit[0][0]), int(hit[0][1])
        if d["map1_class"][i_, j_] != ce["stored_120s_class"] or T != 30.0:
            raise DataError(f"RB1 cell {g}: the stored 120 s class {ce['stored_120s_class']} differs from the map class {d['map1_class'][i_, j_]}, or T_ramp {T} is not 30 s")
        ci.append(i_), cj.append(j_), cD.append(D), ctau.append(t), cT.append(T), cmap.append(str(d["map1_class"][i_, j_])), cmf.append(ce["ref"]["class"])
        cmfon.append(float("nan") if ce["ref"]["onset_s"] is None else float(ce["ref"]["onset_s"]))
        cnet.append(list(ce["classes"])), cagree.append(bool(ce["agrees"]))
    d["cell_i"], d["cell_j"] = np.array(ci), np.array(cj)
    d["cell_Delta"], d["cell_tau_d_ms"], d["cell_T_ramp_s"] = np.array(cD), np.array(ctau), np.array(cT)
    d["cell_map_class"], d["cell_mf30_class"], d["cell_mf30_onset_s"] = np.array(cmap), np.array(cmf), np.array(cmfon)
    d["cell_net_class"], d["cell_agree"] = np.array(cnet), np.array(cagree)
    d["cells_n_agree"], d["cells_n_disagree"] = int(d["cell_agree"].sum()), int((~d["cell_agree"]).sum())
    if (d["cells_n_agree"], ev["rb1_cells"]["n_agree"], ev["rb1_cells"]["disagree"]) != (1, 1, 3):
        raise DataError("RB1 cells: the stored agreement count is not 1 of 4 (DL-320 says 1 of 4, 3 disagree)")
    d["g4_triggered"] = bool(ev["g4"]["triggered"])
    # F5c: recomputed per-seed values against the stored classes and the stored counts, min, median and max
    ch, tsv_all = raw["ch"], {(r["list"], r["name"]): r for r in raw["tsv"]}
    names = [m for m, _ in F5_METRICS]
    stored = ev["N_sweep"]["by_N"]
    cls = np.empty((4, F5_SEEDS), dtype="<U5")
    val = {m: np.full((4, F5_SEEDS), np.nan) for m in names}
    ccls = np.empty((4, F5_CTRL_SEEDS), dtype="<U5")
    cval = {m: np.full((4, F5_CTRL_SEEDS), np.nan) for m in F5_CONTROL_METRICS}
    d["metric_undefined"] = np.zeros((4, len(names)), dtype=np.int64)
    for k, N in enumerate(F5_N):
        g = sorted([r for r in raw["s9"] if r["N"] == N], key=lambda r: r["seed"])
        gc = sorted([r for r in raw["ctrl"] if r["N"] == N], key=lambda r: r["seed"])
        if [r["seed"] for r in g] != list(range(F5_SEEDS)) or [r["seed"] for r in gc] != list(range(F5_CTRL_SEEDS)):
            raise DataError(f"S9 at N = {N}: seeds {[r['seed'] for r in g]}, controls {[r['seed'] for r in gc]}")
        st = stored[str(N)]
        for rows, lst, c_arr in ((g, "S9", cls), (gc, "C2_S9", ccls)):
            for s, r in enumerate(rows):
                if r.get("missing") or str(r["class"]) != tsv_all[(lst, r["name"])]["class"] or int(tsv_all[(lst, r["name"])]["N"]) != N:
                    raise DataError(f"recomputed class {r.get('class')} of {r['name']} differs from the stored class {tsv_all[(lst, r['name'])]['class']} (stop rule)")
                c_arr[k, s] = str(r["class"])
        if dict(sorted(Counter_(c for c in cls[k]).items())) != dict(sorted(st["classes"].items())):
            raise DataError(f"S9 at N = {N}: recomputed class counts differ from the stored {st['classes']} (stop rule)")
        if dict(sorted(Counter_(c for c in ccls[k]).items())) != dict(sorted(st["controls"]["classes"].items())):
            raise DataError(f"S9_ctrl at N = {N}: recomputed class counts differ from the stored {st['controls']['classes']} (stop rule)")
        for mi, m in enumerate(names):
            xs = [E.metric_of(r, m, ch) for r in g]
            got, want = _f5_med(E, xs), st["metrics"][m]
            for key in ("n", "n_undefined", "median", "min", "max"):
                a, b = got[key], want[key]
                if not (a == b or (isinstance(a, float) and np.isnan(a) and (b is None or np.isnan(float(b))))):
                    raise DataError(f"S9 at N = {N}, {m}: recomputed {key} {a!r} differs from the stored {b!r} (stop rule)")
            val[m][k] = xs
            d["metric_undefined"][k, mi] = int(got["n_undefined"])
        for m in F5_CONTROL_METRICS:
            cval[m][k] = [E.metric_of(r, m, ch) for r in gc]
    d["n_values"] = np.array(F5_N, dtype=np.int64)
    d["s9_class"], d["ctrl_class"] = cls, ccls
    for m in names:
        d[f"s9_{m}"] = val[m]
        d[f"stored_{m}"] = np.array([[st_["metrics"][m][q] for q in ("min", "median", "max")] for st_ in (stored[str(N)] for N in F5_N)], dtype=float)
    for m in F5_CONTROL_METRICS:
        d[f"ctrl_{m}"] = cval[m]
    d["s9_stored_counts"] = [dict(sorted(stored[str(N)]["classes"].items())) for N in F5_N]
    d["ctrl_stored_counts"] = [dict(sorted(stored[str(N)]["controls"]["classes"].items())) for N in F5_N]
    ref = ev["N_sweep"]["ref"]
    d["ref_class"], d["ref_onset_s"], d["ref_f_pk_hz"], d["ref_name"] = ref["class"], float(ref["onset_s"]), float(ref["f_pk_hz"]), ref["name"]
    d["n_rule"] = ev["N_sweep"]["no_worse"]
    # status rows and the FAIL-row strip from the stored A11 table
    by = {(r["rb_id"], r["check_id"]): r for r in raw["a11"]}
    d["status"] = []
    for key in F5_STATUS:
        if key not in by:
            raise DataError(f"A11 table: row {key} is missing")
        d["status"].append({"rb_id": key[0], "check_id": key[1], "status": by[key]["pass_or_fail"], "value": by[key]["value"], "threshold": by[key]["threshold"]})
    if d["status"][0]["status"] != "PASS":
        raise DataError("A11 table: RB4 parameter_perturbation is not PASS (DL-258 says PASS)")
    d["strip"] = []
    for key in F5_STRIP:
        if key not in by or by[key]["pass_or_fail"] != "FAIL":
            raise DataError(f"A11 table: {key} is not a FAIL row (strip rows are FAIL rows as logged)")
        x = by[key]
        d["strip"].append({"rb_id": x["rb_id"], "check_id": x["check_id"], "status": x["pass_or_fail"], "value": x["value"], "threshold": x["threshold"]})
    if "203 of 225" not in by[("RB2", "noisy_subgrid_agreement")]["threshold"] or "97 of 225" not in by[("RB2", "noisy_subgrid_agreement")]["value"]:
        raise DataError("A11 table: the RB2 noisy-subgrid row does not read 97 of 225 against 203 of 225")
    d["rb4_rows"] = int(sum(1 for r in raw["a11"] if r["rb_id"] == "RB4"))
    return d


def Counter_(it) -> dict:
    out: dict = {}
    for x in it:
        out[x] = out.get(x, 0) + 1
    return out


def f5_strip_lines(d: dict) -> list[str]:
    return [f"{r['rb_id']} {r['check_id']}: {r['status']} ({r['value'] or 'value blank in the table'}; threshold {r['threshold'] or 'blank'}) - shown, not dropped" for r in d["strip"]]


def f5_status_lines(d: dict) -> list[str]:
    s = d
    lines = ["Table 8.1 triggers: a surge class in < 3% of map-1 cells " + ("OCCURRED" if s["g5_triggered"] else "did NOT occur") + f" (D-tr {s['map1_n_surge']}, D-none {s['map1_n_none']} of {s['map1_n']}; "
             f"threshold {s['g5_threshold_cells']:.0f} cells; G5 CONTINUE, DL-237, DL-258). The network disagrees with the mean field in {s['cells_n_disagree']} of 4 cells (G4 triggered: {s['g4_triggered']}; DL-323, DL-325).",
             "Stored status rows that touch F5:"] + [f"    {r['rb_id']} {r['check_id']}: {r['status']} ({r['value'] or 'no value in the table'})" for r in s["status"]]
    lines += [strip_heading("F5")] + ["    " + t for t in f5_strip_lines(s)]
    return lines


def _f5_tick_text(vals, idx, fmt="{:.3g}"):
    return [fmt.format(float(vals[k])) for k in idx]


def _f5_map(ax, cls, x_vals, y_vals, *, title, xlabel, ylabel, mark_cells=True, tick_idx_x=None, tick_idx_y=None):
    """One regime map, cell by cell as stored: a mesh coloured by class and one class mark per cell (so the class never rests on colour alone)."""
    from matplotlib.colors import ListedColormap
    codes = np.vectorize({c: k for k, c in enumerate(F5_MAP_CLASSES)}.get)(cls).astype(float)
    cmap = ListedColormap([S.get(c).colour for c in F5_MAP_CLASSES])
    n_r, n_c = cls.shape
    mesh = ax.pcolormesh(np.arange(n_c + 1) - 0.5, np.arange(n_r + 1) - 0.5, codes, cmap=cmap, vmin=-0.5, vmax=len(F5_MAP_CLASSES) - 0.5, edgecolors=S.F5_COLOURS["cell_edge"],
                         linewidth=S.F5_SIZES["cell_edge_width"], zorder=1)
    if mark_cells:
        for c in F5_MAP_CLASSES:
            ii, jj = np.nonzero(cls == c)
            st = S.get(c)
            ax.plot(jj, ii, ls="none", marker=st.marker, ms=S.F5_SIZES["map_mark"], color=S.figure_colour("bar_edge"), mfc="none", mew=S.F5_SIZES["map_mark_width"], zorder=2)
    ax.set_xlim(-0.5, n_c - 0.5)
    ax.set_ylim(-0.5, n_r - 0.5)
    ax.set_aspect("auto")
    tx = tick_idx_x if tick_idx_x is not None else list(range(0, n_c, 5)) + ([n_c - 1] if (n_c - 1) % 5 else [])
    ty = tick_idx_y if tick_idx_y is not None else list(range(0, n_r, 5)) + ([n_r - 1] if (n_r - 1) % 5 else [])
    ax.set_xticks(tx, _f5_tick_text(x_vals, tx))
    ax.set_yticks(ty, _f5_tick_text(y_vals, ty))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc=S.TITLE_LOC)
    return mesh


def _f5_x(k: int, s: int, control: bool) -> float:
    return k * F5_SLOT + (F5_CTRL_X0 + s if control else s)


def _draw_F5(d: dict, draft: bool):
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import patheffects
    from matplotlib.colors import ListedColormap
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    fig = plt.figure(figsize=(7.4, 13.4), constrained_layout=True)
    gs = fig.add_gridspec(6, 6, height_ratios=[0.85, 3.5, 3.0, 1.9, 2.4, 2.1])
    edge, fail, dark = S.figure_colour("bar_edge"), S.figure_colour("fail_text"), S.figure_colour("text_dark")
    C = S.F5_COLOURS

    # key row
    kx = fig.add_subplot(gs[0, :])
    kx.axis("off")
    hs = [Line2D([], [], ls="none", marker=S.get(c).marker, ms=S.F5_SIZES["key_mark"], color=S.get(c).colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], label=f"{c} (map cell; mean-field class)") for c in F5_MAP_CLASSES]
    hs += [Line2D([], [], ls="none", marker=S.get(k).marker, ms=S.F5_SIZES["key_mark"] + 1, color=S.get(k).colour, mew=S.F5_SIZES["net_width"], label=lab)
           for k, lab in (("network_agree", f"network cell, agrees with the mean field ({d['cells_n_agree']} of 4)"), ("network_disagree", f"network cell, disagrees ({d['cells_n_disagree']} of 4)"))]
    hs += [Line2D([], [], ls="none", marker=S.F5_STATE_MARKS[k], ms=S.F5_SIZES["key_mark"], color=C[k], mew=S.F5_SIZES["key_state_width"], label=lab) for k, lab in
           (("agree", "subgrid cell agrees"), ("disagree", "subgrid cell disagrees (not a tie)"), ("tie", "subgrid cell is a tie (a disagreement by the D24 rule)"))]
    kx.legend(handles=hs, loc="center", ncol=2, fontsize=S.TEXT_SIZES["legend"], frameon=False, handlelength=2.0, columnspacing=1.6, labelspacing=0.6)

    # (a) map 1 with the network symbols
    ax = fig.add_subplot(gs[1, 0:3])
    _f5_map(ax, d["map1_class"], d["map1_tau_d_ms"], d["map1_Delta"], title=f"(a) map 1, mode D, T_ramp 120 s: D-tr {d['map1_n_surge']}, D-none {d['map1_n_none']} of {d['map1_n']}",
            xlabel="tau_d (ms), cell index j", ylabel="Delta, cell index i")
    for agree in (True, False):
        m = d["cell_agree"] == agree
        if m.any():
            st = S.get("network_agree" if agree else "network_disagree")
            # 13o (DL-494 R9): the white halo carries a dark outline, so the agree glyph stays visible on the blue D-tr tiles
            ax.plot(d["cell_j"][m], d["cell_i"][m], ls="none", marker=st.marker, ms=S.F5_SIZES["net_symbol"], color=C["net_halo"], mew=S.F5_SIZES["net_halo_width"], zorder=4,
                    path_effects=[patheffects.Stroke(linewidth=S.F5_SIZES["net_halo_width"] + 2 * S.F5_SIZES["net_outline_width"], foreground=C["net_outline"]), patheffects.Normal()])
            ax.plot(d["cell_j"][m], d["cell_i"][m], ls="none", marker=st.marker, ms=S.F5_SIZES["net_symbol"], color=st.colour, mew=S.F5_SIZES["net_width"], zorder=5)

    # (b) the 4 network cells: map class at 120 s, mean-field companion at 30 s, network seeds at 30 s
    ax = fig.add_subplot(gs[1, 3:6])
    cols = ("map 1\n(120 s)", "mean-field\ncompanion\n(30 s)", "network\nseed 0", "network\nseed 1", "network\nseed 2")
    for r in range(4):
        pts = [d["cell_map_class"][r], d["cell_mf30_class"][r], *d["cell_net_class"][r]]
        for c_, cls in enumerate(pts):
            st = S.get(cls)
            ax.plot([c_], [r], ls="none", marker=st.marker, ms=S.F5_SIZES["table_mark"], color=st.colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], zorder=3)
        ag = S.get("network_agree" if d["cell_agree"][r] else "network_disagree")
        ax.plot([5.6], [r], ls="none", marker=ag.marker, ms=S.F5_SIZES["net_symbol"], color=ag.colour, mew=S.F5_SIZES["net_width"], zorder=3)
        ax.text(6.1, r, "agrees" if d["cell_agree"][r] else "disagrees", va="center", ha="left", fontsize=S.TEXT_SIZES["small"])
    # 13o (DL-494 R9): the column labels sit below the panel, so the title of (b) is level with the title of (a)
    ax.set_xticks(list(range(5)) + [5.6], list(cols) + ["stored\nRB1"])
    ax.set_yticks(range(4), [f"cell {r + 1} (i {d['cell_i'][r]}, j {d['cell_j'][r]})\nDelta {d['cell_Delta'][r]:.4g}, tau_d {d['cell_tau_d_ms'][r]:.4g} ms" for r in range(4)])
    ax.set_xlim(-0.6, 7.4)
    ax.set_ylim(3.5, -0.6)
    ax.set_title("(b) the 4 network cells (N = 1e4): classes as stored", loc=S.TITLE_LOC, color=fail)
    ax.set_xlabel("The network was run at T_ramp 30 s; the map is at T_ramp 120 s.\nBoth are drawn; no equivalence is claimed.")

    # (c), (d) subgrid agreement: D24 (frozen, FAILED) and P-1 (post hoc), same size and frame, cells at their map-1 indices
    for pos, key, ttl, bad, post in ((gs[2, 0:2], "d24", f"(c) D24, frozen rule: FAILED, {d['d24_n_agree']} of {d['sub_n']} agree ({100.0 * d['d24_n_agree'] / d['sub_n']:.1f}%; {d['d24_needed']} needed)", True, False),
                                     (gs[2, 2:4], "p1", f"(d) P-1, post-hoc, feeds no gate: {d['p1_n_agree']} of {d['sub_n']} agree ({100.0 * d['p1_n_agree'] / d['sub_n']:.1f}%)", False, True)):
        ax = fig.add_subplot(pos)
        st_ = d[f"{key}_state"]
        z = np.full((30, 30), np.nan)
        z[d["sub_i"], d["sub_j"]] = st_
        cm = ListedColormap([C["agree"], C["disagree"], C["tie"]])
        ax.pcolormesh(np.arange(31) - 0.5, np.arange(31) - 0.5, np.ma.masked_invalid(z), cmap=cm, vmin=-0.5, vmax=2.5, edgecolors=C["cell_edge"], linewidth=S.F5_SIZES["cell_edge_width"], zorder=1)
        for s_, nm in enumerate(("agree", "disagree", "tie")):
            m = st_ == s_
            if m.any():
                ax.plot(d["sub_j"][m], d["sub_i"][m], ls="none", marker=S.F5_STATE_MARKS[nm], ms=S.F5_SIZES["state_mark"], color=S.HALO_COLOUR, mew=S.F5_SIZES["state_mark_width"], zorder=2)
        ax.set_xlim(-0.5, 29.5)
        ax.set_ylim(-0.5, 29.5)
        ax.set_xticks([0, 10, 20, 29], _f5_tick_text(d["map1_tau_d_ms"], [0, 10, 20, 29]))
        ax.set_yticks([0, 10, 20, 29], _f5_tick_text(d["map1_Delta"], [0, 10, 20, 29]))
        ax.set_xlabel("tau_d (ms)")
        ax.set_ylabel("Delta")
        ax.set_title(textwrap.fill(ttl, 52) + f"\nagree {d[f'{key}_n_agree']}, disagree {d[f'{key}_n_disagree']}, tie {d[f'{key}_n_tie']}", loc=S.TITLE_LOC, color=fail if bad else dark)
        if post:
            for sp in ax.spines.values():
                sp.set_edgecolor(C["frame_posthoc"])
                sp.set_linestyle("--")
                sp.set_linewidth(1.4)

    # (e) map 2
    ax = fig.add_subplot(gs[2, 4:6])
    _f5_map(ax, d["map2_class"], d["map2_T_ramp_s"], d["map2_J0"], title=f"(e) map 2, mode D:\nD-tr {d['map2_n_surge']}, D-none {d['map2_n_none']} of {d['map2_n']}", xlabel="T_ramp (s)",
            ylabel="J0", tick_idx_x=[0, 3, 6, 9, 12], tick_idx_y=[0, 6, 12, 18, 24])

    # (f) class per seed against N (ramp seeds filled, no-ramp control seeds open)
    ax = fig.add_subplot(gs[3, :])
    ycls = {c: k for k, c in enumerate(F5_NET_CLASSES)}
    for k in range(4):
        for s in range(F5_SEEDS):
            st = S.get(str(d["s9_class"][k, s]))
            ax.plot([_f5_x(k, s, False)], [ycls[str(d["s9_class"][k, s])]], ls="none", marker=st.marker, ms=S.F5_SIZES["seed_mark"], color=st.colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], zorder=3)
        for s in range(F5_CTRL_SEEDS):
            st = S.get(str(d["ctrl_class"][k, s]))
            ax.plot([_f5_x(k, s, True)], [ycls[str(d["ctrl_class"][k, s])]], ls="none", marker=st.marker, ms=S.F5_SIZES["seed_mark"], mfc="none", mec=st.colour, mew=S.F5_SIZES["control_mark_width"], zorder=3)
    _f5_n_axis(ax, d)
    ax.set_yticks(range(len(F5_NET_CLASSES)), list(F5_NET_CLASSES))
    ax.set_ylim(len(F5_NET_CLASSES) - 0.4, -0.6)
    ax.set_title("(f) network class of every seed against N (T_ramp 60 s): ramp seeds filled (10 per N), no-ramp control seeds open (3 per N);\nthe mean-field companion at T_ramp 60 s is D-tr", loc=S.TITLE_LOC)

    # (g) to (i) metrics against N: recomputed per-seed points, stored min to max and median
    for col, (m, lab) in enumerate(F5_METRICS):
        ax = fig.add_subplot(gs[4, 2 * col:2 * col + 2])
        lo_all = np.nanmin([np.nanmin(d[f"s9_{m}"]), d[f"stored_{m}"].min()] + ([np.nanmin(d[f"ctrl_{m}"])] if m in F5_CONTROL_METRICS else []))
        hi_all = np.nanmax([np.nanmax(d[f"s9_{m}"]), d[f"stored_{m}"].max()] + ([np.nanmax(d[f"ctrl_{m}"])] if m in F5_CONTROL_METRICS else []))
        log = m == "duration_ms" and lo_all > 0
        for k in range(4):
            x0 = k * F5_SLOT - 1.3
            ax.vlines([x0], d[f"stored_{m}"][k, 0], d[f"stored_{m}"][k, 2], colors=S.figure_colour("range_line"), lw=S.F5_SIZES["range_line"], zorder=2)
            ax.hlines([d[f"stored_{m}"][k, 1]], x0 - S.F5_SIZES["median_half_width"], x0 + S.F5_SIZES["median_half_width"], colors=S.figure_colour("range_line"), lw=S.F5_SIZES["median_line"], zorder=2)
            for s in range(F5_SEEDS):
                y = d[f"s9_{m}"][k, s]
                if np.isnan(y):
                    continue
                st = S.get(str(d["s9_class"][k, s]))
                ax.plot([_f5_x(k, s, False)], [y], ls="none", marker=st.marker, ms=S.F5_SIZES["seed_mark"], color=st.colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], zorder=3)
            if m in F5_CONTROL_METRICS:
                for s in range(F5_CTRL_SEEDS):
                    y = d[f"ctrl_{m}"][k, s]
                    if np.isnan(y):
                        continue
                    st = S.get(str(d["ctrl_class"][k, s]))
                    ax.plot([_f5_x(k, s, True)], [y], ls="none", marker=st.marker, ms=S.F5_SIZES["seed_mark"], mfc="none", mec=st.colour, mew=S.F5_SIZES["control_mark_width"], zorder=3)
        if m == "f_pk_hz":
            ax.axhline(d["ref_f_pk_hz"], color=S.get("mean_field").colour, ls=":", lw=S.F5_SIZES["ref_line"], zorder=1)
        if m == "onset_s":
            ax.axhline(d["ref_onset_s"], color=S.get("mean_field").colour, ls=":", lw=S.F5_SIZES["ref_line"], zorder=1)
        if log:
            ax.set_yscale("log")
            ax.set_ylim(lo_all / 1.6, hi_all * 4.0)
        else:
            span = hi_all - lo_all
            ax.set_ylim(lo_all - 0.06 * span, hi_all + 0.22 * span)
        _f5_n_axis(ax, d, small=True)
        ax.set_ylabel(lab)
        und = d["metric_undefined"][:, col]
        ttl = f"({'ghi'[col]}) {lab.split(' (')[0]} against N"
        ax.set_title(ttl, loc=S.TITLE_LOC)
        ax.text(0.01, 0.99, "undefined seeds: " + ", ".join(f"{int(u)}" for u in und) if und.any() else "", transform=ax.transAxes, ha="left", va="top", fontsize=S.TEXT_SIZES["small"])

    # status block
    axs = fig.add_subplot(gs[5, :])
    axs.axis("off")
    lines = f5_status_lines(d)
    lines += ["Panels (a) to (e) are rows of the stored A9 tables, (b) and (f) the stored MS10 evaluation and record classes; the per-seed points of (g) to (i) are RECOMPUTED from stored series with the "
              "frozen classifier (the MS10 evaluation call) and equal the stored classes, counts, minimum, median and maximum. Grey bar: stored minimum to maximum of the 10 ramp seeds, "
              "wide tick: stored median; dotted line: mean-field companion at T_ramp 60 s (" + f"{d['ref_class']}, f_pk {d['ref_f_pk_hz']:g} Hz, onset {d['ref_onset_s']:g} s" + "). Controls: no duration was evaluated."]
    lines = [ln for t_ in lines for ln in textwrap.wrap(t_, width=150, subsequent_indent="        ")]
    axs.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=S.TEXT_SIZES["status"], linespacing=1.25)
    return _style_text(fig, F5_FOOTER if draft else "")


def _f5_n_axis(ax, d: dict, small: bool = False):
    ax.set_xticks([k * F5_SLOT + 5.5 for k in range(4)], [(f"{int(n):,}".replace(",", " ") if not small else f"{n:.0e}".replace("e+0", "e")) for n in d["n_values"]] if small
                  else [f"N = {int(n):,}".replace(",", " ") for n in d["n_values"]])
    for k in range(1, 4):
        ax.axvline(k * F5_SLOT - 3.0, color=S.F5_COLOURS["frame_posthoc"], lw=0.4, ls=":", zorder=0)
    ax.set_xlim(-2.6, 4 * F5_SLOT - 2.0)


def f5_caption_notes(d: dict) -> tuple:
    """Sentences about what is and is not drawn (13m). Values come from the prepared data; only the wording is typed here."""
    return (
        "Panels (a) and (e) draw the stored class of every cell of the two mean-field regime maps, cell by cell as stored (map 1: 30 x 30 cells in (Delta, tau_d), T_ramp 120 s, "
        f"{d['map1_n_surge']} D-tr and {d['map1_n_none']} D-none; map 2: 25 x 13 cells in (J0, T_ramp), Delta 0.3, tau_d 5 ms, {d['map2_n_surge']} D-tr and {d['map2_n_none']} D-none); the axes are "
        "cell indices with the stored parameter values as tick labels, nothing is interpolated, smoothed or offset, and every non-surge cell is drawn at the same weight as a surge cell. "
        "The map statements are for mode D (noise-free mean field); there is no claim that the regime map is robust to noise (MS9(e)-2, DL-242, DL-250), and D8 is undefined in mode N and "
        "filters nothing (DL-230), so every D8-dependent class is provisional (DL-163, DL-208). The four network symbols in (a) are the stored RB1 cell comparison: the network at N = 1e4 "
        f"agrees with the mean field at {d['cells_n_agree']} of 4 cells and disagrees at {d['cells_n_disagree']} (DL-320, DL-325, G4-C1); each symbol sits on the map-1 cell with the same "
        "(Delta, tau_d), matched to 1e-9. The network cells were run at T_ramp 30 s and the map is at T_ramp 120 s: panel (b) shows the map class (120 s), the stored mean-field companion "
        "class at 30 s (its own run, DL-319) and the three network classes side by side, and the caption makes no claim that the two durations are equivalent.",
        "Panels (c) and (d) draw the 225-cell noisy subgrid (every cell is the mode-N majority of 10 seeds at sigma 0.0624, checked and not confirmed, G4-C4) at the map-1 indices: (c) the "
        f"frozen D24 rule, which FAILED ({d['d24_n_agree']} of {d['sub_n']} cells agree = {100.0 * d['d24_n_agree'] / d['sub_n']:.1f}%, {d['d24_needed']} needed; {d['d24_n_tie']} ties are disagreements by the rule; "
        f"{d['d24_n_agree_categories']} of {d['sub_n']} agree on the three Table 2.1 categories, our reading, UNVERIFIED; DL-242) and (d) the post-hoc view P-1 ({d['p1_n_agree']} of {d['sub_n']} = "
        f"{100.0 * d['p1_n_agree'] / d['sub_n']:.1f}%, {d['p1_n_tie']} ties), which is post-hoc and feeds no gate (DL-255); it is drawn in its own dashed frame beside D24, at the same size.",
        "Panels (f) to (i) draw the 40 S9 network records (N = 1e3, 3e3, 1e4, 3e4; 10 seeds each; T_ramp 60 s) and the 12 no-ramp control records (S9_ctrl, 3 seeds each). The class of every "
        "seed is the stored class (the stored record-class table of the MS10 evaluation). The per-seed f_pk, onset and duration are recomputed from stored series with the frozen classifier, using the same call as the "
        "MS10 evaluation and no new setting, and are labelled so; the recomputed classes equal the stored classes, and the recomputed counts, minimum, median and maximum equal the stored "
        "values of the stored MS10 evaluation (a test; a difference stops the build). This is a logged exception to the rule that figures read tables first (UNVERIFIED, DL-490). A seed's x position is "
        "its slot in the N group (ramp seeds 0 to 9, then the control seeds 0 to 2), a layout that carries no value. The grey bar is the stored minimum to maximum of the ramp seeds and the "
        "wide tick the stored median; the dotted line is the mean-field companion at T_ramp 60 s. Seeds whose metric is undefined are not drawn and are counted in the panel; the controls "
        "were evaluated without the duration, so panel (i) has no control points. Network classes cannot separate ramp-driven from non-ramp records (G4-C3): the no-ramp controls reach surge "
        "classes (DL-325), and no claim of f_pk or class agreement between network and mean field is made (MS11-C2). The surge result is stated for the mean field only (G4-C2). "
        "RB1 FAILED, RB2 FAILED and D24 FAILED (strip above); RB4 passed. A9 failure labels are not drawn here (F6).",
    )


def make_F5(res=None, out_dir=None, *, tag_build: bool = False, take_home=F5_TAKE_HOME, claim_limit_ids=F5_CLAIM_LIMITS,
            script="scripts/fig_F5.py", root=None) -> dict:
    """Build F5 from results/. Returns {'prov', 'paths', 'timing_s', 'drawn_sha256', 'caption'}. tag_build=True needs a clean tree (figprov)."""
    F.require_buildable("F5")
    root = Path(root) if root is not None else repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "F5"
    t = {"start": time.perf_counter()}
    raw = load_F5(res)
    t["load"] = time.perf_counter()
    d = prepare_F5(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    s9_ref = next(r for r in raw["s9"] if r["N"] == 10000 and r["seed"] == 0)
    ctrl_ref = next(r for r in raw["ctrl"] if r["N"] == 10000 and r["seed"] == 0)
    recs = {"s8_cell1_seed0": raw["cell_recs"][raw["names"]["cells"][0]],
            "s9_N1e4_seed0": json.loads((res / F5_S9_DIR / f"{s9_ref['name']}.json").read_text(encoding="utf-8")),
            "s9_ctrl_N1e4_seed0": json.loads((res / F5_CTRL_DIR / f"{ctrl_ref['name']}.json").read_text(encoding="utf-8"))}
    for key, rec in recs.items():
        for r in make_param_table(rec["config"]):
            rows.append({**r, "panel": key, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    cap = CAP.build_caption("F5", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=[r for r in rows if r["key"] in F5_CAPTION_KEYS],
                            spectrogram=None, symbol_keys=(), notes=f5_caption_notes(d), not_applicable=F5_NOT_APPLICABLE)
    import matplotlib.pyplot as plt
    fig = _draw_F5(d, draft=not tag_build)
    out.mkdir(parents=True, exist_ok=True)
    pdf, png = out / "F5.pdf", out / "F5.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=S.PNG_DPI)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    cap_path, dig_path = out / "F5_caption.txt", out / "F5_drawn_data_sha256.txt"
    from .. import provenance as P
    drawn = drawn_data_sha256(d)
    P.atomic_write_text(cap_path, cap.text + "\n")
    P.atomic_write_text(dig_path, drawn + "\n")
    warnings = []
    for k, rec in recs.items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true")
    prov = F.write_figure_provenance(
        "F5", script=script, inputs=[res / p for p in F5_INPUTS] + raw["record_files"], outputs=[pdf, png, cap_path, dig_path], params_rows=rows,
        modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py", "src/mprsurge/plotting/nordlie.py",
                 "src/mprsurge/plotting/figprov.py", "src/mprsurge/analysis/ms10_eval.py", "src/mprsurge/analysis/ms9_classify.py", "src/mprsurge/analysis/surge_metrics.py"],
        configs=["configs/base.yaml", "configs/ms10/ms10_net.yaml", "configs/ms10/ms10_eval.yaml", "configs/robustness_criteria.yaml"], claim_limits=cap.claim_limits,
        input_tables=[{"path": res / F5_INPUTS[0], "rows": int(len(raw["a9"]))}, {"path": res / F5_INPUTS[1], "rows": int(len(raw["sub"]))},
                      {"path": res / F5_INPUTS[3], "rows": len(raw["tsv"])}, {"path": res / F5_INPUTS[4], "rows": len(raw["a11"])}],
        spectrogram=None, tag_build=tag_build, out_dir=out, root=root, warnings=warnings, wall_time_s=time.perf_counter() - t["start"])
    nordlie_path = out / "F5_nordlie.md"
    N.write_nordlie(out / "F5_params.csv", out / "F5_provenance.json", nordlie_path, root=root)
    t["end"] = time.perf_counter()
    timing = {"load_s": t["load"] - t["start"], "prepare_s": t["prepare"] - t["load"], "draw_s": t["draw"] - t["prepare"],
              "provenance_and_nordlie_s": t["end"] - t["draw"], "total_s": t["end"] - t["start"]}
    return {"prov": prov, "paths": [pdf, png, cap_path, dig_path, out / "F5_params.csv", out / "F5_provenance.json", nordlie_path],
            "timing_s": timing, "drawn_sha256": drawn, "caption": cap.text}


def make_FS6(*args, **kwargs):
    """FS6 is not produced (S14 and S15 were not run, MS12-C1, DL-421): raises figprov.FigureRefused."""
    F.require_buildable("FS6")
