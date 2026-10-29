"""MS13 13k (DL-482): the literal colours and marks of FS3 and F6 are style.py keys. They read the stored results under results/ (git-ignored) and skip if absent.
Tolerances: every comparison is exact (set equality, SHA-256, source-text scan)."""
import inspect
import re

import pytest

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import style as S

ROOT = C.repo_root()
RES = ROOT / "results"
have = all((RES / p).is_file() for p in FG.FS3_INPUTS + FG.F6_INPUTS)
# DL-481 (F6) and the FS3 digest of the stored data other than the key "strip" (DL-482: the strip gains the RB1 FAIL rows, the other 40 keys are unchanged)
F6_DIGEST_DL481 = "4dafe2ab2f5ee3c2b505f82d4f50a3a8b96a9bb1c9cdfb5379b7a3e6f7e2c532"


def test_figure_colour_keys_are_exact_and_an_unknown_key_raises():
    assert set(S.FIGURE_COLOURS) == {"bar_edge", "bar_edge_dark", "range_line", "fail_text", "text_dark", "gate_line", "subgrid_bar", "label_box", "open_fill", "map1_fill", "map2_fill"}
    assert set(S.FIGURE_HATCHES) == {"map1_any", "map2_any"} and S.figure_hatch("map1_any") != S.figure_hatch("map2_any")
    assert S.figure_colour("map1_fill") == "#6a6a6a" and S.figure_colour("map2_fill") == "#b5b5b5"          # the F6 map greys of the 13j drafts
    with pytest.raises(S.StyleError, match="no figure colour"):
        S.figure_colour("nope")
    with pytest.raises(S.StyleError, match="no figure hatch"):
        S.figure_hatch("nope")
    assert all(re.fullmatch(r"#[0-9a-f]{6}", c) for c in S.FIGURE_COLOURS.values())                              # plain colours (edges, text, fills), not marks: they may repeat a table colour


def test_fs3_median_mark_is_unique_and_the_fs5_star_keeps_its_single_meaning():
    m = S.diagram_mark("fs3_median")
    others = [v.marker for k, v in S.DIAGRAM_MARKS.items() if k != "fs3_median" and v.marker is not None]
    assert m.marker not in others and m.marker not in {s.marker for s in S.STYLE.values()}                 # exact: no other diagram, class, path, control or source mark has this shape
    assert m.marker != S.diagram_mark("fs5_pt").marker
    src = inspect.getsource(FG._draw_FS3)
    assert 'diagram_mark("fs3_median")' in src and "fs5_pt" not in src                                  # FS3 uses the new key, not the star
    assert 'diagram_mark("fs5_pt")' in inspect.getsource(FG._draw_FS5)                                    # FS5 still uses its star


def test_no_literal_colour_hatch_or_point_size_is_left_in_the_fs3_and_f6_drawing_code():
    for fn in (FG._fs3_stack, FG._draw_FS3, FG._draw_F6):
        src = inspect.getsource(fn)
        assert not re.findall(r"#[0-9a-fA-F]{3,8}\b", src), fn.__name__                                  # exact: no hex colour literal
        assert not re.findall(r"hatch=[\"']", src), fn.__name__                                          # no hatch literal
        assert not re.findall(r"\bms=[0-9]", src), fn.__name__                                           # no point-size literal


@pytest.mark.skipif(not have, reason="stored FS3 and F6 inputs under results/ are absent")
def test_f6_digest_equals_dl481_and_the_fs3_strip_is_the_rb1_and_rb2_fail_rows():
    assert FG.drawn_data_sha256(FG.prepare_F6(FG.load_F6())) == F6_DIGEST_DL481                          # exact
    d = FG.prepare_FS3(FG.load_FS3())
    assert [(r["rb_id"], r["check_id"]) for r in d["strip"]] == [("RB1", "headline_10s"), ("RB1", "headline_120s"), ("RB1", "cells_30s"), ("RB1", "overall"),
                                                                 ("RB2", "noisy_subgrid_agreement"), ("RB2", "headline_class_kept_1.0_sigma")]
    assert all(r["status"] == "FAIL" for r in d["strip"])
    d6 = FG.prepare_F6(FG.load_F6())
    assert [r["rb_id"] for r in d6["strip"]] == ["G7"] and d6["rb7_rows"] == 0


@pytest.mark.skipif(not have, reason="stored FS3 and F6 inputs under results/ are absent")
def test_captions_state_the_rulings_of_13k():
    cap6 = " ".join(FG.f6_caption_notes(FG.prepare_F6(FG.load_F6())))
    assert "RB7" in cap6 and "no row in the A11 table" in cap6 and "J_exit,static" in cap6 and "not drawn" in cap6 and "a flag, not a demonstrated cause" in cap6
    cap3 = " ".join(FG.fs3_caption_notes(FG.prepare_FS3(FG.load_FS3())))
    assert "NOT EVALUABLE" in cap3 and "DL-322" in cap3 and "G4-C5" in cap3 and "cannot be identified" in cap3 and "not drawn" in cap3 and "RB1 rows" in cap3
