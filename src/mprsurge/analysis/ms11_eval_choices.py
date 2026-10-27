"""MS11 evaluation choices (11b; docs/ms11_eval_rules.md, DL-343): the required fields of configs/ms11/ms11_eval.yaml.

Reads the choices and refuses to default any of them. A choice that the plan and the rulings leave open is a REQUIRED field whose value is null in the file until the
reviewer rules it; reading it (`choice`) raises MissingChoice. `open_fields` lists the null ones; the launcher (ms11_runlist.check_launch) refuses a real launch while any
is open, so the evaluation rules are complete before the first MS11 run (the MS10 10e pattern). Nothing here reads a record, simulates or classifies.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .. import config as C

EVAL_FILE = "configs/ms11/ms11_eval.yaml"


# Items that are not required fields and block nothing but the list they belong to. Empty since 11d: the RB9(d) specification was ruled (Reading A, DL-367) and is a required field.
PENDING: tuple = ()


class MissingChoice(Exception):
    """A required evaluation field is absent, null or not an allowed value."""


# name -> allowed values (None: free value of the stated type, checked only for presence). Every name must appear in `choices` and in `meta` of the file.
REQUIRED: dict[str, tuple | None] = {
    # --- ruled (value present) ------------------------------------------------------------------------------------------------------------------------
    "rb2_gate_class_set": None,                    # DL-336 (ruling 2b): the frozen Table 2.1 surge classes
    "rb2_gate_sigma_factors": None,                # DL-336: 0.5 sigma and sigma only
    "rb2_judged_T_ramp_s": None,                   # M11-2 recommendation, accepted
    "rb2_beside_gate": None,                       # 2 sigma, other T_ramp, stricter readings: reported, post hoc, no gate
    "rb2_subgrid": None,                           # carried in as recorded (97 of 225, D24 failed), not re-evaluated
    "rb2_control": None,                           # DL-251 controls: post hoc, no gate
    "s11_onset_reading": ("classifier_centre",),   # frozen O1; raw crossing secondary
    "s11_short_window_limit_stated": (True,),
    "rb5_delta0_reference": ("s5_grid_member",),
    "rb5_class_unchanged_means": ("same_table21_label",),
    "rb5_delay_shift": ("reported",),
    "rb6_rtol": ("reported_not_a_pass_test",),
    "rb6_solver_pair_scope": ("headline_only",),   # DL-337: Radau only at the headline T_ramp
    "rb6_floor_other_T_ramp": ("reported_default_rung_only",),   # consequence of the ruled floor scope (default rung, M11-4)
    "rb6_network_dt_pair": None,
    "rb6_network_fpk_sources": None,               # M11-6 (c)
    "rb6_network_fpk_bound_boundary": ("strict",), # plan text "< 2%"
    "rb6_network_seeds": None,
    "rb6_network_class_claim": ("none",),          # G4-C3 stands (M11-5: no new controls)
    "rb6_network_time_origin_check": ("required",),
    "rb9c_unit_of_change": ("raw_class_categories_beside",),   # M11-7
    "rb9c_rb10_map_mode": ("D",),
    "rb9c_subgrid": ("reported_no_verdict",),
    "rb9d_method": ("two_runs_tau_8_12_ms_reported_only",),    # M11-8 (d)
    "rb10_variants": None,                         # frozen leaf
    "rb10_window_line_of_s13": ("same_computation",),
    "a11_mode": ("recompute_and_compare",),        # M11-10 (c)
    "a11_row_unit": ("criterion_leaf",),
    "a11_status_vocabulary": None,                 # ruling 13 narrows the 11b vocabulary of six words to the four status words (DL-358); checked in tests
    "a11_new_thresholds": ("none",),
    "d36_basis": ("B",),
    # --- ruled at 11c (DL-345 to DL-358; the 14 fields that were open at 11b) -------------------------------------------------------------------------
    "rb2_failed_run_counts_as": ("not_kept",),                       # ruling 1: denominator stays 10, failed runs reported
    "rb5_updown_source": ("P5_with_S4_reported_beside",),            # ruling 2
    "rb6_network_fpk_no_episode": ("not_evaluable",),                # ruling 3: listed by seed, neither passes nor fails
    "rb6_network_vp_comparison": ("reported_only",),                 # ruling 4
    "within_boundary": ("inclusive",),                               # ruling 5: "within X" is at most X; "<" and ">" strict as the plan writes them
    "rb9a_source": ("unit_test_level",),                             # ruling 6
    "rb9b_cells": ("headline_gate_map_cells_reported",),             # ruling 7
    "rb9b_comparison_window": ("classifier_episode",),               # ruling 8
    "gate_cell_set": ("map1",),                                      # ruling 9
    "not_run_cells_count_as": ("excluded_with_worst_case_flag",),    # ruling 10
    "s13_floor_other_T_ramp_form": ("rb3b_form_reported_only",),     # ruling 11
    "rb9d_runs": ("separate_post_hoc_list",),                        # ruling 12 (YES; the specification was ruled at 11d, rb9d_parameter_spec)
    "a11_logged_verdict_map": None,                                  # ruling 13: table word -> PASS / FAIL / NOT EVALUABLE / REPORTED
    "a11_extra_columns": None,                                       # ruling 14
    # --- ruled at 11d (DL-366 to DL-368) ----------------------------------------------------------------------------------------------------------------
    "rb9d_parameter_spec": None,                                     # 11d ruling 2b: Reading A (tau_ms 8 and 12; tau_d 5 ms, durations in seconds, eta numbers, Delta, J, band, threshold held); reported only
    "a11_pass_with_departures_words": None,                          # 11d ruling 2c: a logged word in this list maps to PASS only with the departures named in the note column
}


def load_choices(path: str | Path | None = None) -> dict:
    p = Path(path) if path else C.repo_root() / EVAL_FILE
    return yaml.safe_load(p.read_text(encoding="utf-8"))["choices"]


def load_file(path: str | Path | None = None) -> dict:
    p = Path(path) if path else C.repo_root() / EVAL_FILE
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def choice(ch: dict, name: str):
    """The value of one required field; MissingChoice if it is absent, null or not an allowed value."""
    if name not in REQUIRED:
        raise MissingChoice(f"{name!r} is not a field of {EVAL_FILE}")
    v = ch.get(name)
    if v is None or (isinstance(v, (list, dict, str)) and len(v) == 0):
        raise MissingChoice(f"{EVAL_FILE}: required field {name!r} is not set (open for the reviewer's ruling)")
    allowed = REQUIRED[name]
    if allowed is not None and v not in allowed:
        raise MissingChoice(f"{EVAL_FILE}: {name} = {v!r} is not one of {allowed}")
    return v


def open_fields(ch: dict | None = None) -> list[str]:
    """Names of the required fields that are absent, null or not allowed (the fields the reviewer still owes)."""
    ch = load_choices() if ch is None else ch
    out = []
    for name in REQUIRED:
        try:
            choice(ch, name)
        except MissingChoice:
            out.append(name)
    return out


def check_all(ch: dict | None = None) -> dict:
    """Every required field read once: {name: value}. Raises MissingChoice at the first open field (nothing is defaulted)."""
    ch = load_choices() if ch is None else ch
    return {name: choice(ch, name) for name in REQUIRED}
