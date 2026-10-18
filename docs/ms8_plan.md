# MS8 sub-step plan (planning and the criteria loader; no ruling yet, questions open)

MS8 plan, written before any MS8 ramp run. Binding source: `docs/plan.md` (Table 11.1 row MS8; Table 11.2 G6; Table 6.2 S5 and S13; 5.2 A4 and A7; Table 7.2 RB3, RB5, RB6; Table 2.1; 6.2, 6.6; 9.2, 9.3, Table 9.1; D8, D12, D26, D35, D36, D40, D43, CP14, CP23, CP25). Decisions go in `docs/decision_log.md`; this plan is DL-168 (the loader is DL-165, the counts and seed keys DL-166, the timing measurement DL-167) and holds none of its own. It changes nothing in the plan and nothing in a frozen file. Rules as for MS4 to MS7: one sub-step at a time; after each, `.venv\Scripts\python.exe -m pytest -m "not slow"` green, one commit `<type>(<scope>): <summary> [IDs]`, a report, then stop. No tags, no pushes unless asked. Every run starts from a clean tree, writes a provenance record (6.6), and (ramp runs) starts only if the criteria loader verifies the freeze. Anything not in the plan or the decision log is marked UNVERIFIED. Where the plan leaves a choice open, this document lists the options and a recommendation; nothing is chosen.

**MS8 row (Table 11.1):** "Ramp study: S5 ramp runs (with the headline cell), A7 (S5 part); S13 headline subset". Done when: "RB3 and the headline RB5 and RB6 checks evaluated". Unlocks: "G6; MS9". Depends on MS7 (closed, tag `criteria-frozen` on dd8330c, DL-162 to DL-164, `docs/ms7_gate_report.md`). The plan names no tag for MS8.

## State at the start of MS8

| Item | State |
|---|---|
| Freeze | Annotated tag `criteria-frozen` on dd8330c (local only). SHA-256 of the LF text of `configs/robustness_criteria.yaml` c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05; secondary `configs/S13.yaml` 317db87e..., `configs/A4_grids.yaml` cf6a60be..., `configs/S5_cells.yaml` fe8590ce.... Any later change of a frozen criterion needs a decision-log entry and is reported in the paper (plan section 7) |
| Loader (8a, DL-165) | `src/mprsurge/criteria.py`: refuses on a missing tag, a hash mismatch (tag blob, working file, three secondary files) or a dirty hashed file; the runner gates every config that names the frozen file; `configs/S5_ramp.yaml` is the first (H-2). Verified against the real tag in 8a |
| Gate departures carried (DL-163) | (1) D8: the plan estimator fails 2 of 8 A8 ring items, every D8-dependent class is "provisional"; (2) zero baseline incl. noise-free inputs: no "undefined" class; (3) RB3(a) not judged at the headline (coverage 0 to 2 of 13 T_ramp per path and profile); (4) pure trend plus noise at W = 0.2 s fails "pure trend -> NS". Reported limitation: short-window false surges on white noise (306 of 500 at W = 0.2 s). Effect on MS8: the S5 grid has T_ramp 1 to 31.6 s (W = 0.2 to 1.05 s, the windows with false surges on white noise: 306, 400, 172, 24 of 500 at W 0.2, 0.333, 0.593, 1.054 s), where mode-N classes are expected to include false surges; and noise-free ramp runs of zero or constant baseline give S-sus or NS by the known difference |
| Existing pieces MS8 uses | Runner and spawn pool (`run.py`); kinds `mf` (DOP853, Radau) and `mf_noisy` (stochastic Heun, dt_tau key); paths P1 `path_eta`, P2 `path_hypoxia`, P5 `path_updown`, profiles linear and sigmoid (`ramps.py`); delta0 kick at t_on in both modes; `analysis/entry_exit.py` (t_pred and the RB3(a) range, 7g); `analysis/surge_metrics.py` (classes, onset, episode metrics); `configs/S13.yaml` (rtol, delta0, Heun ladder, floor levels); `analysis/timing.py` (9.2 arithmetic) |
| Not existing | Start-distance key (D12 fixes 1.5); a noisy-sweep seed prefix (the runner gives seed index s the key [s] = the calibration keys); floor-run configuration and the coupled-increment Heun ladder (F-14); A7 module and `results/A7/`; the O12 definition |

## What the plan fixes for MS8

| Part | Plan wording (Table 6.2 S5, S13; 5.2 A7) | Count default (see Decisions) |
|---|---|---|
| S5 deterministic ramps | P1, P2, P5 x 13 T_ramp (1 to 1000 s, 10^(k/4)) x {linear, sigmoid}; mode D, DOP853 rtol 1e-10, delta0 1e-6 at t_on; durations 5 s + last ramp end + 10 s (P1: T, P2: 1.25 T, P5: 2 T) | 78 runs, 2.058e6 tau |
| S5 start distance | P1 x start distance {0.5, 1.5, 3} (eta_start = eta_H - d); 1.5 is the P1 run above | 26 new runs, 4.957e5 tau |
| S5 noise seeds | P2 x 10 noise seeds (mode N, sigma 0.0624 UNVERIFIED until S8, stochastic Heun dt 1e-3 tau, 2 s discard) | 130 runs, 3.0755e9 Heun steps |
| S5 headline cell | P2, ref_devalle, T_ramp 120 s, linear, I = 0 (120 s is not on the grid) | 1 run, 16,500 tau |
| S13 headline subset | at T_ramp 120 s on P2: rtol ladder {1e-8, 1e-10, 1e-12}, Radau, delta0 ladder {1e-9, 1e-6, 1e-3}, D43 floor with its Heun dt ladder | rtol 2, delta0 2, Radau 1 (rtol 1e-10, DL-100 (3)), floor 120 (3 levels x 4 rungs x 10 seeds) |
| A7 (S5 part) | per run: eta_bar at onset, delay eta_on - eta_H, duration, peak power and frequency, class; P5: offset on the way down and hysteresis width; memory (start distance), profile, noise floor; all against epsilon with the quasi-static reference. Output `results/A7/a7_ramp_metrics.parquet`, feeds F4 | 8c, 8h |
| Gate | RB3 and the headline RB5 and RB6 evaluated, then G6 (Table 11.2): RB3(a) on the runs inside its range, RB3(b) and RB6 pass at the headline; RB3(d) and RB5 evaluated and reported; "surge only outside 56 to 316 s: limit the claim" | 8h, 8i |

## Decisions that need you before the sub-step that uses them

"Recommendation" is mine; nothing below is decided. "Test" is what could overturn it.

| ID | Item | Options | Recommendation | Needed by |
|---|---|---|---|---|
| M-1 | **S5 noise seeds: which T_ramp and profiles** ("P2 x 10 noise seeds") | (a) 13 T_ramp, linear, 10 seeds = 130 runs, 3.0755e9 Heun steps; (b) headline T_ramp 120 s only, 10 runs; (c) 13 T_ramp x 2 profiles = 260 runs | (a). Table 9.1 counts 3.1e9 Heun steps for S2, S5 and S6 together, and only reading (a) gives that figure (3.08e9, arithmetic ours, UNVERIFIED). Cost is small either way (47 s of the 10-worker wall for (a)) | 8b |
| M-2 | **Start-distance runs** ("P1 x start distance {0.5, 1.5, 3}") | T_ramp: (a) all 13, (b) headline 120 s only. Profile: (a) linear only, (b) both. Distance 1.5 re-run or reused | 13 T_ramp, linear, reuse the P1 linear run at 1.5 (26 new runs). Cut order 5 ("drop 562 and 1000 s from P5 and the start-distance runs") implies the start-distance runs span the T_ramp grid | 8b |
| M-3 | **Headline RB5: start-distance part** | RB5 lists delta0 (S13), start distance (S5, defined on P1) and up/down (P5, S4). The headline-point RB5 has the delta0 ladder; the plan gives no start-distance run on P2. (a) delta0 ladder only at the headline, the P1 start-distance runs reported map-wide; (b) add P2 headline x start distance {0.5, 3} (2 runs, 3.3e4 tau, about 3 min of 10-worker wall) | (b), since G6 reports RB5 at the headline and the cost is trivial. Needs your yes because it adds runs the plan does not name | 8b |
| M-4 | **D43 floor design** ("the floor with its Heun dt ladder at 120 s") and its delta0 | Design: (a) full, 3 levels x 4 rungs x 10 seeds = 120 runs (8.5e9 steps, 127 s of 10-worker wall); (b) two-part, RB3(b) 3 levels at dt 1e-3 x 10 seeds plus the RB6 ladder at the middle level, 60 runs. delta0 in floored runs: (i) the default 1e-6 for all levels; (ii) the level's nominal label (1e-9, 1e-6, 1e-3), as F-10 names the levels by delta0. Which level is "the headline floor" for RB6 | (a) and (i). The plan, F-10 and F-14 do not say whether delta0 follows the level; (i) keeps the floor level the only variable in RB3(b). Under (a) RB6 can be reported at every level | 8b |
| M-5 | **Radau** | DL-100 (3): rtol 1e-10 at 120 s is the pass test; rtol 1e-12 only at the 10 s ramp (Radau at 1e-12 on the headline timed out at 3,600 s, DL-097). 316 s and 10 s Radau belong to the full S13, not the headline subset (cut order 1) | One Radau run at rtol 1e-10, T_ramp 120 s. Predicted 19 min on one core under load, the longest single job of 8e. Confirm | 8e |
| M-6 | **Allowance for the S5 part** | Table 9.1 row "S2, S5, S6 (ramp sweeps)" 19 to 57 min is shared with S2 and S6. Judge S5 alone against (a) the full row (0.95 h, limit 1.43 h), or (b) a pro-rata share | (a), and state it; S2 (3 min) and S6 (about 5 min, 20 runs) are small. D36 is checked on the whole table in any case | 8d |
| M-7 | **Start-distance key** | D12 fixes eta_start = eta_H - 1.5. (a) new `path.start_distance`, null by default and left out of the hash view while null, so no stored hash moves (the `path` section is hashed: a plain default would change every hash); (b) explicit `path.eta_start` and `path.eta_peak` computed by the driver (status "provisional" by the present rule, which mislabels an A4 path) | (a) | 8b |
| M-8 | **Noisy sweep seeds** | The runner gives every mf_noisy cell seed index s the key [s] (the calibration keys). (a) runner takes `seeds.spawn_key` as a prefix and appends s (as `run_S5_baseline` does); (b) a dedicated MS8 driver builds the jobs | (a), with the proposed keys below | 8b |
| M-9 | **Seed keys** | [8, 1, s] S5 noise; [8, 2, l, s] floor and ladder (DL-166) | confirm both; UNVERIFIED until you do | 8b |
| M-10 | **Coupled Brownian increments** (F-14, ruled) | Implementation only: draw the dt 1e-4 increments and sum 10, 5 and 2 of them for the coarser rungs, or refine a coarse path by Brownian bridge. Either way the 1e-3 rung of a floor run no longer has the stream of a plain mode-N run | draw-and-sum from one key (exact, simple); cost 10x the random numbers at the default rung | 8b |
| M-11 | **Storage per run** | The writer stores 8 float64 arrays at 1 kHz (t_ms, r, v, s, eta, J, Delta, I). (a) keep (measured size below); (b) float32 for r, v, s only; (c) drop s and the three path columns (recomputable from the config) | (a) if the measured total is a few GB; the plan's under 20 GB is not threatened | 8b |
| M-12 | **Job order** | The runner runs cells in index order. With 10 workers the P5 1000 s runs (up to 49 min each under load, P5 sigmoid) should start first, or the makespan grows by the length of the last long run | longest first (a sort in the driver, no result change) | 8b |

### Status of M-1 to M-12 (updated in 8c; rulings as recorded in DL-169; the table above is the 8a text and is not edited)

- M-1: ruled (a), P2 noise at 13 T_ramp, linear, 10 seeds = 130 runs.
- M-2: ruled, start distance {0.5, 1.5, 3} on P1, 13 T_ramp, linear only, 1.5 reused = 26 new runs.
- M-3: NOT adopted (no extra headline start-distance runs); headline RB5 = delta0 ladder (S13) plus the P1 start-distance runs (S5).
- M-4: ruled, floor = 3 levels x 4 Heun rungs x 10 seeds at delta0 1e-6 = 120 runs.
- M-5: ruled, one Radau run, 120 s, rtol 1e-10.
- M-6: ruled, S5 judged against the whole shared Table 9.1 row (57 min, limit 85.5 min).
- M-7: ruled, null start distance stays out of the hash view; no stored hash moved (8b).
- M-8: ruled, seed-key prefix in the runner (seeds.spawn_prefix); done in 8b.
- M-9: confirmed, keys [8, 1, s] and [8, 2, l, s].
- M-10: ruled with one departure of wording, coupled increments drawn at 5e-5 tau (DL-169); CONFIRMED by the reviewer in 8c (DL-173); stays on the list of method details to report in the paper.
- M-11: ruled as recommended, 8 float64 arrays at 1 kHz kept.
- M-12: ruled as recommended, longest first; for a multi-config list this needs one pooled launch (scripts/run_ms8_list.py, DL-173).

Sub-step numbering note (updated in 8d): the table below is the actual order, as ruled by the reviewer in the 8d prompt: 8c = S5 run, 8d = S13 run, then the A7 code (8e) and the RB3 / RB5 / RB6 and G6 checks (8f). The 8a wording of rows 8c to 8j is replaced by this table; the Technical Plan is not edited.

## Sub-steps

One commit each; code is committed before it is run, so records show `dirty = false`. Before every run sub-step: the loader verifies the freeze, the launch rule of 9.2 is re-applied with the then-current sample, and a part projected over one hour stops for your ruling.

| Step | Files | Inputs | Outputs | Stop point |
|---|---|---|---|---|
| 8a (done) | this plan; `criteria.py`; `ms8_counts.py`; `configs/S5_ramp.yaml`; `configs/timing/ms8/`; DL-165 to DL-168 (commits 939fde2, 1b1bb41 and the docs commit) | `docs/ms7_plan.md`, DL-162 to DL-164 | loader verified against the real tag; counts, prediction, seed-key proposal | Report; your rulings M-1 to M-12 |
| 8b (code, no run) | `run.py` (key prefix, job order); `config.py`/`ramps.py` (start distance, hash-preserving); `simulate_mf.py` (floor runs, coupled increments); `configs/S5_ramp_*.yaml` (the sweep configs: 6 path x profile sweeps, start distance, noise seeds, S13 subset); `tests/` | your rulings M-1 to M-12 | dry-run plans whose run counts equal `ms8_counts`; tests: key prefix, hash unchanged for every stored config, start distance, coupled increments sum to the coarse increment, loader gate on every new config | Fast suite green; dry-run counts printed; no run |
| 8c (S5 run, done) | `scripts/run_ms8_list.py` (DL-173); `results/S5/ramp/` (git-ignored) | 8b, rulings M-1 to M-12 | the whole S5 list in one pool: 105 deterministic ramps (incl. start distance and headline) + 130 noise runs = 235 runs, 235 ok in 52.9 min at 10 workers (DL-174, DL-175); nothing classified | Done (commit d77d60c) |
| 8d (S13 run) | `scripts/run_ms8_list.py --list S13`; `results/S13/` (git-ignored) | 8c; measured re-time (DL-177) | the S13 headline subset, 125 runs (rtol 2, delta0 2, Radau 1, floor 120), one pool, 10 workers, longest first; records; no A7, RB or classification analysis | Report run counts, flags, wall, memory, disk; STOP |
| 8e (A7 code, no run) | `analysis/a7.py` (A7 S5 part: per-run metrics, P5 offset and hysteresis width, memory and profile tables, RB3 to RB6 evaluators reading `configs/robustness_criteria.yaml` from the tag blob); `tests/` | the frozen file, `surge_metrics`, `entry_exit`; synthetic ramp records and the S4 limit-cycle records | metric definitions logged (eta at onset from the classifier onset time, delay, duration, peak power and frequency, offset); evaluators with every threshold read from the frozen file; O12 left undefined | Fast suite green; no run |
| 8f (A7 S5 part, RB3 / RB5 / RB6 evaluation, G6 checks) | `scripts/run_A7.py`; `results/A7/a7_ramp_metrics.parquet`; O12 definition | 8c to 8e | RB3 (a to d), RB5 at the headline, RB6 at the headline evaluated against the frozen file; RB3(a) coverage; classes of the S5 and S13 runs; short-window false-surge counts per W against the limitation; O12 post-surge rate defined with data (reported only, not a criterion; its definition is a frozen-file addition, so a DL entry and a statement in the paper) | Report; your rulings |
| 8g (review and gate report) | `docs/ms8_gate_report.md` | 8a to 8f | fresh-context review as 2f to 7i: values trace to the frozen file, every departure restated, G6 reading | Verdict line; STOP for your approval |
| 8h (close) | DL entry | your approval | G6 statement; MS9 unlocked | No tag is named by the plan; none created |

Order (as run, updated in 8d; the 8a order of separate headline, S13, deterministic-grid and noise launches is superseded by the pooled S5 run of 8c): 8a, 8b, 8c (S5 run), 8d (S13 run), 8e (A7 code), 8f (RB evaluation), 8g, 8h. A run sub-step does not start until the previous one is reported. The first M3 ramp data (the S5 records) exist since 8c; they are not classified before 8f.

## Timing gate prediction (9.2; measured in 8a, DL-167; launch decision DL-168)

**Sample.** Ten cells (`configs/timing/ms8/`), each 10 concurrent copies x 1 batch, per-run medians, from a clean tree at commit 1b1bb41 (`git.dirty = false`), High performance plan, AC, `scripts/run_timing_ms8.sh`. Not the clean machine of 9.1: a browser (waterfox, 111 percent CPU at the start) and the VS Code webview were open, so the figures lean slow; Defender exclusion unknown. One batch per cell (spread within a batch 0.4 percent for P5 sigmoid), no repeats, so batch-to-batch spread is not measured. Nothing was saved or classified; the size probe integrated three short cells in memory once.

| Cell (10 copies) | tau | per-run median | s per tau |
|---|---|---|---|
| headline P2 linear 120 s (DL-122, earlier) | 16,500 | 158.1 s | 9.58e-3 |
| P5 linear 1000 s (DL-104, earlier, provisional path) | 201,500 | 2,329 s | 11.56e-3 |
| P1 linear / sigmoid, T_ramp 56.2 s | 7,123 | 65.4 / 74.4 s | 9.18e-3 / 10.45e-3 |
| P2 linear / sigmoid, T_ramp 56.2 s | 8,529 | 90.8 / 106.5 s | 10.64e-3 / 12.48e-3 |
| P5 linear / sigmoid, T_ramp 56.2 s | 12,747 | 162.9 / 186.9 s | 12.78e-3 / 14.67e-3 |
| P2 10 s, DOP853 rtol 1e-8 / 1e-10 / 1e-12 | 2,750 | 30.5 / 31.0 / 32.4 s | 11.10e-3 / 11.29e-3 / 11.79e-3 |
| D43 floor run, Heun dt 1e-4, 16,700 tau (1.67e8 steps) | 16,700 | 26.0 s | 1.555e-7 s per step (DL-104: 1.51e-7 at dt 1e-3) |

Readings: the sigmoid costs 14 to 17 percent more per tau than the linear profile; rtol 1e-12 costs 4 percent more than 1e-10 (max_step 0.05 tau, not rtol, sets the step); the Heun cost per step is the same at dt 1e-4 as at 1e-3. Rate rule (ours): each family takes the slower of its matching sample cell and the nearest earlier cell (headline for P1 and P2, p5_1000 for P5), so the shorter-ramp sample sets the rate for P5; the 1000 s P5 run is probably cheaper than predicted (UNVERIFIED).

**Counts and prediction** (10 workers, divisor 10, default readings M-1 (a), M-2 (a), M-4 (a); `python -m mprsurge.analysis.ms8_counts --workers 10`, output `results/timing/ms8/prediction_8a.txt`). Sum of run walls / 10, also bounded by the longest run; the longest-first schedule (M-12) gives the same figure.

| Row | Runs | Work | Sum of run walls | Wall at 10 workers | Allowance (Table 9.1) | Limit 1.5 x | Verdict |
|---|---|---|---|---|---|---|---|
| S5 (S2, S5, S6 row, whole row used, M-6) | 105 deterministic + 130 noise = 235 | 2.570e6 tau mean field, 3.0755e9 Heun steps | 8.45 h | **50.7 min** (longest run 49.2 min, P5 sigmoid 1000 s) | 57 min | 85.5 min | PASS (0.89 x) |
| S13 headline subset | 125 | 1.0e5 tau noise-free and Radau, 8.5e9 Heun steps | 50.8 min | **18.9 min** (longest run: Radau, from the 10 s cell's 0.0687 s per tau) | 60 min | 90 min | PASS (0.31 x) |

By part (wall): P1 linear 16.2 min (39 runs), P1 sigmoid 17.7, P2 linear 22.4, P2 sigmoid 26.3, P5 linear 42.9, P5 sigmoid 49.2, headline 2.6, noise seeds 43 s (130 runs); S13: rtol 2.8 + 2.8 min (single runs), delta0 2 x 2.6 min, Radau 18.9 min, floor ladder 127 s (120 runs). **No part is over one hour; no stop is triggered.**

Other readings (S5 row, same method): noise at the headline only 50.0 min; noise at 13 T_ramp x 2 profiles 51.4 min; start distance at the headline only 49.2 min; **start distance on both profiles 59.3 min** (0.7 min under the stop line); floor two-part: S13 18.9 min (sum 37 min). So M-2 (b) is the only reading that comes near the one-hour line.

**D36 (24 h, whole table).** The 5i figure (DL-122): lower bound 8.60 h, conservative 10.23 h, in which the S2/S5/S6 row stood at 1.14 h. Replacing that row by the S5 prediction above (0.85 h) and adding an S6 estimate (20 runs of P2 length, 3.2e5 tau at the P2 sample rate, about 0.09 h, ours) gives a conservative total of about 10.0 h; the S13 headline subset is inside the S13 row, which the 5i total already carries at its 1.0 h allowance. About 10.0 h against 24 h: within the cap. Rows without a timing cell (A7, A8 reclassification, spectrograms of 360 records) remain as in DL-122.

**Memory.** Polled total python working set during the ten 10-copy samples: 1.1 to 1.4 GB for the mean-field cells, 2.7 GB for the dt 1e-4 floor cell (about 270 MB per worker, the random-number chunk of 1000 steps per output sample). In-process peak above the pre-run working set, per kept sample: 284 B (P5 sigmoid), 388 B (P2 linear), 196 B (mode N), against 64 B of raw arrays. Taking 388 B per sample (the maximum), the longest run (P5 1000 s, 2,015,001 samples) peaks near 0.78 GB and the 10 largest runs together 5.5 GB, an upper bound that assumes they all run at once (which a longest-first order makes likely early on). Table 9.1 says under 1 GB for the sweep rows; the measured worst case exceeds that figure and stays inside the 12 GB working limit used since DL-142 and the 16 GB machine. Extrapolated from 127k-sample runs to 2e6 samples: UNVERIFIED.

**Disk.** 360 npz files, 8 float64 arrays at 1 kHz: 4.92 GB raw, measured compression 0.39 to 0.43, about 2.0 GB written (129 GB free; Table 9.1: the plan under 20 GB). M-11 asks whether to keep the layout.

**Launch rule (9.2 step 3) as applied now.** Both rows satisfy prediction <= 1.5 x allowance and the D36 total is inside 24 h, with the default readings. Nothing is launched in 8a. The rule is applied again before 8d, 8e, 8f and 8g with the counts that you then rule, and the one-hour check is repeated: it needs your ruling if any part crosses it. Cut order 9.3 is not triggered; the steps that would apply first are 1 (Radau only at the headline, already the case) and 4 (sigmoid for P2 only).


## Open items that touch MS8

1. **K5 (DL-064, DL-082).** Own reading, UNVERIFIED, passed at MS2, not re-run; re-running touches the frozen `replication.yaml`. No MS8 deliverable uses it. Carried.
2. **K10 (DL-131 to DL-133).** Not reproduced as worded (J dependence 13 to 42 percent at 8 / 20 / 40 ms); definition kept, single-source claim UNVERIFIED, non-blocking. No MS8 deliverable uses it. Carried.
3. **K4-net coupling (MC-03).** The M2 network coupling is unsourced; non-blocking until a source gives it; MS8 has no network run. Carried.
4. **O12 post-surge rate.** Reported-only metric, not a criterion, not implemented; defined at MS8 with data (DL-157). Planned at 8h, after the data exist; its definition and the report format are then yours to rule. The frozen file carries `post_surge_rate: null, UNVERIFIED`; filling it is a change of a frozen file and needs a DL entry and a paper statement.
5. **F-16 (RB1, no worse at N = 3e4 than at 1e4).** A network check (S8, S9), MS10. Entered as an interpretation, UNVERIFIED, no margin. Not evaluated at MS8.
6. **RB6 statistic (DL-154, DL-157).** Median delay over 10 seeds, default Heun step 1e-3 against the finest rung 1e-4, same seeds, coupled increments, relative change below 5 percent. UNVERIFIED. It is evaluated at 8e on the floor ladder; with M-4 (b) the level it uses must be named.
7. **Reported limitations that act on MS8 results:** every D8-dependent class is provisional; short-window false surges per W; sigma 0.0624 UNVERIFIED until S8 at MS10; the A_ref reading (a), 2.1762; the four gate departures.
8. **Defender exclusion.** User-reported only (closed by the user at 7h, `docs/ms7_signoff.md`); affects wall times and the file-writing share of the 360 files. Noted in each timing figure.
9. **Tags and pushes.** None. The tag `criteria-frozen` is local only; no remote exists.
