# 13t-5: fresh-subagent review of the SHORT captions of the recorded build from 5c83f54 (word for word as received; the harness indentation of the hand-back is removed)

Brief given: read each SHORT caption alone, as a reader who has never seen the project, with the image next to it (full image and four quadrant crops of each, 35 images; the seven short captions; nothing else); list every term or sentence not understood, every statement the image does not support, every text on an image that looks like an internal code; check every claim limit and failed check against the image; say whether any label starts with a lower-case word. Report only.

REVIEW OF 7 SHORT CAPTIONS AGAINST IMAGES. I read each caption first, then the full image and all four crops. Nothing was edited.

Notes on method. Counts under 1, 2 and 3 are of the numbered items below. In item 3, class names (D-tr, D-none, S+, S-rel, S-abs, S-sus, NS) are counted as one group per figure.

========== F1 ==========
1. Not understood (7)
 1) The classifier "onset ... when it first flags the gamma rise" is never tied to anything a reader can see. The 12.0 s network onset sits where the traces show nothing.
 2) "first crossing of its detection threshold" is not explained. The image legend adds "post hoc" and "raw", which the caption omits.
 3) The sentence "By eye ... look similar ... the failed check concerns the class ... no claim ... either way" opens by saying the network does not reproduce the surge and then says the shapes look alike. A reader cannot tell what failed.
 4) "noise level sigma = 0.0624 (checked, not confirmed; its check failed)": what was checked is not said.
 5) "no-ramp network controls ... classified into surge classes" and "control flagged in 10 of 10 seeds, ramp runs 10 of 10; other network runs, not drawn". The meaning, and why it matters here, is not clear.
 6) "7 further failed checks ... Supplement F1", and "its power spectrum peaks at 49.0 Hz (not drawn)": the reader has no way to relate this to (g) or (h).
 7) ING, Lorentzian heterogeneity and "synapse" (the s variable) appear in the top schematic but are never explained.

2. Caption statements the image does not support or contradicts (4)
 1) Network onset 12.0 s: the triangles in the strips above (d) and (f) sit near 12 s, but the network r and v envelopes are flat there. Panel (j) shows no oscillation either. The visible network rise begins around 50 s, before the mean-field onset line at 58.7 s.
 2) "the network does not reproduce it" and "S-sus (a rise that does not end)": (d), (f) and (h) show the network rising and ending at about 143 s, just like the mean field. The caption half-admits this ("look similar"), but its opening sentence is contradicted by the picture.
 3) (i) is described as "one row per neuron shown" and (j), (k) as "one row each". (i) is a smooth colour gradient, and (j) and (k) are dense black traces. No individual rows can be read.
 4) "circle, plus, star" = seeds 0, 1, 2: in (d) and (f) the three symbols collapse into one blob. The legend admits this; the caption does not.

3. Internal code or jargon on the image (12)
 - P2
 - M3
 - ING
 - "Lorentzian heterogeneity (Δ)"
 - "J, tau_d, tau"
 - "t_on, T_ramp"
 - "r, v, s"
 - D-tr and S-sus
 - "Network raw first crossing (post hoc ...)"
 - "FAIL" in the (d) and (f) titles
 - "model units"
 - "Event marks ... height has no meaning"

4. Claim limits and failed checks
 - Visible and supported:
   - Red titles on (d) and (f).
   - "Network class S-sus; mean field D-tr" inside (d) and (f).
   - The onsets 12.0 s and 58.698 s in the legend.
   - The three seeds shown as coincident.
   - The 25 and 100 Hz dashed lines.
   - The ramp start and end marks.
 - Stated but not visible:
   - 0 of 3 seeds agree at 10 s and 120 s ramps.
   - 1 of 4 map cells agree.
   - The 7 further failed checks.
   - The sigma check failure.
   - The no-ramp control limit (10 of 10).
   - "all earlier failures stand".
   - N = 10,000 (the image only says "N: network size").

5. Lower-case label starts: yes, in the schematic boxes and the legend.
 - "inhibition-dominated (ING)"
 - "spike raster"
 - "spectrogram of v"
 - "network r(t),"
 - "v(t)"
 - "mean potential,"
 - "synapse"
 - "start and duration"
 - "overlap at this scale: ..."
 - "tau_d" (a symbol, so allowed)

========== F2 ==========
1. Not understood (6)
 1) "class" and "classes" in the red note in (c) and the caption. Classes are not drawn or defined on this figure.
 2) "the main example", "ramp durations of 10 s and 120 s" and "4 map cells". None of these appears in F2.
 3) "the network's v is the mean over the neurons that are not refractory, a different definition": the effect on the comparison is not clear.
 4) "still relaxing" (the grey band) and "v interpolated" (the Hopf marker legend).
 5) "the surge result ... stated for model M3 only and stated for the mean field only", in the Limits: surge is not shown on this figure.
 6) "no agreement criterion is applied ... (information only)": unclear against the red FAIL in (c).

2. Statements not supported or contradicted (2)
 1) Network up and down values at the Hopf point (1.071 and 1.166), the largest up/down difference of 0.095 and the 0.080 at 5.696. The markers overlap, so none of these can be read from (b).
 2) Mean-field amplitudes 0.08 (up) and 0.55 (down) at the Hopf point. In (b) the mean-field markers at 2.9 sit at about 0 to 0.1, and no 0.55 is visible.
 Checked and supported: 15 network steps each way, the 13.2 percent top of (c), -2.5 percent at 6.5, and the cycle line stable to 8.

3. Jargon on the image (5)
 - "FAIL" in (c)
 - "Hopf point (supercritical), v interpolated"
 - "Steps within 0.1 of the Hopf point (still relaxing)"
 - "The network and mean-field classes disagree elsewhere (check failed)"
 - "Fixed point, stable/unstable" shown only as dash types

4. Claim limits and failed checks
 - Visible and supported:
   - Red title on (c) only; (a) and (b) have none.
   - The (c) note "this panel compares amplitudes only".
   - Single-run, no error bars (none drawn).
   - Hopf point 2.896.
   - Grey relaxing band.
   - Up and down sweeps coincide (text in (b)).
 - Stated but not visible:
   - The four failed class checks (10 s, 120 s, 4 cells, overall).
   - No robustness to finite size.
   - M3-only limit.
   - "All earlier failures stand".

5. Lower-case label starts: only continuation lines.
 - "of v amplitude"
 - "(network − mean field)"
 - "/ mean field"
 - "classes disagree elsewhere ..."
 - "the Hopf point"
 - "compares amplitudes only"
 - The symbol v starts two y labels (allowed).

========== F3 ==========
1. Not understood (5)
 1) "The paths coincide in (c) and (d) because they differ in J, drive or time course, which these planes do not show": the logic reads as contradictory.
 2) "the spectral peak (the peak of the power spectrum of the simulated signal)": which signal, and from which run, is not said.
 3) "P3 (P2 plus a common drive)": what the drive is.
 4) "(e) One row per path." The caption gives no x-axis meaning, and the durations in the row labels are not explained.
 5) "no classifier ... or spectrogram ... is used" and "gamma-band result is stated for M3 only": neither is shown.

2. Statements not supported or contradicted (1)
 1) "(e) One row per path": the image has 7 rows for 6 paths, because P5 is split into "P5 up" and "P5 return".
 Verified as supported:
 - 25 Hz bars on 7, 6 and 3 of 9 slices.
 - 8 of 27 bands end before 8.0 (5 in (a), 3 in (b), 0 in (c)).
 - The colour-bar ticks at about 44.6 and 49.
 - "Differ by 4.391 Hz; allowed 0.5 Hz".
 - Open grey circle and dark ring in (c).
 - P4a and P4b drawn separately in (d).

3. Jargon on the image (9)
 - "frequency check: FAIL"
 - "Hopf point of a slice"
 - "25 Hz crossing of a slice"
 - P1 to P5, P4a, P4b and "P5 return leg"
 - "tau_d"
 - "J -21"
 - "identical in η̄, Δ, tau_d (recorded)"
 - "Limit-cycle frequency"
 - "main example"

4. Claim limits and failed checks
 - Visible and supported:
   - Red FAIL on (a), (b) and (c).
   - 4.391 Hz against the 0.5 Hz allowance.
   - Both frequencies marked on the colour bar.
   - Slice counts.
   - Band ends.
 - Stated but not visible:
   - "values from the analysis record".
   - "the reason [bands end] is not recorded".
   - "No other failed check".
   - M3-only limit.
   - "All earlier failures stand".

5. Lower-case label starts: yes, on the second lines of the three panel titles and in the legend.
 - Panel title second lines: "frequency check: FAIL"
 - Legend: "a slice", "slice", "the main example (...)", "identical in", "tau_d (recorded)", "c: Δ 0.3 ...", "panel d: ...", "tau_d 5 ms)"
 - "tau_d (ms), log axis" starts with a symbol (allowed).

========== F5 ==========
1. Not understood (7)
 1) "agrees ... in 97 of 225 cells (43.1 percent; 203 cells, 90 percent, were needed)": what "agree" means for a noisy cell is not clear.
 2) "(our reading, not verified)" in the (b) sentence.
 3) "no equivalence is claimed" between the 30 s network cells and the 120 s map.
 4) "the same cells re-scored by a rule chosen after the results (post hoc; no check)": the rule itself is not stated.
 5) "no-ramp network controls ... are classified into surge classes": unclear significance.
 6) (e) "Map 2": the caption never says what the colours mean, or why J0 (-40 to -5) differs from the stated J = -21.
 7) "(classifier ... shorter ramps use a shorter window)", and "6 further failed checks".

2. Statements not supported or contradicted (0)
 - I found no contradiction.
 - Verified: cell 1 agrees; cells 2 to 4 disagree (S-sus at cells 2 and 4; S-abs and S-rel at the D-none cell 3); the blank lines in (c) and (d); the dashed frame on (d); 30 s against 120 s labels in (b).

3. Jargon on the image (class names counted as one group) (12)
 - Class names D-tr, D-none, S+, S-rel, S-abs, S-sus and NS
 - "cell index i / j"
 - "Subgrid cell agrees / disagrees / is a tie"
 - "90 percent agreement rule"
 - "Post-hoc re-scoring of (c)"
 - "J0 (J at path start)"
 - "T_ramp"
 - "tau_d"
 - "Map 1 / Map 2"
 - "Matching mean-field run (30 s)"
 - "no-noise mean field"
 - "FAIL" and "FAILED". The title of (c) says "FAILED" while the others say "FAIL".

4. Claim limits and failed checks
 - Visible and supported:
   - "network disagrees at 3 of 4 cells" and the 1 of 4 and 3 of 4 legend.
   - Red titles on (a), (b) and (c).
   - A tie counts as disagreement under the 90 percent rule.
   - The dashed frame marks the post hoc re-scoring.
 - Stated but not visible:
   - 97/225, 43.1 percent, 203 needed, and 173/225 and 76.9 percent (no counts printed).
   - The sigma check failure.
   - The 6 further failed checks.
   - "no claim of robustness to noise".
   - The no-ramp control limit.

5. Lower-case label starts: only continuation lines and symbols.
 - "network vs mean field, cells: FAIL"
 - "rule: FAILED"
 - "of (c)"
 - "path start)"
 - "network disagrees / at 3 of 4 cells"
 - "tau_d (ms), cell index j"
 - "tau_d (ms)"

========== F5c ==========
1. Not understood (5)
 1) "step-halving check": what it tests is explained, but it is unclear how a check can fail when "its runs are not recorded".
 2) The meaning of horizontal position inside each N block (seed order or jitter) is never stated.
 3) "the counts 'control flagged in 10 of 10 seeds, ramp runs 10 of 10' come from other network runs, not the controls drawn here": confusing against the 3 and 10 per N that are drawn.
 4) "recorded minimum, 1000 ms" for the classifier.
 5) "a seed on the dotted line is not evidence of agreement (the check of this panel failed)": the logic is unclear.

2. Statements not supported or contradicted (1)
 1) The legend and caption say controls (open symbols) are drawn per N, but (d) shows no open control symbols at all. Controls are also missing from (b) at N = 1000 (the NS controls). The caption does not say they are omitted from (d).
 Verified as supported:
 - Controls in a surge class: 0, 2, 1 and 1 of 3.
 - Controls in S-sus: 0, 0, 2 and 2 of 3.
 - 39 drawn ramp onsets, 8 to 27 s, all below the dotted line at about 33.7.
 - Control onsets 10 to 33 s.
 - No S-rel anywhere.
 - One filled NS ramp seed at N = 10,000.

3. Jargon on the image (7)
 - Class names S+, S-rel, S-abs, S-sus and NS
 - "Step-halving test not drawn: its runs are not recorded"
 - "step-halving check: FAIL"
 - "ramp seed" and "no-ramp control seed"
 - "recorded minimum to maximum and median"
 - "smallest duration the classifier can give"
 - "matching mean-field run"

4. Claim limits and failed checks
 - Visible and supported:
   - Red title on (b), plus the red note "Step-halving test not drawn".
   - Controls and ramp seed counts per N.
   - No S-rel.
   - The 1000 ms floor.
   - Controls flag onsets.
   - Ramp seeds at N = 10,000 are not all in a surge class.
   - 3 controls per N.
 - Stated but not visible:
   - 10 of 10 counts from other runs.
   - The 4 further failed checks.
   - The sigma check failure.
   - "no claim of agreement".
   - "not shown to be converged".

5. Lower-case label starts: only continuation lines in the red in-panel note.
 - "runs are not recorded"
 - "not drawn: its"
 - Axis labels such as "N = 1000" start with a symbol (allowed).

========== F6 ==========
1. Not understood (7)
 1) Failure label c. The caption defines it as "a cell without a surge class whose frequency is below 25 Hz". The image key says "c: a flag, not a demonstrated cause", which tells the reader nothing.
 2) "D-sus" appears in the key under e ("no exit (D-sus or S-sus)") and is not defined in the caption.
 3) The title of (a) says "(D-tr cells, no label: map 1 760, map 2 296)": unexplained.
 4) "negative control 2 (the full path with the drive off and on)": which drive.
 5) "20 pre-registered runs and 4 P2 comparator runs" and "24 points drawn": undefined, and the 24 cannot be counted because the markers overlap.
 6) "every class that depends on the test for damped against non-damped oscillations is provisional": only the key's label h shows this.
 7) "failure label": the caption never says what has "failed" for a non-surge cell.

2. Statements not supported or contradicted (2)
 1) Label c as above: the image key text does not match the caption definition (below 25 Hz).
 2) "The 24 points drawn in (d) and (e)": they are not individually countable. In (e) the P2, P3 (0.5 and 1) and P4b markers sit on top of each other, so the "identical (48.048, 49, 49 and 49.5 Hz)" values cannot be read.
 Verified as supported:
 - Bar totals sum to 169 primary labels.
 - "S-rel in 6 of 130" (the S-rel text labels sum to 6; 13 ramp values at 10 seeds each is 130).
 - Negative control 2 is D-tr everywhere.
 - Negative control 1 gives D-none at the 5 map cells and a red S+ for the network.
 - "(exploratory)" on negative control 3.
 - 120 s points to the right of the 100 tick.

3. Jargon on the image (14)
 - "Failure labels"
 - "non-surge cells"
 - "primary / any label"
 - "Delta above critical"
 - "tau_d outside window"
 - "c: a flag, not a demonstrated cause"
 - "ramp too fast for 10 cycles"
 - "D-sus or S-sus"
 - "amplitude below the fixed threshold"
 - "Hopf point, no time inside"
 - "rejected by the damped-oscillation test"
 - Negative control 1/2/3
 - P2, P3, P4a, P4b and "drive 0.5/1/2"
 - D-tr, D-none, NS, S+, S-rel, "Small mark: class (D-tr)", "Expected: no surge class", "Map cell: Delta, tau_d (ms)", "T_ramp", "FAIL"

4. Claim limits and failed checks
 - Visible and supported:
   - Red title on (c) only.
   - The network S+ where no surge is expected.
   - The label c note "a flag, not a demonstrated cause".
   - The h label (damped test).
   - The exploratory tag.
   - The noisy rows.
 - Stated but not visible:
   - Sigma = 0.0624 and its failed check.
   - The 10 of 10 counts.
   - The no-ramp control limit.
   - M3-only.
   - "No other failed check".
   - "All earlier failures stand".
   - The definition of the first negative control (falling excitability).

5. Lower-case label starts: yes.
 - Key lines in (a): "c: a flag ...", "d: ramp too fast ...", "e: no exit ...", "f: amplitude ...", "g: Hopf point ...", "h: rejected ...". These start with a lower-case letter label, and the descriptions c, d, e, f and h start lower-case.
 - "mean field, no noise"
 - "mean field, noise (10 seeds)"
 - "drive off"
 - "drive on"
 - "(exploratory)"
 - "(text: seeds in another class)"
 - "tau_d" (allowed)

========== FS1 ==========
1. Not understood (7)
 1) "replication checks" and "check against the primary source ... deferred".
 2) "the coupling of an M2 network is unsourced".
 3) "root-count boundary lies within one cell of the formula fold at half spacing ... base spacing ... cusp points need half spacing".
 4) "saddle, a stable focus and a stable node" (not drawn).
 5) "the linearised rate has standard error 0".
 6) "ring", "rings" and "ring rate", versus "focus". The colour bar says "Ring frequency" while the caption says "frequency of the stable focus".
 7) "step test on a network" and "sinusoidal-forcing check": what is being checked, and against what, is not said.

2. Statements not supported or contradicted (2)
 1) (d): "the fitted frequency and decay rate differ from the linearised ones by 2.1e-4 and 6.1e-3 relative". No fit or linearised curve is drawn, only the "Fit window start and end" lines, so the numbers cannot be checked.
 2) (b): the range "0.24 to 153.4 Hz". The colour bar starts near 1 and the 0.24 end cannot be read. The top at about 153 is supported.
 Verified as supported:
 - The largest cycles per e-fold, 5.10 (colour bar top near 5.1).
 - Three fixed points inside the fold wedge, and the cusp.
 - The test point at (-5, 15).
 - Sinusoid amplitude 3 and period about 400 ms.
 - The grey no-focus areas.
 - "No panel has a red title".
 - The "Own reading ... not verified" note in (e).

3. Jargon on the image (10)
 - "Ring frequency"
 - "Fold formula, two branches"
 - "Cusp, formula"
 - "(grid node)"
 - "Fit window start and end"
 - "Focus value of r"
 - "Test point (−5, 15)"
 - "Own reading of this test, not verified"
 - "J/√Δ, η̄/Δ"
 - "Recorded r(t), forced" and "Forcing I(t)"

4. Claim limits and failed checks
 - Visible and supported:
   - No red titles.
   - "Own reading ... not verified" on (e).
   - Grey means no focus.
   - Largest 5.10.
 - Stated but not visible:
   - 4 of 5 checks pass.
   - The primary-source check is deferred.
   - The network step test was not run.
   - 20 of 20 and 18 of 20 boundary agreement.
   - 0 of 25727 non-damped foci.
   - "standard error 0".
   - The 2.1e-4 and 6.1e-3 differences.
   - "nothing in this figure is a result for M3".

5. Lower-case label starts: only one continuation line, "a focus outside the band)". Panel titles, axis labels and legend entries all start capitalised. "r (firing rate)" starts with a symbol (allowed).

========== TOTALS ==========
Item 1 (not understood): F1 7, F2 6, F3 5, F5 7, F5c 5, F6 7, FS1 7. Total 44.
Item 2 (not supported or contradicted): F1 4, F2 2, F3 1, F5 0, F5c 1, F6 2, FS1 2. Total 12.
Item 3 (internal code or jargon on the image): F1 12, F2 5, F3 9, F5 12, F5c 7, F6 14, FS1 10. Total 69.

Item 5 across all seven: no figure has a first-line label starting with a lower-case word other than symbols and class names. Lower-case starts occur on continuation lines (F1, F2, F3, F5, F5c, FS1), on second lines of titles (F3, F5), in the F1 schematic boxes ("spike raster", "spectrogram of v", "inhibition-dominated (ING)"), and in the F6 failure-label key (c to h) and negative-control row labels.
