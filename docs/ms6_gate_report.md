# MS6 gate report (M3 structure: S4, A5, A6; G2 and D40)

Binding source: `docs/plan.md` (Table 11.1 row MS6; 4.3 and Table 11.2 gate G2; Table 7.1 K7, K8, K9, K10; 5.2 A5, A6; 6.2 S4; 7.2 D40; D23, D40, CP23). Decisions: DL-125 to DL-133 (this review and gate: DL-134). Numbers are from the saved, git-ignored results (`results/A5`, `results/A5/check`, `results/A6`, `results/S4`, `results/S3`, `results/G2`) as in the DL entries; nothing was re-run for this report. Gate wording (Table 11.1): "A5 vs S4 amplitudes within 2% (points next to eta_H excluded); frequency map done". Unlocks: G2, confirm D40, MS7.

## Gate items

| Item | Value | Threshold | Verdict |
|---|---|---|---|
| A5 continuation | Supercritical Hopf at ref_ceni (tau_d 4.120866 ms) and at ref_devalle (eta_H 2.8960463); A_ref (v amplitude, ref_devalle, 5 ms) 5.51136. A5 Hopf points equal A4 to 2.1e-6 relative (4.120858 ms, 2.8960462) | Hopf points equal A4; supercritical at ref_ceni (K7) | Pass (DL-126) |
| A5 vs S4 amplitudes, ref_devalle | v peak-to-peak, S4 mean field against the A5 branch, up and down sweeps separately. 39 judged points per direction (eta_bar 3.096 to 6.896). Max relative difference **1.84e-3 up, 6.8e-4 down**, both at eta_bar 4.196 | 2 percent (relative amplitude) | **Pass**, 1.84e-3 against 2e-2 |
| Points next to eta_H | Excluded: \|eta_bar - eta_H\| <= 0.1 (one S4 step), steps 2.796, 2.896, 2.996. 2.796 and 2.896 have no A5 cycle (branch starts at eta_H); 2.996: S4 1.3660 up, 1.3738 down against A5 1.3724, differences -4.7e-3 up, +9.7e-4 down. Reported, not judged. 20 points per direction below eta_H have no A5 cycle | exclusion per gate wording and CP23 | The only excluded point with an A5 value is also under 2 percent, so the exclusion does not change the verdict |
| A5 vs S4, ref_ceni (tau_d sweep) | 9 cycle points per direction (4.25 to 6.5 ms), max 1.49e-4 | 2 percent | Pass. No exclusion applied (none ruled; nearest point 0.129 ms above the Hopf point, settled) |
| Frequency map (A6) | 37 slices run (27 tau_d, 5 J, 5 K10), one Hopf point on each eta_bar slice. 25 Hz contour exists for Delta 0.05 (tau_d >= 3 ms), Delta 0.1 (tau_d >= 5 ms), Delta 0.3 (tau_d 13, 22, 36 ms only); the 100 Hz contour does not occur on eta_bar 0 to 8 (max 73.7 Hz; 71.3 Hz in the (eta_bar, J) plane) | "frequency map done" | **Done**, grids ours (UNVERIFIED, DL-131, kept by DL-132 (b)). Some cycle branches stop short of eta_bar 8; the reason was not examined |

## Deferred items

**K7 amplitude half (deferred from MS5).** Rules pre-registered in DL-126 D-3, window 0.1 to 1.0 ms above tau_d^(H), 7 points (4.25 to 5.05 ms), A^2 linear in tau_d - tau_d^(H):
- R^2 0.99691 against 0.99: pass.
- No hysteresis, up against down 2.0e-7 against 2 percent: pass.
- Largest residual **2.42 percent** of the largest A^2 against the pre-registered **2 percent: FAIL.** This is a **reported failure of a pre-registered rule**. Window and tolerance were not revised (DL-130 (a)). The 2 percent tolerance was our own choice (UNVERIFIED, not in the plan). The same rules on the A5 branch give 2.42 percent as well, so the miss belongs to the model branch, not to S4 settling. A^2 is concave in tau_d: local slope 5.29 per ms at 0 to 0.05 ms above the Hopf point, 3.92 per ms at 0.6 to 1.0 ms; the residuals form a systematic bow.
- **POST HOC, exploratory, not part of the verdict:** a fit on A5's own 11 points in 0.05 to 0.3 ms above the Hopf point (a window chosen after seeing the failure) gives R^2 0.999984, largest residual 0.22 percent. It shows the near-Hopf linear regime; it does not replace the pre-registered result and cannot change it.
- Cross-check: S3 mean-field v peak-to-peak against A5 at the same tau_d: +8.3e-5 (4.95 ms) and +1.4e-4 (8 ms).
- Status: **K7 amplitude half is not passed as pre-registered** (R^2 and hysteresis pass, residual rule fails). The existence of a supercritical Hopf (DL-126) holds.

**K10 (non-blocking).** **Not reproduced as worded.** At ref_ceni (eta_bar 1, Delta 0.05, J -20) the oscillatory interval is 4.14 to 50 ms and the cycle frequency falls from 21.01 to 9.75 Hz, inside 5 to 30 Hz +/- 10 percent, monotone: both pass. The J dependence over J -40 to -5 fails: 13.4 / 25.0 / 42.2 percent at 8 / 20 / 40 ms for the linear definition (DL-115, reproduced), 13.2 / 24.6 / 40.1 percent counting unstable points only. On cycle points the criterion cannot be evaluated: cycles exist for one J at 8 ms and two J at 20 and 40 ms (6.5 and 7.4 percent over those two). K10 keeps its definition from the plan and DL-115 (DL-132 (a)); it is not revised to pass. The source claim is single-source (UNVERIFIED). Non-blocking.

## D40 confirmation

**Confirmed by the owner (DL-132 (c)):** the headline example (P2 at ref_devalle, T_ramp = 120 s, linear profile, I = 0) stands. A6 cycle frequency at ref_devalle is 32.0 Hz at the Hopf point to 39.7 Hz at eta_peak 4.896 (36.26 Hz at eta_bar 4), at least 25 Hz everywhere in the oscillatory region, so the DL-040 overturn test (spectral peak below 25 Hz) is not triggered. The test is the owner-ruled DL-126 D-4 reading.

**Frequency finding.** The linear Hopf frequency at ref_devalle is **32.01 Hz** (Im lambda 2.0112 /tau at eta_H), matching the A6 cycle start. The **36.1 Hz** quoted in DL-115 and `docs/ms6_plan.md` next to Im lambda 2.011 /tau is the linear frequency at eta_bar 4, **36.07 Hz** (Re lambda +0.214, Im lambda 2.266 /tau; an unstable focus, not a damped one). The old note mixes the Hopf-point Im lambda with the eta_bar 4 frequency and Re lambda. The K8 comparison (36.1 Hz against the 36.27 Hz S3 peak) is correct as a value at eta_bar 4. The earlier entries are not edited.

## G2 outcome

Judged by the owner on the DL-132 readings (DL-133). **(a)** met: limit cycles at or above 25 Hz exist with Delta below critical (0.1453 eta_bar, K9) in the cells searched, including the headline cell (32.0 to 39.7 Hz); not met at every cell (ref_ceni cycles are 9.7 to 21.0 Hz). **(b)** met for the P1/P2 path at ref_devalle (stable focus at eta_H - 1.5 = 1.396, Re lambda -0.510 /tau; Hopf crossing at 2.896; stable cycle above); the start states of the other 31 A6 slices were not evaluated. **(c)** not rejected: the plan default, which A4 to A6 cannot test. **No G2 trigger fires: the project stays on M3, and M4 is robustness only.** This rests on the DL-132 readings, UNVERIFIED where the plan leaves room ("Delta below critical", "stable focus", the search range eta_bar 0 to 8, the 25 Hz as a continuation frequency). Rejecting (c) would move G2 to M4 regardless of (a) and (b).

## Network against mean field (information only, no criterion)

S4 network, N = 1e4, seed 0, 15 values up and down (30 steps), 63.4 s (DL-128). Above eta_H + 0.1 (9 values, up and down), network v peak-to-peak against mean field differs by up to 0.132 (+13.2 percent at eta_bar 3.296, falling through zero near eta_bar 5.7 to about -2.5 percent at 6.496); r peak-to-peak differs by up to 0.157 (+15 percent at 3.296, -12 percent at 6.496). The network v is the mean V of non-refractory neurons within the cut, so the definition differs as well as the size. Noise floor below eta_H: r peak-to-peak 0.042 to 0.057 (mean 0.052). At eta_H the network r peak-to-peak is 0.154 up, 0.159 down, about three times that floor. S3/5g network values at ref_ceni (r peak-to-peak 0.290 at 4.95 ms and 0.493 at 8 ms against mean field 0.2066 and 0.4266) are in DL-129. No 2 percent criterion applies to the network.

## Fresh-context review

A subagent that had not seen the work read `docs/ms6_plan.md`, DL-125 to DL-133, the MS6 gate wording, the K7/K8/K9/K10, G2 and D40 rows of the plan, and the saved results, and recomputed. **Numbers: all others match**, including the A5-vs-S4 check (1.84e-3, 39 judged points, exclusion rule), the K7 numbers, the K10 and frequency numbers, the G2 and D40 statements and the test counts. Nine discrepancies in the DL text, none of which changes a verdict. Committed DL entries are not edited; the report uses the correct values (above), and the discrepancies are listed here:

1. **DL-129, network v trend.** Says the difference "falls ... to a minimum of -2.5 percent near 4.5, then rises to +12.4 percent at 6.496". Saved: +13.2 (up) / +12.4 (down) at 3.296, falling monotonically through zero near 5.7, about -2.3 / -2.5 at 6.496. The +12.4 is the down branch at 3.296. Max 0.132 is right. The report above uses the corrected shape.
2. **DL-127, hysteresis size.** "Up and down agree to 3e-4 or better" from 3.096 to 6.9. Saved maximum is 1.16e-3 at eta_bar 4.196 (same point as the A5-vs-S4 maximum). Correct statement: 1.2e-3. Still far under 2 percent.
3. **DL-127, "S4 0.0760 against A5 0.1100 at eta_H".** Unsupported: DL-129 says there is no A5 value at eta_H, and 0.1100 was not reproducible from `a5_cycles.npz`. The report treats eta_H as having no A5 cycle (as DL-129).
4. **DL-128, network amplitude at eta_H.** "About 0.05 ... the whole network amplitude at eta_H" contradicts DL-129 (0.154 / 0.159, about three times the floor); DL-129 is right. Also "stable-side drifts 0.1 to 0.18" is partly true (drifts of 0.005 and 0.016 also occur) and "FFT peak 100 to 460 Hz" should read about 95 to 460 Hz.
5. **DL-129, tau_d^(H) label.** "4.120866 ms (A5/A4 value; 4.120858 in DL-115)": 4.120866 is the A5 value, 4.120858 the A4 value (relative difference 2.1e-6, as DL-126). Fits use the A5 value throughout.
6. **DL-132, "damped-focus frequency at eta_bar 4".** At eta_bar 4 Re lambda is +0.214, an unstable focus; the 36.07 Hz value is right, the label is loose.
7. **DL-126 and DL-131, 8 ms frequency** 17.97 against 17.98 Hz: rounding.
8. **DL-133** forward reference to DL-134: resolved by DL-134 being written.
9. **DL-129, "Points below eta_H (20 per direction) not comparable"** overlaps the excluded step 2.796 (cosmetic): 39 judged + 3 excluded + 19 other below = 61.

Also noted: DL-131 "largest increase 0 Hz" for the K10 monotone check; the true largest step is -0.038 Hz (strictly decreasing), harmless. Not recomputed by the reviewer: the K10 linear percentages (taken from DL-115 and DL-124) and "no Hopf for J > 0 in 240 cases". No discrepancy involves the A5-vs-S4 check, the K7 verdict, the K10 statement, the frequency finding, or the G2 and D40 statements.

## Departures and failures, stated plainly

1. **K7 amplitude half fails its pre-registered residual rule** (2.42 against 2 percent). Reported, not tuned. The post hoc fit is exploratory.
2. **K10 not reproduced as worded** (J dependence 13 to 42 percent). Non-blocking; definition kept.
3. **Frequency note in DL-115 and the MS6 plan is inconsistent** (36.1 Hz is the eta_bar 4 value, not the Hopf-point value 32.01 Hz). Not edited in committed entries.
4. **Not everything is covered by the readings.** G2 (a) is met in the cells searched, not everywhere; G2 (b) is checked only for the P1/P2 path at ref_devalle; (c) is a default, not a test. A6 grids and the Delta used for the (eta_bar, J) plane are ours (UNVERIFIED). Some cycle branches end before eta_bar 8, unexamined.
5. **Design choices ours, UNVERIFIED:** the S4 ref_ceni tau_d sweep (not in the plan), the exclusion width, the hysteresis tolerance and the 1e-3 amplitude floor, the A5 branch interpolation (PCHIP), and the peak-to-peak readouts.
6. The 2 percent check compares A5 with the mean-field S4 on v, the quantity A5 is defined on (owner ruling, DL-129); network amplitudes are information only.

## Carried forward (still open)

- K5 definition and tolerance: UNVERIFIED (DL-064, DL-082); cited, not re-run.
- K10 definition: kept as worded and not reproduced; the single-source claim is UNVERIFIED.
- `/permissions` check (DL-051): not recorded as done.
- Defender exclusion for the repository, `.venv` and the Julia depot: unknown.
- UNVERIFIED readings and grids: G2 readings (DL-132), A6 grids (DL-131, DL-132 (b)), S4 and ref_ceni sweep design, K7 window and tolerances, S3/S4 readouts.
- DL-062 and DL-073 (SE and step-onset estimator bias): fix at MS7.
- D36 24 h cap: lower bound 8.60 h and conservative 10.23 h only (DL-122), still not a full judgement until every row has a timing cell; S4 and A5/A6 rows were run but are not timing cells.
- sigma 0.0624 stays UNVERIFIED; S8 at MS10 is the independent check.
- K4-net: M2 network coupling unsourced.
- Possible private remote backup: no remote exists; owner decision.
- Map 1 Delta spacing (linear, UNVERIFIED): MS8 plan.

**MS6 gate: passed with departures.** Reason: the two gate items are met: A5 against S4 amplitudes agree within 2 percent (max 1.84e-3 at ref_devalle, points next to eta_H excluded, 1.49e-4 at ref_ceni) and the frequency map is done; D40 is confirmed by the owner, and G2 does not trigger (stay on M3), both on stated, partly UNVERIFIED readings. The pass is qualified: the K7 amplitude half fails its pre-registered residual rule (2.42 against 2 percent) and is reported as a failure, with the post hoc fit labelled as such; K10 is not reproduced as worded (non-blocking); the 36.1 Hz note in DL-115 is corrected to 32.01 Hz at eta_H (36.07 Hz at eta_bar 4); G2 (b) is evaluated for one path only. No tag, no push.
