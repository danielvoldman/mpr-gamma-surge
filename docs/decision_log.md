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
