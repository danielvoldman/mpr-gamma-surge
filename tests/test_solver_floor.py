import numpy as np
import pytest

from mprsurge import config as C
from mprsurge.analysis import solver_floor as SF


def test_kind_registered():
    assert "f11floor" in C.RUN_KINDS


def test_constant_record_has_zero_floor():
    x = np.full(100, -0.59)
    out = SF.floor_summary(x, x, x)
    assert out["dv_max"] == 0.0 and out["dv_rms"] == 0.0


def test_known_departure_is_the_max_and_in_v_units():
    v = np.full(100, -0.5)
    v[40] += 3e-13
    v[-1] += 1e-13
    out = SF.floor_summary(v, np.zeros(100), np.zeros(100))
    assert out["dv_max"] == pytest.approx(3e-13, rel=1e-3)
    assert out["dv_final"] == pytest.approx(1e-13, rel=1e-3)
    assert out["dv_max_second_half"] == pytest.approx(1e-13, rel=1e-3)


def test_bad_input_rejected():
    with pytest.raises(ValueError):
        SF.floor_summary(np.ones(5), np.ones(4), np.ones(5))
    with pytest.raises(ValueError):
        SF.floor_summary(np.array([1, np.nan, 1, 1.0]), np.ones(4), np.ones(4))
