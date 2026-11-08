"""MS13 13t-8 and 13t-8b (DL-666 to DL-672): tests of the F4 journal export (F4a and F4b, DL-667 K1 and K2), the code check K4 (DL-668, L1) and the four caption fixes K5. They read the recorded
results under results/ and skip if those are absent. Builds go to a temporary folder, never to figures/."""
import importlib.util
import sys

import matplotlib
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import collide as CO
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jcaption as JCAP
from mprsurge.plotting import jchecks as JCH
from mprsurge.plotting import jf4 as JF4
from mprsurge.plotting import journal as J
from mprsurge.plotting import jshort as JSH
from mprsurge.plotting import plain as PL

ROOT = C.repo_root()
RES = ROOT / "results"
SRC = ROOT / "src" / "mprsurge" / "plotting"
needs = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F4_INPUTS), reason="stored inputs under results/ are absent")


def _script(name):
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("f4")
    res = FG.make_F4(mode="journal", out_dir=out)
    return {"out": out, "res": res}


def test_registrations_of_f4a_and_f4b():
    for f in ("F4a", "F4b"):
        assert f in JCAP.TITLE_MAP and f in JSH.SHORT_NAMED and f in JSH.SHORT_LIMIT_IDS
        assert J.caption_limit(J.load_config(ROOT), f) == 650                                      # K1 (UNVERIFIED limit, as the other main figures)
    v = _script("ms13_verify_export")
    assert "F4a" in v.PILOT and "F4b" in v.PILOT and v.DRAFT_ID["F4a"] == "F4" == v.DRAFT_ID["F4b"] and "F4a" in v.STRICT_ALLOW and "F4b" in v.STRICT_ALLOW
    assert "F4a" in _script("fig_journal").PILOT and "F4b" in _script("fig_journal").PILOT
    assert "F4a" in _script("ms13_pilot_sheet").IDS and "F4b" in _script("ms13_pilot_sheet").IDS
    assert "F4a" in _script("ms13_independent_compare").JOURNAL_FILES and "F4b" in _script("ms13_independent").JOURNAL_FIGURES


def test_l3_the_five_plain_limits_have_the_ruled_numbers_and_no_code():
    from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS
    for i in ("G6-D1", "G6-D2", "G6-D3", "DL-163-D3", "MS11-C6"):
        assert i in PL.PLAIN_LIMITS and not PL.FORBIDDEN.search(PL.PLAIN_LIMITS[i]) and not JSH.code_hits(PL.PLAIN_LIMITS[i]), i
    assert "0 of 6" in PL.PLAIN_LIMITS["G6-D1"] and "58.698" in PL.PLAIN_LIMITS["G6-D2"] and "58.879" in PL.PLAIN_LIMITS["G6-D2"]
    assert "0 to 2 of the 13" in PL.PLAIN_LIMITS["DL-163-D3"] and "10 s and 316 s" in PL.PLAIN_LIMITS["MS11-C6"]
    assert CLAIM_LIMIT_LABELS["G6-D1"][0].startswith("no claim that onset follows")


@needs
def test_f4_split_is_the_whole_draft_data_and_the_two_parts_overlap_only_in_the_shared_entries():
    d = FG.prepare_F4(FG.load_F4())
    a, b = set(JF4.journal_keys("F4a", d)), set(JF4.journal_keys("F4b", d))
    assert a | b == set(d)
    assert all(JF4.part_of(k) == JF4.F4_PARTS for k in a & b)
    assert any(k.startswith("noise_") for k in b) and not any(k.startswith("noise_") for k in a)


@needs
def test_f4_builds_and_the_drawn_data_digest_equals_the_draft_digest(built):
    draft = ROOT / "figures" / "F4" / "F4_drawn_data_sha256.txt"
    for f in ("F4a", "F4b"):
        dig = (built["out"] / f / f"{f}_journal_drawn_data_sha256.txt").read_text(encoding="utf-8").strip()
        assert len(dig) == 64
        if draft.is_file():
            assert dig == draft.read_text(encoding="utf-8").strip()


@needs
@pytest.mark.parametrize("fid", ["F4a", "F4b"])
def test_f4_short_caption_limits_definitions_and_no_code(built, fid):
    short = (built["out"] / fid / f"{fid}_journal_caption.txt").read_text(encoding="utf-8").strip()
    full = (built["out"] / fid / f"{fid}_journal_caption_full.txt").read_text(encoding="utf-8")
    assert JSH.words(short) <= 650
    assert JSH.code_hits(short) == [] and not JSH.ID_PATTERN.search(short)                          # K4, L1: a short caption holds no code
    assert JSH.undefined_terms(short) == []
    assert JSH.numbers_not_in_full(short, full) == []
    assert not JCAP.FORBIDDEN.search(full)


@needs
@pytest.mark.parametrize("fid", ["F4a", "F4b"])
def test_f4_captions_say_that_the_ring_numbers_are_not_drawn(built, fid):
    full = (built["out"] / fid / f"{fid}_journal_caption_full.txt").read_text(encoding="utf-8")
    assert "the numbers are in a row" not in full and "height 0.23" not in full
    if fid == "F4a":
        assert "is not drawn on the ring and is in the source data" in full and "not drawn on the image and are in the source data" in full


@needs
@pytest.mark.parametrize("fid", ["F4a", "F4b"])
def test_f4_collisions_are_all_allowed_by_reason_and_none_is_a_legibility_reason(fid):
    v = _script("ms13_verify_export")
    with FG.journal_figure(fid) as (fig, d, cfg):
        bad, ok = CO.check(fig, pad_pt=cfg["collision"]["pad_pt"], allow=CO.JOURNAL_ALLOW.get(fid, ()))
        assert bad == []                                                                           # no unlisted hit, and no marker-frame hit (L2: fixed by padding, not listed)
        assert all(h.kind != "marker-frame" for h, _ in ok)
        assert {v.reason_class(r) for _, r in ok} <= {"stored coincident positions and ruled mark sizes", "stored coincident positions"}
        assert all(e.reason for e in CO.JOURNAL_ALLOW[fid])


@needs
def test_f4_red_titles_and_no_colour_only_pair():
    for fid, n_red in (("F4a", 2), ("F4b", 1)):
        with FG.journal_figure(fid) as (fig, d, cfg):
            reds = JCH.red_titles(fig)
            assert len(reds) == n_red
            plain = [x[1] for x in JCAP.TITLE_MAP[fid]]
            assert all(any(p in s for p in plain) for _, s in reds)
            assert JCH.non_colour_violations(fig) == []                                            # the prediction lines and the hysteresis width differ in more than colour


def test_k4_code_check_finds_codes_and_not_symbols():
    assert JSH.code_hits("the RB3(a) check, gate G7, rule D24, K10 and headline_class_kept_1.0_sigma") == ["D24", "G7", "K10", "RB3(a)", "headline_class_kept_1.0_sigma"]
    assert JSH.code_hits("eta_bar, T_ramp, tau_d, f_pk and A_ref are symbols; 25 Hz; Delta = 0.3") == []


def test_k4_uncode_gives_plain_wording_and_stops_on_a_code_that_remains():
    t = ("All earlier failures and limits stand: the failure of check RB1 (network against mean field), gate G7 not passed, the failure of the D24 rule, "
         "the six limits set when gate G4 (network against mean field) was triggered.")
    u = JCAP.uncode(t, "FS3")
    assert JSH.code_hits(u) == [] and "the failure of the network-against-mean-field check" in u and "the negative-control gate not passed" in u and "the 90 percent rule" in u
    with pytest.raises(JCAP.JCaptionError):
        JCAP.uncode("the check G9 failed", "FS3")
    md = JCAP.mapping_markdown("FS3")
    assert "RB1" in md and "D24" in md and "G7" in md and "Plain wording of the caption and the code behind it" in md                # the codes stay in the supplement table


def test_k4_the_verifier_has_the_caption_code_check_and_the_scope_of_l1():
    t = (ROOT / "scripts" / "ms13_verify_export.py").read_text(encoding="utf-8")
    assert '"caption codes"' in t and "scope_text = cap if fid in FS_SINGLE else short" in t and "full-caption codes (L1: information only)" in t


def test_k5_1_fs3_says_which_bars_carry_the_check():
    t = (SRC / "jfs3.py").read_text(encoding="utf-8")
    assert "show the check on the 120 s bars at the noise factors 0.5 and 1 only (the 120 s bar at the noise factor 2 has neither)" in t


def test_k5_2_f3_short_says_which_paths_coincide():
    t = (SRC / "jshort.py").read_text(encoding="utf-8")
    assert "P1, P2, P3 and P5 coincide in (c) and (d) because they differ in J, drive or time course, which these planes do not show; P4a and P4b are drawn apart." in t
    assert "The paths coincide in (c) and (d)" not in t


@pytest.mark.skipif(not all((RES / p).is_file() for p in FG.FS1_INPUTS), reason="stored inputs under results/ are absent")
def test_k5_3_fs1_take_home_and_panel_d_say_the_same_with_the_stored_values():
    d = FG.prepare_FS1(FG.load_FS1())
    assert f"{d['k4_rel_err_frequency']:.7f}" == "0.0002128" and f"{d['k4_rel_err_decay']:.7f}" == "0.0060869"      # printed 2.1e-4 and 6.1e-3
    t = (SRC / "jfs.py").read_text(encoding="utf-8")
    assert t.count("differ from the linearised ones by {_e(d['k4_rel_err_frequency'])} and {_e(d['k4_rel_err_decay'])} relative") == 2          # the take-home and the (d) sentence
    assert "rings at the linearised" not in t


def test_k5_4_fs2_says_what_is_drawn_at_3_and_50_ms():
    t = (SRC / "jfs2.py").read_text(encoding="utf-8")
    assert "the difference of the mean of r is drawn there" in t and "so their differences are undefined and not drawn;" not in t
