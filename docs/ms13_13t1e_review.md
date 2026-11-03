# 13t-1e: fresh-subagent review of the SHORT captions of the recorded build from cf92272 (word for word as received; the harness indentation of the hand-back is removed)

Brief given: read each SHORT caption alone, as a reader of the journal who has never seen the project, with the image next to it; list every sentence or term you could not understand, every statement the image does not support, and every text on an image that looks like an internal code. Report only.

REVIEW OF SHORT CAPTIONS (reader view, 1e). All four figures and crops were viewed. Only problems are listed.

=====================================================
F1
=====================================================
(1) Could not understand
- "mean-field class D-tr (a transient surge; all are S-sus, a surge without end)". The classes D-tr and S-sus are named but the full class scheme is never given. A reader cannot tell what "mean-field class" means or how "surge" is defined. "Surge" itself is never defined.
- "the main example run" and "N = 1e4 neurons", "mean-field result". The model is not named in the caption. The image only says "M3" in a box, with no explanation of why it is called M3.
- "spectral peak of 49.0 Hz". The peak is of which signal, and how was it estimated? Nothing on the image shows a 49.0 Hz marker.
- "the network classifier onset is 12.0 s (no claim on the shape of the traces)". What the classifier is, what "onset" means, and what "no claim on the shape" means are all unclear. I cannot reconcile it with panels (d) and (f).
- "event times above (triangle: classifier onset; circle, plus, star: first crossings)". Which threshold is crossed? What is "first crossing"?
- "(i)-(k) Spike counts of seed 0 and spikes in two windows". It is not clear what the rows are in (i), or what the dense black traces in (j) and (k) show.
- "The red titles of (d) and (f) mark the failed check". What the check tests is not said.
- The whole "Failed checks" list is not understandable on its own: "network against mean field (0 of 3 seeds at 10 s and at 120 s; 1 of 4 map cells agree)", "negative-control check not passed (control path in class S+)", "step-halving check of the network peak frequency", "two solvers' onsets differ by 181 ms (1 ms allowed)", "main-run class kept in 7 of 10 noisy seeds (8 needed)", "noise-level check", "onset prediction (0 of 6 runs)", "delay under a noise floor". Terms with no explanation: "10 s and 120 s", "map cells", "control path", "step-halving", "two solvers", "noisy seeds", "noise floor", "delay", "onset prediction". "Map cells" are not part of F1, so the reader has no way to know what they are.
- "Limits: no-ramp network controls are classified into surge classes". Understandable only after reading F5c. "control without a ramp flagged in 10 of 10 seeds, ramp runs 10 of 10" is not understandable. "Flagged" as what?
- "All earlier failures and limits stand". Which earlier ones? The reader has no earlier figure.
- "Supplement F1" is referenced and not available to the reader.
- "same scale" in "(d), (f) the 3 network seeds, same scale": same scale as what? (Mean-field panels (c), (e)?) On the image the y-axes of (d) and (f) are not labelled and carry no ticks.

(2) Statements the image does not support or contradicts
- "the network ... does not reproduce the mean-field result". Panels (d) and (f) show a network envelope that looks like the mean-field envelope in (c) and (e). Both open at about 50 to 58 s, peak at about 115 s, and close at about 142 s. The network spectrogram (h) has the same three rising lines as (g). A reader sees a visually similar transient, which contradicts the opening claim and the red "0 of 3 seeds agree". The caption does not say that disagreement is only by the classifier label.
- "all are S-sus, a surge without end" versus panels (d)/(f). The network envelope in (d) and (f) visibly ends at about 142 s, as in the mean field. It does not look like a surge without end.
- "the network classifier onset is 12.0 s". There is no triangle at 12 s in (d) or (f). The event-time boxes at the top of (d) and (f) contain only legend symbols (triangle, circle/plus/star glyph) and the text "event times; height has no meaning". No markers are placed at any times. Panel (d) and (f) traces show nothing special at 12 s. The only 12 s marker is the orange solid bar in (i) and the "12.000 to 13.000 s" window in (j).
- "the 3 network seeds" in (d), (f). Only one teal line is distinguishable. Seeds 1 and 2 (dashed, dotted per legend) are not visible, so the image does not show three seeds.
- "a spectral peak of 49.0 Hz". Not shown anywhere on the image. In (g) the dashed lines are at 25 and 100 Hz, not 49 Hz. The three bright lines in (g) start at roughly 28, 75 and 130 Hz at 58 s.
- "(a), (b) Mean excitability and coupling J". Okay. But "J" in (b) runs from -21 to 0 and the caption does not say its units or sign.
- "Spectrograms of v" (g)/(h): OK. But the dashed horizontal lines at 25 and 100 Hz in (g) and (h) are not explained in the caption (the image does not explain them either).
- (i) shows an orange solid and dashed bar at 12 s and 58.7 s. The caption does not say these are the windows of (j) and (k).

(3) Internal codes / jargon on the image
- Box titles and text: "ramp protocol", "P2: hypoxia-like path" (P2 is a path code), "M3", "t_on", "T_ramp", "tau_d", "tau", "I: common (non-local) drive", "N → ∞", "ING" ("inhibition-dominated" / "Inhibitory + first-order synapse (ING)"), "(M3)" in "tau_d: Synaptic decay time (M3)", "raster".
- "mean field (stored record)" and "stored values 50.170 to 50.924 s" ("stored" is project-file language).
- Class labels "D-tr", "S-sus" in the legend and in the red boxes ("network class S-sus, mean field D-tr; 0 of 3 seeds agree").
- "network raw first crossing (post hoc ...)", "network classifier onset".
- The red titles "(d) r(t), network vs mean field: FAIL" and "(f) v(t), ... FAIL".
- "r, v, s: Rate, mean potential, synapse" (s undefined in the panels), "model units".
- In the colourbar label "power spectral density (dB); same scale for (g) and (h)": fine, but "path time (s)" is an internal term (what is a "path"?).

=====================================================
F3
=====================================================
(1) Could not understand
- "The frequency check failed: ... the spectral peak is 49.0 Hz and the cycle frequency is 44.609 Hz ... differ by 4.391 Hz against the allowed 0.5 Hz (values from the project log)". "Frequency check", "spectral peak", "cycle frequency", "allowed 0.5 Hz" and "project log" are not explained. A journal reader does not know what the project log is.
- "main example run" and "Hopf point of the main run", "Hopf point", "Hopf curve", "limit-cycle frequency". These are not defined. "Hopf point" is not defined as a bifurcation and the reader is not told what the black mark shows in plain words.
- "(colour, one bar)" and "one band per slice": which slice (the term "slice" is not defined)? It means a fixed tau_d value, but the caption does not say so.
- "black bar = where the 25 Hz contour crosses the cycle". What is the "25 Hz contour" and why 25 Hz?
- "the arrow the combined path of P1, P2, P3 and P5". Paths P1 to P5 are not defined in the caption.
- "Ticks on the colour bar mark the two frequencies of the failed check."
- "(straight segments between its 30 points)" and "(straight segments between its 100 points)": why do the point counts matter to the reader?
- "the paths" in (d). "One row per path, start to end in eta_bar" in (e).
- "the surge result is stated for model M3 only" and "peak frequencies are the classifier's spectral peaks". M3 and "the classifier" are not defined.
- "All earlier failures and limits stand" and "Supplement F3". Neither is available.
- Symbols "eta_bar", "Delta", "tau_d" are written in code form. The caption does not give their meaning (the axis labels on the image do give "mean excitability", "heterogeneity" and "ms").
- "Limits: ... differ by 4.39 Hz": the failed check is not related to the result (why it matters).

(2) Statements not supported or contradicted by the image
- "the spectral peak is 49.0 Hz and the cycle frequency is 44.609 Hz". The colour bar ticks sit at about 44.6 and 49.0 Hz, so this holds. But the Hopf point of the main run (the dark-red ring in (c) and (d)) is at tau_d 5 ms and Delta 0.3, and the image gives no frequency value for it. The 44.609 and 49.0 numbers are not shown anywhere except in the caption and the bar ticks.
- "(a)-(c) ... one band per slice, black mark = Hopf point, black bar = where the 25 Hz contour crosses the cycle". Several rows have no black bar: panel (a) at tau_d 2 and 1 ms (the 3 ms row has a small bar); panel (b) at tau_d 2 and 1 ms; panel (c) at tau_d 8, 5, 3, 2 and 1 ms (no bar). The caption does not say bars are absent when the frequency is above 25 Hz everywhere. At tau_d 5 and 3 ms in (a) the bars sit almost on the Hopf mark.
- "in (c) the line is the Hopf curve ... the ring the Hopf point of the main run". In (c) there are two rings: a grey/white ring at about eta_bar 1.4 (path start) and a dark-red ring at about 2.9. The caption mentions only "the ring". The grey ring (start of the paths) is not explained in the caption. The legend says "P1, P2, P3, P5: identical in eta_bar, Delta, tau_d (stored)".
- "(d) Hopf curve ... against eta_bar and Delta (log axis), with the paths". The paths in (d) are drawn as arrows P4a (pink, up), P4b (olive, down) and brown P5, but the P1/P2/P3 arrows are hidden under the brown P5 arrow. The reader cannot see which path is which. The caption says "with the paths" but does not say they overlap.
- The Hopf curve in (c) is drawn with a visible kink at the top (about tau_d 50 ms, a straight segment to the last point), while the left edge of panel (c) shows tau_d 50 at eta_bar about 6.2. The caption's "straight segments between its 30 points" explains this, but the curve looks like a nose shape (Hopf curve folding back), which the caption does not mention.
- Legend text "Hopf curve, continuation record (panel c: Delta 0.3, J -21; panel d: J -21, tau_d 5 ms)". J -21 does not appear in the caption.
- The paths in (e) all run from eta_bar 1.4 to 4.9 (P5 return goes backwards). The caption's "start to end in eta_bar" is consistent.

(3) Internal codes / jargon on the image
- Panel titles "frequency check: FAIL" (a), (b), (c) in red; "differ by 4.391 Hz; allowed 0.5 Hz" (colour bar header); "cycle frequency at the headline" and "spectral peak at the headline" ("headline" is internal wording).
- "tau_d (ms), log axis" (axis label in code form), "eta_bar" is drawn as a symbol (fine).
- Legend: "Hopf curve, continuation record (panel c: Delta 0.3, J -21; panel d: J -21, tau_d 5 ms)" ("continuation record"), "Frequency-map Hopf point", "frequency-map slice", "P1, P2, P3, P5: identical in eta_bar, Delta, tau_d (stored)", "P5 return leg", "P4a: Delta up", "P4b: Delta down".
- Panel (e) row labels: "P1 eta_bar ramp (100 s)", "P2 hypoxia-like path (120 s)", "P3 drive (120 s)", "P4a Delta up (120 s)", "P4b Delta down (120 s)", "P5 up (100 s)", "P5 return (100 s)". These are path codes P1 to P5.
- "(d) (eta_bar, Delta) plane: Hopf curve and paths".

=====================================================
F5
=====================================================
(1) Could not understand
- "Mean field only: the network disagrees with the mean field at 3 of 4 map cells". "Map cells" is not defined. "Mean field", "network", "map" are not introduced.
- "noisy subgrid agrees in 97 of 225 cells (43.1 percent; 203 needed), so the 90 percent rule failed". What is a noisy subgrid, what does "agrees" mean (with what?), and what is the 90 percent rule? The reader cannot tell where 203 comes from (90 percent of 225).
- "(a) Map 1: class per cell in heterogeneity Delta and synaptic decay time tau_d". "Class" is not explained. "Map 1" versus "Map 2" is not explained.
- "(b) These cells: map, mean-field, network classes". Rows "map 1 class (120 s)" and "mean-field companion (30 s)" are not explained in the caption (120 s versus 30 s).
- "(c) Noisy subgrid: a cell agrees (circle), disagrees (cross) or ties (plus) with the noise-free one; (d) a post-hoc view of the same". What does "ties" mean? What is "a post-hoc view"? Panel (d) is titled "post-hoc view P-1", and P-1 is not explained anywhere.
- "(e) Map 2 in J0 (J at the path start) and ramp duration." J and "path" are not defined.
- "Red titles: network against mean field in (a), (b); the 90 percent rule in (c)."
- The long "Failed checks" list: "network against mean field (0 of 3 seeds at 10 s and at 120 s ...)", "main-run class kept in 7 of 10 noisy seeds (8 needed)", "step-halving check of the network peak frequency", "noise-level check". None is explained. The step-halving check and noise-level check are not part of this figure.
- "the noise level sigma = 0.0624 is checked and not confirmed". What noise, in what unit, what "checked" means.
- "no claim that the regime map is robust to noise", "regime map", "no-ramp network controls are classified into surge classes". Unexplained.
- "All earlier failures and limits stand", "Supplement F5". Not available.
- The first sentence says "Mean field only" but then talks about network cells. It reads contradictory without explanation.

(2) Statements not supported or contradicted by the image
- "the network disagrees with the mean field at 3 of 4 map cells". In (b), cell 1 is marked as agreeing (star), yet none of the three network seeds has the mean-field class there (seeds are S-abs, S-abs, S-rel; map and mean-field class are D-tr). Cells 2, 3 and 4 also show no seed with the matching class. So the image gives no visible rule that makes cell 1 "agree" and the others not. The caption does not say how agreement is decided (possibly surge versus no surge, which is not stated).
- "(97 of 225 cells (43.1 percent)". The reader can only roughly check against (c): panel (c) has many more circles than crosses/pluses in the top-left and mixed elsewhere. I could not confirm 97 by eye. The marks include ties, which the legend calls "a disagreement by the 90 percent agreement rule". The caption says "ties", not "disagreement". Panel (c) is a 15 x 15 grid, which matches 225.
- "(a) Map 1 ... with the 4 network cells (hexagram: agrees, heptagon: disagrees)". The image legend and symbols match (star/hexagram, heptagon). But the symbol numbers (1 to 4) in (a) are not in the caption. Cell 3 is drawn at the green hatched boundary, and cell 3 in (b) is D-none.
- Panel (a) title says "T_ramp 120 s" and (e) shows T_ramp from 1 to 1000 s. The caption does not mention T_ramp 120 s for (a).
- Panel (d) shows far more agreement (circles) than (c). The caption just says "a post-hoc view of the same" without saying how it differs. The grey dashed frame around (d) is not explained.
- Panel (a) y-axis label "Delta, cell index i" and x-axis "tau_d (ms), cell index j". Tick labels read 0.01 to 0.6 and 1 to 50. The caption does not say these are the scan ranges.
- The bold text inside (a) "Mean field only; network disagrees at 3 of 4 cells" is repeated in the caption.
- "Map 2 in J0 (J at the path start) and ramp duration": (e) shows a mostly blue map with a hatched green strip at the top, which matches D-tr and D-none. The caption does not say what blue and green mean (the legend at the top of the figure does).

(3) Internal codes / jargon on the image
- Legend: "D-tr (map cell, mean-field class)", "D-none (map cell, mean-field class)", "network cell agrees (1 of 4)", "network cell disagrees (3 of 4)", "subgrid cell agrees", "subgrid cell disagrees (not a tie)", "subgrid cell is a tie (a disagreement by the 90 percent agreement rule)".
- Panel titles: "(a) map 1, mode D, T_ramp 120 s / network vs mean field, cells: FAIL"; "(b) 4 network cells: network vs mean field FAIL"; "(c) 90 percent agreement rule: FAILED"; "(d) post-hoc view P-1"; "(e) map 2, mode D".
- "mode D" (an internal code, unexplained).
- Row labels in (b): "map 1 class (120 s)", "mean-field companion (30 s)", "network seed 0/1/2", "network against mean field".
- Axis labels: "Delta, cell index i", "tau_d (ms), cell index j", "tau_d (ms)", "J0 (J at path start)", "T_ramp (s)".
- Bottom legend: "classes of the marks in (b)": D-tr, D-none, S+, S-rel, S-abs, S-sus, NS (class codes, not defined anywhere on the image).

=====================================================
F5c
=====================================================
(1) Could not understand
- "Network classes do not reproduce the mean field" and the class codes NS, S-abs, S-sus (and S+, S-rel in the legend) are used without definition.
- "the step-halving check of the network peak frequency failed" (what it is), and later "the test is not drawn (its runs were not saved)". A reader does not know what test or what runs.
- "(10 ramp seeds filled, 3 controls open)". The caption says "filled" and "open" without saying that these are marker styles. "Ramp seeds" and "controls" are not defined. The meaning of a control without a ramp is not stated.
- "the controls reach surge classes at N = 3e3, 1e4 and 3e4 (2, 1 and 1 of 3)". See contradiction below. "Surge classes" is not defined.
- "Grey bar and tick: minimum to maximum and median of the ramp seeds". OK, but "ramp seed" is again undefined.
- "(b) Peak frequency f_pk (dotted: mean field)". What is the peak of?
- "(c) Onset time" and "(d) Duration (log axis)". The onset of what, and the duration of what? Duration unit (ms) is only on the axis.
- "Failed checks: ... noise-level check; network against mean field and the noisy subgrid (see F5)". Refers to F5 for definitions.
- "Limits: ... there is no claim of agreement in peak frequency or class between the network and the mean field; network surge classes at N = 1e4 are not evidence of a ramp-driven surge (control without a ramp flagged in 10 of 10 seeds, ramp runs 10 of 10)". "Flagged" and "ramp-driven surge" are not defined. This sentence contradicts what the caption says earlier about 3 controls per N (see below).
- "All earlier failures and limits stand", "Supplement F5c".
- "N = 1e3 ... the 3 controls are NS": "NS" is not defined.

(2) Statements the image does not support or contradicts
- "the controls reach surge classes at N = 3e3, 1e4 and 3e4 (2, 1 and 1 of 3)". In panel (a) the open (control) markers are: N = 3e3: open S+ circle, open S-abs triangle, open NS = 2 of 3 (OK). N = 1e4: open S+ circle, plus two open S-sus triangles = 3 of 3 (caption says 1). N = 3e4: open S-abs triangle plus two open S-sus triangles = 3 of 3 (caption says 1). So "1 and 1 of 3" is contradicted by the image for N = 1e4 and N = 3e4.
- "(control without a ramp flagged in 10 of 10 seeds, ramp runs 10 of 10)" at N = 1e4. The figure shows only 3 controls per N, so the "10 of 10 seeds" figure for controls cannot be seen here and conflicts with "3 controls" in the same caption and in the legend ("open: no-ramp control seed (3 per N)").
- At N = 1e4 there is one filled NS marker (a ramp seed in class NS, dark grey filled triangle, at the bottom of (a)). With 10 ramp seeds at N = 1e4, the caption's "network surge classes at N = 1e4 are not evidence ..., ramp runs 10 of 10" would be wrong: 9 ramp seeds show a surge class and 1 is NS. (Count of filled markers at 1e4 in (a): 2 S-abs, 7 S-sus, 1 NS.)
- "at N = 1e3 the 3 controls are NS and the ramp seeds are S-abs or S-sus": consistent with the image.
- "the test is not drawn (its runs were not saved)". The image carries the same text in (b), consistent.
- "(10 ramp seeds filled, 3 controls open)": consistent with the legend. But "3 controls open" at N = 1e3 shows 3 open NS arrowheads, consistent.
- The dotted line in (c) at about 34 s is a mean-field onset value, but the caption mentions the dotted line only for (b). The legend says "(b) and (c)". The dashed line in (d) ("stored minimum duration") is not mentioned in the caption at all. In (d) many seeds sit exactly on the dashed line at 1e3 ms, which the caption does not explain (probably the minimum possible duration).
- Panel (b) at N = 1e3 shows no point for the NS controls (no peak), which is expected, but there is no marker indicating "no frequency".
- The grey bar in (b) at N = 3e3 runs from about 30 to 49 Hz and the "min to max and median" marks are shown. At N = 1e4 and N = 3e4 the grey bar is drawn but the controls are outside it. Nothing contradicts the caption here.

(3) Internal codes / jargon on the image
- Legend: "S+", "S-rel", "S-abs", "S-sus", "NS" (class codes, undefined on the image).
- "filled: ramp seed (10 per N)", "open: no-ramp control seed (3 per N)".
- "grey bar and tick: stored minimum to maximum and median of the ramp seeds", "dotted line: mean-field companion value, (b) and (c)", "dashed line: stored minimum duration, (d)" ("stored" and "companion" are project terms).
- Panel titles: "(a) network class of every seed against N", "(b) f_pk against N, step-halving check: FAIL" (f_pk is a variable name), "(c) onset against N", "(d) duration against N, log axis".
- In-panel text in (b): "step-halving test not drawn: its runs are not stored" (internal wording about stored runs).
- Axis labels "f_pk (Hz)", "N = 1e3 / 3e3 / 1e4 / 3e4" (code-style notation), "duration (ms)".
