# 7j procedure: pre-freeze (done at DL-161) and freeze `criteria-frozen` (NOT executed)

Written for: the project owner. **State after the 7j pre-freeze commits (DL-161):** the tests, the criteria file, the companion page and the departures list are in their final content. **Not done, and not to be done without the owner's separate explicit "freeze" instruction:** the tag, any freeze SHA-256 written into a file, the approval DL entry (DL-163), the hash entry (DL-164). No push at any step; no remote is configured, `git push` is denied in Bash (a PowerShell deny rule is Q3, the owner's settings change). All commands use `.venv\Scripts\python.exe`, never plain `python` (3.12). Commit format `<type>(<scope>): <summary> [IDs]` with the attribution lines. Shell commands are Git Bash unless marked.

Plan basis: Table 11.1 MS7 (gate: "test_surge_metrics passes; tag criteria-frozen"), section 7 intro (D35, DL-043: SHA-256 in the tag), `docs/ms7_plan.md` 7j row. Precedent: DL-084 (`tolerances-frozen`): hash of the **LF text as committed** (`git show <commit>:file | sha256sum`), tag on the commit that holds the file, hash recorded in a following docs-only commit. Ruled (Q1): this order, not the plan's wording "tag on the commit that adds the approval DL entry". The commit that holds the final file is called **A** below.

## Departures list for the gate (identical in the gate report, the sheet and the companion page)

Four departures from the plan at the MS7 gate, and one reported limitation. This list is identical in `docs/ms7_gate_report.md`, `docs/ms7_7j_procedure.md`, `docs/ms7_signoff.md` and this page.

1. **D8 (departure 1).** The plan estimator fails 2 of the plan's 8 A8 ring items: the 15-cycle slowly damped ring is called damped in 86.5 percent of 200 draws against the required 95 percent, and D_ring_slow_-3 (mode D, T_ramp 120 s) is classed D-tr where NS or D-none is required (DL-155, DL-157). D8 = A is kept; 26 of 36 pre-registered F1 cells miss the 95 percent sign match and 5 of 5 zero-growth cells exceed 5 percent false damped (DL-137, DL-155); every class that went through a D8 call is provisional. Strict xfails: `test_slowly_damped_ring_rate_matches_true_decay_after_step_onset` (DL-073), `test_a8_ring_class_is_ns_or_d_none[D_ring_slow_-3@T120]`, `test_a8_slowly_damped_ring_called_damped_in_95_percent_of_draws`.
2. **Zero baseline, including noise-free inputs (departure 2).** Table 2.1: with no gamma power "the power ratios and the mode-N classes are undefined". The code has no such class: a constant record gives NS, an exactly zero record gives S-sus with a NaN peak_rho and a RuntimeWarning, and a noise-free pure trend gives S-sus where the plan says NS (option (a), DL-159). Strict xfails: the 3 zero-baseline tests (DL-158) and `test_noise_free_pure_trend_is_ns_in_mode_n[120.0]` and `[3.0]`. This departure concerns noise-free inputs only. Deterministic runs use mode D (D-none).
3. **RB3(a) not judged at the headline (departure 3).** The headline (120 s) is outside the RB3(a) range at every floor >= 1e-16; coverage is 0 to 2 of 13 T_ramp per path and profile; P2 sigmoid has no predicted onset. G6 at the headline rests on RB3(b) and RB6 (DL-149, DL-151, DL-157). Reasoned arithmetic until MS8.
4. **Pure trend plus noise at W = 0.2 s (departure 4, new at the 7j pre-freeze, DL-161).** The plan's "pure trend -> NS" fails at class level at W = 0.2 s (T_ramp 3 s: S-rel in a majority of tested seeds (12 to 16 of 20 across six recorded 20-seed sets; DL-162 lists the sets)). T_ramp 120 s passes (NS). It is tied to the short-window false-surge limitation (306 of 500 white-noise records non-NS at W = 0.2 s). The classifier is not changed; the paper limits its claim to the windows where the classifier passes. Strict xfail: `test_pure_trend_plus_noise_is_ns_in_mode_n_at_t_ramp_3`.

Reported limitation (not a departure): **short-window false surges**, reported per W in every result. On seeded white noise (sd 0.04, mode N) non-NS of 500: 306 (W = 0.2 s), 400 (0.333 s), 172 (0.593 s), 24 to 26 (1.054 s), 2 (1.874 s), 0 (2 s). The rate is set by the power tests on a short PSD and the 10-cycle rule, not by D8. 8 of the 13 map-2 T_ramp have W < 2 s. The real rate on M3 noise is first measured by NC1 (G7).

Strict xfails in the suite: 9 cases (1 in `tests/test_surge_metrics.py`, 8 in `tests/test_surge_classes.py`), all with `raises=AssertionError`.

## Step 0 (done): pre-freeze content, DL-161

Ruled edits, all text or test marks, no number changed: the class-level strict-xfail tests with `raises=AssertionError` (9 cases, gate report section 5); departure 4; `configs/robustness_criteria.yaml` flags (`draft: false`, `frozen: true`, `freeze_tag: criteria-frozen`, `freeze_sha256: null` on purpose), `decision_log_through: DL-161`, F-19 reads ruled, `gate_wording` names every strict xfail, `classifier.gate_departures`, RB4 relabelled, RB3(c) sources note the S5 grid points (values kept exact); `docs/robustness_criteria.md`, `docs/ms7_gate_report.md`, `docs/ms7_signoff.md` and this file updated. Commits: tests first, then content, the full suite run from a clean tree. The commit that holds the final file is **A**; if the owner asks for a further content change, A moves and the hash is taken on the new A.

## Step 1. Preconditions at "freeze" (stop if any fails)

1. The owner's explicit "freeze" instruction.
2. `git status` is clean; `git log --oneline -1` is A or a docs-only commit after A that does not touch the four hashed files (check with `git diff A HEAD --stat -- configs/`); `git tag -l` shows only `env-v1`, `replication-pass`, `tolerances-frozen`.
3. `.venv\Scripts\python.exe --version` prints 3.11.x.

## Step 2. Full suite on the clean tree at A

`.venv\Scripts\python.exe -m pytest` (no marker filter: fast tests and the 7 slow ones). Run in the background (`run_in_background`; `timeout` up to 600000 ms). Required: exit code 0, 0 failed, 0 errors, 0 XPASS, 0 deselected; xfailed = 9. If anything differs: **stop, no tag**, report. Keep the final summary line and the wall time for DL-164. `git status` must still be clean afterwards.

## Step 3. SHA-256 of the LF text

Primary (the one the MS8 loader checks, ruling H-3):

```
git show <A>:configs/robustness_criteria.yaml | sha256sum
git cat-file -p <A>:configs/robustness_criteria.yaml | wc -c
```

Cross-check with the working file after proving it is LF:

```
.venv\Scripts\python.exe -c "b=open('configs/robustness_criteria.yaml','rb').read(); assert b'\r' not in b and not b.startswith(b'\xef\xbb\xbf'); import hashlib; print(hashlib.sha256(b).hexdigest(), len(b))"
```

The two must be equal; if not, stop (do not "fix" by converting: investigate). Secondary hashes (ruled, Q5), same two-line check for `configs/S13.yaml`, `configs/A4_grids.yaml`, `configs/S5_cells.yaml`, reported in the tag message after the headline hash. `docs/robustness_criteria.md` is a rendering, not hashed.

## Step 4. Create the annotated tag, locally

Write the message (step 5) to the session scratchpad as `tagmsg.txt`, with the real values in place of the `<...>` fields, then:

```
git tag -a criteria-frozen <A> -F <scratchpad>/tagmsg.txt
git cat-file -p criteria-frozen
git rev-parse criteria-frozen^{commit}     # equals A
git tag -l -n30 criteria-frozen
```

Never `git push`, never `--tags` to a remote. Deleting a wrong tag (`git tag -d criteria-frozen`) is local and reversible, but only on the owner's say.

## Step 5. Tag message (draft; values filled at step 3)

```
criteria-frozen: MS7 robustness criteria and classifier defaults (D35, DL-043).
SHA-256 of the LF text of configs/robustness_criteria.yaml (as committed in <A>): <hash>.
Secondary: configs/S13.yaml <hash>, configs/A4_grids.yaml <hash>, configs/S5_cells.yaml <hash>.
Gate: pytest exits 0 with the documented strict xfails (9 cases, each raises=AssertionError):
test_slowly_damped_ring_rate_matches_true_decay_after_step_onset (metrics); in tests/test_surge_classes.py the three
zero-baseline tests, test_a8_ring_class_is_ns_or_d_none[D_ring_slow_-3@T120],
test_a8_slowly_damped_ring_called_damped_in_95_percent_of_draws, test_noise_free_pure_trend_is_ns_in_mode_n[120.0] and [3.0],
test_pure_trend_plus_noise_is_ns_in_mode_n_at_t_ramp_3. Full suite: <counts, wall time>.
Gate departures:
 1. D8: the plan estimator fails 2 of the plan's 8 A8 ring items (15-cycle slowly damped ring called damped in
    86.5 percent of 200 draws against 95; D_ring_slow_-3@T120 classed D-tr); 26 of 36 pre-registered F1 cells miss the
    95 percent sign match (DL-137, DL-155). D8 = A, known limitation; every D8-dependent class is provisional.
 2. Zero baseline, including noise-free inputs: no "undefined" mode-N class (Table 2.1); constant record NS, exactly zero
    record S-sus with NaN peak_rho, noise-free pure trend S-sus (DL-158, DL-159, DL-161).
 3. RB3(a) is not judged at the headline (outside the RB3(a) range at every floor >= 1e-16); coverage 0 to 2 of 13 T_ramp
    per path and profile; G6 at the headline rests on RB3(b) and RB6 (DL-157, DL-149).
 4. Pure trend plus noise at W = 0.2 s: the plan's "pure trend -> NS" fails at class level (T_ramp 3 s: S-rel in a majority of tested seeds (12 to 16 of 20 across six recorded 20-seed sets; DL-162 lists the sets); T_ramp 120 s passes); tied to the short-window false-surge limitation (DL-161).
Reported limitation: short-window false surges on white noise, per W (DL-147, DL-155); the claim is limited to the windows
where the classifier passes.
Values with no source are labelled UNVERIFIED in the file and are frozen with the label (sigma 0.0624, A_ref 2.176222,
D43 levels, solver floor, A4 step 0.025, Heun ladder, cell grids, seeds, F-19 key [7, 9]).
Carried: K5 deferred; K10 and K4-net; M4 criteria (F-23); O12 and the loader at MS8; Q3.
Owner approval: <date>, DL-163. Hash entry: DL-164. Not pushed.
```

## Step 6. Approval entry and hash entry

**DL-163** (approval): the owner's approval of the criteria file as it stands in A, the four departures, the UNVERIFIED values frozen with their labels (U-6), the Q1 to Q5 rulings. **DL-164** (hash entry, in a following docs-only commit B): tag `criteria-frozen` on A; the SHA-256 and byte count of the LF text; the secondary hashes; the full-suite counts and wall time; the cross-check; "no push"; "MS8 not started". Mark the 7j row of `docs/ms7_plan.md` done. Fast suite green. Commit: `docs(ms7): 7j criteria-frozen tag created on <A>, SHA-256 recorded [MS7, D35, DL-043, DL-163, DL-164]`. Report: commits, DL numbers, test counts, the hash, the tag object. **Stop. MS8 is not started** (its first step refuses to run if the SHA-256 of the criteria file does not match the tag).

## What can go wrong, and what to do

| Event | Action |
|---|---|
| Full suite fails or a strict xfail XPASSes | Stop, no tag, report; do not edit marks to make it pass |
| The two hashes disagree | Stop; the committed blob is the reference (DL-084); find the CR or BOM source |
| `git status` dirty before the tag | Stop; commit or discard only with the owner's say |
| An edit would change a number | Stop; that is a change of a default (DL entry and ruling) |
| Any need to push | Not part of 7j; ask |
