"""Nordlie parameter table, two stages (MS13 13c; docs/ms13_conventions.md section 6, M13-6).

Stage 1 is <ID>_params.csv written by figprov (rows from make_param_table of the input records). Stage 2 (this module) renders the Nordlie
sectioning from that file and links it to the provenance file by run ID and config hash: every row's source_run_id and source_config_hash12 must
belong to an input of the provenance file and its value must equal the record's config value (figprov.check_params_against_provenance); otherwise
NordlieError. The rendering carries every params.csv row, and parse_nordlie reads it back.

The section names and the mapping from config sections to them are ours and UNVERIFIED (the plan names no Nordlie sectioning beyond "a parameter
table"; the section list follows Nordlie-style model descriptions as a layout choice, not a quoted standard). A key whose config section is not in
the mapping goes to UNASSIGNED_SECTION; a section already set in the csv is kept.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from .. import provenance as P
from ..config import repo_root
from . import figprov as F

UNASSIGNED_SECTION = "UNASSIGNED (mapping UNVERIFIED)"
NUMERICS_SECTION = "Numerics and bookkeeping (not a Nordlie section)"
SECTION_ORDER = ("Populations", "Connectivity", "Neuron model", "Input", "Measurement", NUMERICS_SECTION, UNASSIGNED_SECTION)
SECTION_BY_CONFIG = {                                           # UNVERIFIED: ours
    "network": "Populations",
    "model": "Neuron model",
    "path": "Input", "noise": "Input",
    "analysis": "Measurement", "durations": "Measurement",
    "solver": NUMERICS_SECTION, "seeds": NUMERICS_SECTION, "budget": NUMERICS_SECTION, "run": NUMERICS_SECTION, "output": NUMERICS_SECTION,
    "sweep": NUMERICS_SECTION, "robustness": NUMERICS_SECTION, "replication": NUMERICS_SECTION, "s4": NUMERICS_SECTION,
}
SECTION_BY_KEY = {"model.J": "Connectivity"}                        # UNVERIFIED: ours; the coupling J is a connectivity parameter (presentation fix, DL below 437)
ROW_COLUMNS = tuple(c for c in F.PARAMS_COLUMNS if c not in ("figure", "section"))      # the section is the heading, the figure is in the header


class NordlieError(RuntimeError):
    """The params file does not agree with the provenance file, or a rendered table cannot be read back."""


def read_params_csv(path) -> list[dict]:
    """Stage 1: the rows of <ID>_params.csv as dicts of strings (all F.PARAMS_COLUMNS)."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if rows and tuple(rows[0]) != F.PARAMS_COLUMNS:
        raise NordlieError(f"{path}: columns {tuple(rows[0])} are not {F.PARAMS_COLUMNS}")
    return rows


def section_of(row: dict) -> str:
    if row.get("section"):
        return row["section"]
    if row["key"] in SECTION_BY_KEY:
        return SECTION_BY_KEY[row["key"]]
    return SECTION_BY_CONFIG.get(row["key"].partition(".")[0], UNASSIGNED_SECTION)


def _esc(cell: str) -> str:
    if "\n" in cell or "\r" in cell:
        raise NordlieError(f"cell with a line break cannot be rendered: {cell!r}")
    return cell.replace("\\", "\\\\").replace("|", "\\|")


def _split(line: str) -> list[str]:
    cells, cur, i = [], [], 0
    line = line.rstrip("\r\n")
    if not (line.startswith("|") and line.endswith("|")):
        raise NordlieError(f"not a table line: {line!r}")
    body = line[1:-1]
    while i < len(body):
        c = body[i]
        if c == "\\" and i + 1 < len(body):
            cur.append(body[i + 1])
            i += 2
            continue
        if c == "|":
            cells.append("".join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1
    cells.append("".join(cur))
    return [c[1:-1] if len(c) >= 2 and c[0] == " " and c[-1] == " " else c for c in cells]      # exactly one space of padding each side


def render_nordlie(params_path, prov_path, root=None) -> str:
    """Stage 2: Markdown with a provenance header and one table per Nordlie section; raises NordlieError if params and provenance disagree."""
    root = Path(root) if root is not None else repo_root()
    problems = F.check_params_against_provenance(params_path, prov_path, root)
    if problems:
        raise NordlieError("params.csv does not agree with the provenance file: " + "; ".join(problems))
    rows = read_params_csv(params_path)
    prov = json.loads(Path(prov_path).read_text(encoding="utf-8"))
    runs = sorted({(r["source_run_id"], r["source_config_hash12"]) for r in rows})
    lines = [f"# Parameter table {prov['figure_id']} (Nordlie sectioning, mapping {'UNVERIFIED'})", "",
             f"- figure: {prov['figure_id']}; build {prov['build']}; draft {prov['draft']}",
             f"- criteria SHA-256: {prov['criteria_sha256']}",
             f"- provenance file SHA-256: {P.sha256_file(prov_path)}",
             f"- params file SHA-256: {P.sha256_file(params_path)}",
             f"- source runs (run ID, config hash12): " + "; ".join(f"{a} {b}" for a, b in runs), ""]
    by_sec: dict[str, list[dict]] = {}
    for r in rows:
        by_sec.setdefault(section_of(r), []).append(r)
    order = [s for s in SECTION_ORDER if s in by_sec] + sorted(s for s in by_sec if s not in SECTION_ORDER)
    for sec in order:
        lines += [f"## {sec}", "", "| " + " | ".join(ROW_COLUMNS) + " |", "|" + " --- |" * len(ROW_COLUMNS)]
        lines += ["| " + " | ".join(_esc(r[c]) for c in ROW_COLUMNS) + " |" for r in by_sec[sec]]
        lines.append("")
    return "\n".join(lines) + "\n"


def parse_nordlie(text: str) -> list[dict]:
    """Read the rendered tables back into rows with all F.PARAMS_COLUMNS (figure from the header, section from the heading)."""
    fig, sec, rows, header = None, None, [], False
    for line in text.splitlines():
        if line.startswith("- figure: "):
            fig = line[len("- figure: "):].split(";")[0]
        elif line.startswith("## "):
            sec, header = line[3:], False
        elif sec is not None and line.startswith("|"):
            cells = _split(line)
            if not header:
                if tuple(cells) != ROW_COLUMNS:
                    raise NordlieError(f"unexpected table header {cells}")
                header = True
            elif line.startswith("|" + " --- |"):
                continue
            else:
                rows.append({"figure": fig, "section": sec, **dict(zip(ROW_COLUMNS, cells))})
    return rows


def write_nordlie(params_path, prov_path, out_path, root=None) -> str:
    text = render_nordlie(params_path, prov_path, root)
    P.atomic_write_text(out_path, text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
