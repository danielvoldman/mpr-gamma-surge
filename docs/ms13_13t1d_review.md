# 13t-1d: report of the fresh subagent review of the first build (from 1c58804)

Recovered word for word from the hand-back message of the subagent (the harness had indented every line; the indentation is removed, nothing else is changed). It reviewed the package in the session scratchpad folder review_1d (recorded build from 1c58804, before the fixes of DL-576).

I viewed every image (full, then four quadrants) and read every caption and alt text for F1, F3, F5 and F5c. Nothing was edited, created or deleted. Image sizes are about 1250 px wide at 200 dpi, which is 6.25 in, so "mm" below means mm at print size.

=====================================================
F1
=====================================================
Images:
1. Panels (d) and (f), strip above the axes. The circle, plus and star for the three seeds fuse into one grey-teal blob (about 3 mm). The three seeds cannot be told apart, and the glyph in the legend is just as unreadable. The strip has no time axis or ticks, so its marks cannot be read as times. Major.
2. Panels (d) and (f), the curves. Seeds 0, 1 and 2 are drawn as what looks like a single teal line. The legend entries "network seed 1" (dashed) and "network seed 2" (dotted) cannot be matched to anything visible. Minor.
3. Legend swatch versus panels (c) and (e). The legend shows a thick grey line for the "mean field (stored record)". The panels show a grey filled band with a black outline. Minor.
4. Panels (d) and (f), plotted content versus the verdict. The network envelope is a transient oscillation that starts at about 50 s and collapses at about 143 s, almost identical in shape and amplitude to the mean-field panels (c) and (e). Nothing visible happens at the 12.0 s "classifier onset" triangle. The class label "S-sus" (no termination) and "0 of 3 agree" therefore cannot be tied to anything visible. A careful referee will say the figure contradicts its own headline. Major.
5. Panels (d) and (f), strip title spacing. The red title, the strip frame and the axes are stacked tightly. The gap between the title and the strip frame is only about 1 mm. Minor.
6. Panels (d) and (f), in-panel red bold text. The 4-line text sits about 3 mm above the curve peak. It is legible but crowds the top of the axes. Minor.
7. Panels (c) to (f), y ranges. The y ranges are 0 to 10 for r and about -5 to 32 for v, but the data fill only the lower quarter. About 70 percent of each axis is empty, because the panels were forced to a shared range. Minor.
8. Panels (g) and (h), time axis. A thin white band is visible at the right edge of (g) and at the edges of (h). It looks like a rendering defect even though the caption explains it. Minor.
9. Panels (g) and (h), onset line. The blue dash-dot onset line has very little contrast on black (g) and on the purple-magenta background (h). Minor.
10. Panels (g) and (h), frequency axis. Only 25, 100 and 150 are labelled. The 0 Hz baseline is unlabelled, and the label "25" sits almost at the bottom frame. The white dashed 25 and 100 Hz lines cut across the ridges. Minor.
11. Colour bar for (g) and (h). It sits to the right of (h), far from (g). Its rotated 3-line label ("power spectral density (dB); same scale for (g) and (h)") is taller than the bar and runs below it. The "-100" tick label crowds the extend arrow. Minor.
12. Panel (i), orange window frames. Bars about 2 s wide are drawn on a 165 s axis and hide the data beneath them. They stick out above and below the raster rows into the white padding. They look like data features, not frames. Minor.
13. Panels (j) and (k), top of the raster. The solid dark band at the top (the high-rate neurons) sits flush against the top of the orange frame, with essentially no visible gap. This contradicts the "padded by 30 rows so marks don't fuse with the frame" statement. Minor.
14. Panels (j) and (k), content. At the printed size the raster is an unreadable dark blob in (j) and a texture in (k). There is no y-axis label ("neuron") and no tick labels. Tick labels 58.7 and 59.7 do not match the titles 58.698 and 59.698. Minor.
15. Panels (b) and (a), axis labels. Panel (b) has no y-axis label and no units, and neither does eta_bar in (a). In (b) the dotted "ramp" lines and dashed "J ramp" lines are two overlapping vocabularies and are hard to tell apart at 8 pt. Minor.
16. Schematic, arrow from the "ramp protocol" box to "M3". It is only a tiny arrowhead with no shaft. It overlaps the left box edge and looks like a stray triangle. Minor.
17. Schematic, text. The 'I: common (non-local) drive' entry has no counterpart in any panel. The "network" box reads "N: Network size raster" as one run-on phrase. Names such as tau_d, t_on and T_ramp are printed as code-style names, not typeset symbols. The M3 box text sits about 1.3 mm from the box edge. Minor.
18. Axis units. r and v are in "model units", but the spectrogram and spike axes use s and Hz. The time unit of "model units" is never tied to seconds. A reader cannot connect the two. Minor.
19. Panel (c), alt text. The alt text says r "returns near the baseline after the ramp". The image shows it ending at about 0.7, versus about 0.15 before onset. Minor.
20. Panels (a), (b), (c), (e), (k), colour bar of (i): no overlaps or cut-offs found other than the points above.

Captions:
1. The caption is about 1,800 words. The take-home (network does not reproduce the mean-field class, RB1 failed) is in sentence 1, which is good. But the first paragraph alone contains about 30 numbers and 10 undefined codes. Nobody can find the take-home quickly because it is buried in check bookkeeping.
2. "hypoxia-like path P2", "headline", "stored mean-field headline run", "stored" (used about 40 times). There is no explanation of what "stored" or "headline" means for a reader.
3. "the pre-stated check that a peak below 25 Hz would trigger a new choice of the headline did not fire". Not understandable.
4. "classifier onset", "raw first crossings (post hoc)", "S-sus", "D-tr". The key lists the classes, but they are defined only in terms of "power tests" never explained.
5. "RB1", "RB6", "RB2", "RB3(a)/(b)", "RB8", "RB9(b)", "G4", "G7", "D24", "FS4", "F4": opaque codes. The caption points to "the supplement" for them.
6. "map cell (24, 26)", "finite-size runs at N = 3e3 and 1e4", and "N = 1e4 and 3e4" in Limits. The caption says the 3e4 runs "are not drawn", while finite-size runs are given as 3e3 and 1e4 in one place and 3e4 in another. It is unclear which N values exist.
7. "(not verified as a drawing)", "a display decimation that is not verified as a rule", "our reading, not verified", "a logged verdict NOT INSIDE". Internal audit wording that a journal reader cannot parse.
8. "sigma = 0.0624 (checked, not confirmed; ... FAIL ... NOT INSIDE; mean-field baseline std 0.039522 against the network range 0.037989 to 0.038920)". Sigma is never defined (noise on what?).
9. "A_ref", "limit-cycle amplitude at the reference validation point", "minimum 10 cycles", "threshold 0.1 x A_ref". Not tied to anything visible.
10. "the six limits set when gate G4 was triggered", "the estimator for damped against non-damped oscillations fails 2 of 8 ring items", "the models M4 or M3a and M3b", "RB8 parts that concern M4 and adaptation". Unexplained.
11. "Mode D" and "mode N" are defined only in the Key block, far from where they matter.
12. "network control without a ramp was flagged in 10 of 10 seeds, and the ramp runs in 10 of 10" (Limits). No panel of F1 shows controls, and it conflicts with F5c, which shows only 3 controls per N and one NS ramp seed at 1e4. I cannot reconcile these numbers.
13. "the stored spectrogram windows ... 164 centres", "10 log10 PSD", "32559 of 49364 mean-field cells". Detail of no use to a reader.
14. Panel (a) states "the ramp start t_on = 5 s and the ramp end 125 s", but in (b) the same dotted lines appear alongside the J-ramp lines at 35 s and 155 s. The reader has to deduce which are which.
15. The text "ING" in the schematic and "s" (synapse variable) in the mean-field box are never defined in the caption. "path time" is also never defined.

Organisation. Take-home first, then Panels, Key, Settings, Parameters, Failed checks and Limits, all as labelled paragraphs. The structure is good, but the length and code density defeat it. Failed checks are listed twice (and again in Limits), and about half of the Limits paragraph repeats itself.
Contradictions with the image. (i) The claimed "S-sus, no termination" versus the visibly terminating transient in (d) and (f). (ii) "thin lines for three seeds": no three distinct lines are visible. (iii) Panel (j)/(k) padding versus the flush band.

Overall: Visually clean and the layout is mostly sound, but the central claim in (d)/(f) cannot be verified from the picture, several marks are unreadable at print size, and the caption is an audit log, not a caption.

=====================================================
F3
=====================================================
Images:
1. Panel (a), slice tau_d 3 ms. The Hopf mark and the 25 Hz bar fuse into a fragmentary "J" glyph, and the mark itself is partly hidden. Panel (b), slice 5 ms, is the same. The caption admits this. Major for legibility.
2. Panel (c), slice 13 ms. The Hopf mark sits on the black curve, and the 25 Hz bar sits against the mark (about 0.5 mm). It is not mentioned in the caption (only (a) 3 ms and (b) 5 ms are). Minor.
3. Panel (c), slice 5 ms. The thin dark-brown arrow, the maroon Hopf ring and the start circle lie on a dark-teal band. The arrow and ring are both dark and merge. The arrow also hides the band colour and the Hopf mark of this slice between 1.4 and 4.9. The arrowheads at both ends are not explained in the legend, which shows only a circle with a line. Major.
4. Panel (c), Hopf curve. The black curve is a visibly coarse polyline (30 points). It has a kink near the top (tau_d 36 to 50 ms, eta_bar about 4.7) and a straight segment. It runs through the Hopf marks and covers their white outlines. Minor.
5. Panels (a) to (c), band ends. The bands run off the right frame at eta_bar 8 and are clipped. Frequency continues beyond the plotted range, so a reader cannot tell the band end from the clip. Minor.
6. Panels (a) to (c), y ticks. Slices exist at 3, 8, 13, 22 and 36 ms but only 1, 2, 5, 10, 20 and 50 are labelled. Several bands cannot be read off the axis (for example 3 ms is at an unlabelled position). The 25 Hz bar and Hopf mark are only about 1.5 mm wide and 1 px thin at print size. Minor.
7. Panels (a) to (c), red titles. They say "RB9(b) FAIL" but nothing in the panel shows the failure. The headline cycle frequency 44.6 Hz and the spectral peak 49.0 Hz are not marked on the colour bar or on the 5 ms band. The reader sees a red flag with no evidence. Major for communication.
8. Panel (d), arrow bundle at the start circle. The return-arrow head, P4a, P4b and the combined arrow all converge at the start circle. The return head overlaps the start of the dashed magenta line. At the maroon ring (eta_bar 2.896) the Hopf curve, the ring and the brown arrow coincide. Minor.
9. Panel (d), x axis. It has tick marks but no tick labels and no axis label, so the reader must look down at (e). There is large empty area in the upper left and lower right. Minor.
10. Panel (d), P5 return. The return leg is drawn on top of the up leg. The dash-dot style is barely visible in (c) and (d), so the return is not distinguishable from the up leg there. Minor.
11. Legend. Placed beside (d) and (e), far from (a) to (c), and wraps to 4 to 6 lines per entry. The entry "Hopf curve, A4 record (panel c: Δ 0.3, J -21; panel d: J -21, tau_d 5 ms)" uses the undefined internal IDs "A4" and "A6". Several glyphs (Hopf mark, bar, ring) are tiny. Minor.
12. Panel (e). All seven rows are the same 1.4 to 4.9 segment. The panel carries only labels and durations, and does not show what differs between the paths (J ramp, drive, Delta). The return-arrow head stops at about 1.55, not 1.396 (an acknowledged offset). The last dot of dotted P3 and P4b merges with the arrowhead. Minor.
13. Units. There are no units for eta_bar or Delta, and "tau_d" is a code name. Minor.
14. Colour bar. Fine and well placed. No overlaps or cut-offs found there.

Captions:
1. "RB9(b) FAILED ... 4.391 Hz against 0.5 Hz ... so it does not contain the spectral value". Meaning unclear. What is the "classifier's spectral peak" versus the "cycle frequency"? These are only defined at the end of the Key block.
2. "the 100 Hz contour does not occur", "the 25 Hz contour crosses the cycle branch only on some slices". No contour is drawn. Only a bar is drawn at the 25 Hz crossing, and 100 Hz has no mark at all.
3. "The project's pre-stated check ... would trigger gate G2 (a switch to another model); the project log records ..., it states no outcome for this check itself, so reading the crossings ... is our reading and is not verified". Incomprehensible without the project.
4. "A6 slice", "A4 record" (legend), "frequency map", "continuation", "analysis step 'M3 fixed points and Hopf curves'". Never explained. "Hopf point/curve" and "limit cycle" are not explained for a general reader.
5. "reference validation point at 32.0 to 39.7 Hz". It is not visible in the figure.
6. "the headline", "headline value", "stored" (many times), "combined path arrow", "one stored point drawn twice and not moved", "layout only".
7. "drive amplitude of 1", "P3 = P2 plus a common drive", "Delta multiplied by 1.5 or 2/3 over the ramp", "P5 = eta_bar up, then down, J fixed". These are only in the Key block.
8. The Key lists RB1, RB8, G4, G7, D24 which are never used in this figure, plus "G2" (used once).
9. "tick labels are plain numbers" for log axes. OK. "the shading shows the cycle frequency at J = -21", but J is shown nowhere in the figure.
10. "(black mark with a white outline)" is clear. "tall black bar" is clear.

Organisation. Take-home is "RB9(b) failed so the frequency shading is not confirmed", which is a limit and not a message about the figure's purpose (where gamma frequencies and paths lie relative to the Hopf boundary). Panels, Key, Settings, Parameters, Failed checks and Limits blocks are present. The Panels paragraph is a single 900-word block.
Contradictions with the image: none found. Counts of 25 Hz bars (7, 6, 3) and the P4a/P4b end values (0.45, 0.2) match.

Overall: Panels (a) to (c) are a good compact design, but the dark arrow over dark bands in (c), merged marks in (a) and (b), and the failure flag that is not visually evidenced weaken the figure; the caption uses IDs (A4, A6, G2) the reader cannot know.

=====================================================
F5
=====================================================
Images:
1. Panel (b), class symbols. The blue and green markers, the gold triangles, the purple down-triangles and the orange squares are not defined in the legend or anywhere in the figure. The class of each seed cannot be read. The mapping (gold triangle = S-abs, etc.) only exists in F5c, and the caption does not give it. A reader cannot check why cells 2 to 4 disagree. Major.
2. Left of (c), stray "Δ". A rotated "Δ" sits right beside the right frame of (a) (about 2 mm from it) and about 7 mm left of (c)'s tick labels. It reads as part of (a) and is far from (c), which it belongs to. Major (misattribution).
3. Panel (a), in-panel take-home text. The top of the bold three-line text is about 0.5 mm below the top frame. It is too close, and the text takes about 20 percent of the axes. Major (spacing).
4. Panel (a), numbered symbols. They are about 4 x 4 cells in size. Symbols 3 and 4 sit on the D-none/D-tr boundary, so the class beneath them is hidden. A heptagon (disagree) is hard to distinguish from a circle at this size, though the colour and number help. Minor.
5. Panel (a), cells. The cells are about 3 pt each with white gridlines. The three isolated D-none cells in the lower blue area are about 1 mm and barely visible. Minor.
6. Panels (c) and (d), marks. The colour fills of the three states are mostly covered by the dark marks. The magenta of "disagree" and the ochre of "tie" are only visible as small flecks, so the colour legend matches almost nothing. The crosses in dense disagreement blocks nearly touch horizontally (gap of 1 px), contradicting "no two marks touch". Minor.
7. Panels (c) and (d), layout. The cross-shaped blank gaps divide the subgrid into four blocks and look like four panels or missing data. Only the caption explains it. Minor.
8. Panel (b), spacing. The bottom symbols (hexagram and heptagons) are about 0.9 mm from the bottom frame. Minor.
9. Panel (e). The cells are only 2.3 pt tall, so rows merge into white lines. The y-label "J0 (J at path start)" is a code-like name. Minus signs are hyphens ("-13.8") and not true minus signs, unlike F1. Minor.
10. Legend. It is at the top, far from (c) to (e), and the two-column layout is fine. No overlaps. Minor.
11. Panel titles. "(a) ... RB1 cells: FAIL" and "(b) ... RB1 cells FAIL" are inconsistent. The red titles flag a failure, but the title of (c) says "D24 rule: FAILED" and does not say what the rule requires. Minor.
12. No overlaps or cut-offs found in (d) beyond the above. Its dashed grey frame is fine.

Captions:
1. "Mean field only; network disagrees at 3 of 4 cells; noisy subgrid agrees in 97 of 225 cells (43.1 percent; 203 cells needed)". The first sentence is understandable only as bare numbers. The reader does not know what a "cell" is, what "needed" means, or the 90 percent rule until the Key.
2. "mode D (the noise-free mean field)" and "D-tr", "D-none". The classes are defined in the Key but not in plain language of what they look like.
3. "fine-tuning gate G5 continues", "RB4 passed (0 of 14 changed, 64 of 64 unchanged)", "G4", "RB1 cells", "RB2", "RB6", "G7", "F5c", "F6". Opaque. RB4 is not shown anywhere in the figure.
4. "118 of 225 on the three surge-definition categories, our reading", "post-hoc view P-1 (173 of 225 = 76.9%) feeds no gate". Confusing: three different agreement counts (97, 118, 173) are given with no guidance.
5. "24 ties count as disagreements by the rule", "mode-N majority class of 10 seeds", "noise level sigma = 0.0624, checked and not confirmed (sigma check: FAIL, logged verdict NOT INSIDE)". Sigma is never defined.
6. "matched to 1e-9", "map-1 indices (steps of 2 and 3 cells)", "a 3 pt mark did not fit the D-none cell of (a), which is 4.1 pt high". Meaningless to a reader.
7. "network cells ... at T_ramp 30 s", "mean-field companion class at T_ramp 30 s" versus the map at T_ramp 120 s. The comparison is between different ramps, which the caption admits "no equivalence is claimed". It is unclear why the comparison is shown.
8. Network class symbols in (b): not defined at all (see image point 1).
9. "J0 = the J at which the path starts", "tau_d", "hypoxia-like path P2". Not explained physically.
10. The Key and Limits sections include items that are irrelevant to F5 ("Failure label (c) ... drawn in F6 ... not applicable here", "1,056 of the 1,057 surge-class cells", "baseline is taken as zero", "episode-exit rule to P3 and P4"). Padding.

Organisation. The take-home is first. Panels (a) to (e), Key, Settings, Parameters, Failed checks and Limits are present, but the panel paragraph is long and contains many layout apologies.
Contradictions with the image. (i) "the cells of (a) and (e) carry no class mark", yet (a) carries four large marks (they mean network cells, so a partial contradiction). (ii) "no two marks touch": crosses nearly touch. The remaining counts (cell positions, 1 of 4 agreeing) match.

Overall: The central table (b) cannot be decoded without F5c, a stray "Δ" and cramped in-panel text spoil (a)/(c), and the caption dumps three different agreement scores and unexplained gates.

=====================================================
F5c
=====================================================
Images:
1. Panels (b), (c), (d). The grey min-to-max bar with its wide median tick, the dotted line (mean-field companion) and the dashed line (duration floor) have no legend entry and no label in the panel. They are explained only in the caption. In (c) the dotted line is not labelled with its value 33.698 s. Major.
2. Panel (b), red title "(RB6): FAIL". The check is "halving the step changes f_pk by less than 2 percent", but the panel plots f_pk against N. Nothing visible shows the failed check. The red title flags a problem the panel does not show. Major (communication).
3. Panels (a) to (d), x position in each N group. Marks are laid out in slots (ramp seeds 0 to 9, then controls), and the position carries no value. The figure itself does not say so. A reader will read the within-group x position as data, and the group-left bar and tick look like another data point. Minor.
4. Panels (b), (c), (d), seeds with undefined metrics. At N = 1e3, no control marks are drawn at all, and at 3e3 only two control marks are drawn. The legend and (a) show 3 controls per N, so the absence is not explained in the panel. See caption point 1 below. Minor.
5. Panel (c). The open purple triangle at N = 3e4 (about 33 s) overlaps the dotted line at 33.7 s. Minor.
6. Panel (b). Many purple S-sus triangles sit on the dotted 49 Hz line (N = 1e3, 1e4, 3e4) and hide it. Minor.
7. Panel (d). At the floor, S-abs triangles sit on the dashed 1e3 line and hide it, and at N = 1e4 the median tick coincides with the top of the bar so it looks like an error bar with a cap. The S-sus durations are close to the record length, which suggests censored values, and the figure does not say so. The y axis is in ms while (c) is in s. Minor.
8. Panel (a), N = 1e3. The three open grey NS triangles (controls) almost touch each other. Open gold triangles have a thin outline of low contrast. Minor.
9. Legend. The S-rel square (orange) appears in the legend but in no panel (no data), which is fine but unexplained. There is no label saying the x slots are seeds. Minor.
10. No overlaps with frames, labels or edges, and no cut-off text found. Text size is fine.

Captions:
1. "Seeds whose metric is undefined are not drawn: per N (1 000, 3 000, 10 000, 30 000) f_pk 0, 0, 1, 0; onset 0, 0, 1, 0; duration 0, 0, 1, 0". This contradicts the image. Panel (a) shows NS controls (3 at 1e3, 1 at 3e3) and (b) and (c) draw no marks for them. So at least 4 undefined seeds are missing, not 1. The counts probably refer to ramp seeds only, but the caption does not say so.
2. "the 10 ramp seeds per N fall in S-sus and S-abs (S+ in 6 seeds at N = 3e3, NS in 1 at N = 1e4)". This matches the picture, but "do not ... separate ramp from no-ramp records" overstates it. At N = 1e3 all three controls are NS and all ramp seeds are S-sus or S-abs, which is a clean separation.
3. Limits: "the network control without a ramp was flagged in 10 of 10 seeds, and the ramp runs in 10 of 10" and "the controls without a ramp reach 7 of 10". The figure shows 3 controls per N and 1 NS ramp seed at 1e4. I cannot reconcile these statements with the figure.
4. "ramp seed", "no-ramp control", "ramp" never explained (what ramps, what is a ramp). "surge", "S+", "S-abs", "S-rel", "S-sus", "NS". The Key defines them only in terms of "absolute/relative power tests" and "termination".
5. "stored class", "stored mean-field companion value at T_ramp 60 s", "classifier's own routine", "called as in the stored evaluation", "a build test; a difference stops the build", "logged exception to the rule that figures read stored tables first". Internal workflow language.
6. "duration = flagged windows x step, so one window is the smallest duration, 1.0 s = 1000 ms", "a pinned value that is the floor of the classifier". Hard to follow.
7. "RB6 ... halving the step must change the network f_pk by less than 2 percent". Understandable, but the figure does not show the test (see Images point 2).
8. "RB1 cells 1 of 4; gate G4 triggered", "RB2", "RB8", "RB9(b)", "G7", "D24", "F5", "F6", "mode D". Opaque. The Key and Limits blocks list many things unrelated to F5c.
9. "sigma = 0.0624 (checked, not confirmed ... NOT INSIDE)". Sigma is never defined.
10. "N = 1e3 ... 3e4" is clear. "T_ramp 60 s" is given only in Parameters, while F5 uses 30 s and 120 s.

Organisation. A clear take-home and per-panel text, plus all the standard blocks. Take-home is the first sentence, but mixes RB6 numerics with a statement about class separation. The key to the grey bar, dotted and dashed lines is only in the Panels paragraph (not in the Key).
Contradictions with the image. (i) Undefined-seed counts (see 1). (ii) "do not separate" versus N = 1e3 (see 2). (iii) "10 of 10" and "7 of 10" statements (see 3). Panel counts (6 S+ at 3e3, NS at 1e4, 39 onsets from 8.0 to 27.0 s, 1e3 ms floor) match the image.

Overall: The panels are clear and well spaced, but the missing in-figure key for the bar, dotted and dashed lines and the red RB6 title with no evidence hurt it, and the caption's seed counts and control statements do not agree with what is drawn.

=====================================================
Cross-figure points
=====================================================
- All four captions are 1,300 to 1,800 words. They use unexplained internal IDs (RB1, RB6, RB9(b), G2, G4, G5, G7, D24, A4, A6, F4, F6, FS4) and the words "stored", "headline" and "our reading, not verified" throughout. Each includes the same long Limits paragraph, much of it irrelevant to its own figure.
- The figures use code-style names (tau_d, T_ramp, f_pk, J0) in axis labels and legends. "Model units" never gets a time unit.
- Class symbols are consistent between F1 and F5c (purple down-triangle = S-sus, red circle = S+, gold up-triangle = S-abs), but F5 (b) has no key, so the cross-figure consistency is invisible to a reader of F5 alone.
- The red-title convention (red = failed check) is applied in F1, F3, F5 and F5c, but only F1 (d) and (f) and F5 (a) and (c) show the failure itself. In F3 (a) to (c) and F5c (b) the red title is unsupported by anything plotted.
