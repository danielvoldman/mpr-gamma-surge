"""MS13 13k: tests of the ninth figure (F4, untagged draft). They read the stored results under results/ (git-ignored) and skip if those are absent.
Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (SHA-256, set equality, counts, exact stored values read back from the
drawn artists) except: the A7 headline against the A4 summary (1e-6, the stored values differ at 1e-9), the floor medians against the six digits quoted in DL-182 (abs 5e-7)
and row 9's array comparison (rel 1e-12, plan section 8 row 9)."""
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
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F4_INPUTS), reason="stored F4 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "F4"
    return FG.make_F4(out_dir=out), out


@pytest.fixture(scope="module")
def data():
    return FG.prepare_F4(FG.load_F4())


def _ax(fig, prefix):
    hits = [a for a in fig.axes if a.get_title(loc="left").startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step():
    a, b = FG.prepare_F4(FG.load_F4()), FG.prepare_F4(FG.load_F4())
    assert FG.drawn_data_sha256(a) == FG.drawn_data_sha256(b)                      # exact
    assert sorted(a) == sorted(b)
    for k in a:
        if isinstance(a[k], np.ndarray):
            np.testing.assert_allclose(a[k], b[k], rtol=1e-12, atol=0, equal_nan=True)
    c = dict(a)
    c["noise_delay_eta_cross"] = a["noise_delay_eta_cross"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(a)                      # the hash does see a changed value


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "F4_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.F4_CLAIM_LIMITS)                    # exact set equality
    assert {"MS12-C1", "G6-D2", "G6-D3"} <= set(prov["claim_limits"])
    assert all(i in CL for i in FG.F4_CLAIM_LIMITS)                                # every printed label is defined once in the label table
    assert prov["draft"] is True and prov["figure_id"] == "F4" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]
    assert {t["path"].split("results/")[-1]: t["rows"] for t in prov["input_tables"]} == {FG.F4_INPUTS[0]: 360, FG.F4_INPUTS[1]: 13, FG.F4_INPUTS[3]: 44}


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_F4():
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_F4.py", "fig_F4_for_test")
    files = [e for e in reg.INPUTS["F4"] if e["kind"] == "file"]
    recs = [e for e in reg.INPUTS["F4"] if e["kind"] == "rec"]
    assert {e["path"] for e in files} == set(script.DECLARED_INPUTS) == set(FG.F4_INPUTS)      # exact set equality
    assert {e["pattern"]: e["expected"] for e in recs} == {FG.F4_RECORD_DIRS["S5"] + "/*/*.json": FG.F4_RECORD_COUNTS["S5"],
                                                           FG.F4_RECORD_DIRS["S5_noise"] + "/*.json": FG.F4_RECORD_COUNTS["S5_noise"],
                                                           FG.F4_RECORD_DIRS["S13"] + "/*/*.json": FG.F4_RECORD_COUNTS["S13"],
                                                           FG.F4_RECORD_DIRS["A3"] + "/*.json": FG.F4_RECORD_COUNTS["A3"]}
    assert len(FG.F4_INPUTS) == 4 and reg.TIMING["F4"] == []
    raw = FG.load_F4()
    assert len(raw["record_files"]) == 373 and len(set(raw["record_files"])) == 373            # one record per A7 row and per A3 row


def test_data_step_opens_only_paths_under_results_reads_no_series_and_the_script_opens_nothing_itself():
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        FG.prepare_F4(FG.load_F4())
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res = RES.resolve()
    for path, mode in opened:
        assert Path(path).resolve().is_relative_to(res), path                      # exact: every opened path is under results/
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)               # and none is opened for writing
        assert not str(path).endswith(".npz"), path                                # tables first: no series file is opened
    assert len(opened) >= len(FG.F4_INPUTS) + 373
    tree = ast.parse((ROOT / "scripts" / "fig_F4.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_F4


def test_proposed_take_home_numbers_equal_the_stored_tables(data):
    d = data
    assert (d["n_in_range"], d["n_testable"], d["n_testable_within_one_step"]) == (9, 6, 0)                 # 0 of 6 testable in-range runs within one A4 step
    assert [round(float(x), 1) for x in d["testable_match_steps"]] == [4.4, 7.6, 12.7, 20.6, 25.1, 33.1]    # take-home: 33.1, 20.6, 12.7, 7.6, 4.4, 25.1 (sorted)
    assert (d["head_onset_cross_s"], d["head_radau_onset_cross_s"], d["head_radau_minus_default_ms"]) == (58.698, 58.879, 181.0)      # exact stored values
    assert round(d["head_t_pred_s"], 1) == 115.2 and d["floor_dt_identical"] is True                       # the four Heun rungs agree exactly
    np.testing.assert_allclose(d["floor_median_cross"], [-0.000760417, -0.0423229, -0.105060], rtol=0, atol=5e-7)      # DL-182 (six digits quoted)
    assert d["floor_median_cls"].tolist() == pytest.approx([-1.5, -1.5, -1.0917], abs=5e-5) and d["floor_sigma"].tolist() == [1.59e-09, 1.59e-06, 1.59e-03]
    med = np.median(d["noise_delay_eta_cross"], axis=1)
    assert (med[3:] < 0).all() and med[2] > 0 and med[1] < 0                                                # negative from T_ramp 5.62 s (index 3) on; 3.16 s is positive
    assert d["a3_ring_class"] == ["damped"] * 13 and round(float(d["a3_offset"][0]), 5) == 0.34575 and round(float(d["a3_offset"][-1]), 5) == 0.00343
    assert d["rb5_fail_rows"] == 0 and [(r["rb_id"], r["check_id"]) for r in d["strip"]] == list(FG.F4_STRIP) and all(r["status"] == "FAIL" for r in d["strip"])
    txt = FG.F4_TAKE_HOME
    for s in ("PROPOSED (for ruling):", "0 of 6", "58.698 s", "58.879 s", "181 ms", "-0.000760", "-0.0423", "-0.1051", "5.62 s", "0.346 to 0.0034", "RB3(b) DOES NOT MEET", "RB6 solver clause FAIL"):
        assert s in txt, s


def test_a_changed_headline_gate_or_strip_row_or_count_stops_the_build():
    raw = FG.load_F4()
    a7 = raw["a7"].copy()
    a7.loc[a7["family"] == "radau", "onset_cross_s"] = 58.698
    with pytest.raises(FG.DataError, match="Radau minus DOP853"):
        FG.prepare_F4({**raw, "a7": a7})
    rows = [dict(r) for r in raw["a11"]]
    for r in rows:
        if r["rb_id"] == "RB3" and r["check_id"] == "b_classifier_onset":
            r["pass_or_fail"] = "PASS"
    with pytest.raises(FG.DataError, match="not a FAIL row"):
        FG.prepare_F4({**raw, "a11": rows})
    with pytest.raises(FG.DataError, match="A7 table"):
        FG.prepare_F4({**raw, "a7": raw["a7"].iloc[:-1]})
    eps = dict(raw["eps"])
    eps.pop(next(iter(eps)))
    with pytest.raises(FG.DataError, match="without a run record"):
        FG.prepare_F4({**raw, "eps": eps})
    a3 = raw["a3"].copy()
    a3.loc[a3.index[0], "status"] = "failed"
    with pytest.raises(FG.DataError, match="A3 table"):
        FG.prepare_F4({**raw, "a3": a3})


def test_drawn_series_points_and_bars_equal_the_stored_values_exactly(data):
    import matplotlib.pyplot as plt
    d = data
    fig = FG._draw_F4(d, True)
    try:
        a = _ax(fig, "(a)")
        got = [ln for ln in a.get_lines() if ln.get_marker() == FG.S.get("P2").marker and ln.get_linestyle() == FG.S.get("P2").linestyle]
        assert any(list(ln.get_ydata()) == [float(x) for x in d["p2_linear_delay_eta_cross"]] and list(ln.get_xdata()) == [float(x) for x in d["p2_linear_eps"]] for ln in got)   # exact
        ys = {tuple(float(v) for v in ln.get_ydata()) for ln in a.get_lines()}
        for fam in ("p1_linear", "p1_sigmoid", "p5_linear", "p5_sigmoid", "p2_sigmoid"):
            assert tuple(float(v) for v in d[f"{fam}_delay_eta_cross"]) in {tuple(v if v == v else float("nan") for v in t) for t in ys} or fam == "p2_sigmoid"   # NaN != NaN
        i = _ax(fig, "(i)")
        got = sorted(float(v) for ln in i.get_lines() for v in ln.get_ydata())
        exp = sorted([float(v) for v in d["floor_delay_cross"].ravel()] + [float(v) for v in d["floor_median_cross"]])
        assert got == exp                                                           # exact: 120 floor values and 3 medians, nothing else
        k = _ax(fig, "(k)")
        assert [float(v) for v in k.get_lines()[0].get_ydata()] == [float(v) for v in d["a3_offset"]]
        h = _ax(fig, "(h)")
        segs = [ln for ln in h.get_lines() if len(ln.get_xdata()) == 2 and ln.get_linewidth() == 3.0]
        assert [list(ln.get_ydata()) for ln in segs] == [[float(np.nanmin(c)), float(np.nanmax(c))] for c in d["noise_delay_eta_cross"]]      # exact: stored min to max
        assert "RB2 FAIL" in h.get_title(loc="left") and "FAIL" in " ".join(t.get_text() for t in fig.axes[-1].texts)       # failures drawn, not dropped
    finally:
        plt.close(fig)


def test_layout_no_value_is_hidden_under_a_legend_or_text_and_no_text_leaves_the_canvas(data):
    """Display-pixel geometry of the drawn artists (tests/figlayout.py): no legend over a line or marker, no text outside the canvas, and no stored point of an axes lies
    under a text of that axes (the annotation and the in-axes note) or under the key legend."""
    import matplotlib.pyplot as plt
    from figlayout import clipped_texts, legend_line_hits
    from matplotlib.text import Text
    fig = FG._draw_F4(data, True)
    try:
        assert legend_line_hits(fig) == []
        assert clipped_texts(fig) == []
        fig.canvas.draw()
        rend = fig.canvas.get_renderer()
        for ax in fig.axes:
            boxes = [Text.get_window_extent(t, rend) for t in ax.texts if t.get_text()]                # the text itself: an annotation arrow is a line, not a cover
            lg = ax.get_legend()
            if lg is not None:
                boxes.append(lg.get_window_extent(rend))
            if not boxes:
                continue
            for ln in ax.get_lines():
                xy = ln.get_transform().transform(np.column_stack([np.asarray(ln.get_xdata(), float), np.asarray(ln.get_ydata(), float)]))
                xy = xy[np.isfinite(xy).all(axis=1)]
                for b in boxes:
                    inside = (xy[:, 0] >= b.x0) & (xy[:, 0] <= b.x1) & (xy[:, 1] >= b.y0) & (xy[:, 1] <= b.y1)
                    assert not inside.any(), (ax.get_title(loc="left"), "a drawn value lies under a text or legend")
    finally:
        plt.close(fig)


def test_build_hashes_and_params_agree_with_the_provenance(built):
    res, out = built
    prov = out / "F4_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "F4_params.csv", prov) == []
    assert (out / "F4.pdf").stat().st_size > 0 and (out / "F4.png").stat().st_size > 0
    rec = json.loads(prov.read_text(encoding="utf-8"))
    assert {i["path"].split("results/")[-1] for i in rec["inputs"]} == set(FG.F4_INPUTS) | set(FG.load_F4()["record_files"])


def test_caption_names_the_plotted_quantities_the_onset_reading_marks_the_proposals_and_has_no_provenance_hash(built):
    res, out = built
    caption = (out / "F4_caption.txt").read_text(encoding="utf-8")
    assert caption.startswith("F4. PROPOSED (for ruling):")
    assert "Claim limits: " + "; ".join(f"{i}: {CL[i][0]} ({', '.join(CL[i][1])})" for i in FG.F4_CLAIM_LIMITS) + "." in caption and "PROPOSED for the reviewer's ruling" in caption
    for s in ("Panel (a)", "raw first crossing", "classifier-episode onset", "G6-D1", "reported, not judged", "DL-163-D3", "Panels (b) to (e)", "Panels (i) and (j)",
              "A3 table", "A2 ring map", "RB6 solver clause FAIL", "signed", "peak power", "f_pk", "duration", "D-none"):
        assert s in caption, s
    assert not re.search(r"[0-9a-f]{12,}", caption) and "hash" not in caption.lower() and not re.search(r"\bsha(256)?\b", caption.lower())
    assert "Provenance" not in caption and "F4_" not in caption
