"""QIF network (plan 6.3, Table 6.1; MS5 5e, DL-117). Fast tests, small N except one short largest-N run."""
import pickle
import tracemalloc

import numpy as np
import pytest
from scipy import stats

from mprsurge import config as C
from mprsurge import qif_network as Q
from mprsurge import run as R
from mprsurge.models.fixed_points import classify_all
from mprsurge.units import ms_to_tau

BASE = {"run.kind": "network", "path.name": "I_step", "path.I_amp": 0.0, "path.t_on_s": 0.0,
        "seeds.spawn_key": [0]}


def cfg_n(**kw):
    ov = {**BASE, **kw}
    return C.resolve_config(None, ov)


def test_kind_registered_and_cfg_picklable():
    assert "network" in C.RUN_KINDS and R.TASKS["network"] == "mprsurge.qif_network:run_network"
    assert R.resolve_task(R.TASKS["network"]) is Q.run_network
    cfg = cfg_n()
    assert pickle.loads(pickle.dumps(cfg)) == cfg


def test_quantiles_match_inverse_lorentzian():
    """D28 / Taher Eq. 8: q_j is the Lorentzian (Cauchy) quantile at j/(N+1); independent of the tan formula."""
    for N in (1, 2, 7, 1000):
        q = Q.lorentzian_offsets(N)
        p = np.arange(1, N + 1) / (N + 1)
        np.testing.assert_allclose(q, stats.cauchy.ppf(p), rtol=1e-9, atol=1e-12)
    q = Q.lorentzian_offsets(1000)
    assert np.all(np.diff(q) > 0) and abs(q.sum()) < 1e-6 * np.abs(q).max()      # sorted, symmetric about 0
    assert np.isclose(np.median(q), 0.0)
    assert Q.lorentzian_offsets(5000, "random", np.random.default_rng(1)).shape == (5000,)


def test_single_neuron_spike_period_matches_analytic_qif():
    """N = 1, constant drive c = eta_bar = 1 (J = 0): V' = V^2 + c. The exact time from V_reset to V_peak is
    2 atan(Vp/sqrt(c))/sqrt(c); the hold is 2/V_cross ~ 2/Vp. Euler at dt = 1e-3 is checked against that
    to 1 percent (tolerance ours, UNVERIFIED; measured period error 1.3e-4)."""
    cfg = cfg_n(**{"network.N": 1, "model.eta_bar": 1.0, "model.J": 0.0, "model.ref_point": None,
                   "durations.hold_s": 2.0, "durations.discard_s": 0.1})
    out = Q.run_network(cfg)["arrays"]
    c, Vp = 1.0, cfg["network"]["V_peak"]
    period = 2.0 * np.arctan(Vp / np.sqrt(c)) / np.sqrt(c) + 2.0 / Vp
    t = out["raster_t_ms"] / cfg["model"]["tau_ms"]                       # tau
    assert t.size >= 5 and out["raster_neuron"].tolist() == [0] * t.size
    assert abs(np.diff(t).mean() - period) < 0.01 * period
    assert abs(t.size - 200 / period) <= 1                                 # refractory count over 200 tau
    assert np.isclose(out["r"].sum() * 0.1, t.size)                         # r_N bins count the same spikes


def test_seeded_determinism():
    kw = {"network.N": 300, "durations.hold_s": 0.2, "durations.discard_s": 0.1}
    a, b = Q.run_network(cfg_n(**kw))["arrays"], Q.run_network(cfg_n(**kw))["arrays"]
    c = Q.run_network(cfg_n(**{**kw, "seeds.spawn_key": [1]}))["arrays"]
    for k in a:
        np.testing.assert_array_equal(a[k], b[k])
    assert not np.array_equal(a["raster_t_ms"], c["raster_t_ms"]) or not np.array_equal(a["v"], c["v"])
    d = Q.run_network(cfg_n(**kw), chunk_bins=7)["arrays"]                  # chunking does not change the run
    for k in a:
        np.testing.assert_array_equal(a[k], d[k])


@pytest.mark.parametrize("ref,tau_d,N", [("ref_devalle", 50.0, 2000), ("ref_ceni", 3.0, 2000)])
def test_network_rate_matches_mean_field_fixed_point(ref, tau_d, N):
    """The M3 mean field is the N -> infinity limit for the Lorentzian grid, so at a stable fixed point the
    time-mean r_N must sit on r*. Regimes: ref_devalle tau_d = 50 ms (stable focus, Re -0.069) and ref_ceni
    tau_d = 3 ms (stable focus), no forcing. Tolerance 2 percent of r*, ours (UNVERIFIED): the plan gives
    none ('agreement very good for N > 10^4', Ferrara, single source). Measured when chosen: 0.3 percent
    (devalle, N = 2000), 0.5 percent (devalle, N = 1000), 0.2 percent (ceni, N = 2000). v_N is not
    compared: it excludes refractory neurons and V_peak = 100 truncates the tails, so it sits about 14
    percent above v* (devalle) by construction."""
    cfg = cfg_n(**{"model.ref_point": ref, "model.tau_d_ms": tau_d, "network.N": N,
                   "durations.hold_s": 3.0, "durations.discard_s": 2.0})
    m = cfg["model"]
    (y, kind, _), = classify_all(m["eta_bar"], m["J"], m["Delta"], m["I_drive"], "M3", ms_to_tau(tau_d, m["tau_ms"]))
    assert kind == "stable"
    out = Q.run_network(cfg, s0=y[0])["arrays"]
    n = out["r"].size
    assert abs(out["r"][n // 2:].mean() - y[0]) < 0.02 * y[0]


def test_largest_n_shape_dtype_memory():
    """N = 5x10^4 on 0.05 s (5 tau, 50 bins of 1 ms) with no discard: output shapes and dtypes, a 300-neuron
    raster, and the allocated memory (tracemalloc sees the numpy buffers) below the estimate with margin."""
    N, hold_s = 50_000, 0.05
    cfg = cfg_n(**{"network.N": N, "durations.hold_s": hold_s, "durations.discard_s": 0.0,
                   "model.ref_point": "ref_devalle"})
    tracemalloc.start()
    res = Q.run_network(cfg)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    a = res["arrays"]
    nb = 50
    for k in ("t_ms", "r", "v", "s", "eta", "J", "Delta", "I"):
        assert a[k].shape == (nb,) and a[k].dtype == np.float64, k
    assert a["raster_t_ms"].dtype == np.float64 and a["raster_neuron"].dtype == np.int32
    assert a["raster_j"].shape == (300,) and a["raster_t_ms"].shape == a["raster_neuron"].shape
    assert np.all(a["raster_neuron"] < N) and np.all(a["raster_t_ms"] > 0.0)
    assert np.allclose(a["t_ms"], np.arange(1, nb + 1)) and np.all(np.isfinite(a["r"]))
    est = res["flags"]["memory_estimate_bytes"]
    assert est == Q.memory_estimate_bytes(N, nb, 100, 0.1)
    assert peak < est * 1.5 and peak < 64 * 2**20      # allocation is the estimate, nowhere near 16 GB
    assert res["flags"]["fastmath"] is False and res["flags"]["float"] == "float64"


def test_refuses_m2_and_unbuilt_shapes():
    with pytest.raises(C.ConfigError, match="M2"):
        Q.run_network(cfg_n(**{"model.type": "M2", "model.ref_point": "ref_mpr", "model.J": -5.0,
                               "model.tau_d_ms": None, "network.N": 10}))
    with pytest.raises(C.ConfigError, match="S10"):
        Q.run_network(cfg_n(**{"network.het_dist": "gaussian", "network.N": 10}))
