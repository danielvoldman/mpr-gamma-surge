"""MS13 13h: tests of the fourth figure (FS2, untagged draft). They read the stored results under results/ (git-ignored) and skip if those are absent.
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

ROOT = C.repo_root()
RES = ROOT / "results"
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.FS2_INPUTS), reason="stored FS2 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "FS2"
    return FG.make_FS2(out_dir=out), out


def _ax(fig, prefix):
    hits = [a for a in fig.axes if a.get_title().startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step():
    a, b = FG.prepare_FS2(FG.load_FS2()), FG.prepare_FS2(FG.load_FS2())
    assert FG.drawn_data_sha256(a) == FG.drawn_data_sha256(b)                      # exact
    assert sorted(a) == sorted(b)
    for k in a:
        if isinstance(a[k], np.ndarray):
            np.testing.assert_allclose(a[k], b[k], rtol=1e-12, atol=0, equal_nan=True)
    c = dict(a)
    c["hopf_a4_ms"] = a["hopf_a4_ms"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(a)                      # the hash does see a changed value


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "FS2_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.FS2_CLAIM_LIMITS) == {"MS11-C7"}    # exact set equality
    caption = (out / "FS2_caption.txt").read_text(encoding="utf-8")
    assert all(i in caption for i in FG.FS2_CLAIM_LIMITS)
    assert prov["draft"] is True and prov["figure_id"] == "FS2" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_FS2():
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_FS2.py", "fig_FS2_for_test")
    registry = set()
    for e in reg.INPUTS["FS2"]:
        if e["kind"] == "file":
            registry.add(e["path"])
        else:                                                                      # a record family: json and its npz, as the figure opens both
            for j in RES.glob(e["pattern"]):
                if not j.name.endswith((".dry.json", "_params.md")) and j.suffix == ".json":
                    registry |= {j.relative_to(RES).as_posix(), j.with_suffix(".npz").relative_to(RES).as_posix()}
    assert registry == set(script.DECLARED_INPUTS) == set(FG.FS2_INPUTS)           # exact set equality
    assert len(FG.FS2_INPUTS) == 32 and len(reg.INPUTS["FS2"]) == 15               # 10 entries as before, plus 5 added at 13h (A6 summary, A5 check, A4, A5 and A6 run records)


def test_data_step_opens_only_paths_under_results_and_the_script_opens_nothing_itself():
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        FG.prepare_FS2(FG.load_FS2())
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res = RES.resolve()
    for path, mode in opened:
        assert Path(path).resolve().is_relative_to(res), path                      # exact: every opened path is under results/
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)               # and none is opened for writing
    assert len(opened) >= len(FG.FS2_INPUTS)
    tree = ast.parse((ROOT / "scripts" / "fig_FS2.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_FS2


def test_proposed_take_home_numbers_agree_with_the_stored_arrays_to_the_printed_digits():
    d = FG.prepare_FS2(FG.load_FS2())
    assert d["hopf_a4_ms"] == pytest.approx(4.12, abs=5e-3) and d["hopf_a5_ms"] == pytest.approx(4.12, abs=5e-3)         # printed 4.12 ms
    assert d["k8_net_rel_diff"] * 100 == pytest.approx(-0.09, abs=5e-3)                                                  # printed 0.09 percent (stored -0.0861)
    assert d["k8_net_tol"] == 0.05 and d["k8_net_pass"] and d["k8_summary_pass"] and d["k7_summary_pass"]                # exact
    assert d["k9_ratio"].max() == pytest.approx(0.14531, abs=5e-6) and d["k9_on_edge"] == 0                              # printed 0.14531 (stored 0.145309)
    assert d["k11_max_dev"] == pytest.approx(7.1e-4, abs=5e-6)                                                           # printed 7.1e-4 (stored 7.099e-4)
    assert 100 * d["fit_s4_up_max_resid_frac"] == pytest.approx(2.42, abs=5e-3) and not d["fit_s4_up_resid_pass"]        # printed 2.42 percent, rule fails
    assert [100 * d[f"k10_rel_change_{t}"] for t in ("8.0", "20.0", "40.0")] == pytest.approx([13.4, 25.0, 42.2], abs=0.05)
    assert d["k10_j_limit"] == 0.1 and not d["k10_pass_all"]                                                             # exact
    assert FG.FS2_TAKE_HOME.startswith("PROPOSED (for ruling):")


def test_drawn_curves_points_and_traces_equal_the_stored_values_exactly():
    import matplotlib.pyplot as plt
    raw = FG.load_FS2()
    d = FG.prepare_FS2(raw)
    fig = FG._draw_FS2(d, True)
    try:
        a5 = raw["a5"]
        up = a5["ceni_direction_up"].astype(bool)
        la = _ax(fig, "(a)")
        curves = [ln for ln in la.get_lines() if len(ln.get_xdata()) == int(up.sum()) or len(ln.get_xdata()) == int((~up).sum())]
        assert np.array_equal(curves[0].get_xdata(), a5["ceni_tau_d_ms"][up]) and np.array_equal(curves[0].get_ydata(), a5["ceni_amplitude_v"][up])      # exact
        assert np.array_equal(curves[1].get_ydata(), a5["ceni_amplitude_v"][~up])
        pts = [ln for ln in la.get_lines() if ln.get_linestyle() == "None"][0]
        mf = raw["s3mf"]["cells"]["K7"]
        assert list(pts.get_xdata()) == [3.0, 4.95, 8.0] and list(pts.get_ydata()) == [mf[k]["v_ptp_mean"] for k in ("3.0", "4.95", "8.0")]            # exact
        lb = _ax(fig, "(b)")
        yy = [ln for ln in lb.get_lines() if ln.get_label().startswith("A5 cycle")][0]
        assert np.array_equal(yy.get_ydata(), a5["ceni_amplitude_v"][up] ** 2)
        for i, (title, key, n) in enumerate((("(c)", ("ceni", "3.0"), "ceni_3ms"), ("(d)", ("ceni", "4.95"), "ceni_4.95ms"), ("(e)", ("ceni", "8.0"), "ceni_8ms"),
                                             ("(f)", ("devalle", "5.0"), "devalle_5ms"), ("(g)", ("devalle", "50.0"), "devalle_50ms"))):
            ax = _ax(fig, title)
            lines = ax.get_lines()
            t, r = raw["mf"][key]["series"]["t_ms"], raw["mf"][key]["series"]["r"]
            sel = t >= t[-1] - FG.FS2_TRACE_MS - 1e-9
            assert np.array_equal(lines[0].get_xdata(), t[sel]) and np.array_equal(lines[0].get_ydata(), r[sel])                                      # exact: stored, no smoothing
            tn, rn = raw["net"][n]["series"]["t_ms"], raw["net"][n]["series"]["r"]
            seln = tn >= tn[-1] - FG.FS2_TRACE_MS - 1e-9
            assert np.array_equal(lines[1].get_ydata(), rn[seln])
        lh = _ax(fig, "(h)")
        ys = sorted(float(y) for ln in lh.get_lines() if ln.get_linestyle() == "None" for y in ln.get_ydata() if np.isfinite(y))
        stored = sorted(100 * float(raw["s3net"]["cells"][c]["diff"][q]) for c in raw["s3net"]["cells"] for q in ("f_rel_diff", "r_mean_rel_diff", "r_fit_ptp_rel_diff")
                        if raw["s3net"]["cells"][c]["diff"][q] is not None and np.isfinite(raw["s3net"]["cells"][c]["diff"][q]))
        assert ys == pytest.approx(stored, rel=1e-12, abs=0) and len(ys) == len(stored) == 14           # tolerance rel 1e-12 (the factor 100)
        li = _ax(fig, "(i)")
        assert np.array_equal(li.get_lines()[0].get_ydata(), raw["a4"]["k9_ratio"]) and np.array_equal(li.get_lines()[0].get_xdata(), raw["a4"]["k9_eta_bar"])
        lj = _ax(fig, "(j)")
        assert np.array_equal(lj.get_lines()[0].get_ydata(), raw["a4"]["k11_ratio"]) and np.array_equal(lj.get_lines()[0].get_xdata(), -raw["a4"]["k11_J_H"])
        lk = _ax(fig, "(k)")
        assert np.array_equal(lk.get_lines()[0].get_ydata(), raw["a4"]["k10_freq_hz"]) and np.array_equal(lk.get_lines()[0].get_xdata(), raw["a4"]["k10_tau_d_ms"])
        ll = _ax(fig, "(l)")
        jd = raw["a6"]["k10"]["J_dependence"]
        for ln, tau in zip(ll.get_lines(), ("8.0", "20.0", "40.0")):
            assert list(ln.get_xdata()) == jd[tau]["J"] and list(ln.get_ydata()) == jd[tau]["linear_freq_hz"]                                       # exact
    finally:
        plt.close(fig)


def test_failures_are_shown_in_the_figure_text_and_nothing_is_drawn_for_k4_net():
    import matplotlib.pyplot as plt
    d = FG.prepare_FS2(FG.load_FS2())
    fig = FG._draw_FS2(d, True)
    try:
        text = " ".join(" ".join(t.get_text() for a in fig.axes for t in a.texts).split())       # the status block is wrapped; compare on single spaces
        titles = " ".join(a.get_title() for a in fig.axes)
        assert "REPORTED FAILURE" in text and "FAIL (REPORTED FAILURE, DL-129)" in text and "not passed as worded" in text
        assert "K4-net: not run, M2 network coupling unsourced" in text and "REPORTED FAILURE" in titles and "NOT reproduced as worded" in titles
        assert "K4-net" not in titles
    finally:
        plt.close(fig)


def test_build_hashes_and_params_agree_with_the_provenance(built):
    res, out = built
    prov = out / "FS2_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "FS2_params.csv", prov) == []
    assert (out / "FS2.pdf").stat().st_size > 0 and (out / "FS2.png").stat().st_size > 0
    rec = json.loads(prov.read_text(encoding="utf-8"))
    assert {i["path"].split("results/")[-1] for i in rec["inputs"]} == set(FG.FS2_INPUTS)


def test_caption_names_the_plotted_quantities_marks_the_proposals_and_has_no_provenance_hash(built):
    res, out = built
    caption = (out / "FS2_caption.txt").read_text(encoding="utf-8")
    assert caption.startswith("FS2. PROPOSED (for ruling):")
    from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS as CL                   # 13o (DL-495 T8, R2): the definitions are printed
    assert "Claim limits: MS11-C7: " + CL["MS11-C7"][0] + " (" + ", ".join(CL["MS11-C7"][1]) + ")." in caption and "PROPOSED for the reviewer's ruling" in caption
    assert "REPORTED FAILURE" in caption and "POST HOC" in caption and "no smoothing or interpolation" in caption.lower() and "UNVERIFIED" in caption
    assert "single-source" in caption or "single source" in caption
    assert not re.search(r"[0-9a-f]{12,}", caption) and "hash" not in caption.lower() and not re.search(r"\bsha(256)?\b", caption.lower())
    assert "Provenance" not in caption and "FS2_" not in caption


def test_layout_no_legend_covers_a_line_or_marker_and_the_k9_band_is_a_band_and_the_trace_key_exists():
    """13i layout review: display-space check on the drawn artists (tests/figlayout.py; exact geometry); the K9 band must cover less than half the axes height
    (its height is the plan's +-0.002, the stored values are drawn unchanged); panels (c) to (g) carry a key for the colours of their lines."""
    import matplotlib.pyplot as plt
    from figlayout import legend_line_hits
    d = FG.prepare_FS2(FG.load_FS2())
    fig = FG._draw_FS2(d, True)
    try:
        assert legend_line_hits(fig) == []
        from figlayout import clipped_texts
        assert clipped_texts(fig) == []                                      # no title, label or legend text leaves the figure canvas
        axi = _ax(fig, "(i)")
        lo, hi = axi.get_ylim()
        assert (2 * FG.FS2_K9[1]) / (hi - lo) < 0.5
        assert lo < FG.FS2_K9[0] - FG.FS2_K9[1] and hi > FG.FS2_K9[0] + FG.FS2_K9[1]
        keys = [a for a in fig.axes if a.get_legend() is not None and "mean field" in [t.get_text() for t in a.get_legend().get_texts()]]
        assert len(keys) == 1 and len(keys[0].get_legend().get_texts()) == 3
    finally:
        plt.close(fig)
