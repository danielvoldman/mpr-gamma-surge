"""MS11 11g: the independent recomputation module, on synthetic signals and fabricated tiny records only (no MS11 record is read)."""
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge.analysis import ms11_independent as I

ROOT = C.repo_root()
FS = 1000.0


def sine(f, dur=20.0, amp=1.0):
    t = np.arange(int(dur * FS)) / FS
    return amp * np.sin(2 * np.pi * f * t)


def test_module_and_script_import_no_original_evaluator():
    for p in (ROOT / "src/mprsurge/analysis/ms11_independent.py", ROOT / "scripts/ms11_independent_check.py"):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.startswith(("import ", "from ")):
                for bad in ("ms11_eval", "ms11_hooks", "ms11_runlist", "run_A11", "ms9_classify", "analysis import a7", "ms10_eval"):
                    assert bad not in line, (p.name, line)


def test_comparators_boundaries():
    assert I.le(0.5, 0.5) and I.ge(8, 8) and not I.lt(0.02, 0.02) and I.lt(0.0199, 0.02)
    assert not I.le(math.nan, 1) and not I.ge(None, 1)


def test_thresholds_read_through_the_loader():
    th = I.frozen_thresholds()
    assert (th["rb2_k"], th["rb2_n"]) == (8, 10) and th["net_fpk"] == 0.02 and th["rb9a"] == 0.005 and th["rb9c"] == 0.05 and th["rb10"] == 0.10
    assert abs(th["threshold_abs"] - 0.1 * th["a_ref"]) < 1e-5


@pytest.mark.parametrize("f", [30.0, 44.6, 80.0])
def test_cycle_frequency_zero_crossings(f):
    fr, n = I.cycle_frequency(sine(f), FS, 3.0, 17.0)
    assert abs(fr - f) < 0.05 and n > 2


def test_cycle_frequency_needs_two_crossings():
    fr, n = I.cycle_frequency(np.zeros(5000), FS, 1.0, 4.0)
    assert math.isnan(fr) and n == 0


def test_raw_first_crossing():
    v = np.zeros(20000)
    t = np.arange(8000) / FS
    v[10000:18000] = 1.0 * np.sin(2 * np.pi * 50 * t)
    t0 = I.raw_first_crossing(v, FS, 5.0, 0.2)
    assert 10.0 - 0.05 < t0 < 10.5
    assert math.isnan(I.raw_first_crossing(np.zeros(20000), FS, 5.0, 0.2))


def test_welch_argmax_on_the_grid():
    # W for T_ramp 10 s is 1/3 s (bin 3.003 Hz): a 60.06 Hz sine sits on a bin and is returned without interpolation
    f = 60.06006006006006
    assert abs(I.welch_argmax(sine(f, 12.0), FS, 2.0, 10.0, 10.0) - 60.06006006006006) < 1.5
    assert I.welch_argmax(sine(40.0, 12.0) + sine(70.0, 12.0, 0.2), FS, 2.0, 10.0, 10.0) < 45.0


def test_counts_and_status():
    cls = ["S+", "S-rel", "S-sus", "NS", "S-abs", "failed", "S-rel", "S-rel", "S+", "S-rel"]
    assert I.count_kept(cls) == 7 and I.count_kept(cls, ("S+",)) == 2 and I.count_kept(cls, ("S+", "S-abs")) == 3
    assert I.rb2_status(8, 8) == "PASS" and I.rb2_status(7, 8) == "FAIL"
    assert I.class_counts(["a", "b", "a"]) == {"a": 2, "b": 1}


def test_direction_and_median():
    assert I.direction_word([3.0, 2.0, 1.0]) == "strict decrease" and I.direction_word([1.0, 2.0, 3.0]) == "strict increase"
    assert I.direction_word([-1.5, -0.97, -1.03]) == "not monotone" and I.direction_word([math.nan, 1.0, 2.0]) == "undefined"
    assert I.median_of([1.0, math.nan, 3.0, 5.0]) == 3.0 and math.isnan(I.median_of([math.nan]))


def test_fpk_pair_strict_bound_and_not_evaluable():
    assert I.fpk_pair(100.0, 102.0, 0.02)["status"] == "FAIL"          # exactly 2 percent: strict "<" fails
    assert I.fpk_pair(100.0, 101.9, 0.02)["status"] == "PASS"
    assert I.fpk_pair(math.nan, 60.0, 0.02)["status"] == "NOT EVALUABLE"
    P = lambda s: {"status": s}                                             # noqa: E731
    assert I.reading_verdict([P("PASS"), P("FAIL")]) == "FAIL" and I.reading_verdict([P("PASS"), P("NOT EVALUABLE")]) == "PASS"
    assert I.reading_verdict([P("NOT EVALUABLE")]) == "NOT EVALUABLE"
    assert I.network_verdict(["FAIL", "PASS"]) == "FAIL" and I.network_verdict(["PASS", "PASS"]) == "PASS" and I.network_verdict(["PASS", "NOT EVALUABLE"]) == "NOT EVALUABLE"


def test_changed_fraction_excludes_not_run_and_non_class_baseline():
    base = ["D-tr", "D-tr", "D-none", "x", "D-sus"]
    var = ["D-tr", "D-sus", "D-none", "D-tr", "not_run"]
    f = I.changed_fraction(base, var)
    assert (f["n"], f["changed"], f["excluded"]) == (3, 1, 2) and abs(f["fraction"] - 1 / 3) < 1e-12
    assert I.map_fraction_status(f, 0.05) == "FAIL" and I.map_fraction_status(I.changed_fraction([], []), 0.05) == "NOT EVALUABLE"
    assert I.map_fraction_status({"n": 900, "changed": 45, "excluded": 0, "fraction": 0.05}, 0.05) == "PASS"      # inclusive


def _fab(tmp_path, dirty=False, dry=False, status="ok"):
    cfg = {"run": {"kind": "mf"}, "path": {"T_ramp_s": 10.0, "t_on_s": 5.0, "eta_H": 2.0}, "solver": {"dt_out_ms": 1.0}, "seeds": {"spawn_key": [11, 1, 3]}, "model": {"tau_ms": 10.0}}
    jp = tmp_path / "r.json"
    jp.write_text(json.dumps({"name": "r", "status": status, "dry_run": dry, "config": cfg, "git": {"dirty": dirty, "commit": "abc"}}), encoding="utf-8")
    np.savez(tmp_path / "r.npz", v=np.arange(10.0), eta=np.linspace(1.0, 3.0, 10))
    return jp


def test_load_record_reads_and_refuses(tmp_path):
    r = I.load_record(_fab(tmp_path))
    assert r["mode"] == "D" and r["fs"] == 1000.0 and r["seed"] == 3 and r["v"].size == 10
    for kw in ({"dirty": True}, {"dry": True}):
        with pytest.raises(I.RecordRefused):
            I.load_record(_fab(tmp_path, **kw))
    assert I.classify({"status": "failed"}, 0.2)["cls"] == "failed"


def test_delay_reads_the_stored_eta_series(tmp_path):
    r = I.load_record(_fab(tmp_path))
    r["fs"] = 1.0                                                             # make sample index = seconds for the check
    assert abs(I.delay_vs_hopf(r, 3.0) - (r["eta"][3] - 2.0)) < 1e-12 and math.isnan(I.delay_vs_hopf(r, math.nan))


def test_script_compare_helper_semantics():
    spec = importlib.util.spec_from_file_location("ms11_independent_check", ROOT / "scripts/ms11_independent_check.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    c = m.Cmp()
    c.count("r", "a", 3, 3); c.count("r", "b", 3, 4); c.count("r", "n", math.nan, math.nan); c.real("r", "x", 1.0, 1.5); c.real("r", "y", math.nan, math.nan)
    ok = [i["ok"] for i in c.items if i["kind"] == "count"]
    assert ok == [True, False, True]
    assert c.items[3]["diff"] == -0.5 and c.items[4]["diff"] == 0.0 and all(i["ok"] for i in c.items if i["kind"] == "float")
