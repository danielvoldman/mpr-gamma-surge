# MS10 evaluation rules (10d; written before any network run)

Status: FROZEN with the MS10 lists at 10d (the hashes are in the decision log, DL-308). Binding sources: `docs/plan.md` (Table 2.1, Table 7.2 RB1 and RB8, Tables 4.2 and 11.2 G4, 6.4 and CP21 for sigma), the frozen criteria (`configs/robustness_criteria.yaml`, tag `criteria-frozen`), and the rulings R1 to R24 in `docs/ms10_plan.md`. This file adds no criterion, changes no threshold and reopens no ruling. It says in words what the evaluators (`src/mprsurge/analysis/ms10_eval.py`, `scripts/evaluate_ms10.py`, tests in `tests/test_ms10_eval.py`) compute. Where the plan and the rulings are silent, the point is listed as **E-n** below, **none is chosen**, and the evaluator reads it from `configs/ms10/ms10_eval.yaml`, where it is null; the evaluator stops with `MissingChoice` when it needs a null value. The reviewer fills the values (a decision-log entry each) before any network record is read. Nothing here is simulated: the evaluators read stored records only.

## What every evaluator does first

1. The criteria loader gate (tag `criteria-frozen`) must verify; the RB1 and RB8 leaves are read from the tag's blob, not from the working file.
2. Any MS10 data file (lists, cells, references, eval choices, the two run configs) that is not FROZEN stops the evaluation.
3. Records are looked up by the rows of the frozen run lists, by name. A record is refused (the evaluation stops, nothing is skipped) if its git dirty flag is not exactly false, if it is a dry-run record, if its full config hash or its name differs from the row of the frozen list, or if its criteria SHA-256 is not the frozen one. A record in a family folder that is not a row of the frozen lists is refused. A listed record that is absent is reported as missing and the verdict of every part that needs it is INCOMPLETE; it is never replaced.
4. A record whose status is not ok is class `failed` (A9, never NS) and matches nothing.

## Classes and the mean-field comparator

The class of a network run is the frozen mode-N class of the network signal v (mean V over non-refractory neurons, 1 ms), with the window and step of rule D4 for its T_ramp and the 5 s baseline wholly in [0, t_on]. The mean-field comparator is the mode-D class of: the stored record for the headline at T_ramp 10 s and 120 s (`configs/ms10/mf_references.yaml`, SHA-256 verified; R13); the companion run for each S8 cell at 30 s; the companion run for the headline at 60 s (S9 and S10). **Same class** (primary) is the Table 2.1 correspondence: D-tr meets S+, S-rel or S-abs; D-sus meets S-sus; D-none meets NS. The second reading (post hoc, DL-258 b, R2) does not count S-rel as a match for D-tr; it is reported beside the primary one and feeds no gate. The limits DL-229 and DL-258 b apply to every network class; the C2 control classes (R17) are printed beside each ramp class (same N, T_ramp, shape, Delta and tau_d; 3 seeds) with no verdict.

## RB1 (R15, R18, R23)

*Headline, per T_ramp (10 s and 120 s), per seed (3 seeds).* A seed passes when (a) its class is the same class as the mean-field class, (b) its f_pk is within 5 percent of the stored mode-D f_pk (relative to the mean-field value; the frozen `f_pk_rel_tol`), and (c) its onset is within one spectrogram step of the mean-field onset (step W/2 for T_ramp below 60 s, 1 s from 60 s on; the frozen text). f_pk is the Table 2.1 peak frequency of the classifier's first episode (argmax of the PSD in 25 to 100 Hz in its peak-power window), so its resolution is 1/W: 3 Hz at 10 s, 0.5 Hz at 120 s. The difference in Hz and in frequency bins is printed beside the test (R18); the test itself is the 5 percent as written. The headline passes at a T_ramp when 3 of 3 seeds pass (frozen `classes_agree_seeds`). The post-hoc median reading takes the median f_pk and the median onset of the three seeds against the mean field, with the three classes still required to match; it feeds no gate (R23).

*Cells (S8 map cells, 30 s).* A cell agrees only if all 3 seeds fall in the class that matches the companion mode-D class of that cell (R15). RB1 needs at least 3 of the 4 cells to agree (frozen `classes_agree_cells`). f_pk and onset are not tested for cells (R23 names them for the headline). The stored 120 s class of each cell is printed beside the companion class.

*N rule (R18).* From S9 (60 s, 10 seeds per N): the number of seeds in the mean-field-matching class at N = 3e4 must be at least the number at N = 1e4 (class-based, primary). The f_pk and onset errors (median and range over the seeds) are printed for every N and are not a pass test (frozen `no_worse_tolerance`).

*RB1 verdict.* PASS when both headline T_ramp pass, the cells pass and the N rule passes; FAIL when every part is in and one fails; INCOMPLETE otherwise. Failing RB1 is G4 (frozen `on_fail`).

## Sigma check (R16, R21)

The network baseline std of v of each of the 6 S8 headline runs (3 seeds at 10 s, 3 at 120 s) is the sample std (ddof 1, DL-120) of the 1 ms v series over the 5 s baseline [0, t_on). The mean-field mode-N baseline std at the frozen sigma must lie inside the range (minimum to maximum) of those 6 values. If it does not, it is reported as a limitation and sigma stays frozen (MS7); the evaluator never writes sigma. The six values are printed with the number of distinct values: the baseline of a seed is expected to be the same at both T_ramp because the parameters are constant before t_on (UNVERIFIED, the evaluator reports it, it does not assume it). **The mean-field value is not confirmed at 10d (R21, DL-302): the stored value 0.038852 is the 10-seed mean of runs at sigma 0.0623888, not the frozen 0.0624, and those records carry git dirty = true. The evaluator therefore requires `mf_baseline_std` and its source in the choices file (E-10); nothing was substituted.**

## S9 (finite size)

Per N (1e3, 3e3, 1e4, 3e4): class counts, seeds in a surge class, seeds in the matching class (both readings), and for each metric named in `s9_metrics` the median and the range over the seeds (and the number of seeds for which it is defined). No threshold is applied. Available metrics are those the stored v and the frozen classifier give: onset, f_pk, duration, cycles, peak absolute power (P_G), peak relative power (P_G / P_total), baseline std of v. The J_exit metrics need the path grid and the D8 machinery and are not computed. The N rule above is evaluated here. Control classes are printed beside each N.

## S10 and RB8, heterogeneity part (R8)

Gaussian and uniform must each give the Lorentzian network class in 3 of 3 seeds. The Lorentzian runs are the S10 Lorentzian runs (R3, separate records). How the comparator is formed when the three Lorentzian classes differ (E-7) and what "give the class" means (E-8) are choices. The class of each shape against the mean-field class and the control classes (C2, the Lorentzian one is the N = 1e4, 60 s control) are printed beside. M4 and adaptation parts of RB8 are MS12.

## G4 (R24)

Report-only for the run order. The network misses the surge at an N when no seed at that N is in a surge class (S+, S-rel, S-abs; primary reading); the post-hoc count without S-rel is printed. The text of the three consequences of Tables 4.2 and 11.2 is produced with the truth of each condition: (1) misses at N = 1e4 and 3e4 gives a finite-size limitation and the model is kept; (2) disagreement in 2 or more of the 4 cells gives a rerun of RB6, whose network parts are S13 runs at MS11 (R9); (3) the affected results are reported as mean-field-only (our reading, UNVERIFIED: applies when (1) or (2) holds). If RB1 passes, G4 is not triggered.

## Unspecified evaluation choices (none chosen)

| E-n | Point left open | Allowed values in the choices file |
|---|---|---|
| E-1 | How the network onset is read. R2 and R23 say raw crossing, primary; the plan defines the raw crossing for the noise-free mode-D envelope only (UNVERIFIED for a noisy network record, ms10_plan.md fact 5; the crossing may never occur, DL-226 (6)) | `classifier_centre` (centre of the first flagged window), `classifier_start` (its start), `raw_crossing` (first time the band-passed Hilbert envelope reaches 0.1 x A_ref after t_on, with no cycle count and no D8; the definition is ours, UNVERIFIED) |
| E-2 | A seed with no f_pk or no onset to compare (no episode, or no crossing): whether the test is not met or skipped for that seed | `not_met`, `vacuous` |
| E-3 | Whether "within 5 percent" and "within one step" include the boundary | `inclusive`, `strict` |
| E-4 | Samples of the 5 s sigma-check window: 5000 samples [0, 5) s or 5001 including t = 5 s | `half_open`, `closed` |
| E-5 | Whether "lies inside the range" includes the end values | `inclusive`, `strict` |
| E-6 | Which metrics S9 tabulates (M10-10 was not ruled) | a list of `onset_s, f_pk_hz, duration_s, cycles, peak_p_g, peak_rho, baseline_std_v` |
| E-7 | RB8 comparator when the Lorentzian classes differ across seeds (R4: Lorentzian seed s and Gaussian seed s do not share a stream) | `paired_by_seed_index`, `modal_lorentzian_class` (a tie is UNDETERMINED) |
| E-8 | RB8 "give the class": same label, or the same surge-class membership (same label outside the surge classes) | `exact_label`, `surge_correspondence` |
| E-9 | Which lists' records count for "the network at N" in G4 | a subset of `S8, S9, S10` |
| E-10 | The mean-field baseline std of v for the sigma check (R21 not confirmed) and its run ids and file hashes | a number and a text |

Also not chosen and not configurable, stated as facts: the evaluators use the classifier's own f_pk (Table 2.1) for the network; the cell verdict ignores f_pk and onset; a median and a range over seeds are the only aggregation in S9; no multiple-comparison or confidence statement is made.
