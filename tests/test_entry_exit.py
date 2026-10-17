"""7g entry-exit prediction and RB3(a) range (DL-148). Analysis only; no integration."""
import copy

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge.analysis import entry_exit as E

THR = 0.21762
D0 = 1e-6


def _cfg(path="path_eta", profile="linear", T=120.0):
    cfg = C.resolve_config("configs/RB3a.yaml")
    cfg = copy.deepcopy(cfg)
    cfg["path"].update(name=path, profile=profile, T_ramp_s=T)
    return cfg


def test_rb3a_kind_registered():
    assert "rb3a" in C.RUN_KINDS


def test_constant_eigenvalue_gives_the_analytic_t_pred():
    lam = 0.2
    cfg = _cfg()
    path, t, re, I = E.path_gain(cfg, 0.025, lam_fn=lambda eta, J: lam)
    assert np.allclose(re, lam)
    r = E.entry_exit(cfg, path, t, re, I, D0, THR, 0.025)
    assert r["t_pred"] == pytest.approx(path.t_on + np.log(THR / D0) / lam, rel=1e-12)
    assert r["I_min"] == 0.0


def test_prediction_extends_analytically_after_the_last_node():
    t = np.array([0.0, 10.0])
    re = np.array([0.1, 0.1])
    I = E.cumulative_gain(t, re)
    tp, k = E.t_pred_from(t, re, I, 1e-6, 1.0)
    assert tp == pytest.approx(np.log(1e6) / 0.1) and k == 2
    assert E.t_pred_from(t, -re, E.cumulative_gain(t, -re), 1e-6, 1.0)[0] is None


def test_decay_then_growth_matches_the_closed_form():
    # re = a (t - t0) linear: I(t) = a (t - t0)^2 / 2 - a t0^2 / 2 from t = 0
    a, t0 = 0.01, 20.0
    t = np.linspace(0.0, 200.0, 20001)
    re = a * (t - t0)
    I = E.cumulative_gain(t, re)
    assert I.min() == pytest.approx(-a * t0 ** 2 / 2.0, rel=1e-6)
    tp, _ = E.t_pred_from(t, re, I, 1e-3, 1.0)
    L = np.log(1e3)
    assert tp == pytest.approx(t0 + np.sqrt(2.0 * L / a + t0 ** 2), rel=1e-6)


def test_range_shrinks_as_floor_rises_and_scales_with_t_ramp():
    ins = []
    for T in (1.0, 10.0):
        cfg = _cfg(T=T)
        path, t, re, I = E.path_gain(cfg, 0.025)
        ins.append(E.entry_exit(cfg, path, t, re, I, D0, THR, 0.025)["I_min"])
    assert ins[1] == pytest.approx(10.0 * ins[0], rel=1e-9)               # I_min proportional to T_ramp
    imin = ins[0]
    bounds = [E.t_ramp_max(1.0, imin, D0, fl) for fl in (1e-14, 1e-12, 1e-9, 1e-7)]
    assert all(b2 < b1 for b1, b2 in zip(bounds, bounds[1:]))
    assert E.inside_range(D0, imin, 1e-14) and not E.inside_range(D0, imin, 1e-3)
    assert E.t_ramp_max(1.0, 0.0, D0, 1e-12) == float("inf")


def test_leading_eigenvalue_vanishes_at_the_hopf_point_and_signs_around_it():
    eta_H = 2.8960461989737856
    kw = dict(J=-21.0, Delta=0.3, tau_d_tau=0.5)
    assert abs(E.leading_re(eta_H, **kw)) < 1e-4
    assert E.leading_re(eta_H - 1.5, **kw) < 0.0 < E.leading_re(eta_H + 1.0, **kw)


def test_grid_halving_moves_headline_t_pred_by_under_one_step():
    cfg = _cfg("path_hypoxia", "linear", 120.0)
    tp = {}
    for h in (0.025, 0.0125):
        path, t, re, I = E.path_gain(cfg, h)
        tp[h] = E.entry_exit(cfg, path, t, re, I, D0, THR, h)
    step = tp[0.025]["tol_step"]
    assert step == pytest.approx(120.0 * 0.025 / 3.5 * 100.0, rel=1e-3)   # tau; 0.857 s
    assert abs(tp[0.025]["t_pred"] - tp[0.0125]["t_pred"]) < step


def test_node_times_include_the_grid_levels_and_corners():
    cfg = _cfg("path_hypoxia", "linear", 120.0)
    path = E.ramps.make_path(cfg)
    t = E.node_times(cfg, path, 0.025)
    assert t[0] == path.t_on and t[-1] == path.t_ramp_end and np.all(np.diff(t) > 0)
    eta = path.eta(t)
    levels = E.GRID_ORIGIN + 0.025 * np.arange(0, 801)
    inner = eta[(eta > cfg["path"]["eta_start"] + 1e-9) & (eta < cfg["path"]["eta_peak"] - 1e-9)]
    assert np.isin(np.round(inner, 9), np.round(levels, 9)).sum() >= 139


def test_sigmoid_inverse_profile_roundtrip():
    x = np.linspace(0.0, 1.0, 11)
    y = E.ramps.profile_sigmoid(x, 10.0)
    assert np.allclose(E._inverse_profile("sigmoid", 10.0, y), x, atol=1e-9)


def test_stationary_std_scales_with_sigma_and_grows_towards_the_hopf_point():
    kw = dict(J=-21.0, Delta=0.3, tau_d_tau=0.5)
    s1 = E.stationary_std_v(2.0, sigma=1.0, **kw)
    assert E.stationary_std_v(2.0, sigma=0.5, **kw) == pytest.approx(0.5 * s1)
    assert E.stationary_std_v(2.8, **kw) > s1 > E.stationary_std_v(1.396, **kw) > 0


def test_a4_grid_step_agrees_across_configs():
    import yaml
    root = C.repo_root()
    s13 = yaml.safe_load((root / "configs/S13.yaml").read_text(encoding="utf8"))["ruled_by_owner_7g"]
    g = yaml.safe_load((root / "configs/A4_grids.yaml").read_text(encoding="utf8"))["grids"]["eta_bar"]
    assert (g["hi"] - g["lo"]) / (g["n"] - 1) == pytest.approx(s13["a4_eta_bar_grid_step"], rel=1e-12)
    assert s13["a4_eta_bar_grid_step"] == 0.025
    assert "a4_eta_bar_grid_step: 0.025" not in (root / "configs/A4.yaml").read_text(encoding="utf8")  # comment only, not a key


def test_s13_ruled_values_consistent():
    import yaml
    s = yaml.safe_load((C.repo_root() / "configs/S13.yaml").read_text(encoding="utf8"))
    r = s["ruled_by_owner_7g"]
    assert r["heun_dt_ladder_tau"][0] == s["stated_by_plan"]["heun_dt_default_tau"] == 1e-3
    assert r["heun_dt_ladder_tau"] == [1e-3, 5e-4, 2.5e-4, 1e-4]
    for d0, sf in zip(r["d43_delta0_nominal"], r["d43_floor_levels_sigma_floor"]):
        assert sf == pytest.approx(d0 / r["d43_std_v_over_sigma_at_start_state"], rel=5e-3)
    assert max(r["d43_floor_levels_sigma_floor"]) < 0.0624
    assert "pending_owner_ruling" not in s
