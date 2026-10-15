"""Configuration: load, resolve, validate and hash (plan section 10.3).

resolve_config merges, in this order (DL-054), base < ref_point < run file <
--set overrides, derives eta_start, eta_peak and eps (DL-065, DL-067), rejects unknown
keys and validates every key against a typed schema, casting or rejecting
values (PyYAML reads 1e-10 as a string). config_hash is the SHA-256 of the
canonical JSON of the integration inputs (DL-057).
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import warnings
from dataclasses import dataclass
from pathlib import Path

import yaml

from .params import REF_CENI_TAU_D_MS, REF_POINTS
from .units import s_to_tau

ETA_START_OFFSET = 1.5  # D12: eta_start = eta_H - 1.5
ETA_PEAK_FLOOR = 4.0    # D12: eta_peak = max(4, eta_H + 2)
ETA_PEAK_OFFSET = 2.0

ETA_STATUSES = ("unresolved", "provisional", "explicit", "A4")  # DL-065, DL-067
TAU_D_MS_RANGE = (1.0, 50.0)  # D11
RUN_KINDS = ("mf", "mf_noisy", "a1", "s1", "a2")  # DL-055; "a1", "s1", "a2" are MS2 tasks; "network" is added at MS5
RAMP_PATH_NAMES = ("path_eta", "path_hypoxia", "path_drive", "path_delta_up",
                   "path_delta_down", "path_updown")  # P1, P2, P3, P4a, P4b, P5
FORCING_PATH_NAMES = ("I_step", "I_sin")  # MS2 forcing paths for S1 (DL-085 item 4)
PATH_NAMES = RAMP_PATH_NAMES + FORCING_PATH_NAMES

# Path kinds that read path.t_on_s (every ramp path) and path.J0 (P2 and the paths built
# on it: P3, P4a, P4b; NC2 runs on P3). I_step and I_sin (MS2) are in neither set.
RAMP_PATHS = RAMP_PATH_NAMES
J0_PATHS = ("path_hypoxia", "path_drive", "path_delta_up", "path_delta_down")

# A1 grid and DL-085 refinement widths (plan 5.2 A1; widths UNVERIFIED, the user's). Not config
# keys (the plan lists none); hash_view adds them for run.kind = a1, so changing one changes the
# hash (DL-087). analysis/bifurcation.py reads its constants from here.
A1_GRID = {"n_eta": 241, "n_J": 201, "eta_range": [-10.0, 2.0], "J_range": [0.0, 20.0],
           "band_cells": 4, "box_cells": 10}

# A2 constants (plan 5.2 A2; DL-089). The K4 tail fit ends at t = 40 tau (DL-076; the user's instruction of
# 2026-10-15). Not config keys; hash_view adds them, with the primary band, for run.kind = a2.
A2_WINDOW = {"t_end_tau": 40.0}

# Sections and keys that enter config_hash (DL-057).
_HASH_SECTIONS = ("model", "path", "solver", "noise", "network", "durations")


class ConfigError(ValueError):
    """Invalid configuration: unknown key, wrong type or inconsistent values."""


@dataclass(frozen=True)
class Spec:
    tag: str                      # float int str bool floats floats2 pairs ints
    nullable: bool = False
    choices: tuple | None = None
    positive: bool = False        # strictly > 0 (scalars only)
    derived: bool = False         # filled by resolve_config, never user-set
    optional: bool = False        # absent from base.yaml; in the hash only when given (DL-085 item 4)


def _s(tag, **kw):
    return Spec(tag, **kw)


SCHEMA: dict[str, dict[str, Spec]] = {
    "model": {
        "type": _s("str", choices=("M2", "M3")),
        "ref_point": _s("str", nullable=True, choices=tuple(REF_POINTS)),
        "tau_ms": _s("float", positive=True),
        "tau_d_ms": _s("float", nullable=True, positive=True),
        "eta_bar": _s("float"), "Delta": _s("float", positive=True),
        "J": _s("float"), "I_drive": _s("float"),
    },
    "path": {
        "name": _s("str", choices=PATH_NAMES),
        "profile": _s("str", choices=("linear", "sigmoid")),
        "sigmoid_k": _s("float", positive=True),
        "T_ramp_s": _s("float", positive=True), "t_on_s": _s("float"),
        "eta_H": _s("float", nullable=True),
        "eta_start": _s("float", nullable=True),
        "eta_peak": _s("float", nullable=True),
        "eta_path_status": _s("str", choices=ETA_STATUSES, derived=True),
        "eps": _s("float", nullable=True, derived=True),
        "J0": _s("float"), "J_end": _s("float"),
        "J_lag_frac": _s("float"), "J_T_frac": _s("float"),
        "I_amp": _s("float"), "I_rise_frac": _s("float"),
        "I_plateau_frac": _s("float"), "I_fall_frac": _s("float"),
        "Delta_factor": _s("float", positive=True),
        "I_period_s": _s("float", positive=True, optional=True),   # I_sin period; required there
    },
    "solver": {
        "method": _s("str", choices=("DOP853", "Radau")),
        "rtol": _s("float", positive=True), "atol": _s("float", positive=True),
        "max_step_tau": _s("float", positive=True),
        "dt_out_ms": _s("float", positive=True), "delta0": _s("float"),
    },
    "noise": {
        "scheme": _s("str", choices=("Heun",)),
        "sigma": _s("float", nullable=True),
        "sigma_factor": _s("float", positive=True),
        "dt_tau": _s("float", positive=True),
        "floor_levels": _s("floats", nullable=True),
    },
    "network": {
        "N": _s("int", positive=True), "dt_tau": _s("float", positive=True),
        "V_peak": _s("float", positive=True), "V_reset": _s("float"),
        "het_dist": _s("str", choices=("lorentzian", "gaussian", "uniform")),
        "het_sampling": _s("str", choices=("quantile", "random")),
        "init_V_range": _s("floats2"),
        "rate_bin_ms": _s("float", positive=True),
        "n_raster": _s("int", positive=True), "exclude_refractory": _s("bool"),
    },
    "durations": {
        "baseline_s": _s("float", positive=True),
        "hold_s": _s("float", positive=True),
        "discard_s": _s("float"),
    },
    "analysis": {
        "band_primary_hz": _s("floats2"), "bands_secondary_hz": _s("pairs"),
        "total_band_hz": _s("floats2"),
        "window_rule": _s("str", choices=("D4",)),
        "window_s": _s("float", positive=True),
        "taper": _s("str", choices=("hann",)),
        "rel_factor": _s("float", positive=True),
        "abs_factor": _s("float", positive=True),
        "amin_factor": _s("float", positive=True),
        "min_cycles": _s("int", positive=True),
        "collapse_r_frac": _s("float", positive=True),
    },
    "sweep": {
        "x_name": _s("str", nullable=True), "x_values": _s("floats", nullable=True),
        "y_name": _s("str", nullable=True), "y_values": _s("floats", nullable=True),
        "T_ramp_values": _s("floats", nullable=True),
    },
    "seeds": {
        "root_seed": _s("int"), "n_seeds": _s("int", positive=True),
        "spawn_key": _s("ints", nullable=True),
    },
    "run": {
        "id": _s("str", nullable=True), "workers": _s("int", positive=True),
        "kind": _s("str", choices=RUN_KINDS),
        "wall_limit_s": _s("float", nullable=True, positive=True),
    },
    "output": {"dir": _s("str")},
    "replication": {"tolerances_file": _s("str")},
    "robustness": {
        "check_id": _s("str", nullable=True),
        "criteria_file": _s("str", nullable=True),
        "criteria_sha256": _s("str", nullable=True),
    },
    "budget": {"max_wall_h": _s("float", positive=True)},
}

_META_KEY = "_resolved_from"


def repo_root() -> Path:
    """Repository root; configs/ is resolved from here, not from the cwd."""
    return Path(__file__).resolve().parents[2]


def to_posix(path) -> str:
    """POSIX form of a path, relative to the repository root when inside it."""
    p = Path(path)
    try:
        p = p.resolve().relative_to(repo_root())
    except (ValueError, OSError):
        pass
    return p.as_posix()


# --- casting -----------------------------------------------------------------

def _cast_scalar(tag: str, value, where: str):
    if tag == "float":
        if isinstance(value, bool):
            raise ConfigError(f"{where}: expected a number, got bool {value!r}")
        if isinstance(value, (int, float)):
            out = float(value)
        elif isinstance(value, str):
            try:
                out = float(value.strip())
            except ValueError:
                raise ConfigError(f"{where}: cannot read {value!r} as a number") from None
        else:
            raise ConfigError(f"{where}: expected a number, got {type(value).__name__}")
        if not math.isfinite(out):
            raise ConfigError(f"{where}: value must be finite, got {value!r}")
        return out
    if tag == "int":
        if isinstance(value, bool):
            raise ConfigError(f"{where}: expected an integer, got bool {value!r}")
        if isinstance(value, int):
            return value
        if isinstance(value, (float, str)):
            try:
                f = float(value.strip() if isinstance(value, str) else value)
            except ValueError:
                raise ConfigError(f"{where}: cannot read {value!r} as an integer") from None
            if math.isfinite(f) and f == int(f):
                return int(f)
        raise ConfigError(f"{where}: expected an integer, got {value!r}")
    if tag == "str":
        if not isinstance(value, str):
            raise ConfigError(f"{where}: expected a string, got {type(value).__name__}")
        return value
    if tag == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lower() in ("true", "false"):
            return value.strip().lower() == "true"
        raise ConfigError(f"{where}: expected true or false, got {value!r}")
    raise AssertionError(tag)


def _cast(spec: Spec, value, where: str):
    if value is None:
        if spec.nullable:
            return None
        raise ConfigError(f"{where}: null is not allowed")
    tag = spec.tag
    if tag in ("float", "int", "str", "bool"):
        out = _cast_scalar(tag, value, where)
        if spec.positive and not out > 0:
            raise ConfigError(f"{where}: must be > 0, got {out!r}")
    elif tag in ("floats", "floats2", "ints"):
        if not isinstance(value, (list, tuple)):
            raise ConfigError(f"{where}: expected a list, got {type(value).__name__}")
        out = [_cast_scalar("int" if tag == "ints" else "float", v, f"{where}[{i}]")
               for i, v in enumerate(value)]
        if tag == "floats2" and (len(out) != 2 or not out[0] < out[1]):
            raise ConfigError(f"{where}: expected [low, high] with low < high, got {value!r}")
    elif tag == "pairs":
        if not isinstance(value, (list, tuple)):
            raise ConfigError(f"{where}: expected a list of [low, high], got {value!r}")
        out = [_cast(Spec("floats2"), v, f"{where}[{i}]") for i, v in enumerate(value)]
    else:
        raise AssertionError(tag)
    if spec.choices is not None and out not in spec.choices:
        raise ConfigError(f"{where}: {out!r} is not one of {list(spec.choices)}")
    return out


# --- loading and merging -----------------------------------------------------

def load_config(path) -> dict:
    """Read a YAML file into a plain dict (no validation)."""
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"{to_posix(path)}: top level must be a mapping")
    return data


def _check_keys(layer: dict, where: str, allow_derived: bool = False) -> None:
    for section, body in layer.items():
        if section not in SCHEMA:
            raise ConfigError(f"{where}: unknown section {section!r}")
        if not isinstance(body, dict):
            raise ConfigError(f"{where}: section {section!r} must be a mapping")
        for key in body:
            spec = SCHEMA[section].get(key)
            if spec is None:
                raise ConfigError(f"{where}: unknown key {section}.{key}")
            if spec.derived and not allow_derived:
                raise ConfigError(f"{where}: {section}.{key} is derived and cannot be set")


def _deep_merge(dst: dict, src: dict) -> dict:
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = copy.deepcopy(v)
    return dst


def parse_override(text: str) -> tuple[str, object]:
    """Split 'section.key=value'; the value is read as YAML, then cast by the schema."""
    if "=" not in text:
        raise ConfigError(f"override {text!r}: expected section.key=value")
    key, raw = text.split("=", 1)
    key = key.strip()
    if key.count(".") != 1:
        raise ConfigError(f"override {text!r}: key must be section.key")
    try:
        value = yaml.safe_load(raw)
    except yaml.YAMLError:
        value = raw
    return key, value


def _overrides_to_layer(overrides) -> tuple[dict, dict]:
    pairs = (overrides.items() if isinstance(overrides, dict)
             else [parse_override(o) for o in (overrides or [])])
    layer: dict = {}
    record: dict = {}
    for key, value in pairs:
        section, name = key.split(".")
        layer.setdefault(section, {})[name] = value
        record[key] = value
    return layer, record


# --- resolution --------------------------------------------------------------

def resolve_config(run_file=None, overrides=(), base_file=None) -> dict:
    """Merge, expand ref_point, derive, validate. Returns a plain dict.

    run_file may be a path or an already-loaded dict. overrides is a list of
    'section.key=value' strings or a dict {'section.key': value}.
    """
    base_path = Path(base_file) if base_file else repo_root() / "configs" / "base.yaml"
    base = load_config(base_path)
    _check_keys(base, to_posix(base_path))

    if run_file is None:
        run_layer, run_name = {}, None
    elif isinstance(run_file, dict):
        run_layer, run_name = copy.deepcopy(run_file), None
    else:
        run_layer, run_name = load_config(run_file), to_posix(run_file)
    _check_keys(run_layer, run_name or "run config")
    ov_layer, ov_record = _overrides_to_layer(overrides)
    _check_keys(ov_layer, "--set")

    user = _deep_merge(copy.deepcopy(run_layer), ov_layer)
    cfg = copy.deepcopy(base)

    ref = user.get("model", {}).get("ref_point", cfg["model"].get("ref_point"))
    if ref is not None:
        ref = _cast(SCHEMA["model"]["ref_point"], ref, "model.ref_point")
        cfg["model"].update(REF_POINTS[ref])        # layer 2: ref_point
    _deep_merge(cfg, user)                          # layers 3, 4: explicit wins

    for section, specs in SCHEMA.items():
        body = cfg.setdefault(section, {})
        for key, spec in specs.items():
            if spec.derived:
                continue
            if key not in body and spec.optional:
                continue
            if key not in body:
                raise ConfigError(f"{section}.{key}: missing (not in base.yaml)")
            body[key] = _cast(spec, body[key], f"{section}.{key}")

    _check_model(cfg)
    _check_path_consistency(cfg)
    _check_forcing_path(cfg)
    _derive_eta_path(cfg)
    cfg[_META_KEY] = {"base": to_posix(base_path), "run_file": run_name,
                      "overrides": ov_record}
    return cfg


def _check_model(cfg: dict) -> None:
    m = cfg["model"]
    if m["type"] == "M3" and m["tau_d_ms"] is None:
        raise ConfigError("model.tau_d_ms: required for M3 (ref_ceni needs an "
                          f"explicit value in {list(TAU_D_MS_RANGE)} ms)")
    if m["ref_point"] == "ref_ceni":  # DL-066 (supersedes the set in DL-054)
        lo, hi = TAU_D_MS_RANGE
        if not lo <= m["tau_d_ms"] <= hi:
            raise ConfigError(f"model.tau_d_ms: ref_ceni needs a value in the D11 range "
                              f"[{lo}, {hi}] ms, got {m['tau_d_ms']!r}")
        if not any(math.isclose(m["tau_d_ms"], v, rel_tol=0, abs_tol=1e-9)
                   for v in REF_CENI_TAU_D_MS):
            warnings.warn(f"model.tau_d_ms = {m['tau_d_ms']!r} ms is outside the S3 set "
                          f"{list(REF_CENI_TAU_D_MS)} (allowed for K10/A6, DL-066)",
                          UserWarning, stacklevel=3)


def _check_path_consistency(cfg: dict) -> None:
    """DL-085 item 3: both keys stay in the hash, so a mismatch would be a new hash for an
    identical run. Reject it instead."""
    p, m, d = cfg["path"], cfg["model"], cfg["durations"]
    if p["name"] in RAMP_PATHS and p["t_on_s"] != d["baseline_s"]:
        raise ConfigError(f"path.t_on_s = {p['t_on_s']!r} differs from durations.baseline_s "
                          f"= {d['baseline_s']!r}; the baseline is path.t_on_s (D27), "
                          "so the two must be equal")
    if p["name"] in J0_PATHS and p["J0"] != m["J"]:
        raise ConfigError(f"path.J0 = {p['J0']!r} differs from model.J = {m['J']!r} on "
                          f"{p['name']}; J starts at path.J0, so the two must be equal")


def _check_forcing_path(cfg: dict) -> None:
    p = cfg["path"]
    if p["name"] == "I_sin" and "I_period_s" not in p:
        raise ConfigError("path.I_period_s: required for path I_sin (the period of I_amp sin(2 pi t / period))")
    if p["name"] != "I_sin" and "I_period_s" in p:
        raise ConfigError(f"path.I_period_s: only used by path I_sin, not {p['name']}")


def _derive_eta_path(cfg: dict) -> None:
    """eta_start, eta_peak, status and eps (D12, DL-065). No value of eta_H is entered."""
    p = cfg["path"]
    have_start, have_peak = p["eta_start"] is not None, p["eta_peak"] is not None
    if have_start != have_peak:
        raise ConfigError("path.eta_start and path.eta_peak must be given together")
    if have_start:
        if p["eta_H"] is not None:
            raise ConfigError("give path.eta_H or explicit eta_start/eta_peak, not both")
        # M2 paths come from A1 (explicit); M3 paths given before A4 are provisional
        p["eta_path_status"] = "explicit" if cfg["model"]["type"] == "M2" else "provisional"
    elif p["eta_H"] is not None:
        p["eta_start"] = p["eta_H"] - ETA_START_OFFSET
        p["eta_peak"] = max(ETA_PEAK_FLOOR, p["eta_H"] + ETA_PEAK_OFFSET)
        p["eta_path_status"] = "A4"
    else:
        p["eta_path_status"] = "unresolved"
    if p["eta_start"] is None:
        p["eps"] = None
    else:
        t_ramp_tau = s_to_tau(p["T_ramp_s"], cfg["model"]["tau_ms"])
        p["eps"] = (p["eta_peak"] - p["eta_start"]) / t_ramp_tau


def require_eta_path(cfg: dict) -> None:
    """Raise if a ramp run has no eta path (A4 not run, no explicit override).

    The forcing paths I_step and I_sin keep eta_bar = model.eta_bar and need none."""
    if cfg["path"]["name"] in FORCING_PATH_NAMES:
        return
    if cfg["path"]["eta_path_status"] == "unresolved":
        raise ConfigError("path.eta_start/eta_peak are unresolved: eta_H comes from A4 "
                          "(MS5); give them explicitly with --set to run provisionally")


# --- hash --------------------------------------------------------------------

def hash_view(cfg: dict) -> dict:
    """The integration inputs that config_hash covers (DL-057)."""
    view = {s: copy.deepcopy(cfg[s]) for s in _HASH_SECTIONS}
    view["run"] = {"kind": cfg["run"]["kind"]}
    view["seeds"] = {"root_seed": cfg["seeds"]["root_seed"],
                     "spawn_key": cfg["seeds"]["spawn_key"]}
    if cfg["run"]["kind"] == "a1":      # constants outside the schema; other kinds are unchanged
        view["a1_grid"] = copy.deepcopy(A1_GRID)
    if cfg["run"]["kind"] == "a2":
        view["a2"] = {"window": copy.deepcopy(A2_WINDOW), "band_primary_hz": list(cfg["analysis"]["band_primary_hz"])}
    return view


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def config_hash(cfg: dict) -> str:
    """Full SHA-256 (hex) of the canonical JSON of hash_view(cfg)."""
    return hashlib.sha256(canonical_json(hash_view(cfg)).encode("utf-8")).hexdigest()


def short_hash(full_hash: str) -> str:
    """First 12 hex characters; names each output (section 6.6)."""
    return full_hash[:12]
