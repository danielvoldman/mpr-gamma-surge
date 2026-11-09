# MS13 13t-10: fresh-subagent review of F3, F4a, F4b, FS4 and FS5 (part 1 of 2: F3, F4a, F4b)

Reviewer: one NEW fresh subagent (general-purpose, no earlier context, read-only; brief as in 13t-9 with the special-attention points (a) to (e) of 13t-10). It was given F3, F4a, F4b, FS4 and FS5 (every figure whose caption or image changed in this step). The report below is WORD FOR WORD as handed back (only the harness indentation removed). Part 2 is docs/ms13_13t10_review_part2.md. The triage is in docs/ms13_13t10_triage.md.

REVIEW OF F3, F4a, F4b, FS4, FS5 (read-only; nothing in the project was edited). Crops are in C:\Users\Alpha\AppData\Local\Temp\review13t10_crops (whole-figure plus a 2x3 grid per figure, plus detail crops of F3 a-c and d, F4a a and c, F4b a, d and f-g, FS4 a and f, FS5 d and g-j). I also checked the source-data CSVs and the alt texts.

=====================================================================
F3
=====================================================================
Not understandable (as a stranger, short caption alone):
- "the analysis record listed in the supplement" and "as recorded" appear again and again. "Recorded" is never defined in the short caption.
- "Hopf curve" is defined only indirectly. "Cycle branch" is not defined. "Slice" appears undefined at first use; "one fixed tau_d" gives it away only later.
- "main example in (c)" is odd because the main example is not a panel. "Path leg", "P1 (eta_bar ramped only)", "P5 (up, then back)" and the coupling "J ramped to 0 after a delay" are all used with no scale or meaning for J = -21.
- "model M3" and "the paths P1..P5" are given but never motivated.
- "Supplement F3" is cited three times with no description of what it holds.
- "the failed check was made at the main example in (c) and bears on them too" is hard to follow. The sentence is a long semicolon chain and the reader cannot tell what "them" is.
- "the reason is not recorded" (why bands end early) is a puzzling sentence in a caption.

Not supported by the image:
- The caption says "a black bar marks where the cycle crosses 25 Hz". The image shows a thin dark vertical line with a white outline, not a bar. The alt text says "tall black bar".
- The Hopf mark is called "black mark". It is a tiny three-pronged glyph, a few pixels wide, easy to miss.
- In (c) at tau_d 5 ms the slice's own Hopf mark is not visible. It is covered by the dark-red ring and the arrow. The caption says the ring is "one stored point drawn twice", but the image shows only one.
- The caption says the path starts at the grey open circle. The image also has a left-pointing arrowhead at that circle (the P5 return leg). In the short caption only "(P5 has an up row and a return row)" is mentioned for (e). The leftward arrowhead in (c) and (d) is not explained by the short caption, and in (d) it is hidden under the combined arrow.
- (d) and (e) share an x axis, and (d) has tick marks with no labels. The caption does not say so.
- Several legend phrases are not in the caption: "identical in eta_bar, Delta, tau_d (recorded)" and "Hopf curve (panel c: Delta 0.3, J -21; panel d: J -21, tau_d 5 ms)". The (d) curve is drawn at tau_d 5 ms. The short caption never says so.

Internal-looking text on the image:
- "tau_d (ms), log axis" uses the plain-text underscore form.
- Legend: "Hopf point of a slice", "25 Hz crossing of a slice", "P1, P2, P3, P5: identical in ...(recorded)", "P5 return leg", "P4a: Delta up", "P4b: Delta down".
- Row labels in (e): "P1 eta ramp (100 s)", "P2 hypoxia-like path (120 s)", "P3 drive", "P5 up", "P5 return". The durations in parentheses are not explained in the short caption.
- Colour-bar labels "Cycle frequency, main example" and "Spectral peak, main example" are fine.
- The source-data CSV uses "A4" and "A6" (for example "Hopf point of the A6 slice"). These are not on the image.

Claim limits and failed checks vs image:
- The red titles on (a), (b) and (c), "frequency check: FAIL", are present, as the caption says. (d) and (e) carry no red title, as stated.
- The colour bar carries two ticks. I read about 44.6 and 49.0 Hz off the bar, and the red text "Differ by 4.391 Hz; allowed 0.5 Hz" is present. This matches the caption.
- The limit "gamma-band result is stated for model M3 only" is not visible on the image. That is acceptable for a limit.

Numbers checked:
- 25 Hz crossings: 7, 6 and 3 slices in (a), (b), (c). Checked by counting marks on the image and by the CSV. Correct.
- 8 of 27 bands end before eta_bar 8.0. Checked on the image: 5 in (a) (tau_d 1, 2, 3, 5, 8) and 3 in (b) (tau_d 1, 2, 3). Correct.
- Main-example Hopf point at eta_bar 2.896, tau_d 5, and path start 1.396. Visually plausible: the grey circle is near 1.4 and the dark-red ring near 2.9. Not read to 3 digits.
- Arrow end 4.896: visually about 4.9. OK.
- The 9 tau_d values (1, 2, 3, 5, 8, 13, 22, 36, 50): visible as 9 bands.
- Colour-scale end values 9.8 and 73.7, and the maxima 60.3 and 73.5: could not check on the image. The colour-bar ends are not labelled. The CSV frequency column was not matched to them.
- Cycle 44.609 and spectral 49.0 Hz: tick positions agree.
- Hopf curve with 30 and 100 stored points: CSV rows are 30 (c) and 100 (d). OK.
- Short caption vs full caption: no contradiction found.

Visual problems:
- In (a) at tau_d 3 ms the Hopf mark and the 25 Hz line touch. The caption admits this only in the full version.
- In (b) at tau_d 5 ms they also touch (full caption).
- In (c) at tau_d 13 ms the Hopf mark and the 25 Hz bar also touch, and this is not mentioned anywhere.
- In (c) the tau_d 5 ms slice has the ring, the circle, the arrow and the arrowhead on top of the band. These overlap, and the band's Hopf mark is lost.
- In (d) the three arrows start from one circle. The P4a and P4b arrowheads and the combined arrow are readable, but the P5 return arrowhead is buried.
- In (c) the Hopf curve kink at tau_d 50 is visible (the straight segments). The kink is intended and is explained by the caption.

=====================================================================
F4a
=====================================================================
Not understandable:
- "entry-exit prediction" is defined, but the parenthetical is long and hard ("integral of the real part of the eigenvalue of the linearised model, taken from the start of the ramp, returns to zero").
- "one step of the prediction grid" is never explained in the short caption. The full caption says it is the eta_bar grid spacing.
- "testable", "in range", "octagon/diamond ring", "start distance" (in (c), only "a parameter of the start state" in the full caption), and "level-0 median of (d)" are unclear.
- "double dagger" is named but not described as a small mark.
- "the delay under a noise floor does not meet its check under the classifier-onset reading": a very dense sentence.
- "the onset check ... covers 0 to 2 of the 13 ramp durations" is opaque.
- "RB" codes are absent from the short caption, which is good. The word "hold" is used but not defined: "onset during the hold at the peak of eta_bar".
- "main example at its noise-free, solver-dependent delay 0.0662, not used as evidence (the value used is ... -0.000760)": hard to follow.

Not supported by the image:
- The legend and the caption say the daggers are hollow. Zoomed in, they are tiny dark-grey outlines (a cross-and-bar shape) drawn on top of the filled and open markers. The filled marks beneath are visible (orange, brown, purple fills show through). So (b) of the special-attention list is correct. But the daggers are about 1 percent of the figure width, and on the open (sigmoid) markers they are barely distinguishable from the marker outline.
- The caption lists the prediction line styles as "dash-dot for P1, dashed for P2, solid for P5". On the image, the P5 prediction (solid brown) and the P2 prediction (dashed orange) are clear, but the P1 prediction (dash-dot, a purple-ish line at delay 2) is overdrawn and hard to see.
- "open squares ... the 8 drawn delays": I could not find eight. In (a) two squares are visible (at about 0.02 and 0.035). In (c) five touching squares are visible. The squares in (c) abut and overlap each other, so the count cannot be reconciled with 8 from the image (the CSV gives 8 for P1 linear 2 + P1 sigmoid 2 or 3, ambiguous).
- "diamond: not testable, 3 runs": I see two diamonds in (a) (one hidden inside an octagon and a square at about 0.02, one at 0.035 inside a square) and two diamonds in (c) among the squares. I could not count three clearly.
- The foot-band dash, "one run with no raw crossing", is visible once in (a). In (c) the shaded foot band is drawn but no dash is visible, although the alt text says "a band at the foot".
- In (b) the legend colours the "P5 down-ramp offset (triangles)" and the "P5 hysteresis width" lines in purple, but P5 is brown everywhere else, and purple is P1's colour. The caption does not mention this. It is misleading.
- (c) caption says the octagon rings at start distance 0.5 mark "5 runs": five octagons are visible. OK.
- The red ring of the main example is visible at about 3e-4 on the ramp-rate axis, delay about 0.07. OK.
- The caption says the zero line is "dotted". It is dotted. OK.

Internal-looking text on the image:
- "Floor level (noise floor sigma)", "y range -0.127 to 0.0202, own axis", "Floor, raw crossing", "Floor, classifier onset: FAIL", "(main example)", "1.59e-9".
- Legend: "Hollow marks in (d), (e): 10 seeds; dark: median", "Dash in the shaded foot band: no raw crossing", "Predicted onset, linear (line style by path)", "Classifier onset, second reading".
- The red note, "Prediction: 0 of 6 testable runs within one step / Solvers: main example onset differs by 181 ms (1 ms allowed)", is decodable only with the caption.
- The CSV uses "(1 = untestable)" in a series name. The "untestable" rows are all NaN or zero in my reading, so flags could not be matched.

Claim limits and failed checks vs image:
- Red titles on (a) and (e) only. Yes: (a) "prediction FAIL, solver FAIL" and (e) "Floor, classifier onset: FAIL" are red. (b), (c), (d) are black, as stated.
- "0 of 6 testable in-range runs within one step": the red note in (a) says so. Visible.
- "181 ms against 1 ms": visible in the red note.
- "delays tie at -1.5 at the two lower levels": visible in (e) in red text and as two coincident clusters at -1.5.
- "the delay of the main example is taken from the runs with a noise floor": not visible on the image.
- Most claim limits are not on the image: "classifier flags a surge on pure trend...", "estimator fails 2 of 8 ring items" (full caption), "direction of change unresolved at 10 s and 316 s".

Numbers checked:
- Errors 4.4, 7.6, 12.7, 20.6, 25.1, 33.1: not on the image (the caption says so). Checked against the CSV: 25.07 (P5 linear, rate 0.0197), and for start distance 0.5: 33.15, 20.60, 12.68, 7.57, 4.40. Correct.
- Main-example delay 0.0662: image value is about 0.07. CSV 0.066192. Correct.
- Level medians -0.000760, -0.0423, -0.1051: image (d) shows about 0.00, -0.042, -0.105. CSV gives -0.000760, -0.042323, -0.105060. Correct.
- (e) medians -1.5, -1.5 and about -1.09. CSV: -1.5, -1.5, -1.0917. The caption says the classifier-onset delays tie at -1.5 at levels 0 and 1. Correct.
- 13 ramp durations from 1 to 1000 s: the x axis runs from about 3.5e-5 to 3.5e-2, giving 13 points. Consistent (ramp rate 0.035/T).
- "delay equals eta_peak - eta_H = 2": plateau at 2.0 in (a) and (c). CSV max is 2.0. Correct.
- "classifier equals raw at 8 of 13 (P1 linear)": the CSV gives 8 for P1 linear, 3 for P1 sigmoid and 13 for the others. Correct. Not readable on the image.
- "P1 linear = P1 sigmoid at 2 of 13", "= P5 linear at 11 of 13": could not check.
- 80 of 120, 84, 1.59e-9, 1.59e-6, 0.00159, step sizes: the three sigma values appear on the image's x axis. The rest is not on the image.
- Not checked or not checkable: 58.698 s, 58.879 s, 115.2 s (not on this image), and the 306/400/172/24 numbers (not on the image).
- Alt text says "delays from about 0 to about 3". The data maximum is 2.0 (y-axis goes to about 3.5). Wrong.
- Short caption: "2 further failed checks of the project are not shown". The full caption lists three noise-robustness FAILs (RB2 headline, RB2 subgrid, D24) as "listed with F4b". This is possibly inconsistent (2 vs 3). I cannot verify it.
- Short vs full caption: no direct contradiction in the numbers shown. The short caption does not mention the main-example class or the 58.698 s onset.

Visual problems:
- In (a) the right edge (rates 0.02 and 0.035) is a pile-up: octagon, square, diamond, daggers and filled markers coincide. It is the source of the uncountable marks.
- In (c) the five squares touch each other and the diamonds.
- The legend column of "Dash in the shaded foot band" and "Open square: onset during the hold" is clear but the symbols are small relative to the plot.
- The daggers are drawn in the same dark grey as marker outlines, so the "hollow so the marks beneath are visible" works only in the large-scale view.
- No clipping of labels was found. The red note in (a) fits inside the axes.

=====================================================================
F4b
=====================================================================
Not understandable:
- "foot marks: runs with no episode": whose runs? Noise-free, or the noisy seeds? Not stated.
- "the number above each panel is the number of seeds counted": stated, but the reason it is 8 or 9 at some rates is not.
- "pinned" (medians at 1.0 s are pinned); "flagged windows x step"; "the noise level sigma = 0.0624 is checked and not confirmed"; "checked, not confirmed; its check failed".
- "M2: the comparison model" is never described; "saddle-node (the fold ...)" is defined, but the "ring" in (g) ("the damped oscillation after the jump") is vague.
- "the runs without a ramp reach 7 of 10": what are "runs without a ramp"? This is not in the figure.
- "T_ramp 5.62341 s" is never mapped to the ramp-rate axis, and tau = 10 ms is not stated, so the reader cannot locate that point on the plot.
- "(a result, not a check)" is cryptic.
- "D-none" appears in the legend text only; the short caption never defines it.

Not supported by the image:
- Caption (d): "The dotted line at 1 s in (d) is the smallest duration the classifier can give, so medians at 1.0 s are pinned". The image and CSV contradict it. In (d), a dark median mark sits clearly below the dotted line (at about 0.5 s at ramp rate 0.0035). Whiskers and the orange and brown sigmoid series reach about 0.2 s. The CSV has noisy-seed durations of 0.30, 0.33, 0.40 and 0.50 s, and P2 linear 0.658 s. So 1 s is not the smallest value.
- "foot marks: runs with no episode": green diamonds appear at 10 of the 13 x positions in each of (a)-(d). In (a) the grey bar goes down to zero at positions 5 and 8 (and 4 to 10), yet there is no foot mark at positions 5 and 8. The foot marks do not follow the seed counts (9, 9, 10, 10, 10, 8, 9, 8, ...). I could not tell what they mark.
- "(a) to (d) ... of the six noise-free series": only P2 (orange) and P5 (brown) are clearly visible. P1 (purple) is hidden behind the other series almost everywhere, with one or two purple points at the right end. Not said in the caption.
- (f): "no scaling law is claimed", but the plot shows an almost perfectly straight line on log-log axes through all 13 points. A reader will see a power law.
- Rings: the octagon and diamond are visible at the right end of (a)-(d), as stated.
- (g) error bars, "±1 SE" on the axis label: invisible at this scale.
- (e) red title and the two red lines are present as described.

Internal-looking text on the image:
- "class D-none" in the legend, "Dark mark: median of the seeds with a value", "M2 ring: damped at 13 of 13", "Ring rate (1/s, ±1 SE)", "Jump offset (eta_bar), log axis", "Noise band on the delay, P2: noise robustness FAIL".
- The numbers across the top of each panel (9, 9, 10, ...) are unlabelled on the image.

Claim limits and failed checks vs image:
- Red title on (e) only: correct. (a)-(d), (f), (g) are black.
- "7 of 10 noisy seeds (8 needed)" and "97 of 225 cells agree (203 needed)": both appear in red text in (e). The 43.1 percent figure is not shown.
- "noise level sigma = 0.0624" is not on the image.
- "median delay ... negative from T_ramp 5.62341 s on": CSV medians are negative at all T >= 5.62 s (-0.63 to -0.13), then +0.001 at T = 3.16 s, -0.014 at 1.78 s and +0.108 at 1 s. So the statement is true for the longer ramps but misleading, since the sign flips three times at the fast end.

Numbers checked:
- Jump offset 0.0034 to 0.346: the image shows about 0.003 to 0.35 on a log axis. CSV 0.00343 to 0.34575. Correct.
- Ring rate -25.7 to -24.3: only the ticks -20, -10, 0 are drawn, so the image can show only "about -25". CSV -25.66 to -24.34. Correct, but only the CSV can confirm it.
- 13 ramp durations: 13 points visible. 10 seeds: the numbers at the top are 8 to 10.
- Dotted 1 s line in (d): located at 1 s on the log axis. Correct, but contradicted as "smallest" (see above).
- Not checkable on the image: 0.0624 (sigma) and 43.1 percent.
- Short vs full caption: no contradiction. The full caption defines D-none, but the short caption does not.

Visual problems:
- The seed-count numbers on top of (a), (c) and (d) are crowded: "10 10 10 10" sit close to each other and to the panel titles.
- Heavy overlap of the markers of P2, P5 and P1 along the plateau.
- (d) and (c) share a dense right-hand edge where the octagon and diamond sit on top of the median marks.
