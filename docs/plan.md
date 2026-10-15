Technical Plan · complete document (Parts 1 and 2)

**Technical Plan: MPR neural mass model of the dying-brain gamma surge**

**Contents:** front matter; section 1 (summary, revised in Part 2); sections 2 to 6 (Part 1; edited in v0.4 only where Table 12.1 records it); a short Part 2 preflight; sections 7 to 12 and Appendices A to D (Part 2); the v0.3 additions (section 7.3, section 12.7 and Appendix E); the v0.4 change log (Appendix F); the v0.5 change log (Appendix G); and the Part 1 handoff, moved to the end as an appendix.

**Version** 0.5 (v0.4 revised after one independent sweep, REVIEW 5; changes in Appendix G, v0.4 changes in Appendix F) · **Date** 11 October 2026 · **Evidence base:** the seven attached reports; from v0.3 also RESULT A and RESULT B (RA, RB) · **Target machine:** Ryzen 5 5600, 16 GB RAM, Windows 11, CPU only.

## Read this first

**Prior work: PARTIAL OVERLAP.** The v0.3 G8 pre-check (RA) found no computational model of any class that reproduces the dying-brain gamma surge, and Report 2 found none either \[R2, summary; RA, verdict\]. Each part of the method has precedent: slow passage through a Hopf bifurcation in an exact QIF mean field (Taher, Avitabile and Desroches 2022) and slow-input canards in QIF networks and their mean field (Avitabile, Desroches and Ermentrout 2022) \[RA, verdict\] (section 12.7). Reports 1 and 5 found no MPR-family study that measures a transient gamma episode against ramp rate under a monotone ramp through a Hopf point \[R1, gap statement; R5, gap statement\] \[verified\]; R5 ran one dedicated search. Report 2 rates the idea "novel in combination; components partly covered", medium confidence, because Google Scholar, PubMed and conference abstracts were not searched natively \[R2, summary; R2, §2.6; R2, §7\]. v0.4 decides D41: the claim is a first mechanistic model of the surge, with the slow-passage methods cited as precedent (section 2.6). The research question and the models are unchanged.

**Build order.** Reports 1, 2, 3 and 5 agree that the unforced two-variable MPR population has only fixed-point attractors, so it can give a damped ring but not a sustained surge \[verified\]. The requested order (single population first) is kept, but the 2D stage is short and diagnostic, and gate G1 (section 4.3) decides the move to the three-variable inhibitory model. The reports predict that G1 will trigger \[reasoned, not tested\].

## Conventions

**Reports.** R1 = file "Track T1" (MPR foundations); R2 = "Track T2" (gap check; its file title wrongly reads "Peer Review…"); R3 = "Track T3" (hypoxic failure); R4 = "Track T4" (dying-brain data); R5 = "Track T5" (validation practice); R6 = "Track T6" (journal); R7 = "Track T7" (reviewer expectations). Most report headings were lost in text extraction, so citations give the surviving section number (for example \[R3, §2.5\]) or a named part (for example \[R1, verification list\]). From v0.3: RA = RESULT A (prior-work search for gate G8); RB = RESULT B (primary-source equations and values), cited by item number, for example \[RB-item 2b\]. From v0.5 a RESULT B item is written "RB-item n", so that it cannot be confused with the robustness checks RB1–RB10 (Table 7.2). "MPR App. A/C/E" are appendices of the MPR paper, not of this plan (Appendices A–G); "§" inside a report citation such as \[R3, §2.5\] is a report section, and a bare "§" (as in the "Where" columns of Appendices F and G) is a section of this plan.

**Status tags.** \[verified\] = two or more independent sources in the reports. \[single source\]. \[reasoned, not tested\] = an inference or derivation not yet checked. \[needs decision\] = not settled by the reports; a default and its test are given, or, for an item whose default is set at a named milestone, that milestone and the test (D43: set at MS7); all are listed in Appendix C. From v0.3, an RB item marked VERIFIED counts as one source (the primary text); RB items marked PARTIAL or UNVERIFIED change no tag. From v0.4, RA counts as one source for what it reports reading, at the read depth recorded in Appendix E (for example, the 2025 noisy-Hopf preprint: introduction only). Status words in tables map onto these tags: "confirmed" marks a \[needs decision\] default matched by one VERIFIED RB item; "single source (secondary)" is \[single source\] resting on secondary snippets; "incomplete" marks an optional check whose values RB marks PARTIAL. Review findings are cited by their TRIAGE ID (Appendix F); from v0.5, findings of REVIEW 5 by their review ID (SC-01 to SC-10, MC-01 to MC-33; Appendix G).

**Units in code.** All code integrates in units of the membrane time constant τ and converts to ms and Hz only at output (section 3.3).

**Contents**

[Read this first 1](#read-this-first)

[Conventions 1](#conventions)

[1. Summary 5](#summary)

[2. Scope and hypothesis 7](#scope-and-hypothesis)

[2.1 Research question 7](#research-question)

[2.2 Hypothesis 7](#hypothesis)

[2.3 Operational definition of a surge 7](#operational-definition-of-a-surge)

[2.4 Negative controls 9](#negative-controls)

[2.5 Out of scope 9](#out-of-scope)

[2.6 Novelty boundary 9](#novelty-boundary)

[3. Verified science base 10](#verified-science-base)

[3.1 MPR equations 10](#mpr-equations)

[3.2 Parameter table 11](#parameter-table)

[3.3 Mapping model time and output to measurable quantities 12](#mapping-model-time-and-output-to-measurable-quantities)

[3.4 Dying-brain facts to be matched 12](#dying-brain-facts-to-be-matched)

[3.5 Gaps 13](#gaps)

[4. Model specification 13](#model-specification)

[4.1 Base model M2 and expected primary model M3 13](#base-model-m2-and-expected-primary-model-m3)

[4.2 Extensions 13](#extensions)

[4.3 Decision rules 14](#decision-rules)

[4.4 Hypoxia mapping 14](#hypoxia-mapping)

[4.5 Competing hypotheses: local hypoxia versus non-local drive 15](#competing-hypotheses-local-hypoxia-versus-non-local-drive)

[5. Analysis plan 15](#analysis-plan)

[5.1 Continuation tools on Windows 15](#continuation-tools-on-windows)

[5.2 Steps 16](#steps)

[6. Simulation plan 18](#simulation-plan)

[6.1 Environment (Windows, PowerShell) 18](#environment-windows-powershell)

[6.2 Mean-field integration 19](#mean-field-integration)

[6.3 QIF network comparison 19](#qif-network-comparison)

[6.4 Noise models 20](#noise-models)

[6.5 Runs 20](#runs)

[6.6 Seeds and run records 21](#seeds-and-run-records)

[6.7 Figure budget 21](#figure-budget)

[Part 2 preflight 22](#part-2-preflight)

[7. Validation and robustness 22](#validation-and-robustness)

[7.1 Replication stage 22](#replication-stage)

[7.2 Robustness checks 24](#robustness-checks)

[7.3 Model-variant equations (RB8, S14, S15) 25](#model-variant-equations-rb8-s14-s15)

[8. Figures 27](#figures)

[9. Compute budget 28](#compute-budget)

[9.1 Tools on Windows 29](#tools-on-windows)

[9.2 Feasibility gate 29](#feasibility-gate)

[9.3 Cut order 29](#cut-order)

[10. Repository design 31](#repository-design)

[10.1 Folder tree 31](#folder-tree)

[10.2 README: Windows setup (PowerShell) 33](#readme-windows-setup-powershell)

[10.3 Configuration system 33](#configuration-system)

[10.4 Provenance 34](#provenance)

[10.5 Unit tests 34](#unit-tests)

[10.6 Results and decision log 35](#results-and-decision-log)

[10.7 Git workflow 35](#git-workflow)

[10.8 Reproducibility checklist 36](#reproducibility-checklist)

[10.9 Working with Claude Code in VS Code 37](#working-with-claude-code-in-vs-code)

[11. Milestones and decision gates 38](#milestones-and-decision-gates)

[12. Risks, conflicts and open questions 41](#risks-conflicts-and-open-questions)

[12.1 Corrections to Part 1 41](#corrections-to-part-1)

[12.2 Conflicts between reports 44](#conflicts-between-reports)

[12.3 Items marked \[needs decision\] 45](#items-marked-needs-decision)

[12.4 Not verified 46](#not-verified)

[12.5 Scientific risks 47](#scientific-risks)

[12.6 Open questions 48](#open-questions)

[12.7 G8 result 48](#g8-result)

[Appendix A. Source list 50](#appendix-a.-source-list)

[Appendix B. Parameter table in full 53](#appendix-b.-parameter-table-in-full)

[Appendix C. Decision log template 56](#appendix-c.-decision-log-template)

[Appendix D. Glossary of terms and symbols 59](#appendix-d.-glossary-of-terms-and-symbols)

[Appendix E. G8 search log 61](#appendix-e.-g8-search-log)

[Appendix F. v0.4 change log 63](#appendix-f.-v0.4-change-log)

[Appendix G. v0.5 change log 67](#appendix-g.-v0.5-change-log)

[Part 1 handoff 70](#part-1-handoff)

# 1. Summary

**Question.** Can an MPR neural mass model, driven by a slow hypoxia-like parameter change, produce a transient gamma-range surge, and in which regimes does the surge appear or fail? Motivation: the surge in 2 of 4 dying patients after ventilator withdrawal (Xu et al. 2023) and in rats after cardiac arrest or asphyxia \[R4, §2.1–2.2\] \[verified\]. The project makes no claim about consciousness (section 2.5).

**Prior work: PARTIAL OVERLAP (RA; section 12.7).** No report found a computational model of any class that reproduces the dying-brain gamma surge: after KCl arrest in rats, and after ventilator withdrawal but before arrest in humans \[R2, summary; R4, TL;DR; RA, verdict\]. All searches used a general web engine \[R2, §7; RA, Caveats\]. Report 2 rates the idea "novel in combination; components partly covered", with medium confidence, because native Scholar, PubMed and conference searches were not run \[R2, summary; R2, §2.6; R2, §7\]. Claim to defend (D41, decided in v0.4): a first mechanistic, exact (MPR) mean-field model of a transient gamma surge under a hypoxia-like parameter path, with a map of where it fails. Its slow-passage methods have precedent and are cited as such (Taher, Avitabile and Desroches 2022; Avitabile, Desroches and Ermentrout 2022) \[RA, Recommendations\]. It is not "the first model of dying-brain EEG" \[R2, §6 rec. 1\]. The full must-cite list is in Appendix A, and MS14 and gate G8 repeat the search before writing. The research question and the models are unchanged.

**Build order (final).**

1.  Replicate published results, then gate G0: K1–K5 for M2 (K4's network sub-check, K4-net, at MS5 is non-blocking until a source gives the M2 network coupling; section 12.4) and K7–K9 for M3, including network checks; K10, K11 and K8's frequency band run but do not block (section 7.1).

<!-- -->

1.  Run the M2 ramp diagnostic (S2, A3), then gate G1. G1 uses the fitted envelope growth (damped versus non-damped, D8), with the surge_metrics core built at MS1. The move to M3 is expected \[reasoned, not tested\].

2.  Analyse M3 structure (S4, A5, A6), then gate G2. Confirm the headline example (D40) and freeze the classifier and robustness criteria (the replication tolerances are frozen earlier, at the end of MS1).

3.  Run the M3 ramp study (S5) with the S13 headline subset, then gate G6 (MS8); then the regime maps, controls and perturbation runs (S6, S7, S12, S16) and, after the maps, gates G5 and G7 (MS9).

4.  Validate against the network (S8–S10), then gate G4. Run the noise and remaining numerics checks (S11, rest of S13) and evaluate everything (A11).

5.  Build M4 or adaptation only through G2 or G3, with equations taken from primary sources.

6.  Make the figures, run the novelty re-check (G8) and publish the reproducibility release.

All planned runs, including the short MS7 baseline-only runs added in v0.5, take an estimated 3–12 h of wall-clock time on 6 workers with the longer P2 runs of v0.4: the lower end with S9 at its computed time, the upper end with S9 at its 2 h allowance (Table 9.1) \[reasoned, not tested\]; the timing gate in section 9 replaces this estimate.

**Top five risks (final).**

1.  **Gamma reachability.** M3 may not reach ≥ 25 Hz on a plausible path: Devalle reports gamma, Ceni 5–30 Hz (C2). E–I equations with first-order synapses are now read in a primary source (Dumont and Gutkin 2019, section 7.3) \[single source: RB-item 5\]; the instantaneous M4 form of Table 4.1 is printed in MPR App. E but not yet transcribed \[R1, §2.3; RB-item 5\]; the choice is D42. Mitigation: A6 before any ramp work, then G2.

<!-- -->

1.  **Fine-tuning and circularity.** The headline point is Devalle's published gamma point, and the surge may exist only in a narrow window. Mitigation: pre-registered headline and criteria (D40, D35), map fraction, RB4, G5.

<!-- -->

1.  **Ramp and numerical artefacts.** Onset and duration depend on ramp rate, profile, start state and solver, and none of the 12 sampled MPR-family papers tested ramp-rate dependence \[R5, (b)\]; Taher, Avitabile and Desroches 2022 analysed slow passage through a Hopf in an exact QIF model with short-term plasticity (section 12.7). Mitigation: RB3, RB5, RB6, G6.

<!-- -->

1.  **Mapping and identifiability.** Every hypoxia-to-parameter assignment is untested, the direction of Δ is unknown, and η̄ and I cannot be told apart in one population \[R3, §2.5, §3\]. Mitigation: run both Δ paths and NC1–NC3, claim sufficiency only, use M4 for mechanism.

<!-- -->

1.  **Weak targets and detector choices.** Human data come from n = 2 with EMG contamination; relative and absolute power disagree; band edges vary; deterministic runs have zero baseline \[R4, §8(c); R2, §3\]. Mitigation: qualitative targets, both powers reported, RB9, RB10, NC1 (gate G7).

Part 1's former first risk, "M2 cannot sustain a surge", is now handled by G1. **Counts:** 43 D-items (D1–D43, Appendix C), of which 41 remain \[needs decision\] (D28 settled in v0.3; D41 decided in v0.4; D43 counts because its default is set at MS7, as the Conventions allow); 27 rows in the Corrections to Part 1 table (Table 12.1; CP25–CP27 added in v0.5); 24 conflicts (C1–C24, Table 12.2).

**v0.3 update (RA and RB).** Version 0.3 fills gaps using RESULT A (RA) and RESULT B (RB) only. What changed, and which tags moved:

- **K9 and C4:** δ_c = 0.1453… is the ratio Δ/Θ (Devalle Eq. 8), not an absolute Δ. The K9 heterogeneity limit moves from conflict C4 to \[verified\] (R5; RB-item 2a–2b), and K9 now tests Δ/η̄ at η̄ = 1, 2 and 4 (Table 7.1; CP11).

- **K8:** stays \[verified\]; Devalle Eqs. 3 and 6 and the Fig. 3 values are now quoted from the primary text (note under Table 7.1).

- **D28 and C5:** the Lorentzian grid formula matches Taher, Torcini and Olmi 2020 Eq. 8 \[RB-item 6\], so D28 moves from \[needs decision\] to confirmed.

- **C10:** what the Gast erratum corrects is now known: an erroneous scaling of r with τA in Eq. 3.6, whose corrected form is Eq. 7.3; the α values hold only for the depression system Eqs. 7.2–7.3. The corrected equations stay unverified (section 7.3; wording corrected in v0.4).

- **New \[needs decision\]:** D41 (G8 next step; section 12.7) and D42 (M4 form; the E–I equations with first-order synapses, read in the primary source, are in section 7.3). D41 is decided in v0.4.

- **Not upgraded, because RB marks them PARTIAL or UNVERIFIED:** the K6 values (D38), K7 and C15 (Ceni, arXiv v1 only), the \|Z\| formula (D32), the Gast equations, and the published PRX and Chaos texts (section 12.4). RB does not cover D33.

- **Added:** section 7.3 (model-variant equations), CP11–CP13, section 12.7 (G8 result), Appendix E (search log) and Appendix A sources 67–70.

**Changes in v0.4 (review triage).** Version 0.4 applies the triage of four independent reviews (science, consistency, buildability and evidence). Appendix F lists every applied item by its TRIAGE ID, and Table 12.1 records each change to Part 1 (CP14–CP24). The main changes: P2 runs now last until J reaches 0 (5 s + 1.25 T_ramp + 10 s), so the compute estimate is about 3–12 h; K9 uses one protocol at η̄ = 1, 2 and 4; the slow-ramp expectations and the RB3, RB6 and G6 criteria follow delayed-Hopf theory, with an explicit noise floor (D43) and δ₀ applied at t_on; G1 and the surge classes use the sign of envelope growth, the ratio P_G/P_non-G, named mode-D classes with one fixed amplitude threshold and a new S-abs class; J_exit is reported and the P2 ordering is stated as imposed by design; the novelty claim is reframed as a first mechanistic model (D41 decided) and noise robustness (RB2) is a main result; σ calibration, the network code, the classifier core, S4 and the S13 headline subset move to the milestones that need them, and milestones are renamed MS0–MS15; the repository gains restartable, logged, typed and seeded runs. Two review items could not be confirmed in the sources and are unchanged (Appendix F).

**Changes in v0.5 (REVIEW 5).** Version 0.5 is a targeted edit that fixes all 43 findings of one independent sweep of v0.4 (REVIEW 5: SC-01 to SC-10 on the science of the v0.4 rewrites, MC-01 to MC-33 on consistency, tags and layout). Appendix G lists each by its review ID, and Table 12.1 records the changes to sections 2–6 (CP25–CP27). The main changes: RB3(a) is judged only on the runs where δ₀·exp(∫ Re λ dt) stays above the solver or noise floor, its entry–exit prediction is written along the actual path in time and compared with the threshold-crossing onset, and G6 treats only solver dependence as a numerical fault, while profile and δ₀ effects are reported as slow-passage physics; the D43 floor runs use stochastic Heun, and RB6's 5% test varies the Heun step; the K9 maximisation is tagged \[reasoned, not tested\] and gets a τ_d range, a stopping rule and a fallback for G0; the envelope-growth test gets a fit window and a 2-standard-error band, and "non-damped" replaces the D8 sense of "sustained"; A9 gains failure label (f), J_exit is split into J_exit,static and J_exit,run, A8 gains a slowly damped ring test and S-abs a "broadband" flag; MS7 gains short baseline-only mode-N runs, counted under S5; K4-net is non-blocking until a source gives the M2 network coupling; RESULT B items are cited as "RB-item n". Values that no source gives are marked UNVERIFIED and set at MS7 (section 12.4). The research question, the models, the D-item counts (43; 41 open), the 24 conflicts and the compute total (about 3–12 h) are unchanged.

# 2. Scope and hypothesis

Sources: R4 (targets, bands, absence, artefacts), R3 (timescales, negative controls), R2 (novelty, relative versus absolute power), R1 and R5 (readout, frequency).

## 2.1 Research question

Under which combinations of ramp rate, synaptic decay time, coupling, heterogeneity and exogenous drive does a slow, hypoxia-like change of MPR parameters drive a single cortical population through a transient episode of gamma-band oscillation that ends before activity collapses, and under which combinations does no such episode occur? The question concerns the exact mean field of quadratic integrate-and-fire (QIF) neurons, checked against direct QIF network simulations, and concerns dynamics and physiology only.

## 2.2 Hypothesis

A slow rise in mean excitability η̄, optionally with weakening and then failure of the inhibitory coupling J and with a transient drive I(t), carries a single inhibitory MPR population with first-order synapses from a stable focus across a Hopf bifurcation into an oscillatory window and out again. The episode is a gamma surge when the drive is strong and the synaptic decay time τ_d short enough to put the limit-cycle frequency above 25 Hz, heterogeneity stays below its critical value (Δ/(η̄ + I) below about 0.145; a necessary condition only, because at fixed J and τ_d the limit can be lower \[reasoned, not tested; it rests on the UNVERIFIED reading of δ_c as a limit over J and τ_d, note under Table 7.1\]; CP15, CP26), and the time inside the window exceeds the delayed-onset lag of a ramp through a Hopf point. This holds in the deterministic mean field; noise or finite size may remove the delay \[RA, Key finding 4\] \[single source: RA, introduction depth\], so onset-delay claims are conditional on RB1, RB2 and S9 (CP22). It fails when any of these conditions fails. The two-variable population gives only a damped ring, whose length grows as Δ falls (about πr\*²/Δ cycles per e-fold, from the decay rate and ring frequency in section 3.1; CP17) \[reasoned, not tested; from R1, model-class table and slow passage; R1, §2.5 (ring length scales with r\*²/Δ); R3, §2.5; R5, Devalle entry\].

## 2.3 Operational definition of a surge

Report 4 supports one robust target: gamma rises briefly relative to other bands after hypoxia begins, then gives way to suppression \[R4, summary\] \[verified\]. Fold-changes and human timing are not fitting targets \[R4, deliverable (d); R6, §2.5, §6 rec. 5\] \[verified\]; neither is peak frequency \[R4, deliverable (d)\] \[single source\]. Absolute and relative band power must both be reported, because rat and single-case data show relative gamma rising while total power falls \[R2; R4\] \[verified\]. The thresholds below are detection criteria, not fits.

| **Element** | **Definition and default** | **Basis and status** |
| --- | --- | --- |
| Signal | Primary v(t); secondary r(t). Network: mean V_j over non-refractory neurons and binned spike rate. Sampled at 1 kHz. | v is less affected by finite-size fluctuations (Devalle) and is Segneri's spectral readout \[R5\] \[single source\]. 1 kHz = rat EEG rate \[R4\] \[needs decision\] |
| Gamma band G | 25–100 Hz; also Xu γ1 25–55 Hz and γ2 80–150 Hz; peak frequency | Band edges conflict (handoff g, C1) \[needs decision\]. Test: rerun A9 with 30–120 Hz; if \> 5% of map cells change class, report both |
| Relative power | ρ = P_G/P_total, total 1–150 Hz, linear detrend per window (reported). The surge test uses P_G/P_non-G, with P_non-G = P_total − P_G, which, unlike ρ ≤ 1, is not bounded (CP18) | 150 Hz = top of Xu γ2 \[R4\] \[needs decision\] |
| Time–frequency | Hann spectrogram of v; W = 2 s, step 1 s if T_ramp ≥ 60 s; else W = max(0.2 s, T_ramp/30), step W/2 | Xu used 2 s epochs, 1 s overlap \[R4\]; no corpus spectrogram of a transient \[R5\] \[needs decision\]; test W × 0.5, × 2 |
| Baseline | Last 5 s before ramp onset (t = 0 to t_on); mode N and network runs discard 2 s before t = 0, so the baseline is 5 s in every mode (CP14) | \[needs decision\] |
| Threshold, noisy runs (mode N) | Relative surge: P_G/P_non-G ≥ 2 × its baseline value. Absolute surge: P_G ≥ 2 × baseline P_G. A8 reports baseline ρ for the headline and every map cell before the MS7 freeze, from short baseline-only mode-N runs at MS7 (counted under S5; Table 6.2) | 2 = lower end of Xu's 2–391-fold range \[R4\] \[needs decision\]; test 1.5 and 4. A ρ ratio cannot reach 2 when baseline ρ ≥ 0.5, and a flat 1–150 Hz spectrum gives ρ ≈ 0.50 \[reasoned, not tested\] |
| Threshold, deterministic runs (mode D) | A deterministic run at a stable fixed point has no gamma power, so the power ratios and the mode-N classes are undefined. Episode while the Hilbert envelope of band-passed v ≥ 0.1 × A_ref, where A_ref is the limit-cycle amplitude of v at ref_devalle (A5), used as one fixed absolute threshold for every cell and path (D7) | Zero-baseline problem \[reasoned, not tested\]; factor \[needs decision\]; test 0.05 and 0.2; one fixed threshold from v0.4 (CP18) |
| Minimum duration | ≥ 10 consecutive cycles at the running peak frequency; merge gaps shorter than one window. Damped versus non-damped (D8): the growth rate of the Hilbert envelope is fitted from the threshold crossing over the first 10 cycles; the run counts as damped only if the fitted rate is negative by more than 2 standard errors of the fit, and is otherwise non-damped. "Sustained" is kept for the non-terminating classes (S-sus, D-sus) | A cycle count alone does not separate a slowly damped ring: cycles per e-fold ≈ πr\*²/Δ (section 3.1), above 10 at small Δ \[reasoned, not tested\]; ring length scales with r\*²/Δ \[R1, §2.5\]; far shorter than observed episodes of seconds \[R4\] \[needs decision\] |
| Ordering | Episode ends before the run ends. On P2-based paths the oscillation stops where the path leaves the oscillatory region, at J_exit,static \< 0 (from A4); the observed episode ends at J_exit,run (from the classifier), which can lie beyond it under delayed exit; as J → 0⁻ the rate rises (disinhibition), so this ordering is imposed by design, not evidence of suppression \[reasoned, not tested\]. Collapse marker: r \< 10% of baseline (paths without a J ramp) | Hypoxia → surge → suppression → terminal SD \[R3; R4\] \[verified\]; marker \[needs decision\] (D9; CP19) |
| Classes | Mode N: S+ (absolute and relative, transient); S-rel (relative only); S-abs (absolute only; flagged "broadband" when the rise is not a band-limited peak, with no new threshold); S-sus (no termination, either power test); NS (none). Mode D: D-tr (transient episode); D-sus (sustained, no termination); D-none (no episode). A "surge class" is D-tr in mode D, or S+, S-rel or S-abs in mode N. Noisy and deterministic runs agree when D-tr meets a surge class, D-sus meets S-sus, and D-none meets NS | A relative-only rise is consistent with the rat relative-power framing and with the single case after arrest \[reasoned, not tested; R2, §3\]; before arrest the single case also showed an absolute gamma rise \[R4, §2.3\]. Classes revised in v0.4 (CP18); S-abs flag added in v0.5 (CP26) |
| Metrics | Onset time; η̄ at onset; delay η̄\_on − η̄\_H; duration (ms, cycles, fraction of ramp); peak absolute and relative power; peak frequency; class; on P2-based paths, J_exit,run (where the classifier ends the episode; the reported J_exit metric), J_exit,static (where the path leaves the A4 oscillatory region; the reference), their difference (the exit delay), and the post-surge rate, measured after J_exit,run | R1 recommendations; R5 figure plan |

*Table 2.1. Surge definition implemented in mprsurge.analysis.surge_metrics. Limitations: the classifier is power-based, so coherence-only surges, such as frontal coherence without a power increase in 15/16 rats (Lee 2017) \[R4, §2.2\], cannot register, and model NS is not the same as "no surge" in those preparations. Borjigin's early high-gamma component near 130 Hz lies outside 25–100 and 30–120 Hz and is covered only by γ2 (80–150 Hz) \[R4, §2.2, §8(d)\].*

## 2.4 Negative controls

Report 3 proposes hypothermia, deep GABAergic suppression and sympathetic blockade as manipulations predicted to abolish the surge; none has been tested against the gamma surge, and adrenergic blockade prolongs organized brain activity (Li 2015; Tian 2018) \[R3, §2.7\]. It maps the first two to lowered η̄ and raised inhibition \[R3, negative controls\]. Physiology: hypothermia and deep GABAergic suppression (Kentar 2023, Takaoka 1996) \[single source: R3\] (CP4); adrenergic blockade (Li 2015, Tian 2018) \[verified: R2; R3\]; the model mapping is \[reasoned, not tested\].

- **NC1 (primary):** the hypoxia path with η̄ falling by the same amount; J, Δ, τ_d fixed; I = 0. Expected no surge class (NS, or D-none in mode D) at every ramp rate, because Δ/η̄ rises and the steady rate falls \[reasoned, not tested\]. A surge here flags the detector as responding to ramp artefacts.

<!-- -->

- **NC2:** the full path with I(t) = 0 versus I(t) on, mirroring adrenergic blockade (dissociates local from non-local drive).

<!-- -->

- **NC3 (exploratory):** inhibition raised while η̄ falls. Flagged because Hopf oscillations need inhibition and their frequency depends little on J \[R1\], so stronger inhibition alone may not suppress them.

## 2.5 Out of scope

- Consciousness, awareness, near-death experience or afterlife, and any experiential reading of the surge.

<!-- -->

- Fitting fold-changes, phase–amplitude coupling, coherence, connectivity or spatial patterns (need a slow rhythm or several nodes) \[R4\].

<!-- -->

- Terminal spreading depolarization and depolarization block, which the QIF lacks \[R2\]; on P2 the episode ends by exit from the oscillatory region at J_exit,static \< 0 (observed end J_exit,run; Table 2.1), an ordering imposed by design (CP19).

<!-- -->

- Ion, oxygen, ATP or pump variables; post-anoxic EEG over hours \[R2\].

<!-- -->

- Artefact, volume-conduction and medication modelling; neuromodulator identity, including DMT (disputed) \[R3; R4\].

<!-- -->

- Multi-node networks and conductance-based neurons; the Xu raw EEG on Zenodo (D10; default out) \[needs decision\]; Cauchy-noise mean field (equations absent).

## 2.6 Novelty boundary

**Claim (v0.4, D41):** a first mechanistic, exact (MPR) mean-field model of a transient gamma surge under a hypoxia-like parameter path, with a map of where it fails; the slow-passage methods are taken from prior work and cited as precedent \[RA, Recommendations\]; not "the first model of dying-brain EEG" \[R2, recommendations\]. Must cite and distinguish: Kalia et al. 2023 (ion-based neural mass, alpha baseline, EEG filtered to 40 Hz); the ion-exchange Lorentzian mean field (eLife RP 104249), a competing route if a pump variable were added; Ruijter 2017; Zandt 2011; Kager 2000; Wei, Ullah and Schiff 2014; the 2024 bursting-gamma neural mass; Segneri 2020; Ceni 2020; Dehmelt and Machens 2013; Ching 2012 \[R2, neighbours table\]; Taher, Avitabile and Desroches 2022 \[R1, §2.5; R5, SQ4; RA\]; and, from v0.4, Avitabile, Desroches and Ermentrout 2022 and the 2025 noisy-Hopf preprint \[single source: RA\] (method precedents; CP22).

**Smallest still-novel version** \[reasoned, not tested\]: M3, one η̄ ramp through its Hopf point, surge metrics versus ramp rate, a surge/no-surge map in (Δ, τ_d), NC1, and one network overlay at N = 10⁴. **Required re-check:** native Scholar/PubMed searches and three differently worded slow-passage searches before submission \[R2, §6 rec. 6, §8(e); R5, gap statement\]; Part 2 makes this a gate.

# 3. Verified science base

Sources: R1 (equations, assumptions, analytic results), R3 (equations restated, timescales), R4 (empirical targets), R5 (validation values, readout).

## 3.1 MPR equations

**Microscopic network.** Neuron j obeys τ dV_j/dt = V_j² + η_j + Jτ s(t) + I(t), reset from V_p to V_r with V_p = −V_r → ∞; η_j is Lorentzian with centre η̄ and half-width Δ \[R1, equations: MPR Eqs. 1–2, 11; Ceni\] \[verified\]. V_j is the membrane potential, τ the membrane time constant, J the coupling, s the synaptic activation and I a common input.

**Mean field, dimensional form** (for reporting; r = population rate, v = mean potential) \[R1: Ceni Eq. 5, Devalle Eq. 3\] \[verified form; R1 rates placement of τ as medium confidence\]:

    tau * dr/dt = Delta / (pi * tau) + 2 * r * v
    tau * dv/dt = v**2 + eta_bar + J * tau * s + I(t) - (pi * tau * r)**2
    M2:  s = r                       M3:  tau_d * ds/dt = -s + r

**Nondimensional form** (used in code, τ = 1). The 2D case is MPR Eq. 12 \[R1; R3\] \[verified\]; the 3D case sets τ = 1 in the form above \[reasoned, not tested; A4 checks it\]:

    dr/dt = Delta / pi + 2 * r * v
    dv/dt = v**2 + eta_bar + J * s + I(t) - pi**2 * r**2
    M2: s = r        M3: (tau_d / tau) * ds/dt = -s + r

MPR footnote 44 rescales η̃ = η̄/Δ, J̃ = J/√Δ, (r̃, ṽ) = (r, v)/√Δ, t̃ = √Δ t, Ĩ = I/Δ \[R1\] \[single source\].

**Sign convention (fixed).** J is signed and enters as +J s; inhibition is J \< 0 (Ceni, J = −20). Devalle writes −Jτ_m S with J = 21 and drive Θ, so J_Devalle = 21 maps to J = −21 and Θ to η̄ + I \[R1; R5\] \[reasoned, not tested; A4 tests it via K8\].

**Fixed points and linearisation.** v\* = −Δ/(2πr\*) in τ-units (dimensional form v\* = −Δ/(2πτr\*), from setting dr/dt = 0 in the dimensional equation above) \[R1\] \[single source\]; r\* solves (v\*)² + η̄ + I + J r\* − π²(r\*)² = 0, with s\* = r\* in M3 \[reasoned, not tested\]. For M2, λ = 2v\* ± √(2r\*(J − 2π²r\*)), so the damped angular frequency is √(2r\*(2π²r\* − J)) and the decay rate Δ/(πr\*), per τ \[R1\] \[reasoned, not tested by R1\]. Devalle gives ω_c = 2πR\* on the Hopf line for identical neurons \[R1\] \[single source\].

### Assumptions and validity limits

- All-to-all coupling, quenched Lorentzian heterogeneity, N → ∞, peak and reset at ±∞; no weak coupling or time-scale separation needed \[R1, MPR Conclusions\] \[verified\].

<!-- -->

- Attraction to the Ott–Antonsen manifold is argued and numerically supported, proven only for related classes; coverage of QIF networks with synaptic kinetics is unresolved \[R1\] \[single source: unresolved\].

<!-- -->

- Gaussian or uniform heterogeneity has no exact reduction (MPR App. C shows similar dynamics); Wang–Buzsáki networks lose oscillations at about 6% heterogeneity \[R1; R5\] \[verified\].

<!-- -->

- Cauchy noise is exact and Gaussian noise needs at least three pseudocumulants \[R1\] \[single source\]; additive "effective" noise is not consistent \[R1; R5\] \[verified\].

<!-- -->

- Finite N adds shot noise and can make attractors metastable \[R1\] \[single source\].

<!-- -->

- The unforced M2 has only fixed points: stable node, stable focus, and a bistable wedge bounded by saddle-node curves \[R1; R3; R5\] \[verified\].

### Known results used as checks

| **ID** | **Result and values** | **Source, status** |
| --- | --- | --- |
| K1 | M2 saddle-node curve: (η̄, J)\_SN = \[−π²r² − 3Δ²/(2πr)², 2π²r + Δ²/(2π²r³)\] | MPR Fig. 1 \[R1\] single source |
| K2 | M2 node/focus boundary η̄\_f = −\[J/(2π)\]² − (πΔ/J)²; focus to its right | MPR Fig. 1 \[R1\] single source |
| K3 | M2 has stable focus, stable node and saddle at η̄/Δ = −5, J/√Δ = 15 | MPR Fig. 1d \[R1\] single source |
| K4 | Step I = 3 (J = 15, η̄ = −5, Δ = 1) gives damped oscillation to the focus, matching N = 10⁴ network | MPR Fig. 2 \[R1; R5\] verified |
| K5 | Slow sinusoid I₀ = 3, ω = π/20 gives periodic bursting | MPR Fig. 2 \[R1\] single source |
| K6 | Forcing ω = π at η̄ = −2.5, J = 10.5 gives chaos, λ = 0.183 | MPR Fig. 3 \[R1\] single source |
| K7 | M3 supercritical Hopf at τ_d = 4.95 ms (η̄ = 1, Δ = 0.05, J = −20, τ = 10 ms); damped at 3 ms, sustained at 8 ms | Ceni 2020 \[R1; R5\] verified (superseded: Table 7.1; CP1) |
| K8 | M3 gamma oscillations at τ = 10 ms, τ_d = 5 ms, J = −21, η̄ = 4, Δ = 0.3; none at τ_d = 50 ms | Devalle 2017 \[R1; R5\] verified |
| K9 | Oscillations need J \< 0 and τ_d \> 0; vanish above heterogeneity ≈ 0.1453 (Δ_c per R1/Ceni; Δ/Θ per R5/Devalle) | Conflict C4; single source each (superseded: Table 7.1; CP11) |
| K10 | Ceni regime: 5–30 Hz, falling with τ_d, nearly independent of J | \[R1\] single source |

*Table 3.1. Known results used as checks (K1–K10; K11 is added in Table 7.1).*

## 3.2 Parameter table

| **Symbol (code)** | **Meaning** | **Units** | **Baseline** | **Range** | **Source** | **Status** |
| --- | --- | --- | --- | --- | --- | --- |
| τ (tau_ms) | Membrane time constant | ms | 10 | fixed | R1; R5 | verified |
| τ_d (tau_d_ms) | Synaptic decay (M3) | ms | 5 | 1–50, log, 30 | R1 (K7, K8) | values: K8 verified, K7 single source (CP1); range needs decision |
| η̄ (eta_bar) | Mean excitability | — | 4 (ref_devalle) | path η̄\_H − 1.5 → max(4, η̄\_H + 2); lowest Hopf crossing; headline range if no Hopf (D12) | R1; this plan | path needs decision |
| Δ (Delta) | Heterogeneity half-width | — | 0.3 | 0.01–0.6, 30 | R1; R5 | range needs decision |
| J (J) | Signed coupling | — | −21 | −40 to −5, 25; path → 0 | R1 | sign reasoned; range needs decision |
| I (I_drive) | Common (non-local) drive | — | 0 | pulse 0.5–2 | R3 (existence only) | needs decision |
| r, v, s | Rate, mean potential, synapse | r, s: 1/τ; v: — | fixed point | — | R1 | units reasoned |
| T_ramp (T_ramp_s) | Ramp duration | s | 120 | 1–1000, log, 13 | R3 (1–5 min) | needs decision |
| ε (eps) | Ramp rate | 1/τ | derived | — | R1; R5 | verified concept |
| N (N) | Network size | neurons | 10⁴ | 10³–3×10⁴ | R5 | single source |
| V_p, V_r | Peak, reset | — | ±100 | ±200 check | R5 | single source |
| dt (dt_tau) | Network step | τ | 10⁻³ | 10⁻⁴–10⁻³ | R5 (C6) | needs decision |
| σ (sigma) | MF noise on v | — | calibrated | 0.5–2× | R5 (Segneri) | needs decision |

*Table 3.2. Parameters. Validation points: ref_mpr (η̄, J, Δ) = (−5, 15, 1); ref_ceni (1, −20, 0.05), τ_d ∈ {3, 4.95, 8} ms; ref_devalle (4, −21, 0.3), τ_d = 5 ms. η̄\_H = static Hopf value from A4 (the lowest crossing along η̄; D12).*

## 3.3 Mapping model time and output to measurable quantities

- **Time:** one τ-unit = 10 ms, so t_ms = 10 t_τ, f_Hz = 100 f_τ (cycles per τ), r_Hz = 100 r_τ; in footnote-44 units f_Hz = 100 √Δ f̃ \[reasoned, not tested; R1 rates the 1/τ scaling medium-high\]. All gamma results in the reports fix τ = 10 ms \[R1; R5\] \[verified\].

<!-- -->

- **Units:** r is a rate, τ and τ_d are times, v, η̄, Δ, J, I are dimensionless \[reasoned, not tested\]; R1 lists a units table as not found.

<!-- -->

- **Ramp time:** 1 min = 6,000 τ; drift time over gamma period is about 10³–10⁴, supporting a slow ramp \[R3, §2.6\] \[single source\].

<!-- -->

- **Readout:** v(t) is the field-potential proxy and r(t) the rate output \[single source: R5\]. The map from v to EEG is an assumption with no forward model \[reasoned, not tested\]; claims are limited to the rate time course and the gamma share of power \[R4\] \[single source\].

<!-- -->

- **Generator:** a local cortical generator is assumed \[reasoned, not tested\]; a subcortical volume-conduction alternative exists as opinion \[R2, §3; R4, §3\] \[verified\].

## 3.4 Dying-brain facts to be matched

| **Fact and values** | **Source, status** | **Limits** | **Used as** |
| --- | --- | --- | --- |
| Transient gamma surge within 30 s of KCl arrest, before isoelectric EEG; 9/9 rats | Borjigin 2013 \[R2; R3; R4\] verified | Full text unread; ketamine/xylazine | Ordering |
| Rat stages: CAS2 about 5 s; CAS3 coherence \> 15 s; dominant about 40 Hz (25–50) | \[R4\] single source (secondary snippets) | Secondary snippets | Plausibility only |
| Surge in 2 of 4 patients, within seconds of ventilator removal, heart beating; power 2–391-fold at electrodes F7/F8/C3/C4 | Xu 2023 \[R4 full main text; R2; R3\] verified | n = 2; EMG and motion; seizure histories; sedation and S2 duration unknown | Motivation |
| Absence: Xu Pt2, Pt4 (no heart-rate rise); Chawla 2017 15/28 non-brain-dead, 7/7 brain-dead; Norton 2/4 | \[R4\] single source | Processed EEG; small n | Failure regimes |
| Relative gamma rises while total power falls (rat). Single case: absolute gamma rose in the pre-arrest suppression window and fell after arrest, while relative gamma stayed high \[R4, §2.3\]. Xu reports absolute power | \[R2; R4\] verified | Xu Methods: absolute power by DFT \[R4, §2.1\] | Both powers reported |
| Order: hypoxia → surge → suppression → terminal SD; duration about 30 s (KCl) to minutes (asphyxia) | \[R3; R4\] verified | Mode of death matters | Classifier ordering |
| Terminal SD 3.9 min (IQR 2.6–6.3) after final perfusion drop; 13–266 s after silence | Dreier 2018 \[R3; R4\] verified | Abstract and quotations | Upper bound on path length |
| Spontaneous PSC frequency rises within seconds; IPSCs more anoxia-sensitive (cause disputed) | Revah, Fleidervish, Khazipov \[R3\] single source / conflict C11 | Slice | η̄ and J directions |
| Early beta–gamma surge with rhythmic depolarizations in pyramidal cells | Schramm 2020 \[R2; R4\] verified | Abstracts | Depolarizing-drive mapping |
| All seven measured transmitters up at 1 min of asphyxia; adrenergic blockade prolongs activity | Li 2015, Tian 2018 \[R2; R3\] verified | Animal | I(t), NC2 |

*Table 3.3. No fact is a numerical fitting target \[R4, deliverable (d)\].*

## 3.5 Gaps

- Not in the reports: Ceni's closed-form Hopf curves (Eqs. 11–12); Devalle's Eqs. 6 and 8; the M4 (PING) and adaptation equations; the Cauchy-noise mean field; the deterministic Lorentzian grid; a cusp formula; a units table. A4 re-derives the Hopf condition; M4 and adaptation equations must come from primary papers before S14/S15.

<!-- -->

- No measurement of Δ during hypoxia, and no magnitudes for the η̄ ramp, J weakening or sympathetic drive \[R3, §3\].

<!-- -->

- Xu stage durations, sedation and heart-rate values (supplement unread) \[R4\]; QIF runtimes (R5 figures are estimates); MNA length and code policy \[R6\]; Windows support for BifurcationKit.jl and PyRates \[R5\].

# 4. Model specification

Sources: R1 (model classes, Hopf structure, frequency determinants), R5 (excitatory versus inhibitory populations), R3 (§2.5 mapping, §2.6 timescales, §3 conflicts, §6 recommendations), R2 (termination), R4 (heart-rate observation).

## 4.1 Base model M2 and expected primary model M3

**M2** (r, v; s = r) is the requested starting point. It validates the code (K1–K6) and tests whether a damped ring after a slow crossing meets Table 2.1. Expected: fixed points only; ring frequency about the firing rate for J = 0, ring length scaling as r\*²/Δ, lower frequency for J \> 0 \[R1\] \[reasoned, not tested\].

**M3** (r, v, s; J \< 0, τ_d \> 0) is the minimal model with autonomous fast oscillations, via a Hopf bifurcation (Devalle; Ceni) \[verified\]; supercritical per Ceni \[single source: R1; RB-item 3 PARTIAL\]. An excitatory population with exponential synapses shows only foci, whereas an inhibitory one oscillates for τ_s roughly 0.1–100 (Ferrara) \[R5\] \[single source\]. M3 is read as an inhibition-dominated (ING) local circuit. An exact mean field is used because it tracks within-population synchrony: standard Wilson–Cowan-type masses "cannot describe ERD/ERS" \[R2, §2.2\] \[single source\].

**Interpretive conflict.** The hypoxia evidence concerns pyramidal depolarization and excitatory release, and interneurons may lose excitatory drive early \[R3, §2.2, §3\]. Ramping η̄ in an inhibitory population assumes interneuron drive rises \[reasoned, not tested\]; if this is rejected, gate G2 moves to M4.

## 4.2 Extensions

| **ID** | **Model** | **Dim.** | **Bifurcation** | **Frequency determinants** | **Source** | **Role** |
| --- | --- | --- | --- | --- | --- | --- |
| M2 | MPR, instantaneous synapses | 2 | None sustained; damped focus; forced bursting, chaos | ≈ 2πr\* (J = 0); decay Δ/(πr\*) \[reasoned\] | MPR 2015 | Validation; ring test |
| M3 | Inhibitory + first-order synapse (ING) | 3 | Supercritical Hopf (Ceni) | τ_d (frequency falls with τ_d); drive; Δ (none above Δ/η̄ ≈ 0.145, a necessary condition; CP11, CP15); J weak | Devalle 2017; Ceni 2020 \[verified: Hopf\]; supercritical per Ceni \[single source\] | Expected primary |
| M4 | E–I, instantaneous (PING) | 4 | Mostly supercritical; one subcritical example | Drive to E; E–I couplings; τ_m of E and I | Segneri 2020; MPR App. E \[single source: R1\] | Robustness; primary if G2 |
| M3a | \+ synaptic depression or SFA | 4 | Subcritical Hopf; fold of cycles; bursting–focus bistability | Adaptation strength α, timescale, input | Gast 2020 + erratum \[single source: R1\] | Only if G3 |
| M3b | Exact Izhikevich adaptation | 3–4 | Hopf, double Hopf, bursting | Adaptation jump, η̄, Δ | Chen & Campbell 2022 (abstract) \[single source: R1\] | Alternative to M3a |

*Table 4.1. From the R1 model-class table. Adaptation variants mainly give slow bursting, not gamma \[R1\]. Gast et al. use a global-adaptation approximation and their α values hold only for the corrected equations \[R1; R5\] \[verified\]; what the erratum corrects is settled in content (C10, Table 12.2; v0.4). Two-population, STP-drift, delay and gap-junction routes are not planned.*

## 4.3 Decision rules

| **Gate** | **When** | **Rule** | **Expected** |
| --- | --- | --- | --- |
| G1: M2 → M3 | After A1–A3, S1–S2 | Stay with M2 only if some path with Δ \> 0, τ = 10 ms gives a non-damped episode in G over ≥ 10 cycles (D8: the fitted envelope growth is not negative by more than 2 standard errors); M2 has no amplitude threshold, so the fit window starts at the first of the cycles counted in G \[reasoned, not tested\]. Otherwise move; keep M2 as the damped-ring comparison. M2 has no limit cycle and so no A_ref, so G1 uses no amplitude threshold (CP17). | Move \[reasoned; predicted by R1, R2, R3, R5\] |
| G2: M3 → M4 | After A4–A6 | Move if (a) no limit cycle ≥ 25 Hz with Δ below critical within Table 3.2 ranges, (b) no η̄ path enters the oscillatory region from a stable focus, or (c) the interneuron-drive assumption is rejected. | Stay; M4 as robustness only \[R1; R5\]. (c) \[needs decision\]: not rejected |
| G3: + adaptation | After A7, A9 | Add M3a/M3b only if every onset is S-sus or D-sus and termination by J → 0 is rejected. | Not triggered. R1: only if the surge must end with drive held fixed |
| G4: network | After S8–S9 | If networks at N = 10⁴ and 3×10⁴ miss the surge, report a finite-size limitation; keep the model. | Agreement for N \> 10⁴ (Ferrara) \[R5\] |

*Table 4.2. Decision rules (gates G1–G4).*

## 4.4 Hypoxia mapping

Experiments show rising extracellular K⁺ and depolarization, an early rise in excitatory synaptic activity, early loss of inhibitory transmission, and eventual depolarization block; assigning these to model scalars is \[reasoned, not tested\] throughout \[R3, §2.5\].

| **Parameter** | **Direction and timescale** | **Evidence (R3)** | **Quality (R3)** | **Plan** |
| --- | --- | --- | --- | --- |
| η̄ | Rises during the window (ramp about 1–5 min; surge in first tens of seconds to about 2 min); collapses at terminal SD | K⁺ rise; glutamate-dependent PSC rise (Revah, Fleidervish); V_m rise triggers spiking (Zandt 2013); collapse (Dreier 2018) | High for direction in window (animal/slice); high for collapse | Lead ramp |
| \|J\| (inhibition) | Weakens early, then all transmission fails | IPSCs more anoxia-sensitive (Khazipov 1995) | Medium: early inhibitory-transmission loss well supported; assigning it to scalar J is \[reasoned, not tested\] | P2: J → 0; ends the episode |
| Δ | Unknown; plausibly rises | None measured | Reasoned; pivotal | Both directions \[needs decision\] |
| Adaptation | Opposing (AHP loss versus K_ATP opening) | Both documented | Net sign reasoned | Only via G3 |
| τ_d | Not established | IPSPs preferentially depressed | Reasoned | Static sweep only |
| I(t) | Transient rise (sympathetic, neurochemical) | Li 2015; Tian 2018; Xu 2023 framing | High that real; medium weight | P3; NC2 |

*Table 4.3. Hypoxia mapping (R3, §2.5).*

### Paths

Each ramped parameter follows p(t) = p_start + (p_end − p_start) g((t − t_on)/T), g linear (clipped to \[0, 1\]) by default or sigmoid (logistic with k = 10, rescaled to g(0) = 0, g(1) = 1). Ramp shape changes the onset threshold in slow-passage theory \[R1; R5\] \[verified\]; its effect in MPR models is \[reasoned, not tested\]. Defaults are \[needs decision\], tested in A7 and A9.

- **P1 (path_eta):** η̄ from η̄\_H − 1.5 to max(4, η̄\_H + 2) over T_ramp; ends at Devalle's gamma point (K8). η̄\_H is the lowest Hopf crossing along η̄; a cell with no Hopf point uses the headline cell's eta_start and eta_peak (D12; CP20).

<!-- -->

- **P2 (path_hypoxia), main:** P1 plus J from J0 to 0, starting at t_on + 0.25 T_ramp, lasting T_ramp, so J reaches 0 at t_on + 1.25 T_ramp; the run's 10 s hold starts only then (CP14). M3 needs inhibition to oscillate \[R1\]. R2 lists synaptic failure as one of three ways to end the surge, because QIF lacks depolarization block \[R2, §6 rec. 4\]; this plan chooses it \[reasoned, not tested\]. The path leaves the oscillatory region at J_exit,static \< 0 (A4), before J = 0; the observed episode ends at J_exit,run (Table 2.1) (CP19).

<!-- -->

- **P3 (path_drive):** P2 plus a trapezoid I(t) from t_on (rise 0.1, plateau 0.3, fall 0.1 × T_ramp), I_amp ∈ {0.5, 1, 2}.

<!-- -->

- **P4a, P4b (path_delta_up, path_delta_down):** P2 with Δ × 1.5 or × 2/3 over T_ramp.

<!-- -->

- **P5 (path_updown):** η̄ up over T_ramp, then down over T_ramp, J fixed (hysteresis).

## 4.5 Competing hypotheses: local hypoxia versus non-local drive

Report 3 recommends a local parameter change (η̄ dominant) plus a separable non-local drive I(t) \[R3, §6; §8(c)\] \[single source\]. Report 4 notes that the two Xu patients without a surge had no heart-rate rise (authors' interpretation, n = 4) \[R4\] \[single source\]; Report 3's quantitative heart-rate claim is press-based and not used. Hypotheses: **H-local** (P1/P2 with I = 0 give a surge); **H-drive** (surge only with I on); **H-mixed** (I widens the region or shortens delay).

**Structural caveat** \[reasoned, not tested\]: in one population, η̄ and I enter the same term (v² + η̄ + I), so local and non-local drive differ only in time course. M3 can test whether drive timing matters, not where the drive comes from; that separation needs M4. Part 2 must carry this into the risks.

# 5. Analysis plan

Sources: R1 (checks K1–K10, slow-passage predictions), R5 (tools, figure conventions, ramp-rate practice), R6 (an analytical result confirmed against network simulation), R7 (failure regimes as prominent as surge regimes).

## 5.1 Continuation tools on Windows

| **Tool** | **Status (R5)** | **Use** |
| --- | --- | --- |
| numpy/scipy (roots, brentq, eigenvalues) | Cross-platform \[reasoned\] | A1, A2, A4, A6; no periodic orbits |
| BifurcationKit.jl | Periodic orbits, fold/Hopf detection, two-parameter and codim-2 continuation; Windows not stated | A5 default \[needs decision\] |
| PyRates + PyCoBi | QIF template; continuation via Auto-07p | Fallback |
| AUTO-07p | Windows via MSYS2; CI on Ubuntu | FLAG: MSYS2 or WSL2 (Linux) |
| XPPAUT | Needs X11 server (Xming) | FLAG: fallback only |
| MatCont | MATLAB only | FLAG: needs MATLAB; not planned |
| PyDSTool | Corrected: unmaintained, broken on Python ≥ 3.10 | Do not use |

*Table 5.1. \[R5, tool table; R5, verification list\]. Test for the default: BifurcationKit.jl reproduces K7 and its supercritical type on the Windows machine within one working day; otherwise WSL2 + PyCoBi/AUTO-07p (flagged), or S4 alone.*

## 5.2 Steps

Each step has scripts/run\_\<ID\>.py and writes to results/\<ID\>/. Fixed points of M2 and M3 come from one routine: substituting v\* into dv/dt = 0 gives −π² r⁴ + J r³ + (η̄ + I) r² + Δ²/(4π²) = 0, solved with numpy.roots for positive real r \[reasoned, not tested\].

### A1. M2 fixed points and stability

- **Inputs and method:** Δ = 1; η̄/Δ ∈ \[−10, 2\] (241) × J/√Δ ∈ \[0, 20\] (201). Quartic roots; Jacobian \[\[2v, 2r\], \[J − 2π²r, 2v\]\]; classify node, focus, saddle.

<!-- -->

- **Check:** K1 and K2 boundaries within one grid cell of the formulas; K3 gives focus, node and saddle. Record whether a node region exists for Δ \> 0 (conflict C9).

<!-- -->

- **Feeds:** results/A1/a1_fixedpoints_2d.npz; FS1.

### A2. M2 ring test

- **Inputs and method:** Stable-focus branch from A1, τ = 10 ms. Ring frequency (Hz), fitted envelope decay rate and cycles per e-fold; map where the ring is in G. G1 uses the fitted envelope growth (D8: damped only if negative by more than 2 standard errors), not A_min, because M2 has no limit cycle and so no A_ref (CP17).

<!-- -->

- **Check:** Damped-sinusoid fit to the tail of the S1 step response (K4), after the envelope falls below a stated fraction of the initial jump (fraction set with D34), matches the linear frequency and decay within 2% (CP23).

<!-- -->

- **Feeds:** results/A2/a2_ring_map.npz; G1; FS1.

### A3. M2 slow ramp through the saddle-node

- **Inputs and method:** S2 runs at J/√Δ = 15; jump time, η̄ at jump and ring class versus T_ramp.

<!-- -->

- **Check:** Slowest ramp jumps within one step of the A1 saddle-node value; K5 bursting reproduced in S1.

<!-- -->

- **Feeds:** results/A3/a3_sn_ramp.parquet; G1; F4 comparison curve.

### A4. M3 fixed points and Hopf curves

- **Inputs and method:** Jacobian in τ-units with β = τ/τ_d: \[\[2v, 2r, 0\], \[−2π²r, 2v, J\], \[β, 0, −β\]\]. Characteristic polynomial λ³ + a₁λ² + a₂λ + a₃; Hopf where a₁a₂ = a₃ with a₁, a₃ \> 0 \[reasoned, not tested\]. Trace η̄\_H in planes (η̄, τ_d), (η̄, Δ), (η̄, J) with brentq; record Im λ as a first frequency estimate. For A7, also evaluate the leading eigenvalues λ along each S5 path, on an η̄ grid whose spacing is not set yet (UNVERIFIED; fixed in configs/A4.yaml before criteria-frozen at MS7); one step of this grid is the "A4 grid step" of A7 and RB3(a) (CP25).

<!-- -->

- **Check:** K7: τ_d^(H) = 4.95 ± 0.05 ms. K9: at η̄ = 1, 2 and 4, the largest Δ/η̄ on the Hopf curve over τ_d (the D11 range, 1–50 ms) and J is 0.1453 ± 0.002, with the maximiser inside the ranges searched \[reasoned, not tested\]; the widening, stopping and fallback rules are in Table 7.1 (CP15, CP26). K8: oscillatory at ref_devalle, not at τ_d = 50 ms. No Hopf for J \> 0. A failure means the 3D equations or the J mapping are wrong.

<!-- -->

- **Feeds:** results/A4/a4_hopf_curves.npz; F3.

### A5. M3 limit cycles and criticality

- **Inputs and method:** Periodic-orbit continuation from A4 Hopf points (η̄ at ref_devalle; τ_d at ref_ceni): amplitude, period, stability, folds of cycles, criticality. Cross-check with S4: near a supercritical Hopf, squared amplitude grows linearly and there is no hysteresis \[reasoned, not tested\].

<!-- -->

- **Check:** Supercritical at ref_ceni (K7); continuation and S4 amplitudes within 2%, excluding S4 points within one step of η̄\_H (critical slowing), which are reported separately (CP23). Output A_ref.

<!-- -->

- **Feeds:** results/A5/a5_cycles.npz; F2.

### A6. M3 frequency map

- **Inputs and method:** Limit-cycle frequency over (η̄, τ_d) for Δ ∈ {0.05, 0.1, 0.3}, J = −21, and over (η̄, J) at τ_d = 5 ms; contours at 25 and 100 Hz. Resolves C2. Method: frequencies come from the A5 continuation branches; no brute-force grid is planned, and any brute-force part gets a stated grid and a Table 9.1 row before it runs (CP23).

<!-- -->

- **Check:** K10 in the Ceni regime (5–30 Hz, falling with τ_d, flat in J); band G at ref_devalle (K8).

<!-- -->

- **Feeds:** results/A6/a6_freq_map.npz; G2; F3.

### A7. Slow-ramp analysis

- **Inputs and method:** S5 runs (MS8) and S6 runs (MS9); A7 is completed in two parts, at MS8 and MS9 (Table 11.1). Per run: η̄ at onset, delay η̄\_on − η̄\_H, duration, peak power and frequency, class; for P5 the offset on the way down and the hysteresis width. Memory: start distance {0.5, 1.5, 3}. Profile: linear versus sigmoid. Noise floor: a small additive noise floor on v at the D43 levels, integrated with the mode-N stochastic Heun scheme (section 6.2), not with DOP853. Precedent: Devalle Fig. 6 uses slow periodic forcing with decreasing period, "the nearest analogue to a rate-dependence test" in MPR work \[R5, SQ4\]. All metrics against ε (log axis) with the quasi-static value as reference.

<!-- -->

- **Expected:** onset is delayed past η̄\_H and depends on the starting state (memory effect), with up/down asymmetry \[R1, §2.5; R5, SQ4\]. In exact arithmetic the delay is not expected to vanish as ε falls; in a noise-free double-precision run the delay at slow ramps is set by the solver's error floor and δ₀, so it moves with tolerance \[reasoned, not tested\]. Noise removes the delay \[RA, Key finding 4\] \[single source: RA, introduction depth\]. The onset is predicted from the A4 eigenvalues by the entry–exit relation written along the actual path in time, ∫ Re λ(η̄(t′), J(t′)) dt′ = 0, taken from t_on (where δ₀ is applied), with λ the leading eigenvalue at the path's parameters at time t′ (J is fixed on P1 and P5; any other ramped parameter is also taken at its path value). This form holds for every profile, linear or sigmoid, and through P2's J ramp. The onset compared with a run is t_pred, the time at which the growing mode, started from δ₀ at t_on, reaches the onset amplitude 0.1 × A_ref, that is δ₀·exp(∫ from t_on to t_pred of Re λ dt′) = 0.1 × A_ref \[reasoned, not tested; the general form is not in the reports; delayed-Hopf theory via the v0.4 review, TRIAGE T03\] (CP25). No noise-floor scaling law is entered: none was confirmed in a primary source (UNVERIFIED). A low-frequency Hopf can show onset advance instead of delay \[R5, SQ4, Baer et al. 1989\] (CP16).

<!-- -->

- **Check:** RB3(a) is judged only on the runs inside its range: those where δ₀·exp(∫ Re λ dt′), integrated from t_on along the path with the A4 eigenvalues, stays above the floor until t_pred (the solver error floor in noise-free runs; the D43 level in floored runs; floor values UNVERIFIED, fixed in configs/robustness_criteria.yaml at MS7). A4 computes this, which gives the ramp-rate (T_ramp) range over which RB3(a) applies. On those runs the threshold-crossing onset (the envelope first reaching 0.1 × A_ref, Table 2.1) must match t_pred within one A4 grid step in η̄ (A4). Outside the range the delay is set by the floor, as expected above, and is reported, not failed. These rules are \[reasoned, not tested\] and are fixed before criteria-frozen (MS7) (CP25). With the D43 floor, integrated with stochastic Heun, the headline delay changes \< 5% across the Heun dt ladder of S13 (RB6) and shrinks as the floor rises \[reasoned, not tested; RA reports only that noise removes the delay\]; otherwise it is a numerical artefact. A noise-free DOP853 delay that moves with rtol is expected and is reported, not failed.

<!-- -->

- **Feeds:** results/A7/a7_ramp_metrics.parquet; F4.

### A8. Surge classifier and validation

- **Inputs and method:** Implement surge_metrics per Table 2.1. Unit tests (seeded): 40 Hz burst in seeded noise with known on/off; 20 → 60 Hz chirp; 5-cycle damped ring (must be NS or D-none, with envelope growth \< 0); a slowly damped ring with more than 10 cycles above threshold and negative fitted growth (must be NS or D-none: it passes the cycle count, so only the D8 envelope-growth test separates it); pure ramp trend (must be NS). Sensitivity: band 30–120 Hz, factors 1.5 and 4, A_min factor 0.05 and 0.2, window × 0.5 and × 2. The core functions (band power, envelope, envelope-growth fit, cycle count) and their synthetic tests are built at MS1; A8 adds the classes, A_ref, the baseline ρ report and the sensitivity runs at MS7 (CP17).

<!-- -->

- **Check:** On/off within one window step; frequency within 1/W.

<!-- -->

- **Feeds:** tests/test_surge_metrics.py; results/A8/a8_sensitivity.csv; FS5.

### A9. Regime map

- **Inputs and method:** Classify S7 cells; label cells without a surge class: (a) Δ above critical, (b) τ_d outside the Hopf window, (c) frequency \< 25 Hz, (d) ramp too fast for 10 cycles, (e) no exit (D-sus or S-sus), (f) amplitude below the fixed threshold (the cell oscillates inside the A4 region, but its envelope never reaches 0.1 × A_ref). Failed runs are labelled failed, not NS (section 10.4). Overlay Hopf curves, 25 Hz contour, path arrows and example markers (Devalle Fig. 4 style \[R5\]); failure regions get equal prominence \[R7\].

<!-- -->

- **Check:** Every cell with a surge class lies where the path crosses the A4 oscillatory region (exceptions flagged as ramp artefacts); the noisy subgrid agrees with the deterministic class, under the Table 2.1 correspondence, in ≥ 90% of cells \[needs decision\].

<!-- -->

- **Feeds:** results/A9/a9_regime_map.parquet; F5, F6.

### A10. Negative controls and drive dissociation

- **Inputs and method:** Classify NC1–NC3 (S12) across ramp rates; compare P2 and P3 regions (NC2).

<!-- -->

- **Check:** NC1 has no surge class anywhere (NS or D-none); any NC1 surge triggers a review of A8 thresholds before results are used.

<!-- -->

- **Feeds:** results/A10/a10_controls.csv; F6.

# 6. Simulation plan

Sources: R5 (integrators, steps, N, threshold/reset, refractory correction, heterogeneity sampling, noise, compute estimates, reproducibility), R1 (network checks), R7 (reporting integrator, tolerances and code), R6 (figure budget).

## 6.1 Environment (Windows, PowerShell)

    py -3.11 -m venv .venv
    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # once, if activation is blocked
    .\.venv\Scripts\Activate.ps1
    python -m pip install numpy scipy numba matplotlib pyyaml pandas pyarrow pytest
    python -m pip freeze > environment\requirements-lock.txt
    julia -e "using Pkg; Pkg.add(\"BifurcationKit\")"      # A5 only
    python -m mprsurge.run --config configs\S5.yaml --workers 6
    python -m pytest tests

Note (v0.4): the commands above are superseded by the README in section 10.2 (CP8, CP23): Julia is set up from setup_julia.jl, the lock file is written with Out-File -Encoding utf8, and installs use pinned versions.

Python ≥ 3.11 because R5 rejects tools broken on 3.10+. Windows starts worker processes by spawning, so entry scripts need an if \_\_name\_\_ == "\_\_main\_\_": guard \[reasoned, not tested\]. Only AUTO-07p (MSYS2/WSL2), XPPAUT (X11) and MatCont (MATLAB) are flagged; none is required.

## 6.2 Mean-field integration

- **Mode D:** solve_ivp DOP853, rtol 10⁻¹⁰, atol 10⁻¹², max_step 0.05 τ (0.5 ms), output every 0.1 τ (1 ms); Radau cross-check. Basis: Taher used Dormand–Prince at 10⁻¹²; R5 suggests explicit adaptive plus implicit cross-check \[R5\] \[needs decision; test S13\].

<!-- -->

- **Breakpoints:** integrate piecewise between ramp corners so no step crosses a kink \[reasoned, not tested\].

<!-- -->

- **Initial state:** exact stable fixed point at the start parameters; δ₀ = 10⁻⁶ is added on v at t_on, not at t = 0, where it would decay to the solver floor during the 5 s baseline \[needs decision; D26; CP16\]. The ramp's derivative kink at t_on also seeds the onset \[reasoned, not tested\]. S13 repeats with 10⁻⁹ and 10⁻³ because slow-passage onset depends on the starting state \[R1; R5\] \[verified that it does\].

<!-- -->

- **Mode N:** stochastic Heun, step 10⁻³ τ (0.01 ms), Numba, as Segneri did for the noisy neural mass \[R5\] \[single source\]. The D43 noise-floor runs of A7 also use this scheme, and RB6 varies its step (S13; CP25).

<!-- -->

- **Durations:** mode D: 5 s baseline, the ramp, then a 10 s hold that starts after the last ramp ends: after T_ramp, or after 1.25 T_ramp on P2 and the paths built on it (P3, P4a, P4b, NC2), when J reaches 0 (CP14). Mode N and network: 2 s discarded before t = 0, so the baseline stays 5 s (CP14). P5 doubles T_ramp. The headline P2 run (T_ramp 120 s) lasts 165 s = 16,500 τ. Corpus discards were 1–10 s \[R5\] \[needs decision\].

## 6.3 QIF network comparison

| **Setting** | **Default** | **Basis and status** |
| --- | --- | --- |
| Integrator | Forward Euler, dt = 10⁻³ τ | Corpus norm; 10⁻³ (Chen & Campbell) versus 10⁻⁴ (MPR, Taher) \[R5\] \[needs decision\]; S13 down to 10⁻⁴ |
| Peak, reset | V_p = 100, V_r = −100; check ±200 | MPR App. A, Segneri; Chen & Campbell ±200 \[single source: R5\] |
| Refractory correction | At crossing, hold 2/V_j; count the spike 1/V_j after crossing | MPR App. A; Segneri 2/V_j \[single source: R5\] |
| Synapse (M3) | s ← s + (τ/τ_d)(−s dt + n_spikes/N) per step | Discretized τ_d ds/dt = −s + r \[reasoned, not tested\] |
| Synapse (M2, K4-net) | Not specified: no attached source gives the M2 network coupling (T51; section 12.4) | UNVERIFIED. K4-net is non-blocking until a source gives it (Table 7.1, G0) |
| Heterogeneity | η_j = η̄ + Δ tan(π(2j − N − 1)/(2(N + 1))), j = 1…N | Deterministic sampling as in MPR and Taher \[R5\]; formula = inverse Lorentzian at even quantiles \[reasoned, not tested\]; confirmed against Taher, Torcini, Olmi 2020 Eq. 8 \[RB-item 6\] (D28) |
| Random variant | η_j = η̄ + Δ tan(π(u_j − 1/2)), u_j uniform, seeded | Chen & Campbell practice \[R5\] \[single source\] |
| Ramping η̄ or Δ | Fixed offsets q_j = (η_j − η̄)/Δ; η_j(t) = η̄(t) + Δ(t) q_j | \[reasoned, not tested\] |
| Other shapes (S10) | Gaussian, uniform; half-width at half maximum = Δ (uniform: half-range = Δ, the literal HWHM reading; D29) | MPR App. C \[R1; R5\]; matching \[needs decision\] |
| Initial state | V uniform on \[−100, 100\]; discard 2 s before t = 0 (CP14) | Segneri \[R5\] \[single source\] |
| Readouts | r_N: spikes per 1 ms bin / (N × bin); v_N: mean V_j over non-refractory neurons; raster of 300 neurons | Devalle mean potential; MPR raster \[R5\]; exclusion \[needs decision\] |
| Size | N = 10⁴; sweep {10³, 3×10³, 10⁴, 3×10⁴}; one 5×10⁴ run for K8 | Agreement very good for N \> 10⁴ (Ferrara) \[R5\] \[single source\] |
| Implementation | Numba, float64, no fastmath; one run per process, 6 processes | Floating-point effects can change results \[R7\]; R5 compute table |

*Table 6.1. Network settings (mprsurge.qif_network). R5 estimates 2–5 min per N = 10⁴ run of 10⁴ τ on this CPU \[reasoned, not tested\].*

## 6.4 Noise models

- **None** (mode D) for bifurcation-linked analysis.

<!-- -->

- **Additive white noise on v** in the mean field, stated as phenomenological as Segneri did \[R5; R1\] \[verified\]. σ is calibrated at MS5, after A4 gives η̄\_H, so the baseline std of v matches one N = 10⁴ network baseline run at the P2 start state of ref_devalle (η̄\_H − 1.5, J = −21, Δ = 0.3, τ_d = 5 ms); σ is stored in a committed config and frozen with the criteria at MS7, and S8 checks it (CP21); also 0.5σ and 2σ \[needs decision\].

<!-- -->

- **Finite-size fluctuations** in network runs (S8, S9).

<!-- -->

- **Not implemented:** Cauchy noise and higher-order Gaussian reductions (equations absent, 3.5).

## 6.5 Runs

| **ID** | **Purpose** | **Model** | **What varies** | **Feeds** |
| --- | --- | --- | --- | --- |
| S1 | M2 validation | M2 MF; network N = 10⁴ for K4-net (at MS5, once a source gives the M2 network coupling; UNVERIFIED, section 12.4) | K4 step, K5 sinusoid, K6 chaos | A2, A3; FS1 |
| S2 | M2 ramps through saddle-node | M2 MF | η̄ from 1 below the lower fold to 1 above the upper fold (A1); T_ramp 13 values, 1–1000 s log | A3; G1 |
| S3 | M3 validation | M3 MF + network N = 10⁴; N = 5×10⁴ for K8 | ref_ceni τ_d {3, 4.95, 8} ms; ref_devalle τ_d {5, 50} ms; 10 s | A4–A6; FS2 |
| S4 | Quasi-static sweeps | M3 MF; network at 15 steps | η̄\_H − 2 to η̄\_H + 4, 61 steps up then down, 2 s each (1 s discarded) | A5; F2 |
| S5 | Ramp-rate sweep | M3 MF (D, N) | P1, P2, P5 × 13 T_ramp × {linear, sigmoid}; P1 × start distance {0.5, 1.5, 3}; P2 × 10 noise seeds; plus the headline cell (P2, ref_devalle, T_ramp 120 s, linear, I = 0). Plus short baseline-only mode-N runs (7 s: the 2 s discard and the 5 s baseline, no ramp; 10 seeds) for the headline cell and every map-1 and map-2 cell, run at MS7 for the A8 baseline ρ report (v0.5) | A7, A8; F4 |
| S6 | Drive and Δ paths | M3 MF (D) | P3 (I_amp 0.5, 1, 2), P4a, P4b × T_ramp {10, 30, 120, 300} s | A7, A10; F6 |
| S7 | Regime maps | M3 MF (D); noisy subgrid | Map 1: Δ 0.01–0.6 (30) × τ_d 1–50 ms (30, log), P2, T_ramp 120 s. Map 2: J0 −40 to −5 (25) × T_ramp (13), Δ 0.3, τ_d 5 ms. Noisy 15 × 15 subgrid of map 1 | A9; F5, F6 |
| S8 | Network overlays | M3 network N = 10⁴ | P2 at ref_devalle, T_ramp {10, 120} s, 3 seeds; 4 map cells at T_ramp 30 s | F1, F5; σ check (σ is set at MS5) |
| S9 | Finite size | M3 network | N {10³, 3×10³, 10⁴, 3×10⁴} × 10 seeds; P2, T_ramp 60 s | FS3 |
| S10 | Heterogeneity shape | M3 network N = 10⁴ | Lorentzian, Gaussian, uniform × 3 seeds; P2, 60 s | FS3 |
| S11 | Noise level | M3 MF (N) | σ {0.5, 1, 2} × T_ramp {10, 30, 120, 300} s × 10 seeds | F4, FS3 |
| S12 | Negative controls | M3 MF; network for NC1 | NC1–NC3 × 13 T_ramp; NC1 at 5 map cells; NC1 network 1 seed, 120 s | A10; F6 |
| S13 | Numerical checks | M3 MF and network | Mean field, P2 at ref_devalle, T_ramp 10, 120 (headline) and 316 s: DOP853 vs Radau; rtol {10⁻⁸, 10⁻¹⁰, 10⁻¹²}; δ₀ {10⁻⁹, 10⁻⁶, 10⁻³}; D43 floor levels. Network, 10 s ramp: dt {10⁻³, 5×10⁻⁴, 2.5×10⁻⁴, 10⁻⁴}; V_p ±100 vs ±200, the ±200 check also at dt 10⁻⁴. Window × {0.5, 2}. The D43 floor runs use stochastic Heun on a dt ladder from the mode-N default 10⁻³ τ (lower rungs UNVERIFIED; set in configs/S13.yaml before MS7). The headline subset (rtol ladder, Radau, δ₀ ladder, and the floor with its Heun dt ladder at 120 s) runs at MS8 (CP23) | FS4 |
| S14 | PING (G2 or robustness) | M4 | Specified once M4 equations are taken from primary sources | FS6 |
| S15 | Adaptation (G3 only) | M3a/M3b | Specified from primary sources | FS6 |
| S16 | Local perturbation (RB4) | M3 MF | ±10% one at a time on eta_start, eta_peak, J0, Delta, tau_d_ms, J_lag_frac, J_T_frac (14 runs); 64-point Latin hypercube (RB4, Table 7.2); run at MS9 | A11 (RB4); G5 |

*Table 6.2. Runs; outputs go to results/\<ID\>/. Ramp-rate sweeps over orders of magnitude with a quasi-static limit follow R1 and R5; finite-size values follow R5's figure plan. Grid resolution is \[needs decision\]: accept if halving the spacing near the map boundary moves it by less than one cell.*

## 6.6 Seeds and run records

- Each config has seeds.root_seed (default 20261008); child seeds from numpy.random.SeedSequence(root_seed).spawn(n), spawn key stored. Randomness enters only through initial potentials, random heterogeneity and noise.

<!-- -->

- Each run writes results/\<RUN_ID\>/\<run_id\>\_\<hash12\>.npz (1 ms series, rasters) and a .json record: resolved config, config hash, seed and spawn key, git commit, Python and package versions, OS and CPU, solver settings, wall time, warnings.

<!-- -->

- Each run also writes a Nordlie-format parameter table from its config (make_param_table), because parameters are easily omitted from text \[R7, Pauli 2018; R5\] \[verified\]. Figures come only from scripts reading stored results (Sandve rules) \[R5; R7\] \[verified\].

<!-- -->

- Deliverable consequence: no sampled MPR paper reported seeds or versions \[R5\]; JCNS requires code and parameter sets and PLOS CB requires code \[R7, §2.6\] \[single source; CP5\]; MNA has no code mandate on the pages read \[R6\]. Code and parameter files will be public and versioned.

## 6.7 Figure budget

Report 6 infers about 15–20 pages and 5–6 figures, with at least one analytical result confirmed against network simulation \[R6\] \[single source: R6\]. Sections 5 and 6 therefore feed six main figures (F1–F6) and supplementary figures FS1–FS6 (handoff f).

# Part 2 preflight

**Files read.** All eight files were read in full: Part 1 and R1–R7. Report headings are images, so the section numbers cited in Part 2 were checked against page images. No file was only partly read.

**Inherited and found items.** The 31 inherited \[needs decision\] items (D1–D31) are carried into Appendix C. Ten corrections to Part 1 are listed in Table 12.1: nine conflicts between Part 1 and the reports and one engineering correction (CP8). v0.3 adds CP11–CP12 from RB and CP13 from the repository review; v0.4 adds CP14–CP24 from the review triage, and v0.5 adds CP25–CP27 from REVIEW 5. None changes a model; CP7 adds panel F5c, CP11 changes the K9 criterion, and v0.4 renames the milestones MS0–MS15.

**Additions in Part 2.** Replication step A0 with a new target K11, local-perturbation run S16, robustness step A11, one script per figure, and gates G0 and G5–G8.

**Citation note.** "§2.n" is sub-question n of a report's findings section. R5 has unnumbered headings, so it is cited by part name: SQ1–SQ7, deliverables (a)–(e), "recommendations", "gap statement" or "verification list". Each section opens with the sources it draws on.

# 7. Validation and robustness

Sources: R1 (published values, slow-passage theory), R5 (corpus checks, figure plan, numerics), R3 (ramp timescale), R7 (numerical non-replicability); from v0.3, RB (primary-source equations). Two ordering rules apply \[reasoned, not tested\]:

- No new run (S5 onward) starts before replication gate G0 passes.

- The Table 7.1 tolerances go into configs/replication.yaml and are frozen at the end of MS1, before the MS2 replication runs, under the tag tolerances-frozen (D34). The Table 7.2 thresholds go into configs/robustness_criteria.yaml and are frozen at MS7, under the tag criteria-frozen (D35), before any M3 ramp-study run (S5 onward; the short S5 baseline-only runs at MS7 have no ramp). Any later change needs a decision-log entry and must be reported in the paper.

## 7.1 Replication stage

R1 gives published MPR-family results with values; Part 1 lists them as K1–K10. Part 2 adds K11, Devalle's Hopf frequency ω_c = 2πR\* for identical neurons, as a frequency-mapping check \[R1, §2.2\] \[single source\]. Step A0 (scripts/run_A0.py) evaluates each row and writes results/A0/a0_replication.csv. The tolerances are D34. v0.3 adds the primary-source equations behind K8 and K9 \[RB-item 2\] below the table.

| **ID** | **Published result** | **Run** | **Pass criterion (fixed before running)** | **Status** |
| --- | --- | --- | --- | --- |
| K1 | M2 saddle-node curve \[R1, §2.2\] | A1 | At 20 sampled r, the numerical fold lies within one grid cell (Δη̄ 0.05, ΔJ 0.1) of the formula | single source |
| K2 | Node/focus boundary \[R1, §2.2\] | A1 | Eigenvalue discriminant changes sign within one cell of η̄\_f(J); record whether a node region exists (C9) | single source |
| K3 | Focus, node and saddle at η̄/Δ = −5, J/√Δ = 15 | A1 | Exactly these three fixed points | single source |
| K4 | Step I = 3: damped oscillation matching an N = 10⁴ network \[R1, §2.2; R5, SQ1\] | S1, A2 | K4-MF (MS2): frequency and decay within 2% of the linearisation, fitted on the tail of the step response (A2). K4-net (MS5): first three peak times and final r within 5%; non-blocking until a source gives the M2 network coupling (UNVERIFIED; section 12.4) | verified |
| K5 | Sinusoid I₀ = 3, ω = π/20: periodic bursting | S1 | One burst per period for 5 periods after a 2-period transient | single source |
| K6 | ω = π, η̄ = −2.5, J = 10.5: chaos, λ = 0.183 | S1 | Optional (D38). RB-item 1b finds I₀, ω and Δ only in the arXiv v1 text, with Δ taken from App. A rather than the Fig. 3 caption, and marks them PARTIAL, so they are not entered. If confirmed: λ = 0.183 ± 0.01 | incomplete (RB-item 1b: PARTIAL) |
| K7 | Supercritical Hopf at τ_d = 4.95 ms; damped at 3 ms, sustained at 8 ms \[R1, §2.3\] | A4, A5, S3 | τ_d^(H) = 4.95 ± 0.05 ms; v decays at 3 ms and holds within ± 2% at 8 ms; squared amplitude linear in τ_d − τ_d^(H), no hysteresis | single source (CP1); RB-item 3 matches, but arXiv v1 only (PARTIAL), so not upgraded |
| K8 | ref_devalle: gamma at τ_d = 5 ms, none at 50 ms; N = 5×10⁴ network matches \[R1, §2.4; R5, SQ1\]. Devalle Eq. 3, Fig. 3: τ_m = 10 ms, J = 21, Θ = 4, Δ = 0.3; R(0) = S(0) = 5 Hz, V(0) = 0 \[RB-item 2c\] | A4, A6, S3 | At 5 ms: limit cycle. At 50 ms: stable fixed point. Network peak within 5%. Mean-field runs start from Devalle's Fig. 3 initial values. Non-blocking: peak in 25–100 Hz (feeds G2) | Existence at 5 ms and absence at 50 ms: verified (R1; R5; RB-item 2c). The 25–100 Hz band is \[reasoned, not tested\]: Devalle reports "the gamma range" with no Hz value \[R1, §2.4\] |
| K9 | Oscillation needs J \< 0 and τ_d \> 0, and stops above δ = Δ/Θ = δ_c = 0.1453…, a ratio (Devalle Eqs. 8, 20) \[R1, §2.3; R5, SQ1; RB-item 2a–2b\] | A4 | No Hopf for J \> 0. At η̄ = 1, 2 and 4: the largest Δ/η̄ on the Hopf curve, maximised over τ_d and J, is 0.1453 ± 0.002 (Δ ≈ 0.145, 0.291 and 0.581; Θ ↔ η̄ + I with I = 0, as in section 3.1). That this maximum equals δ_c is \[reasoned, not tested\]. τ_d is searched over the D11 range (1–50 ms). A4 first locates the maximiser and checks that it lies inside the τ_d and J ranges searched; if it lies on an edge, that range is widened and the change logged, at most twice; if the maximiser is still on the edge, the maximum is reported as asymptotic. If the computed maximum differs from 0.1453, K9 blocks only on the verified ratio scaling (the maxima of Δ/η̄ at η̄ = 1, 2 and 4 agree within ± 0.002) and the maximum is reported | δ_c: verified (R5; RB-item 2a–2b), C4 settled; one protocol at all three η̄ (v0.4); J and τ_d conditions: single source; maximisation reading: reasoned, not tested (UNVERIFIED; v0.5) |
| K10 | Ceni: 5–30 Hz, falling with τ_d, nearly independent of J \[R1, §2.4\] | A6 | Over the oscillatory τ_d interval that A4 computes at ref_ceni (from 4.95 ms to its upper end, which is recorded; at most 50 ms): frequency within 5–30 Hz ± 10%, monotone in τ_d, \< 10% change over J from −40 to −5 | single source |
| K11 | ω_c = 2πR\* for identical neurons \[R1, §2.2\] | A4 | On the J → 0⁻ Hopf branch (where J changes sign): Im λ_Hopf/(2πr\*) = 1 ± 0.01 at Δ = 10⁻⁴ | single source |

*Table 7.1. Replication targets (A0). Tolerances: D34 \[needs decision\], frozen at the end of MS1.*

**Primary-source equations for K8 and K9** (Devalle, Roxin, Montbrió 2017, PLoS Comput Biol 13:e1005881, read in arXiv v3 with the PLOS equation numbering cross-checked; R\_\* is the fixed-point rate) \[RB-item 2a–2c\]:

    Eq. (3)   τ_m Ṙ = Δ/(πτ_m) + 2RV
              τ_m V̇ = V² − (πτ_m R)² − Jτ_m S + Θ
              τ_d Ṡ = −S + R
    Eq. (6)   −2Jτ_m R_* = (1 + τ_d λ)[(2πτ_m R_*)² + (τ_m λ + Δ/(πτ_m R_*))²]
    Eq. (8)   δ_c = (Δ/Θ)_c = (1/5)√(5 − 2√5) = 0.1453…
    Eq. (20)  δ = Δ/Θ        (Θ = centre of the Lorentzian, Eq. 14)

Devalle writes the coupling as −Jτ_m S with J ≥ 0 for inhibition, so J_Devalle = −J in this plan (section 3.1, C3). δ_c is a dimensionless ratio, so the critical half-width is Δ_c = 0.1453·Θ; with I = 0, Θ corresponds to η̄ (section 3.1) \[RB-item 2b\]. Tags: Eq. 3 and the value and reading of δ_c are \[verified\] (R1 or R5, plus RB); Eq. 6 is \[single source\] (RB only). A4 can use Eq. 6 to cross-check its characteristic polynomial after the sign mapping \[reasoned, not tested\]. K9 uses one protocol at all three η̄: the largest Δ/η̄ over τ_d and J. That δ_c is a limit over coupling and synaptic time is \[reasoned, not tested\]; RB does not state it (UNVERIFIED). Because the blocking K9 test rests on this reading, G0 blocks on the value 0.1453 only if A4 finds it; otherwise G0 blocks only on the verified ratio scaling across η̄ = 1, 2 and 4 and reports the maximum (Table 7.1; v0.5). Ceni Eqs. 11–12 are not entered, because RB read them only in arXiv v1 (section 12.4).

**Gate G0.** K1–K5 and K7–K9 must pass: K1–K3, K4-MF and K5 at MS2 (G0 part 1, mean field only); K7–K9 at MS5, with K9 judged as in Table 7.1 (if its maximum differs from 0.1453, only the ratio scaling blocks). K4-net is non-blocking until a source gives the M2 network coupling (UNVERIFIED; section 12.4); it runs at MS5 once that coupling is sourced. A K10 or K11 failure, or a K8 peak outside 25–100 Hz, triggers a review of units and τ placement (section 3.3) but does not block; a K8 band failure feeds G2. K6 is optional. Any blocking failure means the equations, the sign convention (C3) or the unit mapping is wrong, and it must be fixed before S5 \[reasoned, not tested\].

## 7.2 Robustness checks

**Headline example (D40).** P2 at ref_devalle, T_ramp = 120 s, linear profile, I = 0. Its default is fixed now and confirmed at MS6, after A6, before any M3 ramp-study run (S5 onward). Metrics are those of Table 2.1: class, onset, delay η̄\_on − η̄\_H, duration, peak frequency f_pk, and absolute and relative power. R5 found the network overlay in 12 of 12 corpus papers, finite-size and noise checks in 2 of 12, and ramp-rate and convergence tests in none \[R5, (b)\] \[single source\].

| **ID** | **Check** | **What is varied (runs)** | **Pass / fail criterion (fixed before S5)** | **Where** |
| --- | --- | --- | --- | --- |
| RB1 | Network vs mean field | N = 10⁴ on the headline path, T_ramp 10 and 120 s, 3 seeds, plus 4 map cells (S8); N sweep (S9) | Same class (Table 2.1 correspondence) in 3/3 seeds and ≥ 3/4 cells; f_pk within 5%; onset within one spectrogram step; N = 3×10⁴ no worse than 10⁴. Fail → G4 | Main F1, F5 |
| RB2 | Noise | σ × 0.5, 1, 2; 10 seeds; 4 T_ramp (S11); noisy subgrid (S7) | Headline surge class kept in ≥ 8/10 seeds at 0.5σ and σ; subgrid agreement ≥ 90% (D24). Noise is stated as phenomenological \[R5, SQ2\] | Main F4, F5; FS3 |
| RB3 | Ramp rate | 13 T_ramp values, 1–1000 s; P1, P2, P5; linear vs sigmoid (S5); D43 floor levels, stochastic Heun (S13) | \(a\) Judged only on the runs inside the RB3(a) range, where δ₀·exp(∫ Re λ dt′) stays above the solver or noise floor until the predicted onset (A4 computes the range; section 5.2, A7): the threshold-crossing onset matches t_pred, the A4 entry–exit prediction along the path, within one A4 η̄ grid step; runs outside the range are reported, not judged \[reasoned, not tested\]. (b) With the D43 noise floor (stochastic Heun), the delay shrinks as the floor rises \[reasoned, not tested; RA, Key finding 4, reports only that noise removes the delay (single source: RA, introduction depth)\]; no scaling law is entered (UNVERIFIED). (c) Class holds at 56, 100, 178 and 316 s, the grid points around the 1–5 min ramp \[R3, §6\]. (d) Profile changes class at ≤ 1 of these; profile effects on the delay are reported as slow-passage physics (section 4.4) | Main F4 \[R5, recommendations\] |
| RB4 | Parameter perturbation | New run S16: ±10% one at a time on eta_start, eta_peak, J0, Delta, tau_d_ms, J_lag_frac, J_T_frac (14 runs); 64-point Latin hypercube | Class unchanged in all but ≤ 2 one-at-a-time runs and in ≥ 80% of the hypercube. Fail → G5 | Main text; appendix table |
| RB5 | Initial conditions | δ₀ of 10⁻⁹, 10⁻⁶, 10⁻³ applied at t_on (S13); start distance 0.5, 1.5, 3 (S5); up vs down ramps (P5, S4) | Class unchanged. Delay shifts are the expected memory effect and are reported \[R1, §2.5; R5, SQ4\] | Main F4; FS4 |
| RB6 | Numerical convergence | rtol 10⁻⁸–10⁻¹² and DOP853 vs Radau (noise-free runs); Heun dt ladder (D43-floored runs); network dt from 10⁻³ to 10⁻⁴ τ; V_p ±100 vs ±200 (S13) | With the D43 floor (stochastic Heun), the headline delay changes \< 5% between the default step 10⁻³ τ and the finest rung of the Heun dt ladder (lower rungs UNVERIFIED; set before MS7); for noise-free DOP853 runs the delay is reported against rtol (10⁻¹⁰ vs 10⁻¹²), not used as a pass test; solvers agree on class with onset within 1 ms; halving dt changes f_pk \< 2% | FS4 \[R5, (c); R7, §2.6\] |
| RB7 | Alternative hypoxia mechanisms | Paths P1–P5; NC1–NC3 (S5, S6, S12) | Claims are stated per path. NC1 has no surge class (NS or D-none) at every T_ramp (else G7). A surge under one path only limits the claim to that mapping | Main F6 |
| RB8 | Model variants | M2 vs M3; Lorentzian, Gaussian or uniform heterogeneity (S10); M4 and M3a/M3b via G2/G3 | Gaussian and uniform give the Lorentzian class (3 seeds). M4 criteria are written before its runs | F4; FS3; FS6 |
| RB9 | Frequency mapping | \(a\) Dimensional vs nondimensional runs; (b) spectral vs cycle frequency; (c) bands 25–100 vs 30–120 Hz; (d) τ ± 20% | \(a\) within 0.5%; (b) within 1/W; (c) ≤ 5% of cells change class; (d) reported only, since every gamma result the reports cite fixes τ = 10 ms \[R1, §2.4; R5\] | FS5; F3 |
| RB10 | Surge-definition sensitivity | A8 band, factors, A_min, window, minimum cycles 5 and 20 | Headline class unchanged under each change; ≤ 10% of map cells change class | FS5 |

*Table 7.2. Robustness checks. Thresholds: D35 \[needs decision\]. The perturbation box and the T_ramp bracket are \[reasoned, not tested\].*

**Main text versus appendix.** Main text: RB1, RB2 (noise robustness, a main result from v0.4: the noise band on F4 and the noisy-subgrid agreement on F5), RB3, RB5 and RB7, and RB4 as a single sentence. Appendix: RB6, RB8, RB9 and RB10. This follows R5, which places ramp-rate and quasi-static results in the main text and numerics in the appendix \[R5, recommendations\], and RA, which recommends noise robustness as a main result \[RA, Recommendations\]. Failure regimes get equal weight \[R7, §2.7\]. The Hopf location (A4) and the A7 entry–exit delay prediction, checked against S4 and S8, supply the analytic-versus-network result R6 asks for \[R6, §6 rec. 4\].

**Evaluation.** Step A11 (scripts/run_A11.py) reads the frozen criteria and writes results/A11/a11_robustness.csv: value, threshold, pass or fail, and the input commits. Failed checks are reported, not dropped, because MNA bars hiding known issues \[R6, §2.1; R7, §2.7\] \[verified\].

## 7.3 Model-variant equations (RB8, S14, S15)

Sources: RB-items 4 and 5 (v0.3). Table 4.1 and the gates are unchanged. This subsection records only what RB read in primary sources, for use if G2, G3 or RB8 calls for an extension.

**M4 (E–I, PING).** RB located the instantaneous-synapse E–I equations (the Table 4.1 form) in MPR App. E but did not transcribe them, and Segneri's equations did not render \[RB-item 5; R1, §2.3\]. The E–I MPR model with first-order synapses of Dumont and Gutkin 2019 (PLoS Comput Biol 15:e1007019), Methods Eqs. (7)–(8), was read in full text and is given as printed, with η̄ the median \[RB-item 5\] \[single source\]:

    Eq. (7), E-cells:
       τ_e ṙ_e = Δ_e/(πτ_e) + 2r_eV_e
       τ_e V̇_e = V_e² + η̄_e + I_e^ext + τ_e s_ee − τ_e s_ei − τ_e²π²r_e²
       τ_s ṡ_ee = −s_ee + J_ee r_e
       τ_s ṡ_ei = −s_ei + J_ei r_i
    Eq. (8), I-cells:
       τ_i ṙ_i = Δ_i/(πτ_i) + 2r_iV_i
       τ_i V̇_i = V_i² + η̄_i + I_i^ext + τ_i s_ie − τ_i s_ii − τ_i²π²r_i²
       τ_s ṡ_ie = −s_ie + J_ie r_e
       τ_s ṡ_ii = −s_ii + J_ii r_i

The same system appears as Eqs. (2)–(3) in their Results. PING parameters (their Fig. 2): τ_e = τ_i = 10, τ_se = τ_si = 1, η̄\_e = η̄\_i = −5, J_ee = 0, J_ei = 15, J_ii = 0, J_ie = 15, Δ_e = Δ_i = 1, I_e^ext = 10; network v_th = 500, v_r = −500 \[RB-item 5\]. The couplings J sit inside the synaptic equations and inhibition enters with a fixed minus sign, unlike this plan's signed J (section 3.1) \[RB, recommendations\]. This is an eight-variable system, not the four-variable M4 of Table 4.1. Which form M4 takes is D42 \[needs decision\]; S14 stays unspecified until then.

**M3a (Gast, Schmidt, Knösche 2020).** The erratum (Neural Comput 33(6):1717, 2021; DOI 10.1162/neco_c_01397) states that Eq. 3.6 "contains an erroneous scaling of the input firing rate r with the capitation time constant τA" and that Eq. 7.3 differs from Eq. 3.6 "merely by a constant scaling of r with τA". The results are unaffected because τA was never varied, but the reported α values for synchronized bursting "hold only for synaptic depression given by equations 7.2 and 7.3" \[RB-item 4; erratum prose read in full\]. So the erratum identifies an erroneous scaling of r with τA in Eq. 3.6; Eq. 7.3 is its corrected form, and the α values hold only for the depression system Eqs. 7.2–7.3 \[R1, §2.3; R5, SQ1\] \[verified\]; RB-item 4 is PARTIAL and adds no tag. Not entered, because RB marks them PARTIAL or UNVERIFIED: the corrected Eqs. 7.1–7.3 (read only from a search-engine rendering; the placement of /τA in 7.1 is ambiguous), the published Eqs. 3.5–3.8 and 4.7–4.8 (not read), and their numbering (3.5–3.6 may be the A/B equations or part of the SFA system) \[RB-item 4\]. Read the publisher PDF before G3 or S15.

**M3b (Chen and Campbell 2022).** RB does not cover it. Its equations remain unread (Table 4.1 cites the abstract only).

# 8. Figures

Sources: R5 (figure conventions and a six-figure plan), R6 (budget), R7 (captions). Handoff (f) fixes six main figures and six supplementary figures. R6 suggests about 15–20 pages and 5–6 figures \[R6, §2.5, §6 rec. 4\] \[single source: R6\], and R5 proposes six main figures \[R5, (c)\]. Conventions \[R5, SQ3\]:

- shaded regions bounded by continued curves;

- network symbols overlaid on mean-field results;

- markers that link diagrams to traces;

- full parameters and spectrogram settings in each caption.

Each figure also gets a Nordlie parameter table \[R5, SQ6; R7, §2.5\] \[verified\].

**Script rule.** Each figure has its own script, scripts/fig\_\<ID\>.py, which calls plotting.figures.make\_\<ID\>. Scripts read only results/ and never simulate. Each script writes the figure, \<ID\>\_provenance.json (input records, config hashes, seeds, commits) and \<ID\>\_params.csv. This follows the Sandve rules \[R5, SQ6; R7, §2.5\]. A figure built from a clean tree is tagged fig-\<ID\>-v\<k\>.

| **ID** | **What it shows** | **From** | **Script** | **Result that would change the plan** |
| --- | --- | --- | --- | --- |
| F1 | Schematic and ramp protocol; mean-field and network r(t), v(t) on the headline path; 300-neuron raster; spectrogram of v | S8, S5, A8 | fig_F1.py | Network shows no surge → G4. Peak \< 25 Hz → re-select the headline via A6 (logged), or G2 |
| F2 | One-parameter diagram along η̄ at ref_devalle, with cycle max/min, Hopf point and network symbols | A5, S4 | fig_F2.py | Subcritical Hopf or fold of cycles → abrupt onset and hysteresis \[R1, §3\]; add P5 to F4 |
| F3 | (η̄, τ_d) and (η̄, Δ) planes: Hopf curves, frequency shading, 25 and 100 Hz contours, path arrows, markers | A4, A6 | fig_F3.py | 25 Hz contour outside the oscillatory region in range → G2 |
| F4 | Delay, peak power (absolute and relative), f_pk and duration against ε; quasi-static line; up vs down ramp; start state; noise band; M2 ring | A7, A3, S5, S11 | fig_F4.py | Onsets miss the A4 entry–exit prediction on the runs inside the RB3(a) range, or the floored delay (D43) depends on the Heun step (RB6) → G6 |
| F5 | Surge/no-surge maps with network symbols and subgrid agreement; F5c: metrics against N (CP7) | A9, S7, S8, S9 | fig_F5.py | A surge class in \< 3% of map-1 cells, or RB4 fails → G5; network disagrees in ≥ 2/4 cells → G4 |
| F6 | Failure reasons; NC1–NC3 against T_ramp; P2 vs P3; P4a and P4b | A9, A10, S6, S12 | fig_F6.py | NC1 surge → G7; only P3 surges → H-drive framing (section 4.5) |
| FS1 | M2 diagram (K1–K3), K4 and K5 traces, ring map | A1, A2, S1 | fig_FS1.py | G0 |
| FS2 | M3 validation (K7–K11) | S3, A4–A6 | fig_FS2.py | G0 |
| FS3 | Finite size, heterogeneity shape, noise | S9–S11 | fig_FS3.py | Shape changes class → claim limited to Lorentzian heterogeneity |
| FS4 | Numerics | S13 | fig_FS4.py | Any RB6 failure → affected results unused |
| FS5 | Classifier tests and sensitivity; frequency mapping | A8 | fig_FS5.py | Synthetic test fails → rework A8 |
| FS6 | M4 or M3a/M3b | S14, S15 | fig_FS6.py | Only if G2 or G3 triggers |

*Table 8.1. Planned figures. Every ID traces to handoff (c) or section 7.*

# 9. Compute budget

Sources: R5 (compute and tool tables). No corpus paper reports runtimes, and every R5 figure is an estimate \[R5, SQ7, gap statement\]. Below, "R5 est." marks R5's estimates and "est." marks my extrapolations \[reasoned, not tested\]. My extrapolations assume:

- at least 20 mean-field steps per τ (max_step, D25);

- 0.1–0.3 ms per scipy DOP853 step;

- 20–50 ns per Numba Heun step;

- R5's rate of 0.5–1×10⁹ neuron-updates/s per core;

- 6 workers.

| **Stage** | **Work** | **Wall time (6 workers)** | **Memory** | **Basis** |
| --- | --- | --- | --- | --- |
| One mean-field P2 ramp, T_ramp 120 s (165 s = 16,500 τ; CP14) | ≥ 3.3×10⁵ steps | 33–99 s per run (one core) | \< 100 MB | est.; R5 gives \< 1–5 s per 10⁴ τ without a max_step limit (R5 est.) |
| S1–S4, A1–A6 (validation, continuation) | ~100 short runs; A6 from continuation (no brute-force grid) | \< 30 min; plus a few minutes for Julia's first compile | \< 1 GB | est.; R5 est. |
| S2, S5, S6 (ramp sweeps) | 7×10⁷ mean-field steps; 3.1×10⁹ Heun steps | 19–57 min | \< 1 GB | est. |
| S5 baseline-only mode-N runs at MS7 (headline and 900 + 325 map cells × 10 seeds × 7 s; MC-01, v0.5) | 8.6×10⁹ Heun steps | 0.5–1.2 min | small | est. \[reasoned, not tested\] |
| S7 map 1 (900 cells × 120 s) | 3.0×10⁸ steps | 1.4–4.1 h | \< 2 GB | est.; R5 est. is 30–60 min for 10⁴ runs of 1 s |
| S7 map 2 (25 × 13) and noisy subgrid (225 × 10 seeds) | 1.5×10⁸ steps; 3.8×10¹⁰ Heun steps | 0.7–2.2 h | \< 2 GB | est. |
| S8, S10, S12 networks, K8 at N = 5×10⁴ and the σ baseline (MS5) | ~2.0×10¹² neuron-updates | \< 30 min | \< 500 MB per run | R5 rate |
| S9 finite size (4 N × 10 seeds) | 4.0×10¹² updates | 11–23 min at the stated rate; allowance 2 h | \< 2 GB | est.; R5 est. 1–2 h |
| S11, S12 mean field, S16 | small | \< 40 min | small | est. |
| S13 numerics (scope: P2 at 10, 120 and 316 s; Radau 3–10× slower; network dt ladder ×17 on the 10 s ramp) | — | \< 1 h | \< 1 GB | est. |
| Spectrograms (10⁶ samples per run) | — | \< 1 s per run | \< 200 MB | R5 est. |
| Analysis and reclassification (A8–A11, RB10) | stored series only; no re-simulation | measured in the timing gate | — | v0.4 |
| **Total, S1–S13 and S16** |  | about 3–12 h (the row ranges sum to 2.6–11.9 h, including the MS7 baseline-only runs: the lower bound with S9 at its computed 11 min, the upper bound with S9 at its 2 h allowance; analysis timed separately); cap 24 h (D36) | \< 3 GB of 16 GB |  |

*Table 9.1. Compute budget on the Ryzen 5 5600 (16 GB, Windows 11, CPU only). Scaling: mean field is linear in simulated time; networks scale as N·T/dt; continuation scales weakly with dimension (R5 est.). S14 and S15 are unknown until their equations are fixed: S14 by D42, S15 by the Gast publisher PDF (section 7.3).*

**Disk.** Map cells keep metrics plus v and r at 1 kHz in float32, about 1 MB per cell. Full series are kept only for examples, the subgrid and network runs. Estimated total: under 20 GB. Series are written with np.savez_compressed, and MS15 decides which result families are archived (D37).

## 9.1 Tools on Windows

- **Python 3.11** with numpy, scipy, numba, pandas, pyarrow, matplotlib, pyyaml and pytest. Used for all stages; cross-platform \[R5, (d) for SciPy; reasoned for the rest\].

- **Julia with BifurcationKit.jl** for A5. Windows support is not stated in its docs \[R5, SQ5\], so a one-day smoke test at MS1 decides (D23): install and precompile, then the Hopf normal form and periodic-orbit continuation of M3 at ref_ceni (K7), with the periodic-orbit method stated. Julia writes CSV plus a JSON record (commit, Julia version, Manifest SHA-256); a Python step validates it and writes results/A5/a5_cycles.npz. Julia and BifurcationKit versions are pinned (Manifest.toml).

- **Flagged fallbacks, none of them required \[R5, SQ5, (d)\]:** PyRates/PyCoBi and AUTO-07p need MSYS2 or WSL2 (Linux); XPPAUT needs an X11 server; MatCont needs MATLAB.

- **PyDSTool:** do not use. It is broken on Python ≥ 3.10 (R5's verification list, corrected) \[single source\].

- **Long sweeps:** disable sleep; pause Windows Update or set active hours; add a Defender exclusion for the repository and .venv; keep the repository outside OneDrive-synced folders and near the drive root (for example C:\dev\mpr-gamma-surge), with long paths enabled (LongPathsEnabled; git core.longpaths true); launch sweeps detached (Start-Process) with logs \[reasoned, not tested\]. Restartable runs (section 10.4) are the safety net.

## 9.2 Feasibility gate

1.  **Time the expensive cells.** After MS1, run python scripts\time_one_run.py --config configs\S5.yaml --cell headline --repeat 3, then the same for each timing cell: the headline (P2, ref_devalle, 120 s); Δ = 0.01 near the Hopf window; Δ = 0.6; P5 at T_ramp 1000 s; Radau at rtol 10⁻¹²; and one mode-N run. Until A4 exists, the η̄ path is provisional and recorded as such; the headline is re-timed after A4 (MS5). Results go to results/timing/. Repeat for the network at N = 10⁴ and 3×10⁴ once that code exists, and time 6, 8 and 10 workers.

<!-- -->

1.  **Extrapolate.** Mean field: Σ τ simulated × measured s/τ ÷ workers. Network: Σ N·T/dt × s/update ÷ workers. Each run family is extrapolated from its matching timing cell, not from the headline alone. The script prints a predicted wall time for each S-ID and the total.

<!-- -->

1.  **Launch only if** the prediction is ≤ 1.5 × the Table 9.1 allowance and the total stays within the D36 cap. Otherwise apply the cut order. Log both the measurement and the decision.

<!-- -->

1.  **Re-time** after any change to the solver, the Numba kernel or package versions.

## 9.3 Cut order

Apply cuts in this order until the prediction fits:

1.  Run Radau only at the headline T_ramp.

<!-- -->

1.  Drop network dt = 10⁻⁴ τ unless 2.5×10⁻⁴ τ fails RB6.

<!-- -->

1.  Cut S9 to 5 seeds.

<!-- -->

1.  Run the sigmoid profile for P2 only.

<!-- -->

1.  Drop the 562 s and 1000 s ramps from P5 and from the start-distance runs.

<!-- -->

1.  Shrink map 1 to 20 × 20, with boundary refinement (D31).

<!-- -->

1.  Shrink map 2 to 13 × 13.

<!-- -->

1.  Raise max_step to 0.1 τ, only if RB6 shows \< 1% change at the headline point.

Never cut: the G0 replication runs, NC1, the S8 headline overlay, the S13 headline tolerance check, the A8 tests and the one-at-a-time part of S16.

# 10. Repository design

Sources: R5 (Sandve and Nordlie rules; corpus practice on code, seeds and versions) \[R5, SQ6, recommendations\]; R7 (code and parameter sets; integrator and tolerances reported; archive with a version identifier) \[R7, §2.5–2.6, §6 rec. 6\]; R6 (no code mandate at MNA, but software and data must be credited) \[R6, §2.1, §8(d)\]. Names come from handoff (d) and (e); A0, A11, S16 and the figure scripts are Part 2 additions.

## 10.1 Folder tree

    mpr-gamma-surge/
    ├── README.md                    Windows setup, run order, figure map
    ├── CHANGELOG.md                 one entry per release tag
    ├── CLAUDE.md                    instructions Claude Code reads every session (10.9)
    ├── LICENSE, CITATION.cff        licence and citation (D37)
    ├── pyproject.toml               package metadata, src layout, pytest markers
    ├── .gitignore, .gitattributes   ignore rules; * text=auto eol=lf; binaries (both below)
    ├── .github/workflows/tests.yml  fast tests on windows-latest (optional)
    ├── .claude/                     Claude Code project files (10.9)
    │   ├── settings.json            shared permission rules (committed)
    │   ├── settings.local.json      personal overrides (git-ignored)
    │   └── rules/                   optional path-scoped rules
    ├── environment/
    │   ├── requirements.in          direct dependencies, == pins (MS0)
    │   ├── requirements-lock.txt    full pip freeze (UTF-8)
    │   ├── python-version.txt       interpreter used at MS0
    │   └── julia/                   Project.toml, Manifest.toml (committed),
    │                                setup_julia.jl
    ├── configs/
    │   ├── base.yaml                path-neutral (P2) defaults
    │   ├── replication.yaml         K1–K11 targets, tolerances (D34), frozen at MS1
    │   ├── robustness_criteria.yaml RB1–RB10 thresholds (D35), frozen at MS7
    │   ├── S1.yaml … S16.yaml       one per run family
    │   └── A0.yaml … A11.yaml       one per analysis step
    ├── src/
    │   └── mprsurge/                every subfolder has an __init__.py
    │       ├── units.py  config.py  params.py  provenance.py
    │       ├── models/              MODEL: mpr2d.py (M2), mpr3d.py (M3),
    │       │                        fixed_points.py
    │       │                        EXTENSIONS: ping4d.py (M4), adaptation.py
    │       ├── ramps.py             paths and breakpoints
    │       ├── simulate_mf.py       run_mf, run_mf_noisy
    │       ├── qif_network.py       NETWORK: run_qif_network, samplers
    │       ├── analysis/            ANALYSIS: bifurcation.py, ramp_analysis.py,
    │       │                        regime_map.py, continuation/bk_cycles.jl,
    │       │                        replication.py (A0), robustness.py (A11)
    │       │                        SURGE METRICS: surge_metrics.py
    │       ├── plotting/            style.py, figures.py (make_F1 … make_FS6)
    │       └── run.py               python -m mprsurge.run --config <yaml>
    ├── scripts/
    │   ├── run_A0.py … run_A11.py   one per analysis step
    │   ├── fig_F1.py … fig_FS6.py   one per figure (12 files)
    │   ├── time_one_run.py          feasibility gate
    │   ├── check_clean_tree.py      blocks tagged builds from a dirty tree
    │   └── make_all.ps1             pipeline in milestone order
    ├── tests/                       test_units, test_config, test_provenance,
    │                                test_models_2d, test_models_3d,
    │                                test_fixed_points, test_ramps,
    │                                test_qif_network, test_surge_metrics, test_noise,
    │                                test_runner, test_julia_io, test_replication (slow)
    ├── docs/                        decision_log.md, robustness_criteria.md,
    │                                figure_map.md, search_log.md,
    │                                plan.md (Markdown copy of this plan)
    ├── results/                     NOT TRACKED (git-ignored)
    └── figures/                     NOT TRACKED (git-ignored)

Drivers (simulate_mf.py, qif_network.py, run.py) only integrate. Analysis modules only analyse. Figure scripts only plot. Each result therefore has exactly one producer \[reasoned, not tested\].

**Layout change (v0.3).** The package now sits under src/, so it can only be imported after pip install -e . (see section 10.2). Without src/, a script run from the repository root could import the source folder by accident and hide a packaging mistake. Module names and the command python -m mprsurge.run are unchanged; only the folder moves. The handoff (d) module paths have been updated to src/mprsurge/ and the change is recorded as CP13 in Table 12.1. This is an engineering convention from the Python Packaging User Guide, not from the seven reports \[reasoned, not tested\].

**Additions.** Besides src/, the tree adds CHANGELOG.md, the optional CI file, \_\_init\_\_.py in each package folder and the pytest marker for slow tests. Julia's Manifest.toml is committed, not ignored, because it pins the exact Julia package versions \[reasoned, not tested\]. The CI file installs the package (pip install -e .) and runs only pytest -m "not slow" on windows-latest; slow tests, Julia and all runs stay on the Ryzen PC. CLAUDE.md, .claude/ and docs/plan.md are described in section 10.9.

Contents of .gitignore:

    # environments and caches
    .venv/
    __pycache__/
    *.pyc
    *.egg-info/
    .pytest_cache/
    .ipynb_checkpoints/
    # numba and julia caches
    *.nbi
    *.nbc
    *.cov
    # outputs (never edited by hand; archived with the release, D37)
    results/
    figures/
    # Claude Code personal files (10.9)
    CLAUDE.local.md
    .claude/settings.local.json
    # Windows
    Thumbs.db
    desktop.ini

Contents of .gitattributes (TRIAGE T86):

    * text=auto eol=lf
    *.npz binary
    *.parquet binary
    *.png binary

pyproject.toml declares the build system and the package, which pip install -e . needs, and the slow-test marker, so that pytest -m "not slow" runs without warnings:

    [build-system]
    requires = ["setuptools>=64"]   # PEP 660 editable installs
    build-backend = "setuptools.build_meta"
    [project]
    name = "mprsurge"
    version = "0.1.0"
    requires-python = ">=3.11,<3.12"
    dependencies = [...]   # the direct dependencies in requirements.in
    [tool.pytest.ini_options]
    markers = ["slow: long-running replication tests"]
    addopts = "--strict-markers"
    testpaths = ["tests"]

## 10.2 README: Windows setup (PowerShell)

Prerequisites: Python 3.11 from python.org (with the py launcher), Git for Windows, and Julia (for A5 only). Record the exact Python installer version in environment/python-version.txt and check that py -0p lists 3.11 and py -3.11 starts it. Pin the Julia version (for example with juliaup) and record it. Keep the repository near the drive root and outside OneDrive.

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

The README also states the integrator, tolerances, step sizes, initial conditions, ramp protocol and gamma-power computation \[R7, §6 rec. 6\]. Julia is set up from a script file to avoid PowerShell quoting problems (CP8). On a clean machine: \<repository-url\> is a placeholder (in PowerShell, \< is reserved); a repository downloaded as a ZIP carries Mark-of-the-Web, so run Get-ChildItem -Recurse \| Unblock-File before activation; add -Force to Set-ExecutionPolicy when it is scripted; calling .venv\Scripts\python.exe directly avoids activation. Bootstrap order (MS0): install the direct dependencies, write environment/requirements.in with == pins from that first successful install, then write requirements-lock.txt with the freeze command above; later installs use the lock.

## 10.3 Configuration system

base.yaml holds path-neutral (P2) defaults for the handoff (e) keys (derived keys are filled by resolve_config); each run file holds only its overrides and a sweep: block. resolve_config merges base, run file and any --set key=value overrides. It then expands ref_point, derives eta_start, eta_peak (D12) and ε, rejects unknown keys, and validates every key against a typed schema, casting or rejecting values, because PyYAML (YAML 1.1) reads 1e-10 or --set solver.rtol=1e-12 as a string. config_hash is the SHA-256 of the canonical JSON of the per-run resolved config: cell parameters, seed spawn key, and solver and numerics settings, but not run.workers, output.dir or any path (paths are written in POSIX form). Its first 12 hexadecimal characters name each output (section 6.6), and on reuse the full SHA-256 stored in the JSON record is compared. New keys:

- replication.tolerances_file

- robustness.check_id, robustness.criteria_file, robustness.criteria_sha256

- budget.max_wall_h

- run.kind

- noise.floor_levels (D43)

Figure scripts reject any input made with an override that is not in a committed config. Excerpt of base.yaml:

    model:    {type: M3, ref_point: ref_devalle, tau_ms: 10, tau_d_ms: 5,
               eta_bar: 4, Delta: 0.3, J: -21, I_drive: 0}
    path:     {name: path_hypoxia, profile: linear, sigmoid_k: 10, T_ramp_s: 120,
               t_on_s: 5, J0: -21, J_end: 0, J_lag_frac: 0.25, J_T_frac: 1.0,
               I_amp: 0, Delta_factor: 1.0}
    solver:   {method: DOP853, rtol: 1.0e-10, atol: 1.0e-12, max_step_tau: 0.05,
               dt_out_ms: 1, delta0: 1.0e-6}
    network:  {N: 10000, dt_tau: 1.0e-3, V_peak: 100, V_reset: -100,
               het_dist: lorentzian, het_sampling: quantile}
    analysis: {band_primary_hz: [25, 100], total_band_hz: [1, 150], rel_factor: 2,
               abs_factor: 2, amin_factor: 0.1, min_cycles: 10, collapse_r_frac: 0.1}
    seeds:    {root_seed: 20261008, n_seeds: 10}

## 10.4 Provenance

Each run record (section 6.6) also stores:

- the git commit, branch, tags and a dirty flag;

- versions of Python, packages, Julia and BifurcationKit;

- OS and CPU;

- SHA-256 of every input and output file;

- the hash of the criteria file.

No sampled MPR paper reported seeds or versions \[R5, SQ6\] \[single source\]. Floating-point effects can change ODE results, so numerical settings are always recorded \[R7, §2.6\] \[single source\].

**Run engineering (v0.4).** Long sweeps on a home PC must survive restarts and failures:

- Restart and failure: each output is keyed by its config hash and skipped if complete; writes go to \*.tmp and then os.replace, retried on PermissionError (Windows file locks); every JSON record stores a status (ok, failed, timeout) and the solver message; each run has a wall-time limit (for example 10× its predicted time); a failed DOP853 run is retried once with Radau and flagged; failed cells are their own label in A9, not NS; results/\<ID\>/manifest.csv journals every run.

- Seeds in Numba: the SeedSequence child is passed into the jitted kernel as a seeded generator, because np.random.seed() called from Python does not seed the generator Numba uses inside jitted code; one run per process, and no prange touches the generator.

- Numba cache: make_all.ps1 clears the Numba cache files (\*.nbi, \*.nbc) before every tagged run and records this in provenance; jitted code never reads config values from module globals; the cache is warmed in the parent before the worker pool starts.

- Logging: the logging module writes one log per run family (results/\<ID\>/run.log) through a queue handler from the workers to the parent; a heartbeat reports progress and ETA every N runs; RuntimeWarning and solver messages go into each record.

- Workers: OMP_NUM_THREADS, OPENBLAS_NUM_THREADS and NUMBA_NUM_THREADS are set to 1 in the pool initializer; workers receive plain dicts of resolved config and rebuild paths inside the worker; configs/ is resolved from the repository root, not the working directory; ramp paths are built from picklable data, not lambdas or closures.

- Memory: solve_ivp always gets t_eval on the 1 ms grid and never dense_output; network runs store only mean V, the binned rate and the 300-neuron raster, and the code asserts this.

## 10.5 Unit tests

| **File** | **Checks** |
| --- | --- |
| test_units | τ → ms; f_Hz = 100 f_τ; dimensional and nondimensional runs agree within 0.5% (RB9a) |
| test_models_2d, test_models_3d | Right-hand side vanishes at fixed points; v\* = −Δ/(2πr\*) \[R1, §2.2\]; Jacobian matches finite differences; r stays positive (dr/dt = Δ/π at r = 0); M3 with τ_d = 10⁻³ τ tracks M2 within a stated tolerance (short run; the system is stiff); the K7 Hopf value is checked in test_replication (slow), not here |
| test_fixed_points | Quartic roots match brute-force bracketing; K1 and K2 on a coarse grid |
| test_ramps | g(0) = 0, g(1) = 1, monotone; breakpoints at the corners; in P2, J reaches 0 at t_on + 1.25 T_ramp and the run covers the full J path (the hold starts after it) |
| test_qif_network | Lorentzian quantiles: median η̄, quartiles η̄ ± Δ; an uncoupled neuron fires at √η/π per τ (derived) within a stated tolerance; synapse update: s converges to the input rate, and each spike is counted once, 1/V_j after crossing; identical seed gives identical output and different seeds differ (seed passed into the jitted kernel); at J = 0 the network rate is within 3% of r\* \[reasoned, not tested\] |
| test_surge_metrics | A8 synthetic signals, seeded: burst on/off within one step; chirp; 5-cycle ring → NS or D-none (envelope growth \< 0); slowly damped ring with more than 10 cycles above threshold → NS or D-none (fitted growth negative by more than 2 standard errors); pure trend → NS; zero baseline; P_G/P_non-G threshold; an S-abs case |
| test_noise | Stochastic Heun: seeded stationary variance of a linear (OU) test case against σ²/(2k) |
| test_runner | Results identical for --workers 1 and --workers 6; a forced solver failure is recorded with its status and does not crash the pool; skip-if-done and resume work |
| test_julia_io | The reader for the Julia CSV + JSON output validates fields and versions |
| test_config, test_provenance | Unknown key raises an error; values are type-checked (rtol: 1e-12 is cast or rejected); overrides are recorded; hash is independent of key order, worker count and paths; all record fields present |
| test_replication (slow) | K1–K5 and K7–K11 on reduced grids, including the K7 Hopf value |

*Table 10.1. Unit tests. Run pytest -m "not slow" before every commit and the full suite before every tag. Every test states its tolerance; synthetic noise is seeded; comparisons are within one process or with tolerances, never bitwise against stored arrays (CPUs differ).*

## 10.6 Results and decision log

results/ and figures/ are git-ignored, so outputs are never edited by hand. Everything the paper uses is archived with the release (D37). docs/decision_log.md follows Appendix C. Entries are never deleted; a change gets a new entry that links back to the old one.

## 10.7 Git workflow

**Branches.** Short-lived feat/…, fix/… and exp/\<RUN_ID\> branches merge into main by fast-forward once the fast tests pass.

**Commits.** Format: \<type\>(\<scope\>): \<summary\> \[IDs\], for example feat(mpr3d): add jacobian_3d \[A4\].

**Tags.** All annotated:

- env-v1;

- tolerances-frozen (end of MS1, with the replication.yaml SHA-256);

- replication-pass (G0);

- criteria-frozen (MS7, with the criteria SHA-256);

- fig-\<ID\>-v\<k\>, for each figure build (inputs and hashes in the message);

- release-v1.0.

<!-- -->

    git switch -c feat/mpr3d
    git add -A   # with a reviewed .gitignore
    git commit -m "feat(mpr3d): add rhs_3d and jacobian_3d [A4]"
    python -m pytest -m "not slow"; if ($LASTEXITCODE -ne 0) { throw "tests failed" }
    git switch main; git merge --ff-only feat/mpr3d
    python scripts\fig_F3.py
    git tag -a fig-F3-v1 -m "F3 from A4 <hash12>, A6 <hash12>"; git push origin main --tags

In Windows PowerShell 5.1, ; runs the next command even when the previous one failed, && is not available, and a failing native command does not stop a script, so the test result is checked before the merge and make_all.ps1 checks \$LASTEXITCODE after every native call (python, julia).

## 10.8 Reproducibility checklist

1.  Clone release-v1.0 on a clean Windows machine and install from the lock files.

<!-- -->

1.  Run pytest; all tests pass, including slow ones.

<!-- -->

1.  Run scripts\make_all.ps1 -Stage replication; every G0 row passes.

<!-- -->

1.  Rebuild one figure from the archive; metrics match within the RB6 tolerances, not bit for bit \[R7, §2.6\].

<!-- -->

1.  Re-run one sweep cell with --from-record \<json\>; its metrics match within tolerance.

<!-- -->

1.  Every provenance file names the release commit and none is marked DRAFT.

<!-- -->

1.  Nordlie tables, seeds, versions, OS and CPU are present for every figure and run \[R5, recommendations\].

<!-- -->

1.  Code and results are archived with a version identifier \[R7, §8(d)\], and reused software is credited \[R6, §2.1\].

## 10.9 Working with Claude Code in VS Code

The build is written with Claude Code in VS Code. Claude Code needs no particular folder layout, so the tree in section 10.1 stands. The files below make its sessions consistent from one day to the next. They come from the Claude Code documentation (checked 11 October 2026), not from the seven reports, so they are engineering conventions \[reasoned, not tested\]. Each one is created at MS0.

- **CLAUDE.md (repository root).** The instructions Claude reads at the start of every session, committed to the repository. It is guidance, not enforcement: Claude treats it as context. Keep it under 200 lines, because longer files are followed less reliably. It states the build rules, so they do not have to be repeated in every chat.

- **docs/plan.md.** This plan as Markdown, so Claude can read the section for the milestone in hand. CLAUDE.md names it inside backticks and does not import it with the @ syntax, because an imported file is loaded in full at every launch, and a plan this long would use up the working context.

- **.claude/settings.json.** Shared permission rules, committed. They allow the safe, repeated commands (the tests and the run driver) so that each one does not ask for approval. They are not a safety boundary for anything else.

- **.claude/settings.local.json and CLAUDE.local.md.** Your own overrides for this project, plus CLAUDE.local.md for personal preferences. Both are listed in .gitignore (section 10.1) so they are never committed.

- **.claude/rules/.** Optional. Short files that load only when Claude works on matching paths, for example numerics rules for src/mprsurge/models/. They keep CLAUDE.md short. Add them only if CLAUDE.md grows past its limit.

Contents of CLAUDE.md, written at MS0 (about 20 lines):

    # mpr-gamma-surge
    Plan: `docs/plan.md` (binding). Read only the section for the current milestone.
    ## Rules
    - Work one milestone at a time (MS0–MS15, Table 11.1). Stop at each gate and report.
    - Python 3.11 in .venv, CPU only. Do not use PyDSTool.
      Install from environment/requirements-lock.txt.
    - Run `python -m pytest -m "not slow"` before every commit.
      Run the full suite before every tag.
    - Drivers only integrate, analysis modules only analyse, figure scripts
      only plot (section 10.1).
    - Never edit results/ or figures/ by hand; they are git-ignored outputs.
    - Never invent an equation, value or citation. Where the plan says UNVERIFIED
      or [needs decision], use its default and say so; do not fill gaps from memory.
    - Every run writes a provenance record (section 6.6). Every change of a
      default gets a docs/decision_log.md entry (Appendix C).
    - Commit format: <type>(<scope>): <summary> [IDs]. Do not push or tag unless asked.
    ## Layout
    src/mprsurge/ code; tests/ tests; configs/ YAML; scripts/ drivers and figures;
    docs/ notes (section 10.1).

Contents of .claude/settings.json, written at MS0:

    {
      "permissions": {
        "allow": [
          "Bash(python -m pytest *)",
          "Bash(python -m mprsurge.run *)",
          "Bash(git status)",
          "Bash(git diff *)"
        ]
      }
    }

In VS Code, open the repository root as the workspace folder and select the .venv interpreter, so that tests run in the right environment. The extension bundles its own copy of the Claude Code command-line tool for the chat panel; the standalone install is needed only to type claude in the VS Code terminal. On native Windows, Git for Windows is optional: without it, Claude Code runs commands through PowerShell, which matches the commands in section 10.2. The rule syntax above is written for the Bash tool; how the PowerShell tool matches rules, and how it activates the .venv, are not verified \[needs a check at MS0\]. Test it once by asking Claude Code to run python -m pytest, and adjust the allow rules to what /permissions shows.

# 11. Milestones and decision gates

Sources: Part 1 gates G1–G4 (section 4.3); R1 and R2 on model order \[R1, §6; R2, §6\]; R2 on handling related work \[R2, §4\]; R5 on re-checking the gap \[R5, gap statement\]. A milestone is done only when its test passes and the result is logged.

| **\#** | **Milestone and deliverables** | **Done when** | **Unlocks** |
| --- | --- | --- | --- |
| MS0 | Repository, environment, README, CLAUDE.md, .claude/settings.json, docs/plan.md, decision log seeded from Appendix C; requirements.in with == pins; Julia version pinned | Environment installs and pytest collects; tag env-v1 | MS1 |
| MS1 | Core code: units, config, params, provenance, mpr2d, mpr3d, fixed_points, ramps, simulate_mf; surge_metrics core with its synthetic tests; BifurcationKit smoke test (D23); replication.yaml frozen | Fast tests pass (all but network); --dry-run writes a run record with the commit hash; tag tolerances-frozen | MS2, MS3 |
| MS2 | M2 replication: A1, A2, S1 (K1–K3, K4-MF, K5) | A0 rows K1–K3, K4-MF and K5 pass | G0, part 1 (mean field); MS4 (with MS3) |
| MS3 | Mean-field timing gate (expensive cells; provisional η̄ path) | Predictions within allowance | S2 (MS4) |
| MS4 | M2 ramp diagnostic: S2, A3 | Slowest ramp jumps within one step of the saddle-node; G1 metric (envelope growth) evaluated | G1; MS5 |
| MS5 | M3 replication and network: A4, S3 (K7–K11), K4-net (once a source gives the M2 network coupling; section 12.4); network code and timing; σ calibration run (N = 10⁴ baseline); headline re-timed | K7–K9 pass (K9 as in Table 7.1); K4-net passes, or is recorded as not run while the coupling is unsourced (non-blocking); σ committed; tag replication-pass | G0 complete; MS6 |
| MS6 | M3 structure: S4, A5, A6 | A5 vs S4 amplitudes within 2% (points next to η̄\_H excluded); frequency map done | G2; confirm D40; MS7 |
| MS7 | Classifier and criteria: S5 baseline-only mode-N runs (headline and map cells; v0.5); A8 (classes, A_ref, sensitivity, baseline ρ report from those runs); D43 floor levels, RB3(a) range and floor values, A4 η̄ grid and Heun dt ladder fixed; criteria files | test_surge_metrics passes; tag criteria-frozen | S5 ramp runs onward (MS8) |
| MS8 | Ramp study: S5 ramp runs (with the headline cell), A7 (S5 part); S13 headline subset | RB3 and the headline RB5 and RB6 checks evaluated | G6; MS9 |
| MS9 | Maps, controls, perturbation: S6, S7, S12, S16, A7 (S6 part), A9, A10 | NC1 classified; RB4 evaluated | G7, G5, G3; MS10 |
| MS10 | Network validation: S8–S10 | RB1 and RB8 (heterogeneity part) evaluated | G4; MS11 |
| MS11 | Noise and numerics: S11, rest of S13, A11 | Every RB check except the RB8 M4/adaptation parts (MS12) has a result | MS12 (only via G2 or G3); MS13 |
| MS12 | Extensions S14, S15 (only via G2 or G3) | Criteria committed before the runs | MS13 |
| MS13 | Figures F1–FS6 with provenance | Each built from a clean tree and tagged | MS14 |
| MS14 | Novelty re-check: Scholar (including cited-by checks on Xu 2023 and Borjigin 2013), PubMed, three slow-passage searches, Kalia journal version, eLife RP 104249, PMC12549018 \[R2, §6 rec. 6; RA, Recommendations\] | docs/search_log.md complete | G8; MS15 |
| MS15 | Reproducibility release (D37); manuscript and submission checklist (below Table 11.2) | Checklist 10.8 passes on a clean machine; submission checklist complete | End |

*Table 11.1. Milestones in build order (renamed MS0–MS15 in v0.4 so that milestone IDs do not collide with the model IDs M2–M4).*

| **Gate** | **Continue if** | **Stop or redirect if** |
| --- | --- | --- |
| G0 Replication (MS2, MS5) | K1–K5 and K7–K9 pass (K4-net non-blocking until the M2 network coupling is sourced; K8 without its frequency band; K9 as in Table 7.1: if its maximum differs from 0.1453, only the ratio scaling across η̄ = 1, 2, 4 blocks) | Still failing after two debugging rounds → stop new work. Check the equations against the Ceni and Devalle forms \[R1, §2.1\], the sign convention (C3) and the units |
| G1 M2 → M3 (Part 1) | As section 4.3 | As section 4.3; the move to M3 is expected |
| G2 No gamma transient (Part 1) | As section 4.3 | Move to M4 once its equations come from MPR App. E and Segneri \[R1, §2.3\], or from Dumont and Gutkin 2019 if D42 chooses that form (section 7.3). If M4 also fails, stop simulating and report a negative result, with the frequency maps as evidence \[reasoned, not tested\] |
| G3 Adaptation (Part 1) | As section 4.3 | As section 4.3 (after A7 and A9, at MS9) |
| G4 Network vs mean field (Part 1, extended) | RB1 passes | Network misses the surge at N = 10⁴ and 3×10⁴ → report a finite-size limit (Part 1). Disagreement in ≥ 2/4 cells → rerun RB6. Note the known caveats: OA attraction with synaptic kinetics is unproven, and shot noise causes metastability \[R1, §2.6\]. Report the affected results as mean-field-only |
| G5 Fine-tuning | A surge class (Table 2.1) in ≥ 3% of map-1 cells and RB4 passes | Surge only at one tuned point → no generic claim. Measure the window width; test whether P3, P4a or P4b widens it; report "narrow window" plus the failure map as the result \[R4, §6 Q6; R7, §2.7\] |
| G6 Ramp artefact | RB3(a) (on the runs inside its range; section 5.2, A7), RB3(b) and RB6 pass at the headline point; RB3(d) and RB5 are evaluated and reported | Class or floored delay depends on the solver (method or rtol; the Heun step for floored runs) → fix the numerics. Dependence on profile or δ₀ is slow-passage physics (section 4.4; RB3(d); RB5): reported, not fixed. Surge only outside 56–316 s → limit the claim |
| G7 Negative control | NC1 has no surge class at every T_ramp | Any NC1 surge → review A8 before any result is used |
| G8 Novelty | No close work found | An MPR hypoxia gamma model exists → reposition as a robustness, regime-map or E–I study and cite it as the precedent. A non-MPR model exists → keep the paper, stress what the exact mean field adds, add a comparison figure \[R2, §4\]. An MPR slow-ramp study exists → adopt its delay metrics \[R1, §4\]. v0.3 pre-check (RA): PARTIAL OVERLAP. MPR slow-passage studies exist (Taher et al. 2022 \[R1, §2.5; R5, SQ4; RA\]; Avitabile et al. 2022 \[single source: RA\]), and a non-MPR ischemia model exists without a surge (Kalia et al. 2023 \[R2; RA\]). v0.4: D41 decided (section 12.7): reframe as a first mechanistic model and cite Taher et al. 2022 and Avitabile et al. 2022 as method precedent; the third branch is met by A7's entry–exit delay metrics |

*Table 11.2. Stop-or-continue gates. G0 and G5–G8 are new. Thresholds: G0, D34; G5–G8, D35. What each gate blocks: G0 blocks S5 onward; G1 sets the model for MS5 onward; G2 and G3 open MS12; G5–G7 limit or stop the claims that depend on them; G4 and G8 are report-only for the run order (G4 limits claims to the mean field; G8 shapes the manuscript at MS15).*

**Manuscript and submission checklist (MS15).** From R7 §8(d) and R6 §6 and §8(d); checked before submission:

- A one-sentence contribution and its scope in the abstract and at the end of the introduction \[R7, §8(d)\].

- An assumptions and limitations section: the exact-reduction assumptions, the single population, the hypoxia proxy and the 2-of-4 motivation \[R7, §8(d)\], plus the limits of a power-based classifier (Table 2.1).

- Nordlie parameter tables, one per experiment or figure; every caption states the parameter regime and the take-home message \[R7, §8(d)\].

- Code archived with a version identifier, parameter files, integrator and tolerances; failure regimes reported alongside surge regimes \[R7, §8(d)\].

- No causal, clinical or consciousness claims; neutral patient language \[R7, §8(d)\].

- Conflicts of interest and AI-use disclosure \[R7, §8(d)\]; conflicts declared to the Editor-in-Chief, and reused figures, code or data credited \[R6, §8(d)\].

- Submission through the MNA site with an arXiv identifier (CC-BY 4.0 licence) and an MNA account with an ORCID; a suggested handling editor with exact mean-field or neural mass experience (Laing, Coombes and Ashwin are documented by their publications) \[R6, §6, §8(d)\].

- Before submitting, check the MNA Submission page by hand or email the editorial office for length, template and code policy; claim no specific indexing \[R6, §6\].

- Revisions: a response letter in Noble format and new arXiv versions; after acceptance, the MNA LaTeX template within 30 days \[R7, §8(d); R6, §8(d)\].

# 12. Risks, conflicts and open questions

Sources: the conflict and verification sections of every report \[R1, §3, §9; R2, §3, §9; R3, §3, §9; R4, §3, §9; R5, conflicts, verification list\], handoff (b), (g) and (h), and section 3.5. From v0.3: RA and RB.

## 12.1 Corrections to Part 1

Sections 2–6 and the handoff are Part 1. Up to v0.3 the Part 1 text was left unchanged, except the handoff (d) module paths (CP13), and these corrections applied from section 7 onward. From v0.4, sections 2–6 are edited in place where a CP row records the change (CP14–CP24, from the review triage, Appendix F; CP25–CP27, from REVIEW 5, Appendix G); the handoff stays unchanged except its (d) module paths (CP13) and the header line that says so. CP11 and CP12 were added in v0.3 from RB; CP13 followed the repository review. Additions in Part 2 (new IDs such as A0, A11 and S16, the scripts run_A0 to run_A11, and new config keys) are additions, not corrections; the preflight and section 10 list them.

| **\#** | **Part 1 says** | **Report says** | **Report, section** | **Recommended fix** |
| --- | --- | --- | --- | --- |
| CP1 | K7 (Ceni Hopf at 4.95 ms; damped at 3 ms, sustained at 8 ms) is "\[R1; R5\] verified"; section 4.1 and Table 4.1 tag the supercritical Hopf \[verified\] | Only R1 reports these values; R5's Ceni entry does not | R1 §2.3; R5 corpus \#8 | Mark K7 \[single source\]; criterion unchanged. v0.4: section 4.1 and Table 4.1 read Hopf (Devalle; Ceni) \[verified\], supercritical per Ceni \[single source\] |
| CP2 | Section 4.4: human surge lasts "to about 2 min" | R3 says seconds to ~2 min. R4 corrects this: onset is "within seconds"; the duration is not reported in the Xu main text | R3 §2.6; R4 §9 item 1 | Rat: within 30 s. Human: onset within seconds, duration not reported. D16 is unaffected |
| CP3 | "Taher" (sections 6.2, 6.3, C5, C6, D28) is not specified | The numerics and the tan formula (Eq. 8) come from Taher, Torcini and Olmi 2020; Taher, Avitabile and Desroches 2022 is the slow–fast paper | R5 corpus \#7, \#12 | Read "Taher" as the 2020 paper wherever numerics are meant \[reasoned\] |
| CP4 | Section 2.4: all negative-control physiology is "verified" | Hypothermia and deep GABAergic suppression are in R3 only; adrenergic blockade is in R2 and R3 | R3 §2.7; R2 §2.4 | Hypothermia and propofol: \[single source\] |
| CP5 | Section 6.6: "PLOS CB and JCNS require public code and parameter sets" | JCNS requires code and parameter sets; PLOS CB requires code | R7 §2.1, §2.5 | Parameter sets: JCNS only. No change to the plan |
| CP6 | Table 2.1 has no synchrony readout | R2 recommends reporting the Kuramoto order parameter \|Z\| alongside both powers | R2 §6 rec. 5 | Add \|Z\| once its formula is taken from MPR 2015 (gap; D32) |
| CP7 | Finite size appears only in FS3 | R5 puts network validation against N in main-text Fig. 5 and calls it reviewer-relevant | R5 recommendations; (c) | Add panel F5c and keep FS3 (D39) |
| CP8 | Section 6.1: the Julia one-liner with escaped quotes, and pip freeze \> … for the lock file | No report covers this. Nested quotes are unreliable in PowerShell, and \> writes UTF-16 in Windows PowerShell 5.1 | none (engineering) | Use setup_julia.jl and Out-File -Encoding utf8 \[reasoned, not tested\] |
| CP9 | Section 2.6 must-cite list contains only R2's neighbours table | R2's full must-cite list adds Coombes and Byrne, Byrne 2020, Pyragas, Gerster, Borjigin, Li, Tian, Xu, Koch, Vicente, Schramm, Shaw and others | R2 §8(d) | Use Appendix A, flag (M) |
| CP10 | K6 is listed as a runnable check | No forcing amplitude I₀ and no Δ is given for MPR Fig. 3 | R1 §2.2 | K6 is optional until these are read from MPR (D38) |
| CP11 | Table 3.1 (K9) and Table 4.1 (M3) read the critical heterogeneity as an absolute Δ ≈ 0.145 ("Δ_c per R1/Ceni"); section 5.2 (A4) runs η̄ = 2 and 4 to test Δ/η̄ scaling (C4) | δ_c = (Δ/Θ)\_c = (1/5)√(5 − 2√5) = 0.1453… is a dimensionless ratio, so Δ_c = 0.1453·Θ. Ceni's absolute value matches only because η̄ = 1 there | RB-item 2a, 2b (Devalle Eqs. 8, 20) | Read the limit as Δ/η̄ \< 0.1453 (I = 0). K9 (Table 7.1) now tests it at η̄ = 1, 2 and 4; C4 settled. Section 2.2 already used the ratio. v0.4: one K9 protocol at all three η̄ (CP15) |
| CP12 | Section 3.5 lists Devalle's Eqs. 6 and 8, the M4 equations and the deterministic Lorentzian grid as missing; Table 6.1 leaves the grid formula to be confirmed (D28) | The primary texts give Devalle Eqs. 3, 6 and 8; Taher, Torcini, Olmi 2020 Eq. 8, the same tan formula as Table 6.1; and E–I equations with first-order synapses (Dumont and Gutkin 2019, Eqs. 7–8). Ceni Eqs. 11–12, the instantaneous M4, M3a, M3b and the Cauchy-noise mean field stay unverified | RB-item 2, 5, 6; RB caveats | Use the note under Table 7.1, section 7.3 and D28 (confirmed). The rest of section 3.5 stands; the M4 form is D42 |
| CP13 | Handoff (d) lists the modules as mprsurge/… in the repository root | No report covers this. The Python Packaging User Guide (outside the seven reports) advises a src layout so the source folder cannot be imported by accident | none (engineering) | Package lives at src/mprsurge/; module names and python -m mprsurge.run are unchanged (section 10.1). Handoff (d) paths updated \[reasoned, not tested\] |
| CP14 | Section 6.2: mode D runs last 5 s + T_ramp + 10 s; mode N and network discard the first 2 s; D27; Table 2.1 Baseline | P2's J ramp ends at t_on + 1.25 T_ramp, after the run ends whenever T_ramp \> 40 s (headline: J ≈ −3.5 at run end); the 2 s discard may fall inside the 5 s baseline | v0.4 review: TRIAGE T01, T54 | P2 and the paths built on it last 5 s + 1.25 T_ramp + 10 s (headline 165 s = 16,500 τ); the discard comes before t = 0, so every baseline is 5 s. Updated: sections 4.4 and 6.2; Tables 2.1, 6.1, 9.1, 10.1; Appendix B; DL-027 |
| CP15 | Section 2.2: heterogeneity below "Δ/η̄ about 0.145"; section 5.2 (A4): K9 at η̄ = 1, J = −20, then η̄ = 2, 4 | K9 used two protocols; δ_c reads as a limit over coupling and synaptic time \[reasoned, not tested; RB does not state it\] | v0.4 review: TRIAGE T02 | One K9 protocol at η̄ = 1, 2, 4 (largest Δ/η̄ over τ_d and J; A4 checks the maximiser lies inside the J range); section 2.2 states Δ/(η̄ + I) \< 0.145 as a necessary condition only |
| CP16 | Section 5.2 (A7): "Delay shrinking as ε falls" \[R1\]; slowest-ramp onset within one A4 step of η̄\_H; delay \< 5% across rtol. Section 6.2: δ₀ added on v at t = 0 (D26) | R1 says only that a slow ramp delays onset and makes it depend on the starting state; noise removes the delay; a noise-free delay at slow ramps is set by the error floor, and δ₀ at t = 0 decays during the baseline \[reasoned, not tested\] | R1, §2.5; R5, SQ4; RA, Key finding 4; v0.4 review: TRIAGE T03, T18, T116 | A7, RB3(a)(b), RB6 and the F4/G6 trigger rewritten from delayed-Hopf theory: entry–exit prediction from the A4 eigenvalues and an explicit noise floor (D43); no scaling law entered (UNVERIFIED); δ₀ applied at t_on |
| CP17 | Section 4.3 (G1): S+ or S-rel (≥ 10 cycles in G); A2: A_min; Table 2.1: ≥ 10 cycles separates a sustained episode from the "few cycles" ring; section 2.2: "a damped ring of a few cycles" | M2 has no limit cycle, so no A_ref, and the classifier is built at MS7, after G1; cycles per e-fold ≈ πr\*²/Δ, above 10 at small Δ \[reasoned, not tested\]; ring length scales with r\*²/Δ \[R1, §2.5\] | R1, §2.5; v0.4 review: TRIAGE T06, T13 | G1 and D8 use the sign of envelope growth; the surge_metrics core and its synthetic tests are built at MS1; section 2.2 states the ring length as Δ-dependent |
| CP18 | Table 2.1: relative threshold ρ ≥ 2 × baseline ρ; classes S+, S-rel, S-sus, NS for all runs; mode-D threshold 0.1 × A_ref; relative-only tagged \[verified\] (D6, D7) | ρ ≤ 1, so a ρ ratio cannot reach 2 when baseline ρ ≥ 0.5; mode-D runs have no baseline power; absolute-only episodes have no class \[reasoned, not tested\]; R2 tags relative-only \[reasoned, not tested\], and the single case shows an absolute rise before arrest | R2, §3; R4, §2.2, §2.3; v0.4 review: TRIAGE T11, T12, T32, T52, T112 | Relative test on P_G/P_non-G; baseline ρ reported before MS7; mode-D classes D-tr, D-sus and D-none with one fixed absolute threshold (0.1 × A_ref at ref_devalle); S-abs added; "surge class" defined; Classes basis retagged; classifier limits stated in the Table 2.1 caption |
| CP19 | Table 2.1 Ordering and D9: collapse = r \< 10% of baseline or J = 0; section 2.5: collapse as J → 0; section 4.4: R2 "recommends" synaptic failure | At the stable root of the quartic, dr\*/dJ \> 0, so the rate rises as J → 0⁻ and the oscillation stops at J_exit \< 0; the ordering holds by construction \[reasoned, not tested\]. R2 lists synaptic failure as one of three options | R2, §6 rec. 4; v0.4 review: TRIAGE T14, T103 | Report J_exit and the post-surge rate; state that the P2 ordering is imposed by design; J = 0 is no longer a collapse marker; R2's options quoted |
| CP20 | D12: eta_start = η̄\_H − 1.5, eta_peak = max(4, η̄\_H + 2) | Map-1 cells with no Hopf point have no path, and cells with two crossings have no rule \[reasoned, not tested\] | v0.4 review: TRIAGE T15 | η̄\_H = the lowest Hopf crossing along η̄; cells with no Hopf point use the headline cell's eta_start and eta_peak (sections 3.2, 4.4; Appendix B; DL-012) |
| CP21 | Section 6.4: σ calibrated to the N = 10⁴ network (S8) | S8 runs at MS10, but the mode-N runs of S5 (MS8) and S7 (MS9) need σ | v0.4 review: TRIAGE T04 | σ calibrated at MS5 from one N = 10⁴ baseline run at the P2 start state of ref_devalle, frozen at MS7; S8 checks it |
| CP22 | Section 2.6: claim "the first exact (MPR) mean-field analysis of a slow hypoxia-like drift"; Taher 2022 cited to R2's neighbours table; re-check cited to R2 sec. 8b. Section 2.2: no noise caveat | RA: PARTIAL OVERLAP; frame as "first mechanistic model" and cite Taher 2022 and Avitabile 2022 as method precedent; noise removes the delay. Taher 2022 is not in R2 §8(a); R2 asks for the re-check in §6 rec. 6 and §8(e) | RA, verdict, Key finding 4, Recommendations; R2, §6 rec. 6, §8(a), §8(e); v0.4 review: TRIAGE T08, T10, T77, T99 | Claim reframed (D41 decided); Avitabile 2022 and the noisy-Hopf preprint added to the must-cite list; Taher 2022 cited to \[R1, §2.5; R5, SQ4; RA\] (locator aligned in v0.5, MC-18); re-check locator corrected; section 2.2 conditional on RB1, RB2 and S9; RB2 in the main text |
| CP23 | Sections 3–6 technical details: v\* without units (3.1); A2 fits the whole step response; A5 compares S4 amplitudes next to η̄\_H; A6 has no stated method; S13 has no stated scope; S5 omits the headline cell; Table 6.1 uses a HWHM for a uniform density; section 6.1 still shows the commands CP8 replaced; section 6.6 names outputs with \<hash8\> | Review findings \[reasoned, not tested\] | v0.4 review: TRIAGE T19, T20, T22, T36, T38, T49, T53, T56, T57, T84 | v\* given in τ-units with its dimensional form; A2 fits the tail; A5 excludes points next to η̄\_H; A6 uses continuation; S13 scope pinned (P2 at 10, 120 and 316 s; network dt ladder on the 10 s ramp; ±200 also at dt 10⁻⁴); headline cell added to S5; uniform rule half-range = Δ (D29); section 6.1 points to section 10.2; outputs named with 12 hash characters |
| CP24 | Sections 2–6 tags and locators: single-report items tagged \[verified\]; R3 grades and locators paraphrased; section 2.4 "no-surge manipulations"; Table 3.3 "Xu quantity read as absolute"; uncaptioned tables in sections 3.1, 4.3 and 4.4. Handoff (g): C1 cites Borjigin 25–250 Hz to \[R3; R4\], C9 lists a sign-convention difference as a conflict, C14 says "Lee 320 vs 400 s" | R3 §2.5 grades η̄ "High for direction in window" and J "Medium"; R3's local plus non-local recommendation is in §6 and §8(c), not §4; R3 §2.7 proposes predicted no-surge manipulations; R4 §2.1 reads Xu's absolute power by DFT; 25–250 Hz is in R2 §2.4 and R3 §2.6; the 320 vs 400 s figures are Li 2015 \[R4, §3\]; from the M2 eigenvalues a node needs J \> 2π²r\* \> 0 | R2–R7 as cited; v0.4 review: TRIAGE T59, T72, T75, T76, T82, T98, T100, T101, T102, T106, T108, T109, T114, T115 | Tags and locators corrected in place (sections 2.3, 2.4, 3.1, 3.3, 4.1, 4.4, 4.5, 6.3, 6.6; Tables 2.1, 3.2, 3.3, 4.1, 6.1); captions for Tables 3.1, 4.2 and 4.3 added. Handoff (g) is left unchanged; its C1, C9 and C14 corrections are in Table 12.2 |
| CP25 | Section 5.2 (A4, A7): entry–exit relation ∫ Re λ(η̄) dη̄ = 0 from eta_start; RB3(a) judged on every run "within one A4 step", with no η̄ grid; D43 floor runs with no named integrator and an rtol test; "Noise removes the delay" and "shrinks as the floor rises" cited to RA; A7 needs S6 (MS9) but is done at MS8. Section 6.2: Heun not linked to D43 | In noise-free runs at slow ramps the delay is set by the floor, so RB3(a) predicts its own failure; the η̄ integral equals the time integral only for constant dη̄/dt and fixed J; Heun has a fixed step, so rtol has no meaning; RA states only that noise eliminates the delay \[reasoned, not tested; single source: RA\] | v0.5 review: REVIEW 5, SC-01, SC-02, SC-03, MC-04, MC-16, MC-26 | RB3(a) range from A4 (δ₀·exp(∫ Re λ dt′) above the floor); onset compared with t_pred; entry–exit integral along the path in time; A4 η̄ grid named (spacing UNVERIFIED); D43 runs on stochastic Heun, RB6 varies the Heun step; RA claims tagged, monotone relation \[reasoned, not tested\]; A7 split over MS8 and MS9. Updated: sections 2.2, 5.2 (A4, A7), 6.2; Table 6.2 (S13) |
| CP26 | Table 2.1: damped vs sustained by the sign of envelope growth (growth ≥ 0 = sustained), with no fit window; one J_exit; S-abs not told apart from broadband growth. Section 4.3 (G1): "sustained" episode. Section 5.2: A8 tests only a 5-cycle ring; A9 labels (a)–(e); A4 states the K9 maximisation as fact. Section 2.2: the necessary-condition consequence untagged | "Sustained" has two senses; a single fitted sign is undefined for a transient and has no tolerance; a damped ring of more than 10 cycles is untested; a below-threshold oscillation fits no label; static and observed J_exit differ under delayed exit; the δ_c-as-limit reading is UNVERIFIED but blocks G0 \[reasoned, not tested\] | v0.5 review: REVIEW 5, SC-05 to SC-10 | Fit window from the threshold crossing over the first 10 cycles; damped only if negative by more than 2 standard errors; D8 sense renamed "non-damped"; J_exit,static and J_exit,run; S-abs "broadband" flag; A8 slowly damped ring test; A9 label (f); K9 maximisation \[reasoned, not tested\] with the D11 τ_d range, a stopping rule and a ratio-scaling fallback. Updated: sections 2.2, 2.5, 4.3, 4.4, 5.2 (A2, A4, A8, A9); Table 2.1 |
| CP27 | Tables 3.1, 3.2, 6.1, 6.2 and sections 2.4, 2.5, 2.6, 3.3, 6.7: K7 and K9 tags differ from Table 7.1; single-report items tagged \[verified\]; section 2.4 hypothermia physiology \[verified\]; Table 6.1 D28 "needs decision" and no M2 network coupling; Table 6.2 has no S16 row, no K8 network size and no run for the baseline ρ report; D10 not cited by ID; Taher 2022 cited to \[R1, §4\]; sections 6.7 and 8 tag the page budget differently | Table 7.1 and the CP rows govern; CP4: hypothermia and propofol \[single source\]; D28 settled \[RB-item 6\]; no attached source gives the M2 network coupling (T51); baseline ρ "before MS7" has no run in milestone order | v0.5 review: REVIEW 5, MC-01, MC-03, MC-11 to MC-15, MC-18, MC-21, MC-22, MC-27 | Tags and locators corrected in place (sections 2.4, 2.5, 2.6, 3.3, 6.7; Tables 3.1, 3.2, 6.1); the M2 network coupling listed as UNVERIFIED (Table 6.1, section 12.4) and K4-net non-blocking until sourced; Table 6.2 gains the S16 row, N = 5×10⁴ for K8 (S3), the MS7 baseline-only runs (S5) and the K4-net condition (S1) |

*Table 12.1. Corrections to Part 1 (27 rows; CP11–CP13 added in v0.3, CP14–CP24 in v0.4, CP25–CP27 in v0.5).*

## 12.2 Conflicts between reports

C1–C15 are given with their values and sources in handoff (g), now an appendix. C16–C19 are new. No conflict is settled silently. v0.3 updates C4, C5, C10 and C15 from RB. v0.4 adds C20–C24 and corrects C1, C5, C9, C10 and C14 (handoff (g) is left unchanged; this table governs).

| **ID** | **Topic** | **Resolution (test or primary-source check)** |
| --- | --- | --- |
| C1 | Gamma band edges; R3 adds "25–140+ Hz" \[R3, §2.6\]. Borjigin 25–250 Hz is in R2 §2.4 and R3 §2.6, not R4 (handoff (g) cites \[R3; R4\]); R4 gives Borjigin low gamma 25–55 Hz (coherence 35–55 Hz) and an early high-gamma component near 130 Hz \[R4, §2.2, §8(a)\] | D2; RB9(c), RB10. Report both bands if \> 5% of cells change class; the 130 Hz component is covered only by γ2 (Table 2.1 caption) |
| C2 | M3 frequency: Devalle gamma vs Ceni 5–30 Hz | A6, K8, K10; G2 |
| C3 | Sign of J | Section 3.1 convention; K7, K8 |
| C4 | Δ_c 0.1453: absolute (R1) or Δ/Θ (R5) | Settled by RB: δ_c = (Δ/Θ)\_c = 0.1453… is a dimensionless ratio (Devalle Eq. 8; δ = Δ/Θ, Eq. 20; Θ = centre of the Lorentzian, Eq. 14), so Δ_c = 0.1453·Θ. Ceni's absolute Δ_c ≈ 0.1453 coincides because η̄ = 1 there \[RB-item 2a, 2b\] \[verified: R5; RB\]. K9 now tests the ratio at η̄ = 1, 2, 4 (Table 7.1; CP11) |
| C5 | Lorentzian grid: arctan vs tan | D28 confirmed against Taher, Torcini, Olmi 2020 Eq. (8), η_i = H + Δ tan\[(π/2)(2i − N − 1)/(N + 1)\] (median H, half-width Δ) \[RB-item 6\], the same as the D28 default. RB read MPR App. A (RB-item 1b) but did not report its grid formula, so the arctan/tan wording in MPR stays unread in the evidence base \[R5, conflicts\]. The quantile test stays in test_qif_network |
| C6 | Network dt and V_p | RB6 |
| C7 | Xu power: posterior vs frontal/central | Use R4 (corrected in R4 §9); not modelled |
| C8, C14 | Fold change 391 vs 392; inconsistencies inside data papers; C14's "Lee 320 vs 400 s" is Li 2015 \[R4, §3\] | Not used numerically |
| C9 | M2: node region vs "always focus" | A1 (K2). Not a real conflict: from the M2 eigenvalues (section 3.1) a node needs J \> 2π²r\* \> 0 (excitation), while Devalle's "always focus" result concerns instantaneous inhibitory synapses \[reasoned, not tested\] |
| C10 | Content and DOI of the Gast erratum | Settled in content \[R1, §2.3; R5, SQ1\] \[verified\]; RB-item 4 (PARTIAL) quotes the erratum prose: the erratum (10.1162/neco_c_01397) identifies an erroneous scaling of r with τA in Eq. 3.6; Eq. 7.3 is its corrected form, and the α values for synchronized bursting hold only for the depression system Eqs. 7.2–7.3; results are unchanged because τA was never varied. DOI: RB gives neco_a_01300 for the original article, agreeing with R1 and R2. Still open: the corrected equations (seen only in a search-engine rendering) and the published Eqs. 3.5–3.8 and 4.7–4.8 \[RB-item 4: PARTIAL / UNVERIFIED\]; read the publisher PDF before G3 (section 7.3) |
| C11 | Interneuron vulnerability | D22; no direction assumed |
| C12, C13 | Rat surge timing; source of the Xu heart-rate claim | Qualitative only; use R4 |
| C15 | Ceni DOI; Δ 0.5 vs 0.05 | Use 1.5125216 and 0.05; K7 tests it. RB reads that DOI and, for the Fig. 1 Hopf point, Δ = 0.05 (η̄ = 1, J = −20, τ = 10 ms, τ_d^(H) = 4.95 ms), but only in arXiv v1 \[RB-item 3: PARTIAL\], so C15 stays open. Δ = 0.5 would exceed 0.1453 and allow no oscillation \[reasoned\] |
| C16 | Human surge duration: ~2 min \[R3, §2.6\] vs not reported \[R4, §9, corrected\] | Use R4 (CP2) |
| C17 | Cauchy-noise run recommended \[R1, §6\] vs no equations in any report | Not run (D33) |
| C18 | Finite size in the main text \[R5, (c)\] vs FS3 \[Part 1\] | CP7, D39 |
| C19 | "Global hypoxia" framing vs Xu Pt3 dying of brain haemorrhage \[R2, §3; R4, §2.1\] | Scientific risk 5; claims stay qualitative |
| C20 | Taher et al. 2022: monotone drift ("a slowly drifting external current") \[R1, §2.5\] vs slow periodic forcing \[R5, SQ4; RA\] | Decides whether Taher 2022 is a monotone-drift precedent. Cited as a method precedent either way (D41, section 12.7); read the full text at MS14 |
| C21 | MPR slow-forcing bursting: R3 cites MPR Fig. 3 \[R3, §2.6\]; R1 and RB place it in Fig. 2 (Fig. 3 is fast forcing, giving chaos) \[R1, §2.2; RB-item 1b\] | Use Fig. 2 (K5); R3's figure label is not used |
| C22 | Calibration and scope: RA recommends ramp-rate predictions "against measured surge latencies" and linking η̄(t) and J(t) to O₂ or ATP \[RA\]; R4 says the data do not support calibrating to onset latencies in human seconds \[R4, §1\]; O₂ and ATP are out of scope (section 2.5) \[R2\] | Not adopted (section 12.7); timing stays a qualitative target |
| C23 | Schramm et al.: 2019 \[RA\] vs Prog Neurobiol 185:101733 (2020) \[R2; R4\] | Use 2020 (Appendix A, 40) |
| C24 | Wang–Buzsáki networks show oscillation–asynchrony bistability at small τ_d that "is not present in the QIF-FRE" (Devalle) \[R1, §3\] | Different models; recorded as a limit on how far the regime map generalises (Table 12.3, risk 13) |

*Table 12.2. Conflicts and how each is resolved.*

## 12.3 Items marked \[needs decision\]

There are 43 D-items: D1–D31 inherited from Part 1, D32–D40 new in Part 2, D41–D42 new in v0.3 and D43 new in v0.4. RB settled D28 in v0.3 and D41 was decided in v0.4, so 41 remain \[needs decision\]. D43 counts among them although it has no default value yet, because under the Conventions its default is set at a named milestone (MS7). Appendix C gives each one's default, the test that could overturn it, and its status. The items with most leverage, and how each is settled:

- D2: tested by RB9(c) and RB10; D6–D8 (detection): tested by RB10.

- **D12, D19** (paths): tested by RB4.

- **D13, D20** (Δ): both directions are run.

- **D22** (interneuron drive): settled by G2(c).

- **D23** (continuation tool): decided by the MS1 smoke test.

- **D25, D26** (solver): tested by RB5 and RB6.

- D34 (tolerances): frozen at the end of MS1; D35 (thresholds): frozen at MS7.

- D40 (headline): default fixed now; confirmed at MS6, before S5.

- D41 (G8 next step): decided in v0.4; section 12.7.

- **D42** (M4 form): decided before S14 or any RB8 M4 run; section 7.3.

- D43 (slow-passage noise floor): levels set at MS7, before criteria-frozen; run with stochastic Heun; tested by RB3(b) and RB6; section 5.2 (A7).

## 12.4 Not verified

v0.3: items that RB verified were removed from this list and entered where they are used: Devalle Eqs. 3, 6 and 8 and δ_c (Table 7.1 and the note under it; Appendix B), the Lorentzian grid formula (D28, C5), and the E–I equations with first-order synapses (section 7.3). What the Gast erratum corrects (section 7.3, C10) rests on R1 and R5; RB-item 4 is PARTIAL and adds no tag (v0.4). Items that RB marks PARTIAL or UNVERIFIED stay here.

- Ceni Eqs. 11–12 and the Hopf value τ_d^(H) = 4.95 ms (K7): RB read them only in arXiv v1, and the first numerator term of Eq. 11 may be garbled by text extraction \[RB-item 3: PARTIAL; RB caveat 3\]. A4 re-derives the Hopf condition numerically.

- The M2 network coupling for K4-net (v0.5): Table 6.1's synapse rule is for M3, and no attached source gives the M2 network coupling (T51; UNVERIFIED). K4-net is non-blocking until a source gives it (Table 7.1; G0); no coupling is entered.

- Values that v0.5 fixes need but no source gives (UNVERIFIED), each set at MS7 before criteria-frozen: the solver and noise floor values that bound the RB3(a) range; the spacing of the A4 η̄ grid used for the entry–exit comparison; and the rungs of the Heun dt ladder below 10⁻³ τ (RB6) (section 5.2, A4 and A7; Table 7.2).

- The M4 equations in the Table 4.1 form (instantaneous synapses), the M3a equations (Gast et al. Eqs. 3.5–3.8 and 4.7–4.8, and erratum Eqs. 7.1–7.3) and the M3b equations \[R1, §8(e); RB-item 4: PARTIAL / UNVERIFIED; RB-item 5\]. They must come from primary sources before S14 or S15.

- The Cauchy-noise and Gaussian reductions (D33; RB does not cover them). The \|Z\| formula (D32): RB found only the complex Z–W map, MPR Eq. 18, in arXiv v1 and no printed \|Z\| formula \[RB-item 1a: PARTIAL\]. The K6 forcing amplitude and Δ (D38): arXiv v1 only, with Δ from App. A rather than the Fig. 3 caption \[RB-item 1b: PARTIAL\].

- Δ during hypoxia, and the magnitudes of the η̄ ramp, J weakening and drive \[R3, §3, §7\].

- Xu SI: sedation, stage durations, heart-rate values \[R4, §7\].

- Runtimes \[R5, gap statement\]: replaced by the timing gate.

- Windows support for BifurcationKit and PyRates \[R5, SQ5\].

- MNA length and code policy \[R6, §7\].

- Native Scholar and PubMed searches \[R2, summary; R2, §2.6; R2, §7\]: RA again used a general web-search engine only and did not walk the cited-by lists of Borjigin 2013 and Xu 2023 \[RA, Caveats\]; MS14 still requires them. R2's own search counts also differ: about 30 differently worded searches \[R2, summary\], 5 own plus at least 7 subagent direct-hit queries \[R2, §2.6\], 14 further subagent queries \[R2, §2.1\], and more than 10 \[R2, verification list\]. RA did run four slow-passage or slow-ramp queries (Appendix E, queries 3, 8, 12 and 16).

- Whether OA attraction holds with synaptic kinetics, and whether the Hopf is sub- or supercritical along the path \[R1, §2.6, §8(e)\]: tested by RB1 and A5.

- Published versions RB did not read: MPR 2015 in Phys Rev X (equation numbers and the Fig. 3 caption may differ from arXiv v1) and Ceni 2020 in Chaos \[RB, caveats 1 and 3\]. The Devalle Fig. 4 Hopf-boundary δ values differ between arXiv v3 (0.05) and the PLOS rev=1 text (0.035); this plan does not use them \[RB, caveat 5\].

## 12.5 Scientific risks

| **\#** | **Risk** | **Test or resolution** | **Gate** |
| --- | --- | --- | --- |
| 1 | **Circularity of tuning.** The headline point is Devalle's gamma point (K8), and τ_d and the drive are chosen so that gamma is possible \[R1, §6\]; reviewers check claims against evidence \[R7, §2.1\] | Report the surge-class fraction of the pre-registered ranges, not one point. Fix D40 and D35 before S5. Run RB4. Separate "the window exists" (A4, A6) from "the ramp crosses it" (A7), and say openly how the parameters were chosen | G5 |
| 2 | **Competing mechanisms.** PING vs ING; adaptation vs synaptic failure; ion or pump route \[R2, §2.1\]; seizure-like activity \[R4, §2.5\]; non-local drive \[R3, §2.4\]; myogenic or volume-conducted signals \[R4, §2.5\] | M4 or M3a via G2/G3; NC2. Claim only "sufficient under conditions X" \[R4, §6 Q5; R7, §2.7\]. State that data-side alternatives are not addressed | G2, G3 |
| 3 | **Specificity.** Any slow upward drift through a Hopf point gives a transient, and termination is imposed by J → 0 | NC1–NC3. P1 is expected to give D-sus (S-sus in mode N). Specificity rests on the order of events and on termination \[reasoned, not tested\] | G7 |
| 4 | **Identifiability.** η̄ and I share one term; the inhibitory population's drive may fall early (C11); the direction of Δ is unknown \[R3, §3\] | Claim only the time course; run both Δ paths; use M4 for local vs non-local (section 4.5) | G2(c) |
| 5 | **Measurement uncertainty (targets).** n = 2 humans with EMG contamination; relative vs absolute power; band edges; preparation effects; Pt3 haemorrhage \[R4, §2.5–2.6, §8(c); R2, §3\] | Use only R4 targets 1–4 \[R4, §8(d)\]; report both powers; RB9(c), RB10; fit no fold changes | — |
| 6 | **Measurement uncertainty (model).** Zero deterministic baseline; no v-to-EEG forward model; window choice | Mode D and mode N definitions; A8 synthetic tests; RB10; NC1 | G7 |
| 7 | **Finite size and metastability** \[R1, §2.6\] | RB1, S9, F5c | G4 |
| 8 | Slow-passage numerics. Onset delay depends on ramp rate, profile and starting state \[R1, §2.5; R5, SQ4\]; noise can remove it \[RA, Key finding 4\]; ODE results can change with floating-point and solver settings \[R7, §2.6\] | RB3, RB5, RB6, δ₀ ladder, D43 noise floor | G6 |
| 9 | **Frequency labels** depend on the τ = 10 ms convention \[R1, §2.4\] | RB9(d) | — |
| 10 | **A precedent is found** at the re-check | Follow the G8 actions \[R2, §4\]. RA pre-check: PARTIAL OVERLAP; D41 decided in v0.4 (section 12.7); MS14 still runs | G8 |
| 11 | Noise or finite size removes the delayed onset: "adding noise to a slow-fast model eliminates the bifurcation delay" \[RA, Key finding 4; Appendix A, 68\] \[single source: RA, which read the preprint at introduction depth\] | RB1, RB2 (main text), S9, S11; section 2.2 is conditional on them; read the preprint in full before it drives design | G4, G6 |
| 12 | Journal depth: "recent MNA papers lean towards proofs and stochastic analysis" \[R6, summary\], and "simulation-only results without analysis" would feel out of scope \[R6, §2.5\] | The A4 Hopf location and the A7 entry–exit delay prediction as analytical results, confirmed against the network \[R6, §6 rec. 4\] \[needs decision\] | G8 |
| 13 | Wang–Buzsáki networks lose oscillations at about 6% heterogeneity, below the QIF value, and show oscillation–asynchrony bistability not present in the QIF-FRE \[R1, §2.6, §3; R5, conflicts\] (C24) | State the limit on how far the regime map generalises; RB8 (heterogeneity shape) | G5 |

*Table 12.3. Scientific risks.*

## 12.6 Open questions

- Do failure regimes correspond to the observed absences: Xu Pt2 and Pt4 without a heart-rate rise, brain death, or coherence without a power rise? R4 calls these candidate correlates, untested as model mappings \[R4, §6 Q6\]. Report them as hypotheses only.

- How should the surge end? Options: synaptic failure (the default), a bounded-voltage QIF variant, or a rate ceiling \[R2, §6 rec. 4\]. Revisit only if G3 triggers.

- Will onset be delayed or advanced? A low-frequency Hopf can advance onset \[R5, SQ4\]. A7 reports the sign either way.

## 12.7 G8 result

**Verdict: PARTIAL OVERLAP** \[RA\]. RA found no paper that models the terminal gamma surge (Borjigin et al. 2013; Xu et al. 2023) with an exact mean-field (MPR) model or with a slow passage through a Hopf bifurcation, and no paper that models the surge mechanistically at all. Each part of the method has precedent, so the novelty lies in combining the parts and applying them to this phenomenon, not in the mathematics \[RA, verdict\] \[single source: RA\]. The research question (section 2.1) and the models are unchanged; the claim is reframed in v0.4 (D41).

Papers that decide the verdict \[RA, TL;DR and comparison table\]:

- **Taher, Avitabile and Desroches 2022**, Nonlinear Dyn 108:4261: slow passage through a Hopf bifurcation in an exact QIF mean field with short-term plasticity, giving elliptic-like bursting; not death and not a one-off transient (Appendix A, 15) \[R1, §2.5; R5, SQ4; RA\] \[verified that it exists; drift type: C20\].

- **Avitabile, Desroches and Ermentrout 2022**, PLoS Comput Biol 18:e1010569: QIF networks and their mean field under slowly varying input, where "canard solutions are the fabric of excitability thresholds"; canard-based, not a gamma Hopf (Appendix A, 67) \[single source: RA\].

- **Kalia, Ligtenstein, Meijer and van Putten 2023**, bioRxiv: ion-based, non-MPR thalamocortical neural mass of EEG in ischemia with an O₂ bath; the EEG slows and then goes into synaptic arrest, a supercritical Hopf appears in parameter sweeps, and there is no gamma surge (Appendix A, 23) \[R2; RA\] \[verified\].

- **"Noisy neural systems with static and dynamic Hopf bifurcation parameters"**, bioRxiv 2025: adding noise removes the bifurcation delay and gives quasi-cycles below the Hopf point; RA calls this "a direct threat" to a delayed-onset mechanism (Appendix A, 68) \[single source: RA, introduction read; its "Section 5.2" quote comes from a part RA did not read (Appendix E)\].

- Energy-failure models without a gamma surge: Zandt et al. 2011 (single neuron; Appendix A, 26) and Roberts et al. 2023, Nat Commun 14:4792 (Hodgkin–Huxley E–I network with oxygen-dependent pumps; abstract only; Appendix A, 69). Zandt \[R2; RA\] \[verified\]; Roberts \[single source: RA, abstract only\].

**What the plan still adds.** RA lists six contributions that no paper has made \[RA, "What your plan would still add"\]. How each maps onto this plan is \[reasoned, not tested\]:

- A first mechanistic, exact-mean-field model of the surge: the claim in section 2.6, reframed in v0.4 to this wording (D41).

- ING versus PING routes under a hypoxia-like ramp: M3 is ING; M4 enters only through G2 or RB8 (D42).

- Ramp-rate dependence of onset and size: A7, RB3 and F4.

- A closed rise-and-fall trajectory: on P2 the oscillation stops as J weakens, at J_exit,static \< 0 (observed end J_exit,run); the rate rises rather than falls, so the "fall" is loss of oscillation, imposed by design (Table 2.1; CP19).

- Whether the delay survives noise and finite size: RB1, RB2, S9 and S11. RA calls noise "the main scientific risk". From v0.4, RB2 is a main-text result and Table 12.3 lists the risk (row 11).

- Outputs that separate a neural surge from artefact: the plan reports peak frequency; cross-frequency coupling and coherence are out of scope (section 2.5).

**Limits of the check.** RA used a general web-search engine only (Appendix E). It did not query Google Scholar, medRxiv or PubMed natively, did not walk the cited-by lists of Borjigin 2013 and Xu 2023 \[RA, Caveats\], and its query 19 failed (search budget exhausted) \[RA, search log\]. MS14 is therefore not complete.

**RA's recommendations** \[RA, Recommendations\]. Go ahead, but frame the claim as "first mechanistic model" rather than "first slow-passage MPR analysis"; cite Taher et al. 2022 and Avitabile et al. 2022 as methodological precedent and Kalia et al. 2023 as the nearest application; make noise robustness a main result; link η̄(t) and J(t) to O₂ or ATP; and re-run a Google Scholar cited-by check on Xu 2023 and Borjigin 2013 before submission. v0.4 adopts all except the O₂/ATP link, which stays out of scope (section 2.5; C22).

**D41, decided in v0.4.** The claim is reframed (section 2.6) and RA's recommendations are adopted as above. G8's third branch ("An MPR slow-ramp study exists → adopt its delay metrics") is taken as triggered by Taher 2022 and met by A7's entry–exit delay metrics (section 5.2). MS14 still runs before writing, including the Scholar cited-by checks.

# Appendix A. Source list

Every source cited in this document, with the identifiers the reports give. "(M)" marks R2's must-cite list \[R2, §8(d)\]. A DOI is listed only where a report gives one; "not given" means no report gives one, and none was added. From v0.3, RA and RB are also sources; rows 67–70 come from them, with the identifiers they give.

| **\#** | **Source** | **DOI / URL (as given in the reports)** | **Report(s)** |
| --- | --- | --- | --- |
| 1 | Montbrió, Pazó, Roxin 2015, Phys Rev X 5:021028 (M) | 10.1103/PhysRevX.5.021028; arXiv 1506.06581 | R1, R2, R3, R5, R6, RB |
| 2 | Devalle, Roxin, Montbrió 2017, PLoS Comput Biol 13:e1005881 | 10.1371/journal.pcbi.1005881; arXiv 1705.09205 | R1, R3, R5, RB |
| 3 | Ceni, Olmi, Torcini, Angulo-Garcia 2020, Chaos 30:053121 (M) | 10.1063/1.5125216; arXiv 1908.07954 (5.0017527 not used, C15) | R1, R2, R5, RB |
| 4 | Segneri, Bi, Olmi, Torcini 2020, Front Comput Neurosci 14:47 (M) | 10.3389/fncom.2020.00047; arXiv 2003.04000 | R1, R2, R5 |
| 5 | Gast, Schmidt, Knösche 2020, Neural Comput 32:1615–1634, and erratum 33(6):1717 (2021) | 10.1162/neco_a_01300 \[R1; R2; RB\] or neco_a_01369 \[R5\] (C10); erratum 10.1162/neco_c_01397 | R1, R2, R5, RB |
| 6 | Chen, Campbell 2022, J Comput Neurosci 50:445–469; ModelDB 267382 | 10.1007/s10827-022-00825-9; arXiv 2203.08341 | R1, R2, R5 |
| 7 | Pietras, Clusella, Montbrió 2025, Phys Rev E 111:014422 | not given | R1 |
| 8 | Clusella, Montbrió 2024, Phys Rev E 109:014229 | arXiv 2208.05515 | R1 |
| 9 | Goldobin et al. 2024, Chaos 34:013121 | not given | R1 |
| 10 | Klinshov, Kirillov 2022, Phys Rev E 106:L062302; Kirillov, Smelov, Klinshov 2024, Chaos 34:053120 | not given | R1 |
| 11 | Ott, Antonsen 2008, Chaos 18:037113; 2009, Chaos 19:023117 | 10.1063/1.2930766; 10.1063/1.3136851 | R1 |
| 12 | Pietras, Daffertshofer 2016, Chaos 26:103101 | not given | R1 |
| 13 | Baer, Erneux, Rinzel 1989, SIAM J Appl Math 49:55–71; Baer, Gaekel 2008, Phys Rev E 78:036205 | PubMed 18851119 (2008) | R1, R5 |
| 14 | Kaper, Vo 2018, Chaos 28:091103 | 10.1063/1.5050508 | R1, R5 |
| 15 | Taher, Avitabile, Desroches 2022, Nonlinear Dyn 108:4261–4285 | 10.1007/s11071-022-07406-6; arXiv 2109.06757 | R1, R2, R5, RA |
| 16 | Taher, Torcini, Olmi 2020, PLoS Comput Biol 16:e1008533 | 10.1371/journal.pcbi.1008533 \[RB\]; arXiv 2010.07071 | R5, RB |
| 17 | Ferrara, Angulo-Garcia, Torcini, Olmi 2023, Phys Rev E 107:024311 | arXiv 2210.04673 | R5 |
| 18 | Coombes, Byrne 2019, book chapter, pp. 1–16; arXiv 1607.06251 (M) | 10.1007/978-3-319-71048-8_1 | R1, R2, R6 |
| 19 | Byrne et al. 2020, J Neurophysiol 123:726–742 (M) | 10.1152/jn.00406.2019 | R1, R2, R5 |
| 20 | Pyragas, Pyragas 2021, Phys Lett A 416:127677 (M) | arXiv 2107.03150 | R2 |
| 21 | Nandi, Valla, di Volo 2024, Front Comput Neurosci 18 (M) | 10.3389/fncom.2024.1422159 | R2, R4 |
| 22 | Gerster et al. 2021, Front Syst Neurosci 15:675272 (M) | 10.3389/fnsys.2021.675272 | R2 |
| 23 | Kalia, Ligtenstein, Meijer, van Putten 2023, bioRxiv (M) | 10.1101/2023.04.07.535995; github mkalia94/BioNeuralMass | R2, RA |
| 24 | Bandyopadhyay, Bernard, Jirsa, Petkoski, ion-exchange mean field (M) | 10.1101/2021.10.29.466427; elifesciences.org/reviewed-preprints/104249 | R2, R5 |
| 25 | Ruijter et al. 2017, Clin Neurophysiol (M) | PubMed 28753456 | R2 |
| 26 | Zandt et al. 2011, PLoS ONE 6:e22127 (M) | 10.1371/journal.pone.0022127 | R2, R4, RA |
| 27 | Zandt et al. 2013, J Neurophysiol | 10.1152/jn.00250.2013 | R3 |
| 28 | Kager, Wadman, Somjen 2000, J Neurophysiol 84:495–512 (M) | 10.1152/jn.2000.84.1.495 | R2, R3 |
| 29 | Wei, Ullah, Schiff 2014, J Neurosci 34:11733–11743; Ullah et al. 2015, PLoS Comput Biol 11:e1004414 (M) | 10.1523/JNEUROSCI.0516-14.2014 | R2, R3 |
| 30 | Dehmelt, Machens 2013, BMC Neurosci 14(Suppl 1):P251 (M) | 10.1186/1471-2202-14-S1-P251 | R2 |
| 31 | Ching et al. 2012, PNAS (burst suppression) (M) | not given | R2 |
| 32 | Rabuffo et al. 2021, eNeuro 8(5) | 10.1523/ENEURO.0283-21.2021 | R2 |
| 33 | Two-phase QIF neurons (bounded voltage), preprint | arXiv 2603.03870 | R2 |
| 34 | Borjigin et al. 2013, PNAS 110:14432 (M) | 10.1073/pnas.1308285110 | R2, R3, R4 |
| 35 | Xu et al. 2023, PNAS 120(19):e2216268120; raw EDF on Zenodo (M) | 10.1073/pnas.2216268120; 10.5281/zenodo.7803212 | R2, R3, R4, R6 |
| 36 | Li et al. 2015, PNAS 112:E2073 (M) | 10.1073/pnas.1423936112 | R2, R3, R4 |
| 37 | Tian et al. 2018, Front Physiol 9:99 (M) | 10.3389/fphys.2018.00099 | R2, R3 |
| 38 | Koch 2023, PNAS commentary (M) | 10.1073/pnas.2305985120 | R2, R3, R4 |
| 39 | Vicente et al. 2022, Front Aging Neurosci 14:813531 (2022 single-patient case) (M) | 10.3389/fnagi.2022.813531 | R2, R4 |
| 40 | Schramm et al. 2020, Prog Neurobiol 185:101733 (M) | 10.1016/j.pneurobio.2019.101733 | R2, R4 |
| 41 | Shaw 2024, F1000Research 13:674 (the F1000 critique) (M) | 10.12688/f1000research.151422.2 | R2, R4 |
| 42 | Greyson, Kelly, Dunseath 2013, PNAS letter | 10.1073/pnas.1316937110 | R4 |
| 43 | Lee et al. 2017, Brain Connectivity 7:172 | 10.1089/brain.2016.0471 | R4 |
| 44 | Zhang et al. 2019, Front Neurosci 13:800 | 10.3389/fnins.2019.00800 | R4 |
| 45 | Chawla et al. 2009, J Palliat Med; Chawla et al. 2017, Death Stud 41:385 | 10.1089/jpm.2009.0159; 10.1080/07481187.2017.1287138 | R4 |
| 46 | Norton et al. 2017, Can J Neurol Sci 44:139; Auyong et al. 2010, Anesth Analg 110:1428 | not given | R4 |
| 47 | Gofton et al. 2022, Am J Transplant; Matory et al. 2021, Neurocrit Care 35:853 | 10.1111/ajt.17146; 10.1007/s12028-021-01233-0 | R4 |
| 48 | Dreier et al. 2018, Ann Neurol 83:295–310 | 10.1002/ana.25147 | R3, R4 |
| 49 | Hartings/Dreier et al. 2022, Neurocrit Care (COSBID) | PMC9259543 | R3 |
| 50 | Revah et al. 2016, Neurobiol Dis; Fleidervish et al. 2001, J Neurosci | PMID 11425888 (2001) | R3 |
| 51 | Khazipov et al. 1995 | PMID 7907132; 7714586 | R3 |
| 52 | Kentar et al. 2023, J Cereb Blood Flow Metab 43:999; Takaoka et al. 1996, Neurosci Lett | PMC10196741 (2023) | R3 |
| 53 | Dean et al. 2019, Sci Rep 9 (DMT; disputed) | 10.1038/s41598-019-45812-w | R3 |
| 54 | Bird et al. 2025, Nat Med 31:3542 | 10.1038/s41591-025-03889-z | R4 |
| 55 | Mashour, Lee, Pal, Li 2024, Anesthesiology 140:1221–1231 | 10.1097/ALN.0000000000004970 | R4 |
| 56 | Sandve et al. 2013, PLoS Comput Biol 9:e1003285 | 10.1371/journal.pcbi.1003285 | R5, R7 |
| 57 | Nordlie, Gewaltig, Plesser 2009, PLoS Comput Biol 5:e1000456 | 10.1371/journal.pcbi.1000456 | R5, R7 |
| 58 | Pauli et al. 2018, Front Neuroinform | 10.3389/fninf.2018.00046 | R7 |
| 59 | J Comput Neurosci 2020 non-replicability paper | 10.1007/s10827-020-00748-3 | R7 |
| 60 | BifurcationKit.jl documentation | docs.sciml.ai; bifurcationkit.github.io | R5 |
| 61 | PyRates docs (tutorial 3.1); Gast et al. 2019, PLoS ONE; Gast, Knösche, Kennedy 2023, PLoS Comput Biol | pyrates.readthedocs.io; 10.1371/journal.pone.0225900; 10.1371/journal.pcbi.1011761 | R5 |
| 62 | AUTO-07p; XPPAUT; MatCont; PyDSTool (tool pages) | github.com/auto-07p/auto-07p/releases; github.com/Ermentrout/xppaut; sites.pitt.edu/~phase/bard; SourceForge MatCont; github.com/robclewley/pydstool | R5 |
| 63 | MNA Home and Editorial Policies | https://mna.episciences.org/; https://mna.episciences.org/page/editorial-policies | R6, R7 |
| 64 | PLOS Comput Biol reviewer guidelines; JCNS submission guidelines | https://journals.plos.org/ploscompbiol/s/reviewer-guidelines; https://link.springer.com/journal/10827/submission-guidelines | R7 |
| 65 | Gale et al. 2022, MNA 2:1; Victor et al. 2025, MNA (code-sharing precedents) | 10.46298/mna.8390; 10.46298/mna.12457 | R6 |
| 66 | Spatiotemporal complexity paper, a lead to check at G8 | PMC12549018 | R2 |
| 67 | Avitabile, Desroches, Ermentrout 2022, PLoS Comput Biol 18:e1010569 | 10.1371/journal.pcbi.1010569; PMC9560555 | RA |
| 68 | "Noisy neural systems with static and dynamic Hopf bifurcation parameters", bioRxiv preprint 2025 | 10.1101/2025.08.04.668381 | RA |
| 69 | Roberts et al. 2023, Nat Commun 14:4792 | 10.1038/s41467-023-40437-0 | RA |
| 70 | Dumont, Gutkin 2019, PLoS Comput Biol 15(5):e1007019 | 10.1371/journal.pcbi.1007019; PMC6529019 | RB |

*Table A.1. Sources.*

# Appendix B. Parameter table in full

Values are copied from Part 1 Table 3.2 and handoff (b) and (e). New keys are marked by their D-ID. Code integrates in τ-units, and outputs are converted to ms and Hz (section 3.3).

| **Symbol** | **Config key** | **Default** | **Range / sweep** | **Units** | **Source / status** | **D-ID** |
| --- | --- | --- | --- | --- | --- | --- |
| τ | model.tau_ms | 10 | fixed | ms | R1; R5 \[verified\] | — |
| τ_d | model.tau_d_ms | 5 | 1–50, 30 log | ms | K7, K8 values; range \[needs decision\] | D11 |
| η̄ | model.eta_bar | 4 (ref_devalle) | path eta_start → eta_peak | — | R1; path \[needs decision\] | D12 |
| Δ | model.Delta | 0.3 | 0.01–0.6, 30 linear | — | R1; R5 | D13 |
| J | model.J | −21 | −40 to −5, 25 values | — | sign reasoned (C3) | D14 |
| I | model.I_drive | 0 | trapezoid, I_amp 0.5–2 | — | R3 (existence only) | D15 |
| ref points | model.ref_point | ref_mpr (−5, 15, 1); ref_ceni (1, −20, 0.05; τ_d 3/4.95/8 ms); ref_devalle (4, −21, 0.3; τ_d 5 ms) | — | — | R1; ref_devalle values confirmed in Devalle Fig. 3 \[RB-item 2c\]; ref_ceni matches Ceni arXiv v1 only \[RB-item 3: PARTIAL\] | — |
| δ_c | replication (K9) | (Δ/Θ)\_c = (1/5)√(5 − 2√5) = 0.1453… (Devalle Eq. 8); a ratio, so Δ_c = 0.1453·η̄ with I = 0 | η̄ ∈ {1, 2, 4} (K9) | — | Devalle 2017 Eqs. 8, 20 \[verified: R5; RB-item 2a–2b\] (C4 settled) | D34 |
| K6 forcing | replication (K6) | not entered | — | — | I₀, ω and Δ of MPR Fig. 3 read in arXiv v1 only, Δ from App. A \[RB-item 1b: PARTIAL\] | D38 |
| path | path.name | path_hypoxia (P2) | P1, P2, P3, P4a, P4b, P5, NC1–NC3 | — | section 4.4 | — |
| profile | path.profile, sigmoid_k | linear; k = 10 | linear, sigmoid | — | R1; R5 | D21 |
| η̄ end points | path.eta_start, eta_peak | η̄\_H − 1.5; max(4, η̄\_H + 2); η̄\_H = lowest Hopf crossing; no Hopf: the headline cell's values | start distance {0.5, 1.5, 3} | — | this plan; CP20 | D12 |
| J path | path.J0, J_end, J_lag_frac, J_T_frac | −21, 0, 0.25, 1.0 | ±10% (S16) | — | R2; R3 | D19 |
| drive | path.I_amp, I_rise_frac, I_plateau_frac, I_fall_frac | 1 (P3); 0.1, 0.3, 0.1 | I_amp {0.5, 1, 2} | — | R3 | D15 |
| Δ path | path.Delta_factor | 1.5 (P4a); 2/3 (P4b) | both | — | R3 §3 | D20 |
| T_ramp | path.T_ramp_s | 120 | 1–1000, 13 log | s | R3 (1–5 min) | D16 |
| t_on | path.t_on_s | 5 | — | s | = baseline | D27 |
| ε | derived | (eta_peak − eta_start)/T_ramp | — | 1/τ | R1; R5 | — |
| solver | solver.method, rtol, atol, max_step_tau | DOP853, 10⁻¹⁰, 10⁻¹², 0.05 | Radau; rtol 10⁻⁸–10⁻¹² | τ | R5 | D25 |
| δ₀ | solver.delta0 | 10⁻⁶, applied at t_on | 10⁻⁹, 10⁻³ | — | R1; R5 | D26 |
| output | solver.dt_out_ms | 1 | — | ms | R4 (1 kHz) | D1 |
| σ | noise.sigma, sigma_factor | calibrated at MS5 to an N = 10⁴ baseline run (P2 start state, ref_devalle) | × 0.5, 1, 2 | — | R5 (Segneri) | D18 |
| noise step | noise.scheme, dt_tau | Heun, 10⁻³ | — | τ | R5 | — |
| noise floor (A7) | noise.floor_levels | set at MS7, before criteria-frozen (Conventions) | — | — | \[needs decision\]; run with stochastic Heun; no scaling law entered (UNVERIFIED) | D43 |
| N | network.N | 10⁴ | 10³–3×10⁴; 5×10⁴ (K8) | neurons | R5 \[single source\] | — |
| dt | network.dt_tau | 10⁻³ | 10⁻³ … 10⁻⁴ | τ | R5 (C6) | D17 |
| V_p, V_r | network.V_peak, V_reset | 100, −100 | ±200 | — | R5 \[single source\] | — |
| heterogeneity | network.het_dist, het_sampling | lorentzian, quantile | gaussian, uniform; random | — | R5; grid formula = Taher 2020 Eq. 8 \[RB-item 6\] | D28 (confirmed), D29 |
| initial V | network.init_V_range | \[−100, 100\] | — | — | R5 | — |
| readouts | network.rate_bin_ms, n_raster, exclude_refractory | 1, 300, true | — | ms | R5 | D30 |
| durations | durations.baseline_s, hold_s, discard_s | 5, 10, 2; the hold starts after the last ramp ends (1.25 T_ramp on P2-based paths); the discard comes before t = 0 | — | s | R5 | D27 |
| G | analysis.band_primary_hz | 25–100 | 30–120; γ1 25–55; γ2 80–150 | Hz | R1; R4 (C1) | D2 |
| total band | analysis.total_band_hz | 1–150 | — | Hz | R4 | D3 |
| window | analysis.window_rule, window_s, taper | D4 rule; 2; Hann | × 0.5, × 2 | s | R4; R5 | D4 |
| baseline window | analysis (fixed rule) | last 5 s before ramp | — | s | — | D5 |
| factors | analysis.rel_factor, abs_factor | 2, 2 (relative test on P_G/P_non-G) | 1.5, 4 | — | R4 | D6 |
| A_min | analysis.amin_factor | 0.1 × A_ref, one fixed absolute threshold (A_ref at ref_devalle) | 0.05, 0.2 | — | A5 | D7 |
| min duration | analysis.min_cycles | 10; damped vs non-damped by the fitted envelope growth (fit from the threshold crossing over the first 10 cycles; damped only if negative by more than 2 standard errors) | 5, 20 (RB10) | cycles | R1; R4 | D8 |
| collapse | analysis.collapse_r_frac | 0.1 | — | — | R3; R4; J = 0 is no longer a marker (CP19) | D9 |
| seeds | seeds.root_seed, n_seeds | 20261008, 10 | — | — | section 6.6 | — |
| replication tol. | replication.tolerances_file | Table 7.1 | — | — | this plan | D34 |
| robustness thr. | robustness.criteria_file | Table 7.2 | — | — | this plan | D35 |
| budget | budget.max_wall_h | 24 | — | h | this plan | D36 |

*Table B.1. Parameters, keys and defaults. v0.3: rows δ_c and K6 forcing added; ref-point and heterogeneity sources updated from RB. v0.4: δ₀, σ, durations, factors, A_min, minimum duration, collapse and η̄ end-point rows updated; noise-floor row (D43) added. v0.5: N, V_p, noise-floor and minimum-duration rows updated.*

# Appendix C. Decision log template

File: docs/decision_log.md. One entry per decision; entries are never deleted. A changed decision gets a new entry that links back to the old one, and its commit or tag is recorded. Template:

    ## DL-<nnn>  <short title>                      [ID: D/G/CP-number]
    Date:            YYYY-MM-DD        Author:
    Decision:        <what is decided>
    Options:         <alternatives considered>
    Chosen:          <value or rule>   Default from: Part 1 / Part 2 / new
    Evidence:        [Rn, section] ... or "none: reasoned, not tested"
    Test:            <what result would overturn it; run or analysis ID>
    Status:          default adopted | confirmed by test | changed (see DL-<mmm>)
    Commit/tag:      <hash or tag>

Pre-filled entries: DL-001 to DL-040 correspond to D1–D40, DL-041 to DL-046 record the other decisions this document makes, and DL-047 and DL-048 correspond to D41 and D42 (added in v0.3), and DL-049 corresponds to D43 (added in v0.4).

| **DL / ID** | **Decision** | **Default (chosen)** | **Overturned by** |
| --- | --- | --- | --- |
| DL-001 / D1 | Output sampling of v, r | 1 kHz (dt_out_ms = 1) | Spectral peak changes with 2 kHz output |
| DL-002 / D2 | Primary gamma band | 25–100 Hz; also γ1, γ2, peak | \> 5% of cells change class at 30–120 Hz (RB9c) |
| DL-003 / D3 | Total band for ρ | 1–150 Hz, detrended | RB10 |
| DL-004 / D4 | Spectrogram | Hann; W = 2 s or the T_ramp rule | Window × 0.5 or × 2 changes class (RB10) |
| DL-005 / D5 | Baseline window | last 5 s before ramp | RB10 |
| DL-006 / D6 | Factors, mode N | 2 × baseline; the relative test uses P_G/P_non-G (v0.4) | 1.5 or 4 changes class (RB10) |
| DL-007 / D7 | Amplitude threshold, mode D | 0.1 × A_ref, one fixed absolute threshold (A_ref at ref_devalle); mode-D classes D-tr, D-sus, D-none (v0.4) | 0.05 or 0.2 changes class (RB10) |
| DL-008 / D8 | Minimum duration; damped vs non-damped | ≥ 10 cycles; non-damped unless the envelope growth, fitted from the threshold crossing over the first 10 cycles, is negative by more than 2 standard errors (v0.5) | 5 or 20 changes class (RB10); the growth test disagrees with A4 stability |
| DL-009 / D9 | Collapse marker | r \< 10% of baseline; J = 0 is no longer a marker; P2 episodes report J_exit,run against J_exit,static (v0.4; split in v0.5) | Classes depend on the marker |
| DL-010 / D10 | Xu raw EEG | out of scope | Scope change only |
| DL-011 / D11 | τ_d sweep | 1–50 ms, 30 log | Map boundary at the range edge |
| DL-012 / D12 | η̄ end points | η̄\_H − 1.5 → max(4, η̄\_H + 2); η̄\_H = lowest crossing; no Hopf: the headline cell's end points (v0.4) | RB4, start-distance runs |
| DL-013 / D13 | Δ sweep | 0.01–0.6, 30 linear | K9 threshold outside range |
| DL-014 / D14 | J sweep | −40 to −5, 25 values | Map boundary at the range edge |
| DL-015 / D15 | Drive I(t) | trapezoid; I_amp 1 {0.5, 1, 2} | S6 and NC2 results |
| DL-016 / D16 | Ramp duration | 120 s; 1–1000 s, 13 log | RB3(c) |
| DL-017 / D17 | Network step | 10⁻³ τ | RB6 dt ladder |
| DL-018 / D18 | MF noise σ | calibrated at MS5 to an N = 10⁴ baseline run; × 0.5, × 2 | RB2 |
| DL-019 / D19 | J path in P2 | J0 → 0 from t_on + 0.25 T over T | RB4 |
| DL-020 / D20 | Δ direction | both (P4a, P4b) | Primary data on Δ |
| DL-021 / D21 | Ramp profile | linear; sigmoid k = 10 | RB3(d) |
| DL-022 / D22 | Interneuron-drive assumption | not rejected; M4 as robustness variant | G2(c) |
| DL-023 / D23 | Continuation tool | BifurcationKit.jl; fallback WSL2 + PyCoBi/AUTO-07p, or S4 alone | K7 not reproduced on Windows within one day (MS1) |
| DL-024 / D24 | Noisy/deterministic agreement | ≥ 90% of subgrid cells | RB2 |
| DL-025 / D25 | MF solver | DOP853, rtol 10⁻¹⁰, atol 10⁻¹², max_step 0.05 τ; Radau check | RB6 |
| DL-026 / D26 | Initial perturbation | δ₀ = 10⁻⁶ on v, applied at t_on (v0.4) | RB5 |
| DL-027 / D27 | Durations | baseline 5 s; hold 10 s after the last ramp ends (1.25 T_ramp on P2-based paths); discard 2 s before t = 0 (v0.4) | Transient visible after discard |
| DL-028 / D28 | Lorentzian grid formula | tan quantiles (Taher, Torcini, Olmi 2020 Eq. 8; CP3) | Settled in v0.3: Taher, Torcini, Olmi 2020 Eq. (8), η_i = H + Δ tan\[(π/2)(2i − N − 1)/(N + 1)\], matches the default \[RB-item 6\]. Status: confirmed by primary source; quantile test kept |
| DL-029 / D29 | Gaussian/uniform width | HWHM = Δ; uniform: half-range = Δ (v0.4) | RB8 |
| DL-030 / D30 | Network v readout | mean over non-refractory neurons | RB1 sensitivity to inclusion |
| DL-031 / D31 | Grid resolution | halving spacing moves the boundary \< 1 cell | Refinement test |
| DL-032 / D32 | Kuramoto \|Z\| readout (CP6) | Add as a secondary readout after the formula is taken from MPR 2015; until then not computed | Formula obtained. v0.3: not settled. RB found only the Z–W map (MPR Eq. 18) and no printed \|Z\| formula, in arXiv v1 only \[RB-item 1a: PARTIAL\] |
| DL-033 / D33 | Cauchy-noise run (C17) | Not run (equations absent) | Equations from Clusella and Montbrió 2024. v0.3: not settled; RB does not cover them |
| DL-034 / D34 | Replication tolerances | Table 7.1, including the K4 tail-fit fraction; frozen at the end of MS1 (tolerances-frozen) | Published precision, once primary figures are read |
| DL-035 / D35 | Robustness and gate thresholds | Table 7.2; G5: 3% of cells, 80% LHS | Frozen at MS7; changes logged |
| DL-036 / D36 | Compute cap and cut order | 24 h wall-clock (S1–S13, S16); cut order of section 9.3 | Timing gate |
| DL-037 / D37 | Code licence and archive | MIT licence; release archived with a persistent identifier; service chosen at MS15 | Institutional requirement |
| DL-038 / D38 | K6 forcing amplitude and Δ | K6 optional until read from MPR Fig. 3 | Values obtained. v0.3: not settled. RB read I₀, ω and Δ in arXiv v1 only, with Δ from App. A \[RB-item 1b: PARTIAL\] |
| DL-039 / D39 | Finite size in the main text (CP7) | Panel F5c plus FS3 | Figure budget |
| DL-040 / D40 | Headline example | P2, ref_devalle, T_ramp 120 s, linear, I = 0; default fixed now, confirmed at MS6, before S5 | Spectral peak \< 25 Hz (F1 rule) |
| DL-041 | Build order | M2 diagnostic → G1 → M3 primary; M4 or adaptation only via G2 or G3 | G1, G2, G3 outcomes |
| DL-042 | Replication before new work | G0 must pass before S5 | — |
| DL-043 | Criteria frozen before M3 ramp-study runs | Tag criteria-frozen at MS7, with SHA-256 in the tag; replication tolerances (D34) frozen at the end of MS1 (tolerances-frozen) | — |
| DL-044 | Corrections to Part 1 | CP1–CP27 applied; sections 2–6 edited in place where CP14–CP27 record it; handoff unchanged except its (d) paths and header line | Primary-source check |
| DL-045 | Figure production | One script per figure, reading results only; tag per build | — |
| DL-046 | Toolchain | Python 3.11 + Numba; no PyDSTool; AUTO-07p, XPPAUT, MatCont flagged | D23 test |
| DL-047 / D41 | G8 next step after PARTIAL OVERLAP (section 12.7) | Decided in v0.4: claim reframed as a first mechanistic model; Taher 2022 and Avitabile 2022 cited as method precedent; noise robustness (RB2) a main result; G8 third branch met by A7's entry–exit metrics; MS14 still runs before writing | MS14 finds closer prior work |
| DL-048 / D42 | M4 form (section 7.3) | Table 4.1 form (E–I, instantaneous synapses); its equations still to be read from MPR App. E or Segneri before S14 | Choosing Dumont and Gutkin 2019 Eqs. (7)–(8) (first-order synapses; read in the primary source \[single source: RB-item 5\]); decide before S14 or any RB8 M4 run |
| DL-049 / D43 | Slow-passage noise floor (A7) | A small additive noise floor on v for the A7 delay test, integrated with stochastic Heun, at levels set at MS7 (before criteria-frozen; Conventions); no scaling law entered (UNVERIFIED) | RB3(b) and RB6 results; a primary-source scaling law |

*Table C.1. Pre-filled decision log. Status of every entry: "default adopted", except D28, confirmed by a primary source in v0.3, D41, decided in v0.4, and D43, whose default is set at MS7 (Conventions). D1–D31 come from Part 1 (2026-10-08); D32–D40 and DL-041 to DL-046 from Part 2 (2026-10-09); D41–D42 (DL-047, DL-048) from v0.3 (2026-10-09). v0.3 checked D32, D33 and D38 against RB: none is settled (reasons in the last column). v0.4: D43 added (DL-049); DL-006 to DL-009, DL-012, DL-018, DL-023, DL-026, DL-027, DL-029, DL-034, DL-040, DL-043, DL-044, DL-047 and DL-048 updated. v0.5: DL-008, DL-009, DL-043, DL-044 and DL-049 updated.*

# Appendix D. Glossary of terms and symbols

| **Term or symbol** | **Meaning** |
| --- | --- |
| MPR | Montbrió–Pazó–Roxin exact mean field of QIF neurons (section 3.1) |
| QIF | Quadratic integrate-and-fire neuron, τ dV/dt = V² + η + input, reset at ±∞ |
| OA manifold | Ott–Antonsen low-dimensional manifold; attraction argued, proven only for related classes |
| Lorentzian | Cauchy distribution of excitabilities η_j, centre η̄, half-width Δ |
| r, v, s | Population rate, mean membrane potential, synaptic activation |
| τ, τ_d | Membrane time constant (10 ms; the code's time unit); synaptic decay time |
| η̄, Δ, J, I(t) | Mean excitability; heterogeneity; signed coupling (inhibition J \< 0); common drive |
| η̄\_H, A_ref | Static Hopf value of η̄ (A4; the lowest crossing); limit-cycle amplitude of v at ref_devalle (A5), used as one fixed absolute threshold |
| δ_c | Critical heterogeneity ratio (Δ/Θ)\_c = 0.1453… (Devalle Eq. 8; Table 7.1, K9); Δ_c = 0.1453·η̄ with I = 0 |
| ε | Ramp rate (eta_peak − eta_start)/T_ramp, in 1/τ |
| G, ρ, \|Z\| | Primary gamma band; relative gamma power P_G/P_total (reported; the surge test uses P_G/P_non-G); Kuramoto order parameter (formula not in the reports, D32) |
| M2, M3, M4, M3a, M3b | Model classes: 2D MPR; inhibitory MPR with a first-order synapse (ING); E–I (PING); adaptation variants |
| ING, PING | Interneuron gamma; pyramidal–interneuron gamma |
| Hopf (super-/subcritical) | Onset of oscillation from a focus; small, reversible cycles vs abrupt onset with hysteresis |
| Saddle-node; node; focus | Fold of fixed points; non-oscillatory and oscillatory approach to a stable state |
| Slow passage / delayed Hopf | When a parameter ramps through a Hopf point, onset is delayed and depends on the starting state (memory effect) |
| Quasi-static | Limit of an infinitely slow ramp; reference for onset delay |
| S+, S-rel, S-abs, S-sus, NS; D-tr, D-sus, D-none | Surge classes of Table 2.1 (mode N; mode D). A surge class is D-tr, S+, S-rel or S-abs; S-abs may carry a "broadband" flag |
| Damped, non-damped; sustained | D8 envelope-growth test: growth fitted from the threshold crossing over the first 10 cycles; damped only if negative by more than 2 standard errors, otherwise non-damped. "Sustained" means non-terminating (S-sus, D-sus) |
| Mode D, mode N | Deterministic MF runs; noisy MF and network runs |
| SD | Spreading depolarization; terminal SD follows non-spreading depression (electrical silence) |
| P1–P5, NC1–NC3 | Parameter paths and negative controls (sections 4.4 and 2.4) |
| K1–K11 | Replication targets (section 3.1 and Table 7.1) |
| A0–A11, S1–S16 | Analysis steps and simulation runs (sections 5, 6 and 7) |
| RB1–RB10 | Robustness checks (Table 7.2) |
| G0–G8 | Decision gates (section 4.3 and Table 11.2) |
| D1–D43 | Items marked \[needs decision\] (Appendix C); D28 settled in v0.3; D41 decided in v0.4 |
| CP1–CP27; C1–C24 | Corrections to Part 1; conflicts between reports |
| RA, RB | RESULT A (prior-work search for gate G8) and RESULT B (primary-source equations and values), added in v0.3; a RESULT B item is cited as "RB-item n" (v0.5) |
| Nordlie table | Standardised tabular model description \[R5; R7\] |
| DOP853, Radau, Heun | Explicit 8th-order Runge–Kutta; implicit Runge–Kutta; stochastic predictor–corrector |
| LHS | Latin hypercube sample (S16) |
| WSL2, MSYS2 | Linux and Unix-like layers on Windows, needed only for the flagged fallback tools |
| MS0–MS15 | Milestones (Table 11.1); renamed from M0–M15 in v0.4 |
| J_exit,static; J_exit,run | J at which a P2-based path leaves the A4 oscillatory region (static, from A4); J at which the classifier ends the observed episode (per run; the reported J_exit metric). They differ under delayed exit (Table 2.1) |
| TRIAGE IDs (T01–T117) | Review findings triaged for v0.4 (Appendix F) |
| REVIEW 5 IDs (SC-01–SC-10, MC-01–MC-33) | Findings of the independent sweep of v0.4, fixed in v0.5 (Appendix G) |

*Table D.1. Glossary.*

# Appendix E. G8 search log

Source: RESULT A, "Search log (paste into search_log.md)", October 2026. This table is the content for docs/search_log.md (section 10.1). It records the G8 pre-check (verdict PARTIAL OVERLAP, section 12.7) and does not complete MS14, which also needs native Scholar and PubMed searches and the other checks in Table 11.1 \[R2, §6 rec. 6\].

| **\#** | **Query or action** | **Tool / database actually reached** |
| --- | --- | --- |
| 1 | model mechanism gamma surge dying brain cardiac arrest | Web search (hits: PNAS, PMC, ScienceDirect) |
| 2 | next generation neural mass model hypoxia | Web search (arXiv, eNeuro, J Neurophysiol, Frontiers) |
| 3 | Taher Avitabile Desroches bursting next generation neural mass slow passage | Web search (Springer, VU Amsterdam, ResearchGate) |
| 4 | computational model near-death gamma oscillations hypoxia network simulation | Web search (Frontiers, PMC, eLife) |
| 5 | neural mass model ischemia EEG oxygen deprivation Hopf bifurcation | Web search (bioRxiv, PMC, arXiv) |
| 6 | exact mean-field quadratic integrate-and-fire anesthesia propofol | Web search (arXiv, bioRxiv) |
| 7 | dying brain gamma surge mechanism computational model 2025 | Web search (ResearchGate, PNAS, ClinicalTrials.gov) |
| 8 | delayed Hopf bifurcation slow ramp neural mass model oscillation onset | Web search (APS PRE, PubMed, bioRxiv, Springer, arXiv) |
| 9 | hypoxia gamma oscillations interneurons model transient increase anoxia | Web search (Springer, PLOS ONE, eNeuro, PMC) |
| 10 | "cardiac arrest" EEG neural mass model simulation gamma | Web search (bioRxiv, PMC, PNAS) |
| 11 | Borjigin gamma surge mechanism model simulation interneuron hypoxia preprint biorxiv | Web search (bioRxiv, PNAS) |
| 12 | Montbrió Pazó Roxin model slow parameter ramp transient oscillations | Web search (arXiv, PLOS Comput Biol, APS PRX) |
| 13 | Li Borjigin 2023 gamma dying brain rat asphyxia | Web search (PubMed, PMC, Borjigin lab site) |
| 14 | next generation neural mass model anaesthesia loss of consciousness | Web search (Cell/Neuron, bioRxiv, Nature Comms Bio, arXiv) |
| 15 | next generation neural mass ion concentration potassium dynamics seizure spreading depolarization | Web search (arXiv, PMC, PLOS ONE) |
| 16 | "slow passage" Hopf "theta neurons" OR "quadratic integrate-and-fire" mean-field | Web search (PMC, Springer, arXiv) |
| 17 | Kalia Meijer van Putten neural mass ischemia EEG 2024 published | Web search (bioRxiv, ResearchGate, U. Twente) |
| 18 | agonal EEG terminal spreading depolarization model gamma before isoelectric | Web search (Wiley Ann Neurol, PubMed, OUP Brain) |
| 19 | arXiv dying brain gamma oscillations model 2024 2025 2026 | Failed (search budget exhausted, not executed) |
| Q-F1 | Fetch: biorxiv.org/content/10.1101/2025.08.04.668381v1.full | bioRxiv full text (introduction) |
| Q-F2 | Fetch: biorxiv.org/content/10.1101/2023.04.07.535995v1.full | bioRxiv full text (introduction + methods) |
| S | Subagent: 9 queries incl. "next generation neural mass model ischemia OR hypoxia OR anoxia", "Montbrió Pazó Roxin model hypoxia energy ATP neural mass", "spiking network model hypoxia transient gamma increase before isoelectric EEG", ""Li D" Borjigin 2023 dying brain gamma" | General web search only; no direct Scholar/PubMed/bioRxiv/arXiv querying |

*Table E.1. G8 search log as recorded by RA. Fetch rows renamed Q-F1 and Q-F2 in v0.4 so they do not collide with figure IDs.*

**Not reached directly:** Google Scholar, medRxiv, the PubMed search interface, and bioRxiv or arXiv native search. These sites appeared only as web-search results \[RA\].

**Coverage and read depth** \[RA, Caveats\]. Results came from PubMed/PMC, bioRxiv, arXiv, PLOS, PNAS, Springer, APS, Frontiers and ResearchGate pages. The cited-by lists of Borjigin 2013 and Xu 2023 were not walked, and conference abstracts (CNS, SfN, BMC Neuroscience supplements) or non-indexed theses could have been missed. Roberts et al. 2023 and Schramm et al. 2019 (RA's year; Appendix A, 40 gives Prog Neurobiol 2020) were read as abstracts only; Kalia et al. 2023 as introduction and methods; the 2025 noisy-Hopf preprint as introduction; Taher et al. 2022 as abstract and introduction.

**Inconsistency in RA.** RA's caveats count 18 searches plus 11 subagent queries, but its log row S lists 9 subagent queries; both are recorded as given. RA also found no 2023 paper with Li as first author on dying-brain gamma; this plan cites Li et al. 2015 (Appendix A, 36), so nothing changes. v0.4 also records: RA's TL;DR quotes the noisy-Hopf preprint's "Section 5.2", although its caveats say only the introduction was read; RA dates Schramm 2019 where R2 and R4 give 2020 (C23); and query 3 looks up known authors (Taher, Avitabile, Desroches) rather than discovering papers \[RA, TL;DR, Caveats, search log\].

# Appendix F. v0.4 change log

Source: TRIAGE.md, the merged triage of four independent reviews of v0.3 (science, consistency, buildability and evidence). Each row is one applied item, by TRIAGE ID. "APPLY" items were clear fixes; "ASK, accepted" items were decided by the author, each following the triage recommendation; "UNVERIFIED, confirmed" items were checked against R1–R7, RA and RB before they were applied. Changes to Part 1 are also recorded in Table 12.1 (CP14–CP24).

| TRIAGE ID | Where | Change (decision) |
| --- | --- | --- |
| T01 | §4.4 P2; §6.2; Tables 2.1, 9.1, 10.1; App. B; DL-027; §1; CP14 | P2-based runs last 5 s + 1.25 T_ramp + 10 s (headline 165 s = 16,500 τ); compute budget recomputed (about 3–12 h) (ASK, accepted) |
| T02 | §2.2; A4; Table 7.1 K9 and note; Table 4.1; CP11; CP15 | One K9 protocol at η̄ = 1, 2 and 4 (largest Δ/η̄ over τ_d and J); §2.2 condition necessary only, with Δ/(η̄ + I) (ASK, accepted) |
| T03 | A7; Table 7.2 RB3, RB6; Table 8.1 F4; D43 (DL-049, App. B, §10.3); §12.3; CP16 | Expectations and criteria from delayed-Hopf theory; entry–exit prediction; explicit noise floor; no scaling law entered (UNVERIFIED) (ASK, accepted) |
| T04 | §6.4; Tables 6.2, 9.1, 11.1; App. B; DL-018; CP21 | σ calibrated at MS5 from one N = 10⁴ baseline run; S8 checks it (APPLY) |
| T05 | Tables 6.2, 7.1, 11.1, 11.2; §7.1 G0; §1 | K4 split into K4-MF (MS2) and K4-net (MS5) (APPLY) |
| T06 | §4.3 G1; A2; A8; Table 11.1 MS1, MS4; §1; CP17 | G1 judged by the sign of envelope growth; surge_metrics core built at MS1 (ASK, accepted) |
| T07 | Read this first; §1 risk 3 | \[verified\] gap narrowed to ramp-rate measurement \[R1; R5\]; "No repositioning is needed" removed; Taher 2022 precedent noted (UNVERIFIED, confirmed). v0.5 note (REVIEW 5, MC-19): the narrowed sentence keeps \[verified\], a deviation from TRIAGE T07 fix (1) ("Remove the \[verified\] tag"); it is kept because R1's and R5's gap statements both support it (two reports; Conventions) |
| T08 | Read this first; §1; §2.6; §12.7; Table 11.2 G8; §12.3; DL-047; CP22 | Claim reframed as a first mechanistic model (D41 decided); Taher 2022 and Avitabile 2022 cited as method precedent (ASK, accepted) |
| T09 | Table 12.3 risks 8 and 11 | Noise and finite-size risk added; risk 8 re-cited to R1, R5, RA and R7 (UNVERIFIED, confirmed) |
| T10 | §2.2; §7.2; Table 7.2 RB2; §12.7; CP22 | Deterministic-limit caveat; RB2 (noise robustness) in the main text (ASK, accepted) |
| T11 | Table 2.1; App. B; DL-006; glossary; Table 10.1; CP18 | Relative test on P_G/P_non-G; baseline ρ reported before MS7 (ASK, accepted) |
| T12 | Table 2.1; §2.4; §4.3; A8–A10; Tables 7.2, 8.1, 11.2, 12.3; App. B; DL-007; glossary; CP18 | Mode-D classes D-tr, D-sus, D-none with one fixed absolute threshold; "surge class" defined (ASK, accepted) |
| T13 | Table 2.1; §2.2; App. B; DL-008; CP17 | Envelope-growth test for damped versus sustained; ring length stated as Δ-dependent (ASK, accepted) |
| T14 | Table 2.1; §2.5; §4.4; §12.7; App. B; DL-009; glossary; CP19 | J_exit and post-surge rate reported; P2 ordering stated as imposed by design (ASK, accepted) |
| T15 | §4.4 P1; Table 3.2; App. B; DL-012; glossary; CP20 | η̄\_H is the lowest Hopf crossing; cells with no Hopf use the headline range (ASK, accepted) |
| T16 | Table 7.1 K10 | K10 evaluated over the oscillatory τ_d interval from A4 (APPLY) |
| T17 | Table 7.1 K8; §7.1 G0; Table 11.2 G0; §1 | K8 frequency band non-blocking, tagged \[reasoned, not tested\], feeds G2 (ASK, accepted) |
| T18 | §6.2; Table 7.2 RB5; App. B; DL-026; CP16 | δ₀ applied at t_on (ASK, accepted) |
| T19 | A2; Table 7.1 K4; DL-034; CP23 | K4 fitted on the tail of the step response (APPLY) |
| T20 | Tables 6.2, 9.1, 11.1; §1 | S13 split (headline subset at MS8) and its scope pinned (APPLY) |
| T21 | Table 11.1 MS6; §1 | S4 added to MS6 (APPLY) |
| T22 | Table 6.2 S5 | Headline cell added to S5 (APPLY) |
| T23 | §9.2; Table 11.1 MS3, MS5 | Timing with a provisional η̄ path; headline re-timed after A4 (APPLY) |
| T24 | §9.2 | Expensive cells timed; extrapolation per run family (APPLY) |
| T25 | §7 intro; Table 7.1 caption; §10.1; §10.7; §12.3; DL-034; DL-043; Table 11.1 | Replication tolerances frozen at the end of MS1 (tag tolerances-frozen) (APPLY) |
| T26 | §7.3; §1 risk 1 | RB-item 5 reading corrected: instantaneous E–I equations located in MPR App. E, not transcribed (APPLY) |
| T27 | §1 risk 1; §1 v0.3 bullet; DL-048 | Dumont–Gutkin equations tagged \[single source: RB-item 5\] everywhere (APPLY) |
| T28 | §1 v0.3 bullet; Table 4.1 caption; §7.3; Table 12.2 C10; §12.4 | Combined erratum wording; "names no other equation" deleted; content \[verified: R1; R5\] (ASK, accepted) |
| T29 | §4.1; Table 4.1; CP1 | Hopf \[verified\]; supercritical per Ceni \[single source\] (APPLY) |
| T30 | Table 11.1 and every milestone reference; glossary | Milestones renamed MS0–MS15 (APPLY) |
| T31 | Conventions | \[needs decision\] list points to Appendix C (APPLY) |
| T32 | Table 2.1 Classes; Table 3.3 | Relative-only retagged \[reasoned, not tested; R2, §3\]; absolute pre-arrest rise in the single case \[R4, §2.3\] (UNVERIFIED, confirmed) |
| T33 | Table 12.3 risk 12; §7.2 | Journal-depth risk; the analytic results named (UNVERIFIED, confirmed) |
| T34 | Table 11.1 MS15; checklist after Table 11.2 | Manuscript and submission checklist from R7 §8(d) and R6 §6, §8(d) (ASK, accepted) |
| T35 | Table 12.2 C20–C23 | Four unlogged conflicts recorded (UNVERIFIED, confirmed) |
| T36 | A6; Table 9.1 | A6 method stated (continuation; no brute-force grid) (APPLY) |
| T37 | §10.4; A9 | Restart and failure handling (APPLY) |
| T38 | §10.3; §6.6; §10.7; Table 10.1 | Config hash scope; 12 hexadecimal characters (APPLY) |
| T39 | §10.3; Table 10.1 | Typed validation of YAML values (APPLY) |
| T40 | §10.4; Table 10.1 | Seeds passed into the Numba kernels (APPLY) |
| T41 | §10.4 | Numba cache cleared before tagged runs (APPLY) |
| T42 | §10.1; §10.2; Table 11.1 MS0 | Version pins and bootstrap order (APPLY) |
| T43 | §9.1; Table 11.1 MS1; §12.3; DL-023 | BifurcationKit smoke test at MS1; Julia output format (APPLY) |
| T44 | §10.7 | Merge only after passing tests; \$LASTEXITCODE checks (APPLY) |
| T45 | §10.4 | Logging design (APPLY) |
| T46 | §9.1 | Windows host hazards (APPLY) |
| T47 | Table 10.1; §10.1 | test_noise, test_runner, test_julia_io; network synapse tests (APPLY) |
| T48 | Table 10.1; A8 | Tolerances stated, noise seeded, no bitwise comparison across machines (APPLY) |
| T49 | §3.1 | v\* units and dimensional form (APPLY) |
| T50 | Table 7.1 K11 | K11 on the J → 0⁻ branch (APPLY) |
| T52 | Table 2.1; glossary; Table 10.1 | S-abs class added (ASK, accepted) |
| T53 | Table 6.1; DL-029 | Uniform width rule (APPLY) |
| T54 | Table 2.1; §6.2; Table 6.1; App. B; DL-027; CP14 | Discard before t = 0, so every baseline is 5 s (ASK, accepted) |
| T56 | A5; Table 11.1 MS6 | S4 points next to η̄\_H excluded from the 2% test (APPLY) |
| T57 | Table 6.2 S13 | ±200 check also at dt 10⁻⁴ (APPLY) |
| T59 | Table 12.2 C9 | Not a real conflict (regime and sign) (APPLY) |
| T62 | Table 12.2 C5 | MPR App. A wording corrected (APPLY) |
| T63 | Handoff header; §12.1 | "Unchanged except the (d) module paths" (APPLY) |
| T64 | CP11 | §2.2 noted as already using the ratio (APPLY) |
| T65 | §1 build order | K10 and K11 run but do not block (APPLY) |
| T66 | §7.2; §1; §12.3; DL-040; Table 11.1 MS6 | D40 default fixed now, confirmed at MS6 (APPLY) |
| T67 | Table 11.2 caption | G0 thresholds belong to D34 (APPLY) |
| T68 | Table 8.1 F5; Table 11.2 G5 | One class definition for G5 (APPLY) |
| T69 | Table 11.2 G2, G3; Table 11.1 | "As section 4.3"; G3 unlocked at MS9 (APPLY) |
| T70 | Table 11.2 caption | What each gate blocks (APPLY) |
| T71 | Table 11.1 MS10 | RB8 (heterogeneity part) (APPLY) |
| T72 | Captions of Tables 3.1, 4.2, 4.3 | Uncaptioned tables captioned (APPLY) |
| T73 | §10.1 | Step number replaced by a section reference (APPLY) |
| T74 | Table 9.1; §1 | Total consistent with the rows; S9 recomputed (APPLY) |
| T75 | Conventions; Table 3.3; §4.4 | Status words mapped to tags (APPLY) |
| T76 | Conventions; §3.3; §4.1; §7.2; §8; §9.1; §10.4; §12.7; Tables 4.1, 11.2 | RA evidence rule; untagged claims tagged (ASK, accepted) |
| T77 | Read this first; §2.6 | R2 locators corrected (§2.6; §6 rec. 6, §8(e)) (UNVERIFIED, confirmed) |
| T78 | Preflight | Counts and claims corrected (APPLY) |
| T79 | §10.1; §10.3 | base.yaml described as path-neutral defaults (APPLY) |
| T80 | §12.3 | D2 test named consistently (APPLY) |
| T81 | §12.1 | Additions are not corrections (APPLY) |
| T82 | Table E.1; Table 3.3; Table 11.2 G5 | Q-F1, Q-F2; electrodes labelled; P4a or P4b (APPLY) |
| T83 | Appendix E | Schramm year cross-referenced (APPLY) |
| T84 | §6.1 | Pointer to section 10.2 (APPLY) |
| T85 | §10.1 | pyproject \[build-system\] and \[project\]; --strict-markers (APPLY) |
| T86 | §10.1 | .gitattributes text=auto; binaries marked (APPLY) |
| T87 | §10.2 | Python installer version recorded (APPLY) |
| T88 | §10.2 | Clean-machine PowerShell notes (APPLY) |
| T89 | Table 11.1 MS0 | MS0 done-when (APPLY) |
| T90 | §10.7 | git add -A before commit (APPLY) |
| T91 | §10.4; §9.2 | Thread pools set to 1; 6, 8 and 10 workers timed (APPLY) |
| T92 | §10.4 | Memory rules (APPLY) |
| T93 | Table 9.1 | Analysis row (APPLY) |
| T94 | §9 Disk | Compressed series (APPLY) |
| T95 | §9.1; §10.2 | Repository location and long paths (APPLY) |
| T96 | §10.4 | Spawn-safe worker arguments; config paths from the repository root (APPLY) |
| T97 | §10.1 | CI installs the package (APPLY) |
| T98 | §4 Sources; §4.5 | Re-cited to R3 §6 (recommendations), §8(c) (UNVERIFIED, confirmed) |
| T99 | §2.6 | Taher 2022 cited to R1, R5 and RA (UNVERIFIED, confirmed) |
| T100 | Table 12.2 C8, C14 | "Lee" corrected to Li 2015 (UNVERIFIED, confirmed) |
| T101 | Table 12.2 C1; Table 2.1 caption | Borjigin band attribution; 130 Hz note (UNVERIFIED, confirmed) |
| T102 | Table 4.3 | R3 grades quoted exactly (UNVERIFIED, confirmed) |
| T103 | §4.4 P2 | R2's three options quoted (APPLY) |
| T104 | §12.4 | R1 §7 locator dropped (UNVERIFIED, confirmed) |
| T105 | §1 | Universal negative reworded; human surge before arrest (APPLY) |
| T106 | §2.4 | Predicted no-surge manipulations (UNVERIFIED, confirmed) |
| T107 | Appendix E; §12.7 | RA inconsistencies recorded; query-19 locator (UNVERIFIED, confirmed) |
| T108 | §3.1; Tables 2.1, 3.2, 3.3, 6.1; §6.6 | Single-report items retagged \[single source\] (APPLY) |
| T109 | §2.3 | Fold-changes and human timing \[verified: R4; R6\] (UNVERIFIED, confirmed) |
| T111 | Table 7.2 RB9(d) | Wording aligned with §3.3 (APPLY) |
| T112 | Table 2.1 caption | Coherence-only limitation stated (UNVERIFIED, confirmed) |
| T113 | Table 12.2 C24; Table 12.3 risk 13 | Wang–Buzsáki risk and bistability conflict (UNVERIFIED, confirmed) |
| T114 | Table 3.3 | Xu power cited to R4 §2.1 (UNVERIFIED, confirmed) |
| T115 | §4.1 | Byrne ERD/ERS argument for the model choice (UNVERIFIED, confirmed) |
| T116 | A7 | Devalle Fig. 6 precedent (UNVERIFIED, confirmed) |
| T117 | §12.4 | R2's search-count inconsistency recorded (UNVERIFIED, confirmed) |

*Table F.1. Items applied in v0.4: 72 APPLY, 18 ASK (accepted) and 21 UNVERIFIED items confirmed in the sources; 111 in total.*

**Not applied.** Rejected (the plan already handles them, or the reviewer was wrong): T58 (upgrading tags from a reviewer's own reading; the Conventions count only report sources), T60 (RB's Ceni Eq. 12 is already not entered), T61 (the plan already calls Θ the centre of the Lorentzian) and T110 (R3 attributes the bursting to the wrong MPR figure, so it cannot confirm K5). Not confirmed in the sources, so left unchanged: T51 (the M2 network coupling kernel for K4-net; no attached source gives it; v0.5 lists it as UNVERIFIED in section 12.4 and Table 6.1 and makes K4-net non-blocking, REVIEW 5 MC-03) and T55 (a condition for onset advance beyond R5's "low-frequency Hopf"; no attached source states it).

# Appendix G. v0.5 change log

Source: REVIEW 5 (REVIEW_5_v04_sweep), one independent sweep of v0.4 with 43 findings: SC-01 to SC-10 on the science of the v0.4 rewrites and MC-01 to MC-33 on consistency, tags and layout. Each row is one finding, by its review ID. Where the review left a choice, the author's decisions were applied as given. Changes to sections 2–6 are also recorded in Table 12.1 (CP25–CP27). Values that a fix needs but no source gives are marked UNVERIFIED in the text and listed in section 12.4.

| Finding ID | Where | Change (decision or note) |
| --- | --- | --- |
| SC-01 | §5.2 A4, A7 Check; Table 7.2 RB3(a); Table 8.1 F4; Table 11.2 G6; Table 11.1 MS7; §12.4; CP25 | RB3(a) applies only to the runs where δ₀·exp(∫ Re λ dt′) stays above the solver or noise floor until the predicted onset; A4 computes this range. G6 judges RB3(a) only on those runs. The threshold-crossing onset (envelope reaching 0.1 × A_ref) is compared with t_pred, the time at which the growing mode started from δ₀ at t_on reaches that amplitude. Tagged \[reasoned, not tested\]; fixed before criteria-frozen (MS7). Floor values UNVERIFIED (set at MS7). |
| SC-02 | §5.2 A7 Expected; Table 7.2 RB3(a); CP25 | Entry–exit prediction written along the actual path in time, with λ evaluated at (η̄(t′), J(t′)) and every other parameter at its path value; valid for every profile. Tagged \[reasoned, not tested; the general form is not in the reports\]. |
| SC-03 | §5.2 A7; §6.2 Mode N; Table 6.2 S13; Table 7.2 RB3, RB6; Table 8.1 F4; Table 11.2 G6; §12.3; App. B; DL-049 | The D43 noise-floor runs use the stochastic Heun integrator. RB6's 5% test varies the Heun dt ladder (default 10⁻³ τ against the finest rung; lower rungs UNVERIFIED, set at MS7). The rtol comparison is kept for noise-free DOP853 runs only (reported, not a pass test). |
| SC-04 | Table 11.2 G6; Table 7.2 RB3(d) | Only solver dependence (method or rtol; the Heun step for floored runs) triggers "fix the numerics". Dependence on profile and δ₀ is reported as slow-passage physics (§4.4, RB3(d), RB5); RB3(d) and RB5 are evaluated and reported, not gated. |
| SC-05 | Table 7.1 K9 and the note below it; §5.2 A4; §2.2; §7.1 Gate G0; Table 11.2 G0; Table 11.1 MS5; §1; CP26 | The "maximum over τ_d and J equals δ_c" criterion is tagged \[reasoned, not tested\]. τ_d is searched over the plan's existing D11 range (1–50 ms), so no new D-item. Stopping rule: widen at most twice, then report the maximum as asymptotic. If the maximum differs from 0.1453, G0 blocks only on the verified ratio scaling across η̄ = 1, 2, 4 and reports the maximum. Interpretation: "ratio scaling" is judged as the three maxima of Δ/η̄ agreeing within the existing K9 tolerance (± 0.002); no new value was introduced. |
| SC-06 | Table 2.1 Minimum duration; §4.3 G1; §5.2 A2; §1 build order; App. B; DL-008; App. D; CP26 | Fit window: from the threshold crossing over the first 10 cycles. A run counts as damped only if the fitted rate is negative by more than 2 standard errors of the fit. The D8 sense of "sustained" is renamed "non-damped"; "sustained" is kept for S-sus and D-sus. Interpretation: M2 (G1) has no amplitude threshold, so its window starts at the first of the cycles counted in G \[reasoned, not tested\]. |
| SC-07 | §5.2 A9 | Failure label (f) added: amplitude below the fixed threshold (oscillates inside the A4 region but never reaches 0.1 × A_ref). |
| SC-08 | Table 2.1 Ordering and Metrics; §2.5; §4.4 P2; §12.7; DL-009; App. D | J_exit,static (from A4) and J_exit,run (from the classifier) defined. The reported J_exit metric and the post-surge rate use J_exit,run; the ordering statement uses J_exit,static; their difference is reported as the exit delay. |
| SC-09 | §5.2 A8; Table 10.1 test_surge_metrics | Synthetic slowly damped ring added: more than 10 cycles above threshold with negative fitted growth; must classify as NS or D-none. |
| SC-10 | Table 2.1 Classes; App. D | S-abs is reported with a "broadband" flag when the rise is not a band-limited peak; no new threshold. |
| MC-01 | Table 2.1 Threshold (mode N); Table 6.2 S5; Table 9.1; Table 11.1 MS7; §1; §7 intro | Short baseline-only mode-N runs (7 s: 2 s discard plus 5 s baseline; 10 seeds) for the headline cell and the 1,225 map cells, run at MS7 and counted under S5 (no new S-ID). Table 9.1 row: 8.6×10⁹ Heun steps, 0.5–1.2 min on 6 workers \[reasoned, not tested\]. Totals updated: the row sums stay 2.6–11.9 h at the stated precision, so the total stays about 3–12 h (§1, Table 9.1). |
| MC-02 | Conventions; §1 counts; §12.3; Table C.1 caption; App. B; DL-049 | \[needs decision\] now also covers an item whose default is set at a named milestone (D43: set at MS7). The open-item count stays 41, and §1 and §12.3 say why. No default value was invented for D43. |
| MC-03 | §12.4; Table 6.1; Table 6.2 S1; Table 7.1 K4; §7.1 Gate G0; Table 11.2 G0; Table 11.1 MS5; §1; App. F | The M2 network coupling is listed as UNVERIFIED in §12.4 and Table 6.1. K4-net is non-blocking until a source gives the coupling, stated in Table 7.1 and G0. No coupling was invented. |
| MC-04 | §5.2 A7; Table 11.1 MS8, MS9 | A7 listed under both milestones: S5 part at MS8, S6 part at MS9. |
| MC-05 | Table 11.1 MS11 | "Every RB check except the RB8 M4/adaptation parts (MS12) has a result". |
| MC-06 | Table 7.2 RB7 | "NC1 has no surge class (NS or D-none) at every T_ramp (else G7)". |
| MC-07 | Table 12.3 risk 3 | "P1 is expected to give D-sus (S-sus in mode N)". |
| MC-08 | Table 12.3 risk 10 | "D41 decided in v0.4 (section 12.7); MS14 still runs". |
| MC-09 | §7 intro; §7.2 headline; DL-043 | "before any M3 ramp-study run (S5 onward)"; the MS7 baseline-only S5 runs are noted as having no ramp. |
| MC-10 | Table 9.1 Total; §1 | Lower bound with S9 at its computed time (11 min), upper bound with its 2 h allowance. |
| MC-11 | §6.7; §8 | One tag for the page and figure budget: \[single source: R6\]. |
| MC-12 | Table 3.1 K7, K9 | "(superseded: Table 7.1; CP1)" and "(superseded: Table 7.1; CP11)" added; Part 1 tags otherwise kept. |
| MC-13 | §2.4 | Hypothermia and deep GABAergic suppression (propofol): \[single source: R3\] (CP4); adrenergic blockade: \[verified: R2; R3\]. |
| MC-14 | Table 6.1 Heterogeneity | "confirmed against Taher, Torcini, Olmi 2020 Eq. 8 \[RB-item 6\] (D28)". |
| MC-15 | Table 3.2 N, V_p; Table 6.1 Peak/reset, Refractory; App. B N, V_p; §3.3 Readout | T108 rule applied: items resting on R5 alone retagged \[single source\]. |
| MC-16 | §2.2; §5.2 A7; Table 7.2 RB3(b) | RA claims tagged \[single source: RA, introduction depth\]; the monotone "shrinks as the floor rises" relation tagged \[reasoned, not tested\]. Wording left as written (fix applied as given). |
| MC-17 | Read this first; §1; §12.4 | One locator set for R2's rating and the missing native searches: \[R2, summary; R2, §2.6; R2, §7\]. R2's section numbers remain unconfirmed (the review could not check them). |
| MC-18 | §2.6; CP22 | Taher 2022 cited as \[R1, §2.5; R5, SQ4; RA\] everywhere. |
| MC-19 | App. F T07 row | Deviation recorded: \[verified\] kept on the narrowed sentence, against TRIAGE T07 fix (1), because R1's and R5's gap statements both support it. |
| MC-20 | §10.1 | .gitattributes lines shown: \* text=auto eol=lf; \*.npz, \*.parquet and \*.png binary (from TRIAGE T86). |
| MC-21 | Table 6.2 | S16 row added (from RB4). |
| MC-22 | §2.5 | "(D10)" added. |
| MC-23 | Throughout; Conventions; App. D | RESULT B citations renamed "RB-item n" by search (48 citations). Safe: every "RB" followed by a space and a digit is a RESULT B item, the checks RB1–RB10 never have a space, and no match spans two text runs. Conventions note added on MPR appendices and on "§". |
| MC-24 | Table 11.1 Unlocks | Next milestone added to the Unlocks column (MS2–MS12, MS14). |
| MC-25 | §1 build order step 4 | "then gate G6 (MS8); … and, after the maps, gates G5 and G7 (MS9)". |
| MC-26 | §5.2 A4, A7; Table 7.2 RB3(a); §12.4 | The η̄ grid on which A4 evaluates λ along each path is named as the "A4 grid step"; its spacing is UNVERIFIED (set in configs/A4.yaml at MS7). |
| MC-27 | Table 6.2 S3 | "N = 5×10⁴ for K8" added. |
| MC-28 | §12.7 | Stray comma before \[RA, Caveats\] deleted. |
| MC-29 | Contents; docProps | TOC (with the new Appendix G entry) and page count refreshed from a LibreOffice render of v0.5. Word may paginate slightly differently; update fields in Word before circulating. |
| MC-30 | §1 (two lists); §9.2; §9.3; §10.8 | Each numbered list now uses one numId, so items continue 1, 2, 3 in every renderer. |
| MC-31 | All 33 tables | First rows were already marked w:tblHeader w:val="true" (the review counted only the bare form); normalised to \<w:tblHeader/\>. Repetition confirmed on continuation pages. |
| MC-32 | All captioned tables; Part 2 preflight | Last row of every captioned table set to keep with its caption; the hard page break before the preflight removed. |
| MC-33 | Table 7.2 | ID column widened from 497 to 560 twips; the criterion column narrowed from 3981 to 3918 so the table width is unchanged. |

*Table G.1. Findings of REVIEW 5: 43 of 43 applied in v0.5 (SC-01 to SC-10 and MC-01 to MC-33); none rejected or left unapplied.*

**Not applied.** None. Fixes that needed a value no source gives mark it UNVERIFIED and set it at MS7, before criteria-frozen: the solver and noise floor values that bound the RB3(a) range (SC-01), the A4 η̄ grid spacing (MC-26) and the lower rungs of the Heun dt ladder (SC-03). The M2 network coupling for K4-net stays UNVERIFIED (MC-03). Two fixes needed an interpretation, recorded in their rows: the start of the G1 fit window for M2, which has no amplitude threshold (SC-06), and the agreement tolerance for the K9 ratio-scaling fallback (SC-05). The source reports R1–R7 and RESULT A/B were not re-read for v0.5, so no decision could be checked against them; none conflicts with the plan or with REVIEW 5.

**Addition.** Added after the review, with no review ID: section 10.9 (Working with Claude Code in VS Code), the matching lines in the section 10.1 tree and .gitignore, and the MS0 row of Table 11.1. No D-item, CP row or count changed.

# Part 1 handoff

**Appendix (moved unchanged from the end of Part 1).** This page fixed the names, IDs and defaults that Part 2 builds on. Where Part 2 corrects it, the correction is in Table 12.1; the text below is unchanged except the (d) module paths (CP13).

Fixed for Part 2 unless Part 2 records a change. Conflicts (g) go into Part 2 Risks.

### (a) Symbols and parameter names

| **Symbol** | **Code name** | **Meaning** |
| --- | --- | --- |
| τ | tau_ms | Membrane time constant (10 ms); time unit of the code |
| τ_d | tau_d_ms | Synaptic decay time (M3) |
| η̄, Δ | eta_bar, Delta | Centre and half-width of Lorentzian excitability |
| J | J | Signed coupling; inhibition J \< 0; J_Devalle = 21 ↦ J = −21 |
| I(t) | I_drive | Common external (non-local) drive |
| r, v, s | r, v, s | Rate, mean potential, synaptic activation |
| η̄\_H | eta_H | Static Hopf value of η̄ (A4) |
| T_ramp, ε | T_ramp_s, eps | Ramp duration; ramp rate (eta_peak − eta_start)/T_ramp |
| A_ref | A_ref | Limit-cycle amplitude of v at ref_devalle (A5) |
| G, ρ | band_primary_hz, rho | Primary gamma band; relative gamma power P_G/P_total |
| M2, M3, M4, M3a, M3b | model.type | Model classes (Table 4.1) |
| P1–P5, NC1–NC3 | path.name | Parameter paths (4.4, 2.4) |
| ref_mpr, ref_ceni, ref_devalle | model.ref_point | (η̄, J, Δ) = (−5, 15, 1); (1, −20, 0.05) with τ_d 3/4.95/8 ms; (4, −21, 0.3) with τ_d 5 ms |

### (b) Items marked \[needs decision\] and proposed defaults

| **ID** | **Item** | **Proposed default** | **Section** |
| --- | --- | --- | --- |
| D1 | Output sampling of v, r | dt_out = 1 ms (1 kHz) | 2.3 |
| D2 | Primary gamma band G | 25–100 Hz; also report γ1 25–55 Hz, γ2 80–150 Hz, peak frequency | 2.3 |
| D3 | Total band for relative power | 1–150 Hz, linear detrend per window | 2.3 |
| D4 | Spectrogram | Hann; W = 2 s, step 1 s if T_ramp ≥ 60 s; else W = max(0.2 s, T_ramp/30), step W/2 | 2.3 |
| D5 | Baseline window | Last 5 s before ramp onset | 2.3 |
| D6 | Amplitude factors (mode N) | Relative and absolute gamma ≥ 2 × baseline | 2.3 |
| D7 | Amplitude threshold (mode D) | Envelope of band-passed v ≥ 0.1 × A_ref (A_ref from A5) | 2.3 |
| D8 | Minimum duration | ≥ 10 consecutive cycles; merge gaps shorter than one window | 2.3 |
| D9 | Collapse marker | r below 10% of baseline, or J reaching 0 | 2.3 |
| D10 | Xu raw EEG (Zenodo) | Out of scope | 2.5 |
| D11 | τ_d sweep | 1–50 ms, 30 log-spaced values | 3.2, 6.5 |
| D12 | η̄ path end points | eta_start = η̄\_H − 1.5; eta_peak = max(4, η̄\_H + 2) | 3.2, 4.4 |
| D13 | Δ sweep | 0.01–0.6, 30 linear values | 3.2 |
| D14 | J sweep | −40 to −5, 25 values | 3.2, 6.5 |
| D15 | Drive I(t) | Trapezoid (rise 0.1, plateau 0.3, fall 0.1 × T_ramp); I_amp = 1, set {0.5, 1, 2} | 3.2, 4.4 |
| D16 | Ramp duration | T_ramp = 120 s; sweep 1–1000 s, 13 log values | 3.2 |
| D17 | Network Euler step | dt = 10⁻³ τ | 3.2, 6.3 |
| D18 | Mean-field noise σ | Calibrated to N = 10⁴ network baseline std of v; also 0.5× and 2× | 6.4 |
| D19 | J path in P2 | J0 → 0, starting at t_on + 0.25 T_ramp, lasting T_ramp | 4.4 |
| D20 | Δ direction | Run both: P4a × 1.5, P4b × 2/3 | 4.4 |
| D21 | Ramp profile | Linear default; sigmoid variant with k = 10 | 4.4 |
| D22 | Interneuron-drive assumption (G2c) | Not rejected; M4 as robustness variant only | 4.3 |
| D23 | Continuation tool | BifurcationKit.jl; fallback WSL2 + PyCoBi/AUTO-07p, or S4 alone | 5.1 |
| D24 | Noisy/deterministic agreement on map | ≥ 90% of subgrid cells | 5.2 (A9) |
| D25 | MF solver settings | DOP853, rtol 10⁻¹⁰, atol 10⁻¹², max_step 0.05 τ; Radau cross-check | 6.2 |
| D26 | Initial perturbation | δ₀ = 10⁻⁶ on v | 6.2 |
| D27 | Durations | Baseline 5 s; hold 10 s; discard 2 s (noisy MF and network) | 6.2, 6.3 |
| D28 | Lorentzian grid formula | η_j = η̄ + Δ tan(π(2j − N − 1)/(2(N + 1))); confirm against Taher Eq. 8 | 6.3 |
| D29 | Gaussian/uniform width | Half-width at half maximum = Δ | 6.3 |
| D30 | Network v readout | Mean V_j over non-refractory neurons | 6.3 |
| D31 | Grid resolution | Accept if halving spacing near the boundary moves it \< 1 cell | 6.5 |

### (c) Analysis steps and simulation runs

| **ID** | **Content** | **Output** | **Figure** |
| --- | --- | --- | --- |
| A1 | M2 fixed points, stability | results/A1/a1_fixedpoints_2d.npz | FS1 |
| A2 | M2 linearisation, ring map | results/A2/a2_ring_map.npz | FS1; G1 |
| A3 | M2 ramp through saddle-node | results/A3/a3_sn_ramp.parquet | F4; G1 |
| A4 | M3 fixed points, Hopf curves | results/A4/a4_hopf_curves.npz | F3 |
| A5 | M3 limit cycles, criticality, A_ref | results/A5/a5_cycles.npz | F2 |
| A6 | M3 frequency map | results/A6/a6_freq_map.npz | F3; G2 |
| A7 | Slow-ramp metrics | results/A7/a7_ramp_metrics.parquet | F4 |
| A8 | Surge classifier and sensitivity | tests/test_surge_metrics.py; results/A8/a8_sensitivity.csv | FS5 |
| A9 | Regime map, failure reasons | results/A9/a9_regime_map.parquet | F5, F6 |
| A10 | Negative controls, drive dissociation | results/A10/a10_controls.csv | F6 |
| S1–S15 | Runs as in Table 6.2 | results/S1/ … results/S15/ (npz + json per run) | As in Table 6.2 |

### (d) Modules and functions

    src/mprsurge/units.py           tau_to_ms, rate_to_hz, freq_to_hz
    src/mprsurge/config.py          load_config, resolve_config, config_hash
    src/mprsurge/params.py          REF_POINTS, make_param_table
    src/mprsurge/provenance.py      seed_sequence, make_run_record, write_run_record
    src/mprsurge/models/mpr2d.py    rhs_2d, jacobian_2d
    src/mprsurge/models/mpr3d.py    rhs_3d, jacobian_3d
    src/mprsurge/models/fixed_points.py   fixed_points, classify_fixed_point
    src/mprsurge/models/ping4d.py, adaptation.py   (only if G2 or G3)
    src/mprsurge/ramps.py           profile_linear, profile_sigmoid, ramp_param,
                                make_path, breakpoints
    src/mprsurge/simulate_mf.py     run_mf, run_mf_noisy
    src/mprsurge/qif_network.py     lorentzian_quantiles, sample_eta_random,
                                sample_eta_gaussian, sample_eta_uniform,
                                run_qif_network
    src/mprsurge/analysis/bifurcation.py    sn_curve_2d, focus_boundary_2d,
                                hopf_condition_3d, hopf_curve_3d, quasi_static_sweep
    src/mprsurge/analysis/continuation/bk_cycles.jl   (Julia, BifurcationKit)
    src/mprsurge/analysis/surge_metrics.py  spectrogram_v, band_power, relative_power,
                                envelope, count_cycles, classify_surge, surge_metrics
    src/mprsurge/analysis/ramp_analysis.py  onset_delay, hysteresis_width, ramp_rate_table
    src/mprsurge/analysis/regime_map.py     classify_grid, failure_reason
    src/mprsurge/plotting/figures.py        make_F1 ... make_F6, make_FS1 ... make_FS6
    src/mprsurge/run.py             CLI entry: python -m mprsurge.run --config <yaml>
    scripts/run_A1.py ... run_A10.py    configs/S1.yaml ... S15.yaml    tests/

### (e) Config keys

    model:     type, ref_point, tau_ms, tau_d_ms, eta_bar, Delta, J, I_drive
    path:      name, profile, sigmoid_k, T_ramp_s, t_on_s, eta_start, eta_peak,
               J0, J_end, J_lag_frac, J_T_frac, I_amp, I_rise_frac,
               I_plateau_frac, I_fall_frac, Delta_factor
    solver:    method, rtol, atol, max_step_tau, dt_out_ms, delta0
    noise:     scheme, sigma, sigma_factor, dt_tau
    network:   N, dt_tau, V_peak, V_reset, het_dist, het_sampling,
               init_V_range, rate_bin_ms, n_raster, exclude_refractory
    durations: baseline_s, hold_s, discard_s
    analysis:  band_primary_hz, bands_secondary_hz, total_band_hz, window_rule,
               window_s, taper, rel_factor, abs_factor, amin_factor,
               min_cycles, collapse_r_frac
    sweep:     x_name, x_values, y_name, y_values, T_ramp_values
    seeds:     root_seed, n_seeds
    run:       id, workers        output: dir

### (f) Figures fed by sections 5 and 6

| **ID** | **Content** | **Fed by** |
| --- | --- | --- |
| F1 | M3 schematic and ramp protocol; MF and network r(t), v(t) overlaid; raster of 300 neurons; spectrogram of v | S8, A8 |
| F2 | One-parameter bifurcation diagram (fixed points, cycle max/min, Hopf labelled) with network symbols | A5, S4 |
| F3 | Two-parameter diagram: Hopf curves, frequency shading, 25 Hz contour, path arrows, example markers | A4, A6 |
| F4 | Onset delay, peak power, peak frequency, duration versus ε (log); quasi-static line; up/down; starting state; M2 comparison | A7, A3, S5, S11 |
| F5 | Surge/no-surge regime map with network symbols | A9, S7, S8 |
| F6 | Failure reasons; negative controls; drive dissociation | A9, A10, S6, S12 |
| FS1–FS6 | M2 diagrams; M3 validation; finite size, heterogeneity shape and noise; numerics; classifier sensitivity; conditional M4/M3a | A1–A2, S1; S3; S9–S11; S13; A8; S14–S15 |

### (g) Conflicts between reports (carry into Part 2 Risks)

| **ID** | **Topic** | **Values and sources** | **Resolution** |
| --- | --- | --- | --- |
| C1 | Gamma band | Ceni 25–100 Hz, Segneri 30–120 Hz \[R1\]; Xu 25–55/80–150 Hz \[R4\]; Borjigin 25–250 Hz \[R3; R4\] | D2; A8 sensitivity |
| C2 | M3 frequency | Devalle gamma (τ_d 5 ms, Θ 4, Δ 0.3) versus Ceni 5–30 Hz (η̄ 1, Δ 0.05, J −20) \[R1\] | A6 frequency map |
| C3 | Sign of J | Devalle −J S, J = 21; Ceni +J s, J = −20 \[R1; R5\] | Convention in 3.1; A4 (K7, K8) |
| C4 | Critical heterogeneity 0.1453 | Ceni Δ_c \[R1\] versus Devalle δ_c = Δ/Θ \[R5\]; R1 lists Devalle value as not found | A4 at η̄ = 1, 2, 4; check Devalle Eq. 8 |
| C5 | Lorentzian grid | "arctan" (MPR App. A text) versus tan (Taher Eq. 8) \[R5\] | D28; check PRX PDF |
| C6 | Network step, peak | dt 10⁻⁴ (MPR, Taher) versus 10⁻³ (Chen & Campbell); V_p 100 versus 200 \[R5\] | S13 |
| C7 | Xu power location | Posterior hot zone \[R2; R3\] versus frontal/central power, posterior coherence \[R4, full text\] | Use R4; not modelled |
| C8 | Xu max fold-change | 391 \[R4\] versus 392 \[R3, Koch\] | Not used numerically |
| C9 | M2 fixed-point type | MPR node and focus regions versus Devalle "always focus" \[R1\] | A1 |
| C10 | Gast erratum, DOI | Corrects depression equations \[R1\] versus Eq. 3.6 τ_A scaling \[R5\]; neco_a_01300 \[R1; R2\] versus 01369 \[R5\] | Check primary record before G3 |
| C11 | Interneuron vulnerability | Khazipov (IPSCs more sensitive) versus not selectively impaired \[R3, §3\] | D22; do not assume |
| C12 | Rat surge timing | Within 30 s versus starts about 10 s, lasts up to 20 s (Shaw) \[R4\] | Qualitative only |
| C13 | Xu heart-rate source | Press quote \[R3\] versus main-text Discussion \[R4\] | Use R4 only |
| C14 | Data-paper inconsistencies | Xu beta 13–25 vs 15–25 Hz; Lee 320 vs 400 s; Gofton vs Matory reference events \[R4\] | Not used numerically |
| C15 | Ceni details | DOI 1.5125216 vs 5.0017527; Δ 0.5 (text) vs 0.05 (caption) \[R1\] | Use 1.5125216 and 0.05 per R1; K7 tests it |

### (h) Five biggest risks so far

| **\#** | **Risk** | **Mitigation in this plan** |
| --- | --- | --- |
| 1 | M2 cannot sustain a surge, so the requested build order reaches a predicted dead end | Short diagnostic M2 stage; gate G1; M2 kept as the damped-ring comparison |
| 2 | M3 does not reach the gamma band on a plausible path (C2) | A6 frequency map before any ramp work; gate G2 to M4 |
| 3 | Surge metrics driven by ramp rate, shape, starting state or solver precision | A7 against ε with quasi-static reference; S13 tolerance and δ₀ checks; NC1 |
| 4 | Hypoxia mapping untested for every scalar; Δ direction unknown; η̄ and I indistinguishable in one population | Both Δ directions; P2/P3/NC2; claims limited to timing; M4 for mechanism |
| 5 | Surge definition could create or hide surges (qualitative targets, zero deterministic baseline) | Two measurement modes; classifier validated on synthetic signals; threshold sensitivity (A8); both absolute and relative power |
