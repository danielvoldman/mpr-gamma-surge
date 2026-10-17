"""MS8 8b: coupled Brownian increments for the Heun ladder (F-14, M-10; DL-169). Short runs only; nothing of the S13 floor study is run."""
import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import simulate_mf as S

LADDER = (1.0e-3, 5.0e-4, 2.5e-4, 1.0e-4)
BASE = 5.0e-5


def _rng(key=(8, 2, 1, 0)):
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(20261008, spawn_key=key)))


def test_heun_chunk_z_reproduces_heun_chunk_bit_for_bit():
    """Supplying z = rng.standard_normal(n) from the same generator gives the identical states: the new kernel is the old arithmetic."""
    n = 5000
    t = np.arange(n + 1) * 1e-3
    eta, J, D, I = 2.0 + 0.01 * t, np.full(n + 1, -21.0), np.full(n + 1, 0.3), np.zeros(n + 1)
    for kind in (0, 1):
        y1, y2 = np.array([0.1, -0.5, 0.1]), np.array([0.1, -0.5, 0.1])
        o1, o2 = np.zeros((n // 7 + 1, 3)), np.zeros((n // 7 + 1, 3))
        S.heun_chunk(y1, eta, J, D, I, 200.0, kind, 0.0624, 1e-3, _rng(), 7, 0, o1)
        S.heun_chunk_z(y2, eta, J, D, I, 200.0, kind, 0.0624, 1e-3, _rng().standard_normal(n), 7, 0, o2)
        assert np.array_equal(y1, y2) and np.array_equal(o1, o2)


@pytest.mark.parametrize("m", [1, 2, 5, 10, 20])
def test_coupled_normals_are_scaled_block_sums_of_the_base_draws(m):
    n = 300
    z = S.coupled_normals(_rng(), n, m)
    fine = _rng().standard_normal(n * m)
    assert np.allclose(z, fine.reshape(n, m).sum(axis=1) / np.sqrt(m), rtol=0, atol=1e-13)
    dt = m * BASE
    assert np.allclose(np.sqrt(dt) * z, np.sqrt(BASE) * fine.reshape(n, m).sum(axis=1), rtol=0, atol=1e-13)    # dW_coarse = sum of dW_fine


def test_every_rung_of_the_ladder_sums_to_the_default_rung_increments():
    """F-14: each finer rung's increments sum to the 1e-3 rung's, per seed. M-10's own wording (base 1e-4, blocks of 10, 5, 2) does not
    give the 2.5e-4 rung; the base 5e-5 does, with blocks of 20, 10, 5, 2."""
    assert [round(dt / 1.0e-4, 9) for dt in LADDER] == [10.0, 5.0, 2.5, 1.0]
    n_coarse = 400
    fine_total = n_coarse * 20
    dW = {}
    for dt in LADDER:
        m = int(round(dt / BASE))
        assert abs(m * BASE - dt) < 1e-12
        dW[dt] = np.sqrt(dt) * S.coupled_normals(_rng(), fine_total // m, m)         # same generator state: the same base stream
    coarse = dW[1.0e-3]
    for dt in LADDER[1:]:
        per = int(round(1.0e-3 / dt))
        assert np.allclose(dW[dt].reshape(n_coarse, per).sum(axis=1), coarse, rtol=0, atol=1e-12), dt
    assert np.allclose(dW[5.0e-4].reshape(-1, 2).sum(axis=1), dW[1.0e-3], atol=1e-12)


def test_coupled_stream_does_not_depend_on_the_chunking():
    r1, r2 = _rng(), _rng()
    a = np.concatenate([S.coupled_normals(r1, n, 10) for n in (7, 100, 3, 890)])
    b = S.coupled_normals(r2, 1000, 10)
    assert np.array_equal(a, b)


def _cfg(dt, key=(8, 2, 1, 0), coupling=BASE, run_file="configs/ms8/s13_floor_l1.yaml"):
    ov = {"path.T_ramp_s": 0.5, "path.t_on_s": 0.5, "durations.baseline_s": 0.5, "durations.hold_s": 0.5,
          "durations.discard_s": 0.2, "noise.sigma": 0.0624, "noise.dt_tau": dt, "seeds.spawn_key": list(key)}
    if coupling != "absent":
        ov["noise.coupling_dt_tau"] = coupling
    return C.resolve_config(run_file, ov)


def test_rungs_of_one_seed_agree_far_better_than_independent_seeds():
    """Coupled rungs share the Brownian path, so v at the same times differs by the discretisation error only; independent seeds
    differ by the noise itself (a short quiet segment of the P2 path at sigma 0.0624)."""
    coarse = S.run_mf_noisy(_cfg(1.0e-3))["arrays"]["v"]
    fine = S.run_mf_noisy(_cfg(1.0e-4))["arrays"]["v"]
    other = S.run_mf_noisy(_cfg(1.0e-4, key=(8, 2, 1, 1)))["arrays"]["v"]
    coupled_gap, independent_gap = np.max(np.abs(coarse - fine)), np.max(np.abs(coarse - other))
    assert coupled_gap < 0.25 * independent_gap, (coupled_gap, independent_gap)


def test_coupled_run_is_deterministic_and_independent_of_the_output_chunking():
    a = S.run_mf_noisy(_cfg(5.0e-4), chunk_samples=2000)["arrays"]
    b = S.run_mf_noisy(_cfg(5.0e-4), chunk_samples=37)["arrays"]
    assert all(np.array_equal(a[k], b[k]) for k in a)


def test_rung_that_is_not_a_multiple_of_the_base_step_is_refused():
    with pytest.raises(C.ConfigError, match="whole multiple"):
        S.run_mf_noisy(_cfg(1.0e-4, coupling=3.0e-5))


def test_uncoupled_path_is_untouched_by_the_new_keys():
    """coupling null or absent: the original one-draw-per-step kernel runs, same output as before the change."""
    cfg = _cfg(1.0e-3, coupling="absent", run_file="configs/S5.yaml")
    cfg["run"]["kind"] = "mf_noisy"
    assert "coupling_dt_tau" not in cfg["noise"]
    a = S.run_mf_noisy(cfg)["arrays"]
    cfg2 = _cfg(1.0e-3, coupling=None)
    assert cfg2["noise"]["coupling_dt_tau"] is None
    b = S.run_mf_noisy(cfg2)["arrays"]
    assert all(np.array_equal(a[k], b[k]) for k in a)
    assert C.config_hash(cfg) == C.config_hash(cfg2)
