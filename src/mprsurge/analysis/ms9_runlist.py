"""MS9 run lists (9b; docs/ms9_plan.md "Rulings", DL-213 to DL-215): S6, S7 (map 1, map 2, noisy subgrid), S12 (NC1, NC2, NC3) and S16.

Analysis only: every entry is a config file under configs/ms9/ plus an override dict; `expand` resolves it with config.resolve_config and
applies the frozen-criteria gate (CR.require_frozen_for_config), nothing integrates. Pre-registered lists (3,618 runs, equal to
ms9_counts) are kept apart from the SUPPLEMENTARY lists (2 P2 reference runs, M9-9; NC1 in mode N, M9-4), which are outside the
pre-registered counts and feed no gate.

Cells: the map grids are the cells of configs/S5_cells.yaml (1 + 900 + 325 = 1,226, cell-list SHA-256 8e67bbd2..., frozen). Building them
runs the Hopf scan (about 90 s), so the cell parameters are stored in configs/ms9/runlists/cells_1226.csv (full-precision floats) and
this module reads that file after checking the frozen cell-list hash; `build_cells_file` rewrites it from analysis.cells (a slow test
compares the two).

Seed keys (root_seed 20261008, first element 9 = MS9; UNVERIFIED, DL-210, M9-21): [9, 1, s] noisy subgrid seed s of every cell; [9, 2, 0]
NC1 network; [9, 3, s] reserved, unused; [9, 4, s] supplementary NC1 mode N (same stream at every T_ramp, DL-069). S16 point runs
[7, 9, 1, k] and the design draw [7, 9, 0] are settled (DL-159, F-19).
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from .. import config as C
from .. import criteria as CR
from .. import provenance as P
from . import ms8_counts as M8

CONFIG_DIR = "configs/ms9"
RUNLIST_DIR = "configs/ms9/runlists"
CELLS_FILE = f"{RUNLIST_DIR}/cells_1226.csv"
FROZEN_CELL_LIST_SHA256 = "8e67bbd2b366e86ffee59e732dd79824bdce82c73c477436cb3b1689b0a328d9"

GRID13 = [float(x) for x in M8.t_ramp_grid()]                     # 10^(k/4), the S5 grid (configs/ms8)
S6_T_RAMP_S = (10.0, 30.0, 120.0, 300.0)
P3_AMPLITUDES = (0.5, 1.0, 2.0)
NC1_MAP_CELLS = ((0, 0), (0, 29), (29, 0), (29, 29), (14, 12))   # M9-5: the four corners and the cell nearest the headline
SUBGRID_N, MAP1_N = 15, 30
N_SEEDS = 10
SEED_SUBGRID, SEED_NC1_NET, SEED_NC1_MODE_N = (9, 1), (9, 2), (9, 4)
RB4_PARAMETERS = ("eta_start", "eta_peak", "J0", "Delta", "tau_d_ms", "J_lag_frac", "J_T_frac")
RB4_REL_BOX = 0.10
LHS_DRAW_KEY, LHS_POINT_KEY = (7, 9, 0), (7, 9, 1)               # F-19, DL-159 (settled)
LHS_POINTS = 64
LHS_DESIGN_FILE = f"{RUNLIST_DIR}/s16_lhs_design.csv"

PRE_REGISTERED = ("NC1", "NC2", "NC3", "S6", "S16", "S7_map1", "S7_map2", "S7_subgrid")
SUPPLEMENTARY = ("SUPP_P2ref", "SUPP_NC1_modeN")
ALL_LISTS = PRE_REGISTERED + SUPPLEMENTARY
COLUMNS = ("list", "pre_registered", "family", "config", "index", "name", "hash", "kind", "path", "T_ramp_s", "spawn_key", "out_dir", "overrides")


class RunListError(RuntimeError):
    pass


# --- cells --------------------------------------------------------------------------------------

_CELL_COLS = ("index", "name", "kind", "i", "j", "J0", "Delta", "tau_d_ms", "T_ramp_s", "hopf_found", "eta_H", "eta_start", "eta_peak")


def build_cells_file(path=None) -> str:
    """Slow (Hopf scan): rewrite the cell file from analysis.cells; returns the cell-list SHA-256."""
    from . import cells as CE
    cells = CE.build_cells()
    path = Path(path) if path else C.repo_root() / CELLS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(_CELL_COLS)
        for c in cells:
            w.writerow([c["index"], c["name"], c["kind"], c["ij"][0], c["ij"][1], repr(c["J0"]), repr(c["Delta"]), repr(c["tau_d_ms"]),
                        repr(c["T_ramp_s"]), int(c["hopf_found"]), repr(c["eta_H"]), repr(c["eta_start"]), repr(c["eta_peak"])])
    return CE.cell_list_hash(cells)


@lru_cache(maxsize=1)
def load_cells(path=None) -> tuple:
    """The 1,226 cells from the cell file; raises if their cell-list hash is not the frozen value."""
    p = Path(path) if path else C.repo_root() / CELLS_FILE
    out = []
    with open(p, "r", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out.append({"index": int(r["index"]), "name": r["name"], "kind": r["kind"], "ij": [int(r["i"]), int(r["j"])],
                        "J0": float(r["J0"]), "Delta": float(r["Delta"]), "tau_d_ms": float(r["tau_d_ms"]), "T_ramp_s": float(r["T_ramp_s"]),
                        "hopf_found": bool(int(r["hopf_found"])), "eta_H": float(r["eta_H"]), "eta_start": float(r["eta_start"]),
                        "eta_peak": float(r["eta_peak"])})
    from . import cells as CE
    h = CE.cell_list_hash(out)
    if h != FROZEN_CELL_LIST_SHA256:
        raise RunListError(f"cell list SHA-256 {h} is not the frozen value {FROZEN_CELL_LIST_SHA256}")
    return tuple(out)


def map1_cell(i: int, j: int) -> dict:
    c = load_cells()[1 + i * MAP1_N + j]
    assert c["kind"] == "map1" and c["ij"] == [i, j]
    return c


def subgrid_indices(n: int = MAP1_N, m: int = SUBGRID_N) -> list[int]:
    """M9-10: round(linspace(0, n - 1, m)) on both axes."""
    return [int(x) for x in np.round(np.linspace(0, n - 1, m)).astype(int)]


def subgrid_indices_sha256() -> str:
    return hashlib.sha256(C.canonical_json(subgrid_indices()).encode()).hexdigest()


def headline_cell() -> dict:
    return load_cells()[0]


# --- S16 design ---------------------------------------------------------------------------------

def nominal() -> dict:
    """The seven S16 parameters at the headline path (eta_start and eta_peak from eta_H by D12)."""
    h = headline_cell()
    return {"eta_start": h["eta_start"], "eta_peak": h["eta_peak"], "J0": h["J0"], "Delta": h["Delta"], "tau_d_ms": h["tau_d_ms"],
            "J_lag_frac": 0.25, "J_T_frac": 1.0}


def lhs_unit(n: int = LHS_POINTS, d: int = len(RB4_PARAMETERS), root_seed: int = 20261008) -> np.ndarray:
    """M9-11: scipy.stats.qmc.LatinHypercube(d=7), scrambled, no optimisation, generator seeded from the key [7, 9, 0]."""
    from scipy.stats import qmc
    rng = np.random.Generator(np.random.PCG64(P.seed_from_key(root_seed, LHS_DRAW_KEY)))
    return qmc.LatinHypercube(d=d, scramble=True, optimization=None, rng=rng).random(n)


def lhs_design(nom: dict | None = None, rel: float = RB4_REL_BOX) -> np.ndarray:
    """(64, 7) parameter values: nominal x (1 - rel + 2 rel u). A multiplicative box, so a negative J0 stays ordered."""
    nom = nom or nominal()
    base = np.array([nom[p] for p in RB4_PARAMETERS])
    return base[None, :] * (1.0 - rel + 2.0 * rel * lhs_unit())


def write_lhs_design(path=None) -> str:
    path = Path(path) if path else C.repo_root() / LHS_DESIGN_FILE
    X = lhs_design()
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(("point", *RB4_PARAMETERS))
        for k, row in enumerate(X):
            w.writerow((k, *[repr(float(x)) for x in row]))
    return P.sha256_file(path)


def _param_overrides(values: dict) -> dict:
    """resolve_config overrides for S16 parameter values; J0 sets model.J and path.J0 together (M9-11)."""
    ov = {"path.eta_start": values["eta_start"], "path.eta_peak": values["eta_peak"], "model.J": values["J0"], "path.J0": values["J0"],
          "model.Delta": values["Delta"], "model.tau_d_ms": values["tau_d_ms"], "path.J_lag_frac": values["J_lag_frac"],
          "path.J_T_frac": values["J_T_frac"]}
    return ov


# --- entries -------------------------------------------------------------------------------------

def _e(lst, family, config, overrides, out_dir, spawn_key=None) -> dict:
    ov = dict(overrides)
    ov["run.id"] = family
    ov["output.dir"] = out_dir
    if spawn_key is not None:
        ov["seeds.spawn_key"] = list(spawn_key)
    return {"list": lst, "pre_registered": lst in PRE_REGISTERED, "family": family, "config": f"{CONFIG_DIR}/{config}", "overrides": ov,
            "spawn_key": list(spawn_key) if spawn_key is not None else None}


def nc1_fall(cell: dict) -> tuple[float, float]:
    """M9-1: (eta_start, eta_end) of NC1 at a cell: eta falls from the cell's eta_start by (eta_peak - eta_start) of that cell."""
    return cell["eta_start"], cell["eta_start"] - (cell["eta_peak"] - cell["eta_start"])


def _nc1_overrides(cell: dict, T: float) -> dict:
    e0, e1 = nc1_fall(cell)
    return {"path.eta_start": e0, "path.eta_peak": e1, "path.T_ramp_s": T, "model.Delta": cell["Delta"], "model.tau_d_ms": cell["tau_d_ms"]}


def entries(name: str) -> list[dict]:
    h = headline_cell()
    out: list[dict] = []
    if name == "NC1":
        out += [_e(name, "NC1", "nc1.yaml", _nc1_overrides(h, T), "results/S12") for T in GRID13]
        out += [_e(name, "NC1_cells", "nc1.yaml", _nc1_overrides(map1_cell(i, j), 120.0), "results/S12") for i, j in NC1_MAP_CELLS]
        out += [_e(name, "NC1_net", "nc1_net.yaml", _nc1_overrides(h, 120.0), "results/S12", SEED_NC1_NET + (0,))]
    elif name == "NC2":
        out += [_e(name, "NC2", "nc2.yaml", {"path.T_ramp_s": T}, "results/S12") for T in GRID13]
    elif name == "NC3":
        out += [_e(name, "NC3", "nc3.yaml", _nc1_overrides(h, T), "results/S12") for T in GRID13]
    elif name == "S6":
        out += [_e(name, "S6_P3", "s6_p3.yaml", {"path.I_amp": a, "path.T_ramp_s": T}, "results/S6") for a in P3_AMPLITUDES for T in S6_T_RAMP_S]
        out += [_e(name, "S6_P4a", "s6_p4a.yaml", {"path.T_ramp_s": T}, "results/S6") for T in S6_T_RAMP_S]
        out += [_e(name, "S6_P4b", "s6_p4b.yaml", {"path.T_ramp_s": T}, "results/S6") for T in S6_T_RAMP_S]
    elif name == "S16":
        nom = nominal()
        for p in RB4_PARAMETERS:
            for s in (-1, 1):
                v = dict(nom)
                v[p] = nom[p] * (1.0 + s * RB4_REL_BOX)
                out.append(_e(name, "S16_oat", "s16.yaml", _param_overrides(v), "results/S16"))
        X = lhs_design(nom)
        for k in range(LHS_POINTS):
            out.append(_e(name, "S16_lhs", "s16.yaml", _param_overrides(dict(zip(RB4_PARAMETERS, [float(x) for x in X[k]]))), "results/S16",
                          LHS_POINT_KEY + (k,)))
    elif name == "S7_map1":
        for i in range(MAP1_N):
            for j in range(MAP1_N):
                out.append(_e(name, "S7_map1", "s7_map.yaml", _cell_overrides(map1_cell(i, j)), "results/S7"))
    elif name == "S7_map2":
        for c in load_cells():
            if c["kind"] == "map2":
                out.append(_e(name, "S7_map2", "s7_map.yaml", _cell_overrides(c), "results/S7"))
    elif name == "S7_subgrid":
        idx = subgrid_indices()
        for i in idx:
            for j in idx:
                for s in range(N_SEEDS):
                    out.append(_e(name, "S7_subgrid", "s7_subgrid.yaml", _cell_overrides(map1_cell(i, j)), "results/S7", SEED_SUBGRID + (s,)))
    elif name == "SUPP_P2ref":
        out += [_e(name, "S6_P2ref", "s6_p2ref.yaml", {"path.T_ramp_s": T}, "results/S6/supp") for T in (30.0, 300.0)]
    elif name == "SUPP_NC1_modeN":
        out += [_e(name, "NC1_modeN", "nc1_modeN.yaml", _nc1_overrides(h, T), "results/S12/supp", SEED_NC1_MODE_N + (s,))
                for T in GRID13 for s in range(N_SEEDS)]
    else:
        raise RunListError(f"unknown list {name!r}")
    return out


def _cell_overrides(c: dict) -> dict:
    return {"model.Delta": c["Delta"], "model.tau_d_ms": c["tau_d_ms"], "model.J": c["J0"], "path.J0": c["J0"], "path.T_ramp_s": c["T_ramp_s"],
            "path.eta_H": c["eta_H"]}


# --- expansion -----------------------------------------------------------------------------------

def _gate_once(cfg: dict, seen: set) -> None:
    key = cfg["robustness"]["criteria_file"]
    if key not in seen:
        CR.require_frozen_for_config(cfg)           # the runner's gate: the freeze must verify
        seen.add(key)


def expand(name: str, check_gate: bool = True) -> list[dict]:
    """Rows of one list (COLUMNS) plus the resolved cfg under "cfg" and the input hashes under "inputs". Names follow the runner:
    <family>_<index within the family, 4 digits>_<12 hex of the config hash>."""
    rows: list[dict] = []
    seen: set = set()
    counter: dict[str, int] = {}
    root = C.repo_root()
    for e in entries(name):
        cfg = C.resolve_config(root / e["config"], e["overrides"])
        if check_gate:
            _gate_once(cfg, seen)
        h = C.config_hash(cfg)
        k = counter.get(e["family"], 0)
        counter[e["family"]] = k + 1
        out_root = Path(cfg["output"]["dir"])
        out_dir = out_root / e["family"]
        inputs = {cfg["_resolved_from"]["base"]: P.sha256_file(root / cfg["_resolved_from"]["base"]), e["config"]: P.sha256_file(root / e["config"])}
        rows.append({"list": name, "pre_registered": e["pre_registered"], "family": e["family"], "config": e["config"], "index": k,
                     "name": f"{e['family']}_{k:04d}_{C.short_hash(h)}", "hash": h, "kind": cfg["run"]["kind"], "path": cfg["path"]["name"],
                     "T_ramp_s": cfg["path"]["T_ramp_s"], "spawn_key": e["spawn_key"], "out_dir": C.to_posix(root / out_dir),
                     "overrides": e["overrides"], "cfg": cfg, "inputs": inputs})
    return rows


def list_sha256(rows: list[dict]) -> str:
    """SHA-256 of the canonical JSON of [family, config, index, config hash, spawn key] per row, in list order (as ms8_runlist)."""
    return hashlib.sha256(C.canonical_json([[r["family"], r["config"], r["index"], r["hash"], r["spawn_key"]] for r in rows]).encode()).hexdigest()


def breakdown(rows: list[dict]) -> dict:
    out: dict[str, int] = {}
    for r in rows:
        out[r["family"]] = out.get(r["family"], 0) + 1
    return out


def duplicates(rows: list[dict]) -> list[tuple[str, str]]:
    seen: dict[str, str] = {}
    dup = []
    for r in rows:
        if r["hash"] in seen:
            dup.append((seen[r["hash"]], r["name"]))
        seen.setdefault(r["hash"], r["name"])
    return dup


def seed_keys(rows: list[dict]) -> list[tuple[int, ...]]:
    return [tuple(r["spawn_key"]) for r in rows if r["spawn_key"] is not None]


def write_manifest(out_dir=None, names=ALL_LISTS) -> dict:
    """One CSV per list plus ms9_runlists.json (counts, list hashes, subgrid and design hashes) under configs/ms9/runlists/ (committed)."""
    gate = CR.verify_frozen_criteria()
    out = Path(out_dir) if out_dir else C.repo_root() / RUNLIST_DIR
    out.mkdir(parents=True, exist_ok=True)
    summary = {"gate": gate, "cell_list_sha256": FROZEN_CELL_LIST_SHA256, "subgrid_indices": subgrid_indices(),
               "subgrid_indices_sha256": subgrid_indices_sha256(), "lists": {}}
    for name in names:
        rows = expand(name, check_gate=False)
        with open(out / f"runlist_{name}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(COLUMNS)
            for r in rows:
                w.writerow([json.dumps(r[c], sort_keys=True) if c in ("overrides", "spawn_key") else r[c] for c in COLUMNS])
        summary["lists"][name] = {"pre_registered": name in PRE_REGISTERED, "runs": len(rows), "by_family": breakdown(rows),
                                  "sha256": list_sha256(rows), "duplicate_hashes": duplicates(rows)}
    summary["pre_registered_total"] = sum(v["runs"] for v in summary["lists"].values() if v["pre_registered"])
    summary["supplementary_total"] = sum(v["runs"] for v in summary["lists"].values() if not v["pre_registered"])
    (out / "ms9_runlists.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="python -m mprsurge.analysis.ms9_runlist", description="MS9 9b run lists: counts, hashes, manifest")
    ap.add_argument("--write", action="store_true", help="write configs/ms9/runlists/ (cells file must exist; design file is written first)")
    ap.add_argument("--build-cells", action="store_true", help="slow: rewrite configs/ms9/runlists/cells_1226.csv from analysis.cells")
    args = ap.parse_args(argv)
    if args.build_cells:
        print("cell-list SHA-256", build_cells_file())
    if args.write:
        print("S16 design file SHA-256", write_lhs_design())
        s = write_manifest()
        for n, v in s["lists"].items():
            print(f"{n:16s} {'pre-registered' if v['pre_registered'] else 'SUPPLEMENTARY':15s} {v['runs']:5d} runs {v['by_family']}  SHA-256 {v['sha256'][:16]}  duplicates {len(v['duplicate_hashes'])}")
        print(f"pre-registered total {s['pre_registered_total']}, supplementary {s['supplementary_total']}; subgrid indices {s['subgrid_indices']} SHA-256 {s['subgrid_indices_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
