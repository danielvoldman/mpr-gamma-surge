"""MS13 13t-2 (DL-614 to DL-616): tests of Part A (A1 to A6, the touch-ups of the F1, F3, F5, F5c journal pilot) and Part B (the journal export of F2 and F6).
They read the stored results under results/ and skip if those are absent. Builds go to a temporary directory, never to figures/. No data assertion of an earlier test changes."""
import re

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import journal as J
from mprsurge.plotting import jshort as JS

ROOT = C.repo_root()
RES = ROOT / "results"
PILOT = ("F1", "F3", "F5", "F5c")
INPUTS = {"F1": FG.F1_INPUTS, "F3": FG.F3_INPUTS, "F5": FG.F5_INPUTS, "F5c": FG.F5_INPUTS}
needs = pytest.mark.skipif(not all((RES / p).is_file() for f in PILOT for p in INPUTS[f]), reason="stored F1, F3 and F5 inputs under results/ are absent")
A2_CLAUSE = "(a) and (b) are the same frequency map at other Delta; the failed check was made at the main example in (c) and bears on them too"


@pytest.fixture(scope="module")
def cfg():
    return J.load_config(ROOT)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("journal13t2a")
    out = {f: getattr(FG, f"make_{f}")(mode="journal", out_dir=base / "journal" / f) for f in ("F1", "F3", "F5")}
    out["F5c"] = out["F5"]["F5c"]
    return {"base": base / "journal", "out": out}


def _short(built, f):
    return (built["base"] / f / f"{f}_journal_caption.txt").read_text(encoding="utf-8").strip()


def _full(built, f):
    return (built["base"] / f / f"{f}_journal_caption_full.txt").read_text(encoding="utf-8").strip()


def _norm(s):
    return " ".join(s.split())


# ---- A6: word limits ----

def test_a6_every_short_caption_limit_is_520(cfg):
    for f in ("F1", "F2", "F3", "F5", "F5c", "F6"):
        assert J.caption_limit(cfg, f) == 520, f
    assert cfg["caption"]["short_max_words"] == 520


@needs
def test_a6_pilot_short_captions_fit(built):
    for f in PILOT:
        assert JS.words(_short(built, f)) <= 520, f


# ---- A1: F5c (d) legend and caption say the same ----

LEGEND_A1 = "dashed line: smallest duration the classifier can give (recorded minimum, 1000 ms)"


def test_a1_legend_text_in_the_code():
    src = (ROOT / "src/mprsurge/plotting/figures.py").read_text(encoding="utf-8")
    assert LEGEND_A1 in src


@needs
def test_a1_short_and_full_caption_use_the_same_words(built):
    short, full = _norm(_short(built, "F5c")), _norm(_full(built, "F5c"))
    assert "dashed line in (d): the smallest duration the classifier can give (recorded minimum, 1000 ms)" in short
    assert "the dashed line is the smallest duration the classifier can give (recorded minimum, 1000 ms)" in full
    assert "one window, 1000 ms" not in short


# ---- A2: F3 clause in the short and the full caption; the red titles stay on (a), (b), (c) ----

@needs
def test_a2_clause_in_short_and_full(built):
    assert A2_CLAUSE in _norm(_short(built, "F3"))
    assert A2_CLAUSE in _norm(_full(built, "F3"))


@needs
def test_a2_red_titles_on_a_b_c():
    with FG.journal_figure("F3", close=False) as (fig, d, cfg):
        reds = [t.get_text() for ax in fig.axes for t in (ax.title, ax._left_title) if t.get_text() and "FAIL" in t.get_text()]
    plt.close("all")
    assert len(reds) == 3 and all("frequency check: FAIL" in r for r in reds)


# ---- A3, A4, A5 ----

@needs
def test_a3_dotted_line_clause(built):
    assert "a seed on the dotted line is not evidence of agreement (the check of this panel failed)" in _norm(_short(built, "F5c"))


@needs
def test_a4_blank_lines_clause(built):
    assert "the blank lines through (c) and (d) are map cells that are not in the noisy subgrid" in _norm(_short(built, "F5"))


@needs
def test_a5_onset_clause_numbers_come_from_the_arrays(built):
    d = FG.prepare_F5(FG.load_F5(RES))
    on = np.asarray(d["s9_onset_s"], dtype=float)
    n = int(np.sum(~np.isnan(on)))
    assert n == int(np.sum(on < d["ref_onset_s"]))
    want = f"all {n} drawn ramp-seed onsets ({np.nanmin(on):.1f} to {np.nanmax(on):.1f} s) are earlier than the mean-field onset ({d['ref_onset_s']:.3f} s)"
    assert (n, f"{np.nanmin(on):.1f}", f"{np.nanmax(on):.1f}", f"{d['ref_onset_s']:.3f}") == (39, "8.0", "27.0", "33.698")
    assert want in _norm(_short(built, "F5c"))


@needs
def test_a_text_only_the_digests_stay_equal(built):
    for f, did in (("F1", "F1"), ("F3", "F3"), ("F5", "F5"), ("F5c", "F5")):
        draft = (ROOT / "figures" / did / f"{did}_drawn_data_sha256.txt")
        if draft.is_file():
            assert built["out"][f]["drawn_sha256"] == draft.read_text(encoding="utf-8").strip(), f
