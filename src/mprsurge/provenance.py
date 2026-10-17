"""Seeds, run records and atomic writes (plan 6.6, 10.4; DL-056, DL-068)."""
from __future__ import annotations

import functools
import hashlib
import importlib.metadata as md
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .config import config_hash, repo_root, short_hash, to_posix

SCHEMA_VERSION = 1
STATUSES = ("ok", "failed", "timeout")   # section 10.4
DRY_STATUS = "dry_run"                   # DL-056
PACKAGES = ("numpy", "scipy", "numba", "pandas", "pyarrow", "pyyaml", "matplotlib", "pytest")

# Fields every record carries (sections 6.6 and 10.4); test_provenance checks them.
RECORD_FIELDS = (
    "schema_version", "status", "message", "dry_run", "name", "config", "config_hash",
    "config_hash12", "seed", "git", "python", "packages", "julia", "os", "cpu", "solver",
    "wall_time_s", "warnings", "flags", "inputs", "outputs", "criteria_sha256",
    "numba_cache_cleared", "created_utc",
)


class ProvenanceError(RuntimeError):
    """Inconsistent stored record (for example a hash12 collision)."""


# --- seeds -------------------------------------------------------------------

def seed_sequence(root_seed: int, n: int) -> list[np.random.SeedSequence]:
    """Children of SeedSequence(root_seed).spawn(n); child k has spawn_key (k,)."""
    return np.random.SeedSequence(root_seed).spawn(n)


def seed_from_key(root_seed: int, spawn_key) -> np.random.SeedSequence:
    """Rebuild the child with the stored spawn key (equal to spawn(n)[k] for key (k,))."""
    return np.random.SeedSequence(root_seed, spawn_key=tuple(spawn_key))


# --- hashing and atomic writes ---------------------------------------------------

def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_bytes(path, data: bytes, attempts: int = 8, delay_s: float = 0.05) -> None:
    """Write to <name>.<pid>.tmp, then os.replace; retry on PermissionError (Windows locks)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    try:
        for k in range(attempts):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                if k == attempts - 1:
                    raise
                time.sleep(delay_s * 2 ** k)
    finally:
        if tmp.exists():
            tmp.unlink()


def atomic_write_text(path, text: str, **kw) -> None:
    atomic_write_bytes(path, text.encode("utf-8"), **kw)


def atomic_write_json(path, obj, **kw) -> None:
    atomic_write_text(path, json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n", **kw)


def atomic_save_npz(path, arrays: dict, **kw) -> None:
    buf = io.BytesIO()
    np.savez_compressed(buf, **arrays)
    atomic_write_bytes(path, buf.getvalue(), **kw)


# --- environment ---------------------------------------------------------------------

def _git(*args) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=repo_root(), capture_output=True,
                             text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def git_info() -> dict:
    """Commit, branch, tags at HEAD and a dirty flag (section 10.4)."""
    status = _git("status", "--porcelain")
    tags = _git("tag", "--points-at", "HEAD")
    return {"commit": _git("rev-parse", "HEAD"),
            "branch": _git("branch", "--show-current"),
            "tags": tags.split() if tags else [],
            "dirty": None if status is None else bool(status)}


@functools.lru_cache(maxsize=1)
def _julia_version() -> str | None:
    exe = shutil.which("julia")
    if exe is None:
        return None
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None


def _bifurcationkit_version() -> str | None:
    from .analysis.continuation.julia_io import pinned_bifurcationkit_version
    return pinned_bifurcationkit_version()


def environment_info(with_julia: bool = True) -> dict:
    """Versions and machine, computed once in the parent and passed to workers.

    bifurcationkit is the version pinned in environment/julia/Manifest.toml (null if absent).
    """
    pk = {}
    for name in PACKAGES:
        try:
            pk[name] = md.version(name)
        except md.PackageNotFoundError:
            pk[name] = None
    return {"git": git_info(),
            "python": {"version": platform.python_version(), "executable": sys.executable},
            "packages": pk,
            "julia": {"version": _julia_version() if with_julia else None,
                      "bifurcationkit": _bifurcationkit_version()},
            "os": platform.platform(),
            "cpu": {"processor": platform.processor(), "machine": platform.machine(),
                    "count": os.cpu_count()}}


# --- records -----------------------------------------------------------------------------

def make_run_record(cfg: dict, env: dict, *, name: str, status: str, message: str = "",
                    wall_time_s: float | None = None, warnings=(), flags: dict | None = None,
                    inputs: dict | None = None, outputs: dict | None = None,
                    dry_run: bool = False, numba_cache_cleared: bool | None = None) -> dict:
    """Run record (sections 6.6, 10.4). Hashes of inputs and outputs are SHA-256 hex."""
    allowed = (DRY_STATUS,) if dry_run else STATUSES
    if status not in allowed:
        raise ValueError(f"status {status!r} not in {allowed}")
    full = config_hash(cfg)
    crit = cfg["robustness"]["criteria_file"]
    crit_sha = None
    if crit is not None:
        p = Path(crit) if Path(crit).is_absolute() else repo_root() / crit
        from .criteria import is_frozen_criteria_path, lf_sha256     # late import: criteria imports config
        if p.exists():     # the frozen file is hashed as LF text (DL-084, DL-164); the other criteria files as bytes
            crit_sha = lf_sha256(p.read_bytes()) if is_frozen_criteria_path(crit) else sha256_file(p)
    return {
        "schema_version": SCHEMA_VERSION, "status": status, "message": message,
        "dry_run": dry_run, "name": name, "config": cfg, "config_hash": full,
        "config_hash12": short_hash(full),
        "seed": {"root_seed": cfg["seeds"]["root_seed"], "spawn_key": cfg["seeds"]["spawn_key"]},
        "git": env["git"], "python": env["python"], "packages": env["packages"],
        "julia": env["julia"], "os": env["os"], "cpu": env["cpu"],
        "solver": {**cfg["solver"], "noise": dict(cfg["noise"])},
        "wall_time_s": wall_time_s, "warnings": [str(w) for w in warnings],
        "flags": dict(flags or {}), "inputs": dict(inputs or {}), "outputs": dict(outputs or {}),
        "criteria_sha256": crit_sha,
        "numba_cache_cleared": numba_cache_cleared,   # null until make_all.ps1 sets it (section 10.4)
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def write_run_record(record: dict, path) -> None:
    atomic_write_json(path, record)


def read_run_record(path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def find_complete(out_dir, cfg: dict) -> Path | None:
    """Record path if this config already has a complete result, else None.

    Keyed by hash12 (any '<name>_<hash12>.json'); the full SHA-256 in the record is
    compared on reuse (section 10.3). Complete = status ok, same full hash, and every
    recorded output present with its recorded SHA-256. failed, timeout and dry-run
    records are not complete (DL-056, DL-068).
    """
    out_dir = Path(out_dir)
    full = config_hash(cfg)
    for rec_path in sorted(out_dir.glob(f"*_{short_hash(full)}.json")):
        rec = read_run_record(rec_path)
        if rec.get("config_hash") != full:
            raise ProvenanceError(f"{to_posix(rec_path)}: hash12 matches but the full "
                                  "SHA-256 differs")
        if rec.get("status") != "ok":
            continue
        outs = rec.get("outputs", {})
        if outs and all((out_dir / n).is_file() and sha256_file(out_dir / n) == h
                        for n, h in outs.items()):
            return rec_path
    return None
