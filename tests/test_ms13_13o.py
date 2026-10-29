"""MS13 13o (DL-494, DL-495): tests of the shared changes and the F1 to F6 fixes. They read the stored results under results/ (git-ignored) and skip if those are absent.
Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (integer counts, string equality, set equality); the F4 hold check compares a
stored delay with the stored eta_peak - eta_H at abs 1e-9 (the stored delay is a difference of two stored floats)."""
import importlib.util
import inspect
import json
import re
from pathlib import Path

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge.plotting import figprov as F
from mprsurge.plotting import figures as FG
from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS as CL

ROOT = C.repo_root()
RES = ROOT / "results"
FIGS = ("F1", "F2", "F3", "F4", "F5", "F6")
INPUTS = {"F1": FG.F1_INPUTS, "F2": FG.F2_INPUTS, "F3": FG.F3_INPUTS, "F4": FG.F4_INPUTS, "F5": FG.F5_INPUTS, "F6": FG.F6_INPUTS}
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for f in FIGS for p in INPUTS[f]), reason="stored F1 to F6 inputs under results/ are absent")
CAPTION_KEYS = {"F1": FG.F1_CAPTION_KEYS, "F2": FG.F2_CAPTION_KEYS, "F3": FG.CAPTION_KEYS, "F4": FG.F4_CAPTION_KEYS, "F5": FG.F5_CAPTION_KEYS, "F6": FG.F6_CAPTION_KEYS}
LIMITS = {"F1": FG.F1_CLAIM_LIMITS, "F2": FG.F2_CLAIM_LIMITS, "F3": FG.F3_CLAIM_LIMITS, "F4": FG.F4_CLAIM_LIMITS, "F5": FG.F5_CLAIM_LIMITS, "F6": FG.F6_CLAIM_LIMITS}
RULED_OUT = {("F3", "G6-D1"), ("F2", "MS11-C3"), ("F2", "G6-D1")}           # DL-494 R5: explicit earlier rulings (MS12-C1 on FS1 is a 13p figure)
FILE_NAME = re.compile(r"\b[\w./-]+\.(?:md|csv|json|npz|parquet|py|png|pdf|txt|yaml|tsv)\b")


def _audit():
    spec = importlib.util.spec_from_file_location("ms13_audit_for_13o", ROOT / "scripts" / "ms13_audit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("figs13o")
    return {f: (getattr(FG, f"make_{f}")(out_dir=base / f), base / f) for f in FIGS}


# ---- F1 (R6, R7)

def test_f1_spike_counts_sum_to_the_stored_spike_count_and_equal_the_stored_spikes_binned():
    raw = FG.load_F1()
    d = FG.prepare_F1(raw, F.K.load_frozen_criteria()[0])
    n0 = raw["net"][0]["npz"]
    t = n0["raster_t_ms"] / 1000.0                                                   # read back from the stored npz, independent of prepare_F1
    row = np.searchsorted(n0["raster_j"], n0["raster_neuron"])
    assert int(d["ras_count"].sum()) == int(t.size) == int(n0["raster_t_ms"].size)    # exact
    want = np.zeros_like(d["ras_count"])
    np.add.at(want, (row, np.minimum(np.floor(t / FG.F1_COUNT_BIN_S).astype(np.int64), want.shape[1] - 1)), 1)
    assert np.array_equal(d["ras_count"], want) and d["ras_count"].dtype.kind == "i"   # exact integers, no smoothing
    assert d["ras_count_bin_s"] == FG.F1_COUNT_BIN_S == 1.0 and d["ras_count_edges_s"][0] == 0.0 and d["ras_count_edges_s"][-1] >= t.max()


def test_f1_schematic_labels_occur_verbatim_in_the_plan_text_carry_no_number_and_are_drawn_as_declared():
    plan = (ROOT / "docs" / "plan.md").read_text(encoding="utf-8")
    labels = [x for _k, head, rows in FG.F1_SCHEMATIC for x in (head, *[lab for r in rows for lab in r])]
    assert len(FG.F1_SCHEMATIC) == 5 and len(labels) >= 10
    for lab in labels:
        assert lab in plan, lab                                                      # exact: verbatim in docs/plan.md
        assert not re.search(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])", lab), lab           # no stand-alone number (model IDs such as M3 and P2 are names)
        assert "=" not in lab, lab                                                   # no equation
    import matplotlib.pyplot as plt
    d = FG.prepare_F1(FG.load_F1(), F.K.load_frozen_criteria()[0])
    fig = FG._draw_F1(d, True)
    try:
        texts = {t.get_gid(): t.get_text() for ax in fig.axes for t in ax.texts if (t.get_gid() or "").startswith("schematic:")}
        for key, head, rows in FG.F1_SCHEMATIC:
            assert texts[f"schematic:{key}:head"] == head
            assert texts[f"schematic:{key}:rows"].replace("\n", " ") == " ".join(FG.F1_SCHEMATIC_SEP.join(r) for r in rows)    # wrapped at spaces only
    finally:
        plt.close(fig)


# ---- F4 (R8)

def test_f4_hold_points_are_exactly_those_whose_stored_onset_lies_after_the_ramp_reached_eta_peak():
    raw = FG.load_F4()
    d = FG.prepare_F4(raw)
    a7 = raw["a7"]
    n_hold = 0
    for fam, tag, cols in [(f, f, (("onset_cross_s", "delay_eta_cross", "hold_cross"), ("onset_s", "delay_eta", "hold_cls"))) for f, _p, _q in FG.F4_FAMILIES] + \
                          [("p1_start_distance", "sd05", (("onset_cross_s", "delay_eta_cross", "hold_cross"),)), ("p1_start_distance", "sd30", (("onset_cross_s", "delay_eta_cross", "hold_cross"),))]:
        sub = a7[(a7["family"] == fam) & (a7["mode"] == "D")]
        if tag in ("sd05", "sd30"):
            sub = sub[sub["start_distance"] == (0.5 if tag == "sd05" else 3.0)]
        sub = sub.sort_values("T_ramp_s")
        cfg = [json.loads((RES / FG._f4_record_path(fam, r)).read_text(encoding="utf-8"))["config"]["path"] for r in sub["run_id"]]      # read independently of load_F4
        for on_col, dl_col, key in cols:
            want = np.array([p["name"] in ("path_eta", "path_hypoxia") and np.isfinite(float(on)) and float(on) > float(p["t_on_s"]) + float(p["T_ramp_s"])
                             for p, on in zip(cfg, sub[on_col])])
            assert np.array_equal(d[f"{tag}_{key}"], want), (tag, key)                 # exact
            top = np.array([float(p["eta_peak"]) for p in cfg]) - sub["eta_H"].astype(float).to_numpy()
            dl = sub[dl_col].astype(float).to_numpy()
            assert np.all(np.abs(dl[want] - top[want]) <= 1e-9)                         # every hold onset sits at eta_peak - eta_H
            at_top = np.isfinite(dl) & (np.abs(dl - top) <= 1e-9)
            assert np.array_equal(at_top, want) or fam.startswith("p5"), (tag, key)     # and no other delay reaches it (P5 has no hold)
            n_hold += int(want.sum())
    assert n_hold == d["n_hold"] == 8 and d["hold_delay_max"] == 2.0                    # DL-494 hold check: 8 points, eta_peak - eta_H = 2.0 (rounded to 12 digits)
    assert not any(d[f"{f}_hold_cross"].any() or d[f"{f}_hold_cls"].any() for f in ("p5_linear", "p5_sigmoid"))


# ---- F5 (R9)

def test_f5_take_home_states_296_of_325_map2_cells_d_tr_as_stored():
    a9 = __import__("pandas").read_parquet(RES / FG.F5_INPUTS[0])
    m2 = a9[a9["map"].astype(str) == "2"]
    assert (int((m2["class"] == "D-tr").sum()), int(len(m2))) == (296, 325)              # exact, from the stored table
    assert "296 of the 325 cells of map 2" in FG.F5_TAKE_HOME and "D-none 29" in FG.F5_TAKE_HOME
    assert set(FG.F5_NOT_APPLICABLE) == {"MS9(e)-3", "MS9(e)-4"} and all("no A9 failure label is drawn" in v for v in FG.F5_NOT_APPLICABLE.values())


# ---- F6 (R10)

def test_f6_network_run_column_label_equals_its_stored_condition():
    import matplotlib.pyplot as plt
    raw = FG.load_F6()
    rec = json.loads((RES / FG.F6_RECORDS["S12_NC1_net"]).read_text(encoding="utf-8"))["config"]          # read independently of load_F6
    want = (f"network run, N = {int(rec['network']['N'])}\n{rec['model']['ref_point']}: Delta {float(rec['model']['Delta']):g}, tau_d {float(rec['model']['tau_d_ms']):g} ms\n"
            f"{rec['path']['name']}, T_ramp {float(rec['path']['T_ramp_s']):g} s")
    cols = FG.f6_column_labels(raw)
    assert cols["network"] == want
    d = FG.prepare_F6(raw)
    fig = FG._draw_F6(d, True, cols)
    try:
        c = [a for a in fig.axes if a.get_title(loc="left").startswith("(c)")][0]
        ticks = [t.get_text() for t in c.get_xticklabels()]
        assert ticks[-1] == want and len(ticks) == len(d["nc1_cells_class"]) + 1          # its own column, after the five map cells
        x_net = c.get_xticks()[-1]
        net = [ln for ln in c.get_lines() if list(ln.get_xdata()) == [x_net]]
        assert len(net) == 1 and x_net not in range(len(d["nc1_cells_class"]))           # not drawn at a map-cell column
    finally:
        plt.close(fig)
    bad = raw["a10"].copy()
    bad.loc[(bad["control"] == "NC1") & (bad["row_type"] == "network_run"), "Delta"] = 0.29
    with pytest.raises(FG.DataError, match="different conditions"):
        FG.f6_column_labels({**raw, "a10": bad})


# ---- shared (R1, R4, R5, R3)

def test_no_literal_colour_mark_point_size_or_font_size_in_the_f1_to_f6_drawing_code():
    A = _audit()
    mod = A.Module(ROOT)
    for fig in FIGS:
        names = mod.reached(fig)
        assert mod.literals(names) == [], fig                                             # the audit's literal check (colours, colour maps, hatches, markers, point sizes)
        for n in names:
            src = inspect.getsource(getattr(FG, n))
            assert not re.findall(r"\b(?:fontsize|labelsize)=\d", src), (fig, n)          # R4: font sizes come from style.TEXT_SIZES


def test_every_claim_limit_the_plan_lists_is_carried_or_ruled_out():
    A = _audit()
    labels = A.load_label_table(ROOT)
    rows = A.load_plan_table(ROOT, labels)
    for fig in FIGS:
        listed = {r["id"] for r in rows if fig in r["figures"] and r["id"]}
        missing = {i for i in listed if i not in LIMITS[fig] and (fig, i) not in RULED_OUT}
        assert missing == set(), (fig, sorted(missing))                                   # exact
        assert all(i in CL for i in LIMITS[fig]), fig


def test_captions_print_every_limit_with_its_definition_name_no_file_and_list_only_the_caption_keys(built):
    for fig, (out, d) in built.items():
        caption = (d / f"{fig}_caption.txt").read_text(encoding="utf-8")
        na = getattr(FG, f"{fig}_NOT_APPLICABLE", {})
        assert "Claim limits: " + "; ".join(f"{i}: {CL[i][0]} ({', '.join(CL[i][1])})" + (f", not applicable here because {na[i]}" if i in na else "")
                                            for i in LIMITS[fig]) + "." in caption, fig
        assert not FILE_NAME.search(caption), (fig, FILE_NAME.findall(caption))          # R3: no file name
        assert f"The full parameter list is in the Nordlie table of {fig}." in caption, fig
        part = caption.split("Parameters: ", 1)[1].split(". The full parameter list", 1)[0]
        keys = [x.split("=", 1)[0] for x in part.split("; ")]
        assert len(keys) == len(set(keys)), fig                                           # no repeated key (per panel or per seed)
        assert set(keys) <= set(CAPTION_KEYS[fig]), fig                                   # only the declared caption keys
        with open(d / f"{fig}_params.csv", newline="", encoding="utf-8") as fh:
            all_keys = {r["key"] for r in __import__("csv").DictReader(fh)}
        assert len(keys) < len(all_keys), fig                                             # not the full parameter dump
        assert "[" not in part.split("=", 1)[0]                                           # no '[panel] key' prefix


def test_draft_note_sits_at_the_bottom_and_titles_are_left_aligned():
    import matplotlib.pyplot as plt
    from mprsurge.plotting import style as S
    crit = F.K.load_frozen_criteria()[0]
    d3 = FG.prepare_F3(FG.load_F3())
    d2 = FG.prepare_F2(FG.load_F2())
    for fig in (FG._draw_F3(d3, True, FG.strip_lines(d3)), FG._draw_F2(d2, True, FG.strip_lines(d2)), FG._draw_F6(FG.prepare_F6(FG.load_F6()), True)):
        try:
            notes = [t for t in fig.texts if t.get_gid() == "draft_note"]
            assert len(notes) == 1 and notes[0].get_position()[1] == S.DRAFT_NOTE["y"] and "DRAFT" in notes[0].get_text()
            assert all(ax.get_title(loc="center") == "" for ax in fig.axes)
            assert all(ax._left_title.get_fontsize() == S.TEXT_SIZES["panel_title"] for ax in fig.axes if ax.get_title(loc="left"))
        finally:
            plt.close(fig)
    assert crit is not None
