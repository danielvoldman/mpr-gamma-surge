"""MS13 13t-9 (DL-681 N4, DL-651 H1, H2): the journal export of FS5 (sensitivity of the surge classifier and the frequency check) as a stand-alone supplement file at the size of the draft (7.4 x 14.4 in).

Same drawing data as the draft (prepare_FS5); plain words on the image, 8 pt, sentence case; the status block of the draft and the list of the test names (panel (b) of the draft) are not on the image:
panel (b) is a plain summary and the names and reasons of the expected failures are in the supplement; the stored case names are replaced by case numbers (the mapping is in the supplement). ONE caption
(`FS5_journal_caption.txt`, seven labelled paragraphs, no word limit). Every number of the caption is read from the prepared data, the stored rows or the frozen criteria (N2).
"""
from __future__ import annotations

import textwrap
import time
from pathlib import Path

import numpy as np

from . import jcaption as JC
from . import journal as J
from . import style as S

FS5_ID = "FS5"
FS5J_HEIGHT = 14.4
MINUS = chr(0x2212)
PM = chr(0xb1)
UNDEFINED_UNVERIFIED = ("'baseline ratio rho' = the gamma-band share of the total power (1 to 150 Hz) of a baseline-only run (plan wording; the plain gloss is ours)",
                        "'case' for one of the synthetic test signals of the classifier (the stored names are in the supplement; the plain description of each case is not stored)",
                        "'variant' for one of the nine one-setting changes of the classifier (the stored names are in the supplement)",
                        "'hold runs' for the stored runs at fixed parameters at the two validation points (the draft's 'holds'; our reading, not verified)")
VAR_LABELS = {"V0": "Baseline", "band_30_120": "Band 30 to 120 Hz", "factors_1.5": "Factors 1.5", "factors_4": "Factors 4", "amin_0.05": "Minimum amplitude 0.05", "amin_0.2": "Minimum amplitude 0.2",
              "window_x0.5": "Window x0.5", "window_x2": "Window x2", "cycles_5": "Minimum cycles 5", "cycles_20": "Minimum cycles 20"}
GROUP_LABELS = ("Mean field", "Hold, point 1", "Hold, point 2", "Noise cases", "No-noise cases")


VBAND = (30, 120)      # the band of the variant band_30_120; tests/test_ms13_13t9_fs.py compares it with the stored variant name


def case_numbers(d: dict) -> tuple:
    """([case number of each row of (a)], [(case number, stored record name)]): the cases are numbered in the order of their first row."""
    names = []
    num = []
    for lab in d["syn_label"]:
        rec = lab.split(" | ")[0]
        if rec not in names:
            names.append(rec)
        num.append(names.index(rec) + 1)
    return num, list(enumerate(names, start=1))


def draw(d: dict, FG):
    """FS5 journal drawing (own plain text; the draft's panels and data placed in inches because the constrained layout cannot place them at 8 pt). Panel (a) is two axes (the cases of the noise mode and of the
    no-noise mode) with the same columns as (c), whose variant labels stand under (c)."""
    from matplotlib.patches import Patch, Rectangle
    fig, cfg = FG._journal_fig(FS5J_HEIGHT, constrained=False, fid=FS5_ID)
    T = S.figure_colour
    ax_in = FG._ax_in
    edge = T("bar_edge")
    classes, var = d["class_order"], d["variants"]
    nums, _names = case_numbers(d)
    n_noise = d["syn_mode"].count("N")
    nrow = len(d["syn_label"])
    pitch = 0.125
    h1, h2 = n_noise * pitch + 0.1, (nrow - n_noise) * pitch + 0.1
    left, wid = 1.4, 3.3
    handles: dict = {}
    # (a) in two axes: noise mode (top) and no-noise mode (below)
    for part, (lo, hi, top, hgt) in enumerate(((0, n_noise, 0.45, h1), (n_noise, nrow, 0.45 + h1 + 0.12, h2))):
        ax = ax_in(fig, left, top, wid, hgt)
        for ci, name in enumerate(classes):
            sel = d["syn_code"][lo:hi] == ci
            if not sel.any():
                continue
            yy, xx = np.nonzero(sel)
            if name == "not_run":
                mk = S.diagram_mark("not_run")
                ax.plot(xx, yy, ls="none", marker=mk.marker, ms=mk.size, color=mk.colour, mew=mk.width, zorder=4)
                handles.setdefault(name, (mk, "Not run (window does not fit)"))
            else:
                st = S.get(name)
                ax.plot(xx, yy, ls="none", marker=st.marker, ms=S.FS_SIZES["fs5_class"], color=st.colour, mec=edge, mew=0.25, zorder=4)
                handles[name] = handles.get(name, (st, 0))
                handles[name] = (st, handles[name][1] + int(sel.sum()))
        ax.set_ylim(hi - lo - 0.5, -0.5)
        ax.set_xlim(-0.6, len(var) - 0.4)
        ax.set_xticks(range(len(var)), [])
        ax.set_yticks(np.arange(hi - lo), [f"Case {k}, {lab.split(' | ')[1]}" for k, lab in zip(nums[lo:hi], d["syn_label"][lo:hi])])
        ax.tick_params(length=2)
        if part == 0:
            FG._journal_title(ax, "a", "Synthetic cases: class under each variant")
        else:
            ax.set_gid("panel part")
    # (b)
    axb = ax_in(fig, 5.2, 0.45, 2.0, 5.1)
    axb.axis("off")
    FG._journal_title(axb, "b", "Tests of the classifier")
    lines = textwrap.wrap("The synthetic tests of the classifier, read as source text and not run.", width=24)
    lines += [f"File {i + 1}: {n} test functions" for i, n in enumerate(d["tests_n"])]
    lines += textwrap.wrap(f"{len(d['tests_xfail_name'])} of them are marked as expected failures (strict); their names and reasons are in the supplement.", width=24)
    lines += [""] + textwrap.wrap("Rows of (a): noise mode above the gap, no-noise mode below it.", width=24)
    axb.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", linespacing=1.25, transform=axb.transAxes)
    from matplotlib.lines import Line2D
    hh, ll = [], []
    for name, (mk, cnt) in handles.items():
        hh.append(Line2D([], [], ls="none", marker=mk.marker, ms=getattr(mk, "size", 5.0) if name == "not_run" else S.FS_SIZES["fs5_class"], color=mk.colour, mec=edge if name != "not_run" else mk.colour, mew=0.25))
        ll.append(cnt if name == "not_run" else f"{name} ({cnt})")
    axb.legend(hh, ll, loc="lower left", ncol=1, frameon=True, framealpha=0.95, title="Class (cells)", borderaxespad=0.0)
    # (c)
    ctop = 0.45 + h1 + 0.12 + h2 + 0.5
    axc = ax_in(fig, left, ctop, wid, 1.5)
    frac = d["chg_changed"] / d["chg_n"][:, None]
    xs_c = np.arange(1, len(var))
    import matplotlib
    cmap = matplotlib.colormaps["viridis_r"]
    for i in range(frac.shape[0]):
        for j in range(frac.shape[1]):
            cell = Rectangle((j + 1 - 0.5, i - 0.5), 1.0, 1.0, fc=cmap(float(frac[i, j])), ec=S.FS_COLOURS["cell_edge"], lw=0.6, zorder=2)
            cell.set_gid("container:cell")
            axc.add_patch(cell)
    for i in range(frac.shape[0]):
        for j in range(frac.shape[1]):
            nr = int(d["chg_not_run"][i, j])
            axc.text(j + 1, i, f"{int(d['chg_changed'][i, j])}" + ("*" if nr else ""), ha="center", va="center",
                     color=S.FS_COLOURS["text_on_light"] if frac[i, j] < S.FS5_TEXT_DARK_ABOVE else S.FS_COLOURS["text_on_dark"])
    axc.set_xlim(-0.6, len(var) - 0.4)
    axc.set_xticks(range(len(var)), [VAR_LABELS[v] for v in var], rotation=90)
    axc.set_yticks(range(frac.shape[0]), [f"{g} ({int(n_)})" for g, n_ in zip(GROUP_LABELS, d["chg_n"])])
    axc.set_ylim(frac.shape[0] - 0.5, -0.5)
    axc.set_xlabel("Variant")
    FG._journal_title(axc, "c", "Records changed (shade: fraction); * includes not run")
    # (d)
    axd = ax_in(fig, 5.55, ctop, 1.65, 1.5)
    for i, w in enumerate(d["reach_W"]):
        mk = S.diagram_mark(f"w_{i}")
        axd.plot(d["reach_level"], d["reach_share"][i], color=mk.colour, ls=mk.linestyle, lw=0.8, marker=mk.marker, ms=mk.size, mfc=mk.colour if mk.filled else "none", mew=mk.width, zorder=3,
                 label=f"{w:.3g} s")
    axd.set_xlabel("Baseline ratio rho, level")
    axd.set_ylabel("Share of cells")
    axd.set_ylim(-0.75, 1.15)
    axd.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    FG._journal_title(axd, "d", "Baseline rho reached")
    axd.legend(loc="lower center", ncol=2, frameon=True, framealpha=0.95, title="Window", columnspacing=0.6, handletextpad=0.3, handlelength=1.4)
    # (e)
    etop = ctop + 1.5 + 1.75 + 0.45
    axe = ax_in(fig, 0.95, etop, 3.0, 1.7)
    bottom = np.zeros(len(d["white_W"]))
    xw = np.arange(len(d["white_W"]), dtype=float)
    legend_h = []
    for ci, name in enumerate(FG.FS5_WHITE_CLASSES):
        st = S.get(name)
        h = d["white_count"][:, ci] / d["white_den"]
        for x_, b_, h_ in zip(xw, bottom, h):
            seg = Rectangle((x_ - 0.35, b_), 0.7, h_, fc=st.colour, ec=edge, lw=0.3, hatch=S.CLASS_HATCH[name], zorder=3)
            seg.set_gid("container:bar segment")
            axe.add_patch(seg)
        legend_h.append(Patch(fc=st.colour, ec=edge, lw=0.3, hatch=S.CLASS_HATCH[name], label=name))
        for x_, b_, h_, c_ in zip(xw, bottom, h, d["white_count"][:, ci]):
            if h_ >= 0.09:
                axe.text(x_, b_ + h_ / 2, f"{int(c_)}", ha="center", va="center", bbox=dict(boxstyle="square,pad=0.1", fc=T("label_box"), ec="none", alpha=0.8), zorder=5)
        bottom = bottom + h
    for x_, n_ in zip(xw, d["white_nonNS"]):
        axe.text(x_, 1.015, f"{int(n_)}", ha="center", va="bottom", fontweight="bold")
    axe.set_xticks(xw, [f"{w:.3g}" for w in d["white_W"]])
    axe.set_ylim(0.0, 1.75)
    axe.set_xlabel("Window length (s)")
    axe.set_ylabel(f"Share of {int(d['white_den'][0])} records")
    FG._journal_title(axe, "e", "White noise (bold: records not NS)")
    axe.set_xlim(-0.6, len(xw) - 0.4)
    axe.legend(handles=legend_h, loc="upper center", ncol=3, frameon=True, framealpha=0.95, handletextpad=0.3, columnspacing=0.8)
    # (f)
    axf = ax_in(fig, 5.45, etop, 1.75, 1.7)
    mk10 = S.diagram_mark("fs5_pt")
    yv = np.arange(len(d["rb10_variant"]), dtype=float)
    axf.plot(d["rb10_fraction"], yv, ls="none", marker=mk10.marker, ms=mk10.size, color=mk10.colour, mew=mk10.width, zorder=4, label="Cells changed")
    tol = S.diagram_mark("tol_band")
    axf.axvline(FG.FS5_RB10_BOUND, color=tol.colour, ls=tol.linestyle, lw=tol.width + 0.3, label=f"Allowed {FG.FS5_RB10_BOUND:g}", zorder=2)
    axf.set_yticks(yv, [VAR_LABELS[v] for v in d["rb10_variant"]])
    axf.set_ylim(len(yv) - 0.5, -0.5)
    axf.set_xlim(-0.015, 0.40)
    axf.set_xlabel("Fraction of map-1 cells")
    FG._journal_title(axf, "f", "Main-example class " + ("unchanged" if d["rb10_headline_all_pass"] else "changed"))
    axf.legend(loc="lower right", frameon=True, framealpha=0.95)
    # (g) to (j)
    rtop = etop + 1.7 + 0.75
    pt = S.diagram_mark("fs5_pt")
    a1 = ax_in(fig, 0.8, rtop, 1.0, 1.3)
    for i, tau in enumerate(d["rb9a_tau_ms"]):
        mk = S.diagram_mark(f"rb9a_{i}")
        a1.plot([0, 1, 2], d["rb9a_diff"][i], ls="none", marker=mk.marker, ms=mk.size, color=mk.colour, zorder=4, label=f"{tau:g} ms")
    a1.axhline(d["rb9a_tol"], color=tol.colour, ls=tol.linestyle, lw=tol.width + 0.3, label="Allowed", zorder=2)
    a1.set_yscale("log")
    a1.set_yticks([1e-9, 1e-6, 1e-3], ["1e-9", "1e-6", "1e-3"])
    a1.minorticks_off()
    a1.set_ylim(1e-10, 3e-2)
    a1.set_xlim(-0.5, 2.5)
    a1.set_xticks([0, 1, 2], ["r*tau", "v", "s*tau"], rotation=90)
    FG._journal_title(a1, "g", "Unit level")
    a1.legend(loc="center", bbox_to_anchor=(0.5, 0.62), frameon=True, framealpha=0.95, title="tau", handlelength=1.2)
    a1.set_ylabel("Relative difference")
    a2 = ax_in(fig, 2.6, rtop, 0.95, 1.3)
    sp, cy = S.diagram_mark("fs5_spectral"), S.diagram_mark("fs5_cycle")
    a2.plot([0], [d["rb9b_f_spectral"]], ls="none", marker=sp.marker, ms=sp.size, color=sp.colour, zorder=4, label="Spectral peak")
    a2.errorbar([1], [d["rb9b_f_cycle"]], yerr=[d["rb9b_bound"]], ls="none", marker=cy.marker, ms=cy.size, color=cy.colour, capsize=3, lw=1.0, zorder=4, label=f"Cycle {PM} 1/W")
    a2.set_xlim(-0.6, 1.6)
    a2.set_ylim(38.0, 51.0)
    a2.set_xticks([0, 1], ["Peak", "Cycle"], rotation=90)
    FG._journal_title(a2, "h", "Frequency check: " + ("PASS" if d["rb9b_within"] else "FAIL"), fail=not d["rb9b_within"])
    a2.set_ylabel("Frequency (Hz)")
    a2.text(0.5, 0.1, f"Difference\n{d['rb9b_diff']:.3f} Hz\n> {d['rb9b_bound']:g} Hz", transform=a2.transAxes, ha="center", va="bottom", bbox=dict(boxstyle="square,pad=0.2", fc=S.FS_COLOURS["box_face"], ec=S.FS_COLOURS["patch_edge"], lw=0.4))
    a3 = ax_in(fig, 4.3, rtop, 1.25, 1.3)
    xs3 = np.arange(3, dtype=float)
    fr3 = d["rb9c_changed"] / d["rb9c_n"]
    a3.plot(xs3, fr3, ls="none", marker=pt.marker, ms=pt.size, color=pt.colour, mew=pt.width, zorder=4)
    a3.axhline(d["rb9c_bound"], color=tol.colour, ls=tol.linestyle, lw=tol.width + 0.3, label=f"Allowed {d['rb9c_bound']:g}", zorder=2)
    a3.plot(xs3[1:], fr3[1:], ls="none", marker=S.FS5_REPORTED["marker"], ms=S.FS_SIZES["fs5_reported_ring"], mfc="none", mec=S.FS5_REPORTED["colour"], mew=S.FS5_REPORTED["width"], zorder=3,
            label="Reported only", gid="rb9c_reported")
    a3.set_xticks(xs3, ["Map 1", "Map 2", "Subgrid"], rotation=90)
    a3.set_xlim(-0.5, 2.5)
    a3.set_ylim(-0.09, 0.95)
    FG._journal_title(a3, "i", f"Band {VBAND[0]} to {VBAND[1]} Hz")
    a3.set_ylabel("Fraction changed")
    a3.legend(loc="upper left", frameon=True, framealpha=0.95)
    for x_, c_, n_ in zip(xs3, d["rb9c_changed"], d["rb9c_n"]):
        hi_ = c_ / n_ > 0.2
        a3.text(x_ - (0.25 if hi_ else 0.0), c_ / n_ + (0.0 if hi_ else 0.16), f"{int(c_)}/{int(n_)}", ha="right" if hi_ else "center", va="center" if hi_ else "bottom")
    a4 = ax_in(fig, 6.3, rtop, 0.9, 1.3)
    for i, (tau, f, c) in enumerate(zip(d["rb9d_tau_ms"], d["rb9d_f_pk"], d["rb9d_class"])):
        st = S.get(c)
        a4.plot([tau], [f], ls="none", marker=st.marker, ms=S.FS_SIZES["fs5_class_g4"], color=st.colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], zorder=4, label=f"{c}" if i == 0 else None)
    ex = S.diagram_mark("fs5_expected")
    a4.plot(d["rb9d_tau_ms"], d["rb9d_headline_f"] * d["rb9d_expected_ratio"], ls="none", marker=ex.marker, ms=ex.size, color=ex.colour, zorder=3, label="10/tau")
    a4.set_xticks(d["rb9d_tau_ms"], [f"{t:g}" for t in d["rb9d_tau_ms"]])
    a4.set_xlim(7.0, 13.0)
    a4.set_ylim(38.0, 82.0)
    a4.set_xlabel("tau (ms)")
    FG._journal_title(a4, "j", "Reported only")
    a4.set_ylabel("Peak frequency (Hz)")
    a4.legend(loc="upper center", frameon=True, framealpha=0.95)
    J.finish(fig, cfg, FS5_ID)
    return fig


# ---- text -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def consts(d: dict, rows: list, raw: dict, crit: dict) -> dict:
    pv = JC.pv
    c = crit["classifier"]
    syn_cases = len({lab.split(" | ")[0] for lab in d["syn_label"]})
    return {"type": pv(rows, "model.type", "A8_sensitivity"), "n_cases": syn_cases, "n_rows": len(d["syn_label"]), "n_var": len(d["variants"]) - 1, "band": [JC.num(v) for v in c["band_primary_hz"]["value"]],
            "cycles": JC.num(c["min_cycles"]["value"]), "amin": JC.num(c["amin_factor"]["value"]), "rb10_max_pct": 100.0 * float(np.max(d["rb10_fraction"])), "n_a8": len(raw["a8"]),
            "tau_a": [float(x) for x in d["rb9a_tau_ms"]], "tau_d": [float(x) for x in d["rb9d_tau_ms"]], "var": variant_values(d), "rw": ramp_windows(d)}


def ramp_windows(d: dict) -> dict:
    """The ramp durations and window lengths of the rows of (a), per mode, parsed from the row labels 'record | 120 s | W 2'."""
    out: dict = {"N": ([], []), "D": ([], [])}
    for lab, mode in zip(d["syn_label"], d["syn_mode"]):
        _rec, t, w = lab.split(" | ")
        t_, w_ = float(t.replace(" s", "")), float(w.replace("W ", ""))
        if t_ not in out[mode][0]:
            out[mode][0].append(t_)
            out[mode][1].append(w_)
    return out


def variant_values(d: dict) -> dict:
    """The values of the variants, parsed from the stored variant names (band_30_120, factors_1.5, amin_0.05, window_x0.5, cycles_5): {group: [values]}."""
    out: dict = {}
    for v in d["variants"][1:]:
        g, _, tail = v.partition("_")
        if g == "band":
            out[g] = [float(x) for x in tail.split("_")]
        else:
            out.setdefault(g, []).append(float(tail.lstrip("x")))
    return out


def _e(x: float) -> str:
    m, e = f"{x:.1e}".split("e")
    return f"{m}e{int(e)}"


def _and(xs) -> str:
    xs = [JC.num(x) for x in xs]
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def caption(d: dict, rows: list, crit: dict, *, ids, c: dict, FG) -> str:
    n = JC.num
    W = float(JC.pv(rows, "analysis.window_s", "A8_sensitivity"))
    fw = d["white_nonNS"]
    wl = d["white_W"][:4]
    if not d["rb10_headline_all_pass"] or d["rb9b_within"]:
        raise JC.JCaptionError("FS5: the stored RB10 or RB9(b) result is not the one the take-home wording needs (RB10 passes, RB9(b) fails)")
    take = (f"The surge classifier (the rule fixed before the analysis that sorts runs into classes; a surge is a transient rise of gamma-band power, {c['band'][0]} to {c['band'][1]} Hz; its call for damped against non-damped oscillations is provisional) was run on {c['n_cases']} synthetic cases and on recorded mean-field runs under "
            f"{c['n_var']} variants that each change one setting, and the frequency check (the spectral and the cycle frequency must differ by at most {d['rb9b_bound']:g} Hz) failed at the main example (the run fixed before the analysis as the main case): the spectral peak (the peak of the power spectrum of the simulated signal) is at {d['rb9b_f_spectral']:.1f} Hz and the cycle frequency "
            f"(the frequency of the oscillation that starts at the Hopf point, where the resting state starts to oscillate) is {d['rb9b_f_cycle']:.3f} Hz, a difference of {d['rb9b_diff']:.3f} Hz against the allowed 1/W = {d['rb9b_bound']:g} Hz, "
            f"where W = {n(W)} s is the window length (a failed check). Which classes change is drawn per variant. Short windows give false surges: {int(fw[0])}, {int(fw[1])}, {int(fw[2])} and {int(fw[3])} of {int(d['white_den'][0])} white-noise records "
            f"are not NS (no rise) at windows of {n(round(wl[0], 3))}, {n(round(wl[1], 3))}, {n(round(wl[2], 3))} and {n(round(wl[3], 3))} s. The class of the main example is unchanged under all {c['n_var']} variants, and at most {c['rb10_max_pct']:.2f} percent of the "
            f"{d['rb10_n_cells']} map-1 cells change class against the {100 * FG.FS5_RB10_BOUND:g} percent allowed (passes). The frequency mapping at the unit level passes ({_e(d['rb9a_value'])} against {d['rb9a_tol']:g}; one test at a time), the band check "
            f"passes ({int(d['rb9c_changed'][0])} of {int(d['rb9c_n'][0])} cells change class), and the check at other synaptic decay times is reported only.")
    panels = " ".join([
        f"(a) The class that the classifier gives each of the {c['n_cases']} synthetic cases (the {c['n_rows']} rows: the cases of the noise mode at the ramp durations {_and(c['rw']['N'][0])} s, the window being {_and(c['rw']['N'][1])} s, and the cases of the no-noise mode at {_and(c['rw']['D'][0])} s) "
        f"under the baseline settings and the {c['n_var']} variants (columns): one mark per cell, class names as in the Key, and 'not run' where the variant's window does not fit; the expected class of a case is not recorded and is not drawn. "
        "The case numbers stand for the recorded case names (in the supplement).",
        f"(b) A summary of the tests of the classifier, read as source text and never run: {d['tests_n'][0]} and {d['tests_n'][1]} test functions in two files, {len(d['tests_xfail_name'])} of them marked as expected failures (strict); the names and the reasons are in the supplement.",
        f"(c) For each group of records (rows) and each variant (columns), the number of records whose class differs from the baseline over the number of records, with the shade giving the fraction (0 to 1); records that the variant could not run "
        f"(window too long) are counted as not run, not as unchanged; {int(d['chg_changed'].sum())} changes over all groups and variants.",
        f"(d) The share of the cells of the maps whose baseline ratio rho (the gamma-band share of the total power in a baseline-only run) is at or above each level, for the {len(d['reach_W'])} window lengths (lines; the numbers of cells per window are {_and([int(x) for x in d['reach_n_cells']])}).",
        f"(e) The number of white-noise records (of {int(d['white_den'][0])} per window) in each class at the baseline settings, by window length; white noise has no resonance, so these are rates of the classifier's logic and not predictions for the model's own noise; "
        "the bold number above a bar is the number of records that are not NS.",
        f"(f) The fraction of the {d['rb10_n_cells']} map-1 cells whose class changes under each variant (marks) against the {FG.FS5_RB10_BOUND:g} allowed (dashed line); the class of the main example is unchanged under every variant.",
        f"(g) The relative difference between the dimensional and the non-dimensional computation of r times tau, v and s times tau at the synaptic decay times {_and(c['tau_a'])} ms (a test at the unit level on a 1 s ramp, not on the main example), against {d['rb9a_tol']:g} allowed (dashed line).",
        f"(h) The frequency check at the main example: the spectral peak ({d['rb9b_f_spectral']:.1f} Hz) and the cycle frequency ({d['rb9b_f_cycle']:.3f} Hz, with the allowed difference 1/W = {d['rb9b_bound']:g} Hz as the bar); the difference is {d['rb9b_diff']:.3f} Hz, so the check fails, "
        f"and the cells of map 1 and map 2 in which the two frequencies agree within 1/W are {d['rb9b_map1_within']} of {d['rb9b_map1_n']} and {d['rb9b_map2_within']} of {d['rb9b_map2_n']} (reported, no allowed fraction).",
        f"(i) The fraction of cells that change class when the gamma band is {n(c['var']['band'][0])} to {n(c['var']['band'][1])} Hz instead of {c['band'][0]} to {c['band'][1]} Hz: map 1 ({int(d['rb9c_changed'][0])} of {int(d['rb9c_n'][0])}, judged against {d['rb9c_bound']:g}), and map 2 and the noisy subgrid (map cells re-run with noise; a map cell (one parameter pair of a grid of mean-field runs) is one cell of a map), reported, not judged (open rings).",
        f"(j) The peak frequency (the peak of the power spectrum) and class of the main example at the synaptic decay times {_and(c['tau_d'])} ms, and the main-example value times 10/tau (marks labelled 10/tau); reported only, it feeds no check.",
    ])
    settings = ("No spectrogram (power against time and frequency) is drawn in this figure. In the settings below the symbols of the reference point are eta_bar (mean excitability), J (coupling), Delta (heterogeneity) and tau_d (synaptic decay time). " + JC.settings_line(crit))
    params = (f"Recorded values (the complete list with the key names as recorded is in the supplement): model {c['type']} (the mean-field model; the mean field is the model's equations for the average activity of the population); "
              f"classifier settings of the baseline: window {n(W)} s, gamma band {c['band'][0]} to {c['band'][1]} Hz, minimum {c['cycles']} cycles, threshold {c['amin']} times the reference amplitude; the {c['n_var']} variants change one of these settings each "
              f"(band {n(c['var']['band'][0])} to {n(c['var']['band'][1])} Hz; the relative and absolute factors together {_and(c['var']['factors'])}; the minimum amplitude {_and(c['var']['amin'])}; the window times {_and(c['var']['window'])}; the minimum cycles {_and(c['var']['cycles'])}); "
              f"{c['n_a8']} recorded classifications; window lengths {_and([round(float(x), 3) for x in d['white_W']])} s in (d) and (e); {int(d['env_n_records'])} baseline records ({int(d['env_any_above'])} have a sample at or above {c['amin']} times the reference amplitude {d['a_ref']:.6f}).")
    lines = [JC.failed_line(r) for r in d["strip"]]
    failed = (f"Failed checks that concern this figure ({len(lines)}): " + "; ".join(lines) + f". The value is blank in the stored table; the numbers ({d['rb9b_f_spectral']:.1f} Hz, {d['rb9b_f_cycle']:.3f} Hz and the difference {d['rb9b_diff']:.3f} Hz) are those of the recorded evaluation. "
              "The estimator for damped against non-damped oscillations also fails part of its own test (a limit, listed below). The project's other failed checks are not about this figure; all of them are listed in the supplement. " + JC.title_sentence(FS5_ID))
    limits = ("In the limits below, T_ramp is the ramp duration T_ramp (in seconds), the main example is the run fixed before the analysis as the main case, the network is a simulated network of N spiking neurons, and control (the same network without the ramp) runs are runs of the project that are not drawn in this figure. "
              + JC.limits_paragraph(ids))
    rest = JC.uncode(" ".join([take, panels, settings, params, failed, limits]), FS5_ID)
    key = " ".join(x for x in [
        JC.key_symbols(rest, "tau", "r", "v"),
        "A surge is a transient rise of gamma-band power; the classes are S+ (absolute and relative rise, ending), S-rel (relative rise only), S-abs (absolute rise only), S-sus (a rise that does not end), NS (no rise), "
        "D-tr (a rise that ends, in the noise-free mean field, which is the model's equations for the average activity of the population), D-sus and D-none (no episode); a failed check = a stated criterion that the result does not meet; W = the window length of the classifier.",
        JC.key_words(rest)] if x)
    return JC.assemble(FS5_ID, take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)


# ---- supplement data, alt text, build ---------------------------------------------------------------------------------------------------------------

def source_rows(d: dict, FG) -> list:
    rows: list = []
    src = FG._src
    nums, _ = case_numbers(d)
    for i, (k, lab) in enumerate(zip(nums, d["syn_label"])):
        for j, v in enumerate(d["variants"]):
            src(rows, "a", f"case {k}, {lab.split(' | ')[1]}: class code {int(d['syn_code'][i, j])} = {d['class_order'][int(d['syn_code'][i, j])]} (x = variant column, y = row)", [j], [i])
    for gi in range(d["chg_changed"].shape[0]):
        for vj, v in enumerate(d["variants"][1:]):
            src(rows, "c", f"{GROUP_LABELS[gi]}, {VAR_LABELS[v]}: records changed, records, not run", [vj], [d["chg_changed"][gi, vj]], [d["chg_n"][gi]])
    for i, w in enumerate(d["reach_W"]):
        src(rows, "d", f"share of cells at or above the level, window {w:.3g} s (x = level)", d["reach_level"], d["reach_share"][i])
    for k, w in enumerate(d["white_W"]):
        for ci, cn in enumerate(FG.FS5_WHITE_CLASSES):
            src(rows, "e", f"white-noise records in class {cn} at window {w:.3g} s (x = window)", [w], [d["white_count"][k, ci]])
    src(rows, "f", "fraction of map-1 cells that change class (x = fraction, y = variant row)", d["rb10_fraction"], np.arange(len(d["rb10_fraction"]), dtype=float))
    for i, tau in enumerate(d["rb9a_tau_ms"]):
        src(rows, "g", f"relative difference at tau {tau:g} ms (x = r*tau, v, s*tau)", [0, 1, 2], d["rb9a_diff"][i])
    src(rows, "h", "spectral peak and cycle frequency in Hz, difference, bound (x = 0, 1, 2, 3)", [0, 1, 2, 3], [d["rb9b_f_spectral"], d["rb9b_f_cycle"], d["rb9b_diff"], d["rb9b_bound"]])
    src(rows, "i", "fraction of cells that change class (x = map 1, map 2, subgrid)", [0, 1, 2], d["rb9c_changed"] / d["rb9c_n"])
    src(rows, "j", "peak frequency in Hz (x = tau in ms)", d["rb9d_tau_ms"], d["rb9d_f_pk"])
    return rows


FG_RB10 = 0.1


def alt_text(d: dict, c: dict) -> dict:
    return {
        "a": f"A grid of class marks: {c['n_rows']} rows (the synthetic cases) by {len(d['variants'])} columns (the baseline and the variants); the colour and shape of each mark give the class; the rows above the dividing line are the noise-mode cases.",
        "b": "A short text summary of the tests of the classifier and the key of the class marks of (a).",
        "c": "A table of fractions: five groups of records by nine variants, each cell giving the number of records whose class changes over the number of records.",
        "d": "Six lines of the share of cells at or above five levels of the baseline ratio rho, one line per window length.",
        "e": f"Six stacked bars of the classes of {int(d['white_den'][0])} white-noise records at six window lengths, with the number of records that are not NS above each bar ({', '.join(str(int(x)) for x in d['white_nonNS'])}).",
        "f": f"Nine marks of the fraction of map-1 cells that change class under the nine variants, all left of the dashed line at {FG_RB10}.",
        "g": f"Marks of the relative difference at the unit level for two synaptic decay times and three quantities, far below a dashed line at {d['rb9a_tol']:g}.",
        "h": f"A spectral peak at {d['rb9b_f_spectral']:.1f} Hz and a cycle frequency at {d['rb9b_f_cycle']:.3f} Hz with an error bar of {d['rb9b_bound']:g} Hz; the title is red and reads 'Frequency check: FAIL'.",
        "i": f"Three marks of the fraction of cells that change class (map 1, map 2, subgrid) with a dashed line at {d['rb9c_bound']:g} and open rings on the two reported ones.",
        "j": "Three marks of the peak frequency at three synaptic decay times with the main-example value times 10 over tau as a second mark.",
    }


def sections(d: dict) -> tuple:
    nums, names = case_numbers(d)
    mapping = ("The journal panels (a) to (j) are the draft panels (a), (b), (c), (d), (e), (f), (g1), (g2), (g3) and (g4) in this order (same data, same size 7.4 x 14.4 in). The draft status block (text under the panels) is not on the image: "
               "its lines are in the 'Status block' section of this sheet; the title of (h) carries the plain form 'Frequency check: FAIL'. The draft panel (b) listed the test names and their reasons on the image; "
               "they are in the table below, and the image shows a summary.")
    cases = "| case number | stored record name |\n|---|---|\n" + "\n".join(f"| {k} | {nm} |" for k, nm in names)
    xf = "| expected failure (strict) | reason as recorded in the test file |\n|---|---|\n" + "\n".join(f"| {a} | {b} |" for a, b in zip(d["tests_xfail_name"], d["tests_xfail_reason"]))
    var = "| plain label in the figure | stored variant name |\n|---|---|\n" + "\n".join(f"| {VAR_LABELS[v]} | {v} |" for v in d["variants"])
    names_t = ("| plain word in the caption | stored name |\n|---|---|\n| frequency check | RB9(b) b_spectral_vs_cycle_headline (the spectral and the cycle frequency must differ by at most 1/W) |\n"
               "| band check | RB9(c) c_band_30_120_map1 |\n| main-example class under the variants | RB10 surge_definition_sensitivity_map1 |")
    return (("Mapping of the draft panels to the journal panels (DL-681)", mapping), ("Case numbers of panel (a) and the stored record names", cases),
            ("The expected failures of the tests, with the reasons recorded in the test files", xf), ("Variant labels and the stored variant names", var), ("Stored names behind the plain words of the caption", names_t))


def build(FG, res, out_dir, root, script, claim_limit_ids, tag_build) -> dict:
    import dataclasses
    import matplotlib.pyplot as plt
    from .. import provenance as P
    root = Path(root) if root is not None else FG.repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "journal" / FS5_ID
    t = {"start": time.perf_counter()}
    raw = FG.load_FS5(res, root)
    t["load"] = time.perf_counter()
    d = FG.prepare_FS5(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for key, rec in raw["records"].items():
        for r in FG.make_param_table(rec["config"]):
            rows.append({**r, "panel": key, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    crit, _ = FG.F.K.load_frozen_criteria(root)
    crows = [r for r in rows if r["key"] in FG.FS5_CAPTION_KEYS]
    cap0 = FG.CAP.build_caption("FS5", take_home=FG.FS5_TAKE_HOME, claim_limit_ids=claim_limit_ids, params_rows=crows, spectrogram=None, symbol_keys=(), notes=FG.fs5_caption_notes(d),
                                class_key=FG.CAP.class_key_line("ND"), classifier_line=FG.CAP.classifier_line(crit), main_failures=FG.FS5_MAIN_FAILURES, swept={})
    plain_md = FG.PL.pairing_markdown(claim_limit_ids, None, cap0.text)
    c = consts(d, rows, raw, crit)
    text = caption(d, rows, crit, ids=claim_limit_ids, c=c, FG=FG)
    cap = dataclasses.replace(cap0, text=text)
    cfg = J.load_config(root)
    out.mkdir(parents=True, exist_ok=True)
    stem = "FS5_journal"
    with plt.rc_context(J.rc_params(cfg)):
        fig = draw(d, FG)
        saved = J.save_all(fig, out, stem, cfg)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    drawn = FG.drawn_data_sha256(d)
    P.atomic_write_text(out / f"{stem}_caption.txt", text + "\n")
    P.atomic_write_text(out / f"{stem}_drawn_data_sha256.txt", drawn + "\n")
    warnings = [f"input record {k} ({rec['name']}) was written with git dirty = true" for k, rec in raw["records"].items() if (rec.get("git") or {}).get("dirty")]
    prov_kw = dict(script=script, inputs=[res / p for p in FG.FS5_INPUTS] + [root / p for p in FG.FS5_TEST_FILES], params_rows=rows,
                   modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py", "src/mprsurge/plotting/jfs5.py", "src/mprsurge/plotting/nordlie.py",
                            "src/mprsurge/plotting/figprov.py"],
                   configs=["configs/A8.yaml", "configs/A8_sensitivity.yaml"], claim_limits=cap.claim_limits, spectrogram=None, tag_build=tag_build, root=root)
    status_text = "\n".join(FG.fs5_strip_lines(d))
    return FG._journal_tail(FS5_ID, out, stem, saved, cap, drawn, d, raw, prov_kw, warnings, strip=[], footer=FG.FS5_FOOTER, timing_t=t, source_rows=source_rows(d, FG), alt=alt_text(d, c),
                            pointers=(), cfg=cfg, status_text=status_text, plain_md=plain_md, extra_sections=sections(d), strip_rows=None, zip_note=False, single_caption=True)
