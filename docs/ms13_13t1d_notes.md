# 13t-1d notes (written after the step; read-only: no code, figure or rebuild changed)

## (a) Findings of the first-build review that were NOT fixed
Full review: docs/ms13_13t1d_review.md. "Fixed" in DL-576: F5 (b) class key, F5 (c) y label beside (a), F5c key lines, F5c undefined-seed counts. Every other finding stays; categories: ruled/stored, caption, display, open.

| # | Review finding | Category | Figure, panel | Why it stays (one sentence) |
|---|---|---|---|---|
| 1 | Raw first-crossing marks (circle, plus, star) fuse | stored coincident positions | F1 (d), (f) strip | The three stored times 50.170 to 50.924 s are not moved (R3, R6, allow-listed). |
| 2 | Seeds 1 and 2 look like one line; legend styles not matched | display | F1 (d), (f) | The envelopes of the three stored seeds nearly coincide; none is chosen or hidden. |
| 3 | Legend swatch (grey line) differs from the grey band | display | F1 (c), (e), key | Minor legend simplification, not changed. |
| 4 | Network envelope looks like the mean field; "S-sus" and "0 of 3 agree" not tied to the picture; contradicts headline | stored result, ruled wording | F1 (d), (f) | The class is the stored classification (rule fixed before the runs); the caption states that no claim is made about the visual shape. |
| 5, 6 | Title/strip gap about 1 mm; red text near the curve | display | F1 (d), (f) | Collision checker passes (0 unlisted), no further change made. |
| 7 | Shared y range leaves 70 percent empty | ruled display | F1 (c) to (f) | One y range per quantity is a ruled choice so mean field and network compare. |
| 8 | White band at the spectrogram edges | explained | F1 (g), (h) | Caption states why (R7: no stored window there). |
| 9, 10 | Low contrast onset line; sparse frequency ticks | display | F1 (g), (h) | Minor; ticks limited to avoid touching at this height (13t-1c). |
| 11 | Colour bar far from (g), long rotated label | display | F1 colour bar | Label text is the ruled T6 wording; right margin limits the size. |
| 12 | Window frames in (i) hide data, look like data | display | F1 (i) | Frames are 1 s windows on a 165 s axis; the caption says so. |
| 13 | Spike band flush with the frame in (j), (k) | open for the reviewer | F1 (j), (k) | Rows are padded by 30 rows; the dense stored top rows still fill to the edge of the data. |
| 14, 15 | Raster unreadable; no y label; tick text 58.7 vs 58.698; (b) no label; dotted and dashed lines | display | F1 (j), (k), (a), (b) | Rows are those of (i) (S5); (b) y label dropped because it touched (a) (DL-574). |
| 16, 17, 18 | Schematic arrow tiny; I-drive has no panel; code-style names; model units | display | F1 schematic | Schematic is our layout of labels, said so in the caption; names kept. |
| 19 | Alt text r returns near baseline | alt text | F1 (c) | Minor wording, not changed. |
| 20 | (nothing found) | - | - | - |
| F3-1, 2 | Hopf mark fuses with the 25 Hz bar | stored coincident positions | F3 (a), (b), (c) | Stored positions closer than the mark widths; allow-listed, not moved. |
| F3-3 | Dark arrow and ring on dark band | ruled | F3 (c) | T7: line at most 1 pt, ring at most 4 pt, hollow. |
| F3-4 | Coarse polyline | stored data | F3 (c) | 30 stored points; the caption says it is drawn as straight segments. |
| F3-5, 6 | Bands clipped at 8; unlabelled slice ticks; small marks | display | F3 (a) to (c) | Axis range and tick set unchanged; marks sized by T7/S3. |
| F3-7 | Red RB9(b) FAIL title with no plotted failure | ruled (J3) | F3 (a), (b), (c) | See below. |
| F3-8, 9, 10, 12, 13 | Arrow bundle; (d) no x labels; P5 return hidden; (e) rows equal; no units | display | F3 (d), (e) | Stored positions coincide (S2); (d) shares the x axis with (e). |
| F3-11 | Legend uses A4, A6 | open | F3 legend | See (b); T8 concerns captions only. |
| F5-3, 4, 5, 6, 7, 8, 9, 10, 11 | In-panel text near frame; numbered symbols hide cells; tiny cells; marks nearly touch; subgrid gaps; spacing; hyphen minus | display / ruled | F5 (a), (c), (d), (e), (b) | Sizes are fixed by the ruled mark rules (S1, T10, allow-listed); checker 0 unlisted. |
| F5c-3, 4, 5, 6, 7, 8, 9 | Slot x positions; controls not drawn; marks hide reference lines; S-rel in key only | stored values / display | F5c (a) to (d) | Marks keep their stored values (allow-listed on the reference line); the caption states the slot layout. |
| F5c-2 | Red RB6 title, nothing shows the test | ruled (J3) | F5c (b) | See below. |
| Caps | Long captions; check IDs; "stored"; headline; "our reading, not verified" | ruled (T8) | all | See below. |
| F1/F5c caption | "10 of 10" and "7 of 10", "do not separate" vs N = 1e3 | ruled claim limits | F1, F5, F5c Limits | MS9(e)-1, MS11-C1, G4-C3 keep their ruled wording and numbers. |

### Red titles with no plotted failure
- F3 (a), (b), (c): the failure is RB9(b), spectral peak 49.0 Hz against cycle frequency 44.609 Hz (difference 4.391 Hz against 0.5 Hz). The panels draw the cycle frequency only; the spectral peak is not a plotted quantity of F3, so no panel can show it. The J3 rule (plan 7.2: failed checks are shown, not dropped) requires FAIL in the title of every panel that shows a result the failed check concerns; the caption gives both frequencies.
- F5c (b): the failure is RB6, the network f_pk row (halving the step must change f_pk by less than 2 percent; stored value blank, threshold < 0.02). Panel (b) draws network f_pk; the step-halving runs are not stored in F5c, so the test cannot be drawn. The title is red by J3 (DL-554 R4); the caption names the check and the stored row.
- F1 (d), (f) and F5 (a), (b), (c) show the failure (class or count) on the panel.
- Open for the reviewer: whether a red title should stay where the panel cannot show the check.

### Long captions, check IDs, the word "stored"
- Long: T8 asks for seven labelled paragraphs, every claim limit with the same meaning and numbers, every FAIL in the caption; the length comes from the limits list (ruled) and the per-panel sentences.
- Check IDs (RB1, RB6, RB9(b), G4, G7, D24 ...): each is defined once in the key paragraph (tested); they are the names under which the failures are logged and listed in the supplement.
- "stored": the figures draw values read from stored result files and the caption says so on purpose (J3, R6, G7 rules: stored values are not recomputed or moved). The word is not explained further; that is open for a ruling.

## (b) Project codes and step IDs still on journal IMAGE text
Extracted from the figure objects of the recorded build (text, panel).

F1
- schematic: "P2: hypoxia-like path", "t_on: ramp start time", "T_ramp: ramp duration" (ramp protocol box); "M3" (box heading); "M3 is read as an inhibition-dominated (ING) local circuit", "tau_d: Synaptic decay time (M3)", "Inhibitory + first-order synapse (ING)", "tau: Membrane time constant" (M3 box).
- (d), (f) in-panel: "network class S-sus, mean field D-tr; 0 of 3 seeds agree (RB1 FAIL)"; titles "(d) r(t), network: FAIL", "(f) v(t), network: FAIL".
- key: "mean-field onset (D-tr, 58.698 s)", "network classifier onset (S-sus, 12.0 s; the 3 seeds coincide)".

F3
- (a) to (c): y label "tau_d (ms), log axis"; titles "(a) Delta = 0.05, RB9(b) FAIL", "(b) ... RB9(b) FAIL", "(c) ... RB9(b) FAIL".
- legend: "Hopf point of an A6 slice", "25 Hz crossing of an A6 slice", "Hopf curve, A4 record (panel c: Delta 0.3, J -21; panel d: J -21, tau_d 5 ms)", "A6 Hopf point (Delta 0.3, tau_d 5 ms)", "P1, P2, P3, P5: identical in eta-bar, Delta, tau_d (stored)", "P5 return leg", "P4a: Delta up", "P4b: Delta down".
- (e): row labels "P1 eta-bar ramp (100 s)", "P2 hypoxia-like path", "P3 drive", "P4a ...", "P4b ...", "P5 up", "P5 return" with ramp durations.

F5
- key: "D-tr (map cell, mean-field class)", "D-none (...)", "subgrid cell is a tie (a disagreement by the D24 rule)".
- (a): title "(a) map 1, mode D, T_ramp 120 s / RB1 cells: FAIL"; x label "tau_d (ms), cell index j"; in-panel "Mean field only; network disagrees at 3 of 4 cells".
- (b): "(b) 4 network cells: RB1 cells FAIL"; rows "map 1 class (120 s)", "mean-field companion (30 s)", "network seed 0/1/2", "network against mean field".
- (c): "(c) D24 rule: FAILED", x label "tau_d (ms)". (d): "(d) post-hoc view P-1", "tau_d (ms)". (e): "(e) map 2, mode D", "T_ramp (s)", "J0 (J at path start)".
- class key under (d): "D-tr, D-none, S+, S-rel, S-abs, S-sus, NS".

F5c
- key: "S+", "S-rel", "S-abs", "S-sus", "NS"; "dotted line: mean-field companion value, (b) and (c)"; "dashed line: stored minimum duration, (d)".
- (a) "network class of every seed against N" with class tick labels S+ ... NS; (b) "(b) f_pk against N (RB6): FAIL", y label "f_pk (Hz)"; (d) "duration against N, log axis".

(No decision-log numbers, run names (S8, S9), file keys or draft marks are on any image; A4 and A6 occur only in the F3 legend.)

## (c) Were the FINAL F5 and F5c recorded PNGs looked at after the 0584741 rebuild?
Before this step only partly: the full images of F5 and F5c were looked at in the pre-commit trial render (same code), and of the recorded PNGs only F5 quadrant 4 and F5c quadrant 2 were read. Now done on the recorded files (PNG at 600 dpi, full image at 1/3 and quadrants at 2x of 200 dpi): F5 full, quadrants 1, 2, 3, 4; F5c full, quadrants 1, 2 (read earlier), 3, 4.

What was seen:
- F5 (6.3 x 5.45 in): key block at top; (a) map with four numbered symbols (hexagram 1, heptagons 2 to 4), in-panel three-line text clear of the frame; (b) class table with all marks readable, symbols clear of the frame; (c) and (d) marks in cells with the blank gaps, no touching marks visible, "Delta" label of (c) about 0.3 in right of the frame of (a) (no longer beside it); (e) map 2 with hatch, labels readable; the new class key "classes of the marks in (b)" under (d) is complete (D-tr, D-none, S+, S-rel, S-abs, S-sus, NS); no cut or overlapping text.
- F5c (6.3 x 8.0 in): class row and five key lines at top, panel (a) title below them without overlap; (a) to (d) marks 4 pt, no touching marks found (three open NS triangles at N = 1e3 are close but separate); reference lines visible, seed marks sit on them where the stored value equals the line; (b) red title; groups separated by thin grey lines; tick labels and axis labels readable; bottom margin clear.
- Nothing needing a further fix was seen; this does not replace the cvd check by hand.

## Open
- Item 5 of the previous prompt: the F3 caption states the 30 stored points of the (c) curve ("is drawn as straight segments between its 30 stored points") but does NOT state the 100 stored points of the (d) curve. Open; needs a caption change and a rebuild, not done here.
- Image legends of F1 and F3 still name A4 and A6.
