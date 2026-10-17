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
from .models.fixed_points import classify_all, fixed_points, stable_fixed_point
from .models.mpr2d import rhs_2d
from .models.mpr3d import jacobian_3d, rhs_3d
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
    I_start = path.meta.get("I_start", float(path.I(t0)))      # forcing paths start before the step
    return np.asarray(stable_fixed_point(float(path.eta(t0)), float(path.J(t0)),
                                         float(path.Delta(t0)), I_start,
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
    return np.concatenate(ts), np.concatenate(Ys, axis=1), nfev, msgs


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
        t, Y, nfev, msgs = _integrate_d(cfg, model, path, tau_d, t_end, dt_out, y_start, method, deadline)
    except SolverFailure as exc:
        if method != "DOP853":
            raise
        flags.update(retried_with_radau=True, first_failure=str(exc), solver="Radau")
        t, Y, nfev, msgs = _integrate_d(cfg, model, path, tau_d, t_end, dt_out, y_start, "Radau", deadline)
    solver_messages = list(dict.fromkeys(msgs))                # distinct solver messages of the final solve (10.4)
    flags.update(nfev=int(nfev), y_start=[float(x) for x in y_start], solver_messages=solver_messages)
    msg = "ok" + (" (Radau retry after DOP853 failure)" if flags["retried_with_radau"] else "")
    msg += "; solver: " + " | ".join(solver_messages)
    return {"arrays": _output(path, t, Y, cfg["model"]["tau_ms"]), "message": msg, "flags": flags}


def low_rate_node(cfg: dict):
    """The stable node of M2 at the model's (eta_bar, J, Delta, I_drive): the low-activity start state
    of S1 (K4, K5; DL-079, DL-082). Raises if there is not exactly one."""
    m = cfg["model"]
    if m["type"] != "M2":
        raise C.ConfigError("run.kind s1 is an M2 run")
    nodes = [y for y, label, _ in classify_all(m["eta_bar"], m["J"], m["Delta"], m["I_drive"])
             if label == "stable_node"]
    if len(nodes) != 1:
        raise ValueError(f"expected exactly one stable node at the S1 point, found {len(nodes)}")
    return np.asarray(nodes[0], dtype=float)


def run_s1(cfg: dict, deadline=None) -> dict:
    """Runner task for run.kind = s1 (MS2, DL-088): mode D from the low-rate stable node, which a
    bistable point does not give to the default start. K8/S3 start-state selection stays at MS5."""
    out = run_mf(cfg, deadline, y0=low_rate_node(cfg))
    out["flags"]["start"] = "low_rate_stable_node"
    return out


def run_s3(cfg: dict, deadline=None) -> dict:
    """Runner task for run.kind = s3 (MS5 5d, DL-116): mode D at constant parameters (path I_step with
    I_amp = 0). ref_devalle starts from Devalle's Fig. 3 state (K8, Table 7.1); any other point starts at
    its single fixed point whatever its stability, plus delta0 on v at t_on = 0 (D26), because the K7 fixed
    point is unstable at 8 ms and stable_fixed_point would refuse it."""
    m = cfg["model"]
    if cfg["path"]["name"] not in C.FORCING_PATH_NAMES or cfg["path"]["I_amp"] != 0.0:
        raise C.ConfigError("run.kind s3 is a constant-parameter run: path I_step with I_amp = 0")
    if m["ref_point"] == "ref_devalle":
        y0, start = np.asarray(devalle_fig3_state(m["type"]), dtype=float), "devalle_fig3"
    else:
        tau_d = ms_to_tau(m["tau_d_ms"], m["tau_ms"])
        fps = classify_all(m["eta_bar"], m["J"], m["Delta"], m["I_drive"], m["type"], tau_d)
        if len(fps) != 1:
            raise ValueError(f"s3: expected one fixed point, found {len(fps)}")
        y0, start = np.asarray(fps[0][0], dtype=float), "fixed_point_" + fps[0][1]
    out = run_mf(cfg, deadline, y0=y0)
    out["flags"]["start"] = start
    out["flags"]["fixed_point"] = [float(x) for x in y0] if start != "devalle_fig3" else None
    return out


def s4_values(cfg: dict) -> np.ndarray:
    """Sweep values in up order: s4.values, or path.eta_H + linspace(span, n_points) (eta_H from A4, not typed);
    s4.indices, if given, keeps those positions of that grid (6d, DL-128)."""
    q = cfg["s4"]
    if q.get("values") is not None:
        vals = np.asarray(q["values"], dtype=float)
    else:
        if q.get("span") is None or q.get("n_points") is None or cfg["path"]["eta_H"] is None:
            raise C.ConfigError("run.kind s4: give s4.values, or s4.span and s4.n_points with path.eta_H")
        if q["param"] != "eta_bar":
            raise C.ConfigError("s4.span is an offset from eta_H and needs s4.param = eta_bar")
        vals = cfg["path"]["eta_H"] + np.linspace(q["span"][0], q["span"][1], q["n_points"])
    return vals if q.get("indices") is None else vals[np.asarray(q["indices"], dtype=int)]


def run_s4(cfg: dict, deadline=None) -> dict:
    """Runner task for run.kind = s4 (MS6 6c, DL-127; plan 6.2 S4, mean field): quasi-static sweep of one parameter
    (eta_bar or tau_d_ms), up through s4.values then down through them again (the top value is run twice, so 2 n steps),
    each step s4.step_s long. Start: the stable fixed point at the first value. The state is carried from step to step;
    delta0 is added to v at the start of every step (D26 applied per step, so an unstable fixed point is left; UNVERIFIED
    reading). Constant parameters inside a step, DOP853 as run_mf. The series is returned whole; step readouts are made
    by analysis.s4 (UNVERIFIED definitions)."""
    m, sv, q = cfg["model"], cfg["solver"], cfg["s4"]
    if m["type"] != "M3":
        raise C.ConfigError("run.kind s4 is an M3 run")
    tau = m["tau_ms"]
    vals = s4_values(cfg)
    order = np.concatenate([vals, vals[::-1]])
    direction = np.concatenate([np.ones(vals.size, dtype=np.int8), np.zeros(vals.size, dtype=np.int8)])
    n_steps = order.size
    dt_out, step_tau = ms_to_tau(sv["dt_out_ms"], tau), s_to_tau(q["step_s"], tau)
    n_out = int(round(step_tau / dt_out))
    method = sv["method"]

    def point(x):
        eta_bar = x if q["param"] == "eta_bar" else m["eta_bar"]
        tau_d = ms_to_tau(x if q["param"] == "tau_d_ms" else m["tau_d_ms"], tau)
        return eta_bar, tau_d

    eta_bar, tau_d = point(order[0])
    y = np.asarray(stable_fixed_point(eta_bar, m["J"], m["Delta"], m["I_drive"], "M3", tau_d), dtype=float)
    y_start = [float(x) for x in y]
    T, R, V, S, X, K = [], [], [], [], [], []
    nfev = 0
    for k in range(n_steps):
        eta_bar, tau_d = point(order[k])
        f = _guarded(lambda t, y, a=eta_bar, d=tau_d: rhs_3d(t, y, a, m["J"], m["Delta"], d, m["I_drive"]), deadline)
        y = y.copy()
        y[1] += sv["delta0"]
        t0 = k * step_tau
        grid = t0 + np.arange(1, n_out + 1) * dt_out
        sol = solve_ivp(f, (t0, t0 + step_tau), y, method=method, t_eval=grid, rtol=sv["rtol"], atol=sv["atol"],
                        max_step=sv["max_step_tau"])
        if sol.status != 0:
            raise SolverFailure(f"step {k}: {method}: {sol.message}")
        nfev += sol.nfev
        y = sol.y[:, -1]
        T.append(grid * tau); R.append(sol.y[0]); V.append(sol.y[1]); S.append(sol.y[2])
        X.append(np.full(n_out, order[k])); K.append(np.full(n_out, k, dtype=np.int32))
    arrays = {"t_ms": np.concatenate(T), "r": np.concatenate(R), "v": np.concatenate(V), "s": np.concatenate(S),
              "param": np.concatenate(X), "step": np.concatenate(K), "step_param": order, "step_up": direction}
    flags = {"solver": method, "param": q["param"], "n_steps": int(n_steps), "step_s": q["step_s"], "read_s": q["read_s"],
             "nfev": int(nfev), "y_start": y_start, "kick_per_step": True}
    return {"arrays": arrays, "message": f"ok; {n_steps} steps of {q['step_s']} s", "flags": flags}


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


@njit(cache=True)
def heun_chunk_z(y, eta, J, Delta, I, beta, kind, sigma, dt, z, stride, g0, out):
    """heun_chunk with the standard-normal draws supplied: step i uses amp * z[i], amp = sigma sqrt(dt) (len(z) = len(eta) - 1).

    The arithmetic is that of heun_chunk line for line, so z = rng.standard_normal(n) from the same generator reproduces it bit for
    bit (tests/test_ms8_coupling.py). Used by the coupled Heun ladder (F-14, MS8 8b); kind 2 (OU) is not supported."""
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
        dw = amp * z[i]
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


def coupled_normals(rng, n: int, m: int) -> np.ndarray:
    """n standard normals for steps of dt that are m times the base step dt_f = dt / m (F-14, M-10).

    Draws n*m normals z_j for the base step, in stream order, and returns the sum of each block of m divided by sqrt(m): the
    Brownian increment of a coarse step is the sum of the m fine increments inside it, sqrt(dt_f) * sum z_j = sqrt(dt) * result.
    For m = 1 this is rng.standard_normal(n). The stream consumed depends only on the number of fine steps, not on the chunking."""
    z = rng.standard_normal(n * m)
    return z if m == 1 else z.reshape(n, m).sum(axis=1) / np.sqrt(m)


def warm_up() -> None:
    """Compile and cache the kernel in the parent before the worker pool starts (10.4)."""
    y = np.array([0.1, -1.0, 0.1])
    a = np.zeros(5)
    out = np.zeros((2, 3))
    rng = np.random.Generator(np.random.PCG64(0))
    for kind in (0, 1, 2):
        heun_chunk(y, a, a, a, a, 1.0, kind, 0.0, 1e-3, rng, 4, 0, out)
    heun_chunk_z(y, a, a, a, a, 1.0, 1, 0.0, 1e-3, np.zeros(4), 4, 0, out)


def make_rng(root_seed: int, spawn_key) -> np.random.Generator:
    """Generator seeded from the SeedSequence child with the stored spawn key (6.6)."""
    if spawn_key is None:
        raise C.ConfigError("seeds.spawn_key is null: a noisy run needs a seed child "
                            "(the runner sets it from the seed index)")
    return np.random.Generator(np.random.PCG64(P.seed_from_key(root_seed, spawn_key)))


def _run_chunks(rng, y, kind, beta, sigma, dt, stride, n_steps, param_fn, kick_step,
                kick_value, chunk_steps, deadline, couple_m=None):
    """Drive heun_chunk over steps [0, n_steps]; returns samples at steps 0, stride, ...

    param_fn(t_index_array) -> (eta, J, Delta, I) at those step indices. A kick is added
    to v at step kick_step, before the sample of that step is taken. The deadline is
    checked between chunks (RunTimeout). couple_m (F-14): each step's normal is the scaled sum of couple_m draws of a step
    dt / couple_m (coupled_normals), so rungs of one stream share their Brownian path.
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
            if couple_m is None:
                heun_chunk(y, eta, J, Delta, I, beta, kind, sigma, dt, rng, stride, g, out)
            else:
                heun_chunk_z(y, eta, J, Delta, I, beta, kind, sigma, dt, coupled_normals(rng, n, couple_m), stride, g, out)
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
    couple_m = None
    if n.get("coupling_dt_tau") is not None:                      # F-14, MS8 8b: dt_tau must be a whole multiple of the fine step
        couple_m = int(round(dt / n["coupling_dt_tau"]))
        if couple_m < 1 or abs(couple_m * n["coupling_dt_tau"] - dt) > 1e-9 * dt:
            raise C.ConfigError(f"noise.dt_tau = {dt} is not a whole multiple of noise.coupling_dt_tau = {n['coupling_dt_tau']}")

    def param_fn(idx):
        t = t0 + idx * dt
        return (np.asarray(path.eta(t), float), np.asarray(path.J(t), float),
                np.asarray(path.Delta(t), float), np.asarray(path.I(t), float))

    rng = make_rng(cfg["seeds"]["root_seed"], cfg["seeds"]["spawn_key"])
    chunk_steps = max(1, int(chunk_samples)) * stride
    S = _run_chunks(rng, y, kind, beta, sigma, dt, stride, n_steps, param_fn, kick_step,
                    cfg["solver"]["delta0"], chunk_steps, deadline, couple_m)
    S = S[n_disc:].T
    t = np.arange(n_keep) * dt_out
    flags = {"scheme": n["scheme"], "dt_tau": dt, "coupling_dt_tau": n.get("coupling_dt_tau"), "sigma_used": sigma, "n_steps": n_steps,
             "start": "explicit" if y0 is not None else "stable_fixed_point",
             "seed_spawn_key": list(cfg["seeds"]["spawn_key"])}
    return {"arrays": _output(path, t, S, cfg["model"]["tau_ms"]), "message": "ok", "flags": flags}


def run_s5_baseline(cfg: dict, deadline=None) -> dict:
    """Runner task for run.kind = s5base (MS7 7d, DL-141; plan Table 6.2 S5, baseline-only mode N).

    One cell, seeds.n_seeds seeds in one call: constant parameters (the path value before t_on: eta_start, J0, Delta,
    I_drive), no kick, no ramp. Start: the one fixed point at those parameters (the 2 s discard then settles it, so an
    unstable start is allowed and is recorded in flags, not refused; UNVERIFIED reading). The 2 s discard comes before
    t = 0 and is not returned; durations.baseline_s is kept, on the 1 ms output grid including t = 0 and t = baseline_s
    (the same grid as a ramp run up to t_on). Seed s has spawn_key seeds.spawn_key + [s] and the stream does not depend
    on the cell. Arrays: t_ms, v and r (n_seeds x n_samples), y_start.
    """
    n = cfg["noise"]
    if n["sigma"] is None:
        raise C.ConfigError("noise.sigma is null: mode N needs it")
    sigma = n["sigma"] * n["sigma_factor"]
    model, path, tau_d, _, dt_out = _setup(cfg)
    if model != "M3":
        raise C.ConfigError("run.kind s5base is an M3 run")
    tau = cfg["model"]["tau_ms"]
    dt = n["dt_tau"]
    stride = int(round(dt_out / dt))
    if stride < 1 or abs(stride * dt - dt_out) > 1e-9 * dt_out:
        raise C.ConfigError(f"noise.dt_tau = {dt} does not divide the output step {dt_out} tau")
    n_disc = int(round(s_to_tau(cfg["durations"]["discard_s"], tau) / dt_out))
    n_keep = int(np.floor(s_to_tau(cfg["durations"]["baseline_s"], tau) / dt_out + _EPS)) + 1
    n_steps = (n_disc + n_keep - 1) * stride
    eta0, J0, D0, I0 = (float(f(0.0)) for f in (path.eta, path.J, path.Delta, path.I))
    fp = fixed_points(eta0, J0, D0, I0, model="M3")
    if len(fp) != 1:
        raise C.ConfigError(f"{len(fp)} fixed points at eta_bar={eta0}, J={J0}, Delta={D0}: the baseline needs one")
    y_start = np.asarray(fp[0], dtype=float)
    ev = np.linalg.eigvals(jacobian_3d(y_start, J0, tau_d))
    beta = 1.0 / tau_d
    prefix = list(cfg["seeds"]["spawn_key"])

    def param_fn(idx):
        k = idx.size
        return np.full(k, eta0), np.full(k, J0), np.full(k, D0), np.full(k, I0)

    V, R = [], []
    for s in range(cfg["seeds"]["n_seeds"]):
        rng = make_rng(cfg["seeds"]["root_seed"], prefix + [s])
        S = _run_chunks(rng, y_start.copy(), 1, beta, sigma, dt, stride, n_steps, param_fn, -1, 0.0,
                        CHUNK_OUT_SAMPLES * stride, deadline)
        S = S[n_disc:].T
        R.append(S[0]); V.append(S[1])
    arrays = {"t_ms": np.arange(n_keep) * dt_out * tau, "v": np.array(V), "r": np.array(R), "y_start": y_start}
    flags = {"scheme": n["scheme"], "dt_tau": dt, "sigma_used": sigma, "n_steps_per_seed": n_steps, "n_seeds": len(V),
             "seed_spawn_keys": [prefix + [s] for s in range(len(V))], "n_samples": n_keep,
             "start": {"eta_bar": eta0, "J": J0, "Delta": D0, "r": float(y_start[0]), "v": float(y_start[1]),
                       "re_max": float(ev.real.max()), "stable": bool(np.all(ev.real < 0)),
                       "complex_pair": bool(np.any(np.abs(ev.imag) > 1e-12))}}
    return {"arrays": arrays, "message": f"ok; {len(V)} seeds x {n_keep} samples", "flags": flags}
