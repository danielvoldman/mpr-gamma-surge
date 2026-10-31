# MS13 figure rules (13t, J11; short numbered lines; later prompts point here)

Sources: G1 to G12 from DL-511 (and the code helpers in `plotting/captions.py` and `plotting/figures.py`); J1 to J15 from the 13t-1 prompt (DL-545); STOP RULE 12 from the 13t-1 prompt. The plan (`docs/plan.md`) is not changed. Everything the plan does not state is UNVERIFIED. All eleven figures are untagged drafts; a tag is made only when the user says "tag".

## G1 to G12 (the draft figures, DL-511)
1. G1 class key: every figure that draws classes has one key line, verbatim from plan Table 2.1, saying which classes are surge classes (`captions.class_key_line`).
2. G2 failures visible: the word FAIL is in the title of every panel that shows a failed check; the red title colour is defined once per figure (`captions.RED_TITLE_NOTE`); FAIL lines are bold; no text below the tick-label size of the draft; blank strip values are explained from the A11 columns, else "blank in the stored table" (`figures.strip_line`).
3. G3 caption order: sentence 1 is the take-home and names the main failure(s) (`build_caption(main_failures=...)`); then what is drawn; then the claim-limit list.
4. G4 pinned values are labelled with their meaning when stored values or frozen code settle it, else "pinned value, cause not determined (UNVERIFIED)".
5. G5 parameters sentence: per-panel tags; swept parameters as range or list (`captions.sweep_text`); noise.sigma only where drawn records use noise, with "checked, not confirmed", G4-C4.
6. G6 class colours and class markers for classes only; seeds, levels and variants use the series marks and the network-seed lightness (`style.series_mark`, `style.network_seed_colour`).
7. G7 coincident stored values keep their stored positions and carry a "coincide" note naming the series (`captions.coincide_note`).
8. G8 classifier and spectrogram settings in one caption line, read from the frozen criteria (`captions.classifier_line`).
9. G9 plain labels: symbols for eta-bar, tau_d and Delta, units, "log axis", one number format (`captions.number_text`), internal codes defined once (`style.INTERNAL_CODES`), P2 = "hypoxia-like path".
10. G10 short on-panel claim-limit pointers only where they change how a panel reads (`figures.claim_pointer`); in the journal export they move to the caption.
11. G11 a number stated but not drawn is marked "(not drawn)" or removed (`captions.not_drawn`).
12. G12 the draft footers keep "as ruled (DL-...)" and cite DL-511 and DL-512 (13r) and DL-537 and DL-538 (13s); the journal export has no footer on the image.

## J1 to J15 (the journal export, DL-545)
1. J1 on the image: panel letters in reading order (top to bottom, left to right); axis labels with units and "log axis" where used, with symbols not code names; legends; class legend marks; short panel titles with FAIL in the title of every panel that shows a failed check (red title); short in-panel lines that change how a panel reads; network symbols; "coincide" notes that sit on a plot.
2. J2 moved out: DRAFT marks, "as ruled (DL-...)" footers, provenance text, status strips and blocks, G10 pointers, internal ID keys (defined once in the caption), long notes inside panels. They go to the caption or to the supplement sheet of the figure. No caption, figure number or title is drawn inside the figure file.
3. J3 failures stay visible (plan 7.2): every FAIL, NOT PASSED, NOT EVALUABLE or FAILED line of the draft strip appears in a panel title or in the journal caption; caption sentence 1 names the main failure(s); the full strip is in the supplement sheet. Nothing is dropped.
4. J4 journal-neutral settings, all UNVERIFIED, all in `configs/journal_export.yaml`: width at most 7.5 in (double column), 84 mm as a second setting, height at most 8.75 in, all text at least 8 pt at the final size, Arial or Helvetica if installed (else DejaVu Sans, said so), vector text and lines, fonts embedded (pdf.fonttype 42, ps.fonttype 42, no Type 3), line width at least 0.3 pt, RGB, PNG 300 dpi, TIFF 600 dpi (LZW, flattened, no alpha) and EPS only if they build without error. No journal requirement is claimed.
5. J5 the export is a mode of the existing make_<ID> drawing code (mode="journal"); the drawn-data digest of an export equals the draft's. Outputs: `figures/journal/<ID>/` (`<ID>_journal.pdf`, `.png`, `_caption.txt`, `_provenance.json`) and `figures/journal/supplement/` (`<ID>_supplement.md`, `<ID>_source_data.csv`, `<ID>_alt_text.txt`). `scripts/fig_journal.py <ID>` writes them and reads only results/.
6. J6 the journal caption is the draft caption rebuilt with the same builder (take-home with the main failure, what is drawn, class key, classifier line, parameters, claim limits including the text of the moved pointers); same stored numbers; the independent comparison applies.
7. J7 pilot F1, F3 and F5 first (13t-1); F2, F4, F6 and FS1 to FS5 follow in 13t-2.
8. J8 no collisions: nothing overlaps or touches (text-text, text-marker, text-line, text-image, text-frame, text-figure edge, legend-data, clipped text, marker-marker) unless it is in the allow-list with a reason; checked by code (`plotting/collide.py`) and by eye.
9. J9 layout is not data: the mode may rearrange panels, change the shape and move labels; it may not change a drawn value; F1 is a two-column grid at double-column width with the panel letters (a) to (k).
10. J10 known F1 draft faults removed (raw-crossings marker on its text, the cell-count text over the spectrogram, (j) and (k) labels on the frame of (i), badly wrapped schematic text, long legend, plain "eta_bar", dense status block).
11. J11 this file.
12. J12 known F2 and F3 draft faults removed (F3 in 13t-1: letters in reading order, one combined path for P1, P2, P3 and P5 with P4a and P4b separate, short titles, a legend of at least 8 pt, the empty space used; F2 in 13t-2).
13. J13 colour and accessibility: continuous scales only magma, viridis or cividis (never jet, rainbow, hsv, turbo); a colour bar with its unit on every colour-coded panel; classes, paths and seeds that share a panel differ in a non-colour attribute; greyscale and colour-vision simulation with an installed package (none installed: STOP that item and say so; no home-made matrices without telling the user); no red-green pair at similar lightness; text contrast at least 4.5:1.
14. J14 file names use only a-z, A-Z, 0-9, underscore, plus, minus, dot, comma, equals, with the case matching in the supplement and provenance files; heavy artists are rasterized, text, axes, ticks, lines and legends stay vector; sizes are reported and a PDF above 5 MB is flagged; everything is listed in `figures/journal/export_manifest.csv`; nothing is uploaded, tagged or pushed.
15. J15 how to work: one verification command (`scripts/ms13_verify_export.py`, a table figure x check, non-zero exit on any FAIL); `docs/ms13_export_checklist.json` and `docs/ms13_13t_progress.md` survive a context compaction; no check is weakened or deleted; an allow-list entry needs a stated reason, is logged and goes to the user for approval; an independent subagent reviews the export; scope stays as listed; a fix that fails twice on one overlap stops that item.

## Failures that stay visible (plan 7.2; shown, not dropped)
RB1 FAIL; RB2 FAIL; RB6 solver FAIL (181 ms); RB6 network f_pk FAIL; RB9(b) FAIL (4.391 Hz against 0.5 Hz); G7 NOT PASSED; D24 noisy subgrid FAILED (97 of 225 = 43.1 percent, 203 needed).

## STOP RULE 12
On any pre-check mismatch, unopenable or changed file, a stored-input hash differing from the provenance, an independent value disagreeing with an original value, record or log text disagreeing with a stored value, a drawn-data digest of an export differing from its draft, a draft file changing, or a pre-existing test failing in the committed state: STOP, report both values and the reading, patch nothing.
