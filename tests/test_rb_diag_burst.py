import math

import numpy as np

from mprsurge.analysis import rb_diag_burst as B


def test_segments_and_classification():
    t = np.arange(0, 100, 0.1)
    env = np.full(t.size, 1e-15)
    env[(t >= 10) & (t <= 11)] = 1e-6
    env[(t >= 10.4) & (t <= 10.5)] = 3e-6
    env[t >= 60] = 1.0
    segs = B.segments(env, t)
    assert len(segs) == 2 and math.isclose(segs[0]["peak"], 3e-6) and 10.4 <= segs[0]["peak_s"] <= 10.5 and segs[0]["start_s"] == 10.0
    c = B.classify_segments(segs, 65.0, [5.0, 10.5, 70.0])
    assert [s["kind"] for s in c] == ["pre", "growth"]
    assert c[0]["breakpoints_inside_s"] == [10.5] and B.segment_at(c, 10.5) is c[0] and B.segment_at(c, 30.0) is None


def test_level_is_strict_and_default_1e12():
    t = np.arange(5.0)
    assert B.segments(np.array([0, 1e-12, 2e-12, 1e-12, 0]), t) == [{"start_s": 2.0, "end_s": 2.0, "peak_s": 2.0, "peak": 2e-12, "n": 1}]


def test_implied_shift_sign():
    assert B.implied_onset_shift_s(1.0, 5.0) == 0.0
    assert math.isclose(B.implied_onset_shift_s(math.exp(-1.0), 5.0), 0.2)        # seed lower by e: later by 1/rate
    assert B.implied_onset_shift_s(2.0, 5.0) < 0


def test_net_gain_and_seed_needed():
    t = np.array([0.0, 100.0, 200.0])
    re = np.array([-1.0, -1.0, 1.0])
    I = np.array([0.0, -100.0, -100.0])
    I = np.concatenate([[0.0], np.cumsum(0.5 * (re[1:] + re[:-1]) * np.diff(t))])
    dI = B.net_gain(t, re, I, 0.0, 1.0, 10.0)          # tau_ms = 10: 0 s to 1 s = 0 to 100 tau
    assert math.isclose(dI, I[1])
    assert math.isclose(B.log10_seed_needed(1.0, math.log(10.0)), -1.0)


def test_bit_equal_arrays():
    a = {"v": np.array([1.0, 2.0]), "t": np.array([0.0, 1.0])}
    assert B.bit_equal_arrays(a, {k: x.copy() for k, x in a.items()})[0]
    ok, per = B.bit_equal_arrays(a, {"v": np.array([1.0, np.nextafter(2.0, 3.0)]), "t": a["t"]})
    assert not ok and per == {"t": True, "v": False}
    assert not B.bit_equal_arrays(a, {"v": a["v"]})[0]


def test_effective_seed():
    import math
    assert B.effective_seed(0.217622, 0.0) == 0.217622
    assert math.isclose(B.effective_seed(0.217622, math.log(10.0)), 0.0217622)
    assert B.effective_seed(0.217622, -1.0) > 0.217622
