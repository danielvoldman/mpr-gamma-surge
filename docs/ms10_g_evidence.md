# MS10 evidence sheet for sigma check, RB1, RB8 and G4 (facts and logged rulings only)

Status: written at 10g from the stored records, `docs/ms10_results.md` (10f), the decision log (DL-273 to DL-329) and the independent recomputation (DL-327, DL-328). Nothing was simulated or launched at 10g. This sheet adds no ruling and no verdict: every verdict is the pre-registered wording of 10f (R30, DL-324); where a ruling exists it is quoted with its DL number. `docs/plan.md` is not edited. Anything that is our reading is marked UNVERIFIED.

Frozen state: tag `criteria-frozen` (commit dd8330c5eaacd63d21e7b7969430988d00862769), criteria SHA-256 c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05, secondary files S13 317db87e69afcb09111a33e78640869b3f588e64390d110655aaa3a7cff52388, A4_grids cf6a60bec781c6f7e53b7f92b747ff745fcc5dc4794c0b83768e0aa4a4e56401, S5_cells fe8590ce81bc8c537f9c92e2afbee80685aaaa52c757474912b243fe9ed38790; the loader verified the freeze at the start of 10g. Frozen threshold 0.217622. MS10 lists, cells, references and run configs FROZEN at 10d (DL-308); `configs/ms10/ms10_eval.yaml` amended at 10e (DL-314) to 29820b066d048c435c3deacf4f07c17f59555d4f377527c8da585bb6a900cabb; `docs/ms10_eval_rules.md` d75d1edb6de9af67d25f077807f2cdec2b47a966aed7d4295f4d5abffc60c6b0; `docs/ms10_results.md` 55a7d1af44bee7f390e0705388dd503f0e2112e9f8f12c7f88450cc512e4a98b. All 103 records: status ok, git dirty false, commit 324a8d8, config hash and name equal to the frozen list row (DL-317). Claim limits: DL-229 and DL-258 b apply to every network class (a class of the frozen mode-N classifier on the mean voltage v of one finite-N realisation).

## 1. Gate statements and the facts behind them

| Item | Pre-registered criterion (source) | Found | Verdict | Records |
|---|---|---|---|---|
| Sigma check | The mean-field baseline std of v (0.039522, E-10 / R25, MS7 record `S5base_0000_1fe2ceaa1659`: mean over 10 seeds of the std of v over samples [0, 5000), ddof 1) lies inside the range, ends included, of the network baseline std over the 6 S8 headline runs, same window (R16, R28, E-4, E-5). If not, a limitation; sigma stays frozen (MS7) | Network baselines 0.037989 (2 runs), 0.038455 (2), 0.038920 (2); 3 distinct values; the 10 s and 120 s baselines of each seed are identical. Range 0.037989 to 0.038920, mean 0.038455. The reference is 0.000602 above the maximum; position in the range 1.6465 (0 at the minimum, 1 at the maximum); reference / network mean 1.0278 | NOT INSIDE (limitation; sigma stays frozen); sigma changed: False | S8_head_0000 to 0005 (section 8.1); reference record `results/S5/baseline/S5base_0000_1fe2ceaa1659`, json sha256 2329991bbd6b1d1f05d677b1d41d62fd22037da1fa362f13993f92c7f2242e83, npz af8f3262043bb65d6a60591e410d243e6152005ab2a9a077bc7a7a6d9816a50c |
| RB1, headline T_ramp 10 s | Per seed, 3 of 3 needed (frozen `classes_agree_seeds`): same class as the stored mode-D mean field under the Table 2.1 correspondence; f_pk within 5% (frozen `f_pk_rel_tol`, inclusive); classifier onset within one spectrogram step (1/6 s), inclusive (R23, R26, R27). Reference D-tr, f_pk 48.05 Hz, onset 10.604 s | Seed 0 S-abs (class met), f_pk 93.09 Hz (15.0 bins of 3 Hz off, not met), onset 5.176 s (not met). Seed 1 S-rel (class met), f_pk 60.06 Hz (4.0 bins off, not met), onset 6.178 s (not met). Seed 2 S-sus (class not met), f_pk 48.05 Hz (met), onset 8.684 s (not met). 0 of 3 pass (0 of 3 without S-rel). C2 controls at 10 s: S-abs 2, S-rel 1 | FAIL | S8_head_0000 to 0002; reference `p2_linear_0004_4f4756348cd8`, json sha256 3f94a9056a83b746770c64dd17c3d7b656282ac70fbe236a57e428ae6c57a33e; controls S8_ctrl (section 8.1) |
| RB1, headline T_ramp 120 s | Same; reference D-tr, f_pk 49.0 Hz, onset 58.698 s, step 1 s | Seeds 0 to 2 S-sus (class not met); f_pk 49.0, 48.5, 49.0 Hz (met); classifier onset 12.0 s in all three (not met, 46.7 s early). 0 of 3 pass. C2 controls at 120 s: S-sus 3 | FAIL | S8_head_0003 to 0005; reference `S5ramp_0000_240de3ef73be`, json sha256 31bb428655b030e8784cbb47d3567f9dda08913d56315eb36327b9fb28ea2b27 |
| RB1, cells | At least 3 of 4 S8 map cells agree; a cell agrees only if 3 of 3 seeds are in the class matching the companion mode-D class at 30 s (frozen `classes_agree_cells`, R15) | (7, 4) D-tr: S-abs, S-abs, S-rel, 3 of 3, agrees. (22, 10) D-tr: S-sus, S-abs, S-abs, 2 of 3. (13, 29) D-none: S-abs, S-rel, S-abs, 0 of 3. (24, 26) D-none: S-sus, S-sus, S-abs, 0 of 3. Agreeing 1 of 4 (0 without S-rel). Control classes: (7, 4) S-sus 2, S-abs 1; (22, 10) S-sus 2, S-abs 1; (13, 29) NS 2, S-rel 1; (24, 26) S-abs 1, S-rel 1, S+ 1 | FAIL | S8_cells_* (12) and the companion records S8_mf_cells_0000 to 0003 (section 8.1) |
| RB1, N rule | Seeds in the mean-field-matching class at N = 3e4 at least as many as at N = 1e4 (S9, 60 s, 10 seeds each; companion class D-tr) (R18) | N = 1e4: 2; N = 3e4: 5 (same without S-rel) | PASS | S9_* (40) and the companion S8_mf_head60_0000 |
| RB1, overall | PASS only if both headline T_ramp, the cells and the N rule pass; failing RB1 is G4 (frozen `on_fail`) | headline FAIL / FAIL, cells FAIL, N rule PASS | **FAIL** | as above |
| RB8, heterogeneity part | Gaussian and uniform each give the Lorentzian network class in 3 of 3 seeds (frozen); compared with the Lorentzian reference only if the 3 Lorentzian seeds share one Table 2.1 correspondence class (E-7, E-8) | Lorentzian S-sus, S-abs, S-sus (levels S-sus and surge); Gaussian S-abs x3; uniform S-abs x3. Lorentzian N = 1e4, 60 s C2 control: S-sus 2, S+ 1. Lorentzian seeds in the mean-field-matching class: 1 of 3 | NOT EVALUABLE (no pass or fail); M4 and adaptation parts of RB8 are MS12 | S10_* (9), S9_ctrl N = 1e4 (section 8.1) |
| G4 | If RB1 fails: (1) network misses the surge at N = 1e4 and 3e4: finite-size limitation, keep the model; (2) disagreement in 2 or more of the 4 cells: rerun RB6, whose network parts are S13 runs at MS11 (R9); (3) report the affected results as mean-field-only (our reading, UNVERIFIED); report-only for the run order (R24, E-9, plan Tables 4.2 and 11.2) | Pools (surge seeds / records, primary): N = 1e4 5 of 19 (S8 headline 2 of 6, S9 2 of 10, S10 Lorentzian 1 of 3; 4 without S-rel); N = 3e4 5 of 10 (S9; 5 without S-rel); no record missing. (1) no. (2) YES, 3 of 4 cells disagree. (3) applies (UNVERIFIED reading) | TRIGGERED by consequence (2); report-only; stops nothing | S8_head_*, S9_*, S10_* |

S9 (finite size) is reported without a threshold (E-6); the tables are in `docs/ms10_results.md`. Classes per N over 10 seeds: N = 1e3 S-sus 6, S-abs 4 (controls NS 3); 3e3 S+ 6, S-sus 3, S-abs 1 (controls NS, S+, S-abs); 1e4 S-sus 7, S-abs 2, NS 1 (controls S-sus 2, S+ 1); 3e4 S-sus 5, S-abs 5 (controls S-sus 2, S-abs 1). Unterminated episodes at the record end (J_exit,run, exit delay and post-surge rates undefined): 4, 1, 7, 5 seeds; N = 1e4 has one seed with no episode.

## 2. Launch table: records and walls against predictions

The six network lists were launched by the reviewer at commit 324a8d8 with `scripts/run_ms10_list.py --workers 10` (DL-317); predictions are the 10c alone-pool predictions from the 10a rates (DL-300, DL-315). The mean-field companion was run by Claude Code after the freeze commit d42f4fc (DL-309).

| List | Runs | Launch wall (s) | Wall (min) | Predicted (min) | List SHA-256 (DL-308) |
|---|---|---|---|---|---|
| S8 | 18 | 333.6 | 5.56 | 5.4 | 7f409c15cffa37c0462684f67d2b82fe5ba0fa305ea53fad8861197bc5647854 |
| C2_S8 | 18 | 320.3 | 5.34 | 5.4 | 172280421c9e2577f4029091e9b75511a17b18b8595e5e56256eed8b534a72e1 |
| S10 | 9 | 192.9 | 3.22 | 3.0 | 79f72a123467ccb0e79c327b7f82b0bd599dc5277cb37dc94466d0409eea94f3 |
| C2_S10 | 6 | 157.4 | 2.62 | 3.0 | d1047ee1f6dc35442a59b17e6b2df233360ebcdccb6abdf26f021d95946b925d |
| S9 | 40 | 825.0 | 13.75 | 14.1 | b429cff50ae112f1ac131ee42cac124a1a3a6a3a8aee900cf0fdbc85d7ed65bb |
| C2_S9 | 12 | 326.7 | 5.44 | 9.9 | 5745e197a662b9af2411c8444b4450d85e17b41c48b38b6f8acfa5b4254e0de4 |
| **Network total** | **103** | **2,155.9** | **35.9** | | |
| MF_COMPANION (mode D) | 5 | 69.7 | 1.16 | 1.5 to 2.8 | c22eca68e3231d64d8d7bc68d6bc6e284e8b22d4951522f0d9111979e30466a9 |

All 108 runs ok, 0 failed, git dirty false. The network total is the sum of the six logged launch walls (arithmetic).

## 3. D36 cap check (24 h, whole table), conservative, UNVERIFIED

Arithmetic on logged figures, as at 9j: the MS9 total 13.595 h (`docs/ms9_g_evidence.md` section 3, 13.60 h) plus the recorded MS10 launch walls 2,155.9 s + 69.7 s = 2,225.6 s = 0.618 h gives 14.21 h against 24 h; margin 9.79 h. The 10c figure was 14.11 h with predicted walls (DL-300). It is a sum of mixed bases (recorded walls, Table 9.1 upper bounds, one prediction), not a measured cumulative wall; analysis, evaluation, recomputation and test time are not included. Cut order 9.3 is not triggered by the arithmetic.

## 4. Independent recomputation (DL-327, DL-328)

`scripts/ms10_independent_check.py` is a separate code path that reads stored records only (no import of the MS10 evaluator, run-list module, results writer or MS9 classify module). It calls the frozen classifier, the frozen criteria loader, the run-path definitions (eta, J) and, for J_exit,static only, the 9i function (not independent). It recomputed the class of all 103 records (S8 18, C2_S8 18, S10 9, C2_S10 6, S9 40, C2_S9 12), the sigma-check statistics, the RB1 per-seed and per-cell tables, the N rule, the S9 class counts, undefined counts and Table 2.1 metrics, S10 and RB8, and the G4 pools and triggering, and compared 282 items with the cells of `docs/ms10_results.md`.

**First pass (kept as found; references recomputed at full precision): 271 MATCH, 7 MATCH at the last printed digit, 4 DIFFERENCE.**

| # | Item | Independent path | docs/ms10_results.md | Gap |
|---|---|---|---|---|
| 1 | Sigma check, position of the reference in the range | 1.646148587546253 (printed 1.6461) | 1.6465 (exact with 0.039522: 1.6464528972) | 3.04e-4 exact; 4e-4 as printed |
| 2 | Sigma check, reference / network mean | 1.0277473597715443 (printed 1.0277) | 1.0278 (exact with 0.039522: 1.0277547279) | 7.4e-6 exact; 1e-4 as printed |
| 3 | RB1 headline 10 s, seed 2, f_pk relative error | 0 | 4.062e-05 | 4.06e-5 |
| 4 | RB1 headline 10 s, seed 2, f_pk difference in bins | 0 | -0.0006507 | 6.5e-4 bins (1.952e-3 Hz at 3 Hz per bin) |

The seven last-digit matches have the same cause: 10 s seed 0 relative error 0.9375 against 0.9374 and difference in bins 15.02 against 15.01; seed 1 relative error 0.25 against 0.2499 and difference in bins 4.004 against 4.003; bin width printed 3 against 3.0 (seeds 0, 1, 2). **Cause:** the evaluator uses the frozen rounded constants (E-10 sigma reference 0.039522; stored_class f_pk 48.05 Hz at 10 s and 49.0 Hz at 120 s); the first pass used the unrounded values (sigma reference 0.03952171666266689; f_pk 48.048048048048045 Hz at 10 s, 49.0 Hz at 120 s). The gaps of the constants are 2.833e-7 (rounding of a 6-decimal constant about 5e-7) and 1.952e-3 Hz (rounding of 48.05 about 5e-3 Hz); 49.0 has no gap. No class, per-seed verdict, count or gate verdict differs.

**Second pass (frozen constants, `--frozen-constants`): 279 MATCH, 3 MATCH as text (bin width 3 against 3.0), 0 DIFFERENCE.** Per-record classes are identical to the first pass. Reports: `results/ms10/10g/independent_report_pass1.txt` 4528808b601cb6d17bff1d8dee5ea8d5cdafb7326a4356424f3e633a8f6b1284; `independent_report_pass2.txt` 4ec5a6fdd0fd0c2d49ee4f730072d4d59f3cc60209065140830005f395447bb8; `record_classes.tsv` ba791914888d66fc2fb15b9ec00c053cbbc8394717b2c6a1f7e8ed72c5802ced. Limit: the check shares the frozen classifier, the criteria loader, the path definitions and the 9i function with the original evaluation and re-reads the same rules text, so a classifier error or a misreading of the rules would not show (as for DL-267).

## 5. Departures from the plan and post-hoc items (all logged)

1. Readings that are ours (UNVERIFIED as plan readings): R23 (per-seed f_pk and onset tests; the plan gives no seed counts for them), R24 (what "misses the surge" means), R18 (N rule class-based), the E-1 to E-10 choices as ruled (R25 to R28), G4 consequence (3) "mean-field-only", and R29 (a reference without f_pk or onset counts as met; a pool with a missing record and no surge seed is not evaluable; 1e-9 floating-point slack; both post-surge windows kept; J_exit,static and the exit-delay sign follow 9i). The control record sizes assume the ramp-run duration (UNVERIFIED).
2. Network onset (R27): the classifier onset (window centre) against the mean-field raw-crossing onset; the evaluator's raw-crossing reading is secondary and post hoc and feeds no gate (10 s: 9.767, 9.594, 9.555 s, 0.84 to 1.05 s before the reference, none within one step; 120 s: 50.92, 50.17, 50.86 s, 7.8 to 8.5 s early). The network and mean-field time origins differ by one sample stamp (1 ms), below every tolerance in use (R27, DL-315).
3. Post-hoc readings (feed no gate): S-rel not counted as a match for D-tr (DL-258 b); the median-based f_pk and onset reading at the headline; the raw-crossing onset.
4. Sigma reference: the DL-120 value 0.038852 (runs at sigma 0.0623888, git dirty true) is not used; the MS7 baseline-only record is the reference (R25, DL-310).
5. Uniform offsets use max |q| = (N-1)/(N+1) (R10); the Gaussian quantile offsets lack the tails beyond u = 1/(N+1) and the sample sd is 0.08 percent below Delta/sqrt(2 ln 2) at N = 1e4 (R11); the cost per update for Gaussian and uniform offsets was not measured (UNVERIFIED, DL-303).
6. S8 cell choice (R20): both D-tr cells have short tau_d (1.715 and 3.853 ms); cell (24, 26) has no Hopf point and its start state is the stored map-1 value (eta_start 1.3960).
7. Disk: the 10e estimate was 0.24 GB (NC1 rate); the records are 450.9 MB, low by a factor 1.9 (UNVERIFIED sizes).
8. No tag, no push, and no diagnostic or exploratory run at MS10 (R32, DL-326).

## 6. Claim limits

### 6.1 MS10 (R31, DL-325; facts only)

1. **G4-C1.** Under the frozen mode-N criteria the network at N = 1e4 and 3e4 does not reproduce the mean-field classes at the headline (0 of 3 seeds at each of T_ramp 10 s and 120 s) or at the 4 map cells (1 of 4 agree).
2. **G4-C2.** The surge result is stated for the mean field only (G4 consequence 3; this reading is UNVERIFIED); no claim of robustness to finite-size fluctuations.
3. **G4-C3.** No-ramp network controls are classified into surge classes (10 s headline S-abs and S-rel; S9 N = 3e3 and 1e4 S+; cell (24, 26) S+), so network classes under the frozen criteria cannot separate ramp-driven from non-ramp records (DL-229, DL-231).
4. **G4-C4.** Sigma 0.0624 is checked and not confirmed (the mean-field baseline std lies above all six network baselines). Noisy mean-field results are labelled accordingly; sigma stays frozen.
5. **G4-C5.** No claim about heterogeneity-shape robustness (RB8 not evaluable).
6. **G4-C6.** The RB6 rerun named in G4 is read as the network part of S13 at MS11 (UNVERIFIED reading; RB6's mean-field parts were done at MS8).

### 6.2 Carried from MS9 and MS8 (unchanged; `docs/ms9_close.md`, `docs/ms8_close.md`)

1. G7 not passed (DL-229, DL-230): network-record surge classes at N = 1e4 under the frozen mode-N criteria are not used as evidence of a ramp-driven surge; one flagged window at W = 2 s passes the 10-cycle minimum by construction; D8 is undefined in mode N and filters nothing; the network baseline has 4 windows with max/min 1.92.
2. RB2 / D24 failed (DL-242, DL-250): no claim that the regime map is robust to noise; map statements are mode D; S-rel is reported and not counted as ramp evidence in mode N (1,095 of 2,250 control runs, 378 of 2,250 ramp runs). The MS9 wording "sigma 0.0624 is UNVERIFIED until S8" is superseded by G4-C4: checked, not confirmed.
3. Every D8-dependent class is provisional; A_ref reading (a) 2.176222.
4. G6-D1 to G6-D3 (`docs/ms8_close.md`): no claim that onset follows the A4 entry-exit prediction (RB3(a) not validated); the headline delay is taken from the D43-floored runs and the noise-free onset is solver-dependent (DOP853 58.698 s, Radau 58.879 s, unexplained); RB3(b) is reported under both onset readings (raw crossing MEETS, classifier onset DOES NOT MEET).
5. The A9 labels are our operational rules (M9-12); label (c) is a flag, not a demonstrated cause (DL-270); the D31 result depends on our boundary definition (DL-254); J_exit,static on P3 and P4 is our extension (DL-263).
6. The P3 cost is 1.57 x the headline; the Defender exclusion on the timing machine is user-reported only (DL-142).

## 7. Open housekeeping

| Item | State |
|---|---|
| Sigma 0.0624 | checked, not confirmed (G4-C4); frozen, not changed |
| K5 (DL-064, DL-082) | own reading, UNVERIFIED, deferred |
| K10 (DL-131 to DL-133) | definition kept, single-source claim UNVERIFIED |
| K4-net coupling (MC-03) | unsourced; the networks use the M3 network, not the M2 coupling |
| D37 storage decision | open to MS15 (DL-223); MS10 result volume 450.9 MB (321 files); disk free at 10g 153 GB (`df`, C: 930 GB, 84% used; the 10e figure was 81.4 GB, the difference is not explained, UNVERIFIED) |
| MS11 note (DL-251), NOT decided | RB2 and S11 need a constant-parameter control at the headline cell for each sigma |
| MS11 note (G4-C6) | the RB6 rerun named in G4 is read as the network part of S13 (UNVERIFIED reading); nothing listed or run |
| Tags and pushes | none created, none pushed |

## 8. SHA-256 of the MS10 files

The per-file table is `docs/ms10_file_hashes.csv` (436 files; columns group, path, bytes, sha256; SHA-256 053c63916ab536a5a3672dd6c1a5c7797a79fa20e2b419840c1d94019949ca10). Group digests are the SHA-256 of the sorted `path<TAB>sha256` lines (script `scripts/hash_ms10_results.py`); the digest of the whole table is 9a7825c9870b2311132efa2869aca5ee014c46d6bd249aa31e10bddef34045cb.

| Group | Files | Bytes | Digest |
|---|---|---|---|
| 10f records and launch journals (103 records x json, npz, params.md; manifest.csv and run.log of 6 lists) | 321 | 450,936,503 | d1b98f05b1b147437ed19ef3dc4ee84c1dda61693c9e9cc3a9de41f4ba572a52 |
| 10f file-hash table | 1 | 37,817 | 816a967d528de6bd0c0fb1ce9aadf106bb1c86afc65ce1077dcc42717b60aa6c |
| 10f evaluation output | 1 | 29,919 | 762d1b0cc4ba461d6a99ab3519bb926c9850397e4386537ca4be95fa529cf564 |
| companion mean-field records and journal (MF_COMPANION) | 17 | 6,419,544 | b4880e2d57294cbee10cf212f894c726987f98d6824fa9efed37d8d848bc264f |
| 10b candidate table | 1 | 223,674 | 594f87f9888a0f0da73ce8d7b85cd6845c3b4eff17ec8ca741d038fed38672fa |
| 10a timing sample | 63 | 258,887 | 2c7c892763fa019726eadf30e584a9c6a1a8059943c6625668ce70973502e6c5 |
| 10g independent recomputation outputs | 5 | 97,078 | 5b93e424159e85ecb8c71eb94a3c1fec8343a15dadd6623bef6773afd4b0dfc4 |
| configs/ms10 (frozen lists, cells, references, eval choices, run configs) | 6 | 9,982 | f34791b1118b9354ec67e4f5b707f1d785c594f9ee5346b0ddd15a61d9741889 |
| code (ms10_* modules, qif_network.py, launcher, evaluators, writers, checks, scripts) | 13 | 152,528 | 171d8c3bfccf78e329a8730e85c0e73ebb135b2039064f22b323a23b5e467bca |
| tests (test_ms10_*) | 3 | 46,967 | bf0607d751e8aa16ee85f09d004aa626619cb1a3871322d00cba8aaffe55bc6d |
| docs (ms10_plan, ms10_eval_rules, ms10_results, 10b and 10c tables) | 5 | 333,432 | 4b2b599e2336565b7d594f3c6ecaf223a8628826f088c32edd9ad119138f6307 |

The 10f digest d1b98f05b1b147437ed19ef3dc4ee84c1dda61693c9e9cc3a9de41f4ba572a52 (321 files) was re-verified at 10g file by file. The MS9 result files were re-verified against `docs/ms9_file_hashes.csv` (24,876 files, 0 differ). Not in the table: this sheet, `docs/ms10_close.md` and the table itself (their SHA-256 are in the decision log, DL-329).

### 8.1 Records (class of the frozen mode-N classifier, JSON SHA-256)

S8 headline (6):

| Record | Class | JSON SHA-256 |
|---|---|---|
| S8_head_0000_a1c3962081d6 | S-abs | ffa4db93c504a1495b21ea159c1482f3221e86d368c30d8f4821e1b53fa97b5a |
| S8_head_0001_c8b2c7055fec | S-rel | 0ec2519dc716545c25dc4833c6a6cc304eb304359645a7460090569ee7874568 |
| S8_head_0002_6cc608689f3f | S-sus | cd31c5fa83ed608b931ab9a84edff8885cd510fb0b55de12bcb3cca4daff0b4c |
| S8_head_0003_7dfd3c05b40c | S-sus | 69a3c11ed3de285667b4582cf9b25385a2500c62d3dd76845309b185ab5c1737 |
| S8_head_0004_4a8295e0a793 | S-sus | 04c3213f5becc38a0282dd0284ea25ba8d30382d6c6190d845ac45312b82e2aa |
| S8_head_0005_188fa49b5ae5 | S-sus | e9511d4d5c51e8c150c616d0c16877c5cb4d120e2ed4e664b36b82f09b9c56e0 |

S8 map cells (12):

| Record | Class | JSON SHA-256 |
|---|---|---|
| S8_cells_0000_aee9e005f8b4 | S-abs | 56ff1ac92296f248f51f5e9acae9b27aa8c7c183955af52cdc8b7b11b44ae6b2 |
| S8_cells_0001_eed3cdd731c3 | S-abs | 5cf31315cf05192d13768db162fe8849e2069bca4af66130d0676cc790aee672 |
| S8_cells_0002_1ab33ddc39d3 | S-rel | 1584f3e9c65f29c69f81882742e4fcad08a98b07fc40fc6e90a16e5cadb24637 |
| S8_cells_0003_00730ac4eca9 | S-sus | e9c3c8638a1094b50944043f2e629a39b616c8ea475bc61d07c523d0a427e1ec |
| S8_cells_0004_f510126a8b30 | S-abs | ddba6da2594a4cfa679d1b3fff92e5533f30abb6187486d0f0d27b3a2fa7e469 |
| S8_cells_0005_a46f9cb55ffd | S-abs | e198b91cad3bfc85a47190c284481f0485bf2cbb768d5b318808bbe975a1c4ea |
| S8_cells_0006_e682abd67176 | S-abs | 9b92b04e6e69aa7ebc653f41473cab696f5048673571b85ad86e3a38696eb46e |
| S8_cells_0007_ef1964fd53b1 | S-rel | aaa9c74ea4bc7e72bfb4c46372d607f06462db98265e53ce031ebf943fb26e0a |
| S8_cells_0008_9c43d4be8d17 | S-abs | 012977126af24539f99d279ae296a38b4fc941a3068498b700464396e8646602 |
| S8_cells_0009_fa5a6fb1715a | S-sus | ecf40258e23bf089445b070e2a1ab65ab60dd60bb625d01f948a600499462bfa |
| S8_cells_0010_1d30dbf4f547 | S-sus | b649c25b0ff62d49ff2188b74e2d488d00635955cc6e6890e05f1a81d3347136 |
| S8_cells_0011_1ac1c9b70140 | S-abs | 1b521aa464ba88e2659d528ed22c3950597754f735ca55887dc4f8f012b4290a |

C2_S8 controls (18):

| Record | Class | JSON SHA-256 |
|---|---|---|
| S8_ctrl_0000_fe2a7041d3aa | S-abs | 27c875d5947dd8e2f5f1e1ce36f34fd845f88137c844070921a80a6caaaa3eb6 |
| S8_ctrl_0001_853bf161ba08 | S-rel | 2bc285d0601734663926df72d004bbfff0d6285ee741d593dd56eb436c784e84 |
| S8_ctrl_0002_71f9b7fa1a13 | S-abs | b5bcff4a49f6f4d340316e071baa758eab472f411ebd9ccff7e7ffbe00a9c94a |
| S8_ctrl_0003_3be852091fa0 | S-sus | e988adcc60c9425be08fbbac944516a61ab7613a5c42b20a82b36d915260eaa2 |
| S8_ctrl_0004_05dd0878a58a | S-sus | f2bd1a38437b06e2a690ed2e76511bc54dabc556e36dfec4eafc465d0d6ecb04 |
| S8_ctrl_0005_c52a29e3ec4a | S-sus | 6cdf7764128666100297d2bdac212cac72b49755d52e9d21268bb3f8787e16b4 |
| S8_ctrl_0006_a62274748bce | S-sus | 3840489b1799b8bf5176bbee033ddabb0e413ceb385b6ee109cc48ca79a4014a |
| S8_ctrl_0007_9da6273d004a | S-abs | 8054dbbb932f2a6f4c58e1886377f1088e5aa6fd2d0bc27f6f97113a1b95d466 |
| S8_ctrl_0008_6e551ceda6ed | S-sus | c939099fa7d5406d0d592cc8c537fe69841bc7faea600f8067966b78df0317e6 |
| S8_ctrl_0009_34bf79b1016c | S-sus | 1a7ee964d7aa55b4ca583797dad039279236c7e91575f2bb1a2f260e34fb51a5 |
| S8_ctrl_0010_dc21707dfa17 | S-sus | ffaee25c63b10fde58fd308ee1f5a316c4dd2fd12ccfa9ad41ef41463e0fcdc4 |
| S8_ctrl_0011_c8ae7243e0d7 | S-abs | ddd7ca3d352f67e824f7f983b6450727da47c8853c19009803793a73777e2d11 |
| S8_ctrl_0012_fe7efdd12df4 | NS | 571756ac69bd4641df68365f460f9face6c7e812cb50184fa8e76f539c0c574f |
| S8_ctrl_0013_5344ff1d2657 | S-rel | 029390841e370038a9fcae5c8fc6d290103aef7b585b3d95f27dd608404a45b6 |
| S8_ctrl_0014_d1e8f790b9ca | NS | 1b75ef53c0e744254417953b04d565ef8dee3dbd91e7b557613d5ed763d63185 |
| S8_ctrl_0015_56311e18cbc4 | S-abs | 0a58f684f640c570482a819beba610fe5bbbfdadabc66d80c18e27e72190d7bf |
| S8_ctrl_0016_1fbbab39ab33 | S-rel | 514a8d29dd84088ec2ebcb5ee347999edad097645e478b6e990a6d2cf836e9a6 |
| S8_ctrl_0017_adffd1e03f32 | S+ | f5bde58d2823cebcc9283be520ea5861827a41ff3b143e941475920d6b665a30 |

S9 (40):

| Record | Class | JSON SHA-256 |
|---|---|---|
| S9_0000_963e33e3f38a | S-sus | 388d066ae385b94d5cca4ffbfae993b5eee2dc25c6d112c31453738748c46f55 |
| S9_0001_4de60d0419f7 | S-sus | 9e3bc29100e5dcc213f38bdcd7d85144d44c4e5be48131e190f48a9830a5f940 |
| S9_0002_1e3530b6923c | S-abs | d3deece54a3fdb0f6990cbea60ff82c89a181d3961d410deea96d2a5c1f93a0a |
| S9_0003_f5db9fdcc54e | S-abs | 1d14e1607af3ac8d2b64a58a9b6b3636a3532e352d318824cc1683c314d332d1 |
| S9_0004_b188460eb8b9 | S-sus | 7f439326df9bae6d04ee040b2bf22cb17e462bc0e065a46e95717a04ab55c3d1 |
| S9_0005_aac03c9208a0 | S-abs | 641528f2b334ede414de8341c6b835aee63084abb9a02583e2e1a3b691ae6070 |
| S9_0006_5e7884f94ff0 | S-sus | 5fc945c5cf684548330e302da8c9df29751616eadb563b1ca2941586e4854b44 |
| S9_0007_788ce4d5a928 | S-sus | d5926b81530fae0d1bec2af8af6df39be4db481d64f602b9055a6b124cccbfe7 |
| S9_0008_86dd0d3687dc | S-abs | 9227def3d90e13aee127c5db09c8d74b63b2d05e60e88d8dc488badb9a77b445 |
| S9_0009_3b268b12cb18 | S-sus | 50ee7d29cef006e0ac536c87430869ca44f4d4ac8f6b1ef5c9f5e7e717dfeb71 |
| S9_0010_438ed5f46f5d | S+ | 63cfdf97044d46076308c1d6147f929aba91d9d52d503b200e4a3d4fbfa374fe |
| S9_0011_2e0a325a27e1 | S+ | 20a08ff26e5b1b9e55c4e4494301324ef413a4cdc156ae77734e2b41d25ef75c |
| S9_0012_523f863677c4 | S+ | 57c966929a1d4067f33f9954bb88cddd788790a4052424176c15d7c5cbcf3912 |
| S9_0013_7c61def56f00 | S+ | 587bae7bdade599f5beae13c95e156d5fc4b08445ec72d64b078b54bc037c9ac |
| S9_0014_ab7672378df3 | S+ | 3be67d7b237a97746821cf568b45791b71350608d1f34aa251ae34d62ef44b66 |
| S9_0015_d2780af715e2 | S-sus | ddd0a82744cab546c560f3752692ff9c93718f6b7728babba7632845d1348b94 |
| S9_0016_2d7ec2f7b90f | S-abs | c3c384f375681a6d79a4298e4a30ef5f08f7838a930eaf7db8116f1888493e54 |
| S9_0017_522d9f19137c | S-sus | a2e7eb85d1d82267e8c566c3723366d13b336a8826648fbe1890b7cb4d0c84b7 |
| S9_0018_0edb32be27ce | S+ | 39cb8836e57f810399ce739a08fc0270bef269ece3ff6baabcaefc8931f3554e |
| S9_0019_c3698b8f40c1 | S-sus | effbce1851900dafcca267bbc71bdec9548c91af63e26d6a9adbcf6788cba849 |
| S9_0020_a5dd7a780586 | S-sus | fd4631991f72ed9003d387b8f1a119c292dad97174193ce718ea3ea90c598b29 |
| S9_0021_04fc4ed8ed57 | S-abs | ac892ed2829b8fb20095b84eaaab39d4d7c36e4686817b731f8490dc66dfcb54 |
| S9_0022_d3e25b3b3313 | S-sus | b6bcb92916414bed076c3a437879e8ae6d22704da8dd8c30a5f4190a4e7c9f40 |
| S9_0023_d3fc07b94c39 | S-sus | 2756a67875a5bd36036e73aab2c673e934c7865d1284d247f02e4d0531b81986 |
| S9_0024_f1567848942c | NS | 5edf358913e8802cc6eb31a6a087b160f65cc74d31b9ca00f2db9ac4bae73799 |
| S9_0025_2f843ac98942 | S-abs | 7b65cb9e0cc305fc62b6f5f03662632710c63156d9dcc1b0bd14ee65b1e64df1 |
| S9_0026_33171bb4b02a | S-sus | 0889184914cf4f8fabe057f47702873e13a3b170910400502908bd9bd01cf3f2 |
| S9_0027_0c784f6792fc | S-sus | a3a8fc8bf8752dde2710357089978a498562a944b2cf92a88a9e92ff2b4c54ed |
| S9_0028_beacf42ed762 | S-sus | 0cf8bdbb2cb7928f1d5b06d6182b2c95a0b18e5c4305e5ab8b7291fb98ec2fc1 |
| S9_0029_433b81b431f5 | S-sus | 24b33e92683f0d303ab42c1e3e6f2cda063c608815955c744637ebd80fce293e |
| S9_0030_caa20d5ecab6 | S-sus | 1bc600df2a60f6514d3ab60aeead7d21cd6d8a2337149f8b1e54d0507546d3a6 |
| S9_0031_987ef000f195 | S-abs | 4ddad9ff6768b645708ef471ed6a2a00bbab2dae65aa71a5bd9cc5bf474254c5 |
| S9_0032_4560ccedd548 | S-sus | aa37bc05eb9c9ccfa04ee3265f380f14a19eda62bc153f07a5d266a94e7a15b1 |
| S9_0033_2c1560349528 | S-abs | d252c55023394e10f47c7f3828fd67c9412455318fcfc3095f511fe796d4d817 |
| S9_0034_0a7ef05f67e3 | S-abs | 2fcb6eb38ee132f71b5ce082c80f0421dae668e176855defa82d13096fe90bc8 |
| S9_0035_3f8b426b432e | S-abs | 91c3b436d2e9353848cb0545e07dfb475c5153a7e8f66dd39c0fddc3dc038734 |
| S9_0036_3e3904cda3de | S-sus | 8fe1ae9a60f9b14191648da52c36119668b71addf88a20f1beef0c550685a45f |
| S9_0037_62bb68361180 | S-sus | 67d41d98c944f4615a952c375bf172e80cf6c37e8108cdd9652c70998ce89c47 |
| S9_0038_b632d3ea7234 | S-abs | 05a288eedca5ba31649b3a27799c7dfec7605b660f00fb12f14c9565770851ea |
| S9_0039_a330dd1ffb7a | S-sus | 5a8d0360fec136f24702e6fa64228690726597c339ec8555dd5aa5d3e67c3824 |

C2_S9 controls (12):

| Record | Class | JSON SHA-256 |
|---|---|---|
| S9_ctrl_0000_ae48f6c64fe2 | NS | b7c04a8a31404f5e939114b81ac952d3f385a663ef5b597ee27add03d022bfa8 |
| S9_ctrl_0001_725ed676a81a | NS | cd8f26ad58c91acbc6abdd76b2fcddb72e6247e9ac7f1649908d30a57709e85f |
| S9_ctrl_0002_4b126dba8d71 | NS | bd0b76bf9f662b966d463731628174b99b365b186a971813121ff7b056199c2d |
| S9_ctrl_0003_d895564bd5f8 | S-abs | 0222bed573bcebc299381b5aca905e18747e4a935c890a0df0bba0a6de5e9240 |
| S9_ctrl_0004_5980cf5a4e88 | S+ | 45f3352e1dd7d35f1ca176970ae03df511510f451699a2ef4198f43966ee2ad9 |
| S9_ctrl_0005_ac2a6548530c | NS | 05fd1c97eb21cf4617deb835ed5e895d6928e4ae952f1288e8f534e72e6047eb |
| S9_ctrl_0006_b842847d094c | S-sus | 71f82049e86e4f7b29333b09933305e2b0653ccaa58c2cb06de8d8fa0ef82098 |
| S9_ctrl_0007_9abd2430a2e5 | S+ | 0cc545c949cfad87a27489b949fa7af4600b60016bc03982645902f830e8fad9 |
| S9_ctrl_0008_46d422e177af | S-sus | fd93fc48ae6f708b26da2d4bea2860ef7ca3ea947539c68cb68aa7dba49c555c |
| S9_ctrl_0009_d621157e2e04 | S-sus | 46d6bf2f55176840edf14d13b91248c5f8baacba085877f4c2c1ac535ba7f6d5 |
| S9_ctrl_0010_526915ccd369 | S-sus | 94e285dbbfee964d5797f214bb94b0411dc7ad6222d78e3b57c077b950060e8b |
| S9_ctrl_0011_424d1250a3ea | S-abs | 6f9b323bcb89ca42e50f2db4f5a2b16c5aa12594ae0a1fa94926f8b81ea4b090 |

S10 (9):

| Record | Class | JSON SHA-256 |
|---|---|---|
| S10_0000_8a0cdc4a874d | S-sus | 7c3b028a3bbd6699815843c15188717225c05bdaad65496eef24628fe9053033 |
| S10_0001_36b70c19c41d | S-abs | 504bb93c7ac59aa7224bd26b4b3f400a466c0c3e97c015a02d54117afe33041a |
| S10_0002_7eab17d1df40 | S-sus | 6bc744ae69fb3220d7a6e5e4751f5a9c5c34deee0905faf50a8c9191235b15dd |
| S10_0003_c88a9f62a8db | S-abs | 91f7dbb4f0b684cfb7b9f192c5b3460cccc3c57e71d211b0239059d1623a0b70 |
| S10_0004_3ae0a39afdf6 | S-abs | 2a442c83385924540526c7d4e7e76985cbc58c2bccbd64f6af6c7de5e5cc402d |
| S10_0005_8ba40619c15d | S-abs | 580e57e272c1d9dee009b582fa325347f7e1e6a1b257ef491dd209a6e90003e4 |
| S10_0006_f8ff32c4eeb3 | S-abs | 6967a5dd492804acc4eda1a3856cba93251c0a636b9dad516ab995181a426ec3 |
| S10_0007_1cc34fd7042e | S-abs | 138ab8a91e8dad57e92042663dc190f643ae1f58322d2806a80dba9da82a838e |
| S10_0008_6c9452e442ea | S-abs | 38c765185922c222d125eede7596cbf290d066fd1ce2a5bad4b2a0f3152b3641 |

C2_S10 controls (6):

| Record | Class | JSON SHA-256 |
|---|---|---|
| S10_ctrl_0000_4a49f05dbb1d | NS | 9813efb2babd92c7aeb61c83614792fc54153416c5c8e1f1687e06695aa989f0 |
| S10_ctrl_0001_b02ee2a12ed3 | NS | a98b0f3512a8162d0de9e2228e44edd62a9da31d115620c510042366c90615a6 |
| S10_ctrl_0002_f2d819e819d7 | NS | 3a37fccfc1d553422ac3b47d3b1249c5f6ee39f85b2705d66ad4d0a02271c1ca |
| S10_ctrl_0003_2f672b2fff45 | NS | 62089559dac2297d51ae9c7f3cff9a4290fd2df1a067e55635eb3fa48b0c1f0f |
| S10_ctrl_0004_525068b30160 | NS | 81739a3d7afabea563183c8a602d8cbae56569813dfe45f3b67937fb1024769b |
| S10_ctrl_0005_30fd6dc66f56 | NS | 1422bc3a6b34876f587845dafa28f2404eb6c7938267cdf4aed50efc91068bf1 |

Companion mean-field records (mode D, DL-309): S8_mf_cells_0000_081b77a5f999 (json d099828e938c106f8c7334aee5e4a0c48e5e6e436748cbdc7ba10edbcdbae9c1), S8_mf_cells_0001_908ef5a1c420 (cc5c5e5861e7c5b3872ea43c661bf52a030e318f9423cc4b64d07800931f5bd8), S8_mf_cells_0002_8cf8eb1029e6 (6334e488ad2fcd3abce8112f640c52876258847ec059a96b0c6e1f52097ced61), S8_mf_cells_0003_1474ff58c0a4 (a04d4ca14202534bf68e4cf75612b4da6a4d868b7cef7caf949b02bc137074eb), S8_mf_head60_0000_0080d385accd (ce1077309bf7d13450ceb7b003c1148ae898b79acf4245cd7ee8b5864b2e6c78).
