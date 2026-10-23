"""MS10 run counts, timing-gate prediction and proposed seed keys (10a; plan Table 6.2 S8, S9, S10, Table 9.1, 9.2, D36).

Analysis only: counts runs from the plan wording, converts them to neuron-updates (P2: discard 2 s + baseline 5 s + 1.25 T_ramp + hold 10 s,
dt 1e-3 tau) and does the 9.2 arithmetic against network timing cells. Nothing integrates. Where the plan gives no number the readings are
listed in OPTIONS and none is chosen (open choices M10-n, docs/ms10_plan.md). The seed keys are PROPOSED (DL-275), UNVERIFIED until the
reviewer confirms them. Reuses the MS5 5f timing conventions (per-run median under n concurrent copies, divisor n; DL-102 to DL-105, DL-118).

  .venv/Scripts/python.exe -m mprsurge.analysis.ms10_counts --timing-dir results/timing/ms10 [--seeds-per-cell 3] [--control-seeds 3]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from . import timing as T

S8_HEADLINE_T_RAMP_S = (10.0, 120.0)        # Table 6.2 S8
S8_HEADLINE_SEEDS = 3                       # Table 6.2 S8
S8_MAP_CELLS, S8_MAP_T_RAMP_S = 4, 30.0     # Table 6.2 S8 ("4 map cells at T_ramp 30 s"; seeds per cell: not in the plan, M10-2)
S9_N = (1000, 3000, 10000, 30000)           # Table 6.2 S9
S9_SEEDS, S9_T_RAMP_S = 10, 60.0
S10_SHAPES = ("lorentzian", "gaussian", "uniform")
S10_SEEDS, S10_T_RAMP_S, S10_N = 3, 60.0, 10000
N_REF = 10000
WORKERS = (6, 8, 10)                        # 9.2 step 1
CELL_OF_N = {1000: "net_1e3", 3000: "net_3e3", 10000: "net_1e4", 30000: "net_3e4"}

# Readings the plan leaves open (none chosen). Each value lists the readings whose count consequence docs/ms10_plan.md shows.
OPTIONS = {
    "M10-2_seeds_per_map_cell": (1, 3, 10),
    "M10-9_s9_n1e4_shared_with_s10_lorentzian": (False, True),
    "M10-8_control_scope": ("C0_none_new", "C1_headline_N1e4", "C2_every_configuration", "C3_twin_of_every_ramp_run"),
    "M10-8_control_seeds": (3, 10),
}

# Proposed spawn keys (DL-275, UNVERIFIED): first element 10 = MS10 (DL-141 convention), root_seed 20261008. Used keys: tests/test_ms9_seed_keys.py.
SEED_KEY_PREFIXES = {
    "s8_headline": (10, 1),     # [10, 1, s], s = 0..2: S8 P2 headline, the same stream at T_ramp 10 and 120 s (initial V only; q_j is deterministic)
    "s8_map_cells": (10, 2),    # [10, 2, c, s], c = 0..3 map cell, s = 0..9 (the count per cell is M10-2; keys reserved for the maximum)
    "s9_finite_size": (10, 3),  # [10, 3, n, s], n = 0..3 index into S9_N, s = 0..9
    "s10_shapes": (10, 4),      # [10, 4, l, s], l = 0..2 index into S10_SHAPES, s = 0..2
    "controls": (10, 5),        # [10, 5, k, s], k = 0..15 control configuration (M10-8), s = 0..9; reserved, used only if a control is ruled
}
N_CONTROL_CONFIGS = 16


def proposed_seed_keys() -> list[tuple[int, ...]]:
    P = SEED_KEY_PREFIXES
    keys = [P["s8_headline"] + (s,) for s in range(S8_HEADLINE_SEEDS)]
    keys += [P["s8_map_cells"] + (c, s) for c in range(S8_MAP_CELLS) for s in range(10)]
    keys += [P["s9_finite_size"] + (n, s) for n in range(len(S9_N)) for s in range(S9_SEEDS)]
    keys += [P["s10_shapes"] + (l, s) for l in range(len(S10_SHAPES)) for s in range(S10_SEEDS)]
    keys += [P["controls"] + (k, s) for k in range(N_CONTROL_CONFIGS) for s in range(10)]
    return keys


# --- run lists: (label, N, T_ramp_s, n_runs) ----------------------------------------------------------------------------------------------

def s8_runs(seeds_per_cell: int = 3) -> list[tuple]:
    return ([("S8 headline", N_REF, t, S8_HEADLINE_SEEDS) for t in S8_HEADLINE_T_RAMP_S]
            + [("S8 map cells", N_REF, S8_MAP_T_RAMP_S, S8_MAP_CELLS * seeds_per_cell)])


def s9_runs() -> list[tuple]:
    return [("S9", n, S9_T_RAMP_S, S9_SEEDS) for n in S9_N]


def s10_runs(shared_with_s9: bool = False) -> list[tuple]:
    """Lorentzian x 3 seeds is the same configuration as S9 N = 1e4 (P2, 60 s); shared drops those runs here (M10-9)."""
    n_shapes = len(S10_SHAPES) - (1 if shared_with_s9 else 0)
    return [("S10", S10_N, S10_T_RAMP_S, n_shapes * S10_SEEDS)]


def control_configs() -> list[tuple]:
    """Distinct network configurations used for class reading (DL-231): (label, N, T_ramp_s). The start state is the headline's except the
    four map cells, each at its own start state. 12 configurations."""
    c = [(f"headline N={N_REF} T{t:g}", N_REF, t) for t in (10.0, S9_T_RAMP_S, 120.0)]
    c += [(f"headline N={n} T60", n, S9_T_RAMP_S) for n in S9_N if n != N_REF]
    c += [(f"headline {s} N=1e4 T60", S10_N, S10_T_RAMP_S) for s in S10_SHAPES[1:]]
    c += [(f"map cell {k} N=1e4 T30", N_REF, S8_MAP_T_RAMP_S) for k in range(S8_MAP_CELLS)]
    return c


def control_runs(scope: str, seeds: int, ramp_runs: list[tuple]) -> list[tuple]:
    if scope == "C0_none_new":
        return []
    if scope == "C1_headline_N1e4":
        return [(f"control {l}", N, t, seeds) for l, N, t in control_configs()[:3]]
    if scope == "C2_every_configuration":
        return [(f"control {l}", N, t, seeds) for l, N, t in control_configs()]
    if scope == "C3_twin_of_every_ramp_run":
        return [(f"twin of {l}", N, t, n) for l, N, t, n in ramp_runs]
    raise ValueError(scope)


def updates(N: float, T_ramp_s: float) -> float:
    return T.p2_updates(N, T_ramp_s)


def total_updates(runs: list[tuple]) -> float:
    return sum(n * updates(N, t) for _, N, t, n in runs)


def n_runs(runs: list[tuple]) -> int:
    return sum(r[3] for r in runs)


# --- prediction (9.2 step 2): sum of N T / dt x s per update / workers, bounded below by the longest run --------------------------------------

def predict_s(runs: list[tuple], rate: dict, workers: int) -> dict:
    """rate: {N: s per update under `workers` concurrent copies}. Returns the wall, the sum of run walls and the longest run (s)."""
    walls = [(n, updates(N, t) * rate[N]) for _, N, t, n in runs]
    total = sum(n * w for n, w in walls)
    longest = max((w for n, w in walls if n), default=0.0)
    return {"wall_s": max(total / workers, longest), "sum_s": total, "longest_s": longest}


def rates(timing_dir, workers: int | None) -> dict:
    """{N: s per neuron-update}: the per-run median of the cell under `workers` copies (None: alone, median of the repeats)."""
    cells = T.load_cells(timing_dir, list(CELL_OF_N.values()), workers=workers)
    out = {}
    for N, c in CELL_OF_N.items():
        if c in cells:
            out[N] = cells[c]["wall_s"] / (N * cells[c]["tau"] / 1e-3)
    return out


def fmt(s: float) -> str:
    return f"{s:.0f} s" if s < 120 else (f"{s / 60:.1f} min" if s < 7200 else f"{s / 3600:.2f} h")


def report(timing_dir, seeds_per_cell: int = 3, control_seeds: int = 3) -> str:
    L = []
    ramp = {"S8": s8_runs(seeds_per_cell), "S9": s9_runs(), "S10": s10_runs(False)}
    for w in WORKERS:
        r = rates(timing_dir, w)
        if len(r) < 4:
            L.append(f"workers {w}: cells missing ({sorted(r)})")
            continue
        L.append(f"--- {w} workers (rate = per-run median under {w} copies) ---")
        for k, runs in ramp.items():
            p = predict_s(runs, r, w)
            L.append(f"{k}: {n_runs(runs)} runs, {total_updates(runs):.3e} updates, wall {fmt(p['wall_s'])} "
                     f"(sum {fmt(p['sum_s'])}, longest {fmt(p['longest_s'])})")
        for sc in OPTIONS["M10-8_control_scope"]:
            runs = control_runs(sc, control_seeds, ramp["S8"] + ramp["S9"] + ramp["S10"])
            p = predict_s(runs, r, w)
            L.append(f"control {sc} ({control_seeds} seeds): {n_runs(runs)} runs, {total_updates(runs):.3e} updates, wall {fmt(p['wall_s'])}")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--timing-dir", default="results/timing/ms10")
    ap.add_argument("--seeds-per-cell", type=int, default=3)
    ap.add_argument("--control-seeds", type=int, default=3)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    txt = report(a.timing_dir, a.seeds_per_cell, a.control_seeds)
    print(txt)
    if a.out:
        Path(a.out).write_text(txt + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
