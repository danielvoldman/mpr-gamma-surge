# 13t-7: fresh-subagent review of the recorded build from df8d8feb (word for word as received; the harness indentation of the hand-back is removed)

Brief given: read each caption alone, as a reader who has never seen the project, with the image next to it (full image and four quadrant crops; tall figures also the four quarter-height crops); list every term or sentence not understood, every statement the image does not support, every text on an image that looks like an internal code; check every claim limit and failed check against the image; say whether any label starts with a lower-case word; say explicitly whether the caption sentence matches the panel for F1 (i) (j) (k), F3 (e), F5c (b) (c) (d), F6 label c and (e), FS1 (b) to (e). Seven figures: F1, F3, F5c, F6, FS1, FS2, FS3. Report only.

REVIEW OF SEVEN JOURNAL FIGURES (F1, F3, F5c, F6, FS1, FS2, FS3). I edited nothing and wrote no project files. Crops are in the scratchpad folder c\ (scratchpad = C:\Users\Alpha\AppData\Local\Temp\claude\cda12b280d989da8\2a8d4107-463e-4d0b-890e-b96f92d3b858\scratchpad). I read only the 7 PNGs and 7 caption files.

Coverage note: for F1, F3, F5c, F6 and FS1 I viewed the full image plus four quadrants. For FS2 and FS3 I viewed the full image plus four quarter-height strips (each 1800 px wide and fully legible). I did NOT view the four quadrant crops of FS2 and FS3.

==================================================
F1
==================================================
1. Terms or sentences I could not understand:
 1. "first crossing of its detection threshold": the threshold of what is never said.
 2. "classifier window 2 s, step 1 s": a window of what, and a step of what, is not explained.
 3. "Delta = 0.3", "tau_d", "membrane time constant 10 ms", "J = -21": "heterogeneity" and "coupling" are named, but nothing says what they do.
 4. "noise level sigma = 0.0624 (checked, not confirmed; its check failed)": which noise, applied where, is not said.
 5. "1 of 4 map cells (one parameter pair of a grid of mean-field runs; not drawn here) agree": which cells, and agree on what?
 6. "0 of 3 seeds agree at ramp durations of 10 s and 120 s (the 10 s ramp is not drawn here)": the check cannot be followed from this figure.
 7. "7 further failed checks of the project are not shown": no content given.
 8. "network surge classes at N = 10,000 are not evidence of a ramp-driven surge (control flagged in 10 of 10 seeds, ramp runs 10 of 10; other network runs, not drawn)": I cannot tell what is claimed.
 9. "All earlier failures and limits stand": undefined.
 10. The opening says the network "does not reproduce it". Three sentences later "the network envelopes ... look similar" and "no claim is made about the visual shape". It reads as self-contradictory until you realise the failure is only about the class label.
 11. "its onset ... is 12.0 s for the network" while the network image shows nothing happening at 12 s. The caption does not say why the classifier fires there.
2. Statements the image does not support or contradicts:
 1. "the network ... does not reproduce it": in (d) and (f) the network envelope has the same shape as the mean field in (c) and (e). The surge visibly starts earlier, at about 50 s, than the mean-field onset at 58.7 s. Only the class label differs. The caption concedes this later.
 2. (i): "the rows are not labelled" while the y axis reads "Neuron (row)" with ticks 0 and 250. This is ambiguous; the rows are numbered but carry no neuron identity.
 3. (j) and (k): "The spikes ... in 1 s windows". They appear as a dense dark band with a trace-like lower edge. Individual spikes cannot be resolved. (k) does show a clear rhythm, (j) does not.
3. Internal-looking codes on the image: "P2", "M3", "D-tr", "S-sus", "ING", "t_on, T_ramp", "tau_d", "tau", "r, v, s". The titles "R(t)" and "V(t)" use capitals while the axes use lower-case r and v. "post hoc" and "(recorded run)" appear in the legend. There is no check ID or step ID. Total: 10 variable or class codes.
4. Claim limits and failed checks against the image:
 - Visible and supported: red titles "(d) ... FAIL" and "(f) ... FAIL"; panel text "Network class S-sus; mean field D-tr"; legend "Mean-field onset (D-tr, 58.698 s)" and "Network classifier onset (S-sus, 12.0 s; the 3 seeds coincide)"; "N = 10,000" and "300 neurons" (axis 0 to ~300); ramp 5 to ~125 s in (a) (the J ramp in (b) runs ~35 s to ~155 s, which fits "after a delay"); dashed 25 and 100 Hz lines in (g) and (h).
 - Stated but not visible: peak 49.0 Hz (caption says not drawn); 0 of 3 seeds at 10 s and 120 s; 1 of 4 map cells; the 7 further failed checks; the sigma check failure; "control flagged in 10 of 10, ramp runs 10 of 10".
5. Lower-case-initial labels: "spike raster" (Network box) and "spectrogram of v" (Outputs box) start with a lower-case word. "t_on, T_ramp: ramp ..." and "r, v, s: ..." start with symbols, which are excepted. All other labels are capitalised.
Panel (i): matches. Orange solid line at ~12 s, orange dashed line at ~58.7 s, 1 s bins ("Spikes per 1 s"), 300 rows.
Panel (j): matches. The title "12.000 to 13.000 s" and the solid orange frame are as described.
Panel (k): matches. The title "58.698 to 59.698 s" and the dashed orange frame are as described. The caption says nothing about what is seen (k shows a clear rhythm, j does not).

==================================================
F3
==================================================
1. Terms or sentences I could not understand:
 1. "cycle branch" and "the last recorded eta_bar of its cycle branch; the reason is not recorded".
 2. "values from the analysis record listed in the supplement".
 3. "path leg" and "common drive".
 4. "The paths coincide in (c) and (d) because they differ in J, drive or time course, which these planes do not show": garbled.
 5. "no classifier ... or spectrogram ... is used": odd to state in a figure with no classifier.
 6. "peak frequencies are spectral peaks"; "the gamma-band result is stated for model M3 only".
 7. "membrane time constant 10 ms".
 8. "7, 6 and 3 of 9 slices have one, as recorded".
 9. "All earlier failures and limits stand".
2. Statements the image contradicts or does not support:
 1. "The paths coincide in (c) and (d)": in (d), P4a (pink, Delta up) and P4b (olive, Delta down) clearly do not coincide with the other paths. The caption itself says in the same sentence that they are separate.
 (Everything else I tested holds; see 4 below.)
3. Codes on the image: "P1", "P2", "P3", "P4a", "P4b", "P5", "tau_d", "J -21", "(recorded)". No check ID. Total: 8.
4. Claims against the image:
 - Visible and supported: the red "frequency check: FAIL" titles on (a), (b), (c); the colour-bar title "Differ by 4.391 Hz; allowed 0.5 Hz"; ticks at ~44.6 and 49.0 Hz.
 - 25 Hz bars: 7, 6 and 3 slices in (a), (b), (c) respectively. This matches "7, 6 and 3 of 9".
 - Bands ending before 8.0: 5 in (a), 3 in (b), 0 in (c) = 8. This matches "8 of the 27".
 - 9 slices per panel: matches.
 - Hopf curve in (c) is kinked (straight segments): matches.
 - Grey open circle at ~1.4, dark ring at ~2.9 on the 5 ms row: matches.
 - Not visible: 44.609 and 49.0 as printed numbers, membrane time constant, "no other failed check", the limits sentence.
5. Lower-case-initial labels: the second title line "frequency check: FAIL" under each of (a), (b), (c) starts with a lower-case word. Legend continuation lines such as "c: Δ 0.3" are wraps. "tau_d ..." is a symbol.
Panel (e): matches. Seven rows, with P5 split into "P5 up" and "P5 return" (arrow back from 4.9 to 1.4). The rows also carry durations (100 s or 120 s) that the caption does not mention.

==================================================
F5c
==================================================
1. Terms or sentences I could not understand:
 1. "absolute and relative rise": relative to what is not said.
 2. NS is not in the class list; it appears only at the end ("NS (no rise)").
 3. "step-halving check ... its runs are not recorded, so not drawn": the logic is hard to follow.
 4. "Control seeds are drawn only where their value is defined": why a value would be undefined is not said.
 5. "noise level sigma = 0.0624 (checked, not confirmed; its check failed)".
 6. The "10 of 10 ... come from other network runs, not the controls drawn here" clause is confusing.
 7. "4 further failed checks ... Supplement F5c" and "All earlier failures and limits stand".
 8. "coupling J", "heterogeneity Delta", "tau_d", "classifier window 2 s, step 1 s".
 9. "ramp duration 60 s" appears only as a parameter, never in the image.
2. Statements not supported by the image:
 1. The opening "Network classes do not reproduce the mean field": the mean-field classes are not drawn, so the image cannot show this (the caption admits "not drawn").
 (The legend lists S-rel although no marker uses it; this is consistent with "No seed is S-rel".)
3. Codes on the image: "S+", "S-rel", "S-abs", "S-sus", "NS", "N". No check ID. Total: 5 class codes.
4. Claims against the image:
 - Visible and supported:
   - Controls in a surge class "0, 2, 1 and 1 of 3": counted, correct (open S+, open S-abs at 3000; open S+ at 10,000; open S-abs at 30,000).
   - Controls in S-sus "0, 0, 2, 2": correct.
   - Controls drawn in (b), (c): 0, 2, 3, 3. This matches, and none appear in (d).
   - No seed is S-rel: correct.
   - One ramp seed at N = 10,000 is NS (filled grey): correct.
   - 39 drawn ramp onsets between 8 and ~27 s, all below the dotted line at ~33.7 s: correct.
   - Control onsets from ~10 to ~33 s: correct.
   - Dashed floor at 1000 ms in (d): correct.
   - Red title of (b) "step-halving check: FAIL" and the in-panel note "Step-halving test not drawn: its runs are not recorded": correct.
 - Stated but not visible: mean-field onset 33.698 s as a number (only the dotted line is seen), the 1000 ms value, all parameters, "4 further failed checks", the limits.
5. Lower-case-initial labels: none (class names and symbols excepted).
Panels (b), (c), (d):
 - (b) matches: grey bar and tick for range and median, dotted mean-field line at ~49 Hz, red title.
 - (c) matches: dotted line at ~33.7 s.
 - (d) matches: log axis, dashed line at 1000 ms. The caption says the grey bar and tick show "range and median of the ramp seeds", and that is what is drawn.

==================================================
F6
==================================================
1. Terms or sentences I could not understand:
 1. "169 non-surge cells ... in two maps": what the two maps are.
 2. "non-surge: not D-tr"; "D-none (no episode)".
 3. "pre-registered runs" and "P2 comparator runs".
 4. "classifier window ... shorter ramps use a shorter window".
 5. "every class that depends on the test for damped against non-damped oscillations is provisional".
 6. "noise level sigma = 0.0624 is checked and not confirmed".
 7. "failure label c is a flag, not a demonstrated cause (below 25 Hz; it marks a cell without a surge class whose frequency is below 25 Hz)": acceptable but dense.
 8. "negative control 3 (inhibition raised while the mean excitability falls; exploratory)": the image only says "(exploratory)".
 9. "All earlier failures and limits stand".
 10. "primary label (the first that applies)" versus the hatched or dotted "any label" bars: the caption never says hatched = Map 1 and dotted = Map 2 (the legend does).
2. Statements not supported by the image:
 1. Mild: (c) caption says "NS (no surge) is expected", while the panel y label says "Expected: no surge class". The caption's "NS" is not shown for the network row.
 (No hard contradiction found.)
3. Codes on the image: classes "D-none", "D-tr", "D-sus", "S-sus", "S-rel", "NS", "S+" (7); failure labels "a" to "h" (8); "P2", "P3", "P4a", "P4b" (4); "T_ramp", "tau_d", "Map 1/Map 2". No check ID. Total: about 21.
4. Claims against the image:
 - Visible and supported:
   - Failure-label counts sum to 169 (map 1 primary 140, map 2 primary 29).
   - 13 T_ramp values (1 to 1000 s).
   - S-rel counts 1, 1, 1, 1, 2 = 6 of 130 runs.
   - Negative control 2 is D-tr everywhere.
   - (c): 5 map-cell diamonds (D-none) and one red S+ network circle; red title "Negative-control check: FAIL".
   - (d), (e): 6 series by 4 points = 24 points; ticks 10, 30, 100, 300 with the "120 s" points right of 100; P3 drive 2 near 39, 40, 40.5, 40.5 Hz; P4a at 45 Hz; the other four lines overlap at ~48 to 49.5 Hz; all marked D-tr.
 - Stated but not visible: "1 seed", N = 10,000 for the network run, exact peak-frequency decimals, amplitude 0.5/1/2 (legend shows drive 0.5, 1, 2: visible), all parameters, the limits, "no other failed check".
5. Lower-case-initial labels: yes. In the label key: "c: a flag ...", "d: ramp too fast ...", "e: no exit ...", "f: amplitude below ...", "h: rejected ..." (after the letter). Also second lines "mean field, no noise", "mean field, noise (10 seeds)", "drive off", "drive on". "b: tau_d ..." starts with a symbol.
Label c: matches. The key says "c: a flag, not a demonstrated cause (below 25 Hz)" and the bar shows 32 for map 1 only, primary and any.
Panel (e): matches. Overlap of four lines near 48 to 49.5 Hz, P3 drive 2 lower, P4a at 45 Hz.

==================================================
FS1
==================================================
1. Terms or sentences I could not understand:
 1. "damped-ring comparison", "ring rate" and "ring-map file": "ring" is never defined in the caption. The colour bar says "Ring frequency", while the caption says "focus".
 2. "root-count boundary lies within one cell of the formula fold at half spacing for 20 of 20 r values ... 18 of 20 at base spacing (the two cusp points need half spacing)".
 3. "the test point has a saddle, a stable focus and a stable node (not drawn)".
 4. "the step response rings at the linearised frequency and decays to 2.1e-4 and 6.1e-3 relative": what decays, to what?
 5. "linearised rate has standard error 0".
 6. "the version of the step test on a network ... was not run (the coupling of an M2 network is unsourced)".
 7. "replication checks"; "check against the primary source deferred".
 8. "Panels (c) and (d) are drawn at different parameter values": unexplained; (c) is a map and (d) is a single point.
 9. "input drive of 0 and an input amplitude of 0 (the ring-map file itself stores no input current)".
2. Statements not supported by the image or contradicting it:
 1. First paragraph says the step response "decays to 2.1e-4 and 6.1e-3 relative", but the (d) sentence says the fitted frequency and decay rate "differ ... by 2.1e-4 and 6.1e-3". The image (d) shows the response decaying towards the focus value (dashed ~1.37). The two sentences are inconsistent.
 2. Hedged: by eye in (d), the ringing amplitude drops by about 0.7 per cycle, so roughly 3 cycles per e-fold. At the test point in (c) the colour is dark blue (well under 1). The caption's "different parameter values" remark may be the explanation, but a reader cannot check it.
3. Codes on the image: none are check or step IDs. Symbols: "J/√Δ", "η̄/Δ", "r", "I(t)", "e-fold". Total IDs: 0.
4. Claims against the image:
 - Visible and supported:
   - "No panel has a red title": true, no red.
   - Axes -10 to 2 and 0 to 20.
   - (b) colour bar spans about 0 to 153 Hz.
   - (c) maximum about 5.1 (yellow).
   - Test point (-5, 15) drawn in all four map panels.
   - The (e) forcing is ±3 amplitude with period 400 ms (peaks at ~100, 500, 900 ms).
   - Annotation "Own reading of this test, not verified" present.
 - Stated but not visible: 4 of 5 checks passed, 20 of 20 and 18 of 20, 0 of 25727, "2.1e-4" and "6.1e-3", grid sizes 241 and 201, the "step amplitude 3" (not on the image), the deferred check.
5. Lower-case-initial labels: none except symbols (r, J/√Δ, η̄/Δ).
Panels (b) to (e):
 - (b) matches. "Frequency of the stable focus", grey = no focus, 0.24 to 153.4 Hz consistent with the colour bar.
 - (c) matches. Cycles per e-fold in the band, max 5.1.
 - (d) matches. Recorded step response of r with a fit window (the caption does not mention the two vertical orange fit-window lines).
 - (e) matches. Sinusoidal current below, response r above (strongly non-sinusoidal bursts), annotation present.

==================================================
FS2
==================================================
1. Terms or sentences I could not understand:
 1. "published Hopf point", "recorded departure", "a failed check".
 2. "straight-line fit of the squared amplitude ... residual of 2.42 percent against 2 percent allowed", "R2 0.99691".
 3. "as worded" and "the source is a single one and our reading is not verified".
 4. "existence checks", "validation point 1 and 2" (defined only in the key block).
 5. "the largest ratio of the heterogeneity Delta to the mean excitability eta_bar on the Hopf curve (0.14531 ...)": what the ratio means is never said.
 6. "ratio of the oscillation frequency to the linearised one".
 7. (j) "−J at the Hopf point" (0.0005 to 0.005) versus J = -20 elsewhere: confusing.
 8. "exploratory fit ... chosen after the results".
 9. Codes in the caption text: K7, K10, RB1, G7, D24, G4, "the six limits set when gate G4 was triggered", "ruled for the map, control and perturbation runs".
 10. "control runs ... are runs of the project that are not drawn in this figure".
 11. "No row of the project's table of failed checks concerns this figure (our reading ...)".
2. Statements not supported by the image:
 1. (a) "up and down sweeps": one black curve is drawn and the two sweeps are not distinguishable.
 2. (h): "the cells at 3 ms and 50 ms have no mean-field oscillation, so their differences are undefined and not drawn". The "Mean of r" circle IS drawn at both of these cells (at ~0). Only frequency and amplitude are absent there. The sentence overstates.
 3. (c) to (g): "N = 50,000 as a third line at point 2 with 5 ms": in (f) I cannot see a distinguishable third line. The legend sample is a very faint dotted line.
3. Codes on the image: "Point 1", "Point 2", "tau_d", "N", "J", "Delta/η̄", "FAIL". No ID on the image. In the caption: K7, K10, RB1, G7, D24, G4 (6).
4. Claims against the image:
 - Visible and supported:
   - Red titles "(b) Amplitude squared: FAIL" and "(l) Frequency against J: FAIL".
   - Hopf 4.1209 ms and published 4.95 ms lines in (a).
   - Legend "residual 2.42 percent (2 allowed)" and "residual 0.22 percent" (exploratory).
   - (l) legend 13.4, 25.0 and 42.2 percent against limit 10.
   - (h) tolerance ±5 percent dashed.
   - (i) ratio ~0.1453 inside the grey band ±0.002.
   - (j) band 1 ± 0.01, with note "18 of 20 marks overlap".
   - (k) dashed lines at ~4.5 and ~33 Hz (5 and 30 widened by 10 percent).
   - Mean-field points at 3, 4.95 and 8 ms in (a).
 - Not visible: R2, the 0.09 percent figure, 1.7e-15, 0.00071, "each network run is a single run", gate G7 and RB1 limits.
5. Lower-case-initial labels: only symbol-led ones ("r, last 400 ms", "tau_d ..."). None otherwise.

==================================================
FS3
==================================================
1. Terms or sentences I could not understand:
 1. "reference run" versus "main example" versus "Headline": three names for apparently the same run.
 2. "noisy grid agrees with the noise-free map in 97 of 225 cells", "noisy subgrid", "map cells ... 30 x 30".
 3. "NOT EVALUABLE", "claim limit, not a result".
 4. "finite size", "the rule that the surge classes are no fewer at 30,000 than at 10,000 passes".
 5. "Lorentzian / Gaussian / uniform heterogeneity".
 6. "D-tr", "D-none" and "mode N".
 7. "Stored (in plain words: recorded) ... a value that is recomputed here is said so where it occurs".
 8. Codes: RB1, RB2, RB6, RB8, D24, G4, G7 and "headline_class_kept_1.0_sigma".
 9. "frozen criteria".
 10. "short windows give false surges (306, 400, 172 and 24 of 500 white-noise records at window lengths ...)".
 11. "pure trend plus noise".
 12. "controls ... reach 7 of 10 at every sigma" (these are mean-field controls; the first paragraph does not say so).
2. Statements not supported by the image:
 1. (e): "for the 120 s bars the words PASS or FAIL and the dashed line (8 of 10 seeds needed) show the check". Only the ×0.5 and ×1 groups carry PASS and FAIL and the dashed line. The ×2 120 s bar (8 seeds) has neither.
 2. (a): "the bold number above a bar": the control labels (0/3, 2/3, 1/3, 1/3) are drawn grey and lighter, not bold. Minor.
3. Codes on the image: "S+", "S-rel", "S-abs", "S-sus", "NS", "T_ramp". No ID on the image. In the caption: RB1, RB2, RB6, RB8, D24, G4, G7, headline_class_kept_1.0_sigma (8).
4. Claims against the image:
 - Visible and supported:
   - 4/10, 7/10, 2/10, 5/10 (ramp) and 0/3, 2/3, 1/3, 1/3 (controls).
   - Lorentzian row S-sus, S-abs, S-sus; Gaussian and uniform rows S-abs ×3; no-ramp row S+, S-sus, S-sus.
   - (d) title is not red ("not evaluable").
   - (e) red title; 120 s counts 8 (×0.5) and 7 (×1); dashed line at 0.8; "FAIL" at ×1.
   - (f) 7, 7, 7.
   - (g) red title "90 percent rule: FAILED"; bar "97 of 225"; dashed line ~203.
   - The note block states ramp 60 s for (a) to (d) and mean-field runs for (e) and (f): matches.
 - Stated but not visible: 43.1 percent; "10, 10, 9, 10 seeds with a defined value"; the six RB1 and RB2 failed-check list (only 2 red titles, the rest explicitly not drawn); gate G7, RB6, RB8; the white-noise counts; "Lorentzian only" limit; sigma value.
5. Lower-case-initial labels: only wrapped lines of the note block ("duration 60 s ...", "noise, 10 seeds each."); all titles and labels begin with capitals or symbols.

==================================================
TOTALS (my counts)
==================================================
| Figure | Item 1: unclear terms/sentences | Item 2: unsupported/contradicted | Item 3: internal codes on image |
|---|---|---|---|
| F1 | 11 | 3 | 10 (+2 case variants R(t), V(t)) |
| F3 | 9 | 1 | 8 |
| F5c | 9 | 1 | 5 |
| F6 | 10 | 1 (mild) | about 21 |
| FS1 | 9 | 2 (1 hedged) | 0 IDs (symbols only) |
| FS2 | 11 | 3 | 0 on image (6 in caption) |
| FS3 | 12 | 2 | 6 on image (8 in caption) |

The three weakest points across the set:
1. FS3's PASS/FAIL claim for all 120 s bars.
2. F3's "paths coincide in (c) and (d)" sentence.
3. FS1's two incompatible statements about the step response.

Smaller points:
- F1's opening sentence and "no claim about visual shape" pull against each other.
- FS2's (h) sentence says the differences are "not drawn" for the 3 ms and 50 ms cells, but the mean-of-r circle is drawn there.
