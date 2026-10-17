# MS7 gate report (7i): classifier and criteria

Written for: the project owner, for the approval before 7j. Fresh-context review of the MS7 work (7a to 7h2), read-only on code, configs and results. Plan v0.5 is not edited; no decision is changed; nothing is frozen, no tag exists, no freeze SHA-256 has been computed. HEAD at the start of 7i: 88ee26a. Fast suite at that HEAD and at the end of 7i: **469 passed, 7 deselected, 4 xfailed, 1 warning** (the warning is a ComplexWarning in `test_ring.py`, from MS5 code); 7i changes no code. Decision log: DL-159 (rulings entered), DL-160 (this review).

## 1. Gate wording (plan)

Table 11.1, row MS7: "Classifier and criteria: S5 baseline-only mode-N runs (headline and map cells; v0.5); A8 (classes, A_ref, sensitivity, baseline rho report from those runs); D43 floor levels, RB3(a) range and floor values, A4 eta_bar grid and Heun dt ladder fixed; criteria files". Done when: "test_surge_metrics passes; tag criteria-frozen". Unlocks: "S5 ramp runs onward (MS8)". Section 11, test table, `test_surge_metrics`: "A8 synthetic signals, seeded: burst on/off within one step; chirp; 5-cycle ring -> NS or D-none (envelope growth < 0); slowly damped ring with more than 10 cycles above threshold -> NS or D-none (fitted growth negative by more than 2 standard errors); pure trend -> NS; zero baseline; P_G/P_non-G threshold; an S-abs case".

Ruling X-1 (DL-157): "test_surge_metrics passes" reads **"pytest exits 0 with the documented xfails"** (the sheet and the criteria file say "xfail"; the plural is the 7i correction, because DL-158 added three).

## 2. Gate items and results

| Gate item | Result | Evidence |
|---|---|---|
| S5 baseline-only mode-N runs, headline and map cells | **Done.** 1,226 cells x 10 seeds = 12,260 runs, 0 failed, all records clean tree, seeds [7, 4, s], cell-list SHA-256 8e67bbd2..., start states equal the 7d list; 25 map-2 duplicate groups bit-identical | DL-141, DL-143; `scripts/check_S5_baseline.py` re-run in 7i: exit 0, 0 problems |
| A8 classes | **Done**, all classes through a D8 call labelled "provisional (D8 open, DL-137)". O10 and O11 implemented; O12 reported-only, not implemented (ruled) | DL-140, DL-157 |
| A8 A_ref | **Done**: 2.176222 (median band-passed Hilbert envelope, whole cycles); threshold 0.217622; UNVERIFIED reading, ruled | DL-139, H-1 |
| A8 sensitivity | **Done on pre-freeze data only** (synthetic, stored S3/S4, baseline records); the plan's RB10/RB9(c) percentages need ramp classes and are evaluated by A11 after the freeze | DL-146, DL-147, U-1, S3S4 |
| A8 baseline rho report | **Done**: 67.5 percent of records and 66.0 percent of cells at rho >= 0.5; headline 0.68; reported per W | DL-145, DL-147 |
| D43 floor levels | **Fixed as draft, UNVERIFIED**: delta_0 1e-9, 1e-6, 1e-3; sigma_floor 1.59e-9, 1.59e-6, 1.59e-3 | DL-152 |
| RB3(a) range and floor values | **Computed.** Solver floor 6.66e-16 (hold run, 88 s); headline t_pred 115.22 s; headline is outside the RB3(a) range; coverage 0 to 2 of 13 T_ramp per path and profile | DL-149, DL-151, DL-152 |
| A4 eta_bar grid | **Fixed as draft**: 0.025 (801 points on [-10, 10]); halving moves t_pred by at most 0.014 of a step | DL-149, DL-152 |
| Heun dt ladder | **Fixed as draft**: {1e-3, 5e-4, 2.5e-4, 1e-4} tau, coupled Brownian increments; RB6 statistic DL-154 | DL-152, DL-154 |
| Criteria files | **Draft complete**: `configs/robustness_criteria.yaml` (124 labelled leaves: 64 logged, 59 UNVERIFIED, 1 open = RB8 M4 criteria, deferred), `configs/S13.yaml`, `docs/robustness_criteria.md` (generated in 7i) | DL-156 to DL-160 |
| `test_surge_metrics` passes | **Passes under X-1 with departures** (section 4 and 5): fast suite exits 0, 4 strict xfails | section 5 |
| Tag `criteria-frozen` | **Not created.** 7j only, on your instruction | `docs/ms7_7j_procedure.md` |

**Verdict.** The MS7 work items are complete as drafts. The MS7 gate is **not yet passed**: the tag does not exist. If you approve, the gate passes at 7j **with three departures** (section 3) and one reported limitation set. Findings below need your read first; findings 7i-1 and 7i-2 should be settled before 7j.

## 3. Departures from the plan at this gate

1. **D8: the plan estimator fails 2 of the plan's 8 A8 ring items** (X-1, D8 = A). The 15-cycle slowly damped ring is called damped in 86.5 percent of draws against 95; D_ring_slow_-3 (mode D, T_ramp 120 s) is classed D-tr where NS or D-none is required. Also: 26 of 36 pre-registered F1 cells miss the 95 percent sign match, 5 of 5 zero-growth cells exceed 5 percent false damped; no candidate fix meets the DL-136 numbers (DL-155). One strict xfail (DL-073).
2. **Zero baseline: Table 2.1 says the power ratios and mode-N classes are "undefined"; the code has no such class** (option (a) ruled at 7i, DL-159). Constant record gives NS; exactly zero record gives S-sus with NaN peak_rho and a RuntimeWarning; a noise-free linear trend gives S-sus. Three strict xfails. Classifier unchanged. Deterministic runs use mode D, which gives D-none.
3. **RB3(a) is not judged at the headline** (G6 reading, DL-157): the headline (120 s) is outside the RB3(a) range for every floor >= 1e-16; coverage is 0 to 2 of 13 T_ramp per path and profile; P2 sigmoid has no predicted onset. G6 at the headline rests on RB3(b) and RB6. This departs from the G6 text "RB3(a) ... pass at the headline point". Reasoned arithmetic until MS8.

Reported limitation (not a departure): **short-window false surges**. On seeded white noise (sd 0.04, mode N) non-NS of 500: 306 (W = 0.2 s), 400 (0.333 s), 172 (0.593 s), 24 to 26 (1.054 s), 2 (1.874 s), 0 (2 s). The rate is set by the power tests and the 10-cycle rule, not by D8. 8 of the 13 map-2 T_ramp have W < 2 s. Reported per W in every result; claim limited through the G6 route; real M3 rate measured by NC1 (G7).

## 4. Plan-named test list (section 11, MS7 row) against the tests that exist

Run in 7i: `tests/test_surge_metrics.py`, `tests/test_surge_classes.py`, `tests/test_criteria_draft.py`: 99 passed, 4 xfailed.

| # | Plan item | Test (file) | Present | Result |
|---|---|---|---|---|
| 1 | burst on/off within one step | `test_burst_on_off_within_one_step` (metrics); `test_a8_onset_offset_within_one_window_step_and_frequency_within_1_over_w` (classes) | yes | pass, pass |
| 2 | chirp | `test_chirp_peak_follows_instantaneous_frequency` (metrics) | yes | pass |
| 3 | 5-cycle ring, NS or D-none, growth < 0 | `test_five_cycle_ring_has_negative_growth_and_fewer_than_ten_cycles` (metrics) | **core level only**: growth < 0, 4 < cycles < 6; no class assertion | pass. Class-level result is measured in the A8 study (passes), not asserted in the suite |
| 4 | slowly damped ring, > 10 cycles, NS or D-none, growth negative by more than 2 SE | `test_slowly_damped_ring_has_more_than_ten_cycles_and_negative_growth` (metrics: > 10 cycles, rate < -2 SE); `test_slowly_damped_ring_rate_matches_true_decay_after_step_onset` (metrics) | **core level only** | first passes; second is **strict XFAIL** (DL-073). The class-level NS or D-none requirement is **not asserted by any test**; it fails in mode D (D-tr) and is recorded only in DL-147/DL-155 |
| 5 | pure trend -> NS | `test_pure_trend_has_no_cycles_and_no_gamma_power` (metrics) | **core level only** | pass. Class level, probed in 7i (not a test): noise-free trend gives S-sus in mode N at W = 0.2, 0.2 and 2 s; trend with noise gives S-rel at W = 0.2 s and NS at W = 2 s; mode D gives D-none |
| 6 | zero baseline | `test_zero_baseline_raises_nothing_and_returns_a_known_class[exact_zero, constant]`, `test_zero_baseline_constant_gives_ns_with_finite_outputs` (classes) | yes | pass x3 |
|   |   | `test_zero_baseline_exact_zero_has_no_nan_in_outputs`, `test_zero_baseline_mode_n_class_is_undefined[exact_zero]`, `[constant]` (classes) | yes | **3 strict XFAIL** (DL-158) |
| 7 | P_G/P_non-G threshold | `test_mode_n_relative_threshold_edges[1.5, 2.0, 4.0]`, `test_mode_n_relative_default_factor_is_two`, `test_mode_n_s_rel_relative_only` (classes) | yes | pass x5 |
| 8 | an S-abs case | `test_mode_n_s_abs_absolute_only`, `test_mode_n_factor_edges[...]`, three O11 tests (classes) | yes | pass |

Missing: nothing is missing by name. Weak: items 3, 4, 5 are asserted at core level only; the class-level half of the plan wording is not in the suite (finding 7i-1).

## 5. The xfails and what "exits 0" means

| # | Test | strict | Reason in the marker | Documented in |
|---|---|---|---|---|
| 1 | `test_surge_metrics.py::test_slowly_damped_ring_rate_matches_true_decay_after_step_onset` | yes | DL-073: step-onset filter bias, rate -3.4 against -6.1 per s (UNVERIFIED) | DL-073, DL-137, DL-155, DL-157 (X-1), sheet 1, criteria `d8_estimator.known_limitation`, `gate_wording` |
| 2 | `test_surge_classes.py::test_zero_baseline_exact_zero_has_no_nan_in_outputs` | yes | DL-158: 0/0 gives NaN odds, absolute test 0 >= 2 x 0 passes, S-sus with NaN peak_rho | DL-158, DL-159, sheet end of section 8; **not in the criteria file** |
| 3 | `...::test_zero_baseline_mode_n_class_is_undefined[exact_zero]` | yes | DL-158: no "undefined" mode-N class | same |
| 4 | `...::test_zero_baseline_mode_n_class_is_undefined[constant]` | yes | same | same |

**What "pytest exits 0 with the documented xfails" means, exactly.** In `pytest` (full) or `pytest -m "not slow"` every selected test passes or is one of these four strict xfails: no failure, no error, and no unexpected pass. Because the marks are strict, an unexpected pass is reported as a failure and pytest exits 1, so exit 0 also asserts that the four behaviours are still present. It does **not** mean: the plan's test items are met (section 4), the estimator is right (departure 1), the class-level ring and trend requirements hold (7i-1), the 7 slow tests were run (they are deselected by `-m "not slow"`; the full run is in 7j), or that there are no warnings (1 ComplexWarning from MS5 code). None of the marks sets `raises=`, so a xfail also "passes" if its body fails for an unrelated reason (7i-4). No global `xfail_strict` or `filterwarnings = error` is set in `pyproject.toml`; each mark carries `strict=True` itself.

## 6. Review findings (read-only; nothing fixed except line endings)

Severity: M = affects what the gate or the freeze claims; L = traceability or hygiene; I = information.

| ID | Sev | Finding | Recommendation |
|---|---|---|---|
| 7i-1 | M | The class-level A8 requirements for the 5-cycle ring, the slowly damped ring and the pure trend are not asserted by any test. Departure 1 (2 of 8 ring items) and the noise-free trend S-sus are recorded in DL, sheet and criteria, but the suite exits 0 whether or not they remain true | Before 7j, with your approval: add the A8 ring items and the trend case as class-level tests, the failing ones as strict xfails with `raises=AssertionError`. Or accept that the departures live in documents only |
| 7i-2 | M | The criteria file cannot be frozen as it stands. `meta.draft: true`, `frozen: false`, `freeze_tag: null` and the header say "DRAFT"; `test_draft_not_frozen` asserts it; the file cannot contain its own hash; F-19 reads "proposed ... not yet ruled" (now confirmed); `decision_log_through` is DL-158; `gate_wording` names one xfail (now four) and names only departure 1; `RB4.perturbation_rel_box` source (7i-6). Also, the plan's 7j row ("the commit that adds the approval DL entry" carries the tag) differs from the DL-084 precedent (tag on the file commit, hash entry in a following docs-only commit) | Pre-freeze content commit (step 3 of the 7j procedure) with your approval, then hash. Follow DL-084: tag on the commit that holds the final file and the approval entry; a following docs-only commit records the hash. Needs your ruling (question Q1) |
| 7i-3 | I | Line endings. The draft criteria file is already LF (26,469 bytes, 240 lines, no CR, no BOM). `docs/ms7_plan.md` (CRLF) and `docs/ms7_signoff.md` (mixed) were not; both are now LF in the working tree. `.gitattributes` sets `* text=auto eol=lf`, so the index and HEAD blobs were LF all along: `git hash-object` of each normalised file equals its HEAD blob, `git diff` and `git diff -w` are empty. **There is no content change to commit, so no normalisation commit was made** (an empty commit adds nothing; say if you want one). Not touched: `ms3_gate_report.md`, `ms4_plan.md`, `ms5_gate_report.md`, `ms6_plan.md` are CRLF in the working tree, LF in the index, not cited | Hash `git show <commit>:configs/robustness_criteria.yaml` (the LF blob), not the working file, as in DL-084 |
| 7i-4 | L | None of the four xfail marks sets `raises=`; a xfail also "passes" when the body fails for another reason (an exception from a refactor) | Add `raises=AssertionError` (changes a mark; your ruling) |
| 7i-5 | L | The criteria file does not list the three zero-baseline xfails or departures 2 and 3 | Add in the pre-freeze commit |
| 7i-6 | L | `RB4.perturbation_rel_box` source says the plan tags the box "[reasoned, not tested]"; I found no such tag in Table 7.2, S16 or the parameter table (line 1692 gives "+-10% (S16)"). The same words are in `ms7_plan.md` F-19 | Reword the source to "Table 7.2 RB4, S16: +-10 percent" in the pre-freeze commit |
| 7i-7 | L | `RB3.c_T_ramp_s` and `d_T_ramp_compared` hold 56.23, 100.0, 177.8, 316.2 and are labelled logged; the plan says 56, 100, 178, 316. The 4-digit values are the grid points 10^(k/4) rounded by us | Label the 4-digit values as the S5 grid points (source S5 grid, `configs/S5_cells.yaml`) |
| 7i-8 | L | Value trace (review item 1). Every leaf of the criteria file has a source and a label (124 leaves, 0 without source; 1 logged leaf carries an owner confirmation in its source text, RB3 `a_range_rule`; fine). `configs/S13.yaml` part 1 is in the plan (S13 row, RB6), part 2 is DL-152, labelled UNVERIFIED. `configs/A4.yaml` is unchanged since MS6 except a comment (DL-152); `configs/A4_grids.yaml` since MS6 only the eta_bar comment; the other A4 grid values trace to DL-113 and DL-114 except **ratio_max 0.5 and tau_d_line n = 491**, which no DL entry names (blanket "working value, UNVERIFIED" header; not in the criteria file) | Name both in a one-line DL note when convenient; no effect on the freeze |
| 7i-9 | I | Pre-registered numbers (review item 2). DL-136 (commit dfa1083, 02:52) precedes the 7b code (b0c33af 02:56) and run (record 02:57:06); `MATCH_MIN` 0.95, `FALSE_DAMPED_MAX` 0.05, `FLOOR` 2.0 per s appear once in history (b0c33af), never changed; `d8_study` reuses them. DL-153 and its code (ff5666a, 12:29) precede the run (record 12:37:13, commit 6343ba9 clean). DL-144 (f3a013e), DL-146 (252bf64), DL-148 (fe2c6ff), DL-150 (fda66a4) each precede their run. The decision log is append-only after dfa1083 except one status line (DL-138 closed by DL-139, commit 6d50d68). No result file was written after its DL commit (nothing in `results/` newer than c06cc90 at 12:38) | none |
| 7i-10 | I | 7e records (review item 5): 1,226 records, 12,260 runs, 0 failed, `dirty = false` in all; commits 87af6c1 (headline, 1 record) and 5963885 (1,225); spawn keys [7, 4, s], s = 0 to 9 in every record; cell-list SHA-256 8e67bbd2b366e86f... equals DL-141; spec hash fe8590ce... equals `configs/S5_cells.yaml`; file mtimes 03:35:42 to 03:47:45, before the DL-143 commit (03:50:28). Every output of every MS7 run (7b, A_ref, 7f x2, 7g, F11, 7g2) hashes to the value stored in its own run record; the A_ref source hashes in the criteria file (bb12620d..., 0231a2b7...) match the files on disk | none |
| 7i-11 | L | Seed keys (review item 6), root seed 20261008 throughout. Streams: [s] s = 0 to 9 (runner seed index, calibration, timing [0]); (7, 2, i) 7b; (7, 3), (7, 5), (7, 7) config keys with no draws; (7, 4, s) baseline; (7, 6, 1, k), (7, 6, 2, k), (7, 6, 3, k) A8 sensitivity; (7, 8, 2, i), (7, 8, 3, i), (7, 8, 5, 1, i), (7, 8, 5, 2, i) 7g2; proposed (7, 9), (7, 9, 0), (7, 9, 1, k). **No equal key and no prefix relation with [7, 9]; no collision between different purposes.** Two reuses by design: the 7g2 F1 family reuses the 7b stream (7, 2, i) (reproduction check), and the 7g2 white-noise table reuses (7, 6, 2, k) (same draws as DL-147). `scripts/study_envelope_growth.py:26` seeds the DL-073 reproduction with a plain `default_rng(20261014)`, outside the SeedSequence scheme (no collision possible). The collision test scans literal `spawn_key=(...)` and `rng_for(...)` only, so it does not see (7, 8, 2) or the constant (7, 2); DL-158's list of keys in use omits (7, 8, 2) | none for the freeze; extend the test regex or list keys in one table at MS8 |
| 7i-12 | L | Housekeeping (review item 9). Deny rule: `Bash(git push:*)` is in `.claude/settings.local.json` (git-ignored, so it is not in the repository); there is **no `PowerShell(git push ...)` rule**. No git remote is configured, so a push cannot succeed now. Defender exclusion and the backup copy are user-reported and cannot be checked from here; the backup is a copy, not a remote, and the tags are local only | Add a PowerShell deny rule (your settings change); keep the backup current after 7j |
| 7i-13 | I | Git identity is the placeholder "Your Name <you@example.com>" on all commits and on the existing tags; the new tag will carry it, as `tolerances-frozen` does | none, or set it before 7j |
| 7i-14 | I | Sign-off sheet (review item 7): every row of sections 1 to 7 has a ruling in section 0 (7h, 7h2, 7i). Rows still open: none needing a ruling. Deferred or carried by ruling: F-23 (M4 criteria), O12 (defined at MS8), H-3 (loader at MS8), U-7 (classifier fix), Q3 (plan question), K5, K10, K4-net. One assumption of mine: the 7h2 note "pure linear trend gives S-sus, same options" is taken as covered by option (a) | Confirm in Q2 |
| 7i-15 | L | The 7h row of the plan lists a loader and repointing `robustness.criteria_file` on A4 and S5; neither was done (H-2, H-3 ruled to MS8). Not in the Table 11.1 MS7 gate text | Carried to MS8 |

## 7. Open and carried items

Carried by ruling: K5 (deferred); K10 (not reproduced as worded, 13 to 42 percent J dependence, non-blocking); K4-net (M2 network coupling unsourced); sigma 0.0624 UNVERIFIED until S8 at MS10; the two DL-105 timing exceptions; D36 24 h cap rows without timing cells; O12 and the loader to MS8; M4 criteria (F-23); Q3 (plan question, after MS8 data); U-7 classifier fix (baseline edges in samples; changes 6 of 500 white-noise records at W = 1.054 s); the real short-window false-surge rate (NC1, G7); real RB10 and RB9(c) percentages (A11, after the freeze).

## 8. What changes if you later choose D8 option B

Data: `docs/ms7_signoff.md` section 1.1 (from the saved 54-candidate table, DL-155). B1 = zero-pad edge treatment with AR(1) SE; B2 = B1 with a 40 ms fit-start shift.

- **Code.** A new estimator behind the existing `D8Estimator` interface; the classifier logic is untouched. B1 changes "standard errors of the fit" and moves edge handling into the estimator (O16 changes from "none" to a pad). B2 also changes the Table 2.1 wording "from the threshold crossing", which is your ruling and a plan-text question.
- **Tests.** B2 would make the strict xfail XPASS (rate within 10 percent in 86.5 percent of draws), and a strict XPASS fails pytest: the test must be retired or turned into a pass by ruling (X-1 (b)). B1 keeps it xfail. `test_d8_choice_a_with_known_limitation` and the O9/O16 rows change.
- **Gate numbers.** B does not meet the pre-registered numbers either: (i) misses 10 and 8 of 36 cells (B1, B2) against 26; (ii) is met by none of B1, B2 (B1c, the per-cycle SE, meets it); A8 ring items failed 4 (B1) and 3 (B2) of 8 against 2, and N_ring_fast_-25 becomes a surge class. Departure 1 would change its wording, not disappear.
- **Re-runs.** The A8 sensitivity once (about 45 s, same driver, U-4 becomes live); the 13 S2 ramps as an information check; the DL-147 white-noise table at sd >= 0.2 (sd 0.04 is identical for every candidate). The 7e records, the baseline rho report and 7g are unaffected (they do not call D8).
- **Criteria file.** `classifier.d8_estimator` (value, choice, known_limitation, gate_wording, unmet items), O9, O16, provisional labels. All before 7j, because they change the hash. After the freeze the same change needs a DL entry and a paper statement and re-classifies every ramp-run class; MS8 has not started, so the cost is lowest now.

## 9. Open questions for you (with a recommendation)

- **Q1 (7i-2).** Approve a pre-freeze content commit of the criteria file and tests at the start of 7j (flags to frozen, F-19 wording, three xfails and departures 2 and 3, `decision_log_through`, source rewording 7i-6 and 7i-7)? And tag order as DL-084 (tag on the file commit, hash in a following docs-only commit) rather than the plan 7j wording? **Recommend yes to both.** The procedure is in `docs/ms7_7j_procedure.md`.
- **Q2 (7i-1, 7i-14).** Add class-level tests and `raises=AssertionError` before the freeze, or leave the departures in documents only? Is the noise-free trend S-sus covered by option (a)? **Recommend adding them (small, no classifier change) and yes.**
- **Q3 (7i-12).** Add a `PowerShell(git push ...)` deny rule? **Recommend yes.**
- **Q4 (7i-3).** Do you want an empty commit labelled "line-ending normalisation only"? **Recommend no**: nothing to commit.
- **Q5.** "SHA-256 of the criteria files": hash only `configs/robustness_criteria.yaml` (the file H-3 names), or also `configs/S13.yaml`, `configs/A4_grids.yaml` and `configs/S5_cells.yaml` as secondary hashes in the tag message (their headers say they are frozen with the tag)? **Recommend the secondary hashes**, listed after the headline hash.
- D8 stays A (ruled); no question unless you reopen it.
