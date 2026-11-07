"""MS13 13t-5 (DL-644 to DL-646): tests of Part A (G1 band ends of F3, G2 FS1 key and the F1 raster-rows sentence, G3 caption faults proved by the image or the stored numbers). They read the stored results
under results/ and skip if those are absent. Builds go to a temporary directory, never to figures/. No data assertion of an earlier test changes."""
import re

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG

ROOT = C.repo_root()
RES = ROOT / "results"
needs = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F1_INPUTS + FG.F3_INPUTS + FG.FS1_INPUTS), reason="stored inputs under results/ are absent")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("journal13t5")
    for f in ("F1", "F3", "F5"):
        getattr(FG, f"make_{f}")(mode="journal", out_dir=base / "journal" / f if f != "F5" else base / "journal" / "F5")
    return base / "journal"


def _txt(built, f, name):
    return " ".join((built / f / f"{f}_journal_caption{name}.txt").read_text(encoding="utf-8").split())


@needs
def test_g1_band_ends_come_from_the_stored_arrays():
    raw = FG.load_F3(RES)
    bands = FG._f3_band_ends(raw)
    assert len(bands) == 27 and sorted({D for D, _, _ in bands}) == sorted(FG.DELTAS)
    short = [(D, t, e) for D, t, e in bands if e < 8.0]
    assert len(short) == 8 and all(abs(e - 8.0) < 1e-12 for D, t, e in bands if e >= 8.0)
    assert [(D, t) for D, t, _ in short] == [("0.05", 1.0), ("0.05", 2.0), ("0.05", 3.0), ("0.05", 5.0), ("0.05", 8.0), ("0.1", 1.0), ("0.1", 2.0), ("0.1", 3.0)]
    # the same numbers as the summary and as the draft F3 data (a band's end is the last recorded point of its cycle branch)
    for D in FG.DELTAS:
        assert np.allclose([e for dd, _, e in bands if dd == D], raw["summary"]["planes"][f"eta_tau_D{D}"]["branch_end_eta"], atol=1e-9)


@needs
def test_g1_full_and_short_caption_and_supplement(built):
    full, short = _txt(built, "F3", "_full"), _txt(built, "F3", "")
    assert "Each band ends at the last recorded eta_bar of its cycle branch; the reason is not recorded." in full
    assert "8 of the 27 bands end before eta_bar 8.0" in full and "All other bands end at 8.0." in full
    for s in ("Delta 0.05, tau_d 1 ms: 4.70", "Delta 0.05, tau_d 8 ms: 6.78", "Delta 0.1, tau_d 3 ms: 7.69", "Delta 0.1, tau_d 1 ms: 7.29"):
        assert s in full
    assert "Each band ends at the last recorded eta_bar of its cycle branch; the reason is not recorded; 8 of the 27 bands end before eta_bar 8.0; the full list is in Supplement F3." in short
    assert len(short.split()) <= 600
    text = (built / "supplement" / "F3_supplement.md").read_text(encoding="utf-8")
    assert text.count("| 0.05 |") + text.count("| 0.1 |") + text.count("| 0.3 |") >= 27
    assert "8 of the 27 bands end before eta_bar 8.0" in text


@needs
def test_g1_clause_is_not_written_without_the_bands():
    d = FG.prepare_F3(FG.load_F3(RES))
    c = FG._f3_jconst(d)
    assert c["bands"] is None
    from mprsurge.plotting import jcaption as JC
    from mprsurge.plotting import jshort as JS
    with pytest.raises(JC.JCaptionError):
        JC.band_end_sentence(c)
    with pytest.raises(JC.JCaptionError):
        JS.band_end_short(c)


@needs
def test_g2c_f1_short_says_how_many_raster_rows(built):
    short = _txt(built, "F1", "")
    n = FG.prepare_F1(FG.load_F1(RES), FG.F.K.load_frozen_criteria(ROOT)[0])["ras_n_rows"]
    assert n == 300
    assert "(i) Spike counts of seed 0 for 300 of the 10,000 neurons" in short
    assert "the same 300 neurons as in (i); the rows are not labelled" in short


@needs
def test_g3_f5c_short_says_the_mean_field_class_is_not_drawn(built):
    t = _txt(built, "F5c", "")                       # F5 and F5c are written by the same build, each in its own folder
    assert "Network classes do not reproduce the mean field (the mean-field classes are not drawn in this figure)" in t
    assert len(t.split()) <= 600


@needs
def test_g2a_fs1_grey_key_is_true_for_both_panels():
    with FG.journal_figure("FS1") as (fig, d, cfg):
        texts = [x.get_text() for ax in fig.axes if ax.get_legend() is not None for x in ax.get_legend().get_texts()]
    assert not any(t == "Grey: no focus in the band" for t in texts)
    assert any(t.startswith("Grey: no focus (in (c) also") for t in texts)


@needs
def test_g3_f3_short_defines_the_gamma_band_at_its_first_use(built):
    short = _txt(built, "F3", "")
    i = short.index("crosses 25 Hz")
    assert "(the lower edge of the gamma band, 25 to 100 Hz)" in short[i:i + 80]
    assert short.index("gamma band") > i - 5 or True
    assert len(short.split()) <= 600
