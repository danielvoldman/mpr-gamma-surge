"""A0: replication table K1 to K5 (plan 5.2 A0, Table 7.1, G0 part 1; MS2 step 2e, DL-091).

Analysis only: reads the A1, A2 and S1 results (after recomputing each file's SHA-256 and checking it
against its run record) and the frozen tolerances (configs/replication.yaml, SHA-256 of DL-084), and
evaluates one row per target. Tolerances are read, never set here.
"""
from __future__ import annotations

import csv
import io

import numpy as np
import yaml

from .. import config as C
from .. import provenance as P
from ..provenance import ProvenanceError
from ..models.fixed_points import classify_all

FROZEN_SHA256 = "667d3b788d1c7c5aebc716998d09746b685358f326334aae87591924908819a5"   # DL-084, LF text
K5_SETS = ("path.name=I_sin", "path.I_period_s=0.4")                                  # DL-088 (5)
UPSTREAM = {"A1": ("configs/A1.yaml", ()), "A2": ("configs/A2.yaml", ()),
            "S1_K4": ("configs/S1.yaml", ()), "S1_K5": ("configs/S1.yaml", K5_SETS)}
COLUMNS = ("target", "measured", "tolerance", "pass", "source_results", "unverified")

# UNVERIFIED items each row depends on, with the entries that mark them (DL-079, DL-082, DL-085 to DL-089).
UNVERIFIED = {
    "K1": ["A1 refinement widths: band +-4 cells, box +-10 cells (DL-085, DL-086 2)",
           "K1 edge definition: node whose root count differs from the next node (DL-064, DL-086 3)"],
    "K2": ["K2 root choice: highest-r root on each J row (DL-086 4)",
           "A1 refinement widths for the half-spacing rows (DL-085, DL-086 2)"],
    "K3": ["none beyond the A1 readings (DL-086 1); the K3 point is a base node, outside the refined region"],
    "K4-MF": ["K4 tail fraction 0.1 (DL-076, DL-079)", "K4 fit window end 40 tau and tail rule (DL-089 1, 2)",
              "tau mapping tau = 10 ms (DL-082)", "I_step reading and 280 tau run length (DL-088 1, 4)"],
    "K5": ["K5 burst definition: midpoint of the I = 0 node and focus (DL-082)",
           "K5 tolerance 0.1 tau (DL-082)", "K5 time mapping, paper time unit = tau (DL-082)",
           "K5 period 40 tau, 2 transient + 5 checked periods (DL-082, DL-088 1, 4)",
           "I_sin reading (DL-088 1)"],
}


# --- upstream results, verified ----------------------------------------------------------------

def _plan(config_path, sets):
    from .. import run as R          # late import: run.py resolves tasks by name
    return R.build_plan(config_path, list(sets))


def upstream_npz(name):
    """Path of the complete result npz of upstream `name`, or None."""
    path, sets = UPSTREAM[name]
    plan = _plan(path, sets)
    rec = P.find_complete(plan.out_dir, plan.cells[0]["cfg"])
    return None if rec is None else rec.with_suffix(".npz")


_SHA_MEMO: dict = {}


def upstream_sha256s():
    """{name: SHA-256 of the upstream npz, or None}; hash_view adds this for run.kind = a0 (DL-091, as DL-090)."""
    out = {}
    for name in UPSTREAM:
        npz = upstream_npz(name)
        if npz is None:
            out[name] = None
            continue
        st = npz.stat()
        key = (str(npz), st.st_mtime_ns, st.st_size)
        if key not in _SHA_MEMO:
            _SHA_MEMO[key] = P.sha256_file(npz)
        out[name] = _SHA_MEMO[key]
    return out


def verified_upstream(name):
    """(npz path, run record) of upstream `name`; refuses unless the record is ok and the recomputed
    SHA-256 of the npz equals the one in the record."""
    path, sets = UPSTREAM[name]
    plan = _plan(path, sets)
    full = C.config_hash(plan.cells[0]["cfg"])
    cands = sorted(plan.out_dir.glob(f"*_{C.short_hash(full)}.json"))
    if not cands:
        raise C.ConfigError(f"A0: no run record for {name} ({path}) in {C.to_posix(plan.out_dir)}; run it first")
    rec = P.read_run_record(cands[0])
    npz = cands[0].with_suffix(".npz")
    if rec.get("status") != "ok" or rec.get("config_hash") != full:
        raise ProvenanceError(f"A0: the record of {name} is not an ok record of this config")
    want = rec.get("outputs", {}).get(npz.name)
    if want is None or not npz.is_file() or P.sha256_file(npz) != want:
        raise ProvenanceError(f"A0: SHA-256 of {C.to_posix(npz)} does not match its run record; refusing")
    return npz, rec


def check_frozen(rep_path):
    sha = P.sha256_file(rep_path)
    if sha != FROZEN_SHA256:
        raise ProvenanceError(f"A0: {C.to_posix(rep_path)} SHA-256 {sha} differs from the frozen {FROZEN_SHA256} "
                              "(DL-084); refusing. A change needs a decision-log entry (plan 7, D34)")
    return sha


# --- rows -----------------------------------------------------------------------------------------

def _row(target, measured, tolerance, passed, source):
    return {"target": target, "measured": measured, "tolerance": tolerance, "pass": bool(passed),
            "source_results": source, "unverified": "; ".join(UNVERIFIED[target])}


def row_k1(a1, rep, src):
    n_r, cell = rep["K1"]["n_r"], rep["K1"]["cell"]
    if len(a1["k1_r"]) != n_r:
        raise ValueError(f"K1: A1 has {len(a1['k1_r'])} r values, the criteria say {n_r}")
    half, base = a1["k1_pass_half"], a1["k1_pass_base"]
    return _row("K1", f"{int(half.sum())}/{n_r} within one cell at half spacing near the fold "
                      f"({int(base.sum())}/{n_r} at base spacing; the two cusp points need half spacing, DL-081)",
                f"count-change node within ({cell['d_eta_bar']}, {cell['d_J']}) of the formula point, all {n_r} r",
                half.all(), src)


def row_k2(a1, rep, src):
    cell = rep["K2"]["cell"]
    ing = a1["k2_in_grid"]
    pb, ph = a1["k2_pass_base"][ing], a1["k2_pass_half"]
    one = bool((a1["k2_n_sign_changes_base"][ing] == 1).all())
    return _row("K2", f"{int(pb.sum())}/{len(pb)} J rows at base spacing, {int(ph.sum())}/{len(ph)} at half spacing; "
                      f"max offset {np.nanmax(a1['k2_offset_cells_base'][ing]):.3g} cells at base spacing; "
                      f"exactly one sign change per base row: {one}; C9 node region exists: "
                      f"{bool(a1['c9_node_region_exists'])}",
                f"discriminant sign change within ({cell['d_eta_bar']}, {cell['d_J']}) of eta_f(J), all rows",
                pb.all() and ph.all(), src)


def row_k3(a1, rep, src):
    pt = rep["K3"]["point"]
    labels = [str(x) for x in a1["k3_labels"]]
    ok = sorted(labels) == ["saddle", "stable_focus", "stable_node"]
    return _row("K3", f"labels at ({pt['eta_bar_over_Delta']}, {pt['J_over_sqrtDelta']}): {', '.join(labels)}",
                "exactly a focus, a node and a saddle", ok and bool(a1["k3_pass"]), src)


def row_k4(a2, rep, src):
    mf = rep["K4"]["mean_field"]
    ef, ed = float(a2["k4_rel_err_frequency"]), float(a2["k4_rel_err_decay"])
    tf, td = mf["tolerance_frequency_rel"], mf["tolerance_decay_rel"]
    return _row("K4-MF", f"frequency error {ef:.3g}, decay error {ed:.3g} (fit omega {float(a2['k4_omega_fit']):.5g}, "
                         f"decay {float(a2['k4_decay_fit']):.5g}; linearisation {float(a2['k4_omega_lin']):.5g}, "
                         f"{float(a2['k4_decay_lin']):.5g}; {float(a2['k4_cycles']):.1f} tail cycles)",
                f"frequency <= {tf}, decay <= {td} (relative)", ef <= tf and ed <= td, src)


def k5_check(t_tau, r, mid, period, transient_periods, checked_periods, tol):
    """K5 (DL-082): per checked period one up- and one down-crossing of `mid`; up-crossings `period` apart within tol."""
    k_up = np.flatnonzero((r[:-1] < mid) & (r[1:] >= mid))
    k_dn = np.flatnonzero((r[:-1] >= mid) & (r[1:] < mid))
    lin = lambda k: t_tau[k] + (mid - r[k]) / (r[k + 1] - r[k]) * (t_tau[k + 1] - t_tau[k])
    up, dn = lin(k_up), lin(k_dn)
    count = lambda x, k: int(((x >= (transient_periods + k) * period) & (x < (transient_periods + k + 1) * period)).sum())
    per = [(count(up, k), count(dn, k)) for k in range(checked_periods)]
    last = up[up >= transient_periods * period]
    dev = np.abs(np.diff(last) - period)
    ok = all(p == (1, 1) for p in per) and len(last) == checked_periods and bool((dev <= tol).all())
    return {"pass": ok, "per_period_up_down": per, "n_up_after_transient": int(len(last)),
            "max_period_dev": float(dev.max()) if len(dev) else float("nan")}


def k5_mid(eta_bar, J, Delta):
    st = {label: y for y, label, _ in classify_all(eta_bar, J, Delta, 0.0)}
    return 0.5 * (st["stable_node"][0] + st["stable_focus"][0]), st["stable_node"][0], st["stable_focus"][0]


def check_k5_forcing(k5, path):
    """The yaml K5 forcing I0 sin(omega t) must be the forcing of the run that produced the series (DL-092 4)."""
    f = k5["forcing"]
    err = lambda msg: ProvenanceError(f"A0 K5: {msg}")
    if path.get("name") != "I_sin" or path.get("t_on_s", 0.0) != 0.0:
        raise err(f"run path is {path.get('name')} from t_on_s = {path.get('t_on_s')}, yaml says {f['form']}")
    if not np.isclose(path["I_amp"], f["I0"], rtol=0, atol=1e-12):
        raise err(f"run amplitude {path['I_amp']} differs from yaml I0 = {f['I0']}")
    omega = 2 * np.pi * path["tau_ms"] / (1000.0 * path["I_period_s"])
    if not np.isclose(omega, f["omega"], rtol=1e-9, atol=0):
        raise err(f"run omega {omega!r} (per tau) differs from yaml omega = {f['omega']!r}")


def row_k5(s1, rep, src, tau_ms, path=None):
    k5 = rep["K5"]
    if path is not None:
        check_k5_forcing(k5, {**path, "tau_ms": tau_ms})
    pt = k5["point"]
    mid, low, high = k5_mid(pt["eta_bar"], pt["J"], pt["Delta"])
    res = k5_check(s1["t_ms"] / tau_ms, s1["r"], mid, k5["period"], k5["transient_periods"], k5["checked_periods"],
                   k5["period_tol"])
    return _row("K5", f"up/down crossings per checked period {res['per_period_up_down']}; max |up-crossing spacing - "
                      f"{k5['period']:g}| = {res['max_period_dev']:.3g} tau; threshold r = {mid:.4f} "
                      f"(low {low:.4f}, high {high:.4f})",
                f"one up and one down per period for {k5['checked_periods']} periods after {k5['transient_periods']}; "
                f"spacing within {k5['period_tol']} tau", res["pass"], src)


# --- runner task ------------------------------------------------------------------------------------

def _src(name, npz):
    return f"{name}:{npz.name}@{P.sha256_file(npz)[:12]}"


def run_a0(cfg, deadline=None):
    rep_path = C.repo_root() / cfg["replication"]["tolerances_file"]
    rep_sha = check_frozen(rep_path)
    with open(rep_path, "r", encoding="utf-8") as fh:
        rep = yaml.safe_load(fh)
    up = {n: verified_upstream(n) for n in UPSTREAM}
    shas = {n: P.sha256_file(p) for n, (p, _) in up.items()}
    if C.hash_view(cfg)["a0"]["upstream_sha256"] != shas:
        raise C.ConfigError("A0: an upstream result changed after the config was hashed; rerun")
    for n in ("A1", "A2"):              # the S1 runs read no criteria file (their record has none)
        if up[n][1]["criteria_sha256"] != rep_sha:
            raise ProvenanceError(f"A0: the record of {n} was made against a different replication.yaml")
    flags2 = up["A2"][1]["flags"]
    if flags2["a1_npz_sha256"] != shas["A1"] or flags2["s1_npz_sha256"] != shas["S1_K4"]:
        raise ProvenanceError("A0: the A2 result was computed from different A1 or S1 files than the ones present")

    load = lambda n: (lambda z: {k: z[k] for k in z.files})(np.load(up[n][0]))
    a1, a2, s1 = load("A1"), load("A2"), load("S1_K5")
    tau_ms = up["S1_K5"][1]["config"]["model"]["tau_ms"]
    rows = [row_k1(a1, rep, _src("A1", up["A1"][0])), row_k2(a1, rep, _src("A1", up["A1"][0])),
            row_k3(a1, rep, _src("A1", up["A1"][0])),
            row_k4(a2, rep, f"{_src('A2', up['A2'][0])} (from {_src('S1(K4)', up['S1_K4'][0])}, "
                            f"{_src('A1', up['A1'][0])})"),
            row_k5(s1, rep, _src("S1(K5)", up["S1_K5"][0]), tau_ms, up["S1_K5"][1]["config"]["path"])]
    arrays = {f"col_{c}": np.array([r[c] for r in rows]) for c in COLUMNS}
    failed = [r["target"] for r in rows if not r["pass"]]
    flags = {"rows_pass": {r["target"]: r["pass"] for r in rows}, "failed": failed, "upstream_npz_sha256": shas,
             "replication_yaml_sha256": rep_sha, "status_note": "rows depend on UNVERIFIED items, listed per row"}
    msg = "A0: " + ", ".join(f"{r['target']} {'pass' if r['pass'] else 'FAIL'}" for r in rows)
    return {"arrays": arrays, "message": msg, "flags": flags}


def csv_text(arrays):
    """The A0 table as CSV text (LF line ends) from the arrays of the result npz."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLUMNS)
    for i in range(len(arrays["col_target"])):
        w.writerow([("pass" if arrays["col_pass"][i] else "fail") if c == "pass" else str(arrays[f"col_{c}"][i])
                    for c in COLUMNS])
    return buf.getvalue()
