"""K5 operational definition (DL-082; UNVERIFIED, our own) on the M2 mean field.

I(t) = 3 sin(pi t / 20) from t = 0, eta_bar = -5, J = 15, Delta = 1, started in the low-activity stable node
(MPR 2015 Sec. II.D, single source). Time is the nondimensional tau = 1 (mapping UNVERIFIED). A burst is r crossing the
midpoint of the I = 0 low (node) and high (focus) states. Pass: in each of the last 5 periods after a 2-period
transient there is one up-crossing and one down-crossing, and successive up-crossings are 40 apart within TOL.
"""
import numpy as np
from scipy.integrate import solve_ivp

from mprsurge.models.fixed_points import classify_all
from mprsurge.models.mpr2d import rhs_2d

ETA, J, D = -5.0, 15.0, 1.0
PERIOD = 40.0                       # 2 pi / (pi / 20)
TOL = 0.1                           # UNVERIFIED: one output step, 1 ms = 0.1 tau at tau = 10 ms (DL-082)
DT = 0.1


def k5_run():
    states = {label: y for y, label, _ in classify_all(ETA, J, D, 0.0)}
    low, high = states["stable_node"], states["stable_focus"]
    mid = 0.5 * (low[0] + high[0])
    t = np.arange(0.0, 7 * PERIOD + DT / 2, DT)                       # 2 transient + 5 periods
    s = solve_ivp(lambda tt, y: rhs_2d(tt, y, ETA, J, D, 3.0 * np.sin(np.pi * tt / 20.0)), [0, t[-1]],
                  np.asarray(low, float), method="DOP853", rtol=1e-10, atol=1e-12, t_eval=t)
    return t, s.y[0], mid


def crossings(t, r, mid):
    k_up = np.flatnonzero((r[:-1] < mid) & (r[1:] >= mid))
    k_dn = np.flatnonzero((r[:-1] >= mid) & (r[1:] < mid))
    lin = lambda k: t[k] + (mid - r[k]) / (r[k + 1] - r[k]) * (t[k + 1] - t[k])     # linear interpolation
    return lin(k_up), lin(k_dn)


def test_k5_one_burst_per_period_with_period_40():
    t, r, mid = k5_run()
    up, dn = crossings(t, r, mid)
    for k in range(5):
        lo, hi = (2 + k) * PERIOD, (3 + k) * PERIOD
        assert ((up >= lo) & (up < hi)).sum() == 1 and ((dn >= lo) & (dn < hi)).sum() == 1
    last = up[up >= 2 * PERIOD]
    assert len(last) == 5 and np.all(np.abs(np.diff(last) - PERIOD) <= TOL)
