"""Estimator study (7b, DL-136): seeded, deterministic, and wired to the pipeline's envelope_growth."""
import numpy as np

from mprsurge import config as C
from mprsurge.analysis import estimator_study as E


def seq():
    return np.random.SeedSequence(20261008, spawn_key=(7, 2))


def test_kind_and_config_load():
    assert "est7b" in C.RUN_KINDS
    cfg = C.resolve_config("configs/est_study.yaml")
    assert cfg["seeds"]["spawn_key"] == [7, 2]


def test_scenario_list_has_zero_growth_and_stationary_cells():
    cells = E.scenarios()
    assert len(cells) == 2 * 2 * len(E.RATES) + 1
    assert sum(c["group"] == "zero" for c in cells) == 2 * 2 + 1
    assert any(c["kind"] == "ar2" for c in cells)


def test_run_cell_is_deterministic():
    cell = dict(kind="ring", rate=-6.0, onset="step", noise=0.005, group="ring")
    a = E.run_cell(cell, 3, seq())
    b = E.run_cell(cell, 3, seq())
    assert all(np.array_equal(x, y) for x, y in zip(a, b))


def test_start_onset_ring_rate_is_recovered_and_called_damped():
    cell = dict(kind="ring", rate=-6.0, onset="start", noise=0.005, group="ring")
    d = E.summarize(cell, *E.run_cell(cell, 20, seq()))
    assert abs(d["bias"]) < 1.0                                # UNVERIFIED test-level
    assert d["match"] == 1.0 and d["n"] == 20


def test_step_onset_underestimates_decay_magnitude_dl073():
    cell = dict(kind="ring", rate=-6.0, onset="step", noise=0.005, group="ring")
    d = E.summarize(cell, *E.run_cell(cell, 20, seq()))
    assert d["bias"] > 1.0                                     # fitted rate closer to zero than the truth (DL-073)


def test_growing_ring_is_not_damped_and_verdict_flags_cells():
    cell = dict(kind="ring", rate=6.0, onset="start", noise=0.005, group="ring")
    d = E.summarize(cell, *E.run_cell(cell, 10, seq()))
    assert d["match"] == 1.0 and d["frac_damped"] == 0.0
    z = dict(d, rate=0.0, match=None, false_damped=0.5, false_non_damped=None, ratio_q=2.0)
    v = E.verdicts([d, z])
    assert v["i_met"] and not v["ii_met"] and v["ii_max_false_damped"] == 0.5


def test_ar2_record_has_unit_mean_envelope():
    v = E.ar2_record(np.random.default_rng(1))
    assert abs(E.M.envelope(v, E.FS, E.BAND).mean() - 1.0) < 1e-9
