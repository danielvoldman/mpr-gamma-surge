# MS8 G6 evidence sheet

Written for: the reviewer who rules on G6. This sheet gives facts and the status of each item as the frozen text reads. It gives no verdict, and no pass or fail for G6 as a whole. It changes no frozen criterion or evaluation rule (tag `criteria-frozen`, criteria file SHA-256 c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05; secondary files S13 317db87e..., A4_grids cf6a60be..., S5_cells fe8590ce...).

Checks behind it (8g): an independent recomputation from the raw stored records (`scripts/recompute_ms8_independent.py`, which does not import `rb_eval`, `rb_tables` or `a7`) agrees with `rb_eval_ms8.json` on all 126 compared numbers and flags, exactly (bit-equal floats), and with the stored parquet on all 1800 run-level fields (360 runs x onset, raw crossing, two delays, class). One input of that script is not an npz series: the eigenvalue integral behind t_pred and eta_pred (item RB3(a)) comes from `entry_exit`, which is unchanged existing code. Output `results/A7/recompute_ms8_independent.json`, SHA-256 4d91aab379c98c88f649802b9f38e59e41b849c33c47a029139c6360983cfd50.

Source files and SHA-256 (all in `results/A7/`, git-ignored):

| Short | File | SHA-256 |
|---|---|---|
| EV | `rb_eval_ms8.json` | 96e9e51cad7ad3b7f32f8da9ac4d937f2bc7ec01b3d990c8374df139a4ba92d8 |
| DG | `rb_diag_ms8.json` | 3fb10f131efe6a40d19459629637aad74a5c2ab95bd9f9651c37835b4af197db |
| EX | `rb_diag_exploratory.json` | 8a388a556a93fc4a0330a2905c095e084b627e1b01e7487dbd00802c53ea2edf |
| SD | `rb_diag_startdist.json` | e16808ccad9949b6572ceb8c0fe9a9e3aa29a9eaa9893783f28ece25ee2fadd5 |
| BU | `rb_diag_burst.json` | a724b37eeddfd2eabf2391d05345f3578b28e949df65e0fa44fbaf4d9b960b39 |
| AT | `rb_diag_atol_seed.json` | 9471e7e088183a69b7ee63739fb65f815e1928117b7d95e62f99960edd3d1dd4 |
| PQ | `a7_ramp_metrics.parquet` | b3732bbb77cf97d0296148f4b8b5265921eb6db1388482f647a4fe24c0f269fa |
| RC | `recompute_ms8_independent.json` | 4d91aab379c98c88f649802b9f38e59e41b849c33c47a029139c6360983cfd50 |

## A. The G6 row of the plan (Table 11.2), quoted exactly

| Gate | Continue if | Stop or redirect if |
|---|---|---|
| G6 Ramp artefact | RB3(a) (on the runs inside its range; section 5.2, A7), RB3(b) and RB6 pass at the headline point; RB3(d) and RB5 are evaluated and reported | Class or floored delay depends on the solver (method or rtol; the Heun step for floored runs) → fix the numerics. Dependence on profile or δ₀ is slow-passage physics (section 4.4; RB3(d); RB5): reported, not fixed. Surge only outside 56–316 s → limit the claim |

"Fail" actions, by clause: (F1) class or floored delay depends on the solver (method or rtol; the Heun step for floored runs) → fix the numerics; (F2) dependence on profile or δ₀ → reported, not fixed; (F3) surge only outside 56–316 s → limit the claim.

## B. Items against the frozen bounds

Status words: MEETS and DOES NOT MEET are against a bound the frozen file states; REPORTED where the frozen text asks for a report only; NOT JUDGED where the frozen text says so; NOT IN MS8 RUNS where the check needs runs MS8 does not contain. "Reading" is primary (a labelled 8f2 ruling, section D) or alternative (kept beside it). Delays are signed, eta units, negative = onset advance.

| Clause | Item | Value | Frozen bound | Status as the frozen text reads | Reading used | Source |
|---|---|---|---|---|---|---|
| RB3(a) | testable in-range runs within one A4 step (grid step 0.025), raw first-crossing onset against t_pred | 0 of 6. Errors in A4 steps: P1 lin start dist 0.5 at T 1 s 33.15; 1.778 s 20.60; 3.162 s 12.68; 5.623 s 7.57; 10 s 4.40; P5 lin 1.778 s 25.07 | within 1 A4 step (all runs in range) | DOES NOT MEET | primary (ruling 2, ruling 1) | EV `RB3a.primary`; RC (e); DG |
| RB3(a) | in-range runs with eta constant at t_pred (no test of the grid-step tolerance) | 3 of 9 in range (P1 lin 1 s and 1.778 s; P1 sig 1 s, all start dist 1.5); time errors -0.289, -0.269, -0.266 s | as above | NO VERDICT (ruling 2) | primary | EV `RB3a.primary.constant_eta_runs_no_verdict` |
| RB3(a) | headline P2 linear 120 s | in range: no; I_min -1122.5; match error 65.95 steps | not judged at the headline (gate departure 3) | NOT JUDGED | frozen | EV `RB3a.headline` |
| RB3(b) | strict decrease of the median delay over the three floor levels (default Heun rung 1e-3 tau, 10 seeds each) | raw crossing: -0.000760, -0.042323, -0.105060 | strictly lower at each level, ties fail | MEETS | primary (ruling 1); the result is the same at all four rungs and with NaN excluded or propagated (no NaN) | EV `RB3b`; RC (b) |
| RB3(b) | same, classifier episode onset | -1.5, -1.5, -1.0917 (ties at levels 0 and 1) | as above | DOES NOT MEET | alternative (labelled) | EV `RB3b`; RC (b) |
| RB6 | Heun delay change, finest rung 1e-4 against default 1e-3, same 10 seeds, per floor level | relative change 0.0, 0.0, 0.0 at levels 0, 1, 2 (raw crossing and classifier onset); the 30 seed pairs have identical onsets (0 ms) | below 5 percent | MEETS | primary (ruling 1); exact 0 is a limit of the 1 ms output grid (ruling 7; bound is 1.3 output steps at level 0, 72.6 at level 1, 180 at level 2) | EV `RB6_heun`; RC (c); DG |
| RB6 | DOP853 against Radau, headline, class | D-tr and D-tr | solvers agree on class | MEETS | literal | EV `RB6_solvers`; RC (a) |
| RB6 | DOP853 against Radau, headline, onset | 58.698 s against 58.879 s: 181 ms (class onset and raw crossing alike); delay 0.066192 against 0.071471 | onset within 1 ms | DOES NOT MEET | primary (ruling 4, literal) | EV `RB6_solvers`; RC (a) |
| RB6 | noise-free DOP853 delay against rtol 1e-8, 1e-10, 1e-12 | 0.066192 at all three; onset 58.698 s at all three | reported against rtol, not a pass test | REPORTED | frozen | EV `RB6_solvers`; RC (a) |
| RB6 | halving the network dt changes f_pk by less than 2 percent; V_p +/-100 against +/-200 | no MS8 run (the S13 headline subset has no network runs) | below 2 percent | NOT IN MS8 RUNS | n/a | `docs/ms8_plan.md` (S13 headline subset) |
| RB3(c) | P2 linear noise-free at T_ramp 56.23, 100, 177.8, 316.2 s against the headline class D-tr | D-tr at all four | same class as the headline (F-18). Not named in the G6 row | MEETS | primary (ruling 5); readings A, B, C in section C | EV `RB3c`; RC (d) |
| RB3(d) | linear against sigmoid, class changes at the four T_ramp, per path | P1 2 (at 56.23 and 177.8 s), P2 0, P5 0 | at most 1 of the four (F-18) | REPORTED per path and T_ramp, no pooled verdict | primary (ruling 6) | EV `RB3d` |
| RB5 | delta0 1e-9, 1e-6, 1e-3 at the headline | class D-tr at all three; delay shift 0.0 at 1e-9 and 1e-3 against 1e-6 | class unchanged; delay shifts reported | MEETS (class); delay shifts REPORTED | frozen | EV `RB5.delta0_headline`; RC (a) |
| RB5 | start distance 0.5, 1.5, 3, P1 linear, 13 T_ramp | class unchanged at 4 of 13 T_ramp, changes at 9 of 13 (T_ramp 1, 3.162, 5.623, 10, 17.78, 56.23, 100, 177.8, 562.3 s) | class unchanged; delay shifts reported | REPORTED per T_ramp, no pooled verdict | primary (ruling 6) | EV `RB5.start_distance_P1_linear` |
| G6 fail clause | P2 surge classes inside and outside 56 to 316 s | see section G | surge only outside 56 to 316 s limits the claim | FACTS only | n/a | EV `P2_surge_class_counts`; RC (f) |

## C. Findings (one line each)

1. RB3(a) misses the A4 grid step on 6 of 6 testable in-range runs (errors 4.4 to 33.1 steps; observed raw crossing earlier than t_pred by 0.33 to 0.44 s on the five start-distance runs and 0.32 s on P5). Three more in-range runs have eta constant at t_pred and carry no verdict.
2. The RB6 solver clause misses as literally read: DOP853 and Radau onsets differ by 181 ms against 1 ms. The cause is unexplained (seed, burst, atol and ulp checks all negative; ruling of the reviewer: closed, carried as unexplained).
3. The RB3(b) verdict depends on the onset reading: raw first crossing MEETS (-0.000760, -0.042323, -0.105060); classifier episode onset DOES NOT MEET (-1.5, -1.5, -1.0917, ties at levels 0 and 1).
4. RB3(c) has three readings. A (every path against the headline class D-tr): holds for P2 and P5, linear and sigmoid, fails for P1 linear (D-sus, D-sus, D-sus, D-none) and P1 sigmoid (D-none, D-sus, D-none, D-none). B (four classes of one path and profile equal each other): same split. C (P2 linear only): holds.
5. P1 class changes with start distance at 9 of 13 T_ramp (P1 linear, start distance 0.5, 1.5, 3).
6. The P2 headline path class is unchanged at start distance 0.5, 1.5 and 3 (D-tr at all three; supplementary runs, section E).
7. The delay falls with start distance on the headline path: +0.1721, +0.0662, -0.0647 eta at start distance 0.5, 1.5, 3 (shift against the headline +0.1059 and -0.1309).

## D. The eight 8f2 clarifications (DL-186) and where each is used

| No. | Clarification | Used in |
|---|---|---|
| 1 | RB3(b) and RB6 delays use the raw first-crossing onset as primary; the classifier-onset reading stays, labelled | section B rows RB3(b), RB6 Heun; section C item 3; section G (floored delay) |
| 2 | RB3(a): judge the testable in-range runs only (6 of 9); runs with eta constant at t_pred get time errors and no verdict | section B rows RB3(a); section C item 1 |
| 3 | P1 linear start distance 0.5 has 5 in-range T_ramp against the frozen "0 to 2 of 13" (reasoned at start distance 1.5; frozen text unchanged) | section F departure 3; section B RB3(a) |
| 4 | DOP853 against Radau: the frozen text is applied literally; any amendment is a new departure | section B row RB6 solvers; section C item 2; section G (method) |
| 5 | RB3(c) gating input is the headline path (P2 linear noise-free) at the four T_ramp; readings A and B beside it as information | section B row RB3(c); section C item 4 |
| 6 | RB3(d) and RB5 reported per path and per T_ramp, no pooled verdict | section B rows RB3(d), RB5; section C items 5 to 7; section G (profile, delta0) |
| 7 | The RB6 Heun exact 0 is a limit of the 1 ms output grid, not extra evidence | section B row RB6 Heun; section G (Heun step) |
| 8 | Floor-run delays are signed (negative = onset advance) | section B rows RB3(b), RB6; section G |

## E. Supplementary and exploratory items (none feeds a gate; none is in the S5 or S13 manifests)

| Step | Label | What | Result | Source |
|---|---|---|---|---|
| 8f3 Set A (DL-191, DL-192) | EXPLORATORY | P1 start distance 0.5 linear, T_ramp 1 s and 10 s, delta0 1e-9 and 1e-3 (4 runs) | The onset does not follow the kick: identical for 1e-9 and 1e-6; at 1e-3 it is 7 ms (T 1 s) and 60 ms (T 10 s) later | EX |
| 8f3 Set B (DL-191, DL-193) | EXPLORATORY | headline start state moved by +1 and -1 ulp (2 runs) | onset 58.698 s in all three; spread 0.0 ms against 181 ms | EX |
| 8f4 (DL-194, DL-195) | SUPPLEMENTARY | headline cell at start distance 0.5 and 3 (2 runs) | class D-tr at both; raw onset 37.260 s and 75.448 s (58.698 s at 1.5); delay shifts +0.1059 and -0.1309 eta | SD |
| 8f5 (DL-196 to DL-199) | EXPLORATORY | burst diagnosis from stored data; clean-tree re-run of the 8f3 sets | the burst is a deterministic response at path breakpoints and the onset is not burst-seeded; Radau / DOP853 burst peak ratio 0.99999997; the six re-runs are bit-identical (git dirty false); no Radau proposal | BU |
| 8f6 (DL-200 to DL-202) | EXPLORATORY | headline cell at atol 1e-10 and 1e-14 (2 runs); effective seed against the ramp-kink burst | onset 58.698 s at atol 1e-10, 1e-12, 1e-14 (0 ms shift): the atol reading is not supported; effective seed against burst peak NOT SEPARABLE in 13 of 13 runs | AT |

The P5 1.778 s burst-seeded prediction (DL-202) uses an extrapolated burst amplitude and stays labelled UNVERIFIED. It is not cited as evidence anywhere in this sheet.

## F. The four frozen gate departures (DL-163) and the MS8 evidence that touches each

| No. | Departure | MS8 evidence that touches it |
|---|---|---|
| 1 | D8: the plan estimator fails 2 of 8 A8 ring items; every D8-dependent class is provisional | 359 of the 360 stored runs carry the label "provisional (D8 open, DL-137)", including every class in sections B, C and G (the one run without it reached its class without a D8 call) |
| 2 | Zero baseline, including noise-free inputs: no "undefined" mode-N class | The 109 mode-D runs use the absolute threshold and no baseline test. The 250 mode-N runs have noise at sigma > 0 (130 S5 noise runs, 120 floor runs). Whether any mode-N baseline is zero was not checked per run (UNVERIFIED) |
| 3 | RB3(a) is not judged at the headline (coverage 0 to 2 of 13 T_ramp per path and profile) | headline not in range (I_min -1122.5, 65.95 steps); P1 linear start distance 0.5 has 5 in-range T_ramp (ruling 3); P1 linear 1.5: 2, P1 sigmoid 1.5: 1, P5 linear 1.5: 1; P2 linear and sigmoid, P5 sigmoid, P1 linear start distance 3: 0 |
| 4 | Pure trend plus noise at W = 0.2 s fails "pure trend -> NS"; short-window false surges on white noise (306, 400, 172, 24 of 500 at W 0.2, 0.333, 0.593, 1.054 s) | mode-N P2 runs at T_ramp 1 to 5.623 s (W = 0.2 s), 10 s (0.333), 17.78 s (0.593), 31.62 s (1.054): surge classes in 6, 7, 7, 8, 2, 2, 3 of 10 seeds at T_ramp 1, 1.778, 3.162, 5.623, 10, 17.78, 31.62 s; these lie outside 56 to 316 s, where W = 1.874 s (56.23 s) and 2 s |

## G. Facts for each "Fail" clause (facts only; no verdict)

| Question | Answer | Numbers |
|---|---|---|
| Class depends on the solver (method) | no | DOP853 D-tr, Radau D-tr (headline) |
| Class depends on the solver (rtol) | no | D-tr at rtol 1e-8, 1e-10, 1e-12 |
| Class depends on the Heun step (floored runs) | no | class counts per level equal at all four rungs (1e-3, 5e-4, 2.5e-4, 1e-4 tau): level 0: 10 S-abs; level 1: 10 S-abs; level 2: 5 S+, 1 S-abs, 2 S-rel, 2 S-sus |
| Floored delay depends on the Heun step | no, at the 1 ms output grid | relative change 0.0 at the three levels; 0 ms onset difference in 30 of 30 seed pairs; bound resolves 1.3 steps (level 0), 72.6 (level 1), 180 (level 2) |
| Noise-free DOP853 delay depends on rtol | no | 0.066192 at 1e-8, 1e-10 and 1e-12; difference 0.0 |
| Noise-free onset depends on the method | yes | 181 ms (58.698 s DOP853, 58.879 s Radau); delay 0.066192 against 0.071471 (difference 0.005279 eta); unexplained |
| Dependence on delta0 | headline: none; exploratory, small and not following the kick | headline class D-tr and delay shift 0.0 at 1e-9, 1e-6, 1e-3; Set A: 0 ms at 1e-9, +7 ms and +60 ms at 1e-3 |
| Dependence on profile | P1 yes, P2 and P5 no | class changes linear against sigmoid at 2 of 4 T_ramp (P1), 0 of 4 (P2), 0 of 4 (P5) |
| Dependence on start distance | P1 yes (class); headline path class no, delay yes | P1 class changes at 9 of 13 T_ramp; headline D-tr at 0.5, 1.5, 3, delay +0.1721, +0.0662, -0.0647 |
| Surge only outside 56 to 316 s | no, in both modes | Mode D, P2 linear: surge class (D-tr) in 4 of 4 runs inside, 9 of 9 outside; P2 sigmoid: 4 of 4 inside, 8 of 9 outside (T_ramp 1 s is D-none). Mode N, P2 linear 10 seeds (surge classes S+, S-rel, S-abs): 26 of 40 runs inside, 53 of 90 outside; every T_ramp has at least 2 of 10 seeds with a surge class. S-sus is not counted as a surge class |
