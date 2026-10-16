"""Sigma calibration analysis (plan 6.4, D18, CP21; MS5 step 5h, DL-120). Analysis only: no integration.

Matching rule (ours, the plan gives none, UNVERIFIED): the baseline std of v over the 5 s after the 2 s discard
is computed per run; the mean-field noisy std is taken as linear in sigma through the origin (a stable fixed
point, small noise; checked by `linearity` on two trial sigmas) and sigma is the target std over the std per
unit sigma.
"""
import numpy as np


def baseline_std(v) -> float:
    """Sample std (ddof 1) of a v series, the whole series being the 5 s baseline."""
    v = np.asarray(v, float)
    return float(v.std(ddof=1))


def spread(values) -> dict:
    """Mean, seed-to-seed std (ddof 1) and standard error of a list of per-seed values."""
    x = np.asarray(values, float)
    sd = float(x.std(ddof=1)) if x.size > 1 else float("nan")
    return {"n": int(x.size), "mean": float(x.mean()), "sd": sd, "sem": sd / np.sqrt(x.size) if x.size > 1 else float("nan")}


def slope_through_origin(sigmas, stds) -> float:
    """Least-squares std per unit sigma for std = k sigma."""
    s, y = np.asarray(sigmas, float), np.asarray(stds, float)
    return float((s * y).sum() / (s * s).sum())


def linearity(sigmas, stds) -> float:
    """Largest relative deviation of std/sigma from its mean over the trial points."""
    k = np.asarray(stds, float) / np.asarray(sigmas, float)
    return float(np.max(np.abs(k / k.mean() - 1.0)))


def match_sigma(sigmas, stds, target_std: float) -> float:
    """sigma at which the linear mean-field std equals the target (network) std."""
    return target_std / slope_through_origin(sigmas, stds)
