"""MS9 9h report: D31 boundary refinement (option B) facts and the post-hoc view P-1 (DL-249 to DL-253). Analysis only: integrates nothing, feeds no gate.
Facts only; the D31 verdict is the reviewer's.

  report_ms9_9h.py [--out-dir results/ms9/9h] [--p1-only]

Part 1 launch completion of the D31_half list (records in results/D31/D31_half, journal results/ms9/launch_9h): ok/failed, commit and git.dirty.
Part 2 D31: each new node classified exactly as map 1 (frozen classifier; A4-region test of the run's own path passed in, as 9e); class at every new node.
        Definition of "the boundary" (UNVERIFIED, reading ours): the boundary is the set of edges between 4-neighbouring nodes of different class, each
        placed at its edge midpoint, in units of one original map-1 cell (node (p, q) of the half-spacing lattice sits at (p / 2, q / 2)). Coarse boundary =
        edges between neighbouring original cells; refined boundary = half-edges between neighbouring nodes of the 3 x 3 lattice of the mixed blocks.
        "The boundary moves by less than one cell" at a boundary-touching cell (an original cell with a 4-neighbour of the other class; 62 cells) is read
        as: every coarse boundary edge of that cell has a refined boundary half-edge midpoint within Euclidean distance < 1 cell. Also reported: the largest
        distance from a refined half-edge midpoint to the nearest coarse edge midpoint, and the refined half-edges with none within 1 cell.
Part 3 P-1 (POST HOC, from the stored subgrid and control classes, no simulation, feeds no gate, frozen D24 unchanged beside it): ramp-linked =
        S+, S-abs, S-sus; not ramp-linked = NS, S-rel. (i) per deterministic class the fraction of ramp-linked runs, subgrid against control; (ii) cell
        agreement with D-tr matched to ramp-linked and D-none to not ramp-linked, cell class = the modal of the two categories over the 10 seeds (a 5/5 tie
        = disagreement), against 203 of 225; per-run agreement.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

from mprsurge import config as C
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import a9 as A9
from mprsurge.analysis import ms9_classify as MCL
from mprsurge.analysis import ms9_d31 as D31

RAMP_LINKED = ("S+", "S-abs", "S-sus")
NEEDED = 203


def sha(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def edges(cls: dict, step: int) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Boundary edges: neighbouring nodes (distance `step` on the fine lattice, along an axis) present in cls with different class."""
    out = []
    for (p, q), c in cls.items():
        for dp, dq in ((step, 0), (0, step)):
            n = (p + dp, q + dq)
            if n in cls and cls[n] != c:
                out.append(((p, q), n))
    return out


def mid(e) -> tuple[float, float]:
    (p0, q0), (p1, q1) = e
    return ((p0 + p1) / 4.0, (q0 + q1) / 4.0)             # fine-lattice units are half cells: node (p, q) is at (p / 2, q / 2)


def dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def d31_geometry(coarse: dict, fine: dict) -> dict:
    """coarse: {(i, j): class} of the 900 cells; fine: {(p, q): class} on the half lattice (originals at even, even, and the new nodes)."""
    cc = {(2 * i, 2 * j): c for (i, j), c in coarse.items()}
    ce = edges(cc, 2)
    fe = edges(fine, 1)
    cm = [mid(e) for e in ce]
    fm = [mid(e) for e in fe]
    touching = sorted({(p // 2, q // 2) for e in ce for (p, q) in e})
    per = []
    for cell in touching:
        own = [mid(e) for e in ce if any((p // 2, q // 2) == cell for (p, q) in e)]
        dd = [min((dist(m, f) for f in fm), default=float("inf")) for m in own]
        per.append({"i": cell[0], "j": cell[1], "coarse_edges": len(own), "max_dist_to_refined": max(dd), "moves_less_than_one": max(dd) < 1.0})
    stray = [(f, min(dist(f, m) for m in cm)) for f in fm]
    return {"coarse_edges": len(ce), "refined_half_edges": len(fe), "touching": len(touching), "per_cell": per,
            "refined_far_from_coarse": [(f, d) for f, d in stray if d >= 1.0], "max_refined_to_coarse": max((d for _, d in stray), default=0.0)}


def part1(root: Path, journal: Path) -> list[Path]:
    files = MCL.record_files(root / "results/D31/D31_half")
    st, git = collections.Counter(), collections.Counter()
    for jp in files:
        rec = json.loads(jp.read_text(encoding="utf-8"))
        st[rec["status"]] += 1
        git[(rec["git"]["commit"][:7], rec["git"]["dirty"])] += 1
    print(f"records on disk {len(files)}; status {dict(st)}; (commit, git.dirty) {dict(git)}")
    if journal.exists():
        rows = read(journal)
        log = journal.with_name("run.log").read_text(encoding="utf-8").splitlines()
        print(f"journal: {len(rows)} rows, {dict(collections.Counter(r['status'] for r in rows))}; launches {sum('runs from' in x for x in log)}; "
              + "; ".join(x.split("INFO ")[-1] for x in log if "finished:" in x))
    return files


def part2(root: Path, files, fi, out_dir: Path) -> None:
    cells = {tuple(c["ij"]): c for c in D31.load_d31_cells()}
    by_node = {(round(c["Delta"], 12), round(c["tau_d_ms"], 12)): k for k, c in cells.items()}
    h = fi["grid_step"]
    rows = []
    for jp in files:
        rec = json.loads(jp.read_text(encoding="utf-8"))
        cfg = rec["config"]
        node = by_node[(round(cfg["model"]["Delta"], 12), round(cfg["model"]["tau_d_ms"], 12))]
        base = {"run": jp.stem, "p": node[0], "q": node[1], "Delta": cfg["model"]["Delta"], "tau_d_ms": cfg["model"]["tau_d_ms"],
                "hopf_found": cells[node]["hopf_found"], "eta_H": cells[node]["eta_H"], "status": rec["status"]}
        if rec["status"] != "ok":
            rows.append({**base, "class": "failed", "reason": rec["status"]})
            continue
        inside, _ = A9.path_region(cfg, h)
        r = MCL.classify_record(jp, fi, inside_a4_region=inside)
        rows.append({**base, "class": r["class"], "reason": r["reason"]})
    rows.sort(key=lambda r: (r["p"], r["q"]))
    write_csv(out_dir / "d31_classes.csv", rows)
    cnt = collections.Counter(r["class"] for r in rows)
    print(f"D31 nodes classified {len(rows)} (cells file {len(cells)}); classes {dict(cnt)}; no Hopf point (eta_H from the headline, CP20) at "
          f"{sum(not r['hopf_found'] for r in rows)} nodes")
    coarse = {(int(r["i"]), int(r["j"])): r["class"] for r in read(root / D31.MAP1_CLASSES)}
    fine = {(2 * i, 2 * j): c for (i, j), c in coarse.items()}
    fine.update({(r["p"], r["q"]): r["class"] for r in rows})
    kinds = {"edge midpoint in Delta (p odd, q even)": lambda p, q: p % 2 and not q % 2,
             "edge midpoint in tau_d (p even, q odd)": lambda p, q: q % 2 and not p % 2, "block centre (both odd)": lambda p, q: p % 2 and q % 2}
    for name, f in kinds.items():
        print(f"  {name}: {dict(collections.Counter(r['class'] for r in rows if f(r['p'], r['q'])))}")
    print("\nclass at each new node (p, q: fine-lattice index, node at (p/2, q/2) in map-1 cell units; Delta, tau_d ms):")
    for r in rows:
        print(f"  ({r['p']:2d},{r['q']:2d})  Delta {r['Delta']:.6f}  tau_d {r['tau_d_ms']:8.4f}  {r['class']:7s} hopf {int(bool(r['hopf_found']))}")
    g = d31_geometry(coarse, fine)
    print(f"\ncoarse boundary edges {g['coarse_edges']}; boundary-touching cells {g['touching']}; refined boundary half-edges {g['refined_half_edges']}")
    per = g["per_cell"]
    write_csv(out_dir / "d31_boundary_cells.csv", per)
    n_lt = sum(r["moves_less_than_one"] for r in per)
    ds = sorted(r["max_dist_to_refined"] for r in per)
    print(f"cells whose boundary moves by less than one original cell: {n_lt} of {len(per)}; max of the per-cell maximum distance {ds[-1]:.4f}, "
          f"median {ds[len(ds) // 2]:.4f}")
    print("distance distribution (per-cell maximum, cells):", dict(sorted(collections.Counter(round(d, 4) for d in ds).items())))
    print(f"refined half-edges with no coarse boundary edge within 1 cell: {len(g['refined_far_from_coarse'])}; largest refined-to-coarse distance "
          f"{g['max_refined_to_coarse']:.4f}")
    for f, d in g["refined_far_from_coarse"]:
        print(f"    half-edge midpoint {f} distance {d:.4f}")
    for r in [r for r in per if not r["moves_less_than_one"]]:
        print(f"    cell ({r['i']},{r['j']}) max distance {r['max_dist_to_refined']:.4f} (not < 1)")


def cat2(c: str) -> str:
    return "linked" if c in RAMP_LINKED else "not"


def part3(root: Path, out_dir: Path, sub_csv: str, ctrl_csv: str) -> None:
    sub, ctrl = read(root / sub_csv), read(root / ctrl_csv)
    print(f"\nP-1 (POST HOC, no simulation, feeds no gate; frozen D24 FAILED stays: 97 of 225 raw, 118 of 225 on categories, {NEEDED} needed)")
    print("ramp-linked = S+, S-abs, S-sus; not ramp-linked = NS, S-rel. Input hashes: subgrid_classes", sha(root / sub_csv)[:8],
          " control_classes", sha(root / ctrl_csv)[:8])
    print("(i) fraction of ramp-linked runs by deterministic class:")
    for det in ("D-tr", "D-none"):
        parts = []
        for nm, rows in (("subgrid", sub), ("control", ctrl)):
            sel = [r for r in rows if r["det"] == det]
            k = sum(r["class"] in RAMP_LINKED for r in sel)
            parts.append(f"{nm} {k}/{len(sel)} = {100 * k / len(sel):.2f}% ({len({(r['i'], r['j']) for r in sel})} cells)")
        print(f"  {det}: " + "; ".join(parts))
    print("(ii) agreement, D-tr matched to ramp-linked, D-none to not ramp-linked:")
    cells = collections.defaultdict(list)
    for r in sub:
        cells[(int(r["i"]), int(r["j"]), r["det"])].append(cat2(r["class"]))
    agree, ties, rows = 0, 0, []
    for (i, j, det), cl in sorted(cells.items()):
        c = collections.Counter(cl)
        top = max(c.values())
        modal = [k for k, v in c.items() if v == top]
        tie = len(modal) > 1
        ok = (not tie) and modal[0] == ("linked" if det == "D-tr" else "not")
        agree += ok
        ties += tie
        rows.append({"i": i, "j": j, "det": det, "linked": c.get("linked", 0), "not": c.get("not", 0), "tie": tie, "cell_agrees": ok})
    write_csv(out_dir / "p1_cells.csv", rows)
    print(f"  cell agreement {agree} of {len(cells)} ({100 * agree / len(cells):.1f}%) against {NEEDED}; ties {ties}")
    for det in ("D-tr", "D-none"):
        sel = [r for r in rows if r["det"] == det]
        print(f"    {det}: {sum(r['cell_agrees'] for r in sel)} of {len(sel)} cells agree")
    pr = sum((cat2(r["class"]) == "linked") == (r["det"] == "D-tr") for r in sub)
    print(f"  per-run agreement {pr} of {len(sub)} ({100 * pr / len(sub):.1f}%)")
    for det in ("D-tr", "D-none"):
        sel = [r for r in sub if r["det"] == det]
        k = sum((cat2(r["class"]) == "linked") == (det == "D-tr") for r in sel)
        print(f"    {det}: {k} of {len(sel)} runs")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="report_ms9_9h")
    ap.add_argument("--out-dir", default="results/ms9/9h")
    ap.add_argument("--journal", default="results/ms9/launch_9h/manifest.csv")
    ap.add_argument("--sub-csv", default="results/ms9/9f/subgrid_classes.csv")
    ap.add_argument("--ctrl-csv", default="results/ms9/9g/control_classes.csv")
    ap.add_argument("--p1-only", action="store_true")
    args = ap.parse_args(argv)
    root = C.repo_root()
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    fi, gate = A7.frozen_inputs()
    print(f"criteria gate ok: tag {gate['tag']}, threshold {fi['threshold']:.6f}")
    if not args.p1_only:
        files = part1(root, root / args.journal)
        print("cells_d31.csv", D31.cells_file_sha256()[:8], " map1_classes.csv", sha(root / D31.MAP1_CLASSES)[:8])
        part2(root, files, fi, out_dir)
    part3(root, out_dir, args.sub_csv, args.ctrl_csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
