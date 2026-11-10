# MS13 13w notes (DL-712)

Written for: the owner who rules on close items 22, 53 and 54, the FS5 tag question and the venue before any tag. Plain words. Nothing in this step changes a result, a figure file, a frozen criterion or the plan (docs/plan.md, read-only). Anything not sourced from the code, the stored files, the plan or the decision log is marked UNVERIFIED.

## W2. FS1 test point (close item 54, G2b-fs1-test-point, DL-646)

Outcome: (b). The two panels show different states of the system at the same grid position, and the text only half says so. Nothing is applied; proposed wording is below for the owner's ruling.

### What (c) and (d) plot

- Test point: eta_bar/Delta = -5, J/sqrt(Delta) = 15, Delta = 1, tau = 10 ms. In (a) to (c) it is the circled dot, grid node eta index 100, J index 150 (read from results/A2/a2_ring_map.npz; the node coordinates are exactly -5.0 and 15.0).
- Panel (c) plots, at every grid node, the cycles per e-fold of the stable focus (a fixed point that the system approaches with damped oscillation) where the focus frequency is inside 25 to 100 Hz. It comes from the A2 ring map, which is built on the A1 root-count grid. The A2 run record (results/A2/A2_0000_ac3c1fb033cc.json) has model.I_drive = 0.0, and the A1 record (results/A1/A1_0000_695d1f3d53a7.json) lists I_drive 0.0. So the map is evaluated with the input current I = 0 (the ring-map file itself stores no input current; that part is a reading from the run records, UNVERIFIED as a statement about the file, sourced from the records).
- Panel (d) plots the recorded S1 step run (results/S1/S1_0000_2bffa787ba51): the firing rate r after the input current is stepped from 0 to 3 (path I_step, I_amp 3.0, t_on 0). The run starts in the low state r = 0.0811 (the stable node at I = 0) and ends at r = 1.3732. The fit and the linearisation printed with it are evaluated at the fixed point after the step: src/mprsurge/analysis/ring.py line 208 calls post_step_focus(eta_bar, J, Delta, I_drive + I_amp), that is at I = 0 + 3 = 3.

### What the four numbers are (stored arrays, read today)

- 52.82 Hz and 1.710 cycles per e-fold (panel c, test-point node): the stable focus that exists at I = 0. Its firing rate is r = 1.0306 (ring_r), eigenvalue -0.3089 + 3.3186 i per tau. 3.3186/(2 pi x 0.010 s) = 52.82 Hz; 3.3186/(2 pi x 0.3089) = 1.710.
- 91.77 Hz and 3.96 cycles per e-fold (panel d): the stable focus that exists after the step to I = 3. Its firing rate is r* = 1.3732 (k4_r_star, the dashed line in (d)), eigenvalue -0.2318 + 5.7664 i per tau (k4_lambda). 5.7664/(2 pi x 0.010 s) = 91.77 Hz; 5.7664/(2 pi x 0.2318) = 3.96. The fitted values of the recorded trace are 5.7651 and 0.2304 per tau (relative differences 2.1e-4 and 6.1e-3, allowed 0.02), so the trace rings at about 91.8 Hz as the linearisation says.
- Neighbours of the test-point node in (c) run from 1.40 to 1.99 cycles per e-fold, so 1.710 sits in a smooth field; 3.96 is not on this map at all (the map's largest value inside the band is 5.10, at other nodes).

So the two values are not two values of one labelled quantity at one state: they are the same kind of quantity (frequency, cycles per e-fold of the stable focus) at two different input currents (I = 0 and I = 3), hence at two different stable foci (r = 1.0306 and r = 1.3732). This is not a STOP-class (c) result. It is consistent with the reading in DL-646, now sourced from ring.py line 208 and from the run records instead of only from the stored fields.

### Do the caption and the image say which is which?

- Image (journal PNG): the panel (d) title is "Step response, test point"; the panel (c) title is "Cycles per e-fold in the band". No input value is on the image, and no number from the table above is on the journal image (the draft panel (d) prints fit and linearised numbers and the title "step I = 0 to 3"; the journal panel does not). The test-point mark in (c) is the same circled dot as in (d)'s caption sentence.
- Short and full caption: "(d) ... a step of the input current from 0 to 3 at the test point" (full caption); the Parameters paragraph says (a) to (c) are "drawn on the grid of the root-count run, whose record lists an input drive of 0 ...", (d) is "drawn at eta_bar -5, J 15 and Delta 1 with the input current stepped from 0 to 3", and ends "Panels (c) and (d) are drawn at different parameter values." The short caption carries the Parameters sentence and the same last sentence. The captions never give 52.82, 1.710, 91.77 or 3.96, never say that the focus at the test point is a different focus before and after the step, and never tell the reader that the ringing in (d) is faster and less damped than the value the map (c) shows at the same circled dot. A reader who compares the dot in (c) with the trace in (d) can be misled; a careful reader of the Parameters paragraph can work it out.
- The alt text of (b) says "the test point is on the grey boundary". The stored map does not support "on": the node and every node in the 7 by 7 block around it hold a focus, and the nearest node without a focus is 8.6 grid steps away (5 steps in eta, 7 in J, about 0.25 and 0.7 axis units). "Near the grey wedge" is what the data support (UNVERIFIED how this looks on the image). Not changed; for the owner.

### Proposed wording (NOT applied; for the owner's ruling)

Add to the (c) sentence of the full caption (and its short counterpart): "At the circled test point the map is read with the input current at 0, where the stable focus has frequency 52.82 Hz and 1.710 cycles per e-fold (recorded)."

Add to the (d) sentence: "After the step to 3 the system settles on a different stable focus (firing rate 1.3732, against 1.0306 at input 0); its linearised oscillation is 91.77 Hz with 3.96 cycles per e-fold, so the values of (c) at the test point do not describe this ringing."

Consequences if applied (UNVERIFIED planning, not run): the FS1 caption hashes change; the FS1 short caption has 570 words by `wc -w` against the limit of 600 (configs/journal_export.yaml short_max_words_FS1), and the two additions are about 80 words, so either other prose goes or the limit is raised by a ruling (Y2: a ruled limit is never dropped for length; repeated prose without a ruled limit goes first); the captions and supplement of FS1 need a rebuild or a scripted text edit like 13v's FS5 fix, with a new final hash list; the independent comparison and verifier would have to pass again. The image would not change.

## W3. MS12 and FS6 facts (close item 22)

All from the plan (docs/plan.md, read only) and the repo. Nothing was run.

### What MS12 is

- Table 11.1 (plan line 1363): "MS12 | Extensions S14, S15 (only via G2 or G3) | Criteria committed before the runs | MS13". S14 is "PING (G2 or robustness)", model M4 (E-I, instantaneous synapses), "Specified once M4 equations are taken from primary sources", feeds FS6 (plan line 761). S15 is "Adaptation (G3 only)", models M3a/M3b, "Specified from primary sources", feeds FS6 (line 762).
- Its job: run the optional model variants (PING circuit, adaptation) as a robustness check or, if gate G2 or G3 had fired, as the main route.

### What FS6 would show

Table 8.1 (plan line 913): "FS6 | M4 or M3a/M3b | S14, S15 | fig_FS6.py | Only if G2 or G3 triggers". Plan line 851: RB8 (model variants) lists "M4 and M3a/M3b via G2/G3" and the figures "F4; FS3; FS6". So FS6 is the only figure that depends on MS12 in Table 8.1. Other figures that mention the MS12 gap carry the claim limit MS12-C1 (F1 to F6; ms13_plan.md line 264), but they do not draw MS12 data.

### What MS12 needs

- New simulation: yes, by the plan's own definition (S14 and S15 are run families; plan Table 9.1 says their compute is unknown until the equations are fixed, line 947).
- Inputs not in the repo (checked by listing src/mprsurge/models: only fixed_points.py, mpr2d.py, mpr3d.py): no M4 model, no M3a/M3b model, no S14 or S15 run list or config. D42 (the M4 form) is still [needs decision] and must be decided "before S14 or any RB8 M4 run" (plan line 1497). The plan says the M4 equations must "come from primary sources before S14 or S15" (line 1511); the Dumont and Gutkin 2019 Eqs. (7)-(8) are given as printed in plan section 7.3 (line 865), and the M3a equations need the Gast et al. paper and its erratum (line 880; Table 9.1 note: "S15 by the Gast publisher PDF").
- The M4 criteria for RB8 are open: configs/robustness_criteria.yaml line 207, M4_criteria value null, status open, "deferred by owner ruling DL-157 (F-23): written before M4 runs (D42 open, G2 does not trigger, DL-133); no ruling owed now". The frozen criteria hash would have to be extended by a new commit; the existing tag criteria-frozen (dd8330c) must not move.
- MS12's own "done when": criteria committed before the runs.
- Then FS6 needs a new figure script and builder (make_FS6 currently refuses with a named error citing MS12-C1, src/mprsurge/plotting/figures.py line 6787; tests/test_fig_F3.py line 52 expects the refusal and that scripts/fig_FS6.py does not exist; plan Table 8.1 lists fig_FS6.py).

### What the plan's MS13 "done when" says, word for word, and what is met

Table 11.1, row MS13 (plan line 1364): deliverable "Figures F1–FS6 with provenance"; done when "Each built from a clean tree and tagged"; unlocks "MS14".

- Built from a clean tree: met for the 13 journal figures (F1 to F6, FS1 to FS5; F4 and F5 are each split into two files) from build commit 5e90575, every provenance record dirty = false (DL-701), one exception recorded (the A4 record, git.dirty = true; close item 2). The FS5 caption and supplement were edited after that build by script (DL-705, DL-706); W1 below tests whether the builder gives the same bytes.
- Tagged: not met. No fig-*-v tag exists; tags are made only when the owner says "tag".
- "F1–FS6": FS6 not produced, so the list is not complete (close item 22).
- Per docs/ms13_close.md lines 9 and 10, MS13 is therefore not done by the plan's own condition until the tags exist and the FS6 gap is accepted or closed by the owner.

### What the decision log already says about skipping MS12

- DL-133 (2026-10-17, MS6): owner ruling that gate G2 does not fire: "So no G2 trigger fires: the project stays on M3, and M4 is robustness only, as the plan says." It rests on readings that are UNVERIFIED where the plan leaves room (DL-132); condition (c) of G2 "not rejected" is the plan's default, marked [needs decision].
- DL-261 (2026-10-23, MS9): G3 recommended NOT TRIGGERED; DL-271 (MS9 close) states "G3 NOT TRIGGERED (DL-261)".
- DL-421 (2026-10-28, ruling by the reviewer, 13a): "MS12 was not run ... S14 and S15 were not run, FS6 is not produced. Claim limit MS12-C1 ... the RB8 M4/adaptation parts have no result."
- DL-435 (2026-10-28, 13c) item (iv): "five supplementary figures FS1 to FS5; the FS6 gap is stated in the manuscript notes."
- DL-157 (F-23) defers the M4 criteria. docs/ms11_close.md lines 153 and 168 repeat that MS12 opens only via G2 or G3 and that no later entry triggers either.
- So the log already has a ruling that FS6 is not produced and that there are five supplementary figures (DL-421, DL-435). What it does not contain is a ruling that this is, or is not, a "deviation" from Table 11.1's wording, and the plan's own FS6 row is conditional ("Only if G2 or G3 triggers"). Whether the plan's row "Figures F1–FS6" is satisfied when the condition did not occur is a reading (UNVERIFIED).

### Options, cost and consequence

1. Run MS12 and build FS6 later. Cost: decide D42; transcribe or implement M4 (and M3a/M3b for S15) from primary sources; write S14 and S15 run lists and configs; write and commit M4 criteria before any run (a new criteria commit, outside the frozen set); implement the model code and tests; simulation of unknown size (plan Table 9.1: unknown); evaluate RB8 M4/adaptation parts; write fig_FS6.py and make_FS6; extend the readiness, verifier, comparison, caption and hash machinery of 13t to a 14th figure; remove the MS12-C1 refusal test. Consequence: the whole MS13 evidence set (hash list, evidence sheet, close document) is redone for the added figure; the tags wait; MS11 is stated as closed on paper with MS12 "only via G2 or G3" and both gates were ruled not triggered (DL-133, DL-261, DL-271), so running it is outside the plan's trigger and needs its own logged ruling (reading UNVERIFIED).
2. Drop FS6, as already ruled in DL-421 and DL-435. Cost: none in code; the paper states the gap (MS12-C1 and the five-supplement list). Consequence: MS13 closes with five supplementary figures; the owner can log one more line saying whether this is treated as a deviation from the row "Figures F1–FS6" or as the plan's conditional FS6 row not being triggered; the plan stays unedited either way. The 13v close document currently says the gap must be "accepted or closed by the user".
3. Another option found in the documents: run S14 "for robustness" only. The plan labels S14 "PING (G2 or robustness)" (line 761) and the model table says M4 is "Robustness; primary if G2" (line 463), and line 1579 says "M4 enters only through G2 or RB8 (D42)", while Table 11.1 says MS12 is "only via G2 or G3". The plan therefore points both ways on whether S14 may be run for robustness without G2. Cost: all of option 1 for M4 alone (no S15, since S15 is "G3 only", line 762); FS6 would show M4 only. Consequence: same machinery cost as option 1 but a smaller run set; it would also have to be reconciled with the Table 11.1 wording by a ruling (UNVERIFIED reading).

No recommendation beyond the documents is made. The documents support: the trigger did not occur (DL-133, DL-261, DL-271), the gap is already ruled (DL-421, DL-435), and the M4 route would need a decision (D42), criteria (DL-157) and new compute that does not exist yet.

## W4. Venue facts

Quotes are word for word.

### The plan (docs/plan.md, read only), manuscript and submission checklist

- Line 1398: "Submission through the MNA site with an arXiv identifier (CC-BY 4.0 licence) and an MNA account with an ORCID; a suggested handling editor with exact mean-field or neural mass experience (Laing, Coombes and Ashwin are documented by their publications) [R6, §6, §8(d)]."
- Line 1400: "Before submitting, check the MNA Submission page by hand or email the editorial office for length, template and code policy; claim no specific indexing [R6, §6]."
- Line 1402: "Revisions: a response letter in Noble format and new arXiv versions; after acceptance, the MNA LaTeX template within 30 days [R7, §8(d); R6, §8(d)]."
- Other plan lines that name MNA: 443 and 1523 ("MNA length and code policy" listed as unknown, [R6]); 781 ("MNA has no code mandate on the pages read [R6]"); 859 ("because MNA bars hiding known issues"); 1017 ("R6 (no code mandate at MNA, but software and data must be credited)"); 1546 (risk row 12, "Journal depth: recent MNA papers lean towards proofs and stochastic analysis"); 1663 and 1665 (source rows 63 and 65: MNA Home and Editorial Policies; Gale et al. 2022, MNA 2:1; Victor et al. 2025, MNA). Line 781 and 1664 also name JCNS and PLOS Comput Biol as comparison venues for code policy. The plan's MS15 checklist does not name Peer Community Journal.

### Ruling R1 (DL-554, decision_log.md line 5973; also docs/ms13_figure_rules.md line 37)

- docs/ms13_figure_rules.md line 37: "R1. Venue: Peer Community Journal (PCJ), after a Peer Community In recommendation. PCJ prefers jpg, tiff or png figures, forbids svg, wmf and emf, states no resolution, size or colour rule, and places figures in line with the text inside 2.54 cm margins (read by the user; not re-read here)."
- DL-554 (line 5973): "R1 VENUE (supersedes the conflicting parts of J4, J5, J9 and J14): the target is Peer Community Journal (PCJ) after a Peer Community In recommendation; ..." The words "supersedes" refer to the figure settings J4, J5, J9, J14 only. DL-554 does not mention the plan's submission checklist, MNA, arXiv or CC-BY.

### Every other place the repo names a venue

- configs/journal_export.yaml line 2 ("Target venue (DL-554 R1): Peer Community Journal (PCJ) after a Peer Community In recommendation ..."), line 6 ("the PCJ template and page size were not read"), line 36 (forbidden_formats svg, wmf, emf, "PCJ forbids them (DL-554 R1)"), line 37 ("pdf_size_flag_mb: 5 # UNVERIFIED; arXiv and Zenodo limits are to be checked by hand at MS15"), line 14 (Zenodo file).
- src/mprsurge/plotting/jchecks.py line 315 (forbidden formats, PCJ, DL-554 R1); src/mprsurge/plotting/style.py line 23 ("Placeholders until the journal is chosen (M13-14 (vii)); all UNVERIFIED."); DL-435 (vii) ("font, size and resolution are placeholders flagged UNVERIFIED until the journal is chosen").
- docs/ms13_13t_progress.md line 5 (R1 to R10, "venue Peer Community Journal"); docs/ms13_close.md line 70 (VENUE CONFLICT, MNA/arXiv/CC-BY against PCJ, "The user must confirm which one is meant"); docs/ms13_evidence_sheet.md line 526 (PCJ figure rules UNVERIFIED); docs/ms13_export_checklist.json line 1238 (PCJ margins not read); tests/test_ms13_13t.py line 492 (heading).
- Zenodo (the record for the zipped F1 source data, R10): docs/ms13_figure_rules.md lines 46, 70 and 104; the plan names only "a persistent identifier, service chosen at MS15" (D37, plan line 1780).
- The decision log has no entry that chooses MNA (the word appears only in DL-710 and DL-712, in this conflict note and the pre-check list) and no entry that withdraws the plan's checklist lines.
- README.md and CLAUDE.md name no venue.

### Conflict

Yes. The plan's checklist (lines 1398 to 1402) describes submission through the MNA site with an arXiv identifier, CC-BY 4.0 and an ORCID; ruling R1 (DL-554) sets Peer Community Journal after a Peer Community In recommendation as the target and every figure setting of 13t follows R1. They are different routes (a journal submission against a preprint plus community recommendation); whether they exclude each other is UNVERIFIED (the repo does not source how PCI and PCJ relate to MNA or arXiv, and R1 says the PCJ page was read by the user and not re-read). Not decided here. The owner confirms which venue, or both, before MS15; the 13t figure files are journal-neutral in content (PNG, TIFF 600 dpi, 6.3 in) and would need only a size check for another venue (UNVERIFIED).
