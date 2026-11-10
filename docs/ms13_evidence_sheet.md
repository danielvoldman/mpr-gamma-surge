# MS13 evidence sheet (13v, DL-703 V5, DL-708)

Written for: the owner and reviewer who close MS13, and the author of the paper. Written by scripts/ms13_evidence_sheet.py from stored files: the hashes are copied from docs/ms13_journal_final_hashes.txt (tests/test_ms13_13v.py compares them again with the files on disk); counts come from the output of scripts/ms13_verify_export.py and scripts/ms13_independent_compare.py run on the committed build in 13v (read only, no rebuild); the captions' failed-check and limit paragraphs are copied word for word. A value that no file gives is written UNVERIFIED. Nothing is tagged, pushed or uploaded.

Build commit of every journal figure: 5e9057563c6c24fbac16b99000e547d08ef9a31a. Later commits are documentation, the audit module, and in 13v the wording fix of the FS5 caption (DL-705, DL-706; FS5 caption and supplement only; the PNG, TIFF and PDF are unchanged).

## F1

Draft audit copy: F1 (figures/F1/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/F1/F1_journal.png | c01f955866a2c2a47f93fbc5a3dbdf7ec5ff995484cefb87f3da209d03091aeb |
| tiff | figures/journal/F1/F1_journal.tiff | 89525e91e58ff9beabbc63c49603640b2684859fe0c960aa910513cd9d4b2e08 |
| pdf | figures/journal/F1/F1_journal.pdf | d784c302085fc960398dc87c1fa7835918e19f497ece6d70f44903c29554c752 |
| caption short | figures/journal/F1/F1_journal_caption.txt | 8ffbb816f42c0611539ab774a1d37ca5fc89d8e8efe372407de3ad15a4e575a0 |
| caption full | figures/journal/F1/F1_journal_caption_full.txt | 78e215ed6133e0e71cb856b20b9637ed067c4191f4598547b12a108e3cfcc427 |
| alt text | figures/journal/supplement/F1_alt_text.txt | 780af815ca1f06a229ee943c2dd079aa2a7f7768e2082e1bb0d62130ff1216eb |
| supplement | figures/journal/supplement/F1_supplement.md | 3c0fe3efc63938f94fb0101c71bf53e31541e553a7d11c5acb445dbc062edfad |
| source data csv | figures/journal/supplement/F1_source_data.csv | 67076c7ed61974de74acf58f40c1496552427a9a555a48a22878485fa4031496 |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: bfdba12d9fc09fbfdc0514b6c5859a13a21948ea9db7e16ec4b1f845e11b8839; draft F1: bfdba12d9fc09fbfdc0514b6c5859a13a21948ea9db7e16ec4b1f845e11b8839; equal: yes. Verifier: PASS - bfdba12d9fc0... export bfdba12d9fc0 draft bfdba12d9fc0; PASS - 88 of the 88 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (21, 21, 0, 0) and short caption (8, 8, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of F1 (shared by the parts of a split figure): equal 51, other 15 (rows without a comparison are not counted as equal).
- Verifier rows for F1 (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/F1/F1_journal_caption_full.txt):

> Failed checks. Shown, not dropped (the full list with value, threshold and source is in the supplement): RB1 (network against mean field), headline path at a ramp duration of 10 s: FAIL (0 of 3 seeds; threshold 3 of 3); RB1 (network against mean field), headline path at a ramp duration of 120 s: FAIL (0 of 3 seeds; threshold 3 of 3); RB1 (network against mean field), the 4 map cells at a ramp duration of 30 s: FAIL (1 of 4 cells; threshold >= 3 of 4); RB1 (network against mean field), overall verdict: FAIL (value blank in the stored table: it is the verdict over its three parts (headline, cells, ramp-duration rule), which are in the note column of the stored table; no single threshold); G7 (negative-control gate): FAIL (value blank in the stored table; threshold blank in the stored table). Two further stored FAIL rows are not in the status strip of this figure: the sigma check (FAIL, logged verdict NOT INSIDE) and RB3(a) (0 of 6 testable in-range runs match). Other failed checks on the headline path are shown elsewhere: the RB2 headline class (kept in 7 of 10 seeds at the noise level sigma; threshold >= 8 of 10), the RB3(a) onset prediction on the testable in-range runs (0 of 6) and the RB3(b) classifier onset in F4, and the RB6 solver onset (181 ms against 1 ms) in F4 and FS4. Red titles show a FAIL (a failed check concerns the panel). The check RB1 (network against mean field) is shown in the title of (d) and (f) as 'network vs mean field: FAIL'. The title of (d) and (f) is red because those panels draw the failed result (the class of the network seeds).
> Limits. Claim limits that change how panels (d) and (f) read: the network does not reproduce the mean-field classes, and no-ramp network controls are classified into surge classes. Claim limits: All earlier failures and limits stand: the failure of check RB1 (network against mean field), gate G7 not passed, the failure of the D24 rule, the six limits set when gate G4 (network against mean field) was triggered, and the limits ruled for the map, control and perturbation runs. The surge result is stated for model M3 only; there is no claim about the models M4 or M3a and M3b, and the parts of check RB8 that concern M4 and adaptation have no result. Surge classes found in network records at N = 10,000 are not evidence of a ramp-driven surge: the network control without a ramp was flagged in 10 of 10 seeds, and the ramp runs in 10 of 10. Every class that depends on the test for damped against non-damped oscillations is provisional. The estimator for damped against non-damped oscillations fails 2 of 8 ring items of its own test; the classes that depend on it are provisional. The network at N = 10,000 and 30,000 does not reproduce the mean-field classes (0 of 3 seeds at T_ramp 10 s and 120 s; 1 of 4 cells). The surge result is stated for the mean field only; there is no claim that it is robust to finite-size fluctuations. No-ramp network controls are classified into surge classes. There is no claim of agreement in peak frequency or in class between the network and the mean field (the RB6 check of the network peak frequency failed). The spectral frequency and the cycle frequency differ by 4.39 Hz at the headline (RB9(b) failed); peak frequencies are the classifier's spectral peaks. RB1 failed: the headline at 10 s failed, the headline at 120 s failed, and the network agrees at 1 of 4 cells. Gate G7 was not passed: the network run of the first negative control (the hypoxia path with the mean excitability falling by the same amount, with coupling, heterogeneity and synaptic decay fixed and no common drive) is in class S+. Scope of the counts 'flagged in 10 of 10 seeds' and 'the ramp runs in 10 of 10': they come from the exploratory network runs of the negative-control step at N = 10,000 with 10 seeds each (the negative-control path along which the mean excitability falls, and the same network held at constant parameters without a ramp); those runs are not drawn here.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 6 stored-value claims listed for F1, 6 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 13 executable checks for F1, 13 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 44 (accepted by the user: S-sus has no recorded reason); 49; 56; 40 (draft label only; the journal text is correct).

## F2

Draft audit copy: F2 (figures/F2/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/F2/F2_journal.png | b6fc7221f1d5dde094ac920ef773fced6d2aa7013f6abdfaebc1c94f32c10feb |
| tiff | figures/journal/F2/F2_journal.tiff | 1c283d9c88a6cd0f58df945b50d392b8c72d3cc871d173c9152184b8bd8177ab |
| pdf | figures/journal/F2/F2_journal.pdf | bda15147705f24d65d58818e2ad3ae43d28e37f12caaca337844c82b4facbfb0 |
| caption short | figures/journal/F2/F2_journal_caption.txt | 0e095ccb1a6230c333fb066abb7721e8869c0801e884cc013c5fd2858bb710a1 |
| caption full | figures/journal/F2/F2_journal_caption_full.txt | 4d3e14050e3e316da382577f1d2aaf8b849d7308fd94c679ed1022120cba752a |
| alt text | figures/journal/supplement/F2_alt_text.txt | 5eab7c27cdf8d00eeacb0c933636c1d5e80a8d124d9d3bc3d786b6721af8a182 |
| supplement | figures/journal/supplement/F2_supplement.md | 76b1a21b4a360c6e6a8fee61a7edd3395bc0d3aed06e511fa2786422f8580e20 |
| source data csv | figures/journal/supplement/F2_source_data.csv | c85d3ba96a3881836673303e4c2e005ba1a114bd3ba305eadd56c5561fd4ceda |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: 3584f8faee5d704a1f172ad4185c133324ddb9f196f32d05d80f3ca5ef28a932; draft F2: 3584f8faee5d704a1f172ad4185c133324ddb9f196f32d05d80f3ca5ef28a932; equal: yes. Verifier: PASS - 3584f8faee5d... export 3584f8faee5d draft 3584f8faee5d; PASS - 50 of the 50 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (8, 8, 0, 0) and short caption (7, 7, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of F2 (shared by the parts of a split figure): equal 18, other 1 (rows without a comparison are not counted as equal).
- Verifier rows for F2 (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/F2/F2_journal_caption_full.txt):

> Failed checks. Shown, not dropped (the full list with value, threshold and source is in the supplement): RB1 (network against mean field), headline path at a ramp duration of 10 s: FAIL (0 of 3 seeds; threshold 3 of 3); RB1 (network against mean field), headline path at a ramp duration of 120 s: FAIL (0 of 3 seeds; threshold 3 of 3); RB1 (network against mean field), the 4 map cells at a ramp duration of 30 s: FAIL (1 of 4 cells; threshold >= 3 of 4); RB1 (network against mean field), overall verdict: FAIL (value blank in the stored table: it is the verdict over its three parts (headline, cells, ramp-duration rule), which are in the note column of the stored table; no single threshold). Red titles show a FAIL (a failed check concerns the panel). The check RB1 (network against mean field: the same class is required at the main example for ramp durations of 10 s and 120 s, at the 4 map cells and overall) is shown in the title of (c) as 'Network vs mean field: FAIL'. The four RB1 checks compare the classes of the network and the mean-field runs (the same class is required) and failed; the network and mean-field classes disagree elsewhere (the check failed); this panel compares amplitudes only. Panels (a) and (b) have no red title. The four RB1 rows are listed here because the figure draws network symbols (our reading of where the check applies, not verified).
> Limits. Claim limits: All earlier failures and limits stand: the failure of check RB1 (network against mean field), gate G7 not passed, the failure of the D24 rule, the six limits set when gate G4 (network against mean field) was triggered, and the limits ruled for the map, control and perturbation runs. The surge result is stated for model M3 only; there is no claim about the models M4 or M3a and M3b, and the parts of check RB8 that concern M4 and adaptation have no result. The surge result is stated for the mean field only; there is no claim that it is robust to finite-size fluctuations. The network values are single runs (one seed) and are drawn without error bars; no agreement criterion is applied to them, so the network symbols have one shape per sweep direction.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 6 stored-value claims listed for F2, 4 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 8 executable checks for F2, 8 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 46 (accepted by the user: journal captions follow the data; the draft stays); 49; 56.

## F3

Draft audit copy: F3 (figures/F3/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/F3/F3_journal.png | 658880b296d0212373732b51d3febc6bbf8284cd73f91cdafd001f5bfaef7026 |
| tiff | figures/journal/F3/F3_journal.tiff | e361e04c918d5503d78d7edd50bca8b1db00b29a47881152b66b5102bf548009 |
| pdf | figures/journal/F3/F3_journal.pdf | ad3491c9067e25f0ebb6ef19786d3fcb4d0fd7588f6b2bc3b4965906475249f6 |
| caption short | figures/journal/F3/F3_journal_caption.txt | a4417ff61fa1eefcfbb7119ca465749e469f16b153e0f9dca959ac756522af4c |
| caption full | figures/journal/F3/F3_journal_caption_full.txt | 35707c8addfe650921566c354858c1e601123594b812163e348bbefd1efe1cc1 |
| alt text | figures/journal/supplement/F3_alt_text.txt | 5f372fc10cd59b8875fc7bf94416e719188c6298dff93cba5212521f1e1bf46f |
| supplement | figures/journal/supplement/F3_supplement.md | 2da270f167d7e07cd268bb3384ec4088e6828352c1e55d24ced0b44e4d693cfc |
| source data csv | figures/journal/supplement/F3_source_data.csv | 566e3cce1dc40db8a2f19606b328df15d5e92b5bf01b09a351848c27553376c8 |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: e12a1086fbe84d1f121618b82dfe61afd7e7b951c1d67b541e782e3e74d1bbc6; draft F3: e12a1086fbe84d1f121618b82dfe61afd7e7b951c1d67b541e782e3e74d1bbc6; equal: yes. Verifier: PASS - e12a1086fbe8... export e12a1086fbe8 draft e12a1086fbe8; PASS - 102 of the 102 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (12, 12, 0, 0) and short caption (7, 7, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of F3 (shared by the parts of a split figure): equal 46, other 11 (rows without a comparison are not counted as equal).
- Verifier rows for F3 (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/F3/F3_journal_caption_full.txt):

> Failed checks. Shown, not dropped (the full list with value, threshold and source is in the supplement): RB9(b) (frequency mapping), spectral frequency against cycle frequency at the headline: FAIL (value blank in the stored table; threshold within the inverse of the window length). The stored table gives no value for this row; the values are those of the project log: spectral 49.0 Hz, cycle 44.609 Hz, difference 4.391 Hz against the allowed 0.5 Hz (the inverse of the 2 s window). Red titles show a FAIL (a failed check concerns the panel). The check RB9(b) (spectral against cycle frequency at the headline) is shown in the title of (a), (b) and (c) as 'frequency check: FAIL'. (a) and (b) are the same frequency map at other Delta; the failed check was made at the main example in (c) and bears on them too. The panels draw the cycle frequency and the failed check compares it with the spectral peak, so the two frequencies are marked on the one shared colour bar (a tick at the cycle frequency, a tick at the spectral peak, and their difference).
> Limits. Claim limits: All earlier failures and limits stand: the failure of check RB1 (network against mean field), gate G7 not passed, the failure of the D24 rule, the six limits set when gate G4 (network against mean field) was triggered, and the limits ruled for the map, control and perturbation runs. The surge result is stated for model M3 only; there is no claim about the models M4 or M3a and M3b, and the parts of check RB8 that concern M4 and adaptation have no result. The spectral frequency and the cycle frequency differ by 4.39 Hz at the headline (RB9(b) failed); peak frequencies are the classifier's spectral peaks. RB9(b) failed: the spectral frequency differs from the cycle frequency by 4.391 Hz against the allowed 0.5 Hz.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 4 stored-value claims listed for F3, 4 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 12 executable checks for F3, 12 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 49; 55 (EPS extra differs between builds); 56.

## F4a

Draft audit copy: F4 (figures/F4/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/F4a/F4a_journal.png | 04ccdaa6b557706e39b5b7c61501c6b2b982a9dfb642c00021dce033c4a27a5a |
| tiff | figures/journal/F4a/F4a_journal.tiff | 0a851b2c41e33d99d8ace33b16338e06371f01863547eaba43290cb346bc0640 |
| pdf | figures/journal/F4a/F4a_journal.pdf | b104bc200eb2755ddbf677f3f920545f9ded07fa0424f2164e57fd3b297843bf |
| caption short | figures/journal/F4a/F4a_journal_caption.txt | dae33a6d95948cfc9e13fdf0a1138c32d9034c14879cd1b211a2a22a32f1fd12 |
| caption full | figures/journal/F4a/F4a_journal_caption_full.txt | 49d9abd3ef2a49a290a83d48026fa1c6f42b5c8297dff8ae106d73a238c74cd0 |
| alt text | figures/journal/supplement/F4a_alt_text.txt | f9442e9e7179381f277d341fc14f829af9dd6d833ed507c3a696183575e6c38b |
| supplement | figures/journal/supplement/F4a_supplement.md | 8fc2cca964b934190f7e92f03d9249fde7e59f28b8fd7569f467d9d82dbc0c68 |
| source data csv | figures/journal/supplement/F4a_source_data.csv | 3ed1044723e2d81d8e461d6c5645e56c6a8bc1632061424da58cd30540d2d8e4 |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: fb05eb9226c9f4d6242ec4ba5fb15f4429eff3680468dc89447bcdf7f2343d6a; draft F4: fb05eb9226c9f4d6242ec4ba5fb15f4429eff3680468dc89447bcdf7f2343d6a; equal: yes. Verifier: PASS - fb05eb9226c9... export fb05eb9226c9 draft fb05eb9226c9; PASS - 106 of the 162 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (19, 19, 0, 0) and short caption (12, 12, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of F4 (shared by the parts of a split figure): equal 58, other 21 (rows without a comparison are not counted as equal).
- Verifier rows for F4a (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/F4a/F4a_journal_caption_full.txt):

> Failed checks. Shown, not dropped (the full list with value, threshold and source is in the supplement): RB3(a) (ramp rate), the onset prediction on the testable in-range runs: FAIL (0 of 6 testable in-range runs; threshold within one step of the prediction grid); RB3(b) (ramp rate), the delay under a noise floor, classifier onset reading: FAIL (value blank in the stored table; threshold blank in the stored table); RB6 (numerical convergence), agreement of the two solvers on the headline onset: FAIL (181 ms; threshold 1 ms). Red titles show a FAIL (a failed check concerns the panel). The check RB3(a), RB6 solver onset (the onset must lie within one step of the entry-exit prediction in the testable runs, and the two solvers must agree on the onset at the main example) is shown in the title of (a) as 'prediction FAIL, solver FAIL'. The check RB3(b) (the delay under a noise floor must meet the check under the classifier-onset reading) is shown in the title of (e) as 'Floor, classifier onset: FAIL'. The RB3(b) row has no stored value or threshold; what is drawn is that the classifier-onset delays tie at −1.5 at levels 0 and 1. The noise-robustness FAILs (RB2 headline class kept, RB2 noisy subgrid agreement, rule D24) are listed with F4b.
> Limits. Claim limits: All earlier failures and limits stand: the failure of check RB1 (network against mean field), gate G7 not passed, the failure of the D24 rule, the six limits set when gate G4 (network against mean field) was triggered, and the limits ruled for the map, control and perturbation runs. The surge result is stated for model M3 only; there is no claim about the models M4 or M3a and M3b, and the parts of check RB8 that concern M4 and adaptation have no result. Every class that depends on the test for damped against non-damped oscillations is provisional. There is no claim that the onset follows the entry-exit prediction; the onset check is not validated (0 of 6 testable in-range runs within one step of the prediction). The delay of the main example is taken from the runs with a noise floor, and the noise-free onset depends on the solver (58.698 s and 58.879 s for the two solvers, 181 ms apart, unexplained). The delay under a noise floor is reported under both onset readings (the raw crossing meets the check, the classifier onset gives equal delays and does not meet it). The estimator for damped against non-damped oscillations fails 2 of 8 ring items of its own test; the classes that depend on it are provisional. The onset check is not judged at the main example (it covers 0 to 2 of the 13 ramp durations). The classifier flags a surge on pure trend plus noise at a window length of 0.2 s; short windows give false surges (306, 400, 172 and 24 of 500 white-noise records at window lengths of 0.2, 0.333, 0.593 and 1.054 s). The direction of the change of the delay with the floor level is unresolved at ramp durations of 10 s and 316 s.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 1 stored-value claims listed for F4a, 1 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 5 executable checks for F4a, 5 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 49; 56; 57 (UNVERIFIED reading of the duration floor).

## F4b

Draft audit copy: F4 (figures/F4/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/F4b/F4b_journal.png | 7b422e38e0f4f18cae984789b954fe082737467a3ea7c4168d4df061bfa71cd5 |
| tiff | figures/journal/F4b/F4b_journal.tiff | d74c0d3b7b4d4fd1fa1488a781e5d11e6c0c182e92b5fea79560f13b263a1e17 |
| pdf | figures/journal/F4b/F4b_journal.pdf | 386a3cf1dd1156a0a53c9073b4292e01135b72e67189d1f6909eb17f7636d421 |
| caption short | figures/journal/F4b/F4b_journal_caption.txt | 0f69389498fe0c18bff96d2f00ab674ec5a258651f6178cbbd9eef6b1f17a79b |
| caption full | figures/journal/F4b/F4b_journal_caption_full.txt | f942cb3a553ffb6192af6c42cbcdb77befe58fb1454a3e19ddd97b1d93c9c2b7 |
| alt text | figures/journal/supplement/F4b_alt_text.txt | f160cc94c120bad2f99bf6f990011a5e7c836d8b3071ebcc2a02549f89512905 |
| supplement | figures/journal/supplement/F4b_supplement.md | e5cada6f03dd577c50d8da97584efa070708486a6893f3b374db8212b7605e61 |
| source data csv | figures/journal/supplement/F4b_source_data.csv | b010899b118f38644c38a3728ea42e8358946847fd955397a18b5bdf6175dd58 |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: fb05eb9226c9f4d6242ec4ba5fb15f4429eff3680468dc89447bcdf7f2343d6a; draft F4: fb05eb9226c9f4d6242ec4ba5fb15f4429eff3680468dc89447bcdf7f2343d6a; equal: yes. Verifier: PASS - fb05eb9226c9... export fb05eb9226c9 draft fb05eb9226c9; PASS - 86 of the 162 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (8, 8, 0, 0) and short caption (5, 5, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of F4 (shared by the parts of a split figure): equal 58, other 21 (rows without a comparison are not counted as equal).
- Verifier rows for F4b (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/F4b/F4b_journal_caption_full.txt):

> Failed checks. Shown, not dropped (the full list with value, threshold and source is in the supplement): RB2 (noise robustness), agreement of the noisy subgrid with the noise-free map (rule D24): FAIL (97 of 225 cells (43.1 percent); threshold 203 of 225 (90 percent, D24)); RB2 (noise robustness), headline class kept at the noise level sigma: FAIL (7 of 10 (0 failed); threshold >= 8 of 10) (n failed = failed runs among the seeds, counted as not kept). Red titles show a FAIL (a failed check concerns the panel). The check RB2 (the main-example class must be kept in at least 8 of 10 noisy seeds, and at least 90 percent of the cells of the noisy subgrid must agree with the noise-free class) is shown in the title of (e) as 'noise robustness FAIL'. The sigma check also FAILED (stored status in Parameters). The onset-prediction, solver and noise-floor FAILs (RB3(a), RB6 solver onset, RB3(b)) are listed with F4a.
> Limits. Claim limits: All earlier failures and limits stand: the failure of check RB1 (network against mean field), gate G7 not passed, the failure of the D24 rule, the six limits set when gate G4 (network against mean field) was triggered, and the limits ruled for the map, control and perturbation runs. The surge result is stated for model M3 only; there is no claim about the models M4 or M3a and M3b, and the parts of check RB8 that concern M4 and adaptation have no result. There is no claim that the regime map is robust to noise, and the class S-rel is not counted as evidence of a ramp in the noisy mode (mode N). Every class that depends on the test for damped against non-damped oscillations is provisional. The estimator for damped against non-damped oscillations fails 2 of 8 ring items of its own test; the classes that depend on it are provisional. The baseline is taken as zero, including for noise-free inputs. The classifier flags a surge on pure trend plus noise at a window length of 0.2 s; short windows give false surges (306, 400, 172 and 24 of 500 white-noise records at window lengths of 0.2, 0.333, 0.593 and 1.054 s). The noise level sigma = 0.0624 is checked and not confirmed; the noisy mean-field runs are labelled as such. The headline class is kept in 7 of 10 seeds at the noise level sigma (8 are needed); the controls without a ramp reach 7 of 10. The spectral frequency and the cycle frequency differ by 4.39 Hz at the headline (RB9(b) failed); peak frequencies are the classifier's spectral peaks. RB2 failed: the headline class is kept in 7 of 10 seeds at the noise level sigma, and the noisy subgrid agrees at 97 of 225 cells. The D24 rule failed: subgrid agreement is 43.1 percent on the raw classes. Scope of the count 'the controls without a ramp reach 7 of 10': it comes from the noisy mean-field runs with constant parameters at the start state of the headline, 10 seeds at each noise level; those runs are not network runs and are not drawn here.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 3 stored-value claims listed for F4b, 1 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 5 executable checks for F4b, 5 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 49; 50 (legend scope); 52 (caption at 650 of 650 words); 56; 57 (UNVERIFIED reading of the duration floor).

## F5

Draft audit copy: F5 (figures/F5/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/F5/F5_journal.png | 22cc0dff3980a632738aa08609df5e70eff732a6d2d08a6bcbd58c5820095175 |
| tiff | figures/journal/F5/F5_journal.tiff | 61d13b62c6a18134611512f29832b7feb3b99d4918ca41c8ddb17da2bd73ab78 |
| pdf | figures/journal/F5/F5_journal.pdf | eb1a5cdc3feb19fee0fcf14d56af2d891141c34a749926ad2421223994c584e3 |
| caption short | figures/journal/F5/F5_journal_caption.txt | 870baeb3459b258befcae0964642f67146cc351f790c83f6aa8579fdb7b7f2cc |
| caption full | figures/journal/F5/F5_journal_caption_full.txt | 5c1353b32c1b34949aa66e8d6ee32454ecb4e5f9ff7d4c3ecc08c9983ae20943 |
| alt text | figures/journal/supplement/F5_alt_text.txt | 138b6f90510b9d72715f40b92f6a30154de18c11f68945a05f0bba8e4fe6aa1c |
| supplement | figures/journal/supplement/F5_supplement.md | 2fc48f8da3ab7cb5fe4d9f90d2381aa15e32080b28e2a3d0a2b4dadeb696ef40 |
| source data csv | figures/journal/supplement/F5_source_data.csv | f9b85fa88df3c14b1e1c577944dcea688f61c081b0df0d2614b295c013d3a40a |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: 4a32b1c3061260eaf9defd322a6a3304ce2b190468459a338cf9f9b5849de2c8; draft F5: 4a32b1c3061260eaf9defd322a6a3304ce2b190468459a338cf9f9b5849de2c8; equal: yes. Verifier: PASS - 4a32b1c30612... export 4a32b1c30612 draft 4a32b1c30612; PASS - 44 of the 62 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (34, 34, 0, 0) and short caption (5, 5, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of F5 (shared by the parts of a split figure): equal 143, other 22 (rows without a comparison are not counted as equal).
- Verifier rows for F5 (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/F5/F5_journal_caption_full.txt):

> Failed checks. Shown, not dropped (the full list with value, threshold and source is in the supplement): RB1 (network against mean field), headline path at a ramp duration of 10 s: FAIL (0 of 3 seeds; threshold 3 of 3); RB1 (network against mean field), headline path at a ramp duration of 120 s: FAIL (0 of 3 seeds; threshold 3 of 3); RB1 (network against mean field), the 4 map cells at a ramp duration of 30 s: FAIL (1 of 4 cells; threshold >= 3 of 4); RB1 (network against mean field), overall verdict: FAIL (value blank in the stored table: it is the verdict over its three parts (headline, cells, ramp-duration rule), which are in the note column of the stored table; no single threshold); RB2 (noise robustness), agreement of the noisy subgrid with the noise-free map (rule D24): FAIL (97 of 225 cells (43.1 percent); threshold 203 of 225 (90 percent, D24)); RB2 (noise robustness), headline class kept at the noise level sigma: FAIL (7 of 10 (0 failed); threshold >= 8 of 10) (n failed = failed runs among the seeds, counted as not kept); RB6 (numerical convergence), the network peak frequency f_pk when the step is halved: FAIL (value blank in the stored table; threshold < 0.02). The sigma check also FAILED (stored status in Parameters). Red titles show a FAIL (a failed check concerns the panel). The check RB1 (network against mean field, the 4 map cells) is shown in the title of (a) as 'network vs mean field, cells: FAIL'. The check RB1 (network against mean field, the 4 map cells) is shown in the title of (b) as 'network vs mean field FAIL'. The check D24 (the rule that at least 90% of the cells of the noisy subgrid agree with the noise-free class) is shown in the title of (c) as '90 percent agreement rule: FAILED'. Per-seed results against N, with the RB6 network f_pk FAIL, are in F5c.
> Limits. Claim limits: All earlier failures and limits stand: the failure of check RB1 (network against mean field), gate G7 not passed, the failure of the D24 rule, the six limits set when gate G4 (network against mean field) was triggered, and the limits ruled for the map, control and perturbation runs. The surge result is stated for model M3 only; there is no claim about the models M4 or M3a and M3b, and the parts of check RB8 that concern M4 and adaptation have no result. Surge classes found in network records at N = 10,000 are not evidence of a ramp-driven surge: the network control without a ramp was flagged in 10 of 10 seeds, and the ramp runs in 10 of 10. There is no claim that the regime map is robust to noise, and the class S-rel is not counted as evidence of a ramp in the noisy mode (mode N). Failure label (c) of the regime map (a cell without a surge class whose frequency is below 25 Hz; drawn in F6) is a flag, not a demonstrated cause; not applicable here because no failure label is drawn in F5 (F6 draws them). The check of the regime-map failure labels covers 1,056 of the 1,057 surge-class cells; not applicable here because no failure label is drawn in F5 (F6 draws them). Every class that depends on the test for damped against non-damped oscillations is provisional. The boundary definition and the extension of the episode-exit rule to the paths P3 and P4 are our own. The estimator for damped against non-damped oscillations fails 2 of 8 ring items of its own test; the classes that depend on it are provisional. The baseline is taken as zero, including for noise-free inputs. The network at N = 10,000 and 30,000 does not reproduce the mean-field classes (0 of 3 seeds at T_ramp 10 s and 120 s; 1 of 4 cells). The surge result is stated for the mean field only; there is no claim that it is robust to finite-size fluctuations. No-ramp network controls are classified into surge classes. The noise level sigma = 0.0624 is checked and not confirmed; the noisy mean-field runs are labelled as such. The headline class is kept in 7 of 10 seeds at the noise level sigma (8 are needed); the controls without a ramp reach 7 of 10. There is no claim of agreement in peak frequency or in class between the network and the mean field (the RB6 check of the network peak frequency failed). The spectral frequency and the cycle frequency differ by 4.39 Hz at the headline (RB9(b) failed); peak frequencies are the classifier's spectral peaks. RB1 failed: the headline at 10 s failed, the headline at 120 s failed, and the network agrees at 1 of 4 cells. RB2 failed: the headline class is kept in 7 of 10 seeds at the noise level sigma, and the noisy subgrid agrees at 97 of 225 cells. The D24 rule failed: subgrid agreement is 43.1 percent on the raw classes. Scope of the counts 'flagged in 10 of 10 seeds' and 'the ramp runs in 10 of 10': they come from the exploratory network runs of the negative-control step at N = 10,000 with 10 seeds each (the negative-control path along which the mean excitability falls, and the same network held at constant parameters without a ramp); those runs are not drawn here. Scope of the count 'the controls without a ramp reach 7 of 10': it comes from the noisy mean-field runs with constant parameters at the start state of the headline, 10 seeds at each noise level; those runs are not network runs and are not drawn here.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 1 stored-value claims listed for F5, 1 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 5 executable checks for F5, 5 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 49; 51 (N written 1e3 in the alt text); 55; 56.

## F5c

Draft audit copy: F5 (figures/F5/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/F5c/F5c_journal.png | 84713c3349799febac4c0864fa97c65c40c170a534bc9ae5be44e7b17963017d |
| tiff | figures/journal/F5c/F5c_journal.tiff | 16ee475e738bb168f7372b3138c768da2727de632d68a7a4fb2a60a6cdab1168 |
| pdf | figures/journal/F5c/F5c_journal.pdf | 221eab9ccc806bac35d6ecea8a3bff38380ab258e8ec1261fa47cd99cf31abb2 |
| caption short | figures/journal/F5c/F5c_journal_caption.txt | 1b236dd5e2dd0f120d5c2b2b6f6c9a2ee081cb22462b0497412357a24f956470 |
| caption full | figures/journal/F5c/F5c_journal_caption_full.txt | af19a27d0a6d330857e26177fff4b574533d2b9c9f6e5bbceaf9154d90c5ad45 |
| alt text | figures/journal/supplement/F5c_alt_text.txt | 23259e68c54e6835096fcc6dd9018b17c24eef1a434969285edfebc19b31c6af |
| supplement | figures/journal/supplement/F5c_supplement.md | 165e7ee140b43ea75d110c814fd4c31ab7b2ee572ef1be8ff0993300d823e7ca |
| source data csv | figures/journal/supplement/F5c_source_data.csv | 08311e6599724eb7ddd34540ace405d6576121024bf27abb8ee9714fe205caee |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: 4a32b1c3061260eaf9defd322a6a3304ce2b190468459a338cf9f9b5849de2c8; draft F5: 4a32b1c3061260eaf9defd322a6a3304ce2b190468459a338cf9f9b5849de2c8; equal: yes. Verifier: PASS - 4a32b1c30612... export 4a32b1c30612 draft 4a32b1c30612; PASS - 22 of the 62 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (16, 16, 0, 0) and short caption (8, 8, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of F5 (shared by the parts of a split figure): equal 143, other 22 (rows without a comparison are not counted as equal).
- Verifier rows for F5c (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/F5c/F5c_journal_caption_full.txt):

> Failed checks. Shown, not dropped (the full list with value, threshold and source is in the supplement): RB6 (numerical convergence), the network peak frequency f_pk when the step is halved: FAIL (value blank in the stored table; threshold < 0.02). The sigma check also FAILED (stored status in Parameters). Red titles show a FAIL (a failed check concerns the panel). The check RB6 (numerical convergence, the network f_pk when the step is halved) is shown in the title of (b) as 'step-halving check: FAIL'. The test itself (halving the step) is not drawn because its runs are not stored; a plain line in panel (b) says so. The F5 caption lists the other FAILs of the figure (RB1 cells, D24, RB2).
> Limits. Claim limits that change how panel (a) reads: no-ramp network controls are classified into surge classes, and there is no claim that the regime map is robust to noise. Claim limits: All earlier failures and limits stand: the failure of check RB1 (network against mean field), gate G7 not passed, the failure of the D24 rule, the six limits set when gate G4 (network against mean field) was triggered, and the limits ruled for the map, control and perturbation runs. The surge result is stated for model M3 only; there is no claim about the models M4 or M3a and M3b, and the parts of check RB8 that concern M4 and adaptation have no result. Surge classes found in network records at N = 10,000 are not evidence of a ramp-driven surge: the network control without a ramp was flagged in 10 of 10 seeds, and the ramp runs in 10 of 10. There is no claim that the regime map is robust to noise, and the class S-rel is not counted as evidence of a ramp in the noisy mode (mode N). Failure label (c) of the regime map (a cell without a surge class whose frequency is below 25 Hz; drawn in F6) is a flag, not a demonstrated cause; not applicable here because no failure label is drawn in F5 (F6 draws them). The check of the regime-map failure labels covers 1,056 of the 1,057 surge-class cells; not applicable here because no failure label is drawn in F5 (F6 draws them). Every class that depends on the test for damped against non-damped oscillations is provisional. The boundary definition and the extension of the episode-exit rule to the paths P3 and P4 are our own. The estimator for damped against non-damped oscillations fails 2 of 8 ring items of its own test; the classes that depend on it are provisional. The baseline is taken as zero, including for noise-free inputs. The network at N = 10,000 and 30,000 does not reproduce the mean-field classes (0 of 3 seeds at T_ramp 10 s and 120 s; 1 of 4 cells). The surge result is stated for the mean field only; there is no claim that it is robust to finite-size fluctuations. No-ramp network controls are classified into surge classes. The noise level sigma = 0.0624 is checked and not confirmed; the noisy mean-field runs are labelled as such. The headline class is kept in 7 of 10 seeds at the noise level sigma (8 are needed); the controls without a ramp reach 7 of 10. There is no claim of agreement in peak frequency or in class between the network and the mean field (the RB6 check of the network peak frequency failed). The spectral frequency and the cycle frequency differ by 4.39 Hz at the headline (RB9(b) failed); peak frequencies are the classifier's spectral peaks. RB1 failed: the headline at 10 s failed, the headline at 120 s failed, and the network agrees at 1 of 4 cells. RB2 failed: the headline class is kept in 7 of 10 seeds at the noise level sigma, and the noisy subgrid agrees at 97 of 225 cells. The D24 rule failed: subgrid agreement is 43.1 percent on the raw classes. Scope of the counts 'flagged in 10 of 10 seeds' and 'the ramp runs in 10 of 10': they come from the exploratory network runs of the negative-control step at N = 10,000 with 10 seeds each (the negative-control path along which the mean excitability falls, and the same network held at constant parameters without a ramp); those runs are not drawn here. Scope of the count 'the controls without a ramp reach 7 of 10': it comes from the noisy mean-field runs with constant parameters at the start state of the headline, 10 seeds at each noise level; those runs are not network runs and are not drawn here.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 2 stored-value claims listed for F5c, 2 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 0 executable checks for F5c, 0 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 48 (accepted by the user: control durations are in the source data); 49; 51; 55; 56; 57 (UNVERIFIED reading of the duration floor).

## F6

Draft audit copy: F6 (figures/F6/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/F6/F6_journal.png | 9b0e21a46a1f57a21324796b232854b192908d5dc5e8a3fc4843ad8c1537f025 |
| tiff | figures/journal/F6/F6_journal.tiff | e82667be656a99c42f4070ccc7b3544a9aa3b4c58e9f7146c9971002472effa7 |
| pdf | figures/journal/F6/F6_journal.pdf | 77f1845ae0b7525e4d48d98e1f4fa5df42b979195e9817748a74f33126ef9e00 |
| caption short | figures/journal/F6/F6_journal_caption.txt | a0d3f4aa4e0dbe5d876a08be670b087b366ebabc97f797b2ac83bd9c742a0628 |
| caption full | figures/journal/F6/F6_journal_caption_full.txt | 3b4354f0fc560114045c764eb951f618ac3fd65a354326f0a0c6fcd899d1974d |
| alt text | figures/journal/supplement/F6_alt_text.txt | 6eaf2af0b52c296518336d57ca7ca4d67b63474b4cc3f4370da4543589e32ebd |
| supplement | figures/journal/supplement/F6_supplement.md | e314b955dc8d4fd360fad873ad3d00c12386556b5ef7ca24eaa3088a7a8f8d19 |
| source data csv | figures/journal/supplement/F6_source_data.csv | a911c78a1dd193601050abb73b08178b9fdeddaca645b7e8bb8982d13b61fdd7 |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: 4dafe2ab2f5ee3c2b505f82d4f50a3a8b96a9bb1c9cdfb5379b7a3e6f7e2c532; draft F6: 4dafe2ab2f5ee3c2b505f82d4f50a3a8b96a9bb1c9cdfb5379b7a3e6f7e2c532; equal: yes. Verifier: PASS - 4dafe2ab2f5e... export 4dafe2ab2f5e draft 4dafe2ab2f5e; PASS - 28 of the 28 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (19, 19, 0, 0) and short caption (5, 5, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of F6 (shared by the parts of a split figure): equal 23, other 7 (rows without a comparison are not counted as equal).
- Verifier rows for F6 (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/F6/F6_journal_caption_full.txt):

> Failed checks. Shown, not dropped (the full list with value, threshold and source is in the supplement): G7 (negative-control gate): FAIL (value blank in the stored table; threshold blank in the stored table). Red titles show a FAIL (a failed check concerns the panel). The check G7 (the negative-control gate: the network run of the first negative control must not be in a surge class) is shown in the title of (c) as 'Negative-control check: FAIL'. The failed result is the class S+ of the one network run, drawn as the red circle of (c); the stored table gives no value or threshold for the gate row.
> Limits. Claim limits: All earlier failures and limits stand: the failure of check RB1 (network against mean field), gate G7 not passed, the failure of the D24 rule, the six limits set when gate G4 (network against mean field) was triggered, and the limits ruled for the map, control and perturbation runs. The surge result is stated for model M3 only; there is no claim about the models M4 or M3a and M3b, and the parts of check RB8 that concern M4 and adaptation have no result. Surge classes found in network records at N = 10,000 are not evidence of a ramp-driven surge: the network control without a ramp was flagged in 10 of 10 seeds, and the ramp runs in 10 of 10. Failure label (c) of the regime map (a cell without a surge class whose frequency is below 25 Hz; drawn in F6) is a flag, not a demonstrated cause. The check of the regime-map failure labels covers 1,056 of the 1,057 surge-class cells. Every class that depends on the test for damped against non-damped oscillations is provisional. The boundary definition and the extension of the episode-exit rule to the paths P3 and P4 are our own; not applicable here because neither the boundary of the regime map nor the exit extension of the episode rule to P3 and P4 is drawn. The estimator for damped against non-damped oscillations fails 2 of 8 ring items of its own test; the classes that depend on it are provisional. The baseline is taken as zero, including for noise-free inputs. No-ramp network controls are classified into surge classes. Gate G7 was not passed: the network run of the first negative control (the hypoxia path with the mean excitability falling by the same amount, with coupling, heterogeneity and synaptic decay fixed and no common drive) is in class S+. The noise level sigma = 0.0624 is checked and not confirmed; the noisy mean-field runs are labelled as such. Scope of the counts 'flagged in 10 of 10 seeds' and 'the ramp runs in 10 of 10': they come from the exploratory network runs of the negative-control step at N = 10,000 with 10 seeds each (the negative-control path along which the mean excitability falls, and the same network held at constant parameters without a ramp); those runs are not drawn here.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 1 stored-value claims listed for F6, 1 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 7 executable checks for F6, 7 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 49; 56.

## FS1

Draft audit copy: FS1 (figures/FS1/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/FS1/FS1_journal.png | e10a6825cd5edd6f351d1c2d9b108e55b3e24ada6f917fa7397faa06c034edb1 |
| tiff | figures/journal/FS1/FS1_journal.tiff | c49127bf937be8d630390af003f0216b33a649c72035429acc000c4fb4e0a7f4 |
| pdf | figures/journal/FS1/FS1_journal.pdf | 737637a280a5b87865ba683e4962466940cddf0fa982c24772c5236fd98b9f54 |
| caption short | figures/journal/FS1/FS1_journal_caption.txt | 35465cf1d2ebb1790e91e1fa92ec96430a803702a397c06bc631dc1be9766e06 |
| caption full | figures/journal/FS1/FS1_journal_caption_full.txt | 984e64698cbd97aab32c0f60ba2963447bddf1742c3e445ac835ed7dda17f8e6 |
| alt text | figures/journal/supplement/FS1_alt_text.txt | 4ca9f417fc258ad74e44f2c6788a1639cf58466546a5ddbd85c9927045696cb8 |
| supplement | figures/journal/supplement/FS1_supplement.md | 03495083e08e43f8b4052035c151db41d3c65f36cfb9a45b8cf2b198072cbfd8 |
| source data csv | figures/journal/supplement/FS1_source_data.csv | 49a55e21fd36dc6fb3ed0551becd99e198443ce3cf70bdb0e494a6d909613b77 |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: e19ae701c594421531ac81fa79814d5099451e189a04d378f7117f4df642f9b0; draft FS1: e19ae701c594421531ac81fa79814d5099451e189a04d378f7117f4df642f9b0; equal: yes. Verifier: PASS - e19ae701c594... export e19ae701c594 draft e19ae701c594; PASS - 60 of the 60 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (8, 8, 0, 0) and short caption (8, 8, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of FS1 (shared by the parts of a split figure): equal 21, other 0 (rows without a comparison are not counted as equal).
- Verifier rows for FS1 (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/FS1/FS1_journal_caption_full.txt):

> Failed checks. No row of the project's table of failed checks concerns this figure (our reading of where the checks apply; not verified). Two limits of the checks are stated instead of failures: the sinusoidal-forcing check passes only on our own reading of its burst definition, tolerance and time mapping, with the check against the primary source deferred, and the version of the step test on a network of N simulated spiking neurons was not run because the coupling of an M2 network is unsourced. No panel has a red title: no failed check is drawn here.
> Limits. Claim limits: All earlier failures and limits stand: the failure of check RB1 (network against mean field), gate G7 not passed, the failure of the D24 rule, the six limits set when gate G4 (network against mean field) was triggered, and the limits ruled for the map, control and perturbation runs.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 1 stored-value claims listed for FS1, 1 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 7 executable checks for FS1, 7 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 49; 54 (the STOP of DL-646, not resolved); 55; 56.

## FS2

Draft audit copy: FS2 (figures/FS2/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/FS2/FS2_journal.png | 582566520dd2dbd5214162ad6b18945cd98ba09ddeff483eb45eb519e24b18ea |
| tiff | figures/journal/FS2/FS2_journal.tiff | 272c17784c2e960a196e6f721b41a9841b71afd957328756c0005c404da64870 |
| pdf | figures/journal/FS2/FS2_journal.pdf | deb2dce329bf58689143500b2eb53791cdf0fcc278d9a38c4fbd05e2b00048f2 |
| caption (single) | figures/journal/FS2/FS2_journal_caption.txt | 38675e45b334c9a90365204abfc03625a554cedaccfaa4d2d872fbadac98aff0 |
| alt text | figures/journal/supplement/FS2_alt_text.txt | 82eb6c25cb60bd23195a821d639dccb86aecaedac77593a60db05449eb284b85 |
| supplement | figures/journal/supplement/FS2_supplement.md | cd4444c8d7235946930ad16e012bf7c560702ad0ce5bf2c9cfb4f85523579eb2 |
| source data csv | figures/journal/supplement/FS2_source_data.csv | 246d51e12e6e32916d2dae4f8842b2c7e9d124bc0037b78b747ea7bdf9af453f |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: 72fc4361202cb4d18a344f1186d7651788771ff7ab53d6c3621d1793f6f262af; draft FS2: 72fc4361202cb4d18a344f1186d7651788771ff7ab53d6c3621d1793f6f262af; equal: yes. Verifier: PASS - 72fc4361202c... export 72fc4361202c draft 72fc4361202c; PASS - 97 of the 97 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (10, 10, 0, 0) and short caption (0, 0, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of FS2 (shared by the parts of a split figure): equal 15, other 0 (rows without a comparison are not counted as equal).
- Verifier rows for FS2 (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/FS2/FS2_journal_caption.txt):

> Failed checks. Two failed or not reproduced results concern this figure and both are drawn. (1) The test of the straight-line fit of the squared amplitude of the cycle against tau_d over the pre-set window: the residual must not exceed 2 percent; it is 2.42 percent (panel (b)). (2) The test of the dependence of the frequency on J: the frequency must change by at most 10 percent over the J range; it changes by 13.4, 25.0 and 42.2 percent (panel (l); single source, not verified). Red titles show a FAIL (a failed check concerns the panel). The amplitude-residual check (the straight-line fit of the squared amplitude of the cycle against tau_d over the pre-set window must leave a residual of at most 2 percent) is shown in the title of (b) as 'Amplitude squared: FAIL'. The J-dependence check (the frequency of the linearised model must change by at most 10 percent over the J range at tau_d 8, 20 and 40 ms (single source, not verified)) is shown in the title of (l) as 'Frequency against J: FAIL'. The Hopf point at 4.12 ms against the published 4.95 ms is a recorded departure, drawn in (a). No row of the project's table of failed checks concerns this figure (our reading of where the checks apply; not verified); the version of the step test on a network is not part of this figure.
> Limits. Claim limits: All earlier failures and limits stand: the failure of the network-against-mean-field check, the negative-control gate not passed, the failure of the 90 percent rule (at least 90 percent of the cells must agree), the six limits set when the network-against-mean-field gate was triggered, and the limits ruled for the map, control and perturbation runs. In these limits, control (the same network without the ramp) runs are runs of the project that are not drawn in this figure.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 3 stored-value claims listed for FS2, 3 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 3 executable checks for FS2, 3 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 49; 56.

## FS3

Draft audit copy: FS3 (figures/FS3/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/FS3/FS3_journal.png | 01ed53e0912ad4daf34b8db00f5a480ab502c00a100d23863e31056c1d6256d0 |
| tiff | figures/journal/FS3/FS3_journal.tiff | d62c5208111ff8977809f93cd17699501bfb7f021d7115278dfb3e7e460be8c2 |
| pdf | figures/journal/FS3/FS3_journal.pdf | d0bbab4e41513d489eeda8a852ed5c5cb890fb669db5eb37f2013fd7ba32ec67 |
| caption (single) | figures/journal/FS3/FS3_journal_caption.txt | 3252559faebc4d188a84a82326812d117f984476dd1f48ffb1c37276ad279204 |
| alt text | figures/journal/supplement/FS3_alt_text.txt | 4c0fb76afd3623dceb993cc80d27581c126cbe2cb49e11e0e0bc7730a9bca534 |
| supplement | figures/journal/supplement/FS3_supplement.md | fdfeec8903ab98354bbf39f402e085585726d0709dad16abdfd66325c3d71000 |
| source data csv | figures/journal/supplement/FS3_source_data.csv | 070e6157d6ee86d71cc4c38dea99da2227ac16b960e9c33290fb1f7af97295e1 |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: 93bf2508cc3233ed14a75d7b8b8266e12f895d91725477511fa532bd9b57b258; draft FS3: 93bf2508cc3233ed14a75d7b8b8266e12f895d91725477511fa532bd9b57b258; equal: yes. Verifier: PASS - 93bf2508cc32... export 93bf2508cc32 draft 93bf2508cc32; PASS - 40 of the 40 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (18, 18, 0, 0) and short caption (0, 0, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of FS3 (shared by the parts of a split figure): equal 49, other 3 (rows without a comparison are not counted as equal).
- Verifier rows for FS3 (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/FS3/FS3_journal_caption.txt):

> Failed checks. Failed checks that concern this figure (6; the noisy subgrid (map cells re-run with noise) is the part of the project's map that was re-run with noise; the map cells (one parameter pair of a 30 x 30 grid of mean-field runs) are the cells of the project's map; the ramp-duration rule uses a duration (how long a ramp lasts)): network-against-mean-field check, headline path at a ramp duration of 10 s: FAIL (0 of 3 seeds; threshold 3 of 3); network-against-mean-field check, headline path at a ramp duration of 120 s: FAIL (0 of 3 seeds; threshold 3 of 3); network-against-mean-field check, the 4 map cells at a ramp duration of 30 s: FAIL (1 of 4 cells; threshold >= 3 of 4); network-against-mean-field check, overall verdict: FAIL (value blank in the stored table: it is the verdict over its three parts (headline, cells, ramp-duration rule), which are in the note column of the stored table; no single threshold); noise-robustness check, agreement of the noisy subgrid with the noise-free map (the 90 percent rule: at least 90 percent of the cells agree): FAIL (97 of 225 cells (43.1 percent); threshold 203 of 225 (90 percent)); noise-robustness check, headline class kept at the noise level sigma: FAIL (7 of 10 (0 failed); threshold >= 8 of 10) (n failed = failed runs among the seeds, counted as not kept). The checks against the mean field at the ramp durations 10 s and 120 s and at the 4 map cells are not drawn here (their runs are not in this figure; (a) draws the network at 60 s); the title of (e) is red as 'Noise check: FAIL' and the title of (g) as '90 percent rule: FAILED' (the 90 percent rule: at least 90 percent of the cells of the noisy subgrid must agree with the noise-free class). The heterogeneity check is NOT EVALUABLE (panel (d)). The project's other failed checks are not about this figure; all of them are listed in the supplement. Red titles show a FAIL (a failed check concerns the panel). The noise check (the headline class must be kept (a surge class) in at least 8 of 10 noisy seeds at the noise level sigma) is shown in the title of (e) as 'Noise check: FAIL'. The 90 percent rule (the rule that at least 90% of the cells of the noisy subgrid agree with the noise-free class) is shown in the title of (g) as '90 percent rule: FAILED'.
> Limits. In the limits below, T_ramp is the ramp duration T_ramp (in seconds), the main example (the run fixed before the analysis as the main case) is the reference run of the first paragraph, and control (the same network without the ramp) runs are runs without a ramp: the controls of (a) and (d); the constant-parameter controls of (f) are mean-field runs. Claim limits: All earlier failures and limits stand: the failure of the network-against-mean-field check, the negative-control gate not passed, the failure of the 90 percent rule (at least 90 percent of the cells must agree), the six limits set when the network-against-mean-field gate was triggered, and the limits ruled for the map, control and perturbation runs. Surge classes found in network records at N = 10,000 are not evidence of a ramp-driven surge: the network control without a ramp was flagged in 10 of 10 seeds, and the ramp runs in 10 of 10. There is no claim that the regime map is robust to noise, and the class S-rel is not counted as evidence of a ramp in the noisy mode (mode N). Every class that depends on the test for damped against non-damped oscillations is provisional. The classifier flags a surge on pure trend plus noise at a window length of 0.2 s; short windows give false surges (306, 400, 172 and 24 of 500 white-noise records at window lengths of 0.2, 0.333, 0.593 and 1.054 s). The network at N = 10,000 and 30,000 does not reproduce the mean-field classes (0 of 3 seeds at T_ramp 10 s and 120 s; 1 of 4 cells). The surge result is stated for the mean field only; there is no claim that it is robust to finite-size fluctuations. No-ramp network controls are classified into surge classes. The noise level sigma = 0.0624 is checked and not confirmed; the noisy mean-field runs are labelled as such. No claim is made about whether the result holds for other shapes of the heterogeneity (the check of the heterogeneity shape is not evaluable). The headline class is kept in 7 of 10 seeds at the noise level sigma (8 are needed); the controls without a ramp reach 7 of 10. There is no claim of agreement in peak frequency or in class between the network and the mean field (the numerical-convergence check of the network peak frequency failed). The noise-robustness check failed: the headline class is kept in 7 of 10 seeds at the noise level sigma, and the noisy subgrid agrees at 97 of 225 cells. The 90 percent rule failed: subgrid agreement is 43.1 percent on the raw classes.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 1 stored-value claims listed for FS3, 1 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 1 executable checks for FS3, 1 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 49; 56.

## FS4

Draft audit copy: FS4 (figures/FS4/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/FS4/FS4_journal.png | 29407ccba41c5a8af2647440dc2205d4162b8ec3ae1a08c370a1b1d8dfa1aa00 |
| tiff | figures/journal/FS4/FS4_journal.tiff | 551ccd81db9cbf975b43e19fcdc9f4925e373c9a1cb364aebe763a7888eae2f6 |
| pdf | figures/journal/FS4/FS4_journal.pdf | 2065eb833c14f1c5f01f29b92ea2955903efbad50e96944dc70022c8a40a491f |
| caption (single) | figures/journal/FS4/FS4_journal_caption.txt | 73278db1e62918342d3ab4101b2ae6448a4cc804d0ca161beb629ce99b1bad12 |
| alt text | figures/journal/supplement/FS4_alt_text.txt | e94c36c49f6fb8eb07de832ec0d2d7aaf39fd418233f4bd565f26624ebbe7a53 |
| supplement | figures/journal/supplement/FS4_supplement.md | d3d8290675c87525b5c40eaec778d063a2be81ed22e074c8391d1b625e17ef5f |
| source data csv | figures/journal/supplement/FS4_source_data.csv | f168b0c87a92b1d08171ff06c91b8f726de6189af75e5f3aae7e3082ec19c3b4 |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: 188b383f47b2cb6a75d8e5565ed7bfac86804f4a745c41fe915ebc70038edd6d; draft FS4: 188b383f47b2cb6a75d8e5565ed7bfac86804f4a745c41fe915ebc70038edd6d; equal: yes. Verifier: PASS - 188b383f47b2... export 188b383f47b2 draft 188b383f47b2; PASS - 36 of the 36 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (18, 18, 0, 0) and short caption (0, 0, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of FS4 (shared by the parts of a split figure): equal 10, other 18 (rows without a comparison are not counted as equal).
- Verifier rows for FS4 (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).

Failed checks shown and claim limits kept (word for word from figures/journal/FS4/FS4_journal_caption.txt):

> Failed checks. Failed checks that concern this figure (2): Numerical-convergence check, agreement of the two solvers on the onset of the main example: FAIL (181 ms; threshold 1 ms); Numerical-convergence check, the network peak frequency when the time step is halved: FAIL (value blank in the stored table; threshold < 0.02). The network row has no value in the stored table; the recorded evaluation gives 0 of 3 seeds passing under the classifier-episode reading and 2 of 3 under the spectrum-maximum reading (the check fails if any seed that can be evaluated fails). The solver difference is drawn in (a) and the changes of the network peak frequency in (f) and (g); results that rest on the network peak frequency are not used as evidence. The project's other failed checks are not about this figure; all of them are listed in the supplement. Red titles show a FAIL (a failed check concerns the panel). The solver check (the two solvers must agree on the onset of the main example within 1 ms) is shown in the title of (a) as 'Onset by setting; solver check: FAIL'. The check of the network peak frequency (halving the network time step must change the peak frequency by less than 2 percent) is shown in the title of (f) as 'Network peak frequency: FAIL'. The check of the network peak frequency (halving the network time step must change the peak frequency by less than 2 percent) is shown in the title of (g) as 'Change per step halving: FAIL'.
> Limits. In the limits below, T_ramp is the ramp duration T_ramp (in seconds), the main example is the run of the first paragraph, and control (the same network without the ramp) runs are runs of the project that are not drawn in this figure. Claim limits: All earlier failures and limits stand: the failure of the network-against-mean-field check, the negative-control gate not passed, the failure of the 90 percent rule (at least 90 percent of the cells must agree), the six limits set when the network-against-mean-field gate was triggered, and the limits ruled for the map, control and perturbation runs. Every class that depends on the test for damped against non-damped oscillations is provisional. The delay of the main example is taken from the runs with a noise floor, and the noise-free onset depends on the solver (58.698 s and 58.879 s for the two solvers, 181 ms apart, unexplained). The delay under a noise floor is reported under both onset readings (the raw crossing meets the check, the classifier onset gives equal delays and does not meet it). The rerun of the numerical-convergence check for the network, named when the network-against-mean-field gate was triggered, is read as the network part of the numerical checks (our reading, not verified). There is no claim of agreement in peak frequency or in class between the network and the mean field (the numerical-convergence check of the network peak frequency failed). The comparison of the default solver with the Radau solver covers the ramp duration 120 s only. The direction of the change of the delay with the floor level is unresolved at ramp durations of 10 s and 316 s. In the numerical-convergence check of the network, the peak frequency of episodes shorter than the window is found by a method that the rules fixed before the analysis do not state. The numerical-convergence check failed for the peak frequency of the network, under both readings of the peak frequency.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 4 stored-value claims listed for FS4, 3 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 9 executable checks for FS4, 9 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 49; 56.

## FS5

Draft audit copy: FS5 (figures/FS5/); the journal files are the main versions.

| file | path | SHA-256 (full) |
|---|---|---|
| png | figures/journal/FS5/FS5_journal.png | c94e9b2c722ae3cc595679d4eea8458caba16e9b8cd488364084f24cf2281786 |
| tiff | figures/journal/FS5/FS5_journal.tiff | dd4424f54bedd7a750dddf2652da9a08e24dba3d821fac9f73fae2e5ccab5f9f |
| pdf | figures/journal/FS5/FS5_journal.pdf | 1aa2437af1d64dada969a12fa5bc2186c8c77ffecad012ab75c55a0229425460 |
| caption (single) | figures/journal/FS5/FS5_journal_caption.txt | b5adab6a2005fd99b1c855616fc6d6c6fc09bf3de58a2b66bd242fdee02b8b8f |
| alt text | figures/journal/supplement/FS5_alt_text.txt | 55a35abedfa251de2fd52c9bdeb2609400af32854c8a9a37c89ef56bb38b507b |
| supplement | figures/journal/supplement/FS5_supplement.md | fd983284aafeedb0e012bc946a11471cd909ed3567d6afa80b5b1e57d2d9f895 |
| source data csv | figures/journal/supplement/FS5_source_data.csv | 927f43ba0e6fbd1d2e7518d42a58dccdbfd8934e1a1015ee9b138bfab81cc9b6 |

- Build commit: 5e9057563c6c24fbac16b99000e547d08ef9a31a.
- Drawn-data digest of the journal figure: 66238f8b7f480cf98b6ed4d76f9ec52f6f1cb81802622076ef7f733fac8d31a5; draft FS5: 66238f8b7f480cf98b6ed4d76f9ec52f6f1cb81802622076ef7f733fac8d31a5; equal: yes. Verifier: PASS - 66238f8b7f48... export 66238f8b7f48 draft 66238f8b7f48; PASS - 52 of the 52 arrays of the draft data, per-array digests equal.
- Independent comparison (this run): journal caption (15, 15, 0, 0) and short caption (0, 0, 0, 0) as (quantities, equal, not equal, unresolved); draft rows of FS5 (shared by the parts of a split figure): equal 28, other 1 (rows without a comparison are not counted as equal).
- Verifier rows for FS5 (this run): 44 PASS, 0 FAIL, 1 MANUAL (the MANUAL row is the colour-vision check of the user).
- Reproducibility of the corrected FS5 text (13w W1, DL-714): one build from the committed code (commit af5193d, scratchpad, nothing written under figures/) gave the same PNG, TIFF, PDF, caption, alt text, source-data CSV and drawn-data digest as listed above; the supplement differed only in the build-commit hash and the provenance-file hash (full values in DL-714).

Failed checks shown and claim limits kept (word for word from figures/journal/FS5/FS5_journal_caption.txt):

> Failed checks. Failed checks that concern this figure (1): Frequency check, spectral frequency against cycle frequency at the main example: FAIL (value blank in the stored table; threshold within the inverse of the window length). The value is blank in the stored table; the numbers (49.0 Hz, 44.609 Hz and the difference 4.391 Hz) are those of the recorded evaluation. The estimator for damped against non-damped oscillations also fails part of its own test (a limit, listed below). The project's other failed checks are not about this figure; all of them are listed in the supplement. Red titles show a FAIL (a failed check concerns the panel). The frequency check (the spectral and the cycle frequency of the main example must differ by at most 0.5 Hz) is shown in the title of (h) as 'Frequency check: FAIL'.
> Limits. In the limits below, T_ramp is the ramp duration T_ramp (in seconds), the main example is the run fixed before the analysis as the main case, the network is a simulated network of N spiking neurons, and control (the same network without the ramp) runs are runs of the project that are not drawn in this figure. Claim limits: All earlier failures and limits stand: the failure of the network-against-mean-field check, the negative-control gate not passed, the failure of the 90 percent rule (at least 90 percent of the cells must agree), the six limits set when the network-against-mean-field gate was triggered, and the limits ruled for the map, control and perturbation runs. Every class that depends on the test for damped against non-damped oscillations is provisional. The estimator for damped against non-damped oscillations fails 2 of 8 ring items of its own test; the classes that depend on it are provisional. The baseline is taken as zero, including for noise-free inputs. The classifier flags a surge on pure trend plus noise at a window length of 0.2 s; short windows give false surges (306, 400, 172 and 24 of 500 white-noise records at window lengths of 0.2, 0.333, 0.593 and 1.054 s). The spectral frequency and the cycle frequency differ by 4.39 Hz at the headline (the frequency check failed); peak frequencies are the classifier's spectral peaks. The check of the dimensional against the non-dimensional frequency mapping rests on a test at the unit level only (a 1 s ramp, membrane time constants tau of 10 and 20 ms), not on the main example. The rules fixed before the analysis do not name the estimator of the cycle frequency in the frequency check; the fractions of map cells within the bound are 51 of 760 (Hilbert phase) and 45 of 760 (zero crossings), both reported, and the failure of the frequency check at the main example holds under either estimator. The frequency check failed: the spectral frequency differs from the cycle frequency by 4.391 Hz against the allowed 0.5 Hz.

Audits that cover it:
- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value passed in this run.
- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): 3 stored-value claims listed for FS5, 3 equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* ['passed'] in this run.
- P2 alt text (docs/ms13_13t11_alt_table.md): 1 executable checks for FS5, 1 equal; test test_p2_every_alt_text_claim_equals_the_source_data passed in this run.
- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.

Open close items that touch it (docs/ms13_close_items.md, section L): 45 (accepted by the user: the full captions carry what the short captions leave out); 49; 53 (answered in 13v: no 'not run' cell in (a); the caption was corrected); 56.

## Tags

none made; 13u makes them when the user says tag, journal files as main versions, drafts as audit copies. Tags that exist in the repository: criteria-frozen, env-v1, replication-pass, tolerances-frozen (none of them is a figure tag).

## Drafts

The eleven draft files (audit copies; byte-identical to docs/ms13_figure_manifest.csv; copied from docs/ms13_journal_final_hashes.txt). The pre-check of 13v (scripts/ms13_check_hashes.py: 104 manifest rows, 0 problems) and the verifier (7 draft files per figure, 0 differ) were run on them.

| hash | draft | path |
|---|---|---|
| b91e37c680e7c959774351befe4042d9d077721876b7d5d88cf01a9959bd65c1 | F1 | figures/F1/F1.pdf |
| 47ff902522dc4959cc57e14346d4f3ef061049dbcab04eb136bc0fa7d19436c0 | F1 | figures/F1/F1.png |
| 96dffcbbf22f6a2f9931ed9fd9360ee6f449eafb90d5cc940b988cfcc60f5404 | F1 | figures/F1/F1_caption.txt |
| e2fdaa20513ea77a418a865187609908883f044e8284bd6eaad62fd6d63fa14f | F1 | figures/F1/F1_drawn_data_sha256.txt |
| c1cb5bb7a3deef294010657d8c45a156c1ce463d51767e8bb0e921da550de280 | F1 | figures/F1/F1_params.csv |
| 642525d81d6dab67e082a3a1f807d933eb8aeb20a79010a230a31ae3ebd52c5f | F1 | figures/F1/F1_provenance.json |
| 8f1d0a558222416cea2fdd40a76e162518dc28ec5c09cf75b05b951460c9aede | F1 | figures/F1/F1_nordlie.md |
| 6f516e77abcf4b55caec15c5fb7dbb616dbe11c172198422098072b8be05024b | F2 | figures/F2/F2.pdf |
| 15f88cf0f04405cffb94cce008d71931289e4231725bc3a18e01eebb7470d2d6 | F2 | figures/F2/F2.png |
| dee2106261ad49be9b38cc40db466167deeb3c62550d45c7370ac14507eaa881 | F2 | figures/F2/F2_caption.txt |
| dd931068bfe221f1e4cd63c5225c00bd029a21f106755d88bb69559bd9004fd9 | F2 | figures/F2/F2_drawn_data_sha256.txt |
| 6fb23b13d67d5b2f009c3d2b20ad05c28182c6e59f47e9eb1d63036b84e16071 | F2 | figures/F2/F2_params.csv |
| bc0fb5b0baca73af86929c81fd9b6426c816cd6994b25091dab2020e9431210e | F2 | figures/F2/F2_provenance.json |
| 1f2e14905366fdf534414da6c335c043cf479517a2bf79bc95e9f26c4cd32f30 | F2 | figures/F2/F2_nordlie.md |
| 11e8fe56c1d3e2d98e8903bf497a49b0993fda7a086e2f912d93be92c3c257c8 | F3 | figures/F3/F3.pdf |
| 9fadb56d6a964eba595e51078adc1199e3ab76c009a951c8921f8fd781e5210f | F3 | figures/F3/F3.png |
| d67a94c59afd73f148680c747769845f769508c6037b5dca69e83ed20af026fe | F3 | figures/F3/F3_caption.txt |
| 008d124776e0dc4cf314065e275e9f76751b81d1e0c415d180e50af73eae873e | F3 | figures/F3/F3_drawn_data_sha256.txt |
| 07ce5b3d97fcc82b92c0fb8597307e97db4bf5e8a3e04fcd3c2482f150670071 | F3 | figures/F3/F3_params.csv |
| 114fbde70f10fe70e82e0a2725f08b4b7c318f6d81afd121c7444da607d6ffbd | F3 | figures/F3/F3_provenance.json |
| 64ba1263a4cd2316d00159e5b71dac8c06aab43d11de79e23810ab320ddb4d21 | F3 | figures/F3/F3_nordlie.md |
| 67cecfe72a086866dbf9d5461d2d8a972982dc3bab1a5ff67ffb446704f1b64c | F4 | figures/F4/F4.pdf |
| 07faa00732abb086ba838bb001c16ac630218f189039e39ec937630ddb0d0a27 | F4 | figures/F4/F4.png |
| d09a71b4c5035366807cb4d794190676c3e596d4d59a572cb0dd8c278e871477 | F4 | figures/F4/F4_caption.txt |
| 235a0c700668a9bc3c6dfd6ecf8980b8ac7937372989606f0f1271246c95f119 | F4 | figures/F4/F4_drawn_data_sha256.txt |
| d2714f9af461821ee92b6e33fc09d2ae860fd72cfd74e38c5940410da24e61bf | F4 | figures/F4/F4_params.csv |
| 2726707f7dcef10603a978c2d06a615734eeaee99f62dc44c3e46df3e88ef25f | F4 | figures/F4/F4_provenance.json |
| bd65e3dab18780d5385bf5a73ccc430d8f281e574cc390930cdcea33b8f7a992 | F4 | figures/F4/F4_nordlie.md |
| eeb218600eb31217c2a71afa30a184d82c4282be8806169b0e0aafae0a985cd6 | F5 | figures/F5/F5.pdf |
| 3dc6b3593e8039ca0f4fb814fb79f127081d74ad568838d22971657639ef267d | F5 | figures/F5/F5.png |
| 7bce8ec64117f71f71fe9e6bbbf89e4b88edccf4b8039fcc7d97b3be132eab85 | F5 | figures/F5/F5_caption.txt |
| 6906ac2b03a40d018dc10e2f25b4035cf2f3e651b04da3f2780e372775f49844 | F5 | figures/F5/F5_drawn_data_sha256.txt |
| 05eb76d9207c4bfe822fd0bf2b345a81c6ffb07fde08590cd9f4f5b0e209acd0 | F5 | figures/F5/F5_params.csv |
| 933f9f30dcb030a8fb4d6bad3e0b1592c9266664ab7ce4ed192f8eaca4480887 | F5 | figures/F5/F5_provenance.json |
| 9fea24fc13e7dc8b732b8dcd7093f171e5401378abff7e28165b0aa5eb95d547 | F5 | figures/F5/F5_nordlie.md |
| 7bf71649ae4a3375e88db6bbaf956ddbaf71a96e24b5b660fd2829b9c393c49b | F6 | figures/F6/F6.pdf |
| c7d31b9ef76f2ef5610bec59a1c52f375c528775f9304abb08834dc11733e2be | F6 | figures/F6/F6.png |
| 383e0a26b1b96d094173c2b7c6d90241a9573a02cf870e51fe77b54dc8e762d4 | F6 | figures/F6/F6_caption.txt |
| 899bd54748ab22c298bce06080cf0e653c6b4f1eb7a32bc9838552204f7b8aff | F6 | figures/F6/F6_drawn_data_sha256.txt |
| 72503d9c900d45d34c1497e2a95921ccdcb819e6cd96880e475fc4626323d7ea | F6 | figures/F6/F6_params.csv |
| bf091fdb4f15e600ae4886da972a5beb560892c4298f73c07867eeae7e7b704c | F6 | figures/F6/F6_provenance.json |
| cd8e681b994783c96766b4e1b4403b2d81300628fe28800c0438f295b0f10db8 | F6 | figures/F6/F6_nordlie.md |
| 4181af4217a95363b38dc92960f879003a034c0c6f088a660051a4ac8c77cfa3 | FS1 | figures/FS1/FS1.pdf |
| 5748b81855a437254de1c6549685f0ba3e573e16a1970003ac96e3b9e8b354f8 | FS1 | figures/FS1/FS1.png |
| d9d2c442c478cad05d25afcd4338c8c70737e8af58bcf0079c2ce75070053132 | FS1 | figures/FS1/FS1_caption.txt |
| 5a18863fd2c4aca24c6874b79e534bf9531b482205d5267b285b46064af4d24c | FS1 | figures/FS1/FS1_drawn_data_sha256.txt |
| 45aaade944be4b544d6cc50170062b19220deca110db6a1cf5ad9828cec51101 | FS1 | figures/FS1/FS1_params.csv |
| eb46903d0d4291bbcf779bdbb75dedb0d190ef6788921dc0bf34a3c3bc21cae8 | FS1 | figures/FS1/FS1_provenance.json |
| 2febc02cfd7c1619f888e75893d8d59b2bad5e53f1efb0af7f0fd7a58ddbcd42 | FS1 | figures/FS1/FS1_nordlie.md |
| ac1e04c9545447dd2a16ca4903bf095b6f1e13e2966d81a6be46b7d96e637a63 | FS2 | figures/FS2/FS2.pdf |
| e0aa692017ec3a2501ac2781d9e3547880744e4698a16b4ea2707b40f607755a | FS2 | figures/FS2/FS2.png |
| 9187bdad708ab84416073aa95161511a125a60133e99e769a5da045a843eadeb | FS2 | figures/FS2/FS2_caption.txt |
| fd9fdaa47de498debb3b7518d2389333d7949296cbc8466f2b37337c03a3f36b | FS2 | figures/FS2/FS2_drawn_data_sha256.txt |
| c2a26474c24c6209bc77021160d5e0288c9ce9760e26bf804c1bddacea85eeca | FS2 | figures/FS2/FS2_params.csv |
| 2763b11c14f602f3c88c2f5ad43bd50683fadb915a1eb50190dc12b1d262b70d | FS2 | figures/FS2/FS2_provenance.json |
| 87fbcaf9d9768b6bf4a0efa628cb049b0d2c9fac339945fdef06bd00d2b9c6b2 | FS2 | figures/FS2/FS2_nordlie.md |
| b95940f6c0d12aa892d9c50bd65142d6e2ce41eb2621a566b9687e5b47bb9b6f | FS3 | figures/FS3/FS3.pdf |
| bb0d1450e5aeba6bab715e8513aa40cd49a36d35a91c1ab122b7b1f5c2682057 | FS3 | figures/FS3/FS3.png |
| 73bd205f5bda4cc2bf9497a410881bf172e103b0f86cba8eb3dff6c3b96264ce | FS3 | figures/FS3/FS3_caption.txt |
| b22afb515966a28bdcd8f79c568cd82a4248fadab76ac02930b027449ca87160 | FS3 | figures/FS3/FS3_drawn_data_sha256.txt |
| 074e5b44d11004ddc5feeea9a9358467c264c227f6b8f83e7dbf7c6da9e65fa3 | FS3 | figures/FS3/FS3_params.csv |
| e09e3968af82fad08f7df86e53d92a4252f300372bf4f8698398c23182f217f7 | FS3 | figures/FS3/FS3_provenance.json |
| 3ffbd92856bba8d66eae54d802e32e59d5364f6acd8fc326e3bb9a39173546f5 | FS3 | figures/FS3/FS3_nordlie.md |
| 68a53c1151563fd1ae2c1db68da85a92890f58efaf03f92b1d4d0a2cc030593e | FS4 | figures/FS4/FS4.pdf |
| 4c8d9852b970c20bda5ebc0cdfb69b4159cbd5c3e5dd55ee82e29f5152d1a3d0 | FS4 | figures/FS4/FS4.png |
| 4e2c6a5174b402c2b17e7058e41590543344e2d403a1d424ce4b7d7063968864 | FS4 | figures/FS4/FS4_caption.txt |
| b228797b1ef42443680ac82dbda6c6c182ce9a296db2e2845acbb120cd5e21d0 | FS4 | figures/FS4/FS4_drawn_data_sha256.txt |
| 945c0f6813c27c19b9361421a22c1cc9747b4420671897695b6dfce6744bb47a | FS4 | figures/FS4/FS4_params.csv |
| 773abc1fabf7bda9c0a373e5ce3d29c1f663bcf9916033c3d774d7a226a7fc4d | FS4 | figures/FS4/FS4_provenance.json |
| 756d0bebede587b7dc3efcef09ec3ff20185f3afa4b1208fbd382d5ba367b10b | FS4 | figures/FS4/FS4_nordlie.md |
| ec37d38463b962e034516638dbf88120910c33a9167e61908e8772882784a39c | FS5 | figures/FS5/FS5.pdf |
| 650b8171a7a85e559d50774a1be0456fa1e9719e7d8f5b14fef2d56cd700b5bd | FS5 | figures/FS5/FS5.png |
| 3de611c4a757613a1f591ad68a3de891cb91481d2fc2fb0b3e9dc5e28a823f20 | FS5 | figures/FS5/FS5_caption.txt |
| 9a394e29162eb039b5387fc7d066bab8bc05109102f200092b6d69eb0ac259ce | FS5 | figures/FS5/FS5_drawn_data_sha256.txt |
| 65a00ab74399e72bb2e792327beee85c365099c7368c62dd96cbdf425d4d9de9 | FS5 | figures/FS5/FS5_params.csv |
| d921027a01bbd0f7c9b126ec9157e4cc7ded09bc31c31326853abfb5ee760830 | FS5 | figures/FS5/FS5_provenance.json |
| 5d3f554fca3825ad5ef80c0ff57b22679679f46fba4f41c288b15ca9b056f570 | FS5 | figures/FS5/FS5_nordlie.md |

## What this evidence does not show

- The colour-vision check of the 13 final PNGs: MANUAL, the user's task; the verifier row reads MANUAL for every figure (R2).
- Muscle artifact cannot be ruled out as a source of the gamma-band signal: the study is a model, and nothing here tests that reading against recordings.
- Checklist status after the 13v re-check (docs/ms13_export_checklist.json, docs/ms13_13v_checklist_recheck.md): {'not re-verified': 79, 'passing': 243, 'MANUAL': 1}. Items marked 'not re-verified' were not proven again in 13v (a human look, a review record, or no item-specific check was found); their earlier passing status rests on the recorded evidence of the 13t steps only. G2b-fs1-test-point carries the unresolved STOP of DL-646.
- The 'name-matched tests' class of re-verified items is weaker than a verifier row: a test named for the ruling code passed, but whether it covers the whole claim of the item was not checked item by item.
- UNVERIFIED glosses and defaults remain as marked in the captions and the close items (for example item 57, the layout limits of the journal export, the PCJ figure rules, the colour-vision reading); none was sourced in 13v.
- The panel-by-panel image content was not looked at again in 13v (no figure was built or opened); the visual reviews of 13t are recorded in docs/ms13_13t*_review.md.
- The EPS extras differ between builds (item 55); they are not part of the hash list.
