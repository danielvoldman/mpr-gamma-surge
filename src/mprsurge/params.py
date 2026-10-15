"""Reference points and the parameter table (plan Appendix B, section 6.6)."""
from __future__ import annotations

# Validation points (Table 3.2, Appendix B). ref_mpr is the M2 point; ref_ceni
# and ref_devalle are M3 points. ref_ceni has no tau_d of its own: S3 uses
# tau_d in {3, 4.95, 8} ms; a run must give it explicitly, in the D11 range,
# with a warning outside that set (DL-054, DL-066).
REF_POINTS: dict[str, dict] = {
    "ref_mpr": {"type": "M2", "eta_bar": -5.0, "J": 15.0, "Delta": 1.0,
                "tau_d_ms": None},
    "ref_ceni": {"type": "M3", "eta_bar": 1.0, "J": -20.0, "Delta": 0.05,
                 "tau_d_ms": None},
    "ref_devalle": {"type": "M3", "eta_bar": 4.0, "J": -21.0, "Delta": 0.3,
                    "tau_d_ms": 5.0},
}
REF_CENI_TAU_D_MS = (3.0, 4.95, 8.0)

# key -> (symbol, units, source/status), copied from Appendix B (Table B.1).
# Keys without an Appendix B row carry the entry that introduced them.
PARAM_META: dict[str, tuple[str, str, str]] = {
    "model.type": ("model", "", "section 4.1"),
    "model.ref_point": ("ref points", "", "R1; ref_devalle values confirmed in Devalle Fig. 3 [RB-item 2c]; ref_ceni matches Ceni arXiv v1 only [RB-item 3: PARTIAL]"),
    "model.tau_ms": ("tau", "ms", "R1; R5 [verified]"),
    "model.tau_d_ms": ("tau_d", "ms", "K7, K8 values; range [needs decision] (D11)"),
    "model.eta_bar": ("eta_bar", "", "R1; path [needs decision] (D12)"),
    "model.Delta": ("Delta", "", "R1; R5 (D13)"),
    "model.J": ("J", "", "sign reasoned (C3) (D14)"),
    "model.I_drive": ("I", "", "R3 (existence only) (D15)"),
    "path.name": ("path", "", "section 4.4"),
    "path.profile": ("profile", "", "R1; R5 (D21)"),
    "path.sigmoid_k": ("sigmoid k", "", "R1; R5 (D21)"),
    "path.T_ramp_s": ("T_ramp", "s", "R3 (1-5 min) (D16)"),
    "path.t_on_s": ("t_on", "s", "= baseline (D27)"),
    "path.eta_start": ("eta_start", "", "this plan; CP20 (D12)"),
    "path.eta_peak": ("eta_peak", "", "this plan; CP20 (D12)"),
    "path.eta_H": ("eta_H", "", "A4 (MS5); null until then (DL-065)"),
    "path.eta_path_status": ("eta path status", "", "DL-065"),
    "path.eps": ("eps", "1/tau", "derived: (eta_peak - eta_start)/T_ramp; R1; R5"),
    "path.J0": ("J0", "", "R2; R3 (D19)"),
    "path.J_end": ("J_end", "", "R2; R3 (D19)"),
    "path.J_lag_frac": ("J_lag_frac", "", "R2; R3 (D19)"),
    "path.J_T_frac": ("J_T_frac", "", "R2; R3 (D19)"),
    "path.I_amp": ("I_amp", "", "R3 (D15)"),
    "path.I_rise_frac": ("I_rise_frac", "", "R3 (D15)"),
    "path.I_plateau_frac": ("I_plateau_frac", "", "R3 (D15)"),
    "path.I_fall_frac": ("I_fall_frac", "", "R3 (D15)"),
    "path.Delta_factor": ("Delta_factor", "", "R3 section 3 (D20)"),
    "solver.method": ("solver", "", "R5 (D25)"),
    "solver.rtol": ("rtol", "", "R5 (D25)"),
    "solver.atol": ("atol", "", "R5 (D25)"),
    "solver.max_step_tau": ("max_step", "tau", "R5 (D25)"),
    "solver.dt_out_ms": ("dt_out", "ms", "R4 (1 kHz) (D1)"),
    "solver.delta0": ("delta0", "", "R1; R5 (D26)"),
    "noise.scheme": ("noise step scheme", "", "R5"),
    "noise.dt_tau": ("noise dt", "tau", "R5"),
    "noise.sigma": ("sigma", "", "calibrated at MS5 (R5, Segneri) (D18); null until then (DL-065)"),
    "noise.sigma_factor": ("sigma factor", "", "R5 (Segneri) (D18)"),
    "noise.floor_levels": ("noise floor (A7)", "", "set at MS7 [needs decision]; no scaling law entered (UNVERIFIED) (D43)"),
    "network.N": ("N", "neurons", "R5 [single source]"),
    "network.dt_tau": ("dt", "tau", "R5 (C6) (D17)"),
    "network.V_peak": ("V_p", "", "R5 [single source]"),
    "network.V_reset": ("V_r", "", "R5 [single source]"),
    "network.het_dist": ("heterogeneity", "", "R5; Taher 2020 Eq. 8 [RB-item 6] (D28, D29)"),
    "network.het_sampling": ("heterogeneity sampling", "", "R5; Taher 2020 Eq. 8 [RB-item 6] (D28)"),
    "network.init_V_range": ("initial V", "", "R5"),
    "network.rate_bin_ms": ("rate bin", "ms", "R5 (D30)"),
    "network.n_raster": ("raster neurons", "", "R5 (D30)"),
    "network.exclude_refractory": ("exclude refractory", "", "R5 (D30)"),
    "durations.baseline_s": ("baseline", "s", "R5 (D27)"),
    "durations.hold_s": ("hold", "s", "R5 (D27)"),
    "durations.discard_s": ("discard", "s", "R5 (D27)"),
    "analysis.band_primary_hz": ("G", "Hz", "R1; R4 (C1) (D2)"),
    "analysis.bands_secondary_hz": ("gamma1, gamma2", "Hz", "R4 (D2)"),
    "analysis.total_band_hz": ("total band", "Hz", "R4 (D3)"),
    "analysis.window_rule": ("window rule", "", "R4; R5 (D4)"),
    "analysis.window_s": ("window", "s", "R4; R5 (D4)"),
    "analysis.taper": ("taper", "", "R4; R5 (D4)"),
    "analysis.rel_factor": ("rel_factor", "", "R4 (D6)"),
    "analysis.abs_factor": ("abs_factor", "", "R4 (D6)"),
    "analysis.amin_factor": ("A_min factor", "", "A5 (D7)"),
    "analysis.min_cycles": ("min_cycles", "cycles", "R1; R4 (D8)"),
    "analysis.collapse_r_frac": ("collapse", "", "R3; R4 (D9)"),
    "sweep.x_name": ("sweep x", "", "section 10.3 (handoff e)"),
    "sweep.x_values": ("sweep x values", "", "section 10.3 (handoff e)"),
    "sweep.y_name": ("sweep y", "", "section 10.3 (handoff e)"),
    "sweep.y_values": ("sweep y values", "", "section 10.3 (handoff e)"),
    "sweep.T_ramp_values": ("T_ramp values", "s", "section 10.3 (handoff e); D16"),
    "seeds.root_seed": ("root_seed", "", "section 6.6"),
    "seeds.n_seeds": ("n_seeds", "", "section 6.6"),
    "seeds.spawn_key": ("spawn_key", "", "section 6.6 (child of SeedSequence)"),
    "replication.tolerances_file": ("replication tol.", "", "Table 7.1 (D34)"),
    "robustness.check_id": ("robustness check", "", "Table 7.2 (D35)"),
    "robustness.criteria_file": ("robustness thr.", "", "Table 7.2 (D35)"),
    "robustness.criteria_sha256": ("criteria SHA-256", "", "Table 7.2 (D35)"),
    "budget.max_wall_h": ("budget", "h", "this plan (D36)"),
    "run.kind": ("run kind", "", "section 10.3; values DL-055"),
    "run.id": ("run id", "", "section 10.3"),
    "run.workers": ("workers", "", "section 10.3"),
    "run.wall_limit_s": ("wall limit", "s", "DL-058"),
    "output.dir": ("output dir", "", "section 10.3"),
}


def make_param_table(cfg: dict) -> list[dict]:
    """Rows (name, key, value, units, status) for every resolved key (DL-059).

    A plain table built from the resolved config; it does not claim Nordlie
    sectioning. The reserved bookkeeping key `_resolved_from` is not listed.
    """
    rows = []
    for section, body in cfg.items():
        if section.startswith("_") or not isinstance(body, dict):
            continue
        for name, value in body.items():
            key = f"{section}.{name}"
            symbol, units, status = PARAM_META.get(key, (name, "", ""))
            rows.append({"name": symbol, "key": key, "value": value,
                         "units": units, "status": status})
    return rows


def param_table_markdown(rows: list[dict]) -> str:
    """Render make_param_table rows as a Markdown table."""
    head = "| Name | Key | Value | Units | Source / status |\n| --- | --- | --- | --- | --- |\n"
    body = "".join(
        f"| {r['name']} | {r['key']} | {r['value']} | {r['units']} | {r['status']} |\n"
        for r in rows)
    return head + body
