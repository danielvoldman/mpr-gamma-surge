"""MS13 13t-1e (DL-581 to DL-583): tests of the fix round on the F1, F3, F5 and F5c journal pilot: U1 (red titles carry evidence), U2 (plain image text), U3 (two captions per figure), U4 (the 100 stored
points of the F3 (d) curve), U5 (words defined once, Key entries only for terms the caption uses), U6 (true minus signs, the F1 y-limit sentence, the F5c per-N counts, the scope of two limit statements).
They read the stored results under results/ and skip if those are absent. Builds go to a temporary directory, never to figures/. No data assertion of an earlier test changes."""
import re
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jcaption as JC
from mprsurge.plotting import jchecks as JK
from mprsurge.plotting import journal as J
from mprsurge.plotting import jshort as JS
from mprsurge.plotting import plain as PL

ROOT = C.repo_root()
RES = ROOT / "results"
PILOT = ("F1", "F3", "F5", "F5c")
INPUTS = {"F1": FG.F1_INPUTS, "F3": FG.F3_INPUTS, "F5": FG.F5_INPUTS, "F5c": FG.F5_INPUTS}
needs = pytest.mark.skipif(not all((RES / p).is_file() for f in PILOT for p in INPUTS[f]), reason="stored F1, F3 and F5 inputs under results/ are absent")
CLAIM = {"F1": (FG.F1_CLAIM_LIMITS, None), "F3": (FG.F3_CLAIM_LIMITS, None), "F5": (FG.F5_CLAIM_LIMITS, FG.F5_NOT_APPLICABLE), "F5c": (FG.F5_CLAIM_LIMITS, FG.F5_NOT_APPLICABLE)}


@pytest.fixture(scope="module")
def cfg():
    return J.load_config(ROOT)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("journal13t1e")
    out = {f: getattr(FG, f"make_{f}")(mode="journal", out_dir=base / "journal" / f) for f in ("F1", "F3", "F5")}
    out["F5c"] = out["F5"]["F5c"]
    return {"base": base / "journal", "out": out}


def _short(built, f):
    return (built["base"] / f / f"{f}_journal_caption.txt").read_text(encoding="utf-8").strip()


def _full(built, f):
    return (built["base"] / f / f"{f}_journal_caption_full.txt").read_text(encoding="utf-8").strip()


def _supp(built, f):
    return (built["base"] / "supplement" / f"{f}_supplement.md").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def figs():
    res = {}
    for f in PILOT:
        c = FG.journal_figure(f, close=False)
        res[f] = c.__enter__()
        c.__exit__(None, None, None)
    yield res
    plt.close("all")


# ---- U2: plain image text ----

def test_u2_id_pattern_matches_check_and_step_ids_and_not_class_or_path_names():
    for s in ("RB1", "RB2", "RB6", "RB9(b)", "G4", "G7", "D24", "A4", "A6", "S8", "S9", "MS11", "(a) RB9(b) FAIL", "the D24 rule"):
        assert JS.ID_PATTERN.search(s), s
    for s in ("S+", "S-rel", "S-abs", "S-sus", "NS", "D-tr", "D-sus", "D-none", "P1", "P2", "P3", "P4a", "P4b", "P5", "M3", "ING", "eta_bar", "T_ramp 120 s", "J0", "tau_d (ms)", "N = 1e4", "f_pk",
              "network class S-sus, mean field D-tr"):
        assert not JS.ID_PATTERN.search(s), s


@needs
def test_u2_no_check_id_or_step_id_on_any_journal_image(figs):
    for f in PILOT:
        fig = figs[f][0]
        assert JK.image_id_violations(fig) == [], f


@needs
def test_u2_plain_titles_are_the_ruled_words(figs):
    texts = {f: " ".join(" ".join(t.get_text().split()) for t in figs[f][0].findobj(matplotlib.text.Text) if t.get_text()) for f in PILOT}
    assert "frequency check: FAIL" in texts["F3"] and "network vs mean field: FAIL" in texts["F1"] + " " + "network vs mean field: FAIL"   # F1 holds the words in the titles of (d) and (f)
    assert "network vs mean field" in texts["F1"] and "network vs mean field, cells: FAIL" in texts["F5"] and "network vs mean field FAIL" in texts["F5"]
    assert "90 percent agreement rule: FAILED" in texts["F5"] and "step-halving check: FAIL" in texts["F5c"]
    assert "continuation" in texts["F3"] and "frequency-map" in texts["F3"]
    for f, words in (("F3", ("A4", "A6")), ("F5", ("RB1", "D24")), ("F5c", ("RB6",)), ("F1", ("RB1",))):
        assert not any(re.search(rf"(?<![A-Za-z0-9_]){w}(?![A-Za-z0-9_])", texts[f]) for w in words), (f, words)


def test_u2_title_map_names_every_plain_title_and_its_check():
    assert set(JC.TITLE_MAP) == {"F1", "F3", "F5", "F5c"}
    assert [x[2] for x in JC.TITLE_MAP["F5"]] == ["RB1", "RB1", "D24"] and JC.TITLE_MAP["F3"][0][2] == "RB9(b)" and JC.TITLE_MAP["F5c"][0][2] == "RB6" and JC.TITLE_MAP["F1"][0][2] == "RB1"
    md = JC.mapping_markdown("F3")
    assert "frequency check: FAIL" in md and "RB9(b)" in md and "continuation | legend | A4" in md and "frequency-map | legend | A6" in md


@needs
def test_u2_each_plain_title_is_mapped_in_the_full_caption_and_the_supplement(built):
    for f in PILOT:
        full, sup = _full(built, f), _supp(built, f)
        for panels, plain, cid, what in JC.TITLE_MAP[f]:
            assert f"The check {cid} ({what}) is shown in the title of {panels} as '{plain}'." in full, (f, plain)
            assert f"| {plain} | {panels} | {cid} |" in sup, (f, plain)


# ---- U1: red titles carry evidence ----

@needs
def test_u1_every_red_title_is_a_mapped_plain_title_and_the_panels_are_the_mapped_ones(figs):
    for f in PILOT:
        reds = JK.red_titles(figs[f][0])
        plain = [x[1] for x in JC.TITLE_MAP[f]]
        assert reds and all(any(p in s for p in plain) for _, s in reds), (f, reds)
    assert [l for l, _ in JK.red_titles(figs["F1"][0])] == ["d", "f"] and [l for l, _ in JK.red_titles(figs["F3"][0])] == ["a", "b", "c"]
    assert [l for l, _ in JK.red_titles(figs["F5"][0])] == ["a", "b", "c"] and [l for l, _ in JK.red_titles(figs["F5c"][0])] == ["b"]


@needs
def test_u1_f3_marks_the_two_frequencies_on_the_one_shared_colour_bar(figs):
    fig, d, cfg = figs["F3"]
    spec, cyc, diff = FG.F3_RB9B
    assert (spec, cyc, diff) == (49.0, 44.609, 4.391)
    marks = fig.findobj(lambda a: a.get_gid() == "frequency mark")
    assert len(marks) == 2 and sorted(round(float(a.xy[0]), 3) for a in marks) == [44.609, 49.0]
    labels = sorted(a.get_text() for a in fig.findobj(lambda a: a.get_gid() == "frequency mark label"))
    assert labels == ["cycle frequency, main example", "spectral peak, main example"]            # DL-592 V3
    (dt,) = fig.findobj(lambda a: a.get_gid() == "frequency mark difference")
    assert dt.get_text() == "differ by 4.391 Hz; allowed 0.5 Hz"
    bars = [ax for ax in fig.axes if ax.get_gid() == "colour bar frequency"]
    assert len(bars) == 1                                                 # ONE shared bar for (a) to (c)
    assert 4.391 == pytest.approx(spec - cyc)


def test_u1_f3_values_are_the_values_of_the_project_log_dl_388():
    log = (ROOT / "docs" / "decision_log.md").read_text(encoding="utf-8")
    m = re.search(r"## DL-388 .*?RB9\(b\) headline FAIL: ([\d.]+) Hz spectral against ([\d.]+) Hz cycle, difference ([\d.]+) Hz against 1/W = ([\d.]+) Hz", log, re.S)
    assert m is not None
    assert (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))) == (*FG.F3_RB9B, 0.5)


@needs
def test_u1_f5c_b_has_the_plain_line_and_no_other_f5c_panel_has_a_red_title(figs):
    fig = figs["F5c"][0]
    lines = [a.get_text() for a in fig.findobj(lambda a: a.get_gid() == "step-halving line")]
    assert len(lines) == 1 and " ".join(lines[0].split()) == "step-halving test not drawn: its runs are not recorded" == FG.F5CJ_B_LINE            # DL-592 V3
    assert len(JK.red_titles(fig)) == 1


# ---- U3: two captions per figure ----

@needs
def test_u3_two_caption_files_full_in_supplement_and_manifest(built, cfg):
    for f in PILOT:
        full, short = _full(built, f), _short(built, f)
        assert short != full and len(full) > len(short)
        norm = lambda s: " ".join(s.split())
        assert norm(full) in norm(_supp(built, f))
        prov = (built["base"] / f / f"{f}_journal_provenance.json").read_text(encoding="utf-8")
        assert f"{f}_journal_caption_full.txt" in prov and f"{f}_journal_caption.txt" in prov
    J.write_export_manifest(built["base"])
    man = (built["base"] / "export_manifest.csv").read_text(encoding="utf-8")
    assert all(f"{f}/{f}_journal_caption_full.txt" in man and f"{f}/{f}_journal_caption.txt" in man for f in PILOT)


def test_u3_config_limits_are_set_and_unverified(cfg):
    assert cfg["caption"]["short_max_words"] == 330 and cfg["caption"]["short_max_words_F1"] == 480            # DL-593 V8 (were 220 and 280)
    assert J.caption_limit(cfg, "F1") == 480 and J.caption_limit(cfg, "F3") == 480 and J.caption_limit(cfg, "F5c") == 480
    assert "UNVERIFIED" in (ROOT / "configs" / "journal_export.yaml").read_text(encoding="utf-8")


@needs
def test_u3_short_caption_word_limit_plain_language_and_order(built, cfg):
    for f in PILOT:
        s = _short(built, f)
        assert JS.words(s) <= J.caption_limit(cfg, f), (f, JS.words(s))
        assert s.startswith(f"{f}. ") and "\n" not in s
        assert not JS.ID_PATTERN.search(s) and not JC.FORBIDDEN.search(s), f
        assert not re.search(r"\bstored\b|\bDL\b|\bplan\b|\bgate\b|\bG\d", s), f
        first = s[len(f) + 2:].split(". ")[0]
        for m in {"F1": ("does not reproduce it",), "F3": ("frequency check",), "F5": ("holds for the noise-free mean field only",),
                  "F5c": ("step-halving check", "do not reproduce the mean field")}[f]:            # DL-593 V6
            assert m in first, (f, m)
        assert s.endswith(JS.POINTER.format(fid=f)) and "(listed in the supplement)" in s, f            # DL-593 V7
        assert "red title" in s.lower() and "Limits:" in s
        assert s.index("Limits:") < s.index("All earlier failures") and s.index(" (a)") < s.index("Failed check") < s.index("Limits:") if "Failed check" in s else True


@needs
def test_u3_short_caption_names_every_failed_check_of_the_figure(built):
    # DL-593 V7: the short caption names only the failed checks whose result is drawn (JS.SHORT_NAMED); the full caption lists every one (checked in tests/test_ms13_13t1f.py)
    tokens = {("RB1", "headline_10s"): "network against mean field", ("RB1", "headline_120s"): "network against mean field", ("RB1", "cells_30s"): "network against mean field",
              ("RB6", "network_fpk_halving_dt"): "step-halving check", ("RB9", "b_spectral_vs_cycle_headline"): "frequency check", ("RB2", "noisy_subgrid_agreement"): "90 percent rule"}
    for f in ("F1", "F5", "F3", "F5c"):
        s = _short(built, f)
        for k in JS.SHORT_NAMED[f]:
            assert tokens[k] in s, (f, k)


@needs
def test_u3_every_ruled_claim_limit_is_in_the_full_caption_and_the_short_limits_have_the_same_numbers(built):
    norm = lambda s: " ".join(s.split())
    for f in PILOT:
        ids, na = CLAIM[f]
        full = norm(_full(built, f))
        for i in ids:
            assert norm(JC.plain_n(PL.plain_limit_text((i,), na))) in full, (f, i)            # DL-592 V4: 10,000 for 1e4
        short = _short(built, f)
        nums_full = set(re.findall(r"\d+(?:\.\d+)?(?:e\d+)?", full))
        assert JS.limits_missing(f, short) == [], f            # DL-593 V6, V8: the clause of each short limit (a distinctive phrase), its numbers are in the full caption
        sent = short[short.index("Limits: "):short.index("All earlier failures")]
        assert JS.numbers_of(sent) <= JS.numbers_of(full), f


def test_u3_a_short_limit_with_a_number_that_the_ruled_wording_does_not_have_stops_the_build(monkeypatch):
    monkeypatch.setitem(JS.SHORT_LIMITS, "G4-C3", "no-ramp network controls are classified into surge classes (in 9 of 10 seeds)")
    with pytest.raises(JS.JShortError):
        JS.limit_clauses("F1")


def test_u3_finish_stops_on_too_many_words_an_id_or_the_word_stored():
    with pytest.raises(JS.JShortError):
        JS.finish("F1", ["word " * 30], 20)
    with pytest.raises(JS.JShortError):
        JS.finish("F1", ["the RB1 check failed"], 50)
    with pytest.raises(JS.JShortError):
        JS.finish("F1", ["a stored value"], 50)
    assert JS.finish("F1", ["a recorded value."], 50).startswith("F1. a recorded value.")            # DL-596: 'recorded' is an ordinary word of the short captions, no definition sentence


# ---- U4: the 100 stored points of the (d) curve ----

@needs
def test_u4_f3_full_and_short_caption_state_100_and_30_points(built):
    full, short = _full(built, "F3"), _short(built, "F3")
    assert "drawn as straight segments between its 30 stored points" in full
    assert "(drawn as straight segments between its 100 stored points, next to the 30 stored points of the curve in (c))" in full
    assert "straight segments between recorded points" in short and "30 points" not in short and "100 points" not in short            # DL-593 V6


@needs
def test_u4_counts_are_read_from_the_stored_arrays_and_a_different_count_stops_the_build():
    d = FG.prepare_F3(FG.load_F3())
    assert (len(d["a4_tau_d_ms"]), len(d["a4_Delta"])) == (30, 100) == FG.F3_A4_POINTS
    c = FG._f3_jconst(d)
    assert (c["a4_points"], c["a4_points_d"]) == (30, 100)
    d2 = dict(d)
    d2["a4_Delta"] = d["a4_Delta"][:99]
    d2["a4_Delta_eta_H"] = d["a4_Delta_eta_H"][:99]
    with pytest.raises(FG.DataError):
        FG._f3_jconst(d2)


# ---- U5: words defined once; Key entries only for terms the caption uses ----

@needs
def test_u5_key_defines_stored_headline_and_sigma_once_and_only_where_used(built):
    for f in PILOT:
        full = _full(built, f)
        key = next(p for p in full.split("\n\n") if p.startswith("Key and abbreviations. "))
        rest = "\n\n".join(p for p in full.split("\n\n") if p is not key)
        assert JC.key_unused_terms(full) == [], f
        for pat, defin in JC.WORD_ENTRIES:
            used = re.search(pat, rest) is not None
            defin = JC.plain_n(defin)            # DL-592 V4
            assert (defin in key) == used, (f, pat)
            assert full.count(defin) <= 1
    assert "Stored (in plain words: recorded) = read from the saved result files of the analysis, not recalculated" in _full(built, "F3")
    assert "Headline = the main example run" in _full(built, "F1") and "Sigma = the amplitude of the additive white noise on v" in _full(built, "F5")


def test_u5_a_key_entry_whose_term_is_not_used_is_found():
    text = "\n\n".join(["F1. take.", "Panels. panel.", "Key and abbreviations. Symbols: J = signed coupling (negative: inhibitory). " + JC.WORD_ENTRIES[1][1], "Parameters. none."])
    assert set(JC.key_unused_terms(text)) == {"J", r"\bheadline\b"}


@needs
def test_u5_short_caption_never_says_stored_and_defines_recorded_if_it_uses_it(built):
    for f in PILOT:
        s = _short(built, f)
        assert not re.search(r"\bstored\b", s)
    assert "Recorded results are read from the saved result files of the analysis, not recalculated." == JS.RECORDED_DEF


def test_u5_sigma_meaning_is_the_plans_wording():
    plan = (ROOT / "docs" / "plan.md").read_text(encoding="utf-8")
    assert "Additive white noise on v" in plan and "phenomenological" in plan and "baseline std of v matches one N = 10" in plan
    d = dict(JC.WORD_ENTRIES)[r"\bsigma\b"]
    assert "additive white noise on v" in d and "phenomenological" in d and "baseline standard deviation of v" in d


# ---- U6 (a): true minus signs ----

def test_u6a_true_minus_replaces_a_typed_hyphen_in_fixed_and_function_formatters_and_changes_no_position():
    from matplotlib.ticker import FuncFormatter
    fig, (a, b) = plt.subplots(1, 2)
    a.set_yticks([0, 1, 2], ["-40", "-5", "0"])
    b.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{-x:g}"))
    b.set_yticks([1, 2])
    before = (list(a.get_yticks()), list(b.get_yticks()))
    assert JK.tick_hyphens(fig)
    J.true_minus(fig)
    assert JK.tick_hyphens(fig) == []
    assert [t.get_text() for t in a.yaxis.get_ticklabels()] == ["−40", "−5", "0"]
    assert [t.get_text() for t in b.yaxis.get_ticklabels()] == ["−1", "−2"]
    assert (list(a.get_yticks()), list(b.get_yticks())) == before
    plt.close(fig)


@needs
def test_u6a_no_hyphen_minus_on_any_journal_tick_label_and_the_drawn_data_digests_are_equal(figs, built):
    for f in PILOT:
        assert JK.tick_hyphens(figs[f][0]) == [], f
    drafts = {f: (ROOT / "figures" / f / f"{f}_drawn_data_sha256.txt") for f in ("F1", "F3", "F5")}
    if all(p.is_file() for p in drafts.values()):
        for f in ("F1", "F3", "F5"):
            assert built["out"][f]["drawn_sha256"] == drafts[f].read_text(encoding="utf-8").strip(), f
        assert built["out"]["F5c"]["drawn_sha256"] == drafts["F5"].read_text(encoding="utf-8").strip()


# ---- U6 (b), (c), (d): F1 y limit sentence, F5c per-N counts, scope of two limit sentences ----

@needs
def test_u6b_f1_y_limit_sentence_has_no_purpose_clause(built):
    full = _full(built, "F1")
    assert "the y limit is padded by 30 rows on each side (display only, no spike is moved)" in full
    assert "do not fuse with the frame" not in full and "first and last row" not in full


@needs
def test_u6c_f5c_per_n_counts_come_from_the_figure_arrays_and_the_take_home_follows_them(built):
    d = FG.prepare_F5(FG.load_F5())
    per = FG._f5_per_n(d)
    surge = ("S+", "S-rel", "S-abs")
    for k, p in enumerate(per):
        assert p["ramp_surge"] == sum(str(x) in surge for x in d["s9_class"][k]) and p["ctrl_surge"] == sum(str(x) in surge for x in d["ctrl_class"][k])
        assert (p["ramp_n"], p["ctrl_n"]) == (10, 3)
    assert [p["ctrl_surge"] for p in per][0] == 0 and per[0]["ctrl_classes"] == ["NS"] and set(per[0]["ramp_classes"]) <= {"S-abs", "S-sus"}
    cn = JC.f5c_counts(per)
    full, short = _full(built, "F5c"), _short(built, "F5c")
    assert JC.plain_n(f"the ramp seeds {cn['ramp_text']}; the no-ramp controls {cn['ctrl_text']}; the no-ramp controls in S-sus (not a surge class): {cn['sus_text']}.") in full            # DL-592 V4, DL-596
    assert "do not reproduce the mean field or separate ramp from no-ramp records" not in full and "do not separate ramp from no-ramp records" not in full
    assert "at N = 1000 the 3 controls are NS and the ramp seeds are S-abs or S-sus" in full            # DL-592 V4; the short caption has the control counts of (a) (tests/test_ms13_13t1f.py)
    assert JC.plain_n(f"the controls reach surge classes at N = {JC._and_list(cn['with_surge'])} ({cn['surge_text']})") in full or "Controls in a surge class" in short
    assert "No-ramp network controls are classified into surge classes." in full            # the ruled limit stays unchanged
    assert "(S+ in 6 seeds at N = 3000, NS in 1 at N = 10,000)" in full            # DL-592 V4


def test_u6c_counts_helper_on_synthetic_data():
    per = [{"label": "1e3", "ramp_n": 10, "ctrl_n": 3, "ramp_surge": 4, "ctrl_surge": 0, "ctrl_sus": 0, "ramp_classes": ["S-abs", "S-sus"], "ctrl_classes": ["NS"]},
           {"label": "3e3", "ramp_n": 10, "ctrl_n": 3, "ramp_surge": 7, "ctrl_surge": 2, "ctrl_sus": 0, "ramp_classes": ["S+", "S-sus"], "ctrl_classes": ["S+", "NS"]}]
    cn = JC.f5c_counts(per)
    assert cn["ctrl_text"] == "0 and 2 of 3 at N = 1e3 and 3e3" and cn["with_surge"] == ["3e3"] and cn["surge_text"] == "2 of 3"
    assert cn["zero"] == "at N = 1e3 the 3 controls are NS and the ramp seeds are S-abs or S-sus"


@needs
def test_u6d_scope_of_the_10_of_10_and_7_of_10_statements_is_in_the_full_captions(built):
    for f in ("F1", "F5", "F5c"):
        assert JC.plain_n(JC.LIMIT_SCOPE["MS9(e)-1"]) in _full(built, f), f            # DL-592 V4
    assert JC.plain_n(JC.LIMIT_SCOPE["MS11-C1"]) in _full(built, "F5") and JC.plain_n(JC.LIMIT_SCOPE["MS11-C1"]) not in _full(built, "F3")
    assert "negative-control step at N = 1e4 with 10 seeds each" in JC.LIMIT_SCOPE["MS9(e)-1"] and "noisy mean-field runs with constant parameters" in JC.LIMIT_SCOPE["MS11-C1"]
    # the ruled sentences themselves are unchanged
    assert PL.PLAIN_LIMITS["MS9(e)-1"].endswith("the network control without a ramp was flagged in 10 of 10 seeds, and the ramp runs in 10 of 10.")
    assert "the controls without a ramp reach 7 of 10" in PL.PLAIN_LIMITS["MS11-C1"]


def test_u6d_the_sources_named_in_the_scope_exist_in_the_log():
    log = (ROOT / "docs" / "decision_log.md").read_text(encoding="utf-8")
    assert "the constant-parameter control is flagged 10 of 10 seeds, the ramp runs 10 of 10 (DL-227)" in log
    assert "MS11-C1: the headline surge class is kept in 7 of 10 seeds at sigma (required 8 of 10), and the constant-parameter controls reach the same class in 7 of 10 at each sigma" in log


# ---- U3 (d): the independent comparison covers the short and the full captions ----

@needs
def test_u3d_independent_comparison_short_rows_and_full_rows_are_equal(built):
    sys.path.insert(0, str(ROOT / "scripts"))
    import ms13_independent as IND
    import ms13_independent_compare as CMP
    rows = IND.compute(figures=("F1", "F3", "F5"))
    shorts, fulls = CMP.short_captions(built["base"]), CMP.journal_captions(built["base"])
    nshort = nfull = 0
    for r in rows:
        s, _, sf = CMP.compare_short(r, shorts)
        j, _, jf = CMP.compare_journal(r, fulls)
        assert s in ("yes", "n.a.") and j in ("yes", "n.a."), (r["id"], s, j)
        nshort += s == "yes"
        nfull += j == "yes"
    assert nshort >= 20 and nfull >= 60            # DL-597: the short rows of the RB2 count, the RB6 solver difference and the F3 point counts left the short captions (V6, V7); rows for the F3 slice counts and the F5c control counts were added
    assert all(any(r["sprinted"] and f in r["stargets"] for r in rows) for f in PILOT)
