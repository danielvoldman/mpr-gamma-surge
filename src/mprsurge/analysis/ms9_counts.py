"""MS9 run counts, timing-gate prediction inputs and proposed seed keys (9a; plan Table 6.2 S6, S7, S12, S16, Table 9.1, 9.2, 9.3).

Analysis only: counts runs from the plan wording, converts them to tau simulated and Heun steps, and does the 9.2 arithmetic against
timing cells. Nothing integrates. Where the plan leaves a count open, OPTIONS lists the readings; DEFAULTS is the reading recommended in
docs/ms9_plan.md (a ruling is still needed for each, UNVERIFIED; nothing is chosen). The seed keys are PROPOSED (DL-210), UNVERIFIED
until the owner confirms them. Reuses the MS8 arithmetic (durations, longest-first schedule, disk and memory estimates).
"""
from __future__ import annotations

import numpy as np

from .. import config as C
from ..units import s_to_tau
from . import cells as CE
from . import ms8_counts as M8
from . import timing as T

HEADLINE_T_RAMP_S = M8.HEADLINE_T_RAMP_S
S6_T_RAMP_S = (10.0, 30.0, 120.0, 300.0)            # Table 6.2 S6 (not the 10^(k/4) grid values except 10)
P3_AMPLITUDES = (0.5, 1.0, 2.0)                     # Table 6.2 S6, 4.4 P3, D15
P4A_FACTOR, P4B_FACTOR = 1.5, 2.0 / 3.0             # 4.4 P4a, P4b
N_SEEDS = 10
MAP1_SHAPE, SUBGRID_SHAPE = (30, 30), (15, 15)      # Table 6.2 S7
N_ONE_AT_A_TIME, N_LHS = 14, 64                     # Table 6.2 S16, Table 7.2 RB4
N_NC_MAP_CELLS = 5                                  # Table 6.2 S12
RB4_PARAMETERS = ("eta_start", "eta_peak", "J0", "Delta", "tau_d_ms", "J_lag_frac", "J_T_frac")
G5_MIN_FRACTION, RB4_LHS_MIN_FRACTION, RB4_OAT_MAX_CHANGES = 0.03, 0.80, 2     # Table 11.2 G5, Table 7.2 RB4 (frozen file)

# Each key is a plan wording that leaves a count open. First entry of each tuple is the recommended reading (docs/ms9_plan.md).
OPTIONS = {
    "nc1_map_cells_T_ramp": ("T120", "grid13"),         # "NC1 at 5 map cells": T_ramp 120 s (map-1 value), or all 13 T_ramp
    "nc2_amplitudes": ("I_amp_1", "all_three"),         # "I(t) on": I_amp 1 (D15 default) or all of {0.5, 1, 2}
    "nc3_J_timing": ("simultaneous", "p2_lag"),         # inhibition raised while eta falls: from t_on over T_ramp, or P2 timing (lag 0.25 T)
}
DEFAULTS = {k: v[0] for k, v in OPTIONS.items()}

# Proposed spawn keys (DL-210, UNVERIFIED): first element 9 = MS9 (DL-141 convention), root_seed 20261008. Used keys are in tests/test_ms9_seed_keys.py.
SEED_KEY_PREFIXES = {
    "s7_noisy_subgrid": (9, 1),     # [9, 1, s], s = 0..9: mode-N seed s of every subgrid cell (same stream per cell, DL-069 convention)
    "s12_nc1_network": (9, 2),      # [9, 2, 0]: the NC1 network run, 1 seed
    "s12_nc_mode_n": (9, 3),        # [9, 3, s]: reserved, confirmed (M9-21) and unused
    "s12x_nc1_net_seeds": (9, 5),   # [9, 5, s], s = 0..8: S12x EXPLORATORY, NC1 network at nine more seeds (9c); the original [9, 2, 0] is the 10th
    "s12x_const_net": (9, 6),       # [9, 6, s], s = 0..9: S12x EXPLORATORY, the network held at the NC1 start state (9c)
    "s12_nc1_mode_n_supp": (9, 4),  # [9, 4, s]: SUPPLEMENTARY NC1 in mode N (M9-4, 9b), same stream at every T_ramp, outside the pre-registered counts
}


def proposed_seed_keys(include_reserved: bool = True) -> list[tuple[int, ...]]:
    keys = [SEED_KEY_PREFIXES["s7_noisy_subgrid"] + (s,) for s in range(N_SEEDS)]
    keys.append(SEED_KEY_PREFIXES["s12_nc1_network"] + (0,))
    keys += [SEED_KEY_PREFIXES["s12_nc1_mode_n_supp"] + (s,) for s in range(N_SEEDS)]
    if include_reserved:
        keys += [SEED_KEY_PREFIXES["s12_nc_mode_n"] + (s,) for s in range(N_SEEDS)]
    return keys


def exploratory_seed_keys() -> list[tuple[int, ...]]:
    """S12x (9c) keys, kept apart from proposed_seed_keys: exploratory, outside the pre-registered lists, UNVERIFIED until confirmed."""
    return ([SEED_KEY_PREFIXES["s12x_nc1_net_seeds"] + (s,) for s in range(9)]
            + [SEED_KEY_PREFIXES["s12x_const_net"] + (s,) for s in range(N_SEEDS)])


def subgrid_indices(n: int = 30, m: int = 15) -> np.ndarray:
    """Reading (b) of M9-6: m indices of an n-point axis at round(linspace(0, n - 1, m)); both ends, steps 2 and one step 3."""
    return np.round(np.linspace(0, n - 1, m)).astype(int)


def lhs_pass_count(n: int = N_LHS, frac: float = RB4_LHS_MIN_FRACTION) -> int:
    """Smallest number of unchanged-class points with fraction >= frac (80 percent of 64 = 51.2, so 52; arithmetic ours)."""
    return int(np.ceil(frac * n - 1e-12))


def g5_min_cells(n_cells: int = 900, frac: float = G5_MIN_FRACTION) -> int:
    return int(np.ceil(frac * n_cells - 1e-12))


# --- durations and runs -----------------------------------------------------------------------

def _run(family, path, T, mode="D", **kw) -> dict:
    d = {"family": family, "path": path, "T_ramp_s": float(T), "mode": mode,
         "kept_s": M8.run_duration_s(path, T), "tau": s_to_tau(M8.run_integrated_s(path, T, mode)),
         "dt_tau": None, "n_seeds": 1, "kind": "mf"}
    d.update(kw)
    return d


def s6_runs() -> list[dict]:
    """S6: P3 x I_amp {0.5, 1, 2}, P4a, P4b, each x T_ramp {10, 30, 120, 300}; P2-based, so last ramp end 1.25 T (CP14). Mode D."""
    runs = [_run("S6_P3", "path_hypoxia", T, I_amp=a) for a in P3_AMPLITUDES for T in S6_T_RAMP_S]
    runs += [_run("S6_P4a", "path_hypoxia", T, Delta_factor=P4A_FACTOR) for T in S6_T_RAMP_S]
    runs += [_run("S6_P4b", "path_hypoxia", T, Delta_factor=P4B_FACTOR) for T in S6_T_RAMP_S]
    return runs


def s7_map1_runs() -> list[dict]:
    return [_run("S7_map1", "path_hypoxia", HEADLINE_T_RAMP_S, cell=i) for i in range(MAP1_SHAPE[0] * MAP1_SHAPE[1])]


def s7_map2_runs() -> list[dict]:
    spec = CE.load_spec()["map2"]
    n_j = int(spec["J0"]["n"])
    return [_run("S7_map2", "path_hypoxia", T, J0_index=k) for k in range(n_j) for T in M8.t_ramp_grid()]


def s7_subgrid_runs() -> list[dict]:
    """225 cells x 10 seeds, mode N, P2 at T_ramp 120 s, stochastic Heun dt 1e-3 tau, 2 s discard (adds to the 5 + 165 s record)."""
    return [_run("S7_noisy", "path_hypoxia", HEADLINE_T_RAMP_S, mode="N", kind="mf_noisy", dt_tau=1.0e-3, n_seeds=N_SEEDS, cell=c, seed=s)
            for c in range(SUBGRID_SHAPE[0] * SUBGRID_SHAPE[1]) for s in range(N_SEEDS)]


def s12_runs(opts=None) -> list[dict]:
    """S12 mean field: NC1 and NC3 x 13 T_ramp (eta-only duration for NC1), NC2 (P3 with I on; the I = 0 side is the S5 P2 run),
    NC1 at 5 map cells."""
    o = {**DEFAULTS, **(opts or {})}
    grid = M8.t_ramp_grid()
    runs = [_run("S12_NC1", "path_eta", T) for T in grid]
    amps = P3_AMPLITUDES if o["nc2_amplitudes"] == "all_three" else (1.0,)
    runs += [_run("S12_NC2", "path_hypoxia", T, I_amp=a) for a in amps for T in grid]
    nc3_path = "path_hypoxia" if o["nc3_J_timing"] == "p2_lag" else "path_eta"      # simultaneous: last ramp end = T_ramp
    runs += [_run("S12_NC3", nc3_path, T) for T in grid]
    Ts = grid if o["nc1_map_cells_T_ramp"] == "grid13" else [HEADLINE_T_RAMP_S]
    runs += [_run("S12_NC1_cells", "path_eta", T, cell=c) for c in range(N_NC_MAP_CELLS) for T in Ts]
    return runs


def s12_network_runs() -> list[dict]:
    """NC1 network, N = 1e4, one seed, T_ramp 120 s: discard 2 s + 5 s + 120 s + 10 s, dt 1e-3 tau."""
    r = _run("S12_NC1_net", "path_eta", HEADLINE_T_RAMP_S, mode="N", kind="network", dt_tau=1.0e-3, N=10000)
    r["updates"] = 10000 * r["tau"] / 1.0e-3                 # neuron-updates, N x tau / dt
    return [r]


def s16_runs() -> list[dict]:
    """S16: 14 one-at-a-time (+-10 percent of seven parameters) and 64 Latin-hypercube points, P2 at the headline cell (nominal duration;
    J_lag_frac and J_T_frac change the last ramp end by up to +10 percent: longest one-at-a-time run is the J_T_frac x 1.1 cell)."""
    return [_run("S16_oat", "path_hypoxia", HEADLINE_T_RAMP_S, param=p, sign=s) for p in RB4_PARAMETERS for s in (-1, 1)] + \
           [_run("S16_lhs", "path_hypoxia", HEADLINE_T_RAMP_S, point=k) for k in range(N_LHS)]


def s11_runs() -> list[dict]:
    """S11 (MS11, Table 11.1; not launched at MS9): sigma {0.5, 1, 2} x T_ramp {10, 30, 120, 300} s x 10 seeds, mode N, P2."""
    return [_run("S11", "path_hypoxia", T, mode="N", kind="mf_noisy", dt_tau=1.0e-3, n_seeds=N_SEEDS, sigma_factor=f, seed=s)
            for f in (0.5, 1.0, 2.0) for T in S6_T_RAMP_S for s in range(N_SEEDS)]


def all_runs(opts=None) -> dict:
    return {"S6": s6_runs(), "S7_map1": s7_map1_runs(), "S7_map2": s7_map2_runs(), "S7_noisy": s7_subgrid_runs(),
            "S12": s12_runs(opts), "S12_net": s12_network_runs(), "S16": s16_runs()}


def summarise(runs: list[dict]) -> dict:
    out = {}
    for r in runs:
        f = out.setdefault(r["family"], {"runs": 0, "tau": 0.0, "heun_steps": 0.0, "kept_s": 0.0, "longest_tau": 0.0})
        f["runs"] += 1
        f["tau"] += r["tau"]
        f["kept_s"] += r["kept_s"]
        f["longest_tau"] = max(f["longest_tau"], r["tau"])
        if r.get("dt_tau") and r["kind"] == "mf_noisy":
            f["heun_steps"] += r["tau"] / r["dt_tau"]
    return out


# --- timing-gate arithmetic (9.2) ---------------------------------------------------------

ALLOWANCE_H = {"S6": 0.95, "S7_map1": 4.1, "S7_map2_noisy": 2.2, "S12_S16": 40.0 / 60.0, "S12_net": 0.5}   # Table 9.1 upper ends
CELLS = {"p3": "ms9_p3_t120", "map2": "ms9_map2_j-40_t316", "noisy": "ms9_noisy_t120", "s16": "ms9_s16_jt1p1", "nc1": "ms9_nc1_t120",
         "nc1_net": "ms9_nc1_net_t120", "d001": "delta_0.01", "d06": "delta_0.6"}
SAMPLE_CELLS = tuple(CELLS.values())
# Corners of map 1 that this sample does not re-time (kept from the earlier A4-path records; labelled in the report).
EARLIER_MAP1_CORNERS = {"0.01,1": "delta_0.01_td1", "0.01,50": "delta_0.01_td50", "0.3,5": "headline", "0.6,1": "delta_0.6_td1", "0.6,50": "delta_0.6_td50"}


def _spt(c: dict) -> float:
    return c["wall_s"] / c["tau"]


def _slower(cells: dict, names) -> str:
    have = [n for n in names if n in cells]
    return max(have, key=lambda n: _spt(cells[n]))


def map1_estimates(cells: dict, earlier: dict, workers: int) -> dict:
    """Map-1 wall (s, divided by workers) three ways: (i) weighted over the 900 cells from the 7 corners (new Delta 0.01 and 0.6 at tau_d 5 ms,
    the other five from the earlier records), (ii) the same with the earlier corners scaled by the new/old ratio of the corner re-timed
    at the same Delta, (iii) bound: all 900 cells at the slower of the two new cells."""
    mc = {"0.01,5": cells["delta_0.01"]["wall_s"], "0.6,5": cells["delta_0.6"]["wall_s"]}
    old = {k: earlier[v]["wall_s"] for k, v in EARLIER_MAP1_CORNERS.items() if v in earlier}
    out = {}
    if len(old) == len(EARLIER_MAP1_CORNERS):
        pts = {**old, **mc}
        meas = [(float(k.split(",")[0]), float(k.split(",")[1]), w) for k, w in pts.items()]
        out["weighted"] = T.weighted_family_estimate(meas, T.map_grid(), workers)
        ratio_lo = mc["0.01,5"] / earlier["delta_0.01"]["wall_s"] if "delta_0.01" in earlier else 1.0
        ratio_hi = mc["0.6,5"] / earlier["delta_0.6"]["wall_s"] if "delta_0.6" in earlier else 1.0
        scaled = {}
        for k, w in old.items():
            d = float(k.split(",")[0])
            scaled[k] = w * (ratio_lo if d <= 0.01 else ratio_hi if d >= 0.6 else max(ratio_lo, ratio_hi))
        meas2 = [(float(k.split(",")[0]), float(k.split(",")[1]), w) for k, w in {**scaled, **mc}.items()]
        out["weighted_scaled"] = T.weighted_family_estimate(meas2, T.map_grid(), workers)
        out["ratios"] = {"delta_0.01": ratio_lo, "delta_0.6": ratio_hi}
    w = max(mc.values())
    out["bound_slowest_new"] = {"n_cells": 900, "total_s": 900 * w / workers, "mean_s_per_run": w, "max_s_per_run": w}
    return out


def predict(cells: dict, earlier: dict, workers: int, opts=None) -> list[dict]:
    """Rows of 9.2 steps 2 and 3 for the MS9 families. `cells`: {cell: {wall_s, tau}} per-run medians under `workers` concurrent copies.
    Wall of a part = sum of run walls / workers, bounded below by its longest run. Returns parts with seconds, row prediction, limit, verdict."""
    fam = all_runs(opts)
    rows = []

    def mf_part(label, runs, cell_names):
        name = _slower(cells, cell_names)
        rate = _spt(cells[name])
        tot = sum(r["tau"] for r in runs)
        return {"label": label, "runs": len(runs), "cell": name, "tau": tot, "sum_s": tot * rate, "longest_s": max(r["tau"] for r in runs) * rate}

    rows.append({"id": "S6", "s_ids": ["S6"], "allowance_h": ALLOWANCE_H["S6"], "parts": [
        mf_part("P3 (12 runs)", [r for r in fam["S6"] if r["family"] == "S6_P3"], [CELLS["p3"]]),
        mf_part("P4a, P4b (8 runs)", [r for r in fam["S6"] if r["family"] != "S6_P3"], [CELLS["p3"], "headline"])]})
    m1 = map1_estimates(cells, earlier, workers)
    key = "weighted" if "weighted" in m1 else "bound_slowest_new"
    m1p = {"label": f"map 1, 900 cells ({key})", "runs": 900, "cell": "delta_0.01, delta_0.6 + corners", "tau": sum(r["tau"] for r in fam["S7_map1"]),
           "sum_s": m1[key]["total_s"] * workers, "longest_s": m1[key]["max_s_per_run"]}
    rows.append({"id": "S7_map1", "s_ids": ["S7"], "allowance_h": ALLOWANCE_H["S7_map1"], "parts": [m1p], "map1": m1})
    n = fam["S7_noisy"]
    heun_rate = cells[CELLS["noisy"]]["wall_s"] / (cells[CELLS["noisy"]]["tau"] / 1.0e-3)
    steps = sum(r["tau"] / r["dt_tau"] for r in n)
    rows.append({"id": "S7_map2_noisy", "s_ids": ["S7"], "allowance_h": ALLOWANCE_H["S7_map2_noisy"], "parts": [
        mf_part("map 2, 325 cells", fam["S7_map2"], [CELLS["map2"]]),
        {"label": "noisy subgrid, 2250 runs (Heun)", "runs": len(n), "cell": CELLS["noisy"], "steps": steps, "sum_s": steps * heun_rate,
         "longest_s": n[0]["tau"] / n[0]["dt_tau"] * heun_rate}]})
    s12 = fam["S12"]
    nc_cells = [CELLS["nc1"], "headline"]
    parts = [mf_part("NC1 (13 + cells)", [r for r in s12 if r["family"] in ("S12_NC1", "S12_NC1_cells")], nc_cells),
             mf_part("NC2 + NC3", [r for r in s12 if r["family"] in ("S12_NC2", "S12_NC3")], [CELLS["p3"], CELLS["nc1"], "headline"]),
             mf_part("S16 (78 runs)", fam["S16"], [CELLS["s16"], "headline"])]
    rows.append({"id": "S12_S16", "s_ids": ["S12", "S16"], "allowance_h": ALLOWANCE_H["S12_S16"], "parts": parts})
    nw = cells[CELLS["nc1_net"]]["wall_s"]
    rows.append({"id": "S12_net", "s_ids": ["S12"], "allowance_h": ALLOWANCE_H["S12_net"], "parts": [
        {"label": "NC1 network, N 1e4, 120 s, 1 seed", "runs": 1, "cell": CELLS["nc1_net"], "sum_s": nw, "longest_s": nw}]})
    for row in rows:
        for p in row["parts"]:
            p["wall_s"] = max(p["sum_s"] / workers, p["longest_s"])
        row["sum_s"] = sum(p["sum_s"] for p in row["parts"])
        row["longest_run_s"] = max(p["longest_s"] for p in row["parts"])
        row["prediction_s"] = max(row["sum_s"] / workers, row["longest_run_s"])
        row["allowance_s"] = row["allowance_h"] * 3600.0
        row["limit_s"] = 1.5 * row["allowance_s"]
        row["verdict"] = "PASS" if row["prediction_s"] <= row["limit_s"] else "FAIL"
        row["parts_over_one_hour"] = [p["label"] for p in row["parts"] if p["wall_s"] > 3600.0]
    return rows


def s11_informational(cells: dict, workers: int) -> float:
    """S11 (MS11) wall for the shared Table 9.1 row: Heun steps x the noisy cell's s per step / workers. Not an MS9 launch."""
    rate = cells[CELLS["noisy"]]["wall_s"] / (cells[CELLS["noisy"]]["tau"] / 1.0e-3)
    return sum(r["tau"] / r["dt_tau"] for r in s11_runs()) * rate / workers


# --- D36 (conservative, UNVERIFIED) ---------------------------------------------------------------

# Hours. Recorded walls where the decision log has one; otherwise the Table 9.1 upper bound (labelled). Source of each in docs/ms9_plan.md.
D36_RECORDED = {"S5 ramp list (MS8, DL-175)": 3174.9 / 3600.0, "S13 headline subset (MS8, DL-178)": 1578.8 / 3600.0,
                "S5 baseline-only list (MS7, DL-143)": 147.8 / 3600.0}
D36_TABLE_91_UPPER = {"S1-S4, A1-A6 (earlier, no recorded wall)": 0.5, "S2 (earlier, prediction 3 min, DL-168)": 0.05,
                      "S8, S10, S12 networks, K8 and sigma (MS5 to MS10; S12 NC1 network counted here)": 0.5,
                      "S9 finite size (MS10)": 2.0, "S13 rest, MS11 (row upper bound, headline part counted again)": 1.0}


def d36_conservative(rows: list, s11_s: float | None = None) -> dict:
    """Conservative total, hours: recorded MS7 and MS8 walls + Table 9.1 upper bounds for the rest + the MS9 predictions (each at max(prediction,
    its Table 9.1 allowance) is NOT used: the 1.5 x rule is judged separately) + S11 at its prediction. UNVERIFIED sum, not a plan quantity."""
    ms9 = {r["id"]: r["prediction_s"] / 3600.0 for r in rows}
    s11_h = (s11_s or 0.0) / 3600.0
    items = {**D36_RECORDED, **D36_TABLE_91_UPPER, **{f"MS9 {k} (prediction)": v for k, v in ms9.items()}, "S11 (MS11, prediction)": s11_h}
    return {"items_h": items, "total_h": sum(items.values()), "cap_h": 24.0}


# --- disk and memory ---------------------------------------------------------------------------

def disk_layouts(fam: dict, compression: float) -> dict:
    """Bytes by layout. A: the MS8 writer (8 float64 arrays at 1 kHz) for every run, compressed by `compression`. B: the Table 9.1 wording
    (map cells: metrics + v and r in float32, about 1 MB per cell; subgrid and network runs: full series)."""
    def samples(r):
        return M8.kept_samples(r)
    a = {k: sum(samples(r) for r in v) * M8.ARRAYS_PER_RUN * 8 * compression for k, v in fam.items()}
    b = dict(a)
    for k in ("S7_map1", "S7_map2"):
        b[k] = sum(samples(r) for r in fam[k]) * 2 * 4 * compression
    return {"A_all_float64": a, "B_table_9_1": b}


def lpt(walls, workers: int) -> float:
    return M8.lpt_makespan(walls, workers)


def _fmt(sec: float) -> str:
    return f"{sec:.1f} s" if sec < 600 else (f"{sec / 60:.1f} min" if sec < 7200 else f"{sec / 3600:.2f} h")


def format_report(cells: dict, earlier: dict, workers: int, opts=None) -> str:
    fam = all_runs(opts)
    lines = [f"MS9 9a timing-gate prediction, {workers} concurrent copies (per-run medians, divisor {workers}); options {({**DEFAULTS, **(opts or {})})}",
             "Launch rule (9.2 step 3): prediction <= 1.5 x the Table 9.1 allowance and the D36 total <= 24 h. A part over one hour stops for a ruling.", "",
             "Run counts:"]
    tot = 0
    for name, runs in fam.items():
        for f, v in summarise(runs).items():
            work = f"{v['heun_steps']:.3e} Heun steps" if v["heun_steps"] else f"{v['tau']:,.0f} tau"
            lines.append(f"  {f:16s} {v['runs']:5d} runs  {work:>24s}  longest {v['longest_tau']:,.0f} tau")
            tot += v["runs"]
    lines.append(f"  total {tot} runs (the cell-list count 1 + 900 + 325 = 1226 is the baseline list of MS7, not a run count here)")
    lines.append("")
    rows = predict(cells, earlier, workers, opts)
    for row in rows:
        lines.append(f"{row['id']:15s} prediction {_fmt(row['prediction_s']):>9s}  (sum of runs {_fmt(row['sum_s'])}, longest run {_fmt(row['longest_run_s'])})  "
                     f"allowance {_fmt(row['allowance_s'])}  limit {_fmt(row['limit_s'])}  {row['verdict']}  ratio {row['prediction_s'] / row['allowance_s']:.2f} x")
        for p in row["parts"]:
            lines.append(f"    {p['label']:46s} {p['runs']:5d} runs  cell {p['cell']:34s} sum {_fmt(p['sum_s']):>9s}  wall {_fmt(p['wall_s']):>9s}")
        if row.get("map1"):
            for k, v in row["map1"].items():
                if isinstance(v, dict) and "total_s" in v:
                    lines.append(f"    map 1 {k:20s} {_fmt(v['total_s'])}  (mean {v['mean_s_per_run']:.0f} s per run, max {v['max_s_per_run']:.0f} s)")
        if row["parts_over_one_hour"]:
            lines.append(f"    PARTS OVER ONE HOUR (stop for a ruling): {row['parts_over_one_hour']}")
    s11 = s11_informational(cells, workers)
    lines += ["", f"S11 (MS11, informational, not launched at MS9): {_fmt(s11)} at {workers} workers (shares the Table 9.1 row 'S11, S12 MF, S16', 40 min)"]
    d = d36_conservative(rows, s11 * 1.0)
    lines += ["", "D36 conservative check (UNVERIFIED sum): "]
    lines += [f"  {k:90s} {v:6.2f} h" for k, v in d["items_h"].items()]
    lines.append(f"  total {d['total_h']:.2f} h against the cap {d['cap_h']:g} h")
    return "\n".join(lines)


def main(argv=None) -> int:
    import argparse
    from pathlib import Path
    ap = argparse.ArgumentParser(prog="python -m mprsurge.analysis.ms9_counts", description="MS9 9a counts and 9.2 prediction")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--sample-dir", default="results/timing/ms9")
    ap.add_argument("--earlier-dir", default="results/timing/a4")
    ap.add_argument("--opt", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    opts = dict(o.split("=", 1) for o in args.opt)
    for k, v in opts.items():
        if k not in OPTIONS or v not in OPTIONS[k]:
            ap.error(f"{k}={v}: not an option ({OPTIONS.get(k)})")
    root = C.repo_root()
    earlier = T.load_cells(root / args.earlier_dir, ("headline", "delta_0.01", "delta_0.6", "delta_0.01_td1", "delta_0.01_td50", "delta_0.6_td1",
                                                    "delta_0.6_td50"), args.workers)
    for c in ("delta_0.01_td1", "delta_0.01_td50", "delta_0.6_td1", "delta_0.6_td50", "delta_0.01", "delta_0.6"):
        if c not in earlier:
            earlier.update(T.load_cells(root / "results/timing/clean", (c,), args.workers))
    cells = T.load_cells(root / args.sample_dir, SAMPLE_CELLS, args.workers)
    cells["headline"] = earlier.get("headline") or T.load_cells(root / "results/timing/ms8d", ("ms8_dop_1e-10_t120",), args.workers).get("ms8_dop_1e-10_t120")
    text = format_report(cells, earlier, args.workers, opts)
    print(text)
    if args.out:
        Path(root / args.out).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
