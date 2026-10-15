"""Unit conversions (plan section 3.3).

All code integrates in units of the membrane time constant tau and converts
to ms, s and Hz only at output. With tau = 10 ms: t_ms = 10 t_tau,
f_Hz = 100 f_tau (cycles per tau), r_Hz = 100 r_tau.
"""
from __future__ import annotations

TAU_MS = 10.0  # model.tau_ms baseline (Table 3.2: fixed)


def tau_to_ms(t_tau, tau_ms: float = TAU_MS):
    """Time in tau units -> ms."""
    return t_tau * tau_ms


def ms_to_tau(t_ms, tau_ms: float = TAU_MS):
    """Time in ms -> tau units."""
    return t_ms / tau_ms


def s_to_tau(t_s, tau_ms: float = TAU_MS):
    """Time in s -> tau units (1 min = 6000 tau at tau = 10 ms)."""
    return t_s * 1000.0 / tau_ms


def tau_to_s(t_tau, tau_ms: float = TAU_MS):
    """Time in tau units -> s."""
    return t_tau * tau_ms / 1000.0


def rate_to_hz(r_tau, tau_ms: float = TAU_MS):
    """Rate in 1/tau -> Hz (r_Hz = 100 r_tau at tau = 10 ms)."""
    return r_tau * 1000.0 / tau_ms


def freq_to_hz(f_tau, tau_ms: float = TAU_MS):
    """Frequency in cycles per tau -> Hz (f_Hz = 100 f_tau at tau = 10 ms)."""
    return f_tau * 1000.0 / tau_ms


def hz_to_rate(r_hz, tau_ms: float = TAU_MS):
    """Rate in Hz -> 1/tau."""
    return r_hz * tau_ms / 1000.0


def hz_to_freq(f_hz, tau_ms: float = TAU_MS):
    """Frequency in Hz -> cycles per tau."""
    return f_hz * tau_ms / 1000.0
