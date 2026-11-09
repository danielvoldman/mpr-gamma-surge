# MS13 13t-10 O2: audit of superlatives, ranges, bounds, counts and direction words in the captions of all 13 journal figures (DL-690)

## Method and coverage (read this first)

1. Listing by script (scratchpad script, run on the recorded captions of 13t-9, `figures/journal/<ID>/<ID>_journal_caption.txt` and `_caption_full.txt`, the FS captions have one file): every sentence is split at `.` or `;` and kept if it holds one of: largest, smallest, highest, lowest, at most, at least, up to, "N to M", all, none, every, only, "N of M", increase(s), decrease(s), rise(s), fall(s), most, least, never, always, both, each, "no <noun>". Result: **488 sentences** (the same script on the recorded captions of this build, after the fixes: see the last line of this section); per file: F1 8+45, F2 14+24, F3 8+27, F4a 6+31, F4b 8+32, F5 14+50, F5c 11+37, F6 12+33, FS1 11+20, FS2 15, FS3 30, FS4 27, FS5 25 (short + full; FS2 to FS5 have one caption).
   After the fixes the same script on the recorded captions of the 13t-10 build lists **490 sentences**; the phrases 'falls from', 'the largest change, at the first', 'tall black bar', 'synaptic decay times' and 'Colour and contours' occur 0 times.
2. Of these, **115 distinct sentences** hold a superlative, a bound, a comparison or a direction word (largest, smallest, highest, lowest, at most, at least, up to, increases, decreases, rises, falls, grows, larger, smaller, more than, less than, fewer, between): they were read one by one. Every claim in them that carries a **data number or a direction** was checked against the stored arrays or tables (table below, 47 rows). The remaining words (all, none, every, only, both, each; about 370 sentences) are mostly the ruled claim-limit text, class definitions and Key entries; their stored numbers are covered by (3) and (4), their wording is not a data claim.
3. The number audit (`jnumaudit`, docs/ms13_13t9_n2_audit.md, kind S: every number that a builder types and that is a stored quantity is compared with the stored value: 244 occurrences, all equal) and, new in this step, the **superlative review** (`jnumaudit.superlative_review`): every numeric constant of a builder that stands in a superlative, a range or a bound and is not a kind S row is listed with a class and a reason (59 constants, 20 reviewed groups, 0 unreviewed); the test fails if a new one appears without a review.
4. The independent comparison (scripts/ms13_independent_compare.py: draft 462 equal, journal and short rows all equal, 0 not equal) compares about 550 numbers of the captions with values recomputed from the stored files.

## What the checks cannot cover (said, not hidden)

- A right number taken from the wrong stored quantity (the context pattern of an S rule narrows this but does not remove it).
- A claim of direction, of "all", "none", "every" or "only" whose words carry no number (a sentence "the delays do not depend on the step" is checked only where an independent row exists: FS4 floor rows).
- Small integer counts (cannot be told from a stored value of the same size by value).
- The words around a number (a true number in a wrong sentence, as in F4b (f): the numbers were right, the direction against the drawn axis was not).
- Numbers in a string built at run time from stored values are not typed and are not seen by the audit (they are right by construction; the sentence around them is read here).

## Wrong statements found (all fixed in this step)

| # | figure | statement | what the stored data or the image say | fix |
|---|---|---|---|---|
| 1 | FS4 | "the largest change, at the first halving, is 43 percent" and "changes by 5 to 43 percent when the time step is halved" (take-home, (g), alt text) | seed 0: 0.4286, 0.3333, 0.5500; seed 1: 0.20, 0.25, 0.20; seed 2: 0.05, 0.0, 0.0526. Largest 55 percent at the third halving; over all halvings 0 to 55 percent; 5 to 43 percent holds for the first halving only; 8 of 9 changes above the bound 0.02 | take-home, (g) and alt text computed from the array (`jfs4.change_stats`); per-halving ranges 5 to 43, 0 to 33, 5 to 55 |
| 2 | F4b | "the jump offset ... falls from 0.346 to 0.0034" (take-home, (f), short and full) | stored: 0.346 at the largest ramp rate 0.04607, 0.0034 at the smallest 4.607e-5, monotone over the 13 values; the drawn axis is the ramp RATE, against which the offset rises (it falls as the ramp is made slower) | "rises with the ramp rate, from 0.0034 to 0.346"; the build stops if the offset is not monotone in the rate |
| 3 | FS5 | the limit MS11-C4, (g), (j) and the alt text called tau "synaptic decay times" | stored: the unit-level test and RB9(d) vary model.tau_ms (the membrane time constant: 10 and 20 ms; 8 and 12 ms) with tau_d held (plan section 3.3 reference to tau = 10 ms; docs/ms11_eval_rules.md 4 (d)); the Key and the image were right, the caption was wrong | "membrane time constants tau ... the synaptic decay time tau_d staying at its reference value" |
| 4 | F3 | full caption: "a tall black bar", "black mark with a white outline", "hollow ring", "Colour and contours", "called 'continuation' / 'frequency-map' in the legend" | image: thin vertical line with a white outline, small black three-pronged mark with a white outline, small dark-red ring, no contour line drawn, legend words "Hopf curve", "Hopf point of a slice", "25 Hz crossing of a slice" | caption names what the image shows; the ruled A6 take-home sentence on the 25 Hz and 100 Hz contours stays (stored data, ruled wording) |

## Claims checked against the stored arrays and tables (equal = the printed value equals the stored value at the digits printed)

| figure | claim | value in text | stored value | equal |
|---|---|---|---|---|
| F1 | (g)/(h) shared colour range lower end | -100.25 dB (minimum of the network panel) | -100.2516 | yes |
| F1 | upper end, "the larger of the two maxima" | 5.42 dB | network 5.4179, mean field 5.4027 | yes |
| F1 | stored mean-field range | -437.98 to 5.40 dB | -437.9811 to 5.4027 | yes |
| F1 | cells below the shared minimum | 32559 of 49364 | 32559 of 49364 | yes |
| F1 | (i) spikes sum, rows that spike | 1777037; 294 of 300 | 1777037; 294 of 300 | yes |
| F1 | (i) colour range, cells above it, up to | 0 to 116 (99th percentile); 492 of 49500; up to 981 | 116; 492; 981 | yes |
| F2 | up/down network difference, largest | 0.095 (1.071 up, 1.166 down) at eta_bar 2.896 | 0.0949 (1.0708, 1.1656) at 2.896 | yes |
| F2 | same above eta_bar 3.0 | 0.080 at 5.696 | 0.0800 at 5.696 | yes |
| F2 | network against mean field, up to / range | up to 13.2 percent; +13.2 to -2.5 | 0.1317; -0.0248 | yes |
| F2 | mean-field sweeps coincide, largest relative difference from 0.2 above Hopf | 1.2e-3 | 1.16e-3 | yes (rounded) |
| F2 | stable cycle to | eta_bar 8 | 8.0 | yes |
| F2 | continuation against the sweeps, at most; largest value below Hopf - 0.1 | 1.84e-3; 6.2e10 | ruled draft take-home (DL-129, not drawn); not re-derived | ruled wording, not re-checked |
| F3 | largest cycle frequency (a), (b), (c); one scale | 60.3; 73.5; 73.7 Hz; 9.8 to 73.7 Hz | 60.284; 73.497; 73.692; 9.773 to 73.692 | yes |
| F3 | 25 Hz crossing slices (a), (b), (c) | 7 of 9; 6 of 9; 3 of 9 (tau_d 13, 22, 36) | 7, 6, 3 (13, 22, 36) | yes |
| F3 | cycle at the reference validation point | 32.0 to 39.7 Hz | 32.017 and 39.680 (A6 summary) | yes |
| F3 | points of the two Hopf curves | 30 and 100 | 30 and 100 | yes |
| F4a | solvers differ; testable runs within one step | 181 ms (1 ms); 0 of 6 | 181; 0 of 6 | yes |
| F4b | ring rate range, damped | between -25.7 and -24.3, 13 of 13 | -25.66 to -24.34, 13 | yes |
| F4b | M2 ramp rates (13 values) | 4.607e-5 to 0.04607 | 4.607e-5 to 0.04607 | yes (13t-9 fix) |
| F4b | jump offset | 0.346 to 0.0034 | 0.34575 and 0.003430 | numbers yes, direction wrong (item 2) |
| F5 | surge seeds per N; controls | S+ in 6 at N = 3000, NS in 1 at 10,000; 2, 1, 1 of 3 | 6; 1; 2, 1, 1 | yes |
| F5c | same per-N counts; "S-sus and S-abs" classes of the 10 ramp seeds | as F5 | ramp seeds N=1000: S-abs 4, S-sus 6; 3000: S+ 6, S-abs 1, S-sus 3; 10000: NS 1, S-abs 2, S-sus 7; 30000: S-abs 5, S-sus 5 | yes |
| F5c | stored minimum duration | 1000 ms at all four N | ruled floor, independent rows | yes |
| F6 | "all are D-tr" (P2, P3, P4a, P4b at four ramp durations) | all | 48 of 48 values D-tr | yes |
| FS1 | non-damped foci; nodes with a focus; band nodes; largest cycles per e-fold | 0 of 25727; 25727; 14793; 5.10 | 0 of 25727; 25727; 14793; 5.1004 | yes |
| FS2 | largest Delta/eta_bar; largest deviation from 1 | 0.14531; 0.00071 | 0.145309; 1.000710 | yes |
| FS2 | frequency change with J | 13.4, 25.0, 42.2 percent | peak-to-peak over the mean of the 5 stored values: 13.4, 25.0 (tau_d 20: 17.98 - 14.19 over the mean), 42.2 | yes |
| FS2 | network against mean field in the frequency | within 0.09 percent | -0.0861 | yes |
| FS3 | surge seeds per N; controls; the N rule | 4, 7, 2, 5 of 10; 2, 1, 1 of 3; 5 at 30,000 against 2 at 10,000 | 4, 7, 2, 5; 2, 1, 1; 5 and 2 | yes |
| FS4 | main-example onsets; Radau difference | 58.698, 58.879 s; 181 ms | stored A7 | yes |
| FS4 | the 8 cells of (b); largest shift | D-tr in all 8; 0 s | 8 of 8 D-tr; 0.0 | yes |
| FS4 | f_pk change per halving | **43 percent, the largest** | **55 percent at the third halving** | **no, fixed (item 1)** |
| FS4 | seeds that pass | 0 of 3 (2 of 3 spectrum maximum) | 0 and 2 | yes |
| FS5 | white-noise records not NS | 306, 400, 172, 24 of 500 | 306, 400, 172, 24 | yes |
| FS5 | largest change of the main example variants | at most 1.67 percent of 900 cells | 1.67 | yes |
| FS5 | frequency check | 49.0, 44.609, 4.391 Hz against 0.5 Hz | stored A11 evaluator | yes |

Claims that are ruled wording from the plan or the decision log (they stay, the rule is the claim, not a result): "at least 8 of 10 seeds", "at least 90 percent of the cells", "RB1 needs at least 3 of 4 cells", "differ by at most 0.5 Hz", "the surge classes are no fewer at 30,000 than at 10,000", "the linearised rate has standard error 0" (DL-092), "no 100 Hz contour in range ... 25 Hz contour crosses the cycle branch only on some slices" (A6, DL-131; the stored numbers in it are checked above), the claim-limit sentences (docs/claim_limit_labels.md).
