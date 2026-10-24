"""MS10 10c: timing gate on the final lists (plan 9.2 step 3, R7 = DL-283, R17 = DL-295). Reads the 10a timing sample; integrates nothing.

  .venv/Scripts/python.exe scripts/predict_ms10_10c.py [--timing-dir results/timing/ms10] [--out results/timing/ms10/prediction_10c.txt]

Run walls = neuron-updates x the 10a per-run median s per update under 10 copies (no re-time: the kernel qif_chunk and the package versions are
unchanged since the 10a sample, see docs/ms10_plan.md 'Timing gate on the final list'). Wall of a pool = max(sum of run walls / 10, longest run).
Controls count under the S-ID they accompany (ms10_lists.yaml 'accompanies'). The companion mean-field time uses the MS9 s-per-tau range (UNVERIFIED
for these cells).
"""
from __future__ import annotations

import argparse
from pathlib import Path

from mprsurge import config as C
from mprsurge.analysis import ms10_counts as M
from mprsurge.analysis import ms10_runlist as RL

W = 10
MF_S_PER_TAU = (9.76e-3, 1.1e-2, 18.9e-3)       # MS9 9a: fastest cell, runner order estimate (8a), slowest map-1 cell
MF_TAU_30, MF_TAU_60 = 5250.0, 9000.0           # mode D: baseline 5 s + 1.25 T_ramp + hold 10 s (no discard), tau = 10 ms


def lists(n_cell_seeds: int = 3) -> dict:
    p = RL.params()
    ctrl = {s: [(x["label"], x["N"], x["T_ramp_s"], p["controls"]["seeds"]) for x in p["controls"]["configs"] if x["accompanies"] == s] for s in ("S8", "S9", "S10")}
    return {"S8": M.s8_runs(n_cell_seeds), "C2_S8": ctrl["S8"], "S10": M.s10_runs(False), "C2_S10": ctrl["S10"], "S9": M.s9_runs(), "C2_S9": ctrl["S9"]}


def pool(runs, rate) -> dict:
    return M.predict_s(runs, rate, W)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timing-dir", default="results/timing/ms10")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    rate = M.rates(a.timing_dir, W)
    L = lists()
    out = [f"10c timing gate, rate = per-run median under {W} copies of the 10a sample (s per update x1e-9): " + ", ".join(f"N={n}: {r * 1e9:.3f}" for n, r in sorted(rate.items()))]
    for k, v in L.items():
        out.append(f"{k:7s} {M.n_runs(v):3d} runs  {M.total_updates(v):.4e} updates  alone-pool wall {M.fmt(pool(v, rate)['wall_s'])} (sum {M.fmt(pool(v, rate)['sum_s'])}, longest {M.fmt(pool(v, rate)['longest_s'])})")
    assert sum(M.n_runs(L[k]) for k in ("C2_S8", "C2_S9", "C2_S10")) == RL.EXPECTED_CONTROLS
    groups = {"S8 + C2_S8 (one launch)": L["S8"] + L["C2_S8"], "S10 + C2_S10 (one launch)": L["S10"] + L["C2_S10"],
              "S8 + C2_S8 + S10 + C2_S10 (one pool, the row reading)": L["S8"] + L["C2_S8"] + L["S10"] + L["C2_S10"],
              "S9 + C2_S9 (one launch)": L["S9"] + L["C2_S9"]}
    res = {}
    for g, v in groups.items():
        res[g] = pool(v, rate)
        out.append(f"{g}: {M.n_runs(v)} runs, {M.total_updates(v):.4e} updates, wall {M.fmt(res[g]['wall_s'])} (sum {M.fmt(res[g]['sum_s'])}, longest {M.fmt(res[g]['longest_s'])})")
    sep = res["S8 + C2_S8 (one launch)"]["wall_s"] + res["S10 + C2_S10 (one launch)"]["wall_s"]
    out.append(f"S8 and S10 launches one after the other (R5): {M.fmt(sep)} in all")
    row = M.verdict(res["S8 + C2_S8 + S10 + C2_S10 (one pool, the row reading)"]["wall_s"], M.ALLOWANCE_ROW_S)
    rowsep = M.verdict(sep, M.ALLOWANCE_ROW_S)
    v9 = M.verdict(res["S9 + C2_S9 (one launch)"]["wall_s"], M.ALLOWANCE_S9_S)
    out.append(f"RULE row S8/S10/S12 networks (30 min, limit 45 min): one pool {M.fmt(row['pred_s'])} = {row['ratio']:.2f} x, {'PASS' if row['ok'] else 'FAIL'}; two launches {M.fmt(rowsep['pred_s'])} = {rowsep['ratio']:.2f} x, {'PASS' if rowsep['ok'] else 'FAIL'}")
    out.append(f"RULE S9 + controls (2 h, limit 3 h): {M.fmt(v9['pred_s'])} = {v9['ratio']:.2f} x, {'PASS' if v9['ok'] else 'FAIL'}")
    longest = max(r["longest_s"] for r in res.values())
    out.append(f"longest single network run {M.fmt(longest)}; largest launch {M.fmt(max(r['wall_s'] for r in res.values()))}; launches over 1 h: "
               + (", ".join(g for g, r in res.items() if r["wall_s"] > 3600) or "none"))
    # D36 (DL-268 conservative reading): on top and with the placeholders replaced, all three launches
    tot = sep + v9["pred_s"]
    d = M.d36_totals(tot)
    out.append(f"D36: all ramp runs and controls, S8 + S10 launches then S9: {M.fmt(tot)}; MS9 total {M.MS9_D36_TOTAL_H} h + this = {d['on_top_h']:.2f} h on top "
               f"(replaced reading {d['replaced_h']:.2f} h) against {M.D36_CAP_H:g} h")
    lo = [(4 * MF_TAU_30 + MF_TAU_60) * r for r in MF_S_PER_TAU]
    out.append(f"companion MF (5 mode-D runs, 4 x {MF_TAU_30:.0f} tau + {MF_TAU_60:.0f} tau): sum of run walls at {MF_S_PER_TAU} s per tau = " + ", ".join(M.fmt(x) for x in lo)
               + f"; at 5 workers the wall is the longest run, {M.fmt(MF_TAU_60 * MF_S_PER_TAU[0])} to {M.fmt(MF_TAU_60 * MF_S_PER_TAU[2])}")
    txt = "\n".join(out)
    print(txt)
    if a.out:
        Path(a.out).write_text(txt + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
