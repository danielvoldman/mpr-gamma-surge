"""MS13 13i: tests of the fifth figure (FS5, untagged draft). They read the stored results under results/ (git-ignored) and the two classifier test files as text,
and skip if those are absent. Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (SHA-256, set equality, exact stored
values read back from the drawn artists) except row 9's array comparison (rel 1e-12, plan section 8 row 9) and the take-home numbers, each quoted to the digits the
message prints (stated per assertion)."""
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

ROOT = C.repo_root()
RES = ROOT / "results"
pytestmark = pytest.mark.skipif(not (all((RES / p).is_file() for p in FG.FS5_INPUTS) and all((ROOT / p).is_file() for p in FG.FS5_TEST_FILES)),
                                reason="stored FS5 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "FS5"
    return FG.make_FS5(out_dir=out), out


def _ax(fig, prefix):
    hits = [a for a in fig.axes if a.get_title(loc="left").startswith(prefix) or a.get_title().startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step():
    a, b = FG.prepare_FS5(FG.load_FS5()), FG.prepare_FS5(FG.load_FS5())
    assert FG.drawn_data_sha256(a) == FG.drawn_data_sha256(b)                      # exact
    assert sorted(a) == sorted(b)
    for k in a:
        if isinstance(a[k], np.ndarray):
            np.testing.assert_allclose(a[k], b[k], rtol=1e-12, atol=0, equal_nan=True)
    c = dict(a)
    c["rb9b_diff"] = a["rb9b_diff"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(a)                      # the hash does see a changed value


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "FS5_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.FS5_CLAIM_LIMITS)                   # exact set equality
    assert "MS12-C1" not in prov["claim_limits"]                                   # the section 5 table lists MS12-C1 for F1 to F6 and FS6 only
    caption = (out / "FS5_caption.txt").read_text(encoding="utf-8")
    assert all(i in caption for i in FG.FS5_CLAIM_LIMITS)
    assert prov["draft"] is True and prov["figure_id"] == "FS5" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]
    assert prov["git"]["dirty"] in (True, False)


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_FS5():
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_FS5.py", "fig_FS5_for_test")
    registry = {e["path"] for e in reg.INPUTS["FS5"] if e["kind"] == "file"}
    assert all(e["kind"] == "file" for e in reg.INPUTS["FS5"])
    declared = set(FG.FS5_INPUTS) | {"../" + p for p in FG.FS5_TEST_FILES}
    assert registry == declared                                                    # exact set equality (results files and the two test files)
    assert set(script.DECLARED_INPUTS) == set(FG.FS5_INPUTS) and tuple(script.DECLARED_TEST_FILES) == FG.FS5_TEST_FILES
    assert len(FG.FS5_INPUTS) == 12 and len(reg.INPUTS["FS5"]) == 14               # 12 results files and 2 test files; 7 registry entries added at 13i


def test_data_step_opens_only_paths_under_results_and_the_two_declared_test_files_and_the_script_opens_nothing_itself():
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        FG.prepare_FS5(FG.load_FS5())
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res = RES.resolve()
    allowed_tests = {(ROOT / p).resolve() for p in FG.FS5_TEST_FILES}
    for path, mode in opened:
        pr = Path(path).resolve()
        assert pr.is_relative_to(res) or pr in allowed_tests, path                 # exact: results/ or one of the two declared test files (read as text)
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)               # and none is opened for writing
    assert len(opened) >= len(FG.FS5_INPUTS)
    tree = ast.parse((ROOT / "scripts" / "fig_FS5.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_FS5
    src = (ROOT / "src" / "mprsurge" / "plotting" / "figures.py").read_text(encoding="utf-8")
    block = src[src.index("def load_FS5"):src.index("def prepare_FS5")]
    assert "pytest" not in block and "subprocess" not in block and "exec(" not in block and "import_module" not in block          # the test files are parsed, never imported or run


def test_proposed_take_home_numbers_agree_with_the_stored_arrays_to_the_printed_digits():
    d = FG.prepare_FS5(FG.load_FS5())
    assert list(d["white_nonNS"][:4]) == [306.0, 400.0, 172.0, 24.0] and list(d["white_W"][:4]) == pytest.approx([0.2, 1 / 3, 0.592759, 1.054093], abs=1e-6)       # exact counts
    assert set(d["white_den"]) == {500.0}                                                                   # 500 records per window
    assert d["rb10_headline_all_pass"] and d["rb10_n_cells"] == 900 and len(d["rb10_variant"]) == 9
    assert float(d["rb10_fraction"].max()) == pytest.approx(0.0167, abs=5e-5)                               # printed 1.67 percent (stored 1.6667)
    assert d["rb9a_value"] == pytest.approx(1.2e-8, abs=5e-10) and d["rb9a_tol"] == 0.005                   # printed 1.2e-8 (stored 1.2258e-8)
    assert (int(d["rb9c_changed"][0]), int(d["rb9c_n"][0])) == (14, 900)                                    # exact: 14 of 900
    assert (d["rb9b_f_spectral"], d["rb9b_bound"]) == (49.0, 0.5) and d["rb9b_within"] is False             # exact
    assert d["rb9b_f_cycle"] == pytest.approx(44.609, abs=5e-4) and d["rb9b_diff"] == pytest.approx(4.391, abs=5e-4)    # printed 44.609 and 4.391
    assert len(d["syn_label"]) == 39 and len({s.split(" | ")[0] for s in d["syn_label"]}) == 26             # 26 synthetic cases, 39 (case, T_ramp) rows
    assert d["tests_n"] == [8, 56] and len(d["tests_xfail_name"]) == 7                                       # exact: 7 strict-xfail marks (6 on functions, 1 on parameters)
    assert sum("(xfail mark on parameters)" in n for n in d["tests_xfail_name"]) == 1
    assert FG.FS5_TAKE_HOME.startswith("PROPOSED (for ruling):")


def test_the_test_case_reader_lists_functions_and_xfail_marks_from_the_decorators_without_running_anything():
    # The fixture source is built from pieces so that this file itself holds no decorator text: tests/test_criteria_draft.py scans every tests/test_*.py for
    # the strict-xfail decorator followed by a test function and counts the names against the gate wording (DL-161).
    mark = "pytest.mark." + "xf" + "ail"
    src = "\n".join([
        "import pytest",
        f'_ALIAS = {mark}(strict=True, raises=AssertionError, reason="r1")',
        "def test_plain():",
        "    pass",
        f'@{mark}(strict=True, reason="r2")',
        "def test_marked():",
        "    assert False",
        "@_ALIAS",
        "def test_alias():",
        "    assert False",
        "def _params():",
        "    return [pytest.param(1, marks=[_ALIAS])]",
        "",
    ])
    got = FG._test_cases(src)
    by = {c["name"]: c for c in got}
    assert by["test_plain"]["xfail"] is False
    assert (by["test_marked"]["xfail"], by["test_marked"]["strict"], by["test_marked"]["reason"]) == (True, True, "r2")
    assert (by["test_alias"]["xfail"], by["test_alias"]["reason"]) == (True, "r1")
    assert by["_params (xfail mark on parameters)"]["helper"] is True and by["_params (xfail mark on parameters)"]["reason"] == "r1"
    assert len(got) == 4


def test_a_class_change_count_that_disagrees_with_the_stored_summary_stops_the_build():
    raw = FG.load_FS5()
    raw["sens"]["changes_vs_V0"][0]["changed"] += 1
    with pytest.raises(FG.DataError, match="class changes"):
        FG.prepare_FS5(raw)


def test_an_a11_status_that_disagrees_with_the_evaluator_file_stops_the_build():
    raw = FG.load_FS5()
    for r in raw["a11"]:
        if r["check_id"] == "b_spectral_vs_cycle_headline":
            r["pass_or_fail"] = "PASS"
    with pytest.raises(FG.DataError, match="differs from the evaluator file"):
        FG.prepare_FS5(raw)


def test_the_a6_slice_check_stops_the_build_when_the_summary_value_differs():
    raw = FG.load_FS5()
    raw["a6_summary"]["devalle"]["f_at_eta_4"] += 1e-9
    with pytest.raises(FG.DataError, match="A6 slice"):
        FG.prepare_FS5(raw)


def test_drawn_markers_lines_bars_and_points_equal_the_stored_values_exactly():
    import matplotlib.pyplot as plt
    raw = FG.load_FS5()
    d = FG.prepare_FS5(raw)
    fig = FG._draw_FS5(d, True)
    try:
        la = _ax(fig, "(a)")
        for ci, name in enumerate(d["class_order"]):
            sel = d["syn_code"] == ci
            if not sel.any():
                continue
            ln = [x for x in la.get_lines() if x.get_label().startswith(name if name != "not_run" else "not run")][0]
            yy, xx = np.nonzero(sel)
            assert np.array_equal(ln.get_xdata(), xx) and np.array_equal(ln.get_ydata(), yy)                  # exact: class cell positions
        assert sum(len(x.get_xdata()) for x in la.get_lines() if x.get_linestyle() == "None") == 390          # every stored synthetic classification is drawn
        lc = _ax(fig, "(c)")
        texts = [t.get_text() for t in lc.texts]
        assert texts[0] == f"{int(d['chg_changed'][0, 0])}/{int(d['chg_n'][0])}" and len(texts) == 45
        assert "71 not run" in " ".join(texts)
        ld = _ax(fig, "(d)")
        for i, ln in enumerate(ld.get_lines()):
            assert np.array_equal(ln.get_xdata(), d["reach_level"]) and np.array_equal(ln.get_ydata(), d["reach_share"][i])      # exact
        le = _ax(fig, "(e)")
        rects = le.patches
        assert len(rects) == 30
        h = np.array([p.get_height() for p in rects]).reshape(5, 6)
        assert np.array_equal(h, (d["white_count"][:, :5] / d["white_den"][:, None]).T)                          # exact: stored counts over 500
        tops = np.array([p.get_y() + p.get_height() for p in rects]).reshape(5, 6)
        assert np.array_equal(tops[-1], np.cumsum(h, axis=0)[-1]) and np.allclose(tops[-1], 1.0, atol=1e-12)   # the five classes stack to the whole of the 500 records
        lf = _ax(fig, "(f)")
        pts = [x for x in lf.get_lines() if x.get_linestyle() == "None"][0]
        assert np.array_equal(pts.get_xdata(), d["rb10_fraction"])
        panels = [a for a in fig.axes if a.get_title().startswith("(g")]
        assert len(panels) == 4
        g1, g2, g3, g4 = panels
        assert np.array_equal(g1.get_lines()[0].get_ydata(), d["rb9a_diff"][0]) and np.array_equal(g1.get_lines()[1].get_ydata(), d["rb9a_diff"][1])
        assert g2.get_lines()[0].get_ydata()[0] == d["rb9b_f_spectral"] and g2.get_lines()[1].get_ydata()[0] == d["rb9b_f_cycle"]
        assert np.array_equal(g3.get_lines()[0].get_ydata(), d["rb9c_changed"] / d["rb9c_n"])
        assert np.array_equal(np.array([x.get_ydata()[0] for x in g4.get_lines()[:3]]), d["rb9d_f_pk"])           # the three stored peak frequencies
        assert g1.get_lines()[2].get_ydata()[0] == FG.FS5_RB9A_TOL and g3.get_lines()[1].get_ydata()[0] == FG.FS5_RB9C_BOUND      # the plan bounds, as stored
    finally:
        plt.close(fig)


def test_layout_no_legend_covers_a_line_or_marker_no_text_leaves_the_canvas_and_the_failure_is_shown():
    """13i layout check on the drawn artists (tests/figlayout.py; exact geometry in display pixels)."""
    import matplotlib.pyplot as plt
    from figlayout import clipped_texts, legend_line_hits
    d = FG.prepare_FS5(FG.load_FS5())
    fig = FG._draw_FS5(d, True)
    try:
        assert legend_line_hits(fig) == []
        assert clipped_texts(fig) == []
        texts = " ".join(t.get_text() for a in fig.axes for t in a.texts) + " ".join(a.get_title() for a in fig.axes)
        assert "RB9 b_spectral_vs_cycle_headline: FAIL" in texts and "(g2) RB9(b) FAIL" in texts           # the RB9(b) failure is drawn at equal weight, not dropped
        assert "(g1) RB9(a) PASS" in texts and "(g3) RB9(c) PASS" in texts
    finally:
        plt.close(fig)


def test_build_hashes_and_params_agree_with_the_provenance(built):
    res, out = built
    prov = out / "FS5_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "FS5_params.csv", prov) == []
    assert (out / "FS5.pdf").stat().st_size > 0 and (out / "FS5.png").stat().st_size > 0
    rec = json.loads(prov.read_text(encoding="utf-8"))
    paths = {i["path"] for i in rec["inputs"]}
    assert {p.split("results/")[-1] for p in paths if "results/" in p} == set(FG.FS5_INPUTS)
    assert {p for p in paths if "results/" not in p} == set(FG.FS5_TEST_FILES)


def test_caption_names_the_plotted_quantities_marks_the_proposals_and_has_no_provenance_hash(built):
    res, out = built
    caption = (out / "FS5_caption.txt").read_text(encoding="utf-8")
    assert caption.startswith("FS5. PROPOSED (for ruling):")
    assert "Claim limits: " + ", ".join(FG.FS5_CLAIM_LIMITS) + "." in caption and "PROPOSED for the reviewer's ruling" in caption
    assert "RB9(b) FAILS" in caption and "UNVERIFIED" in caption
    assert "Panel (a)" in caption and "Panel (c)" in caption and "Panel (d)" in caption and "Panel (e)" in caption and "Panels (f) and (g)" in caption
    assert "DL-430" in caption and "provisional" in caption
    assert not re.search(r"[0-9a-f]{12,}", caption) and "hash" not in caption.lower() and not re.search(r"\bsha(256)?\b", caption.lower())
    assert "Provenance" not in caption and "FS5_" not in caption
