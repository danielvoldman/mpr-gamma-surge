"""MS13 13r-3a: per-figure tests of F1, F2 and F3 for the 13r items (DL-516, DL-517, DL-518). Reads the stored results under results/ (skipped if absent); builds go to a temporary
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
_need = list(FG.F1_INPUTS) + list(FG.F2_INPUTS) + list(FG.F3_INPUTS)
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in _need), reason="stored F1 to F3 inputs under results/ are absent")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs13r3a")
    return {"F1": FG.make_F1(out_dir=out / "F1"), "F2": FG.make_F2(out_dir=out / "F2"), "F3": FG.make_F3(out_dir=out / "F3")}


@pytest.fixture(scope="module")
def figs():
    import matplotlib.pyplot as plt
    crit, _ = F.K.load_frozen_criteria(ROOT)
    d1 = FG.prepare_F1(FG.load_F1(), crit)
    d2 = FG.prepare_F2(FG.load_F2())
    d3 = FG.prepare_F3(FG.load_F3())
    out = {"F1": (d1, FG._draw_F1(d1, True)), "F2": (d2, FG._draw_F2(d2, True, FG.strip_lines(d2))), "F3": (d3, FG._draw_F3(d3, True, FG.strip_lines(d3)))}
    yield out
    for _d, fig in out.values():
        plt.close(fig)


def _sentence1(caption: str, fid: str) -> str:
    body = caption[len(fid) + 2:]
    return body.split(". ")[0]


def test_sentence_one_contains_the_main_failure(built):
    for fid, needles in (("F1", FG.F1_MAIN_FAILURES), ("F2", FG.F2_MAIN_FAILURES), ("F3", FG.F3_MAIN_FAILURES)):
        first = _sentence1(built[fid]["caption"], fid)
        for n in needles:
            assert n in first, (fid, n)
    assert "0 of 3 seeds match the mean-field class D-tr (all 3 are S-sus" in _sentence1(built["F1"]["caption"], "F1")


def test_class_key_is_in_f1_and_absent_where_no_class_is_drawn(built):
    assert K.class_key_line("ND", agree=True) in built["F1"]["caption"]
    assert K.classifier_line(F.K.load_frozen_criteria(ROOT)[0]) in built["F1"]["caption"]
    for fid in ("F2", "F3"):
        assert "Class key" not in built[fid]["caption"]


def test_fail_is_in_the_title_of_every_panel_that_shows_a_fail(figs):
    from figlayout import red_titles_without_fail
    d1, f1 = figs["F1"]
    assert red_titles_without_fail(f1) == []
    red = [ax.get_title(loc="left") for ax in f1.axes if to_hex(ax._left_title.get_color()).lower() == S.figure_colour("fail_text").lower()]
    assert len(red) == 2 and all("(d)" in t or "(f)" in t for t in red) and all("RB1 FAIL" in t for t in red)
    for fid in ("F2", "F3"):
        assert red_titles_without_fail(figs[fid][1]) == []
    f3 = figs["F3"][1]
    assert any(t.get_text() == "RB9(b)\nFAIL" and to_hex(t.get_color()).lower() == S.figure_colour("fail_text").lower() for ax in f3.axes for t in ax.texts)


def test_f1_in_panel_line_and_j_ramp_marks(figs):
    d1, f1 = figs["F1"]
    texts = [t.get_text() for ax in f1.axes for t in ax.texts]
    line = "network class S-sus, mean field D-tr; 0 of 3 seeds agree (RB1 FAIL)"
    assert sum(t.startswith(line) for t in texts) == 2
    assert FG.f1_net_line(d1) == line
    assert "J ramp starts 35 s (derived)" in texts and "J ramp ends 155 s (derived)" in texts
    assert d1["path_J_lag_frac"] == 0.25 and d1["path_J_T_frac"] == 1.0
    assert any("raw crossings" in t for t in texts)
    assert any(t.endswith("percent) lie below the shared dB range (drawn in its lowest colour)") for t in texts)


def test_f1_caption_states_the_stored_crossings_and_onsets(built):
    cap = built["F1"]["caption"]
    for s in ("50.170 to 50.924 s against the mean-field onset 58.698 s", "network classifier onset 12.0 s", "by the pre-registered classes the network does not reproduce the mean-field class",
              "no claim about the visual shape of the traces", "MS11-C2; RB6 network f_pk FAIL, FS4", "consequence (2): the network disagrees with the mean field in 2 or more of the 4 map cells"):
        assert s in cap, s
    assert "all 3 S-sus (3 of 3)" not in cap and "{'" not in cap


def test_parameters_sentence_lists_swept_ranges(built):
    c3 = built["F3"]["caption"]
    assert "model.tau_d_ms=1 to 50 (9 values), swept" in c3 and "model.Delta=0.05, 0.1, 0.3, swept" in c3
    c2 = built["F2"]["caption"]
    assert "model.eta_bar=0.896046 to 6.89605 (61 values), swept" in c2
    assert "path.T_ramp_s=120.0" in built["F1"]["caption"] and "swept" not in built["F1"]["caption"].split("Claim limits:")[0].split("Parameters:")[1].split("The full parameter list")[0]


def test_f2_marks_not_drawn_values_and_the_bounded_statements(built):
    cap = built["F2"]["caption"]
    assert "(2.8975; not drawn)" in cap and "percent (stored; not drawn)" in cap and "(not drawn)).\n" not in cap
    assert "1.84e-3 (not drawn)" in cap and "supercritical Hopf bifurcation (plan:" in cap
    assert "mean V of non-refractory neurons" in cap and "information only, no criterion" in cap


def test_f3_caption_states_j_the_25_hz_rule_and_the_coincident_paths(built):
    cap = built["F3"]["caption"]
    assert "fixed J = -21 (the stored A6 record; the A6 J slices are not drawn)" in cap
    assert K.coincide_note(["P1", "P2", "P3", "P5"], "eta_bar, Delta and tau_d") in cap
    assert FG.F3_RULE_25HZ in cap and "DL-131" in cap and "DL-133" in cap
    assert "mean_field = tri up" not in cap and "Symbols: P1 = pentagon; P2 = hexagon; P3 = rotated hexagon; P4a = plus (filled); P4b = cross (filled); P5 = octagon." in cap


def test_no_class_colour_is_used_for_a_non_class_series_in_f2_and_f3(figs):
    classes = {v[0].lower() for v in S._TABLE["class"].values()}
    for fid in ("F2", "F3"):
        for ax in figs[fid][1].axes:
            for ln in ax.lines:
                if ln.get_marker() in ("None", "none", "", None) and ln.get_linestyle() in ("None", "none", ""):
                    continue
                assert to_hex(ln.get_color()).lower() not in classes, (fid, ln.get_label())
    for k in FG.F1_SEED_KEYS:
        assert not S.is_class_colour(S.diagram_mark(k).colour)
    d2 = figs["F2"][0]
    net = [ln for ax in figs["F2"][1].axes for ln in ax.lines if ln.get_label().startswith("S4 network")]
    assert net and all(to_hex(ln.get_color()).lower() == S.SOURCE_COLOURS["network"].lower() for ln in net)
    assert d2["mf_param"].size == 122
