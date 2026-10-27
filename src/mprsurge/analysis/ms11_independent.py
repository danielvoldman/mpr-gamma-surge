"""MS11 11g: independent recomputation of the MS11 rows of the A11 table (analysis only: reads stored records, integrates nothing, plots nothing).

Written from docs/ms11_eval_rules.md and the plan text. It does NOT import, call or copy ms11_eval, ms11_hooks, ms11_eval_choices, ms11_runlist, ms9_classify, a7 or
scripts/run_A11.py. What it does share with the original evaluation, on purpose and by name:
  * the criteria loader (mprsurge.criteria): the thresholds are read through it (the gate verifies the tag first);
  * the frozen classifier (surge_metrics.classify_mode_d / classify_mode_n and window_for_ramp, the D8 estimator inside it) and the frozen A8 variant definitions
    (a8_sensitivity.classify): every Table 2.1 class and episode (onset, end, f_pk) in this file was written by them;
  * the 9i-independent parts only: the 9i function (J_exit) is not used here at all.
What is its own code: the record reader, the comparators, the counts and verdicts, the zero-crossing cycle frequency, the spectrogram-window PSD argmax of DL-401,
the medians and the direction word, the class-change fractions, and the row-by-row comparison with the A11 output.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
from scipy import signal

from .. import criteria as CR
from . import a8_sensitivity as A8
from . import surge_metrics as M

TOL = 1e-9                       # tolerance on a compared number (rules section 0, comparison rule)
SURGE_N = ("S+", "S-rel", "S-abs")     # rules section 1: "kept" = Table 2.1 class S+, S-rel or S-abs
BAND = (25.0, 100.0)
ORDER = 4                        # DL-062: zero-phase Butterworth band-pass of order 4 (the plan's filter)


# --- comparators (rules section 0: "within" and "<=" and ">=" inclusive, "<" and ">" strict) ------------------------------------------------

def le(x: float, bound: float) -> bool:
    return x is not None and math.isfinite(x) and x <= bound + TOL


def ge(x: float, bound: float) -> bool:
    return x is not None and math.isfinite(x) and x >= bound - TOL


def lt(x: float, bound: float) -> bool:
    return x is not None and math.isfinite(x) and x < bound - TOL


# --- thresholds: through the criteria loader, own parsing -----------------------------------------------------------------------------------

def _find_value(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            v = obj[key]
            return v["value"] if isinstance(v, dict) and "value" in v else v
        for v in obj.values():
            r = _find_value(v, key)
            if r is not None:
                return r
    return None


def frozen_thresholds() -> dict:
    crit, info = CR.load_frozen_criteria()
    R = crit["robustness"]
    m = re.match(r"\s*(\d+)\s+of\s+(\d+)", str(R["RB2"]["headline_class_kept_min_seeds"]["value"]))
    thr_abs = float(_find_value(crit, "threshold_abs"))
    a_ref = float(_find_value(crit, "a_ref"))
    return {"sha256": info["sha256"], "commit": info["commit"], "rb2_k": int(m.group(1)), "rb2_n": int(m.group(2)),
            "net_fpk": float(R["RB6"]["network_dt_f_pk_change_max"]["value"]), "rb9a": float(R["RB9"]["a_dimensional_vs_nondimensional_rel_tol"]["value"]),
            "rb9c": float(R["RB9"]["c_band_30_120_max_cell_class_change"]["value"]), "rb10": float(R["RB10"]["max_map_cell_class_change"]["value"]),
            "threshold_abs": thr_abs, "a_ref": a_ref}


# --- records ----------------------------------------------------------------------------------------------------------------------------------

class RecordRefused(Exception):
    pass


def load_record(json_path, need_v: bool = True) -> dict:
    """One stored record: config, status, v, eta. Refuses a dirty or dry-run record (rules section 0.3)."""
    jp = Path(json_path)
    rec = json.loads(jp.read_text(encoding="utf-8"))
    git = rec.get("git") or {}
    if git.get("dirty") is not False or rec.get("dry_run"):
        raise RecordRefused(f"{jp.name}: dirty or dry-run record")
    cfg = rec["config"]
    kind = cfg["run"]["kind"]
    out = {"name": rec["name"], "path": str(jp), "cfg": cfg, "status": rec["status"], "commit": git.get("commit"), "kind": kind,
           "mode": "D" if kind == "mf" else "N", "T": float(cfg["path"]["T_ramp_s"]), "t_on": float(cfg["path"]["t_on_s"]),
           "fs": 1000.0 / (float(cfg["network"]["rate_bin_ms"]) if kind == "network" else float(cfg["solver"]["dt_out_ms"])),
           "seed": int(cfg["seeds"]["spawn_key"][-1]) if cfg["seeds"].get("spawn_key") else -1}
    if need_v and rec["status"] == "ok":
        with np.load(jp.with_suffix(".npz")) as z:
            out["v"] = np.asarray(z["v"], float)
            out["eta"] = np.asarray(z["eta"], float)
    return out


def json_files(folder) -> list[Path]:
    return sorted(p for p in Path(folder).glob("*.json") if not p.name.endswith(".dry.json"))


# --- classes: the frozen classifier is called, nothing else ---------------------------------------------------------------------------------

def classify(rec: dict, threshold: float) -> dict:
    """Table 2.1 class and episode of one loaded record by the frozen classifier. A record that did not run ok is class 'failed' (A9)."""
    if rec["status"] != "ok":
        return {"cls": "failed", "onset": math.nan, "end": math.nan, "fpk": math.nan, "terminated": None}
    f = M.classify_mode_d if rec["mode"] == "D" else M.classify_mode_n
    res = f(rec["v"], rec["fs"], rec["t_on"], rec["T"], threshold)
    ep = res.episode
    return {"cls": res.cls, "onset": math.nan if ep is None else float(ep.onset_s), "end": math.nan if ep is None else float(ep.end_s),
            "fpk": math.nan if ep is None else float(ep.f_pk_hz), "terminated": None if ep is None else bool(ep.terminated)}


# --- own signal code ---------------------------------------------------------------------------------------------------------------------------

def bandpass(v, fs: float, band=BAND):
    sos = signal.butter(ORDER, band, btype="bandpass", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, np.asarray(v, float))


def cycle_frequency(v, fs: float, t_start: float, t_end: float, band=BAND) -> tuple[float, int]:
    """Cycle frequency (Hz) of the band-passed v between t_start and t_end by upward zero crossings, linearly interpolated: (n crossings - 1) / (t_last - t_first).
    Returns (nan, n) when there are fewer than two crossings."""
    x = bandpass(v, fs, band)
    i0, i1 = int(round(t_start * fs)), int(round(t_end * fs))
    seg = x[i0:i1 + 1]
    up = np.flatnonzero((seg[:-1] < 0.0) & (seg[1:] >= 0.0))
    if up.size < 2:
        return math.nan, int(up.size)
    t = (i0 + up + (0.0 - seg[up]) / (seg[up + 1] - seg[up])) / fs
    return float((up.size - 1) / (t[-1] - t[0])), int(up.size)


def overlap_window_psd_argmax(v, fs: float, a_s: float, b_s: float, T_ramp_s: float, band=BAND) -> float:
    """Reading (ii) of the network f_pk, as described in DL-401 (method taken from the original behaviour, arithmetic independent): the Hann spectrogram of the WHOLE record
    (window W of the Table 2.1 window rule for T_ramp, step per that rule, linear detrend, density scaling, window centres in seconds from 0); keep the windows whose centre lies in
    [a_s, b_s] (inclusive, 1e-9 s); mean PSD over them; frequency of the maximum in band[0] <= f < band[1], no interpolation. nan if no window centre lies in the span."""
    W, step = M.window_for_ramp(T_ramp_s)
    nper, nstep = int(round(W * fs)), max(1, int(round(step * fs)))
    f, t, S = signal.spectrogram(np.asarray(v, float), fs=fs, window="hann", nperseg=nper, noverlap=nper - nstep, detrend="linear", scaling="density", mode="psd")
    sel = (t >= a_s - TOL) & (t <= b_s + TOL)
    if not sel.any():
        return math.nan
    bsel = (f >= band[0]) & (f < band[1])
    return float(f[bsel][np.argmax(S[bsel][:, sel].mean(axis=1))])


def eta_at(rec: dict, t_s: float) -> float:
    """eta of the stored path at time t_s, read from the stored eta series on the 1/fs grid (the onsets are on that grid)."""
    if not math.isfinite(t_s):
        return math.nan
    return float(rec["eta"][int(round(t_s * rec["fs"]))])


def delay_vs_hopf(rec: dict, onset_s: float) -> float:
    if not math.isfinite(onset_s):
        return math.nan
    return eta_at(rec, onset_s) - float(rec["cfg"]["path"]["eta_H"])


# --- counts and verdicts -----------------------------------------------------------------------------------------------------------------------

def count_kept(classes, kept=SURGE_N) -> int:
    return sum(1 for c in classes if c in kept)


def class_counts(classes) -> dict:
    out: dict = {}
    for c in classes:
        out[c] = out.get(c, 0) + 1
    return out


def rb2_status(kept: int, k: int) -> str:
    return "PASS" if ge(kept, k) else "FAIL"


def median_of(values) -> float:
    a = [x for x in values if x is not None and math.isfinite(x)]
    return float(np.median(a)) if a else math.nan


def direction_word(medians: list[float]) -> str:
    """Direction of the median over the three floor levels (RB3(b) form): 'undefined' when any level has no median."""
    if any(not math.isfinite(m) for m in medians):
        return "undefined"
    d = np.diff(medians)
    if np.all(d < 0):
        return "strict decrease"
    if np.all(d > 0):
        return "strict increase"
    return "not monotone"


def fpk_pair(f1: float, f2: float, bound: float) -> dict:
    """RB6 network: relative change of f_pk when dt is halved (against the dt 1e-3 value). Strictly less than the bound passes; an undefined f_pk at either dt is NOT EVALUABLE."""
    if not (math.isfinite(f1) and math.isfinite(f2)):
        return {"rel": math.nan, "diff_hz": math.nan, "status": "NOT EVALUABLE"}
    rel = abs(f2 - f1) / f1
    return {"rel": float(rel), "diff_hz": float(f2 - f1), "status": "PASS" if lt(rel, bound) else "FAIL"}


def reading_verdict(pairs: list[dict]) -> str:
    st = [p["status"] for p in pairs]
    if "FAIL" in st:
        return "FAIL"
    return "PASS" if "PASS" in st else "NOT EVALUABLE"


def network_verdict(per_reading: list[str]) -> str:
    if "FAIL" in per_reading:
        return "FAIL"
    return "PASS" if all(s == "PASS" for s in per_reading) else "NOT EVALUABLE"


def changed_fraction(base: list[str], var: list[str]) -> dict:
    """Cells whose variant class differs from the stored baseline; a cell with variant class 'not_run' or a baseline that is not a class is excluded (ruling 10)."""
    ok_base = {"D-tr", "D-sus", "D-none"}
    n = ch = ex = 0
    for b, v in zip(base, var):
        if v == "not_run" or b not in ok_base:
            ex += 1
            continue
        n += 1
        ch += int(b != v)
    return {"n": n, "changed": ch, "excluded": ex, "fraction": (ch / n) if n else math.nan}


def map_fraction_status(fr: dict, bound: float) -> str:
    return "NOT EVALUABLE" if not fr["n"] else ("PASS" if le(fr["fraction"], bound) else "FAIL")


# --- one map cell, for the process pool --------------------------------------------------------------------------------------------------------

def analyse_cell(json_path: str, threshold: float, a_ref: float, variants: tuple[str, ...]) -> dict:
    """Baseline class and episode of one stored mode-D cell by the frozen classifier, the cycle frequency of its episode by the zero-crossing code, and the class under each variant."""
    rec = load_record(json_path)
    base = classify(rec, threshold)
    out = {"run": Path(json_path).stem, "T": rec["T"], "cls": base["cls"], "onset": base["onset"], "end": base["end"], "fpk": base["fpk"],
           "W": float(M.window_for_ramp(rec["T"])[0]), "cyc": math.nan, "variants": {}}
    if math.isfinite(base["onset"]):
        out["cyc"], out["n_cross"] = cycle_frequency(rec["v"], rec["fs"], base["onset"], base["end"])
    for vname in variants:
        out["variants"][vname] = A8.classify(rec["v"], rec["mode"], rec["t_on"], rec["T"], a_ref, vname)["cls"]
    return out


def analyse_record(json_path: str, threshold: float) -> dict:
    """Class, episode, delay against eta_H (classifier onset) and the config facts of one stored record."""
    rec = load_record(json_path)
    c = classify(rec, threshold)
    cfg = rec["cfg"]
    eta_H = cfg["path"].get("eta_H")
    out = {"name": rec["name"], "commit": rec["commit"], "status": rec["status"], "mode": rec["mode"], "T": rec["T"], "seed": rec["seed"], **c,
           "sigma_factor": cfg.get("noise", {}).get("sigma_factor"), "sigma": cfg.get("noise", {}).get("sigma"),
           "delta0": cfg.get("solver", {}).get("delta0"), "rtol": cfg.get("solver", {}).get("rtol"), "tau_ms": float(cfg["model"]["tau_ms"]),
           "V_peak": cfg.get("network", {}).get("V_peak"), "dt_tau": cfg.get("network", {}).get("dt_tau"),
           "delay": delay_vs_hopf(rec, c["onset"]) if eta_H is not None and rec["status"] == "ok" else math.nan}
    return out
