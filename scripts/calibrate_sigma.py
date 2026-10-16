"""Sigma calibration driver (plan 6.4, D18, CP21; MS5 step 5h, DL-120). Runs the network baseline (configs/sigma_net.yaml),
the mean-field noisy trial runs (configs/sigma_mf.yaml, two trial sigmas), then the mean-field noisy check at the fitted
sigma, and writes results/sigma/sigma_summary.json. The runs go through the runner (provenance records); the std
arithmetic is in analysis/sigma.py. It does not write sigma into any config.
"""
import json
import sys
import time

import numpy as np

from mprsurge import config as C
from mprsurge import run as R
from mprsurge.analysis import sigma as S


def series_stds(config: str, sets=()) -> dict:
    """Axis value (noise.sigma, or None) -> list of per-seed baseline std of v, in seed order."""
    plan = R.build_plan(config, list(sets))
    out = {}
    for c in plan.cells:
        with np.load(plan.out_dir / f"{c['name']}.npz") as z:
            v = z["v"]
        out.setdefault(c["cfg"]["noise"]["sigma"], []).append(S.baseline_std(v))
    return out


def main(argv=None) -> int:
    t0 = time.monotonic()
    rc = R.main(["--config", "configs/sigma_net.yaml"])
    rc = max(rc, R.main(["--config", "configs/sigma_mf.yaml"]))
    if rc:
        return rc
    net = next(iter(series_stds("configs/sigma_net.yaml").values()))
    trial = series_stds("configs/sigma_mf.yaml")
    sig_t = sorted(trial)
    mf_means = [float(np.mean(trial[s])) for s in sig_t]
    target = net[0]                       # the plan's single baseline run: seed index 0
    sigma = S.match_sigma(sig_t, mf_means, target)
    sigma_mean = S.match_sigma(sig_t, mf_means, float(np.mean(net)))
    # check: mean-field noisy at the fitted sigma, 10 seeds
    sets = [f"noise.sigma={sigma!r}", f"sweep.x_values=[{sigma!r}]"]
    rc = R.main(["--config", "configs/sigma_mf.yaml", *[x for s in sets for x in ("--set", s)]])
    if rc:
        return rc
    chk = next(iter(series_stds("configs/sigma_mf.yaml", sets).values()))
    # per-seed sigma: each network seed matched on its own, the seed-to-seed spread of the calibration
    k = S.slope_through_origin(sig_t, mf_means)
    summary = {"net_std": S.spread(net), "net_std_seed0": target, "net_std_per_seed": net,
               "trial_sigma": sig_t, "trial_mf_std": {str(s): S.spread(trial[s]) for s in sig_t},
               "linearity_max_rel_dev": S.linearity(sig_t, mf_means), "std_per_unit_sigma": k,
               "sigma_seed0": sigma, "sigma_net_mean": sigma_mean,
               "sigma_per_net_seed": [x / k for x in net], "sigma_per_net_seed_spread": S.spread([x / k for x in net]),
               "check_mf_std": S.spread(chk), "check_mf_std_per_seed": chk,
               "check_rel_diff_to_seed0": float(np.mean(chk) / target - 1.0),
               "check_rel_diff_to_net_mean": float(np.mean(chk) / np.mean(net) - 1.0),
               "wall_time_s": time.monotonic() - t0}
    (C.repo_root() / "results" / "sigma" / "sigma_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
