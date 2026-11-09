# MS13 13t-10: triage of the fresh-subagent review (mine; the review itself is verbatim in docs/ms13_13t10_review.md and docs/ms13_13t10_review_part2.md)

Rule O8 (DL-692): a finding that proves a caption number wrong or a statement that the image contradicts earns ONE targeted rebuild in the NEXT step; every other finding is logged here with its category and left. Nothing is rebuilt in this step. Each reviewer claim in the first table was checked by me against the stored data or the code (read-only) before it was put in a category.

## A. Findings that earn the one targeted rebuild of the next step (wrong number or statement contradicted by the image)

| # | figure | finding | my check | category |
|---|---|---|---|---|
| A1 | FS4 (a), caption and alt text | caption: 'the small cross is the raw first crossing ... the cross lies on the mark'; the image draws the raw first crossing as a small downward triangle (legend 'Raw first crossing'), no cross | CONFIRMED: jfs4.py line 252 says 'small cross' and the alt text repeats it; the mark is the style entry fs4 raw-crossing mark (a nabla, style.py comment 13i) | image contradiction |
| A2 | F4b short caption (d) | 'The dotted line at 1 s is the smallest duration the classifier can give, so medians at 1.0 s are pinned'; the drawn durations include values below 1 s | CONFIRMED in the stored values drawn in (d): P2 linear 0.658 s, P2 sigmoid 0.373 s, P5 0.67 and 0.449 s, noisy seeds 0.30 to 0.80 s. The floor of 1.0 s holds for ramp durations of 60 s or more only (the full caption says so: 'one window times the step, 1.0 s for ramp durations of 60 s or more'); the short caption drops that scope, and so does the F5c wording 'smallest duration the classifier can give' (recorded minimum 1000 ms is correct there: the F5c durations are at T_ramp >= 60 s) | statement contradicted by the data it describes |
| A3 | F4a alt text (a) | 'delays from about 0 to about 3'; the drawn maximum is 2.0 (the y axis runs to about 3.5) | CONFIRMED: jf4.py line 472 types 'about 3' (the maximum of the six series is 2.0, the plateau eta_peak minus eta_H) | wrong number in an alt text (not in a caption; the caption says 2) |

## B. Wording, clarity, jargon, density: logged and left (O8)

| figure | finding (reviewer) | category |
|---|---|---|
| F3 | 'recorded', 'cycle branch', 'slice', 'main example in (c)', 'path leg', J = -21, 'Supplement F3' undefined or dense; the failed-check sentence is a long chain | jargon / wording |
| F3 | the Hopf mark is a tiny glyph; touching at tau_d 3 ms (a), 5 ms (b), 13 ms (c) (the full caption names the first two, not the third); the tau_d 5 ms slice in (c) is overlaid by ring, circle and arrow; the P5 return arrowhead is buried in (d); (d) and (e) share an x axis | design (listed to the reviewer: the (c) 13 ms touch is a stored coincident position of the same kind as the two named; allow-listed as such) |
| F3 | legend phrase 'identical in eta_bar, Delta, tau_d (recorded)' and the tau_d 5 ms of the (d) curve are not in the short caption; the alt text still says 'tall black bar' | wording (the alt text wording 'tall black bar' is a statement the image does not contradict badly: a 1 px wide line; listed) |
| F4a | long definitions (entry-exit prediction, step of the grid, testable, in range, start distance, hold), dense sentences | jargon / density |
| F4a | squares, diamonds and daggers pile up at the fast end, so '8 open squares' and '3 diamonds' cannot be counted on the image; the counts are stored (8 delays in the hold; 3 untestable in-range runs) and unchanged since 13t-8 | density; the counts are right, the image cannot show them (design, open since 13t-8 item 6) |
| F4a | hollow dagger: works (the filled marks beneath are visible, the reviewer confirms), but is small and dark like the open-marker outlines | confirmation of O3; design remark left |
| F4a | in (b) the P5 offset and hysteresis lines use the purple of P1 although P5 is brown elsewhere; the P1 prediction line is overdrawn | design (the colour of f4_down and f4_hyst is a ruled style entry; listed) |
| F4a | 'two further failed checks' (short) against three noise-robustness rows listed with F4b | not a defect: the short caption counts the failed rows of the full caption that it does not name (V7, DL-688 triage); the reviewer counts the rows differently |
| F4b | 'foot marks' (whose runs; not following the seed counts), 'pinned', 'runs without a ramp', 'T_ramp 5.62341 s' not mapped to the rate axis, 'D-none' undefined in the short caption, 'a result, not a check' | jargon / wording |
| F4b | 'negative from T_ramp 5.62341 s on' is true for the longer ramps but the median sign flips at the fast end (+0.001 at 3.16 s, -0.014 at 1.78 s, +0.108 at 1 s) | wording (the stored values are right; the phrase is the ruled F4 caption wording, listed) |
| F4b | (f) shows a straight line on log-log axes next to 'no scaling law is claimed' | wording (a ruled claim limit; the figure is what it is) |
| F4b | P1 hidden behind P2 and P5; error bars of (g) invisible at this scale; seed counts crowded above the panels | design / density |
| FS4 | 'default solver', the actual noise-floor sigmas, 'not strictly monotone', network step against Heun step, 'spectrum-maximum reading', V_p reset | jargon |
| FS4 | (a) rows 'Perturbation 1e-9 / 1e-3' on the image, 0.001 in (b) and in the caption (same number, two notations) | wording |
| FS4 | (h) and (i): V_p 200 was run at two steps only; not said | wording (one clause) |
| FS4 | (e) title does not say 'classifier onset'; (c)/(d) y label has no unit | wording |
| FS4 | the sentence 'panels (f) and (g) carry a red title with FAIL' omits (a), which is red too | wording (a is named in the first paragraph and in the Failed checks paragraph; the sentence is about results that rest on the network peak frequency, which (a) is not) |
| FS4 | the figure's numbers (0 to 55; 5 to 43, 0 to 33, 5 to 55; 55 at the third halving, seed 0; 8 of 9 above the bound) | CONFIRMED CORRECT by the reviewer against the image and the source data (O1 fixed) |
| FS5 | group names 'Hold, point 1/2', the counts in the row labels, 's times tau', 'rho', 'map 1/2', 'subgrid', 'ring items', '(strict)' not explained; the first sentence is long | jargon / wording |
| FS5 | (c): the cells show the numerator only (the denominator is in the row label), the Baseline column is empty without a word; the colour bar stands under (d), not under (c) | wording (the caption says 'the number of records ... over the number of records': to be reworded to 'the number, the number of records being in the row label'); design |
| FS5 | (a): 'not run' mentioned but no such mark in (a) and no legend entry | wording: the caption describes the possibility; I did not establish whether any cell of (a) is 'not run' in the stored table (the mark would be drawn if so; the reviewer found none, the star of (c) is a not-run record); to be checked and reworded in the next step |
| FS5 | (h) '51 of 760 and 71 of 296' not on the image or in the (h) source data; (i) shows 0/325, a different denominator | the numbers are STORED values (A11 evaluator rb9b cells_reported: map 1 51 of 760, map 2 71 of 296; checked) and equal the printed ones; they are stated but not drawn, and 296 (the check of (h)) and 325 (the band check of (i)) are two different evaluations; wording: say so in one clause |
| FS5 | (f) title 'Main-example class unchanged' for a panel that plots the fraction of map-1 cells that change | wording of an image title (the caption says both) |
| FS5 | (d) windows 1.05 and 1.87 s on the image against 1.054 and 1.874 s in the caption; the cell counts per window are not on the image; only two x ticks labelled | rounding; wording |
| FS5 | image text 'R*tau', 'S*tau' (sentence-case guard capitalises the first letter; the caption writes r times tau) | jargon (open since 13t-9) |
| FS5 | tau and tau_d consistent with the Key (reviewer's check, special attention d) | CONFIRMS the fix of O4 (b) |
| FS5 | the columns of (a) are explained in the caption (special attention c) | CONFIRMS O4 (c); the weak link between (a) and the labels under (c) remains (design, no relayout ruled) |

## C. What this review confirmed of the 13t-10 fixes

- O1 FS4 numbers right against the image and the source data. O3 the hollow dagger shows the marks beneath. O4 (b), (c), (d) and (e) as logged in DL-693. F3: no new statement that the image contradicts; the 'tall black bar' remains only in the alt text (listed under B).
- The reviewer found no wrong caption number in F3, F4a (the alt text 'about 3' apart), FS4 and FS5 other than the three items of table A; every checkable number was reported correct.

## D. For the reviewer (not decided here)

Items 44, 45, 46, 48 of docs/ms13_close_items.md stay open. UNVERIFIED glosses stay marked (O7). The reviewer's first-time-reader complaints about jargon (B) are the unavoidable kind named in O8; they are left.
