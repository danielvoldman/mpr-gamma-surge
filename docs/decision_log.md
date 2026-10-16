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

## DL-095  User rulings on the MS3 plan: D-1, D-3, D-4, D-8    [ID: D36, T23, T24]
Date:            2026-10-15        Author:
Decision:        (1) D-1: one yaml per timing cell under configs/timing/, each a normal committed run file layered on configs/S5.yaml; --cell headline resolves to configs/timing/headline.yaml. No schema change and no new config key. (2) D-3: default. tau_d = 5 ms, J = -21 and the provisional path as in the headline, only Delta changed; "near the Hopf window" is recorded as not located and re-timed at MS5. (3) D-4: placeholder noise.sigma = 1e-3, recorded UNVERIFIED and labelled not calibrated. (4) D-8: default. Records of kind timing, outside RUN_KINDS, no skip rule, written to results/timing/, each carrying the commit, the dirty flag and the package versions.
Reason:          user rulings of 2026-10-15 on docs/ms3_plan.md.
Options:         see the D table in docs/ms3_plan.md.
Chosen:          as above   Default from: user ruling
Evidence:        plan 9.2, 6.4, Table 9.1; DL-094.
Test:            none (docs only).
Status:          done
Commit/tag:      the commit that adds this entry

## DL-096  MS3 3a: configs/S5.yaml, seven timing cells, analysis/timing.py    [ID: D36, T23]
Date:            2026-10-15        Author:
Decision:        none beyond implementing 3a of docs/ms3_plan.md with DL-094 and DL-095. configs/S5.yaml is the headline (P2, ref_devalle, T_ramp 120 s, linear, I = 0) with the provisional UNVERIFIED eta path 2.5 and 6.0 (placeholder eta_H = 4.0). configs/timing/ holds headline, delta_0.01, delta_0.6, p5_1000, radau_1e-12, mode_n (noise.sigma = 1e-3, UNVERIFIED, not calibrated) and m2_ramp; analysis/timing.py layers a cell over S5.yaml and reports tau simulated and the eta path status; nothing integrates. m2_ramp check (DL-094 D-9): the existing path_eta with model.type M2 is enough, no new path kind and no code in make_path. Its eta_start and eta_peak are the A1-formula folds at J = 15, Delta = 1 (-5.7435, -3.1361) minus and plus 1, status explicit; both ends have a unique stable fixed point. Cells resolve to tau simulated: headline 16,500; Delta cells 16,500; p5_1000 201,500; radau 16,500; mode_n 16,700; m2_ramp 101,500.
Reason:          3a of docs/ms3_plan.md.
Options:         -
Chosen:          as above   Default from: DL-094, DL-095
Evidence:        plan 9.2 step 1, 4.4, 6.2, CP14, D12, Table 6.2 S2.
Test:            tests/test_timing_cells.py.
Status:          done
Commit/tag:      the 3a commit

## DL-097  MS3 3b: scripts/time_one_run.py, timing functions, first run of the seven cells    [ID: D36, T23]
Date:            2026-10-15        Author:
Decision:        none; no default changed. Implements 3b of docs/ms3_plan.md with DL-094 and DL-095. The driver layers a cell over configs/S5.yaml, warms the Numba kernel (mode N only; timed apart, not in any repeat), times each repeat on its own (perf_counter around the integration call only), enforces 3600 s per repeat (D-6) through the solver deadline, and writes results/timing/<cell>.json (kind timing, D-8) with commit, dirty flag, package versions, OS, CPU, machine state before and after, eta_path_status and the sigma label. A repeat that is not ok ends the cell (remaining repeats not run); no solver setting is changed. Mode N runs with seeds.spawn_key [0] (seed index 0, as the runner). analysis/timing.py gained summarise_repeats, s_per_tau and extrapolate (arithmetic only, tested on a toy table; no family is extrapolated, 3e).
Results (median of 3 repeats, s per run / s per 1e4 tau): headline 119.3 / 72.3 (nfev 5.95e6; spread 3.7%); delta_0.6 97.1 / 58.9 (spread 3.3%); p5_1000 1945 / 96.5 (repeats 1822, 1945, 2109 s, rising; spread 14.8%); m2_ramp 602 / 59.3 (spread 5.8%); mode_n 0.70 / 0.42 (16.7e6 steps; spread 14%; warm-up 0.39 s, cache already warm, so a cold compile time was not measured); delta_0.01 FAILED at the start state (FixedPointError: no stable fixed point at eta_bar 2.5, J -21, Delta 0.01), not timed; radau_1e-12 TIMEOUT at 3600 s on repeat 1 (so at least 30 times the headline), not timed, lower bound only. Provisional eta path (UNVERIFIED until A4) on all but m2_ramp; mode_n sigma 1e-3 UNVERIFIED, not calibrated.
Caveats: records carry dirty = true (the only uncommitted files were the 3b files; commit b09f3f1). The 9.1 machine state was NOT met: Balanced power plan, a browser, VS Code and Defender (MsMpEng up to 88% before m2_ramp) were active; the machine-state fields record this. Treat the numbers as upper-side and re-time in the 9.1 state at 3c. Open for the user (not decided): delta_0.01 as defined cannot start at the provisional path (its start point has no stable fixed point), and Radau at rtol 1e-12 does not finish in the limit; neither cell was altered.
Reason:          3b of docs/ms3_plan.md.
Options:         -
Chosen:          as above   Default from: DL-094, DL-095
Evidence:        plan 9.2 step 1, D-6, D-8; results/timing/*.json (git-ignored).
Test:            tests/test_timing.py.
Status:          done; two cells failed or timed out as recorded
Commit/tag:      the 3b commit

## DL-098  User rulings on MS3 3c: plan-rule eta_bar paths, Radau timeout and t10 cells, re-timing    [ID: D12, D36, T23]
Date:            2026-10-15        Author:
Decision:        (1) Every timing cell's provisional eta_bar path is rebuilt with the plan's rule (D12): eta_start = eta_H - 1.5, eta_peak = max(4, eta_H + 2). eta_H is taken from a numerical scan with the repo's fixed_points and jacobian_3d (classify_all, model M3, J = -21, tau_d = 5 ms, tau_d/tau = 0.5, I = 0): the lowest eta_bar at which the stable root loses stability, scanned from -10 to 10 in steps of 0.01 and refined by bisection. Our own result, not the user's rough outside scan: Delta = 0.01 -> 0.393453; Delta = 0.3 -> 2.896046; Delta = 0.6 -> 4.774430. The outside scan (about 0.37, 2.87, 4.77) agrees for Delta = 0.6 and is about 0.02 to 0.03 low for the other two. At each value the crossing is a complex pair with Re lambda changing sign (about -7e-4 to +7e-4 at Delta = 0.01, +-2e-4 at 0.3 and 0.6), i.e. a Hopf crossing, and one fixed point exists over the whole scan. Resulting paths: Delta = 0.01: eta_start -1.106547, eta_peak 4.0; Delta = 0.3 (headline, P5, Radau, mode N): 1.396046, 4.896046; Delta = 0.6: 3.274430, 6.774430. These replace the D-2 placeholder (eta_H = 4.0, path 2.5 and 6.0), which was off: the scan puts eta_H of the headline at 2.896, not 4.0 (4.0 is the ref_devalle eta_bar, not its Hopf point), and at Delta = 0.01 the placeholder start 2.5 lies above eta_H (0.393), so that cell could not start (DL-097). Every such path stays provisional and UNVERIFIED until A4 (MS5), where eta_H comes from the A4 grid. The values are entered as explicit eta_start and eta_peak (status provisional), not through path.eta_H. m2_ramp is unchanged (explicit, from the A1 folds). (2) radau_1e-12 is recorded as a timeout: no finish within 3600 s on the first repeat of DL-097 (old placeholder path), so at least 30 times the headline (119 s); a lower bound only. It is not re-run; its record is kept as is and carries the old path. Two cells are added on the P2 10 s ramp (plan Table 6.2 S13 scope: P2 at 10, 120 and 316 s): radau_1e-12_t10 and radau_1e-10_t10, Radau with rtol 1e-12 and 1e-10, T_ramp 10 s, headline path otherwise. Noted: a DOP853-to-Radau retry (10.4) on a run that hits the DOP853 limit could take over an hour. (3) 3c is done as docs/ms3_plan.md defines it, with the new paths and cells, after the user prepared the machine (High performance power plan, Defender exclusion, other programs closed). The machine state is recorded again, the median and spread are reported, and the cold Numba compile time is measured once with the cache cleared. Extrapolate and the launch rule (prediction <= 1.5 x the upper end of the matching Table 9.1 row at 6 workers, D-5) are applied as 3c defines them. A cell that fails again is recorded and reported; no solver setting is changed.
Reason:          user rulings of 2026-10-15 after DL-097.
Options:         see DL-097 open items.
Chosen:          as above   Default from: user ruling, plan D12
Evidence:        plan D12, CP20, 9.2, Table 6.2 S13; DL-094, DL-096, DL-097; scan with mprsurge.models.fixed_points.
Test:            none (docs only); the config and test changes follow in the 3c commit.
Status:          done (decision); the path and cell files follow in the 3c commit
Commit/tag:      the commit that adds this entry

## DL-099  MS3 3c: re-timing of the cells on the plan-rule paths, extrapolation and launch rule    [ID: D12, D36, T23, T24]
Date:            2026-10-15        Author:
Decision:        none; no default and no solver setting changed. Implements DL-098 (3): the cells of DL-098 (1) and (2), 3 repeats each, commit 247c5d2, dirty = false, DOP853 rtol 1e-10 unless named, 6 workers for the extrapolation (D-7), results/timing/*.json and prediction_3c.txt (git-ignored).
Machine state: power plan High performance, AC (no battery), checked before each cell. Defender exclusion: cannot be read without admin rights, user-reported only. NOT met: a browser (waterfox, Edge webview), VLC, the EA app helper and VS Code were still open throughout; CPU load before each cell 6 to 22%, the busiest process up to 119% of one core (Edge webview) before the headline. The spread below includes this. Cold Numba compile (cache cleared, then fresh process): 0.78 s for warm_up (mode N); 0.16 s in the later mode_n run (cache rebuilt).
Results (median of 3, s per run; s per 1e4 tau; spread = (max - min)/median; solver count = nfev, mode N Heun steps):
  headline         117.3 s   71.1   1.9%   nfev 5.28e6
  delta_0.01       203.6 s  123.4   3.1%   nfev 9.55e6   (path -1.107 to 4.0)
  delta_0.6        107.5 s   65.2   3.8%   nfev 4.87e6   (path 3.274 to 6.774)
  p5_1000         1777.3 s   88.2   6.9%   nfev 6.06e7
  m2_ramp          512.0 s   50.4   6.2%   nfev 2.74e7
  mode_n            0.61 s    0.365 3.0%   1.67e7 steps (sigma 1e-3 UNVERIFIED, not calibrated)
  radau_1e-10_t10  143.4 s  521.5   0.8%   (2,750 tau; nfev 3.02e6)
  radau_1e-12_t10  299.7 s 1089.7   8.2%   (2,750 tau; nfev 6.41e6)
  radau_1e-12      TIMEOUT at 3600 s (DL-097, old path), at least 30 x headline, lower bound, not re-run.
Against DL-097 (old path, Balanced plan): headline 119.3 -> 117.3 s, delta_0.6 97.1 -> 107.5 s, p5_1000 1945 -> 1777 s, m2_ramp 602 -> 512 s, mode_n 0.70 -> 0.61 s. The Delta = 0.01 cell now runs (203.6 s, 1.7 x the headline). The rows hold the same order, so the change from the power plan is small next to the path change.
Extrapolation (analysis/timing.extrapolate, 6 workers, Table 9.1 work counts at 20 steps per tau, so 3.3e5 steps = 16,500 tau; this is not the 3e family table; allowance = upper end of the Table 9.1 row, rule prediction <= 1.5 x allowance):
  One P2 ramp: headline 117.3 s PASS, delta_0.6 107.5 s PASS, delta_0.01 203.6 s FAIL (limit 148.5 s).
  S2, S5, S6 sweeps (7e7 MF steps, 3.1e9 Heun): 1.16 h at headline s/tau, PASS (limit 1.42 h; at the P5 s/tau 1.43 h, just over, FAIL).
  S5 baseline-only mode N: 0.01 h PASS.
  S7 map 1: 4.94 h at headline, 4.53 h at delta_0.6 PASS (limit 6.15 h); 8.57 h at delta_0.01 FAIL.
  S7 map 2 and noisy subgrid: 2.53 h PASS (limit 3.30 h).
  Not extrapolated (no run count, or no cell): S1 to S4/A1 to A6, networks S8 to S10/S12 (R5 estimates, not measured), S11/S12 mean field/S16, S13 numerics, spectrograms, analysis. No total is formed; the D36 cap is not judged.
  Radau/DOP853 s/tau (Radau at the 10 s ramp, DOP853 at the 120 s headline, so indicative): 7.3 x at 1e-10 and 15.3 x at 1e-12, against the plan's 3 to 10 x.
Verdict: not all rows meet the launch rule. Rows that fail: the Delta = 0.01 edge for the single run and for map 1, and (marginally, only if all sweep work costs the P5 rate) S2/S5/S6. Whether map 1 is judged on the headline or on the Delta bounds, and the 9.3 cut order, are for the user; nothing is cut and no S-run starts. Paths stay provisional and UNVERIFIED until A4, and the cells are re-timed at MS5.
Reason:          3c of docs/ms3_plan.md.
Options:         -
Chosen:          as above   Default from: DL-094, DL-095, DL-098
Evidence:        results/timing/*.json, prediction_3c.txt, logs/ (git-ignored); plan 9.2, Table 9.1.
Test:            fast suite green.
Status:          done; launch verdict open for the user
Commit/tag:      the 3c commit

## DL-100  User rulings after DL-099: map 1 as a weighted family, four tau_d corner cells, no cut now, Radau reading of RB6    [ID: D12, D36, T23, T24]
Date:            2026-10-15        Author:
Decision:        (1) Map 1 (S7: Delta 0.01 to 0.6, 30 values, x tau_d 1 to 50 ms, 30 values log, P2, T_ramp 120 s) is judged as a family: a weighted estimate over its actual 900-cell grid, with the cost of each cell interpolated between measured cells in log Delta and log tau_d. The plan does not state the Delta spacing (only tau_d carries "log"), so the Delta grid is taken as linear, 30 points from 0.01 to 0.6, UNVERIFIED. The all-Delta = 0.01 value (8.57 h in DL-099) is reported only as a worst case, not as a verdict. Our reading of the interpolation, not specified by the user: piecewise linear (Delaunay) in (log Delta, log tau_d) on the measured cells, applied to s per run, no extrapolation outside the hull of the measured cells; the weighted estimate is the sum over the 900 grid cells divided by 6 workers; the limit is 1.5 x 4.1 h (D-5). Four tau_d corner cells are added, each a committed yaml under configs/timing/: delta_0.01_td1, delta_0.01_td50, delta_0.6_td1, delta_0.6_td50 (J = -21, I = 0, P2, T_ramp 120 s, DOP853 rtol 1e-10, as the headline). Their paths are the D12 rule with eta_H from the repo's scan (fixed_points and jacobian_3d, J = -21, tau_d/tau = tau_d_ms/10, eta_bar from -10 to 10 in steps of 0.01 with bisection; at each crossing a complex pair with Re lambda changing sign): (Delta 0.01, tau_d 1 ms) eta_H 0.838033, path -0.661967 to 4.0; (0.01, 50 ms) eta_H 0.250995, path -1.249005 to 4.0; (0.6, 1 ms) eta_H 7.786041, path 6.286041 to 9.786041; (0.6, 50 ms) no loss of stability on [-10, 10], so by CP20 the headline cell's start and peak 1.396046 and 4.896046. All provisional and UNVERIFIED until A4 (MS5). They are timed like the others (3 repeats, same limit, same machine-state record).
(2) Cut order: none applied now. The sweeps at the P5 rate (1.43 h against 1.42 h) are a tie within measurement noise. If after the re-time the sweeps still fail, or the weighted map 1 estimate exceeds its limit, section 9.3 is applied from the top and the step is named.
(3) Radau (S13): the DOP853-versus-Radau pass test uses rtol 1e-10 on P2 at 10, 120 and 316 s; rtol 1e-12 is used only at the 10 s ramp, for the delay-versus-rtol report (RB6 says that comparison is reported, not a pass test). The Radau cost is extrapolated from the radau_1e-10_t10 cell and marked indicative, because the two Radau cells use a short ramp. This reading of RB6 is UNVERIFIED; the criteria are unchanged.
(4) 6, 8 and 10 worker timings (9.2 step 1, last sentence): not done. They are sub-step 3d of docs/ms3_plan.md (scripts/time_one_run.py --workers N, results/timing/workers_{6,8,10}.json); scripts/time_one_run.py has no --workers option yet and no workers_*.json exists. Per D-7 they do not change the 6-worker extrapolation. Rows that now have a run count and a matching cell are extrapolated in the next entry. The 24 h cap (D36) is not judged until the network rows can be timed (qif_network, MS5).
Reason:          user rulings of 2026-10-15 on DL-099.
Options:         see DL-099 verdict.
Chosen:          as above   Default from: user ruling
Evidence:        plan Table 6.2 S7, S13, RB6, CP20, 9.2, 9.3, Table 9.1; DL-098, DL-099; docs/ms3_plan.md 3d.
Test:            none (docs only); the cells, tests and timing follow in the next commit.
Status:          done (decision); timing follows
Commit/tag:      the commit that adds this entry

## DL-101  MS3 3c (continued): tau_d corner cells, map 1 weighted estimate, remaining rows    [ID: D12, D36, T23, T24]
Date:            2026-10-16        Author:
Decision:        none; no default and no solver setting changed; no cut applied (DL-100 (2)). Cells and code at commit 6bd871f (dirty = false), 3 repeats, DOP853 rtol 1e-10, High performance plan; the browser, VLC and Edge webview were still open (CPU load 9 to 31% before each cell), as in DL-099. Paths provisional and UNVERIFIED until A4.
Results (median s per run; spread):
  delta_0.01_td1   243.0 s  7.7%   (path -0.662 to 4.0)
  delta_0.01_td50  127.2 s  4.8%   (-1.249 to 4.0)
  delta_0.6_td1    125.3 s  0.6%   (6.286 to 9.786)
  delta_0.6_td50    91.6 s  0.6%   (headline start and peak, no Hopf point, CP20)
Map 1 (S7), weighted over the 900-cell grid (Delta linear, UNVERIFIED; tau_d log), cost interpolated piecewise linearly in (log Delta, log tau_d) on seven measured cells (the four corners, delta_0.01, headline, delta_0.6 at 5 ms), 6 workers: 5.14 h; per run mean 123.4 s, min 91.6, max 243.0. Allowance 4.1 h, limit 1.5 x = 6.15 h: PASS. Sensitivity (our check, not ruled): with a log-spaced Delta grid the estimate is 6.02 h, still inside but close to the limit; interpolation between only seven cells is coarse, and the cost is not guaranteed smooth. Worst case, all 900 cells at the slowest cell (243 s): 10.13 h, reported as a worst case only, not a verdict.
Cut order: none applied. Map 1 passes on the weighted estimate and the sweeps are unchanged (1.16 h at the headline rate, 1.43 h at the P5 rate, limit 1.42 h; a tie within the 7% spread of p5_1000, DL-100 (2)).
Remaining rows extrapolated (6 workers; counts from Table 6.2; indicative where noted):
  S13 Radau at rtol 1e-10 on P2 at 10, 120, 316 s (tau 2,750, 16,500, 41,000), cost from the 10 s cell (0.0521 s per tau): Radau 143, 861, 2138 s; DOP853 counterpart 20, 117, 292 s; 59.5 min one core, 9.9 min at 6 workers, longest run 35.6 min. Indicative (short-ramp Radau rate applied to long ramps). rtol 1e-12 at 10 s: 5.0 min measured. This reading of RB6 and S13 is UNVERIFIED (DL-100 (3)). The S13 row (< 1 h, limit 1.5 h) also holds the rtol 1e-8 and 1e-12 ladders on other ramps, delta0, the D43 floor ladder and the network dt ladder, which have no cell or count here: the row is not fully extrapolated.
  S11 (sigma 3 x T_ramp 4 x 10 seeds, 120 mode-N runs, 2 s discard + 5 + 1.25 T + 10 s): 1.93e9 Heun steps, 0.20 min (assumes sigma does not change the cost).
  S16 (14 + 64 = 78 runs at the headline cost): 25.4 min. Indicative: tau_d and Delta perturbations cost more or less (cells above: 0.7 to 2 x).
  S11 + S16 = 25.6 min against the row S11, S12 mean field, S16 (< 40 min, limit 60 min); S12 mean field is not included (the NC path durations are not in the text read for this entry), so the row is partial.
  S2 (M2 ramp, 13 T_ramp 1 to 1000 s, 5 + T + 10 s): 3.5 min; S4 (M3, 122 steps x 2 s at the headline rate): 0.5 min; with S1, S3 and A1 to A6 not extrapolated the row S1 to S4/A1 to A6 (< 30 min, limit 45 min) is partial.
Workers 6, 8, 10: not done; they are sub-step 3d (DL-100 (4)). The 24 h cap (D36) is not judged: the network rows (S8 to S10, S12, K8) are not measured until qif_network exists (MS5).
Reason:          DL-100.
Options:         -
Chosen:          as above   Default from: DL-100
Evidence:        results/timing/*.json, prediction_dl101.txt (git-ignored); plan Table 6.2, Table 9.1, 9.2, 9.3.
Test:            fast suite green (206 passed).
Status:          done; sub-step 3d and the family table 3e remain
Commit/tag:      the commit that adds this entry

## DL-102  MS3 3d: 1, 6, 8, 10 concurrent workers, measured throughput, extrapolations and launch rule re-applied    [ID: D12, D36, T23, T24]
Date:            2026-10-16        Author:
Decision:        none; no default, solver setting, plan text or ruling changed; no cut applied; no S-run started. Implements 3d of docs/ms3_plan.md: scripts/time_one_run.py --cell headline --workers N --repeat 3 runs N copies of the cell at once through the spawn pool and run.py initialiser (thread variables 1, plain dicts), a barrier releasing all copies together (start spread 0.00 s, N distinct pids in every batch); each copy is timed on its own. Code commit before this entry, dirty = false, DOP853 rtol 1e-10, High performance plan, AC. Machine state per batch recorded in results/timing/workers_{1,6,8,10}.json (git-ignored): CPU load 8 to 29% before, 0 to 22% after; the browser (waterfox, Edge webview) and Task Manager were still open, as in DL-099 and DL-101, so not the clean 9.1 state. CPU: Ryzen 5 5600, 6 cores / 12 threads, so 8 and 10 workers use SMT siblings.
Results (3 batches each; per-run median s; batch wall median s; runs/h = N x 3600 / batch wall; speed-up and efficiency against N = 1):
  N=1    119.51   119.52    30.1   1.00   100%
  N=6    171.96   172.31   125.4   4.16    69%   (per run 1.44 x slower than alone)
  N=8    166.52   167.15   172.3   5.72    72%   (1.39 x)
  N=10   201.84   202.65   177.6   5.90    59%   (1.69 x)
Best worker count: 10 (highest throughput), only 3% above 8 (batch-wall spread within a cell was 0.5 to 6%, so 8 and 10 are close to a tie; 8 has the better efficiency and shorter per-run time). 10 is used below. Six workers deliver 4.16 x one worker, not 6 x: the "divide by 6" assumption (ideal) is met in effect only at 10 workers (5.90). The D-7 ruling (6 workers in the extrapolation) is not changed by this entry; the 6-worker column is shown for it.
Extrapolation: DL-099/DL-101 values at "6 ideal workers" recomputed with the measured speed-up S in place of 6 (extrapolate is linear in 1/workers; map 1 re-run through weighted_family_estimate with S). Rates s/tau are those measured alone. Script: results/timing/predict_3d.py, output prediction_3d.txt (git-ignored). Launch rule: <= 1.5 x upper end of the Table 9.1 row (D-5).
  Row                         limit   S=5.90 (10 w)    S=5.72 (8 w)   S=4.16 (6 w)
  Sweeps S2/S5/S6, headline   1.42 h   1.18 PASS        1.22 PASS      1.67 FAIL +18%
  Sweeps, P5 rate             1.42 h   1.45 FAIL +2%    1.50 FAIL +6%  2.06 FAIL +45%
  S7 map 1 weighted           6.15 h   5.23 PASS        5.39 PASS      7.41 FAIL +21%
  S7 map 2 + noisy subgrid    3.30 h   2.57 PASS        2.65 PASS      3.65 FAIL +11%
  S5 baseline mode N          -        0.01 h PASS      0.01 PASS      0.01 PASS
  S11 + S16 (partial)         60 min   26.0 PASS        26.9 PASS      36.9 PASS
  S2 + S4 (partial)           45 min   4.1 PASS         4.2 PASS       5.8 PASS
  S13 Radau pass set (indicative; row limit 1.5 h, row not fully extrapolated): 10.1 / 10.4 / 14.3 min at 6 ideal-equivalent workers; longest run 35.6 min alone, 60 min at 10 concurrent copies.
Single-run row (limit 148.5 s), one run's wall under N concurrent copies (alone x per-run slowdown): headline 117 alone, 169 (6 w), 164 (8 w), 198 (10 w); delta_0.6 108, 155, 150, 182; delta_0.01 204, 293, 284, 344. Alone only delta_0.01 fails; under any concurrency the headline and delta_0.6 also exceed 148.5 s. Whether the single-run row is judged alone or under load is not stated in the plan text read: left for the user.
Verdict at the chosen count (10): not all rows meet the launch rule. Failing: the sweeps if all sweep work costs the P5 rate, by 2% (1.45 h against 1.42 h; the tie flagged in DL-100 (2), inside the 7% spread of p5_1000), and the single-run row (delta_0.01 alone; headline and delta_0.6 under load). Map 1 passes (5.23 h against 6.15 h). At 6 workers (D-7) the sweeps, map 1 and map 2 all fail. Next step if the user rules the P5-rate sweeps a fail: 9.3 step (5), drop the 562 s and 1000 s ramps from P5 and the start-distance runs (steps 1 to 4 do not apply or are not measured: Radau is already at the headline T_ramp in the pass set, network dt and S9 seeds have no mean-field cost here, sigmoid for P2 only is a path change). If map 1 or map 2 later fail at 6 workers, step (6) map 1 to 20 x 20 and (7) map 2 to 13 x 13. Nothing is cut. The 24 h cap (D36) is not judged: network rows unmeasured until qif_network (MS5). Paths provisional, UNVERIFIED until A4.
Reason:          3d of docs/ms3_plan.md; DL-100 (4).
Options:         -
Chosen:          as above   Default from: DL-094 (D-7), DL-100
Evidence:        results/timing/workers_{1,6,8,10}.json, prediction_3d.txt, logs/workers_*.log (git-ignored); plan 9.2 step 1, 9.3, Table 9.1.
Test:            fast suite green (208 passed, 1 xfailed) on the code commit; tests/test_timing.py worker mode.
Status:          done; launch verdict open for the user; 3e and 3f remain
Commit/tag:      the commit that adds this entry

## DL-103  User rulings after DL-102: launch rule judged at 10 workers, single run judged alone, no cut now, clean re-time at 3f    [ID: D12, D36, T23, T24]
Date:            2026-10-16        Author:
Decision:        (1) The launch rule (plan 9.2 step 3, <= 1.5 x the Table 9.1 allowance) is judged at the worker count actually used, 10 workers, using the measured speed-up of 5.90 in place of the ideal 6. This is a logged departure from the D-7 ruling (DL-094), which fixed 6 workers for the extrapolation; D-7 is otherwise unchanged and the 6-worker column stays in DL-102 for reference. (2) The single-run row (limit 148.5 s) is judged alone, not under concurrent load: only delta_0.01 (204 s alone) fails it; the headline (117 s) and delta_0.6 (108 s) pass. (3) Nothing is cut now. The cells are re-timed once on a clean machine (VLC and browser closed) at 3f. Section 9.3 step (5) (drop the 562 s and 1000 s ramps from P5 and the start-distance runs) is applied only if the sweeps at the P5 rate still fail after that re-time; the weighted map 1 estimate and map 2 are re-checked in the same pass, and steps (6) and (7) stay as in DL-102.
Context:         At 6 workers (4.16 x speed-up) the sweeps, map 1 and map 2 fail. At 10 workers the sweeps pass at the headline rate and fail by 2% at the P5 rate (1.45 h against 1.42 h, a tie inside the 7% spread of p5_1000); map 1 passes (5.23 h against 6.15 h) and map 2 passes (2.57 h against 3.30 h). Run alone, only delta_0.01 fails the 148.5 s row. The 24 h cap (D36) cannot be judged until the network rows exist (MS5, qif_network). Paths are provisional and UNVERIFIED until A4. A browser (waterfox, Edge webview) was open during 3d, so the timings are slightly pessimistic.
Reason:          project owner rulings on DL-102 of 2026-10-16.
Options:         judge at 6 workers (D-7) or 10; judge the single run alone or under load; cut now or re-time first.
Chosen:          as above   Default from: user ruling (departs from D-7 / DL-094 for the launch rule only)
Evidence:        DL-102; results/timing/workers_{1,6,8,10}.json, prediction_3d.txt (git-ignored); plan 9.2, 9.3, Table 9.1.
Test:            none (docs only).
Status:          done (decision); re-time at 3f
Commit/tag:      the commit that adds this entry

## DL-104  MS3 3f: clean re-time at 10 workers, rows judged under DL-103, section 9.3 step 5 not applied    [ID: D12, D36, T23, T24]
Date:            2026-10-16        Author:
Decision:        No default, solver setting, plan text or ruling changed; section 9.3 step (5) is NOT applied and nothing is cut: the sweeps at the P5 rate now pass (1.14 h against the limit of 1.43 h, DL-103 (3)). No S-run started. Implements DL-103 (3): every cell is re-timed once at 10 concurrent copies x 3 batches (pooled per-run median over the 30 copies, as DL-102), the single-run row alone (3 repeats). Judged at 10 workers, divisor 10 on the per-run median measured under 10-way load (DL-103 (1), a logged departure from D-7); the single-run row judged alone (DL-103 (2)). Code: 2092b94 (families, prediction), 2ba28b5 (step-count fallback); tree clean at 2092b94 for every cell (the mode_n x10 supplementary run only after the fallback edit, analysis code only). Raw outputs in results/timing/clean/ next to the 3d ones (git-ignored); report results/timing/clean/prediction.txt, written by python -m mprsurge.analysis.timing --predict --workers 10 --results-dir results/timing/clean.
Machine state: VLC, waterfox, Edge and Task Manager closed before the run. Residual caveat: six msedgewebview2 processes (VS Code's) stayed open, as the user ruled. High performance plan, sleep after = never on AC (display off 900 s), AC. CPU load before each cell 0 to 19% (0 to 10% for the 10-worker cells), after 0 to 11%. Ryzen 5 5600, 6 cores / 12 threads, so 10 workers use SMT siblings. Limit per repeat 3600 s, raised to 7200 s for p5_1000 (expected about 3000 s under load; measured 2,329 s). Paths provisional and UNVERIFIED until A4.
Results, per-run median s at 10 concurrent copies (3d, clean, change): headline 201.8, 162.8 (-19.3%); throughput 177.6, 220.4 runs/h (+24%); delta_0.01 343.8*, 285.1; delta_0.6 181.6*, 150.5 (*3d: alone x slowdown). Corner cells (clean only): delta_0.01_td1 330.6, delta_0.01_td50 194.3, delta_0.6_td1 189.9, delta_0.6_td50 139.1. p5_1000 2,329.4 (batches 2,341, 2,333, 2,329 s); m2_ramp 736.8; radau_1e-10_t10 189.1. Alone (3 repeats): headline 117.3, 101.4 s (-13.6%); delta_0.6 107.5, 93.5 (-13.0%); delta_0.01 203.6, 178.3 (-12.4%). Headline alone against 10 copies: 1.61 x slower per run (3d: 1.69 x), speed-up 6.2 (3d: 5.90).
Rows (launch rule: prediction <= 1.5 x Table 9.1 allowance; 3d from DL-102 at S = 5.90; clean at 10 workers measured):
  Row                          limit     3d            clean          change   verdict (clean)
  Single run, alone (headline)  148.5 s   117.3         101.4          -13.6%   PASS
  Single run, alone (d_0.6)     148.5 s   107.5         93.5           -13.0%   PASS
  Single run, alone (d_0.01)    148.5 s   203.6         178.3          -12.4%   FAIL (+20% over the limit)
  Sweeps S2/S5/S6, headline     1.43 h    1.18 h        0.97 h         -17.8%   PASS
  Sweeps, P5 rate               1.43 h    1.45 h FAIL   1.14 h         -21.4%   PASS
  S7 map 1 weighted             6.15 h    5.23 h        4.44 h         -15.1%   PASS
  S7 map 2 + noisy subgrid      3.30 h    2.57 h        2.20 h         -14.4%   PASS
  S5 baseline-only mode N       108 s     53 s (a)      121 s          (a)      FAIL (+12% over the limit)
  S11 + S16 (partial)           60 min    26.0 min      21.5 min       -17%     PASS (partial)
  S2 + S4 (partial)             45 min    4.1 min       3.4 min        -17%     PASS (partial)
  S13 Radau pass set (indic.)   1.5 h     10.1 min      7.9 min        -22%     PASS (partial, indicative)
(a) not like for like: 3d took the alone Heun rate (3.65e-8 s per step) divided by 5.90; the clean run measures the mode_n cell under 10 copies directly. Mode N takes 2.34 s per run under 10 copies against 0.61 s alone. A supplementary mode_n run with a 1200 s ramp (151,700 tau, 10 copies x 3 batches, results/timing/clean/mode_n_x10) took 22.67 s; the line through the two points has slope 1.51e-7 s per Heun step and an offset near zero, so the 4 x slowdown is a rate under SMT load, not a start-up cost. This also means the 3d Heun parts (alone rate / S) were too low; in the clean figures they are included at the loaded rate (sweeps 44 s, map 2 533 s, both small against their mean-field parts).
Map 1 (weighted, 900 cells, Delta linear UNVERIFIED) 4.44 h on the clean per-run medians of the seven cells; the single-run row's failing cell is the Delta = 0.01 edge, which map 1 weights by its 30 values of 900.
Verdict: all mean-field rows with a complete count pass except two. (1) Single run, delta_0.01 alone, 178.3 s against 148.5 s (the plan's per-run range 33 to 99 s, one core). (2) S5 baseline-only mode-N, 121 s against 108 s, a 2 min row in the MS7 plan. Neither is covered by a step of section 9.3 (steps 1 to 4 and 6, 7 name other rows; step 5 names the P5 and start-distance ramps, which now pass), so nothing is cut and both go to the user. The partial rows are lower bounds. The 24 h cap (D36) is not judged: S8 to S10, S12, K8 have no timing cell (network code is MS5), and S1, S3, A1 to A6, S12 mean field and the S13 ladders have no count here.
Reason:          3f of docs/ms3_plan.md; DL-103 (3).
Options:         apply 9.3 step 5 (not needed, P5-rate sweeps pass); cut nothing.
Chosen:          cut nothing   Default from: DL-103
Evidence:        results/timing/clean/ (workers_10.json per cell, alone json, logs/, prediction.txt, mode_n_x10), git-ignored; DL-102; plan 9.2, 9.3, Table 9.1.
Test:            fast suite green (211 passed, 1 xfailed).
Status:          done; two row failures open for the user
Commit/tag:      the commit that adds this entry

## DL-105  User ruling after DL-104: the two failing MS3 rows accepted as logged exceptions; Heun loaded-rate item carried to MS5    [ID: D12, D36, T23, T24]
Date:            2026-10-16        Author:
Decision:        Both rows that still fail after the clean re-time (DL-104) are accepted as logged exceptions. No row and no allowance is changed; no default, solver setting or plan text is changed. (a) Single run, delta_0.01, alone: 178.3 s against the 148.5 s limit. Informational: its cells are already inside map 1 (weighted), which passes at 4.44 h against 6.15 h. (b) S5 baseline-only mode N: 121 s against the 108 s limit. The row is small in absolute time, and the clean number is the real rate under 10 concurrent copies. Carried forward to MS5 (network timing): the Heun kernel runs about 4x slower per step under 10 copies than alone (1.51e-7 against 3.65e-8 s per step; 2.34 against 0.61 s per mode-N run), which is about 2.3x above what 3d assumed (alone rate divided by 5.90; 120.6 s against 53.2 s for the mode-N row), so the 3d Heun predictions were understated and the MS5 network rows must be timed under load. The D36 24 h cap stays unjudged until then.
Context:         DL-104 left two rows failing that no step of section 9.3 covers. Rate under load: 2.34 s per mode-N run against 0.61 s alone; 1.51e-7 against 3.65e-8 s per Heun step (DL-104 note (a)).
Reason:          project owner ruling on DL-104 of 2026-10-16.
Options:         accept as exceptions; change the row or its allowance; reduce the work.
Chosen:          accept as exceptions   Default from: user ruling
Evidence:        DL-104; results/timing/clean/ (git-ignored); plan 9.2, 9.3, Table 9.1.
Test:            none (docs only). Fresh-context review of docs/ms3_gate_report.md against the raw outputs: no numeric mismatches; the 'about 4x' wording above corrected (the project owner's ruling text compared the loaded rate with the alone rate divided by 5.90); DL-104 and the report give S11+S16 clean as 21.5 min, raw recomputation gives 21.6 min (report corrected; DL-104 left as committed); DL-104 p5_1000 third batch 2,329 s is 2,329.7 s raw (rounds to 2,330).
Status:          done; MS3 gate closed with two logged exceptions
Commit/tag:      the commit that adds this entry

## DL-106  MS4 4a: sub-step plan docs/ms4_plan.md, map 1 weighted figure recomputed    [ID: D8, D12, D36, T06]
Date:            2026-10-16        Author:
Decision:        none; no default, solver setting, plan text or ruling changed. Adds docs/ms4_plan.md (MS4 goal and gate as the plan states them, inputs and their locations, sub-steps 4a to 4f, run-time expectations from DL-102 to DL-105, open items, four questions for the user before 4b). No S2 or A3 run. Check made first: the map 1 weighted figure was recomputed from the raw per-copy walls in results/timing/clean/<cell>/workers_10.json (30 copies per cell, median), seven cells at (Delta, tau_d ms) = (0.01,1), (0.01,5), (0.01,50), (0.3,5), (0.6,1), (0.6,5), (0.6,50), Delta linear 30 values and tau_d log 30 values (900 cells), piecewise-linear interpolation in (log Delta, log tau_d), divisor 10: 4.442 h, mean 177.7 s per run. docs/ms3_gate_report.md and DL-104 give 4.44 h: match. The recomputation is independent of mprsurge.analysis.timing but uses the same grid and interpolation choices; Delta linear stays UNVERIFIED (plan gives no spacing). Four corners alone would give 4.83 h (not a plan quantity).
Open for the user before 4b (docs/ms4_plan.md): D-1 meaning of "within one step" of the saddle-node and the target fold; D-2 S2 baseline, hold, sampling, profile and G band for M2; D-3 G1 scope (S2 is one path); D-4 K5 kept as defined at MS2 (not redefined here). Also flagged: the DL-062/DL-073 growth-estimator caveats apply to G1; the map 1 Delta spacing concerns MS8.
Reason:          4a of docs/ms4_plan.md; Table 11.1 MS4.
Options:         -
Chosen:          defaults listed in docs/ms4_plan.md   Default from: plan Table 11.1, DL-082, DL-085, DL-093
Evidence:        results/timing/clean/ (git-ignored), docs/ms3_gate_report.md, plan 5.2 A3, 4.3 G1, 6.2 S2.
Test:            fast suite green (211 passed, 1 xfailed).
Status:          done; 4b waits for the user
Commit/tag:      the commit that adds this entry

## DL-107  User rulings on DL-106 (D-1 to D-4) and MS4 4b: configs/S2.yaml, scripts/run_S2.py dry run    [ID: D8, D12, T06]
Date:            2026-10-16        Author:
Decision:        (a) "Within one step" of the A1 saddle-node value (A3 check) means one A1 grid cell, d_eta_bar = 0.05 (K1's cell). The result is also reported against 0.025, for information only. This reading is UNVERIFIED. The target fold is the one the upward ramp crosses, read from A1 (not assumed). (b) S2 setup: 5 s baseline, the ramp, then a 10 s hold; linear profile; D25/D26 solver settings (DOP853, rtol 1e-10, atol 1e-12, max_step 0.05 tau); G band 25 to 100 Hz; output sampling as the m2_ramp timing cell (dt_out 1 ms). Band and sampling are UNVERIFIED. (c) G1 is judged on S2 alone; "move to M3" is the expected outcome and needs no further paths. (d) K5 is not re-run; the MS2 pass is cited. The K5 definition stays an open item (DL-064, DL-082, DL-088).
4b build:        configs/S2.yaml (kind mf with a 13-value T_ramp_values family, no new run kind; J = 15, Delta = 1, tau = 10 ms, I = 0; path_eta eta_start -6.743527161657844, eta_peak -2.136134086195692; T_ramp 10^(k/4) s, k = 0..12). The two eta values are typed in the YAML (as in configs/timing/m2_ramp.yaml); scripts/run_S2.py recomputes the folds with bifurcation.fold_etas(15, 1) (the A1 formula, not the stored grid) and stops with exit 2 if the path is not (fold_low - 1, fold_up + 1) to 1e-12. Folds found: lower -5.743527161657844, upper -3.1361340861956917. --dry-run prints the folds and the 13-run list (T_ramp, t_on, ramp end, total tau, hash), checks the ramp breakpoints of every cell (t_on = 500 tau, ramp end = t_on + T, eta at the ends), writes 13 dry-run records, integrates nothing. Total simulated 247,860 tau, equal to the MS3 family count. The run's results/ output is not read from A1's stored npz; the formula is what K1 and K2 check.
Reason:          project owner rulings on docs/ms4_plan.md D-1 to D-4; 4b of the plan.
Options:         D-1 half-spacing step (plan default) or the A1 cell; ruled: the A1 cell.
Chosen:          as above   Default from: user ruling (a), (c), (d); (b) = plan defaults of DL-106 D-2
Evidence:        docs/ms4_plan.md; configs/S2.yaml; scripts/run_S2.py; tests/test_s2_config.py; plan 5.2 A3, 6.2 S2, 4.3 G1.
Test:            tests/test_s2_config.py (7 new); fast suite green (218 passed, 1 xfailed).
Status:          done (4b); 4c waits for the user
Commit/tag:      the commit that adds this entry

## DL-108  User ruling on the S2 fold source; MS4 4c: analysis/sn_ramp.py (A3 jump and G1 fit)    [ID: D8, D12, T06]
Date:            2026-10-16        Author:
Decision:        (a) Ruling: the S2 folds are read from the A1 formula (bifurcation.fold_etas), as scripts/run_S2.py does (DL-107). Step 4e also cross-checks them against the stored A1 fixed-point grid (results/A1), within one grid cell. (b) 4c build: src/mprsurge/analysis/sn_ramp.py, pure functions on one stored series (t_ms, r, v, eta) and the fold value passed in. Jump definition, UNVERIFIED (the plan defines none): sliding window 0.1 s; a jump exists if the largest change of r over a window is at least 0.5 of the range of r; jump time = largest single-sample change of r inside that window; eta_bar at the jump = ramp value at that time. Window, fraction and time convention are ours. Ring class: envelope_growth (surge_metrics, MS1) on v from the jump time, G band 25 to 100 Hz, threshold 0 (no amplitude threshold in M2, CP17), first 10 cycles; damped only if rate < -2 SE (D8), else non_damped; no_jump when no jump. Returns offset from the fold in eta_bar and in steps (step 0.05, DL-107 (a)). The plan gives no definition of "ring class"; damped / non_damped is our reading, UNVERIFIED. DL-062 (SE too small) and DL-073 (step-onset bias) apply to the fit.
Reason:          project owner ruling; 4c of docs/ms4_plan.md.
Options:         jump by threshold on dr/dt or by crossing of the r midpoint; ruled by us: windowed change relative to range.
Chosen:          as above   Default from: user ruling (a); (b) our proposal, for the owner to confirm
Evidence:        src/mprsurge/analysis/sn_ramp.py, tests/test_sn_ramp.py; plan 5.2 A3, 4.3 G1, Table 2.1, D8.
Test:            tests/test_sn_ramp.py (7 new, seeded synthetic: known jump time and eta_bar; 5-cycle damped; slowly damped over 10 cycles; non-damped; smooth ramp, no jump); S2 not run.
Status:          done (4c); 4d waits for the user
Commit/tag:      the commit that adds this entry
