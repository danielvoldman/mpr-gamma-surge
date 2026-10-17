"""DL-132: linear frequency at ref_devalle: 32.01 Hz at the Hopf point, 36.07 Hz at eta_bar 4 (the 36.1 Hz of DL-115)."""
import pytest

from mprsurge.analysis.hopf import _hz, leading_mode

ETA_H = 2.8960461989737856


def _hz_at(eta):
    return _hz(leading_mode(eta, -21.0, 0.3, 0.5)["pair_im"], 10.0)


def test_freq_at_hopf_point():
    assert _hz_at(ETA_H) == pytest.approx(32.01, abs=0.01)


def test_freq_at_eta_bar_4_is_the_36p1():
    assert _hz_at(4.0) == pytest.approx(36.07, abs=0.01)
