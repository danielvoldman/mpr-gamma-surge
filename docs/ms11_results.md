# MS11 results (11f; the frozen A11 evaluation, run once on the real records)

Written for: the reviewer, who rules on the claim limits in section 8. Every number below is copied from `results/A11/a11_robustness.csv` and `results/A11/a11_evaluators.json` (git-ignored outputs of `scripts/run_A11.py`, one run, exit code 0, 44 rows, 0 missing records) or from the run journals; nothing was recomputed by hand, no diagnostic or alternative evaluation was run. Interpretation is limited to the frozen rules (`docs/ms11_eval_rules.md`, SHA-256 4b1a1a66...48a5; `configs/ms11/ms11_eval.yaml` fcb43964...09cf; DL-377). Statements marked UNVERIFIED are readings the rules themselves mark so.

## 1. Pre-checks, launch outcome and audit

All pre-checks passed before anything else was done: criteria-loader gate (tag `criteria-frozen`, commit dd8330c5eaacd63d21e7b7969430988d00862769, criteria SHA-256 c7d2f36b...fa05); the three config hashes (S13, A4_grids, S5_cells); the four MS10 result files and the 10f table (321 files, 0 mismatches, digest d1b98f05...2a52); the eval freeze of DL-377; the five list definition hashes; tree clean; HEAD d29268f.

Launch (by the reviewer, PowerShell, 2026-10-26, clean tree; journals in `results/ms11/launch_*`): MS11_S11 120 ok, 34.1 s; MS11_CTRL 30 ok, 10.6 s; MS11_RB9D 2 ok, 143.3 s (2 workers); MS11_S13_MF 68 ok, 407.5 s; MS11_S13_NET 18 ok, 502.5 s. Total 238 ok, 0 failed, list wall 1098 s (18.3 min).

Run-record audit (records only): every list has all listed records, status ok in all, git dirty = false in all, commit d29268f73943c75383b1be942d57d0f6afe01b81 in all, full config hash and name equal to the frozen list row, no duplicates, an npz beside every record, criteria SHA-256 c7d2f36b... in all. Result-file table (238 records x json, npz, params.md, plus manifest.csv and run.log of the five journals, 10f convention): 724 files, 1192.35 MB, digest cdafcc0831580ea4b9f7dfd8e095deb50e8b86db2974f556cf7ffe7d75637f53.

Slow tests: 24 passed, 910 deselected, 551.72 s, pytest exit code 0 (taken from pytest itself).

## 2. A11 table (all 44 rows)

Status words: PASS, FAIL, NOT EVALUABLE, REPORTED. "match" is `recomputed_match`; "no" on the 18 MS11 rows means no logged verdict exists yet (first evaluation), not a mismatch. n_evaluated is empty on the 26 carried rows (the column is filled for the MS11 evaluators only).

| # | RB | check | value | threshold | status | logged word | match | n_evaluated | label | note |
|---|---|---|---|---|---|---|---|---|---|---|
|1|RB1|headline_10s|0 of 3 seeds|3 of 3|FAIL|FAIL|yes||pre-registered|recomputed, equals logged; T_ramp 10 s: 0 of 3 seeds pass|
|2|RB1|headline_120s|0 of 3 seeds|3 of 3|FAIL|FAIL|yes||pre-registered|recomputed, equals logged; T_ramp 120 s: 0 of 3 seeds pass|
|3|RB1|cells_30s|1 of 4 cells|>= 3 of 4|FAIL|FAIL|yes||pre-registered|recomputed, equals logged; 1 of 4 cells agree (3 needed)|
|4|RB1|n_rule_60s|||PASS|PASS|yes||pre-registered|recomputed, equals logged; N rule at 60 s (no worse with N)|
|5|RB1|overall|||FAIL|FAIL|yes||pre-registered|recomputed, equals logged; parts {'headline': {10.0: 'FAIL', 120.0: 'FAIL'}, 'cells': 'FAIL', 'N_rule': 'PASS'}|
|6|RB2|noisy_subgrid_agreement|97 of 225 cells (43.1 percent)|203 of 225 (90 percent, D24)|FAIL|FAILED|yes||pre-registered|recomputed, equals logged; 97 of 225 cells agree (43.1 percent), 203 needed; P-1 post hoc 173 of 225 feeds no gate (DL-257)|
|7|RB3|a_inrange_runs|0 of 6 testable in-range runs|within one A4 step|FAIL|DOES NOT MEET|yes||pre-registered|recomputed, equals logged; 0 of 6 testable in-range runs within one A4 step|
|8|RB3|a_headline|||NOT EVALUABLE|NOT JUDGED|yes||pre-registered|recomputed, equals logged; headline not in range (match error 65.94769903531791 steps)|
|9|RB3|b_raw_crossing||strict decrease over the three floor levels|PASS|MEETS|yes||pre-registered|recomputed, equals logged; raw first crossing (primary reading, 8f2 ruling 1)|
|10|RB3|b_classifier_onset|||FAIL|DOES NOT MEET|yes||pre-registered|recomputed, equals logged; classifier onset (alternative reading kept beside the primary); alternative reading kept beside the primary; label as written in the sheet|
|11|RB3|c_T_ramp_56_to_316|||PASS|MEETS|yes||pre-registered|recomputed, equals logged; P2 linear classes ['D-tr', 'D-tr', 'D-tr', 'D-tr'] against the headline class|
|12|RB3|d_profile|||REPORTED|REPORTED|yes||pre-registered|recomputed, equals logged; per path, no pooled verdict; per path and T_ramp, no pooled verdict|
|13|RB4|parameter_perturbation|0 of 14 changed; 64 of 64 unchanged|<= 2 of 14; >= 80 percent|PASS|PASS|yes||pre-registered|recomputed, equals logged; 0 of 14 one-at-a-time runs changed (at most 2); 64 of 64 hypercube points unchanged (52 needed)|
|14|RB5|delta0_headline_class|||PASS|MEETS|yes||pre-registered|recomputed, equals logged; class unchanged over the delta0 ladder: True|
|15|RB5|delta0_headline_delay|||REPORTED|REPORTED|yes||pre-registered|recomputed, equals logged; delay shifts against the 1e-6 member are computed and reported, not tested|
|16|RB5|start_distance|||REPORTED|REPORTED|yes||pre-registered|recomputed, equals logged; per T_ramp, no pooled verdict; per T_ramp, no pooled verdict|
|17|RB6|heun_headline|||PASS|MEETS|yes||pre-registered|recomputed, equals logged; onset reading cross; relative change against the bound; relative change 0, a limit of the 1 ms output grid|
|18|RB6|solver_class_headline|||PASS|MEETS|yes||pre-registered|recomputed, equals logged; D-tr against D-tr|
|19|RB6|solver_onset_headline|181 ms|1 ms|FAIL|DOES NOT MEET|yes||pre-registered|recomputed, equals logged; onset difference 181.000 ms (classifier) and 181.000 ms (raw crossing) against 1.0 ms; covers the headline T_ramp only (DL-337)|
|20|RB6|rtol_headline|||REPORTED|REPORTED|yes||pre-registered|recomputed, equals logged; reported against rtol, not a pass test|
|21|RB8|heterogeneity|||NOT EVALUABLE|NOT EVALUABLE|yes||pre-registered|recomputed, equals logged; the 3 Lorentzian seeds do not share one Table 2.1 correspondence class|
|22|RB8|m4_adaptation|||NOT EVALUABLE|OPEN|yes||pre-registered|recomputed, equals logged; the frozen leaf RB8.M4_criteria has no value (F-23, deferred; MS12)|
|23|G5|gate|||REPORTED|PASSED, continue|yes||pre-registered|recomputed, equals logged; 760 of 900 map-1 cells in a surge class (27 needed); RB4 passes|
|24|G6|gate|||PASS|PASSED WITH DEPARTURES|yes||pre-registered|recomputed, equals logged; components not MEETS: {'RB3/a_inrange_runs': 'DOES NOT MEET', 'RB3/a_headline': 'NOT JUDGED', 'RB3/b_classifier_onset': 'DOES NOT MEET', 'RB6/solver_onset_headline': 'DOES NOT MEET'}; covered by departures ['G6-D1', 'G6-D2', 'G6-D...|
|25|G7|gate|||FAIL|NOT PASSED|yes||pre-registered|recomputed, equals logged; 1 of 19 NC1 runs in a surge class (Counter({'S+': 1}))|
|26|sigma_check|S8_baseline_std|||FAIL|NOT INSIDE|yes||pre-registered|recomputed, equals logged; mean-field baseline std 0.039522 against the network range [0.037989016862495596, 0.03892009915468159]|
|27|RB2|headline_class_kept_0.5_sigma|8 of 10 (0 failed)|>= 8 of 10|PASS||no|10|pre-registered|no logged verdict yet (first evaluation); sigma checked, not confirmed (G4-C4)|
|28|RB2|headline_class_kept_1.0_sigma|7 of 10 (0 failed)|>= 8 of 10|FAIL||no|10|pre-registered|no logged verdict yet (first evaluation); sigma checked, not confirmed (G4-C4)|
|29|RB2|two_sigma_reported|||REPORTED||no|20|pre-registered|no logged verdict yet (first evaluation); sigma checked, not confirmed (G4-C4); post hoc, feeds no gate|
|30|RB2|stricter_readings|||REPORTED||no|20|post hoc|no logged verdict yet (first evaluation); post hoc, feeds no gate|
|31|RB2|dl251_controls|||REPORTED||no|20|post hoc|no logged verdict yet (first evaluation); POST-HOC AMENDMENT (DL-251)|
|32|RB5|delta0_T10_T316||same Table 2.1 label as the 1e-6 member|PASS||no|4|pre-registered|no logged verdict yet (first evaluation)|
|33|RB5|updown|||REPORTED||no|13|pre-registered|no logged verdict yet (first evaluation); S4 labelled no class|
|34|RB6|rtol_T10_T316|||REPORTED||no|4|pre-registered|no logged verdict yet (first evaluation)|
|35|RB6|floor_other_T_ramp|||REPORTED||no|4|pre-registered|no logged verdict yet (first evaluation); RB3(b) form, reported only, no scaling law (UNVERIFIED)|
|36|RB6|network_fpk_halving_dt||< 0.02|FAIL||no|6|pre-registered|no logged verdict yet (first evaluation); G4-C1 to G4-C6 apply (network records)|
|37|RB6|network_vp_pm100_vs_pm200|||REPORTED||no|6|pre-registered|no logged verdict yet (first evaluation); reported only, no pass number in the plan|
|38|RB9|a_dimensional_vs_nondimensional|1.2258082426051166e-08|within 0.005|PASS||no|2|pre-registered|no logged verdict yet (first evaluation); unit-level test: 1 s path_eta ramp (eta 1 to 4), tau 10 and 20 ms, not the headline path, no run record (ruling 6, DL-351)|
|39|RB9|b_spectral_vs_cycle_headline||within 1/W|FAIL||no|1|pre-registered|no logged verdict yet (first evaluation)|
|40|RB9|b_map_cells_fraction|||REPORTED||no|1|pre-registered|no logged verdict yet (first evaluation); reported as a fraction, no gate fraction|
|41|RB9|c_band_30_120_map1|0.015555555555555555|<= 0.05|PASS||no|900|pre-registered|no logged verdict yet (first evaluation)|
|42|RB9|d_tau_pm20|tau 8 ms: D-tr, f_pk 49.5 Hz (0.396 per tau); tau 12 ms: D-tr, f_pk 43 Hz (0.516 per tau); headline 10 ms: D-tr, f_pk 49 Hz|reported only, no pass test|REPORTED||no|2|post hoc|no logged verdict yet (first evaluation); post hoc, feeds no gate; a class change mixes the tau effect with the path missing a shifted Hopf point; the 1/tau frequency scaling is [reasoned, not tested]|
|43|RB10|surge_definition_sensitivity_map1||headline unchanged; <= 0.1|PASS||no|900|pre-registered|no logged verdict yet (first evaluation)|
|44|S13|window_x0.5_x2||headline unchanged; <= 0.1|PASS||no|900|pre-registered|no logged verdict yet (first evaluation)|

Labels on every row of the noisy mean-field and network results: "sigma checked, not confirmed" (G4-C4, sigma 0.0624); "provisional (D8 open, DL-137)" on classes that went through a D8 call; G4-C1 to G4-C6 on the network rows. The short-window false-surge rates (306, 400, 172, 24 of 500 at W = 0.2, 0.333, 0.593, 1.054 s) apply beside the S11 classes at T_ramp 10 s and 30 s.

## 3. RB2 at 0.5 sigma, sigma and 2 sigma, with the DL-251 controls

Gate (T_ramp 120 s, "kept" = class S+, S-rel or S-abs, at least 8 of 10 seeds, failed runs 0): **0.5 sigma 8 of 10 PASS; sigma 7 of 10 FAIL**; 2 sigma 8 of 10 reported, no pass rule. Classes over the 10 seeds at 120 s: 0.5 sigma S+ 2, S-rel 5, S-sus 2, S-abs 1; sigma S+ 2, S-rel 4, S-sus 2, S-abs 1, NS 1; 2 sigma S+ 2, S-rel 5, S-sus 2, S-abs 1. The seed index is the same noise stream at every sigma (paired).

Kept counts of 10 at the other T_ramp (reported, no verdict, post hoc, feed no gate): 10 s 3 / 3 / 3, 30 s 4 / 4 / 5, 300 s 10 / 9 / 10 (0.5 sigma / sigma / 2 sigma). Stricter readings at 120 s (post hoc): S+ only 2 / 2 / 2; S+ or S-abs 3 / 3 / 3.

DL-251 constant-parameter controls (POST-HOC AMENDMENT, feed no gate): at every one of the three sigma levels, NS 3 and S-rel 7 of 10 seeds, i.e. a kept-class count of 7 of 10 with no ramp. By the rule's own reading (section 1 of the eval rules), where the control also gives a surge class in k of 10 seeds, the S11 count at that sigma is not ramp evidence beyond the control: control 7 of 10 against S11 8 of 10 (0.5 sigma) and 7 of 10 (sigma) at 120 s. Subgrid carried in unchanged: 97 of 225 (43.1 percent), 203 needed, FAILED (DL-242).

## 4. The open RB5 and RB6 parts

RB5 delta_0 ladder (Table 2.1 label against the S5 grid 1e-6 member, exact label): T_ramp 10 s and 316.2278 s, delta_0 1e-9 and 1e-3, all four D-tr against D-tr: **PASS (4 of 4 unchanged)**; onset shift 0.0 s and delay shift 0.0 at the 1 ms output grid in all four (reported, not tested). RB5 up versus down: P5 classes at the 13 T_ramp values 1 to 1000 s are all D-tr; status REPORTED; S4 stands beside it labelled "no class", supporting amplitude evidence only.

RB6 rtol (1e-8 and 1e-12 against the 1e-10 grid run, T_ramp 10 s and 316.2278 s): class D-tr in all four, onset difference 0.0 s and delay difference 0.0 in all four; REPORTED, not a pass test. Solver agreement (DOP853 against Radau) covers the headline T_ramp 120 s only (181 ms against 1 ms, DOES NOT MEET, carried and recomputed); nothing is said at 10 s or 316 s.

RB6 mean-field floor at T_ramp 10 s and 316.2278 s: see section 6. The 5 percent Heun test cannot be formed there (only the default rung is run); it stands at 120 s as recorded.

RB6 network (N = 1e4, 10 s ramp, 3 seeds per configuration; "halving dt" is dt 1e-3 against 5e-4; bound 2 percent; labels as in section 2; f_pk reading UNVERIFIED, M11-6): **row FAIL** (rule: FAIL if either reading fails). Classifier-episode f_pk: seeds 0, 1, 2 give 63.06 against 90.09 Hz (43 percent), 60.06 against 48.05 Hz (20 percent), 60.06 against 57.06 Hz (5 percent): 0 pass, 3 fail, reading FAIL. PSD argmax (25 to 100 Hz): 63.06 against 63.06, 60.06 against 60.06, 60.06 against 57.06 Hz (5 percent): 2 pass, 1 fail, reading FAIL. No seed is NOT EVALUABLE and no class change in either reading (1 bin = 3.003 Hz). Printed beside, no test: 5e-4 against 2.5e-4 and 2.5e-4 against 1e-4 (classifier-episode f_pk, per seed relative differences 33, 25, 0 percent and 55, 20, 5 percent); V_p +-100 against +-200 at dt 1e-3 (63.06 against 81.08, 60.06 against 78.08, 60.06 against 75.08 Hz) and at dt 1e-4 (93.09 against 93.09, 48.05 against 48.05, 60.06 against 96.10 Hz). Classes of the 18 network runs are information only: no class claim (G4-C3 stands).

## 5. RB9 (a) to (d), RB10 and the window line

- **RB9(a)** PASS: maximum relative difference 1.2258e-08 against 0.005 (tau 10 ms 1.2258e-08, tau 20 ms 2.2124e-09). Scope limit: a 1 s path_eta ramp (eta 1 to 4), tau 10 and 20 ms, not the headline path, no run record (ruling 6, DL-351).
- **RB9(b)** headline FAIL: spectral f_pk 49.0 Hz (classifier episode) against cycle frequency 44.609 Hz, difference 4.391 Hz against the bound 1/W = 0.5 Hz (8.78 bins). Cells reported as a fraction, no gate fraction: map 1, 51 of 760 within the bound (6.7 percent); map 2, 71 of 296 (24.0 percent).
- **RB9(c)** PASS: band 30 to 120 Hz changes the class of 14 of 900 map-1 cells (1.56 percent, bound 5 percent, 0 excluded); three-category change also 14. Beside, no verdict: map 2 0 of 325 changed; noisy subgrid 1096 of 2250 changed (48.7 percent; 718, 31.9 percent, in the three-category form). Label: provisional (D8 open).
- **RB9(d)** (post hoc, reported only, feeds no gate, deterministic): the stored headline at tau 10 ms is D-tr, f_pk 49 Hz (0.49 per tau), onset 58.698 s. tau 8 ms: D-tr, f_pk 49.5 Hz (0.396 per tau), onset 55.628 s. tau 12 ms: D-tr, f_pk 43 Hz (0.516 per tau), onset 62.184 s. The class is unchanged at both tau; the 1/tau scaling of the frequency (expected 1.25 and 0.833 times the headline, observed 1.010 and 0.878) is [reasoned, not tested]. A class change under this reading would mix the tau effect with the path missing a shifted Hopf point (tau_d stays 5 ms, so tau_d/tau is 0.625 or 0.4167 while the eta numbers are held); no class change occurred.
- **RB10** PASS: headline class unchanged under all nine variants; share of map-1 cells changing class (bound 10 percent, 900 evaluated, 0 excluded): band 30 to 120 1.56 percent, factors 1.5 and 4 0.0 percent, A_min 0.05 1.00 percent, A_min 0.2 1.67 percent, window x0.5 and x2 0.0 percent, minimum cycles 5 and 20 0.0 percent.
- **S13 window line** (window x 0.5 and x 2, the window variant of the RB10 computation, no separate run): PASS, 0.0 percent of 900 cells at both.

## 6. Mean-field floor medians at T_ramp 10 s and 316.2278 s (RB3(b) form, reported only, no scaling law entered, UNVERIFIED; feeds no gate)

Three floor levels x 10 seeds, default Heun rung. Median delay (as stored) by level 0 / 1 / 2:

| Onset reading | T_ramp 10 s | T_ramp 316.2278 s |
|---|---|---|
| classifier onset | -1.4967 / -0.9706 / -1.0291; not monotone; seeds without onset 0 / 0 / 0 | -1.5000 / -1.5000 / -1.2731; not monotone; seeds without onset 0 / 0 / 0 |
| raw first crossing | undefined (NaN at every level); seeds without onset 10 / 10 / 10 | undefined (NaN at every level); seeds without onset 10 / 10 / 10 |

Direction of the change of the median with floor level: not monotone under the classifier-onset reading, undefined under the raw-crossing reading (no seed has a raw onset at either T_ramp).

## 7. Carried checks: recomputed against logged (26)

**26 of 26 recomputed values match the logged word under the 11d map; 0 mismatches.** Words (logged -> status): RB1 headline 10 s and 120 s, cells, overall FAIL; n_rule PASS; RB2 subgrid FAILED -> FAIL; RB3 a_inrange DOES NOT MEET -> FAIL, a_headline NOT JUDGED -> NOT EVALUABLE, b_raw MEETS -> PASS, b_classifier DOES NOT MEET -> FAIL, c MEETS -> PASS, d REPORTED; RB4 PASS; RB5 class MEETS -> PASS, delay and start distance REPORTED; RB6 heun and solver class MEETS -> PASS, solver onset DOES NOT MEET -> FAIL, rtol REPORTED; RB8 heterogeneity NOT EVALUABLE, m4 OPEN -> NOT EVALUABLE; G5 "PASSED, continue" -> REPORTED (DL-377); G6 PASSED WITH DEPARTURES -> PASS (departures named in the note, DL-208); G7 NOT PASSED -> FAIL; sigma_check NOT INSIDE -> FAIL.

What the recomputation shares with the original (from the `note` column, so it is not independent of these): all 25 hooks except RB8 m4 share the criteria loader and the frozen classifier (class column); the original evaluator function itself (same code) is shared by the 5 RB1 rows, the 6 RB3 rows, the 3 RB5 rows, the 4 RB6 MS8 rows, RB8 heterogeneity, G6 and sigma_check (21 hooks); the A7 table-writing pieces by the RB3, RB5, RB6 and G6 hooks (14); the 9i function (ms9_9i.j_exit_static_path via ms10_eval.table21_fields) by the 7 MS10 hooks (RB1 x5, RB8 heterogeneity, sigma_check); G6 also applies the reviewer's departure ruling (applied, not recomputed). RB2 subgrid, RB4, G5 and G7 recompute from the stored class tables with the loader and classifier only. RB8 m4 reads the frozen leaf of the tag blob (no value, F-23, MS12).

## 8. Claim limits that follow (candidates for the reviewer to rule on; none is entered as a decision)

1. RB2 is not met at sigma (7 of 10 at T_ramp 120 s, against 8 needed); met at 0.5 sigma (8 of 10). A candidate limit: no claim that the headline surge class is robust to noise at the calibrated sigma; and, by the rule's control reading, the S11 counts (8 and 7 of 10) are not ramp evidence beyond the constant-parameter controls (7 of 10 at every sigma).
2. RB6 network f_pk: FAIL under both readings. A candidate limit: no network f_pk or frequency claim to any resolution finer than the observed differences (up to 27 Hz, 9 bins, between dt 1e-3 and 5e-4); with G4-C3, no class claim from the network runs.
3. RB9(b) headline FAIL: spectral and cycle frequency differ by 4.39 Hz against 0.5 Hz. A candidate limit: no claim that the spectral f_pk equals the cycle frequency of the flagged episode to within the window resolution.
4. RB9(a) evidence is unit-level only (1 s path_eta ramp, tau 10 and 20 ms, no headline-path record).
5. Solver agreement (RB6 DOP853 against Radau) is known at 120 s only and DOES NOT MEET there (181 ms against 1 ms); no statement at 10 s or 316 s.
6. The floor-level direction (RB3(b) form) is not monotone under the classifier reading and undefined under the raw-crossing reading at 10 s and 316 s; no scaling law and no direction claim from these runs. The 5 percent Heun test is not formed at 10 s and 316 s.
7. RB9(c), RB10 and the window line are on map 1 (900 cells) with D8 provisional; the noisy subgrid changes class in 48.7 percent of runs under the 30 to 120 Hz band (reported only).
8. RB9(d) is post hoc and class-unchanged at tau +-20 percent under Reading A; no frequency-scaling claim ([reasoned, not tested]).
9. Carried failures stand as logged: RB1 overall FAIL, RB2 subgrid FAILED, RB3 a_inrange and b_classifier DOES NOT MEET, G7 NOT PASSED, sigma_check NOT INSIDE, RB8 heterogeneity and M4 NOT EVALUABLE.

Choices the frozen rules leave open: none were needed to produce any row; no choice was made. Readings the rules mark UNVERIFIED and that were used as written: "class unchanged" as the exact label; RB2 judged at 120 s; the network f_pk sources; all-evaluable-seeds-inside for the network verdict; the D43 floor levels. One observation for the reviewer, not interpreted: the raw-crossing floor readings have no onset in any of the 60 seeds at 10 s and 316 s.

## 9. Erratum (11g, appended; the text above is kept unchanged)

Written for: the reviewer. Cause: an implementation fact found while preparing the independent recomputation, confirmed by reading `classify_stored` in `src/mprsurge/analysis/ms11_eval.py` and `docs/ms11_eval_rules.md` (read only; no run, no diagnostic).

Facts. (1) `classify_stored` computes the raw-crossing onset (`onset_raw_s`) only when the record is mode D (`... if mode == "D" else None`); for a mode N record it is NaN. (2) `mode_of` returns D for run kind `mf` and N for every other kind, and the 60 floor runs of MS11_S13_MF are kind `mf_noisy`, i.e. mode N. (3) The eval rules (section 3, floor) ask for the floor medians under both onset readings of the MS8 sheet, and do not say that the raw crossing is restricted to mode D. So the raw-crossing floor rows of section 2 (row 35), section 6 and section 8 item 6 were produced by a function that cannot return an onset for these runs; "NaN at every level" and "seeds without onset 10 / 10 / 10" are consequences of that, not a finding about the data.

Corrections. The last sentence of section 6 ("the raw-crossing floor readings have no onset in any of the 60 seeds at 10 s and 316 s") and the sentence under the section 6 table ("undefined under the raw-crossing reading (no seed has a raw onset at either T_ramp)") are wrong as findings. The correct statement: the raw-crossing onset is defined only for mode D records, so no raw-crossing median exists for the mode N floor runs; whether the raw envelope crosses the threshold in these runs was not examined. The classifier-onset medians in section 6 are unaffected. Claim limit MS11-C6 is reworded accordingly (see the decision log). Row 35 stays REPORTED; no other row is affected.
