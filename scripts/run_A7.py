"""8e driver (DL-179): A7 per-run ramp metrics over the stored S5 and S13 records. Integrates nothing, judges nothing.
Writes results/A7/a7_ramp_metrics.parquet and a run record in results/A7. The criteria gate runs first (refuses on any mismatch)."""
import sys
import time

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a7

CONFIG = "configs/A7.yaml"
OUT = "results/A7/a7_ramp_metrics.parquet"


def main() -> int:
    t0 = time.time()
    root = C.repo_root()
    cfg = C.resolve_config(CONFIG)
    fi, info = a7.frozen_inputs(root)                       # gate: CriteriaError on any mismatch
    a7.check_a4_grid(fi["grid_step"], root)
    env = P.environment_info(with_julia=False)
    files = a7.record_files(root)
    cache, rows = {}, []
    for lst, jp in files:
        rows.append(a7.run_row(jp, fi, lst, cache))
    df = a7.to_frame(rows)
    bad = a7.check_reasons(df)
    if bad:
        raise a7.A7Error(f"{len(bad)} missing values without a reason code, first: {bad[:5]}")
    out = root / OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    sha = P.sha256_file(out)
    inputs = {str(jp.relative_to(root).as_posix()): P.sha256_file(jp) for _, jp in files}
    run = P.make_run_record(cfg, env, name="A7_0000", status="ok", wall_time_s=time.time() - t0, inputs=inputs,
                            outputs={"a7_ramp_metrics.parquet": sha},
                            flags={"n_rows": len(df), "n_columns": len(df.columns), "criteria_sha256": fi["criteria_sha256"],
                                   "grid_step": fi["grid_step"], "threshold": fi["threshold"], "a_ref": fi["a_ref"]})
    P.write_run_record(run, out.parent / f"A7_0000_{C.short_hash(C.config_hash(cfg))}.json")
    print(f"{len(df)} rows, {len(df.columns)} columns, sha256 {sha}, git.dirty={env['git']['dirty']}, {time.time() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
