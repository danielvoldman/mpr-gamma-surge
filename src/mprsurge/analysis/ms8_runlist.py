"""MS8 run lists (8b; docs/ms8_plan.md, DL-169): the S5 ramp study and the S13 headline subset, expanded from configs/ms8/*.yaml.

Analysis only: every config goes through run.build_plan (so the frozen-criteria gate runs), nothing integrates. A list is the cells of
its configs in the order below; its SHA-256 is taken over the canonical JSON of [family, cell index, full config hash, spawn key]
per cell, so a changed config, key, sweep value or order changes it. The manifest (CSV per list and a JSON summary) is written
under results/ms8/ (git-ignored output).

Shared runs: the headline run (configs/S5_ramp.yaml, P2 120 s linear, DOP853 rtol 1e-10, delta0 1e-6) is the S5 headline cell and also
the rtol 1e-10, delta0 1e-6 and DOP853 member of the S13 ladders; it is in the S5 list only. The start-distance run at 1.5 is the P1
linear grid run (M-2).
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from .. import config as C
from .. import criteria as CR
from .. import run as R

# (config, family label): the order of the lists.
S5_CONFIGS = (
    ("configs/ms8/s5_p1_linear.yaml", "S5_grid"), ("configs/ms8/s5_p1_sigmoid.yaml", "S5_grid"),
    ("configs/ms8/s5_p2_linear.yaml", "S5_grid"), ("configs/ms8/s5_p2_sigmoid.yaml", "S5_grid"),
    ("configs/ms8/s5_p5_linear.yaml", "S5_grid"), ("configs/ms8/s5_p5_sigmoid.yaml", "S5_grid"),
    ("configs/ms8/s5_p1_start_distance.yaml", "S5_start_distance"),
    ("configs/S5_ramp.yaml", "S5_headline"),
    ("configs/ms8/s5_p2_noise.yaml", "S5_noise"),
)
S13_CONFIGS = (
    ("configs/ms8/s13_rtol.yaml", "S13_rtol"), ("configs/ms8/s13_delta0.yaml", "S13_delta0"), ("configs/ms8/s13_radau.yaml", "S13_radau"),
    ("configs/ms8/s13_floor_l0.yaml", "S13_floor"), ("configs/ms8/s13_floor_l1.yaml", "S13_floor"), ("configs/ms8/s13_floor_l2.yaml", "S13_floor"),
)
LISTS = {"S5": S5_CONFIGS, "S13": S13_CONFIGS}
COLUMNS = ("list", "family", "config", "index", "name", "hash", "kind", "path", "profile", "T_ramp_s", "start_distance", "solver", "rtol",
           "delta0", "dt_tau", "coupling_dt_tau", "sigma", "spawn_key", "eta_start", "out_dir")


def expand(name: str, sets=()) -> list[dict]:
    """The cells of one list, each a flat dict (COLUMNS) plus the full resolved cfg under "cfg"."""
    rows = []
    for cfg_path, family in LISTS[name]:
        plan = R.build_plan(cfg_path, sets)
        for c in plan.cells:
            g = c["cfg"]
            key = g["seeds"]["spawn_key"]
            rows.append({
                "list": name, "family": family, "config": cfg_path, "index": c["index"], "name": c["name"],
                "hash": C.config_hash(g), "kind": g["run"]["kind"], "path": g["path"]["name"], "profile": g["path"]["profile"],
                "T_ramp_s": g["path"]["T_ramp_s"], "start_distance": g["path"].get("start_distance"), "solver": g["solver"]["method"],
                "rtol": g["solver"]["rtol"], "delta0": g["solver"]["delta0"],
                "dt_tau": g["noise"]["dt_tau"] if g["run"]["kind"] == "mf_noisy" else None,
                "coupling_dt_tau": g["noise"].get("coupling_dt_tau") if g["run"]["kind"] == "mf_noisy" else None,
                "sigma": g["noise"]["sigma"] * g["noise"]["sigma_factor"] if g["run"]["kind"] == "mf_noisy" else None,
                "spawn_key": list(key) if key is not None else None, "eta_start": g["path"]["eta_start"],
                "out_dir": C.to_posix(plan.out_dir), "cfg": g})
    return rows


def list_sha256(rows: list[dict]) -> str:
    """SHA-256 of the canonical JSON of [family, index, full config hash, spawn key] per cell, in list order."""
    return hashlib.sha256(C.canonical_json([[r["family"], r["config"], r["index"], r["hash"], r["spawn_key"]] for r in rows]).encode()).hexdigest()


def breakdown(rows: list[dict]) -> dict:
    """{family: runs} in list order."""
    out: dict[str, int] = {}
    for r in rows:
        out[r["family"]] = out.get(r["family"], 0) + 1
    return out


def duplicates(rows: list[dict]) -> list[tuple[str, str]]:
    """Cells of different positions with the same full config hash (the same run twice): (name, name) pairs."""
    seen: dict[str, str] = {}
    dup = []
    for r in rows:
        if r["hash"] in seen:
            dup.append((seen[r["hash"]], r["name"]))
        seen.setdefault(r["hash"], r["name"])
    return dup


def seed_keys(rows: list[dict]) -> list[tuple[int, ...]]:
    return [tuple(r["spawn_key"]) for r in rows if r["spawn_key"] is not None]


def write_manifest(out_dir, sets=()) -> dict:
    """Write results/ms8/-style manifest files; returns the summary dict (also written as ms8_runlists.json)."""
    gate = CR.verify_frozen_criteria()                 # first: a list that fails the freeze check writes nothing
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    summary = {"gate": gate, "lists": {}}
    for name in LISTS:
        rows = expand(name, sets)
        with open(out / f"runlist_{name}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(COLUMNS)
            for r in rows:
                w.writerow([json.dumps(r[c]) if isinstance(r[c], list) else r[c] for c in COLUMNS])
        summary["lists"][name] = {"runs": len(rows), "by_family": breakdown(rows), "sha256": list_sha256(rows),
                                  "duplicate_hashes": duplicates(rows), "n_seed_keys": len(seed_keys(rows))}
    (out / "ms8_runlists.json").write_text(json.dumps(summary, indent=1, sort_keys=True), encoding="utf-8")
    return summary


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="python -m mprsurge.analysis.ms8_runlist", description="MS8 8b run lists: counts, hashes, manifest")
    ap.add_argument("--out", default="results/ms8", help="manifest directory (git-ignored)")
    ap.add_argument("--dry-run", action="store_true",
                    help="also run every config through the runner's --dry-run (a run record per cell, nothing integrated)")
    args = ap.parse_args(argv)
    s = write_manifest(C.repo_root() / args.out)
    g = s["gate"]
    print(f"criteria gate: ok, tag {g['tag']} on {g['commit'][:7]}, SHA-256 {g['sha256']}")
    for name, v in s["lists"].items():
        print(f"{name}: {v['runs']} runs  {v['by_family']}  list SHA-256 {v['sha256']}  duplicate hashes {len(v['duplicate_hashes'])}")
    if args.dry_run:
        bad = 0
        for name in LISTS:
            for cfg_path, _ in LISTS[name]:
                bad += R.main(["--config", cfg_path, "--dry-run"]) != 0
        print(f"dry run: {'all configs ok' if not bad else f'{bad} config(s) failed'}; nothing integrated")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
