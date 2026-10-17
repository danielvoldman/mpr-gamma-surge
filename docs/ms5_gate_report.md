# MS5 gate report (M3 replication and network: A4, S3, network code and timing, sigma, headline re-time)

Updated by step 5k (DL-124): dirty-tree check, clean-tree re-runs, K10 units review. Binding source: `docs/plan.md` (Table 11.1 row MS5; Gate G0; Table 7.1 K4, K7 to K11; 5.2 A4; 6.2 S3; 6.4; 9.2, 9.3, Table 9.1; D12, D18, D34, D36). Decisions: DL-112 to DL-122 (this review and gate: DL-123). Numbers are from the saved, git-ignored results (`results/A4`, `results/S3`, `results/sigma`, `results/timing/a4`, `results/timing/clean`) as in the DL entries; nothing was re-run for this report.

## Gate items

| Item | Value | Threshold | Verdict |
|---|---|---|---|
| K7 existence, mean field (A4 linear) | Hopf at tau_d = 4.1209 ms; Re lambda -0.054 at 3 ms, +0.084 at 8 ms | 4.12 +/- 0.05 ms (approved blocking value, DL-113) | Pass. Not independent: the 4.12 ms value came from the same Jacobian code (DL-074 to DL-079), so this shows consistency, not external agreement |
| K7 time series (S3 mean field) | 3 ms: v decays (final-second peak-to-peak 0.0 against 1e-6). 8 ms: sustained, window amplitudes within 8.3e-6 of their mean, v peak-to-peak 2.911 | decays at 3 ms; holds within 2 percent at 8 ms | Pass (existence only) |
| K7 against the paper's 4.95 ms | 4.1209 ms, difference -0.829 ms | 4.95 +/- 0.05 (Table 7.1 as written) | Outside. Documented departure, see below |
| K7 amplitude half | not judged | squared amplitude linear in tau_d - tau_d^(H), no hysteresis | Deferred to MS6 (A5, S4), owner's reading, DL-113 |
| K7 network | not judged | the plan gives no network criterion | Not judged (information only, DL-119) |
| K8 existence (A4) | unstable complex pair at 5 ms (Re +0.214 /tau, 36.1 Hz), stable at 50 ms (Re -0.069); Hopf crossings at 1.756 and 36.79 ms; no Hopf for J > 0 in 240 cases | oscillation at 5 ms, none at 50 ms | Pass |
| K8 time series (S3 mean field) | 5 ms limit cycle (hold deviation 9.2e-6, v peak-to-peak 5.512), 36.27 Hz; 50 ms fixed point | as above | Pass |
| K8 network peak, N = 5e4 | 36.24 Hz against 36.27 Hz, -0.09 percent | within 5 percent | Pass. "Peak" read as spectral peak frequency (ours, UNVERIFIED) |
| K8 band | 36.1 to 36.27 Hz; network 36.24 Hz | 25 to 100 Hz, non-blocking | Inside |
| K9 | largest Delta/eta_bar 0.145309 at eta_bar 1, 2, 4 (maximisers tau_d 10.06, 7.11, 5.03 ms; J -5.31, -7.52, -10.63); spread 1.7e-15 | ratio scaling within 0.002; maximum 0.1453 within 0.002 | Pass as in Table 7.1; no maximiser on a range edge. Also no Hopf for J > 0 (240 cases). The Table 7.1 clause "tau_d > 0" is not tested separately |
| K9 network | nothing run | the plan has no network part | n/a |
| K10 (non-blocking) | oscillatory interval 4.12 to 50 ms; 21.0 down to 10.7 Hz, monotone falling, inside 5 to 30 Hz +/- 10 percent; J dependence over J -40 to -5: 13.4 / 25.0 / 42.2 percent at 8 / 20 / 40 ms | J change under 10 percent | Frequency range and monotonicity pass; **J-dependence fails**. Non-blocking, rechecked from A6 at MS6. The J-change definition is ours (UNVERIFIED) |
| K11 (non-blocking) | 20 of 20 branches; largest deviation from 1 is 7.1e-4 | 0.01 | Pass |
| K4-net | not run | coupling unsourced (T51; 12.4) | Recorded as not run, non-blocking (DL-113) |
| sigma | 0.0624 committed in `configs/base.yaml` (fit 0.06239) | baseline std of v matches one N = 1e4 network baseline run | Committed by owner ruling (DL-121). The mean-field check (+0.07 percent) is nearly circular; it confirms linearity, not the value. See below |
| Headline re-time | A4 path, alone 99.30 s (101.4 s before); 10 copies 158.13 s per run (162.81 s) | launch rule, 9.2 | Done. No row changes verdict |

## Departures, stated plainly

1. **K7 at 4.12 ms, not 4.95 ms.** The blocking value is the approved 4.12 ms (UNVERIFIED, A4-derived), not the paper's 4.95 ms. A4 gives 4.1209 ms; the paper value is 0.829 ms away and was not reproduced. The sign convention and critical-Delta value (0.1453) were matched earlier (DL-075), but the 4.95 ms point and its parameters were not. At 4.95 ms the system is already oscillating in our model (20.5 Hz).
2. **K7 amplitude half deferred to MS6.** Table 7.1 lists K7 under A4, A5 and S3; the split is the owner's reading of the gate, not stated in the plan. So K7 is judged on existence only (damped at 3 ms, sustained at 8 ms).
3. **K10 J-dependence misses.** Non-blocking by the plan. Gate G0 also says a K10 or K11 failure "triggers a review of units and tau placement (section 3.3)". That review was done at 5k (DL-124, section "5k" below): no error in units or tau placement; the K10 value stays as recorded.
4. **Two timing exceptions from DL-105, unchanged.** Single-run delta_0.01 at 178.3 s alone against a 148.5 s limit, and the S5 baseline mode-N row at 120.6 s against 108 s. Neither cell was re-timed on the A4 path.

## Network results and the mean-field comparison

Network runs: N = 1e4 (five S3 cells) and N = 5e4 (K8), one seed, 10 s after a 2 s discard, 71.0 s wall for all six (DL-119). Comparison readouts are ours (UNVERIFIED): FFT peak frequency, r_N mean, fitted sinusoid peak-to-peak. Network minus mean field, over mean field:

| Cell | Frequency (Hz) net / MF | Mean r | Fitted peak-to-peak |
|---|---|---|---|
| ref_ceni 8 ms | 18.00 / 17.96 (+0.2 %) | +3.6 % | +6.8 % |
| ref_ceni 4.95 ms | 20.62 / 20.53 (+0.5 %) | +8.1 % | +18.3 % |
| ref_ceni 3 ms | no oscillation in MF | -0.04 % | network noise only, fitted peak-to-peak 0.0016 |
| ref_devalle 5 ms, N = 1e4 | 36.33 / 36.27 (+0.2 %) | +1.0 % | +2.4 % |
| ref_devalle 5 ms, N = 5e4 | 36.24 / 36.27 (-0.09 %) | +0.9 % | +1.5 % |
| ref_devalle 50 ms | fixed point | -0.13 % | network noise only |

Frequencies agree within 0.5 percent. The amplitude differences are information, not checks; the 4.95 ms amplitude differs by 18 percent at N = 1e4 (one seed, no N scan for that cell). Network start state is V uniform, s = 0, not the mean-field start.

## Timing and D36

Network kernel (DL-118): per-run rate 0.9e9 updates/s alone, 0.5e9 under 10 copies (slowdown 1.76 to 1.81, against about 4 for the Heun kernel). The ms5_plan loaded-factor assumption of 4 is replaced by 1.8. Speed-up at 10 workers 5.51 (efficiency 55 percent); 8 and 10 workers tie within 1.3 percent. The combined network row (S3, S8, S10, S12 NC1, K8, sigma) predicts 471 s against a 0.75 h limit; S9 predicts 0.22 h against 3 h. Both pass.

D36 24 h cap, after the A4 re-time (DL-122): **lower bound 8.60 h, conservative 10.23 h**, both under 24 h. This is **not yet a full judgement**: S1, S3 mean field, A1 to A6, S12 mean field, S13 ladders beyond the Radau pass set, the network dt ladder, spectrograms and analysis have no count or timing cell. The cap stays open until every row has a timing cell. Defender exclusion unknown; DCv2, warp-svc and Nord services were still running during the 5i re-time. The -2 to -3 percent shift against the earlier headline is within run-to-run and machine-state differences and is not attributed further.

## sigma

0.0624 v-units per sqrt(tau), the dv = f dt + sigma dW convention (DL-072, UNVERIFIED). Network std of v: seed 0 0.038824, 10-seed mean 0.038522 (sd 0.000322). Option (b), 0.06190, differs by 0.8 percent. The matching rule (sample std, linear in sigma) is ours. The mean-field check is nearly circular and weaker than the DL text suggests: the review found the check runs reuse the same ten seed indices as the trial runs, so it rescales identical noise realisations and cannot test seed noise; the "+0.07 percent" agreement is close to guaranteed. **sigma stays UNVERIFIED until S8 at MS10 (CP21).**

## Fresh-context review

A subagent that had not seen the work read `docs/ms5_plan.md`, DL-112 to DL-122, the K7 to K11 rows and the MS5 gate wording, and the saved results. **Numbers: no material mismatch** (A4, S3 mean field and network, 5f and 5i timing, D36 sums 8.602 / 10.234 h, sigma figures, the 4.12 ms and K9 maximiser claims all recomputed and matching). Findings, handled in this report (committed DL entries are not edited):

1. **DL-119 ratio, minor numeric mismatch.** DL-119 says the 3 ms network noise is "170 times" below the 8 ms cycle, and "174" for the proposed reading. Saved values: 0.27814 / 0.0015634 = 178 (167 against the mean-field fitted peak-to-peak 0.2605). Neither DL figure is right; 178 is the value. It is information only; no check uses it.
2. **K10 review owed.** DL-115 does not say whether the G0 "units and tau placement" review was done. It was not; now listed as carried forward.
3. **sigma check more circular than stated** (above).
4. **K7 "pass" is consistency, not independence** (table above).
5. **K9 line placement.** The "no Hopf for J > 0" result sits on the K8 line in DL-115; the value is correct and is shown under K9 here. "tau_d > 0" is not tested.
6. **Provenance.** A4, S3 and sigma records show `git.dirty = true` (A4 at commit f92a691); the 5f and 5i timing records are clean. Examined at 5k: see below. Result: tracked code did differ at run time, re-runs from a clean tree are bit-identical.

Not checked from saved results: test counts, DL-117 unit-test values, the five delta-cell eta_H values in DL-122 (from tests and code).

## 5k: dirty-tree check, clean re-runs, K10 review (DL-124)

**Dirty tree.** The records store only `git.dirty = true` and the parent commit, no diff hash or file list. Reconstructed from the history: every run was made before the commit that adds its code, so the recorded commit is the parent of the code that ran. A4 (record commit f92a691) ran code first committed in b0ff998 (`run_A4.py`, `hopf.py` additions, `config.py` and `run.py` edits, `A4_grids.yaml`). S3 mean field (b0ff998) ran code first committed in 6e62da0 (`s3` run kind in `config.py` and `run.py`, `simulate_mf.py`, `analysis/s3.py`, configs). S3 network (68f7ede) ran code first committed in 96d40b4 (`run_S3.py` and `analysis/s3.py` network parts, configs). Sigma (96d40b4) ran code first committed in 510fe8a (`calibrate_sigma.py`, `analysis/sigma.py`, configs). So **tracked files were modified, not only untracked or ignored ones**, in all four sets. The exact diffs at run time cannot be recovered.

**Re-runs from a clean committed tree (HEAD fffb63e, `git status` clean, record `dirty = false`).** Same configs and seeds, written to `results/rerun/` (git-ignored) next to the originals. A4 (1 cell), S3 mean field (5), S3 network (6), sigma network (10), sigma mean-field trial (20) and check at the fitted sigma (10): **52 `.npz` outputs, all arrays bit-identical** (shape, dtype, values) to the stored ones. The A4 verdicts equal. Sigma refitted from the re-run data: 0.06238876981899888, identical to the stored value; network std per seed and the check std per seed identical. Config differences between old and new records: `noise.sigma` null -> 0.0624 in base (DL-121; unused by the deterministic mean-field and network runs, and replaced by the axis value in the sigma runs), and the output directory. These change the config hash and so the record file names, not the results. The stored results are therefore confirmed; nothing was changed.

**K10 review (units and tau placement, section 3.3).** `analysis/hopf.py`, `models/mpr3d.py`, `configs/A4_grids.yaml`. (1) tau_d enters only as tau_d_tau = tau_d_ms / tau_ms (tau_ms = 10, `configs/A4.yaml`), and the Jacobian uses beta = 1/tau_d_tau; the grid and Hopf search run in tau units. (2) Frequency: Im lambda in 1/tau, f_Hz = Im lambda / (2 pi tau_ms 1e-3), which is the plan 3.3 mapping (f_Hz = 100 f_tau at tau = 10 ms). Cross-check at the Hopf point 4.1209 ms: sqrt(a2) = 1.32059 equals the eigenvalue Im part to 1e-16, 21.018 Hz. (3) The J-change is (max - min)/mean of the leading complex-pair frequency over J in {-40, -30, -20, -10, -5} at eta_bar = 1, Delta = 0.05 fixed, at tau_d 8, 20, 40 ms. **No unit or tau-placement error found.** Two observations on the definition (ours, UNVERIFIED), not errors and not applied: (a) the sweep includes points where the fixed point is a stable focus (J = -40 at all three tau_d, J = -30 at 8 ms), so the frequency there is a damped frequency; (b) eta_bar is held fixed while J moves, so r* varies 0.027 to 0.154, and the J = -5 point carries most of the spread. Restricting to unstable points (Re > 0) still gives 13.2 percent at 8 ms and 24 percent at 20 ms (read from the same calculation), above 10 percent, so the miss does not come from (a). K10 stays recorded as in DL-115 (J-dependence 13.4 / 25.0 / 42.2 percent), non-blocking, recheck at A6.

## Carried forward (still open)

- K10 J-dependence: units and tau-placement review done at 5k (no error); recheck from A6 at MS6, with the J-sweep definition in view (see 5k).
- K7 amplitude half at MS6; K7 4.12 ms value UNVERIFIED and A4-derived; 4.95 ms not reproduced.
- K5 definition and tolerance: UNVERIFIED (DL-064, DL-082); cited, not re-run.
- `/permissions` check (DL-051): not recorded as done.
- Defender exclusion for the repository and `.venv`: unknown.
- Jump definition (DL-108, DL-109) and S3 start states (DL-116): UNVERIFIED. S3 and K8 readout definitions (FFT peak, fitted peak-to-peak, "peak within 5 percent") are ours, UNVERIFIED.
- DL-062 and DL-073 (SE and step-onset bias): fix at MS7.
- D36 24 h cap: lower bound and conservative figure only, until all rows have timing cells.
- K4-net: M2 network coupling unsourced.
- sigma: S8 at MS10 is the independent check.
- Possible private remote backup: no remote exists; owner decision.
- Map 1 Delta spacing (linear, UNVERIFIED): MS8 plan.

**MS5 gate: passed with departures.** Reason: K7 (existence, at the approved 4.12 ms), K8 (including the network peak at -0.09 percent) and K9 (ratio scaling and maximum 0.1453) pass as Table 7.1 and the DL-113 rulings define them; K4-net is recorded as not run, non-blocking; sigma is committed; the headline is re-timed with no verdict change. The pass is qualified: K7 differs from the paper's 4.95 ms and its amplitude half is deferred to MS6; K10 J-dependence misses and its review is owed; the K7 pass is not independent; sigma is only weakly checked until MS10; the D36 cap is read from lower bounds. Conditions: definitions marked UNVERIFIED stand as working definitions; no tag, no push.
