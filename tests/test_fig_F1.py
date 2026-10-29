"""MS13 13l: tests of the tenth figure (F1, untagged draft). They read the stored results under results/ (git-ignored) and skip if those are absent.
Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (SHA-256, set equality, counts, stored values read back from the drawn artists,
the computed spectrogram against the frozen routine's own output, display-pixel geometry) except the stored classifier onsets re-derived by the frozen classifier from the
stored v (abs 1e-9 s) and the rounded take-home numbers (the printed digits)."""
import ast
import importlib.util
import inspect
import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge.analysis import surge_metrics as M
from mprsurge.plotting import figprov as F
from mprsurge.plotting import figures as FG
from mprsurge.plotting import style as S
from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS as CL

ROOT = C.repo_root()
RES = ROOT / "results"
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F1_INPUTS) or not (RES / (FG.F1_MF_RECORD + ".npz")).is_file(),
                                reason="stored F1 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def crit():
    return F.K.load_frozen_criteria()[0]


@pytest.fixture(scope="module")
def raw():
    return FG.load_F1()


@pytest.fixture(scope="module")
def data(raw, crit):
    return FG.prepare_F1(raw, crit)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "F1"
    return FG.make_F1(out_dir=out), out


def _ax(fig, prefix):
    hits = [a for a in fig.axes if a.get_title(loc="left").startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step(crit):
    a, b = FG.prepare_F1(FG.load_F1(), crit), FG.prepare_F1(FG.load_F1(), crit)
    assert FG.drawn_data_sha256(a) == FG.drawn_data_sha256(b)                      # exact
    assert sorted(a) == sorted(b)
    c = dict(a)
    c["spec_mf_db"] = a["spec_mf_db"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(a)                      # the hash does see a changed value


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "F1_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.F1_CLAIM_LIMITS)                    # exact set equality
    assert {"MS12-C1", "G4-C1", "G4-C2", "G4-C3", "MS11-C2"} <= set(prov["claim_limits"])
    assert all(i in CL for i in FG.F1_CLAIM_LIMITS)
    assert prov["draft"] is True and prov["figure_id"] == "F1" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]
    assert {t["path"].split("results/")[-1]: t["rows"] for t in prov["input_tables"]} == {FG.F1_INPUTS[2]: 44}


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_F1():
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_F1.py", "fig_F1_for_test")
    files = [e["path"] for e in reg.INPUTS["F1"] if e["kind"] == "file" and not e["path"].startswith("configs/")]
    recs = [e for e in reg.INPUTS["F1"] if e["kind"] == "rec"]
    assert set(files) == set(script.DECLARED_INPUTS) == set(FG.F1_INPUTS)           # exact set equality
    assert {e["pattern"]: e["expected"] for e in recs} == {FG.F1_MF_RECORD + ".json": 1, FG.F1_NET_DIR + "/*.json": FG.F1_NET_COUNT}
    assert [e["path"] for e in reg.INPUTS["F1"] if e["kind"] == "file" and e["path"].startswith("configs/")] == ["configs/robustness_criteria.yaml"]


def test_data_step_opens_only_paths_under_results_and_the_script_opens_nothing_itself(crit):
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        FG.prepare_F1(FG.load_F1(), crit)
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res = RES.resolve()
    for path, mode in opened:
        assert Path(path).resolve().is_relative_to(res), path                      # exact: every opened path is under results/
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)               # and none is opened for writing
    assert len(opened) >= len(FG.F1_INPUTS) + 1 + FG.F1_NET_COUNT + 1 + 3          # inputs, mean-field json and npz, 6 network json, 3 network npz
    tree = ast.parse((ROOT / "scripts" / "fig_F1.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_F1


def test_envelope_extremes_equal_the_stored_extremes_exactly(raw, data):
    for name, arr in [("mf", raw["mf"])] + [(f"net{i}", n["npz"]) for i, n in enumerate(raw["net"])]:
        for q in ("r", "v"):
            assert data[f"{name}_{q}_lo"].min() == arr[q].min() and data[f"{name}_{q}_hi"].max() == arr[q].max()          # exact: whole-series extremes
            assert data[f"{name}_{q}_min"] == float(arr[q].min()) and data[f"{name}_{q}_max"] == float(arr[q].max())
    y = raw["mf"]["r"]
    edges = np.linspace(0, y.size, FG.F1_COLUMNS + 1).astype(np.int64)
    for i in (0, 1, 650, 1298, 1299):                                              # exact: block extremes of the first, middle and last blocks
        blk = y[edges[i]:edges[i + 1]]
        assert data["mf_r_lo"][i] == blk.min() and data["mf_r_hi"][i] == blk.max()
    assert data["mf_n"] == y.size and sum(edges[1:] - edges[:-1]) == y.size        # every sample belongs to exactly one block
    with pytest.raises(FG.DataError, match="blocks"):
        FG.envelope_minmax(np.arange(5.0), np.arange(5.0), 10)


def test_spectrograms_equal_the_frozen_routines_own_output_for_the_stored_v(raw, data):
    sp = data["spec_settings"]
    W, step = M.window_for_ramp(120.0)
    assert (sp["window_s"], sp["step_s"], sp["fs_hz"]) == (W, step, 1000.0) == (2.0, 1.0, 1000.0)
    assert sp["taper"] == "hann" and sp["band_primary_hz"] == [25.0, 100.0] and sp["total_band_hz"] == [1.0, 150.0] and sp["detrend"] == "linear"
    for name, v in (("mf", raw["mf"]["v"]), ("net0", raw["net"][0]["npz"]["v"])):
        tc, f, S_ = M.spectrogram_v(v, 1000.0, W, step)
        sel = f <= 150.0
        np.testing.assert_array_equal(data[f"spec_{name}_db"], 10.0 * np.log10(S_[sel]))      # exact: the same routine, the same display transform
        np.testing.assert_array_equal(data["spec_t_s"], tc)
        np.testing.assert_array_equal(data["spec_f_hz"], f[sel])


def test_stored_classes_and_onsets_in_the_take_home_equal_the_stored_evaluation_and_the_frozen_classifier(raw, data):
    th = FG.F1_TAKE_HOME
    assert data["ref_class"] == "D-tr" and data["ref_onset_s"] == 58.698 and data["ref_f_pk_hz"] == 49.0 and "58.698 s" in th and "49.0 Hz" in th        # exact
    assert data["cls120"] == ["S-sus"] * 3 and data["onset120_s"] == [12.0] * 3 and "classifier onset 12.0 s" in th
    assert round(data["ref_onset_s"] - data["onset120_s"][0], 1) == 46.7 and "46.7 s" in th                                       # the printed digits
    assert data["fpk120_hz"] == [49.0, 48.5, 49.0] and "49.0, 48.5 and 49.0 Hz" in th
    assert data["cls10"] == ["S-abs", "S-rel", "S-sus"] and "S-abs, S-rel and S-sus" in th
    assert data["ctrl120"] == {"S-sus": 3} and data["ctrl10"] == {"S-abs": 2, "S-rel": 1} and "S-sus 3 of 3" in th and "S-abs 2 and S-rel 1" in th
    assert data["g4_triggered"] is True and data["rb1_verdict"] == "FAIL"
    assert [r["check_id"] for r in data["strip"]] == ["headline_10s", "headline_120s", "cells_30s", "overall", "gate"] and all(r["status"] == "FAIL" for r in data["strip"])
    from mprsurge.analysis import a7 as A7
    from mprsurge.analysis import ms9_classify as MCL
    thr = A7.frozen_inputs()[0]["threshold"]
    for mode, v, t_on, want_cls, want_onset in (("D", raw["mf"]["v"], 5.0, "D-tr", data["ref_onset_s"]), ("N", raw["net"][0]["npz"]["v"], 5.0, "S-sus", data["onset120_s"][0])):
        res, err = MCL.classify_array(mode, v, 1000.0, t_on, 120.0, thr)
        assert err == "" and res.cls == want_cls and abs(res.episode.onset_s - want_onset) < 1e-9        # the frozen classifier on the stored v gives the stored class and onset


def test_a_changed_record_class_or_strip_row_stops_the_build(raw, crit):
    rows = [dict(r) for r in raw["a11"]]
    for r in rows:
        if r["rb_id"] == "RB1" and r["check_id"] == "headline_120s":
            r["pass_or_fail"] = "PASS"
    with pytest.raises(FG.DataError, match="not a FAIL row"):
        FG.prepare_F1({**raw, "a11": rows}, crit)
    ev = json.loads(json.dumps(raw["ev"]))
    ev["rb1_headline"]["120.0"]["seeds"][0]["name"] = "other"
    with pytest.raises(FG.DataError, match="does not match record"):
        FG.prepare_F1({**raw, "ev": ev}, crit)
    with pytest.raises(FG.DataError, match="3 seeds at 120 s"):
        FG.prepare_F1({**raw, "net": raw["net"][:2]}, crit)


def test_drawn_series_equal_the_stored_values_exactly(data):
    import matplotlib.pyplot as plt
    fig = FG._draw_F1(data, True)
    try:
        a = _ax(fig, "(a)")
        assert any(list(ln.get_ydata()) == [float(x) for x in data["path_eta"]] and list(ln.get_xdata()) == [float(x) for x in data["path_t_s"]] for ln in a.get_lines())      # exact
        b = _ax(fig, "(b)")
        assert any(list(ln.get_ydata()) == [float(x) for x in data["path_J"]] for ln in b.get_lines())
        for title, name, q in (("(c)", "mf", "r"), ("(e)", "mf", "v")):
            ys = [list(ln.get_ydata()) for ln in _ax(fig, title).get_lines()]
            assert [float(x) for x in data[f"{name}_{q}_lo"]] in ys and [float(x) for x in data[f"{name}_{q}_hi"]] in ys                                                      # exact: the envelope
        for title, q in (("(d)", "r"), ("(f)", "v")):
            ys = [list(ln.get_ydata()) for ln in _ax(fig, title).get_lines()]
            for i in range(3):
                assert [float(x) for x in data[f"net{i}_{q}_lo"]] in ys and [float(x) for x in data[f"net{i}_{q}_hi"]] in ys
        r = _ax(fig, "(i)")
        got = [ln for ln in r.get_lines() if len(ln.get_xdata()) == data["ras_t_s"].size][0]
        assert np.array_equal(got.get_xdata(), data["ras_t_s"]) and np.array_equal(got.get_ydata(), data["ras_row"])                                                         # exact: every stored spike
        for title, win in (("(j)", data["zoom_windows_s"][0]), ("(k)", data["zoom_windows_s"][1])):
            ln = [x for x in _ax(fig, title).get_lines()][0]
            m = (data["ras_t_s"] >= win[0]) & (data["ras_t_s"] <= win[1])
            assert np.array_equal(ln.get_xdata(), data["ras_t_s"][m]) and np.array_equal(ln.get_ydata(), data["ras_row"][m])
        g = _ax(fig, "(g)")
        assert any(np.array_equal(np.asarray(c.get_array()).ravel(), data["spec_mf_db"].ravel()) for c in g.collections)                                                       # exact: the computed spectrogram
    finally:
        plt.close(fig)


def test_layout_no_value_is_hidden_under_a_legend_or_text_and_no_text_leaves_the_canvas(data):
    import matplotlib.pyplot as plt
    from figlayout import clipped_texts, legend_line_hits
    from matplotlib.text import Text
    fig = FG._draw_F1(data, True)
    try:
        assert legend_line_hits(fig) == []
        assert clipped_texts(fig) == []
        fig.canvas.draw()
        rend = fig.canvas.get_renderer()
        for ax in fig.axes:
            boxes = [Text.get_window_extent(t, rend) for t in ax.texts if t.get_text()]
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


def test_no_literal_colour_hatch_or_point_size_in_the_f1_drawing_code():
    for fn in (FG._draw_F1, FG._f1_onset_marks, FG._f1_env):
        src = inspect.getsource(fn)
        assert not re.findall(r"#[0-9a-fA-F]{3,8}\b", src), fn.__name__                                  # exact: no hex colour literal
        assert not re.findall(r"hatch=[\"']", src) and not re.findall(r"\bms=[0-9]", src), fn.__name__
        assert not re.findall(r"marker=[\"'][^\"']", src), fn.__name__                                    # no marker literal: marks come from style.py
    assert S.SPECTROGRAM_CMAP and set(S.RASTER_MARKS) == {"full", "zoom"}


def test_build_hashes_and_params_agree_with_the_provenance(built):
    res, out = built
    prov = out / "F1_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "F1_params.csv", prov) == []
    assert (out / "F1.pdf").stat().st_size > 0 and (out / "F1.png").stat().st_size > 0
    rec = json.loads(prov.read_text(encoding="utf-8"))
    assert {i["path"].split("results/")[-1] for i in rec["inputs"]} == set(FG.F1_INPUTS) | set(FG.load_F1()["record_files"])
    assert rec["spectrogram"]["window_s"] == 2.0 and rec["spectrogram"]["taper"] == "hann"


def test_caption_has_the_spectrogram_settings_the_decimation_and_the_proposals_and_no_provenance_hash(built):
    res, out = built
    caption = (out / "F1_caption.txt").read_text(encoding="utf-8")
    assert caption.startswith("F1. PROPOSED (for ruling):")
    assert "Claim limits: " + "; ".join(f"{i}: {CL[i][0]} ({', '.join(CL[i][1])})" for i in FG.F1_CLAIM_LIMITS) + "." in caption and "PROPOSED for the reviewer's ruling" in caption
    assert "Spectrogram: " in caption and "window_s=2.0" in caption and "step_s=1.0" in caption and '"hann"' in caption and "band_primary_hz=[25.0, 100.0]" in caption
    for s in ("Panels (a) and (b)", "min-to-max envelope per pixel column", "Panels (g) and (h) are NOT stored", "frozen classifier routine", "G4-C3", "RB1 FAILED", "all three stored seeds",
              "N = 1e4", "not hidden", "2.176222"):
        assert s in caption, s
    assert not re.search(r"(?=[0-9a-f]*[a-f])[0-9a-f]{12,}", caption) and "hash" not in caption.lower() and not re.search(r"\bsha(256)?\b", caption.lower())
    assert "Provenance" not in caption and "F1_" not in caption
