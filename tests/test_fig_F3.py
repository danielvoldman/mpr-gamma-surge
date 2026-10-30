"""MS13 13d, 13e, 13g: tests of the first figure (F3, untagged draft v3) and of plan 13a rows 9 to 12. They read the stored results under results/
(git-ignored) and skip if those are absent. Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (SHA-256, set
equality, exact messages, arrow end points against the stored config.path values) except row 9's array comparison (rel 1e-12, plan section 8 row 9), the
derived P4 end Delta (rel 1e-12) and the quoted maximum frequency (abs 0.05 Hz, 73.7 against the stored 73.692...). 13g: the drawn arrow and start-marker
coordinates are read from the figure artists and equal the stored values exactly (no tolerance); the colour-bar gap is bounded in figure fractions (< 0.08)."""
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
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F3_INPUTS), reason="stored F3 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "F3"
    return FG.make_F3(out_dir=out), out


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step():
    # data step run twice in one process (not the plotting): exact SHA-256 of the drawn data, and every array equal at rel 1e-12
    a, b = FG.prepare_F3(FG.load_F3()), FG.prepare_F3(FG.load_F3())
    assert FG.drawn_data_sha256(a) == FG.drawn_data_sha256(b)
    assert sorted(a) == sorted(b)
    for k in a:
        if isinstance(a[k], np.ndarray):
            np.testing.assert_allclose(a[k], b[k], rtol=1e-12, atol=0, equal_nan=True)
    c = dict(a)
    c["f_max_hz"] = a["f_max_hz"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(a)                  # the hash does see a changed value


def test_row10_make_FS6_is_refused_citing_ms12_c1_and_no_fig_FS6_script():
    with pytest.raises(F.FigureRefused, match="MS12-C1"):
        FG.make_FS6()
    assert not (ROOT / "scripts" / "fig_FS6.py").exists()


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "F3_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.F3_CLAIM_LIMITS) == {"MS11-C7", "MS12-C1", "MS11-C3", "RB9(b) FAIL (plan label)"}           # exact set equality (13o, DL-497 T12)
    caption = (out / "F3_caption.txt").read_text(encoding="utf-8")
    assert all(i in caption for i in FG.F3_CLAIM_LIMITS)
    assert caption.startswith("F3. RB9(b) FAILED (spectral against cycle frequency")           # the ruled take-home message (DL-453), no PROPOSED marker
    assert "PROPOSED" not in caption
    assert prov["draft"] is True and prov["figure_id"] == "F3" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_F3():
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_F3.py", "fig_F3_for_test")
    registry = {e["path"] for e in reg.INPUTS["F3"]}
    assert all(e["kind"] == "file" for e in reg.INPUTS["F3"])
    assert registry == set(script.DECLARED_INPUTS) == set(FG.F3_INPUTS)           # exact set equality
    assert len(FG.F3_INPUTS) == len(reg.INPUTS["F3"]) == 12                         # 6 stored analysis inputs and 6 path records (DL-447)


def test_data_step_opens_only_paths_under_results_and_the_script_opens_nothing_itself():
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        FG.prepare_F3(FG.load_F3())
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res = RES.resolve()
    for path, mode in opened:
        assert Path(path).resolve().is_relative_to(res), path                      # exact: every opened path is under results/
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)               # and none is opened for writing
    tree = ast.parse((ROOT / "scripts" / "fig_F3.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_F3


def test_proposed_take_home_numbers_agree_with_the_stored_a6_arrays():
    d = FG.prepare_F3(FG.load_F3())
    first = {D: float(d[f"D{D}_tau_d_ms"][d[f"D{D}_c25_count"] > 0][0]) for D in FG.DELTAS}
    assert first == {"0.05": 3.0, "0.1": 5.0, "0.3": 13.0}                         # DL-131: 25 Hz contour from tau_d 3, 5, 13 ms
    assert list(d["D0.3_tau_d_ms"][d["D0.3_c25_count"] > 0]) == [13.0, 22.0, 36.0]
    assert d["c100_total_crossings"] == 0
    assert d["f_max_hz"] == pytest.approx(73.7, abs=0.05)
    assert [(r["rb_id"], r["check_id"], r["status"]) for r in d["strip"]] == [("RB9", "b_spectral_vs_cycle_headline", "FAIL")]


def test_build_hashes_and_params_agree_with_the_provenance(built):
    res, out = built
    prov = out / "F3_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "F3_params.csv", prov) == []
    text = (out / "F3_nordlie.md").read_text(encoding="utf-8")
    conn = text.split("## Connectivity", 1)[1].split("## ", 1)[0]
    assert "model.J" in conn                                                       # J sits under Connectivity (13d fix)
    assert (out / "F3.pdf").stat().st_size > 0 and (out / "F3.png").stat().st_size > 0


PATH_KEYS = ("P1", "P2", "P3", "P4a", "P4b", "P5")


def test_arrow_end_points_equal_the_stored_config_path_values_exactly():
    d = FG.prepare_F3(FG.load_F3())
    assert set(FG.F3_PATH_RECORDS) == set(PATH_KEYS)
    for k, rel in FG.F3_PATH_RECORDS.items():
        rec = json.loads((RES / rel).read_text(encoding="utf-8"))
        p, m = rec["config"]["path"], rec["config"]["model"]
        assert p["name"] == FG.PATH_NAMES[k] and p["profile"] == "linear" and rec["status"] == "ok"
        for name in ("eta_start", "eta_peak", "eta_H", "T_ramp_s", "I_amp", "Delta_factor"):
            assert d[f"{k}_{name}"] == float(p[name])                              # exact
        assert d[f"{k}_tau_d_ms"] == float(m["tau_d_ms"]) and d[f"{k}_Delta"] == float(m["Delta"])
    assert d["P3_I_amp"] == 1.0                                                    # the default amplitude (DL-015), as ruled
    assert (d["P1_T_ramp_s"], d["P5_T_ramp_s"], d["P2_T_ramp_s"]) == (100.0, 100.0, 120.0)


def test_derived_p4_end_delta_equals_stored_delta_times_stored_factor_rel_1e12():
    d = FG.prepare_F3(FG.load_F3())
    for k in ("P4a", "P4b"):
        rec = json.loads((RES / FG.F3_PATH_RECORDS[k]).read_text(encoding="utf-8"))
        want = rec["config"]["model"]["Delta"] * rec["config"]["path"]["Delta_factor"]
        assert d[f"{k}_Delta_end_derived"] == pytest.approx(want, rel=1e-12, abs=0)
        z = np.load((RES / FG.F3_PATH_RECORDS[k]).with_suffix(".npz"))             # the stored trace agrees with the derived end value
        assert float(z["Delta"][-1]) == pytest.approx(want, rel=1e-12, abs=0)
        assert float(z["eta"][0]) == d[f"{k}_eta_start"] and float(z["eta"].max()) == d[f"{k}_eta_peak"]


def test_p5_legs_follow_from_the_stored_eta_trace_and_the_others_have_one_leg():
    d = FG.prepare_F3(FG.load_F3())
    for k in PATH_KEYS:
        z = np.load((RES / FG.F3_PATH_RECORDS[k]).with_suffix(".npz"))
        eta = z["eta"]
        returns = bool(eta[-1] < eta.max() - 1e-9)                                  # the stored eta comes back down
        assert d[f"{k}_legs"] == (2 if returns else 1), k
        assert d[f"{k}_eta_peak"] == float(eta.max()) and d[f"{k}_eta_start"] == float(eta[0])
    assert d["P5_legs"] == 2


def test_a4_curve_parameters_are_read_from_the_a4_record_and_the_100hz_note_from_the_arrays():
    raw = FG.load_F3()
    d = FG.prepare_F3(raw)
    m = raw["records"]["A4"]["config"]["model"]
    assert (d["a4_curve_Delta"], d["a4_curve_J"], d["a4_curve_tau_d_ms"]) == (m["Delta"], m["J"], m["tau_d_ms"]) == (0.3, -21.0, 5.0)
    for D in FG.DELTAS:
        note = FG.note_100hz(d, D)
        assert note == f"no 100 Hz contour in range, maximum {float(d[f'D{D}_po_f_hz'].max()):.1f} Hz"


def test_caption_has_the_frequency_type_sentence_and_no_provenance_hash(built):
    import re
    res, out = built
    caption = (out / "F3_caption.txt").read_text(encoding="utf-8")
    assert "limit-cycle frequency of the continuation (A6), not the classifier's spectral peak" in caption
    assert "panel (d) shows the Hopf curve only, because A6 stores no Delta slices" in caption
    assert "J ramp of P2 and P3 is not drawn" in caption and "derived" in caption and "the Nordlie table of F3" in caption and "F3_" not in caption      # 13o (DL-495 T4, R3)
    assert not re.search(r"[0-9a-f]{12,}", caption) and "hash" not in caption.lower() and not re.search(r"\bsha(256)?\b", caption.lower())
    assert "Provenance" not in caption
    assert "model.Delta=0.05, 0.1, 0.3, swept" in caption and "noise.sigma" not in caption          # only the slice and regime keys are listed


# ---- 13g: layout clean-up (v3)

def _fig_v3():
    import matplotlib.pyplot as plt
    d = FG.prepare_F3(FG.load_F3())
    return d, FG._draw_F3(d, True, FG.strip_lines(d)), plt


def _stored(k):
    rec = json.loads((RES / FG.F3_PATH_RECORDS[k]).read_text(encoding="utf-8"))
    return rec["config"]["path"], rec["config"]["model"]


def test_drawn_arrows_and_start_markers_equal_the_stored_values_exactly_in_data_coordinates():
    # exact (==, no tolerance): coordinates read back from the annotation and marker artists, against the stored run records read independently of prepare_F3
    d, fig, plt = _fig_v3()
    try:
        arrows, starts, axes_of = {}, {}, {}
        for ax in fig.axes:
            for a in ax.texts:
                if (a.get_gid() or "").startswith("arrow:"):
                    arrows[a.get_gid()[6:]] = a
                    axes_of[a.get_gid()[6:]] = ax
            for ln in ax.lines:
                if (ln.get_gid() or "").startswith("start:"):
                    starts[ln.get_gid()[6:]] = (ln, ax)
        legs = {"P1": 1, "P2": 1, "P3": 1, "P5": 2}
        want = {f"{pl}:{k}:{leg}" for pl in ("tau_d", "Delta", "strip") for k, n in legs.items() for leg in range(n)}
        want |= {"Delta:P4a:0", "Delta:P4b:0", "strip:P4a:0", "strip:P4b:0"}
        assert set(arrows) == want == set(starts)
        for gid, a in arrows.items():
            plane, k, leg = gid.split(":")
            p, m = _stored(k)
            e0, e1 = float(p["eta_start"]), float(p["eta_peak"])
            x0, x1 = (e0, e1) if leg == "0" else (e1, e0)
            assert a.xycoords == "data" and a.anncoords == "data"                         # no transform shift: nothing is offset
            if plane == "tau_d":
                y0 = y1 = float(m["tau_d_ms"])
            elif plane == "Delta":
                y0 = float(m["Delta"])
                y1 = float(m["Delta"]) * float(p["Delta_factor"]) if k in ("P4a", "P4b") else float(m["Delta"])
            else:
                y0 = y1 = float(list(FG.STRIP_ROWS).index((k, int(leg))))                # the strip row number is a label, x is the stored eta
            assert (a.xyann, a.xy) == ((x0, y0), (x1, y1)), gid
            ln, ax = starts[gid]
            assert list(ln.get_xdata()) == [x0] and list(ln.get_ydata()) == [y0], gid
            assert ln.get_transform() == ax.transData and ax is axes_of[gid]
    finally:
        plt.close(fig)


def test_a6_hopf_point_has_its_own_mark_and_colour_and_is_drawn_on_top_of_every_arrow():
    d, fig, plt = _fig_v3()
    try:
        hp, found = S.diagram_mark("hopf_point"), []
        for ax in fig.axes:
            for ln in ax.lines:
                if ln.get_gid() == "a6_hopf_point":
                    found.append((ax, ln))
        assert len(found) == 2                                                          # panel (c) and panel (d)
        assert sorted(float(ln.get_ydata()[0]) for _, ln in found) == sorted([d["headline_tau_d_ms"], d["headline_Delta"]])      # exact
        for ax, ln in found:
            assert list(ln.get_xdata()) == [d["headline_hopf_eta"]]                      # exact
            assert ln.get_marker() == hp.marker and ln.get_color() == hp.colour
            others = [o.get_zorder() for o in list(ax.texts) + list(ax.lines) if o is not ln and (o.get_gid() or "").startswith(("arrow:", "start:"))]
            assert others and ln.get_zorder() > max(others)                              # on top of every arrow and start marker
        path_colours = {S.get(k).colour.lower() for k in FG.PATH_ORDER}
        assert hp.colour.lower() not in path_colours and hp.marker not in {S.get(k).marker for k in FG.PATH_ORDER}      # not the P2 hexagon, not any path mark
    finally:
        plt.close(fig)


def test_25hz_mark_is_a_tall_bar_across_the_slice_line_not_the_old_horizontal_bar():
    m = S.contour_mark("25hz")
    assert m.marker != "_" and m.size >= 10.0 and m.width > 0.0                          # exact thresholds: the old mark was "_" at size 7
    d, fig, plt = _fig_v3()
    try:
        sizes = {ln.get_markersize() for ax in fig.axes for ln in ax.lines if ln.get_marker() == m.marker}
        assert sizes == {m.size}                                                           # the drawn marks carry the style size
    finally:
        plt.close(fig)


def test_colour_bar_sits_next_to_the_panels_gap_below_0_08_of_the_figure_width():
    # tolerance: the gap between the right edge of panel (c) and the colour bar is bounded at 0.08 of the figure width (v2 had about 0.30)
    d, fig, plt = _fig_v3()
    try:
        fig.canvas.draw()
        cax = [ax for ax in fig.axes if ax.get_ylabel() == "limit-cycle frequency (Hz)"]
        assert len(cax) == 1
        panel_c = [ax for ax in fig.axes if ax.get_title(loc="left").startswith("(c)")][0]                 # 13o (DL-495 T5, R4): titles are left-aligned
        gap = cax[0].get_position().x0 - panel_c.get_position().x1
        assert 0.0 < gap < 0.08, gap
    finally:
        plt.close(fig)


def test_caption_never_says_offset_and_states_the_shared_stored_position(built):
    res, out = built
    caption = (out / "F3_caption.txt").read_text(encoding="utf-8")
    assert not re.search(r"offset", caption, re.I)                                       # exact: the word does not occur
    assert "no shift is applied" in caption and "path strip" in caption and "rows are labels" in caption
    d = FG.prepare_F3(FG.load_F3())
    assert f"eta_bar {d['P1_eta_start']:.3f}" in caption and f"Delta {d['P1_Delta']:g}, tau_d {d['P1_tau_d_ms']:g} ms" in caption
    assert "P1, P2, P3 and P5 start at the same" in caption                               # the grouping is computed from the stored values
    assert "DRAFT v3" in FG.FOOTER
