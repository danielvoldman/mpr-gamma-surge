"""MS10 10f: write docs/ms10_results.md from the stored evaluation (results/ms10/eval/ms10_eval.json). Text only: tables and pre-registered verdict wording.

  .venv/Scripts/python.exe scripts/write_ms10_results.py
"""
import json
import math

from mprsurge import config as C

ROOT = C.repo_root()
LIMITS = ("Claim limits: DL-229 and DL-258 b apply to every network class below (a network class is a class of the frozen mode-N classifier on the mean voltage v "
          "of one finite-N realisation; the primary reading is the Table 2.1 correspondence, the post-hoc reading does not count S-rel as a match for D-tr).")
MET = ["onset_s", "eta_onset", "delay_eta", "duration_ms", "duration_cycles", "duration_frac_ramp", "peak_power_abs", "peak_power_rel", "f_pk_hz",
       "J_exit_run", "J_exit_static", "exit_delay", "r_post_1s", "r_post_5s"]
CELL_IJ = {"0": "(7, 4)", "1": "(22, 10)", "2": "(13, 29)", "3": "(24, 26)"}


def f(x, nd=4):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "undefined"
    return f"{x:.{nd}g}" if isinstance(x, float) else str(x)


def cls_str(d):
    return ", ".join(f"{k} {v}" for k, v in sorted(d.items())) or "-"


def sigma_section(d):
    s = d["sigma_check"]
    o = ["## Sigma check (R16, R25, R28)", "",
         f"Reference {s['mf_baseline_std']} (MS7 baseline-only record, DL-310). Network baseline std of v over samples [0, 5000), ddof 1, 6 S8 headline runs, bounds inclusive.", "",
         "| run | baseline std |", "|---|---|"]
    o += [f"| {k} | {v:.6f} |" for k, v in s["per_run"].items()]
    same = all(v == 1 for v in s["n_distinct_per_seed"].values())
    o += ["", f"Range {s['network_min']:.6f} to {s['network_max']:.6f}, mean {s['network_mean']:.6f}. Distinct values overall: {s['n_distinct_values']}; distinct per seed across the two T_ramp: "
          f"{s['n_distinct_per_seed']} (the 10 s and 120 s baselines of one seed are identical: {same}). "
          f"Position of the reference in the range {s['position_in_range']:.4f} (0 at the minimum, 1 at the maximum); margin to the nearest end {s['margin_to_nearest_end']:.6f}. "
          f"Reference / network mean = {s['mf_over_network_mean']:.4f}. **Verdict: {s['verdict']}.** sigma changed: {s['sigma_changed']}.", ""]
    return o


def rb1_section(d):
    o = ["## RB1 (R15, R18, R23, R26, R27)", "", LIMITS, "", "### Headline, per seed", "",
         "| T_ramp | seed | class | MF class | class match (primary) | match without S-rel | f_pk Hz | MF f_pk | rel err | diff in bins (bin Hz) | f_pk ok | onset (classifier) s | MF onset s | diff s | step s | onset ok | raw-crossing onset s (post hoc) | pass |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for T, h in d["rb1_headline"].items():
        for r in h["seeds"]:
            o.append(f"| {T} | {r['seed']} | {r['class']} | {r['ref_class']} | {r['class_match']} | {r['class_match_posthoc']} | {f(r['f_pk_hz'])} | {f(r['f_pk_ref_hz'])} | "
                     f"{f(r['f_pk_rel_err'])} | {f(r['f_pk_diff_bins'])} ({r['bin_hz']}) | {r['f_pk_ok']} | {f(r['onset_s'])} | {f(r['onset_ref_s'])} | {f(r['onset_diff_s'])} | "
                     f"{f(r['step_s'])} | {r['onset_ok']} | {f(r['onset_raw_s'])} | {r['pass']} |")
    o += ["", "| T_ramp | seeds passing | passing without S-rel (post hoc) | C2 control classes beside (same N, T_ramp, Delta, tau_d; 3 seeds; R17) | post-hoc median reading: f_pk median Hz, ok / onset median s, ok / all classes match | verdict |",
          "|---|---|---|---|---|---|"]
    for T, h in d["rb1_headline"].items():
        m = h["posthoc_median"]
        o.append(f"| {T} | {h['pass_count']} of 3 | {h['pass_count_srel_not_counted']} of 3 | {cls_str(h['controls']['classes'])} | "
                 f"{f(m['f_pk_median_hz'])}, {m['f_pk_ok']} / {f(m['onset_median_s'])}, {m['onset_ok']} / {m['classes_all_match']} | {h['verdict']} |")
    rc = d["rb1_cells"]
    o += ["", "### Cells (30 s, companion mode-D class; a cell agrees only if 3 of 3 seeds are in the matching class)", "",
          "| cell (i, j) | companion MF class | stored 120 s class | network classes (seeds 0 to 2) | seeds matching | matching without S-rel | C2 control classes | agrees |",
          "|---|---|---|---|---|---|---|---|"]
    for c, r in rc["cells"].items():
        o.append(f"| {c} {CELL_IJ[c]} | {r['ref']['class']} | {r['stored_120s_class']} | {', '.join(r['classes'])} | {sum(r['matches'])} of 3 | "
                 f"{sum(r['matches_srel_not_counted'])} of 3 | {cls_str(r['controls']['classes'])} | {r['agrees']} |")
    ns = d["N_sweep"]
    nw = ns["no_worse"]
    o += ["", f"Cells agreeing: {rc['n_agree']} of {rc['n_cells']} (need {rc['need']}); without S-rel (post hoc) {rc['n_agree_srel_not_counted']}. Cells part: **{rc['verdict']}**.", "",
          "### N rule (R18)", "",
          f"Seeds in the mean-field-matching class (60 s, companion class {ns['ref']['class']}): N = 1e4: {nw['count_1e4']}; N = 3e4: {nw['count_3e4']} "
          f"(without S-rel: {nw['count_1e4_srel_not_counted']} and {nw['count_3e4_srel_not_counted']}). N = 3e4 no worse than 1e4: **{'PASS' if nw['pass'] else 'FAIL'}**.", "",
          "### RB1 verdict", "",
          f"Parts: headline {d['rb1']['parts']['headline']}, cells {d['rb1']['parts']['cells']}, N rule {d['rb1']['parts']['N_rule']}. "
          f"**RB1: {d['rb1']['verdict']}** (primary reading; post-hoc readings feed no gate). Failing RB1 is G4 (frozen `on_fail`).", ""]
    return o


def s9_section(d):
    ns = d["N_sweep"]
    o = ["## S9 (finite size; E-6)", "", LIMITS, "",
         "| N | seeds | classes | surge seeds | matching seeds (primary / without S-rel) | f_pk rel err median [range] | onset abs err s median [range] | C2 control classes |",
         "|---|---|---|---|---|---|---|---|"]
    for N, r in ns["by_N"].items():
        fe, oe = r["f_pk_rel_err"], r["onset_abs_err_s"]
        o.append(f"| {N} | {r['seeds_present']} | {cls_str(r['classes'])} | {r['surge_seeds']} | {r['match_seeds']} / {r['match_seeds_srel_not_counted']} | "
                 f"{f(fe['median'])} [{f(fe['min'])}, {f(fe['max'])}] (n {fe['n']}) | {f(oe['median'])} [{f(oe['min'])}, {f(oe['max'])}] (n {oe['n']}) | {cls_str(r['controls']['classes'])} |")
    o += ["", "Table 2.1 Metrics: median [min, max] over the seeds for which the metric is defined; then n defined / n undefined (undefined counted, not imputed; reasons below). "
          "J_exit,static and the sign of the exit delay follow the 9i reading (UNVERIFIED, no gate). Both post-surge windows (1 s, 5 s) are kept (O12).", "",
          "| metric | " + " | ".join(f"N = {N}" for N in ns["by_N"]) + " |", "|---|" + "---|" * len(ns["by_N"])]
    for m in MET:
        cells = []
        for r in ns["by_N"].values():
            x = r["metrics"].get(m)
            if x is None:
                cells.append("not reported")
            elif x["n"]:
                cells.append(f"{f(x['median'])} [{f(x['min'])}, {f(x['max'])}]; {x['n']}/{x['n_undefined']}")
            else:
                cells.append(f"-; 0/{x['n_undefined']}")
        o.append(f"| {m} | " + " | ".join(cells) + " |")
    o.append("")
    for N, r in ns["by_N"].items():
        o.append(f"Undefined reasons, N = {N}: " + ("; ".join(f"{k}: {v}" for k, v in r["metric_undefined_reasons"].items()) or "none") + ".")
        o.append("")
    return o


def rb8_section(d):
    b = d["rb8"]
    o = ["## S10 and RB8, heterogeneity part (R8, E-7, E-8)", "", LIMITS, "", "| shape | seed | class | correspondence level |", "|---|---|---|---|"]
    for shape, rows in b["per_seed_table"].items():
        o += [f"| {shape} | {r['seed']} | {r['class']} | {r['level']} |" for r in rows]
    o += ["", f"Lorentzian classes {b['lorentzian_classes']}; C2 control classes beside the Lorentzian (N = 1e4, 60 s): {cls_str(b['lorentzian_controls']['classes'])}; "
          f"Lorentzian seeds in the mean-field-matching class: {b['lorentzian_mf_match_seeds']} of 3. "
          f"**RB8 heterogeneity part: {b['verdict']}** ({b['reason']}); no pass or fail is made.", ""]
    return o


def g4_section(d):
    g = d["g4"]
    o = ["## G4 (R24, E-9; report-only for the run order)", "", LIMITS, "",
         "| pool | records | missing | surge seeds (primary) | surge seeds without S-rel | misses |", "|---|---|---|---|---|---|"]
    for N, r in g["misses_by_N"].items():
        o.append(f"| N = {N} | {r['records']} | {r['missing']} | {r['surge_seeds']} | {r['surge_seeds_srel_not_counted']} | {r['misses']} |")
        for k, v in r["per_list"].items():
            o.append(f"| {k} | {v['records']} | {v['missing']} | {v['surge_seeds']} | {v['surge_seeds_srel_not_counted']} | |")
    o += ["", f"RB1: {g['rb1']}. Cells in disagreement, 2 or more: {g['cells_disagree_2_or_more']}. G4 triggered: {g['triggered']}.", ""]
    o += [t + "  " for t in g["text"]]
    return o


def main():
    d = json.loads((ROOT / "results/ms10/eval/ms10_eval.json").read_text(encoding="utf-8"))
    n_shared = sum(1 for t in d["time_origin"] if t["shared"])
    o = ["# MS10 results (10f)", "",
         "Tables and verdicts only, in the pre-registered wording (`docs/ms10_eval_rules.md`, `configs/ms10/ms10_eval.yaml`). Source: `results/ms10/eval/ms10_eval.json`, "
         "written by `scripts/evaluate_ms10.py` from the stored records of the six launched lists; nothing was integrated at 10f. " + LIMITS, "",
         f"Criteria gate (tag criteria-frozen): {d['criteria_gate']}. Time origins (R27): shared = true in {n_shared} of {len(d['time_origin'])} comparisons; stamp offset 1 ms.", ""]
    o += sigma_section(d) + rb1_section(d) + s9_section(d) + rb8_section(d) + g4_section(d)
    o += ["", "## Not verified", "",
          "A reference without f_pk or onset gives n/a and counts as met (R29, UNVERIFIED reading; does not arise for the headline). Control record sizes assume the ramp-run "
          "duration (UNVERIFIED). J_exit,static and the exit-delay sign follow 9i (UNVERIFIED, no gate)."]
    (ROOT / "docs/ms10_results.md").write_text("\n".join(o) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
