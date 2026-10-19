"""MS9 9b: classification of stored MS9 run records and the NC1 report (DL-216; plan 2.3 Table 2.1, 5.2 A10, Table 11.2 G7).

Analysis only: reads stored records (<name>.json with <name>.npz beside it), applies the frozen classifier (surge_metrics, unchanged;
threshold = the frozen 0.1 x A_ref through analysis.a7.frozen_inputs, which runs the criteria gate) and returns one row per run. Mode D for
kind mf (class D-tr, D-sus or D-none), mode N for kind mf_noisy and network (S+, S-rel, S-abs, S-sus or NS); a record that is not ok, or
whose output is not finite, is 'failed', never NS (A9, 10.4). The sampling rate is 1 kHz for the mean field (solver.dt_out_ms) and the
network (network.rate_bin_ms).

A "surge class" is D-tr in mode D and S+, S-rel or S-abs in mode N (Table 2.1). NC1 expects NS or D-none (plan 2.4, RB7, G7); the report
also flags D-sus and S-sus, which are not NS or D-none, so that nothing but the expected result passes silently.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import a7 as A7
from . import surge_metrics as M

QUIET = {"D": "D-none", "N": "NS"}


def fs_of(cfg: dict) -> float:
    return 1000.0 / (cfg["network"]["rate_bin_ms"] if cfg["run"]["kind"] == "network" else cfg["solver"]["dt_out_ms"])


def mode_of(cfg: dict) -> str:
    return "D" if cfg["run"]["kind"] == "mf" else "N"


def classify_array(mode: str, v, fs: float, t_on: float, T_ramp_s: float, threshold: float, inside_a4_region=None):
    """(ClassResult or None, error text) for one record's v; ValueError of the classifier (record too short) is returned, not raised."""
    try:
        if mode == "D":
            return M.classify_mode_d(v, fs, t_on, T_ramp_s, threshold, inside_a4_region=inside_a4_region), ""
        return M.classify_mode_n(v, fs, t_on, T_ramp_s, threshold), ""
    except ValueError as exc:
        return None, str(exc)[:80]


def row_from_result(res, err: str, mode: str, T_ramp_s: float) -> dict:
    W, step = M.window_for_ramp(T_ramp_s)
    row = {"mode": mode, "W_s": float(W), "step_s": float(step), "class": "not_run" if res is None else res.cls,
           "reason": err if res is None else res.reason, "label_f": bool(res.label_f) if res is not None else False,
           "provisional": (res.provisional or "") if res is not None else ""}
    ep = None if res is None else res.episode
    for k in ("onset_s", "end_s", "duration_s", "cycles", "terminated", "f_pk_hz", "peak_p_g", "peak_rho"):
        row[k] = getattr(ep, k) if ep is not None else (float("nan") if k != "terminated" else None)
    row["surge"] = bool(res is not None and M.is_surge_class(res.cls))
    row["quiet"] = bool(res is not None and res.cls == QUIET[mode])
    return row


def classify_record(json_path, fi: dict | None = None, inside_a4_region=None) -> dict:
    """One row for one stored record. fi: A7.frozen_inputs()[0] (loaded once by the caller for many records)."""
    fi = fi or A7.frozen_inputs()[0]
    jp = Path(json_path)
    rec = json.loads(jp.read_text(encoding="utf-8"))
    cfg = rec["config"]
    p = cfg["path"]
    mode = mode_of(cfg)
    key = cfg["seeds"]["spawn_key"]
    base = {"run": jp.stem, "family": jp.parent.name, "supplementary": "supp" in jp.parts, "kind": cfg["run"]["kind"], "path_name": p["name"],
            "T_ramp_s": float(p["T_ramp_s"]), "status": rec["status"], "config_hash12": rec["config_hash12"],
            "spawn_key": json.dumps(list(key)) if key is not None else "", "seed": int(key[-1]) if key is not None and mode == "N" else -1,
            "git_commit": rec["git"]["commit"], "git_dirty": rec["git"]["dirty"], "wall_time_s": rec["wall_time_s"],
            "Delta": cfg["model"]["Delta"], "tau_d_ms": cfg["model"]["tau_d_ms"], "J0": cfg["path"]["J0"],
            "eta_start": p["eta_start"], "eta_end": p["eta_peak"]}
    if rec["status"] != "ok":
        W, step = M.window_for_ramp(base["T_ramp_s"])
        return {**base, "mode": mode, "W_s": float(W), "step_s": float(step), "class": M.FAILED, "reason": f"record status {rec['status']}",
                "surge": False, "quiet": False, "label_f": False, "provisional": ""}
    with np.load(jp.with_suffix(".npz")) as z:
        v = z["v"]
    res, err = classify_array(mode, v, fs_of(cfg), p["t_on_s"], base["T_ramp_s"], fi["threshold"], inside_a4_region)
    return {**base, **row_from_result(res, err, mode, base["T_ramp_s"])}


def record_files(root) -> list[Path]:
    """Run records (not dry-run files, not the journals) under root, sorted."""
    return sorted(p for p in Path(root).rglob("*.json") if not p.name.endswith(".dry.json") and p.with_suffix(".npz").exists())


def classify_tree(root, fi: dict | None = None) -> list[dict]:
    fi = fi or A7.frozen_inputs()[0]
    return [classify_record(p, fi) for p in record_files(root)]


# --- NC1 report ---------------------------------------------------------------------------------

def unexpected(rows: list[dict], pre_registered_only: bool = True) -> list[dict]:
    """Rows that are not the expected NC1 result (NS in mode N, D-none in mode D): the STOP-RULE set. Failed runs are included."""
    return [r for r in rows if not (r["quiet"]) and not (pre_registered_only and r["supplementary"])]


def supplementary_per_window(rows: list[dict]) -> list[dict]:
    """Supplementary NC1 mode N: per T_ramp (window W) the number of seeds, non-NS runs, the fraction, and the class counts."""
    out = []
    sup = [r for r in rows if r["supplementary"] and r["mode"] == "N"]
    for T in sorted({r["T_ramp_s"] for r in sup}):
        g = [r for r in sup if r["T_ramp_s"] == T]
        counts: dict[str, int] = {}
        for r in g:
            counts[r["class"]] = counts.get(r["class"], 0) + 1
        non = sum(1 for r in g if r["class"] != "NS")
        out.append({"T_ramp_s": T, "W_s": g[0]["W_s"], "step_s": g[0]["step_s"], "n": len(g), "non_NS": non, "fraction_non_NS": non / len(g),
                    "counts": counts})
    return out


def _cl(r: dict) -> str:
    return r["class"] + ("*" if r.get("provisional") else "")


def nc1_report(rows: list[dict]) -> str:
    pre = [r for r in rows if not r["supplementary"]]
    L = ["NC1 classes (mode D: D-none expected; mode N: NS expected). * = class depended on the D8 call (provisional, gate departure 1).", ""]
    mf = sorted([r for r in pre if r["family"] == "NC1"], key=lambda r: r["T_ramp_s"])
    L.append("Mean field, headline cell, class per T_ramp:")
    for r in mf:
        L.append(f"  T_ramp {r['T_ramp_s']:8.3f} s  W {r['W_s']:.3f} s  {_cl(r):8s} {r['reason'] if r['class'] != 'D-none' else ''}  (status {r['status']})")
    L.append("")
    L.append("NC1 at the 5 map cells, T_ramp 120 s:")
    for r in sorted([r for r in pre if r["family"] == "NC1_cells"], key=lambda r: (r["Delta"], r["tau_d_ms"])):
        L.append(f"  Delta {r['Delta']:.5f}  tau_d {r['tau_d_ms']:8.4f} ms  {_cl(r):8s} {r['reason'] if r['class'] != 'D-none' else ''}  (status {r['status']})")
    L.append("")
    L.append("NC1 network run (N = 1e4, mode N, 120 s, 1 seed):")
    for r in [r for r in pre if r["family"] == "NC1_net"]:
        L.append(f"  {_cl(r):8s} W {r['W_s']:.3f} s  {r['reason']}  (status {r['status']})")
    L.append("")
    L.append("SUPPLEMENTARY NC1, mode N, headline cell, 10 seeds per T_ramp (feeds no gate; per window W):")
    for g in supplementary_per_window(rows):
        L.append(f"  T_ramp {g['T_ramp_s']:8.3f} s  W {g['W_s']:.3f} s  non-NS {g['non_NS']:2d}/{g['n']}  fraction {g['fraction_non_NS']:.2f}  {g['counts']}")
    bad = unexpected(rows)
    L.append("")
    L.append(f"STOP RULE (pre-registered NC1 runs that are not {QUIET['D']} / {QUIET['N']}, failed runs included): "
             + (", ".join(f"{r['run']}={r['class']}" for r in bad) if bad else "none"))
    return "\n".join(L)
