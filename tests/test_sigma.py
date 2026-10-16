"""Sigma calibration analysis (MS5 step 5h, DL-120): std on a synthetic series and the matching routine on a toy."""
import numpy as np
import pytest

from mprsurge import run as R
from mprsurge.analysis import sigma as S


def test_baseline_std_synthetic():
    v = 0.3 * np.random.default_rng(1).standard_normal(200000) + 5.0
    assert S.baseline_std(v) == pytest.approx(0.3, rel=0.01)


def test_match_sigma_toy():
    sig = [0.001, 0.01]
    std = [0.6 * s for s in sig]
    assert S.linearity(sig, std) < 1e-12
    assert S.match_sigma(sig, std, 0.03) == pytest.approx(0.05)
    assert S.linearity([1.0, 2.0], [1.0, 3.0]) > 0.1


def test_spread():
    d = S.spread([1.0, 2.0, 3.0])
    assert d["mean"] == 2.0 and d["sd"] == 1.0 and d["sem"] == pytest.approx(1 / np.sqrt(3))


def test_configs():
    n, m = R.build_plan("configs/sigma_net.yaml"), R.build_plan("configs/sigma_mf.yaml")
    assert len(n.cells) == 10 and len(m.cells) == 20
    for c in (*n.cells, *m.cells):
        assert c["cfg"]["model"]["eta_bar"] == pytest.approx(2.8960461989737856 - 1.5)
        assert c["cfg"]["durations"]["hold_s"] == 5.0 and c["cfg"]["durations"]["discard_s"] == 2.0
