# MS13 13t-3 notes: findings of Part A (F2, F6 and the short captions of the six journal figures) that stay, and of Part B (FS1 to FS5) (DL-628 to DL-630)

Findings that could not be fixed inside the rulings and choices the reviewer should confirm. Nothing was fixed by shrinking, jittering or hiding a mark. Categories: ruled, stored, caption, display, open.

| # | finding | figure and panel | category | why it stays |
|---|---|---|---|---|
| 1 | STOP (C3 a): sentence 1 of the F2 short caption reads 'does not follow the mean-field branch closely', the RULED take-home wording (draft F2_TAKE_HOME, DL-128, DL-129); the image shows the network symbols on the mean-field branch in (a) and (b), and the plotted relative differences (c) are 13.2 and 12.4 percent at eta_bar 3.296, about 7 percent at 3.696 and at most 4.8 percent from 4.096 up (largest negative -2.5 percent) | F2 sentence 1, (a), (b), (c) | ruled | the ruling forbids changing the ruled text; the reviewer is asked for the sentence (proposal: 'Above the Hopf point the network amplitude lies close to the mean-field branch in (a) and (b) and differs from it by up to 13.2 percent in (c)') |
| 2 | the stored data do not say why the cycle bands end before eta_bar 8 in F3 (a) and (b): the stored A6 summary lists branch_end_eta 4.70, 4.60, 4.86, 5.56 and 6.78 for the slices tau_d 1, 2, 3, 5 and 8 ms at Delta 0.05 (8.0 for the others), slice status ok, no stop reason | F3 (a), (b) | open | C5: no clause was written; the cause of the stop of the continuation is not recorded (UNVERIFIED) |
| 3 | F6 short caption: to fit 600 words the sentence 'so the surge is not confined to P3' and the sentence 'Failed check: the network run of negative control 1 must not be in a surge class: FAIL' were removed from the SHORT caption (both stay in the full caption; the failed check is named in sentence 1 and again in the negative-control sentence) | F6 short caption | caption | C6: repeated prose without a ruled claim limit is removed first; every ruled limit stays, including the added sigma limit |
| 4 | the key handle of F2 is 3.8 font sizes (30.4 pt = 3.07 periods of the 9.9 pt dash-dot pattern); DL-630 says 3.7 (29.6 pt, 2.99 periods; the first test found it 0.1 pt short) | F2 key | display | a slip of the log text, corrected here and in DL-631 (cited entries are not amended) |
| 5 | F2 (c): the red title is the four RB1 rows; they are named in the red-title sentence of the short caption, so the short caption now ends the failed-check part with 'No other failed check is about this figure' (it said '4 further failed checks') | F2 short caption | caption | follows from C1; counts computed from the full caption (0) |
| 6 | the F6 key lists the failure labels a to h with plain words that are ours (UNVERIFIED), as before (13t-2 item 9) | F6 key | caption | unchanged |
| 7 | Part B (FS1 to FS5): see the end of this file | FS1 to FS5 | open | see below |

## Part B (FS1 to FS5): not exported in 13t-3 (DL-629 D1, D3; DL-631)

FS1 to FS5 are left 'failing' in docs/ms13_export_checklist.json; no FS journal file was written, no FS code was changed, the FS drafts are unchanged. What each draft panel draws and which FAIL statuses concern it is in docs/ms13_13t_progress.md (13t-3 Part B reading). Reasons and proposals for the reviewer:

| figure | status | reason | proposal |
|---|---|---|---|
| FS1 | not attempted | the step was already large (Part A plus the one build, checks, review); FS1 has 5 panels in 9.8 in and no FAIL row, it is the first candidate for the next step and may fit at 6.3 x 8.0 in | do FS1 first in 13t-4 as one figure; layout code of its own as for F2 and F6 |
| FS2 | not tried; expected not to fit on one page (area estimate, no layout was tried) | 12 panels (7.4 x 11.2 in), five trace panels, two panels with a FAIL title | split: FS2a = (a), (b) and (c) to (g) (K7, with the FAIL title of (b) drawn as its residual), FS2b = (h) to (l) (S3, K9, K10, K11; (l) NOT reproduced as worded) |
| FS3 | not tried; expected not to fit on one page (area estimate, no layout was tried) | 7 panels (7.4 x 12.6 in) with about 100 in-panel text cells (class shares, counts) | split: FS3a = (a) to (c) (finite size, S9), FS3b = (d) to (g) (S10, S11, controls, noisy subgrid with the RB2 FAIL evidence) |
| FS4 | not tried; expected not to fit on one page (area estimate, no layout was tried) | 9 panels (7.4 x 13.8 in) | split: FS4a = (a) to (d) (solver settings, floors; the RB6 solver FAIL 181 ms drawn), FS4b = (e) to (h) (network dt and V_p; the RB6 network FAIL drawn) |
| FS5 | not tried; expected not to fit on one page (area estimate, no layout was tried) | 11 axes (7.4 x 14.4 in) | split: FS5a = (a), (c), (d), (e) (classifier cases and noise), FS5b = (f), (g1) to (g4) (RB10 and RB9, the RB9(b) FAIL drawn) |

D2: every red title of an FS export needs evidence on its panel; the draft FS titles that carry a failure word are FS2 (b) and (l), FS3 (d), (e), (g), FS4 (a), (e), (f), FS5 (g2); the evidence (a drawn failure, a mark on the scale or one plain line) has to be built with the layout. Not done in 13t-3.
