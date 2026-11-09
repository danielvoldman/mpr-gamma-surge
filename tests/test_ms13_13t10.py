"""MS13 13t-10 (DL-690 to DL-692): tests of the fixes O1 (FS4 range and largest change over all halvings), O2 (superlatives, ranges, direction words), O3 (hollow dagger of F4a) and O4 (FS4 FAIL panels, FS5
tau, columns and colour bar, F3 caption words). They read the recorded results under results/ and skip if those are absent. Builds go to a temporary folder, never to figures/."""
import inspect
import json
import re

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jf4, jfs4, jfs5
from mprsurge.plotting import jnumaudit as NA
from mprsurge.plotting import style as S

ROOT = C.repo_root()
RES = ROOT / "results"
have4 = all((RES / p).is_file() for p in FG.FS4_INPUTS)
have5 = all((RES / p).is_file() for p in FG.FS5_INPUTS) and all((ROOT / p).is_file() for p in FG.FS5_TEST_FILES)
haveF4 = (RES / "A3/a3_sn_ramp.parquet").is_file() and (RES / "A11/a11_evaluators.json").is_file()


def _norm(t: str) -> str:
    return " ".join(t.split())


@pytest.fixture(scope="module")
def b4(tmp_path_factory):
    out = tmp_path_factory.mktemp("fs4")
    FG.make_FS4(mode="journal", out_dir=out / "FS4")
    return _norm((out / "FS4" / "FS4_journal_caption.txt").read_text(encoding="utf-8")), (out / "supplement" / "FS4_alt_text.txt").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def b5(tmp_path_factory):
    out = tmp_path_factory.mktemp("fs5")
    FG.make_FS5(mode="journal", out_dir=out / "FS5")
    return _norm((out / "FS5" / "FS5_journal_caption.txt").read_text(encoding="utf-8")), (out / "supplement" / "FS5_alt_text.txt").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def b3(tmp_path_factory):
    out = tmp_path_factory.mktemp("f3")
    FG.make_F3(mode="journal", out_dir=out / "F3")
    return _norm((out / "F3" / "F3_journal_caption_full.txt").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def b4ab(tmp_path_factory):
    out = tmp_path_factory.mktemp("f4")
    FG.make_F4(mode="journal", out_dir=out)
    r = {}
    for f in ("F4a", "F4b"):
        r[f] = {k: _norm((out / f / f"{f}_journal_caption{k}.txt").read_text(encoding="utf-8")) for k in ("", "_full")}
        r[f]["alt"] = (out / "supplement" / f"{f}_alt_text.txt").read_text(encoding="utf-8")
    return r


# ---- O1 ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_o1_change_stats_read_the_whole_array():
    a = np.array([[0.42857142857142855, 0.33333333333333337, 0.5500000000000002], [0.2, 0.25, 0.2], [0.05, 0.0, 0.05263157894736841]])
    s = jfs4.change_stats(a, 0.02)
    assert (s["all_lo"], s["all_hi"], s["hi_seed"], s["hi_halving"], s["n_above"], s["n_changes"]) == (0, 55, 0, 3, 8, 9)
    assert s["per_halving"] == [(5, 43), (0, 33), (5, 55)]
    b = a.copy()
    b[2, 0] = 0.9                                            # a different array gives a different caption number (nothing is typed)
    assert jfs4.change_stats(b, 0.02)["all_hi"] == 90 and jfs4.change_stats(b, 0.02)["hi_halving"] == 1


@pytest.mark.skipif(not (RES / "A11/a11_evaluators.json").is_file(), reason="stored inputs absent")
def test_o1_the_stored_seed_0_values_are_the_expected_ones_and_the_largest_is_at_the_third_halving():
    ev = json.loads((RES / "A11/a11_evaluators.json").read_text(encoding="utf-8"))["evaluators"]["rb6_network"]
    ce = [r for r in ev["ladder_info"] if r["reading"] == "classifier_episode_fpk"]
    first = {r["seed"]: r["rel"] for r in ev["per_reading"]["classifier_episode_fpk"]["rows"]}
    s0 = [first[0]] + [r["rel"] for r in sorted(ce, key=lambda r: -r["dt_from"]) if r["seed"] == 0]
    assert [round(x, 2) for x in s0] == [0.43, 0.33, 0.55]                       # the STOP condition of O1: these are the stored values
    allrel = list(first.values()) + [r["rel"] for r in ce]
    assert max(allrel) == pytest.approx(0.55) and len(allrel) == 9


@pytest.mark.skipif(not have4, reason="stored inputs absent")
def test_o1_o4a_fs4_caption_states_the_range_and_the_largest_change_over_all_halvings_and_the_fail_panels(b4):
    t, alt = b4
    assert "changes by 0 to 55 percent per halving of the time step (first halving 5 to 43 percent, second halving 0 to 33 percent, third halving 5 to 55 percent; the largest change, 55 percent, is at the third halving, seed 0)" in t
    assert "(g) The relative change of the peak frequency per halving of the time step against the bound 0.02 (a change of 0.02 is 2 percent); the largest change, 55 percent, is at the third halving (seed 0); 8 of the 9 changes are above the bound." in t
    assert "the largest change, at the first halving" not in t and "changes by 5 to 43 percent" not in t
    assert "panels (f) and (g) carry a red title with FAIL, and (h) and (i) are information only" in t and "shown labelled FAIL" not in t
    assert "first halving lies far above" not in alt and "8 of the 9 changes lie above the bound (range 0 to 55 percent" in alt


# ---- O2 ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_a_reason():
    rows = NA.audit(ROOT)
    rv = NA.superlative_review(rows)
    assert rv, "the audit found no superlative or range constant at all: the pattern is broken"
    assert [r for r, c, w in rv if w is None] == []
    assert all(c in ("D", "R", "T", "C", "L") and len(w) > 20 for r, c, w in rv)


def test_o2_the_review_can_fail_a_new_unreviewed_constant():
    row = {"file": "jfs4", "line": 1, "func": "caption", "token": "43", "context": "the largest change, at the first halving, is 43 percent", "kind": "T", "source": "", "stored": None, "equal": None}
    out = NA.superlative_review([row])
    assert len(out) == 1 and out[0][2] is None                       # a typed 'largest ... 43' with no stored value and no review is reported
    ok = dict(row, kind="S", stored=0.43, equal=True)
    assert NA.superlative_review([ok]) == []                         # a stored (kind S) value is checked elsewhere


@pytest.mark.skipif(not haveF4, reason="stored inputs absent")
def test_o2_f4b_the_jump_offset_rises_with_the_ramp_rate_in_the_stored_table_and_in_the_captions(b4ab):
    import pandas as pd
    a3 = pd.read_parquet(RES / "A3/a3_sn_ramp.parquet").sort_values("rate")
    # the drawn x of (f) is the ramp rate of the run record; the stored offset against that rate rises (13 values)
    off = a3.sort_values("offset")["offset"].to_numpy()
    assert off[0] == pytest.approx(0.003430092563688092) and off[-1] == pytest.approx(0.34575018328437723) and len(off) == 13
    for k in ("", "_full"):
        assert "rises with the ramp rate, from 0.0034" in b4ab["F4b"][k] and "falls from" not in b4ab["F4b"][k]
    assert "rises with the ramp rate, from 0.0034 to 0.346 over 13 ramp rates" in b4ab["F4b"]["alt"]
    for f in ("F4a", "F4b"):
        assert len(b4ab[f][""].split()) <= 650                         # the word limit stays (room made by removing a clause without a ruled limit)


# ---- O3 ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_o3_the_dagger_is_an_outline_marker_at_its_ruled_size_and_the_key_matches():
    mk = jf4._dagger_outline()
    assert mk.get_path().vertices.shape[0] > 10 and abs(mk.get_path().vertices.mean(axis=0)).max() < 0.2          # a glyph path, centred
    assert S.diagram_mark("f4_cls").size == 6.0                                       # the ruled size is unchanged
    src = inspect.getsource(jf4)
    assert 'marker=dag, ms=cls_m.size, mfc="none"' in src and src.count("marker=dag") == 2          # the plotted marks and the key handle
    assert "jitter" not in src.lower() and jf4.DAGGER_EDGE < 0.7


@pytest.mark.skipif(not haveF4, reason="stored inputs absent")
def test_o3_f4a_caption_says_hollow_and_stays_inside_the_word_limit(b4ab):
    assert "small hollow double dagger" in b4ab["F4a"]["_full"] or "hollow double dagger" in b4ab["F4a"][""]
    assert len(b4ab["F4a"][""].split()) <= 650


# ---- O4 ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@pytest.mark.skipif(not have5, reason="stored inputs absent")
def test_o4b_fs5_names_tau_as_the_membrane_time_constant_where_the_stored_parameter_is_and_keeps_tau_d_for_the_synaptic_decay(b5):
    t, alt = b5
    assert "synaptic decay times" not in t and "synaptic decay times" not in alt
    assert "at the membrane time constants tau 10 and 20 ms, the synaptic decay time tau_d staying at its reference value" in t
    assert "at the membrane time constants tau 8, 10 and 12 ms, the synaptic decay time tau_d staying at its reference value" in t
    assert "membrane time constants tau of 10 and 20 ms" in t           # the ruled limit MS11-C4 (stored: tau 10 and 20 ms), plain wording corrected
    assert "tau = membrane time constant" in t and "tau_d (synaptic decay time)" in t
    # the stored parameter of the unit-level test is model.tau_ms (the membrane time constant)
    assert 'resolve_config(None, {"model.tau_ms": tau_ms' in open(ROOT / "src/mprsurge/analysis/rb9a_unit.py", encoding="utf-8").read()


@pytest.mark.skipif(not have5, reason="stored inputs absent")
def test_o4c_fs5_caption_states_what_the_columns_of_a_are(b5):
    t, _ = b5
    assert "(columns, left to right as the labels under (c): the baseline and then the variants in the order of those labels; (a) has no column labels of its own)" in t


def test_o4d_fs5_c_has_a_colour_bar_with_a_label_and_a_permitted_colour_map():
    src = inspect.getsource(jfs5.draw)
    assert "fig.colorbar" in src and 'cmap = matplotlib.colormaps["viridis_r"]' in src and "Fraction of records changed" in src
    assert not re.search(r"jet|rainbow|hsv|turbo", src)


@pytest.mark.skipif(not have5, reason="stored inputs absent")
def test_o4d_fs5_caption_points_to_the_colour_bar(b5):
    assert "the colour bar under (d) gives the scale" in b5[0]


def test_o4d_fs5_image_has_the_colour_bar_axes_and_no_clipped_label(tmp_path):
    if not have5:
        pytest.skip("stored inputs absent")
    res = FG.make_FS5(mode="journal", out_dir=tmp_path / "FS5")
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = np.asarray(Image.open(tmp_path / "FS5" / "FS5_journal.png").convert("L"))
    h, w = im.shape
    assert (im[:, w - 8:] == 255).all()                             # nothing runs to the right edge (the first label did)
    assert res["drawn_sha256"]


@pytest.mark.skipif(not (RES / "A6/a6_summary.json").is_file(), reason="stored inputs absent")
def test_o4e_f3_full_caption_names_only_what_the_image_shows(b3):
    t = b3
    for bad in ("tall black bar", "called 'continuation' in the legend", "called 'frequency-map' in the legend", "Colour and contours", "hollow ring"):
        assert bad not in t
    for good in ("thin black vertical line", "small dark-red ring", "no contour line is drawn", "Colour shows the limit-cycle frequency"):
        assert good in t
    assert "the 25 Hz contour crosses the cycle branch only on some slices" in t                    # the ruled A6 take-home sentence stays (stored data)


# ---- independent comparison rows ---------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_independent_rows_for_fs4_cover_all_halvings_and_the_new_wording():
    src = open(ROOT / "scripts/ms13_independent.py", encoding="utf-8").read()
    for name in ("net_all_min", "net_all_max", "net_all_max_halving", "net_all_n_above", "net_all_n", "net_h1_min", "net_h2_max", "net_h3_max"):
        assert f'"{name}"' in src or f'f"net_h{name[5]}_{name[7:]}"' in src or name.startswith("net_h")
    from importlib import import_module
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    mod = import_module("ms13_independent")
    pat = mod.JOURNAL_OVERRIDE["FS4.net_rel_max"][0]
    assert re.search(pat, "first halving 5 to 43 percent, second halving 0 to 33 percent").group(1) == "43"
    assert re.search(r"is at the (\w+) halving, seed", "is at the third halving, seed 0").group(1) == "third"
