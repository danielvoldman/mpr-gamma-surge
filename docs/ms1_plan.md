# MS1 sub-step plan (approved 2026-10-14)

Record of the approved MS1 plan for a fresh session. Binding source: `docs/plan.md` (Table 11.1, row MS1). Decisions are in `docs/decision_log.md` (DL-053 onward); this file holds none of its own. Rules: one sub-step at a time; after each, tests green, one commit `<type>(<scope>): <summary> [IDs]`, a report of at most 8 lines, then stop. No tags, no pushes unless asked. Use `.venv\Scripts\python.exe` for every Python command.

MS1 is done when: fast tests pass (all but network); `--dry-run` writes a run record with the commit hash; the tag `tolerances-frozen` exists (created only when the user says so).

## Sub-steps

| Step | Files | Tests (Table 10.1) | Plan sections |
|---|---|---|---|
| 1a-i (done, 9f27a8f) | units.py, config.py, params.py, configs/base.yaml | test_units (conversions only), test_config | 3.3, 3.1, 10.3, App. B, handoff (d)(e) |
| 1a-ii | provenance.py, run.py (`--dry-run`, runner skeleton, pool initialiser, atomic write, skip-if-done, manifest.csv) | test_provenance; test_runner part 1 (dry-run record with commit hash, skip-if-done/resume, forced failure recorded, toy task) | 6.6, 10.4, 6.1 (spawn guard) |
| 1b-i | models/mpr2d.py, mpr3d.py, fixed_points.py, ramps.py; run.py change per DL-069 (spawn key = seed index, so sweep cells share noise streams) | test_models_2d, test_models_3d, test_fixed_points (K1, K2 coarse), test_ramps; test_runner: spawn keys per DL-069 | 3.1, 5.2 A1/A4, 4.4 Paths, 10.5 |
| 1b-ii | simulate_mf.py (`run_mf`; `run_mf_noisy` with Numba stochastic Heun); enforce `run.wall_limit_s` for jitted and solve_ivp runs (a chunked kernel with a wall-time check between chunks, or a parent hard kill of the worker); DOP853 to Radau retry, flagged; record field `numba_cache_cleared` (null until make_all.ps1 sets it) | test_noise; RB9a part of test_units; test_runner part 2 (workers 1 vs 6 with real `run_mf`, solver failure then Radau retry flagged, wall-limit timeout for a long solve_ivp and a long jitted run); a heartbeat test (the ETA log line, including runs fewer than 10) | 6.2, 10.4 |
| 1c | analysis/surge_metrics.py core: `spectrogram_v`, `band_power`, `envelope`, `envelope_growth`, `count_cycles` | test_surge_metrics subset: burst on/off, chirp, 5-cycle ring, slowly damped ring (more than 10 cycles, growth negative by more than 2 SE), pure trend | 2.3 (Table 2.1), 5.2 A8 |
| 1d | environment/julia (Project.toml, Manifest.toml, setup_julia.jl), continuation/bk_smoke.jl, continuation/julia_io.py | test_julia_io (fixtures, no Julia needed) | 9.1, 5.2 A5, 7.1 K7, D23 |
| 1e | fresh-context subagent review of the whole MS1 diff against the plan (real gaps only); configs/replication.yaml; fill Commit/tag fields of DL-053 onward; user approves before the freeze | none | 7.1 (Table 7.1), 10.7 |

1d: read the BifurcationKit documentation first; every call comes from it; time-box one day (D23). If K7 is not reproduced, report; no fallback without the user's decision.

Not built at MS1: classes, A_ref, baseline rho, sensitivity (MS7); qif_network, test_qif_network, test_replication; NC1 to NC3 paths (MS9).

## Decisions taken (see the decision log for text)

- Test scope: every Table 10.1 fast test except test_qif_network and test_replication. test_runner is split over 1a-ii and 1b-ii; the RB9a assertion is in 1b-ii; test_surge_metrics is the class-free subset.
- K4 tail-fit fraction: 0.1, UNVERIFIED, confirmed by the user at 1e after a tail-cycle count for 0.05, 0.1 and 0.2 (read-only, from the section 3.1 linearisation). The fit also needs the definition of the initial jump (first peak deviation of r from r*) and the starting fixed point (K3 has three at I = 0); the user is asked for the start state.
- eta_H before A4 (DL-065, DL-067): `path.eta_H` is null until A4; eta_start and eta_peak are derived only from a non-null eta_H. Explicit values give status `provisional` (M3) or `explicit` (M2, for example S2 from A1). An unresolved path raises an error in a ramp run. `noise.sigma` is null until MS5 and mode N refuses to run with it null.
- Items 1 to 12 (DL-053 to DL-064): stable-root rule; ref_point precedence (explicit overrides win; DL-054, with its tau_d rule superseded by DL-066: explicit tau_d_ms in the D11 range 1 to 50 ms, warning outside {3, 4.95, 8}); run.kind values; dry-run record status; config_hash key set; wall-limit key; parameter-table format; ramp readings (logistic centre 0.5 is an unsourced choice); test-level tolerances; surge_metrics methods (the 2-SE test uses plain OLS standard errors on a smooth, autocorrelated envelope, to be revisited at MS7 (A8) before classifying noisy runs); new Julia files; Table 7.1 gaps.
- Seeds (DL-068, DL-069): the seed axis applies to every stochastic run.kind (mf_noisy; the network kinds when added at MS5); deterministic mf is one run with spawn_key null. Chosen: spawn_key = [seed_index], so the same seed gives the same stream in every sweep cell (common random numbers). The code at 7f48642 still uses [k] with k the position in the product list (independent streams); the change is in 1b-i.
- Skip-if-done matches on the config hash (any `*_<hash12>.json`, then the full SHA-256), not on the file index.
- K8 follows Table 7.1 (start from Devalle's Fig. 3 initial values).

## K1, K5, K7 operational definitions (DL-064)

- **K1** (approved): 20 r values uniform on the r-interval where the K1 formula point lies inside the A1 grid (computed from the formula at 1e). Pass: the grid edge where the positive-root count changes lies within one cell (0.05 in eta_bar, 0.1 in J) of the formula point.
- **K5** (open): no definition entered. The user checks the primary source before the freeze at 1e. If no usable definition exists, the user decides then, and a decision-log entry records the departure from G0 (which lists K5 as blocking).
- **K7** (UNVERIFIED, approved with one change): "decays" at 3 ms means max Re(lambda) below 0 (A4) and the G1 rule on the S3 run (the fit window starts at the first of the cycles counted in G, no amplitude threshold, because A_ref exists only from A5 at MS6), growth negative by more than 2 standard errors. "Holds within 2%" at 8 ms means the peak-to-peak v of each of the last 10 cycles (min_cycles) of the 10 s S3 run is within 2% of their mean. Reason for UNVERIFIED: it reuses D8, min_cycles and the S3 duration, none of which is sourced for K7.
