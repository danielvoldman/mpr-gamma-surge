"""MS13 13r-2: tests of the shared code for G1 to G12 (DL-511, DL-512, DL-513). Exact comparisons; nothing is simulated, no figure is rebuilt, nothing reads results/ except where the
A11 table is named. The per-figure application of these helpers is tested in 13r-3."""
import ast
import re
from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import captions as K
from mprsurge.plotting import figures as FG
from mprsurge.plotting import style as S

ROOT = C.repo_root()
PLAN = (ROOT / "docs" / "plan.md").read_text(encoding="utf-8")


def _unescape(t: str) -> str:
    return t.replace("\\[", "[").replace("\\]", "]")


# ---- G1: the class key is verbatim from plan Table 2.1 -----------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("text", [K.TABLE_2_1_MODE_N, K.TABLE_2_1_MODE_D, K.TABLE_2_1_SURGE, K.TABLE_2_1_AGREE])
def test_class_key_sentences_occur_verbatim_in_plan_table_2_1(text):
    assert text in _unescape(PLAN)


def test_class_key_line_composition():
    both = K.class_key_line("ND")
    assert both.startswith("Class key (plan Table 2.1): ")
    assert K.TABLE_2_1_MODE_N in both and K.TABLE_2_1_MODE_D in both and K.TABLE_2_1_SURGE in both and K.TABLE_2_1_AGREE not in both
    assert K.TABLE_2_1_MODE_N not in K.class_key_line("D") and K.TABLE_2_1_MODE_D not in K.class_key_line("N")
    assert K.TABLE_2_1_AGREE in K.class_key_line("ND", agree=True)
    for bad in ("", "X", "NX"):
        with pytest.raises(K.CaptionError):
            K.class_key_line(bad)


def _caption(**kw):
    base = dict(take_home="Sentence one names RB9(b) FAIL. Second sentence.", claim_limit_ids=["MS11-C7"])
    base.update(kw)
    return K.build_caption("F9", **base)


def test_caption_carries_class_key_and_classifier_line_between_symbols_and_notes():
    t = _caption(class_key=K.class_key_line("D"), classifier_line="Classifier line.", notes=("A note.",)).text
    assert t.index("Class key") < t.index("Classifier line.") < t.index("A note.") < t.index("Claim limits:")


# ---- G3: sentence 1 contains the main failure ---------------------------------------------------------------------------------------------------------------------

def test_main_failure_must_be_in_sentence_one():
    assert _caption(main_failures=("RB9(b) FAIL",)).text.startswith("F9. Sentence one names RB9(b) FAIL.")
    with pytest.raises(K.CaptionError):
        _caption(main_failures=("RB3(a) 0 of 6",))
    with pytest.raises(K.CaptionError):
        _caption(main_failures=("Second sentence",))                      # present, but not in sentence 1
    n = "58.698 s"
    assert _caption(take_home=f"Onset {n} fails RB6. Next.", main_failures=("RB6",)).text.startswith("F9. Onset 58.698 s fails RB6.")


# ---- G5: parameters sentence --------------------------------------------------------------------------------------------------------------------------------------

def test_swept_parameters_are_printed_as_range_or_list_and_noise_sigma_is_tagged():
    rows = [{"key": "path.T_ramp_s", "value": v, "panel": "a"} for v in (1.0, 2.0, 4.0, 8.0, 16.0, 32.0)] + [{"key": "noise.sigma", "value": 0.0624, "panel": "a"}]
    s = K.parameter_string(rows, swept={"path.T_ramp_s": [1.0, 2.0, 4.0, 8.0, 16.0, 32.0]})
    assert "path.T_ramp_s=1 to 32 (6 values), swept" in s
    assert "noise.sigma=0.0624 (checked, not confirmed, G4-C4)" in s
    assert K.sweep_text([3, 5, 13]) == "3, 5, 13" and K.sweep_text([1e3, 3e3, 1e4, 3e4]) == "1000, 3000, 10000, 30000"
    assert K.sweep_text([1e-4, 2.5e-4, 5e-4, 1e-3]) == "1e-4, 2.5e-4, 5e-4, 0.001"
    assert K.sweep_text(range(1, 14)) == "1 to 13 (13 values)"
    with pytest.raises(K.CaptionError):
        K.sweep_text([])


def test_one_number_format_has_no_plus_or_padded_exponent():
    for x, want in ((1000.0, "1000"), (1e5, "1e5"), (2.5e-4, "2.5e-4"), (1e-4, "1e-4"), (1e-3, "0.001"), (3e6, "3e6"), (1e-5, "1e-5"), (0.0, "0"), (0.0624, "0.0624")):
        assert K.number_text(x) == want, x
    assert "e+" not in "".join(K.number_text(x) for x in (1e3, 1e5, 1e9, 1e-9, 12345678.0))


# ---- G4, G7, G8, G11 ------------------------------------------------------------------------------------------------------------------------------------------------

def test_pinned_coincide_not_drawn_texts():
    assert K.PINNED_UNDETERMINED == "pinned value, cause not determined (UNVERIFIED)"
    assert K.not_drawn("r amplitude 0.1 to 0.2") == "r amplitude 0.1 to 0.2 (not drawn)"
    assert K.coincide_note(["P1 linear", "P5 linear"]).startswith("P1 linear and P5 linear coincide")
    assert K.coincide_note(["a", "b", "c"]).startswith("a, b and c coincide")
    with pytest.raises(K.CaptionError):
        K.coincide_note(["only"])


def test_classifier_line_is_read_from_the_frozen_criteria():
    from mprsurge import criteria
    crit, _ = criteria.load_frozen_criteria(ROOT)
    line = K.classifier_line(crit)
    c = crit["classifier"]
    assert c["window_rule"]["value"] in line and c["spectrogram_taper"]["value"] in line
    assert "gamma band 25 to 100 Hz" in line and "total band 1 to 150 Hz" in line and "minimum 10 cycles" in line and "threshold 0.1 x A_ref" in line
    with pytest.raises(K.CaptionError):
        K.classifier_line({"classifier": {}})


def test_shared_statements_quoted_from_the_logged_verifications():
    assert "saturated" in K.D2_STATEMENT and "-1.5" in K.D2_STATEMENT and K.D2_STATEMENT.startswith("classifier onset at or before the ramp start")
    assert "median of the seeds with a value" in K.NOISE_BAR_TEXT and "number of seeds counted" in K.NOISE_BAR_TEXT
    assert "1.0 s" in K.DURATION_FLOOR_TEXT and "criteria O2_episode_end" in K.DURATION_FLOOR_TEXT
    assert K.FLAGGED_CLAUSE == "as worded in the MS9 limit; not the final classes drawn in (f)"


# ---- G2: failures visible, no small text --------------------------------------------------------------------------------------------------------------------------------

def test_fail_title_adds_the_word_and_the_red_colour():
    assert S.fail_title("(h) noise band", True) == ("(h) noise band: FAIL", "fail_text")
    assert S.fail_title("(h) noise band: RB2 FAIL", True) == ("(h) noise band: RB2 FAIL", "fail_text")
    assert S.fail_title("(c) fine", False) == ("(c) fine", "text_dark")
    assert S.RED_TITLE_RULE == K.RED_TITLE_NOTE


def test_titles_missing_fail_checker_on_a_synthetic_figure():
    import matplotlib.pyplot as plt
    from figlayout import red_titles_without_fail
    fig, (a, b, c) = plt.subplots(1, 3)
    a.set_title(*S.fail_title("one", True)[:1], color=S.figure_colour("fail_text"), loc="left")
    b.set_title("two", color=S.figure_colour("fail_text"), loc="left")                      # red without FAIL
    c.set_title("three", color=S.figure_colour("text_dark"), loc="left")
    assert red_titles_without_fail(fig) == ["two"]
    plt.close(fig)


def test_text_size_table_has_nothing_below_the_tick_size():
    assert S.MIN_TEXT_PT == S.TEXT_SIZES["tick"] == 5.0
    assert min(S.TEXT_SIZES.values()) >= S.TEXT_SIZES["tick"]


def test_style_text_raises_every_smaller_text_to_the_tick_size():
    import matplotlib.pyplot as plt
    from matplotlib.text import Text
    fig, ax = plt.subplots(constrained_layout=True)
    ax.plot([0, 1], [0, 1])
    ax.text(0.5, 0.5, "tiny", fontsize=3.0)
    ax.annotate("tinier", (0.1, 0.1), fontsize=2.0)
    ax.set_title("title", fontsize=3.5)
    fig.text(0.1, 0.9, "figure text", fontsize=4.0)
    FG._style_text(fig, "")
    small = [(t.get_text(), t.get_fontsize()) for t in fig.findobj(Text) if t.get_text() and t.get_visible() and t.get_fontsize() < S.MIN_TEXT_PT]
    assert small == []
    plt.close(fig)


def test_no_literal_font_size_below_the_tick_size_in_the_plotting_code():
    bad = []
    for path in sorted((ROOT / "src" / "mprsurge" / "plotting").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.keyword) and node.arg in ("fontsize", "size", "labelsize") and isinstance(node.value, ast.Constant) and isinstance(node.value.value, (int, float)):
                if node.value.value < S.MIN_TEXT_PT:
                    bad.append((path.name, node.value.lineno, node.value.value))
    assert bad == []


def test_fail_lines_of_a_status_block_are_bold_and_the_rest_is_not():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(constrained_layout=True)
    ax.axis("off")
    n = FG.status_block(ax, ["RB2 x: FAIL (7 of 10; threshold >= 8 of 10)", "RB4 y: PASS", "a long line without the word " * 12 + " FAIL at the end"], size=5.0, width=60)
    assert n >= 4
    weights = {t.get_text(): t.get_fontweight() for t in ax.texts}
    assert weights["RB2 x: FAIL (7 of 10; threshold >= 8 of 10)"] == "bold" and weights["RB4 y: PASS"] == "normal"
    long_pieces = [t for t in ax.texts if t.get_text() not in ("RB2 x: FAIL (7 of 10; threshold >= 8 of 10)", "RB4 y: PASS")]
    assert len(long_pieces) >= 2 and all(t.get_fontweight() == "bold" for t in long_pieces)             # a wrapped FAIL line is bold on every piece
    plt.close(fig)


def test_strip_line_explains_blanks_from_the_table_columns():
    full = FG.strip_line({"rb_id": "RB2", "check_id": "noisy_subgrid_agreement", "status": "FAIL", "value": "97 of 225 cells (43.1 percent)", "threshold": "203 of 225 (90 percent, D24)"})
    assert full == "RB2 noisy_subgrid_agreement: FAIL (97 of 225 cells (43.1 percent); threshold 203 of 225 (90 percent, D24)) - shown, not dropped"
    blank = FG.strip_line({"rb_id": "RB3", "check_id": "b_classifier_onset", "status": "FAIL", "value": "", "threshold": ""})
    assert "value blank in the stored table" in blank and "threshold blank in the stored table" in blank
    overall = FG.strip_line({"rb_id": "RB1", "check_id": "overall", "status": "FAIL", "value": "", "threshold": ""})
    assert "verdict over its three parts" in overall
    failed = FG.strip_line({"rb_id": "RB2", "check_id": "headline_class_kept_1.0_sigma", "status": "FAIL", "value": "7 of 10 (0 failed)", "threshold": ">= 8 of 10"})
    assert K.FAILED_RUNS_NOTE in failed


# ---- G6: no class colour for a non-class series -----------------------------------------------------------------------------------------------------------------------

def _hexes(obj):
    if isinstance(obj, str):
        if re.fullmatch(r"#[0-9a-fA-F]{6}", obj):
            yield obj.lower()
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _hexes(v)
    elif isinstance(obj, (tuple, list)):
        for v in obj:
            yield from _hexes(v)


def test_no_class_colour_is_used_for_a_non_class_series():
    classes = {v[0].lower() for v in S._TABLE["class"].values()}
    for fam in ("path", "control", "source"):
        for key, entry in S._TABLE[fam].items():
            assert entry[0].lower() not in classes, (fam, key)
    for name in ("FIGURE_COLOURS", "SOURCE_COLOURS", "F4_MARKS", "F5_COLOURS", "FS_COLOURS", "F1_SCHEMATIC", "F6_MARKS"):
        assert not (set(_hexes(getattr(S, name))) & classes), name
    for key, m in S.DIAGRAM_MARKS.items():
        assert m.colour.lower() not in classes, key
    for kind in S.SERIES_MARK_KEYS:
        for i in range(3):
            assert not S.is_class_colour(S.series_mark(kind, i).colour)
    assert S.SOURCE_COLOURS["mean_field"] == S.get("mean_field").colour
    with pytest.raises(S.StyleError):
        S.series_mark("seed", 3)
    with pytest.raises(S.StyleError):
        S.series_mark("variant", 0)


def test_series_marks_are_not_class_markers():
    class_markers = {S.get(k).marker for k in S.CLASS_KEYS}
    for kind in S.SERIES_MARK_KEYS:
        for i in range(3):
            assert S.series_mark(kind, i).marker not in class_markers


# ---- G9, G10, G12 ---------------------------------------------------------------------------------------------------------------------------------------------------------

def test_plain_labels_and_codes():
    assert S.PATH_PLAIN["P2"] == "P2 (hypoxia-like path)" and "hypoxia" not in S.PATH_PLAIN["P1"]
    for k in ("eta_bar", "tau_d", "Delta", "J", "eps", "T_ramp"):
        assert k in S.PLAIN_LABELS
    assert "(1, -20, 0.05)" in S.INTERNAL_CODES["ref_ceni"] and "(4, -21, 0.3)" in S.INTERNAL_CODES["ref_devalle"]
    for text in S.INTERNAL_CODES.values():
        key = text.split(":")[0]
        assert key in PLAN


def test_on_panel_pointer_is_short_and_comes_from_the_label_table():
    from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS as CL
    p = FG.claim_pointer("G4-C1")
    assert p.startswith("claim limit G4-C1: ") and CL["G4-C1"][0] in p and len(p) <= 160
    with pytest.raises(K.CaptionError):
        FG.claim_pointer("NOT-A-LIMIT")


def test_footers_of_f1_to_f6_cite_the_new_rulings_and_the_fs_footers_do_not_yet():
    for fid in ("F1", "F2", "F3", "F4", "F5", "F6"):
        assert FG.RULED_DL[fid][-2:] == ("DL-511", "DL-512"), fid
        assert "DL-511, DL-512" in FG.draft_footer(fid) and "DL-511, DL-512" in FG.strip_heading(fid)
    for fid in ("FS1", "FS2", "FS3", "FS4", "FS5"):
        assert "DL-511" not in FG.RULED_DL[fid], fid                    # 13s


def test_noise_bar_counts_are_the_number_of_seeds_with_a_value():
    import numpy as np
    v = np.array([[1.0, np.nan, 3.0], [np.nan, np.nan, np.nan], [1.0, 2.0, 3.0]])
    assert FG.noise_counts(v).tolist() == [2, 0, 3]
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    FG._f4_noise(ax, {"noise_eps": np.array([1.0, 2.0, 3.0]), "k": v}, "k")
    fig.canvas.draw()
    assert [t.get_text() for sx in ax.child_axes for t in sx.get_xticklabels()] == ["2", "0", "3"]
    plt.close(fig)
