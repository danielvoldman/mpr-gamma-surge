# MS2 sub-step plan (rulings recorded 2026-10-15)

MS2 plan with the user's rulings on the open questions (DL-085). Binding source: `docs/plan.md` (Table 11.1, row MS2; sections 5.2 A1 and A2, Table 6.2 S1, Table 7.1, section 7.1 G0). Decisions are in `docs/decision_log.md` (DL-085 onward for MS2); this file holds none of its own and changes nothing in the plan. Rules: one sub-step at a time; after each, tests green (`.venv\Scripts\python.exe -m pytest -m "not slow"`), one commit `<type>(<scope>): <summary> [IDs]`, a report of at most 8 lines, then stop. No tags, no pushes unless asked. Use `.venv\Scripts\python.exe` for every Python command. Every run writes a provenance record (6.6). Drivers only integrate, analysis modules only analyse, figure scripts only plot (10.1).

MS2 is done when (Table 11.1): A0 rows K1, K2, K3, K4-MF and K5 pass. That is G0 part 1 (mean field only). Starting point: tag `tolerances-frozen` on bd301ce (DL-084); `configs/replication.yaml` is frozen, so no tolerance changes in MS2 without a decision-log entry (D34) and a report in the paper.

Not built at MS2: K4-net (MS5; non-blocking until a source gives the M2 network coupling, UNVERIFIED, 12.4); K6 (optional, not entered); K7 to K11 (MS3 to MS5); A3 (ramp through the saddle-node, not in the MS2 row); the figure FS1 (not in the MS2 row; ruled out of MS2, DL-085); `qif_network`.

## Sub-steps

| Step | Files | Tests (Table 10.1) | Plan sections |
|---|---|---|---|
| 2a (carry-overs) | tests/test_provenance.py or a new tests/test_replication_yaml.py (LF-hash); config.py and run.py wiring of `durations.baseline_s` and `model.J` / `model.eta_bar` versus `path.J0` (DL-077 item 2); K8/S3 start-state selector (deferred to MS5, DL-085; gate-report note only) | LF-hash test: `configs/replication.yaml` contains no CR byte and its SHA-256 equals 667d3b78...19a5 (DL-084); `provenance.sha256_file` of the file gives that value. test_config / test_runner: a ramp config with `t_on_s` different from `baseline_s`, or `J0` different from `model.J`, is rejected with a clear error (DL-085: reject; the keys stay in the hash); unchanged runs keep their hash | 6.6, 10.4, 10.3, 7.1 (D34); DL-077 (2), DL-079, DL-084 |
| 2b (A1) | analysis/bifurcation.py (`sn_curve_2d`, `focus_boundary_2d`, grid classification; analysis only, no integration), configs/A1.yaml, scripts/run_A1.py (writes results/A1/a1_fixedpoints_2d.npz and a run record) | test_fixed_points extension: the A1 grid has 241 x 201 base nodes on eta_bar/Delta in [-10, 2], J/sqrt(Delta) in [0, 20], Delta = 1; the refined region (DL-085: band of +-4 base cells in eta_bar along the formula fold curve over the whole J range, plus a box of +-10 base cells in eta_bar and J around the cusp; widths UNVERIFIED) has the half spacing (0.025, 0.05) and is nested in the base grid; the Table 6.2 halving check (boundary shift in cells, base versus half spacing) is stored as a field along the fold and at the cusp, with no pass/fail test; K3 point gives exactly focus, node, saddle; K2 discriminant sign change within one cell (0.05, 0.1) of eta_f(J) on a reduced grid; the C9 record (node region exists for Delta > 0, yes or no) is a field of the npz | 5.2 A1, 3.1, Table 7.1 K1 to K3, Table 6.2 resolution note (D31), 4.4 |
| 2c (S1 runs) | configs/S1.yaml; the M2 forcing paths for K4 (step I = 0 to 3 at t = 0) and K5 (I(t) = 3 sin(pi t / 20) from t = 0) in ramps.py and config.py (DL-085: new optional kinds `I_step` and `I_sin`); run through run.py with `run_mf` (DOP853, rtol per base.yaml); output results/S1/ | test_ramps: the step and sinusoid I(t) values (I = 0 before the step, I = 3 after; sin at t = 0, 10, 20, 40); test_runner or test_simulate_mf: an S1 config runs to completion with a record, from the low-rate stable node (r = 0.0811, v = -1.962) as start state; test_k5_definition stays and is reused on the runner output | 6.5 (Table 6.2 S1), 6.2, 3.1, Table 7.1 K4 and K5, DL-079, DL-082 |
| 2d (A2) | analysis/ring.py (in analysis/ring.py, DL-085): damped-sinusoid fit to the tail of the K4 step response, linearisation frequency and decay at the post-step focus, ring map over the stable-focus branch of A1 (frequency in Hz, decay rate, cycles per e-fold, G1 by envelope growth per D8); scripts/run_A2.py; results/A2/a2_ring_map.npz | synthetic damped sinusoid with known frequency and decay recovered within 2% (fit routine); the linearisation of the K4 point gives lambda = -0.2318 +/- 5.7664i (DL-076, reasoned from 3.1); the tail starts where the envelope falls below 0.1 of the initial jump (first peak deviation of r from r*, DL-079); G1 on the M2 ring uses envelope growth, not A_min (CP17) | 5.2 A2, Table 7.1 K4-MF, 2.3, 4.3 G1, D8, D34 |
| 2e (A0 and gate) | scripts/run_A0.py (evaluates K1 to K5 from A1, A2, S1 outputs against configs/replication.yaml, writes results/A0/a0_replication.csv, and records the SHA-256 of the yaml, LF text); tests/test_replication.py (slow): K1 to K5 on reduced grids | test_replication (slow): K1 (20 r values, all pass at half spacing near the fold, DL-081), K2, K3, K4-MF (frequency and decay within 2%), K5 (DL-082); the csv has one row per K with value, tolerance, pass; criteria_sha256 in the record equals the frozen hash. Full suite run (including slow) before the gate | 7.1, Table 7.1, G0 part 1, 10.4, 10.5 |
| 2f (review and gate report) | fresh-context subagent review of the MS2 diff against the plan (real gaps only); fill the Commit/tag field of the MS2 decision-log entries; the gate report | none | Table 11.1 MS2, 7.1 G0 |

2e needs 2b, 2c and 2d first. 2b and 2c are independent of each other.

## Carry-overs from MS1

| Item | Source | Handling in MS2 |
|---|---|---|
| LF-hash test for replication.yaml | DL-084 | 2a; a test that pins the frozen SHA-256 on the LF text and fails on a CRLF working copy. It fails by design if the tolerances change, which needs a new decision-log entry. |
| K8/S3 start-state selector | DL-071 item 7 (deferred to MS2 "when the S3 config is written") | Deferred to MS5 (DL-085). Table 7.1 K8 follows Devalle's Fig. 3 initial values. The gate report carries a one-line note. |
| `durations.baseline_s` wiring and `model.J` / `model.eta_bar` versus `path.J0` | DL-077 (2) | 2a; today these enter the config hash but not the integration (a different hash for an identical run). |
| A1 half spacing near the cusp | DL-081, DL-083 (1) | 2b; base grid as in 5.2 A1 elsewhere, half spacing (0.025 in eta_bar/Delta, 0.05 in J/sqrt(Delta)) near the fold curve and the cusp (r = (3/(4 pi^4))^(1/4) = 0.2965). Extent ruled in DL-085: a band of +-4 base cells in eta_bar along the whole formula fold curve plus a box of +-10 base cells in eta_bar and J around the cusp (widths UNVERIFIED, the user's); the halving check is recorded, not tested. |
| DL-073 filter-bias fix | DL-083 (2) | Deferred to MS7; its strict xfail stays. Not touched. |
| find_complete ProvenanceError in a pool sweep | DL-077 (4) | Known and accepted, not wired in MS2. |
| K5 and K4 sources | DL-079, DL-082 | K5 definition and K4 start state are fixed and UNVERIFIED as marked; MS2 uses them as written. |

## Rulings (DL-085, 2026-10-15)

No open questions remain.

- **A1 refinement:** half spacing (0.025 in eta_bar/Delta, 0.05 in J/sqrt(Delta)) in a band of +-4 base cells in eta_bar along the whole formula fold curve, plus a box of +-10 base cells in eta_bar and J around the cusp. The widths are UNVERIFIED (the user's). A1 stores the Table 6.2 halving check (boundary shift in cells) along the fold and at the cusp as a recorded field; there is no pass/fail test on it.
- **K8/S3 start-state selector:** deferred to MS5; the gate report carries a one-line note.
- **Inconsistent configs:** rejected (`path.t_on_s` not equal to `durations.baseline_s`, or `path.J0` not equal to `model.J`). The keys stay in the hash.
- **S1 paths:** new path kinds `I_step` and `I_sin`, with optional keys so existing config hashes are unchanged.
- **G0 part 1 on failure:** as in Table 11.2, with no tolerance change.
- **FS1:** not at MS2.
- **A2 fit module:** `analysis/ring.py` (new file), listed in the layout notes.
- **UNVERIFIED values:** K4 tail fraction 0.1, the K5 burst midpoint and 0.1 tau tolerance, and the tau mapping are used as written. Results that depend on them are labelled UNVERIFIED in the record and the gate report.
