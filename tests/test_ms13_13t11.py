"""MS13 13t-11 (DL-699, DL-700): tests of P1 (FS4 marker wording, F4b duration floor, F4a alt-text delays), R1/R2 (duration floor read from the stored data, the F4b legend text) and P2 (the alt-text audit).
They read the recorded results under results/ and skip if those are absent; the alt-text audit reads the recorded journal build under figures/journal/ and skips if it is absent. Builds go to a temporary folder."""
import inspect
import re

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jaltaudit as AA
from mprsurge.plotting import jcaption as JCAP
from mprsurge.plotting import jf4, jf4cap, jfs4
from mprsurge.plotting import jshort as JSH

ROOT = C.repo_root()
RES = ROOT / "results"
haveF4 = (RES / "A3/a3_sn_ramp.parquet").is_file() and (RES / "A11/a11_evaluators.json").is_file() and all((RES / p).is_file() for p in FG.F4_INPUTS)
have4 = all((RES / p).is_file() for p in FG.FS4_INPUTS)
haveBuild = all((ROOT / f"figures/journal/supplement/{f}_alt_text.txt").is_file() and (ROOT / f"figures/journal/supplement/{f}_source_data.csv").is_file() for f in AA.IDS)


def _norm(t: str) -> str:
    return " ".join(t.split())


FAMS = ("p1_linear", "p1_sigmoid", "p2_linear", "p2_sigmoid", "p5_linear", "p5_sigmoid")


def _dur_arrays(short_min=0.3, floor=1.0):
    T = np.array([1.0, 10.0, 100.0, 1000.0])
    d = {}
    for f in FAMS:
        d[f"{f}_T_ramp_s"] = T
        d[f"{f}_duration_s"] = np.array([short_min, 5.0, floor, 50.0])
    d["noise_T_ramp_s"] = np.broadcast_to(T[:, None], (4, 10)).copy()
    d["noise_duration_s"] = np.full((4, 10), 7.0)
    return d


# ---- R1: the duration floor is read from the stored durations -------------------------------------------------------------------------------------------------------------------------

def test_r1_duration_facts_are_read_and_counted():
    f = jf4cap.duration_facts(_dur_arrays(), "60")
    assert (f["dur_T"], f["dur_floor"], f["dur_min"]) == (60.0, 1.0, 0.3)
    assert f["dur_n_short_below"] + f["dur_n_short_reach"] == f["dur_n_short"] and f["dur_n"] == 6 * 4 + 40
    assert f["dur_n_short_below"] == 6                                       # the six values of 0.3 s, all under 60 s


@pytest.mark.parametrize("kw, msg", [({"floor": 1.2}, "not exactly 1.0 s"), ({"short_min": 0.25}, "not 0.30 s")])
def test_r1_a_different_stored_value_stops_the_build(kw, msg):
    with pytest.raises(JCAP.JCaptionError, match=msg):
        jf4cap.duration_facts(_dur_arrays(**kw), "60")


def test_r1_the_wording_is_built_from_the_facts_and_has_no_range_for_shorter_ramps():
    f = {"dur_floor": 1.0, "dur_T": 60.0, "dur_min": 0.3}
    s = jf4cap.duration_floor_sentence(f)
    assert s == "durations are 1 s or more for ramp durations of 60 s or more; some faster ramps give shorter durations, down to 0.30 s"
    assert "0.94" not in s and "0.3 to" not in s
    f2 = dict(f, dur_min=0.25, dur_T=100.0)
    assert "100 s or more" in jf4cap.duration_floor_sentence(f2) and "0.25 s" in jf4cap.duration_floor_sentence(f2)       # nothing is typed


def test_r1_the_legend_text_is_a_template_over_the_read_facts():
    assert jf4._F4B_DURATION_LABEL == "Dotted line in (d): {dur_floor:g} s"                   # R2 fallback (attempt 2): the scope is in the caption and the alt text; the old claim 'the smallest duration' is gone
    assert "smallest" not in jf4._F4B_DURATION_LABEL


# ---- R3: the delays of F4a (a) ---------------------------------------------------------------------------------------------------------------------------------------------------------

def _delay_arrays(lo=-0.092041, hi=2.0):
    d = {}
    for i, f in enumerate(FAMS):
        d[f"{f}_eps"] = np.array([1.0, 2.0, 3.0])
        d[f"{f}_delay_eta_cross"] = np.array([0.1, 0.5, hi])
        d[f"{f}_delay_eta"] = np.array([0.1, 0.5, hi])
    d["p2_linear_delay_eta_cross"] = np.array([lo, 0.5, hi])
    return d


def test_r3_delay_facts_and_the_stop():
    f = jf4cap._delay_facts(_delay_arrays(), FAMS)
    assert round(f["delay_lo"], 3) == -0.092 and f["delay_hi"] == 2.0 and f["n_rising_with_rate"] == 6
    assert jf4._neg(f["delay_lo"]) == "−0.1"                            # true minus sign
    with pytest.raises(JCAP.JCaptionError, match="not -0.092 and 2.0"):
        jf4cap._delay_facts(_delay_arrays(hi=3.0), FAMS)


# ---- built texts of F4a and F4b -----------------------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def b4(tmp_path_factory):
    out = tmp_path_factory.mktemp("f4_13t11")
    FG.make_F4(mode="journal", out_dir=out)
    r = {}
    for f in ("F4a", "F4b"):
        r[f] = {k: _norm((out / f / f"{f}_journal_caption{k}.txt").read_text(encoding="utf-8")) for k in ("", "_full")}
        r[f]["alt"] = _norm((out / "supplement" / f"{f}_alt_text.txt").read_text(encoding="utf-8"))
    return r


FLOOR = "durations are 1 s or more for ramp durations of 60 s or more; some faster ramps give shorter durations, down to 0.30 s"


@pytest.mark.skipif(not haveF4, reason="stored inputs absent")
def test_p1b_f4b_texts_state_the_scoped_duration_floor(b4):
    for k in ("", "_full", "alt"):
        t = b4["F4b"][k]
        assert FLOOR in t, k
        assert "is the smallest duration the classifier can give" not in t and "the smallest duration the classifier can give" not in t
    for k in ("", "_full", "alt"):
        assert "smallest duration" not in b4["F4a"][k].replace("one window is the smallest duration, 1.0 s (1000 ms) for T_ramp >= 60 s", "")      # the scoped floor text of F4a is ruled wording
    assert len(b4["F4b"][""].split()) <= 650 and len(b4["F4a"][""].split()) <= 650


@pytest.mark.skipif(not haveF4, reason="stored inputs absent")
def test_p1c_f4a_alt_text_delays(b4):
    a = b4["F4a"]["alt"]
    assert "delays from about −0.1 to 2.0" in a
    assert "about 3" not in a and "as the ramp slows" not in a and "with the ramp rate" in a


@pytest.mark.skipif(not haveF4, reason="stored inputs absent")
def test_r2_the_f4b_legend_names_the_scope(tmp_path):
    import matplotlib.text as mtext
    with FG.journal_figure("F4b", root=ROOT) as (fig, d, cfg):
        texts = [t.get_text() for t in fig.findobj(mtext.Text)]
    assert any(t.startswith("Dotted line in (d): 1 s") for t in texts)
    assert "Dotted line in (d): 1 s, the smallest duration" not in texts


# ---- FS4 (a) and (c) ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def b4s(tmp_path_factory):
    out = tmp_path_factory.mktemp("fs4_13t11")
    FG.make_FS4(mode="journal", out_dir=out / "FS4")
    return _norm((out / "FS4" / "FS4_journal_caption.txt").read_text(encoding="utf-8")), _norm((out / "supplement" / "FS4_alt_text.txt").read_text(encoding="utf-8"))


@pytest.mark.skipif(not have4, reason="stored inputs absent")
def test_p1a_fs4_says_what_is_drawn(b4s):
    cap, alt = b4s
    assert "the small hollow downward triangle is the raw first crossing" in cap and "so the triangle lies on the mark" in cap
    assert "small cross" not in cap and "the cross lies" not in cap
    assert "small hollow downward triangle (the raw first crossing)" in alt and "and a cross at" not in alt
    assert "small and negative" not in alt and "level 0 from" in alt and "median" in alt
    from mprsurge.plotting import style as S
    assert "nabla" in S.diagram_mark("fs4_cross").marker_name                    # the marker name in the code (R4)


def test_p2_floor_delay_text_reports_both_signs_of_level_0():
    d = {"floor_l0_cross_delay": np.array([[-0.0026, 0.0033]]), "floor_l1_cross_delay": np.array([[-0.047, -0.037]]), "floor_l2_cross_delay": np.array([[-0.11, -0.096]])}
    t = jfs4._floor_delay_text(d)
    assert "level 0 from −0.0026 to 0.0033" in t and "level 2 from −0.11 to −0.096" in t


# ---- other alt-text fixes (P2) --------------------------------------------------------------------------------------------------------------------------------------------------------------

@pytest.mark.skipif(not (RES / "A11/a11_evaluators.json").is_file() or not all((RES / p).is_file() for p in FG.F6_INPUTS), reason="stored inputs absent")
def test_p2_f6_alt_names_the_largest_bar_of_each_map():
    d = FG.prepare_F6(FG.load_F6())
    t = FG._f6_alt_text(d)["a"]
    assert "the largest primary bar is label g (51) in map 1 and label f (16) in map 2" in t
    assert "any label, map 1: label g (70)" in t and "labels d and e are 0 in both maps" in t
    assert "(primary 51 and 13" not in t                                          # the old sentence put g first in both maps


def test_p2_wording_fixes_are_in_the_builders():
    assert "the top colour starts at" in inspect.getsource(FG._f1_alt_text) and "have more than" in inspect.getsource(FG._f1_alt_text)
    assert "tall black bar" not in inspect.getsource(FG._f3_alt_text) and "thin black vertical line" in inspect.getsource(FG._f3_alt_text)
    assert "coincide from 0.2 above the Hopf point" in inspect.getsource(FG._f2_alt_text)


# ---- the alt-text audit ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_p2_the_audit_can_fail(tmp_path, monkeypatch):
    sup = tmp_path / "figures/journal/supplement"
    sup.mkdir(parents=True)
    (sup / "F1_alt_text.txt").write_text("Panel (a): A line from eta_bar 1.396 to 4.8 between 5 s and 125 s.\n", encoding="utf-8")
    (sup / "F1_source_data.csv").write_text("panel,series,x,y,value\na,eta_bar(t) stored,0,1.39605,\na,eta_bar(t) stored,165,4.89605,\n", encoding="utf-8")
    monkeypatch.setattr(AA, "CHECKS", [("F1", "a", "eta_bar from to", r"from eta_bar (\S+) to (\S+) between",
                                        lambda r: (AA.Y(AA.sel(r, "F1", "a", startswith="eta_bar(t)")).min(), AA.Y(AA.sel(r, "F1", "a", startswith="eta_bar(t)")).max()))])
    AA._cache.clear()
    r = AA.rows(tmp_path)
    assert len(r) == 1 and r[0][5] is False and r[0][3] == ("1.396", "4.8") and r[0][4] == (1.39605, 4.89605)      # 4.8 is not 4.896 at the digits printed
    AA._cache.clear()


@pytest.mark.skipif(not haveBuild, reason="the recorded journal build under figures/journal is absent")
def test_p2_every_alt_text_claim_equals_the_source_data():
    AA._cache.clear()
    rows = AA.rows(ROOT)
    assert len(rows) >= 70
    old = "on the grey boundary" in (ROOT / "figures/journal/supplement/FS1_alt_text.txt").read_text(encoding="utf-8")      # 13x DL-718: the FS1 (b) row is compared once the recorded alt text holds the 13x sentence
    assert [r for r in rows if not r[5] and not (old and r[0] == "FS1" and r[2].startswith("grid steps and units"))] == []


# numbers of the alt texts that no check covers and that the caption of the same figure does not hold, each with its reason (D axis or drawing constant, S stored value checked below, G grid or notation)
ALLOW = {
    "F2": ["8"],                                           # D: the eta_bar axis ends at 8 (the stored sweeps end at 8)
    "F3": ["49"],                                          # S: the spectral peak 49 Hz, compared with the stored RB9(b) value below
    "F5c": ["1e3", "3e3", "1e4", "3e4", "49"],             # G: the four N of the grid in the notation of the alt text (open item: plain notation); 49 Hz the matching mean-field run (the caption writes 49.0)
    "FS2": ["2.5", "10.5", "0.99", "1.01"],                # D: axis limits of (a); the dashed target lines of (j) (stored target 1 percent)
    "FS4": ["58.65", "58.93"],                             # D: the x axis range of (a)
}


@pytest.mark.skipif(not haveBuild, reason="the recorded journal build under figures/journal is absent")
def test_p2_no_number_of_an_alt_text_is_left_uncompared():
    AA._cache.clear()
    left = AA.coverage(ROOT, ALLOW)
    assert left == [], left


@pytest.mark.skipif(not (RES / "A11/a11_evaluators.json").is_file(), reason="stored inputs absent")
def test_p2_the_allow_listed_stored_numbers_equal_the_stored_values():
    from mprsurge.plotting import jnumaudit as NA
    q = NA.stored(ROOT)
    assert int(q["rb9b_spec"]) == 49 and 0.9 < q["rb9b_bound"] + 0.5 < 1.1
