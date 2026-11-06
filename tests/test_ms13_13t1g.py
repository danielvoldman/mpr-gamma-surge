"""MS13 13t-1g (DL-602 to DL-605): tests of the last fix round on the F1, F3, F5 and F5c journal pilot: W1 (the ruled claim limits are in the short captions; the word limits are 460, 400, 460, 460),
W2 (the one 'Parameters:' sentence takes its numbers from the full caption), W3 (plain numbers on the images, no superscript), W4 (a to e: F1 orange lines, F5 class definitions and tie clause,
F3 plain image words, F3 sentence on other failed checks and the supplement list of all FAIL rows).
They read the stored results under results/ and skip if those are absent. Builds go to a temporary directory, never to figures/. No data assertion of an earlier test changes."""
import csv
import re

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jchecks as JK
from mprsurge.plotting import journal as J
from mprsurge.plotting import jshort as JS

ROOT = C.repo_root()
RES = ROOT / "results"
PILOT = ("F1", "F3", "F5", "F5c")
INPUTS = {"F1": FG.F1_INPUTS, "F3": FG.F3_INPUTS, "F5": FG.F5_INPUTS, "F5c": FG.F5_INPUTS}
needs = pytest.mark.skipif(not all((RES / p).is_file() for f in PILOT for p in INPUTS[f]), reason="stored F1, F3 and F5 inputs under results/ are absent")
LIMITS = {"F1": 520, "F3": 520, "F5": 520, "F5c": 520}


@pytest.fixture(scope="module")
def cfg():
    return J.load_config(ROOT)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("journal13t1g")
    out = {f: getattr(FG, f"make_{f}")(mode="journal", out_dir=base / "journal" / f) for f in ("F1", "F3", "F5")}
    out["F5c"] = out["F5"]["F5c"]
    return {"base": base / "journal", "out": out}


def _short(built, f):
    return (built["base"] / f / f"{f}_journal_caption.txt").read_text(encoding="utf-8").strip()


def _full(built, f):
    return (built["base"] / f / f"{f}_journal_caption_full.txt").read_text(encoding="utf-8").strip()


def _sup(built, f):
    return (built["base"] / "supplement" / f"{f}_supplement.md").read_text(encoding="utf-8")


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
    fig.canvas.draw()
    return [" ".join(t.get_text().split()) for t in fig.findobj(matplotlib.text.Text) if t.get_text() and t.get_visible()]


# ---- W1: limits and word limits ----

def test_w1_word_limits_in_the_config(cfg):
    for f, n in LIMITS.items():
        assert J.caption_limit(cfg, f) == n, f


def test_w1_limit_lists_are_those_of_13t_1e():
    assert JS.SHORT_LIMIT_IDS["F5"] == ("G4-C4", "MS9(e)-2", "G4-C3")
    assert JS.SHORT_LIMIT_IDS["F5c"] == ("G4-C3", "MS11-C2", "MS9(e)-1")
    assert JS.SHORT_LIMIT_IDS["F1"] == ("G4-C3", "MS9(e)-1") and JS.SHORT_LIMIT_IDS["F3"] == ("MS11-C3", "MS12-C1")


@needs
def test_w1_every_limit_clause_is_in_the_short_caption_and_the_caption_fits(built, cfg):
    for f in PILOT:
        s = _short(built, f)
        assert JS.limits_missing(f, s) == [], f
        assert JS.words(s) <= J.caption_limit(cfg, f), (f, JS.words(s))


@needs
def test_w1_f5_and_f5c_words(built):
    f5, f5c = _short(built, "F5"), _short(built, "F5c")
    assert "no-ramp network controls" in f5 and "classified into surge classes" in f5
    assert "sigma = 0.0624" in f5 and "checked and not confirmed" in f5
    assert "regime map is robust to noise" in f5 and "maps are robust" not in f5
    assert "no-ramp network controls" in f5c and "classified into surge classes" in f5c
    assert "no claim of agreement in peak frequency or class between the network and the mean field" in f5c
    assert "N = 1000, 3000, 10,000 and 30,000" in f5c or "1000, 3000, 10,000 and 30,000" in f5c


# ---- W2: the Parameters sentence ----

@needs
def test_w2_each_short_caption_has_one_parameters_sentence_with_numbers_from_the_full_caption(built):
    for f in PILOT:
        s = _short(built, f)
        assert s.count("Parameters:") == 1, f
        assert JS.parameters_numbers_missing(s, _full(built, f)) == [], f


@needs
def test_w2_values_of_the_sentences(built):
    p = {f: JS.parameters_sentence(_short(built, f)) for f in PILOT}
    for needle in ("M3", "J = -21", "Delta = 0.3", "tau_d = 5 ms", "10 ms", "120 s", "5 s", "10,000", "2 s", "1 s", "25 to 100 Hz", "0.0624", "checked, not confirmed"):
        assert needle in p["F1"], needle
    assert "no classifier" in p["F3"] and "is used" in p["F3"] and "0.05" in p["F3"] and "1 to 50 ms" in p["F3"] and "J = -21" in p["F3"]
    for needle in ("0.01 to 0.6", "1 to 50 ms", "120 s", "-40 to -5", "30 s", "0.0624", "25 to 100 Hz"):
        assert needle in p["F5"], needle
    for needle in ("1000, 3000, 10,000", "30,000", "60 s", "25 to 100 Hz", "0.0624"):
        assert needle in p["F5c"], needle


def test_w2_guard_names_an_invented_number_and_a_missing_sentence():
    full = "F9. x.\n\nParameters. Stored values: J = -21 and N = 10000.\n\nClassifier and spectrogram settings. window W = 2 s, gamma band 25 to 100 Hz."
    assert JS.parameters_numbers_missing("F9. a. Parameters: J = -21, N = 10,000, window 2 s, band 25 to 100 Hz. b.", full) == []
    assert JS.parameters_numbers_missing("F9. a. Parameters: J = -21, N = 12,000. b.", full) == ["12000"]
    assert JS.parameters_numbers_missing("F9. a.", full) == ["no 'Parameters:' sentence"]


# ---- W3: no superscripts ----

def test_w3_checker_catches_unicode_and_mathtext_superscripts():
    fig, ax = plt.subplots()
    ax.set_xticks([0, 1], ["N = 10³", "ok"])
    assert JK.superscript_violations(fig)
    plt.close(fig)
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, "$10^3$")
    assert JK.superscript_violations(fig)
    plt.close(fig)
    fig, ax = plt.subplots()
    ax.set_xticks([0, 1], ["1000", "10,000"])
    assert JK.superscript_violations(fig) == []
    plt.close(fig)


@needs
def test_w3_no_image_text_holds_a_superscript(figs):
    for f in PILOT:
        assert JK.superscript_violations(figs[f][0]) == [], f
        for t in _texts(figs[f][0]):
            assert not re.search("[²³¹⁰ⁱ⁴-ⁿ]", t), (f, t)


@needs
def test_w3_plain_tick_labels(figs):
    fig = figs["F5c"][0]
    labs = {t for t in _texts(fig)}
    for t in ("1000", "3000", "10,000", "30,000"):
        assert any(t in x for x in labs), t
    for t in ("1,000", "10,000", "100,000"):
        assert t in labs, t
    assert any("ms" in x and "duration" in x for x in labs)                          # the unit is in the axis label of (d)


# ---- W4 ----

@needs
def test_w4a_f1_orange_lines_and_frames(built):
    s = _short(built, "F1")
    assert "an orange solid line and an orange dashed line" in s and "orange frames" in s
    assert "orange frames: the windows" not in s
    i = s.index("orange frames")
    assert "(j)" in s[max(0, i - 120): i + 60] and "(k)" in s[max(0, i - 120): i + 60]


@needs
def test_w4b_f5_defines_every_class_on_the_image(built):
    s = _short(built, "F5")
    assert JS.undefined_terms(s) == []
    for cls in ("S+", "S-rel", "S-abs", "S-sus", "NS", "D-tr", "D-none"):
        assert cls in s, cls
    assert re.search(r"S-sus[^;]{0,30}does not end", s)


@needs
def test_w4c_f5_tie_clause_in_plain_words(built):
    s = _short(built, "F5")
    assert "no single majority class" in s and "10 seeds" in s and "disagreement" in s
    assert "plus: an equal split, a disagreement by the 90 percent rule" not in s and "equal split" not in s
    assert "no single majority class among the 10 seeds of the cell; it counts as a disagreement" in s
    assert JS.undefined_terms(s) == []


def test_w4d_word_list_has_the_three_phrases():
    for s in ("continuation record", "Frequency-map slice", "Frequency-map Hopf point", "the frequency-map slice (9)"):
        assert JK.PLAIN_WORD_BAN.search(s), s
    for s in ("Hopf curve", "Hopf point of a slice", "25 Hz crossing of a slice", "Hopf point of the main example", "frequency map"):
        assert not JK.PLAIN_WORD_BAN.search(s), s


@needs
def test_w4d_f3_image_words(figs):
    t = " | ".join(_texts(figs["F3"][0]))
    assert JK.plain_word_violations(figs["F3"][0]) == []
    for p in ("Hopf curve", "Hopf point of a slice", "25 Hz crossing of a slice", "Hopf point of the main example"):
        assert p in t, p
    for p in ("continuation record", "frequency-map slice", "Frequency-map Hopf point"):
        assert p.lower() not in t.lower(), p


@needs
def test_w4e_f3_sentence_and_supplement_list_every_fail_row(built):
    s = _short(built, "F3")
    assert "No other failed check is about this figure; the project's other failed checks are listed in Supplement F3." in s
    assert "No further failed check of the project" not in s
    with open(RES / "A11" / "a11_robustness.csv", newline="", encoding="utf-8") as fh:
        a11 = list(csv.DictReader(fh))
    fails = [r for r in a11 if r["pass_or_fail"] == "FAIL"]
    assert len(fails) == 13
    assert JK.fail_rows_missing(_sup(built, "F3"), a11) == []
