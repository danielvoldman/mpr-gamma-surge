"""8h (DL-207): O12 post-surge rate file, reported only (not a criterion). Reads the stored O12 data package (sha256 checked), integrates nothing.

Rulings (8h prompt, ruling 2): post-surge rate = mean r over a window after J_exit,run as the classifier gives it; BOTH the 1 s and the 5 s
window are columns, none is chosen; no "main episode" rule for mode N (reported as given); runs with J_exit,run at J0 are flagged, not
interpreted. J_exit,static is the last positive-to-non-positive crossing of the leading Re lambda along the path (UNVERIFIED).
Writes results/A7/a7_o12_post_surge.csv and .parquet (a7_ramp_metrics.parquet is not touched) and a run record. Every missing value
carries a reason code in its own column.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd

PACKAGE_SHA256 = "e59f7e64da73cc8a366362224ce9f2a5f3eef0cfb97bbbd8891095dafefe08a4"
J0_TOL = 1e-9
FAMILY_DIR = {"p2_linear": "ramp", "p2_sigmoid": "ramp", "S5ramp": "ramp", "p2_noise": "ramp_noise"}
COLUMNS = ["run_id", "path", "profile", "T_ramp_s", "mode", "seed", "cls", "J0", "J_exit_run", "J_exit_static", "exit_delay", "r0",
           "r_post_1s", "r_post_5s", "flag_J_exit_run_at_J0", "flag_no_J_exit_run", "reason_no_J_exit_run", "reason_J_exit_static",
           "reason_exit_delay", "reason_r_post_1s", "reason_r_post_5s"]


def _nan(x):
    return float("nan") if x is None else float(x)


def build_row(x: dict, j0: float) -> dict:
    """One output row from one data-package run; every NaN gets a reason code."""
    has_j = x.get("J_exit_run") is not None
    if has_j:
        no_j = ""
    elif not x["episode"]:
        no_j = "no_episode"
    elif not x["terminated"]:
        no_j = "episode_unterminated_at_run_end"
    else:
        no_j = "J_exit_run_not_returned"
    r1, r5 = x.get("r_mean_1s"), x.get("r_mean_5s")
    jst = x.get("J_exit_static")
    return {"run_id": x["run_id"], "path": "P2", "profile": x["profile"], "T_ramp_s": x["T_ramp_s"], "mode": x["mode"],
            "seed": -1 if x["seed"] is None else x["seed"], "cls": x["cls"], "J0": j0, "J_exit_run": _nan(x.get("J_exit_run")),
            "J_exit_static": _nan(jst), "exit_delay": _nan(x.get("exit_delay")), "r0": float(x["r0"]),
            "r_post_1s": _nan(r1), "r_post_5s": _nan(r5),
            "flag_J_exit_run_at_J0": bool(has_j and abs(x["J_exit_run"] - j0) <= J0_TOL),
            "flag_no_J_exit_run": not has_j, "reason_no_J_exit_run": no_j,
            "reason_J_exit_static": "" if jst is not None else "no_positive_to_nonpositive_crossing_of_leading_re_lambda",
            "reason_exit_delay": "" if x.get("exit_delay") is not None else ("no_J_exit_run" if not has_j else "no_J_exit_static"),
            "reason_r_post_1s": "" if r1 is not None else ("no_J_exit_run" if not has_j else "window_extends_past_run_end"),
            "reason_r_post_5s": "" if r5 is not None else ("no_J_exit_run" if not has_j else "window_extends_past_run_end")}


def check_reasons(df: pd.DataFrame) -> list:
    """(run, column) pairs with a NaN and no reason code."""
    pairs = {"J_exit_run": "reason_no_J_exit_run", "J_exit_static": "reason_J_exit_static", "exit_delay": "reason_exit_delay",
             "r_post_1s": "reason_r_post_1s", "r_post_5s": "reason_r_post_5s"}
    bad = []
    for col, rc in pairs.items():
        m = df[col].isna() & (df[rc] == "")
        bad += [(r, col) for r in df.loc[m, "run_id"]]
    for col in ("r0", "T_ramp_s", "J0"):
        bad += [(r, col) for r in df.loc[df[col].isna(), "run_id"]]
    return bad


def group_counts(df: pd.DataFrame) -> dict:
    head = df["run_id"].str.startswith("S5ramp")
    groups = {"noise-free linear (13)": (df["mode"] == "D") & (df["profile"] == "linear") & ~head,
              "noise-free sigmoid (13)": (df["mode"] == "D") & (df["profile"] == "sigmoid"),
              "headline (1)": head,
              "mode N (130)": df["mode"] == "N"}
    out = {}
    for name, m in groups.items():
        d = df[m]
        out[name] = {"n_runs": int(len(d)), "J_exit_run_defined": int((~d["flag_no_J_exit_run"]).sum()),
                     "no_J_exit_run": int(d["flag_no_J_exit_run"].sum()),
                     "no_J_exit_run_by_reason": {k: int(v) for k, v in d.loc[d["flag_no_J_exit_run"], "reason_no_J_exit_run"].value_counts().items()},
                     "J_exit_run_at_J0": int(d["flag_J_exit_run_at_J0"].sum()),
                     "r_post_1s_defined": int(d["r_post_1s"].notna().sum()), "r_post_5s_defined": int(d["r_post_5s"].notna().sum()),
                     "J_exit_static_missing": int(d["J_exit_static"].isna().sum())}
    return out


def main() -> int:
    t0 = time.time()
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    from mprsurge import config as C
    from mprsurge import provenance as P
    pkg = root / "results/A7/o12_data_package.json"
    if P.sha256_file(pkg) != PACKAGE_SHA256:
        raise SystemExit("o12_data_package.json does not match the recorded sha256")
    rows_in = json.loads(pkg.read_text(encoding="utf-8"))["runs"]
    rows = []
    for x in rows_in:
        jp = root / "results/S5" / FAMILY_DIR[x["family"]] / x["family"] / f"{x['run_id']}.json"
        j0 = float(json.loads(jp.read_text(encoding="utf-8"))["config"]["path"]["J0"])
        rows.append(build_row(x, j0))
    df = pd.DataFrame(rows, columns=COLUMNS)
    bad = check_reasons(df)
    if bad:
        raise SystemExit(f"{len(bad)} missing values without a reason code, first: {bad[:5]}")
    out = root / "results/A7"
    df.to_csv(out / "a7_o12_post_surge.csv", index=False, lineterminator="\n")
    df.to_parquet(out / "a7_o12_post_surge.parquet", index=False)
    sha_csv, sha_pq = P.sha256_file(out / "a7_o12_post_surge.csv"), P.sha256_file(out / "a7_o12_post_surge.parquet")
    counts = group_counts(df)
    cfg = C.resolve_config("configs/A7.yaml")
    env = P.environment_info(with_julia=False)
    run = P.make_run_record(cfg, env, name="O12_0000", status="ok", wall_time_s=time.time() - t0,
                            inputs={"results/A7/o12_data_package.json": PACKAGE_SHA256},
                            outputs={"a7_o12_post_surge.csv": sha_csv, "a7_o12_post_surge.parquet": sha_pq},
                            flags={"n_rows": len(df), "counts": counts})
    P.write_run_record(run, out / f"O12_0000_{C.short_hash(C.config_hash(cfg))}.json")
    print(json.dumps(counts, indent=1))
    print("csv", sha_csv, "parquet", sha_pq, "git.dirty", env["git"]["dirty"], f"{time.time() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
