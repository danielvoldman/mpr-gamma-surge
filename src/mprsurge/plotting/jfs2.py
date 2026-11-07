"""MS13 13t-6 (DL-651 H1, H2): the journal export of FS2 (the M3 validation figure) as a stand-alone supplement file.

Same drawing data as the draft (prepare_FS2); the draft's size (7.4 x 11.2 in), gridspec and panel order are kept; the text is plain words (no check, step or key IDs), 8 pt, sentence case.
ONE caption (`FS2_journal_caption.txt`, seven labelled paragraphs, no word limit). Every number in the caption is read from the prepared data or the recorded parameter rows; only the wording is typed here.
Terms that no plan or Key defines in plain words are listed in UNDEFINED_UNVERIFIED.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from . import jcaption as JC
from . import journal as J
from . import style as S

FS2_ID = "FS2"
FS2J_HEIGHT = 11.2
UNDEFINED_UNVERIFIED = ("validation points 1 and 2 (defined here from the parameter table of the plan; the names ref_ceni and ref_devalle are internal)",
                        "'REPORTED FAILURE' of the straight-line fit is written as 'failed check' (ruled draft wording kept in the supplement)",
                        "the single-source status of the frequency-against-J check (ruled draft wording: single source, not verified)")
CELL_NAMES = {"ceni_3ms": "Point 1, 3 ms", "ceni_4.95ms": "Point 1, 4.95 ms", "ceni_8ms": "Point 1, 8 ms", "devalle_5ms": "Point 2, 5 ms", "devalle_50ms": "Point 2, 50 ms",
              "k8_5e4_5ms": "Point 2, 5 ms, N 50,000"}
MINUS = "−"
LS_NET = {"s3_net_1e4": "--", "s3_net_5e4": ":"}           # non-colour distinction of the three line kinds in (c) to (g): mean field solid, network of 10,000 dashed, network of 50,000 dotted


def _fmt(x: float, nd: int = 2) -> str:
    return f"{x:.{nd}f}".replace("-", MINUS)


def draw(d: dict, FG):
    """FS2 journal drawing (own plain text, the draft's gridspec and size)."""
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator
    fig, cfg = FG._journal_fig(FS2J_HEIGHT, constrained=True, fid=FS2_ID)
    cyc, hp = S.diagram_mark("a5_cycle"), S.diagram_mark("hopf_point")
    mf, n1, n5 = S.diagram_mark("s3_mf"), S.diagram_mark("s3_net_1e4"), S.diagram_mark("s3_net_5e4")
    paper, tol = S.diagram_mark("k7_paper"), S.diagram_mark("tol_band")
    fig.get_layout_engine().set(w_pad=0.18, h_pad=0.14)
    gs = fig.add_gridspec(4, 6, height_ratios=[1.35, 1.5, 1.25, 1.25])
    lw_fit = 1.6
    # (a)
    ax = fig.add_subplot(gs[0, 0:3])
    for name in ("up", "down"):
        ax.plot(d[f"a5c_{name}_tau_d"], d[f"a5c_{name}_amp"], color=cyc.colour, lw=cyc.width, zorder=3, label="Stable cycle" if name == "up" else None)
    ax.axvline(d["hopf_a4_ms"], color=hp.colour, ls=hp.linestyle, lw=hp.width, label=f"Hopf point {d['hopf_a4_ms']:.4f} ms", zorder=1)
    ax.axvline(FG.FS2_K7_PAPER_MS, color=paper.colour, ls=paper.linestyle, lw=paper.width, label=f"Published {FG.FS2_K7_PAPER_MS:g} ms", zorder=1)
    ax.plot(d["k7_tau"], d["k7_mf_vptp"], ls="none", marker=mf.marker, ms=mf.size, color=mf.colour, zorder=5, label="Mean field")
    ax.set_xlabel("tau_d (ms)")
    ax.set_ylabel("Amplitude of v (max minus min)")
    ax.set_xlim(2.5, 10.5)
    FG._journal_title(ax, "a", "Amplitude of v against tau_d")
    ax.legend(loc="lower right", frameon=True, framealpha=0.95)
    # (b) red: the straight-line fit misses its residual rule; evidence = both fits and their residuals in the legend
    axb = fig.add_subplot(gs[0, 3:6])
    for name in ("up", "down"):
        axb.plot(d[f"a5c_{name}_tau_d"], d[f"a5c_{name}_amp"] ** 2, color=cyc.colour, lw=cyc.width, zorder=3, label="Stable cycle, amplitude squared" if name == "up" else None)
    h, w = d["fit_hopf_ms"], d["fit_window_ms"]
    x = np.array([h + w[0], h + w[1]])
    axb.plot(x, d["fit_s4_up_slope"] * (x - h) + d["fit_s4_up_intercept"], color=paper.colour, lw=lw_fit, ls="-.", zorder=4,
             label=f"Fit, {w[0]:g} to {w[1]:g} ms above Hopf point:\nresidual {100 * d['fit_s4_up_max_resid_frac']:.2f} percent ({100 * d['fit_rel_tol']:g} allowed)")
    pw = d["fit_posthoc_window_ms"]
    xp = np.array([h + pw[0], h + pw[1]])
    axb.plot(xp, d["fit_posthoc_near_hopf_slope"] * (xp - h) + d["fit_posthoc_near_hopf_intercept"], color=tol.colour, lw=lw_fit, ls="--", zorder=4,
             label=f"Exploratory fit, window chosen\nafter the results: residual {100 * d['fit_posthoc_near_hopf_max_resid_frac']:.2f} percent")
    axb.axvline(h, color=hp.colour, ls=hp.linestyle, lw=hp.width, zorder=1)
    axb.set_xlim(h - 0.1, 6.0)
    axb.set_ylim(0.0, 14.0)
    axb.set_xlabel("tau_d (ms); axis cut at 6 ms, the cycle runs to 10 ms")
    axb.set_ylabel("Amplitude of v, squared")
    FG._journal_title(axb, "b", "Amplitude squared: FAIL", fail=True)
    axb.legend(loc="upper right", frameon=True, framealpha=0.95)
    # (c) to (g)
    sub = gs[1, :].subgridspec(2, 5, wspace=0.12, height_ratios=[0.16, 1.0])
    axl = fig.add_subplot(sub[0, :])
    axl.axis("off")
    axl.set_gid("legend axes")
    axl.legend([Line2D([], [], color=m.colour, lw=m.width, ls=LS_NET.get(k_, m.linestyle)) for k_, m in (("s3_mf", mf), ("s3_net_1e4", n1), ("s3_net_5e4", n5))],
               ["Mean field", "Network, N = 10,000 (all panels)", "Network, N = 50,000 (point 2, 5 ms only)"], loc="center", ncol=3, frameon=False)
    specs = [("Point 1,\n3 ms", [("mf_ceni_3.0", "s3_mf"), ("net_ceni_3ms", "s3_net_1e4")]), ("Point 1,\n4.95 ms", [("mf_ceni_4.95", "s3_mf"), ("net_ceni_4.95ms", "s3_net_1e4")]),
             ("Point 1,\n8 ms", [("mf_ceni_8.0", "s3_mf"), ("net_ceni_8ms", "s3_net_1e4")]),
             ("Point 2,\n5 ms", [("mf_devalle_5.0", "s3_mf"), ("net_devalle_5ms", "s3_net_1e4"), ("net_k8_5e4_5ms", "s3_net_5e4")]),
             ("Point 2,\n50 ms", [("mf_devalle_50.0", "s3_mf"), ("net_devalle_50ms", "s3_net_1e4")])]
    for i, (title, series) in enumerate(specs):
        axt = fig.add_subplot(sub[1, i])
        for key, mark in series:
            st = S.diagram_mark(mark)
            axt.plot(d[f"tr_{key}_t"], d[f"tr_{key}_r"], color=st.colour, lw=st.width, ls=LS_NET.get(mark, st.linestyle), zorder=3 if mark == "s3_mf" else 2)
        FG._journal_title(axt, "cdefg"[i], title)
        axt.set_xlabel("Time (ms)")
        axt.set_xticks([9600.0, 10000.0])
        axt.yaxis.set_major_locator(MaxNLocator(nbins=2, min_n_ticks=2))
        axt.set_xticklabels(["9,600", "10,000"])
        if i == 0:
            axt.set_ylabel("r, last 400 ms")
    # (h)
    axd = fig.add_subplot(gs[2, 0:2])
    names = d["net_cells"]
    xs = np.arange(len(names), dtype=float)
    for q, glyph, lab in (("f_rel_diff", "d_freq", "Peak frequency"), ("r_mean_rel_diff", "d_mean", "Mean of r"), ("r_fit_ptp_rel_diff", "d_ptp", "Fitted amplitude of r")):
        axd.plot(xs, 100 * d[f"net_{q}"], ls="none", marker=S.FS2_DIFF_MARKS[glyph], ms=S.FS_SIZES["fs2_diff"], color=S.FS_COLOURS["mark_dark"], label=lab, zorder=4)
    axd.axhline(100 * FG.FS2_K8_TOL, color=tol.colour, ls=tol.linestyle, lw=tol.width, label="Tolerance, 5 percent")
    axd.axhline(-100 * FG.FS2_K8_TOL, color=tol.colour, ls=tol.linestyle, lw=tol.width)
    axd.axhline(0.0, color=S.FS_COLOURS["patch_edge"], lw=0.5, zorder=1)
    axd.set_xticks(xs)
    axd.set_xticklabels([CELL_NAMES[n] for n in names], rotation=90, ha="center")
    axd.set_ylim(-7.0, 42.0)
    axd.set_ylabel("(Network " + MINUS + " mean field) / mean field (percent)")
    FG._journal_title(axd, "h", "Network against mean field")
    axd.legend(loc="upper left", frameon=True, framealpha=0.95)
    # (i)
    axe = fig.add_subplot(gs[2, 2:4])
    k9 = S.diagram_mark("k9_pt")
    axe.plot(d["k9_eta_bar"], d["k9_ratio"], ls="none", marker=k9.marker, ms=k9.size, color=k9.colour, zorder=4, label="Largest ratio")
    axe.axhspan(FG.FS2_K9[0] - FG.FS2_K9[1], FG.FS2_K9[0] + FG.FS2_K9[1], color=tol.colour, alpha=0.3, lw=0, label="Target band")
    axe.set_xticks(d["k9_eta_bar"])
    axe.set_ylim(FG.FS2_K9[0] - 3 * FG.FS2_K9[1], FG.FS2_K9[0] + 3 * FG.FS2_K9[1])
    axe.set_xlim(0.5, 4.5)
    axe.set_xlabel(FG.JETA + " (mean excitability)")
    axe.set_ylabel("Delta/" + FG.JETA)
    FG._journal_title(axe, "i", "Heterogeneity ratio")
    axe.legend(loc="lower right", frameon=True, framealpha=0.95)
    # (j)
    axk = fig.add_subplot(gs[2, 4:6])
    k11 = S.diagram_mark("k11_pt")
    axk.plot(-d["k11_J_H"], d["k11_ratio"], ls="none", marker=k11.marker, ms=k11.size, color=k11.colour, zorder=4, label="Frequency ratio")
    for sgn in (-1, 1):
        axk.axhline(1.0 + sgn * FG.FS2_K11, color=tol.colour, ls=tol.linestyle, lw=tol.width, label="Target band" if sgn == -1 else None)
    axk.set_xscale("log")
    axk.set_xticks([5e-4, 1e-3, 2e-3, 5e-3])
    axk.set_xticklabels(["0.0005", "0.001", "0.002", "0.005"])
    axk.minorticks_off()
    axk.set_ylim(0.980, 1.014)
    axk.set_xlabel(MINUS + "J at the Hopf point (log axis)")
    axk.set_ylabel("Ratio (Delta = 0.0001)")
    FG._journal_title(axk, "j", "Frequency ratio")
    axk.legend(loc="lower left", frameon=True, framealpha=0.95)
    # (k)
    axf = fig.add_subplot(gs[3, 0:3])
    k10 = S.diagram_mark("k10_curve")
    axf.plot(d["k10_tau_d"], d["k10_freq"], color=k10.colour, lw=k10.width, label=f"Linear frequency ({FG.JETA} 1, J {MINUS}20)", zorder=3)
    lo, hi = d["k10_band_hz"]
    sl = d["k10_band_slack"]
    for yv, lab in ((lo * (1 - sl), f"Target band, plus or minus {100 * sl:g} percent"), (hi * (1 + sl), None)):
        axf.axhline(yv, color=tol.colour, ls=tol.linestyle, lw=tol.width, label=lab)
    axf.set_xlabel("tau_d (ms)")
    axf.set_ylabel("Frequency (Hz)")
    FG._journal_title(axf, "k", "Frequency against tau_d")
    axf.legend(loc="center right", bbox_to_anchor=(1.0, 0.68), frameon=True, framealpha=0.95)
    # (l) red: not reproduced as worded; evidence = the changes in the legend
    axg = fig.add_subplot(gs[3, 3:6])
    for tau, key in (("8.0", "k10_j8"), ("20.0", "k10_j20"), ("40.0", "k10_j40")):
        st = S.diagram_mark(key)
        axg.plot(d[f"k10_J_{tau}"], d[f"k10_lin_{tau}"], color=st.colour, ls=st.linestyle, lw=0.7, marker=st.marker, ms=st.size, zorder=3,
                 label=f"tau_d {float(tau):g} ms: change {100 * d[f'k10_rel_change_{tau}']:.1f} percent (limit {100 * d['k10_j_limit']:.0f})")
    axg.set_xlabel("J")
    axg.set_ylabel("Linear frequency (Hz)")
    axg.set_xticks(d["k10_J_8.0"])
    axg.set_xticklabels([f"{x:g}".replace("-", MINUS) for x in d["k10_J_8.0"]])
    axg.set_ylim(10.0, 28.0)
    FG._journal_title(axg, "l", "Frequency against J: FAIL", fail=True)
    axg.legend(loc="upper left", frameon=True, framealpha=0.95)
    fig.canvas.draw()
    pts = axk.get_lines()[0]
    n_co = FG.coincident_marks(axk, pts, S.FS_SIZES["fs2_coincide_mark"])
    n_all = len(pts.get_xdata())
    axk.text(0.5, 0.85, f"{n_co} of {n_all} marks overlap\nat the drawn size; the\nrecorded values differ", transform=axk.transAxes, ha="center", va="top",
             color=S.figure_colour("text_dark")).set_gid("coincide_note")
    J.finish(fig, cfg, FS2_ID)
    return fig


# ---- text ------------------------------------------------------------------------------------------------------------------------------------------

def consts(d: dict, rows: list) -> dict:
    pv = JC.pv
    return {"type": pv(rows, "model.type", "A5"), "tau": pv(rows, "model.tau_ms", "A5"), "N": pv(rows, "network.N", "S3 network ceni"), "N5": pv(rows, "network.N", "S3 network K8 (N 50,000)"),
            "hold": pv(rows, "durations.hold_s", "A5"), "p1": (pv(rows, "model.eta_bar", "S3 mean field point 1"), pv(rows, "model.J", "S3 mean field point 1"), pv(rows, "model.Delta", "S3 mean field point 1")),
            "p2": (pv(rows, "model.eta_bar", "S3 mean field point 2"), pv(rows, "model.J", "S3 mean field point 2"), pv(rows, "model.Delta", "S3 mean field point 2"))}


def caption(d: dict, rows: list, *, ids, c: dict, FG) -> str:
    n = JC.num
    r2, resid, tolr = d["fit_s4_up_r2"], 100 * d["fit_s4_up_max_resid_frac"], 100 * d["fit_rel_tol"]
    ch = [100 * d[f"k10_rel_change_{t}"] for t in ("8.0", "20.0", "40.0")]
    lim = 100 * d["k10_j_limit"]
    take = (f"The mean field of model M3 (the mean-field model, that is the model's equations for the average activity of the population) does not reproduce the published Hopf point (where the resting state starts to oscillate): it is at the synaptic decay time tau_d {d['hopf_a4_ms']:.2f} ms, not {FG.FS2_K7_PAPER_MS:g} ms (a recorded departure), and the straight-line fit of the squared "
            f"amplitude of v against tau_d leaves a residual of {resid:.2f} percent against {tolr:g} percent allowed (a failed check); it also does not reproduce the published dependence of the oscillation frequency on the coupling J as worded "
            f"(the frequency changes by {ch[0]:.1f}, {ch[1]:.1f} and {ch[2]:.1f} percent at tau_d 8, 20 and 40 ms against a limit of {lim:.0f} percent; the source is a single one and our reading is not verified). "
            f"It reproduces the existence checks (a limit cycle at tau_d 5 ms and a fixed point at 50 ms; the oscillation frequency of the network (a simulated network of N spiking neurons; N = 50,000 here) is within {100 * abs(d['k8_net_rel_diff']):.2f} percent of the mean field, "
            f"tolerance 5 percent), the largest ratio of the heterogeneity Delta to the mean excitability eta_bar on the Hopf curve ({d['k9_ratio'].max():.5f} at eta_bar 1, 2 and 4) and the ratio of the oscillation frequency to the linearised one "
            f"(largest deviation from 1: {d['k11_max_dev']:.5f}).")
    panels = " ".join([
        f"(a) The amplitude of v (maximum minus minimum) of the stable cycle against tau_d ({n(min(d['a5c_up_tau_d'].min(), d['a5c_down_tau_d'].min()))} to {n(max(d['a5c_up_tau_d'].max(), d['a5c_down_tau_d'].max()))} ms, "
        f"up and down sweeps), the Hopf point ({d['hopf_a4_ms']:.4f} ms), the published value {FG.FS2_K7_PAPER_MS:g} ms and the amplitude of the mean-field runs at tau_d 3, 4.95 and 8 ms.",
        f"(b) The squared amplitude of the same cycle against tau_d, axis cut at 6 ms, with the straight-line fit over the window of {d['fit_window_ms'][0]:g} to {d['fit_window_ms'][1]:g} ms above the Hopf point "
        f"(R2 {r2:.5f}, residual {resid:.2f} percent against {tolr:g} percent allowed) and an exploratory fit over {d['fit_posthoc_window_ms'][0]:g} to {d['fit_posthoc_window_ms'][1]:g} ms above it, chosen after the results "
        f"(residual {100 * d['fit_posthoc_near_hopf_max_resid_frac']:.2f} percent); the title is red because the residual of the pre-set fit is above the allowance.",
        "(c) to (g) The firing rate r of the mean-field and network runs over the last 400 ms of each 10 s run at validation point 1 with tau_d 3, 4.95 and 8 ms and at validation point 2 with tau_d 5 and 50 ms; "
        "the network has N = 10,000 neurons in every panel and N = 50,000 as a third line at point 2 with 5 ms; each network run is a single run.",
        "(h) The difference between network and mean field, relative to the mean field, in percent, for the oscillation frequency, the mean of r and the fitted amplitude of r; the cells at 3 ms and 50 ms have no "
        "mean-field oscillation, so their differences are undefined and not drawn; only the frequency has a tolerance (5 percent).",
        f"(i) The largest ratio of Delta to eta_bar on the Hopf curve at eta_bar 1, 2 and 4 (all {d['k9_ratio'].max():.5f} within {d['k9_ratio'].max() - d['k9_ratio'].min():.1e}), against the target band {FG.FS2_K9[0]:g} plus or minus {FG.FS2_K9[1]:g}.",
        f"(j) The ratio of the imaginary part of the linearised eigenvalue to 2 pi times the rate at the fixed point, for 20 Hopf points at Delta 0.0001, against the target band 1 plus or minus {FG.FS2_K11:g}; the largest deviation is "
        f"{d['k11_max_dev']:.5f}; the panel counts the marks that overlap at the drawn size.",
        f"(k) The linearised frequency against tau_d ({n(d['k10_tau_d'].min())} to {n(d['k10_tau_d'].max())} ms) at eta_bar 1 and J {MINUS}20, against the target band {d['k10_band_hz'][0]:g} to {d['k10_band_hz'][1]:g} Hz widened by {100 * d['k10_band_slack']:g} percent.",
        f"(l) The linearised frequency against J ({n(d['k10_J_8.0'].min())} to {n(d['k10_J_8.0'].max())}) at tau_d 8, 20 and 40 ms, with the relative change over the J range ({ch[0]:.1f}, {ch[1]:.1f} and {ch[2]:.1f} percent against a limit of {lim:.0f} percent); the title is red because the dependence is not reproduced as worded; the linearised frequency is not the frequency of the cycle.",
    ])
    settings = ("The classifier (a rule fixed before the analysis that sorts runs into classes) and the spectrogram (power against time and frequency) are not used in this figure.")
    params = (f"Recorded values (the complete list with the key names as recorded is in the supplement): model {c['type']} with membrane time constant {n(c['tau'])} ms; validation point 1: eta_bar {n(c['p1'][0])}, J {n(c['p1'][1]).replace('-', MINUS)}, "
              f"Delta {n(c['p1'][2])}, tau_d 3, 4.95 and 8 ms; validation point 2: eta_bar {n(c['p2'][0])}, J {n(c['p2'][1]).replace('-', MINUS)}, Delta {n(c['p2'][2])}, tau_d 5 and 50 ms; the cycle branch runs over tau_d "
              f"{n(min(d['a5c_up_tau_d'].min(), d['a5c_down_tau_d'].min()))} to {n(max(d['a5c_up_tau_d'].max(), d['a5c_down_tau_d'].max()))} ms; the traces are the last 400 ms of runs of {n(c['hold'])} s; "
              f"networks of N = {n(c['N'])} neurons, and {n(c['N5'])} for the extra run; eta_bar {', '.join(n(x) for x in sorted(set(d['k9_eta_bar'].tolist())))} for (i); J {', '.join(n(x).replace('-', MINUS) for x in d['k10_J_8.0'])} for (l).")
    failed = (f"Two failed or not reproduced results concern this figure and both are drawn. (1) The test of the straight-line fit of the squared amplitude of the cycle against tau_d over the pre-set window: the residual must not exceed {tolr:g} percent; it is {resid:.2f} percent "
              f"(panel (b)). (2) The test of the dependence of the frequency on J: the frequency must change by at most {lim:.0f} percent over the J range; it changes by {ch[0]:.1f}, {ch[1]:.1f} and {ch[2]:.1f} percent "
              f"(panel (l); single source, not verified). " + JC.title_sentence(FS2_ID) + f" The Hopf point at {d['hopf_a4_ms']:.2f} ms against the published {FG.FS2_K7_PAPER_MS:g} ms is a recorded departure, drawn in (a). "
              "No row of the project's table of failed checks concerns this figure (our reading of where the checks apply; not verified); the version of the step test on a network is not part of this figure.")
    limits = JC.limits_paragraph(ids) + " In these limits, control (the same network without the ramp) runs are runs of the project that are not drawn in this figure."
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        JC.key_symbols(rest, "eta", "Delta", "J", "tau_d", "tau", "r", "v", "N", "M3"),
        "Mean field = the model of the average over the neurons; network = a simulation of N spiking neurons; Hopf point = the value of tau_d at which the fixed point turns into an oscillation; stable cycle = the oscillation that remains after the "
        "transient; validation point 1 and 2 = the two parameter sets of the project at which the published results are checked (their values are in Parameters); a failed check = a stated criterion that the result does not meet.",
        JC.key_words(rest)] if x)
    return JC.assemble(FS2_ID, take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)


# ---- supplement data, alt text, build ---------------------------------------------------------------------------------------------------------------

def source_rows(d: dict, FG) -> list:
    rows: list = []
    src = FG._src
    for name in ("up", "down"):
        src(rows, "a", f"stable cycle, amplitude of v, {name} sweep (x = tau_d in ms)", d[f"a5c_{name}_tau_d"], d[f"a5c_{name}_amp"])
        src(rows, "b", f"stable cycle, amplitude squared, {name} sweep (x = tau_d in ms)", d[f"a5c_{name}_tau_d"], d[f"a5c_{name}_amp"] ** 2)
    src(rows, "a", "Hopf point (tau_d in ms)", [d["hopf_a4_ms"]])
    src(rows, "a", "mean-field amplitude of v (x = tau_d in ms)", d["k7_tau"], d["k7_mf_vptp"])
    for k, p in [("mf_ceni_3.0", "c"), ("mf_ceni_4.95", "d"), ("mf_ceni_8.0", "e"), ("mf_devalle_5.0", "f"), ("mf_devalle_50.0", "g")]:
        src(rows, p, f"mean-field r(t) (x = time in ms)", d[f"tr_{k}_t"], d[f"tr_{k}_r"])
    for k, p in [("net_ceni_3ms", "c"), ("net_ceni_4.95ms", "d"), ("net_ceni_8ms", "e"), ("net_devalle_5ms", "f"), ("net_k8_5e4_5ms", "f"), ("net_devalle_50ms", "g")]:
        src(rows, p, f"network r(t), {k} (x = time in ms)", d[f"tr_{k}_t"], d[f"tr_{k}_r"])
    xs = np.arange(len(d["net_cells"]), dtype=float)
    for q in ("f_rel_diff", "r_mean_rel_diff", "r_fit_ptp_rel_diff"):
        ok = np.isfinite(d[f"net_{q}"])
        src(rows, "h", f"{q} in percent (x = cell number)", xs[ok], 100 * d[f"net_{q}"][ok])
    src(rows, "i", "largest Delta/eta_bar (x = eta_bar)", d["k9_eta_bar"], d["k9_ratio"])
    src(rows, "j", "frequency ratio (x = minus J at the Hopf point)", -d["k11_J_H"], d["k11_ratio"])
    src(rows, "k", "linear frequency in Hz (x = tau_d in ms)", d["k10_tau_d"], d["k10_freq"])
    for t in ("8.0", "20.0", "40.0"):
        src(rows, "l", f"linear frequency in Hz at tau_d {t} ms (x = J)", d[f"k10_J_{t}"], d[f"k10_lin_{t}"])
    return rows


def alt_text(d: dict) -> dict:
    ch = [100 * d[f"k10_rel_change_{t}"] for t in ("8.0", "20.0", "40.0")]
    return {
        "a": (f"Amplitude of v of the stable cycle against tau_d from 2.5 to 10.5 ms: it grows from zero at the Hopf point ({d['hopf_a4_ms']:.2f} ms, dotted vertical line) to the right; a second vertical line marks the published value 4.95 ms; "
              "three marks give the mean-field amplitude at 3, 4.95 and 8 ms."),
        "b": (f"Squared amplitude of the cycle against tau_d (axis ends at 6 ms): a nearly straight rise from the Hopf point; two short fitted lines; the legend gives their residuals ({100 * d['fit_s4_up_max_resid_frac']:.2f} percent against "
              f"{100 * d['fit_rel_tol']:g} allowed for the pre-set window); the title is red and reads 'Amplitude squared: FAIL'."),
        "c": "Firing rate over 400 ms at validation point 1, tau_d 3 ms: mean field and network.",
        "d": "Firing rate over 400 ms at validation point 1, tau_d 4.95 ms: mean field and network.",
        "e": "Firing rate over 400 ms at validation point 1, tau_d 8 ms: mean field and network.",
        "f": "Firing rate over 400 ms at validation point 2, tau_d 5 ms: mean field and networks of 10,000 and 50,000 neurons.",
        "g": "Firing rate over 400 ms at validation point 2, tau_d 50 ms: mean field and network.",
        "h": "Six cells on the horizontal axis; three kinds of mark give the relative difference between network and mean field in percent; two dashed lines at plus and minus 5 percent mark the tolerance of the frequency.",
        "i": f"Largest ratio of Delta to eta_bar at eta_bar 1, 2 and 4: the marks lie at {d['k9_ratio'].max():.4f}, inside the shaded target band.",
        "j": f"Twenty marks of the frequency ratio against minus J on a log axis, between the two dashed lines at 0.99 and 1.01; the largest deviation from 1 is {d['k11_max_dev']:.5f}.",
        "k": "Linear frequency against tau_d, a falling curve, between the dashed lines of the target band of 5 to 30 Hz widened by 10 percent.",
        "l": (f"Linear frequency against J at tau_d 8, 20 and 40 ms; the legend gives the relative changes {ch[0]:.1f}, {ch[1]:.1f} and {ch[2]:.1f} percent against a limit of {100 * d['k10_j_limit']:.0f}; the title is red and reads "
              "'Frequency against J: FAIL'."),
    }


def sections(d: dict) -> tuple:
    mapping = ("The journal panels (a) to (l) are the draft panels (a) to (l) (same letters, same data, same size 7.4 x 11.2 in). The draft status block (text under the panels) is not on the image: its lines are in the "
               "'Status block' section of this sheet; the titles of (b) and (l) carry the plain forms 'Amplitude squared: FAIL' and 'Frequency against J: FAIL'.")
    names = ("| plain word in the caption | stored name |\n|---|---|\n| validation point 1 | model.ref_point = ref_ceni: (eta_bar, J, Delta) = (1, -20, 0.05), tau_d in {3, 4.95, 8} ms (plan Table 3.2) |\n"
             "| validation point 2 | model.ref_point = ref_devalle: (eta_bar, J, Delta) = (4, -21, 0.3), tau_d = 5 ms (plan Table 3.2) |\n"
             "| straight-line fit of the squared amplitude | K7 amplitude check (A5 check file; DL-129, DL-130) |\n| dependence of the frequency on J | K10 J dependence (DL-131, DL-132) |\n"
             "| ratio of Delta to eta_bar | K9 (DL-115) |\n| ratio of the frequency to the linearised one | K11 (DL-115) |\n| existence checks | K8 (DL-116, DL-119) |")
    return (("Mapping of the draft panels to the journal panels (DL-651)", mapping), ("Stored names behind the plain words of the caption", names))


def build(FG, res, out_dir, root, script, claim_limit_ids, tag_build) -> dict:
    import dataclasses
    import matplotlib.pyplot as plt
    from .. import provenance as P
    root = Path(root) if root is not None else FG.repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "journal" / FS2_ID
    t = {"start": time.perf_counter()}
    raw = FG.load_FS2(res)
    t["load"] = time.perf_counter()
    d = FG.prepare_FS2(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for panel, key in (("a,b,i-l", "A4"), ("a,b", "A5"), ("k,l", "A6"), ("a,c-e", "S3_mf_ceni"), ("f,g", "S3_mf_devalle"), ("c-e,h", "S3_net_ceni"), ("f,h", "S3_net_devalle"), ("f,h", "S3_net_k8")):
        rec = raw["records"][key]
        for r in FG.make_param_table(rec["config"]):
            rows.append({**r, "panel": panel, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    names = {"A5": "A5", "S3_mf_ceni": "S3 mean field point 1", "S3_mf_devalle": "S3 mean field point 2", "S3_net_ceni": "S3 network ceni", "S3_net_k8": "S3 network K8 (N 50,000)"}
    crows = [{**r, "panel": names[k]} for k in names for r in FG.make_param_table(raw["records"][k]["config"]) if r["key"] in FG.FS2_CAPTION_KEYS]
    cap0 = FG.CAP.build_caption("FS2", take_home=FG.FS2_TAKE_HOME, claim_limit_ids=claim_limit_ids, params_rows=crows, spectrogram=None, symbol_keys=(), notes=FG.fs2_caption_notes(d),
                                main_failures=FG.FS2_MAIN_FAILURES, swept={})
    plain_md = FG.PL.pairing_markdown(claim_limit_ids, None, cap0.text)
    c = consts(d, crows)
    text = caption(d, crows, ids=claim_limit_ids, c=c, FG=FG)
    cap = dataclasses.replace(cap0, text=text)
    cfg = J.load_config(root)
    out.mkdir(parents=True, exist_ok=True)
    stem = "FS2_journal"
    with plt.rc_context(J.rc_params(cfg)):
        fig = draw(d, FG)
        saved = J.save_all(fig, out, stem, cfg)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    drawn = FG.drawn_data_sha256(d)
    P.atomic_write_text(out / f"{stem}_caption.txt", text + "\n")
    P.atomic_write_text(out / f"{stem}_drawn_data_sha256.txt", drawn + "\n")
    warnings = [f"input record {k} ({rec['name']}) was written with git dirty = true" for k, rec in raw["records"].items() if (rec.get("git") or {}).get("dirty")]
    prov_kw = dict(script=script, inputs=[res / p for p in FG.FS2_INPUTS], params_rows=rows,
                   modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py", "src/mprsurge/plotting/jfs2.py", "src/mprsurge/plotting/nordlie.py",
                            "src/mprsurge/plotting/figprov.py"],
                   configs=["configs/A4_grids.yaml", "configs/A5.yaml", "configs/A6.yaml", "configs/S3.yaml", "configs/S3_ceni.yaml", "configs/S3_net_ceni.yaml", "configs/S3_net_devalle.yaml", "configs/S3_net_k8.yaml"],
                   claim_limits=cap.claim_limits, spectrogram=None, tag_build=tag_build, root=root)
    status_text = "\n".join(FG.fs2_status_lines(d))
    return FG._journal_tail(FS2_ID, out, stem, saved, cap, drawn, d, {**raw, "a11": []}, prov_kw, warnings, strip=[], footer=FG.FS2_FOOTER, timing_t=t, source_rows=source_rows(d, FG), alt=alt_text(d),
                            pointers=(), cfg=cfg, status_text=status_text, plain_md=plain_md, extra_sections=sections(d), strip_rows=[], zip_note=False, single_caption=True)
