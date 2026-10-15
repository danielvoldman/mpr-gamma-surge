"""A2 (MS2 step 2d, DL-089): damped-sinusoid fit, K4 linearisation and tail rule, ring map, hash."""
import copy

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from mprsurge import config as C
from mprsurge.analysis import ring as RG
from mprsurge.models.fixed_points import classify_all

PI = np.pi


def test_fit_recovers_known_frequency_and_decay_within_2_percent():
    t = np.arange(0, 30, 0.1)
    for a, w, c, phi in [(0.2318, 5.7664, 1.37, 0.7), (0.05, 2.0, -0.3, 2.5), (0.5, 9.0, 0.0, -1.0)]:
        y = c + 0.15 * np.exp(-a * t) * np.cos(w * t + phi)
        f = RG.fit_damped_sinusoid(t, y)
        assert abs(f["omega"] - w) / w < 0.02 and abs(f["decay"] - a) / a < 0.02
        assert f["offset"] == pytest.approx(c, abs=1e-6)
        assert f["cycles"] == pytest.approx(w * 29.9 / (2 * PI), rel=1e-6)


def test_fit_with_noise_stays_within_2_percent():
    rng = np.random.default_rng(3)
    t = np.arange(0, 30, 0.1)
    y = 1.37 + 0.15 * np.exp(-0.2318 * t) * np.cos(5.7664 * t + 0.4) + 1e-4 * rng.standard_normal(len(t))
    f = RG.fit_damped_sinusoid(t, y)
    assert abs(f["omega"] - 5.7664) / 5.7664 < 0.02 and abs(f["decay"] - 0.2318) / 0.2318 < 0.02
    assert f["se_decay"] > 0 and f["se_omega"] > 0


def test_fit_rejects_a_window_without_oscillation():
    t = np.arange(0, 5, 0.1)
    with pytest.raises(ValueError):
        RG.fit_damped_sinusoid(t, np.exp(-t))


def test_k4_linearisation_is_the_dl076_value():
    y, lam = RG.post_step_focus(-5.0, 15.0, 1.0, 3.0)
    assert lam.real == pytest.approx(-0.2318, abs=5e-5) and lam.imag == pytest.approx(5.7664, abs=5e-5)
    assert y[0] == pytest.approx(1.3732, abs=5e-5)
    with pytest.raises(C.ConfigError):          # a lone stable node, no stable focus
        RG.post_step_focus(-10.0, 12.0, 1.0, 0.0)


def test_tail_start_and_jump():
    t = np.arange(0, 60, 0.1)
    r = 1.0 + np.exp(-0.2 * t) * np.sin(3.0 * t)
    i0, jump = RG.tail_start(r, 1.0, 0.1)
    dev = np.abs(r - 1.0)
    assert jump == pytest.approx(dev[:60].max(), rel=1e-12)       # first peak, near t = 0.4
    assert dev[i0] < 0.1 * jump and dev[i0] == pytest.approx(np.exp(-0.2 * t[i0]), rel=0.05)
    with pytest.raises(ValueError):
        RG.tail_start(r[:20], 1.0, 0.1)


def test_k4_mf_check_on_an_integrated_step_passes_and_a_wrong_target_fails():
    eta, J, Delta, I = -5.0, 15.0, 1.0, 3.0
    y0 = [y for y, lab, _ in classify_all(eta, J, Delta, 0.0) if lab == "stable_node"][0]

    def f(t, y):
        return [Delta / PI + 2 * y[0] * y[1], y[1] ** 2 + eta + I + J * y[0] - PI**2 * y[0] ** 2]

    t = np.arange(0, 60.0001, 0.1)
    sol = solve_ivp(f, (0, 60), y0, method="DOP853", t_eval=t, rtol=1e-10, atol=1e-12)
    y_star, lam = RG.post_step_focus(eta, J, Delta, I)
    k = RG.k4_mf_check(t, sol.y[0], y_star[0], lam, 0.1, 0.02, 0.02, 40.0)
    assert k["pass"] and k["rel_err_frequency"] < 0.02 and k["rel_err_decay"] < 0.02
    assert k["t_end_tau"] <= 40.0 and k["cycles"] > 20
    bad = RG.k4_mf_check(t, sol.y[0], y_star[0], lam * 1.1, 0.1, 0.02, 0.02, 40.0)
    assert not bad["pass"]


def test_ring_map_units_and_band():
    # one stable-focus root at the K4 point (eta_bar, J) = (-5, 15) at I = 0 is the high-rate focus
    from mprsurge.analysis import bifurcation as B
    n, r, v, code, disc = B.classify_point(-5.0, 15.0)
    r3, lab3 = r[None, None, :], code[None, None, :]
    rm = RG.ring_map(np.array([15.0]), r3, lab3, B.CODE["stable_focus"], 10.0, (25.0, 100.0))
    k = np.flatnonzero(code == B.CODE["stable_focus"])
    assert len(k) == 1
    k = k[0]
    lam = RG.focus_eigenvalue(np.array([r[k], v[k]]), 15.0)
    f_tau = lam.imag / (2 * PI)
    assert rm["freq_hz"][0, 0, k] == pytest.approx(100.0 * f_tau)           # f_Hz = 100 f_tau at tau = 10 ms
    assert rm["decay_rate"][0, 0, k] == pytest.approx(-lam.real)
    assert rm["cycles_per_efold"][0, 0, k] == pytest.approx(lam.imag / (2 * PI * -lam.real))
    assert rm["is_focus"].sum() == 1 and np.isnan(rm["freq_hz"][~rm["is_focus"]]).all()
    assert rm["in_G"][0, 0, k] == (25.0 <= 100.0 * f_tau <= 100.0)
    assert not rm["g1_nondamped"].any()                                       # a stable focus is damped


def test_a2_kind_and_hash_covers_window_and_band():
    assert "a2" in C.RUN_KINDS
    cfg = C.resolve_config(C.repo_root() / "configs/A2.yaml", {})
    h = C.config_hash(cfg)
    c2 = copy.deepcopy(cfg)
    c2["analysis"]["band_primary_hz"] = [30.0, 120.0]
    assert C.config_hash(c2) != h
    old = dict(C.A2_WINDOW)
    try:
        C.A2_WINDOW["t_end_tau"] = 30.0
        assert C.config_hash(cfg) != h
    finally:
        C.A2_WINDOW.update(old)
    other = C.resolve_config(C.repo_root() / "configs/S1.yaml", {})
    assert "a2" not in C.hash_view(other)


def test_a2_hash_covers_the_upstream_result_hashes(upstream_results, tmp_path, monkeypatch):
    cfg = C.resolve_config(C.repo_root() / "configs/A2.yaml", {})
    view = C.hash_view(cfg)["a2"]["upstream_sha256"]
    assert set(view) == {"A1", "S1"} and all(len(v) == 64 for v in view.values())
    real = RG.upstream_npz
    h = C.config_hash(cfg)
    copies = {}
    for name, cfg_path in RG.UPSTREAM.items():
        copies[cfg_path] = tmp_path / f"{name}.npz"
        copies[cfg_path].write_bytes(real(cfg_path).read_bytes())
    monkeypatch.setattr(RG, "upstream_npz", lambda p: copies[p])
    assert C.config_hash(cfg) == h                      # identical bytes, same hash
    for p, f in copies.items():
        f.write_bytes(f.read_bytes() + b"\0")           # a changed upstream file
        assert C.config_hash(cfg) != h
        f.write_bytes(f.read_bytes()[:-1])
        assert C.config_hash(cfg) == h


def test_current_a2_result_passes_and_is_found_by_its_hash(upstream_results):
    from mprsurge import provenance as P
    from mprsurge import run as R
    plan = R.build_plan("configs/A2.yaml")
    rec = P.find_complete(plan.out_dir, plan.cells[0]["cfg"])
    assert rec is not None, "run scripts/run_A2.py"
    flags = P.read_run_record(rec)["flags"]
    assert flags["k4_pass"]
    assert flags["a1_npz_sha256"] == C.hash_view(plan.cells[0]["cfg"])["a2"]["upstream_sha256"]["A1"]
    assert flags["s1_npz_sha256"] == C.hash_view(plan.cells[0]["cfg"])["a2"]["upstream_sha256"]["S1"]
