"""S4 mean-field driver (plan 6.2 S4; MS6 step 6c, DL-127): runs configs/S4.yaml (ref_devalle, eta_bar sweep) and
configs/S4_ceni.yaml (ref_ceni, tau_d sweep) through the runner as two processes, then reads the series back with
analysis.s4 and writes results/S4/s4_summary.npz (per-step cycle amplitude, frequency, branch up/down) and
results/S4/s4_summary.json. eta_H is layered in from configs/path_A4.yaml for the eta_bar sweep. No comparison to A5 is made here (6e).
--dry-run only resolves and writes dry records.
--net (MS6 6d, DL-128) runs configs/S4_net.yaml instead (QIF network, 15 steps, one process) and writes
results/S4/s4_net_summary.{npz,json}, with the network-against-mean-field numbers from the 6c summary (information only).
"""
import json
import subprocess
import sys
import time

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import s4

CONFIGS = {"devalle": "configs/S4.yaml", "ceni": "configs/S4_ceni.yaml", "net": "configs/S4_net.yaml"}
MF_KEYS = ("devalle", "ceni")
PATH_A4 = "configs/path_A4.yaml"


def sets_for(key: str) -> list:
    """--set overrides: the eta_bar sweep takes eta_H from path_A4.yaml (A4), not from a typed value."""
    import yaml
    if key not in ("devalle", "net"):
        return []
    eta_H = yaml.safe_load((C.repo_root() / PATH_A4).read_text(encoding="utf-8"))["path"]["eta_H"]
    return [f"path.eta_H={eta_H!r}"]


def summarise() -> tuple[dict, dict]:
    arrays, info = {}, {}
    for key in MF_KEYS:
        cfgf = CONFIGS[key]
        plan = R.build_plan(cfgf, sets_for(key))
        cell = plan.cells[0]
        with np.load(plan.out_dir / f"{cell['name']}.npz") as z:
            series = {k: z[k] for k in z.files}
        cfg = cell["cfg"]
        tab = s4.step_table(series, cfg["s4"]["read_s"], cfg["solver"]["delta0"])
        pairs = s4.branch_pairs(tab)
        for k, v in tab.items():
            arrays[f"{key}_{k}"] = v
        for k, v in pairs.items():
            arrays[f"{key}_pair_{k}"] = v
        info[key] = {"cell": cell["name"], "param": cfg["s4"]["param"], "n_steps": int(tab["step"].size),
                     "step_s": cfg["s4"]["step_s"], "read_s": cfg["s4"]["read_s"],
                     "max_abs_drift_cycle_steps": float(np.nanmax(np.abs(tab["drift"][~tab["decays"]]))),
                     "max_abs_updown_rel_diff": float(np.nanmax(np.abs(pairs["v_ptp_rel_diff"][pairs["v_ptp_up"] > 0])))}
    return arrays, info


def summarise_net() -> tuple[dict, dict]:
    """Network table, and its difference to the mean-field S4 devalle table of 6c (read from s4_summary.npz)."""
    plan = R.build_plan(CONFIGS["net"], sets_for("net"))
    cell = plan.cells[0]
    with np.load(plan.out_dir / f"{cell['name']}.npz") as z:
        series = {k: z[k] for k in z.files}
    cfg = cell["cfg"]
    tab = s4.step_table(series, cfg["s4"]["read_s"], cfg["solver"]["delta0"])
    pairs = s4.branch_pairs(tab)
    cols = ("step", "param", "up", "v_ptp", "r_ptp", "v_mean", "f_fft_hz", "f_cross_hz", "drift", "decays")
    with np.load(C.repo_root() / "results" / "S4" / "s4_summary.npz") as z:
        mf = {c: z[f"devalle_{c}"] for c in cols}
    cmp_ = s4.net_vs_mf(tab, mf, cfg["s4"]["indices"])
    arrays = {f"net_{k}": v for k, v in tab.items()} | {f"net_pair_{k}": v for k, v in pairs.items()}         | {f"cmp_{k}": v for k, v in cmp_.items()}
    info = {"cell": cell["name"], "N": cfg["network"]["N"], "n_steps": int(tab["step"].size),
            "indices": cfg["s4"]["indices"], "step_s": cfg["s4"]["step_s"], "read_s": cfg["s4"]["read_s"]}
    return arrays, info


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--net" in argv:
        argv.remove("--net")
        t0 = time.monotonic()
        rc = R.main(["--config", CONFIGS["net"], *[x for s in sets_for("net") for x in ("--set", s)], *argv])
        if rc or "--dry-run" in argv:
            return rc
        arrays, info = summarise_net()
        out = C.repo_root() / "results" / "S4"
        P.atomic_save_npz(out / "s4_net_summary.npz", arrays)
        info["wall_time_s"] = time.monotonic() - t0
        info["s4_net_summary.npz_sha256"] = P.sha256_file(out / "s4_net_summary.npz")
        (out / "s4_net_summary.json").write_text(json.dumps(info, indent=1, default=float), encoding="utf-8")
        print(json.dumps(info, indent=1, default=float))
        return 0
    if "--child" in argv:                      # one config, as its own runner process
        i = argv.index("--child")
        key = argv[i + 1]
        rest = argv[:i] + argv[i + 2:]
        return R.main(["--config", CONFIGS[key], *[x for s in sets_for(key) for x in ("--set", s)], *rest])
    t0 = time.monotonic()
    procs = [subprocess.Popen([sys.executable, str(C.repo_root() / "scripts" / "run_S4.py"),
                               "--child", key, *argv]) for key in MF_KEYS]
    rc = max(p.wait() for p in procs)
    if rc or "--dry-run" in argv:
        return rc
    arrays, info = summarise()
    out = C.repo_root() / "results" / "S4"
    P.atomic_save_npz(out / "s4_summary.npz", arrays)
    info["wall_time_s"] = time.monotonic() - t0
    info["s4_summary.npz_sha256"] = P.sha256_file(out / "s4_summary.npz")
    (out / "s4_summary.json").write_text(json.dumps(info, indent=1, default=float), encoding="utf-8")
    print(json.dumps(info, indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
