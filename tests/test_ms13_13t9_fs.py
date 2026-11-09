"""MS13 13t-9 (DL-681 N4): tests of the journal exports of FS4 and FS5 (stand-alone supplement files at the size of the draft, ONE plain caption each, DL-651 H1 and H2). They read the recorded results
under results/ and skip if those are absent. Builds go to a temporary folder, never to figures/."""
import re
import subprocess
import sys

import matplotlib
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jcaption as JCAP
from mprsurge.plotting import jfs4, jfs5
from mprsurge.plotting import jshort as JSH

ROOT = C.repo_root()
RES = ROOT / "results"
have4 = all((RES / p).is_file() for p in FG.FS4_INPUTS)
have5 = all((RES / p).is_file() for p in FG.FS5_INPUTS) and all((ROOT / p).is_file() for p in FG.FS5_TEST_FILES)


@pytest.fixture(scope="module")
def b4(tmp_path_factory):
    out = tmp_path_factory.mktemp("fs4")
    FG.make_FS4(mode="journal", out_dir=out / "FS4")
    return out


@pytest.fixture(scope="module")
def b5(tmp_path_factory):
    out = tmp_path_factory.mktemp("fs5")
    FG.make_FS5(mode="journal", out_dir=out / "FS5")
    return out


def _cap(base, fid):
    return (base / fid / f"{fid}_journal_caption.txt").read_text(encoding="utf-8")


@pytest.mark.skipif(not have4, reason="stored inputs absent")
def test_fs4_files_one_caption_seven_paragraphs_no_code(b4):
    t = _cap(b4, "FS4")
    assert not (b4 / "FS4" / "FS4_journal_caption_full.txt").exists()                     # H2: ONE caption
    paras = t.strip().split("\n\n")
    assert len(paras) == 7 and paras[0].startswith("FS4. ")
    assert [p.split(". ")[0] for p in paras[1:]] == ["Panels", "Key and abbreviations", "Classifier and spectrogram settings", "Parameters", "Failed checks", "Limits"]
    assert JSH.code_hits(t) == [] and not JSH.ID_PATTERN.search(t)                          # K4: no check, gate or key name
    assert JSH.undefined_terms(t) == []
    for f in ("FS4_journal.png", "FS4_journal.tiff", "FS4_journal.pdf"):
        assert (b4 / "FS4" / f).is_file()


@pytest.mark.skipif(not have4, reason="stored inputs absent")
def test_fs4_numbers_are_the_stored_ones_and_both_failures_are_named(b4):
    t = " ".join(_cap(b4, "FS4").split())
    assert "181 ms apart against 1 ms allowed" in t and "58.698 s and 58.879 s" in t.replace("(when the classifier, a rule fixed before the analysis, first flags the gamma rise) ", "")
    assert ("changes by 0 to 55 percent per halving of the time step (first halving 5 to 43 percent, second halving 0 to 33 percent, third halving 5 to 55 percent; the largest change, 55 percent, "
            "is at the third halving, seed 0), against 2 percent allowed (8 of the 9 changes are above it; 0 of 3 seeds pass") in t         # 13t-10 (DL-693): the range and the largest change over all stored halvings
    assert "passes in 2 of 3 seeds" in t
    assert "Numerical-convergence check, agreement of the two solvers on the onset of the main example: FAIL (181 ms; threshold 1 ms)" in t
    assert "Numerical-convergence check, the network peak frequency when the time step is halved: FAIL" in t
    for title in ("Onset by setting; solver check: FAIL", "Network peak frequency: FAIL", "Change per step halving: FAIL"):
        assert f"'{title}'" in t                                                           # every red title is mapped in the Failed checks paragraph
    assert "gives equal delays" in t and " ties " not in t


@pytest.mark.skipif(not have4, reason="stored inputs absent")
def test_fs4_size_digest_and_red_titles_with_evidence(b4):
    with FG.journal_figure("FS4") as (fig, d, cfg):
        w, h = fig.get_size_inches()
        assert (round(w, 2), round(h, 2)) == (7.4, 13.8)                                  # the size of the draft (H1)
        titles = {ax.get_gid(): ax.get_title(loc="left") for ax in fig.axes if str(ax.get_gid()).startswith("panel:")}
        assert sorted(titles) == [f"panel:{x}" for x in "abcdefghi"]
        red = [k for k, v in titles.items() if "FAIL" in v]
        assert sorted(red) == ["panel:a", "panel:f", "panel:g"]
        notes = [t.get_text() for ax in fig.axes for t in ax.texts if "FAIL" in t.get_text() or "percent allowed" in t.get_text()]
        assert any("Solver check: FAIL" in x and "181 ms" in x for x in notes)             # (a): the solver difference is on the panel
        assert any("5 to 43 percent" in x and "2 percent allowed" in x for x in notes)    # (f): the plain line that says why it is red; (g) draws the bound
        assert FG.drawn_data_sha256(d) == (ROOT / "figures" / "FS4" / "FS4_drawn_data_sha256.txt").read_text().strip() or not (ROOT / "figures" / "FS4" / "FS4_drawn_data_sha256.txt").is_file()


@pytest.mark.skipif(not have5, reason="stored inputs absent")
def test_fs5_files_one_caption_seven_paragraphs_no_code(b5):
    t = _cap(b5, "FS5")
    assert not (b5 / "FS5" / "FS5_journal_caption_full.txt").exists()
    paras = t.strip().split("\n\n")
    assert len(paras) == 7 and paras[0].startswith("FS5. ")
    assert JSH.code_hits(t) == [] and not JSH.ID_PATTERN.search(t)
    assert JSH.undefined_terms(t) == []
    assert "Frequency check, spectral frequency against cycle frequency at the main example: FAIL" in " ".join(t.split())
    assert "'Frequency check: FAIL'" in t


@pytest.mark.skipif(not have5, reason="stored inputs absent")
def test_fs5_numbers_and_the_replacement_of_stored_names_on_the_image(b5):
    t = " ".join(_cap(b5, "FS5").split())
    for s in ("49.0 Hz and the cycle frequency", "44.609 Hz", "a difference of 4.391 Hz against the allowed 1/W = 0.5 Hz", "306, 400, 172 and 24 of 500 white-noise records", "26 synthetic cases", "at most 1.67 percent of the 900 map-1 cells"):
        assert s in t
    with FG.journal_figure("FS5") as (fig, d, cfg):
        w, h = fig.get_size_inches()
        assert (round(w, 2), round(h, 2)) == (7.4, 14.4)
        texts = " ".join(x.get_text() for x in fig.findobj(matplotlib.text.Text))
        assert "N_burst" not in texts and "xfail" not in texts and "test_surge" not in texts and not re.search(r"\b[a-z]+_[a-z0-9]+_", texts)      # no stored case or test name on the image
        reds = [ax.get_title(loc="left") for ax in fig.axes if "FAIL" in ax.get_title(loc="left")]
        assert reds == ["(h) Frequency check: FAIL"]
        assert any("4.391 Hz" in t_.get_text() for ax in fig.axes for t_ in ax.texts)       # the difference is on the red panel


def test_fs5_plain_variant_labels_carry_the_numbers_of_the_stored_variant_names():
    names = ["band_30_120", "factors_1.5", "factors_4", "amin_0.05", "amin_0.2", "window_x0.5", "window_x2", "cycles_5", "cycles_20"]
    assert sorted(jfs5.VAR_LABELS) == sorted(["V0"] + names)
    for n in names:
        nums = re.findall(r"\d+(?:\.\d+)?", n)
        lab_nums = re.findall(r"\d+(?:\.\d+)?", jfs5.VAR_LABELS[n])
        assert nums == lab_nums, (n, jfs5.VAR_LABELS[n])
    assert jfs5.VBAND == (30, 120)


@pytest.mark.skipif(not (have4 and have5), reason="stored inputs absent")
def test_verifier_has_no_fail_for_fs4_and_fs5(b4, b5, tmp_path):
    import shutil
    base = tmp_path / "journal"
    (base).mkdir()
    for fid, src in (("FS4", b4), ("FS5", b5)):
        shutil.copytree(src / fid, base / fid)
        shutil.copytree(src / "supplement", base / "supplement", dirs_exist_ok=True)
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "ms13_verify_export.py"), "FS4", "FS5", "--dir", str(base)], capture_output=True, text=True, cwd=ROOT, encoding="utf-8")
    assert re.search(r"\b0 FAIL\b", r.stdout), r.stdout[-1500:]


def test_registrations_of_fs4_and_fs5():
    sys.path.insert(0, str(ROOT / "scripts"))
    import ms13_independent_compare as IC
    import ms13_verify_export as VE
    import fig_journal as FJ
    for fid in ("FS4", "FS5"):
        assert fid in VE.FS_SINGLE and fid in IC.FS_SINGLE and fid in IC.JOURNAL_FILES and fid in FJ.PILOT and fid in JCAP.UNCODE_FIGS and fid in JCAP.TITLE_MAP
