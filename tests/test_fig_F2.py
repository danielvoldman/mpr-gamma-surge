"""MS13 13f: tests of the second figure (F2, untagged draft). They read the stored results under results/ (git-ignored) and skip if those are absent.
Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (SHA-256, set equality, exact stored values) except
row 9's array comparison (rel 1e-12, plan section 8 row 9), the read-window extrema against the stored v amplitude (abs 1e-12) and the take-home numbers,
each quoted to the digits the message prints (stated per assertion)."""
import ast
import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge.plotting import figprov as F
from mprsurge.plotting import figures as FG
from mprsurge.plotting import style as S

ROOT = C.repo_root()
RES = ROOT / "results"
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F2_INPUTS) or not (RES / "A5/check/a5_check.json").is_file(),
                                reason="stored F2 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "F2"
    return FG.make_F2(out_dir=out), out


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step():
    a, b = FG.prepare_F2(FG.load_F2()), FG.prepare_F2(FG.load_F2())
    assert FG.drawn_data_sha256(a) == FG.drawn_data_sha256(b)                      # exact
    assert sorted(a) == sorted(b)
    for k in a:
        if isinstance(a[k], np.ndarray):
            np.testing.assert_allclose(a[k], b[k], rtol=1e-12, atol=0, equal_nan=True)
    c = dict(a)
    c["eta_H"] = a["eta_H"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(a)                      # the hash does see a changed value


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "F2_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.F2_CLAIM_LIMITS) == {"MS11-C7", "MS12-C1", "G4-C2"}      # exact set equality
    caption = (out / "F2_caption.txt").read_text(encoding="utf-8")
    assert all(i in caption for i in FG.F2_CLAIM_LIMITS)
    assert prov["draft"] is True and prov["figure_id"] == "F2" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_F2():
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_F2.py", "fig_F2_for_test")
    registry = set()
    for e in reg.INPUTS["F2"]:
        if e["kind"] == "file":
            registry.add(e["path"])
        else:                                                                      # a record family: json and its npz, as the figure opens both
            for j in RES.glob(e["pattern"]):
                if not j.name.endswith((".dry.json", "_params.md")) and j.suffix == ".json":
                    registry |= {j.relative_to(RES).as_posix(), j.with_suffix(".npz").relative_to(RES).as_posix()}
    assert registry == set(script.DECLARED_INPUTS) == set(FG.F2_INPUTS)            # exact set equality
    assert len(FG.F2_INPUTS) == 10 and len(reg.INPUTS["F2"]) == 8                  # 4 files and 2 record families, plus 4 added at 13f (3 files and the A11 table; the A5 record)


def test_data_step_opens_only_paths_under_results_and_the_script_opens_nothing_itself():
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        FG.prepare_F2(FG.load_F2())
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res = RES.resolve()
    for path, mode in opened:
        assert Path(path).resolve().is_relative_to(res), path                      # exact: every opened path is under results/
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)               # and none is opened for writing
    tree = ast.parse((ROOT / "scripts" / "fig_F2.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_F2


def test_take_home_numbers_agree_with_the_stored_arrays_to_the_printed_digits():
    d = FG.prepare_F2(FG.load_F2())
    assert d["eta_H"] == pytest.approx(2.896, abs=5e-4) and d["hopf_type"] == "SuperCritical"       # printed 2.896; DL-126 verdict is the stored a5.json string
    assert d["a5_cycle_unstable_count"] == 0 and d["a5_eta_max"] == 8.0                              # exact: stable cycles to eta_bar 8
    assert d["mf_updown_max_abs_from_0p2"] == pytest.approx(1.2e-3, abs=5e-5)                         # printed 1.2e-3 (stored 1.1634e-3)
    assert 100 * d["cmp_rel_v_above_max"] == pytest.approx(13.2, abs=0.05) and 100 * d["cmp_rel_v_above_min"] == pytest.approx(-2.5, abs=0.05)
    assert d["net_floor_v_ptp_min"] == pytest.approx(0.22, abs=0.005) and d["net_floor_v_ptp_max"] == pytest.approx(0.31, abs=0.005)
    assert d["net_floor_steps"] == 10
    chk = json.loads((RES / "A5/check/a5_check.json").read_text(encoding="utf-8"))
    assert chk["a5_vs_s4"]["devalle"]["max_abs_rel_diff"] == pytest.approx(1.84e-3, abs=5e-6)         # DL-129, stored; printed 1.84e-3
    assert [(r["rb_id"], r["check_id"], r["status"]) for r in d["strip"]] == [("RB1", "headline_10s", "FAIL"), ("RB1", "headline_120s", "FAIL"),
                                                                              ("RB1", "cells_30s", "FAIL"), ("RB1", "overall", "FAIL")]


def test_a5_arrays_and_the_hopf_point_equal_the_stored_values_exactly():
    raw = FG.load_F2()
    d = FG.prepare_F2(raw)
    with np.load(RES / FG.F2_INPUTS[0]) as z:
        up = z["devalle_direction_up"]
        for name, m in (("up", up), ("down", ~up)):
            for col, stored in (("param", "devalle_param"), ("vmax", "devalle_vmax"), ("vmin", "devalle_vmin"), ("amp", "devalle_amplitude_v")):
                assert np.array_equal(d[f"a5_{name}_{col}"], z[stored][m])
        assert np.array_equal(d["fixed_v"], z["devalle_fixed_v"]) and d["eta_H"] == float(z["devalle_hopf_eta_bar"][0])
        assert d["hopf_v_interp"] == pytest.approx(float(np.interp(d["eta_H"], z["devalle_fixed_param"], z["devalle_fixed_v"])), rel=1e-12, abs=0)
    assert d["eta_H"] == raw["a5json"]["branches"]["devalle"]["hopf_param"]


def test_every_network_symbol_plotted_equals_a_stored_value():
    # network symbols are the Line2D objects with the open square or open diamond marks; every plotted y must be a stored value (v max and min recomputed
    # here from the stored series by a separate code path; the stored v amplitude; the stored network-against-mean-field difference), every x a stored step parameter
    raw = FG.load_F2()
    d = FG.prepare_F2(raw)
    fig = FG._draw_F2(d, True, [])
    net = [S.diagram_mark("s4_net_up").marker, S.diagram_mark("s4_net_down").marker]
    with np.load(RES / FG.F2_INPUTS[6]) as z, np.load(RES / FG.F2_INPUTS[8]) as q:
        t, v, k, p = z["t_ms"], z["v"], z["step"], z["step_param"]
        ext_max, ext_min = [], []
        for i in range(p.size):
            ti, vi = t[k == i], v[k == i]
            w = vi[ti >= ti[-1] - 1000.0 - 1e-9]
            ext_max.append(w.max())
            ext_min.append(w.min())
        stored_y = [np.array(ext_max), np.array(ext_min), q["net_v_ptp"], q["cmp_rel_v_ptp"]]
        stored_x = p
    n_symbols = 0
    for ax in fig.axes:
        for ln in ax.get_lines():
            mk = ln.get_marker()
            if any(isinstance(mk, type(m)) and np.array_equal(np.asarray(mk, dtype=float), np.asarray(m, dtype=float)) for m in net):
                x, y = ln.get_xdata(), ln.get_ydata()
                assert np.all(np.isin(x, stored_x))                                 # exact
                assert all(np.isin(yy, np.concatenate(stored_y)) for yy in y)       # exact
                n_symbols += len(x)
    # panel a: max and min of 30 steps, panel b: 30 amplitudes, panel c: the steps above eta_H + 0.1 (18 of 30)
    assert n_symbols == 30 * 2 + 30 + int(d["net_above_mask"].sum()) == 60 + 30 + 18
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_read_window_extrema_minus_stored_amplitude_is_below_1e_12_and_the_mean_field_matches_the_summary():
    d = FG.prepare_F2(FG.load_F2())
    for key in ("mf", "net"):
        assert float(np.max(np.abs((d[f"{key}_vmax"] - d[f"{key}_vmin"]) - d[f"{key}_v_ptp"]))) <= 1e-12
        assert d[f"{key}_ptp_check_max_abs"] <= 1e-12
    assert d["mf_param"].size == 122 and d["net_param"].size == 30


def test_build_hashes_and_params_agree_with_the_provenance(built):
    res, out = built
    prov = out / "F2_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "F2_params.csv", prov) == []
    assert (out / "F2.pdf").stat().st_size > 0 and (out / "F2.png").stat().st_size > 0
    rec = json.loads(prov.read_text(encoding="utf-8"))
    assert {i["path"].split("results/")[-1] for i in rec["inputs"]} == set(FG.F2_INPUTS)


def test_caption_names_the_plotted_quantity_states_the_ruled_limits_and_has_no_provenance_hash(built):
    res, out = built
    caption = (out / "F2_caption.txt").read_text(encoding="utf-8")
    assert caption.startswith("F2. At ref_devalle the limit cycle appears") and "PROPOSED" not in caption        # take-home and claim limits ruled in 13g
    assert "Nothing in this figure is a frequency or a spectral peak" in caption and "voltage variable v" in caption
    assert "not a fold of cycles" in caption and "mean V of non-refractory neurons" in caption and "F2_" not in caption
    from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS as CL                   # 13o (DL-495 T3, R2): the definitions are printed
    assert "Claim limits: " + "; ".join(f"{i}: {CL[i][0]} ({', '.join(CL[i][1])})" for i in ("MS11-C7", "MS12-C1", "G4-C2")) + "." in caption and "UNVERIFIED readings of the plan" in caption
    assert not re.search(r"[0-9a-f]{12,}", caption) and "hash" not in caption.lower() and not re.search(r"\bsha(256)?\b", caption.lower())
    assert "Provenance" not in caption


# ---- 13g: layout review of the first draft (v2)

def test_panel_c_limits_keep_every_drawn_point_inside_the_frame_with_a_margin_of_at_least_5_percent():
    # tolerance: the margin is at least 5 percent of the axis span on each side (the first draft had its largest point on the frame)
    import matplotlib.pyplot as plt
    d = FG.prepare_F2(FG.load_F2())
    fig = FG._draw_F2(d, True, FG.strip_lines(d))
    try:
        ax = fig.axes[2]
        lo, hi = ax.get_ylim()
        v = d["cmp_rel_v_ptp"][d["net_above_mask"] == 1.0]
        assert lo < min(v.min(), 0.0) - 0.05 * (hi - lo) and hi > max(v.max(), 0.0) + 0.05 * (hi - lo)
    finally:
        plt.close(fig)


def test_strip_text_says_when_the_stored_threshold_is_blank():
    d = FG.prepare_F2(FG.load_F2())
    lines = FG.strip_lines(d)
    assert len(lines) == 4 and not any("threshold )" in s for s in lines)               # exact
    blank = [r for r in d["strip"] if not r["threshold"]]
    assert len([s for s in lines if "threshold blank in the table" in s]) == len(blank) == 1
