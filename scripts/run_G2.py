"""G2 metrics (a), (b) and the DL-115 frequency check from saved A4/A6 results (plan 4.3 G2; MS6 step 6g, DL-132).

Analysis only: re-evaluates the A4 spectrum at ref_devalle and reads results/A6; integrates nothing and decides nothing
(G2 is the owner's). Writes results/G2/g2_metrics.json and a run record.
"""
import json
import sys

import numpy as np
import yaml

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis.hopf import _hz, leading_mode

TAU_MS, J_DV, DELTA_DV, TAU_D_DV_MS = 10.0, -21.0, 0.3, 5.0
K9_RATIO = 0.1453085        # A4 K9 maximum of Delta / eta_bar (results/A4, all three eta_bar), DL-115
BAND_HZ = 25.0


def spectrum(eta_bar):
    m = leading_mode(eta_bar, J_DV, DELTA_DV, TAU_D_DV_MS / TAU_MS)
    return {"eta_bar": float(eta_bar), "re_lambda_per_tau": m["pair_re"], "im_lambda_per_tau": m["pair_im"],
            "freq_hz": float(_hz(m["pair_im"], TAU_MS)), "r": m["r"]}


def slice_table(a6):
    ids, hp = a6["slice_ids"], a6["slice_hopf_param"]
    idx, par, f = a6["po_slice_index"], a6["po_param"], a6["po_frequency_hz"]
    rows = []
    for i, s in enumerate(map(str, ids)):
        if s.startswith("k10"):
            continue
        m = idx == i
        if not m.any():
            continue
        row = {"slice": s, "hopf_param": float(hp[i]), "n_cycle_points": int(m.sum()),
               "f_min_hz": float(f[m].min()), "f_max_hz": float(f[m].max()), "n_ge_25hz": int((f[m] >= BAND_HZ).sum())}
        if s.startswith("eta_tau_D"):    # eta_bar is the parameter; Delta is in the id
            D = float(s.split("_D")[1].split("_")[0])
            row["Delta"] = D
            row["delta_critical_at_hopf"] = K9_RATIO * float(hp[i])
            row["delta_below_critical_all_ge25_points"] = bool(np.all(D < K9_RATIO * par[m][f[m] >= BAND_HZ]))
        rows.append(row)
    return rows


def main(argv=None) -> int:
    root = C.repo_root()
    a6_path = root / "results/A6/a6_freq_map.npz"
    a6 = np.load(a6_path, allow_pickle=True)
    eta_H = yaml.safe_load((root / "configs/path_A4.yaml").read_text(encoding="utf-8"))["path"]["eta_H"]
    eta_peak = max(4.0, eta_H + 2.0)
    info = {"eta_H": eta_H, "eta_start": eta_H - 1.5, "eta_peak": eta_peak,
            "freq_check": {"at_eta_H": spectrum(eta_H), "at_eta_bar_4": spectrum(4.0)},
            "path_P1": {"start": spectrum(eta_H - 1.5), "hopf": spectrum(eta_H), "end": spectrum(eta_peak)},
            "k9_ratio": K9_RATIO, "slices": slice_table(a6)}
    out_dir = root / "results" / "G2"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "g2_metrics.json").write_text(json.dumps(info, indent=1, default=float), encoding="utf-8")
    cfg = C.resolve_config("configs/A6.yaml")
    rec = P.make_run_record(cfg, P.environment_info(with_julia=False), name="G2_0000", status="ok", wall_time_s=0.0,
                            flags={"kind": "analysis_only"}, inputs={"results/A6/a6_freq_map.npz": P.sha256_file(a6_path)},
                            outputs={"g2_metrics.json": P.sha256_file(out_dir / "g2_metrics.json")})
    P.write_run_record(rec, out_dir / "G2_0000.json")
    print(json.dumps({k: info[k] for k in ("freq_check", "path_P1")}, indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
