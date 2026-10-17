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

## DL-109  User rulings on the 4c definitions; MS4 4d: S2 run (13 ramps) and results/A3/a3_sn_ramp.parquet    [ID: D8, D12, T06]
Date:            2026-10-16        Author:
Decision:        (a) The 4c jump definition (largest change of r over any 0.1 s window >= 0.5 of the range of r) stays as a working definition, UNVERIFIED; not tuned. A ramp with no clean jump is recorded as ambiguous; the jump for fractions 0.3 and 0.7 is recorded as information only. (b) Ring class is damped / non_damped / no_jump. (c) The G1 fit window starts at the jump sample, as the plan says; 4e reports a window shifted by a few ms as information only.
4d build:        scripts/run_A3.py (analysis driver: reads the stored series, applies analysis.sn_ramp, writes the parquet; fold = upper A1 fold from the formula), tests/test_run_A3.py (2 toy runs). S2 run with scripts/run_S2.py --set output.dir=results/A3 --workers 10; series in results/A3/S2/ (git-ignored) so 4e can re-analyse without re-running.
Produced:        13 of 13 runs ok. Wall 544 s in total (4a estimate: under 10 minutes, UNVERIFIED; 4a per-run estimate for the 1000 s run 12 to 13 min, found 526.9 s = 8.8 min). Per-run wall 13.3 s (T_ramp 1 s) to 526.9 s (1000 s). Parquet: 13 rows. Every ramp has a jump (change_frac 0.949 to 0.974, direction up), none ambiguous; the 0.3 and 0.7 variants give the same jump as 0.5 in all 13. All 13 ring classes are "damped" (rate about -24 to -26 per unit time, SE 0.3 to 0.6, about 10 cycles in window); DL-062 and DL-073 caveats apply to these numbers. Offsets from the upper fold fall from 6.9 steps (T_ramp 1 s) to 0.069 steps (1000 s). Not judged here: the A3 check and G1 are for 4e.
Reason:          project owner rulings; 4d of docs/ms4_plan.md.
Options:         -
Chosen:          as above   Default from: user rulings (a) to (c)
Evidence:        scripts/run_A3.py, results/A3/ (git-ignored), docs/ms4_plan.md run-time table.
Test:            tests/test_run_A3.py (1 new); fast suite green (226 passed, 1 xfailed).
Status:          done (4d); 4e waits for the user
Commit/tag:      the commit that adds this entry

## DL-110  MS4 4e: A3 check, fold cross-check, K5 citation, G1 metric and window sensitivity    [ID: D8, D12, T06]
Date:            2026-10-16        Author:
Decision:        None; no default or definition changed. Numbers from the saved S2 series and results/A3/a3_sn_ramp.parquet (no S2 re-run). Script: scripts/check_A3_G1.py (analysis only; writes results/A3/a3_4e_check.csv, git-ignored). Rates are per second (envelope_growth).
A3 check:        Slowest ramp (T_ramp 1000 s): eta_bar at the jump -3.132704, upper fold -3.136134, offset +0.003430 = 0.069 of the 0.05 step: within one step, PASS (step 0.05, DL-107 (a)). Against 0.025 (information only): 0.137 of that step, also within. Offsets for T_ramp 1, 1.78, 3.16, 5.62, 10, 17.8, 31.6, 56.2, 100, 178, 316, 562, 1000 s: 0.34575, 0.23495, 0.16037, 0.10906, 0.07437, 0.05048, 0.03449, 0.02344, 0.01595, 0.01086, 0.00740, 0.00504, 0.00343. Strictly monotone falling as the ramp slows (all 12 differences negative). Within 0.05 from T_ramp 31.6 s (17.8 s is 0.0505, just outside); within 0.025 from 56.2 s. The jump definition is UNVERIFIED (DL-108, DL-109).
Fold cross-check: (DL-108 (a)) formula fold_etas(15, 1): lower -5.743527, upper -3.136134. Stored A1 base grid (J = 15, cell 0.05): the root count changes between -5.75 and -5.70 (formula point inside the cell, 0.0065 from the nearer edge) and between -3.15 and -3.10 (inside, 0.0139 from the nearer edge, 0.0361 from the far edge). Half-spacing lattice (cell 0.025): edges -5.75/-5.725 and -3.15/-3.125, formula points inside both. Agreement within one grid cell (0.05) at both folds: PASS.
K5:              Cited, not re-run and not redefined: "K5 bursting reproduced in S1" passed in MS2, DL-088 (S1 series: up-crossings of r = 0.5559 every 40 tau, one up and one down in each of 5 periods) and DL-091 (A0 table, results/A0 hash 724055e00481: K5 pass, spacing deviation 8.7e-13 tau, tolerance 0.1). Definition and tolerance UNVERIFIED (DL-082); the open item stands.
G1 metric:       Plan wording (4.3, D8): stay with M2 only if some path with Delta > 0, tau = 10 ms gives a non-damped episode in G over >= 10 cycles (fitted envelope growth not negative by more than 2 SE); otherwise move to M3 and keep M2 as the damped-ring comparison. Per ramp (fit window from the jump sample, G band 25 to 100 Hz, threshold 0, first 10 cycles), all 13: rate -24.3 to -25.7 /s, SE 0.29 to 0.57 /s (rate/SE -45 to -84), cycles in window 10.00 to 10.11 (n 121 to 130 samples), call damped in all 13. Table (T_ramp: rate, SE, cycles): 1: -24.34, 0.29, 10.10; 1.78: -24.91, 0.44, 10.08; 3.16: -24.77, 0.36, 10.08; 5.62: -25.19, 0.46, 10.03; 10: -25.00, 0.37, 10.05; 17.8: -25.66, 0.57, 10.04; 31.6: -24.90, 0.31, 10.07; 56.2: -25.59, 0.49, 10.11; 100: -25.66, 0.52, 10.09; 178: -25.63, 0.51, 10.08; 316: -24.98, 0.33, 10.00; 562: -25.64, 0.51, 10.07; 1000: -25.39, 0.42, 10.09. Implication per the plan: no non-damped episode in G on S2 (J = 15, Delta = 1, tau = 10 ms), so G1's condition to stay with M2 is not met on this path, and the plan's wording is "move" (predicted by R1, R2, R3, R5, reasoned, not tested). Limits: S2 is one path (DL-107 (c)); the decision to move to M3 is the user's and is not taken here. Caveats: DL-062 (plain OLS SE too small, damped is declared too easily) and DL-073 (filter step-onset bias distorts the rate magnitude, not the sign). The margin is large (rate/SE at least 45 in magnitude over about 10 cycles), but the SE values are not trustworthy as written.
Sensitivity:     Window start shifted after the jump sample by 2, 5 and 10 ms (our choice of values; the band-pass is re-run from the shifted start, so the step-onset transient moves with the window). Sign agrees with the unshifted fit and the damped call agrees in all 13 ramps at every shift. Rates: 2 ms -21.6 to -23.4 /s, 5 ms -23.5 to -24.1, 10 ms -21.4 to -23.2; rate/SE at least 21.6 in magnitude; cycles in window 10.01 to 10.09. The rate magnitude moves by up to about 15 percent (DL-073 effect), the sign and call do not.
Reason:          4e of docs/ms4_plan.md, instructions of the owner.
Options:         -
Chosen:          as above   Default from: DL-107 to DL-109 definitions; shifts 2, 5, 10 ms ours
Evidence:        scripts/check_A3_G1.py, results/A3/ (git-ignored), results/A1/a1_fixedpoints_2d.npz, plan 4.3 G1, 5.2 A3, D8.
Test:            fast suite green (226 passed, 1 xfailed). No new test (script prints from existing functions).
Status:          done (4e); 4f and the G1 move decision wait for the user
Commit/tag:      the commit that adds this entry

## DL-111  User ruling after DL-110: gate G1 judged on S2 alone; project moves from M2 to M3, M2 kept as the damped-ring comparison    [ID: D8, D12, T06]
Date:            2026-10-16        Author:
Decision:        Gate G1 is judged on S2 alone (DL-107 (c)). S2 gave no non-damped episode in G: all 13 ramps are damped (DL-110). By the plan's own rule (4.3, D8) the project moves from M2 to M3, and M2 is kept as the damped-ring comparison. This is the plan's expected outcome [reasoned, not tested in the plan]. No plan text, D-item, model, surge class, path or control is changed.
Basis:           One path only (J = 15, Delta = 1, tau = 10 ms, I = 0, linear ramp); other M2 paths were not run. The call rests on our own definitions, UNVERIFIED: the jump definition (DL-108), the G band 25 to 100 Hz and the output sampling (DL-107 (b)), and damped / non_damped as the ring class.
Caveats:         DL-062: the plain OLS standard error is too small, so damped is declared too easily. DL-073: the step-onset filter bias distorts the rate magnitude, not the sign in the case tried (about 45 percent in that case, ms4_plan.md). The 2, 5, 10 ms window-shift test (DL-110, rate moves up to about 16 percent, sign unchanged) is a window-start sensitivity, not a bound on the DL-073 bias. Both stay open; the fix is deferred to MS7 (DL-083 (2)). The margin (rate/SE at least 45 in magnitude, at least 21.6 under window shifts) is large, but the SE values are not trustworthy as written.
Reason:          project owner ruling after DL-110.
Options:         -
Chosen:          as above   Default from: user ruling; plan 4.3 G1, D8
Evidence:        DL-107, DL-110, results/A3/a3_sn_ramp.parquet (git-ignored).
Test:            no code change.
Status:          done; MS4 gate report and fresh-context review next
Commit/tag:      the commit that adds this entry

## DL-112  MS5 5a: sub-step plan docs/ms5_plan.md    [ID: D12, D18, D34, D36, T04, T05, T23]
Date:            2026-10-16        Author:
Decision:        None; no default, definition, plan text, D-item, model, surge class, path or control is changed. docs/ms5_plan.md lists sub-steps 5a to 5j (plan, A4 module, A4 run with K7/K8/K9/K11 values, S3 mean field, network code, network timing, S3 network with K8 at N = 5x10^4 and the K4-net status, sigma calibration, headline re-time, gate report), run-time expectations from DL-102 to DL-105 (Heun about 4x slower per step under 10 copies; the D36 24 h cap to be judged at 5f; all network figures UNVERIFIED), which runs need the clean machine, and the open items. No A4, S3 or network run was made.
Open items:      K4-net M2 coupling unsourced (default: recorded not run); K7 4.12 ms against the paper's 4.95 ms, UNVERIFIED, and the amplitude half of K7 assumed deferred to MS6 (UNVERIFIED reading); K10 at MS5 from A4, non-blocking (default); K5 definition; /permissions (DL-051); Defender exclusion; paths provisional until A4; possible private remote backup; sigma search rule and K8 comparison definitions (ours, UNVERIFIED).
Reason:          instruction of the project owner; 5a of docs/ms5_plan.md.
Options:         -
Chosen:          as above   Default from: plan Table 11.1 MS5, Table 7.1, Table 9.1
Evidence:        docs/plan.md (Table 11.1, 5.2 A4, 6.2, 6.3, 6.4, 7.1, 9.2, Table 9.1), docs/ms4_gate_report.md, docs/ms3_gate_report.md, DL-074 to DL-079, DL-102 to DL-111.
Test:            fast suite green (226 passed, 1 xfailed).
Status:          done (5a); 5b waits for the user
Commit/tag:      the commit that adds this entry

## DL-113  User rulings on MS5 open items 1 to 3; MS5 5b: analysis/hopf.py and configs/A4.yaml    [ID: D34, T05, CP1, CP11, CP15, CP26]
Date:            2026-10-16        Author:
Decision:        (a) K4-net: no source gives the M2 network coupling, so K4-net is recorded as not run (non-blocking, plan Table 11.1 MS5) unless a source appears. No coupling is entered. (b) K7: the blocking value stays the approved 4.12 ms (UNVERIFIED, DL-074 to DL-079), a documented departure from the paper's 4.95 ms. The amplitude half of K7 (squared amplitude linear in tau_d - tau_d^(H), no hysteresis) is deferred to MS6, where A5 and S4 live, because Table 7.1 lists K7 under A4, A5 and S3. This deferral is the owner's reading of the gate, not stated in the plan: a visible departure, UNVERIFIED, to be re-checked at MS6. (c) K10 is computed at MS5 from the A4 frequency as a non-blocking check and re-checked at MS6 (Table 7.1 assigns it to A6). (d) 5b: analysis/hopf.py takes (a1, a2, a3) numerically from the existing Jacobian (np.poly of jacobian_3d); Hopf where a1 a2 = a3 with a1, a3 > 0 (brentq); Im lambda = sqrt(a2). Ceni Eqs. 11-12 are not used.
Basis:           Owner ruling on D-1 to D-3 of docs/ms5_plan.md. 5b: plan 5.2 A4, Table 7.1 K7 to K9, K11, CP15, CP26.
Working values (UNVERIFIED, plan gives none): configs/A4.yaml grids (eta_bar 801 points on [-10, 10], spacing 0.025, the working "A4 grid step", fixed at MS7); J search range [-40, -0.5]; K9 grid 16 x 16 x 120 ratio points then Nelder-Mead; "on the edge" = refined maximiser within 1 percent of a range bound (EDGE_FRAC); widening = tau_d bounds x2 each side, J lower bound x2, at most twice. No run kind a4 is added (optional).
Checks made in tests, not an A4 run: Hopf at ref_ceni on the tau_d line gives 4.1209 ms (matches DL-074's 4.12); small K9 search at eta_bar = 1 gives 0.1453 at tau_d about 10 ms, J about -5.3, inside the ranges (a reading of the plan's reasoned claim, to be judged at 5c on the full grids).
Reason:          instruction of the project owner; 5b of docs/ms5_plan.md.
Options:         -
Chosen:          as above   Default from: owner ruling; ms5_plan D-1 to D-3
Evidence:        tests/test_hopf.py; docs/ms5_plan.md.
Test:            fast suite green (234 passed, 1 xfailed).
Status:          done (5b); 5c waits for the user
Commit/tag:      the commit that adds this entry

## DL-114  Owner ruling: the a4 run kind; MS5 5c code (analysis/hopf.run_a4, scripts/run_A4.py, configs/A4_grids.yaml)    [ID: D34, T05, CP15, CP26]
Date:            2026-10-16        Author:
Decision:        "a4" is added to config.RUN_KINDS (owner ruling), so A4 runs through the runner, the provenance record and the config hash. Run config configs/A4.yaml now holds only schema sections (run, model ref_devalle, robustness); the grids and K-check protocol moved unchanged to configs/A4_grids.yaml, and config.hash_view adds them to the hash for kind a4 (as DL-090 and DL-091 do for a2 and a0). Task: mprsurge.analysis.hopf:run_a4; driver scripts/run_A4.py publishes results/A4/a4_hopf_curves.npz. The grid values are the 5b working values, unchanged (UNVERIFIED).
Added working protocols (ours, UNVERIFIED; the plan gives none): Hopf planes traced at the ref_devalle values of the other two parameters; K8 'oscillatory' = fixed point unstable with a complex pair at tau_d = 5 ms, 'not at 50 ms' = fixed point stable (the limit cycle itself is S3, step 5d); K9 'no Hopf for J > 0' = no crossing with a1, a3 > 0 on a 20 (J in 0.5..40) x 4 (tau_d 1, 5, 10, 50 ms) x 3 (Delta 0.05, 0.3, 1) set of eta_bar scans; K10 = frequency of the leading complex pair over the oscillatory tau_d interval at ref_ceni (64 points), J dependence as (max - min)/mean over J in {-40, -30, -20, -10, -5} at tau_d 8, 20, 40 ms; K11 = Hopf crossing nearest J = 0- along J at Delta = 1e-4 for eta_bar {0.5, 1, 2, 4, 8} x tau_d {1, 5, 10, 50} ms.
Reason:          owner ruling; MS5 5c of docs/ms5_plan.md.
Options:         -
Chosen:          as above   Default from: owner ruling; plan 5.2 A4
Evidence:        tests/test_hopf.py (run kind, hash covers grids, toy-grid compute and evaluate).
Test:            fast suite green (237 passed, 1 xfailed).
Status:          done
Commit/tag:      the commit that adds this entry

## DL-115  MS5 5c: A4 run on the full grids, K7 to K11 values, eta_H, path status    [ID: D12, D34, T05, CP15, CP26, K7, K8, K9, K10, K11]
Date:            2026-10-16        Author:
Decision:        A4 run on the full configs/A4_grids.yaml grids, record results/A4/A4_0000_4ece63ed731f.json, status ok, wall 75.8 s (git-ignored outputs). No grid was tuned. Numbers:
  eta_H (ref_devalle, J -21, Delta 0.3, tau_d 5 ms) = 2.896046 (Im lambda 2.011 /tau). This equals the DL-098 scan value, and the scanned values of the map cells checked (Delta 0.01 and 0.6; tau_d 1, 5, 50 ms) agree with A4 to 6 digits. Path status: the headline P2 path is now A4 (configs/path_A4.yaml: eta_H, giving eta_start 1.396046 and eta_peak 4.896046, the numbers already used). configs/S5.yaml and the timing cells still say provisional until 5i (their hashes and tests pin it); the old and new paths are the same to 6 digits, so no verdict moves.
  K7: tau_d_H at ref_ceni = 4.1209 ms; against the approved 4.12 +/- 0.05 (UNVERIFIED): pass; against the paper's 4.95: -0.829 ms, outside 0.05 (information; the DL-079 departure stands). Fixed point is a stable focus at 3 ms (Re -0.054) and unstable at 8 ms (Re +0.084): linear stability only; the decay and the 2 percent hold are S3 (5d); the amplitude half is not judged (deferred to MS6, DL-113). No upper Hopf crossing up to 50 ms.
  K8: at ref_devalle the fixed point is unstable with a complex pair at 5 ms (Re +0.214 /tau, linear frequency 36.1 Hz) and stable at 50 ms (Re -0.069); the Hopf crossings along tau_d at eta_bar = 4 are at 1.756 and 36.79 ms; no Hopf for J > 0 in 240 cases. Pass (existence). Band 25 to 100 Hz: 36.1 Hz is inside (non-blocking; linear estimate, the cycle frequency is S3).
  K9: largest Delta/eta_bar 0.145309 at eta_bar = 1 (maximiser tau_d 10.06 ms, J -5.31), 2 (7.11 ms, -7.52) and 4 (5.03 ms, -10.63); spread 1.7e-15 (tolerance 0.002): ratio scaling passes; maximum matches 0.1453 within 0.002. All maximisers inside the ranges searched (tau_d 1 to 50 ms, J -40 to -0.5): no edge, no widening, none asymptotic. Pass.
  K11: Im lambda/(2 pi r*) on the J -> 0- branch at Delta = 1e-4: 20 of 20 branches found (J_H from -0.0005 to -0.0064), largest deviation from 1 is 7.1e-4 (tolerance 0.01). Pass (non-blocking).
  K10 (non-blocking): oscillatory interval 4.12 to 50 ms (end of range, not a Hopf point); frequency 21.0 down to 10.7 Hz, monotone decreasing, inside 5 to 30 Hz +/- 10 percent. J dependence FAILS the 10 percent limit: relative change over J -40 to -5 is 13.4 percent at 8 ms, 25.0 percent at 20 ms, 42.2 percent at 40 ms. By the plan this is non-blocking; K10 is re-checked from A6 at MS6 (DL-113 (c)). The definition of the J change is ours (UNVERIFIED). No debugging was started.
Basis:           Table 7.1; DL-113 rulings; the K10 and K11 protocols are ours (DL-114).
Reason:          instruction of the project owner; 5c of docs/ms5_plan.md. All blocking A4 checks (K7 existence parts, K8 existence, K9) pass; no debugging round used.
Options:         -
Chosen:          as above   Default from: plan Table 7.1; DL-113
Evidence:        results/A4/a4_hopf_curves.npz sha256 affbddcac9ae21954a59e4309c13a7caa097397ae38461ba7a15dea7490a5dc4; record A4_0000_4ece63ed731f.json.
Test:            fast suite green (237 passed, 1 xfailed).
Status:          done (5c); 5d waits for the user
Commit/tag:      the commit that adds this entry

## DL-116  MS5 5d: S3 mean-field runs, the s3 run kind, K7 and K8 time-series values    [ID: D12, D25, D26, D34, K7, K8, K10]
Date:            2026-10-16        Author:
Decision:        "s3" is added to config.RUN_KINDS (task simulate_mf:run_s3), as DL-114 did for a4. Cells: configs/S3_ceni.yaml (ref_ceni, tau_d 3, 4.95, 8 ms) and configs/S3.yaml (ref_devalle, tau_d 5, 50 ms), each 10 s at constant parameters (path I_step with I_amp 0 and t_on 0, hold 10 s; baseline_s stays at 5 s in the hash and is unused), D25/D26 solver settings (DOP853, rtol 1e-10, atol 1e-12, max_step 0.05 tau, delta0 1e-6 on v at t = 0), output every 1 ms. Start state (ours, UNVERIFIED): ref_devalle from Devalle's Fig. 3 state (R(0) = S(0) = 5 Hz, V(0) = 0, Table 7.1 K8); ref_ceni from its single fixed point, stable or not, plus delta0 (stable_fixed_point refuses the unstable 8 ms point). Series in results/S3/ceni and results/S3/devalle (git-ignored), summary results/S3/s3_mf_summary.json, one provenance record per cell. Readout definitions (ours, UNVERIFIED, in analysis/s3.py): final window = last 4 s in four 1 s windows; amplitude = peak-to-peak; 'decays' = final 1 s peak-to-peak of v below delta0; 'holds' = the four window amplitudes within 2 percent of their mean and mean above 1000 delta0; frequency = Hann-windowed FFT peak of r over the final 4 s (zero-padded x8), mean-crossing count as cross-check.
Numbers (wall 12.5 s for all five runs, three and two in parallel):
  K7 (ref_ceni): 3 ms: v decays (final-second peak-to-peak 0.0 against delta0 1e-6): pass. 8 ms: sustained oscillation, window amplitudes within 8.3e-6 of their mean (limit 0.02), v peak-to-peak 2.911: pass. Information: 4.95 ms (above our Hopf 4.1209 ms, so oscillating, not marginal): v peak-to-peak 1.995, frequency 20.5 Hz; 8 ms frequency 18.0 Hz (FFT; crossing count 17.97). The Hopf value was judged at 5c. The amplitude half (squared amplitude linear in tau_d - tau_d^(H), no hysteresis) is not judged (DL-113, MS6); the measured v peak-to-peak (4.95 ms 1.994719, 8 ms 2.910826) and r peak-to-peak (0.206636, 0.426567, in 1/tau) are saved in the summary.
  K8 (ref_devalle): 5 ms: limit cycle, window amplitudes within 9.2e-6 of their mean, v peak-to-peak 5.512, r peak-to-peak 1.262 /tau: pass. 50 ms: fixed point (final-second v peak-to-peak 0.0): pass. Peak frequency 36.27 Hz (FFT; 36.25 crossing count; A4 linear estimate 36.1 Hz): inside 25 to 100 Hz (non-blocking): pass.
  K10: unchanged from DL-115 (the plan's 5d part is the A4 Im lambda reading, already recorded; the J-dependence failure and its MS6 recheck stand). The 4.95 and 8 ms cycle frequencies above are information, not a K10 judgement.
  No check failed; no debugging round used. The network half of K8 (peak within 5 percent) is 5g.
Reason:          instruction of the project owner; 5d of docs/ms5_plan.md.
Options:         config kind s3 (chosen, as the plan allows 'if needed') against kind mf, which cannot take y0 or an unstable start.
Chosen:          as above   Default from: plan 6.2 S3, Table 7.1; DL-113
Evidence:        tests/test_s3_config.py; results/S3/s3_mf_summary.json; records ceni_0000_0de955d7d683, ceni_0001_52277c9529ac, ceni_0002_032f8992d047, devalle_0000_9e49def91dfc, devalle_0001_9a3f46a18b44.
Test:            fast suite green (241 passed, 1 xfailed).
Status:          done (5d); 5e waits for the user
Commit/tag:      the commit that adds this entry

## DL-117  MS5 5e: network code qif_network.py, run kind network    [ID: D28, D18, CP27, T51, DL-117]
Date:            2026-10-16        Author:
Decision:        src/mprsurge/qif_network.py per Table 6.1: Numba, float64, no fastmath, forward Euler at network.dt_tau (1e-3 tau), no prange (single thread whatever the pool sets; run._init_worker still sets the thread variables). Neuron dV/dt = V^2 + eta_bar(t) + Delta(t) q_j + J(t) s + I(t); q_j = tan(pi(2j-N-1)/(2(N+1))) (D28; a 'random' Lorentzian variant is built, Gaussian and uniform (S10) are refused). M3 synapse s <- s + (tau/tau_d)(-s dt + n_spikes/N). Crossing V >= V_peak: reset to V_reset, hold 2/V_cross, count the spike 1/V_cross after the crossing. V(0) uniform on [-100, 100] from the seed child; 2 s discarded before t = 0 (CP14). Readouts: r_N per rate_bin_ms bin (1/tau units), v_N mean over non-refractory neurons, s, the path columns, raster of 300 neurons (times and indices). config.RUN_KINDS gains "network"; run.TASKS maps it to qif_network:run_network; build_plan expands seeds for "network" as for mf_noisy (one cell per seed index, spawn_key [i]). The network has no noise term: the noise.sigma and Heun conventions are the mean field's (6.4) and are not used here. Floating-point settings (float64, fastmath false, numba version, thread variable, scheme, dt) go in the run record flags (R7). No M2 synapse (open item 1, T51, UNVERIFIED): model.type M2 raises ConfigError.
Not in the plan, ours (UNVERIFIED): hold and spike delay counted in whole steps, no sub-step carry-over; a pending spike is counted at the first step where its delay has elapsed and never on the crossing step; s(start) = 0 (an argument s0, used only by tests); raster neurons evenly spaced in j; r_N and v_N stamped at bin end; raster buffer sized at 4 spikes per neuron per tau per chunk, overflow raises.
Numbers:         Single neuron, N = 1, eta_bar = 1, J = 0: mean spike period 3.1420 tau against the analytic 2 atan(V_p/sqrt(c))/sqrt(c) + 2/V_p = 3.14159 (relative error 1.3e-4; test tolerance 1 percent, ours); 63 spikes in 200 tau against 63.7 predicted. Quantiles equal scipy cauchy.ppf(j/(N+1)) to 1e-9 for N = 1 to 1000. Mean-field match (time-mean r_N over the second half of 3 s after a 2 s discard, start s = r*): ref_devalle tau_d 50 ms N = 2000: 0.17830 against r* 0.17884 (0.3 percent); N = 1000: 0.17808 (0.4 percent; range of windows to 0.5); ref_ceni tau_d 3 ms N = 2000: 0.05014 against 0.05003 (0.2 percent). Test tolerance 2 percent of r*, ours: the plan gives none ('agreement very good for N > 10^4', Ferrara, single source). v_N is not compared: with the exclusion and V_p = 100 it sits about 14 percent above v* at devalle (-0.229 against -0.267), by construction.
Memory (N = 5x10^4): neuron state 5 arrays = 1.8 MB, per-chunk parameter arrays (200 bins) 0.64 MB, raster buffer 0.3 MB, outputs for a 10 s run (10^4 bins) 0.7 MB: estimate 3.5 MB for a 10 s, 1 ms-bin run; the 0.05 s test run peaks at 2.35 MB of numpy allocation (tracemalloc) against its estimate of 2.74 MB. The Python process itself (interpreter, numba, scipy) is not included and not measured. Nothing near the 16 GB limit. No timing claim (5f).
Reason:          instruction of the project owner; 5e of docs/ms5_plan.md.
Options:         Heun for the network (the task text mentioned 'the Heun kernel') against forward Euler: Table 6.1 specifies Euler (S13 varies dt), so Euler.
Chosen:          as above   Default from: plan 6.3 Table 6.1, D28 (confirmed)
Evidence:        tests/test_qif_network.py (8 tests).
Test:            fast suite green (249 passed, 1 xfailed).
Status:          done (5e); 5f waits for the user
Commit/tag:      the commit that adds this entry

## DL-118  MS5 5f: network timing under load, rows judged, D36 24 h cap judged for the first time    [ID: D36, D28, T23, T24]
Date:            2026-10-16        Author:
Decision:        No default, solver setting, plan text or ruling changed; no cut applied (section 9.3 not entered: every row passes). Implements 5f of docs/ms5_plan.md with the DL-102 to DL-105 conventions: per-run median pooled over all copies of 3 batches, divisor 10 on the per-run median measured under 10 concurrent copies (DL-103 (1)), launch rule prediction <= 1.5 x the Table 9.1 allowance (upper end). Code commit 4726e08 (cells net_1e3, net_1e4, net_3e4; network part kinds net and net_p2 in timing_families.yaml; D36 sum with lower and conservative figures; scripts/run_timing_5f.sh); tree clean (dirty = false) in every record. Raw outputs in results/timing/clean/ (net_<cell>.json alone, net_<cell>/workers_<n>.json, logs/, prediction_5f.txt), git-ignored.
Machine state:   Before the run: High performance plan, sleep never on AC, AC; Steam, Waterfox, Edge, VLC and Task Manager closed as the owner reported and checked by process list (six VS Code msedgewebview2 stay open as ruled). Defender exclusion for the repository and .venv: UNKNOWN (cannot be read without administrator rights, Get-MpPreference returns "Must be an administrator"; the owner's message did not settle whether it was added; nothing changed). Residual: EACefSubProcess and EOSOverlayRenderer-Win64-Shipping (EA app / Epic overlay) were among the top CPU processes in the machine_state records (11 to 22 percent of one logical core at the sample), not in the owner's list and not closed; CPU load before each cell 3 to 12 percent, after 0 to 11 percent. Ryzen 5 5600, 6 cores / 12 threads, so 8 and 10 workers use SMT siblings.
Cells:           P2 at ref_devalle, T_ramp 10 s, provisional eta path (re-time on the A4 path is 5i), 2,950 tau incl. the 2 s discard, forward Euler dt 1e-3 tau. Work 2.95e9 (N 1e3), 2.95e10 (1e4), 8.85e10 (3e4) neuron-updates. Cost per update is the cell wall over N x tau / dt. net_1e3 is ours (for S9 N = 1e3 and 3e3), UNVERIFIED as a plan cell. Per-run limit 3600 s; 7200 s for net_3e4 under 10 copies, raised because at a ten times slower kernel than R5's rate the loaded run would take about 3500 s; not needed (169 s measured).
Results:         Per-run median s, alone (3 repeats) / under 10 copies (3 batches), rate in updates/s, slowdown loaded over alone:
  net_1e3   3.31 / 5.95    8.9e8 / 4.96e8   1.80 x
  net_1e4   32.52 / 58.74  9.07e8 / 5.02e8  1.81 x
  net_3e4   96.23 / 169.27 9.20e8 / 5.23e8  1.76 x
  net_1e4 under 6 and 8 copies: 39.22 and 47.48 s per run; batch walls 39.63, 47.78, 58.97 s at 6, 8, 10 copies; throughput 545.0, 602.7, 610.4 runs/h; speed-up on one worker (110.7 runs/h alone) 4.92, 5.44, 5.51; efficiency 82, 68, 55 percent. 8 and 10 workers differ by 1.3 percent, a tie within the batch spread (up to 4 percent in one batch of net_3e4); 10 is kept, as in DL-103.
  The Numba network kernel slows 1.8 x under 10 copies; the Heun kernel slowed about 4 x (DL-105). The R5 rate of 0.5 to 1e9 updates/s per core is met alone (about 0.9e9) and under load (about 0.5e9). The loaded factor of 4 assumed in docs/ms5_plan.md is not met by the network kernel: that assumption was UNVERIFIED and is now replaced by 1.8.
Rows (prediction at 10 workers; limit 1.5 x allowance):
  Network S3 + S8 + S10 + S12 NC1 + K8 (5e4) + sigma baseline   471 s (7.9 min)   allowance 0.5 h   limit 0.75 h   PASS
  S9 finite size (4 N x 10 seeds)                                0.22 h (13.2 min) allowance 2 h     limit 3 h      PASS
  Work counts: row 1 about 2.4e12 updates (S3 6e10, K8 6e10, sigma 7e9, S8 1.24e12, S10 8.3e11, S12 1.7e11), plan 2.0e12 without S3; S9 4.05e12, plan 4.0e12. Ours, UNVERIFIED: S8 map cells at 3 seeds, S12 NC1 at N 1e4, K8 rate from the slower of net_1e4 and net_3e4, S9 N 3e3 rate from the slower of net_1e3 and net_1e4. The first row's parts: S8 247.6 s, S10 164.9 s, S12 33.3 s, S3 11.9 s, K8 11.9 s, sigma 1.4 s.
  All other rows unchanged from DL-104/DL-105 (single-run delta_0.01 and the S5 baseline mode N remain the two accepted exceptions).
D36 24 h cap:    Sum of the rows with a prediction, leaving out the single-run row and the duplicate headline-rate sweeps row (sweeps counted at the P5 rate): 8.71 h (lower bound). With each partial row (S11+S16, S2+S4 and S1, S13) taken at max(prediction, Table 9.1 allowance) in place of its missing run families: 10.33 h (conservative). Both are under the 24 h cap: PASS. Not complete: S1, S3 mean field, A1 to A6, S12 mean field, S13 ladders other than the Radau pass set, the network dt ladder, spectrograms and analysis have no count or cell, so the cap is read from the two bounds and is not a full judgement; the margin (13.7 h on the conservative figure) is large against what is missing (Table 9.1 gives those rows well under 3 h together at the allowances). The sum uses the 10-copy per-run medians; the Heun understatement of 3d is already in the clean rows (DL-104).
Reason:          5f of docs/ms5_plan.md; DL-105 (Heun loaded-rate item carried to MS5); plan 9.2 steps 1 to 3, Table 9.1, D36.
Options:         -
Chosen:          cut nothing   Default from: DL-103, DL-105
Evidence:        results/timing/clean/net_*.json, net_*/workers_{6,8,10}.json, logs/, prediction_5f.txt (git-ignored); tests/test_timing.py (network part kinds, update counts, D36 bounds, toy network cell); plan 9.2, Table 9.1.
Test:            fast suite green (255 passed, 1 xfailed) on the code commit 4726e08; this entry changes docs only.
Status:          done (5f); 5g waits for the user
Commit/tag:      the commit that adds this entry

## DL-119  MS5 5g: S3 network runs, K8 at N = 5x10^4, network parts of K7 to K9, K4-net status    [ID: D28, K7, K8, K9, K4, T51]
Date:            2026-10-16        Author:
Decision:        Network runs with qif_network (DL-117), kind network, configs/S3_net_ceni.yaml (ref_ceni, tau_d 3, 4.95, 8 ms), configs/S3_net_devalle.yaml (ref_devalle, 5, 50 ms), both N = 1e4, and configs/S3_net_k8.yaml (ref_devalle, 5 ms, N = 5e4). Each 10 s after the 2 s discard, constant parameters (I_step, I_amp 0, t_on 0 as the 5d cells), one seed (spawn_key [0], root 20261008), 10 workers (DL-118); the three configs are launched together by scripts/run_S3.py --network, which writes results/S3/s3_net_summary.json next to s3_mf_summary.json (git-ignored; records net_ceni_0000_3f4561d07a32, _0001_1d7353d4b3fc, _0002_73624487461f, net_devalle_0000_82a8c8cca980, _0001_0bdf9ad62b84, net_k8_0000_6d90ef8de3c5; all status ok). Readouts in analysis/s3.py (ours, UNVERIFIED): final 4 s, FFT peak frequency of r_N (as the mean-field 5d readout), r_N mean, fitted sinusoid peak-to-peak at the FFT peak (the plain peak-to-peak is inflated by bin noise). The same readouts are applied to the mean-field series, and the difference is network minus mean field over mean field. Network start V(0) uniform, s(0) = 0 (5e), not the mean-field 5d start.
Wall time:       71.0 s for all six runs, run together on 6 processes; the 50000-neuron run took 69 s (6e10 updates, 8.7e8 /s) and sets the wall; the 1e4 runs took 16.5 to 17.4 s. The 5f combined row (471 s) holds S8, S10, S12 and sigma as well and is not comparable; its S3 and K8 parts were 11.9 s each with perfect packing over 10 workers (23.8 s). The measured 71 s is 3 times that, because the single 5e4 run cannot be split. Within the launch rule and the 0.75 h limit by a large margin.
Numbers (net / mean field; frequency Hz, r_N mean in 1/tau, fitted r peak-to-peak in 1/tau):
  ref_ceni 8 ms:    f 18.00 / 17.96 (+0.2 percent); mean 0.0915 / 0.0884 (+3.6); ptp 0.278 / 0.261 (+6.8).
  ref_ceni 4.95 ms: f 20.62 / 20.53 (+0.5); mean 0.0761 / 0.0704 (+8.1); ptp 0.193 / 0.163 (+18.3).
  ref_ceni 3 ms:    mean 0.05001 / 0.05003 (-0.04); no mean-field oscillation. Network r_N std 0.0067, fitted ptp at the largest FFT line (23.1 Hz) 0.0016 (finite-N noise), 170 times below the 8 ms cycle.
  ref_devalle 5 ms, N = 1e4: f 36.33 / 36.27 (+0.2); mean 0.2628 / 0.2602 (+1.0); ptp 0.767 / 0.750 (+2.4).
  ref_devalle 5 ms, N = 5e4: f 36.24 / 36.27 (-0.09); mean 0.2625 / 0.2602 (+0.9); ptp 0.761 / 0.750 (+1.5).
  ref_devalle 50 ms: mean 0.1786 / 0.1788 (-0.13); fixed point in the mean field; network r_N std 0.0108 (noise).
Checks:
  K8 network (blocking, Table 7.1 'network peak within 5%'; N = 5e4): peak 36.24 Hz against 36.27 Hz, difference -0.09 percent, tolerance 5 percent (plan): PASS. 'Peak' is read as the spectral peak frequency, ours, UNVERIFIED. The amplitude differences above are information, not a check. The 25 to 100 Hz band (non-blocking): 36.24 Hz inside. The 50 ms network cell sits at the mean-field rate with noise only: information.
  K7 network: the plan gives no network criterion (K7's 'decays at 3 ms, holds within 2 percent at 8 ms' is the mean-field reading of 5d; a finite-N run neither decays to zero nor holds to 2 percent). NOT JUDGED. Information as above: the network oscillates at 8 and 4.95 ms with the mean-field frequency within 0.5 percent and is at the fixed-point rate with only noise at 3 ms. A proposed reading, UNVERIFIED and not used: 8 ms fitted ptp above 10 times the 3 ms fitted ptp (here 174 times).
  K9 network: the plan has no network part (K9 is A4 only, Table 7.1). Nothing run. The A4 verdict of DL-115 stands.
  K4-net: not run, M2 network coupling unsourced (open item 1, T51); non-blocking (DL-113). No source was supplied.
  K7 amplitude half: deferred to MS6 (DL-113). Sigma: not judged here (5h).
  No blocking check failed; no debugging round used.
Reason:          instruction of the project owner; 5g of docs/ms5_plan.md.
Options:         one runner call for all six cells (the sweep covers one axis and one N only) against three configs launched together (chosen).
Chosen:          as above   Default from: plan 6.2 S3, Table 7.1 K8; DL-113, DL-118
Evidence:        tests/test_s3_config.py (network cells, readouts, K8 judgement on synthetic signals); results/S3/s3_net_summary.json.
Test:            fast suite green (256 passed, 1 xfailed).
Status:          done (5g); 5h waits for the user
Commit/tag:      the commit that adds this entry

## DL-120  MS5 5h: sigma calibration run, N = 1e4 baseline at the P2 start state, sigma NOT committed (waits for ruling)    [ID: D18, CP21, T04, D27, CP14]
Date:            2026-10-16        Author:
Decision:        Calibration run and fit done; the number is reported and NOT written into any config: the plan gives the matching target ("baseline std of v matches one N = 1e4 network baseline run") but no tolerance or acceptance rule, so by the instruction for 5h the commit waits for the owner's ruling. noise.sigma stays null in base.yaml. No default changed.
Runs:            configs/sigma_net.yaml (network, N = 1e4, ref_devalle, eta_bar = eta_H - 1.5 = 1.3960461989737856 from A4, J -21, Delta 0.3, tau_d 5 ms, I_step with I_amp 0 = constant parameters, 2 s discard then 5 s, 10 seeds on 10 workers); configs/sigma_mf.yaml (mode N Heun dt 1e-3 tau, same state, 10 seeds, trial sigma 1e-3 and 1e-2, then the fitted sigma as check); scripts/calibrate_sigma.py; analysis/sigma.py; tests/test_sigma.py. Series in results/sigma/ (git-ignored), summary results/sigma/sigma_summary.json, records in results/sigma/*/ with provenance.
Method (ours, UNVERIFIED, the plan gives no search method): baseline std of v = sample std (ddof 1) of the 1 ms v series over the 5 s; network v is v_N, the mean over non-refractory neurons per 1 ms bin, the mean-field v is the instantaneous output at 1 ms (the two sampling conventions differ). Mean-field std taken as linear in sigma through the origin and sigma = target std / (std per unit sigma). Target = seed index 0, the plan's single baseline run; seeds 1 to 9 are extra, for the spread. The mean-field std per unit sigma is the mean over 10 seeds of both trial points.
Results:         Network baseline std of v: seed 0 0.038824; 10 seeds mean 0.038522, seed-to-seed sd 0.000322 (0.8 percent).
  Mean-field std per unit sigma 0.62229 (trial points 1e-3 and 1e-2 differ by 3e-6 relative: linear to numerical precision; seed sd 3.5 percent of a single mean-field run).
  sigma (seed 0 target) = 0.06239. sigma (10-seed network mean target) = 0.06190. sigma matched per network seed: mean 0.06190, sd 0.00052 (0.8 percent), range 0.06091 to 0.06251. Units: v-units per sqrt(tau), the dv = f dt + sigma dW convention of DL-072, UNVERIFIED.
Check:           Mean-field noisy run at sigma = 0.06239, 10 seeds: std of v 0.038852, seed sd 0.001384 (sem 0.00044). Against the network seed 0: +0.07 percent; against the network 10-seed mean: +0.86 percent; both well inside the mean-field seed sd (3.6 percent). This check is nearly circular (the fit uses the same quantity); it confirms linearity and the seed noise, not an independent validation. S8 (MS10) is the independent check (CP21). Nothing was tuned to make the check pass; no debugging round used.
Wall time:       21.5 s for the calibration script on 10 workers (network 10 seeds, 20 trial and 10 check mean-field runs).
Reason:          5h of docs/ms5_plan.md; plan 6.4, D18, CP21, T04.
Options:         (a) commit sigma = 0.06239 (the plan's single seed-0 baseline); (b) commit 0.06190 (10-seed network mean, less sensitive to the one seed; differs by 0.8 percent); (c) a different match statistic (spectrum, band-limited std) or a tolerance rule. All three are inside the seed spread of the mean-field check.
Chosen:          none; waits for the owner's ruling   Default from: -
Evidence:        results/sigma/sigma_summary.json (git-ignored); tests/test_sigma.py.
Test:            fast suite green (260 passed, 1 xfailed).
Status:          done (5h) except the commit of sigma; waits for the user
Commit/tag:      the commit that adds this entry

## DL-121  MS5 5i: owner ruling on sigma, sigma = 0.0624 committed to configs/base.yaml    [ID: D18, CP21, T04, DL-120]
Date:            2026-10-16        Author:
Decision:        noise.sigma = 0.0624 in configs/base.yaml (was null). This is option (a) of DL-120: the match to the plan's single baseline run (network seed 0, N = 1e4, P2 start state of ref_devalle). The fitted value was 0.06239; the owner's ruling is the rounded 0.0624 (0.02 percent above the fit, far inside the mean-field seed spread of 3.6 percent). 0.5 sigma and 2 sigma are derived by noise.sigma_factor, not calibrated. Units: v-units per sqrt(tau), the dv = f dt + sigma dW convention of DL-072, UNVERIFIED.
Recorded:        (1) The 10-seed network mean target (option (b), sigma 0.06190, network std 0.038522 +/- 0.000322 seed-to-seed sd) differs from the committed value by 0.8 percent (committed value 0.8 percent above it). (2) The DL-120 mean-field check (std of v 0.038852 at sigma 0.06239, +0.07 percent against seed 0) is nearly circular: it uses the same quantity as the fit. It confirms linearity and the seed noise, not the value. (3) The independent check of sigma is S8 at MS10 (CP21); sigma stays UNVERIFIED until then. The matching rule (sample std ddof 1 of the 1 ms v series over 5 s; mean-field std linear in sigma) is ours, UNVERIFIED (DL-120).
Changed:         configs/base.yaml noise.sigma null -> 0.0624. The pinned base-config hash in tests/test_config.py (BASE_HASH) changes with it, deliberately: 12eab64876ba... -> 754230ce4ee3... . configs/timing/mode_n.yaml keeps its timing-only placeholder sigma 1e-3 (timing does not depend on sigma; scripts/time_one_run.py still flags it as not calibrated). configs/sigma_mf.yaml and sigma_net.yaml are unchanged (calibration inputs).
Reason:          instruction of the project owner after DL-120; 5i/5h of docs/ms5_plan.md.
Options:         -
Chosen:          as above   Default from: owner ruling on DL-120 option (a)
Test:            fast suite green with the BASE_HASH update (see DL-122 for the final count).
Status:          done
Commit/tag:      the commit that adds this entry

## DL-122  MS5 5i: path status provisional -> A4 in S5.yaml and the timing cells, headline re-time on the A4 path    [ID: D12, D36, T23, T24]
Date:            2026-10-16        Author:
Decision:        (part 1, prepared before timing) The eta path status of the S5 headline and the timing cells is A4. configs/S5.yaml now gives path.eta_H = 2.8960461989737856 (A4, DL-115, configs/path_A4.yaml) instead of the explicit 1.396046 / 4.896046; resolve_config derives eta_start = eta_H - 1.5 and eta_peak = max(4, eta_H + 2) (D12) and status "A4". No default of the plan changed; the path numbers move by under 6e-7 (rounding of the old 6-digit entries). Results part: see below once timed.
Changed:         configs/S5.yaml (explicit start/peak -> eta_H). Cells with their own D12 path (delta_0.01, delta_0.6, delta_0.01_td1, delta_0.01_td50, delta_0.6_td1) now give path.eta_H from hopf.lowest_eta_hopf on the A4 eta_bar grid (0.3934525674725519, 4.7744298595858385, 0.8380331229059412, 0.25099487389417097, 7.786040869518495), each equal to the DL-098/DL-100 scan to 6 digits. delta_0.6_td50 has no Hopf crossing in A4 (returns None): it drops its explicit path and inherits the headline eta_H (CP20, DL-100 rule unchanged). m2_ramp keeps its explicit A1 path (sets eta_H null, status explicit). Cells inheriting from S5 (headline, mode_n, net_1e3/1e4/3e4, p5_1000, radau_*) change status only. Comments updated in configs/timing/*.yaml, configs/path_A4.yaml; scripts/time_one_run.py writes an A4 note into the timing record flags (was provisional only). Hashes: every cell, m2_ramp included, changes config hash (status/eta_H keys, and base sigma from DL-121); the clean (DL-104/118) timing records keep their old hashes and stay untouched in results/timing/clean/. Tests changed deliberately: tests/test_timing_cells.py (provisional -> A4 in five asserts, headline path to 1e-6, eta override test uses path.eta_H, delta-cell comparison also ignores eta_H), tests/test_timing.py (flag A4), tests/test_hopf.py (comment only); new test_cell_paths_equal_the_d12_rule_from_the_a4_eta_H. The 3d numbers (results/timing/*.json) and the clean re-time (results/timing/clean/) are not edited; the A4 re-time goes to results/timing/a4/ (scripts/run_timing_5i.sh).
Machine state:   Owner reported closed: Epic, EA, LM Studio, NordVPN, WARP, DCv2, Waterfox, Edge, VLC, Steam, Task Manager. By process list before the run: the apps were gone, but background services remained: DCv2 (1 process, still listed; the owner's closing did not take effect or it restarted), warp-svc, nordsec-threatprotection-service, NordUpdateService; six VS Code msedgewebview2 as ruled in DL-118; this Claude session. High performance plan. Defender exclusion: UNKNOWN (as DL-118). List saved in results/timing/a4/machine_state_before.txt. Code commit 342aea3, tree clean (dirty false) in the records.
Results:         Headline on the A4 path (results/timing/a4/headline.json, headline/workers_10.json, logs/, prediction_5i.txt; git-ignored). Against the provisional-path clean re-time of DL-104 (results/timing/clean/, untouched):
  alone, median of 3:           99.30 s   against 101.4 s   (-2.1 percent; s per 1e4 tau 60.18)
  10 copies, per-run median:    158.13 s  against 162.81 s  (-2.9 percent)
  10 copies, batch wall median: 158.77 s  against 163.32 s
  throughput at 10 copies:      226.7 runs/h against 220.4 runs/h (+2.9 percent)
  The paths are identical to 6 digits, so the difference is not the path. It is the same size as run-to-run and machine-state differences (batch spread up to 1.6 percent in the clean run); the machine state differed slightly (the DL-104 run had EA and Epic overlay processes among the top CPU users). Not attributed further.
  Prediction (10 copies, divisor 10, launch rule 1.5 x allowance), clean (DL-118) -> A4 re-time; only the cells re-timed are the headline, so only rows built on the headline rate move:
    single_run (max of the cells; delta_0.01)   178.3 s -> 178.3 s    FAIL -> FAIL (accepted exception, DL-105; delta_0.01 not re-timed); headline cell 101.4 -> 99.3 s PASS
    sweeps_headline_rate S2/S5/S6               0.97 h -> 0.94 h      PASS -> PASS
    map1 S7 (weighted 900 cells)                4.44 h -> 4.40 h      PASS -> PASS
    map2 S7                                     2.20 h -> 2.14 h      PASS (at the allowance) -> PASS
    s11_s16                                     0.36 h -> 0.35 h      PASS (partial) -> PASS (partial)
    s1_s4                                       204.0 s -> 203.3 s    PASS (partial) -> PASS (partial)
    s13                                         473.6 s -> 471.9 s    PASS (partial) -> PASS (partial)
    s5_baseline_mode_n (120.6 s, FAIL, accepted exception DL-105) unchanged: mode_n not re-timed. sweeps_p5_rate, the two network rows and network_s9 unchanged (1.14 h, 471.0 s, 0.22 h; PASS).
  No row changes verdict. The two failing rows are the two accepted exceptions of DL-105, unchanged. Map-1 weighted figure: re-derived by the prediction, 4.40 h (was 4.44 h); the corner and map cells were not re-timed, since their paths moved by under 6e-7 (their timings carry the old config hashes; the hashes differ only by status and eta_H keys and the DL-121 sigma).
D36 24 h cap:    Lower bound 8.71 h -> 8.60 h; conservative 10.33 h -> 10.23 h; cap 24 h: PASS (same two bounds and same incompleteness as DL-118).
Reason:          5i of docs/ms5_plan.md; DL-103 to DL-105 conventions.
Options:         -
Chosen:          no cut, nothing changed beyond the path status   Default from: DL-118
Test:            fast suite 261 passed, 1 xfailed (before the timing run; this entry changes docs only).
Status:          done (5i); 5j waits for the user
Commit/tag:      the commit that adds this entry

## DL-123  MS5 5j: fresh-context review and gate report, MS5 gate passed with departures    [ID: K7, K8, K9, K10, K11, K4, D18, D36, DL-112 to DL-122]
Date:            2026-10-17        Author:
Decision:        docs/ms5_gate_report.md written. Verdict line: "MS5 gate: passed with departures". No default, plan text or ruling changed; no tag, no push; MS6 not started.
Review:          A subagent that had not seen the work read docs/ms5_plan.md, DL-112 to DL-122, the K7 to K11 rows, the MS5 gate wording and the saved results. No material numeric mismatch. Findings (committed DL entries not edited; corrected in the report): (1) DL-119 gives 170 and 174 for the 8 ms to 3 ms network noise ratio; saved values give 178 (167 against the mean-field fitted peak-to-peak); information only. (2) The G0 "review of units and tau placement" after the K10 J-dependence miss was not done (DL-115 silent); now carried forward. (3) The sigma check reuses the same ten seed indices as the trial runs, so it is more circular than DL-120/121 say; sigma stays UNVERIFIED until S8 at MS10. (4) K7 pass against 4.12 ms is consistency, not independence (value is A4-derived). (5) K9 "no Hopf for J > 0" sits on the K8 line in DL-115; "tau_d > 0" is not tested. (6) A4, S3 and sigma records have git.dirty true; not examined.
Reason:          5j of docs/ms5_plan.md; Table 11.1 MS5.
Options:         -
Chosen:          as above   Default from: plan Table 11.1, Gate G0; DL-113
Test:            fast suite 261 passed, 1 xfailed.
Status:          done (5j); waits for the owner on the replication-pass tag
Commit/tag:      the commit that adds this entry; no tag

## DL-124  MS5 5k: dirty-tree check, clean-tree re-runs of A4, S3 and sigma (identical), K10 units review (no error)    [ID: K7, K8, K10, D18, DL-115, DL-116, DL-119, DL-120, DL-123]
Date:            2026-10-17        Author:
Decision:        No default, plan text, ruling or recorded value changed. docs/ms5_gate_report.md updated (section 5k, items 3 and 6, carried-forward K10 line). Verdict stays "MS5 gate: passed with departures". Local tag replication-pass created on the commit that adds this entry (owner's authorisation for this tag, conditional on no discrepancy; none found). No push; MS6 not started.
Dirty tree:      Records store only git.dirty = true and the parent commit (no diff hash, no file list). From the history, each run was made before the commit that adds its code: A4 (record f92a691) before b0ff998; S3 mean field (b0ff998) before 6e62da0; S3 network (68f7ede) before 96d40b4; sigma (96d40b4) before 510fe8a. Tracked files were modified in every case (config.py, run.py, simulate_mf.py, hopf.py, analysis/s3.py), besides new untracked files. The exact diffs cannot be recovered, so the results could in principle have differed from a clean-tree run: re-runs done.
Re-runs:         From HEAD fffb63e, clean tree, same configs and seeds, output.dir overridden to results/rerun (git-ignored, next to the originals, which are untouched). A4 (1), S3 mean field (5), S3 network (6), sigma network (10), sigma mean-field trial (20) and check at sigma 0.06238876981899888 (10). 52 npz outputs: all arrays identical (shape, dtype, values), A4 verdicts equal, sigma refit equal to the stored value, per-seed stds equal. Record config differs only by base noise.sigma (null -> 0.0624, DL-121; unused in these runs) and output.dir, hence new record names/hashes. New records dirty = false. Wall times: about 75 s (A4), minutes for the rest, as announced.
K10 review:      Units and tau placement checked in analysis/hopf.py, models/mpr3d.py, configs/A4_grids.yaml: tau_d_tau = tau_d_ms / tau_ms, beta = 1/tau_d_tau, f_Hz = Im lambda / (2 pi tau_ms 1e-3), plan 3.3 mapping; at the Hopf point sqrt(a2) equals the eigenvalue Im part (1.32059, 21.018 Hz). No error found. Definition observations (ours, UNVERIFIED, not applied): the J sweep includes stable-focus points (damped frequency) and holds eta_bar fixed so r* moves 0.027 to 0.154; excluding stable points still leaves 13.2 percent (8 ms) and 24 percent (20 ms). K10 value stays as in DL-115, non-blocking, recheck at A6 (MS6).
Reason:          instruction of the project owner, 5k before the replication-pass tag; DL-123 finding (6) and the G0 review (plan 3.3, Gate G0).
Options:         -
Chosen:          as above   Default from: plan Gate G0, DL-123
Test:            fast suite 261 passed, 1 xfailed.
Status:          done (5k)
Commit/tag:      the commit that adds this entry; local tag replication-pass

## DL-125  MS6 6a: sub-step plan docs/ms6_plan.md    [ID: D23, D40, K7, K10, CP23, T21, T56, T66]
Date:            2026-10-17        Author:
Decision:        docs/ms6_plan.md written: MS6 goal and gate as the plan states them (A5 vs S4 amplitudes within 2 percent, points next to eta_H excluded; frequency map done), inputs from MS5, deferred items (K7 amplitude half, K10 recheck from A6, 3d/5g amplitudes), sub-steps 6a to 6h, run-time expectations, machine state, open items. No default, plan text, ruling or recorded value changed. Nothing run. No tag, no push; 6b not started.
Basis:           Table 11.1 MS6, 5.2 A5 and A6, 6.2 S4, 4.3 and Table 11.2 G2, 7.2 D40, Table 7.1 K7 and K10; DL-113, DL-115, DL-123, DL-124.
Working values (UNVERIFIED, plan gives none, in the plan as defaults): exclusion width 1 S4 step = 0.1 in eta_bar; network steps k = 0, 4, ..., 56 plus the last; S4 tau_d sweep at ref_ceni for the K7 amplitude cross-check; K7 fit window and tolerance; D40 "confirmed" test; G2 readings.
Reason:          instruction of the project owner; 6a.
Options:         -
Chosen:          as above   Default from: docs/ms5_plan.md structure; plan Table 11.1
Test:            fast suite 261 passed, 1 xfailed.
Status:          done (6a); questions D-1 to D-5 open, D-2 and D-3 before 6c
Commit/tag:      the commit that adds this entry; no tag

## DL-126  MS6 6b: owner rulings D-1 to D-5, A5 periodic-orbit continuation run (Julia/BifurcationKit), supercritical at ref_ceni    [ID: D23, D40, K7, K10, CP23, DL-125]
Date:            2026-10-17        Author:
Decision:        (1) Owner rulings on DL-125, recorded as given. (2) 6b done: A5 run, results/A5/a5_cycles.npz. No plan text, D-item or earlier default changed. No tag, no push; 6c not started.
Rulings:         D-1  G2 is judged by the owner at the gate. Metrics for (a) and (b) are reported in the plan's own wording, (c) as "not rejected" (the plan's default, D22). My reading of each is stated in the report; no thresholds invented.
                 D-2  Addition to the S4 row (not in plan 6.2, which varies only eta_bar): a small mean-field tau_d sweep at ref_ceni in step 6c, so the K7 amplitude half has a time-domain check besides A5. Design in docs/ms6_plan.md (UNVERIFIED), a few runs.
                 D-3  "Next to eta_H" = within one S4 step (0.1 in eta_bar), as CP23 says. The K7 fit window and tolerance are fixed here, before 6e looks at any data, as UNVERIFIED defaults, and are not tuned afterwards: fit A^2 against tau_d - tau_d^(H) on points 0.1 to 1.0 ms above tau_d^(H); pass if R^2 >= 0.99 and the largest fit residual is under 2 percent of the largest A^2 in the window. The 2 percent rule is a relative difference of amplitude (not of A^2).
                 D-4  D40 is confirmed if the A6 frequency at ref_devalle in the oscillatory region is >= 25 Hz (the DL-040 overturn test). The owner records the confirmation; Claude does not.
                 D-5  Both K10 J-definitions recorded at A6; K5 stays open. The /permissions check, the Defender exclusion and the remote backup are answered at the gate.
A5 method:       src/mprsurge/analysis/continuation/a5_cycles.jl: PALC fixed-point continuation of the M3 right-hand side (plan 3.1, tau units); first Hopf point; normal form from get_normal_form; cycles by orthogonal collocation Collocation(Ntst=40, m=4, meshadapt=true), PALC, from the Hopf point in both directions; Floquet stability from the package (detect_bifurcation=1). Julia writes CSV plus a5.json; scripts/run_A5.py validates (julia_io.load_a5) and analysis/a5.py builds the arrays. Julia 1.10.11, BifurcationKit 0.8.7, Manifest sha256 pinned. Branches: tau_d at ref_ceni (eta 1, J -20, Delta 0.05, tau_d/tau 0.1 to 1.0), eta_bar at ref_devalle (J -21, Delta 0.3, tau_d 5 ms, eta_bar 0 to 8). Numerical settings and tolerances (Hopf match rtol 1e-4, criticality parameter tolerance 1e-3) UNVERIFIED working values.
Result:          Supercritical at ref_ceni: package normal-form verdict SuperCritical (a = 0.3947); no cycle at tau_d below the Hopf point (cycle branch starts at tau_d/tau 0.412092 against Hopf 0.412087); no fold of cycles; cycles stable along the branch. Also SuperCritical at ref_devalle (no fold, stable, to eta_bar 8, no second Hopf found on 0 to 8). Hopf points equal A4: ceni 4.120866 ms against 4.120858 (rel 2.1e-6), eta_H 2.8960463 against 2.8960462 (rel 3.8e-8). Cycles at ref_ceni: v amplitude (max - min) 1.99455 at 4.95 ms (20.54 Hz), 2.91043 at 8 ms (17.97 Hz); S3 mean field 1.99472 and 2.91083. A_ref = 5.51136 (v max - v min, ref_devalle, eta_bar 4, tau_d 5 ms, 36.26 Hz); S3 5.512, 36.27 Hz. Peak-to-peak readout is ours, UNVERIFIED.
Oddities:        (1) The down direction from the Hopf point retraces the same branch (turn-around at the Hopf point, reported as a "fold" at 0.41238 and 2.8975, not counted as a fold of cycles); it serves as the criticality probe. (2) First draft read the Floquet stability wrongly (stable all false, attribute not forwarded by the branch wrapper); fixed before the committed run. One diagnostic look, as ruled.
Reason:          instruction of the project owner; 6b of docs/ms6_plan.md; Table 11.1 MS6; plan 5.2 A5.
Options:         -
Chosen:          as above   Default from: plan 5.2 A5; DL-074, DL-075, DL-125
Test:            fast suite 272 passed, 1 xfailed (261 + 11 new, test_a5.py).
Status:          done (6b). Code commit df4b98b; run from that clean tree (record A5_0000_506cf5745380.json, git.dirty false); results/A5/ git-ignored. Wall 53.7 s for the Julia run (compile included; not a timing cell).
Commit/tag:      the commit that adds this entry; no tag

## DL-127  MS6 6c: owner ruling on the ref_ceni tau_d sweep grid; S4 mean-field sweeps run    [ID: D23, D40, K7, CP23, DL-125, DL-126]
Date:            2026-10-17        Author:
Decision:        (1) Owner ruling, recorded as given: the ref_ceni tau_d sweep uses a finer grid near the Hopf point, with at least 6 points inside the pre-registered K7 fit window (0.1 to 1.0 ms above tau_d^(H) = 4.1209 ms), at least 2 points on the stable side below the Hopf point and 1 to 2 points above the window; up then down as in docs/ms6_plan.md; step length long enough for settling, justified below. The window, the R^2 >= 0.99 rule and the 2 percent residual tolerance of DL-126 D-3 are NOT changed. This replaces the 14-step design in the plan's S4 addition (4.0 to 6.0 ms, 20 s steps, five points in the window; UNVERIFIED working values of 6a). (2) 6c done: S4 mean field at ref_devalle and the ref_ceni tau_d sweep run. No D-item, plan text or earlier default changed. No tag, no push; 6d not started.
Grid (UNVERIFIED working values, mine within the ruling): ref_ceni tau_d = 3.8, 4.0 (stable side, 2) | 4.25, 4.35, 4.45, 4.6, 4.75, 4.9, 5.05 (inside the window 4.2209 to 5.1209 ms, 7 points) | 5.5, 6.5 (above, 2): 11 values, 22 steps up then down, top value run twice. Step 60 s (6000 tau), last 10 s read.
Settling basis: linearised Re lambda at ref_ceni (eta 1, J -20, Delta 0.05, M3 fixed point) is 0.0050 /tau at 4.25 ms, 0.0087 at 4.35, 0.0140 at 4.5 (-0.0049 at 4.0); weakest point of the grid is 4.25 ms. Growth from the delta0 = 1e-6 kick to a saturated cycle of v amplitude about 0.8: ln(4e5) / 0.005 = 2600 tau = 26 s; relaxation to the cycle at about 2 Re lambda = 0.01 /tau, time constant 1 s, about 7 s to reach 1e-3. Linear estimate, about 33 s in all, 60 s gives a factor 1.8. Checked on the data (drift below), not assumed.
S4 design (not in plan 6.2, UNVERIFIED, mine): state carried from step to step; start = stable fixed point at the first value; delta0 added to v at the start of every step (D26 per step; without it an unstable fixed point is never left); constant parameters inside a step; DOP853 rtol 1e-10 as run_mf. Devalle: eta_bar = eta_H + linspace(-2, 4, 61) with eta_H read from configs/path_A4.yaml (2.896046), 122 steps of 2 s, last 1 s read. Readouts (ours): v and r peak-to-peak and Hann-FFT peak of r over the read window; drift = peak-to-peak of v in the second half of the read window over the first half, minus 1. New: run kind s4 (simulate_mf.run_s4), schema section s4 (optional keys, in the hash for kind s4), analysis/s4.py, scripts/run_S4.py, configs/S4.yaml, configs/S4_ceni.yaml.
Result:          Run from the committed tree 3bfb5ab, git.dirty false in both records (devalle_0000_48a5a3bd19e9, ceni_0000_5ba1b35edd35). Wall: devalle 95.3 s, ceni 305.6 s, run in parallel as two processes, 307.6 s total (not a timing cell). Output results/S4/{devalle,ceni}/ (series) and results/S4/s4_summary.{npz,json} (per step: parameter, up flag, v and r peak-to-peak, v mean, frequency FFT and crossing, drift, decays; and up/down pairs); npz sha256 7c4527be...99b6f.
Information only (the 2 percent A5 comparison and the K7 amplitude judgement are 6e; nothing judged here):
                 ref_ceni, 9 cycle points 4.25 to 6.5 ms: up and down v amplitudes agree to 2e-7 or better (absolute), no hysteresis loop; no cycle at 3.8 and 4.0 (amplitude below 1e-5 after the kick, decayed); drift of the read window below 6e-5 at every cycle point, so the 60 s steps are settled. S4 against the A5 branch (PCHIP on the up branch, my interpolation): relative differences +2e-5 to +1.5e-4; e.g. 4.25 ms S4 0.82792 against A5 0.82791, 4.9 ms 1.94493 against 1.94471, 6.5 ms 2.75009 against 2.74985; frequency 20.97 against 20.98 Hz at 4.25 ms, 20.57 against 20.58 at 4.9 ms.
                 ref_devalle: up and down agree to 3e-4 relative or better from eta_bar 3.096 (0.2 above eta_H) to 6.9 (e.g. 4.096: 5.84239 up, 5.84223 down; 5.296: 10.17507, 10.17523). Next to eta_H the branches differ: 2.796: 0.0064 up, 0.0367 down; 2.896: 0.0760 up, 0.5511 down; 2.996: 1.3660 up, 1.3738 down. This is the 2 s step against critical slowing (the amplitude is still growing or decaying at the end of the step, drift -0.71 and -0.004 up, -0.71 and -0.16 down), the points CP23 excludes, not a persistent hysteresis loop. Against A5: 2.996: 1.3660 against 1.3724 (-4.7e-3); 3.096: 1.98514 against 1.98502 (+5.9e-5); 3.296: 2.92525 against 2.92483 (+1.4e-4); 4.096: 5.84239 against 5.84233; 5.296: 10.17507 against 10.17509; 6.896: 16.57095 against 16.56940 (+9e-5). At eta_H itself S4 0.0760 against A5 0.1100 (excluded). Frequency 31.97 Hz at eta_H against 32.01, 36.59 against 36.63 at 4.096.
Reason:          instruction of the project owner; 6c of docs/ms6_plan.md; Table 11.1 MS6; plan 6.2 S4.
Options:         -
Chosen:          as above   Default from: plan 6.2 S4; DL-125, DL-126
Test:            fast suite 278 passed, 1 xfailed (272 + 6 new, test_s4.py).
Status:          done (6c). Code commit 3bfb5ab.
Commit/tag:      the commit that adds this entry; no tag

## DL-128  MS6 6d: owner rulings on the S4 network steps and the two 6c design choices; S4 network sweep run    [ID: D23, K7, CP23, DL-125, DL-127]
Date:            2026-10-17        Author:
Decision:        (1) Owner rulings, recorded as given: (a) S4 network steps are 15, k = 0, 4, 8, ..., 56 of the 61 (eta_H is step 20, included), up and down as the plan specifies; no network tau_d sweep at ref_ceni, only the mean-field one of 6c. (b) The two 6c design choices stay, both UNVERIFIED: delta0 is added to v at the start of every step (reading of D26), and the top value is run twice (end of the up sweep, start of the down sweep). (2) 6d done, N = 10^4 (plan 6.3 / MS5 default), seed spawn key [0], dt 1e-3 tau, 2 s steps, last 1 s read, sigma-free network dynamics of 5e (no noise term). No D-item, plan text or earlier default changed. No tag, no push; 6e not started.
Design (not in the plan, UNVERIFIED, mine): new run kind s4_net (qif_network.run_s4_network), same kernel as run_network; state (V, refractory, pending spikes, s) carried from step to step; start V drawn from the seed child, s = the mean-field stable fixed-point s at the first value (the unread first second of step 0 is the transient); delta0 added to every V at the start of each step (network analogue of the mean-field kick; it is far below the finite-size fluctuation); no raster. New optional schema key s4.indices (positions kept from the 61-point grid, in the hash). Readouts are those of 6c (analysis.s4.step_table); the network v is the mean V of non-refractory neurons within the V_peak/V_reset cut, not the mean-field v, so v amplitudes differ in definition as well as by finite size. analysis.s4.net_vs_mf gives relative differences against the 6c mean-field table at the same value and direction. New: configs/S4_net.yaml, scripts/run_S4.py --net.
Result:          Run from the committed tree 2709b56, git.dirty false (net_0000_38692898ae60). Wall 63.4 s run, 64.5 s with summary (one process; not a timing cell). 30 steps x 2 s. Output results/S4/net/ and results/S4/s4_net_summary.{npz,json}; npz sha256 4183adae...2fd86.
Information only (the 2 percent A5 check is 6e; nothing judged):
                 Network against mean field (r peak-to-peak, eta_bar, network | MF): 3.296: 0.566 | 0.493 (+15 percent); 4.096: 1.433 | 1.376 (+4.1); 4.896: 2.344 | 2.373 (-1.2); 5.696: 3.186 | 3.430 (-7.1); 6.496: 3.963 | 4.508 (-12.1). Frequency (FFT): 33.59 | 33.59 Hz at 3.296; 36.71 | 36.59 at 4.096; 39.71 | 39.71 at 4.896; 45.33 | 45.33 at 6.496 (same to the 0.0 to 0.1 Hz FFT bin or better away from eta_H). v peak-to-peak: 3.311 | 2.925 at 3.296, 6.122 | 5.842 at 4.096, 14.58 | 14.93 at 6.496 (definition differs, see above).
                 Near eta_H (2.896, step 20): network r ptp 0.154 up, 0.159 down; MF 0.010 up, 0.071 down; frequency 32.09 Hz against 31.97. Below eta_H (0.896 to 2.496) the network does not rest: finite-size fluctuations give r ptp 0.04 to 0.06 and v ptp 0.22 to 0.31 at every step, no cycle, so the frequency readout there (FFT peak 100 to 460 Hz) is noise; the MF values there are 0. The finite-size noise floor is therefore about 0.05 in r ptp, which is the whole network amplitude at eta_H.
                 Up and down branches of the network agree: r ptp up against down at 4.096 1.433 | 1.427, 5.296 2.776 | 2.789, 6.496 3.963 | 3.966 (r ptp within 1 percent from 3.296 up; v ptp within 2 percent from 3.696 up, e.g. 14.58 against 14.56 at 6.496); no hysteresis loop in the network. Only at eta_H do the branches differ visibly: v ptp 1.071 up, 1.166 down, r ptp 0.154 and 0.159 (the point CP23 excludes). Frequency identical to the FFT bin from 3.296. Drift of the read window below 0.02 (absolute) at all cycle steps; the stable-side steps drift 0.1 to 0.18 because the signal is noise.
Reason:          instruction of the project owner; 6d of docs/ms6_plan.md; Table 11.1 MS6; plan 6.2 S4.
Options:         -
Chosen:          as above   Default from: plan 6.2 S4 (15 steps); DL-127
Test:            fast suite 281 passed, 1 xfailed (278 + 3 new in test_s4.py).
Status:          done (6d). Code commit 2709b56.
Commit/tag:      the commit that adds this entry; no tag

## DL-129  MS6 6e: owner rulings on the gate comparison; A5 against S4 check; K7 amplitude half (rule failed on residual)    [ID: D23, K7, CP23, DL-126, DL-127, DL-128]
Date:            2026-10-17        Author:
Decision:        (1) Owner rulings, recorded as given: (a) the 2 percent gate check compares A5 against the mean-field S4 on v (the quantity A5 and A_ref are defined on), with r reported alongside for information; (b) network amplitudes are information only, no 2 percent criterion; (c) the time estimate in docs/ms6_plan.md is corrected to count up plus down (S4 network row: 15 values = 30 steps, 6000 tau, about 60 s alone and 120 s loaded, not 3000 tau, 30 s and 60 s; measured 63.4 s in DL-128; correction noted in the file). (2) 6e done from saved results only, no new simulation. No D-item, plan text or earlier default changed. No tag, no push; 6f not started.
Design (mine, UNVERIFIED): analysis/cycle_check.py (pure) and scripts/run_A5_check.py, outputs results/A5/check/a5_check.{npz,json} plus a record (analysis only, no wall). A5 branch = cycles continued from the Hopf point (the supercritical side), PCHIP on parameter (tau_d in ms for ceni), NaN outside the branch range. Relative difference (S4 - A5) / A5 of v peak-to-peak (= A5 vmax - vmin), up and down S4 steps separately. Exclusion: |eta_bar - eta_H| <= 0.1 (steps 19, 20, 21 of the 61). Points below eta_H have no A5 cycle (NaN) and are not comparable. For ref_ceni no exclusion was applied (none ruled; the nearest point 4.25 ms is 0.129 ms above the Hopf point and settled, drift < 6e-5). The A5 cycle arrays carry v only, so r has no A5 value; S4 r peak-to-peak is in the json for information. Hysteresis tolerance is not in DL-126; I used the 2 percent amplitude rule with a 1e-3 amplitude floor (UNVERIFIED reading).
A5 vs S4:        ref_devalle: judged points eta_bar 3.096 to 6.896 (39 per direction, 78 in all). Max |rel diff| 1.84e-3 up, 6.8e-4 down, both at eta_bar 4.196; next largest 3.8e-4 up, 2.5e-4 down. 2 percent rule: PASS (both directions). Excluded (within 0.1 of eta_H = 2.896): 2.796 (S4 0.0064 up, 0.0367 down) and 2.896 (0.0760 up, 0.5511 down) have no A5 cycle at those values (branch starts at eta_H, interpolation NaN, no difference defined); 2.996: S4 1.3660 up, 1.3738 down against A5 1.3724, rel diff -4.7e-3 up, +9.7e-4 down. Reported, not judged. Points below eta_H (20 per direction) not comparable. Verdict (the gate item): pass, 1.84e-3 against 2e-2.
                 ref_ceni tau_d sweep (same rule, same interpolation): 9 cycle points per direction (4.25 to 6.5 ms), max 1.49e-4 up and down, PASS; 3.8 and 4.0 ms are below the Hopf point (no cycle, not comparable).
K7 amplitude:    Rules of DL-126 D-3 applied as logged: window 0.1 to 1.0 ms above tau_d^(H) = 4.120866 ms (A5/A4 value; 4.120858 in DL-115; same points), S4 ref_ceni sweep, 7 points in the window (4.25 to 5.05 ms), line A^2 = slope (tau_d - tau_d^(H)) + intercept.
                 Up sweep: slope 4.6043 per ms, intercept 0.1796, R^2 0.99691, largest residual 2.42 percent of largest A^2. Down sweep: identical to 7 digits (slope 4.60435, R^2 0.99691, residual 2.42 percent).
                 R^2 >= 0.99: PASS. Residual under 2 percent: FAIL (2.42 against 2.0). K7 amplitude linearity: FAIL on the residual rule, as logged; window and tolerances not changed.
                 No hysteresis: PASS. Up against down max relative difference 2.0e-7 over the oscillating points (largest absolute 1.6e-7 in the window), against 2 percent.
                 Cross-check A5: the same rules on the A5 branch at the S4 window values: slope 4.6033, R^2 0.99691, residual 2.42 percent (fail); on A5's own 22 points in the window: slope 4.644, R^2 0.99668, residual 3.74 percent (fail). So the miss is a property of the model branch, not of S4 settling or of one code path; S4 slope / A5 own slope 0.991.
                 Cross-check 3d (S3 mean field v peak-to-peak) against A5 at the same tau_d: 4.95 ms 1.994719 against 1.994553 (+8.3e-5); 8 ms 2.910826 against 2.910425 (+1.4e-4). 5g network r peak-to-peak (information only): 0.290 at 4.95 ms and 0.493 at 8 ms against mean field 0.2066 and 0.4266 (r, finite size and discrete 0.001 readout).
                 Diagnostic look (one, as pre-registered): residuals along the window run -2.0, -0.5, +0.8, +1.9, +1.8, +0.4, -2.4 percent, a systematic bow. A^2 is concave in tau_d: local slope of A^2 on the A5 branch 5.29 per ms at 0 to 0.05 ms above the Hopf point, 5.27 at 0.1 to 0.3, 4.82 at 0.3 to 0.6, 3.92 at 0.6 to 1.0; a quadratic fit on the window gives -1.15 (tau_d - H)^2 and an intercept near zero (-0.05). So A^2 is linear to the Hopf point as the normal form says, with a curvature that the 1 ms window is too wide to ignore at the 2 percent level. Stopped; whether the window or tolerance is revised is the owner's call (not mine).
Network (information only, no criterion): above eta_H + 0.1 (18 steps, 9 values, up and down): v peak-to-peak network against mean field, relative difference +13.2 percent at eta_bar 3.296, falling through zero near 4.5 to a minimum of -2.5 percent, then rising to +12.4 percent at 6.496 (max |diff| 0.132); r peak-to-peak max |diff| 0.157 (+15 percent at 3.296, -12 percent at 6.496, DL-128). Network v is the mean V of non-refractory neurons within the cut, so the definition differs as well as the size (DL-128). Noise floor below eta_H (10 steps): r peak-to-peak 0.042 to 0.057 (mean 0.052), v peak-to-peak 0.22 to 0.31 with no cycle. At eta_H: network r 0.154 up, 0.159 down; v 1.071 up, 1.166 down; mean field r 0.0096 up, 0.0713 down; v 0.0760 up, 0.5511 down; network amplitude at eta_H is about three times the noise floor in r but the mean-field value there is the 2 s critical-slowing point.
Reason:          instruction of the project owner; 6e of docs/ms6_plan.md; Table 11.1 MS6; plan 5.2 A5, 7.1 K7, CP23.
Options:         -
Chosen:          as above   Default from: DL-126 D-3 (rules), DL-125
Test:            fast suite 287 passed, 1 xfailed (281 + 6 new, test_cycle_check.py).
Status:          done (6e); gate item A5 vs S4 passed; K7 amplitude half: R^2 and hysteresis pass, residual rule fails (reported, not tuned). Code commit 9baf359.
Commit/tag:      the commit that adds this entry; no tag

## DL-130  MS6 6f: owner rulings on the DL-129 K7 outcome; post hoc near-Hopf fit (exploratory)    [ID: K7, D23, CP23, DL-126, DL-129]
Date:            2026-10-17        Author:
Decision:        (1) Owner rulings (a) to (c) on DL-129, recorded as given. (2) A labelled POST HOC fit added to scripts/run_A5_check.py (no new simulation). No D-item, plan text, window or tolerance changed. No tag, no push.
Rulings:         (a) The K7 amplitude-half residual miss (2.42 percent against the pre-registered 2 percent, DL-129) stays a REPORTED FAILURE. Window (0.1 to 1.0 ms above tau_d^(H)) and tolerances are not revised. The 2 percent tolerance was our own choice (UNVERIFIED, not in the plan). A^2 is concave in tau_d over the 1 ms window (DL-129 diagnostic look). A5 and S3 agree to about 1e-4 (8.3e-5 and 1.4e-4); R^2 (0.99691), no hysteresis and the existence of the supercritical Hopf (DL-126) pass.
                 (b) The hysteresis reading (up against down within 2 percent of amplitude, 1e-3 amplitude floor) is accepted as UNVERIFIED.
                 (c) POST HOC exploratory fit on the A5 branch, no new simulations, to show the near-Hopf linear regime. It does not replace the pre-registered result and cannot change the verdict.
POST HOC fit:    A^2 = slope (tau_d - tau_d^(H)) + intercept on A5's own points in the window 0.05 to 0.3 ms above tau_d^(H) = 4.120866 ms (window is the owner's example, UNVERIFIED): 11 points, slope 5.2866 per ms, intercept 0.0018, R^2 0.999984, largest residual 0.22 percent of the largest A^2 in the window. For comparison the pre-registered window gave slope 4.60, R^2 0.99691, residual 2.42 percent (DL-129). Exploratory only; the K7 amplitude half stays: R^2 pass, hysteresis pass, residual rule FAIL.
Reason:          instruction of the project owner; 6f of docs/ms6_plan.md; Table 7.1 K7.
Options:         -
Chosen:          as above   Default from: DL-126 D-3, DL-129
Test:            covered by the fast suite (see DL-131).
Status:          done
Commit/tag:      the commit that adds this entry; no tag

## DL-131  MS6 6f: A6 frequency map and K10 recheck; D40 evidence    [ID: D23, D40, K8, K10, CP23, DL-115, DL-124, DL-126, DL-130]
Date:            2026-10-17        Author:
Decision:        (1) A6 built and run: analysis/freq_map.py (pure), analysis/continuation/a6_freq.jl, scripts/run_A6.py, configs/A6.yaml, julia_io.load_a6, run kind "a6". Output results/A6/a6_freq_map.npz (sha256 0ac74bd9...5084), a6_summary.json, record A6_0000_daa85487fd0a.json, run from a clean tree (git.dirty false). (2) K10 recheck recorded under both J-change definitions (below); non-blocking, no debugging round. (3) D40 evidence reported, not decided. No D-item, plan text or earlier default changed. No tag, no push; 6g not started.
Grids (mine, UNVERIFIED, set in 6f; continuation only, so no Table 9.1 row): eta_bar slices 0 to 8 for Delta {0.05, 0.1, 0.3} at J -21 and tau_d {1, 2, 3, 5, 8, 13, 22, 36, 50} ms (27 slices); eta_bar slices at Delta 0.3 (the plan names none: UNVERIFIED), tau_d 5 ms, J {-40, -30, -21, -12, -5} (5); K10 slices at eta_bar 1, Delta 0.05, tau_d 1 to 50 ms, J {-40, -30, -20, -10, -5} (5). Method as A5 (first Hopf, collocation Ntst 40, up direction only). Contours are the crossings of the cycle frequency with 25 and 100 Hz along each slice; nothing is interpolated between slices. All 37 slices ran (3 K10 slices have no Hopf, below). Wall 68.8 s including Julia compile (not a timing cell).
Map:             25 Hz contour crosses the cycle branch in the Delta 0.05 plane for tau_d >= 3 ms (eta_bar 1.26 at 3 ms, 1.60 at 5, 2.38 at 8, 3.49 at 13, 4.60 at 22, 5.26 at 36, 5.52 at 50); Delta 0.1 for tau_d >= 5 ms (1.63 at 5 ms to 5.51 at 50); Delta 0.3 only at tau_d 13, 22, 36 ms (3.13, 4.40, 5.12). Elsewhere the whole branch lies above 25 Hz (lowest branch frequency at 1 ms: 31.6, 38.1, 52.0 Hz for the three Delta; Delta 0.3 at 50 ms starts at 27.7 Hz, Hopf at eta_bar 6.21). The 100 Hz contour does not occur on eta_bar 0 to 8: largest frequency 73.7 Hz (Delta 0.3, 1 ms, eta_bar 8) and 71.3 Hz in the (eta_bar, J) plane (J -5). (eta_bar, J) plane at tau_d 5 ms, Delta 0.3: 30.6 to 71.3 Hz, no 25 Hz crossing, Hopf eta_bar 4.03 (J -40) to 2.24 (J -5). Cycle branches stop short of eta_bar 8 for Delta 0.05 at tau_d <= 8 ms and Delta 0.1 at tau_d <= 3 ms (end at 4.6 to 7.7); the reason was not examined. One Hopf point on every eta_bar slice.
K10 (ceni, eta_bar 1, Delta 0.05, J -20): oscillatory interval 4.14 to 50 ms (first cycle point; Hopf 4.1209 ms; the branch reaches the end of the range, not a Hopf point). Cycle frequency 21.01 down to 9.75 Hz, inside 5 to 30 Hz +/- 10 percent (4.5 to 33): PASS. Monotone decreasing (largest increase 0 Hz on a 64-point grid, tolerance 1e-6 Hz UNVERIFIED): PASS.
                 J change, (max - min) / mean over J {-40, -30, -20, -10, -5}, limit 10 percent:
                   readout                                         8 ms                  20 ms                 40 ms
                   (1) linear Im lambda, all J (DL-115)            13.4% (5 J) FAIL      25.0% (5 J) FAIL      42.2% (5 J) FAIL      reproduces DL-115
                   (2) linear, unstable points only (DL-124)       13.2% (3 J) FAIL      24.6% (4 J) FAIL      40.1% (4 J) FAIL
                   (3) cycle frequency, J where a cycle exists     undefined (1 J)       6.5% (2 J) pass       7.4% (2 J) pass
                 Readout (3) does not cover J -40 to -5: at eta_bar 1 and Delta 0.05 there is no Hopf point on tau_d 1 to 50 ms for J -40, -10 and -5; J -30 has cycles only between 8.92 and 43.4 ms (two Hopf points). Cycles exist at 8 ms for J -20 only (17.98 Hz, v amplitude 2.909); at 20 ms for J -30 (13.82 Hz, amp 0.839) and -20 (12.96 Hz, amp 2.185); at 40 ms for J -30 (11.16 Hz, amp 0.246) and -20 (10.36 Hz, amp 1.318). So the linear J dependence of the damped frequency at stable points is real (readouts 1, 2), while the cycle frequency over the two J values that have a cycle changes 6.5 to 7.4 percent; the J -40 to -5 criterion cannot be evaluated on cycles. Sub-checks: band PASS, monotone PASS, J(1) FAIL x3, J(2) FAIL x3, J(3) pass x2 and undefined at 8 ms. K10 overall not passed under the plan's wording; non-blocking. Whether the definition changes is the owner's call (open item 5).
D40 evidence (not decided; DL-126 D-4): ref_devalle (eta_bar 4, J -21, Delta 0.3, tau_d 5 ms), cycle branch from eta_H = 2.8960 to eta_peak = 4.8960: frequency 32.0 Hz at the Hopf point to 39.7 Hz at eta_peak, 36.26 Hz at eta_bar 4 (v amplitude 5.511, equals A_ref); minimum over the oscillatory region 32.0 Hz, so >= 25 Hz everywhere (DL-040 overturn test not triggered); inside the 25 to 100 Hz band G (K8, non-blocking). The owner records the confirmation.
Observation:     The linear Hopf frequency at ref_devalle is 32.01 Hz (Im lambda 2.011 /tau divided by 2 pi tau; A5 and A6 agree), not 36.1 Hz as DL-115 and docs/ms6_plan.md say for Im lambda 2.011 /tau; 36.1 Hz is not what that number gives. Committed entries are not edited; the 36.26 Hz cycle frequency at eta_bar 4 may be the source of the figure. Reported for the owner.
Reason:          instruction of the project owner; 6f of docs/ms6_plan.md; Table 11.1 MS6; plan 5.2 A6, Table 7.1 K8 and K10.
Options:         -
Chosen:          as above   Default from: plan 5.2 A6, DL-115, DL-124, DL-126
Test:            fast suite 302 passed, 1 xfailed (287 + 15 new, test_freq_map.py).
Status:          done (6f); map done, K10 recheck recorded (not passed as worded, non-blocking), D40 evidence reported.
Commit/tag:      the commit that adds this entry; no tag

## DL-132  MS6 6g: owner rulings on K10, the A6 grids and D40; DL-115 frequency check; G2 metrics (not decided)    [ID: D40, K8, K9, K10, G2, CP23, DL-115, DL-124, DL-126, DL-131]
Date:            2026-10-17        Author:
Decision:        (1) Owner rulings (a) to (c), recorded as given. (2) 6g done from saved A4, A5, A6 and S4 results only, no new simulation; analysis in scripts/run_G2.py (results/G2/g2_metrics.json, record G2_0000.json) and tests/test_g2_freq.py. G2 is NOT decided here: the owner decides at the gate. No D-item, plan text or earlier default changed; committed entries not edited. No tag, no push; 6h not started.
Rulings:         (a) K10 keeps its definition from the plan and DL-115. Reported as NOT reproduced as worded: J dependence 13 to 42 percent for the linear definition (13.4, 25.0, 42.2 percent at 8, 20, 40 ms); the cycle readout is undefined over the full J range (DL-131). Non-blocking. The source claim is single-source (UNVERIFIED). Not revised to pass.
                 (b) The A6 grids (tau_d, J, eta_bar) and Delta = 0.3 for the eta_bar-J plane stay as the UNVERIFIED defaults chosen in 6f (DL-131).
                 (c) D40 CONFIRMED: the headline example (P2 at ref_devalle, T_ramp = 120 s, linear profile, I = 0) stands. The A6 cycle frequency at ref_devalle stays at 32.0 to 39.7 Hz across the oscillatory region (eta_H 2.896 to 4.896), so the DL-040 overturn test (spectral peak below 25 Hz) is not triggered.
Frequency check: DL-115 and docs/ms6_plan.md give 36.1 Hz as the linear Hopf frequency at ref_devalle. Im lambda / (2 pi tau) from the A4 Jacobian (hopf.leading_mode, J -21, Delta 0.3, tau_d 5 ms, tau 10 ms):
                   (a) at eta_H = 2.89605: Re lambda -1.5e-15, Im lambda 2.01120 /tau, 32.009 Hz.
                   (b) at eta_bar = 4 (ref_devalle's own point, unstable focus): Re lambda +0.21425, Im lambda 2.26626 /tau, 36.069 Hz.
                 Finding: the 36.1 Hz matches (b), the damped-focus frequency at eta_bar = 4, not (a). The plan's note pairs 36.1 Hz with Im lambda 2.011 /tau and eta_H, which is inconsistent: 2.011 /tau is 32.01 Hz, and 36.1 Hz is 2.266 /tau. Re lambda +0.214 in the same note is also the eta_bar = 4 value (at eta_H it is 0). So the note mixes the Hopf-point Im lambda with the eta_bar = 4 frequency and Re lambda. The Hopf-point frequency is 32.01 Hz (matches the A6 cycle start, DL-131). DL-131's guess that 36.26 Hz (cycle) was the source is not needed: the linear value at eta_bar = 4 is 36.07 Hz. K8's comparison of the 36.1 Hz linear estimate with the 36.27 Hz S3 peak (in the S3 entry) is correct as a value at eta_bar = 4. Not edited; to carry into the gate report.
G2 metrics:      (not decided; wording of plan 4.3, Table 11.2; readings marked UNVERIFIED where the plan leaves room)
                 Ranges used: Table 3.2 tau_d 1 to 50 ms, J -40 to -5, Delta 0.01 to 0.6, eta_bar from path (A6 used eta_bar 0 to 8, UNVERIFIED). A6 sampled tau_d at 9 values, Delta at 0.05, 0.1, 0.3 (tau_d slices), J at 5 values (Delta 0.3, tau_d 5 ms). Critical Delta: K9 (A4) gives max Delta / eta_bar = 0.14531 at eta_bar 1, 2 and 4 (maximisers tau_d 10.06, 7.11, 5.03 (as stored in the A4 npz, k9_tau_d_ms) and J -5.3, -7.5, -10.6, none on an edge), so Delta_c = 0.1453 eta_bar, e.g. 0.145 at eta_bar 1, 0.421 at eta_H 2.896, 0.581 at 4 (Delta 0.3 at eta_bar 4 is ratio 0.075).
                 (a) "limit cycle >= 25 Hz with Delta below critical": YES in the cells searched. All 32 A6 eta-slices (27 tau_d + 5 J) have cycle points >= 25 Hz, and at every one of those points Delta < 0.1453 eta_bar. Cases: ref_devalle 32.0 to 39.7 Hz on eta_bar 2.896 to 4.896 (Delta 0.3: Delta / eta_bar 0.104 at eta_H, 0.061 at 4.896, against 0.1453); Delta 0.3 at tau_d 1 to 36 ms and 50 ms (f max 33.9 to 73.7 Hz); Delta 0.1 and 0.05 at all tau_d (f max 33.8 to 73.5 Hz); all five J values (30.6 to 71.3 Hz). Not satisfied everywhere: at ref_ceni (eta_bar 1, Delta 0.05, J -20 and -30) cycles are 9.7 to 21.0 Hz, none >= 25 Hz (K10 slices); some slices begin below 25 Hz (Delta 0.05, tau_d >= 3 ms; Delta 0.3, tau_d >= 13 ms) and cross 25 Hz at the contour values of DL-131.
                   Readings, UNVERIFIED (plan does not say): (i) existence, at least one cell in the ranges: met. (ii) the headline cell (D40): met, 32.0 to 39.7 Hz. (iii) every cell in the ranges: not met, but the plan does not require it. The 25 Hz is a continuation frequency of the periodic orbit; S3/S4 agree with it at ref_devalle (K8 36.27 Hz). Under (i) or (ii) trigger (a) is not met (no move to M4 on (a)); under (iii) it would be triggered, a reading the plan's wording ("no limit cycle ... within the ranges") does not support.
                 (b) "an eta_bar path enters the oscillatory region from a stable focus": YES for P1/P2 at ref_devalle. Start eta_bar = eta_H - 1.5 = 1.396: stable focus, Re lambda -0.510 /tau, Im lambda 1.656 /tau (26.35 Hz damped); the fixed point is unique for J < 0. Hopf crossing at eta_H = 2.896: Re lambda 0, Im 2.011 /tau (32.01 Hz), supercritical (A5, DL-126), stable cycle above. Peak eta_bar = max(4, eta_H + 2) = 4.896: unstable focus, Re lambda +0.334, Im 2.462 /tau (39.19 Hz linear), stable cycle 39.7 Hz (A6). State on each side: stable focus below, stable limit cycle around an unstable focus above. One Hopf point on every A6 eta-slice. Reading, UNVERIFIED: "stable focus" taken as a complex pair with Re < 0; node-versus-focus is not otherwise defined in the plan. The pass covers the ref_devalle path only; A6 gives the same single Hopf crossing on the other 31 slices, but their start values (eta_H - 1.5) were not evaluated.
                 (c) interneuron-drive assumption: plan default "not rejected" ([needs decision], Table 11.2). Nothing in A4 to A6 tests it: M3 is one inhibitory population, J < 0 is imposed, and eta_bar is varied as given, so the results hold conditional on the assumption and cannot reject it. The one related fact: oscillation needs J < 0 and tau_d > 0 (K9, no Hopf for J > 0 in 240 cases), so the M3 surge requires inhibitory feedback, not a particular sign of the eta_bar change. A test needs data on interneuron excitability (R3, single source, existence only), which is outside these results. G2 (c) stays at "not rejected" unless the owner rules otherwise; if rejected, G2 moves to M4 regardless of (a) and (b).
                 Summary: (a) met, (b) met, (c) not rejected by default; on these readings none of the three triggers, so M3 stays and M4 is robustness only. The decision is the owner's.
Reason:          instruction of the project owner; 6g of docs/ms6_plan.md; plan 4.3 G2, Table 11.2, 7.2 D40, Table 7.1 K9, K10.
Options:         -
Chosen:          as above   Default from: plan 4.3 G2 (c "not rejected", needs decision), DL-126 D-4, DL-131
Test:            fast suite 304 passed, 1 xfailed (302 + 2 new, test_g2_freq.py).
Status:          done (6g); D40 confirmed by owner; G2 metrics reported, decision pending with the owner.
Commit/tag:      the commit that adds this entry; no tag

## DL-133  MS6 6h: owner ruling, gate G2 judged on the DL-132 readings    [ID: G2, D40, K9, CP23, DL-132]
Date:            2026-10-17        Author:
Decision:        Owner ruling, recorded as given. Gate G2 is judged on the DL-132 readings: (a) met; (b) met for the P1/P2 path at ref_devalle (the headline path; the start states of the other 31 A6 slices were not evaluated); (c) not rejected (the plan's default, [needs decision] in Table 11.2; A4 to A6 cannot test it). So no G2 trigger fires: the project stays on M3, and M4 is robustness only, as the plan says. This rests on those readings, which are UNVERIFIED where the plan leaves room (DL-132: "Delta below critical" read as 0.1453 eta_bar and the search as existence or the headline cell; "stable focus" read as a complex pair with Re lambda < 0). If (c) were rejected, G2 would move to M4 regardless of (a) and (b). No D-item, plan text or earlier default changed. No tag, no push.
Reason:          instruction of the project owner; plan 4.3 G2, Table 11.2.
Options:         -
Chosen:          as above   Default from: plan 4.3 G2 (c "not rejected"), DL-132
Test:            no code change.
Status:          done
Commit/tag:      the commit that adds DL-134; no tag

## DL-134  MS6 6h: fresh-context review and gate report, MS6 gate passed with departures    [ID: K7, K10, G2, D40, CP23, DL-125 to DL-133]
Date:            2026-10-17        Author:
Decision:        (1) Fresh-context review by a subagent that had not seen the work (read docs/ms6_plan.md, DL-125 to DL-133, the MS6 gate wording, the K7/K8/K9/K10/G2/D40 rows, results/A5, A6, S3, S4, G2). Numbers: all others match, including the A5-vs-S4 check (max 1.84e-3 up, 6.8e-4 down at eta_bar 4.196; 39 judged points per direction; exclusion 2.796, 2.896, 2.996; ref_ceni 1.49e-4), K7 (R^2 0.99691, residual 2.42 vs 2 percent stated as a reported failure; post hoc fit labelled), K10 (not reproduced as worded), the frequency finding (32.01 Hz at eta_H, 36.07 Hz at eta_bar 4) and the G2/D40 statements. Nine text discrepancies, none changing a verdict: DL-129 network v trend shape (right: +13.2 up / +12.4 down at 3.296, zero near 5.7, about -2.4 at 6.496; re-checked against a5_check.json), DL-127 hysteresis 3e-4 (right: 1.2e-3), DL-127 "A5 0.1100 at eta_H" (unsupported), DL-128 network amplitude at eta_H "about 0.05" (right: 0.154/0.159) plus drift and FFT range wording, DL-129 tau_d^(H) label (4.120866 is A5, 4.120858 is A4), DL-132 "damped" for an unstable focus, two cosmetic. Committed entries not edited; docs/ms6_gate_report.md uses the correct values and lists them. (2) docs/ms6_gate_report.md written (structure of the MS5 report). (3) Verdict: MS6 gate passed with departures. Reason: A5 vs S4 within 2 percent (1.84e-3, points next to eta_H excluded) and the frequency map done; D40 confirmed, G2 does not trigger (DL-132, DL-133). Qualified by: K7 amplitude half fails the pre-registered residual rule (reported); K10 not reproduced as worded (non-blocking); G2 (b) checked for one path; UNVERIFIED readings and grids. No D-item, plan text or earlier default changed. No tag, no push; MS7 not started.
Reason:          instruction of the project owner; 6h of docs/ms6_plan.md; Table 11.1 MS6.
Options:         -
Chosen:          as above   Default from: docs/ms5_gate_report.md structure
Test:            fast suite 304 passed, 1 xfailed.
Status:          done (6h); MS6 gate passed with departures.
Commit/tag:      the commit that adds this entry; no tag

## DL-135  MS7 7a: sub-step plan docs/ms7_plan.md    [ID: D6, D7, D8, D12, D35, D43, CP17, CP18, CP20, CP25, DL-062, DL-073]
Date:            2026-10-17        Author:
Decision:        docs/ms7_plan.md written (structure of docs/ms6_plan.md). Planning only: no code, no run, no S5 or A8 run, no ruling taken, no D-item, plan text or earlier default changed, committed entries not edited. Contents: MS7 goal and gate as Table 11.1 states them; what is frozen at criteria-frozen and what waits for it; the inputs from MS1 to MS6 and where each lives; 28 items that must be decided before the freeze (F-1 to F-28: A_ref and classifier definitions, D43 floor levels, solver floor, RB3(a) range, A4 grid step, Heun dt ladder, every Table 7.2 row, cell lists and storage), each with the plan default, the test that could overturn it, what the plan leaves open and what is needed from the owner; the MS4 to MS6 UNVERIFIED readings and whether they reach the classifier; the DL-062 and DL-073 caveats with a proposed handling; sub-steps 7a to 7j; run-time expectations; machine state; open items.
Findings:        (1) A_ref as stored (results/A5/a5_cycles.npz, 5.51136) is a peak-to-peak (analysis/a5.py), while Table 2.1 compares 0.1 x A_ref with a Hilbert envelope, which for a sinusoid equals half the peak-to-peak: the threshold would sit at about 20 percent of the envelope-scale amplitude, not 10 percent. Owner ruling needed (F-1). (2) The baseline-only runs need the map 1 Delta spacing, which earlier notes parked for the MS8 plan (F-27). (3) The solver-floor value (A7) cannot be measured by a ramp run before the freeze; a constant-parameter hold run is proposed and needs a ruling (F-11). (4) RB6's 5 percent Heun-ladder test is not interpretable on a random floored run without common random numbers or enough seeds; the plan names neither (F-14). (5) A8 sensitivity needs surge records, and ramp runs are blocked; the plan does not say what it runs on at MS7 (F-4). (6) DL-062 declares damped too easily, DL-073 pulls the rate toward zero: opposite directions, both untested on M3 output. (7) The Table 2.1 clause "a rho ratio cannot reach 2 when baseline rho >= 0.5" does not stop the surge test, which is on P_G/P_non-G (F-7). (8) The "t_pred within one A4 grid step" tolerance assumes linear growth up to 0.1 x A_ref, which the K7 fit does not support beyond the Hopf neighbourhood; it cannot be tested before the freeze (F-12).
Owner decisions: before 7b: D-1 (A_ref definition) and D-2 (DL-062/DL-073 handling and acceptance rule); before 7c: D-3 (A8 data, open classifier definitions, broadband flag); before 7d: D-4 (cell lists, bundle storage); F-10 to F-26 and the housekeeping items before 7g or 7h.
Reason:          instruction of the project owner; plan Table 11.1 MS7, Table 2.1, 5.2 A8, Table 7.2, D35, D43, RB3.
Options:         -
Chosen:          as above   Default from: docs/ms6_plan.md structure
Test:            fast suite 304 passed, 1 xfailed (run before the commit).
Status:          done (7a); questions open; 7b not started.
Commit/tag:      the commit that adds this entry; no tag

## DL-136  MS7: owner rulings D-1 to D-4; 7b pre-registration of the estimator-study acceptance numbers    [ID: D7, D8, D35, D43, F-1, F-3, F-4, F-5, F-27, F-28, DL-062, DL-073, DL-126, DL-135]
Date:            2026-10-17        Author:
Decision:        Owner rulings, recorded as given. (D-1, F-1) A_ref is the envelope-scale amplitude of the A5 cycle at ref_devalle (eta_bar 4, 5 ms): the level of the detector's own band-passed Hilbert envelope on the A5 cycle, computed with the same band and filter as the detector, so that 0.1 x A_ref in Table 2.1 means 10 percent of the cycle on the detector's scale. The stored peak-to-peak 5.5114 (results/A5/a5_cycles.npz, DL-126) is kept as a recorded value only. The new value is computed in 7c and both are reported. (D-2, F-3) The DL-062/DL-073 handling is a synthetic-data-only study (no model runs), with the acceptance numbers below fixed before anything is run. A change to the D8 fit start or to the 2-SE rule needs an owner ruling: if the study points to one, stop and report, do not change it. (D-3, F-4, F-5) The A8 sensitivity may run before the freeze on synthetic signals, the baseline-only records and the stored S3/S4 mode-D records only (no ramp-study data exist). Classifier definitions the plan leaves open (onset convention, episode end, mode-N cycle threshold, broadband flag): follow Table 2.1 wording; where it is open, the simplest choice, marked UNVERIFIED and listed for owner sign-off at the draft criteria in 7h. (D-4, F-27, F-28) Cell lists use linear Delta spacing, log tau_d and linear J0 as working defaults (UNVERIFIED), per-cell bundle storage (10 seeds in one npz and one record). These cells become the MS9 map grid and are frozen with the tag; 7d lists them clearly in the plan. Timing rule for 7e: before the full run, time a small sample of real baseline-only cells under 10 concurrent copies, project the total, and stop for an owner ruling if the projection is over one hour.
Pre-registration (7b; every number below is ours or owner-chosen, UNVERIFIED, fixed before any study run): Synthetic seeded signals at 1 kHz, 4 s, band 25 to 100 Hz, threshold 0.1, 10 cycles, the same envelope_growth code as the pipeline, D8 call "damped" iff rate < -2 SE. Truth is the exponential rate of a 40 Hz ring (envelope A0 exp(rate t), A0 = 2 x threshold x exp(0.3 max(-rate, 0)) so that a full 10-cycle window exists), with additive Gaussian white noise (band-passing makes the envelope noise autocorrelated), onset at the record start or as a step at 1 s (filter transient), rates -25 to +12 per s, 200 draws per cell. Zero-growth cases: a constant-amplitude sinusoid in noise, and a stationary narrow-band AR(2) process (not a mode-D signal; it exercises threshold selection on a stationary envelope). Floor: |true rate| >= 2 per s (owner asked for a stated floor; basis: 10 cycles at 40 Hz is 0.25 s, so 2 per s is a 40 percent envelope change over the fit window). Acceptance: (i) in every cell with |true rate| >= 2 per s, the D8 call (damped or non-damped) matches the sign of the true rate in at least 95 percent of draws (the 95 percent is ours: the owner wrote "must match", a noisy estimator cannot give 100 percent); met iff all such cells pass. (ii) On the zero-growth signals the false-damped rate is at most 5 percent (owner default) in every zero-growth cell; the false-non-damped rate (a damped call missed, over the cells with true rate <= -2 per s) is reported. (iii) The inflation factor k is the 95.45th percentile of |fitted - true| / SE (the nominal coverage of 2 SE), per group and pooled; reported. Also reported: bias of fitted minus true rate, empirical coverage of the 2-SE rule, and the DL-073 xfail case. Any fix (SE method, fit start, signal) is out of scope and needs a ruling.
Reason:          instruction of the project owner; ms7_plan.md D-1 to D-4, 7b.
Options:         -
Chosen:          as above   Default from: owner rulings; ms7_plan.md
Test:            docs only; no run yet.
Status:          done (rulings recorded, pre-registration fixed before any run)
Commit/tag:      the commit that adds this entry; no tag

## DL-137  MS7 7b: estimator study for DL-062 and DL-073 on synthetic data; acceptance numbers not met; no change made    [ID: D8, DL-062, DL-073, DL-136]
Date:            2026-10-17        Author:
Decision:        Study run from a committed tree (b0c33af, git.dirty = false), 56 cells x 200 draws, 18.7 s, synthetic data only. Code: analysis/estimator_study.py, scripts/study_envelope_growth.py, configs/est_study.yaml (run kind est7b); outputs results/A8/est_study/ (git-ignored). Two generator settings were fixed in debugging before the real run and differ from, or complete, the DL-136 text: onset amplitude A0 = 5 x threshold x exp(0.3 max(-rate, 0)) (DL-136 said 2 x; at 2 x the envelope dipped below threshold at the record start and cut the window), and growth is capped after 0.5 s from onset (an uncapped exp(12 t) over 4 s overflows the filter). Both are ours, UNVERIFIED. Results against the pre-registered numbers: (i) NOT MET: 26 of the 36 cells with |true rate| >= 2 per s fall below 95 percent sign match. Record-start onset: damped rings (rates -25 to -2) match 100 percent except -25 (fit window cut short, 24 percent full windows), growing rings match 84 to 93 percent (rare fits of about -200 per s from a window of 0.1 cycles). Step onset (the DL-073 transient): damped rings at -25, -12, -6, -3 are called non-damped in 100 percent of draws (fitted rate +1 to +24 against the truth: the fit starts in the rise of the filter transient), -2 matches 57 percent; growing rings at +2 to +12 are called damped in 92 to 100 percent of draws (fitted rate about -20 to -190 per s). (ii) NOT MET: false-damped rate on zero-growth signals 29 percent and 24 percent (sinusoid in noise, record-start onset, noise 0.005 and 0.02), 62 and 67 percent (step onset), 61 percent (stationary AR(2)); the 5 percent limit is exceeded in all 5 cells. False non-damped (damped rings at -2 per s or steeper): 0 percent at record-start onset (except the -25 cell), 89 percent mean over step-onset cells, maximum 100 percent. (iii) Bias (fitted minus true), record-start damped rings: +0.3 to +0.4 per s (magnitude too small); step onset: +1.6 (at -2) to +48.6 (at -25) per s. Empirical coverage of the 2-SE rule: 0.34 to 0.48 for record-start damped rings (nominal 0.95), 0.00 for most step-onset cells, 0.19 for the AR(2) case. Inflation factor k (95.45th percentile of |error| / SE, maximum over cells of a group): record-start rings 619, step-onset rings 302, AR(2) 18.9; typical cells 6 to 8 (median-type SE inflation of 6 to 8 for well-behaved record-start rings), but the outliers (windows of a fraction of a cycle, SE tiny) make no single inflation factor give nominal coverage. DL-073 xfail case (40 Hz ring, 15 cycles above threshold, step at 1 s): fitted -3.36 +/- 0.35 against -6.14, as in DL-073, not within 10 percent. Reading, for the owner (nothing changed): the step-onset and short-window failures are driven by the fit starting inside the filter transient or on a window of a fraction of a cycle, so an SE rescaling alone cannot meet (i) or (ii); a different fit start (after the transient, or a minimum cycles for the window) and/or an autocorrelation-aware SE would be the candidates, and both change the D8 wording of Table 2.1 or the 2-SE rule, so they need an owner ruling. Caveats: the step onset is a harsh case (real S5 ramps are gradual, reasoned, not tested), the A0 and noise settings are ours, and the zero-growth cells are a synthetic proxy for mode N. The strict xfail test_slowly_damped_ring_rate_matches_true_decay_after_step_onset still fails as the current estimator stands (xfail holds); retiring it needs an owner ruling and was not done. Not done: the S2 re-check of the 13 ramps (it applies to a changed estimator; none was made). D8 fit start, 2-SE rule, plan text and all D-items unchanged.
Reason:          instruction of the project owner; DL-136 D-2, 7b.
Options:         -
Chosen:          as above   Default from: DL-136 pre-registration
Test:            fast suite 311 passed, 1 xfailed (304 + 7 new tests in tests/test_estimator_study.py).
Status:          done (7b); acceptance numbers not met; stopped for an owner ruling before 7c.
Commit/tag:      study code b0c33af; the commit that adds this entry; no tag

## DL-138  MS7 7c: A_ref "envelope-scale" level is not fully defined by D-1; candidate readings listed, none chosen    [ID: D7, F-1, DL-126, DL-136]
Date:            2026-10-17        Author:
Decision:        No A_ref value stored and no code written. D-1 (DL-136) fixes the scale (the detector's own band-passed Hilbert envelope, same band 25 to 100 Hz and filter, Butterworth order 4 zero-phase) but not (1) the statistic that turns the envelope into one "level", and (2) the source waveform: results/A5/a5_cycles.npz holds only vmax, vmin, period (A_ref = 5.51136 peak-to-peak, record A5_0000_506cf5745380.json, kept as recorded value only), not a waveform. The stored ref_devalle limit-cycle time series is results/S3/devalle/devalle_0000_9e49def91dfc.npz (eta_bar 4, tau_d 5 ms, 1 kHz, 10 s; S3 peak-to-peak 5.5118 agrees with A5 5.5114). Read-only look, code SHA 7e75fbc, all UNVERIFIED readings. On that record (t >= 7 s; t >= 9 s in brackets), envelope within the cycle runs 1.027 to 3.299, so the statistic matters: median 2.169 (2.155); mean 2.185 (2.184); maximum 3.299; minimum 1.027; sqrt(2) x RMS of the mean-removed v 2.406 (2.409); half peak-to-peak 2.756 (not the detector scale). Resulting 0.1 x A_ref threshold: 0.215 (median) to 0.330 (max), against 0.551 for the literal value. Options for the owner: (a) median of the envelope over whole cycles (F-1(c); my recommendation: robust to the filter edge, matches "level"); (b) mean; (c) maximum; (d) the A5 branch point re-simulated as an exact periodic orbit (needs a run, not done). Edge handling (drop the first and last 1 s of the record) also needs confirming. Table 2.1 wording used only; plan, D8 fit start, 2-SE rule, strict xfail unchanged.
Reason:          instruction of the project owner (stop if "envelope-scale" is ambiguous); 7c.
Options:         (a) median, (b) mean, (c) max, (d) re-simulated orbit
Chosen:          none; stopped for an owner ruling   Default from: none
Test:            docs only; no tests added, no run.
Status:          closed by DL-139 (owner ruled reading (a))
Commit/tag:      the commit that adds this entry; no tag

## DL-139  MS7 7c: A_ref fixed at 2.1762 (median band-passed envelope over whole cycles); closes DL-138    [ID: D7, F-1, DL-126, DL-136, DL-138]
Date:            2026-10-17        Author:
Decision:        Owner ruling on DL-138: reading (a). A_ref = median of the band-passed Hilbert envelope of v (25 to 100 Hz, zero-phase Butterworth order 4, the detector's own surge_metrics.envelope) over whole cycles of results/S3/devalle/devalle_0000_9e49def91dfc.npz (ref_devalle, eta_bar 4, tau_d 5 ms), first 1 s and last 1 s dropped. Option (d) not taken, no new simulation. Whole cycles, defined in analysis/a_ref.py: trimmed window [t_first + 1 s, t_last - 1 s] = [1 s, 9 s]; period P = stored A5 value 2.75791 tau = 27.579 ms (A5_0000_506cf5745380.json, devalle_ref); n = floor(8 s / P) = 290 cycles; window = samples with 1 s <= t < 1 s + n P (half-open, 1 kHz, window ends at 8.997 s). The envelope is computed on the whole untrimmed record and then cut. Stored value (results/A8/a_ref/a_ref.json, git-ignored, run record AREF_0000_3e2af5943a93.json, run kind aref7c, configs/a_ref.yaml, scripts/compute_a_ref.py, code SHA c386bf4, git.dirty = false): A_ref = 2.176222; threshold 0.1 x A_ref = 0.217622, one absolute number for every cell and path (D7). Source record sha256 and A5 json sha256 are stored in the file. Alternates stored beside it, each labelled "alternate, not used": mean 2.186789; maximum 3.219102; sqrt(2) x RMS of mean-removed v 2.404543; half peak-to-peak 2.755908; literal A5 peak-to-peak 5.511356 (the 5.5114, kept as a recorded value only, threshold from it would be 0.551). Against DL-138 (read-only look): median 2.176 against 2.155 to 2.169 (different window: 1 s to 9 s whole cycles instead of t >= 7 s or 9 s; 0.3 to 1 percent higher, the test tolerance is 2.15 to 2.18); mean 2.187 against 2.184 to 2.185; maximum 3.219 against 3.299 (the maximum is window-sensitive); sqrt(2) x RMS 2.405 against 2.406 to 2.409. Invariance: dropping 1, 2 or 5 extra whole cycles at each end changes the median by under 0.01 percent (2.17617 to 2.17627). All readings UNVERIFIED; the half-open window, the 1e-9 floor tolerance and the choice of the A5 period are ours. Plan, D8 fit start, 2-SE rule, strict xfail unchanged. No ramp, S3 or classifier run.
Reason:          instruction of the project owner; 7c.
Options:         (a) median, (b) mean, (c) max, (d) re-simulated orbit (DL-138)
Chosen:          (a)   Default from: owner ruling
Test:            tests/test_a_ref.py, 8 tests (value within 2.15 to 2.18; 290 cycles; alternates near DL-138 values; invariance to extra cycles within 0.2 percent; one threshold for all cells and paths; no literal 5.5114 in src/mprsurge; loader rejects other statistics); fast suite 319 passed, 6 deselected, 1 xfailed.
Status:          done (7c A_ref part). Open for the 7h sign-off: the reading choice (a) against the alternates as an A8 sensitivity item (no sensitivity run done here). The rest of 7c (classes, metrics, F-5 definitions) is not part of this step.
Commit/tag:      code c386bf4; the commit that adds this entry; no tag

## DL-140  MS7 7c: classes, metrics and the D8 interface; classifier definitions the plan leaves open listed, not ruled    [ID: D6, D7, D8, D9, F-5, F-6, F-7, CP17, CP18, CP26, DL-062, DL-073, DL-137, DL-139]
Date:            2026-10-17        Author:
Decision:        Rest of 7c built in analysis/surge_metrics.py (below the MS1 core), tests in tests/test_surge_classes.py (65 tests). Implemented as Table 2.1 words it: window rule D4 (window_for_ramp); mode N relative test P_G/P_non-G >= 2 x its baseline and absolute test P_G >= 2 x baseline P_G (G 25 to 100 Hz, total 1 to 150 Hz, factors 2 and 2 as arguments), baseline = last 5 s before t_on; at least 10 cycles; gaps shorter than one window merged; classes S+, S-rel, S-abs, S-sus, NS. Mode D: episode while the band-passed envelope >= the single threshold 0.1 x A_ref (passed in from analysis.a_ref, no other threshold, no cell or path argument); classes D-tr, D-sus, D-none. Also: the correspondence (classes_agree) and the surge-class set; A9 failure label (f) (D-none, the caller says the cell oscillates inside the A4 region, and the post-onset envelope never reaches the threshold); non-finite input gives class "failed", never NS or D-none; metrics: onset, end, duration (s, cycles), peak P_G, peak rho, f_pk, baseline rho (P_G/P_total, reported), onset_delay (eta at onset minus eta_H), j_exit_metrics (J_exit,run, J_exit,static, difference), collapse_time (r < 10 percent of baseline r). D8: one interface, D8Estimator (call(v, fs, band, threshold) returns D8Result with .damped); PlanD8Estimator is the plan wording exactly (fit from the threshold crossing over the first 10 cycles by envelope_growth, damped only if rate < -2 SE, nan is non-damped); fit start and 2-SE rule unchanged. The class functions read only .damped (a test checks that their source does not name envelope_growth or the 2-SE constant; stub estimators flip the class through the interface only). Every class output that went through a D8 call carries provisional = "provisional (D8 open, DL-137)"; classes reached without a D8 call (NS and D-none with no qualifying episode) do not. The strict xfail is unchanged. No A8 sensitivity run, no S2 re-run, no new simulation, no criteria file, no timing.
Open definitions:  each is left open by the plan and is not ruled here. The code uses the plain reading named, marked "working convention, UNVERIFIED, open for 7h sign-off (DL-140)"; only O1 is a switch (Conventions.onset). DL-136 D-3 asked for the simplest choice, marked UNVERIFIED, for onset, episode end, mode-N cycle threshold and broadband flag; the current instruction says not to choose, so I implemented only what a class needs to exist and left the rest out. O1 mode-N onset time: window centre of the first flagged window (used) or its start (switch); the mode-D onset is the envelope crossing, which Table 2.1 defines; recommend centre. O2 episode end, duration and gap merging: gap = unflagged windows x step, merged if < W; end = last flagged centre + step/2; duration = flagged windows x step; alternative: gap measured from window span to window span; recommend as used. O3 termination: an episode is sustained if no gap of W or more follows it before the record ends (mode N: trailing unflagged windows x step; mode D: trailing samples); alternative: any unflagged final window terminates; recommend as used (consistent with the merge rule). O4 amplitude threshold in mode N: the D8 fit uses the single 0.1 x A_ref (owner constraint) and the 10-cycle count in mode N uses no amplitude threshold; open whether a mode-N noise envelope at sigma 0.0624 crosses 0.2176 in the baseline (not measured; 7f will show it); the alternative, a baseline-relative envelope level, is a new threshold and needs a ruling. O5 cycle count: mode N = duration x mean f_pk over the episode windows; mode D = unwrapped analytic phase / 2 pi (the count_cycles measure); alternatives: phase-based in mode N, or the integral of f_pk; recommend as used. O6 peak frequency: argmax of the PSD in G, resolution 1/W, no interpolation; alternative: parabolic interpolation; recommend as used (the A8 check is within 1/W). O7 baseline value: mean over the windows wholly inside [t_on - 5, t_on] of P_G/P_non-G and of P_G (mean of window ratios), baseline rho the mean of window rho; alternatives: median, ratio of means; recommend mean. O8 tested windows: windows with centre >= t_on; alternative: window start >= t_on (no baseline overlap, onset later by W/2); recommend start >= t_on if baseline contamination matters more than onset timing; your call. O9 D8 scope: the call is made once per record on v from t_on (the plan says "the run counts as damped"), and a damped run has no episode (NS or D-none); the reading that damped means not an episode comes from the Table 2.1 minimum-duration row and CP17, not from a class sentence; alternative: per episode on the episode segment. O10 which episode: mode D: the first qualifying episode defines the class; mode N: the first qualifying episode per test, S-sus if any qualifying episode is unterminated, S+ if both tests qualify (no overlap in time required); alternatives: overlap required for S+, longest episode; recommend requiring overlap for S+. O11 S-abs "broadband" flag (F-6): NOT implemented (the plan gives no operational test); options: spectrogram argmax of the rise outside G (a location test, no new number), spectral flatness, none. O12 post-surge rate: NOT implemented (the statistic after J_exit,run is not defined); options: mean r over [J_exit,run, end], r over the last second. O13 baseline r for the collapse marker: mean of r over the baseline; marker = first sample with r < 10 percent of it, no smoothing, no minimum duration. O14 sign of the exit delay: J_exit,run minus J_exit,static. O15 label (f): A4-region membership is an argument supplied by the caller (A4), not computed here. O16 edge handling: none in the classifier; the caller discards transients (existing edge note).
Findings:        all on the plan-literal D8 estimator; nothing changed. (1) The Hilbert transform is periodic, so a record that is quiet at its start and nonzero at its end gets a spurious envelope at its start; the D8 fit then runs on 4 samples (synthetic ramp-up to a sustained 40 Hz burst: rate -280 +/- 52 per s, called damped), so a sustained episode can be read as damped and the class becomes D-none or NS. With the end padded with zeros the same signal fits +4.5 +/- 0.04 per s. (2) On real model output (stored S3 limit cycle at ref_devalle, 10 s, 1 kHz) the plan estimator gives non-damped for t_on = 0 s (rate -0.23 +/- 0.29) and t_on = 3 s (+0.16 +/- 0.28) and damped for t_on = 1 s (-0.54 +/- 0.24, 2.2 SE): a steady limit cycle called damped, the DL-062 understatement of SE on real output. The tests use t_on = 0 and 3 s and stub estimators elsewhere; the t_on = 1 s case is not asserted. (3) On the stored S3 fixed-point record with its start transient, the Hilbert wrap puts the envelope above 0.2176 at the end of the record (0.78), so label (f) would read "reached the threshold"; the test uses the settled part (2 to 8 s). (4) With W = 0.2 s (T_ramp <= 6 s) one seeded white-noise record gave S-rel from three flagged windows at 70 Hz (10.5 cycles by f_pk x duration): the 10-cycle rule is weak at short W. One record; the rate belongs to the 7f baseline false-positive report. These add to the D8 reasons in DL-137; they are inputs for the D8 ruling, not changes.
Reason:          instruction of the project owner; ms7_plan.md 7c.
Options:         O1 to O16 as listed
Chosen:          none of O1 to O16 ruled; the plain reading is implemented where a class needs it   Default from: Table 2.1 wording only
Test:            tests/test_surge_classes.py, 65 tests (each class reachable in both modes; factor edges 1.5, 2, 4; A_min edges 0.05, 0.1, 0.2; minimum cycles; gap merging; label (f) cases; failed input; correspondence table; D8 swap and plan-rule tests; A8 on/off within one step and f_pk within 1/W; metrics; stored S3 records). Fast suite 384 passed, 6 deselected, 1 xfailed.
Status:          done (7c classes and metrics; D8 provisional). Open for the 7h sign-off: O1 to O16 and the D8 findings. Strict xfail stays; the D8 ruling is still needed.
Commit/tag:      the commit that adds this entry; no tag

## DL-141  MS7 7d: S5 baseline-only cell lists, run kind s5base, driver, headline cell run    [ID: D6, D12, CP14, CP20, F-27, F-28, DL-069, DL-120, DL-121, DL-123, DL-136]
Date:            2026-10-17        Author:
Decision:        Built as docs/ms7_plan.md orders 7d and as DL-136 D-4 ruled (Delta linear, tau_d log, J0 linear, per-cell bundle, 10 seeds in one npz and one record). Code commit 87af6c1 (run from this commit, git.dirty = false). Files: src/mprsurge/analysis/cells.py (cell lists, start state and stability record), configs/S5_cells.yaml (grids), configs/S5_baseline.yaml (run config, headline values), run kind s5base (config.RUN_KINDS, run.TASKS, simulate_mf.run_s5_baseline; config.hash_view adds seeds.n_seeds for this kind only, so other hashes are unchanged), scripts/run_S5_baseline.py (--dry-run, --cells headline|all|indices, --workers), tests/test_cells.py. Cells (1,226): headline; map 1 = Delta 0.01 to 0.6 (30, linear, ends included) x tau_d 1 to 50 ms (30, log), J0 -21, T_ramp 120 s; map 2 = J0 -40 to -5 (25, linear) x T_ramp 1 to 1000 s (13, log, 10^(k/4), the S2 list), Delta 0.3, tau_d 5 ms. All grid values are UNVERIFIED working defaults (DL-136); they become the MS9 map grid and are frozen with the criteria. Start state (D12, CP20): eta_start = eta_H - 1.5 with eta_H the lowest Hopf crossing along eta_bar at the cell's (J0, Delta, tau_d) on the A4 grid (801 points, spacing 0.025, the working A4 step, analysis.hopf.lowest_eta_hopf); a cell with no crossing uses the headline eta_H (A4 value 2.8960461989737856 from configs/path_A4.yaml), so eta_start 1.396046. Run (one task per cell): constant parameters, no kick, no ramp; 2 s discard before t = 0 (not returned), then 5 s kept on the 1 ms grid including t = 0 and t = 5 s (5001 samples; the ramp-run grid up to t_on); stochastic Heun dt 1e-3 tau, sigma 0.0624 (UNVERIFIED until S8), 7e5 steps per seed; v and r both stored (10 x 5001 each) plus t_ms and y_start. Seeds: spawn_key [7, 4, s], s = 0 to 9, so the stream for seed s does not depend on the cell (as DL-069) and does not use the sigma-calibration keys [0] to [9] (DL-123 finding 3). Readings that are ours, UNVERIFIED: the t = 5 s endpoint is kept; the start is the one fixed point of the cell even if it were unstable (recorded in flags, not refused; none is); the driver builds one job per cell through the runner (execute_job, run_jobs) instead of sweep expansion because eta_H differs per cell; the cell-list file is read from configs/S5_cells.yaml, a file the 7d row of the plan did not name.
Results:         Dry run of the full list (scripts/run_S5_baseline.py --dry-run --cells all, 104 s, Hopf scans only, nothing integrated): 1 + 900 + 325 = 1,226 cells; cell-list SHA-256 8e67bbd2b366e86ffee59e732dd79824bdce82c73c477436cb3b1689b0a328d9 (changes with any grid or start-state change; configs/S5_cells.yaml SHA-256 fe8590ce...790). Hopf crossing found in 852 of 900 map-1 cells; 48 map-1 cells have none (Delta 0.336 to 0.6 and tau_d 25.5 to 50 ms) and inherit the headline eta_start 1.396046; all 325 map-2 cells have a crossing (eta_H 2.129 to 4.031; 25 distinct start states, T_ramp enters only through W). Start-state stability: all 1,226 start states are stable (largest Re lambda -0.0133); stable focus in 1,170, stable node in 56 (all map 1, tau_d 7.6 to 50 ms, Delta 0.01 to 0.6; 54 of them with a Hopf crossing, 2 without). So 56 map-1 baselines are non-oscillatory fixed points under noise (a node has no resonance); this is information for the 7f baseline rho report, no flag or class added. Map-1 eta_start runs from -1.251 to 7.937. Headline cell run (scripts/run_S5_baseline.py --cells headline, record S5base_0000_1fe2ceaa1659.json, git commit 87af6c1, git.dirty = false): 10 seeds, 5001 samples, task wall 0.20 s (script wall 96.6 s, almost all the cell-list build; plan estimate about 0.3 s alone, arithmetic UNVERIFIED); start (r, v) = (0.08029, -0.59468), stable focus, Re lambda max -0.5098; v mean per seed -0.5940 to -0.5961 against the fixed point -0.5947, v std per seed 0.0376 to 0.0417. Nothing else was run: no 7e timing sample, no full run, no A8, no S2, no criteria file. Map-2 records at one J0 should be bit-identical for the 13 T_ramp (same state, same seeds; tested on the toy for T_ramp 10 against 120); 7e can confirm and may not need to be told apart.
Reason:          instruction of the project owner; ms7_plan.md 7d; DL-136 D-4.
Options:         -
Chosen:          as above   Default from: DL-136 D-4, plan D12/CP20
Test:            tests/test_cells.py, 13 fast tests + 1 slow (full list 900 + 325 + headline): axes and counts, headline start 1.396046, no-Hopf inheritance, map-2 shared start states, cell-list hash and run hash change with the grid and the seed count, toy run writes a bundle and a record (spawn keys [7,4,s], stable focus), determinism, stream independent of T_ramp, calibration keys not reused, stationarity. Fast suite 397 passed, 7 deselected, 1 xfailed (384 + 13). D8, the 2-SE rule, the estimator, the strict xfail, O1 to O16 untouched.
Status:          done (7d). Open for you: item 10 in docs/ms7_plan.md. 7e not started.
Commit/tag:      code 87af6c1; the commit that adds this entry; no tag

## DL-142  MS7 7e: timing sample of real baseline-only cells under 10 concurrent jobs; projection; go for the full run    [ID: D12, CP20, F-27, F-28, DL-105, DL-136, DL-141]
Date:            2026-10-17        Author:
Decision:        Timing sample before the full run, as the DL-136 rule orders. Code commit e2c9e18 (adds only scripts/run_S5_baseline.py --out-dir and scripts/check_S5_baseline.py; no model, config or cell change), git.dirty = false. Sample: 10 real cells, 10 workers, one job each, all running at once, written to results/S5/baseline_timing (git-ignored, not the production directory): headline (0); map 1 stable focus (1, 450); map 1 stable node start (16); map 1 last cell, no Hopf crossing, headline start (899); map 2 at J0 -40 with T_ramp 1 s and 1000 s (901, 913, the duplicate pair); map 2 (1000, 1100, 1225). Same computation per cell (7e5 Heun steps x 10 seeds), so cells differ only in start state.
Results:         Wall time per job under 10 concurrent: 0.578 to 0.610 s (median 0.594 s), all ten ok (task time, includes the npz and record write; the cell-list build, 95.9 s per driver call, is outside it). Script wall 98.3 s = 95.9 s list build + 2.4 s for the 10 jobs including pool start. Peak memory: whole process tree 1.48 GB working set (12 python processes seen: 10 workers, parent, pool helper), largest single process 169 MB peak working set (polled every 0.3 s from PowerShell, so a lower bound on a sub-0.3 s peak: UNVERIFIED). Disk per cell: npz 737,370 B + record about 6 KB + params md; the 21 files of the sample total 8.25 MB for 10 cells, so 0.83 MB per cell. Bit-identity: cells 901 and 913 (same J0, T_ramp 1 s and 1000 s) have identical v, r, y_start and t_ms. Projection for 1,226 cells: jobs 1,226 / 10 x 0.594 s = 73 s plus list build 96 s plus start-up: about 3 to 4 minutes; memory about 1.5 GB (limit about 12 GB); disk about 1.0 GB (149 GB free). All three are inside the limits (one hour, 12 GB, disk), so the full run goes ahead. Not in the projection: antivirus scanning of 3,700 files and a Defender exclusion is unknown (open item 3); the sample is one wave of 10 cells, so the steady-state rate with 123 waves is UNVERIFIED. The 5,001-sample baseline cells give 0.594 s for 7e6 steps per job, i.e. 8.5e-8 s per step per job at 10-way load, against 1.51e-7 in the plan row (DL-104): the plan row is more pessimistic by 1.8, which is arithmetic from our own numbers, UNVERIFIED.
Reason:          instruction of the project owner (7e ruling 1); DL-136 timing rule.
Options:         -
Chosen:          full run (ruling 2); resumable, failed labelled "failed", no retry with changed settings; verification afterwards with scripts/check_S5_baseline.py (count 12,260 = 1,226 x 10, clean tree, spawn keys [7, 4, s], start states against the 7d list, the 13 T_ramp duplicates per map-2 J0 bit-identical, stationarity reported). Duplicates kept, so the plan count is 12,260. Default from: DL-136, DL-141 item 10 (duplicates run by owner ruling).
Test:            the timing run itself; fast suite 397 passed, 7 deselected, 1 xfailed with the 7e driver change (no test added; the driver option is a path override).
Status:          timing done; full run next (DL-143 will hold the totals).
Commit/tag:      the commit that adds this entry; no tag

## DL-143  MS7 7e: full baseline-only S5 run, 1,226 cells x 10 seeds, kind s5base    [ID: D12, CP20, F-27, F-28, DL-136, DL-141, DL-142]
Date:            2026-10-17        Author:
Decision:        Full run as DL-142 and the owner ruling ordered it: scripts/run_S5_baseline.py --cells all --workers 10, from a clean tree (code commit e2c9e18 plus the docs commit 5963885, git.dirty = false), output results/S5/baseline/ (git-ignored). Resumable (a complete record is skipped; a cell that raises is recorded "failed"; no retry was needed). Nothing else run: no 7f report (baseline rho, O4 noise envelope and the white-noise false-positive check are 7f, not in the 7e row of the plan), no A8 sensitivity, no S2 re-run, no criteria file, no tag.
Results:         1,226 records, all status ok, 0 failed, 0 timeout (manifest.csv: 1,226 ok rows, 1 skipped = the headline record from the 7d run, commit 87af6c1, dirty = false, kept because its hash is identical). Runs: 1,226 x 10 = 12,260 = the plan count. Wall: 147.8 s script (cell-list build 104.5 s, jobs and writing about 43 s; antivirus unknown, open item 3); per job 0.58 s. Peak memory 1.56 GB whole tree, 188 MB largest process (polled, UNVERIFIED). Disk 892 MB (npz 737 kB per cell). Against the DL-142 projection (3 to 4 min, 1.5 GB, 1.0 GB): inside it. Verification (scripts/check_S5_baseline.py, exit 0, 0 problems): records 1,226, all clean tree (dirty 0), spawn keys [7, 4, s] for s = 0..9 in every record, n_seeds 10, cell-list SHA-256 8e67bbd2... equals DL-141, cell-spec hash in every record equals configs/S5_cells.yaml (fe8590ce...), start state (r, v) of every bundle equals the 7d list (rtol 1e-9). Duplicates: 25 map-2 J0 groups of 13 T_ramp each; v, r and y_start bit-identical in all 25 groups (0 mismatches), as the toy test predicted. Per-cell sanity, reported not judged: the first-half mean of v against the second-half mean, in units of the seed's std, has median 0.084 and maximum 0.285 over cells (cell 32); the mean of v against the start fixed point, same units, median 0.038, maximum 0.077 (cell 33). Both are small, so the 2 s discard leaves a stationary baseline by this crude measure (UNVERIFIED: no autocorrelation-aware test; the plan row names none). The 56 stable-node baselines are in the set and are not separated here (7f). Anything D8-dependent: not used in 7e.
Reason:          instruction of the project owner; ms7_plan.md 7e; DL-136 timing rule.
Options:         -
Chosen:          as above   Default from: DL-136 D-4, DL-141 item 10 (duplicates run by owner ruling)
Test:            scripts/check_S5_baseline.py on the production directory (no new pytest test; the script is a check on outputs). Fast suite unchanged at 397 passed, 7 deselected, 1 xfailed.
Status:          done (7e). 7f not started. D8 open (DL-137, DL-140); O1 to O16 for the 7h sign-off, not ruled.
Commit/tag:      the commit that adds this entry; no tag

## DL-144  MS7 7f: baseline rho report and O4 noise-envelope measurement on the 7e records; what is computed, fixed before the run; false-positive report held for a ruling    [ID: D2, D3, D4, D5, D7, F-7, O4, CP14, CP18, DL-137, DL-139, DL-140, DL-143]
Date:            2026-10-17        Author:
Decision:        Fixed before the analysis runs (D-2 rule). Code commit = the commit that adds this entry (analysis/baseline_report.py, scripts/run_A8.py, configs/A8.yaml, run kind a8base in config.RUN_KINDS, tests/test_baseline_report.py, 5 tests); the analysis runs after it from a clean tree. Reads the 7e records only (not altered); no simulation. (1) Baseline rho: for each of the 12,260 records, rho = mean over the windows wholly inside the record of P_G / P_total (G 25 to 100 Hz, total 1 to 150 Hz, Hann, linear detrend), with W and step from the cell's own T_ramp by D4 (W = 2 s for T_ramp >= 60 s, else max(0.2 s, T_ramp / 30)); the record is read as the 5 s baseline (t_on = record end). Mean P_G and P_non-G over the same windows are stored beside it. Reported: quantiles; number and fraction of records, and of cells (cell value = mean over its 10 seeds; also "any seed"), with rho >= 0.5 (F-7: reported, no flag, no class); for all records, and split as a reporting split only into stable focus (1,170 cells) and stable node (56 cells, map-1, tau_d >= 7.6 ms), and by headline, map 1, map 2, and by W. (2) O4: the band-passed (25 to 100 Hz) Hilbert envelope of each record (surge_metrics.envelope) against the single threshold 0.1 x A_ref = 0.217622 (A_ref 2.1762, DL-139) at sigma 0.0624 (UNVERIFIED until S8): per record the maximum, 99th percentile and median of the envelope, the fraction of samples at or above, whether any sample is, and the cycles (unwrapped phase / 2 pi) of the longest run at or above. Two variants: whole record, and with the first and last 1 s dropped after filtering (the A_ref convention) because of the filter and Hilbert edge note; the second is ours, UNVERIFIED. The D8 call is not used. Pass/fail numbers: none. The plan gives no acceptance number for either measurement, so none is invented; both are measurements, listed for the 7h sign-off. Defender exclusion status (open item 3) is unknown to this session; no timing figure from 7e or 7f assumes it.
Held, not run: the white-noise / baseline false-positive report (item 3, incl. DL-140 finding 4). Reason: neither docs/ms7_plan.md nor the Technical Plan define how a baseline-only record is classified. Table 2.1 takes the baseline as the last 5 s before t_on and tests windows from t_on, but a 7e record is 5 s, so it has no post-t_on span. Options, none chosen: (A) pair records of one cell: baseline = seed a, test = seed b (10 s signal, t_on = 5 s, 10 ordered pairs per cell, 12,260 classifications); follows the Table 2.1 wording, independent noise, but the join at 5 s is a discontinuity that adds broadband power to the first test window (inflates false positives; its size can be measured); (B) split each record (baseline = first part, test = rest): not Table 2.1 wording, baseline shorter than 5 s, with W = 2 s fewer than 2 windows; (C) self-referenced: test every window of a record against that record's own baseline mean: circular (a window above 2 x the mean of a set that contains it), measures the spread of window power, not the classifier; (D) synthetic white noise at the classifier's real window sizes (seeded, many draws, W = 0.2 s and 2 s, with the same pairing), which isolates the 10-cycle rule at short W (DL-140 finding 4) and does not use the 7e data. Which D8 estimator call to include: every class number that uses the call is "provisional (D8 open, DL-137)". Recommendation: (A) for the 7e data, plus (D) for the short-W question, rates per class with counts and denominators, no pass/fail number until you give one.
Reason:          instruction of the project owner; ms7_plan.md 7f row (baseline rho), DL-140 O4 and finding 4.
Options:         as listed for the held item
Chosen:          items 1 and 2 as above; item 3 held   Default from: Table 2.1 wording for rho; no plan default for item 3
Test:            tests/test_baseline_report.py (white noise gives the flat-spectrum rho 0.50, a resonance gives rho > 0.9, window sizes by D4, envelope threshold and cycle counting on a synthetic burst, run kind registered).
Status:          in progress (7f items 1 and 2); item 3 waits for the ruling.
Commit/tag:      the commit that adds this entry; no tag

## DL-145  MS7 7f: baseline rho report and O4 noise-envelope result on the 7e records (D8 not used)    [ID: D2, D5, D7, F-7, O4, DL-139, DL-140, DL-143, DL-144]
Date:            2026-10-17        Author:
Decision:        Ran scripts/run_A8.py as fixed in DL-144 (code commit = the one adding DL-144; git.dirty = false; 53 s; outputs results/A8/baseline/a8_baseline_rho.csv, a8_noise_envelope.csv, a8_baseline_summary.json and a run record, git-ignored). The 7e records were read, not changed. No pass/fail number applied; nothing here is a class. No sensitivity run, no S2 re-run, no new simulation, no criteria file, no tag. Defender exclusion status: unknown to this session (as DL-144).
Results:         Baseline rho (P_G / P_total, mean over windows, cell's own D4 window; UNVERIFIED readings O7 and "record = 5 s baseline"). All 12,260 records: median 0.640, quartiles 0.466 / 0.819, 5th to 95th percentile 0.353 to 0.957, range 0.109 to 0.994. Records with rho >= 0.5: 8,272 of 12,260 (67.5 percent). Cells whose 10-seed mean is >= 0.5: 809 of 1,226 (66.0 percent); cells with at least one seed >= 0.5: 1,015. Headline: rho median 0.680 (0.646 to 0.731), 10 of 10 seeds >= 0.5. By kind: map 1 (900 cells) median 0.550, 5,212 of 9,000 records >= 0.5, 500 cells by mean; map 2 (325 cells) median 0.715, 3,050 of 3,250 >= 0.5, 308 cells by mean (the 13 T_ramp of a J0 share the state and seeds, so these 325 cells are 25 distinct baselines with different windows). Reporting split by start type (no class, flag or criterion added): stable focus, 1,170 cells, 11,700 records: median 0.660, 8,202 records >= 0.5 (70.1 percent), 809 cells by mean; stable node, 56 cells, 560 records (map 1, tau_d >= 7.6 ms): median 0.454, range 0.354 to 0.543, 70 of 560 records >= 0.5 (12.5 percent), 0 cells by mean, 36 of 56 cells with at least one seed >= 0.5. So the nodes sit just under the flat-spectrum value 0.50 (Table 2.1 "about 0.50"), the foci mostly above it. By window (W): W = 0.2 s (T_ramp 1 to 5.6 s) median 0.754, 1000 of 1000 >= 0.5; W 0.33 to 1.87 s medians 0.67 to 0.71, 83 to 96 percent >= 0.5; W = 2 s median 0.588, 6,352 of 10,260 >= 0.5. rho therefore depends on W for the same state (the 13 T_ramp of one J0 differ only by W), so "baseline rho" is a function of the D4 window as well as of the cell: UNVERIFIED reading, for the 7h sign-off. Per F-7 the fraction is reported and nothing is flagged: 33 percent of cells are below 0.5 and about two thirds are at or above it, where Table 2.1 says a rho ratio cannot reach 2.
                 O4 noise envelope (band 25 to 100 Hz, threshold 0.217622 = 0.1 x A_ref, sigma 0.0624 UNVERIFIED until S8). Median over records of the envelope median 0.10 to 0.11 (headline 0.11) and of the 99th percentile 0.087; the envelope maximum has median 0.107 and 95th percentile 0.218. Whole record: 460 of 12,260 records (3.8 percent), in 125 of 1,226 cells, have at least one sample at or above 0.217622 (fraction of all samples 0.26 percent); trimmed 1 s each end: 381 records (3.1 percent). All of them are in map 1 at Delta 0.13 to 0.60 (none below Delta 0.10); none in the headline (envelope maximum 0.133 at most), none in map 2 (maximum 0.167), none of the 56 stable-node cells (maximum 0.09). Runs of at least 10 cycles at or above the threshold (the D8 / 10-cycle scale): 31 records (28 trimmed), in 8 cells, all with Delta 0.32 to 0.58 and tau_d 25 to 50 ms, longest 25.8 cycles (22.9 trimmed). So O4: at the headline and in map 2 the noise envelope does not reach the threshold; in map 1 it does in 125 cells, and for 8 cells (large Delta, large tau_d, the lightly damped foci) the noise alone makes a run of 10 or more cycles above 0.217622. Whether that matters for the mode-N classifier depends on O4's ruling (mode N uses no amplitude threshold in the code; only the D8 fit does): not ruled. No acceptance number was given; none applied.
Reason:          instruction of the project owner; ms7_plan.md 7f row (baseline rho); DL-140 O4.
Options:         -
Chosen:          as above   Default from: Table 2.1 wording; no plan number
Test:            tests/test_baseline_report.py (5 tests); fast suite 402 passed, 7 deselected, 1 xfailed (397 + 5).
Status:          7f items 1 and 2 done. Item 3 (false-positive report) held, options in DL-144. Rest of the 7f row not done: sensitivity (D-3 runs are separate, not asked), a8_aref.json (A_ref already stored by 7c, results/A8/a_ref/a_ref.json, DL-139). D8 open (DL-137); O1 to O16 for 7h, not ruled.
Commit/tag:      the commit that adds this entry; no tag

## DL-146  MS7 7f (rest): A8 sensitivity, a8_aref.json, reachability share, white-noise report; design fixed before the run    [ID: D2, D6, D7, D8, F-4, F-7, O4, CP18, DL-136, DL-139, DL-140, DL-144, DL-145]
Date:            2026-10-17        Author:
Decision:        Fixed before the run (D-2). Label: the step instruction calls this "7g"; docs/ms7_plan.md defines 7g as D43 / RB3(a) / Heun ladder / A4 grid (not started). The work done here is the part of the 7f row that DL-145 left open (sensitivity, a8_aref.json), plus the white-noise item (option D of DL-144) and the reachability share. 7g as the plan defines it is untouched. Code = the commit that adds this entry (analysis/a8_sensitivity.py, scripts/run_A8_sensitivity.py, configs/A8_sensitivity.yaml, run kind a8sens, tests/test_a8_sensitivity.py); the run follows from a clean tree. Data allowed (ruling 1, DL-136 D-3): seeded synthetic signals, the 7e baseline-only records, stored S3/S4 mode-D records, seeded white noise. No M3 ramp run, no S2 re-run, no new S5 or other simulation. The 7e records and 7f outputs are read only. Network S3/S4 records are not used (not mode D mean field).
  Variants (plan A8 and RB10, 7f row): V0 default; band 30 to 120 (G band; total band 1 to 150 unchanged); factors 1.5 and 4 (relative and absolute test together; mode D has none); A_min factor 0.05 and 0.2 (threshold = factor x A_ref 2.176222; it enters mode N only through the D8 fit); window x 0.5 and x 2 (W' = factor x the D4 window, step = W'/2; in mode D W' sets only the gap merge and f_pk); minimum cycles 5 and 20. A_ref stays the 25 to 100 Hz value under the band variant. D8 = the plan estimator unchanged; every class that called it is "provisional (D8 open, DL-137)"; d8_called, damped, rate and SE are written per row so D8-caused changes can be told apart.
  (i) Synthetic set, seeded (SeedSequence entropy 20261008, spawn key [7, 6, ...]), fs 1 kHz. Mode N: 40 s, t_on 10 s, white noise sd 0.02, event 12 to 20 s; 40 Hz bursts at target P_G ratios 1.3, 1.8, 2.5, 3.5, 6 (amplitude sqrt(2 (ratio-1) 0.15 sigma^2), white-noise arithmetic ours, UNVERIFIED), a sustained burst, a 20 to 60 Hz chirp, rings with rate -25 and -3 per s, a trend, bursts at 27 and 110 Hz (the band-edge cases), a noise-only case; each at T_ramp 120 s (W 2 s) and 3 s (W 0.2 s). Mode D: 14 s, t_on 1 s, noise 1e-4, T_ramp 120 s: 40 Hz bursts of amplitude 0.07, 0.15, 0.3, 0.6, 1.5 (envelope against 0.109, 0.218, 0.435), sustained, chirp, rings (-25 and -3 per s, amplitude 3), trend, 27 and 110 Hz bursts, noise only. Amplitudes are ours, UNVERIFIED.
  (iii) Stored mode-D records: S3 mean field (devalle 2 records, ceni 3 records): v from 2 to 8 s, t_on 1 s, T_ramp 120; S4 mean field (devalle 122 and ceni 22 constant-parameter holds): v of each hold, t_on = hold start, T_ramp 120 (window x 2 does not fit the 2 s devalle holds: recorded "not_run"). One A_ref and one threshold for all of them (D7). Conventions ours, UNVERIFIED.
  (ii) 7e baseline-only records: class-free measurements only (the DL-140 finding 3 / DL-144 false-positive question on these records is withdrawn, options A to C dropped): baseline rho under the band and window variants; the O4 noise envelope (any sample, longest run in cycles, whole record and trimmed 1 s) under A_min 0.05, 0.1, 0.2 and the band variant.
  Reachability share (ruling 4), from the stored 7f baseline rho (results/A8/baseline/a8_baseline_rho.csv, not recomputed), per W: records, cells (10-seed mean) and cells (any seed) at or above the levels 0.25, 0.333, 0.5, 0.667, 0.75. Reading, UNVERIFIED arithmetic: a rho ratio cannot exceed 1/rho0, so it cannot reach f when rho0 >= 1/f: 0.5 at f = 2 is the plan's wording (Table 2.1); 0.667 at 1.5 and 0.25 at 4 are our arithmetic. The step instruction gave "1 - 1/ratio" with 0.5, 0.667, 0.75 for 2, 1.5, 4; those three numbers do not follow one formula (1 - 1/f is 0.333 at 1.5; 1/f is 0.25 at 4). All five levels are tabulated, none is chosen. The surge test itself is on the odds P_G/P_non-G (CP18), which has no upper bound, so a level reached means the plan's sentence applies to the reported rho ratio only (F-7).
  Option D (white noise): per distinct D4 window of the 13 map-2 T_ramp (W 0.2, 0.333, 0.593, 1.054, 1.874, 2.0 s), 500 seeded white-noise records of 25 s (sd 0.04, the headline baseline v std, DL-141; 5 s baseline + 20 s test span in one continuous record, t_on 5 s; spawn key [7, 6, 2, k], the same draws for every variant and T_ramp), mode N, plan D8; counts per class with denominators 500, for V0 and each variant. At sd 0.04 the band envelope sits far below 0.2176, so the D8 fit has no crossing and returns non-damped: the rates are those of the class logic without a D8 filter, and white noise has no resonance (real baselines have rho 0.45 to 0.99). No pass/fail number.
  A_ref reading as a sensitivity item (ruling 5): not in the plan A8 list (band, factors, A_min factor, window; RB10 adds cycles) and not in DL-136 D-3, so not run; A_ref chosen (a), alternates stored in results/A8/a_ref/a_ref.json; a8_aref.json restates the stored file (three F-1 numbers, chosen one) and recomputes nothing. Listed for 7h.
  Acceptance numbers: the plan gives none for this data. RB10 (headline unchanged, at most 10 percent of map cells change class) and RB9(c)/D2 (5 percent) are map-cell tests on ramp-run classes for A11 after the freeze; they cannot be evaluated here and are not applied. Everything is reported, none judged; listed for the 7h sign-off.
Reason:          instruction of the project owner (rulings 1 to 6); ms7_plan.md 7f row; plan A8, RB10.
Options:         -
Chosen:          as above   Default from: plan A8 and RB10 variant list; ours where marked
Test:            tests/test_a8_sensitivity.py (variants, seeded synthetic set, amplitude ladder against A_min, not_run, factor 4, reachability counts, rho window multiplier, white-noise determinism, run kind).
Status:          design fixed, run next (results in the following entry). D8 open (DL-137); O1 to O16 for 7h, not ruled.
Commit/tag:      the commit that adds this entry; no tag

## DL-147  MS7 7f (rest): A8 sensitivity, reachability share and white-noise report, results (D8 not changed)    [ID: D2, D6, D7, D8, F-4, F-7, O4, O5, CP18, DL-137, DL-139, DL-140, DL-144, DL-145, DL-146]
Date:            2026-10-17        Author:
Decision:        Ran scripts/run_A8_sensitivity.py as fixed in DL-146 (code commits: the one adding DL-146 and the config fix after it; git.dirty = false; 43 s; outputs results/A8/a8_sensitivity.csv, a8_aref.json, results/A8/sensitivity/{a8_sens_baseline_records.csv, a8_reachability.csv, a8_whitenoise.csv, a8_sens_summary.json} and run record A8sens_0000_*.json, git-ignored). The 7e records and the 7f outputs were read, not changed. No ramp run, no S2 re-run, no simulation, no criteria file, no tag. No pass/fail number applied (the plan gives none for this data; DL-146). All class results below are "provisional (D8 open, DL-137)" where the D8 call was made. D8 fit start, 2-SE rule, estimator, Hilbert/edge handling and the strict xfail unchanged.
Results:         (1) a8_aref.json written from the stored A_ref file (nothing recomputed): chosen (a) median envelope 2.176222, threshold 0.217622; the three F-1 numbers (a) 2.1762, (b) half peak-to-peak 2.7559, (c) literal peak-to-peak 5.5114; other alternates stored (mean 2.1868, maximum 3.2191, sqrt2 x RMS 2.4045). The alternates were not run as a sensitivity item (ruling 5; not in plan A8 list or D-3): listed for 7h.
  (2) Class changes against V0 (1,880 classifications; csv has every row; "chg" = class differs from V0; n excludes nothing; "not_run" = window does not fit): synthetic mode N (26 = 13 cases x W 2 s and 0.2 s): band 30-120 5, factors 1.5 8, factors 4 8, A_min 0.05 0, 0.2 4, window x0.5 3, x2 1, cycles 5 3, 20 3. Synthetic mode D (13): A_min 0.05 1, 0.2 4, every other variant 0. Stored S3 (5 mean-field records): A_min 0.05 2 (D-sus to D-none), all other variants 0. Stored S4 devalle (122 holds): A_min 0.05 2, 0.2 11, band 4, cycles 0, window x2 not run in 71 (hold 2 s, W 4 s); S4 ceni (22 holds): A_min 0.05 7, 0.2 8, band 6, cycles 20 1, others 0. Mode D has no factor, and its window enters only the gap merge. D8 involvement: of the 41 class changes in the stored records and the 5 in synthetic mode D, 39 and 5 come with a different D8 call or outcome between V0 and the variant, so the amplitude and band sensitivity of mode D cannot be separated from D8 behaviour with the plan estimator; the same holds for 4 of 4 (A_min 0.2), 7 of 8 (factors 4), 5 of 8 (factors 1.5) in synthetic mode N. This is an input to the D8 ruling, not a change.
  (3) Synthetic V0 findings, report only: (a) D_sustained40 (burst from 2 s to the record end) is D-none because the plan D8 reads it as damped (rate -192.7 +/- 24.0 per s): the Hilbert wrap of DL-140 finding 1; (b) D_ring_slow (true rate -3 per s, 35 cycles above 0.2176) is D-tr, fitted rate +0.51 +/- 0.40, non-damped: the plan's A8 slowly damped ring requirement (NS or D-none) is not met on this step-onset synthetic with the plan estimator (DL-073 onset bias); the mode-N ring_slow and ring_fast are NS with damped calls (-2.7 +/- 0.07, -6.3 +/- 2.0); (c) at W = 0.2 s (T_ramp 3 s) the noise-only record is S-rel and the trend-only record S-rel, and 40 Hz bursts of P_G ratio 1.3 and 1.8 are S+ (at W = 2 s they are NS; ratio 2.5 and up S+): the short-window noise of the PSD estimate passes the tests (DL-140 finding 4); (d) the band-edge bursts at W = 2 s: 27 Hz S+ at V0 and NS under band 30-120; 110 Hz NS at V0 and S+ under band 30-120 (at W = 0.2 s: 27 Hz S+ both, 110 Hz S-rel at V0 and S+ under band 30-120). Amplitudes in the synthetic ladder are ours.
  (4) 7e baseline-only records (12,260; class-free). Baseline rho >= 0.5: V0 8,272 (67.5 percent, median 0.640); band 30-120 5,722 (46.7 percent, median 0.480); window x0.5 8,456 (69.0 percent); window x2 8,135 (66.4 percent, 1 window on the 5 s record). O4 noise envelope (records with any sample at or above; records with a run of at least 5, 10, 20 cycles): threshold 0.1 x A_ref, whole record 460 (3.8 percent) in 125 cells; 75, 31, 3 (31 records in 8 cells at 10 cycles; matches DL-145); trimmed 381; A_min 0.05 (0.109): 6,291 records (51.3 percent) in 867 cells; 420, 110, 57 (110 records in 15 cells at 10 cycles); trimmed 5,478; A_min 0.2 (0.435): 66 records in 11 cells, no run of 5 cycles; trimmed 53; band 30-120 at 0.2176: 363 records in 98 cells; 25, 8, 1. So the noise alone crosses the A_min 0.05 threshold in most map-1 cells. Whether that bears on the classifier depends on O4 (not ruled).
  (5) Reachability (ruling 4; stored 7f baseline rho, cell value = mean of 10 seeds, per W; percent of cells with baseline rho at or above the level; UNVERIFIED arithmetic, DL-146). Columns: 0.25 (1/f at f = 4), 0.5 (plan wording, f = 2), 0.667 (1/f at f = 1.5), 0.75 (1 - 1/f at f = 4). W 0.2 s (100 cells): 100, 100, 76, 52. W 0.333 (25): 100, 92, 52, 24. W 0.593 (25): 100, 100, 60, 40. W 1.054 (25): 100, 92, 56, 32. W 1.874 (25): 100, 88, 56, 36. W 2 s (1,026 cells incl. the headline and map 1): 98.3, 60.0, 43.3, 35.6. The 0.333 column (1 - 1/f at f = 1.5) and the any-seed and per-record counts are in a8_reachability.csv. Reading of ruling 4: the four numbers given in the instruction (0.5, 0.667, 0.75 for 2, 1.5, 4) do not follow one formula; both forms are tabulated, none chosen. The surge test is on odds and has no upper bound (F-7), so these shares say how many cells the plan's sentence about the rho ratio would exclude, not how many cells cannot show a surge. The headline (rho 0.68, 0.646 to 0.731) lies above 0.667.
  (6) White noise at the real window sizes (option D; sd 0.04, 500 records per W, mode N, t_on 5 s, 20 s test span; counts of 500; non-NS = surge class or S-sus). V0: W 0.2 s: S+ 24, S-rel 278, S-abs 4, NS 194 (306 non-NS, 61 percent); W 0.333: S+ 80, S-rel 307, S-abs 9, S-sus 4, NS 100; W 0.593: S+ 7, S-rel 158, S-abs 2, S-sus 5, NS 328; W 1.054: S-rel 22, S-sus 2, NS 476; W 1.874: S-rel 2, NS 498; W 2 s: NS 500. Variants at W 0.2 s (non-NS of 500): factors 1.5: 499; factors 4: 1; window x0.5: 383; window x2: 346; cycles 5: 498; cycles 20: 112; band 30-120: 475. At W 2 s all variants give NS 500 except band 30-120 (S-rel 1). A_min 0.05 and 0.2 change nothing (the D8 fit has no threshold crossing at sd 0.04, as predicted in DL-146). Full table in a8_whitenoise.csv. No pass/fail number; white noise has no resonance (real baselines have rho 0.45 to 0.99), so these are rates of the class logic, not predictions for M3 noise.
Reason:          instruction of the project owner (rulings 1 to 6); ms7_plan.md 7f row; plan A8, RB10.
Options:         -
Chosen:          as above   Default from: DL-146
Test:            tests/test_a8_sensitivity.py (9 tests); fast suite 411 passed, 7 deselected, 1 xfailed (402 + 9).
Status:          done: sensitivity, a8_aref.json, reachability, white-noise report (the rest of the 7f row). Open for 7h: items 7, 11, 12 in docs/ms7_plan.md. D8 ruling still needed; O1 to O16 not ruled; F-6 and the post-surge rate not implemented. 7g as the plan defines it (D43, RB3(a), Heun ladder, A4 grid) not started.
Commit/tag:      the commit that adds this entry; no tag

## DL-148  MS7 7g: entry-exit prediction, RB3(a) range and A4 grid-step evidence along P1, P2, P5; design fixed before the run; no value chosen    [ID: D43, A4, A7, RB3, RB6, F-10 to F-15, CP25, DL-049, DL-135, DL-139]
Date:            2026-10-17        Author:
Decision:        7g as docs/ms7_plan.md defines it. Rule used (owner instruction): a value the plan marks UNVERIFIED or "set at MS7" is derived from the plan's own range or rule; where the plan gives a range or rule but no value, only measurements the plan names are run, candidates are listed with evidence, and the value is left for the owner. The plan gives no value for any of the four items (D43 floor levels, solver floor, A4 eta grid step, Heun dt rungs below 1e-3), so none is written as final: configs/S13.yaml carries the plan's stated S13 values and null for the four pending ones; configs/A4_grids.yaml keeps its working 0.025 unchanged (UNVERIFIED); configs/robustness_criteria.yaml is not created. Code = the commit that adds this entry: analysis/entry_exit.py (leading Re lambda along the path on nodes from the A4 grid, trapezoid I(t), t_pred, I_min, range test, T_ramp bound by scaling, stationary std of v by the Lyapunov equation), scripts/run_RB3a.py, configs/RB3a.yaml, run kind rb3a, configs/S13.yaml, tests/test_entry_exit.py. The run follows from a clean tree. No integration of any model, no hold run (F-11 not ruled), no ramp run, no S2 re-run, no criteria file, no tag. The 7e records and 7f outputs are not read or changed except results/A8/a_ref/a_ref.json (read).
  What is computed (all analysis): for P1 (path_eta), P2 (path_hypoxia), P5 (path_updown), linear and sigmoid (k = 10), the 13 T_ramp values 1 to 1000 s (10^(k/4)), delta_0 in the S13 ladder {1e-9, 1e-6, 1e-3}, A4 spacing h in {0.1, 0.05, 0.025, 0.0125, 0.00625} (a measurement grid; 0.025 is the working value): the leading Re lambda of the M3 fixed point at (eta(t), J(t)) on nodes at the A4 grid levels of eta (plus corners, and equal-time nodes in P2's J tail); I(t) by trapezoid; t_pred = first time delta_0 exp(I) = 0.1 x A_ref with A_ref 2.176222 (reading (a), DL-138, DL-139, for the 7h sign-off); after the last corner Re lambda is constant and I is extended analytically. Outputs: eta at onset and delay eta_on - eta_H; I_min over [t_on, t_pred] (the decay before the Hopf crossing); the range test delta_0 exp(I_min) >= floor over a grid of candidate floors 1e-16 to 1e-3 by decade; the T_ramp bound T_max(floor) = T ln(delta_0/floor) / (-I_min) from the exact scaling of I_min with T_ramp (checked in the tests); which of the 13 T_ramp lie inside; the time of one grid step at t_pred (h divided by the local rate of eta); the change of t_pred under grid halving in units of that step. Noise evidence for D43: the stationary std of v divided by sigma from the linearisation (Lyapunov equation, noise on v only, dv = f dt + sigma dW in tau units, the DL-072 convention, UNVERIFIED) at the start state and at eta_H - 1, -0.5, -0.25, -0.1. Heun dt rungs: no run; cost by arithmetic from the DL-104 rates only, in the results entry.
  Acceptance numbers: the plan's own numbers are "one A4 grid step" (RB3(a)) and "under 5 percent" (RB6); both are for A11 and MS8 on ramp runs, and neither is applied here. For everything in this step the plan gives no number, so everything is a measurement; nothing is judged. The grid-halving comparison (t_pred moved by under one step) is our test, UNVERIFIED, reported not applied. Anything that uses the D8 call is not used here. Timing: analysis, about 0.01 s per path evaluation, projected under one minute for the full set; timed on one case and under 10 concurrent copies first (7g rule 3).
Reason:          instruction of the project owner (7g); ms7_plan.md 7g row; plan 5.2 A4 and A7, Table 7.2 RB3 and RB6, D43.
Options:         -
Chosen:          as above   Default from: plan wording for the rules; ours where marked
Test:            tests/test_entry_exit.py (constant eigenvalue gives the analytic t_pred, decay-then-growth closed form, I_min proportional to T_ramp, range shrinks as the floor rises, Hopf point, grid halving on the headline, node times, sigmoid inverse, Lyapunov scaling).
Status:          design fixed, run next (results in DL-149). D8 open (DL-137).
Commit/tag:      the commit that adds this entry; no tag

## DL-149  MS7 7g: entry-exit, RB3(a) range, D43 noise evidence, A4 grid step and Heun ladder: results and candidates; nothing chosen, STOP for ruling    [ID: D43, A4, A7, RB3, RB6, F-10 to F-15, CP25, DL-049, DL-148]
Date:            2026-10-17        Author:
Decision:        Ran scripts/run_RB3a.py as fixed in DL-148 (code commits fe2c6ff and the driver fix after it, which adds the headline 120 s, not on the 13-value list, as an extra T_ramp; git.dirty = false; 10 s; one case timed under 10 concurrent copies first: 30 path evaluations in 0.9 s). Outputs results/A4/a4_rb3a_range.csv (1,260 rows), a4_rb3a_floor.csv (252 rows), a4_rb3a_summary.json, record results/A4/rb3a/RB3A_0000_*.json (git-ignored). No integration, no hold run, no ramp run, no S2 re-run, no criteria file, no tag; the 7e records and 7f outputs untouched. No D8 call used. A_ref 2.176222 (threshold 0.217622) is the DL-138 reading, for 7h. No value was written as final: configs/S13.yaml holds null for the four pending items and configs/A4_grids.yaml still holds the working 0.025, UNVERIFIED.
Results:         (1) Headline (P2, linear, 120 s, delta_0 1e-6, h 0.025): t_pred 115.22 s on the run clock (t_on 5 s, so 110.2 s after t_on); eta at onset 4.6109; delay eta_on - eta_H 1.7149; I_min = -1122.5 (the decay before the Hopf crossing, in e-folds); one grid step in time at t_pred 0.857 s. delta_0 = 1e-9 and 1e-3 give 115.58 s and 114.87 s: one decade of delta_0 moves t_pred by 0.36 s, 0.42 of a grid step.
  (2) Range: I_min is proportional to T_ramp (tested), about -9.8 per second of T_ramp on P1 and P5 linear (-9.35 on P2 linear; sigmoid -16.8 and -16.7). delta_0 exp(I_min) at the headline is e^-1122 of delta_0, below any double-precision value, so the headline 120 s lies outside the RB3(a) range for every floor at or above 1e-16 and for every delta_0 in the ladder. T_max(floor) = T ln(delta_0/floor)/(-I_min) depends on the floor only through a logarithm. P1 linear, delta_0 1e-6: floor 1e-16 gives T_max 2.36 s, 1e-13 1.65 s, 1e-12 1.42 s, 1e-10 0.94 s, 1e-9 0.71 s; at floor equal to delta_0 or above there is none (the csv prints T_max <= 0 there; read it as "no T_ramp"). P2 linear, delta_0 1e-6: 2.46, 1.72, 1.48, 0.98, 0.74 s for the same floors. Of the 13 T_ramp (1 to 1000 s) at most the first two (1 and 1.78 s) are ever inside, and only for floors at or below about 1e-16 to 1e-12 (P1 linear delta_0 1e-6: 2 of 13 at floor 1e-16, 1 of 13 at 1e-13 and 1e-12, 0 at 1e-10 and above; delta_0 1e-3: up to 2 of 13; P2 linear at 1e-3 and floor 1e-16: only 3.16 s, 1 of 13; delta_0 1e-9: at most 1). The floor value decides 1 to 2 runs per path and profile at the boundary, not the other 11 or 12. Consequence for the gate wording: RB3(a) (Table 7.2, G6) is judged on 0 to 2 of 13 T_ramp per path and profile and on none at the headline; RB3(b) and RB6 are then the only G6 checks at the headline. This follows from the plan's own rule and the A4 eigenvalues; it is reasoned arithmetic until MS8 (the entry-exit form is [reasoned, not tested] in the plan) and is the structural reading of CP25 ("RB3(a) predicts its own failure at slow ramps").
  (3) Onset predicted at all (delta_0 1e-6, h 0.025, 14 T_ramp incl. the headline): P1 at every row, P5 at all but 2 (linear) and 3 (sigmoid) of 42 rows; P2 linear except the fastest ramps (9 of 42 rows with none); P2 sigmoid never: the integral does not return to delta_0 exp(I) = 0.2176 before J reaches 0 (Re lambda final -0.1355). P1 sigmoid onset falls after the eta ramp end (eta_on = eta_peak, so the grid tolerance in eta has no meaning there; tol_step blank). Delay eta_on - eta_H on P1 linear: 2.000 (T 1 to 10 s, onset on the hold) to 1.898 (1000 s).
  (4) A4 grid step (F-13). t_pred moves under grid halving by at most 0.0141 of one step (h 0.025 to 0.0125; median 0.0017; 0.0072 for 0.0125 to 0.00625; 0.0223 for 0.05 to 0.025; 0.0484 for 0.1 to 0.05; 137 comparable rows each), so the trapezoid on the grid nodes is converged at every candidate spacing; the spacing sets only the width of the RB3(a) tolerance, h / (local rate of eta): headline 0.857 s at 0.025, 7.1 s at T_ramp 1000 s, 0.13 s at 17.8 s. Candidates (all UNVERIFIED): 0.1 (3.4 s at the headline, about 9.5 delta_0 decades), 0.05 (1.7 s, about 4.8), 0.025 (0.857 s, the working value, about 2.4), 0.0125 (0.43 s, about 1.2), 0.00625 (0.21 s, about 0.6); the decade counts are proportional arithmetic from 0.36 s per delta_0 decade. A coarser step passes more runs; a step finer than the t_pred shift from delta_0 makes the test depend on a free parameter. Recommendation: keep 0.025 (converged, a tolerance of a little over two delta_0 decades, already the A4 grid so no recomputation); alternatives for you: 0.0125 or 0.05. The A_ref reading changes ln(0.1 A_ref) by 0.24 (half peak-to-peak) or 0.93 (literal), about 0.03 s at Re lambda near 0.3 per tau (arithmetic, not run), well inside one step.
  (5) D43 floor levels (F-10). Stationary std of v over sigma from the linearisation (noise on v only, DL-072 convention, UNVERIFIED): 0.6292 at the start state (DL-120 gave 0.622; the 1.2 percent difference is not explained here), 0.762 at eta_H - 1, 1.080 at -0.5, 1.535 at -0.25, 2.437 at -0.1, diverging at eta_H. A noise floor therefore has no single amplitude along a ramp: 0.63 sigma_floor at the start, growing towards the Hopf point. Candidates for the levels: (A) sigma_floor = delta_0 / 0.629 for delta_0 in {1e-9, 1e-6, 1e-3}, i.e. 1.59e-9, 1.59e-6, 1.59e-3 (std at the start state equals the delta_0 ladder; our F-10 proposal; all below sigma 0.0624); (B) sigma_floor directly on {1e-9, 1e-6, 1e-3} (std at start 0.63 of each); (C) relative to sigma, {1e-4, 1e-3, 1e-2} x 0.0624 = 6.2e-6, 6.2e-5, 6.2e-4. Which amplitude the range test compares with (std at the start state, at eta_H - 0.5, or sigma_floor itself) changes the floor by a factor 0.6 to 1.7, and T_max only logarithmically; the ladder matters more. Per (2), for any floor from 1e-9 to 1e-3, 0 to 1 of the 13 T_ramp are inside. Recommendation: (A), because it ties the levels to the delta_0 ladder the plan already has; three levels; the range test uses the std at the start state (ours).
  (6) Solver floor (F-11). Not measured: a hold run is not a measurement the plan names and F-11 is not ruled. Arithmetic candidates, not measurements: 1e-12 (solver.atol, base.yaml), about 6e-11 (rtol 1e-10 times |v*| = 0.595 at the start state), about 1.3e-16 (machine epsilon times |v*|). By (2) they differ in T_max by 1.7 to 2.5 times (P1 linear delta_0 1e-6: 2.36 s at 1e-16, 1.42 s at 1e-12, 0.97 s at 6e-11) and decide whether T_ramp 1.78 s is inside. Recommendation: allow the one hold run (constant parameters at the P2 start state, delta_0 = 0, headline length) so the number is measured; or state the floor as an assumption at 1e-12 (atol).
  (7) Heun dt ladder (F-14). Not run. The mode-N output step is 0.1 tau and run_mf_noisy needs dt to divide it: 1e-3, 5e-4, 2.5e-4, 1e-4 all do (strides 100, 200, 400, 1000). Cost by arithmetic from the DL-104 rates (3.65e-8 s per step alone, 1.51e-7 under 10 copies; UNVERIFIED at these lengths): headline P2 (16,500 tau) at 1e-4 is 1.65e8 steps, about 6 s alone, 25 s loaded; the longest P2 (T_ramp 1000 s, 126,500 tau) 1.27e9 steps, about 46 s alone, 190 s loaded. Cost is no constraint on the finest rung. Candidates: (A) {1e-3, 5e-4, 2.5e-4, 1e-4} tau, the four rungs the plan lists for the network in S13 (our F-14 proposal); (B) {1e-3, 5e-4, 2.5e-4}; (C) {1e-3, 1e-4}. The comparison statistic (same Brownian path summed to the finer step, median over seeds) is not in the plan and is for your ruling. Recommendation: (A) with coupled Brownian increments.
  (8) F-15 (RB3(b)): not run. By (2) the floor levels of (5) leave at most 1 to 2 runs inside RB3(a)'s range; "delay shrinks as the floor rises" concerns floored runs and is tested at MS8 on the headline, outside RB3(a)'s range. Proposal unchanged: monotone non-increasing median delay over the three levels, 10 seeds, values reported.
Reason:          instruction of the project owner (7g rules 1 to 4); ms7_plan.md 7g row; plan 5.2 A4 and A7.
Options:         -
Chosen:          no value chosen; candidates and recommendations above. Default from: plan rules; ours where marked
Test:            tests/test_entry_exit.py (10 tests); fast suite 421 passed, 7 deselected, 1 xfailed.
Status:          7g computation done; STOP for the owner's ruling on: floor levels (F-10) and what the range test compares, the solver floor (F-11, hold run), the A4 spacing (F-13), the Heun rungs and statistic (F-14), RB3(b) (F-15), and whether RB3(a) judged on 0 to 2 of 13 T_ramp is acceptable (finding 2). configs/S13.yaml pending items stay null. D8 open (DL-137); O1 to O16, O4/O5, reachability and A_ref reading for 7h, not ruled.
Commit/tag:      the commit that adds this entry; no tag

## DL-150  MS7 7g: F-11 solver-floor hold run, design fixed before the run    [ID: D43, A7, F-11, CP25, DL-148, DL-149]
Date:            2026-10-17        Author:
Decision:        Owner ruling (7g continuation): run the one constant-parameter hold run to measure the noise-free solver error floor; fix the design here first. Plan wording (A7, section 5.2; section 12 "solver and noise floor values that bound the RB3(a) range"; Table 6.2 initial state: delta_0 "would decay to the solver floor") gives no measurement protocol, so the design is ours, UNVERIFIED.
  Design. (1) Run: configs/F11.yaml, kind mf, mode D, M3 at ref_devalle, DOP853 rtol 1e-10, atol 1e-12, max_step 0.05 tau, dt_out 1 ms (all base.yaml), start = exact stable fixed point at the P2 start parameters (eta_bar = eta_H - 1.5 = 1.3960461989737856, J -21, Delta 0.3, tau_d 5 ms), every parameter constant for the whole run (P2 geometry with eta_start = eta_peak and J0 = J_end, so the length is the headline's 165 s = 16,500 tau), solver.delta0 = 0 (no perturbation). No ramp, no noise, no seeds. (2) Measured: the departure of the computed state from its start value, |v(t) - v(0)| over all 165,001 output samples (r and s also reported). Because the start is the fixed point and the flow is constant, any departure is solver or round-off error. (3) Equivalent amplitude: in v units, the unit of delta_0 (delta_0 is added on v, 6.2), so the candidate floor is dv_max = max_t |v(t) - v(0)|, directly comparable with delta_0 exp(I) in the RB3(a) range test. Also reported, not candidates: the maximum over the second half, the final value, the RMS, dr_max, ds_max, and dv_max in units of eps x |v(0)|. (4) Ambiguity check before the run (25 s slice, T_ramp 8 s, scratchpad, not a result): dv_max = 6.7e-16 (3 ulp of 0.595), the second-half maximum and the final value the same; so max, second half and final agree within one decade and the plan wording cannot move the value by a decade. (5) Limits, stated: a constant-parameter run at a stable fixed point measures round-off and step-control error at rest, not the error accumulated while tracking a moving fixed point near the Hopf point or while a perturbation grows; it is a lower bound of the solver error in a ramp run. The value is a candidate floor, UNVERIFIED, draft, not frozen. The rtol dependence is not measured (the plan keeps the rtol comparison for noise-free ramp runs, reported not failed). (6) Timing first: 25 s slice took 13.06 s wall, 5.2e-3 s per tau; projection for 16,500 tau is about 86 s, under the one-hour rule. Code: src/mprsurge/analysis/solver_floor.py (analysis only), scripts/run_F11.py (reads the run, writes results/F11/f11_floor.json and a record, integrates nothing), run kind f11floor, tests/test_solver_floor.py (4 tests). The run itself is made by `python -m mprsurge.run --config configs/F11.yaml` from a clean tree. No ramp run, no S2 re-run, no criteria file, no tag; the 7e records and 7f outputs are untouched. D8 not used.
Reason:          owner ruling; ms7_plan.md 7g row, F-11.
Options:         -
Chosen:          as above   Default from: ours (plan has no protocol), UNVERIFIED
Test:            tests/test_solver_floor.py (4 tests)
Status:          design fixed, run next (result in DL-151).
Commit/tag:      the commit that adds this entry; no tag

## DL-151  MS7 7g: F-11 solver-floor hold run, result    [ID: D43, A7, F-11, DL-148, DL-149, DL-150]
Date:            2026-10-17        Author:
Decision:        Ran configs/F11.yaml (python -m mprsurge.run, from the clean tree of commit fda66a4, git.dirty = false, 88.2 s wall against the 86 s projection) and scripts/run_F11.py as fixed in DL-150. Outputs results/F11/F11/F11_0000_855b0538c3fb.{npz,json}, results/F11/f11_floor.json and record F11FLOOR_0000_*.json (git-ignored). No ramp, no noise, no S2 re-run, no criteria file, no tag; D8 not used; 7e records and 7f outputs untouched.
Results:         165,001 samples (165 s). max |v - v(0)| = 6.661e-16, identical for the second-half maximum and the final value; RMS 6.661e-16; dr_max = 0 and ds_max = 0 exactly. dv_max = 5.04 x eps x |v(0)| (v(0) = -0.5947). The departure is a constant offset of a few ulp in v that appears at the first step and does not grow: no accumulating drift over 16,500 tau. Candidate noise-free solver floor (v units, the unit of delta_0): 6.66e-16, UNVERIFIED, draft, not frozen. The plan-wording ambiguity check of DL-150 held: max, second half and final all give 6.66e-16 (no decade of spread). Limits as in DL-150 (5): this is the floor at rest, a lower bound for a ramp run; the rtol dependence is not measured.
  Arithmetic effect on RB3(a) (from the exact scaling of DL-149, not a new run): T_max = T ln(delta_0/floor) / (-I_min); for P1 linear, delta_0 1e-6 the 1e-16 row gave 2.36 s, so floor 6.66e-16 gives about 2.36 x ln(1.5e9)/ln(1e10) = 2.16 s, which still holds the 1.78 s ramp (2 of 13 at the boundary, as at 1e-16). The D43 floors (1e-9 and above) are far above this solver floor, so for the D43 runs the noise floor, not the solver, bounds the range.
Reason:          owner ruling F-11; ms7_plan.md 7g row.
Options:         -
Chosen:          candidate floor 6.66e-16 written to configs/S13.yaml (DL-152)   Default from: measured; protocol ours, UNVERIFIED
Test:            tests/test_solver_floor.py (4 tests)
Status:          done.
Commit/tag:      the commit that adds this entry; no tag

## DL-152  MS7 7g: owner rulings F-10, F-11 (value), F-13, F-14, F-15, G6 reading; values entered as draft, not frozen; open item 13 closed    [ID: D43, A4, A7, RB3, RB6, G6, F-10 to F-15, CP25, DL-148, DL-149, DL-150, DL-151]
Date:            2026-10-17        Author:
Decision:        Entered the owner's 7g rulings. Every value below is UNVERIFIED (no source gives it) and "draft, not frozen"; nothing is frozen until 7j, no criteria file is created, no tag. The plan is not edited. D8 is open (DL-137, DL-140, DL-147); nothing in 7g uses the D8 call.
  F-10 (D43 levels): delta_0 = 1e-9, 1e-6, 1e-3 (nominal labels); sigma_floor = delta_0 / 0.629 = 1.59e-9, 1.59e-6, 1.59e-3 (v-units per sqrt(tau), the DL-072 convention; all below sigma 0.0624). 0.629 = stationary std of v over sigma at the P2 start state (Lyapunov, noise on v only, DL-149); it rises to 2.44 at eta_H - 0.1 and diverges at eta_H, so delta_0 is a nominal label of the level, not the amplitude along the ramp. Gap to DL-120's 0.622 (0.62229): a 1.1 percent difference, explained as sampling: DL-120's value is an empirical mean over 10 seeds of the sample std of 1 ms values over 5 s, and its single-run seed sd is 3.5 percent (DL-120), so the standard error of the 10-seed mean is about 1.1 percent, the size of the gap; 0.629 is the exact linear value. Not a different model. (Arithmetic from the DL-120 numbers; the DL-120 runs were not repeated.) The sigma = 0.0624 calibration is not touched.
  F-11 (solver floor): measured in DL-151, candidate 6.66e-16 (v units), UNVERIFIED, draft, not frozen.
  F-13 (A4 grid step): 0.025 in eta-bar, entered in configs/S13.yaml (a4_eta_bar_grid_step), realised by configs/A4_grids.yaml (801 points on [-10, 10]); configs/A4.yaml carries it as a comment only, because its schema rejects a new key and a new key in A4_grids.yaml values would change the A4 run hash (a deviation from the instruction wording "into configs/A4.yaml"; tests check the three agree). The A4 hash is unchanged.
  F-14 (Heun ladder): {1e-3, 5e-4, 2.5e-4, 1e-4} tau with coupled Brownian increments across rungs (each finer rung's increments sum to the 1e-3 rung's, per seed); default 1e-3 tau; RB6 compares the default with the finest rung (1e-4); in configs/S13.yaml. The 5 percent statistic is the plan's; the per-seed delay and the median over seeds as the statistic is not stated in the ruling and is not entered (to settle at 7h).
  F-15 (RB3(b)): the median delay over seeds decreases strictly over the three floor levels, each step lower than the one before, 10 seeds per level; flat or tied fails; no scaling law; no number beyond this. Recorded in configs/S13.yaml (rb3b_form) for the draft criteria.
  G6 reading, a plan interpretation for the owner's sign-off at 7h (not a change): the headline (120 s) is outside the RB3(a) range (DL-149 (2): I_min about -9.4 per second of T_ramp, e^-1122 of delta_0 at 120 s), and the plan says runs outside the range are reported, not judged. So the RB3(a) clause of G6 is "not judged at the headline"; G6 at the headline rests on RB3(b) and RB6; RB3(a) is reported with its coverage, 0 to 2 of the 13 T_ramp values per path and profile (DL-149 (2), DL-151). Open for 7h sign-off, with the other items 7h already holds (O1 to O16, O4/O5, reachability, A_ref reading). Not ruled here: O1 to O16, O4/O5, reachability, A_ref reading; F-6 and the post-surge rate are not implemented.
Reason:          owner rulings of the 7g continuation; ms7_plan.md 7g row.
Options:         -
Chosen:          as above   Default from: owner ruling; UNVERIFIED
Test:            tests/test_entry_exit.py (2 new: the A4 step agrees across configs; S13 ruled values consistent); fast suite below.
Status:          7g done. Open item 13 closed (docs/ms7_plan.md). Next: 7h (criteria file) only on the owner's instruction.
Commit/tag:      the commit that adds this entry; no tag

## DL-153  MS7 7g2 (inserted by owner ruling, not in the plan): test of candidate fixes for the D8 estimator on synthetic data and stored records; design and acceptance numbers fixed before the run    [ID: D8, DL-062, DL-073, DL-136, DL-137, DL-140, DL-147]
Date:            2026-10-17        Author:
Decision:        Owner ruling: test candidate fixes for the D8 damped / non-damped estimator on synthetic data and stored records only, in a study module, not in the classifier. Inserted into docs/ms7_plan.md before 7h; 7h stays blocked until the owner rules on the result. The plan estimator stays the default (surge_metrics.PlanD8Estimator, PLAN_D8), the strict xfail stays, and the D8 wording, the fit start and the 2-SE rule are not changed in any live code path (a test checks that surge_metrics does not import the candidates). Code = the commit that adds this entry: analysis/d8_candidates.py (candidates, behind the D8Estimator interface), analysis/d8_study.py (families, summaries, ranking), scripts/study_d8_candidates.py, configs/d8_cand.yaml (run kind d8cand), tests/test_d8_candidates.py (15 tests). The run follows from a clean tree. No model run, no M3 ramp-study run, no S2 re-run, no criteria file, no SHA freeze, no tag. The 7e records and the 7f/7g outputs are not read or changed (stored inputs: the S3 limit-cycle record results/S3/devalle/devalle_0000_9e49def91dfc.npz and results/A8/a_ref/a_ref.json, read only). Any change of the D8 wording in Table 2.1 or of the 2-SE rule needs the owner's ruling after the report.
  Candidates (each UNVERIFIED; the Technical Plan defines none of them; Table 2.1 says only "fitted from the threshold crossing over the first 10 cycles" and "damped only if negative by more than 2 standard errors of the fit"). Four choices, each with the plan's own behaviour as level 0, tested as a full grid (3 x 3 x 2 x 3 = 54 candidates, the plan first):
   (c) edge treatment of the periodic Hilbert wrap (DL-140 finding 1), same band 25 to 100 Hz and same order-4 zero-phase filter: none (the plan); zero (zero-pad both ends by 1 s before the filter and the Hilbert transform, crop afterwards); odd (odd reflection about the end values, 1 s each end, crop). The 1 s pad is ours (the A_ref edge convention, DL-139).
   (a1) fit start: 0, 1 or 2 lower-band-edge periods (1 / 25 Hz = 40 ms each) after the threshold crossing; the 10-cycle window is counted from the shifted start. 40 and 80 ms are ours; the DL-073 smear is about 20 ms.
   (a2) minimum-window rule: a window spanning fewer than 5 cycles gives no call (nan, non-damped by the plan's own nan convention); 0 = the plan. 5 is the plan's own short-ring length (A8 5-cycle ring; RB10 min_cycles 5).
   (b) standard error: plain (the plan); ar1 (plain SE times sqrt((1 + phi) / (1 - phi)), phi the lag-1 autocorrelation of the OLS residuals clipped to [0, 0.999], i.e. effective sample size n (1 - phi) / (1 + phi)); cycle (one envelope sample per cycle: the first sample at each 2 pi of unwrapped phase from the window start, slope and plain OLS SE on those samples, at least 3). No free parameter in either.
   (d) combinations: all 54 are run; the single-factor ones (plan plus 7) are the named candidates (a) to (c), the rest are the combinations. Candidate id: E{n,z,o}-S{0,1,2}-M{0,5}-{plain,ar1,cycle}.
  Options not tested, with reasons (your call whether any is wanted): Newey-West (needs a lag) and block bootstrap (needs a block length), neither defined by the plan; DL-073 (b) causal or one-sided filter and (c) analytic signal of the unfiltered v (both change the filter or the signal, which this step may not do); (e) calibration on step-onset rings (a fitted correction, not defined). Recommendation if you want one of them tested: the start shift and the AR(1) or per-cycle SE are the closest to the plan wording ("from the threshold crossing", "standard errors of the fit"); the edge pad is an implementation detail of the Hilbert transform and does not touch the wording.
  Pre-registered numbers, the DL-136 numbers unchanged and not relaxed: (i) in every cell with |true rate| >= 2 per s the D8 call matches the sign of the true rate in >= 95 percent of draws; (ii) false "damped" <= 5 percent in every zero-growth cell; (iii) bias, 2-SE coverage and the inflation factor k (95.45th percentile of |error| / SE) are reported, not pass/fail. One change of counting, stated here: a draw whose fit is undefined (nan) is counted as a non-damped call over all 200 draws (the plan's convention), not dropped as in estimator_study.summarize; bias, coverage and k use the defined fits only. (i) and (ii) are applied cell by cell in every family with these numbers; "missed" means one cell fails.
  Families (200 draws per cell throughout; root entropy 20261008):
   F1 = the 7b scenarios unchanged (estimator_study.scenarios(): rings at 14 rates -25 to +12 per s, onset at the record start or as a step at 1 s, noise 0.005 and 0.02; zero-growth sinusoid in noise; stationary AR(2)), same generator settings as DL-137 (A0 = 5 x threshold x exp(0.3 max(-rate, 0)), growth capped 0.5 s after onset), same stream (spawn key (7, 2)), so the plan row must reproduce DL-137 (26 of 36 cells below 95 percent in (i); all 5 zero cells above 5 percent in (ii)). This is the table the DL-136 numbers come from.
   F2 = gradual onset: the F1 ring with a raised-cosine amplitude gate of 0.1 s or 0.5 s from the onset at 1 s (ours; a step is 0 s), noise 0.005 and 0.02, 14 rates; spawn key (7, 8, 2). Truth is the sign of the exponential rate after the gate. For the 0.5 s gate and damped rings the envelope really rises inside the first-10-cycle window, so the truth sign is ambiguous there; the two gate lengths are reported separately and both are counted in the ranking.
   F3 = DL-140 finding 1: 14 s, quiet until 2 s, 0.5 s rise to a sustained 40 Hz sinusoid of amplitude 1.5 to the record end, noise 1e-4, random phase, v from t_on = 1 s, threshold 0.217622 (0.1 x A_ref, reading (a)); truth non-damped; (ii) applies (false damped <= 5 percent); spawn key (7, 8, 3).
   F4 = the stored ref_devalle limit cycle (S3 record, 10 s, 1 kHz), v from t_on = 0, 1 and 3 s, threshold 0.217622: must be non-damped at all three (zero false damped of 3). A supplement over t_on = 0 to 4 s in steps of 0.25 s (17 values) is reported, not judged.
   F5 = the A8 ring tests: (a) the five-cycle ring of test_surge_metrics (record start, lam = ln(1/0.1) / (5/40), noise 1e-4, 200 draws): growth must be negative in >= 95 percent; (b) the slowly damped ring (15 cycles above threshold, step onset at 1 s, noise 1e-4, 200 draws): must be called damped in >= 95 percent (class NS or D-none needs it); the fitted rate within 10 percent of the truth is reported (the strict-xfail criterion; the xfail itself is not touched); (c) the four ring cases of the DL-146 synthetic set (D_ring_slow_-3, D_ring_fast_-25 in mode D; N_ring_slow_-3, N_ring_fast_-25 in mode N at T_ramp 120 s and 3 s) classified with the candidate as D8: the class must be NS or D-none. A8 failures = the number of failed items among (a), (b) and the (c) cases.
   F6 = white noise at the real window sizes, class level: mode N, t_on 5 s, 25 s records, T_ramp 3.16, 10, 17.78, 31.62, 56.23, 100 s (W = 0.2, 0.333, 0.593, 1.054, 1.874, 2 s), 500 records per cell with the DL-147 draws (white_record, spawn key (7, 6, 2, k)), at sd 0.04 (DL-147: the band envelope never reaches 0.2176, so the D8 fit is never run and no D8 candidate can change a class) and, because of that, at sd 0.2 and 0.45 (ours, UNVERIFIED), where the band envelope crosses the threshold and D8 is called. Counts per class with denominators, plus how often D8 was called and said damped. All 54 candidates. No pass/fail number (none exists); the plan row must reproduce DL-147 at sd 0.04 (W 0.2 s: 306 of 500 non-NS). "Band-limited white noise" is read as this white-noise record seen through the detector band; no extra generator.
  Ranking (lexicographic, lower is better): (1) F1 failing cells ((i) + (ii)); (2) F4 damped calls at t_on 0, 1, 3; (3) F3 failure (1 if false damped > 5 percent); (4) A8 failures; (5) F2 failing cells; (6) F1 mean absolute bias on the damped-ring cells. The literal DL-136 acceptance is F1 (i) and (ii) both met; a candidate that meets it and fails elsewhere is reported as such. The study chooses nothing; the recommendation goes to you.
  Timing (rule: time under 10 concurrent copies, stop for a ruling if the projection is over one hour): 10 concurrent copies of a sample gave 40 draws x 54 candidates in 0.55 to 0.62 s and 100 white-noise classifications in 0.48 to 0.55 s. Projection: F1 and F2 (22,600 draws) about 6 core-minutes, F6 (972 tasks of 500 records) about 80 core-minutes, the rest seconds: about 10 minutes wall at 10 workers, inside the limit (UNVERIFIED arithmetic from the sample).
Reason:          instruction of the project owner (7g2); DL-136 D-2, DL-137, DL-140 findings 1 and 2, DL-147.
Options:         as listed
Chosen:          as above   Default from: DL-136 pre-registration (numbers); ours where marked
Test:            tests/test_d8_candidates.py (15 tests: grid and ids; the plan candidate equals envelope_growth and PlanD8Estimator; the shift moves the step-onset fit to the truth; AR(1) keeps the rate and inflates the SE; the minimum-window rule gives nan; the edge pad removes the finding-1 wrap; filter and band untouched; undefined fits count as non-damped; ramp generator; DL-136 numbers unchanged; the F1 stream equals the 7b stream; surge_metrics does not import the candidates; run kind and config).
Status:          design fixed, run next (results in DL-155). D8 open (DL-137, DL-140); O1 to O16, O4/O5, reachability, the G6 reading and the A_ref reading choice stay for the 7h sign-off, not ruled.
Commit/tag:      the commit that adds this entry; no tag

## DL-154  MS7: RB6 statistic as ruled by the owner, recorded for the 7h sign-off    [ID: RB6, F-14, A7, DL-152]
Date:            2026-10-17        Author:
Decision:        Recorded as ruled, for the owner's sign-off at 7h (DL-152 left the statistic to settle at 7h): the RB6 statistic is the median delay over 10 seeds at the default Heun step (1e-3 tau) against the median delay over the same 10 seeds at the finest rung (1e-4 tau), same seeds and coupled Brownian increments across the rungs (F-14, DL-152), and the relative change must be below 5 percent (the plan's number, Table 7.2 RB6). UNVERIFIED: no source gives the statistic. Readings of ours, not ruled, marked for 7h: "relative change" is taken relative to the median at the default step, |median(1e-4) - median(1e-3)| / median(1e-3); the delay per seed is eta at onset minus eta_H as in Table 2.1 (onset_delay), and a seed with no onset is reported and left out of the median with its count; the comparison is made on the runs where the floored A7 runs are made (MS8 headline subset). Nothing is run here; configs/S13.yaml and the criteria file are not changed; no criteria file frozen.
Reason:          instruction of the project owner (7g2 item 5); DL-152 left the statistic open.
Options:         -
Chosen:          as ruled   Default from: owner ruling; plan Table 7.2 RB6 (the 5 percent)
Test:            docs only.
Status:          recorded; for the 7h sign-off.
Commit/tag:      the commit that adds this entry; no tag

## DL-155  MS7 7g2: D8 candidate-fix study, results; no candidate meets the DL-136 numbers; nothing changed, STOP for ruling    [ID: D8, DL-062, DL-073, DL-136, DL-137, DL-140, DL-147, DL-153]
Date:            2026-10-17        Author:
Decision:        Ran scripts/study_d8_candidates.py as fixed in DL-153 (code commits ff5666a and the csv-writer fix after it; first attempt crashed at the csv write after the computation, outputs deleted, rerun from the clean tree; git.dirty = false; 224 s wall at 10 workers against the 10 min projection). Outputs results/A8/d8_cand/ (d8cand.json, d8cand_summary.csv, d8cand_cells.csv, d8cand_lc.csv, d8cand_a8.csv, d8cand_whitenoise.csv, run record), git-ignored. Synthetic data and the stored S3 limit cycle only. The plan estimator, the D8 wording, the fit start, the 2-SE rule and the strict xfail are unchanged; no S2 re-run, no criteria file, no tag.
Results:         Reproduction check passed: the plan row gives 26 of 36 cells below 95 percent in (i), 5 of 5 zero cells above 5 percent in (ii) (DL-137), and the DL-147 white-noise counts at sd 0.04 (306, 400, 172, 26, 2, 0 of 500).
  (1) DL-136 numbers on F1, 54 candidates: (i) met by none (fewest failing cells 6 of 36); (ii) met by 12 (false damped <= 5 percent); both met by none. (iii) reported in the csv.
  (2) Best by the pre-registered ranking: Ez-S2-M5-ar1 (zero-pad, start 2 periods = 80 ms after the crossing, minimum window 5 cycles, AR(1) SE). F1: (i) MISSED in 6 cells, all damped step-onset rings: -25 per s 0 percent match (both noises; window under 5 cycles gives no call, bias +28 per s), -3 per s 59 to 63 percent, -2 per s 84 to 87 percent; (ii) met (max false damped 4.0 percent); false non-damped mean 0.16 (plan 0.45); inflation k max 2.5 (plan 619); 2-SE coverage 0.99 to 1.00 on record-start rings. Stored limit cycle: non-damped at t_on 0, 1, 3 and at all 17 grid values (plan: damped at 1 s, 2.2 SE; rate -0.54 +/- 0.24, with the candidate -0.30 +/- 2.2). Finding 1 case (F3): false damped 0.0 (plan 34.5 percent). F5: 4 of 8 items fail (five-cycle ring growth negative in 0 percent because the minimum window gives no call; slowly damped ring called damped in 86.5 percent, below 95; N_ring_fast_-25 at T_ramp 120 and 3 s becomes a surge class instead of NS). Fitted rate within 10 percent of the true -6.14 (xfail criterion): 86.5 percent of draws (plan 0.5 percent); the strict xfail itself untouched. F2 (gradual onset): ramp 0.1 s: 2 of 14 (i) cells fail (rate -25), (ii) met; ramp 0.5 s: 6 (i) cells fail (rates -6, -3, -2 at both noises, 0 percent match: the envelope rises through the whole window, so the sign of the truth is ambiguous there, DL-153).
  (3) What each choice does (single-factor rows, F1 failing (i)/(ii) cells; plan 26/5): start shift 1 period 12/5, 2 periods 10/5 (fixes step-onset damped rings, not the false-damped rate); AR(1) SE alone 28/3, per-cycle SE alone 24/0 (cures false damped, not the sign match); minimum window alone 12/3; zero-pad alone 10/1, odd reflection alone 12/3 (the wrap, finding 1: F3 34.5 percent to 0). The combination of shift, minimum window and an autocorrelation-aware SE is needed to reach (ii); the minimum window costs the -25 per s cell and the five-cycle ring growth item. Odd reflection made the stored limit cycle damped at t_on 1 s in single-factor use (plan-like); zero-pad did not.
  (4) White noise, class level (non-NS of 500; counts for all 54 candidates in d8cand_whitenoise.csv). The D8 call is never damped at sd 0.04 (no candidate changes a class), so W 0.2 s stays 306, 0.333 s 400, 0.593 s 172, 1.054 s 26, 1.874 s 2, 2 s 0 for every candidate. At sd 0.45 the plan estimator calls noise damped in 101 of 500 (W 0.2 s), 133, 57, 10, 1, 0 and so lowers non-NS to 205, 267, 115, 16, 1, 0; Ez-S2-M5-ar1 never calls noise damped (0 of 500 at every W) and keeps 306, 400, 172, 26, 2, 0. So a trustworthy SE removes the accidental noise filtering of the plan estimator; the class-level false-surge rate at short W is set by the power tests and the 10-cycle rule (DL-140 finding 4), not by D8, and no D8 candidate lowers it.
  (5) Missed, in short: no candidate meets (i) and (ii) together; the best misses (i) in 6 of 36 F1 cells (damped step-onset rings at -25, -3, -2 per s) and fails 4 of 8 A8 ring items, so it trades the false-damped and limit-cycle failures for new ones. Recommendation (for your ruling, nothing applied): (A) keep the plan D8 estimator for MS7 and report its failures, as DL-073 (d) allows; or (B) if you accept a change, rule in this order: zero-pad edge treatment (does not touch the Table 2.1 wording; cures finding 1), an autocorrelation-aware SE (AR(1) or per-cycle; touches only "standard errors of the fit"), and the fit-start shift (touches "from the threshold crossing" and your ruling), with the minimum-window rule left out unless you accept losing the fast-ring D8 call; then re-run this study once on that single choice. The plan wording needs a different gate for fast-damped rings (-25 per s) than a D8 fit, e.g. the cycle count already classes them NS; that is a plan question for you.
Reason:          instruction of the project owner (7g2); DL-153.
Options:         (A) keep plan D8 and report; (B) the staged change above; (C) test Newey-West, block bootstrap or DL-073 (b), (c), (e) (not tested, DL-153).
Chosen:          none   Default from: plan estimator stays
Test:            tests/test_d8_candidates.py (15); fast suite 442 passed, 7 deselected, 1 xfailed.
Status:          done; STOP. 7h blocked until the owner rules. D8 open; O1 to O16, O4/O5, reachability, G6 reading, A_ref reading and the RB6 statistic (DL-154) for the 7h sign-off.
Commit/tag:      the commit that adds this entry; no tag

## DL-156  MS7 7h: owner rulings D8 = A for MS7, Q3, SW; draft criteria file and sign-off sheet written; nothing ruled, nothing frozen    [ID: D8, D35, D43, A4, A7, RB3, RB6, G5, G6, G7, F-6, F-16 to F-26, O1 to O16, DL-137, DL-140, DL-147, DL-152, DL-154, DL-155]
Date:            2026-10-17        Author:
Decision:        Owner rulings entered as given. (1) D8 for MS7 is option A: the plan estimator (PlanD8Estimator, 10 cycles, 2 SE) stays the default, the strict xfail stays, the D8 wording, the fit start and the 2-SE rule are not changed, and its documented failures (DL-137, DL-140, DL-147, DL-155) are written as a known limitation in the criteria draft (classifier.d8_estimator.known_limitation). D8 goes into the sign-off sheet as a choice between A and B, with the DL-155 data; for B the rows (zero-pad edge treatment with the AR(1) SE, and with the per-cycle SE, each with no shift and a 40 ms shift, no minimum window) were read from the saved 54-candidate csv files, with every F1, F2, F3, stored-limit-cycle, A8 ring and white-noise item; no new run. (2) Q3 (DL-155: fast-damped rings are already NS by the cycle count, so a D8 fit may not be the right gate) is a plan question on the sheet; not acted on. (3) The short-window false-surge finding (306 of 500 white-noise records non-NS at W = 0.2 s; from the power tests and the 10-cycle rule, not D8) is on the sheet with O4 and O5 (row SW).
  Written: configs/robustness_criteria.yaml (draft, not frozen; every leaf labelled logged, UNVERIFIED or open, with its source and the sheet row; Table 7.2 RB1 to RB10, G5 to G7, classifier defaults, A_ref 2.176222 and its source hashes, F-10, F-11, F-13, F-14, F-15 as in DL-152, the cell lists as in DL-141 and DL-143, the RB6 statistic of DL-154; O1 to O16, F-6 and the post-surge rate are open and not implemented); docs/ms7_signoff.md (one row per item needing a ruling: D8 with the option-B data, Q3, X-1, SW, O1 to O16, H-1 A_ref reading, F-7, RHO, REACH, G6, RB6, F-26, F-12, F-9, F-8, F-2, F-10 to F-15, F-27, F-28, S3S4, F-16 to F-25, U-1 to U-7, H-2 to H-4, K5, K10, K4-net, Defender, backup, 24 h cap, /permissions, tag mechanics); tests/test_criteria_draft.py (11 tests: draft flags, every Table 7.2 row and gate present, every leaf labelled, open values hold no number, plan numbers unchanged, agreement with configs/S13.yaml and base.yaml, no config points at the draft).
  Findings on the way: (a) the plan's 7h row says to repoint robustness.criteria_file in configs/A4.yaml and S5.yaml; run_a4 reads the K tolerances from that file (analysis/hopf.py), so repointing A4 would break it, and S5.yaml has no such key (it inherits null from base.yaml); not repointed, row H-2. (b) DL-147 gives 24 of 500 non-NS at W = 1.054 s on white noise (sd 0.04), the D8 study (DL-155) gives 26 and says it reproduced DL-147; all other windows agree; unresolved, row U-7, no re-run. (c) No loader in config.py, no docs/robustness_criteria.md (rows H-3, H-4).
  Not done, by instruction: no freeze SHA-256, no tag, no S2 re-run, no M3 ramp-study run, no F-6 broadband flag, no post-surge rate, no ruling on any sheet item; the 7e records and the 7f, 7g and 7g2 outputs were read, not changed; the plan is not edited; no D-item changed.
Reason:          instruction of the project owner; ms7_plan.md 7h row.
Options:         -
Chosen:          as above   Default from: owner rulings; plan values where logged
Test:            tests/test_criteria_draft.py (11); fast suite 453 passed, 7 deselected, 1 xfailed (442 + 11).
Status:          7h draft done; STOP for the owner's rulings on docs/ms7_signoff.md. 7i and 7j not started.
Commit/tag:      the commit that adds this entry; no tag
