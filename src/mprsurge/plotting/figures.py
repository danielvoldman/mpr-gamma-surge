"""Figure builders (MS13 13d; plan section 10.1: plotting/figures.py, make_F1 ... make_FS6). Only make_F3 and the make_FS6 refusal exist so far.

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
FOOTER = "DRAFT v2: untagged build. Layout, colour map and contour marks are UNVERIFIED design choices (style.py)."


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
OFFSET_PT = 5.0                          # vertical offset between arrows that share one stored position, in points (legibility only; stated in the caption)


def note_100hz(d: dict, D: str) -> str:
    """The 100 Hz statement of a panel, in words, from the stored arrays (counts and the largest cycle frequency of that slice set)."""
    n = int(d[f"D{D}_c100_count"].sum())
    if n == 0:
        return f"no 100 Hz contour in range, maximum {d[f'D{D}_f_max_hz']:.1f} Hz"
    return f"100 Hz contour: {n} crossings"


def _arrow(ax, trans, x0, x1, y0, y1, st, ms=4.0):
    """One path arrow with its marker at the start; the transform `trans` carries the legibility offset in points."""
    from matplotlib import patheffects
    halo = [patheffects.withStroke(linewidth=2.6, foreground=S.HALO_COLOUR)]
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), xycoords=trans, textcoords=trans, zorder=6,
                arrowprops=dict(arrowstyle="-|>", color=st.colour, lw=1.1, ls=st.linestyle, shrinkA=0, shrinkB=0, mutation_scale=7, path_effects=halo))
    ax.plot([x0], [y0], ls="none", marker=st.marker, ms=ms, color=st.colour, mec=st.colour, transform=trans, zorder=7, path_effects=halo, clip_on=False)


def _draw_paths(ax, d: dict, fig, *, plane: str, y0: float):
    """Horizontal arrows (P1, P2, P3, and P5 up and return) at y0, offset in points; in the Delta plane also the diagonal P4a and P4b arrows."""
    import matplotlib.transforms as mt
    slots = [k for k in PATH_ORDER if k not in ("P4a", "P4b")]
    first = (sum(int(d[f"{k}_legs"]) for k in slots) - 1) / 2.0
    i = 0
    for k in slots:
        st = S.get(k)
        for leg in range(int(d[f"{k}_legs"])):
            trans = mt.offset_copy(ax.transData, fig=fig, y=(first - i) * OFFSET_PT, units="points")
            a, b = d[f"{k}_eta_start"], d[f"{k}_eta_peak"]
            x0, x1 = (a, b) if leg == 0 else (b, a)
            _arrow(ax, trans, x0, x1, y0, y0, st)
            i += 1
    if plane == "Delta":
        for k in ("P4a", "P4b"):
            _arrow(ax, ax.transData, d[f"{k}_eta_start"], d[f"{k}_eta_peak"], d[f"{k}_Delta"], d[f"{k}_Delta_end_derived"], S.get(k))


def _draw_F3(d: dict, draft: bool, strip_lines: list[str]):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    mf, p2 = S.get("mean_field"), S.get("P2")
    m25 = S.contour_mark("25hz")
    fig = plt.figure(figsize=(7.4, 7.2), constrained_layout=True)
    gs = fig.add_gridspec(3, 3, height_ratios=[1.35, 1.0, 0.07])
    vmin, vmax = d["f_min_hz"], d["f_max_hz"]
    sc = None
    a4_D = f"{d['a4_curve_Delta']:g}"
    for j, D in enumerate(DELTAS):
        ax = fig.add_subplot(gs[0, j])
        sc = ax.scatter(d[f"D{D}_po_eta"], d[f"D{D}_po_tau_d_ms"], c=d[f"D{D}_po_f_hz"], s=5, marker="s", linewidths=0, cmap=S.FREQUENCY_CMAP,
                        vmin=vmin, vmax=vmax, rasterized=True)
        ax.plot(d[f"D{D}_hopf_eta"], d[f"D{D}_tau_d_ms"], ls="none", marker=mf.marker, ms=5, color=mf.colour)
        c = np.isfinite(d[f"D{D}_c25_eta"])
        ax.plot(d[f"D{D}_c25_eta"][c], d[f"D{D}_tau_d_ms"][c], ls="none", marker=m25.marker, ms=m25.size + 2, mew=m25.width + 0.6, color=S.HALO_COLOUR,
                mec=S.HALO_COLOUR, zorder=3)
        ax.plot(d[f"D{D}_c25_eta"][c], d[f"D{D}_tau_d_ms"][c], ls="none", marker=m25.marker, ms=m25.size, mew=m25.width, color=m25.colour,
                mec=m25.colour, zorder=4)
        if D == a4_D:
            ax.plot(d["a4_tau_d_eta_H"], d["a4_tau_d_ms"], ls=mf.linestyle, color=mf.colour, lw=1.0)
            ax.plot([d["headline_hopf_eta"]], [d["headline_tau_d_ms"]], ls="none", marker=p2.marker, ms=8, mfc="none", mec=p2.colour, mew=1.6, zorder=5)
            _draw_paths(ax, d, fig, plane="tau_d", y0=d["P1_tau_d_ms"])
        ax.set_yscale("log")
        ax.set_xlabel(r"$\bar\eta$")
        ax.set_ylabel(r"$\tau_d$ (ms)" if j == 0 else "")
        ax.set_title(rf"({'abc'[j]}) $\Delta$ = {D}" + "\n" + note_100hz(d, D).replace(", maximum", ",\nmaximum"), fontsize=S.FONT_SIZE_PT - 1)
        ax.set_xlim(0, 8)
    cb = fig.colorbar(sc, ax=fig.axes[:3], shrink=0.9, pad=0.01)
    cb.set_label("limit-cycle frequency (Hz)")
    axd = fig.add_subplot(gs[1, 0])
    axd.plot(d["a4_Delta_eta_H"], d["a4_Delta"], ls=mf.linestyle, color=mf.colour, lw=1.0)
    axd.plot([d["headline_hopf_eta"]], [d["headline_Delta"]], ls="none", marker=p2.marker, ms=8, mfc="none", mec=p2.colour, mew=1.6, zorder=5)
    _draw_paths(axd, d, fig, plane="Delta", y0=d["P1_Delta"])
    ends = [d[f"{k}_Delta_end_derived"] for k in ("P4a", "P4b")]
    axd.set_yscale("log")
    axd.set_xlim(0, 8)
    axd.set_ylim(min(d["a4_Delta"].min(), *ends) * 0.8, max(d["a4_Delta"].max(), *ends) * 1.25)
    axd.set_xlabel(r"$\bar\eta$")
    axd.set_ylabel(r"$\Delta$")
    axd.set_title(r"(d) ($\bar\eta$, $\Delta$): Hopf curve and paths", fontsize=S.FONT_SIZE_PT)
    axt = fig.add_subplot(gs[1, 1:])
    axt.axis("off")
    handles = [Line2D([], [], ls="none", marker=mf.marker, ms=5, color=mf.colour, label="Hopf point of an A6 slice"),
               Line2D([], [], ls="none", marker=m25.marker, ms=m25.size, mew=m25.width, color=m25.colour, label="25 Hz crossing of an A6 slice"),
               Line2D([], [], ls=mf.linestyle, color=mf.colour, lw=1.0,
                      label=f"Hopf curve (A4 record: Delta {d['a4_curve_Delta']:g}, J {d['a4_curve_J']:g}, tau_d {d['a4_curve_tau_d_ms']:g} ms)"),
               Line2D([], [], ls="none", marker=p2.marker, ms=8, mfc="none", mec=p2.colour, mew=1.6,
                      label=f"A6 Hopf point at Delta {d['headline_Delta']:g}, tau_d {d['headline_tau_d_ms']:g} ms (a separate marker, not the A4 curve)")]
    names = {"P1": "eta ramp", "P2": "hypoxia, eta part", "P3": f"drive, eta part, I_amp {d['P3_I_amp']:g}", "P4a": "Delta up", "P4b": "Delta down",
             "P5": "eta up, then return"}
    for k in PATH_ORDER:
        st = S.get(k)
        handles.append(Line2D([], [], ls=st.linestyle, marker=st.marker, ms=4, color=st.colour,
                              label=f"{k} {names[k]} (stored path, T_ramp {d[f'{k}_T_ramp_s']:g} s)"))
    axt.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=6, ncol=1, frameon=False, borderaxespad=0)
    axt.text(0.0, 0.27, "FAIL rows of the stored A11 table that touch F3 (not recomputed):", va="top", fontsize=S.FONT_SIZE_PT - 1, weight="bold")
    axt.text(0.0, 0.21, "\n".join(strip_lines) if strip_lines else "none", va="top", fontsize=6.2, wrap=True)
    axt.text(0.0, 0.0, "Not drawn: (eta, Delta) frequency shading (A6 has no Delta slices), the J plane, the J ramp of P2 and P3, "
             "the sigmoid and start-distance variants.", va="bottom", fontsize=6, wrap=True)
    axf = fig.add_subplot(gs[2, :])
    axf.axis("off")
    axf.text(0.0, 0.5, FOOTER if draft else "", fontsize=5.5, color="#7f0000", ha="left", va="center")
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
        out.append(f"{r['rb_id']} {r['check_id']}: {r['status']} ({val}; threshold {r['threshold']})" + (f"; {note}" if note else ""))
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
         "times stored Delta_factor). Arrows that share a stored position are offset vertically for legibility."),
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


def make_FS6(*args, **kwargs):
    """FS6 is not produced (S14 and S15 were not run, MS12-C1, DL-421): raises figprov.FigureRefused."""
    F.require_buildable("FS6")
