"""D8 candidate study (7g2, DL-153): the plan candidate is the plan estimator, candidates are deterministic and behind
the D8Estimator interface, the live code path is untouched. Study code only."""
import inspect

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge.analysis import d8_candidates as DC
from mprsurge.analysis import d8_study as D
from mprsurge.analysis import estimator_study as E
from mprsurge.analysis import surge_metrics as M

FS, BAND, THR = 1000.0, (25.0, 100.0), 0.1


def step_ring(rate, seed=3, noise=0.005):
    return E.ring(np.random.default_rng(seed), rate, "step", noise)


def test_grid_and_ids():
    c = DC.all_candidates()
    assert len(c) == 54 and len({x.id for x in c}) == 54 and c[0].is_plan
    assert len(DC.single_factor_candidates()) == 8


@pytest.mark.parametrize("rate,onset", [(-6.0, "step"), (3.0, "start"), (-2.0, "start")])
def test_plan_candidate_equals_envelope_growth(rate, onset):
    v = E.ring(np.random.default_rng(5), rate, onset, 0.005)
    g = M.envelope_growth(v, FS, BAND, THR)
    r, s, cyc = DC.fit_all(v, FS, BAND, THR, [DC.PLAN])[DC.PLAN.id]
    assert (r, s) == (g["rate"], g["se"]) and cyc == pytest.approx(g["cycles"])
    d = DC.CandidateD8(DC.PLAN)(v, FS, BAND, THR)
    assert d.damped == M.PLAN_D8(v, FS, BAND, THR).damped


def test_shift_moves_the_step_onset_fit_toward_the_truth():
    v = step_ring(-6.0)
    plan = DC.fit_all(v, FS, BAND, THR, [DC.PLAN])[DC.PLAN.id][0]
    sh = DC.fit_all(v, FS, BAND, THR, [DC.Candidate(shift=2)])["En-S2-M0-plain"][0]
    assert abs(sh + 6.0) < abs(plan + 6.0) and abs(sh + 6.0) < 0.6


def test_se_kinds_order_and_cycle_sampling():
    v = E.ring(np.random.default_rng(1), -3.0, "start", 0.005)
    out = DC.fit_all(v, FS, BAND, THR, [DC.Candidate(se=k) for k in DC.SES])
    plain, ar1, cyc = (out[f"En-S0-M0-{k}"] for k in DC.SES)
    assert ar1[0] == plain[0] and ar1[1] > plain[1]            # AR(1) keeps the rate, inflates the SE
    assert cyc[2] == plain[2] and np.isfinite(cyc[0]) and np.isfinite(cyc[1])


def test_minimum_window_rule_gives_no_call():
    v = E.ring(np.random.default_rng(2), -25.0, "start", 0.005)      # the window is a fraction of 10 cycles
    r, s, cyc = DC.fit_all(v, FS, BAND, THR, [DC.Candidate(minwin=5.0)])["En-S0-M5-plain"]
    if cyc < 5.0:
        assert np.isnan(r) and np.isnan(s)
    d = DC.CandidateD8(DC.Candidate(minwin=5.0))(v, FS, BAND, THR)
    assert d.damped is False or cyc >= 5.0


def test_edge_treatment_removes_the_periodic_wrap():
    t = np.arange(int(14 * FS)) / FS
    gate = np.clip((t - 2.0) / 0.5, 0, 1)
    v = 1.5 * gate * np.sin(2 * np.pi * 40 * t)
    v = v + 1e-4 * np.random.default_rng(1).standard_normal(t.size)
    seg = v[1000:]
    plan = M.PLAN_D8(seg, FS, BAND, 0.2176)
    assert plan.damped                                            # DL-140 finding 1 reproduced
    for edge in ("zero", "odd"):
        assert not DC.CandidateD8(DC.Candidate(edge=edge))(seg, FS, BAND, 0.2176).damped


def test_pad_does_not_change_the_band_or_the_filter():
    assert M.FILTER_ORDER == 4
    v = np.sin(2 * np.pi * 40 * np.arange(4000) / FS)
    for edge in ("zero", "odd"):
        z = DC.analytic(v, FS, BAND, edge)
        assert z.size == v.size and np.allclose(np.abs(z)[1000:-1000], 1.0, rtol=2e-2)
    with pytest.raises(ValueError):
        DC.analytic(v, FS, BAND, "bad")


def test_summarize_c_counts_undefined_fits_as_non_damped():
    cell = dict(kind="ring", rate=-6.0, onset="step", noise=0.005, group="ring")
    rate = np.array([-10.0, np.nan, -10.0, np.nan]); se = np.array([1.0, np.nan, 1.0, np.nan])
    row = D.summarize_c(cell, rate, se, np.full(4, 10.0))
    assert row["match"] == 0.5 and row["n"] == 2 and row["n_draw"] == 4


def test_ramp_ring_is_seeded_and_gradual():
    a = D.ring_ramp(np.random.default_rng(4), 0.0, 0.5, 0.0)
    b = D.ring_ramp(np.random.default_rng(4), 0.0, 0.5, 0.0)
    assert np.array_equal(a, b)
    env = M.envelope(a, FS, BAND)
    assert env[1100] < 0.2 * env[1700]                            # still rising 0.1 s after the onset at 1 s


def test_family_verdict_applies_the_dl136_numbers_unchanged():
    assert (E.FLOOR, E.MATCH_MIN, E.FALSE_DAMPED_MAX) == (2.0, 0.95, 0.05)
    base = dict(kind="ring", onset="step", noise=0.0, ratio_q=1.0, false_non_damped=None)
    rows = [dict(base, rate=-3.0, match=0.94, false_damped=None), dict(base, rate=0.0, match=None, false_damped=0.06),
            dict(base, rate=3.0, match=0.95, false_damped=None)]
    v = D.family_verdict(rows)
    assert v["i_fail_n"] == 1 and v["ii_fail_n"] == 1 and not v["i_met"] and not v["ii_met"]


def test_f1_stream_matches_the_7b_stream():
    cell = dict(kind="ring", rate=-6.0, onset="step", noise=0.005, group="ring")
    seq = np.random.SeedSequence(20261008, spawn_key=(7, 2))
    a = E.run_cell(cell, 4, seq)
    res = D.run_cell_all(*D.gen_for_cell(cell)[:1], 4, np.random.SeedSequence(20261008, spawn_key=(7, 2)), [DC.PLAN], THR)
    assert np.array_equal(a[0], res[DC.PLAN.id][0], equal_nan=True)


def test_live_code_path_untouched():
    src = inspect.getsource(M)
    assert "d8_candidates" not in src and M.PlanD8Estimator.label == M.D8_PROVISIONAL
    assert M.D8_SE_MULT == 2.0 and isinstance(M.PLAN_D8, M.PlanD8Estimator)


def test_run_kind_and_config_load():
    assert "d8cand" in C.RUN_KINDS
    cfg = C.resolve_config("configs/d8_cand.yaml")
    assert cfg["seeds"]["spawn_key"] == [7, 8]
