# MS11 sub-step plan (planning, scripts and timing only; no ruling yet, questions open)

**Status (11a, DL-330 to DL-334): planned. Nothing run except the timing samples (section 9, labelled TIMING SAMPLES, in no pre-registered run list); no MS11 family launched; no list written.** Written for the reviewer who rules the M11 list below. Binding source: `docs/plan.md` (Table 11.1 row MS11; Table 6.2 S11, S12 (context), S13; 6.2; 6.4; Table 7.2 RB1 to RB10; the A11 evaluation paragraph under Table 7.2; D24, D35, D36, D43; Table 9.1; 9.2; 9.3; Table 2.1). Decisions go in `docs/decision_log.md`; this plan is DL-331 (pre-checks, plan quantities, status inventory, carry-in notes), R33 is DL-330, the open choices and run counts are DL-332, the proposed seed keys DL-333, the timing result and launch-rule application DL-334; it holds no decision of its own. It changes nothing in the plan and nothing in a frozen file, and it reopens no earlier ruling (the 41 D-items at defaults, the `src/mprsurge/` layout, MS0 to MS15, models M2/M3/M4/M3a/M3b, the surge classes, paths P1 to P5, controls NC1 to NC3, R1 to R33, DL-210 to DL-329, the MS7 and MS8 rulings, the claim limits G4-C1 to G4-C6, the G7 limits of DL-229 and DL-230, G6-D1 to G6-D3 and the MS9 limits). Open housekeeping is untouched: K5, K10, K4-net coupling, D37.

**Opening note, ruling R33 (DL-330), quoted exactly as ruled:**

> R33: The MS10 close is accepted with its stated limits: the independent check shares the frozen classifier, the criteria loader and the 9i function with the original evaluation; the D36 figure 14.21 h is a sum on mixed bases (UNVERIFIED); disk free is 153 GB while the 10e log recorded 81.4 GB, now explained (the user deleted a video game), so free space is still measured before every launch; D37 stays open to MS15.

**MS11 row (Table 11.1):** "Noise and numerics: S11, rest of S13, A11". Done when: "Every RB check except the RB8 M4/adaptation parts (MS12) has a result". Unlocks: "MS12 (only via G2 or G3); MS13". Depends on MS10 (closed on paper, R30 to R33, DL-329, `docs/ms10_close.md`). The plan names no tag for MS11.

## 1. Pre-checks at 11a (all pass)

| Check | Result |
|---|---|
| `docs/ms11_plan.md` from an earlier attempt | did not exist: 11a had not been run before; `docs/ms10_plan.md` read for the layout |
| Criteria-loader gate against tag `criteria-frozen` (dd8330c5eaacd63d21e7b7969430988d00862769) | PASS (`verify_frozen_criteria()` returned the tag, the commit and all four hashes) |
| Criteria file SHA-256 (LF text) | PASS c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05 |
| `configs/S13.yaml` | PASS 317db87e69afcb09111a33e78640869b3f588e64390d110655aaa3a7cff52388 |
| `configs/A4_grids.yaml` | PASS cf6a60bec781c6f7e53b7f92b747ff745fcc5dc4794c0b83768e0aa4a4e56401 |
| `configs/S5_cells.yaml` | PASS fe8590ce81bc8c537f9c92e2afbee80685aaaa52c757474912b243fe9ed38790 |
| Working tree clean; HEAD a83a6ee or a descendant | PASS (clean; HEAD = a83a6ee7eade23c2179346dfe15842af2858eb2c) |
| `docs/ms10_close.md` | PASS 29b2cab8be79804c847908a0bbb0482ede1bde2f23a698ae42e59f957f2e2517 (the prompt wrote "29bb..." for the first characters: a typo; the value 29b2cab8... given in the prompt was used, as the prompt allowed) |
| `docs/ms10_g_evidence.md` | PASS 8ffc2858e70c0e2288ac13554f2dc8412b6194ea559765cfb454d41a731b45c4 |
| `docs/ms10_file_hashes.csv` | PASS 053c63916ab536a5a3672dd6c1a5c7797a79fa20e2b419840c1d94019949ca10 |
| `docs/ms10_results.md` | PASS 55a7d1af44bee7f390e0705388dd503f0e2112e9f8f12c7f88450cc512e4a98b |
| 10f result-file table digest | PASS d1b98f05b1b147437ed19ef3dc4ee84c1dda61693c9e9cc3a9de41f4ba572a52 (321 files, every file hashes to its listed value, 0 mismatches) |

Test baseline before any 11a change: fast suite 783 passed, 11 deselected, 9 xfailed (as stated in the 11a prompt).

## 2. Plan quantities quoted (section references; quoted from `docs/plan.md`, nothing paraphrased)

Where a value is not in the plan, the text below says UNVERIFIED.

### 2.1 Table 11.1, MS11 row (section 11)

> | **\#** | **Milestone and deliverables** | **Done when** | **Unlocks** |
> | --- | --- | --- | --- |
> | MS11 | Noise and numerics: S11, rest of S13, A11 | Every RB check except the RB8 M4/adaptation parts (MS12) has a result | MS12 (only via G2 or G3); MS13 |
>
> *Table 11.1. Milestones in build order (renamed MS0–MS15 in v0.4 so that milestone IDs do not collide with the model IDs M2–M4).*

### 2.2 Table 6.2, rows S11, S12 (context only) and S13 (section 6.5)

> | **ID** | **Purpose** | **Model** | **What varies** | **Feeds** |
> | --- | --- | --- | --- | --- |
> | S11 | Noise level | M3 MF (N) | σ {0.5, 1, 2} × T_ramp {10, 30, 120, 300} s × 10 seeds | F4, FS3 |
> | S12 | Negative controls | M3 MF; network for NC1 | NC1–NC3 × 13 T_ramp; NC1 at 5 map cells; NC1 network 1 seed, 120 s | A10; F6 |
> | S13 | Numerical checks | M3 MF and network | Mean field, P2 at ref_devalle, T_ramp 10, 120 (headline) and 316 s: DOP853 vs Radau; rtol {10⁻⁸, 10⁻¹⁰, 10⁻¹²}; δ₀ {10⁻⁹, 10⁻⁶, 10⁻³}; D43 floor levels. Network, 10 s ramp: dt {10⁻³, 5×10⁻⁴, 2.5×10⁻⁴, 10⁻⁴}; V_p ±100 vs ±200, the ±200 check also at dt 10⁻⁴. Window × {0.5, 2}. The D43 floor runs use stochastic Heun on a dt ladder from the mode-N default 10⁻³ τ (lower rungs UNVERIFIED; set in configs/S13.yaml before MS7). The headline subset (rtol ladder, Radau, δ₀ ladder, and the floor with its Heun dt ladder at 120 s) runs at MS8 (CP23) | FS4 |
>
> *Table 6.2. Runs; outputs go to results/\<ID\>/. Ramp-rate sweeps over orders of magnitude with a quasi-static limit follow R1 and R5; finite-size values follow R5's figure plan. Grid resolution is \[needs decision\]: accept if halving the spacing near the map boundary moves it by less than one cell.*

No run duration, path, profile or drive is stated in the S11 row; the plan states the path of S13 ("P2 at ref_devalle"). The S11 path is open choice M11-1 (UNVERIFIED reading: the headline example, D40).

### 2.3 Section 6.2 (mean field), the four bullets S13 and S11 rest on

> - **Mode D:** solve_ivp DOP853, rtol 10⁻¹⁰, atol 10⁻¹², max_step 0.05 τ (0.5 ms), output every 0.1 τ (1 ms); Radau cross-check. Basis: Taher used Dormand–Prince at 10⁻¹²; R5 suggests explicit adaptive plus implicit cross-check \[R5\] \[needs decision; test S13\].
>
> - **Initial state:** exact stable fixed point at the start parameters; δ₀ = 10⁻⁶ is added on v at t_on, not at t = 0, where it would decay to the solver floor during the 5 s baseline \[needs decision; D26; CP16\]. The ramp's derivative kink at t_on also seeds the onset \[reasoned, not tested\]. S13 repeats with 10⁻⁹ and 10⁻³ because slow-passage onset depends on the starting state \[R1; R5\] \[verified that it does\].
>
> - **Mode N:** stochastic Heun, step 10⁻³ τ (0.01 ms), Numba, as Segneri did for the noisy neural mass \[R5\] \[single source\]. The D43 noise-floor runs of A7 also use this scheme, and RB6 varies its step (S13; CP25).
>
> - **Durations:** mode D: 5 s baseline, the ramp, then a 10 s hold that starts after the last ramp ends: after T_ramp, or after 1.25 T_ramp on P2 and the paths built on it (P3, P4a, P4b, NC2), when J reaches 0 (CP14). Mode N and network: 2 s discarded before t = 0, so the baseline stays 5 s (CP14). P5 doubles T_ramp. The headline P2 run (T_ramp 120 s) lasts 165 s = 16,500 τ. Corpus discards were 1–10 s \[R5\] \[needs decision\].

### 2.4 Section 6.4 (noise models)

> ## 6.4 Noise models
>
> - **None** (mode D) for bifurcation-linked analysis.
>
> <!-- -->
>
> - **Additive white noise on v** in the mean field, stated as phenomenological as Segneri did \[R5; R1\] \[verified\]. σ is calibrated at MS5, after A4 gives η̄\_H, so the baseline std of v matches one N = 10⁴ network baseline run at the P2 start state of ref_devalle (η̄\_H − 1.5, J = −21, Δ = 0.3, τ_d = 5 ms); σ is stored in a committed config and frozen with the criteria at MS7, and S8 checks it (CP21); also 0.5σ and 2σ \[needs decision\].
>
> <!-- -->
>
> - **Finite-size fluctuations** in network runs (S8, S9).
>
> <!-- -->
>
> - **Not implemented:** Cauchy noise and higher-order Gaussian reductions (equations absent, 3.5).

### 2.5 Table 7.2, rows RB2, RB3, RB5, RB6, RB9, RB10 (section 7.2)

> | **ID** | **Check** | **What is varied (runs)** | **Pass / fail criterion (fixed before S5)** | **Where** |
> | --- | --- | --- | --- | --- |
> | RB2 | Noise | σ × 0.5, 1, 2; 10 seeds; 4 T_ramp (S11); noisy subgrid (S7) | Headline surge class kept in ≥ 8/10 seeds at 0.5σ and σ; subgrid agreement ≥ 90% (D24). Noise is stated as phenomenological \[R5, SQ2\] | Main F4, F5; FS3 |
> | RB3 | Ramp rate | 13 T_ramp values, 1–1000 s; P1, P2, P5; linear vs sigmoid (S5); D43 floor levels, stochastic Heun (S13) | \(a\) Judged only on the runs inside the RB3(a) range, where δ₀·exp(∫ Re λ dt′) stays above the solver or noise floor until the predicted onset (A4 computes the range; section 5.2, A7): the threshold-crossing onset matches t_pred, the A4 entry–exit prediction along the path, within one A4 η̄ grid step; runs outside the range are reported, not judged \[reasoned, not tested\]. (b) With the D43 noise floor (stochastic Heun), the delay shrinks as the floor rises \[reasoned, not tested; RA, Key finding 4, reports only that noise removes the delay (single source: RA, introduction depth)\]; no scaling law is entered (UNVERIFIED). (c) Class holds at 56, 100, 178 and 316 s, the grid points around the 1–5 min ramp \[R3, §6\]. (d) Profile changes class at ≤ 1 of these; profile effects on the delay are reported as slow-passage physics (section 4.4) | Main F4 \[R5, recommendations\] |
> | RB5 | Initial conditions | δ₀ of 10⁻⁹, 10⁻⁶, 10⁻³ applied at t_on (S13); start distance 0.5, 1.5, 3 (S5); up vs down ramps (P5, S4) | Class unchanged. Delay shifts are the expected memory effect and are reported \[R1, §2.5; R5, SQ4\] | Main F4; FS4 |
> | RB6 | Numerical convergence | rtol 10⁻⁸–10⁻¹² and DOP853 vs Radau (noise-free runs); Heun dt ladder (D43-floored runs); network dt from 10⁻³ to 10⁻⁴ τ; V_p ±100 vs ±200 (S13) | With the D43 floor (stochastic Heun), the headline delay changes \< 5% between the default step 10⁻³ τ and the finest rung of the Heun dt ladder (lower rungs UNVERIFIED; set before MS7); for noise-free DOP853 runs the delay is reported against rtol (10⁻¹⁰ vs 10⁻¹²), not used as a pass test; solvers agree on class with onset within 1 ms; halving dt changes f_pk \< 2% | FS4 \[R5, (c); R7, §2.6\] |
> | RB9 | Frequency mapping | \(a\) Dimensional vs nondimensional runs; (b) spectral vs cycle frequency; (c) bands 25–100 vs 30–120 Hz; (d) τ ± 20% | \(a\) within 0.5%; (b) within 1/W; (c) ≤ 5% of cells change class; (d) reported only, since every gamma result the reports cite fixes τ = 10 ms \[R1, §2.4; R5\] | FS5; F3 |
> | RB10 | Surge-definition sensitivity | A8 band, factors, A_min, window, minimum cycles 5 and 20 | Headline class unchanged under each change; ≤ 10% of map cells change class | FS5 |
>
> *Table 7.2. Robustness checks. Thresholds: D35 \[needs decision\]. The perturbation box and the T_ramp bracket are \[reasoned, not tested\].*

RB1, RB4, RB7 and RB8 are quoted in `docs/ms10_plan.md` (RB1, RB8) and `docs/ms9_plan.md` (RB4, RB7) and are not restated here; their status is in section 4.1.

### 2.6 The A11 evaluation paragraph (section 7.2; the plan has no separate A11 section)

> **Main text versus appendix.** Main text: RB1, RB2 (noise robustness, a main result from v0.4: the noise band on F4 and the noisy-subgrid agreement on F5), RB3, RB5 and RB7, and RB4 as a single sentence. Appendix: RB6, RB8, RB9 and RB10. This follows R5, which places ramp-rate and quasi-static results in the main text and numerics in the appendix \[R5, recommendations\], and RA, which recommends noise robustness as a main result \[RA, Recommendations\]. Failure regimes get equal weight \[R7, §2.7\]. The Hopf location (A4) and the A7 entry–exit delay prediction, checked against S4 and S8, supply the analytic-versus-network result R6 asks for \[R6, §6 rec. 4\].
>
> **Evaluation.** Step A11 (scripts/run_A11.py) reads the frozen criteria and writes results/A11/a11_robustness.csv: value, threshold, pass or fail, and the input commits. Failed checks are reported, not dropped, because MNA bars hiding known issues \[R6, §2.1; R7, §2.7\] \[verified\].

The only other plan mention of A11 is the Table 9.1 row "Analysis and reclassification (A8–A11, RB10)": "stored series only; no re-simulation", "measured in the timing gate". The plan gives no module name beyond `scripts/run_A11.py` and no column list beyond "value, threshold, pass or fail, and the input commits".

### 2.7 D24, D35, D36 and D43 (Appendix C, Table C.1; Appendix B)

> Table C.1 rows:
>
> | DL-024 / D24 | Noisy/deterministic agreement | ≥ 90% of subgrid cells | RB2 |
> | DL-035 / D35 | Robustness and gate thresholds | Table 7.2; G5: 3% of cells, 80% LHS | Frozen at MS7; changes logged |
> | DL-036 / D36 | Compute cap and cut order | 24 h wall-clock (S1–S13, S16); cut order of section 9.3 | Timing gate |
> | DL-049 / D43 | Slow-passage noise floor (A7) | A small additive noise floor on v for the A7 delay test, integrated with stochastic Heun, at levels set at MS7 (before criteria-frozen; Conventions); no scaling law entered (UNVERIFIED) | RB3(b) and RB6 results; a primary-source scaling law |
>
> Appendix B rows:
>
> | noise floor (A7) | noise.floor_levels | set at MS7, before criteria-frozen (Conventions) | — | — | \[needs decision\]; run with stochastic Heun; no scaling law entered (UNVERIFIED) | D43 |
> | budget | budget.max_wall_h | 24 | — | h | this plan | D36 |
>
> Section 7 (convention, D35):
>
> The Table 7.1 tolerances go into configs/replication.yaml and are frozen at the end of MS1, before the MS2 replication runs, under the tag tolerances-frozen (D34). The Table 7.2 thresholds go into configs/robustness_criteria.yaml and are frozen at MS7, under the tag criteria-frozen (D35), before any M3 ramp-study run (S5 onward; the short S5 baseline-only runs at MS7 have no ramp). Any later change needs a decision-log entry and must be reported in the paper.

### 2.8 Table 9.1 (section 9)

> | **Stage** | **Work** | **Wall time (6 workers)** | **Memory** | **Basis** |
> | --- | --- | --- | --- | --- |
> | One mean-field P2 ramp, T_ramp 120 s (165 s = 16,500 τ; CP14) | ≥ 3.3×10⁵ steps | 33–99 s per run (one core) | \< 100 MB | est.; R5 gives \< 1–5 s per 10⁴ τ without a max_step limit (R5 est.) |
> | S1–S4, A1–A6 (validation, continuation) | ~100 short runs; A6 from continuation (no brute-force grid) | \< 30 min; plus a few minutes for Julia's first compile | \< 1 GB | est.; R5 est. |
> | S2, S5, S6 (ramp sweeps) | 7×10⁷ mean-field steps; 3.1×10⁹ Heun steps | 19–57 min | \< 1 GB | est. |
> | S5 baseline-only mode-N runs at MS7 (headline and 900 + 325 map cells × 10 seeds × 7 s; MC-01, v0.5) | 8.6×10⁹ Heun steps | 0.5–1.2 min | small | est. \[reasoned, not tested\] |
> | S7 map 1 (900 cells × 120 s) | 3.0×10⁸ steps | 1.4–4.1 h | \< 2 GB | est.; R5 est. is 30–60 min for 10⁴ runs of 1 s |
> | S7 map 2 (25 × 13) and noisy subgrid (225 × 10 seeds) | 1.5×10⁸ steps; 3.8×10¹⁰ Heun steps | 0.7–2.2 h | \< 2 GB | est. |
> | S8, S10, S12 networks, K8 at N = 5×10⁴ and the σ baseline (MS5) | ~2.0×10¹² neuron-updates | \< 30 min | \< 500 MB per run | R5 rate |
> | S9 finite size (4 N × 10 seeds) | 4.0×10¹² updates | 11–23 min at the stated rate; allowance 2 h | \< 2 GB | est.; R5 est. 1–2 h |
> | S11, S12 mean field, S16 | small | \< 40 min | small | est. |
> | S13 numerics (scope: P2 at 10, 120 and 316 s; Radau 3–10× slower; network dt ladder ×17 on the 10 s ramp) | — | \< 1 h | \< 1 GB | est. |
> | Spectrograms (10⁶ samples per run) | — | \< 1 s per run | \< 200 MB | R5 est. |
> | Analysis and reclassification (A8–A11, RB10) | stored series only; no re-simulation | measured in the timing gate | — | v0.4 |
> | **Total, S1–S13 and S16** |  | about 3–12 h (the row ranges sum to 2.6–11.9 h, including the MS7 baseline-only runs: the lower bound with S9 at its computed 11 min, the upper bound with S9 at its 2 h allowance; analysis timed separately); cap 24 h (D36) | \< 3 GB of 16 GB |  |
>
> *Table 9.1. Compute budget on the Ryzen 5 5600 (16 GB, Windows 11, CPU only). Scaling: mean field is linear in simulated time; networks scale as N·T/dt; continuation scales weakly with dimension (R5 est.). S14 and S15 are unknown until their equations are fixed: S14 by D42, S15 by the Gast publisher PDF (section 7.3).*

### 2.9 Section 9.2 (launch rule) and 9.3 (cut order)

> ## 9.2 Feasibility gate
>
> 1.  **Time the expensive cells.** After MS1, run python scripts\time_one_run.py --config configs\S5.yaml --cell headline --repeat 3, then the same for each timing cell: the headline (P2, ref_devalle, 120 s); Δ = 0.01 near the Hopf window; Δ = 0.6; P5 at T_ramp 1000 s; Radau at rtol 10⁻¹²; and one mode-N run. Until A4 exists, the η̄ path is provisional and recorded as such; the headline is re-timed after A4 (MS5). Results go to results/timing/. Repeat for the network at N = 10⁴ and 3×10⁴ once that code exists, and time 6, 8 and 10 workers.
>
> <!-- -->
>
> 1.  **Extrapolate.** Mean field: Σ τ simulated × measured s/τ ÷ workers. Network: Σ N·T/dt × s/update ÷ workers. Each run family is extrapolated from its matching timing cell, not from the headline alone. The script prints a predicted wall time for each S-ID and the total.
>
> <!-- -->
>
> 1.  **Launch only if** the prediction is ≤ 1.5 × the Table 9.1 allowance and the total stays within the D36 cap. Otherwise apply the cut order. Log both the measurement and the decision.
>
> <!-- -->
>
> 1.  **Re-time** after any change to the solver, the Numba kernel or package versions.

> ## 9.3 Cut order
>
> Apply cuts in this order until the prediction fits:
>
> 1.  Run Radau only at the headline T_ramp.
>
> <!-- -->
>
> 1.  Drop network dt = 10⁻⁴ τ unless 2.5×10⁻⁴ τ fails RB6.
>
> <!-- -->
>
> 1.  Cut S9 to 5 seeds.
>
> <!-- -->
>
> 1.  Run the sigmoid profile for P2 only.
>
> <!-- -->
>
> 1.  Drop the 562 s and 1000 s ramps from P5 and from the start-distance runs.
>
> <!-- -->
>
> 1.  Shrink map 1 to 20 × 20, with boundary refinement (D31).
>
> <!-- -->
>
> 1.  Shrink map 2 to 13 × 13.
>
> <!-- -->
>
> 1.  Raise max_step to 0.1 τ, only if RB6 shows \< 1% change at the headline point.
>
> Never cut: the G0 replication runs, NC1, the S8 headline overlay, the S13 headline tolerance check, the A8 tests and the one-at-a-time part of S16.

### 2.10 Table 2.1 (section 2.3; the class definition RB2 uses)

> | **Element** | **Definition and default** | **Basis and status** |
> | --- | --- | --- |
> | Signal | Primary v(t); secondary r(t). Network: mean V_j over non-refractory neurons and binned spike rate. Sampled at 1 kHz. | v is less affected by finite-size fluctuations (Devalle) and is Segneri's spectral readout \[R5\] \[single source\]. 1 kHz = rat EEG rate \[R4\] \[needs decision\] |
> | Gamma band G | 25–100 Hz; also Xu γ1 25–55 Hz and γ2 80–150 Hz; peak frequency | Band edges conflict (handoff g, C1) \[needs decision\]. Test: rerun A9 with 30–120 Hz; if \> 5% of map cells change class, report both |
> | Relative power | ρ = P_G/P_total, total 1–150 Hz, linear detrend per window (reported). The surge test uses P_G/P_non-G, with P_non-G = P_total − P_G, which, unlike ρ ≤ 1, is not bounded (CP18) | 150 Hz = top of Xu γ2 \[R4\] \[needs decision\] |
> | Time–frequency | Hann spectrogram of v; W = 2 s, step 1 s if T_ramp ≥ 60 s; else W = max(0.2 s, T_ramp/30), step W/2 | Xu used 2 s epochs, 1 s overlap \[R4\]; no corpus spectrogram of a transient \[R5\] \[needs decision\]; test W × 0.5, × 2 |
> | Baseline | Last 5 s before ramp onset (t = 0 to t_on); mode N and network runs discard 2 s before t = 0, so the baseline is 5 s in every mode (CP14) | \[needs decision\] |
> | Threshold, noisy runs (mode N) | Relative surge: P_G/P_non-G ≥ 2 × its baseline value. Absolute surge: P_G ≥ 2 × baseline P_G. A8 reports baseline ρ for the headline and every map cell before the MS7 freeze, from short baseline-only mode-N runs at MS7 (counted under S5; Table 6.2) | 2 = lower end of Xu's 2–391-fold range \[R4\] \[needs decision\]; test 1.5 and 4. A ρ ratio cannot reach 2 when baseline ρ ≥ 0.5, and a flat 1–150 Hz spectrum gives ρ ≈ 0.50 \[reasoned, not tested\] |
> | Threshold, deterministic runs (mode D) | A deterministic run at a stable fixed point has no gamma power, so the power ratios and the mode-N classes are undefined. Episode while the Hilbert envelope of band-passed v ≥ 0.1 × A_ref, where A_ref is the limit-cycle amplitude of v at ref_devalle (A5), used as one fixed absolute threshold for every cell and path (D7) | Zero-baseline problem \[reasoned, not tested\]; factor \[needs decision\]; test 0.05 and 0.2; one fixed threshold from v0.4 (CP18) |
> | Minimum duration | ≥ 10 consecutive cycles at the running peak frequency; merge gaps shorter than one window. Damped versus non-damped (D8): the growth rate of the Hilbert envelope is fitted from the threshold crossing over the first 10 cycles; the run counts as damped only if the fitted rate is negative by more than 2 standard errors of the fit, and is otherwise non-damped. "Sustained" is kept for the non-terminating classes (S-sus, D-sus) | A cycle count alone does not separate a slowly damped ring: cycles per e-fold ≈ πr\*²/Δ (section 3.1), above 10 at small Δ \[reasoned, not tested\]; ring length scales with r\*²/Δ \[R1, §2.5\]; far shorter than observed episodes of seconds \[R4\] \[needs decision\] |
> | Ordering | Episode ends before the run ends. On P2-based paths the oscillation stops where the path leaves the oscillatory region, at J_exit,static \< 0 (from A4); the observed episode ends at J_exit,run (from the classifier), which can lie beyond it under delayed exit; as J → 0⁻ the rate rises (disinhibition), so this ordering is imposed by design, not evidence of suppression \[reasoned, not tested\]. Collapse marker: r \< 10% of baseline (paths without a J ramp) | Hypoxia → surge → suppression → terminal SD \[R3; R4\] \[verified\]; marker \[needs decision\] (D9; CP19) |
> | Classes | Mode N: S+ (absolute and relative, transient); S-rel (relative only); S-abs (absolute only; flagged "broadband" when the rise is not a band-limited peak, with no new threshold); S-sus (no termination, either power test); NS (none). Mode D: D-tr (transient episode); D-sus (sustained, no termination); D-none (no episode). A "surge class" is D-tr in mode D, or S+, S-rel or S-abs in mode N. Noisy and deterministic runs agree when D-tr meets a surge class, D-sus meets S-sus, and D-none meets NS | A relative-only rise is consistent with the rat relative-power framing and with the single case after arrest \[reasoned, not tested; R2, §3\]; before arrest the single case also showed an absolute gamma rise \[R4, §2.3\]. Classes revised in v0.4 (CP18); S-abs flag added in v0.5 (CP26) |
> | Metrics | Onset time; η̄ at onset; delay η̄\_on − η̄\_H; duration (ms, cycles, fraction of ramp); peak absolute and relative power; peak frequency; class; on P2-based paths, J_exit,run (where the classifier ends the episode; the reported J_exit metric), J_exit,static (where the path leaves the A4 oscillatory region; the reference), their difference (the exit delay), and the post-surge rate, measured after J_exit,run | R1 recommendations; R5 figure plan |
>
> *Table 2.1. Surge definition implemented in mprsurge.analysis.surge_metrics. Limitations: the classifier is power-based, so coherence-only surges, such as frontal coherence without a power increase in 15/16 rats (Lee 2017) \[R4, §2.2\], cannot register, and model NS is not the same as "no surge" in those preparations. Borjigin's early high-gamma component near 130 Hz lies outside 25–100 and 30–120 Hz and is covered only by γ2 (80–150 Hz) \[R4, §2.2, §8(d)\].*

## 3. State at the start of MS11

| Item | State |
|---|---|
| Freeze | Annotated tag `criteria-frozen` (commit dd8330c5eaacd63d21e7b7969430988d00862769), local only; all four hashes verified at 11a (section 1). No frozen file changes at 11a. |
| MS10 close | `docs/ms10_close.md` SHA-256 29b2cab8...; verdicts carried: sigma check NOT INSIDE (limitation), RB1 FAIL, RB8 heterogeneity part NOT EVALUABLE, G4 triggered by consequence (2) and report-only for the run order; claim limits G4-C1 to G4-C6 (R31, DL-325); R32 no diagnostic run; R33 (DL-330). |
| Earlier closes | MS9 (`docs/ms9_close.md`): G5 continue, G7 NOT PASSED with DL-229 limits, G3 NOT TRIGGERED, RB4 PASS, RB2 / D24 FAILED (P-1 post hoc), D31 PASS. MS8 (`docs/ms8_close.md`): G6 PASSED WITH DEPARTURES, G6-D1 to G6-D3. |
| Machine | Ryzen 5 5600, 16 GB, Windows 11, CPU only; Python 3.11 in `.venv`; disk free 153 GB at MS10 close (R33); free space is measured before every launch. |
| Code that exists for MS11 | Mean-field kinds `mf` (DOP853, Radau) and `mf_noisy` (stochastic Heun, `noise.sigma_factor`, `noise.dt_tau`, coupled increments) and the network kind (`network.dt_tau`, `V_peak`, `V_reset`) are in the runner. No `scripts/run_A11.py`, no `ms11_*` evaluator, no S11 or S13-remainder run list. `analysis/a8_sensitivity.py` holds the A8 variants (band, factors, A_min, window, cycles) for stored arrays. |

## 4. RB and S13 status inventory (from the stored records and the decision log)

Status words: **done** (a result exists and is logged), **partial**, **open at MS11**, **UNVERIFIED** (cannot be confirmed from the records). Verdicts are quoted as logged; nothing is re-evaluated at 11a.

### 4.1 RB1 to RB10

| ID | Status | Result and references |
|---|---|---|
| RB1 | **done (FAIL)** | MS10. Headline 10 s FAIL (0 of 3), 120 s FAIL (0 of 3), cells 1 of 4 FAIL (need 3), N rule PASS; overall FAIL, which is G4 (DL-319, DL-320, DL-323, R30; `docs/ms10_results.md`, `results/ms10/eval/`). Nothing open at MS11 except its row in A11. |
| RB2 | **partial** | Subgrid part (D24): FAILED, 97 of 225 cells (43.1%) on raw classes, 118 of 225 (52.4%) on the three categories, 203 needed (DL-242); P-1 post hoc 173 of 225 (DL-255, DL-257); control S12x/M9-22 shows S-rel in 1,095 of 2,250 runs without a ramp (DL-248, DL-250). **S11 part open at MS11**: "Headline surge class kept in ≥ 8/10 seeds at 0.5σ and σ" has no S11 run; no S11 list exists (the 9a figure for S11 is a 27 s prediction, DL-211). The S5 mode-N P2 noise runs (130 runs, σ × 1, 13 T_ramp, key [8, 1, s], DL-175) are not an RB2 evaluation: their T_ramp grid has no 30, 120 or 300 s (UNVERIFIED whether any of them can stand in for an S11 cell). DL-251 (control at the headline cell for each sigma) is carried in. |
| RB3 | **done** (MS8) | (a) not judged at the headline (frozen departure); 0 of 6 testable in-range runs within one A4 step (G6-D1; DL-188, DL-208). (b) MEETS under the raw first crossing, DOES NOT MEET under the classifier onset (G6-D3). (c) D-tr at all four T_ramp, reading C holds. (d) P1 2 changes, P2 0, P5 0. The D43 floor runs at 120 s are the S13 floor part (DL-178). Nothing open except the A11 row. |
| RB4 | **done (PASS)** | MS9: 0 of 14 one-at-a-time changes, 64 of 64 hypercube unchanged (DL-235). |
| RB5 | **partial** | Headline δ₀ ladder done: D-tr at 1e-9, 1e-6, 1e-3, delay shift 0.0 at the 1 kHz output (DL-183). Start distance (S5, P1): class changes at 9 of 13 T_ramp; the headline path is D-tr at 0.5, 1.5 and 3 (DL-183, DL-195 supplementary). Up/down: P5 (S5, MS8) done; the S4 up/down quasi-static part was an MS6 product and is not restated as an RB5 result in the MS8 close (UNVERIFIED). **Open at MS11**: δ₀ at T_ramp 10 and 316 s (S13 remainder). Plan: "Class unchanged. Delay shifts … are reported"; G6 reports, does not gate. |
| RB6 | **partial** | Done at 120 s (MS8): rtol 1e-8, 1e-10, 1e-12 identical onset 58.698 s, reported not a pass test; Heun default against finest rung, relative change 0 at all three floor levels, 30 of 30 seed pairs identical, a limit of the 1 ms output grid (DL-184, DL-190); DOP853 against Radau: classes agree, onset 58.698 s against 58.879 s, 181 ms against the 1 ms bound, DOES NOT MEET, cause unexplained (DL-184, DL-189; G6-D2). **Open at MS11**: the network part (network dt from 1e-3 to 1e-4 τ; halving dt changes f_pk < 2%; V_p ±100 against ±200); the mean-field parts at T_ramp 10 and 316 s. G4-C6: the RB6 rerun named in G4 is read as the network part of S13 (UNVERIFIED reading). |
| RB7 | **done** (MS9) | NC1 mean field D-none at 18 of 18; NC2 D-tr at 13 of 13; NC3 D-none at 13 of 13; G7 NOT PASSED because the NC1 network run is S+ (DL-228, DL-229, DL-230). Per-path claims are a paper task. Nothing open except the A11 row. |
| RB8 | **partial; M4/adaptation parts belong to MS12** | Heterogeneity part NOT EVALUABLE (Lorentzian S-sus, S-abs, S-sus have no common level; Gaussian S-abs ×3 and uniform S-abs ×3 reported; DL-322, G4-C5). M4 criteria: open, "written before M4 runs" (F-23; D42 open); G2 does not trigger (DL-133, as written in the frozen file); G3 NOT TRIGGERED (DL-261). So the MS11 done-when excludes these parts by its own wording. |
| RB9 | **open** (one partial) | (a) A unit-level check exists: `tests/test_units.py::test_rb9a_...` compares a dimensional and a non-dimensional M3 run at τ = 10 and 20 ms on a short `path_eta` ramp, tolerance 0.5% (DL-061); it is not a run on the headline path and is not logged as an RB9 result (UNVERIFIED whether it counts). (b), (c) and (d): no result. The A8 pre-freeze sensitivity (DL-146, DL-147) ran the 30–120 Hz band on synthetic, baseline-only and S3/S4 records, not on ramp or map records; the frozen file says the map-cell tests are for A11 after the freeze (`rb9`, `rb10` leaves; `s3s4_sensitivity`). |
| RB10 | **open** | Variants (band 30–120, factors 1.5 and 4, A_min 0.05 and 0.2, window ×0.5 and ×2, minimum cycles 5 and 20) have been run only on synthetic, baseline-only and S3/S4 records (DL-146, DL-147) and post hoc on the NC1 network record (DL-226); not on the headline run or on map cells. The frozen file states that the real RB10 "is evaluated by A11 on ramp records". |

### 4.2 S13 sub-families (Table 6.2 S13) and S11

| Part | Ran at MS8 (headline subset, 125 runs, 26.3 min, DL-178; CP23) | Remains at MS11 |
|---|---|---|
| Mean field, rtol ladder {1e-8, 1e-10, 1e-12} | T_ramp 120 s: 1e-8 and 1e-12 new, 1e-10 is the headline run (DL-178, DL-184) | T_ramp 10 s and 316 s. The 1e-10 run is the S5 grid P2 linear run at 10 s and 316.2278 s (UNVERIFIED that its config equals the S13 baseline apart from T_ramp; 11b checks the config hashes) |
| DOP853 against Radau | 120 s: Radau rtol 1e-10 only (1,578.4 s, 0.0957 s per τ; DL-178). Radau 1e-12 at the headline timed out at 3,600 s (DL-097; DL-100 (3)); not run | 10 s (rtol 1e-10; 1e-12 at 10 s only, M-5) and 316 s. Radau at 316 s projects to about 65 min at the 120 s rate (section 9) |
| δ₀ ladder {1e-9, 1e-6, 1e-3} | 120 s: 1e-9 and 1e-3 new, 1e-6 is the headline run | T_ramp 10 s and 316 s (1e-6 from the S5 grid) |
| D43 floor levels, Heun dt ladder | 120 s: 3 levels × 4 rungs × 10 seeds = 120 runs, coupled increments (DL-169, DL-178; the plan's wording "the floor with its Heun dt ladder at 120 s") | The plan lists "D43 floor levels" in the mean-field list at 10, 120 and 316 s but puts the ladder at 120 s only: floor levels at 10 s and 316 s remain (rungs: M11-4) |
| Network, 10 s ramp, dt {1e-3, 5e-4, 2.5e-4, 1e-4} | nothing. One rung exists as MS10 data: S8 headline 10 s, N = 1e4, dt 1e-3, 3 seeds, keys [10, 1, s] (DL-317, DL-319); not a ladder | all four rungs (the plan's "×17" cost; section 7). This is the network part of RB6/S13 (G4-C6, UNVERIFIED reading) |
| Network V_p ±100 against ±200; the ±200 check also at dt 1e-4 | nothing (±100 is the network default in S8, S9, S10) | V_p ±200 at dt 1e-3 and at dt 1e-4 |
| Window × {0.5, 2} | nothing as a run. The window variants of A8 ran on synthetic, baseline-only and S3/S4 records (DL-147) | classifier-only on stored series (no re-simulation): the same variants as RB10 (M11-7) |
| S11 (σ × T_ramp × seeds) | nothing | all of it (section 7) |
| A11 | no module (`scripts/run_A11.py` absent) | write and run after the evaluation rules are frozen (M11-10) |

### 4.3 Where RB9 and RB10 stand and which stored series they read

Both read stored series, with no re-simulation (Table 9.1 row "Analysis and reclassification (A8–A11, RB10)": "stored series only; no re-simulation"). Stored and, by file count, complete (UNVERIFIED that every file is readable; 11b checks): `results/S5/ramp*` (the S5 ramp runs and the headline run S5ramp_0000_240de3ef73be), `results/S7/S7_map1` (900 cells, mode D), `S7_map2` (325 cells), `S7_subgrid` (2,250 mode-N runs); 3,475 npz files under `results/S7`, each with `t_ms, r, v, s, eta, J, Delta, I` at 1 kHz in float64 (M9-16, DL-223); the network records of MS10 (103 runs) under `results/S8`, `results/S9`, `results/S10`. RB10's "headline class unchanged under each change; ≤ 10% of map cells change class" and RB9(c)'s "≤ 5% of cells change class" need the map records; RB9(b) needs the stored v of D-tr cells.

## 5. Carry-in notes (carried forward unchanged)

1. **DL-251 (NOT decided).** "RB2 and S11 need a constant-parameter control at the headline cell for each sigma. To be planned at the start of MS11. Nothing is run or listed now." Planned in this document as open choice M11-3 and labelled a POST-HOC AMENDMENT; nothing is run or listed.
2. **Sigma 0.0624.** Checked at MS10 and not confirmed: the mean-field baseline std reference 0.039522 lies above all six network baselines (0.037989 to 0.038920, mean 0.038455) (DL-318, R25, G4-C4). Frozen, not changed. Every noisy mean-field result of MS11 is labelled "sigma checked, not confirmed". The S11 levels are 0.5, 1 and 2 times 0.0624 (0.0312, 0.0624, 0.1248), by Table 7.2's wording "σ × 0.5, 1, 2"; the plan does not say that the level 1 must equal a network baseline (UNVERIFIED reading).
3. **Claim limits carried unchanged.** G4-C1 to G4-C6 (R31, DL-325; text in `docs/ms10_close.md` (e)), the MS9 limits (G7 of DL-229 and DL-230; D24 of DL-242 and DL-250; A9 label (c) DL-270; the D31 boundary definition DL-254; J_exit,static on P3 and P4 DL-263; the P3 cost 1.57 × the headline; the Defender exclusion user-reported only DL-142) and the MS8 limits (D8 estimator provisional, A_ref reading (a) 2.176222, G6-D1 to G6-D3). They apply to every MS11 statement that uses a network record or a noisy mean-field record. In particular G4-C3 (network classes cannot separate ramp-driven from non-ramp records) bears on how the network part of S13 may be read (M11-5, M11-6).
4. **D36 running total.** 14.21 h of 24 h is a sum on mixed bases (recorded walls, Table 9.1 upper bounds where no wall was recorded, one prediction), UNVERIFIED, not a measured cumulative wall (R33, DL-329). It carries two placeholders that MS11 replaces: "Rest of S13" at its 1.0 h upper bound and "S11 (MS11, not launched)" at the 9a prediction 0.0075 h (`docs/ms9_g_evidence.md` section 3). A single accounting basis for MS11 is open choice M11-11.
5. **Disk (R33).** 153 GB free at MS10 close; free space is measured before every launch; D37 stays open to MS15. MS11 adds about 120 + 30 + 71 + 18 npz of 1 kHz float64 series (section 7); the volume is estimated at 11b from the run lengths, not here.
6. **Open housekeeping untouched:** K5 (DL-064, DL-082), K10 (DL-131 to DL-133), K4-net coupling (MC-03), D37.

## 6. Open choices (none chosen; each with options and a plan-grounded recommendation)

**M11-1. S11 design.** The S11 row names σ, T_ramp and seeds only. (a) Path and profile: P2 at ref_devalle, linear, I = 0, i.e. the headline example (D40), at T_ramp 10, 30, 120 and 300 s; or other paths. (b) Level meaning: factors 0.5, 1, 2 on σ = 0.0624 (`noise.sigma_factor`). (c) T_ramp values: the nominal 10, 30, 120, 300 s as written (30 and 300 s are not S5 grid values, 120 s is the headline value). (d) Noise streams: seed index s is the same stream at every σ and T_ramp (S5 precedent, DL-069) or an independent stream per σ. *Recommendation:* (a) the headline example, because RB2 speaks of "the headline surge class" and Table 6.4 fixes σ on the P2 start state; (b) factors on 0.0624; (c) as written; (d) the same stream per s across σ and T_ramp (S5 precedent; the σ comparison is then paired). 120 runs.

**M11-2. How the RB2 class criterion is read for S11 (class definition per Table 2.1, mode N).** The frozen leaf says "kept means same class as the headline mode-D class under the correspondence" (F-17, DL-157, UNVERIFIED label). The headline mode-D class is D-tr; under Table 2.1, "Noisy and deterministic runs agree when D-tr meets a surge class", and a surge class in mode N is S+, S-rel or S-abs. Options: (A) kept = S+, S-rel or S-abs (the correspondence as written); (B) kept = S+ only; (C) kept = S+ or S-abs (the DL-250 post-hoc view, S-rel not counted); (D) A as the gate with B and C reported beside it, labelled post hoc. Also: at which T_ramp the ≥ 8/10 test is judged (the headline T_ramp 120 s only, or all four); the plan's text says "Headline surge class kept in ≥ 8/10 seeds at 0.5σ and σ" and the frozen file says "2 sigma reported, no pass rule" (F-17). *Recommendation:* (D) with the gate on reading A at T_ramp 120 s at 0.5σ and σ, and the other T_ramp, the 2σ level and readings B and C reported without a verdict; the M9-22 result that S-rel occurs in 1,095 of 2,250 no-ramp runs means reading A alone can pass without a surge, which is what the control of M11-3 exists to show.

**M11-3. The constant-parameter control at the headline cell for each sigma (DL-251; POST-HOC AMENDMENT).** The M9-22 precedent (DL-245): same record structure (2 s discard, 5 s baseline, ramp period, hold), the start state held constant (η̄ = η_start, J = J0), the same σ. Options: (a) headline cell at T_ramp 120 s × 3 σ levels × 10 seeds = 30 runs; (b) a twin of every S11 run (4 T_ramp × 3 σ × 10 seeds) = 120 runs; (c) no new control (M9-22 rates at σ × 1 on the 225 subgrid cells as context only; whether the headline cell was among them is UNVERIFIED). Key [11, 2, s]. *Recommendation:* (a), because DL-251 says "at the headline cell for each sigma"; (b) costs seconds more (section 9) if the reviewer wants the control at every T_ramp. Controls are labelled post hoc, feed no gate, and are reported beside the S11 classes.

**M11-4. Which S13 families run at MS11 and which are already done.** Done at MS8 and not repeated: all of the headline subset at 120 s (section 4.2). Remaining by the plan's wording: (1) rtol ladder at 10 and 316 s; (2) δ₀ ladder at 10 and 316 s; (3) DOP853 against Radau at 10 and 316 s; (4) D43 floor levels at 10 and 316 s; (5) the network part (M11-5); (6) window (M11-7). Sub-choices: Radau scope: full (rtol 1e-10 at 10 and 316 s, 1e-12 at 10 s only, M-5), 10 s only, or none away from the headline (cut order step 1); floor scope at 10 and 316 s: the default rung 1e-3 only (3 levels × 10 seeds), the full ladder (3 × 4 × 10), or none; the T_ramp 316 reading: the S5 grid value 316.2278 s (RB3(c) uses 316.2 s) or the rounded 316 s; reuse of the S5 grid run as the 1e-10 / 1e-6 member. *Recommendation:* the plan's full scope for (1) to (3) as the first list, with the cut order of 9.3 applied only as far as the measured prediction requires (section 9); floor at the default rung, because the plan puts the ladder "at 120 s"; T_ramp 316.2278 s; reuse the S5 grid runs after 11b confirms the config hashes. Any run projecting over one hour (Radau at 316 s) is flagged for the reviewer and launched by the reviewer.

**M11-5. The network part of S13 (the RB6 rerun of G4; G4-C6, UNVERIFIED reading).** Table 11.2 G4: "Disagreement in ≥ 2/4 cells → rerun RB6". Options for what "rerun RB6" is: (a) the network part of S13 (dt ladder, V_p) at N = 1e4 on the 10 s ramp; (b) all of RB6 again (the mean-field parts are deterministic and would repeat); (c) not run (G4 is report-only for the run order). Sub-choices: seeds per configuration (1, 3 as in S8's headline, or 10); whether the 1e-3 rung is re-run under the new key (so that all rungs of one seed share their initial V; the S8 runs use [10, 1, s], which the collision rule forbids reusing) or the S8 runs stand for it; constant-parameter controls per configuration (DL-231; MS10 carried one per configuration) or none. *Recommendation:* (a); 3 seeds; re-run the 1e-3 rung under [11, 4, s]; no new controls, because RB6's network clause is a numerical-convergence statement on f_pk and no class statement is made from these runs (G4-C3 stands), with the controls as an option if the reviewer wants class statements.

**M11-6. Which f_pk the network RB6 clause reads ("halving dt changes f_pk < 2%"; compared dt 1e-3 against 5e-4, F-21).** Options: (a) the classifier's episode f_pk (undefined when the network record has no episode, and the network classes are not ramp-specific, G4-C3); (b) the PSD argmax in the 25–100 Hz band of v over a fixed post-onset window (O6 convention: argmax of the PSD in G, resolution 1/W, no interpolation); (c) both. The plan gives no window. *Recommendation:* (c), with (b) over the window that the same-seed 1e-3 run's classifier episode defines, stated in `docs/ms11_eval_rules.md` before any run; "UNVERIFIED reading" labelled.

**M11-7. How RB9 and RB10 (and the window line of S13) are evaluated: stored series only, or new runs.** Table 9.1: "stored series only; no re-simulation". Options: (a) stored series only: RB10 variants and RB9(b), (c) by reclassification of the stored headline run and the map records; (b) add new runs. Sub-choices: which records count for "≤ 10% of map cells" and "≤ 5% of cells": map 1 mode D (900 cells, as the G5 mapping `map1_mode_that_counts`, F-26) alone, or map 1 and map 2 (1,225 cells), with the mode-N subgrid reported separately; and the unit of "changes class" (raw class or the three Table 2.1 categories, M9-14). *Recommendation:* (a); map 1 and map 2 pooled and each alone, mode D, raw classes with the categories beside them; the mode-N subgrid reported without a verdict; the S13 line "Window × {0.5, 2}" is the window variant of RB10, not a separate run.

**M11-8. RB9(a) and RB9(d).** (a) "within 0.5%": the test-level check exists (section 4.1). Options: cite it as the result (labelled test-level), or add one dimensional headline-length run beside the non-dimensional headline run (needs a dimensional right-hand side, which exists only in the test). (d) "τ ± 20% … reported only": options: two mean-field runs at τ = 8 and 12 ms on the headline path, or no run (the model is non-dimensional, so frequencies in Hz scale with 1/τ by construction; durations in seconds do not). *Recommendation:* (a) cite the test as test-level and ask whether it counts; (d) two runs reported only (about 2 × the headline, section 9), labelled, in no gate.

**M11-9. RB9(b) and (c) detail.** (b) "spectral vs cycle frequency, within 1/W": spectral f_pk is the PSD argmax (O6), cycle frequency is the unwrapped analytic phase over 2π in mode D (O5); which cells (the headline run and the D-tr cells of map 1 are the stored ones). (c) bands 25–100 against 30–120 Hz: ≤ 5% of cells change class (reuses the A8 band variant). *Recommendation:* all D-tr cells of map 1 and map 2 plus the headline; cell count and per-cell differences written out; the threshold applied to the cell fraction.

**M11-10. How A11 aggregates and what it does with checks that already have a result.** The plan: A11 "reads the frozen criteria and writes results/A11/a11_robustness.csv: value, threshold, pass or fail, and the input commits. Failed checks are reported, not dropped". Options: (a) recompute each verdict from stored result files with the stored evaluators; (b) copy the logged verdicts with their DL numbers; (c) recompute and print the logged verdict beside it, flagging any difference. Status values for checks without a numeric threshold (REPORTED, NOT JUDGED, NOT EVALUABLE). *Recommendation:* (c); one row per criterion leaf of the frozen file; RB1 FAIL, RB3(a) not judged at the headline, RB3(b) under both onset readings, RB6 solver clause DOES NOT MEET, RB8 heterogeneity NOT EVALUABLE and the M4 parts "open to MS12" appear as logged, never as PASS; no new numeric threshold is written into A11.

**M11-11. D36 accounting basis for MS11 (one basis).** Options: (A) add the MS11 prediction on top of 14.21 h (errs high; the two placeholders stay); (B) replace the two placeholders ("Rest of S13" 1.0 h and "S11" 0.0075 h) with the MS11 figure on one basis: the predicted wall at 10 workers (the larger of the sum divided by 10 and the longest run), replaced by the recorded launch wall of each list once it has run; the carried 14.21 h otherwise untouched and still labelled mixed-basis and UNVERIFIED; (C) rebuild the whole total from recorded walls (not formable: the MS8 close (f) says the log does not support a measured cumulative figure). *Recommendation:* (B), stating (A) beside it so the margin is shown both ways.

**M11-12. How the Table 9.1 allowance is shared for S13 and S11.** S13: one row "< 1 h" for the whole of S13 (scope names 10, 120 and 316 s and the network ladder); the MS8 part took 26.3 min (DL-178). S11 shares the row "S11, S12 mean field, S16: < 40 min" with S12 and S16, which have run (MS9). Options: judge the MS11 remainder alone against 1 h and 40 min; judge S13 as a whole (MS8 recorded + MS11 predicted) against 1 h; give S11 a share of the 40 min (the plan states none: UNVERIFIED). *Recommendation:* S13 as a whole (MS8 recorded + MS11 predicted) against 1.5 × 1 h; S11 (with its control) against 1.5 × 40 min; the shares are written in the timing record.

**M11-13. Things the plan leaves without a number, stated in words (each needs the reviewer's reading before the evaluation file is frozen).** (i) RB2 at 2σ and at T_ramp other than 120 s: the plan and the frozen file give no pass rule; reported. (ii) RB6 rtol at 10 and 316 s: reported, not a pass test (the plan says so for rtol). (iii) RB6 solver agreement ("class with onset within 1 ms") at 10 and 316 s: the plan states it in the RB6 row without a T_ramp; G6 applies it "at the headline point"; reading: judged at the headline, reported elsewhere. (iv) RB6 / RB5 / RB3(b) floor runs at 10 and 316 s: no criterion in the plan (RB3(b) is stated for the headline delay); reported. (v) RB6 network: no pass number for V_p ±100 against ±200 other than the f_pk change; the plan names none, so the comparison is reported with the 2% value applied only to the dt halving as the frozen file states. (vi) RB6 network seeds and the f_pk source (M11-5, M11-6). (vii) RB9(b), (c) cell sets (M11-9) and RB9(d) method (M11-8). (viii) RB10's cell set and unit of change (M11-7). (ix) A11's treatment of partly evaluated checks (M11-10). (x) S11: that the headline in RB2 is T_ramp 120 s with I = 0 on P2 (D40). In every case the criterion is stated in words and the reviewer is asked; no number is invented.

**M11-14. Parts projecting over one hour.** Radau at T_ramp 316 s (one run, about 65 min at 0.0957 s per τ, section 9), and possibly the dt 1e-4 network runs (several minutes each, section 9). Options: leave in the list with a separate launch by the reviewer; apply cut order step 1 (Radau only at the headline T_ramp). *Recommendation:* decided on the measured table (section 9.4); any part over one hour is launched by the reviewer in PowerShell, never by Claude Code.

## 7. Run counts with derivations (readings of section 6 as recommended; alternatives in the counts module)

Computed by `mprsurge.analysis.ms11_counts` (tests: `tests/test_ms11_counts.py`). One τ = 10 ms, so 100 τ per second. A mode-N or network run integrates 2 s of discard, the 5 s baseline, 1.25 T_ramp (P2: the J ramp ends 1.25 T_ramp after t_on, CP14) and the 10 s hold.

| Family | Derivation | Runs | Work |
|---|---|---|---|
| S11 | σ {0.5, 1, 2} × T_ramp {10, 30, 120, 300} s × 10 seeds. Integrated seconds per (σ, seed): 29.5 + 54.5 + 167 + 392 = 643 s = 64,300 τ | 3 × 4 × 10 = **120** | 30 × 64,300 = 1.929e6 τ = 1.929e9 Heun steps at dt 1e-3 τ |
| S11 control (M11-3 (a)) | headline T_ramp 120 s (167 s = 16,700 τ) × 3 σ × 10 seeds. (b): 120 runs; (c): 0 | **30** | 5.01e8 Heun steps |
| S13 MF rtol | {1e-8, 1e-12} × {10 s, 316.2278 s} (1e-10 is the S5 grid run) | **4** | 2 values × (2,750 τ at 10 s + 41,028 τ at 316.2278 s), DOP853 |
| S13 MF δ₀ | {1e-9, 1e-3} × {10 s, 316.2278 s} (1e-6 is the S5 grid run) | **4** | 2 values × (2,750 τ + 41,028 τ), DOP853 |
| S13 MF Radau (M11-4) | rtol 1e-10 at 10 s and 316.2278 s, 1e-12 at 10 s only (M-5) | **3** (10 s only: 2; cut order 1: 0) | 2,750 τ ×2, 41,029 τ ×1 |
| S13 MF floor (M11-4) | 3 levels × 10 seeds × {10 s, 316.2278 s} at the default rung (full ladder: × 4 rungs = 240) | **60** | 60 coupled Heun runs |
| S13 network (M11-5) | 6 configurations (dt 1e-3, 5e-4, 2.5e-4, 1e-4 at V_p 100; V_p 200 at dt 1e-3 and 1e-4) × 3 seeds, N = 1e4, 10 s ramp (2,950 τ). Cost in units of one dt-1e-3 run: 1 + 2 + 4 + 10 = 17 for the ladder (the plan's "×17"), 1 + 10 = 11 for the V_p pair | **18** (with controls 36) | 28 units × 2.95e10 updates × 3 seeds = 2.48e12 neuron-updates |
| RB9(d) (M11-8) | 2 mean-field runs, τ = 8 and 12 ms, headline path | 2 (optional) | about 2 × the headline |
| RB9(a)–(c), RB10, window | stored series only | 0 | analysis time, timed separately |
| A11 | stored results only | 0 | analysis time |
| **Total new simulation runs (recommended readings)** | 120 + 30 + 4 + 4 + 3 + 60 + 18 | **239** (+ 2 optional) | |

Disk and memory are estimated at 11b from the run lengths (float64, 8 arrays at 1 kHz, M9-16); the largest MS11 mean-field series is 410 s (about 3.3 MB raw).

## 8. Evaluation rules to be written in words and frozen before any run (MS10 pattern)

11a does not write these files. `docs/ms11_eval_rules.md` and `configs/ms11/ms11_eval.yaml` must be written and committed at 11c, before any MS11 run, and must contain the following. Unspecified choices are **required fields in the YAML that raise an error when missing** (the `ms10_eval.yaml` mechanism); each carries its status (`ruled`, `UNVERIFIED`) and its DL source.

1. **RB2 / S11:** the class set that counts as "kept" (M11-2), the T_ramp at which the ≥ 8/10 test is judged, the σ levels that carry a pass rule (0.5σ and σ) and the one that does not (2σ), the readings reported beside the gate (B, C), the control rates (M11-3) and how they are reported; labels "sigma checked, not confirmed" (G4-C4), "POST-HOC AMENDMENT" for the control, "S-rel not counted as ramp evidence" (DL-250) as report-only.
2. **S11 time-origin and onset conventions:** the classifier onset (window centre) as in R27, the raw crossing secondary; D8 provisional label; the baseline windows (last 5 s before t_on, 4 windows at W = 2 s for T_ramp ≥ 60 s; W = max(0.2 s, T_ramp/30) otherwise, Table 2.1); the short-window false-surge limit (306, 400, 172, 24 of 500 at W = 0.2, 0.333, 0.593, 1.054 s) stated beside the classes at T_ramp 10 and 30 s.
3. **S13 mean field:** per T_ramp the quantities reported (class, onset to the 1 ms output grid, delay, rtol and δ₀ shifts), the solver-pair statement at 10 and 316 s (class and onset difference in ms, judged only at the headline per M11-13 (iii)), the floor medians per level with the RB3(b) form at 10 and 316 s (reported), the 5% Heun statement at 120 s unchanged.
4. **S13 network:** the f_pk source and window (M11-6), the 2% bound on the dt halving (1e-3 against 5e-4, F-21), the V_p comparison (reported), the statement that no class is claimed from these runs (G4-C3) unless M11-5 adds controls, seed count, the time-origin check as in MS10.
5. **RB9:** (a) the source (test-level or run), (b) the cell set and the 1/W rule with W per cell, (c) the cell set and the 5% rule, (d) the method and "reported only".
6. **RB10:** the five variants, the headline-unchanged rule, the 10% rule, the cell set and unit of change (M11-7), the window variants as the S13 window line, how cells for which a variant does not fit are counted (a "not run" count, as in DL-147).
7. **A11:** the rows (one per criterion leaf of the frozen file), the status vocabulary (M11-10), the recompute-and-compare rule, the input commits column, the non-use of any new threshold.
8. **D36 / timing:** the accounting basis (M11-11) and the allowance shares (M11-12), the rule that any part projecting over one hour is flagged and launched by the reviewer.
9. **Labels and claim limits:** exploratory and post-hoc items labelled and kept out of every pre-registered list and out of every gate; G4-C1 to G4-C6, MS9 and MS8 limits attached to the outputs that use a network or noisy record.
10. **Launcher refusal rules** (as in MS10 10e): refuse to start unless the criteria loader verifies the freeze, the tree is clean, the list hash equals the frozen list hash, free disk space is measured and above the estimate, and the seed keys equal the frozen keys.

## 9. Measured timing gate (plan 9.2; the 8a/9a/10a method)

**Method.** Each untimed family is timed from its matching timing cell (9.2 step 2: "not from the headline alone"): 10 concurrent copies, one batch, per-run median pooled over the copies (DL-102), judged at 10 workers (DL-103), the longest single run also alone. The cells are `configs/timing/ms11/*.yaml`, layered on `configs/S5.yaml` by `scripts/time_one_run.py`, started by `scripts/run_timing_ms11.sh` from a clean tree after the commit that adds this plan (so every timing record shows git dirty = false). **These are TIMING SAMPLES: not pre-registered runs, in no run list, feeding no gate, no record of a result family.** Each prediction is the larger of (sum of run walls ÷ 10) and the longest run, with the longest-first schedule also printed (`ms11_counts`).

| Family | Matching timing cell(s) |
|---|---|
| S11 and its control (mode N, σ levels, T_ramp 10, 30, 120, 300 s) | `ms11_s11_t10`, `ms11_s11_t30`, `ms11_s11_t120_sf0p5`, `ms11_s11_t120_sf2`, `ms11_s11_t300` (cost per Heun step; the slowest cell is used) |
| S13 DOP853 rtol / δ₀ at 316 s | `ms11_dop_1e-10_t316`, `ms11_dop_1e-12_t316`; at 10 s the MS8 cells `ms8_dop_1e-8/1e-10/1e-12_t10` |
| S13 Radau | not sampled at 316 s (it would run for over an hour): the measured 120 s rate 0.0957 s per τ (DL-178); rtol 1e-12 at 10 s from the ratio of the 10 s Radau samples (299.7 s over 143.4 s alone, `results/timing/radau_1e-12_t10.json`, `radau_1e-10_t10.json`) |
| S13 floor levels at 10 and 316 s (Heun dt ladder, coupled increments) | `ms11_floorc_l2_dt1e-3_t316`, `ms11_floorc_l2_dt1e-4_t316` (wall = c₀·τ + c₁·τ/dt fitted on the two) |
| S13 network dt ladder, V_p | `net_1e4` (MS10, dt 1e-3), `ms11_net_dt5e-4`, `ms11_net_dt2p5e-4`, `ms11_net_dt1e-4` (also alone), `ms11_net_vp200`, `ms11_net_vp200_dt1e-4` |
| Window, RB9, RB10, A11 | analysis on stored series; timed when the analysis modules exist (Table 9.1: "measured in the timing gate") |

**Allowances (Table 9.1) used, with their status.** S11: "S11, S12 mean field, S16 … < 40 min" (40 min; the share for S11 is not stated). S13: "S13 numerics … < 1 h" (60 min, whole of S13). Launch rule: prediction ≤ 1.5 × allowance and the total inside the D36 cap of 24 h. Cut order 9.3 (quoted in section 2.9) if it does not fit.

### 9.4 Result of the timing samples (DL-334; TIMING SAMPLES, in no run list, feeding no gate)

Samples taken at commit 2b43379 on a clean tree (`git status --porcelain` empty before each; `results/timing/ms11/`, git-ignored; prediction text `results/timing/ms11/prediction_11a.txt`). 10 concurrent copies, one batch, per-run median. **Incident:** the five S11 mode-N cells failed in the first pass (0.0 s, "not ok") because `scripts/run_timing_ms11.sh` set `--set seeds.spawn_key=[0]` only for the floor cells; they were rerun from the shell with that option on the same clean tree (the script is corrected in the post-timing commit). The other nine cells and the alone run were taken by the script as committed. Peak total python working set polled during the cells: 2.78 GB (a lower bound, UNVERIFIED, as DL-142).

| Cell | Per-run median (10 copies) | τ simulated | s per τ |
|---|---|---|---|
| `ms11_s11_t10` / `t30` / `t120_sf0p5` / `t120_sf2` / `t300` | 0.41 / 0.84 / 2.62 / 2.73 / 5.68 s | 2,950 / 5,450 / 16,700 / 16,700 / 39,200 | 1.4–1.6e-4 (σ factor 0.5 and 2 cost the same per step; 1.635e-7 s per Heun step used) |
| `ms11_dop_1e-10_t316` / `ms11_dop_1e-12_t316` | 494.5 / 604.1 s | 41,028 | 0.01205 / 0.01472 |
| `ms11_floorc_l2_dt1e-3_t316` / `dt1e-4_t316` | 18.6 / 82.2 s | 41,228 | 0.00045 / 0.00199 |
| `net_1e4` (MS10, dt 1e-3) / `ms11_net_dt5e-4` / `dt2p5e-4` / `dt1e-4` | 56.8 / 140.8 / 286.0 / 691.1 s (alone, dt 1e-4: 340.4 s) | 2,950 | 0.0193 / 0.0477 / 0.0970 / 0.2343 |
| `ms11_net_vp200` / `ms11_net_vp200_dt1e-4` | 68.2 / 669.5 s | 2,950 | 0.0231 / 0.2269 |
| Radau (not sampled at 316 s) | DL-178: 0.0957 s per τ at 120 s | 41,028 | 65.4 min predicted for the one run |

**Prediction per family, recommended readings (M11-1 to M11-5 as recommended; Radau at the plan's scope):**

| Family | Runs | Prediction (10 workers) | Allowance (Table 9.1) | Ratio | Rule (≤ 1.5 ×) |
|---|---|---|---|---|---|
| S11 + control | 150 | 40 s (sum 397 s, longest 6 s) | 40 min (row shared with S12, S16; share UNVERIFIED) | 0.02 | fits |
| S13 remainder: mean field (rtol, δ₀, Radau, floor) | 71 | run walls 2.1 h in all, of which the one Radau run at 316 s is 65.4 min | | | |
| S13 remainder: network (6 configurations × 3 seeds) | 18 | sum 1.6 h of run walls, longest 11.5 min | | | |
| **S13 remainder, whole** | 89 | **65.4 min** (the longest run) | | | |
| **S13 as a whole** (MS8 recorded 26.3 min + remainder) | | **91.8 min** | 60 min (whole row) | **1.53** | **FAIL by 1.8 min** (limit 90 min) |

Per part: S13 rtol at 316 s 18.3 min of run walls (longest 10.1 min), δ₀ at 316 s 16.5 min (longest 8.2 min), floor at 316 s 9.3 min (longest 19 s), floor at 10 s 40 s, rtol and δ₀ at 10 s about 1 min each, Radau at 10 s 263 s (rtol 1e-10) and 550 s (rtol 1e-12); network: dt 1e-3 170 s, 5e-4 7.0 min, 2.5e-4 14.3 min, 1e-4 34.6 min of run walls (longest 11.5 min), V_p 200 at dt 1e-3 205 s and at dt 1e-4 33.5 min (longest 11.2 min).

**Other readings (same arithmetic):**

| Reading | S13 whole | Rule | S11 + control | MS11 added to D36 |
|---|---|---|---|---|
| Radau at 10 s only (`t10_only`) | 41.9 min (0.70 ×) | fits | 40 s | 0.271 h |
| Radau only at the headline T_ramp (cut order step 1, `headline_only_cut_1`) | 40.6 min (0.68 ×) | fits | 40 s | 0.249 h |
| Cut-1, floor full ladder at 10 and 316 s, control at every T_ramp, network controls | 58.0 min (0.97 ×) | fits | 63 s | 0.546 h |

**Parts over one hour (flagged for the reviewer's ruling; launched by the reviewer in PowerShell, never by Claude Code):** the Radau run at T_ramp 316.2278 s, rtol 1e-10, one run, predicted 65.4 min from the measured 120 s rate (DL-178: 0.0957 s per τ, which was 1.27 × the linear-scaled 10 s value). The prediction is an extrapolation, not a sample (a sample would itself run over an hour). No other part exceeds one hour: the longest network run is 11.5 min (dt 1e-4, 10 copies; 5.7 min alone), the longest DOP853 run 10.1 min (rtol 1e-12 at 316 s).

**D36 (24 h cap), basis B of M11-11 (the two placeholders replaced by the MS11 predicted wall):** carried 14.21 h (mixed bases, UNVERIFIED) − 1.0075 h + 1.102 h = 14.30 h with the full-scope Radau, 13.47 h with Radau at 10 s only, 13.45 h with cut order step 1; basis A (added on top): 15.31 h, 14.48 h, 14.46 h. All inside 24 h; the margin is at least 8.7 h on either basis. Analysis, evaluation and A11 time are not included (no timing cell exists yet; M11-11).

**Launch-rule application and cut order (9.2 step 3, 9.3).** With the plan's full S13 scope, the whole-row prediction is 91.8 min against the limit 90 min, a FAIL by 1.8 min that is caused by the single Radau run at 316 s alone (without it the row is 40.6–41.9 min). Cut order step 1 ("Run Radau only at the headline T_ramp") removes exactly that run and the 10 s Radau runs, and the row fits at 40.6 min; step 2 (drop network dt 1e-4) is not needed. Nothing has been cut by this plan: which option is used is M11-4 and M11-14 for the reviewer. Judged against the MS11 remainder alone (1 h, M11-12 option 1) the full scope is 65.4 min, 1.09 × the allowance, which fits the 1.5 × limit. The rule is applied to the recommended readings only; it is re-applied on the ruled lists at 11b.


## 10. Proposed seed keys (DL-333; PROPOSED, UNVERIFIED until the reviewer confirms; none is in a config yet)

Root seed 20261008. First element 11 = MS11 (DL-141 convention). Existing keys (the authority): [0]–[9]; [7, 4, s]; [7, 9], [7, 9, 0], [7, 9, 1, k]; [8, 1, s]; [8, 2, l, s]; [9, 1, s], [9, 2, 0], [9, 3, s]; [9, 4, s]; [9, 5, 0..8]; [9, 6, 0..9]; [9, 7, s]; [10, 1, s]; [10, 2, c, s]; [10, 3, n, s]; [10, 4, l, s]; [10, 5, k, s].

| Key | Use |
|---|---|
| [11, 1, s], s = 0..9 | S11 ramp runs; the same stream at every σ and T_ramp (M11-1 (d)) |
| [11, 2, s], s = 0..9 | S11 constant-parameter controls (M11-3) |
| [11, 3, t, l, s], t = 0..1 (T_ramp 10, 316.2278 s), l = 0..2 (floor level), s = 0..9 | S13 mean-field floor runs; the rungs of one (t, l, s) share the key (F-14, as [8, 2, l, s]) |
| [11, 4, s], s = 0..2 | S13 network runs; every configuration of one s shares the key (same initial V) |
| [11, 5, k, s], k = 0..5, s = 0..2 | S13 network controls (only if M11-5 chooses them) |

Total distinct keys: 10 + 10 + 60 + 3 + 18 = 101. The collision test is `tests/test_ms11_counts.py`: it writes out every existing key above and also scans the repository, and fails if a proposed key is equal to, a prefix of, or prefixed by any existing key; a second test checks that the rule catches a deliberately colliding key (teeth). Result: see section 12.

## 11. What 11b must do next (no prompt text)

1. Obtain the reviewer's rulings on M11-1 to M11-14 and on the timing decision (section 9.4); record them as R34 onward.
2. Confirm or replace the proposed seed keys.
3. Write `docs/ms11_eval_rules.md` and `configs/ms11/ms11_eval.yaml` (section 8) with required fields, and freeze them before any run.
4. Write the run lists (S11, control, S13 mean-field remainder, S13 network), their configs and a launcher with refusal rules, with tests on the counts and hashes; check that the S5 grid runs at 10 s and 316.2278 s equal the S13 baselines apart from T_ramp, if they are to be reused.
5. Write `scripts/run_A11.py` and the RB9 / RB10 reclassification code on stored series, with tests on synthetic fixtures; check that the stored map series are readable.
6. Re-apply the launch rule on the ruled lists (the timing in section 9 holds for the recommended readings only), measure free disk space, and hand each list to the reviewer to launch; any part over one hour is launched by the reviewer in PowerShell.

## 12. Decision-log entries of 11a and results of the checks made in 11a

| DL | Content |
|---|---|
| DL-330 | R33 recorded as ruled (opening note of this file) |
| DL-331 | pre-checks, plan quantities, status inventory, carry-in notes |
| DL-332 | open choices M11-1 to M11-14, run counts, evaluation-file contents (not decided) |
| DL-333 | proposed seed keys [11, ...] and the collision test |
| DL-334 | measured timing, launch-rule application and decision (post-timing update) |

Checks made in 11a: the seed-key collision test (`tests/test_ms11_counts.py`) and the run-count tests pass; fast suite before the first commit (2b43379): 792 passed, 11 deselected, 9 xfailed, pytest exit code 0 (baseline 783 passed; the 9 new tests are `tests/test_ms11_counts.py`); the second fast-suite run is recorded in DL-334.

