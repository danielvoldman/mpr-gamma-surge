# MS13 13t-8b: fresh-subagent review of F4a, F4b and the K4 and K5 caption fixes

Reviewer: one NEW fresh subagent (general-purpose, no earlier context), read-only, asked for an adversarial review of figures/journal/F4a and F4b (PNG, short and full captions, supplements, source data, alt text), the FS2, FS3, FS1 and F3 captions, the rulings DL-664 to DL-676 and the code. The report below is the subagent's final report, UNEDITED (verbatim). The triage is the second part of this file and is mine. No rebuild after this review (L5).

## Report of the subagent (unedited)

1. **HIGH — wrong line style for "linear" in F4a and F4b.**
   - Where: short and full captions of F4a (a) and F4b (a)–(d).
   - Claim: "linear (solid) and sigmoid (dashed)". The full text says "linear profile (solid line, filled marks)".
   - Evidence: the keys in both PNGs draw "P5 linear" as a dash-dot line. The sigmoid entries are dashed. Only P1 and P2 linear are solid.
   - This also muddles the prediction lines, which the caption gives as "dash-dot for P1, dashed for P2, solid for P5". The P1 prediction (dash-dot) shares a style with the P5 data line. The P5 prediction (solid) shares one with the P1 and P2 data lines. The key swatch for "Predicted onset" is a brown dash-dot line, which matches no single prediction line.
   - Fix: say "linear (solid; P5 dash-dot)". Or draw P5 linear solid. Make the prediction key swatch neutral.

2. **HIGH — F4b full caption (f) gives the wrong ramp-rate range.**
   - Where: F4b_journal_caption_full.txt, panel (f).
   - Claim: "13 values from 3.5e-5 to 0.035".
   - Evidence: the F4b_source_data.csv panel f and g rows have x from 4.607e-05 to 0.0461. The image (f) and (g) x-axes start near 5e-5 and end near 0.05, unlike (a)–(e), which end at 0.035. The F4a supplement text says "eps 4.61e-05 to 0.0461".
   - Fix: write "4.6e-5 to 0.046".

3. **MEDIUM-HIGH — ring error numbers 33.1, 20.6, 12.7, 7.6 and 4.4 are not in the source data.**
   - Where: short and full captions of F4a: "in the source data" appears twice, once for (a) and once for (c).
   - Evidence: F4a_source_data.csv has no error rows for panel c. It has only 13 delay rows per start distance. Panel a carries one error value, 25.07 (P5 linear). The other five numbers appear only in the caption and in the supplement .md prose.
   - A second fault: the three diamond runs (not testable) carry error "0" in the "error of the prediction in steps" series. Nothing in the file marks "0" as "not testable", so it reads as a perfect match. The flag series "in range and constant eta (1 = untestable)" exists, but the 0 is still misleading.
   - Fix: add the five panel-c error rows, and blank the error for untestable runs. Or reword to "listed in Supplement F4a".

4. **MEDIUM — "1 further failed check" in the F4a short caption disagrees with the supplement.**
   - Where: F4a short caption, near the end; counted by `jshort.further_count`.
   - Evidence: F4a_supplement.md lists five FAIL rows touching F4: RB2 subgrid, RB2 headline class, RB3a, RB3b and RB6 solver. F4a shows three of them, so two are not shown. The F4a count treats the single "RB2" mention as one. F4b counts rows ("3 further": RB3a, RB3b, RB6). So the same figure pair counts rows in one place and mentions in the other.
   - The status block also holds a stored FAIL, RB6 network_fpk_halving_dt, which neither count includes.
   - Fix: count rows ("2 further") or say "the noise-robustness failures are in F4b". State once what is counted.

5. **MEDIUM — the main example is drawn at one delay and quoted at another.**
   - Where: F4a (a) red ring, and the caption "the delay of the main example is taken from the runs with a noise floor".
   - Evidence: the red ring sits at the noise-free value, 0.0662 (source row "main example: delay"). Panel (d) level 0, which the full caption calls "the delay of the main example", is −0.00076.
   - The short caption says the red ring is the main example "not used as evidence" and never says its drawn value is the solver-dependent one. A reader sees 0.066 against about 0.
   - Fix: add "the ring is the noise-free, solver-dependent value (0.066); the value used is (d) level 0".

6. **MEDIUM — the primary raw marks in F4a (a) are mostly hidden.**
   - Evidence: the dark "‡" classifier marks sit on the raw marks at all 13 positions. The filled purple and brown pentagons and circles of P1 and P5 are largely covered, and P1 is also hidden under P5 where they coincide (11 of 13). At 0.0197 and 0.035 the octagon, diamond, square, ‡ and raw marks all stack. The caption calls the raw crossing "primary", but the dark second-reading mark dominates the picture.
   - Fix: draw ‡ smaller or lighter, or offset it. Offsetting conflicts with the "no jitter" rule, so shrinking or lightening is better.

7. **MEDIUM — the collision allow-list is a blanket and its reason is partly untrue.**
   - Where: collide.py, JOURNAL_ALLOW F4a and F4b.
   - Evidence: every entry uses the patterns `marks:` and `marks:` (and `marks:` and `line:`). That matches any marks, so any future overlap in these panels passes silently. The reason text, "stored coincident positions and ruled mark sizes", is true for the P1/P5 coincidences and for the concentric floor marks. It is not shown for the ring and square stacks, which are deliberate nested symbols, and the red ring on a data mark. It is also not shown for the F4b noise-bar median marks, which sit on data marks and are described as "within the ruled mark size", unchecked.
   - Fix: narrow the label patterns to the series that actually coincide, or add a count check per entry.

8. **MEDIUM — undefined terms in the short captions.**
   - F4a short: "testable" and "in the range of the onset check" are never defined. "Within one step of the prediction" does not say what a step is. "Hysteresis width" and "offset on the way down" are not explained. "Delay" is used for two things: the onset delay in eta_bar units, and the P2 path "ramped to 0 after a delay". "Minimum 10 cycles" is not explained.
   - F4b short: "classes of the noisy runs are mixed" appears with no class definition. "Saddle-node", "jump offset from the fold" and "ring" ("the ring is damped") are all undefined. "Noisy runs: mode N; noise-free: mode D" keeps the mode codes. "The red lines give the two failed results" refers to red text lines, not drawn lines.
   - Length: both short captions run to the limit, 650 words for F4a and 648 for F4b, against a cap of 650. That is long for a manuscript caption and leaves a 2-word margin.
   - Fix: one clause each, or move them to the full caption.

9. **LOW-MEDIUM — "all 84 such delays" is not in the drawn data.**
   - Where: F4a full caption (e).
   - Evidence: the drawn panel-e rows contain 80 delays at −1.5. That is 40 at level 0 and 40 at level 1, none at level 2. The 84 comes from an undrawn record (V1).
   - Fix: say "80 of the drawn delays", or name the source of the 84.

10. **LOW — figure and caption legibility and wording.**
    - F4b legend: the right column "Dark mark: median of the seeds with a value" ends about 0.12 in from the right edge, and the left "Grey bar … (P2)" ends about 0.1 in from the next column's swatch. This is tight but not clipped.
    - F4b (d): the "Duration (s), log axis" label sits against the right frame of (c).
    - F4a (e): the "(d), (e)" key swatch is a single brown square for 4 concentric marks.
    - The F4a full caption quotes "value blank in the stored table; threshold blank" for RB3(b). That is accurate, but it reads as a FAIL without a number. Pair it with the plain statement "ties at −1.5".
    - F4b short: the lead cites "median delay of the 10 seeds is negative from T_ramp 5.62341 s on" (true) as a failure consequence. It is not a failed check and its role is unexplained.

11. **LOW — F3 K5 wording.**
    - Where: F3 short caption.
    - Claim: "P1, P2, P3 and P5 coincide in (c) and (d) … P4a and P4b are drawn apart".
    - Evidence: in the F3 image, (c) draws only one arrow (the P1/P2/P3/P5 bundle plus the start circle). P4a and P4b appear only in (d) and (e). "Drawn apart" is true for (d) and (e), not (c).
    - Fix: "P4a and P4b are drawn apart in (d)".

**Checks 5, 6, 8 and 9: findings**
- (5) The plain wording of G6-D1, G6-D2, G6-D3, DL-163-D3 and MS11-C6 matches claim_limit_labels.md plain column. The numbers match: 0 of 6, 58.698 and 58.879 s, 0 to 2 of 13, and 10 s and 316 s.
- (8) K4: a regex scan of all `*_caption.txt` files (short and FS2/FS3) for K+digits, RB+digits, G+digits, D24, D43, MS-ids, DL-ids and underscore-digit names found zero hits. Class names (S+, D-tr and so on) remain in the FS3 caption. These are not check codes, so they are within K4 as written.
- (9) K5: all four fixes are true against the images.
  - FS3 (e): PASS and FAIL labels and the dashed 8-of-10 line sit only on the 120 s bars of ×0.5 and ×1. The ×2 120 s bar has neither.
  - FS1: the take-home and (d) sentences now say the same, 2.1e-4 and 6.1e-3.
  - FS2 (h): at 3 ms and 50 ms only the mean-of-r circle is drawn, and the caption says exactly that.
  - F3: see item 11 for the one residual wording point.

**Checked and fine**
- **Caption numbers against stored data.**
  - 181 ms = 58.879 − 58.698.
  - 97/225 = 43.1 percent.
  - 7 of 10 seeds.
  - 16 of 78 D-none runs in F4b.
  - Floor medians −0.000760, −0.0423 and −0.1051, and (e) ties at −1.5 at levels 0 and 1.
  - M2 jump offset 0.3458 to 0.00343.
  - M2 ring rate −25.66 to −24.34.
  - Raw-crossing coincidences 2, 11 and 11 of 13.
  - The 25.07 error of P5 linear in (a).
  - Noisy medians negative for T of 5.62 s and above (rate 0.00622 gives −0.13).
  - Seed counts above the panels match the non-NaN counts.
- **Image against caption.**
  - Red titles on (a) and (e) in F4a and on (e) in F4b.
  - Foot-band dash for the one run with no raw crossing.
  - Octagon in (a) at the P5 linear run, and five octagons in (c).
  - Open squares at the hold onsets.
  - Concentric hollow marks in (d) and (e).
  - Hysteresis dashed (linear) and dash-dot (sigmoid), and offset solid and dotted.
  - The ring error numbers are not drawn on the image.
- **FAILs.** All present: RB3(a) 0 of 6, RB3(b), RB6 181 ms, RB2 97 of 225 and 7 of 10.
- **FS2 and FS3 images** match the captions on the checked points: the red titles, the 97 of 225 bar, the 5% tolerance lines, and the "18 of 20 marks overlap" note.
- **Frame contact.** No mark or text is clipped by the frame in F4a or F4b. F4b (a) diamond at 4.5 stays inside the frame.

Files: `C:\dev\mpr-gamma-surge\figures\journal\F4a\F4a_journal_caption.txt`, `F4a_journal_caption_full.txt`, the same pair in `F4b\`, `figures\journal\supplement\F4a_source_data.csv`, `F4b_source_data.csv`, and `src\mprsurge\plotting\collide.py` (lines 563–590).

## Triage (mine; nothing is changed in this step: a fix of a caption or an image needs a rebuild, and L5 allows no rebuild after the review)

Checked by me against the stored data before this triage: item 2 is CONFIRMED. The values in jf4cap.py `eps_lo` and `eps_hi` are the minimum and maximum of the P1 linear ramp rates (3.5e-5 and 0.035); the M2 ramp table (A3, panels (f) and (g)) has the rates 4.607e-05 to 0.04607. The F4b full caption (f) states 3.5e-5 to 0.035 for the M2 values. That is a printed value that disagrees with the stored value (STOP RULE 12); it was not caught by the independent comparison because that comparison has no row for it. Reported, patched nothing.

| item | reading | action |
|---|---|---|
| 1 | CONFIRMED by the key: P5 linear is dash-dot in the image; the captions say 'linear (solid)'. The prediction key swatch is one dash-dot swatch for three lines. | next step (needs a rebuild): caption says 'linear (solid; P5 dash-dot)', key swatch neutral |
| 2 | CONFIRMED (above), STOP RULE 12 | next step: the (f) and (g) range from the A3 table, a new independent row |
| 3 | CONFIRMED in reading (the captions say the error numbers are 'in the source data'; I did not re-read the CSV rows for panel (c)); not verified by me | next step: add the rows, or reword to 'in Supplement F4a' |
| 4 | PLAUSIBLE: the counts are by the wording of the 'Failed checks' paragraph (jshort.further_count), the rule of earlier figures; not changed here | next step: decide what is counted |
| 5 | PLAUSIBLE, a wording gap | next step: one clause |
| 6 | PLAUSIBLE, a design point (the dagger marks cover the raw marks) | next step: ruling needed (smaller or lighter dagger) |
| 7 | PLAUSIBLE: the allow-list patterns are blanket per kind and panel by the ruled L2 form (only stored coincident positions and ruled mark sizes, one entry per kind and panel); the count of hits per entry is printed (374 and 271) | next step: narrow the patterns or add a count check |
| 8 | PLAUSIBLE: the term check passed (every DEFS term defined); the terms named are outside DEFS | next step: one clause each, within 650 words |
| 9 | PLAUSIBLE: the '84' is the draft text of the stored V1 reading; not re-derived by me | next step: check against the data, reword |
| 10 | LOW: legibility notes; none is a collision by the checker | next step: look again, no action now |
| 11 | CONFIRMED by reading the F3 image description: (c) has one arrow; 'drawn apart' holds in (d) | next step: 'in (d)' |

The review confirms the K5 fixes 1, 3 and 4 and the K4 scope (no code in any short caption, FS2 or FS3 caption). Everything open above needs a new build and so belongs to the next step; the recorded build of this step stays as built.
