"""Claim-limit labels printed in captions (MS13 13j, DL-477): label -> (short form, DL numbers).

Generated from the table in docs/claim_limit_labels.md (one definition; tests/test_claim_labels.py checks that this module equals that table). The short form is the one-line
content of the plan's section 5 table; the Greek letter sigma is written "sigma". A caption that is given these definitions prints them after each label.
"""
CLAIM_LIMIT_LABELS = {
    'MS9(e)-1': ('network-record surge classes at N = 1e4 are not evidence of a ramp-driven surge (control flagged 10 of 10 seeds; ramp 10 of 10)', ('DL-229', 'DL-230')),
    'MS9(e)-2': ('no claim that the regime map is robust to noise; S-rel not counted as ramp evidence in mode N', ('DL-242', 'DL-250')),
    'MS9(e)-3': ('label (c) is a flag, not a demonstrated cause', ('DL-270',)),
    'MS9(e)-4': ('the check covers 1,056 of 1,057 surge-class cells', ('DL-269',)),
    'MS9(e)-5': ('every D8-dependent class is provisional', ('DL-163', 'DL-208')),
    'MS9(e)-6': ('the boundary definition and the P3/P4 exit extension are ours', ('DL-254', 'DL-263')),
    'DL-163-D1': ('D8: the plan estimator fails 2 of 8 A8 ring items; classes provisional', ('DL-155', 'DL-157', 'DL-161', 'DL-163')),
    'DL-163-D2': ('zero baseline, including noise-free inputs', ('DL-158', 'DL-159', 'DL-163')),
    'DL-163-D3': ('RB3(a) not judged at the headline (coverage 0 to 2 of 13 T_ramp)', ('DL-163',)),
    'DL-163-D4': ('pure trend plus noise at W = 0.2 s; short-window false surges (306, 400, 172, 24 of 500 at W = 0.2, 0.333, 0.593, 1.054 s)', ('DL-161', 'DL-162', 'DL-163')),
    'G6-D1': ('no claim that onset follows the A4 entry–exit prediction; RB3(a) not validated (0 of 6 testable in-range runs within one A4 step)', ('DL-208',)),
    'G6-D2': ('headline delay taken from D43-floored runs; noise-free onset solver-dependent (DOP853 58.698 s, Radau 58.879 s)', ('DL-189', 'DL-208')),
    'G6-D3': ('RB3(b) reported under both onset readings', ('DL-208',)),
    'G4-C1': ('network at N = 1e4 and 3e4 does not reproduce MF classes (0 of 3 seeds at T_ramp 10 and 120 s; 1 of 4 cells)', ('DL-325',)),
    'G4-C2': ('surge result stated for the mean field only; no claim of robustness to finite-size fluctuations', ('DL-325',)),
    'G4-C3': ('no-ramp network controls are classified into surge classes', ('DL-325', 'DL-229', 'DL-231')),
    'G4-C4': ('sigma = 0.0624 checked and not confirmed; noisy MF labelled', ('DL-325',)),
    'G4-C5': ('no claim about heterogeneity-shape robustness (RB8 not evaluable)', ('DL-325', 'DL-322')),
    'G4-C6': ('the RB6 rerun was read as the network part of S13 (UNVERIFIED reading)', ('DL-325',)),
    'MS11-C1': ('headline class kept in 7 of 10 seeds at sigma (needs 8); controls reach 7 of 10 with no ramp', ('DL-394',)),
    'MS11-C2': ('no claim of f_pk or class agreement between network and MF (RB6 network f_pk FAIL)', ('DL-394',)),
    'MS11-C3': ("spectral and cycle frequency differ by 4.39 Hz at the headline (RB9(b) FAIL); peak frequencies are the classifier's spectral peaks", ('DL-394', 'DL-388')),
    'MS11-C4': ('RB9(a) rests on a unit-level test only', ('DL-394',)),
    'MS11-C5': ('DOP853 against Radau covers T_ramp 120 s only', ('DL-394', 'DL-337')),
    'MS11-C6': ('floor-level direction of RB3(b) unresolved at 10 s and 316 s', ('DL-394', 'DL-402')),
    'MS11-C7': ('all earlier failures and limits stand (RB1 FAIL, G7 not passed, D24 failed, G4-C1 to G4-C6, MS9 limits)', ('DL-394',)),
    'MS11-C8': ('RB6 network reading (ii) f_pk for episodes shorter than W uses a method not in the frozen rules', ('DL-401', 'DL-406')),
    'MS11-C9': ('cycle-frequency estimator in RB9(b) not named in the rules; 51 against 45 of 760 cells', ('DL-407', 'DL-412')),
    'MS12-C1': ('surge result stated for M3; no claim about M4 or M3a/M3b; RB8 M4/adaptation parts have no result', ('DL-421',)),
    'RB2 FAIL (plan label)': ('7 of 10 at sigma; noisy subgrid 97 of 225', ('DL-387', 'DL-242')),
    'D24 failed (plan label)': ('subgrid agreement 43.1 percent on raw classes', ('DL-242',)),
    'G7 not passed (plan label)': ('NC1 network S+', ('DL-228',)),
}

# A9 failure labels printed in F6 (13k, DL-482): label -> (short form, DL numbers). Generated from the second table of docs/claim_limit_labels.md; tests/test_a9_labels.py
# checks that this dict equals that table and that each source wording is verbatim in its source.
A9_LABELS = {
    'a': ('Delta above critical', ('DL-214', 'DL-244')),
    'b': ('tau_d outside window', ('DL-214', 'DL-244')),
    'c': ('a flag, not a demonstrated cause', ('DL-214', 'DL-270')),
    'd': ('ramp too fast for 10 cycles', ('DL-214', 'DL-244')),
    'e': ('no exit (D-sus or S-sus)', ('DL-214', 'DL-244')),
    'f': ('amplitude below the fixed threshold', ('DL-214', 'DL-244')),
    'g': ('Hopf point, no time inside', ('DL-244',)),
    'h': ('rejected by the damped (D8) clause', ('DL-244',)),
}
