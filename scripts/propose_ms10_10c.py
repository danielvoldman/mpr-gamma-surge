"""MS10 10c: three proposed S8 map cells per stratum (R14, DL-288). Reads docs/ms10_10b_s8_candidates.csv only; integrates nothing, chooses nothing.

  .venv/Scripts/python.exe scripts/propose_ms10_10c.py [--out docs/ms10_10c_s8_proposals.csv]

Strata: class (D-tr, D-none) x Delta side of the median of the 30 map-1 Delta values (reading ours, UNVERIFIED: one median of the axis,
0.305, for both classes). Eligible: dist_refined > 1 original cell (R14; the distance is a selection aid only, R12). Presentation rule
for the three per stratum (ours, UNVERIFIED, a mechanical spread and not a recommendation): eligible cells sorted by (j, i); the cells at
positions round(n (2k + 1) / 6), k = 0, 1, 2.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from mprsurge import config as C

COLS = ["stratum", "i", "j", "Delta", "tau_d_ms", "class", "onset_s", "f_pk_hz", "hopf_found", "hopf_f_hz", "eta_start", "base_rate_hz",
        "dist_refined", "subgrid_modeN_modal", "subgrid_modeN_counts", "run_id"]


def propose(d: pd.DataFrame) -> pd.DataFrame:
    med = float(np.median(np.sort(d["Delta"].unique())))
    out = []
    for cls in ("D-tr", "D-none"):
        for side, sel in (("below", d["Delta"] < med), ("above", d["Delta"] > med)):
            e = d[(d["class"] == cls) & sel & (d["dist_refined"] > 1.0)].sort_values(["j", "i"]).reset_index(drop=True)
            for k in range(3):
                r = e.iloc[int(round(len(e) * (2 * k + 1) / 6))].copy()
                r["stratum"] = f"{cls} {side} median ({len(e)} eligible)"
                out.append(r)
    return pd.DataFrame(out)[COLS]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/ms10_10c_s8_proposals.csv")
    a = ap.parse_args(argv)
    t = propose(pd.read_csv(C.repo_root() / "docs/ms10_10b_s8_candidates.csv"))
    t.to_csv(C.repo_root() / a.out, index=False)
    print(t.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
