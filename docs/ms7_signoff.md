# MS7 sign-off sheet (7h): items that need the owner's ruling

Draft, not frozen. Written in 7h (DL-156). Nothing on this sheet is ruled; every "Recommendation" is the author's one-line suggestion, marked ours. The draft criteria file is `configs/robustness_criteria.yaml` (each value labelled logged, UNVERIFIED or open; `sheet:` names the row here). No freeze SHA-256 exists and no tag was created. Plan v0.5 is not edited. D8: ruling for MS7 is option A (plan estimator stays), recorded below with the choice A or B left to you.

Row format: ID, what it is, options, recommendation (ours), evidence. IDs F-n and O-n are from `docs/ms7_plan.md` and DL-140; H-n, D8, Q3, SW, RHO, REACH, G6, RB6 and U-n are added here.

## 1. D8 and the estimator

| ID | What | Options | Recommendation (ours) | Evidence |
|---|---|---|---|---|
| D8 | Damped / non-damped estimator for MS7 | **A** plan estimator stays default, strict xfail stays, failures stated as a known limitation in the criteria draft (already written). **B** staged change: zero-pad edge treatment plus an autocorrelation-aware SE, no shift or a 40 ms shift, no minimum window (data in 1.1 below); needs your ruling on the SE and on any fit-start change, then one re-run of the study and of the A8 sensitivity (about 45 s) | **A.** B as extracted meets neither pre-registered number and trades failures (1.1); no candidate in the 54 meets both | DL-137, DL-140, DL-147, DL-155 |
| Q3 | Plan question, not acted on: fast-damped rings (about -25 per s) are already classed NS by the 10-cycle count, so a D8 envelope-fit gate may not be the right gate for them. The D8 fit is the only thing that separates a slowly damped ring (more than 10 cycles above threshold) from a surge, and that is where every candidate struggles | (a) leave Table 2.1 as written; (b) change the plan wording so the D8 test applies only to rings that pass the cycle count and states its own tolerance; (c) replace the D8 fit by a different gate (for example a fit on the unfiltered analytic signal, DL-073 (c), not tested) | Your plan question; ours: (a) for MS7, (b) or (c) to be considered after MS8 data exist | DL-155 (5), DL-153 (options not tested) |
| X-1 | The strict xfail `test_slowly_damped_ring_rate_matches_true_decay_after_step_onset` and the gate wording "test_surge_metrics passes" | (a) xfail stays; the gate reads "pytest exits 0 with the documented xfail"; (b) retire the test by ruling with a DL entry; (c) fix the estimator first (B) | (a), consistent with D8 = A | DL-073, DL-137, DL-155 |

### 1.1 Option B data, from the existing 54-candidate table (no new run)

Source: `results/A8/d8_cand/` (d8cand_summary.csv, d8cand_cells.csv, d8cand_lc.csv, d8cand_a8.csv, d8cand_whitenoise.csv; run D8CAND_0000_047a4881d01d, DL-155). Rows below are zero-pad edge treatment with the AR(1) SE (B1 = no shift, B2 = 40 ms shift) and, for completeness, the per-cycle SE (B1c, B2c); no minimum window (M0). The plan row is the reference (A). The extraction was a read of the saved csv files; nothing was integrated or re-run. Candidate ids: plan `En-S0-M0-plain`, B1 `Ez-S0-M0-ar1`, B2 `Ez-S1-M0-ar1`, B1c `Ez-S0-M0-cycle`, B2c `Ez-S1-M0-cycle`. For reference, the study's best-ranked candidate (zero-pad, 80 ms, 5-cycle minimum window, AR(1)) is `Ez-S2-M5-ar1`.

**Pre-registered acceptance (DL-136, unchanged)**

| Item | Plan (A) | B1 | B2 | B1c | B2c | Best-ranked (ref.) |
|---|---|---|---|---|---|---|
| (i) F1 cells below 95 percent sign match, of 36 | 26 | 10 | 8 | 14 | 8 | 6 |
| (i) met | no | no | no | no | no | no |
| (ii) zero-growth cells above 5 percent false damped, of 5 | 5 | 1 | 1 | 0 | 3 | 0 |
| (ii) largest false-damped rate | 0.545 | 0.175 | 0.295 | 0.030 | 0.180 | 0.040 |
| (ii) met | no | no | no | yes | no | yes |
| Both met | no | no | no | no | no | no |
| False non-damped, mean (reported) | 0.454 | 0.490 | 0.255 | 0.564 | 0.255 | 0.155 |
| Inflation factor k, maximum (reported) | 619 | 4.4 | 18.4 | 8.8 | 6.3 | 2.5 |

The F1 cells that still fail for B1 (11 lines, 10 ring cells plus the AR(2) zero cell) are the damped step-onset rings at -25, -12, -6, -3 and -2 per s at both noise levels (0 to 8.5 percent match for -2 per s, 0 for the rest; bias +48.6 per s at -25). For B2 the failures are -25 and -12 per s (match 0 at both noises), -3 and -2 per s (59 to 87 percent), and the AR(2) zero cell (false damped 0.295). The -25 per s ring fails because the fit starts inside the filter transient; the shift of 40 ms repairs -6 per s but not -12 or -25.

**Other F-families**

| Item | Plan (A) | B1 | B2 | B1c | B2c |
|---|---|---|---|---|---|
| F2 gradual onset, (i) cells failing, of 40 (ramp 0.1 s / 0.5 s) | 35 (17 / 18) | 20 (10 / 10) | 10 (2 / 8) | 20 (10 / 10) | 10 (2 / 8) |
| F2 (ii) cells failing | 4 | 0 | 0 | 0 | 0 |
| F3 (DL-140 finding 1, sustained burst to record end): false damped | 34.5 percent | 0 | 0 | 0 | 0 |

**Stored limit-cycle items (F4: the S3 ref_devalle limit cycle must be non-damped)**

| Item | Plan (A) | B1 | B2 | B1c | B2c |
|---|---|---|---|---|---|
| t_on = 0 s damped | no (rate -0.23 +/- 0.29) | no (-0.24 +/- 1.98) | no (+0.09 +/- 2.08) | no (-0.14 +/- 0.16) | no (-0.14 +/- 0.09) |
| t_on = 1 s damped | **yes** (-0.54 +/- 0.24, 2.2 SE) | no (+0.03 +/- 2.14) | no (+0.25 +/- 2.17) | no (+0.70 +/- 0.39) | no (-0.15 +/- 0.15) |
| t_on = 3 s damped | no (+0.16 +/- 0.28) | no (+0.58 +/- 1.94) | no (-0.27 +/- 2.13) | no (+2.27 +/- 1.30) | no (+0.03 +/- 0.06) |
| Damped at t_on 0 to 4 s, step 0.25 s (reported, 17 values) | 2 | 0 | 0 | 0 | 0 |

**A8 ring items (8 items: 5-cycle ring growth negative; 15-cycle slowly damped ring damped in at least 95 percent; four mode-N and two mode-D ring cases classified NS or D-none)**

| Item | Plan (A) | B1 | B2 | B1c | B2c |
|---|---|---|---|---|---|
| Items failed, of 8 | 2 | 4 | 3 | 4 | 3 |
| 5-cycle ring: growth negative | 100 percent, pass | 100 percent, pass | 100 percent, pass | 100 percent, pass | 100 percent, pass |
| 15-cycle slowly damped ring called damped (needs 95 percent) | 86.5 percent, **fail** | 37.0 percent, **fail** | 86.5 percent, **fail** | 0.0 percent, **fail** | 86.5 percent, **fail** |
| 15-cycle ring: fitted rate within 10 percent of true -6.14 (the xfail criterion; reported) | 0.5 percent | 0.5 percent | 86.5 percent | 0.0 percent | 86.5 percent |
| D_ring_fast_-25 (mode D, T 120 s): D-none | pass | pass | pass | pass | pass |
| D_ring_slow_-3 (mode D, T 120 s): NS or D-none | **fail** (D-tr) | **fail** | pass | **fail** | pass |
| N_ring_slow_-3 (mode N, T 120 and 3 s) | pass, pass | pass, pass | pass, pass | pass, pass | pass, pass |
| N_ring_fast_-25 (mode N, T 120 and 3 s) | pass, pass | **fail, fail** (becomes a surge class) | **fail, fail** | **fail, fail** | **fail, fail** |

The two-item failure of the plan row is the 15-cycle ring item and D_ring_slow_-3 (DL-147 (3)). B1 and B2 both lose the two N_ring_fast_-25 items (the class becomes a surge class instead of NS, DL-155); B2 also repairs D_ring_slow_-3. The cause of the N_ring_fast_-25 change was not examined in 7h.

**White-noise rates (class level, non-NS of 500 per window; mode N, t_on 5 s; all five candidates are identical at sd 0.04, where the band envelope never reaches the threshold and D8 is not called)**

| Noise sd | W = 0.2 s | 0.333 s | 0.593 s | 1.054 s | 1.874 s | 2 s |
|---|---|---|---|---|---|---|
| 0.04, every candidate | 306 | 400 | 172 | 26 | 2 | 0 |
| 0.20, plan (A) | 285 | 374 | 161 | 23 | 1 | 0 |
| 0.20, B1 / B2 / B1c / B2c | 306 / 306 / 306 / 306 | 399 / 400 / 400 / 400 | 171 / 172 / 172 / 172 | 26 / 26 / 26 / 26 | 2 / 2 / 2 / 2 | 0 |
| 0.45, plan (A) | 205 | 267 | 115 | 16 | 1 | 0 |
| 0.45, B1 | 294 | 379 | 162 | 23 | 2 | 0 |
| 0.45, B2 | 304 | 395 | 169 | 26 | 2 | 0 |
| 0.45, B1c / B2c | 306 | 400 | 172 | 26 | 2 | 0 |

D8 "damped" calls on the noise at sd 0.45 (of 500; W = 0.2, 0.333, 0.593, 1.054, 1.874, 2 s): plan 101, 133, 57, 10, 1, 0; B1 12, 21, 10, 3, 0, 0; B2 2, 5, 3, 0, 0, 0; B1c and B2c 0. The plan estimator lowers the false-surge count at short W by calling noise damped, which is accidental filtering from a too-small SE. A better SE removes that, and the counts return to the sd 0.04 values. No candidate lowers the rate set by the power tests and the 10-cycle rule (row SW).

Reading for the choice (ours, UNVERIFIED): B1 and B2 fix finding 1 (F3), the stored limit cycle at t_on = 1 s, and the SE inflation, but they miss (i) in 10 and 8 of 36 cells, miss (ii) in one cell, and fail 4 and 3 of 8 A8 ring items against 2 for the plan estimator. B2 changes "from the threshold crossing" in Table 2.1 and so needs your ruling; B1 changes only "standard errors of the fit" and the Hilbert edge treatment. On the xfail criterion (fitted rate within 10 percent of the true -6.14) B1 is within it in 0.5 percent of draws and B2 in 86.5 percent; the xfail test itself was not run against a candidate.

## 2. Short-window false surge (O4 and O5 with the white-noise finding)

| ID | What | Options | Recommendation (ours) | Evidence |
|---|---|---|---|---|
| SW | **Short-window false-surge finding.** On seeded white noise (sd 0.04, mode N, plan classifier, D8 never called) 306 of 500 records are non-NS at W = 0.2 s (T_ramp 1 to 5.6 s), 400 of 500 at 0.333 s, 172 at 0.593 s, 26 (24 in DL-147) at 1.054 s, 2 at 1.874 s, 0 at 2 s. It comes from the power tests on a 0.2 s PSD estimate and from the 10-cycle rule, which passes after one or two flagged windows (duration x f_pk), not from D8. Factors 4 give 1 of 500 and minimum cycles 20 give 112 of 500 at W = 0.2 s; white noise has no resonance, so this is the rate of the class logic and not a prediction for M3 noise; the rate on real M3 baselines at short W was not measured (options A to C of DL-144 were withdrawn) | (a) report only, label cells with T_ramp <= 6 s (W = 0.2 s) and 0.333 s as short-window in every result, no threshold change; (b) require a minimum number of flagged windows or a minimum duration in seconds at short W (a new rule); (c) raise the factors or the minimum cycles at short W (changes D6 or D8 for those cells; needs a DL entry); (d) do not classify mode N below a given T_ramp | (a) now; the real rate is measured on M3 baselines by NC1 at MS9 (G7) and any change after the freeze costs a DL entry and a paper statement. Note that 8 of the 13 map-2 T_ramp have W < 2 s (4 of them W = 0.2 s) | DL-140 finding 4, DL-147 (3)(6), DL-155 (4) |
| O4 | Mode-N amplitude threshold: the D8 fit uses the single 0.1 x A_ref; the mode-N 10-cycle count uses none. The baseline noise envelope reaches 0.217622 in 460 of 12,260 records (3.8 percent, 125 map-1 cells at Delta >= 0.13; never at the headline, in map 2 or in the 56 nodes); 31 records in 8 cells (Delta 0.32 to 0.58, tau_d 25 to 50 ms) have a 10-cycle run above it. Under A_min 0.05 the envelope crosses in 51 percent of records (867 cells) | (a) keep as coded; (b) a baseline-relative envelope level for the mode-N count (a new threshold); (c) report the 8 cells as noise-prone and leave the classifier unchanged | (a), plus (c) in the reporting of the maps | DL-140 O4, DL-145, DL-147 (4) |
| O5 | Cycle count: mode N = duration x mean f_pk over the episode windows; mode D = unwrapped analytic phase / 2 pi | (a) as coded; (b) phase-based count in mode N; (c) integral of f_pk | (a), but note that at short W it is what passes the 10-cycle rule on noise (row SW) | DL-140 O5, DL-147 (6) |

## 3. Classifier definitions O1 to O16 (DL-140)

The code uses the plain reading named below, marked "working convention, UNVERIFIED". Only O1 is a switch (`Conventions.onset`). Rulings that change the code are done after your answer, not before.

| ID | What | Options | Recommendation (ours) | Evidence |
|---|---|---|---|---|
| O1 | Mode-N onset time | window centre of the first flagged window (used); window start | centre | DL-140 O1 |
| O2 | Episode end, duration and gap merging (gap = unflagged windows x step, merged if < W; end = last flagged centre + step/2; duration = flagged windows x step) | as used; gap measured from window span to window span | as used | DL-140 O2 |
| O3 | Termination at the record end (sustained if no gap of W or more follows before the record ends) | as used; any unflagged final window terminates | as used (consistent with the merge rule) | DL-140 O3 |
| O4 | Mode-N amplitude threshold | see section 2 | keep as coded | DL-140, DL-145, DL-147 |
| O5 | Cycle count | see section 2 | as coded | DL-140, DL-147 |
| O6 | Peak frequency (argmax of the PSD in G, resolution 1/W) | as used; parabolic interpolation | as used (the A8 check is within 1/W) | DL-140 O6 |
| O7 | Baseline value statistic (mean over windows wholly inside the last 5 s of P_G/P_non-G and P_G) | mean; median; ratio of means | mean | DL-140 O7 |
| O8 | Tested windows | centre >= t_on (used); start >= t_on (no baseline overlap, onset later by W/2) | as used (centre >= t_on): keeps the onset convention of O1 and the RB1 "within one step" test; your call, DL-140 left it open | DL-140 O8 |
| O9 | D8 scope: one call per record on v from t_on; damped means no episode (NS or D-none) | as used; per episode on the episode segment | as used under D8 = A | DL-140 O9, DL-137 |
| O10 | Which episode defines the class; S+ without an overlap requirement | as used (first qualifying episode; S+ if both tests qualify anywhere); require time overlap for S+; longest episode | require overlap for S+ (DL-140's own recommendation; needs a code change and tests after your ruling) | DL-140 O10 |
| O11 (= F-6) | S-abs "broadband" flag (CP26: no new threshold). **Not implemented** | (a) flag when the spectrogram argmax of the rise lies outside G (a location test, no new number); (b) spectral flatness (needs a number); (c) no flag | (a), implemented only after your ruling | DL-140 O11, F-6 |
| O12 | Post-surge rate (the statistic after J_exit,run is not defined in the plan). **Not implemented** | (a) mean r over [J_exit,run, end]; (b) r over the last second; (c) none | (a), after your ruling; or (c) if you prefer to define it at MS8 with data | DL-140 O12 |
| O13 | Baseline r for the collapse marker (mean of r over the baseline; marker = first sample with r < 10 percent of it, no smoothing) | as used; median; with a minimum duration | as used | DL-140 O13 |
| O14 | Sign of the exit delay | J_exit,run minus J_exit,static (used); the reverse | as used | DL-140 O14 |
| O15 | Label (f): A4-region membership supplied by the caller | as used; computed in the classifier | as used | DL-140 O15 |
| O16 | Edge handling: none in the classifier, the caller discards transients | as used; edge trimming inside the classifier | as used under D8 = A (an edge pad is part of option B) | DL-140 O16 |

## 4. Values and readings

| ID | What | Options | Recommendation (ours) | Evidence |
|---|---|---|---|---|
| H-1 | **A_ref reading.** 2.176222 (median of the band-passed Hilbert envelope over whole cycles of the stored S3 ref_devalle record, first and last 1 s dropped); threshold 0.217622. Alternates stored, not used, not run as a sensitivity item: mean 2.186789, maximum 3.219102, sqrt(2) x RMS 2.404543, half peak-to-peak 2.755908, literal peak-to-peak 5.511356 | (a) confirm (a); (b) run the alternates as an A8 sensitivity item (not in the plan's A8 list or DL-136 D-3); (c) another reading | (a). The threshold from the alternates would be 0.2187, 0.3219, 0.2405, 0.2756, 0.5511; the A_min 0.05 and 0.2 variants already span 0.109 to 0.435 | DL-138, DL-139, DL-146, DL-147; open item 7 |
| F-7 | Baseline rho of 0.5 or more: rho reported, surge test on the odds (unbounded); no flag, no class | confirm; or add a flag | confirm. Fraction measured: 67.5 percent of records and 66.0 percent of cells at rho >= 0.5; headline 0.68; 56 stable nodes median 0.454 (12.5 percent of records >= 0.5) | DL-145 |
| RHO | Baseline rho depends on W for the same state (W = 0.2 s median 0.754, W = 2 s 0.588): is "baseline rho" per D4 window acceptable for the criteria file | (a) accept; (b) report at W = 2 s only | (a), reported per W | DL-145, DL-147 (5) |
| REACH | Reachability finding: the plan's sentence "a rho ratio cannot reach 2 when baseline rho >= 0.5" is the only point in the plan (ratio 2, level 0.5). The levels 1/ratio at 1.5 and 4 (0.667, 0.25) are our arithmetic, and the instruction's 1 - 1/ratio forms (0.333 at 1.5, 0.75 at 4) do not follow one formula. Share of cells at or above each level per W is in `a8_reachability.csv` (at 0.5: 100 percent at W 0.2 s, 60.0 percent at W 2 s; at 0.667: 76 and 43.3 percent). The surge test is on odds, so a level reached does not mean a surge is unreachable | (a) use only the plan's 0.5 at ratio 2 for reporting; (b) also report 1/ratio at 1.5 and 4; (c) drop the sentence from the criteria | (a); (b) as information in the appendix | DL-146, DL-147 (5), F-7 |
| G6 | G6 reading: the headline (120 s) is outside the RB3(a) range (I_min about -9.4 per second of T_ramp, e^-1122 of delta_0 at 120 s), so the RB3(a) clause is "not judged at the headline"; G6 at the headline rests on RB3(b) and RB6; RB3(a) is reported with its coverage (0 to 2 of 13 T_ramp per path and profile; none at the headline; P2 sigmoid has no predicted onset) | (a) accept this reading; (b) change the gate or the headline so RB3(a) applies at the headline (a plan change, outside MS7); (c) report RB3(a) at T_ramp 1 and 1.78 s only | (a). Reasoned arithmetic until MS8 | DL-149 (2)(3), DL-151, DL-152 |
| RB6 | RB6 statistic: median delay over 10 seeds at 1e-3 tau against the median over the same seeds at 1e-4 tau, coupled increments, relative change < 5 percent (DL-154). Readings of ours, not ruled: relative to the default-step median; delay = eta at onset minus eta_H; a seed with no onset is reported and left out of the median with its count; made on the MS8 headline subset | confirm; or change any reading | confirm | DL-152, DL-154 |
| F-26 | G5 "3 percent of map-1 cells": which mode counts | mode D map 1 (default); noisy subgrid separate; or mode N | mode D map 1 | ms7_plan F-26 |
| F-12 | RB3(a) range rule as written; the one-grid-step tolerance (0.857 s at the headline, 7.1 s at T_ramp 1000 s) is frozen without ramp evidence; the first test is RB3(a) at MS8 | confirm | confirm | DL-149 (4), F-12 |
| F-9 | sigma = 0.0624 frozen with the criteria while UNVERIFIED until S8 at MS10 | confirm freezing; a later change by DL entry | confirm | DL-121, F-9 |
| F-8 | D-items D3, D4, D5, D6, D8, D9 and the other classifier defaults at the plan values (draft file section `classifier`) | confirm all | confirm | ms7_plan F-8 |
| F-2 | A_min factor 0.1 x A_ref, one absolute threshold for every cell and path | confirm | confirm | D7, CP18 |
| F-10, F-11, F-13, F-14, F-15 | D43 levels, solver floor, A4 step, Heun ladder, RB3(b) form: entered as ruled in DL-152, all UNVERIFIED | confirm the entries in the draft file | confirm | DL-152 |
| F-27, F-28 | Baseline cell lists and storage (UNVERIFIED working grids: Delta linear 0.01 to 0.6, tau_d log 1 to 50 ms, J0 linear -40 to -5; per-cell bundle; seeds [7, 4, s]); these become the MS9 map grid | confirm; or change any axis (needs a re-run of 7d to 7f) | confirm | DL-136 D-4, DL-141, DL-143 |
| S3S4 | Conventions of the stored-record sensitivity (S3 records 2 to 8 s with t_on 1 s; each S4 hold with t_on at its start; window x 2 does not fit the 2 s devalle holds: not_run in 71) are ours, UNVERIFIED | accept as a pre-freeze sensitivity only; or re-define | accept (the real RB10 is evaluated by A11 on ramp records) | DL-146, DL-147 (2) |

## 5. Table 7.2 and gate rows to confirm or rule (F-16 to F-26)

| ID | What is open | Options | Recommendation (ours) | Evidence |
|---|---|---|---|---|
| F-16 (RB1) | **MUST.** "N = 3e4 no worse than 1e4": which metric; f_pk reference (per seed or the mean); network v is the mean V of non-refractory neurons, not the mean-field v | metric: class agreement count, or |f_pk error| and onset error not larger; reference: per seed, or the 3-seed mean | metric: class agreement and the onset and f_pk errors each not larger; reference: per seed | DL-129, F-16 |
| F-17 (RB2) | "Kept" = same class as the headline mode-D class under the correspondence; no pass rule at 2 sigma | confirm | confirm | F-17 |
| F-18 (RB3) | (c) "holds" = same class as the headline; (d) which of the 4 T_ramp are compared | (d): the 4 of (c), or all 13 | (d) the four of (c) | F-18 |
| F-19 (RB4) | Latin hypercube seed and box (plus or minus 10 percent, reasoned, not tested); "class unchanged" per run | confirm; seed from root_seed 20261008 | confirm | F-19 |
| F-20 (RB5) | none | confirm | confirm | F-20 |
| F-21 (RB6) | Solver pair list (DOP853 vs Radau); which dt for the network f_pk test | pair as written; network dt 1e-3 against 5e-4 | confirm; dt 1e-3 against 5e-4 | F-21 |
| F-22 (RB7) | none (G7) | confirm | confirm | F-22 |
| F-23 (RB8) | M4 criteria not written now (D42 open, G2 does not trigger) | confirm deferral | confirm | DL-133, F-23 |
| F-24 (RB9) | none | confirm | confirm | F-24 |
| F-25 (RB10) | Variation list: band 30 to 120; factors 1.5 and 4; A_min 0.05 and 0.2; window x 0.5 and x 2; cycles 5 and 20 | confirm | confirm | F-25 |

## 6. A8 items from the plan that are still unmeasured, and the other UNVERIFIED values

| ID | What | Options | Recommendation (ours) | Evidence |
|---|---|---|---|---|
| U-1 | A8 sensitivity as the plan states it for RB10 ("headline class unchanged; at most 10 percent of map cells change class") and RB9(c)/D2 (5 percent): needs M3 ramp-run classes; not measurable before the freeze. Measured instead on synthetic and stored mode-D records, with no acceptance number applied | accept that these are evaluated by A11 after the freeze | accept | DL-146, DL-147 |
| U-2 | A8 requirements not met by the plan classifier on the synthetic set: slowly damped ring must be NS or D-none (mode D gives D-tr; mode N passes); pure trend must be NS (mode N at W = 0.2 s gives S-rel; mode D gives D-none, mode N at W = 2 s gives NS) | report as known limitations with D8 = A | report | DL-147 (3) |
| U-3 | Real-baseline false-surge rate at short W on M3 noise: not measured (DL-144 options A to C were withdrawn; white noise has no resonance). The classifier is unvalidated on this point until NC1 | accept; or set an MS8-time check | accept; NC1 and G7 are the plan's check | DL-144, DL-147, row SW |
| U-4 | A8 sensitivity repeated on a final estimator: needed only if D8 = B | none under A | none under A | DL-147 |
| U-5 | The plan's A8 test list also names a zero-baseline case and a P_G/P_non-G threshold test; I did not check each against `tests/test_surge_classes.py` by name in 7h | check in 7i | check in 7i | docs/plan.md A8 |
| U-6 | Every UNVERIFIED value in the draft file (A_ref 2.176222, sigma 0.0624, sigma_floor levels 1.59e-9 / 1.59e-6 / 1.59e-3, solver floor 6.66e-16, A4 step 0.025, Heun ladder, RB3(b) form, cell grids, seeds, headline t_pred 115.22 s, coverage 0 to 2 of 13, RB6 statistic) stays labelled UNVERIFIED at the freeze | confirm that "frozen" means frozen with the label | confirm | `configs/robustness_criteria.yaml` |
| U-7 | A discrepancy between two logged tables, not resolved: DL-147 gives 24 non-NS of 500 at W = 1.054 s (S-rel 22, S-sus 2); the D8 study (DL-155, which says it reproduced DL-147) gives 26 (S-rel 23, S-sus 3). All other windows agree. No re-run was made in 7h | (a) leave both and note it; (b) investigate in a recorded diagnostic run | (a) now; (b) before 7i if the white-noise table is cited in the paper | DL-147 (6), DL-155 (4) |

## 7. Housekeeping and open items

| ID | What | Options | Recommendation (ours) | Evidence |
|---|---|---|---|---|
| H-2 | Plan row 7h says to repoint `robustness.criteria_file` in `configs/A4.yaml` and `S5.yaml`. `run_a4` reads K-tolerances from that file (`analysis/hopf.py`, `evaluate_a4`), so pointing A4 at `robustness_criteria.yaml` would break it; `S5.yaml` has no such key (it inherits null from `base.yaml`). Not done in 7h | (a) leave A4 on `replication.yaml`, set the key on the ramp-run configs (S5 ramp onward) at MS8 when a run reads it; (b) split A4's two uses; (c) repoint now and change `run_a4` | (a) | `hopf.py:370`, `provenance.py:169` |
| H-3 | A loader for the criteria file in `config.py` (plan row 7h) and "hash enters the provenance record": the record already hashes `robustness.criteria_file` when set (`provenance.py`). No loader written in 7h; the test reads the YAML directly | (a) write a loader at 7h after rulings; (b) at MS8 when the first run reads it | (b) | ms7_plan 7h row |
| H-4 | `docs/robustness_criteria.md` appears in the plan's layout tree; not written | (a) produce it from this sheet at 7i; (b) this sheet is the companion; (c) skip | (a) at 7i | plan layout (Appendix) |
| K5 | K5 definition (own reading, UNVERIFIED, passed at MS2, cited, not re-run; re-running touches the frozen `replication.yaml`) | keep deferred; request a definition or source check | keep deferred | DL-064, DL-082, ms7_plan item 1 |
| K10 | Not reproduced as worded (J dependence 13 to 42 percent at 8 / 20 / 40 ms); definition kept, single-source claim UNVERIFIED, non-blocking | carry; or revise the definition by ruling | carry | DL-131 to DL-134, `docs/ms6_gate_report.md` |
| K4-net | M2 network coupling unsourced (MC-03); non-blocking until a source gives it | carry | carry | plan Appendix G (MC-03), ms7_plan item 6 |
| DEF | Defender exclusion for the repository, `.venv` and `results/`: status unknown; needs admin to read; affects wall times in any timing figure | you say yes or no; or leave unknown and state it in timing figures | tell me | plan 9.1, ms7_plan item 3 |
| BAK | Private remote backup: none exists; `results/` is git-ignored; tags are local only | yes or no, ideally before 7j | yes (private) before 7j; I will not create one unprompted | ms7_plan item 4 |
| CAP | D36 24 h cap: rows without timing cells (S1, S3 mean field, A1 to A6, S4, S12 MF, S13 ladders, network dt ladder, A8, baseline analysis, F11 hold run 88 s); bounds 8.60 h lower and 10.23 h conservative stay; two DL-105 exceptions carried | accept; or build the missing timing cells | accept; fold measured times into the next timing summary | DL-122, ms7_plan item 5 |
| PERM | `/permissions` check (DL-051): not recorded since MS3; MS7 adds no new external command | run `/permissions` once and tell me whether the venv-path rules match without a prompt; or drop the item | tell me | DL-051, ms7_plan item 2 |
| TAG | Tag mechanics for 7j: full suite (including slow) green, `criteria-frozen` annotated on the approved commit with the SHA-256 of the LF text of `configs/robustness_criteria.yaml` (DL-084), approval DL entry in the same commit; no push | confirm | confirm | ms7_plan 7j |
