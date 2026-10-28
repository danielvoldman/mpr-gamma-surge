"""Figure builders (MS13 13d; plan section 10.1: plotting/figures.py, make_F1 ... make_FS6). Only make_F3 and the make_FS6 refusal exist so far.

A figure builder reads stored results under results/ (never simulates, never writes under results/), draws, and writes the figure, <ID>_provenance.json
and <ID>_params.csv into figures/<ID>/ through figprov. The step order is fixed: load_<ID> (files -> arrays), prepare_<ID> (pure: arrays -> the drawn
data), draw (matplotlib), then caption, provenance and the Nordlie table. The drawn data of prepare_<ID> is what test row 9 hashes.

Layout, scalar colour map and the F3-local marks are design choices, UNVERIFIED (docs/ms13_conventions.md). The take-home message and the claim-limit
list below are PROPOSED for the reviewer's ruling, not final (13d prompt).
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
)
F3_RECORDS = {"A4": "A4/A4_0000_4ece63ed731f.json", "A6": "A6/A6_0000_daa85487fd0a.json"}
# RB ids whose Table 7.2 "Where" column names F3 (plan.md line 852: RB9 -> "FS5; F3"). Reading of the table: UNVERIFIED.
FIGURE_RB = {"F3": ("RB9",)}
# DL-388 gives the RB9(b) numbers that the stored A11 table leaves blank (value column empty for that row).
STRIP_NOTE = {"b_spectral_vs_cycle_headline": "4.391 Hz against 0.5 Hz (DL-388)"}
DELTAS = ("0.05", "0.1", "0.3")             # the A6 eta-tau slices (DL-131)
LEVELS_HZ = (25.0, 100.0)                   # read back from a6_summary.json and checked

# PROPOSED for the reviewer's ruling; every statement is from a logged result (DL-131, DL-132) and is checked against the stored A6 arrays by
# prepare_F3 (counts and ranges) where the array holds it.
F3_PROPOSED_TAKE_HOME = (
    "PROPOSED, not ruled: on the A6 slices the 100 Hz contour does not occur for eta_bar 0 to 8 (largest cycle frequency 73.7 Hz), and the 25 Hz "
    "contour crosses the cycle branch only on some slices (Delta 0.05 from tau_d 3 ms, Delta 0.1 from 5 ms, Delta 0.3 only at 13, 22 and 36 ms; "
    "DL-131), with the cycle at ref_devalle at 32.0 to 39.7 Hz (DL-131, DL-132)."
)
# PROPOSED: MS11-C7 (every figure), MS12-C1 (F1 to F6), RB9(b) FAIL (names F3), all from docs/ms13_plan.md section 5. G6-D1 applies only if path
# arrows carry predicted entries; this draft has no path arrows, so it is not listed (decision for the reviewer when arrows are added).
F3_PROPOSED_CLAIM_LIMITS = ("MS11-C7", "MS12-C1", "RB9(b) FAIL")

_SLICE = re.compile(r"^eta_tau_D([0-9.]+)_td([0-9.]+)$")
FOOTER = "DRAFT: untagged build. Take-home message and claim-limit list are PROPOSED, not ruled. Scalar colour map and 25 Hz mark are F3-local (UNVERIFIED)."


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
        with open(res / F3_INPUTS[5], newline="", encoding="utf-8") as fh:
            a11 = list(csv.DictReader(fh))
    except (OSError, ValueError, KeyError) as exc:
        raise F.MissingInputError(f"an F3 input cannot be read: {exc}") from exc
    return {"a4": a4, "a6": a6, "summary": summary, "records": records, "a11": a11}


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
    d["headline_Delta"] = 0.3
    d["headline_tau_d_ms"] = 5.0
    d["headline_hopf_eta"] = float(d["D0.3_hopf_eta"][list(d["D0.3_tau_d_ms"]).index(5.0)])
    # agreement of the A4 tau_d curve with the A6 Hopf points at Delta 0.3 (log-tau interpolation); a number to look at, not a test
    d["a4_vs_a6_hopf_max_abs"] = float(np.max(np.abs(np.interp(np.log(d["D0.3_tau_d_ms"]), np.log(d["a4_tau_d_ms"]), d["a4_tau_d_eta_H"]) - d["D0.3_hopf_eta"])))
    d["c100_total_crossings"] = int(sum(d[f"D{D}_c100_count"].sum() for D in DELTAS))
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

def _draw_F3(d: dict, draft: bool, strip_lines: list[str]):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": S.FONT_FAMILY, "font.size": S.FONT_SIZE_PT, "pdf.fonttype": 42})
    mf, p2 = S.get("mean_field"), S.get("P2")
    fig = plt.figure(figsize=(7.4, 6.4), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.35, 1.0])
    vmin, vmax = d["f_min_hz"], d["f_max_hz"]
    sc = None
    for j, D in enumerate(DELTAS):
        ax = fig.add_subplot(gs[0, j])
        sc = ax.scatter(d[f"D{D}_po_eta"], d[f"D{D}_po_tau_d_ms"], c=d[f"D{D}_po_f_hz"], s=5, marker="s", linewidths=0, cmap="viridis",
                        vmin=vmin, vmax=vmax, rasterized=True)
        ax.plot(d[f"D{D}_hopf_eta"], d[f"D{D}_tau_d_ms"], ls="none", marker=mf.marker, ms=5, color=mf.colour, label="Hopf point of a slice (A6)")
        c = np.isfinite(d[f"D{D}_c25_eta"])
        ax.plot(d[f"D{D}_c25_eta"][c], d[f"D{D}_tau_d_ms"][c], ls="none", marker="_", ms=9, mew=1.6, color="white", mec="white", zorder=3)
        ax.plot(d[f"D{D}_c25_eta"][c], d[f"D{D}_tau_d_ms"][c], ls="none", marker="_", ms=7, mew=1.0, color="black", mec="black", zorder=4,
                label="25 Hz crossing of a slice")
        if D == "0.3":
            ax.plot(d["a4_tau_d_eta_H"], d["a4_tau_d_ms"], ls=mf.linestyle, color=mf.colour, lw=1.0, label="Hopf curve (A4)")
            ax.plot([d["headline_hopf_eta"]], [d["headline_tau_d_ms"]], ls="none", marker=p2.marker, ms=8, mfc="none", mec=p2.colour, mew=1.6,
                    label="ref_devalle Hopf point (P2)", zorder=5)
        n100 = int(d[f"D{D}_c100_count"].sum())
        ax.text(0.03, 0.97, f"100 Hz: {n100} crossings on {len(d[f'D{D}_tau_d_ms'])} slices", transform=ax.transAxes, va="top", fontsize=6.5,
                bbox=dict(fc="white", ec="none", alpha=0.8, pad=1.5))
        ax.set_yscale("log")
        ax.set_xlabel(r"$\bar\eta$")
        ax.set_ylabel(r"$\tau_d$ (ms)" if j == 0 else "")
        ax.set_title(rf"({'abc'[j]}) $\Delta$ = {D}", fontsize=S.FONT_SIZE_PT)
        ax.set_xlim(0, 8)
        if D == "0.3":
            ax.legend(loc="lower right", fontsize=5.5, framealpha=0.9)
    cb = fig.colorbar(sc, ax=fig.axes[:3], shrink=0.85, pad=0.01)
    cb.set_label("limit-cycle frequency (Hz); no interpolation between slices")
    axd = fig.add_subplot(gs[1, 0])
    axd.plot(d["a4_Delta_eta_H"], d["a4_Delta"], ls=mf.linestyle, color=mf.colour, lw=1.0, label="Hopf curve (A4)")
    axd.plot([d["headline_hopf_eta"]], [d["headline_Delta"]], ls="none", marker=p2.marker, ms=8, mfc="none", mec=p2.colour, mew=1.6,
             label="ref_devalle Hopf point (P2)")
    axd.set_yscale("log")
    axd.set_xlabel(r"$\bar\eta$")
    axd.set_ylabel(r"$\Delta$")
    axd.set_title(r"(d) ($\bar\eta$, $\Delta$) plane: Hopf curve only", fontsize=S.FONT_SIZE_PT)
    axd.legend(loc="lower right", fontsize=5.5)
    axt = fig.add_subplot(gs[1, 1:])
    axt.axis("off")
    axt.text(0.0, 1.0, "FAIL rows of the stored A11 table that touch F3 (not recomputed):", va="top", fontsize=S.FONT_SIZE_PT, weight="bold")
    axt.text(0.0, 0.88, "\n".join(strip_lines) if strip_lines else "none", va="top", fontsize=7, wrap=True)
    axt.text(0.0, 0.0, "Not drawn in this draft: (eta, Delta) frequency shading (A6 has no Delta slices), path arrows, the J plane.",
             va="bottom", fontsize=6.5)
    fig.text(0.01, 0.003, FOOTER if draft else "", fontsize=5.5, color="#7f0000", ha="left", va="bottom")
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


def make_F3(res=None, out_dir=None, *, tag_build: bool = False, take_home=F3_PROPOSED_TAKE_HOME, claim_limit_ids=F3_PROPOSED_CLAIM_LIMITS,
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
    cap = CAP.build_caption("F3", take_home=take_home, claim_limit_ids=claim_limit_ids, params_rows=rows, spectrogram=None, symbol_keys=("P2", "mean_field"))
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
    for k, rec in raw["records"].items():
        if (rec.get("git") or {}).get("dirty"):
            warnings.append(f"input record {k} ({rec['name']}) was written with git dirty = true")
    warnings.append(f"A4 tau_d curve against A6 Hopf points at Delta 0.3: max |difference| {d['a4_vs_a6_hopf_max_abs']:.3e} (assumes the A4 curve is at Delta 0.3, J -21; UNVERIFIED)")
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
