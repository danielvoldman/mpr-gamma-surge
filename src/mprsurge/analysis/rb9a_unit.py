"""RB9(a), unit-level (11c ruling 6, DL-351): the dimensional right-hand side of plan 3.1 against the non-dimensional mean-field run on a short path_eta ramp.

This is the computation tests/test_units.py::test_rb9a_... asserts on, moved here so that the same code gives the measured value that is stored for citation
(scripts/run_rb9a_unit.py). SCOPE LIMIT, stated with every use of the value: a 1 s path_eta ramp (eta 1 to 4, t_on 0.5 s, baseline 0.5 s, hold 0.5 s), tau = 10 and 20 ms,
M3 at ref_devalle values; not the headline path; the non-dimensional run is made in memory and no run record is written (DL-341).
Metric: for each of r*tau, v, s*tau the maximum absolute difference over the run divided by the maximum absolute value of the non-dimensional variable.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from .. import config as C
from .. import simulate_mf as S
from .. import units
from ..models.fixed_points import stable_fixed_point

TAU_MS_VALUES = (10.0, 20.0)
OVERRIDES = {"path.name": "path_eta", "path.eta_start": 1.0, "path.eta_peak": 4.0, "path.T_ramp_s": 1.0, "path.t_on_s": 0.5,
             "durations.baseline_s": 0.5, "durations.hold_s": 0.5}
SCOPE = "1 s path_eta ramp (eta 1 to 4), tau 10 and 20 ms, M3 at ref_devalle values; not the headline path; no run record (DL-341)"


def max_rel_diff(tau_ms: float) -> dict:
    """{'r', 'v', 's', 'max'}: relative maximum differences of the dimensional run against the non-dimensional run at this tau."""
    cfg = C.resolve_config(None, {"model.tau_ms": tau_ms, **OVERRIDES})
    res = S.run_mf(cfg)["arrays"]
    m, p = cfg["model"], cfg["path"]
    tau, tau_d = tau_ms, m["tau_d_ms"]
    t_on, T = p["t_on_s"] * 1e3, p["T_ramp_s"] * 1e3
    eta = lambda t: p["eta_start"] + (p["eta_peak"] - p["eta_start"]) * min(max((t - t_on) / T, 0.0), 1.0)

    def f(t, y):
        r, v, s = y
        return [(m["Delta"] / (np.pi * tau) + 2 * r * v) / tau,
                (v * v + eta(t) + m["J"] * tau * s + m["I_drive"] - (np.pi * tau * r) ** 2) / tau,
                (r - s) / tau_d]
    r0, v0, s0 = stable_fixed_point(p["eta_start"], m["J"], m["Delta"], m["I_drive"], "M3", units.ms_to_tau(tau_d, tau))
    y = [r0 / tau, v0, s0 / tau]
    t_end = res["t_ms"][-1]
    t_all, Y = [], []
    for a, b in ((0.0, t_on), (t_on, t_on + T), (t_on + T, t_end)):
        if a == t_on:
            y[1] += cfg["solver"]["delta0"]
        grid = res["t_ms"][(res["t_ms"] >= a - 1e-9) & (res["t_ms"] < b - 1e-9)]
        if b == t_end:
            grid = res["t_ms"][res["t_ms"] >= a - 1e-9]
        sol = solve_ivp(f, (a, b), y, method="DOP853", rtol=1e-10, atol=1e-13, t_eval=np.append(grid, b) if b != t_end else grid, max_step=0.5 * tau)
        n = len(grid)
        t_all.append(grid)
        Y.append(sol.y[:, :n])
        y = list(sol.y[:, -1])
    Yd = np.concatenate(Y, axis=1)
    if np.concatenate(t_all).shape != res["t_ms"].shape:
        raise RuntimeError("dimensional and non-dimensional output grids differ")
    out = {k: float(np.max(np.abs(dim - nd)) / np.max(np.abs(nd))) for k, dim, nd in (("r", Yd[0] * tau, res["r"]), ("v", Yd[1], res["v"]), ("s", Yd[2] * tau, res["s"]))}
    out["max"] = max(out["r"], out["v"], out["s"])
    return out


def all_taus() -> dict:
    per = {str(t): max_rel_diff(t) for t in TAU_MS_VALUES}
    return {"per_tau": per, "max_rel_diff": max(v["max"] for v in per.values())}
