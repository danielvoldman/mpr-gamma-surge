"""MS9 9j: A9 table v2 builder. Synthetic rows; nothing is integrated."""
import pandas as pd

from mprsurge.analysis import ms9_9j as N


def _row(surge, status="ok", flags="", prim="", g=pd.NA, h=pd.NA):
    return {"surge": surge, "status": status, "labels_a_f_all": flags, "label_a_f_primary": prim, "g": g, "h": h}


def test_failure_label_empty_on_surge_cells():
    assert N.failure_label(_row(True, flags="a,b", prim="a")) == ""


def test_failure_label_primary_then_g_h_then_empty():
    assert N.failure_label(_row(False, flags="c,f", prim="c")) == "c"
    assert N.failure_label(_row(False, g=True, h=False)) == "g"
    assert N.failure_label(_row(False, g=False, h=True)) == "h"
    assert N.failure_label(_row(False, g=False, h=False)) == ""
    assert N.failure_label(_row(False, g=pd.NA, h=pd.NA)) == ""


def test_failed_run_is_labelled_failed():
    assert N.failure_label(_row(False, status="failed", flags="a", prim="a")) == "failed"


def test_reasons_roundtrip():
    assert N._reasons("a=x;b=y") == {"a": "x", "b": "y"} and N._reasons(None) == {}


def test_flag_counts_counts_letters_per_map():
    df = pd.DataFrame({"map": ["1", "1", "1", "2"], "surge": [True, True, False, True], "class": ["D-tr", "D-tr", "D-none", "D-tr"],
                       "struct_flags": ["a,c", "", "b", ""]})
    fc = N.flag_counts(df)
    assert fc["1"]["surge_cells"] == 2 and fc["1"]["any_flag"] == 1 and fc["1"]["per_letter"]["a"] == 1 and fc["1"]["per_letter"]["b"] == 0
    assert fc["2"]["any_flag"] == 0
