"""MS10 run lists (10c, DRAFT; docs/ms10_plan.md "Rulings after 10a" and "Rulings after 10b", DL-277 to DL-300).

Analysis only: every entry is configs/ms10/ms10_net.yaml (network) or ms10_mf.yaml (companion mean field) plus an override dict; `expand` resolves it with
config.resolve_config and applies the frozen-criteria gate, nothing integrates. Parameters are read from configs/ms10/ms10_lists.yaml, the four S8 map cells
from configs/ms10/s8_cells.yaml. While any cell is TO_BE_CHOSEN, `expand` raises RunListError for the lists that need cells (S8, C2_S8, MF_COMPANION);
`nominal_counts` gives their run counts without cells. While a data file says status DRAFT nothing is frozen (the launcher refuses a real launch).

Lists: S8 (headline T_ramp {10, 120} s x 3 seeds, keys [10, 1, s]; 4 cells at 30 s x 3 seeds, keys [10, 2, c, s]), S9 (N x 10 seeds, [10, 3, n, s]),
S10 (shape x 3 seeds, [10, 4, l, s]), C2 controls (R17: 12 configurations x 3 seeds, [10, 5, k, s]; C2_S8 18, C2_S9 12, C2_S10 6 runs, each counted under the
S-ID it accompanies), MF_COMPANION (R13: mode D, 4 cells at 30 s and the headline at 60 s, 5 runs). Controls hold eta_start = eta_peak and J_end = J0 with
the T_ramp of their ramp run, so duration and start state are those of the ramp run (S12x_ctrl_mf pattern).
"""
from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path

import yaml

from .. import config as C
from .. import provenance as P
from . import ms9_runlist as RL9

CONFIG_DIR = "configs/ms10"
LISTS_FILE = f"{CONFIG_DIR}/ms10_lists.yaml"
CELLS_FILE = f"{CONFIG_DIR}/s8_cells.yaml"
REFS_FILE = f"{CONFIG_DIR}/mf_references.yaml"
CANDIDATES_FILE = "docs/ms10_10b_s8_candidates.csv"
PLACEHOLDER = "TO_BE_CHOSEN"
RAMP_LISTS = ("S8", "S9", "S10")
CONTROL_LISTS = ("C2_S8", "C2_S9", "C2_S10")
ALL_LISTS = RAMP_LISTS + CONTROL_LISTS + ("MF_COMPANION",)
NEEDS_CELLS = ("S8", "C2_S8", "MF_COMPANION")
EXPECTED_COUNTS = {"S8": 18, "S9": 40, "S10": 9, "C2_S8": 18, "C2_S9": 12, "C2_S10": 6, "MF_COMPANION": 5}      # 10c prompt; expand asserts them
EXPECTED_CONTROLS = 36
N_CONTROL_CONFIGS = 12
COLUMNS = RL9.COLUMNS


class RunListError(RL9.RunListError):
    pass


def _read(rel: str) -> dict:
    return yaml.safe_load((C.repo_root() / rel).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def params() -> dict:
    return _read(LISTS_FILE)


STATUS_YAML = (LISTS_FILE, CELLS_FILE, REFS_FILE, f"{CONFIG_DIR}/ms10_eval.yaml")
STATUS_COMMENT = (f"{CONFIG_DIR}/ms10_net.yaml", f"{CONFIG_DIR}/ms10_mf.yaml")      # the config schema has no status key: first comment line "# STATUS: ..."


def _comment_status(rel: str) -> str:
    first = (C.repo_root() / rel).read_text(encoding="utf-8").splitlines()[0]
    m = re.match(r"#\s*STATUS:\s*(\w+)", first)
    return m.group(1) if m else "MISSING"


def status() -> dict:
    """Status of each data file (DRAFT until frozen): the status field of the yaml data files, the first comment line of the two run configs."""
    return {**{f: _read(f)["status"] for f in STATUS_YAML}, **{f: _comment_status(f) for f in STATUS_COMMENT}}


def is_draft() -> bool:
    return any(s != "FROZEN" for s in status().values())


# --- cells --------------------------------------------------------------------------------------

def chosen_cells() -> list[dict]:
    """The four S8 map cells (map 1 cell dicts, c = 0..3). Raises RunListError while any entry is TO_BE_CHOSEN; checks a filled entry against the 10b
    candidate table (R14: class by stratum, Delta side of the median of the 30 map-1 Delta values, dist_refined > 1, four distinct)."""
    ent = _read(CELLS_FILE)["cells"]
    if len(ent) != 4 or [e["c"] for e in ent] != [0, 1, 2, 3]:
        raise RunListError("s8_cells.yaml must list cells c = 0..3")
    if any(PLACEHOLDER in (e["i"], e["j"]) for e in ent):
        raise RunListError(f"{CELLS_FILE}: {PLACEHOLDER}: the S8 map cells are chosen by the reviewer; no run list is built until all four are filled")
    ij = [(int(e["i"]), int(e["j"])) for e in ent]
    if len(set(ij)) != 4:
        raise RunListError("the four S8 map cells must be distinct")
    cand = {}
    with open(C.repo_root() / CANDIDATES_FILE, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            cand[(int(r["i"]), int(r["j"]))] = r
    ds = sorted({float(r["Delta"]) for r in cand.values()})
    med = 0.5 * (ds[14] + ds[15])
    for e, (i, j) in zip(ent, ij):
        r = cand[(i, j)]
        cls, side = e["stratum"].split(" ")[0], e["stratum"].split(" ")[1]
        if r["class"] != cls or (float(r["Delta"]) < med) != (side == "below"):
            raise RunListError(f"cell {(i, j)} is {r['class']}, Delta {r['Delta']}: not in stratum {e['stratum']!r}")
        if not float(r["dist_refined"]) > 1.0:
            raise RunListError(f"cell {(i, j)}: dist_refined {r['dist_refined']} is not more than one original cell (R14)")
    return [RL9.map1_cell(i, j) for i, j in ij]


def verify_references() -> list[dict]:
    """R13: the stored mode-D records of the headline at T_ramp 10 s and 120 s; the SHA-256 of every listed file must equal the value in the config."""
    out = []
    for ref in _read(REFS_FILE)["references"]:
        for f, h in ref["files"].items():
            got = P.sha256_file(C.repo_root() / f)
            if got != h:
                raise RunListError(f"{f}: SHA-256 {got} is not the listed {h}")
        out.append({"T_ramp_s": ref["T_ramp_s"], "run_id": ref["run_id"], "files": len(ref["files"])})
    return out


# --- entries -------------------------------------------------------------------------------------

def _e(lst, family, config, overrides, out_dir, spawn_key=None) -> dict:
    ov = dict(overrides)
    ov["run.id"] = family
    ov["output.dir"] = out_dir
    if spawn_key is not None:
        ov["seeds.spawn_key"] = list(spawn_key)
    return {"list": lst, "family": family, "config": f"{CONFIG_DIR}/{config}", "overrides": ov,
            "spawn_key": list(spawn_key) if spawn_key is not None else None}


def _headline_ov(T: float, N: int = 10000, het: str = "lorentzian") -> dict:
    return {"path.eta_H": RL9.headline_cell()["eta_H"], "path.T_ramp_s": T, "network.N": N, "network.het_dist": het}


def _cell_ov(c: dict, T: float, N: int = 10000) -> dict:
    return {"model.Delta": c["Delta"], "model.tau_d_ms": c["tau_d_ms"], "model.J": c["J0"], "path.J0": c["J0"], "path.T_ramp_s": T, "path.eta_H": c["eta_H"],
            "network.N": N, "network.het_dist": "lorentzian"}


def _control_ov(cfg: dict, cells) -> dict:
    """Constant-parameter control: the start state of the configuration held for the whole run (eta_peak = eta_start, J_end = J0)."""
    c = RL9.headline_cell() if cfg["start"] == "headline" else cells[cfg["start"]["cell"]]
    ov = {"model.Delta": c["Delta"], "model.tau_d_ms": c["tau_d_ms"], "model.J": c["J0"], "path.J0": c["J0"], "path.eta_start": c["eta_start"],
          "path.eta_peak": c["eta_start"], "path.J_end": c["J0"], "path.T_ramp_s": cfg["T_ramp_s"], "network.N": cfg["N"],
          "network.het_dist": cfg["het_dist"]}
    return ov


def entries(name: str) -> list[dict]:
    p = params()
    out: list[dict] = []
    if name == "S8":
        h, c = p["lists"]["S8"]["headline"], p["lists"]["S8"]["cells"]
        cells = chosen_cells()
        out += [_e(name, "S8_head", "ms10_net.yaml", _headline_ov(T), "results/S8", tuple(h["key"]) + (s,)) for T in h["T_ramp_s"] for s in range(h["seeds"])]
        out += [_e(name, "S8_cells", "ms10_net.yaml", _cell_ov(cells[k], c["T_ramp_s"]), "results/S8", tuple(c["key"]) + (k, s))
                for k in range(c["n_cells"]) for s in range(c["seeds"])]
    elif name == "S9":
        q = p["lists"]["S9"]
        out += [_e(name, "S9", "ms10_net.yaml", _headline_ov(q["T_ramp_s"], N), "results/S9", tuple(q["key"]) + (n, s))
                for n, N in enumerate(q["N"]) for s in range(q["seeds"])]
    elif name == "S10":
        q = p["lists"]["S10"]
        out += [_e(name, "S10", "ms10_net.yaml", _headline_ov(q["T_ramp_s"], q["N"], het), "results/S10", tuple(q["key"]) + (l, s))
                for l, het in enumerate(q["het_dist"]) for s in range(q["seeds"])]
    elif name in CONTROL_LISTS:
        sid = name.split("_")[1]
        cc = p["controls"]
        cells = chosen_cells() if sid == "S8" else None
        out += [_e(name, f"{sid}_ctrl", "ms10_net.yaml", _control_ov(x, cells), f"results/{sid}", tuple(cc["key"]) + (x["k"], s))
                for x in cc["configs"] if x["accompanies"] == sid for s in range(cc["seeds"])]
    elif name == "MF_COMPANION":
        q = p["lists"]["MF_COMPANION"]
        out += [_e(name, "S8_mf_cells", "ms10_mf.yaml", {"model.Delta": c["Delta"], "model.tau_d_ms": c["tau_d_ms"], "model.J": c["J0"], "path.J0": c["J0"],
                                                         "path.T_ramp_s": q["cells_T_ramp_s"], "path.eta_H": c["eta_H"]}, "results/S8/mf")
                for c in chosen_cells()]
        out.append(_e(name, "S8_mf_head60", "ms10_mf.yaml", {"path.T_ramp_s": q["headline_T_ramp_s"]}, "results/S8/mf"))
    else:
        raise RunListError(f"unknown list {name!r}")
    return out


def nominal_counts() -> dict:
    """Run counts from the parameter file alone (no cells needed)."""
    p = params()
    L, cc = p["lists"], p["controls"]
    n = {"S8": len(L["S8"]["headline"]["T_ramp_s"]) * L["S8"]["headline"]["seeds"] + L["S8"]["cells"]["n_cells"] * L["S8"]["cells"]["seeds"],
         "S9": len(L["S9"]["N"]) * L["S9"]["seeds"], "S10": len(L["S10"]["het_dist"]) * L["S10"]["seeds"],
         "MF_COMPANION": L["S8"]["cells"]["n_cells"] + 1}
    for sid in ("S8", "S9", "S10"):
        n[f"C2_{sid}"] = sum(1 for x in cc["configs"] if x["accompanies"] == sid) * cc["seeds"]
    return n


def control_total() -> int:
    n = nominal_counts()
    return sum(n[k] for k in CONTROL_LISTS)


# --- expansion -----------------------------------------------------------------------------------

def expand(name: str, check_gate: bool = True) -> list[dict]:
    """Rows of one list (COLUMNS) plus the resolved cfg under "cfg" and the input hashes under "inputs" (as ms9_runlist.expand)."""
    rows: list[dict] = []
    seen: set = set()
    counter: dict[str, int] = {}
    root = C.repo_root()
    for e in entries(name):
        cfg = C.resolve_config(root / e["config"], e["overrides"])
        if check_gate:
            RL9._gate_once(cfg, seen)
        h = C.config_hash(cfg)
        k = counter.get(e["family"], 0)
        counter[e["family"]] = k + 1
        out_dir = Path(cfg["output"]["dir"]) / e["family"]
        inputs = {cfg["_resolved_from"]["base"]: P.sha256_file(root / cfg["_resolved_from"]["base"]), e["config"]: P.sha256_file(root / e["config"])}
        rows.append({"list": name, "pre_registered": True, "family": e["family"], "config": e["config"], "index": k,
                     "name": f"{e['family']}_{k:04d}_{C.short_hash(h)}", "hash": h, "kind": cfg["run"]["kind"], "path": cfg["path"]["name"],
                     "T_ramp_s": cfg["path"]["T_ramp_s"], "spawn_key": e["spawn_key"], "out_dir": C.to_posix(root / out_dir),
                     "overrides": e["overrides"], "cfg": cfg, "inputs": inputs})
    if len(rows) != EXPECTED_COUNTS[name]:
        raise RunListError(f"{name}: {len(rows)} runs, expected {EXPECTED_COUNTS[name]}")
    return rows


list_sha256 = RL9.list_sha256
breakdown = RL9.breakdown
duplicates = RL9.duplicates
seed_keys = RL9.seed_keys


def summary(names=ALL_LISTS) -> dict:
    """Counts, list SHA-256 (None while the list needs unchosen cells), breakdown and duplicate config hashes for each list."""
    out = {}
    nom = nominal_counts()
    for name in names:
        try:
            rows = expand(name)
            out[name] = {"runs": len(rows), "sha256": list_sha256(rows), "by_family": breakdown(rows), "duplicate_hashes": duplicates(rows)}
        except RunListError as exc:
            if name not in NEEDS_CELLS or PLACEHOLDER not in str(exc):
                raise
            out[name] = {"runs": nom[name], "sha256": None, "by_family": None, "duplicate_hashes": None, "unresolved": PLACEHOLDER}
    return out
