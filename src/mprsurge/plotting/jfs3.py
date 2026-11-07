"""MS13 13t-6 (DL-651 H1, H2): the journal export of FS3 (finite size, heterogeneity shape and noise) as a stand-alone supplement file at the size of the draft (7.4 x 12.6 in).

Same drawing data as the draft (prepare_FS3); plain words on the image, 8 pt, sentence case; ONE caption (`FS3_journal_caption.txt`, seven labelled paragraphs, no word limit). Every number of the caption is
read from the prepared data or the stored rows; only the wording is typed here.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from . import jcaption as JC
from . import journal as J
from . import style as S

FS3_ID = "FS3"
FS3J_HEIGHT = 12.6
MINUS = chr(0x2212)
UNDEFINED_UNVERIFIED = ("'surge class' and the class names are defined in the Key from the surge definition of the plan; the plain glosses are ours",
                        "'reference run' for the run that the project fixed before the analysis as its main case",
                        "'noise factor' = the multiple of the calibrated noise level sigma used in the noisy runs")
NLAB = {1000: "1000", 3000: "3000", 10000: "10,000", 30000: "30,000"}


def draw(d: dict, FG):
    from matplotlib.patches import Rectangle
    fig, cfg = FG._journal_fig(FS3J_HEIGHT, constrained=True, fid=FS3_ID)
    fig.get_layout_engine().set(w_pad=0.18, h_pad=0.14)
    T = S.figure_colour
    gs = fig.add_gridspec(4, 6, height_ratios=[2.2, 1.7, 2.3, 1.6])
    tol = S.diagram_mark("tol_band")
    pt = S.diagram_mark("fs3_median")
    nl = [NLAB[int(n)] for n in d["N"]]
    # (a)
    ax = fig.add_subplot(gs[0, 0:4])
    xs = np.arange(4, dtype=float)
    h_a = FG._fs3_stack(ax, xs - 0.2, d["s9_count"], d["s9_seeds"][:, None].astype(float), width=0.36)
    FG._fs3_stack(ax, xs + 0.2, d["s9_ctrl_count"], d["s9_ctrl_n"][:, None].astype(float), width=0.36, label_min=0.2)
    for x_, s_, n_, cs, cn in zip(xs, d["s9_surge"], d["s9_seeds"], d["s9_ctrl_surge"], d["s9_ctrl_n"]):
        ax.text(x_ - 0.2, 1.02, f"{int(s_)}/{int(n_)}", ha="center", va="bottom", fontweight="bold")
        ax.text(x_ + 0.2, 1.02, f"{int(cs)}/{int(cn)}", ha="center", va="bottom", fontweight="bold", color=T("range_line"))
    ax.set_xticks(np.concatenate([xs - 0.2, xs + 0.2]), [f"Ramp\nN {n}" for n in nl] + [f"No ramp\nN {n}" for n in nl])
    ax.set_xlim(-0.6, 3.6)
    ax.set_ylim(0.0, 1.3)
    ax.set_ylabel("Share of seeds")
    FG._journal_title(ax, "a", "Class at each N; bold: seeds in a surge class")
    ax.legend(handles=h_a, loc="upper left", ncol=5, frameon=True, framealpha=0.95, handlelength=1.4, columnspacing=0.8)
    # (b)
    axb = fig.add_subplot(gs[0, 4:6])
    for x_, lo, md, hi in zip(xs, d["s9_fpk_err_min"], d["s9_fpk_err_median"], d["s9_fpk_err_max"]):
        axb.plot([x_, x_], [lo, hi], color=T("range_line"), lw=1.0, zorder=2)
        axb.plot([x_], [md], ls="none", marker=pt.marker, ms=pt.size, color=pt.colour, mew=pt.width, zorder=4)
    axb.set_xticks(xs, nl)
    axb.set_xlim(-0.5, 3.5)
    axb.set_ylim(-0.04, 0.46)
    axb.set_xlabel("N (neurons)")
    axb.set_ylabel("Peak frequency error (fraction)")
    FG._journal_title(axb, "b", "Frequency error")
    # (c)
    axc = fig.add_subplot(gs[1, 0:3])
    for x_, lo, md, hi in zip(xs, d["s9_onset_err_min"], d["s9_onset_err_median"], d["s9_onset_err_max"]):
        axc.plot([x_, x_], [lo, hi], color=T("range_line"), lw=1.0, zorder=2)
        axc.plot([x_], [md], ls="none", marker=pt.marker, ms=pt.size, color=pt.colour, mew=pt.width, zorder=4)
    axc.set_xticks(xs, nl)
    axc.set_xlim(-0.5, 3.5)
    axc.set_ylim(0.0, 31.0)
    axc.set_xlabel("N (neurons)")
    axc.set_ylabel("Onset error (s)")
    FG._journal_title(axc, "c", "Onset error against the mean field")
    # (d)
    axd = fig.add_subplot(gs[1, 3:6])
    for i in range(3):
        for j in range(3):
            st = S.get(d["shape_class"][i][j])
            axd.plot([j], [i], ls="none", marker=st.marker, ms=S.POINT_SIZES["fs3_shape"], color=st.colour, mec=T("bar_edge"), mew=S.POINT_EDGE_WIDTH["class"], zorder=4)
            axd.text(j + 0.2, i, d["shape_class"][i][j], va="center")
    nz = [c for c, k in zip(FG.FS3_CLASSES, d["shape_ctrl_counts"]) for _ in range(int(k))]
    for j, c in enumerate(nz):
        st = S.get(c)
        axd.plot([j], [3.0], ls="none", marker=st.marker, ms=S.POINT_SIZES["fs3_shape"], color=st.colour, mec=T("bar_edge"), mew=S.POINT_EDGE_WIDTH["class"], zorder=4)
        axd.text(j + 0.2, 3.0, c, va="center")
    axd.set_yticks(range(4), ["Lorentzian", "Gaussian", "Uniform", "Lorentzian, no ramp\n(all seeds)"])
    axd.set_xticks(range(3), ["Seed 0", "Seed 1", "Seed 2"])
    axd.set_xlim(-0.5, 2.9)
    axd.set_ylim(3.6, -0.5)
    FG._journal_title(axd, "d", "Heterogeneity shape: not evaluable")
    # (e)
    axe = fig.add_subplot(gs[2, 0:4])
    xe = np.arange(12, dtype=float) + np.repeat(np.arange(3), 4) * 0.5
    gate_y = FG.FS3_RB2_KEPT_NEEDED / 10.0
    FG._fs3_stack(axe, xe, d["noise_count"], np.full((12, 1), 10.0), width=0.8, label_min=0.12, avoid=[gate_y if g else None for g in d["noise_gated"]])
    for x_, k, g in zip(xe, d["noise_kept"], d["noise_gated"]):
        axe.text(x_, 1.02, f"{int(k)}", ha="center", va="bottom", fontweight="bold")
        if g:
            axe.text(x_, 1.1, d["gate_status"][0 if x_ < 4 else 1], ha="center", va="bottom", fontweight="bold", color=T("fail_text") if (x_ > 4) else T("text_dark"))
            axe.plot([x_ - 0.4, x_ + 0.4], [gate_y] * 2, color=T("gate_line"), ls=tol.linestyle, lw=tol.width + 0.4, zorder=6, gid="rb2_gate")
    axe.set_xticks(xe, [f"{t:g}\n×{s_:g}" for t, s_ in zip(d["noise_T"], d["noise_sigma"])])
    axe.set_xlabel("Ramp duration T_ramp (s) and noise factor (×)")
    axe.set_ylim(0.0, 1.5)
    axe.set_xlim(-0.6, float(xe[-1]) + 0.6)
    axe.set_ylabel("Share of 10 seeds")
    FG._journal_title(axe, "e", "Noise check: FAIL", fail="FAIL" in d["gate_status"])
    from matplotlib.lines import Line2D
    axe.legend([Line2D([], [], color=T("gate_line"), ls=tol.linestyle, lw=tol.width + 0.4)], ["At least 8 of 10 seeds needed (bars of 120 s)"], loc="upper left", frameon=True, framealpha=0.95)
    # (f)
    axf = fig.add_subplot(gs[2, 4:6])
    xf = np.arange(3, dtype=float)
    FG._fs3_stack(axf, xf, d["noise_ctrl_count"], np.full((3, 1), 10.0), width=0.7, label_min=0.12)
    for x_, k in zip(xf, d["noise_ctrl_kept"]):
        axf.text(x_, 1.02, f"{int(k)}", ha="center", va="bottom", fontweight="bold")
    axf.set_xticks(xf, [f"×{s_:g}" for s_ in FG.FS3_SIGMA])
    axf.set_xlim(-0.6, 2.6)
    axf.set_ylim(0.0, 1.14)
    axf.set_xlabel("Noise factor (×)")
    FG._journal_title(axf, "f", "Controls without a ramp")
    # (g)
    axg = fig.add_subplot(gs[3, 0:2])
    axg.add_patch(Rectangle((-0.3, 0), 0.6, d["subgrid_agree"], fc=T("subgrid_bar"), ec=T("bar_edge"), lw=0.4, zorder=3))
    axg.axhline(d["subgrid_needed"], color=tol.colour, ls=tol.linestyle, lw=tol.width + 0.3, label="Needed: 90 percent", zorder=2)
    axg.text(0.0, d["subgrid_agree"] / 2, f"{d['subgrid_agree']} of {d['subgrid_cells']}", ha="center", va="center",
             bbox=dict(boxstyle="square,pad=0.15", fc=T("label_box"), ec="none", alpha=0.85), zorder=5)
    axg.set_xlim(-0.8, 0.8)
    axg.set_ylim(0, d["subgrid_cells"] * 1.4)
    axg.set_xticks([0], ["Cells that agree"])
    axg.set_ylabel(f"Cells (of {d['subgrid_cells']})")
    FG._journal_title(axg, "g", "90 percent rule: FAILED", fail="FAIL" in d["subgrid_status"])
    axg.legend(loc="upper right", frameon=True, framealpha=0.95)
    # key
    axs = fig.add_subplot(gs[3, 2:6])
    axs.axis("off")
    axs.set_gid("legend axes")
    axs.text(0.0, 1.0, "Panels (a) to (d): network runs, ramp duration 60 s (N = 10,000 in (d), 3 seeds).\n"
             "Panels (e) and (f): mean-field runs with noise, 10 seeds each.\n"
             "A surge class is S+, S-rel or S-abs. Bold numbers: seeds in a surge class.\n"
             "Hatching and colour both mark the classes.", va="top", ha="left")
    J.finish(fig, cfg, FS3_ID)
    return fig


# ---- text ------------------------------------------------------------------------------------------------------------------------------------------

CLASS_DEF = ("A surge (a transient rise of gamma-band power, 25 to 100 Hz) is sorted into classes: S+ (absolute and relative rise, ending), S-rel (relative rise only), S-abs (absolute rise only), "
             "S-sus (a rise that does not end), NS (no rise); D-tr (a rise that ends) and D-none (no episode) are the classes of the noise-free mean field; a surge class is S+, S-rel or S-abs.")


def consts(d: dict, rows: list) -> dict:
    pv = JC.pv
    return {"type": pv(rows, "model.type", "S9"), "T9": pv(rows, "path.T_ramp_s", "S9"), "N10": pv(rows, "network.N", "S10"), "path": pv(rows, "path.name", "S9"), "sigma": pv(rows, "noise.sigma", "S11"),
            "sfac": pv(rows, "noise.sigma_factor", "S11")}


def caption(d: dict, rows: list, a11: list, *, ids, c: dict, FG) -> str:
    n = JC.num
    surge, ctl = d["s9_surge"], d["s9_ctrl_surge"]
    pct = 100.0 * d["subgrid_agree"] / d["subgrid_cells"]
    sh = {s: d["shape_class"][i] for i, s in enumerate(FG.FS3_SHAPES)}
    take = (f"At the reference run (the run that the project fixed before the analysis as its main case) the noise check failed: the surge class is kept in only {d['gate_kept'][1]} of 10 noisy mean-field seeds at the noise level sigma against 8 needed "
            f"(a failed check), and the noisy grid agrees with the noise-free map in {d['subgrid_agree']} of {d['subgrid_cells']} cells ({pct:.1f} percent) against {d['subgrid_needed']} needed (a failed check); "
            f"the effect of the heterogeneity shape cannot be evaluated (the check is NOT EVALUABLE), and the claim holds for Lorentzian heterogeneity only (a claim limit, not a result). " + CLASS_DEF + " "
            f"Finite size (the mean field is D-tr; ramp duration {n(c['T9'])} s, 10 seeds per N; the network is a simulated network of N spiking neurons, the mean field is the model's equations for the average activity of the population): the network gives a surge class in "
            f"{surge[0]}, {surge[1]}, {surge[2]} and {surge[3]} of 10 seeds at N = 1000, 3000, 10,000 and 30,000; the rule that the surge classes are no fewer at 30,000 than at 10,000 passes ({d['nrule_count_3e4']} seeds at 30,000 against "
            f"{d['nrule_count_1e4']} at 10,000), but controls without a ramp also reach surge classes ({ctl[1]} of 3 at 3000, {ctl[2]} of 3 at 10,000 and {ctl[3]} of 3 at 30,000), so the network classes do not separate ramp-driven from non-ramp runs. "
            f"Heterogeneity shape (N = 10,000, 3 seeds): Gaussian and uniform give S-abs in {sh['gaussian'].count('S-abs')} of 3 seeds each and the Lorentzian seeds give {', '.join(sh['lorentzian'])}, so no verdict on shape is drawn and no claim about shape robustness is made. "
            f"Noise (ramp duration 120 s, 10 seeds): the surge class is kept in {d['gate_kept'][0]} of 10 seeds at 0.5 sigma (passes) and {d['gate_kept'][1]} of 10 at sigma (a failed check), and controls with constant parameters reach "
            f"{d['noise_ctrl_kept'][0]} of 10 at every sigma.")
    panels = " ".join([
        f"(a) For each N (1000, 3000, 10,000 and 30,000 neurons), the share of the 10 ramp seeds in each class (left bar) and of the 3 control seeds without a ramp (right bar); the bold number above a bar is the number of seeds in a surge class; ramp duration {n(c['T9'])} s.",
        f"(b) The error of the peak frequency of the network (the peak of the power spectrum of its mean potential v) relative to the mean field, per N: the line is the range and the mark the median ({', '.join(str(int(x)) for x in d['s9_fpk_err_n'])} seeds with a defined value).",
        "(c) The absolute error of the onset time of the network (when the classifier, a rule fixed before the analysis that sorts runs into classes, first flags the rise) against the mean field, per N: range and median.",
        f"(d) The class of each of 3 seeds for Lorentzian, Gaussian and uniform heterogeneity at N = {c['N10']:,}, and the classes of the {int(d['shape_ctrl_n'])} control runs without a ramp with Lorentzian heterogeneity; the title is not red because the check is not evaluable, not failed.",
        "(e) The share of 10 noisy mean-field seeds in each class for ramp durations of 10, 30, 120 and 300 s and the noise factors 0.5, 1 and 2 (multiples of the calibrated noise level sigma); the number above a bar is the number of seeds in a surge class; for the 120 s bars "
        f"the words PASS or FAIL and the dashed line (8 of 10 seeds needed) show the check; the title is red because it fails at the noise factor 1.",
        f"(f) The share of 10 constant-parameter control seeds (no ramp) in each class for the three noise factors; the number above a bar is the number of seeds in a surge class ({', '.join(str(int(x)) for x in d['noise_ctrl_kept'])}).",
        f"(g) The number of cells of the noisy grid ({d['subgrid_cells']} cells) whose class agrees with the noise-free class ({d['subgrid_agree']}) against the 90 percent needed ({d['subgrid_needed']}); the title is red because the rule failed.",
    ])
    settings = ("The classifier (a rule fixed before the analysis that sorts runs into classes) and its settings are those of the project's frozen criteria; the spectrogram (power against time and frequency) is not drawn in this figure; "
                "the values are not repeated here because no panel draws a classifier run.")
    params = (f"Recorded values (the complete list with the key names as recorded is in the supplement): model {c['type']}; path P2 (the hypoxia-like path, mean excitability raised) with ramp duration {n(c['T9'])} s in (a) to (d); N = 1000, 3000, 10,000 and 30,000 in (a) to (c) and "
              f"{c['N10']:,} in (d) to (f); the noise level sigma = {n(c['sigma'])} in (e) and (f), with the noise factors 0.5, 1 and 2 and the ramp durations 10, 30, 120 and 300 s in (e).")
    rows_ = FG.strip_rows_of(FS3_ID, d)
    lines = [JC.failed_line(r) for r in rows_]
    failed = (f"Failed checks that concern this figure ({len(lines)}): " + "; ".join(lines) + ". The checks against the mean field at the ramp durations 10 s and 120 s and at the 4 map cells are not drawn here (their runs are not in this figure; (a) draws the network at 60 s); "
              "the title of (e) is red as 'Noise check: FAIL' and the title of (g) as '90 percent rule: FAILED'. The heterogeneity check is NOT EVALUABLE (panel (d)). "
              "The project's other failed checks are not about this figure; all of them are listed in the supplement. " + JC.title_sentence(FS3_ID))
    limits = JC.limits_paragraph(ids) + " In these limits, control (the same network without the ramp) runs are runs without a ramp: the controls of (a) and (d), and the constant-parameter controls of (f) are mean-field runs."
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        JC.key_symbols(rest, "eta", "Delta", "J", "tau_d", "r", "v", "N", "T_ramp", "M3", "modes"),
        "Mean field = the model of the average over the neurons; network = a simulation of N spiking neurons; noise level sigma = the amplitude of the additive white noise on v in the noisy mean-field runs; the noise factor multiplies it; "
        "a seed = one random realisation; a control = a run without the ramp; a failed check = a stated criterion that the result does not meet.",
        JC.key_words(rest)] if x)
    return JC.assemble(FS3_ID, take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)


# ---- supplement data, alt text, build ---------------------------------------------------------------------------------------------------------------

def source_rows(d: dict, FG) -> list:
    rows: list = []
    src = FG._src
    cls = FG.FS3_CLASSES
    for i, n in enumerate(d["N"]):
        for k, cn in enumerate(cls):
            src(rows, "a", f"ramp seeds in class {cn} (x = N)", [n], [d["s9_count"][i][k]])
            src(rows, "a", f"control seeds without a ramp in class {cn} (x = N)", [n], [d["s9_ctrl_count"][i][k]])
        src(rows, "b", "peak frequency error: minimum, median, maximum (x = N)", [n] * 3, [d["s9_fpk_err_min"][i], d["s9_fpk_err_median"][i], d["s9_fpk_err_max"][i]])
        src(rows, "c", "onset error in s: minimum, median, maximum (x = N)", [n] * 3, [d["s9_onset_err_min"][i], d["s9_onset_err_median"][i], d["s9_onset_err_max"][i]])
    for i, sh in enumerate(FG.FS3_SHAPES):
        for j, cl in enumerate(d["shape_class"][i]):
            src(rows, "d", f"{sh} heterogeneity, class of seed {j}: {cl} (x = seed, y = shape row)", [j], [i])
    for k, cn in enumerate(cls):
        src(rows, "d", f"Lorentzian controls without a ramp in class {cn}", [0], [d["shape_ctrl_counts"][k]])
    for i in range(len(d["noise_T"])):
        for k, cn in enumerate(cls):
            src(rows, "e", f"seeds in class {cn} (x = ramp duration in s, y = noise factor)", [d["noise_T"][i]], [d["noise_sigma"][i]], [d["noise_count"][i][k]])
    for i, s_ in enumerate(FG.FS3_SIGMA):
        for k, cn in enumerate(cls):
            src(rows, "f", f"control seeds in class {cn} (x = noise factor)", [s_], [d["noise_ctrl_count"][i][k]])
    src(rows, "g", "cells that agree, cells, cells needed", [0, 1, 2], [d["subgrid_agree"], d["subgrid_cells"], d["subgrid_needed"]])
    return rows


def alt_text(d: dict) -> dict:
    return {
        "a": f"Stacked bars of the share of seeds in each class at four network sizes, ramp seeds left and no-ramp control seeds right; the numbers above the bars count surge-class seeds: {', '.join(str(int(x)) for x in d['s9_surge'])} of 10 for the ramp seeds.",
        "b": "Range and median of the relative error of the peak frequency of the network against the mean field at the four network sizes.",
        "c": "Range and median of the onset error in seconds at the four network sizes.",
        "d": "A grid of class marks: three seeds each for Lorentzian, Gaussian and uniform heterogeneity, and the classes of the Lorentzian controls without a ramp; the title says the check is not evaluable.",
        "e": f"Stacked bars of the classes of 10 noisy seeds for four ramp durations and three noise factors; a dashed line marks 8 of 10 on the 120 s bars; above them PASS at 0.5 and FAIL at 1 ({int(d['gate_kept'][0])} and {int(d['gate_kept'][1])} of 10 seeds); the title is red and reads 'Noise check: FAIL'.",
        "f": "Stacked bars of the classes of 10 constant-parameter control seeds at three noise factors.",
        "g": f"One bar of {d['subgrid_agree']} cells that agree out of {d['subgrid_cells']}, below a dashed line at {d['subgrid_needed']} cells needed; the title is red and reads '90 percent rule: FAILED'.",
    }


def sections(d: dict) -> tuple:
    mapping = ("The journal panels (a) to (g) are the draft panels (a) to (g) (same letters, same data, same size 7.4 x 12.6 in). The draft status block (text under the panels) is not on the image: its lines are in the "
               "'Status block' section of this sheet and in the strip section; the titles of (e) and (g) carry the plain forms 'Noise check: FAIL' and '90 percent rule: FAILED'.")
    names = ("| plain word in the caption | stored name |\n|---|---|\n| finite size | S9 (N sweep; ramp seeds and no-ramp controls) |\n| heterogeneity shape | S10 (per-seed table; RB8 NOT EVALUABLE) |\n"
             "| noise | S11 (RB2 gate, beside rows and controls) |\n| noise check | RB2 headline_class_kept_1.0_sigma (at least 8 of 10 seeds keep the headline class) |\n| 90 percent rule | D24 / RB2 noisy_subgrid_agreement |\n"
             "| network against mean field | RB1 headline_10s, headline_120s, cells_30s, overall |")
    return (("Mapping of the draft panels to the journal panels (DL-651)", mapping), ("Stored names behind the plain words of the caption", names))


def build(FG, res, out_dir, root, script, claim_limit_ids, tag_build) -> dict:
    import dataclasses
    import matplotlib.pyplot as plt
    from .. import provenance as P
    root = Path(root) if root is not None else FG.repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "journal" / FS3_ID
    t = {"start": time.perf_counter()}
    raw = FG.load_FS3(res)
    t["load"] = time.perf_counter()
    d = FG.prepare_FS3(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for key, rec in raw["records"].items():
        for r in FG.make_param_table(rec["config"]):
            rows.append({**r, "panel": key, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    crows = [r for r in rows if r["key"] in FG.FS3_CAPTION_KEYS and not (r["key"] in ("noise.sigma", "noise.sigma_factor") and r["panel"] != "S11")]
    crit, _ = FG.F.K.load_frozen_criteria(root)
    cap0 = FG.CAP.build_caption("FS3", take_home=FG.FS3_TAKE_HOME, claim_limit_ids=claim_limit_ids, params_rows=crows, spectrogram=None, symbol_keys=(), notes=FG.fs3_caption_notes(d),
                                limit_labels=FG.CLAIM_LIMIT_LABELS, class_key=FG.CAP.class_key_line("ND", agree=True), classifier_line=FG.CAP.classifier_line(crit),
                                main_failures=FG.FS3_MAIN_FAILURES, swept={})
    plain_md = FG.PL.pairing_markdown(claim_limit_ids, None, cap0.text)
    c = consts(d, crows)
    text = caption(d, crows, raw["a11"], ids=claim_limit_ids, c=c, FG=FG)
    cap = dataclasses.replace(cap0, text=text)
    cfg = J.load_config(root)
    out.mkdir(parents=True, exist_ok=True)
    stem = "FS3_journal"
    with plt.rc_context(J.rc_params(cfg)):
        fig = draw(d, FG)
        saved = J.save_all(fig, out, stem, cfg)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    drawn = FG.drawn_data_sha256(d)
    P.atomic_write_text(out / f"{stem}_caption.txt", text + "\n")
    P.atomic_write_text(out / f"{stem}_drawn_data_sha256.txt", drawn + "\n")
    warnings = [f"input record {k} ({rec['name']}) was written with git dirty = true" for k, rec in raw["records"].items() if (rec.get("git") or {}).get("dirty")]
    prov_kw = dict(script=script, inputs=[res / p for p in FG.FS3_INPUTS], params_rows=rows,
                   modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py", "src/mprsurge/plotting/jfs3.py", "src/mprsurge/plotting/nordlie.py",
                            "src/mprsurge/plotting/figprov.py"],
                   configs=["configs/base.yaml", "configs/ms10/ms10_net.yaml", "configs/ms11/ms11_mfn.yaml"], claim_limits=cap.claim_limits, spectrogram=None, tag_build=tag_build, root=root)
    status_text = "\n".join(FG.fs3_strip_lines(d))
    return FG._journal_tail(FS3_ID, out, stem, saved, cap, drawn, d, raw, prov_kw, warnings, strip=[], footer=FG.FS3_FOOTER, timing_t=t, source_rows=source_rows(d, FG), alt=alt_text(d),
                            pointers=(), cfg=cfg, status_text=status_text, plain_md=plain_md, extra_sections=sections(d), strip_rows=None, zip_note=False, single_caption=True)
