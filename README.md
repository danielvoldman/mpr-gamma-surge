# mpr-gamma-surge

Code, configurations, tests, figure scripts and documents for a computational study of the dying-brain gamma surge with an exact mean-field (MPR) neural mass model and a spiking-network check. The plan that governs the project is `docs/plan.md` ("Technical Plan: MPR neural mass model of the dying-brain gamma surge", version 0.5). Everything below is read from files of this repository; a statement that no file supports is marked UNVERIFIED or left out.

**Status of this release (MS15a, part 2a).** The repository is being prepared for a reproducibility release. No release tag (`release-v1.0`) and no `fig-<ID>-v2` tag exists yet, nothing is archived, no version number and no DOI are assigned (shown as "not yet assigned"), and the repository has no remote yet. The 13 journal figures were rebuilt once from the clean commit 90b177acc694de0b9756542f236977d782f185e1 (`scripts\fig_journal.py --release`, `docs/decision_log.md` DL-741 and DL-742): every journal provenance record says `draft = false`, `git.dirty = false` and names that commit (checklist item 6 of the plan, section 10.8; what "release commit" means is UNVERIFIED, see `docs/ms15_draft_flag_notes.md`). The eleven drafts in `figures/F1` to `figures/FS5` are audit copies and stay `draft = true`. The PNG, TIFF and PDF files of the rebuild are byte-identical to those of the first build (v1).

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

Prerequisites: Python 3.11 from python.org (with the py launcher), Git for Windows, and Julia (for A5 only). The interpreter used here is recorded in `environment/python-version.txt` ("Python 3.11.9") and the Julia version in `environment/julia-version.txt` ("julia version 1.10.11"). Keep the repository near the drive root and outside OneDrive. `<repository-url>` is a placeholder: the repository has no remote yet (the URL is not yet assigned).

```powershell
git clone <repository-url> mpr-gamma-surge; cd mpr-gamma-surge
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # once, if activation is blocked
.\.venv\Scripts\Activate.ps1
python -m pip install -r environment\requirements-lock.txt
python -m pip install -e . --no-deps
julia --project=environment\julia environment\julia\setup_julia.jl   # A5 only
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

- The 13 provenance records of the recorded build hold a figure build time of 2.3 to 13.9 s each, 85.4 s in all (figure build only).
- Regenerating `results/` (the simulations) is not timed: no documented time exists (UNVERIFIED). `results/` is 32.6 GB in 32,070 files, is git-ignored and is not in the repository; the figure rebuild needs it on the machine.
- `figures/` is git-ignored too: the figure files are **not** in any tagged tree. Their SHA-256 hashes are in `docs/ms13_journal_final_hashes.txt` (the files of the rebuild) and in the messages of the tags `fig-<ID>-v1` (the first build; the supplement hashes in those messages are superseded); `docs/figure_map.md` lists them per figure.
- A rebuild from another commit does not give identical supplement files. In the rebuild of MS15a 19 (DL-742, all 13 figures, one clean commit) the PNG, TIFF, PDF, captions, alt texts and source data were byte-equal to the first build, and the supplements and provenance records differed (build commit, draft flag, provenance-file hash; the supplement text says `draft = false, release build`). The EPS extras of F3, F5, F5c and FS1 differ between any two builds (not in the hash list).
- Checks that read files only: `.\.venv\Scripts\python.exe scripts\ms13_check_hashes.py` and `.\.venv\Scripts\python.exe scripts\ms13_make_tags.py --verify --target e6666cb2e8120a1619527c5ee7fce01e1beedb55` (since MS15a 19 its column "hash list in tag tree equal" reads NO for the 13 v1 tags and the exit code is 1, because the hash list was rewritten for the rebuild; the columns annotated, target equal, message equal and files on disk read yes).
- `scripts\make_all.ps1 -Stage replication` and `-Stage figures` are written but have not been run; their header says which steps are the plan's and which are inferred.

## Tags (all local, annotated unless noted; nothing pushed)

`env-v1`, `tolerances-frozen`, `criteria-frozen`, `replication-pass` (a lightweight tag, a departure from the plan's "all annotated"), and the 13 figure tags `fig-F1-v1`, `fig-F2-v1`, `fig-F3-v1`, `fig-F4a-v1`, `fig-F4b-v1`, `fig-F5-v1`, `fig-F5c-v1`, `fig-F6-v1`, `fig-FS1-v1`, `fig-FS2-v1`, `fig-FS3-v1`, `fig-FS4-v1`, `fig-FS5-v1` (all at commit e6666cb2e8120a1619527c5ee7fce01e1beedb55). The tagger of these 17 tags and of the earlier commits is the placeholder identity "Your Name <you@example.com>" (a git configuration placeholder at the time; not changed). No `release-v1.0` tag exists. The tags `fig-<ID>-v2` (for the files of the MS15a 19 rebuild) and `release-v1.0` are planned and not created; the v1 tags stay as they are.

## Tests

`.\.venv\Scripts\python.exe -m pytest -m "not slow"` is run before every commit. The last recorded full fast suites: 1582 passed, 24 deselected, 9 xfailed, exit 0 (`docs/decision_log.md`, DL-737); MS15a 19 adds 11 test items and its own suite line is the last line of the decision log. The 24 deselected tests are the slow ones; the plan's checklist item 2 wants them to pass too, and that run is not recorded for the current commit (UNVERIFIED).

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
