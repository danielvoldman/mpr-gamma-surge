"""8f4 analysis (DL-194): the two supplementary start-distance runs of the headline path against the headline (start distance 1.5).
Analysis only: reads stored records, integrates nothing, changes no rule. Rows come from a7.run_row (unchanged A7 code). Writes the NEW file
results/A7/rb_diag_startdist.json; no existing rb_eval or rb_diag file is touched. Label: supplementary; no G6 verdict.
"""
import json
import sys
from pathlib import Path

import numpy as np

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a7

LABEL = "supplementary"
KEEP = ("run_id", "config_hash12", "git_commit", "start_distance", "eta_start", "eta_H", "T_ramp_s", "delta0", "cls", "class_reason", "provisional",
        "onset_cross_s", "eta_onset_cross", "delay_eta_cross", "onset_s", "eta_onset", "delay_eta", "end_s", "duration_s", "terminated",
        "peak_power_abs", "peak_power_rel", "f_pk_hz", "t_pred_s", "eta_pred", "delay_eta_pred", "I_min", "in_range", "t_pred_in_run",
        "floor", "match_err_steps", "onset_cross_minus_t_pred_s", "nan_reasons")


def clean(r):
    return {k: (None if isinstance(r.get(k), float) and np.isnan(r[k]) else (r[k].item() if hasattr(r.get(k), "item") else r.get(k))) for k in KEEP}


def main() -> int:
    root = C.repo_root()
    fi, _ = a7.frozen_inputs(root)
    cache = {}
    head = next(Path(root / "results/S5/ramp").rglob("S5ramp_0000_240de3ef73be.json"))
    runs = {"1.5": (head, "headline (existing S5 run)")}
    for jp in sorted((root / "results/ms8_diag/startdist").glob("supp_*.json")):
        rec = P.read_run_record(jp)
        assert rec["flags"]["label"] == LABEL
        runs[repr(float(rec["flags"]["start_distance"]))] = (jp, LABEL)
    rows = {}
    for sd, (jp, role) in runs.items():
        r = clean(a7.run_row(jp, fi, "SUPP", cache))
        r["role"] = role
        r["record"] = jp.name
        r["record_git_dirty"] = P.read_run_record(jp)["git"]["dirty"]
        rows[sd] = r
    base = rows["1.5"]
    for sd, r in rows.items():
        r["same_class_as_headline"] = r["cls"] == base["cls"]
        for k in ("onset_cross_s", "eta_onset_cross", "delay_eta_cross", "delay_eta", "duration_s", "peak_power_abs", "f_pk_hz"):
            r[f"shift_{k}"] = None if (r[k] is None or base[k] is None) else r[k] - base[k]
    out = {"label": LABEL, "reason": "post-hoc, after the 8f RB5 reading (P1 changes class with start distance at 9 of 13 T_ramp); the headline path was never run at "
           "other start distances (M-3 not adopted); outside S5, S13 and every rb_eval manifest; feeds no gate; no G6 verdict",
           "threshold": fi["threshold"], "runs": rows}
    p = root / "results/A7/rb_diag_startdist.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rows, indent=1, default=str), "\nsha256", P.sha256_file(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
