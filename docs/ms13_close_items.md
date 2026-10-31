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
