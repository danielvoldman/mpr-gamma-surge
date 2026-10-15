# MS2 gate report: G0 part 1 (mean field only)

Plan: Table 11.1 MS2, 7.1 G0, Table 7.1. Tolerances: `configs/replication.yaml` as frozen (tag `tolerances-frozen`, SHA-256 667d3b78...19a5, DL-084); no tolerance changed in MS2. Results: `results/A0/a0_replication.csv` (run A0_0000_724055e00481, `criteria_sha256` = frozen hash). Every row depends on UNVERIFIED items; they are listed per row.

## Rows

| Row | Measured | Frozen tolerance | Result | UNVERIFIED items the row depends on |
|---|---|---|---|---|
| K1 | 20/20 r values within one cell at half spacing (18/20 at base spacing; the two cusp points need half spacing, DL-081) | count-change node within (0.05, 0.1) of the formula point, all 20 r | pass | A1 refinement widths, band +-4 and box +-10 cells (DL-085, DL-086 2); K1 edge definition (DL-064, DL-086 3) |
| K2 | 189/189 J rows at base spacing, 261/261 at half; max offset 0.5 cells; one sign change per base row; C9: node region exists | discriminant sign change within (0.05, 0.1) of eta_f(J), all rows | pass | K2 root choice, highest-r root per J row (DL-086 4); refinement widths |
| K3 | at (-5, 15): saddle, stable_focus, stable_node | exactly a focus, a node and a saddle | pass | none beyond the A1 readings (DL-086 1) |
| K4-MF | frequency error 2.13e-4, decay error 6.09e-3 (fit omega 5.7651, decay 0.23038; linearisation 5.7664, 0.23179; 26.2 tail cycles) | each <= 0.02 relative | pass | tail fraction 0.1 (DL-076, DL-079); fit window end 40 tau and tail rule (DL-089 1, 2); tau = 10 ms (DL-082); I_step reading and 280 tau run length (DL-088 1, 4) |
| K5 | one up and one down crossing in each of 5 checked periods; max spacing deviation 8.67e-13 tau | one up and one down per period; spacing within 0.1 tau | pass | burst definition (midpoint of the I = 0 node and focus), the 0.1 tau tolerance, tau mapping, period 40 tau with 2 + 5 periods (DL-082, DL-088) |

Result: K1, K2, K3, K4-MF and K5 pass, so G0 part 1 is met on the definitions above. A pass on an UNVERIFIED definition is a pass on our reading, not on a sourced one.

## Not part of MS2
- K4-net, K7 to K11 and the K8/S3 start-state selector are not part of MS2 and belong to MS5 (K4-net non-blocking until a source gives the M2 network coupling; the selector deferred by DL-085 item 2).
- No tag is created. `replication-pass` is MS5. `tolerances-frozen` is unchanged.
- The header of `configs/replication.yaml` still reads "DRAFT / NOT FROZEN". The file is frozen by tag and hash; editing the header would change the hash.

## Review (DL-092)
Fresh-context review of d007378..HEAD: no blocking defect, no wrong result, no tolerance change. Known, non-blocking, logged in DL-092: fast tests that read git-ignored results/ (fail on a fresh clone); A2 ring map is the linearisation with SE 0, so the D8 2-SE rule is vacuous there; D31 halving met along the fold, not at the cusp; A0 K5 does not cross-check the yaml forcing; hash_view file I/O.

## Carries into MS3 and later
- DL-073 step-onset filter bias in `envelope_growth`: fix deferred to MS7, strict xfail stays (DL-083 item 2).
- DL-077 items: (2) wired in MS2 (DL-085 item 3); (4) `find_complete` ProvenanceError in a pool sweep, known and accepted, not wired; (1), (3), (5) were fixed at MS1 (DL-078, DL-080).
- K7: the Hopf value 4.12 ms (A4-derived, UNVERIFIED) departs from the paper's 4.95 ms; the departure was approved (DL-079) and 4.95 is not reproduced (DL-074 to DL-076).
- From the review: the decisions on DL-092 (2) and (3) before G1 uses the ring map or D31 is claimed; the DL-092 (1) test fix before any CI.
