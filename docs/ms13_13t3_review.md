# 13t-3: fresh-subagent review of the SHORT captions of the recorded build from c39adb1 (word for word as received; the harness indentation of the hand-back is removed)

Brief given: read each SHORT caption alone, as a reader of the journal who has never seen the project, with the image next to it (the full image and four quadrant crops of each, 30 images; the six short captions; nothing else); list every sentence or term you could not understand, every statement the image does not support, every text on an image that looks like an internal code; check every claim limit and every failed check the short caption states against the image; say whether any label starts with a lower-case word. Report only.

Files opened (36, and nothing else): the six caption files (F1_journal_caption.txt, F2_journal_caption.txt, F3_journal_caption.txt, F5_journal_caption.txt, F5c_journal_caption.txt, F6_journal_caption.txt in C:\dev\mpr-gamma-surge\figures\journal\<fig>\) and all 30 PNGs in C:\Users\Alpha\AppData\Local\Temp\claude\cda12b280d989da8\fa5edfc1-7c60-47f5-a439-1264ede3246f\scratchpad\rec\ (F1, F2, F3, F5, F5c and F6, each as _full, _q1, _q2, _q3 and _q4).

# F1

1. Not understood by a new reader:
- "the main example (the run fixed before the analysis as the main case)" is understandable but heavy. "P2" is defined only inline.
- "class D-tr (an episode that ends)" and "S-sus (a rise that does not end)": the class system is opaque, and the caption does not say which classes exist or what "class" means.
- "its power spectrum peaks at 49.0 Hz (not drawn)": it is unclear which spectrum or signal this refers to.
- "its onset (when it first flags the gamma rise) is 12.0 s for the network": "flags" and "classifier" have no stated criterion.
- "triangle = classifier onset, circle, plus, star = first crossing of its detection threshold": "detection threshold" is undefined.
- "network envelopes": "envelope" is never defined, and the grey fill and min/max lines are not explained.
- "(j) and (k)": the caption never says what is plotted there (no axis label, no y axis).
- "noise level sigma = 0.0624 (checked, not confirmed; its check failed)": what was checked is unexplained.
- "map cells (one parameter pair of a grid of mean-field runs; not drawn here)" and "1 of 4 map cells agree": the 4 cells are not introduced.
- "7 further failed checks ... Supplement F1": unexplained, and the supplement is not available to the reader.
- "classifier window 2 s, step 1 s".
- "Delta" (heterogeneity) is not defined in the caption. It is "heterogeneity Delta = 0.3" with no meaning given.
- "synaptic decay time tau_d" and "model M3": M3 is defined only as "the mean-field model", and the image box says M3 is the all-to-all, Lorentzian-heterogeneity model.
- "control flagged in 10 of 10 seeds, ramp runs 10 of 10; other network runs, not drawn": the data behind this are not visible.

2. Unsupported or contradicted:
- "its onset ... is 12.0 s for the network": the strip shows the triangle at 12 s, but the network r(t) and v(t) envelopes in (d) and (f) are flat until about 50 s. Panel (j) at 12 s shows no visible oscillation, and the raw first crossing is about 50.2 to 50.9 s. The caption does not reconcile this, and the image does not support a visible gamma rise at 12 s.
- "(c), (e) Rate r and mean potential v": the panel titles say "R(t)" and "V(t)" (capitals), and the strip titles say "R(t), network vs mean field: FAIL". This is a minor mismatch.
- "(d), (f) The 3 network seeds ... same y axes": (d) and (f) show only one visible line (the seeds coincide), and the y axes have no tick labels of their own. This is consistent but not checkable.
- "its power spectrum peaks at 49.0 Hz": the spectrogram (g) shows a band rising from about 28 Hz to about 75 Hz, and the 49 Hz figure is not readable from the image (the caption says "not drawn").
- Everything else (ramp 120 s from about 5 s, J from -21 to 0, MF onset 58.698 s, D-tr ending near 143 s, orange windows at 12 s and 58.7 s, the 25 and 100 Hz dashed lines) matches.

3. Internal codes or jargon on the image:
- "P2: hypoxia-like path"
- "t_on, T_ramp"
- "J, tau_d, tau"
- "M3"
- "inhibition-dominated (ING)"
- "r, v, s"
- "D-tr"
- "S-sus"
- "Network class S-sus; mean field D-tr"
- "R(t)", "V(t)"
- "FAIL"
- "post hoc"
- "recorded run"
- "recorded values 50.170 to 50.924 s"
- "Event marks ... height has no meaning"
- "model units"
- "Neuron (row)"
- "tau_d"

4. Claim limits and failed checks versus the image:
- The caption states the failed check and the limits (no-ramp controls classified as surges, S-sus in all seeds, noise sigma failed) clearly.
- The red "FAIL" titles and the "Network class S-sus; mean field D-tr" boxes in (d) and (f) support the failed check.
- The caption explicitly warns that the envelopes look similar.
- Missing: the classifier network onset at 12 s precedes any visible rise in the plotted traces, so a reader may over-read or dismiss the onset marker. Nothing on the image says why the onset is so early (the caption limits mention controls, but only as "not evidence of a ramp-driven surge").
- The 3 seeds are said to agree, but only seed 0 is visible.
- The mean-field spectral peak at 49 Hz and the "58.698 s" onset are not tied to anything readable except the legend.
- Lower-case start of labels: yes. "inhibition-dominated (ING)", "spike raster", "spectrogram of v" (box lines), and the wrapped continuation lines "mean potential, synapse" and "network r(t), v(t)" start lower-case. Also "J, tau_d, tau" and "t_on, T_ramp: ramp start and duration" begin with symbols (excluded).

# F2

1. Not understood:
- "Hopf point (where the resting state starts to oscillate)" is acceptable.
- "supercritical bifurcation (the oscillation grows smoothly ...)" is acceptable.
- "limit cycle" is not defined.
- "sweeps (in a sweep eta_bar is raised step by step ... each step lasting 2 s)": whether the up and down sweep is a hysteresis test is not stated.
- "hollow caret (down)": the symbol is not clearly visible.
- "1.2e-3 relative from 0.2 above the Hopf point".
- "the steps within 0.1 of the Hopf point are still relaxing" (the term "relaxing" is undefined).
- "network's v is the mean over the neurons that are not refractory, a different definition": "refractory" is jargon.
- "ramp durations of 10 s and 120 s, at 4 map cells ... and overall; all four checks failed": the ramp, the map cells and the classes are not defined here, and the caption says they are not drawn.
- "Supplement F2".
- "no agreement criterion is applied to the amplitude comparison (information only)".

2. Unsupported or contradicted:
- "the network ... does not follow the mean-field branch closely": in (a) and (b) the network squares and diamonds lie almost on the mean-field cycle. The difference is at most 13 percent, visible only in (c), and the image gives the opposite visual impression to this opening sentence, except below the Hopf point.
- "the mean field is swept from 0.896 to 6.896 in 61 steps": the mean-field markers do end near 6.9. The network markers run only from 0.9 to 6.5 (15 steps), which the caption does not state.
- "(b) ... the mean-field up and down sweeps coincide": supported.
- "(c) above eta_bar 2.996 only": the first point drawn is at about 3.3, and the shaded band covers about 2.8 to 3.0, so the "2.996" limit is not readable.
- "At the Hopf point the network v amplitude is 1.07 and 1.17 against 0.08 and 0.55 for the mean field": the 0.08 and 0.55 are not visible on the image, and the up and down sweeps are not distinguishable there.
- "differs ... by +13.2 to -2.5 percent": supported by (c). "network ... below the Hopf point ... 0.22 to 0.31": supported by (b).
- The grey up/down markers at the Hopf point (values 0.08 and 0.55) cannot be checked.

3. Internal codes or jargon on the image:
- "Hopf point (supercritical), v interpolated"
- "Steps within 0.1 of the Hopf point (still relaxing)"
- "Network N = 10,000"
- "Mean field, down sweep (hollow, smaller)"
- "Fixed point, stable/unstable"
- "FAIL"
- "classes disagree elsewhere (check failed)"
- "Network vs mean field: FAIL"
- "eta_bar" (symbol, fine)

4. Claim limits and failed checks versus the image:
- The caption says the failed check concerns classes that are not drawn, and that this panel compares amplitudes only. The red title of (c) sits on an amplitude panel and the text inside it says so. This is stated clearly.
- It is also stated that "No other failed check is about this figure".
- Missing: a reader could over-read the near-coincidence of network and mean field in (a) and (b) as agreement. The caption gives the limits (single runs, no error bars, M3 only, no robustness claim) but the opening sentence says the opposite of what (a) and (b) look like.
- The network points sit on the mean-field branch except for the 13 percent bias near the threshold.
- Lower-case start of labels: none. Everything starts with an upper-case word or a symbol (v, eta_bar). The y label "v amplitude (max - min)" begins with a symbol.

# F3

1. Not understood:
- "spectral peak (the peak of the power spectrum of the simulated signal)": which signal and which run are not clear to a new reader.
- "cycle frequency (the frequency of the oscillation that starts at the Hopf point ...)".
- "values from the analysis record listed in the supplement".
- "Each band is one slice (one fixed tau_d)": acceptable, but what the bar's right end means is not explained. In (a) to (c) bars for small tau_d stop at eta_bar 4.7 to 7.8, and the bar start and end meaning is not stated.
- "a black bar marks where the cycle crosses 25 Hz and is absent where it never does (7, 6 and 3 of 9 slices have one, as recorded)".
- "the Hopf curve, straight segments between recorded points".
- "paths P1 ... P5": P1 to P5 and the "path start" circle are explained only inline.
- "P5 (up, then back) drawn as one arrow because their eta_bar, Delta and tau_d are equal; P4a, P4b".
- "The paths coincide in (c) and (d) because they differ in J, drive or time course, which these planes do not show": the logic is confusing.
- "no classifier ... or spectrogram ... is used".
- "gamma-band result is stated for model M3 only".
- "frequency check (the two frequencies below must differ by at most 0.5 Hz)" is clear.

2. Unsupported or contradicted:
- "(7, 6 and 3 of 9 slices have one)": I counted 7, 6 and 3 ticks, so this is supported.
- "P5 ... drawn as one arrow": (c) shows a double-headed arrow and (d) a single right arrow, so the return leg is not visible in (d).
- "a black bar": the marks are thin vertical lines, a minor issue.
- "the grey open circle is the start of the paths (eta_bar 1.396)": the circle is near 1.4, supported.
- "the cycle frequency is 44.609 Hz": the colourbar tick is at about 44.6 and the spectral peak at about 49, supported.
- "(e) One row per path": supported. The path durations (100 s or 120 s) shown on the image are not mentioned in the caption.
- "tau_d = 1 to 50 ms (9 values)": supported.

3. Internal codes or jargon on the image:
- "tau_d (ms), log axis"
- "frequency check: FAIL"
- "Differ by 4.391 Hz; allowed 0.5 Hz"
- "Cycle frequency, main example"
- "Spectral peak, main example"
- "Limit-cycle frequency (Hz)"
- "Hopf point of a slice"
- "25 Hz crossing of a slice"
- "Hopf curve (panel c: Δ 0.3, J -21; panel d: J -21, tau_d 5 ms)"
- "P1, P2, P3, P5: identical in η̄, Δ, tau_d (recorded)"
- "P5 return leg"
- "P4a: Δ up", "P4b: Δ down"
- "P3 drive", "P1 η̄ ramp (100 s)"
- "(η̄, Δ) plane"

4. Claim limits and failed checks versus the image:
- The failed frequency check is supported by the red titles and the red "Differ by 4.391 Hz" text.
- The caption says the failed check was made at the main example in (c) and "bears on" (a) and (b).
- Missing: the caption states the limit that peak frequencies are spectral peaks, but does not say what the 25 Hz crossing bars mean in terms of any claim.
- The check is a single comparison, and one difference of 4.39 Hz at one point is easy to over-read as the whole map being wrong or right.
- Lower-case start of labels: yes. The second line of each panel title, "frequency check: FAIL" in (a), (b) and (c), starts lower-case (it is a wrapped title). "tau_d (ms), log axis" starts with a symbol (excluded). "P1 η̄ ramp", "P3 drive" start with codes.

# F5

1. Not understood:
- "map cell (one parameter pair of a 30 x 30 grid of mean-field runs in heterogeneity and synaptic decay time)": long but readable.
- "D-tr (an episode that ends) or D-none (none)".
- "S+: absolute and relative rise, ending; S-rel: relative only; S-abs: absolute only".
- "NS (no rise)": which cells use which class is hard to follow.
- "our reading, not verified".
- "Network cells and matching run: ramp duration 30 s (map: 120 s); no equivalence is claimed".
- "noisy subgrid (map cells re-run with noise, 10 seeds each)", and "tie (plus: no single majority class ...)".
- "90 percent rule: at least 90 percent of the cells must agree": the 90 percent is not justified.
- "a rule chosen after the results (post hoc; no check; dashed frame)".
- "the blank lines through (c) and (d)".
- "(e) Map 2: initial coupling J0 and ramp duration": the caption gives no result for (e), and the reader is not told what (e) shows.
- "classifier ... for ramp durations of 60 s or more (shorter ramps use a shorter window)".
- "noise level sigma = 0.0624 (its check failed)".
- "6 further failed checks ... Supplement F5".
- "203 cells, 90 percent, were needed".
- "no-ramp network controls ... are classified into surge classes".

2. Unsupported or contradicted:
- "the 4 network cells are numbered 1 to 4 here and in (b)": supported.
- "network disagrees at 3 of the 4 cells": supported (cell 1 star, cells 2 to 4 red heptagons).
- Cell 1 agreeing via seeds S-abs, S-abs, S-rel: supported. Cell 2 disagrees because seed 0 is S-sus, supported. Cell 3 disagrees (D-none against S-abs and S-rel seeds), supported. Cell 4 disagrees, supported.
- "97 of 225 (43.1 percent)" and "173 of 225 (76.9 percent)": not countable from the image. Panel (c) looks like a clear majority of circles in its left half and crosses in the right, and panel (d) mostly circles.
- "(c) ... the blank lines through (c) and (d)": supported.
- The legend "Classes of the marks in (b)" includes S+ and NS, which are not used in (b). This is not a contradiction, only unused legend entries.
- Nothing is contradicted.

3. Internal codes or jargon on the image:
- "D-tr (map cell, mean-field class)"
- "D-none"
- "Subgrid cell agrees / disagrees (not a tie) / is a tie (a disagreement by the 90 percent agreement rule)"
- "Δ, cell index i"
- "tau_d (ms), cell index j"
- "Map 1 class (120 s)"
- "Matching mean-field run (30 s)"
- "Network against mean field"
- "(c) 90 percent agreement rule: FAILED"
- "(d) Post-hoc re-scoring of (c)"
- "(e) Map 2, no-noise mean field"
- "J0 (J at path start)"
- "T_ramp (s)"
- "Classes of the marks in (b)": S+, S-rel, S-abs, S-sus, NS, D-tr, D-none
- "Mean field only; network disagrees at 3 of 4 cells"
- "cells: FAIL"
- "Cell 1 to Cell 4"

4. Claim limits and failed checks versus the image:
- The caption states the failed checks (network against mean field at 4 cells, the 90 percent rule), the limits (sigma check failed, no robustness claim, controls classified into surge classes) and that (d) feeds no check. All appear in the image as red titles or the dashed frame.
- Missing: the caption does not say what the sparse green (D-none) cells inside the blue region of (a) mean, or what (e) shows.
- The number of network cells (4, with 3 seeds each) is a small sample, stated but easy to miss.
- The mean field is evaluated at 120 s while the network cells run at 30 s, so (a) overlays cells whose network run is at a different ramp duration. This is stated in the caption (b) but not in (a), where the numbered cells sit on the 120 s map.
- Lower-case start of labels: yes. The wrapped second lines "network vs mean field, cells: FAIL" (a), "rule: FAILED" (c), and "of (c)" (d) start lower-case. The (c) and (d) y label "Δ" and "tau_d (ms), cell index j" start with symbols.

# F5c

1. Not understood:
- "step-halving check failed (halving the numerical time step must change the network peak frequency ... by less than 2 percent; its runs are not recorded, so not drawn)": what "not recorded" means and why the check is cited is unclear.
- "ramp seeds (a simulated network run with the ramp, one per random seed; filled, 10 per N) and controls (the same network without the ramp; open, 3 per N)".
- "Controls in a surge class: 0, 2, 1 and 1 of 3; controls in S-sus: 0, 0, 2 and 2 of 3": readable only with N order.
- "grey bar and tick: range and median".
- "dotted line in (b), (c): the matching mean-field run".
- "dashed line in (d): the smallest duration the classifier can give (recorded minimum, 1000 ms)".
- "In (c), all 39 drawn ramp-seed onsets (8.0 to 27.0 s) are earlier than the mean-field onset (33.698 s)": 39 against 40 seeds is explained only in the limits (one NS seed).
- "a seed on the dotted line is not evidence of agreement".
- "the counts 'control flagged in 10 of 10 seeds, ramp runs 10 of 10' come from other network runs, not the controls drawn here; one ramp seed at N = 10,000 is NS": confusing.
- "3 control seeds per N is a small sample".
- "onset is not a ramp-specific signal".
- "4 further failed checks ... Supplement F5c".
- "ramp duration 60 s".
- "noise level sigma = 0.0624 ... check failed".

2. Unsupported or contradicted:
- Control counts: I counted surge-class controls 0, 2, 1, 1 and S-sus controls 0, 0, 2, 2. Supported.
- "No seed is S-rel": supported (no square drawn).
- "Network classes do not reproduce the mean field": the mean-field class (D-tr) is not drawn in (a), so the image does not itself show a mean-field comparison for class. It does appear in (b) and (c) as dotted lines only.
- "all 39 drawn ramp-seed onsets (8.0 to 27.0 s)": I could confirm a range of about 8 to 27 s and 39 (one NS has none).
- "the controls also flag onsets from 10.0 to 33.0 s": supported (about 10 to 33).
- "one ramp seed at N = 10,000 is NS": supported (one filled grey triangle).
- The peak frequencies cluster at the 49 Hz dotted line for N = 10,000 and N = 1000 (S-sus seeds). The caption says this is not evidence of agreement, supported by the text.
- "dashed line in (d) 1000 ms": supported.
- Nothing is contradicted. The in-panel note "Step-halving test not drawn: its runs are not recorded" matches the caption.

3. Internal codes or jargon on the image:
- "S+, S-rel, S-abs, S-sus, NS"
- "Filled: ramp seed (10 per N)"
- "Open: no-ramp control seed (3 per N)"
- "Grey bar and tick: recorded minimum to maximum and median of the ramp seeds"
- "Dotted line: matching mean-field run"
- "Dashed line: smallest duration the classifier can give (recorded minimum, 1000 ms)"
- "(b) Peak frequency against N, step-halving check: FAIL"
- "Step-halving test not drawn: its runs are not recorded"
- "(a) Network class of every seed against N"
- "(d) Duration against N, log axis"

4. Claim limits and failed checks versus the image:
- The caption states the failed step-halving check, the small control sample, the NS seed, and that onsets are not ramp-specific. All of these are supported by the image.
- Missing: the failed check is about peak frequency, but the "agreement near 49 Hz" at N = 10,000 and 1000 is the thing a reader will over-read. This is warned, but the image has no marker for which seeds came from the failed-convergence runs (all of them did, per the caption).
- The mean-field class (D-tr) is not drawn in (a), so the reader must trust the caption.
- Lower-case start of labels: none. All labels start upper-case ("Filled", "Open", "Grey", "Dotted", "Dashed", "Peak", "Onset", "Duration", "Step-halving").

# F6

1. Not understood:
- "negative control ... (a run in which no surge is expected: here the hypoxia-like path with the mean excitability falling by the same amount)": what "the same amount" refers to is unclear.
- "169 non-surge map cells (one parameter pair of a grid of mean-field runs, in two maps ...)": the two maps are defined in F5, not here.
- "failure label a to h (the labels are listed in the key above panel (a))".
- "primary label (the first that applies)".
- "hatched and dotted bars".
- "negative control 1 without and with noise (10 seeds; text: other-class seeds, S-rel in 6 of 130 runs ...)".
- "NS: no rise, the noisy-run counterpart of D-none (no episode)".
- "negative control 3 (inhibition raised while the mean excitability falls; exploratory)".
- "P2, P3 (P2 plus a common drive, amplitude 0.5, 1, 2), P4a and P4b".
- "The 24 points drawn in (d) and (e) are the 20 pre-registered runs and 4 P2 comparator runs".
- "recorded peak frequencies ... are identical (48.048, 49, 49 and 49.5 Hz)".
- "failure label c (a cell without a surge class whose frequency is below 25 Hz) is a flag, not a demonstrated cause".
- "every class that depends on the test for damped against non-damped oscillations is provisional": the test is not defined.
- "noise level sigma = 0.0624 ... (its check failed; the noisy rows of (b) use it)".
- "the 5 map cells (all D-none, no episode)".

2. Unsupported or contradicted:
- "the key above panel (a)": the key is below the bars of (a), not above. This is a contradiction.
- "(a) ... 169 non-surge cells": the bars add to 169 (Map 1 primary 48+32+8+51+1 = 140, Map 2 primary 16+13 = 29). Supported.
- The (a) title also states "D-tr cells, no label: map 1 760, map 2 296", which the caption does not mention.
- "S-rel in 6 of 130 runs": the labels sum to 1+1+1+1+2 = 6. Supported. 13 ramp durations, supported.
- "negative control 2 is D-tr at every ramp duration": supported. Negative control 3 D-none everywhere (the caption says only "exploratory").
- "(c) ... the network run (red S+)": supported. "5 map cells": supported.
- "24 points drawn in (d) and (e)": 4 + 12 + 4 + 4 = 24, supported.
- "(e) ... P3 (drive 0.5 and 1), P4b and the P2 comparators identical (48.048, 49, 49, 49.5)": supported (orange line 48 to 49.5). But P3 drive 2 (about 39 to 40.5 Hz) and P4a (about 45 Hz) are plotted and not mentioned.
- "at T_ramp 10, 30, 120 and 300 s": the (d) and (e) x axes are labelled 10, 30, 100 and 300 (the tick for 120 s is labelled 100), a small mismatch. In (b) the 100 s column is used, not 120 s.
- The legend in the image says "P2 (filled: 10, 120 s; open: 30, 300 s)" and the caption does not mention filled against open.
- The rows of (b) are labelled "mean field", and there is no network row in (b), so the caption's mention of the network belongs only to (c). This is not stated.

3. Internal codes or jargon on the image:
- Failure labels "a: Delta above critical", "b: tau_d outside window", "c: a flag, not a demonstrated cause", "d: ramp too fast for 10 cycles", "e: no exit (D-sus or S-sus)", "f: amplitude below the fixed threshold", "g: Hopf point, no time inside", "h: rejected by the damped-oscillation test"
- "Map 1, primary", "Map 2, any label", "no label: map 1 760, map 2 296"
- "Negative control 1 mean field, no noise"
- "Negative control 3 (exploratory)"
- "T_ramp (s)"
- "D-none", "NS", "D-tr", "S+", "S-rel"
- "Expected: no surge class"
- "Negative-control check: FAIL"
- "Map cell: Delta, tau_d (ms)"
- "P3, drive 0.5", "P4a", "P4b"
- "P2 (filled: 10, 120 s; open: 30, 300 s)"
- "Small mark: class (D-tr)"

4. Claim limits and failed checks versus the image:
- The failed negative-control check (network S+ where NS is expected) is stated clearly and supported by the red title and the red S+ marker in (c). The caption also says it is a single seed.
- Missing: only one network seed is behind the failed check, and (b) shows no network run, so a reader looking at (b) will see only mean-field rows. A reader could also over-read the clean D-none, D-tr columns of (b) as a pass. The caption says the failed check is negative control 1 (network S+) and that negative control 2 is D-tr in the mean field.
- Label c is a flag, not a cause, and the damped-oscillation-test dependency is stated in the limits, which is good. The caption does not explain what "(exploratory)" means for negative control 3.
- Lower-case start of labels: yes. The key entries in (a) start with the lower-case letters a to h (panel-letter-like, excluded) but also lower-case words: "tau_d outside window", "ramp too fast for 10 cycles", "no exit (D-sus or S-sus)", "amplitude below the fixed threshold", "rejected by the damped-oscillation test", "a flag, not a demonstrated cause". Also "mean field, no noise", "mean field, noise (10 seeds)", "drive off", "drive on" in the (b) row labels (second lines), "(exploratory)", and the "text: seeds in another class" parenthetical.

Counts per figure (items under 1, 2, 3):
F1: 14, 4, 18
F2: 10, 5, 8
F3: 12, 3, 15
F5: 15, 0, 17
F5c: 13, 0, 10
F6: 16, 4, 29
