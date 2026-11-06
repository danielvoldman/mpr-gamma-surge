# 13t-1g: fresh-subagent review of the SHORT captions of the recorded build from bab7055 (word for word as received; the harness indentation of the hand-back is removed)

Brief given: read each SHORT caption alone, as a reader of the journal who has never seen the project, with the image next to it (the full image and four quadrant crops of each, 20 images; the four short captions; nothing else); list every sentence or term you could not understand, every statement the image does not support, every text on an image that looks like an internal code; and (13t-1g addition) check every claim limit and every failed check the short caption states against the image and say if anything a reader needs to avoid over-reading the figure is missing. Report only.

REVIEW OF F1, F3, F5, F5c (SHORT captions)

Files opened: all five images of each figure (F1_full, F1_q1 to q4; F3_full, F3_q1 to q4; F5_full, F5_q1 to q4; F5c_full, F5c_q1 to q4), plus the four short-caption .txt files. That is 20 images. I read small text on the quadrant crops.

=====================================================
F1
=====================================================
(1) Not understood
1. "hypoxia-like path P2 (mean excitability raised and coupling J ramped to 0 after a delay)". The link to hypoxia is not explained. The "delay" is not given.
2. "class D-tr: an episode that ends" and "S-sus (a rise that does not end)". The D- versus S- naming is not explained, and neither is why a mean field and a network get different families of labels.
3. "its onset (when it first flags the gamma rise) is 12.0 s for the network and 58.698 s for the mean field". The ramp starts at 5 s. It is not said why a network onset of 12 s is meaningful.
4. "the failed check concerns the class given by the fixed classifier ... and no claim is made about the visual shape, either way". This is hard to follow, and it sits next to "does not reproduce it".
5. "circle, plus, star = first crossing of its detection threshold". The threshold is never defined.
6. "noise level sigma = 0.0624 (checked, not confirmed; its check failed)". The caption does not say noise of what, in what units, or what "checked, not confirmed" means. The mean field is described as noise-free.
7. "1 of 4 map cells (one parameter pair of a grid of mean-field runs) agree". The grid is not in this figure.
8. "0 of 3 seeds agree at ramp durations of 10 s and 120 s". It is unclear whether this means 0 of 3 at each duration. Only 120 s is shown.
9. "7 further failed checks of the project ... Supplement F1". The reader cannot know what they are.
10. "network surge classes at N = 10,000 are not evidence of a ramp-driven surge (control flagged in 10 of 10 seeds, ramp runs 10 of 10; other network runs, not drawn)". The reasoning and the data are not shown.
11. "All earlier failures and limits stand". The caption does not say earlier than what.
12. "power spectrum peaks at 49.0 Hz (not drawn)". The reader cannot check it.
13. "classifier window 2 s, step 1 s" and "membrane time constant 10 ms". No definition is given and no role is explained.

(2) Caption statements not supported or contradicted by the image
1. "the network ... does not reproduce it" against what the panels show. Network traces (d), (f) and network spectrogram (h) look like the mean-field traces (c), (e), (g). The caption admits this.
2. "labels the network S-sus (a rise that does not end)". In (d) and (f) the network envelope collapses at about 143 s, the same time as the mean field. Visually the rise does end.
3. "onset ... is 12.0 s for the network". The triangle sits at about 12 s, where the traces in (d) and (f) are flat. The network envelope starts to open at about 50 s. Window (j) at 12 to 13 s shows no visible oscillation.
4. "power spectrum peaks at 49.0 Hz". Panel (g) shows ridges that start near 28 Hz and rise to about 45 Hz, plus higher ridges. No 49 Hz mark is drawn.
5. "7 further failed checks", "0 of 3 seeds ... at 10 s and 120 s", "1 of 4 map cells" and "10 of 10" appear nowhere in the image.
6. In the diagram, box "M3" is the parent of both "mean field" and "network". The caption says "model M3 (the mean-field model)".
7. The legend marks the first-crossing symbols "post hoc" and gives 50.170 to 50.924 s. The caption does not say post hoc and does not give these values. The caption calls the crossings "first crossing of its detection threshold", which is a different description.

(3) Internal codes or jargon on the image
"M3"; "ING" and "inhibition-dominated (ING)"; "P2"; "t_on, T_ramp"; "J, tau_d, tau"; "r, v, s: Rate, mean potential, synapse"; "raster"; "all-to-all coupling"; "Lorentzian heterogeneity (Δ)"; "η̄"; "D-tr"; "S-sus"; "recorded run"; "network raw first crossing (post hoc ...)"; "event marks: strips above (d) and (f); height has no meaning"; "FAIL"; "model units"; "power spectral density (dB); same scale for (g) and (h)"; "neuron (row)"; "spikes per 1 s"; "network class S-sus; mean field D-tr".

(4) Limits and failed checks: missing or over-readable
- Supported by the image: the red "FAIL" titles on (d) and (f), and the in-panel text "network class S-sus; mean field D-tr".
- Not shown: the other ramp durations, the map cells, the no-ramp controls and the 10 of 10 counts. A reader cannot see how the limit "no-ramp controls are classified into surge classes" bears on this figure.
- Over-readable: the failure is a class-label mismatch from one classifier. The image shows near-identical shapes. A reader may conclude either that the network reproduces the surge or that it clearly fails. The caption disclaims both.
- Missing on the image: the sigma value, and that the figure covers one parameter set and N = 10,000 only.
- Missing: any statement of how large the onset gap is (12 s versus 58.7 s, with crossings near 50 s) and why the triangle and the crossing marks are far apart.
- Missing: that the network is plotted for 3 seeds that coincide, so there is no spread to judge.
- Missing: how "does not end" can hold when the plotted envelope ends.

=====================================================
F3
=====================================================
(1) Not understood
1. "the two frequencies below must differ by at most 0.5 Hz". It is not said why 0.5 Hz. The check seems to apply to one point (the main example), not to a map.
2. "values from the analysis record listed in the supplement".
3. "cycle frequency (the frequency of the oscillation that starts at the Hopf point ...)". The image colour bar says "limit-cycle frequency". "Hopf curve" and "Hopf point" are explained only in a clause.
4. "Each band is one slice (one fixed tau_d)". "slice" is not otherwise defined.
5. "a black bar marks where the cycle crosses 25 Hz and is absent where it never does (7, 6 and 3 of 9 slices have one, as recorded)". "as recorded" is unclear.
6. "the grey open circle is the start of the paths (eta_bar 1.396)". Paths are only defined later in (d).
7. "P3 (P2 plus a common drive)" and "P5 (up, then back)". "common drive" is not defined.
8. "drawn as one arrow because their eta_bar, Delta and tau_d are equal". The reader cannot tell that P3 differs from P2 in anything the figure shows.
9. "(e) One row per path." The caption does not say what the axis or durations mean.
10. "no classifier ... or spectrogram ... is used". The reader does not know why this is stated.
11. "No other failed check is about this figure; the project's other failed checks are listed in Supplement F3".
12. "peak frequencies are spectral peaks; the gamma-band result is stated for model M3 only". The meaning is unclear.
13. "J = -21" and "model M3 ... with rate, mean potential and a synaptic variable". No meaning is given.

(2) Caption statements not supported or contradicted by the image
1. I checked the slice counts of 7, 6 and 3 of 9 against the bars and they match. The grey circle (1.396), the dark ring and the colour-bar ticks at about 44.6 and 49.0 are consistent. Only "4.391 Hz" is printed on the image. The 49.0 and 44.609 values cannot be read to that precision.
2. "The frequency check ... failed (red titles)". The check concerns the main example at Delta = 0.3, tau_d = 5 ms. The red "frequency check: FAIL" titles are also on (a) Delta = 0.05 and (b) Delta = 0.1, which do not contain the main example. The image therefore over-states where the check failed.
3. The caption does not mention that the arrow in (c) and (d) is double-headed. The P5 return arrow also appears in (e), and the (d) legend has a "P5 return leg" entry.
4. Panel (e) labels give path durations "(100 s)" and "(120 s)". The caption does not mention them. Rows P1 to P5 look identical in (e), so the P2/P3 differences are invisible.

(3) Internal codes or jargon on the image
"frequency check: FAIL"; "differ by 4.391 Hz; allowed 0.5 Hz"; "main example"; "limit-cycle frequency (Hz)"; "Hopf point of a slice"; "25 Hz crossing of a slice"; "Hopf curve (panel c: Δ 0.3, J -21; panel d: J -21, tau_d 5 ms)"; "Hopf point of the main example (Δ 0.3, tau_d 5 ms)"; "P1, P2, P3, P5: identical in η̄, Δ, tau_d (recorded)"; "P5 return leg"; "P4a: Δ up"; "P4b: Δ down"; "P5 up"; "P3 drive"; "P2 hypoxia-like path"; "P1 η̄ ramp"; "(η̄, Δ) plane"; "tau_d"; "η̄".

(4) Limits and failed checks: missing or over-readable
- Supported: the failed frequency check and the 4.391 Hz gap.
- Missing from the image: the 49.0 and 44.609 Hz values, which appear only as unlabelled ticks.
- Missing from the image: the source of the "spectral peak" (a simulated run, not the cycle). A reader will not see why a peak of a signal and a cycle frequency could differ.
- Over-readable: the large colour map and the paths suggest the paths pass through gamma-frequency oscillations. The figure does not say whether the paths enter the oscillatory region or how the frequency along a path compares with the signal.
- Over-readable: the bars end at different eta_bar values, for example in (a) tau_d = 1 and 2 near 4.7 to 4.8, and all bars are cut at 8. This is unexplained in both the caption and the image.
- Missing: the map has only 3 Delta values and 9 tau_d values. The 25 Hz black marks do not say what they mean for the manuscript's gamma band.
- The caption limit "gamma-band result is stated for model M3 only" has no counterpart on the image.

=====================================================
F5
=====================================================
(1) Not understood
1. "The surge result holds for the noise-free mean field only". The reader does not know what "the surge result" is before the definitions that follow.
2. "the network disagrees with it at 3 of the 4 cells tested". It is not said why only 4 cells, or how they were chosen.
3. "the noisy mean field agrees with the noise-free map in 97 of 225 cells (43.1 percent; 203 cells, 90 percent, were needed)". The reader does not know what "agree" means here, or why 225 cells and 90 percent.
4. "map cell (one parameter pair of a 30 x 30 grid of mean-field runs in heterogeneity and synaptic decay time)".
5. "D-tr (an episode that ends) or D-none (none)".
6. "a network cell agrees when all 3 seeds are in a surge class (S+ ..., S-rel ..., S-abs ...) where the mean field is D-tr, or in NS (no rise) where it is D-none (our reading, not verified)". It is dense. The reader cannot tell what "our reading, not verified" refers to.
7. "S-sus ... is not a surge class; cell 1 agrees".
8. "Network cells and matching run: ramp duration 30 s (map: 120 s); no equivalence is claimed". It is not clear why the plot compares a 30 s run with a 120 s map.
9. "(c) Noisy subgrid (map cells re-run with noise, 10 seeds each)". How the subgrid maps onto the 30 x 30 map is not stated.
10. "tie (plus: no single majority class among the 10 seeds of the cell; it counts as a disagreement under the 90 percent rule ...)".
11. "(d) The same cells re-scored by a rule chosen after the results (post hoc; no check; dashed frame)". The rule is not described.
12. "(e) Map 2: initial coupling J0 and ramp duration". The reader does not know what is mapped or what colours mean.
13. "(shorter ramps use a shorter window)".
14. "noise level sigma = 0.0624 (its check failed)".
15. "6 further failed checks of the project ... Supplement F5".
16. "no-ramp network controls ... are classified into surge classes". No controls appear in this figure.
17. "no claim that the regime map is robust to noise". "regime map" is not defined.

(2) Caption statements not supported or contradicted by the image
1. "97 of 225 cells (43.1 percent; 203 cells, 90 percent ...)". No counts or percentages are on the image. The reader cannot verify them from (c).
2. The caption describes a 225-cell subgrid. Panel (c) is drawn as a grid of about 15 x 15 marks with an unexplained gap through the middle (about 7+8 columns and 8+7 rows). The gap is not explained in either place.
3. "no-ramp network controls ... are classified into surge classes". No controls are drawn anywhere in F5, so the image does not support this limit.
4. Panel (a) places the 4 network cells on the 120 s map, while (b) shows they were run at 30 s. The caption notes the mismatch, but the in-panel text "network disagrees at 3 of 4 cells" is not qualified on the image.
5. The caption's "sigma = 0.0624" and "classifier window ... gamma band" do not appear on the image.

(3) Internal codes or jargon on the image
"D-tr (map cell, mean-field class)"; "D-none"; "S+"; "S-rel"; "S-abs"; "S-sus"; "NS"; "classes of the marks in (b)"; "map 1 class (120 s)"; "matching mean-field run (30 s)"; "network against mean field"; "subgrid cell agrees / disagrees (not a tie) / is a tie (a disagreement by the 90 percent agreement rule)"; "cell index i / j"; "map 1, no-noise mean field"; "map 2"; "post-hoc re-scoring of (c)"; "90 percent agreement rule: FAILED" (versus "FAIL" elsewhere); "J0 (J at path start)"; "T_ramp (s)"; "tau_d"; "Δ".

(4) Limits and failed checks: missing or over-readable
- Supported by the image: "network ... 3 of 4 cells" (the markers match), the red titles on (a), (b) and (c), and the dashed frame on (d).
- Over-readable: panel (d), after post-hoc re-scoring, looks almost all green. A reader may take it as a rescue of the result, since the rule is not described.
- Over-readable: the large blue map (a) and map (e) look like a robust regime map, but they are noise-free mean field only. The image title says so, but the limit "no claim that ... robust to noise" is only in the caption.
- Missing: the network evidence is only 4 cells at a different ramp duration (30 s versus 120 s). The comparison is not like for like, and the image does not say how the cells were chosen.
- Missing: the noisy comparison is noisy mean field against noise-free mean field, not against the network. The panel title only says "90 percent agreement rule: FAILED". A reader may think it concerns the network.
- Missing: sigma is not on the image. The "no-ramp controls" limit has no data in the figure.

=====================================================
F5c
=====================================================
(1) Not understood
1. "Network classes do not reproduce the mean field". The mean-field class is never stated in the caption.
2. "the step-halving check failed (halving the numerical time step must change the network peak frequency ... by less than 2 percent; its runs are not recorded, so not drawn)". It is not clear how a check "failed" if its runs are not recorded.
3. "S-sus (a rise that does not end) is not [a surge class]".
4. "ramp seeds (a simulated network run with the ramp, one per random seed; filled, 10 per N) and controls (the same network without the ramp; open, 3 per N)".
5. "Controls in a surge class: 0, 2, 1 and 1 of 3; controls in S-sus: 0, 0, 2 and 2 of 3". What the remaining controls are (NS) is not stated.
6. "(d) duration (how long it flags it ...)" and "the smallest duration the classifier can give (one window, 1000 ms)". Elsewhere the classifier window is said to be 2 s with step 1 s.
7. "grey bar and tick: range and median of the ramp seeds".
8. "network surge classes at N = 10,000 are not evidence of a ramp-driven surge (... come from other network runs, not the controls drawn here ...)". "other network runs" is vague.
9. "one ramp seed at N = 10,000 is NS (no rise), so the drawn ramp seeds are not 10 of 10 in a surge class". It is hard to follow.
10. "noise level sigma = 0.0624 (checked, not confirmed; its check failed)".
11. "4 further failed checks ... Supplement F5c" and "All earlier failures and limits stand".
12. "peak frequency, the peak of its power spectrum". Of which signal is not said.

(2) Caption statements not supported or contradicted by the image
1. "Network classes do not reproduce the mean field". The mean-field class is not drawn in (a), so the class mismatch cannot be seen. Only the dotted lines in (b) and (c) show the mean field.
2. "dashed line in (d): the smallest duration the classifier can give (one window, 1000 ms)". The image legend says "recorded minimum duration, (d)". These are different statements.
3. I checked these against the image and they match: the control counts (0, 2, 1, 1 surge; 0, 0, 2, 2 S-sus), 10 filled and 3 open per N, and one NS ramp seed at N = 10,000.
4. In (b), many S-sus ramp seeds sit on the dotted 49 Hz line at all N. This is visually close agreement. It is at odds with the opening "do not reproduce". The caption does say "no claim of agreement in peak frequency".

(3) Internal codes or jargon on the image
"S+"; "S-rel"; "S-abs"; "S-sus"; "NS"; "filled: ramp seed (10 per N)"; "open: no-ramp control seed (3 per N)"; "grey bar and tick: recorded minimum to maximum and median of the ramp seeds"; "dotted line: matching mean-field run, (b) and (c)"; "dashed line: recorded minimum duration, (d)"; "(a) network class of every seed against N"; "step-halving check: FAIL"; "step-halving test not drawn: its runs are not recorded"; "onset (s)"; "duration (ms)"; "peak frequency (Hz)"; "N = 1000 ... 30,000".

(4) Limits and failed checks: missing or over-readable
- Supported by the image: the step-halving failure (red title plus in-plot note), the control counts, and the dotted mean-field lines.
- Over-readable: panel (b). Because step-halving failed, the peak frequencies are not trustworthy. Yet many seeds line up on 49 Hz, and the caption does not warn the reader against reading this as agreement.
- Over-readable: panel (a). The S+ cluster at N = 3000 (6 of 10 filled) looks like a clean ramp-driven surge. The same panel shows an open S+ control at N = 3000, and another at N = 10,000.
- Missing: NS seeds have no onset, frequency or duration, so they vanish from (b) to (d). The caption does not say so.
- Missing: the values at 1,000 ms in (d) are floor values (a single window), not measured durations. The image legend says so but the caption's wording differs.
- Missing: network onsets in (c) (about 8 to 33 s) are all earlier than the mean-field onset (about 33.7 s), apart from some N = 30,000 controls. Neither the caption nor the image comments on this.
- The N = 10,000 "10 of 10" counts are not drawn, so the image cannot verify them.
- Only one ramp duration (60 s) and one parameter set are shown. The horizontal positions within each N are jitter and carry no meaning. This is not stated.

=====================================================
COUNTS (items under each heading)
=====================================================
F1:  (1) 13 | (2) 7 | (3) 20 | (4) 6
F3:  (1) 13 | (2) 4 | (3) 19 | (4) 6
F5:  (1) 17 | (2) 5 | (3) 17 | (4) 6
F5c: (1) 12 | (2) 4 | (3) 16 | (4) 7
