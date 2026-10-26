"""RB9(a), unit-level (11c ruling 6, DL-351): run the dimensional-against-non-dimensional check once, as an analysis step, and store the measured value.

  .venv/Scripts/python.exe scripts/run_rb9a_unit.py [--out results/A11/rb9a_unit_level.json]

The same computation as tests/test_units.py::test_rb9a_... (mprsurge.analysis.rb9a_unit). Not a result run on a record: it integrates a 1 s path_eta ramp in memory twice
(non-dimensional and dimensional) at tau 10 and 20 ms and writes one labelled JSON with the maximum relative differences, the scope limit and the provenance. No new RB9(a) run.
"""
import argparse
import json
import sys
from pathlib import Path

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge.analysis import rb9a_unit as U


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="run_rb9a_unit")
    ap.add_argument("--out", default="results/A11/rb9a_unit_level.json")
    a = ap.parse_args(argv)
    env = P.environment_info(with_julia=False)
    out = U.all_taus()
    out.update({"label": "RB9(a) unit-level result (ruling 6, DL-351); NOT a run on the headline path; no run record",
                "scope_limit": U.SCOPE, "tolerance_frozen": 0.005, "git": env["git"], "metric": "max |dimensional - non-dimensional| / max |non-dimensional|, per variable r*tau, v, s*tau"})
    p = Path(a.out)
    p = p if p.is_absolute() else C.repo_root() / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("per_tau", "max_rel_diff")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
