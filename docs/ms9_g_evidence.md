# MS9 evidence sheet for G5, G7 and G3 (facts and logged recommendations only)

Status: written at 9j from the stored records, the decision log (DL-210 to DL-267) and the independent recomputation (DL-267: 94 items, 94 MATCH, 0 DIFFERENCE). Nothing was simulated or launched at 9j. This sheet adds no ruling and no verdict: where a ruling exists it is quoted with its DL number; where the plan gives no number, the criterion is stated in words. `docs/plan.md` is not edited. Every reading that is ours is marked UNVERIFIED. `docs/ms9_close.md` is not written.

Frozen state: tag `criteria-frozen` (commit dd8330c), criteria SHA-256 c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05, secondary files S13 317db87e, A4_grids cf6a60be, S5_cells fe8590ce; the loader verified the freeze at the start of 9j and before each analysis run. Frozen threshold 0.217622 (0.1 x A_ref 2.176222, reading (a)). No frozen criterion was changed at MS9 (DL-228, DL-257).

## 1. Gate statements and the facts behind them

| Item | Statement (source) | Facts |
|---|---|---|
| G5 | CONTINUE (DL-258, ruled) | Map 1 (mode D, 30 x 30, T_ramp 120 s): D-tr 760 of 900 cells (84.4%), D-none 140, D-sus 0, failed 0; threshold 27 of 900 (3%, M9-15). RB4 passed (next row). Map 2 (25 x 13): D-tr 296, D-none 29, D-sus 0, failed 0. |
| RB4 | PASS (DL-235; recomputed, DL-267) | Nominal class D-tr (S5 headline run S5ramp_0000_240de3ef73be). One-at-a-time: 0 of 14 changed (limit 2). Latin hypercube: 64 of 64 unchanged (needed 52). 0 failed. All 78 runs D-tr. The `perturbation_rel_box` 0.10 label is UNVERIFIED (frozen file). |
| G7 | NOT PASSED, claim limits of DL-229 (DL-228, DL-258, ruled) | NC1 mean field (mode D): D-none at 18 of 18 (13 T_ramp at the headline cell + 5 map cells). NC1 network run (N = 1e4, mode N, 120 s, 1 seed): S+, provisional (D8 undefined), one episode 14.0 to 16.5 s, 128 cycles by the formula, peak 41.5 Hz. Supplementary NC1 mode N (headline cell, 10 seeds per T_ramp, feeds no gate): 124 of 130 NS, the 6 non-NS all S-rel, 0 of 40 at W = 0.2 s; per T_ramp non-NS: 10 s 1, 177.8 s 1, 316.2 s 1, 562.3 s 1, 1000 s 2, all others 0. A8 and every frozen criterion unchanged (DL-228). S12x (exploratory, DL-227): the constant-parameter network control is flagged 10 of 10 seeds and the ramp runs 10 of 10 (DL-229). |
| G3 | NOT TRIGGERED, recommended (DL-261); the formal statement is made at the MS9 close | Clause 2 read as M9-17: P2-based runs that keep oscillating after J = 0 with no end (D-sus in mode D). Mode D has no D-sus on P2, S6, map 1 or map 2. Clause 1 also fails: 26 of 27 mode-D P2 runs and 760 of 900 map-1 cells are D-tr. Mode-N S-sus (44 of 130 S5 P2 mode-N runs, 829 of 2,250 subgrid runs) is a reported caveat and cannot trigger G3 (DL-261). Class table: `docs/ms9_g3_facts.md`, `results/A10/g3_facts.csv`. |
| RB2 / D24 (subgrid part) | FAILED, claim limit (DL-242, DL-243, ruled); P-1 is post hoc and feeds no gate (DL-255, DL-257) | Frozen D24, agreement of the noisy subgrid (225 cells x 10 seeds, sigma 0.0624 UNVERIFIED until S8) with the deterministic class under Table 2.1: 97 of 225 cells (43.1%) on raw classes (24 ties), 118 of 225 (52.4%) on the three categories (modal category, tie = disagreement), 203 needed; per-run 1,119 of 2,250 (49.7%); 84 cells with 8 of 10 seeds or more. Subgrid classes: S+ 475, S-rel 378, S-abs 507, S-sus 829, NS 61. P-1 (POST HOC: S+, S-abs, S-sus matched to D-tr, S-rel and NS to D-none): 173 of 225 cells (76.9%), 16 ties, D-tr 171 of 188, D-none 2 of 37; per-run 1,591 of 2,250 (70.7%). Claim limit (DL-242): no claim that the regime map is robust to noise; map-1 and map-2 statements are mode D. |
| D31 (grid resolution) | PASS under the logged boundary definition (DL-256, ruled; UNVERIFIED, reading ours) | 178 new nodes (45 mixed map-1 blocks): D-tr 112, D-none 66. 46 coarse boundary edges, 85 refined half-edges; 62 of 62 boundary-touching cells within 0.25 cell; no refined half-edge 1 cell or more from a coarse edge midpoint (largest 0.9014). The 0.25 follows from the definition with two classes (DL-254 note); the informative number is 0.9014. Supplementary list outside the frozen 1,226 cells; feeds no gate. |
| A10 NC1 to NC3 | Facts, no verdict (DL-220, DL-248, DL-252, DL-267) | NC1: see the G7 row. NC2 (P2 with I = 0 against I(t) on, I_amp 1): D-tr at 13 of 13 T_ramp in both arms; onset earlier and the surge longer with I = 1 (T_ramp 100 s: onset 25.311 s against 50.418 s, duration 93.910 s against 68.806 s; the same direction at the other T_ramp, `results/ms9/9g/nc2_table.csv`). NC3 (J to -40 while eta falls, exploratory, -40 UNVERIFIED): D-none at 13 of 13 T_ramp ("envelope never reaches the threshold"). The `a10_controls.csv` G7 status field reads "not passed (network S+)" on all 58 rows. |
| S6 / A7 (S6 part) | Facts (DL-235, DL-260, DL-262) | 24 rows (20 pre-registered, 2 supplementary P2 references at 30 s and 300 s, 2 S5 comparators at 10 s and 120 s); all D-tr. J_exit,static on P3 and P4 is a labelled UNVERIFIED extension (DL-263); it is the same on all P3 runs (-2.5303, the P2 value). |
| A9 | Facts (DL-236, DL-244, DL-249, DL-266) | 0 of 1,056 surge-class map cells lack Re lambda > 0 along their path (no ramp artefact; map 1 760, map 2 296; the headline row has no stored value for this field). Non-surge cells: map 1 140 (failure_label g 51, a 48, c 32, f 8, h 1), map 2 29 (f 16, g 13); none unlabelled under a to h. Structural flags on surge-class cells: map 1 260 of 760 carry the flag c alone (A4 Hopf frequency 6.57 to 24.95 Hz; episode f_pk 25.0 to 97.5 Hz), map 2 0 of 296; flags a and b are on no D-tr cell. |

## 2. Run counts and walls (recomputed from the stored journals and records, DL-267; all runs ok, 0 failed, git.dirty = false in every record)

| Family | Runs | Launch wall |
|---|---|---|
| NC1 family (19 pre-registered + 130 supplementary mode N) | 149 | 597.5 s (9.96 min) |
| S16 (78) + S6 (20) + 2 P2 references | 100 | 1,734.4 s (28.9 min) |
| S7 map 1 | 900 | 14,755.0 s (4.10 h) |
| S7 map 2 + noisy subgrid | 325 + 2,250 | 7,648.8 s (2.12 h) |
| 9g: M9-22 control (2,250, exploratory) + NC2 (13) + NC3 (13) | 2,276 | 1,432.8 s (23.9 min) |
| 9h: D31 option B | 178 | 2,740.7 s (45.7 min) |
| S12x exploratory (9c; outside the lists) | 19 | 524.3 s (8.7 min) |
| **Total** | **6,197** | 29,433.5 s (8.18 h) |

(6,197 = 149 + 100 + 900 + 2,575 + 2,276 + 178 + 19. DL-267 classified 6,211 records because it also read the 13 S5 P2 linear runs and the S5 headline run, which are MS8 records.)

## 3. D36 cap check (24 h, whole table), updated at 9j; conservative, UNVERIFIED

Mixed bases, as at 9a (DL-211): recorded walls, Table 9.1 upper bounds where no wall was recorded, and one prediction. It is a sum, not a measured cumulative wall (MS8 close (f)). Analysis, classification, A9 and recomputation time are not included (no timing cell exists for them; classification of the 3,618 MS9-list runs cost 265 s, DL-218). The networks row keeps its upper bound of 0.5 h although the NC1 network run is now inside the recorded NC1 family wall (a double count that errs high).

| Part | Basis | Hours |
|---|---|---|
| S5 ramp family | recorded 52.9 min (DL-175) | 0.8817 |
| S13 headline subset | recorded 26.3 min (DL-178) | 0.4383 |
| S5 baseline-only | recorded 147.8 s (DL-143) | 0.0411 |
| S1 to S4, A1 to A6 | Table 9.1 upper bound | 0.5000 |
| S2 | 3-minute prediction (DL-168) | 0.0500 |
| Networks (S8, S10, S12) | Table 9.1 upper bound | 0.5000 |
| S9 | Table 9.1 upper bound | 2.0000 |
| Rest of S13 | Table 9.1 upper bound (the recorded headline part counted again) | 1.0000 |
| NC1 family | recorded 9.96 min | 0.1660 |
| S16 + S6 | recorded 28.9 min | 0.4818 |
| S7 map 1 | recorded 4.10 h | 4.0986 |
| S7 map 2 + subgrid | recorded 2.12 h | 2.1247 |
| 9g control, NC2, NC3 | recorded 23.9 min | 0.3980 |
| 9h D31 | recorded 45.7 min | 0.7613 |
| S12x exploratory | recorded 8.7 min | 0.1456 |
| S11 (MS11, not launched) | 9a prediction 27 s | 0.0075 |
| **Total** | | **13.60 h** against 24 h; margin 10.40 h |

Against the 9a figure of 13.42 h (DL-211): the recorded MS9 walls (8.18 h) replace the 9a predictions for the MS9 families (8.00 h: S6 0.16, map 1 4.45, map 2 + subgrid 2.60, S12 mean field + S16 0.71, NC1 network 0.08); the recorded figure also holds work 9a did not count (D31 0.76 h, S12x 0.15 h, and the M9-22 control inside the 9g wall). Cut order 9.3 is not triggered by the arithmetic. "Never cut": NC1 and the one-at-a-time part of S16 (both done).

## 4. Departures from the plan and post-hoc items (all logged)

Departures and gate departures carried (UNVERIFIED where marked):

1. D8 estimator provisional: every D8-dependent class carries the label "provisional" (gate departure 1; DL-137). Includes the NC1 network S+.
2. Zero-baseline classes; RB3(a) not judged at the headline; pure-trend-plus-noise at W = 0.2 s; short-window false surges on white noise (306, 400, 172, 24 of 500 at W = 0.2, 0.333, 0.593, 1.054 s; 0 of 500 at 2 s) (gate departures 2 to 5, `docs/ms9_plan.md`).
3. Storage in float64, the MS8 writer, instead of the plan's float32 default (M9-16, DL-223; about 20 GB against "under 20 GB"). The storage decision D37 is open to MS15.
4. The 9a timing records carry git.dirty = true; they are timing-only records (9b standing ruling).
5. Launcher duplicate-hash behaviour: S6 P3 I_amp 1 at 10 s and NC2 at 10 s share a config hash and each ran in its own out_dir, one extra 10 s run (DL-224, DL-225, DL-232).
6. Labels UNVERIFIED in the frozen file or the rulings: `map1_mode_that_counts` (F-26), `perturbation_rel_box`, the seed keys [9, 1, s], [9, 2, 0], [9, 3, s] (reserved, unused), [9, 4, s], [9, 7, s], NC3 J_end -40, the A9 label rules (M9-12), the A4-region test (M9-13), the delay reference (M9-19).
7. G7 NOT PASSED (outcome): claim limits of DL-229 apply to every MS9 statement that uses a network record.

Supplementary or exploratory runs, outside the pre-registered lists, feeding no gate: supplementary NC1 mode N (130 runs, M9-4); two supplementary P2 references (M9-9); S12x exploratory (19 runs, DL-227); the M9-22 constant-parameter control (2,250 runs, DL-245); D31 option B (178 runs, DL-253).

Post-hoc items, to be reported as post hoc: A8 sensitivity variants on the NC1 network record (9 of 10 variants still give a surge class; DL-226); A9 descriptors g and h (DL-244, DL-249) and the M9-14 correction to the modal-category rule (DL-243); the claim limit that mode-N evidence rests on the ramp-linked classes S+, S-abs and S-sus with S-rel reported but not counted (control rates 1.2%, 0.9%, 0.1% against 21%, 22.5%, 37% in the ramp runs; DL-250); P-1 (DL-255, DL-257); "ramp runs not NS" read as fewer than 8 of 10 NS seeds (DL-249); the D31 boundary definition (DL-254, DL-256); the J_exit,static extension on P3 and P4 (DL-263); the map-1 Hopf frequency from the A4 solver evaluated at each cell (DL-264, 852 of 900 cells; 48 have no Hopf point); the A9 v2 columns (DL-265, DL-266).

## 5. Known limitations to carry to the paper

1. Network-record surge classes at N = 1e4 under the frozen mode-N criteria are not used as evidence of a ramp-driven surge (DL-229 (1)). One flagged window at W = 2 s passes the 10-cycle minimum by construction; D8 is undefined in mode N and filters nothing; the network baseline has 4 windows with max/min 1.92 (DL-230).
2. Mean-field NC1 passes (18 of 18 D-none); the supplementary mode-N NC1 has 6 of 130 non-NS (all S-rel), none at W = 0.2 s (DL-229 (2)).
3. The noisy subgrid does not agree with the deterministic classes by the frozen D24 (97 of 225 on raw classes, 118 of 225 on categories, 203 needed); no claim that the regime map is robust to noise; map statements are mode D (DL-242). The constant-parameter control shows S-rel in 1,095 of 2,250 runs without a ramp, so S-rel is not counted as ramp evidence (DL-248, DL-250). sigma 0.0624 is UNVERIFIED until S8 (MS10).
4. Every D8-dependent class is provisional; the A_ref reading (a) 2.176222; the G6 claim limits G6-D1 to G6-D3 apply to any statement about onset against the entry-exit prediction (`docs/ms8_close.md`).
5. The A9 failure labels are our operational rules (M9-12) on plan words; 48 map-1 cells have no A4 Hopf point; 260 D-tr cells carry the flag c (A4 Hopf frequency below 25 Hz) while the episode peak frequency is in the classifier band 25 to 100 Hz. Not interpreted here.
6. The D31 result depends on a boundary definition that is ours (DL-254); with two classes the 0.25 value is built in.
7. J_exit,static on P3 and P4 is an extension that is ours (DL-263); on P3 it equals the P2 value.
8. The P3 cost is 1.57 x the headline (9a timing). The Defender exclusion on the timing machine is user-reported only (DL-142).

## 6. Open housekeeping

| Item | State |
|---|---|
| K5 (DL-064, DL-082) | own reading, UNVERIFIED, deferred |
| K10 (DL-131 to DL-133) | definition kept, single-source claim UNVERIFIED |
| K4-net coupling (MC-03) | unsourced; the NC1 network run uses the M3 network, not the M2 coupling |
| D37 storage decision | open to MS15 (DL-223); float64 kept for MS9 |
| MS10 note (DL-231), NOT decided | network class statements (RB1, S8) need a constant-parameter control at each network configuration; to be planned at the start of MS10 and labelled a POST-HOC AMENDMENT |
| MS11 note (DL-251), NOT decided | RB2 and S11 need a constant-parameter control at the headline cell for each sigma; to be planned at the start of MS11; nothing run or listed |
| F-16 (RB1 at N = 3e4) | MS10 |
| Tags and pushes | none created, none pushed |
| Not written | `docs/ms9_close.md`; the MS9 gate report of the plan (9m) |

## 7. SHA-256 of the MS9 files

Group digests: SHA-256 of the sorted `path<TAB>sha256` lines of the group (script `scripts/hash_ms9_results.py`, DL-267). The per-file list of all 24,876 files is `results/ms9/9j/file_hashes.csv` (git-ignored, SHA-256 53201f91af504ac10f7b441c8ede593c7a069007e8f6df5b1b0054c3c68e6a61); the group digests are in `results/ms9/9j/file_digests.txt` (SHA-256 63f3d0cf3d47b28f488bb7dc45be15969799779d0867cb6fa83076da6b7888cc).

| Group | Files | Bytes | Digest |
|---|---|---|---|
| Records S12 (NC1, NC2, NC3, supplementary) | 700 | 0.946 GB | 8d5459408d298405de91ad61489e8266dcaf9c6db7db30b13d7a2c0e5a84c828 |
| Records S12x (exploratory: NC1 network, constant-parameter network, M9-22 control) | 9,076 | 8.740 GB | ad3a37bc2ff310b574fdf28612467e2d1f55cc9fd5b4efc12950a0facbf39293 |
| Records S16 | 312 | 0.366 GB | 211a363d8d917a2f73d0a6888740cfe62edf6365ed726b95ec79e2b40b5eba21 |
| Records S6 | 88 | 0.103 GB | 4302f56cce60a814da0dffe99428e084d4fb50b5a3dc0bd8e1f61ac0c59a0898 |
| Records S7 (map 1, map 2, subgrid) | 13,900 | 16.665 GB | 02b70bc148d321beeb4fc7c18203f07f4d9e07ece71114c2c9edcb8fc184cb23 |
| Records D31 | 712 | 0.707 GB | e7ca4f66d87374f612b0e80b47fff534281cc4dff86e04e4c768043d6f56cda8 |
| results/ms9 (journals, class tables) | 44 | 0.003 GB | d70ada22338f452b1d4590459db20861d1deafa318fc8a13378bd922f9c3179f |
| A7 (S6 part), A9, A10 tables | 7 | | e3ed298bbc42a841d7122ee1049bfb4365b280eb56fc7beddd577e9a49d7776f |
| configs/ms9 (configs, run lists, cell files) | 36 | 0.003 GB | 09594c7a17ab2ddf570eaa2d3824dd3cdcd57754f1808cc95841123a3b32ea91 |
| docs/ms9_g3_facts.md | 1 | | a4f1293d9647c32ab176f2262d391e550015c69c166a5a26e38284ed1e564475 |

9j outputs (written after the hash list, so not in the digests): `results/A9/a9_regime_map_v2.parquet` 5ce4b1818e2cb79f1242803c91ca503fb740733f0880fbc1855f69b2086944a8 (1,226 rows, 29 columns; the stored `a9_regime_map.parquet` 7ed857c12ba208a23d3e1dc2fc463606ff612ea9d912b41e80f4cbc1c2997b06 is unchanged); `results/ms9/9j/a9_v2_report.txt` 5df640357385b69b9ffee199f91477c96ad0242b2c707da1d9af159f4ef148e7; `results/ms9/9j/recompute_report.txt` 10faa7ed7add8c0cd4d3b87229681d1449fd86198b1fbfcda72646db2fb200b5; run record `results/ms9/9j/MS9_9j_b81c51be5f86.json` a5b99844682240d46ec504a4129aac7a0a75dc5068bee3837641a2533f608ad1.

Frozen cell list: 1,226 cells, SHA-256 8e67bbd2b366e86ffee59e732dd79824bdce82c73c477436cb3b1689b0a328d9 (unchanged, DL-141, DL-236).

### 7.1 results/ms9 files

| File | Bytes | SHA-256 |
|---|---|---|
| results/ms9/9c/nc1_net_variants.csv | 1360 | cac69254f8117d44bea50a66fce8bf722f4f78e24962eea409e4f053240d8597 |
| results/ms9/9c/nc1_net_windows.csv | 16488 | 207e5876772f5461ab0546694df47fab5e369c8bffe75ae5ef6a2ee967bc495e |
| results/ms9/9c/s12x_table.csv | 6348 | ac7297e63cb6e897c481fe8c1db28a9a7d558c6342f9bcd27575bb732bb662ec |
| results/ms9/9d/rb4_runs.csv | 5740 | dc385c863c4e92cd8cda17314e2399838531f14ef9d02e9e8b96f2a5dd7f91e1 |
| results/ms9/9d/rb4_summary.json | 203 | 22b58a9e8e770c08f95767ceb23be19e9866769a5c0988a110609171cbe3c7c4 |
| results/ms9/9d/s16_classes.csv | 31274 | 1b61b864a93e877e00e2fb3fc1981b83ba083bcb4bbce60983e633764f395588 |
| results/ms9/9d/s5_headline_classes.csv | 629 | 6d82d43e6914017b6a1e3d2f43b9ce6851b5a82cb3e05adc99fc9e682b267c25 |
| results/ms9/9d/s5_p2_classes.csv | 5172 | 67e19cc60e69fc6d3f72267030b9675761d7a39ab38381228e009e5ed051beda |
| results/ms9/9d/s6_classes.csv | 8090 | 581aa1cdbf6bea04ca75ea679e41c720e4e0deade628ae400dde1cd307d9c223 |
| results/ms9/9d/s6_table.csv | 2036 | 590ec60400243b24a19d0ad16fcb16ca3cb064f7306262144a7c086a3d12d0c0 |
| results/ms9/9e/map1_classes.csv | 167846 | d16d85e49dde4cbb0b1a89171a8e411b7204c7d227f61d6310a42e9a8dac37f5 |
| results/ms9/9f/map1_unlabelled_diag.csv | 11033 | 5c1f0cf9af3cb9d7c836a161533608e738981af78b86a1be8e8c2c7f74aaa923 |
| results/ms9/9f/map2_classes.csv | 63324 | 7eee10e1779ffeccc09e9f18c464ce645682134f1ab814af969627a54fefe2cb |
| results/ms9/9f/subgrid_cells.csv | 15745 | fd1025e1e35bdc0e23403e39747815488e7cbbcdf5c55d68ed8e37a6777982db |
| results/ms9/9f/subgrid_classes.csv | 232817 | f907c9fd53ac05d2b9ed16cd8203f3ecdec9a5e5f8c3048171e580e2d0459698 |
| results/ms9/9f_report.txt | 21268 | 57e3eb84f466fb3b931fa29a829c3c76e58c6633b15b605f5da3a9f2dd24c4e5 |
| results/ms9/9g/a9_gh.csv | 13732 | 9921619e7c252865db09382f3aa55cb82722a8ed3e618ec441214e825575faaa |
| results/ms9/9g/control_cells.csv | 20456 | 776bdbc64448ab5a2ce5584cc37015dcdec4f1e2e718d103c8189d65b0ed887c |
| results/ms9/9g/control_classes.csv | 223142 | 55bfe77c67991775557594a53dbea3fed68e074e0371f0fefa9af317470e3685 |
| results/ms9/9g/nc2_table.csv | 1870 | 2c7bffc401e20f5ccc73bdeaa87bb888e047acc62e22197405d80d31614f1e1c |
| results/ms9/9g/nc3_table.csv | 996 | 8fb5c4926bd909b49ce664fd8599ceb0794b4b9018660642d67e25b5ac73fd0a |
| results/ms9/9g/ramp_baseline_spread.csv | 204731 | ae5ecfc60afd1f4e4bd0eab93dc04c628b506723fba1dfae7a432051261da602 |
| results/ms9/9g_report.txt | 5677 | 702468d675869eaf64aabb4519e202e1ac3022ab509c2dc6e20eee4f8978d644 |
| results/ms9/9h/d31_boundary_cells.csv | 1156 | 8bcf5ef5663165e78886466300e6670e31733179180fd7e81644477c9f344c55 |
| results/ms9/9h/d31_classes.csv | 20745 | a490fefa9046e8be92d609554b6c98da0b55ecf41e2172d5336f19b239e0dc19 |
| results/ms9/9h/p1_cells.csv | 5911 | 479d89410a7c5a8ace2ea2602b066ea68e1e7d9f0b3103a1d6a1d9666b7ad46c |
| results/ms9/9h_report.txt | 12383 | 1d33230d5e3d0ebb7b36a3142da2cd4022aaf4e0b4929a750e6aeab9aa339d5c |
| results/ms9/9i/consistency.txt | 166 | 2b289a4ce448c15549b5d6ff653113ba295b9ba38b21c2c6e6350a146c62da08 |
| results/ms9/9i/MS9_9i_b81c51be5f86.json | 8455 | bd1e37248b41098ceb0148566031aa3ecb24a117d302d4f01d1c9d1415207e8e |
| results/ms9/launch_9g/manifest.csv | 141880 | b0bc69d5d2682a452e93ef361ca4872b6f9a372810d05e194748da5932618dc0 |
| results/ms9/launch_9g/run.log | 368568 | 1858ff6af6e0366189c4a6cb55d675820948da8e6db27103be8d4e4ef57925d5 |
| results/ms9/launch_9h/manifest.csv | 24322 | 29fa7450ab88b658fb70433758707a50cb0f74487ffaae8afc9dd55bb0f8eb3c |
| results/ms9/launch_9h/run.log | 27840 | 7276ba9241f996a582ed425b16da60a95ca9d2afb593cd0445e8fb6b562f761e |
| results/ms9/launch_map1/manifest.csv | 122336 | d34c86175b39c3c7bae8a0348d61c7d83cbbc4bc1b8881e5dd4715856e3c9401 |
| results/ms9/launch_map1/run.log | 138796 | ebd153dac7e455e29d99832ba2890508de148f8ea3fdac68d1b74f9d7ffb85d7 |
| results/ms9/launch_map2_subgrid/manifest.csv | 178286 | 5efb4c01affd66bd750aa60f1ee3f52fe7b5822d016a3fc2c8a3d9b90c69222a |
| results/ms9/launch_map2_subgrid/run.log | 406241 | bb1d50a85a05d6a732bc61db14c4d9cce9aac0745282650b8d9c27707b5b3b64 |
| results/ms9/launch_nc1/manifest.csv | 9926 | 054814329c9d3ffbf5aba7417534f752f58fdc3aa0bd232c720d1f4ade205280 |
| results/ms9/launch_nc1/run.log | 23158 | 19bd14da842f666c3bea7bf2e759118dcf02c858d191f886dc114aee65db10eb |
| results/ms9/launch_s12x/manifest.csv | 1234 | f77a7d45a8e5d76890630fc20aee4ea3ab82a95e05e81da65922bceff9d4cf6f |
| results/ms9/launch_s12x/run.log | 3236 | dd00ccc7f8df8aecd2a380aa28a5a9f96f7a572adb690e2aa0ef80418a07b666 |
| results/ms9/launch_s16_s6/manifest.csv | 13495 | 7cccad8f92dba094053db786f092ff37ec84d30b83f9aff86d94b49cc995d358 |
| results/ms9/launch_s16_s6/run.log | 15389 | 451ec2e700761cb5ec3746e4aa918da2dced360757bfac785c465c3c5c3e7e34 |
| results/ms9/nc1_classes.csv | 47227 | 77055e82184fa9f769e502469b9276c3133bebdc7444b534c59b571a47b2d097 |

### 7.2 A7, A9, A10 tables and the G3 facts text

| File | Bytes | SHA-256 |
|---|---|---|
| results/A7/a7_s6_metrics.parquet | 28449 | 9f384fdf5f8c7ead2621e504128684ff2238b6278e630f6e7db30543d870bfa4 |
| results/A9/a9_d31_refined_nodes_supplementary.parquet | 20601 | af27c676a6cdf9036349d75ca4403ba36d38fd939c0124f62a328fd4c5b80256 |
| results/A9/a9_regime_map.parquet | 76362 | 7ed857c12ba208a23d3e1dc2fc463606ff612ea9d912b41e80f4cbc1c2997b06 |
| results/A9/a9_regime_map_v2.parquet | 84135 | 5ce4b1818e2cb79f1242803c91ca503fb740733f0880fbc1855f69b2086944a8 |
| results/A9/a9_subgrid_agreement.parquet | 15501 | 6d53d4c7dc401a899d2e41889153c9942eab1a670122ed1cd1ee29fc759fcd3e |
| results/A10/a10_controls.csv | 9734 | b9139af697b5485a6e6e0748632909c8fd1d4c59967484dee530c5d2be716ef4 |
| results/A10/g3_facts.csv | 1115 | ff90d22a7c9b2ddc27fa70a881223a0f3de15954ae317ac1eafada79f42abb23 |
| docs/ms9_g3_facts.md | 1670 | 4a9a407272029fec710ac225d9dc9a41430036e0c1f2d1ab854c1866abbf8b07 |

### 7.3 configs/ms9 (configs, run lists, cell files, seed and design files)

| File | Bytes | SHA-256 |
|---|---|---|
| configs/ms9/9i_tables.yaml | 594 | e1b374f0bc83b9114a5efe26e094cde31f7bb28ca8940703d56522670a7b8143 |
| configs/ms9/nc1.yaml | 856 | 0f74f90cde5e5b3f381e938f13140bc655a6bb3ca87e7093fb898ccaa8306540 |
| configs/ms9/nc1_modeN.yaml | 814 | 01aae9924147db95f1c8b91046f599e54ac4c6ef6f9d119933db6fa440ce22bf |
| configs/ms9/nc1_net.yaml | 751 | db18803f1ff6e8fc703c963bedbc82a4f3da330d61090412cc15d6c7b15d056b |
| configs/ms9/nc2.yaml | 800 | f38e6d20b929e082ad596acc802b77a975ce102f6fb14317862bc99fec4dd438 |
| configs/ms9/nc3.yaml | 897 | fbddf2f62e8fea9a70e037244d6737d7693a05be9b896f2e727ce9c23bf33cfa |
| configs/ms9/runlists/cells_1226.csv | 151262 | 1379952a695d0e269abd13e75505151c5a03484548f667eb15caf72ec301ad8a |
| configs/ms9/runlists/cells_d31.csv | 23714 | b7ade8fbc5a5df7282f7deeade6f929c7e7183e32bc63f3b77e265cd87132d35 |
| configs/ms9/runlists/ms9_9g_runlists.json | 1169 | 720b7ccf0702116f76f8b2af237482efd2a8f75cb4f07afb384854ccd66ab953 |
| configs/ms9/runlists/ms9_9h_runlists.json | 1158 | 9e160c899fe22c9050c5735a472feaeaf60d97cf40570892805a1cbcbb15064b |
| configs/ms9/runlists/ms9_runlists.json | 3226 | d7b651c8b12a2646ce963008d808d452a4157627451bd0cb19121ab230742a50 |
| configs/ms9/runlists/ms9_s12x_runlists.json | 1396 | 945ab0fcb82412f9b8f2021bfa7c6f54002a3de5b74ed6fb6bea1fa19652557f |
| configs/ms9/runlists/runlist_D31_half.csv | 76813 | 2ad3414d4e73f4cb50308fd1cec368d4e60fc65094edeae51c518a7844273616 |
| configs/ms9/runlists/runlist_NC1.csv | 7587 | f6455f2cc7be7e01828a0e37a6c84b8404aa549c3477730a062452192a7d27ce |
| configs/ms9/runlists/runlist_NC2.csv | 3531 | 6e079d85e159709402167263a0415eb4d7a1f37d15a067834a11558d156acb06 |
| configs/ms9/runlists/runlist_NC3.csv | 5195 | c4427bd3b4bb8c3aee98fa034a80ef0d049e6380ac81083f901a85d0b63dc7dc |
| configs/ms9/runlists/runlist_S12x_const_net.csv | 4877 | 1a7732016efc3d24ce55efdeed874342fa36db59c1b9cc9985523662ce0b72cc |
| configs/ms9/runlists/runlist_S12x_ctrl_mf.csv | 1278647 | f73824403ce0b14cc65f349f1bacc1a0a53e6438ed721f48d2542554dca63981 |
| configs/ms9/runlists/runlist_S12x_NC1_net.csv | 4309 | 007d9fd0640ac56dc78b365baeac3ccb1660209854e6bdd469bc94d79a7a2ea1 |
| configs/ms9/runlists/runlist_S16.csv | 44141 | 6fd829877b42dc8a4d49af11709ef8c634c4bdffcf89e074dbc2432a855268b5 |
| configs/ms9/runlists/runlist_S6.csv | 5483 | 7c787fc68b09a993c0c6a06758389cb7d402cce4ef6bd836e440f49ecf3037e4 |
| configs/ms9/runlists/runlist_S7_map1.csv | 380071 | 9c984e10df1d13f2a265851a84febf8d6401d7943a2cf47cd67b5c02a958b35c |
| configs/ms9/runlists/runlist_S7_map2.csv | 139712 | d23cc8f82283a98b523e2354971b78c2d914802f9d340ba152563676d9f3fafb |
| configs/ms9/runlists/runlist_S7_subgrid.csv | 1091087 | fe16f68af4c5260b02791877c06fe897a49ae760fe4738276d93da6b68f9fdc5 |
| configs/ms9/runlists/runlist_SUPP_NC1_modeN.csv | 63287 | cd1d1721d0945b3be5b858ab272997cfc7ab005e3ed984c424bb9bb38614390b |
| configs/ms9/runlists/runlist_SUPP_P2ref.csv | 675 | 55b3b1e4e805cd95ab7997bec3d9328ca3b2bfd4f7fdc9179b576f00a10f2d37 |
| configs/ms9/runlists/s16_lhs_design.csv | 8692 | 1c201665494ba98f267d8f4b3343e64731e93910484dc4a979ce8953b3561e40 |
| configs/ms9/s12x_ctrl_mf.yaml | 1006 | 74d8613543fe1ae7f0394a905b380c177209d18b9b353c39307a6bda36d5ddcc |
| configs/ms9/s12x_net.yaml | 931 | 8fc5fec7adab2782e59cf67f8120d96cba563e74915df640117fe3cfec642d66 |
| configs/ms9/s16.yaml | 920 | 7d1ee650e85a77e7885b2d9968cd7d71145ef0c21ec4d6165b8a31dabb6cf2a1 |
| configs/ms9/s6_p2ref.yaml | 758 | 2bbd06149904ab6084000367d6277f1b9000fc4f682a8294dd418a8fdfb236cb |
| configs/ms9/s6_p3.yaml | 815 | 9592cf8c00c67f3785df870a4752e3825780b4a0d2c1bfd314a0c60d724b918a |
| configs/ms9/s6_p4a.yaml | 858 | 1e266b8a3b7bba40efd500cafaf21dfe222002697a20f8bee95c3f45c7e2480c |
| configs/ms9/s6_p4b.yaml | 727 | eb21fd3113a9bda49f184c31841dc0156feed2d6b41797aeedaed0dcd269203e |
| configs/ms9/s7_map.yaml | 840 | e8ade816433523ec01e4d4aaf3e6871d1da05a8f14960cbbaa7f899600a833ac |
| configs/ms9/s7_subgrid.yaml | 784 | f9bfa577a6931bec4df8878aa89833b1e8b97509df0482f039c985be91fd9f36 |
