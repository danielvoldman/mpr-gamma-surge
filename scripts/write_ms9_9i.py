"""MS9 9i driver (DL-256 to DL-260): writes the A7 (S6 part), A9 and A10 data files and the G3 facts table from stored records and stored
class tables. Integrates nothing, judges nothing. The criteria gate runs first (refuses on any mismatch).

  .venv/Scripts/python.exe scripts/write_ms9_9i.py

Writes results/A7/a7_s6_metrics.parquet, results/A9/a9_regime_map.parquet, results/A9/a9_d31_refined_nodes_supplementary.parquet,
results/A9/a9_subgrid_agreement.parquet, results/A10/a10_controls.csv, results/A10/g3_facts.csv, docs/ms9_g3_facts.md,
results/ms9/9i/consistency.txt and a run record in results/ms9/9i. Prints the row counts, the SHA-256 of each file and the inconsistencies.
"""
import sys
import time

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import ms9_9i as N

CONFIG = "configs/ms9/9i_tables.yaml"


def write_csv(df, path):
    df.to_csv(path, index=False, lineterminator="\n")


def main() -> int:
    t0 = time.time()
    root = C.repo_root()
    cfg = C.resolve_config(CONFIG)
    fi, _ = A7.frozen_inputs(root)                          # gate: CriteriaError on any mismatch
    A7.check_a4_grid(fi["grid_step"], root)
    env = P.environment_info(with_julia=False)
    files = N.s6_files(root)
    cache, rows = {}, []
    for kind, lst, jp in files:
        rows.append(N.s6_row(jp, fi, kind, lst, root, cache))
    s6 = N.s6_frame(rows)
    bad = N.nan_reason_columns(s6, N.S6_NUMERIC)
    if bad:
        raise N.NineIError(f"{len(bad)} missing S6 values without a reason code, first: {bad[:5]}")
    a9 = N.a9_regime_map(root)
    bad = N.nan_reason_columns(a9, N.A9_NUMERIC + ("g", "h", "inside_a4_region"))
    if bad:
        raise N.NineIError(f"{len(bad)} missing A9 values without a reason code, first: {bad[:5]}")
    d31 = N.d31_nodes(root)
    sub = N.subgrid_agreement(root)
    a10 = N.a10_controls(root)
    g3 = N.g3_facts(s6, root)
    lines = N.consistency(s6, a9, root)
    outs = {
        "results/A7/a7_s6_metrics.parquet": lambda p: s6.to_parquet(p, index=False),
        "results/A9/a9_regime_map.parquet": lambda p: a9.to_parquet(p, index=False),
        "results/A9/a9_d31_refined_nodes_supplementary.parquet": lambda p: d31.to_parquet(p, index=False),
        "results/A9/a9_subgrid_agreement.parquet": lambda p: sub.to_parquet(p, index=False),
        "results/A10/a10_controls.csv": lambda p: write_csv(a10, p),
        "results/A10/g3_facts.csv": lambda p: write_csv(g3, p),
    }
    shas, counts = {}, {"a7_s6_metrics": len(s6), "a9_regime_map": len(a9), "a9_d31_refined_nodes_supplementary": len(d31),
                        "a9_subgrid_agreement": len(sub), "a10_controls": len(a10), "g3_facts": len(g3)}
    for rel, fn in outs.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        fn(p)
        shas[rel] = P.sha256_file(p)
    md = root / "docs/ms9_g3_facts.md"
    md.write_text(N.g3_markdown(g3), encoding="utf-8", newline="\n")
    shas["docs/ms9_g3_facts.md"] = P.sha256_file(md)
    out_dir = root / cfg["output"]["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    rep = out_dir / "consistency.txt"
    text = ["label facts: " + "; ".join(N.label_policy_facts(a9)), f"{len(lines)} mismatches between stored files"] + lines
    rep.write_text("\n".join(text) + "\n", encoding="utf-8", newline="\n")
    inputs = {str(jp.relative_to(root).as_posix()): P.sha256_file(jp) for _, _, jp in files}
    run = P.make_run_record(cfg, env, name="MS9_9i", status="ok", wall_time_s=time.time() - t0, inputs=inputs, outputs=dict(shas),
                            flags={"row_counts": counts, "n_mismatches": len(lines), "criteria_sha256": fi["criteria_sha256"],
                                   "threshold": fi["threshold"], "grid_step": fi["grid_step"]})
    P.write_run_record(run, out_dir / f"MS9_9i_{C.short_hash(C.config_hash(cfg))}.json")
    print("row counts:", counts)
    for k, v in shas.items():
        print(f"{v}  {k}")
    print("\n".join(text))
    print(f"git.dirty={env['git']['dirty']}, {time.time() - t0:.1f} s")
    print(N.g3_markdown(g3))
    return 0


if __name__ == "__main__":
    sys.exit(main())
