"""MS9 9h: D31 option B list (178 nodes outside the frozen 1,226), block/node logic, report geometry. Nothing integrates."""
import math
import sys
from pathlib import Path

import pytest

from mprsurge.analysis import ms9_d31 as D31
from mprsurge.analysis import ms9_runlist as RL

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import report_ms9_9h as R  # noqa: E402


def test_blocks_and_nodes_on_a_toy_grid():
    g = [["a", "a", "a"], ["a", "b", "b"], ["a", "b", "b"]]
    assert D31.mixed_blocks(g) == [(0, 0), (0, 1), (1, 0)]
    n = D31.half_nodes([(0, 0)])
    assert len(n) == 5 and {(1, 1), (0, 1), (2, 1), (1, 0), (1, 2)} == set(n)
    assert len(D31.half_nodes([(0, 0), (0, 1)])) == 9              # 5 + 5 nodes, the shared edge midpoint (1, 2) counted once


def test_midpoints_linear_in_delta_geometric_in_tau_d():
    D, T = D31.axes()
    d, t = D31.node_values(1, 1, D, T)
    assert d == pytest.approx((D[0] + D[1]) / 2) and t == pytest.approx(math.sqrt(T[0] * T[1]))
    assert D31.node_values(2, 4, D, T) == (D[1], T[2])


def test_cells_file_178_nodes_outside_the_frozen_cells():
    cs = D31.load_d31_cells()
    assert len(cs) == 178 and all(c["kind"] == "map1_half" for c in cs)
    assert all(c["ij"][0] % 2 or c["ij"][1] % 2 for c in cs)
    key = lambda c: (round(c["Delta"], 12), round(c["tau_d_ms"], 12))   # noqa: E731
    assert not {key(c) for c in RL.load_cells()} & {key(c) for c in cs}
    assert len({key(c) for c in cs}) == 178
    assert RL.FROZEN_CELL_LIST_SHA256.startswith("8e67bbd2") and len(RL.load_cells()) == 1226


def test_list_is_exploratory_and_disjoint():
    rows = RL.expand("D31_half")
    assert len(rows) == 178 and all(not r["pre_registered"] and r["spawn_key"] is None for r in rows)
    assert len({r["hash"] for r in rows}) == 178
    other = {r["hash"] for n in RL.PRE_REGISTERED + RL.SUPPLEMENTARY + RL.EXPLORATORY + RL.EXPLORATORY_9G for r in RL.expand(n)}
    assert not {r["hash"] for r in rows} & other


def test_geometry_toy():
    coarse = {(i, j): ("x" if j < 1 else "y") for i in range(2) for j in range(2)}     # boundary between columns 0 and 1
    fine = {(2 * i, 2 * j): c for (i, j), c in coarse.items()}
    fine.update({(0, 1): "x", (2, 1): "x", (1, 1): "x", (1, 0): "x", (1, 2): "y"})
    g = R.d31_geometry(coarse, fine)
    assert g["coarse_edges"] == 2 and g["touching"] == 4
    assert all(r["moves_less_than_one"] for r in g["per_cell"])
