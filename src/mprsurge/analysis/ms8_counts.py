"""MS8 run counts, timing-gate prediction inputs and proposed seed keys (8a; plan Table 6.2 S5 and S13, 9.2, 9.3, Table 9.1).

Analysis only: counts runs from the plan wording, converts them to tau simulated and Heun steps, and does the 9.2 arithmetic
against timing cells. Nothing integrates. Where the plan leaves a count open, OPTIONS lists the readings; DEFAULTS is the
reading recommended in docs/ms8_plan.md (an owner ruling is still needed for each, UNVERIFIED). The seed keys are PROPOSED
(DL-166), UNVERIFIED until the owner confirms them.
"""
from __future__ import annotations

import numpy as np

from .. import config as C
from ..units import s_to_tau
from . import cells as CE

PATHS = ("path_eta", "path_hypoxia", "path_updown")          # P1, P2, P5
PATH_LABEL = {"path_eta": "P1", "path_hypoxia": "P2", "path_updown": "P5"}
RAMP_FACTOR = {"path_eta": 1.0, "path_hypoxia": 1.25, "path_updown": 2.0}     # time of the last ramp end in units of T_ramp (4.4, CP14)
PROFILES = ("linear", "sigmoid")
BASELINE_S, HOLD_S, DISCARD_S = 5.0, 10.0, 2.0                  # Appendix B durations (D27, CP14)
HEADLINE_T_RAMP_S = 120.0
HEUN_DT_LADDER = (1.0e-3, 5.0e-4, 2.5e-4, 1.0e-4)             # configs/S13.yaml (F-14)
FLOOR_LEVELS = (1.59e-9, 1.59e-6, 1.59e-3)                    # sigma_floor, configs/S13.yaml (F-10)
HEADLINE_N_STEPS_PER_TAU = 1000.0                             # Heun dt 1e-3 tau
# 8b (DL-169, DL-172): the coupled ladder draws its Brownian increments at 5e-5 tau (configs/ms8/s13_floor_l*.yaml, F-14), whatever the rung:
# tau / 5e-5 normals per floor run. Cost per normal alone: measured in 8b (numpy PCG64 standard_normal plus the block sum), UNVERIFIED; under
# load it is scaled by the DL-104 factor of the Heun step (1.51e-7 s under 10 copies over 3.65e-8 s alone), which is an assumption here.
COUPLING_DT_TAU = 5.0e-5
COUPLED_DRAW_S_ALONE = {20: 9.1e-9, 10: 9.7e-9, 5: 10.8e-9, 2: 14.0e-9}      # per normal, by draws per step m = dt / 5e-5 (rungs 1e-3, 5e-4, 2.5e-4, 1e-4)
LOAD_FACTOR_10_COPIES = 1.51e-7 / 3.65e-8

# Each key is a plan wording that leaves a count open. First entry of each tuple is the recommended reading.
OPTIONS = {
    "noise_seeds_T_ramp": ("grid_linear", "headline_only", "grid_both_profiles"),     # "P2 x 10 noise seeds"
    "start_distance_T_ramp": ("grid", "headline_only"),                                # "P1 x start distance {0.5, 1.5, 3}"
    "start_distance_profiles": ("linear", "both"),
    "floor_design": ("full", "two_part"),                                              # "the floor with its Heun dt ladder at 120 s"
}
DEFAULTS = {k: v[0] for k, v in OPTIONS.items()}

# Proposed spawn keys (DL-166, UNVERIFIED): first element 8 = MS8 (DL-141 convention), root_seed 20261008.
SEED_KEY_PREFIXES = {
    "s5_p2_noise": (8, 1),      # [8, 1, s], s = 0..9: S5 P2 mode-N runs; seed index s gives the same stream in every T_ramp cell (DL-069)
    "d43_floor": (8, 2),        # [8, 2, l, s], l = 0..2 floor level, s = 0..9; the four Heun rungs of one (l, s) share the key (F-14)
}
N_SEEDS = 10


def proposed_seed_keys() -> list[tuple[int, ...]]:
    """Every concrete key the MS8 proposal would use."""
    keys = [SEED_KEY_PREFIXES["s5_p2_noise"] + (s,) for s in range(N_SEEDS)]
    keys += [SEED_KEY_PREFIXES["d43_floor"] + (l, s) for l in range(len(FLOOR_LEVELS)) for s in range(N_SEEDS)]
    return keys


def t_ramp_grid() -> np.ndarray:
    """The 13 T_ramp values, 10^(k/4) s (configs/S5_cells.yaml map2, as S2)."""
    return CE.axis(CE.load_spec()["map2"]["T_ramp_s"])


def run_duration_s(path: str, T_ramp_s: float, mode: str = "D") -> float:
    """Simulated seconds kept: baseline + last ramp end + hold (CP14). Mode N integrates the 2 s discard before t = 0 as well
    (returned by run_integrated_s)."""
    return BASELINE_S + RAMP_FACTOR[path] * T_ramp_s + HOLD_S


def run_integrated_s(path: str, T_ramp_s: float, mode: str = "D") -> float:
    return run_duration_s(path, T_ramp_s) + (DISCARD_S if mode == "N" else 0.0)


def _run(family, path, profile, T, mode="D", solver="DOP853", rtol=1.0e-10, **kw) -> dict:
    d = {"family": family, "path": path, "profile": profile, "T_ramp_s": float(T), "mode": mode, "solver": solver, "rtol": rtol,
         "kept_s": run_duration_s(path, T), "tau": s_to_tau(run_integrated_s(path, T, mode)), "dt_tau": None, "n_seeds": 1}
    d.update(kw)
    return d


def s5_mode_d_runs(opts=None) -> list[dict]:
    """S5 deterministic ramp runs: P1, P2, P5 x 13 T_ramp x 2 profiles, P1 start-distance runs, the headline cell."""
    o = {**DEFAULTS, **(opts or {})}
    grid = t_ramp_grid()
    runs = [_run("S5_grid", p, pr, T) for p in PATHS for pr in PROFILES for T in grid]
    sd_T = grid if o["start_distance_T_ramp"] == "grid" else [HEADLINE_T_RAMP_S]
    sd_pr = PROFILES if o["start_distance_profiles"] == "both" else ("linear",)
    # distance 1.5 is the P1 default (D12) and already in S5_grid; 0.5 and 3 are new
    runs += [_run("S5_start_distance", "path_eta", pr, T, start_distance=d) for d in (0.5, 3.0) for pr in sd_pr for T in sd_T]
    runs.append(_run("S5_headline", "path_hypoxia", "linear", HEADLINE_T_RAMP_S))
    return runs


def s5_mode_n_runs(opts=None) -> list[dict]:
    """S5 P2 noise-seed runs (mode N, sigma 0.0624, stochastic Heun dt 1e-3 tau)."""
    o = {**DEFAULTS, **(opts or {})}
    sel = o["noise_seeds_T_ramp"]
    Ts = [HEADLINE_T_RAMP_S] if sel == "headline_only" else list(t_ramp_grid())
    prs = PROFILES if sel == "grid_both_profiles" else ("linear",)
    return [_run("S5_noise", "path_hypoxia", pr, T, mode="N", solver="Heun", rtol=None, dt_tau=1.0e-3, n_seeds=N_SEEDS, seed=s)
            for pr in prs for T in Ts for s in range(N_SEEDS)]


def s13_headline_runs(opts=None) -> list[dict]:
    """S13 headline subset at T_ramp 120 s on P2 (Table 6.2 S13, CP23). New runs only: rtol 1e-10, delta0 1e-6 and DOP853 are the
    headline run itself (S5_headline)."""
    o = {**DEFAULTS, **(opts or {})}
    T, P2 = HEADLINE_T_RAMP_S, "path_hypoxia"
    runs = [_run("S13_rtol", P2, "linear", T, rtol=r) for r in (1.0e-8, 1.0e-12)]
    runs += [_run("S13_delta0", P2, "linear", T, delta0=d) for d in (1.0e-9, 1.0e-3)]
    runs.append(_run("S13_radau", P2, "linear", T, solver="Radau", rtol=1.0e-10))           # DL-100 (3): 1e-10 at the headline
    levels = range(len(FLOOR_LEVELS))
    if o["floor_design"] == "full":                       # 3 levels x 4 rungs x 10 seeds
        combos = [(l, dt, s) for l in levels for dt in HEUN_DT_LADDER for s in range(N_SEEDS)]
    else:                                                 # RB3(b): 3 levels at the default rung; RB6: middle level, other rungs
        combos = [(l, HEUN_DT_LADDER[0], s) for l in levels for s in range(N_SEEDS)]
        combos += [(1, dt, s) for dt in HEUN_DT_LADDER[1:] for s in range(N_SEEDS)]
    runs += [_run("S13_floor", P2, "linear", T, mode="N", solver="Heun", rtol=None, dt_tau=dt, floor_level=l, seed=s, coupled=True)
             for l, dt, s in combos]
    return runs


def heun_steps(run: dict) -> float:
    return run["tau"] / run["dt_tau"]


def coupled_draws(run: dict) -> float:
    """Normals drawn for a coupled floor run (F-14, M-10): tau / 5e-5 whatever the rung; 0 for an uncoupled run."""
    return run["tau"] / COUPLING_DT_TAU if run.get("coupled") else 0.0


def coupled_draw_s(run: dict) -> float:
    """Seconds per normal of a coupled floor run under 10 copies (alone x the DL-104 load factor)."""
    return COUPLED_DRAW_S_ALONE[int(round(run["dt_tau"] / COUPLING_DT_TAU))] * LOAD_FACTOR_10_COPIES


def summarise(runs: list[dict]) -> dict:
    """Counts by family: runs, tau (mode D) or Heun steps (mode N), samples kept at 1 kHz."""
    out = {}
    for r in runs:
        f = out.setdefault(r["family"], {"runs": 0, "tau": 0.0, "heun_steps": 0.0, "kept_s": 0.0, "longest_tau": 0.0})
        f["runs"] += 1
        f["tau"] += r["tau"]
        f["kept_s"] += r["kept_s"]
        f["longest_tau"] = max(f["longest_tau"], r["tau"])
        if r["dt_tau"]:
            f["heun_steps"] += heun_steps(r)
    return out


# --- timing-gate arithmetic (9.2) ---------------------------------------------------------

# Candidate cells for the s/tau of a mode-D family: the matching MS8 sample cell and the nearest earlier cell; the slower is used.
RATE_CELLS = {
    ("path_eta", "linear"): ("ms8_p1_lin_t56", "headline"),
    ("path_eta", "sigmoid"): ("ms8_p1_sig_t56", "headline"),
    ("path_hypoxia", "linear"): ("ms8_p2_lin_t56", "headline"),
    ("path_hypoxia", "sigmoid"): ("ms8_p2_sig_t56", "headline"),
    ("path_updown", "linear"): ("ms8_p5_lin_t56", "p5_1000"),
    ("path_updown", "sigmoid"): ("ms8_p5_sig_t56", "p5_1000"),
}
HEUN_CELL = "mode_n"                  # 16,700 tau at dt 1e-3 (steps = tau / dt_tau)
FLOOR_FINE_CELL = "ms8_floor_dt1e-4"
RTOL_CELLS = {1.0e-8: "ms8_dop_1e-8_t10", 1.0e-10: "ms8_dop_1e-10_t10", 1.0e-12: "ms8_dop_1e-12_t10"}
RADAU_CELL = "radau_1e-10_t10"
SAMPLE_CELLS = tuple(sorted({c for v in RATE_CELLS.values() for c in v if c.startswith("ms8_")} | set(RTOL_CELLS.values()) | {FLOOR_FINE_CELL}))
EARLIER_CELLS = ("headline", "p5_1000", HEUN_CELL, RADAU_CELL)
# Table 9.1 upper ends in hours (D-5): "S2, S5, S6 (ramp sweeps)" 19-57 min, "S13 numerics" < 1 h.
ALLOWANCE_H = {"ms8_s5": 0.95, "ms8_s13_headline": 1.0}


def _s_per_tau(c: dict) -> float:
    return c["wall_s"] / c["tau"]


def slowest(cells: dict, names) -> str:
    have = [n for n in names if n in cells]
    if not have:
        raise KeyError(f"no timing cell among {list(names)}")
    return max(have, key=lambda n: _s_per_tau(cells[n]))


def heun_s_per_step(cells: dict, dt_tau: float) -> float:
    """Wall seconds per Heun step under the load of the cells: the mode_n cell (dt 1e-3); for the 1e-4 rung also the sample cell;
    the slower of those available."""
    rates = [cells[HEUN_CELL]["wall_s"] / (cells[HEUN_CELL]["tau"] / 1.0e-3)]
    if dt_tau <= 1.0e-4 and FLOOR_FINE_CELL in cells:
        rates.append(cells[FLOOR_FINE_CELL]["wall_s"] / (cells[FLOOR_FINE_CELL]["tau"] / 1.0e-4))
    return max(rates)


def predict(cells: dict, workers: int, opts=None) -> list[dict]:
    """9.2 steps 2 and 3 for the MS8 families. `cells`: {cell: {wall_s, tau}} per-run walls under `workers` concurrent copies
    (DL-103 (1)); wall time of a family = sum of run walls / workers (the divisor of DL-104), also bounded below by its longest run.
    Returns one dict per row with parts (seconds), longest_run_s, prediction_s, limit_s (1.5 x allowance), verdict."""
    d, n, s13 = s5_mode_d_runs(opts), s5_mode_n_runs(opts), s13_headline_runs(opts)
    rows = []

    def mf_part(label, runs, cell):
        rate = _s_per_tau(cells[cell])
        return {"label": label, "runs": len(runs), "cell": cell, "tau": sum(r["tau"] for r in runs),
                "sum_s": sum(r["tau"] for r in runs) * rate, "longest_s": max(r["tau"] for r in runs) * rate}

    parts = []
    for p in PATHS:
        for pr in PROFILES:
            sel = [r for r in d if r["path"] == p and r["profile"] == pr and r["family"] != "S5_headline"]
            if sel:
                parts.append(mf_part(f"{PATH_LABEL[p]} {pr}", sel, slowest(cells, RATE_CELLS[(p, pr)])))
    parts.append(mf_part("headline cell", [r for r in d if r["family"] == "S5_headline"], "headline"))
    rate = heun_s_per_step(cells, 1.0e-3)
    parts.append({"label": "S5 P2 noise seeds (Heun)", "runs": len(n), "cell": HEUN_CELL, "steps": sum(heun_steps(r) for r in n),
                  "sum_s": sum(heun_steps(r) for r in n) * rate, "longest_s": max(heun_steps(r) for r in n) * rate})
    rows.append({"id": "ms8_s5", "s_ids": ["S5"], "allowance_h": ALLOWANCE_H["ms8_s5"], "parts": parts})

    p13 = []
    base = cells[RTOL_CELLS[1.0e-10]] if RTOL_CELLS[1.0e-10] in cells else None
    for r in (1.0e-8, 1.0e-12):
        runs = [x for x in s13 if x["family"] == "S13_rtol" and x["rtol"] == r]
        ratio = _s_per_tau(cells[RTOL_CELLS[r]]) / _s_per_tau(base) if base and RTOL_CELLS[r] in cells else 1.0
        w = _s_per_tau(cells["headline"]) * max(1.0, ratio) * runs[0]["tau"]
        p13.append({"label": f"DOP853 rtol {r:g} (x{ratio:.2f} of 1e-10 at the same path)", "runs": 1, "cell": "headline",
                    "sum_s": w, "longest_s": w})
    dl = [x for x in s13 if x["family"] == "S13_delta0"]
    p13.append(mf_part("delta0 ladder, noise-free", dl, "headline"))
    rd = [x for x in s13 if x["solver"] == "Radau"]
    p13.append(mf_part("Radau rtol 1e-10 at 120 s", rd, RADAU_CELL))
    fl = [x for x in s13 if x["family"] == "S13_floor"]
    sec = sum(heun_steps(x) * heun_s_per_step(cells, x["dt_tau"]) + coupled_draws(x) * (coupled_draw_s(x) if x.get("coupled") else 0.0) for x in fl)
    lng = max(heun_steps(x) * heun_s_per_step(cells, x["dt_tau"]) + coupled_draws(x) * (coupled_draw_s(x) if x.get("coupled") else 0.0) for x in fl)
    p13.append({"label": "D43 floor ladder (Heun)", "runs": len(fl), "cell": f"{HEUN_CELL}, {FLOOR_FINE_CELL}",
                "steps": sum(heun_steps(x) for x in fl), "sum_s": sec, "longest_s": lng})
    rows.append({"id": "ms8_s13_headline", "s_ids": ["S13"], "allowance_h": ALLOWANCE_H["ms8_s13_headline"], "parts": p13})

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


def lpt_makespan(walls, workers: int) -> float:
    """Wall time of a longest-first list schedule of independent runs on `workers` workers (the order recommended as M-12).
    Arithmetic only: run walls are the per-run medians under load, so the result is a prediction, not a guarantee."""
    import heapq
    free = [0.0] * workers
    heapq.heapify(free)
    for w in sorted(walls, reverse=True):
        heapq.heappush(free, heapq.heappop(free) + w)
    return max(free)


def run_walls(cells: dict, opts=None) -> dict:
    """Predicted wall of every new run, by row id (mode D: tau x slowest candidate s/tau; Heun: steps x s/step; S13 DOP853/Radau
    runs at the headline or Radau rate)."""
    d, n, s13 = s5_mode_d_runs(opts), s5_mode_n_runs(opts), s13_headline_runs(opts)
    w5 = [r["tau"] * _s_per_tau(cells[slowest(cells, RATE_CELLS[(r["path"], r["profile"])])]) if r["family"] != "S5_headline"
          else r["tau"] * _s_per_tau(cells["headline"]) for r in d]
    w5 += [heun_steps(r) * heun_s_per_step(cells, r["dt_tau"]) for r in n]
    w13 = []
    for r in s13:
        if r["mode"] == "N":
            w13.append(heun_steps(r) * heun_s_per_step(cells, r["dt_tau"]) + coupled_draws(r) * (coupled_draw_s(r) if r.get("coupled") else 0.0))
        elif r["solver"] == "Radau":
            w13.append(r["tau"] * _s_per_tau(cells[RADAU_CELL]))
        else:
            w13.append(r["tau"] * _s_per_tau(cells["headline"]))
    return {"ms8_s5": w5, "ms8_s13_headline": w13}


# --- disk and memory ---------------------------------------------------------------------

ARRAYS_PER_RUN = 8           # t_ms, r, v, s, eta, J, Delta, I (simulate_mf._output), float64


def kept_samples(run: dict) -> int:
    return int(round(run["kept_s"] * 1000.0)) + 1


def disk_estimate(runs: list[dict], compression: float) -> dict:
    """Bytes written by np.savez_compressed for the 8 float64 arrays of each run at 1 kHz; `compression` = compressed / raw
    (measured on sample runs; 1.0 is the raw upper bound)."""
    raw = sum(kept_samples(r) * ARRAYS_PER_RUN * 8 for r in runs)
    return {"files": len(runs), "raw_bytes": raw, "compression": compression, "bytes": raw * compression}


def memory_estimate(runs: list[dict], workers: int, bytes_per_sample: float) -> dict:
    """Peak memory of `workers` concurrent runs if the largest ones run together; bytes_per_sample = peak resident bytes of one
    run per kept sample, measured on the sample cells (the raw arrays are 64 B per sample)."""
    big = sorted((kept_samples(r) for r in runs), reverse=True)[:workers]
    return {"largest_run_samples": big[0], "per_run_peak_bytes": big[0] * bytes_per_sample, "workers": workers,
            "all_largest_together_bytes": sum(big) * bytes_per_sample}


# --- report -----------------------------------------------------------------------------

def _fmt(sec: float) -> str:
    return f"{sec:.1f} s" if sec < 600 else (f"{sec / 60:.1f} min" if sec < 7200 else f"{sec / 3600:.2f} h")


def format_report(cells: dict, workers: int, opts=None, probe: dict | None = None, mem_polled: dict | None = None) -> str:
    o = {**DEFAULTS, **(opts or {})}
    runs = s5_mode_d_runs(o) + s5_mode_n_runs(o) + s13_headline_runs(o)
    lines = [f"MS8 8a timing-gate prediction, {workers} concurrent copies (per-run median walls, divisor {workers}); options {o}",
             "Launch rule (9.2 step 3): prediction <= 1.5 x the Table 9.1 allowance and the D36 total <= 24 h. A part over one hour stops for a ruling.", ""]
    lines.append("Run counts (new runs; the S13 rtol 1e-10, delta0 1e-6 and DOP853 runs are the headline run itself):")
    for fam, v in summarise(runs).items():
        work = f"{v['heun_steps']:.3e} Heun steps" if v["heun_steps"] else f"{v['tau']:,.0f} tau"
        lines.append(f"  {fam:20s} {v['runs']:4d} runs  {work:>22s}  longest {v['longest_tau']:,.0f} tau")
    lines.append(f"  total {len(runs)} runs")
    lines.append("")
    for row in predict(cells, workers, o):
        lines.append(f"{row['id']:18s} prediction {_fmt(row['prediction_s']):>9s}  (sum of runs {_fmt(row['sum_s'])}, longest run {_fmt(row['longest_run_s'])})"
                     f"  allowance {_fmt(row['allowance_s'])}  limit {_fmt(row['limit_s'])}  {row['verdict']}")
        for p in row["parts"]:
            lines.append(f"    {p['label']:44s} {p['runs']:4d} runs  cell {p['cell']:34s} sum {_fmt(p['sum_s']):>9s}  wall {_fmt(p['wall_s']):>9s}")
        row_lpt = lpt_makespan(run_walls(cells, o)[row["id"]], workers)
        lines.append(f"    longest-first schedule on {workers} workers: {_fmt(row_lpt)}")
        if row["parts_over_one_hour"]:
            lines.append(f"    PARTS OVER ONE HOUR (stop for a ruling): {row['parts_over_one_hour']}")
    lines.append("")
    comp = float(np.mean([c["compression"] for c in probe["cells"].values()])) if probe else 1.0
    dk = disk_estimate(runs, comp)
    lines.append(f"Disk: {dk['files']} npz files, raw {dk['raw_bytes'] / 1e9:.2f} GB (8 float64 arrays at 1 kHz), compression "
                 f"{'measured ' if probe else 'ASSUMED '}{comp:.3f} -> {dk['bytes'] / 1e9:.2f} GB (limit: Table 9.1 under 20 GB for the plan)")
    bps = max(c["peak_increase_per_sample_bytes"] for c in probe["cells"].values()) if probe else 64.0 * 3
    me = memory_estimate(runs, workers, bps)
    lines.append(f"Memory: largest run {me['largest_run_samples']:,} samples x {bps:.0f} B per sample ({'measured peak, max of the probe cells' if probe else 'ASSUMED 3 x raw'})"
                 f" = {me['per_run_peak_bytes'] / 1e6:.0f} MB per run; the {workers} largest together {me['all_largest_together_bytes'] / 1e9:.2f} GB (Table 9.1: under 1 GB; limit used since DL-142: 12 GB)")
    if mem_polled:
        lines.append("Polled total python working set during the 10-copy samples (GB): " + ", ".join(f"{k} {v / 1e9:.2f}" for k, v in mem_polled.items()))
    return "\n".join(lines)


def main(argv=None) -> int:
    import argparse
    import json
    from pathlib import Path

    from . import timing as T
    ap = argparse.ArgumentParser(prog="python -m mprsurge.analysis.ms8_counts", description="MS8 8a counts and 9.2 prediction")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--sample-dir", default="results/timing/ms8")
    ap.add_argument("--earlier-dir", default="results/timing/a4")
    ap.add_argument("--opt", action="append", default=[], metavar="KEY=VALUE", help="a reading from OPTIONS, for example floor_design=two_part")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    opts = dict(o.split("=", 1) for o in args.opt)
    for k, v in opts.items():
        if k not in OPTIONS or v not in OPTIONS[k]:
            ap.error(f"{k}={v}: not an option ({OPTIONS.get(k)})")
    root = C.repo_root()
    cells = T.load_cells(root / args.earlier_dir, EARLIER_CELLS, args.workers)
    cells.update(T.load_cells(root / args.sample_dir, SAMPLE_CELLS, args.workers))
    probe_p = root / args.sample_dir / "size_probe.json"
    probe = json.loads(probe_p.read_text(encoding="utf-8")) if probe_p.exists() else None
    mem = {}
    for c in SAMPLE_CELLS:
        mp = root / args.sample_dir / "logs" / f"mem_{c}.csv"
        if mp.exists():
            txt = mp.read_text(encoding="utf-8-sig").strip()
            if txt.isdigit():
                mem[c] = float(txt)
    text = format_report(cells, args.workers, opts, probe, mem)
    print(text)
    if args.out:
        Path(root / args.out).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
