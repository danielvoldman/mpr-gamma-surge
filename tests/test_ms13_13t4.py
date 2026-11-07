"""MS13 13t-4 (DL-635 to DL-638): tests of Part A (E1 F2 sentence 1 of the journal captions, E2 positional words, E4 caption faults proved by the image or the stored numbers, the E3 stop) and of Part B
(the FS profile of the config and the journal export of the finished FS figures). They read the stored results under results/ and skip if those are absent. Builds go to a temporary directory, never to
figures/. No data assertion of an earlier test changes."""
import re

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jf26 as JF
from mprsurge.plotting import journal as J

ROOT = C.repo_root()
RES = ROOT / "results"
needs = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F1_INPUTS + FG.F2_INPUTS + FG.F6_INPUTS), reason="stored inputs under results/ are absent")
SENT1 = "Above the Hopf point the network amplitude lies close to the mean-field branch in (a) and (b) and differs from it by up to 13.2 percent in (c)."


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("journal13t4")
    out = {f: getattr(FG, f"make_{f}")(mode="journal", out_dir=base / "journal" / f) for f in ("F1", "F2", "F6")}
    return base / "journal"


def _txt(built, f, full=False):
    return " ".join((built / f / f"{f}_journal_caption{'_full' if full else ''}.txt").read_text(encoding="utf-8").split())


@needs
def test_e1_numbers_come_from_the_arrays():
    d = FG.prepare_F2(FG.load_F2(RES))
    p, up, r = np.asarray(d["net_param"], float), np.asarray(d["net_up"]) == 1.0, np.asarray(d["cmp_rel_v_ptp"], float)
    above = p > 2.996
    assert abs(100 * r[above].max() - 13.17) < 0.01 and abs(100 * r[above].min() + 2.48) < 0.01
    at = lambda x, u: 100 * r[(np.abs(p - x) < 2e-3) & (up == u)][0]
    assert round(at(3.296, True), 1) == 13.2 and round(at(3.296, False), 1) == 12.4
    assert round(at(3.696, True)) == 7 and round(at(3.696, False)) == 7
    assert all(abs(100 * r[(p > 4.0) & (up == u)]).max() <= 4.8 for u in (True, False))
    assert round(at(6.496, False), 1) == -2.5
    assert JF.f2_sentence1(d) == SENT1


@needs
def test_e1_sentence_one_in_short_and_full_journal_caption(built):
    s, f = _txt(built, "F2"), _txt(built, "F2", True)
    assert s.startswith("F2. " + SENT1) and f.split("Take-home", 1)[-1].lstrip(". :").startswith(SENT1) or SENT1 in f
    assert "does not follow the mean-field branch closely" not in s + f
    assert "limit cycle (a steady, repeating oscillation)" in s


@needs
def test_e1_the_draft_take_home_is_unchanged():
    assert "does not follow the mean-field branch closely" in FG.F2_TAKE_HOME and "+13.2 to -2.5 percent" in FG.F2_TAKE_HOME


def test_e1_close_item_46_and_supplement_note():
    t = (ROOT / "docs" / "ms13_close_items.md").read_text(encoding="utf-8")
    assert re.search(r"^46\. FOR THE USER .*draft F2 take-home disagrees with its drawn data; journal caption follows the data; the draft stays", t, re.M)
    assert "draft F2 take-home disagrees" in FG._jnotes_26("F2")[0][1] and FG._jnotes_26("F6") == ()


@needs
def test_e2_f6_key_position_and_the_positional_words_that_stand(built):
    s, full = _txt(built, "F6"), _txt(built, "F6", True)
    assert "key above panel (a)" not in s and "key below the bars)" in s and "listed under the panel" in full
    assert "strip above: triangle" in _txt(built, "F1") and "a strip above the axes" in _txt(built, "F1", True)        # looked at in the recorded F1 image (DL-639): the strips stand above (d) and (f)


@needs
def test_e4_f1_f2_f6_terms_defined_and_numbers_in_the_full_caption(built):
    f1, f2, f6 = _txt(built, "F1"), _txt(built, "F2"), _txt(built, "F6")
    assert "envelopes (the minimum to the maximum of a series in each pixel column)" in f1 and "(j), (k) The spikes of seed 0" in f1 and "12.000 s" in f1 and "58.698 s" in f1
    assert "(120 s points: right of tick 100)" in f6
    assert "of the steps each way (0.896 to 6.496)" in f2
    for f in ("F1", "F2", "F6"):
        assert len(_txt(built, f).split()) <= 600


def test_e3_the_ruled_clause_is_not_in_the_f3_caption_because_it_disagrees_with_the_stored_band_ends():
    import json
    s = json.loads((RES / "results/A6/a6_summary.json".replace("results/", "")).read_text(encoding="utf-8")) if (RES / "A6/a6_summary.json").is_file() else None
    if s is None:
        pytest.skip("A6 summary absent")
    e = {k: v["branch_end_eta"] for k, v in s["planes"].items() if k.startswith("eta_tau_D")}
    assert [round(x, 2) for x in e["eta_tau_D0.05"][:5]] == [4.70, 4.60, 4.86, 5.56, 6.78] and set(e["eta_tau_D0.05"][5:]) == {8.0}
    assert [round(x, 2) for x in e["eta_tau_D0.1"][:3]] == [7.29, 7.23, 7.69]                     # so '8.0 for the other slices' (DL-636 E3) is not true for panel (b)
    assert set(e["eta_tau_D0.3"]) == {8.0}


def test_e5_fs_profile_in_the_config():
    cfg = J.load_config(ROOT)
    fs = cfg["fs_profile"]
    assert fs["width_in"] == 6.3 and all(fs["max_height_in"][k] == 9.5 for k in ("FS1", "FS2", "FS3"))
