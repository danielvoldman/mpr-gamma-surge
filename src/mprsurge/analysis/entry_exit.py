"""7g: entry-exit prediction and RB3(a) range along the S5 paths (plan 5.2 A4 last sentence, A7; Table 7.2 RB3, RB6).

Analysis only, no integration. Along a path the leading eigenvalue lambda(eta(t), J(t)) of the M3 fixed point at the
instantaneous parameters is evaluated on nodes taken from the A4 eta grid (the 'A4 grid step' h, UNVERIFIED, its value is
for the owner); I(t) = int_{t_on}^t Re lambda dt' is accumulated by the trapezoid rule; after the last path corner the
parameters are constant, so Re lambda is constant and I is extended analytically.

  t_pred : first t with delta_0 exp(I(t)) = threshold (0.1 x A_ref, A5 reading chosen in DL-138/DL-139, for 7h sign-off)
  range  : delta_0 exp(I(t)) >= floor for every t in [t_on, t_pred] (plan A7 Check). The minimum of I over that interval is
           the decay accumulated before the Hopf crossing, so the range is a bound on T_ramp.

Scaling: the nodes, the corners and the ramp part of I scale with T_ramp, so I_min is proportional to T_ramp and
T_max(floor) = T ln(delta_0 / floor) / (-I_min); this is a check on the code and the way the bound is read off, not an assumption.
The floor values are inputs: nothing here chooses one.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import solve_continuous_lyapunov

from .. import ramps
from ..models.fixed_points import fixed_points
from ..models.mpr3d import jacobian_3d
from ..units import s_to_tau

GRID_ORIGIN = -10.0     # lower end of the A4 eta grid (configs/A4_grids.yaml, eta_bar.lo)


def leading_re(eta, J, Delta, tau_d_tau):
    """Max Re of the eigenvalues at the (unique for J <= 0) fixed point of M3 at these parameters."""
    y = fixed_points(eta, J, Delta, model="M3")[0]
    return float(np.linalg.eigvals(jacobian_3d(y, J, tau_d_tau)).real.max())


def _inverse_profile(name, k, y):
    """x with g(x) = y for the linear or logistic profile of ramps.py."""
    y = np.clip(np.asarray(y, dtype=float), 0.0, 1.0)
    if name == "linear":
        return y
    lo, hi = ramps._logistic(-k / 2.0), ramps._logistic(k / 2.0)
    z = lo + y * (hi - lo)
    return 0.5 + np.log(z / (1.0 - z)) / k


def node_times(cfg, path, h):
    """Sorted node times (tau): t_on, every A4 grid level of eta between eta_start and eta_peak on the way up (and down for
    P5), all path corners, and for P2 equally spaced nodes (the time of one grid step at the mean ramp rate) from the end of
    the eta ramp to the end of the J ramp."""
    p = cfg["path"]
    T, t_on = s_to_tau(p["T_ramp_s"], cfg["model"]["tau_ms"]), path.t_on
    e0, e1 = p["eta_start"], p["eta_peak"]
    k0 = int(np.floor((min(e0, e1) - GRID_ORIGIN) / h)) + 1
    k1 = int(np.ceil((max(e0, e1) - GRID_ORIGIN) / h)) - 1
    lv = GRID_ORIGIN + h * np.arange(k0, k1 + 1)
    lv = lv[(lv > min(e0, e1)) & (lv < max(e0, e1))]
    x = _inverse_profile(p["profile"], p["sigmoid_k"], (lv - e0) / (e1 - e0))
    nodes = [path.breakpoints, t_on + T * x]
    if p["name"] == "path_updown":
        nodes.append(t_on + 2.0 * T - T * x)
    if path.t_ramp_end > t_on + T and p["name"] != "path_updown":
        step = T * h / abs(e1 - e0)
        nodes.append(np.arange(t_on + T, path.t_ramp_end, step))
    nodes.append([t_on, path.t_ramp_end])
    return np.unique(np.concatenate([np.atleast_1d(np.asarray(a, dtype=float)) for a in nodes]))


def cumulative_gain(t, re):
    """I[k] = int_{t[0]}^{t[k]} re dt, trapezoid rule on the nodes."""
    return np.concatenate([[0.0], np.cumsum(0.5 * (re[1:] + re[:-1]) * np.diff(t))])


def t_pred_from(t, re, I, delta0, threshold):
    """First time delta0 exp(I) = threshold, linear in I between nodes, extended with constant re[-1] after the last node.
    Returns (t_pred or None, index of the node interval)."""
    L = np.log(threshold / delta0)
    hit = np.nonzero(I >= L)[0]
    if hit.size:
        k = int(hit[0])
        if k == 0:
            return float(t[0]), 0
        f = (L - I[k - 1]) / (I[k] - I[k - 1])
        return float(t[k - 1] + f * (t[k] - t[k - 1])), k
    if re[-1] > 0.0:
        return float(t[-1] + (L - I[-1]) / re[-1]), len(t)
    return None, len(t)


def path_gain(cfg, h, lam_fn=None):
    """Nodes, Re lambda and I along the configured path for A4 grid step h: (path, t, re, I)."""
    path = ramps.make_path(cfg)
    m = cfg["model"]
    tau_d_tau = m["tau_d_ms"] / m["tau_ms"]
    lam = lam_fn or (lambda eta, J: leading_re(eta, J, m["Delta"], tau_d_tau))
    t = node_times(cfg, path, h)
    eta, J = np.asarray(path.eta(t), float), np.asarray(path.J(t), float)
    re = np.array([lam(a, b) for a, b in zip(eta, J)])
    return path, t, re, cumulative_gain(t, re)


def entry_exit(cfg, path, t, re, I, delta0, threshold, h):
    """t_pred and the range quantities for one delta_0 (tau units for times). tol_step is the time of one grid step in eta at
    the local ramp rate at t_pred (None when eta is constant there, e.g. on the hold or in the J tail)."""
    tp, k = t_pred_from(t, re, I, delta0, threshold)
    out = {"t_on": path.t_on, "t_end": path.t_ramp_end, "n_nodes": int(t.size), "t_pred": tp, "re_final": float(re[-1]),
           "I_min_all": float(min(I.min(), 0.0))}
    if tp is None:
        out.update(I_min=out["I_min_all"], eta_on=None, delay_eta=None, in_run=False, tol_step=None)
        return out
    out["I_min"] = float(min(I[:max(k, 1)].min(), 0.0))
    eta_on = float(path.eta(tp))
    d = 1e-3 * path.t_ramp_end
    rate = abs(float(path.eta(tp + d)) - float(path.eta(tp - d))) / (2.0 * d)
    hold_end = path.t_ramp_end + s_to_tau(cfg["durations"]["hold_s"], cfg["model"]["tau_ms"])
    out.update(eta_on=eta_on, delay_eta=eta_on - cfg["path"]["eta_H"], in_run=bool(tp <= hold_end),
               tol_step=(h / rate if rate > 1e-12 and tp <= path.t_ramp_end else None))
    return out


def inside_range(delta0, I_min, floor):
    """The A7 range test: delta0 exp(I) stays at or above the floor until t_pred."""
    return bool(delta0 * np.exp(I_min) >= floor)


def t_ramp_max(T, I_min, delta0, floor):
    """Largest T_ramp (same unit as T) inside the range, from the scaling I_min proportional to T."""
    return float(T * np.log(delta0 / floor) / (-I_min)) if I_min < 0.0 else float("inf")


def stationary_std_v(eta, J, Delta, tau_d_tau, sigma=1.0):
    """Stationary std of v for the linearisation at the fixed point with additive noise sigma dW on v only (mode N,
    dv = f dt + sigma dW, tau units, DL-072 convention UNVERIFIED): Lyapunov equation A X + X A^T + sigma^2 e_v e_v^T = 0."""
    y = fixed_points(eta, J, Delta, model="M3")[0]
    A = jacobian_3d(y, J, tau_d_tau)
    Q = np.zeros((3, 3))
    Q[1, 1] = sigma ** 2
    X = solve_continuous_lyapunov(A, -Q)
    return float(np.sqrt(X[1, 1]))
