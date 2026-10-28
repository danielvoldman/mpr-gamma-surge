"""Figure provenance and parameter-table writer (plan 10.4; docs/ms13_plan.md section 7, docs/ms13_conventions.md).

Writes <ID>_params.csv and <ID>_provenance.json into figures/<ID>/ (git-ignored). Reads stored inputs, hashes them, writes nothing under
results/ and imports no simulation or run module. The run-record machinery (git_info, environment_info, sha256_file, atomic writes, the
frozen-criteria loader) is reused, not copied. Every field not named in the plan is UNVERIFIED (docs/ms13_plan.md section 7).
"""
from __future__ import annotations

import csv
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from .. import criteria as K
from .. import provenance as P
from ..config import repo_root

SCHEMA_VERSION = 1                                   # UNVERIFIED (as the run records)
FIGURES = ("F1", "F2", "F3", "F4", "F5", "F6", "FS1", "FS2", "FS3", "FS4", "FS5")
REFUSED = {"FS6": "FS6 is not produced: S14 and S15 were not run (MS12 not run, claim limit MS12-C1, DL-421)"}
PARAMS_COLUMNS = ("figure", "panel", "section", "name", "key", "value", "units", "status",
                  "source_run_id", "source_config_hash12", "varied")
PROVENANCE_FIELDS = (
    "schema_version", "figure_id", "build", "status", "draft", "git", "python", "packages", "julia", "os", "cpu",
    "criteria_sha256", "criteria_tag", "criteria_commit", "script", "modules", "configs", "inputs", "input_tables",
    "seeds", "numerical_settings", "spectrogram", "claim_limits", "outputs", "numba_cache_cleared",
    "created_utc", "wall_time_s", "warnings",
)
INPUT_FIELDS = ("path", "bytes", "sha256")
RECORD_INPUT_FIELDS = ("run_id", "config_hash12", "record_commit", "record_dirty", "seed", "criteria_sha256", "record_status")


class FigureError(RuntimeError):
    """Base class of the errors below."""


class FigureRefused(FigureError):
    """The figure may not be built (FS6)."""


class MissingInputError(FigureError):
    """A listed input file is missing or unreadable; the message names the path."""


class HashMismatchError(FigureError):
    """A stored file differs from the hash recorded for it."""


class DirtyTreeError(FigureError):
    """A tagged build was requested from a dirty tree."""


def dirty_lines(root=None) -> list[str]:
    """Lines of `git status --porcelain` (modified and untracked; results/ and figures/ are git-ignored). Raises if git fails."""
    root = Path(root) if root is not None else repo_root()
    out = K._git(root, "status", "--porcelain")
    if out.returncode != 0:
        raise FigureError(f"git status failed in {root}: {out.stderr.decode(errors='replace').strip()}")
    return [ln for ln in out.stdout.decode("utf-8", errors="replace").splitlines() if ln.strip()]


def require_buildable(figure_id: str) -> None:
    if figure_id in REFUSED:
        raise FigureRefused(REFUSED[figure_id])
    if figure_id not in FIGURES:
        raise FigureError(f"unknown figure id {figure_id!r}; known: {', '.join(FIGURES)}")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def file_record(path, root) -> dict:
    """{path, bytes, sha256} of a stored file; MissingInputError naming the path if it cannot be read."""
    p = Path(path)
    if not p.is_absolute():
        p = Path(root) / p
    if not p.is_file():
        raise MissingInputError(f"input file not found: {p}")
    try:
        return {"path": _rel(p, root), "bytes": p.stat().st_size, "sha256": P.sha256_file(p)}
    except OSError as exc:
        raise MissingInputError(f"input file cannot be read: {p} ({exc})") from exc


def input_record(path, root) -> dict:
    """file_record plus, for a run-record json, the fields of section 7 (run_id = the record's name)."""
    rec = file_record(path, root)
    p = Path(root) / rec["path"] if not Path(rec["path"]).is_absolute() else Path(rec["path"])
    if p.suffix == ".json":
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise MissingInputError(f"input file is not readable json: {p} ({exc})") from exc
        if isinstance(r, dict) and "config_hash12" in r and "seed" in r:
            g = r.get("git") or {}
            rec.update({"run_id": r.get("name"), "config_hash12": r["config_hash12"], "record_commit": g.get("commit"),
                        "record_dirty": g.get("dirty"), "seed": r["seed"], "criteria_sha256": r.get("criteria_sha256"),
                        "record_status": r.get("status")})
    return rec


def _numerical_settings(root, inputs) -> list[dict]:
    out, seen = [], set()
    for rec in inputs:
        if "run_id" not in rec:
            continue
        r = json.loads((Path(root) / rec["path"]).read_text(encoding="utf-8")) if not Path(rec["path"]).is_absolute() \
            else json.loads(Path(rec["path"]).read_text(encoding="utf-8"))
        s = {"solver": r.get("solver"), "network": (r.get("config") or {}).get("network")}
        key = json.dumps(s, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append({"config_hash12": rec["config_hash12"], **s})
    return out


def write_params_csv(path, rows: list[dict], figure_id: str) -> None:
    """<ID>_params.csv (columns PARAMS_COLUMNS). `varied` is computed: true if the value of (panel, key) differs between source runs."""
    require_buildable(figure_id)
    vals: dict = {}
    for r in rows:
        vals.setdefault((r.get("panel", ""), r["key"]), set()).add(json.dumps(r["value"], sort_keys=True, default=str))
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=PARAMS_COLUMNS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        row = {c: r.get(c, "") for c in PARAMS_COLUMNS}
        row["figure"] = figure_id
        row["varied"] = len(vals[(r.get("panel", ""), r["key"])]) > 1
        row["value"] = json.dumps(r["value"], sort_keys=True, default=str)       # JSON text: the round trip is exact
        w.writerow(row)
    P.atomic_write_text(path, buf.getvalue())


def write_figure_provenance(figure_id: str, *, script, inputs, outputs=(), params_rows=(), modules=(), configs=(),
                            claim_limits=(), input_tables=(), spectrogram=None, build: int = 1, tag_build: bool = False,
                            out_dir=None, root=None, warnings=(), wall_time_s=None, status: str = "ok") -> dict:
    """Write figures/<ID>/<ID>_params.csv and <ID>_provenance.json; return the provenance dict.

    inputs: stored files read by the figure (paths relative to `root` or absolute). A missing one raises MissingInputError before
    anything is written. outputs: figure files already written (hashed). tag_build=True refuses a dirty tree; draft = dirty or untagged.
    """
    require_buildable(figure_id)
    root = Path(root) if root is not None else repo_root()
    out_dir = Path(out_dir) if out_dir is not None else root / "figures" / figure_id
    if _rel(out_dir, root).split("/")[0] == "results":
        raise FigureError(f"figures are never written under results/: {out_dir}")
    t0 = time.perf_counter()
    in_recs = [input_record(p, root) for p in inputs]                      # raises on the first missing input, writes nothing
    script_rec = file_record(script, root)
    module_recs = [file_record(m, root) for m in modules]
    config_recs = {c["path"]: c["sha256"] for c in (file_record(c, root) for c in configs)}
    table_recs = [{**file_record(t["path"], root), "rows": t.get("rows")} for t in input_tables]
    out_recs = [file_record(o, root) for o in outputs]
    env = P.environment_info()
    crit = K.verify_frozen_criteria(root)
    dirty = bool(dirty_lines(root))
    if tag_build and dirty:
        raise DirtyTreeError("a tagged build needs a clean tree (git status --porcelain is not empty)")
    out_dir.mkdir(parents=True, exist_ok=True)
    params_path = out_dir / f"{figure_id}_params.csv"
    write_params_csv(params_path, [dict(r) for r in params_rows], figure_id)
    out_recs.append(file_record(params_path, root))
    prov = {
        "schema_version": SCHEMA_VERSION, "figure_id": figure_id, "build": build, "status": status,
        "draft": dirty or not tag_build,
        "git": env["git"], "python": env["python"], "packages": env["packages"], "julia": env["julia"],
        "os": env["os"], "cpu": env["cpu"],
        "criteria_sha256": crit["sha256"], "criteria_tag": crit["tag"], "criteria_commit": crit["commit"],
        "script": script_rec, "modules": module_recs, "configs": config_recs, "inputs": in_recs, "input_tables": table_recs,
        "seeds": {"inputs": [{"run_id": r["run_id"], **r["seed"]} for r in in_recs if "seed" in r],
                  "figure_script": None},                       # the figure script draws no random numbers (expected; UNVERIFIED)
        "numerical_settings": _numerical_settings(root, in_recs), "spectrogram": spectrogram,
        "claim_limits": list(claim_limits), "outputs": out_recs, "numba_cache_cleared": None,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "wall_time_s": wall_time_s if wall_time_s is not None else time.perf_counter() - t0,
        "warnings": [str(w) for w in warnings],
    }
    P.atomic_write_json(out_dir / f"{figure_id}_provenance.json", prov)
    return prov


def verify_figure_provenance(prov_path, root=None) -> list[str]:
    """Re-hash every file recorded in a provenance file; return the list of problems (empty = all equal)."""
    root = Path(root) if root is not None else repo_root()
    prov = json.loads(Path(prov_path).read_text(encoding="utf-8"))
    recs = [prov["script"], *prov["modules"], *prov["inputs"], *prov["input_tables"], *prov["outputs"]]
    bad = []
    for r in recs:
        p = Path(r["path"]) if Path(r["path"]).is_absolute() else root / r["path"]
        if not p.is_file():
            bad.append(f"missing: {p}")
        elif P.sha256_file(p) != r["sha256"]:
            bad.append(f"sha256 differs: {p}")
    return bad


def check_params_against_provenance(params_path, prov_path, root=None) -> list[str]:
    """Every row's source_run_id and config hash12 belong to an input, and `value` equals the record's config value for `key`."""
    root = Path(root) if root is not None else repo_root()
    prov = json.loads(Path(prov_path).read_text(encoding="utf-8"))
    by_run = {r["run_id"]: r for r in prov["inputs"] if "run_id" in r}
    bad = []
    with open(params_path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for i, row in enumerate(rows):
        rec = by_run.get(row["source_run_id"])
        if rec is None:
            bad.append(f"row {i}: source_run_id {row['source_run_id']!r} is not an input")
            continue
        if row["source_config_hash12"] != rec["config_hash12"]:
            bad.append(f"row {i}: config hash12 {row['source_config_hash12']} != {rec['config_hash12']}")
            continue
        p = Path(rec["path"]) if Path(rec["path"]).is_absolute() else root / rec["path"]
        cfg = json.loads(p.read_text(encoding="utf-8"))["config"]
        section, _, name = row["key"].partition(".")
        if json.loads(row["value"]) != cfg.get(section, {}).get(name):
            bad.append(f"row {i}: {row['key']} = {row['value']} != config value {cfg.get(section, {}).get(name)!r}")
    return bad
