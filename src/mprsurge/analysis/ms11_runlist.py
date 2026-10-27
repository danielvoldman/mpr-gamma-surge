"""MS11 run lists (11b; docs/ms11_eval_rules.md, DL-336 to DL-344).

Analysis only: every entry is one of the four MS11 run configs (configs/ms11/ms11_{mf,mfn,ctrl,net}.yaml) plus an override dict; `expand` resolves it with
config.resolve_config and applies the frozen-criteria gate, nothing integrates. Parameters are read from the four definition files configs/ms11/lists/<LIST>.yaml.

Lists (the MS10 pattern: all cells of a launch go into one pool, longest first, restartable):
  MS11_S11      120  S11: sigma factor {0.5, 1, 2} x T_ramp {10, 30, 120, 300} s x 10 seeds, mode N, P2 headline, key [11, 1, s]
  MS11_CTRL      30  DL-251 constant-parameter controls (POST-HOC AMENDMENT), headline cell, T_ramp 120 s, 3 sigma factors x 10 seeds, key [11, 2, s]
  MS11_S13_MF    68  S13 mean field at T_ramp 10 s and 316.2278 s: rtol 4, delta0 4, Radau 0 (cut order step 1, DL-337), floor 60 at the default rung, key [11, 3, t, l, s]
  MS11_S13_NET   18  S13 network, N = 1e4, 10 s ramp: 6 configurations x 3 seeds, key [11, 4, s]
  MS11_RB9D       2  RB9(d), POST HOC, reported only (11d, DL-367): headline run with model.tau_ms 8 and 12 ms, nothing else changed, mean field mode D, no seed key (spawn key null)
The frozen list hashes and seed-key hashes are in configs/ms11/ms11_list_hashes.yaml; `check_launch` is the launcher's refusal rule (plan 8 item 10).
"""
from __future__ import annotations

import hashlib
import shutil
from functools import lru_cache
from pathlib import Path

import yaml

from .. import config as C
from .. import criteria as CR
from .. import provenance as P
from . import ms9_runlist as RL9
from . import timing as T

CONFIG_DIR = "configs/ms11"
LISTS_DIR = f"{CONFIG_DIR}/lists"
HASHES_FILE = f"{CONFIG_DIR}/ms11_list_hashes.yaml"
EVAL_FILE = f"{CONFIG_DIR}/ms11_eval.yaml"
PREREG_LISTS = ("MS11_S11", "MS11_CTRL", "MS11_S13_MF", "MS11_S13_NET")
POSTHOC_LISTS = ("MS11_RB9D",)                  # 11d (DL-370): RB9(d), separate post hoc list, reported only, feeds no gate (ruling 12)
ALL_LISTS = PREREG_LISTS + POSTHOC_LISTS
EXPECTED_COUNTS = {"MS11_S11": 120, "MS11_CTRL": 30, "MS11_S13_MF": 68, "MS11_S13_NET": 18, "MS11_RB9D": 2}      # 11b prompt, DL-337 and 11d (DL-370); expand asserts them
COLUMNS = RL9.COLUMNS
STATUS_COMMENT = tuple(f"{CONFIG_DIR}/ms11_{n}.yaml" for n in ("mf", "mfn", "ctrl", "net"))      # the config schema has no status key: first comment line "# STATUS: ..."
BYTES_PER_SAMPLE = 8 * 8                  # 8 float64 arrays at 1 kHz (M9-16, DL-223); the network record is assumed the same (UNVERIFIED)


class RunListError(RL9.RunListError):
    pass


def _read(rel: str) -> dict:
    return yaml.safe_load((C.repo_root() / rel).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def params(name: str) -> dict:
    if name not in ALL_LISTS:
        raise RunListError(f"unknown list {name!r}")
    p = _read(f"{LISTS_DIR}/{name}.yaml")
    if p.get("list") != name:
        raise RunListError(f"{LISTS_DIR}/{name}.yaml names list {p.get('list')!r}")
    return p


def definition_files() -> list[str]:
    return [f"{LISTS_DIR}/{n}.yaml" for n in ALL_LISTS]


def definition_sha256(name: str) -> str:
    return P.sha256_file(C.repo_root() / f"{LISTS_DIR}/{name}.yaml")


def _comment_status(rel: str) -> str:
    import re
    first = (C.repo_root() / rel).read_text(encoding="utf-8").splitlines()[0]
    m = re.match(r"#\s*STATUS:\s*(\w+)", first)
    return m.group(1) if m else "MISSING"


def status() -> dict:
    """Status of each data file: the status field of the list definition files and the hashes file, the first comment line of the four run configs."""
    return {**{f: _read(f)["status"] for f in definition_files()}, HASHES_FILE: _read(HASHES_FILE)["status"],
            **{f: _comment_status(f) for f in STATUS_COMMENT}}


def is_draft() -> bool:
    return any(s != "FROZEN" for s in status().values())


# --- entries -------------------------------------------------------------------------------------

def _e(lst, family, config, overrides, out_dir, spawn_key=None) -> dict:
    ov = dict(overrides)
    ov["run.id"] = family
    ov["output.dir"] = out_dir
    if spawn_key is not None:
        ov["seeds.spawn_key"] = list(spawn_key)
    return {"list": lst, "family": family, "config": config, "overrides": ov, "spawn_key": list(spawn_key) if spawn_key is not None else None}


def _control_ov(T_ramp_s: float, sigma_factor: float) -> dict:
    """Constant-parameter control: the start state of the headline held for the whole run (eta_peak = eta_start, J_end = J0), as the S12x_ctrl_mf pattern."""
    c = RL9.headline_cell()
    return {"model.Delta": c["Delta"], "model.tau_d_ms": c["tau_d_ms"], "model.J": c["J0"], "path.J0": c["J0"], "path.J_end": c["J0"],
            "path.eta_start": c["eta_start"], "path.eta_peak": c["eta_start"], "path.T_ramp_s": T_ramp_s, "noise.sigma_factor": sigma_factor}


def entries(name: str) -> list[dict]:
    p = params(name)
    out: list[dict] = []
    if name == "MS11_S11":
        out += [_e(name, p["family"], p["config"], {"path.T_ramp_s": T_, "noise.sigma_factor": f}, "results/S11", tuple(p["key"]) + (s,))
                for f in p["sigma_factors"] for T_ in p["T_ramp_s"] for s in range(p["n_seeds"])]
    elif name == "MS11_CTRL":
        out += [_e(name, p["family"], p["config"], _control_ov(p["T_ramp_s"], f), "results/S11", tuple(p["key"]) + (s,))
                for f in p["sigma_factors"] for s in range(p["n_seeds"])]
    elif name == "MS11_S13_MF":
        fl = p["floor"]
        for t, T_ in enumerate(p["T_ramp_s"]):
            out += [_e(name, "S13_rtol", p["config_mf"], {"path.T_ramp_s": T_, "solver.rtol": r}, "results/S13/ms11") for r in p["rtol_new"]]
            out += [_e(name, "S13_delta0", p["config_mf"], {"path.T_ramp_s": T_, "solver.delta0": d}, "results/S13/ms11") for d in p["delta0_new"]]
            out += [_e(name, "S13_floor", p["config_mfn"], {"path.T_ramp_s": T_, "noise.sigma": sg, "noise.sigma_factor": 1.0, "noise.dt_tau": fl["dt_tau"],
                                                           "noise.coupling_dt_tau": fl["coupling_dt_tau"]}, "results/S13/ms11", tuple(fl["key"]) + (t, l, s))
                    for l, sg in enumerate(fl["sigma_floor_levels"]) for s in range(fl["seeds"])]
    elif name == "MS11_S13_NET":
        out += [_e(name, p["family"], p["config"], {"path.T_ramp_s": p["T_ramp_s"], "network.N": p["N"], "network.dt_tau": x["dt_tau"], "network.V_peak": x["V_peak"],
                                                     "network.V_reset": -x["V_peak"]}, "results/S13/ms11", tuple(p["key"]) + (s,))
                for x in p["configurations"] for s in range(p["n_seeds"])]
    elif name == "MS11_RB9D":
        out += [_e(name, p["family"], p["config"], {"path.T_ramp_s": p["T_ramp_s"], "model.tau_ms": t}, "results/RB9D") for t in p["tau_ms"]]       # no seed key: deterministic
    return out


def nominal_counts() -> dict:
    """Run counts from the definition files alone."""
    a, b, c, d, e = (params(n) for n in ALL_LISTS)
    return {"MS11_S11": len(a["sigma_factors"]) * len(a["T_ramp_s"]) * a["n_seeds"], "MS11_CTRL": len(b["sigma_factors"]) * b["n_seeds"], "MS11_RB9D": len(e["tau_ms"]),
            "MS11_S13_MF": len(c["T_ramp_s"]) * (len(c["rtol_new"]) + len(c["delta0_new"]) + len(c["floor"]["sigma_floor_levels"]) * c["floor"]["seeds"]) + c["radau"]["runs"],
            "MS11_S13_NET": len(d["configurations"]) * d["n_seeds"]}


# --- expansion -----------------------------------------------------------------------------------

def expand(name: str, check_gate: bool = True) -> list[dict]:
    """Rows of one list (COLUMNS) plus the resolved cfg under "cfg" and the input hashes under "inputs" (as ms10_runlist.expand)."""
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
        rows.append({"list": name, "pre_registered": name in PREREG_LISTS, "family": e["family"], "config": e["config"], "index": k,
                     "name": f"{e['family']}_{k:04d}_{C.short_hash(h)}", "hash": h, "kind": cfg["run"]["kind"], "path": cfg["path"]["name"],
                     "T_ramp_s": cfg["path"]["T_ramp_s"], "spawn_key": e["spawn_key"], "out_dir": C.to_posix(root / out_dir),
                     "overrides": e["overrides"], "cfg": cfg, "inputs": inputs})
    if len(rows) != EXPECTED_COUNTS[name] or len(rows) != params(name)["expected_runs"]:
        raise RunListError(f"{name}: {len(rows)} runs, expected {EXPECTED_COUNTS[name]} (definition file: {params(name)['expected_runs']})")
    return rows


list_sha256 = RL9.list_sha256
breakdown = RL9.breakdown
duplicates = RL9.duplicates
seed_keys = RL9.seed_keys


def keys_sha256(rows: list[dict]) -> str:
    return hashlib.sha256(C.canonical_json([list(k) for k in seed_keys(rows)]).encode()).hexdigest()


def summary(names=ALL_LISTS) -> dict:
    """Counts, list SHA-256, seed-key SHA-256, breakdown and duplicate config hashes for each list."""
    out = {}
    for name in names:
        rows = expand(name)
        out[name] = {"runs": len(rows), "sha256": list_sha256(rows), "keys_sha256": keys_sha256(rows), "by_family": breakdown(rows),
                     "duplicate_hashes": duplicates(rows), "n_seed_keys": len(seed_keys(rows)), "definition_sha256": definition_sha256(name)}
    return out


# --- launch refusal rules (plan 8 item 10; as MS10 10e) -------------------------------------------

def frozen_hashes() -> dict:
    return _read(HASHES_FILE)["lists"]


def disk_estimate_bytes(rows: list[dict]) -> float:
    """Raw size of the records of a list: 8 float64 arrays at 1 kHz over the simulated time (tau_simulated, so the discard is included; an upper bound for kept samples)."""
    return sum(T.tau_simulated(r["cfg"]) * r["cfg"]["model"]["tau_ms"] / 1000.0 * 1000.0 * BYTES_PER_SAMPLE for r in rows)


def check_launch(names, disk_path=None) -> list[str]:
    """Reasons to refuse a real launch of these lists (empty: none). Never raises for a refusal; each reason is one string."""
    why: list[str] = []
    try:
        CR.verify_frozen_criteria()
    except Exception as exc:                                    # CriteriaError and any git failure
        why.append(f"criteria loader: {exc}")
    if P.environment_info(with_julia=False)["git"].get("dirty"):
        why.append("git tree is dirty: commit first (records must show dirty = false)")
    st = status()
    why += [f"{f}: status {s}, not FROZEN" for f, s in st.items() if s != "FROZEN"]
    try:
        from . import ms11_eval_choices as EC
        open_ = EC.open_fields()
        if open_:
            why.append(f"{EVAL_FILE}: required evaluation fields still open ({len(open_)}): {', '.join(open_)}")
    except Exception as exc:
        why.append(f"{EVAL_FILE}: {exc}")
    froz = frozen_hashes()
    from . import ms11_counts as MC
    proposed = set(MC.proposed_seed_keys())
    disk_need = 0.0
    for n in names:
        try:
            rows = expand(n)
        except Exception as exc:
            why.append(f"{n}: cannot be expanded: {exc}")
            continue
        f = froz.get(n) or {}
        if f.get("sha256") != list_sha256(rows):
            why.append(f"{n}: list SHA-256 {list_sha256(rows)} is not the frozen {f.get('sha256')}")
        if f.get("keys_sha256") != keys_sha256(rows):
            why.append(f"{n}: seed keys do not equal the frozen keys")
        if f.get("runs") != len(rows):
            why.append(f"{n}: {len(rows)} runs, frozen {f.get('runs')}")
        bad = [k for k in seed_keys(rows) if tuple(k) not in proposed]
        if bad:
            why.append(f"{n}: seed key {bad[0]} is not in the confirmed key set of ms11_counts")
        disk_need += disk_estimate_bytes(rows)
    free = shutil.disk_usage(disk_path or C.repo_root()).free
    if free < disk_need:
        why.append(f"free disk space {free / 1e9:.1f} GB is below the estimated {disk_need / 1e9:.2f} GB")
    return why
