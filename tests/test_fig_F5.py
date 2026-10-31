"""MS13 13m: tests of the eleventh figure (F5, untagged draft). They read the stored results under results/ (git-ignored) and skip if those are absent.
Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (SHA-256, set equality, integer counts, stored values read back from the drawn artists,
recomputed per-seed values against the stored classes and the stored counts, minimum, median and maximum of ms10_eval.json, display-pixel geometry) except the rounded
percentages of the take-home (the printed digit, 0.05)."""
import ast
import copy
import importlib.util
import inspect
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
from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS as CL

ROOT = C.repo_root()
RES = ROOT / "results"
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F5_INPUTS) or not (RES / FG.F5_S9_DIR).is_dir(), reason="stored F5 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def raw():
    return FG.load_F5()


@pytest.fixture(scope="module")
def data(raw):
    return FG.prepare_F5(raw)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "F5"
    return FG.make_F5(out_dir=out), out


def _ax(fig, prefix):
    hits = [a for a in fig.axes if a.get_title(loc="left").startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step(raw, data):
    b = FG.prepare_F5(FG.load_F5())
    assert FG.drawn_data_sha256(data) == FG.drawn_data_sha256(b)                   # exact
    assert sorted(data) == sorted(b)
    c = dict(data)
    c["s9_f_pk_hz"] = data["s9_f_pk_hz"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(data)                   # the hash does see a changed value


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "F5_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.F5_CLAIM_LIMITS)                    # exact set equality
    assert {"MS12-C1", "MS9(e)-2", "G4-C1", "G4-C3", "MS11-C2", "MS11-C1"} <= set(prov["claim_limits"])
    assert all(i in CL for i in FG.F5_CLAIM_LIMITS) and len(FG.F5_CLAIM_LIMITS) == 20          # 13o (DL-497 T13): three plan labels added (DL-495)
    assert prov["draft"] is True and prov["figure_id"] == "F5" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]
    assert {t["path"].split("results/")[-1]: t["rows"] for t in prov["input_tables"]} == {FG.F5_INPUTS[0]: 1226, FG.F5_INPUTS[1]: 225, FG.F5_INPUTS[3]: 103, FG.F5_INPUTS[4]: 44}


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_F5(raw):
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_F5.py", "fig_F5_for_test")
    files = [e["path"] for e in reg.INPUTS["F5"] if e["kind"] == "file" and not e["path"].startswith("configs/")]
    recs = {e["pattern"]: e["expected"] for e in reg.INPUTS["F5"] if e["kind"] == "rec"}
    assert set(files) == set(script.DECLARED_INPUTS) == set(FG.F5_INPUTS)           # exact set equality
    assert [e["path"] for e in reg.INPUTS["F5"] if e["kind"] == "file" and e["path"].startswith("configs/")] == ["configs/robustness_criteria.yaml"]
    assert recs == {FG.F5_CELL_DIR + "/*.json": 12, FG.F5_S9_DIR + "/*.json": 40, FG.F5_CTRL_DIR + "/*.json": 12, "S8/mf/S8_mf_cells/*.json": 4, "S8/mf/S8_mf_head60/*.json": 1,
                    FG.F5_ORIGIN_RECORDS[0] + ".json": 1, FG.F5_ORIGIN_RECORDS[1] + ".json": 1}
    assert reg.TIMING["F5"] == []
    assert len(raw["record_files"]) == 12 + 2 * (40 + 12) + 2 * 7 and len(set(raw["record_files"])) == len(raw["record_files"])
    assert not [e for e in reg.INPUTS["F5"] if "S7" in e["pattern" if e["kind"] == "rec" else "path"]]         # no S7 series is read


def test_data_step_opens_only_paths_under_results_or_the_frozen_configs_and_the_script_opens_nothing_itself():
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        raw = FG.load_F5()
        FG.prepare_F5(raw)
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res, root = RES.resolve(), ROOT.resolve()
    allowed_cfg = [(root / p).resolve() for p in FG.F5_FROZEN_CONFIG_READS]
    interp = [Path(sys.prefix).resolve(), (root / "src").resolve(), Path(sys.base_prefix).resolve()]
    seen_results = set()
    for path, mode in opened:
        if path.startswith("<") or not Path(path).is_absolute() and not Path(path).exists():
            continue
        p = Path(path).resolve()
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)                # none is opened for writing
        if p.is_relative_to(res):
            seen_results.add(p)
        elif any(p.is_relative_to(a) for a in allowed_cfg):
            pass
        else:
            assert any(p.is_relative_to(i) for i in interp), path                    # exact: nothing else than the interpreter's own imports
    declared = {(RES / q).resolve() for q in FG.F5_INPUTS} | {f.resolve() for f in raw["record_files"]}
    assert declared <= seen_results                                                  # every declared input was opened (the S8 cell npz are not declared)
    assert not [p for p in seen_results if "S7" in p.parts]                          # exact: no S7 file
    assert seen_results - declared == set()                                          # and nothing under results/ that is not declared
    tree = ast.parse((ROOT / "scripts" / "fig_F5.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_F5


def test_take_home_numbers_equal_the_stored_tables(raw, data):
    th = FG.F5_TAKE_HOME
    assert (data["map1_n_surge"], data["map1_n_none"], data["map1_n"]) == (760, 140, 900)                        # exact integers
    assert (data["map2_n_surge"], data["map2_n_none"], data["map2_n"]) == (296, 29, 325)
    assert (data["d24_n_agree"], data["sub_n"], data["d24_n_agree_categories"], data["p1_n_agree"], data["d24_needed"]) == (97, 225, 118, 173, 203)
    assert (data["d24_n_tie"], data["d24_n_disagree"], data["p1_n_tie"], data["p1_n_disagree"]) == (24, 104, 16, 36)
    for s in ("760 of the 900", "D-none 140", "296 of the 325", "D-none 29", "97 of 225", "203", "118 of 225", "173 of 225", "3 of the 4 map cells", "0 of 14", "64 of 64", "S+ in 6 seeds", "NS in 1"):
        assert s in th, s
    for printed, got in (("84.4%", 100.0 * 760 / 900), ("43.1%", 100.0 * 97 / 225), ("76.9%", 100.0 * 173 / 225)):
        assert printed in th and abs(float(printed[:-1]) - got) <= 0.05              # the printed digit
    assert data["g5_triggered"] is False and data["g5_threshold_cells"] == 27.0 and data["cells_n_agree"] == 1 and data["cells_n_disagree"] == 3 and data["g4_triggered"] is True
    assert data["s9_stored_counts"][1].get("S+") == 6 and data["s9_stored_counts"][2].get("NS") == 1
    assert data["status"][0]["status"] == "PASS" and "0 of 14 changed" in data["status"][0]["value"] and "64 of 64 unchanged" in data["status"][0]["value"]
    assert [r["check_id"] for r in data["strip"]] == [k[1] for k in FG.F5_STRIP] and all(r["status"] == "FAIL" for r in data["strip"])


def test_the_four_network_cells_match_the_map_cells_and_the_stored_comparison(data):
    assert data["cell_i"].tolist() == [7, 22, 13, 24] and data["cell_j"].tolist() == [4, 10, 29, 26]
    assert data["cell_T_ramp_s"].tolist() == [30.0] * 4 and set(data["map1_class"].ravel()) == {"D-tr", "D-none"}
    assert data["cell_map_class"].tolist() == ["D-tr", "D-tr", "D-none", "D-none"] == data["cell_mf30_class"].tolist()
    assert data["cell_agree"].tolist() == [True, False, False, False]
    for k in range(4):                                                               # the symbol sits on the map-1 cell of the same (Delta, tau_d), to 1e-9
        assert abs(data["map1_Delta"][data["cell_i"][k]] - data["cell_Delta"][k]) < 1e-9 and abs(data["map1_tau_d_ms"][data["cell_j"][k]] - data["cell_tau_d_ms"][k]) < 1e-9
        assert data["map1_class"][data["cell_i"][k], data["cell_j"][k]] == data["cell_map_class"][k]
    assert data["cell_net_class"][0].tolist() == ["S-abs", "S-abs", "S-rel"]


def test_recomputed_per_seed_values_equal_the_stored_classes_and_the_stored_ranges_exactly(raw, data):
    tsv = {(r["list"], r["name"]): r["class"] for r in raw["tsv"]}
    for lst, key, arr in (("S9", "s9", data["s9_class"]), ("C2_S9", "ctrl", data["ctrl_class"])):
        for k, N in enumerate(FG.F5_N):
            rows = sorted([r for r in raw[key] if r["N"] == N], key=lambda r: r["seed"])
            assert [tsv[(lst, r["name"])] for r in rows] == arr[k].tolist()           # exact: recomputed class = stored class, per seed
    stored = raw["ev"]["N_sweep"]["by_N"]
    for m, _ in FG.F5_METRICS:
        for k, N in enumerate(FG.F5_N):
            x = data[f"s9_{m}"][k]
            ok = x[np.isfinite(x)]
            want = stored[str(N)]["metrics"][m]
            assert (ok.min(), float(np.median(ok)), ok.max()) == (want["min"], want["median"], want["max"])      # exact: at the stored digits
            assert data[f"stored_{m}"][k].tolist() == [want["min"], want["median"], want["max"]]
            assert len(ok) == want["n"] and x.size - len(ok) == want["n_undefined"]
    for k, N in enumerate(FG.F5_N):
        assert FG.Counter_(data["s9_class"][k].tolist()) == stored[str(N)]["classes"] and FG.Counter_(data["ctrl_class"][k].tolist()) == stored[str(N)]["controls"]["classes"]


def test_a_recomputed_value_that_differs_from_a_stored_one_stops_the_build(raw):
    ev = copy.deepcopy(raw["ev"])
    ev["N_sweep"]["by_N"]["1000"]["metrics"]["f_pk_hz"]["median"] += 0.5
    with pytest.raises(FG.DataError, match="stop rule"):
        FG.prepare_F5({**raw, "ev": ev})
    ev = copy.deepcopy(raw["ev"])
    ev["N_sweep"]["by_N"]["3000"]["classes"] = {"S+": 5, "S-sus": 3, "S-abs": 2}
    with pytest.raises(FG.DataError, match="stop rule"):
        FG.prepare_F5({**raw, "ev": ev})
    tsv = [dict(r) for r in raw["tsv"]]
    for r in tsv:
        if r["list"] == "S9" and r["N"] == "1000" and r["seed"] == "0":
            r["class"] = "NS"
    with pytest.raises(FG.DataError, match="stop rule"):
        FG.prepare_F5({**raw, "tsv": tsv})
    a11 = [dict(r) for r in raw["a11"]]
    for r in a11:
        if r["rb_id"] == "RB2" and r["check_id"] == "noisy_subgrid_agreement":
            r["pass_or_fail"] = "PASS"
    with pytest.raises(FG.DataError, match="not a FAIL row"):
        FG.prepare_F5({**raw, "a11": a11})


def test_drawn_artist_coordinates_equal_the_stored_values_exactly(data):
    import matplotlib.pyplot as plt
    fig = FG._draw_F5(data, True)
    try:
        a = _ax(fig, "(a)")
        mesh = a.collections[0]
        codes = np.vectorize({c: k for k, c in enumerate(FG.F5_MAP_CLASSES)}.get)(data["map1_class"]).astype(float)
        assert np.array_equal(np.asarray(mesh.get_array()).reshape(30, 30), codes)                                  # exact: every cell as stored
        marks = {tuple(ln.get_xdata()) + tuple(ln.get_ydata()) for ln in a.get_lines()}
        for c in FG.F5_MAP_CLASSES:
            ii, jj = np.nonzero(data["map1_class"] == c)
            assert tuple(jj.astype(float)) + tuple(ii.astype(float)) in marks
        for agree in (True, False):
            m = data["cell_agree"] == agree
            want = tuple(data["cell_j"][m].astype(float)) + tuple(data["cell_i"][m].astype(float))
            assert sum(1 for ln in a.get_lines() if tuple(ln.get_xdata()) + tuple(ln.get_ydata()) == want) == 2           # halo and symbol
        for title, key in (("(c)", "d24"), ("(d)", "p1")):
            ax = _ax(fig, title)
            z = np.asarray(ax.collections[0].get_array())
            z = np.ma.filled(z.reshape(30, 30), np.nan)
            assert np.array_equal(z[data["sub_i"], data["sub_j"]], data[f"{key}_state"].astype(float))              # exact: every subgrid cell as stored
            assert np.isnan(z).sum() == 900 - 225
        e = _ax(fig, "(e)")
        codes2 = np.vectorize({c: k for k, c in enumerate(FG.F5_MAP_CLASSES)}.get)(data["map2_class"]).astype(float)
        assert np.array_equal(np.asarray(e.collections[0].get_array()).reshape(25, 13), codes2)
        f = _ax(fig, "(f)")
        ycls = {c: k for k, c in enumerate(FG.F5_NET_CLASSES)}
        pts = {(float(ln.get_xdata()[0]), float(ln.get_ydata()[0])) for ln in f.get_lines() if len(ln.get_xdata()) == 1}
        for k in range(4):
            for s in range(10):
                assert (FG._f5_x(k, s, False), float(ycls[str(data["s9_class"][k, s])])) in pts
            for s in range(3):
                assert (FG._f5_x(k, s, True), float(ycls[str(data["ctrl_class"][k, s])])) in pts
        for col, (m, _lab) in enumerate(FG.F5_METRICS):
            ax = _ax(fig, "(" + "ghi"[col] + ")")
            pts = {(float(ln.get_xdata()[0]), float(ln.get_ydata()[0])) for ln in ax.get_lines() if len(ln.get_xdata()) == 1}
            for k in range(4):
                for s in range(10):
                    y = data[f"s9_{m}"][k, s]
                    assert (np.isnan(y)) or (FG._f5_x(k, s, False), float(y)) in pts                                    # exact: every recomputed point
                if m in FG.F5_CONTROL_METRICS:
                    for s in range(3):
                        y = data[f"ctrl_{m}"][k, s]
                        assert np.isnan(y) or (FG._f5_x(k, s, True), float(y)) in pts
            segs = np.concatenate([np.asarray(c.get_segments()).reshape(-1, 2, 2) for c in ax.collections if c.get_segments() and len(c.get_segments()[0]) == 2])
            for k in range(4):                                                                                           # stored min to max (vertical) and median (horizontal)
                lo, med, hi = data[f"stored_{m}"][k]
                assert any(np.allclose(s_, [[k * FG.F5_SLOT - 1.3, lo], [k * FG.F5_SLOT - 1.3, hi]], rtol=0, atol=0) for s_ in segs)
                assert any(np.allclose(s_[:, 1], [med, med], rtol=0, atol=0) for s_ in segs)
    finally:
        plt.close(fig)


def test_layout_no_value_is_hidden_under_a_legend_or_text_and_no_text_leaves_the_canvas(data):
    import matplotlib.pyplot as plt
    from figlayout import clipped_texts, legend_line_hits
    from matplotlib.text import Text
    fig = FG._draw_F5(data, True)
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


def test_no_literal_colour_hatch_marker_or_point_size_in_the_f5_drawing_code():
    for fn in (FG._draw_F5, FG._f5_map, FG._f5_n_axis):
        src = inspect.getsource(fn)
        assert not re.findall(r"#[0-9a-fA-F]{3,8}\b", src), fn.__name__                                  # exact: no hex colour literal
        assert not re.findall(r"hatch=[\"']", src) and not re.findall(r"\bms=[0-9]", src), fn.__name__
        assert not re.findall(r"marker=[\"'][^\"']", src), fn.__name__                                    # no marker literal: marks come from style.py
    assert set(S.F5_STATE_MARKS) == {"agree", "disagree", "tie"} and len(set(S.F5_STATE_MARKS.values())) == 3 and len(set(S.F5_COLOURS[k] for k in S.F5_STATE_MARKS)) == 3


def test_build_hashes_and_params_agree_with_the_provenance(built, raw):
    res, out = built
    prov = out / "F5_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "F5_params.csv", prov) == []
    assert (out / "F5.pdf").stat().st_size > 0 and (out / "F5.png").stat().st_size > 0
    rec = json.loads(prov.read_text(encoding="utf-8"))
    assert {i["path"].split("results/")[-1] for i in rec["inputs"]} == set(FG.F5_INPUTS) | {f.relative_to(RES).as_posix() for f in raw["record_files"]}


def test_caption_has_the_mode_d_statement_the_limits_and_no_provenance_hash(built):
    res, out = built
    caption = (out / "F5_caption.txt").read_text(encoding="utf-8")
    assert caption.startswith("F5. Mean field only; network disagrees at 3 of 4 cells; noisy subgrid 43.1 percent (203 needed)")
    na = FG.F5_NOT_APPLICABLE                                                          # 13o (DL-495 T6, R5): a limit can be carried as not applicable
    assert "Claim limits: " + "; ".join(f"{i}: {CL[i][0]} ({', '.join(CL[i][1])})" + (f", not applicable here because {na[i]}" if i in na else "") for i in FG.F5_CLAIM_LIMITS) + "." in caption and "PROPOSED" not in caption        # 13p (DL-501, R13): ruled, no PROPOSED
    for s in ("The map statements are for mode D", "no claim that the regime map is robust to noise", "D8 is undefined in mode N", "T_ramp 30 s", "T_ramp 120 s", "no claim that the two durations are equivalent",
              "post-hoc and feeds no gate", "FAILED", "recomputed from stored series with the frozen classifier", "G4-C3", "RB4 passed", "not drawn"):
        assert s in caption, s
    assert not re.search(r"(?=[0-9a-f]*[a-f])[0-9a-f]{12,}", caption) and "hash" not in caption.lower() and not re.search(r"\bsha(256)?\b", caption.lower())
    assert "Provenance" not in caption and "F5_" not in caption
