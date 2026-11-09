# MS13 13t-11 P2: audit of the alt texts of all 13 journal figures (DL-699, DL-700, DL-701)

## Method and coverage
1. Listing (scripts/ms13_list_alt_claims.py, read-only): 107 alt-text sentences hold a number or a claim word (largest, smallest, at most, at least, up to, N to M, all, none, only, N of M, rises, falls, ...); 379 number tokens on the 13t-10 build, 406 on this build (71 and 83 not found in the caption of the same figure).
2. Executable table (src/mprsurge/plotting/jaltaudit.py, 76 checks, run on the RECORDED alt texts and the RECORDED source data of this build, test tests/test_ms13_13t11.py): the table at the end. All 76 equal. Coverage: every number of an alt text is either in a check, in the caption of the same figure, or in a short allow-list with a stated reason (axis limits of F2 (a), FS2 (a), FS4 (a): drawing constants; 49 Hz in F3: the stored spectral peak, compared with the stored value in the test; the four N of F5c in the notation 1e3 to 3e4; the dashed target lines 0.99 and 1.01 of FS2 (j)); 0 numbers left over.
3. Image texts (R5, scripts/ms13_list_image_claims.py, 216 texts with a claim word or a number read from the drawn figures): see the last section.

## Wrong alt-text claims found (before the build) and fixed (wording only; images unchanged)
| # | figure | claim in the alt text | stored value or image | fix |
|---|---|---|---|---|
| 1 | F4a (a) | 'delays from about 0 to about 3' | stored minimum -0.092 (P2 linear), maximum 2.0 (P1) | 'from about -0.1 to 2.0' (true minus), read from the arrays; STOP if different |
| 2 | F4a (a) | 'most of them rising as the ramp slows' | the delays rise with the ramp RATE (the drawn axis): slowest ramp 0.10, fastest 2.0 in P1; 6 of 6 series are higher at the fastest ramp | 'rising with the ramp rate (6 of 6 series ...)' |
| 3 | F4b (d) | 'the smallest duration the classifier can give' | 38 of 113 durations under T_ramp 60 s are below 1 s (0.300 to 0.937 s); 72 at T_ramp >= 60 s have the minimum 1.0 s exactly | 'durations are 1 s or more for ramp durations of 60 s or more; some faster ramps give shorter durations, down to 0.30 s' (short, full, alt, R1) |
| 4 | FS4 (a) | 'a cross at the onset' (caption: 'the small cross') | the image draws a small hollow downward triangle (nabla, style fs4_cross), the blue mark visible through it | 'small hollow downward triangle' (caption and alt) |
| 5 | FS4 (c) | 'the delays are small and negative' | level 0: -0.0026 to +0.0033 (16 of 40 values positive); level 1: -0.048 to -0.037; level 2: -0.11 to -0.096 | per level: smallest, largest, median, read from the arrays |
| 6 | F6 (a) | 'the largest bars are label g (primary 51 and 13 ...) and labels a and c' | map 1: g 51, a 48, c 32; map 2: f 16 is above g 13 | 'the largest primary bar is label g (51) in map 1 and label f (16) in map 2 (any label, map 1: label g (70))', from the counts |
| 7 | F1 (i) | 'the top colour is 116 spikes and more (492 of 49500 cells)' | 492 cells are above 116; 512 reach 116 | 'the top colour starts at 116 spikes (492 of 49500 cells have more than 116)' |
| 8 | F3 (a) to (c) | 'tall black bar' | the image has a thin vertical line with a white outline (the caption was corrected in 13t-10) | 'thin black vertical line' |
| 9 | F2 (b) | 'the up and down sweeps coincide' (no scope) | the mean-field amplitudes differ by 0.475 at the Hopf point and by at most 0.0012 (relative) from 0.2 above it | scope added, number from the data |
| 10 | FS4 (i) | 'for each step and seed' | the points are the two time steps at which V_p 200 was run (3 seeds each) | the two steps named (wording) |

## Ruled wording or image reading (stay, marked)
- Statements about what an image looks like, not compared with a number: F1 (g), (h) 'bright rising ridges', F1 (k) 'regular vertical volleys', FS1 (b) 'the test point is on the grey boundary' (the coloured region begins 0.2 left of the point at J/sqrt(Delta) 14.3), FS1 (e) 'seven bursts, one per period' (checked: 42 peaks = 7 bursts of 6), F2 'lie on the lines' and 'lie close to them'.
- F1 (e) 'symmetric about a small offset' is a description of the stored extremes -4.32 and 4.08 (mid-point -0.12), not a claim of exact symmetry.
- The ruled A6 take-home sentence about the 25 Hz and 100 Hz contours (F3) and the ruled limits stay as in the captions.
- Open (listed, not changed; needs a ruling): the alt texts of F5 and F5c write N as 1e3, 3e3, 1e4, 3e4 whereas captions and images use 1000, 3000, 10,000, 30,000 (V4, W3).

## Image texts (R5)
216 texts of the 13 drawn figures hold a claim word or a number. Wrong: ONE, the F4b legend 'Dotted line in (d): 1 s, the smallest duration' (fixed to 'Dotted line in (d): 1 s' after the longer wording ran past the right edge of the key; attempt 2 of 2). Checked equal or built from the stored arrays: F4a notes 'y range -0.127 to 0.0202' and '-1.58 to -0.863' (own axis limits), 'Prediction: 0 of 6 testable runs within one step', 'main example onset differs by 181 ms (1 ms allowed)'; F4b '7 of 10', '97 of 225', '13 of 13'; F5 '1 of 4', '3 of 4'; FS2 '18 of 20 marks overlap', 'residual 2.42 percent (2 allowed)'; FS3 'At least 8 of 10 seeds needed', '97 of 225'; FS4 'First halving: change of 5 to 43 percent'; FS5 'D-none (61)' and the window labels. No other wrong image text found.

## What the audit cannot cover
A statement about what the image looks like; a right number from the wrong stored quantity; the words around a number; a number that also stands in the caption of the same figure is counted as covered by the caption audits (N2, O2, the independent comparison), which is weaker than a comparison with the source data. The audit reads the recorded build; the builders are covered by the builder tests of tests/test_ms13_13t11.py.

## Table of the 76 executable checks (figure, panel, claim, value in the alt text, stored value, equal)
| figure | panel | claim | value in the alt text | stored value (source data) | equal |
|---|---|---|---|---|---|
| F1 | a | eta_bar from ... to (rises linearly between the guide levels) | 1.396, 4.896 | 1.396046, 4.896046 | yes |
| F1 | a | ramp from ... s to ... s | 5, 125 | 5.001, 124.999 | yes |
| F1 | a | mean-field onset | 58.698 | 58.698 | yes |
| F1 | b | J(t) from ... to ... | -21, 0 | -21.0, 0.0 | yes |
| F1 | c | mean-field rate below ... before the onset | 0.185 | 0.18456 | yes |
| F1 | c | upper edge peaks at (largest block maximum) | 2.65 | 2.653677 | yes |
| F1 | d | raw first crossings recorded from ... to ... s | 50.170, 50.924 | 50.17, 50.924 | yes |
| F1 | d | classifier onset | 12.0 | 12.0 | yes |
| F1 | e | v from ... to (smallest block minimum, largest block maximum) | -4.32, 4.08 | -4.318522, 4.081629 | yes |
| F1 | g | frequency 0 to ... Hz | 150 | 150.0 | yes |
| F1 | i | rows | 300 | 300.0 | yes |
| F1 | i | top colour starts at ... spikes; N of M cells have more | 116, 492, 49500 | 116.0, 492.0, 49500.0 | yes |
| F1 | j | window from ... s | 12.000 | 12.0 | yes |
| F2 | a | Hopf point | 2.896 | 2.896046 | yes |
| F2 | a | cycle maximum and minimum of v at eta_bar 8 | 10.4, -10.8 | 10.432828, -10.757365 | yes |
| F2 | a | mean-field steps each way | 61 | 61.0 | yes |
| F2 | a | network steps each way | 15 | 15.0 | yes |
| F2 | b | amplitude rises to about ... | 21 | 21.190124 | yes |
| F2 | b | network amplitude below the Hopf point | 0.22, 0.31 | 0.222577, 0.310916 | yes |
| F2 | c | relative difference from ... to ... percent | 13.2, -2.5 | 13.170139, -2.480113 | yes |
| F3 | a | largest frequency of panel (a) | 60.3 | 60.284043 | yes |
| F3 | a | slices with a 25 Hz crossing in (a) | 7 | 7.0 | yes |
| F3 | a | maximum on (a) (no 100 Hz contour) | 60.3 | 60.284043 | yes |
| F3 | b | largest frequency of panel (b) | 73.5 | 73.496876 | yes |
| F3 | b | slices with a 25 Hz crossing in (b) | 6 | 6.0 | yes |
| F3 | b | maximum on (b) (no 100 Hz contour) | 73.5 | 73.496876 | yes |
| F3 | c | largest frequency of panel (c) | 73.7 | 73.692072 | yes |
| F3 | c | slices with a 25 Hz crossing in (c) | 3 | 3.0 | yes |
| F3 | c | maximum on (c) (no 100 Hz contour) | 73.7 | 73.692072 | yes |
| F3 | a | colour scale of (a) to (c) | 9.8, 73.7 | 9.772593, 73.692072 | yes |
| F3 | d | Hopf curve reaches eta_bar ... at Delta 1 | 7.30 | 7.297369 | yes |
| F3 | e | up legs from ... to ... (eta_bar) | 1.396, 4.896 | 1.396046, 4.896046 | yes |
| F4a | a | delays from about ... to ... | −0.1, 2.0 | -0.092041, 2.0 | yes |
| F4a | c | errors of the testable runs, ... to ... steps | 4.4, 33.1 | 4.404772, 33.148127 | yes |
| F4a | d | medians of the three levels | -0.0008, -0.042, -0.105 | -0.00076, -0.042323, -0.10506 | yes |
| F4a | a | ramp-rate axis from ... to ... | 3.5e-5, 0.035 | 3.5e-05, 0.035 | yes |
| F4a | e | delays tie at ... at the two lower levels | -1.5 | -1.5 | yes |
| F4b | f | jump offset from ... to ... (slowest and fastest ramp) | 0.0034, 0.346 | 0.00343, 0.34575 | yes |
| F4b | g | fitted rate between ... and ... per s | −25.7, −24.3 | -25.660858, -24.337272 | yes |
| F4b | g | damped at N of 13 | 13 | 13.0 | yes |
| F4b | d | duration floor (smallest duration at T_ramp >= 60 s) | 1 | 1.0 | yes |
| F4b | d | shortest duration of any ramp | 0.30 | 0.3 | yes |
| F5 | a | D-tr cells | 760 | 760.0 | yes |
| F5 | a | D-none cells | 140, 900 | 140.0, 900.0 | yes |
| F5 | c | agree, disagree, tie | 97, 104, 24 | 97.0, 104.0, 24.0 | yes |
| F5 | d | agree, disagree, tie (post-hoc view) | 173, 36, 16 | 173.0, 36.0, 16.0 | yes |
| F5 | e | D-tr and D-none cells of the 325 | 296, 29, 325 | 296.0, 29.0, 325.0 | yes |
| F6 | d | onset about ... to ... s | 6, 160 | 6.0, 160.0 | yes |
| F6 | e | P3 and P4b and P2 near ... to ... Hz | 48, 49.5 | 48.0, 49.5 | yes |
| F6 | e | P4a near ... Hz | 45 | 45.0 | yes |
| F6 | e | P3 at drive 2 near ... to ... Hz | 39, 40.5 | 39.0, 40.5 | yes |
| FS1 | b | focus frequency from ... to ... Hz | 0.24, 153.4 | 0.242401, 153.408936 | yes |
| FS1 | c | largest cycles per e-fold | 5.10 | 5.100391 | yes |
| FS1 | d | r from ... towards ... | 0.0811, 1.3732 | 0.081134, 1.373244 | yes |
| FS1 | d | first peak near ... | 2.9 | 2.867124 | yes |
| FS1 | d | fit window ... and ... ms | 114, 400 | 114.0, 400.0 | yes |
| FS1 | a | cusp | -1.732, 7.796 | -1.732051, 7.796217 | yes |
| FS1 | a | test point (eta_bar/Delta, J/sqrt(Delta)) | -5, 15 | -5.0, 15.0 | yes |
| FS2 | a | Hopf point | 4.12 | 4.120858 | yes |
| FS2 | i | largest ratio of Delta to eta_bar | 0.1453 | 0.145309 | yes |
| FS2 | j | largest deviation from 1 | 0.00071 | 0.00071 | yes |
| FS3 | a | surge-class ramp seeds at the four N | 4, 7, 2, 5 | 4.0, 7.0, 2.0, 5.0 | yes |
| FS4 | a | default onset | 58.698 | 58.698 | yes |
| FS4 | a | Radau onset | 58.879 | 58.879 | yes |
| FS4 | a | Radau minus default in ms | 181 | 181.0 | yes |
| FS4 | g | changes above the bound | 8, 9 | 8.0, 9.0 | yes |
| FS4 | g | range of the changes (percent) | 0, 55 | 0.0, 55.0 | yes |
| FS4 | d | delays at levels 0 and 1 | -1.5 | -1.5 | yes |
| F6 | a | largest primary bar of map 1 and of map 2 | g, 51, f, 16 | g, 51.0, f, 16.0 | yes |
| F6 | a | largest any-label bar of map 1 | g, 70 | g, 70.0 | yes |
| F6 | a | primary label counts of both maps (a, c, f, g, h) | 48, 32, 24, 64, 1 | 48.0, 32.0, 24.0, 64.0, 1.0 | yes |
| F2 | b | largest relative difference of the mean-field up and down amplitudes from 0.2 above the Hopf point | 0.0012 | 0.001163 | yes |
| FS4 | c | raw-crossing delays of level 0: smallest, largest, median | −0.0026, 0.0033, −0.00076 | -0.002613, 0.003279, -0.00076 | yes |
| FS4 | c | raw-crossing delays of level 1: smallest, largest, median | −0.048, −0.037, −0.042 | -0.047529, -0.037058, -0.042323 | yes |
| FS4 | c | raw-crossing delays of level 2: smallest, largest, median | −0.11, −0.096, −0.11 | -0.109683, -0.095975, -0.10506 | yes |
| FS5 | e | records that are not NS (six windows) | 306, 400, 172, 24, 2, 0 | 306.0, 400.0, 172.0, 24.0, 2.0, 0.0 | yes |
