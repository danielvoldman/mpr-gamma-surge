# MS11 evidence sheet (11g)

Written for: the reviewer. Every number is read from `results/A11/a11_robustness.csv` and `results/A11/a11_evaluators.json` (A11, run once at 11f), from `results/A11/independent/` (the independent recomputation, run once at 11g) or from `results/A11/post_hoc_9b_look/` (post hoc, exploratory, read only, feeds no gate). Nothing here changes a frozen rule or an A11 output.

## 1. Result in one paragraph

The independent recomputation (`scripts/ms11_independent_check.py`, written from `docs/ms11_eval_rules.md` and the plan text, not from `run_A11.py`, `ms11_eval.py` or `ms11_hooks.py`) agrees with A11 on 17 of the 18 MS11 rows (identical status words and identical counts). One row does not: RB9 `b_map_cells_fraction` (map 1: independent 45 of 760, A11 51 of 760; map 2 equal at 71 of 296). A post-hoc read-only look shows the two numbers reconcile through two cycle-frequency estimators (Hilbert phase against zero crossings), see section 4. The A11 output is unchanged.

## 2. Rows (A11 rows 27 to 44)

Agreement = identical status words and identical counts. Floats are listed with their difference and are not judged. Independence notes: "frozen classifier (shared)" means every Table 2.1 class and episode came from the same frozen classifier as in A11; the criteria loader is shared by all rows.

| # | RB | check | A11 value | A11 status | independent value | independent status | match | counts equal | floats listed (max abs difference) | independence note |
|---|---|---|---|---|---|---|---|---|---|---|
|27|RB2|headline_class_kept_0.5_sigma|8 of 10 (0 failed)|PASS|kept 8 of 10 (0 failed)|PASS|yes|5 of 5|0 (0)|classes: frozen classifier (shared) on the raw v read by my own reader; kept counts, thresholds, status: own code|
|28|RB2|headline_class_kept_1.0_sigma|7 of 10 (0 failed)|FAIL|kept 7 of 10 (0 failed)|FAIL|yes|5 of 5|0 (0)|classes: frozen classifier (shared) on the raw v read by my own reader; kept counts, thresholds, status: own code|
|29|RB2|two_sigma_reported|see results section 3|REPORTED|kept counts and class tables, 12 (sigma, T_ramp) cells: all equal|REPORTED|yes|36 of 36|0 (0)|classes: frozen classifier (shared) on the raw v read by my own reader; kept counts, thresholds, status: own code|
|30|RB2|stricter_readings|see results section 3|REPORTED|S+ only and S+ or S-abs counts, 12 cells: all equal|REPORTED|yes|24 of 24|0 (0)|classes: frozen classifier (shared) on the raw v read by my own reader; kept counts, thresholds, status: own code|
|31|RB2|dl251_controls|7 of 10 at each sigma|REPORTED|kept 7 of 10 at each sigma (NS 3, S-rel 7): equal|REPORTED|yes|6 of 6|0 (0)|classes: frozen classifier (shared) on the raw v read by my own reader; kept counts, thresholds, status: own code|
|32|RB5|delta0_T10_T316|4 of 4 unchanged|PASS|4 of 4 unchanged (D-tr)|PASS|yes|10 of 10|8 (0)|classes: frozen classifier (shared); label equality and onset/delay shifts: own code from the stored onset and the stored eta series|
|33|RB5|updown|13 D-tr|REPORTED|P5 classes at 13 T_ramp: all D-tr, equal|REPORTED|yes|14 of 14|0 (0)|classes: frozen classifier (shared); label equality and onset/delay shifts: own code from the stored onset and the stored eta series|
|34|RB6|rtol_T10_T316|D-tr in 4 of 4, differences 0.0|REPORTED|D-tr in 4 of 4, differences 0.0|REPORTED|yes|8 of 8|8 (0)|classes: frozen classifier (shared); onset and delay differences: own subtraction|
|35|RB6|floor_other_T_ramp|classifier-onset medians T10: -1.4967 / -0.9706 / -1.0291; T316 as independent; raw crossing: NaN by construction (erratum)|REPORTED|classifier-onset medians T10: -1.4965 / -0.9708 / -1.0289, T316: -1.5 / -1.5 / -1.2731, not monotone; raw crossing: not defined for mode N, nothing computed|REPORTED|yes|10 of 10|6 (0.000175)|classifier-onset reading: frozen classifier (shared) + own delay (stored eta series) and median; raw-crossing reading: not defined for the mode N floor runs (DL-402), nothing computed, only the A11 word compared|
|36|RB6|network_fpk_halving_dt|classifier-episode 0 pass / 3 fail; PSD argmax 2 pass / 1 fail|FAIL|classifier-episode f_pk 0 pass / 3 fail; PSD argmax 2 pass / 1 fail; row FAIL|FAIL|yes|31 of 31|30 (0)|reading (i): frozen classifier episode f_pk (shared); reading (ii): method taken from original behaviour (DL-401), arithmetic independent (own spectrogram call on the raw v); bound, pair and verdict logic: own|
|37|RB6|network_vp_pm100_vs_pm200|12 f_pk values|REPORTED|12 f_pk values equal|REPORTED|yes|1 of 1|12 (0)|reading (i): frozen classifier episode f_pk (shared); reading (ii): method taken from original behaviour (DL-401), arithmetic independent (own spectrogram call on the raw v); bound, pair and verdict logic: own|
|38|RB9|a_dimensional_vs_nondimensional|1.2258082426051166e-08|PASS|1.2258082426051166e-08 (re-read of the stored file)|PASS|yes|1 of 1|1 (0)|NOT independent: re-reads results/A11/rb9a_unit_level.json written by rb9a_unit.py; only the max and the inclusive comparison are mine|
|39|RB9|b_spectral_vs_cycle_headline|49.0 Hz against 44.609402 Hz (Hilbert phase), difference 4.390598 Hz, bound 0.5 Hz|FAIL|49.0 Hz against 44.609421 Hz (zero crossings), difference 4.390579 Hz, bound 0.5 Hz|FAIL|yes|1 of 1|6 (1.86e-05)|cycle frequency: own zero-crossing code from the raw v (independent); episode window and spectral f_pk: frozen classifier (shared)|
|40|RB9|b_map_cells_fraction|map 1: 51 of 760; map 2: 71 of 296|REPORTED|map 1: 45 of 760 within 1/W; map 2: 71 of 296|REPORTED|no|7 of 8|2 (0.00789)|cycle frequency: own zero-crossing code from the raw v (independent); episode window and spectral f_pk: frozen classifier (shared)|
|41|RB9|c_band_30_120_map1|14 of 900 (0.015556)|PASS|14 of 900 (0.015556)|PASS|yes|4 of 4|1 (0)|variant classes: frozen A8 variant classifier (shared) applied by my reader to the raw map-1 v; baseline from the stored map1_classes.csv; counting and fractions: own|
|42|RB10|surge_definition_sensitivity_map1|headline unchanged; max 1.67 percent|PASS|headline unchanged under 9 variants; map-1 fractions equal (max 1.67 percent)|PASS|yes|37 of 37|9 (0)|variant classes: frozen A8 variant classifier (shared) on the raw map-1 and headline v; counting, fractions and verdict: own|
|43|S13|window_x0.5_x2|0.0 percent at both|PASS|0.0 percent at both; headline unchanged|PASS|yes|2 of 2|2 (0)|as RB10 (the window line is the window variants of the RB10 computation)|
|44|RB9|d_tau_pm20|as results section 5|REPORTED|tau 8 ms D-tr 49.5 Hz, tau 12 ms D-tr 43 Hz, headline D-tr 49 Hz; classes equal|REPORTED|yes|5 of 5|12 (0.001)|classes and f_pk, onset, eta at onset: frozen classifier (shared) + own eta read from the stored series; ratios own|

Independence in short. Recomputed from raw stored series by code of its own: RB9(b) cycle frequency (zero crossings), RB6 floor delays and medians (stored eta series), RB6 network reading (ii) arithmetic, all counts, fractions and verdicts. Only re-counted values the frozen classifier, criteria loader or A8 variant function had produced: every class in RB2, RB5, RB6, RB9(c), RB10, window line and RB9(d), and the episode window and spectral f_pk of RB9(b). Not independent at all: RB9(a) (re-reads the stored unit-level file written by `rb9a_unit.py`). RB6 network reading (ii): "method taken from original behaviour, arithmetic independent" (DL-401). The 9i function is not used by the independent check. The 26 carried rows (1 to 26) were recomputed at 11f by the hooks (26 of 26 match); the independent recomputations of MS8, MS9 and MS10 are the earlier steps 8g, 9j and 10g and are not repeated here.

Float differences of note (listed, not judged): RB6 floor classifier-onset medians at 10 s differ by 1.75e-4 (independent eta read from the stored 1 ms series, A11 from the continuous path); RB9(d) duration at tau 8 ms differs by 1.0e-3 s; the headline cycle frequency differs by 1.9e-5 Hz (zero crossings against Hilbert phase).

## 3. The mismatch row

RB9 `b_map_cells_fraction` (REPORTED in both, no gate fraction): map 1 cells with an episode 760 in both; within 1/W (0.5 Hz): A11 51 (Hilbert phase over the flagged episode, rules section 4(b)), independent 45 (upward zero crossings in the same window). Map 2: 71 of 296 in both. The match is therefore "no" for this row. No code path was patched and neither output was re-run (DL-405).

## 4. Post-hoc look at the mismatch (post hoc, exploratory, read only; DL-406, DL-407)

760 map-1 cells: Hilbert estimator 51 within, zero-crossing estimator 45 within. The estimators disagree on "within" in 18 cells: 12 within by Hilbert and outside by zero crossings, 6 the other way; 12 - 6 = 51 - 45, so the counts reconcile through the listed cells. The disagreements are not near-bound flips: in the 12 cells the zero-crossing frequency is 0.88 to 11.25 Hz from the spectral f_pk while the Hilbert frequency is within 0.5 Hz; in the 6 cells the Hilbert frequency is 5.09 to 8.32 Hz below f_pk while the zero-crossing frequency is within 0.5 Hz; the largest difference between the two estimators over all 760 cells is 14.76 Hz. Why was not investigated (UNVERIFIED). Headline under both: Hilbert 44.609402 Hz, zero crossings 44.609421 Hz, spectral 49.0 Hz, difference 4.3906 Hz against 0.5 Hz: FAIL under either. Table: `results/A11/post_hoc_9b_look/ms11_9b_map1_estimator_look.csv`.

## 5. Claim limits (DL-394 as reworded, DL-401, DL-402, DL-406, DL-407)

- MS11-C1: the headline surge class is kept in 7 of 10 seeds at sigma (required 8 of 10), and the constant-parameter controls reach the same class in 7 of 10 at each sigma; no claim that a ramp-driven surge is robust to noise (carry with DL-229, DL-258 and the MS9 D24 failure).
- MS11-C2: no claim of f_pk or class agreement between the network and the mean field (RB6 network f_pk failed under both readings; carry with G4-C1).
- MS11-C3: at the headline the spectral and the cycle frequency differ by 4.39 Hz against the 1/W bound of 0.5 Hz (RB9(b) FAIL); the cause is not investigated; peak frequencies are stated as the classifier's spectral peaks.
- MS11-C4: RB9(a) rests on the unit-level test only (1 s path_eta ramp, tau 10 and 20 ms, not the headline).
- MS11-C5: the DOP853 versus Radau comparison covers T_ramp 120 s only (cut order step 1, DL-337).
- MS11-C6 (reworded, DL-402): the floor-level direction of RB3(b) is unresolved at T_ramp 10 s and 316 s: classifier-onset medians are not monotone; the raw-crossing onset is defined only for mode D records, so no raw-crossing median exists for the mode N floor runs; no scaling law is entered (UNVERIFIED).
- MS11-C7: all earlier failures and claim limits stand as logged (RB1 FAIL, G7 not passed, D24 failed, G4-C1 to G4-C6, the MS9 claim limits).
- MS11-C8 (accepted, DL-406): RB6 network reading (ii) f_pk for episodes shorter than W relies on a method not stated in the frozen rules (described in DL-401); the verdict stands as evaluated. All 3 of 3 reading-(ii) comparisons have a base episode of 0.083 s against W = 0.333 s.
- MS11-C9 (CANDIDATE, open for the reviewer, DL-407): the frozen rules do not name the estimator of the cycle frequency in RB9(b); the map-cell fractions are 51 of 760 (A11, Hilbert phase) and 45 of 760 (independent, zero crossings), both reported; the headline RB9(b) FAIL holds under either estimator. To be carried with it: the two estimators differ by several Hz in 18 of 760 cells.

## 6. Commits involved

dd78cc1 (11f, A11 run and results); 8ff8ee3 (rulings DL-392 to DL-397, pre-checks, independent script, module, tests); 228e948 (stop, DL-400); 8690b14 (DL-401 to DL-404, erratum, amended independent script); 02ad127 (independent result, DL-405); the commit adding DL-406 and `scripts/ms11_9b_look.py`; the 11g closing commit (this sheet, the hash CSV, DL-407 to the last entry). Records were produced at d29268f. No tag, no push.

## 7. Known weak points

- The independent check shares the frozen classifier, the criteria loader and the A8 variant definitions with the original evaluation; a fault there is common to both. The 9i function is not used.
- RB9(a) is not independent (re-reads a stored file) and is unit-level only (MS11-C4).
- The RB6 network reading (ii) method is taken from the original behaviour (DL-401) and is not in the frozen rules (MS11-C8).
- The cycle-frequency estimator is not named in the rules (MS11-C9, candidate); the map-cell fraction of RB9(b) depends on it.
- D36: the total after MS11 on basis B is 13.51 h of 24 h (basis A 14.52 h); basis B is the one basis from now on; the 14.21 h mixed-basis figure stays UNVERIFIED (DL-396).
- Sigma 0.0624 was checked and not confirmed (G4-C4); every noisy mean-field result carries that label. Classes that went through the D8 call are provisional (D8 open, DL-137).
- The A11 floor raw-crossing rows were undefined by construction (erratum in `docs/ms11_results.md` section 9, DL-402); DL-387 and DL-390 carry the old sentence and are corrected by DL-402.
- RB2 judged at T_ramp 120 s, "class unchanged" as the exact label, the network f_pk sources and all-evaluable-seeds-inside are readings the rules mark UNVERIFIED.
- Map 2 and the noisy subgrid were not recomputed independently for RB9(c) or RB10 (reported only in A11); the 26 carried rows were not recomputed again at 11g.
