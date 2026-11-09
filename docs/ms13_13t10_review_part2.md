# MS13 13t-10: fresh-subagent review (part 2 of 2: FS4, FS5, the five most serious findings)

Word for word as handed back by the reviewer (only the harness indentation removed). Part 1 is docs/ms13_13t10_review.md.

=====================================================================
FS4
=====================================================================
Not understandable:
- "Radau solver (a second solver ...)" is explained; "default solver" is not.
- "class mark" and "D-tr (a rise that ends)", "V_p", "level 0, 1 and 2", "initial perturbation" are explained but dense. "Noise floor (a very small added noise at three levels, 0, 1 and 2)" does not say the actual sigmas.
- "not strictly monotone" is not explained in the caption.
- "network time step" vs "Heun step" in different panels: two different step variables. A reader may confuse them.
- "spectrum-maximum reading of the first halving" is hard to understand.
- "peak value V_p ... reset to the negative of that value" is understandable only after careful reading.

Not supported by the image:
- (a): The caption says "the small cross is the raw first crossing of its detection threshold ... so the cross lies on the mark". The image draws the raw first crossing as a small open downward-pointing triangle (legend "Raw first crossing" with a triangle marker). No cross anywhere. The alt text repeats "a cross". WRONG.
- (a): The rows are labelled "Perturbation 1e-9", "Perturbation 1e-3". The caption and panel (b) call this 0.001. Inconsistent labelling on the image itself ("1e-3" in (a), "0.001" in (b)).
- (h): The caption says the classes are for "each time step and each peak value V_p (100 and 200)". The image has 6 rows: V_p 100 at 4 steps, V_p 200 at only 2 steps (0.001 and 0.0001). The caption does not say that V_p 200 was run at only 2 steps.
- (i): The caption says "the peak frequency of each seed at V_p ±100 against ±200". The image shows only the steps 0.001 and 0.0001 (6 points), not stated.
- (e): Title is "Noise floor at 10 s and 316 s" and y label "Median delay". Nothing on the image says "classifier onset". The caption says classifier onset; the CSV name says so too.
- (c)/(d): y label is only "Delay of the onset" with no unit.
- The caption says the "spectrum-maximum reading ... passes in 2 of 3 seeds" and "0 of 3 seeds pass". These are not drawn. I computed from the CSV: seed 0 63.06 to 63.06 (0 percent), seed 1 60.06 to 60.06 (0 percent), seed 2 60.06 to 57.06 (5 percent). So 2 of 3 pass under the spectrum-maximum reading; the claim is correct but only from the CSV. The "0 of 3 seeds" under the classifier reading is plausible from (g) but not drawn as such.
- In (f) the open marks (circle for seed 0, open square for seed 1, open star for seed 2) overlap with the filled marks and each other at 0.001 and 0.0005, and are hard to separate.

Internal-looking text on the image:
- "Perturbation 1e-9 / 1e-3", "Tolerance 1e-8 / 1e-12", "Radau solver", "D-tr (classifier onset)", "Heun step (tau)", "Level 0/1/2", "V_p 200, step 0.001", "S-rel", "S+", "S-abs", "S-sus", "Allowed 0.02", "Open: spectrum maximum", "not strictly monotone", "Ramp duration" with "316.228 s". The class codes are defined only in the Key.

Claim limits and failed checks vs image (special attention e):
- The red titles: (a) "solver check: FAIL", (f) "Network peak frequency: FAIL", (g) "Change per step halving: FAIL" are red. The caption sentence "panels (f) and (g) carry a red title with FAIL, and (h) and (i) are information only" is right but omits (a), which is also red. The caption names (a) elsewhere. (b)-(e), (h), (i) are black. (h) and (i) have no "FAIL" and no red. Correct.
- The red note in (a) reads "Radau - default = 181 ms against the 1 ms allowed". Visible.
- (f) red note: "First halving: change of 5 to 43 percent against 2 percent allowed (g)". Visible. Correct against the CSV.
- (g) bound line "Allowed 0.02": visible as a dashed line near zero.
- "0 of 3 seeds pass; 2 of 3 under the spectrum-maximum reading": not on the image.

Numbers checked (statement of the network peak-frequency change per halving):
- (g) points read from the image: seed 0 about 0.43, 0.33, 0.55; seed 1 0.20, 0.25, 0.20; seed 2 0.05, 0.00, 0.055. CSV: 0.4286, 0.3333, 0.55; 0.20, 0.25, 0.20; 0.05, 0.00, 0.0526.
- Caption "0 to 55 percent per halving": correct. "first halving 5 to 43 percent": correct. "second halving 0 to 33 percent": correct. "third halving 5 to 55 percent": correct (seed 2 is 5.3 percent; seed 1 is 20 percent; seed 0 is 55 percent).
- "largest change 55 percent at the third halving, seed 0": correct. "8 of the 9 changes above 0.02": correct (only seed 2 second halving is 0). The image does not annotate this; it must be read.
- (f) peak frequencies: seed 0 63, 90, 60, 93 Hz; seed 1 60, 48, 60, 48; seed 2 60, 57, 57, 60. These match the CSV and the percentage changes (63 to 90 is 43 percent).
- (a): five rows at 58.698 s and Radau at 58.879 s. On the x axis (58.65 to 58.90) the Radau mark is at about 58.88. Correct. The two marks per row (triangle and open triangle) overlap so tightly that equality of the two onsets cannot be seen at this scale.
- (b): all 8 marks D-tr, all "0 s". Correct, "largest shift is 0 s".
- (e): 316.228 s medians -1.5, -1.5, -1.27; 10 s medians -1.5, about -0.97, about -1.03. Caption: "-1.5, -1.5 and -1.273". Correct. "10 of 10 seeds have no onset": printed on the image.
- (c)/(d): levels read: level 0 about 0, level 1 about -0.04, level 2 about -0.1; (d) -1.5, -1.5, and -0.94 to -1.27. Correct.
- N = 10,000, 3 seeds, 10 s: not on the image.
- 1.87 s vs 1.874 s: that is FS5.

Visual problems:
- In (a) the filled and open triangles sit on top of each other in every row and can be told apart only with a zoom.
- In (f) heavy overlap of seed-1 and seed-2 marks at 0.001 and 0.0005 (open and filled). The red note box sits between the legend and the data; no collision.
- In (b) the group labels "Perturbation" and "Tolerance" under the columns are small and sit in a second row below the tick labels. Readable.

=====================================================================
FS5
=====================================================================
Not understandable:
- "classifier", "surge", "frequency check ... 1/W" are explained, but the first sentence is very long.
- "(c) For each group of records (rows)" never names the groups. The image rows are "Mean field (5)", "Hold, point 1 (22)", "Hold, point 2 (122)", "Noise cases (26)", "No-noise cases (13)". "Hold" and "point 1/point 2" appear nowhere in the caption. The numbers in parentheses (5, 22, 122, 26, 13) are not explained.
- "the variants in the order of those labels" depends on a different panel; reading (a) requires looking at (c).
- "s times tau": the Key defines r and v but not s (it is the synaptic variable, but the Key does not say so).
- "rho (the gamma-band share of the total power in a baseline-only run)" is defined only inside (d).
- "1/W", "Hilbert phase", "zero crossings" (limits).
- "map 1", "map 2", "noisy subgrid" are used with only a short gloss in (i).
- "ring items of its own test" is cryptic.
- "(strict)" in (b) is jargon.

Special attention (c): does the caption say what the columns of (a) are, and can a reader tell?
- The caption does say it: columns are the baseline followed by the 9 variants, "left to right as the labels under (c)", and "(a) has no column labels of its own". The columns of (a) are x-aligned with the columns of (c) on the image (baseline at the left, ticks at the same x positions), so a careful reader can transfer the labels. But on the image (a) itself shows no labels, so the reader must scroll down to (c), which is about 740 px lower, and the first (Baseline) column of (c) is an empty column. The caption does not say that the Baseline column of (c) is empty on purpose.
- (c) now has a colour bar: yes, placed under (d), labelled "Fraction of records changed (the shade of (c))", 0.0 to 1.0, yellow to purple. The caption points to it ("the colour bar under (d)"). It matches the shades. OK. The bar sits under (d), not under (c), and a gap of about 130 px (whole-figure scale) lies between the bar and (c), so the association is weak.

Not supported by the image:
- The caption says each (c) cell gives "the number of records whose class differs from the baseline over the number of records". The cells show only the numerator (6, 0, 2, ...). The denominators are in the row labels. A fraction like "6/22" is not shown. The alt text says "each cell giving the number ... over the number of records", repeating the claim.
- (a): "'not run' where the variant's window does not fit": I found no "not run" mark in (a) and no "not run" entry in the legend. The class legend lists only S+, S-rel, S-abs, S-sus, NS, D-tr, D-sus, D-none (counts 126, 24, 1, 21, 88, 68, 1, 61, total 390 = 39 x 10).
- (h): the caption says "the cells of map 1 and map 2 in which the two frequencies agree within 1/W are 51 of 760 and 71 of 296 (reported, no allowed fraction)". Neither number is on the image. The CSV for (h) has only four rows (49.0, 44.609, difference, bound). So this claim is neither visible nor in the source data of the figure.
- (i): the image shows labels "14/900", "0/325", "1096/2250". The caption gives 14 of 900 only. The map-2 count 325 differs from the 296 given for map 2 in (h), which is unexplained.
- (f): the panel title on the image is "Main-example class unchanged". The panel actually plots the fraction of map-1 cells that change class under each variant (x axis "Fraction of map-1 cells"). The title describes something else. The caption says both. A stranger reading the title sees a mismatch.
- (d): the legend says "1.05 s" and "1.87 s", the caption says "1.054 s" and "1.874 s" (rounded; the same lengths).
- (d): the caption says the numbers of cells per window (100, 25, 25, 25, 25, 1026). These numbers are not on the image.
- (e): only some class counts are written inside the bars; the S+ (24 at 0.2 s) and S-abs/S-sus counts are not labelled.
- Caption (g) says "against 0.005 allowed (dashed line)": the dashed line is drawn, but the y axis (log) only has the ticks 1e-3, 1e-6, 1e-9, so 0.005 is not directly readable.

Internal-looking text on the image:
- Row labels "Case 1, 120 s" ... "Case 26, 120 s" (the caption says the case numbers stand for recorded names in the supplement), "Hold, point 1 (22)", "Hold, point 2 (122)", "Mean field (5)".
- Column labels: "Factors 1.5", "Factors 4", "Minimum amplitude 0.05", "Window x0.5", "Minimum cycles 5".
- "0*" with the title note "* includes not run".
- "R*tau", "v", "S*tau" (x axis of (g)).
- "Baseline ratio rho, level", "Map 1", "Map 2", "Subgrid", "10/tau".
- (b) text: "File 1: 8 test functions, File 2: 56 test functions, 7 of them are marked as expected failures (strict)".

Claim limits and failed checks vs image:
- The red title appears on (h) only: "(h) Frequency check: FAIL", as the caption says. (a)-(g), (i), (j) are black.
- The failed check is visible: "Difference 4.391 Hz > 0.5 Hz" in a box in (h). The red title and the box agree with the caption.
- "reported only" appears in titles (j) and in (i) legend ("Reported only"). The caption says (i) map 2 and the subgrid have open rings: visible as large open rings around the stars; map 1 is a plain star. Correct.
- (f) "Allowed 0.1" dashed line: visible; all 9 marks are left of it. "Class of the main example unchanged under every variant": that is the title, not a drawn check.

Special attention (d): tau and tau_d consistency:
- The image uses only "tau" (legend "tau 10 ms / 20 ms" in (g); "tau (ms)" in (j)). tau_d does not appear on the image. The caption mentions "the synaptic decay time tau_d staying at its reference value" in (g) and (j), and in the Parameters. The Key defines "tau = membrane time constant" among its symbols and defines tau_d in the Classifier settings paragraph as "synaptic decay time" and again inside (g). So each use is consistent with the Key. The one soft spot is that tau_d is not in the Key's own "Symbols:" list, but it is defined at its first use in the Panels and in the settings paragraph.

Numbers checked:
- 306, 400, 172, 24 (and 2, 0): on the bars in (e) in bold. Correct. CSV: S+ 24 + S-rel 278 + S-abs 4 = 306. Correct.
- 81 changes in (c): I summed the cells: 2 + 22 + 17 + 35 + 5 = 81. Correct.
- "at most 1.67 percent of the 900 map-1 cells change class": (f) marks are at about 0.00 to 0.02. CSV: maximum 0.016667 (Minimum amplitude 0.2), band 30 to 120 is 0.015556 (= 14 of 900). Correct.
- "10 percent allowed": the dashed line is at 0.1. Correct.
- "1.2e-8 against 0.005": the largest mark in (g) is at "v", tau 10 ms. CSV 1.2258e-8. Correct, and read from the image roughly as 1e-8 (log scale). The dashed line is at about 5e-3. OK.
- "14 of 900", "0/325", "1096/2250 (0.487)": image labels agree with the CSV.
- "49.0 and 44.609 Hz", difference 4.391: on the image the peak marker is at about 49 and the cycle at about 44.6, with the 0.5 Hz bar. CSV 49.0, 44.609402, 4.390598. Correct.
- 8 and 56 test functions, 7 expected failures: printed in (b). Correct vs caption.
- (j): triangles at about 49.5, 49, 43 Hz; stars (10/tau) at about 61, 49, 41 Hz. CSV y: 49.5, 49.0, 43.0. 49 x 10/8 = 61.25 and 49 x 10/12 = 40.8: agree with the stars.
- 39 rows, 26 cases, 10 columns: counted on the image (13 + 13 rows above the gap, 13 below). Correct.
- Could not check on the image: 51 of 760, 71 of 296, 45 of 760, 1026 cells per window, 1880 recorded classifications, 12260 baseline records, 460 records, 2.176222, "0.005", and the windows' cell counts.
- (d) windows and five levels: legend lists 6 windows; x positions show 5 levels (about 0.25, 0.33, 0.5, 0.67, 0.75). Matches the alt text.

Visual problems:
- (d): six lines largely overlap at the high end; the 0.2 s and 2 s lines are separable but the others are not. Only x ticks 0.4 and 0.6 are labelled, although five levels are plotted (0.25, 0.33, 0.5, 0.67, 0.75).
- (d): the legend occupies the lower half of the axes and sits in empty space, so no collision, but the y axis extends to about -0.5 for it.
- (e): y axis goes up to 1.75 with bars to 1.0 and the legend in the upper empty area.
- (g): the legend sits between the dashed line and the data.
- (j): at tau = 10 ms the star sits exactly on the triangle.
- (a): in some rows the marks of different classes are close, but no clipping.

=====================================================================
FIVE MOST SERIOUS FINDINGS
=====================================================================
1. FS4 (a) and its alt text say the raw first crossing is a "small cross" lying on the class mark. The image draws it as a small open downward triangle (legend "Raw first crossing"). The statement is wrong in the caption and in the alt text, and the two onsets cannot be told apart at the drawn scale.
2. F4b (d): the caption says the dotted line at 1 s is "the smallest duration the classifier can give, so medians at 1.0 s are pinned". The image and the CSV show medians and individual noisy-seed durations well below 1 s (about 0.2 to 0.5 s). The statement is contradicted by the data it describes.
3. FS5 (h): the caption's "51 of 760 and 71 of 296" are neither on the image nor in the (h) source data. In (i) the image shows "0/325" for map 2, a different denominator than the 296 of (h), with no explanation.
4. F4a (a)/(c): the counts "8 open squares" and "3 diamonds" cannot be reconciled with what is drawn (2 and 5 squares, about 2 and 2 diamonds), because marks pile on one another at the fast end. The alt text claims delays reach "about 3" while the data maximum is 2.0. The P5 offset and hysteresis lines in (b) use P1's purple although P5 is brown elsewhere.
5. F4b foot marks and the (f) line. The foot marks (green diamonds) appear at 10 of 13 positions with no stated owner and do not follow the seed counts or the zero values of the grey bars. The caption does not say whether they are noisy seeds or noise-free runs. (f) shows a straight log-log line while the caption says "no scaling law is claimed". Also FS5 (c) cells show only numerators while the caption promises "over the number of records", FS5 (f) is titled "Main-example class unchanged" for a panel that plots the fraction of map-1 cells, and FS5 (a) has no "not run" mark although the caption describes one.
