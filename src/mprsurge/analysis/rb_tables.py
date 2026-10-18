"""8f: plain-text rendering of the rb_eval result dict (no computation beyond formatting)."""
from __future__ import annotations


def _f(x, n=4):
    return "n/a" if x is None else f"{x:.{n}g}" if isinstance(x, float) else str(x)


def render(r: dict) -> str:
    L = []
    if "rulings_8f2" in r:
        L += ["8f2 rulings applied as labelled primary readings (DL-186):"] + [f"  {k}. {v}" for k, v in r["rulings_8f2"].items()] + [""]
    s = r["no_t_pred"]["split"]
    L += ["no t_pred (%d runs): %s" % (s["n"], s["reason_counts"])]
    for k, v in s["by_reason_path_profile"].items():
        L.append(f"  {k}: {v}")
    a = r["RB3a"]
    L += ["", f"RB3(a): {a['n_in_range']} in range, {a['n_testable']} testable (eta not constant at t_pred), tolerance 1 A4 step; headline: {a['headline']['status']}"]
    for x in a["runs"]:
        L.append(f"  {x['path']} {x['profile']} sd {x['start_distance']} T {x['T_ramp_s']:.4g}: cross {_f(x['match_err_steps_cross'])} steps, class {_f(x['match_err_steps_class'])}, const {x['eta_const_at_t_pred']}")
    L.append("  pass counts: %s" % a["pass_counts"])
    pa = a["primary"]
    L.append(f"  PRIMARY (ruling 2): {pa['n_within_one_step']} of {pa['n_judged']} testable runs within one step: {pa['status']}")
    for x in pa["constant_eta_runs_no_verdict"]:
        L.append(f"  constant-eta run {x['family']} sd {x['start_distance']} T {x['T_ramp_s']:.4g}: time error {_f(x['time_err_cross_s_signed'])} s (signed), no verdict")
    L.append("  groups above 2 of 13: %s" % [(g["path"], g["profile"], g["start_distance"], g["n_in_range"]) for g in a["groups_above_2"]])
    b = r["RB3b"]
    L += ["", "RB3(b): PRIMARY (cross onset, ruling 1) %s; secondary (classifier onset) %s; flips %s" % (b["primary"]["status"], b["primary"]["secondary"]["status"], b["verdict_flips_between_onsets"])]
    for on, per in b["by_onset"].items():
        for rung, d in per.items():
            if rung.startswith("_"):
                continue
            L.append(f"  {on} dt {rung}: medians %s  decreasing(excl) {d['strictly_decreasing_exclude']}" % [_f(x["median_exclude"], 6) for x in d["levels"]])
    c = r["RB3c"]
    L += ["", f"RB3(c): headline class {c['headline_class']}; PRIMARY (ruling 5, P2 linear) {c['primary']['n_equal_headline']} of 4 equal: {c['primary']['status']}; information A/B/C: {c['summary']}"]
    for f, v in c["by_family"].items():
        L.append(f"  {f}: {v['classes']}")
    d = r["RB3d"]
    L += ["", f"RB3(d): bound {d['bound']}; per path " + str({p: v['n_class_changes'] for p, v in d['by_path'].items()}) + f"; {d['status']}"]
    for p, v in d["by_path"].items():
        L.append(f"  {p}: changes at T_ramp {v['changed_at_T_ramp_s']}")
    e = r["RB5"]
    L += ["", f"RB5 delta0: class unchanged {e['delta0_headline']['class_unchanged']}; " + str([(x['delta0'], x['cls'], _f(x['delay_eta_cross'], 6)) for x in e['delta0_headline']['ladder']])]
    L.append(f"RB5 start distance (P1 linear): {e['start_distance_P1_linear']['n_class_changes']} of {e['start_distance_P1_linear']['n_T_ramp']} T_ramp change class: {e['start_distance_P1_linear']['T_ramp_with_change_s']}")
    h = r["RB6_heun"]
    L += ["", "RB6 Heun: PRIMARY (cross onset, ruling 1) %s; secondary (classifier onset) %s; exact 0 is a 1 ms grid limit (ruling 7)" % (h["primary"]["status"], h["primary"]["secondary"]["status"])]
    for on, rows in h["by_onset"].items():
        for x in rows:
            L.append(f"  {on} level {x['level']}: median 1e-3 {_f(x['median_default'], 6)} 1e-4 {_f(x['median_finest'], 6)} rel {_f(x['rel_change'])} {x['status']} (identical seeds {x['n_seeds_identical_to_float']}/10)")
    q = r["RB6_solvers"]
    L += ["", "RB6 DOP853 vs Radau: %s" % {k: q["dop853_vs_radau"][k] for k in ("class_agree", "onset_diff_ms_class", "onset_diff_ms_cross", "status")},
          "RB6 rtol 1e-10 vs 1e-12: %s" % q["rtol_1e-10_vs_1e-12"]]
    L += ["", "P2 surge-class counts (T_ramp, classes):"]
    for tag, v in r["P2_surge_class_counts"]["rows"].items():
        L.append(f"  {tag}: surge inside window {v['n_surge_inside_window']}/{v['n_runs_inside_window']}, outside {v['n_surge_outside_window']}/{v['n_runs_outside_window']}")
        for x in v["per_T_ramp"]:
            L.append(f"    {x['T_ramp_s']:.4g} {'in ' if x['in_window'] else 'out'} {x['classes']}")
    return "\n".join(L) + "\n"
