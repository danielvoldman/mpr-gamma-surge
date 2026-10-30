"""MS13 13p (DL-500, DL-501): tests of the shared rulings R1, R4, R5 and R13 over all eleven figures and of the FS1 to FS5 fixes R14 to R18. They read the stored results under
results/ (git-ignored) and skip if those are absent. Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (string and set equality,
integer counts, display-pixel boxes of the drawn artists); the provenance test reads the recorded builds under figures/ (git-ignored) and skips if they are absent."""
import importlib.util
import json
import re

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import style as S

ROOT = C.repo_root()
RES = ROOT / "results"
FIGS = ("F1", "F2", "F3", "F4", "F5", "F6", "FS1", "FS2", "FS3", "FS4", "FS5")
INPUTS = {f: getattr(FG, f"{f}_INPUTS") for f in FIGS}
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for f in FIGS for p in INPUTS[f]), reason="stored inputs of the eleven figures under results/ are absent")
FOOTERS = {"F1": FG.F1_FOOTER, "F2": FG.F2_FOOTER, "F3": FG.FOOTER, "F4": FG.F4_FOOTER, "F5": FG.F5_FOOTER, "F6": FG.F6_FOOTER,
           "FS1": FG.FS1_FOOTER, "FS2": FG.FS2_FOOTER, "FS3": FG.FS3_FOOTER, "FS4": FG.FS4_FOOTER, "FS5": FG.FS5_FOOTER}


def _audit():
    spec = importlib.util.spec_from_file_location("ms13_audit_for_13p", ROOT / "scripts" / "ms13_audit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ax(fig, prefix):
    hits = [a for a in fig.axes if a.get_title(loc="left").startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


def _draw(fig_id):
    raw = getattr(FG, f"load_{fig_id}")()
    return getattr(FG, f"_draw_{fig_id}")(getattr(FG, f"prepare_{fig_id}")(raw), True)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("figs13p")
    return {f: getattr(FG, f"make_{f}")(out_dir=base / f) for f in FIGS}


# ---- shared rulings over all eleven figures

def test_no_literal_colour_marker_point_size_or_font_size_in_the_drawing_code_of_any_figure():
    au = _audit()
    mod = au.Module(ROOT)
    for f in FIGS:
        assert mod.literals(mod.reached(f)) == [], f                                   # exact: the audit's own rule (R1, R4)


def test_no_proposed_in_any_caption_footer_or_strip_heading(built):
    for f in FIGS:
        assert "PROPOSED" not in built[f]["caption"], f
        assert "PROPOSED" not in FOOTERS[f], f
    for f in ("F1", "F4", "F5"):
        assert "PROPOSED" not in FG.strip_heading(f) and FG.strip_heading(f).endswith(f"(as ruled: {', '.join(FG.RULED_DL[f])}):")
    for f in FIGS:
        th = getattr(FG, f"{f}_TAKE_HOME", None) if f != "F3" else FG.F3_TAKE_HOME
        assert "PROPOSED" not in th, f
    src = (ROOT / "src" / "mprsurge" / "plotting" / "figures.py").read_text(encoding="utf-8")
    assert "PROPOSED strip" not in src and "are PROPOSED for the reviewer" not in src


def test_every_footer_cites_the_ruled_dl_numbers_and_each_exists_in_the_decision_log():
    log = (ROOT / "docs" / "decision_log.md").read_text(encoding="utf-8")
    present = set(re.findall(r"^## (DL-\d+) ", log, flags=re.M))
    assert set(FG.RULED_DL) == set(FIGS)
    for f in FIGS:
        cited = re.findall(r"DL-\d+", FOOTERS[f])
        assert cited == list(FG.RULED_DL[f]), f                                        # exact: the footer names exactly the ruling entries of the figure
        assert set(cited) <= present, (f, sorted(set(cited) - present))
        assert "take-home and claim limits as ruled (" in FOOTERS[f] and FOOTERS[f].startswith(("DRAFT:", "DRAFT v2:", "DRAFT v3:"))
        assert "DL-500" in cited


def test_every_plan_listed_claim_limit_is_carried_or_ruled_out_for_all_eleven_figures():
    au = _audit()
    labels = au.load_label_table(ROOT)
    rows = au.load_plan_table(ROOT, labels)
    for f in FIGS:
        listed = {r["id"] for r in rows if f in r["figures"] and r["id"] in labels}
        carried = set(getattr(FG, f"{f}_CLAIM_LIMITS"))
        missing = {i for i in listed - carried if (f, i) not in au.R5_RULED_OUT}
        assert missing == set(), (f, sorted(missing))                                  # exact (R5); the ruled exceptions are the four pairs of DL-494 R5
    assert {"RB2 FAIL (plan label)", "D24 failed (plan label)"} <= set(FG.FS3_CLAIM_LIMITS)
    assert "RB6 FAIL (plan label)" in FG.FS4_CLAIM_LIMITS and "RB9(b) FAIL (plan label)" in FG.FS5_CLAIM_LIMITS and "MS12-C1" not in FG.FS1_CLAIM_LIMITS


def test_the_provenance_files_of_the_eleven_recorded_builds_name_one_commit_clean_and_draft():
    paths = [ROOT / "figures" / f / f"{f}_provenance.json" for f in FIGS]
    if not all(p.is_file() for p in paths):
        pytest.skip("recorded builds under figures/ are absent")
    recs = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    assert len({r["git"]["commit"] for r in recs}) == 1                                # exact: one build commit (R19)
    assert all(r["git"]["dirty"] is False and r["draft"] is True for r in recs)
    assert len({tuple(sorted((m["path"], m["sha256"]) for m in r["modules"])) for r in recs}) == 1      # every record names the same build code


def test_draft_note_at_the_bottom_and_left_titles_in_fs1_to_fs5():
    import matplotlib.pyplot as plt
    for f in ("FS1", "FS2", "FS3", "FS4", "FS5"):
        fig = _draw(f)
        try:
            notes = [t for t in fig.texts if t.get_gid() == "draft_note"]
            assert len(notes) == 1 and notes[0].get_text() == FOOTERS[f] and notes[0].get_position()[1] == S.DRAFT_NOTE["y"], f
            assert not [a for a in fig.axes if a.get_title(loc="center")], f              # every title is left-aligned (R4)
        finally:
            plt.close(fig)


# ---- R14 FS1

def test_fs1_k4_numbers_lie_between_the_fit_window_lines_and_the_forcing_has_its_own_axes():
    import matplotlib.pyplot as plt
    d = FG.prepare_FS1(FG.load_FS1())
    fig = FG._draw_FS1(d, True)
    try:
        fig.canvas.draw()
        rend = fig.canvas.get_renderer()
        axd = _ax(fig, "(d)")
        box = [t for t in axd.texts if t.get_gid() == "k4_numbers"][0].get_bbox_patch().get_window_extent(rend)
        xs = sorted(axd.transData.transform((x, 0.0))[0] for x in (d["k4_t_start_ms"], d["k4_t_end_ms"]))
        assert xs[0] < box.x0 and box.x1 < xs[1]                                       # exact display pixels: the box sits between the two lines, touching neither
        axe = _ax(fig, "(e)")
        assert not [ln for ln in axe.get_lines() if np.array_equal(ln.get_ydata(), d["K5_I"])]          # the forcing is not drawn on the r axes
        own = [a for a in fig.axes if a is not axe and a.get_shared_x_axes().joined(a, axe)]
        assert len(own) == 1 and np.array_equal(own[0].get_lines()[0].get_ydata(), d["K5_I"])
        assert own[0].yaxis.label.get_color() == S.diagram_mark("s1_forcing").colour
    finally:
        plt.close(fig)


# ---- R15 FS2

def test_fs2_one_tick_size_in_every_panel_and_the_k11_coincide_note_equals_the_drawn_overlap():
    import matplotlib.pyplot as plt
    fig = _draw("FS2")
    try:
        sizes = {t.get_fontsize() for a in fig.axes if a.axison for t in a.get_xticklabels() + a.get_yticklabels() if t.get_text()}
        assert sizes == {S.TEXT_SIZES["tick"]}                                          # exact: one tick size (R4, R15)
        axk = _ax(fig, "(j)")
        pts = axk.get_lines()[0]
        note = [t for t in axk.texts if t.get_gid() == "coincide_note"]
        assert len(note) == 1
        n = FG.coincident_marks(axk, pts, S.FS_SIZES["fs2_coincide_mark"])
        assert note[0].get_text().startswith(f"{n} of {len(pts.get_xdata())} coincide at the drawn size") and n > 0
        assert "stored values all differ" in note[0].get_text()
        raw = FG.load_FS2()
        assert np.array_equal(pts.get_ydata(), raw["a4"]["k11_ratio"])                 # the asterisks stay at their stored positions
    finally:
        plt.close(fig)


# ---- R16 FS3

def test_fs3_no_count_label_of_panel_e_is_crossed_by_a_gate_line():
    import matplotlib.pyplot as plt
    fig = _draw("FS3")
    try:
        fig.canvas.draw()
        rend = fig.canvas.get_renderer()
        axe = _ax(fig, "(e)")
        gates = [ln for ln in axe.get_lines() if ln.get_gid() == "rb2_gate"]
        labels = [t for t in axe.texts if t.get_gid() == "count_label"]
        assert len(gates) == 2 and len(labels) > 0
        for g in gates:
            gb = g.get_window_extent(rend)
            for t in labels:
                assert not t.get_bbox_patch().get_window_extent(rend).overlaps(gb), t.get_text()
    finally:
        plt.close(fig)


def test_fs3_label_rule_moves_a_label_off_the_gate_line_and_keeps_it_inside_its_segment():
    assert FG._fs3_label_y(0.5, 0.25, 0.625) == 0.6875 and FG._fs3_label_y(0.5, 0.25, None) == 0.625          # exact binary values; a tie takes the upper part (DL-502 (b))
    assert FG._fs3_label_y(0.5, 0.25, 0.6) == pytest.approx(0.675, abs=1e-12)                                     # the larger (upper) part 0.6 to 0.75: its middle (abs 1e-12, not binary-exact)
    assert FG._fs3_label_y(0.0, 0.2, 0.8) == pytest.approx(0.1, abs=1e-12)          # gate outside the segment: the middle
    y = FG._fs3_label_y(0.6, 0.3, 0.75)
    assert 0.6 < y < 0.9 and abs(y - 0.75) >= S.FS3_GATE_CLEAR


# ---- R17 FS4 and R18 FS5 marks

def test_fs4_seed_marks_and_fs5_window_marks_are_distinct_vertex_shapes_with_legends():
    seeds = [S.diagram_mark(f"fs4_s{i}") for i in range(3)]
    wins = [S.diagram_mark(f"w_{i}") for i in range(6)]
    for m in seeds + wins:
        assert isinstance(m.marker, tuple), m.key                                      # vertex polygons, no glyph text
        assert not any(w in m.marker_name for w in ("digit", "club", "spade", "heart", "suit", "bowtie", "dagger")), m.key
    assert len({m.marker for m in seeds}) == 3 and len({m.marker for m in wins}) == 6
    import matplotlib.pyplot as plt
    fig = _draw("FS4")
    try:
        for p in ("(e)", "(f)"):
            labs = [t.get_text() for t in _ax(fig, p).get_legend().get_texts()]
            assert {"seed 0", "seed 1", "seed 2"} <= set(labs), p
    finally:
        plt.close(fig)


def test_fs5_g3_judges_map1_and_marks_map2_and_subgrid_reported_not_judged():
    import matplotlib.pyplot as plt
    d = FG.prepare_FS5(FG.load_FS5())
    fig = FG._draw_FS5(d, True)
    try:
        g3 = _ax(fig, "(g3)")
        assert "judged on map 1" in g3.get_title(loc="left")
        rep = [ln for ln in g3.get_lines() if ln.get_gid() == "rb9c_reported"]
        assert len(rep) == 1 and rep[0].get_label() == "reported, not judged"
        assert list(rep[0].get_xdata()) == [1.0, 2.0] and np.array_equal(rep[0].get_ydata(), (d["rb9c_changed"] / d["rb9c_n"])[1:])        # exact: map 2 and subgrid
        assert "reported, not judged" in [t.get_text() for t in g3.get_legend().get_texts()]
        axb = [a for a in fig.axes if any(t.get_text().startswith("(b)") for t in a.texts)][0]
        assert axb.texts[0].get_text().startswith("(b) from test source text, not from results/")
        assert all(len(ln) <= S.FS_LAYOUT["fs5_b_wrap"] + 4 for ln in axb.texts[0].get_text().splitlines()[1:])
    finally:
        plt.close(fig)
