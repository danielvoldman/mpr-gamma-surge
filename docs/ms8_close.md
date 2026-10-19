# MS8 close (8h)

Written for: the reviewer and owner who closed MS8, and the author of the paper's limitations section. MS8 is closed on paper: **G6 passed with departures** (DL-208). No simulation was run at 8h, no tag was made, nothing was pushed, and no frozen criterion or evaluation rule changed (tag `criteria-frozen`, criteria file SHA-256 c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05; secondary files S13 317db87e..., A4_grids cf6a60be..., S5_cells fe8590ce...). All numbers below are those of `docs/ms8_g6_evidence.md` (EV sheet, SHA-256 2da296675f12229d90ccf9b8c1fc47a8edfe84d25be8e3f0d9c201fcb82bac14) and the files it names, all in `results/A7/` (git-ignored). Pre-check at 8h: the criteria gate passes against the tag, the four frozen hashes match, the tree was clean and all ten result files carry the hashes recorded in DL-207.

## (a) The G6 ruling (plan Table 11.2)

None of the three listed "Stop or redirect" actions is triggered: class does not depend on the solver (method or rtol) or on the Heun step; the floored delay does not depend on the Heun step (at the 1 ms output grid); surge is not only outside 56 to 316 s (it occurs inside in both modes). RB3(a) is not judged at the headline (frozen departure 3) and misses on 6 of 6 testable in-range runs; the RB6 solver clause misses (181 ms, unexplained). Ruling: **G6 PASSED WITH DEPARTURES**, with three claim limits.

| ID | Claim limit | Evidence (file, SHA-256) |
|---|---|---|
| G6-D1 | No claim that onset follows the A4 entry-exit prediction. RB3(a) is not validated (0 of 6 testable in-range runs within one A4 step of 0.025; errors 4.4 to 33.1 steps; 3 further in-range runs have eta constant at t_pred and carry no verdict). Fast-ramp onsets are ramp-seeded: onset independent of delta0 over 1e-9 to 1e-6, effective seed far above delta0. The mechanism is qualitative; the burst is not separable from the effective seed in the stored data (13 of 13 runs) | `rb_eval_ms8.json` 96e9e51cad7ad3b7f32f8da9ac4d937f2bc7ec01b3d990c8374df139a4ba92d8 (RB3a); `rb_diag_exploratory.json` 8a388a556a93fc4a0330a2905c095e084b627e1b01e7487dbd00802c53ea2edf (Set A); `rb_diag_burst.json` a724b37eeddfd2eabf2391d05345f3578b28e949df65e0fa44fbaf4d9b960b39; `rb_diag_atol_seed.json` 9471e7e088183a69b7ee63739fb65f815e1928117b7d95e62f99960edd3d1dd4 |
| G6-D2 | The headline delay is taken from the D43-floored runs. The noise-free onset is reported as solver-dependent: DOP853 58.698 s, Radau 58.879 s (181 ms; delay 0.066192 against 0.071471 eta), unexplained; seed, burst, atol, ulp and rtol checks are negative (onset 58.698 s at atol 1e-10, 1e-12, 1e-14 and at +/-1 ulp of the start state; rtol 1e-8, 1e-10, 1e-12 identical) | `rb_eval_ms8.json` (RB6_solvers); `rb_diag_ms8.json` 3fb10f131efe6a40d19459629637aad74a5c2ab95bd9f9651c37835b4af197db; `rb_diag_exploratory.json` (Set B); `rb_diag_atol_seed.json` |
| G6-D3 | RB3(b) is reported under both onset readings. Raw first crossing: MEETS (median floored delay -0.000760, -0.042323, -0.105060 over the three floor levels). Classifier episode onset: -1.5, -1.5, -1.0917, ties at levels 0 and 1, DOES NOT MEET. The raw crossing is the primary reading by the 8f2 clarification | `rb_eval_ms8.json` (RB3b); `recompute_ms8_independent.json` 4d91aab379c98c88f649802b9f38e59e41b849c33c47a029139c6360983cfd50 (b) |

RB3(d) and RB5 are reported as they stand, per path and per T_ramp, no pooled verdict: P1 class changes with start distance at 9 of 13 T_ramp; the P2 headline path class is unchanged at start distance 0.5, 1.5 and 3 (D-tr at all three); RB3(d) linear against sigmoid at the four T_ramp: P1 2 changes, P2 0, P5 0.

## (b) Items reported without a verdict

- **RB3(c)** (not in the G6 row). Gating input is the headline path (P2 linear noise-free) at 56.23, 100, 177.8, 316.2 s against the headline class D-tr: D-tr at all four (reading C: holds). Reading A (every path against D-tr): holds for P2 and P5, linear and sigmoid; fails for P1 linear (D-sus, D-sus, D-sus, D-none) and P1 sigmoid (D-none, D-sus, D-none, D-none). Reading B (the four classes of one path and profile equal each other): same split as A. Source: `rb_eval_ms8.json` (RB3c).
- **RB3(d)**: above; **RB5**: delta0 1e-9, 1e-6, 1e-3 at the headline gives class D-tr at all three and delay shift 0.0 at 1e-9 and 1e-3 against 1e-6; start distance on P1: class unchanged at 4 of 13 T_ramp, changes at 9 of 13. Delay on the headline path falls with start distance (+0.1721, +0.0662, -0.0647 eta at 0.5, 1.5, 3). Source: `rb_eval_ms8.json` (RB5), `rb_diag_startdist.json` e16808ccad9949b6572ceb8c0fe9a9e3aa29a9eaa9893783f28ece25ee2fadd5.
- **RB6 rtol**: the noise-free DOP853 delay is 0.066192 at rtol 1e-8, 1e-10 and 1e-12 (difference 0.0); reported against rtol, not a pass test. The RB6 Heun check shows relative change 0.0 at all three floor levels (30 of 30 seed pairs with identical onsets), a limit of the 1 ms output grid, not extra evidence. Source: `rb_eval_ms8.json` (RB6_solvers, RB6_heun).
- **O12 post-surge rate** (reported only, not a criterion): `results/A7/a7_o12_post_surge.csv` and `.parquet` (DL-207), 157 P2-based runs, both the 1 s and the 5 s window as separate columns, no window chosen. Mode N is reported as given: no "main episode" rule; 70 of the 116 mode-N runs with a defined J_exit,run have it at J0 (flagged, not interpreted). The frozen file still carries `post_surge_rate: null` (UNVERIFIED); it is not edited.

## (c) Supplementary and exploratory items (none feeds a gate; none is in the S5 or S13 manifests)

| Step | Label | Result | Source |
|---|---|---|---|
| 8f3 Set A (DL-191, DL-192) | EXPLORATORY | P1 start distance 0.5 linear, T_ramp 1 s and 10 s, delta0 1e-9 and 1e-3: onset identical for 1e-9 and 1e-6; 7 ms and 60 ms later at 1e-3 | `rb_diag_exploratory.json` |
| 8f3 Set B (DL-191, DL-193) | EXPLORATORY | headline start state +/-1 ulp: onset 58.698 s in all three | `rb_diag_exploratory.json` |
| 8f4 (DL-194, DL-195) | SUPPLEMENTARY | headline at start distance 0.5 and 3: D-tr at both; raw onset 37.260 s and 75.448 s | `rb_diag_startdist.json` |
| 8f5 (DL-196 to DL-199) | EXPLORATORY | burst diagnosis from stored data (deterministic response at path breakpoints); clean-tree re-run of the 8f3 sets bit-identical | `rb_diag_burst.json` |
| 8f6 (DL-200 to DL-202) | EXPLORATORY | atol 1e-10 and 1e-14: 0 ms shift; effective seed against burst not separable in 13 of 13 | `rb_diag_atol_seed.json` |

None of these feeds a gate. The P5 1.778 s burst-seeded prediction (DL-202, extrapolated burst amplitude) stays UNVERIFIED and is not cited as evidence.

## (d) Clarifications of rules the frozen file does not state

The eight 8f2 clarifications (DL-186; EV sheet section D): (1) RB3(b) and RB6 delays use the raw first-crossing onset as primary, the classifier-onset reading stays labelled; (2) RB3(a) judges the testable in-range runs only (6 of 9), runs with eta constant at t_pred get time errors and no verdict; (3) P1 linear start distance 0.5 has 5 in-range T_ramp against the frozen "0 to 2 of 13"; (4) DOP853 against Radau applied literally, any amendment is a new departure; (5) RB3(c) gating input is the headline path at the four T_ramp, readings A and B beside it; (6) RB3(d) and RB5 per path and per T_ramp, no pooled verdict; (7) the RB6 Heun exact 0 is a limit of the 1 ms grid; (8) floor-run delays are signed (negative = onset advance).

8h rulings (DL-207, DL-209): **O12**: post-surge rate = mean r over a window after J_exit,run as the classifier gives it, 1 s and 5 s as separate columns, no window chosen, no mode-N "main episode" rule, runs with J_exit,run at J0 flagged. **J_exit,static**: J at the last positive-to-non-positive crossing of the leading Re lambda along the path, accepted as a working reading, **UNVERIFIED** (the plan gives no operational rule).

## (e) Known limitations for the paper

1. D8 estimator: the plan estimator fails 2 of 8 A8 ring items (gate departure 1); every D8-dependent class is provisional (359 of 360 stored runs carry the label).
2. Short-window false surges on white noise (306, 400, 172, 24 of 500 at W 0.2, 0.333, 0.593, 1.054 s); mode-N P2 classes at T_ramp 1 to 31.62 s include them (gate departure 4).
3. Breakpoint transients at every ramp breakpoint (EV sheet, `rb_diag_burst.json`).
4. RB6 Heun resolution is limited by the 1 ms output grid (bound resolves 1.3 output steps at level 0, 72.6 at level 1, 180 at level 2).
5. Mode N J_exit,run: the plan gives no main-episode rule; J_exit,run of the earliest episode lies at J0 in 70 of 116 runs.
6. The Heun ladder uses a 5e-5 tau coupling base step (DL-169, confirmed DL-173), derived from the F-14 ladder, not from a source; the 1e-3 rung of a floor run does not have the stream of a plain mode-N run.
7. S5 was launched by the pooled launcher `scripts/run_ms8_list.py` (DL-173), not by the runner's per-config CLI (equivalence check DL-176).
8. Also carried: sigma 0.0624 UNVERIFIED until S8 (MS10); A_ref reading (a) 2.176222; the 181 ms DOP853 / Radau onset difference unexplained.

## (f) Measured compute

Recorded walls (10 workers): S5 list 3,174.9 s = **52.9 min** for 232 runs (235 in all; DL-175; prediction 50.7 min, limit 85.5 min); S13 list 1,578.8 s = **26.3 min** for 125 runs (DL-178; prediction 20.6 min, limit 90 min). Together 79.2 min (1.32 h) against the 24 h D36 cap. No wall is recorded in the decision log for the 8f3 to 8f6 diagnostic runs or for the 8h file, so none is stated. A cumulative measured wall for MS0 to MS8 is **not formed**: the log records the D36 totals only as predictions (conservative 10.23 h at DL-122; about 10.0 h at DL-168), and not every run wall is recorded. Stating a measured cumulative figure would need a sum the log does not support.

## (g) Carry-forward to MS9

- Criteria frozen and unchanged (tag `criteria-frozen`, loader gate active).
- Radau measured at **0.0957 s per tau at 120 s** (DL-178, DL-179); use it, not the 10 s scaling, for Radau planning.
- The 9.2 timing gate is to be repeated before map runs, with the counts then ruled.
- Open housekeeping: K5 definition UNVERIFIED and deferred (DL-064, DL-082); K10 definition kept, single-source claim UNVERIFIED (DL-131 to DL-133); K4-net coupling unsourced (MC-03); the 24 h D36 cap accepted. F-16 (RB1 at N = 3e4 against 1e4) is a network check for MS10, not evaluated at MS8. MS9 work is not started.
