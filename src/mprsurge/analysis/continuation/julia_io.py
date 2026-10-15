"""Read and validate the CSV + JSON that the Julia continuation scripts write (plan 9.1, DL-063).

Validation only: shapes, required fields, finite numbers, and the Manifest SHA-256 against the
committed environment/julia/Manifest.toml. No Julia is needed.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from ...config import repo_root
from ...provenance import sha256_file

JSON_FIELDS = ("commit", "dirty", "julia_version", "bifurcationkit_version", "manifest_sha256",
               "periodic_orbit_method", "equations", "hopf_td_over_tau", "hopf_tau_d_ms",
               "hopf_type", "timings_s", "written_utc")
BRANCH_COLUMNS = ("td_over_tau", "tau_d_ms", "r", "v", "s", "stable")
PO_COLUMNS = ("td_over_tau", "tau_d_ms", "vmax", "vmin", "amplitude_v", "period_tau", "frequency_hz")


class JuliaOutputError(ValueError):
    """The Julia output is missing, malformed or inconsistent with the pinned environment."""


def manifest_path() -> Path:
    return repo_root() / "environment" / "julia" / "Manifest.toml"


def _table(path, columns) -> pd.DataFrame:
    df = pd.read_csv(path)
    if tuple(df.columns) != tuple(columns):
        raise JuliaOutputError(f"{path}: columns {tuple(df.columns)}, expected {tuple(columns)}")
    if df.empty:
        raise JuliaOutputError(f"{path}: no rows")
    if not np.isfinite(df.to_numpy(dtype=float)).all():
        raise JuliaOutputError(f"{path}: non-finite values")
    return df


def load_smoke(outdir, check_manifest: bool = True) -> dict:
    """Load smoke.json, smoke_branch.csv and smoke_po.csv from `outdir`; raise JuliaOutputError."""
    outdir = Path(outdir)
    try:
        rec = json.loads((outdir / "smoke.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise JuliaOutputError(f"{outdir / 'smoke.json'}: {exc}") from exc
    missing = [k for k in JSON_FIELDS if k not in rec]
    if missing:
        raise JuliaOutputError(f"smoke.json: missing fields {missing}")
    for k in ("hopf_td_over_tau", "hopf_tau_d_ms"):
        if not (isinstance(rec[k], (int, float)) and math.isfinite(rec[k])):
            raise JuliaOutputError(f"smoke.json: {k} is not a finite number")
    sha = rec["manifest_sha256"]
    if not (isinstance(sha, str) and len(sha) == 64 and all(c in "0123456789abcdef" for c in sha)):
        raise JuliaOutputError("smoke.json: manifest_sha256 is not a SHA-256 hex digest")
    if check_manifest and sha != sha256_file(manifest_path()):
        raise JuliaOutputError("smoke.json: manifest_sha256 differs from environment/julia/Manifest.toml")
    return {"record": rec,
            "branch": _table(outdir / "smoke_branch.csv", BRANCH_COLUMNS),
            "po": _table(outdir / "smoke_po.csv", PO_COLUMNS)}


def pinned_bifurcationkit_version() -> str | None:
    """BifurcationKit version in the committed Manifest.toml, or None if absent."""
    import tomllib
    try:
        with open(manifest_path(), "rb") as fh:
            entries = tomllib.load(fh).get("deps", {}).get("BifurcationKit", [])
    except (OSError, tomllib.TOMLDecodeError):
        return None
    return entries[0].get("version") if entries else None
