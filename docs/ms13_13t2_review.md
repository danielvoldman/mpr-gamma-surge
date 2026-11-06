# 13t-2: fresh-subagent review of the SHORT captions of the recorded build from 282d3f5 (word for word as received; the harness indentation of the hand-back is removed)

Brief given: read each SHORT caption alone, as a reader of the journal who has never seen the project, with the image next to it (the full image and four quadrant crops of each, 30 images; the six short captions; nothing else); list every sentence or term you could not understand, every statement the image does not support, every text on an image that looks like an internal code; check every claim limit and every failed check the short caption states against the image and say if anything a reader needs to avoid over-reading the figure is missing. Report only.

Files opened: 6 short captions (F1, F2, F3, F5, F5c, F6) and 30 images (6 full images plus 24 quadrant crops). Nothing else was opened. Panel counts and values below come from the images as rendered. Anything I could not verify from the image is marked as such.

# F1

1. Not understood:
- "the main example (the run fixed before the analysis as the main case)" does not tell the reader what the main example is.
- "The classifier (a rule fixed before the analysis)" gives no rule. "class D-tr", "S-sus" and "surge classes" are explained only by one-phrase glosses.
- "its power spectrum peaks at 49.0 Hz (not drawn)" is a number the reader cannot find in any panel.
- "onset (when it first flags the gamma rise) is 12.0 s for the network" is never explained. The network traces in (d) and (f) are flat at 12 s, so the reader cannot see why a gamma rise is flagged there. The strip shows a purple triangle at about 12 s and the circle, plus and star at about 50 s.
- "no claim is made about the visual shape, either way" is odd given that the caption's first claim is "does not reproduce it".
- "map cells (one parameter pair of a grid of mean-field runs)", "ramp durations of 10 s and 120 s" and "0 of 3 seeds agree ... 1 of 4 map cells agree" refer to data that is not in this figure.
- "noise level sigma = 0.0624 (checked, not confirmed; its check failed)" is unexplained. The caption never says what sigma is noise in, or whether the network is noisy.
- "model M3", "ramp start and duration" and "J = -21" are given as bare parameters.
- "(j) and (k)": the caption says only "two windows shown". It never says what is plotted in (j) and (k), and the image has no y axis there.
- "(i) Spike counts of seed 0": the y axis is "neuron (row)", with ticks 0 to about 300, although N = 10,000. The caption does not say how rows were chosen or binned.

2. Statements the image does not support or contradicts:
- "the network ... does not reproduce it" (the surge). Visually the network envelopes in (d) and (f) closely match the mean field, and the network spectrogram (h) shows the same three ridges. The caption concedes the visual similarity later.
- "In the mean field the surge ends" is fine, but the image shows the network traces also narrowing and ending near 143 s, the same as the mean field. This sits oddly with the "S-sus (a rise that does not end)" label. The caption notes the label comes from the classifier and says nothing about the shape.
- The network rise starts visibly at about 50 s, earlier than the mean-field onset line at 58.7 s. The caption gives the 58.698 s and 12.0 s onsets but not this offset.
- "Failed check (red titles) ... 0 of 3 seeds agree at ramp durations of 10 s and 120 s, and 1 of 4 map cells": the red titles on (d) and (f) read only "network vs mean field: FAIL". The 10 s ramp and the map cells are not drawn.
- "7 further failed checks ... not shown": not checkable from the image.

3. Internal-looking texts on the image:
- "M3", "tau_d, tau", "t_on, T_ramp".
- "D-tr" and "S-sus", including the in-panel bold "network class S-sus; mean field D-tr".
- "ING".
- "mean field (recorded run)", "recorded values 50.170 to 50.924 s", "network raw first crossing (post hoc; ...)", and "event marks: strips above (d) and (f); height has no meaning".
- "(d) r(t), network vs mean field: FAIL", which is a check result rather than a scientific label.
- "r, v, s: Rate, mean potential, synapse".

4. Claim limits and failed checks:
- The network-versus-mean-field FAIL is visible in (d) and (f). The S-sus versus D-tr classes are visible in-panel.
- The 12.0 s onset and 58.698 s onset (the 58.698 s onset matches the blue line and (k)) are shown.
- The other failed-check counts (0 of 3 at two ramp durations, 1 of 4 map cells, 7 others) are not shown.
- The control result "control flagged in 10 of 10 seeds, ramp runs 10 of 10" is explicitly not drawn. A reader cannot confirm that the S-sus classification, and the 12 s onset, may be a control-type false flag. The caption gives the limit but the figure shows no control.
- Nothing in the figure tells the reader that the single network trace is largely a mean-field-like envelope. The caption flags this itself.

# F2

1. Not understood:
- "v is the mean membrane potential; the network's v is the mean over the neurons that are not refractory, a different definition". Why this matters for the comparison is not said.
- "supercritical bifurcation (the oscillation grows smoothly from zero, with no jump and no hysteresis)" is defined loosely.
- "a sweep steps eta_bar up and then down again".
- "no agreement criterion is applied to the amplitude comparison (information only)".
- "the surge result ... is stated for model M3 only; the surge result is stated for the mean field only": the figure has no surge, and the two statements are near-duplicates that read as contradictory.
- "no classifier ... or spectrogram ... is used" is irrelevant to the reader.
- "(c) ... above eta_bar 2.996 only (nearer to the Hopf point the shaded steps are still relaxing)": the 2.996 cutoff is explained only by the shading.

2. Statements the image does not support or contradicts:
- Mostly consistent: panel (c) runs from +0.13 at 3.3 to about -0.024 at 6.5, matching "+13.2 to -2.5 percent".
- Network amplitude below the Hopf point is about 0.2 to 0.3 in (b). I count 5 network points below it and 15 network points in total, which fits the "15 steps".
- The mean-field sweeps coincide, as stated.
- "does not follow the mean-field branch closely": panels (a) and (b) show the network points sitting almost on the black curves, with visible offset only at the first few points in (c). The caption's "differs by up to 13.2 percent" is true but the figure looks like close tracking. A reader will see agreement.
- Stable fixed point: legend swatch is solid, but the line drawn left of about 0.9 in (a) is dash-dot. The caption just says "Fixed point (grey)".
- "stable to eta_bar 8" is consistent with the black curves ending at the right edge, but the sweeps stop near 6.9 and the network at 6.5. The portion above 6.9 is a continuation (not sweep data), which the caption does not separate.
- The network up and down sweeps (square and diamond) separate visibly in (c) at about 4.9 and 5.7. The caption says nothing about network hysteresis between its up and down sweeps.
- At the Hopf point (about 2.9) the network amplitude is about 1 in (b), while the mean field is about 0. Not mentioned.

3. Internal-looking texts:
- "Hopf point (supercritical), v interpolated".
- "steps within 0.1 of the Hopf point (still relaxing)".
- "network N = 10,000, up sweep (open square)".
- Axis "relative difference (network - mean field) / mean field".
- None of these is a code name. "Hopf point: eta_bar 2.896" has an exact value.

4. Claim limits and failed checks:
- The caption correctly says there is no red title. The image has none, and no panel shows a failed check.
- The stated claim limits are single seed and no error bars (not visible; the image has no error bars and a single set of markers), plus M3-only and mean-field-only.
- Missing: that panel (c) is not drawn for the shaded steps near the Hopf point, so the difference there is not shown. The caption does mention it.
- Missing: that the network at the Hopf point has a large relative amplitude difference. The reader could over-read "the limit cycle appears at the Hopf point" as valid for the network, though the caption says the network does not rest below it.

# F3

1. Not understood:
- "values from the analysis record listed in the supplement".
- "the cycle frequency (the frequency of the oscillation that starts at the Hopf point ...)". The caption never says how a cycle frequency is chosen when it varies along the band.
- "as recorded" in "(7, 6 and 3 of 9 slices have one, as recorded)".
- "drawn as one arrow because their eta_bar, Delta and tau_d are equal". The caption never says why the paths are placed at the same point (equal parameters, different time courses), so the reader cannot tell what distinguishes P1, P2, P3 and P5 in (d).
- "(e) One row per path" has no description of what the rows show (only the time over which eta_bar is ramped, labelled with the 100 s or 120 s).
- "the failed check was made at the main example in (c) and bears on them too" is hard to follow.
- Bands that end before eta_bar 8 (for example tau_d 1 to 8 in (a), (b)) are not explained. A reader does not know whether the cycle disappears or the sweep was cut.

2. Statements the image does not support or contradicts:
- Tick counts (7, 6, 3 of 9) match what I count: (a) 7, (b) 6, (c) 3.
- "4.391 Hz" and "differ by 4.391 Hz; allowed 0.5 Hz" match the colourbar marks (about 44.6 and 49.0).
- "the grey open circle is the start of the paths (eta_bar 1.396)" matches (c).
- Red FAIL titles appear on (a), (b) and (c) alike, though the check was made only at the main example, which is shown only in (c). The caption explains this, but the panels (a) and (b) do not contain any marking of the check.
- In (e), P1 is 100 s and P5 up and return are 100 s while the others are 120 s. The caption does not mention that the paths differ in duration, and does not say whether this is relevant to "identical" paths.
- (d)'s legend says "P1, P2, P3, P5: identical in eta, Delta, tau_d (recorded)". P5 return is a separate brown arrow pointing back in the image. The caption's "P5 (up, then back)" is fine.

3. Internal-looking texts:
- "(recorded)" on the legend.
- "Hopf curve (panel c: Delta 0.3, J -21; panel d: J -21, tau_d 5 ms)".
- "Hopf point of the main example".
- Axis "tau_d (ms), log axis".
- "frequency check: FAIL" and "differ by 4.391 Hz; allowed 0.5 Hz" are check text, not scientific labels.
- "P5 return leg".
- "P4a: Delta up" and "P4b: Delta down" are code-like names.
- Row labels "P3 drive".

4. Claim limits and failed checks:
- The failed frequency check is stated correctly and matches the red titles and the colourbar.
- The caption says "No other failed check is about this figure".
- Missing:
  - The spectral peak comes from a simulated signal in a different run, and the colourbar has no uncertainty.
  - The 0.5 Hz allowance is not justified, so a reader cannot tell whether 4.39 Hz is large.
  - There is no statement that the maps (a) and (b) have no corresponding spectral peak.

# F5

1. Not understood:
- "the surge result holds for the noise-free mean field only" as the opening claim. Whether it "holds" is not defined.
- "a network cell agrees when all 3 seeds are in a surge class ... where the mean field is D-tr, or in NS ... where it is D-none (our reading, not verified)". The agreement rule is hard to parse, and "our reading, not verified" is unexplained.
- "Network cells and matching run: ramp duration 30 s (map: 120 s); no equivalence is claimed."
- "tie (plus: no single majority class among the 10 seeds of the cell; it counts as a disagreement under the 90 percent rule ...)".
- "(d) The same cells re-scored by a rule chosen after the results (post hoc; no check; dashed frame)". The re-scoring rule is not stated.
- "(e) Map 2: initial coupling J0 and ramp duration": nothing about what the colours mean.
- "203 cells, 90 percent, were needed": not defined where 90 percent comes from.
- "the blank lines through (c) and (d) are map cells that are not in the noisy subgrid".
- "(shorter ramps use a shorter window)".
- "no-ramp network controls ... are classified into surge classes" with no control drawn.

2. Statements the image does not support or contradicts:
- "3 of the 4 cells" matches the four markers (1 star, 2 to 4 octagon).
- Cell 1 agrees, matching the three surge-class marks (two S-abs and one S-rel).
- Subgrid: I count 15 by 15, consistent with 225 cells. I cannot count the 97 circles exactly from the image, so "97 of 225" is unverified, but the arithmetic 97/225 = 43.1 percent and 0.9 x 225 = 202.5, so 203, is correct.
- Panel (d) is mostly circles, in clear visual contrast to (c). The caption does not give the agreement count for (d). A reader can over-read (d) as a rescue of the result, though the caption calls it post hoc.
- The caption does not mention that no network seed anywhere is S+ (the legend lists it, and none is drawn).
- In (b), the "map 1 class (120 s)" and "matching mean-field run (30 s)" rows are identical for all four cells. The caption says no equivalence is claimed but the figure invites the opposite reading.
- Cell 3 and cell 4 sit at the hatched D-none edge, so mean-field classes there are near a boundary. Not stated.
- "Failed checks (red titles): network against mean field at the 4 cells and the 90 percent rule" matches red titles on (a), (b) and (c). In (a) the red title says "cells: FAIL", while the caption wording differs slightly.
- "6 further failed checks ... not shown": unverifiable.

3. Internal-looking texts:
- Axis "Delta, cell index i" and "tau_d (ms), cell index j".
- "D-tr", "D-none", "S+", "S-rel", "S-abs", "S-sus", "NS".
- "map 1", "map 2", "J0 (J at path start)", "T_ramp (s)".
- "subgrid cell agrees (...)", "(a disagreement by the 90 percent agreement rule)".
- "classes of the marks in (b)".
- "Mean field only; network disagrees at 3 of 4 cells" printed in the plot.

4. Claim limits and failed checks:
- The failed network-versus-mean-field check and the 90 percent rule are shown with red titles.
- Missing or weak:
  - The noisy subgrid is only 15 by 15, a subset of the 30 by 30 map, with 10 seeds, and the network is only 4 cells with 3 seeds. The caption states the numbers but nothing about how the 4 cells were chosen.
  - The caption says there is no claim of robustness to noise, but the (d) panel invites that reading.
  - The failed noise-level check sigma is mentioned in the parameter list only.

# F5c

1. Not understood:
- "Network classes do not reproduce the mean field" as the opening claim. The mean-field class is not drawn in this figure (only a frequency and onset line).
- "step-halving check ... halving the numerical time step must change the network peak frequency ... by less than 2 percent; its runs are not recorded, so not drawn". It is clear that the check failed because there is no data, but what it implies for the plotted frequencies is not said.
- "grey bar and tick: range and median of the ramp seeds".
- "dashed line in (d): the smallest duration the classifier can give (recorded minimum, 1000 ms)".
- "the counts 'control flagged in 10 of 10 seeds, ramp runs 10 of 10' come from other network runs, not the controls drawn here" is hard to parse and relies on data the reader cannot see.
- "ramp duration 60 s" is not visible in the figure, and the dotted onset line at 33.698 s is not explained against a ramp.
- "Controls in a surge class: 0, 2, 1 and 1 of 3; controls in S-sus: 0, 0, 2 and 2 of 3": the reader must count open marks by hand.
- The horizontal spread of marks within each N is not explained.

2. Statements the image does not support or contradicts:
- Control counts match what I count in (a): N = 1000, three open NS; 3000, one open S+, one open S-abs and one open NS; 10,000, one open S+ and two open S-sus; 30,000, one open S-abs and two open S-sus.
- "all 39 drawn ramp-seed onsets (8.0 to 27.0 s) are earlier than the mean-field onset (33.698 s)" is consistent with (c) (lowest about 8, highest about 27; the dotted line is about 33.7).
- The control onsets reach about 33 s at N = 30,000 in (c), i.e. near the mean-field onset. The caption restricts its claim to ramp seeds, but no-ramp controls also flag onsets of 10 to 33 s, which weakens any reading of the onset as ramp-driven. Only mentioned indirectly.
- At N = 10,000 and 30,000 several ramp seeds sit on the 49 Hz dotted line in (b). The caption says a seed on the line is not evidence of agreement, and that no agreement claim is made.
- "one ramp seed at N = 10,000 is NS" matches the single filled grey left triangle.
- Panel (a) shows no S-rel anywhere, although it is in the legend and caption. The caption does not say so.
- The caption mentions "(a) Class of every seed", but S+ ramp seeds appear only at N = 3000.
- The mean-field class is not drawn in (a), so "do not reproduce the mean field" cannot be read from (a).

3. Internal-looking texts:
- "recorded minimum to maximum and median of the ramp seeds".
- "(recorded minimum, 1000 ms)".
- "step-halving test not drawn: its runs are not recorded".
- "(b) peak frequency against N, step-halving check: FAIL".
- Legend "filled: ramp seed (10 per N)" and "open: no-ramp control seed (3 per N)".
- "S+", "S-rel", "S-abs", "S-sus", "NS".

4. Claim limits and failed checks:
- The step-halving failure is stated and shown as the red title of (b) with an in-panel note, which is consistent.
- Other limits in the caption: the controls are classified into surge classes, and there is no agreement claim. Both are consistent with the figure.
- Missing: that 3 control seeds per N is a small sample. The caption notes counts but not their weakness.
- Missing: that the plotted frequencies come from runs whose time-step convergence check failed, so the frequency values themselves are unvalidated. The caption implies it via "a seed on the dotted line is not evidence of agreement".

# F6

1. Not understood:
- "negative control (a run in which no surge is expected: here the hypoxia-like path with the mean excitability falling by the same amount)". The caption never defines negative controls 2 and 3 ("drive off, on", "exploratory"), although they are drawn in (b).
- "non-surge map cells ... in two regime maps". The two maps are not defined here.
- "failure label a to h": only c and e are defined in the caption. Labels a, b, d, f, g, h are in the figure as phrases such as "Delta above critical" and "amplitude below the fixed threshold" ("critical", "fixed threshold" and "damped-oscillation test" are undefined).
- "primary label (the first that applies; filled) and every label that applies (hatched)". The image legend uses "primary" and "any label" with grey shading and dots as well as hatching, so the caption's "hatched" does not match all bars (map 2 uses dots).
- "(a)" title in the image: "D-tr cells, no label: map 1 760, map 2 296" is unexplained in the caption.
- "P3 (P2 plus a common drive, amplitude 0.5, 1, 2)" and "rows with equal recorded values coincide": the reader cannot tell which curves coincide.
- "the test for damped against non-damped oscillations" is provisional but not explained.
- "2/3" and "Delta multiplied by 1.5 or 2/3" is clear but P4a and P4b are not labelled with this in the image.

2. Statements the image does not support or contradicts:
- Matches: red title on (c) and a red S+ network marker in (c). The five D-none map cells match "class D-none at all".
- S-rel counts 1, 1, 1, 1 and 2 in the noise row of (b), summing to 6, match "6 of 130" (13 ramp durations times 10 seeds).
- Failure-label bars sum to 169 (map 1: 48+32+8+51+1 = 140; map 2: 16+13 = 29). This matches "169 non-surge cells".
- "the first negative control without and with noise": the noise row is all NS, not D-none, so the noise changes the class from D-none to NS. The caption does not say so.
- "all are D-tr, including all 20 pre-registered runs": panels (d) and (e) show P2 (4 points), P3 at three drives (12 points), P4a (4) and P4b (4), i.e. 24 plotted points. I cannot reconcile 20 with the 24 shown. This is unverifiable from the image.
- (b) shows negative control 2 (drive off and drive on) as D-tr at every T_ramp (not D-none), so a no-surge control gives an episode that ends. The caption never mentions this, though it concerns the same controls the caption says test the claim.
- Negative control 3 is D-none at all T_ramp, so does not test anything in the caption.
- (d) and (e): the legend lists five P-series but only about three visibly distinct lines appear in (e); P2, P4b and P3 drive 2 overlap at 48 to 49.5 Hz, P4a at 45 Hz and one P3 line at 39 to 40.5 Hz. In (d), P2 open versus filled markers distinguish T_ramp only. The reader cannot read off which series is which.
- Panel (a) says the network cell has "S+" and the caption says "S+ ... where NS (no rise) is expected". This agrees with the image.

3. Internal-looking texts:
- "negative control 1 / 2 / 3", "(exploratory)", "drive off / drive on".
- "map 1, primary", "map 2, any label", "(D-tr cells, no label: map 1 760, map 2 296)".
- Labels "a: Delta above critical", "b: tau_d outside window", "c: a flag, not a demonstrated cause", "d: ramp too fast for 10 cycles", "e: no exit (D-sus or S-sus)", "f: amplitude below the fixed threshold", "g: Hopf point, no time inside", "h: rejected by the damped-oscillation test".
- "T_ramp", "map cell: Delta, tau_d (ms)", "D-none", "NS", "D-tr", "S+", "S-rel".
- "small mark: class (D-tr)".
- "P3, drive 0.5 / 1 / 2", "P4a", "P4b".
- "(c) negative-control check: FAIL".

4. Claim limits and failed checks:
- The failed negative-control check is stated and consistent with the red title of (c). The failure involves a single network seed, as the caption says.
- The caption says "No other failed check is about this figure".
- Missing:
  - The noise level sigma check failed (stated only in the parameters), yet the noise row of (b) uses that noise.
  - Negative control 2 gives D-tr in the mean field at every T_ramp, which the figure shows but the caption does not discuss. A reader may conclude that control 2 failed too, or that it is not a negative control.
  - The label c is described in the caption as a flag, not a demonstrated cause. The image label ("a flag, not a demonstrated cause") gives no meaning, so the caption's definition is the only one.
  - The "all 20 pre-registered runs" is not checkable and may not match the 24 drawn points.
