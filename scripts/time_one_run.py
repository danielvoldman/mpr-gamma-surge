"""Timing driver (plan 9.2 steps 1 and 2; MS3 step 3b, DL-094, DL-095).

Times one timing cell: the run file (configs/S5.yaml) layered with configs/timing/<cell>.yaml, run
--repeat times in this process, each repeat timed on its own. The Numba warm-up (mode N) is timed
separately and is not part of any repeat. Each repeat is limited to --limit-s (default 3600, D-6);
a repeat that fails or reaches the limit is recorded as such, the remaining repeats are not run and
no solver setting is changed. Writes <out-dir>/<cell>.json, a record of kind `timing` (D-8) with the
provenance fields of 6.6. The wall time is of the integration call only; nothing is saved but the record.

--workers N (3d) instead times N concurrent copies of the cell per batch through the runner's spawn pool
(mprsurge.timing_run), --repeat batches, and writes <out-dir>/workers_<N>.json.

Drivers only integrate: summaries come from mprsurge.analysis.timing. No extrapolation here (3e).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")               # as the runner's workers (single_thread_env, 9.1)

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge import simulate_mf as S
from mprsurge import timing_run as TR
from mprsurge.analysis import timing as T

KIND = "timing"
DEFAULT_LIMIT_S = 3600.0                         # D-6
PS = ("powershell", "-NoProfile", "-NonInteractive", "-Command")


def _ps(cmd: str, timeout: float = 60.0) -> str | None:
    try:
        out = subprocess.run([*PS, cmd], capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def machine_state() -> dict:
    """What can be read without admin rights: power plan, AC or battery, CPU load, the busiest processes."""
    state = {"time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        plan = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True, timeout=30)
        state["power_plan"] = plan.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        state["power_plan"] = None
    bat = _ps("Get-CimInstance Win32_Battery | Select-Object -ExpandProperty BatteryStatus")
    state["battery_status"] = bat if bat else "no battery reported"      # 2 = on AC (Win32_Battery)
    load = _ps("(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average")
    state["cpu_load_percent"] = float(load) if load else None
    top = _ps("Get-CimInstance Win32_PerfFormattedData_PerfProc_Process | "
              "Where-Object { $_.Name -ne '_Total' -and $_.Name -ne 'Idle' } | "
              "Sort-Object PercentProcessorTime -Descending | Select-Object -First 5 | "
              "ForEach-Object { '{0}:{1}' -f $_.Name, $_.PercentProcessorTime }")
    state["top_processes_cpu_percent"] = top.splitlines() if top else None
    return state


run_once = TR.run_once


def _updates(cfg: dict):
    """Neuron-updates of one run of a network cell (N x tau / dt), None for mean-field cells (5f)."""
    return T.network_updates(cfg) if cfg["run"]["kind"] == "network" else None


def time_cell(cfg: dict, repeat: int, limit_s: float, say=print) -> dict:
    """Warm up, then time `repeat` runs. Stops at the first repeat that is not ok."""
    compile_s = None
    if cfg["run"]["kind"] == "mf_noisy":
        t0 = time.perf_counter()
        S.warm_up()
        compile_s = time.perf_counter() - t0
        say(f"  warm-up (Numba, mode N): {compile_s:.2f} s, not in the repeats")
    elif cfg["run"]["kind"] == "network":
        from mprsurge import qif_network as Q
        t0 = time.perf_counter()
        Q.warm_up()
        compile_s = time.perf_counter() - t0
        say(f"  warm-up (Numba, network kernel): {compile_s:.2f} s, not in the repeats")
    tau = T.tau_simulated(cfg)
    repeats = []
    for i in range(repeat):
        r = run_once(cfg, limit_s)
        r["s_per_tau"] = T.s_per_tau(r["wall_s"], tau)
        repeats.append(r)
        say(f"  repeat {i + 1}/{repeat}: {r['status']}  {r['wall_s']:.2f} s  ({r['s_per_tau'] * 1e4:.3f} s per 1e4 tau)")
        if r["status"] != "ok":
            break
    ok = [r["wall_s"] for r in repeats if r["status"] == "ok"]
    statuses = {r["status"] for r in repeats}
    status = "failed" if "failed" in statuses else "timeout" if "timeout" in statuses else "ok"
    out = {"kind": KIND, "status": status, "tau_simulated": tau, "updates": _updates(cfg), "repeats_requested": repeat,
           "repeats_done": len(repeats), "limit_s": limit_s, "compile_warmup_s": compile_s, "repeats": repeats}
    if ok:
        summ = T.summarise_repeats(ok)
        spt = T.s_per_tau(summ["median_s"], tau)
        out.update(summary=summ, median_s_per_tau=spt, median_s_per_1e4_tau=spt * 1e4)
        steps = [r["n_steps"] or r["nfev"] for r in repeats if r["status"] == "ok" and (r["n_steps"] or r["nfev"])]
        if steps:
            out.update(solver_count=steps[0], solver_count_name="n_steps" if repeats[0]["n_steps"] else "nfev",
                       median_s_per_solver_count=summ["median_s"] / steps[0])
    return out


def build_record(cfg: dict, cell: str, timing: dict, state_before: dict, state_after: dict) -> dict:
    env = P.environment_info(with_julia=False)
    rec = P.make_run_record(cfg, env, name=cell, status=timing["status"],
                            message=next((r["message"] for r in timing["repeats"] if r["status"] != "ok"), "ok"),
                            wall_time_s=sum(r["wall_s"] for r in timing["repeats"]),
                            flags={"eta_path_status": cfg["path"]["eta_path_status"],
                                   "eta_path_note": ("provisional, UNVERIFIED until A4 (MS5), DL-094"
                                                     if cfg["path"]["eta_path_status"] == "provisional"
                                                     else "explicit, see config"),
                                   "sigma": ({"value": cfg["noise"]["sigma"], "status": "UNVERIFIED, not calibrated (D-4, DL-095)"}
                                             if cfg["run"]["kind"] == "mf_noisy" else None)})
    rec["kind"] = KIND
    rec["cell"] = cell
    rec["timing"] = timing
    rec["machine_state"] = {"before": state_before, "after": state_after}
    return rec


def time_workers(cfg: dict, n: int, batches: int, limit_s: float, say=print) -> dict:
    """3d: `batches` batches of n concurrent copies of the cell; each copy timed on its own."""
    out = []
    for i in range(batches):
        b = TR.run_batch(cfg, n, limit_s)
        walls = [c["wall_s"] for c in b["copies"]]
        say(f"  batch {i + 1}/{batches}: {b['status']}  n={n}  copies {min(walls):.1f}-{max(walls):.1f} s  "
            f"batch wall {b['batch_wall_s']:.1f} s  start spread {b['start_spread_s']:.2f} s  pids {b['distinct_pids']}")
        b["run_walls_s"] = walls
        b["machine_state_after"] = machine_state()
        out.append(b)
        if b["status"] != "ok":
            break
    done = [b for b in out if b["status"] == "ok"]
    res = {"kind": KIND, "mode": "workers", "workers": n, "status": "ok" if len(done) == len(out) == batches else "not ok",
           "tau_simulated": T.tau_simulated(cfg), "updates": _updates(cfg), "batches_requested": batches, "limit_s": limit_s, "batches": out}
    if done:
        res["summary"] = T.worker_summary(n, done)
    return res


def main_workers(args, cell: str) -> int:
    out_dir = Path(args.out_dir) if args.out_dir else C.repo_root() / "results" / KIND
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg = T.resolve_cell(args.config, cell, args.sets)
    print(f"{cell}: {args.workers} concurrent copies x {args.repeat} batches, tau simulated {T.tau_simulated(cfg):,.0f}, "
          f"eta path {cfg['path']['eta_path_status']}", flush=True)
    before = machine_state()
    timing = time_workers(cfg, args.workers, args.repeat, args.limit_s, say=lambda m: print(m, flush=True))
    rec = build_record(cfg, cell, {**timing, "repeats": []}, before, machine_state())
    rec["status"] = timing["status"]
    P.atomic_write_json(out_dir / f"workers_{args.workers}.json", rec)
    if "summary" in timing:
        s = timing["summary"]
        print(f"workers {args.workers}: per-run median {s['per_run']['median_s']:.2f} s, batch wall median "
              f"{s['batch_wall']['median_s']:.2f} s, throughput {s['throughput_runs_per_h']:.1f} runs/h")
    return 0 if timing["status"] == "ok" else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="time_one_run", description=__doc__.split("\n")[0])
    ap.add_argument("--config", default="configs/S5.yaml")
    ap.add_argument("--cell", required=True, help="a cell of configs/timing/, or 'all'")
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--limit-s", type=float, default=DEFAULT_LIMIT_S, help="wall limit per repeat (D-6)")
    ap.add_argument("--out-dir", default=None, help="default: results/timing")
    ap.add_argument("--workers", type=int, default=None, help="3d: time N concurrent copies of the cell per batch (--repeat batches)")
    ap.add_argument("--set", dest="sets", nargs="+", default=[], metavar="KEY=VALUE", help="config overrides")
    args = ap.parse_args(argv)
    if args.workers is not None:
        if args.cell == "all" or args.workers < 1:
            ap.error("--workers needs one named --cell and N >= 1")
        return main_workers(args, args.cell)
    out_dir = Path(args.out_dir) if args.out_dir else C.repo_root() / "results" / KIND
    out_dir.mkdir(parents=True, exist_ok=True)
    cells = list(T.CELLS) if args.cell == "all" else [args.cell]
    table = []
    for cell in cells:
        cfg = T.resolve_cell(args.config, cell, args.sets)
        if cfg["run"]["kind"] == "mf_noisy" and cfg["seeds"]["spawn_key"] is None:
            cfg = T.resolve_cell(args.config, cell, [*args.sets, "seeds.spawn_key=[0]"])   # seed index 0, as the runner
        print(f"{cell}: {cfg['run']['kind']} {cfg['model']['type']} {cfg['solver']['method']} rtol {cfg['solver']['rtol']:g}, "
              f"tau simulated {T.tau_simulated(cfg):,.0f}, eta path {cfg['path']['eta_path_status']}", flush=True)
        before = machine_state()
        timing = time_cell(cfg, args.repeat, args.limit_s, say=lambda m: print(m, flush=True))
        rec = build_record(cfg, cell, timing, before, machine_state())
        P.atomic_write_json(out_dir / f"{cell}.json", rec)
        table.append((cell, cfg, timing))
    print_table(table)
    return 0 if all(t["status"] == "ok" for _, _, t in table) else 1


def print_table(table) -> None:
    head = f"{'cell':12s} {'tau simulated':>13s} {'median s/run':>13s} {'s per 1e4 tau':>14s} {'repeats':>8s}  status"
    print("\n" + head + "\n" + "-" * len(head))
    for cell, cfg, t in table:
        flag = ("" if cfg["path"]["eta_path_status"] == "explicit" else f"  [eta path {cfg['path']['eta_path_status']}]")
        if cfg["run"]["kind"] == "network":
            flag += "  [network, provisional eta path as the mean-field cells]"
        if cfg["run"]["kind"] == "mf_noisy":
            flag += "  [sigma 1e-3 UNVERIFIED, not calibrated]"
        if "summary" in t:
            med, per = f"{t['summary']['median_s']:.2f}", f"{t['median_s_per_1e4_tau']:.3f}"
        else:
            med = per = "-"
        print(f"{cell:12s} {t['tau_simulated']:13,.0f} {med:>13s} {per:>14s} {str(t['repeats_done']) + '/' + str(t['repeats_requested']):>8s}  {t['status']}{flag}")


if __name__ == "__main__":
    sys.exit(main())
