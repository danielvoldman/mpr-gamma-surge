"""A3 analysis driver (plan 5.2 A3; MS4 step 4d): applies analysis.sn_ramp to each stored S2 series under
results/A3/S2/ and writes results/A3/a3_sn_ramp.parquet (one row per T_ramp). Analysis only: nothing is
integrated, and no pass or fail is judged here (4e). The 0.3 and 0.7 jump fractions are information only.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from mprsurge import config as C
from mprsurge.analysis import sn_ramp as SN

ROOT = C.repo_root()
SERIES = ROOT / "results" / "A3" / "S2"
OUT = ROOT / "results" / "A3" / "a3_sn_ramp.parquet"
CONFIG = "configs/S2.yaml"


def upper_fold(cfg: dict) -> float:
    """Fold crossed by the upward ramp = the upper A1 fold (formula, DL-108 (a))."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import run_S2
    return run_S2.fold_values(cfg)[1]


def main(series=SERIES, out=OUT) -> int:
    cfg = C.resolve_config(ROOT / CONFIG, {})
    fold = upper_fold(cfg)
    band = tuple(cfg["analysis"]["band_primary_hz"])
    rows = []
    for rec_path in sorted(Path(series).glob("S2_*_*.json")):
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
        if rec.get("status") != "ok":
            rows.append({"run": rec_path.stem, "status": rec.get("status"), "ring_class": "failed"})
            continue
        d = np.load(rec_path.with_suffix(".npz"))
        T = float(rec["config"]["path"]["T_ramp_s"]) if "config" in rec else np.nan
        row = {"run": rec_path.stem, "status": "ok", "T_ramp_s": T, "wall_time_s": rec.get("wall_time_s")}
        a = SN.analyse_trajectory(d["t_ms"], d["r"], d["v"], d["eta"], fold, band)
        row.update(t_jump_s=a["t_jump_s"], eta_jump=a["eta_jump"], fold_eta=a["fold_eta"],
                   offset=a["offset"], offset_steps=a["offset_steps"], rate=a["rate"], se=a["se"],
                   cycles_fit=a["cycles_fit"], n_fit=a["n_fit"], ring_class=a["ring_class"],
                   direction=a["direction"], change_frac=a["change_frac"])
        for f in (0.3, 0.7):
            j = SN.detect_jump(np.asarray(d["t_ms"]) * 1e-3, d["r"], d["eta"], frac=f)
            tag = f"f{int(round(f * 10)):02d}"
            row[f"t_jump_s_{tag}"] = j["t_jump_s"]
            row[f"eta_jump_{tag}"] = j["eta_jump"]
            row[f"offset_steps_{tag}"] = (j["eta_jump"] - fold) / SN.A1_STEP if j["jump"] else np.nan
        rows.append(row)
    df = pd.DataFrame(rows).sort_values("T_ramp_s").reset_index(drop=True)
    df.to_parquet(out)
    print(f"wrote {out} ({len(df)} rows)")
    print(df[["T_ramp_s", "ring_class", "offset_steps", "wall_time_s"]].to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
