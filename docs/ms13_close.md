# MS13 close (13v)

Written for: the owner and reviewer who close MS13, and the author of the paper's limitations section. It claims no more than docs/ms13_evidence_sheet.md shows. Rulings of this step: DL-703; results: DL-704 to DL-709 (and the end-of-step entry that follows them). The plan (Technical Plan v0.5, docs/plan.md) is read-only and was not edited. It names no required contents for an MS13 evidence sheet or close document (Table 11.1: MS13 "Figures F1-FS6 with provenance", done when "Each built from a clean tree and tagged"); the structure below follows the 13v prompt.

## Status against the plan's own "done when"

- Built from a clean tree: yes for the 13 journal figures (build commit 5e9057563c6c24fbac16b99000e547d08ef9a31a, every provenance record dirty = false, DL-701). One exception is recorded: the A4 record was written with git.dirty = true (provenance warning on F3, close item 2; the clean-tree rerun was identical).
- Tagged: NO. No fig-*-v tag exists (the tags are criteria-frozen, env-v1, replication-pass, tolerances-frozen). 13u makes them when the user says "tag".
- F1 to FS6: FS6 is NOT produced, by user ruling of 2026-11-09 (DL-716 X3, DL-720): the plan's FS6 row is conditional (Table 8.1, plan line 913: "Only if G2 or G3 triggers"; MS12 "only via G2 or G3", Table 11.1, line 1363), G2 and G3 were ruled not triggered (DL-133, DL-261, DL-271), and DL-421 and DL-435 (iv) already rule five supplementary figures. So the FS6 part is "conditional row not triggered, user-ruled", not a failed milestone (close item 22 closed; option 3, S14 only as robustness, not chosen).
- So MS13 is NOT done by the plan's own condition until the tags are made (13u); the FS6 part is settled by the ruling above. This document closes the evidence, not the milestone.

## (1) What MS13 produced

- 13 journal figures: F1, F2, F3, F4a, F4b, F5, F5c, F6, FS1, FS2, FS3, FS4, FS5. Two are splits of one draft figure made in the journal export only (F5 and F5c from the draft F5, ruling T1; F4a and F4b from the draft F4, ruling K2), a departure from the plan's single figures; the union of the arrays of each pair equals the draft's (verifier "arrays" row) and the drawn-data digest equals the draft's.
- Per figure: PNG and flattened TIFF at 600 dpi (main files), PDF (extra), a short and a full caption (F1 to F6 and FS1) or one caption (FS2 to FS5), alt text, a supplement sheet, the source-data CSV, a provenance record. EPS extras exist for some figures (close item 55 names F3, F5, F5c, FS1) and are not in the hash list.
- The eleven drafts (figures/F1 to F6, FS1 to FS5) are untouched, byte-identical to docs/ms13_figure_manifest.csv, and kept as audit copies; the journal files are the main versions.
- The final hash list: docs/ms13_journal_final_hashes.txt (full SHA-256 of every file above, the build commit, the drawn-data digests, the eleven draft files). In 13v only two lines of it changed: the FS5 caption and the FS5 supplement (DL-705, DL-706; the FS5 'not run' clause, wording only). The PNG, TIFF and PDF hashes of all 13 figures are unchanged.
- Documents: docs/ms13_evidence_sheet.md (13v), docs/ms13_13v_checklist_recheck.md (13v), docs/ms13_close_items.md (section L added in 13v), docs/ms13_export_checklist.json (re-checked in 13v), docs/ms13_13t_progress.md, the review and audit files of 13t, and the decision log (DL-419 onward for MS13).

## (2) Checks passed, and failures shown as failures

Passed (13v, committed build, read-only, no rebuild): scripts/ms13_verify_export.py exit 0, 0 FAIL, 13 MANUAL (colour vision), all other rows PASS for all 13 figures; scripts/ms13_independent_compare.py exit 0 (draft rows 561: 462 equal, 0 not equal, 0 unresolved, 99 without comparison; the journal and short caption rows of every figure: 0 not equal, 0 unresolved); scripts/ms13_check_hashes.py 104 manifest rows, 0 problems; the 13 figures' PNG, TIFF and PDF equal the final hash list. The checklist re-check (V4) is in docs/ms13_13v_checklist_recheck.md: 323 items; 115 re-verified by a verifier row, a comparison row or the hash check; 128 re-verified only through tests named for their ruling code (weaker); 1 MANUAL; 79 not re-verified (human looks and review records that cannot be re-run, and items with no item-specific check). The start-of-step fast suite passed (1546 passed, 24 deselected, 9 xfailed, DL-704); the end-of-step suite is logged after this file in the decision log.

Failures that the science produced, shown in the figures and captions as failures (none dropped; numbers as in the captions):

- RB1 FAIL (network against mean field): headline path at 10 s 0 of 3 seeds and at 120 s 0 of 3 seeds (3 of 3 needed); the 4 map cells at 30 s 1 of 4 (3 of 4 needed). F1, F5.
- RB2 FAIL: headline class kept in 7 of 10 noisy seeds (8 of 10 needed). F4b, F5.
- RB3(a) FAIL: onset prediction on the testable in-range runs, 0 of 6. F4a (also named in F1).
- RB3(b) FAIL: delay under a noise floor, classifier-onset reading; the stored table has no value or threshold; the drawn fact is that the classifier-onset delays tie at -1.5 at levels 0 and 1. F4a.
- RB6 solver FAIL: the two solvers disagree on the headline onset by 181 ms (1 ms allowed). F4a, FS4.
- RB6 network f_pk FAIL: the network peak frequency when the step is halved (value blank in the stored table; threshold < 0.02). F5, F5c.
- RB9(b) FAIL: spectral peak 49.0 Hz against cycle frequency 44.609 Hz, a difference of 4.391 Hz against 0.5 Hz (1/W). F3, FS5.
- G7 NOT PASSED (the negative-control gate; the stored row reads FAIL with value and threshold blank); the network run of the first negative control is in the surge class S+. F6, F1.
- D24 noisy subgrid FAILED: 97 of 225 cells agree (43.1 percent); 203 of 225 (90 percent) needed. F4b, F5.
- The sigma check FAIL (logged verdict NOT INSIDE): mean-field baseline std 0.039522 against the network range 0.037989 to 0.038920.

## (3) Close items (docs/ms13_close_items.md, sections A to L; items 1 to 43 stay listed there as collected in 13n to 13t-1g)

Accepted by the user on 2026-11-09 as disclosed limitations (DL-703):
- 44: the class S-sus of the F1 network seeds has no recorded reason in the stored results; the traces look like the mean field; the paper must say so (cause UNVERIFIED; DL-709 gives where it was looked for).
- 45: the full captions (supplement) carry what the short captions leave out.
- 46: the journal F2 captions follow the data; the draft F2 stays as an audit copy.
- 48: the F5c control durations are in the source data; the draft stays.

Not accepted, still open:
- 49: triage table B of the 13t-10 review left as triaged.
- 50: the F4b legend says "Dotted line in (d): 1 s" only; the scope is in the captions and alt text.
- 51: the F5 and F5c alt texts write N as 1e3, 3e3, 1e4, 3e4.
- 52: the F4b short caption is at 650 of 650 words.
- 53: answered in 13v: the stored table has 71 "not run" records, all in the mean-field group S4 devalle (variant window x2) and none among the 390 cells of FS5 (a); the (a) clause of the FS5 caption was wrong and is corrected (wording only); the user still reads and accepts it.
- 54: G2b-fs1-test-point (DL-646): ruled 2026-11-09 (DL-716 X1): panel (c) is the stable focus at input 0 (52.82 Hz, 1.71 cycles per e-fold), panel (d) the focus after the step to 3 (91.77 Hz, 3.96); the FS1 captions now say so, with every number read from the stored arrays and the FS1 short-caption limit raised from 600 to 650 words; applied in the 13x build (DL-717 to DL-719 and the result entry; the final state is in docs/ms13_close_items.md section N).
- 55: the EPS extras differ between builds (probably embedded dates).
- 56: the colour-vision check is MANUAL.
- 57: the reading of the duration floor ("1 s or more for ramps of 60 s or more"; "down to 0.30 s") is UNVERIFIED.

## (4) The user's tasks still open

1. The colour-vision check of the 13 final PNGs with an online simulator (MANUAL; verifier row cvd).
2. A backup folder path for figures/ and the repository (figures/ and results/ are git-ignored outputs; the repo alone cannot restore the figure files). Not given yet.
3. The tag decision: whether to say "tag"; which of F5 and F5c, F4a and F4b get which tag; journal files as main versions, drafts as audit copies.
4. A human check of the figures and captions by someone who has not seen the project.
5. The zipped form of the F1 source-data CSV (28 MB as written) for the Zenodo record, later.
6. Rulings on the open close items 49 to 57, above all 54 (FS1 caption) and 53 (read the corrected FS5 caption).
7. The venue: Peer Community Journal, by user ruling of 2026-11-09 (DL-716 X4, DL-720); MNA is dropped (see section 5).

## (5) What the next steps need

- 13u (tags, only when the user says "tag"): re-run scripts/ms13_check_hashes.py and scripts/ms13_verify_export.py on a clean tree; tag from a commit whose recorded build equals docs/ms13_journal_final_hashes.txt (the build commit 5e90575 is the commit of record; later commits are documentation, the audit module, and in 13v the FS5 clause fix); do not rebuild before tagging. Note for 13u: the FS5 caption and supplement were corrected after the recorded build by a text edit (scripts/ms13_13v_fs5_caption_fix.py), and jfs5.py now writes the same clause; the FS5 provenance record still names the older build code. Whether a fresh FS5 build from the tagged commit gives these same bytes was NOT run (UNVERIFIED); that needs a ruling before tagging.
- MS14 (novelty re-check, plan Table 11.1): Scholar including cited-by checks on Xu 2023 and Borjigin 2013, PubMed, three slow-passage searches, the Kalia journal version, eLife RP 104249, PMC12549018; done when docs/search_log.md is complete. Not started.
- MS15 (reproducibility release and manuscript checklist). Sourced in the plan: D37 (MIT licence, release archived with a persistent identifier, service chosen at MS15); checklist 10.8 on a clean machine; the manuscript checklist after Table 11.2 (contribution sentence, assumptions and limitations, Nordlie parameter tables with the parameter regime and take-home in each caption, archived code with version, failure regimes reported next to surge regimes, no causal or clinical claims, conflicts of interest and AI-use disclosure). VENUE (ruled 2026-11-09, DL-716 X4, DL-720): Peer Community Journal after a Peer Community In recommendation (R1, DL-554); MNA is dropped. The decision log supersedes the plan's checklist lines about the MNA site, an arXiv identifier, an MNA account and the MNA LaTeX template (plan lines 1398 to 1402; the plan is not edited). MS15 follows the PCJ template and figure rules. Everything below is UNVERIFIED because the repo does not source it: the Peer Community Journal template and figure rules (R1 records only that PCJ prefers jpg, tiff or png and states no resolution, size or colour rule), a versioned DOI repository, the rule "no AI-generated illustrations", the Zenodo limits of 100 files and 50 GB per record, and "confirm the PCI section". The AI-use disclosure and CC-BY 4.0 are in the plan's checklist (R7 8(d), R6 6 and 8(d)).

## What this does not show

See the last section of docs/ms13_evidence_sheet.md: the colour-vision check is not done; muscle artifact cannot be ruled out; items marked not re-verified were not proven again; UNVERIFIED glosses remain as marked.
