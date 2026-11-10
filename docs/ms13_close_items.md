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
