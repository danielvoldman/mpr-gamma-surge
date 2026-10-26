# MS10 close (10g)

Written for: the reviewer and owner who close MS10, and the author of the paper's limitations section. MS10 is closed on paper (DL-324 to DL-326, DL-329): **sigma check NOT INSIDE (limitation; sigma stays frozen), RB1 FAIL (headline 10 s FAIL, 120 s FAIL, cells 1 of 4 FAIL, N rule PASS), RB8 heterogeneity part NOT EVALUABLE, G4 triggered by consequence (2), report-only for the run order.** The MS10 gate of Table 11.1 is not restated here; the verdicts above are the pre-registered wording of 10f (R30). No simulation of any kind was run at 10g, no tag was made, nothing was pushed, and no frozen criterion, list, config or evaluator choice changed (tag `criteria-frozen`, commit dd8330c5eaacd63d21e7b7969430988d00862769, criteria SHA-256 c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05; S13 317db87e, A4_grids cf6a60be, S5_cells fe8590ce). Numbers are those of `docs/ms10_g_evidence.md` (SHA-256 8ffc2858e70c0e2288ac13554f2dc8412b6194ea559765cfb454d41a731b45c4), `docs/ms10_results.md` (55a7d1af44bee7f390e0705388dd503f0e2112e9f8f12c7f88450cc512e4a98b) and the decision log (DL-273 to DL-329). The hash of every MS10 result file, frozen list, config, evaluator, test and doc is in `docs/ms10_file_hashes.csv` (436 entries, SHA-256 053c63916ab536a5a3672dd6c1a5c7797a79fa20e2b419840c1d94019949ca10; table digest 9a7825c9870b2311132efa2869aca5ee014c46d6bd249aa31e10bddef34045cb). The SHA-256 of this file is in DL-329.

## (a) Sub-steps and commits

| Step | Commits | Content (DL) |
|---|---|---|
| 10a | 586a423, 0e56045, c9d70ef | run counts, prediction arithmetic, proposed seed keys, network timing sample, `docs/ms10_plan.md` with M10-1 to M10-16 open (DL-273 to DL-276) |
| 10b | afb7371 | rulings R1 to R9; Gaussian and uniform heterogeneity offsets; stored mean-field reference inventory and S8 candidate table (DL-277 to DL-287) |
| 10c | 5bb9244 | draft pre-registration, run lists S8/S9/S10/C2/MF companion, launcher, 12 S8 cell proposals, timing gate; R10 to R19 (DL-288 to DL-300) |
| 10d | d42f4fc, 0bb6d7b | S8 cells (R20), lists and configs FROZEN, evaluators and rules text; R21 to R24; five mean-field companion runs (DL-301 to DL-309) |
| 10e | 324a8d8 | R25 to R28, evaluation choices E-1 to E-10, evaluators amended, launch readiness (DL-310 to DL-315) |
| 10f | 81d6be6 | six lists launched by the reviewer at 324a8d8 and verified (103 records ok); evaluators run as frozen; R29 (DL-316 to DL-323) |
| 10g | the commits that add DL-324 to DL-329, `docs/ms10_g_evidence.md`, `docs/ms10_file_hashes.csv`, `scripts/ms10_independent_check.py`, `scripts/hash_ms10_results.py` and this file | close on paper; independent recomputation; no simulation |

## (b) What MS10 ran

| List | Runs | Launch wall | Predicted |
|---|---|---|---|
| S8 (network, headline T_ramp 10 s and 120 s, 3 seeds each; 4 map cells at 30 s, 3 seeds each) | 18 | 333.6 s (5.56 min) | 5.4 min |
| C2_S8 (constant-parameter controls) | 18 | 320.3 s (5.34 min) | 5.4 min |
| S10 (Lorentzian, Gaussian, uniform, N = 1e4, 60 s, 3 seeds each) | 9 | 192.9 s (3.22 min) | 3.0 min |
| C2_S10 | 6 | 157.4 s (2.62 min) | 3.0 min |
| S9 (N = 1e3, 3e3, 1e4, 3e4, 10 seeds each, 60 s) | 40 | 825.0 s (13.75 min) | 14.1 min |
| C2_S9 | 12 | 326.7 s (5.44 min) | 9.9 min |
| Network total | 103 | 2,155.9 s (35.9 min) | |
| MF_COMPANION (mode D; 4 cells at 30 s, headline at 60 s) | 5 | 69.7 s | 88 s to 2.8 min |

All 108 runs ok, 0 failed, git dirty false, commit 324a8d8 (companion: after d42f4fc). No other run was made at MS10: no diagnostic, no exploratory run, no RB6 rerun (R32).

## (c) Verdicts as logged (pre-registered wording; R30)

| Item | Verdict | Numbers | Source |
|---|---|---|---|
| Sigma check | NOT INSIDE (limitation; sigma stays frozen) | reference 0.039522 above the six network baselines 0.037989 to 0.038920 (mean 0.038455); 0.000602 above the maximum | DL-318, DL-310 |
| RB1, headline 10 s | FAIL | 0 of 3 seeds pass (S-abs, S-rel, S-sus; f_pk 93.09, 60.06, 48.05 Hz against 48.05; classifier onset 5.176, 6.178, 8.684 s against 10.604) | DL-319 |
| RB1, headline 120 s | FAIL | 0 of 3 (S-sus x3; f_pk 49.0, 48.5, 49.0 Hz met; classifier onset 12.0 s against 58.698) | DL-319 |
| RB1, cells | FAIL | 1 of 4 cells agree (need 3); (7, 4) agrees, (22, 10) 2 of 3, (13, 29) 0 of 3, (24, 26) 0 of 3 | DL-320 |
| RB1, N rule | PASS | seeds in the matching class: 2 at N = 1e4, 5 at N = 3e4 | DL-320 |
| RB1, overall | FAIL (failing RB1 is G4) | headline FAIL / FAIL, cells FAIL, N rule PASS | DL-320 |
| S9 | facts, no threshold | classes per N and Table 2.1 metrics in `docs/ms10_results.md` | DL-321 |
| RB8, heterogeneity part | NOT EVALUABLE | Lorentzian S-sus, S-abs, S-sus (no common level); Gaussian S-abs x3, uniform S-abs x3 reported | DL-322 |
| G4 | triggered by consequence (2), report-only | (1) network misses the surge at 1e4 and 3e4: no (5 of 19 and 5 of 10 pooled seeds in a surge class); (2) 3 of 4 cells disagree: YES; (3) mean-field-only reading applies (UNVERIFIED) | DL-323 |

Independent recomputation (DL-327, DL-328): 103 records, 282 items compared with `docs/ms10_results.md`. First pass (references at full precision): 4 DIFFERENCE, all from the frozen rounded constants (sigma position in range 1.6461 | 1.6465, gap 3.04e-4; sigma reference over network mean 1.0277 | 1.0278, gap 7.4e-6; RB1 10 s seed 2 f_pk relative error 0 | 4.062e-05; difference in bins 0 | -0.0006507, gap 1.952e-3 Hz; constants' gaps 2.83e-7 and 1.95e-3 Hz, below their rounding); no class, per-seed verdict, count or gate verdict differs. Second pass (frozen constants 0.039522, 48.05 Hz, 49.0 Hz): 0 DIFFERENCE. The check shares the frozen classifier, the criteria loader, the path definitions and, for J_exit,static, the 9i function with the original evaluation, so it cannot show a classifier error.

## (d) Departures and post-hoc items

Readings that are ours (UNVERIFIED as plan readings): R23, R24, R18, R26 (E-1 to E-10 as ruled), R29, and G4 consequence (3). Network onset is the classifier window centre (R27); the raw-crossing onset is secondary and post hoc. The post-hoc readings (S-rel not counted, median f_pk and onset) feed no gate. The DL-120 sigma value 0.038852 is not used (R25). Uniform offsets max |q| = (N-1)/(N+1) (R10); the Gaussian quantile offsets lack the tails beyond u = 1/(N+1) (R11). Both D-tr S8 cells have short tau_d (R20); cell (24, 26) has no Hopf point. Control record sizes assume the ramp-run duration (UNVERIFIED). Full list: `docs/ms10_g_evidence.md` section 5.

## (e) Claim limits to carry to the paper

MS10 (R31, DL-325):

1. **G4-C1.** Under the frozen mode-N criteria the network at N = 1e4 and 3e4 does not reproduce the mean-field classes at the headline (0 of 3 seeds at each of T_ramp 10 s and 120 s) or at the 4 map cells (1 of 4 agree).
2. **G4-C2.** The surge result is stated for the mean field only (G4 consequence 3; this reading is UNVERIFIED); no claim of robustness to finite-size fluctuations.
3. **G4-C3.** No-ramp network controls are classified into surge classes (10 s headline S-abs and S-rel; S9 N = 3e3 and 1e4 S+; cell (24, 26) S+), so network classes under the frozen criteria cannot separate ramp-driven from non-ramp records (DL-229, DL-231).
4. **G4-C4.** Sigma 0.0624 is checked and not confirmed (the mean-field baseline std lies above all six network baselines). Noisy mean-field results are labelled accordingly; sigma stays frozen.
5. **G4-C5.** No claim about heterogeneity-shape robustness (RB8 not evaluable).
6. **G4-C6.** The RB6 rerun named in G4 is read as the network part of S13 at MS11 (UNVERIFIED reading; RB6's mean-field parts were done at MS8).

Carried unchanged from MS9 and MS8 (`docs/ms9_close.md`, `docs/ms8_close.md`): G7 not passed (DL-229, DL-230); RB2 / D24 failed, no claim that the regime map is robust to noise, S-rel not counted as ramp evidence in mode N (DL-242, DL-250; the MS9 wording "sigma 0.0624 UNVERIFIED until S8" is superseded by G4-C4); every D8-dependent class provisional, A_ref reading (a) 2.176222; G6-D1 to G6-D3; the A9 labels are our operational rules (M9-12) and label (c) is a flag (DL-270); the D31 boundary definition is ours (DL-254); J_exit,static on P3 and P4 is our extension (DL-263); the P3 cost 1.57 x the headline; the Defender exclusion user-reported only (DL-142).

## (f) Open housekeeping

| Item | State |
|---|---|
| Sigma 0.0624 | was "UNVERIFIED until S8"; now checked, not confirmed (G4-C4); frozen, not changed |
| K5 (DL-064, DL-082) | own reading, UNVERIFIED, deferred (unchanged) |
| K10 (DL-131 to DL-133) | definition kept, single-source claim UNVERIFIED (unchanged) |
| K4-net coupling (MC-03) | unsourced; the networks use the M3 network, not the M2 coupling (unchanged) |
| D37 storage decision | open to MS15 (DL-223). MS10 result volume 450.9 MB (321 files; the 10e estimate 0.24 GB was low by a factor 1.9, UNVERIFIED); disk free now 153 GB (`df`, C: 930 GB, 84% used; the 10e figure was 81.4 GB, the difference is not explained, UNVERIFIED) |
| Tags and pushes | none created, none pushed |

## (g) Measured compute and the D36 cap

Recorded MS10 walls: 2,155.9 s for the six network lists (35.9 min) and 69.7 s for the companion, 2,225.6 s (0.618 h) in all. D36 cap check (24 h, whole table), arithmetic on logged figures: MS9 13.595 h + 0.618 h = **14.21 h, conservative, UNVERIFIED**, margin 9.79 h (the 10c figure with predicted walls was 14.11 h). Mixed bases, not a measured cumulative wall; analysis, evaluation, recomputation and test time are not included. Cut order 9.3 is not triggered by the arithmetic. Test suites at 10g: see DL-329.

## (h) Carried to MS11

1. **DL-251 (NOT decided):** RB2 and S11 need a constant-parameter control at the headline cell for each sigma; to be planned at the start of MS11 and labelled a POST-HOC AMENDMENT; nothing run or listed.
2. **G4-C6:** the RB6 rerun named in G4 is read as the network part of S13 (UNVERIFIED reading); the RB6 mean-field parts were done at MS8. Any such run comes to the reviewer first.
3. **G4-C3 and DL-231:** network class statements need a constant-parameter control at each network configuration; MS10 carried one per configuration (C2) and reported the control classes beside the ramp classes; the frozen criteria do not use them.
4. Sigma stays 0.0624 (frozen, MS7); noisy mean-field results are labelled "sigma checked, not confirmed" (G4-C4).
5. The MS10 claim limits G4-C1 to G4-C6 and the carried MS9 and MS8 limits apply to every MS11 statement that uses a network record or a noisy mean-field record.
6. Open items unchanged: K5, K10, K4-net, D37 at MS15.
