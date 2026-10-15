"""julia_io on committed fixtures (a real smoke run, 1d); no Julia needed."""
import json
import shutil

import pytest

from mprsurge.analysis.continuation import julia_io as J
from mprsurge.provenance import environment_info

FIX = __import__("pathlib").Path(__file__).parent / "fixtures" / "julia"


def test_fixture_loads_and_matches_committed_manifest():
    out = J.load_smoke(FIX)
    assert out["record"]["manifest_sha256"] == J.sha256_file(J.manifest_path())
    assert out["record"]["bifurcationkit_version"] == J.pinned_bifurcationkit_version()
    assert len(out["branch"]) >= 3 and len(out["po"]) >= 3


def test_bad_manifest_hash_is_rejected(tmp_path):
    shutil.copytree(FIX, tmp_path / "o")
    p = tmp_path / "o" / "smoke.json"
    rec = json.loads(p.read_text(encoding="utf-8"))
    rec["manifest_sha256"] = "0" * 64
    p.write_text(json.dumps(rec), encoding="utf-8")
    with pytest.raises(J.JuliaOutputError, match="Manifest"):
        J.load_smoke(tmp_path / "o")
    assert J.load_smoke(tmp_path / "o", check_manifest=False)


def test_missing_field_bad_column_and_nonfinite_are_rejected(tmp_path):
    for case in ("field", "column", "nan"):
        d = tmp_path / case
        shutil.copytree(FIX, d)
        if case == "field":
            rec = json.loads((d / "smoke.json").read_text(encoding="utf-8"))
            del rec["commit"]
            (d / "smoke.json").write_text(json.dumps(rec), encoding="utf-8")
        elif case == "column":
            t = (d / "smoke_po.csv").read_text(encoding="utf-8").replace("vmax", "vmaxx", 1)
            (d / "smoke_po.csv").write_text(t, encoding="utf-8")
        else:
            t = (d / "smoke_branch.csv").read_text(encoding="utf-8").splitlines()
            t[1] = t[1].replace(t[1].split(",")[2], "nan", 1)
            (d / "smoke_branch.csv").write_text("\n".join(t), encoding="utf-8")
        with pytest.raises(J.JuliaOutputError):
            J.load_smoke(d)


def test_run_record_carries_pinned_bifurcationkit_version():
    assert environment_info(with_julia=False)["julia"]["bifurcationkit"] == J.pinned_bifurcationkit_version() == "0.8.7"
