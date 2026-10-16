"""S3 mean-field readouts (plan 6.2 S3, 7.1 K7, K8; MS5 step 5d, DL-116). Analysis only, no integration.

Definitions are ours and UNVERIFIED (the plan gives none): the final window is the last WINDOW_S seconds
cut into N_SUBWINDOWS windows of WINDOW_S / N_SUBWINDOWS seconds; amplitude is the peak-to-peak of the
signal in a window; 'decays' means the final-window peak-to-peak of v is below delta0 (the size of the
initial kick, D26); 'holds' means the sub-window peak-to-peak values stay within HOLD_TOL of their mean
and that mean is above GROWN_FACTOR * delta0. The frequency is the Hann-windowed FFT peak of r over the
final window (zero-padded x PAD), with the mean-crossing count of r as a cross-check.
"""
from __future__ import annotations

import numpy as np

WINDOW_S = 4.0
N_SUBWINDOWS = 4
HOLD_TOL = 0.02          # K7: 'holds within +/- 2%' (Table 7.1)
GROWN_FACTOR = 1000.0
PAD = 8
BAND_HZ = (25.0, 100.0)  # K8 non-blocking band (Table 7.1)


def _final(t_ms, x, window_s=WINDOW_S):
    return x[t_ms >= t_ms[-1] - 1e3 * window_s - 1e-9]


def window_amplitudes(t_ms, x, window_s=WINDOW_S, n=N_SUBWINDOWS):
    """Peak-to-peak of x in each of n consecutive sub-windows of the final window."""
    seg = _final(t_ms, x, window_s)
    return np.array([np.ptp(c) for c in np.array_split(seg, n)])


def peak_frequency_hz(t_ms, x, window_s=WINDOW_S):
    """(FFT peak, mean-crossing frequency) of x over the final window, in Hz; NaN for a flat signal."""
    seg = _final(t_ms, x, window_s)
    dt = (t_ms[1] - t_ms[0]) * 1e-3
    seg = seg - seg.mean()
    if np.ptp(seg) == 0.0:
        return float("nan"), float("nan")
    spec = np.abs(np.fft.rfft(seg * np.hanning(seg.size), n=PAD * seg.size))
    f_fft = float(np.fft.rfftfreq(PAD * seg.size, dt)[1:][np.argmax(spec[1:])])
    up = np.flatnonzero((seg[:-1] < 0) & (seg[1:] >= 0))
    f_cross = float((up.size - 1) / ((up[-1] - up[0]) * dt)) if up.size > 2 else float("nan")
    return f_fft, f_cross


def evaluate_cell(t_ms, r, v, delta0: float) -> dict:
    """Readouts of one constant-parameter run."""
    av, ar = window_amplitudes(t_ms, v), window_amplitudes(t_ms, r)
    mean_v = float(av.mean())
    f_fft, f_cross = peak_frequency_hz(t_ms, r)
    return {"v_ptp_windows": [float(a) for a in av], "r_ptp_windows": [float(a) for a in ar],
            "v_ptp_mean": mean_v, "r_ptp_mean": float(ar.mean()),
            "v_ptp_final_s": float(np.ptp(_final(t_ms, v, 1.0))),
            "decays": bool(np.ptp(_final(t_ms, v, 1.0)) < delta0),
            "hold_dev": float(np.max(np.abs(av / mean_v - 1.0))) if mean_v > 0 else float("nan"),
            "grown": bool(mean_v > GROWN_FACTOR * delta0),
            "f_fft_hz": f_fft, "f_cross_hz": f_cross}


def judge_k7(cells: dict, delta0: float) -> dict:
    """cells: tau_d_ms -> evaluate_cell(...) at ref_ceni. Pass: decays at 3 ms, holds within HOLD_TOL at 8 ms."""
    lo, hi = cells[3.0], cells[8.0]
    holds = bool(hi["grown"] and hi["hold_dev"] <= HOLD_TOL)
    return {"decays_at_3ms": lo["decays"], "v_ptp_final_s_3ms": lo["v_ptp_final_s"],
            "holds_at_8ms": holds, "hold_dev_8ms": hi["hold_dev"], "v_ptp_8ms": hi["v_ptp_mean"],
            "pass": bool(lo["decays"] and holds)}


def judge_k8(cells: dict, delta0: float) -> dict:
    """cells: tau_d_ms -> evaluate_cell(...) at ref_devalle. Blocking: sustained cycle at 5 ms (steady within
    HOLD_TOL, grown), fixed point at 50 ms (decays). Non-blocking: peak frequency in BAND_HZ."""
    on, off = cells[5.0], cells[50.0]
    cycle = bool(on["grown"] and on["hold_dev"] <= HOLD_TOL)
    f = on["f_fft_hz"]
    return {"limit_cycle_at_5ms": cycle, "hold_dev_5ms": on["hold_dev"], "v_ptp_5ms": on["v_ptp_mean"],
            "fixed_point_at_50ms": off["decays"], "v_ptp_final_s_50ms": off["v_ptp_final_s"],
            "f_fft_hz": f, "f_cross_hz": on["f_cross_hz"],
            "in_band": bool(BAND_HZ[0] <= f <= BAND_HZ[1]), "pass": bool(cycle and off["decays"])}


# --- network readouts (MS5 step 5g, DL-119). Definitions are ours and UNVERIFIED; the plan gives K8 only
# 'network peak within 5%' and no network criterion for K7 or K9. ---
K8_NET_TOL = 0.05        # Table 7.1 K8: 'Network peak within 5%'; 'peak' read as the spectral peak frequency (ours)


def sine_fit_ptp(t_ms, x, f_hz, window_s=WINDOW_S):
    """Peak-to-peak (2 A) of the least-squares sinusoid of frequency f_hz fitted to x over the final window."""
    seg, ts = _final(t_ms, x, window_s), _final(t_ms, t_ms, window_s) * 1e-3
    if not np.isfinite(f_hz):
        return float("nan")
    M = np.column_stack([np.ones_like(ts), np.cos(2 * np.pi * f_hz * ts), np.sin(2 * np.pi * f_hz * ts)])
    c = np.linalg.lstsq(M, seg, rcond=None)[0]
    return float(2.0 * np.hypot(c[1], c[2]))


def evaluate_net_cell(t_ms, r, v) -> dict:
    """Readouts of one network run (r_N per bin in 1/tau): final-window mean and std of r_N, peak frequency
    (FFT, crossing count), fitted peak-to-peak at the FFT peak, and the plain peak-to-peak (inflated by the
    finite-N bin noise)."""
    seg = _final(t_ms, r)
    f_fft, f_cross = peak_frequency_hz(t_ms, r)
    return {"r_mean": float(seg.mean()), "r_std": float(seg.std()), "r_ptp": float(np.ptp(seg)),
            "r_fit_ptp": sine_fit_ptp(t_ms, r, f_fft), "v_mean": float(_final(t_ms, v).mean()),
            "f_fft_hz": f_fft, "f_cross_hz": f_cross}


def compare_to_mf(net: dict, mf: dict) -> dict:
    """Difference of a network cell to its mean-field cell (both from evaluate_net_cell / evaluate_cell + fit)."""
    rel = lambda a, b: float((a - b) / b) if b else float("nan")
    return {"f_net_hz": net["f_fft_hz"], "f_mf_hz": mf["f_fft_hz"], "f_diff_hz": net["f_fft_hz"] - mf["f_fft_hz"],
            "f_rel_diff": rel(net["f_fft_hz"], mf["f_fft_hz"]),
            "r_mean_rel_diff": rel(net["r_mean"], mf["r_mean"]),
            "r_fit_ptp_rel_diff": rel(net["r_fit_ptp"], mf["r_fit_ptp"])}


def judge_k8_net(cmp5: dict) -> dict:
    """K8 network (N = 5e4): spectral peak within K8_NET_TOL of the mean-field peak."""
    return {"f_net_hz": cmp5["f_net_hz"], "f_mf_hz": cmp5["f_mf_hz"], "rel_diff": cmp5["f_rel_diff"],
            "tol": K8_NET_TOL, "pass": bool(abs(cmp5["f_rel_diff"]) <= K8_NET_TOL)}
