"""QIF network, M3 synapse (plan 6.3, Table 6.1; MS5 5e, DL-117).

Neuron j, tau units: dV_j/dt = V_j^2 + eta_j(t) + J(t) s + I(t), eta_j(t) = eta_bar(t) + Delta(t) q_j,
q_j = tan(pi (2j - N - 1) / (2 (N + 1))) (D28, Taher, Torcini, Olmi 2020 Eq. 8). Synapse (M3):
s <- s + (tau/tau_d)(-s dt + n_spikes/N) per step. Forward Euler, dt = network.dt_tau. At a crossing
V >= V_peak the neuron is reset to V_reset, held for 2/V_cross and its spike is counted 1/V_cross after
the crossing (Table 6.1). Heterogeneity is fixed offsets q_j; the network has no noise term (the sigma of
6.4 belongs to the mean field), so the only random input is the initial V, drawn from the seed child.

Choices the plan does not state (UNVERIFIED, DL-117): the hold and the spike delay are counted in whole
steps (no sub-step carry-over); the pending spike is counted on the first step at which its delay has
elapsed, and not before the step after the crossing; s(start) = 0; the 300 raster neurons are evenly
spaced in j; r_N and v_N are stamped at the end of their bin. There is no M2 coupling (open item 1,
section 12.4): model.type M2 is refused.

Numba, float64, no fastmath, one run per process, no prange (single thread whatever the pool sets).
Drivers only integrate: this module has no analysis.
"""
from __future__ import annotations

import os
import time

import numba
import numpy as np
from numba import njit

from . import config as C
from .errors import RunTimeout
from .ramps import make_path
from .simulate_mf import make_rng
from .units import ms_to_tau, s_to_tau

_EPS = 1e-9
CHUNK_BINS = 200          # bins per kernel call (deadline check and parameter arrays are per chunk)
RASTER_RATE_CAP = 4.0     # per neuron per tau, sizes the raster buffer; overflow raises


# --- heterogeneity -------------------------------------------------------------------------------

def lorentzian_offsets(N: int, sampling: str = "quantile", rng=None) -> np.ndarray:
    """q_j = (eta_j - eta_bar)/Delta, Table 6.1. quantile: tan(pi(2j-N-1)/(2(N+1))), j = 1..N (D28);
    random: tan(pi(u_j - 1/2)), u_j uniform (seeded)."""
    if sampling == "quantile":
        j = np.arange(1, N + 1, dtype=float)
        return np.tan(np.pi * (2.0 * j - N - 1.0) / (2.0 * (N + 1.0)))
    if sampling == "random":
        return np.tan(np.pi * (rng.random(N) - 0.5))
    raise C.ConfigError(f"network.het_sampling {sampling!r}")


def raster_indices(N: int, n_raster: int) -> np.ndarray:
    """Evenly spaced neuron indices for the raster (ours, UNVERIFIED)."""
    n = min(n_raster, N)
    return np.unique(np.round(np.linspace(0, N - 1, n)).astype(np.int64))


def _raster_cap(n_raster: int, chunk_bins: int, bin_tau: float) -> int:
    return int(RASTER_RATE_CAP * n_raster * chunk_bins * bin_tau) + 1000


def memory_estimate_bytes(N: int, n_bins: int, steps_per_bin: int, bin_tau: float, n_raster: int = 300,
                          chunk_bins: int = CHUNK_BINS) -> int:
    """Bytes held by run_network: neuron state (V, q, tref, tspk float64; slot int32), the per-chunk
    parameter arrays (4 float64 per step), the raster buffer and the per-bin outputs (counts int64 and
    5 float64 per bin, plus the path columns)."""
    neuron = N * (4 * 8 + 4)
    params = 4 * 8 * chunk_bins * steps_per_bin
    raster = (8 + 4) * _raster_cap(n_raster, chunk_bins, bin_tau)
    out = n_bins * (8 + 8 * 8)
    return neuron + params + raster + out


# --- kernel --------------------------------------------------------------------------------------

@njit(cache=True, fastmath=False)
def qif_chunk(V, q, tref, tspk, s_io, slot, eta, J, Delta, I, beta, dt, Vp, Vr, spb, nbins,
              exclude, g0, t0, counts, vmean, sout, rt, ri, rn):
    """Advance nbins bins of spb steps each, in place (V, tref, tspk, s_io[0]). eta, J, Delta, I hold the
    parameter at the start of each step (nbins*spb entries). counts[b] = spikes counted in bin b,
    vmean[b] = mean V (over non-refractory neurons if exclude) and sout[b] = s at the end of bin b.
    Raster rows (time of counting, neuron) go to rt, ri; rn[0] is the number of rows wanted, so a value
    above len(rt) means overflow. g0 is the global index of step 0 and t0 the time of global step 0."""
    N = V.shape[0]
    s = s_io[0]
    cap = rt.shape[0]
    for b in range(nbins):
        nb = 0
        for k in range(spb):
            i = b * spb + k
            drive = J[i] * s + I[i]
            e0 = eta[i]
            dl = Delta[i]
            ns = 0
            tnow = t0 + (g0 + i + 1) * dt
            for j in range(N):
                if tspk[j] > 0.0:
                    tspk[j] -= dt
                    if tspk[j] <= 0.0:
                        tspk[j] = 0.0
                        ns += 1
                        sl = slot[j]
                        if sl >= 0:
                            if rn[0] < cap:
                                rt[rn[0]] = tnow
                                ri[rn[0]] = j
                            rn[0] += 1
                if tref[j] > 0.0:
                    tref[j] -= dt
                    continue
                v = V[j]
                v = v + dt * (v * v + e0 + dl * q[j] + drive)
                if v >= Vp:
                    tref[j] = 2.0 / v
                    tspk[j] = 1.0 / v
                    v = Vr
                V[j] = v
            nb += ns
            s = s + beta * (-s * dt + ns / N)
        counts[b] = nb
        acc = 0.0
        cnt = 0
        for j in range(N):
            if exclude and tref[j] > 0.0:
                continue
            acc += V[j]
            cnt += 1
        vmean[b] = acc / cnt if cnt > 0 else np.nan
        sout[b] = s
    s_io[0] = s


def warm_up() -> None:
    """Compile and cache the kernel in the parent before the pool starts (10.4)."""
    N = 8
    z = np.zeros(4)
    V = np.linspace(-1.0, 1.0, N)
    qif_chunk(V, np.zeros(N), np.zeros(N), np.zeros(N), np.zeros(1), -np.ones(N, np.int32), z, z, z, z,
              1.0, 1e-3, 100.0, -100.0, 2, 2, True, 0, 0.0, np.zeros(2, np.int64), np.zeros(2), np.zeros(2),
              np.zeros(4), np.zeros(4, np.int32), np.zeros(1, np.int64))


# --- runner task ---------------------------------------------------------------------------------

def run_network(cfg: dict, deadline=None, s0: float = 0.0, chunk_bins: int = CHUNK_BINS) -> dict:
    """Runner task for run.kind = network (picklable cfg in, plain arrays out). Mode N conventions:
    discard_s before t = 0 is not returned (CP14). Output grid: one sample per rate_bin_ms bin, stamped
    at the bin end, t_ms = (b + 1) bin for b = 0..n-1; r in 1/tau units like the mean field."""
    m, nw, d = cfg["model"], cfg["network"], cfg["durations"]
    if m["type"] != "M3":
        raise C.ConfigError("network: only M3 is built; no attached source gives the M2 network coupling "
                            "(open item 1, section 12.4, UNVERIFIED)")
    if m["tau_d_ms"] is None:
        raise C.ConfigError("model.tau_d_ms is required for the network")
    if nw["het_dist"] != "lorentzian":
        raise C.ConfigError(f"network.het_dist {nw['het_dist']!r}: S10 shapes are not built")
    tau = m["tau_ms"]
    path = make_path(cfg)
    dt, N = nw["dt_tau"], nw["N"]
    bin_tau = ms_to_tau(nw["rate_bin_ms"], tau)
    spb = int(round(bin_tau / dt))
    if spb < 1 or abs(spb * dt - bin_tau) > 1e-9 * bin_tau:
        raise C.ConfigError(f"network.dt_tau = {dt} does not divide the rate bin {bin_tau} tau")
    t_end = path.t_ramp_end + s_to_tau(d["hold_s"], tau)
    disc = s_to_tau(d["discard_s"], tau)
    n_disc, n_keep = int(round(disc / bin_tau)), int(round(t_end / bin_tau))
    if abs(n_disc * bin_tau - disc) > 1e-9 * max(disc, 1.0) or abs(n_keep * bin_tau - t_end) > 1e-9 * t_end:
        raise C.ConfigError("discard and end time must be whole numbers of rate bins")
    n_bins = n_disc + n_keep
    t0 = -n_disc * bin_tau
    beta = 1.0 / ms_to_tau(m["tau_d_ms"], tau)

    rng = make_rng(cfg["seeds"]["root_seed"], cfg["seeds"]["spawn_key"])
    lo, hi = nw["init_V_range"]
    V = lo + (hi - lo) * rng.random(N)
    q = lorentzian_offsets(N, nw["het_sampling"], rng)
    tref, tspk = np.zeros(N), np.zeros(N)
    ridx = raster_indices(N, nw["n_raster"])
    slot = np.full(N, -1, dtype=np.int32)
    slot[ridx] = np.arange(ridx.size, dtype=np.int32)
    s_io = np.array([float(s0)])

    counts = np.empty(n_bins, dtype=np.int64)
    vmean, sout = np.empty(n_bins), np.empty(n_bins)
    cap = _raster_cap(ridx.size, chunk_bins, bin_tau)
    rt, ri = np.empty(cap), np.empty(cap, dtype=np.int32)
    rast_t, rast_i = [], []
    b0 = 0
    while b0 < n_bins:
        if deadline is not None and time.monotonic() > deadline:
            raise RunTimeout("wall-time limit reached between kernel chunks")
        nb = min(chunk_bins, n_bins - b0)
        t = t0 + (b0 * spb + np.arange(nb * spb)) * dt
        rn = np.zeros(1, dtype=np.int64)
        qif_chunk(V, q, tref, tspk, s_io, slot, np.asarray(path.eta(t), float), np.asarray(path.J(t), float),
                  np.asarray(path.Delta(t), float), np.asarray(path.I(t), float), beta, dt,
                  nw["V_peak"], nw["V_reset"], spb, nb, bool(nw["exclude_refractory"]), b0 * spb, t0,
                  counts[b0:b0 + nb], vmean[b0:b0 + nb], sout[b0:b0 + nb], rt, ri, rn)
        if rn[0] > cap:
            raise RuntimeError(f"raster buffer overflow ({rn[0]} rows, capacity {cap}); lower chunk_bins")
        rast_t.append(rt[:rn[0]].copy())
        rast_i.append(ri[:rn[0]].copy())
        b0 += nb
    tb = (np.arange(1, n_keep + 1)) * bin_tau            # bin ends after t = 0, tau units
    keep = slice(n_disc, n_bins)
    rt_all, ri_all = np.concatenate(rast_t), np.concatenate(rast_i)
    sel = rt_all > 0.0
    arrays = {"t_ms": tb * tau, "r": counts[keep] / (N * bin_tau), "v": vmean[keep], "s": sout[keep],
              "eta": np.asarray(path.eta(tb), float), "J": np.asarray(path.J(tb), float),
              "Delta": np.asarray(path.Delta(tb), float), "I": np.asarray(path.I(tb), float),
              "raster_t_ms": rt_all[sel] * tau, "raster_neuron": ri_all[sel].astype(np.int32),
              "raster_j": ridx}
    flags = {"scheme": "forward_euler", "dt_tau": dt, "N": N, "V_peak": nw["V_peak"], "V_reset": nw["V_reset"],
             "het": f"{nw['het_dist']}_{nw['het_sampling']}", "spikes_total": int(counts.sum()),
             "float": "float64", "fastmath": False, "numba": numba.__version__,
             "numba_threads_env": os.environ.get("NUMBA_NUM_THREADS"),
             "s_start": float(s0), "n_bins_discarded": n_disc, "seed_spawn_key": list(cfg["seeds"]["spawn_key"]),
             "m2_coupling": "unsourced, not built",
             "memory_estimate_bytes": memory_estimate_bytes(N, n_keep, spb, bin_tau, ridx.size, chunk_bins)}
    return {"arrays": arrays, "message": "ok", "flags": flags}


def run_s4_network(cfg: dict, deadline=None, chunk_bins: int = CHUNK_BINS) -> dict:
    """Runner task for run.kind = s4_net (MS6 6d, DL-128; plan 6.2 S4, network part): the quasi-static sweep of run_s4
    on the QIF network. s4.param is eta_bar (the network tau_d is fixed). Up through the s4.values (after s4.indices),
    then down again, the top value run twice; each step s4.step_s long, state (V, refractory, pending spikes, s)
    carried over. Start: V drawn from the seed child, s = the mean-field stable fixed point s at the first value
    (UNVERIFIED; the first step's unread part is the transient). delta0 is added to every V at the start of each step
    (the network analogue of the mean-field per-step kick; UNVERIFIED). Same sigma-free dynamics and kernel as
    run_network; no raster. Output series as run_s4 (r, v, s per rate bin, step, param) so analysis.s4 reads it."""
    from .models.fixed_points import stable_fixed_point
    from .simulate_mf import s4_values
    m, nw, q, sv = cfg["model"], cfg["network"], cfg["s4"], cfg["solver"]
    if m["type"] != "M3" or q["param"] != "eta_bar" or m["tau_d_ms"] is None:
        raise C.ConfigError("run.kind s4_net: M3, s4.param eta_bar and model.tau_d_ms are required")
    if nw["het_dist"] != "lorentzian":
        raise C.ConfigError(f"network.het_dist {nw['het_dist']!r}: S10 shapes are not built")
    tau, dt, N = m["tau_ms"], nw["dt_tau"], nw["N"]
    bin_tau = ms_to_tau(nw["rate_bin_ms"], tau)
    spb = int(round(bin_tau / dt))
    step_tau = s_to_tau(q["step_s"], tau)
    nb_step = int(round(step_tau / bin_tau))
    if spb < 1 or abs(spb * dt - bin_tau) > 1e-9 * bin_tau or abs(nb_step * bin_tau - step_tau) > 1e-9 * step_tau:
        raise C.ConfigError("network.dt_tau must divide the rate bin and the rate bin the step")
    beta = 1.0 / ms_to_tau(m["tau_d_ms"], tau)
    vals = s4_values(cfg)
    order = np.concatenate([vals, vals[::-1]])
    direction = np.concatenate([np.ones(vals.size, dtype=np.int8), np.zeros(vals.size, dtype=np.int8)])
    rng = make_rng(cfg["seeds"]["root_seed"], cfg["seeds"]["spawn_key"])
    lo, hi = nw["init_V_range"]
    V = lo + (hi - lo) * rng.random(N)
    qj = lorentzian_offsets(N, nw["het_sampling"], rng)
    tref, tspk = np.zeros(N), np.zeros(N)
    slot = np.full(N, -1, dtype=np.int32)                      # no raster
    y0 = stable_fixed_point(order[0], m["J"], m["Delta"], m["I_drive"], "M3", ms_to_tau(m["tau_d_ms"], tau))
    s_io = np.array([float(y0[2])])
    rt, ri, rn = np.empty(1), np.empty(1, dtype=np.int32), np.zeros(1, dtype=np.int64)
    counts = np.empty(order.size * nb_step, dtype=np.int64)
    vmean, sout = np.empty_like(counts, dtype=float), np.empty(order.size * nb_step)
    for k, x in enumerate(order):
        V += sv["delta0"]
        b0 = 0
        while b0 < nb_step:
            if deadline is not None and time.monotonic() > deadline:
                raise RunTimeout("wall-time limit reached between kernel chunks")
            nb = min(chunk_bins, nb_step - b0)
            n = nb * spb
            full = lambda c: np.full(n, c, dtype=float)
            a, z = k * nb_step + b0, k * nb_step + b0 + nb
            qif_chunk(V, qj, tref, tspk, s_io, slot, full(x), full(m["J"]), full(m["Delta"]), full(m["I_drive"]),
                      beta, dt, nw["V_peak"], nw["V_reset"], spb, nb, bool(nw["exclude_refractory"]),
                      (k * nb_step + b0) * spb, 0.0, counts[a:z], vmean[a:z], sout[a:z], rt, ri, rn)
            b0 += nb
    n_bins = order.size * nb_step
    arrays = {"t_ms": np.arange(1, n_bins + 1) * bin_tau * tau, "r": counts / (N * bin_tau), "v": vmean, "s": sout,
              "param": np.repeat(order, nb_step), "step": np.repeat(np.arange(order.size, dtype=np.int32), nb_step),
              "step_param": order, "step_up": direction}
    flags = {"scheme": "forward_euler", "dt_tau": dt, "N": N, "param": q["param"], "n_steps": int(order.size),
             "step_s": q["step_s"], "read_s": q["read_s"], "V_peak": nw["V_peak"], "V_reset": nw["V_reset"],
             "het": f"{nw['het_dist']}_{nw['het_sampling']}", "spikes_total": int(counts.sum()),
             "s_start": float(y0[2]), "kick_per_step": True, "float": "float64", "fastmath": False,
             "numba": numba.__version__, "numba_threads_env": os.environ.get("NUMBA_NUM_THREADS"),
             "seed_spawn_key": list(cfg["seeds"]["spawn_key"])}
    return {"arrays": arrays, "message": f"ok; {order.size} steps of {q['step_s']} s", "flags": flags}
