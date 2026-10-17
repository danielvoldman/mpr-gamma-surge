"""S4 step readouts (plan 6.2 S4; MS6 step 6c, DL-127). Analysis only, no integration.

Definitions are ours and UNVERIFIED (the plan gives none). For each step the last read_s seconds are read out:
v and r peak-to-peak, v mean, the Hann-windowed FFT peak and the mean-crossing frequency of r (analysis.s3), and
the settling drift = peak-to-peak of v in the second half of the read window over that of the first half, minus 1
(0 for a settled cycle). `decays` means the read-window peak-to-peak of v is below delta0 (as analysis.s3).
Branch comparison (up against down at the same value) is reported as numbers; no verdict is made here (6e).
"""
from __future__ import annotations

import numpy as np

from . import s3


def step_table(arrays: dict, read_s: float, delta0: float) -> dict:
    """Per-step arrays (one entry per step, in run order) from the series written by simulate_mf.run_s4."""
    t, r, v, k = arrays["t_ms"], arrays["r"], arrays["v"], arrays["step"]
    n = int(arrays["step_param"].size)
    cols = {c: np.full(n, np.nan) for c in ("v_ptp", "r_ptp", "v_mean", "f_fft_hz", "f_cross_hz", "drift")}
    for i in range(n):
        m = k == i
        ti, ri, vi = t[m], r[m], v[m]
        cut = ti >= ti[-1] - 1e3 * read_s - 1e-9
        ti, ri, vi = ti[cut], ri[cut], vi[cut]
        half = ti.size // 2
        cols["v_ptp"][i], cols["r_ptp"][i], cols["v_mean"][i] = np.ptp(vi), np.ptp(ri), vi.mean()
        cols["f_fft_hz"][i], cols["f_cross_hz"][i] = s3.peak_frequency_hz(ti, ri, read_s)
        a, b = np.ptp(vi[:half]), np.ptp(vi[half:])
        cols["drift"][i] = b / a - 1.0 if a > 0 else np.nan
    out = {"step": np.arange(n), "param": np.asarray(arrays["step_param"], dtype=float),
           "up": np.asarray(arrays["step_up"], dtype=np.int8), **cols}
    out["decays"] = cols["v_ptp"] < delta0
    return out


def branch_pairs(table: dict) -> dict:
    """Up and down values at each sweep value: arrays over the n values in up order (the down step of value i is
    step 2n - 1 - i). Reports the differences; no judgement."""
    n = table["step"].size // 2
    up = {c: table[c][:n] for c in ("param", "v_ptp", "f_fft_hz")}
    dn = {c: table[c][n:][::-1] for c in ("param", "v_ptp", "f_fft_hz")}
    if not np.allclose(up["param"], dn["param"]):
        raise ValueError("down steps are not the up values in reverse")
    return {"param": up["param"], "v_ptp_up": up["v_ptp"], "v_ptp_down": dn["v_ptp"],
            "f_up_hz": up["f_fft_hz"], "f_down_hz": dn["f_fft_hz"],
            "v_ptp_rel_diff": np.where(up["v_ptp"] > 0, (dn["v_ptp"] - up["v_ptp"]) / np.where(up["v_ptp"] > 0, up["v_ptp"], 1), np.nan)}
