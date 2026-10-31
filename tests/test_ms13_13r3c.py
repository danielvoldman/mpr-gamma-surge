"""MS13 13r-3c: per-figure tests of F5 and F6 for the 13r items (DL-529, DL-530, DL-531). Reads the stored results under results/ (skipped if absent); builds go to a temporary
directory, never to figures/. Exact comparisons."""
import numpy as np
import pytest
from matplotlib.colors import to_hex

from mprsurge import config as C
from mprsurge.plotting import captions as K
from mprsurge.plotting import figprov as F
from mprsurge.plotting import figures as FG
from mprsurge.plotting import style as S

ROOT = C.repo_root()
RES = ROOT / "results"
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in list(FG.F5_INPUTS) + list(FG.F6_INPUTS)), reason="stored F5 and F6 inputs under results/ are absent")
CLASS_MARKERS = {S.get(k).marker for k in S.CLASS_KEYS}
CLASS_COLOURS = {v[0].lower() for v in S._TABLE["class"].values()}


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs13r3c")
    return {"F5": FG.make_F5(out_dir=out / "F5"), "F6": FG.make_F6(out_dir=out / "F6")}


@pytest.fixture(scope="module")
def figs():
    import matplotlib.pyplot as plt
    d5 = FG.prepare_F5(FG.load_F5())
    raw6 = FG.load_F6()
    d6 = FG.prepare_F6(raw6)
    out = {"F5": (d5, FG._draw_F5(d5, True)), "F6": (d6, FG._draw_F6(d6, True, columns=FG.f6_column_labels(raw6)))}
    yield out
    for _d, fig in out.values():
        plt.close(fig)


def _sentence1(caption: str, fid: str) -> str:
    return caption[len(fid) + 2:].split(". ")[0]


def _crit():
    return F.K.load_frozen_criteria(ROOT)[0]


def test_sentence_one_names_the_failures(built):
    s5 = _sentence1(built["F5"]["caption"], "F5")
    assert s5 == "Mean field only; network disagrees at 3 of 4 cells; noisy subgrid 43.1 percent (203 needed)"
    for n in FG.F5_MAIN_FAILURES:
        assert n in s5
    s6 = _sentence1(built["F6"]["caption"], "F6")
    assert FG.F6_MAIN_FAILURES == ("G7 NOT PASSED (1 network seed, S+)",) and s6.startswith("G7 NOT PASSED (1 network seed, S+): the NC1 network run")


def test_class_key_and_classifier_line_are_in_both_captions(built):
    assert K.class_key_line("ND", agree=True) in built["F5"]["caption"] and K.class_key_line("ND") in built["F6"]["caption"]
    for f in ("F5", "F6"):
        assert K.classifier_line(_crit()) in built[f]["caption"]


def test_fail_is_in_every_red_title(figs):
    from figlayout import red_titles_without_fail
    for fid, want in (("F5", ["(b)", "(c)"]), ("F6", ["(c)"])):
        fig = figs[fid][1]
        assert red_titles_without_fail(fig) == []
        red = [ax.get_title(loc="left") for ax in fig.axes if to_hex(ax._left_title.get_color()).lower() == S.figure_colour("fail_text").lower()]
        assert [t[:3] for t in red] == want and all("FAIL" in t for t in red), (fid, red)
    d6, f6 = figs["F6"]
    c = next(ax for ax in f6.axes if ax.get_title(loc="left").startswith("(c)"))
    assert "G7 NOT PASSED (1 network seed, S+)" in c.get_title(loc="left")


def test_no_class_colour_for_a_non_class_series_and_the_network_shapes_are_not_class_markers(figs):
    for fid in ("F5", "F6"):
        for ax in figs[fid][1].axes:
            for ln in ax.lines:
                if to_hex(ln.get_color()).lower() in CLASS_COLOURS and ln.get_marker() not in ("None", "none", "", None):
                    assert ln.get_marker() in CLASS_MARKERS, (fid, ax.get_title(loc="left")[:20], ln.get_marker())
    for k in ("agree", "disagree"):
        assert S.F5_NET_MARKS[k] not in CLASS_MARKERS
    assert not S.is_class_colour(S.get("network_agree").colour) and not S.is_class_colour(S.get("network_disagree").colour)
    p3, p4b = S.get("P3").colour, S.get("P4b").colour
    assert p3 != p4b and not S.is_class_colour(p4b)
    def hue(h):
        import colorsys
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
        return colorsys.rgb_to_hsv(r, g, b)[0]
    assert abs(hue(p3) - hue(p4b)) > 0.1                                    # distinct hues, not two shades of teal


def test_parameters_sentence_lists_the_swept_ranges(built):
    c5, c6 = built["F5"]["caption"], built["F6"]["caption"]
    assert "network.N=1000, 3000, 10000, 30000, swept" in c5 and "noise.sigma=" in c5 and "(checked, not confirmed, G4-C4)" in c5
    assert "path.T_ramp_s=1 to 1000 (13 values), swept" in c6 and "path.I_amp=0.5, 1, 2, swept" in c6


def test_f5_items(built, figs):
    d, fig = figs["F5"]
    cap = built["F5"]["caption"]
    assert ("RB6", "network_fpk_halving_dt") in FG.F5_STRIP and [r["check_id"] for r in d["strip"]][-1] == "network_fpk_halving_dt" and d["strip"][-1]["status"] == "FAIL"
    lines = FG.f5_status_lines(d)
    assert any("RB6 network_fpk_halving_dt is listed because panel (g) draws the network f_pk (UNVERIFIED reading)" in s for s in lines)
    assert FG.F5_RB1_RULE in cap and K.FLAGGED_CLAUSE in cap and "Map 2 has no network runs" in cap
    assert "39 of the 39 drawn network onsets (8.0 to 27.0 s) are earlier than the stored mean-field companion onset 33.698 s" in cap
    assert "the stored minimum duration is 1000 ms at all four N" in cap and "no mean-field duration reference is drawn" in cap and K.DURATION_FLOOR_TEXT in cap
    assert "steps of 2 and 3 cells: uneven spacing" in cap
    axa = next(ax for ax in fig.axes if ax.get_title(loc="left").startswith("(a)"))
    assert FG.F5_LINE_A.replace(" ", "") in axa.get_xlabel().replace("\n", "").replace(" ", "")
    assert sorted(t.get_text() for t in axa.texts if "/" in t.get_text()) == sorted("/".join(c) for c in d["cell_net_class"])
    assert any(getattr(c, "get_hatch", lambda: None)() == S.F5_HATCH["D-none"] for c in axa.collections)       # D-none cells hatched
    d_ax = next(ax for ax in fig.axes if ax.get_title(loc="left").startswith("(d)"))
    assert "below the 203 needed" in d_ax.get_title(loc="left").replace("\n", " ")
    ticks = [t.get_text() for ax in fig.axes for t in ax.get_xticklabels() + ax.get_yticklabels()]
    assert not any("e+" in t for t in ticks)


def test_f6_items(built, figs):
    d, fig = figs["F6"]
    cap = built["F6"]["caption"]
    for s in ("NC1 (primary): the hypoxia path with eta_bar falling by the same amount", "NC2: the full path with I(t) = 0 versus I(t) on (drive off against drive on)", "NC3 (exploratory): inhibition raised while eta_bar falls",
              "any-label bars are hatched (diagonal lines for map 1, dots for map 2)", "not counted for G7 per DL-220 (4)", FG.F6_A10_SENTENCE):
        assert s in cap, s
    assert "S-rel 1 of 10, 1 of 10, 1 of 10, 1 of 10, 2 of 10 at T_ramp 10, 178, 316, 562, 1000 s (6 of 130 runs)" in cap
    assert "is not found under P3 only" not in cap and "the surge is not confined to P3" in cap
    axb = next(ax for ax in fig.axes if ax.get_title(loc="left").startswith("(b)"))
    labs = [t.get_text().split("\n")[0] for t in axb.get_yticklabels()]
    assert labs == ["NC1 mean field, mode D (noise-free)", "NC1 mean field + noise, 10 seeds (mode N)", "NC2 drive off (I = 0)", "NC2 drive on (I = 1)", "NC3 (exploratory)"]
    assert [t.get_text() for t in axb.get_xticklabels()][-1] == "1000"
    axc = next(ax for ax in fig.axes if ax.get_title(loc="left").startswith("(c)"))
    assert any(t.get_text().startswith("network N = 1e4, 1 seed") for t in axc.get_xticklabels())
    ax_d = next(ax for ax in fig.axes if ax.get_title(loc="left").startswith("(d)"))
    assert len(ax_d.get_lines()) == 6 and len(ax_d.collections) >= 25                          # six series lines; scatter overlays: the S6 P2 references and one class mark per point
    assert not any(t.get_text().startswith("coincide") for ax in fig.axes for t in ax.texts)     # the coincidence note is outside the plots
    assert any("(e) f_pk: rows with identical stored values coincide" in a.get_text() for ax in fig.axes for a in ax.texts)
