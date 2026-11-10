"""MS13 13x (DL-716 to DL-718): tests of X1 (FS1 caption wording on the test point, word limit 650) and X2 (FS1 (b) alt text from the stored map).
They read the stored results under results/ and skip if those are absent. Nothing is built into figures/. No data assertion of an earlier test changes."""
import re

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jaltaudit as AA
from mprsurge.plotting import jfs as JFS
from mprsurge.plotting import jshort as JS
from mprsurge.plotting import journal as J

ROOT = C.repo_root()
RES = ROOT / "results"
needs = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.FS1_INPUTS), reason="stored FS1 inputs under results/ are absent")


@pytest.fixture(scope="module")
def fs1():
    raw = FG.load_FS1(RES)
    d = FG.prepare_FS1(raw)
    rows = []
    for panel, key in (("a-c", "A1"), ("a-c", "A2"), ("d", "S1_K4"), ("e", "S1_K5")):
        rec = raw["records"][key]
        for r in FG.make_param_table(rec["config"]):
            rows.append({**r, "panel": panel, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    c = JFS.fs1_consts(d, rows, a2=raw["a2"])
    full = JFS.fs1_caption(d, rows, ids=[], c=c)
    cfg = J.load_config(ROOT)
    short = JFS.fs1_short(d, c, J.caption_limit(cfg, "FS1"), full)
    return {"raw": raw, "d": d, "c": c, "full": " ".join(full.split()), "short": " ".join(short.split()), "cfg": cfg}


def test_x1_the_fs1_limit_is_650_in_the_one_place_where_it_is_defined():
    cfg = J.load_config(ROOT)
    assert cfg["caption"]["short_max_words_FS1"] == 650 and J.caption_limit(cfg, "FS1") == 650
    assert cfg["caption"]["short_max_words"] == 600                           # the default and the other figures are not changed


@needs
def test_x1_test_point_numbers_equal_values_recomputed_from_the_arrays(fs1):
    a = np.load(RES / "A2" / "a2_ring_map.npz")
    i, j = int(np.argmin(abs(a["eta_over_Delta"] + 5))), int(np.argmin(abs(a["J_over_sqrtDelta"] - 15)))
    k = int(np.flatnonzero(a["ring_is_focus"][i, j])[0])
    lam, tau = complex(a["k4_lambda"]), float(a["tau_ms"]) / 1000
    want = {"f_c": a["ring_lambda_im"][i, j, k] / (2 * np.pi * tau), "cyc_c": a["ring_lambda_im"][i, j, k] / (2 * np.pi * abs(a["ring_lambda_re"][i, j, k])),
            "f_d": lam.imag / (2 * np.pi * tau), "cyc_d": lam.imag / (2 * np.pi * abs(lam.real)), "r_c": a["ring_r"][i, j, k], "r_d": a["k4_r_star"]}
    tp = fs1["c"]["tp"]
    for key, v in want.items():
        assert abs(tp[key] - float(v)) < 1e-9, key
    assert (f"{want['f_c']:.2f}", f"{want['cyc_c']:.2f}", f"{want['f_d']:.2f}", f"{want['cyc_d']:.2f}") == ("52.82", "1.71", "91.77", "3.96")
    for t in (fs1["short"], fs1["full"]):
        assert "the stable focus has 52.82 Hz and 1.71 cycles per e-fold" in t
        assert "(firing rate 1.3732, against 1.0306 at input 0)" in t and "has 91.77 Hz and 3.96 cycles per e-fold" in t
        assert "so the values of (c) at the test point do not describe this ringing" in t and "After the step to 3 the system settles on a different stable focus" in t
        assert "read with the input current at 0" in t


@needs
def test_x1_short_caption_fits_650_every_new_number_is_in_the_full_caption_and_terms_are_plain(fs1):
    short, full = fs1["short"], fs1["full"]
    assert JS.words(short) <= 650 and len(short.split()) <= 650
    assert JS.numbers_not_in_full(short, full) == []
    assert JS.undefined_terms(short) == []
    new = [short[short.index("At the circled test point"):short.index("(d) Recorded")], short[short.index("After the step to"):short.index("(e) Recorded")]]
    for t in new + [full[full.index("At the circled test point"):full.index("(d) The recorded")]]:
        assert not re.search(r"\b(stored|linearised|headline|companion|f_pk|K[0-9]|RB[0-9]|G[0-9]|D24|DL-)", t), t       # plain words, no codes (V3, K4)
    assert not re.search(r"\b(RB\d|DL-\d|G\d+\b|D24|[A-Z]\d_)", short)                                                  # no code in the short caption (K4)
    assert "No panel has a red title" in short and "No other failed check is about this figure" in short             # only drawn failed checks are named


@needs
def test_x1_ruled_claim_limits_and_failed_checks_paragraphs_are_unchanged(fs1):
    short, full = fs1["short"], fs1["full"]
    assert "Limits: M2 is the comparison model, so nothing in this figure is a result for model M3 (the mean-field model); the focus is damped by construction" in short
    assert "Panels (c) and (d) are drawn at different parameter values." in short and "Panels (c) and (d) are drawn at different parameter values." in full
    assert JS.limits_missing("FS1", short) == []
    assert "Failed checks. No row of the project's table of failed checks concerns this figure" in full or "No row of the project's table of failed checks concerns this figure" in full


@needs
def test_x2_alt_text_sentence_is_built_from_the_map_and_replaces_the_boundary_claim(fs1):
    alt = FG._fs1_alt_text(fs1["d"], fs1["c"]["tp"])["b"]
    assert "on the grey boundary" not in alt
    a = np.load(RES / "A2" / "a2_ring_map.npz")
    has = a["ring_is_focus"].any(axis=2)
    i, j = int(np.argmin(abs(a["eta_over_Delta"] + 5))), int(np.argmin(abs(a["J_over_sqrtDelta"] - 15)))
    assert has[i - 3:i + 4, j - 3:j + 4].all() and has[i, j]
    ii, jj = np.nonzero(~has)
    m = int(np.argmin((ii - i) ** 2 + (jj - j) ** 2))
    assert (i - ii[m], j - jj[m]) == (5, 7) and abs(((ii[m] - i) ** 2 + (jj[m] - j) ** 2) ** 0.5 - 8.6) < 0.05
    assert "lies on the coloured side, in the region where a stable focus exists" in alt
    assert "5 grid steps lower in eta_bar/Delta (0.25 units) and 7 lower in J/sqrt(Delta) (0.7 units)" in alt
    assert "reaches the grey edge" in alt and "stored" not in alt


@needs
def test_x2_the_sentence_stops_if_the_map_layout_changes(fs1):
    tp = dict(fs1["c"]["tp"], block7=False)
    with pytest.raises(FG.DataError):
        FG._fs1_alt_text(fs1["d"], tp)
    with pytest.raises(FG.DataError):
        FG._fs1_alt_text(fs1["d"], dict(fs1["c"]["tp"], near_di=3))


@needs
def test_x2_the_audit_check_recomputes_the_distance_from_the_source_data_once_the_build_holds_the_new_sentence():
    p = ROOT / "figures/journal/supplement/FS1_alt_text.txt"
    if not p.is_file() or "grid steps lower in eta_bar/Delta" not in p.read_text(encoding="utf-8"):
        pytest.skip("the recorded FS1 alt text still holds the pre-13x sentence (the 13x build is not recorded yet)")
    AA._cache.clear()
    rows = [r for r in AA.rows(ROOT) if r[0] == "FS1" and r[2].startswith("grid steps and units")]
    assert len(rows) == 1 and rows[0][5] and rows[0][3] == ("5", "0.25", "7", "0.7")
