"""MS13 13h: tests of the third figure (FS1, untagged draft). They read the stored results under results/ (git-ignored) and skip if those are absent.
Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (SHA-256, set equality, exact stored values read back from
the drawn artists) except row 9's array comparison (rel 1e-12, plan section 8 row 9) and the take-home numbers, each quoted to the digits the message
prints (stated per assertion)."""
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
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.FS1_INPUTS), reason="stored FS1 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "FS1"
    return FG.make_FS1(out_dir=out), out


def _axes_by_title(fig, prefix):
    hits = [ax for ax in fig.axes if ax.get_title().startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step():
    a, b = FG.prepare_FS1(FG.load_FS1()), FG.prepare_FS1(FG.load_FS1())
    assert FG.drawn_data_sha256(a) == FG.drawn_data_sha256(b)                      # exact
    assert sorted(a) == sorted(b)
    for k in a:
        if isinstance(a[k], np.ndarray):
            np.testing.assert_allclose(a[k], b[k], rtol=1e-12, atol=0, equal_nan=True)
    c = dict(a)
    c["tau_ms"] = a["tau_ms"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(a)                      # the hash does see a changed value


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "FS1_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.FS1_CLAIM_LIMITS) == {"MS11-C7"}    # exact set equality
    caption = (out / "FS1_caption.txt").read_text(encoding="utf-8")
    assert all(i in caption for i in FG.FS1_CLAIM_LIMITS)
    assert prov["draft"] is True and prov["figure_id"] == "FS1" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]
    assert prov["git"]["dirty"] in (True, False)


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_FS1():
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_FS1.py", "fig_FS1_for_test")
    registry = set()
    for e in reg.INPUTS["FS1"]:
        if e["kind"] == "file":
            registry.add(e["path"])
        else:                                                                      # a record family: json and its npz, as the figure opens both
            for j in RES.glob(e["pattern"]):
                if not j.name.endswith((".dry.json", "_params.md")) and j.suffix == ".json":
                    registry |= {j.relative_to(RES).as_posix(), j.with_suffix(".npz").relative_to(RES).as_posix()}
    assert registry == set(script.DECLARED_INPUTS) == set(FG.FS1_INPUTS)           # exact set equality
    assert len(FG.FS1_INPUTS) == 13 and len(reg.INPUTS["FS1"]) == 6                # 3 files and the S1 family as before, plus the A1 and A2 run records added at 13h


def test_data_step_opens_only_paths_under_results_and_the_script_opens_nothing_itself():
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        FG.prepare_FS1(FG.load_FS1())
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res = RES.resolve()
    for path, mode in opened:
        assert Path(path).resolve().is_relative_to(res), path                      # exact: every opened path is under results/
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)               # and none is opened for writing
    assert len(opened) >= len(FG.FS1_INPUTS)
    tree = ast.parse((ROOT / "scripts" / "fig_FS1.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_FS1


def test_proposed_take_home_numbers_agree_with_the_stored_arrays_to_the_printed_digits():
    d = FG.prepare_FS1(FG.load_FS1())
    assert (d["k1_pass_half"], d["k1_pass_base"], d["k1_n"]) == (20, 18, 20)                         # exact: 20 of 20 at half spacing, 18 of 20 at base spacing
    assert d["k3_labels"] == "saddle, stable_focus, stable_node" and d["k3_pass"] and (d["k_eta"], d["k_J"]) == (-5.0, 15.0)      # exact
    assert d["k4_rel_err_frequency"] == pytest.approx(2.1e-4, abs=5e-6)                              # printed 2.1e-4 (stored 2.128e-4)
    assert d["k4_rel_err_decay"] == pytest.approx(6.1e-3, abs=5e-5)                                  # printed 6.1e-3 (stored 6.087e-3)
    assert d["ring_n_nondamped"] == 0 and d["ring_n_focus"] == 25727                                 # exact: 0 of 25727
    assert d["ring_cyc_inG_max"] == pytest.approx(5.1, abs=0.05)                                     # printed 5.1 (stored 5.1004; DL-089 prints 5.10)
    assert np.array_equal(d["band_hz"], [25.0, 100.0])
    assert FG.FS1_TAKE_HOME.startswith("PROPOSED (for ruling):")


def test_drawn_maps_and_points_equal_the_stored_values_exactly():
    raw = FG.load_FS1()
    d = FG.prepare_FS1(raw)
    fig = FG._draw_FS1(d, True)
    a1, a2 = raw["a1"], raw["a2"]
    try:
        ax = _axes_by_title(fig, "(a)")
        mesh = [c for c in ax.collections if type(c).__name__ == "QuadMesh"][0]
        assert np.array_equal(np.asarray(mesh.get_array()).reshape(201, 241), a1["n_roots"].T.astype(float))     # exact: one cell per stored node
        lines = {ln.get_label(): ln for ln in ax.get_lines()}
        fx = [ln for ln in ax.get_lines() if ln.get_linestyle() == "-" and len(ln.get_xdata()) == 201]
        assert len(fx) == 2
        for ln, col in zip(fx, (0, 1)):
            assert np.array_equal(ln.get_xdata(), a1["halving_fold_eta_formula"][:, col], equal_nan=True)     # exact: stored fold positions
            assert np.array_equal(ln.get_ydata(), a1["halving_fold_J"])
        pts = [ln for ln in ax.get_lines() if ln.get_linestyle() == "None"]
        pos = sorted((float(ln.get_xdata()[0]), float(ln.get_ydata()[0])) for ln in pts)
        assert pos == sorted([(float(a1["cusp_r_eta_J"][1]), float(a1["cusp_r_eta_J"][2])), (-5.0, 15.0)])    # exact: stored cusp and the stored S1 point
        mb = [c for c in _axes_by_title(fig, "(b)").collections if type(c).__name__ == "QuadMesh"][0]
        stored_f = np.where(a2["ring_is_focus"].any(axis=2), np.where(a2["ring_is_focus"], a2["ring_freq_hz"], 0.0).sum(axis=2), np.nan).T
        assert np.array_equal(np.ma.filled(np.ma.masked_invalid(mb.get_array()).reshape(201, 241), np.nan), stored_f, equal_nan=True)       # exact
        mc = [c for c in _axes_by_title(fig, "(c)").collections if type(c).__name__ == "QuadMesh"][0]
        shown = np.ma.filled(np.ma.masked_invalid(mc.get_array()).reshape(201, 241), np.nan)
        cyc = np.where(a2["ring_is_focus"].any(axis=2), np.where(a2["ring_is_focus"], a2["ring_cycles_per_efold"], 0.0).sum(axis=2), np.nan).T
        inG = np.where(a2["ring_is_focus"].any(axis=2), np.where(a2["ring_is_focus"], a2["ring_in_G"].astype(float), 0.0).sum(axis=2), np.nan).T == 1.0
        assert np.array_equal(shown[inG], cyc[inG]) and np.isnan(shown[~inG]).all()                      # exact: stored cycles per e-fold, only where the ring is in the band
        assert int(inG.sum()) == int((a2["ring_in_G"] & a2["ring_is_focus"]).sum()) == 14793
        td = _axes_by_title(fig, "(d)")
        s4 = raw["series"]["S1_K4"][0]
        ln = [x for x in td.get_lines() if x.get_label().startswith("S1 K4")][0]
        assert np.array_equal(ln.get_xdata(), s4["t_ms"]) and np.array_equal(ln.get_ydata(), s4["r"])    # exact: the stored series, no smoothing
        hl = [x for x in td.get_lines() if x.get_label().startswith("focus r*")][0]
        assert hl.get_ydata()[0] == float(a2["k4_r_star"])
        vx = sorted(float(x.get_xdata()[0]) for x in td.get_lines() if x.get_label().startswith("fit window"))
        assert vx == [float(a2["k4_t_start_tau"]) * float(a2["tau_ms"]), float(a2["k4_t_end_tau"]) * float(a2["tau_ms"])]
        te = _axes_by_title(fig, "(e)")
        s5 = raw["series"]["S1_K5"][0]
        lr = [x for x in te.get_lines() if x.get_label().startswith("S1 K5")][0]
        assert np.array_equal(lr.get_xdata(), s5["t_ms"]) and np.array_equal(lr.get_ydata(), s5["r"])
        twin = [x for x in fig.axes if x is not te and x.get_shared_x_axes().joined(x, te)][0]
        assert np.array_equal(twin.get_lines()[0].get_ydata(), s5["I"])                                  # exact: the stored forcing
        texts = " ".join(t.get_text() for ax_ in fig.axes for t in ax_.texts)
        assert "K4-net: not run, M2 network coupling unsourced" in texts and "own reading, UNVERIFIED, deferred" in texts
        assert not [x for x in fig.axes if "K4-net" in x.get_title()]                                   # no K4-net panel and no K4-net data
    finally:
        import matplotlib.pyplot as plt
        plt.close(fig)


def test_a_later_copy_of_an_s1_record_that_differs_stops_the_build():
    raw = FG.load_FS1()
    raw["series"]["S1_K5"][1] = {**raw["series"]["S1_K5"][1], "r": raw["series"]["S1_K5"][1]["r"] + 1e-12}
    with pytest.raises(FG.DataError, match="later copy differs"):
        FG.prepare_FS1(raw)


def test_the_two_stored_copies_of_each_s1_run_have_equal_arrays_and_the_cited_one_is_drawn():
    raw = FG.load_FS1()
    for key in ("S1_K4", "S1_K5"):
        a, b = raw["series"][key]
        assert sorted(a) == sorted(b) and all(np.array_equal(a[k], b[k]) for k in a)                    # exact
    assert FG.FS1_RECORDS["S1_K4"].endswith("2bffa787ba51.json") and FG.FS1_RECORDS["S1_K5"].endswith("ee3bd60993e0.json")      # the records the A0 table cites
    cited = " ".join(r["source_results"] for r in raw["a0"]) if "source_results" in raw["a0"][0] else ""
    assert "S1_0000_2bffa787ba51" in cited and "S1_0000_ee3bd60993e0" in cited


def test_build_hashes_and_params_agree_with_the_provenance(built):
    res, out = built
    prov = out / "FS1_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "FS1_params.csv", prov) == []
    assert (out / "FS1.pdf").stat().st_size > 0 and (out / "FS1.png").stat().st_size > 0
    rec = json.loads(prov.read_text(encoding="utf-8"))
    assert {i["path"].split("results/")[-1] for i in rec["inputs"]} == set(FG.FS1_INPUTS)


def test_caption_names_the_plotted_quantities_marks_the_proposals_and_has_no_provenance_hash(built):
    res, out = built
    caption = (out / "FS1_caption.txt").read_text(encoding="utf-8")
    assert caption.startswith("FS1. PROPOSED (for ruling):")                       # take-home and claim limits are proposals until ruled
    assert "Claim limits: MS11-C7." in caption and "PROPOSED for the reviewer's ruling" in caption
    assert "root count" in caption and "ring map" in caption and "cycles per e-fold" in caption and "K4-net was not run" in caption
    assert "UNVERIFIED" in caption and "No crossing is drawn" in caption and "nothing here is a result for M3" in caption
    assert not re.search(r"[0-9a-f]{12,}", caption) and "hash" not in caption.lower() and not re.search(r"\bsha(256)?\b", caption.lower())
    assert "Provenance" not in caption and "FS1_" not in caption


def test_layout_no_legend_covers_a_line_and_the_k4_numbers_do_not_cross_the_fit_window_lines():
    """13i layout review: display-space check on the drawn artists (tests/figlayout.py; exact geometry). The legend of panel (a) covers map cells only (not tested: background)."""
    import matplotlib.pyplot as plt
    from figlayout import legend_line_hits, text_line_hits
    d = FG.prepare_FS1(FG.load_FS1())
    fig = FG._draw_FS1(d, True)
    try:
        assert legend_line_hits(fig) == []
        from figlayout import clipped_texts
        assert clipped_texts(fig) == []                                      # no title, label or legend text leaves the figure canvas
        axd = [a for a in fig.axes if a.get_title().startswith("(d)")][0]
        from figlayout import texts_below_axes
        assert texts_below_axes(fig, axd, "fit: omega") == []                # the number block lies inside the axes frame
        assert text_line_hits(fig, axd, "fit: omega") == []                  # the two dash-dot window lines and the trace are clear of the number block
        axe = [a for a in fig.axes if a.get_title().startswith("(e)")][0]
        assert axe.get_ylim()[1] > 1.5 * float(np.max(d["K5_r"]))             # headroom for the legend above the r peaks
    finally:
        plt.close(fig)
