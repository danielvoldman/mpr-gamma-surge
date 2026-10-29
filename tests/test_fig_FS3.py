"""MS13 13j: tests of the seventh figure (FS3, untagged draft). They read the stored results under results/ (git-ignored) and skip if those are absent.
Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (SHA-256, set equality, counts, exact stored values read back from the
drawn artists) except row 9's array comparison (rel 1e-12, plan section 8 row 9); the take-home numbers are integer counts and are compared exactly."""
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
from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS as CL

ROOT = C.repo_root()
RES = ROOT / "results"
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.FS3_INPUTS), reason="stored FS3 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "FS3"
    return FG.make_FS3(out_dir=out), out


def _ax(fig, prefix):
    hits = [a for a in fig.axes if a.get_title(loc="left").startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step():
    a, b = FG.prepare_FS3(FG.load_FS3()), FG.prepare_FS3(FG.load_FS3())
    assert FG.drawn_data_sha256(a) == FG.drawn_data_sha256(b)                      # exact
    assert sorted(a) == sorted(b)
    for k in a:
        if isinstance(a[k], np.ndarray):
            np.testing.assert_allclose(a[k], b[k], rtol=1e-12, atol=0, equal_nan=True)
    c = dict(a)
    c["s9_fpk_err_median"] = a["s9_fpk_err_median"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(a)                      # the hash does see a changed value


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "FS3_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.FS3_CLAIM_LIMITS)                   # exact set equality
    assert "MS12-C1" not in prov["claim_limits"]                                   # the section 5 table lists MS12-C1 for F1 to F6 and FS6 only
    assert all(i in CL for i in FG.FS3_CLAIM_LIMITS)                               # every printed label is defined once in the label table
    assert prov["draft"] is True and prov["figure_id"] == "FS3" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]
    assert {t["path"].split("results/")[-1]: t["rows"] for t in prov["input_tables"]} == {FG.FS3_INPUTS[2]: 44}      # table row count is recorded


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_FS3():
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_FS3.py", "fig_FS3_for_test")
    assert all(e["kind"] == "file" for e in reg.INPUTS["FS3"])
    assert {e["path"] for e in reg.INPUTS["FS3"]} == set(script.DECLARED_INPUTS) == set(FG.FS3_INPUTS)      # exact set equality
    assert len(FG.FS3_INPUTS) == 6 and set(reg.TIMING["FS3"]) <= {e["label"] for e in reg.INPUTS["FS3"]}


def test_data_step_opens_only_paths_under_results_reads_no_series_and_the_script_opens_nothing_itself():
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        FG.prepare_FS3(FG.load_FS3())
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res = RES.resolve()
    for path, mode in opened:
        assert Path(path).resolve().is_relative_to(res), path                      # exact: every opened path is under results/
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)               # and none is opened for writing
        assert not str(path).endswith(".npz"), path                                # tables first: no series file is opened
    assert len(opened) >= len(FG.FS3_INPUTS)
    tree = ast.parse((ROOT / "scripts" / "fig_FS3.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_FS3


def test_proposed_take_home_numbers_equal_the_stored_tables_exactly():
    d = FG.prepare_FS3(FG.load_FS3())
    assert d["s9_surge"].tolist() == [4, 7, 2, 5] and d["s9_seeds"].tolist() == [10, 10, 10, 10]               # take-home: surge seeds per N
    assert (d["nrule_count_3e4"], d["nrule_count_1e4"], d["nrule_pass"]) == (5, 2, True) and d["mf_ref_class"] == "D-tr"
    assert d["s9_ctrl_surge"].tolist() == [0, 2, 1, 1] and d["s9_ctrl_n"].tolist() == [3, 3, 3, 3]            # take-home: controls reaching a surge class
    assert d["shape_class"] == [["S-sus", "S-abs", "S-sus"], ["S-abs"] * 3, ["S-abs"] * 3] and d["rb8_verdict"] == "NOT EVALUABLE"
    assert d["gate_kept"].tolist() == [8, 7] and d["gate_status"] == ["PASS", "FAIL"]
    assert d["noise_ctrl_kept"].tolist() == [7, 7, 7]
    assert (d["subgrid_agree"], d["subgrid_cells"], d["subgrid_needed"], d["subgrid_status"]) == (97, 225, 203, "FAILED")
    txt = FG.FS3_TAKE_HOME
    assert txt.startswith("PROPOSED (for ruling):") and "4, 7, 2 and 5 of 10" in txt and "8 of 10 seeds at 0.5 sigma (PASS) and 7 of 10 at sigma (FAIL)" in txt
    assert "97 of 225" in txt and "203 needed" in txt and "NOT EVALUABLE" in txt


def test_a_broken_count_or_a_changed_status_or_a_changed_verdict_stops_the_build():
    raw = FG.load_FS3()
    bad = json.loads(json.dumps(raw["ms10"]))
    bad["N_sweep"]["by_N"]["3000"]["surge_seeds"] += 1
    with pytest.raises(FG.DataError, match="surge-class counts disagree"):
        FG.prepare_FS3({**raw, "ms10": bad})
    bad = json.loads(json.dumps(raw["ms10"]))
    bad["rb8"]["verdict"] = "PASS"
    with pytest.raises(FG.DataError, match="RB8 heterogeneity verdict"):
        FG.prepare_FS3({**raw, "ms10": bad})
    rows = [dict(r) for r in raw["a11"]]
    for r in rows:
        if r["check_id"] == "headline_class_kept_1.0_sigma":
            r["pass_or_fail"] = "PASS"
    with pytest.raises(FG.DataError, match="A11 table RB2 gate rows disagree"):
        FG.prepare_FS3({**raw, "a11": rows})
    ev = json.loads(json.dumps(raw["evaluators"]))
    ev["evaluators"]["rb2"]["beside"][2]["kept_primary"] += 1
    with pytest.raises(FG.DataError, match="kept_primary"):
        FG.prepare_FS3({**raw, "evaluators": ev})


def test_drawn_bars_points_lines_and_markers_equal_the_stored_values_exactly():
    import matplotlib.pyplot as plt
    d = FG.prepare_FS3(FG.load_FS3())
    fig = FG._draw_FS3(d, True)
    try:
        a = _ax(fig, "(a)")                                                         # stacked class bars: heights are the stored shares, summing to 1 per bar
        h = sorted(p.get_height() for p in a.patches)
        tot = {}
        for p in a.patches:
            tot[round(p.get_x() + p.get_width() / 2, 6)] = tot.get(round(p.get_x() + p.get_width() / 2, 6), 0.0) + p.get_height()
        assert len(tot) == 8 and all(abs(v - 1.0) < 1e-12 for v in tot.values())
        exp = sorted(float(c) / float(n) for cnt, n in zip(np.vstack([d["s9_count"], d["s9_ctrl_count"]]), np.concatenate([d["s9_seeds"], d["s9_ctrl_n"]])) for c in cnt if c > 0)
        assert h == exp                                                             # exact
        for title, lo, md, hi in (("(b)", d["s9_fpk_err_min"], d["s9_fpk_err_median"], d["s9_fpk_err_max"]),
                                  ("(c)", d["s9_onset_err_min"], d["s9_onset_err_median"], d["s9_onset_err_max"])):
            ax = _ax(fig, title)
            segs = [ln for ln in ax.get_lines() if len(ln.get_xdata()) == 2]
            pts = [ln for ln in ax.get_lines() if len(ln.get_xdata()) == 1]
            assert [list(ln.get_ydata()) for ln in segs] == [[float(x), float(y)] for x, y in zip(lo, hi)]    # exact: min to max
            assert [float(ln.get_ydata()[0]) for ln in pts] == [float(x) for x in md]                          # exact: medians
        e = _ax(fig, "(e)")
        assert len(e.patches) == int((d["noise_count"] > 0).sum())
        assert [t.get_text() for t in e.texts if t.get_fontweight() == "bold" and t.get_text().isdigit()] == [str(int(k)) for k in d["noise_kept"]]
        g = _ax(fig, "(g)")
        assert g.patches[0].get_height() == d["subgrid_agree"] and [ln.get_ydata()[0] for ln in g.get_lines()] == [d["subgrid_needed"]]
        dd = _ax(fig, "(d)")
        assert [ln.get_marker() for ln in dd.get_lines()][:9] == [FG.S.get(c).marker for row in d["shape_class"] for c in row]
        assert "NOT EVALUABLE" in dd.get_title(loc="left") and "FAILED" in g.get_title(loc="left")        # failures drawn, not dropped
    finally:
        plt.close(fig)


def test_layout_no_legend_covers_a_line_or_marker_or_text_and_no_text_leaves_the_canvas():
    """Layout check on the drawn artists (tests/figlayout.py; exact geometry in display pixels), plus: no text of an axes lies under that axes' legend."""
    import matplotlib.pyplot as plt
    from figlayout import clipped_texts, legend_line_hits
    d = FG.prepare_FS3(FG.load_FS3())
    fig = FG._draw_FS3(d, True)
    try:
        assert legend_line_hits(fig) == []
        assert clipped_texts(fig) == []
        fig.canvas.draw()
        rend = fig.canvas.get_renderer()
        for ax in fig.axes:
            lg = ax.get_legend()
            if lg is None:
                continue
            box = lg.get_window_extent(rend)
            for t in ax.texts:
                assert not t.get_window_extent(rend).overlaps(box), (ax.get_title(loc="left"), t.get_text())
            for p in ax.patches:
                assert not p.get_window_extent(rend).overlaps(box) or p.get_height() == 0, (ax.get_title(loc="left"), "patch under the legend")
    finally:
        plt.close(fig)


def test_build_hashes_and_params_agree_with_the_provenance(built):
    res, out = built
    prov = out / "FS3_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "FS3_params.csv", prov) == []
    assert (out / "FS3.pdf").stat().st_size > 0 and (out / "FS3.png").stat().st_size > 0
    rec = json.loads(prov.read_text(encoding="utf-8"))
    assert {i["path"].split("results/")[-1] for i in rec["inputs"]} == set(FG.FS3_INPUTS)


def test_caption_names_the_plotted_quantities_marks_the_proposals_and_has_no_provenance_hash(built):
    res, out = built
    caption = (out / "FS3_caption.txt").read_text(encoding="utf-8")
    assert caption.startswith("FS3. PROPOSED (for ruling):")
    assert "Claim limits: " + "; ".join(f"{i}: {CL[i][0]} ({', '.join(CL[i][1])})" for i in FG.FS3_CLAIM_LIMITS) + "." in caption and "PROPOSED for the reviewer's ruling" in caption
    assert "NOT EVALUABLE" in caption and "FAIL rows" in caption and "Panel (a)" in caption and "Panel (d)" in caption and "Panels (e) and (f)" in caption
    assert not re.search(r"[0-9a-f]{12,}", caption) and "hash" not in caption.lower() and not re.search(r"\bsha(256)?\b", caption.lower())
    assert "Provenance" not in caption and "FS3_" not in caption
