"""MS11 11b evaluation choices (DL-343): required fields raise MissingChoice when open, the ruled values equal their sources, nothing is defaulted."""
import copy
from pathlib import Path

import pytest
import yaml

from mprsurge.analysis import ms11_eval_choices as EC

ROOT = Path(__file__).resolve().parents[1]
FILE = EC.load_file()
CH, META = FILE["choices"], FILE["meta"]
FROZEN = yaml.safe_load((ROOT / "configs/robustness_criteria.yaml").read_text(encoding="utf-8"))["robustness"]


def test_every_required_field_is_in_the_file_with_a_meta_entry_and_nothing_else():
    assert set(EC.REQUIRED) == set(CH) == set(META)
    assert all(m["status"] in ("ruled", "plan", "frozen", "OPEN") for m in META.values())


def test_no_required_field_is_open_after_11d_and_nothing_is_pending():
    assert EC.open_fields() == [] and all(v is not None for v in CH.values())
    assert all(m["status"] != "OPEN" for m in META.values())
    assert len(EC.check_all(CH)) == len(EC.REQUIRED) == 47            # 45 at 11c; 11d adds rb9d_parameter_spec (ruling 2b) and a11_pass_with_departures_words (ruling 2c)
    assert EC.PENDING == () and not FILE["pending"] and "rb9d_parameter_spec" in EC.REQUIRED


def test_a_missing_empty_or_disallowed_value_raises_and_nothing_is_defaulted():
    ch = copy.deepcopy(CH)
    assert EC.choice(ch, "rb2_judged_T_ramp_s") == 120.0
    for bad in (None, [], ""):
        ch["rb2_judged_T_ramp_s"] = bad
        with pytest.raises(EC.MissingChoice):
            EC.choice(ch, "rb2_judged_T_ramp_s")
    del ch["rb2_judged_T_ramp_s"]
    with pytest.raises(EC.MissingChoice):
        EC.choice(ch, "rb2_judged_T_ramp_s")
    ch["within_boundary"] = "strict"                      # ruling 5 allows only the inclusive reading
    with pytest.raises(EC.MissingChoice):
        EC.choice(ch, "within_boundary")
    ch["within_boundary"] = "inclusive"
    assert EC.choice(ch, "within_boundary") == "inclusive"
    with pytest.raises(EC.MissingChoice):
        EC.choice(ch, "not_a_field")


def test_ruled_values_equal_their_sources():
    assert CH["rb2_gate_class_set"] == ["S+", "S-rel", "S-abs"] and CH["rb2_gate_sigma_factors"] == [0.5, 1.0]       # ruling 2b
    assert CH["rb2_subgrid"]["cells_agree"] == 97 and CH["rb2_subgrid"]["cells"] == 225 and CH["rb2_subgrid"]["re_evaluated"] is False
    assert CH["rb10_variants"] == FROZEN["RB10"]["variations"]["value"]                                          # frozen leaf
    assert {"default_tau": CH["rb6_network_dt_pair"][0], "halved_tau": CH["rb6_network_dt_pair"][1]} == FROZEN["RB6"]["network_dt_for_f_pk_test"]["value"]
    assert CH["rb6_solver_pair_scope"] == "headline_only" and CH["rb6_network_seeds"] == 3 and CH["d36_basis"] == "B"
    assert EC.REQUIRED["rb6_network_fpk_bound_boundary"] == ("strict",)
    assert FROZEN["RB6"]["network_dt_f_pk_change_max"]["value"] == 0.02 and FROZEN["RB2"]["sigma_factors"]["value"] == [0.5, 1.0, 2.0]
    assert FROZEN["RB2"]["headline_class_kept_min_seeds"]["value"].startswith("8 of 10")


def test_no_numeric_threshold_is_typed_in_the_choices():
    """The thresholds (8 of 10, 2 percent, 0.5 percent, 5 percent, 10 percent, 1/W) are read from the frozen criteria, not stored here."""
    flat = repr({k: v for k, v in CH.items() if k != "rb10_variants"})          # the RB10 variant list is the frozen list, checked equal above
    for t in ("0.02", "0.005", "0.05", "0.10", "0.9", "1/W"):
        assert t not in flat
