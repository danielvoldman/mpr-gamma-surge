"""MS9 9i: A7 (S6 part), A9, A10 and G3 table builders. Synthetic inputs and, where the stored files exist, structural checks; nothing is integrated."""
import copy
import math

import pandas as pd
import pytest

from mprsurge import config as C
from mprsurge.analysis import entry_exit as EE
from mprsurge.analysis import ms9_9i as N

ROOT = C.repo_root()


def _cfg(name="path_hypoxia", T=10.0, **over):
    cfg = copy.deepcopy(C.resolve_config("configs/S5_ramp.yaml"))
    cfg["path"].update(name=name, T_ramp_s=T, **over)
    return cfg


def test_lead_re_matches_entry_exit_without_drive():
    a = N.lead_re_full(2.0, -21.0, 0.3, 0.0, 0.5)
    b = EE.leading_re(2.0, -21.0, 0.3, 0.5)
    assert math.isclose(a, b, rel_tol=1e-12)


def test_lead_re_drive_equals_shifted_eta():
    assert math.isclose(N.lead_re_full(1.0, -21.0, 0.3, 1.0, 0.5), N.lead_re_full(2.0, -21.0, 0.3, 0.0, 0.5), rel_tol=1e-12)


def test_static_exit_p2_equals_the_o12_reading():
    """On P2 (I and Delta constant) the generalised J_exit,static lies in the node interval of the last positive-to-non-positive crossing."""
    cfg = _cfg(T=10.0)
    h = 0.025
    j, why = N.j_exit_static_path(cfg, h)
    path, t, re, _ = EE.path_gain(cfg, h)
    idx = [k for k in range(len(re) - 1) if re[k] > 0.0 >= re[k + 1]]
    assert why == "" and idx
    lo, hi = sorted((float(path.J(t[idx[-1]])), float(path.J(t[idx[-1] + 1]))))
    assert lo - 1e-9 <= j <= hi + 1e-9


def test_static_exit_p3_passes_the_drive_to_the_eigenvalue(monkeypatch):
    seen = []
    orig = N.lead_re_full
    monkeypatch.setattr(N, "lead_re_full", lambda eta, J, D, I, td: (seen.append(I), orig(eta, J, D, I, td))[1])
    N.j_exit_static_path(_cfg("path_drive", I_amp=2.0), 0.025)
    assert max(seen) == pytest.approx(2.0) and min(seen) == 0.0


def test_static_exit_p4_passes_the_ramped_delta(monkeypatch):
    seen = []
    orig = N.lead_re_full
    monkeypatch.setattr(N, "lead_re_full", lambda eta, J, D, I, td: (seen.append(D), orig(eta, J, D, I, td))[1])
    N.j_exit_static_path(_cfg("path_delta_up", Delta_factor=1.5), 0.025)
    assert max(seen) == pytest.approx(0.3 * 1.5) and min(seen) == pytest.approx(0.3)


def test_letters_normalises_label_strings():
    assert N._letters("cf") == ["c", "f"] == N._letters("c,f") == N._letters(" f c")
    assert N._letters(float("nan")) == [] == N._letters(None)


def test_nan_reason_check_finds_missing_reason():
    df = pd.DataFrame({"x": [1.0, float("nan"), float("nan")], "nan_reasons": ["", "x=because", ""]})
    assert N.nan_reason_columns(df, ["x"]) == [(2, "x")]


def test_count_row_and_g3_columns():
    r = N._count_row("g", "s", "N", ["S+", "S+", "S-sus", "NS", "weird"])
    assert r["n_runs"] == 5 and r["S+"] == 2 and r["S-sus"] == 1 and r["NS"] == 1 and r["other"] == 1
    assert r["n_surge_class"] == 2 and r["n_sus_class"] == 1 and r["n_quiet_class"] == 1


def test_g3_markdown_has_one_line_per_group():
    df = pd.DataFrame([N._count_row("a", "s", "D", ["D-tr", "D-none"]), N._count_row("b", "s", "N", ["NS"])], columns=list(N.G3_COLUMNS))
    md = N.g3_markdown(df)
    assert md.count("\n| a | D | 2 |") == 1 and md.count("\n| b | N | 1 |") == 1
    assert "no verdict" in md


stored = pytest.mark.skipif(not (ROOT / "results/ms9/9h/p1_cells.csv").exists(), reason="stored MS9 tables are not in this clone")


@stored
def test_subgrid_agreement_numbers_are_the_logged_ones():
    sub = N.subgrid_agreement()
    assert len(sub) == 225 and int(sub["d24_cell_agrees"].sum()) == 97 and int(sub["p1_cell_agrees"].sum()) == 173


@stored
def test_d31_nodes_and_a10_structure():
    d = N.d31_nodes()
    assert len(d) == 178 and d["supplementary"].all() and d["class"].value_counts().to_dict() == {"D-tr": 112, "D-none": 66}
    a = N.a10_controls()
    assert (a["g7_status"] == N.G7_STATUS).all()
    assert a["control"].value_counts().to_dict() == {"NC1": 13 + 5 + 1 + 13, "NC2": 13, "NC3": 13}


@stored
def test_a9_regime_map_structure():
    a9 = N.a9_regime_map()
    assert a9["map"].value_counts().to_dict() == {"1": 900, "2": 325, "headline": 1}
    assert int(a9["unlabelled_a_h"].sum()) == 0 and a9["headline_marker"].sum() == 1
    assert N.nan_reason_columns(a9, N.A9_NUMERIC + ("g", "h", "inside_a4_region")) == []
