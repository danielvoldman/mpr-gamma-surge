"""MS13 13r-3b: per-figure tests of F4 and the F1 coincide note (DL-524, DL-525, DL-526). Reads the stored results under results/ (skipped if absent); builds go to a temporary
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
_need = list(FG.F4_INPUTS) + list(FG.F1_INPUTS)
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in _need), reason="stored F1 and F4 inputs under results/ are absent")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs13r3b")
    return {"F4": FG.make_F4(out_dir=out / "F4"), "F1": FG.make_F1(out_dir=out / "F1")}


@pytest.fixture(scope="module")
def f4():
    import matplotlib.pyplot as plt
    d = FG.prepare_F4(FG.load_F4())
    fig = FG._draw_F4(d, True)
    yield d, fig
    plt.close(fig)


def _sentence1(caption: str) -> str:
    return caption[len("F4. "):].split(". ")[0]


def test_sentence_one_contains_every_named_failure_and_the_g6_ruling(built):
    first = _sentence1(built["F4"]["caption"])
    for n in FG.F4_MAIN_FAILURES:
        assert n in first, n
    assert "PASSED WITH DEPARTURES (DL-208)" in first and "RB3(a) 0 of 6" in first and "181 ms" in first and "RB2 FAIL" in first and "RB3(b) DOES NOT MEET" in first


def test_class_key_and_classifier_line_are_in_the_caption(built):
    cap = built["F4"]["caption"]
    assert K.class_key_line("ND", agree=True) in cap
    assert K.classifier_line(F.K.load_frozen_criteria(ROOT)[0]) in cap


def test_fail_is_in_every_red_title(f4):
    from figlayout import red_titles_without_fail
    d, fig = f4
    assert red_titles_without_fail(fig) == []
    red = [ax.get_title(loc="left") for ax in fig.axes if to_hex(ax._left_title.get_color()).lower() == S.figure_colour("fail_text").lower()]
    assert len(red) == 3 and [t[:3] for t in red] == ["(a)", "(h)", "(j)"] and all("FAIL" in t for t in red)


def test_the_minus_1_5_statement_is_on_panel_j_and_in_the_caption_because_v1_confirmed(built, f4):
    d, fig = f4
    assert K.D2_STATEMENT in built["F4"]["caption"]
    texts = [" ".join(t.get_text().split()) for ax in fig.axes for t in ax.texts]
    assert K.D2_STATEMENT in texts
    raw = FG.load_F4()
    a7 = raw["a7"]
    sel = a7[np.isclose(a7["delay_eta"].astype(float), -1.5, atol=1e-9)]
    t_on = np.array([raw["ramp"][r][0] for r in sel["run_id"]])
    assert len(sel) == 84 and np.all(sel["onset_s"].astype(float).to_numpy() == t_on)            # V1 (DL-512): every such onset is at the ramp start


def test_seed_counts_are_stated_for_every_noise_bar(built, f4):
    d, fig = f4
    got = []
    for ax in fig.axes:
        labels = [t.get_text() for sx in ax.child_axes for t in sx.get_xticklabels()]
        if labels:
            got.append(labels)
    keys = ("noise_peak_power_abs", "noise_peak_power_rel", "noise_f_pk_hz", "noise_duration_s", "noise_delay_eta_cross")
    want = [[str(int(n)) for n in FG.noise_counts(d[k])] for k in keys]
    assert got == want and all(len(g) == 13 for g in got)
    cap = built["F4"]["caption"]
    assert K.NOISE_BAR_TEXT in cap and "seeds counted" in cap


def test_no_class_colour_or_marker_is_used_for_a_non_class_series(f4):
    d, fig = f4
    classes = {v[0].lower() for v in S._TABLE["class"].values()}
    allowed_markers = {S.get("D-none").marker}
    for ax in fig.axes:
        for ln in ax.lines:
            if ln.get_marker() in ("None", "none", "", None) and ln.get_linestyle() in ("None", "none", ""):
                continue
            if to_hex(ln.get_color()).lower() in classes:
                assert ln.get_marker() in allowed_markers, (ax.get_title(loc="left"), ln.get_marker())
    class_markers = {S.get(k).marker for k in S.CLASS_KEYS}
    for lvl in range(3):
        assert S.diagram_mark(f"fs4_l{lvl}").marker not in class_markers
    assert S.F4_MARKS["hold_colour"].lower() not in classes and S.F4_MARKS["hold_colour"].lower() not in {S.get(p).colour.lower() for p in S.PATH_KEYS}
    assert S.F4_MARKS["nocross"] is not S.F4_MARKS["untestable"] and S.F4_MARKS["nocross_colour"].lower() not in classes


def test_parameters_sentence_lists_the_swept_ranges_and_the_noise_tag(built):
    cap = built["F4"]["caption"]
    assert "path.T_ramp_s=" in cap and "(13 values), swept" in cap
    assert "path.name=path_eta, path_hypoxia, path_updown, swept" in cap and "path.profile=linear, sigmoid, swept" in cap
    assert "noise.sigma=0.0624 (checked, not confirmed, G4-C4)" in cap


def test_rings_carry_the_stored_errors_and_the_untestable_runs_have_their_own_ring(f4):
    d, fig = f4
    axa = next(ax for ax in fig.axes if ax.get_title(loc="left").startswith("(a)"))
    axg = next(ax for ax in fig.axes if ax.get_title(loc="left").startswith("(g)"))
    assert [t.get_text() for t in axa.texts if t.get_text() in ("25.1",)] == ["25.1"]
    assert sorted(t.get_text() for t in axg.texts if t.get_text()[0].isdigit()) == ["12.7", "20.6", "33.1", "4.4", "7.6"]
    untest = [ln for ln in axa.lines if ln.get_marker() is S.F4_MARKS["untestable"] or (not isinstance(ln.get_marker(), str) and np.array_equal(np.asarray(ln.get_marker()), np.asarray(S.F4_MARKS["untestable"])))]
    assert sum(len(ln.get_xdata()) for ln in untest) == 3
    assert int(d["p1_linear_eta_const"].sum() + d["p1_sigmoid_eta_const"].sum()) == 3


def test_coincidence_and_reading_notes_are_computed_from_the_stored_arrays(f4, built):
    d, fig = f4
    eq = {(a, b): n for a, b, n in FG.f4_equal_runs(d, "delay_eta_cross")}
    assert eq[("P1 linear", "P5 linear")] == 11 and eq[("P1 sigmoid", "P5 sigmoid")] == 11 and eq[("P1 linear", "P1 sigmoid")] == 2
    assert dict(FG.f4_reading_equal(d)) == {"P1 linear": 8, "P1 sigmoid": 3, "P2 linear": 13, "P2 sigmoid": 13, "P5 linear": 13, "P5 sigmoid": 13}
    assert "P1 linear = P5 linear at 11 of 13 T_ramp" in built["F4"]["caption"]


def test_v2_v8_and_the_strip_only_sentence_and_the_k_l_panels(built, f4):
    d, fig = f4
    cap = built["F4"]["caption"]
    assert K.DURATION_FLOOR_TEXT in cap and "no scaling law" in cap and "Panel (l) has a zero line" in cap
    lines = FG.f4_status_lines(d)
    assert any("F4 draws no network run (ruled in 13k); see FS4" in s for s in lines)
    assert any("RB3(c) and RB2 at 0.5 and 2 sigma are in this status block only" in s for s in lines)
    axl = next(ax for ax in fig.axes if ax.get_title(loc="left").startswith("(l)"))
    assert axl.get_ylim()[1] > 0 > axl.get_ylim()[0] and any(float(np.max(np.abs(ln.get_ydata()))) == 0.0 and len(ln.get_ydata()) == 2 for ln in axl.lines)


def test_f1_caption_has_the_g7_coincide_note(built):
    cap = built["F1"]["caption"]
    assert K.coincide_note(["seed 0", "seed 1", "seed 2"], "in their stored classifier onset, 12.000 s") in cap
    assert "50.170 to 50.924 s, stored, not equal" in cap
