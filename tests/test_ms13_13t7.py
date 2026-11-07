"""MS13 13t-7 (DL-658 to DL-660): tests of the J3 wording (H4 a to d, H5, H6 of DL-653). They read the recorded results under results/ and skip if those are absent.
Nothing is built into figures/. No data assertion of an earlier test changes."""
from pathlib import Path

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jcaption as JCAP
from mprsurge.plotting import jf26 as JF26
from mprsurge.plotting import jfs as JFS

ROOT = C.repo_root()
RES = ROOT / "results"
SRC = ROOT / "src" / "mprsurge" / "plotting"


def _has(inputs):
    return all((RES / p).is_file() for p in inputs)


def test_j3a_f3_short_names_the_path_legs():
    t = (SRC / "jshort.py").read_text(encoding="utf-8")
    assert "(e) One row per path leg (P5 has an up row and a return row)." in t and "(e) One row per path." not in t


def test_j3c_f1_short_rows_are_recorded_neurons_not_labelled():
    t = (SRC / "jshort.py").read_text(encoding="utf-8")
    assert "each row is one of the {d['ras_n_rows']} recorded neurons; the rows are not labelled" in t
    assert "one row per neuron shown" not in t


def test_j3b_f6_label_c_key_and_caption_agree():
    key = FG.F6J_LABEL_WORDS["c"]
    assert key == "a flag, not a demonstrated cause (below 25 Hz)"
    for f in ("jshort.py", "jf26.py"):
        t = (SRC / f).read_text(encoding="utf-8")
        assert "a flag, not a demonstrated cause (below 25 Hz" in t
    assert "failure label c is a flag, not a demonstrated cause (below 25 Hz; it marks a cell without a surge class" in JF26.F6_LIMIT_EXTRA["MS9(e)-3"]


@pytest.mark.skipif(not _has(FG.F5_INPUTS), reason="stored inputs under results/ are absent")
def test_j3d_f5c_controls_in_panel_d_are_not_drawn_and_the_caption_says_so():
    d = FG.prepare_F5(FG.load_F5())
    assert "ctrl_duration_ms" not in d and "duration_ms" not in FG.F5_CONTROL_METRICS               # no control point in (d)
    defined = [int(np.sum(np.isfinite(d["ctrl_f_pk_hz"][k]))) for k in range(4)]
    assert defined == [int(np.sum(np.isfinite(d["ctrl_onset_s"][k]))) for k in range(4)] and defined[0] == 0 and max(defined) <= 3
    assert "no control seed is drawn in this panel" in (SRC / "jcaption.py").read_text(encoding="utf-8")
    assert "evaluated without the duration" not in (SRC / "jcaption.py").read_text(encoding="utf-8")


@pytest.mark.skipif(not _has(FG.F6_INPUTS) if hasattr(FG, "F6_INPUTS") else True, reason="stored inputs under results/ are absent")
def test_h6_f6_points_sentence_has_p3_drive_2_and_p4a():
    d = FG.prepare_F6(FG.load_F6())
    s = JF26.f6_sentence_points(d)
    lab = [x[2] for x in FG.F6_S6_ROWS]
    fmt = lambda row: [f"{x:.3f}".rstrip("0").rstrip(".") for x in d["s6_f_pk_hz"][lab.index(row)]]
    assert "P3 with drive 2 and P4a differ" in s
    assert ", ".join(fmt("P3, I_amp 2")[:-1]) + " and " + fmt("P3, I_amp 2")[-1] + " Hz for P3 with drive 2" in s
    assert ", ".join(fmt("P4a")[:-1]) + " and " + fmt("P4a")[-1] + " Hz for P4a" in s
    assert "at T_ramp 10, 30, 120 and 300 s in that order" in s


@pytest.mark.skipif(not _has(FG.FS1_INPUTS), reason="stored inputs under results/ are absent")
def test_h5_fs1_panel_values_sentence():
    raw = FG.load_FS1()
    d = FG.prepare_FS1(raw)
    rows = []
    for panel, key in (("a-c", "A1"), ("a-c", "A2"), ("d", "S1_K4"), ("e", "S1_K5")):
        rec = raw["records"][key]
        for r in FG.make_param_table(rec["config"]):
            rows.append({**r, "panel": panel, "section": "", "source_run_id": rec["name"], "source_config_hash12": rec["config_hash12"]})
    c = JFS.fs1_consts(d, rows)
    s = JFS.panel_values_sentence(c)
    assert "input drive of 0 and an input amplitude of 0" in s and "stepped from 0 to 3" in s
    assert "eta_bar -5, J 15 and Delta 1" in s and "amplitude 3 and period 400 ms" in s
    assert s.endswith("Panels (c) and (d) are drawn at different parameter values.")
    # the draft caption does not say that (c) and (d) show the same point (H5: otherwise stop)
    draft = (ROOT / "figures" / "FS1" / "FS1_caption.txt")
    if draft.is_file():
        assert "same fixed point" not in draft.read_text(encoding="utf-8").lower() and "same point" not in draft.read_text(encoding="utf-8").lower()
