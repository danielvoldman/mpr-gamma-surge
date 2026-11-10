# Items the MS13 close document must state (13n, DL-493)

LIST ONLY. Collected from the decision log from DL-419 onward and from docs/ms13_plan.md; nothing is decided here. A DL number is the entry that holds the ruling or fact; "(not re-read)" marks a number taken from an entry heading or a grep in 13n without re-reading its full text.

## A. Rulings and departures the close must state

1. DL-436 supersedes the PENDING colour-blind text of docs/ms13_conventions.md sections 2 and 11; that file is not edited and keeps its pinned hash (DL-442).
2. The A4 record was written with git.dirty = true: provenance warning on F3 (DL-450; origin DL-124, clean-tree rerun identical).
3. FS5 reads two tracked files under tests/ as text (departure from "scripts read only results/"), under the conditions of DL-477 ruling (6); SHA-256 of both files is in the FS5 provenance (DL-476, DL-477).
4. F5c exception to "tables first": per-seed metric points recomputed from the 52 stored S9 and S9_ctrl series with the frozen classifier, all equal to the stored values (DL-490 ruling 2; accepted DL-492).
5. The spectrogram-computation reading of the script rule (F1 panels g and h computed from stored v with the frozen routine) and the 1300-block min-max decimation rule stay UNVERIFIED (DL-486, DL-488 ruling 5).
6. FS4 reading of Table 8.1 "Any RB6 failure -> affected results unused" (DL-429).
7. FS5 inputs assumption: A8 plus A6 plus the A11 RB9 rows; no A6 element drawn (DL-430, DL-477 ruling 5).
8. Scripts that read config JSON of run records (F4 epsilon and other config values read from stored records, not retyped; F4 entries DL-483, DL-484; not re-read in 13n).
9. Claim-limit label table docs/claim_limit_labels.md (DL-477; G6-D1 and DL-163-D3 added DL-485): 32 labels, of which three exist only in the plan (RB2 FAIL, D24 failed, G7 not passed) and are written in plain words; RB1 FAIL, RB6 FAIL, RB9(b) FAIL and MS9(e)-7 and -8 have no entry.
10. Erratum entries for logged text that disagreed with stored arrays: DL-459, DL-462, DL-463.
11. Logged rulings of 13n: F5 accepted as a draft; the F5 take-home, claim limits and strip rows (DL-491) accepted as drafts; display choices accepted (DL-492).

## B. Draft status

12. Every figure is an untagged draft until the user says "tag <ID>" (DL-422, DL-431, DL-492). Latest result entries: F3 DL-466; F2 DL-467; FS1 and FS2 DL-473; FS5 and FS4 DL-476 (rebuilds DL-478); FS3 and F6 DL-481 (housekeeping rebuilds DL-484); F4 DL-484, label-table rebuild DL-487; F1 DL-487, rebuilt DL-489; F5 DL-491. The take-home, claim limits and strip of each are PROPOSED unless a later ruling accepted them.
13. PENDING CHANGES for the polish step (DL-492 ruling 6): F5 caption states MS9(e)-3 and MS9(e)-4 not applicable; F5 take-home also covers map 2 (296 of 325 D-tr); the F1 model schematic.

## C. UNVERIFIED design choices (every figure)

14. Layout, colours, marks, symbol sizes, font (DejaVu Sans 8 pt, PNG 200 dpi placeholders, DL-435), style.py scalar tables (F1_SIZES, F5_COLOURS, F5_STATE_MARKS and others), draft banners.
15. Strip readings: F2 and FS3 list RB1 rows because the figure draws network or S9 records (DL-460, DL-482); FS1 and FS2 have no RB row; F6 has the G7 gate row only and RB7 has no A11 row; F5 includes RB2 headline_class_kept_1.0_sigma (UNVERIFIED, DL-491, DL-492); F4 and F1 have explicit strips.
16. G4-C2 placement on F2 and the F3 G6-D1 arrow reading (DL-455, DL-457; UNVERIFIED).
17. The 118-of-225 count on the three Table 2.1 categories (our reading, DL-491, accepted DL-492).
18. T_ramp 30 s network cells shown against the 120 s map without an equivalence claim (DL-490 ruling 3).
19. Hopf-marker interpolation and the derived Delta_end of P4a and P4b (F2 and F3 captions).

## D. Gaps against Table 8.1

20. F1: no model schematic (proposal in docs/ms13_f1_schematic_proposal.md).
21. F3: (eta, Delta) frequency shading absent, A6 stores no Delta slices; Hopf curve only (DL-451). J plane, J ramp of P2 and P3, sigmoid and start-distance variants not drawn.
22. FS6 not produced (MS12 not run, MS12-C1; DL-421, DL-435).
23. F4: A2 ring map not drawn, panels k and l use the A3 table (DL-483, not re-read).
24. F5: no S7 series and no A9 failure labels on the maps (labels are on F6); per-seed subgrid class counts not drawn; no network symbols on map 2; control durations not evaluated (DL-491).
25. FS3: RB8 heterogeneity NOT EVALUABLE; other S10 control records not identifiable (DL-479).
26. FS5: no A6 frequency map drawn (DL-477).
27. F1: panels g and h are not stored but computed (see item 5); seeds 1 and 2 are not in the raster or the network spectrogram (DL-488).

## E. Found by the 13n audit (docs/ms13_audit.md; reported, not fixed)

28. Build-code drift: src/mprsurge/plotting/figures.py and style.py (and captions.py for F2, F3, FS1, FS2) differ from the hashes in the provenance of ten figures; the recorded figures are as built, the code has moved on (informational).
29. Literal hex colours, markers or sizes in the drawing code of F2, F3, FS1, FS2, FS4, FS5 (F1, F4, F5, F6, FS3 have none); the rule is none.
30. The "Claim limits:" sentence prints IDs only in F2, F3, FS1, FS2 and ID, short form and DL numbers in the others.
31. The F3 caption names F3_nordlie.md (its test requires it); the other captions forbid the file prefix.
32. The module docstring of src/mprsurge/plotting/figures.py still says only make_F3, make_F2 and make_FS6 exist.
33. Captions carry a full Parameters dump (F1 caption 9,733 characters, about 60 percent repeated per-seed keys).
34. Tools: scripts/ms13_check_hashes.py with docs/ms13_figure_manifest.csv replaces ad hoc hashing; scripts/ms13_audit.py regenerates docs/ms13_audit.md; scripts/ms13_contact_sheets.py writes the git-ignored figures/_review/.

## F. Added in 13r (DL-511, DL-512)

35. F4 (j) and FS4: the 84 classifier-onset delays of -1.5 are onsets at the ramp start (onset_s = t_on_s = 5.0 s; delay = eta_start - eta_H = -1.5). Statement on the figures: "classifier onset at or before the ramp start; the eta-based delay equals its minimum eta_start - eta_H (-1.5); the classifier-onset reading is saturated at these levels". No gate verdict changes (D2, DL-511).

36. F4 caption (and any caption that lists the params of the floor runs): the D43 floor sigma 1.59e-09 is printed in the stored params format (value_text, the params.csv cell text), a small departure from the G9 number format; accepted (DL-529 (b)). No positive-exponent style such as 1e+03 may appear on a figure or in a caption.
37. Shared style: the P4b colour is now olive (#8a8f1c, was teal #3f9f96), so that P4b differs in hue from P3; one colour per path in every figure at its next build (DL-532).
38. F6 and the NC1 mode-N rows: the supplementary S-rel counts (1 of 10 at T_ramp 10, 177.8, 316.2 and 562.3 s, 2 of 10 at 1000 s; 6 of 130) are "not counted for G7 per DL-220 (4)" (supplementary, feeds no gate); S-rel is a surge class by Table 2.1, so this reading of G7 is UNVERIFIED.
39. F4 (a): the coincidences of stored raw-crossing values are pairs computed from the stored arrays (P1 linear = P5 linear at 11 of 13 T_ramp, P1 sigmoid = P5 sigmoid at 11, P1 linear = P1 sigmoid at 2); the 13r-3b prompt named a P1 linear, P1 sigmoid and P5 linear group, which the stored values do not form (DL-525).

## G. Added in 13t-1b (DL-554)

40. F1 draft (figures/F1/F1.png, F1.pdf, caption): the label "raw crossings: 3 seeds coincide" and the caption sentence "a note says that the 3 seeds coincide" disagree with the stored raw first crossings (50.170, 50.924 and 50.857 s, span 0.754 s; only the three classifier onsets, 12.000 s, are equal). The drafts are left unchanged by ruling (R6); the same correction ("overlap at this scale: stored values 50.170 to 50.924 s") is to be made in the draft label and caption at the next rebuild of the drafts. The journal text already carries it.

## H. Added in 13t-1c (DL-563)

41. F5 (f) to (i): seed marks 2.5 pt (ramp) and 2.2 pt (control), neighbouring marks touch; (c), (d) state marks (4.2 pt) larger than their 3.0 pt cells; stopped under S14, the allow-list entries are PROVISIONAL until the user rules (DL-565, DL-568).
42. The journal captions are in plain words with the ruled text paired in the supplement (DL-565); the Parameters line keeps the stored key names.
43. Stored FAIL rows sigma_check S8_baseline_std (NOT INSIDE) and RB3 a_inrange_runs (0 of 6) are named in no F1, F3 or F5 caption (strip membership not changed without a ruling; DL-567).

44. FOR THE USER (13t-1e, DL-583 U7, DL-586): F1 (d), (f): stored class S-sus, reviewer reading of an ending episode near 143 s, reason not shown by stored fields. The stored classifier output of the three network seeds (results/ms10/eval/ms10_eval.json, rb1_headline 120 s) holds the class (S-sus), the classifier onset (12.0 s), the raw first crossing (50.170, 50.857, 50.924 s) and f_pk; it holds no termination flag or time, no power-test result and no onset reason. The class, the wording 'no claim is made about the visual shape' and the figures are unchanged; the classifier was not recomputed.
45. FOR THE USER (13t-1e, DL-584): the plan (section 8 conventions; MS15 checklist) asks for 'full parameters and spectrogram settings in each caption' and for every caption to state the parameter regime and the take-home message; the SHORT journal caption (DL-582 U3) cannot hold the full parameters and settings, which are in the FULL caption and the supplement. The plan does not require the full claim limits inside the figure caption. Needs a ruling whether the short caption alone meets the plan's caption convention.

## I. Added in 13t-4 (DL-636)

46. FOR THE USER (13t-4, DL-636 E1): draft F2 take-home disagrees with its drawn data; journal caption follows the data; the draft stays. The ruled draft constant F2_TAKE_HOME (DL-128, DL-129) says the network sweep 'does not follow the mean-field branch closely'; the recorded relative differences of the v amplitude above eta_bar 3.0 are +13.2 and +12.4 percent at eta_bar 3.296, about 7 percent at 3.696, at most 4.8 percent from 4.096 up and -2.5 percent at 6.496, and (a) and (b) show the network symbols on the mean-field branch. The journal captions (short and full) read 'Above the Hopf point the network amplitude lies close to the mean-field branch in (a) and (b) and differs from it by up to 13.2 percent in (c)'; the draft figure, caption and constant are byte-identical to before.
47. REPLACED (13t-5, DL-645 G1): the ruled F3 band-end clause is written from the stored A6 arrays (key eta_tau_D<Delta>_param_last): each band ends at the last recorded eta_bar of its cycle branch; 8 of the 27 bands end before 8.0 (listed in the F3 captions and supplement); the REASON the bands end is not recorded (open note in docs/ms13_13t5_notes.md).

## J. Added in 13t-8 (DL-668)

48. FOR THE USER (13t-8, DL-668 K3): F5c (d): draft omits control durations although the records hold 9 of 12; the draft says they were not evaluated; reconcile before the paper cites it. (The 12 control records hold duration_s for 9 of 12; the evaluation fields duration_ms are NaN for all controls; the journal figure draws what the draft draws, and its captions say that no control seed is drawn in (d).)

## K. Open for the user at the end of 13t (13t-11, DL-699 to DL-702)

Items 44, 45, 46 and 48 stay open, text as above (repeated here word for word):

44. FOR THE USER (13t-1e, DL-583 U7, DL-586): F1 (d), (f): stored class S-sus, reviewer reading of an ending episode near 143 s, reason not shown by stored fields. The stored classifier output of the three network seeds (results/ms10/eval/ms10_eval.json, rb1_headline 120 s) holds the class (S-sus), the classifier onset (12.0 s), the raw first crossing (50.170, 50.857, 50.924 s) and f_pk; it holds no termination flag or time, no power-test result and no onset reason. The class, the wording 'no claim is made about the visual shape' and the figures are unchanged; the classifier was not recomputed.

45. FOR THE USER (13t-1e, DL-584): the plan (section 8 conventions; MS15 checklist) asks for 'full parameters and spectrogram settings in each caption' and for every caption to state the parameter regime and the take-home message; the SHORT journal caption (DL-582 U3) cannot hold the full parameters and settings, which are in the FULL caption and the supplement. The plan does not require the full claim limits inside the figure caption. Needs a ruling whether the short caption alone meets the plan's caption convention.

46. FOR THE USER (13t-4, DL-636 E1): draft F2 take-home disagrees with its drawn data; journal caption follows the data; the draft stays. The ruled draft constant F2_TAKE_HOME (DL-128, DL-129) says the network sweep 'does not follow the mean-field branch closely'; the recorded relative differences of the v amplitude above eta_bar 3.0 are +13.2 and +12.4 percent at eta_bar 3.296, about 7 percent at 3.696, at most 4.8 percent from 4.096 up and -2.5 percent at 6.496, and (a) and (b) show the network symbols on the mean-field branch. The journal captions (short and full) read 'Above the Hopf point the network amplitude lies close to the mean-field branch in (a) and (b) and differs from it by up to 13.2 percent in (c)'; the draft figure, caption and constant are byte-identical to before.

48. FOR THE USER (13t-8, DL-668 K3): F5c (d): draft omits control durations although the records hold 9 of 12; the draft says they were not evaluated; reconcile before the paper cites it. (The 12 control records hold duration_s for 9 of 12; the evaluation fields duration_ms are NaN for all controls; the journal figure draws what the draft draws, and its captions say that no control seed is drawn in (d).)

New items (one line each):

49. FOR THE USER (13t-10, 13t-11): the triage of the 13t-10 review (docs/ms13_13t10_triage.md table B: wording, clarity, jargon, density, design) is left as triaged; no rebuild was made for it.
50. FOR THE USER (13t-11 R2): the F4b legend says 'Dotted line in (d): 1 s' only; the scope (1 s or more for ramp durations of 60 s or more; some faster ramps down to 0.30 s) is in the captions and the alt text, because the longer legend ran past the key edge (attempt 2 of 2).
51. FOR THE USER (13t-11): the alt texts of F5 and F5c write N as 1e3, 3e3, 1e4, 3e4; captions and images use 1000, 3000, 10,000, 30,000 (V4, W3); not changed.
52. FOR THE USER (13t-11): the F4b short caption has 650 of 650 words; any further clause needs a ruled change of the limit or the removal of other prose.
53. FOR THE USER (13t-10 triage, FS5 (a)): the caption mentions 'not run' cells but no mark or legend entry for them in (a); whether any cell of the stored table is 'not run' was not established; not changed.
54. FOR THE USER (13t-5, DL-646): checklist item G2b-fs1-test-point records a read-only check that STOPPED with nothing patched; it was set passing only by the 13t-11 ruling P5 and is not resolved.
55. FOR THE USER: the EPS extras of F3, F5, F5c and FS1 differed between the 13t-10 and 13t-11 builds although the code of those figures did not change (probably embedded dates; not the main files; PNG, TIFF and PDF are byte-identical across builds).
56. FOR THE USER (R2): the colour-vision check of the 13 final PNGs is MANUAL (online simulator); the verifier row cvd reads MANUAL.
57. UNVERIFIED (13t-11): 'durations are 1 s or more for ramp durations of 60 s or more' rests on the frozen window rule T_ramp >= 60 s and the stored durations (minimum exactly 1.0 s there); the plan gives no sentence on the pinned medians; the claim 'some faster ramps down to 0.30 s' is the stored minimum, not a limit of the classifier.

## L. Status at the end of 13v (user rulings of 2026-11-09, DL-703; results DL-705 to DL-707)

ACCEPTED BY THE USER as disclosed limitations (2026-11-09; nothing in results, frozen criteria or drafts is changed for them):

44. ACCEPTED (V1, V2). The class S-sus of the F1 network seeds has no recorded reason in the stored results; the traces look like the mean field; the paper must say so. Cause: UNVERIFIED. Where the read-only look was made (one pass): docs/decision_log.md (DL-583 at line 6263 and DL-586 at line 6291 list the stored fields; no other entry gives a reason for the three seeds); results/ms10/eval/ms10_eval.json, key rb1_headline, 120.0, seeds (fields class, onset_s, onset_raw_s, f_pk_hz, onset_ok, class_match and the margins; no termination flag or time, no power-test result, no onset reason); docs/ms10_results.md lines 33 to 35 and docs/ms10_g_evidence.md line 13 (class, onsets, f_pk only); configs/ms10/ms10_eval.yaml; configs/robustness_criteria.yaml line 127 (rule O10: "S-sus if any is unterminated") and docs/plan.md line 260 (Table 2.1: S-sus = no termination, either power test). The last two are the DEFINITION of the class, not a record for these seeds: they say what S-sus means, not why the classifier gave it to these three runs. No class, result or draft was changed and the classifier was not run again.
45. ACCEPTED (V1). The full captions (supplement) carry what the short captions leave out (full parameters, spectrogram settings, every failed check, the claim limits).
46. ACCEPTED (V1). The journal F2 captions follow the data (ruling E1); the draft F2 stays unchanged as an audit copy.
48. ACCEPTED (V1). The control durations are in the source data (9 of 12 control records hold duration_s); the F5c draft stays as it is.

NOT ACCEPTED, STILL OPEN (one line each; "settles it" = what would close the item):

49. OPEN. The triage of the 13t-10 review (docs/ms13_13t10_triage.md table B: wording, clarity, jargon, density, design) was left as triaged, no rebuild. Settles it: the user reads table B and accepts it, or rules which rows are fixed in a rebuild.
50. OPEN. F4b legend says "Dotted line in (d): 1 s" only; the scope (1 s or more for ramps of 60 s or more; some faster ramps down to 0.30 s) is in the captions and the alt text. Settles it: the user accepts the shorter legend, or rules a wider legend / another layout (one rebuild of F4b).
51. OPEN. The alt texts of F5 and F5c write N as 1e3, 3e3, 1e4, 3e4; captions and images write 1000, 3000, 10,000, 30,000. Settles it: a ruling to accept, or an alt-text edit and a new hash list.
52. OPEN. The F4b short caption has 650 of 650 words. Settles it: a ruled higher limit, or ruled removal of other prose, before any further clause.
53. OPEN, ANSWERED IN 13v (V3, DL-705, DL-706). Result: the stored table (results/A8/a8_sensitivity.csv) holds 71 "not run" records, all in the stored mean-field group S4 devalle (mode D), variant window x2; the synthetic cases of FS5 (a) hold 0 of 390. Panel (a) therefore has no such cell and needs no mark; panel (c) marks the 71 with an asterisk. The wrong clause of the (a) sentence of the FS5 caption (and of its copy in the FS5 supplement) is corrected, wording only; the image is unchanged. Settles it: the user reads the corrected FS5 caption and accepts it.
54. OPEN, NOT RESOLVED. Checklist item G2b-fs1-test-point (DL-646): the read-only check STOPPED, nothing was patched, no later entry settles it (see docs/ms13_13v_checklist_recheck.md). Settles it: a ruling on whether the FS1 caption must say that (d) is the response after the input step to I = 3 while the decay read in (c) is at the node as stored (52.82 Hz, 1.710 cycles per e-fold against 91.77 Hz, 3.96 in (d), DL-646); the FS1 caption already says that (d) is a step from 0 to 3.
55. OPEN. The EPS extras of F3, F5, F5c and FS1 differed between the 13t-10 and 13t-11 builds (probably embedded dates; not the main files). Settles it: the user accepts that EPS is an extra with no fixed hash.
56. OPEN (MANUAL). The colour-vision check of the 13 final PNGs (online simulator) is the user's task; verifier row cvd reads MANUAL. Settles it: the user reports the result.
57. OPEN (UNVERIFIED). "Durations are 1 s or more for ramp durations of 60 s or more" rests on the frozen window rule T_ramp >= 60 s and the stored durations; the plan has no sentence on the pinned medians; "down to 0.30 s" is the stored minimum, not a classifier limit. Settles it: a ruling that the reading is accepted, or a source from the plan.

## M. State at the end of 13w (DL-712 to DL-715; details in docs/ms13_13w_notes.md; nothing here is a ruling)

- Item 22 (FS6 not produced): facts gathered for the owner's ruling (W3). The plan's FS6 row reads "Only if G2 or G3 triggers" (Table 8.1) and MS12 is "only via G2 or G3" (Table 11.1); G2 and G3 were ruled not triggered (DL-133, DL-261, DL-271); DL-421 and DL-435 (iv) already rule that FS6 is not produced and that there are five supplementary figures; M4 and M3a/M3b code, the S14 and S15 run lists, the M4 criteria (DL-157) and D42 do not exist yet. Options 1 (run MS12, later), 2 (drop FS6) and 3 (S14 as robustness only) with cost are in the notes. STILL OPEN: the owner rules.
- Item 54 (FS1 test point): answered in plain words (W2). Panel (c) is the stable focus at input current I = 0 (r = 1.0306; 52.82 Hz, 1.710 cycles per e-fold); panel (d) is the response after the step to I = 3 and its linearisation at the post-step focus (r = 1.3732; 91.77 Hz, 3.96); these are two different foci, not two values of one quantity (outcome b). The captions say that (c) and (d) are drawn at different parameter values and that (d) steps from 0 to 3, but not what follows from it. Wording is proposed in the notes and NOT applied. STILL OPEN: the owner rules on the wording (a new FS1 caption hash and a word-limit question follow if applied).
- G2b-fs1-test-point: stays "not re-verified" in docs/ms13_export_checklist.json and docs/ms13_13v_checklist_recheck.md (not edited); the explanation above is read from src/mprsurge/analysis/ring.py line 208 and the A2 and S1 run records.
- Also found in W2 (new, not changed): the alt text of FS1 (b) says the test point "is on the grey boundary"; the stored map has a focus at the test point and at every node of the 7 by 7 block around it, and the nearest node without a focus is 8.6 grid steps away.
- Venue (W4): the plan's checklist (MNA, arXiv identifier, CC-BY 4.0, ORCID; plan lines 1398 to 1402) and ruling R1 (DL-554, Peer Community Journal) disagree; no entry reconciles them. STILL OPEN: the owner confirms the venue.
- FS5 reproducibility (W1, DL-714): a fresh build from the committed code gives the same FS5 PNG, TIFF, PDF, caption, alt text, source data and drawn-data digest as docs/ms13_journal_final_hashes.txt; the supplement differs only in the build-commit hash and the provenance-file hash. This closes the "not run" note of docs/ms13_close.md section 5 for 13u, except for the supplement reading.

## N. User rulings of 2026-11-09 applied in 13x (DL-716 to DL-720; nothing in results, frozen criteria, drafts or the plan changes)

- 22. CLOSED BY USER RULING (X3, DL-716, DL-720). FS6 is NOT produced. The plan's FS6 row reads "Only if G2 or G3 triggers" (Table 8.1, plan line 913) and MS12 is "only via G2 or G3" (Table 11.1, line 1363); G2 and G3 were ruled not triggered (DL-133, DL-261, DL-271); DL-421 and DL-435 (iv) already rule that MS12, S14, S15 and FS6 are not produced and that there are five supplementary figures. This is the plan's conditional row not firing, not a failed milestone. Not chosen: option 1 (run MS12 later) and option 3 (S14 only as robustness). The tags remain not done until 13u.
- 54. RULED AND APPLIED (X1, DL-716; code DL-717 to DL-719). The FS1 captions say that panel (c) is the stable focus at input 0 (52.82 Hz, 1.71 cycles per e-fold at the test point) and that panel (d) is the focus after the step to 3 (91.77 Hz, 3.96), with every number read from results/A2/a2_ring_map.npz at build time; the FS1 short-caption word limit is 650 (was 600). The FS1 (b) alt text no longer says "on the grey boundary" (X2: the test point lies on the coloured side; the nearest grid node without a focus is 5 grid steps lower in eta_bar/Delta and 7 lower in J/sqrt(Delta); image and stored map agree). The checklist item G2b-fs1-test-point in docs/ms13_export_checklist.json is NOT edited. The new FS1 hashes are in docs/ms13_journal_final_hashes.txt after the 13x build.
- Venue. RULED (X4, DL-716, DL-720): Peer Community Journal; MNA is dropped. The decision log supersedes the plan's checklist lines about MNA, an arXiv identifier and an MNA account (plan lines 1398 to 1402; ruling R1, DL-554 stands). UNVERIFIED until sourced: the PCJ template and figure rules, a versioned DOI repository, CC-BY, no AI-generated illustrations, the Zenodo limits (100 files and 50 GB per record), the AI-use disclosure, "confirm the PCI section".
- 53. STILL OPEN (X5, DL-716): the owner accepts the reading that the FS5 supplement differs from a fresh build only in the build-commit line and the provenance-file hash (DL-714); the owner still has to read the corrected FS5 caption.
- 49, 50, 51, 52, 55, 56, 57 stay open as in section L.

## O. Tag-time state (13u, DL-723 to DL-725; nothing here is a ruling about an item, nothing is closed)

- The user said "tag" (2026-11-09, DL-723 T1): 13 annotated local tags fig-<ID>-v1, one per journal figure (F1, F2, F3, F4a, F4b, F5, F5c, F6, FS1 to FS5), all at the one final commit of 13u; drafts are audit copies and are not tagged; venue Peer Community Journal. This file was committed before the tags were created (`git tag -l 'fig-*'` and `python scripts/ms13_make_tags.py --verify` show the result).
- Finding (DL-723): figures/ is git-ignored, so the figure files are not in a tagged tree; the tag message and docs/ms13_journal_final_hashes.txt carry their SHA-256. The figure files exist only on this machine until the user backs them up.
- OPEN AT TAG TIME (a later fix gets a new tag version v2; the v1 tag stays): 49 (triage table B left as triaged); 50 (F4b legend scope); 51 (alt texts of F5 and F5c write N as 1e3, 3e3, 1e4, 3e4); 52 (F4b short caption at 650 of 650 words); 53 (the user still reads the corrected FS5 caption and accepts the DL-714 reading); 55 (EPS extras differ between builds); 56 (colour-vision check, MANUAL); 57 (duration-floor reading, UNVERIFIED). None of their texts says it must be fixed before tagging.
- Settled: 22 (FS6 not produced, DL-716 X3), 54 (FS1 wording, DL-716 X1, applied in 13x); 44, 45, 46, 48 accepted as disclosed limitations (DL-703).
- Checklist item G2b-fs1-test-point: status "not re-verified" unchanged; key recheck_13x points to the 13x evidence (DL-723 T5).

## P. Sub-step 14 (2026-11-10; DL-727; results in the entry after it; user reports and one read-only search; nothing in results, frozen criteria, drafts, figures, the plan or any tag changes; sections L, N and O above are kept as they were and are superseded only where this section says so)

- Y1 (tag result of 13u, DL-727): the 13 annotated local tags fig-<ID>-v1 exist, all at e6666cb2e8120a1619527c5ee7fce01e1beedb55; re-checked from git (tag type, target, hash list read from each tag's tree, no path under figures/ in any tagged tree, `--verify` 13 of 13; once HEAD has moved on, run it with `--target e6666cb2e8120a1619527c5ee7fce01e1beedb55`, DL-729); details in docs/ms13_close.md section (6). The figure files are not in the tagged trees; they exist only on the user's machine until backed up and until the Zenodo record (MS15).
- 56. CLOSED BY USER REPORT (Y2, DL-727; 2026-11-10, chat message). The manual colour-vision check on the pilot sheet was done by the user and is fine. Evidence: the user's statement only, no file. UNVERIFIED: which figures and which tool were used; whether the check covered all 13 final PNGs (item 56 names the 13 final PNGs, the statement names the pilot sheet). The verifier row cvd still reads MANUAL; docs/ms13_export_checklist.json keeps the status MANUAL on R2-cvd-manual-row and carries the note key user_report_14.
- F2 right margin (Y3, DL-727): CLOSED NON-FINDING. An outside AI claimed that the right margin of the F2 journal figure is clipped or double-rendered. The user looked at F2 at full size on 2026-11-10 and found it fine; the verifier (margins at least 0.10 in, no unlisted collisions; scripts/ms13_verify_export.py exit 0, DL-726) does not support the claim. F2 is not changed.
- MS14 novelty check (Y4, DL-727): user report only (2026-11-10, chat message): the check was done by the user outside Claude Code and the novelty claims are fine. What was searched, where, when and what was found are NOT stored (UNVERIFIED). The plan passages on MS14 are quoted word for word, with a reading of whether such a report meets the plan's "done when" ("docs/search_log.md complete"), in docs/ms13_close.md section (7). MS14 is not closed; that is the user's decision.
- Word search "delineate" (Y6, DL-727): NO HIT for "delineate", "delineated", "non-delineate" or "non-delineated" (searched before this step's own documents were written) in any tracked file, any text file of figures/ or results/, the plan or the decision log; the F6 panel (a) title on the image reads "Failure labels of the 169 non-surge cells". So docs/ms13_v2_wording_list.md is not written and nothing is proposed for a v2 tag. Details in the entry after DL-727.

OPEN after sub-step 14 (the user has not ruled on them; none is closed by this step):

49. OPEN. Triage table B of the 13t-10 review left as triaged (as in section L).
50. OPEN. The F4b legend says "Dotted line in (d): 1 s" only; the scope is in the captions and the alt text (as in section L).
51. OPEN. The alt texts of F5 and F5c write N as 1e3, 3e3, 1e4, 3e4 (as in section L).
52. OPEN. The F4b SHORT caption is at 650 of 650 words (limit short_max_words_F4b: 650 in configs/journal_export.yaml; the file figures/journal/F4b/F4b_journal_caption.txt has 650 words by `wc -w`). Any further clause needs a ruled higher limit or the removal of other prose.
53. OPEN. The user has still to read the corrected FS5 caption (DL-705, DL-706, DL-714).
55. OPEN. The EPS extras differ between builds (probably embedded dates; not the main files).
57. OPEN (UNVERIFIED). For the user, plain: the part "1 s or more for ramps of 60 s or more" is sourced (the frozen window rule T_ramp >= 60 s and the stored durations, as the item says; not re-derived in sub-step 14); only the side comment on the pinned medians has no plan source; recommended: accept.

SETTLED OR CLOSED: 22 (FS6 not produced, DL-716 X3); 54 (FS1 wording, DL-716 X1, applied in 13x); 56 (user report, above); 44, 45, 46, 48 accepted as disclosed limitations (DL-703).

Also open from docs/ms13_close.md section (4), not close items: a backup folder path for figures/ and the repository; a human check by someone who has not seen the project; the zipped F1 source-data CSV for Zenodo; pushing the tags; the MS14 decision above.

## Q. Sub-step 15 (2026-11-10; DL-730; docs/search_log.md written from the user's two reports; nothing in results, frozen criteria, drafts, figures, the plan or any tag changes; sections L to P above are kept as they were and are superseded only where this section says so)

- docs/ms14_user_reports_2026-11-10.md holds the user's two reports word for word; docs/search_log.md holds the log (plan Appendix E columns plus Date and Result; one row per action; a Taher 2022 row "not stated in the user's reports"; "G8 outcome: to be written by the user"). Both are user reports, not independently checked by Claude Code; paper titles, authors and DOIs are UNVERIFIED (DL-730 Z1).
- 58. [REPLACED in sub-step 16 by the user's ruling of 2026-11-10, DL-732 A3, see section R; text kept as written in sub-step 15] OPEN (new; MS14 gaps, DL-730 Z4). MS14 is NOT closed; whether docs/search_log.md meets the plan's "complete" is the user's decision. Gaps: the "About N results" numbers shown by Google Scholar are not recorded; the exact method of items 1 and 2 is user-reported and AI-tidied (the user did not go through the numbers 0, 0, 3, 4 one by one with the notes); the three slow-passage searches have query text only (no tool, date or result); the Taher 2022 full-text reading (plan line 1467, C20) is not stated and not marked done; paper details UNVERIFIED; the handwritten notes are not in the repository (option: the user photographs them and has them added later as docs/ms14_handwritten_notes.jpg; not created); the user's G8 outcome is not written; the query texts of report 1 equal rows of the plan's Table E.1 (RA, October 2026), and whether report 1 is new work of 2026-11-10 or a restatement of that log is not shown by the repository (UNVERIFIED). Settles it: the user rules that the log is complete as it stands (logged as a ruling), or supplies the missing items, or rules that MS14 stays open.

OPEN after sub-step 15 (the user has not ruled on them; none is closed by this step):

49. OPEN. Triage table B of the 13t-10 review left as triaged (as in section L).
50. OPEN. The F4b legend says "Dotted line in (d): 1 s" only (as in section L).
51. OPEN. The alt texts of F5 and F5c write N as 1e3, 3e3, 1e4, 3e4 (as in section L).
52. OPEN. The F4b SHORT caption is at 650 of 650 words (as in section P).
53. OPEN. The user has still to read the corrected FS5 caption (as in section P).
55. OPEN. The EPS extras differ between builds (as in section L).
57. OPEN (UNVERIFIED). The reading of the duration floor (as in section P; recommended: accept).
58. [REPLACED in sub-step 16, see section R] OPEN (new). The MS14 gaps above.

SETTLED OR CLOSED (unchanged): 22; 54; 56; 44, 45, 46, 48.

Also open from docs/ms13_close.md section (4), not close items: a backup folder path for figures/ and the repository; a human check by someone who has not seen the project; the zipped F1 source-data CSV for Zenodo; pushing the tags; the MS14 decision.

## R. Sub-step 16 (2026-11-10; DL-732; the user's statement of 15:12: MS14 items 1 to 7 not done natively; nothing in results, frozen criteria, drafts, figures, the plan or any tag changes; section Q above is kept as it was and is superseded only where this section says so)

- The user's two reports of 02:19 and 02:21 are WITHDRAWN (A1); docs/ms14_user_reports_2026-11-10.md keeps them with a note at the top and holds the statement at the end; docs/search_log.md is rewritten (A2): the plan's Table E.1 (the October 2026 general web-search pre-check; copied by script) and items 1 to 7 as "Not done natively on Nov 10; general web-search pre-check only". Nothing in the withdrawn reports is evidence of any search.
- 58. REPLACED by the user's ruling of 2026-11-10 (A3, DL-732); its text above (section Q) is kept as written in sub-step 15 and no longer lists open gaps: the gaps it named (Scholar numbers, method of items 1 and 2, slow-passage tool and result, Taher 2022 reading) rest on the withdrawn reports or are now stated as "not done".
- 59. SETTLED BY USER RULING (A3, DL-732). MS14: native searches not done; proceed by user ruling 2026-11-10; this is a departure from the plan (the plan is not edited). The plan's MS14 done-when ("docs/search_log.md complete", plan line 1365) and Table 11.1 (native Scholar and PubMed searches) are not met; the user rules to proceed.
- 60. OPEN (A3). The G8 outcome (plan lines 1380 and 1382) is to be written by the user; Claude Code does not write it and does not judge novelty. Because no systematic search was done, any novelty statement must be limited to what the web-search pre-check supports.
- 61. OPEN (A4; UNVERIFIED wording). The draft limitations paragraph docs/manuscript_limitations_novelty.md is for the user to edit; no manuscript file exists in the repository; it belongs in the "assumptions and limitations" section (plan line 1388); the date "October 2026" follows the plan's line 1842 (month only; UNVERIFIED).
- 62. OPEN (UNVERIFIED). The wording "general web-search pre-check only" is entered for all seven items as the user gave it; no row of the plan's Table E.1 names eLife RP 104249 or PMC12549018, so whether it is accurate for items 5 and 6 is for the user to say.

OPEN after sub-step 16 (the user has not ruled on them; none is closed by this step): 49, 50, 51, 52, 53, 55, 57, 60, 61, 62.

SETTLED OR CLOSED: 22; 54; 56; 44, 45, 46, 48; 58 (replaced by 59); 59.

Also open from docs/ms13_close.md section (4), not close items: a backup folder path for figures/ and the repository; a human check by someone who has not seen the project; the zipped F1 source-data CSV for Zenodo; pushing the tags.

## S. Sub-step 17 (2026-11-10; DL-734, DL-735; read-only scoping of MS15 in docs/ms15_scope_notes.md; nothing in results, frozen criteria, drafts, figures, the plan or any tag changes; section R above is kept as it was)

New open items, one line each (the user decisions of B4 (c); "UNVERIFIED" = no plan or repository source):

- 63. OPEN. Archive service and account for the release (plan D37, line 1780: "service chosen at MS15"); the repository names Zenodo only for the zipped F1 source-data CSV (R10, T12).
- 64. OPEN. Licences: code MIT by DL-037 (default adopted), copyright-holder name not sourced (UNVERIFIED); data and figures: the plan has CC-BY 4.0 only in the superseded MNA line (line 1398); for PCJ UNVERIFIED.
- 65. OPEN. Author names, affiliations, ORCID, funding, ethics, data and code availability statements, conflict-of-interest statement and AI-use disclosure text (plan line 1396 names conflicts and AI-use only; the rest has no plan source, UNVERIFIED).
- 66. OPEN. The manuscript text and who writes it (plan lines 1384 to 1396); no manuscript file exists.
- 67. OPEN. Which result families and figure files are archived and how (plan line 949; results/ is 32.6 GB in 32,070 files, git-ignored; any per-record file or size limit UNVERIFIED).
- 68. OPEN. Backup folder for figures/ and the repository; a remote and where the tags are pushed (none configured; branch is master, the plan writes main).
- 69. OPEN. The tagger and author identity "Your Name <you@example.com>" on all commits and 17 tags: leave it or not (Claude Code does not change tags).
- 70. OPEN. Checklist 10.8 item 6 (plan line 1284): the 13 journal provenance records are draft = true and name the build commit 5e90575 (FS1 f5d3f0d), not a release commit: accept as built with a note, or rule a rebuild (new hashes, v2 tags).
- 71. OPEN. Scope of the code and document additions the checklist needs: LICENSE, CITATION.cff, full README, CHANGELOG entry, docs/figure_map.md, scripts/make_all.ps1 with -Stage replication, a --from-record option (src/ or tests/ changes trigger the full fast suite).
- 72. OPEN. The clean Windows machine for checklist 10.8 (Python 3.11, Julia 1.10.11, Git) and who runs it.
- 73. OPEN. The zipped F1 source-data CSV (28,821,335 bytes as written; R10, T12): when and where.
- 74. OPEN. The PCJ and PCI requirements (template, code and data policy, AI-use disclosure, figure rules, licences, recommendation process): the user reads the pages; all UNVERIFIED here.
- 75. OPEN. docs/robustness_criteria.md still says "NOT YET FROZEN" in its opening lines although criteria-frozen exists; leave it as in the tag or correct it before the archive.
- 76. OPEN. Permission and time to run the full suite including the 24 slow tests before a release tag (plan lines 1224, 1268; the fast suite took 1405.18 s, DL-726; the slow-suite time is not documented).

OPEN after sub-step 17 (the user has not ruled on them; none is closed by this step): 49, 50, 51, 52, 53, 55, 57, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76.

SETTLED OR CLOSED (unchanged): 22; 54; 56; 44, 45, 46, 48; 58 (replaced by 59); 59.

## T. Sub-step 18 (2026-11-10; DL-736, DL-737; MS15 split into MS15a and MS15b by user ruling of 17:22; release files written; nothing in results, frozen criteria, drafts, figures, the plan or any tag changes; section S above is kept as it was and is superseded only where this section says so)

Items 63 to 76 after the rulings (one line each):

- 63. CLOSED, user ruling 2026-11-10: archive service Zenodo (D37). The account and the deposit are the user's, later (see 78 and 67).
- 64. CLOSED, user ruling 2026-11-10: code MIT with holder Daniel Voldman (LICENSE, 2026); data, figures and text CC-BY 4.0 (LICENSE-DATA.md). That PCJ requires or accepts CC-BY stays UNVERIFIED (74); the CC-BY legal text is not yet in the file (77).
- 65. CLOSED IN PART, user ruling 2026-11-10: name, email, affiliation, ORCID, funding and conflict-of-interest lines given and used. STILL OPEN: ethics statement, data and code availability statements and the AI-use disclosure (plan line 1396), which belong to MS15b.
- 66. OPEN, MOVED TO MS15b by the user's split (manuscript text; no manuscript in the repository).
- 67. OPEN. Which result families and figure files go into the Zenodo data record (a separate record from the software record of .zenodo.json); 32.6 GB in 32,070 files; any Zenodo limit UNVERIFIED.
- 68. CLOSED IN PART. The user reports a backup of C:\dev\mpr-gamma-surge (the path of the backup is not given; not checked by Claude Code); a GitHub remote is wanted. STILL OPEN: URL, public or private, where the tags are pushed (see 79).
- 69. OPEN. The placeholder identity "Your Name <you@example.com>" stays on all earlier commits and on the 17 tags; the user has set the git identity to Daniel Voldman for new commits (checked: this step's commits carry it); whether the old commits and tags are left as they are is the user's call; they become public when pushed.
- 70. OPEN. Checklist item 6 (DRAFT flag): finding and options A, B, C in docs/ms15_draft_flag_notes.md; part 2 needs the ruling (see 81).
- 71. CLOSED IN PART. LICENSE, CITATION.cff, README, CHANGELOG, docs/figure_map.md and scripts/make_all.ps1 are written (ruled by the user). STILL OPEN: a `--from-record` option for mprsurge.run (checklist item 5, plan line 1280) and what `-Stage replication` must contain (80).
- 72. OPEN. The clean Windows machine and who runs checklist 10.8.
- 73. OPEN. The zipped F1 source-data CSV (28,821,335 bytes as written): when and where.
- 74. OPEN. The PCJ and PCI requirements (template, code and data policy, AI-use disclosure, figure rules, licences, recommendation process).
- 75. OPEN. docs/robustness_criteria.md header "NOT YET FROZEN" (leave as in the tag or correct before the archive).
- 76. OPEN. Permission and time for the full suite including the 24 slow tests before the release tag.

New items:

- 77. OPEN (UNVERIFIED). LICENSE-DATA.md has the CC-BY 4.0 notice and link but NOT the full legal text; it is to be added from https://creativecommons.org/licenses/by/4.0/legalcode before the archive (Claude Code has no internet).
- 78. OPEN (UNVERIFIED). .zenodo.json: every field (title, upload_type, creators with name, affiliation and orcid, license "mit") is unchecked against Zenodo's current schema; it has no description and no version; CITATION.cff was parsed as YAML only (no CFF validator is installed). The Zenodo account, the GitHub-Zenodo link (if wanted) and the deposit are the user's.
- 79. OPEN, needed for part 2. The GitHub address and whether the repository is public or private. Everything in the history, including the author details, becomes public when pushed or archived (the user chose this).
- 80. OPEN (UNVERIFIED). scripts/make_all.ps1 was written and NOT run; its PowerShell parse check was blocked by the safety classifier and is not done (only a character and bracket check was made); the steps of -Stage replication (S1, A1, A2, A4, S3 mean-field, A0) and -Stage figures are partly inferred (the header marks which); not sourced and not written: the other milestones' steps, the network cells of S3, the Julia steps, the recording of the cleared Numba cache in provenance, -Stage all (it stops with an error); whether the stage covers "every G0 row" and whether the exit codes of run_A4.py and run_S3.py encode the K7 to K11 verdicts is UNVERIFIED.
- 81. OPEN, needed for part 2. The DRAFT-flag decision (item 70): A accept as built, B rebuild the 13 journal figures from one clean release commit (code change in scripts/fig_journal.py, new v2 tags), C B with the 11 drafts declared audit copies; and what "release commit" means (docs/ms15_draft_flag_notes.md sections 4 and 5).
- 82. OPEN. The README does not restate the initial conditions and the full gamma-power computation that the plan (line 1147) wants stated; it gives the numerical defaults of configs/base.yaml and points to the code (UNVERIFIED that a short statement is correct without a further read).

Settled by this step: the file line endings (CHANGELOG.md was CRLF in the working copy with a byte-order mark; it is now LF without a BOM; README.md was already LF).

OPEN after sub-step 18 (not closed by this step): 49, 50, 51, 52, 53, 55, 57, 60, 61, 62, 65 (in part), 66 (MS15b), 67, 68 (in part), 69, 70, 71 (in part), 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82.

SETTLED OR CLOSED: 22; 54; 56; 44, 45, 46, 48; 58 (replaced by 59); 59; 63; 64.
