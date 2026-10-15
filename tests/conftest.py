"""Session fixtures that build the git-ignored results the fast tests read, when they are missing (T97)."""
import pytest

from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import replication as RP

# (config, sets) in dependency order: A2 reads A1 and S1 (K4); A0 reads all of them.
_CHAIN = [("configs/A1.yaml", []), ("configs/S1.yaml", []), ("configs/S1.yaml", list(RP.K5_SETS)),
          ("configs/A2.yaml", [])]


def _ensure(config, sets):
    plan = R.build_plan(config, sets)
    if P.find_complete(plan.out_dir, plan.cells[0]["cfg"]) is None:
        args = ["--config", config] + [a for s in sets for a in ("--set", s)]
        assert R.main(args) == 0, f"building {config} {sets} failed"


@pytest.fixture(scope="session")
def upstream_results():
    """A1, S1 (K4 and K5 runs) and A2 results; built through the runner only if missing."""
    for config, sets in _CHAIN:
        _ensure(config, sets)


@pytest.fixture(scope="session")
def a0_result(upstream_results):
    _ensure("configs/A0.yaml", [])
