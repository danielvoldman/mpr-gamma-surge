"""MS9 9c: A8 review of the NC1 network S+ (G7 triggered). Analysis only: nothing is integrated, no threshold or criterion changes.

  .venv/Scripts/python.exe scripts/analyse_nc1_net.py part1 [--out results/ms9/9c]
  .venv/Scripts/python.exe scripts/analyse_nc1_net.py part2 [--out results/ms9/9c]

part1: decomposition of the classifier decision on the STORED record results/S12/NC1_net (signal, baseline, ratios against 2.0, episode,
       cycle bookkeeping, D8 fit, rate, eta-bar, A4 leading Re lambda) and the A8 sensitivity variants on that record (post-hoc, feed no gate).
part2: the S12x exploratory runs (results/S12x), classified with the unchanged classifier, plus the original NC1 network run as the
       10th seed of (i): class, episode start and end, f_pk, margins.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

from mprsurge import config as C
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import a8_sensitivity as A8S
from mprsurge.analysis import a9 as A9
from mprsurge.analysis import entry_exit as EE
from mprsurge.analysis import hopf
from mprsurge.analysis import ms9_classify as MCL
from mprsurge.analysis import ms9_nc1_decomp as D

NET = "results/S12/NC1_net/NC1_net_0000_1a8cb131785a"
TAU_S = 0.010


def load(stem):
    p = C.repo_root() / stem
    rec = json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))
    with np.load(p.with_suffix(".npz")) as z:
        arr = {k: z[k] for k in ("t_ms", "r", "v", "s", "eta", "J", "Delta", "I")}
    return rec, arr


def fmt(x, n=4):
    return "nan" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{n}g}"


def part1(out: Path) -> int:
    fi, gate = A7.frozen_inputs()
    a_ref, thr = fi["a_ref"], fi["threshold"]
    rec, z = load(NET)
    cfg = rec["config"]
    t_on, T = cfg["path"]["t_on_s"], cfg["path"]["T_ramp_s"]
    v, t = z["v"], z["t_ms"] / 1000.0
    row = MCL.classify_record(C.repo_root() / (NET + ".json"), fi)
    print(f"record {NET}  status {rec['status']}  git {rec['git']['commit'][:8]} dirty {rec['git']['dirty']}  N {cfg['network']['N']}  seed key {cfg['seeds']['spawn_key']}")
    print(f"stored classification (frozen classifier, ms9_classify): {row['class']}  onset {row['onset_s']}  end {row['end_s']}  duration {row['duration_s']}  "
          f"cycles {row['cycles']:.3f}  f_pk {row['f_pk_hz']}  terminated {row['terminated']}  peak_rho {row['peak_rho']:.4f}")
    print(f"threshold 0.1 x A_ref = {thr:.6f} (A_ref {a_ref:.6f}); t_on {t_on} s, T_ramp {T} s, record {t[0]:.3f} to {t[-1]:.3f} s, fs 1000 Hz")
    print(f"signal: classify_record reads npz['v'] = the bin-end mean V over the non-refractory neurons (network.exclude_refractory = "
          f"{cfg['network']['exclude_refractory']}), NOT the binned rate r; r is stored beside it and unused by the classifier.")
    v0 = D.decompose(v, t_on, T, thr, a_ref)
    assert v0["class"] == row["class"], (v0["class"], row["class"])
    wt = v0["_wt"]
    b = v0["baseline"]
    print("\n== BASELINE (windows lying wholly in [t_on - 5 s, t_on]) ==")
    print(f"W {b['W_s']} s step {b['step_s']} s; baseline windows {b['n_windows']} (centres {b['t_first_centre']} to {b['t_last_centre']} s)")
    print(f"P_G mean {b['base_pg']:.6g}  (min {b['p_g_min']:.6g}, max {b['p_g_max']:.6g}, max/min {b['p_g_max_over_min']:.3f})")
    print(f"P_non-G mean {b['base_png']:.6g}  (min {b['p_ng_min']:.6g}, max {b['p_ng_max']:.6g}, max/min {b['p_ng_max_over_min']:.3f})")
    print(f"odds P_G/P_non-G mean {b['base_odds']:.6g}  (min {b['odds_min']:.6g}, max {b['odds_max']:.6g}, max/min {b['odds_max_over_min']:.3f})")
    print(f"baseline window values: P_G {[round(float(x), 7) for x in wt['p_g'][wt['baseline_mask']]]}")
    print(f"                        odds {[round(float(x), 5) for x in wt['odds'][wt['baseline_mask']]]}")
    # ratios over time
    print("\n== RATIOS AGAINST THE FACTOR 2.0 (rel = odds / baseline odds; abs = P_G / baseline P_G), windows from t_on to 40 s ==")
    print(f"{'t_c (s)':>8} {'f_pk':>6} {'P_G':>11} {'abs':>7} {'rel':>7} {'abs/2':>7} {'rel/2':>7}  flag")
    for k, tc in enumerate(wt["tc"]):
        if tc < t_on - 1e-9 or tc > 40:
            continue
        fl = ("rel " if wt["rel_ratio"][k] >= 2 else "") + ("abs" if wt["abs_ratio"][k] >= 2 else "")
        print(f"{tc:8.1f} {wt['fpk'][k]:6.1f} {wt['p_g'][k]:11.4e} {wt['abs_ratio'][k]:7.3f} {wt['rel_ratio'][k]:7.3f} "
              f"{wt['abs_ratio'][k] / 2:7.3f} {wt['rel_ratio'][k] / 2:7.3f}  {fl}")
    post = wt["post_mask"]
    for key in ("rel", "abs"):
        r = v0[key]
        print(f"{key}: peak ratio {r['peak_ratio']:.3f} at t_c {r['peak_time_s']} s = {r['peak_margin_over_factor']:.3f} x the factor 2.0 "
              f"(margin {r['peak_ratio'] - 2:+.3f}); flagged windows after t_on: {r['n_flagged_windows']}; runs (window centres) {r['runs_time']}; "
              f"episode {r['episode']}")
    # distribution of the post-t_on ratios outside the episode (how often a window is near the threshold)
    for key in ("rel", "abs"):
        x = wt[f"{key}_ratio"][post]
        print(f"{key} ratio over all {x.size} post-t_on windows: median {np.median(x):.3f}, 90th pct {np.percentile(x, 90):.3f}, 99th pct {np.percentile(x, 99):.3f}, "
              f"max {x.max():.3f}; windows >= 1.5: {(x >= 1.5).sum()}, >= 2: {(x >= 2).sum()}, >= 4: {(x >= 4).sum()}")
    # episode bookkeeping
    print("\n== EPISODE AND CYCLE BOOKKEEPING ==")
    print(f"class {v0['class']}  reason '{v0['reason']}'  provisional '{v0['provisional']}'")
    print(f"classifier episode: {v0['episode']}")
    ew = v0.get("episode_windows")
    if ew:
        print(f"window run behind it: {ew['windows']} windows, centres {ew['first_centre']} to {ew['last_centre']} s, per-window f_pk {ew['fpk_per_window_hz']} Hz, "
              f"mean {ew['mean_fpk_hz']:.4f} Hz")
        print(f"  duration = windows x step = {ew['windows']} x {wt['step']} = {ew['duration_s']} s; cycles = duration x mean f_pk = {ew['cycles']:.3f}")
        print(f"  onset = first window CENTRE {ew['onset_s']} s; end = last window centre + step/2 = {ew['end_s']} s; end - onset = {ew['end_minus_onset_s']} s")
        print(f"  the spectrogram data the windows touch: {ew['data_first_s']} to {ew['data_last_s']} s ({ew['data_last_s'] - ew['data_first_s']:.1f} s)")
        print(f"  independent unwrapped-phase count of the 25-100 Hz band-passed v over onset..end: {D.phase_cycles(v, ew['onset_s'], ew['end_s']):.1f} cycles; "
              f"over the touched data span: {D.phase_cycles(v, ew['data_first_s'], ew['data_last_s']):.1f} cycles  (ours, comparison only)")
        print(f"  episode peak window f_pk {v0['episode']['f_pk_hz']} Hz (the 41.5 Hz); the cycle count uses the MEAN over the run's windows")
    d8 = v0["d8"]
    print(f"D8 fit (fit on v from t_on, threshold {thr:.4f}, band 25-100 Hz, first 10 cycles from the first envelope crossing): {d8}")
    if d8 and np.isfinite(d8["rate_per_s"]):
        print(f"  rate {d8['rate_per_s']:.4g} /s, SE {d8['se_per_s']:.4g} /s, rate/SE {d8['rate_per_s'] / d8['se_per_s']:.3f}; damped only if rate < -2 SE; fit starts {d8['t_start_s']} s "
              f"(t_on + {d8['t_start_s'] - t_on:.3f} s), {d8['n_samples']} samples, {d8['cycles']:.2f} cycles")
    # context: rate, eta-bar, distance to eta_H, A4
    print("\n== CONTEXT AT THE EPISODE TIME ==")
    m = cfg["model"]
    J0, Dl, td = float(cfg["path"]["J0"]), float(m["Delta"]), float(m["tau_d_ms"])
    hp = A9.hopf_point(J0, Dl, td, float(m["tau_ms"]))
    eta_H = hp["eta_bar"] if hp else None
    print(f"A4 Hopf point at (J0 {J0}, Delta {Dl}, tau_d {td} ms): eta_H {fmt(eta_H, 7)}, f_Hopf {fmt(hp['f_hz'] if hp else None)} Hz  (eta_start {cfg['path']['eta_start']:.7f}, eta_peak NC1 end {cfg['path']['eta_peak']:.7f})")
    rate_hz = z["r"] / TAU_S
    eta, J = z["eta"], z["J"]

    def at(t0, t1):
        sel = (t >= t0) & (t < t1)
        return sel

    def lead(e):
        return EE.leading_re(float(e), J0, Dl, td / m["tau_ms"])

    segs = [("baseline [t_on-5, t_on]", t_on - 5, t_on)]
    if ew:
        segs += [("episode windows' data span", ew["data_first_s"], ew["data_last_s"]), ("episode onset..end", ew["onset_s"], ew["end_s"])]
    segs += [("whole record after t_on", t_on, t[-1] + 1e-3)]
    print(f"{'segment':32s} {'mean r (Hz)':>12s} {'sd r (Hz)':>10s} {'mean v':>9s} {'sd v':>8s} {'eta-bar':>9s} {'eta-eta_H':>10s} {'Re lam (/s)':>12s}")
    for name, a, bb in segs:
        s = at(a, bb)
        e = float(np.mean(eta[s]))
        print(f"{name:32s} {rate_hz[s].mean():12.3f} {rate_hz[s].std():10.3f} {v[s].mean():9.4f} {v[s].std():8.4f} {e:9.4f} {e - eta_H:10.4f} {lead(e) / TAU_S:12.3f}")
    print("\neta-bar(t) and the A4 leading Re lambda along the path (Re lambda in 1/s = per tau / 0.01 s; Hopf point at Re lambda = 0):")
    for tt in (0, t_on, 10, 14, 15, 16, 17, 20, 30, 60, 90, 125, 130):
        k = min(int(round(tt * 1000)) - 1, len(t) - 1)
        e = float(eta[k])
        lm = hopf.leading_mode(e, J0, Dl, td / m["tau_ms"])
        print(f"  t {tt:6.1f} s  eta-bar {e:8.4f}  eta-bar - eta_H {e - eta_H:8.4f}  leading Re lambda {lm['re_max'] / TAU_S:9.3f} /s  complex pair Re {lm['pair_re'] / TAU_S:9.3f} /s  "
              f"|Im|/(2 pi) {lm['pair_im'] / (2 * np.pi * TAU_S):7.2f} Hz  mean-field r* {lm['r'] / TAU_S:7.3f} Hz   window mean rate {rate_hz[max(k - 500, 0):k + 500].mean():7.3f} Hz")
    # A8 sensitivity variants on this record (post-hoc)
    print("\n== A8 SENSITIVITY VARIANTS ON THIS STORED RECORD (post-hoc; feed no gate; configs/A8_sensitivity.yaml set, a8_sensitivity.VARIANTS) ==")
    print(f"{'variant':14s} {'W':>5s} {'class':>6s} {'onset':>6s} {'end':>6s} {'dur':>5s} {'cyc':>7s} {'f_pk':>5s} {'rel pk':>7s} {'abs pk':>7s} {'nbase':>5s}  D8 (rate /SE, t_start, cycles)  reason")
    rows = []
    for var in A8S.VARIANTS:
        d = D.decompose(v, t_on, T, thr, a_ref, variant=var)
        e = d["episode"]
        d8v = d["d8"]
        d8s = "none" if d8v is None else f"{d8v['rate_per_s']:.3g}/{d8v['se_per_s']:.3g} ({'damped' if d8v['damped'] else 'non-damped'}), {d8v['t_start_s']:.3f}, {d8v['cycles']:.1f}"
        print(f"{var:14s} {d['W_s']:5.2f} {d['class']:>6s} {fmt(e['onset_s'] if e else None):>6s} {fmt(e['end_s'] if e else None):>6s} {fmt(e['duration_s'] if e else None):>5s} "
              f"{fmt(e['cycles'] if e else None):>7s} {fmt(e['f_pk_hz'] if e else None):>5s} {d['rel']['peak_ratio']:7.2f} {d['abs']['peak_ratio']:7.2f} {d['baseline']['n_windows']:5d}  {d8s}  {d['reason']}")
        rows.append({"variant": var, "W_s": d["W_s"], "class": d["class"], "onset_s": e["onset_s"] if e else "", "end_s": e["end_s"] if e else "",
                     "duration_s": e["duration_s"] if e else "", "cycles": e["cycles"] if e else "", "f_pk_hz": e["f_pk_hz"] if e else "",
                     "rel_peak_ratio": d["rel"]["peak_ratio"], "abs_peak_ratio": d["abs"]["peak_ratio"], "baseline_windows": d["baseline"]["n_windows"],
                     "rel_flagged": d["rel"]["n_flagged_windows"], "abs_flagged": d["abs"]["n_flagged_windows"], "provisional": d["provisional"], "reason": d["reason"]})
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "nc1_net_variants.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    with open(out / "nc1_net_windows.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["t_centre_s", "f_pk_hz", "p_g", "p_non_g", "odds", "abs_ratio", "rel_ratio", "baseline", "post"])
        for k in range(len(wt["tc"])):
            w.writerow([wt["tc"][k], wt["fpk"][k], wt["p_g"][k], wt["p_ng"][k], wt["odds"][k], wt["abs_ratio"][k], wt["rel_ratio"][k],
                        bool(wt["baseline_mask"][k]), bool(wt["post_mask"][k])])
    print(f"\nwritten: {out / 'nc1_net_variants.csv'}, {out / 'nc1_net_windows.csv'}")
    return 0


def part2(out: Path) -> int:
    fi, _ = A7.frozen_inputs()
    root = C.repo_root()
    recs = sorted(p for p in (root / "results/S12x").rglob("*.json") if not p.name.endswith(".dry.json") and p.with_suffix(".npz").exists())
    recs = [root / (NET + ".json")] + recs
    rows = []
    for p in recs:
        row = MCL.classify_record(p, fi)
        rec, z = load(str(p.with_suffix("").relative_to(root)).replace("\\", "/"))
        cfg = rec["config"]
        d = D.decompose(z["v"], cfg["path"]["t_on_s"], cfg["path"]["T_ramp_s"], fi["threshold"], fi["a_ref"])
        assert d["class"] == row["class"]
        eta_on = float(z["eta"][min(int(round(row["onset_s"] * 1000)) - 1, len(z["eta"]) - 1)]) if np.isfinite(row["onset_s"]) else float("nan")
        rows.append({"family": "NC1_net (original, 10th seed)" if p.parent.name == "NC1_net" else p.parent.name, "run": p.stem, "spawn_key": row["spawn_key"],
                     "eta_start": cfg["path"]["eta_start"], "eta_end": cfg["path"]["eta_peak"], "status": row["status"], "git_dirty": row["git_dirty"],
                     "wall_s": row["wall_time_s"], "class": row["class"], "provisional": bool(row["provisional"]), "onset_s": row["onset_s"], "end_s": row["end_s"],
                     "duration_s": row["duration_s"], "cycles": row["cycles"], "f_pk_hz": row["f_pk_hz"], "terminated": row["terminated"],
                     "eta_at_onset": eta_on, **D.peak_margins(d),
                     "d8_rate_over_se": (d["d8"]["rate_per_s"] / d["d8"]["se_per_s"]) if d["d8"] and d["d8"]["se_per_s"] else float("nan")})
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "s12x_table.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("S12x (exploratory, outside the pre-registered lists, feeds no gate); classes by the unchanged frozen classifier; margins = peak ratio / 2.0 over post-t_on windows")
    print(f"{'family':32s} {'key':>10s} {'class':>6s} {'onset':>6s} {'end':>6s} {'dur':>5s} {'cyc':>6s} {'f_pk':>5s} {'rel pk':>7s} {'abs pk':>7s} {'rel/2':>6s} {'abs/2':>6s} {'eta@on':>7s} {'D8 r/SE':>8s} {'dirty':>5s}")
    for r in rows:
        print(f"{r['family']:32s} {r['spawn_key']:>10s} {r['class']:>6s}{'*' if r['provisional'] else ' '}{fmt(r['onset_s']):>6s} {fmt(r['end_s']):>6s} {fmt(r['duration_s']):>5s} "
              f"{fmt(r['cycles']):>6s} {fmt(r['f_pk_hz']):>5s} {r['rel_peak_ratio']:7.2f} {r['abs_peak_ratio']:7.2f} {r['rel_peak_margin']:6.2f} {r['abs_peak_margin']:6.2f} "
              f"{fmt(r['eta_at_onset']):>7s} {fmt(r['d8_rate_over_se'], 3):>8s} {str(r['git_dirty']):>5s}")
    by: dict = {}
    for r in rows:
        key = "const" if "const" in r["family"] else "ramp (9 new + original)"
        by.setdefault(key, []).append(r["class"])
    for k, c in by.items():
        counts: dict = {}
        for x in c:
            counts[x] = counts.get(x, 0) + 1
        print(f"{k}: n {len(c)}  classes {counts}")
    print(f"written: {out / 's12x_table.csv'}  (* = class depended on the D8 call, provisional)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="analyse_nc1_net")
    ap.add_argument("part", choices=("part1", "part2"))
    ap.add_argument("--out", default="results/ms9/9c")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out = out if out.is_absolute() else C.repo_root() / out
    return part1(out) if a.part == "part1" else part2(out)


if __name__ == "__main__":
    sys.exit(main())
