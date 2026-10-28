"""Figure builders (MS13 13d; plan section 10.1: plotting/figures.py, make_F1 ... make_FS6). Only make_F3, make_F2 and the make_FS6 refusal exist so far.

A figure builder reads stored results under results/ (never simulates, never writes under results/), draws, and writes the figure, <ID>_provenance.json
and <ID>_params.csv into figures/<ID>/ through figprov. The step order is fixed: load_<ID> (files -> arrays), prepare_<ID> (pure: arrays -> the drawn
data), draw (matplotlib), then caption, provenance and the Nordlie table. The drawn data of prepare_<ID> is what test row 9 hashes.

Layout is a design choice, UNVERIFIED (docs/ms13_conventions.md). The scalar colour map and the contour marks are style.py keys (13e, DL-448). The take-home
message and the claim-limit list below were accepted by the reviewer in the 13e prompt (DL-453).
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from pathlib import Path

import numpy as np

from ..config import repo_root
from ..params import make_param_table
from . import captions as CAP
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
# figure, read from the stored A11 table. G6-D1: not listed, the arrows carry no predicted entry (DL-455).
F3_CLAIM_LIMITS = ("MS11-C7", "MS12-C1", "MS11-C3")
# keys of the A4 and A6 run records that define the plotted slices and the regime; the full list stays in F3_params.csv and the Nordlie table
CAPTION_KEYS = ("model.type", "model.ref_point", "model.tau_ms", "model.J")

_SLICE = re.compile(r"^eta_tau_D([0-9.]+)_td([0-9.]+)$")
FOOTER = "DRAFT v3: untagged build. Layout, colour map and contour marks are UNVERIFIED design choices (style.py)."


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
                          arrowprops=dict(arrowstyle="-|>", color=st.colour, lw=1.6, ls=st.linestyle, shrinkA=0, shrinkB=0, mutation_scale=8))
        ann.set_gid(f"arrow:strip:{k}:{leg}")
        (mk,) = ax.plot([x0], [i], ls="none", marker=st.marker, ms=5, color=st.colour, mec=S.HALO_COLOUR, mew=0.4, zorder=6, clip_on=False)
        mk.set_gid(f"start:strip:{k}:{leg}")
        labels.append((names[k] if leg == 0 else "P5 return") + f" ({d[f'{k}_T_ramp_s']:g} s)")
    ax.set_ylim(len(STRIP_ROWS) - 0.5, -0.5)
    ax.set_yticks(range(len(STRIP_ROWS)), labels, fontsize=S.FONT_SIZE_PT - 2)
    ax.tick_params(axis="x", labelbottom=False, length=2)
    ax.tick_params(axis="y", length=2)
    ax.set_title("path strip: one row per arrow, rows are labels", fontsize=S.FONT_SIZE_PT - 1, loc="left")


def _draw_F3(d: dict, draft: bool, strip_lines: list[str]):
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import patheffects
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    mf, hp = S.get("mean_field"), S.diagram_mark("hopf_point")
    m25 = S.contour_mark("25hz")
    fig = plt.figure(figsize=(7.4, 8.9), constrained_layout=True)
    gs = fig.add_gridspec(4, 4, width_ratios=[1, 1, 1, 0.05], height_ratios=[1.45, 1.05, 1.55, 0.5])
    vmin, vmax = d["f_min_hz"], d["f_max_hz"]
    sc = None
    a4_D = f"{d['a4_curve_Delta']:g}"
    hopf_halo = [patheffects.withStroke(linewidth=3.2, foreground=S.HALO_COLOUR)]

    def hopf_mark(ax, y):
        (h,) = ax.plot([d["headline_hopf_eta"]], [y], ls="none", marker=hp.marker, ms=hp.size - 2, mew=hp.width + 0.4, color=hp.colour, mec=hp.colour,
                       zorder=HOPF_Z, path_effects=hopf_halo)
        h.set_gid("a6_hopf_point")

    for j, D in enumerate(DELTAS):
        ax = fig.add_subplot(gs[0, j])
        sc = ax.scatter(d[f"D{D}_po_eta"], d[f"D{D}_po_tau_d_ms"], c=d[f"D{D}_po_f_hz"], s=5, marker="s", linewidths=0, cmap=S.FREQUENCY_CMAP,
                        vmin=vmin, vmax=vmax, rasterized=True)
        ax.plot(d[f"D{D}_hopf_eta"], d[f"D{D}_tau_d_ms"], ls="none", marker=mf.marker, ms=5, color=mf.colour)
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
        ax.set_title(rf"({'abc'[j]}) $\Delta$ = {D}" + "\n" + note_100hz(d, D).replace(", maximum", ",\nmaximum"), fontsize=S.FONT_SIZE_PT - 1)
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
    axd.set_title(r"(d) ($\bar\eta$, $\Delta$): Hopf curve and paths", fontsize=S.FONT_SIZE_PT)
    axs = fig.add_subplot(gs[1, 0:2], sharex=axd)
    _draw_strip(axs, d)
    axt = fig.add_subplot(gs[1:3, 2:4])
    axt.axis("off")

    def wrap(s):
        return "\n".join(textwrap.wrap(s, 44))

    handles = [Line2D([], [], ls="none", marker=mf.marker, ms=5, color=mf.colour, label="Hopf point of an A6 slice"),
               Line2D([], [], ls="none", marker=m25.marker, ms=m25.size - 2, mew=m25.width, color=m25.colour, mec=S.HALO_COLOUR, label="25 Hz crossing of an A6 slice"),
               Line2D([], [], ls=mf.linestyle, color=mf.colour, lw=1.0,
                      label=wrap(f"Hopf curve (A4 record: Delta {d['a4_curve_Delta']:g}, J {d['a4_curve_J']:g}, tau_d {d['a4_curve_tau_d_ms']:g} ms)")),
               Line2D([], [], ls="none", marker=hp.marker, ms=hp.size, mew=hp.width, color=hp.colour,
                      label=wrap(f"A6 Hopf point, Delta {d['headline_Delta']:g}, tau_d {d['headline_tau_d_ms']:g} ms (not the A4 curve)"))]
    names = {"P1": "eta ramp", "P2": "hypoxia, eta part", "P3": f"drive, eta part, I_amp {d['P3_I_amp']:g}", "P4a": "Delta up", "P4b": "Delta down",
             "P5": "eta up, then return"}
    for k in PATH_ORDER:
        st = S.get(k)
        handles.append(Line2D([], [], ls=st.linestyle, marker=st.marker, ms=4, lw=2, color=st.colour, label=wrap(f"{k} {names[k]} (T_ramp {d[f'{k}_T_ramp_s']:g} s)")))
    leg = axt.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=6, ncol=1, frameon=False, borderaxespad=0, labelspacing=0.55)
    leg.set_in_layout(False)
    axb = fig.add_subplot(gs[3, :])
    axb.axis("off")
    t1 = axb.text(0.0, 1.0, "FAIL rows of the stored A11 table that touch F3 (not recomputed):", va="top", fontsize=S.FONT_SIZE_PT - 1, weight="bold")
    t2 = axb.text(0.0, 0.8, "\n".join(strip_lines) if strip_lines else "none", va="top", fontsize=6.2)
    t3 = axb.text(0.0, 0.42, "Not drawn: (eta, Delta) frequency shading (A6 has no Delta slices), the J plane, the J ramp of P2 and P3, the sigmoid and "
                  "start-distance variants.", va="top", fontsize=6)
    t4 = axb.text(0.0, 0.0, FOOTER if draft else "", fontsize=5.5, color="#7f0000", ha="left", va="bottom")
    for t in (t1, t2, t3, t4):
        t.set_in_layout(False)
    return fig


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
        "Only the parameters that define the plotted slices and the regime are listed; the full list is in the Nordlie table F3_nordlie.md and in F3_params.csv.",
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
F2_FOOTER = "DRAFT v2: untagged build. Layout, marks and colours are UNVERIFIED design choices (style.py). G4-C2 and the RB1 FAIL-row list are UNVERIFIED readings."


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
        ax.plot(d[f"{key}_param"][m], d[ycol][m], ls="none", marker=st.marker, ms=st.size, mew=st.width, mfc=st.colour if st.filled else "none",
                mec=st.colour, color=st.colour, zorder=5 if kind == "net" else 4, clip_on=False,
                label=(f"{label}, {direction} sweep" if label else None))


def _draw_F2(d: dict, draft: bool, strip_lines: list[str]):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    cyc, fs, fu, hp = S.diagram_mark("a5_cycle"), S.diagram_mark("a5_fixed_stable"), S.diagram_mark("a5_fixed_unstable"), S.diagram_mark("hopf_point")
    fig = plt.figure(figsize=(7.4, 8.6), constrained_layout=True)
    gs = fig.add_gridspec(5, 1, height_ratios=[1.7, 1.15, 0.95, 1.05, 0.07])
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
    ax.set_title(r"(a) $\bar\eta$ diagram at ref_devalle: fixed point and cycle maximum and minimum of v", fontsize=S.FONT_SIZE_PT)
    # (b) amplitude
    ax2 = fig.add_subplot(gs[1], sharex=ax)
    for name in ("up", "down"):
        ax2.plot(d[f"a5_{name}_param"], d[f"a5_{name}_amp"], color=cyc.colour, lw=cyc.width, zorder=3)
    _vline_hopf(ax2, d)
    _s4_points(ax2, d, "mf", "mf_v_ptp", "mf")
    _s4_points(ax2, d, "net", "net_v_ptp", "net")
    ax2.set_ylabel("v amplitude (max - min)")
    ax2.set_title("(b) amplitude: A5 cycles, S4 mean field and S4 network, stored values", fontsize=S.FONT_SIZE_PT)
    # (c) stored relative difference, network against mean field
    ax3 = fig.add_subplot(gs[2], sharex=ax)
    above = d["net_above_mask"] == 1.0
    ax3.axhline(0.0, color="#7a7a7a", lw=0.6, zorder=1)
    _vline_hopf(ax3, d)
    _s4_points(ax3, d, "net", "cmp_rel_v_ptp", "net", mask=above)
    ax3.set_xlim(*xlim)
    v = d["cmp_rel_v_ptp"][above]
    lo, hi = min(float(v.min()), 0.0), max(float(v.max()), 0.0)
    ax3.set_ylim(lo - 0.12 * (hi - lo), hi + 0.12 * (hi - lo))
    ax3.set_ylabel("(network - MF) / MF")
    ax3.set_xlabel(r"$\bar\eta$")
    ax3.set_title(r"(c) stored relative difference of the v amplitude, drawn above $\bar\eta_H$ + 0.1 only", fontsize=S.FONT_SIZE_PT)
    ax3.text(0.99, 0.97, "not drawn at and below eta_H: the mean-field amplitude there is ~0 or still\nrelaxing, so the stored relative difference is not a measure (largest |stored value|\n"
             f"below eta_H - 0.1: {d['cmp_rel_v_below_max_abs']:.2g}). Network below eta_H: no rest, v amplitude\n"
             f"{d['net_floor_v_ptp_min']:.2f} to {d['net_floor_v_ptp_max']:.2f} (panel b).", transform=ax3.transAxes, fontsize=5.8, va="top", ha="right")
    # legend and strip
    axl = fig.add_subplot(gs[3])
    axl.axis("off")
    h, l = ax.get_legend_handles_labels()
    axl.legend(h, l, loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=6, ncol=2, frameon=False, borderaxespad=0)
    axl.text(0.0, 0.40, "FAIL rows of the stored A11 table that touch F2 through the network symbols (not recomputed; UNVERIFIED reading):",
             va="top", fontsize=S.FONT_SIZE_PT - 1, weight="bold")
    axl.text(0.0, 0.33, "\n".join(strip_lines) if strip_lines else "none", va="top", fontsize=6.2)
    axf = fig.add_subplot(gs[4])
    axf.axis("off")
    axf.text(0.0, 0.5, F2_FOOTER if draft else "", fontsize=5.5, color="#7f0000", ha="left", va="center")
    return fig


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


def make_FS6(*args, **kwargs):
    """FS6 is not produced (S14 and S15 were not run, MS12-C1, DL-421): raises figprov.FigureRefused."""
    F.require_buildable("FS6")
