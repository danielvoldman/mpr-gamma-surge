"""MS13 13t-9 (DL-679 to DL-683): tests of N1 (the F4b ramp-rate range is read from the stored table), N2 (the audit of the numbers typed into the caption builders), N3 (review findings of the
13t-8 review) and N6 (the journal reference hashes). They read the recorded results under results/ and skip if those are absent. Builds go to a temporary folder, never to figures/."""
import csv
import hashlib
import importlib.util
import re
import sys

import matplotlib
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jcaption as JCAP
from mprsurge.plotting import jf4cap as C4
from mprsurge.plotting import jnumaudit as AUD
from mprsurge.plotting import jshort as JSH

ROOT = C.repo_root()
RES = ROOT / "results"
needs = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F4_INPUTS), reason="stored inputs under results/ are absent")


def _script(name):
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("f4_13t9")
    res = FG.make_F4(mode="journal", out_dir=out)
    return {"out": out, "res": res, "sup": out / "supplement"}


def _read(built, fid, name):
    return (built["out"] / fid / f"{fid}_journal_{name}.txt").read_text(encoding="utf-8")


# ---- N1 -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@needs
def test_n1_f4b_m2_ramp_rate_range_is_the_stored_a3_range(built):
    full = _read(built, "F4b", "caption_full")
    assert "13 values from 4.607e-5 to 0.04607" in full                  # the stored A3 ramp table: 4.607393e-05 to 0.0460739 (13 runs)
    assert "3.5e-5 to 0.035" not in full                                 # the P1 linear range that the 13t-8 caption printed by mistake
    short = _read(built, "F4b", "caption")
    assert "3.5e-5" not in short and "0.035" not in short


@needs
def test_n1_range_is_read_from_the_data_not_from_a_constant():
    raw = FG.load_F4()
    d = FG.prepare_F4(raw)
    f = C4.f4_facts(d)
    assert f["m2_eps_lo"] == float(format(float(min(d["a3_eps"])), ".4g")) == 4.607e-05
    assert f["m2_eps_hi"] == float(format(float(max(d["a3_eps"])), ".4g")) == 0.04607
    assert f["m2_eps_lo"] != f["eps_lo"] and f["m2_eps_hi"] != f["eps_hi"]       # the M2 range differs from the P1 linear range 3.5e-5 to 0.035


@needs
def test_n1_a_stored_table_that_does_not_give_the_range_stops_the_build():
    d = dict(FG.prepare_F4(FG.load_F4()))
    d["a3_eps"] = d["a3_eps"] * 0.5
    with pytest.raises(JCAP.JCaptionError, match="4.607e-05 to 0.04607"):
        C4.f4_facts(d)


# ---- N2 -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def audit_rows():
    return AUD.audit(ROOT)


@needs
def test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value(audit_rows):
    unclassified = [(r["file"], r["line"], r["token"], r["context"]) for r in audit_rows if r["kind"] == "?"]
    assert unclassified == []                                            # a new typed number without a stored source or a ruled-wording entry fails here
    wrong = [(r["file"], r["line"], r["token"], r["stored"], r["context"]) for r in audit_rows if r["kind"] == "S" and not r["equal"]]
    assert wrong == []
    assert sum(1 for r in audit_rows if r["kind"] == "S") >= 200         # the stored quantities are really compared (244 at the time of writing)


def test_n2_the_audit_can_fail_a_wrong_stored_number_and_an_unknown_number():
    q = {"sub_agree": 98.0}                                              # a stored value that differs from the typed 97
    row = {"file": "jcaption", "line": 1, "func": "take", "token": "97", "context": "agrees in 97 of 225 cells"}
    assert AUD.classify([row], q)[0]["equal"] is False
    q["sub_agree"] = 97.0
    assert AUD.classify([row], q)[0]["equal"] is True
    other = {"file": "jcaption", "line": 1, "func": "nonexistent_function", "token": "77.7", "context": "a number nobody ruled 77.7"}
    assert AUD.classify([other], {})[0]["kind"] == "?"


@needs
def test_n2_f4_captions_state_no_typed_data_number_that_the_stored_files_contradict(built):
    """The F4 captions read their data numbers (counts of the stored A11 rows, the Heun steps, the medians, the M2 ranges); the numbers of the built captions equal the stored ones."""
    full_a, full_b = _read(built, "F4a", "caption_full"), _read(built, "F4b", "caption_full")
    a11 = FG.load_F4()["a11"]
    k = C4.a11_counts(a11)
    assert f"{k['sub_agree']} of {k['sub_cells']} cells, {k['sub_pct']} percent, against {k['sub_needed']} needed" in full_b
    assert f"kept in {k['kept']} of {k['kept_n']} noisy seeds" in full_b
    assert "0.001, 5e-4, 2.5e-4 and 1e-4 tau" in full_a                  # the ladder is read from the stored A7 table
    assert "−0.000760, −0.0423 and −0.1051 at levels 0, 1 and 2" in full_a
    assert "between −25.7 and −24.3 per s" in full_b                    # rate_lo -25.66 and rate_hi -24.34 of the stored A3 table


# ---- N3 -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@needs
def test_n3_item1_p5_linear_is_dash_dot_in_both_f4a_captions(built):
    assert "linear (solid; P5 dash-dot)" in _read(built, "F4a", "caption")
    assert "solid line for P1 and P2, dash-dot line for P5" in _read(built, "F4a", "caption_full")
    assert "linear (solid)" not in _read(built, "F4a", "caption")
    from mprsurge.plotting import style as S
    assert S.get("P5").linestyle == "-." and S.get("P1").linestyle == "-" and S.get("P2").linestyle == "-"       # the drawing code uses the path style for the linear profile


@needs
def test_n3_item3_panel_c_errors_are_in_the_source_data_and_untestable_runs_have_no_error(built):
    rows = list(csv.DictReader(open(built["sup"] / "F4a_source_data.csv", newline="", encoding="utf-8")))
    err = [r for r in rows if "error of the prediction in steps" in r["series"]]
    by_panel = {p: sorted(round(float(r["y"]), 1) for r in err if r["panel"] == p) for p in ("a", "c")}
    assert by_panel["c"] == [4.4, 7.6, 12.7, 20.6, 33.1]                 # the five start-distance runs that the captions name
    assert by_panel["a"] == [25.1]                                       # only the testable P5 linear run; the three untestable in-range runs carry no error (13t-8 had a '0')
    assert all(float(r["y"]) != 0.0 for r in err)


@needs
def test_n3_item4_further_failed_checks_count_rows(built):
    sa, sb = _read(built, "F4a", "caption"), _read(built, "F4b", "caption")
    fa, fb = _read(built, "F4a", "caption_full"), _read(built, "F4b", "caption_full")
    assert "2 further failed checks" in sa and JSH.further_count("F4a", fa) == 2        # the two RB2 rows, named by their long form in the full caption
    assert "4 further failed checks" in sb and JSH.further_count("F4b", fb) == 4        # RB3(a), RB3(b), RB6 solver onset and the sigma check (its result is not drawn)


@needs
def test_n3_item5_the_red_ring_is_the_solver_dependent_value_and_the_used_value_is_named(built):
    for name in ("caption", "caption_full"):
        t = _read(built, "F4a", name)
        assert "0.0662" in t and "solver-dependent" in t or "which depends on the solver" in t
        assert "−0.000760" in t


@needs
def test_n3_item9_the_tie_counts_are_those_of_the_drawn_data(built):
    t = _read(built, "F4a", "caption_full")
    assert "80 of the 120 delays drawn in (e) equal −1.5" in t
    assert "the stored table holds 84 such delays, the other 4 being noisy seeds of F4b" in t
    assert "all 84 such delays" not in t


@needs
def test_n3_item10_rb3b_row_is_paired_with_the_tie(built):
    t = _read(built, "F4a", "caption_full")
    assert "The RB3(b) row has no stored value or threshold; what is drawn is that the classifier-onset delays tie at −1.5 at levels 0 and 1." in t
    assert "(a result, not a check)" in _read(built, "F4b", "caption")


@needs
def test_n3_word_limits_and_definitions(built):
    for fid in ("F4a", "F4b"):
        short = _read(built, fid, "caption").strip()
        assert JSH.words(short) <= 650
        assert JSH.undefined_terms(short) == []
        assert JSH.code_hits(short) == []


@needs
def test_n3_item8_terms_are_defined_in_the_short_captions(built):
    a = _read(built, "F4a", "caption")
    assert "testable, eta_bar not constant at the predicted time" in a and "steps of the prediction grid" in a
    assert "offset on the way down (eta_bar at the start of the down ramp minus eta_bar at the Hopf point)" in a
    assert "after a waiting time" in a                                   # P2: the second sense of 'delay' is not used for the path
    b = _read(built, "F4b", "caption")
    assert "the saddle-node (the fold, where the resting state disappears)" in b
    assert "the jump offset (eta_bar at the jump minus eta_bar at the fold)" in b
    assert "mode N" not in b and "mode D" not in b                       # the mode codes are gone from the short caption


# ---- N6 -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_n6_journal_reference_compares_with_the_latest_logged_hash_only(tmp_path):
    H = _script("ms13_check_hashes")
    rel = "figures/journal/F3/F3_journal.png"
    f = tmp_path / rel
    f.parent.mkdir(parents=True)
    f.write_bytes(b"new build")
    new = hashlib.sha256(b"new build").hexdigest()
    old = hashlib.sha256(b"old build").hexdigest()
    log = f"## DL-100 first\nDecision: {rel} {old}\n\n## DL-200 second\nDecision: {rel} {new}\n"
    assert H.journal_reference_problems(tmp_path, log) == []             # the older logged hash is not used
    log2 = f"## DL-100 first\nDecision: {rel} {new}\n\n## DL-200 second\nDecision: {rel} {old}\n"
    p = H.journal_reference_problems(tmp_path, log2)
    assert len(p) == 1 and p[0].startswith("JOURNAL-CHANGED") and old in p[0]
    assert H.journal_reference_problems(tmp_path, "## DL-1 x\nDecision: nothing logged\n") == []        # a file with no logged hash is not checked
    f.unlink()
    assert H.journal_reference_problems(tmp_path, log)[0].startswith("JOURNAL-MISSING")
    other = "figures/journal/F6/F6_journal.png"
    (tmp_path / other).parent.mkdir(parents=True)
    (tmp_path / other).write_bytes(b"f6")
    stale = f"## DL-50 early
Decision: {other} {old}

## DL-200 second
Decision: {rel} {new}
"
    f.write_bytes(b"new build")
    assert H.journal_reference_problems(tmp_path, stale) == []             # F6 is logged only in an older entry than the latest one with journal hashes: not a reference


def test_n6_the_real_f3_files_match_the_reference_logged_in_the_decision_log():
    H = _script("ms13_check_hashes")
    log = (ROOT / "docs" / "decision_log.md").read_bytes().decode("utf-8")
    assert H.journal_reference_problems(ROOT, log) == [] or not (ROOT / "figures/journal/F3/F3_journal.png").is_file()
    assert re.search(r"figures/journal/F3/F3_journal\.png [0-9a-f]{64}", log)
