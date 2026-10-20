"""MS9 9e report: map-1 completion check, class counts, G5 facts, class grid, window extent, A9 labels and check (DL-236). Analysis only.

  report_ms9_9e.py [--out-dir results/ms9/9e]

Reads the 900 stored map-1 records (results/S7/S7_map1) and the launch journal; integrates nothing. Per record: the A4-region test of the run's
own path (M9-13: leading Re lambda > 0 somewhere along the path, a9.path_region) is made first and passed to the frozen classifier as
inside_a4_region (so label (f) is defined), then the A9 labels (a) to (f) are applied exactly as M9-12 (a9.labels). Facts only: no G5 verdict.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

from mprsurge import config as C
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import a9 as A9
from mprsurge.analysis import ms9_classify as MCL
from mprsurge.analysis import ms9_runlist as RL

SYM = {"D-tr": "T", "D-sus": "s", "D-none": ".", "failed": "F"}


def journal(path) -> dict:
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    log = Path(path).with_name("run.log").read_text(encoding="utf-8").splitlines()
    return {"manifest_rows": len(rows), "status": dict(collections.Counter(r["status"] for r in rows)),
            "unique_names": len({r["name"] for r in rows}), "launch_lines": sum("runs from" in x for x in log),
            "finished": [x.split("INFO ")[-1] for x in log if "finished:" in x]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="report_ms9_9e")
    ap.add_argument("--out-dir", default="results/ms9/9e")
    ap.add_argument("--root", default="results/S7/S7_map1")
    ap.add_argument("--journal", default="results/ms9/launch_map1/manifest.csv")
    args = ap.parse_args(argv)
    root = C.repo_root()
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    fi, gate = A7.frozen_inputs()
    h = fi["grid_step"]
    print(f"criteria gate ok: tag {gate['tag']}, threshold {fi['threshold']:.6f}")
    jr = journal(root / args.journal)
    print("journal:", json.dumps(jr))
    cells = [c for c in RL.load_cells() if c["kind"] == "map1"]
    d_axis = sorted({c["Delta"] for c in cells})
    t_axis = sorted({c["tau_d_ms"] for c in cells})
    by_ij = {tuple(c["ij"]): c for c in cells}
    files = MCL.record_files(root / args.root)
    print(f"records on disk: {len(files)}; cells {len(cells)}; Delta axis {len(d_axis)}, tau_d axis {len(t_axis)}")
    rows, git = [], collections.Counter()
    for jp in files:
        rec = json.loads(jp.read_text(encoding="utf-8"))
        cfg = rec["config"]
        git[(rec["git"]["commit"], rec["git"]["dirty"], rec["status"])] += 1
        D, td = cfg["model"]["Delta"], cfg["model"]["tau_d_ms"]
        i, j = next(k for k, c in by_ij.items() if abs(c["Delta"] - D) < 1e-12 and abs(c["tau_d_ms"] - td) < 1e-12)
        base = {"run": jp.stem, "i": i, "j": j, "Delta": D, "tau_d_ms": td, "status": rec["status"], "git_commit": rec["git"]["commit"],
                "git_dirty": rec["git"]["dirty"], "wall_time_s": rec["wall_time_s"]}
        if rec["status"] != "ok":
            rows.append({**base, "class": "failed", "surge": False, "inside_a4_region": "", "time_inside_s": "", "labels_all": "failed",
                         "label_primary": "failed", "label_f": False, "onset_s": "", "f_pk_hz": ""})
            continue
        inside, t_in = A9.path_region(cfg, h)
        r = MCL.classify_record(jp, fi, inside_a4_region=inside)
        m = cfg["model"]
        J0 = float(cfg["path"]["J0"])
        lab = A9.labels(r["class"], r["label_f"], A9.hopf_point(J0, D, td, m["tau_ms"]), A9.delta_max(J0, td, d_axis, m["tau_ms"]),
                        A9.taud_interval(J0, D, t_axis, m["tau_ms"]), D, td, t_in)
        rows.append({**base, "class": r["class"], "surge": r["surge"], "inside_a4_region": inside, "time_inside_s": t_in,
                     "labels_all": "".join(lab["all"]), "label_primary": lab["primary"] or "", "label_f": r["label_f"],
                     "onset_s": r["onset_s"], "f_pk_hz": r["f_pk_hz"]})
    rows.sort(key=lambda r: (r["i"], r["j"]))
    out = out_dir / "map1_classes.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"git/status of the records: {dict(git)}")
    cnt = collections.Counter(r["class"] for r in rows)
    print(f"records classified {len(rows)}; missing cells {len(cells) - len({(r['i'], r['j']) for r in rows})}")
    print("class counts:", {k: cnt.get(k, 0) for k in ("D-tr", "D-sus", "D-none", "failed")}, "other:", {k: v for k, v in cnt.items() if k not in SYM})
    ntr = cnt.get("D-tr", 0)
    print(f"G5 fact: surge class (D-tr) in {ntr} of {len(cells)} cells = {100 * ntr / len(cells):.2f}% ; 3% of 900 = 27")
    grid = {(r["i"], r["j"]): r["class"] for r in rows}
    print("\nclass grid (rows: Delta index i, ascending downwards; columns: tau_d index j, ascending to the right)")
    print("T = D-tr, s = D-sus, . = D-none, F = failed;  Delta axis", f"{d_axis[0]:.4g}..{d_axis[-1]:.4g}", " tau_d axis", f"{t_axis[0]:.4g}..{t_axis[-1]:.4g} ms")
    print("      " + "".join(str(j % 10) for j in range(len(t_axis))))
    for i in range(len(d_axis)):
        print(f"i={i:2d}  " + "".join(SYM.get(grid.get((i, j), ""), "?") for j in range(len(t_axis))) + f"   Delta={d_axis[i]:.4f}")
    tr = np.zeros((len(d_axis), len(t_axis)), bool)
    for (i, j), c in grid.items():
        tr[i, j] = c == "D-tr"
    if tr.any():
        ii, jj = np.where(tr)
        _, ncomp = ndimage.label(tr)
        print(f"\nD-tr extent: Delta index {ii.min()}..{ii.max()} ({d_axis[ii.min()]:.4f}..{d_axis[ii.max()]:.4f}, {ii.max() - ii.min() + 1} grid cells); "
              f"tau_d index {jj.min()}..{jj.max()} ({t_axis[jj.min()]:.4f}..{t_axis[jj.max()]:.4f} ms, {jj.max() - jj.min() + 1} grid cells)")
        print(f"bounding box {(ii.max() - ii.min() + 1) * (jj.max() - jj.min() + 1)} cells, D-tr cells in it {ntr}; 4-connected components {ncomp}")
        print("D-tr cells per Delta row:", {int(i): int(tr[i].sum()) for i in range(len(d_axis)) if tr[i].any()})
        print("D-tr cells per tau_d column:", {int(j): int(tr[:, j].sum()) for j in range(len(t_axis)) if tr[:, j].any()})
    non = [r for r in rows if not r["surge"]]
    prim = collections.Counter(r["label_primary"] or "none" for r in non)
    multi = sum(len(r["labels_all"]) > 1 for r in non if r["labels_all"] != "failed")
    unl = sum(1 for r in non if not r["label_primary"])
    anyc = collections.Counter(ch for r in non for ch in r["labels_all"] if r["labels_all"] != "failed")
    print(f"\nA9 labels over {len(non)} non-surge cells: primary {dict(sorted(prim.items()))}; several labels {multi}; unlabelled {unl}")
    print("A9 labels, any (not only primary):", dict(sorted(anyc.items())))
    print("combinations:", dict(collections.Counter(r["labels_all"] or "none" for r in non).most_common()))
    art = [r for r in rows if r["surge"] and r["inside_a4_region"] is not True]
    print(f"A9 check: surge-class cells {ntr}; without Re lambda > 0 along the path (ramp artefacts, M9-13): {len(art)}", [(r["i"], r["j"]) for r in art])
    print(f"\ncell (14, 12) (nearest to the headline, not the headline; Delta {d_axis[14]:.5f}, tau_d {t_axis[12]:.4f} ms): class {grid[(14, 12)]}; S5 headline: D-tr")
    print("launch wall from the journal:", jr["finished"], "; sum of per-run wall times", f"{sum(float(r['wall_time_s']) for r in rows):.0f} s")
    print(f"written {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
