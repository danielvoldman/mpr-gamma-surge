# MS13 sub-step plan (planning only; no ruling beyond DL-420 to DL-422, open choices M13-1 to M13-14)

**Status (13a, DL-419 to DL-424): planned. No figure built, nothing simulated, no list written, no tag made, nothing pushed. The only things run are read-only: the pre-checks, the readiness check (`scripts/ms13_inputs.py readiness`) and the load-time sample (`scripts/ms13_inputs.py timing`, section 10).** Written for: the reviewer who rules the open choices M13-1 to M13-14 below, and the author of the paper's figures and limitations section. Binding source: `docs/plan.md` (Table 11.1 rows MS13, MS14, MS15; section 8 and Table 8.1; section 6.6 and 6.7; section 7.2; section 10.1, 10.4, 10.7, 10.8; DL-045; Table 11.2; handoff (c), (d), (f)). Decisions go in `docs/decision_log.md`. This file holds no decision of its own except the three rulings that the 13a prompt gives and that are logged as DL-420 to DL-422. It changes nothing in the plan or in a frozen file and reopens no earlier ruling (the 41 D-items at defaults, the `src/mprsurge/` layout, MS0 to MS15, models M2/M3/M4/M3a/M3b, the surge classes, paths P1 to P5, controls NC1 to NC3, and all earlier rulings). Where the plan gives no number, the text states the criterion in words and leaves it for the reviewer; no value is invented. UNVERIFIED marks anything the plan does not state.

**Rulings carried in by the 13a prompt (logged as DL-420, DL-421, DL-422):**

1. The MS11 close (`docs/ms11_close.md`) is acknowledged as closed on paper, with claim limits MS11-C1 to MS11-C9 standing (DL-420).
2. MS12 was not run: G2 had no trigger (DL-133), G3 was not triggered (DL-261, DL-271), S14 and S15 were not run, FS6 is not produced. Claim limit **MS12-C1**: the surge result is stated for M3; no claim about robustness to a PING circuit (M4) or to adaptation (M3a/M3b); the RB8 M4/adaptation parts have no result (DL-421).
3. Tags, including any `fig-<ID>-v<k>`, are created only when the user says so (DL-422).

**MS13 row (Table 11.1):** "Figures F1–FS6 with provenance". Done when: "Each built from a clean tree and tagged". Unlocks: "MS14". Depends on MS11 (closed on paper, DL-418); MS12 is not run (MS12-C1). The row's "tagged" is read here under ruling 3: the tags are made only on the user's say-so.

## 1. Pre-checks at 13a (all pass)

| Check | Result |
|---|---|
| `docs/ms13_plan.md` from an earlier attempt | did not exist; `docs/ms11_plan.md` read for the layout |
| Working folder | `C:\dev\mpr-gamma-surge` (pwd) |
| Criteria-loader gate against tag `criteria-frozen` (dd8330c5eaacd63d21e7b7969430988d00862769) | PASS (`verify_frozen_criteria()` returned the tag, the commit and all four hashes) |
| Criteria file SHA-256 (LF text of the committed blob) | PASS c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05 |
| `configs/S13.yaml` | PASS 317db87e69afcb09111a33e78640869b3f588e64390d110655aaa3a7cff52388 |
| `configs/A4_grids.yaml` | PASS cf6a60bec781c6f7e53b7f92b747ff745fcc5dc4794c0b83768e0aa4a4e56401 |
| `configs/S5_cells.yaml` | PASS fe8590ce81bc8c537f9c92e2afbee80685aaaa52c757474912b243fe9ed38790 |
| Working tree clean (`git status --porcelain` empty); HEAD 128a53e | PASS |
| `docs/ms11_close.md` (WC / LF blob) | PASS f911c7b11ecfbdaeab9a106246afed87e554343ad8ca60e49bf4cc09482a192c / same |
| `docs/ms11_results.md` (WC / LF blob) | PASS 02b9fe9fc6d9b0caa8dd70298fae5f92d0201d7cfa525f095ba872d90d347ade / ce8739da6357adbdccd194b15c81534e0a7f767d0fbaa4938e8a353ea121096a (differ: CRLF in the working copy, DL-414) |
| `docs/ms11_evidence.md` (WC / LF blob) | PASS daf2820eb0cf94f4a844e45218f34f3c775fc0f0d8404d763f30d524c5515a92 / 7cc25fd51f7279144df3a5334cd7ba6c1a76dc892f9c241efed4150c1e719cb3 (differ: CRLF) |
| `docs/ms11_file_hashes.csv` (771 rows; WC / LF blob) | PASS c6571235b98369c89ac3a76045d6f98e83e09858ce12a2a1d2b71aafdc729d75 / same |
| `results/A11/a11_robustness.csv` (44 rows; git-ignored) | PASS b4f26b003d88f7d13dcb582786da32c1a2fe4e3b8de051ce1f494e81a1d8cffb |
| `docs/ms11_eval_rules.md` (WC / LF blob) | PASS 4b1a1a66dba379015f6c78f5f0431bd16cfdd81bb69b925b8857f4ccc55c48a5 / same |
| `configs/ms11/ms11_eval.yaml` (WC / LF blob) | PASS fcb439645473667b5bdd3d59f902b4e0498547af7403b79d5044a7d69d4209cf / same |
| MS11 result files | PASS 724 files, 1192.347 MB, digest cdafcc0831580ea4b9f7dfd8e095deb50e8b86db2974f556cf7ffe7d75637f53 (DL-383, DL-408) |
| `docs/ms10_close.md` | PASS 29b2cab8be79804c847908a0bbb0482ede1bde2f23a698ae42e59f957f2e2517 |
| `docs/ms10_file_hashes.csv` (436 files) | PASS 053c63916ab536a5a3672dd6c1a5c7797a79fa20e2b419840c1d94019949ca10 |
| 10f result-file table digest | PASS d1b98f05b1b147437ed19ef3dc4ee84c1dda61693c9e9cc3a9de41f4ba572a52 (321 files, every file hashes to its listed value, 0 mismatches) |
| `docs/ms9_close.md` | PASS 11f8b1eb2ab6d6860565020e9bc30a25d3038eea16f5a78e063b3d4a97cde3c2 |
| `docs/ms9_file_hashes.csv` (24,876 files) | PASS 53201f91af504ac10f7b441c8ede593c7a069007e8f6df5b1b0054c3c68e6a61 (the table's own hash and row count; the 24,876 listed files were not rehashed, as in DL-410) |
| Fast suite at the start | PASS: 916 passed, 24 deselected, 9 xfailed, 1 warning, 453.20 s, pytest exit code 0 (output redirected to a file, exit code echoed right after, no pipe) |

Stray processes: not looked for at 13a. Stray non-project files in the repository: none (tree clean at the start). Two commands in this session were run with the bare `python` (no file, nothing executed); every run used `.venv\Scripts\python.exe`.

## 2. Plan quantities quoted (quoted from `docs/plan.md`, nothing paraphrased)

### 2.1 Table 11.1, rows MS13, MS14 and MS15 (section 11)

> | **\#** | **Milestone and deliverables** | **Done when** | **Unlocks** |
> | --- | --- | --- | --- |
> | MS13 | Figures F1–FS6 with provenance | Each built from a clean tree and tagged | MS14 |
> | MS14 | Novelty re-check: Scholar (including cited-by checks on Xu 2023 and Borjigin 2013), PubMed, three slow-passage searches, Kalia journal version, eLife RP 104249, PMC12549018 \[R2, §6 rec. 6; RA, Recommendations\] | docs/search_log.md complete | G8; MS15 |
> | MS15 | Reproducibility release (D37); manuscript and submission checklist (below Table 11.2) | Checklist 10.8 passes on a clean machine; submission checklist complete | End |
>
> *Table 11.1. Milestones in build order (renamed MS0–MS15 in v0.4 so that milestone IDs do not collide with the model IDs M2–M4).*

### 2.2 Section 8: conventions, Nordlie table and script rule

> Sources: R5 (figure conventions and a six-figure plan), R6 (budget), R7 (captions). Handoff (f) fixes six main figures and six supplementary figures. R6 suggests about 15–20 pages and 5–6 figures \[R6, §2.5, §6 rec. 4\] \[single source: R6\], and R5 proposes six main figures \[R5, (c)\]. Conventions \[R5, SQ3\]:
>
> - shaded regions bounded by continued curves;
> - network symbols overlaid on mean-field results;
> - markers that link diagrams to traces;
> - full parameters and spectrogram settings in each caption.
>
> Each figure also gets a Nordlie parameter table \[R5, SQ6; R7, §2.5\] \[verified\].
>
> **Script rule.** Each figure has its own script, scripts/fig\_\<ID\>.py, which calls plotting.figures.make\_\<ID\>. Scripts read only results/ and never simulate. Each script writes the figure, \<ID\>\_provenance.json (input records, config hashes, seeds, commits) and \<ID\>\_params.csv. This follows the Sandve rules \[R5, SQ6; R7, §2.5\]. A figure built from a clean tree is tagged fig-\<ID\>-v\<k\>.

### 2.3 Table 8.1 (section 8), all rows, columns as in the plan

> | **ID** | **What it shows** | **From** | **Script** | **Result that would change the plan** |
> | --- | --- | --- | --- | --- |
> | F1 | Schematic and ramp protocol; mean-field and network r(t), v(t) on the headline path; 300-neuron raster; spectrogram of v | S8, S5, A8 | fig_F1.py | Network shows no surge → G4. Peak \< 25 Hz → re-select the headline via A6 (logged), or G2 |
> | F2 | One-parameter diagram along η̄ at ref_devalle, with cycle max/min, Hopf point and network symbols | A5, S4 | fig_F2.py | Subcritical Hopf or fold of cycles → abrupt onset and hysteresis \[R1, §3\]; add P5 to F4 |
> | F3 | (η̄, τ_d) and (η̄, Δ) planes: Hopf curves, frequency shading, 25 and 100 Hz contours, path arrows, markers | A4, A6 | fig_F3.py | 25 Hz contour outside the oscillatory region in range → G2 |
> | F4 | Delay, peak power (absolute and relative), f_pk and duration against ε; quasi-static line; up vs down ramp; start state; noise band; M2 ring | A7, A3, S5, S11 | fig_F4.py | Onsets miss the A4 entry–exit prediction on the runs inside the RB3(a) range, or the floored delay (D43) depends on the Heun step (RB6) → G6 |
> | F5 | Surge/no-surge maps with network symbols and subgrid agreement; F5c: metrics against N (CP7) | A9, S7, S8, S9 | fig_F5.py | A surge class in \< 3% of map-1 cells, or RB4 fails → G5; network disagrees in ≥ 2/4 cells → G4 |
> | F6 | Failure reasons; NC1–NC3 against T_ramp; P2 vs P3; P4a and P4b | A9, A10, S6, S12 | fig_F6.py | NC1 surge → G7; only P3 surges → H-drive framing (section 4.5) |
> | FS1 | M2 diagram (K1–K3), K4 and K5 traces, ring map | A1, A2, S1 | fig_FS1.py | G0 |
> | FS2 | M3 validation (K7–K11) | S3, A4–A6 | fig_FS2.py | G0 |
> | FS3 | Finite size, heterogeneity shape, noise | S9–S11 | fig_FS3.py | Shape changes class → claim limited to Lorentzian heterogeneity |
> | FS4 | Numerics | S13 | fig_FS4.py | Any RB6 failure → affected results unused |
> | FS5 | Classifier tests and sensitivity; frequency mapping | A8 | fig_FS5.py | Synthetic test fails → rework A8 |
> | FS6 | M4 or M3a/M3b | S14, S15 | fig_FS6.py | Only if G2 or G3 triggers |
>
> *Table 8.1. Planned figures. Every ID traces to handoff (c) or section 7.*

### 2.4 Related plan text

Section 6.6 (run output): "Each run also writes a Nordlie-format parameter table from its config (make_param_table), because parameters are easily omitted from text \[R7, Pauli 2018; R5\] \[verified\]. Figures come only from scripts reading stored results (Sandve rules) \[R5; R7\] \[verified\]." Section 6.7: "Sections 5 and 6 therefore feed six main figures (F1–F6) and supplementary figures FS1–FS6 (handoff f)."

Section 10.1 (repository layout entries): "plotting/ style.py, figures.py (make_F1 … make_FS6)"; "fig_F1.py … fig_FS6.py one per figure (12 files)"; "check_clean_tree.py blocks tagged builds from a dirty tree"; "make_all.ps1 pipeline in milestone order"; "docs/ decision_log.md, robustness_criteria.md, figure_map.md, search_log.md, plan.md (Markdown copy of this plan)"; "results/ NOT TRACKED (git-ignored)"; "figures/ NOT TRACKED (git-ignored)". "Drivers (simulate_mf.py, qif_network.py, run.py) only integrate. Analysis modules only analyse. Figure scripts only plot. Each result therefore has exactly one producer \[reasoned, not tested\]." Handoff (d): "src/mprsurge/plotting/figures.py make_F1 ... make_F6, make_FS1 ... make_FS6".

Section 10.4 (provenance), the list the figure records inherit: "the git commit, branch, tags and a dirty flag; versions of Python, packages, Julia and BifurcationKit; OS and CPU; SHA-256 of every input and output file; the hash of the criteria file." And "No sampled MPR paper reported seeds or versions \[R5, SQ6\] \[single source\]. Floating-point effects can change ODE results, so numerical settings are always recorded \[R7, §2.6\] \[single source\]." And: "Numba cache: make_all.ps1 clears the Numba cache files (\*.nbi, \*.nbc) before every tagged run and records this in provenance."

Section 10.7 (tags): "All annotated: env-v1; tolerances-frozen (end of MS1, with the replication.yaml SHA-256); replication-pass (G0); criteria-frozen (MS7, with the criteria SHA-256); fig-\<ID\>-v\<k\>, for each figure build (inputs and hashes in the message); release-v1.0." The plan's example: `python scripts\fig_F3.py` then `git tag -a fig-F3-v1 -m "F3 from A4 <hash12>, A6 <hash12>"; git push origin main --tags`. Under ruling 3 (DL-422) no tag is made and nothing is pushed unless the user says so. Existing tags: criteria-frozen, env-v1, replication-pass, tolerances-frozen.

Section 10.8 items touching figures: "Rebuild one figure from the archive; metrics match within the RB6 tolerances, not bit for bit \[R7, §2.6\]." "Every provenance file names the release commit and none is marked DRAFT." "Nordlie tables, seeds, versions, OS and CPU are present for every figure and run \[R5, recommendations\]." Submission checklist (MS15): "Nordlie parameter tables, one per experiment or figure; every caption states the parameter regime and the take-home message \[R7, §8(d)\]." and "Code archived with a version identifier, parameter files, integrator and tolerances; failure regimes reported alongside surge regimes \[R7, §8(d)\]."

### 2.5 DL-045 (decision log; Table C.1)

> DL-045 | Figure production | One script per figure, reading results only; tag per build | — (default adopted, Default from: Part 2)

### 2.6 Section 7.2: failed checks and "Failure regimes get equal weight"

> **Main text versus appendix.** Main text: RB1, RB2 (noise robustness, a main result from v0.4: the noise band on F4 and the noisy-subgrid agreement on F5), RB3, RB5 and RB7, and RB4 as a single sentence. Appendix: RB6, RB8, RB9 and RB10. This follows R5, which places ramp-rate and quasi-static results in the main text and numerics in the appendix \[R5, recommendations\], and RA, which recommends noise robustness as a main result \[RA, Recommendations\]. Failure regimes get equal weight \[R7, §2.7\]. The Hopf location (A4) and the A7 entry–exit delay prediction, checked against S4 and S8, supply the analytic-versus-network result R6 asks for \[R6, §6 rec. 4\].
>
> **Evaluation.** Step A11 (scripts/run_A11.py) reads the frozen criteria and writes results/A11/a11_robustness.csv: value, threshold, pass or fail, and the input commits. Failed checks are reported, not dropped, because MNA bars hiding known issues \[R6, §2.1; R7, §2.7\] \[verified\].

CP7 (Table 12.1): "Finite size appears only in FS3 | R5 puts network validation against N in main-text Fig. 5 and calls it reviewer-relevant | … | Add panel F5c and keep FS3 (D39)."

### 2.7 Table 11.2, the gate rows the Table 8.1 triggers name

> | G0 Replication (MS2, MS5) | K1–K5 and K7–K9 pass (K4-net non-blocking until the M2 network coupling is sourced; K8 without its frequency band; K9 as in Table 7.1: if its maximum differs from 0.1453, only the ratio scaling across η̄ = 1, 2, 4 blocks) | Still failing after two debugging rounds → stop new work. Check the equations against the Ceni and Devalle forms \[R1, §2.1\], the sign convention (C3) and the units |
> | G2 No gamma transient (Part 1) | As section 4.3 | Move to M4 once its equations come from MPR App. E and Segneri \[R1, §2.3\], or from Dumont and Gutkin 2019 if D42 chooses that form (section 7.3). If M4 also fails, stop simulating and report a negative result, with the frequency maps as evidence \[reasoned, not tested\] |
> | G4 Network vs mean field (Part 1, extended) | RB1 passes | Network misses the surge at N = 10⁴ and 3×10⁴ → report a finite-size limit (Part 1). Disagreement in ≥ 2/4 cells → rerun RB6. Note the known caveats: OA attraction with synaptic kinetics is unproven, and shot noise causes metastability \[R1, §2.6\]. Report the affected results as mean-field-only |
> | G5 Fine-tuning | A surge class (Table 2.1) in ≥ 3% of map-1 cells and RB4 passes | Surge only at one tuned point → no generic claim. Measure the window width; test whether P3, P4a or P4b widens it; report "narrow window" plus the failure map as the result \[R4, §6 Q6; R7, §2.7\] |
> | G6 Ramp artefact | RB3(a) (on the runs inside its range; section 5.2, A7), RB3(b) and RB6 pass at the headline point; RB3(d) and RB5 are evaluated and reported | Class or floored delay depends on the solver (method or rtol; the Heun step for floored runs) → fix the numerics. Dependence on profile or δ₀ is slow-passage physics (section 4.4; RB3(d); RB5): reported, not fixed. Surge only outside 56–316 s → limit the claim |
> | G7 Negative control | NC1 has no surge class at every T_ramp | Any NC1 surge → review A8 before any result is used |
>
> *Table 11.2. Stop-or-continue gates. … What each gate blocks: G0 blocks S5 onward; G1 sets the model for MS5 onward; G2 and G3 open MS12; G5–G7 limit or stop the claims that depend on them; G4 and G8 are report-only for the run order (G4 limits claims to the mean field; G8 shapes the manuscript at MS15).*

## 3. State at the start of MS13

| Item | State |
|---|---|
| Freeze | Annotated tag `criteria-frozen` (commit dd8330c5eaacd63d21e7b7969430988d00862769), local only; all four hashes verified at 13a (section 1). No frozen file changes at 13a. |
| MS11 close | `docs/ms11_close.md` (DL-418), acknowledged by DL-420. RB2 FAIL at σ (7 of 10), RB6 network f_pk FAIL, RB9(b) headline FAIL (4.391 Hz against 0.5 Hz); RB5 δ₀, RB9(a), RB9(c), RB10 and the window line PASS; the rest REPORTED. Claim limits MS11-C1 to MS11-C9. |
| MS12 | Not run (DL-421). G2 no trigger (DL-133); G3 not triggered (DL-261, DL-271); S14, S15 not run; FS6 not produced. MS12-C1. |
| Earlier closes | MS10: RB1 FAIL, σ check NOT INSIDE, RB8 heterogeneity part NOT EVALUABLE, G4 triggered by consequence (2) (DL-323), claim limits G4-C1 to G4-C6 (DL-325). MS9: G5 passed (DL-258), G7 NOT PASSED (DL-228, DL-229), G3 not triggered, RB4 PASS (DL-235), RB2 / D24 FAILED (DL-242). MS8: G6 PASSED WITH DEPARTURES, G6-D1 to G6-D3 (DL-208). MS7: four gate departures (DL-163). |
| Machine | Ryzen 5 5600, 16 GB, Windows 11 (build 10.0.26300), CPU only, 12 logical processors; Python 3.11 in `.venv`; matplotlib 3.11.2, pandas 3.0.6, pyarrow 26.0.0, numpy 2.4.6 (lock file). |
| Figure code that exists | **None.** `src/mprsurge/plotting/` holds only `__init__.py`. There is no `plotting/style.py`, no `plotting/figures.py`, no `scripts/fig_*.py` (12 planned), no `scripts/check_clean_tree.py`, no `scripts/make_all.ps1`, no `docs/figure_map.md`, no `figures/` folder. |
| Code that exists and can be reused | `params.make_param_table` and `params.param_table_markdown` (Nordlie-style table from a resolved config; DL-059 states it "does not claim Nordlie sectioning"); every run already writes `<run>_params.md`; `provenance.git_info()` (commit, branch, tags, dirty flag), `provenance.environment_info()` (Python, packages, Julia, BifurcationKit, OS, CPU), `provenance.sha256_file`, `provenance.atomic_write_*`; `criteria.verify_frozen_criteria()` (tag, commit, hashes, clean-tree step 5); `scripts/hash_ms*_results.py` (hash-table convention). The stored run JSON already carries: `git`, `python`, `packages`, `julia`, `os`, `cpu`, `inputs`, `outputs` (SHA-256), `criteria_sha256`, `numba_cache_cleared`, `seed` (root_seed, spawn_key), `solver`, `flags`, `wall_time_s`. |
| Tags | criteria-frozen, env-v1, replication-pass, tolerances-frozen. No MS-level tag, no `fig-*` tag. |

## 4. Figure inventory

Legend for every entry. **Inputs** are the stored files the figure needs (the plan's "From" column and handoff (c)/(f)); the DL numbers name the entries that produced or judged them. **Code** says what exists. **Readiness** is the result of `scripts/ms13_inputs.py readiness`, which OPENED every listed file (json parsed; npz: zip directory read, `testzip`, required arrays checked by name; parquet and csv read); "ready" means every listed file was found, opened and matched the record count the plan's Table 6.2 row implies; it does **not** mean the series were read in full (the timing sample reads them in full, section 10) or that any figure code exists. **Trigger** is the Table 8.1 "result that would change the plan" and whether it occurred, read from the decision log and the stored results; "not found in the log" means exactly that, nothing is inferred.

Common to every figure: **Code** — `scripts/fig_<ID>.py`, `plotting.figures.make_<ID>` and `plotting/style.py` do not exist; no figure has been built. **Nordlie table** — one per figure is required (section 2.2); none exists at figure level (the per-run `*_params.md` files exist).

### F1. Schematic and ramp protocol; mean-field and network r(t), v(t) on the headline path; 300-neuron raster; spectrogram of v
- **Inputs:** S5 headline mean-field record `results/S5/ramp/S5ramp/S5ramp_0000_240de3ef73be.{json,npz}` (P2, ref_devalle, T_ramp 120 s; `docs/ms8_close.md`); S8 network headline `results/S8/S8_head/` (6 records: T_ramp 10 and 120 s × 3 seeds, N = 1e4, each npz with `raster_t_ms`, `raster_neuron`, `raster_j` (300 neurons); MS10 10f, DL-317); S8 mean-field companion `results/S8/mf/S8_mf_head60/`; A8 `results/A8/a8_aref.json` and `a8_sensitivity.csv`; spectrogram settings from the frozen criteria file (`configs/robustness_criteria.yaml`, tag `criteria-frozen`). The schematic and ramp protocol are drawn from the path definitions (section 4.4, `ramps.py` breakpoints), not from a result file.
- **Code:** none. The raster is stored for 300 neurons only (the plan's memory rule, section 10.4).
- **Readiness: ready.** 1 + 6 + 1 + 3 files opened (counts match S8: 2 T_ramp × 3 seeds = 6).
- **Trigger 1, "Network shows no surge → G4":** not in that literal form (DL-323 consequence (1): the network does not miss the surge at N = 1e4 and 3e4; S8 headline 2 of 6 records are a surge class). The broader G4 trigger **occurred**: RB1 FAIL, headline 10 s FAIL, 120 s FAIL, 3 of 4 cells disagree, G4 triggered through consequence (2), report-only for the run order (DL-319, DL-320, DL-323, DL-325 G4-C1 to G4-C6; `docs/ms10_close.md`). **Trigger 2, "Peak < 25 Hz":** not found in the log; the headline spectral peak is 49.0 Hz (A11 row 39, `docs/ms11_close.md` (c)), and DL-133 records no G2 trigger.

### F2. One-parameter diagram along η̄ at ref_devalle, with cycle max/min, Hopf point and network symbols
- **Inputs:** A5 `results/A5/a5_cycles.npz` (devalle branch: `devalle_param`, `devalle_vmax`, `devalle_vmin`, `devalle_stable`, fixed-point arrays; DL-126), `results/A5/julia/a5.json`; S4 mean-field sweep `results/S4/devalle/` (61 steps up then down) and network sweep `results/S4/net/` (15 steps; DL-127, DL-128).
- **Code:** none.
- **Readiness: ready.** 4 inputs opened.
- **Trigger "Subcritical Hopf or fold of cycles":** **did not occur.** DL-126: "Also SuperCritical at ref_devalle (no fold, stable, to eta_bar 8, no second Hopf found on 0 to 8)"; supercritical at ref_ceni too. The K7 amplitude-half residual miss (2.42 percent against 2 percent) is a REPORTED FAILURE of a replication row, not a criticality finding (DL-129, DL-130). Whether P5 is added to F4 follows from this: P5 is already in S5 and A7 (section F4).

### F3. (η̄, τ_d) and (η̄, Δ) planes: Hopf curves, frequency shading, 25 and 100 Hz contours, path arrows, markers
- **Inputs:** A4 `results/A4/a4_hopf_curves.npz` (`curve_tau_d_*`, `curve_Delta_*`, `curve_J_*`; DL-115); A6 `results/A6/a6_freq_map.npz` and `a6_summary.json` (37 slices, `po_frequency_hz`; DL-131, DL-132).
- **Code:** none.
- **Readiness: ready.** 3 files opened.
- **Trigger "25 Hz contour outside the oscillatory region in range → G2":** **did not occur at the headline**: DL-133 (owner ruling): "So no G2 trigger fires: the project stays on M3"; (b) is met for the P1/P2 path at ref_devalle, and "the start states of the other 31 A6 slices were not evaluated" (DL-133). So for the other slices of F3 the check was not made (UNVERIFIED either way). RB9 lists F3 in its "Where" column (Table 7.2): the RB9(b) FAIL and RB9(c) PASS are in `docs/ms11_close.md` (c).

### F4. Delay, peak power (absolute and relative), f_pk and duration against ε; quasi-static line; up vs down ramp; start state; noise band; M2 ring
- **Inputs:** A7 `results/A7/a7_ramp_metrics.parquet` (360 rows); A3 `results/A3/a3_sn_ramp.parquet` (13 rows, M2); A2 ring map (M2 ring); A4 entry–exit prediction `results/A4/a4_rb3a_range.csv` (1,260 rows) and `a4_rb3a_summary.json`; S5 ramp families `results/S5/ramp/` (105 records: P1, P2, P5 × linear, sigmoid × 13 T_ramp, start-distance family, headline); S5 baseline-only mode-N runs `results/S5/baseline/S5base_*` (1,226 records: the headline cell, 900 and 325 map cells; the noise baseline); S11 `results/S11/S11/` (120 records) and `S11_ctrl` (30 records, DL-251, post hoc); `results/A11/a11_robustness.csv` rows 27 to 31 for the noise band.
- **Code:** none. The quasi-static line is computed by A4/A5 (stored), not by the figure script.
- **Readiness: ready.** 9 inputs opened; counts match (S11 120 and 30; S5 baseline 1 + 900 + 325).
- **Trigger, "Onsets miss the A4 entry–exit prediction on the runs inside the RB3(a) range, or the floored delay (D43) depends on the Heun step (RB6) → G6":** first part **occurred**: 0 of 6 testable in-range runs within one A4 step (G6-D1); G6 was ruled PASSED WITH DEPARTURES, claim limits G6-D1 to G6-D3 (DL-208, DL-209; `docs/ms8_close.md`). Second part **did not occur**: the floored delay does not depend on the Heun step at the 1 ms output grid (DL-190; `docs/ms8_close.md` line 7). The solver dependence of the noise-free onset (DOP853 58.698 s, Radau 58.879 s) is G6-D2 (DL-189, DL-208). In addition the noise band on F4 rests on RB2 at σ, which FAILED (7 of 10; MS11-C1, DL-394) — not a Table 8.1 trigger, listed in section 6.

### F5. Surge/no-surge maps with network symbols and subgrid agreement; F5c: metrics against N (CP7)
- **Inputs:** A9 `results/A9/a9_regime_map.parquet` and `a9_regime_map_v2.parquet` (1,226 rows: map 1 = 900, map 2 = 325, plus the headline row), `a9_subgrid_agreement.parquet` (225 rows); S7 `results/S7/S7_map1` (900), `S7_map2` (325), `S7_subgrid` (2,250); S8 cells `results/S8/S8_cells/` (4 map cells × 3 seeds = 12 records); S9 `results/S9/S9/` (4 N × 10 seeds = 40 records) and `S9_ctrl` (12). F5c uses S9 (N = 1e3, 3e3, 1e4, 3e4; CP7, D39) and the S8/S9 N = 1e4 and 3e4 results of MS10 (DL-320, DL-321).
- **Code:** none.
- **Readiness: ready.** 9 inputs opened; counts match the Table 6.2 rows. The three S7 families are 15.9 GB (section 10); the A9 table carries the classes, so which S7 series the figure must read is open choice M13-12.
- **Trigger 1, "A surge class in < 3% of map-1 cells, or RB4 fails → G5":** **did not occur**: D-tr in 760 of 900 map-1 cells (84.4%; threshold 27 of 900), RB4 PASS (0 of 14 changed; 64 of 64 unchanged) (DL-235, DL-237, DL-258; `docs/ms9_close.md` (b)). **Trigger 2, "network disagrees in ≥ 2/4 cells → G4":** **occurred**: 3 of 4 cells disagree, G4 triggered (DL-323), G4-C1 (1 of 4 agree) (DL-325). Also relevant to F5: D24 / RB2 subgrid agreement FAILED, 97 of 225 (43.1%) (DL-242).

### F6. Failure reasons; NC1–NC3 against T_ramp; P2 vs P3; P4a and P4b
- **Inputs:** A9 `results/A9/a9_regime_map_v2.parquet` (failure labels a to h, DL-243, DL-244, DL-249, DL-265); A10 `results/A10/a10_controls.csv` (58 rows); A7 `a7_s6_metrics.parquet` (24 rows); S6 `results/S6/S6_P3` (12), `S6_P4a` (4), `S6_P4b` (4); S12 NC1 (13), NC1 at 5 map cells (5), NC1 network (1), NC2 (13), NC3 (13).
- **Code:** none.
- **Readiness: ready.** 11 inputs opened; counts match.
- **Trigger 1, "NC1 surge → G7":** **occurred**: the NC1 network run (N = 1e4, mode N, 120 s, 1 seed) is class S+ (provisional); the 18 mean-field NC1 runs are D-none; G7 NOT PASSED, A8 and every frozen criterion unchanged (DL-220, DL-221, DL-228; claim limits DL-229, DL-230). **Trigger 2, "only P3 surges → H-drive framing":** **did not occur**: the 24 S6 rows (P3, P4a, P4b) are all D-tr (DL-235; `docs/ms9_close.md` (b)); NC2 is D-tr at 13 of 13 T_ramp with I = 1 and with I = 0.

### FS1. M2 diagram (K1–K3), K4 and K5 traces, ring map
- **Inputs:** A1 `results/A1/a1_fixedpoints_2d.npz` (DL-086); A2 `results/A2/a2_ring_map.npz` (DL-089); S1 `results/S1/` (4 records: K4 step, K5 sinusoid; DL-088); A0 `results/A0/a0_replication.csv` (5 rows, DL-091).
- **Code:** none.
- **Readiness: ready.** 4 inputs opened.
- **Trigger "G0":** not triggered as a stop: G0 part 1 K1–K3, K4-MF, K5 pass (`docs/ms2_gate_report.md`, DL-091, DL-092); G0 part 2 passed with departures at MS5 (DL-123). Open: K5 is our own reading, UNVERIFIED (DL-064, DL-082); K4-net is unsourced (MC-03). G1 judged on S2 alone, move from M2 to M3 (DL-111).

### FS2. M3 validation (K7–K11)
- **Inputs:** S3 `results/S3/` mean-field (ceni 3, devalle 2) and network (ceni 3, devalle 2, K8 1) records and the two summaries `s3_mf_summary.json`, `s3_net_summary.json` (DL-116, DL-119); A4 Hopf curves (K9, K10, K11 arrays); A5 cycles; A6 frequency map.
- **Code:** none.
- **Readiness: ready.** 10 inputs opened.
- **Trigger "G0":** not triggered as a stop (DL-123, MS5 gate passed with departures). Facts that must be shown in the figure's caption or table, not decided here: the K7 Hopf value was not reproduced at 1d (DL-074; departure DL-076, DL-079); the K7 amplitude-half residual miss 2.42 percent against 2 percent stays a REPORTED FAILURE (DL-129); K10 single-source claim UNVERIFIED; K4-net unsourced.

### FS3. Finite size, heterogeneity shape, noise
- **Inputs:** S9 (40 records; 12 controls), S10 `results/S10/S10` (9 records: Lorentzian, Gaussian, uniform × 3 seeds) and `S10_ctrl` (6), S11 (120) and `S11_ctrl` (30).
- **Code:** none.
- **Readiness: ready.** 5 inputs opened; counts match.
- **Trigger "Shape changes class → claim limited to Lorentzian heterogeneity":** **not evaluable as worded**: RB8 heterogeneity part NOT EVALUABLE — Lorentzian seeds S-sus, S-abs, S-sus (no single correspondence class), Gaussian S-abs × 3, uniform S-abs × 3 (DL-322); G4-C5 "No claim about heterogeneity-shape robustness" (DL-325). The limit the plan names (claim limited to Lorentzian) is the same in effect; whether it is adopted in those words is the reviewer's.

### FS4. Numerics
- **Inputs:** S13 `results/S13/` MS8 part (δ₀ 2, rtol 2, Radau 1, floor levels 0, 1, 2 with 40 records each) and MS11 part (68 mean-field records: δ₀, floor at 10 and 316.2278 s, rtol; 18 network records: dt ladder and V_p); `results/A11/a11_robustness.csv` rows for RB5, RB6.
- **Code:** none.
- **Readiness: ready.** 8 inputs opened. (The first draft of the check mis-pointed at the MS11 folder and at `cell_list.json`; both were errors of the check, corrected before the numbers above; the record is DL-423.)
- **Trigger "Any RB6 failure → affected results unused":** **occurred**: RB6 network f_pk FAIL under both readings (A11 row 36; DL-387, DL-394 MS11-C2); RB6 solver clause: DOP853 against Radau onset 181 ms against 1 ms (DL-189; G6-D2). What "affected results unused" means for the figures that use network f_pk is not decided here (section 7, M13-9). Not a failure: RB6 floored delay against the Heun step (DL-190); RB6 rtol rows REPORTED (rows 34, 35).

### FS5. Classifier tests and sensitivity; frequency mapping
- **Inputs:** A8 `results/A8/a8_sensitivity.csv` (1,880 rows), `A8/baseline/a8_baseline_summary.json`, `A8/sensitivity/a8_reachability.csv`; the synthetic tests `tests/test_surge_metrics.py` (read as a list of cases, never run by the figure script); A11 rows for RB9 and RB10 and `rb9a_unit_level.json`; the "frequency mapping" panel has no input named in Table 8.1 beyond "A8": the reading that it uses A6 and the A11 RB9 rows is UNVERIFIED (M13-14).
- **Code:** none. `analysis/a8_sensitivity.py` and `analysis/surge_metrics.py` exist (analysis only).
- **Readiness: ready** for the stored files listed; the panel inputs are an UNVERIFIED reading.
- **Trigger "Synthetic test fails → rework A8":** **occurred in a reduced form and was ruled not to rework A8**: the plan's D8 estimator fails 2 of the plan's 8 A8 ring items (gate departure 1, DL-161, DL-163); the class-level cases are strict xfail (9 xfailed in the suite); the D8 call stays provisional; A8 left unchanged by the G7 ruling (DL-228). The four departures are listed in DL-163.

### FS6. M4 or M3a/M3b
- **NOT PRODUCED.** S14 and S15 were not run; MS12 did not open (DL-421); claim limit **MS12-C1**. The plan's trigger, "Only if G2 or G3 triggers", did not occur (DL-133; DL-261, DL-271). `fig_FS6.py` and `make_FS6` are not built. Whether the figure inventory in the paper then has five supplementary figures is a statement for the reviewer (M13-14).

### Readiness table (one line per figure; output of `scripts/ms13_inputs.py readiness`, section 10 holds the load times)

| Figure | Readiness | What is missing |
|---|---|---|
| F1 | ready | no figure code; no schematic source (drawn from path definitions) |
| F2 | ready | no figure code |
| F3 | ready | no figure code |
| F4 | ready | no figure code |
| F5 | ready | no figure code |
| F6 | ready | no figure code |
| FS1 | ready | no figure code |
| FS2 | ready | no figure code |
| FS3 | ready | no figure code |
| FS4 | ready | no figure code |
| FS5 | ready (stored files) | no figure code; the "frequency mapping" panel input is an UNVERIFIED reading |
| FS6 | NOT PRODUCED (MS12-C1) | S14, S15 inputs do not exist and are not to be made |

All 11 producible figures have every stored input they need present and readable. The missing items are all code: 12 script slots (11 needed), `plotting/style.py`, `plotting/figures.py`, `scripts/check_clean_tree.py`, `scripts/make_all.ps1`, the figure provenance writer, the figure-level Nordlie table writer, and `docs/figure_map.md` (named in the plan's layout, absent).

## 5. Claim-limit placement table (LISTED ONLY; nothing decided)

The right-hand column lists the figures whose inputs (section 4) contain the result the limit applies to, so a statement made in or beside that figure falls under the limit. "Where it must be visible" (caption, panel, table) is the reviewer's choice (M13-5); this table does not make it. The limits are quoted from `docs/ms11_close.md` (h), `docs/ms9_close.md` (e), `docs/ms10_close.md`, DL-163, DL-325 and DL-421.

| Claim limit (source) | One-line content | Figures whose inputs it touches |
|---|---|---|
| MS9 (e)-1, G7 (DL-229, DL-230) | network-record surge classes at N = 1e4 are not evidence of a ramp-driven surge (control flagged 10 of 10 seeds; ramp 10 of 10) | F1, F5 (network symbols, F5c), F6, FS3 |
| MS9 (e)-2, D24 (DL-242, DL-250) | no claim that the regime map is robust to noise; S-rel not counted as ramp evidence in mode N | F4 (noise band), F5 (noisy subgrid), FS3 |
| MS9 (e)-3, A9 label (c) (DL-270) | label (c) is a flag, not a demonstrated cause | F5, F6 |
| MS9 (e)-4, A9 check (DL-269) | the check covers 1,056 of 1,057 surge-class cells | F5, F6 |
| MS9 (e)-5, D8 provisional; A_ref (a) 2.176222; G6-D1 to G6-D3 apply | every D8-dependent class is provisional | F1, F4, F5, F6, FS3, FS4, FS5 |
| MS9 (e)-6, D31 boundary and J_exit,static (DL-254, DL-263) | the boundary definition and the P3/P4 exit extension are ours | F5 (boundary), F6 (P3, P4a, P4b) |
| MS9 (e)-7 | P3 cost 1.57 × the headline; Defender exclusion user-reported only | none visible in a figure (methods or provenance note) |
| MS9 (e)-8 (DL-267) | the independent recomputation shares the frozen classifier and the wording of D24, P-1, D31 | none visible in a figure (methods) |
| G6-D1 (DL-208) | no claim that onset follows the A4 entry–exit prediction; RB3(a) not validated (0 of 6 testable in-range runs within one A4 step) | F4, F3 (if path arrows carry predicted entries; UNVERIFIED) |
| G6-D2 (DL-208) | headline delay taken from D43-floored runs; noise-free onset solver-dependent (DOP853 58.698 s, Radau 58.879 s) | F4, FS4 |
| G6-D3 (DL-208) | RB3(b) reported under both onset readings | F4, FS4 |
| DL-163 departure 1 | D8: the plan estimator fails 2 of 8 A8 ring items; classes provisional | F1, F4, F5, F6, FS5 |
| DL-163 departure 2 | zero baseline, including noise-free inputs | F4, F5, F6, FS5 |
| DL-163 departure 3 | RB3(a) not judged at the headline (coverage 0 to 2 of 13 T_ramp) | F4 |
| DL-163 departure 4 | pure trend plus noise at W = 0.2 s; short-window false surges (306, 400, 172, 24 of 500 at W = 0.2, 0.333, 0.593, 1.054 s) | F4 (T_ramp 10 s, 30 s), FS5, FS3 |
| G4-C1 (DL-325) | network at N = 1e4 and 3e4 does not reproduce MF classes (0 of 3 seeds at T_ramp 10 and 120 s; 1 of 4 cells) | F1, F5, FS3 |
| G4-C2 | surge result stated for the mean field only; no claim of robustness to finite-size fluctuations | F1, F5, FS3 |
| G4-C3 | no-ramp network controls are classified into surge classes | F1, F5, F6, FS3 |
| G4-C4 | σ = 0.0624 checked and not confirmed; noisy MF labelled | F4, F5 (noisy subgrid), FS3 |
| G4-C5 | no claim about heterogeneity-shape robustness (RB8 not evaluable) | FS3 |
| G4-C6 | the RB6 rerun was read as the network part of S13 (UNVERIFIED reading) | FS4 |
| MS11-C1 | headline class kept in 7 of 10 seeds at σ (needs 8); controls reach 7 of 10 with no ramp | F4 (noise band), F5, FS3 |
| MS11-C2 | no claim of f_pk or class agreement between network and MF (RB6 network f_pk FAIL) | F1, F5, FS3, FS4 |
| MS11-C3 | spectral and cycle frequency differ by 4.39 Hz at the headline (RB9(b) FAIL); peak frequencies are the classifier's spectral peaks | F1, F4 (f_pk), F5, FS5 |
| MS11-C4 | RB9(a) rests on a unit-level test only | FS5 |
| MS11-C5 | DOP853 against Radau covers T_ramp 120 s only | FS4 |
| MS11-C6 (reworded, DL-402) | floor-level direction of RB3(b) unresolved at 10 s and 316 s | F4, FS4 |
| MS11-C7 | all earlier failures and limits stand (RB1 FAIL, G7 not passed, D24 failed, G4-C1 to G4-C6, MS9 limits) | every figure |
| MS11-C8 (DL-406) | RB6 network reading (ii) f_pk for episodes shorter than W uses a method not in the frozen rules | FS4 |
| MS11-C9 (DL-412) | cycle-frequency estimator in RB9(b) not named in the rules; 51 against 45 of 760 cells | FS5 |
| MS12-C1 (DL-421) | surge result stated for M3; no claim about M4 or M3a/M3b; RB8 M4/adaptation parts have no result | every figure whose caption states the result (F1 to F6), FS6 (not produced) |
| RB1 FAIL (DL-319, DL-320) | headline 10 s FAIL, 120 s FAIL, cells 1 of 4 | F1, F5 |
| RB2 FAIL (DL-387, DL-242) | 7 of 10 at σ; noisy subgrid 97 of 225 | F4, F5, FS3 |
| RB6 FAIL (DL-387) | network f_pk both readings | FS4 |
| RB9(b) FAIL (DL-388) | 4.391 Hz against 0.5 Hz | FS5, F3 |
| G7 not passed (DL-228) | NC1 network S+ | F6, F1 |
| D24 failed (DL-242) | subgrid agreement 43.1 percent on raw classes | F5, F4, FS3 |

## 6. Open choices (none chosen; each with options and a plan-grounded recommendation)

Recommendations are UNVERIFIED where the plan is silent and say so. Where the plan gives no number, the criterion is stated in words.

**M13-1. File formats.** The plan names the figure, `<ID>_provenance.json` and `<ID>_params.csv` and no image format (UNVERIFIED). Options: (a) vector PDF plus a PNG preview; (b) SVG; (c) PNG only. A raster with a 300-neuron raster of up to ~1e6 spikes can be heavy as a vector. *Recommendation:* (a) PDF for the paper, PNG for review, same script and same provenance file; the raster drawn as a rasterised layer inside the PDF; the format list is written in the provenance file. No resolution number is given by the plan; left for the reviewer.

**M13-2. Colours.** Plan: "markers that link diagrams to traces" and "network symbols overlaid on mean-field results"; no palette (UNVERIFIED). Criterion in words: colour-blind-safe; the same colour for the same class or path in every figure (surge classes S+, S-rel, S-abs, S-sus, NS, D-tr, D-sus, D-none; paths P1 to P5, NC1 to NC3; mean field against network against noise). Options: (a) one fixed table in `plotting/style.py`, keyed by class and path, plus marker shapes so that no meaning rests on colour alone; (b) per-figure palettes. *Recommendation:* (a). The specific palette is the reviewer's; no hex values are proposed here.

**M13-3. How failures and failure regimes are shown (equal weight, section 2.6).** Options: (a) every map, table and sweep draws failure cells and non-surge regimes with the same area, outline and legend weight as surge cells, and A9's failure labels (a to h) get their own panel in F6; (b) failures in a supplement table only; (c) failed checks as a "claim limits" panel in each figure. *Recommendation:* (a), plus a figure-level "checks" strip listing the FAIL rows that touch the figure (section 5), because Section 7.2 says "Failure regimes get equal weight" and "Failed checks are reported, not dropped". The figure scripts read A11 for the strip; they do not recompute it. Whether the strip is drawn on the figure or in the caption is M13-5.

**M13-4. How network disagreement with the mean field is shown (F1, F4, F5, G4).** The record is: RB1 FAIL, 3 of 4 cells disagree, G4-C1 (1 of 4 agree), headline 0 of 3 seeds at each T_ramp. Options: (a) network symbols are drawn at the cells and times where they exist, in a different marker for "agrees with the MF class" and "does not", with the count in the legend; (b) network symbols drawn only where they agree; (c) a separate panel. The plan's convention is "network symbols overlaid on mean-field results". *Recommendation:* (a); never (b). Disagreeing symbols stay on the map, labelled by their class. The network spectrogram and raster in F1 are drawn beside the MF trace for all 6 S8 headline records, not only the matching ones (UNVERIFIED how many seeds are drawn; the plan says "network r(t), v(t)" without a seed count).

**M13-5. Caption template.** Plan: "full parameters and spectrogram settings in each caption" and the checklist "every caption states the parameter regime and the take-home message \[R7, §8(d)\]". Proposed template (UNVERIFIED as a layout): (1) one sentence take-home message; (2) parameter regime (model M3, reference point, path, profile, T_ramp, N where used, σ and its label "checked, not confirmed" where used); (3) spectrogram settings (band, window W and rule, step, taper, from the frozen criteria file; never retyped by hand); (4) what the symbols and markers mean; (5) claim limits that apply, by ID, from section 5 (which IDs print in the caption and which stay in the checks strip is the reviewer's); (6) provenance pointer (the `<ID>_provenance.json` hash12 and the tag if one exists). *Recommendation:* the caption text is generated by `make_<ID>` from the same config values that the provenance file records, so that a caption cannot disagree with its parameter table. The length limit of a caption is the journal's, not the plan's (UNVERIFIED).

**M13-6. Nordlie parameter tables.** The plan requires one per figure and the existing per-run `*_params.md` is "a plain table ... [that] does not claim Nordlie sectioning" (DL-059). Options: (a) `plotting/` builds a Nordlie-sectioned table (model, populations, connectivity, neuron model, input, measurement) from the configs of the figure's input records, written as `<ID>_params.csv` (the plan's name) and rendered as a Markdown/LaTeX table for the manuscript; (b) reuse `make_param_table` rows unchanged. *Recommendation:* (a) in two stages: rows from `make_param_table` of every input record, deduplicated into constant and varied columns, then the Nordlie sectioning as a fixed mapping from keys to sections in `plotting/style.py` or a small `params` helper (the mapping is ours, UNVERIFIED). `<ID>_params.csv` links to the provenance by listing the source run ID and config hash12 per row.

**M13-7. Build order.** The plan gives no order within MS13. Options: (a) by figure number F1 to F6, FS1 to FS5; (b) cheapest inputs first (F3, F2, FS1, FS2, FS5, FS4, FS3, F6, F4, F1, F5) so that style, provenance and the clean-tree check are exercised on small inputs; (c) by decreasing journal importance. *Recommendation:* (b) for 13b to 13e, with `style.py`, the provenance writer, the Nordlie writer and `check_clean_tree.py` first (13b, with their tests) and F5 last (heaviest inputs, section 10). One sub-step per figure group with a stop after each.

**M13-8. When tags are proposed.** Ruling 3 (DL-422): tags are created only when the user says so. Options: (a) after each figure passes its tests and a clean-tree build, Claude proposes `fig-<ID>-v1` with the message text and waits; (b) one batch proposal at the end of MS13; (c) no proposal until MS15. *Recommendation:* (a), because the plan tags "each figure build" and a rebuild that changes an input needs `v2`; the proposal text carries the inputs and hashes (section 8). A tag is never moved; a new build is a new `v<k>`. Nothing is pushed.

**M13-9. Noise-free against noisy, and the solver-dependent onset (G6-D1 to G6-D3), in the figures.** Facts: the headline delay is taken from D43-floored runs; the noise-free onset is solver-dependent (58.698 s DOP853, 58.879 s Radau); RB3(b) is reported under both onset readings. Options: (a) F4 draws both the noise-free (mode D, DOP853) and the noisy/floored (mode N) delays as separate series with the solver difference shown as a band or a pair of markers, the onset reading named in the legend; (b) only the floored delay in the main panel, the rest in FS4; (c) one pooled series. *Recommendation:* (a) for F4 and FS4, with G6-D2 stated in the caption; never (c). The FS4 "affected results unused" wording for RB6 (section 4, FS4) is the reviewer's to read; the figure shows the RB6 FAIL and does not hide the results that depend on it.

**M13-10. How F5c and the N = 1e4 against 3e4 results are shown.** Plan: "F5c: metrics against N (CP7)" and RB1's "N = 3×10⁴ no worse than 10⁴" (MS10: the N rule PASSED while RB1 FAILED, `docs/ms10_close.md`). Options: (a) metrics (class, f_pk, onset, duration; Table 2.1) against N = 1e3, 3e3, 1e4, 3e4 with all 10 seeds drawn as points and the MF value as a reference line, the no-ramp control (S9_ctrl) drawn beside; (b) means with error bars; (c) classes only. *Recommendation:* (a), because G4-C3 says network classes cannot separate ramp-driven from non-ramp records and the control is the only way to show that.

**M13-11. Figure code placement, tests and `docs/figure_map.md`.** The plan names `plotting/style.py`, `plotting/figures.py` (all `make_*`), 12 scripts and `docs/figure_map.md` (content not specified: UNVERIFIED). Options: (a) as named, with `figure_map.md` mapping each figure to its inputs, analysis IDs and DL numbers (this file's section 4 as the source); (b) one module per figure under `plotting/`. *Recommendation:* (a) as in the plan; `figure_map.md` generated from the same input registry as the readiness script (`scripts/ms13_inputs.py` INPUTS) so that the two cannot drift. If `figures.py` grows large, splitting is an engineering change for the reviewer.

**M13-12. How much of S7, S9 and S13 the figure scripts read.** F5 can be drawn from the A9 tables alone (1,226 rows) plus a handful of example series, or can reload the 3,475 S7 series (15.9 GB). The plan says scripts "read only results/"; it does not say which files. Options: (a) tables first, series only for example panels and the hash check of the inputs; (b) all series. *Recommendation:* (a); the provenance file hashes every input record it reads, and for a table-only figure also names the records the table was built from by the table's own hash (UNVERIFIED: A9 stores `run_id`, so the link exists). Time estimates in section 10.

**M13-13. Reuse of the run-record machinery for figure provenance.** Options: (a) reuse `provenance.git_info`, `environment_info`, `sha256_file`, `atomic_write_*` and the frozen-criteria loader; (b) new code. *Recommendation:* (a); plan section 10.4 says the same fields apply to run records, and the loader's step 5 (no hashed file modified or untracked) is already the clean-tree test for the criteria. Whether `check_clean_tree.py` counts untracked files as dirty is M13-14 below.

**M13-14. Things the plan leaves without a statement, in words (each needs the reviewer's reading before the code is written).** (i) Whether an untracked file makes the tree dirty for a tagged build: `git status --porcelain` lists them; `figures/` and `results/` are ignored. *Reading proposed:* any line from `git status --porcelain` is dirty (a stray non-project file in the repository blocks the build; the 13a prompt says to report such a file). (ii) The "frequency mapping" panel of FS5: Table 8.1 gives only "A8"; the proposed inputs are A6 and the A11 RB9 rows (UNVERIFIED). (iii) Whether a figure built from a dirty tree for review is allowed and how its provenance is marked (the checklist says "none is marked DRAFT" for the release). *Reading proposed:* a dirty-tree build is allowed only without `--tag`, writes `"draft": true` and the provenance file shows `git.dirty = true`; it can never be tagged. (iv) The supplementary figure count with FS6 absent. (v) Whether F4's M2 ring panel uses A2's ring map or S2/A3; Table 8.1 lists A3 for F4 and A1, A2, S1 for FS1. (vi) Whether the claim-limit strip (M13-3) is part of the figure or of its caption. (vii) Resolution, font and size of the figures: the plan gives none; the journals are not chosen. (viii) Whether `make_all.ps1` is written at MS13 or MS15 (the plan lists it in the layout and uses it in 10.4 for the Numba cache).

## 7. Provenance specification (proposed; every field not in the plan is UNVERIFIED)

Plan basis: section 2.2 (script rule: "input records, config hashes, seeds, commits") and section 2.4 (10.4: commit, branch, tags, dirty flag; Python, packages, Julia, BifurcationKit; OS and CPU; SHA-256 of every input and output file; hash of the criteria file; numerical settings; the Numba cache note). The other fields follow the stored run records (section 3).

**`figures/<ID>/<ID>_provenance.json`** (location of the folder UNVERIFIED: `figures/` is git-ignored, section 2.4; the plan gives no sub-layout):

| Field | Content | Plan basis |
|---|---|---|
| `schema_version` | integer | UNVERIFIED (as the run records) |
| `figure_id`, `build` | ID, build counter `k` of the next tag | plan: `fig-<ID>-v<k>` |
| `status` | `ok` / `failed` | UNVERIFIED, as the run records (10.4: "every JSON record stores a status") |
| `draft` | true if built with `git.dirty = true` or untagged | UNVERIFIED (10.8: "none is marked DRAFT") |
| `git` | commit, branch, tags at HEAD, dirty flag (`provenance.git_info()`) | 10.4 |
| `python`, `packages` | version and executable; numpy, scipy, numba, pandas, pyarrow, pyyaml, matplotlib, pytest | 10.4 |
| `julia` | version and BifurcationKit version (null if not used) | 10.4 |
| `os`, `cpu` | platform string; processor, machine, count | 10.4 |
| `criteria_sha256`, `criteria_tag`, `criteria_commit` | from `verify_frozen_criteria()` | 10.4 (hash of the criteria file); tag and commit UNVERIFIED |
| `script` | path and SHA-256 of `scripts/fig_<ID>.py` | UNVERIFIED (the plan says "script hash" nowhere; the 13a prompt asks for it) |
| `modules` | path and SHA-256 of `plotting/figures.py`, `plotting/style.py` and any helper imported | UNVERIFIED |
| `configs` | path to SHA-256 for each config the inputs were produced with (`configs/S5.yaml`, `S13.yaml`, `ms11/…`) | script rule ("config hashes") |
| `inputs` | for every input file read: path, bytes, SHA-256, and for run records `run_id`, `config_hash12`, the record's own `git.commit` and `git.dirty`, `seed` (root_seed, spawn_key), `criteria_sha256`, `status` | 10.4 ("SHA-256 of every input … file"); script rule ("input records … seeds, commits") |
| `input_tables` | for a table-derived figure, the table's hash and the row count read | UNVERIFIED (M13-12) |
| `seeds` | seeds of the input records used; seed of any random choice made by the figure script (expected: none; any use is an error) | script rule; the "none" expectation is UNVERIFIED |
| `numerical_settings` | solver method, rtol, atol, max_step, δ₀, noise scheme/σ/dt, network N/dt/V_p of the input records, read from their JSON | 10.4 ("numerical settings are always recorded") |
| `spectrogram` | band, window rule, W, step, taper read from the frozen criteria | section 2.2 (captions) |
| `claim_limits` | IDs from section 5 that apply, with their DL numbers | UNVERIFIED |
| `outputs` | path and SHA-256 of the figure files, `<ID>_params.csv`, the caption text | 10.4 ("every … output file") |
| `numba_cache_cleared` | null for figure builds (no jitted code is called); the field is kept as in the run records | 10.4 (Numba cache note), value UNVERIFIED |
| `created_utc`, `wall_time_s`, `warnings` | as the run records | UNVERIFIED |

**`<ID>_params.csv`** (columns UNVERIFIED; the plan names the file only): `figure`, `panel`, `section` (Nordlie section), `name`, `key`, `value`, `units`, `status` (the five columns of `make_param_table`), plus `source_run_id`, `source_config_hash12`, `varied` (true if the value differs between the figure's inputs). A test (section 8) checks that every row matches the corresponding input record's config.

**Output folder.** `figures/<ID>/` (git-ignored, section 2.4). Contents: the figure files, `<ID>_provenance.json`, `<ID>_params.csv`. Never edited by hand (CLAUDE.md).

**`scripts/check_clean_tree.py`.** Plan: "blocks tagged builds from a dirty tree" (layout entry). Proposed behaviour (UNVERIFIED): called first by every `fig_<ID>.py --tag` and by `make_all.ps1`; runs `git status --porcelain`; exits 1 with the list of lines if there is any (M13-14 (i)); exits 0 otherwise; prints HEAD, branch and the tags at HEAD; also runs `verify_frozen_criteria()`. A build without `--tag` may run on a dirty tree and is marked `draft` (M13-14 (iii)). It writes nothing.

**Tag message** (plan: "inputs and hashes in the message"; example "F3 from A4 <hash12>, A6 <hash12>"). Proposed content, UNVERIFIED as a layout: line 1 `fig-<ID>-v<k> <ID> built <date UTC> at <commit>`; then one line per input family `<analysis or run ID> <path> <sha256 or hash12>`; the criteria SHA-256; the SHA-256 of `<ID>_provenance.json`, of the figure file(s) and of `<ID>_params.csv`; the claim-limit IDs. Tags are annotated, created only when the user says so (DL-422) and never pushed unless asked.

## 8. Tests to add (listed, not written at 13a; each states its tolerance)

| # | Test | Tolerance / criterion |
|---|---|---|
| 1 | A figure script reads only `results/` and never simulates: the AST of every `scripts/fig_*.py` and of `plotting/*.py` imports none of `simulate_mf`, `qif_network`, `run`, `timing_run`, `models.*`; a run with `results/` set read-only (or a spy on `open` / `np.savez` / `Path.write_*`) finds no write under `results/` | exact: the import set and the write set are empty |
| 2 | Provenance fields complete: every field of section 7 present, correct type, no null where non-null is required; criteria hash equals the frozen value | exact set equality of field names |
| 3 | Hashes match: every input and output hash in a provenance file equals `sha256_file` of the stored file; a changed byte is detected | exact (SHA-256) |
| 4 | `check_clean_tree.py` refuses a dirty tree: a temporary git repository with a modified tracked file, with an untracked file, and clean; exit codes 1, 1 (under M13-14 (i)), 0; nothing written | exact exit codes |
| 5 | `params.csv` matches provenance: every row's `source_run_id` is in `inputs`, and each `value` equals the config value of that record | exact for strings and integers; floats equal after JSON round-trip (rel 0) |
| 6 | A missing or unreadable input gives a clear error: a deleted npz, a truncated parquet and a hash mismatch each raise one named error (the missing path in the message) and no figure file is written; no blank panel | exact exception type and a message containing the path |
| 7 | Caption and parameter table are generated from the same config values: the caption's parameter string equals the one in `params.csv` | exact |
| 8 | Colour table: one fixed colour and one marker per class and path; no two classes share a colour; the colour-blind-safety criterion in words (M13-2) is checked by a stated simulation of one deficiency type | UNVERIFIED: the criterion needs a number from the reviewer |
| 9 | A rebuilt figure from the same inputs gives the same data arrays that were plotted (not the pixels): drawn-data hash equal across two runs in one process | rel 1e-12 on floats (not bitwise across machines, plan 10.5) |
| 10 | FS6 is refused: `fig_FS6.py` is not present, `make_FS6` raises a named error citing MS12-C1 | exact |
| 11 | Claim-limit strip: every ID in section 5 assigned to a figure by the reviewer appears in that figure's provenance `claim_limits` | exact set equality |
| 12 | Readiness registry: `scripts/ms13_inputs.py` INPUTS and the figure scripts' declared inputs name the same files | exact set equality |

Slow-marked tests: none expected except a full rebuild of F5 from stored inputs (UNVERIFIED).

## 9. What 13b must do next (no prompt text)

1. Obtain the reviewer's rulings on M13-1 to M13-14; record them under the next free DL numbers.
2. Write `plotting/style.py`, the provenance writer, the Nordlie writer and `scripts/check_clean_tree.py` with the tests of section 8 (1 to 7); commit before any figure is built.
3. Build the figures in the ruled order, one group per sub-step, from a clean tree, each with its tests; stop after each; propose tags per M13-8.
4. Write `docs/figure_map.md` from the input registry; `make_all.ps1` per M13-14 (viii).

## 10. Load-time sample (read-only; `scripts/ms13_inputs.py timing`)

Committed before it was run (script and this file, commit recorded in DL-423), so the record shows git dirty = false. The script reads and times; it simulates nothing and writes nothing. Results are filled in below after the run.

TIMING_PLACEHOLDER

## 11. Decision-log entries of 13a

| DL | Content |
|---|---|
| DL-419 | pre-checks (all PASS), starting fast suite |
| DL-420 | ruling: the MS11 close is acknowledged, MS11-C1 to MS11-C9 stand |
| DL-421 | ruling: MS12 not run; claim limit MS12-C1 |
| DL-422 | ruling: tags only when the user says so |
| DL-423 | 13a facts: figure code inventory, readiness (11 ready, FS6 not produced), triggers per figure, the commit of this file and the script before the timing sample |
| DL-424 | 13a result: timing sample, SHA-256 of this file (working copy and LF blob), fast suite, commit |
