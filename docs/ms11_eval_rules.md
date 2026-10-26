# MS11 evaluation rules (11b; written before any MS11 run)

Status: written and frozen at 11b (DL-343, DL-344) except the 14 required fields listed in section 12, which are open for the reviewer's rulings and which stop a real launch while open. Binding sources: `docs/plan.md` (Table 2.1, Table 7.2 RB2, RB5, RB6, RB9, RB10, the A11 evaluation paragraph, Table 6.2 S11 and S13, Table 9.1, 9.2, 9.3, D24, D36, D43), the frozen criteria (`configs/robustness_criteria.yaml`, tag `criteria-frozen`), the rulings R1 to R33 and the 11b rulings (DL-336, DL-337). This file adds no criterion, changes no threshold and reopens no ruling. Where the plan gives no number the criterion is stated in words and is a required field, not a choice made here. Thresholds are read from the tag's blob by the evaluators and are not typed in `configs/ms11/ms11_eval.yaml` (a test checks this). No MS11 evaluator is written at 11b; these rules say what they will compute. Nothing is simulated or launched at 11b.

The ruled and open values are in `configs/ms11/ms11_eval.yaml` (`choices`, with `meta` giving status and source of each). A null or absent value raises `MissingChoice` (`src/mprsurge/analysis/ms11_eval_choices.py`); nothing is defaulted.

## 0. What every MS11 evaluator does first

1. The criteria loader gate (tag `criteria-frozen`) must verify; the thresholds are read from the tag's blob.
2. Any MS11 data file (the four list definition files, the list-hash file, the four run configs) that is not FROZEN, and any required field of `ms11_eval.yaml` that is open, stops the evaluation.
3. Records are looked up by the rows of the frozen lists (`configs/ms11/ms11_list_hashes.yaml`), by name. A record is refused if its git dirty flag is not exactly false, if it is a dry-run record, if its full config hash or name differs from the frozen row, or if its criteria SHA-256 is not the frozen one. A listed record that is absent is reported missing and every part that needs it is INCOMPLETE; it is never replaced. A record whose status is not ok is class `failed` (A9, never NS).
4. Labels attached to every output: "sigma checked, not confirmed" (G4-C4, sigma 0.0624) on every noisy mean-field result; "provisional (D8 open, DL-137)" on every class that went through a D8 call; the short-window false-surge rates per W (306, 400, 172, 24 of 500 at W = 0.2, 0.333, 0.593, 1.054 s; frozen criteria) beside the S11 classes at T_ramp 10 s and 30 s; G4-C1 to G4-C6, the MS9 and MS8 limits beside every output that uses a network or noisy record. Exploratory and post-hoc readings are labelled "post hoc", are kept out of the four pre-registered lists and feed no gate.
5. Time origins. The mean-field mode-N classes of S11 use the classifier onset (window centre, frozen O1); the raw crossing is secondary and post hoc. For the network part of S13 the time-origin check of MS10 (R27) is applied before any network record is read: same path clock, same `t_on`, same sample interval; a mismatch stops the evaluation.

## 1. RB2: S11 and the DL-251 controls (Table 7.2 RB2; DL-336 ruling 2b)

*Data.* MS11_S11: sigma factors 0.5, 1, 2 (sigma = factor x 0.0624) x T_ramp 10, 30, 120, 300 s x 10 seeds, P2 headline example, mode N. The seed index is the same noise stream at every sigma and T_ramp (the comparison across sigma is paired).

*Gate.* The headline surge class is "kept" in a run when its Table 2.1 class is a surge class: S+, S-rel or S-abs (ruled; `rb2_gate_class_set`). The test is the frozen "at least 8 of 10 seeds" at 0.5 sigma and at sigma, judged at the headline T_ramp 120 s (`rb2_judged_T_ramp_s`, the M11-2 recommendation, accepted; the plan names no T_ramp for the S11 test: UNVERIFIED reading). The count is the number of the 10 seeds in a surge class, the comparison is "at least" (the plan's text). Only these two sigma levels carry a verdict.

*Reported beside the gate, no verdict, feeding no gate.* (a) 2 sigma at every T_ramp (the frozen file: "2 sigma reported, no pass rule"); (b) the other T_ramp 10, 30, 300 s at every sigma; (c) the stricter readings S+ only and S+ or S-abs, labelled post hoc (the first of these not counting S-rel, as DL-250); (d) the class table per (sigma, T_ramp): counts per class, the metrics of Table 2.1 (median and range over seeds, undefined entries counted and not imputed).

*Controls (DL-251, POST-HOC AMENDMENT).* MS11_CTRL: constant parameters at the headline start state, headline record structure (2 s discard, 5 s baseline, 120 s ramp period, 10 s hold), the same three sigma factors, 10 seeds. The class rates of the controls are printed beside the S11 rates at T_ramp 120 s with the label "POST-HOC AMENDMENT (DL-251)"; they feed no gate. Reading: where the control also gives a surge class in k of 10 seeds, the S11 count at that sigma is not ramp evidence beyond the control (S-rel without a ramp occurred in 1,095 of 2,250 runs at MS9, DL-248, DL-250).

*Subgrid.* The noisy-subgrid agreement of RB2 is carried in as recorded at MS9: 97 of 225 cells (43.1 percent), 203 needed (90 percent, D24), FAILED (DL-242; P-1 post hoc 173 of 225, DL-255, DL-257). It is not re-evaluated.

*Open:* how a failed run counts in the 10 seeds (`rb2_failed_run_counts_as`).

## 2. RB5 (initial conditions), the parts open at MS11

*delta_0 ladder at T_ramp 10 s and 316.2278 s (S13).* "Class unchanged": the Table 2.1 class (mode D label) at delta_0 1e-9 and 1e-3 is compared with the class of the S5 grid P2 linear run at the same T_ramp (the 1e-6 member; config hashes equal, DL-338). Equal exact labels = unchanged (UNVERIFIED reading of "class unchanged"). The delay shift (eta at onset minus eta_H, at the 1 kHz output grid) and the onset shift are reported, not tested ("expected memory effect"; G6 reports and does not gate it). At T_ramp 120 s the MS8 result stands (D-tr at all three, shift 0.0 at the output grid; DL-183).

*Up versus down.* The P5 result of MS8 is carried in. Whether the S4 quasi-static up/down record is also an RB5 result is an open field (`rb5_updown_source`; the facts are in DL-340).

## 3. RB6 (numerical convergence), the parts open at MS11

*Mean field, noise-free.* rtol 1e-8 and 1e-12 against the 1e-10 grid run at T_ramp 10 s and 316.2278 s: the onset difference and the class are reported against rtol, not a pass test (plan). DOP853 against Radau: Radau runs only at the headline T_ramp (ruling 2c, DL-337, plan 9.3 step 1), so the criterion "solvers agree on class with onset within 1 ms" has its MS8 result at 120 s (class agrees, onset difference 181 ms against 1 ms, DOES NOT MEET, G6-D2) and no other T_ramp. **Claim limit, in words: the DOP853 against Radau comparison covers the headline T_ramp (120 s) only.** Nothing is said about the solver agreement at 10 s or 316 s.

*Mean field, D43 floor.* Three floor levels x 10 seeds at T_ramp 10 s and 316.2278 s at the default Heun rung 1e-3 tau only (coupled increments at 5e-5 tau). The finest rung is not run there, so the 5 percent Heun test (default step against the finest rung) cannot be formed at these T_ramp; it stands at 120 s as recorded at MS8 (DL-184, DL-190: relative change 0, a limit of the 1 ms output grid). At 10 s and 316.2278 s the per-level median delay and the number of seeds with no onset are reported (`rb6_floor_other_T_ramp`); whether the strict-decrease form of RB3(b) is also printed there is open (`s13_floor_other_T_ramp_form`).

*Network (MS11_S13_NET).* N = 1e4, 10 s ramp, P2 headline, 3 seeds per configuration, six configurations: dt 1e-3, 5e-4, 2.5e-4, 1e-4 at V_p 100 and V_p 200 at dt 1e-3 and 1e-4. The configuration of dt 1e-3, V_p 100 is re-run under the new key; the MS10 S8 runs are not reused. For each seed and configuration, f_pk is read two ways (`rb6_network_fpk_sources`, ruled M11-6 (c), UNVERIFIED reading): (i) the classifier's episode f_pk (Table 2.1, resolution 1/W), (ii) the argmax of the PSD of v in 25 to 100 Hz (O6, resolution 1/W, no interpolation) over the window of the classifier episode of the same seed's dt 1e-3 run. The criterion "halving dt changes f_pk by less than 2 percent" is applied to the pair dt 1e-3 against dt 5e-4 at V_p 100 (frozen F-21), per seed, strictly less than the frozen 2 percent (the plan's "<", `rb6_network_fpk_bound_boundary`), for each of the two readings; the other rungs (5e-4 against 2.5e-4, 2.5e-4 against 1e-4) and the V_p pair are printed with their differences. The differences in Hz and in frequency bins are printed beside each value. No class claim is made from these runs (G4-C3 stands; no new controls); the classes are printed as information with that label. The network RB6 result is the network part of S13 as read in G4-C6 (UNVERIFIED reading).

*Open:* what a seed with no episode in its dt 1e-3 run counts as (`rb6_network_fpk_no_episode`); whether the V_p comparison is reported only or the 2 percent bound is also applied (`rb6_network_vp_comparison`; the plan names no number for it).

## 4. RB9 (frequency mapping), stored series only except (d)

*(a) Dimensional against non-dimensional, within 0.5 percent.* The existing test-level check is described in DL-341. Whether it counts as the RB9(a) result, or a run is added, is open (`rb9a_source`).

*(b) Spectral against cycle frequency, within 1/W.* Spectral f_pk is the PSD argmax in G (O6). Cycle frequency is the unwrapped analytic phase over 2 pi (O5, mode D). W is the window of the cell's T_ramp (D4), so the bound is 1/W per cell. Cell set, comparison window and the equality case are open (`rb9b_cells`, `rb9b_comparison_window`, `within_boundary`).

*(c) Band 25 to 100 Hz against 30 to 120 Hz, at most 5 percent of cells change class.* The frozen A8 band variant (band_30_120, `a8_sensitivity.classify`) is applied to the stored mode-D series of map 1 (900 cells, 165,001 samples each) and map 2 (325 cells, 25 cells x 13 T_ramp), mode D. A cell "changes class" when its raw Table 2.1 class differs from the stored baseline class (`results/ms9/9e/map1_classes.csv`, `9f/map2_classes.csv`); the three-category change is printed beside (ruled M11-7). The noisy subgrid (2,250 mode-N runs) is reported without a verdict. Which set carries the verdict (pooled map 1 and map 2, map 1, or each alone), and how a cell for which a variant does not fit the record (class `not_run`, as at DL-147) is counted, are open (`gate_cell_set`, `not_run_cells_count_as`). The count of such cells is always printed.

*(d) tau plus or minus 20 percent, reported only.* Ruled M11-8 (d): two mean-field runs at tau = 8 and 12 ms on the headline path, reported only. Those two runs are in none of the four lists written at 11b; whether and how they are run is open (`rb9d_runs`). No gate.

## 5. RB10 (surge-definition sensitivity), stored series only

The five variants are the frozen list: band 30 to 120 Hz, factors 1.5 and 4 (relative and absolute together), A_min 0.05 and 0.2 x A_ref, window x 0.5 and x 2 (step W/2), minimum cycles 5 and 20 (`a8_sensitivity.VARIANTS`; a test checks the list against the frozen leaf). Each is applied to the stored headline series (the S5 headline run, T_ramp 120 s) and to the map cells (set as in RB9(c)). Pass: the headline class is unchanged under each change, and at most 10 percent (frozen) of the map cells in the verdict set change class under each change. The window x {0.5, 2} line of S13 is the window variant of this computation, not a separate run (ruled M11-7). Cells for which a variant does not fit are counted as under RB9(c). The D8-dependent classes carry the provisional label. The variants that rest on [needs decision] plan values (factors, A_min, window) are reported with those labels.

## 6. S13 mean field, per T_ramp (10 s, 316.2278 s; 120 s from MS8)

Reported per run: Table 2.1 class, onset to the 1 ms output grid, eta at onset, delay, duration, f_pk. Tables: rtol {1e-8, 1e-10, 1e-12}; delta_0 {1e-9, 1e-6, 1e-3}; D43 floor levels (default rung). The 1e-10 and 1e-6 members are the S5 grid runs. No scaling law is entered (D43, UNVERIFIED). The 5 percent Heun statement at 120 s stays as recorded.

## 7. A11 (`scripts/run_A11.py`, not written at 11b)

Rows: one per criterion leaf of the frozen file (RB1 to RB10 leaves, the gates' leaves that are RB-derived), `a11_row_unit = criterion_leaf`. Columns: the plan's value, threshold, pass or fail, and the input commits; further columns are open (`a11_extra_columns`). Status vocabulary: PASS, FAIL, REPORTED, NOT_JUDGED, NOT_EVALUABLE, OPEN (the last for the M4 and adaptation parts of RB8, open to MS12). Mode: each check evaluated at MS8, MS9 and MS10 is recomputed from the stored records with the stored evaluators and compared with the logged verdict; the logged verdict is printed beside; any difference is flagged and reported, never resolved silently. Failed checks (RB1 FAIL, RB2 subgrid FAILED, RB6 solver clause DOES NOT MEET, RB3(a) not judged at the headline, RB3(b) under both onset readings, RB8 heterogeneity NOT EVALUABLE) appear as logged and are never shown as PASS, never dropped. No new numeric threshold is written into A11. How the logged words map to the vocabulary is open (`a11_logged_verdict_map`).

## 8. D36 and timing

Accounting basis B (ruled): the placeholders "rest of S13" (1.0 h) and "S11" (0.0075 h) of the 14.21 h total are replaced by the MS11 figure, and basis A (added on top) is stated beside. 14.21 h is a sum on mixed bases (UNVERIFIED). Launch rule 9.2: S13 as a whole (MS8 recorded 26.3 min plus the MS11 prediction) against 1.5 x 60 min; with Radau cut, 40.6 min (0.68 x); S11 plus controls 40 s against 1.5 x 40 min. No part of the four lists is predicted to run over one hour (the Radau run at 316.2278 s is dropped, DL-337); the longest is a network run at dt 1e-4, 11.5 min under 10 copies; any run found over one hour is flagged and launched by the reviewer in PowerShell, never by Claude Code. The share of the 40 min row for S11 (S12 and S16 have run) is not ruled and is moot at 0.02 x.

## 9. Launcher refusal rules (plan section 8 item 10; as MS10 10e)

`scripts/run_ms11_list.py` refuses a real launch (exit 3) unless `ms11_runlist.check_launch` returns no reason: the criteria loader verifies the freeze; the git tree is clean; every MS11 data file is FROZEN; no required field of `ms11_eval.yaml` is open; the list SHA-256 and the seed-key SHA-256 equal the frozen ones in `configs/ms11/ms11_list_hashes.yaml`; every seed key is in the confirmed key set of `ms11_counts`; the free disk space is above the raw estimate of the lists (8 float64 arrays at 1 kHz per run; the network record is assumed the same: UNVERIFIED). `--dry-run` prints all of this and writes nothing. Network runs go through this launcher only.

## 10. Claims that are not made

No class claim from the S13 network runs (G4-C3). No statement about the solver agreement away from 120 s. No re-evaluation of the noisy-subgrid agreement. No new threshold in A11. No sigma confirmation (G4-C4). No scaling law for the noise floor.

## 11. Plan quantities marked UNVERIFIED that these rules touch

D43 floor levels 1.59e-9, 1.59e-6, 1.59e-3 and the Heun dt ladder below 1e-3 (lower rungs UNVERIFIED; only the default rung is run at 10 s and 316 s); the no-scaling-law statement of D43; sigma 0.0624 (frozen, checked and not confirmed); the A_ref reading 2.176222 and the 0.1 x A_ref threshold; the D8 estimator (provisional); `kept means` (F-17); network dt for the f_pk test (F-21); the meaning of "class unchanged" for RB5 (exact label); the T_ramp at which RB2 is judged; the S11 path and profile (D40 reading); the f_pk source for the network RB6 (M11-6); G4-C6 (that "rerun RB6" is the network part of S13); T_ramp 316 as 316.2278 s; the Table 2.1 [needs decision] items (band edges, factors 2, window rule, baseline, minimum duration); the Table 7.2 thresholds (D35 [needs decision]); the disk assumption for network records; the D36 total.

## 12. Required fields still open (14), for the reviewer

| Field | Question | Proposal (not a ruling) |
|---|---|---|
| `rb2_failed_run_counts_as` | A failed run among the 10 seeds: not kept, or excluded | not kept |
| `rb5_updown_source` | Which record is the RB5 up-versus-down result | P5 with S4 reported beside |
| `rb6_network_fpk_no_episode` | A seed with no episode in its dt 1e-3 run | undefined, fails the test |
| `rb6_network_vp_comparison` | V_p +-100 against +-200: reported only, or the 2 percent bound applied | reported only |
| `within_boundary` | Equality case of "within 0.5 percent" and "within 1/W" | inclusive |
| `rb9a_source` | Unit test, new run, or left open | none proposed |
| `rb9b_cells` | Cell set of RB9(b) | headline and all D-tr cells of map 1 and map 2 |
| `rb9b_comparison_window` | Span over which spectral and cycle frequency are compared | none proposed (the plan gives no window) |
| `gate_cell_set` | Which set carries the RB9(c) and RB10 verdict | pooled map 1 and map 2 |
| `not_run_cells_count_as` | Cells where a variant does not fit the record | excluded, with the count printed |
| `s13_floor_other_T_ramp_form` | Floor medians at 10 s and 316 s: reported only, or the RB3(b) form printed | reported only |
| `rb9d_runs` | The two tau runs: not run, or a separate post-hoc list | none proposed |
| `a11_logged_verdict_map` | Mapping of logged words (DOES NOT MEET, NOT INSIDE, PASSED WITH DEPARTURES) to the vocabulary | none proposed |
| `a11_extra_columns` | Columns beyond value, threshold, pass or fail, input commits | none |

Not a field, not ruled: the S11 share of the 40 min allowance (M11-12), moot.
