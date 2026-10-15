"""Mean-field drivers (plan 6.2, 10.4): mode D `run_mf` and mode N `run_mf_noisy`.

Drivers only integrate. Both are runner tasks, task(cfg, deadline) -> dict with
"arrays", "message", "flags" (see run.py).

Mode D: start at the stable fixed point at the path start, add delta0 on v at t_on,
integrate piecewise between the path breakpoints with t_eval on the output grid and no
dense_output. DOP853, with one Radau retry flagged in the record.

Mode N: additive white noise on v, dv = f_v dt + sigma dW, stochastic Heun with step
noise.dt_tau, in a Numba kernel run in chunks (a wall-time check between chunks). The
kernel receives a numpy Generator seeded from the SeedSequence child (spawn key in the
config) and reads no module globals. No prange.

Time is in tau units inside; arrays are written on the output grid, t in ms.

Reading choices (DL-072): a sample at time t includes a kick applied at t; sigma
convention dW; the wall limit in mode D is checked inside the right-hand side.
"""
from __future__ import annotations

import time

import numpy as np
from numba import njit
from scipy.integrate import solve_ivp

from . import config as C
from . import provenance as P
from .errors import RunTimeout
from .models.fixed_points import stable_fixed_point
from .models.mpr2d import rhs_2d
from .models.mpr3d import rhs_3d
from .ramps import Path, make_path
from .units import hz_to_rate, ms_to_tau, s_to_tau

# Devalle 2017 Fig. 3 initial values for K8 and S3 runs (Table 7.1, K8): R(0) = S(0) = 5 Hz,
# V(0) = 0. Passed as y0 by the caller; no config key selects them yet (open, see DL-072).
DEVALLE_FIG3_RATE_HZ = 5.0
DEVALLE_FIG3_V0 = 0.0

CHUNK_OUT_SAMPLES = 2000     # mode N: output samples per kernel call (a coding choice)
_EPS = 1e-9

_PI = np.pi
_PI2 = np.pi ** 2


class SolverFailure(RuntimeError):
    """solve_ivp reported failure (status != 0)."""


# --- shared setup ----------------------------------------------------------------------------

def devalle_fig3_state(model_type: str):
    """(r, v) or (r, v, s) at tau = 10 ms: r = s = 5 Hz as 1/tau, v = 0 (K8, S3)."""
    r = hz_to_rate(DEVALLE_FIG3_RATE_HZ)
    return (r, DEVALLE_FIG3_V0) if model_type == "M2" else (r, DEVALLE_FIG3_V0, r)


def _setup(cfg: dict):
    m = cfg["model"]
    tau = m["tau_ms"]
    path = make_path(cfg)
    tau_d = None if m["tau_d_ms"] is None else ms_to_tau(m["tau_d_ms"], tau)
    if m["type"] == "M3" and tau_d is None:
        raise C.ConfigError("model.tau_d_ms is required for M3")
    hold = s_to_tau(cfg["durations"]["hold_s"], tau)
    t_end = path.t_ramp_end + hold                     # the hold starts after the last ramp (6.2)
    dt_out = ms_to_tau(cfg["solver"]["dt_out_ms"], tau)
    return m["type"], path, tau_d, t_end, dt_out


def _start_state(model: str, path: Path, tau_d, y0):
    if y0 is not None:
        y0 = np.asarray(y0, dtype=float)
        if y0.shape != ((2,) if model == "M2" else (3,)):
            raise ValueError(f"y0 has shape {y0.shape} for model {model}")
        return y0
    t0 = 0.0
    return np.asarray(stable_fixed_point(float(path.eta(t0)), float(path.J(t0)),
                                         float(path.Delta(t0)), float(path.I(t0)),
                                         model, tau_d), dtype=float)


def _output(path: Path, t_tau, Y, tau_ms):
    """Output arrays on the grid: t_ms, r, v, s and the path parameters."""
    r, v = Y[0], Y[1]
    s = Y[2] if Y.shape[0] == 3 else Y[0]
    return {"t_ms": t_tau * tau_ms, "r": r, "v": v, "s": s,
            "eta": np.asarray(path.eta(t_tau), dtype=float),
            "J": np.asarray(path.J(t_tau), dtype=float),
            "Delta": np.asarray(path.Delta(t_tau), dtype=float),
            "I": np.asarray(path.I(t_tau), dtype=float)}


def _grid_range(a: float, b: float, dt: float, last: bool):
    """Integer grid indices k with a <= k dt < b (b included for the last segment)."""
    lo = int(np.ceil(a / dt - _EPS))
    hi = int(np.floor(b / dt + _EPS)) + 1 if last else int(np.ceil(b / dt - _EPS))
    return lo, hi


# --- mode D --------------------------------------------------------------------------------------

def _guarded(f, deadline):
    """Wrap an rhs so that it raises RunTimeout once the deadline has passed (checked
    every 256 calls). Does not change the numerics."""
    if deadline is None:
        return f
    calls = [0]

    def g(t, y):
        calls[0] += 1
        if not calls[0] & 255 and time.monotonic() > deadline:
            raise RunTimeout("wall-time limit reached during solve_ivp")
        return f(t, y)
    return g


def _integrate_d(cfg, model, path, tau_d, t_end, dt_out, y0, method, deadline):
    sv = cfg["solver"]
    delta0 = sv["delta0"]
    if model == "M2":
        def f(t, y):
            return rhs_2d(t, y, float(path.eta(t)), float(path.J(t)), float(path.Delta(t)),
                          float(path.I(t)))
    else:
        def f(t, y):
            return rhs_3d(t, y, float(path.eta(t)), float(path.J(t)), float(path.Delta(t)),
                          tau_d, float(path.I(t)))
    f = _guarded(f, deadline)
    bp = path.breakpoints
    pts = np.unique(np.concatenate([[0.0], bp[(bp > 0.0) & (bp < t_end)], [t_end]]))
    y = np.array(y0, dtype=float)
    ts, Ys, nfev, msgs = [], [], 0, []
    for i in range(len(pts) - 1):
        a, b = float(pts[i]), float(pts[i + 1])
        last = i == len(pts) - 2
        if abs(a - path.t_on) < _EPS:
            y[1] += delta0                                # delta0 on v at t_on (6.2, D26)
        lo, hi = _grid_range(a, b, dt_out, last)
        grid = np.arange(lo, hi) * dt_out
        grid = np.clip(grid, a, b)
        t_eval = grid if (last and grid.size and grid[-1] >= b) else np.append(grid, b)
        sol = solve_ivp(f, (a, b), y, method=method, t_eval=t_eval, rtol=sv["rtol"],
                        atol=sv["atol"], max_step=sv["max_step_tau"])
        if sol.status != 0:
            raise SolverFailure(f"{method}: {sol.message}")
        nfev += sol.nfev
        msgs.append(sol.message)
        n_rec = grid.size
        ts.append(grid)
        Ys.append(sol.y[:, :n_rec])
        y = sol.y[:, -1].copy()
    return np.concatenate(ts), np.concatenate(Ys, axis=1), nfev


def run_mf(cfg: dict, deadline=None, y0=None) -> dict:
    """Mode D (plan 6.2). y0 overrides the stable fixed point (K8/S3: devalle_fig3_state).

    A failed DOP853 run is retried once with Radau and flagged (10.4); a RunTimeout is
    never retried.
    """
    model, path, tau_d, t_end, dt_out = _setup(cfg)
    y_start = _start_state(model, path, tau_d, y0)
    method = cfg["solver"]["method"]
    flags = {"solver": method, "start": "explicit" if y0 is not None else "stable_fixed_point",
             "retried_with_radau": False}
    try:
        t, Y, nfev = _integrate_d(cfg, model, path, tau_d, t_end, dt_out, y_start, method, deadline)
    except SolverFailure as exc:
        if method != "DOP853":
            raise
        flags.update(retried_with_radau=True, first_failure=str(exc), solver="Radau")
        t, Y, nfev = _integrate_d(cfg, model, path, tau_d, t_end, dt_out, y_start, "Radau", deadline)
    flags.update(nfev=int(nfev), y_start=[float(x) for x in y_start])
    msg = "ok" + (" (Radau retry after DOP853 failure)" if flags["retried_with_radau"] else "")
    return {"arrays": _output(path, t, Y, cfg["model"]["tau_ms"]), "message": msg, "flags": flags}


# --- mode N ----------------------------------------------------------------------------------------

@njit(cache=True)
def heun_chunk(y, eta, J, Delta, I, beta, kind, sigma, dt, rng, stride, g0, out):
    """Stochastic Heun, additive noise sigma dW on v, over len(eta) - 1 steps.

    y (r, v, s) is advanced in place. Parameter arrays hold the values at t_i, i = 0..n
    (n + 1 entries). kind 0 = M2 (s = r), 1 = M3 with beta = tau/tau_d, 2 = OU validation
    (dv/dt = -J v, r and s unused). The state at the start of every stride-th step is
    written to out; g0 is the global index of step 0, so the output grid is the same for any
    chunking. One generator, one thread; nothing here reads module state.
    """
    n = eta.shape[0] - 1
    amp = sigma * np.sqrt(dt)
    r = y[0]
    v = y[1]
    s = y[2]
    k = 0
    for i in range(n):
        if (g0 + i) % stride == 0:
            out[k, 0] = r
            out[k, 1] = v
            out[k, 2] = s
            k += 1
        dw = amp * rng.standard_normal()
        if kind == 2:
            f1 = -J[i] * v
            vp = v + dt * f1 + dw
            f2 = -J[i + 1] * vp
            v = v + 0.5 * dt * (f1 + f2) + dw
            continue
        fr1 = Delta[i] / np.pi + 2.0 * r * v
        fv1 = v * v + eta[i] + I[i] + J[i] * s - np.pi * np.pi * r * r
        fs1 = (r - s) * beta
        rp = r + dt * fr1
        vp = v + dt * fv1 + dw
        sp = s + dt * fs1 if kind == 1 else rp
        fr2 = Delta[i + 1] / np.pi + 2.0 * rp * vp
        fv2 = vp * vp + eta[i + 1] + I[i + 1] + J[i + 1] * sp - np.pi * np.pi * rp * rp
        fs2 = (rp - sp) * beta
        r = r + 0.5 * dt * (fr1 + fr2)
        v = v + 0.5 * dt * (fv1 + fv2) + dw
        s = s + 0.5 * dt * (fs1 + fs2) if kind == 1 else r
    y[0] = r
    y[1] = v
    y[2] = s


def warm_up() -> None:
    """Compile and cache the kernel in the parent before the worker pool starts (10.4)."""
    y = np.array([0.1, -1.0, 0.1])
    a = np.zeros(5)
    out = np.zeros((2, 3))
    rng = np.random.Generator(np.random.PCG64(0))
    for kind in (0, 1, 2):
        heun_chunk(y, a, a, a, a, 1.0, kind, 0.0, 1e-3, rng, 4, 0, out)


def make_rng(root_seed: int, spawn_key) -> np.random.Generator:
    """Generator seeded from the SeedSequence child with the stored spawn key (6.6)."""
    if spawn_key is None:
        raise C.ConfigError("seeds.spawn_key is null: a noisy run needs a seed child "
                            "(the runner sets it from the seed index)")
    return np.random.Generator(np.random.PCG64(P.seed_from_key(root_seed, spawn_key)))


def _run_chunks(rng, y, kind, beta, sigma, dt, stride, n_steps, param_fn, kick_step,
                kick_value, chunk_steps, deadline):
    """Drive heun_chunk over steps [0, n_steps]; returns samples at steps 0, stride, ...

    param_fn(t_index_array) -> (eta, J, Delta, I) at those step indices. A kick is added
    to v at step kick_step, before the sample of that step is taken. The deadline is
    checked between chunks (RunTimeout).
    """
    edges = sorted({0, n_steps} | ({kick_step} if 0 < kick_step < n_steps else set()))
    rows = []
    for e0, e1 in zip(edges[:-1], edges[1:]):
        if e0 == kick_step:
            y[1] += kick_value
        g = e0
        while g < e1:
            if deadline is not None and time.monotonic() > deadline:
                raise RunTimeout("wall-time limit reached between kernel chunks")
            n = min(chunk_steps, e1 - g)
            idx = np.arange(g, g + n + 1)
            eta, J, Delta, I = param_fn(idx)
            out = np.empty(((g + n + stride - 1) // stride - (g + stride - 1) // stride, 3))
            heun_chunk(y, eta, J, Delta, I, beta, kind, sigma, dt, rng, stride, g, out)
            rows.append(out)
            g += n
    rows.append(y[None, :].copy())                       # state at step n_steps
    return np.concatenate(rows, axis=0)


def run_mf_noisy(cfg: dict, deadline=None, y0=None, chunk_samples: int = CHUNK_OUT_SAMPLES) -> dict:
    """Mode N (plan 6.2, 6.4): stochastic Heun with additive noise on v.

    The 2 s discard comes before t = 0 and is not returned (6.2, CP14). sigma =
    noise.sigma * noise.sigma_factor; mode N refuses to run with noise.sigma null
    (DL-065). The dW convention, dv = f dt + sigma dW, is UNVERIFIED (DL-072).
    """
    n = cfg["noise"]
    if n["sigma"] is None:
        raise C.ConfigError("noise.sigma is null: it is calibrated at MS5 (DL-065); give it "
                            "explicitly to run mode N")
    sigma = n["sigma"] * n["sigma_factor"]
    model, path, tau_d, t_end, dt_out = _setup(cfg)
    dt = n["dt_tau"]
    stride = int(round(dt_out / dt))
    if stride < 1 or abs(stride * dt - dt_out) > 1e-9 * dt_out:
        raise C.ConfigError(f"noise.dt_tau = {dt} does not divide the output step {dt_out} tau")
    discard = s_to_tau(cfg["durations"]["discard_s"], cfg["model"]["tau_ms"])
    n_disc = int(round(discard / dt_out))
    if abs(n_disc * dt_out - discard) > 1e-9 * max(discard, 1.0):
        raise C.ConfigError("durations.discard_s is not a whole number of output steps")
    n_keep = int(np.floor(t_end / dt_out + _EPS)) + 1
    n_steps = (n_disc + n_keep - 1) * stride
    t0 = -n_disc * dt_out
    y = _start_state(model, path, tau_d, y0)
    y = np.array([y[0], y[1], y[2] if model == "M3" else y[0]])
    kind = 1 if model == "M3" else 0
    beta = 0.0 if tau_d is None else 1.0 / tau_d
    kick_step = int(round((path.t_on - t0) / dt))

    def param_fn(idx):
        t = t0 + idx * dt
        return (np.asarray(path.eta(t), float), np.asarray(path.J(t), float),
                np.asarray(path.Delta(t), float), np.asarray(path.I(t), float))

    rng = make_rng(cfg["seeds"]["root_seed"], cfg["seeds"]["spawn_key"])
    chunk_steps = max(1, int(chunk_samples)) * stride
    S = _run_chunks(rng, y, kind, beta, sigma, dt, stride, n_steps, param_fn, kick_step,
                    cfg["solver"]["delta0"], chunk_steps, deadline)
    S = S[n_disc:].T
    t = np.arange(n_keep) * dt_out
    flags = {"scheme": n["scheme"], "dt_tau": dt, "sigma_used": sigma, "n_steps": n_steps,
             "start": "explicit" if y0 is not None else "stable_fixed_point",
             "seed_spawn_key": list(cfg["seeds"]["spawn_key"])}
    return {"arrays": _output(path, t, S, cfg["model"]["tau_ms"]), "message": "ok", "flags": flags}
