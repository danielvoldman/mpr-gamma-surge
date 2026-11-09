"""MS13 13t-9 (DL-681 N4, DL-651 H1, H2): the journal export of FS4 (numerical checks: solver, tolerance, initial perturbation, noise floor, network time step and peak value V_p) as a stand-alone
supplement file at the width of the draft (7.4 in; height 14.4 in, the limit of the FS profile, because the panels are placed in inches).

Same drawing data as the draft (prepare_FS4); plain words on the image, 8 pt, sentence case; the status block of the draft is not on the image (its lines are in the caption and the supplement). ONE caption
(`FS4_journal_caption.txt`, seven labelled paragraphs, no word limit). Every number of the caption is read from the prepared data, the stored A11 rows, the stored A7 table or the recorded parameter rows (N2);
only the wording is typed here. Terms that no plan or Key defines in plain words are listed in UNDEFINED_UNVERIFIED.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from . import jcaption as JC
from . import journal as J
from . import style as S

FS4_ID = "FS4"
FS4J_HEIGHT = 14.4
MINUS = chr(0x2212)
PM = chr(0xb1)
UNDEFINED_UNVERIFIED = ("'classifier onset' and 'raw first crossing' are the two onset readings of the plan; the plain glosses are ours",
                        "'noise floor' for the very small added noise of the project's floored runs (our wording)",
                        "'step halving' for the halving of the network time step (our wording)",
                        "'spectrum-maximum reading' for the PSD-argmax reading of the network peak frequency (our wording)")


def draw(d: dict, FG):
    """FS4 journal drawing (own plain text; the draft's panels and data, placed in inches because the constrained layout cannot place them at 8 pt; width 7.4 in as the draft)."""
    fig, cfg = FG._journal_fig(FS4J_HEIGHT, constrained=False, fid=FS4_ID)
    T = S.figure_colour
    tol = S.diagram_mark("tol_band")
    fcl = S.diagram_mark("fs4_cross")
    edge = T("bar_edge")
    ax_in = FG._ax_in
    # (a)
    ax = ax_in(fig, 1.7, 0.45, 3.0, 2.15)
    n = len(d["head_label"])
    for i in range(n):
        st = S.get(d["head_class"][i])
        ax.plot([d["head_onset_s"][i]], [i], ls="none", marker=st.marker, ms=S.FS_SIZES["fs4_class"], color=st.colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], zorder=4,
                label=f"{d['head_class'][i]} (classifier onset)" if i == 0 else None)
        ax.plot([d["head_onset_cross_s"][i]], [i], ls="none", marker=fcl.marker, ms=fcl.size, color=fcl.colour, mew=fcl.width, zorder=5, label="Raw first crossing" if i == 0 else None)
    ax.set_yticks(range(n), [plain_head_label(x) for x in d["head_label"]])
    ax.set_ylim(n - 0.5, -0.5)
    ax.set_xlim(58.65, 58.93)
    ax.set_xlabel("Onset (s)")
    FG._journal_title(ax, "a", "Onset by setting; solver check: FAIL", fail=d["head_radau_minus_default_ms"] > FG.FS4_RB6_SOLVER_BOUND_MS)
    ax.text(0.98, 0.40, f"Solver check: FAIL\nRadau {MINUS} default = {d['head_radau_minus_default_ms']:g} ms\nagainst the {FG.FS4_RB6_SOLVER_BOUND_MS:g} ms allowed", transform=ax.transAxes, ha="right", va="center",
            color=T("fail_text"), bbox=dict(boxstyle="square,pad=0.25", fc=S.FS_COLOURS["box_face"], ec=T("fail_text"), lw=0.5))
    ax.legend(loc="upper right", frameon=True, framealpha=0.95)
    # (b)
    axb = ax_in(fig, 5.6, 0.45, 1.6, 2.15)
    for j in range(4):
        for i in range(2):
            st = S.get(d["ms11_class"][i][j])
            axb.plot([j], [i], ls="none", marker=st.marker, ms=S.FS_SIZES["fs4_class_b"], color=st.colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], zorder=4)
            axb.text(j, i + 0.32, f"{d['ms11_onset_shift_s'][i, j]:g} s", ha="center", va="center")
    axb.set_xticks(range(4), [plain_ms11_label(x).replace("\n", " ") for x in d["ms11_col_label"]], rotation=45, ha="right")
    axb.set_yticks(range(2), [f"{t:g} s" for t in d["ms11_T"]])
    axb.set_ylabel("Ramp duration")
    axb.set_ylim(1.6, -0.5)
    axb.set_xlim(-0.6, 3.6)
    FG._journal_title(axb, "b", "Class, onset shift")
    # (c), (d)
    for col, (q, ttl, letter, left) in enumerate((("cross", "Noise floor, raw first crossing", "c", 0.95), ("class", "Noise floor, classifier onset", "d", 4.45))):
        axc = ax_in(fig, left, 3.4, 2.7, 2.15)
        for L in (0, 1, 2):
            mk = S.diagram_mark(f"fs4_l{L}")
            arr = d[f"floor_l{L}_{q}_delay"]
            for i, dt in enumerate(d["floor_dt"]):
                axc.plot([dt] * arr.shape[1], arr[i], ls="none", marker=mk.marker, ms=mk.size, color=mk.colour, mew=mk.width, zorder=3, label=f"Level {L}" if i == 0 else None)
        axc.set_xscale("log")
        axc.set_xlabel("Heun step (tau)")
        axc.set_ylabel("Delay of the onset" if col == 0 else "")
        FG._journal_title(axc, letter, ttl)
        axc.set_ylim((-0.125, 0.065) if q == "cross" else (-1.64, -0.52))
        if q == "class":
            axc.text(0.5, 0.2, f"{MINUS}1.5: onset at the ramp start", transform=axc.transAxes, ha="center", va="bottom").set_gid("d2_note")
        axc.legend(loc="upper center", ncol=3, frameon=True, framealpha=0.95, handletextpad=0.2, columnspacing=0.6, handlelength=1.0)
    # (e)
    axd = ax_in(fig, 0.95, 6.35, 2.7, 2.15)
    for i, T_ in enumerate(d["ms11_T"]):
        mk = S.diagram_mark(f"w_{i}")
        axd.plot([0, 1, 2], d["floorT_median"][i], ls="-" if i == 0 else "--", lw=0.8, marker=mk.marker, ms=S.FS_SIZES["fs4_floor_T"], color=mk.colour,
                 mfc=mk.colour if mk.filled else "none", mew=mk.width, zorder=3, label=f"{T_:g} s: {FG.FS4_D3_WORDS.get(d['floorT_direction'][i], d['floorT_direction'][i])}")
    axd.set_xticks([0, 1, 2], ["Level 0", "Level 1", "Level 2"])
    axd.set_xlim(-0.4, 2.4)
    axd.set_ylim(-2.1, -0.4)
    axd.set_ylabel("Median delay")
    FG._journal_title(axd, "e", "Noise floor at 10 s and 316 s")
    axd.legend(loc="lower center", frameon=True, framealpha=0.95, title="Ramp duration")
    lo_, hi_ = int(d["floorT_raw_noonset_seeds"].min()), int(d["floorT_raw_noonset_seeds"].max())
    axd.text(0.5, 0.97, "Raw crossing: no onset in " + (f"{lo_}" if lo_ == hi_ else f"{lo_} to {hi_}") + " of 10 seeds", transform=axd.transAxes, ha="center", va="top")
    # (f)
    axe = ax_in(fig, 4.45, 6.35, 2.75, 2.15)
    psd = S.diagram_mark("fs4_psd")
    for s_ in range(3):
        mk = S.diagram_mark(f"fs4_s{s_}")
        axe.plot(d["net_dt"], d["net_f_pk_hz"][s_], color=mk.colour, ls=mk.linestyle, lw=0.8, marker=mk.marker, ms=mk.size, mew=mk.width, zorder=3, label=f"Seed {s_}")
        axe.plot(d["net_dt"][:2], d["net_psd_f_pk_hz"][s_], ls="none", marker=psd.marker, ms=psd.size, color=mk.colour, mew=psd.width, zorder=4, label="Open: spectrum maximum" if s_ == 0 else None)
    axe.set_xscale("log")
    axe.invert_xaxis()
    axe.set_xlabel("Network time step (tau)")
    axe.set_ylabel("Peak frequency (Hz)")
    FG._journal_title(axe, "f", "Network peak frequency: FAIL", fail="FAIL" in d["net_status"])
    axe.set_ylim(40.0, 135.0)
    axe.legend(loc="upper center", ncol=2, frameon=True, framealpha=0.95, handletextpad=0.3, columnspacing=1.0)
    # (g)
    axf = ax_in(fig, 0.95, 9.15, 2.7, 2.15)
    for s_ in range(3):
        mk = S.diagram_mark(f"fs4_s{s_}")
        axf.plot([0, 1, 2], d["net_rel_change"][s_], ls="none", marker=mk.marker, ms=mk.size, color=mk.colour, mew=mk.width, zorder=3, label=f"Seed {s_}")
    axf.axhline(FG.FS4_RB6_FPK_BOUND, color=tol.colour, ls=tol.linestyle, lw=tol.width + 0.3, label=f"Allowed {FG.FS4_RB6_FPK_BOUND:g}", zorder=2)
    axf.set_xticks([0, 1, 2], ["1e-3 to\n5e-4", "5e-4 to\n2.5e-4", "2.5e-4 to\n1e-4"])
    axf.set_xlabel("Halving of the network time step")
    axf.set_xlim(-0.5, 2.5)
    axf.set_ylim(-0.03, 0.78)
    axf.set_ylabel("Relative change")
    FG._journal_title(axf, "g", "Change per step halving: FAIL", fail=bool((d["net_rel_change"] > FG.FS4_RB6_FPK_BOUND).any()))
    axf.legend(loc="upper right", frameon=True, framealpha=0.95, labelspacing=0.5)
    # (h)
    axg = ax_in(fig, 5.05, 9.15, 2.15, 2.15)
    for i, row in enumerate(d["netcls_class"]):
        for s_, c in enumerate(row):
            st = S.get(c)
            axg.plot([s_], [i], ls="none", marker=st.marker, ms=S.FS_SIZES["fs4_class"], color=st.colour, mec=edge, mew=S.POINT_EDGE_WIDTH["class"], zorder=4)
            axg.text(s_ + 0.16, i, c, va="center")
    axg.set_yticks(range(len(d["netcls_row"])), [r.replace("dt", "step") for r in d["netcls_row"]])
    axg.set_xticks(range(3), ["Seed 0", "Seed 1", "Seed 2"])
    axg.set_xlim(-0.35, 2.95)
    axg.set_ylim(len(d["netcls_row"]) - 0.6, -0.4)
    FG._journal_title(axg, "h", "Class by step and V_p")
    # (i)
    axh = ax_in(fig, 0.95, 11.95, 3.6, 1.85)
    v1, v2 = S.diagram_mark("fs4_vp100"), S.diagram_mark("fs4_vp200")
    xx = np.arange(len(d["vp_seed"]), dtype=float)
    axh.plot(xx, d["vp_f100_hz"], ls="none", marker=v1.marker, ms=v1.size, color=v1.colour, zorder=3, label="V_p " + PM + "100")
    axh.plot(xx, d["vp_f200_hz"], ls="none", marker=v2.marker, ms=v2.size, color=v2.colour, mew=v2.width, zorder=4, label="V_p " + PM + "200")
    axh.set_xticks(xx, [f"{dt:g}\nseed {int(s)}" for dt, s in zip(d["vp_dt"], d["vp_seed"])])
    axh.set_xlabel("Network time step (tau) and seed")
    axh.set_ylim(40.0, 118.0)
    axh.set_xlim(-0.5, len(xx) - 0.5)
    axh.set_ylabel("Peak frequency (Hz)")
    FG._journal_title(axh, "i", "V_p " + PM + "100 against " + PM + "200")
    axh.legend(loc="upper left", frameon=True, framealpha=0.95)
    J.finish(fig, cfg, FS4_ID)
    return fig


# ---- plain labels of the image from the labels of the draft data (one source of the numbers) ----------------------------------------------------------------------------------------

def plain_head_label(lab: str) -> str:
    """'default: delta0 1e-6, rtol 1e-10' -> 'Default (perturbation 1e-6, tolerance 1e-10)'; 'delta0 1e-9' -> 'Perturbation 1e-9'; 'rtol 1e-8' -> 'Tolerance 1e-8'; 'Radau, rtol 1e-10' -> 'Radau solver, tolerance 1e-10'."""
    import re
    m = re.fullmatch(r"default: delta0 (\S+), rtol (\S+)", lab)
    if m:
        return "Default"
    m = re.fullmatch(r"delta0 (\S+)", lab)
    if m:
        return f"Perturbation {m.group(1)}"
    m = re.fullmatch(r"rtol (\S+)", lab)
    if m:
        return f"Tolerance {m.group(1)}"
    m = re.fullmatch(r"Radau, rtol (\S+)", lab)
    if m:
        return "Radau solver"
    raise JC.JCaptionError(f"FS4: the setting label {lab!r} of the draft data has no plain form")


def plain_ms11_label(lab: str) -> str:
    kind, val = lab.split()
    return ("Perturbation" if kind == "delta0" else "Tolerance") + "\n" + JC.num(float(val))


# ---- text -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def consts(d: dict, rows: list, raw: dict) -> dict:
    pv = JC.pv
    a7 = raw["a7"]
    base = a7[a7["family"] == "S5ramp"]
    if len(base) != 1:
        raise JC.JCaptionError(f"FS4: the stored A7 table has {len(base)} default rows, not 1")
    rad = a7[a7["family"] == "radau"]
    d0 = sorted(float(x) for x in a7.loc[a7["family"] == "delta0", "delta0"])
    rt = sorted(float(x) for x in a7.loc[a7["family"] == "rtol", "rtol"])
    ce = d["net_rel_change"][:, 0]
    return {"type": pv(rows, "model.type", "S13_MS8_delta0"), "ref": pv(rows, "model.ref_point", "S13_MS8_delta0"), "T_main": float(base["T_ramp_s"].iloc[0]), "T_net": pv(rows, "path.T_ramp_s", "S13_MS11_network"),
            "N": int(pv(rows, "network.N", "S13_MS11_network")), "Vp": float(pv(rows, "network.V_peak", "S13_MS11_network")), "d0_default": float(base["delta0"].iloc[0]), "rtol_default": float(base["rtol"].iloc[0]),
            "d0": d0, "rtol": rt, "radau_rtol": float(rad["rtol"].iloc[0]), "n_seeds": int(d["net_f_pk_hz"].shape[0]), "n_floor_seeds": int(d["floor_l0_cross_delay"].shape[1]),
            "rel_lo": int(round(100 * float(ce.min()))), "rel_hi": int(round(100 * float(ce.max()))), "onset_default": float(d["head_onset_cross_s"][0]), "onset_radau": float(d["head_onset_cross_s"][-1]),
            "shift_max": float(np.max(np.abs(d["ms11_onset_shift_s"]))), "n_ms11": int(len(d["ms11_class"]) * len(d["ms11_class"][0])), "tie": float(np.min(d["floor_l0_class_delay"])),
            "tie_levels": [L for L in range(3) if np.allclose(d[f"floor_l{L}_class_delay"], np.min(d["floor_l0_class_delay"]))], "ok_rows": int(sum(1 for c in d["head_class"] if c == "D-tr")),
            "n_rows": len(d["head_class"]), "ms11_T": [float(x) for x in d["ms11_T"]]}


def _and(xs) -> str:
    xs = [JC.num(x) for x in xs]
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def caption(d: dict, rows: list, crit: dict, *, ids, c: dict, FG) -> str:
    n = JC.num
    ms = d["head_radau_minus_default_ms"]
    bound = FG.FS4_RB6_SOLVER_BOUND_MS
    fb = 100 * FG.FS4_RB6_FPK_BOUND
    if c["ok_rows"] != c["n_rows"] or any(cl != "D-tr" for row in d["ms11_class"] for cl in row):
        raise JC.JCaptionError("FS4: a setting does not give the class D-tr (the take-home wording needs it)")
    if c["tie"] != -1.5 or c["tie_levels"] != [0, 1]:
        raise JC.JCaptionError(f"FS4: the classifier-onset delays at the minimum are {c['tie']} at levels {c['tie_levels']}, not -1.5 at 0 and 1")
    take = (f"The numerical checks of the main example (the run that the project fixed before the analysis as its main case: path P2, the hypoxia-like path, at the second validation point, ramp duration {n(c['T_main'])} s, no noise) "
            f"failed in two places: the default solver and the Radau solver (a second solver for the model's differential equations) give the onset {n(c['onset_default'])} s and {n(c['onset_radau'])} s, {ms:.0f} ms apart against {bound:g} ms allowed "
            f"(a failed check, the cause is not known), and the peak frequency of the network (a simulated network of {c['N']:,} spiking neurons, {c['n_seeds']} seeds, ramp duration {n(c['T_net'])} s) changes by {c['rel_lo']} to {c['rel_hi']} percent when the "
            f"time step is halved, against {fb:g} percent allowed ({d['net_ce_n_pass']} of {c['n_seeds']} seeds pass; the spectrum-maximum reading of the peak frequency passes in {d['net_psd_n_pass']} of {c['n_seeds']} seeds; a failed check). "
            f"Results that rest on the network peak frequency are shown labelled FAIL and are not used as evidence. The class of the main example is D-tr (a rise that ends) under every setting of the initial perturbation, the relative tolerance and the solver, "
            f"and the onset is {n(c['onset_default'])} s everywhere except under Radau; the delays of the noise-floor runs do not depend on the Heun time step at the 1 ms output grid.")
    panels = " ".join([
        f"(a) The onset of the main example for {c['n_rows']} settings (rows): the default, the initial perturbations {_and(c['d0'])}, the relative tolerances {_and(c['rtol'])} and the Radau solver. The class mark is the classifier onset "
        f"(the first window that the classifier, a rule fixed before the analysis, flags); the small cross is the raw first crossing (the envelope of v at a detection threshold); the two onsets are equal in every run, so the cross lies on the mark. "
        f"The red title and the red note give the solver check: Radau minus default = {ms:g} ms against the {bound:g} ms allowed.",
        f"(b) The class and the onset shift (s) at the ramp durations {_and(c['ms11_T'])} s for the initial perturbations {_and(c['d0'])} and the relative tolerances {_and(c['rtol'])} (the default values are those of (a)): D-tr in all {c['n_ms11']} cells; "
        f"the largest shift is {n(c['shift_max'])} s.",
        f"(c) and (d) The delay (eta_bar at the onset minus eta_bar at the Hopf point) of every run of the noise floor (a very small added noise at three levels, 0, 1 and 2, {c['n_floor_seeds']} seeds each, integrated with the Heun scheme at "
        f"{len(d['floor_dt'])} time steps {_and(sorted(d['floor_dt'], reverse=True))} tau) at the main example, under the raw first crossing (c) and under the classifier onset (d); the delay is the same at every step at the 1 ms output grid, "
        f"so the points of one level lie on one another. In (d) the delays {MINUS}{abs(c['tie']):g} at levels {c['tie_levels'][0]} and {c['tie_levels'][1]} are onsets at the ramp start (the classifier-onset reading is saturated); no gate verdict changes.",
        f"(e) The median delay at the noise floor under the classifier onset at the ramp durations {_and(c['ms11_T'])} s, by level (reported only); the direction of the change with the level is called \"not strictly monotone\" at both durations "
        f"(the medians at {n(c['ms11_T'][1])} s are {MINUS}{abs(d['floorT_median'][1][0]):.4g}, {MINUS}{abs(d['floorT_median'][1][1]):.4g} and {MINUS}{abs(d['floorT_median'][1][2]):.4g}); under the raw first crossing "
        f"{int(d['floorT_raw_noonset_seeds'].min())} to {int(d['floorT_raw_noonset_seeds'].max())} of {c['n_floor_seeds']} seeds have no onset.",
        f"(f) The peak frequency (the peak of the power spectrum) of the {c['n_seeds']} network seeds against the network time step {_and(sorted(d['net_dt'], reverse=True))} tau; open marks: the spectrum-maximum reading of the first halving.",
        f"(g) The relative change of the peak frequency per halving of the time step against the bound {FG.FS4_RB6_FPK_BOUND:g} (a change of {n(FG.FS4_RB6_FPK_BOUND)} is {fb:g} percent); the largest change, at the first halving, is {c['rel_hi']} percent.",
        f"(h) The class of the network for each time step and each peak value V_p ({n(c['Vp'])} and 200), seeds 0 to {c['n_seeds'] - 1}; information only, one seed per cell, not evidence of a ramp-driven surge.",
        f"(i) The peak frequency of each seed at V_p {PM}{n(c['Vp'])} against {PM}200 (reported only).",
    ])
    settings = JC.settings_line(crit)
    params = (f"Recorded values (the complete list with the key names as recorded is in the supplement): model {c['type']} (the mean-field model of the project) at the second validation point (eta_bar {n(JC.pv(rows, 'model.eta_bar'))}, "
              f"J {n(JC.pv(rows, 'model.J')).replace('-', MINUS)}, Delta {n(JC.pv(rows, 'model.Delta'))}, tau_d {n(JC.pv(rows, 'model.tau_d_ms'))} ms); default initial perturbation {n(c['d0_default'])} and relative tolerance {n(c['rtol_default'])}; "
              f"initial perturbations {_and(sorted(c['d0'] + [c['d0_default']]))} and relative tolerances {_and(sorted(c['rtol'] + [c['rtol_default']]))} in (a) and (b); the ramp duration is {n(c['T_main'])} s in (a), (c) and (d), "
              f"{_and(c['ms11_T'])} s in (b) and (e) and {n(c['T_net'])} s in (f) to (i); noise: the {JC.pv(rows, 'noise.scheme')} scheme with the time steps of (c) and (d); network of N = {c['N']:,} neurons with {c['n_seeds']} seeds, peak value V_p = {n(c['Vp'])} "
              f"(the reset value is {MINUS}{n(c['Vp'])}) and the check value 200.")
    lines = [JC.failed_line(r) for r in d["strip"]]
    failed = (f"Failed checks that concern this figure ({len(lines)}): " + "; ".join(lines) + f". The network row has no value in the stored table; the recorded evaluation gives {d['net_ce_n_pass']} of {c['n_seeds']} seeds passing under the "
              f"classifier-episode reading and {d['net_psd_n_pass']} of {c['n_seeds']} under the spectrum-maximum reading (the check fails if any seed that can be evaluated fails). The solver difference is drawn in (a) and the changes of the network peak "
              "frequency in (f) and (g); results that rest on the network peak frequency are not used as evidence. The project's other failed checks are not about this figure; all of them are listed in the supplement. " + JC.title_sentence(FS4_ID))
    limits = ("In the limits below, T_ramp is the ramp duration T_ramp (in seconds), and the main example is the run of the first paragraph. " + JC.limits_paragraph(ids))
    rest = " ".join([take, panels, settings, params, failed, limits])
    key = " ".join(x for x in [
        JC.key_symbols(rest, "eta", "Delta", "J", "tau_d", "tau", "r", "v", "N", "M3"),
        "V_p = the peak value of the membrane potential of a network neuron at which it is reset to the negative of that value (the project's values are 100 and, as a check, 200); the Heun scheme is the fixed-step scheme for the noisy runs; "
        "the initial perturbation is the small starting displacement of v; the relative tolerance is the error tolerance of the solver; a failed check = a stated criterion that the result does not meet.",
        JC.class_key(), JC.key_words(rest)] if x)
    return JC.assemble(FS4_ID, take_home=take, panels=panels, key=key, settings=settings, parameters=params, failed=failed, limits=limits)


# ---- supplement data, alt text, build ---------------------------------------------------------------------------------------------------------------

def source_rows(d: dict, FG) -> list:
    rows: list = []
    src = FG._src
    for i, lab in enumerate(d["head_label"]):
        src(rows, "a", f"{plain_head_label(lab)}: classifier onset in s (y = row), class {d['head_class'][i]}", [d["head_onset_s"][i]], [i])
        src(rows, "a", f"{plain_head_label(lab)}: raw first crossing in s (y = row)", [d["head_onset_cross_s"][i]], [i])
    for j, lab in enumerate(d["ms11_col_label"]):
        for i, T in enumerate(d["ms11_T"]):
            src(rows, "b", f"{plain_ms11_label(lab).replace(chr(10), ' ')}, ramp duration {T:g} s: onset shift in s, class {d['ms11_class'][i][j]} (x = column)", [j], [d["ms11_onset_shift_s"][i, j]])
    for L in range(3):
        for q, pn in (("cross", "c"), ("class", "d")):
            arr = d[f"floor_l{L}_{q}_delay"]
            for k, dt in enumerate(d["floor_dt"]):
                src(rows, pn, f"level {L}, Heun step {dt:g} tau: delay of the {arr.shape[1]} seeds (x = step)", [dt] * arr.shape[1], arr[k])
    for i, T in enumerate(d["ms11_T"]):
        src(rows, "e", f"median delay, classifier onset, ramp duration {T:g} s (x = level)", [0, 1, 2], d["floorT_median"][i])
    for s_ in range(d["net_f_pk_hz"].shape[0]):
        src(rows, "f", f"seed {s_}: peak frequency in Hz, classifier-episode reading (x = network time step)", d["net_dt"], d["net_f_pk_hz"][s_])
        src(rows, "f", f"seed {s_}: peak frequency in Hz, spectrum-maximum reading of the first halving (x = network time step)", d["net_dt"][:2], d["net_psd_f_pk_hz"][s_])
        src(rows, "g", f"seed {s_}: relative change of the peak frequency per halving (x = halving 0, 1, 2)", [0, 1, 2], d["net_rel_change"][s_])
    for i, (row, cl) in enumerate(zip(d["netcls_row"], d["netcls_class"])):
        for s_, c_ in enumerate(cl):
            src(rows, "h", f"{row.replace('dt', 'step')}, seed {s_}: class {c_} (x = seed, y = row)", [s_], [i])
    for nm, arr in (("V_p 100", d["vp_f100_hz"]), ("V_p 200", d["vp_f200_hz"])):
        src(rows, "i", f"{nm}: peak frequency in Hz (x = step and seed position)", np.arange(len(arr), dtype=float), arr)
    return rows


def alt_text(d: dict, c: dict) -> dict:
    return {
        "a": f"Six rows, one per numerical setting, with a class mark and a cross at the onset of the main example between 58.65 and 58.93 s; five rows lie at {c['onset_default']:g} s and the Radau row at {c['onset_radau']:g} s; the title is red "
             f"('Solver check: FAIL') and a red note gives Radau minus default = {d['head_radau_minus_default_ms']:g} ms against 1 ms allowed.",
        "b": f"Two rows of marks (ramp durations {c['ms11_T'][0]:g} s and {c['ms11_T'][1]:g} s) for four settings, each labelled with its onset shift in s; all marks are the class D-tr.",
        "c": "Delay of the noise-floor runs under the raw first crossing against the Heun time step (log axis): three levels of ten seeds each at four steps, the points of one level on one another; the delays are small and negative.",
        "d": f"The same runs under the classifier onset: the delays are {c['tie']:g} at levels 0 and 1 and higher at level 2; a note says that {c['tie']:g} is the onset at the ramp start.",
        "e": "Median delay at the noise floor for the levels 0, 1 and 2 at two ramp durations (lines with marks); the legend gives the direction word 'not strictly monotone' for both.",
        "f": "Peak frequency of three network seeds against the network time step (log axis, decreasing to the right), with open marks for the spectrum-maximum reading at the first halving; the title is red and reads 'Network peak frequency against step: FAIL (not evidence)'.",
        "g": f"Relative change of the peak frequency per step halving for three seeds against a dashed bound at {FG_BOUND}; the first halving lies far above the bound ({c['rel_lo']} to {c['rel_hi']} percent); the title is red.",
        "h": "A grid of class marks, one row per time step and V_p, one column per seed; information only.",
        "i": "Peak frequency of each seed at V_p 100 (filled) and 200 (open) for each step and seed; reported only.",
    }


FG_BOUND = 0.02


def sections(d: dict) -> tuple:
    mapping = ("The journal panels (a) to (i) are the draft panels (a), (b), (c), (c2), (d), (e), (f), (g) and (h) in this order (same data, same size 7.4 x 13.8 in): journal (c) = draft (c), journal (d) = draft (c2), journal (e) = draft (d), "
               "journal (f) = draft (e), journal (g) = draft (f), journal (h) = draft (g), journal (i) = draft (h). The draft status block (text under the panels) is not on the image: its lines are in the 'Status block' section of this sheet; "
               "the titles of (a), (f) and (g) carry the plain forms 'Solver check: FAIL' and 'FAIL'.")
    names = ("| plain word in the caption | stored name |\n|---|---|\n| solver check | RB6 solver_onset_headline (the two solvers must agree on the onset within 1 ms) |\n"
             "| network peak frequency check | RB6 network_fpk_halving_dt (the peak frequency must change by less than 2 percent when the time step is halved) |\n"
             "| initial perturbation | solver.delta0 |\n| relative tolerance | solver.rtol |\n| noise floor | D43 floor levels 0 to 2 (sigma_floor) |\n| peak value V_p | network.V_peak |")
    return (("Mapping of the draft panels to the journal panels (DL-681)", mapping), ("Stored names behind the plain words of the caption", names))


def build(FG, res, out_dir, root, script, claim_limit_ids, tag_build) -> dict:
    import dataclasses
    import matplotlib.pyplot as plt
    from .. import provenance as P
    root = Path(root) if root is not None else FG.repo_root()
    res = Path(res) if res is not None else root / "results"
    out = Path(out_dir) if out_dir is not None else root / "figures" / "journal" / FS4_ID
    t = {"start": time.perf_counter()}
    raw = FG.load_FS4(res)
    t["load"] = time.perf_counter()
    d = FG.prepare_FS4(raw)
    t["prepare"] = time.perf_counter()
    rows = []
    for key, rec in raw["records"].items():
        for r in FG.make_param_table(rec["config"]):
            rows.append({**r, "panel": key, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    crit, _ = FG.F.K.load_frozen_criteria(root)
    crows = [r for r in rows if r["key"] in FG.FS4_CAPTION_KEYS and not (r["key"] == "network.N" and r["panel"] != "S13_MS11_network")]
    cap0 = FG.CAP.build_caption("FS4", take_home=FG.FS4_TAKE_HOME, claim_limit_ids=claim_limit_ids, params_rows=crows, spectrogram=None, symbol_keys=(), notes=FG.fs4_caption_notes(d),
                                class_key=FG.CAP.class_key_line("ND"), classifier_line=FG.CAP.classifier_line(crit), main_failures=FG.FS4_MAIN_FAILURES, swept={})
    plain_md = FG.PL.pairing_markdown(claim_limit_ids, None, cap0.text)
    c = consts(d, rows, raw)
    text = caption(d, rows, crit, ids=claim_limit_ids, c=c, FG=FG)
    cap = dataclasses.replace(cap0, text=text)
    cfg = J.load_config(root)
    out.mkdir(parents=True, exist_ok=True)
    stem = "FS4_journal"
    with plt.rc_context(J.rc_params(cfg)):
        fig = draw(d, FG)
        saved = J.save_all(fig, out, stem, cfg)
    plt.close(fig)
    t["draw"] = time.perf_counter()
    drawn = FG.drawn_data_sha256(d)
    P.atomic_write_text(out / f"{stem}_caption.txt", text + "\n")
    P.atomic_write_text(out / f"{stem}_drawn_data_sha256.txt", drawn + "\n")
    warnings = [f"input record {k} ({rec['name']}) was written with git dirty = true" for k, rec in raw["records"].items() if (rec.get("git") or {}).get("dirty")]
    prov_kw = dict(script=script, inputs=[res / p for p in FG.FS4_INPUTS], params_rows=rows,
                   modules=["src/mprsurge/plotting/figures.py", "src/mprsurge/plotting/style.py", "src/mprsurge/plotting/captions.py", "src/mprsurge/plotting/jfs4.py", "src/mprsurge/plotting/nordlie.py",
                            "src/mprsurge/plotting/figprov.py"],
                   configs=["configs/S13.yaml"], claim_limits=cap.claim_limits, spectrogram=None, tag_build=tag_build, root=root)
    status_text = "\n".join(FG.fs4_strip_lines(d))
    return FG._journal_tail(FS4_ID, out, stem, saved, cap, drawn, d, raw, prov_kw, warnings, strip=[], footer=FG.FS4_FOOTER, timing_t=t, source_rows=source_rows(d, FG), alt=alt_text(d, c),
                            pointers=(), cfg=cfg, status_text=status_text, plain_md=plain_md, extra_sections=sections(d), strip_rows=None, zip_note=False, single_caption=True)
