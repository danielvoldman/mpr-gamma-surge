# MS15 scope notes (sub-step 17, DL-734; results DL-735)

Written for: the user (owner), who decides the open MS15 items. It says what the Technical Plan v0.5 (docs/plan.md, read-only, binding) requires for MS15, what the repository already holds, and what is missing or blocked. It writes no README, no data statement, no code statement and no manuscript text, makes no release, archive, upload or tag, and uses no web source. Claude Code has no internet.

**Rules of this file.** Plan passages are quoted word for word with plan line numbers (markdown escapes as in the file; copied by script and checked against the plan lines). Line numbers are lines of docs/plan.md as it stands. Everything that is not a quote is either a fact read from the repository (path given) or marked UNVERIFIED. Venue: Peer Community Journal after a Peer Community In recommendation (DL-554 R1; user ruling of 2026-11-09, DL-716 X4, DL-720). The following are UNVERIFIED because neither the plan nor the repository sources them (searched, section 1.K): the PCJ template and policies, a versioned DOI repository, CC-BY for data or figures, "no AI-generated illustrations", the Zenodo limits of 100 files and 50 GB per record, the AI-use disclosure wording a venue wants, and "confirm the PCI section".

## 1. The plan's MS15 passages, word for word (B2)

### 1.A The MS15 row, its done-when, and the rows around it (Table 11.1)

> L1349: | **\#** | **Milestone and deliverables** | **Done when** | **Unlocks** |
>
> L1351: | MS0 | Repository, environment, README, CLAUDE.md, .claude/settings.json, docs/plan.md, decision log seeded from Appendix C; requirements.in with == pins; Julia version pinned | Environment installs and pytest collects; tag env-v1 | MS1 |
>
> L1365: | MS14 | Novelty re-check: Scholar (including cited-by checks on Xu 2023 and Borjigin 2013), PubMed, three slow-passage searches, Kalia journal version, eLife RP 104249, PMC12549018 \[R2, §6 rec. 6; RA, Recommendations\] | docs/search_log.md complete | G8; MS15 |
>
> L1366: | MS15 | Reproducibility release (D37); manuscript and submission checklist (below Table 11.2) | Checklist 10.8 passes on a clean machine; submission checklist complete | End |
>
> L1368: *Table 11.1. Milestones in build order (renamed MS0–MS15 in v0.4 so that milestone IDs do not collide with the model IDs M2–M4).*
>
> L187: 6.  Make the figures, run the novelty re-check (G8) and publish the reproducibility release.
>
**The MS15 row and its done-when** (Table 11.1): deliverables "Reproducibility release (D37); manuscript and submission checklist (below Table 11.2)"; done when "Checklist 10.8 passes on a clean machine; submission checklist complete"; unlocks "End". The plan gives MS15 no other test.

### 1.B What G8 shapes at MS15 (Table 11.2)

> L1380: | G8 Novelty | No close work found | An MPR hypoxia gamma model exists → reposition as a robustness, regime-map or E–I study and cite it as the precedent. A non-MPR model exists → keep the paper, stress what the exact mean field adds, add a comparison figure \[R2, §4\]. An MPR slow-ramp study exists → adopt its delay metrics \[R1, §4\]. v0.3 pre-check (RA): PARTIAL OVERLAP. MPR slow-passage studies exist (Taher et al. 2022 \[R1, §2.5; R5, SQ4; RA\]; Avitabile et al. 2022 \[single source: RA\]), and a non-MPR ischemia model exists without a surge (Kalia et al. 2023 \[R2; RA\]). v0.4: D41 decided (section 12.7): reframe as a first mechanistic model and cite Taher et al. 2022 and Avitabile et al. 2022 as method precedent; the third branch is met by A7's entry–exit delay metrics |
>
> L1382: *Table 11.2. Stop-or-continue gates. G0 and G5–G8 are new. Thresholds: G0, D34; G5–G8, D35. What each gate blocks: G0 blocks S5 onward; G1 sets the model for MS5 onward; G2 and G3 open MS12; G5–G7 limit or stop the claims that depend on them; G4 and G8 are report-only for the run order (G4 limits claims to the mean field; G8 shapes the manuscript at MS15).*
>
The G8 outcome is "to be written by the user" (docs/search_log.md section 4; DL-732 A3; close item 60). MS14 was closed by user ruling as a departure from the plan (native searches not done). Any novelty statement is limited to what the web-search pre-check supports.

### 1.C Reproducibility release, archive, licence (D37; disk; results)

> L1780: | DL-037 / D37 | Code licence and archive | MIT licence; release archived with a persistent identifier; service chosen at MS15 | Institutional requirement |
>
> L949: **Disk.** Map cells keep metrics plus v and r at 1 kHz in float32, about 1 MB per cell. Full series are kept only for examples, the subgrid and network runs. Estimated total: under 20 GB. Series are written with np.savez_compressed, and MS15 decides which result families are archived (D37).
>
> L1228: results/ and figures/ are git-ignored, so outputs are never edited by hand. Everything the paper uses is archived with the release (D37). docs/decision_log.md follows Appendix C. Entries are never deleted; a change gets a new entry that links back to the old one.
>
> L1096:     # outputs (never edited by hand; archived with the release, D37)
>
> L1017: Sources: R5 (Sandve and Nordlie rules; corpus practice on code, seeds and versions) \[R5, SQ6, recommendations\]; R7 (code and parameter sets; integrator and tolerances reported; archive with a version identifier) \[R7, §2.5–2.6, §6 rec. 6\]; R6 (no code mandate at MNA, but software and data must be credited) \[R6, §2.1, §8(d)\]. Names come from handoff (d) and (e); A0, A11, S16 and the figure scripts are Part 2 additions.
>
Also in the decision log: DL-037 (docs/decision_log.md lines 365 to 373): "Chosen: MIT licence; release archived with a persistent identifier; service chosen at MS15   Default from: Part 2", Test "Institutional requirement", Status "default adopted".

### 1.D Repository tree items that belong to the release (section 10.1)

> L1022:     ├── README.md                    Windows setup, run order, figure map
>
> L1023:     ├── CHANGELOG.md                 one entry per release tag
>
> L1025:     ├── LICENSE, CITATION.cff        licence and citation (D37)
>
> L1028:     ├── .github/workflows/tests.yml  fast tests on windows-latest (optional)
>
> L1033:     ├── environment/
>
> L1034:     │   ├── requirements.in          direct dependencies, == pins (MS0)
>
> L1035:     │   ├── requirements-lock.txt    full pip freeze (UTF-8)
>
> L1036:     │   ├── python-version.txt       interpreter used at MS0
>
> L1037:     │   └── julia/                   Project.toml, Manifest.toml (committed),
>
> L1038:     │                                setup_julia.jl
>
> L1064:     │   ├── check_clean_tree.py      blocks tagged builds from a dirty tree
>
> L1065:     │   └── make_all.ps1             pipeline in milestone order
>
> L1072:     │                                figure_map.md, search_log.md,
>
> L1073:     │                                plan.md (Markdown copy of this plan)
>
> L1074:     ├── results/                     NOT TRACKED (git-ignored)
>
> L1075:     └── figures/                     NOT TRACKED (git-ignored)
>
> L1081: **Additions.** Besides src/, the tree adds CHANGELOG.md, the optional CI file, \_\_init\_\_.py in each package folder and the pytest marker for slow tests. Julia's Manifest.toml is committed, not ignored, because it pins the exact Julia package versions \[reasoned, not tested\]. The CI file installs the package (pip install -e .) and runs only pytest -m "not slow" on windows-latest; slow tests, Julia and all runs stay on the Ryzen PC. CLAUDE.md, .claude/ and docs/plan.md are described in section 10.9.
>
### 1.E README (section 10.2)

> L1128: ## 10.2 README: Windows setup (PowerShell)
>
> L1130: Prerequisites: Python 3.11 from python.org (with the py launcher), Git for Windows, and Julia (for A5 only). Record the exact Python installer version in environment/python-version.txt and check that py -0p lists 3.11 and py -3.11 starts it. Pin the Julia version (for example with juliaup) and record it. Keep the repository near the drive root and outside OneDrive.
>
> L1132:     git clone <repository-url> mpr-gamma-surge; cd mpr-gamma-surge
>
> L1133:     py -3.11 -m venv .venv
>
> L1134:     Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # once, if activation is blocked
>
> L1135:     .\.venv\Scripts\Activate.ps1
>
> L1136:     python -m pip install -r environment\requirements-lock.txt
>
> L1137:     python -m pip install -e . --no-deps
>
> L1138:     julia --project=environment\julia environment\julia\setup_julia.jl   # A5 only
>
> L1139:     python -m pytest -m "not slow"
>
> L1140:     python scripts\time_one_run.py --config configs\S5.yaml --cell headline --repeat 3
>
> L1141:     python -m mprsurge.run --config configs\S3.yaml --workers 6
>
> L1142:     python scripts\fig_FS2.py
>
> L1143:     # after a deliberate upgrade; writes UTF-8, not UTF-16:
>
> L1144:     python -m pip freeze --exclude-editable |
>
> L1145:         Out-File -Encoding utf8 environment\requirements-lock.txt
>
> L1147: The README also states the integrator, tolerances, step sizes, initial conditions, ramp protocol and gamma-power computation \[R7, §6 rec. 6\]. Julia is set up from a script file to avoid PowerShell quoting problems (CP8). On a clean machine: \<repository-url\> is a placeholder (in PowerShell, \< is reserved); a repository downloaded as a ZIP carries Mark-of-the-Web, so run Get-ChildItem -Recurse \| Unblock-File before activation; add -Force to Set-ExecutionPolicy when it is scripted; calling .venv\Scripts\python.exe directly avoids activation. Bootstrap order (MS0): install the direct dependencies, write environment/requirements.in with == pins from that first successful install, then write requirements-lock.txt with the freeze command above; later installs use the lock.
>
### 1.F Provenance, Numba cache, Nordlie tables (sections 6.6, 8, 10.4)

> L1178: ## 10.4 Provenance
>
> L1182: - the git commit, branch, tags and a dirty flag;
>
> L1184: - versions of Python, packages, Julia and BifurcationKit;
>
> L1186: - OS and CPU;
>
> L1188: - SHA-256 of every input and output file;
>
> L1190: - the hash of the criteria file.
>
> L1200: - Numba cache: make_all.ps1 clears the Numba cache files (\*.nbi, \*.nbc) before every tagged run and records this in provenance; jitted code never reads config values from module globals; the cache is warmed in the parent before the worker pool starts.
>
> L777: - Each run also writes a Nordlie-format parameter table from its config (make_param_table), because parameters are easily omitted from text \[R7, Pauli 2018; R5\] \[verified\]. Figures come only from scripts reading stored results (Sandve rules) \[R5; R7\] \[verified\].
>
> L896: Each figure also gets a Nordlie parameter table \[R5, SQ6; R7, §2.5\] \[verified\].
>
> L1224: *Table 10.1. Unit tests. Run pytest -m "not slow" before every commit and the full suite before every tag. Every test states its tolerance; synthetic noise is seeded; comparisons are within one process or with tolerances, never bitwise against stored arrays (CPUs differ).*
>
### 1.G Tags and git workflow (section 10.7)

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
### 1.H Reproducibility checklist 10.8 (the first half of the MS15 done-when)

(In the file every item is numbered "1." because of the markdown conversion; the numbers below are the reading order, items 1 to 8.)

> L1262: ## 10.8 Reproducibility checklist
>
> L1264 (item 1): 1.  Clone release-v1.0 on a clean Windows machine and install from the lock files.
>
> L1268 (item 2): 1.  Run pytest; all tests pass, including slow ones.
>
> L1272 (item 3): 1.  Run scripts\make_all.ps1 -Stage replication; every G0 row passes.
>
> L1276 (item 4): 1.  Rebuild one figure from the archive; metrics match within the RB6 tolerances, not bit for bit \[R7, §2.6\].
>
> L1280 (item 5): 1.  Re-run one sweep cell with --from-record \<json\>; its metrics match within tolerance.
>
> L1284 (item 6): 1.  Every provenance file names the release commit and none is marked DRAFT.
>
> L1288 (item 7): 1.  Nordlie tables, seeds, versions, OS and CPU are present for every figure and run \[R5, recommendations\].
>
> L1292 (item 8): 1.  Code and results are archived with a version identifier \[R7, §8(d)\], and reused software is credited \[R6, §2.1\].
>
### 1.I Manuscript and submission checklist (below Table 11.2; the second half of the MS15 done-when)

> L1384: **Manuscript and submission checklist (MS15).** From R7 §8(d) and R6 §6 and §8(d); checked before submission:
>
> L1386: - A one-sentence contribution and its scope in the abstract and at the end of the introduction \[R7, §8(d)\].
>
> L1388: - An assumptions and limitations section: the exact-reduction assumptions, the single population, the hypoxia proxy and the 2-of-4 motivation \[R7, §8(d)\], plus the limits of a power-based classifier (Table 2.1).
>
> L1390: - Nordlie parameter tables, one per experiment or figure; every caption states the parameter regime and the take-home message \[R7, §8(d)\].
>
> L1392: - Code archived with a version identifier, parameter files, integrator and tolerances; failure regimes reported alongside surge regimes \[R7, §8(d)\].
>
> L1394: - No causal, clinical or consciousness claims; neutral patient language \[R7, §8(d)\].
>
> L1396: - Conflicts of interest and AI-use disclosure \[R7, §8(d)\]; conflicts declared to the Editor-in-Chief, and reused figures, code or data credited \[R6, §8(d)\].
>
> L1398: - Submission through the MNA site with an arXiv identifier (CC-BY 4.0 licence) and an MNA account with an ORCID; a suggested handling editor with exact mean-field or neural mass experience (Laing, Coombes and Ashwin are documented by their publications) \[R6, §6, §8(d)\].
>
> L1400: - Before submitting, check the MNA Submission page by hand or email the editorial office for length, template and code policy; claim no specific indexing \[R6, §6\].
>
> L1402: - Revisions: a response letter in Noble format and new arXiv versions; after acceptance, the MNA LaTeX template within 30 days \[R7, §8(d); R6, §8(d)\].
>
**Status of the last three bullets (L1398, L1400, L1402).** They name the MNA site, an arXiv identifier, CC-BY 4.0, an MNA account with an ORCID, an MNA submission page, a response letter "in Noble format", new arXiv versions and the MNA LaTeX template. By user ruling the venue is Peer Community Journal and MNA is dropped (DL-716 X4, DL-720; ruling R1, DL-554 stands); the decision log supersedes these lines for the venue; the plan is not edited. They are quoted because the prompt asks for them; what replaces them is UNVERIFIED (section 1.K).

### 1.J Other plan lines that touch MS15 (data deposit, scope, history)

> L301: - Multi-node networks and conductance-based neurons; the Xu raw EEG on Zenodo (D10; default out) \[needs decision\]; Cauchy-noise mean field (equations absent).
>
> L1753: | DL-010 / D10 | Xu raw EEG | out of scope | Scope change only |
>
> L1916: | T34 | Table 11.1 MS15; checklist after Table 11.2 | Manuscript and submission checklist from R7 §8(d) and R6 §6, §8(d) (ASK, accepted) |
>
> L1418: | CP5 | Section 6.6: "PLOS CB and JCNS require public code and parameter sets" | JCNS requires code and parameter sets; PLOS CB requires code | R7 §2.1, §2.5 | Parameter sets: JCNS only. No change to the plan |
>
L301 and DL-010 are about the third-party Xu 2023 raw EEG on Zenodo, which the plan puts out of scope: no external data set is reused, so the plan's "reused ... data credited" (L1396) has no external data to name apart from what the reference list gives (UNVERIFIED reading).

### 1.K Search terms and what they found (B2 completeness)

Searched in docs/plan.md (case-insensitive): MS15, zenodo, archiv, persistent identifier, README, licen[cs]e, MIT, CC-BY, AI-use, disclosure, requirements-lock, environment/, clean machine, 10.8, DOI, ORCID, conflict, Nordlie, CITATION, CHANGELOG, release-v1, make_all, data availability, data statement, code availability, figure_map, credit, persistent, version identifier, backup, template, response letter, Editor-in-Chief, generative, AI-generated, illustrat.

- **No passage** says: "no AI-generated illustrations"; a data-availability, code-availability, funding or ethics statement; a backup rule; Zenodo or any named archive for the release (only "service chosen at MS15", L1780); a licence for data or figures (CC-BY 4.0 appears once, L1398, superseded for the venue); a Peer Community Journal template or policy (the word "template" appears at L1400 and L1402 for MNA only); the Zenodo limits (100 files, 50 GB per record).
- **Not quoted, with the reason:** DOI hits in the reference list and in conflict rows (L1459 and others, third-party papers); L1635 (Xu 2023 data DOI 10.5281/zenodo.7803212, a third-party record); "conflict" hits (C1 to C24, scientific conflicts between reports, not conflicts of interest); L153 (Appendix C decision log template); L533 (PyRates "QIF template").
- **Repository sources for the venue and for Zenodo:** docs/ms13_figure_rules.md R1 (line 37, PCJ prefers jpg, tiff or png, forbids svg, wmf and emf, "states no resolution, size or colour rule", figures in line with the text inside 2.54 cm margins; "read by the user; not re-read here"; template and page size not read), R10 (line 46) and T12 (line 70): "the supplement notes that it is to be zipped for the Zenodo record" (the F1 source-data CSV, 28 MB); configs/journal_export.yaml line 37: "pdf_size_flag_mb: 5  # UNVERIFIED; arXiv and Zenodo limits are to be checked by hand at MS15"; docs/ms13_13w_notes.md line 105: "the plan names only 'a persistent identifier, service chosen at MS15' (D37, plan line 1780)". No file states the Zenodo limits, CC-BY for data or figures, or an AI-use rule.

## 2. What the repository already holds for MS15 (B3; read-only listing; sizes read, nothing copied or moved)

**Environment and lock files** (tracked)
- environment/requirements.in: 8 direct pins (numpy 2.4.6, scipy 1.17.1, numba 0.68.0, matplotlib 3.11.2, pyyaml 6.0.3, pandas 3.0.6, pyarrow 26.0.0, pytest 9.1.1); begins with a BOM.
- environment/requirements-lock.txt: 23 lines. Whether it equals a fresh freeze of .venv was NOT checked here (UNVERIFIED).
- environment/python-version.txt: "Python 3.11.9", installed with winget. environment/julia-version.txt: "julia version 1.10.11". environment/julia/Project.toml, Manifest.toml, setup_julia.jl.
- pyproject.toml: package mprsurge 0.1.0, requires-python ">=3.11,<3.12", the same 8 pins, pytest marker "slow".
- .gitignore and .gitattributes (`* text=auto eol=lf`, binaries) as the plan shows them.

**Tags** (git, read this step; none created, moved or deleted)
- env-v1: annotated, tag object bfb8ce3ad34407a7849524263d6d8f639279bfc6, commit 034a565828191dc730f5cd4ecd4169da7b84181a, 2026-10-14, "MS0: skeleton, pinned environment, lock file, smoke test".
- tolerances-frozen: annotated, 9c7fee3c94cc5579d59b3889eca1c43a0f24c9d6 at bd301ce9fd3ca05d67020cb575c055148b3bdabc; message names the SHA-256 of configs/replication.yaml 667d3b788d1c7c5aebc716998d09746b685358f326334aae87591924908819a5.
- criteria-frozen: annotated, 0ad5793c1c64b04f40efba6b121b7e41743dbe83 at dd8330c5eaacd63d21e7b7969430988d00862769; criteria SHA-256 c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05.
- replication-pass: a LIGHTWEIGHT tag (not annotated) at 3d02526c605cdb46e2f723344ae2ac5d86eaef5e; the plan (L1236) says "All annotated" (an existing departure; no tag is touched).
- 13 fig-<ID>-v1 tags, annotated, local, all at e6666cb2e8120a1619527c5ee7fce01e1beedb55 (`ms13_make_tags.py --verify --target e6666cb...`: 13 of 13). No release-v1.0 tag exists. 17 tags in all.
- Tagger and committer of tags and commits: "Your Name <you@example.com>" (git config placeholder). git remote: none configured (`git remote -v` prints nothing); current branch master (the plan's workflow says main, L1232 to L1258).

**README, LICENSE and friends**
- README.md (tracked, 24 lines, last changed in the MS0 commit 6eb50ff): the Windows setup block of plan section 10.2, the sentence "The README also states the integrator, tolerances ...", and a last heading "To be filled when the code exists" with no body. So it is the MS0 skeleton: no integrator, tolerances, run order or figure map.
- CHANGELOG.md: one line, "# Changelog" (with a BOM).
- LICENSE: none found. CITATION.cff: none found. docs/figure_map.md: none found. scripts/make_all.ps1: none found. .github/ (CI): none found (optional in the plan). CLAUDE.md exists (project rules).

**Figure and evidence documents** (tracked)
- docs/ms13_journal_final_hashes.txt: 242 lines, 177 file entries (full SHA-256) for the 13 journal figures and the 11 drafts, the build commit 5e9057563c6c24fbac16b99000e547d08ef9a31a (FS1: f5d3f0d8858c5c523f53985bba36dbb3fca77fe7) and the drawn-data digests; all 177 files exist on this machine and equal their hash (checked this step).
- docs/ms13_evidence_sheet.md (13v): per figure evidence, tags, drafts, "What this evidence does not show".
- docs/ms13_close.md and docs/ms13_close_items.md: close state, user tasks, open items (49 to 53, 55, 57, 60 to 62 open at the start of this step).
- docs/search_log.md: plan Table E.1 plus MS14 items 1 to 7 as "Not done natively on Nov 10; general web-search pre-check only"; G8 outcome "to be written by the user".
- docs/manuscript_limitations_novelty.md: ONE draft paragraph (prior-work check) for the user to edit.
- docs/ms13_figure_manifest.csv (104 rows, checked by scripts/ms13_check_hashes.py: 0 problems), docs/ms13_export_checklist.json, docs/ms13_13v_checklist_recheck.md, docs/claim_limit_labels.md, docs/ms13_conventions.md, docs/robustness_criteria.md (its first lines still read "FINAL CONTENT FOR THE FREEZE, NOT YET FROZEN" although the tag criteria-frozen exists; its SHA-256 7ed9b3cf3c349a05bc5a0f14b4ba60f3328d875c524f97ca1fd3adea5a0cda7c equals the blob in the tag; see section 8).
- docs/decision_log.md: DL-037 (D37) default adopted; the plan copy docs/plan.md (2216 lines).

**Source-data files** (git-ignored, figures/journal/supplement/, 39 files, 41.1 MB)
- F1_source_data.csv: 28,821,335 bytes (about 28.8 MB; R10, T12: to be zipped for the Zenodo record; not zipped yet). FS1_source_data.csv about 9.7 MB; F3_source_data.csv about 0.8 MB; the others smaller. Each figure also has _supplement.md and _alt_text.txt there.

**Git-ignored folders** (`git check-ignore`: .gitignore lines 13 and 14; `git ls-files results figures` lists 0 files)
- results/: 32,070 files, 32,575.4 MB (about 32.6 GB), NOT tracked. Largest families: S7 16,665 MB (13,900 files), S12x 8,740 MB (9,076 files), S5 2,620 MB, S13 1,046 MB, S12 946 MB, D31 707 MB, S11 687 MB; the rest under 400 MB each. The plan's estimate was "under 20 GB" (L949). Per-run Nordlie tables exist as results/<ID>/*_params.md (for example results/A0/A0_0000_724055e00481_params.md).
- figures/: 227 files, 114.9 MB, NOT tracked, in no tagged tree (DL-723). Folders: F1 to F6 and FS1 to FS5 (the eleven drafts, audit copies), journal/ (145 files, 102.7 MB: the 13 journal figures, supplement/, export_manifest.csv), _review, style. The journal figure files exist only on this machine.
- .venv/ (611 MB), .pytest_cache/, __pycache__ folders, src/mprsurge.egg-info/, .claude/settings.local.json, .claude/scheduled_tasks.lock (not project files).

**Scripts that rebuild or check figures**
- scripts/fig_journal.py <IDs>: builds the journal export from results/ only (no simulation). The provenance records of the 13 journal figures hold wall_time_s of 2.3 to 13.9 s each, 85.4 s in all (read from the 13 *_journal_provenance.json; figure build only). A documented time to regenerate results/ from the configs (the simulations): none found in one place (UNVERIFIED; the plan L229 gives an estimate for the P2 runs only).
- scripts/fig_F1.py to fig_FS5.py (drafts), scripts/ms13_make_tags.py, ms13_check_hashes.py, ms13_verify_export.py, ms13_write_final_hashes.py, ms13_independent_compare.py, check_clean_tree.py, time_one_run.py, run_A0.py to run_A11.py and many run_S*/ms*_list scripts. python -m mprsurge.run takes --config, --set, --workers, --longest-first, --dry-run; it has NO --from-record option (searched src/ and scripts/: only a test whose name contains "from_records").
- Tests: 125 .py files under tests/; the last full fast suite: 1572 passed, 24 deselected, 9 xfailed, exit 0, 1405.18 s (DL-726). The 24 deselected are the slow tests (marker "slow"); the plan's 10.8 item 2 wants "all tests pass, including slow ones"; a full-suite run including them is not shown at the current HEAD (UNVERIFIED).

**Drafts of README, data statement, code statement or manuscript text**
- README.md (the MS0 skeleton above) and docs/manuscript_limitations_novelty.md (one limitations paragraph about prior-work checking). Nothing else: no data statement, no code statement, no abstract, no manuscript file, no .tex, .bib or .docx, no cover letter, no CITATION.cff, no LICENSE.
- Folders and patterns searched: the whole tree except .git and .venv (docs/, src/, tests/, scripts/, configs/, environment/, figures/, results/, the root; also paper/, manuscript/, submission/, release/, dist/: those folders do not exist) for file names matching *readme*, *data_statement*, *code_statement*, *availability*, *manuscript*, *abstract*, *cover*letter*, *.tex, *.bib, *.docx, *.cff, LICENSE*. Hits: README.md, .pytest_cache/README.md (pytest's own), docs/manuscript_limitations_novelty.md, results/**/*_params.md (run parameter tables), PDFs of the figures.

**Other facts relevant to the release**
- The 13 journal provenance records (figures/journal/<ID>/<ID>_journal_provenance.json) all hold draft = true, git.dirty = false, git.tags = [], and the build commit 5e90575 (FS1: f5d3f0d), status ok. The plan's item 6 (L1284) asks that "Every provenance file names the release commit and none is marked DRAFT" (section 3, item 18, and section 8).
- Git: 599 tracked files, 686 commits, .git 163.5 MB.

## 3. What the plan requires at MS15, and what exists (B4 (a) and (b))

Status words: EXISTS (path), PARTLY, MISSING, NOT MET AS BUILT, SUPERSEDED. "Quote" gives the plan lines in section 1.

| # | Required at MS15 (plan quote lines) | Status | Evidence in the repository |
| --- | --- | --- | --- |
| 1 | An archive service with a persistent identifier chosen (D37; L1366, L1780, L1292) | MISSING (a decision) | DL-037 says "service chosen at MS15"; only the F1 CSV Zenodo record is mentioned in the repository (R10, T12) |
| 2 | Code licence MIT; a LICENSE file (L1780, L1025) | MISSING | DL-037 "default adopted" (MIT); no LICENSE file |
| 3 | CITATION.cff (L1025) | MISSING | none found |
| 4 | Annotated tag release-v1.0, after the full suite (L1248, L1264, L1224) | MISSING | no such tag; not to be created in sub-step 17 |
| 5 | Decide which result families are archived; outputs archived with the release (L949, L1228, L1096) | MISSING (a decision) | results/ 32.6 GB, 32,070 files, git-ignored; figures/ 114.9 MB, git-ignored |
| 6 | README: setup, run order, figure map, integrator, tolerances, step sizes, initial conditions, ramp protocol, gamma-power computation (L1022, L1128 to L1147) | PARTLY | README.md, 24 lines, MS0 skeleton, "To be filled when the code exists" |
| 7 | CHANGELOG.md, one entry per release tag (L1023) | PARTLY | CHANGELOG.md has only its title |
| 8 | Environment files (L1033 to L1038) | EXISTS | environment/ (requirements.in, requirements-lock.txt, python-version.txt, julia-version.txt, julia/Project.toml, Manifest.toml, setup_julia.jl); currency of the lock not re-checked here |
| 9 | scripts/make_all.ps1, pipeline in milestone order, `-Stage replication`, clears the Numba cache before a tagged run (L1065, L1272, L1200) | MISSING | no such file; scripts/check_clean_tree.py (L1064) exists; run_A0.py etc. exist |
| 10 | docs/: decision_log.md, robustness_criteria.md, figure_map.md, search_log.md, plan.md (L1071 to L1073) | PARTLY | all but docs/figure_map.md exist; robustness_criteria.md has a stale header (section 8) |
| 11 | Optional CI file .github/workflows/tests.yml (L1028) | MISSING (optional) | none |
| 12 | 10.8 item 1: clone release-v1.0 on a clean Windows machine, install from the lock files (L1264) | NOT STARTED | needs the tag, a repository the user can clone, a clean machine (user); README commands exist |
| 13 | 10.8 item 2: pytest all pass, including slow (L1268) | PARTLY | fast suite 1572 passed (DL-726); the 24 slow tests not shown at HEAD |
| 14 | 10.8 item 3: `make_all.ps1 -Stage replication`, every G0 row passes (L1272) | MISSING (script) | tag replication-pass (lightweight); scripts/run_A0.py; results/A0 |
| 15 | 10.8 item 4: rebuild one figure from the archive, metrics within the RB6 tolerances (L1276) | PARTLY | scripts/fig_journal.py reads results/ only; an FS5 rebuild from committed code gave the same bytes as the hash list, except that the supplement differs in the build-commit line and the provenance-file hash (DL-714); needs the archived results/ |
| 16 | 10.8 item 5: re-run one sweep cell with `--from-record <json>` (L1280) | MISSING | mprsurge.run has no --from-record option |
| 17 | 10.8 item 6: every provenance file names the release commit, none marked DRAFT (L1284) | NOT MET AS BUILT | the 13 journal records: draft = true, build commit 5e90575 / f5d3f0d (section 8) |
| 18 | 10.8 item 7: Nordlie tables, seeds, versions, OS and CPU for every figure and run (L1288) | PARTLY | per-figure <ID>_params.csv and provenance (seeds, packages, os, cpu keys); per-run results/*/*_params.md; completeness for every run not checked here (UNVERIFIED) |
| 19 | 10.8 item 8: code and results archived with a version identifier; reused software credited (L1292) | MISSING | nothing archived; hash list and tag messages carry SHA-256 only |
| 20 | One-sentence contribution in abstract and end of introduction (L1386) | MISSING | no manuscript; the claim wording is plan L305 and section 2.6 (not copied here) |
| 21 | Assumptions and limitations section: exact-reduction assumptions, single population, hypoxia proxy, 2-of-4 motivation, limits of a power-based classifier (L1388) | PARTLY | docs/manuscript_limitations_novelty.md (one paragraph, prior-work check only); limits material in docs/ms13_close.md, docs/claim_limit_labels.md, figure captions |
| 22 | Nordlie parameter tables per experiment or figure; every caption states regime and take-home (L1390) | PARTLY | journal captions and <ID>_params.csv exist; close item 45 accepted as a disclosed limitation (short captions do not hold full parameters; full captions do); no manuscript tables |
| 23 | Code archived with version identifier, parameter files, integrator and tolerances; failure regimes next to surge regimes (L1392) | PARTLY | failures are shown in captions and docs/ms13_close.md section 2; archive missing |
| 24 | No causal, clinical or consciousness claims; neutral patient language (L1394) | MISSING (cannot be checked without manuscript text) | no manuscript |
| 25 | Conflicts of interest and AI-use disclosure; conflicts to the Editor-in-Chief; reused figures, code, data credited (L1396) | MISSING | needs the user; no text in the repository |
| 26 | MNA submission, arXiv identifier, CC-BY 4.0, MNA account with ORCID, suggested handling editor, MNA page check, Noble-format response letter, MNA LaTeX template (L1398 to L1402) | SUPERSEDED for the venue (DL-716 X4, DL-720); PCJ equivalent UNVERIFIED | nothing in the repository sources PCJ steps beyond R1 (figures) |
| 27 | G8 outcome shapes the manuscript (L1382) | OPEN | docs/search_log.md section 4: "to be written by the user" (close item 60) |
| 28 | Novelty statement limited to the pre-check (DL-732 A3; not a plan line) | PARTLY | docs/manuscript_limitations_novelty.md draft paragraph |

## 4. What the user must supply or decide (B4 (c)); each becomes one open close item (63 to 76)

1. (63) Archive service and account for the release. Plan: D37, L1780: "service chosen at MS15". The repository names Zenodo only for the zipped F1 CSV record (R10, T12). Whether the same service takes the release is not stated (UNVERIFIED).
2. (64) Licences. Code: MIT by DL-037 (default adopted); the name for the LICENSE copyright line is not in the plan or the repository (UNVERIFIED: the user supplies). Data and figures: the plan names CC-BY 4.0 only inside the superseded MNA line (L1398); for PCJ it is UNVERIFIED.
3. (65) Author names, affiliations, ORCID (plan names an ORCID only for the MNA account, L1398, superseded), funding, ethics, data and code availability statements, the conflict-of-interest statement and the AI-use disclosure text (plan source: L1396 for conflicts and AI-use only; the other statements have no plan source: UNVERIFIED whether the venue wants them).
4. (66) The manuscript text and who writes it: abstract, introduction contribution sentence, assumptions and limitations, parameter tables, claims check (plan: L1384 to L1396). No manuscript file exists.
5. (67) Which result families and which figure files go into the archive, and how to handle 32.6 GB in 32,070 files (plan: L949, "MS15 decides which result families are archived"). Whether a per-record file-count or size limit applies is UNVERIFIED (the 100 files and 50 GB figures are not sourced).
6. (68) The backup folder for figures/ and the repository (close.md section 4 task 2), a remote for the repository and where the 13 figure tags and the other four tags are pushed (no remote is configured; plan L1132 and L1147 use the placeholder <repository-url>; L1258 pushes `origin main`, the branch here is master).
7. (69) The tagger and author identity "Your Name <you@example.com>" on all commits and 17 tags (a git config placeholder; the identity will be in the archived history). Claude Code does not change or move tags; whether to leave it is the user's call.
8. (70) Checklist 10.8 item 6 (L1284): the 13 journal provenance records say draft = true and name the build commit, not a release commit. Options for the user (no recommendation on the science): accept them as built and say so in the release notes (a departure from the literal item), or rule a rebuild from the release commit (new hashes, new v2 tags; "no rebuild after the review" was the rule of 13t).
9. (71) Scope of the code and document additions that the checklist needs: LICENSE, CITATION.cff, a full README, CHANGELOG entry, docs/figure_map.md, scripts/make_all.ps1 with -Stage replication, a --from-record option for mprsurge.run. Changes under src/ or tests/ trigger the full fast suite.
10. (72) The clean Windows machine for 10.8: which machine, with Python 3.11, Julia 1.10.11 and Git, and who runs it (Claude Code cannot).
11. (73) The zipped F1 source-data CSV (R10, T12; close.md section 4 task 5): when it is made and where it is stored.
12. (74) The PCJ and PCI requirements (template, policies on code and data, AI-use disclosure, figure rules, licences, the PCI recommendation process): the user reads the pages; Claude Code cannot.
13. (75) docs/robustness_criteria.md header still says "NOT YET FROZEN" (section 8): leave it as in the tag, or correct it before the archive.
14. (76) Permission and time to run the full suite including the 24 slow tests before the release tag (CLAUDE.md: "Run the full suite before every tag"; L1224, L1268); its run time is not documented (the fast suite took 1405.18 s, DL-726).

Already open elsewhere and bearing on MS15 (not duplicated as new items): the G8 outcome (item 60), the limitations paragraph (61), the wording of items 5 and 6 of MS14 (62), the open figure items 49 to 53, 55, 57 (item 51: N written as 1e3 in two alt texts; item 55: EPS extras differ between builds, so EPS cannot carry a fixed hash), and the human check by someone who has not seen the project (close.md section 4 task 4).

## 5. What needs web access or an account, so Claude Code cannot do it (B4 (d))

- Creating or using an archive account and uploading (Zenodo or another service): an upload and an account; restricted by this step's rule "no upload, no web", by CLAUDE.md ("Do not push or tag unless asked") and by the fact that Claude Code has no internet. A persistent identifier (DOI) exists only after a deposit.
- Reading the PCJ and PCI pages, templates and policies (code and data policy, AI-use disclosure, figure rules, licences, the recommendation process): web; "no web search" and CLAUDE.md "Never invent an equation, value or citation" (so no statement about them is written from memory).
- Pushing the repository or tags to a remote; creating a remote: "do not push".
- The clean-machine run of checklist 10.8 (a second Windows machine, a fresh clone, a fresh install of the lock files): a machine and an install; "install no package" in this step; the user runs it and reports.
- The ORCID, author details, funding, ethics, conflicts and AI-use text: information only the user holds.
- Any native literature check (MS14): already ruled not done.

## 6. The order the plan implies for the MS15 steps (B4 (e))

The plan states no order inside MS15. What it does state: MS14 unlocks "G8; MS15" (L1365); MS15 is the last milestone ("Unlocks End", L1366); the checklist 10.8 lists items 1 to 8 (L1264 to L1292) and item 1 starts from the tag release-v1.0 (L1264); the full suite runs "before every tag" (L1224); the manuscript checklist is "checked before submission" (L1384); G8 "shapes the manuscript at MS15" (L1382). The sequence below is INFERRED and UNVERIFIED:

1. User rulings on section 4 items 63 to 76 (service, licences, result families, provenance DRAFT question, scope).
2. Release files: LICENSE, CITATION.cff, README body, CHANGELOG entry, docs/figure_map.md; make_all.ps1 and --from-record (code; tests; full fast suite).
3. Resolve item 70 (provenance draft flag and release commit).
4. Clean tree, full suite including slow tests, annotated tag release-v1.0 (only on the user's instruction).
5. Archive packaging (zip the F1 CSV, select result families, manifest and hashes); deposit by the user (account).
6. Checklist 10.8 on a clean Windows machine (the user), items 1 to 8.
7. Manuscript text against the manuscript checklist (G8 outcome, limitations, contribution sentence, tables, CoI and AI-use, claims check); PCJ and PCI steps read by the user.
8. A possible circularity, UNVERIFIED: the persistent identifier exists only after the deposit, while CITATION.cff, README and the manuscript may want to cite it, and 10.8 item 6 asks the provenance to name the release commit; a second small commit or a version note may follow the deposit.

## 7. Size estimate in Claude Code steps (B4 (f); UNVERIFIED; no time estimate)

About 12 to 22 further prompts, as follows (each prompt may need a ruling by the user before it): rulings and decision-log entries 1 or 2; release documents (LICENSE, CITATION.cff, CHANGELOG, figure_map, README body) 2 to 3; make_all.ps1 and --from-record with tests and the full fast suite 2 to 4; the provenance DRAFT question and, if a rebuild is ruled, one build step with checks 1 to 3; archive packaging and manifests 1 to 2; full suite with slow tests and the release tag 1 to 2; reporting the user's clean-machine run 1 to 2; manuscript-checklist support (the user writes the text; Claude Code checks claims, tables and numbers against the stored results) 2 to 4.

## 8. Findings and observations (read-only; nothing changed for them)

- The 13 journal provenance records are marked draft = true and name the build commit (5e90575; FS1 f5d3f0d), which is not the commit of the 13 tags (e6666cb) and not a future release commit. Checklist item 6 (L1284) is therefore not met as built (item 70 above). This is a finding, not a stop: no value disagrees with an expectation recorded earlier (docs/ms13_close.md says the records have dirty = false and names the build commit).
- docs/robustness_criteria.md says "FINAL CONTENT FOR THE FREEZE, NOT YET FROZEN" in its opening lines although criteria-frozen exists; the YAML file is stated to be authoritative in the same text. The file equals its blob in the tag, so a correction would be a deliberate change to a frozen-era file (item 75).
- The lightweight tag replication-pass departs from "All annotated" (L1236); the tagger identity is a placeholder; there is no remote; the branch is master where the plan writes main.
- results/ is 32.6 GB, above the plan's "under 20 GB" estimate (L949); the figure files and results/ exist only on this machine until backed up (close.md section 4 task 2).
- README.md and CHANGELOG.md begin with a byte-order mark (README.md was checked as text only; the BOM was seen in CHANGELOG.md, requirements.in, python-version.txt and julia-version.txt). The plan's own lock-file command writes UTF-8 (L1143 to L1145). Whether the BOM matters is UNVERIFIED.

## 9. UNVERIFIED in this file (all of it needs the user or a source)

The PCJ template, policies and figure rules beyond R1; a versioned DOI repository; CC-BY for data and figures; "no AI-generated illustrations"; the Zenodo limits (100 files, 50 GB per record) and whether they apply; the AI-use disclosure wording; "confirm the PCI section"; whether Zenodo is the service for the release; the order in section 6; the step counts in section 7; whether the lock file equals a fresh freeze; whether the slow tests pass at HEAD; whether per-run parameter tables exist for every run; the BOM remark; the reading of L1396 "reused ... data" for this project.

## User rulings of 2026-11-10, 17:22 local time (America/Toronto)

Recorded in sub-step 18 (DL-736, ruling labels C1 to C8 of that prompt). The block below is the user's text word for word (one paragraph in the chat message; the characters are unchanged).

```text
Let's adjust the MS15 plan. I am ruling to split MS15 into two sub-steps: - MS15a: Reproducibility Release (LICENSE, CITATION.cff, make_all.ps1, README.md updates, git tags/config, and figure provenance/DRAFT flags). - MS15b: Manuscript & Submission (handled outside/later). We do NOT need the manuscript text drafted inside the code repository for MS15a. Here are the five release decisions for MS15a: 1. Code licence: MIT 2. Data/Text licence: CC-BY 4.0 3. Archive service: Zenodo 4. Author details: - Full Name: Daniel Voldman - Email: daniel.voldman@proton.me - Affiliation: Independent Researcher - ORCID: 0009-0005-3409-8944 - Funding: No funding received. - Conflict of Interest: The author declares no conflicts of interest. 5. GitHub: Yes, push to GitHub remote. I have backed up C:\dev\mpr-gamma-surge and configured git (git config user.name "Daniel Voldman" and user.email "daniel.voldman@proton.me"). Please proceed with MS15a now: generate the release files (LICENSE, CITATION.cff, make_all.ps1, README update), set up the repository metadata, update the DRAFT flags / provenance records, and prepare the release tags. Skip drafting manuscript files for this turn.
```

**What this changes in this file (sub-step 18; the plan is not edited).**

- **C1, the split.** MS15 is split by user ruling into MS15a (reproducibility release) and MS15b (manuscript and submission, outside the repository and later). The plan's MS15 row (L1366) has one done-when: "Checklist 10.8 passes on a clean machine; submission checklist complete". The split is a DEPARTURE FROM THE PLAN. MS15 is NOT complete until MS15b is done. MS15a's own done-when: checklist 10.8 (items 1 to 8) passes on a clean machine and the release is archived. Sections 1.I (manuscript checklist), 3 rows 20 to 28 and 4 item 66 now belong to MS15b; they are kept as written in sub-step 17.
- **C2, the decisions.** Code licence MIT (D37, L1780). Data, figure and text licence CC-BY 4.0 (user ruling; the plan names CC-BY 4.0 only in the superseded L1398; whether Peer Community Journal requires or accepts it is UNVERIFIED, item 74). Archive service Zenodo (D37: "service chosen at MS15"). GitHub remote: yes; URL and public or private not yet given (needed for part 2).
- **C3, author details** as given above (and used exactly in LICENSE, CITATION.cff, .zenodo.json and README.md). They become public when the repository is pushed or archived (the user chose this). Nothing else personal is added.
- **Data record, a separate decision (D37, L949).** `.zenodo.json` describes the SOFTWARE record only (upload_type "software", license "mit"). The data record (which of the figures, source data and results families go to Zenodo, how to archive 32.6 GB in 32,070 files, the zipped F1 source-data CSV, the licence CC-BY 4.0 on it, any Zenodo file-count or size limit, UNVERIFIED) is not decided; it is close items 67 and 73. No second .zenodo.json is created.
- **Settled and open items.** See docs/ms13_close_items.md section T: 63 and 64 closed; 65, 68 and 71 closed in part; 66 moved to MS15b; 67, 69, 70, 72 to 76 open.
- **UNVERIFIED (new in sub-step 18).** The full legal text of CC-BY 4.0 (not in the repository; Claude Code has no internet), the field names and values of .zenodo.json against Zenodo's current schema, the CFF schema validity of CITATION.cff (no CFF validator is installed; it is checked as YAML only), whether PCJ accepts CC-BY 4.0 for figures and text, and whether Zenodo is a fit for a 32.6 GB data record.

## Release files written in sub-step 18 (MS15a part 1; DL-736, DL-737)

- LICENSE (MIT, 2026, Daniel Voldman; its body equals, after whitespace normalisation, the MIT text of the installed PyYAML 6.0.3 licence file; no copy from opensource.org was available: no internet). LICENSE-DATA.md (CC-BY 4.0 notice and link; the legal code is NOT reproduced, UNVERIFIED, to be added from creativecommons.org).
- CITATION.cff: cff-version 1.2.0, type software, title "mpr-gamma-surge" (the title of README.md; the plan gives a title only to the plan document), author with family and given names, email, affiliation and ORCID URL, license MIT, keywords "MPR neural mass model" and "dying-brain gamma surge" (words of the plan's title). No version, date-released, doi or repository-code (not yet assigned; comments in the file say so). Parsed as YAML only; the CFF schema was not checked (no validator, UNVERIFIED).
- .zenodo.json, every field UNVERIFIED against Zenodo's current schema (no internet): `title` "mpr-gamma-surge"; `upload_type` "software"; `creators` [{`name` "Voldman, Daniel", `affiliation` "Independent Researcher", `orcid` "0009-0005-3409-8944" (the bare identifier; whether Zenodo wants the bare identifier or the URL is UNVERIFIED)}]; `license` "mit" (the identifier form is UNVERIFIED). No `description`, `version`, `publication_date` or `keywords` (not sourced or not yet assigned). It describes the software record only; the data record is a separate decision (see above), and no second file exists.
- scripts/make_all.ps1: not run. From the plan: the file name and place (L1065), `-Stage replication` (L1272), clearing the Numba cache files *.nbi and *.nbc (L1200), the clean-tree check (L1064), the step names of Table 11.1 (MS2: A1, A2, S1, A0 rows; MS5: A4, S3; MS13: the figures). Inferred (marked in the file): the command of each step (from the docstrings of scripts/run_A0.py, run_A1.py, run_A2.py, run_A4.py, run_S3.py and fig_journal.py), the order, the stage value "figures", the clean-tree check on every stage. NOT written because the plan names no commands: the steps of MS3, MS4, MS6 to MS12 (the run lists scripts/run_ms8_list.py, run_ms9_list.py, run_ms10_list.py, run_ms11_list.py exist but were not read for this), the network cells of S3, the Julia steps (A5, A6), the recording of the cleared cache in provenance (a change under src/ would be needed; provenance.py has the field numba_cache_cleared, always null in the figure records), and `-Stage all` (it stops with an error). Line endings LF (the repository rule `* text=auto eol=lf`; the plan does not require CRLF); ASCII only. The PowerShell parse check was blocked by the safety classifier and not repeated (close item 80).
- README.md, CHANGELOG.md, docs/figure_map.md (generated by scripts/ms15a_write_figure_map.py; hashes copied from docs/ms13_journal_final_hashes.txt), docs/ms15_draft_flag_notes.md, tests/test_ms15a_release.py: see the files.
