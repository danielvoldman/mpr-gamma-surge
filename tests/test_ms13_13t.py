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
    assert cfg["page"]["double_column_width_in"] <= 7.5 and cfg["page"]["max_height_in"] <= 8.75
    assert cfg["text"]["min_pt"] >= 8 and cfg["text"]["pdf_fonttype"] == 42 and cfg["text"]["ps_fonttype"] == 42
    assert cfg["lines"]["min_width_pt"] >= 0.3 and cfg["output"]["dpi"] == 300 and cfg["output"]["tiff_dpi"] == 600
    assert set(cfg["colour"]["allowed_cmaps"]) == {"magma", "viridis", "cividis"}
    assert not set(cfg["colour"]["allowed_cmaps"]) & set(cfg["colour"]["forbidden_cmaps"])
    fam, fallback = J.font_choice(cfg)
    assert fam in ("Arial", "Helvetica", "DejaVu Sans") and (fallback == (fam == "DejaVu Sans"))
    assert re.fullmatch(cfg["files"]["name_pattern"], "F1_journal.pdf") and not re.fullmatch(cfg["files"]["name_pattern"], "F1 journal.pdf")


def test_page_size_refuses_a_figure_that_is_too_tall(cfg):
    with pytest.raises(J.JournalError):
        J.page_size(cfg, cfg["page"]["max_height_in"] + 0.5)
    assert J.page_size(cfg, 8.0) == (cfg["page"]["double_column_width_in"], 8.0)


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
    assert w <= cfg["page"]["double_column_width_in"] + 1e-9 and h <= cfg["page"]["max_height_in"] + 1e-9
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
    assert w <= cfg["page"]["double_column_width_in"] + 0.01 and h <= cfg["page"]["max_height_in"] + 0.01
    if J.font_choice(cfg)[0] != "DejaVu Sans":
        assert any(J.font_choice(cfg)[0] in f for f in r["basefonts"])


@needs
@pytest.mark.parametrize("fid", PILOT)
def test_exported_files_png_tiff_names(built, figs, cfg, fid):
    base = built["base"] / "journal"
    out = base / fid
    from PIL import Image
    W, H = figs[fid][0].get_size_inches()
    assert Image.open(out / f"{fid}_journal.png").size == (round(W * 300), round(H * 300))
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
    for ln in lines:
        assert ln in cap, ln
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
    assert take in cap and take in draft_cap
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
    assert any("P1, P2, P3, P5: identical in" in t for t in legend_texts)


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
