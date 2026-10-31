"""MS13 13t journal export: settings, rc parameters, saving, the supplement sheet, the source-data table (DL-545 J4, J5, J14; DL-546).

Every setting is read from configs/journal_export.yaml (UNVERIFIED; no journal requirement is claimed). The drawing code of the figures is in figures.py (mode="journal"); this
module holds what is shared: the config, the matplotlib settings (font, sizes, embedded fonts), the final text and line-width guard, the output writers (PDF, PNG, TIFF, EPS)
and the supplement and source-data writers. It reads no results and simulates nothing.
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
import warnings
from pathlib import Path

import yaml

from ..config import repo_root

CONFIG = "configs/journal_export.yaml"
SOURCE_COLUMNS = ("panel", "series", "x", "y", "value")


class JournalError(RuntimeError):
    """A journal-export setting or output is not valid."""


def config_path(root=None) -> Path:
    return Path(root) if root is not None else repo_root()


def load_config(root=None) -> dict:
    p = config_path(root) / CONFIG
    cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
    cfg["_sha256"] = hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    return cfg


def font_choice(cfg: dict) -> tuple[str, bool]:
    """(family, is_fallback): the first preferred font that is installed, else the fallback (and True, so the provenance says so)."""
    from matplotlib import font_manager as fm
    for fam in cfg["text"]["font_preferred"]:
        try:
            fm.findfont(fam, fallback_to_default=False)
            return fam, False
        except ValueError:
            continue
    return cfg["text"]["font_fallback"], True


def rc_params(cfg: dict) -> dict:
    fam, _ = font_choice(cfg)
    pt = cfg["text"]["min_pt"]
    return {"font.family": fam, "font.size": pt, "axes.labelsize": pt, "axes.titlesize": cfg["text"]["title_pt"], "xtick.labelsize": pt, "ytick.labelsize": pt, "legend.fontsize": pt,
            "pdf.fonttype": cfg["text"]["pdf_fonttype"], "ps.fonttype": cfg["text"]["ps_fonttype"], "mathtext.fontset": "custom", "mathtext.rm": fam, "mathtext.it": f"{fam}:italic",
            "mathtext.bf": f"{fam}:bold", "mathtext.default": "it", "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 3.0,
            "ytick.major.size": 3.0, "figure.dpi": cfg["output"]["dpi"], "savefig.dpi": cfg["output"]["dpi"], "savefig.facecolor": "white", "figure.facecolor": "white"}


def page_size(cfg: dict, height_in: float, width: str = "double") -> tuple[float, float]:
    """(width, height) in inches; the height is checked against the page maximum."""
    w = cfg["page"]["double_column_width_in"] if width == "double" else cfg["page"]["single_column_width_mm"] / 25.4
    if height_in > cfg["page"]["max_height_in"] + 1e-9:
        raise JournalError(f"figure height {height_in} in is above the page maximum {cfg['page']['max_height_in']} in")
    return float(w), float(height_in)


def finish(fig, cfg: dict) -> dict:
    """The final guard on the figure object: no text below the minimum size, no line thinner than the minimum width. Returns what it changed (a count, for the provenance)."""
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.text import Text
    pt, lw = cfg["text"]["min_pt"], cfg["lines"]["min_width_pt"]
    n_text = n_line = 0
    for t in fig.findobj(Text):
        if t.get_text() and t.get_fontsize() < pt:
            t.set_fontsize(pt)
            n_text += 1
    for ln in fig.findobj(Line2D):
        if ln.get_linestyle() not in ("None", "none", "", " ") and 0 < ln.get_linewidth() < lw:
            ln.set_linewidth(lw)
            n_line += 1
    for p in fig.findobj(Patch):
        if p.get_edgecolor()[3] > 0 and 0 < p.get_linewidth() < lw:
            p.set_linewidth(lw)
            n_line += 1
    for ax in fig.axes:
        for sp in ax.spines.values():
            if sp.get_visible() and 0 < sp.get_linewidth() < lw:
                sp.set_linewidth(lw)
                n_line += 1
    w, h = fig.get_size_inches()
    if w > cfg["page"]["double_column_width_in"] + 1e-9 or h > cfg["page"]["max_height_in"] + 1e-9:
        raise JournalError(f"figure size {w:.3f} x {h:.3f} in is above the page size of the config")
    return {"text_raised": n_text, "lines_thickened": n_line}


def uses_transparency(fig) -> bool:
    """True if any artist is drawn with alpha below 1 (the EPS format does not carry it)."""
    from matplotlib.artist import Artist
    for a in fig.findobj(Artist):
        al = a.get_alpha()
        if al is not None and al < 1.0 and a.get_visible():
            return True
    return False


def valid_name(name: str, cfg: dict) -> bool:
    return re.match(cfg["files"]["name_pattern"], name) is not None


def save_all(fig, out_dir, stem: str, cfg: dict) -> dict:
    """Write <stem>.pdf, <stem>.png (and <stem>.tiff, <stem>.eps if they build cleanly) into out_dir; returns {'paths': {...}, 'notes': [...]} (the notes say what was skipped and why)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if not valid_name(stem + ".pdf", cfg):
        raise JournalError(f"file name {stem!r} has characters outside the allowed set")
    paths, notes = {}, []
    dpi = cfg["output"]["dpi"]
    pdf, png = out / f"{stem}.pdf", out / f"{stem}.png"
    fig.savefig(pdf, format="pdf", dpi=dpi, metadata={"CreationDate": None})
    fig.savefig(png, format="png", dpi=dpi)
    paths["pdf"], paths["png"] = pdf, png
    if cfg["output"].get("tiff"):
        try:
            from PIL import Image
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=cfg["output"]["tiff_dpi"])
            buf.seek(0)
            im = Image.open(buf).convert("RGB")                           # flattened onto the white figure face, no alpha
            tif = out / f"{stem}.tiff"
            im.save(tif, compression="tiff_lzw", dpi=(cfg["output"]["tiff_dpi"],) * 2)
            paths["tiff"] = tif
        except Exception as exc:                                          # reported, not hidden
            notes.append(f"TIFF not written: {type(exc).__name__}: {exc}")
    if cfg["output"].get("eps"):
        if uses_transparency(fig):
            notes.append("EPS not written: the figure uses transparency (alpha below 1), which EPS does not carry, so the EPS would differ from the PDF")
        else:
            eps = out / f"{stem}.eps"
            try:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    fig.savefig(eps, format="eps", dpi=dpi)
                if w:
                    eps.unlink(missing_ok=True)
                    notes.append("EPS not written: " + "; ".join(str(x.message) for x in w))
                else:
                    paths["eps"] = eps
            except Exception as exc:
                eps.unlink(missing_ok=True)
                notes.append(f"EPS not written: {type(exc).__name__}: {exc}")
    return {"paths": paths, "notes": notes}


def write_csv(path, header, rows) -> None:
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    Path(path).write_text(buf.getvalue(), encoding="utf-8", newline="")


def num(x) -> str:
    """One number text for the source-data tables: shortest round-trip repr of a float, an integer as an integer."""
    if x is None:
        return ""
    if isinstance(x, (bool,)):
        return str(x)
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return str(x)
    if xf != xf:
        return "nan"
    return repr(xf) if not float(xf).is_integer() or abs(xf) >= 1e15 else str(int(xf))


def write_supplement(path, fig_id: str, *, strip_rows, strip_heading: str, footer: str, provenance_text: str, pointers, parameter_table: str, extra=()) -> None:
    """<ID>_supplement.md: the status-strip rows (value, threshold, status, DL numbers), the footer and the provenance text of the draft, the G10 pointers, the parameter table (J5)."""
    lines = [f"# {fig_id} supplement sheet (journal export; draft = true)", "",
             "This sheet holds what the journal figure does not draw: the status strip, the footer and provenance text of the draft, the claim-limit pointers and the parameter table. "
             "Nothing here is a new result.", "", "## Status strip", "", strip_heading, "",
             "| check | value | threshold | status | decision-log entries |", "|---|---|---|---|---|"]
    for r in strip_rows:
        lines.append("| {check} | {value} | {threshold} | {status} | {dl} |".format(**{k: str(v).replace("|", "/") for k, v in r.items()}))
    lines += ["", "## Footer of the draft (moved off the image)", "", footer, "", "## Provenance text", "", provenance_text, "", "## Claim-limit pointers moved off the image", ""]
    lines += [f"- {p}" for p in pointers] or ["- none"]
    for title, body in extra:
        lines += ["", f"## {title}", "", body]
    lines += ["", "## Parameter table (Nordlie style)", "", parameter_table.rstrip(), ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8", newline="")


def write_export_manifest(base) -> Path:
    """figures/journal/export_manifest.csv: every export file under `base` (relative path, size in bytes, size in KB), sorted; the manifest itself is not listed (J14)."""
    base = Path(base)
    rows = []
    for p in sorted(base.rglob("*")):
        if p.is_file() and p.name != "export_manifest.csv":
            rows.append((p.relative_to(base).as_posix(), p.stat().st_size, f"{p.stat().st_size / 1024.0:.1f}"))
    out = base / "export_manifest.csv"
    write_csv(out, ("file", "bytes", "kilobytes"), rows)
    return out
