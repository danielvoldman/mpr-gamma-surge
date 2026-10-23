"""MS9 9j driver (DL-261 to DL-266): writes the second version of the A9 regime-map table from the stored 9i table. Integrates nothing,
judges nothing. The criteria gate runs first; the stored 9i table must still have the SHA-256 recorded in DL-260.

  .venv/Scripts/python.exe scripts/write_ms9_9j.py

Writes results/A9/a9_regime_map_v2.parquet (the stored a9_regime_map.parquet is not touched), results/ms9/9j/a9_v2_report.txt and a run
record in results/ms9/9j. Prints the SHA-256, the Hopf-frequency fill, the structural-flag counts on surge-class cells and the failure labels.
"""
import json
import sys
import time

import pandas as pd

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import ms9_9j as N

CONFIG = "configs/ms9/9j_tables.yaml"
OLD = "results/A9/a9_regime_map.parquet"
OLD_SHA = "7ed857c12ba208a23d3e1dc2fc463606ff612ea9d912b41e80f4cbc1c2997b06"      # DL-260
NEW = "results/A9/a9_regime_map_v2.parquet"


def main() -> int:
    t0 = time.time()
    root = C.repo_root()
    cfg = C.resolve_config(CONFIG)
    fi, _ = A7.frozen_inputs(root)                          # gate: CriteriaError on any mismatch
    env = P.environment_info(with_julia=False)
    have = P.sha256_file(root / OLD)
    if have != OLD_SHA:
        raise SystemExit(f"{OLD} hashes to {have}, DL-260 records {OLD_SHA}: refusing")
    old = pd.read_parquet(root / OLD)
    new, notes = N.a9_v2(old, tau_ms=float(cfg["model"]["tau_ms"]))
    out = root / NEW
    new.to_parquet(out, index=False)
    sha = P.sha256_file(out)
    fc, ff = N.flag_counts(new), N.failure_facts(new)
    hf = new.loc[new["map"] == "1", "hopf_f_hz"]
    lines = [f"stored 9i table {OLD} sha256 {have} (= DL-260)", f"new table {NEW}: {len(new)} rows, {len(new.columns)} columns, sha256 {sha}"]
    lines += notes
    lines.append(f"map 1 hopf_f_hz: {int(hf.notna().sum())} of {len(hf)} filled, min {hf.min():.2f}, max {hf.max():.2f} Hz; "
                 f"below 25 Hz: {int((hf < 25).sum())}; headline {float(new.loc[new['map'] == 'headline', 'hopf_f_hz'].iloc[0]):.4f} Hz")
    lines.append("structural flags a to f on surge-class cells (stored flags, not interpreted):")
    for m, d in fc.items():
        lines.append(f"  map {m}: {d['any_flag']} of {d['surge_cells']} surge-class cells carry some flag; per letter {d['per_letter']}; "
                     f"cells with a flag by class {d['by_class']}; combinations {d['combos']}")
    lines.append("failure_label on non-surge cells: " + json.dumps(ff))
    text = "\n".join(lines) + "\n"
    out_dir = root / cfg["output"]["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "a9_v2_report.txt").write_text(text, encoding="utf-8", newline="\n")
    run = P.make_run_record(cfg, env, name="MS9_9j", status="ok", wall_time_s=time.time() - t0, inputs={OLD: have},
                            outputs={NEW: sha}, flags={"rows": len(new), "criteria_sha256": fi["criteria_sha256"]})
    P.write_run_record(run, out_dir / f"MS9_9j_{C.short_hash(C.config_hash(cfg))}.json")
    print(text)
    print(f"git.dirty={env['git']['dirty']}, {time.time() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
