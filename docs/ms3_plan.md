# MS3 sub-step plan (rulings DL-094 and DL-095 applied; no decision open)

MS3 plan, written before any MS3 code. Binding source: `docs/plan.md` (Table 11.1 row MS3; sections 9.2 feasibility gate and 9.3 cut order; Table 9.1; T23 and T24 in the triage list). Decisions go in `docs/decision_log.md`; the rulings on D-2, D-5, D-6, D-7 and D-9 are DL-094, on D-1, D-3, D-4 and D-8 DL-095. This file holds none of its own and changes nothing in the plan. Rules as for MS2: one sub-step at a time; after each, `.venv\Scripts\python.exe -m pytest -m "not slow"` green, one commit `<type>(<scope>): <summary> [IDs]`, a report of at most 8 lines, then stop. No tags, no pushes unless asked. Every run writes a provenance record (6.6). Drivers only integrate, analysis modules only analyse, figure scripts only plot (10.1).

**MS3 row (Table 11.1):** "Mean-field timing gate (expensive cells; provisional eta_bar path)". Gate: "Predictions within allowance". Unlocks: S2 (MS4). Depends on MS1 (done). The plan places the first timing "after MS1" (9.2 step 1), so MS3 does not wait for A4.

**State at start:** `run_mf` (DOP853, Radau, breakpoints), `run_mf_noisy` (Numba stochastic Heun, `warm_up`), `make_path` with P1/P2/P5 paths, `resolve_config` with `path.eta_path_status` ("provisional" for an M3 path with explicit `eta_start` and `eta_peak`, "A4" when `path.eta_H` is given, "unresolved" otherwise), `run.py` spawn pool with `single_thread_env`, `run.wall_limit_s`. Not present: `configs/S5.yaml`, `scripts/time_one_run.py`, `results/timing/`, any timing code, `qif_network` (MS5).

**Not in MS3:** network timing at N = 10^4 and 3x10^4 (9.2 step 1 says "once that code exists"; MS5); re-timing of the headline on the A4 path (MS5, T23); any S-ID run; the Table 9.1 rows for S8 to S10 cannot be predicted from measurements yet (Open points 3).

## Sub-steps

| Step | Files | Tests (Table 10.1) | Plan sections | Acceptance |
|---|---|---|---|---|
| 3a (timing cells and provisional path) | `configs/S5.yaml` (the headline cell as a run config: P2, ref_devalle, T_ramp 120 s, linear, I = 0, mode D, explicit provisional `eta_start` and `eta_peak`); the timing-cell table (D-1); decision-log entry for the provisional path values | test_config: S5.yaml resolves with `path.eta_path_status == "provisional"` and the run record carries it; the hash changes if `eta_start` or `eta_peak` change; headline duration is 5 + 1.25 x 120 + 10 = 165 s = 16,500 tau (CP14); P5 at T_ramp 1000 s lasts 5 + 2 x 1000 + 10 s (P5 doubles T_ramp, 6.2) | 9.2 step 1, 4.4 (P2, P5), 6.2 durations, CP14, D12, T23 | Every timing cell resolves from its name and prints its tau simulated and path status; nothing integrates. |
| 3b (`scripts/time_one_run.py`) | `scripts/time_one_run.py` (CLI `--config configs\S5.yaml --cell <name> --repeat 3 [--workers N]`); `src/mprsurge/analysis/timing.py` (pure functions: summarise repeats, s/tau, extrapolation; no integration); `results/timing/` | test_timing (fast): summary of synthetic repeats (min, median, spread); s/tau = wall / tau simulated; extrapolation arithmetic on a toy family table (mean field: sum of tau x s/tau / workers; Heun: sum of steps x s/step / workers); the script on a toy cell of about 20 tau writes a record and a json into a tmp results dir; Numba compile and warm-up time is excluded and reported separately | 9.2 steps 1 and 2, 10.1, 6.6 | The script times a cell `--repeat 3` times, excludes first-call compile (`warm_up`), and writes `results/timing/<cell>.json` and a provenance record (commit, package versions, config hash, `eta_path_status`, repeats, tau simulated, solver step count where the solver reports it). |
| 3c (run the timing cells) | `results/timing/` outputs only (git-ignored); the log goes in the decision-log entry | none new (acceptance by inspection of the records) | 9.2 step 1 | The seven cells below run with `--repeat 3`, in the 9.1 machine state (sleep off, Defender exclusion, nothing else running). Per-cell wall, s/tau, steps and spread are tabulated. A cell that exceeds the time limit (D-6) is recorded as such, not dropped. |
| 3d (6, 8, 10 workers) | `scripts/time_one_run.py --workers N`; `results/timing/workers_{6,8,10}.json` | test_timing: the worker mode runs N identical-cost tasks in the runner's spawn pool with `single_thread_env` (toy cell) and reports per-task wall and throughput | 9.2 step 1 (last sentence), 9.1, 6.3 (one run per process) | Throughput (runs/h and speed-up against one worker) for the headline cell at 6, 8 and 10 workers; the worker count for the extrapolation is chosen from these (D-7). |
| 3e (extrapolation and launch rule) | `configs/timing_families.yaml` (run families: S-ID, Table 9.1 row, tau simulated or steps, number of runs, matching timing cell, allowance copied from Table 9.1); `analysis/timing.py` extended; the printed report also written to `results/timing/prediction.txt` | test_timing: per-family prediction equals the hand calculation on the toy table; the rule "prediction <= 1.5 x allowance and total <= D36 cap" is evaluated per row and for the total and reported pass or fail; a family with no matching cell is reported "no timing cell", never silently predicted | 9.2 steps 2 and 3, Table 9.1, 9.3, D36, T24 | The script prints a predicted wall time per run family and the total; each family is extrapolated from its matching cell, not from the headline alone; the launch verdict is printed with the numbers it used. |
| 3f (gate, review, report) | `docs/ms3_gate_report.md`; decision-log entries (the measurement and the decision, 9.2 step 3); fill the Commit/tag fields; fresh-context review of the MS3 diff (real gaps only), as 2f | none | 9.2 step 3, Table 11.1 MS3 | Gate "Predictions within allowance": all mean-field rows meet the rule, or the cut order of 9.3 is applied in order and logged until they do. Report, then stop; no S-run starts. |

Order: 3a, 3b, then 3c and 3d (independent), then 3e, then 3f.

## Timing cells (9.2 step 1) and the run family each stands for

| Cell | Definition (defaults, see Decisions) | Stands for | tau simulated |
|---|---|---|---|
| headline | P2, ref_devalle (J = -21, Delta = 0.3, tau_d = 5 ms), T_ramp 120 s, linear, I = 0, DOP853 rtol 1e-10 | S5 P1 and P2 mode D, S6 (P3, P4a, P4b are P2-based), S12 NC paths, S13 DOP853 rungs, S16 | 16,500 |
| delta_0.01 | headline with Delta = 0.01 | S7 map 1, low-Delta edge | 16,500 |
| delta_0.6 | headline with Delta = 0.6 | S7 map 1, high-Delta edge | 16,500 |
| p5_1000 | P5, T_ramp 1000 s | S5 P5 at the longest ramp | 201,500 |
| m2_ramp | M2 mean field, eta_bar from 1 below the lower fold to 1 above the upper fold, T_ramp 1000 s, J = 15, Delta = 1 (D-9) | S2 | 1000 s ramp (tau = 10 ms: 100,000 tau) plus baseline and hold per S2 |
| radau_1e-12 | headline path, Radau, rtol 1e-12 | S13 Radau | 16,500 |
| mode_n | headline path, mode N, stochastic Heun dt 1e-3 tau, 2 s discard, placeholder sigma | S5 noisy seeds, S11, S7 noisy subgrid | 16,700 (2 s + 165 s) |

Radau and mode N are timed on the headline path because the plan names no other. Solver step counts (`nfev`) are recorded where available, so s/step is reported next to s/tau.

## Extrapolation per run family (9.2 step 2)

Mean field: sum over runs of tau simulated x measured s/tau, divided by workers. Heun: sum of steps x measured s/step, divided by workers. The plan says only "each run family is extrapolated from its matching timing cell"; the mapping below is this plan's proposal.

| Table 9.1 row | Matching cell | Work count |
|---|---|---|
| One P2 ramp, T_ramp 120 s | headline | 16,500 tau |
| S1 to S4, A1 to A6 | S1, A0 to A2 from their MS2 records; S2 (13 T_ramp values, 1 to 1000 s log) from m2_ramp (D-9) | tau simulated summed over the 13 T_ramp values; row allowance < 30 min |
| S2, S5, S6 (ramp sweeps) | headline for P1, P2, P3, P4; p5_1000 for P5; mode_n for the noisy seeds | sum over the 13 T_ramp values (1 to 1000 s) of the run durations (P2: 5 + 1.25 T + 10 s), times profiles, paths and start distances as in Table 6.2 |
| S5 baseline-only mode-N (MS7) | mode_n | 7 s runs: per-step cost x steps (Table 9.1 gives 8.6e9 Heun steps) |
| S7 map 1 (900 cells x 120 s) | delta_0.01 and delta_0.6 as bounds, headline as the centre; all three reported | 900 x 16,500 tau |
| S7 map 2 and noisy subgrid | headline (map 2); mode_n (225 x 10 seeds) | Table 9.1 step counts |
| S8, S10, S12 networks, K8, S9 | none until `qif_network` exists | Table 9.1 R5 estimate shown, labelled "not measured" |
| S11, S12 mean field, S16 | headline, mode_n | small; counts from Table 6.2 |
| S13 numerics | headline, radau_1e-12 (the plan assumes Radau is 3 to 10 times slower; this is what is checked), mode_n | scope in Table 6.2 S13 |

## Launch rule (9.2 step 3)

Launch only if the prediction is <= 1.5 x the Table 9.1 allowance and the total is within the D36 cap (24 h). Otherwise apply 9.3 in order: (1) Radau only at the headline T_ramp; (2) drop network dt = 1e-4 tau unless 2.5e-4 tau fails RB6; (3) S9 to 5 seeds; (4) sigmoid for P2 only; (5) drop the 562 s and 1000 s ramps from P5 and the start-distance runs; (6) map 1 to 20 x 20 with boundary refinement (D31); (7) map 2 to 13 x 13; (8) max_step to 0.1 tau, only if RB6 shows < 1% change at the headline point. Never cut: the G0 replication runs, NC1, the S8 headline overlay, the S13 headline tolerance check, the A8 tests and the one-at-a-time part of S16. Log both the measurement and the decision. Re-time after any change to the solver, the Numba kernel or package versions (9.2 step 4); the timing records carry the package versions so a change is detectable.

## Decisions that need the user (defaults used if no ruling)

| # | Question | Default |
|---|---|---|
| D-1 | **Ruled (DL-095).** How `--cell` names resolve. | One yaml per timing cell under `configs/timing/`, each a normal committed run file layered on `configs/S5.yaml`: `--cell headline` resolves to `configs/timing/headline.yaml`, merged over `configs/S5.yaml` (the layering is done by `time_one_run.py`, which passes the merged dict to `resolve_config`). No schema change, no new config key. |
| D-2 | **Ruled (DL-094): accepted.** Provisional eta_bar path values. | `path.eta_start = 2.5` and `path.eta_peak = 6.0`: the D12 rule with a placeholder eta_H = 4.0 (the ref_devalle eta_bar, Table 3.2), recorded `provisional` and UNVERIFIED until A4 (MS5); a placeholder, not an estimate of eta_H. One headline repeat is also timed on a second bracket (eta_start 1.5, eta_peak 5.0) to show the sensitivity. |
| D-3 | **Ruled (DL-095): default.** The Delta cells. | tau_d = 5 ms, J = -21 and the provisional path as in the headline, only Delta changed (0.01 and 0.6). "Near the Hopf window" is recorded as not located and re-timed at MS5. |
| D-4 | **Ruled (DL-095).** Sigma for the mode-N cell. | Placeholder `noise.sigma = 1e-3`, recorded UNVERIFIED and labelled "not calibrated" (calibration is MS5, 6.4). |
| D-5 | **Ruled (DL-094).** "Allowance" in the 1.5 x rule. | The upper end of the matching Table 9.1 row's wall-time range, which is stated at 6 workers; rows given as "< X" use X. Launch if the prediction is <= 1.5 x that value (and the total is within the D36 cap). The prediction is made per Table 9.1 row and lists the S-IDs the row covers. |
| D-6 | **Ruled (DL-094).** Time limit for the timing runs. | `run.wall_limit_s = 3600` per timing repeat; a cell reaching it is recorded "limit reached" with partial progress and its family is marked "lower bound". |
| D-7 | **Ruled (DL-094).** Worker count in the extrapolation. | 6 workers. The 8 and 10 worker timings are reported as measured and do not change the extrapolation; the report also prints the ideal-division value and the measured effective speed-up. |
| D-8 | **Ruled (DL-095): default.** Timing records. | Kind `timing`, outside `RUN_KINDS`, no skip rule; written to `results/timing/`; each record carries the commit, the dirty flag and the package versions. |
| D-9 | **Ruled (DL-094): yes.** An M2 ramp timing cell so S2 is extrapolated from its matching family. | Cell `m2_ramp`: M2 mean field, eta_bar ramped from 1 below the lower fold to 1 above the upper fold (Table 6.2 S2), T_ramp 1000 s (the longest of the 13 values; cost is linear in tau simulated), at the K4 point J = 15, Delta = 1 as used in S1 and A2; the fold eta_bar values are read from the A1 result, not entered by hand. Added as a seventh cell in 3a and 3c; it needs the M2 ramp path kind in `make_path` (3a checks that it exists and reports if it does not; no code is added without a ruling). Expected: `path_eta` with `model.type: M2` is enough. |

## Open points the plan leaves open (flagged, not decided)

1. **Cell definitions:** the plan gave no file layout for `--cell` and no tau_d, eta values or sigma for the Delta, P5 and mode-N cells; ruled in D-1 to D-4 (DL-095).
2. **Hopf window before A4:** "near the Hopf window" has no meaning until A4 gives eta_H; the plan itself says the path is provisional and the headline is re-timed after A4.
3. **Network rows (ruled, DL-094: the network gate is mean-field only until `qif_network` exists):** 9.2 step 1 repeats the timing for N = 10^4 and 3x10^4 "once that code exists" (MS5). At MS3 the S8 to S10 rows have only R5's estimates, so "Predictions within allowance" can be judged for the mean-field rows only, and the total mixes measured mean-field values with R5 estimates. The gate report must say so.
4. **S2 (M2 ramps through the saddle-node):** closed by D-9 (an M2 ramp cell is timed). The plan lists no such cell, so D-9 is a user-ruled addition to the cell list, not a plan edit.
5. **tau_d dependence of cost:** map 1 spans tau_d 1 to 50 ms and the plan lists no tau_d timing cell; the Delta cells bracket Delta only. The report says the tau_d range is not covered.
6. **Rows without a run count:** "S11, S12 mean field, S16 small" and "Spectrograms < 1 s per run" have no counts in Table 9.1; counts come from Table 6.2 or the row is reported "not extrapolated".
7. **Analysis timing:** Table 9.1 says analysis and reclassification (A8 to A11, RB10) are "measured in the timing gate", but no analysis timing cell is listed. Default: time `surge_metrics` on the stored headline series as an extra cell labelled "not listed in 9.2"; say if not wanted.
8. **Allowance vs prediction basis:** Table 9.1's allowances assume DOP853 at 20 steps per tau and 0.1 to 0.3 ms per step (estimates, not tests); the measured s/tau replaces those assumptions, and the report states the measured values next to them.
