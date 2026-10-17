# Robustness criteria (MS7): readable companion to `configs/robustness_criteria.yaml`

**FINAL CONTENT FOR THE FREEZE, NOT YET FROZEN.** Regenerated at the 7j pre-freeze commit (DL-161) from the sign-off sheet (`docs/ms7_signoff.md`, ruling H-4) and from the criteria file. The tag `criteria-frozen`, the owner's approval entry and the SHA-256 of the LF text of the YAML file are not made yet; they follow only on the owner's separate explicit instruction. **The YAML file is authoritative: this page restates it and adds nothing.** Where the page and the file differ, the file is right; at the pre-freeze commit they do not differ (section 7).

Status labels (the owner's three): **logged** = written in the plan (Table 7.2, Table 11.2, Table 2.1, Appendix B) or in a decision-log entry; **UNVERIFIED** = no source gives it (ours, or an owner ruling that no source backs), carried as ruled and labelled; **open** = not decided. Plan numbers marked [needs decision] are carried at the plan default (D35).

Plan v0.5 is not edited. The D-items are at their defaults.

## 1. Rulings (sheet sections 0 and 8; DL-157, DL-158, DL-159, DL-161)

| ID | Ruling |
|---|---|
| D8 | A for MS7: the plan estimator (10 cycles, 2 SE, zero-phase order-4 band-pass, plain OLS SE) stays; the strict xfail stays; its documented failures are a known limitation. B (zero-pad edge treatment plus an autocorrelation-aware SE) stays on the sheet with the DL-155 data |
| X-1 | Gate reads "pytest exits 0 with the documented xfails". The MS7 gate passes with departures (section 6) |
| Q3 | Plan question (fast-damped rings are already NS by the cycle count): Table 2.1 left as written for MS7, to be considered after MS8 data |
| SW | Short-window false surge: report only, no new threshold; the paper states the white-noise rate per W and limits the claim through the G6 route |
| O1 to O9, O13 to O16 | The code's plain readings (section 2) |
| O10 | S+ needs a shared flagged window of the relative and absolute episodes; two qualifying episodes with no shared window give the class of the earlier one (fallback ours, UNVERIFIED, accepted in DL-158). Implemented |
| O11 (F-6) | S-abs flagged broadband when the argmax of the rise lies outside G; no threshold; "rise" is our definition, UNVERIFIED. Implemented |
| O12 | Post-surge rate: reported-only metric, not a criterion, not implemented, defined at MS8 with data |
| H-1 | A_ref = 2.176222 (median band-passed Hilbert envelope over whole cycles, stored S3 ref_devalle record); threshold 0.217622; alternates stored, not run |
| F-7, RHO, REACH | Baseline rho reported (odds test, no flag, no class), per W; only the plan's 0.5 at ratio 2 reported, 1/ratio levels in an appendix |
| G6 | RB3(a) "not judged at the headline" (outside the RB3(a) range); G6 at the headline rests on RB3(b) and RB6 |
| RB6 | Median delay over 10 seeds, default step 1e-3 tau against 1e-4 tau, same seeds, coupled increments, relative change < 5 percent (DL-154) |
| F-8 to F-15, F-17, F-20, F-22 to F-28 | Confirmed as recommended; F-10 to F-15 as entered in DL-152 |
| F-16 | Class agreement, onset and f_pk errors not larger, f_pk reference per seed; tolerance: if N = 1e4 is inside the RB1 pass bands, N = 3e4 must also be (DL-158), no margin |
| F-18, F-21 | (d) compares the four T_ramp of (c); solver pair DOP853 vs Radau; network dt 1e-3 against 5e-4 |
| F-19 | Latin hypercube seed: root_seed 20261008, **spawn key [7, 9] confirmed by the owner at 7i (DL-159)**: design draw [7, 9, 0], point runs [7, 9, 1, k], k = 0 to 63. UNVERIFIED (no source gives a key) |
| F-23 | M4 criteria deferred; written before M4 runs |
| U-5 zero baseline | **Option (a) ruled at 7i (DL-159):** the code has no "undefined" mode-N class; a known difference from Table 2.1, recorded as the second MS7 gate departure; three strict xfails document it; classifier unchanged |
| U-7 | Baseline-edge window tie explained (T_ramp 31.6228 against 31.62 s); classifier fix deferred |
| H-2, H-3 | A4 stays on `replication.yaml`; the criteria loader is written at MS8 and refuses to run if the SHA-256 of the criteria file does not match the tag |
| K5, K10, K4-net, CAP | K5 deferred; K10 and K4-net carried; the 24 h cap rows without timing cells accepted |
| DEF, BAK, PERM | Closed by the user (Defender exclusion, backup copy, git push denied); user-reported, not machine-checked |

## 2. Classifier (Table 2.1, `analysis/surge_metrics.py`)


| Key | Value | Status | Source | Sheet |
|---|---|---|---|---|
| band_primary_hz | [25, 100] | logged | D2, Table 2.1 | F-8 |
| total_band_hz | [1, 150] | logged | D3, Table 2.1; linear detrend | F-8 |
| spectrogram_taper | hann | logged | D4 | F-8 |
| window_rule | W = 2 s, step 1 s for T_ramp >= 60 s; else W = max(0.2 s, T_ramp/30), step W/2 | logged | D4 | F-8 |
| baseline_s | 5 | logged | D5, CP14: last 5 s before t_on; 2 s discard before it | F-8 |
| baseline_discard_s | 2 | logged | D5, CP14 | F-8 |
| rel_factor | 2 | logged | D6: P_G/P_non-G >= 2 x baseline (odds, CP18) | F-8 |
| abs_factor | 2 | logged | D6: P_G >= 2 x baseline P_G | F-8 |
| min_cycles | 10 | logged | D8 | F-8 |
| collapse_r_frac | 0.1 | logged | D9: r < 10 percent of baseline | F-8 |
| amin_factor | 0.1 | logged | D7, F-2: 0.1 x A_ref, one absolute threshold for every cell and path | F-2 |
| d8_estimator | PlanD8Estimator: fit ln(envelope) from the threshold crossing over the first 10 cycles; damped only if the rate is < -2 SE; zero-phase Butterworth order 4 band-pass; plain OLS SE; nan is non-damped | logged | Table 2.1 D8 wording (plan); estimator choices per DL-062, DL-140 | D8 |
| d8_estimator.a8_unmet_items_known_limitations | Of the plan's 8 A8 ring items the plan estimator fails 2 (DL-155 F5, DL-147 (3)): the slowly damped 15-cycle ring is called damped in 86.5 percent of draws against the required 95 percent, and the slowly damped mode-D ring (D_ring_slow_-3, T 120 s) is classed D-tr where NS or D-none is required. Also not met on the synthetic set: a pure trend at W = 0.2 s in mode N gives S-rel (mode D gives D-none; mode N at W = 2 s gives NS). Reported as known limitations (ruling U-2); not fixed in MS7. | UNVERIFIED | owner ruling DL-157 (U-2, X-1); DL-147 (3), DL-155 (2) | U-2 |
| d8_estimator.gate_wording | MS7 gate 'test_surge_metrics passes' reads: pytest exits 0 with the documented strict xfails, each with raises=AssertionError (9 test cases; no failure, no error, no unexpected pass). tests/test_surge_metrics.py: test_slowly_damped_ring_rate_matches_true_decay_after_step_onset. tests/test_surge_classes.py: test_zero_baseline_exact_zero_has_no_nan_in_outputs; test_zero_baseline_mode_n_class_is_undefined[exact_zero]; test_zero_baseline_mode_n_class_is_undefined[constant]; test_a8_ring_class_is_ns_or_d_none[D_ring_slow_-3@T120]; test_a8_slowly_damped_ring_called_damped_in_95_percent_of_draws; test_noise_free_pure_trend_is_ns_in_mode_n[120.0]; test_noise_free_pure_trend_is_ns_in_mode_n[3.0]; test_pure_trend_plus_noise_is_ns_in_mode_n_at_t_ramp_3. The gate passes with the four departures listed under gate_departures. | UNVERIFIED | owner ruling DL-157 (X-1); DL-161 (strict xfails with raises=AssertionError, class-level tests, departure 4) | X-1 |
| gate_departures.D8 | D8: the plan estimator fails 2 of the plan's 8 A8 ring items: the 15-cycle slowly damped ring is called damped in 86.5 percent of 200 draws against the required 95 percent, and D_ring_slow_-3 (mode D, T_ramp 120 s) is classed D-tr where NS or D-none is required. D8 = A is kept; every D8-dependent class is provisional. | UNVERIFIED | owner ruling DL-157 (X-1, U-2); DL-155 F5; DL-147 (3); strict xfails DL-073 and DL-161 | X-1 |
| gate_departures.zero_baseline | Zero baseline, including noise-free inputs: Table 2.1 says the power ratios and mode-N classes are undefined; the code has no such class. A constant record gives NS; an exactly zero record gives S-sus with NaN peak_rho; a noise-free pure trend gives S-sus where the plan says NS. Strict xfails: 3 zero-baseline tests (DL-158) and the noise-free pure-trend test (2 cases, DL-161). Classifier unchanged. | UNVERIFIED | owner ruling DL-159 (U-5, option (a)); DL-158; DL-161 | U-5 |
| gate_departures.rb3a_not_judged_at_headline | RB3(a) is not judged at the headline (120 s): the headline is outside the RB3(a) range for every floor >= 1e-16; coverage 0 to 2 of 13 T_ramp per path and profile. G6 at the headline rests on RB3(b) and RB6. | UNVERIFIED | owner ruling DL-157 (G6 reading); DL-149, DL-151 | G6 |
| gate_departures.pure_trend_plus_noise_short_window | Pure trend plus noise at W = 0.2 s: the plan's 'pure trend -> NS' fails at class level (T_ramp 3 s: S-rel in a majority of tested seeds (12 to 16 of 20 across six recorded 20-seed sets; DL-162 lists the sets); T_ramp 120 s passes, NS). Tied to the short-window false-surge limitation (306 of 500 white-noise records non-NS at W = 0.2 s). Concerns noisy inputs; departure 2 concerns noise-free inputs only. One strict xfail. Classifier unchanged; the paper limits its claim to the windows where the classifier passes. | UNVERIFIED | owner ruling at 7j pre-freeze (option A, departure 4); DL-147; DL-161 | X-1 |
| reported_limitation_short_window_false_surges | Not a departure: short-window false surges on seeded white noise (sd 0.04, mode N), non-NS of 500: 306 (W = 0.2 s), 400 (0.333 s), 172 (0.593 s), 24 to 26 (1.054 s), 2 (1.874 s), 0 (2 s). Reported per W in every result. | UNVERIFIED | DL-147, DL-155; gate report section 3 | X-1 |
| a_ref | 2.176222 | UNVERIFIED | DL-139: median of the band-passed Hilbert envelope over whole cycles of the stored S3 ref_devalle record, first and last 1 s dropped | H-1 |
| a_ref.threshold_abs | 0.217622 | UNVERIFIED | 0.1 x A_ref (D7) | H-1 |
| a_ref.source_record | results/S3/devalle/devalle_0000_9e49def91dfc.npz | logged | DL-139 |  |
| a_ref.source_record_sha256 | bb12620d7152c50584e3a6b2d22e6703305fa6dc2f29143695fc38547c33748a | logged | DL-139 |  |
| a_ref.a5_cycles_npz_sha256 | 0231a2b74274fe0e84d2cef1afcd44c12dbff56d970cacb3d072ce7203782e4d | logged | results/A8/a_ref/a_ref.json |  |
| a_ref.period_source | results/A5/A5_0000_506cf5745380.json | logged | DL-139 |  |
| a_ref.alternates_stored_not_used | {mean: 2.186789, maximum: 3.219102, sqrt2_x_rms: 2.404543, half_peak_to_peak: 2.755908, literal_peak_to_peak: 5.511356} | logged | DL-139, results/A8/a8_aref.json |  |
| sigma | 0.0624 | UNVERIFIED | DL-121; frozen with the criteria (6.4, CP21), checked at S8 (MS10) | F-9 |
| mode_n_conventions.O1_onset_time | window centre of the first flagged window (Conventions.onset = centre) | UNVERIFIED | owner ruling DL-157; DL-140 O1 | O1 |
| mode_n_conventions.O2_episode_end | gap = unflagged windows x step, merged if < W; end = last flagged centre + step/2; duration = flagged windows x step | UNVERIFIED | owner ruling DL-157; DL-140 O2 | O2 |
| mode_n_conventions.O3_termination | sustained if no gap of W or more follows before the record ends | UNVERIFIED | owner ruling DL-157; DL-140 O3 | O3 |
| mode_n_conventions.O4_mode_n_amplitude | keep as coded: the D8 fit uses the single 0.1 x A_ref, the mode-N 10-cycle count uses none; the 8 noise-prone cells are reported in the maps, classifier unchanged | UNVERIFIED | owner ruling DL-157 (a) plus (c); DL-145, DL-147 (4) | O4 |
| mode_n_conventions.O5_cycle_count | mode N = duration x mean f_pk over the episode windows; mode D = unwrapped analytic phase / 2 pi | UNVERIFIED | owner ruling DL-157; DL-140 O5 | O5 |
| mode_n_conventions.O6_peak_frequency | argmax of the PSD in G, resolution 1/W, no interpolation | UNVERIFIED | owner ruling DL-157; DL-140 O6 | O6 |
| mode_n_conventions.O7_baseline_statistic | mean over the windows wholly inside the last 5 s of P_G/P_non-G and of P_G | UNVERIFIED | owner ruling DL-157; DL-140 O7 | O7 |
| mode_n_conventions.O8_tested_windows | window centre >= t_on | UNVERIFIED | owner ruling DL-157; DL-140 O8 | O8 |
| mode_n_conventions.O9_d8_scope | one D8 call per record on v from t_on; damped means no episode (NS or D-none) | UNVERIFIED | owner ruling DL-157 under D8 = A; DL-140 O9 | O9 |
| mode_n_conventions.O10_episode_and_s_plus | mode D: first qualifying episode. Mode N: first qualifying episode per test; S-sus if any is unterminated; S+ only if the relative and absolute episodes share a flagged window (time overlap); two qualifying episodes with no shared window give the class of the earlier one | UNVERIFIED | owner ruling DL-157 (implemented and tested); the fallback for the non-overlapping pair is ours, accepted by the owner as UNVERIFIED (DL-158) | O10 |
| mode_n_conventions.O11_s_abs_broadband | S-abs is flagged broadband when the spectrogram argmax of the rise lies outside G; rise = the absolute episode's peak-power window minus the mean baseline spectrum, over 1 to 150 Hz; no new threshold | UNVERIFIED | owner ruling DL-157 (implemented and tested; the definition of 'rise' is ours); CP26, F-6 | O11 |
| mode_n_conventions.O12_post_surge_rate | reported-only metric, not a criterion; not implemented; defined at MS8 with data | UNVERIFIED | owner ruling DL-157 | O12 |
| mode_n_conventions.O13_collapse_baseline_r | mean of r over the baseline; marker = first sample with r < 10 percent of it, no smoothing | UNVERIFIED | owner ruling DL-157; DL-140 O13 | O13 |
| mode_n_conventions.O14_exit_delay_sign | J_exit,run minus J_exit,static | UNVERIFIED | owner ruling DL-157; DL-140 O14 | O14 |
| mode_n_conventions.O15_label_f | A4-region membership is supplied by the caller | UNVERIFIED | owner ruling DL-157; DL-140 O15 | O15 |
| mode_n_conventions.O16_edge_handling | none in the classifier; the caller discards transients | UNVERIFIED | owner ruling DL-157 under D8 = A; DL-140 O16 | O16 |
| reading_conventions.rho_reported_per_W | baseline rho is reported per D4 window W (median 0.754 at W = 0.2 s, 0.588 at W = 2 s) | UNVERIFIED | owner ruling DL-157 (RHO); DL-145, DL-147 (5) | RHO |
| reading_conventions.rho_ge_half | rho reported, surge test on the odds (unbounded); no flag, no class | UNVERIFIED | owner ruling DL-157 (F-7); DL-145 | F-7 |
| reading_conventions.reachability_levels | report only the plan's 0.5 at ratio 2; the 1/ratio levels (0.667 at 1.5, 0.25 at 4) in an appendix as information | UNVERIFIED | owner ruling DL-157 (REACH); the appendix levels are our arithmetic | REACH |
| reading_conventions.short_window_false_surge | report only, no new threshold. The paper states the white-noise false-surge rate per W (non-NS of 500 at sd 0.04: 306 at 0.2 s, 400 at 0.333 s, 172 at 0.593 s, 24 at 1.054 s (T_ramp 31.6228 s; 26 at the rounded 31.62 s), 2 at 1.874 s, 0 at 2 s) and limits the claim through the G6 'limit the claim' route | UNVERIFIED | owner ruling DL-157 (SW); DL-140 finding 4, DL-147 (6), DL-155 (4), DL-157 (U-7) | SW |
| reading_conventions.s3s4_sensitivity | stored-record sensitivity (S3 2 to 8 s, t_on 1 s; each S4 hold with t_on at its start) is a pre-freeze sensitivity only; the real RB10 is evaluated by A11 on ramp records | UNVERIFIED | owner ruling DL-157; DL-146, DL-147 (2) | S3S4 |
| reading_conventions.a_ref_reading | median of the band-passed Hilbert envelope; alternates not run as a sensitivity item | UNVERIFIED | owner ruling DL-157 (H-1); DL-139 | H-1 |

## 3. Table 7.2 robustness checks (D35)

| Key | Value | Status | Source | Sheet |
|---|---|---|---|---|
| RB1.classes_agree_seeds | 3 of 3 | logged | Table 7.2 RB1 |  |
| RB1.classes_agree_cells | >= 3 of 4 | logged | Table 7.2 RB1 |  |
| RB1.f_pk_rel_tol | 0.05 | logged | Table 7.2 RB1 |  |
| RB1.onset_tol | one spectrogram step (1 s for T_ramp >= 60 s, else W/2) | logged | Table 7.2 RB1; D4 |  |
| RB1.n_3e4_no_worse_than_1e4 | class agreement count not smaller, onset error not larger and f_pk error not larger at N = 3e4 than at N = 1e4 (network v is the mean V of non-refractory neurons) | UNVERIFIED | owner ruling DL-157 (F-16, MUST); wording of the metric only | F-16 |
| RB1.f_pk_reference | per seed | UNVERIFIED | owner ruling DL-157 (F-16) | F-16 |
| RB1.no_worse_tolerance | if N = 1e4 is inside the RB1 pass bands (same class per Table 2.1, f_pk within 5 percent, onset within one spectrogram step), N = 3e4 must also be inside them; the f_pk and onset errors at both N are reported side by side but are not a pass test; no margin is invented | UNVERIFIED | owner ruling DL-158 (F-16); an interpretation, no source gives a tolerance | F-16 |
| RB2.headline_class_kept_min_seeds | 8 of 10 at 0.5 sigma and at sigma | logged | Table 7.2 RB2 |  |
| RB2.noisy_subgrid_agreement_min | 0.9 | logged | Table 7.2 RB2, D24 |  |
| RB2.sigma_factors | [0.5, 1, 2] | logged | Table 7.2 RB2; 2 sigma reported, no pass rule | F-17 |
| RB2.kept_means | same class as the headline mode-D class under the correspondence | UNVERIFIED | ours; confirmed by owner ruling DL-157 (F-17) | F-17 |
| RB3.a_onset_tol | one A4 grid step in eta_bar | logged | Table 7.2 RB3(a) |  |
| RB3.a_judged_only_inside_range | true | logged | Table 7.2 RB3(a); CP25 |  |
| RB3.a_range_rule | delta_0 exp(integral of Re lambda from t_on) stays above the floor until t_pred; t_pred where it reaches 0.1 x A_ref | logged | A7, CP25; code analysis/entry_exit.py; confirmed by owner ruling DL-157 (F-12): the one-grid-step tolerance is frozen without ramp evidence, first test is RB3(a) at MS8 | F-12 |
| RB3.a_range_reported_coverage | 0 to 2 of 13 T_ramp per path and profile; none at the headline (120 s) | UNVERIFIED | DL-149 (2), DL-151; reasoned arithmetic until MS8 | G6 |
| RB3.b_form | strict_decrease_of_median_delay_over_the_three_floor_levels | UNVERIFIED | DL-152 F-15; no scaling law | F-15 |
| RB3.b_seeds_per_level | 10 | UNVERIFIED | DL-152 F-15 |  |
| RB3.c_T_ramp_s | [56.23, 100.0, 177.8, 316.2] | logged | Table 7.2 RB3(c): 56, 100, 178, 316 s; the 4-digit values are the S5 grid points 10^(k/4) of configs/S5_cells.yaml (kept exact) |  |
| RB3.c_holds_means | same class as the headline | UNVERIFIED | ours; confirmed by owner ruling DL-157 (F-18) | F-18 |
| RB3.d_profile_max_class_changes | 1 | logged | Table 7.2 RB3(d) |  |
| RB3.d_T_ramp_compared | [56.23, 100.0, 177.8, 316.2] | UNVERIFIED | owner ruling DL-157 (F-18): the four T_ramp of RB3(c), at the S5 grid values 56.23, 177.8, 316.2 (kept exact); the plan does not say which are compared | F-18 |
| RB4.one_at_a_time_runs | 14 | logged | Table 7.2 RB4, S16 |  |
| RB4.one_at_a_time_max_class_changes | 2 | logged | Table 7.2 RB4 |  |
| RB4.perturbation_rel_box | 0.1 | logged | Table 7.2 RB4, S16: +-10 percent; a tag [reasoned, not tested] on the box: UNVERIFIED (label not in plan text) |  |
| RB4.latin_hypercube_points | 64 | logged | Table 7.2 RB4 |  |
| RB4.latin_hypercube_min_class_unchanged | 0.8 | logged | Table 7.2 RB4, G5 |  |
| RB4.latin_hypercube_seed | {root_seed: 20261008, spawn_key_prefix: [7, 9], design_draw: [7, 9, 0], point_run_seeds: [7, 9, 1, k], k = 0 to 63} | UNVERIFIED | ruled by the owner at 7i (DL-159, F-19): key [7, 9], design draw [7, 9, 0], point runs [7, 9, 1, k]; no source gives a key; follows the DL-141 convention (first element 7 = MS7, second element the next free index after [7, 8] d8cand; calibration keys [0] to [9] and [7, 4, s] untouched); no collision with any key in the repo (tests/test_criteria_draft.py) | F-19 |
| RB4.class_unchanged_means | same class as the unperturbed run, per run | UNVERIFIED | owner ruling DL-157 (F-19) | F-19 |
| RB5.delta0_ladder | [1e-09, 1e-06, 0.001] | logged | Table 7.2 RB5; S13 |  |
| RB5.start_distances | [0.5, 1.5, 3] | logged | Table 7.2 RB5; S5 |  |
| RB5.criterion | class unchanged; delay shifts reported | logged | Table 7.2 RB5; G6 reports it, does not gate it |  |
| RB6.heun_delay_change_max | 0.05 | logged | Table 7.2 RB6 |  |
| RB6.heun_dt_ladder_tau | [0.001, 0.0005, 0.00025, 0.0001] | UNVERIFIED | DL-152 F-14; configs/S13.yaml |  |
| RB6.heun_default_dt_tau | 0.001 | logged | 6.2, Table 7.2 RB6 |  |
| RB6.heun_coupled_brownian_increments | true | UNVERIFIED | DL-152 F-14 |  |
| RB6.statistic | median delay over 10 seeds at the default step against the median over the same 10 seeds at the finest rung (1e-4 tau), same seeds, coupled increments; \|median(1e-4) - median(1e-3)\| / median(1e-3) < 0.05 | UNVERIFIED | DL-154 (owner ruling); the plan's 5 percent only | RB6 |
| RB6.rtol_ladder | [1e-08, 1e-10, 1e-12] | logged | S13; reported, not a pass test |  |
| RB6.solvers_agree_onset_ms | 1 | logged | Table 7.2 RB6 (DOP853 vs Radau) |  |
| RB6.solver_pair_list | DOP853 vs Radau | UNVERIFIED | S13 lists both; pair list confirmed by owner ruling DL-157 (F-21) | F-21 |
| RB6.network_dt_f_pk_change_max | 0.02 | logged | Table 7.2 RB6 (halving dt) |  |
| RB6.network_dt_for_f_pk_test | {default_tau: 0.001, halved_tau: 0.0005} | UNVERIFIED | owner ruling DL-157 (F-21): network dt 1e-3 against 5e-4; both are rungs of the S13 network dt ladder | F-21 |
| RB7.NC1_surge_class_allowed | false | logged | Table 7.2 RB7; G7: NS or D-none at every T_ramp |  |
| RB8.gaussian_uniform_give_lorentzian_class_seeds | 3 | logged | Table 7.2 RB8 |  |
| RB8.M4_criteria | null | open | deferred by owner ruling DL-157 (F-23): written before M4 runs (D42 open, G2 does not trigger, DL-133); no ruling owed now | F-23 |
| RB9.a_dimensional_vs_nondimensional_rel_tol | 0.005 | logged | Table 7.2 RB9(a) |  |
| RB9.b_spectral_vs_cycle_frequency | within 1/W | logged | Table 7.2 RB9(b) |  |
| RB9.c_band_30_120_max_cell_class_change | 0.05 | logged | Table 7.2 RB9(c); D2 |  |
| RB9.d_tau_pm20_percent | reported only | logged | Table 7.2 RB9(d) |  |
| RB10.headline_class_unchanged | true | logged | Table 7.2 RB10 |  |
| RB10.max_map_cell_class_change | 0.1 | logged | Table 7.2 RB10 |  |
| RB10.variations | {band_hz: [30, 120], factors: [1.5, 4], amin_factor: [0.05, 0.2], window_multiplier: [0.5, 2], min_cycles: [5, 20]} | logged | Table 7.2 RB10; A8 sensitivity list |  |

## 4. Gates G5 to G7 (Table 11.2)

| Key | Value | Status | Source | Sheet |
|---|---|---|---|---|
| G5.surge_class_min_fraction_of_map1_cells | 0.03 | logged | Table 11.2 G5, D35 |  |
| G5.map1_mode_that_counts | mode D (S7 map 1); noisy subgrid separate | UNVERIFIED | owner ruling DL-157 (F-26); default proposed in DL-135 F-26 | F-26 |
| G5.rb4_must_pass | true | logged | Table 11.2 G5 |  |
| G6.rb3a_inside_range_pass | true | logged | Table 11.2 G6 |  |
| G6.rb3b_pass | true | logged | Table 11.2 G6 |  |
| G6.rb6_pass_at_headline | true | logged | Table 11.2 G6 |  |
| G6.rb3d_rb5 | evaluated and reported, not gated | logged | Table 11.2 G6; SC-04 |  |
| G6.reading | the headline (120 s) is outside the RB3(a) range, so the RB3(a) clause is 'not judged at the headline'; G6 at the headline rests on RB3(b) and RB6; RB3(a) is reported with its coverage | UNVERIFIED | owner ruling DL-157 (G6; reading of DL-152, not a change of the plan) | G6 |
| G7.NC1_no_surge_at_every_T_ramp | true | logged | Table 11.2 G7 |  |

## 5. D43 floors, A4 grid step, Heun ladder (7g rulings, DL-152; same numbers as `configs/S13.yaml`)

| Key | Value | Status | Source | Sheet |
|---|---|---|---|---|
| delta0_ladder | [1e-09, 1e-06, 0.001] | logged | S13, Table 7.2 RB5 |  |
| sigma_floor_levels | [1.59e-09, 1.59e-06, 0.00159] | UNVERIFIED | DL-152 F-10: delta_0 / 0.629, v-units per sqrt(tau) |  |
| std_v_over_sigma_at_start | 0.629 | UNVERIFIED | DL-149 (Lyapunov, noise on v only) |  |
| solver_floor_noise_free_v | 6.66e-16 | UNVERIFIED | DL-151 F-11: measured at rest, a lower bound for a ramp run; protocol ours |  |
| a4_eta_bar_grid_step | 0.025 | UNVERIFIED | DL-152 F-13; realised by configs/A4_grids.yaml (801 points on [-10, 10]) |  |
| rb3a_tolerance_in_time_at_headline_s | 0.857 | UNVERIFIED | DL-149 (4): one grid step at t_pred |  |
| headline_t_pred_run_clock_s | 115.22 | UNVERIFIED | DL-149 (1), delta_0 1e-6, reading (a) of A_ref |  |

### Baseline-only cell lists (7d, 7e)

| Key | Value | Status | Source | Sheet |
|---|---|---|---|---|
| n_cells | 1226 | logged | DL-141: 1 + 900 + 325 |  |
| n_runs | 12260 | logged | DL-143: 10 seeds each, 0 failed |  |
| cell_list_sha256 | 8e67bbd2b366e86ffee59e732dd79824bdce82c73c477436cb3b1689b0a328d9 | logged | DL-141 (not the freeze SHA) |  |
| grid_spacing | map 1: Delta linear 0.01 to 0.6 (30), tau_d log 1 to 50 ms (30); map 2: J0 linear -40 to -5 (25), T_ramp log 1 to 1000 s (13) | UNVERIFIED | DL-136 D-4 working defaults; configs/S5_cells.yaml | F-27 |
| start_state | eta_start = eta_H - 1.5 from the lowest Hopf crossing of the cell; cells with none use the headline values (D12, CP20) | logged | DL-141 |  |
| seeds | root_seed 20261008; baseline spawn key [7, 4, s], s = 0 to 9 | UNVERIFIED | DL-141 (ours; avoids the sigma-calibration keys) | F-28 |
| storage | one npz and one record per cell (10 seeds); v and r kept | logged | DL-136 D-4 ruling | F-28 |

### Not implemented, housekeeping

| Key | Value | Status | Source | Sheet |
|---|---|---|---|---|
| post_surge_rate | null | UNVERIFIED | owner ruling DL-157 (O12): reported only, not a criterion, defined at MS8 with data | O12 |

| Key | Value | Status | Source | Sheet |
|---|---|---|---|---|
| criteria_key_on_configs | configs/A4.yaml stays on configs/replication.yaml (run_a4 reads K tolerances from it); robustness.criteria_file is set on the ramp-run configs at MS8 | UNVERIFIED | owner ruling DL-157 (H-2) | H-2 |
| loader | written at MS8; its first step refuses to run if the SHA-256 of this file does not match the tag | UNVERIFIED | owner ruling DL-157 (H-3) | H-3 |
| readable_companion | docs/robustness_criteria.md is generated from the sign-off sheet at 7i | UNVERIFIED | owner ruling DL-157 (H-4) | H-4 |
| deferred_or_carried | K5 deferred; K10 and K4-net carried; D36 cap rows without timing cells accepted | UNVERIFIED | owner ruling DL-157 (K5, K10, K4-net, CAP) |  |
| closed_by_user | Defender exclusion in place; backup copy of the repository and results exists; /permissions shows no saved rules and a Deny rule for git push | UNVERIFIED | user answers recorded in DL-157 (DEF, BAK, PERM) |  |

## 6. Known limitations and gate departures stated in the criteria

Four departures from the plan at the MS7 gate, and one reported limitation. This list is identical in `docs/ms7_gate_report.md`, `docs/ms7_7j_procedure.md`, `docs/ms7_signoff.md` and this page.

1. **D8 (departure 1).** The plan estimator fails 2 of the plan's 8 A8 ring items: the 15-cycle slowly damped ring is called damped in 86.5 percent of 200 draws against the required 95 percent, and D_ring_slow_-3 (mode D, T_ramp 120 s) is classed D-tr where NS or D-none is required (DL-155, DL-157). D8 = A is kept; 26 of 36 pre-registered F1 cells miss the 95 percent sign match and 5 of 5 zero-growth cells exceed 5 percent false damped (DL-137, DL-155); every class that went through a D8 call is provisional. Strict xfails: `test_slowly_damped_ring_rate_matches_true_decay_after_step_onset` (DL-073), `test_a8_ring_class_is_ns_or_d_none[D_ring_slow_-3@T120]`, `test_a8_slowly_damped_ring_called_damped_in_95_percent_of_draws`.
2. **Zero baseline, including noise-free inputs (departure 2).** Table 2.1: with no gamma power "the power ratios and the mode-N classes are undefined". The code has no such class: a constant record gives NS, an exactly zero record gives S-sus with a NaN peak_rho and a RuntimeWarning, and a noise-free pure trend gives S-sus where the plan says NS (option (a), DL-159). Strict xfails: the 3 zero-baseline tests (DL-158) and `test_noise_free_pure_trend_is_ns_in_mode_n[120.0]` and `[3.0]`. This departure concerns noise-free inputs only. Deterministic runs use mode D (D-none).
3. **RB3(a) not judged at the headline (departure 3).** The headline (120 s) is outside the RB3(a) range at every floor >= 1e-16; coverage is 0 to 2 of 13 T_ramp per path and profile; P2 sigmoid has no predicted onset. G6 at the headline rests on RB3(b) and RB6 (DL-149, DL-151, DL-157). Reasoned arithmetic until MS8.
4. **Pure trend plus noise at W = 0.2 s (departure 4, new at the 7j pre-freeze, DL-161).** The plan's "pure trend -> NS" fails at class level at W = 0.2 s (T_ramp 3 s: S-rel in a majority of tested seeds (12 to 16 of 20 across six recorded 20-seed sets; DL-162 lists the sets)). T_ramp 120 s passes (NS). It is tied to the short-window false-surge limitation (306 of 500 white-noise records non-NS at W = 0.2 s). The classifier is not changed; the paper limits its claim to the windows where the classifier passes. Strict xfail: `test_pure_trend_plus_noise_is_ns_in_mode_n_at_t_ramp_3`.

Reported limitation (not a departure): **short-window false surges**, reported per W in every result. On seeded white noise (sd 0.04, mode N) non-NS of 500: 306 (W = 0.2 s), 400 (0.333 s), 172 (0.593 s), 24 to 26 (1.054 s), 2 (1.874 s), 0 (2 s). The rate is set by the power tests on a short PSD and the 10-cycle rule, not by D8. 8 of the 13 map-2 T_ramp have W < 2 s. The real rate on M3 noise is first measured by NC1 (G7).

Strict xfails in the suite: 9 cases (1 in `tests/test_surge_metrics.py`, 8 in `tests/test_surge_classes.py`), all with `raises=AssertionError`.
5. **Baseline rho.** 67.5 percent of the 12,260 records and 66.0 percent of cells have baseline rho >= 0.5 (headline 0.68; 56 stable nodes median 0.454). Rho depends on W (median 0.754 at 0.2 s, 0.588 at 2 s). Reported; the surge test is on odds.
6. **O4.** The baseline noise envelope reaches 0.217622 in 3.8 percent of records (125 map-1 cells at Delta >= 0.13); 8 cells (Delta 0.32 to 0.58, tau_d 25 to 50 ms) have a 10-cycle run above it. Reported with the maps; the classifier is unchanged.
7. **UNVERIFIED values frozen with the label** (ruling U-6): sigma 0.0624 (checked at S8, MS10), A_ref 2.176222, sigma_floor levels, solver floor 6.66e-16, A4 step 0.025, Heun ladder, RB3(b) form, cell grids, seeds, headline t_pred 115.22 s, coverage, RB6 statistic, F-19 key.

## 7. Where this page and the YAML file differ

None at the 7j pre-freeze commit (DL-161): the F-19 source, the four gate departures, `gate_wording`, `meta.decision_log_through` (DL-161), and the flags `draft: false`, `frozen: true`, `freeze_tag: criteria-frozen`, `freeze_sha256: null` (null on purpose, a file cannot contain its own hash) are as in the YAML. The tag and the hash do not exist yet.
