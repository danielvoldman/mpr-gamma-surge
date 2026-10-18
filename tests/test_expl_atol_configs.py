"""8f6 (DL-200): the atol configs are the headline config with only solver.atol set."""
from mprsurge import run as R

HEAD_H12 = "240de3ef73be"


def test_only_atol_differs():
    head = R.build_plan("configs/S5_ramp.yaml").cells[0]
    assert head["hash12"] == HEAD_H12 and head["cfg"]["solver"]["atol"] == 1e-12
    for f, a in (("1e-10", 1e-10), ("1e-14", 1e-14)):
        c = R.build_plan(f"configs/ms8/expl_atol_{f}.yaml").cells[0]
        assert c["hash12"] != HEAD_H12
        assert c["cfg"]["solver"]["atol"] == a
        for sec in c["cfg"]:
            if sec in ("run", "_resolved_from"):
                continue
            if sec == "solver":
                assert {k for k in c["cfg"][sec] if c["cfg"][sec][k] != head["cfg"][sec][k]} == {"atol"}
            else:
                assert c["cfg"][sec] == head["cfg"][sec], sec
