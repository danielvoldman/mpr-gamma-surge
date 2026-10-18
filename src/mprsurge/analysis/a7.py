"""8e: A7 per-run ramp metrics for the S5 and S13 records (plan 5.2 A7; Table 2.1 Metrics; Table 7.2 RB3(a); DL-179).

Analysis only: it reads stored records and writes nothing (scripts/run_A7.py writes the table). It judges nothing: no RB3, RB5, RB6 or
G6 verdict, no pass or fail. Every threshold, floor, A_ref and the A4 grid step is read from the frozen criteria (blob of the tag
criteria-frozen, gate checked first); none is typed here. Onset, duration, peak power, f_pk and class come from surge_metrics unchanged;
lambda along the path and t_pred come from entry_exit unchanged (trapezoid on the A4 grid nodes, DL-149).

Definitions used (working readings, UNVERIFIED where the plan gives none; DL-179):
  mode             : kind mf -> mode D, kind mf_noisy -> mode N (Table 2.1); threshold = frozen threshold_abs for both.
  onset            : the classifier episode onset (first qualifying episode; mode N: the earlier of the relative and absolute episodes).
  onset_cross      : first sample after t_on at which the band-passed Hilbert envelope reaches the threshold, whatever the cycle count
                     or damping (the RB3(a) wording "the envelope first reaching 0.1 x A_ref"); the match error uses this one.
  peak power       : mode D: the episode's P_G (absolute) and P_G / P_total (relative); mode N: the absolute episode's P_G and the
                     relative episode's P_G / P_total, as the classifier returns them.
  t_pred           : delta0 exp(int_{t_on}^{t_pred} Re lambda dt') = threshold, delta0 of the run, no eigenvector scaling.
  floor            : noise-free runs: solver_floor_noise_free_v; Heun runs whose sigma is a D43 level: that sigma_floor_levels value;
                     the S5 noise runs (calibrated sigma): none (in_range is NaN with a reason code).
  match error      : |eta_onset_cross - eta_pred| / A4 grid step; eta_const_at_t_pred marks t_pred on a stretch with no eta change,
                     where the number does not test the grid-step tolerance.
  P5               : eta_off = eta at the classifier episode end when the episode terminated after the eta peak; hysteresis_width =
                     eta_onset - eta_off.
Every NaN or missing value in a numeric column has a reason code in the column nan_reasons ("column=reason;...").
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from .. import config as C
from .. import criteria as CR
from .. import ramps
from ..units import tau_to_s
from . import entry_exit as EE
from . import surge_metrics as M

PATH_LABEL = {"path_eta": "P1", "path_hypoxia": "P2", "path_updown": "P5"}
SOLVER_FLOOR_KEY = "solver_floor_noise_free_v"

ID_COLUMNS = ("run_id", "list", "family", "run_file", "config_hash", "config_hash12", "kind", "mode", "path", "path_name", "profile",
              "solver", "spawn_key", "git_commit", "criteria_sha256")
NUMERIC_COLUMNS = (
    "T_ramp_s", "start_distance", "eta_start", "eta_H", "delta0", "rtol", "heun_dt_tau", "coupling_dt_tau", "sigma", "d43_level",
    "seed", "t_on_s",
    "onset_s", "eta_onset", "delay_eta", "end_s", "duration_s", "duration_cycles", "duration_frac_ramp", "f_pk_hz",
    "peak_power_abs", "peak_power_rel",
    "onset_cross_s", "eta_onset_cross", "delay_eta_cross",
    "t_pred_s", "eta_pred", "delay_eta_pred", "I_min", "re_final", "floor", "match_err_steps", "match_err_steps_cls",
    "onset_cross_minus_t_pred_s",
    "eta_off", "offset_minus_eta_H", "hysteresis_width")
BOOL_COLUMNS = ("terminated", "t_pred_in_run", "eta_const_at_t_pred", "in_range")
STR_COLUMNS = ("cls", "class_reason", "provisional", "floor_kind", "nan_reasons")
COLUMNS = ID_COLUMNS + NUMERIC_COLUMNS + BOOL_COLUMNS + STR_COLUMNS


class A7Error(RuntimeError):
    pass


def frozen_inputs(root=None):
    """(frozen inputs dict, gate info). Runs the criteria gate first; refuses (CriteriaError) on any mismatch."""
    crit, info = CR.load_frozen_criteria(root)
    d = crit["d43_and_numerics"]
    a = crit["a_ref"] if "a_ref" in crit else None
    out = {
        "threshold": float(_find(crit, "threshold_abs")), "a_ref": float(_find(crit, "a_ref", leaf=True)),
        "solver_floor": float(d[SOLVER_FLOOR_KEY]["value"]), "grid_step": float(d["a4_eta_bar_grid_step"]["value"]),
        "d43_levels": [float(x) for x in d["sigma_floor_levels"]["value"]], "criteria_sha256": info["sha256"],
    }
    if abs(out["threshold"] - 0.1 * out["a_ref"]) > 1e-6 * out["a_ref"]:
        raise A7Error(f"frozen threshold_abs {out['threshold']} is not 0.1 x frozen A_ref {out['a_ref']}")
    return out, info


def _find(obj, key, leaf=False):
    """The 'value' of the first mapping entry named key, searched depth first (the frozen file nests threshold_abs under a_ref)."""
    if isinstance(obj, dict):
        if key in obj:
            v = obj[key]
            if isinstance(v, dict) and "value" in v:
                return v["value"]
            if not leaf or not isinstance(v, dict):
                return v
        for v in obj.values():
            r = _find(v, key, leaf)
            if r is not None:
                return r
    return None


def check_a4_grid(grid_step, root=None):
    """The A4 grid in configs/A4_grids.yaml (hash-verified by the gate) has the frozen spacing and the origin entry_exit assumes."""
    import yaml
    root = Path(root) if root is not None else C.repo_root()
    g = yaml.safe_load((root / "configs/A4_grids.yaml").read_text(encoding="utf-8"))["grids"]["eta_bar"]
    step = (g["hi"] - g["lo"]) / (g["n"] - 1)
    if abs(step - grid_step) > 1e-12 or g["lo"] != EE.GRID_ORIGIN:
        raise A7Error(f"A4 grid in configs/A4_grids.yaml (lo {g['lo']}, step {step}) does not match the frozen step {grid_step} "
                      f"and the entry_exit origin {EE.GRID_ORIGIN}")


# ---- pieces -------------------------------------------------------------------------------------------------------
def first_crossing(v, fs, t_on_s, threshold, band=M.G_BAND):
    """First time (s) at or after t_on at which the band-passed Hilbert envelope reaches threshold; None if never."""
    env = M.envelope(v, fs, band)
    i_on = int(round(t_on_s * fs))
    hit = np.flatnonzero(env[i_on:] >= threshold)
    return float((i_on + hit[0]) / fs) if hit.size else None


def predict(cfg, delta0, threshold, h, lam_fn=None, cache=None):
    """Entry-exit prediction along the configured path: dict from entry_exit.entry_exit (times in tau) plus the node arrays' key.

    cache (dict) shares the eigenvalue evaluation between runs on the same path (the floor ladder)."""
    key = json.dumps([cfg["path"], cfg["model"], cfg["durations"], h], sort_keys=True, default=str)
    if cache is not None and lam_fn is None and key in cache:
        path, t, re, I = cache[key]
    else:
        path, t, re, I = EE.path_gain(cfg, h, lam_fn=lam_fn)
        if cache is not None and lam_fn is None:
            cache[key] = (path, t, re, I)
    return EE.entry_exit(cfg, path, t, re, I, delta0, threshold, h)


def floor_for(cfg, fi):
    """(floor, floor_kind, d43_level_index or None, reason or None) from the frozen inputs."""
    if cfg["run"]["kind"] == "mf":
        return fi["solver_floor"], "solver", None, None
    sigma = cfg["noise"]["sigma"] * cfg["noise"]["sigma_factor"]
    for k, lv in enumerate(fi["d43_levels"]):
        if math.isclose(sigma, lv, rel_tol=1e-6):
            return lv, "D43", k, None
    return None, "none", None, "no_D43_floor_sigma_calibrated"


def classify_run(cfg, v, fs, threshold):
    """surge_metrics classifier for the run's mode; (ClassResult or None, error text)."""
    t_on, T = cfg["path"]["t_on_s"], cfg["path"]["T_ramp_s"]
    try:
        if cfg["run"]["kind"] == "mf":
            return M.classify_mode_d(v, fs, t_on, T, threshold), ""
        return M.classify_mode_n(v, fs, t_on, T, threshold), ""
    except ValueError as exc:
        return None, str(exc)[:80]


# ---- one row ------------------------------------------------------------------------------------------------------
def run_row(json_path, fi, list_name, cache=None):
    """The A7 row of one stored record (json path); the npz sits beside it."""
    jp = Path(json_path)
    rec = json.loads(jp.read_text(encoding="utf-8"))
    cfg = rec["config"]
    with np.load(jp.with_suffix(".npz")) as z:
        arr = {k: z[k] for k in z.files}
    tau_ms = cfg["model"]["tau_ms"]
    fs = 1000.0 / cfg["solver"]["dt_out_ms"]
    t_s = arr["t_ms"] / 1000.0
    p, kind = cfg["path"], cfg["run"]["kind"]
    noisy = kind == "mf_noisy"
    key = cfg["seeds"]["spawn_key"]
    why: dict[str, str] = {}
    row: dict = {
        "run_id": jp.stem, "list": list_name, "family": jp.parent.name, "run_file": cfg["_resolved_from"]["run_file"],
        "config_hash": rec["config_hash"], "config_hash12": rec["config_hash12"], "kind": kind, "mode": "N" if noisy else "D",
        "path": PATH_LABEL[p["name"]], "path_name": p["name"], "profile": p["profile"],
        "solver": "Heun" if noisy else cfg["solver"]["method"], "spawn_key": json.dumps(list(key)) if key is not None else "none",
        "git_commit": rec["git"]["commit"], "criteria_sha256": rec["criteria_sha256"],
        "T_ramp_s": float(p["T_ramp_s"]), "start_distance": float(p["eta_H"] - p["eta_start"]), "eta_start": float(p["eta_start"]),
        "eta_H": float(p["eta_H"]), "delta0": float(cfg["solver"]["delta0"]), "t_on_s": float(p["t_on_s"]),
    }

    def put(col, value, reason):
        if value is None or (isinstance(value, float) and math.isnan(value)):
            row[col] = float("nan")
            why[col] = reason
        else:
            row[col] = value

    put("rtol", None if noisy else float(cfg["solver"]["rtol"]), "not_applicable_heun")
    put("heun_dt_tau", float(cfg["noise"]["dt_tau"]) if noisy else None, "not_applicable_noise_free")
    put("coupling_dt_tau", cfg["noise"].get("coupling_dt_tau") if noisy else None,
        "not_applicable_noise_free" if not noisy else "no_coupled_increments")
    put("sigma", float(cfg["noise"]["sigma"] * cfg["noise"]["sigma_factor"]) if noisy else None, "not_applicable_noise_free")
    put("seed", int(key[-1]) if key is not None else None, "not_applicable_noise_free")

    floor, floor_kind, lvl, floor_why = floor_for(cfg, fi)
    row["floor_kind"] = floor_kind
    put("floor", floor, floor_why or "")
    put("d43_level", lvl, "not_applicable_not_D43_floor_run")

    # class and episode metrics (surge_metrics, unchanged)
    res, err = classify_run(cfg, arr["v"], fs, fi["threshold"])
    ep = None
    if res is None:
        row.update(cls="not_run", class_reason=err, provisional="")
        no_ep = "classifier_error"
    else:
        ep = res.episode
        row.update(cls=res.cls, class_reason=res.reason or "", provisional=res.provisional or "")
        no_ep = "no_episode"
    row["terminated"] = None if ep is None else bool(ep.terminated)
    if ep is None:
        why["terminated"] = no_ep
    eta_t = arr["eta"]
    onset_s = None if ep is None else ep.onset_s
    put("onset_s", onset_s, no_ep)
    if onset_s is not None:
        eta_on, delay = M.onset_delay(onset_s, t_s, eta_t, p["eta_H"])
    else:
        eta_on = delay = None
    put("eta_onset", eta_on, no_ep)
    put("delay_eta", delay, no_ep)
    put("end_s", None if ep is None else ep.end_s, no_ep)
    put("duration_s", None if ep is None else ep.duration_s, no_ep)
    put("duration_cycles", None if ep is None else ep.cycles, no_ep)
    put("duration_frac_ramp", None if ep is None else ep.duration_s / p["T_ramp_s"], no_ep)
    put("f_pk_hz", None if ep is None else ep.f_pk_hz, no_ep)
    if res is not None and res.mode == "N":
        put("peak_power_abs", None if res.abs is None else res.abs.peak_p_g, "no_absolute_episode" if ep is not None else no_ep)
        put("peak_power_rel", None if res.rel is None else res.rel.peak_rho, "no_relative_episode" if ep is not None else no_ep)
    else:
        put("peak_power_abs", None if ep is None else ep.peak_p_g, no_ep)
        put("peak_power_rel", None if ep is None else ep.peak_rho, no_ep)

    # raw first threshold crossing
    tc = first_crossing(arr["v"], fs, p["t_on_s"], fi["threshold"])
    put("onset_cross_s", tc, "envelope_never_reaches_threshold")
    if tc is not None:
        eta_c, delay_c = M.onset_delay(tc, t_s, eta_t, p["eta_H"])
    else:
        eta_c = delay_c = None
    put("eta_onset_cross", eta_c, "envelope_never_reaches_threshold")
    put("delay_eta_cross", delay_c, "envelope_never_reaches_threshold")

    # entry-exit prediction along the path (entry_exit, unchanged)
    h = fi["grid_step"]
    pr = predict(cfg, row["delta0"], fi["threshold"], h, cache=cache)
    tp = pr["t_pred"]
    t_pred_s = None if tp is None else tau_to_s(tp, tau_ms)
    put("t_pred_s", t_pred_s, "no_t_pred")
    put("eta_pred", pr["eta_on"], "no_t_pred")
    put("delay_eta_pred", pr["delay_eta"], "no_t_pred")
    put("I_min", pr["I_min"], "no_t_pred")
    put("re_final", pr["re_final"], "")
    row["t_pred_in_run"] = None if tp is None else bool(pr["in_run"])
    row["eta_const_at_t_pred"] = None if tp is None else bool(pr["tol_step"] is None)
    for c in ("t_pred_in_run", "eta_const_at_t_pred"):
        if row[c] is None:
            why[c] = "no_t_pred"
    if tp is None:
        row["in_range"] = None
        why["in_range"] = "no_t_pred"
    elif floor is None:
        row["in_range"] = None
        why["in_range"] = floor_why
    else:
        row["in_range"] = EE.inside_range(row["delta0"], pr["I_min"], floor)
    put("match_err_steps", None if (tc is None or tp is None) else abs(eta_c - pr["eta_on"]) / h,
        "no_t_pred" if tp is None else "envelope_never_reaches_threshold")
    put("match_err_steps_cls", None if (eta_on is None or tp is None) else abs(eta_on - pr["eta_on"]) / h,
        "no_t_pred" if tp is None else no_ep)
    put("onset_cross_minus_t_pred_s", None if (tc is None or tp is None) else tc - t_pred_s,
        "no_t_pred" if tp is None else "envelope_never_reaches_threshold")

    # P5 offset and hysteresis width
    up_down = p["name"] == "path_updown"
    eta_off = None
    off_why = "not_applicable_not_P5"
    if up_down:
        t_peak_s = p["t_on_s"] + p["T_ramp_s"]
        if ep is None:
            off_why = no_ep
        elif not ep.terminated:
            off_why = "episode_not_terminated"
        elif ep.end_s <= t_peak_s:
            off_why = "episode_ends_before_eta_peak"
        else:
            eta_off = float(np.interp(ep.end_s, t_s, eta_t))
    put("eta_off", eta_off, off_why)
    put("offset_minus_eta_H", None if eta_off is None else eta_off - p["eta_H"], off_why)
    put("hysteresis_width", None if (eta_off is None or eta_on is None) else eta_on - eta_off, off_why)

    row["nan_reasons"] = ";".join(f"{c}={r}" for c, r in why.items())
    return row


# ---- table --------------------------------------------------------------------------------------------------------
def record_files(root=None):
    """(list name, json path) for every stored S5 ramp, S5 noise and S13 record (dry-run files excluded), sorted."""
    root = Path(root) if root is not None else C.repo_root()
    out = []
    for lst, base in (("S5", "results/S5/ramp"), ("S5", "results/S5/ramp_noise"), ("S13", "results/S13")):
        for p in sorted((root / base).rglob("*.json")):
            if p.name.endswith(".dry.json"):
                continue
            out.append((lst, p))
    return out


def to_frame(rows):
    import pandas as pd
    df = pd.DataFrame(rows, columns=list(COLUMNS))
    for c in BOOL_COLUMNS:
        df[c] = df[c].astype("boolean")
    for c in NUMERIC_COLUMNS:
        df[c] = df[c].astype("float64")
    return df


def check_reasons(df):
    """Rows (index, column) whose value is missing and not named in nan_reasons; empty when every NaN carries a reason."""
    bad = []
    for c in NUMERIC_COLUMNS + BOOL_COLUMNS:
        miss = df[c].isna()
        for i in df.index[miss]:
            if f"{c}=" not in df.at[i, "nan_reasons"]:
                bad.append((i, c))
    for c in ID_COLUMNS + STR_COLUMNS[:-1]:
        if df[c].isna().any():
            bad.extend((i, c) for i in df.index[df[c].isna()])
    return bad


def reason_counts(df):
    """{column: {reason: count}} from nan_reasons."""
    out: dict = {}
    for s in df["nan_reasons"]:
        for item in filter(None, s.split(";")):
            c, r = item.split("=", 1)
            out.setdefault(c, {}).setdefault(r, 0)
            out[c][r] += 1
    return out
