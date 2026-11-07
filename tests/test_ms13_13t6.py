"""MS13 13t-6 (DL-650 to DL-653): tests of the FS profile v2 (H1: stand-alone FS files at the draft's size), the single FS caption (H2) and, as they are done, Part A (H4 to H6).
They read the stored results under results/ and skip if those are absent. Builds go to a temporary directory, never to figures/. No data assertion of an earlier test changes."""
import re

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import collide as CO
from mprsurge.plotting import jcaption as JCAP
from mprsurge.plotting import jchecks as JC
from mprsurge.plotting import journal as J
from mprsurge.plotting import jshort as JSH
from mprsurge.plotting import figures as FG

ROOT = C.repo_root()
RES = ROOT / "results"
needs = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.FS2_INPUTS), reason="stored inputs under results/ are absent")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("journal13t6")
    FG.make_FS2(mode="journal", out_dir=base / "journal" / "FS2")
    return base / "journal"


def test_config_fs_profile_v2_and_word_limit():
    cfg = J.load_config(ROOT)
    for f in ("FS2", "FS3", "FS4", "FS5"):
        assert J.width_limit(cfg, f) == 7.4 and J.height_limit(cfg, f) == 14.4
    assert J.width_limit(cfg, "FS1") == 6.3 and J.height_limit(cfg, "FS1") == 9.5          # FS1 stays as built
    for f in ("F1", "F2", "F3", "F5", "F5c", "F6"):
        assert J.caption_limit(cfg, f) == 650                                                  # DL-653 H6


@needs
def test_fs2_one_caption_seven_paragraphs_and_plain_words(built):
    assert not (built / "FS2" / "FS2_journal_caption_full.txt").exists()                       # H2: one caption only
    cap = (built / "FS2" / "FS2_journal_caption.txt").read_text(encoding="utf-8").strip()
    paras = cap.split("\n\n")
    labels = ["Panels.", "Key and abbreviations.", "Classifier and spectrogram settings.", "Parameters.", "Failed checks.", "Limits."]
    assert len(paras) == 7 and paras[0].startswith("FS2. ") and all(paras[i + 1].startswith(w + " ") for i, w in enumerate(labels))
    assert not JCAP.FORBIDDEN.search(cap) and not re.search(r"\bUNVERIFIED\b|\bcompanion\b|\bf_pk\b", cap)
    assert JSH.undefined_terms(cap) == []                                                      # every term defined where first used
    assert "failed check" in paras[0].split(". ")[1] or "failed check" in paras[0]             # the main failure is named in sentence 1
    for k in ("Amplitude squared: FAIL", "Frequency against J: FAIL"):
        assert f"as '{k}'" in cap                                                              # every red title is mapped
    assert not JCAP.key_unused_terms(cap)


@needs
def test_fs2_drawn_data_digest_equals_the_draft(built):
    draft = (ROOT / "figures" / "FS2" / "FS2_drawn_data_sha256.txt").read_text(encoding="utf-8").strip()
    mine = (built / "FS2" / "FS2_journal_drawn_data_sha256.txt").read_text(encoding="utf-8").strip()
    assert mine == draft == FG.drawn_data_sha256(FG.prepare_FS2(FG.load_FS2(RES)))


@needs
def test_fs2_size_text_margins_collisions_and_sentence_case():
    with FG.journal_figure("FS2", root=ROOT) as (fig, d, cfg):
        W, H = fig.get_size_inches()
        assert (round(W, 3), round(H, 3)) == (7.4, 11.2)                                       # the draft's size, no squeezing (H1)
        assert JC.text_sizes(fig, cfg["text"]["min_pt"]) == []
        bad, ok = CO.check(fig, pad_pt=cfg["collision"]["pad_pt"], allow=CO.JOURNAL_ALLOW.get("FS2", ()))
        assert bad == []
        assert all(("stored" in r or "reference line" in r or "ruled mark" in r) for _, r in ok)   # allow-list reasons: stored coincident positions, ruled mark sizes, reference lines
        assert JC.image_id_violations(fig) == [] and JC.plain_word_violations(fig) == [] and JC.image_text_violations(fig) == []
        assert J.lowercase_starts(fig) == [] and JC.tick_hyphens(fig) == []
        assert JC.non_colour_violations(fig) == []
        reds = JC.red_titles(fig)
        assert sorted(s for _, s in reds) == ["(b) Amplitude squared: FAIL", "(l) Frequency against J: FAIL"]
        names, c_bad = JC.cmap_report(fig, cfg)
        assert not c_bad


@needs
def test_fs2_png_margins_and_caption_numbers(built):
    mv = JC.margin_violations(built / "FS2" / "FS2_journal.png", 0.10)
    assert not mv
    d = FG.prepare_FS2(FG.load_FS2(RES))
    cap = " ".join((built / "FS2" / "FS2_journal_caption.txt").read_text(encoding="utf-8").split())
    for x in (f"{100 * d['fit_s4_up_max_resid_frac']:.2f}", f"{d['hopf_a4_ms']:.2f}", f"{d['k9_ratio'].max():.5f}"):
        assert x in cap
    for t in ("8.0", "20.0", "40.0"):
        assert f"{100 * d[f'k10_rel_change_{t}']:.1f}" in cap


needs3 = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.FS3_INPUTS), reason="stored inputs under results/ are absent")


@pytest.fixture(scope="module")
def built3(tmp_path_factory):
    base = tmp_path_factory.mktemp("journal13t6fs3")
    FG.make_FS3(mode="journal", out_dir=base / "journal" / "FS3")
    return base / "journal"


@needs3
def test_fs3_one_caption_digest_size_collisions_and_failures_shown(built3):
    assert not (built3 / "FS3" / "FS3_journal_caption_full.txt").exists()
    cap = (built3 / "FS3" / "FS3_journal_caption.txt").read_text(encoding="utf-8").strip()
    paras = cap.split("\n\n")
    assert len(paras) == 7 and paras[0].startswith("FS3. ") and not JCAP.FORBIDDEN.search(cap) and JSH.undefined_terms(cap) == [] and not JCAP.key_unused_terms(cap)
    d = FG.prepare_FS3(FG.load_FS3(RES))
    for r in d["strip"]:                                                                       # every failed row of the figure is in the caption in plain words
        assert JCAP.failed_line(r) in cap
    for x in ("97 of 225", "203 needed", "NOT EVALUABLE", "Lorentzian heterogeneity only"):
        assert x in cap
    draft = (ROOT / "figures" / "FS3" / "FS3_drawn_data_sha256.txt").read_text(encoding="utf-8").strip()
    assert (built3 / "FS3" / "FS3_journal_drawn_data_sha256.txt").read_text(encoding="utf-8").strip() == draft
    with FG.journal_figure("FS3", root=ROOT) as (fig, d2, cfg):
        assert tuple(round(v, 3) for v in fig.get_size_inches()) == (7.4, 12.6)
        assert JC.text_sizes(fig, cfg["text"]["min_pt"]) == []
        bad, ok = CO.check(fig, pad_pt=cfg["collision"]["pad_pt"], allow=CO.JOURNAL_ALLOW.get("FS3", ()))
        assert bad == [] and all("stored" in r for _, r in ok)
        assert JC.image_id_violations(fig) == [] and JC.plain_word_violations(fig) == [] and J.lowercase_starts(fig) == [] and JC.non_colour_violations(fig) == []
        assert sorted(s for _, s in JC.red_titles(fig)) == ["(e) Noise check: FAIL", "(g) 90 percent rule: FAILED"]
    assert not JC.margin_violations(built3 / "FS3" / "FS3_journal.png", 0.10)
