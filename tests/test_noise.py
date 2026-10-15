"""Mode N: stochastic Heun kernel and run_mf_noisy (plan 6.2, 6.4, 10.4; DL-072)."""
import time

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import simulate_mf as S
from mprsurge.errors import RunTimeout

SHORT = {"path.name": "path_eta", "path.eta_start": 1.0, "path.eta_peak": 4.0, "path.T_ramp_s": 1.0,
         "path.t_on_s": 0.5, "durations.baseline_s": 0.5, "durations.hold_s": 0.5, "durations.discard_s": 0.5,
         "noise.sigma": 0.05, "seeds.spawn_key": [0]}


def cfg_n(**extra):
    ov = {**SHORT, **extra}
    return C.resolve_config(None, ov)


def test_ou_stationary_variance_matches_sigma2_over_2k():
    # Plan 10.5 (test_noise): variance of an Ornstein-Uhlenbeck process, dv = -k v dt + sigma dW, is
    # sigma^2/(2k). Same kernel, same Heun and noise lines (kind 2). Tolerance 5%: UNVERIFIED test-level
    # value (DL-072); the statistical error of the estimate is about 1% for these settings.
    k, sigma, dt, n = 2.0, 0.5, 1e-3, 20_000_000
    rng = S.make_rng(20261008, [0])
    y = np.array([0.0, 0.0, 0.0])
    par = np.full(n + 1, k)
    zero = np.zeros(n + 1)
    out = np.empty((n // 100, 3))
    S.heun_chunk(y, zero, par, zero, zero, 0.0, 2, sigma, dt, rng, 100, 0, out)
    v = out[10:, 1]                                   # drop the first 1000 tau of transient
    assert v.var() == pytest.approx(sigma**2 / (2 * k), rel=0.05)
    assert abs(v.mean()) < 5 * np.sqrt(sigma**2 / (2 * k) / (len(v) / 25))   # mean zero, loose


def test_validation_drift_kind_is_not_selectable_from_a_config(monkeypatch):
    # kind 2 (OU drift) is test-only (DL-072 item 6): run_mf_noisy derives kind from model.type.
    seen = []
    real = S._run_chunks
    monkeypatch.setattr(S, "_run_chunks", lambda rng, y, kind, *a, **k: (seen.append(kind), real(rng, y, kind, *a, **k))[1])
    S.run_mf_noisy(cfg_n())
    S.run_mf_noisy(C.resolve_config(None, {**SHORT, "model.type": "M2", "model.ref_point": "ref_mpr", "model.J": -5.0,
                                           "path.eta_start": -1.0, "path.eta_peak": 0.0}))
    assert sorted(seen) == [0, 1]


def test_same_spawn_key_same_stream_and_other_key_differs():
    a = S.run_mf_noisy(cfg_n())["arrays"]
    b = S.run_mf_noisy(cfg_n())["arrays"]
    c = S.run_mf_noisy(cfg_n(**{"seeds.spawn_key": [1]}))["arrays"]
    assert all(np.array_equal(a[k], b[k]) for k in a)
    assert not np.array_equal(a["v"], c["v"])


def test_result_does_not_depend_on_chunking():
    a = S.run_mf_noisy(cfg_n(), chunk_samples=7)["arrays"]          # many chunks, odd length
    b = S.run_mf_noisy(cfg_n(), chunk_samples=100000)["arrays"]     # one chunk
    assert all(np.array_equal(a[k], b[k]) for k in a)


def test_grid_discard_and_kick():
    cfg = cfg_n(**{"noise.sigma": 1e-12})                           # essentially deterministic
    res = S.run_mf_noisy(cfg)["arrays"]
    n_expected = int(np.floor((0.5 + 1.0 + 0.5) * 1000 / 1.0 + 1e-9)) + 1    # t_on + T_ramp + hold, 1 ms grid
    assert res["t_ms"].shape == (n_expected,) and res["t_ms"][0] == 0.0 and res["t_ms"][1] == 1.0
    v = res["v"]
    k_on = 500
    assert v[k_on - 1] == pytest.approx(v[0], abs=1e-9)             # flat before t_on (fixed point start)
    assert v[k_on] - v[k_on - 1] == pytest.approx(cfg["solver"]["delta0"], abs=1e-8)   # delta0 at t_on


def test_noise_scales_with_sigma_and_sigma_factor():
    base = cfg_n(**{"noise.sigma": 0.02})
    std = lambda cfg: np.std(S.run_mf_noisy(cfg)["arrays"]["v"][:400])
    s1 = std(base)
    s2 = std(cfg_n(**{"noise.sigma": 0.02, "noise.sigma_factor": 2.0}))
    assert s2 / s1 == pytest.approx(2.0, rel=0.05)                  # linear regime at the fixed point


def test_refuses_null_sigma_and_null_spawn_key():
    with pytest.raises(C.ConfigError, match="noise.sigma"):
        S.run_mf_noisy(cfg_n(**{"noise.sigma": None}))
    with pytest.raises(C.ConfigError, match="spawn_key"):
        S.run_mf_noisy(cfg_n(**{"seeds.spawn_key": None}))


def test_m2_noisy_runs():
    cfg = C.resolve_config(None, {"model.type": "M2", "model.ref_point": "ref_mpr", "model.J": -5.0, "path.name": "path_eta",
                                  "path.eta_start": -1.0, "path.eta_peak": 0.0, "path.T_ramp_s": 0.5,
                                  "path.t_on_s": 0.2, "durations.baseline_s": 0.2, "durations.hold_s": 0.2, "durations.discard_s": 0.2,
                                  "noise.sigma": 0.05, "seeds.spawn_key": [0]})
    res = S.run_mf_noisy(cfg)["arrays"]
    assert np.all(np.isfinite(res["v"])) and np.array_equal(res["s"], res["r"])


def test_wall_limit_stops_a_long_jitted_run_between_chunks():
    cfg = cfg_n(**{"path.T_ramp_s": 1000.0})                         # about 1e8 steps: many seconds
    S.warm_up()
    t0 = time.monotonic()
    with pytest.raises(RunTimeout):
        S.run_mf_noisy(cfg, deadline=t0 + 0.3)
    assert time.monotonic() - t0 < 5.0
