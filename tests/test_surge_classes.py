"""Surge classes and metrics, 7c (plan Table 2.1, A8, A9 label (f); DL-140). Synthetic and stored records only.

Every class that goes through the D8 call is provisional (D8 open, DL-137). Synthetic class-logic tests use a stub
D8 estimator so that they do not depend on the open estimator; the end-to-end tests with the plan estimator are
marked as such. Test-level tolerances are UNVERIFIED (the plan gives none) and are stated where used.
"""
import inspect
from pathlib import Path

import numpy as np
import pytest

from mprsurge.analysis import a_ref as AR
from mprsurge.analysis import surge_metrics as M

FS = 1000.0
A_REF = 2.176222                                   # DL-139 (stored value; tests only, src reads the file)
THR = AR.threshold_abs(A_REF)                      # 0.1 x A_ref, the one absolute threshold
ROOT = Path(__file__).resolve().parents[1]
S3_LC = ROOT / "results/S3/devalle/devalle_0000_9e49def91dfc.npz"     # limit cycle at ref_devalle
S3_FP = ROOT / "results/S3/devalle/devalle_0001_9a3f46a18b44.npz"     # fixed point (settles after a transient)
needs_s3 = pytest.mark.skipif(not (S3_LC.exists() and S3_FP.exists()),
                              reason="stored S3 records not present (results/ is git-ignored)")


def rng(seed=20261017):
    return np.random.default_rng(seed)


class Stub:
    """A D8 estimator that returns a fixed call; records what it was given."""
    def __init__(self, damped):
        self.damped, self.calls = damped, []

    def __call__(self, v, fs, band, threshold):
        self.calls.append((len(v), threshold))
        return M.D8Result(self.damped, -1.0 if self.damped else 0.0, 0.1, 100, 10.0, 0.0)


NEVER, ALWAYS = Stub(False), Stub(True)


def smooth_burst(on, off, amp=1.0, f=40.0, rise=0.5, total=20.0, noise=1e-4, seed=1):
    t = np.arange(int(total * FS)) / FS
    g = np.clip((t - on) / rise, 0, 1) * np.clip((off - t) / rise, 0, 1)
    return amp * g * np.sin(2 * np.pi * f * t) + noise * rng(seed).standard_normal(t.size)


def mixed(total=30.0, on=None, off=None, a0=0.0, a1=1.0, low0=0.0, low1=0.0, noise=0.02, seed=3):
    """40 Hz and 10 Hz sinusoids plus white noise; the event swaps the amplitudes between on and off."""
    t = np.arange(int(total * FS)) / FS
    ev = (t >= on) & (t < off) if on is not None else np.zeros(t.size, bool)
    ag, al = np.where(ev, a1, a0), np.where(ev, low1, low0)
    return (ag * np.sin(2 * np.pi * 40 * t) + al * np.sin(2 * np.pi * 10 * t)
            + noise * rng(seed).standard_normal(t.size))


# ---- windows and constants (Table 2.1 as the plan words them) ----------------------------------------------------
def test_window_rule_d4():
    assert M.window_for_ramp(120) == (2.0, 1.0)
    assert M.window_for_ramp(60) == (2.0, 1.0)
    w, s = M.window_for_ramp(30)
    assert w == pytest.approx(1.0) and s == pytest.approx(0.5)
    w, s = M.window_for_ramp(1)
    assert w == pytest.approx(0.2) and s == pytest.approx(0.1)          # max(0.2, 1/30)
    with pytest.raises(ValueError):
        M.window_for_ramp(0)


def test_defaults_are_the_plan_values():
    assert (M.G_BAND, M.TOTAL_BAND, M.FACTOR_REL, M.FACTOR_ABS) == ((25.0, 100.0), (1.0, 150.0), 2.0, 2.0)
    assert (M.MIN_CYCLES, M.BASELINE_S, M.COLLAPSE_FRACTION, M.D8_SE_MULT) == (10, 5.0, 0.1, 2.0)


# ---- mode D: every class reachable --------------------------------------------------------------------------------
def test_mode_d_transient_with_plan_d8_end_to_end():
    r = M.classify_mode_d(smooth_burst(8, 14), FS, 5.0, 120, THR)
    assert r.cls == "D-tr" and r.mode == "D" and r.episode.terminated
    assert r.provisional == "provisional (D8 open, DL-137)" and r.d8 is not None and not r.d8.damped
    assert r.episode.cycles > 10 and r.episode.f_pk_hz == pytest.approx(40.0, abs=1.0)
    assert is_close(r.episode.onset_s, 8.1, 0.2) and is_close(r.episode.end_s, 13.9, 0.2)


def is_close(a, b, tol):
    return abs(a - b) <= tol


def test_mode_d_sustained_with_stub_d8():
    r = M.classify_mode_d(smooth_burst(8, 40), FS, 5.0, 120, THR, d8=NEVER)
    assert r.cls == "D-sus" and not r.episode.terminated and r.provisional == M.D8_PROVISIONAL


def test_mode_d_none_below_threshold_and_label_f():
    v = smooth_burst(8, 14, amp=0.05)                                    # envelope 0.05 < 0.2176
    for inside, expect in ((True, True), (False, False), (None, False)):
        r = M.classify_mode_d(v, FS, 5.0, 120, THR, d8=NEVER, inside_a4_region=inside)
        assert r.cls == "D-none" and r.label_f is expect and r.d8 is None and r.provisional is None
        assert not M.is_surge_class(r.cls)


def test_label_f_needs_envelope_never_reaching_threshold():
    short = smooth_burst(8, 8.1, rise=0.03)                              # reaches the threshold, fewer than 10 cycles
    r = M.classify_mode_d(short, FS, 5.0, 120, THR, d8=NEVER, inside_a4_region=True)
    assert r.cls == "D-none" and r.label_f is False and "minimum cycles" in r.reason
    r = M.classify_mode_d(smooth_burst(8, 14), FS, 5.0, 120, THR, d8=NEVER, inside_a4_region=True)
    assert r.cls == "D-tr" and r.label_f is False


def test_mode_d_damped_run_is_not_an_episode():
    r = M.classify_mode_d(smooth_burst(8, 14), FS, 5.0, 120, THR, d8=ALWAYS)
    assert r.cls == "D-none" and "damped" in r.reason and r.provisional == M.D8_PROVISIONAL
    assert r.label_f is False


def test_mode_d_damped_ring_with_plan_d8():
    t = np.arange(int(20 * FS)) / FS
    v = np.where(t >= 8.0, 2.0 * np.exp(-8.0 * (t - 8.0)) * np.sin(2 * np.pi * 40 * (t - 8.0)), 0.0)
    v = v + 1e-4 * rng(5).standard_normal(t.size)
    # step onset: the DL-073 transient can bias the fit, so only the label and the D8 call are checked here
    r = M.classify_mode_d(v, FS, 5.0, 120, THR)
    assert r.provisional == M.D8_PROVISIONAL and r.d8 is not None
    assert r.cls in ("D-none", "D-tr")                                   # D8 open: either call is a provisional output


def test_mode_d_minimum_cycles_edge():
    short = smooth_burst(8, 8.25, rise=0.02)                             # about 8 cycles at 40 Hz
    long = smooth_burst(8, 9.0, rise=0.02)                               # about 38 cycles
    assert M.classify_mode_d(short, FS, 5.0, 120, THR, d8=NEVER).cls == "D-none"
    assert M.classify_mode_d(long, FS, 5.0, 120, THR, d8=NEVER).cls == "D-tr"
    assert M.classify_mode_d(short, FS, 5.0, 120, THR, d8=NEVER, min_cycles=5).cls == "D-tr"


def test_mode_d_gaps_shorter_than_one_window_are_merged():
    def two(gap):
        a = smooth_burst(8, 8.2, rise=0.02, total=30)                    # about 8 cycles: too short alone
        b = smooth_burst(8.2 + gap, 9.2 + gap, rise=0.02, total=30, seed=2)
        return a + b
    near = M.classify_mode_d(two(1.0), FS, 5.0, 120, THR, d8=NEVER)      # gap 1 s < W = 2 s: merged
    far = M.classify_mode_d(two(3.0), FS, 5.0, 120, THR, d8=NEVER)       # gap 3 s: separate; first one fails
    assert near.cls == "D-tr" and near.episode.onset_s == pytest.approx(8.0, abs=0.1)
    assert far.cls == "D-tr" and far.episode.onset_s == pytest.approx(11.2, abs=0.1)


@pytest.mark.parametrize("factor,expect", [(0.05, "D-tr"), (0.1, "D-none"), (0.2, "D-none")])
def test_mode_d_amplitude_threshold_edges(factor, expect):
    amp = 0.075 * A_REF                                                   # above 0.05 x A_ref, below 0.1 x A_ref
    r = M.classify_mode_d(smooth_burst(8, 14, amp=amp), FS, 5.0, 120, AR.threshold_abs(A_REF, factor), d8=NEVER)
    assert r.cls == expect


@pytest.mark.parametrize("factor,expect", [(0.05, "D-tr"), (0.1, "D-tr"), (0.2, "D-none")])
def test_mode_d_amplitude_threshold_edges_upper(factor, expect):
    amp = 0.15 * A_REF                                                    # above 0.1 x A_ref, below 0.2 x A_ref
    r = M.classify_mode_d(smooth_burst(8, 14, amp=amp), FS, 5.0, 120, AR.threshold_abs(A_REF, factor), d8=NEVER)
    assert r.cls == expect


# ---- mode N: every class reachable --------------------------------------------------------------------------------
T_ON = 5.0


def test_mode_n_ns_when_nothing_happens():
    r = M.classify_mode_n(mixed(), FS, T_ON, 120, THR, d8=NEVER)
    assert r.cls == "NS" and r.d8 is None and r.provisional is None and r.episode is None


def test_mode_n_s_plus_with_plan_d8_end_to_end():
    r = M.classify_mode_n(mixed(on=12, off=18), FS, T_ON, 120, THR)
    assert r.cls == "S+" and r.rel and r.abs and r.episode.terminated
    assert r.provisional == "provisional (D8 open, DL-137)" and r.d8 is not None
    assert M.is_surge_class(r.cls)


def test_mode_n_s_rel_relative_only():
    v = mixed(on=12, off=18, a0=1.0, low0=3.0, a1=1.3, low1=0.5)        # G power x1.7, non-G power /36
    r = M.classify_mode_n(v, FS, T_ON, 120, THR, d8=NEVER)
    assert r.cls == "S-rel" and r.rel is not None and r.abs is None


def test_mode_n_s_abs_absolute_only():
    k = np.sqrt(3.0)
    v = mixed(on=12, off=18, a0=1.0, low0=3.0, a1=k, low1=3.0 * k)      # both bands x3: odds unchanged
    r = M.classify_mode_n(v, FS, T_ON, 120, THR, d8=NEVER)
    assert r.cls == "S-abs" and r.abs is not None and r.rel is None


def test_mode_n_s_sus_when_no_termination():
    r = M.classify_mode_n(mixed(on=12, off=40), FS, T_ON, 120, THR, d8=NEVER)
    assert r.cls == "S-sus" and not r.episode.terminated and not M.is_surge_class(r.cls)


def test_mode_n_damped_run_is_not_an_episode():
    r = M.classify_mode_n(mixed(on=12, off=18), FS, T_ON, 120, THR, d8=ALWAYS)
    assert r.cls == "NS" and r.provisional == M.D8_PROVISIONAL and r.d8.damped


@pytest.mark.parametrize("ratio,factor,expect", [
    (3.0, 1.5, "S-abs"), (3.0, 2.0, "S-abs"), (3.0, 4.0, "NS"),
    (1.8, 1.5, "S-abs"), (1.8, 2.0, "NS"), (2.2, 2.0, "S-abs")])
def test_mode_n_factor_edges(ratio, factor, expect):
    k = np.sqrt(ratio)                                                    # both bands scaled: absolute test only
    v = mixed(on=12, off=18, a0=1.0, low0=3.0, a1=k, low1=3.0 * k, noise=0.01)
    r = M.classify_mode_n(v, FS, T_ON, 120, THR, d8=NEVER, factor_abs=factor, factor_rel=factor)
    assert r.cls == expect


def test_mode_n_minimum_cycles_and_gap_merging():
    near = mixed(on=12, off=13.0, a0=0.0, a1=1.0)
    assert M.classify_mode_n(near, FS, T_ON, 120, THR, d8=NEVER).cls == "S+"        # 1 s step, 2 s window: 1 flagged window...
    assert M.classify_mode_n(near, FS, T_ON, 120, THR, d8=NEVER, min_cycles=500).cls == "NS"


def test_mode_n_onset_convention_is_a_named_option():
    v = mixed(on=12, off=18)
    c = M.classify_mode_n(v, FS, T_ON, 120, THR, d8=NEVER)
    s = M.classify_mode_n(v, FS, T_ON, 120, THR, d8=NEVER, conv=M.Conventions(onset="start"))
    assert c.episode.onset_s - s.episode.onset_s == pytest.approx(1.0)           # W / 2
    with pytest.raises(ValueError):
        M.Conventions(onset="first window")


def test_a8_onset_offset_within_one_window_step_and_frequency_within_1_over_w():
    for T in (120, 6):
        W, step = M.window_for_ramp(T)
        v = mixed(on=12, off=18, noise=1e-3)
        r = M.classify_mode_n(v, FS, T_ON, T, THR, d8=NEVER)
        e = r.episode
        assert abs(e.onset_s - 12.0) <= step + 1e-9, (T, e.onset_s)
        assert abs((e.end_s - step / 2) - 18.0) <= step + 1e-9, (T, e.end_s)       # last flagged window centre
        assert abs(e.f_pk_hz - 40.0) <= 1.0 / W + 1e-9


def test_baseline_too_short_and_bad_input():
    with pytest.raises(ValueError):
        M.classify_mode_n(mixed(total=10), FS, 1.0, 120, THR, d8=NEVER)            # baseline shorter than one window


# ---- failed runs --------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("bad", [np.nan, np.inf])
def test_non_finite_input_is_failed_not_ns(bad):
    v = smooth_burst(8, 14)
    v[1234] = bad
    for r in (M.classify_mode_d(v, FS, 5.0, 120, THR), M.classify_mode_n(v, FS, T_ON, 120, THR)):
        assert r.cls == "failed" and r.cls not in M.MODE_N_CLASSES + M.MODE_D_CLASSES
        assert not M.is_surge_class(r.cls) and r.label_f is False
    assert M.classify_mode_d(np.array([]), FS, 5.0, 120, THR).cls == "failed"


# ---- correspondence ------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("cd,cn,agree", [
    ("D-tr", "S+", True), ("D-tr", "S-rel", True), ("D-tr", "S-abs", True), ("D-tr", "S-sus", False),
    ("D-tr", "NS", False), ("D-sus", "S-sus", True), ("D-sus", "S+", False), ("D-sus", "NS", False),
    ("D-none", "NS", True), ("D-none", "S+", False), ("D-none", "S-sus", False),
    ("failed", "NS", False), ("D-none", "failed", False)])
def test_correspondence(cd, cn, agree):
    assert M.classes_agree(cd, cn) is agree


def test_surge_class_definition():
    assert {c for c in M.MODE_N_CLASSES + M.MODE_D_CLASSES if M.is_surge_class(c)} == {"D-tr", "S+", "S-rel", "S-abs"}


# ---- D8 interface: swappable without touching the class logic -----------------------------------------------------
def test_class_logic_does_not_name_the_d8_estimator_internals():
    for fn in (M.classify_mode_d, M.classify_mode_n):
        src = inspect.getsource(fn)
        assert "envelope_growth" not in src and "D8_SE_MULT" not in src and ".rate" not in src and ".se" not in src
        assert ".damped" in src                                              # the only thing the classes read


def test_swapping_the_estimator_changes_the_class_only_through_the_interface():
    v_d, v_n = smooth_burst(8, 14), mixed(on=12, off=18)
    never, always = Stub(False), Stub(True)
    assert M.classify_mode_d(v_d, FS, 5.0, 120, THR, d8=never).cls == "D-tr"
    assert M.classify_mode_d(v_d, FS, 5.0, 120, THR, d8=always).cls == "D-none"
    assert M.classify_mode_n(v_n, FS, T_ON, 120, THR, d8=never).cls == "S+"
    assert M.classify_mode_n(v_n, FS, T_ON, 120, THR, d8=always).cls == "NS"
    assert never.calls[0][1] == THR                                         # the one absolute threshold is passed on


def test_swapped_estimator_is_called_on_the_post_onset_record_once():
    st = Stub(False)
    M.classify_mode_n(mixed(on=12, off=18), FS, T_ON, 120, THR, d8=st)
    assert len(st.calls) == 1 and st.calls[0][0] == 30000 - 5000


@pytest.mark.parametrize("rate,se,damped", [
    (-2.01, 1.0, True), (-1.99, 1.0, False), (-2.0, 1.0, False), (0.5, 1.0, False), (-5.0, 0.0, True),
    (np.nan, np.nan, False)])
def test_plan_d8_rule_is_negative_by_more_than_two_se(monkeypatch, rate, se, damped):
    monkeypatch.setattr(M, "envelope_growth", lambda *a, **k: {"rate": rate, "se": se, "n": 50, "cycles": 10.0,
                                                               "t_start": 0.0})
    assert M.PLAN_D8(np.zeros(100), FS, M.G_BAND, THR).damped is damped


def test_plan_d8_fit_settings_are_the_plans(monkeypatch):
    seen = {}

    def spy(v, fs, band, threshold, n_cycles=10):
        seen.update(band=band, threshold=threshold, n_cycles=n_cycles)
        return {"rate": 0.0, "se": 1.0, "n": 5, "cycles": 1.0, "t_start": 0.0}
    monkeypatch.setattr(M, "envelope_growth", spy)
    M.PLAN_D8(np.zeros(10), FS, M.G_BAND, THR)
    assert seen == {"band": (25.0, 100.0), "threshold": THR, "n_cycles": 10}
    assert M.PLAN_D8.label == "provisional (D8 open, DL-137)"


# ---- metrics ------------------------------------------------------------------------------------------------------
def test_baseline_rho_of_a_flat_spectrum_is_about_one_half():
    v = 0.1 * rng(9).standard_normal(30000)
    assert M.baseline_rho(v, FS, 5.0, 120) == pytest.approx(0.50, abs=0.03)      # plan: flat 1-150 Hz gives about 0.50


def test_onset_delay_and_j_exit_metrics():
    t = np.linspace(0, 100, 1001)
    eta = -4.0 + 0.1 * t
    eta_on, delay = M.onset_delay(50.0, t, eta, eta_H=0.5)
    assert eta_on == pytest.approx(1.0) and delay == pytest.approx(0.5)
    J = -20.0 + 0.1 * t
    j_run, j_static, exit_delay = M.j_exit_metrics(80.0, t, J, -15.0)
    assert (j_run, j_static) == (pytest.approx(-12.0), -15.0) and exit_delay == pytest.approx(3.0)


def test_collapse_marker_is_ten_percent_of_baseline_r():
    t = np.arange(20000) / FS
    r = np.where(t < 12.0, 1.0, 0.05)
    assert M.collapse_time(r, FS, 5.0) == pytest.approx(12.0)
    assert M.collapse_time(np.ones(20000), FS, 5.0) is None
    r2 = np.where(t < 12.0, 1.0, 0.11)
    assert M.collapse_time(r2, FS, 5.0) is None                                   # 11 percent is not below 10 percent
    with pytest.raises(ValueError):
        M.collapse_time(r, FS, 0.0)


# ---- stored records (no new run) ----------------------------------------------------------------------------------
@needs_s3
@pytest.mark.parametrize("t_on", [0.0, 3.0])
def test_stored_limit_cycle_is_sustained_with_plan_d8(t_on):
    v = np.load(S3_LC)["v"]
    r = M.classify_mode_d(v, FS, t_on, 120, AR.threshold_abs(AR.load_a_ref(ROOT / "results/A8/a_ref/a_ref.json")))
    assert r.cls == "D-sus" and r.provisional == M.D8_PROVISIONAL
    assert r.episode.f_pk_hz == pytest.approx(36.5, abs=1.0 / 2.0)                # W = 2 s: resolution 0.5 Hz


@needs_s3
def test_stored_fixed_point_is_none_with_label_f_when_inside_the_region():
    # The caller discards the start transient (surge_metrics edge note): the Hilbert transform is periodic, so a
    # transient at one end puts a spurious envelope above THR at the other end of the record.
    v = np.load(S3_FP)["v"][2000:8000]
    r = M.classify_mode_d(v, FS, 1.0, 120, THR, inside_a4_region=True)
    assert r.cls == "D-none" and r.label_f is True and r.d8 is None


@needs_s3
def test_stored_limit_cycle_stub_d8_class_logic_does_not_depend_on_start_time():
    v = np.load(S3_LC)["v"]
    assert M.classify_mode_d(v, FS, 1.0, 120, THR, d8=NEVER).cls == "D-sus"


# ---- owner rulings at 7h: O10 (S+ needs overlap) and O11 (S-abs broadband flag, F-6) ------------------------------
def two_events(rel_at, abs_at, total=40.0, dur=6.0, seed=5):
    """40 Hz and 10 Hz sinusoids plus noise with a relative-only event (G x1.7 power, non-G /36: odds x61, absolute
    power below 2) and an absolute-only event (both bands x3 in power: odds unchanged), starting at rel_at, abs_at (where they coincide
    the effects multiply)."""
    t = np.arange(int(total * FS)) / FS
    ag, al = np.ones(t.size), 3.0 * np.ones(t.size)
    r = (t >= rel_at) & (t < rel_at + dur)
    a = (t >= abs_at) & (t < abs_at + dur)
    ag[r], al[r] = 1.3, 0.5
    k = np.sqrt(3.0)
    ag[a], al[a] = ag[a] * k, al[a] * k                                   # multiplies where the events coincide
    return (ag * np.sin(2 * np.pi * 40 * t) + al * np.sin(2 * np.pi * 10 * t) + 0.02 * rng(seed).standard_normal(t.size))


def test_o10_disjoint_relative_and_absolute_episodes_are_not_s_plus():
    r = M.classify_mode_n(two_events(rel_at=8, abs_at=22), FS, T_ON, 120, THR, d8=NEVER)
    assert r.rel is not None and r.abs is not None
    assert r.rel.end_s < r.abs.onset_s                                    # no shared window
    assert r.cls == "S-rel" and r.episode is r.rel and "overlap" in r.reason
    r2 = M.classify_mode_n(two_events(rel_at=22, abs_at=8), FS, T_ON, 120, THR, d8=NEVER)
    assert r2.rel is not None and r2.abs is not None
    assert r2.cls == "S-abs" and r2.episode is r2.abs


def test_o10_overlapping_episodes_are_s_plus_and_adjacent_ones_are_not():
    assert M.classify_mode_n(two_events(rel_at=8, abs_at=12), FS, T_ON, 120, THR, d8=NEVER).cls == "S+"
    assert M.classify_mode_n(two_events(rel_at=8, abs_at=14), FS, T_ON, 120, THR, d8=NEVER).cls in ("S-rel", "S-abs")


def test_o10_overlap_does_not_depend_on_the_onset_convention():
    v = two_events(rel_at=8, abs_at=22)
    for onset in ("centre", "start"):
        assert M.classify_mode_n(v, FS, T_ON, 120, THR, d8=NEVER, conv=M.Conventions(onset=onset)).cls == "S-rel"


def test_o11_s_abs_is_flagged_broadband_when_the_rise_peaks_outside_g():
    k = np.sqrt(3.0)
    v = mixed(on=12, off=18, a0=1.0, low0=3.0, a1=k, low1=3.0 * k)       # both bands x3; the larger rise is at 10 Hz
    r = M.classify_mode_n(v, FS, T_ON, 120, THR, d8=NEVER)
    assert r.cls == "S-abs" and r.broadband is True
    assert not (M.G_BAND[0] <= r.rise_peak_hz < M.G_BAND[1]) and r.rise_peak_hz == pytest.approx(10.0, abs=1.0)


def test_o11_s_abs_is_band_limited_when_the_rise_peaks_inside_g():
    k = np.sqrt(3.0)
    v = mixed(on=12, off=18, a0=3.0, low0=1.0, a1=3.0 * k, low1=k)       # both bands x3; the larger rise is at 40 Hz
    r = M.classify_mode_n(v, FS, T_ON, 120, THR, d8=NEVER)
    assert r.cls == "S-abs" and r.broadband is False and r.rise_peak_hz == pytest.approx(40.0, abs=1.0)


def test_o11_flag_is_only_set_for_s_abs_and_adds_no_threshold():
    for r in (M.classify_mode_n(mixed(), FS, T_ON, 120, THR, d8=NEVER),
              M.classify_mode_n(mixed(on=12, off=18), FS, T_ON, 120, THR, d8=NEVER)):
        assert r.cls in ("NS", "S+") and r.broadband is None and r.rise_peak_hz is None
    # the class itself is unchanged by the flag: same record, same class as the O11-free logic (S-abs from the absolute test)
    k = np.sqrt(3.0)
    assert M.classify_mode_n(mixed(on=12, off=18, a0=1.0, low0=3.0, a1=k, low1=3.0 * k), FS, T_ON, 120, THR,
                             d8=NEVER, factor_abs=2.0).cls == "S-abs"


# ---- U-5 (DL-158): P_G/P_non-G threshold edges for the relative test -----------------------------------------------
def rel_only(ratio, noise=0.02):
    """G power unchanged, non-G power divided by `ratio` during the event: the odds P_G/P_non-G rise by about `ratio`
    and the absolute test (P_G) does not move."""
    return mixed(on=12, off=18, a0=1.0, low0=3.0, a1=1.0, low1=3.0 / np.sqrt(ratio), noise=noise)


@pytest.mark.parametrize("factor", [1.5, 2.0, 4.0])
def test_mode_n_relative_threshold_edges(factor):
    below = M.classify_mode_n(rel_only(0.9 * factor), FS, T_ON, 120, THR, d8=NEVER, factor_rel=factor)
    above = M.classify_mode_n(rel_only(1.1 * factor), FS, T_ON, 120, THR, d8=NEVER, factor_rel=factor)
    assert below.cls == "NS" and below.rel is None and below.abs is None
    assert above.cls == "S-rel" and above.rel is not None and above.abs is None


def test_mode_n_relative_default_factor_is_two():
    assert M.FACTOR_REL == 2.0
    assert M.classify_mode_n(rel_only(1.8), FS, T_ON, 120, THR, d8=NEVER).cls == "NS"
    assert M.classify_mode_n(rel_only(2.2), FS, T_ON, 120, THR, d8=NEVER).cls == "S-rel"


# ---- U-5 (DL-158): zero baseline (Table 2.1: no gamma power at a stable fixed point, ratios and mode-N classes
# undefined). The code has no "undefined" class; where it differs from the plan wording the difference is recorded as
# a strict xfail and the classifier is not changed (owner instruction, DL-158). ---------------------------------------
N_ZB = 30000


def _zero_baseline_signals():
    return {"exact_zero": np.zeros(N_ZB), "constant": np.full(N_ZB, -0.5)}


@pytest.mark.parametrize("name", ["exact_zero", "constant"])
def test_zero_baseline_raises_nothing_and_returns_a_known_class(name):
    v = _zero_baseline_signals()[name]
    with np.errstate(all="ignore"):
        rn = M.classify_mode_n(v, FS, T_ON, 120, THR)
        rd = M.classify_mode_d(v, FS, T_ON, 120, THR)
        rho = M.baseline_rho(v, FS, T_ON, 120) if name == "constant" else None
    assert rn.cls in M.MODE_N_CLASSES + ("failed",) and rd.cls in M.MODE_D_CLASSES + ("failed",)
    assert rd.cls == "D-none"
    if rho is not None:
        assert np.isfinite(rho)


def test_zero_baseline_constant_gives_ns_with_finite_outputs():
    """A constant (nonzero) record carries only round-off power (about 1e-35): the baseline is not exactly zero."""
    r = M.classify_mode_n(_zero_baseline_signals()["constant"], FS, T_ON, 120, THR)
    assert r.cls == "NS" and r.episode is None


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="DL-158: exact zero baseline: 0/0 gives NaN odds, the absolute test 0 >= 2 x 0 "
                   "passes and the class is S-sus with NaN peak_rho; the plan wording says 'undefined'")
def test_zero_baseline_exact_zero_has_no_nan_in_outputs():
    with np.errstate(all="ignore"):
        r = M.classify_mode_n(np.zeros(N_ZB), FS, T_ON, 120, THR)
    nums = [x for e in (r.episode, r.rel, r.abs) if e is not None for x in (e.peak_p_g, e.peak_rho, e.f_pk_hz)]
    assert all(np.isfinite(nums))


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="DL-158: the code has no 'undefined' mode-N class (Table 2.1 zero-baseline "
                   "wording); a zero or round-off baseline is classified NS or S-sus")
@pytest.mark.parametrize("name", ["exact_zero", "constant"])
def test_zero_baseline_mode_n_class_is_undefined(name):
    with np.errstate(all="ignore"):
        r = M.classify_mode_n(_zero_baseline_signals()[name], FS, T_ON, 120, THR)
    assert r.cls == "undefined"


# ---- 7j pre-freeze (DL-161): class-level halves of the plan-named A8 items (section 11, MS7 row) -------------------------
# Plan wording: 5-cycle ring -> NS or D-none (envelope growth < 0); slowly damped ring with more than 10 cycles above
# threshold -> NS or D-none (fitted growth negative by more than 2 SE); pure trend -> NS. The plan's 8 A8 ring items are the
# two draw-level items of scripts/study_d8_candidates.py (5-cycle growth negative, 15-cycle ring called damped, each in at
# least 95 percent of 200 draws, DL-136) and the six class items of the A8 synthetic set (a8_sensitivity). With D8 = A
# (plan estimator) two fail: the 15-cycle ring is called damped in 86.5 percent, and D_ring_slow_-3 is classed D-tr
# (departure 1, DL-155). The failing ones are strict xfails with raises=AssertionError; the others are plain tests.
from mprsurge.analysis import a8_sensitivity as S8          # noqa: E402
from mprsurge.analysis import d8_study as D8S               # noqa: E402

A8_DRAWS = 200                                               # DL-136
_A8_CASES = {c[0]: c for c in S8.synthetic_cases() if c[0] in D8S.A8_RING_CASES}
_A8_FAIL_DEPARTURE_1 = pytest.mark.xfail(strict=True, raises=AssertionError,
                                         reason="DL-155/DL-157 departure 1: the plan estimator classes D_ring_slow_-3 D-tr")


def _a8_ring_params():
    out = []
    for name, (_, mode, _v, _t_on, ts) in _A8_CASES.items():
        for T in ts:
            marks = [_A8_FAIL_DEPARTURE_1] if (name, T) == ("D_ring_slow_-3", 120.0) else []
            out.append(pytest.param(name, T, marks=marks, id=f"{name}@T{T:g}"))
    return out


@pytest.mark.parametrize("name,T", _a8_ring_params())
def test_a8_ring_class_is_ns_or_d_none(name, T):
    _, mode, v, t_on, _ = _A8_CASES[name]
    r = S8.classify(v, mode, t_on, T, A_REF, "V0")
    assert r["cls"] in ("NS", "D-none"), (r["cls"], r["note"])


def test_a8_five_cycle_ring_growth_negative_in_95_percent_of_draws():
    seqs = np.random.SeedSequence(20261008, spawn_key=(7, 8, 5, 1)).spawn(A8_DRAWS)
    rates = [M.envelope_growth(D8S.f5_ring5(np.random.default_rng(s)), FS, D8S.BAND, D8S.E.THR)["rate"] for s in seqs]
    assert np.mean(np.asarray(rates) < 0) >= 0.95


def test_a8_five_cycle_ring_class_is_d_none_at_draw_level():
    v = D8S.f5_ring5(np.random.default_rng(1))
    r = M.classify_mode_d(v, FS, 0.0, 120, THR)
    assert r.cls == "D-none"


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="DL-155/DL-157 departure 1: 15-cycle slowly damped ring called damped in 86.5 percent of 200 draws, "
                          "required 95 (plan estimator, step onset)")
def test_a8_slowly_damped_ring_called_damped_in_95_percent_of_draws():
    seqs = np.random.SeedSequence(20261008, spawn_key=(7, 8, 5, 2)).spawn(A8_DRAWS)
    damped = [M.PLAN_D8(D8S.f5_ring15(np.random.default_rng(s)), FS, D8S.BAND, D8S.E.THR).damped for s in seqs]
    assert np.mean(damped) >= 0.95


# ---- pure trend through the classifier (plan: pure trend -> NS) -----------------------------------------------------------
def _trend(noise_sd, seed=11):
    t = np.arange(40000) / FS
    v = 0.5 * np.clip((t - 12.0) / 8.0, 0, 1)                # as N_trend of the A8 synthetic set
    return v + (noise_sd * rng(seed).standard_normal(t.size) if noise_sd else 0.0)


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="DL-159 departure 2 (noise-free inputs to mode N, option (a)): a noise-free trend has zero non-trend "
                          "baseline power; 0/0 odds and 0 >= 2 x 0 give S-sus, not the plan's 'pure trend -> NS'")
@pytest.mark.parametrize("T", [120.0, 3.0])
def test_noise_free_pure_trend_is_ns_in_mode_n(T):
    with np.errstate(all="ignore"):
        r = M.classify_mode_n(_trend(0.0), FS, 10.0, T, THR)
    assert r.cls == "NS"


def test_pure_trend_plus_noise_is_ns_in_mode_n_at_t_ramp_120():
    r = M.classify_mode_n(_trend(0.02), FS, 10.0, 120.0, THR)
    assert r.cls == "NS", r.reason


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="DL-161 departure 4: pure trend plus noise at T_ramp 3 s (W = 0.2 s) is S-rel in a majority of tested seeds (12 to 16 of 20, six 20-seed sets, DL-162); the "
                          "short-window false-surge limit (306 of 500 white-noise records non-NS at W = 0.2 s, DL-147)")
def test_pure_trend_plus_noise_is_ns_in_mode_n_at_t_ramp_3():
    r = M.classify_mode_n(_trend(0.02), FS, 10.0, 3.0, THR)
    assert r.cls == "NS", r.reason
