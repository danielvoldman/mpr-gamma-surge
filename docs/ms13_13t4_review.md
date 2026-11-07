# 13t-4: fresh-subagent review of the SHORT captions of the recorded build from 86b7d86 (word for word as received; the harness indentation of the hand-back is removed)

Brief given: read each SHORT caption alone, as a reader who has never seen the project, with the image next to it (the full image and four quadrant crops of each, 35 images; the seven short captions; nothing else); list every sentence or term not understood, every statement the image does not support, every text on an image that looks like an internal code; check every claim limit and failed check against the image; say whether any label starts with a lower-case word. Report only.

Files opened (42, as briefed): the seven caption files (F1, F2, F3, F5, F5c, F6, FS1 `_journal_caption.txt` in C:\dev\mpr-gamma-surge\figures\journal\<fig>\) and 35 PNGs (<fig>_full, _q1 to _q4) in the session scratchpad folder rec1.

REVIEW OF 7 SHORT CAPTIONS AGAINST THEIR IMAGES (read-only; I opened only the 7 caption files and the 35 images).

## F1
1. Could not understand
- a. "its power spectrum peaks at 49.0 Hz (not drawn)": which signal (v? r? mean field?) is never said. Panel (g) shows ridges of about 28 Hz rising to about 60 Hz, so a reader cannot connect 49.0 to anything.
- b. "the network envelopes (the minimum to the maximum of a series in each pixel column)": a rendering detail, not a scientific meaning.
- c. "first crossing of its detection threshold": what threshold, and why it is "post hoc" (the image legend says "post hoc"; the caption never explains it).
- d. "the failed check concerns the class given by the fixed classifier ... no claim is made about the visual shape, either way". This contradicts the opening "the network ... does not reproduce it".
- e. "(control flagged in 10 of 10 seeds, ramp runs 10 of 10; other network runs, not drawn)": what is "flagged" and what "control" refers to is unexplained.
- f. "noise level sigma = 0.0624 (checked, not confirmed; its check failed)": the role of noise is never described, and nothing in the image shows noise.
- g. "classifier window 2 s, step 1 s": never explained.
- h. "hypoxia-like path P2 ... coupling J ramped to 0 after a delay": the delay is not given. The image shows two sets of vertical lines (dotted = eta ramp, dashed = J ramp) that the caption does not distinguish.
- i. The values 1.396, 2.896, 4.896 on the y axis of (a) are not explained (2.896 is presumably the Hopf point, but F1 does not say so).
2. Unsupported or contradicted by the image
- a. "does not reproduce it": by eye the network envelopes in (d) and (f) look like the mean-field ones in (c) and (e). The caption half admits this. The only visible support is the red text "Network class S-sus; mean field D-tr".
- b. "its onset ... is 12.0 s for the network": the triangle is at about 12 s, but nothing visibly rises in (d), (f) or (h) until about 50 s. The window in (j), 12.0 to 13.0 s, shows only dense, irregular spiking with no visible gamma. The onset claim is not visually supported.
- c. "(j), (k) The spikes of seed 0 (one row per neuron, as in (i))": (j) and (k) have no row axis, and the picture is a dark band over a ragged lower edge, not rasters in which rows can be read.
- d. "(i) ... one row per neuron" with N = 10,000: the y axis of (i) stops at about 300 ("Neuron (row)"). The caption does not say rows are subsampled or binned.
- e. "(a), (b) ... J (negative = inhibitory)": no such wording on the image; (b) just shows 0 to -20.
- f. Panels (a) to (f) have no time labels. Only (g) and (h) show time, so "starting at 5 s", "ramp duration 120 s" and "12.0 s" cannot be read on those panels.
- g. "(c), (e) Rate r and mean potential v": the panel titles say "R(t)" and "V(t)", capital letters against lower-case axis labels.
3. Internal code or jargon on the image
"P2: hypoxia-like path", "M3", "inhibition-dominated (ING)", "Lorentzian heterogeneity (Δ)", "t_on, T_ramp", "J, tau_d, tau", "r, v, s", "D-tr", "S-sus", "(d) ... FAIL", "Network raw first crossing (post hoc ...)", "Event marks: strips above (d) and (f)".
4. Claim limits and failed checks
- Visible and supported: the class mismatch (red titles and the in-panel text "S-sus / D-tr"); the mean-field onset at 58.698 s (dash-dot line); the classifier onset (triangle); the three first-crossing marks at 50.170 to 50.924 s (circle, plus and star overlap); the two windows (solid and dashed orange in (i) match the frames in (j) and (k)).
- Stated but not visible (all marked "not drawn" or not marked): 0 of 3 seeds at ramps of 10 s and 120 s; 1 of 4 map cells; the noise-level failed check; the 7 further failed checks; the no-ramp control limit (no control run in the image); "control flagged in 10 of 10, ramp runs 10 of 10" (marked not drawn). The "network surge classes ... not evidence of a ramp-driven surge" limit has no visual support.
5. Lower-case label starts: yes. "r (model units)", "v (model units)", "t_on, T_ramp: ...", "tau_d", "inhibition-dominated (ING)", "spike raster", "spectrogram of v", "mean potential,", "synapse", "overlap at this scale ...". Titles "R(t)" and "V(t)" are inconsistent with the axes "r" and "v".

## F2
1. Could not understand
- a. "same class is required", "classes disagree", "class": a class is never defined in this caption (D-tr, S-sus, and so on are not named), so the failed check cannot be understood.
- b. "checked at the main example ... for ramp durations of 10 s and 120 s, at 4 map cells and overall; all four checks failed": which four checks? The list reads as five items (main example, 10 s, 120 s, 4 map cells, overall).
- c. "(the steps within 0.1 of the Hopf point are still relaxing)": relaxing to what?
- d. "the surge result ... is stated for model M3 only and stated for the mean field only": clumsy and opaque, and the figure does not draw a surge.
- e. "differs from it by up to 13.2 percent in (c)" and "differing by +13.2 to -2.5 percent above eta_bar of 3.0": the same range is stated twice with different wording.
- f. "(largest difference 1.2e-3 relative from 0.2 above the Hopf point)".
- g. "no agreement criterion is applied ... (information only)".
- h. "the network's v is the mean over the neurons that are not refractory, a different definition": the reader is not told why this matters.
- i. "v interpolated" (image legend) is not in the caption.
2. Unsupported or contradicted by the image
- a. "against 0.08 and 0.55 for the mean field" at the Hopf point: the mean-field markers in (b) sit at about 0 there, and 0.55 is not visible.
- b. "network up and down sweeps ... 0.095 (1.071 up, 1.166 down) at eta_bar 2.896" and "0.080 at eta_bar 5.696": squares and diamonds overlap in (b) and the differences cannot be read.
- c. "(c) ... above eta_bar 2.996 only": the first drawn point in (c) is at about 3.3; the image says "Not drawn at and below the Hopf point"; 2.996 is not visible.
- d. "stable to eta_bar 8": the black line simply ends at the axis limit of 8. The sweeps end at 6.9.
- e. The legend entry "Mean field, down sweep (hollow, smaller)" shows a small black "v", not a hollow marker (image problem).
3. Internal code or jargon on the image
"(c) Network vs mean field: FAIL", "Hopf point (supercritical), v interpolated", "Steps within 0.1 of the Hopf point (still relaxing)", "The network and mean-field classes disagree elsewhere (check failed)", "Relative difference of v amplitude (network − mean field) / mean field".
4. Claim limits and failed checks
- Supported: red title on (c) only; (a) and (b) have none; the text "this panel compares amplitudes only"; max 13.2 percent at about 3.3 and about -2.5 percent at 6.5; the 15 network steps (0.896 to 6.496) and the 61 mean-field steps match the markers.
- Not visible: the class disagreement itself (the caption says it is not drawn). Also not visible: the single-seed limit (no error bars is true), "no robustness to finite-size fluctuations", and the 10 s and 120 s ramp and map-cell checks.
5. Lower-case label starts: yes. "v (mean potential)" and "v amplitude (max − min)".

## F3
1. Could not understand
- a. "The paths coincide in (c) and (d) because they differ in J, drive or time course, which these planes do not show": the logic is garbled ("coincide because they differ").
- b. "a black bar marks where the cycle crosses 25 Hz": why 25 Hz is never said, because "gamma band" is not defined in this caption. It also says "the gamma-band result is stated for model M3 only".
- c. "(7, 6 and 3 of 9 slices have one, as recorded)": "as recorded" is meaningless to a reader.
- d. "spectral peak (the peak of the power spectrum of the simulated signal)": which simulation and signal.
- e. "the failed check was made at the main example in (c) and bears on them too": why (a) and (b) have red titles is hard to follow.
- f. "no classifier ... or spectrogram ... is used": irrelevant noise for the reader.
- g. "(e) One row per path.": the caption does not explain the path durations (100 s and 120 s) printed on the image, or P5 "return".
- h. "straight segments between recorded points": a plotting detail.
2. Unsupported or contradicted by the image
- No contradictions found. I checked that 4.391 Hz, 0.5 Hz, the ticks at about 44.6 and 49, the slice counts with a 25 Hz bar (7, 6, 3), the ring at 2.9, the circle at 1.4, and P4a up and P4b down are all consistent.
- Omissions: the arrows in (c) (paths) and the colour range (10 to 73 Hz) are not described. The caption says "cycle frequency" but the colourbar says "Limit-cycle frequency".
- In (a), the slice at tau_d about 3 has its 25 Hz bar touching the Hopf mark, so "7 of 9" is hard to verify by eye.
3. Internal code or jargon on the image
"tau_d (ms), log axis", "Hopf point of a slice", "25 Hz crossing of a slice", "P1 ... P5", "P4a: Δ up", "P4b: Δ down", "P5 return leg", "P1, P2, P3, P5: identical in η̄, Δ, tau_d (recorded)", "frequency check: FAIL", "Differ by 4.391 Hz; allowed 0.5 Hz", "main example".
4. Claim limits and failed checks
- Supported: the failed frequency check is fully visible (red titles, red bar annotation, two ticks 4.391 Hz apart).
- Not visible: "values from the analysis record" and the "peak frequencies are spectral peaks" limit (only the 49.0 Hz tick, no spectrum).
5. Lower-case label starts: yes. "tau_d (ms), log axis" (y axis in (a)).

## F5
1. Could not understand
- a. "97 of 225 cells (43.1 percent; 203 cells, 90 percent, were needed)": agree with what, and how is "agree" defined for a noisy cell? Not stated.
- b. "a network cell agrees when all 3 seeds are in a surge class ... where the mean field is D-tr, or in NS ... where it is D-none (our reading, not verified)": dense and hard to follow.
- c. "Network cells and matching run: ramp duration 30 s (map: 120 s); no equivalence is claimed": unclear why 30 s versus 120 s.
- d. "(d) ... re-scored by a rule chosen after the results": the rule is never stated, and the sentence repeats itself ("the same cells agree in 173 of 225 ... under the re-scoring chosen after the results").
- e. "the blank lines through (c) and (d) are map cells that are not in the noisy subgrid".
- f. "(e) Map 2: initial coupling J0 and ramp duration": what the colours mean is not said, and J0 is not defined.
- g. "classifier ... shorter ramps use a shorter window".
- h. "noise level sigma = 0.0624 (its check failed)".
- i. "no-ramp network controls ... are classified into surge classes": the sentence is cryptic.
- j. "cell index i / j" (image) versus "map cell" (caption).
2. Unsupported or contradicted by the image
- a. 97 of 225 (43.1 percent), 203 and 173 of 225 (76.9 percent) are printed nowhere on the image. By eye the circles in (c) are roughly half and in (d) clearly more, which is plausible, but no counts are given.
- b. No contradictions found. I checked the per-seed classes in (b) (cell 1 S-abs, S-abs, S-rel gives agreement; cells 2 to 4 each have an S-sus, or NS is missing where D-none is required, giving disagreement), the 1-of-4 count, and the position of the numbered cells.
- c. The legend in (b) includes S+ and NS marks that are not used in the data (harmless).
3. Internal code or jargon on the image
"D-tr", "D-none", "S+", "S-rel", "S-abs", "S-sus", "NS", "Map 1 / Map 2", "cell index i / j", "T_ramp", "J0 (J at path start)", "Subgrid cell is a tie (a disagreement by the 90 percent agreement rule)", "Post-hoc re-scoring of (c)", "(a) ... cells: FAIL", "(c) ... rule: FAILED", "tau_d".
4. Claim limits and failed checks
- Supported: three red titles ((a), (b), (c)). The 3-of-4 disagreement is in the in-panel text. The tie symbol is in the key.
- Not visible: "noise level not confirmed (its check failed)", the "no robustness to noise" limit, the 6 further failed checks, and the "no-ramp control" limit.
- The caption says "failed check: the 90 percent rule", but the image title says "FAILED" with no number or threshold on it.
5. Lower-case label starts: yes. "tau_d (ms), cell index j" and "tau_d (ms)" in (c) and (d). The y label "J0 (J at path start)" is fine.

## F5c
1. Could not understand
- a. The opening "Network classes do not reproduce the mean field": the mean-field class is never stated and not drawn in (a), so the reader cannot see what the network fails to reproduce.
- b. "halving the numerical time step must change the network peak frequency ... by less than 2 percent": it reads as the opposite of the intended meaning, which is that it should change little.
- c. "recorded minimum, 1000 ms".
- d. "a seed on the dotted line is not evidence of agreement (the check of this panel failed)".
- e. "the counts 'control flagged in 10 of 10 seeds, ramp runs 10 of 10' come from other network runs, not the controls drawn here": very confusing.
- f. "so onset is not a ramp-specific signal in this figure": the logic is not obvious.
- g. "noise level sigma = 0.0624 (checked, not confirmed; its check failed)".
- h. "ramp seeds ... controls": the sample-size limit "3 control seeds per N is a small sample" is stated, but the roles of "ramp" and "control" are only clear from the legend.
2. Unsupported or contradicted by the image
- Only one: the class mismatch with the mean field is not drawn (see 1a).
- Checks that PASSED: controls in a surge class 0, 2, 1, 1 of 3 and in S-sus 0, 0, 2, 2 of 3; one NS ramp seed at N = 10,000; no S-rel; 39 ramp onsets from 8 to 27 s, all earlier than the dotted line at about 33.7 s; control onsets 10 to 33 s; the grey bar and tick; the dashed 1000 ms line.
3. Internal code or jargon on the image
"S+", "S-rel", "S-abs", "S-sus", "NS", "ramp seed", "no-ramp control seed", "Grey bar and tick: recorded minimum to maximum and median", "Dotted line: matching mean-field run", "Step-halving test not drawn: its runs are not recorded", "step-halving check: FAIL".
4. Claim limits and failed checks
- Supported: the step-halving failure (red title of (b) plus in-panel text "not drawn"). The limit "peak frequencies not shown to be converged" follows from it. The "controls are in surge classes" limit is visible (open marks at S+, S-abs).
- Not visible: "there is no claim of agreement in class" (no mean-field class drawn), the noise-level failed check, and the 4 further failed checks.
5. Lower-case label starts: none found (all labels begin with a capital or a symbol).

## F6
1. Could not understand
- a. "169 non-surge map cells (one parameter pair of a grid of mean-field runs, in two maps ...)": the two maps are never described in this caption.
- b. "failure label a to h": only c is defined in the caption text; the others are in the key.
- c. "every class that depends on the test for damped against non-damped oscillations is provisional".
- d. "the 20 pre-registered runs and 4 P2 comparator runs".
- e. "P3 (P2 plus a common drive, amplitude 0.5, 1, 2)": the drive of what?
- f. "negative control 2 is D-tr at every ramp duration; the failed check is the one on negative control 1": why a D-tr (a surge) for a negative control is not a failure is not explained.
- g. "(120 s points: right of tick 100)": a plotting note.
- h. "negative control 3 (inhibition raised while the mean excitability falls; exploratory)".
- i. "the noisy rows of (b) use it": the noise level, with its failed check, is mentioned only in the limits.
- j. "NS: no rise, the noisy-run counterpart of D-none".
2. Unsupported or contradicted by the image
- a. No contradictions found. I checked: 48 + 32 + 8 + 51 + 1 = 140 for map 1 and 16 + 13 = 29 for map 2, which give 169; the S-rel counts 1 + 1 + 1 + 1 + 2 = 6 of 130; negative control 2 D-tr everywhere; 5 map cells D-none and the network S+ in (c); 24 plotted points; all small markers D-tr.
- b. Omission: the caption says the lines "overlap" in (e), but only 4 of the 6 coincide. P3 drive 2 (about 39 to 40.5 Hz) and P4a (45 Hz) are clearly separate and are not mentioned.
- c. The network parameters in (c) (N = 10,000, Delta = 0.3, tau_d = 5 ms, 120 s) are not shown on the image; the x label just says "Network".
3. Internal code or jargon on the image
"T_ramp", "Negative control 1 / 2 / 3", "mean field, noise (10 seeds)", "D-none", "NS", "D-tr", "S+", "S-rel 1", "a: Delta above critical", "b: tau_d outside window", "c: a flag, not a demonstrated cause", "d: ramp too fast for 10 cycles", "e: no exit (D-sus or S-sus)", "f: amplitude below the fixed threshold", "g: Hopf point, no time inside", "h: rejected by the damped-oscillation test", "(D-tr cells, no label: map 1 760, map 2 296)", "primary / any label", "P2, P3, P4a, P4b", "Small mark: class (D-tr)", "Negative-control check: FAIL".
4. Claim limits and failed checks
- Supported: the failed negative-control check (red title, red S+). The "label c is a flag" limit (the image key says "a flag, not a demonstrated cause", though without saying what is flagged).
- Not visible: "the noise level sigma = 0.0624 is checked and not confirmed", the "no-ramp controls classified into surge classes" limit, the "not evidence of a ramp-driven surge" limit, and the "provisional damped/non-damped test" limit (only label h hints at it).
5. Lower-case label starts: yes. Second lines "mean field, no noise", "drive off", "drive on", "(exploratory)", and the key lines after the letter code, such as "tau_d outside window", "a flag, not ...", "ramp too fast ...", "no exit ...", "amplitude below ...", "rejected by ...". The parenthetical "(text: seeds in another class)" inside a title is lower-case.

## FS1
1. Could not understand
- a. "comparison model M2 (kept as the damped-ring comparison)": M2 and "damped ring" are not explained.
- b. "4 of its 5 replication checks": which five, and which panel shows which check, is not said.
- c. "passes only on our own reading, with its check against the primary source deferred".
- d. "the version of the step test on a network ... was not run (the coupling of an M2 network is unsourced)".
- e. "The root-count boundary lies within one cell of the formula fold at half spacing for 20 of 20 r values (not drawn), 18 of 20 at base spacing ... the two cusp points need half spacing": "r values" and "half spacing" are opaque.
- f. "the test point (-5, 15) has a saddle, a stable focus and a stable node (not drawn)".
- g. "the step response rings at the linearised frequency and decays to 2.1e-4 and 6.1e-3 relative": it reads as if the signal decays to those values; it is really a fit-versus-linearised difference.
- h. "No stable focus on the grid is non-damped (0 of 25727; the linearised rate has standard error 0)".
- i. "the largest cycles per e-fold inside the 25 to 100 Hz band is 5.1".
- j. "the focus is damped by construction (the ring rate is the linearised rate, not a fit to simulated rings)".
2. Unsupported or contradicted by the image
- a. (d): "the fitted frequency and decay rate differ from the linearised ones by 2.1e-4 and 6.1e-3 relative": the image shows only the trace, the dashed focus value and the fit-window lines. There is no fitted curve and no numbers.
- b. (b): the caption says "grey: no focus" but the image legend says "Grey: no focus in the band". (b) has no band, and in (c) the grey also covers the region above 100 Hz, which the caption does not say.
- c. "0.24 to 153.4 Hz" in (b): the lower end cannot be read (colourbar ticks 20 to 140). "Ring frequency" on the bar versus "stable focus" in the title is unmatched.
- d. "passes 4 of its 5 replication checks" and "the 5th ... passes only on our own reading": the image states only "Own reading of this test, not verified". There is no pass criterion or threshold in any panel, and the forced response in (e) looks like strongly nonlinear bursts once per cycle.
- e. The test point sits on the boundary of the grey (no-focus) region in (b) and (c). In (c) its colour is dark blue (about 1 cycle per e-fold or less), while (d) shows about 15 visible cycles decaying by roughly e every 3 cycles. I could not reconcile these by eye; they may not be consistent.
3. Internal code or jargon on the image
"J/√Δ", "η̄/Δ", "Ring frequency (Hz)", "Cycles per e-fold", "Fold formula, two branches", "Cusp, formula", "One / Three fixed points (grid node)", "Test point (−5, 15)", "Grey: no focus in the band", "Fit window start and end", "Focus value of r", "Recorded r(t), forced", "Forcing I(t)", "Own reading of this test, not verified".
4. Claim limits and failed checks
- The caption says no panel has a red title and none does ✓.
- Supported: "own reading, not verified" (in the image); the "M2 is the comparison model" limit (only in the caption).
- Not visible: the root-count checks (marked not drawn), the saddle and node (not drawn), "0 of 25727", the network step test (not run), the deferred primary-source check, and any "damped by construction" evidence.
5. Lower-case label starts: yes. "r (firing rate)" in (d) and (e).

## COUNTS (items under 1, 2, 3)
F1: 9, 7, 11
F2: 9, 5, 5
F3: 8, 2 (omissions only, no contradiction), 11
F5: 10, 2 (no contradiction), 12
F5c: 8, 1, 6
F6: 10, 3, 14
FS1: 10, 5, 14

Lower-case label start (item 5): yes in F1, F2, F3, F5, F6 and FS1; none in F5c.
