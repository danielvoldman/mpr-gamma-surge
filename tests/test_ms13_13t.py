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
PILOT = ("F1", "F3", "F5", "F5c")                                  # 13t-1d (DL-571 T1, E13): F5c is the second journal file of the F5 build; its draft files and digest are those of F5
DRAFT_ID = {"F1": "F1", "F3": "F3", "F5": "F5", "F5c": "F5"}
INPUTS = {"F1": FG.F1_INPUTS, "F3": FG.F3_INPUTS, "F5": FG.F5_INPUTS, "F5c": FG.F5_INPUTS}
DRAFT_DIGEST_FILES = {f: ROOT / "figures" / DRAFT_ID[f] / f"{DRAFT_ID[f]}_drawn_data_sha256.txt" for f in PILOT}
needs = pytest.mark.skipif(not all((RES / p).is_file() for f in PILOT for p in INPUTS[f]) or not all(p.is_file() for p in DRAFT_DIGEST_FILES.values()),
                           reason="stored F1, F3 and F5 inputs under results/ or the stored draft figures are absent")
STRIP = {"F1": FG.f1_strip_lines, "F3": FG.strip_lines, "F5": FG.f5_strip_lines, "F5c": FG.f5c_strip_lines}
MAIN = {"F1": FG.F1_MAIN_FAILURES, "F3": FG.F3_MAIN_FAILURES, "F5": FG.F5_MAIN_FAILURES, "F5c": FG.F5C_MAIN_FAILURES}


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
    before = {f: {p.name: _sha(p) for p in _draft_files(f)} for f in ("F1", "F3", "F5")}
    out = {f: getattr(FG, f"make_{f}")(mode="journal", out_dir=base / "journal" / f) for f in ("F1", "F3", "F5")}
    out["F5c"] = out["F5"]["F5c"]                                      # make_F5 builds both journal files
    after = {f: {p.name: _sha(p) for p in _draft_files(f)} for f in ("F1", "F3", "F5")}
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
    assert CO.letters_in_order(figs["F5"][0]) == (True, list("abcde"))                              # 13t-1d E14 (T1): (f) to (i) of the draft are (a) to (d) of F5c
    assert CO.letters_in_order(figs["F5c"][0]) == (True, list("abcd"))


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
    for ln, row in zip(lines, FG.strip_rows_of(fid, d)):
        assert JCAP.failed_line(row) in cap, ln               # 13t-1d (DL-575 E15): the journal caption holds the plain failed-check text of each row, the supplement the verbatim line
        assert ln in sup, ln
    assert CAP.RED_TITLE_NOTE.split(":")[0].lower() in cap.lower()          # the red-title definition is in the caption


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_caption_sentence_one_names_the_main_failure_and_has_the_take_home(built, fid):
    cap = built["out"][fid]["caption"]
    s1 = cap[len(fid) + 2:].split(". ")[0]
    for m in MAIN[fid]:
        assert m in s1, m
    if fid != "F5c":
        draft_cap = (ROOT / "figures" / fid / f"{fid}_caption.txt").read_text(encoding="utf-8")
        take = {"F1": FG.F1_TAKE_HOME, "F3": FG.F3_TAKE_HOME, "F5": FG.F5_TAKE_HOME}[fid]
        if fid != "F5":                                                     # the stored draft caption of F5 has the 13r wording of sentence 1; the constant has the T4 wording (DL-571)
            assert take in draft_cap
    assert "DRAFT" not in cap and "as ruled (DL" not in cap                 # the footer text is in the supplement, not in the caption


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_no_draft_decision_log_or_provenance_text_on_the_image(figs, fid):
    assert not JC.image_text_violations(figs[fid][0])


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_supplement_lists_every_strip_row_footer_and_parameters(built, figs, fid):
    sup = (built["base"] / "journal" / "supplement" / f"{fid}_supplement.md").read_text(encoding="utf-8")
    for r in FG.strip_rows_of(fid, figs[fid][1]):
        assert f"{r['rb_id']} {r['check_id']}" in sup
        assert r["status"] in sup
    assert "DRAFT" in sup and "as ruled" in sup and "Parameter table" in sup
    assert (built["base"] / "journal" / "supplement" / f"{fid}_source_data.csv").stat().st_size > 100
    alt = (built["base"] / "journal" / "supplement" / f"{fid}_alt_text.txt").read_text(encoding="utf-8")
    letters = {"F1": "abcdefghijk", "F3": "abcde", "F5": "abcde", "F5c": "abcd"}[fid]
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
    assert f"the Hopf point of the tau_d {d['headline_tau_d_ms']:g} ms slice of this panel" in cap and "drawn twice and not moved" in cap         # 13t-1d (DL-575 E19): the seven-paragraph wording
    assert f"eta_bar {d['headline_hopf_eta']:.3f}" in cap
    assert all(e.reason.strip() for e in CO.JOURNAL_ALLOW["F3"]) and len(CO.JOURNAL_ALLOW["F3"]) == 5


@needs
def test_r4_f5_titles_a_and_g_carry_fail_and_are_red_and_the_f1_caption_has_the_other_failed_checks(built, figs):
    from matplotlib.colors import to_hex
    from mprsurge.plotting import style as S
    red = S.figure_colour("fail_text").lower()
    fig = figs["F5"][0]
    titles = {ax.get_gid().split(":")[1]: ax for ax in fig.axes if (ax.get_gid() or "").startswith("panel:")}
    for letter in "abc":                                                       # 13t-1d (DL-575 E19, T1): F5 holds the draft panels (a) to (e); (g) is panel (b) of F5c
        ax = titles[letter]
        assert "FAIL" in ax.get_title(loc="left") and to_hex(ax._left_title.get_color()).lower() == red, letter
    assert sum("FAIL" in ax.get_title(loc="left") for ax in fig.axes) == 3
    assert "FAIL" not in titles["d"].get_title(loc="left") and "FAIL" not in titles["e"].get_title(loc="left")
    figc = figs["F5c"][0]
    tc = {ax.get_gid().split(":")[1]: ax for ax in figc.axes if (ax.get_gid() or "").startswith("panel:")}
    assert "FAIL" in tc["b"].get_title(loc="left") and to_hex(tc["b"]._left_title.get_color()).lower() == red
    assert sum("FAIL" in ax.get_title(loc="left") for ax in figc.axes) == 1
    cap = " ".join(built["out"]["F1"]["caption"].split())
    assert ("Other failed checks on the headline path are shown elsewhere: the RB2 headline class (kept in 7 of 10 seeds at the noise level sigma; threshold >= 8 of 10), "
            "the RB3(a) onset prediction on the testable in-range runs (0 of 6) and the RB3(b) classifier onset in F4, and the RB6 solver onset (181 ms against 1 ms) in F4 and FS4.") in cap
    alt5 = (built["base"] / "journal" / "supplement" / "F5_alt_text.txt").read_text(encoding="utf-8")
    alt5c = (built["base"] / "journal" / "supplement" / "F5c_alt_text.txt").read_text(encoding="utf-8")
    assert "network vs mean field, cells: FAIL" in alt5 and "step-halving check: FAIL" in alt5c         # 13t-1e (DL-587): the alt text names the plain titles of the image


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
    assert "which differ and overlap at this scale (stored values 50.170 to 50.924 s)" in " ".join(cap.split())
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
    assert not [e for fid in PILOT for e in CO.JOURNAL_ALLOW[fid] if "PROVISIONAL" in e.reason]          # 13t-1d (DL-575 E20, T10): S14 is decided, no provisional entry is left
    assert all(len(e.reason) > 40 for fid in PILOT for e in CO.JOURNAL_ALLOW[fid])


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_s4_the_journal_caption_has_no_ruling_code_and_no_dl_number_and_every_limit_is_in_plain_words_and_paired_in_the_supplement(built, fid):
    from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS
    cap = built["out"][fid]["caption"]
    assert not PL.FORBIDDEN.search(cap), PL.FORBIDDEN.findall(cap)
    ids = {"F1": FG.F1_CLAIM_LIMITS, "F3": FG.F3_CLAIM_LIMITS, "F5": FG.F5_CLAIM_LIMITS, "F5c": FG.F5_CLAIM_LIMITS}[fid]
    for i in ids:
        assert PL.PLAIN_LIMITS[i].rstrip(".") in cap, i
    sup = (built["base"] / "journal" / "supplement" / f"{fid}_supplement.md").read_text(encoding="utf-8")
    for i in ids:
        short, dls = CLAIM_LIMIT_LABELS[i]
        assert f"{i}: {short} ({', '.join(dls)})" in sup, i                    # the verbatim ruled text with its DL numbers
        assert PL.PLAIN_LIMITS[i].rstrip(".") in sup, i
    assert "Checks: " in cap                                                   # 13t-1d (DL-575 E19): the check, gate and rule IDs are defined in the key paragraph


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
    assert "the rows are the neurons of (i), in the same order" in built["out"]["F1"]["caption"]


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_s9_and_s13_no_code_names_on_any_journal_image_tau_d_has_the_underscore_psd_is_spelled_out(figs, fid):
    from matplotlib.text import Text
    fig = figs[fid][0]
    texts = [t.get_text() for t in fig.findobj(Text) if t.get_text()]
    for bad in ("path_hypoxia", "T_ramp_s", "tau_d_ms", "I_drive", "tau_ms", "eta_bar", "τd", "τ_d", "(Delta)", "N (N)", "ref_devalle"):       # 13t-1d (DL-575 E18, T3): tau_d is the form, the Greek tau-d is not
        assert not any(bad in s for s in texts), (fid, bad)
    assert not any("PSD" in s for s in texts)
    if fid == "F1":
        assert any("power spectral" in s for s in texts)
    if fid in ("F1", "F3", "F5"):
        assert any("tau_d" in s for s in texts)


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
    assert "power spectral" in cb.get_ylabel() and "density" in " ".join(cb.get_ylabel().split()) and "(dB)" in cb.get_ylabel()
    assert "J0" in _panel(f5, "e").get_ylabel() and "path start" in _panel(f5, "e").get_ylabel()
    assert _panel(f5, "d").get_title(loc="left") == "(d) post-hoc view P-1"
    assert _panel(f3, "e").get_title(loc="left") == "(e) paths, one row per path"
    cap5 = built["out"]["F5"]["caption"]
    assert "P-1 = a post-hoc view" in cap5 and "synaptic decay time" in cap5


# ---- 13t-1d (DL-571 T1 to T9; DL-575): new tests ------------------------------------------------------------------------------------------------------------------------------
import numpy as np                                    # noqa: E402
from mprsurge.plotting import jcaption as JCAP          # noqa: E402

FIGS4 = ("F1", "F3", "F5", "F5c")
LABELS7 = ("Panels. ", "Key and abbreviations. ", "Classifier and spectrogram settings. ", "Parameters. ", "Failed checks. ", "Limits. ")


def _cap(built, fid) -> str:
    return (built["base"] / "journal" / fid / f"{fid}_journal_caption_full.txt").read_text(encoding="utf-8")


@needs
def test_t1_f5_and_f5c_together_draw_exactly_the_arrays_of_the_draft_with_equal_digests(built):
    d = FG.prepare_F5(FG.load_F5())
    draft = FG.array_digests(d)
    provs = {f: json.loads((built["base"] / "journal" / f / f"{f}_journal_provenance.json").read_text(encoding="utf-8"))["journal"] for f in ("F5", "F5c")}
    a5, a5c = provs["F5"]["array_digests"], provs["F5c"]["array_digests"]
    assert set(a5) | set(a5c) == set(draft) == set(d)
    assert set(a5) & set(a5c) == set(FG.F5C_SHARED)
    for k in set(a5) | set(a5c):
        assert {**a5, **a5c}[k] == draft[k], k
    assert provs["F5"]["drawn_data_sha256"] == provs["F5c"]["drawn_data_sha256"] == DRAFT_DIGEST_FILES["F5"].read_text(encoding="utf-8").strip()
    assert provs["F5c"]["journal_file"] == "F5c" and provs["F5c"]["draft_figure"] == "F5"
    assert FG.journal_keys("F5", d) == sorted(a5) and FG.journal_keys("F5c", d) == sorted(a5c)


@needs
def test_t1_f5c_is_full_width_four_stacked_panels_with_marks_of_at_least_4_pt_and_nothing_hidden(figs, cfg):
    fig, d, _ = figs["F5c"]
    w, h = fig.get_size_inches()
    assert abs(w - cfg["page"]["main_width_in"]) < 1e-9 and h <= cfg["page"]["main_max_height_in"] + 1e-9
    panels = [ax for ax in fig.axes if (ax.get_gid() or "").startswith("panel:")]
    assert [ax.get_gid() for ax in panels] == ["panel:a", "panel:b", "panel:c", "panel:d"]
    tops = [ax.get_position().y1 for ax in panels]
    assert tops == sorted(tops, reverse=True)                                           # stacked, top to bottom
    assert all(abs(ax.get_position().width * w - FG.F5CJ_WIDTH) < 1e-6 for ax in panels)
    n_seed = n_ctrl = 0
    for ax in panels:
        for ln in ax.lines:
            gid = ln.get_gid() or ""
            if gid.startswith("seed ") or gid.startswith("control "):
                assert ln.get_markersize() >= 4.0 - 1e-9, gid
                n_seed += gid.startswith("seed ")
                n_ctrl += gid.startswith("control ")
    und = d["metric_undefined"]
    assert n_seed == 40 + sum(40 - int(und[:, k].sum()) for k in range(3))                                # every ramp seed with a defined value is a mark, in (a) all 40
    assert n_ctrl == 12 + int((~np.isnan(d["ctrl_f_pk_hz"])).sum()) + int((~np.isnan(d["ctrl_onset_s"])).sum())      # the controls have no duration


@needs
def test_t1_f5c_has_no_provisional_allow_list_entry_and_the_reference_line_entries_keep_their_reason(cfg):
    ents = CO.JOURNAL_ALLOW["F5c"]
    assert ents and all("PROVISIONAL" not in e.reason and e.reason.strip() for e in ents)
    assert {e.panel for e in ents} == {"b", "c", "d"} and all("stored" in e.reason for e in ents)
    for fid in ("F1", "F3", "F5", "F5c"):
        assert all("PROVISIONAL" not in e.reason for e in CO.JOURNAL_ALLOW.get(fid, ()))
    f5 = CO.JOURNAL_ALLOW["F5"]
    assert {e.panel for e in f5 if e.kind == "marker-cell"} >= {"c", "d"} and not any(e.panel in ("f", "g", "h", "i") for e in f5)
    assert all("stored" in e.reason for e in CO.JOURNAL_ALLOW["F3"])                      # T10: the F3 entries are for stored coincident positions only


@needs
def test_t1_f5_caption_points_to_f5c_and_f5c_sentence_one_names_its_main_failure(built):
    c5, c5c = _cap(built, "F5"), _cap(built, "F5c")
    assert "Per-seed results against N are in F5c" in c5
    s1 = c5c[len("F5c. "):].split(". ")[0]
    assert "RB6 network f_pk" in s1 and "per-N results" in s1
    sup = (built["base"] / "journal" / "supplement" / "F5c_supplement.md").read_text(encoding="utf-8")
    assert "(a) = draft (f), (b) = draft (g), (c) = draft (h), (d) = draft (i)" in sup
    assert "departure" not in c5 and "plan" not in c5c.lower().split()                      # the departure is logged and in the supplement, not in the caption
    assert "RB6 network_fpk_halving_dt" in sup


@needs
def test_t1_the_export_manifest_lists_the_f5c_files(built):
    m = J.write_export_manifest(built["base"] / "journal")
    text = m.read_text(encoding="utf-8")
    for f in ("F5c/F5c_journal.png", "F5c/F5c_journal.tiff", "F5c/F5c_journal.pdf", "F5c/F5c_journal_caption.txt", "supplement/F5c_supplement.md", "supplement/F5c_alt_text.txt", "supplement/F5c_source_data.csv"):
        assert f in text, f
    alt = (built["base"] / "journal" / "supplement" / "F5c_alt_text.txt").read_text(encoding="utf-8")
    assert all(f"Panel ({k}):" in alt for k in "abcd") and "Panel (e):" not in alt


@needs
@pytest.mark.parametrize("fid", ("F1", "F5", "F5c"))
def test_t2_the_caption_gives_the_stored_status_of_the_sigma_check_and_the_supplement_has_both_rows(built, fid):
    import csv as _csv
    a11 = list(_csv.DictReader(open(RES / "A11" / "a11_robustness.csv", newline="", encoding="utf-8")))
    st = JCAP.sigma_status(a11)
    assert (st["status"], st["verdict"]) == ("FAIL", "NOT INSIDE") and (f"{st['mf_std']:.6f}", f"{st['lo']:.6f}", f"{st['hi']:.6f}") == ("0.039522", "0.037989", "0.038920")
    cap = " ".join(_cap(built, fid).split())
    assert ("sigma check on the baseline standard deviation: FAIL, logged verdict NOT INSIDE; mean-field baseline std 0.039522 against the network range 0.037989 to 0.038920") in cap
    assert "checked, not confirmed" in cap and "0.0624" in cap
    sup = (built["base"] / "journal" / "supplement" / f"{fid}_supplement.md").read_text(encoding="utf-8")
    assert "sigma_check S8_baseline_std" in sup and "RB3 a_inrange_runs" in sup and "0 of 6 testable in-range runs" in sup and "S8 baseline std" in sup and "G4-C4" in sup


@needs
def test_t2_f1_caption_names_the_rb3a_onset_prediction_among_the_checks_shown_in_f4(built):
    cap = " ".join(_cap(built, "F1").split())
    assert "the RB3(a) onset prediction on the testable in-range runs (0 of 6)" in cap and "in F4" in cap


def test_t2_a_sigma_row_that_differs_from_the_stored_status_stops_the_build():
    import csv as _csv
    a11 = list(_csv.DictReader(open(RES / "A11" / "a11_robustness.csv", newline="", encoding="utf-8")))
    bad = [dict(r) for r in a11]
    for r in bad:
        if (r["rb_id"], r["check_id"]) == ("sigma_check", "S8_baseline_std"):
            r["logged_verdict"] = "INSIDE"
    with pytest.raises(JCAP.JCaptionError):
        JCAP.sigma_status(bad)
    bad2 = [dict(r) for r in a11]
    for r in bad2:
        if (r["rb_id"], r["check_id"]) == ("RB3", "a_inrange_runs"):
            r["pass_or_fail"] = "PASS"
    with pytest.raises(JCAP.JCaptionError):
        JCAP.rb3a_value(bad2)


@needs
@pytest.mark.parametrize("fid", FIGS4)
def test_t3_tau_d_has_the_underscore_on_every_image_and_the_caption_defines_it_once(figs, built, fid):
    from matplotlib.text import Text
    fig = figs[fid][0]
    texts = [t.get_text() for t in fig.findobj(Text) if t.get_text()]
    assert not any("τ" in s and "d" in s.split("τ", 1)[1][:1] for s in texts)             # no Greek tau followed by d on any image
    assert FG.JTAU == "tau_d"
    if fid != "F5c":
        assert any("tau_d" in s for s in texts), fid
    cap = _cap(built, fid)
    if "tau_d" in cap:
        assert cap.count("tau_d = synaptic decay time") == 1


@needs
def test_t4_f5_wording_203_cells_needed_in_sentence_one_the_line_under_a_and_the_take_home(built):
    s = "noisy subgrid agrees in 97 of 225 cells (43.1 percent; 203 cells needed)"
    assert s in FG.F5_TAKE_HOME and FG.F5_TAKE_HOME.startswith("Mean field only; network disagrees at 3 of 4 cells; " + s + ". ")
    assert FG.F5_LINE_A.endswith(s) and "203 cells needed" in FG.F5_MAIN_FAILURES
    assert _cap(built, "F5").startswith("F5. Mean field only; network disagrees at 3 of 4 cells; " + s + ". ")
    for f in ("F5", "F5c"):
        assert "203 needed" not in _cap(built, f)
    # the stored numbers behind the sentence
    d = FG.prepare_F5(FG.load_F5())
    assert (d["d24_n_agree"], d["sub_n"], d["d24_needed"]) == (97, 225, 203) and f"{100.0 * 97 / 225:.1f}" == "43.1"


@needs
@pytest.mark.parametrize("fid", FIGS4)
def test_t5_every_journal_image_has_at_least_0p10_in_of_white_margin_on_all_four_sides(built, fid):
    png = built["base"] / "journal" / fid / f"{fid}_journal.png"
    m = JC.margins_in(png)
    assert all(v >= 0.10 for v in m.values()), m
    assert not JC.margin_violations(png, 0.10)


def test_t5_margin_check_measures_the_non_white_box_of_a_synthetic_png(tmp_path):
    from PIL import Image
    im = Image.new("RGB", (600, 300), "white")
    for x in range(60, 540):
        for y in range(30, 270):
            im.putpixel((x, y), (0, 0, 0))
    p = tmp_path / "m.png"
    im.save(p, dpi=(600, 600))
    m = JC.margins_in(p)
    assert abs(m["left"] - 0.10) < 1e-3 and abs(m["right"] - (600 - 540) / 600) < 0.002 and abs(m["top"] - 0.05) < 1e-3
    assert JC.margin_violations(p, 0.10) and not JC.margin_violations(p, 0.04)


@needs
@pytest.mark.parametrize("fid", FIGS4)
def test_t6_an_x_label_is_at_least_0p05_in_above_the_next_panels_title(figs, fid):
    assert not JC.label_title_gaps(figs[fid][0], 0.05)


def test_t6_label_title_gap_check_finds_a_label_that_touches_the_next_title():
    fig = plt.figure(figsize=(3, 3))
    a = fig.add_axes([0.2, 0.55, 0.6, 0.3])
    a.set_xlabel("x label")
    b = fig.add_axes([0.2, 0.1, 0.6, 0.3])
    b.set_title("(b) title", loc="left")
    gap_axes = JC.label_title_gaps(fig, 0.05)
    fig2 = plt.figure(figsize=(3, 3))
    a2 = fig2.add_axes([0.2, 0.75, 0.6, 0.15])
    a2.set_xlabel("x label")
    b2 = fig2.add_axes([0.2, 0.1, 0.6, 0.3])
    b2.set_title("(b) title", loc="left")
    assert not JC.label_title_gaps(fig2, 0.05)
    plt.close("all")
    assert isinstance(gap_axes, list)


@needs
def test_t6_f1_colour_bar_label_vertical_line_labels_and_padded_y_limits(figs, built):
    fig, d, _ = figs["F1"]
    cb = next(a for a in fig.axes if a.get_gid() == "colour bar spectrogram")
    assert " ".join(cb.get_ylabel().split()) == "power spectral density (dB); same scale for (g) and (h)"
    leg = next(a for a in fig.axes if a.get_gid() == "legend axes").get_legend()
    labels = [t.get_text() for t in leg.get_texts()]
    assert any(t.startswith("ramp start and end") for t in labels) and any(t.startswith("J ramp start and end") for t in labels)
    by = {a.get_gid(): a for a in fig.axes if (a.get_gid() or "").startswith("panel:")}
    n = d["ras_n_rows"]
    for k in "ijk":
        lo, hi = by[f"panel:{k}"].get_ylim()
        assert lo <= -0.5 - FG.F1J_PAD_ROWS + 1e-9 and hi >= n - 0.5 + FG.F1J_PAD_ROWS - 1e-9, k
    assert f"padded by {FG.F1J_PAD_ROWS} rows" in " ".join(_cap(built, "F1").split())
    # the strip of event marks stays off the frame of its panel (0.05 in apart)
    strips = [a for a in fig.axes if (a.get_gid() or "") in ("panel:d", "panel:f") and a.get_ylim() == (0.0, 1.0)]
    assert len(strips) == 2


@needs
def test_t6_f1_schematic_arrows_into_outputs_are_apart_and_the_schematic_text_is_clear(figs):
    fig = figs["F1"][0]
    ax = next(a for a in fig.axes if a.get_gid() == "schematic")
    arrows = [c for c in ax.texts if hasattr(c, "arrow_patch") and c.arrow_patch is not None]
    ends = sorted(c.xy[1] for c in arrows if abs(c.xy[0] - 5.06) < 1e-6)
    assert len(ends) == 2 and (ends[1] - ends[0]) * 72.0 >= 4.0                           # the two arrows end at least 4 pt apart
    rows = {t.get_gid(): t.get_text() for t in ax.texts if (t.get_gid() or "").endswith(":rows")}
    assert "tau_d: Synaptic decay time (M3)" in rows["schematic:model:rows"]


@needs
def test_t7_f3_combined_path_is_thin_the_a6_marker_is_a_hollow_ring_of_4_pt_and_the_slice_hopf_marks_have_a_white_outline(figs):
    from matplotlib.patheffects import withStroke
    fig, d, _ = figs["F3"]
    heads = [t for ax in fig.axes for t in ax.texts if (t.get_gid() or "") == "arrow:tau_d:combined"]
    assert len(heads) == 1 and heads[0].arrow_patch.get_linewidth() <= 1.0 + 1e-9
    a6 = [ln for ax in fig.axes for ln in ax.lines if ln.get_gid() == "a6_hopf_point"]
    assert len(a6) == 2 and all(ln.get_markersize() <= 4.0 and ln.get_markerfacecolor() in ("none", "None") for ln in a6)
    sl = [ln for ax in fig.axes for ln in ax.lines if ln.get_gid() == "slice Hopf points"]
    assert len(sl) == 3
    for ln in sl:
        pe = ln.get_path_effects()
        assert pe and isinstance(pe[0], withStroke) and pe[0]._gc.get("foreground") == "white"


@needs
def test_t7_f3_caption_says_straight_segments_30_points_the_rb9b_frequencies_and_that_the_shading_has_no_spectral_value(built):
    cap = " ".join(_cap(built, "F3").split())
    assert "is drawn as straight segments between its 30 stored points" in cap
    assert "spectral peak is 49.0 Hz and the cycle frequency is 44.609 Hz" in cap and "4.391 Hz against 0.5 Hz" in cap
    assert "the shading shows the cycle frequency at J = -21, so it does not contain the spectral value" in cap
    import json as _json
    ev = _json.loads((RES / "A11" / "a11_evaluators.json").read_text(encoding="utf-8"))["evaluators"]["rb9b"]["headline"]
    assert (ev["f_spectral_hz"], round(ev["f_cycle_hz"], 3), round(ev["diff_hz"], 3)) == FG.F3_RB9B == (49.0, 44.609, 4.391)


@needs
@pytest.mark.parametrize("fid", FIGS4)
def test_t8_the_journal_caption_is_seven_labelled_paragraphs(built, fid):
    cap = _cap(built, fid).rstrip("\n")
    paras = cap.split("\n\n")
    assert len(paras) == 7 and paras[0].startswith(f"{fid}. ")
    for p, lab in zip(paras[1:], LABELS7):
        assert p.startswith(lab), (fid, lab)
    s1 = paras[0][len(fid) + 2:].split(". ")[0]
    main = {"F1": FG.F1_MAIN_FAILURES, "F3": FG.F3_MAIN_FAILURES, "F5": FG.F5_MAIN_FAILURES, "F5c": FG.F5C_MAIN_FAILURES}[fid]
    assert all(m in s1 for m in main)


@needs
@pytest.mark.parametrize("fid", FIGS4)
def test_t8_no_plan_milestone_table_dl_step_id_or_code_name_in_any_journal_caption(built, fid):
    cap = _cap(built, fid)
    assert not JCAP.FORBIDDEN.findall(cap), JCAP.FORBIDDEN.findall(cap)
    for bad in ("the plan", "milestone", "Table ", "DL-", "analysis.surge_metrics", "path_hypoxia", "ref_devalle", "DOP853", "model.tau_d_ms", "seeds.root_seed", "UNVERIFIED", "NC1", "S8", "S9", "A4", "A6", "A9", "A11"):
        assert bad not in cap, (fid, bad)
    for step in ("S8", "S9", "A4", "A6", "A9", "A11"):
        assert not re.search(rf"\b{step}\b", cap)


@needs
@pytest.mark.parametrize("fid", FIGS4)
def test_t8_every_check_gate_and_rule_id_in_a_caption_is_defined_in_its_key_paragraph(built, fid):
    paras = _cap(built, fid).rstrip("\n").split("\n\n")
    key = paras[2]
    rest = "\n\n".join(p for i, p in enumerate(paras) if i != 2)
    for ident, pat in (("RB1", r"\bRB1\b"), ("RB2", r"\bRB2\b"), ("RB3", r"\bRB3\b"), ("RB4", r"\bRB4\b"), ("RB6", r"\bRB6\b"), ("RB8", r"\bRB8\b"), ("RB9(b)", r"\bRB9\(b\)"),
                       ("G2", r"\bG2\b"), ("G4", r"\bG4\b"), ("G5", r"\bG5\b"), ("G7", r"\bG7\b"), ("D24", r"\bD24\b")):
        if re.search(pat, rest):
            assert re.search(re.escape(ident) + r"[^;.]* = ", key), (fid, ident)


@needs
@pytest.mark.parametrize("fid", FIGS4)
def test_t8_nc1_is_defined_as_the_plan_defines_it_and_the_milestone_9_wording_is_gone(built, fid):
    cap = " ".join(_cap(built, fid).split())
    nc1 = "the hypoxia path with the mean excitability falling by the same amount, with coupling, heterogeneity and synaptic decay fixed and no common drive"
    if fid == "F1":                                                           # the figure whose caption speaks of the negative control (gate G7) and of its limit
        assert nc1 in cap and cap.count(nc1) == 2                             # the key sentence and the plain sentence of the G7 limit
    assert nc1 in " ".join(PL.PLAIN_LIMITS["G7 not passed (plan label)"].split())
    if fid != "F3":
        assert "the limits ruled for the map, control and perturbation runs" in cap
    assert "milestone" not in cap.lower() and "the regime maps and their failure labels" not in cap


def test_t8_plain_limits_say_what_changed():
    assert "milestone" not in PL.PLAIN_LIMITS["MS11-C7"] and "the map, control and perturbation runs" in PL.PLAIN_LIMITS["MS11-C7"]
    assert "plan" not in PL.PLAIN_LIMITS["DL-163-D1"].lower().split()
    assert "no common drive" in PL.PLAIN_LIMITS["G7 not passed (plan label)"]


def test_t8_assemble_refuses_a_forbidden_word():
    ok = dict(take_home="a", panels="b", key="c", settings="d", parameters="e", failed="f", limits="g")
    assert JCAP.assemble("F1", **ok).count("\n\n") == 6
    for bad in ("see the plan", "milestone 9", "Table 2.1", "DL-388", "step A4", "the S9 sweep", "path_hypoxia", "DOP853", "seeds.root_seed", "UNVERIFIED"):
        with pytest.raises(JCAP.JCaptionError):
            JCAP.assemble("F1", **{**ok, "panels": bad})


@needs
def test_t9_the_journal_rows_of_the_independent_comparison_are_equal_for_the_built_captions(built):
    import importlib.util
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    for name in ("ms13_independent", "ms13_independent_compare"):
        spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    ind, cmpmod = sys.modules["ms13_independent"], sys.modules["ms13_independent_compare"]
    rows = ind.compute(figures=["F1", "F3", "F5"])
    figs_ = ["F1", "F3", "F5"]
    res = cmpmod.compare(rows, cmpmod.drawn_sets(figs_), cmpmod.journal_captions(built["base"] / "journal"))
    jr = [r for r in res if r["journal_equal"] != "n.a."]
    assert [r["id"] for r in jr if r["journal_equal"] != "yes"] == []
    for f in ("F1", "F3", "F5", "F5c"):
        assert sum(1 for r in jr if f in r["journal_files"].split(", ")) >= 5, f
    # every row of F1, F3, F5 that has a draft pattern has a journal pattern
    assert all(r["jprinted"] is not None for r in rows if r["figure"] in ("F1", "F3", "F5") and r["printed"] is not None)
    assert [r["id"] for r in res if r["equal"] in ("no", "unresolved")] == []
    # a caption that does not hold the number is found: alter the F1 journal caption in memory
    caps = cmpmod.journal_captions(built["base"] / "journal")
    caps["F1"] = caps["F1"].replace("classifier onset is 12.0 s", "classifier onset is 13.0 s")
    res2 = cmpmod.compare(rows, cmpmod.drawn_sets(figs_), caps)
    assert [r["id"] for r in res2 if r["journal_equal"] == "no"] == ["F1.onset120_text"]
    caps["F1"] = caps["F1"].replace("classifier onset is 13.0 s", "classifier onset was 13.0 s")
    res3 = cmpmod.compare(rows, cmpmod.drawn_sets(figs_), caps)
    assert "F1.onset120_text" in [r["id"] for r in res3 if r["journal_equal"] == "unresolved"]


@needs
def test_t12_the_f1_supplement_still_names_the_zip_of_the_source_data(built):
    sup = (built["base"] / "journal" / "supplement" / "F1_supplement.md").read_text(encoding="utf-8")
    assert "zipped for the Zenodo record" in sup
