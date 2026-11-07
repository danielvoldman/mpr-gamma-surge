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
from mprsurge.plotting import jchecks as JK
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
        assert J.caption_limit(cfg, f) == 650, f              # DL-628 C6 (was 520, DL-615 A6)
    assert cfg["caption"]["short_max_words"] == 600


@needs
def test_a6_pilot_short_captions_fit(built):
    for f in PILOT:
        assert JS.words(_short(built, f)) <= 600, f


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


# ================================ Part B: the journal export of F2 and F6 (DL-616 B1 to B7, DL-620, DL-621) ================================
import csv
import importlib.util

from mprsurge.plotting import collide as CO
from mprsurge.plotting import jcaption as JCAP

B_FIGS = ("F2", "F6")
B_INPUTS = {"F2": FG.F2_INPUTS, "F6": FG.F6_INPUTS}
needs_b = pytest.mark.skipif(not all((RES / p).is_file() for f in B_FIGS for p in B_INPUTS[f]), reason="stored F2 and F6 inputs under results/ are absent")
PLAIN_BAN = ("stored", "headline", "companion", "mode D", "f_pk", "P-1", "path time", "continuation record", "frequency-map slice")
A_DEFINED = ("surge", "classes S+", "S-rel", "S-abs", "S-sus", "NS", "D-tr", "D-sus", "D-none", "mean field", "network", "main example", "hypoxia-like path P2", "Hopf point", "slice", "map cell",
             "noisy subgrid", "ramp seed", "control", "onset", "duration", "first crossing")


@pytest.fixture(scope="module")
def builtb(tmp_path_factory):
    base = tmp_path_factory.mktemp("journal13t2b")
    out = {f: getattr(FG, f"make_{f}")(mode="journal", out_dir=base / "journal" / f) for f in B_FIGS}
    return {"base": base / "journal", "out": out}


@pytest.fixture(scope="module")
def verify():
    spec = importlib.util.spec_from_file_location("ms13_verify_export", ROOT / "scripts" / "ms13_verify_export.py")
    VE = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(VE)
    return VE


def _txt(built, f, name):
    return (built["base"] / f / f"{f}_journal_{name}.txt").read_text(encoding="utf-8").strip()


@needs_b
def test_b_digest_of_each_journal_figure_equals_its_draft(builtb):
    for f in B_FIGS:
        draft = (ROOT / "figures" / f / f"{f}_drawn_data_sha256.txt").read_text(encoding="utf-8").strip()
        assert builtb["out"][f]["drawn_sha256"] == draft, f


@needs_b
def test_b_all_verifier_checks_pass_for_f2_and_f6(builtb, verify):
    with open(ROOT / "docs" / "ms13_figure_manifest.csv", newline="", encoding="utf-8") as fh:
        manifest = {(r["figure"], r["file"]): r["sha256"] for r in csv.DictReader(fh)}
    for f in B_FIGS:
        res, info = verify.check_figure(f, builtb["base"], ROOT, manifest)
        assert [c for c, (st, _) in res.items() if st == "FAIL"] == [], (f, {c: v for c, v in res.items() if v[0] == "FAIL"})
        assert set(verify.CHECKS) == set(res)
        W, H = info["inches"]
        assert abs(W - 6.3) < 1e-9 and H <= 8.0 + 1e-9
        m = info["margins"]
        assert min(m.values()) >= 0.10, (f, m)


@needs_b
def test_b_short_captions_limits_definitions_and_counts(builtb):
    cfg = J.load_config(ROOT)
    for f in B_FIGS:
        short, full = _txt(builtb, f, "caption"), _txt(builtb, f, "caption_full")
        assert JS.words(short) <= J.caption_limit(cfg, f) <= 650, f
        assert JS.undefined_terms(short) == [], f
        assert JS.limits_missing(f, short) == [], f
        assert JS.numbers_not_in_full(short, full) == [], f
        assert JS.parameters_numbers_missing(short, full) == [], f
        assert short.endswith(JS.POINTER.format(fid=f))
        assert JS.further_sentence(f, full) in short
        for w in PLAIN_BAN:
            assert not re.search(rf"\b{re.escape(w)}\b", short), (f, w)
        assert not JCAP.FORBIDDEN.search(short) and not JS.ID_PATTERN.search(short)
    assert JS.further_count("F2", _txt(builtb, "F2", "caption_full")) == 0 and "No other failed check is about this figure" in _txt(builtb, "F2", "caption")       # DL-628 C1: the four RB1 rows are named in the red-title sentence (were 4 further failed checks)
    assert "No other failed check is about this figure" in _txt(builtb, "F6", "caption")


@needs_b
def test_b_full_captions_have_seven_paragraphs_and_the_failed_rows(builtb):
    for f in B_FIGS:
        full = _txt(builtb, f, "caption_full")
        paras = full.split("\n\n")
        assert len(paras) == 7 and paras[0].startswith(f"{f}. ")
        assert JS.failed_in_full(full) == ({("RB1", "headline_10s"), ("RB1", "headline_120s"), ("RB1", "cells_30s"), ("RB1", "overall")} if f == "F2" else {("G7", "gate")})
        assert not re.search(r"\bNC1\b|UNVERIFIED|\bD8\b", full)


@needs_b
def test_b_red_titles_and_plain_words_on_the_images():
    for f, n_red in (("F2", 1), ("F6", 1)):                  # DL-628 C1: F2 (c) has the red title
        with FG.journal_figure(f, close=False) as (fig, d, cfg):
            fig.canvas.draw()
            texts = [" ".join(t.get_text().split()) for t in fig.findobj(matplotlib.text.Text) if t.get_text() and t.get_visible()]
            reds = [t for t in texts if "FAIL" in t]
        plt.close("all")
        assert len(reds) == n_red, (f, reds)
        for t in texts:
            for w in PLAIN_BAN:
                assert not re.search(rf"\b{re.escape(w)}\b", t), (f, t)
            assert not JS.ID_PATTERN.search(t) and "NC1" not in t and "^" not in t and not JK.E_NOTATION.search(t), (f, t)
        if f == "F6":
            assert "negative-control check: fail" in " ".join(reds).lower() and "S+" in texts


@needs_b
def test_b_allow_list_has_reasons_and_no_provisional_entry():
    for f in B_FIGS:
        entries = CO.JOURNAL_ALLOW[f]
        assert entries and all(e.reason and "PROVISIONAL" not in e.reason for e in entries)
    for f, es in CO.JOURNAL_ALLOW.items():
        assert all("PROVISIONAL" not in e.reason for e in es), f


@needs_b
def test_b_supplement_source_data_and_alt_text(builtb):
    sup = builtb["base"] / "supplement"
    for f in B_FIGS:
        text = (sup / f"{f}_supplement.md").read_text(encoding="utf-8")
        assert "plain text on the image" in text and "stored key names" in text.lower() or "Stored names behind" in text
        assert (sup / f"{f}_source_data.csv").stat().st_size / 1e6 < 20
        assert (sup / f"{f}_alt_text.txt").read_text(encoding="utf-8").startswith("Panel (a)")
    assert "Negative-control check: FAIL" in (sup / "F6_supplement.md").read_text(encoding="utf-8")            # DL-628 C9: the plain title as drawn


@needs_b
def test_b_part_a_clauses_survive_in_the_pilot_checklist_items():
    items = {i["id"]: i for i in __import__("json").load(open(ROOT / "docs" / "ms13_export_checklist.json", encoding="utf-8"))["items"]}
    for k in ("X-A1-f5c-duration-legend-caption", "X-A6-word-limit-520", "X-F2-B1-image", "X-F6-B3-captions"):
        assert k in items
