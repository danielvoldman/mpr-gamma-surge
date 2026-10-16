# MS4 gate report (M2 ramp diagnostic: S2, A3)

Binding source: `docs/plan.md` (Table 11.1 row MS4; 5.2 A3; 4.3 G1; 6.2 S2; D8). Decisions: DL-106 to DL-111. Numbers below are from `results/A3/a3_sn_ramp.parquet` and the saved S2 series (git-ignored), as in DL-110; S2 was not re-run for this report.

## A3 check (slowest ramp against one step)

"One step" = one A1 grid cell, d_eta_bar = 0.05 (DL-107 (a), UNVERIFIED reading). T_ramp 1000 s: eta_bar at the jump -3.132704, upper fold -3.136134, offset +0.003430 = 0.069 of a step. **Within one step: pass.** Against 0.025 (information only): 0.137 of that step, also within.

Offsets (eta_bar) for T_ramp 1, 1.78, 3.16, 5.62, 10, 17.8, 31.6, 56.2, 100, 178, 316, 562, 1000 s: 0.34575, 0.23495, 0.16037, 0.10906, 0.07437, 0.05048, 0.03449, 0.02344, 0.01595, 0.01086, 0.00740, 0.00504, 0.00343. Strictly falling as the ramp slows. Within 0.05 from 31.6 s (17.8 s is 0.0505, just outside).

## Fold cross-check

Formula `fold_etas(15, 1)`: lower -5.743527, upper -3.136134. Stored A1 grid (J = 15, cell 0.05): root count changes between -5.75 and -5.70 and between -3.15 and -3.10; the formula points lie inside both cells (0.0065 and 0.0139 from the nearer edge). Half-spacing lattice: edges -5.75/-5.725 and -3.15/-3.125, formula points inside. **Agreement within one cell at both folds: pass.** Valid for J = 15, Delta = 1 only.

## K5

Cited, not re-run, not redefined: "K5 bursting reproduced in S1" passed at MS2 (DL-088; DL-091, A0 table hash 724055e00481, spacing deviation 8.7e-13 tau against 0.1 tau). The K5 definition and tolerance are UNVERIFIED (DL-082).

## G1 metric and the move to M3 (DL-111)

Fit window from the jump sample, G band 25 to 100 Hz, threshold 0, first 10 cycles, damped if rate < -2 SE (D8). All 13 ramps: rate -24.3 to -25.7 /s, SE 0.29 to 0.57 /s (rate/SE -45 to -84), 10.00 to 10.11 cycles, **damped in all 13**. Full per-ramp table: DL-110. Sensitivity (window start shifted 2, 5, 10 ms): sign and damped call unchanged in all 13; rate/SE at least 21.6 in magnitude; rate moves up to about 16 percent.

By the plan's rule (4.3, D8) there is no non-damped episode on S2, so the project **moves from M2 to M3; M2 is kept as the damped-ring comparison** (owner ruling, DL-111; the plan's expected outcome, reasoned, not tested in the plan). Basis: one path (J = 15, Delta = 1, tau = 10 ms, I = 0, linear ramp), G1 judged on S2 alone (DL-107 (c)). Estimator caveats: DL-062 (plain OLS SE too small, damped declared too easily) and DL-073 (step-onset filter bias distorts rate magnitude, not the sign, in the case tried). The large margin does not make the SE values trustworthy as written.

## Wall times

S2 (13 ramps, 10 workers): 544 s in total (4a estimate: under 10 min, UNVERIFIED, met). Per run 13.3 s (T_ramp 1 s) to 526.9 s (1000 s, 8.8 min against the 12 to 13 min estimate). A3 analysis and the 4e check: seconds, not timed.

## Fresh-context review

A subagent that had not seen the work read `docs/ms4_plan.md`, DL-106 to DL-111, the parquet, `run_A3.py`, `check_A3_G1.py` and the plan wording. **Numbers: no mismatches** (offsets, G1 table, sensitivity ranges, walls, jump fractions, fold-grid edges and distances all recomputed and matching). The A3 check, the G1 call and the fold cross-check follow the plan's wording. Three wording points, handled as follows (DL-109 and DL-110 are committed and not edited; the corrections are stated here, and the DL-073 sentence in the not-yet-committed DL-111 was corrected):

1. Window start: DL-109 (c) says the fit window starts at the jump sample "as the plan says". The plan (4.3, SC-06) says it starts at the first of the cycles counted in G. The jump sample is our proxy, UNVERIFIED; nothing checks that those cycles are "in G", and the ring (about 92 Hz) is near the 100 Hz band edge.
2. The "up to about 15 percent" rate change in DL-110 is a window-start sensitivity (largest change about 16 percent, T_ramp 17.8 s), not a measure or bound of the DL-073 bias (about 45 percent in the earlier case). Shifted windows still contain a filter start-up. The sign result stands.
3. The damped call uses a fixed 10-cycle window after the jump only. Later cycles and other paths were not examined; "no non-damped episode" holds for that window on this path.

## Carried forward (still open)

- Jump definition (window 0.1 s, fraction 0.5, time convention): UNVERIFIED (DL-108, DL-109).
- G band (25 to 100 Hz) and output sampling (dt_out 1 ms): UNVERIFIED (DL-107 (b)); fit-window start is a proxy (review point 1).
- "One step" = 0.05: UNVERIFIED reading.
- K5 definition and tolerance: UNVERIFIED (DL-064, DL-082).
- DL-062 (SE) and DL-073 (step-onset bias): fix at MS7 (DL-083 (2)); strict xfail stays.
- Heun about 4x slowdown under load: carry into the MS5 network timing (DL-105).
- D36 24 h cap: unjudged until MS5.
- Paths P1 to P5 provisional until A4.
- Map 1 Delta spacing (linear, UNVERIFIED): decide at the MS8 plan; re-time map 1 if changed to log.

**MS4 gate: passed.** Reason: the A3 check passes (0.069 of one step, step reading UNVERIFIED), the fold cross-check passes, the G1 metric is evaluated (damped in 13 of 13, stable under window shifts) and the move to M3 is ruled (DL-111). The review found no numeric mismatch; three wording points are recorded above. Conditions: definitions marked UNVERIFIED stand as working definitions; no tag, no push.
