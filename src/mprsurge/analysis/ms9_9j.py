"""MS9 9j: second version of the A9 regime-map table (DL-261 to DL-266). Reads the stored 9i table, writes a new one; nothing is integrated.

Changes against the 9i table (the stored file is never overwritten):
  struct_flags         the stored structural flags a to f (stored column labels_a_f_all), kept for every cell, surge-class or not;
  failure_label        set ONLY for non-surge cells: 'failed' if the run is not ok (A9, 10.4), else the primary of a to f, else the
                       first of the post-hoc descriptors g, h (DL-244) that holds, else '' (unlabelled); empty on surge-class cells;
  failure_labels_all   every label of a to h that applies, non-surge cells only (stored labels_a_h_all, emptied on surge-class cells);
  hopf_f_hz            filled on the 900 map-1 cells and the headline from the A4 Hopf solver (analysis.a9.hopf_point ->
                       hopf.lowest_eta_hopf, the function that filled map 2 and the label (c) rule). The stored A4 files
                       (a4_hopf_curves.npz, a6_freq_map.npz) hold one-dimensional curves only, no per-cell table, so a per-cell value
                       is the A4 solver evaluated at the cell; reading ours, UNVERIFIED. NaN with a reason where there is no Hopf point.
Columns label_a_f_primary and labels_a_h_all of the 9i table are replaced by failure_label and failure_labels_all; labels_a_f_all is
renamed struct_flags.
"""
from __future__ import annotations

import math

import pandas as pd

from . import a9 as A9

NEW_COLUMNS = (
    "map", "cell_id", "i", "j", "J0", "Delta", "tau_d_ms", "T_ramp_s", "eta_H", "hopf_found", "run_id", "status", "class", "surge",
    "onset_s", "f_pk_hz", "inside_a4_region", "time_inside_s", "hopf_f_hz", "label_f", "struct_flags", "failure_label",
    "g", "h", "failure_labels_all", "unlabelled_a_h", "classifier_reason", "headline_marker", "nan_reasons")


def _letters(x) -> list:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return []
    return sorted(ch for ch in str(x) if ch.isalpha())


def _reasons(s) -> dict:
    out = {}
    for part in ("" if s is None or (isinstance(s, float) and math.isnan(s)) else str(s)).split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
    return out


def failure_label(row) -> str:
    """The failure label of one cell: '' for a surge-class cell and for an unlabelled non-surge cell."""
    if bool(row["surge"]):
        return ""
    if row["status"] != "ok":
        return "failed"
    af = _letters(row["labels_a_f_all"])
    prim = str(row["label_a_f_primary"]) if isinstance(row["label_a_f_primary"], str) else ""
    if prim:
        return prim
    if af:
        return af[0]
    for k in ("g", "h"):
        if row[k] is not pd.NA and row[k] is not None and bool(row[k]):
            return k
    return ""


def a9_v2(old: pd.DataFrame, tau_ms: float = 10.0) -> tuple[pd.DataFrame, list]:
    """(new table, notes). notes lists the cells whose Hopf frequency stayed NaN and the map-2 comparison with the stored values."""
    df = old.copy()
    notes = []
    max_dev = 0.0
    n_cmp = 0
    n_fill = 0
    for k, r in df.iterrows():
        hp = A9.hopf_point(float(r["J0"]), float(r["Delta"]), float(r["tau_d_ms"]), tau_ms)
        why = _reasons(r["nan_reasons"])
        if r["map"] == "2":
            if hp is not None and not math.isnan(r["hopf_f_hz"]):
                max_dev = max(max_dev, abs(hp["f_hz"] - float(r["hopf_f_hz"])))
                n_cmp += 1
            continue
        if hp is None:
            why["hopf_f_hz"] = "no_hopf_point"
            notes.append(f"{r['cell_id']}: no A4 Hopf point, hopf_f_hz stays NaN")
        else:
            df.at[k, "hopf_f_hz"] = hp["f_hz"]
            why.pop("hopf_f_hz", None)
            n_fill += 1
        df.at[k, "nan_reasons"] = ";".join(f"{a}={b}" for a, b in why.items())
    notes.append(f"hopf_f_hz filled on {n_fill} map-1 and headline rows; map 2: {n_cmp} stored values re-evaluated, max |difference| {max_dev:.3e} Hz")
    df["struct_flags"] = df["labels_a_f_all"].map(lambda s: ",".join(_letters(s)))
    df["failure_label"] = df.apply(failure_label, axis=1)
    df["failure_labels_all"] = [("" if bool(s) else str(a)) for s, a in zip(df["surge"], df["labels_a_h_all"].fillna(""))]
    df = df[list(NEW_COLUMNS)]
    df["hopf_f_hz"] = df["hopf_f_hz"].astype("float64")
    return df, notes


def flag_counts(df: pd.DataFrame) -> dict:
    """Facts on the structural flags of the surge-class cells, per map: counts per letter, cells with any flag, flags on D-tr cells."""
    out = {}
    for m in ("1", "2", "headline"):
        s = df[(df["map"] == m) & (df["surge"].astype(bool))]
        per = {c: sum(1 for x in s["struct_flags"] if c in _letters(x)) for c in "abcdef"}
        out[m] = {"surge_cells": int(len(s)), "any_flag": int((s["struct_flags"] != "").sum()), "per_letter": per,
                  "by_class": {c: int(((s["class"] == c) & (s["struct_flags"] != "")).sum()) for c in sorted(s["class"].unique())},
                  "combos": s.loc[s["struct_flags"] != "", "struct_flags"].value_counts().to_dict()}
    return out


def failure_facts(df: pd.DataFrame) -> dict:
    ns = df[~df["surge"].astype(bool)]
    return {m: {"non_surge": int((ns["map"] == m).sum()), "labels": ns.loc[ns["map"] == m, "failure_label"].replace("", "(unlabelled)").value_counts().to_dict()}
            for m in ("1", "2", "headline")}
