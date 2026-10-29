"""MS13 13i: tests of the sixth figure (FS4, untagged draft). They read the stored results under results/ (git-ignored) and skip if those are absent.
Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (SHA-256, set equality, exact stored values read back from the drawn
artists) except row 9's array comparison (rel 1e-12, plan section 8 row 9) and the take-home numbers, each quoted to the digits the message prints (stated per
assertion)."""
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
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.FS4_INPUTS), reason="stored FS4 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "FS4"
    return FG.make_FS4(out_dir=out), out


def _ax(fig, prefix):
    hits = [a for a in fig.axes if a.get_title(loc="left").startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step():
    a, b = FG.prepare_FS4(FG.load_FS4()), FG.prepare_FS4(FG.load_FS4())
    assert FG.drawn_data_sha256(a) == FG.drawn_data_sha256(b)                      # exact
    assert sorted(a) == sorted(b)
    for k in a:
        if isinstance(a[k], np.ndarray):
            np.testing.assert_allclose(a[k], b[k], rtol=1e-12, atol=0, equal_nan=True)
    c = dict(a)
    c["head_radau_minus_default_ms"] = a["head_radau_minus_default_ms"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(a)                      # the hash does see a changed value


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "FS4_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.FS4_CLAIM_LIMITS)                   # exact set equality
    assert "MS12-C1" not in prov["claim_limits"]                                   # the section 5 table lists MS12-C1 for F1 to F6 and FS6 only
    caption = (out / "FS4_caption.txt").read_text(encoding="utf-8")
    assert all(i in caption for i in FG.FS4_CLAIM_LIMITS)
    assert prov["draft"] is True and prov["figure_id"] == "FS4" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]
    assert prov["git"]["dirty"] in (True, False)
    assert {t["path"].split("results/")[-1] for t in prov["input_tables"]} == {FG.FS4_INPUTS[0], FG.FS4_INPUTS[2]}      # table hash and row count are recorded
    assert {t["path"].split("results/")[-1]: t["rows"] for t in prov["input_tables"]}[FG.FS4_INPUTS[0]] == 360


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_FS4():
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_FS4.py", "fig_FS4_for_test")
    assert all(e["kind"] == "file" for e in reg.INPUTS["FS4"])
    assert {e["path"] for e in reg.INPUTS["FS4"]} == set(script.DECLARED_INPUTS) == set(FG.FS4_INPUTS)      # exact set equality
    assert len(FG.FS4_INPUTS) == 5 and set(reg.TIMING["FS4"]) <= {e["label"] for e in reg.INPUTS["FS4"]}     # the timing sample names registry labels


def test_data_step_opens_only_paths_under_results_reads_no_series_and_the_script_opens_nothing_itself():
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        FG.prepare_FS4(FG.load_FS4())
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res = RES.resolve()
    for path, mode in opened:
        assert Path(path).resolve().is_relative_to(res), path                      # exact: every opened path is under results/
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)               # and none is opened for writing
        assert not str(path).endswith(".npz"), path                                # tables first: no series file is opened
    assert len(opened) >= len(FG.FS4_INPUTS)
    tree = ast.parse((ROOT / "scripts" / "fig_FS4.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_FS4


def test_proposed_take_home_numbers_agree_with_the_stored_tables_to_the_printed_digits():
    d = FG.prepare_FS4(FG.load_FS4())
    assert list(d["head_onset_s"][:5]) == [58.698] * 5 and d["head_onset_s"][5] == 58.879                  # exact: stored onsets, DOP853 under every setting, Radau
    assert np.array_equal(d["head_onset_cross_s"], d["head_onset_s"])                                      # exact: both onset readings give the same onsets
    assert d["head_radau_minus_default_ms"] == pytest.approx(181.0, abs=1e-6) and set(d["head_class"]) == {"D-tr"}      # printed 181 ms; D-tr under all six
    assert np.all(d["ms11_onset_shift_s"] == 0.0) and {c for row in d["ms11_class"] for c in row} == {"D-tr"}            # exact: zero shift, D-tr at 10 s and 316.2278 s
    for L in (0, 1, 2):                                                                                     # DL-184: the delay is identical at the two Heun rungs, both readings
        for q in ("cross", "class"):
            a = d[f"floor_l{L}_{q}_delay"]
            assert np.array_equal(a[0], a[-1]) and np.array_equal(np.median(a, axis=1)[[0, -1]], np.median(a, axis=1)[[0, 0]])     # exact
    assert d["net_ce_n_pass"] == 0 and d["net_psd_n_pass"] == 2 and d["net_status"] == "FAIL"              # exact: 0 of 3 and 2 of 3
    rel1 = d["net_rel_change"][:, 0]
    assert float(rel1.min()) == pytest.approx(0.05, abs=5e-3) and float(rel1.max()) == pytest.approx(0.43, abs=5e-3)    # printed 5 to 43 percent (stored 5.0 and 42.9)
    assert d["net_dt"].tolist() == [1e-3, 5e-4, 2.5e-4, 1e-4] and d["net_f_pk_hz"].shape == (3, 4)
    assert FG.FS4_TAKE_HOME.startswith("PROPOSED (for ruling):")


def test_a_changed_headline_onset_or_a_broken_dt_chain_or_a_changed_status_stops_the_build():
    raw = FG.load_FS4()
    a7 = raw["a7"].copy()
    a7.loc[a7["family"] == "radau", "onset_s"] = 58.7
    raw["a7"] = a7
    with pytest.raises(FG.DataError, match="Radau minus default"):
        FG.prepare_FS4(raw)
    raw = FG.load_FS4()
    raw["evaluators"]["evaluators"]["rb6_network"]["ladder_info"][0]["f1_hz"] += 1.0
    with pytest.raises(FG.DataError, match="differs between two stored rows"):
        FG.prepare_FS4(raw)
    raw = FG.load_FS4()
    for r in raw["a11"]:
        if r["check_id"] == "network_fpk_halving_dt":
            r["pass_or_fail"] = "PASS"
    with pytest.raises(FG.DataError, match="network_fpk_halving_dt"):
        FG.prepare_FS4(raw)


def test_drawn_markers_points_lines_and_values_equal_the_stored_tables_exactly():
    import matplotlib.pyplot as plt
    d = FG.prepare_FS4(FG.load_FS4())
    fig = FG._draw_FS4(d, True)
    try:
        la = _ax(fig, "(a)")
        marks = [ln for ln in la.get_lines() if ln.get_linestyle() == "None"]
        xs = np.array([ln.get_xdata()[0] for ln in marks])
        assert np.array_equal(xs[0::2], d["head_onset_s"]) and np.array_equal(xs[1::2], d["head_onset_cross_s"])      # exact: stored onsets, both readings
        assert [ln.get_ydata()[0] for ln in marks[0::2]] == list(range(6))
        lc = _ax(fig, "(c) D43")
        pts = [ln for ln in lc.get_lines() if ln.get_linestyle() == "None"]
        assert len(pts) == 12 and np.array_equal(pts[0].get_ydata(), d["floor_l0_cross_delay"][0]) and np.array_equal(pts[4].get_ydata(), d["floor_l1_cross_delay"][0])   # exact
        assert np.array_equal(np.array([ln.get_xdata()[0] for ln in pts[:4]]), d["floor_dt"])
        lc2 = _ax(fig, "(c2)")
        assert np.array_equal([ln for ln in lc2.get_lines() if ln.get_linestyle() == "None"][8].get_ydata(), d["floor_l2_class_delay"][0])
        le = _ax(fig, "(e)")
        for s_, ln in enumerate([x for x in le.get_lines() if x.get_linestyle() != "None"]):
            assert np.array_equal(ln.get_ydata(), d["net_f_pk_hz"][s_]) and np.array_equal(ln.get_xdata(), d["net_dt"])                 # exact
        lf = _ax(fig, "(f)")
        for s_, ln in enumerate([x for x in lf.get_lines() if x.get_linestyle() == "None"]):
            assert np.array_equal(ln.get_ydata(), d["net_rel_change"][s_])
        assert [x for x in lf.get_lines() if x.get_linestyle() != "None"][0].get_ydata()[0] == FG.FS4_RB6_FPK_BOUND      # the plan bound, as stored in the A11 row text
        lh = _ax(fig, "(h)")
        ln = [x for x in lh.get_lines()]
        assert np.array_equal(ln[0].get_ydata(), d["vp_f100_hz"]) and np.array_equal(ln[1].get_ydata(), d["vp_f200_hz"])
        lg = _ax(fig, "(g)")
        assert len([x for x in lg.get_lines()]) == 18 and len(lg.texts) == 18
        texts = " ".join(t.get_text() for a in fig.axes for t in a.texts)
        assert "RB6 solver_onset_headline: FAIL" in texts and "RB6 network_fpk_halving_dt: FAIL" in texts and "Radau - default = 181 ms" in texts      # failures drawn at equal weight
    finally:
        plt.close(fig)


def test_layout_no_legend_covers_a_line_or_marker_and_no_text_leaves_the_canvas():
    """13i layout check on the drawn artists (tests/figlayout.py; exact geometry in display pixels)."""
    import matplotlib.pyplot as plt
    from figlayout import clipped_texts, legend_line_hits
    d = FG.prepare_FS4(FG.load_FS4())
    fig = FG._draw_FS4(d, True)
    try:
        assert legend_line_hits(fig) == []
        assert clipped_texts(fig) == []
    finally:
        plt.close(fig)


def test_build_hashes_and_params_agree_with_the_provenance(built):
    res, out = built
    prov = out / "FS4_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "FS4_params.csv", prov) == []
    assert (out / "FS4.pdf").stat().st_size > 0 and (out / "FS4.png").stat().st_size > 0
    rec = json.loads(prov.read_text(encoding="utf-8"))
    assert {i["path"].split("results/")[-1] for i in rec["inputs"]} == set(FG.FS4_INPUTS)


def test_caption_names_the_plotted_quantities_marks_the_proposals_and_has_no_provenance_hash(built):
    res, out = built
    caption = (out / "FS4_caption.txt").read_text(encoding="utf-8")
    assert caption.startswith("FS4. PROPOSED (for ruling):")
    assert "Claim limits: " + ", ".join(FG.FS4_CLAIM_LIMITS) + "." in caption and "PROPOSED for the reviewer's ruling" in caption
    assert "FAILS" in caption and "not used as evidence" in caption and "UNVERIFIED" in caption and "Panel (a)" in caption and "Panels (e) and (f)" in caption
    assert not re.search(r"[0-9a-f]{12,}", caption) and "hash" not in caption.lower() and not re.search(r"\bsha(256)?\b", caption.lower())
    assert "Provenance" not in caption and "FS4_" not in caption
