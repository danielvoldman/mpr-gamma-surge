# mpr-gamma-surge

Code, configurations, tests, figure scripts and documents for a computational study of the dying-brain gamma surge with an exact mean-field (MPR) neural mass model and a spiking-network check. The plan that governs the project is `docs/plan.md` ("Technical Plan: MPR neural mass model of the dying-brain gamma surge", version 0.5). Everything below is read from files of this repository; a statement that no file supports is marked UNVERIFIED or left out.

**Status of this release (MS15a, through sub-step 22).** The repository is being prepared for a reproducibility release. The tags `fig-<ID>-v2` (13 figures) and `release-v1.0` are created at commit T, the final commit of MS15a sub-step 20 (the commit that holds this text; `git rev-parse release-v1.0^{commit}` names it); T is read as the "release commit" of the tags and R (below) as the "release commit" of the provenance: UNVERIFIED reading of the plan's wording. Nothing is archived, no version number beyond the tag name and no DOI are assigned (shown as "not yet assigned"). The remote is https://github.com/danielvoldman/mpr-gamma-surge. The user pushed `master` and the 18 tags named below; their `git ls-remote` output is saved in `docs/ms15a_push_record.md` and `scripts/ms15a_check_push_record.py` finds it equal to the local tag objects (no network). The user states that the repository is private; Claude Code did not verify it (UNVERIFIED). Commits made after the push are local until the user pushes them; as reported by the user in the chat (their output `## master...origin/master` after a later push), `master` was in sync with `origin/master` at that time (Claude Code ran no network command). **What the tags mean:** the figure provenance names R; release-v1.0 differs from R only in documents, the figure map, the hash list and helper scripts for tagging and hash lists (R = 90b177acc694de0b9756542f236977d782f185e1, the commit that adds DL-741). The 13 journal figures were rebuilt once from the clean commit 90b177acc694de0b9756542f236977d782f185e1 (`scripts\fig_journal.py --release`, `docs/decision_log.md` DL-741 and DL-742): every journal provenance record says `draft = false`, `git.dirty = false` and names that commit (checklist item 6 of the plan, section 10.8; what "release commit" means is UNVERIFIED, see `docs/ms15_draft_flag_notes.md`). The eleven drafts in `figures/F1` to `figures/FS5` are audit copies and stay `draft = true`. The PNG, TIFF and PDF files of the rebuild are byte-identical to those of the first build (v1).

## What this repository claims, and what it does not

**Claim limits (stated as in the figure captions and `docs/claim_limit_labels.md`).**

- The surge result is stated for the mean field only (label G4-C2: "this reading is UNVERIFIED"); there is no claim of robustness to finite-size fluctuations, and no claim of class or peak-frequency agreement between the network and the mean field.
- Muscle artifact cannot be ruled out as a source of the gamma-band signal: the study is a model, and nothing here tests that reading against recordings (`docs/ms13_evidence_sheet.md`).
- No causal, clinical or consciousness claim is made (the plan's manuscript checklist, line 1394, asks for this).
- Several defaults and wordings are marked UNVERIFIED in the captions and in `docs/ms13_close_items.md`; none was sourced by a later step.

**Failures that the science produced are shown as failures** (in the figures, the captions and `docs/ms13_close.md` section 2; numbers as in the captions):

- RB1 FAIL (network against mean field): headline path at 10 s 0 of 3 seeds and at 120 s 0 of 3 seeds (3 of 3 needed); the 4 map cells at 30 s 1 of 4 (3 of 4 needed).
- RB2 FAIL: headline class kept in 7 of 10 noisy seeds (8 of 10 needed).
- RB3(a) FAIL: onset prediction on the testable in-range runs, 0 of 6.
- RB3(b) FAIL: delay under a noise floor, classifier-onset reading (the stored table has no value or threshold).
- RB6 solver FAIL: the two solvers disagree on the headline onset by 181 ms (1 ms allowed).
- RB6 network peak-frequency FAIL (value blank in the stored table; threshold < 0.02).
- RB9(b) FAIL: spectral peak 49.0 Hz against cycle frequency 44.609 Hz, a difference of 4.391 Hz against 0.5 Hz.
- G7 NOT PASSED (the negative-control gate): the network run of the first negative control is in the surge class S+.
- D24 noisy subgrid FAILED: 97 of 225 cells agree (43.1 percent); 203 of 225 (90 percent) needed.
- The sigma check FAIL (logged verdict NOT INSIDE): mean-field baseline std 0.039522 against the network range 0.037989 to 0.038920.

## Windows setup (PowerShell)

Prerequisites: Python 3.11 from python.org (with the py launcher), Git for Windows, and Julia (for A5 and A6). The interpreter used here is recorded in `environment/python-version.txt` ("Python 3.11.9") and the Julia version in `environment/julia-version.txt` ("julia version 1.10.11"). Keep the repository near the drive root and outside OneDrive. `<repository-url>` is https://github.com/danielvoldman/mpr-gamma-surge (the user states that it is private; not verified here).

```powershell
git clone <repository-url> mpr-gamma-surge; cd mpr-gamma-surge
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # once, if activation is blocked
.\.venv\Scripts\Activate.ps1
python -m pip install -r environment\requirements-lock.txt
python -m pip install -e . --no-deps
julia --project=environment\julia environment\julia\setup_julia.jl   # A5 and A6
python -m pytest -m "not slow"
python scripts\time_one_run.py --config configs\S5.yaml --cell headline --repeat 3
python -m mprsurge.run --config configs\S3.yaml --workers 6
python scripts\fig_FS2.py
# after a deliberate upgrade; writes UTF-8, not UTF-16:
python -m pip freeze --exclude-editable |
    Out-File -Encoding utf8 environment\requirements-lock.txt
```

On a clean machine: in PowerShell `<` is reserved, so replace the placeholder with the real address; a repository downloaded as a ZIP carries Mark-of-the-Web, so run `Get-ChildItem -Recurse | Unblock-File` before activation; add `-Force` to `Set-ExecutionPolicy` when it is scripted; calling `.venv\Scripts\python.exe` directly avoids activation. Julia is set up from a script file to avoid PowerShell quoting problems. In this repository plain `python` may not be the environment (on the author's machine it resolves to Python 3.12): use `.venv\Scripts\python.exe`.

## Environment

- Python 3.11 only (`requires-python = ">=3.11,<3.12"` in `pyproject.toml`); CPU only.
- Eight direct dependencies pinned with `==` in `environment/requirements.in` and `pyproject.toml`: numpy 2.4.6, scipy 1.17.1, numba 0.68.0, matplotlib 3.11.2, pyyaml 6.0.3, pandas 3.0.6, pyarrow 26.0.0, pytest 9.1.1. The full pip freeze is `environment/requirements-lock.txt`. Whether the lock file equals a fresh freeze of the current environment was not re-checked in this step (UNVERIFIED).
- Julia 1.10.11 with `environment/julia/Project.toml` and `Manifest.toml` (committed), used for the continuation steps (A5, A6) only.

## Numerical settings (defaults of `configs/base.yaml`)

These are the path-neutral defaults; an individual run's own config can override them, and every run record and per-run parameter table (`results/<ID>/*_params.md`, not in git) holds the values actually used.

- Mean-field integrator: DOP853, `rtol` 1.0e-10, `atol` 1.0e-12, `max_step_tau` 0.05, output step 1 ms (`dt_out_ms` 1.0).
- Noisy mean field: Heun scheme, `dt_tau` 1.0e-3, `sigma` 0.0624 (checked and not confirmed; see the sigma check above).
- Network: N = 10000 default, `dt_tau` 1.0e-3, `V_peak` 100.0, `V_reset` -100.0, Lorentzian heterogeneity by quantile sampling.
- Ramp: default hypoxia-like path with `T_ramp_s` 120.0, `t_on_s` 5.0, linear profile, J from `J0` -21.0 to `J_end` 0.0.
- Durations: baseline 5.0 s, hold 10.0 s, discard 2.0 s. Seeds: root seed 20261008, 10 seeds per cell.
- Gamma-power analysis: primary band 25 to 100 Hz, window rule D4 with 2.0 s windows, Hann taper, relative and absolute factors 2.0 (`analysis:` block of `configs/base.yaml`).
- Tolerances: the frozen replication tolerances are in `configs/replication.yaml` (tag `tolerances-frozen`) and the robustness criteria in `configs/robustness_criteria.yaml` (tag `criteria-frozen`, SHA-256 c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05).
- Not restated here (UNVERIFIED that a short statement is correct without the code): the initial conditions and the full gamma-power computation. They are in `src/mprsurge/` (for example `analysis/surge_metrics.py`) and the plan; the plan's section 10.2 asks for them to be stated in this README, which is an open item (`docs/ms13_close_items.md`).

## Rebuilding the figures

The 13 journal figures (F1, F2, F3, F4a, F4b, F5, F5c, F6, FS1 to FS5) are built from stored results by `scripts\fig_journal.py`; they never simulate:

```powershell
.\.venv\Scripts\python.exe scripts\fig_journal.py F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5
```

- The 13 provenance records of the recorded build (field `wall_time_s` of `figures/journal/<ID>/<ID>_journal_provenance.json`; the files are git-ignored) hold a figure build time of 1.9 to 9.8 s each, 61.5 s in all (figure build only); `docs/decision_log.md` DL-742 gives 59.4 s as the wall time of the one script run.
- Regenerating `results/` (the simulations) is not timed: no documented time exists (UNVERIFIED). `results/` is 32.6 GB in 32,070 files, is git-ignored and is not in the repository; the figure rebuild needs it on the machine.
- `figures/` is git-ignored too: the figure files are **not** in any tagged tree. Their SHA-256 hashes are in `docs/ms13_journal_final_hashes.txt` (the files of the rebuild) and in the messages of the tags `fig-<ID>-v1` (the first build; the supplement hashes in those messages are superseded); `docs/figure_map.md` lists them per figure.
- A rebuild from another commit does not give identical supplement files. In the rebuild of MS15a 19 (DL-742, all 13 figures, one clean commit) the PNG, TIFF, PDF, captions, alt texts and source data were byte-equal to the first build, and the supplements and provenance records differed (build commit, draft flag, provenance-file hash; the supplement text says `draft = false, release build`). The EPS extras of F3, F5, F5c and FS1 differ between any two builds (not in the hash list).
- Checks that read files only: `.\.venv\Scripts\python.exe scripts\ms13_check_hashes.py` and `.\.venv\Scripts\python.exe scripts\ms13_make_tags.py --verify --version v2 --release` (checks the 13 v2 tags and release-v1.0 at the commit they point to) and `.\.venv\Scripts\python.exe scripts\ms13_make_tags.py --verify --target e6666cb2e8120a1619527c5ee7fce01e1beedb55` (since MS15a 19 its column "hash list in tag tree equal" reads NO for the 13 v1 tags and the exit code is 1, because the hash list was rewritten for the rebuild; the columns annotated, target equal, message equal and files on disk read yes).
- `scripts\make_all.ps1 -Stage replication` and `-Stage figures` are written but have not been run; their header says which steps are the plan's and which are inferred. The figures stage passes `--release` to `scripts\fig_journal.py` (a release build: run it on a clean tree).

## Tags

Created before sub-step 20 (all annotated except `replication-pass`, a lightweight tag and a departure from the plan's "all annotated"): `env-v1`, `tolerances-frozen`, `criteria-frozen`, `replication-pass`, and the 13 first-build figure tags `fig-<ID>-v1` (all at commit e6666cb2e8120a1619527c5ee7fce01e1beedb55). The tagger of these tags and of the earlier commits (689 of the 717 commits on `master` before sub-step 20) is the placeholder identity "Your Name <you@example.com>" (a git configuration placeholder at the time; history is not rewritten). **The `fig-<ID>-v1` tags are superseded by `fig-<ID>-v2`, stay local and are not pushed.**

Created at commit T = 33b7575721184b90571c2bbaffc4a9a0b1607a77 (MS15a sub-step 20; annotated; `git tag -l` lists them): the 13 figure tags `fig-F1-v2`, `fig-F2-v2`, `fig-F3-v2`, `fig-F4a-v2`, `fig-F4b-v2`, `fig-F5-v2`, `fig-F5c-v2`, `fig-F6-v2`, `fig-FS1-v2`, `fig-FS2-v2`, `fig-FS3-v2`, `fig-FS4-v2`, `fig-FS5-v2` (the files of the rebuild from R, with the full SHA-256 of every file in the tag message and "provenance: draft false, built from R"), and `release-v1.0` (author, licences, the 13 v2 tag names, the SHA-256 of `docs/ms13_journal_final_hashes.txt`, R, T, the criteria tag and hash). The figure provenance names R; release-v1.0 differs from R only in documents, the figure map, the hash list and helper scripts for tagging and hash lists. The v2 tags and `release-v1.0` carry the configured identity "Daniel Voldman <daniel.voldman@proton.me>".

Published to the remote (only these 18 tags, by name, never `--tags`): the 13 `fig-<ID>-v2` tags, `release-v1.0`, `criteria-frozen`, `env-v1`, `replication-pass`, `tolerances-frozen`. The branch is `master` (the plan writes `main`; not renamed). Remote: https://github.com/danielvoldman/mpr-gamma-surge. These 18 tags and `master` are on the remote (the user's push output is in `docs/ms15a_push_record.md`); the 13 `fig-<ID>-v1` tags are local only and were not pushed.

## Tests

`.\.venv\Scripts\python.exe -m pytest -m "not slow"` is run before every commit. The last recorded full fast suite: 1628 passed, 24 deselected, 9 xfailed, 9 warnings, exit 0 (`docs/decision_log.md`, DL-754, on commit 4d9366c). The 24 deselected tests are the slow ones (`-m slow`); they were run once in MS15a 21 and all 24 passed (exit 0, 588.86 s; `docs/decision_log.md`, DL-748). The plan's checklist 10.8 has not been run on a clean machine; see `docs/ms15a_clean_machine_notes.md` for what a stand-in on the development PC can and cannot show.

## Layout

`src/mprsurge/` code; `tests/` tests; `configs/` YAML; `scripts/` drivers, figure scripts and checks; `docs/` notes, the decision log (`docs/decision_log.md`), the plan copy (`docs/plan.md`), `docs/figure_map.md`, `docs/search_log.md`; `environment/` pinned environment files. Drivers only integrate, analysis modules only analyse, figure scripts only plot. `results/` and `figures/` are git-ignored outputs and are never edited by hand.

## Licence

- Code: MIT (file `LICENSE`).
- Data, figures, captions and text: CC-BY 4.0 (file `LICENSE-DATA.md`). UNVERIFIED: the full legal text of CC-BY 4.0 is still to be added to that file from creativecommons.org, and whether Peer Community Journal requires or accepts CC-BY is not sourced in this repository.

## How to cite

See `CITATION.cff`. It names the author and the licence; no version, release date or DOI is assigned yet (these keys are left out on purpose until they exist). The archive service chosen for the release is Zenodo; no record has been created.

## Author, funding, conflicts of interest

- Author: Daniel Voldman, Independent Researcher, daniel.voldman@proton.me, ORCID https://orcid.org/0009-0005-3409-8944.
- Funding: No funding received.
- Conflict of interest: The author declares no conflicts of interest.
