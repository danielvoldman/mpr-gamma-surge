"""MS11 run counts, timing-gate prediction and proposed seed keys (11a; plan Table 6.2 S11 and S13, Table 7.2 RB2/RB6, Table 9.1, 9.2, 9.3, D36).

Analysis only: counts runs from the plan wording, converts them to Heun steps, tau or neuron-updates, and does the 9.2 arithmetic against the
11a timing cells (configs/timing/ms11/ and the earlier cells they extend). Nothing integrates. Where the plan gives no number the readings are
listed in OPTIONS and none is chosen (open choices M11-n, docs/ms11_plan.md); the defaults used for the arithmetic are the recommendations of that
plan, UNVERIFIED until the reviewer rules. The seed keys are PROPOSED (DL-333), UNVERIFIED until confirmed. Reuses the MS8 8a conventions
(ms8_counts: per-run median under 10 concurrent copies, divisor 10, longest-first schedule) and the MS10 10a network conventions (ms10_counts).

  .venv/Scripts/python.exe -m mprsurge.analysis.ms11_counts [--out results/timing/ms11/prediction_11a.txt] [--opt KEY=VALUE ...]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .. import config as C
from ..units import s_to_tau
from . import ms8_counts as M8
from . import timing as T

P2 = "path_hypoxia"
SIGMA_REF = 0.0624                                   # configs/base.yaml, frozen at MS7, "checked, not confirmed" (G4-C4)
S11_SIGMA_FACTORS = (0.5, 1.0, 2.0)                  # Table 6.2 S11, Table 7.2 RB2
S11_T_RAMP_S = (10.0, 30.0, 120.0, 300.0)            # Table 6.2 S11
S11_SEEDS = 10
S13_MF_T_RAMP_S = (10.0, 316.22776601683796)         # Table 6.2 S13 (120 s done at MS8); 316 s = the S5 grid value 10^2.5
S13_RTOL_NEW = (1.0e-8, 1.0e-12)                     # 1e-10 is the S5 grid run itself
S13_DELTA0_NEW = (1.0e-9, 1.0e-3)                    # 1e-6 is the S5 grid run itself
FLOOR_SEEDS = 10
NET_DT_LADDER = (1.0e-3, 5.0e-4, 2.5e-4, 1.0e-4)     # Table 6.2 S13 (network, 10 s ramp)
NET_N, NET_T_RAMP_S = 10000, 10.0
NET_VP_CONFIGS = ((200.0, 1.0e-3), (200.0, 1.0e-4))  # V_p +-200, "the +-200 check also at dt 1e-4"
RADAU_S_PER_TAU_120 = 0.0957                          # DL-178 (measured in the S13 pool at 120 s, 10 workers)
RADAU_RTOL_COST_RATIO = 299.6674131 / 143.42087119999997   # rtol 1e-12 over 1e-10 at the 10 s ramp, alone (results/timing/radau_1e-12_t10.json, radau_1e-10_t10.json)
MS8_S13_WALL_S = 1578.8                               # DL-178: S13 headline subset, 125 runs
ALLOWANCE_S11_S = 40 * 60.0                           # Table 9.1 "S11, S12 mean field, S16": "< 40 min" (shared row; the share for S11 is not stated)
ALLOWANCE_S13_S = 60 * 60.0                           # Table 9.1 "S13 numerics": "< 1 h" (whole of S13, MS8 part included)
RULE_FACTOR = 1.5                                     # 9.2 step 3
ONE_HOUR_S = 3600.0
D36_CAP_H = 24.0                                      # D36
D36_CARRIED_H = 14.21                                 # DL-329: sum of mixed bases, conservative, UNVERIFIED
D36_PLACEHOLDERS_H = 1.0 + 0.0075                     # of that: "Rest of S13" at its 1 h upper bound and "S11" at its 9a prediction (ms9_g_evidence section 3)
WORKERS = 10

# Readings the plan leaves open (none chosen). First entry of each tuple is the recommendation of docs/ms11_plan.md.
OPTIONS = {
    "M11-3_control": ("headline_T120", "twin_every_T_ramp", "none_new"),
    "M11-4_floor_at_10_316": ("default_rung", "full_ladder", "none"),
    "M11-4_radau": ("t10_and_t316", "t10_only", "headline_only_cut_1"),
    "M11-5_net_seeds": (3, 1, 10),
    "M11-5_net_controls": ("none_new", "per_configuration"),
}
DEFAULTS = {k: v[0] for k, v in OPTIONS.items()}

# Proposed spawn keys (DL-333, UNVERIFIED): first element 11 = MS11 (DL-141 convention), root_seed 20261008.
SEED_KEY_PREFIXES = {
    "s11_ramp": (11, 1),          # [11, 1, s], s = 0..9: S11 mode-N ramp runs; seed index s is the same stream at every sigma and T_ramp (S5 precedent, DL-069)
    "s11_control": (11, 2),       # [11, 2, s], s = 0..9: constant-parameter controls (DL-251)
    "s13_mf_floor": (11, 3),      # [11, 3, t, l, s], t = 0..1 (T_ramp 10, 316 s), l = 0..2 floor level, s = 0..9; rungs of one (t, l, s) share the key (F-14)
    "s13_net": (11, 4),           # [11, 4, s], s = 0..2: S13 network runs; every configuration of one s shares the key (same initial V)
    "s13_net_control": (11, 5),   # [11, 5, k, s], k = 0..5 network configuration, s = 0..2 (only if M11-5 chooses controls)
}
N_NET_SEEDS_MAX_KEYS, N_NET_CONFIGS = 3, 6


def proposed_seed_keys() -> list[tuple[int, ...]]:
    P = SEED_KEY_PREFIXES
    keys = [P["s11_ramp"] + (s,) for s in range(S11_SEEDS)] + [P["s11_control"] + (s,) for s in range(S11_SEEDS)]
    keys += [P["s13_mf_floor"] + (t, l, s) for t in range(len(S13_MF_T_RAMP_S)) for l in range(len(M8.FLOOR_LEVELS)) for s in range(FLOOR_SEEDS)]
    keys += [P["s13_net"] + (s,) for s in range(N_NET_SEEDS_MAX_KEYS)]
    keys += [P["s13_net_control"] + (k, s) for k in range(N_NET_CONFIGS) for s in range(N_NET_SEEDS_MAX_KEYS)]
    return keys


# --- run lists --------------------------------------------------------------------------------------------------------------------------

def _noisy(family, T_ramp, **kw):
    return M8._run(family, P2, "linear", T_ramp, mode="N", solver="Heun", rtol=None, dt_tau=1.0e-3, **kw)


def s11_runs() -> list[dict]:
    """S11: sigma {0.5, 1, 2} x T_ramp {10, 30, 120, 300} s x 10 seeds, mode N, P2 headline cell (path: reading, M11-1)."""
    return [_noisy("S11", T_, sigma_factor=f, seed=s) for f in S11_SIGMA_FACTORS for T_ in S11_T_RAMP_S for s in range(S11_SEEDS)]


def control_runs(scope: str) -> list[dict]:
    """DL-251 constant-parameter controls (POST-HOC AMENDMENT): mode N, eta held at eta_start, J at J0, the ramp run's duration and sigma."""
    if scope == "none_new":
        return []
    Ts = (120.0,) if scope == "headline_T120" else S11_T_RAMP_S if scope == "twin_every_T_ramp" else None
    if Ts is None:
        raise ValueError(scope)
    return [_noisy("S11_control", T_, sigma_factor=f, seed=s) for f in S11_SIGMA_FACTORS for T_ in Ts for s in range(S11_SEEDS)]


def s13_mf_runs(opts=None) -> list[dict]:
    """S13 mean-field remainder at T_ramp 10 and 316 s (new runs only; rtol 1e-10 and delta0 1e-6 are the S5 grid runs, UNVERIFIED until 11b checks the hashes)."""
    o = {**DEFAULTS, **(opts or {})}
    radau = o["M11-4_radau"]
    runs = []
    for T_ in S13_MF_T_RAMP_S:
        runs += [M8._run("S13_rtol", P2, "linear", T_, rtol=r) for r in S13_RTOL_NEW]
        runs += [M8._run("S13_delta0", P2, "linear", T_, delta0=d) for d in S13_DELTA0_NEW]
        if radau == "t10_and_t316" or (radau == "t10_only" and T_ == 10.0):         # headline_only_cut_1 (9.3 step 1): no Radau away from 120 s
            runs.append(M8._run("S13_radau", P2, "linear", T_, solver="Radau", rtol=1.0e-10))
        if T_ == 10.0 and radau != "headline_only_cut_1":
            runs.append(M8._run("S13_radau", P2, "linear", T_, solver="Radau", rtol=1.0e-12))      # M-5, DL-100 (3): 1e-12 only at the 10 s ramp
        if o["M11-4_floor_at_10_316"] != "none":
            rungs = M8.HEUN_DT_LADDER if o["M11-4_floor_at_10_316"] == "full_ladder" else M8.HEUN_DT_LADDER[:1]
            runs += [M8._run("S13_floor", P2, "linear", T_, mode="N", solver="Heun", rtol=None, dt_tau=dt, floor_level=l, seed=s, coupled=True)
                     for l in range(len(M8.FLOOR_LEVELS)) for dt in rungs for s in range(FLOOR_SEEDS)]
    return runs


def net_configs() -> list[tuple]:
    """The 6 network configurations of S13 on the 10 s ramp: the dt ladder (4 rungs; the 1e-3 rung is re-run under the new key, M11-5) and V_p +-200 at dt 1e-3 and 1e-4."""
    return [(100.0, dt) for dt in NET_DT_LADDER] + [(vp, dt) for vp, dt in NET_VP_CONFIGS]


def s13_net_runs(opts=None) -> list[dict]:
    o = {**DEFAULTS, **(opts or {})}
    out = []
    tau = s_to_tau(M8.run_integrated_s(P2, NET_T_RAMP_S, "N"))
    for k, (vp, dt) in enumerate(net_configs()):
        for s in range(int(o["M11-5_net_seeds"])):
            r = {"family": "S13_net", "k": k, "V_peak": vp, "dt_tau": dt, "N": NET_N, "seed": s, "control": False, "tau": tau}
            out.append(r)
            if o["M11-5_net_controls"] == "per_configuration":
                out.append({**r, "family": "S13_net_control", "control": True})
    return out


def net_updates(r: dict) -> float:
    return r["N"] * r["tau"] / r["dt_tau"]


def counts(opts=None) -> dict:
    o = {**DEFAULTS, **(opts or {})}
    f = {"S11": s11_runs(), "S11_control": control_runs(o["M11-3_control"]), "S13_mf": s13_mf_runs(o), "S13_net": s13_net_runs(o)}
    out = {}
    for k, v in f.items():
        net = [r for r in v if "V_peak" in r]
        heun = [r for r in v if "V_peak" not in r and r.get("mode") == "N"]
        mf = [r for r in v if "V_peak" not in r and r.get("mode") != "N"]
        out[k] = {"runs": len(v), "heun_steps": sum(M8.heun_steps(r) for r in heun), "tau": sum(r["tau"] for r in mf), "updates": sum(net_updates(r) for r in net)}
    return out


# --- per-run wall predictions (9.2 step 2), seconds under 10 concurrent copies -------------------------------------------------------------------

def _spt(c: dict) -> float:
    return c["wall_s"] / c["tau"]


def heun_s_per_step(cells: dict) -> float:
    names = [n for n in cells if n.startswith("ms11_s11_")]
    if not names:
        raise KeyError("no ms11_s11_* timing cell")
    return max(cells[n]["wall_s"] / (cells[n]["tau"] / 1.0e-3) for n in names)


def floor_wall_s(cells: dict, tau: float, dt_tau: float) -> float:
    """Coupled floor run: wall = c0 tau + c1 tau / dt, fitted on the two 316 s floor cells (dt 1e-3 and 1e-4)."""
    a, b = cells["ms11_floorc_l2_dt1e-3_t316"], cells["ms11_floorc_l2_dt1e-4_t316"]
    c1 = (b["wall_s"] / b["tau"] - a["wall_s"] / a["tau"]) / (1.0e4 - 1.0e3)
    c0 = a["wall_s"] / a["tau"] - c1 * 1.0e3
    return tau * (c0 + c1 / dt_tau)


def mf_wall_s(cells: dict, r: dict) -> float:
    if r["family"] == "S13_radau":
        return r["tau"] * RADAU_S_PER_TAU_120 * (RADAU_RTOL_COST_RATIO if r["rtol"] == 1.0e-12 else 1.0)
    if r["mode"] == "N":
        return floor_wall_s(cells, r["tau"], r["dt_tau"])
    if r["T_ramp_s"] > 100.0:
        c = cells["ms11_dop_1e-12_t316"] if r["rtol"] == 1.0e-12 else cells["ms11_dop_1e-10_t316"]
    else:
        c = cells[M8.RTOL_CELLS[r["rtol"]]] if r["family"] == "S13_rtol" else cells[M8.RTOL_CELLS[1.0e-10]]
    return r["tau"] * _spt(c)


NET_CELL = {(100.0, 1.0e-3): "net_1e4", (100.0, 5.0e-4): "ms11_net_dt5e-4", (100.0, 2.5e-4): "ms11_net_dt2p5e-4", (100.0, 1.0e-4): "ms11_net_dt1e-4",
            (200.0, 1.0e-3): "ms11_net_vp200", (200.0, 1.0e-4): "ms11_net_vp200_dt1e-4"}


def net_wall_s(cells: dict, r: dict) -> float:
    """Neuron-updates of the run times the seconds per update of the matching cell (the cell at the same V_p and dt)."""
    c = cells[NET_CELL[(r["V_peak"], r["dt_tau"])]]
    return net_updates(r) * c["wall_s"] / (NET_N * c["tau"] / r["dt_tau"])


def lpt(walls, workers: int = WORKERS) -> float:
    return M8.lpt_makespan(walls, workers)


def _family_key(label: str) -> str:
    return label


def predict(cells: dict, opts=None, workers: int = WORKERS) -> dict:
    """Rows: ms11_s11 (S11 + control, allowance 40 min) and ms11_s13 (MS8 recorded 26.3 min + MF remainder + network, allowance 1 h)."""
    o = {**DEFAULTS, **(opts or {})}
    hs = heun_s_per_step(cells)
    s11 = [(r["family"], M8.heun_steps(r) * hs) for r in s11_runs() + control_runs(o["M11-3_control"])]
    mf = [(f"{r['family']} T{r['T_ramp_s']:.0f}" + (f" rtol {r['rtol']:g}" if r["family"] == "S13_radau" else ""), mf_wall_s(cells, r)) for r in s13_mf_runs(o)]
    net = [(f"{r['family']} cfg{r['k']} Vp{r['V_peak']:.0f} dt{r['dt_tau']:g}", net_wall_s(cells, r)) for r in s13_net_runs(o)]
    out = {}
    for rid, parts, carried, allow in (("ms11_s11", s11, 0.0, ALLOWANCE_S11_S), ("ms11_s13", mf + net, MS8_S13_WALL_S, ALLOWANCE_S13_S)):
        walls = [w for _, w in parts]
        pred = max(sum(walls) / workers, max(walls, default=0.0))
        by = {}
        for lab, w in parts:
            d = by.setdefault(lab, {"runs": 0, "sum_s": 0.0, "longest_s": 0.0})
            d["runs"] += 1
            d["sum_s"] += w
            d["longest_s"] = max(d["longest_s"], w)
        out[rid] = {"runs": len(parts), "sum_s": sum(walls), "longest_s": max(walls, default=0.0), "prediction_s": pred, "lpt_s": lpt(walls, workers),
                    "carried_ms8_s": carried, "total_s": pred + carried, "allowance_s": allow, "limit_s": RULE_FACTOR * allow, "by_family": by,
                    "over_one_hour": sorted({lab for lab, w in parts if w > ONE_HOUR_S}),
                    "verdict": "PASS" if pred + carried <= RULE_FACTOR * allow else "FAIL"}
    return out


def d36(pred_s: float) -> dict:
    h = pred_s / 3600.0
    replaced = D36_CARRIED_H - D36_PLACEHOLDERS_H + h
    return {"on_top_h": D36_CARRIED_H + h, "replaced_h": replaced, "margin_replaced_h": D36_CAP_H - replaced, "within_cap": D36_CARRIED_H + h <= D36_CAP_H}


def fmt(s: float) -> str:
    return f"{s:.0f} s" if s < 600 else (f"{s / 60:.1f} min" if s < 7200 else f"{s / 3600:.2f} h")


def report(cells: dict, opts=None) -> str:
    o = {**DEFAULTS, **(opts or {})}
    L = [f"MS11 11a timing-gate prediction, {WORKERS} concurrent copies (per-run median walls, divisor {WORKERS}); readings used (recommendations, none ruled): {o}", ""]
    for k, v in counts(o).items():
        L.append(f"  {k:12s} {v['runs']:4d} runs  Heun steps {v['heun_steps']:.3e}  tau {v['tau']:.3e}  neuron-updates {v['updates']:.3e}")
    P = predict(cells, o)
    L.append("")
    for rid, p in P.items():
        L.append(f"{rid}: {p['runs']} runs, prediction {fmt(p['prediction_s'])} (sum {fmt(p['sum_s'])}, longest {fmt(p['longest_s'])}, longest-first {fmt(p['lpt_s'])})"
                 f" + carried MS8 {fmt(p['carried_ms8_s'])} = {fmt(p['total_s'])}; allowance {fmt(p['allowance_s'])}, limit {fmt(p['limit_s'])}, "
                 f"ratio {p['total_s'] / p['allowance_s']:.2f} x allowance, {p['verdict']}")
        for lab, d in p["by_family"].items():
            L.append(f"    {lab:44s} {d['runs']:4d} runs  sum {fmt(d['sum_s']):>9s}  longest {fmt(d['longest_s']):>9s}")
        if p["over_one_hour"]:
            L.append(f"    RUNS OVER ONE HOUR (flag for the reviewer; launched by the reviewer): {p['over_one_hour']}")
    tot = sum(p["prediction_s"] for p in P.values())
    t = d36(tot)
    L.append("")
    L.append(f"D36: carried {D36_CARRIED_H} h (DL-329, mixed bases, UNVERIFIED) + MS11 {tot / 3600:.3f} h = {t['on_top_h']:.2f} h on top; "
             f"with the 'rest of S13' 1 h and 'S11' 0.0075 h placeholders replaced {t['replaced_h']:.2f} h; cap {D36_CAP_H:g} h, "
             f"{'within' if t['within_cap'] else 'OVER'} the cap")
    return "\n".join(L)


def load_cells(root) -> dict:
    cells = T.load_cells(root / "results/timing/ms11", [p.stem for p in (root / "configs/timing/ms11").glob("*.yaml")], WORKERS)
    cells.update(T.load_cells(root / "results/timing/ms10", ["net_1e4"], WORKERS))
    cells.update(T.load_cells(root / "results/timing/ms8", list(M8.RTOL_CELLS.values()), WORKERS))
    return cells


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out")
    ap.add_argument("--opt", action="append", default=[], metavar="KEY=VALUE")
    a = ap.parse_args(argv)
    opts = {}
    for kv in a.opt:
        k, v = kv.split("=", 1)
        if k not in OPTIONS or v not in [str(x) for x in OPTIONS[k]]:
            ap.error(f"{k}={v}: not an option ({OPTIONS.get(k)})")
        opts[k] = type(OPTIONS[k][0])(v)
    root = C.repo_root()
    txt = report(load_cells(root), opts)
    print(txt)
    if a.out:
        Path(root / a.out).write_text(txt + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
