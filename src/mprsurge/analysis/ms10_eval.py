"""MS10 10d/10e: evaluators for RB1, the sigma check, S9, S10/RB8 and G4 (docs/ms10_eval_rules.md; rulings R2, R8, R15 to R18, R23 to R28).

Analysis only: it reads stored records (<name>.json with <name>.npz beside it), applies the frozen mode-N / mode-D classifier (surge_metrics,
unchanged) and the frozen RB1 / RB8 leaves (criteria gate first), and returns dicts. Nothing is integrated and nothing is plotted.

Refusals (EvalRefused): a record with git.dirty not exactly False, a dry-run record, a config hash that is not the hash of the frozen run list row
(the record's name and its full hash must both match), a criteria SHA-256 other than the frozen one, an unlisted record in a family folder, and any MS10
data file still DRAFT. The evaluation choices E-1 to E-10 are ruled (R25 to R28) and read from configs/ms10/ms10_eval.yaml; a null or absent choice raises
MissingChoice (nothing is defaulted in this module). A missing record is reported ("missing"), never replaced.
Network onset (R27): the classifier onset (centre of the first flagged window); the evaluator's own raw crossing is a secondary, post-hoc reading. Before a
network record is read, check_time_origin compares the time origins of the classifier onset and of the mean-field onset and stops on a mismatch.
Sigma check (R28): one common window, samples [0, 5000) of v, std with ddof 1, for the reference and for every network baseline.

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
    "network_onset_definition": ("classifier_centre",),                  # E-1 / R27
    "not_evaluable_counts_as": ("not_met", "vacuous"),                   # E-2 ruled: not_met (undefined fails)
    "tolerance_boundary": ("inclusive", "strict"),                       # E-3 ruled: inclusive
    "sigma_range_bounds": ("inclusive", "strict"),                       # E-5 ruled: inclusive
    "rb8_comparator": ("common_lorentzian_class",),                      # E-7
    "rb8_class_equality": ("surge_correspondence",),                    # E-8 ruled
}
SIGMA_WINDOW = (0, 5000)                 # R28: samples [0, 5000) of v (the 5 s baseline of Table 2.1 at 1 kHz); not the classifier's own baseline windows
SIGMA_DDOF = 1
# E-6: the Table 2.1 Metrics row. Names are the keys of the record dicts; J_exit_*, exit_delay and r_post_* are P2-based paths only.
METRIC_NAMES = ("onset_s", "eta_onset", "delay_eta", "duration_ms", "duration_cycles", "duration_frac_ramp", "peak_power_abs", "peak_power_rel", "f_pk_hz",
                "J_exit_run", "J_exit_static", "exit_delay", "r_post_1s", "r_post_5s", "baseline_std_v")
TABLE21_METRICS = METRIC_NAMES[:-1]
EPS = 1e-9
SRC_LISTS = ("S8", "S9", "S10")
ONSET_TOL_STEPS = 1.0                    # R27: one spectrogram step (Table 2.1), inclusive (E-3)
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


def sigma_window_of(ch: dict) -> tuple[int, int, int]:
    """E-4 / R28: (start, stop, ddof) of the sigma-check window; must be the one common window [0, 5000), ddof 1."""
    w = choice(ch, "sigma_window")
    got = (w.get("start_sample"), w.get("stop_sample"), w.get("ddof")) if isinstance(w, dict) else None
    if got != (SIGMA_WINDOW[0], SIGMA_WINDOW[1], SIGMA_DDOF):
        raise MissingChoice(f"sigma_window {w!r} is not the common window samples [0, 5000), ddof 1 of R28")
    return got


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


def sigma_baseline_std(v) -> float:
    """R28: std (ddof 1) of v over the common window, samples [0, 5000); the same function is used for the reference record and for every network record."""
    a, b = SIGMA_WINDOW
    v = np.asarray(v, float)
    if v.size < b:
        raise EvalError(f"v has {v.size} samples, the sigma-check window needs {b}")
    return float(np.std(v[a:b], ddof=SIGMA_DDOF))


def _raw_crossing_s(v, fs, t_on, threshold):
    """First time at or after t_on at which the band-passed Hilbert envelope reaches the threshold (the mode-D raw crossing, no cycle count, no D8)."""
    env = M.envelope(v, fs, M.G_BAND)
    i_on = int(round(t_on * fs))
    hit = np.flatnonzero(env[i_on:] >= threshold)
    return float((hit[0] + i_on) / fs) if hit.size else float("nan")


# --- time origins (R27) -----------------------------------------------------------------------------------------

def origin_facts(cfg: dict, first_stamp_ms: float) -> dict:
    """What the classifier time means for one record type. The classifier time of sample i is i / fs for both modes (surge_metrics, v starts at t = 0 with the
    2 s discard removed). Mean field (mode D): sample i is the state at t = i dt_out, so its first stamp is 0. Network: sample i is the mean over the bin that
    ENDS at the stamp (i + 1) bin (qif_network.run_network), so the bin starts at i bin; the first stamp is one bin."""
    net = cfg["run"]["kind"] == "network"
    dt = float(cfg["network"]["rate_bin_ms"] if net else cfg["solver"]["dt_out_ms"])
    return {"kind": cfg["run"]["kind"], "t_on_s": float(cfg["path"]["t_on_s"]), "sample_ms": dt, "first_stamp_ms": float(first_stamp_ms),
            "path_time_of_sample0_ms": float(first_stamp_ms) - (dt if net else 0.0), "classifier_time_of_sample0_s": 0.0,
            "stamp_is": "bin end" if net else "instant"}


def check_time_origin(net: dict, mf: dict, label: str = "") -> dict:
    """R27: the classifier onset (network) and the mean-field onset must share one time origin, else STOP (EvalRefused). Inputs are origin_facts dicts.
    Shared origin = same path clock (path time of sample 0 equal), the same t_on and the same sample interval. The stamp convention differs by one sample
    (bin end against instant); the difference is reported (stamp_offset_ms) and is one sample interval."""
    probs = []
    if net["t_on_s"] != mf["t_on_s"]:
        probs.append(f"t_on {net['t_on_s']} s (network) vs {mf['t_on_s']} s (mean field)")
    if net["sample_ms"] != mf["sample_ms"]:
        probs.append(f"sample interval {net['sample_ms']} ms vs {mf['sample_ms']} ms")
    if abs(net["path_time_of_sample0_ms"] - mf["path_time_of_sample0_ms"]) > EPS:
        probs.append(f"path time of sample 0: {net['path_time_of_sample0_ms']} ms (network) vs {mf['path_time_of_sample0_ms']} ms (mean field)")
    if net["classifier_time_of_sample0_s"] != mf["classifier_time_of_sample0_s"]:
        probs.append("classifier time of sample 0 differs")
    if probs:
        raise EvalRefused(f"STOP (R27) {label}: the network classifier onset and the mean-field onset do not share a time origin: " + "; ".join(probs))
    return {"label": label, "shared": True, "network": net, "mean_field": mf, "stamp_offset_ms": net["first_stamp_ms"] - mf["first_stamp_ms"]}


def mf_origin_of_record(ref_json) -> dict:
    """origin_facts of a stored mean-field record (config from its json, first stamp from its npz t_ms)."""
    jp = Path(ref_json)
    cfg = json.loads(jp.read_text(encoding="utf-8"))["config"]
    with np.load(jp.with_suffix(".npz")) as z:
        t0 = float(z["t_ms"][0])
    return origin_facts(cfg, t0)


def origin_check_all(rows_net: list[dict], root=None) -> list[dict]:
    """The R27 check for the network configs of the given rows against the stored and companion mean-field records they are compared with. Reads the
    network configs and the mean-field t_ms only; no network record is opened (the network first stamp is the rate bin by construction of
    qif_network.run_network; read_record re-checks it on every record that carries t_ms)."""
    root = Path(root) if root else C.repo_root()
    mf_files = [f for ref in RL._read(RL.REFS_FILE)["references"] for f in ref["files"] if f.endswith(".json")]
    mf_files += [str(record_path(r)) for r in RL.expand("MF_COMPANION")]
    mfo = {Path(f).name: mf_origin_of_record(root / f) for f in mf_files}
    seen, out = set(), []
    for r in rows_net:
        cfg = r["cfg"]
        if cfg["run"]["kind"] != "network":
            continue
        net = origin_facts(cfg, float(cfg["network"]["rate_bin_ms"]))
        key = (net["t_on_s"], net["sample_ms"])
        for n, m in mfo.items():
            if (key, n) not in seen:
                seen.add((key, n))
                out.append(check_time_origin(net, m, n))
    return out


def read_record(row: dict, fi: dict, criteria_sha256: str | None = None, table21: bool = False, static_cache: dict | None = None) -> dict:
    """One record of a listed row: refusals first, then the class and the metrics. {'name', 'missing': True} if the file is absent.

    Network rows: frozen mode-N class; onset_s is the classifier onset (centre of the first flagged window, Conventions.onset default; R27, primary);
    onset_raw_crossing_s is the evaluator's own raw-crossing reading (secondary, post hoc, may be NaN); baseline_std_v is the R28 common-window std.
    table21=True adds the Table 2.1 Metrics row (E-6). Mean-field rows: mode D."""
    jp = record_path(row)
    if not jp.exists():
        cfg0, key0 = row["cfg"], row["spawn_key"]
        net0 = cfg0["run"]["kind"] == "network"
        return {"name": row["name"], "list": row["list"], "family": row["family"], "missing": True, "seed": int(key0[-1]) if key0 else -1,
                "group": int(key0[2]) if key0 and len(key0) > 3 else None, "T_ramp_s": float(cfg0["path"]["T_ramp_s"]),
                "N": cfg0["network"]["N"] if net0 else None, "het_dist": cfg0["network"]["het_dist"] if net0 else None}
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
        r_arr = z["r"] if "r" in z.files else None
        t0 = float(z["t_ms"][0]) if "t_ms" in z.files else None
    fs = MCL.fs_of(cfg)
    if mode == "N" and t0 is not None:                  # R27: the stored stamp of sample 0 must be the first bin end
        check_time_origin(origin_facts(cfg, t0), origin_facts(cfg, float(cfg["network"]["rate_bin_ms"])), row["name"])
    res, err = MCL.classify_array(mode, v, fs, p["t_on_s"], T, fi["threshold"])
    out.update(MCL.row_from_result(res, err, mode, T))
    if mode == "N":
        out["onset_classifier_centre_s"] = out["onset_s"]
        out["onset_raw_crossing_s"] = _raw_crossing_s(v, fs, p["t_on_s"], fi["threshold"]) if res is not None else float("nan")
        out["baseline_std_v"] = sigma_baseline_std(v)
    if table21:
        out.update(table21_fields(cfg, v, r_arr, res, fi, static_cache))
    return out


def table21_fields(cfg: dict, v, r, res, fi: dict, static_cache: dict | None = None) -> dict:
    """E-6: the Table 2.1 Metrics row of one record, reusing the MS9 9i pieces (surge_metrics.onset_delay, j_exit_metrics, ms9_9i.j_exit_static_path).
    A value that does not exist is NaN with a reason in out['undefined'] ({metric: reason}); nothing is imputed. J_exit, exit delay and the post-surge rate
    exist on P2 (path_hypoxia) only and need a terminated episode; r_post_1s and r_post_5s are the two windows of the O12 ruling (DL-207), none chosen."""
    from .. import ramps
    from ..units import s_to_tau
    from . import ms9_9i as N9
    nan = float("nan")
    out = {k: nan for k in TABLE21_METRICS}
    why: dict[str, str] = {}
    ep = None if res is None else res.episode
    if ep is None:
        out["undefined"] = {k: "no_episode" for k in TABLE21_METRICS}
        return out
    p, m = cfg["path"], cfg["model"]
    fs = MCL.fs_of(cfg)
    t_s = np.arange(len(v)) / fs
    path = ramps.make_path(cfg)
    tau = s_to_tau(t_s, m["tau_ms"])
    eta = np.broadcast_to(np.asarray(path.eta(tau), float), t_s.shape)
    J = np.broadcast_to(np.asarray(path.J(tau), float), t_s.shape)
    out["onset_s"] = float(ep.onset_s)
    out["eta_onset"], out["delay_eta"] = M.onset_delay(ep.onset_s, t_s, eta, p["eta_H"])
    out["duration_ms"] = 1000.0 * float(ep.duration_s)
    out["duration_cycles"] = float(ep.cycles)
    out["duration_frac_ramp"] = float(ep.duration_s) / float(p["T_ramp_s"])
    out["peak_power_abs"], out["peak_power_rel"], out["f_pk_hz"] = float(ep.peak_p_g), float(ep.peak_rho), float(ep.f_pk_hz)
    if p["name"] != "path_hypoxia":
        for k in ("J_exit_run", "J_exit_static", "exit_delay", "r_post_1s", "r_post_5s"):
            why[k] = "not_applicable_not_P2"
    else:
        cache = static_cache if static_cache is not None else {}
        key = json.dumps([p, m], sort_keys=True, default=str)
        if key not in cache:
            cache[key] = N9.j_exit_static_path(cfg, fi["grid_step"])
        j_static, static_why = cache[key]
        if j_static is None:
            why["J_exit_static"] = static_why
        else:
            out["J_exit_static"] = float(j_static)
        if not ep.terminated:
            for k in ("J_exit_run", "exit_delay", "r_post_1s", "r_post_5s"):
                why[k] = "episode_unterminated_at_run_end"
        else:
            out["J_exit_run"], _, _ = M.j_exit_metrics(ep.end_s, t_s, J, 0.0)
            if j_static is None:
                why["exit_delay"] = "no_J_exit_static"
            else:
                out["exit_delay"] = out["J_exit_run"] - float(j_static)
            for w in N9.WINDOWS_S:
                k = f"r_post_{int(w)}s"
                if r is not None and ep.end_s + w <= t_s[-1] + 1.0 / fs:
                    sel = (t_s >= ep.end_s) & (t_s < ep.end_s + w)
                    out[k] = float(np.asarray(r)[sel].mean())
                else:
                    why[k] = "window_extends_past_run_end" if r is not None else "no_r_in_record"
    out["undefined"] = {k: why.get(k, "undefined") for k in TABLE21_METRICS if not math.isfinite(out[k])}
    return out


def read_lists(lists, fi: dict, require_frozen: bool = True, table21: bool = False) -> dict:
    """{list: [record dicts in list order]}; refuses unlisted records in the family folders. R27: the time-origin check runs before any record is read.
    table21 adds the Table 2.1 Metrics row to the ramp lists (S8, S9, S10), not to the controls."""
    rows = expected_rows(lists, require_frozen)
    stray = unlisted_records(rows)
    if stray:
        raise EvalRefused(f"{len(stray)} record(s) in the family folders are not rows of the frozen lists, e.g. {stray[0]}")
    origin_check_all([r for rs in rows.values() for r in rs])
    cache: dict = {}
    return {n: [read_record(r, fi, table21=table21 and n in RL.RAMP_LISTS, static_cache=cache) for r in rs] for n, rs in rows.items()}


# --- readings ---------------------------------------------------------------------------------------

def surge_set(posthoc: bool = False):
    return POSTHOC_SREL if posthoc else M.SURGE_CLASSES


def matches(ref_cls: str, cls: str, posthoc: bool = False) -> bool:
    """Table 2.1 correspondence of the mean-field class to the network class (primary); posthoc: S-rel not counted (DL-258 b)."""
    ok = M.classes_agree(ref_cls, cls)
    return ok and not (posthoc and ref_cls == "D-tr" and cls == "S-rel")


def onset_of(rec: dict, ch: dict) -> float:
    """The network onset (E-1 / R27): the classifier onset, the centre of the first flagged window (Conventions.onset default). NaN where undefined."""
    choice(ch, "network_onset_definition")
    return float(rec.get("onset_classifier_centre_s", float("nan")))


def metric_of(rec: dict, name: str, ch: dict) -> float:
    if name == "onset_s":
        return onset_of(rec, ch)
    return float(rec.get(name, float("nan")))


def _within(diff: float, tol: float, boundary: str) -> bool:
    return diff <= tol + EPS if boundary == "inclusive" else diff < tol - EPS


def _policy(v, ch):
    """True / False / None (undefined) to a bool by E-2: with not_met an undefined test fails; None is also the n/a of a reference without a value."""
    if v is None:
        return choice(ch, "not_evaluable_counts_as") == "vacuous"
    return bool(v)


def seed_assessment(rec: dict, ref: dict, ch: dict, tol: float) -> dict:
    """RB1 for one network run against its mean-field reference (R23, R26, R27): class (both readings), f_pk within tol, onset within one spectrogram step.

    E-2: a seed whose f_pk or onset is undefined fails that test (status "undefined"); a reference without the value (not D-tr) has nothing to compare and
    the test is "n/a" (counts as met; the class test carries the comparison). E-3: boundaries inclusive; margins reported (>= 0 means met).
    R27: the onset is the classifier onset; the own raw-crossing onset is a secondary, post-hoc reading (onset_raw_*), feeds no gate, undefined allowed."""
    out = {"name": rec["name"], "seed": rec["seed"], "class": rec["class"], "ref_class": ref["class"],
           "class_match": matches(ref["class"], rec["class"]), "class_match_posthoc": matches(ref["class"], rec["class"], posthoc=True)}
    bd = choice(ch, "tolerance_boundary")
    has_ref = ref["class"] == "D-tr"
    f, rf = rec.get("f_pk_hz"), ref.get("f_pk_hz")
    out["f_pk_hz"], out["f_pk_ref_hz"], out["bin_hz"] = f, rf, rec["bin_hz"]
    out["f_pk_rel_err"] = out["f_pk_diff_hz"] = out["f_pk_diff_bins"] = out["f_pk_margin"] = float("nan")
    if not has_ref:
        out["f_pk_status"], out["f_pk_ok"] = "n/a", None
    elif _finite(f) and _finite(rf):
        out["f_pk_rel_err"] = abs(f - rf) / rf
        out["f_pk_diff_hz"] = f - rf
        out["f_pk_diff_bins"] = (f - rf) / rec["bin_hz"]
        out["f_pk_margin"] = tol - out["f_pk_rel_err"]
        out["f_pk_ok"] = _within(out["f_pk_rel_err"], tol, bd)
        out["f_pk_status"] = "ok"
    else:
        out["f_pk_status"], out["f_pk_ok"] = "undefined", None
    on, ron = onset_of(rec, ch), ref.get("onset_s")
    step = ONSET_TOL_STEPS * rec["step_s"]
    out["onset_s"], out["onset_ref_s"], out["step_s"] = on, ron, rec["step_s"]
    out["onset_diff_s"] = out["onset_margin_s"] = float("nan")
    if not has_ref:
        out["onset_status"], out["onset_ok"] = "n/a", None
    elif _finite(on) and _finite(ron):
        out["onset_diff_s"] = on - ron
        out["onset_margin_s"] = step - abs(on - ron)
        out["onset_ok"] = _within(abs(on - ron), step, bd)
        out["onset_status"] = "ok"
    else:
        out["onset_status"], out["onset_ok"] = "undefined", None
    raw = rec.get("onset_raw_crossing_s", float("nan"))                    # secondary, post hoc (R27)
    out["onset_raw_s"] = raw
    out["onset_raw_diff_s"] = (raw - ron) if has_ref and _finite(raw) and _finite(ron) else float("nan")
    out["onset_raw_ok"] = _within(abs(out["onset_raw_diff_s"]), step, bd) if _finite(out["onset_raw_diff_s"]) else None
    out["onset_raw_status"] = "n/a" if not has_ref else ("ok" if _finite(out["onset_raw_diff_s"]) else "undefined")
    out["onset_raw_label"] = "post hoc, feeds no gate"
    out["f_pk_ok_policy"] = True if out["f_pk_status"] == "n/a" else _policy(out["f_pk_ok"], ch)
    out["onset_ok_policy"] = True if out["onset_status"] == "n/a" else _policy(out["onset_ok"], ch)
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
    """Median and range over the defined values; undefined entries are counted (n_undefined), never imputed."""
    xs = list(xs)
    ok = [float(x) for x in xs if _finite(x)]
    return {"n": len(ok), "n_undefined": len(xs) - len(ok), "median": float(np.median(ok)) if ok else float("nan"), "min": min(ok) if ok else float("nan"),
            "max": max(ok) if ok else float("nan")}


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
            if any(m in TABLE21_METRICS and m != "onset_s" for m in names) and any(r["class"] != M.FAILED and "duration_ms" not in r for r in live):
                raise EvalError("s9 metrics need the Table 2.1 fields: read the records with table21=True")
            d["metrics"] = {m: _med_range([metric_of(r, m, ch) for r in live]) for m in names}
            d["metric_undefined_reasons"] = dict(Counter(f"{k}: {why}" for r in live for k, why in (r.get("undefined") or {}).items() if k in names))
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
    """R16, R25, R28: the mean-field baseline std of v (E-10, 0.039522 from the MS7 baseline-only record) lies inside the range of the network baseline std
    over the S8 headline baselines. One common window for the reference and every network baseline: samples [0, 5000), ddof 1 (sigma_baseline_std).
    Sigma is never changed here. Reports the number of distinct baseline values, per seed across the two T_ramp (the baseline is expected equal at 10 s and
    120 s because the parameters are constant before t_on; UNVERIFIED, reported not assumed) and overall, and the position of the reference in the range (E-5)."""
    mf = float(choice(ch, "mf_baseline_std"))
    choice(ch, "mf_baseline_std_source")
    sigma_window_of(ch)
    bounds = choice(ch, "sigma_range_bounds")
    live = [r for r in head_recs if not r.get("missing") and r["class"] != M.FAILED]
    if len(live) < len(head_recs):
        return {"verdict": "INCOMPLETE", "n_runs": len(live), "n_expected": len(head_recs)}
    vals = [r["baseline_std_v"] for r in live]
    lo, hi = min(vals), max(vals)
    inside = (lo <= mf <= hi) if bounds == "inclusive" else (lo < mf < hi)
    by_seed: dict = {}
    for r in live:
        by_seed.setdefault(r["seed"], []).append(r["baseline_std_v"])
    return {"verdict": "PASS" if inside else "NOT INSIDE (limitation; sigma stays frozen)", "mf_baseline_std": mf, "network_min": lo, "network_max": hi,
            "network_mean": float(np.mean(vals)), "n_runs": len(vals), "n_distinct_values": len({round(x, 12) for x in vals}), "bounds": bounds,
            "n_distinct_per_seed": {k: len({round(x, 12) for x in v}) for k, v in sorted(by_seed.items())},
            "window": {"start_sample": SIGMA_WINDOW[0], "stop_sample": SIGMA_WINDOW[1], "ddof": SIGMA_DDOF},
            "position_in_range": float((mf - lo) / (hi - lo)) if hi > lo else float("nan"), "margin_to_nearest_end": float(min(mf - lo, hi - mf)),
            "per_run": {r["name"]: r["baseline_std_v"] for r in live}, "mf_over_network_mean": float(mf / np.mean(vals)), "sigma_changed": False}


# --- S10 / RB8 -----------------------------------------------------------------------------------------

TRANSIENT_SURGE = ("S+", "S-rel", "S-abs")


def corr_level(cls: str, posthoc: bool = False) -> str:
    """The Table 2.1 correspondence level of a network class (E-8): transient surge (S+, S-rel, S-abs), S-sus or NS. A failed run is its own level and
    matches nothing. Post hoc (DL-258 b): S-rel is not counted as a surge, it is its own level."""
    if cls in TRANSIENT_SURGE:
        return "S-rel" if (posthoc and cls == "S-rel") else "surge"
    return cls


def _same(a: str, b: str, posthoc: bool = False) -> bool:
    """Same correspondence level (E-8); failed records never match."""
    if M.FAILED in (a, b):
        return False
    return corr_level(a, posthoc) == corr_level(b, posthoc)


def rb8(recs: list[dict], controls: list[dict], ref: dict | None, ch: dict, fr: dict) -> dict:
    """R8, R26 E-7/E-8: Gaussian and uniform give the Lorentzian network class in rb8_seeds of 3 seeds. Each Gaussian and uniform seed is compared with the
    Lorentzian reference only if the 3 Lorentzian seeds share one Table 2.1 correspondence class; otherwise RB8 is NOT EVALUABLE (per-seed table, no
    pass/fail). "Gives the class" is read at the correspondence level (surge-class membership, S-sus, NS); the exact labels are reported beside it."""
    choice(ch, "rb8_comparator")
    choice(ch, "rb8_class_equality")
    lor = sorted([r for r in recs if r["het_dist"] == "lorentzian"], key=lambda r: r["seed"])
    out = {"comparator": "common_lorentzian_class", "equality": "surge_correspondence", "shapes": {}}
    if len(lor) < 3 or any(r.get("missing") for r in lor):
        return {**out, "verdict": "INCOMPLETE", "reason": "Lorentzian runs missing"}
    table = {"lorentzian": [{"seed": r["seed"], "class": r["class"], "level": corr_level(r["class"])} for r in lor]}
    for shape in ("gaussian", "uniform"):
        g = sorted([r for r in recs if r["het_dist"] == shape], key=lambda r: r["seed"])
        table[shape] = [{"seed": r["seed"], "class": r["class"], "level": corr_level(r["class"])} for r in g if not r.get("missing")]
    out["per_seed_table"] = table
    out["lorentzian_classes"] = [r["class"] for r in lor]
    out["lorentzian_controls"] = control_classes(lor[0], controls)
    levels = {corr_level(r["class"]) for r in lor}
    out["lorentzian_levels"] = sorted(levels)
    out["lorentzian_mf_match_seeds"] = sum(matches(ref["class"], r["class"]) for r in lor) if ref is not None else None
    if len(levels) != 1 or M.FAILED in levels:
        return {**out, "verdict": "NOT EVALUABLE", "reason": "the 3 Lorentzian seeds do not share one Table 2.1 correspondence class" if len(levels) != 1
                else "the Lorentzian runs failed"}
    common = next(iter(levels))
    out["common_level"] = common
    verdicts = []
    for shape in ("gaussian", "uniform"):
        g = sorted([r for r in recs if r["het_dist"] == shape], key=lambda r: r["seed"])
        if len(g) < 3 or any(r.get("missing") for r in g):
            out["shapes"][shape] = {"verdict": "INCOMPLETE"}
            verdicts.append("INCOMPLETE")
            continue
        hit = [r["class"] != M.FAILED and corr_level(r["class"]) == common for r in g]
        lv_ph = {corr_level(r["class"], True) for r in lor}
        hit_ph = [r["class"] != M.FAILED and corr_level(r["class"], True) == next(iter(lv_ph)) for r in g] if len(lv_ph) == 1 else None
        d = {"classes": [r["class"] for r in g], "levels": [corr_level(r["class"]) for r in g], "hits": sum(hit),
             "hits_srel_not_counted": None if hit_ph is None else sum(hit_ph), "controls": control_classes(g[0], controls),
             "verdict": "PASS" if sum(hit) >= fr["rb8_seeds"] else "FAIL"}
        if ref is not None:
            d["match_mf_seeds"] = sum(matches(ref["class"], r["class"]) for r in g)
        out["shapes"][shape] = d
        verdicts.append(d["verdict"])
    out["verdict"] = "INCOMPLETE" if "INCOMPLETE" in verdicts else ("PASS" if all(v == "PASS" for v in verdicts) else "FAIL")
    return out


# --- G4 --------------------------------------------------------------------------------------------------

G4_POOL_SELECTORS = ("", "headline", "lorentzian")


def _pool(spec: str, by_list: dict, N: int) -> tuple[str, list[dict]]:
    """Records of one pool entry 'LIST' or 'LIST:headline' (S8 headline runs) or 'LIST:lorentzian' at N."""
    lst, _, sel = spec.partition(":")
    if lst not in SRC_LISTS or sel not in G4_POOL_SELECTORS:
        raise MissingChoice(f"g4_pools entry {spec!r} is not LIST[:headline|:lorentzian] with LIST in {SRC_LISTS}")
    recs = [r for r in by_list.get(lst, []) if r.get("N") == N]
    if sel == "headline":
        recs = [r for r in recs if r["name"].startswith("S8_head")]
    elif sel == "lorentzian":
        recs = [r for r in recs if r.get("het_dist") == "lorentzian"]
    return lst, recs


def g4_summary(by_list: dict, rb1: dict, cells: dict, ch: dict) -> dict:
    """R24, R26 E-9: the network misses the surge at an N when no pooled seed at that N is in a surge class (primary reading). "The network at N = 1e4" pools
    the Lorentzian records at N = 1e4 (S8 headline, S9, S10 Lorentzian); "at N = 3e4" is S9 at 3e4 (configs/ms10/ms10_eval.yaml g4_pools). Per-list counts are
    reported beside the pooled count. A pool with a missing record and no surge seed among the present ones is not evaluable (None), never a "miss".
    Report-only for the run order. Text of the three plan consequences (Tables 4.2 and 11.2) with whether each condition holds."""
    pools = choice(ch, "g4_pools")
    miss = {}
    for N in (10000, 30000):
        specs = pools.get(str(N)) if isinstance(pools, dict) else None
        if not specs:
            raise MissingChoice(f"g4_pools has no entry for N = {N}")
        per_list, allrecs = {}, []
        for spec in specs:
            lst, g = _pool(spec, by_list, N)
            live = [r for r in g if not r.get("missing")]
            per_list[spec] = {"records": len(live), "missing": len(g) - len(live), "surge_seeds": sum(1 for r in live if r["surge"]),
                              "surge_seeds_srel_not_counted": sum(1 for r in live if r["class"] in POSTHOC_SREL)}
            allrecs += g
        live = [r for r in allrecs if not r.get("missing")]
        n_missing = len(allrecs) - len(live)
        n_surge = sum(1 for r in live if r["surge"])
        m = None if not live else (False if n_surge else (True if n_missing == 0 else None))
        miss[N] = {"records": len(live), "missing": n_missing, "surge_seeds": n_surge,
                   "surge_seeds_srel_not_counted": sum(1 for r in live if r["class"] in POSTHOC_SREL), "misses": m, "per_list": per_list}
    both = None if any(m["misses"] is None for m in miss.values()) else all(m["misses"] for m in miss.values())
    dis = cells.get("disagree")
    c2 = None if dis is None else dis >= 2
    ok = rb1["verdict"]
    text = [
        "RB1 passes: continue (G4 not triggered)." if ok == "PASS" else ("RB1 does not pass: G4 is evaluated." if ok == "FAIL" else "RB1 is incomplete: G4 cannot be stated."),
        f"(1) Network misses the surge at N = 1e4 and 3e4 (no pooled seed at that N in a surge class): {_yn(both)} -> if yes, report a finite-size limitation (Part 1, Table 4.2); keep the model.",
        f"(2) Disagreement in 2 or more of the 4 cells: {_yn(c2)} -> if yes, rerun RB6 (its network parts, the dt ladder and V_p, are S13 runs at MS11; R9). Known caveats: OA attraction with synaptic kinetics is unproven; shot noise causes metastability [R1, 2.6].",
        "(3) Report the affected results as mean-field-only: applies when (1) or (2) holds (our reading of the Table 11.2 sentence, UNVERIFIED).",
        "G4 is report-only for the run order (Table 11.2 footnote); it limits claims to the mean field, it stops nothing.",
    ]
    return {"misses_by_N": miss, "misses_both": both, "cells_disagree_2_or_more": c2, "triggered": None if (both is None and c2 is None) else bool(both or c2),
            "rb1": ok, "text": text}


def _yn(x):
    return "not evaluable (records missing)" if x is None else ("YES" if x else "no")
