# MS11 close (11h)

Written for: the reviewer and owner who close MS11, and the author of the paper's limitations section. MS11 is closed on paper (DL-330 to DL-418): **238 runs ok; RB2 FAIL at sigma (7 of 10; 0.5 sigma PASS, 8 of 10; constant-parameter controls keep 7 of 10 at every sigma), RB6 network f_pk FAIL (both readings), RB9(b) headline FAIL (4.391 Hz against 0.5 Hz); RB5 delta_0, RB9(a), RB9(c), RB10 and the window line PASS; the rest REPORTED; 26 of 26 carried checks recompute equal; the independent recomputation agrees on 17 of 18 rows.** MS11 has no gate in Table 11.1; its acceptance ("every RB check except the RB8 M4/adaptation parts has a result") is met (DL-393, DL-415). No simulation, launch or diagnostic of any kind was run at 11h, no tag was made, nothing was pushed, and no frozen criterion, list, config or evaluator changed (tag `criteria-frozen`, commit dd8330c5eaacd63d21e7b7969430988d00862769, criteria SHA-256 c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05; S13 317db87e, A4_grids cf6a60be, S5_cells fe8590ce; eval freeze of DL-377: `docs/ms11_eval_rules.md` 4b1a1a66dba379015f6c78f5f0431bd16cfdd81bb69b925b8857f4ccc55c48a5, `configs/ms11/ms11_eval.yaml` fcb439645473667b5bdd3d59f902b4e0498547af7403b79d5044a7d69d4209cf). Numbers are those of `docs/ms11_results.md`, `docs/ms11_evidence.md` and the decision log (DL-330 to DL-418). Hash convention (DL-414): documents are hashed both as working-copy bytes and as the committed LF blob (`git show HEAD:<path>`); the pre-checks use the working-copy bytes and keep that method. The SHA-256 of this file is in DL-418 (a file cannot contain its own hash).

## (a) Sub-steps and commits

| Step | Commits | Content (DL) |
|---|---|---|
| 11a | 2b43379, dae2dcd | R33 (MS10 close accepted), plan quantities, status inventory, open choices M11-1 to M11-14, proposed seed keys, timing sample; `docs/ms11_plan.md` (DL-330 to DL-334) |
| 11b | 4a085fb | rulings on 11a; cut order step 1 (Radau only at the headline T_ramp, DL-337); evaluation rules written and frozen before any run; run lists, launcher and frozen list hashes (DL-335 to DL-344) |
| 11c | a31c89b, a778462 | rulings 1 to 14; evaluators and A11 script written on synthetic fixtures; RB9(a) unit-level value stored (DL-345 to DL-365) |
| 11d | 2e29ced | RB9(d) Reading A and list MS11_RB9D (238 runs in all); verdict table; 26 recompute hooks coded; launch preparation (DL-366 to DL-375) |
| 11e | d29268f | "PASSED, continue" mapped to REPORTED (old and new eval hashes in DL-377); reader-path tests on fabricated records; dry run (DL-376 to DL-381) |
| 11f | dd78cc1 | five lists launched by the reviewer at d29268f and audited; slow tests; frozen A11 run once; `docs/ms11_results.md` (DL-382 to DL-391) |
| 11g | 8ff8ee3, 228e948, 8690b14, 02ad127, 2ea57ea, e189428 | rulings on 11f; claim limits MS11-C1 to C9; independent recomputation (stopped once on a script error, then run once); bounded post-hoc look at RB9(b); evidence sheet and file-hash CSV (DL-392 to DL-409) |
| 11h | the commit that adds DL-410 to DL-418 and this file | close on paper; no simulation (DL-410 to DL-418) |

## (b) What MS11 ran

| List | Runs | Launch wall |
|---|---|---|
| MS11_S11 | 120 | 34.1 s |
| MS11_CTRL (DL-251 constant-parameter controls) | 30 | 10.6 s |
| MS11_RB9D (post hoc, reported only) | 2 | 143.3 s (2 workers) |
| MS11_S13_MF | 68 | 407.5 s |
| MS11_S13_NET | 18 | 502.5 s |
| Total | 238 | 1098 s (18.3 min) |

All 238 ok, 0 failed, git dirty false, commit d29268f73943c75383b1be942d57d0f6afe01b81 in all records (DL-382, DL-383). Result files: 724 (json, npz, params.md, manifest.csv, run.log), 1192.347 MB, digest cdafcc0831580ea4b9f7dfd8e095deb50e8b86db2974f556cf7ffe7d75637f53. Slow tests at 11f: 24 passed, 910 deselected (DL-385). No other run was made at MS11 (the A11 evaluation, the independent check and the post-hoc look read stored records).

## (c) Results (A11, rows 27 to 44; value, threshold, status, label)

Labels on every noisy mean-field and network row: "sigma checked, not confirmed" (G4-C4); "provisional (D8 open, DL-137)" where a class went through a D8 call; G4-C1 to G4-C6 on the network rows. Status words: PASS, FAIL, NOT EVALUABLE, REPORTED.

| # | RB | check | value | threshold | status | label |
|---|---|---|---|---|---|---|
|27|RB2|headline class kept, 0.5 sigma|8 of 10 (0 failed)|>= 8 of 10|PASS|pre-registered; sigma not confirmed|
|28|RB2|headline class kept, 1.0 sigma|7 of 10 (0 failed)|>= 8 of 10|FAIL|pre-registered; sigma not confirmed|
|29|RB2|2 sigma, reported|8 of 10|no pass rule|REPORTED|pre-registered; feeds no gate|
|30|RB2|stricter readings|S+ only 2 / 2 / 2; S+ or S-abs 3 / 3 / 3|none|REPORTED|post hoc; feeds no gate|
|31|RB2|DL-251 controls|NS 3 and S-rel 7 of 10 at each sigma (kept-class count 7 of 10 with no ramp)|none|REPORTED|post hoc amendment (DL-251)|
|32|RB5|delta_0 at T_ramp 10 s and 316.2278 s|4 of 4 same Table 2.1 label as the 1e-6 member|same label|PASS|pre-registered|
|33|RB5|up versus down|P5 D-tr at 13 T_ramp values; S4 beside, "no class"|none|REPORTED|pre-registered|
|34|RB6|rtol 1e-8 and 1e-12|class D-tr in 4 of 4; onset and delay differences 0.0|none|REPORTED|pre-registered|
|35|RB6|floor at 10 s and 316.2278 s|classifier-onset medians not monotone; raw-crossing median undefined for mode N (erratum, DL-402)|none|REPORTED|pre-registered; no scaling law (UNVERIFIED)|
|36|RB6|network f_pk, halving dt|reading 1: 0 pass, 3 fail; reading 2: 2 pass, 1 fail|< 0.02|FAIL|pre-registered; f_pk reading UNVERIFIED (M11-6); G4-C1 to G4-C6|
|37|RB6|network V_p +-100 against +-200|f_pk 63.06 / 60.06 / 60.06 against 81.08 / 78.08 / 75.08 Hz (dt 1e-3)|none|REPORTED|pre-registered|
|38|RB9|(a) dimensional against non-dimensional|1.2258e-08|within 0.005|PASS|pre-registered; unit level only (MS11-C4)|
|39|RB9|(b) spectral against cycle frequency, headline|49.0 Hz against 44.609 Hz, difference 4.391 Hz|within 1/W = 0.5 Hz|FAIL|pre-registered|
|40|RB9|(b) map cells within 1/W|map 1: 51 of 760 (A11, Hilbert phase); map 2: 71 of 296|no gate fraction|REPORTED|pre-registered; see MS11-C9|
|41|RB9|(c) band 30 to 120 Hz, map 1|14 of 900 (1.56 percent)|<= 5 percent|PASS|pre-registered; provisional (D8 open)|
|42|RB9|(d) tau +-20 percent|tau 8 ms D-tr 49.5 Hz; tau 12 ms D-tr 43 Hz; headline D-tr 49 Hz|none|REPORTED|post hoc; feeds no gate|
|43|RB10|surge definition sensitivity, map 1|headline unchanged under 9 variants; max 1.67 percent|<= 10 percent|PASS|pre-registered|
|44|S13|window x0.5 and x2|0.0 percent of 900 at both; headline unchanged|<= 10 percent|PASS|pre-registered|

Rows 1 to 26 are the carried checks (section (e)). The short-window false-surge rates (306, 400, 172, 24 of 500 at W = 0.2, 0.333, 0.593, 1.054 s) apply beside the S11 classes at T_ramp 10 s and 30 s.

## (d) RB2 sigma result and the constant-parameter control

Gate (T_ramp 120 s, "kept" = S+, S-rel or S-abs; at least 8 of 10 seeds; failed runs count as not kept, none occurred): 0.5 sigma 8 of 10 PASS; sigma 7 of 10 FAIL; 2 sigma 8 of 10 reported. Classes over 10 seeds at 120 s: 0.5 sigma S+ 2, S-rel 5, S-sus 2, S-abs 1; sigma S+ 2, S-rel 4, S-sus 2, S-abs 1, NS 1; 2 sigma S+ 2, S-rel 5, S-sus 2, S-abs 1. Seeds are paired across sigma. DL-251 controls (constant parameters, post-hoc amendment, feed no gate): at each of the three sigma levels NS 3 and S-rel 7 of 10, so a kept-class count of 7 of 10 with no ramp. By the rule's own reading, the S11 counts (8 of 10 at 0.5 sigma, 7 of 10 at sigma) are not ramp evidence beyond the control. The noisy subgrid (97 of 225, 43.1 percent, 203 needed) stands FAILED as logged (DL-242).

## (e) Carried-check recompute

26 of 26 carried rows (RB1, RB2 subgrid, RB3, RB4, RB5, RB6 MS8 parts, RB8 heterogeneity and M4, G5, G6, G7, sigma_check) recomputed equal to the logged words under the 11d map, 0 mismatches (DL-389). The recomputation shares the criteria loader and the frozen classifier on all hooks except RB8 M4, and the original evaluator code on 21 hooks (`docs/ms11_results.md` section 7), so it is not independent of these. It was not repeated at 11g.

## (f) Independent recomputation (11g)

`scripts/ms11_independent_check.py`, written from `docs/ms11_eval_rules.md` and the plan text, run once on the real records after one earlier stop on an error in the script itself (DL-400; no A11 comparison was made then). **17 of 18 MS11 rows agree** on status word and counts (DL-405, DL-406, `docs/ms11_evidence.md`). The one mismatch is RB9 `b_map_cells_fraction` (REPORTED in both): map 1 within 1/W, independent 45 of 760, A11 51 of 760; map 2 equal at 71 of 296.

Explanation (post hoc, exploratory, read only, feeds no gate; DL-407): the two numbers come from two cycle-frequency estimators, the unwrapped Hilbert phase over the flagged episode (A11) and upward zero crossings of the band-passed v in the same episode (independent). They disagree on "within 1/W" in 18 of 760 cells: 12 within by Hilbert only, 6 within by zero crossings only; 12 - 6 = 51 - 45, so the counts reconcile through the listed cells. The DL-405 near-bound hypothesis is disproved: the disagreements are not near-bound flips (in the 12 cells the zero-crossing frequency is 0.88 to 11.25 Hz from the spectral f_pk while the Hilbert frequency is within 0.5 Hz; in the 6 cells the Hilbert frequency is 5.09 to 8.32 Hz below f_pk while the zero-crossing frequency is within 0.5 Hz; the largest difference between the estimators over all 760 cells is 14.76 Hz). Why they differ was not investigated (UNVERIFIED). At the headline both estimators give FAIL (Hilbert 44.609402 Hz, zero crossings 44.609421 Hz, spectral 49.0 Hz). No code path was patched, nothing was re-run, A11 and independent outputs are unchanged. Per ruling DL-413, no further diagnostic on the estimator difference; any diagnostic comes to the reviewer first.

Extra equalities: the independent map-1 and map-2 baseline classes equal the stored class tables (900 and 325 cells, 0 disagreements).

Independence limits: the check shares the frozen classifier, the criteria loader and (for the A8 variant rows) the A8 variant definitions with the original evaluation, so a fault in these is common to both; the 9i function is not used by the independent check (it is shared by the carried MS10 hooks of the A11 recompute). RB9(a) is not independent (it re-reads the stored unit-level file). RB6 network reading (ii) is marked "method taken from original behaviour, arithmetic independent" (DL-401). Map 2 and the noisy subgrid were not recomputed independently for RB9(c) and RB10. Float differences listed, not judged: RB6 floor classifier-onset medians at 10 s up to 1.75e-4; RB9(d) duration at tau 8 ms 1.0e-3 s; headline cycle frequency 1.9e-5 Hz.

## (g) Rules gaps found

1. **Reading (ii) for episodes shorter than W** (DL-401, MS11-C8): the frozen rules say only "argmax of the PSD of v in 25 to 100 Hz over the window of the classifier episode". A11 takes the spectrogram of the whole stored v, keeps the windows whose centre lies in the base-run episode, averages the PSD and takes the argmax in 25 <= f < 100 Hz. The 3 of 3 reading-(ii) comparisons have a base episode of 0.0833 s against W = 0.3333 s.
2. **Cycle-frequency estimator in RB9(b)** (DL-407, MS11-C9): the rules do not name it (section (j), MS11-C9).
3. **Raw crossing for mode N** (DL-402, MS11-C6): the raw-crossing onset is computed only for mode D records; the 60 floor runs are mode N, so the raw-crossing floor rows are undefined by construction (erratum, `docs/ms11_results.md` section 9; DL-387 and DL-390 carry the old sentence and are corrected by DL-402).

## (h) Claim limits

MS11 (MS11-C1 to MS11-C9 are the MS11 claim limits; DL-394, DL-402, DL-406, DL-412):

1. **MS11-C1.** The headline surge class is kept in 7 of 10 seeds at sigma (required 8 of 10), and the constant-parameter controls reach the same class in 7 of 10 at each sigma; no claim that a ramp-driven surge is robust to noise (carry with DL-229, DL-258 and the MS9 D24 failure).
2. **MS11-C2.** No claim of f_pk or class agreement between the network and the mean field (RB6 network f_pk failed under both readings; carry with G4-C1).
3. **MS11-C3.** At the headline the spectral and the cycle frequency differ by 4.39 Hz against the 1/W bound of 0.5 Hz (RB9(b) FAIL); the cause is not investigated; peak frequencies are stated as the classifier's spectral peaks.
4. **MS11-C4.** RB9(a) rests on the unit-level test only (1 s path_eta ramp, tau 10 and 20 ms, not the headline).
5. **MS11-C5.** The DOP853 versus Radau comparison covers T_ramp 120 s only (cut order step 1, DL-337).
6. **MS11-C6** (reworded, DL-402). The floor-level direction of RB3(b) is unresolved at T_ramp 10 s and 316 s: classifier-onset medians are not monotone; the raw-crossing onset is defined only for mode D records, so no raw-crossing median exists for the mode N floor runs; no scaling law is entered (UNVERIFIED).
7. **MS11-C7.** All earlier failures and claim limits stand as logged (RB1 FAIL, G7 not passed, D24 failed, G4-C1 to G4-C6, the MS9 claim limits).
8. **MS11-C8** (accepted, DL-406). RB6 network reading (ii) f_pk for episodes shorter than W relies on a method not stated in the frozen rules (described in DL-401); the verdict stands as evaluated.
9. **MS11-C9** (accepted, DL-412). The frozen rules do not name the estimator of the cycle frequency in RB9(b); the map-cell fractions are 51 of 760 (A11, Hilbert phase) and 45 of 760 (independent, zero crossings), both reported; the two estimators differ by several Hz in 18 of 760 cells for reasons not investigated; the headline RB9(b) FAIL holds under either estimator.

Carried earlier limits.

MS10 (`docs/ms10_close.md`, DL-325):

- **G4-C1.** Under the frozen mode-N criteria the network at N = 1e4 and 3e4 does not reproduce the mean-field classes at the headline (0 of 3 seeds at each of T_ramp 10 s and 120 s) or at the 4 map cells (1 of 4 agree).
- **G4-C2.** The surge result is stated for the mean field only (G4 consequence 3; this reading is UNVERIFIED); no claim of robustness to finite-size fluctuations.
- **G4-C3.** No-ramp network controls are classified into surge classes, so network classes under the frozen criteria cannot separate ramp-driven from non-ramp records (DL-229, DL-231).
- **G4-C4.** Sigma 0.0624 is checked and not confirmed (the mean-field baseline std lies above all six network baselines); noisy mean-field results are labelled accordingly; sigma stays frozen.
- **G4-C5.** No claim about heterogeneity-shape robustness (RB8 not evaluable).
- **G4-C6.** The RB6 rerun named in G4 was read as the network part of S13 at MS11 (UNVERIFIED reading); see (i).

MS9 and MS8 limits carried unchanged (`docs/ms9_close.md`, `docs/ms8_close.md`, as restated in `docs/ms10_close.md`): G7 not passed (DL-229, DL-230); RB2 / D24 failed, no claim that the regime map is robust to noise, S-rel not counted as ramp evidence in mode N (DL-242, DL-250); every D8-dependent class provisional, A_ref reading (a) 2.176222; the A9 labels are our operational rules (M9-12) and label (c) is a flag (DL-270); the D31 boundary definition is ours (DL-254); J_exit,static on P3 and P4 is our extension (DL-263); the P3 cost 1.57 x the headline; the Defender exclusion is user-reported only (DL-142).

MS8 departures:

- **G6-D1.** No claim that onset follows the A4 entry-exit prediction; RB3(a) is not validated (0 of 6 testable in-range runs within one A4 step); fast-ramp onsets are ramp-seeded.
- **G6-D2.** The headline delay is taken from the D43-floored runs; the noise-free onset is solver-dependent (DOP853 58.698 s, Radau 58.879 s, 181 ms), unexplained.
- **G6-D3.** RB3(b) is reported under both onset readings (raw first crossing MEETS, classifier onset DOES NOT MEET; raw crossing primary by the 8f2 clarification).

(The G6-D wording is shortened here; the full text and file hashes are in `docs/ms8_close.md`.)

## (i) Closure of the MS11 notes

- **DL-251** (RB2 and S11 constant-parameter control): done. MS11_CTRL, 30 runs, labelled POST-HOC AMENDMENT; result in section (d).
- **G4-C6** (network part of S13): done. MS11_S13_NET, 18 runs; result RB6 network f_pk FAIL (row 36), with G4-C1 to G4-C6 applying.
- **G4-C3 and DL-231:** the network rows carry the G4 labels; no network class claim is made from the 18 network runs.

## (j) D36 accounting

Measured MS11 wall 1098 s = 0.305 h (DL-382, DL-384). Basis B (ruled basis, the one used from now on, DL-396): **13.51 h of 24 h** (13.5075), margin 10.49 h. Basis A (MS11 figure on top of 14.21 h): 14.52 h (14.515), margin 9.49 h. The 14.21 h mixed-basis figure stays UNVERIFIED. Analysis, A11 evaluation, independent recomputation and test time are not included.

## (k) Open housekeeping

| Item | State |
|---|---|
| K5 (DL-064, DL-082) | own reading, UNVERIFIED, deferred (unchanged) |
| K10 (DL-131 to DL-133) | definition kept, single-source claim UNVERIFIED (unchanged) |
| K4-net coupling (MC-03) | unsourced; the networks use the M3 network, not the M2 coupling (unchanged) |
| D37 storage decision | open to MS15. MS11 result volume 1192.347 MB (724 files); free disk 109.8 GB at 11e (DL-379; 71.0 GB at 11d, 153 GB at the MS10 close; the changes are not explained, UNVERIFIED) |
| Sigma 0.0624 | checked and not confirmed (G4-C4); frozen, not changed |
| 14.21 h figure | mixed bases, UNVERIFIED |
| Tags and pushes | none created, none pushed |

## (l) Evidence references

| File | SHA-256 working copy | SHA-256 LF blob (HEAD at the pre-checks) |
|---|---|---|
| `docs/ms11_evidence.md` | daf2820eb0cf94f4a844e45218f34f3c775fc0f0d8404d763f30d524c5515a92 | 7cc25fd51f7279144df3a5334cd7ba6c1a76dc892f9c241efed4150c1e719cb3 |
| `docs/ms11_file_hashes.csv` (771 rows; table digest 7a28624ba44cf7e960a656f89a174e0005859cf2c7766b16af735df4c6adb1e0) | c6571235b98369c89ac3a76045d6f98e83e09858ce12a2a1d2b71aafdc729d75 | c6571235b98369c89ac3a76045d6f98e83e09858ce12a2a1d2b71aafdc729d75 |
| `docs/ms11_results.md` (with the erratum, DL-402) | 02b9fe9fc6d9b0caa8dd70298fae5f92d0201d7cfa525f095ba872d90d347ade | ce8739da6357adbdccd194b15c81534e0a7f767d0fbaa4938e8a353ea121096a |
| `results/A11/a11_robustness.csv` (git-ignored output) | b4f26b003d88f7d13dcb582786da32c1a2fe4e3b8de051ce1f494e81a1d8cffb | not in git |
| MS11 result-file digest (724 files, 1192.347 MB) | cdafcc0831580ea4b9f7dfd8e095deb50e8b86db2974f556cf7ffe7d75637f53 | not in git |

The pre-checks of 11h all passed (DL-410), including the 10f digest d1b98f05b1b147437ed19ef3dc4ee84c1dda61693c9e9cc3a9de41f4ba572a52 and the five list definition hashes.

## (m) G2 and G3 status as read from the log (no decision made here)

Read at 11h (DL-416): G2 was judged at MS6 by the owner, DL-133: "So no G2 trigger fires: the project stays on M3, and M4 is robustness only, as the plan says." G3 was recommended NOT TRIGGERED at DL-261 and stated at the MS9 close, DL-271: "G3 NOT TRIGGERED (DL-261)". No later decision-log entry triggers G2 or G3 (the MS10 close triggers G4 by consequence (2), which is report-only for the run order). MS12 opens only via G2 or G3 (Table 11.1). The log therefore records neither G2 nor G3 as triggered; whether MS12 opens is the reviewer's to say.

Full test suite at 11h: 940 passed, 9 xfailed, 3 warnings, 906.44 s, pytest exit code 0, 0 deselected (DL-417).

## (n) STATE block (for pasting into a new chat)

```
STATE (MS11 closed on paper, 11h)
Repo: c:\dev\mpr-gamma-surge, branch master. Existing tags: criteria-frozen (dd8330c5eaacd63d21e7b7969430988d00862769), env-v1, replication-pass, tolerances-frozen. No MS11 tag created (create only when the user says so). Nothing pushed.
Latest commit before 11h: e189428. The 11h commit adds docs/ms11_close.md and DL-410 to DL-418.
Frozen: criteria c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05; S13 317db87e; A4_grids cf6a60be; S5_cells fe8590ce; ms11_eval_rules 4b1a1a66dba379015f6c78f5f0431bd16cfdd81bb69b925b8857f4ccc55c48a5; ms11_eval.yaml fcb439645473667b5bdd3d59f902b4e0498547af7403b79d5044a7d69d4209cf.
MS11 results: 238 runs ok (wall 1098 s). FAIL: RB2 at sigma (7 of 10), RB6 network f_pk, RB9(b) headline (4.391 Hz vs 0.5 Hz). PASS: RB2 at 0.5 sigma (8 of 10), RB5 delta_0, RB9(a), RB9(c), RB10, window line. Rest REPORTED. 26 of 26 carried checks equal. Independent check: 17 of 18 rows agree; RB9(b) map-1 cells 45 vs 51 of 760 explained by two estimators (18 cells), no further diagnostic.
Claim limits: MS11-C1 to C9; carried G4-C1 to G4-C6, MS9 and MS10 limits, G6-D1 to G6-D3.
Hashes: ms11_evidence daf2820e... (WC) / 7cc25fd5... (LF blob); ms11_file_hashes c6571235...; ms11_results 02b9fe9f... (WC) / ce8739da... (LF blob); A11 csv b4f26b00...; MS11 digest cdafcc08...7f53 (724 files); ms11_close.md hash in DL-418.
D36: 13.51 h of 24 h (basis B); basis A 14.52 h; 14.21 h UNVERIFIED.
Gates: G2 not triggered (DL-133), G3 not triggered (DL-261, DL-271), G4 triggered by consequence (2), report-only. MS12 opens only via G2 or G3.
Open housekeeping: K5, K10, K4-net coupling, D37 (open to MS15), sigma 0.0624 checked and not confirmed.
Next: reviewer decides on the MS11 tag and on MS13 (MS12 only via G2 or G3). Any diagnostic comes to the reviewer first.
```
