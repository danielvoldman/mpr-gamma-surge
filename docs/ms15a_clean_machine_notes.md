# MS15a clean-machine notes: checklist 10.8 read-only (sub-step 21, part C; DL-747 F3)

Written for: the user (owner), who decides how checklist 10.8 is run and what the README may claim. Read-only: nothing was cloned, installed, built, tagged, pushed or run for this part. Plan passages are quoted word for word with plan line numbers (markdown escapes as in the file; copied by script from docs/plan.md and checked equal; the plan is not edited). Everything that is not a quote is a fact read from the repository (path given) or marked UNVERIFIED. Claude Code has no internet.

## 1. The plan passages relied on (word for word)

### Releases, tags and the push line (section 10.7)

> L1236: **Tags.** All annotated:
>
> L1238: - env-v1;
>
> L1240: - tolerances-frozen (end of MS1, with the replication.yaml SHA-256);
>
> L1242: - replication-pass (G0);
>
> L1244: - criteria-frozen (MS7, with the criteria SHA-256);
>
> L1246: - fig-\<ID\>-v\<k\>, for each figure build (inputs and hashes in the message);
>
> L1248: - release-v1.0.
>
> L1258:     git tag -a fig-F3-v1 -m "F3 from A4 <hash12>, A6 <hash12>"; git push origin main --tags
>
### Full suite before every tag; archive of results (Table 10.1 note, section 10.6, disk, repository tree)

> L1224: *Table 10.1. Unit tests. Run pytest -m "not slow" before every commit and the full suite before every tag. Every test states its tolerance; synthetic noise is seeded; comparisons are within one process or with tolerances, never bitwise against stored arrays (CPUs differ).*
>
> L1228: results/ and figures/ are git-ignored, so outputs are never edited by hand. Everything the paper uses is archived with the release (D37). docs/decision_log.md follows Appendix C. Entries are never deleted; a change gets a new entry that links back to the old one.
>
> L949: **Disk.** Map cells keep metrics plus v and r at 1 kHz in float32, about 1 MB per cell. Full series are kept only for examples, the subgrid and network runs. Estimated total: under 20 GB. Series are written with np.savez_compressed, and MS15 decides which result families are archived (D37).
>
> L1096:     # outputs (never edited by hand; archived with the release, D37)
>
### D37

> L1780: | DL-037 / D37 | Code licence and archive | MIT licence; release archived with a persistent identifier; service chosen at MS15 | Institutional requirement |
>
> L1017: Sources: R5 (Sandve and Nordlie rules; corpus practice on code, seeds and versions) \[R5, SQ6, recommendations\]; R7 (code and parameter sets; integrator and tolerances reported; archive with a version identifier) \[R7, §2.5–2.6, §6 rec. 6\]; R6 (no code mandate at MNA, but software and data must be credited) \[R6, §2.1, §8(d)\]. Names come from handoff (d) and (e); A0, A11, S16 and the figure scripts are Part 2 additions.
>
### Checklist 10.8 (section 10.8)

> L1262: ## 10.8 Reproducibility checklist
>
> L1264: 1.  Clone release-v1.0 on a clean Windows machine and install from the lock files.
>
> L1268: 1.  Run pytest; all tests pass, including slow ones.
>
> L1272: 1.  Run scripts\make_all.ps1 -Stage replication; every G0 row passes.
>
> L1276: 1.  Rebuild one figure from the archive; metrics match within the RB6 tolerances, not bit for bit \[R7, §2.6\].
>
> L1280: 1.  Re-run one sweep cell with --from-record \<json\>; its metrics match within tolerance.
>
> L1284: 1.  Every provenance file names the release commit and none is marked DRAFT.
>
> L1288: 1.  Nordlie tables, seeds, versions, OS and CPU are present for every figure and run \[R5, recommendations\].
>
> L1292: 1.  Code and results are archived with a version identifier \[R7, §8(d)\], and reused software is credited \[R6, §2.1\].
>
### The G0 row (Table 11.2) and the MS15 row (Table 11.1)

> L1372: | G0 Replication (MS2, MS5) | K1–K5 and K7–K9 pass (K4-net non-blocking until the M2 network coupling is sourced; K8 without its frequency band; K9 as in Table 7.1: if its maximum differs from 0.1453, only the ratio scaling across η̄ = 1, 2, 4 blocks) | Still failing after two debugging rounds → stop new work. Check the equations against the Ceni and Devalle forms \[R1, §2.1\], the sign convention (C3) and the units |
>
> L1366: | MS15 | Reproducibility release (D37); manuscript and submission checklist (below Table 11.2) | Checklist 10.8 passes on a clean machine; submission checklist complete | End |
>


## 2. The eight items of checklist 10.8

Reading order 1 to 8 (in the plan file every item is numbered "1."). "Stand-in" means the user's ruling of 2026-11-10 (DL-738 D1): a fresh clone and a fresh environment on THIS PC, labelled as a stand-in. "Time" is read from documented records only (file cited); nothing was timed; every sum is an UNVERIFIED estimate.

| # | Item, word for word (plan line) | What it needs | Exists | Missing | Time (documented records; UNVERIFIED sums) | Internet | Only the user can | Can the stand-in satisfy it? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | "Clone release-v1.0 on a clean Windows machine and install from the lock files." (L1264) | a clone of the tag release-v1.0 (now on the remote, https://github.com/danielvoldman/mpr-gamma-surge, private as the user states, UNVERIFIED); Python 3.11, Git, Julia 1.10.11 installed; `py -3.11 -m venv .venv`; `pip install -r environment\requirements-lock.txt`; `pip install -e . --no-deps` (README.md, plan L1132 to L1138) | the tag on the remote (the user's ls-remote output, docs/ms15a_push_record.md); environment/requirements.in, requirements-lock.txt (23 pins), python-version.txt, julia-version.txt, julia/Project.toml, Manifest.toml, setup_julia.jl; README setup block | whether the lock equals a fresh freeze was never checked (UNVERIFIED, docs/ms15_scope_notes.md section 2); a run of the commands has never been made on another environment | no documented time for a clone or a pip install (UNVERIFIED: none stated anywhere); the clone holds 5417 objects, 6.60 MiB pushed (docs/ms15a_push_record.md) | YES: GitHub (private: needs the user's credentials), PyPI wheels (numba, llvmlite, scipy, pandas, pyarrow, matplotlib), python.org if Python is missing; Julia packages for A5 only | the clone of a private repository with the user's credentials; the pip install (Claude Code has no internet); a second PC or a new Windows account | PARTLY. It tests that the tracked files, the lock and the README commands are enough, on one PC. It cannot test a clean machine: Python 3.11, Git, Julia, the pip cache, the stored Git credentials and the environment variables of this account are already there. |
| 2 | "Run pytest; all tests pass, including slow ones." (L1268) | the full suite without `-m "not slow"` in the clone; fast 1604 passed + 24 slow | fast suite 1604 passed, 24 deselected, 9 xfailed, exit 0, 1268.14 s (DL-746; 1405.18 s in DL-726); the 24 slow tests (marker slow, pyproject.toml line 19) run once at T in this step: 24 passed, 1613 deselected, exit 0, 588.86 s (DL-748; output outside the repository) | in a fresh clone `results/` and `figures/` do not exist (git-ignored): 59 of 124 test files mention `results/` and 41 mention `figures/` (text match); which of them fail, skip or pass without those folders was NOT run (UNVERIFIED). tests/test_replication.py::test_a0_table_has_one_passing_row_per_target_and_the_frozen_hash reads the table written by scripts/run_A0.py (its docstring), so it needs item 3 first. 9 xfailed are expected failures, not passes | fast about 21 to 23 minutes (DL-746 1268.14 s; DL-726 1405.18 s); slow: 9 min 49 s (588.86 s, DL-748) | no (after the install) | decide if "all tests pass" means the clone with or without results/ and figures/; any Julia-dependent test needs the Julia packages (which tests, UNVERIFIED) | PARTLY. In the working repository (with results/ and figures/) the answer is the one above. In a bare fresh clone the literal item cannot be shown without the git-ignored data; running it there would show which tests need them (a finding), not a pass. Copying results/ (32.6 GB) or figures/ into the clone makes it no longer clean. |
| 3 | "Run scripts\make_all.ps1 -Stage replication; every G0 row passes." (L1272) | scripts\make_all.ps1 (92 lines; header: written in sub-step 18, NEVER RUN, parse check blocked by the safety classifier, steps marked plan or inferred); it runs check_clean_tree, clears *.nbi and *.nbc, then S1, A1, A2, A4, S3 mean-field cells, A0; G0 row = plan Table 11.2 line 1372 "K1–K5 and K7–K9 pass (K4-net non-blocking ...)" | the script; the run scripts; stored records of every step from 2026-10-16 (results/S1, A1, A2, A4, S3, A0 manifests); the tag replication-pass (lightweight) | the script has never been run: it may fail at the first step (UNVERIFIED); the network cells of S3, the Julia steps and the recording of the cleared cache in provenance are NOT in it; -Stage all stops with an error; whether the stage equals "every G0 row" is UNVERIFIED (header); A4 records `K10 fail` (non-blocking, DL-115; K10 is not a G0 row in the plan's line 1372) | from the stored manifests of 2026-10-16: S1 1.1 to 1.8 s per run (4 records), A1 5.4 to 6.8 s (3), A2 0.6 to 0.8 s (3), A4 75.8 s (1), S3 mean-field 4.4 to 5.3 s per cell (5 cells), A0 0.55 s; sum about 2 minutes of compute (UNVERIFIED; plus the first-call compile, results/timing/cold_compile.txt: 0.78 s, plus startup) | no | decide whether the written stage is the one the plan means | YES in form: a fresh clone on this PC can run the stage and compare each K row; it shows the script works and the K rows pass on THIS CPU and OS. It does not show portability to another machine. The stage overwrites results/ inside the clone only (the clone has none), not this repository's results/. |
| 4 | "Rebuild one figure from the archive; metrics match within the RB6 tolerances, not bit for bit \[R7, §2.6\]." (L1276) | an ARCHIVE of the results one figure reads, and a script to build it (scripts/fig_journal.py reads results/ only); a comparison of metrics with the RB6 tolerances | the build script; in the rebuild of MS15a 19 (DL-742) PNG, TIFF and PDF of the 13 figures were byte-identical to v1 on this PC; FS5 rebuilt from another commit gave equal bytes except two lines of the supplement (DL-714); the hash list | an ARCHIVE of results: by ruling the Zenodo data record holds the figure files, source data and hash list, NOT results/ (32.6 GB); so no archive of the inputs exists for a rebuild; no script compares "metrics within the RB6 tolerances" (UNVERIFIED: none found by name; not searched further here) | the recorded build of the 13 figures: 59.4 s (DL-742); sum of the 13 provenance wall times 85.4 s (docs/ms15_scope_notes.md section 2) | no | provide an archive of the results a figure needs, if the plan's wording is to be met | NO as written. The stand-in could rebuild a figure from this PC's `results/` copied into the clone; that is a rebuild from a copy, not from an archive, and it compares bytes, not metrics against the RB6 tolerances. |
| 5 | "Re-run one sweep cell with --from-record \<json\>; its metrics match within tolerance." (L1280) | an option `--from-record <json>` of `python -m mprsurge.run`, one stored record, a tolerance | stored run records (results/<ID>/*.json) | the option itself: `python -m mprsurge.run` takes --config, --set, --workers, --longest-first, --dry-run; a search of src/ and scripts/ for from-record finds only a test whose name contains from_records (docs/ms15_scope_notes.md section 2; re-searched here: no hit in src/ or scripts/ other than one comment line in ms11_eval.py); writing it is a change under src/ (decision, tests, full fast suite) | - (not written) | no | rule that it is written (close item 71), or rule a departure | NO. It does not exist; a stand-in run cannot satisfy a missing option. |
| 6 | "Every provenance file names the release commit and none is marked DRAFT." (L1284) | the provenance records of the figures and runs | the 13 journal records: draft false, git.dirty false, git.commit R = 90b177acc694de0b9756542f236977d782f185e1, tags [] (checked in this step, all 13) | "every provenance file": the 11 draft records (draft true, audit copies by ruling), the run records (no `draft` key; some say dirty true, for example the A4 dry record), and the plan does not define "release commit" (read as R for the provenance and T for the tags: UNVERIFIED); the records are in git-ignored figures/ and results/, so a fresh clone does not hold them | seconds (a file check) | no | rule the reading of "every" and of "release commit" | PARTLY, and no stand-in is needed: it is a file check on this PC. Under the user-ruled reading (the 13 journal records; option B) it holds; read literally (all provenance files) it does not. |
| 7 | "Nordlie tables, seeds, versions, OS and CPU are present for every figure and run \[R5, recommendations\]." (L1288) | per figure and per run: a parameter table, seeds, package versions, OS and CPU | per figure `<ID>_params.csv` and `<ID>_nordlie.md` (drafts), supplement Nordlie tables and provenance with seeds, packages, os, cpu keys (journal); per run `results/<ID>/*_params.md` | a script that checks "every figure and run" does not exist; completeness for every run was not checked (UNVERIFIED, docs/ms15_scope_notes.md section 3 row 18); the OS and CPU in every record are THIS PC's | seconds to minutes for a scan (UNVERIFIED; not timed) | no | nothing; but the records show one machine only | PARTLY, no stand-in needed: a scan of the stored files on this PC (it needs a new check script, not written). The stand-in adds the OS and CPU of a second run on the same machine, which shows nothing new. |
| 8 | "Code and results are archived with a version identifier \[R7, §8(d)\], and reused software is credited \[R6, §2.1\]." (L1292) | a Zenodo record (software from the GitHub release, one data record) with a DOI or version identifier; credit of reused software | LICENSE (MIT), LICENSE-DATA.md (CC-BY 4.0 notice), CITATION.cff and .zenodo.json (no version, date or DOI on purpose), the tag release-v1.0 on the remote, the data package prepared in this step (outside the repository) | the deposit, the identifier, the GitHub release; "results are archived": by ruling the 32.6 GB of results/ are NOT archived (figure files, source data and hash list only); a statement crediting reused software (numpy, scipy, numba, matplotlib, pandas, pyarrow, pyyaml, pytest, Julia packages) is not in the repository as a statement (README lists the pinned versions; UNVERIFIED that this meets "credited") | - | YES (Zenodo, GitHub) | the Zenodo account, enabling the repository on Zenodo, making the repository public before a GitHub release, the GitHub release from release-v1.0, the deposit; all UNVERIFIED mechanics (not in the repository); Claude Code has no internet | NO. A clone cannot archive anything. |

## 3. What the stand-in can honestly satisfy, and what it cannot

- Can satisfy in substance (on this PC, with the stated limits): item 3 (run the stage in a fresh clone; the script has never been run, so the first run is itself the test), the mechanical part of item 1 (clone, venv, install from the lock; needs the user's internet and credentials), and, with this PC's `results/` copied in, the byte comparison of a figure rebuild (not the item as written).
- Partly: item 2 (the full suite passes here at T; in a bare clone it would show which tests depend on git-ignored folders), item 6 and item 7 (file checks that need no clone; item 7 needs a new check script).
- Cannot satisfy: item 4 as written (no archive of the results exists by ruling, and no metrics-within-RB6 comparison is named), item 5 (the option does not exist), item 8 (a deposit and an identifier).
- What no stand-in on this PC can show at all: that the project runs on a different Windows installation, CPU or account (it has the same Python, Git, Julia, pip cache, credentials, environment variables and CPU); the plan's own rule that results are compared "within tolerance, never bitwise against stored arrays (CPUs differ)" (L1224) is only testable on another CPU.
- Therefore the plan's done-when for MS15 ("Checklist 10.8 passes on a clean machine", L1366) and the user's MS15a done-when are NOT met by the stand-in. At most it can be reported as: items 1 and 3 run as a stand-in on the same PC; items 4, 5 and 8 not met; items 2, 6, 7 partly.

## 4. What the README must say about the stand-in (proposal; written only if the user agrees)

"Checklist 10.8 was not run on a clean machine. A stand-in was run on the development PC: a fresh clone of release-v1.0 and a fresh environment from the lock files (date, commands and outcome in docs/...). It shares the operating system, CPU, installed Python, Julia, Git, pip cache and credentials with the development environment, so it does not show that the project runs on another machine. Items 4 (rebuild from an archive of results; no such archive exists, by ruling), 5 (`--from-record`; not implemented) and 8 (archive with an identifier; not yet deposited) are not met; items 2, 6 and 7 are met only in part (see docs/ms15a_clean_machine_notes.md)."

No date, version or DOI is written in it. This section is a proposal only: the README is changed only to state what is true now (DL-747 F5), and the stand-in has not been run.

## 5. What only the user can do

- Run the clone and the pip install (Claude Code has no internet and no permission to push or clone from the private remote); give permission and time for the stand-in run (after it, step 22).
- A second PC or a clean Windows account (the only way to satisfy item 1 as written).
- Confirm on GitHub that the repository is private (UNVERIFIED by Claude Code).
- Rule: the reading of "every provenance file" and "release commit" (item 6); whether a `--from-record` option is written (item 5); what "archived" means for results (item 4, item 8); whether the README states the stand-in as in section 4.
- The Zenodo account, the Zenodo-GitHub link, making the repository public before a GitHub release, the GitHub release from release-v1.0, the deposit of the data package, then (later commit) adding the DOI to CITATION.cff and README (all mechanics UNVERIFIED: not in the repository).

## 6. UNVERIFIED in this file

Every time sum; that no time exists for a pip install or a clone; which fast tests need results/ or figures/; whether the stage `-Stage replication` as written equals "every G0 row"; that make_all.ps1 runs at all; whether a metrics-within-RB6 comparison script exists under another name; the reading of "release commit" and of "every provenance file"; whether credit of reused software is met; all Zenodo and GitHub mechanics; that the repository is private.
