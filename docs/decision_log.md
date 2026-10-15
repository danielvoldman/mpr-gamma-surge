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
