"""MS13 13a: read-only readiness check and load-time sample of the stored figure inputs (docs/ms13_plan.md sections 2 and 7).

  .venv/Scripts/python.exe scripts/ms13_inputs.py readiness
  .venv/Scripts/python.exe scripts/ms13_inputs.py timing

Reads results/ and writes nothing (no file under results/, figures/ or anywhere else; the report goes to stdout). It simulates nothing and
imports no run or simulation module. 'readiness' OPENS every stored file a figure needs (json parsed; npz opened and its member list read, the
required arrays checked by name; parquet and csv read) and reports ready / partly ready / missing per figure and per input. 'timing' times the
full load of the largest files of each input family and of a fixed stride sample, and extrapolates to the whole family (the extrapolation is an
ESTIMATE). The input lists are the plan's 'From' column of Table 8.1 and the output paths of handoff (c); the expected record counts are the
counts of the plan's Table 6.2 rows (derivations in docs/ms13_plan.md section 2); a count is None where the plan states none.
"""
from __future__ import annotations

import json
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from mprsurge import config as C
from mprsurge.provenance import environment_info, git_info

ROOT = C.repo_root()
RES = ROOT / "results"
MF = ("t_ms", "r", "v")
NET = ("t_ms", "r", "v", "raster_t_ms", "raster_neuron", "raster_j")


def rec(label, pattern, expected, keys=MF):
    """A family of run records: <stem>.json (not .dry.json) and <stem>.npz."""
    return {"kind": "rec", "label": label, "pattern": pattern, "expected": expected, "keys": keys}


def fil(label, path):
    return {"kind": "file", "label": label, "path": path}


INPUTS = {
    "F1": [
        rec("S5 headline mean-field record (P2, ref_devalle, 120 s)", "S5/ramp/S5ramp/S5ramp_0000_240de3ef73be.json", 1),
        rec("S8 network headline (T_ramp 10 and 120 s x 3 seeds)", "S8/S8_head/*.json", 6, NET),
        rec("S8 mean-field companions of the headline (head60)", "S8/mf/S8_mf_head60/*.json", None),
        fil("A8 reference amplitude", "A8/a8_aref.json"),
        fil("A8 sensitivity table", "A8/a8_sensitivity.csv"),
        fil("criteria file (spectrogram settings)", "configs/robustness_criteria.yaml"),
    ],
    "F2": [
        fil("A5 cycles", "A5/a5_cycles.npz"),
        fil("A5 Julia summary", "A5/julia/a5.json"),
        rec("S4 mean-field sweep, ref_devalle", "S4/devalle/*.json", 1, ("t_ms", "r", "v", "param", "step", "step_param", "step_up")),
        rec("S4 network sweep (15 steps)", "S4/net/*.json", 1, ("t_ms", "r", "v", "param", "step", "step_param", "step_up")),
    ],
    "F3": [
        fil("A4 Hopf curves", "A4/a4_hopf_curves.npz"),
        fil("A6 frequency map", "A6/a6_freq_map.npz"),
        fil("A6 summary", "A6/a6_summary.json"),
        fil("A4 run record (source of the F3 parameter rows)", "A4/A4_0000_4ece63ed731f.json"),
        fil("A6 run record (source of the F3 parameter rows)", "A6/A6_0000_daa85487fd0a.json"),
        fil("A11 robustness table (FAIL-row strip)", "A11/a11_robustness.csv"),
        fil("P1 run record (linear, T_ramp 100 s; path arrow)", "S5/ramp/p1_linear/p1_linear_0008_333859d6472b.json"),
        fil("P2 run record (linear, T_ramp 120 s, headline; path arrow)", "S5/ramp/S5ramp/S5ramp_0000_240de3ef73be.json"),
        fil("P3 run record (linear, T_ramp 120 s, I_amp 1; path arrow)", "S6/S6_P3/S6_P3_0006_5fb237a3d3fd.json"),
        fil("P4a run record (linear, T_ramp 120 s; path arrow)", "S6/S6_P4a/S6_P4a_0002_42415b96d00c.json"),
        fil("P4b run record (linear, T_ramp 120 s; path arrow)", "S6/S6_P4b/S6_P4b_0002_7be4a3067a9d.json"),
        fil("P5 run record (linear, T_ramp 100 s; path arrow)", "S5/ramp/p5_linear/p5_linear_0008_da88da96d075.json"),
    ],
    "F4": [
        fil("A7 ramp metrics", "A7/a7_ramp_metrics.parquet"),
        fil("A3 saddle-node ramp table (M2)", "A3/a3_sn_ramp.parquet"),
        fil("A2 ring map (M2 ring)", "A2/a2_ring_map.npz"),
        fil("A4 entry-exit range (RB3(a))", "A4/a4_rb3a_range.csv"),
        fil("A4 entry-exit summary", "A4/a4_rb3a_summary.json"),
        rec("S5 ramp families (P1, P2, P5 x linear, sigmoid x 13 T_ramp; start distance; headline)", "S5/ramp/*/*.json", None),
        rec("S5 baseline-only mode-N runs (headline cell + 900 + 325 map cells; noise band)", "S5/baseline/S5base_*.json", 1226),
        rec("S11 noise level (3 sigma x 4 T_ramp x 10 seeds)", "S11/S11/*.json", 120),
        rec("S11 constant-parameter controls (DL-251)", "S11/S11_ctrl/*.json", 30),
    ],
    "F5": [
        fil("A9 regime map (map 1, map 2)", "A9/a9_regime_map.parquet"),
        fil("A9 regime map v2", "A9/a9_regime_map_v2.parquet"),
        fil("A9 subgrid agreement", "A9/a9_subgrid_agreement.parquet"),
        rec("S7 map 1 (30 x 30, 120 s)", "S7/S7_map1/*.json", 900),
        rec("S7 map 2 (25 x 13)", "S7/S7_map2/*.json", 325),
        rec("S7 noisy subgrid (225 cells x 10 seeds)", "S7/S7_subgrid/*.json", 2250),
        rec("S8 network at 4 map cells (3 seeds)", "S8/S8_cells/*.json", 12, NET),
        rec("S9 finite size (4 N x 10 seeds)", "S9/S9/*.json", 40, NET),
        rec("S9 constant-parameter controls", "S9/S9_ctrl/*.json", None, NET),
    ],
    "F6": [
        fil("A9 regime map (failure reasons)", "A9/a9_regime_map_v2.parquet"),
        fil("A10 controls", "A10/a10_controls.csv"),
        fil("A7 S6 metrics", "A7/a7_s6_metrics.parquet"),
        rec("S6 P3 (3 I_amp x 4 T_ramp)", "S6/S6_P3/*.json", 12),
        rec("S6 P4a", "S6/S6_P4a/*.json", 4),
        rec("S6 P4b", "S6/S6_P4b/*.json", 4),
        rec("S12 NC1 (13 T_ramp)", "S12/NC1/*.json", 13),
        rec("S12 NC1 at 5 map cells", "S12/NC1_cells/*.json", 5),
        rec("S12 NC1 network (1 seed, 120 s)", "S12/NC1_net/*.json", 1, NET),
        rec("S12 NC2 (13 T_ramp)", "S12/NC2/*.json", 13),
        rec("S12 NC3 (13 T_ramp)", "S12/NC3/*.json", 13),
    ],
    "FS1": [
        fil("A1 fixed points (M2)", "A1/a1_fixedpoints_2d.npz"),
        fil("A2 ring map", "A2/a2_ring_map.npz"),
        fil("A0 replication table", "A0/a0_replication.csv"),
        rec("S1 M2 validation (K4 step, K5 sinusoid)", "S1/*.json", 4),
    ],
    "FS2": [
        rec("S3 mean field, ref_ceni (3 tau_d)", "S3/ceni/*.json", 3),
        rec("S3 mean field, ref_devalle (2 tau_d)", "S3/devalle/*.json", 2),
        rec("S3 network, ref_ceni", "S3/net_ceni/*.json", None, NET),
        rec("S3 network, ref_devalle", "S3/net_devalle/*.json", 2, NET),
        rec("S3 network, K8 (N = 5e4)", "S3/net_k8/*.json", None, NET),
        fil("S3 mean-field summary", "S3/s3_mf_summary.json"),
        fil("S3 network summary", "S3/s3_net_summary.json"),
        fil("A4 Hopf curves", "A4/a4_hopf_curves.npz"),
        fil("A5 cycles", "A5/a5_cycles.npz"),
        fil("A6 frequency map", "A6/a6_freq_map.npz"),
    ],
    "FS3": [
        rec("S9 finite size", "S9/S9/*.json", 40, NET),
        rec("S10 heterogeneity shape (3 shapes x 3 seeds)", "S10/S10/*.json", 9, NET),
        rec("S10 controls", "S10/S10_ctrl/*.json", None, NET),
        rec("S11 noise level", "S11/S11/*.json", 120),
        rec("S11 constant-parameter controls", "S11/S11_ctrl/*.json", 30),
    ],
    "FS4": [
        rec("S13 delta_0 ladder", "S13/delta0/*.json", None),
        rec("S13 rtol ladder", "S13/rtol/*.json", None),
        rec("S13 Radau", "S13/radau/*.json", None),
        rec("S13 floor level 0", "S13/floor_l0/*.json", None),
        rec("S13 floor level 1", "S13/floor_l1/*.json", None),
        rec("S13 floor level 2", "S13/floor_l2/*.json", None),
        rec("S13 MS11 mean-field records (delta_0, floor 10 and 316 s, rtol: 68)", "S13/ms11/S13_[dfr]*/*.json", 68),
        rec("S13 MS11 network records (dt ladder, V_p, 18)", "S13/ms11/S13_net/*.json", 18, NET),
        fil("A11 robustness table", "A11/a11_robustness.csv"),
    ],
    "FS5": [
        fil("A8 sensitivity table", "A8/a8_sensitivity.csv"),
        fil("A8 baseline summary", "A8/baseline/a8_baseline_summary.json"),
        fil("A8 reachability", "A8/sensitivity/a8_reachability.csv"),
        fil("A11 robustness table (RB9, RB10 rows)", "A11/a11_robustness.csv"),
        fil("A11 RB9(a) unit level", "A11/rb9a_unit_level.json"),
        fil("A6 frequency map (frequency mapping panel; UNVERIFIED)", "A6/a6_freq_map.npz"),
        fil("tests/test_surge_metrics.py (synthetic signals)", "../tests/test_surge_metrics.py"),
    ],
    "FS6": [],   # S14, S15 not run (MS12-C1)
}



def open_file(p: Path, keys=()):
    """Open one stored file; return (ok, note). Raises nothing."""
    try:
        s = p.suffix
        if s == ".json":
            json.loads(p.read_text(encoding="utf-8"))
        elif s == ".npz":
            with zipfile.ZipFile(p) as zf:
                names = {n[:-4] for n in zf.namelist() if n.endswith(".npy")}
                if zf.testzip() is not None:
                    return False, "bad zip member"
            miss = [k for k in keys if k not in names]
            if miss:
                return False, "missing arrays " + ",".join(miss)
        elif s == ".parquet":
            d = pd.read_parquet(p)
            return True, f"{len(d)} rows"
        elif s == ".csv":
            d = pd.read_csv(p)
            return True, f"{len(d)} rows"
        elif s in (".yaml", ".py", ".md"):
            p.read_bytes()
        return True, ""
    except Exception as e:  # noqa: BLE001 - a stored file that cannot be opened is reported, not raised
        return False, f"{type(e).__name__}: {e}"[:120]


def resolve(spec):
    """Return the list of (json_path, npz_path or None) for a record family, or [path] for a file."""
    if spec["kind"] == "file":
        p = (ROOT / spec["path"][3:]) if spec["path"].startswith("../") else (ROOT / spec["path"] if spec["path"].startswith("configs/") else RES / spec["path"])
        return [p]
    js = sorted(q for q in RES.glob(spec["pattern"]) if not q.name.endswith(".dry.json") and not q.name.endswith("_params.md"))
    return [(j, j.with_suffix(".npz")) for j in js]


def check_spec(spec):
    items = resolve(spec)
    if spec["kind"] == "file":
        p = items[0]
        if not p.exists():
            return {"found": 0, "ok": 0, "expected": 1, "notes": ["missing"]}
        ok, note = open_file(p)
        return {"found": 1, "ok": int(ok), "expected": 1, "notes": [note] if note else []}
    def one(it):
        j, z = it
        okj, nj = open_file(j)
        if z.exists():
            okz, nz = open_file(z, spec["keys"])
        else:
            okz, nz = False, "npz missing"
        return okj and okz, (nj if not okj else nz)
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(one, items))
    notes = sorted({n for ok, n in res if not ok and n})
    return {"found": len(items), "ok": sum(1 for ok, _ in res if ok), "expected": spec["expected"], "notes": notes[:3]}


def verdict(rows):
    if not rows:
        return "NOT PRODUCED (no inputs: S14, S15 not run)"
    full = all(r["ok"] == r["found"] and r["found"] > 0 and (r["expected"] is None or r["found"] == r["expected"]) for r in rows)
    none = all(r["ok"] == 0 for r in rows)
    return "ready" if full else ("missing" if none else "partly ready")


def readiness():
    print("# MS13 13a readiness (read-only; every listed file opened)")
    print("git", json.dumps(git_info()))
    for fig, specs in INPUTS.items():
        rows = []
        for sp in specs:
            r = check_spec(sp)
            r["label"] = sp["label"]
            rows.append(r)
        print(f"\n## {fig}: {verdict(rows)}")
        for r in rows:
            exp = "-" if r["expected"] is None else r["expected"]
            flag = "OK " if (r["ok"] == r["found"] and r["found"] > 0 and (r["expected"] is None or r["found"] == r["expected"])) else "BAD"
            print(f"  {flag} found {r['found']}, opened {r['ok']}, expected {exp}: {r['label']} {'; '.join(r['notes'])}")


TIMING = {   # figure -> families whose load is timed (largest files + stride sample)
    "F1": ["S5 headline mean-field record (P2, ref_devalle, 120 s)", "S8 network headline (T_ramp 10 and 120 s x 3 seeds)"],
    "F4": ["S5 ramp families (P1, P2, P5 x linear, sigmoid x 13 T_ramp; start distance; headline)", "S11 noise level (3 sigma x 4 T_ramp x 10 seeds)"],
    "F5": ["S7 map 1 (30 x 30, 120 s)", "S7 map 2 (25 x 13)", "S7 noisy subgrid (225 cells x 10 seeds)", "S8 network at 4 map cells (3 seeds)", "S9 finite size (4 N x 10 seeds)"],
    "F6": ["S6 P3 (3 I_amp x 4 T_ramp)", "S12 NC1 (13 T_ramp)", "S12 NC1 network (1 seed, 120 s)", "S12 NC2 (13 T_ramp)"],
    "FS3": ["S9 finite size", "S10 heterogeneity shape (3 shapes x 3 seeds)", "S11 noise level"],
    "FS4": ["S13 rtol ladder", "S13 floor level 0", "S13 MS11 network records (dt ladder, V_p, 18)"],
}


def load_npz(p):
    t0 = time.perf_counter()
    with np.load(p) as z:
        n = sum(z[k].nbytes for k in z.files)
    return time.perf_counter() - t0, n


def timing():
    print("# MS13 13a timing sample (read-only; full load of every array of each sampled npz)")
    print("git", json.dumps(git_info()))
    env = environment_info(with_julia=False)
    print("env", json.dumps({k: env[k] for k in ("python", "os", "cpu") if k in env}))
    print("note: first read of a file may come from disk, a repeat from the Windows file cache; each file is read once here (cold unless recently used)")
    specs = {s["label"]: s for fig in INPUTS.values() for s in fig}
    total_s = 0.0
    seen = set()
    per_fig = {}
    for fig, labels in TIMING.items():
        fig_est = 0.0
        print(f"\n## {fig}")
        for lab in labels:
            sp = specs[lab]
            items = [z for _, z in resolve(sp) if z.exists()]
            sizes = [z.stat().st_size for z in items]
            order = np.argsort(sizes)[::-1]
            pick = list(order[:5]) + list(range(0, len(items), max(1, len(items) // 15)))
            pick = list(dict.fromkeys(int(i) for i in pick))
            times, byt = [], []
            for i in pick:
                if items[i] in seen:      # a file loaded for an earlier figure is not read again here
                    continue
                dt, n = load_npz(items[i])
                seen.add(items[i])
                times.append(dt); byt.append(sizes[i]); total_s += dt
            if not times:
                print(f"  {lab}: all sampled files already loaded under an earlier figure")
                continue
            mean_s = float(np.mean(times)); mean_b = float(np.mean(byt))
            fam_mb = sum(sizes) / 1e6
            est = mean_s * len(items)
            fig_est += est
            big = int(order[0])
            print(f"  {lab}: {len(items)} npz, {fam_mb:.1f} MB; sampled {len(times)} files, mean {mean_s * 1e3:.1f} ms ({mean_b / 1e6:.2f} MB mean compressed), "
                  f"largest {sizes[big] / 1e6:.2f} MB; family load ESTIMATE {est:.1f} s")
        per_fig[fig] = fig_est
        print(f"  {fig} input load ESTIMATE (whole families, one read each): {fig_est:.1f} s")
    print("\n## tables")
    for p in ("A7/a7_ramp_metrics.parquet", "A9/a9_regime_map.parquet", "A9/a9_regime_map_v2.parquet", "A9/a9_subgrid_agreement.parquet", "A3/a3_sn_ramp.parquet", "A7/a7_s6_metrics.parquet",
              "A4/a4_hopf_curves.npz", "A5/a5_cycles.npz", "A6/a6_freq_map.npz", "A1/a1_fixedpoints_2d.npz", "A2/a2_ring_map.npz"):
        q = RES / p
        t0 = time.perf_counter()
        if q.suffix == ".parquet":
            pd.read_parquet(q)
        else:
            with np.load(q) as z:
                [z[k] for k in z.files]
        dt = time.perf_counter() - t0
        total_s += dt
        print(f"  {p}: {q.stat().st_size / 1e6:.2f} MB, {dt * 1e3:.1f} ms")
    print(f"\nTOTAL measured load time of the sampled files and tables: {total_s:.2f} s")
    print(f"SUM of the per-figure whole-family load ESTIMATES: {sum(per_fig.values()):.1f} s")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "readiness":
        readiness()
    elif mode == "timing":
        timing()
    else:
        raise SystemExit("usage: ms13_inputs.py readiness|timing")
