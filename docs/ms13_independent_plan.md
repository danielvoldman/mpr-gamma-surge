# MS13 13q: plan of the independent recomputation (DL-508 to follow)

Written for: the reviewer who rules on the 13q result. Written BEFORE `scripts/ms13_independent.py` is coded or run. No figure code changes, no figure rebuild, no simulation, no tag. UNVERIFIED marks anything the plan does not state.

## 1. Structure

| Piece | Role | May import |
|---|---|---|
| `scripts/ms13_independent.py` | the independent code path. Own readers (json, numpy, csv, pandas/parquet) of stored files under `results/`. `compute()` returns a list of rows (figure, id, quantity, value, tolerance, shared flag, source). Writes nothing (no file under `results/`, none anywhere). | stdlib, numpy, pandas, `mprsurge.criteria` (frozen loader), `mprsurge.analysis.surge_metrics` and the frozen classifier modules, the 9i function (all marked "shared"). NOT `mprsurge.plotting.*`, `figures.py`, `figprov`, `claim_labels`, `captions`, nor any figure data step. |
| `scripts/ms13_independent_compare.py` | the comparison step (the only place that may import the figure data steps). Obtains the drawn values from `load_<ID>`/`prepare_<ID>` and the printed values from the take-home constants; compares; writes `docs/ms13_independent_results.md` and `.csv`. | `ms13_independent`, `mprsurge.plotting.figures` |
| `tests/test_ms13_independent.py` | tests of section 5 | both scripts |

The prompt (item 2) names `scripts/ms13_independent.py` as the writer of the two result files while item 4 forbids figure data steps inside the independent module. The two requirements are met by the split above: the module computes, the comparison step writes. UNVERIFIED reading; reported.

## 2. Row fields and comparison rules

`docs/ms13_independent_results.csv` columns: figure, id, quantity, independent value, drawn value, printed value, source of the drawn value, source of the printed value, equal (yes/no/n.a.), tolerance, shared flag, independent source.
Printed value: the token in the figure's take-home constant (the constants in `figures.py` are the captions' source; DL citations are those of the text). Drawn value: a key of the dict returned by `prepare_<ID>` (or a cheap derivation of it, written in the comparison step). Tolerance: integers, counts, class labels and strings exact; a printed float compares after rounding the independent value to the printed digits (tolerance = half a unit of the last printed digit); arrays compare with rel 1e-12 (abs 0 where both are exactly 0). A row without a drawn or without a printed value shows "n.a." for it.

## 3. Rows that are NOT independent ("shared")

A row is shared if its value passes through frozen code or through an output the original evaluation wrote:
1. F1 spectrogram (frozen `surge_metrics` spectrogram routine): the settings, the shape, the dB range and the peak bin.
2. F5c per-seed metrics (f_pk, onset, duration of the S9 and S9_ctrl records): recomputed through the frozen classifier.
3. Any value read from `results/ms10/eval/ms10_eval.json`, `results/ms10/10g/record_classes.tsv`, `results/A11/a11_evaluators.json` or `results/A11/a11_robustness.csv` (the A11 table, the RB status rows, the strip rows): they are the original evaluator's stored output; the row checks the figure against the stored value, not against a second evaluation.
4. Anything evaluated through the criteria loader or the 9i function (the spectral peak of RB9(b), class labels written by the frozen classifier into A7/A9 tables are READ, not recomputed: marked "stored class (frozen classifier)" in the source column and counted shared when the row is a class label).
All other rows read a primary stored file (run record json, npz series, A-analysis npz/json/parquet/csv) with own code and are independent. Class labels read from A7/A9 parquet columns are tallied by own code (independent tally of a stored label); the label itself is the frozen classifier's. These are marked shared = "label".

## 4. Quantities per figure (source file : key; method). Groups are expanded by loops over N, class, T_ramp, seed, path

### F5 (take-home: 760, 900, 84.4, 140, 296, 325, 29; RB4 0 of 14 and 64 of 64; 97, 225, 43.1, 203, 118, 173, 76.9; cells 1 of 4, 3 of 4; seeds per class per N; controls)
- A9 table `A9/a9_regime_map_v2.parquet`: cells per map (900, 325), D-tr and D-none per map (760/140, 296/29), headline row count, share 84.4 percent, T_ramp set of map 1 {120}, G5 threshold 27 cells and trigger flag.
- Subgrid `A9/a9_subgrid_agreement.parquet`: rows 225, d24 agree 97, ties 24, disagree 104, percent 43.1, needed ceil(0.9*225)=203, P-1 agree 173, ties 16, disagree 36, percent 76.9, categories agree 118 (own tally of `d24_ramp_class_counts` by the three Table 2.1 categories; reading ours).
- A11 table rows (shared): RB4 text "0 of 14 changed; 64 of 64 unchanged", RB2 subgrid text, RB1 cells "1 of 4", status words.
- Network cells (4): per-cell class lists from `ms10/10g/record_classes.tsv` and `ms10/eval/ms10_eval.json:rb1_cells` (shared); agree 1, disagree 3, G4 triggered.
- N sweep `S9` (10 seeds per N) and `C2_S9` (3 seeds per N): class tally per N and class (4 x 5 each; shared: stored class column), surge seeds per N (n rule 2 at 1e4, 5 at 3e4), "S+ in 6 seeds at 3e3", "NS in 1 at 1e4".
- F5c metrics (shared, frozen classifier): f_pk, onset, duration per seed per N; min, median, max per N; compared to the drawn arrays and the stored `N_sweep` entries.

### F1 (49.0 Hz, 58.698 s, 25 Hz, N 1e4, 3 of 3 S-sus, onset 12.0 s, 46.7 s, f_pk 49.0/48.5/49.0, T_ramp 10 s classes S-abs/S-rel/S-sus, controls, cells 1 of 4)
- Mean-field record `S5/ramp/S5ramp/S5ramp_0000_240de3ef73be.{json,npz}`: sample count 165001, t_on, eta start/H/peak, J0, J end, min and max of r and v, path end points.
- Network records `S8/S8_head/*` (6): sample counts (165000 at 120 s), r min and max per seed, raster spike count and active rows for seed 0 (300 rows), counts per 1 s bin tally.
- Class and metric words of the 120 s and 10 s seeds from `ms10_eval.json:rb1_headline` (shared), difference 58.698 - 12.0 = 46.698, headline reference class and onset, A_ref from `A8/a8_aref.json`, control classes (shared).
- Spectrogram (shared): window, step, taper, shape, peak frequency of the mean-field headline.

### F2 (Hopf at 2.896, supercritical, no fold, stable to 8; up-down 1.2e-3; A5 against S4 1.84e-3; network +13.2 to -2.5 percent above 3.0; below Hopf 0.22 to 0.31)
- `A5/a5_cycles.npz`, `A5/julia/a5.json`: Hopf eta_bar, hopf type word, number of branch points (483), unstable-cycle count, eta_max, fixed-point rows (119).
- `S4/devalle/*.npz` series: per-step v max and min over the read window recomputed from the series (own reader), up/down amplitude pairs, largest relative difference from 0.2 above the Hopf point.
- `S4/net/*.npz`, `S4/s4_summary.npz`, `S4/s4_net_summary.npz`: network amplitude per step, relative difference to mean field above 3.0 (min, max), floor below the Hopf point (min, max), step counts (30, 10 below).
- `A5/check/a5_check.json`: A5 against S4 maximum relative difference.

### F3 (100 Hz contour absent, largest cycle frequency 73.7 Hz; 25 Hz crossings by slice; cycle at ref_devalle 32.0 to 39.7 Hz)
- `A6/a6_freq_map.npz`, `A6/a6_summary.json`: per slice (Delta 0.05, 0.1, 0.3; 9 tau_d each) hopf eta, c25 and c100 counts, f max per slice, overall f max 73.69 and f min, point counts per slice (4629, 3926, 1798), tau_d at which the first 25 Hz crossing occurs per slice.
- `A4/a4_hopf_curves.npz`: curve sizes (30, 100), headline Hopf eta; `A4` against `A6` Hopf maximum difference.
- Path record json (6): eta start, peak, T_ramp, I_amp, Delta factor, end Delta (derived), legs.

### F4 (0 of 6 within one step; 33.1, 20.6, 12.7, 7.6, 4.4, 25.1 steps; 3 more with eta constant; 58.698 s, 115.2 s; 181 ms; floored delays -0.000760, -0.0423, -0.1051; sigma 0.0624; M2 offset 0.346 to 0.0034; 13 T_ramp)
- `A7/a7_ramp_metrics.parquet` (360 rows): rows per family (235 S5, 125 S13), tallies of in_range, testable, within one step, nocross; per-family arrays of delay, power, f_pk, duration per T_ramp; headline onset, predicted entry, Radau shift; floor delays per level; noise medians per T_ramp.
- `A3/a3_sn_ramp.parquet`: 13 rows, offset first and last, ring classes.
- `A4/a4_rb3a_summary.json`: predicted entry and h_working.

### F6 (169 = 140 + 29; labels a 48, c 32, f 24, g 64, h 1; NC1 13 of 13 and 5 cells; NC3 13 of 13; NC2 13 of 13 with I = 0 and 1; NC1 network S+; 20 S6 rows all D-tr)
- `A9/a9_regime_map_v2.parquet`: non-surge counts per map, primary failure labels tally, any-label tallies.
- `A10/a10_controls.csv`: NC rows by control and row type, class tallies.
- `A7/a7_s6_metrics.parquet`: 24 rows, 20 pre-registered, classes.

### FS1 (20 of 20 and 18 of 20; saddle/focus/node; 2.1e-4, 6.1e-3; 0 of 25727; 5.1 cycles per e-fold)
- `A1/a1_fixedpoints_2d.npz`: k1 pass counts, cusp position, fold arrays; `A2/a2_ring_map.npz`: focus count 25727, non-damped count, maximum cycles per e-fold inside the band, k4 numbers; `A0/a0_replication.csv` rows; `S1` series point counts.

### FS2 (K7, K8, K9, K10, K11 numbers: 0.09 percent, 0.14531, 7.1e-4, 4.12 ms, 2.42 against 2 percent, 13.4/25.0/42.2 percent)
- `A4/a4_hopf_curves.npz` (k9, k10, k11), `A5/check/a5_check.json` (K7 fit), `A6/a6_summary.json` (k10), `S3/s3_*_summary.json` and the S3 series files: K8 network against mean field relative peak difference; K10 relative changes recomputed from the frequency arrays.

### FS3 (4, 7, 2, 5 of 10; 5 against 2; controls 2/1/1 of 3; S10 classes; S11 8 and 7 of 10, controls 7 of 10; 97 of 225 against 203)
- `ms10/eval/ms10_eval.json:N_sweep`, `rb8`; `A11/a11_evaluators.json:rb2`; `A11/a11_robustness.csv` (all shared); `A9/a9_subgrid_agreement.parquet` (independent).

### FS4 (58.698 and 58.879 s, 181 ms; dt ladder; 5 to 43 percent; 0 of 3 and 2 of 3)
- `A7/a7_ramp_metrics.parquet` S13 families; `A11/a11_evaluators.json:rb5,rb6` (shared); network f_pk arrays.

### FS5 (26 synthetic cases; 306/400/172/24 of 500; 1.67 percent of 900; 1.2e-8 against 0.005; 14 of 900; 49.0 against 44.609 Hz; 4.391 against 0.5)
- `A8/a8_sensitivity.csv` (1880 rows): rows per dataset and variant, synthetic case count, changes vs V0; `A8/sensitivity/a8_whitenoise.csv`, `a8_reachability.csv`; `A11/rb9a_unit_level.json`; `A11/a11_evaluators.json` (RB9, RB10; shared); `A6/a6_summary.json` cycle frequency.

Exact counts of rows per figure are fixed when the module is run and are reported in `docs/ms13_independent_results.md` (header table) and in the 13q result entry; this plan fixes the sources and methods, not the number of loop-expanded rows.

## 5. Tests (`tests/test_ms13_independent.py`)

1. The import graph of `scripts/ms13_independent.py` (parsed with `ast`, followed one level into `mprsurge` imports) contains none of `mprsurge.plotting`, `figures`, `figprov`, `claim_labels`, `captions`, `style`, `nordlie`.
2. Running `compute()` leaves `results/` byte-identical in file listing (names, sizes, mtimes) and writes no file.
3. The F5 counts 760, 140, 296 of 325, 97 of 225, 118, 173 are reproduced exactly.
4. A copy of one stored table in a temporary directory with one altered value makes the corresponding row report "not equal" (no real file is touched; `compute(root=tmp)`).

## 6. Stop rule

Any independent value that disagrees with a printed or drawn value stops the step: both values, the quantity and the figure are reported, nothing is patched.

## 7. Coverage as run (added after the module was written; nothing above is changed)

Quantities NOT recomputed, although the sections above name their sources (reported, not dropped):
- F1: the spectrogram is recomputed only as a window count (frozen routine); the dB range, the peak bin and the shared range are not; the per-second spike-count tally is not.
- F2: the per-step S4 amplitudes are read from the stored summaries (`s4_summary.npz`, `s4_net_summary.npz`), not recomputed from the S4 series; the series are only counted.
- F4: the noisy arrays per seed, the start-distance families (sd05, sd30), the A3 per-T arrays and the hold-flag count are not compared with the drawn arrays; the six family tables (delay, f_pk, power, duration per T_ramp) are.
- F6: the per-cell failure-label arrays, the S6 onset and f_pk tables and the NC1 mode-N count arrays are not compared with the drawn arrays; tallies are.
- FS1: no K5 number; the K4-net statement is text. FS2: K7 is read from the stored check file (shared); the K8 existence statements (limit cycle at 5 ms, fixed point at 50 ms) are not recomputed.
- FS4: the zero onset shift at T_ramp 10 s and 316.2278 s and the delta0 and rtol settings are read from the stored RB5 rows (shared). FS5: "2 of the plan's 8 A8 ring items" (DL-161, DL-163), the class changes per variant (panel c) and the reachability shares are not recomputed.
- F5: cell agreement uses our reading of the Table 2.1 correspondence (D-tr with a surge class, D-none with NS or S-sus), UNVERIFIED; the original evaluator's own cell flags are carried as a shared row.
Reading of two definitions that the first run exposed (the module, not a figure, was changed): see the 13q result entry.
