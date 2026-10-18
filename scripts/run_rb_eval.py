"""8f driver (DL-181 to DL-185): RB3 / RB5 / RB6 status numbers from the stored A7 table. Integrates nothing, makes no G6 statement.
Reads results/A7/a7_ramp_metrics.parquet, writes results/A7/rb_eval_ms8.json and results/A7/rb_eval_ms8_table.txt and a run record."""
import json
import sys
import time

import pandas as pd

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a7, rb_eval, rb_tables

CONFIG = "configs/A7.yaml"
TABLE = "results/A7/a7_ramp_metrics.parquet"
OUT_JSON = "results/A7/rb_eval_ms8.json"
OUT_TXT = "results/A7/rb_eval_ms8_table.txt"


def main() -> int:
    t0 = time.time()
    root = C.repo_root()
    cfg = C.resolve_config(CONFIG)
    fi, info = a7.frozen_inputs(root)                       # gate: CriteriaError on any mismatch
    env = P.environment_info(with_julia=False)
    tab = root / TABLE
    df = pd.read_parquet(tab)
    if set(df.criteria_sha256) != {fi["criteria_sha256"]}:
        raise SystemExit("parquet was written under a different frozen file")
    fv = rb_eval.frozen_values(root)
    res = rb_eval.evaluate(df, fv)
    records = {jp.stem: jp for _, jp in a7.record_files(root)}
    res["no_t_pred"]["split"] = rb_eval.no_t_pred_split(df, fi, records)
    res["input"] = {"table": TABLE, "table_sha256": P.sha256_file(tab), "n_rows": int(len(df))}
    out = root / OUT_JSON
    out.write_text(json.dumps(res, indent=1, sort_keys=False, default=str), encoding="utf-8")
    txt = root / OUT_TXT
    txt.write_text(rb_tables.render(res), encoding="utf-8")
    run = P.make_run_record(cfg, env, name="RBEVAL_0000", status="ok", wall_time_s=time.time() - t0, inputs={TABLE: res["input"]["table_sha256"]},
                            outputs={"rb_eval_ms8.json": P.sha256_file(out), "rb_eval_ms8_table.txt": P.sha256_file(txt)},
                            flags={"criteria_sha256": fi["criteria_sha256"]})
    P.write_run_record(run, out.parent / f"RBEVAL_0000_{C.short_hash(C.config_hash(cfg))}.json")
    print(f"json {P.sha256_file(out)}\ntable {P.sha256_file(txt)}\ngit.dirty={env['git']['dirty']} {time.time() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
