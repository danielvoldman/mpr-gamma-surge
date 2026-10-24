"""MS10 10d: evaluators for RB1, the sigma check, S9, S10/RB8 and G4 (docs/ms10_eval_rules.md; rulings R2, R8, R15 to R18, R23, R24).

Analysis only: it reads stored records (<name>.json with <name>.npz beside it), applies the frozen mode-N / mode-D classifier (surge_metrics,
unchanged) and the frozen RB1 / RB8 leaves (criteria gate first), and returns dicts. Nothing is integrated and nothing is plotted.

Refusals (EvalRefused): a record with git.dirty not exactly False, a dry-run record, a config hash that is not the hash of the frozen run list row
(the record's name and its full hash must both match), a criteria SHA-256 other than the frozen one, an unlisted record in a family folder, and any MS10
data file still DRAFT. An evaluation choice that the plan and the rulings leave open (E-n) is read from configs/ms10/ms10_eval.yaml; it is null there and
the evaluator raises MissingChoice when it needs one. No choice is made in this module. A missing record is reported ("missing"), never replaced.

Readings, fixed by rulings: the class of a network run is the frozen mode-N class; "same class" is the Table 2.1 correspondence (primary) or the same
with S-rel not counted (post hoc, DL-258 b); the mean-field comparator is the mode-D class of the companion run (R1, R13) or the stored record
(T_ramp 10 s and 120 s, mf_references.yaml). Post-hoc readings feed no gate.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np
import yaml

from .. import config as C
from .. import criteria as CR
from . import a7 as A7
from . import ms9_classify as MCL
from . import ms10_runlist as RL
from . import surge_metrics as M

EVAL_FILE = "configs/ms10/ms10_eval.yaml"
CHOICE_VALUES = {
    "network_onset_definition": ("classifier_centre", "classifier_start", "raw_crossing"),
    "not_evaluable_counts_as": ("not_met", "vacuous"),
    "tolerance_boundary": ("inclusive", "strict"),
    "baseline_sample_convention": ("half_open", "closed"),
    "sigma_range_bounds": ("inclusive", "strict"),
    "rb8_comparator": ("paired_by_seed_index", "modal_lorentzian_class"),
    "rb8_class_equality": ("exact_label", "surge_correspondence"),
}
METRIC_NAMES = ("onset_s", "f_pk_hz", "duration_s", "cycles", "peak_p_g", "peak_rho", "baseline_std_v")
EPS = 1e-9
SRC_LISTS = ("S8", "S9", "S10")
POSTHOC_SREL = ("S+", "S-abs")          # surge classes when S-rel is not counted (DL-258 b)


class EvalError(Exception):
    pass


class EvalRefused(EvalError):
    """A record or a data file that the evaluators do not read."""


class MissingChoice(EvalError):
    """An evaluation choice (E-n) that the plan and rulings leave open is not set in configs/ms10/ms10_eval.yaml."""


# --- choices and frozen leaves -------------------------------------------------------------------

def load_choices(path: str | Path | None = None) -> dict:
    p = Path(path) if path else C.repo_root() / EVAL_FILE
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    return doc["choices"]


def choice(ch: dict, name: str):
    """The value of one E-n choice; MissingChoice if it is absent, null or not an allowed value."""
    v = ch.get(name)
    if v is None:
        raise MissingChoice(f"evaluation choice {name!r} is not set in {EVAL_FILE}: the plan and the rulings leave it open (docs/ms10_eval_rules.md); the reviewer sets it")
    if name in CHOICE_VALUES and v not in CHOICE_VALUES[name]:
        raise MissingChoice(f"evaluation choice {name!r} = {v!r} is not one of {CHOICE_VALUES[name]}")
    return v


def _frac(text: str) -> tuple[int, int]:
    m = re.search(r"(\d+)\s+of\s+(\d+)", str(text))
    if not m:
        raise EvalError(f"frozen criterion {text!r} is not of the form 'k of n'")
    return int(m.group(1)), int(m.group(2))


def frozen_rb1(root=None) -> dict:
    """RB1 and RB8 leaves of the frozen criteria (blob of the tag, gate first)."""
    crit, info = CR.load_frozen_criteria(root)
    r1, r8 = crit["robustness"]["RB1"], crit["robustness"]["RB8"]
    seeds_k, seeds_n = _frac(r1["classes_agree_seeds"]["value"])
    cells_k, cells_n = _frac(r1["classes_agree_cells"]["value"])
    return {"criteria_sha256": info["sha256"], "seeds_k": seeds_k, "seeds_n": seeds_n, "cells_k": cells_k, "cells_n": cells_n,
            "f_pk_rel_tol": float(r1["f_pk_rel_tol"]["value"]), "rb8_seeds": int(r8["gaussian_uniform_give_lorentzian_class_seeds"]["value"])}


# --- records ----------------------------------------------------------------------------------------

def expected_rows(lists, require_frozen: bool = True) -> dict:
    """{list name: rows} of the frozen run lists. Refuses while any MS10 data file is DRAFT."""
    if require_frozen and RL.is_draft():
        raise EvalRefused(f"the MS10 data files are DRAFT, not frozen: {RL.status()}")
    return {n: RL.expand(n) for n in lists}


def _finite(x) -> bool:
    return x is not None and math.isfinite(float(x))


def check_record(rec: dict, row: dict, criteria_sha256: str) -> None:
    """EvalRefused unless the record is a clean, non-dry run of exactly this row of the frozen list."""
    git = rec.get("git") or {}
    if git.get("dirty") is not False:
        raise EvalRefused(f"{row['name']}: git dirty flag is {git.get('dirty')!r}; only dirty = false records are evaluated")
    if rec.get("dry_run"):
        raise EvalRefused(f"{row['name']}: dry-run record")
    if rec.get("config_hash") != row["hash"]:
        raise EvalRefused(f"{row['name']}: config hash {str(rec.get('config_hash'))[:12]} differs from the frozen list ({row['hash'][:12]})")
    if rec.get("name") != row["name"]:
        raise EvalRefused(f"{row['name']}: record name {rec.get('name')!r} is not the listed name")
    if rec.get("criteria_sha256") != criteria_sha256:
        raise EvalRefused(f"{row['name']}: criteria SHA-256 {rec.get('criteria_sha256')} is not the frozen one")


def record_path(row: dict) -> Path:
    return Path(row["out_dir"]) / f"{row['name']}.json"


def unlisted_records(rows_by_list: dict, roots=None) -> list[str]:
    """Run records in a family folder of the lists that are not rows of the frozen lists (stale or foreign records)."""
    listed = {record_path(r).resolve() for rows in rows_by_list.values() for r in rows}
    dirs = {Path(r["out_dir"]) for rows in rows_by_list.values() for r in rows}
    found = []
    for d in dirs:
        if d.is_dir():
            found += [p for p in MCL.record_files(d) if p.resolve() not in listed and p.parent.resolve() == d.resolve()]
    return sorted(str(p) for p in found)


def _baseline_std(v, fs, t_on, baseline_s, convention):
    i1 = int(round(t_on * fs))
    i0 = i1 - int(round(baseline_s * fs))
    seg = np.asarray(v, float)[i0:i1 + (1 if convention == "closed" else 0)]
    return float(np.std(seg, ddof=1))


def _raw_crossing_s(v, fs, t_on, threshold):
    """First time at or after t_on at which the band-passed Hilbert envelope reaches the threshold (the mode-D raw crossing, no cycle count, no D8)."""
    env = M.envelope(v, fs, M.G_BAND)
    i_on = int(round(t_on * fs))
    hit = np.flatnonzero(env[i_on:] >= threshold)
    return float((hit[0] + i_on) / fs) if hit.size else float("nan")


def read_record(row: dict, fi: dict, criteria_sha256: str | None = None) -> dict:
    """One record of a listed row: refusals first, then the class and the metrics. {'name', 'missing': True} if the file is absent.

    Network rows: frozen mode-N class and all candidate onset readings and both baseline-window conventions (E-1, E-4 select later). Mean-field rows: mode D."""
    jp = record_path(row)
    if not jp.exists():
        return {"name": row["name"], "list": row["list"], "missing": True}
    rec = json.loads(jp.read_text(encoding="utf-8"))
    check_record(rec, row, criteria_sha256 or fi["criteria_sha256"])
    cfg = row["cfg"]
    p = cfg["path"]
    mode = MCL.mode_of(cfg)
    T = float(p["T_ramp_s"])
    W, step = M.window_for_ramp(T)
    key = row["spawn_key"]
    out = {"name": row["name"], "list": row["list"], "family": row["family"], "hash": row["hash"], "missing": False, "mode": mode, "spawn_key": key,
           "seed": int(key[-1]) if key else -1, "group": int(key[2]) if key and len(key) > 3 else None, "T_ramp_s": T,
           "N": cfg["network"]["N"] if cfg["run"]["kind"] == "network" else None,
           "het_dist": cfg["network"]["het_dist"] if cfg["run"]["kind"] == "network" else None,
           "Delta": cfg["model"]["Delta"], "tau_d_ms": cfg["model"]["tau_d_ms"], "status": rec["status"], "git_dirty": rec["git"]["dirty"],
           "W_s": float(W), "step_s": float(step), "bin_hz": 1.0 / float(W)}
    if rec["status"] != "ok":
        return {**out, "class": M.FAILED, "reason": f"record status {rec['status']}", "surge": False, "quiet": False}
    with np.load(jp.with_suffix(".npz")) as z:
        v = z["v"]
    fs = MCL.fs_of(cfg)
    res, err = MCL.classify_array(mode, v, fs, p["t_on_s"], T, fi["threshold"])
    out.update(MCL.row_from_result(res, err, mode, T))
    if mode == "N":
        out["onset_classifier_centre_s"] = out["onset_s"]
        out["onset_classifier_start_s"] = out["onset_s"] - W / 2 if _finite(out["onset_s"]) else float("nan")
        out["onset_raw_crossing_s"] = _raw_crossing_s(v, fs, p["t_on_s"], fi["threshold"]) if res is not None else float("nan")
        for conv in CHOICE_VALUES["baseline_sample_convention"]:
            out[f"baseline_std_v_{conv}"] = _baseline_std(v, fs, p["t_on_s"], M.BASELINE_S, conv)
    return out


def read_lists(lists, fi: dict, require_frozen: bool = True) -> dict:
    """{list: [record dicts in list order]}; refuses unlisted records in the family folders."""
    rows = expected_rows(lists, require_frozen)
    stray = unlisted_records(rows)
    if stray:
        raise EvalRefused(f"{len(stray)} record(s) in the family folders are not rows of the frozen lists, e.g. {stray[0]}")
    return {n: [read_record(r, fi) for r in rs] for n, rs in rows.items()}


# --- readings ---------------------------------------------------------------------------------------

def surge_set(posthoc: bool = False):
    return POSTHOC_SREL if posthoc else M.SURGE_CLASSES


def matches(ref_cls: str, cls: str, posthoc: bool = False) -> bool:
    """Table 2.1 correspondence of the mean-field class to the network class (primary); posthoc: S-rel not counted (DL-258 b)."""
    ok = M.classes_agree(ref_cls, cls)
    return ok and not (posthoc and ref_cls == "D-tr" and cls == "S-rel")


def onset_of(rec: dict, ch: dict) -> float:
    """The network onset by E-1 (MissingChoice if unset). NaN where the reading is undefined for the record."""
    d = choice(ch, "network_onset_definition")
    return float(rec.get({"classifier_centre": "onset_classifier_centre_s", "classifier_start": "onset_classifier_start_s",
                          "raw_crossing": "onset_raw_crossing_s"}[d], float("nan")))


def metric_of(rec: dict, name: str, ch: dict) -> float:
    if name == "onset_s":
        return onset_of(rec, ch)
    if name == "baseline_std_v":
        return float(rec[f"baseline_std_v_{choice(ch, 'baseline_sample_convention')}"])
    return float(rec.get(name, float("nan")))


def _within(diff: float, tol: float, boundary: str) -> bool:
    return diff <= tol + EPS if boundary == "inclusive" else diff < tol - EPS


def _policy(v, ch):
    """True / False / None (not evaluable) to a bool by E-2."""
    if v is None:
        return choice(ch, "not_evaluable_counts_as") == "vacuous"
    return bool(v)


def seed_assessment(rec: dict, ref: dict, ch: dict, tol: float) -> dict:
    """RB1 for one network run against its mean-field reference (R23): class (both readings), f_pk within tol, onset within one spectrogram step."""
    out = {"name": rec["name"], "seed": rec["seed"], "class": rec["class"], "ref_class": ref["class"],
           "class_match": matches(ref["class"], rec["class"]), "class_match_posthoc": matches(ref["class"], rec["class"], posthoc=True)}
    bd = choice(ch, "tolerance_boundary")
    f, rf = rec.get("f_pk_hz"), ref.get("f_pk_hz")
    out["f_pk_hz"], out["f_pk_ref_hz"], out["bin_hz"] = f, rf, rec["bin_hz"]
    if _finite(f) and _finite(rf) and ref["class"] == "D-tr":
        out["f_pk_rel_err"] = abs(f - rf) / rf
        out["f_pk_diff_hz"] = f - rf
        out["f_pk_diff_bins"] = (f - rf) / rec["bin_hz"]
        out["f_pk_ok"] = _within(out["f_pk_rel_err"], tol, bd)
    else:
        out["f_pk_rel_err"] = out["f_pk_diff_hz"] = out["f_pk_diff_bins"] = float("nan")
        out["f_pk_ok"] = None
    on, ron = onset_of(rec, ch), ref.get("onset_s")
    out["onset_s"], out["onset_ref_s"], out["step_s"] = on, ron, rec["step_s"]
    if _finite(on) and _finite(ron) and ref["class"] == "D-tr":
        out["onset_diff_s"] = on - ron
        out["onset_ok"] = _within(abs(on - ron), rec["step_s"], bd)
    else:
        out["onset_diff_s"] = float("nan")
        out["onset_ok"] = None
    out["f_pk_ok_policy"], out["onset_ok_policy"] = _policy(out["f_pk_ok"], ch), _policy(out["onset_ok"], ch)
    out["pass"] = bool(out["class_match"] and out["f_pk_ok_policy"] and out["onset_ok_policy"])
    out["pass_srel_not_counted"] = bool(out["class_match_posthoc"] and out["f_pk_ok_policy"] and out["onset_ok_policy"])
    return out


def config_key(rec_or_cfg) -> tuple:
    """(N, T_ramp, het_dist, Delta, tau_d) that ties a ramp run to its constant-parameter control."""
    r = rec_or_cfg
    return (r["N"], r["T_ramp_s"], r["het_dist"], round(float(r["Delta"]), 12), round(float(r["tau_d_ms"]), 12))


def control_classes(ramp_rec: dict, controls: list[dict]) -> dict:
    """Class counts of the C2 control seeds with the configuration of the ramp run (R17); reported beside, no verdict."""
    mine = [c for c in controls if not c.get("missing") and config_key(c) == config_key(ramp_rec)]
    return {"n": len(mine), "classes": dict(Counter(c["class"] for c in mine)), "surge": sum(1 for c in mine if c["surge"]),
            "missing_controls_in_list": sum(1 for c in controls if c.get("missing"))}


def _med_range(xs):
    xs = [float(x) for x in xs if _finite(x)]
    return {"n": len(xs), "median": float(np.median(xs)) if xs else float("nan"), "min": min(xs) if xs else float("nan"),
            "max": max(xs) if xs else float("nan")}


# --- references --------------------------------------------------------------------------------------

def _mf_ref(rec: dict, source: str) -> dict:
    return {"class": rec["class"], "onset_s": rec.get("onset_s"), "f_pk_hz": rec.get("f_pk_hz"), "source": source, "name": rec["name"]}


def mf_references(fi: dict, require_frozen: bool = True) -> dict:
    """{('head', T): ref, ('cell', c): ref}: stored records (T 10 and 120 s, R13; SHA-256 verified) and the companion runs (cells at 30 s, headline at 60 s)."""
    RL.verify_references()
    refs = {}
    for r in RL._read(RL.REFS_FILE)["references"]:
        sc = r["stored_class"]
        refs[("head", float(r["T_ramp_s"]))] = {"class": sc["class"], "onset_s": sc["onset_s"], "f_pk_hz": sc["f_pk_hz"], "source": f"stored {r['run_id']}", "name": r["run_id"]}
    rows = expected_rows(("MF_COMPANION",), require_frozen)["MF_COMPANION"]
    recs = [read_record(r, fi) for r in rows]
    for r, rec in zip(rows, recs):
        if rec.get("missing"):
            continue
        key = ("head", float(rec["T_ramp_s"])) if r["family"] == "S8_mf_head60" else ("cell", r["index"])
        refs[key] = _mf_ref(rec, "companion")
    return refs


def stored_120s_classes() -> dict:
    """{cell c: stored map-1 mode-D class at T_ramp 120 s} for the four S8 cells (10b candidate table, stored, not recomputed)."""
    import csv
    with open(C.repo_root() / RL.CANDIDATES_FILE, newline="", encoding="utf-8") as fh:
        cand = {(int(r["i"]), int(r["j"])): r["class"] for r in csv.DictReader(fh)}
    return {e["c"]: cand[(int(e["i"]), int(e["j"]))] for e in RL._read(RL.CELLS_FILE)["cells"]}


# --- RB1 ----------------------------------------------------------------------------------------------

def rb1_headline(recs: list[dict], refs: dict, controls: list[dict], ch: dict, fr: dict) -> dict:
    out = {}
    for T in sorted({r["T_ramp_s"] for r in recs}):
        ref = refs.get(("head", T))
        group = sorted([r for r in recs if r["T_ramp_s"] == T], key=lambda r: r["seed"])
        part = {"T_ramp_s": T, "ref": ref, "seeds_expected": fr["seeds_n"], "seeds_present": sum(1 for r in group if not r.get("missing"))}
        if ref is None or part["seeds_present"] < fr["seeds_n"]:
            part.update(complete=False, verdict="INCOMPLETE")
            out[T] = part
            continue
        sa = [seed_assessment(r, ref, ch, fr["f_pk_rel_tol"]) for r in group]
        part["seeds"] = sa
        part["controls"] = control_classes(group[0], controls)
        part["pass_count"] = sum(s["pass"] for s in sa)
        part["pass_count_srel_not_counted"] = sum(s["pass_srel_not_counted"] for s in sa)
        part["verdict"] = "PASS" if part["pass_count"] >= fr["seeds_k"] else "FAIL"
        # post hoc (R23): medians over the seeds for f_pk and onset; feeds no gate
        bd = choice(ch, "tolerance_boundary")
        mf, mo = _med_range([s["f_pk_hz"] for s in sa])["median"], _med_range([s["onset_s"] for s in sa])["median"]
        part["posthoc_median"] = {"f_pk_median_hz": mf, "onset_median_s": mo,
                                  "f_pk_ok": bool(ref["class"] == "D-tr" and _finite(mf) and _within(abs(mf - ref["f_pk_hz"]) / ref["f_pk_hz"], fr["f_pk_rel_tol"], bd)),
                                  "onset_ok": bool(ref["class"] == "D-tr" and _finite(mo) and _within(abs(mo - ref["onset_s"]), group[0]["step_s"], bd)),
                                  "classes_all_match": all(s["class_match"] for s in sa), "label": "post hoc, feeds no gate"}
        part["complete"] = True
        out[T] = part
    return out


def rb1_cells(recs: list[dict], refs: dict, controls: list[dict], stored120: dict, fr: dict) -> dict:
    """Per S8 map cell: all seeds in the matching class (R15); RB1 needs cells_k of cells_n."""
    cells = {}
    for c in sorted({r["group"] for r in recs}):
        group = sorted([r for r in recs if r["group"] == c], key=lambda r: r["seed"])
        ref = refs.get(("cell", c))
        n = sum(1 for r in group if not r.get("missing"))
        d = {"cell": c, "ref": ref, "stored_120s_class": stored120.get(c), "seeds_present": n}
        if ref is None or n < fr["seeds_n"]:
            d.update(complete=False, agrees=None)
        else:
            d.update(complete=True, classes=[r["class"] for r in group], controls=control_classes(group[0], controls),
                     matches=[matches(ref["class"], r["class"]) for r in group], matches_srel_not_counted=[matches(ref["class"], r["class"], True) for r in group])
            d["agrees"] = all(d["matches"])
            d["agrees_srel_not_counted"] = all(d["matches_srel_not_counted"])
        cells[c] = d
    done = [d for d in cells.values() if d["complete"]]
    n_agree = sum(1 for d in done if d["agrees"])
    return {"cells": cells, "n_cells": len(cells), "n_complete": len(done), "n_agree": n_agree, "n_agree_srel_not_counted": sum(1 for d in done if d["agrees_srel_not_counted"]),
            "need": fr["cells_k"], "verdict": "INCOMPLETE" if len(done) < fr["cells_n"] else ("PASS" if n_agree >= fr["cells_k"] else "FAIL"),
            "disagree": None if len(done) < fr["cells_n"] else len(done) - n_agree}


def n_sweep(recs: list[dict], ref: dict | None, controls: list[dict], ch: dict, fr: dict, metrics: bool = False) -> dict:
    """S9 by N: class counts, seeds in the MF-matching class, f_pk and onset errors (median, range; reported, not a pass test).
    RB1 N rule (R18): seeds in the matching class at N = 3e4 at least as many as at N = 1e4."""
    by_n = {}
    for N in sorted({r["N"] for r in recs}):
        g = sorted([r for r in recs if r["N"] == N], key=lambda r: r["seed"])
        live = [r for r in g if not r.get("missing")]
        d = {"N": N, "seeds_present": len(live), "classes": dict(Counter(r["class"] for r in live)), "surge_seeds": sum(1 for r in live if r["surge"]),
             "surge_seeds_srel_not_counted": sum(1 for r in live if r["class"] in POSTHOC_SREL)}
        if ref is not None:
            d["match_seeds"] = sum(matches(ref["class"], r["class"]) for r in live)
            d["match_seeds_srel_not_counted"] = sum(matches(ref["class"], r["class"], True) for r in live)
            if ref["class"] == "D-tr":
                d["f_pk_rel_err"] = _med_range([abs(r["f_pk_hz"] - ref["f_pk_hz"]) / ref["f_pk_hz"] for r in live if _finite(r.get("f_pk_hz"))])
                d["onset_abs_err_s"] = _med_range([abs(onset_of(r, ch) - ref["onset_s"]) for r in live if _finite(onset_of(r, ch))])
        if live:
            d["controls"] = control_classes(live[0], controls)
            d["bin_hz"] = live[0]["bin_hz"]
        if metrics:
            names = choice(ch, "s9_metrics")
            bad = [m for m in names if m not in METRIC_NAMES]
            if bad:
                raise MissingChoice(f"s9_metrics names {bad} are not in {METRIC_NAMES}")
            d["metrics"] = {m: _med_range([metric_of(r, m, ch) for r in live if r["class"] != M.FAILED]) for m in names}
        by_n[N] = d
    out = {"by_N": by_n, "ref": ref}
    ns = sorted(by_n)
    if ref is not None and len(ns) >= 2 and 10000 in by_n and 30000 in by_n:
        a, b = by_n[10000], by_n[30000]
        full = a["seeds_present"] == b["seeds_present"] == 10
        out["no_worse"] = {"count_1e4": a["match_seeds"], "count_3e4": b["match_seeds"], "pass": (b["match_seeds"] >= a["match_seeds"]) if full else None,
                           "count_1e4_srel_not_counted": a["match_seeds_srel_not_counted"], "count_3e4_srel_not_counted": b["match_seeds_srel_not_counted"],
                           "complete": full}
    else:
        out["no_worse"] = {"complete": False, "pass": None}
    return out


def rb1_overall(head: dict, cells: dict, nsw: dict) -> dict:
    parts = {"headline": {T: p["verdict"] for T, p in head.items()}, "cells": cells["verdict"],
             "N_rule": "INCOMPLETE" if nsw["no_worse"].get("pass") is None else ("PASS" if nsw["no_worse"]["pass"] else "FAIL")}
    vals = list(parts["headline"].values()) + [parts["cells"], parts["N_rule"]]
    v = "INCOMPLETE" if "INCOMPLETE" in vals else ("PASS" if all(x == "PASS" for x in vals) else "FAIL")
    return {"parts": parts, "verdict": v, "label": "primary reading (Table 2.1 correspondence); post-hoc readings are reported beside each part and feed no gate"}


# --- sigma check ---------------------------------------------------------------------------------------

def sigma_check(head_recs: list[dict], ch: dict) -> dict:
    """R16: the mean-field baseline std of v lies inside the range of the network baseline std over the S8 headline baselines (same 5 s window).
    Sigma is never changed here. The mean-field value is a required choice (R21: not confirmed at 10d)."""
    mf = choice(ch, "mf_baseline_std")
    choice(ch, "mf_baseline_std_source")
    conv, bounds = choice(ch, "baseline_sample_convention"), choice(ch, "sigma_range_bounds")
    live = [r for r in head_recs if not r.get("missing") and r["class"] != M.FAILED]
    if len(live) < len(head_recs):
        return {"verdict": "INCOMPLETE", "n_runs": len(live), "n_expected": len(head_recs)}
    vals = [r[f"baseline_std_v_{conv}"] for r in live]
    lo, hi = min(vals), max(vals)
    inside = (lo <= mf <= hi) if bounds == "inclusive" else (lo < mf < hi)
    return {"verdict": "PASS" if inside else "NOT INSIDE (limitation; sigma stays frozen)", "mf_baseline_std": float(mf), "network_min": lo, "network_max": hi,
            "network_mean": float(np.mean(vals)), "n_runs": len(vals), "n_distinct_values": len({round(x, 12) for x in vals}), "bounds": bounds,
            "per_run": {r["name"]: r[f"baseline_std_v_{conv}"] for r in live}, "mf_over_network_mean": float(mf / np.mean(vals)), "sigma_changed": False}


# --- S10 / RB8 -----------------------------------------------------------------------------------------

def _same(a: str, b: str, how: str, posthoc: bool = False) -> bool:
    if how == "exact_label":
        return a == b
    s = surge_set(posthoc)
    return (a in s) == (b in s) and (a == b or a in s)


def rb8(recs: list[dict], controls: list[dict], ref: dict | None, ch: dict, fr: dict) -> dict:
    """R8: Gaussian and uniform give the Lorentzian network class in rb8_seeds of 3 seeds (comparator by E-7, equality by E-8)."""
    comp, how = choice(ch, "rb8_comparator"), choice(ch, "rb8_class_equality")
    lor = sorted([r for r in recs if r["het_dist"] == "lorentzian"], key=lambda r: r["seed"])
    out = {"comparator": comp, "equality": how, "shapes": {}}
    if len(lor) < 3 or any(r.get("missing") for r in lor):
        return {**out, "verdict": "INCOMPLETE", "reason": "Lorentzian runs missing"}
    lcls = [r["class"] for r in lor]
    modal = Counter(lcls).most_common()
    tie = len(modal) > 1 and modal[0][1] == modal[1][1]
    out["lorentzian_classes"] = lcls
    out["lorentzian_controls"] = control_classes(lor[0], controls)
    verdicts = []
    for shape in ("gaussian", "uniform"):
        g = sorted([r for r in recs if r["het_dist"] == shape], key=lambda r: r["seed"])
        if len(g) < 3 or any(r.get("missing") for r in g):
            out["shapes"][shape] = {"verdict": "INCOMPLETE"}
            verdicts.append("INCOMPLETE")
            continue
        if comp == "paired_by_seed_index":
            comps = [lor[i]["class"] for i in range(len(g))]
        elif tie:
            out["shapes"][shape] = {"verdict": "UNDETERMINED", "reason": "modal Lorentzian class is tied"}
            verdicts.append("UNDETERMINED")
            continue
        else:
            comps = [modal[0][0]] * len(g)
        hit = [_same(r["class"], c, how) for r, c in zip(g, comps)]
        hit_ph = [_same(r["class"], c, how, posthoc=True) for r, c in zip(g, comps)]
        d = {"classes": [r["class"] for r in g], "comparator_classes": comps, "hits": sum(hit), "hits_srel_not_counted": sum(hit_ph),
             "controls": control_classes(g[0], controls), "verdict": "PASS" if sum(hit) >= fr["rb8_seeds"] else "FAIL"}
        if ref is not None:
            d["match_mf_seeds"] = sum(matches(ref["class"], r["class"]) for r in g)
        out["shapes"][shape] = d
        verdicts.append(d["verdict"])
    out["verdict"] = "INCOMPLETE" if "INCOMPLETE" in verdicts else ("UNDETERMINED" if "UNDETERMINED" in verdicts else ("PASS" if all(v == "PASS" for v in verdicts) else "FAIL"))
    out["lorentzian_mf_match_seeds"] = sum(matches(ref["class"], c) for c in lcls) if ref is not None else None
    return out


# --- G4 --------------------------------------------------------------------------------------------------

def g4_summary(by_list: dict, rb1: dict, cells: dict, ch: dict) -> dict:
    """R24: the network misses the surge at an N when no seed at that N is in a surge class (primary reading). Report-only for the run order.
    Text of the three plan consequences (Tables 4.2 and 11.2) with whether each condition holds."""
    src = choice(ch, "g4_source_lists")
    bad = [s for s in src if s not in SRC_LISTS]
    if bad:
        raise MissingChoice(f"g4_source_lists {bad} are not in {SRC_LISTS}")
    recs = [r for n in src for r in by_list.get(n, [])]
    miss = {}
    for N in (10000, 30000):
        g = [r for r in recs if r.get("N") == N and not r.get("missing")]
        miss[N] = {"records": len(g), "surge_seeds": sum(1 for r in g if r["surge"]),
                   "surge_seeds_srel_not_counted": sum(1 for r in g if r["class"] in POSTHOC_SREL),
                   "misses": (sum(1 for r in g if r["surge"]) == 0) if g else None}
    both = None if any(m["misses"] is None for m in miss.values()) else all(m["misses"] for m in miss.values())
    dis = cells.get("disagree")
    c2 = None if dis is None else dis >= 2
    ok = rb1["verdict"]
    text = [
        "RB1 passes: continue (G4 not triggered)." if ok == "PASS" else ("RB1 does not pass: G4 is evaluated." if ok == "FAIL" else "RB1 is incomplete: G4 cannot be stated."),
        f"(1) Network misses the surge at N = 1e4 and 3e4 (no seed at that N in a surge class): {_yn(both)} -> if yes, report a finite-size limitation (Part 1, Table 4.2); keep the model.",
        f"(2) Disagreement in 2 or more of the 4 cells: {_yn(c2)} -> if yes, rerun RB6 (its network parts, the dt ladder and V_p, are S13 runs at MS11; R9). Known caveats: OA attraction with synaptic kinetics is unproven; shot noise causes metastability [R1, 2.6].",
        "(3) Report the affected results as mean-field-only: applies when (1) or (2) holds (our reading of the Table 11.2 sentence, UNVERIFIED).",
        "G4 is report-only for the run order (Table 11.2 footnote); it limits claims to the mean field, it stops nothing.",
    ]
    return {"misses_by_N": miss, "misses_both": both, "cells_disagree_2_or_more": c2, "triggered": None if (both is None and c2 is None) else bool(both or c2),
            "rb1": ok, "text": text}


def _yn(x):
    return "not evaluable (records missing)" if x is None else ("YES" if x else "no")
