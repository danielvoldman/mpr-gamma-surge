"""MS13 13t-3 (DL-627 to DL-629): tests of Part A (C1 to C9: F2 red title and note, the key handle, the short captions of the six journal figures, the word limit 600, the allow-list reason classes and the
sentence case of every journal image) and of Part B (the journal export of the finished FS figures). They read the stored results under results/ and skip if those are absent. Builds go to a
temporary directory, never to figures/. No data assertion of an earlier test changes (text edits: DL-630)."""
import re
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import collide as CO
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jf26 as JF
from mprsurge.plotting import jshort as JS
from mprsurge.plotting import journal as J

ROOT = C.repo_root()
RES = ROOT / "results"
FIGS = ("F1", "F2", "F3", "F5", "F5c", "F6")
needs = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F1_INPUTS + FG.F2_INPUTS + FG.F3_INPUTS + FG.F5_INPUTS + FG.F6_INPUTS), reason="stored inputs under results/ are absent")


@pytest.fixture(scope="module")
def cfg():
    return J.load_config(ROOT)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("journal13t3")
    out = {f: getattr(FG, f"make_{f}")(mode="journal", out_dir=base / "journal" / f) for f in ("F1", "F2", "F3", "F5", "F6")}
    out["F5c"] = out["F5"]["F5c"]
    return {"base": base / "journal", "out": out}


def _short(built, f):
    return (built["base"] / f / f"{f}_journal_caption.txt").read_text(encoding="utf-8").strip()


def _full(built, f):
    return (built["base"] / f / f"{f}_journal_caption_full.txt").read_text(encoding="utf-8").strip()


def _norm(s):
    return " ".join(s.split())


@pytest.fixture(scope="module")
def f2d():
    return FG.prepare_F2(FG.load_F2(RES))


@pytest.fixture(scope="module")
def f6d():
    return FG.prepare_F6(FG.load_F6(RES))


# ---- C9: sentence case ----

def test_c9_sentence_start_rules():
    ok = ["Mean field (recorded run)", "(a) Fixed point", "eta_bar", "S-sus rise", "D-tr", "(c) Network vs mean field: FAIL", "a: Delta above critical", "N: network size", "J: coupling", "5 s", "Delta above critical",
          "T_ramp (s)", "P4b", "r, v, s: rate, mean potential, synapse", "tau_d (ms), log axis", "ms", "FAIL"]
    bad = ["network size", "(a) fixed point", "map cell", "mean field (recorded run)", "negative control 1", "time (s)", "onset (s)", "peak frequency (Hz)"]
    assert all(J.sentence_start_ok(s) for s in ok), [s for s in ok if not J.sentence_start_ok(s)]
    assert not any(J.sentence_start_ok(s) for s in bad)


def test_c9_sentence_case_capitalises_a_label_and_keeps_the_exceptions():
    fig, ax = plt.subplots()
    ax.set_title("(a) fixed point")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("eta_bar (mean excitability)")
    ax.text(0.5, 0.5, "network size")
    ax.set_yticks([0, 1], ["negative control", "S-sus"])
    n = J.sentence_case(fig)
    fig.canvas.draw()
    texts = {t.get_text() for t in fig.findobj(matplotlib.text.Text)}
    assert n >= 4 and {"(a) Fixed point", "Time (s)", "eta_bar (mean excitability)", "Network size", "Negative control", "S-sus"} <= texts
    assert J.lowercase_starts(fig) == []
    plt.close(fig)


@needs
@pytest.mark.parametrize("fid", FIGS)
def test_c9_no_image_label_starts_with_a_lower_case_word(fid):
    with FG.journal_figure(fid, close=False) as (fig, d, cfg):
        fig.canvas.draw()
        assert J.lowercase_starts(fig) == [], fid
    plt.close("all")


# ---- C6: word limits ----

def test_c6_every_short_caption_limit_is_600(cfg):
    assert cfg["caption"]["short_max_words"] == 600
    for f in ("F1", "F2", "F3", "F5", "F5c", "F6"):
        assert J.caption_limit(cfg, f) == 600, f


@needs
def test_c6_short_captions_fit_and_every_number_is_in_the_full_caption(built):
    for f in FIGS:
        short, full = _short(built, f), _full(built, f)
        assert JS.words(short) <= 600, (f, JS.words(short))
        assert JS.numbers_not_in_full(short, full) == [], f
        assert JS.undefined_terms(short) == [], f
        assert JS.limits_missing(f, short) == [], f


# ---- C1, C2, C3: F2 ----

@needs
def test_c1_f2_has_one_red_title_on_c_and_the_one_plain_note():
    with FG.journal_figure("F2", close=False) as (fig, d, cfg):
        fig.canvas.draw()
        from mprsurge.plotting import jchecks as JK
        reds = JK.red_titles(fig)
        notes = [" ".join(a.get_text().split()) for a in fig.findobj(lambda a: a.get_gid() == "panel note")]
        titles = {ax.get_gid(): ax._left_title.get_text() for ax in fig.axes if ax.get_gid()}
    plt.close("all")
    assert [r[0] for r in reds] == ["c"] and reds[0][1] == "(c) Network vs mean field: FAIL"
    assert "The network and mean-field classes disagree elsewhere (check failed); this panel compares amplitudes only" in notes
    assert "FAIL" not in titles["panel:a"] and "FAIL" not in titles["panel:b"]


@needs
def test_c1_f2_captions_say_the_same_in_one_sentence(built):
    short, full = _short(built, "F2"), _full(built, "F2")
    assert JF.F2_RED_NOTE in short and JF.F2_RED_NOTE in full
    assert "Panels (a) and (b) have no red title" in short and "Panels (a) and (b) have no red title" in full
    assert "No other failed check is about this figure" in short                      # the four RB1 rows are named in the red-title sentence (DL-628 C1)
    assert JS.further_count("F2", full) == 0


def test_c2_the_stable_fixed_point_key_handle_holds_three_dash_periods():
    ls = FG.F2J_STABLE_LS
    assert isinstance(ls, tuple) and ls[0] == 0
    lw = FG.S.diagram_mark("a5_fixed_stable").width
    period_pt = sum(ls[1]) * lw
    assert FG.F2J_KEY_HANDLE * 8.0 >= 3 * period_pt - 1e-9, (FG.F2J_KEY_HANDLE * 8.0, period_pt)


@needs
def test_c3_f2_short_caption_new_sentences_numbers_from_the_arrays(built, f2d):
    short = _short(built, "F2")
    f = JF.f2_facts(f2d)
    big = f["big"]
    assert abs(abs(big[2] - big[1]) - 0.095) < 5e-4 and abs(big[0] - 2.896) < 5e-4                     # the values read in DL-630
    assert f"is {abs(big[2] - big[1]):.3f} ({big[1]:.3f} up, {big[2]:.3f} down) at eta_bar {big[0]:.3f}" in short
    assert (f"At the Hopf point the network v amplitude is {f['hopf_net'][0]:.2f} (up sweep) and {f['hopf_net'][1]:.2f} (down sweep) against {f['hopf_mf'][0]:.2f} and {f['hopf_mf'][1]:.2f} for the mean field") in short
    assert "below the Hopf point the network does not rest" in short
    assert (round(f["hopf_net"][0], 2), round(f["hopf_net"][1], 2), round(f["hopf_mf"][0], 2), round(f["hopf_mf"][1], 2)) == (1.07, 1.17, 0.08, 0.55)
    assert "in a sweep eta_bar is raised step by step, then lowered again" in short
    assert "no classifier" not in short and "spectrogram" not in short.split("Parameters:")[1].split("Limits:")[0]
    lim = short.split("Limits:")[1]
    assert lim.count("model M3 only") == 1 and "stated for the mean field only" in lim and "finite-size fluctuations" in lim
    assert "no classifier" in _full(built, "F2").lower() or "no classifier or spectrogram" in _full(built, "F2")           # the full caption keeps it


@needs
def test_c3_the_ruled_f2_sentence_one_is_not_changed(built):
    assert FG.F2_TAKE_HOME.startswith("The N = 1e4 network sweep does not follow the mean-field branch closely")
    assert _short(built, "F2").startswith("F2. The network (the simulated network of N = 10,000 spiking neurons) does not follow the mean-field branch closely")


# ---- C4: F6 ----

@needs
def test_c4_f6_short_caption(built, f6d):
    short = _short(built, "F6")
    assert "listed in the key above panel (a)" in short
    assert "filled bars: the primary label (the first that applies); hatched and dotted bars: every label that applies" in short
    assert FG.S.figure_hatch("map1_any") != FG.S.figure_hatch("map2_any") and "." in FG.S.figure_hatch("map2_any")
    assert "NS: no rise, the noisy-run counterpart of D-none" in short
    assert "Negative control 2 is D-tr at every ramp duration in the mean field; the failed check is the one on negative control 1 (network S+)" in short
    assert "negative control 2 (the full path with the drive off and on)" in short and "negative control 3 (inhibition raised while the mean excitability falls; exploratory)" in short
    f = JF.f6_facts(f6d)
    assert (f["n_all"], f["n_pre"], f["n_cmp"]) == (24, 20, 4) and f["fpk"] == ["48.048", "49", "49", "49.5"]
    assert "The 24 points drawn in (d) and (e) are the 20 pre-registered runs and 4 P2 comparator runs" in short
    assert "are identical (48.048, 49, 49 and 49.5 Hz), so those lines overlap" in short
    assert "the noise level sigma = 0.0624 is checked and not confirmed" in short and "the noisy rows of (b) use it" in short


@needs
def test_c4_f6_values_stop_the_build_when_they_differ(f6d):
    d = dict(f6d)
    d["s6_n_prereg"] = 19
    with pytest.raises(Exception, match="pre-registered"):
        JF.f6_facts(d)
    d = dict(f6d)
    fp = np.array(f6d["s6_f_pk_hz"], dtype=float)
    fp[1, 0] += 0.5
    d["s6_f_pk_hz"] = fp
    with pytest.raises(Exception, match="identical"):
        JF.f6_facts(d)


# ---- C5: the other short captions ----

@needs
def test_c5_f5_f5c_f3_f1_short_clauses(built):
    f5, f5c, f3, f1 = (_short(built, f) for f in ("F5", "F5c", "F3", "F1"))
    assert "the same cells agree in 173 of 225 (76.9 percent) under the re-scoring chosen after the results; it feeds no check" in f5
    assert "the blank lines through (c) and (d) are map cells that are not in the noisy subgrid" in f5
    for s in ("no seed is S-rel", "3 control seeds per N is a small sample", "the controls also flag onsets from 10.0 to 33.0 s, so onset is not a ramp-specific signal in this figure",
              "the plotted peak frequencies come from runs whose step-halving check failed, so they are not shown to be converged"):
        assert s in f5c, s
    assert "The paths coincide in (c) and (d) because they differ in J, drive or time course, which these planes do not show" in f3
    assert f1.count("not drawn here") == 2 and "(the 10 s ramp is not drawn here)" in f1 and "map cells (one parameter pair of a grid of mean-field runs; not drawn here)" in f1


@needs
def test_c5_the_numbers_come_from_the_arrays():
    d = FG.prepare_F5(FG.load_F5(RES))
    assert (int(d["p1_n_agree"]), int(d["sub_n"])) == (173, 225) and f"{100.0 * d['p1_n_agree'] / d['sub_n']:.1f}" == "76.9"
    cl = np.concatenate([np.asarray(d["s9_class"]).ravel(), np.asarray(d["ctrl_class"]).ravel()])
    assert "S-rel" not in set(cl) and np.asarray(d["ctrl_class"]).shape[1] == 3
    on = np.asarray(d["ctrl_onset_s"], float)
    assert (np.nanmin(on), np.nanmax(on)) == (10.0, 33.0)


# ---- C7: the allow-lists ----

def test_c7_every_allow_entry_of_f2_and_f6_is_a_stored_coincidence_a_ruled_size_or_a_reference_line():
    sys.path.insert(0, str(ROOT / "scripts"))
    import ms13_verify_export as V
    for f in ("F2", "F6"):
        assert CO.JOURNAL_ALLOW[f]
        for e in CO.JOURNAL_ALLOW[f]:
            assert V.reason_class(e.reason) != V.REASON_OTHER, (f, e.reason[:60])
    assert V.reason_class("the label is easier to read when it overlaps") == V.REASON_OTHER
    assert V.reason_class("a stored value on the line (a reference line)") == "value on a reference line"
