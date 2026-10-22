"""MS9 9h: D31 boundary refinement, option B (DL-249 to DL-253). Analysis only: nothing integrates.

Supplementary cells OUTSIDE the frozen 1,226 (cell-list SHA-256 8e67bbd2... stays unchanged): every mixed 2x2 block of the map-1 D-tr / D-none
classes (a block of four neighbouring map-1 cells holding both classes) is fully halved. The half-spacing points of a block are the 5 new nodes of
its 3 x 3 lattice (4 edge midpoints and the centre), shared between blocks. Midpoints: Delta at the linear midpoint, tau_d at the geometric midpoint
(the map axes are linear in Delta and log in tau_d). Each new cell gets its own A4 Hopf scan for eta_H through the existing cell builder
(analysis.cells._cell, the code that built the 1,226); cells keep the fine-lattice index (p, q), p = 2 i + a, q = 2 j + b, with a new node having p or q odd.

The cells are stored in configs/ms9/runlists/cells_d31.csv (full-precision floats), as the 1,226 are in cells_1226.csv.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import numpy as np

from .. import config as C
from . import cells as CE

CELLS_D31_FILE = "configs/ms9/runlists/cells_d31.csv"
MAP1_CLASSES = "results/ms9/9e/map1_classes.csv"
_COLS = ("index", "name", "kind", "p", "q", "J0", "Delta", "tau_d_ms", "T_ramp_s", "hopf_found", "eta_H", "eta_start", "eta_peak")


def axes() -> tuple[np.ndarray, np.ndarray]:
    m1 = CE.load_spec()["map1"]
    return CE.axis(m1["Delta"]), CE.axis(m1["tau_d_ms"])


def mixed_blocks(grid) -> list[tuple[int, int]]:
    """Top-left corners (i, j) of the 2 x 2 blocks of neighbouring cells that hold more than one class; grid[i][j] is the class."""
    n, m = len(grid), len(grid[0])
    return [(i, j) for i in range(n - 1) for j in range(m - 1)
            if len({grid[i][j], grid[i + 1][j], grid[i][j + 1], grid[i + 1][j + 1]}) > 1]


def half_nodes(blocks) -> list[tuple[int, int]]:
    """Fine-lattice nodes (p, q) of the fully halved blocks that are not original map nodes (p or q odd), sorted, without duplicates."""
    s = {(2 * i + a, 2 * j + b) for i, j in blocks for a in range(3) for b in range(3)}
    return sorted(n for n in s if n[0] % 2 or n[1] % 2)


def node_values(p: int, q: int, D: np.ndarray, T: np.ndarray) -> tuple[float, float]:
    """Delta (linear midpoint) and tau_d (geometric midpoint) of fine-lattice node (p, q)."""
    i, j = p // 2, q // 2
    d = float(D[i]) if p % 2 == 0 else float((D[i] + D[i + 1]) / 2.0)
    t = float(T[j]) if q % 2 == 0 else float(np.sqrt(T[j] * T[j + 1]))
    return d, t


def read_map1_grid(path=None) -> list[list[str]]:
    p = Path(path) if path else C.repo_root() / MAP1_CLASSES
    with open(p, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    g = [["" for _ in range(30)] for _ in range(30)]
    for r in rows:
        g[int(r["i"])][int(r["j"])] = r["class"]
    return g


def build_d31_cells(nodes, J0=None, T_ramp_s=None, tau_ms: float = 10.0) -> list[dict]:
    """One cell per node through the existing cell builder (Hopf scan at the cell's own J0, Delta, tau_d)."""
    from . import hopf
    spec = CE.load_spec()
    m1 = spec["map1"]
    J0 = m1["J0"] if J0 is None else J0
    T_ramp_s = m1["T_ramp_s"] if T_ramp_s is None else T_ramp_s
    D, T = axes()
    eg = hopf._grid(hopf.load_a4_params()["grids"]["eta_bar"])
    eta_H_head, cache, out = CE.headline_eta_H(), {}, []
    for k, (p, q) in enumerate(nodes):
        d, t = node_values(p, q, D, T)
        out.append(CE._cell(k, f"d31_{p:02d}_{q:02d}", "map1_half", (p, q), J0, d, t, T_ramp_s, tau_ms, eg, eta_H_head, cache))
    return out


def write_cells_file(cells, path=None) -> str:
    path = Path(path) if path else C.repo_root() / CELLS_D31_FILE
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(_COLS)
        for c in cells:
            w.writerow([c["index"], c["name"], c["kind"], c["ij"][0], c["ij"][1], repr(c["J0"]), repr(c["Delta"]), repr(c["tau_d_ms"]),
                        repr(c["T_ramp_s"]), int(c["hopf_found"]), repr(c["eta_H"]), repr(c["eta_start"]), repr(c["eta_peak"])])
    return cells_file_sha256(path)


def cells_file_sha256(path=None) -> str:
    return hashlib.sha256(Path(path or C.repo_root() / CELLS_D31_FILE).read_bytes()).hexdigest()


def load_d31_cells(path=None) -> tuple:
    p = Path(path) if path else C.repo_root() / CELLS_D31_FILE
    out = []
    with open(p, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out.append({"index": int(r["index"]), "name": r["name"], "kind": r["kind"], "ij": [int(r["p"]), int(r["q"])], "J0": float(r["J0"]),
                        "Delta": float(r["Delta"]), "tau_d_ms": float(r["tau_d_ms"]), "T_ramp_s": float(r["T_ramp_s"]),
                        "hopf_found": bool(int(r["hopf_found"])), "eta_H": float(r["eta_H"]), "eta_start": float(r["eta_start"]),
                        "eta_peak": float(r["eta_peak"])})
    return tuple(out)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="python -m mprsurge.analysis.ms9_d31", description="write configs/ms9/runlists/cells_d31.csv (Hopf scans, slow)")
    ap.add_argument("--build-cells", action="store_true")
    args = ap.parse_args(argv)
    if args.build_cells:
        blocks = mixed_blocks(read_map1_grid())
        nodes = half_nodes(blocks)
        print(f"{len(blocks)} mixed blocks, {len(nodes)} new nodes")
        print("cells_d31.csv SHA-256", write_cells_file(build_d31_cells(nodes)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
