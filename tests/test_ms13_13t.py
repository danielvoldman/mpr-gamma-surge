"""MS13 13t-1 (DL-545, DL-546, DL-547): tests of the journal export (mode="journal") of F1, F3 and F5, of the collision checker (plotting/collide.py) and of the colour, font and
file checks (plotting/jchecks.py). They read the stored results under results/ (git-ignored) and the stored draft figures under figures/ (git-ignored) and skip if those are absent.
Builds go to a temporary directory, never to figures/. No data assertion of an earlier test changes."""
import hashlib
import json
import re
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import captions as CAP
from mprsurge.plotting import collide as CO
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jchecks as JC
from mprsurge.plotting import journal as J
from mprsurge.plotting import plain as PL

ROOT = C.repo_root()
RES = ROOT / "results"
PILOT = ("F1", "F3", "F5")
INPUTS = {"F1": FG.F1_INPUTS, "F3": FG.F3_INPUTS, "F5": FG.F5_INPUTS}
DRAFT_DIGEST_FILES = {f: ROOT / "figures" / f / f"{f}_drawn_data_sha256.txt" for f in PILOT}
needs = pytest.mark.skipif(not all((RES / p).is_file() for f in PILOT for p in INPUTS[f]) or not all(p.is_file() for p in DRAFT_DIGEST_FILES.values()),
                           reason="stored F1, F3 and F5 inputs under results/ or the stored draft figures are absent")
STRIP = {"F1": FG.f1_strip_lines, "F3": FG.strip_lines, "F5": FG.f5_strip_lines}
MAIN = {"F1": FG.F1_MAIN_FAILURES, "F3": FG.F3_MAIN_FAILURES, "F5": FG.F5_MAIN_FAILURES}


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _draft_files(fid):
    return sorted(p for p in (ROOT / "figures" / fid).glob("*") if p.is_file())


@pytest.fixture(scope="module")
def cfg():
    return J.load_config(ROOT)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """The three journal builds in a temporary directory, with the SHA-256 of the draft files before and after."""
    base = tmp_path_factory.mktemp("journal13t")
    before = {f: {p.name: _sha(p) for p in _draft_files(f)} for f in PILOT}
    out = {f: getattr(FG, f"make_{f}")(mode="journal", out_dir=base / "journal" / f) for f in PILOT}
    after = {f: {p.name: _sha(p) for p in _draft_files(f)} for f in PILOT}
    return {"base": base, "out": out, "before": before, "after": after}


@pytest.fixture(scope="module")
def figs():
    """(fig, d, cfg) of the journal figure objects (inside the journal rc settings) for the checks that need the rendered artists."""
    res = {}
    for f in PILOT:
        c = FG.journal_figure(f, close=False)
        res[f] = c.__enter__()
        c.__exit__(None, None, None)                                 # the rc settings are not left open between tests; a test that draws re-enters them (see _jrc)
    yield res
    plt.close("all")


def _jrc():
    return plt.rc_context(J.rc_params(J.load_config(ROOT)))


# ---- the settings file ----

def test_config_values_and_font(cfg):
    assert cfg["page"]["main_width_in"] == 6.3 and cfg["page"]["main_max_height_in"] == 8.0 and cfg["page"]["double_column_width_in"] <= 7.5 and cfg["page"]["double_column_max_height_in"] <= 8.75
    assert cfg["text"]["min_pt"] >= 8 and cfg["text"]["pdf_fonttype"] == 42 and cfg["text"]["ps_fonttype"] == 42
    assert cfg["lines"]["min_width_pt"] >= 0.3 and cfg["output"]["pdf_dpi"] == 300 and cfg["output"]["png_dpi"] == 600 and cfg["output"]["tiff_dpi"] == 600
    assert set(cfg["colour"]["allowed_cmaps"]) == {"magma", "viridis", "cividis"}
    assert not set(cfg["colour"]["allowed_cmaps"]) & set(cfg["colour"]["forbidden_cmaps"])
    fam, fallback = J.font_choice(cfg)
    assert fam in ("Arial", "Helvetica", "DejaVu Sans") and (fallback == (fam == "DejaVu Sans"))
    assert re.fullmatch(cfg["files"]["name_pattern"], "F1_journal.pdf") and not re.fullmatch(cfg["files"]["name_pattern"], "F1 journal.pdf")


def test_page_size_refuses_a_figure_that_is_too_tall(cfg):
    with pytest.raises(J.JournalError):
        J.page_size(cfg, cfg["page"]["main_max_height_in"] + 0.5)
    assert J.page_size(cfg, 8.0) == (cfg["page"]["main_width_in"], 8.0)


# ---- the collision checker on synthetic figures (the checker is tested before it is trusted on the figures) ----

def _toy(dpi=100):
    fig = plt.figure(figsize=(3, 2.6), dpi=dpi)
    ax = fig.add_axes([0.2, 0.3, 0.7, 0.5])
    ax.set_gid("panel:a")
    ax.set_title("(a) toy", loc="left")
    return fig, ax


def test_checker_finds_text_on_text_marker_line_and_image():
    fig, ax = _toy()
    ax.plot([0.5], [0.5], "o", ms=10, gid="m1")
    ax.plot([0.1, 0.9], [0.2, 0.2], "-", gid="l1")
    ax.text(0.5, 0.5, "on the marker", ha="center")
    ax.text(0.5, 0.2, "on the line", ha="center", va="center")
    ax.text(0.3, 0.8, "one text")
    ax.text(0.3, 0.8, "one text")
    kinds = {h.kind for h in CO.check(fig)[0]}
    assert {"text-marker", "text-line", "text-text"} <= kinds
    plt.close(fig)
    fig, ax = _toy()
    ax.imshow([[0, 1], [1, 0]], extent=(0, 1, 0, 1), aspect="auto")
    ax.text(0.5, 0.5, "on the image")
    assert any(h.kind == "text-image" for h in CO.check(fig)[0])
    plt.close(fig)


def test_checker_finds_marker_on_marker_frame_edge_and_legend():
    fig, ax = _toy()
    ax.plot([0.5], [0.5], "s", ms=8, gid="m1")
    ax.plot([0.5], [0.5], "o", ms=8, gid="m2")
    ax.text(0.0, 0.5, "straddles the frame", ha="center")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    (under,) = ax.plot([0.9], [0.9], "o", ms=6, gid="under legend")
    ax.legend(handles=[under], labels=["a legend entry that is long"], loc="upper right")
    fig.text(-0.1, 0.5, "outside the figure")
    kinds = {h.kind for h in CO.check(fig)[0]}
    assert {"marker-marker", "text-frame", "legend-marker", "text-figure-edge"} <= kinds
    plt.close(fig)


def test_checker_is_silent_on_a_clean_figure_and_allow_list_needs_a_match():
    fig, ax = _toy()
    ax.plot([0.2], [0.2], "o", ms=4, gid="m1")
    ax.plot([0.8], [0.8], "s", ms=4, gid="m2")
    ax.set_xlabel("x")
    assert CO.check(fig)[0] == []
    ax.plot([0.2], [0.2], "s", ms=4, gid="m3")
    bad, ok = CO.check(fig)
    assert [h.kind for h in bad] == ["marker-marker"] and not ok
    entry = CO.AllowEntry("marker-marker", "a", "m1", "m3", "toy reason")
    bad, ok = CO.check(fig, allow=(entry,))
    assert not bad and ok and ok[0][1] == "toy reason"
    plt.close(fig)


# 13t-1c (DL-563 S3, DL-564): the checker gaps found by the independent review of the first build; every case below must be flagged, and a clear case must stay silent.
PT = 1.0 / 151.2           # one point in data units on the toy axes (0 to 1 over 2.1 in at 100 dpi)


def _toy01():
    fig, ax = _toy()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return fig, ax


def _kinds(fig):
    bad = CO.check(fig)[0]
    plt.close(fig)
    return {h.kind for h in bad}


def test_s3_two_overlapping_markers_are_flagged_also_with_the_same_name_and_the_pad_counts():
    fig, ax = _toy01()
    ax.plot([0.4], [0.5], "s", ms=8, mew=0, gid="same name")
    ax.plot([0.4 + 4 * PT], [0.5], "o", ms=8, mew=0, gid="same name")
    assert "marker-marker" in _kinds(fig)
    fig, ax = _toy01()                                              # a gap of 0.2 pt is below the pad of 0.5 pt: touching; a gap of 1 pt is clear
    ax.plot([0.4], [0.5], "o", ms=6, mew=0, gid="a")
    ax.plot([0.4 + 6.2 * PT], [0.5], "o", ms=6, mew=0, gid="b")
    assert "marker-marker" in _kinds(fig)
    fig, ax = _toy01()
    ax.plot([0.4], [0.5], "o", ms=6, mew=0, gid="a")
    ax.plot([0.4 + 7.0 * PT], [0.5], "o", ms=6, mew=0, gid="b")
    assert _kinds(fig) == set()


def test_s3_marks_of_one_line_that_overlap_each_other_are_flagged():
    fig, ax = _toy01()
    ax.plot([0.4, 0.4 + 3 * PT], [0.5, 0.5], "o", ls="none", ms=8, mew=0, gid="one line")
    assert "marker-marker" in _kinds(fig)


def test_s3_an_arrowhead_on_a_dot_is_flagged_and_the_start_circle_of_the_arrow_is_not():
    fig, ax = _toy01()
    ax.annotate("", xy=(0.8, 0.5), xytext=(0.2, 0.5), arrowprops=dict(arrowstyle="-|>", lw=1.0, shrinkA=0, shrinkB=0, mutation_scale=8), gid="arr")
    ax.plot([0.2], [0.5], "o", ms=5, mew=0, gid="start circle")
    assert "marker-arrow" not in _kinds(fig)
    fig, ax = _toy01()
    ax.annotate("", xy=(0.8, 0.5), xytext=(0.2, 0.5), arrowprops=dict(arrowstyle="-|>", lw=1.0, shrinkA=0, shrinkB=0, mutation_scale=8), gid="arr")
    ax.plot([0.8], [0.5], "o", ms=5, mew=0, gid="end dot")
    bad = CO.check(fig)[0]
    plt.close(fig)
    assert any(h.kind == "marker-arrow" and "end dot" in h.a for h in bad)


def test_s3_a_marker_on_the_frame_is_flagged_and_one_inside_is_not():
    fig, ax = _toy01()
    ax.plot([0.0], [0.5], "o", ms=6, mew=0, clip_on=False, gid="on the frame")
    ax.plot([0.5], [0.5], "o", ms=6, mew=0, gid="inside")
    bad = CO.check(fig)[0]
    plt.close(fig)
    assert [h.a for h in bad if h.kind == "marker-frame"] == ["marks:on the frame"]


def test_s3_a_median_tick_on_a_marker_and_a_marker_on_a_separator_line_are_flagged():
    fig, ax = _toy01()
    ax.hlines([0.5], 0.4, 0.6, colors="k", lw=1.6)
    ax.plot([0.5], [0.5], "o", ms=4, mew=0, gid="on the tick")
    ax.plot([0.5], [0.8], "o", ms=4, mew=0, gid="clear of the tick")
    bad = CO.check(fig)[0]
    plt.close(fig)
    assert [h.a for h in bad if h.kind == "marker-tick"] == ["marks:on the tick"]
    fig, ax = _toy01()
    ax.axvline(0.3, lw=0.4)
    ax.plot([0.3], [0.6], "o", ms=4, mew=0, gid="on the separator")
    ax.plot([0.7], [0.6], "o", ms=4, mew=0, gid="away")
    bad = CO.check(fig)[0]
    plt.close(fig)
    assert [h.a for h in bad if h.kind == "marker-line"] == ["marks:on the separator"]


def test_s3_a_marker_larger_than_its_cell_is_flagged():
    import numpy as np
    fig, ax = _toy01()
    ax.pcolormesh(np.arange(11) / 10.0, np.arange(11) / 10.0, np.zeros((10, 10)))                    # cells of 15 pt
    ax.plot([0.55], [0.55], "o", ms=20, mew=0, gid="too big")
    ax.plot([0.25], [0.25], "o", ms=8, mew=0, gid="fits")
    bad = CO.check(fig)[0]
    plt.close(fig)
    assert [h.a for h in bad if h.kind == "marker-cell"] == ["marks:too big"]


def test_letters_in_reading_order_detects_a_swap():
    fig = plt.figure(figsize=(4, 4))
    for title, pos in (("(a) one", [0.1, 0.6, 0.3, 0.3]), ("(b) two", [0.6, 0.6, 0.3, 0.3]), ("(c) three", [0.1, 0.1, 0.3, 0.3])):
        fig.add_axes(pos).set_title(title, loc="left")
    assert CO.letters_in_order(fig) == (True, ["a", "b", "c"])
    plt.close(fig)
    fig = plt.figure(figsize=(4, 4))
    for title, pos in (("(a) one", [0.1, 0.7, 0.3, 0.2]), ("(c) three", [0.1, 0.4, 0.3, 0.2]), ("(b) two", [0.1, 0.1, 0.3, 0.2])):
        fig.add_axes(pos).set_title(title, loc="left")
    assert CO.letters_in_order(fig)[0] is False
    plt.close(fig)


# ---- the colour and font checks on synthetic figures ----

def test_cmap_report_and_forbidden_maps(cfg):
    fig, ax = _toy()
    ax.imshow([[0, 1]], cmap="magma")
    ax.imshow([[0, 1]], cmap="cividis_r")
    names, bad = JC.cmap_report(fig, cfg)
    assert not bad and {"magma", "cividis_r"} <= set(names)
    ax.imshow([[0, 1]], cmap="jet")
    ax.imshow([[0, 1]], cmap="turbo")
    ax.imshow([[0, 1]], cmap="hsv")
    assert {"jet", "turbo", "hsv"} <= set(JC.cmap_report(fig, cfg)[1])
    plt.close(fig)


def test_non_colour_distinction_flags_colour_only_pairs():
    fig, ax = _toy()
    ax.plot([0, 1], [0, 1], "-", color="#ff0000", gid="a")
    ax.plot([0, 1], [1, 0], "-", color="#0000ff", gid="b")
    assert JC.non_colour_violations(fig)
    ax.lines[1].set_linestyle("--")
    assert not JC.non_colour_violations(fig)
    ax.plot([0, 1], [0.5, 0.5], "o", color="#00ff00", gid="c")
    ax.plot([0, 1], [0.6, 0.6], "s", color="#ff00ff", gid="d")
    assert not JC.non_colour_violations(fig)
    plt.close(fig)


def test_lightness_and_contrast_use_the_colour_library():
    assert JC.lightness("#000000") < 1 and JC.lightness("#ffffff") > 99
    assert JC.contrast_ratio("#000000", "#ffffff") > 20 and JC.contrast_ratio("#777777", "#808080") < 1.2
    assert JC.red_green_pairs is not None


def test_text_and_line_guards(cfg):
    fig, ax = _toy()
    ax.text(0.5, 0.5, "small", fontsize=6)
    ax.plot([0, 1], [0, 1], lw=0.1, gid="thin")
    assert JC.text_sizes(fig, 8) and JC.line_widths(fig, 0.3)
    changed = J.finish(fig, J.load_config(ROOT))                    # the final guard raises the text and thickens the line, and says how many
    assert changed["text_raised"] >= 1 and changed["lines_thickened"] >= 1
    assert not JC.text_sizes(fig, 8) and not JC.line_widths(fig, 0.3)
    plt.close(fig)


# ---- the journal builds ----

@needs
@pytest.mark.parametrize("fid", PILOT)
def test_zero_unlisted_collisions_in_the_journal_build(figs, cfg, fid):
    fig, d, _ = figs[fid]
    with _jrc():
        bad, ok = CO.check(fig, pad_pt=cfg["collision"]["pad_pt"], allow=CO.JOURNAL_ALLOW.get(fid, ()))
    assert not bad, [str(h) for h in bad]
    assert all(reason.strip() for _, reason in ok)
    for e in CO.JOURNAL_ALLOW.get(fid, ()):
        assert e.reason.strip()


@needs
def test_checker_finds_the_known_faults_of_the_draft_f1_and_f3():
    """J10 and J12 regression: the same checker, run on the draft figure objects, reports the faults named in the prompt (report only; nothing is fixed)."""
    crit, _ = FG.F.K.load_frozen_criteria(ROOT)
    d1 = FG.prepare_F1(FG.load_F1(), crit)
    fig = FG._draw_F1(d1, True)
    bad = CO.check(fig)[0]
    texts = [(h.kind, h.a, h.b) for h in bad]
    assert any(k == "text-marker" and "raw crossings" in a for k, a, b in texts)                       # the raw-crossings marker sits on its text
    assert any(k == "text-image" and "32559 of 49364" in a for k, a, b in texts)                       # the cell-count text is printed over the spectrogram
    assert any(k == "text-text" and ("(j)" in a or "(j)" in b) for k, a, b in texts)                   # the (j) label collides with the title of (i)
    plt.close(fig)
    d3 = FG.prepare_F3(FG.load_F3())
    fig = FG._draw_F3(d3, True, FG.strip_lines(d3))
    assert CO.letters_in_order(fig)[0] is False                                                        # (e) is above (d)
    assert sum(1 for h in CO.check(fig)[0] if h.kind == "marker-marker" and "start:" in h.a + h.b) >= 6      # the start marks of P1, P2, P3, P4a, P4b and P5 sit on each other
    plt.close(fig)


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_size_shape_letters_text_fonts_lines_colour(figs, cfg, fid):
    fig, d, _ = figs[fid]
    w, h = fig.get_size_inches()
    assert w <= cfg["page"]["main_width_in"] + 1e-9 and h <= cfg["page"]["main_max_height_in"] + 1e-9
    assert CO.letters_in_order(fig)[0], CO.letters_in_order(fig)
    assert not JC.text_sizes(fig, cfg["text"]["min_pt"])
    assert not JC.line_widths(fig, cfg["lines"]["min_width_pt"])
    names, bad = JC.cmap_report(fig, cfg)
    assert not bad
    assert not JC.non_colour_violations(fig)
    assert not JC.red_green_pairs(fig, cfg["colour"]["min_lightness_difference"])
    assert not JC.text_contrast(fig, cfg["colour"]["min_text_contrast"], {"ramp": "#fdf0e6", "net": "#eaf0f7", "model": "#f4f4f4", "mf": "#f4f4f4", "out": "#f4f4f4"})
    assert not JC.image_text_violations(fig)


@needs
def test_f1_and_f3_letters_are_a_to_k_and_a_to_e(figs):
    assert CO.letters_in_order(figs["F1"][0]) == (True, list("abcdefghijk"))
    assert CO.letters_in_order(figs["F3"][0]) == (True, list("abcde"))
    assert CO.letters_in_order(figs["F5"][0]) == (True, list("abcdefghi"))


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_pdf_fonts_embedded_no_type3_and_sizes(built, cfg, fid):
    r = JC.pdf_report(built["base"] / "journal" / fid / f"{fid}_journal.pdf")
    assert not r["type3"] and r["descriptors"] > 0 and r["fontfile2"] + r["fontfile3"] >= r["descriptors"]
    assert r["tf_sizes"] and min(r["tf_sizes"]) >= cfg["text"]["min_pt"]
    w, h = r["mediabox"][2] / 72.0, r["mediabox"][3] / 72.0
    assert w <= cfg["page"]["main_width_in"] + 0.01 and h <= cfg["page"]["main_max_height_in"] + 0.01
    if J.font_choice(cfg)[0] != "DejaVu Sans":
        assert any(J.font_choice(cfg)[0] in f for f in r["basefonts"])


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_exported_files_png_tiff_names(built, figs, cfg, fid):
    base = built["base"] / "journal"
    out = base / fid
    from PIL import Image
    W, H = figs[fid][0].get_size_inches()
    im = Image.open(out / f"{fid}_journal.png")
    assert im.size == (round(W * cfg["output"]["png_dpi"]), round(H * cfg["output"]["png_dpi"])) and tuple(round(x) for x in im.info["dpi"]) == (600, 600)
    t = JC.tiff_report(out / f"{fid}_journal.tiff")
    assert t["mode"] == "RGB" and t["dpi"] == (600, 600) and str(t["compression"]).lower() in ("tiff_lzw", "lzw")
    assert not JC.bad_file_names(base, cfg["files"]["name_pattern"])
    prov = json.loads((out / f"{fid}_journal_provenance.json").read_text(encoding="utf-8"))
    assert not JC.case_mismatches([Path(o["path"]).name for o in prov["outputs"]], out)
    sup = (base / "supplement" / f"{fid}_supplement.md").read_text(encoding="utf-8")
    assert not JC.case_mismatches(re.findall(r"\b([A-Za-z0-9_+=,.\-]+_(?:journal_provenance\.json|journal\.pdf|params\.csv))\b", sup), out)


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_journal_provenance_records_the_settings_and_is_a_draft(built, fid):
    prov = json.loads((built["base"] / "journal" / fid / f"{fid}_journal_provenance.json").read_text(encoding="utf-8"))
    assert prov["draft"] is True
    assert prov["journal"]["mode"] == "journal" and prov["journal"]["config"] == "configs/journal_export.yaml"
    assert "configs/journal_export.yaml" in prov["configs"]
    assert prov["inputs"] and prov["criteria_sha256"]


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_drawn_data_digest_of_the_export_equals_the_draft(built, fid):
    draft = DRAFT_DIGEST_FILES[fid].read_text(encoding="utf-8").strip()
    assert built["out"][fid]["drawn_sha256"] == draft
    prov = json.loads((built["base"] / "journal" / fid / f"{fid}_journal_provenance.json").read_text(encoding="utf-8"))
    assert prov["journal"]["drawn_data_sha256"] == draft


@needs
def test_draft_files_are_byte_identical_before_and_after_and_to_the_manifest(built):
    assert built["before"] == built["after"]
    import csv
    with open(ROOT / "docs" / "ms13_figure_manifest.csv", newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["figure"] in PILOT and r["file"].startswith("figures/")]
    assert rows
    for r in rows:
        assert _sha(ROOT / r["file"]) == r["sha256"], r["file"]


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_every_draft_strip_fail_line_is_in_the_journal_caption(built, figs, fid):
    cap = built["out"][fid]["caption"]
    d = figs[fid][1]
    lines = STRIP[fid](d)
    assert lines
    sup = (built["base"] / "journal" / "supplement" / f"{fid}_supplement.md").read_text(encoding="utf-8")
    for ln in lines:
        assert PL.plain_fragment(ln) in cap, ln               # 13t-1c (DL-566 E8): the journal caption holds the plain form, the supplement the verbatim line
        assert ln in sup, ln
    assert CAP.RED_TITLE_NOTE.split(":")[0].lower() in cap.lower()          # the red-title definition is in the caption


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_caption_sentence_one_names_the_main_failure_and_has_the_take_home(built, fid):
    cap = built["out"][fid]["caption"]
    s1 = cap.split(". ")[1]
    for m in MAIN[fid]:
        assert m in s1, m
    draft_cap = (ROOT / "figures" / fid / f"{fid}_caption.txt").read_text(encoding="utf-8")
    take = {"F1": FG.F1_TAKE_HOME, "F3": FG.F3_TAKE_HOME, "F5": FG.F5_TAKE_HOME}[fid]
    assert PL.plain_fragment(take) in cap and take in draft_cap            # 13t-1c (DL-566 E9): the journal caption holds the plain form of the take-home
    assert "DRAFT" not in cap and "as ruled (DL" not in cap                 # the footer text is in the supplement, not in the caption


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_no_draft_decision_log_or_provenance_text_on_the_image(figs, fid):
    assert not JC.image_text_violations(figs[fid][0])


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_supplement_lists_every_strip_row_footer_and_parameters(built, figs, fid):
    sup = (built["base"] / "journal" / "supplement" / f"{fid}_supplement.md").read_text(encoding="utf-8")
    for r in figs[fid][1]["strip"]:
        assert f"{r['rb_id']} {r['check_id']}" in sup
        assert r["status"] in sup
    assert "DRAFT" in sup and "as ruled" in sup and "Parameter table" in sup
    assert (built["base"] / "journal" / "supplement" / f"{fid}_source_data.csv").stat().st_size > 100
    alt = (built["base"] / "journal" / "supplement" / f"{fid}_alt_text.txt").read_text(encoding="utf-8")
    letters = {"F1": "abcdefghijk", "F3": "abcde", "F5": "abcdefghi"}[fid]
    for ltr in letters:
        assert f"Panel ({ltr}):" in alt


@needs
def test_f3_journal_has_one_combined_path_and_p4a_p4b_separate(figs):
    fig, d, _ = figs["F3"]
    gids = [t.get_gid() for ax in fig.axes for t in ax.texts if t.get_gid()]
    assert sum(1 for g in gids if g == "arrow:tau_d:combined") == 1 and sum(1 for g in gids if g == "arrow:Delta:combined") == 1
    assert not any(g.startswith("arrow:tau_d:P1") or g.startswith("arrow:Delta:P2") for g in gids)
    assert {"arrow:Delta:P4a", "arrow:Delta:P4b"} <= set(gids)
    legend_texts = [t.get_text() for ax in fig.axes if ax.get_legend() for t in ax.get_legend().get_texts()]
    assert any("P1, P2, P3, P5: identical in" in " ".join(t.split()) for t in legend_texts)


@needs
def test_titles_with_fail_are_red_and_carry_the_word(figs):
    from matplotlib.colors import to_hex
    from mprsurge.plotting import style as S
    red = S.figure_colour("fail_text").lower()
    for fid in PILOT:
        fig = figs[fid][0]
        for ax in fig.axes:
            t = ax.get_title(loc="left")
            if t and to_hex(ax._left_title.get_color()).lower() == red:
                assert "FAIL" in t
    titles = {fid: [ax.get_title(loc="left") for ax in figs[fid][0].axes] for fid in PILOT}
    assert sum("FAIL" in t for t in titles["F3"]) == 3 and sum("FAIL" in t for t in titles["F1"]) == 2


# ---- 13t-1b (DL-554, DL-556, DL-557): the PCJ settings, FAIL titles, wording of coincide, edge bands, in-cell marks ----

def test_r1_save_all_writes_png_and_tiff_main_files_and_never_svg_wmf_emf(tmp_path, cfg):
    import matplotlib.pyplot as plt
    from PIL import Image
    fig = plt.figure(figsize=(1.5, 1.0))
    fig.add_axes([0.2, 0.2, 0.6, 0.6]).plot([0, 1], [0, 1])
    saved = J.save_all(fig, tmp_path, "toy_journal", cfg)
    plt.close(fig)
    assert {"png", "tiff", "pdf"} <= set(saved["paths"])
    names = {p.suffix for p in tmp_path.iterdir()}
    assert {".png", ".tiff", ".pdf"} <= names and not names & {".svg", ".wmf", ".emf"}
    png, tif = Image.open(tmp_path / "toy_journal.png"), Image.open(tmp_path / "toy_journal.tiff")
    assert png.size == tif.size == (900, 600) and tuple(round(x) for x in png.info["dpi"]) == (600, 600)
    assert tif.mode == "RGB" and tuple(round(x) for x in tif.info["dpi"]) == (600, 600)
    assert cfg["output"]["forbidden_formats"] == ["svg", "wmf", "emf"] and not JC.forbidden_format_files(tmp_path, cfg["output"]["forbidden_formats"])
    (tmp_path / "x.svg").write_text("<svg/>")
    assert JC.forbidden_format_files(tmp_path, cfg["output"]["forbidden_formats"]) == ["x.svg"]


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_r1_main_png_and_tiff_are_600_dpi_6p3_in_wide_at_most_8_in_high_and_the_pdf_is_an_extra(built, figs, cfg, fid):
    from PIL import Image
    base = built["base"] / "journal"
    out = base / fid
    W, H = figs[fid][0].get_size_inches()
    assert abs(W - 6.3) < 1e-9 and H <= 8.0 + 1e-9
    png, tif = Image.open(out / f"{fid}_journal.png"), Image.open(out / f"{fid}_journal.tiff")
    assert png.size == tif.size == (round(6.3 * 600), round(H * 600))
    assert (out / f"{fid}_journal.pdf").is_file()
    assert not JC.forbidden_format_files(base, cfg["output"]["forbidden_formats"])
    r = JC.pdf_report(out / f"{fid}_journal.pdf")
    assert abs(r["mediabox"][2] / 72.0 - 6.3) < 0.02
    for f in (out / f"{fid}_journal.png", out / f"{fid}_journal.tiff"):
        assert f.stat().st_size / 1e6 <= cfg["output"]["raster_size_flag_mb"], f.name
    assert (out / f"{fid}_journal.pdf").stat().st_size / 1e6 <= cfg["output"]["pdf_size_flag_mb"]


@needs
def test_r2_verifier_cvd_row_is_manual_and_the_three_builds_have_no_fail(built, cfg):
    import csv
    import importlib.util
    spec = importlib.util.spec_from_file_location("ms13_verify_export", ROOT / "scripts" / "ms13_verify_export.py")
    VE = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(VE)
    with open(ROOT / "docs" / "ms13_figure_manifest.csv", newline="", encoding="utf-8") as fh:
        manifest = {(r["figure"], r["file"]): r["sha256"] for r in csv.DictReader(fh)}
    for fid in PILOT:
        res, _ = VE.check_figure(fid, built["base"] / "journal", ROOT, manifest)
        assert res["cvd"][0] == "MANUAL" and "online simulator" in res["cvd"][1]
        assert [c for c, (st, _) in res.items() if st == "FAIL"] == [], (fid, {c: v for c, v in res.items() if v[0] == "FAIL"})
        assert set(VE.CHECKS) == set(res)


@needs
def test_r3_f3_caption_says_that_the_headline_hopf_point_is_the_5_ms_slice_point(built, figs):
    cap = built["out"]["F3"]["caption"]
    d = figs["F3"][1]
    assert f"the Hopf point of the tau_d {d['headline_tau_d_ms']:g} ms slice of the Delta {d['headline_Delta']:g} panel" in cap and "drawn twice and not moved" in cap
    assert f"eta_bar {d['headline_hopf_eta']:.3f}" in cap
    assert all(e.reason.strip() for e in CO.JOURNAL_ALLOW["F3"]) and len(CO.JOURNAL_ALLOW["F3"]) == 5


@needs
def test_r4_f5_titles_a_and_g_carry_fail_and_are_red_and_the_f1_caption_has_the_other_failed_checks(built, figs):
    from matplotlib.colors import to_hex
    from mprsurge.plotting import style as S
    red = S.figure_colour("fail_text").lower()
    fig = figs["F5"][0]
    titles = {ax.get_gid().split(":")[1]: ax for ax in fig.axes if (ax.get_gid() or "").startswith("panel:")}
    for letter in "agbc":
        ax = titles[letter]
        assert "FAIL" in ax.get_title(loc="left") and to_hex(ax._left_title.get_color()).lower() == red, letter
    assert sum("FAIL" in ax.get_title(loc="left") for ax in fig.axes) == 4
    assert "FAIL" not in titles["h"].get_title(loc="left") and "FAIL" not in titles["i"].get_title(loc="left")
    cap = built["out"]["F1"]["caption"]
    assert ("Other failed checks on the headline path are shown elsewhere: the RB2 headline class and the RB3(b) classifier onset in F4, and the RB6 solver onset "
            "(181 ms against 1 ms) in F4 and FS4.") in cap
    alt5 = (built["base"] / "journal" / "supplement" / "F5_alt_text.txt").read_text(encoding="utf-8")
    assert "RB1 cells: FAIL" in alt5 and "RB6 network f_pk FAIL" in alt5


@needs
def test_r4_other_failed_checks_sentence_needs_fail_rows_in_the_stored_table():
    a11 = FG.load_F1(RES)["a11"]
    assert FG._f1_other_failures(a11).startswith("Other failed checks on the headline path are shown elsewhere: the RB2 headline class and the RB3(b) classifier onset in F4, and the RB6 solver onset (181 ms against 1 ms)")
    bad = [{**r, "pass_or_fail": "PASS"} if (r["rb_id"], r["check_id"]) == ("RB6", "solver_onset_headline") else r for r in a11]
    with pytest.raises(FG.DataError):
        FG._f1_other_failures(bad)


@needs
def test_r6_raw_first_crossings_overlap_and_only_equal_stored_values_coincide(built, figs):
    d = figs["F1"][1]
    r0, r1 = min(d["raw120_s"]), max(d["raw120_s"])
    assert len(set(d["raw120_s"])) == 3 and len(set(d["onset120_s"])) == 1                      # stored: raw crossings differ, classifier onsets are equal
    assert (f"{r0:.3f}", f"{r1:.3f}") == ("50.170", "50.924")
    legend = [t.get_text() for ax in figs["F1"][0].axes if ax.get_legend() for t in ax.get_legend().get_texts()]
    raw = [t for t in legend if "raw first crossing" in t]
    assert len(raw) == 1 and "coincide" not in raw[0] and "overlap at this scale: stored values 50.170 to 50.924" in raw[0]
    ons = [t for t in legend if "classifier onset" in t]
    assert len(ons) == 1 and "the 3 seeds coincide" in ons[0]
    cap = built["out"]["F1"]["caption"]
    assert "a note says that the 3 seeds coincide" not in cap and "the key says that the 3 seeds coincide" not in cap
    assert "overlap at this scale (stored values 50.170 to 50.924 s, not equal; the key says so)" in cap
    for m in re.finditer(r"coincide", cap):                                                    # every use of the word is about the equal classifier onsets
        ctx = cap[max(0, m.start() - 160):m.end() + 160]
        assert "classifier onset" in ctx or "S-sus" in ctx or "12.0" in ctx, ctx
    alt = (built["base"] / "journal" / "supplement" / "F1_alt_text.txt").read_text(encoding="utf-8")
    assert "coincide" not in alt and "50.170 to 50.924" in alt


def test_r6_reword_helper_stops_if_the_stored_raw_crossings_were_equal():
    with pytest.raises(FG.DataError):
        FG._f1_stored_reword({"raw120_s": [50.0, 50.0, 50.0]})
    pairs = FG._f1_stored_reword({"raw120_s": [50.924, 50.170, 50.857]})
    assert "50.170 to 50.924" in pairs[0][1]


@needs
def test_r7_edge_band_sentence_is_computed_from_the_stored_time_vector(built, figs):
    d = figs["F1"][1]
    t = d["spec_t_s"]
    s_ = FG._f1_edge_bands(d)
    assert s_ in built["out"]["F1"]["caption"]
    assert f"{d['spec_settings']['window_s']:g} s long with a step of {d['spec_settings']['step_s']:g} s" in s_
    assert f"{t.size} centres from {t[0]:g} to {t[-1]:g} s" in s_
    assert "path time 0 to 0.5 s and 164.5 to 165 s has no stored window and no cell" in s_
    d2 = {**d, "spec_t_s": t[[0, 1, 3]]}                                                        # a non-uniform vector is not settled by the stored times
    assert "cause not determined (UNVERIFIED)" in FG._f1_edge_bands(d2)


@needs
def test_r8_in_cell_marks_of_f5_c_and_d_are_readable_and_in_the_key_as_plotted(figs):
    from matplotlib.lines import Line2D
    from matplotlib.colors import to_hex
    from mprsurge.plotting import style as S
    fig = figs["F5"][0]
    plotted = {}
    for ax in fig.axes:
        for ln in ax.lines:
            g = ln.get_gid() or ""
            if g[:3] in ("d24", "p1 ") and g.split()[-1] in ("agree", "disagree", "tie"):
                plotted.setdefault(g.split()[-1], set()).add((ln.get_marker(), ln.get_markersize(), ln.get_markeredgewidth(), to_hex(ln.get_color())))
    assert set(plotted) == {"agree", "disagree", "tie"}
    for nm, marks in plotted.items():
        assert len(marks) == 1
        (mk, ms, mew, col), = marks
        assert mk == S.F5_STATE_MARKS[nm] and ms >= 4.0 and col.lower() == S.figure_colour("text_dark").lower()
    key = [ax for ax in fig.axes if ax.get_gid() == "legend axes (a to e)"][0].get_legend()
    keyed = {(ln.get_marker(), ln.get_markersize(), ln.get_markeredgewidth()) for ln in key.findobj(Line2D)}
    for nm, marks in plotted.items():
        (mk, ms, mew, col), = marks
        assert (mk, ms, mew) in keyed, nm


@needs
def test_r10_f1_supplement_names_the_zip_of_the_source_data(built):
    sup = (built["base"] / "journal" / "supplement" / "F1_supplement.md").read_text(encoding="utf-8")
    assert "F1_source_data.csv is" in sup and "to be zipped for the Zenodo record" in sup
    assert "zipped" not in (built["base"] / "journal" / "supplement" / "F3_supplement.md").read_text(encoding="utf-8")


# ---- 13t-1c (DL-563 S1 to S14; DL-566): new tests ----

def _panel(fig, letter):
    return next(ax for ax in fig.axes if ax.get_gid() == f"panel:{letter}")


@needs
def test_s1_f5_a_and_e_carry_no_class_mark_the_key_shows_the_hatch_swatch_and_the_source_data_has_every_cell_class(figs, built):
    from matplotlib.patches import Patch
    fig, d, _ = figs["F5"]
    for letter in "ae":
        ax = _panel(fig, letter)
        assert not any((ln.get_gid() or "").startswith("class marks") for ln in ax.lines), letter
        assert not [ln for ln in ax.lines if ln.get_marker() not in ("None", None, "") and len(ln.get_xdata()) > 20], letter       # no run of class marks
    key = next(ax for ax in fig.axes if ax.get_gid() == "legend axes (a to e)").get_legend()
    patches = [h for h in key.legend_handles if isinstance(h, Patch)]
    assert len(patches) >= 2 and sum(1 for p_ in patches if p_.get_hatch()) >= 1        # D-none has its hatch in the key, as plotted
    src = (built["base"] / "journal" / "supplement" / "F5_source_data.csv").read_text(encoding="utf-8")
    assert src.count("map1 class per cell") == d["map1_class"].size and src.count("map2 class per cell") == d["map2_class"].size


@needs
def test_s2_f3_every_arrow_has_a_solid_head_and_no_marker_at_its_end(figs):
    import numpy as np
    fig, d, _ = figs["F3"]
    fig.canvas.draw()
    heads = [(ax, t) for ax in fig.axes for t in ax.texts if (t.get_gid() or "").startswith("arrowhead:")]
    assert len(heads) == 13                                                  # combined (2: (c) and (d)), P5 return (2), P4a and P4b (2, in (d)), seven strip rows in (e)
    for ax, h in heads:
        assert h.arrow_patch.get_linestyle() in ("-", "solid")
        tip = np.asarray(ax.transData.transform(h.xy), float)
        for ln in ax.lines:
            if ln.get_marker() in ("None", None, "") or not len(ln.get_xdata()) or (ln.get_gid() or "").startswith("start:"):
                continue
            for x, y in zip(ln.get_xdata(), ln.get_ydata()):
                pt = np.asarray(ax.transData.transform((x, y)), float)
                if (ln.get_gid() or "") in ("a6_hopf_point", "slice Hopf points"):
                    continue                                                 # stored positions on the path (allow-listed, DL-565)
                assert np.hypot(*(pt - tip)) > fig.dpi / 72.0, (h.get_gid(), ln.get_gid())
    gids = {ln.get_gid() for ax in fig.axes for ln in ax.lines}
    assert "start:tau_d:P5:1" not in gids and "start:Delta:P5:1" not in gids


@needs
def test_s3_extended_checker_has_zero_unlisted_hits_and_the_provisional_entries_name_the_stop(figs, cfg):
    for fid in PILOT:
        fig, d, _ = figs[fid]
        with _jrc():
            bad, ok = CO.check(fig, pad_pt=cfg["collision"]["pad_pt"], allow=CO.JOURNAL_ALLOW.get(fid, ()))
        assert not bad, (fid, [str(h) for h in bad][:3])
    prov = [e for e in CO.JOURNAL_ALLOW["F5"] if e.reason.startswith("PROVISIONAL")]
    assert prov and all("S14" in e.reason for e in prov)
    assert all(len(e.reason) > 40 for fid in PILOT for e in CO.JOURNAL_ALLOW[fid])


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_s4_the_journal_caption_has_no_ruling_code_and_no_dl_number_and_every_limit_is_in_plain_words_and_paired_in_the_supplement(built, fid):
    from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS
    cap = built["out"][fid]["caption"]
    assert not PL.FORBIDDEN.search(cap), PL.FORBIDDEN.findall(cap)
    ids = {"F1": FG.F1_CLAIM_LIMITS, "F3": FG.F3_CLAIM_LIMITS, "F5": FG.F5_CLAIM_LIMITS}[fid]
    for i in ids:
        assert PL.PLAIN_LIMITS[i].rstrip(".") in cap, i
    sup = (built["base"] / "journal" / "supplement" / f"{fid}_supplement.md").read_text(encoding="utf-8")
    for i in ids:
        short, dls = CLAIM_LIMIT_LABELS[i]
        assert f"{i}: {short} ({', '.join(dls)})" in sup, i                    # the verbatim ruled text with its DL numbers
        assert PL.PLAIN_LIMITS[i].rstrip(".") in sup, i
    assert "IDs used in this caption:" in cap


def test_s4_every_number_of_a_ruled_claim_limit_occurs_in_its_plain_sentence():
    import re
    from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS
    num = re.compile(r"[0-9][0-9,]*(?:[.][0-9]+)?(?:e[0-9]+)?")
    code = re.compile(r"(?<![0-9.])[A-Za-z]+[0-9]+[A-Za-z0-9()-]*")            # RB1, G7, D24, G4-C1, MS9: the digits of a code are not numbers of a limit
    for i, plain in PL.PLAIN_LIMITS.items():
        short = code.sub("", CLAIM_LIMIT_LABELS[i][0])
        have = {n.rstrip(",") for n in num.findall(code.sub("", plain))}
        for n in num.findall(short):
            assert n.rstrip(",") in have, (i, n)


def test_s4_plain_helpers_remove_dl_numbers_and_stop_on_a_ruling_code():
    assert PL.scrub_dl("a (DL-319, DL-323), b; c (DL-163, DL-208).") == "a, b; c."
    assert "DL-" not in PL.scrub_dl("x, DL-319; y (DL-320) z")
    with pytest.raises(PL.PlainError):
        PL.to_plain("F9. A claim with a stray code G4-C1 here. Claim limits: x.", ("MS11-C7",))
    with pytest.raises(PL.PlainError):
        PL.plain_limit_text(("no such limit",))


@needs
def test_s5_f1_j_and_k_have_no_y_tick_marks_and_the_caption_says_the_rows_are_those_of_i(figs, built):
    fig = figs["F1"][0]
    for letter in "jk":
        ax = _panel(fig, letter)
        assert not any(tk.tick1line.get_visible() for tk in ax.yaxis.get_major_ticks()), letter
        assert not any(t.get_text() for t in ax.get_yticklabels())
    assert "rows of (j) and (k) are the neurons of (i), in the same order" in built["out"]["F1"]["caption"]


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_s9_and_s13_no_code_names_on_any_journal_image_tau_d_has_no_underscore_psd_is_spelled_out(figs, fid):
    from matplotlib.text import Text
    fig = figs[fid][0]
    texts = [t.get_text() for t in fig.findobj(Text) if t.get_text()]
    for bad in ("path_hypoxia", "T_ramp_s", "tau_d_ms", "I_drive", "tau_ms", "eta_bar", "tau_d", "τ_d", "(Delta)", "N (N)", "ref_devalle"):
        assert not any(bad in s for s in texts), (fid, bad)
    assert not any("PSD" in s for s in texts)
    if fid == "F1":
        assert any("power spectral" in s for s in texts)
    if fid in ("F1", "F3", "F5"):
        assert any("τd" in s for s in texts)


@needs
def test_s9_f1_schematic_has_plain_names_and_no_box_wraps_one_word_per_line(figs):
    fig = figs["F1"][0]
    ax = next(a for a in fig.axes if a.get_gid() == "schematic")
    rows = {t.get_gid(): t.get_text() for t in ax.texts if (t.get_gid() or "").endswith(":rows")}
    assert set(rows) == {"schematic:ramp:rows", "schematic:model:rows", "schematic:mf:rows", "schematic:net:rows", "schematic:out:rows"}
    for g, s in rows.items():
        lines = s.split(chr(10))
        assert sum(1 for ln in lines if len(ln.split()) >= 2) * 2 >= len(lines), (g, lines)
    joined = " ".join(" ".join(rows.values()).split()).lower()
    for word in ("mean excitability", "coupling", "ramp duration", "common (non-local) drive"):
        assert word in joined, word


@needs
def test_s10_the_event_strip_above_d_and_f_holds_the_stored_times_and_is_labelled(figs):
    import numpy as np
    fig, d, _ = figs["F1"]
    strips = [ax for ax in fig.axes if (ax.get_gid() or "") in ("panel:d", "panel:f") and ax.get_ylim() == (0.0, 1.0) and ax.texts]
    assert len(strips) == 2
    for ax in strips:
        assert any("height has no meaning" in t.get_text() and "event times" in t.get_text() for t in ax.texts)
        xs = sorted(float(ln.get_xdata()[0]) for ln in ax.lines if (ln.get_gid() or "").startswith(("classifier onset", "raw first crossing")))
        want = sorted([float(x) for x in set(d["onset120_s"])] + [float(x) for x in d["raw120_s"]])
        assert np.allclose(xs, want)


@needs
def test_s11_s12_labels_colour_bar_j0_p1_and_the_f3_e_title(figs, built):
    f1, f3, f5 = figs["F1"][0], figs["F3"][0], figs["F5"][0]
    cb = next(a for a in f1.axes if a.get_gid() == "colour bar spectrogram")
    assert "power spectral" in cb.get_ylabel() and "density (dB)" in cb.get_ylabel()
    assert "J0" in _panel(f5, "e").get_ylabel() and "path start" in _panel(f5, "e").get_ylabel()
    assert _panel(f5, "d").get_title(loc="left") == "(d) post-hoc view P-1"
    assert _panel(f3, "e").get_title(loc="left") == "(e) paths, one row per path"
    cap5 = built["out"]["F5"]["caption"]
    assert "P-1 = a post-hoc view" in cap5 and "synaptic decay time" in cap5
