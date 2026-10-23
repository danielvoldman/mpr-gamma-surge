# MS9 close (9k)

Written for: the reviewer and owner who closed MS9, and the author of the paper's limitations section. MS9 is closed on paper (DL-271): **G5 passed (continue), G7 not passed with the logged claim limits, G3 not triggered, RB4 pass, RB2 / D24 failed (P-1 post hoc), D31 pass.** The MS9 gate of Table 11.1, "NC1 classified; RB4 evaluated", is met. No simulation was run at 9k, no tag was made, nothing was pushed, and no frozen criterion or evaluation rule changed (tag `criteria-frozen`, commit dd8330c, criteria SHA-256 c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05; S13 317db87e, A4_grids cf6a60be, S5_cells fe8590ce). All numbers are those of `docs/ms9_g_evidence.md` (SHA-256 85d8a3fc094525e1b101f19ed8fca34b35941ec4914df1fa01542d84f5d0104a) and the decision log (DL-210 to DL-271); the hash of every MS9 result file is in `docs/ms9_file_hashes.csv` (24,876 entries, SHA-256 53201f91af504ac10f7b441c8ede593c7a069007e8f6df5b1b0054c3c68e6a61). Pre-check at 9k: the criteria gate passes against the tag, the tree was clean, the 9j evidence sheet and the A9 v2 table (5ce4b1818e2cb79f1242803c91ca503fb740733f0880fbc1855f69b2086944a8) carry the logged hashes. The plan (`docs/plan.md`) is not edited. Readings that are ours are marked UNVERIFIED.

## (a) Sub-steps and commits

| Step | Commits | Content (DL) |
|---|---|---|
| 9a | 07e028e, 8518dc7 | timing scripts and sample, counts module, plan with M9-1 to M9-21 open, 3,618 pre-registered runs, D36 13.42 h conservative (DL-210 to DL-212) |
| 9b | c3e61f4, 317e31d, ee68f3d | rulings M9-1 to M9-21, run lists (3,618 + 132 supplementary), pooled launcher, seed key [9, 4, s]; map-1 re-timing; NC1 family run (149 ok); NC1 network run S+ stops the run (DL-213 to DL-220) |
| 9c | 2a777b7, b70ef30 | G7 triggered, map 1 held, M9-16 float64 storage; A8 review facts, S12x exploratory 19 runs (DL-221 to DL-227) |
| 9d | 5cc2584, ea2c56a | G7 ruling (not passed, A8 unchanged), claim limits, MS10 note; S16 + S6 run (100 ok), RB4 PASS (DL-228 to DL-235) |
| 9e | 9b87d43, 86a5e18 | map 1 (900 ok, 4.10 h), G5 facts, A9 labels (DL-236) |
| 9f | b2ec8b5, 7227021 | map 2 + noisy subgrid (2,575 ok, 2.12 h), D24 agreement (DL-237 to DL-241) |
| 9g | 3a837b4, bfff542 | D24 failed, M9-22 control, NC2, NC3 (2,276 ok, 23.9 min) (DL-242 to DL-248) |
| 9h | decc43f, 6ae6501 | D31 option B (178 ok, 45.7 min), post-hoc claim limit, MS11 note, P-1 (DL-249 to DL-255) |
| 9i | 66bcb64, f19cf3c | D31 pass, G5 continue, G7 not passed ruled; A7 (S6 part), A9, A10 and G3 facts files (DL-256 to DL-260) |
| 9j | 2d7603d, f933a0c, a20f02d | G3 reading, A9 v2, independent recomputation (94 of 94 items match), hash list, evidence sheet (DL-261 to DL-268) |
| 9k | the commits that add DL-269 to DL-272, `docs/ms9_file_hashes.csv` and this file | close on paper; no simulation |

## (b) Results with the pre-registered numbers

Run counts and walls are as recomputed at 9j from the stored journals and records (DL-267): 6,197 MS9 runs, all ok, 0 failed, `git.dirty = false` in every launch record, total launch wall 29,433.5 s (8.18 h).

- **G5 (map 1, mode D, 30 x 30, T_ramp 120 s):** D-tr 760 of 900 cells (84.4%), D-none 140, D-sus 0, failed 0; the pre-registered threshold was 27 of 900 (3%, M9-15). Map 2 (25 x 13): D-tr 296, D-none 29, D-sus 0, failed 0.
- **RB4 (S16):** nominal class D-tr (S5 headline run S5ramp_0000_240de3ef73be). One-at-a-time: 0 of 14 changed (limit 2). Latin hypercube: 64 of 64 unchanged (needed 52). 0 failed. The `perturbation_rel_box` 0.10 label is UNVERIFIED (frozen file).
- **NC1 (G7):** mean field (mode D) D-none at 18 of 18 (13 T_ramp at the headline cell + 5 map cells). Network run (N = 1e4, mode N, 120 s, 1 seed): S+, provisional (D8 undefined), one episode 14.0 to 16.5 s, peak 41.5 Hz. Supplementary NC1 mode N (headline cell, 10 seeds per T_ramp, feeds no gate): 124 of 130 NS, the 6 non-NS all S-rel, 0 of 40 at W = 0.2 s.
- **NC2:** D-tr at 13 of 13 T_ramp with I = 1 and with I = 0. At T_ramp 100 s onset 25.311 s against 50.418 s, duration 93.910 s against 68.806 s. **NC3** (J to -40 while eta falls; -40 UNVERIFIED, exploratory): D-none at 13 of 13 T_ramp.
- **RB2 / D24 (noisy subgrid, 225 cells x 10 seeds; sigma 0.0624 UNVERIFIED until S8):** agreement 97 of 225 cells (43.1%) on raw classes (24 ties), 118 of 225 (52.4%) on the three categories, 203 needed; per-run 1,119 of 2,250 (49.7%). Subgrid classes: S+ 475, S-rel 378, S-abs 507, S-sus 829, NS 61. P-1 (post hoc, feeds no gate): 173 of 225 cells (76.9%), per-run 1,591 of 2,250 (70.7%).
- **D31:** 178 new nodes (D-tr 112, D-none 66); 62 of 62 boundary-touching cells within 0.25 cell by our definition (UNVERIFIED); largest refined half-edge distance 0.9014.
- **S6 / A7 (S6 part):** 24 rows, all D-tr. **A9:** 0 of 1,056 surge-class map cells lack Re lambda > 0 along the path; non-surge cells map 1 140 (g 51, a 48, c 32, f 8, h 1), map 2 29 (f 16, g 13); none unlabelled under a to h. **G3:** class table in `docs/ms9_g3_facts.md`.

## (c) Gate verdicts as logged

| Gate | Verdict | Source |
|---|---|---|
| G5 | PASSED, continue | DL-258 |
| G7 | NOT PASSED; claim limits of DL-229 apply to every statement that uses a network record; A8 and every frozen criterion unchanged | DL-228, DL-229, DL-258 |
| G3 | NOT TRIGGERED (clause 2 read as M9-17: no D-sus in mode D on P2, S6, map 1 or map 2; clause 1 also fails, 26 of 27 mode-D P2 runs and 760 of 900 map-1 cells are D-tr); mode-N S-sus (44 of 130 S5 P2 mode-N runs, 829 of 2,250 subgrid runs) is a reported caveat and cannot trigger G3 | DL-261 |
| RB4 | PASS | DL-235, DL-267 |
| RB2 / D24 | FAILED, claim limit: no claim that the regime map is robust to noise; P-1 post hoc | DL-242, DL-243, DL-255, DL-257 |
| D31 | PASS under the logged boundary definition | DL-256 |

## (d) Departures and post-hoc items

Departures carried: (1) D8 estimator provisional, every D8-dependent class labelled provisional (gate departure 1); (2) zero-baseline classes, RB3(a) not judged at the headline, pure-trend-plus-noise at W = 0.2 s, short-window false surges on white noise (306, 400, 172, 24 of 500 at W = 0.2, 0.333, 0.593, 1.054 s) (gate departures 2 to 5); (3) storage in float64 instead of the plan's float32 default (M9-16, DL-223); (4) 9a timing records carry `git.dirty = true`; (5) launcher duplicate-hash behaviour for S6 P3 I_amp 1 and NC2 at 10 s (DL-224, DL-225, DL-232); (6) labels UNVERIFIED in the frozen file or the rulings: `map1_mode_that_counts` (F-26), `perturbation_rel_box`, seed keys [9, 1, s], [9, 2, 0], [9, 3, s] (reserved, unused), [9, 4, s], [9, 7, s], NC3 J_end -40, the A9 label rules (M9-12), the A4-region test (M9-13), the delay reference (M9-19); (7) G7 not passed.

Supplementary or exploratory runs, outside the pre-registered lists, feeding no gate: supplementary NC1 mode N (130 runs), two supplementary P2 references, S12x exploratory (19 runs), the M9-22 constant-parameter control (2,250 runs), D31 option B (178 runs).

Post hoc, to be reported as post hoc: A8 sensitivity variants on the NC1 network record (9 of 10 variants still give a surge class, DL-226); A9 descriptors g and h and the M9-14 category rule (DL-243, DL-244, DL-249); the mode-N claim limit (DL-250); P-1 (DL-255, DL-257); "ramp runs not NS" read as fewer than 8 of 10 NS seeds (DL-249); the D31 boundary definition (DL-254, DL-256); the J_exit,static extension on P3 and P4 (DL-263); the map-1 Hopf frequency from the A4 solver (DL-264, 852 of 900 cells, 48 have no Hopf point); the A9 v2 columns and the 9j rulings (DL-265, DL-266, DL-269).

## (e) Claim limits and limitations to carry to the paper

1. **G7 (DL-229, DL-230):** network-record surge classes at N = 1e4 under the frozen mode-N criteria are not used as evidence of a ramp-driven surge: the constant-parameter network control is flagged 10 of 10 seeds and the ramp runs 10 of 10. One flagged window at W = 2 s passes the 10-cycle minimum by construction; D8 is undefined in mode N and filters nothing; the network baseline has 4 windows with max/min 1.92.
2. **D24 (DL-242, DL-250):** no claim that the regime map is robust to noise; map statements are mode D. Mode-N evidence rests on the ramp-linked classes S+, S-abs and S-sus (control rates 1.2%, 0.9%, 0.1% against 21%, 22.5%, 37% in the ramp runs); S-rel is reported and not counted (1,095 of 2,250 control runs, 378 of 2,250 ramp runs). sigma 0.0624 is UNVERIFIED until S8 (MS10).
3. **A9 label (c) (DL-270):** label (c) uses the A4 Hopf frequency, the first estimate at onset. On the 260 D-tr map-1 cells that carry it, it is 6.57 to 24.95 Hz while the episode f_pk is 25.0 to 97.5 Hz; only 32 of the 292 map-1 cells with Hopf frequency below 25 Hz are D-none. Label (c) on a non-surge cell is a flag, not a demonstrated cause. No label is changed. Flags a and b are on no D-tr cell. The A9 failure labels are our operational rules (M9-12) on plan words.
4. **A9 check (DL-269):** it covers 1,056 of the 1,057 surge-class cells; the headline row has no stored `inside_a4_region`.
5. Every D8-dependent class is provisional; A_ref reading (a) 2.176222; the G6 claim limits G6-D1 to G6-D3 apply to any statement about onset against the entry-exit prediction (`docs/ms8_close.md`).
6. The D31 result depends on a boundary definition that is ours (DL-254); with two classes the 0.25 value is built in. J_exit,static on P3 and P4 is an extension that is ours (DL-263).
7. The P3 cost is 1.57 x the headline (9a timing). The Defender exclusion on the timing machine is user-reported only (DL-142).
8. The independent recomputation (94 of 94 items match) shares the frozen classifier code and the wording of the D24, P-1 and D31 definitions with the original runs (DL-267), so a classifier error or a misreading of that wording would not show.

## (f) Open housekeeping

| Item | State |
|---|---|
| K5 (DL-064, DL-082) | own reading, UNVERIFIED, deferred |
| K10 (DL-131 to DL-133) | definition kept, single-source claim UNVERIFIED |
| K4-net coupling (MC-03) | unsourced; the NC1 network run uses the M3 network, not the M2 coupling |
| D37 storage decision | open to MS15 (DL-223); float64 kept for MS9 (about 20 GB against "under 20 GB") |
| F-16 (RB1 at N = 3e4 against 1e4) | network check for MS10 |
| Tags and pushes | none created, none pushed |
| MS9 gate report of the plan (9m) | not written |

## (g) Measured compute and the D36 cap

Recorded MS9 walls: NC1 family 597.5 s (9.96 min); S16 + S6 1,734.4 s (28.9 min); map 1 14,755.0 s (4.10 h); map 2 + subgrid 7,648.8 s (2.12 h); 9g 1,432.8 s (23.9 min); 9h 2,740.7 s (45.7 min); S12x exploratory 524.3 s (8.7 min); sum 29,433.5 s (8.18 h). D36 cap check (24 h, whole table): **13.60 h, conservative, UNVERIFIED**, margin 10.40 h. It is a sum of mixed bases (recorded walls, Table 9.1 upper bounds where no wall was recorded, one prediction), not a measured cumulative wall; analysis, classification, A9 and recomputation time and tests are not included; the networks row keeps its upper bound although the NC1 network run is inside the recorded NC1 wall (errs high). The 9a figure was 13.42 h (DL-211). Cut order 9.3 is not triggered by the arithmetic. Full table: `docs/ms9_g_evidence.md`, section 3.

## (h) Inputs to MS10

1. **Network null-control note (DL-231, NOT decided):** network class statements (RB1, S8) need a constant-parameter control at each network configuration; to be planned at the start of MS10 and labelled a POST-HOC AMENDMENT.
2. **MS11 note (DL-251, NOT decided):** RB2 and S11 need a constant-parameter control at the headline cell for each sigma; to be planned at the start of MS11; nothing run or listed. (DL-246 is the NC2 / NC3 "run now" entry, not the MS11 note.)
3. **N = 1e4 baseline spread and specificity finding.** Spread (DL-248): in the 2,250 ramp subgrid runs (4 baseline windows, W = 2 s) the max/min of the baseline odds P_G / P_non-G has median 1.917, 90th percentile 2.689, min 1.039, max 9.934, and is at or above 2.0 in 0.436 of runs (981 of 2,250). The NC1 network baseline has 4 windows with max/min 1.92 (DL-230). Specificity (DL-227, DL-229, DL-248, DL-250): the constant-parameter network control is flagged 10 of 10 seeds, as are the ramp runs; in the mean-field control (M9-22, 2,250 runs, no ramp) S-rel occurs in 1,095 runs, so S-rel is not counted as ramp evidence, while S+, S-abs and S-sus occur at 1.2%, 0.9% and 0.1%.
4. **sigma:** 0.0624 stays UNVERIFIED until S8 checks it (DL-018, T04).
5. **Table 6.2 scope as the plan gives it:**
   - S8: Purpose "Network overlays"; Model "M3 network N = 10⁴"; What varies "P2 at ref_devalle, T_ramp {10, 120} s, 3 seeds; 4 map cells at T_ramp 30 s"; Feeds "F1, F5; σ check (σ is set at MS5)".
   - S9: Purpose "Finite size"; Model "M3 network"; What varies "N {10³, 3×10³, 10⁴, 3×10⁴} × 10 seeds; P2, T_ramp 60 s"; Feeds "FS3".
   - S10: Purpose "Heterogeneity shape"; Model "M3 network N = 10⁴"; What varies "Lorentzian, Gaussian, uniform × 3 seeds; P2, 60 s"; Feeds "FS3".
   - K8 (S3 row of Table 6.2 and Table 7.1): "N = 5×10⁴ for K8"; K8 check "ref_devalle: gamma at τ_d = 5 ms, none at 50 ms; N = 5×10⁴ network matches"; "Network peak within 5%"; the 25 to 100 Hz band is non-blocking and [reasoned, not tested].
   - Table 9.1 upper bounds for these families: S8, S10, S12 networks, K8 at N = 5×10⁴ and the σ baseline about 2.0×10¹² neuron-updates, under 30 min; S9 about 4.0×10¹² updates, 11 to 23 min at the stated rate, allowance 2 h.
