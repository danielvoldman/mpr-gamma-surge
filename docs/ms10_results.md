# MS10 results (10f)

Tables and verdicts only, in the pre-registered wording (`docs/ms10_eval_rules.md`, `configs/ms10/ms10_eval.yaml`). Source: `results/ms10/eval/ms10_eval.json`, written by `scripts/evaluate_ms10.py` from the stored records of the six launched lists; nothing was integrated at 10f. Claim limits: DL-229 and DL-258 b apply to every network class below (a network class is a class of the frozen mode-N classifier on the mean voltage v of one finite-N realisation; the primary reading is the Table 2.1 correspondence, the post-hoc reading does not count S-rel as a match for D-tr).

Criteria gate (tag criteria-frozen): c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05. Time origins (R27): shared = true in 7 of 7 comparisons; stamp offset 1 ms.

## Sigma check (R16, R25, R28)

Reference 0.039522 (MS7 baseline-only record, DL-310). Network baseline std of v over samples [0, 5000), ddof 1, 6 S8 headline runs, bounds inclusive.

| run | baseline std |
|---|---|
| S8_head_0000_a1c3962081d6 | 0.038920 |
| S8_head_0001_c8b2c7055fec | 0.037989 |
| S8_head_0002_6cc608689f3f | 0.038455 |
| S8_head_0003_7dfd3c05b40c | 0.038920 |
| S8_head_0004_4a8295e0a793 | 0.037989 |
| S8_head_0005_188fa49b5ae5 | 0.038455 |

Range 0.037989 to 0.038920, mean 0.038455. Distinct values overall: 3; distinct per seed across the two T_ramp: {'0': 1, '1': 1, '2': 1} (the 10 s and 120 s baselines of one seed are identical: True). Position of the reference in the range 1.6465 (0 at the minimum, 1 at the maximum); margin to the nearest end -0.000602. Reference / network mean = 1.0278. **Verdict: NOT INSIDE (limitation; sigma stays frozen).** sigma changed: False.

## RB1 (R15, R18, R23, R26, R27)

Claim limits: DL-229 and DL-258 b apply to every network class below (a network class is a class of the frozen mode-N classifier on the mean voltage v of one finite-N realisation; the primary reading is the Table 2.1 correspondence, the post-hoc reading does not count S-rel as a match for D-tr).

### Headline, per seed

| T_ramp | seed | class | MF class | class match (primary) | match without S-rel | f_pk Hz | MF f_pk | rel err | diff in bins (bin Hz) | f_pk ok | onset (classifier) s | MF onset s | diff s | step s | onset ok | raw-crossing onset s (post hoc) | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10.0 | 0 | S-abs | D-tr | True | True | 93.09 | 48.05 | 0.9374 | 15.01 (3.0) | False | 5.176 | 10.6 | -5.427 | 0.1667 | False | 9.767 | False |
| 10.0 | 1 | S-rel | D-tr | True | False | 60.06 | 48.05 | 0.2499 | 4.003 (3.0) | False | 6.178 | 10.6 | -4.425 | 0.1667 | False | 9.594 | False |
| 10.0 | 2 | S-sus | D-tr | False | False | 48.05 | 48.05 | 4.062e-05 | -0.0006507 (3.0) | True | 8.684 | 10.6 | -1.92 | 0.1667 | False | 9.555 | False |
| 120.0 | 0 | S-sus | D-tr | False | False | 49 | 49 | 0 | 0 (0.5) | True | 12 | 58.7 | -46.7 | 1 | False | 50.92 | False |
| 120.0 | 1 | S-sus | D-tr | False | False | 48.5 | 49 | 0.0102 | -1 (0.5) | True | 12 | 58.7 | -46.7 | 1 | False | 50.17 | False |
| 120.0 | 2 | S-sus | D-tr | False | False | 49 | 49 | 0 | 0 (0.5) | True | 12 | 58.7 | -46.7 | 1 | False | 50.86 | False |

| T_ramp | seeds passing | passing without S-rel (post hoc) | C2 control classes beside (same N, T_ramp, Delta, tau_d; 3 seeds; R17) | post-hoc median reading: f_pk median Hz, ok / onset median s, ok / all classes match | verdict |
|---|---|---|---|---|---|
| 10.0 | 0 of 3 | 0 of 3 | S-abs 2, S-rel 1 | 60.06, False / 6.178, False / False | FAIL |
| 120.0 | 0 of 3 | 0 of 3 | S-sus 3 | 49, True / 12, False / False | FAIL |

### Cells (30 s, companion mode-D class; a cell agrees only if 3 of 3 seeds are in the matching class)

| cell (i, j) | companion MF class | stored 120 s class | network classes (seeds 0 to 2) | seeds matching | matching without S-rel | C2 control classes | agrees |
|---|---|---|---|---|---|---|---|
| 0 (7, 4) | D-tr | D-tr | S-abs, S-abs, S-rel | 3 of 3 | 2 of 3 | S-abs 1, S-sus 2 | True |
| 1 (22, 10) | D-tr | D-tr | S-sus, S-abs, S-abs | 2 of 3 | 2 of 3 | S-abs 1, S-sus 2 | False |
| 2 (13, 29) | D-none | D-none | S-abs, S-rel, S-abs | 0 of 3 | 0 of 3 | NS 2, S-rel 1 | False |
| 3 (24, 26) | D-none | D-none | S-sus, S-sus, S-abs | 0 of 3 | 0 of 3 | S+ 1, S-abs 1, S-rel 1 | False |

Cells agreeing: 1 of 4 (need 3); without S-rel (post hoc) 0. Cells part: **FAIL**.

### N rule (R18)

Seeds in the mean-field-matching class (60 s, companion class D-tr): N = 1e4: 2; N = 3e4: 5 (without S-rel: 2 and 5). N = 3e4 no worse than 1e4: **PASS**.

### RB1 verdict

Parts: headline {'10.0': 'FAIL', '120.0': 'FAIL'}, cells FAIL, N rule PASS. **RB1: FAIL** (primary reading; post-hoc readings feed no gate). Failing RB1 is G4 (frozen `on_fail`).

## S9 (finite size; E-6)

Claim limits: DL-229 and DL-258 b apply to every network class below (a network class is a class of the frozen mode-N classifier on the mean voltage v of one finite-N realisation; the primary reading is the Table 2.1 correspondence, the post-hoc reading does not count S-rel as a match for D-tr).

| N | seeds | classes | surge seeds | matching seeds (primary / without S-rel) | f_pk rel err median [range] | onset abs err s median [range] | C2 control classes |
|---|---|---|---|---|---|---|---|
| 1000 | 10 | S-abs 4, S-sus 6 | 4 | 4 / 4 | 0.1531 [0, 0.3776] (n 10) | 15.2 [12.7, 17.7] (n 10) | NS 3 |
| 3000 | 10 | S+ 6, S-abs 1, S-sus 3 | 7 | 7 / 7 | 0.3316 [0, 0.3878] (n 10) | 24.7 [22.7, 25.7] (n 10) | NS 1, S+ 1, S-abs 1 |
| 10000 | 10 | NS 1, S-abs 2, S-sus 7 | 2 | 2 / 2 | 0 [0, 0.05102] (n 9) | 20.7 [18.7, 23.7] (n 9) | S+ 1, S-sus 2 |
| 30000 | 10 | S-abs 5, S-sus 5 | 5 | 5 / 5 | 0.1327 [0.0102, 0.3878] (n 10) | 12.7 [6.698, 18.7] (n 10) | S-abs 1, S-sus 2 |

Table 2.1 Metrics: median [min, max] over the seeds for which the metric is defined; then n defined / n undefined (undefined counted, not imputed; reasons below). J_exit,static and the sign of the exit delay follow the 9i reading (UNVERIFIED, no gate). Both post-surge windows (1 s, 5 s) are kept (O12).

| metric | N = 1000 | N = 3000 | N = 10000 | N = 30000 |
|---|---|---|---|---|
| onset_s | 18.5 [16, 21]; 10/0 | 9 [8, 11]; 10/0 | 13 [10, 15]; 9/1 | 21 [15, 27]; 10/0 |
| eta_onset | 2.184 [2.038, 2.329]; 10/0 | 1.629 [1.571, 1.746]; 10/0 | 1.863 [1.688, 1.979]; 9/1 | 2.329 [1.979, 2.679]; 10/0 |
| delay_eta | -0.7125 [-0.8583, -0.5667]; 10/0 | -1.267 [-1.325, -1.15]; 10/0 | -1.033 [-1.208, -0.9167]; 9/1 | -0.5667 [-0.9167, -0.2167]; 10/0 |
| duration_ms | 2.1e+04 [1000, 7.3e+04]; 10/0 | 4000 [1000, 8.1e+04]; 10/0 | 7.6e+04 [1000, 8e+04]; 9/1 | 3.35e+04 [1000, 7e+04]; 10/0 |
| duration_cycles | 794.8 [30.5, 3414]; 10/0 | 122.2 [31.5, 3633]; 10/0 | 3630 [46.5, 3838]; 9/1 | 1763 [61.5, 3635]; 10/0 |
| duration_frac_ramp | 0.35 [0.01667, 1.217]; 10/0 | 0.06667 [0.01667, 1.35]; 10/0 | 1.267 [0.01667, 1.333]; 9/1 | 0.5583 [0.01667, 1.167]; 10/0 |
| peak_power_abs | 1.954 [0.01052, 3.923]; 10/0 | 0.004858 [0.002721, 3.897]; 10/0 | 3.857 [0.0003367, 3.868]; 9/1 | 1.925 [8.932e-05, 3.855]; 10/0 |
| peak_power_rel | 0.8379 [0.7478, 0.8834]; 10/0 | 0.8456 [0.7462, 0.8824]; 10/0 | 0.8819 [0.5701, 0.8823]; 9/1 | 0.7535 [0.5215, 0.8823]; 10/0 |
| f_pk_hz | 41.5 [30.5, 49]; 10/0 | 32.75 [30, 49]; 10/0 | 49 [46.5, 51.5]; 9/1 | 55 [48.5, 68]; 10/0 |
| J_exit_run | -21 [-21, -6.475]; 6/4 | -21 [-21, -21]; 9/1 | -21 [-21, -21]; 2/8 | -20.12 [-21, -20.12]; 5/5 |
| J_exit_static | -2.53 [-2.53, -2.53]; 10/0 | -2.53 [-2.53, -2.53]; 10/0 | -2.53 [-2.53, -2.53]; 9/1 | -2.53 [-2.53, -2.53]; 10/0 |
| exit_delay | -18.47 [-18.47, -3.945]; 6/4 | -18.47 [-18.47, -18.47]; 9/1 | -18.47 [-18.47, -18.47]; 2/8 | -17.59 [-18.47, -17.59]; 5/5 |
| r_post_1s | 0.1083 [0.1038, 0.4758]; 6/4 | 0.0955 [0.08931, 0.09552]; 9/1 | 0.0958 [0.09162, 0.09998]; 2/8 | 0.1226 [0.1023, 0.1226]; 5/5 |
| r_post_5s | 0.1148 [0.1087, 0.5]; 6/4 | 0.0998 [0.09347, 0.09981]; 9/1 | 0.1 [0.09578, 0.1043]; 2/8 | 0.1312 [0.1066, 0.1312]; 5/5 |

Undefined reasons, N = 1000: J_exit_run: episode_unterminated_at_run_end: 4; exit_delay: episode_unterminated_at_run_end: 4; r_post_1s: episode_unterminated_at_run_end: 4; r_post_5s: episode_unterminated_at_run_end: 4.

Undefined reasons, N = 3000: J_exit_run: episode_unterminated_at_run_end: 1; exit_delay: episode_unterminated_at_run_end: 1; r_post_1s: episode_unterminated_at_run_end: 1; r_post_5s: episode_unterminated_at_run_end: 1.

Undefined reasons, N = 10000: J_exit_run: episode_unterminated_at_run_end: 7; exit_delay: episode_unterminated_at_run_end: 7; r_post_1s: episode_unterminated_at_run_end: 7; r_post_5s: episode_unterminated_at_run_end: 7; onset_s: no_episode: 1; eta_onset: no_episode: 1; delay_eta: no_episode: 1; duration_ms: no_episode: 1; duration_cycles: no_episode: 1; duration_frac_ramp: no_episode: 1; peak_power_abs: no_episode: 1; peak_power_rel: no_episode: 1; f_pk_hz: no_episode: 1; J_exit_run: no_episode: 1; J_exit_static: no_episode: 1; exit_delay: no_episode: 1; r_post_1s: no_episode: 1; r_post_5s: no_episode: 1.

Undefined reasons, N = 30000: J_exit_run: episode_unterminated_at_run_end: 5; exit_delay: episode_unterminated_at_run_end: 5; r_post_1s: episode_unterminated_at_run_end: 5; r_post_5s: episode_unterminated_at_run_end: 5.

## S10 and RB8, heterogeneity part (R8, E-7, E-8)

Claim limits: DL-229 and DL-258 b apply to every network class below (a network class is a class of the frozen mode-N classifier on the mean voltage v of one finite-N realisation; the primary reading is the Table 2.1 correspondence, the post-hoc reading does not count S-rel as a match for D-tr).

| shape | seed | class | correspondence level |
|---|---|---|---|
| lorentzian | 0 | S-sus | S-sus |
| lorentzian | 1 | S-abs | surge |
| lorentzian | 2 | S-sus | S-sus |
| gaussian | 0 | S-abs | surge |
| gaussian | 1 | S-abs | surge |
| gaussian | 2 | S-abs | surge |
| uniform | 0 | S-abs | surge |
| uniform | 1 | S-abs | surge |
| uniform | 2 | S-abs | surge |

Lorentzian classes ['S-sus', 'S-abs', 'S-sus']; C2 control classes beside the Lorentzian (N = 1e4, 60 s): S+ 1, S-sus 2; Lorentzian seeds in the mean-field-matching class: 1 of 3. **RB8 heterogeneity part: NOT EVALUABLE** (the 3 Lorentzian seeds do not share one Table 2.1 correspondence class); no pass or fail is made.

## G4 (R24, E-9; report-only for the run order)

Claim limits: DL-229 and DL-258 b apply to every network class below (a network class is a class of the frozen mode-N classifier on the mean voltage v of one finite-N realisation; the primary reading is the Table 2.1 correspondence, the post-hoc reading does not count S-rel as a match for D-tr).

| pool | records | missing | surge seeds (primary) | surge seeds without S-rel | misses |
|---|---|---|---|---|---|
| N = 10000 | 19 | 0 | 5 | 4 | False |
| S8:headline | 6 | 0 | 2 | 1 | |
| S9 | 10 | 0 | 2 | 2 | |
| S10:lorentzian | 3 | 0 | 1 | 1 | |
| N = 30000 | 10 | 0 | 5 | 5 | False |
| S9 | 10 | 0 | 5 | 5 | |

RB1: FAIL. Cells in disagreement, 2 or more: True. G4 triggered: True.

RB1 does not pass: G4 is evaluated.  
(1) Network misses the surge at N = 1e4 and 3e4 (no pooled seed at that N in a surge class): no -> if yes, report a finite-size limitation (Part 1, Table 4.2); keep the model.  
(2) Disagreement in 2 or more of the 4 cells: YES -> if yes, rerun RB6 (its network parts, the dt ladder and V_p, are S13 runs at MS11; R9). Known caveats: OA attraction with synaptic kinetics is unproven; shot noise causes metastability [R1, 2.6].  
(3) Report the affected results as mean-field-only: applies when (1) or (2) holds (our reading of the Table 11.2 sentence, UNVERIFIED).  
G4 is report-only for the run order (Table 11.2 footnote); it limits claims to the mean field, it stops nothing.  

## Not verified

A reference without f_pk or onset gives n/a and counts as met (R29, UNVERIFIED reading; does not arise for the headline). Control record sizes assume the ramp-run duration (UNVERIFIED). J_exit,static and the exit-delay sign follow 9i (UNVERIFIED, no gate).
