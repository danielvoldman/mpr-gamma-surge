"""S2 driver (plan 6.2 S2, 5.2 A3; MS4 step 4b): resolves configs/S2.yaml, checks that its eta path ends 1 beyond
each A1 fold, and checks the ramp breakpoints of every T_ramp cell. With --dry-run it prints the fold values and
the run list and writes the dry-run records; nothing integrates. Without --dry-run it hands the config to the
runner (the real S2 run is step 4d).
"""
import sys

import numpy as np

from mprsurge import config as C
from mprsurge import ramps
from mprsurge import run as R
from mprsurge.analysis import bifurcation as B
from mprsurge.units import s_to_tau

CONFIG = "configs/S2.yaml"
MARGIN = 1.0        # eta_bar units beyond each fold (plan 6.2 S2)
TOL = 1e-12


def fold_values(cfg: dict) -> tuple[float, float]:
    """(lower fold, upper fold) in eta_bar from the A1 formula at the config's J and Delta."""
    folds = np.sort(B.fold_etas(cfg["model"]["J"], cfg["model"]["Delta"]))
    if len(folds) != 2:
        raise C.ConfigError(f"S2: expected 2 folds at J = {cfg['model']['J']}, found {len(folds)}")
    return float(folds[0]), float(folds[1])


def check_path(cfg: dict, fold_low: float, fold_up: float) -> None:
    p = cfg["path"]
    if abs(p["eta_start"] - (fold_low - MARGIN)) > TOL or abs(p["eta_peak"] - (fold_up + MARGIN)) > TOL:
        raise C.ConfigError(f"S2: eta path ({p['eta_start']}, {p['eta_peak']}) is not (fold_low - 1, fold_up + 1) = "
                            f"({fold_low - MARGIN}, {fold_up + MARGIN})")


def check_breakpoints(cfg: dict) -> dict:
    """Ramp breakpoints of one cell: t_on and t_on + T in tau; eta at both ends and at the ends of the run."""
    tau = cfg["model"]["tau_ms"]
    path = ramps.make_path(cfg)
    t_on, t_end = s_to_tau(cfg["path"]["t_on_s"], tau), s_to_tau(cfg["path"]["t_on_s"] + cfg["path"]["T_ramp_s"], tau)
    bp = [float(x) for x in path.breakpoints]
    ok = (np.allclose(bp, [t_on, t_end], rtol=0, atol=1e-9) and abs(path.t_ramp_end - t_end) <= 1e-9
          and abs(float(path.eta(t_on)) - cfg["path"]["eta_start"]) <= TOL
          and abs(float(path.eta(t_end)) - cfg["path"]["eta_peak"]) <= TOL
          and abs(float(path.eta(0.0)) - cfg["path"]["eta_start"]) <= TOL)
    if not ok:
        raise C.ConfigError(f"S2: ramp breakpoints {bp} do not match t_on = {t_on}, t_on + T = {t_end}")
    return {"t_on": t_on, "t_ramp_end": t_end, "t_end": t_end + s_to_tau(cfg["durations"]["hold_s"], tau)}


def dry_run(argv) -> int:
    try:
        plan = R.build_plan(CONFIG, [a for prev, a in zip([""] + argv, argv) if prev == "--set"])
        lo, up = fold_values(plan.cfg)
        check_path(plan.cfg, lo, up)
        rows = [check_breakpoints(c["cfg"]) for c in plan.cells]
    except C.ConfigError as exc:
        print(f"S2 config error: {exc}", file=sys.stderr)
        return 2
    print(f"S2 folds (A1 formula, J = {plan.cfg['model']['J']}, Delta = {plan.cfg['model']['Delta']}): "
          f"lower {lo!r}, upper {up!r}; eta path {plan.cfg['path']['eta_start']!r} -> {plan.cfg['path']['eta_peak']!r}")
    print(f"S2 runs: {len(plan.cells)}; baseline {plan.cfg['durations']['baseline_s']} s, hold {plan.cfg['durations']['hold_s']} s, "
          f"band {plan.cfg['analysis']['band_primary_hz']} Hz, dt_out {plan.cfg['solver']['dt_out_ms']} ms")
    print(f"{'idx':>3} {'T_ramp_s':>10} {'t_on_tau':>9} {'ramp_end_tau':>13} {'tau_total':>10}  hash12")
    for c, r in zip(plan.cells, rows):
        print(f"{c['index']:>3} {c['cfg']['path']['T_ramp_s']:>10.4f} {r['t_on']:>9.1f} {r['t_ramp_end']:>13.1f} "
              f"{r['t_end']:>10.1f}  {c['hash12']}")
    print(f"S2 total simulated: {sum(r['t_end'] for r in rows):.0f} tau")
    return R.main(["--config", CONFIG, *argv])


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--dry-run" in argv:
        return dry_run(argv)
    return R.main(["--config", CONFIG, *argv])


if __name__ == "__main__":
    sys.exit(main())
