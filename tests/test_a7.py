"""8e A7 per-run ramp metrics (DL-179). Seeded, synthetic, known answers; no stored result is read, nothing is integrated."""
import copy
import json
import math

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import criteria as K
from mprsurge import ramps
from mprsurge.analysis import a7
from mprsurge.analysis import entry_exit as E
from mprsurge.units import s_to_tau, tau_to_s

from test_criteria_loader import make_repo

FS = 1000.0
THR = 0.217622
FROZEN_SHA = "c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05"


@pytest.fixture(scope="module")
def fi():
    try:
        return a7.frozen_inputs()[0]
    except K.CriteriaError as exc:
        pytest.skip(f"the freeze does not verify in this clone: {exc}")


def _cfg(name="path_eta", T=120.0, profile="linear"):
    cfg = copy.deepcopy(C.resolve_config("configs/S5_ramp.yaml"))
    cfg["path"].update(name=name, T_ramp_s=T, profile=profile)
    return cfg


def synth_record(tmp_path, v_fn=None, *, name="path_hypoxia", T=1.0, profile="linear", kind="mf", sigma=None, delta0=1e-6,
                 tag="syn", seed=0):
    """Write a stored-record pair (json + npz) with the arrays of a ramp run: eta, J from the path, v from v_fn(t_s)."""
    cfg = _cfg(name, T, profile)
    cfg["run"]["kind"] = kind
    cfg["solver"]["delta0"] = delta0
    if kind == "mf_noisy":
        cfg["noise"].update(sigma=sigma, sigma_factor=1.0, dt_tau=1e-3)
        cfg["seeds"]["spawn_key"] = [8, 1, 3]
    cfg["_resolved_from"] = {"run_file": "synthetic"}
    path = ramps.make_path(cfg)
    t_end = tau_to_s(path.t_ramp_end) + cfg["durations"]["hold_s"]
    t_s = np.arange(int(round(t_end * FS)) + 1) / FS
    tt = s_to_tau(t_s)
    rng = np.random.default_rng(seed)
    v = 1e-4 * rng.standard_normal(t_s.size) if v_fn is None else v_fn(t_s)
    d = tmp_path / tag
    d.mkdir(parents=True, exist_ok=True)
    np.savez(d / f"{tag}.npz", t_ms=t_s * 1000, v=v, eta=path.eta(tt), J=path.J(tt))
    (d / f"{tag}.json").write_text(json.dumps({"config": cfg, "config_hash": "ab" * 32, "config_hash12": "ab" * 6,
                                               "git": {"commit": "x"}, "criteria_sha256": FROZEN_SHA}))
    return d / f"{tag}.json", cfg, path


def burst(on, off, amp=0.5, f=40.0, rise=0.5):
    def fn(t):
        gate = np.clip((t - on) / rise, 0, 1) * np.clip((off - t) / rise, 0, 1)
        return amp * gate * np.sin(2 * np.pi * f * t)
    return fn


# (a) entry-exit integral against a closed form -------------------------------------------------------------------
def test_integral_matches_closed_form_for_re_lambda_linear_in_t():
    cfg = _cfg("path_eta", 120.0)
    p = cfg["path"]
    T_tau = s_to_tau(p["T_ramp_s"])
    a, k = 0.05, 0.3                                                   # Re lambda = a + k (eta - eta_start)
    b = k * (p["eta_peak"] - p["eta_start"]) / T_tau                   # per tau^2, because eta is linear in t on the ramp
    path, t, re, I = E.path_gain(cfg, 0.025, lam_fn=lambda eta, J: a + k * (eta - p["eta_start"]))
    s = t - path.t_on
    on_ramp = (s >= 0) & (s <= T_tau)
    assert on_ramp.sum() > 60
    assert np.allclose(I[on_ramp] - I[on_ramp][0], (a * s + 0.5 * b * s ** 2)[on_ramp] - (a * s + 0.5 * b * s ** 2)[on_ramp][0],
                       rtol=1e-12, atol=1e-12)


# (b) t_pred against the closed form given delta0 and the threshold ------------------------------------------------
def test_t_pred_matches_closed_form_with_delta0_and_threshold():
    cfg = _cfg("path_eta", 120.0)
    p = cfg["path"]
    T_tau = s_to_tau(p["T_ramp_s"])
    a, k = 0.1, 0.3
    b = k * (p["eta_peak"] - p["eta_start"]) / T_tau
    delta0 = 1e-6
    L = math.log(THR / delta0)
    s_star = (-a + math.sqrt(a * a + 2 * b * L)) / b                   # a s + b s^2 / 2 = L
    assert 0 < s_star < T_tau
    r = a7.predict(cfg, delta0, THR, 0.0025, lam_fn=lambda eta, J: a + k * (eta - p["eta_start"]))
    path = ramps.make_path(cfg)
    assert r["t_pred"] - path.t_on == pytest.approx(s_star, abs=0.01)
    # no eigenvector scaling: a ten-fold smaller delta0 moves t_pred by the closed form too
    r2 = a7.predict(cfg, delta0 / 10, THR, 0.0025, lam_fn=lambda eta, J: a + k * (eta - p["eta_start"]))
    s2 = (-a + math.sqrt(a * a + 2 * b * (L + math.log(10)))) / b
    assert r2["t_pred"] - path.t_on == pytest.approx(s2, abs=0.01)


# (c) in-range flag inside and outside ----------------------------------------------------------------------------
def test_in_range_flag_inside_outside_and_floor_kinds(tmp_path, fi):
    inside, _, _ = synth_record(tmp_path, name="path_eta", T=1.0, tag="in")
    outside, _, _ = synth_record(tmp_path, name="path_eta", T=100.0, tag="out")
    r_in, r_out = a7.run_row(inside, fi, "S5"), a7.run_row(outside, fi, "S5")
    assert r_in["floor_kind"] == "solver" and r_in["floor"] == fi["solver_floor"] == 6.66e-16
    assert r_in["in_range"] is True and r_out["in_range"] is False
    assert r_in["I_min"] > r_out["I_min"]
    # D43 level above delta0: outside even for a fast ramp; the level is the frozen one
    lv = fi["d43_levels"][2]
    top, _, _ = synth_record(tmp_path, name="path_eta", T=1.0, kind="mf_noisy", sigma=lv, tag="l2")
    r_top = a7.run_row(top, fi, "S13")
    assert (r_top["floor_kind"], r_top["floor"], r_top["d43_level"], r_top["in_range"]) == ("D43", lv, 2.0, False)
    # calibrated sigma: no floor, NaN with a reason code, t_pred still computed
    cal, _, _ = synth_record(tmp_path, name="path_eta", T=1.0, kind="mf_noisy", sigma=0.0624, tag="cal")
    r_cal = a7.run_row(cal, fi, "S5")
    assert r_cal["floor_kind"] == "none" and r_cal["in_range"] is None and not math.isnan(r_cal["t_pred_s"])
    assert "in_range=no_D43_floor_sigma_calibrated" in r_cal["nan_reasons"]


def test_a_run_with_no_t_pred_has_reason_codes(tmp_path, fi):
    # P2 sigmoid never returns to delta0 exp(I) = threshold before J reaches 0 (DL-149 (3)); T_ramp 10 s
    rec, _, _ = synth_record(tmp_path, name="path_hypoxia", T=10.0, profile="sigmoid", tag="nop")
    r = a7.run_row(rec, fi, "S5")
    assert math.isnan(r["t_pred_s"]) and "t_pred_s=no_t_pred" in r["nan_reasons"] and "in_range=no_t_pred" in r["nan_reasons"]
    assert r["in_range"] is None


# (d) onset detection on a synthetic growing envelope --------------------------------------------------------------
def test_first_crossing_on_a_growing_envelope():
    g, A0, t_on = 0.5, 0.01, 5.0
    t = np.arange(int(15 * FS)) / FS
    env = np.where(t >= t_on, A0 * np.exp(g * (t - t_on)), 0.0)
    v = env * np.sin(2 * np.pi * 40.0 * t)
    t_true = t_on + math.log(THR / A0) / g
    assert a7.first_crossing(v, FS, t_on, THR) == pytest.approx(t_true, abs=0.03)
    assert a7.first_crossing(0.5 * v * 0.0 + 1e-4 * np.sin(2 * np.pi * 40.0 * t), FS, t_on, THR) is None


def test_row_onset_and_match_columns_on_a_burst(tmp_path, fi):
    rec, cfg, path = synth_record(tmp_path, burst(12.0, 35.0), name="path_eta", T=30.0, tag="b")
    r = a7.run_row(rec, fi, "S5")
    assert r["cls"] == "D-tr" and r["onset_s"] == pytest.approx(12.0, abs=0.3)
    assert r["onset_cross_s"] == pytest.approx(12.0, abs=0.3)
    assert r["eta_onset"] == pytest.approx(float(path.eta(s_to_tau(r["onset_s"]))), abs=1e-3)
    assert r["delay_eta"] == pytest.approx(r["eta_onset"] - cfg["path"]["eta_H"])
    assert r["f_pk_hz"] == pytest.approx(40.0, abs=3.0)
    assert r["match_err_steps"] == pytest.approx(abs(r["eta_onset_cross"] - r["eta_pred"]) / 0.025)


def test_p5_offset_and_hysteresis_width(tmp_path, fi):
    rec, cfg, path = synth_record(tmp_path, burst(12.0, 35.0), name="path_updown", T=20.0, tag="p5")
    r = a7.run_row(rec, fi, "S5")
    assert r["cls"] == "D-tr" and r["end_s"] == pytest.approx(35.0, abs=0.5)
    eta_end = float(path.eta(s_to_tau(r["end_s"])))
    assert r["eta_off"] == pytest.approx(eta_end, abs=1e-3)
    assert r["hysteresis_width"] == pytest.approx(r["eta_onset"] - r["eta_off"])
    assert r["offset_minus_eta_H"] == pytest.approx(r["eta_off"] - cfg["path"]["eta_H"])
    none, _, _ = synth_record(tmp_path, name="path_updown", T=20.0, tag="p5n")
    rn = a7.run_row(none, fi, "S5")
    assert math.isnan(rn["eta_off"]) and "eta_off=no_episode" in rn["nan_reasons"]
    assert "hysteresis_width=no_episode" in rn["nan_reasons"]


# (e) the frozen-criteria gate -------------------------------------------------------------------------------------
def test_gate_passes_on_a_clean_freeze_and_refuses_on_a_mismatch(tmp_path):
    root = make_repo(tmp_path)
    fi, info = a7.frozen_inputs(root)
    assert fi["threshold"] == THR and fi["a_ref"] == 2.176222 and fi["grid_step"] == 0.025 and fi["solver_floor"] == 6.66e-16
    f = root / K.CRITERIA_PATH
    f.write_bytes(f.read_bytes().replace(b"6.66e-16", b"6.67e-16"))
    with pytest.raises(K.CriteriaError):
        a7.frozen_inputs(root)


def test_grid_check_refuses_a_different_step(tmp_path):
    root = make_repo(tmp_path)
    a7.check_a4_grid(0.025, root)
    with pytest.raises(a7.A7Error):
        a7.check_a4_grid(0.05, root)


# (f) schema and no silent NaN --------------------------------------------------------------------------------------
def test_table_schema_and_every_nan_has_a_reason(tmp_path, fi):
    recs = [synth_record(tmp_path, T=1.0, tag="s1")[0], synth_record(tmp_path, T=100.0, tag="s2")[0],
            synth_record(tmp_path, burst(12.0, 35.0), name="path_updown", T=20.0, tag="s3")[0],
            synth_record(tmp_path, T=1.0, kind="mf_noisy", sigma=0.0624, tag="s4")[0],
            synth_record(tmp_path, T=1.0, kind="mf_noisy", sigma=fi["d43_levels"][0], tag="s5")[0]]
    cache = {}
    df = a7.to_frame([a7.run_row(p, fi, "S5", cache) for p in recs])
    assert list(df.columns) == list(a7.COLUMNS) and len(df) == 5
    assert all(str(df[c].dtype) == "float64" for c in a7.NUMERIC_COLUMNS)
    assert all(str(df[c].dtype) == "boolean" for c in a7.BOOL_COLUMNS)
    assert a7.check_reasons(df) == []
    assert df[list(a7.ID_COLUMNS)].notna().all().all()
    # negative control: stripping a reason is detected
    bad = df.copy()
    bad.at[0, "nan_reasons"] = bad.at[0, "nan_reasons"].replace("sigma=not_applicable_noise_free", "")
    assert ("sigma" in [c for _, c in a7.check_reasons(bad)])
    counts = a7.reason_counts(df)
    assert counts["sigma"]["not_applicable_noise_free"] == 3


def test_a7_kind_registered_and_config_resolves():
    assert "a7" in C.RUN_KINDS
    assert C.resolve_config("configs/A7.yaml")["run"]["kind"] == "a7"
