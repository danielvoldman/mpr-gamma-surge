# MS3 gate report: mean-field timing gate

Plan: Table 11.1 MS3, sections 9.2 and 9.3, Table 9.1, D36, T23, T24. Gate: "Predictions within allowance". Rule (9.2 step 3): prediction <= 1.5 x the Table 9.1 allowance. Measurements and decisions: DL-096 to DL-104. Raw outputs: `results/timing/` (3c, 3d) and `results/timing/clean/` (3f, clean re-time), git-ignored. Machine: Ryzen 5 5600, High performance plan, sleep never on AC, browsers and VLC closed; six VS Code `msedgewebview2` processes stayed open (residual caveat). Paths provisional and UNVERIFIED until A4 (MS5).

## Method
Mean-field cells timed three times (single run alone) or as 10 concurrent copies x 3 batches (pooled per-run median over 30 copies, as DL-102). Each family is extrapolated from its matching cell (`configs/timing_families.yaml`, `python -m mprsurge.analysis.timing --predict --workers 10 --results-dir results/timing/clean`). Per DL-103: judged at 10 workers, not the 6 of D-7 (logged departure, below); the single-run row judged alone. Map 1 is a weighted estimate over its 900-cell grid (DL-100; Delta linear, UNVERIFIED).

## Rows (10 workers)

| Row | Limit | 3d (DL-102) | Clean | Change | Verdict |
|---|---|---|---|---|---|
| Single run alone, headline | 148.5 s | 117.3 s | 101.4 s | -13.6% | pass |
| Single run alone, delta_0.6 | 148.5 s | 107.5 s | 93.5 s | -13.0% | pass |
| Single run alone, delta_0.01 | 148.5 s | 203.6 s | 178.3 s | -12.4% | **fail** (+20%) |
| Sweeps S2/S5/S6, headline rate | 1.43 h | 1.18 h | 0.97 h | -17.8% | pass |
| Sweeps, P5 rate | 1.43 h | 1.45 h (fail) | 1.14 h | -21.4% | pass |
| S7 map 1, weighted | 6.15 h | 5.23 h | 4.44 h | -15.1% | pass |
| S7 map 2 + noisy subgrid | 3.30 h | 2.57 h | 2.20 h | -14.4% | pass |
| S5 baseline-only mode N (MS7) | 108 s | 53 s (a) | 121 s | (a) | **fail** (+12%) |
| S11 + S16 | 60 min | 26.0 min | 21.5 min | -17% | pass, partial |
| S2 + S4 (row S1-S4, A1-A6) | 45 min | 4.1 min | 3.4 min | -17% | pass, partial |
| S13 Radau pass set (indicative) | 1.5 h | 10.1 min | 7.9 min | -22% | pass, partial |

(a) Not like for like. 3d divided the alone Heun rate by 5.90. The clean run measures mode N under 10 copies: 2.34 s per run against 0.61 s alone. A supplementary 1200 s-ramp run (22.67 s) shows the slowdown is a rate (1.51e-7 against 3.65e-8 s per step, offset near zero), not a start-up cost. The 3d Heun parts were therefore low.

Headline cell under 10 copies: 201.8 s (3d) to 162.8 s (clean), throughput 177.6 to 220.4 runs/h, speed-up 6.2 (3d: 5.90). Partial rows are lower bounds: S1, S3, A1 to A6, S12 mean field and the S13 ladders have no count or timing cell here.

## Cut order
Section 9.3 step 5 (drop the 562 s and 1000 s ramps from P5 and the start-distance runs) was conditional on the P5-rate sweeps still failing (DL-103 (3)). They pass, so nothing is cut (DL-104). Steps 1 to 4, 6 and 7 do not apply to a failing row. No cut-order step covers the two failing rows.

## Result
**Not a clean pass.** The gate "all mean-field rows meet the rule, or the cut order is applied until they do" is met for every row except two, and the cut order has no step for either:
1. Single run at Delta = 0.01 alone, 178.3 s against 148.5 s. It is the edge of map 1, which passes as a family.
2. S5 baseline-only mode-N runs, 121 s against 108 s, a 2 min stage at MS7.
Both are for the user to rule on (accept as an exception, change the row or its allowance, or reduce the work). No S-run has started. The 24 h cap (D36) is not judged.

## Departure from D-7
D-7 (DL-094) fixed 6 workers for the extrapolation. DL-103 (1) judges the launch rule at the 10 workers actually used. At 6 workers the 3d speed-up was 4.16, and the sweeps, map 1 and map 2 failed; the 6-worker column stays in DL-102. D-7 is otherwise unchanged.

## Carried forward, still open
- 24 h cap (D36): not judged until the network rows exist (qif_network, MS5).
- Paths provisional and UNVERIFIED until A4; the headline is re-timed after A4 (MS5, T23).
- /permissions check (DL-051).
- Defender exclusion for the repository and .venv (9.1): not confirmed here.
- K5 definition: own reading, UNVERIFIED (DL-082).
- Map 1 Delta spacing: taken as linear, UNVERIFIED (DL-100); log spacing gives 6.02 h at 6 ideal workers in DL-101, not re-run.
- DL-073 (step-onset filter bias) at MS7.
- Possible private remote backup.
- Also open from MS3: 20 steps per tau conversion of Table 9.1 step counts, S13 reading of RB6 (DL-100 (3)), sigma 1e-3 not calibrated (D-4).

## Review
Fresh-context review of the MS3 diff was not run in this session; it is not part of the 3f gate rows and is left to the user to request.
