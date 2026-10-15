# Decision log

File: docs/decision_log.md. One entry per decision; entries are never deleted. A changed decision gets a new entry that links back to the old one, and its commit or tag is recorded.

## DL-001  Output sampling of v, r    [ID: D1]
Date:                              Author:
Decision:        Output sampling of v, r
Options:
Chosen:          1 kHz (dt_out_ms = 1)   Default from: Part 1
Evidence:
Test:            Spectral peak changes with 2 kHz output
Status:          default adopted
Commit/tag:

## DL-002  Primary gamma band    [ID: D2]
Date:                              Author:
Decision:        Primary gamma band
Options:
Chosen:          25–100 Hz; also γ1, γ2, peak   Default from: Part 1
Evidence:
Test:            > 5% of cells change class at 30–120 Hz (RB9c)
Status:          default adopted
Commit/tag:

## DL-003  Total band for ρ    [ID: D3]
Date:                              Author:
Decision:        Total band for ρ
Options:
Chosen:          1–150 Hz, detrended   Default from: Part 1
Evidence:
Test:            RB10
Status:          default adopted
Commit/tag:

## DL-004  Spectrogram    [ID: D4]
Date:                              Author:
Decision:        Spectrogram
Options:
Chosen:          Hann; W = 2 s or the T_ramp rule   Default from: Part 1
Evidence:
Test:            Window × 0.5 or × 2 changes class (RB10)
Status:          default adopted
Commit/tag:

## DL-005  Baseline window    [ID: D5]
Date:                              Author:
Decision:        Baseline window
Options:
Chosen:          last 5 s before ramp   Default from: Part 1
Evidence:
Test:            RB10
Status:          default adopted
Commit/tag:

## DL-006  Factors, mode N    [ID: D6]
Date:                              Author:
Decision:        Factors, mode N
Options:
Chosen:          2 × baseline; the relative test uses P_G/P_non-G (v0.4)   Default from: Part 1
Evidence:
Test:            1.5 or 4 changes class (RB10)
Status:          default adopted
Commit/tag:

## DL-007  Amplitude threshold, mode D    [ID: D7]
Date:                              Author:
Decision:        Amplitude threshold, mode D
Options:
Chosen:          0.1 × A_ref, one fixed absolute threshold (A_ref at ref_devalle); mode-D classes D-tr, D-sus, D-none (v0.4)   Default from: Part 1
Evidence:
Test:            0.05 or 0.2 changes class (RB10)
Status:          default adopted
Commit/tag:

## DL-008  Minimum duration; damped vs non-damped    [ID: D8]
Date:                              Author:
Decision:        Minimum duration; damped vs non-damped
Options:
Chosen:          ≥ 10 cycles; non-damped unless the envelope growth, fitted from the threshold crossing over the first 10 cycles, is negative by more than 2 standard errors (v0.5)   Default from: Part 1
Evidence:
Test:            5 or 20 changes class (RB10); the growth test disagrees with A4 stability
Status:          default adopted
Commit/tag:

## DL-009  Collapse marker    [ID: D9]
Date:                              Author:
Decision:        Collapse marker
Options:
Chosen:          r < 10% of baseline; J = 0 is no longer a marker; P2 episodes report J_exit,run against J_exit,static (v0.4; split in v0.5)   Default from: Part 1
Evidence:
Test:            Classes depend on the marker
Status:          default adopted
Commit/tag:

## DL-010  Xu raw EEG    [ID: D10]
Date:                              Author:
Decision:        Xu raw EEG
Options:
Chosen:          out of scope   Default from: Part 1
Evidence:
Test:            Scope change only
Status:          default adopted
Commit/tag:

## DL-011  τ_d sweep    [ID: D11]
Date:                              Author:
Decision:        τ_d sweep
Options:
Chosen:          1–50 ms, 30 log   Default from: Part 1
Evidence:
Test:            Map boundary at the range edge
Status:          default adopted
Commit/tag:

## DL-012  η̄ end points    [ID: D12]
Date:                              Author:
Decision:        η̄ end points
Options:
Chosen:          η̄_H − 1.5 → max(4, η̄_H + 2); η̄_H = lowest crossing; no Hopf: the headline cell's end points (v0.4)   Default from: Part 1
Evidence:
Test:            RB4, start-distance runs
Status:          default adopted
Commit/tag:

## DL-013  Δ sweep    [ID: D13]
Date:                              Author:
Decision:        Δ sweep
Options:
Chosen:          0.01–0.6, 30 linear   Default from: Part 1
Evidence:
Test:            K9 threshold outside range
Status:          default adopted
Commit/tag:

## DL-014  J sweep    [ID: D14]
Date:                              Author:
Decision:        J sweep
Options:
Chosen:          −40 to −5, 25 values   Default from: Part 1
Evidence:
Test:            Map boundary at the range edge
Status:          default adopted
Commit/tag:

## DL-015  Drive I(t)    [ID: D15]
Date:                              Author:
Decision:        Drive I(t)
Options:
Chosen:          trapezoid; I_amp 1 {0.5, 1, 2}   Default from: Part 1
Evidence:
Test:            S6 and NC2 results
Status:          default adopted
Commit/tag:

## DL-016  Ramp duration    [ID: D16]
Date:                              Author:
Decision:        Ramp duration
Options:
Chosen:          120 s; 1–1000 s, 13 log   Default from: Part 1
Evidence:
Test:            RB3(c)
Status:          default adopted
Commit/tag:

## DL-017  Network step    [ID: D17]
Date:                              Author:
Decision:        Network step
Options:
Chosen:          10⁻³ τ   Default from: Part 1
Evidence:
Test:            RB6 dt ladder
Status:          default adopted
Commit/tag:

## DL-018  MF noise σ    [ID: D18]
Date:                              Author:
Decision:        MF noise σ
Options:
Chosen:          calibrated at MS5 to an N = 10⁴ baseline run; × 0.5, × 2   Default from: Part 1
Evidence:
Test:            RB2
Status:          default adopted
Commit/tag:

## DL-019  J path in P2    [ID: D19]
Date:                              Author:
Decision:        J path in P2
Options:
Chosen:          J0 → 0 from t_on + 0.25 T over T   Default from: Part 1
Evidence:
Test:            RB4
Status:          default adopted
Commit/tag:

## DL-020  Δ direction    [ID: D20]
Date:                              Author:
Decision:        Δ direction
Options:
Chosen:          both (P4a, P4b)   Default from: Part 1
Evidence:
Test:            Primary data on Δ
Status:          default adopted
Commit/tag:

## DL-021  Ramp profile    [ID: D21]
Date:                              Author:
Decision:        Ramp profile
Options:
Chosen:          linear; sigmoid k = 10   Default from: Part 1
Evidence:
Test:            RB3(d)
Status:          default adopted
Commit/tag:

## DL-022  Interneuron-drive assumption    [ID: D22]
Date:                              Author:
Decision:        Interneuron-drive assumption
Options:
Chosen:          not rejected; M4 as robustness variant   Default from: Part 1
Evidence:
Test:            G2(c)
Status:          default adopted
Commit/tag:

## DL-023  Continuation tool    [ID: D23]
Date:                              Author:
Decision:        Continuation tool
Options:
Chosen:          BifurcationKit.jl; fallback WSL2 + PyCoBi/AUTO-07p, or S4 alone   Default from: Part 1
Evidence:
Test:            K7 not reproduced on Windows within one day (MS1)
Status:          default adopted
Commit/tag:

## DL-024  Noisy/deterministic agreement    [ID: D24]
Date:                              Author:
Decision:        Noisy/deterministic agreement
Options:
Chosen:          ≥ 90% of subgrid cells   Default from: Part 1
Evidence:
Test:            RB2
Status:          default adopted
Commit/tag:

## DL-025  MF solver    [ID: D25]
Date:                              Author:
Decision:        MF solver
Options:
Chosen:          DOP853, rtol 10⁻¹⁰, atol 10⁻¹², max_step 0.05 τ; Radau check   Default from: Part 1
Evidence:
Test:            RB6
Status:          default adopted
Commit/tag:

## DL-026  Initial perturbation    [ID: D26]
Date:                              Author:
Decision:        Initial perturbation
Options:
Chosen:          δ₀ = 10⁻⁶ on v, applied at t_on (v0.4)   Default from: Part 1
Evidence:
Test:            RB5
Status:          default adopted
Commit/tag:

## DL-027  Durations    [ID: D27]
Date:                              Author:
Decision:        Durations
Options:
Chosen:          baseline 5 s; hold 10 s after the last ramp ends (1.25 T_ramp on P2-based paths); discard 2 s before t = 0 (v0.4)   Default from: Part 1
Evidence:
Test:            Transient visible after discard
Status:          default adopted
Commit/tag:

## DL-028  Lorentzian grid formula    [ID: D28]
Date:                              Author:
Decision:        Lorentzian grid formula
Options:
Chosen:          tan quantiles (Taher, Torcini, Olmi 2020 Eq. 8; CP3)   Default from: Part 1
Evidence:
Test:            Settled in v0.3: Taher, Torcini, Olmi 2020 Eq. (8), η_i = H + Δ tan[(π/2)(2i − N − 1)/(N + 1)], matches the default [RB-item 6]. Status: confirmed by primary source; quantile test kept
Status:          confirmed by primary source
Commit/tag:

## DL-029  Gaussian/uniform width    [ID: D29]
Date:                              Author:
Decision:        Gaussian/uniform width
Options:
Chosen:          HWHM = Δ; uniform: half-range = Δ (v0.4)   Default from: Part 1
Evidence:
Test:            RB8
Status:          default adopted
Commit/tag:

## DL-030  Network v readout    [ID: D30]
Date:                              Author:
Decision:        Network v readout
Options:
Chosen:          mean over non-refractory neurons   Default from: Part 1
Evidence:
Test:            RB1 sensitivity to inclusion
Status:          default adopted
Commit/tag:

## DL-031  Grid resolution    [ID: D31]
Date:                              Author:
Decision:        Grid resolution
Options:
Chosen:          halving spacing moves the boundary < 1 cell   Default from: Part 1
Evidence:
Test:            Refinement test
Status:          default adopted
Commit/tag:

## DL-032  Kuramoto |Z| readout (CP6)    [ID: D32]
Date:                              Author:
Decision:        Kuramoto |Z| readout (CP6)
Options:
Chosen:          Add as a secondary readout after the formula is taken from MPR 2015; until then not computed   Default from: Part 2
Evidence:
Test:            Formula obtained. v0.3: not settled. RB found only the Z–W map (MPR Eq. 18) and no printed |Z| formula, in arXiv v1 only [RB-item 1a: PARTIAL]
Status:          default adopted
Commit/tag:

## DL-033  Cauchy-noise run (C17)    [ID: D33]
Date:                              Author:
Decision:        Cauchy-noise run (C17)
Options:
Chosen:          Not run (equations absent)   Default from: Part 2
Evidence:
Test:            Equations from Clusella and Montbrió 2024. v0.3: not settled; RB does not cover them
Status:          default adopted
Commit/tag:

## DL-034  Replication tolerances    [ID: D34]
Date:                              Author:
Decision:        Replication tolerances
Options:
Chosen:          Table 7.1, including the K4 tail-fit fraction; frozen at the end of MS1 (tolerances-frozen)   Default from: Part 2
Evidence:
Test:            Published precision, once primary figures are read
Status:          default adopted
Commit/tag:

## DL-035  Robustness and gate thresholds    [ID: D35]
Date:                              Author:
Decision:        Robustness and gate thresholds
Options:
Chosen:          Table 7.2; G5: 3% of cells, 80% LHS   Default from: Part 2
Evidence:
Test:            Frozen at MS7; changes logged
Status:          default adopted
Commit/tag:

## DL-036  Compute cap and cut order    [ID: D36]
Date:                              Author:
Decision:        Compute cap and cut order
Options:
Chosen:          24 h wall-clock (S1–S13, S16); cut order of section 9.3   Default from: Part 2
Evidence:
Test:            Timing gate
Status:          default adopted
Commit/tag:

## DL-037  Code licence and archive    [ID: D37]
Date:                              Author:
Decision:        Code licence and archive
Options:
Chosen:          MIT licence; release archived with a persistent identifier; service chosen at MS15   Default from: Part 2
Evidence:
Test:            Institutional requirement
Status:          default adopted
Commit/tag:

## DL-038  K6 forcing amplitude and Δ    [ID: D38]
Date:                              Author:
Decision:        K6 forcing amplitude and Δ
Options:
Chosen:          K6 optional until read from MPR Fig. 3   Default from: Part 2
Evidence:
Test:            Values obtained. v0.3: not settled. RB read I₀, ω and Δ in arXiv v1 only, with Δ from App. A [RB-item 1b: PARTIAL]
Status:          default adopted
Commit/tag:

## DL-039  Finite size in the main text (CP7)    [ID: D39]
Date:                              Author:
Decision:        Finite size in the main text (CP7)
Options:
Chosen:          Panel F5c plus FS3   Default from: Part 2
Evidence:
Test:            Figure budget
Status:          default adopted
Commit/tag:

## DL-040  Headline example    [ID: D40]
Date:                              Author:
Decision:        Headline example
Options:
Chosen:          P2, ref_devalle, T_ramp 120 s, linear, I = 0; default fixed now, confirmed at MS6, before S5   Default from: Part 2
Evidence:
Test:            Spectral peak < 25 Hz (F1 rule)
Status:          default adopted
Commit/tag:

## DL-041  Build order    [ID: ]
Date:                              Author:
Decision:        Build order
Options:
Chosen:          M2 diagnostic → G1 → M3 primary; M4 or adaptation only via G2 or G3   Default from: Part 2
Evidence:
Test:            G1, G2, G3 outcomes
Status:          default adopted
Commit/tag:

## DL-042  Replication before new work    [ID: ]
Date:                              Author:
Decision:        Replication before new work
Options:
Chosen:          G0 must pass before S5   Default from: Part 2
Evidence:
Test:            —
Status:          default adopted
Commit/tag:

## DL-043  Criteria frozen before M3 ramp-study runs    [ID: ]
Date:                              Author:
Decision:        Criteria frozen before M3 ramp-study runs
Options:
Chosen:          Tag criteria-frozen at MS7, with SHA-256 in the tag; replication tolerances (D34) frozen at the end of MS1 (tolerances-frozen)   Default from: Part 2
Evidence:
Test:            —
Status:          default adopted
Commit/tag:

## DL-044  Corrections to Part 1    [ID: ]
Date:                              Author:
Decision:        Corrections to Part 1
Options:
Chosen:          CP1–CP27 applied; sections 2–6 edited in place where CP14–CP27 record it; handoff unchanged except its (d) paths and header line   Default from: Part 2
Evidence:
Test:            Primary-source check
Status:          default adopted
Commit/tag:

## DL-045  Figure production    [ID: ]
Date:                              Author:
Decision:        Figure production
Options:
Chosen:          One script per figure, reading results only; tag per build   Default from: Part 2
Evidence:
Test:            —
Status:          default adopted
Commit/tag:

## DL-046  Toolchain    [ID: ]
Date:                              Author:
Decision:        Toolchain
Options:
Chosen:          Python 3.11 + Numba; no PyDSTool; AUTO-07p, XPPAUT, MatCont flagged   Default from: Part 2
Evidence:
Test:            D23 test
Status:          default adopted
Commit/tag:

## DL-047  G8 next step after PARTIAL OVERLAP (section 12.7)    [ID: D41]
Date:                              Author:
Decision:        G8 next step after PARTIAL OVERLAP (section 12.7)
Options:
Chosen:          Decided in v0.4: claim reframed as a first mechanistic model; Taher 2022 and Avitabile 2022 cited as method precedent; noise robustness (RB2) a main result; G8 third branch met by A7's entry–exit metrics; MS14 still runs before writing   Default from: v0.3
Evidence:
Test:            MS14 finds closer prior work
Status:          decided in v0.4
Commit/tag:

## DL-048  M4 form (section 7.3)    [ID: D42]
Date:                              Author:
Decision:        M4 form (section 7.3)
Options:
Chosen:          Table 4.1 form (E–I, instantaneous synapses); its equations still to be read from MPR App. E or Segneri before S14   Default from: v0.3
Evidence:
Test:            Choosing Dumont and Gutkin 2019 Eqs. (7)–(8) (first-order synapses; read in the primary source [single source: RB-item 5]); decide before S14 or any RB8 M4 run
Status:          default adopted
Commit/tag:

## DL-049  Slow-passage noise floor (A7)    [ID: D43]
Date:                              Author:
Decision:        Slow-passage noise floor (A7)
Options:
Chosen:          A small additive noise floor on v for the A7 delay test, integrated with stochastic Heun, at levels set at MS7 (before criteria-frozen; Conventions); no scaling law entered (UNVERIFIED)   Default from: v0.4
Evidence:
Test:            RB3(b) and RB6 results; a primary-source scaling law
Status:          default set at MS7
Commit/tag:

## DL-050  settings.json adds PowerShell(...) allow rules    [ID: ]
Date:            2026-10-13        Author:
Decision:        the shared settings.json carries PowerShell(...) versions of the four allow rules next to the Bash(...) rules of section 10.9.
Reason:          on Windows without Git for Windows, Claude Code has only the PowerShell tool, so Bash(...) rules would not match.
Options:
Chosen:          "PowerShell(python -m pytest *)", "PowerShell(python -m mprsurge.run *)", "PowerShell(git status)", "PowerShell(git diff *)"   Default from: new
Evidence:        Claude Code documentation, Permissions page (PowerShell section) and Tools reference (PowerShell tool), https://code.claude.com/docs/en/permissions and https://code.claude.com/docs/en/tools-reference
Test:            at MS0, ask Claude Code to run python -m pytest and check /permissions; adjust to what it shows.
Status:          default adopted
Commit/tag:

## DL-051  venv-path allow rules and CLAUDE.md commands    [ID: ]
Date:            2026-10-14        Author:
Decision:        settings.json adds four allow rules that use the venv interpreter by path (PowerShell and Bash forms, pytest and mprsurge.run); CLAUDE.md names .venv\Scripts\python.exe for the pytest command and states that plain python is not the venv.
Reason:          plain python resolves to Python 3.12.10 (no pytest, no project packages) in both the PowerShell and the Bash tool, so the rules of DL-050 allow a command that runs the wrong interpreter.
Options:         activate the venv (needs Set-ExecutionPolicy; not tested); keep plain python rules only.
Chosen:          venv-path rules added next to the existing eight; DL-050 rules kept   Default from: new
Evidence:        MS0 test 6b: python --version gave 3.12.10 in both tools; python -m pytest failed with "No module named pytest"; .venv\Scripts\python.exe -m pytest ran under Python 3.11.9. Links back to DL-050.
Test:            whether /permissions shows the new rules matching the venv-path commands without a prompt.
Status:          default adopted
Commit/tag:

## DL-052  tests/test_smoke.py added                  [ID: ]
Date:            2026-10-14        Author:
Decision:        add tests/test_smoke.py (import mprsurge, assert its name) so that pytest collects at least one test.
Reason:          pytest exits with code 5 on an empty suite, and the MS0 done-when is "pytest collects".
Options:         no test file (exit 5); a test that asserts a version.
Chosen:          one import test, no version asserted   Default from: new
Evidence:        MS0 run: collected 0 items, exit code 5.
Test:            remove or supersede when real tests exist.
Status:          default adopted
Commit/tag:

## DL-053  Stable fixed-point selection rule    [ID: ]
Date:            2026-10-14        Author:
Decision:        the start state of a run is the stable fixed point at the start parameters; if there is not exactly one stable root, the code raises an error.
Reason:          section 6.2 says "exact stable fixed point" but not what to do with several stable roots (M2 bistable wedge) or none.
Options:         pick the stable root with the largest r; add a branch key; raise.
Chosen:          raise   Default from: new (user accepted 2026-10-14)
Evidence:        plan 6.2 (Initial state), 3.1 (bistable wedge). The rule itself is a choice, not from the plan.
Test:            test_fixed_points (1b-i).
Status:          default adopted
Commit/tag:      entry added in 9f27a8f

## DL-054  ref_point precedence and ref_ceni tau_d    [ID: ]
Date:            2026-10-14        Author:
Decision:        layer order base < ref_point < run file < --set; explicit overrides win over ref_point. ref_mpr is M2 (eta_bar, J, Delta, no tau_d); ref_ceni sets eta_bar, J, Delta and requires an explicit tau_d_ms in {3, 4.95, 8}; ref_devalle sets eta_bar, J, Delta, tau_d_ms = 5.
Reason:          section 10.3 says resolve_config merges base, run file and --set and then expands ref_point; read literally, the expansion would overwrite run-file values. The user confirmed that explicit overrides win.
Options:         literal order (expand after merge); explicit-wins.
Chosen:          explicit-wins   Default from: new (user confirmed 2026-10-14)
Evidence:        plan 10.3; Appendix B (ref points, tau_d values). Membership in {3, 4.95, 8} is a restriction of this entry, not of the plan: a ref_ceni run at another tau_d (for example the K10 range up to 50 ms) needs a new entry.
Test:            test_config.
Status:          default adopted
Commit/tag:      entry added in 9f27a8f

## DL-055  run.kind values    [ID: ]
Date:            2026-10-14        Author:
Decision:        run.kind takes "mf" and "mf_noisy" at MS1; "network" is added at MS5.
Reason:          section 10.3 lists the key but gives no values.
Options:         free string; fixed set.
Chosen:          fixed set   Default from: new (user accepted 2026-10-14)
Evidence:        plan 10.3, 10.1 (simulate_mf: run_mf, run_mf_noisy).
Test:            test_config.
Status:          default adopted
Commit/tag:      entry added in 9f27a8f

## DL-056  Dry-run record status    [ID: ]
Date:            2026-10-14        Author:
Decision:        --dry-run writes <run_id>_<hash12>.dry.json with status "dry_run"; it is never counted as complete by skip-if-done.
Reason:          the plan allows ok, failed, timeout; a dry-run record with status ok would be skipped as finished.
Options:         status ok plus a flag; separate file and status.
Chosen:          separate file and status   Default from: new (user accepted 2026-10-14)
Evidence:        plan Table 11.1 (MS1 done-when), 10.4 (statuses).
Test:            test_runner part 1.
Status:          default adopted
Commit/tag:      entry added in 9f27a8f

## DL-057  config_hash key set    [ID: ]
Date:            2026-10-14        Author:
Decision:        config_hash covers the sections model, path, solver, noise, network, durations, the key run.kind, and seeds.root_seed and seeds.spawn_key. It excludes analysis, sweep, run.workers, run.id, run.wall_limit_s, output, replication, robustness, budget, seeds.n_seeds.
Reason:          section 10.3 says "cell parameters, seed spawn key, and solver and numerics settings"; I read this as the inputs of an integration, because drivers only integrate (10.1). seeds.root_seed is added to the spawn key because a spawn key alone does not define the random stream.
Options:         hash the whole resolved config minus the excluded keys of 10.3.
Chosen:          integration inputs only   Default from: new (user accepted 2026-10-14)
Evidence:        plan 10.3, 10.1, 6.6.
Test:            test_config (independent of key order, workers, paths).
Status:          default adopted
Commit/tag:      entry added in 9f27a8f

## DL-058  Per-run wall-time limit key    [ID: ]
Date:            2026-10-14        Author:
Decision:        new key run.wall_limit_s (seconds, default null = no limit) until MS3 timing gives predicted times.
Reason:          section 10.4 requires a per-run limit "for example 10x its predicted time"; no prediction exists before MS3. budget.max_wall_h is the total budget (D36), a different key.
Options:         fixed default; null until MS3.
Chosen:          null until MS3   Default from: new (user accepted 2026-10-14)
Evidence:        plan 10.4, 9.2, Appendix B (budget).
Test:            test_runner.
Status:          default adopted
Commit/tag:      entry added in 9f27a8f

## DL-059  make_param_table format    [ID: ]
Date:            2026-10-14        Author:
Decision:        make_param_table returns rows (name, config key, value, units, source/status from Appendix B); no claim of Nordlie sectioning.
Reason:          section 6.6 and handoff (d) name the function and say "Nordlie-format"; the format is not specified.
Options:         full Nordlie sections; plain table.
Chosen:          plain table   Default from: new (user accepted 2026-10-14)
Evidence:        plan 6.6, Appendix B.
Test:            test_config (rows carry every resolved key).
Status:          default adopted
Commit/tag:      entry added in 9f27a8f

## DL-060  Ramp readings (logistic centre, P5 duration, Delta_factor)    [ID: D21]
Date:            2026-10-14        Author:
Decision:        (1) the logistic centre is 0.5: g(x) = (L(k(x - 0.5)) - L(-k/2)) / (L(k/2) - L(-k/2)), L the logistic function. This is an UNSOURCED choice: section 4.4 gives k = 10 and the rescaling but no centre. (2) P5 lasts 2 x T_ramp in total (up over T_ramp, down over T_ramp), hold after that. (3) Delta_factor stays 1.0 in base.yaml; the P4a/P4b values 1.5 and 2/3 are set in run configs.
Reason:          sections 4.4, 6.2, Appendix B and base.yaml (10.3) leave these open.
Options:         other centres; P5 doubling each leg.
Chosen:          as above   Default from: new (user accepted 2026-10-14)
Evidence:        plan 4.4 (Paths), 6.2 (Durations), Appendix B.
Test:            test_ramps (1b-i); A7 profile comparison.
Status:          default adopted
Commit/tag:      entry added in 9f27a8f

## DL-061  Test-level tolerances    [ID: ]
Date:            2026-10-14        Author:
Decision:        tolerances not given by section 10.5 (finite-difference Jacobian check, M3 at tau_d = 1e-3 tau tracking M2) are chosen in the test and stated there and in the sub-step report. The 0.5% of RB9a is the plan's.
Reason:          section 10.5 requires every test to state its tolerance but gives no value for these.
Options:         -
Chosen:          per test   Default from: new (user accepted 2026-10-14)
Evidence:        plan 10.5.
Test:            test_models_2d, test_models_3d (1b-i).
Status:          default adopted
Commit/tag:      entry added in 9f27a8f

## DL-062  surge_metrics core methods    [ID: D8]
Date:            2026-10-14        Author:
Decision:        zero-phase Butterworth band-pass (order 4); Hann periodogram per window with linear detrend, bins summed over the band; cycle count = unwrapped analytic phase / 2 pi while the envelope is at or above the threshold; growth = OLS slope of ln(envelope) over the first 10 cycles from the threshold crossing, with the OLS standard error. The threshold is an argument (A_ref exists from MS6/MS7).
Reason:          Table 2.1 names the quantities (Hann, linear detrend, Hilbert envelope, 10 cycles, 2 standard errors) but not the filter, the estimator or the cycle-counting method.
Options:         other filters or orders; Welch; zero-crossing cycle count.
Chosen:          as above   Default from: new (user accepted 2026-10-14)
Evidence:        plan Table 2.1, 5.2 A8. CAVEAT: the 2-standard-error test uses plain OLS standard errors on a smooth, autocorrelated envelope, so the standard error is too small and "damped" is too easily declared. To be revisited at MS7 (A8) before classifying noisy runs.
Test:            test_surge_metrics (1c); revisit at MS7.
Status:          default adopted; revisit at MS7
Commit/tag:      entry added in 9f27a8f

## DL-063  New files for the Julia smoke test    [ID: D23]
Date:            2026-10-14        Author:
Decision:        add src/mprsurge/analysis/continuation/bk_smoke.jl and julia_io.py (not in the section 10.1 tree). Julia is run by hand, not inside pytest; test_julia_io validates fixtures only.
Reason:          section 9.1 says a Python step validates the Julia output; section 10.1 names bk_cycles.jl (A5) and test_julia_io but no smoke script or reader module.
Options:         put the smoke test in bk_cycles.jl; new files.
Chosen:          new files   Default from: new (user accepted 2026-10-14)
Evidence:        plan 9.1, 10.1, 10.5.
Test:            test_julia_io (1d).
Status:          default adopted
Commit/tag:      entry added in 9f27a8f

## DL-064  Operational definitions for Table 7.1 gaps (K1, K5, K7, K8)    [ID: D34]
Date:            2026-10-14        Author:
Decision:        K8: follow Table 7.1 (mean-field runs start from Devalle's Fig. 3 initial values), although section 6.2 says to start from the fixed point; that applies to this replication run only. K1 (approved by the user): 20 r values uniform on the r-interval where the K1 formula point lies inside the A1 grid (computed from the formula at 1e); pass when the grid edge where the positive-root count changes lies within one cell (0.05, 0.1) of the formula point. K7 (UNVERIFIED, approved by the user with one change): "decays" at 3 ms = max Re(lambda) < 0 (A4) and the G1 rule on the S3 run (the fit window starts at the first of the cycles counted in G, no amplitude threshold, because A_ref exists only from A5 at MS6), growth negative by more than 2 standard errors; "holds within +-2%" at 8 ms = peak-to-peak v of each of the last 10 cycles (min_cycles) of the 10 s S3 run within 2% of their mean. K5: OPEN. No definition is entered; the user checks the primary source before the freeze at 1e. If no usable definition exists, the user decides then and a new entry records the departure from G0 (which lists K5 as blocking).
Reason:          Table 7.1 gives "20 sampled r" without a range, K5 without a forcing form or burst definition, and K7 without an operational test.
Options:         guess; enter as non-blocking; hold open.
Chosen:          as above   Default from: new
Evidence:        plan 7.1, 3.1 (K5), 6.2, Table 2.1, 5.2 A2/A4. K7 reuses D8, min_cycles and the S3 duration; none of that is sourced for K7. K4 tail fraction 0.1 (UNVERIFIED) is confirmed at 1e and logged then.
Test:            test_replication (MS2/MS5).
Status:          partly open (K5)
Commit/tag:      entry added in 9f27a8f

## DL-065  Provisional eta path and sigma placeholders    [ID: D12]
Date:            2026-10-14        Author:
Decision:        new keys path.eta_H (null until A4) and path.eta_path_status (unresolved / provisional / A4). eta_start = eta_H - 1.5 and eta_peak = max(4, eta_H + 2) are derived only from a non-null eta_H. Explicit eta_start and eta_peak (--set) give status "provisional", recorded in the record and the hash. A ramp run with an unresolved path raises an error. noise.sigma is null until the MS5 calibration; mode N refuses to run with it null.
Reason:          D12 derives the path from eta_H, but A4 does not exist until MS5; section 9.2 says the path is "recorded as such" until then. No value of eta_H is entered.
Options:         invented eta_H; throwaway Hopf solve at MS3; null plus explicit override.
Chosen:          null plus explicit override   Default from: new (user chose 2026-10-14)
Evidence:        plan 3.2 (eta row), 4.4 (P1), 9.2, 6.4, Appendix B.
Test:            test_config.
Status:          default adopted
Commit/tag:      entry added in 9f27a8f

## DL-066  ref_ceni tau_d validated against the D11 range (supersedes DL-054 in part)    [ID: D11]
Date:            2026-10-14        Author:
Decision:        for model.ref_point = ref_ceni, model.tau_d_ms must still be given explicitly, and is validated against the D11 range 1-50 ms (error outside it). A value outside {3, 4.95, 8} ms gives a warning, not an error.
Reason:          DL-054 restricted ref_ceni to {3, 4.95, 8}; the user accepted an explicit tau_d_ms, not that restriction. K10 and A6 need ref_ceni values up to 50 ms.
Options:         keep the set (blocks K10/A6); range check with a warning.
Chosen:          range 1-50 ms, warning outside the S3 set   Default from: new (user decision 2026-10-14)
Evidence:        plan 5.2 A6, Table 7.1 K10 (up to 50 ms), D11 (range 1-50 ms), Appendix B. Supersedes the membership rule in DL-054; DL-054 is not edited.
Test:            test_config.
Status:          default adopted
Commit/tag:      entry added in 5f94fb9

## DL-067  eta_path_status value "explicit" (extends DL-065)    [ID: D12]
Date:            2026-10-14        Author:
Decision:        path.eta_path_status takes a fourth value, "explicit": explicit eta_start and eta_peak on an M2 model (for example S2, whose values come from the A1 folds). "provisional" stays for M3 paths given explicitly before A4 exists. The derived status is part of the hash, as in DL-065.
Reason:          DL-065 labelled every explicit path "provisional", which would mislabel M2 paths whose end points come from A1, not from a missing A4.
Options:         one value for both; separate value.
Chosen:          separate value   Default from: new (user decision 2026-10-14)
Evidence:        plan 6.5 (S2), 5.2 A1, 9.2 ("recorded as such"). DL-065 is not edited.
Test:            test_config.
Status:          default adopted
Commit/tag:      entry added in 5f94fb9

## DL-068  Runner readings (cells, seeds, naming, skip, pool, logging)    [ID: ]
Date:            2026-10-14        Author:
Decision:        (1) sweep axes are sweep.x_name/x_values, sweep.y_name/y_values (dotted section.key names, not derived keys) and sweep.T_ramp_values (path.T_ramp_s); cells are their product. (2) Only run.kind = mf_noisy repeats each cell seeds.n_seeds times; run k (position in the expanded list, M runs in all) gets seeds.spawn_key = [k], the child SeedSequence(root_seed).spawn(M)[k]; deterministic runs keep spawn_key null, so equal configs hash equal. (3) Output files are results/<family>/<family>_<index:04d>_<hash12>.{npz,json,_params.md}, family = run.id or the config file stem; skip-if-done looks up any '*_<hash12>.json' and compares the full SHA-256. (4) Only status ok with all recorded outputs present and matching their SHA-256 is complete; failed, timeout and dry-run records are rerun or ignored. (5) The record is written after the outputs; the manifest.csv journal is written by the parent only. (6) workers = 1 runs in-process; workers > 1 uses a spawn pool; the thread variables are set in the parent before the pool starts and again in the initializer; worker log records reach the parent through a queue handler; a heartbeat with ETA is logged every 10 runs. (7) A task is 'module:function' called as task(cfg, deadline); the wall-time limit is cooperative (the task raises RunTimeout). (8) Relative config paths resolve from the repository root first, then the cwd; a relative output.dir is under the repository root.
Reason:          sections 6.6, 10.3, 10.4 and Table 6.2 fix the behaviour (atomic writes, hash keys, statuses, one thread per library, spawn-safe plain dicts) but not these details.
Options:         seeds as a separate axis for deterministic runs; nested spawn keys (cell, seed); a pool of one worker.
Chosen:          as above   Default from: new
Evidence:        plan 6.6 (SeedSequence.spawn(n), spawn key stored), 10.3, 10.4 (Run engineering), 6.5 (Table 6.2: seeds as an axis of the noisy runs).
Test:            test_runner part 1, test_provenance.
Status:          default adopted (to be confirmed by the user at the 1a-ii report)
Commit/tag:      entry added in 7f48642

## DL-069  Seed axis and spawn keys (amends DL-068)    [ID: ]
Date:            2026-10-14        Author:
Decision:        (1) the seeds.n_seeds expansion applies to every stochastic run.kind: mf_noisy now, and the network kinds when they are added at MS5. Deterministic mf is one run with spawn_key null. (2) A stochastic run with seed index s (0 to n_seeds-1) gets seeds.spawn_key = [s], the child SeedSequence(root_seed).spawn(n_seeds)[s]. The same seed index therefore gives the same stream in every sweep cell: common random numbers across cells. Different seed indices give independent streams. (3) The streams are identical across cells only as far as the integration consumes them in the same way (same noise.dt_tau and the same order of draws); cells with different durations share a common prefix.
Reason:          the user chose common random numbers across sweep cells. DL-068 item (2) gave run k the key [k], k being the position in the cell-major list; that makes every cell's stream independent, not common. The code at commit 7f48642 still behaves as DL-068 (2) says; the change to the new rule is made in sub-step 1b-i, with a test. Skip-if-done is unaffected: it matches on config_hash (spawn_key is part of the hash), not on the file index.
Options:         (a) keep [k]: independent streams per cell; (b) [seed_index]: common random numbers.
Chosen:          (b)   Default from: new (user choice 2026-10-14)
Evidence:        plan 6.6 (SeedSequence.spawn(n), spawn key stored), 10.4 (Seeds in Numba), Table 6.2 (seeds as an axis of S5, S11). Amends DL-068 item (2); DL-068 is not edited.
Test:            test_runner (1b-i): same spawn_key across cells at equal seed index, distinct across seed indices; deterministic mf has spawn_key null.
Status:          default adopted; code change pending (1b-i)
Commit/tag:      entry added in e7fbbe1

## DL-070  spawn_key = [seed_index] in the runner (implements DL-069), and the F4 noise-band caveat    [ID: ]
Date:            2026-10-14        Author:
Decision:        (1) build_plan gives a stochastic run with seed index s the key seeds.spawn_key = [s] (it was [k], k the position in the cell-major list). The same seed index has the same key, and so the same SeedSequence child, in every sweep cell; different indices differ. Deterministic mf keeps spawn_key null. config_hash is unchanged in form; stochastic cells hashed at 7f48642 (key [k]) get new hashes where k != s, so no earlier noisy result is reused. Inserting a sweep value, or raising n_seeds, leaves every existing cell's hash unchanged (the file index in the name does change; skip-if-done matches on the hash). (2) CAVEAT, recorded for the noise band on F4 and the noisy-subgrid agreement on F5 (RB2): with common random numbers the noise realisations are shared along the swept axis, so the band across eps (T_ramp) is correlated along eps. The band at one eps is still a spread over independent seeds, but neighbouring eps points are not independent samples; the band's wiggles along eps, and any count of agreeing cells across a noisy sweep, must not be read as independent evidence. Cells with different T_ramp or duration share a stream only as far as the integration consumes it in the same way (DL-069 item 3), so the correlation is expected, not measured.
Reason:          the user chose common random numbers in DL-069 (b); DL-069 said the code change was made in 1b-i. The caveat follows from the choice and is not a new decision.
Options:         (a) keep [k]; (b) [seed_index] (chosen in DL-069).
Chosen:          (b)   Default from: DL-069 (user choice 2026-10-14)
Evidence:        DL-068 item (2), DL-069; plan 6.6, Table 6.2 (S5, S11), RB2, F4. No measurement of the correlation exists; the statement is reasoned, not tested.
Test:            test_runner (1b-i): keys per seed index and per cell, stream equals SeedSequence(root).spawn(n_seeds)[s], hashes stable under an inserted sweep value and a larger n_seeds, deterministic mf null key.
Status:          default adopted; implemented in 1b-i
Commit/tag:      entry added in fcb739e

## DL-071  M3-vs-M2 tolerance of 1e-2 was set after observing the error (UNVERIFIED)    [ID: ]
Date:            2026-10-14        Author:
Decision:        the test-level tolerance in test_models_3d::test_m3_with_tiny_tau_d_tracks_m2 (1e-2 absolute on r and v, M3 at tau_d = 1e-3 tau against M2) was chosen after the observed error of 6e-3 was seen, as about 1.6 times that value. It is therefore not an independent check threshold. The convergence assertion (error at tau_d = 1e-4 below a fifth of the error at 1e-3) was designed before it was run and does not depend on the 1e-2 value.
Reason:          section 10.5 asks for "a stated tolerance" and gives no value (DL-061). The order of events is recorded so that the 1e-2 is not read as a pre-set criterion.
Options:         -
Chosen:          1e-2 kept   Default from: DL-061
Evidence:        none beyond the observed 6e-3 from the 1b-i run; plan 10.5.
Test:            test_models_3d (1b-i).
Status:          UNVERIFIED; recorded at 1b-ii at the user's request
Commit/tag:      entry added in 2cb7842

## DL-072  Mean-field driver readings (mode D, mode N, wall limit, retry)    [ID: ]
Date:            2026-10-14        Author:
Decision:        (1) Samples: a sample at time t includes any delta0 kick applied at t; the kick is at t_on in modes D and N alike. (2) Mode D: piecewise segments between 0, the path breakpoints inside the run, and the end (baseline + ramp end + hold); t_eval holds the 1 ms grid points of each segment (the segment end is added to carry the state on), no dense_output. A DOP853 failure (solve_ivp status != 0) restarts the whole run once with Radau at the same tolerances; the record flags retried_with_radau, first_failure and solver. A failure of Radau, or a RunTimeout, is not retried. (3) Wall limit: mode D checks the deadline every 256 right-hand-side calls and raises RunTimeout (no change to the numerics); mode N checks it between kernel chunks of 2000 output samples (2e5 steps). (4) Mode N noise: dv = f_v dt + sigma dW, sigma = noise.sigma * noise.sigma_factor, dW a Wiener increment (sd sqrt(dt)), noise only on v. This convention is UNVERIFIED: section 6.4 says "additive white noise on v" without fixing it; the OU test of 10.5 (variance sigma^2/(2k)) is consistent with it. Heun with the same increment in predictor and corrector (additive noise). The generator is numpy PCG64 seeded from the SeedSequence child with the stored spawn key, passed into the kernel; mode N refuses to run with noise.sigma or seeds.spawn_key null. (5) Mode N starts at the fixed point at t = -discard_s (the path is constant before t_on) and the discard is not returned. (6) The kernel has a validation drift (kind 2: dv/dt = -k v) for test_noise; it shares the Heun and noise lines with the model kinds. (7) K8/S3 initial values: run_mf(cfg, y0=...) and devalle_fig3_state() give R = S = 5 Hz (0.05 per tau), V = 0 (Table 7.1, K8). No config key selects them yet; choosing one is left to the user. (8) RunTimeout moved to mprsurge/errors.py (re-exported from run.py) so that `python -m mprsurge.run` and a task catch the same class. (9) Run record field numba_cache_cleared, null until make_all.ps1 sets it. (10) Heartbeat: unchanged (every 10 runs, never after the last), so a sweep of fewer than 10 runs logs none; a test records this. (11) Test-level values (UNVERIFIED unless the plan gives them): OU variance within 5% (estimate error about 1%); RB9a 0.5% is the plan's, measured as max difference over the max value of the variable.
Reason:          sections 6.2, 6.4 and 10.4 fix the scheme, the seeding, the retry and the limit but not these details.
Options:         wall limit by a parent hard kill; a chunked solve_ivp (changes the step sequence); noise written as sigma sqrt(2) dW or per unit time; a config key for the start state.
Chosen:          as above   Default from: new
Evidence:        plan 6.2, 6.4, 6.6, 10.4, 10.5, Table 7.1 (K8).
Test:            test_noise, test_simulate_mf, test_units (RB9a), test_runner part 2.
Status:          confirmed by the user at 1c. Item 4 accepted as UNVERIFIED: dv = f dt + sigma dW with t in units of tau, so sigma has units of v per sqrt(tau) (v is dimensionless); sigma is calibrated at MS5. Item 7: the start-state selector is deferred to MS2, when the S3 config is written. Item 10: heartbeat unchanged.
Commit/tag:      entry added in 2cb7842

## DL-073  Step-onset filter bias in envelope_growth (OPEN, UNVERIFIED)    [ID: ]
Date:            2026-10-14        Author:
Decision:        none. Finding only. With a ring starting as a step at 1 s (40 Hz, true decay 6.14 per s, band 25-100 Hz, threshold 0.1), the D8 fit (threshold crossing, first 10 cycles) gives rate -3.36 +/- 0.35 per s (plain OLS SE, n = 256); the same ring starting at the record start gives -6.08 +/- 0.05. The zero-phase band filter smears the onset over about 20 ms, and the window starts inside that transient (t_start 0.984 s). The sign and the 2-SE test are unaffected here; the magnitude is biased by about 45%.
Reason:          found at 1d while restoring the slowly damped ring test to the D8 window. In 1c the test had been moved to start at the record start, which hid the bias; it is restored and the rate-accuracy assertion is a strict xfail (test_surge_metrics) pointing here.
Options:         candidate fixes, none chosen: (a) start the fit a stated number of filter lengths after the crossing; (b) fit the envelope of a causal or one-sided filter; (c) take the analytic signal of the unfiltered v for the fit; (d) report the bias as a limitation and use rates only for sign and class; (e) calibrate on synthetic step-onset rings.
Chosen:          none   Default from: -
Evidence:        tests/test_surge_metrics.py (ring, lead_s = 1.0), measured at 1d. Affects K7 (growth rate near the Hopf point, if read from the envelope) and D8 (Table 2.1 growth-rate rule). Not tested on M3 output.
Test:            xfail test_slowly_damped_ring_rate_matches_true_decay_after_step_onset.
Status:          open, UNVERIFIED; awaiting the user's choice
Commit/tag:      entry added in 538f205

## DL-074  K7 Hopf value not reproduced at 1d; BifurcationKit works on Windows (OPEN source issue)    [ID: D23]
Date:            2026-10-15        Author:
Decision:        none on D23, which stays undecided until the user rules; no fallback. Findings: (1) Julia 1.10.11 with BifurcationKit 0.8.7 installs, precompiles and runs Hopf detection, the Hopf normal form and periodic-orbit continuation (orthogonal collocation, Collocation(40, 4)) on Windows (smoke test, commit 538f205). (2) Under the section 3.1 equations at ref_ceni (eta_bar 1, J -20, Delta 0.05, tau 10 ms) the Hopf point is at tau_d = 4.12 ms (tau_d/tau = 0.4121), frequency 21.0 Hz, not the 4.95 +/- 0.05 ms of K7. (3) BifurcationKit agrees with an independent Python check: the sign change of the largest real eigenvalue of mpr3d.jacobian_3d at the same fixed point is at 4.12 ms. At 4.95 ms the fixed point is already unstable (largest real part +0.028 per tau). The tool is therefore not the cause; the discrepancy lies in the K7 value or in the equations or parameters it is tested against.
Reason:          K7 rests on one source (Ceni, arXiv v1 only; RB-item 3 PARTIAL; CP1), and C15 is open: Delta 0.05 (caption) vs 0.5 (text). Delta = 0.5 would exceed the 0.1453 limit of K9 and allow no Hopf at all, so it cannot reconcile the value (reasoned from K9, not run here). Not investigated further at 1d.
Options:         left to the user: re-read the source for the 4.95 ms point and its parameters; test other readings of C15 or of the J mapping; keep 4.12 ms as the model's value and restate K7; none chosen.
Chosen:          none   Default from: -
Evidence:        results/A5/smoke (git-ignored; fixture in tests/fixtures/julia); plan Table 7.1 K7, C15, CP1, D23, DL-023. Supercritical check, convention-free: squared amplitude of v on the periodic-orbit branch is linear in tau_d/tau - tau_H/tau over the first 8 points (x up to 0.0098; slope about 53 per unit tau_d/tau, intercept within 1e-3 of zero, max residual 2e-4); at x = 0.030 the linear fit has residual 5e-3. Direct integration of M3 from a perturbed fixed point (DOP853, 1e-10) decays to the fixed point at tau_d = 4.0 ms and settles on a cycle at 4.3 ms with squared peak-to-peak 0.951 against 0.95 predicted by the slope. This is an attracting cycle past the Hopf point with no hysteresis in the two points tried, consistent with a supercritical Hopf given l1 = +0.395 whatever its sign convention. The Floquet multipliers themselves are not in the smoke output (the Julia script did not write them) and were not computed; the stability statement rests on the integration.
Test:            none; test_replication (K7) at MS5 will fail on the 4.95 ms criterion unless K7 is resolved.
Status:          open, UNVERIFIED; awaiting the user's ruling on K7 and D23
Commit/tag:      entry added in 94f0b85

## DL-075  D23 ruled: BifurcationKit.jl confirmed; K7 source check    [ID: D23]
Date:            2026-10-15        Author:
Decision:        (1) D23: the user rules BifurcationKit.jl confirmed; the DL-023 default is kept and no fallback (WSL2 + PyCoBi/AUTO-07p, or S4 alone) is taken. (2) K7 source check, done by the user in review: Ceni et al. (arXiv 1908.07954 v1; Chaos 30, 053121) Eq. 5 matches plan 3.1, including the placement of tau and the sign convention. Our critical heterogeneity at eta_bar = 1, maximised over J, is Delta_c = 0.14531 (J about -5.3), matching the paper's 0.1453. With the stated Fig. 1 parameters (eta_bar = 1, Delta = 0.05, J = -20, tau = 10 ms) the Hopf is at 4.12 ms (21.0 Hz); the paper's 4.95 ms would need Delta about 0.056 or J about -22.7. Delta = 0.5 was run in review and gives no Hopf. The paper's Hopf formulas were garbled in extraction and were not checked (UNVERIFIED). The K7 value 4.95 +/- 0.05 ms is therefore not reproduced from the paper's own parameters. (3) Re-run at 1e from the repository code, as a cross-check of the numbers in (2): Hopf at 4.1209 ms at the Fig. 1 point; 4.948 ms at Delta = 0.056 (J = -20); 4.950 ms at J = -22.7 (Delta = 0.05); no Hopf at Delta = 0.5; largest Delta with a Hopf at eta_bar = 1 is 0.14530 at J = -5.25 on a J grid of step 0.25 and a bisection to 1e-5 (a coarser search than the review's). The Jacobian of mpr3d.jacobian_3d was used, tau_d searched from 0.2 to 50 ms.
Reason:          closes the D23 question left open in DL-074; the K7 source issue stays open in the form below.
Options:         D23: keep BifurcationKit (chosen) or the fallbacks of DL-023. K7: see DL-076.
Chosen:          D23 kept   Default from: DL-023 (user ruling 2026-10-15)
Evidence:        DL-074; user review; item (3) above from the 1e run. Plan Table 7.1 K7, C15, CP1, D23.
Test:            none.
Status:          D23 decided; the K7 source issue remains UNVERIFIED and open (arXiv v1 only, PARTIAL)
Commit/tag:      entry added in b3d914b

## DL-076  Draft configs/replication.yaml; K7 departure; K4 tail fraction    [ID: D34]
Date:            2026-10-15        Author:
Decision:        DRAFT, not frozen, pending the user's approval; tolerances-frozen is not tagged. configs/replication.yaml carries Table 7.1 as written, with these departures and gaps, each flagged in the file: (1) K7 tau_d^H = 4.12 ms +/- 0.05 ms, the A4-derived value, in place of the paper's 4.95 ms (DL-075); UNVERIFIED. The 3 ms (decays) and 8 ms (sustained) conditions are kept as in Table 7.1. (2) K10's lower end is written as the A4 Hopf value, not the fixed 4.95 ms of Table 7.1, as a consequence of (1); UNVERIFIED, for approval. (3) K4 tail-fit fraction 0.1, UNVERIFIED (ms1_plan: confirmed by the user at 1e after the count below); the start state is not chosen. (4) K5 has no operational definition (open, ms1_plan); stored as null. (5) K6 optional and not entered (Table 7.1). (6) K9's 0.1453 +/- 0.002 and K1, K2, K3, K8, K10, K11 are copied from Table 7.1; none is invented.
Reason:          section 7.1 and D34 require the tolerances in configs/replication.yaml, frozen at the end of MS1.
Options:         K7: 4.12 ms with a flag (drafted); keep 4.95 ms (would fail at MS5 by DL-074); restate K7 after a source re-check. K4 fraction: 0.05, 0.1, 0.2, from the count below.
Chosen:          drafted as above   Default from: user instruction 2026-10-15 (K7 value and flag); K4 fraction 0.1 from ms1_plan
Evidence:        K4 tail-cycle count, from the 3.1 M2 equations at eta_bar = -5, J = 15, Delta = 1, step I = 0 to 3: the post-step fixed point is a stable focus with lambda = -0.2318 +/- 5.7664i (period 1.090 tau, 3.96 cycles per e-fold). K3 has two stable states at I = 0 (a node at r = 0.0811 and a focus at r = 1.0306), so the start state is open (UNVERIFIED). The first-peak deviation of r from r* is 1.509 from the node and 0.348 from the focus. First peak below the fraction f of the first peak, and the cycles left in the tail to t = 40 tau: from the node, f = 0.05 at t = 15.2 (22.7 cycles), 0.1 at 12.0 (25.7), 0.2 at 8.7 (28.8); from the focus, 0.05 at 13.7 (24.2), 0.1 at 10.4 (27.2), 0.2 at 8.2 (29.2). With the window ending when the envelope reaches 1e-6 of the first peak, the tail holds about 43, 46 and 49 cycles (node) for f = 0.05, 0.1, 0.2. At f = 0.2 the deviation is still 0.07 to 0.3 in r, so nonlinearity may bias the fit; this is reasoned, not tested. The run length of S1 is not stated in the plan, so the window end is an assumption.
Test:            none at 1e; test_replication (MS2 onward) reads the file.
Status:          draft, UNVERIFIED, awaiting the user's approval before the freeze
Commit/tag:      entry added in b3d914b

## DL-077  1e fresh-context review of the MS1 diff: findings, none fixed    [ID: ]
Date:            2026-10-15        Author:
Decision:        none. A fresh-context subagent reviewed the MS1 diff (034a565..94f0b85) against the plan and DL-053..074 and found no blocking defect (fast suite 130 passed, 1 xfailed). Its real gaps are recorded here for the user to rule on; no code was changed at 1e. Reviewer-reported, not independently re-checked unless stated: (1) simulate_mf.py around lines 136-179: the per-segment solver messages are collected in msgs but the stochastic path returns message "ok" (line 320) and the record keeps only first_failure after a retry; plan 10.4 asks for the solver message in each record. I did not re-check whether the mode D path returns the collected message (line 179 returns a variable msg). (2) durations.baseline_s is read only by config and params (grep confirms no use in the integration); the baseline comes from path.t_on_s. model.J and model.eta_bar are ignored on ramp paths with a J path (path.J0 is used), while all of these enter config_hash, so --set durations.baseline_s=10 gives a new hash and an identical run. Not covered by a DL. (3) tests/test_fixed_points.py (K1) does not implement the DL-064 definition (20 r values on the A1 grid, one cell in both axes): its 20-r loop checks the formula against the double-root condition, and the grid check covers 4 J values and the eta_bar edge only. (4) run.py execute_job: P.find_complete can raise ProvenanceError outside the try block, which would abort a pool sweep; reachable only by a hash12 collision or a corrupted record. (5) Fixture provenance: tests/fixtures/julia/smoke.json records commit 464f1ec. That is correct: the smoke run was made at 464f1ec with the new files uncommitted, before commit 538f205 added them. I changed "dirty" from true to false in the fixture by hand, which is wrong for that run; DL-074's "commit 538f205" names the commit that added the script, not the run's commit. The Manifest SHA-256 matches the committed Manifest.
Reason:          sub-step 1e asks for real plan gaps only; fixing any of them is a change of behaviour or of a DL that needs the user's agreement.
Options:         for each of (1)-(4): fix in a later commit, or log a decision accepting the behaviour. For (2) a check that t_on_s equals baseline_s and J0 equals model.J, or removal of the dead keys from the hash. For (5): regenerate the fixture from a clean commit.
Chosen:          none   Default from: -
Evidence:        subagent report of 2026-10-15; grep for baseline_s in src; commit history.
Test:            none.
Status:          ruled 2026-10-15 by the user: (1) mode D solver messages fixed with tests (flags.solver_messages and the record message; test_simulate_mf, test_runner), (3) K1 test follows DL-064 (see DL-078), (5) fixture regenerated (DL-080). Known and accepted as non-blocking: (2) dead config inputs, to be wired at MS2 (durations.baseline_s, and the model.J / model.eta_bar versus path.J0 inconsistency), (4) a ProvenanceError in find_complete can abort a pool sweep, reachable only by a hash12 collision or a corrupted record.
Commit/tag:      entry added in b3d914b

## DL-078  K1 test follows DL-064; the cusp points are below one A1 cell (UNVERIFIED)    [ID: D34]
Date:            2026-10-15        Author:
Decision:        none beyond implementing DL-064. test_fixed_points now builds the A1 grid (eta_bar/Delta 241 points on [-10, 2], J/sqrt(Delta) 201 points on [0, 20]), takes 20 r values uniform on the r-interval where the K1 formula point lies inside the grid (r from 0.1434 to 1.0028), and asks for a grid node where the positive-root count changes within one cell (0.05, 0.1) of each formula point. Result: 18 of 20 points pass; the two points near the cusp of the fold curve (r = 0.279 and 0.324, J about 7.84 to 7.89, the cusp at r = (3/(4 pi^4))^(1/4) = 0.2965) have their nearest count-change node 2.1 to 2.6 cells away, because the gap between the two folds there is below one cell [reasoned, not tested]. The full 20-point test is therefore a strict xfail pointing here, and a second test covers the points with |r - r_cusp| >= 0.05 (18 points); that 0.05 is a test-level choice made after seeing which points fail (UNVERIFIED).
Reason:          DL-064 as written cannot pass at the cusp on the 241 x 201 grid. The first K1 test of 1b did not test this (review, DL-077 item 3).
Options:         (a) keep the split (done); (b) change the K1 definition at the freeze, for example by excluding the cusp neighbourhood; (c) finer grid near the cusp. (b) and (c) need the user's decision.
Chosen:          (a) for now   Default from: DL-064
Evidence:        test_fixed_points (K1 tests); plan Table 7.1 K1, A1 (grid sizes).
Test:            test_k1_all_20_points_... (xfail, strict), test_k1_points_away_from_the_cusp_..., test_k1_formula_points_are_double_roots.
Status:          open, UNVERIFIED; the K1 criterion in replication.yaml is unchanged
Commit/tag:      entry added in the commit that follows b3d914b (see git log)

## DL-079  Decisions at 1e: K4 fraction and start state, K10 lower end, K7 departure    [ID: D34]
Date:            2026-10-15        Author:
Decision:        the user decided: (1) K4 tail-fit fraction 0.1 confirmed (still UNVERIFIED as a value; DL-076 count). (2) K4 start state = the low-rate stable node (eta_bar = -5, J = 15, Delta = 1, I = 0: r = 0.0811, v = -1.962); updated 2026-10-15 at the user's instruction: the low-activity start state is sourced to MPR 2015 Sec. II.D (single source) and is no longer UNVERIFIED; K4-MF checks frequency and decay from the post-step linearisation, which does not depend on the start state. (3) K10's lower tau_d end is the A4 Hopf value, not 4.95 ms. (4) K7 tau_d^H = 4.12 +/- 0.05 ms as a documented departure from the paper's 4.95 ms (DL-074, DL-075), and the K7 operational definition of DL-064 are approved. K5 is still open, so the file stays a draft and tolerances-frozen is not tagged.
Reason:          closes the approval items of DL-076.
Options:         see DL-076.
Chosen:          as above   Default from: user decision 2026-10-15
Evidence:        DL-064, DL-074, DL-075, DL-076.
Test:            none at 1e.
Status:          decided; replication.yaml updated; freeze waits for K5
Commit/tag:      entry added in the commit that follows b3d914b (see git log)

## DL-080  Correction of DL-074's commit reference; Julia smoke fixture regenerated    [ID: D23]
Date:            2026-10-15        Author:
Decision:        DL-074 says the smoke test ran "at commit 538f205". That is the commit that added the script; the first run was made at 464f1ec with the new files uncommitted, and its fixture had "dirty" set to false by hand, which was wrong for that run. DL-074 is not edited. The fixture in tests/fixtures/julia was regenerated from a clean committed tree: bk_smoke.jl was run with HEAD = b3d914b and an empty git status, giving commit b3d914b3350c6a7bf41dfcbc4b41d80a7170d9da, dirty false, Julia 1.10.11, BifurcationKit 0.8.7, Manifest SHA-256 73ac380d3d7d06bbdfa7fea64c85abbb08c74aee489e87625464864cecfd53e5 (unchanged), Hopf 4.1209 ms. The fixture files are copied unedited (the CSV files are truncated to their first rows).
Reason:          review finding 5 (DL-077).
Options:         -
Chosen:          -   Default from: user instruction 2026-10-15
Evidence:        tests/fixtures/julia/smoke.json.
Test:            test_julia_io.
Status:          done
Commit/tag:      entry added in the commit that follows b3d914b (see git log)

## DL-081  K1 cusp points re-run with the grid spacing halved near the fold curve (Table 6.2 rule)    [ID: D31]
Date:            2026-10-15        Author:
Decision:        none; the K1 criterion is unchanged (a count-change grid node within one cell, 0.05 in eta_bar and 0.1 in J, of the formula point). The two points that failed in DL-078 (r = 0.2791 and 0.3244) were re-run on a local grid around each point (+-6 base cells) at the base spacing, at half spacing (0.025, 0.05) and, once outside the test, at quarter spacing (0.0125, 0.025). Base: both fail (nearest count-change node at -2.11 and +2.61 cells for r = 0.2791; -1.79 and +2.13 for r = 0.3244, in units of the eta and J cells). Half: both pass (-0.61 and +0.61 cells; -0.29 and +0.13). Quarter: both pass (-0.36 and +0.36; -0.04 and -0.12). All 20 points therefore pass with halved spacing near the fold curve. Table 6.2's resolution rule asks whether halving moves the boundary by less than one cell; that is not what was measured here (the nearest node moved by 1.5 cells in eta and 2.0 cells in J for both points between base and half spacing), so the rule is not claimed to be met at the cusp. The two cusp points need the finer grid for K1 to pass [reasoned: the fold-to-fold gap is below one cell there].
Reason:          requested by the user after DL-078.
Options:         base grid with the cusp excluded (DL-078 b); halved spacing near the fold curve (run here); finer grid at A1.
Chosen:          none   Default from: -
Evidence:        tests/test_fixed_points.py (test_k1_cusp_points_fail_at_the_base_spacing_and_pass_when_halved, test_k1_all_20_points_pass_on_the_a1_grid_with_halved_spacing_near_the_fold_curve); plan Table 6.2 note, D31. The strict xfail of DL-078 is removed because all 20 points pass at half spacing; the 18-point base-spacing test is kept as the base-grid statement.
Test:            as above.
Status:          K1 passes at half spacing; whether A1 itself runs at half spacing near the cusp is for the user to decide before the freeze
Commit/tag:      entry added in the commit that follows 2c14881 (see git log)

## DL-082  K5 operational definition (own, UNVERIFIED) and test    [ID: D34]
Date:            2026-10-15        Author:
Decision:        K5 is entered, blocking in G0, from the user's instruction of 2026-10-15. Source: MPR 2015 Sec. II.D, single source; the paper gives no burst count or transient length. Forcing: I(t) = 3 sin(pi t / 20) from t = 0, J = 15, eta_bar = -5, Delta = 1, started in the low-activity state (the stable node of K3 at I = 0, r = 0.0811). The mapping of the paper's time unit to our nondimensional tau = 1 is UNVERIFIED. Operational definition, UNVERIFIED and our own: a burst is r crossing the midpoint between the low and high states, taken as the stable node and the stable focus at I = 0 (r = 0.0811 and 1.0306; midpoint 0.5559; this reading of "low and high states" is ours). Pass: after a transient of 2 periods (80 tau, from Table 7.1's 2-period transient), each of the next 5 periods (period 40 tau) contains one up-crossing and one down-crossing, and successive up-crossings are 40 apart within 0.1 tau. The 0.1 is UNVERIFIED and our own: one output step (1 ms at tau = 10 ms, base.yaml dt_out_ms), chosen with the measured result in view. Measured: up-crossings at 87.785, 127.785, 167.785, 207.785, 247.785 tau (spacings equal 40 to 1e-12), down-crossings 22.95 tau after each; the pass margin is therefore large and the tolerance is not tight.
Reason:          DL-064 left K5 open pending the user's source check; closes that item. The plan's Table 7.1 gives "one burst per period for 5 periods after a 2-period transient" without a burst definition or tolerance.
Options:         other burst definitions (a threshold on r, peaks of r); other tolerances.
Chosen:          as above   Default from: user instruction 2026-10-15
Evidence:        plan Table 3.1 and 7.1 K5, C21 (Fig. 2); tests/test_k5_definition.py (mean field, DOP853 1e-10, 0.1 tau output).
Test:            test_k5_definition (fast); test_replication (MS2) will run it through the runner.
Status:          UNVERIFIED; replication.yaml still a draft, tolerances-frozen not tagged
Commit/tag:      entry added in the commit that follows 2c14881 (see git log)

## DL-083  Freeze approvals: A1 spacing, DL-073 deferral, replication.yaml as written    [ID: D31, D34]
Date:            2026-10-15        Author:
Decision:        the user approved: (1) A1 runs at half grid spacing near the fold curve and the cusp (eta_bar/Delta step 0.025, J/sqrt(Delta) step 0.05 there; the base grid of plan 5.2 A1 elsewhere); the extent of the refined region is not fixed here and is set when A1 is written at MS2 (UNVERIFIED). Basis: DL-078, DL-081. (2) The DL-073 filter-bias fix is deferred to MS7; its strict xfail stays. (3) configs/replication.yaml as written at bd301ce: K1; K2; K3; K4 (tail fraction 0.1, low-rate node start); K5 (DL-082, with the 0.1 tau period tolerance); K7 at 4.12 +/- 0.05 ms with its operational definition (DL-064, DL-075); K10's lower end at the A4 Hopf value; K8, K9, K11 as in Table 7.1. Entries the file marks UNVERIFIED stay UNVERIFIED in the file; the approval fixes the tolerances, not their sources.
Reason:          closes the open items of DL-076, DL-078, DL-079, DL-081 and DL-082 before the freeze.
Options:         -
Chosen:          as above   Default from: user decision 2026-10-15
Evidence:        DL-073, DL-078, DL-081, DL-082.
Test:            none.
Status:          decided
Commit/tag:      entry added in the docs-only commit that follows the tag tolerances-frozen (tagged commit bd301ce)

## DL-084  Freeze: tag tolerances-frozen, SHA-256 of configs/replication.yaml    [ID: D34]
Date:            2026-10-15        Author:
Decision:        the annotated tag tolerances-frozen was created on bd301ce9fd3ca05d67020cb575c055148b3bdabc (the tagged commit; this entry is in a later, docs-only commit). SHA-256 of configs/replication.yaml: 667d3b788d1c7c5aebc716998d09746b685358f326334aae87591924908819a5, taken on the LF text as committed (.gitattributes sets eol=lf; `git show bd301ce:configs/replication.yaml | sha256sum`). On this Windows machine the working copy had been written with CRLF and hashes to 55c049715d9884b57e0c02f0be27c7a55211240c8517070bbeea6e22f42d7ca6; the working copy was converted to LF (no content change) so that it hashes to the frozen value, and a fresh checkout gives LF. Anything that hashes the file (provenance, criteria_sha256) must hash the LF text. Checks before the tag: fast suite 136 passed, 1 xfailed (the DL-073 xfail), run on bd301ce with a clean tree; a real --dry-run (configs/base.yaml, output.dir results/dryrun_freeze) wrote a run record with status dry_run and git.commit bd301ce9fd3ca05d67020cb575c055148b3bdabc, dirty false. K5 is entered (DL-082), so the freeze is not blocked by it. Any later change to the tolerances needs a new entry (plan 7, D34) and a report in the paper.
Reason:          Table 11.1 MS1 gate and plan section 7: tolerances are frozen at the end of MS1, before the MS2 replication runs.
Options:         -
Chosen:          -   Default from: user instruction 2026-10-15
Evidence:        git tag tolerances-frozen; DL-083.
Test:            -
Status:          done
Commit/tag:      tag tolerances-frozen on bd301ce; this entry in the following docs-only commit

## DL-085  MS2 rulings: A1 refinement extent, deferrals, config checks, S1 path kinds    [ID: D31, D34]
Date:            2026-10-15        Author:
Decision:        the user ruled on the MS2 questions of docs/ms2_plan.md: (1) A1 refines to half spacing (0.025 in eta_bar/Delta, 0.05 in J/sqrt(Delta)) in a band of +-4 base cells in eta_bar along the whole formula fold curve, plus a box of +-10 base cells in eta_bar and J around the cusp; the widths are UNVERIFIED and the user's. A1 stores the Table 6.2 halving check (boundary shift in cells) along the fold and at the cusp as a recorded field, with no pass/fail test. (2) The K8/S3 start-state selector is deferred to MS5, with a one-line note in the MS2 gate report. (3) Configs with path.t_on_s different from durations.baseline_s, or path.J0 different from model.J, are rejected. (4) New path kinds I_step and I_sin with optional keys, so existing config hashes are unchanged. (5) G0 part 1 follows Table 11.2, with no tolerance change. (6) No FS1 at MS2. (7) The A2 fit goes in analysis/ring.py. (8) The UNVERIFIED values in replication.yaml (K4 tail fraction 0.1, K5 burst midpoint and 0.1 tau tolerance, the tau mapping) are used as written, and results that depend on them are labelled UNVERIFIED.
Reason:          closes the open questions of the MS2 plan; (1) completes DL-083 item 1, (3) closes DL-077 item 2, (2) carries DL-071 item 7.
Options:         see docs/ms2_plan.md before this commit.
Chosen:          as above   Default from: user decision 2026-10-15
Evidence:        DL-071, DL-077, DL-078, DL-081, DL-083; plan 5.2 A1, Table 6.2 note, Table 11.2 G0.
Test:            none yet (tests are specified in docs/ms2_plan.md, steps 2a to 2e).
Status:          decided
Commit/tag:      landed in 2e421c2

## DL-086  MS2 2b (A1): run kind a1, reading choices, results at base and half spacing    [ID: D31, D34]
Date:            2026-10-15        Author:
Decision:        none beyond implementing DL-085 item 1. Reading choices made while building A1, all ours and UNVERIFIED, for the user to confirm: (1) A1 is a runner task, run.kind = a1 (RUN_KINDS and TASKS), so it has a config hash, a run record and criteria_sha256 of the frozen replication.yaml; the grid (241 x 201, Delta = 1) and the DL-085 widths are constants in analysis/bifurcation.py, not config keys, so they are outside the hash. The runner names its output A1_0000_<hash12>.npz; scripts/run_A1.py publishes a byte-identical copy as results/A1/a1_fixedpoints_2d.npz and checks its SHA-256 against the record. (2) The refined region is the set of half-spacing nodes within 4 base cells in eta_bar of each formula fold (on every half-spacing J row with J >= J_cusp = 7.796) union the nodes within 10 base cells in eta_bar and 10 base cells in J of the cusp (eta_bar = -1.732, J = 7.796); the lattice is 481 x 401 and its even-even nodes are the base nodes. (3) K1 edge = the DL-064/DL-078 definition (a node whose root count differs from the next node in eta or J), unchanged cell (0.05, 0.1) from replication.yaml; at half spacing only nodes in the refined region are compared. (4) K2 uses the discriminant (lambda1 - lambda2)^2 of the highest-r root on each J row; K2 rows are those with eta_f(J) inside [-10, 2] (J from 1.0 to 19.8 at base spacing); pass = a sign-change interval with an end node within 0.05 of eta_f. (5) The halving record: along the fold, on each base J row the count-change position (midpoint of the node pair) of each fold at base and at half spacing, shift = (base - half)/0.05; at the cusp, the lowest J with three roots in the cusp box and the mean eta of the nodes there, base against half. Recorded in the npz, no pass/fail test. (6) C9 record: a node (stable or unstable) exists, yes.
Results (npz and run record, fast suite 157 passed, 1 xfailed): K1 18/20 at base spacing (the two cusp points fail, as in DL-078) and 20/20 at half spacing (DL-081). K2 189/189 rows at base spacing, 261/261 rows at half spacing (each with exactly one sign change at base). K3 at the base node (-5, 15): saddle, stable_focus, stable_node; the node is not in the refined region (the roots do not depend on the spacing). C9: node region exists (28532 grid nodes carry a node, J >= 1.0, all with J > 2 pi^2 r*), and the highest-r root is a node somewhere, consistent with the reasoning in plan C9. Halving: along the fold the boundary moves by 0.25 base cells at all 236 resolved fold positions, which is the quantisation floor of the midpoint estimate (below one cell, so Table 6.2 is met along the fold). At the cusp it is not met: the wedge tip moves 2.5 J cells (J 8.20 to 7.95, formula 7.796) and 1.5 eta cells (-1.85 to -1.775, formula -1.732), as DL-081 found for K1.
Reason:          2b of docs/ms2_plan.md; DL-083 item 1 and DL-085 item 1 left the extent and the record to A1.
Options:         widths and halving definition as in DL-085; other readings of (4) and (5) possible.
Chosen:          as above   Default from: DL-085
Evidence:        DL-064, DL-078, DL-081, DL-085; plan 5.2 A1, Table 6.2 note, Table 7.1 K1 to K3, C9.
Test:            tests/test_fixed_points.py (test_a1_*, fast).
Status:          done; readings (1) to (5) UNVERIFIED; the cusp halving is recorded, not claimed met
Commit/tag:      165b62f

## DL-087  A1 grid sizes and refinement widths enter the config hash and the run record    [ID: D31, D34]
Date:            2026-10-15        Author:
Decision:        none beyond follow-up to DL-086 (1), which recorded the grid and the DL-085 widths as constants outside the hash. They now live in config.A1_GRID (n_eta 241, n_J 201, eta_range, J_range, band_cells 4, box_cells 10); analysis/bifurcation.py takes its constants from it; hash_view adds them under "a1_grid" when run.kind = a1, and run_a1 writes them to the record flags. No config key was added (the plan lists none), no value changed, and hashes of every other run kind are unchanged. The hash of an a1 run changes once (the old A1 record is superseded, the result is the same; results/A1 was regenerated).
Reason:          a change of grid or width would otherwise give the same hash and a stale "already complete" skip.
Options:         config keys (needs a schema change; not done).
Chosen:          as above   Default from: user instruction 2026-10-15
Evidence:        DL-085, DL-086.
Test:            tests/test_fixed_points.py: test_a1_grid_and_widths_change_the_hash_and_other_kinds_are_unchanged, test_a1_record_carries_the_grid_and_widths; the A1 K1 to K3 tests pass unchanged.
Status:          done
Commit/tag:      8ec1bde

## DL-088  MS2 2c (S1): path kinds I_step and I_sin, run kind s1, K4 and K5 runs    [ID: D34]
Date:            2026-10-15        Author:
Decision:        none beyond implementing DL-085 item 4. Reading choices made while building S1, all ours, for the user to confirm: (1) I_step: I = I_drive for t < t_on, I_drive + I_amp from t_on; I_sin: I_drive + I_amp sin(2 pi (t - t_on)/period) from t_on. One new optional key, path.I_period_s (absent from base.yaml, in the hash only when given, so every existing hash is unchanged; BASE_HASH test passes); I_sin requires it and no other path accepts it. K5 uses 0.4 s = 40 tau at tau = 10 ms, so omega = pi/20 (the tau mapping stays UNVERIFIED, DL-082). Both paths keep eta_bar, J, Delta at the model values and need no eta path (require_eta_path skips them); they are in neither RAMP_PATHS nor J0_PATHS, so DL-085 item 3 does not apply to them. (2) The S1 point is bistable, so the default start (the unique stable fixed point) raises. The start-state selector is deferred to MS5 (DL-085 item 2), so no config key was added; instead a new run kind s1 (RUN_KINDS, TASKS) calls run_mf with y0 = the stable node at I = I_drive, and fails if there is not exactly one. The start state is the I = I_drive node for I_step too (meta I_start), not the node at I(0) = 3. (3) solver.delta0 = 0 in S1.yaml (no kick, 'the same state' for K4 and K5). (4) durations.hold_s = 2.8 s = 280 tau for both runs: K5 needs 7 periods; the K4 length is our choice and A2 (2d) may extend it. (5) K5 is the same S1.yaml with --set path.name=I_sin --set path.I_period_s=0.4; no second config file, no driver script.
Results (results/S1/, DOP853 rtol 1e-10, dt_out 1 ms; records ok): K5 UNVERIFIED definition and 0.1 tau tolerance, unchanged: up-crossings of r = 0.5559 at 7.785, 47.785, 87.785, 127.785, 167.785, 207.785, 247.785 tau, down-crossings 22.95 tau after each; one up and one down in each of the 5 checked periods; successive up-crossings 40 within 9e-13 tau (tolerance 0.1): pass. K4 step response, summary only: start r = 0.0811, v = -1.962; first peak r = 2.867 at t = 2.8 tau, then peaks at 4.1, 5.3, 6.4, 7.6 tau (r = 2.37, 2.08, 1.87, 1.75), decaying to the I = 3 stable focus r = 1.3732 (final r = 1.3732 at 280 tau). The K4 frequency and decay fit against the linearisation is 2d (A2), not run.
Reason:          2c of docs/ms2_plan.md.
Options:         a start-state config key (a schema change, MS5); making the default start pick the low node (would pre-empt the MS5 selector).
Chosen:          as above   Default from: DL-085
Evidence:        DL-079, DL-082, DL-085; plan 6.5 (Table 6.2 S1), Table 7.1 K4 and K5.
Test:            tests/test_ramps.py (step and sinusoid values, key rules), tests/test_runner.py (test_s1_*: K4 run with record and start state, K5 definition on the runner output), tests/test_k5_definition.py unchanged.
Status:          done; K5 pass on UNVERIFIED definition and tolerance; readings (1) to (5) UNVERIFIED
Commit/tag:      f0c16fe

## DL-089  MS2 2d (A2): analysis/ring.py, run kind a2, ring map and K4-MF check    [ID: D34]
Date:            2026-10-15        Author:
Decision:        none beyond implementing the 2d row of docs/ms2_plan.md and DL-085 item 7. Reading choices made while building A2, all ours and UNVERIFIED, for the user to confirm: (1) A2 is a runner task, run.kind = a2 (RUN_KINDS, TASKS), config configs/A2.yaml (K4 point and I_step as in S1), driver scripts/run_A2.py publishing results/A2/a2_ring_map.npz (byte-identical copy, SHA-256 checked against the record). It reads the published A1 and S1 results (the complete run of configs/A1.yaml and configs/S1.yaml as written, found by hash) and records their npz SHA-256 in the run record. The fit window end t = 40 tau (config.A2_WINDOW, DL-076 and the user's instruction) and the primary band enter the a2 config hash (as DL-087 did for A1); the upstream results do not, so a changed S1 or A1 result with an unchanged A2 config is not detected by the skip rule except through the recorded SHA-256s. (2) K4 tail: the initial jump is the first local maximum of |r - r*| (r* = the I = 3 focus), the tail starts at the first later local maximum below 0.1 of the jump (the envelope is read from successive extrema), and ends at t = 40 tau. The fit is y = c + exp(-a t)(A cos wt + B sin wt) by least squares on all samples (dt_out 1 ms = 0.1 tau), offset c free; compared with the eigenvalue of the M2 Jacobian at the post-step focus. Pass = frequency and decay relative errors both within 0.02 (replication.yaml K4, unchanged). hold_s of S1 (280 tau) was not changed; no extension was needed. (3) Ring map: over every root of the A1 base grid labelled stable_focus (per root slot, three slots), lambda = eigenvalue of the Jacobian at that root; f_Hz = 1000 omega/(2 pi tau_ms) (= 100 f_tau at tau = 10 ms), decay rate = -Re(lambda) per tau, cycles per e-fold = Im(lambda)/(2 pi decay). The map uses the linearised growth rate, which is the exact envelope growth of the linear ring, with standard error 0, so D8 "damped only if negative by more than 2 SE" gives damped at every focus; it is not a fit to simulated rings. G = analysis.band_primary_hz (25-100 Hz); the refined A1 nodes are not used. g1_nondamped is false everywhere by construction.
Results (results/A2, hash f53757ab91ef): K4-MF pass. Fit: omega 5.7651, decay 0.23038 per tau (SE 0.0014 each); linearisation: omega 5.7664, decay 0.23179 (lambda = -0.2318 +/- 5.7664i, DL-076). Relative errors: frequency 2.1e-4, decay 6.1e-3 (tolerance 0.02 each). Tail from t = 11.4 to 40 tau (peak deviation 0.143 against 0.1 x 1.4939 = 0.149), 287 samples, 26.2 cycles; fit rms 1.5e-3. Ring map: 25727 stable-focus roots, ring frequency 0.24 to 153.4 Hz, 14793 of them with the ring in G; the largest cycles per e-fold inside G is 5.10, so no damped ring in G reaches 10 cycles per e-fold on the base grid (reasoned, not tested, against CP17's guess of "above 10 at small Delta"); no focus is non-damped.
Reason:          2d of docs/ms2_plan.md; G1 needs the envelope-growth sign (D8, CP17).
Options:         fitting simulated rings for the map (not done, costly); a config key for the window end (a schema change).
Chosen:          as above   Default from: DL-085 item 7, DL-076, DL-079
Evidence:        DL-076, DL-079, DL-082, DL-085, DL-088; plan 5.2 A2, Table 7.1 K4-MF, 4.3 G1, D8, CP17.
Test:            tests/test_ring.py (synthetic fit within 2%, tail rule, K4 linearisation, integrated step passes, map units, hash).
Status:          done; K4-MF pass; readings (1) to (3) UNVERIFIED
Commit/tag:      dad256f

## DL-090  A2 hash covers the SHA-256s of the upstream A1 and S1 results    [ID: D34]
Date:            2026-10-15        Author:
Decision:        none beyond follow-up to DL-089 (1), which recorded the upstream SHA-256s in the run record but left them out of the hash, so a changed A1 or S1 result with an unchanged A2 config would have been skipped as complete. hash_view now adds a2.upstream_sha256 = {A1, S1} (SHA-256 of the npz of the complete result of configs/A1.yaml and configs/S1.yaml as written; null if absent, in which case run_a2 raises) via analysis.ring.upstream_sha256s (memoised on path, mtime, size). run_a2 also refuses if the hashed view differs from what it read. No config key was added (the plan lists none), no value changed, and hashes of every other run kind are unchanged. The hash of the a2 run changes once (A2_0000_f53757ab91ef superseded by A2_0000_ac3c1fb033cc, same K4-MF result; results/A2 rerun).
Reason:          requested by the user after DL-089.
Options:         config keys for the upstream hashes (a schema change; not done).
Chosen:          as above   Default from: user instruction 2026-10-15
Evidence:        DL-087 (same pattern for A1), DL-089.
Test:            tests/test_ring.py: test_a2_hash_covers_the_upstream_result_hashes (a changed upstream file changes the hash, restoring it restores the hash), test_current_a2_result_passes_and_is_found_by_its_hash.
Status:          done
Commit/tag:      d353855

## DL-091  MS2 2e (A0): run kind a0, replication table K1 to K5, test_replication    [ID: D34]
Date:            2026-10-15        Author:
Decision:        none; no tolerance, definition or default changed. Implements the 2e row of docs/ms2_plan.md. Reading choices, all ours, for the user to confirm: (1) A0 is a runner task (run.kind = a0, configs/A0.yaml, analysis/replication.py), driver scripts/run_A0.py publishes results/A0/a0_replication.csv from the verified result npz (exit code 1 if a row fails). The record carries criteria_sha256 = the frozen hash. (2) Refusals: configs/replication.yaml must hash to the DL-084 value (667d3b78...), else ProvenanceError; each of the A1, A2, S1 (K4 run) and S1 (K5 run, --set path.name=I_sin path.I_period_s=0.4) results is read only after its npz SHA-256 is recomputed and equals the one in its run record; A1 and A2 records must carry the frozen criteria hash; the A2 record's A1 and S1 hashes must equal the files present. The S1 runs read no criteria file, so their record has no criteria hash. (3) The A0 hash covers the frozen hash and the four upstream SHA-256s (same pattern as DL-087, DL-090). (4) Row logic: K1 passes if all 20 r pass at half spacing (DL-081, DL-083; the base-spacing count 18/20 is reported in the row); K2 passes if every in-grid J row passes at base and at half spacing; K3 as A1; K4-MF re-evaluates the stored frequency and decay errors against the yaml tolerances; K5 is evaluated from the S1 K5 series with the DL-082 definition (midpoint of the I = 0 node and focus, 2 transient + 5 checked periods of 40 tau, 0.1 tau). (5) UNVERIFIED column per row, from the lists in analysis/replication.UNVERIFIED (DL-079, DL-082, DL-085, DL-086, DL-088, DL-089). (6) test_replication (slow) recomputes K1 to K5 on reduced grids (K1: local half-spacing lattices around the 20 points; K2: five J rows with eta_f inside the A1 range, J = 2, 5, 10, 15, 19, since eta_f(20) lies outside [-10, 2]; K3: classify_all; K4 and K5: one integration each) with the yaml tolerances, plus a check of the written A0 table. K7 to K11 are not included (MS5).
Results (results/A0, hash 724055e00481): K1 pass (20/20 at half spacing, 18/20 at base), K2 pass (189/189 base, 261/261 half), K3 pass (saddle, stable_focus, stable_node), K4-MF pass (frequency error 2.13e-4, decay error 6.09e-3, tolerances 0.02), K5 pass (one up and one down in each of 5 periods, spacing deviation 8.7e-13 tau, tolerance 0.1). All rows depend on UNVERIFIED items, listed in the csv.
Reason:          2e of docs/ms2_plan.md; G0 part 1.
Options:         -
Chosen:          as above   Default from: DL-084, DL-085
Evidence:        DL-064, DL-079, DL-081, DL-082, DL-084, DL-085, DL-086, DL-088, DL-089, DL-090; plan 5.2 A0, Table 7.1, 10.4, 10.5.
Test:            tests/test_a0.py (fast: hash coverage, frozen-hash refusal, upstream mismatch refusal, K5 logic, csv); tests/test_replication.py (slow).
Status:          done; rows pass on UNVERIFIED definitions and tolerances as marked
Commit/tag:      e430923

## DL-092  MS2 2f: fresh-context review of the MS2 diff, findings logged as known    [ID: D31, D34]
Date:            2026-10-15        Author:
Decision:        none. A fresh-context subagent reviewed d007378..HEAD against the plan and DL-085..DL-091 (read-only, nothing run). It found no wrong result, no change to the frozen tolerances and no blocking defect; nothing was fixed. Findings, reviewer-reported and not independently re-run: (1) tests/test_a0.py and tests/test_ring.py (fast suite) read git-ignored results/ files (A0, A1, A2, S1), so `pytest -m "not slow"` fails on a fresh clone or CI; fix would be marking them slow, skipping when absent, or tmp_path fixtures; no decision needed; not blocking at MS2, to fix before any CI. (2) The A2 ring map takes lambda from the Jacobian with standard error 0 (ring.py 130-145), so the D8 "negative by more than 2 SE" rule is vacuous there and test_ring_map_units_and_band's assert on g1_nondamped cannot fail; DL-089 says it is not a fit to simulated rings but not that the 2-SE rule is vacuous; user to decide before G1 uses the map: accept the linear ring or fit simulated rings. K4-MF is unaffected (it fits the S1 step response). (3) Table 6.2 / D31 halving is met along the fold and not met at the cusp (DL-086; DL-085 ruled recorded, not tested); the user decides whether that is acceptable under D31. (4) A0 K5 hard-codes path.I_period_s = 0.4 (K5_SETS) and takes I_amp from S1.yaml; the yaml forcing.I0 and forcing.omega are not compared with the run that produced the series (replication.py 21, 172-182); cheap assert, no decision, not live while the files are frozen. (5) config.hash_view reads files and imports analysis modules for kinds a2 and a0 (DL-090, DL-091, user-ruled); the memo key (path, mtime_ns, size) could miss a same-size rewrite within one mtime tick, theoretical. (6) configs/replication.yaml lines 1-3 still say "DRAFT / NOT FROZEN / status: draft"; the file is frozen by tag and hash (DL-084), and editing the header would change the hash, so it stays and the gate report says so.
Reason:          2f of docs/ms2_plan.md asks for real gaps only; fixing (1) to (5) is not needed for the gate, and (2), (3) need the user.
Options:         for each: fix in a later commit, or accept.
Chosen:          none   Default from: -
Evidence:        subagent report of 2026-10-15; docs/ms2_gate_report.md.
Test:            none.
Status:          open for (1) to (5), none blocking; (6) informational
Commit/tag:      the 2f commit (see git log)

## DL-093  User rulings on DL-092 (2) and (3): D8 2-SE rule scope, cusp halving accepted as a limitation    [ID: D8, D31, D34]
Date:            2026-10-15        Author:
Decision:        (a) In the A2 ring map the D8 "damped only if negative by more than 2 SE" rule reduces to Re lambda < 0, because the linearised standard error is 0 (DL-089 (3), DL-092 (2)). The 2-SE rule applies to fitted growth of simulated envelopes (A3, S2, S3); G1 at MS4 uses those. The linear ring map is not used as the G1 growth evidence. (b) The cusp halving (Table 6.2 / D31) is accepted as a recorded limitation (DL-086, DL-092 (3)). The cusp position is known to about 2.5 base J cells and 1.5 eta_bar cells; this is stated in any figure or claim about the cusp. No further refinement now.
Reason:          user rulings of 2026-10-15 closing DL-092 (2) and (3).
Options:         fit simulated rings for the map; refine the cusp further (neither chosen).
Chosen:          as above   Default from: user ruling
Evidence:        DL-086, DL-089, DL-092; plan 4.3 G1, D8, D31, Table 6.2.
Test:            none (docs only).
Status:          done; DL-092 (2) and (3) closed
Commit/tag:      the commit that adds this entry

## DL-094  User rulings on the MS3 plan: D-2, D-5, D-6, D-7, D-9; network gate; DL-092 status    [ID: D36, D12, T23, T24]
Date:            2026-10-15        Author:
Decision:        (1) D-2 accepted: provisional eta_bar path path.eta_start = 2.5 and path.eta_peak = 6.0, from the D12 rule with a placeholder eta_H = 4.0, recorded provisional (UNVERIFIED) until A4 (MS5); the placeholder is not an estimate of eta_H. (2) D-5: the allowance in the 9.2 launch rule is the upper end of the wall-time range of the matching Table 9.1 row, which is stated at 6 workers; launch if the prediction is <= 1.5 x that value and the total is within the D36 cap. (3) D-6: 3600 s per timing repeat (run.wall_limit_s for timing cells). (4) D-7: 6 workers for the extrapolation; the 8 and 10 worker timings are reported as measured. (5) D-9: add an M2 ramp timing cell (m2_ramp) so S2 is extrapolated from its matching family; the cell definition is the default in docs/ms3_plan.md. (6) The network gate is mean-field only until qif_network exists; network rows carry R5 estimates labelled not measured. (7) DL-092: its Status line was not edited. Of its items, (1) and (4) are fixed (commit 5eeaadf), (5) is left as is by ruling (config.hash_view unchanged), (2) and (3) were closed by DL-093, (6) is informational. D-1, D-3, D-4 and D-8 are not ruled; no default of them is applied.
Reason:          user rulings of 2026-10-15 on docs/ms3_plan.md.
Options:         see the D table in docs/ms3_plan.md.
Chosen:          as above   Default from: user ruling
Evidence:        plan 9.2, 9.3, Table 9.1, D12, D36, T23, T24; DL-092, DL-093.
Test:            none (docs only).
Status:          done for items 1 to 7; D-1, D-3, D-4, D-8 open
Commit/tag:      the commit that adds this entry
