"""A_ref and the absolute threshold (7c, DL-138 ruling, DL-139). Tolerances are UNVERIFIED (the plan gives none) and stated where used."""
import re
from pathlib import Path

import numpy as np
import pytest

from mprsurge.analysis import a_ref as A

ROOT = Path(__file__).resolve().parents[1]
S3 = ROOT / "results/S3/devalle/devalle_0000_9e49def91dfc.npz"
PERIOD_S = 2.7579110267979594 * 0.01        # stored A5 period at ref_devalle (A5_0000_506cf5745380.json), tau = 10 ms
needs_record = pytest.mark.skipif(not S3.exists(), reason="stored S3 record not present (results/ is git-ignored)")


def synthetic(amp=2.0, f=36.0, total_s=10.0, fs=1000.0):
    t = np.arange(int(total_s * fs) + 1) / fs
    return t, amp * np.sin(2 * np.pi * f * t)


def test_whole_cycle_window_is_integer_periods_inside_trim():
    t = np.arange(10001) / 1000.0
    i0, i1, n = A.whole_cycle_window(t, PERIOD_S)
    assert n == 290                                   # floor(8 s / 27.579 ms)
    assert t[i0] == pytest.approx(1.0) and t[i1 - 1] < 9.0
    assert (i1 - i0) * 1e-3 == pytest.approx(n * PERIOD_S, abs=1.5e-3)    # within one sample


def test_envelope_median_of_steady_sine_is_its_amplitude():
    t, v = synthetic()
    r = A.compute_a_ref(t, v, 1 / 36.0)
    assert r["value"] == pytest.approx(2.0, rel=0.01)       # 1 percent, UNVERIFIED


def test_short_record_and_bad_period_rejected():
    t, v = synthetic(total_s=1.5)
    with pytest.raises(ValueError):
        A.compute_a_ref(t, v, 1 / 36.0)
    with pytest.raises(ValueError):
        A.whole_cycle_window(t, 0.0)


@needs_record
def test_reproduces_dl138_candidate_values():
    d = np.load(S3)
    r = A.compute_a_ref(d["t_ms"] * 1e-3, d["v"], PERIOD_S, a5_ptp=5.5113557649740965)
    # DL-138 gave median 2.155 to 2.169 on t >= 9 s / t >= 7 s windows; the whole-cycle window on [1 s, 9 s) gives
    # 2.1762 (observed). Tolerance: 2.15 to 2.18, UNVERIFIED.
    assert 2.15 < r["value"] < 2.18
    assert r["n_cycles"] == 290
    alt = r["alternates"]
    assert alt["mean"]["value"] == pytest.approx(2.185, abs=0.01)
    assert alt["sqrt2_rms"]["value"] == pytest.approx(2.406, abs=0.01)
    assert alt["half_ptp"]["value"] == pytest.approx(2.756, abs=0.01)
    assert alt["literal_ptp_a5"]["value"] == pytest.approx(5.5114, abs=1e-3)
    assert all(a["label"] == "alternate, not used" for a in alt.values())


@needs_record
def test_invariant_to_dropping_extra_whole_cycles_at_the_ends():
    d = np.load(S3)
    t, v = d["t_ms"] * 1e-3, d["v"]
    base = A.compute_a_ref(t, v, PERIOD_S)["value"]
    for k in (1, 2, 5):
        assert A.compute_a_ref(t, v, PERIOD_S, extra_cycles=k)["value"] == pytest.approx(base, rel=2e-3)   # 0.2 percent, UNVERIFIED


def test_threshold_is_one_absolute_number():
    import inspect
    assert list(inspect.signature(A.threshold_abs).parameters) == ["a_ref", "factor"]    # no cell, path or run argument
    thr = A.threshold_abs(2.1762)
    assert thr == pytest.approx(0.21762)
    cells = [(m, p) for m in ("M2", "M3", "M4") for p in ("P1", "P2", "P3", "P4", "P5")]
    assert len({A.threshold_abs(2.1762) for _ in cells}) == 1


def test_peak_to_peak_is_not_a_threshold_anywhere():
    hits = []
    for p in (ROOT / "src/mprsurge").rglob("*.py"):
        text = p.read_text(encoding="utf-8")
        if re.search(r"5\.5114|5\.51135|5\.5118", text):
            hits.append(p.name)
    assert hits == []                        # no literal peak-to-peak value in code
    assert A.threshold_abs(2.1762) != pytest.approx(0.1 * 5.5114, rel=0.1)


def test_load_rejects_other_definition(tmp_path):
    import json
    p = tmp_path / "a.json"
    p.write_text(json.dumps({"statistic": "max", "value": 3.3}), encoding="utf-8")
    with pytest.raises(ValueError):
        A.load_a_ref(p)
    p.write_text(json.dumps({"statistic": "median", "value": 2.2}), encoding="utf-8")
    assert A.load_a_ref(p) == 2.2
