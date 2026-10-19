"""MS9 9a: the proposed seed keys collide with no key already used (DL-210; UNVERIFIED until confirmed). Nothing integrates.

A collision is equal keys or one key a prefix of the other (they would share a stream), as in test_criteria_draft.py; the calibration
keys [0] to [9] (the runner gives seed index s the key [s]) are compared for equality only, because [7, ...] and [8, ...] already sit
under them by the DL-141 convention (first element = milestone number)."""
from mprsurge.analysis import ms9_counts as M

from test_criteria_draft import _key_prefixes_in_repo

CALIBRATION = {(s,) for s in range(10)}
# Keys named in the decision log and the frozen criteria, written out so that the test does not depend on a scan finding them.
KNOWN = ([(7, 2), (7, 3), (7, 4, 0), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (7, 9, 0), (8, 1, 0), (8, 2, 0, 0)]
         + [(7, 4, s) for s in range(10)] + [(7, 9, 1, k) for k in range(64)] + [(8, 1, s) for s in range(10)]
         + [(8, 2, l, s) for l in range(3) for s in range(10)])


def _related(a, b):
    n = min(len(a), len(b))
    return a[:n] == b[:n]


def test_the_scan_sees_the_keys_the_proposal_must_avoid():
    used = _key_prefixes_in_repo()
    assert (7, 4) in used       # the F-19 key lives in the frozen file, not in a config: KNOWN carries it
    assert (8, 1) in used and (8, 2, 0) in used and (7, 6, 1) in used


def test_proposed_keys_collide_with_no_key_in_use():
    used = _key_prefixes_in_repo() | set(KNOWN)
    mine = M.proposed_seed_keys()
    assert len(mine) == len(set(mine)) == 31      # 10 subgrid + 1 network + 10 supplementary NC1 mode N (9b) + 10 reserved
    for m in mine:
        assert m not in CALIBRATION
        for u in used:
            assert not _related(m, u), (m, u)


def test_the_proposed_prefixes_do_not_overlap_each_other():
    pre = list(M.SEED_KEY_PREFIXES.values())
    for i, a in enumerate(pre):
        for b in pre[i + 1:]:
            assert not _related(a, b), (a, b)


def test_the_f19_key_is_untouched():
    """[7, 9], [7, 9, 0] and [7, 9, 1, k] are settled (DL-159, F-19); no proposed key shares their first two elements."""
    assert all(k[:2] != (7, 9) for k in M.proposed_seed_keys())


def test_the_9b_supplementary_key_is_new_and_collides_with_nothing():
    """[9, 4, s] (supplementary NC1 in mode N, M9-4) is not a key of the first 9a proposal and is related to no key in use or proposed."""
    supp = [(9, 4, s) for s in range(10)]
    assert all(k in M.proposed_seed_keys() for k in supp)
    others = [k for k in M.proposed_seed_keys() if k not in supp] + sorted(_key_prefixes_in_repo() | set(KNOWN))
    for k in supp:
        for u in others:
            assert not _related(k, u), (k, u)


def test_the_collision_rule_has_teeth():
    assert _related((8, 1, 3), (8, 1)) and _related((7, 9), (7, 9, 1, 5)) and not _related((9, 1, 0), (8, 1))
    assert not M.SEED_KEY_PREFIXES["s7_noisy_subgrid"] == (8, 1)
