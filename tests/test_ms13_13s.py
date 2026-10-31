"""MS13 13s (DL-537, DL-538, DL-539): tests of the FS1 to FS5 changes (G1 to G12, D1 to D3, the FS4 reading) and of the F2 and F6 layout fixes.
They read the stored results under results/ (git-ignored) and skip if those are absent. Builds go to a temporary directory, never to figures/.
Every comparison is exact (string containment, set equality, SHA-256 of the drawn data)."""
import re

import pytest

from mprsurge import config as C
from mprsurge.plotting import captions as CAP
from mprsurge.plotting import figures as FG
from mprsurge.plotting import style as S

ROOT = C.repo_root()
RES = ROOT / "results"
FS = ("FS1", "FS2", "FS3", "FS4", "FS5")
INPUTS = {f: getattr(FG, f"{f}_INPUTS") for f in FS}
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for f in FS for p in INPUTS[f]), reason="stored FS1 to FS5 inputs under results/ are absent")
DL535 = {"F2": "3584f8faee5d704a1f172ad4185c133324ddb9f196f32d05d80f3ca5ef28a932", "F6": "4dafe2ab2f5ee3c2b505f82d4f50a3a8b96a9bb1c9cdfb5379b7a3e6f7e2c532"}
D2 = CAP.D2_STATEMENT


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("figs13s")
    return {f: getattr(FG, f"make_{f}")(out_dir=base / f) for f in FS}


@pytest.fixture(scope="module")
def figs():
    import matplotlib.pyplot as plt
    out = {}
    for f in FS:
        d = getattr(FG, f"prepare_{f}")(getattr(FG, f"load_{f}")())
        out[f] = getattr(FG, f"_draw_{f}")(d, True)
    yield out
    plt.close("all")


def _cap(built, f):
    return built[f]["caption"]


def test_class_key_is_verbatim_where_classes_are_drawn_and_absent_where_none_are(built):
    for f in ("FS3", "FS4", "FS5"):
        key = CAP.class_key_line("ND", agree=(f == "FS3"))
        assert key in _cap(built, f), f
        assert CAP.TABLE_2_1_SURGE in _cap(built, f), f
    for f in ("FS1", "FS2"):
        assert "Class key" not in _cap(built, f), f


def test_no_text_below_the_tick_size_in_fs1_to_fs5(figs):
    from matplotlib.text import Text
    assert S.FS_SIZES["fs5_class"] >= S.MIN_TEXT_PT
    for f, fig in figs.items():
        small = [t.get_text() for t in fig.findobj(Text) if t.get_text() and t.get_fontsize() < S.MIN_TEXT_PT]
        assert small == [], (f, small[:3])


def test_every_red_title_has_fail_and_the_red_title_rule_is_stated(figs, built):
    red = S.figure_colour("fail_text")
    for f, fig in figs.items():
        from matplotlib.colors import to_hex
        for ax in fig.axes:
            t = ax.get_title(loc="left")
            if t and to_hex(ax._left_title.get_color()) == to_hex(red):
                assert "FAIL" in t, (f, t)
    for f in ("FS2", "FS3", "FS4", "FS5"):
        assert CAP.RED_TITLE_NOTE.capitalize() in _cap(built, f), f


def test_sentence_one_names_the_main_failure(built):
    mains = {"FS1": FG.FS1_MAIN_FAILURES, "FS2": FG.FS2_MAIN_FAILURES, "FS3": FG.FS3_MAIN_FAILURES, "FS4": FG.FS4_MAIN_FAILURES, "FS5": FG.FS5_MAIN_FAILURES}
    for f, ms in mains.items():
        first = getattr(FG, f"{f}_TAKE_HOME").split(". ")[0]
        assert all(m in first for m in ms), f
        assert _cap(built, f).startswith(f"{f}. "), f


def test_d2_statement_is_on_fs4_only(built, figs):
    assert D2 in _cap(built, "FS4")
    for f in ("FS1", "FS2", "FS3", "FS5"):
        assert D2 not in _cap(built, f), f
    texts = [t.get_text() for t in figs["FS4"].findobj(__import__("matplotlib").text.Text)]
    assert any(D2 in t.replace("\n", " ") or "eta_start - eta_H (-1.5)" in t for t in texts) or any("D2" in t for t in texts)
    assert "Project reading (DL-429" in "".join(texts).replace("\n", " ") or "DL-429" in _cap(built, "FS4")


def test_fs3_states_the_lorentzian_claim_limit_not_a_result(built):
    phrase = "the claim is stated for Lorentzian heterogeneity only"
    assert phrase in FG.FS3_TAKE_HOME and phrase in _cap(built, "FS3")
    assert "not a result" in FG.FS3_TAKE_HOME


def test_fs4_draws_not_strictly_monotone_only(figs):
    from matplotlib.text import Text
    texts = [t.get_text() for t in figs["FS4"].findobj(Text)]
    assert any("not strictly monotone" in t for t in texts)
    assert not any(re.search(r"not monotone", t) for t in texts)


def test_parameters_sentence_lists_swept_ranges_and_noise_sigma_only_where_noise_is_drawn(built):
    def params(f):
        return _cap(built, f).split("Parameters: ", 1)[1].split(". The full parameter list", 1)[0]
    for f in FS:
        assert "swept" in params(f), f
    assert "noise.sigma=0.0624 (checked, not confirmed, G4-C4)" in params("FS3")
    for f in ("FS1", "FS2", "FS4", "FS5"):
        assert "noise.sigma" not in params(f), f
    assert "model.eta_bar=-10 to 2 (241 values), swept" in params("FS1") and "model.J=0 to 20 (201 values), swept" in params("FS1")
    assert "path_hypoxia" not in params("FS1")


def test_footers_and_strip_headings_cite_the_13s_entries():
    for f in FS:
        assert FG.RULED_DL[f][-4:] == ("DL-511", "DL-512", "DL-537", "DL-538")
        assert "DL-537, DL-538" in FG.draft_footer(f) and "DL-537, DL-538" in FG.strip_heading(f)


def test_f2_and_f6_drawn_data_digests_are_unchanged():
    for f in ("F2", "F6"):
        d = getattr(FG, f"prepare_{f}")(getattr(FG, f"load_{f}")())
        assert FG.drawn_data_sha256(d) == DL535[f], f


def test_the_f2_status_text_lies_above_the_draft_footer():
    import matplotlib.pyplot as plt
    d = FG.prepare_F2(FG.load_F2())
    fig = FG._draw_F2(d, True, FG.strip_lines(d))
    try:
        fig.canvas.draw()
        rend = fig.canvas.get_renderer()
        foot = [t for t in fig.texts if t.get_gid() == "draft_note"][0].get_window_extent(rend)
        from matplotlib.text import Annotation
        bottoms = [t.get_window_extent(rend).y1 for ax in fig.axes for t in ax.texts if isinstance(t, Annotation)]
        assert bottoms and min(t.get_window_extent(rend).y0 for ax in fig.axes for t in ax.texts if isinstance(t, Annotation)) > foot.y1
    finally:
        plt.close(fig)
