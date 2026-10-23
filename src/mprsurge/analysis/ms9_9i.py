"""MS9 9i: data files for A7 (S6 part), A9 and A10 and the G3 facts table, from stored records and stored class tables (DL-256 to DL-260).

Analysis only: nothing is integrated, nothing is judged. Frozen inputs (threshold, A4 grid step) come from analysis.a7.frozen_inputs
(criteria gate first). The S6 rows reuse the MS8 A7 pieces unchanged (a7.classify_run, a7.frozen_inputs, surge_metrics.onset_delay,
entry_exit.node_times); there is no entry-exit prediction for S6 (RB3(a) is judged on S5, 9i prompt).

Readings, UNVERIFIED where marked:
  eta_H            : the nominal eta_H of the run's path block (M9-19), the same value on every S6 run.
  J_exit,run       : J at the classifier episode end (surge_metrics.j_exit_metrics) when the episode terminated before the record end.
  J_exit,static    : J at the last positive-to-non-positive crossing of the leading Re lambda along the run's own path (the S5 reading of
                     DL-209, UNVERIFIED), extended here to P3 and P4: the fixed point is taken at eta + I(t) and Delta(t) of the path
                     (fixed_points takes I; ramps.Path carries I(t) and Delta(t)); the extension is ours, UNVERIFIED.
  post-surge rate  : mean r over [end, end + w) for w = 1 s and 5 s, both columns, none chosen (O12 ruling, DL-207); NaN when the window
                     passes the record end.
  exit delay       : J_exit,run - J_exit,static (the sign is not stated in the plan, UNVERIFIED).
Every NaN in a numeric column has a reason code in nan_reasons ("column=reason;...").
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq

from .. import config as C
from ..models.fixed_points import fixed_points
from ..models.mpr3d import jacobian_3d
from ..units import tau_to_s
from . import a7 as A7
from . import entry_exit as EE
from . import ms9_classify as MCL
from . import surge_metrics as M

J0_TOL = 1e-9
WINDOWS_S = (1.0, 5.0)
PATH_LABEL = {"path_hypoxia": "P2", "path_drive": "P3", "path_delta_up": "P4a", "path_delta_down": "P4b"}
DIRECTION = {"path_delta_up": "up", "path_delta_down": "down"}
G7_STATUS = "not passed (network S+)"
DET_CLASSES = ("D-tr", "D-sus", "D-none")
N_CLASSES = ("S+", "S-rel", "S-abs", "S-sus", "NS")
SURGE_CLASSES = ("D-tr", "S+", "S-rel", "S-abs")
SUS_CLASSES = ("D-sus", "S-sus")


class NineIError(RuntimeError):
    pass


def root_of(root=None) -> Path:
    return Path(root) if root is not None else C.repo_root()


def read_csv(rel, root=None, **kw) -> pd.DataFrame:
    return pd.read_csv(root_of(root) / rel, **kw)


def nan_reason_columns(df: pd.DataFrame, columns, reasons_col="nan_reasons") -> list:
    """(row index, column) pairs whose value is missing and not named in the row's reason string."""
    bad = []
    for c in columns:
        for i in df.index[df[c].isna()]:
            if f"{c}=" not in df.at[i, reasons_col]:
                bad.append((i, c))
    return bad


# ---- A7, S6 part -------------------------------------------------------------------------------------------------
def lead_re_full(eta, J, Delta, I, tau_d_tau):
    """Max Re of the eigenvalues at the (smallest-r) positive fixed point at eta + I, J, Delta (M3). ValueError when there is none."""
    fp = fixed_points(eta, J, Delta, I=I, model="M3")
    if len(fp) == 0:
        raise ValueError("no positive fixed point")
    return float(np.linalg.eigvals(jacobian_3d(fp[0], J, tau_d_tau)).real.max())


def j_exit_static_path(cfg: dict, h: float):
    """(J of the last positive-to-non-positive crossing of the leading Re lambda along the run's own path or None, reason or '').

    Nodes: entry_exit.node_times (A4 grid levels in eta, path corners, equally spaced nodes in the J tail), refined by bisection in t."""
    from .. import ramps
    path = ramps.make_path(cfg)
    m = cfg["model"]
    td = m["tau_d_ms"] / m["tau_ms"]
    t = EE.node_times(cfg, path, h)
    try:
        re = np.array([lead_re_full(float(path.eta(x)), float(path.J(x)), float(path.Delta(x)), float(path.I(x)), td) for x in t])
    except ValueError:
        return None, "no_positive_fixed_point_on_path"
    idx = [k for k in range(len(re) - 1) if re[k] > 0.0 >= re[k + 1]]
    if not idx:
        return None, "no_positive_to_nonpositive_crossing_of_leading_re_lambda"
    k = idx[-1]
    f = lambda x: lead_re_full(float(path.eta(x)), float(path.J(x)), float(path.Delta(x)), float(path.I(x)), td)
    ts = brentq(f, t[k], t[k + 1], xtol=1e-9)
    return float(path.J(ts)), ""


S6_COLUMNS = (
    "run_id", "row_kind", "supplementary", "list", "family", "record_path", "config_hash12", "git_commit", "criteria_sha256",
    "path", "path_name", "profile", "I_amp", "Delta_factor", "direction", "T_ramp_s", "class", "class_reason", "provisional",
    "terminated", "t_on_s", "onset_s", "eta_onset", "eta_H_nominal", "delay_eta", "end_s", "duration_s", "duration_cycles",
    "duration_frac_ramp", "peak_power_abs", "peak_power_rel", "f_pk_hz", "J0", "J_exit_run", "J_exit_static", "exit_delay",
    "flag_J_exit_run_at_J0", "r0", "r_post_1s", "r_post_5s", "nan_reasons")
S6_NUMERIC = ("I_amp", "Delta_factor", "T_ramp_s", "t_on_s", "onset_s", "eta_onset", "eta_H_nominal", "delay_eta", "end_s", "duration_s",
              "duration_cycles", "duration_frac_ramp", "peak_power_abs", "peak_power_rel", "f_pk_hz", "J0", "J_exit_run", "J_exit_static",
              "exit_delay", "r0", "r_post_1s", "r_post_5s")
S6_BOOL = ("supplementary", "terminated", "flag_J_exit_run_at_J0")


def s6_row(json_path, fi: dict, row_kind: str, list_name: str, root=None, static_cache: dict | None = None) -> dict:
    """The A7 (S6 part) row of one stored mode-D record; no entry-exit prediction."""
    root = root_of(root)
    jp = Path(json_path)
    rec = json.loads(jp.read_text(encoding="utf-8"))
    cfg = rec["config"]
    if cfg["run"]["kind"] != "mf":
        raise NineIError(f"{jp.name}: S6 and its P2 comparators are mode D (kind mf), found {cfg['run']['kind']}")
    with np.load(jp.with_suffix(".npz")) as z:
        t_s = z["t_ms"] / 1000.0
        arr = {k: z[k] for k in ("r", "v", "eta", "J")}
    fs = 1000.0 / cfg["solver"]["dt_out_ms"]
    p = cfg["path"]
    why: dict[str, str] = {}
    try:
        rel = jp.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rel = jp.as_posix()
    row: dict = {
        "run_id": jp.stem, "row_kind": row_kind, "supplementary": row_kind == "S6_supplementary", "list": list_name,
        "family": jp.parent.name, "record_path": rel, "config_hash12": rec["config_hash12"], "git_commit": rec["git"]["commit"],
        "criteria_sha256": rec["criteria_sha256"], "path": PATH_LABEL[p["name"]], "path_name": p["name"], "profile": p["profile"],
        "T_ramp_s": float(p["T_ramp_s"]), "t_on_s": float(p["t_on_s"]), "eta_H_nominal": float(p["eta_H"]), "J0": float(p["J0"]),
        "direction": DIRECTION.get(p["name"], ""),
    }

    def put(col, value, reason):
        if value is None or (isinstance(value, float) and math.isnan(value)):
            row[col] = float("nan")
            why[col] = reason
        else:
            row[col] = value

    put("I_amp", float(p["I_amp"]) if p["name"] == "path_drive" else None, "not_applicable_not_P3")
    put("Delta_factor", float(p["Delta_factor"]) if p["name"] in DIRECTION else None, "not_applicable_not_P4")

    res, err = A7.classify_run(cfg, arr["v"], fs, fi["threshold"])
    ep = None if res is None else res.episode
    no_ep = "classifier_error" if res is None else "no_episode"
    row["class"] = "not_run" if res is None else res.cls
    row["class_reason"] = err if res is None else (res.reason or "")
    row["provisional"] = "" if res is None else (res.provisional or "")
    row["terminated"] = None if ep is None else bool(ep.terminated)
    if ep is None:
        why["terminated"] = no_ep
    onset = None if ep is None else ep.onset_s
    put("onset_s", onset, no_ep)
    if onset is not None:
        eta_on, delay = M.onset_delay(onset, t_s, arr["eta"], p["eta_H"])
    else:
        eta_on = delay = None
    put("eta_onset", eta_on, no_ep)
    put("delay_eta", delay, no_ep)
    put("end_s", None if ep is None else ep.end_s, no_ep)
    put("duration_s", None if ep is None else ep.duration_s, no_ep)
    put("duration_cycles", None if ep is None else ep.cycles, no_ep)
    put("duration_frac_ramp", None if ep is None else ep.duration_s / p["T_ramp_s"], no_ep)
    put("peak_power_abs", None if ep is None else ep.peak_p_g, no_ep)
    put("peak_power_rel", None if ep is None else ep.peak_rho, no_ep)
    put("f_pk_hz", None if ep is None else ep.f_pk_hz, no_ep)

    i_on = int(round(p["t_on_s"] * fs))
    i_lo = max(0, int(round((p["t_on_s"] - M.BASELINE_S) * fs)))
    row["r0"] = float(arr["r"][i_lo:i_on].mean())

    # exit quantities
    te = None if (ep is None or not ep.terminated) else float(ep.end_s)
    no_j = no_ep if ep is None else "episode_unterminated_at_run_end"
    cache = static_cache if static_cache is not None else {}
    key = json.dumps([cfg["path"], cfg["model"]], sort_keys=True, default=str)
    if key not in cache:
        cache[key] = j_exit_static_path(cfg, fi["grid_step"])
    j_static, static_why = cache[key]
    put("J_exit_static", j_static, static_why)
    if te is None:
        for c in ("J_exit_run", "exit_delay", "r_post_1s", "r_post_5s"):
            put(c, None, f"no_J_exit_run({no_j})")
        row["flag_J_exit_run_at_J0"] = False
    else:
        j_run, _, _ = M.j_exit_metrics(te, t_s, arr["J"], 0.0)
        row["J_exit_run"] = j_run
        row["flag_J_exit_run_at_J0"] = bool(abs(j_run - p["J0"]) <= J0_TOL)
        put("exit_delay", None if j_static is None else j_run - j_static, "no_J_exit_static")
        for w in WINDOWS_S:
            sel = (t_s >= te) & (t_s < te + w)
            ok = te + w <= t_s[-1] + 1.0 / fs
            put(f"r_post_{int(w)}s", float(arr["r"][sel].mean()) if ok else None, "window_extends_past_run_end")
    row["nan_reasons"] = ";".join(f"{c}={r}" for c, r in why.items())
    return row


def s6_files(root=None) -> list:
    """(row_kind, list, json path): 20 pre-registered S6 records, 2 supplementary P2 references, and the two S5 comparators
    (p2_linear at 10 s and the headline at 120 s), all sorted."""
    root = root_of(root)
    out = []
    for fam in ("S6_P3", "S6_P4a", "S6_P4b"):
        out += [("S6_pre_registered", "S6", p) for p in sorted((root / "results/S6" / fam).glob("*.json")) if not p.name.endswith(".dry.json")]
    out += [("S6_supplementary", "S6", p) for p in sorted((root / "results/S6/supp/S6_P2ref").glob("*.json")) if not p.name.endswith(".dry.json")]
    comp = []
    for p in sorted((root / "results/S5/ramp/p2_linear").glob("*.json")):
        if p.name.endswith(".dry.json"):
            continue
        if abs(json.loads(p.read_text(encoding="utf-8"))["config"]["path"]["T_ramp_s"] - 10.0) < 1e-9:
            comp.append(("S5_comparator", "S5", p))
    comp += [("S5_comparator", "S5", p) for p in sorted((root / "results/S5/ramp/S5ramp").glob("*.json")) if not p.name.endswith(".dry.json")]
    return out + comp


def s6_frame(rows: list) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=list(S6_COLUMNS))
    for c in S6_BOOL:
        df[c] = df[c].astype("boolean")
    for c in S6_NUMERIC:
        df[c] = df[c].astype("float64")
    kind_order = {"S6_pre_registered": 0, "S6_supplementary": 1, "S5_comparator": 2}
    df["_k"] = df["row_kind"].map(kind_order)
    df = df.sort_values(["_k", "path", "I_amp", "T_ramp_s"], kind="stable").drop(columns="_k").reset_index(drop=True)
    return df


# ---- A9 ----------------------------------------------------------------------------------------------------------
A9_COLUMNS = (
    "map", "cell_id", "i", "j", "J0", "Delta", "tau_d_ms", "T_ramp_s", "eta_H", "hopf_found", "run_id", "status", "class", "surge",
    "onset_s", "f_pk_hz", "inside_a4_region", "time_inside_s", "hopf_f_hz", "label_f", "labels_a_f_all", "label_a_f_primary",
    "g", "h", "labels_a_h_all", "unlabelled_a_h", "classifier_reason", "headline_marker", "nan_reasons")
A9_NUMERIC = ("J0", "Delta", "tau_d_ms", "T_ramp_s", "eta_H", "onset_s", "f_pk_hz", "time_inside_s", "hopf_f_hz")
A9_BOOL = ("hopf_found", "surge", "inside_a4_region", "label_f", "g", "h", "unlabelled_a_h", "headline_marker")


def _s(x) -> str:
    return "" if x is None or (isinstance(x, float) and math.isnan(x)) else str(x)


def _letters(x) -> list:
    """The label letters of a stored labels cell ('cf', 'c,f' or empty) as a sorted list."""
    return sorted(ch for ch in _s(x) if ch.isalpha())


def _opt(x):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else x


def a9_regime_map(root=None) -> pd.DataFrame:
    """One row per cell of the 1,226-cell list: map 1 (900), map 2 (325) and the headline cell, from the stored class tables."""
    root = root_of(root)
    cells = read_csv("configs/ms9/runlists/cells_1226.csv", root)
    m1 = read_csv("results/ms9/9e/map1_classes.csv", root)
    m2 = read_csv("results/ms9/9f/map2_classes.csv", root).rename(columns={"k": "j"})
    gh = read_csv("results/ms9/9g/a9_gh.csv", root, dtype={"key": str})
    ghk = {(int(r["map"]), r["key"]): r for _, r in gh.iterrows()}
    hl = cells[cells["kind"] == "headline"].iloc[0]
    hl_cls = read_csv("results/ms9/9d/s5_headline_classes.csv", root).iloc[0]
    rows = []

    def build(map_label, c, rec, has_hopf_f):
        why: dict[str, str] = {}
        cls = rec["class"]
        surge = bool(rec["surge"]) if "surge" in rec else M.is_surge_class(cls)
        row = {"map": map_label, "cell_id": c["name"], "i": int(c["i"]), "j": int(c["j"]), "J0": float(c["J0"]), "Delta": float(c["Delta"]),
               "tau_d_ms": float(c["tau_d_ms"]), "T_ramp_s": float(c["T_ramp_s"]), "eta_H": float(c["eta_H"]),
               "hopf_found": bool(c["hopf_found"]), "run_id": rec["run"], "status": rec.get("status", "ok"), "class": cls, "surge": surge}
        for col, src, reason in (("onset_s", "onset_s", "no_episode"), ("f_pk_hz", "f_pk_hz", "no_episode")):
            v = _opt(rec.get(src))
            row[col] = float("nan") if v is None else float(v)
            if v is None:
                why[col] = reason
        row["inside_a4_region"] = bool(rec["inside_a4_region"]) if _opt(rec.get("inside_a4_region")) is not None else None
        tin = _opt(rec.get("time_inside_s"))
        row["time_inside_s"] = float("nan") if tin is None else float(tin)
        if tin is None:
            why["time_inside_s"] = "not_stored_for_this_run"
        if row["inside_a4_region"] is None:
            why["inside_a4_region"] = "not_stored_for_this_run"
        hf = _opt(rec.get("hopf_f_hz")) if has_hopf_f else None
        row["hopf_f_hz"] = float("nan") if hf is None else float(hf)
        if hf is None:
            why["hopf_f_hz"] = "not_stored_in_map1_table" if not has_hopf_f else ("no_hopf_point" if not row["hopf_found"] else "not_stored_for_this_run")
        row["label_f"] = bool(rec["label_f"]) if _opt(rec.get("label_f")) is not None else None
        la = _letters(rec.get("labels_all"))
        lp = _s(rec.get("label_primary"))
        row["labels_a_f_all"], row["label_a_f_primary"] = ",".join(la), lp
        g_ = h_ = None
        reason = _s(rec.get("reason"))
        if map_label in ("1", "2") and (int(map_label), f"{c['i']},{c['j']}") in ghk:
            r = ghk[(int(map_label), f"{c['i']},{c['j']}")]
            g_, h_ = bool(r["g"]), bool(r["h"])
            reason = reason or _s(r["reason"])
            if _letters(r["labels_a_f"]) != la:
                raise NineIError(f"{c['name']}: labels a to f in a9_gh.csv ({r['labels_a_f']!r}) differ from the class table ({la!r})")
        elif not surge and map_label in ("1", "2"):
            raise NineIError(f"{c['name']}: non-surge cell without a g, h row in results/ms9/9g/a9_gh.csv")
        row["g"], row["h"] = g_, h_
        if g_ is None:
            why["g"] = why["h"] = "descriptor_defined_on_non_surge_cells_only"
        extra = [k for k, v in (("g", g_), ("h", h_)) if v]
        row["labels_a_h_all"] = ",".join(la + extra)
        row["unlabelled_a_h"] = bool((not surge) and map_label in ("1", "2") and not row["labels_a_h_all"])
        row["classifier_reason"] = reason
        row["headline_marker"] = bool(map_label == "headline")
        row["nan_reasons"] = ";".join(f"{k}={v}" for k, v in why.items())
        rows.append(row)

    c1 = cells[cells["kind"] == "map1"].set_index(["i", "j"])
    for _, rec in m1.iterrows():
        build("1", {**c1.loc[(int(rec["i"]), int(rec["j"]))].to_dict(), "i": int(rec["i"]), "j": int(rec["j"])}, rec, False)
    c2 = cells[cells["kind"] == "map2"].set_index(["i", "j"])
    for _, rec in m2.iterrows():
        build("2", {**c2.loc[(int(rec["i"]), int(rec["j"]))].to_dict(), "i": int(rec["i"]), "j": int(rec["j"])}, rec, True)
    hrec = {"run": hl_cls["run"], "status": hl_cls["status"], "class": hl_cls["class"], "surge": bool(hl_cls["surge"]),
            "onset_s": hl_cls["onset_s"], "f_pk_hz": hl_cls["f_pk_hz"], "label_f": hl_cls["label_f"]}
    build("headline", {**hl.to_dict(), "i": int(hl["i"]), "j": int(hl["j"])}, hrec, False)
    df = pd.DataFrame(rows, columns=list(A9_COLUMNS))
    for c in A9_NUMERIC:
        df[c] = df[c].astype("float64")
    for c in A9_BOOL:
        df[c] = df[c].astype("boolean")
    return df


def d31_nodes(root=None) -> pd.DataFrame:
    """The 178 D31 refined nodes (supplementary, exploratory, outside the 1,226 cells) with their cell parameters."""
    root = root_of(root)
    d = read_csv("results/ms9/9h/d31_classes.csv", root)
    cells = read_csv("configs/ms9/runlists/cells_d31.csv", root)
    m = d.merge(cells[["p", "q", "name", "kind", "J0", "T_ramp_s", "eta_start", "eta_peak"]], on=["p", "q"], how="outer", indicator=True)
    if (m["_merge"] != "both").any():
        raise NineIError(f"D31 class table and cell file differ on {int((m['_merge'] != 'both').sum())} nodes")
    m = m.drop(columns="_merge")
    m["supplementary"] = True
    m["surge"] = m["class"].map(M.is_surge_class).astype(bool)
    m["reason"] = m["reason"].fillna("")
    cols = ["supplementary", "name", "kind", "run", "p", "q", "J0", "Delta", "tau_d_ms", "T_ramp_s", "eta_H", "eta_start", "eta_peak",
            "hopf_found", "status", "class", "surge", "reason"]
    return m[cols].sort_values(["p", "q"]).reset_index(drop=True)


def subgrid_agreement(root=None) -> pd.DataFrame:
    """225 subgrid cells: the frozen D24 agreement (FAILED, DL-242) beside the post-hoc P-1 view (DL-255) and the control counts."""
    root = root_of(root)
    d24 = read_csv("results/ms9/9f/subgrid_cells.csv", root)
    p1 = read_csv("results/ms9/9h/p1_cells.csv", root)
    ct = read_csv("results/ms9/9g/control_cells.csv", root)
    m1 = read_csv("results/ms9/9e/map1_classes.csv", root)[["i", "j", "Delta", "tau_d_ms", "class"]].rename(columns={"class": "map1_class"})
    d24 = d24.rename(columns={"modal": "d24_modal_class", "tie": "d24_tie", "cell_agrees": "d24_cell_agrees", "n_seed_agree": "d24_n_seed_agree",
                              "counts": "d24_ramp_class_counts"})
    p1 = p1.rename(columns={"linked": "p1_ramp_linked", "not": "p1_not_ramp_linked", "tie": "p1_tie", "cell_agrees": "p1_cell_agrees"})
    p1 = p1.drop(columns="det")
    ct = ct[["i", "j", "control_counts", "control_NS", "ramp_NS"]].rename(columns={"control_counts": "control_class_counts"})
    out = d24.merge(p1, on=["i", "j"], validate="1:1").merge(ct, on=["i", "j"], validate="1:1").merge(m1, on=["i", "j"], validate="1:1")
    out["d24_frozen_status"] = "FAILED (DL-242)"
    out["p1_status"] = "post hoc, feeds no gate (DL-255)"
    out = out.rename(columns={"det": "deterministic_class"})
    for c in ("d24_tie", "d24_cell_agrees", "p1_tie", "p1_cell_agrees"):
        out[c] = out[c].astype(bool)
    if len(out) != 225:
        raise NineIError(f"subgrid agreement has {len(out)} cells, expected 225")
    return out.sort_values(["i", "j"]).reset_index(drop=True)


# ---- A10 ---------------------------------------------------------------------------------------------------------
A10_COLUMNS = (
    "control", "row_type", "supplementary", "run", "run_I1", "T_ramp_s", "W_s", "Delta", "tau_d_ms", "mode", "class", "class_I1",
    "onset_s", "onset_s_I1", "delay_eta", "delay_eta_I1", "duration_s", "duration_s_I1", "n_seeds", "n_non_NS", "fraction_non_NS",
    "class_counts", "reason", "status", "provisional", "expected_class", "as_expected", "g7_status")


def a10_controls(root=None) -> pd.DataFrame:
    root = root_of(root)
    nc1 = read_csv("results/ms9/nc1_classes.csv", root)
    rows: list[dict] = []

    def add(**kw):
        r = {c: "" for c in A10_COLUMNS}
        r.update(kw)
        r["g7_status"] = G7_STATUS
        rows.append(r)

    for _, r in nc1[nc1["family"] == "NC1"].sort_values("T_ramp_s").iterrows():
        add(control="NC1", row_type="mean_field_headline_cell", supplementary=False, run=r["run"], T_ramp_s=r["T_ramp_s"], W_s=r["W_s"],
            Delta=r["Delta"], tau_d_ms=r["tau_d_ms"], mode="D", **{"class": r["class"]}, reason=_s(r["reason"]), status=r["status"],
            provisional=_s(r["provisional"]), expected_class="D-none", as_expected=bool(r["quiet"]))
    for _, r in nc1[nc1["family"] == "NC1_cells"].sort_values(["Delta", "tau_d_ms"]).iterrows():
        add(control="NC1", row_type="map_cell", supplementary=False, run=r["run"], T_ramp_s=r["T_ramp_s"], W_s=r["W_s"], Delta=r["Delta"],
            tau_d_ms=r["tau_d_ms"], mode="D", **{"class": r["class"]}, reason=_s(r["reason"]), status=r["status"], provisional=_s(r["provisional"]),
            expected_class="D-none", as_expected=bool(r["quiet"]))
    for _, r in nc1[nc1["family"] == "NC1_net"].iterrows():
        add(control="NC1", row_type="network_run", supplementary=False, run=r["run"], T_ramp_s=r["T_ramp_s"], W_s=r["W_s"], Delta=r["Delta"],
            tau_d_ms=r["tau_d_ms"], mode="N", **{"class": r["class"]}, onset_s=_opt(r["onset_s"]), duration_s=_opt(r["duration_s"]),
            reason=_s(r["reason"]), status=r["status"], provisional=_s(r["provisional"]), expected_class="NS", as_expected=bool(r["quiet"]))
    for g in MCL.supplementary_per_window(nc1.to_dict("records")):
        add(control="NC1", row_type="mode_N_summary_per_window", supplementary=True, T_ramp_s=g["T_ramp_s"], W_s=g["W_s"], mode="N",
            n_seeds=g["n"], n_non_NS=g["non_NS"], fraction_non_NS=g["fraction_non_NS"], class_counts=json.dumps(g["counts"], sort_keys=True),
            expected_class="NS")
    nc2 = read_csv("results/ms9/9g/nc2_table.csv", root)
    for _, r in nc2.sort_values("T_ramp_s").iterrows():
        add(control="NC2", row_type="per_T_ramp", supplementary=False, run=r["I0_run"], run_I1=r["I1_run"], T_ramp_s=r["T_ramp_s"], mode="D",
            **{"class": r["I0_class"], "class_I1": r["I1_class"]}, onset_s=_opt(r["I0_onset_s"]), onset_s_I1=_opt(r["I1_onset_s"]),
            delay_eta=_opt(r["I0_delay_eta"]), delay_eta_I1=_opt(r["I1_delay_eta"]), duration_s=_opt(r["I0_duration_s"]),
            duration_s_I1=_opt(r["I1_duration_s"]))
    nc3 = read_csv("results/ms9/9g/nc3_table.csv", root)
    for _, r in nc3.sort_values("T_ramp_s").iterrows():
        add(control="NC3", row_type="per_T_ramp", supplementary=False, run=r["run"], T_ramp_s=r["T_ramp_s"], mode="D", **{"class": r["class"]},
            reason=_s(r["reason"]))
    df = pd.DataFrame(rows, columns=list(A10_COLUMNS))
    return df


# ---- G3 facts ----------------------------------------------------------------------------------------------------
G3_COLUMNS = ("group", "source", "mode", "n_runs", "D-tr", "D-sus", "D-none", "failed", "S+", "S-rel", "S-abs", "S-sus", "NS", "other",
              "n_surge_class", "n_sus_class", "n_quiet_class", "n_surge_class_not_sus")


def _count_row(group: str, source: str, mode: str, classes) -> dict:
    classes = list(classes)
    r = {"group": group, "source": source, "mode": mode, "n_runs": len(classes)}
    known = DET_CLASSES + ("failed",) + N_CLASSES
    for c in known:
        r[c] = sum(1 for x in classes if x == c)
    r["other"] = sum(1 for x in classes if x not in known)
    r["n_surge_class"] = sum(1 for x in classes if x in SURGE_CLASSES)
    r["n_sus_class"] = sum(1 for x in classes if x in SUS_CLASSES)
    r["n_quiet_class"] = sum(1 for x in classes if x in ("D-none", "NS"))
    r["n_surge_class_not_sus"] = r["n_surge_class"]          # surge classes are by definition not the sus classes
    return r


def g3_facts(s6: pd.DataFrame, root=None) -> pd.DataFrame:
    """Class counts by group; facts only. S5 from the stored A7 table (list S5), S6 from the 9i S6 table, maps and subgrid from the
    stored class tables (map 1: 900 cells, map 2: 325 cells, subgrid: 2,250 mode-N runs and 225 cell classes)."""
    root = root_of(root)
    a7 = pd.read_parquet(root / "results/A7/a7_ramp_metrics.parquet")
    s5 = a7[a7["list"] == "S5"]
    rows = []
    for pth in ("P1", "P2", "P5"):
        for mode in ("D", "N"):
            sel = s5[(s5["path"] == pth) & (s5["mode"] == mode)]
            if len(sel):
                rows.append(_count_row(f"S5 {pth}", "results/A7/a7_ramp_metrics.parquet (list S5)", mode, sel["cls"]))
    pre = s6[s6["row_kind"] == "S6_pre_registered"]
    rows.append(_count_row("S6 pre-registered (20)", "results/A7/a7_s6_metrics.parquet", "D", pre["class"]))
    sup = s6[s6["row_kind"] == "S6_supplementary"]
    rows.append(_count_row("S6 supplementary P2 references (2)", "results/A7/a7_s6_metrics.parquet", "D", sup["class"]))
    m1 = read_csv("results/ms9/9e/map1_classes.csv", root)
    m2 = read_csv("results/ms9/9f/map2_classes.csv", root)
    rows.append(_count_row("map 1 (900 cells)", "results/ms9/9e/map1_classes.csv", "D", m1["class"]))
    rows.append(_count_row("map 2 (325 cells)", "results/ms9/9f/map2_classes.csv", "D", m2["class"]))
    sg = read_csv("results/ms9/9f/subgrid_classes.csv", root)
    rows.append(_count_row("subgrid runs (225 cells x 10 seeds)", "results/ms9/9f/subgrid_classes.csv", "N", sg["class"]))
    sc = read_csv("results/ms9/9f/subgrid_cells.csv", root)
    rows.append(_count_row("subgrid cells, deterministic class (225)", "results/ms9/9f/subgrid_cells.csv", "D", sc["det"]))
    return pd.DataFrame(rows, columns=list(G3_COLUMNS))


def g3_markdown(df: pd.DataFrame) -> str:
    cls = ["D-tr", "D-sus", "D-none", "failed", "S+", "S-rel", "S-abs", "S-sus", "NS", "other"]
    L = ["# MS9 9i: G3 facts table (class counts; facts only, no verdict)", "",
         "Source: stored records and class tables, no simulation (DL-258 to DL-260). The G3 rule (plan, Table 11.2 and section 4.3): add M3a/M3b "
         "only if every onset is S-sus or D-sus and termination by J -> 0 is rejected. This table gives the class counts only; it does not "
         "test whether termination by J -> 0 is rejected (the plan gives no operational test; asked in the 9i report).", "",
         "| group | mode | runs | " + " | ".join(cls) + " | surge class | sus class | quiet class |",
         "|---|---|---|" + "---|" * len(cls) + "---|---|---|"]
    for _, r in df.iterrows():
        L.append(f"| {r['group']} | {r['mode']} | {r['n_runs']} | " + " | ".join(str(int(r[c])) for c in cls) +
                 f" | {int(r['n_surge_class'])} | {int(r['n_sus_class'])} | {int(r['n_quiet_class'])} |")
    L += ["", "Surge class = D-tr (mode D) or S+, S-rel, S-abs (mode N), Table 2.1. Sus class = D-sus or S-sus. Quiet class = D-none or NS.", ""]
    return "\n".join(L)


def label_policy_facts(a9: pd.DataFrame) -> list:
    """Facts on which cells carry a to f labels in the stored tables (map 1 labelled surge-class cells, map 2 did not)."""
    out = []
    for lab in ("1", "2"):
        sg = a9[(a9["map"] == lab) & a9["surge"]]
        out.append(f"map {lab}: labels a to f stored on {int((sg['labels_a_f_all'] != '').sum())} of {len(sg)} surge-class cells")
    return out


# ---- consistency checks between stored files (reported, never fixed) ------------------------------------------------
def consistency(s6: pd.DataFrame, a9: pd.DataFrame, root=None) -> list:
    """Lines describing every mismatch found between the stored files; an empty list means none found."""
    root = root_of(root)
    out: list[str] = []
    cells = read_csv("configs/ms9/runlists/cells_1226.csv", root)
    for kind, label, n in (("map1", "1", 900), ("map2", "2", 325), ("headline", "headline", 1)):
        have = int((a9["map"] == label).sum())
        if have != n or int((cells["kind"] == kind).sum()) != n:
            out.append(f"A9 rows for {kind}: file has {have}, cell list has {int((cells['kind'] == kind).sum())}, expected {n}")
    if a9["cell_id"].duplicated().any():
        out.append("A9: duplicate cell ids")
    if set(a9["cell_id"]) != set(cells["name"]):
        out.append("A9: cell ids differ from configs/ms9/runlists/cells_1226.csv")
    if a9["status"].ne("ok").any():
        out.append(f"A9: {int(a9['status'].ne('ok').sum())} cells with status other than ok")
    # run records on disk against the class tables
    for lab, rel in (("1", "results/S7/S7_map1"), ("2", "results/S7/S7_map2")):
        disk = {p.stem for p in (root / rel).rglob("*.json") if not p.name.endswith(".dry.json")}
        tab = set(a9.loc[a9["map"] == lab, "run_id"])
        if disk != tab:
            out.append(f"map {lab}: {len(disk - tab)} records on disk without a table row, {len(tab - disk)} table rows without a record")
    if int(a9["unlabelled_a_h"].sum()) != 0:
        out.append(f"A9: {int(a9['unlabelled_a_h'].sum())} non-surge cells unlabelled under a to h (DL-249 says none)")
    # S6 against the 9d table and the O12 file
    if len(s6) != 24 or int((s6["row_kind"] == "S6_pre_registered").sum()) != 20 or int((s6["row_kind"] == "S6_supplementary").sum()) != 2:
        out.append(f"S6 table: {len(s6)} rows ({s6['row_kind'].value_counts().to_dict()}), expected 20 + 2 + 2")
    if s6["eta_H_nominal"].nunique() != 1:
        out.append(f"S6 table: eta_H differs between runs: {sorted(s6['eta_H_nominal'].unique())}")
    t9d = read_csv("results/ms9/9d/s6_table.csv", root)
    for _, r in t9d.iterrows():
        m = s6[s6["run_id"] == r["run"]]
        if len(m) != 1:
            out.append(f"9d s6_table run {r['run']} not found once in the S6 table")
            continue
        m = m.iloc[0]
        for a, b in (("onset_s", "onset_s"), ("f_pk_hz", "f_pk_hz"), ("duration_s", "duration_s")):
            if not math.isclose(float(r[a]), float(m[b]), rel_tol=1e-9, abs_tol=1e-9):
                out.append(f"{r['run']}: {a} 9d {r[a]} vs 9i {m[b]}")
        if r["class"] != m["class"]:
            out.append(f"{r['run']}: class 9d {r['class']} vs 9i {m['class']}")
    o12 = read_csv("results/A7/o12_data_package.csv", root)
    for _, m in s6[s6["row_kind"] == "S5_comparator"].iterrows():
        o = o12[o12["run_id"] == m["run_id"]]
        if len(o) != 1:
            out.append(f"{m['run_id']}: not found once in o12_data_package.csv")
            continue
        o = o.iloc[0]
        for a, b in (("J_exit_run", "J_exit_run"), ("J_exit_static", "J_exit_static"), ("exit_delay", "exit_delay"), ("r_mean_1s", "r_post_1s"),
                     ("r_mean_5s", "r_post_5s")):
            x, y = o[a], m[b]
            if not ((pd.isna(x) and pd.isna(y)) or (not pd.isna(x) and not pd.isna(y) and math.isclose(float(x), float(y), rel_tol=1e-6, abs_tol=1e-9))):
                out.append(f"{m['run_id']}: {a} O12 package {x} vs 9i {y}")
    a7 = pd.read_parquet(root / "results/A7/a7_ramp_metrics.parquet").set_index("run_id")
    for _, m in s6[s6["row_kind"] == "S5_comparator"].iterrows():
        if m["run_id"] in a7.index:
            q = a7.loc[m["run_id"]]
            for a, b in (("onset_s", "onset_s"), ("duration_s", "duration_s"), ("f_pk_hz", "f_pk_hz"), ("delay_eta", "delay_eta")):
                if not math.isclose(float(q[a]), float(m[b]), rel_tol=1e-9, abs_tol=1e-9):
                    out.append(f"{m['run_id']}: {a} MS8 A7 table {q[a]} vs 9i {m[b]}")
            if q["cls"] != m["class"]:
                out.append(f"{m['run_id']}: class MS8 A7 table {q['cls']} vs 9i {m['class']}")
        else:
            out.append(f"{m['run_id']}: not in a7_ramp_metrics.parquet")
    return [x for x in out if x]
