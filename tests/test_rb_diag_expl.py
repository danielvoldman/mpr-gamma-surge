import math

import numpy as np

from mprsurge.analysis import rb_diag_expl as X


def test_perturb_v_one_ulp_each_way():
    y = np.array([0.3, -0.5947, 0.3])
    up, dn = X.perturb_v(y, +1), X.perturb_v(y, -1)
    assert up[1] > y[1] > dn[1]
    assert up[1] - y[1] == abs(np.spacing(y[1])) and y[1] - dn[1] == abs(np.spacing(y[1]))
    assert up[0] == y[0] and up[2] == y[2] and y[1] == -0.5947


def test_predicted_shift_sign_and_size():
    s = X.predicted_shift_s(1e-9, 1e-6, 0.05, 10.0)        # smaller kick: later, ln(1000)/0.05 tau = 138.2 tau = 1.382 s
    assert math.isclose(s, math.log(1000) / 0.05 * 0.01)
    assert X.predicted_shift_s(1e-3, 1e-6, 0.05, 10.0) < 0


def test_pattern_words():
    assert X.pattern([0.9, 1.1]) == "onset moves with the kick as predicted"
    assert X.pattern([0.0, 0.01]) == "onset does not follow the kick (|ratio| below 0.25; sign may be opposite)"
    assert X.pattern([0.0, 1.0]) == "in between"


def test_plateau_floor():
    t = np.linspace(0, 60, 61)
    e = np.where(t < 6, 1.0, 2.0)
    e[10] = 0.0
    f = X.plateau_floor(e, t)
    assert f["n_zero"] == 1 and f["median"] == 2.0
