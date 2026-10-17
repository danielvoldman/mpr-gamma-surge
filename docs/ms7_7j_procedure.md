# 7j procedure: freeze `criteria-frozen` (written in 7i, NOT executed)

Written for: the project owner, to approve before anything is run. Nothing below has been done: no tag, no freeze SHA-256 computed or stored, no file frozen. 7j runs only on the owner's explicit instruction ("run 7j"), after the questions Q1 to Q5 of `docs/ms7_gate_report.md` are answered. No push at any step; no remote is configured, `git push` is denied in Bash (a PowerShell deny rule is Q3). All commands use `.venv\Scripts\python.exe`, never plain `python` (3.12). Commit format `<type>(<scope>): <summary> [IDs]` with the attribution lines. Shell commands below are Git Bash unless marked.

Plan basis: Table 11.1 MS7 (gate: "test_surge_metrics passes; tag criteria-frozen"), section 7 intro (D35, DL-043: SHA-256 in the tag), `docs/ms7_plan.md` 7j row. Precedent: DL-084 (`tolerances-frozen`): hash of the **LF text as committed** (`git show <commit>:file | sha256sum`), tag on the commit that holds the file, hash recorded in a following docs-only commit. The plan's 7j row says the tag goes on "the commit that adds the approval DL entry". The order below follows that (the approval entry DL-161 is in the tagged commit A) and DL-084 (the hash is known only after the file is committed, so a following docs-only commit B records it in DL-162). Q1 asks you to confirm this reading.

## Step 0. Preconditions (stop if any fails)

1. The owner's instruction to run 7j, and answers to Q1 to Q5.
2. `git status` is clean; `git log --oneline -1` is the 7i commit; `git tag -l` shows only `env-v1`, `replication-pass`, `tolerances-frozen`.
3. `.venv\Scripts\python.exe --version` prints 3.11.x.
4. The edits of step 1 are the only edits: no change to the classifier, the D8 estimator, the 2-SE rule, any existing xfail, `configs/S13.yaml`, `configs/A4*.yaml`, `configs/S5_*.yaml`, or any value in `configs/robustness_criteria.yaml`. Only labels, sources, flags, wording and the added departure leaves change (list in step 1).

## Step 1. Pre-freeze content commit "A" (needs Q1 = yes)

Edits (all text, no number changes):

| File | Edit |
|---|---|
| `configs/robustness_criteria.yaml` | header: replace "DRAFT, NOT FROZEN" and the "nothing is frozen" lines with a statement that the file is frozen at tag `criteria-frozen`, that its SHA-256 (LF text) is in the tag message and in the DL entry that follows, and that a file cannot contain its own hash. `meta.draft: false`, `meta.frozen: true`, `meta.freeze_tag: criteria-frozen`, `meta.freeze_sha256: null` (kept null on purpose; comment says why), `meta.decision_log_through: DL-161` |
| same | `RB4.latin_hypercube_seed.source`: "confirmed by the owner at 7i (DL-159); follows the DL-141 convention ..." (status stays UNVERIFIED) |
| same | `RB4.perturbation_rel_box.source`: "Table 7.2 RB4, S16: +-10 percent" (drop the "[reasoned, not tested]" claim, gate report 7i-6) |
| same | `RB3.c_T_ramp_s`, `d_T_ramp_compared`: source adds "the 4-digit values are the S5 grid points 10^(k/4), configs/S5_cells.yaml; the plan gives 56, 100, 178, 316" (7i-7) |
| same | `classifier.d8_estimator.gate_wording`: "pytest exits 0 with the documented strict xfails" (the D8 test and the three zero-baseline tests, by node id). New leaves under `gate_departures` (status UNVERIFIED, sheet X-1, U-5, G6): D8 (2 of 8 A8 ring items), zero baseline (no "undefined" class), RB3(a) not judged at the headline; and the reported limitation "short-window false surges" |
| `tests/test_criteria_draft.py` | `test_draft_not_frozen` becomes a test that the flags are consistent with the freeze (draft false, frozen true, tag name, `freeze_sha256` null); the F-19 test text and `gate_wording` test follow; a new test that the file has no CR byte and no BOM (LF text); a test that each departure leaf exists. Fast suite counts change by the number of tests added (report them) |
| `docs/robustness_criteria.md` | regenerated from the YAML and the sheet (section 7 of the page then lists no difference) |
| `docs/ms7_signoff.md` | section 8 tag-message draft replaced by the text of step 5 below; row F-19 and TAG marked ruled |
| `docs/decision_log.md` | **DL-161**, approval entry: owner approval of the criteria file as it stands in this commit, the three departures, the UNVERIFIED values frozen with their labels (U-6), the Q1 to Q4 rulings, "SHA-256 in the tag message and in DL-162" |
| `docs/ms7_plan.md` | 7j row marked in progress |

Then: `.venv\Scripts\python.exe -m pytest -m "not slow"` green (expected: the 7i count, 469 passed, 4 xfailed, plus tests added in this step; plus any class-level tests Q2 adds, and their strict xfails). Commit: `docs(ms7): 7j pre-freeze content edits and approval entry, criteria file frozen in this commit [MS7, D35, DL-043, DL-161]`. Record the hash of this commit as A. `git status` clean.

## Step 2. Full suite on the clean tree at A

`.venv\Scripts\python.exe -m pytest` (no marker filter: the 469+ fast tests and the 7 slow ones: `test_cells::test_full_cell_list_is_900_plus_325_plus_headline` and the six `test_replication.py` K1 to K5, A0 tests). Run in the background (the fast part alone took 135 s; the slow part is not timed here, UNVERIFIED), `timeout` 600000 ms or `run_in_background`. Required: exit code 0, 0 failed, 0 errors, 0 XPASS; xfailed = 4 (plus any Q2 additions, each named); 0 deselected. If anything differs: **stop, no tag**, report. Keep the final summary line and the wall time for DL-162. Check `git status` is still clean afterwards (the suite must not write tracked files).

Optional, as in DL-084: a real `--dry-run` of `configs/base.yaml` with `output.dir results/dryrun_freeze` to show the record carries `git.commit` = A and `dirty = false`.

## Step 3. SHA-256 of the LF text

Primary (the one the MS8 loader checks, ruling H-3):

```
git show <A>:configs/robustness_criteria.yaml | sha256sum
git cat-file -p <A>:configs/robustness_criteria.yaml | wc -c        # byte count for the record
```

Cross-check with the working file after proving it is LF:

```
.venv\Scripts\python.exe -c "b=open('configs/robustness_criteria.yaml','rb').read(); assert b'\r' not in b and not b.startswith(b'\xef\xbb\xbf'); import hashlib; print(hashlib.sha256(b).hexdigest(), len(b))"
```

The two hashes must be equal; if not, stop (do not "fix" by converting: investigate). PowerShell `Get-FileHash` on the working file is acceptable only if the check above passed.

Further files, if Q5 of the gate report is yes (recommended): the same two-line check for `configs/S13.yaml`, `configs/A4_grids.yaml`, `configs/S5_cells.yaml` (their headers say they are frozen with the criteria tag), reported as secondary hashes in the tag message. The headline hash is the one for `robustness_criteria.yaml`. `docs/robustness_criteria.md` is a rendering, not hashed.

## Step 4. Create the annotated tag, locally

Write the message (step 5) to the session scratchpad as `tagmsg.txt`, with the real hash in place of `<hash>`, then:

```
git tag -a criteria-frozen <A> -F <scratchpad>/tagmsg.txt
git cat-file -p criteria-frozen            # object is A, type commit, message as written
git rev-parse criteria-frozen^{commit}     # equals A
git tag -l -n30 criteria-frozen
```

Never `git push`, never `--tags` to a remote. If the tag is wrong, deleting it (`git tag -d criteria-frozen`) is local and reversible, but only on the owner's say.

## Step 5. Tag message (draft; hash filled at step 3)

```
criteria-frozen: MS7 robustness criteria and classifier defaults (D35, DL-043).
SHA-256 of the LF text of configs/robustness_criteria.yaml (as committed in <A>): <hash>.
Secondary (if asked): configs/S13.yaml <hash>, configs/A4_grids.yaml <hash>, configs/S5_cells.yaml <hash>.
Gate: pytest exits 0 with the documented strict xfails: test_slowly_damped_ring_rate_matches_true_decay_after_step_onset
and the three zero-baseline tests of tests/test_surge_classes.py. Full suite: <counts, wall time>.
Gate departures:
 1. D8: the plan estimator fails 2 of the plan's 8 A8 ring items (15-cycle slowly damped ring called damped in
    86.5 percent against 95; D_ring_slow_-3 classed D-tr); 26 of 36 pre-registered F1 cells miss the 95 percent
    sign match (DL-137, DL-155). D8 = A, known limitation; every D8-dependent class is provisional.
 2. Zero baseline: the code has no "undefined" mode-N class (Table 2.1); constant record gives NS, exactly zero
    record gives S-sus with NaN peak_rho; three strict xfails (DL-158, DL-159).
 3. RB3(a) is not judged at the headline (outside the RB3(a) range at every floor >= 1e-16); coverage 0 to 2 of 13
    T_ramp per path and profile; G6 at the headline rests on RB3(b) and RB6 (DL-157, DL-149).
Reported limitation: short-window false surges on white noise, per W (DL-147, DL-155); claim limited through G6.
Values with no source are labelled UNVERIFIED in the file and are frozen with the label (sigma 0.0624, A_ref 2.176222,
D43 levels, solver floor, A4 step 0.025, Heun ladder, cell grids, seeds, F-19 key [7, 9]).
Carried: K5 deferred; K10 and K4-net; M4 criteria (F-23); O12 and the loader at MS8; Q3.
Owner approval: <date>, DL-161. Not pushed.
```

## Step 6. Hash entry and close (docs-only commit "B")

Add **DL-162**: tag `criteria-frozen` on A; the SHA-256 (and byte count) of the LF text; the full-suite counts and wall time; the cross-check; the departures; "no push"; "MS8 not started". Mark the 7j row of `docs/ms7_plan.md` done. Fast suite green. Commit: `docs(ms7): 7j criteria-frozen tag created on <A>, SHA-256 recorded [MS7, D35, DL-043, DL-162]`. Report: commits, DL numbers, test counts, the hash, the tag object. **Stop. MS8 is not started** (its plan needs the loader note: first step refuses to run if the SHA-256 of the criteria file does not match the tag).

## What can go wrong, and what to do

| Event | Action |
|---|---|
| Full suite fails or a strict xfail XPASSes | Stop, no tag, report; do not edit marks to make it pass |
| The two hashes disagree | Stop; the committed blob is the reference (DL-084); find the CR or BOM source |
| `git status` dirty before the tag | Stop; commit or discard only with the owner's say |
| An edit in step 1 would change a number | Stop; that is a change of a default (DL entry and ruling) |
| Any need to push | Not part of 7j; ask |
