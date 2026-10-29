"""MS13 13j: tests of the eighth figure (F6, untagged draft). They read the stored results under results/ (git-ignored) and skip if those are absent.
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
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F6_INPUTS), reason="stored F6 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "F6"
    return FG.make_F6(out_dir=out), out


def _ax(fig, prefix):
    hits = [a for a in fig.axes if a.get_title(loc="left").startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step():
    a, b = FG.prepare_F6(FG.load_F6()), FG.prepare_F6(FG.load_F6())
    assert FG.drawn_data_sha256(a) == FG.drawn_data_sha256(b)                      # exact
    assert sorted(a) == sorted(b)
    for k in a:
        if isinstance(a[k], np.ndarray):
            np.testing.assert_allclose(a[k], b[k], rtol=1e-12, atol=0, equal_nan=True)
    c = dict(a)
    c["s6_onset_s"] = a["s6_onset_s"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(a)                      # the hash does see a changed value


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "F6_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.F6_CLAIM_LIMITS)                    # exact set equality
    assert "MS12-C1" in prov["claim_limits"]                                       # the section 5 table lists MS12-C1 for F1 to F6
    assert all(i in CL for i in FG.F6_CLAIM_LIMITS)                                # every printed label is defined once in the label table
    assert prov["draft"] is True and prov["figure_id"] == "F6" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]
    assert {t["path"].split("results/")[-1]: t["rows"] for t in prov["input_tables"]} == {FG.F6_INPUTS[0]: 1226, FG.F6_INPUTS[1]: 58, FG.F6_INPUTS[2]: 24, FG.F6_INPUTS[3]: 44}


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_F6():
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_F6.py", "fig_F6_for_test")
    assert all(e["kind"] == "file" for e in reg.INPUTS["F6"])
    assert {e["path"] for e in reg.INPUTS["F6"]} == set(script.DECLARED_INPUTS) == set(FG.F6_INPUTS)      # exact set equality
    assert len(FG.F6_INPUTS) == 7 and set(reg.TIMING["F6"]) <= {e["label"] for e in reg.INPUTS["F6"]}


def test_data_step_opens_only_paths_under_results_reads_no_series_and_the_script_opens_nothing_itself():
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        FG.prepare_F6(FG.load_F6())
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res = RES.resolve()
    for path, mode in opened:
        assert Path(path).resolve().is_relative_to(res), path                      # exact: every opened path is under results/
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)               # and none is opened for writing
        assert not str(path).endswith(".npz"), path                                # tables first: no series file is opened
    assert len(opened) >= len(FG.F6_INPUTS)
    tree = ast.parse((ROOT / "scripts" / "fig_F6.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_F6


def test_proposed_take_home_numbers_equal_the_stored_tables_exactly():
    d = FG.prepare_F6(FG.load_F6())
    assert d["label_primary"].tolist() == [[48, 0, 32, 0, 0, 8, 51, 1], [0, 0, 0, 0, 0, 16, 13, 0]]               # labels a to h, primary, map 1 and map 2
    assert d["label_primary"].sum(axis=0).tolist() == [48, 0, 32, 0, 0, 24, 64, 1]                                 # take-home: a 48, c 32, f 24, g 64, h 1
    assert d["map_nonsurge"].tolist() == [140, 29] and int(d["map_nonsurge"].sum()) == 169 and d["map_surge"].tolist() == [760, 296]
    assert d["label_any"].tolist() == [[48, 48, 32, 0, 0, 18, 70, 4], [0, 0, 0, 0, 0, 16, 13, 0]]
    assert set(d["nc1_mf_class"]) == {"D-none"} and len(d["nc1_mf_class"]) == 13 and d["nc1_cells_class"] == ["D-none"] * 5
    assert set(d["nc3_class"]) == {"D-none"} and set(d["nc2_I0_class"]) == {"D-tr"} and set(d["nc2_I1_class"]) == {"D-tr"} and len(d["nc2_I1_class"]) == 13
    assert (d["nc1_net_class"], d["nc1_net_expected"], d["nc1_net_as_expected"]) == ("S+", "NS", False) and d["g7_status"].startswith("not passed")
    assert d["nc1_modeN_count"][:, 1].tolist() == [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 2]                          # S-rel seeds per T_ramp in the NC1 mode-N records
    assert d["s6_n_prereg"] == 20 and d["s6_prereg_all_Dtr"] is True and all(c == ["D-tr"] * 4 for c in d["s6_class"])
    assert d["s6_onset_s"][0].tolist() == [8.838, 15.377, 43.386, 98.343] and d["rb7_rows"] == 0 and [r["rb_id"] for r in d["strip"]] == ["G7"]
    txt = FG.F6_TAKE_HOME
    assert txt.startswith("PROPOSED (for ruling):") and "a 48, c 32, f 24, g 64, h 1" in txt and "13 of 13" in txt and "G7 is NOT PASSED" in txt and "All 20 pre-registered S6 rows" in txt


def test_a_labelled_surge_cell_or_a_changed_class_or_a_changed_gate_stops_the_build():
    raw = FG.load_F6()
    a9 = raw["a9"].copy()
    i = a9.index[(a9["map"].astype(str) == "1") & (a9["class"] == "D-tr")][0]
    a9.loc[i, "failure_label"] = "a"
    with pytest.raises(FG.DataError, match="surge-class cell carries a failure label"):
        FG.prepare_F6({**raw, "a9": a9})
    a10 = raw["a10"].copy()
    j = a10.index[(a10["control"] == "NC1") & (a10["row_type"] == "network_run")][0]
    a10.loc[j, "class"] = "NS"
    with pytest.raises(FG.DataError, match="NC1 network run"):
        FG.prepare_F6({**raw, "a10": a10})
    rows = [dict(r) for r in raw["a11"]]
    for r in rows:
        if r["rb_id"] == "G7":
            r["pass_or_fail"] = "PASS"
    with pytest.raises(FG.DataError, match="G7 row is not FAIL"):
        FG.prepare_F6({**raw, "a11": rows})
    s6 = raw["s6"].copy()
    s6 = s6[~((s6["family"] == "S6_P4a") & (s6["T_ramp_s"] == 300.0))]
    with pytest.raises(FG.DataError, match="T_ramp values"):
        FG.prepare_F6({**raw, "s6": s6})


def test_drawn_bars_points_lines_and_markers_equal_the_stored_values_exactly():
    import matplotlib.pyplot as plt
    d = FG.prepare_F6(FG.load_F6())
    fig = FG._draw_F6(d, True)
    try:
        a = _ax(fig, "(a)")
        h = [p.get_height() for p in a.patches]                                      # order of drawing: map 1 primary, map 2 primary, map 1 any, map 2 any
        assert h == [float(x) for x in np.concatenate([d["label_primary"][0], d["label_primary"][1], d["label_any"][0], d["label_any"][1]])]      # exact
        b = _ax(fig, "(b)")
        marks = [ln.get_marker() for ln in b.get_lines()]
        exp = []
        for i, cls in enumerate((d["nc1_mf_class"], None, d["nc2_I0_class"], d["nc2_I1_class"], d["nc3_class"])):
            for j in range(13):
                c = FG.FS3_CLASSES[int(np.argmax(d["nc1_modeN_count"][j]))] if cls is None else cls[j]
                exp.append(FG.S.get(c).marker)
        assert marks == exp                                                         # exact: one marker per stored class
        for title, key in (("(d)", "s6_onset_s"), ("(e)", "s6_f_pk_hz")):
            ax = _ax(fig, title)
            assert [list(ln.get_ydata()) for ln in ax.get_lines()] == [[float(x) for x in row] for row in d[key]]
            assert [list(ln.get_xdata()) for ln in ax.get_lines()] == [list(d["s6_T"])] * 6
        c_ = _ax(fig, "(c)")
        assert "NOT PASSED" in " ".join(t.get_text() for t in c_.texts) and "(c)" in c_.get_title(loc="left")     # the failure is drawn, not dropped
    finally:
        plt.close(fig)


def test_layout_no_legend_covers_a_line_or_marker_or_text_and_no_text_leaves_the_canvas():
    """Layout check on the drawn artists (tests/figlayout.py; exact geometry in display pixels), plus: no text of an axes lies under that axes' legend."""
    import matplotlib.pyplot as plt
    from figlayout import clipped_texts, legend_line_hits
    d = FG.prepare_F6(FG.load_F6())
    fig = FG._draw_F6(d, True)
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
                assert p.get_height() == 0 or not p.get_window_extent(rend).overlaps(box), (ax.get_title(loc="left"), "patch under the legend")
    finally:
        plt.close(fig)


def test_build_hashes_and_params_agree_with_the_provenance(built):
    res, out = built
    prov = out / "F6_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "F6_params.csv", prov) == []
    assert (out / "F6.pdf").stat().st_size > 0 and (out / "F6.png").stat().st_size > 0
    rec = json.loads(prov.read_text(encoding="utf-8"))
    assert {i["path"].split("results/")[-1] for i in rec["inputs"]} == set(FG.F6_INPUTS)


def test_caption_names_the_plotted_quantities_marks_the_proposals_and_has_no_provenance_hash(built):
    res, out = built
    caption = (out / "F6_caption.txt").read_text(encoding="utf-8")
    assert caption.startswith("F6. PROPOSED (for ruling):")
    na = FG.F6_NOT_APPLICABLE                                                          # 13o (DL-495 T7, R5): a limit can be carried as not applicable
    assert "Claim limits: " + "; ".join(f"{i}: {CL[i][0]} ({', '.join(CL[i][1])})" + (f", not applicable here because {na[i]}" if i in na else "") for i in FG.F6_CLAIM_LIMITS) + "." in caption and "PROPOSED for the reviewer's ruling" in caption
    assert "NOT PASSED" in caption and "Panel (a)" in caption and "Panel (b)" in caption and "Panels (d) and (e)" in caption and "same weight" in caption
    assert not re.search(r"[0-9a-f]{12,}", caption) and "hash" not in caption.lower() and not re.search(r"\bsha(256)?\b", caption.lower())
    assert "Provenance" not in caption and "F6_" not in caption
