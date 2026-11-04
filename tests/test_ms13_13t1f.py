"""MS13 13t-1f (DL-592 to DL-594): tests of the second fix round on the F1, F3, F5 and F5c journal pilot: V1 (the F1 event strips hold only marks), V2 (F1 canvas text), V3 (plain words on the images),
V4 (powers of ten on the images, plain network sizes in the captions), V5 (every technical term of a short caption is defined where first used), V6 (the facts the short captions state, checked against
the figure arrays), V7 (the count of the other failed checks equals the full caption's), V8 (word limits, numbers of the short caption are in the full caption).
They read the stored results under results/ and skip if those are absent. Builds go to a temporary directory, never to figures/. No data assertion of an earlier test changes."""
import re

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jcaption as JC
from mprsurge.plotting import jchecks as JK
from mprsurge.plotting import journal as J
from mprsurge.plotting import jshort as JS

ROOT = C.repo_root()
RES = ROOT / "results"
PILOT = ("F1", "F3", "F5", "F5c")
INPUTS = {"F1": FG.F1_INPUTS, "F3": FG.F3_INPUTS, "F5": FG.F5_INPUTS, "F5c": FG.F5_INPUTS}
needs = pytest.mark.skipif(not all((RES / p).is_file() for f in PILOT for p in INPUTS[f]), reason="stored F1, F3 and F5 inputs under results/ are absent")


@pytest.fixture(scope="module")
def cfg():
    return J.load_config(ROOT)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("journal13t1f")
    out = {f: getattr(FG, f"make_{f}")(mode="journal", out_dir=base / "journal" / f) for f in ("F1", "F3", "F5")}
    out["F5c"] = out["F5"]["F5c"]
    return {"base": base / "journal", "out": out}


def _short(built, f):
    return (built["base"] / f / f"{f}_journal_caption.txt").read_text(encoding="utf-8").strip()


def _full(built, f):
    return (built["base"] / f / f"{f}_journal_caption_full.txt").read_text(encoding="utf-8").strip()


@pytest.fixture(scope="module")
def figs():
    res = {}
    for f in PILOT:
        c = FG.journal_figure(f, close=False)
        res[f] = c.__enter__()
        c.__exit__(None, None, None)
    yield res
    plt.close("all")


def _texts(fig):
    return [" ".join(t.get_text().split()) for t in fig.findobj(matplotlib.text.Text) if t.get_text() and t.get_visible()]


# ---- V3: plain words ----

def test_v3_ban_pattern_matches_each_word_and_not_the_plain_replacements():
    for s in ("mean field (stored record)", "cycle frequency at the headline", "the matching companion", "map 1, mode D", "f_pk (Hz)", "post-hoc view P-1", "path time (s)"):
        assert JK.PLAIN_WORD_BAN.search(s), s
    for s in ("mean field (recorded run)", "cycle frequency, main example", "matching mean-field run", "no-noise mean field", "peak frequency (Hz)", "post-hoc re-scoring of (c)", "time (s)", "map cell"):
        assert not JK.PLAIN_WORD_BAN.search(s), s


@needs
def test_v3_no_image_text_holds_stored_headline_companion_mode_d_fpk_p1_or_path_time(figs):
    for f in PILOT:
        bad = [t for t in _texts(figs[f][0]) if re.search(r"\bstored\b|\bheadline\b|\bcompanion\b|\bmode D\b|\bf_pk\b|\bP-1\b|\bpath time\b", t)]
        assert bad == [], (f, bad)
        assert JK.plain_word_violations(figs[f][0]) == [], f


@needs
def test_v3_the_ruled_plain_words_are_on_the_images(figs):
    t = {f: " | ".join(_texts(figs[f][0])) for f in PILOT}
    assert "mean field (recorded run)" in t["F1"] and "recorded values" in t["F1"]
    assert "cycle frequency, main example" in t["F3"] and "spectral peak, main example" in t["F3"] and "(recorded)" in t["F3"]
    assert "no-noise mean field" in t["F5"] and "matching mean-field run (30 s)" in t["F5"] and "post-hoc re-scoring" in t["F5"] and "of (c)" in t["F5"]
    assert "recorded minimum duration" in t["F5c"] and "recorded minimum to maximum and median" in t["F5c"] and "matching mean-field run" in t["F5c"] and "peak frequency" in t["F5c"]
    assert "map cell" in t["F5"]                                   # 'map cell' stays (V3)


# ---- V4: powers of ten ----

@needs
def test_v4_no_e_notation_on_the_images_and_powers_of_ten_in_mathtext(figs):
    for f in PILOT:
        assert JK.e_notation_violations(figs[f][0]) == [], f
    t = _texts(figs["F5c"][0])
    for want in (r"N = $\mathregular{10^{3}}$", r"N = $\mathregular{3\times10^{3}}$", r"N = $\mathregular{10^{4}}$", r"N = $\mathregular{3\times10^{4}}$", r"$\mathregular{10^{3}}$ ms", r"$\mathregular{10^{4}}$ ms", r"$\mathregular{10^{5}}$ ms"):
        assert want in t, want
    assert any("peak frequency" in s for s in t)


def test_v4_plain_n_rewrites_only_the_network_sizes():
    assert JC.plain_n("N = 1e3, 3e3, 1e4 and 3e4") == "N = 1000, 3000, 10,000 and 30,000"
    assert JC.plain_n("matched to 1e-9, 1e-3 tau, 2e3x") == "matched to 1e-9, 1e-3 tau, 2e3x"
    assert JC.plain_n("(N = 1e4)") == "(N = 10,000)"


@needs
def test_v4_captions_hold_no_e_notation_of_n(built):
    for f in PILOT:
        for text in (_short(built, f), _full(built, f)):
            assert not re.search(r"(?<![\w.+-])(?:1e3|3e3|1e4|3e4)\b", text), f
    assert "N = 10,000" in _short(built, "F1") and "30,000" in _full(built, "F5c")


# ---- V2, V1: F1 canvas text and strips ----

@needs
def test_v2_f1_in_panel_line_is_one_plain_line_and_the_time_label_is_plain(figs):
    fig, d, _ = figs["F1"]
    lines = [t for t in fig.findobj(lambda a: a.get_gid() == "net line")]
    assert len(lines) == 2
    want = f"network class {d['cls120'][0]}; mean field {d['ref_class']}"
    for t in lines:
        assert " ".join(t.get_text().split()).replace("; ", ";") in (want.replace("; ", ";"), want.replace("; ", ";")), t.get_text()
        assert "seeds agree" not in t.get_text() and "FAIL" not in t.get_text() and "RB1" not in t.get_text()
    labels = {t.get_text() for ax in fig.axes for t in (ax.xaxis.label,) if t.get_text()}
    assert "time (s)" in labels and "path time (s)" not in labels


@needs
def test_v2_f1_schematic_keeps_six_boxes_with_at_most_three_label_lines_from_existing_words(figs):
    boxes = FG.F1J_SCHEMATIC
    assert [b[0] for b in boxes] == ["ramp", "model", "mf", "net", "out"] and len(FG.F1_SCHEMATIC_ARROWS) >= 3
    assert all(len(rows) <= 4 for _, _, rows in boxes)
    text = " ".join(" ".join(r) for _, _, rows in boxes for r in rows)
    assert "N →" not in text and "∞" not in text and "common (non-local)" not in text
    model = [" ".join(r) for r in boxes[1][2]]
    assert model[0] == "all-to-all coupling" and "Lorentzian heterogeneity" in model[1] and "inhibition-dominated (ING)" in model[-1]
    ramp = [": ".join(r) for r in boxes[0][2]]
    assert "P2: hypoxia-like path" in ramp and "t_on, T_ramp: ramp start and duration" in ramp


@needs
def test_v1_f1_strips_hold_only_marks_and_the_key_holds_the_strip_note(figs):
    fig, d, _ = figs["F1"]
    strips = [ax for ax in fig.axes if ax.get_gid() in ("panel:d", "panel:f") and ax.get_ylim() == (0.0, 1.0) and not ax.get_yticks().size]
    assert len(strips) == 2
    for ax in strips:
        assert [t for t in ax.texts] == []
        xs = sorted(round(float(l.get_xdata()[0]), 3) for l in ax.lines if len(l.get_xdata()) == 1)
        assert xs == sorted([d["onset120_s"][0], *[round(x, 3) for x in d["raw120_s"]]]) or len(xs) == 4
    assert any("event marks: strips above (d) and (f); height has no meaning" in t for t in _texts(fig))
    assert not any(t == "event times; height has no meaning" for t in _texts(fig))


# ---- V5: definitions ----

def test_v5_undefined_terms_flags_a_term_without_its_definition_and_accepts_it_with_the_definition():
    assert "surge" in JS.undefined_terms("A surge happens.")
    assert JS.undefined_terms("A surge (a transient rise of gamma-band power, 25 to 100 Hz) happens.") == []
    assert "control" in JS.undefined_terms("The controls end. " + "x" * 600 + " controls (the same network without the ramp)")
    assert JS.undefined_terms("network: N simulated spiking neurons; controls (the same network without the ramp) end") == []


@needs
def test_v5_every_technical_term_of_each_short_caption_is_defined_where_first_used(built):
    for f in PILOT:
        assert JS.undefined_terms(_short(built, f)) == [], (f, JS.undefined_terms(_short(built, f)))


def test_v5_every_definition_has_a_probe_and_the_two_unverified_wordings_carry_a_note():
    assert len(JS.DEFS) >= 40
    for k, (rx, probe, note) in JS.DEFS.items():
        re.compile(rx)
        re.compile(probe)
    assert JS.DEFS["first crossing"][2] and JS.DEFS["duration"][2] and JS.DEFS["map cell"][2]
    assert "first crossings? of its detection threshold" in JS.DEFS["first crossing"][1]


# ---- V6: the statements the short captions make, against the arrays ----

@needs
def test_v6_f5c_control_counts_are_those_of_the_arrays(built):
    d = FG.prepare_F5(FG.load_F5())
    surge = [int(np.sum([str(c) in JC.MODE_N_SURGE for c in row])) for row in d["ctrl_class"]]
    sus = [int(np.sum(np.asarray(row) == "S-sus")) for row in d["ctrl_class"]]
    assert surge == [0, 2, 1, 1] and sus == [0, 0, 2, 2]
    ns = int(np.sum(np.asarray(d["s9_class"])[2] == "NS"))
    assert ns == 1
    short = _short(built, "F5c")
    assert "Controls in a surge class: 0, 2, 1 and 1 of 3; controls in S-sus: 0, 0, 2 and 2 of 3" in short
    assert "one ramp seed at N = 10,000 is NS" in short and "not 10 of 10 in a surge class" in short
    full = _full(built, "F5c")
    assert "the no-ramp controls in S-sus (not a surge class): 0, 0, 2 and 2 of 3 at N = 1000, 3000, 10,000 and 30,000" in full


@needs
def test_v6_f5_sentence_one_is_the_ruled_sentence_and_the_agreement_rule_is_stated(built):
    short = _short(built, "F5")
    s1 = ("F5. The surge result holds for the noise-free mean field only: the network disagrees with it at 3 of the 4 cells tested, and the noisy mean field agrees with the noise-free map in 97 of 225 cells "
          "(43.1 percent; 203 cells, 90 percent, were needed).")
    assert short.startswith(s1)
    for want in ("a network cell agrees when all 3 seeds are in a surge class (S+: absolute and relative rise, ending; S-rel: relative only; S-abs: absolute only) where the mean field is D-tr", "cell 1 agrees",
                 "numbered 1 to 4 here and in (b)", "a 30 x 30 grid", "at ramp duration 120 s", "ramp duration 30 s (map: 120 s); no equivalence is claimed", "tie (plus: an equal split, a disagreement by the 90 percent rule",
                 "chosen after the results (post hoc; no check; dashed frame)", "Map 2: initial coupling J0"):
        assert want in short, want


@needs
def test_v6_f3_states_the_slice_counts_the_grey_circle_and_the_one_arrow(built):
    short = _short(built, "F3")
    for want in ("(7, 6 and 3 of 9 slices have one, as recorded)", "straight segments between recorded points", "the grey open circle is the start of the paths (eta_bar 1.396)",
                 "the dark ring the Hopf point of the main example at tau_d 5 ms", "drawn as one arrow because their eta_bar, Delta and tau_d are equal", "P4a, P4b", "analysis record listed in the supplement"):
        assert want in short, want
    assert "30" not in re.sub(r"\b30,000\b", "", short) and "100 points" not in short and "project log" not in short
    assert "30 points" in _full(built, "F3") and "100 stored points" in _full(built, "F3")


@needs
def test_v6_f1_states_the_ruled_facts(built):
    short = _short(built, "F1")
    for want in ("By eye the network envelopes in (d) and (f) look similar to the mean-field ones in (c) and (e)", "no claim is made about the visual shape, either way", "(nearly coincident)",
                 "same y axes as (c), (e)", "dashed lines: 25 and 100 Hz, the gamma band", "orange frames: the windows of (j), (k)",
                 "coupling J (negative = inhibitory)", "peaks at 49.0 Hz (not drawn)", "all 3 random seeds"):
        assert want in short, want


@needs
def test_v6_f5c_short_has_the_dotted_and_dashed_line_wording(built):
    short = _short(built, "F5c")
    assert "dotted line in (b), (c): the matching mean-field run" in short
    assert "dashed line in (d): the smallest duration the classifier can give (one window, 1000 ms)" in short
    assert "come from other network runs, not the controls drawn here" in short


# ---- V7: the count of the other failed checks ----

def test_v7_failed_in_full_counts_each_row_once_and_the_count_excludes_the_rows_named_in_the_short_caption():
    para = "Failed checks. Shown, not dropped: RB1 (network against mean field), the 4 map cells at a ramp duration of 30 s: FAIL; RB6 (numerical convergence), the network peak frequency f_pk when the step is halved: FAIL. The sigma check also FAILED."
    full = "F9. take.\n\n" + para
    assert JS.failed_in_full(full) == {("RB1", "cells_30s"), ("RB6", "network_fpk_halving_dt"), ("sigma_check", "S8_baseline_std")}
    JS.SHORT_NAMED["F9"] = {("RB1", "cells_30s")}
    try:
        assert JS.further_count("F9", full) == 2
        assert "2 further failed checks of the project are not shown in this figure; all are listed in Supplement F9." == JS.further_sentence("F9", full)
    finally:
        del JS.SHORT_NAMED["F9"]


@needs
def test_v7_the_count_in_each_short_caption_equals_the_count_computed_from_the_full_caption(built):
    for f in PILOT:
        short, full = _short(built, f), _full(built, f)
        n = JS.further_count(f, full)
        if n == 0:
            assert "No further failed check of the project is listed for this figure" in short, f
        else:
            assert f"{n} further failed checks of the project are not shown in this figure; all are listed in Supplement {f}." in short, f
        # an independent recount of the rows named in the full caption's failed-checks paragraph
        para = next(p for p in full.split("\n\n") if p.startswith("Failed checks. "))
        named = {k for k, rx in JS.FAILED_DETECT.items() if re.search(rx, para)}
        assert len(named - JS.SHORT_NAMED[f]) == n
        assert JS.SHORT_NAMED[f] <= named, (f, JS.SHORT_NAMED[f] - named)       # a check named in the short caption is also listed in the full caption


@needs
def test_v7_short_names_only_failed_checks_that_are_drawn(built):
    assert JS.SHORT_NAMED == {"F1": {("RB1", "headline_10s"), ("RB1", "headline_120s"), ("RB1", "cells_30s")}, "F3": {("RB9", "b_spectral_vs_cycle_headline")},
                              "F5": {("RB1", "cells_30s"), ("RB2", "noisy_subgrid_agreement")}, "F5c": {("RB6", "network_fpk_halving_dt")}}
    for f in PILOT:
        assert "listed in the supplement" in _short(built, f) and "All earlier failures and limits stand" in _short(built, f)


# ---- V8: limits and numbers ----

def test_v8_word_limits_are_the_ruled_ones(cfg):
    assert [J.caption_limit(cfg, f) for f in PILOT] == [400, 330, 330, 330]


@needs
def test_v8_short_captions_are_within_the_limits_and_every_number_is_in_the_full_caption(built, cfg):
    for f in PILOT:
        short, full = _short(built, f), _full(built, f)
        assert JS.words(short) <= J.caption_limit(cfg, f), (f, JS.words(short))
        assert JS.numbers_not_in_full(short, full) == [], (f, JS.numbers_not_in_full(short, full))
        assert JS.limits_missing(f, short) == [], f


def test_v8_numbers_of_helper_removes_thousands_separators():
    assert JS.numbers_of("N = 10,000 and 30,000, 7, 6 and 3") == {"10000", "30000", "7", "6", "3"}
    assert JS.numbers_not_in_full("N = 10,000 and 5", "10000 only") == ["5"]
