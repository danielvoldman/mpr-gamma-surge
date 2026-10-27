"""FABRICATED records for the code-path test of 11d (DL-373). NOT results: every record written here is made up, carries the label "fabricated" in its message and in its
flags, lives in a temporary folder outside results/, and is never evaluated as a result.

The records use the REAL writers and formats: provenance.make_run_record / write_run_record (json), provenance.atomic_save_npz (npz with the eight 1 kHz float64 arrays),
the names and config hashes of the rows of the frozen MS11 lists, the S5 grid names of run_A11.S5_GRID, and the CSV layouts of the stored MS9 class tables. Only the series
(v) is made up: baseline noise plus a burst, so that the frozen classifier has something to read.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import ms8_counts as M8
from mprsurge.analysis import ms11_eval as E
from mprsurge.analysis import ms11_runlist as RL

ROOT = C.repo_root()
FABRICATED = "FABRICATED record for a code-path test; not a result; never evaluated as a result"
ARRAYS = ("t_ms", "r", "v", "s", "eta", "J", "Delta", "I")
S5_GRID = {"10": "p2_linear_0004_4f4756348cd8", "316": "p2_linear_0010_2ec39c34e678"}
HEADLINE = "S5ramp_0000_240de3ef73be"


def env():
    e = P.environment_info(with_julia=False)
    e["git"] = {**e["git"], "dirty": False, "commit": "fabricated0000000000000000000000000000000"}
    return e


def series(cfg: dict, rng, burst=True) -> dict:
    kind = cfg["run"]["kind"]
    fs = 1000.0 / (cfg["network"]["rate_bin_ms"] if kind == "network" else cfg["solver"]["dt_out_ms"])
    T = float(cfg["path"]["T_ramp_s"])
    dur = M8.run_duration_s(cfg["path"]["name"], T)
    n = int(round(dur * fs)) + 1
    t = np.arange(n) / fs
    v = rng.normal(0.0, 0.04, n) if kind != "mf" else np.zeros(n)
    if burst:
        t_on = float(cfg["path"]["t_on_s"])
        sel = (t >= t_on + 0.3 * T) & (t < t_on + 0.6 * T)
        v = v + sel * np.sin(2 * np.pi * 45.0 * t)
    arrs = {k: np.zeros(n) for k in ARRAYS}
    arrs["t_ms"] = t * 1000.0
    arrs["v"] = v
    return arrs


def write_record(cfg: dict, out_dir: Path, name: str, rng, *, burst=True, status="ok", dry=False) -> Path:
    """One fabricated record pair <name>.json + <name>.npz in the real format. The record's name and config hash are those given by the caller's row."""
    out_dir.mkdir(parents=True, exist_ok=True)
    npz = out_dir / f"{name}.npz"
    P.atomic_save_npz(npz, series(cfg, rng, burst))
    rec = P.make_run_record(cfg, env(), name=name, status=status, message=FABRICATED, wall_time_s=1.0, flags={"fabricated": True},
                            inputs={}, outputs={npz.name: P.sha256_file(npz)}, dry_run=dry)
    jp = out_dir / f"{name}.json"
    P.write_run_record(rec, jp)
    return jp


def list_records(results_root: Path, lists=None, skip: dict | None = None, seed=0) -> dict:
    """A fabricated record for every row of the frozen MS11 lists, under results_root (named and hashed as the row says). skip: {list: n} leaves out the last n rows (a missing record)."""
    rng = np.random.default_rng(seed)
    out = {}
    for name in lists or RL.ALL_LISTS:
        rows = E.redirect_rows(RL.expand(name), results_root)
        keep = len(rows) - (skip or {}).get(name, 0)
        for r in rows[:keep]:
            write_record(r["cfg"], Path(r["out_dir"]), r["name"], rng, burst=True)
        out[name] = len(rows[:keep])
    return out


def _s5_cfg(T: float, **over) -> dict:
    return C.resolve_config(ROOT / "configs/S5_ramp.yaml", {"path.T_ramp_s": T, **over})


def s5_records(results_root: Path, seed=1) -> dict:
    """The S5 grid members (T_ramp 10 s and 316.2278 s, the 1e-6 / 1e-10 members of the ladders), a P5 pair and the headline, with their class table row."""
    rng = np.random.default_rng(seed)
    base = Path(results_root) / "S5/ramp"
    paths = {}
    paths["grid10"] = write_record(_s5_cfg(10.0), base / "p2_linear", S5_GRID["10"], rng)
    paths["grid316"] = write_record(_s5_cfg(316.22776601683796), base / "p2_linear", S5_GRID["316"], rng)
    for k, T in enumerate((56.23, 177.8)):
        write_record(_s5_cfg(T), base / "p5_linear", f"p5_linear_{k:04d}_fabricated{k}", rng)
    paths["headline"] = write_record(_s5_cfg(120.0), base / "S5ramp", HEADLINE, rng)
    return paths


def class_tables(results_root: Path, cells=3, subgrid_cells=4, seeds=2, seed=2) -> dict:
    """Map 1, map 2 and subgrid records with the real CSV layouts (results/ms9/9e/map1_classes.csv, 9f/map2_classes.csv, 9f/subgrid_classes.csv, 9d/s5_headline_classes.csv)."""
    from mprsurge.analysis import a7 as A7
    from mprsurge.analysis import ms9_classify as MCL
    rng = np.random.default_rng(seed)
    fi, _ = A7.frozen_inputs()
    res = Path(results_root)
    out = {}
    cfg = _s5_cfg(120.0)
    for set_name, sub, csv_rel, mode in (("map1", "S7/S7_map1", "ms9/9e/map1_classes.csv", "D"), ("map2", "S7/S7_map2", "ms9/9f/map2_classes.csv", "D"),
                                          ("subgrid", "S7/S7_subgrid", "ms9/9f/subgrid_classes.csv", "N")):
        n = cells if set_name != "subgrid" else subgrid_cells * seeds
        rows = []
        for k in range(n):
            c = {**cfg, "model": {**cfg["model"], "Delta": 0.1 + 0.01 * k}}
            if mode == "N":
                c = {**c, "run": {**c["run"], "kind": "mf_noisy"}}
            name = f"{set_name}_{k:04d}_fabricated"
            jp = write_record(c, res / sub, name, rng)
            r = MCL.classify_record(jp, fi)
            if set_name == "subgrid":
                rows.append({"run": name, "i": k // seeds, "j": 0, "seed": k % seeds, "class": r["class"], "det": "D-tr", "W_s": r["W_s"], "git_commit": "fabricated",
                             "git_dirty": "False", "agree": "False"})
            else:
                rows.append({"run": name, "i": k, "j": 0, "Delta": c["model"]["Delta"], "tau_d_ms": 5.0, "status": "ok", "git_commit": "fabricated", "git_dirty": "False",
                             "wall_time_s": 1.0, "class": r["class"], "surge": r["surge"], "inside_a4_region": "", "time_inside_s": "", "labels_all": "", "label_primary": "",
                             "label_f": r["label_f"], "onset_s": r["onset_s"], "f_pk_hz": r["f_pk_hz"]})
        p = res / csv_rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        out[set_name] = len(rows)
    hr = MCL.classify_record(res / f"S5/ramp/S5ramp/{HEADLINE}.json", fi)
    p = res / "ms9/9d/s5_headline_classes.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(hr), lineterminator="\n")
        w.writeheader()
        w.writerow(hr)
    out["headline_class"] = hr["class"]
    return out


def rb9a_file(results_root: Path, value=1.2258e-8) -> Path:
    import json
    p = Path(results_root) / "A11/rb9a_unit_level.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"max_rel_diff": value, "per_tau": {"10": {"max": value}, "20": {"max": value / 2}}, "label": FABRICATED}), encoding="utf-8")
    return p


def build_all(results_root: Path, skip: dict | None = None) -> dict:
    results_root = Path(results_root)
    out = {"lists": list_records(results_root, skip=skip)}
    s5_records(results_root)
    out["tables"] = class_tables(results_root)
    rb9a_file(results_root)
    return out
