"""A5 (MS6 6b): julia_io.load_a5 and analysis.a5 on committed fixtures and synthetic branches; no Julia needed."""
import json
import shutil

import numpy as np
import pandas as pd
import pytest

from mprsurge import config as C
from mprsurge.analysis import a5
from mprsurge.analysis.continuation import julia_io as J

FIX = __import__("pathlib").Path(__file__).parent / "fixtures" / "julia" / "a5"
A4_CENI_MS = 4.1209            # A4 value (DL-115)
A4_ETA_H = 2.8960461989737856  # configs/path_A4.yaml


def test_a5_config_resolves():
    cfg = C.resolve_config("configs/A5.yaml")
    assert cfg["run"]["kind"] == "a5" and cfg["output"]["dir"] == "results/A5"


def test_fixture_loads_and_matches_manifest():
    out = J.load_a5(FIX)
    assert out["record"]["manifest_sha256"] == J.sha256_file(J.manifest_path())
    assert out["record"]["bifurcationkit_version"] == J.pinned_bifurcationkit_version()
    for name in J.A5_NAMES:
        assert len(out["po"][name]) >= 5 and len(out["fixed"][name]) >= 5


@pytest.mark.parametrize("case", ["manifest", "field", "column", "nan", "direction", "branch"])
def test_bad_a5_output_is_rejected(tmp_path, case):
    d = tmp_path / case
    shutil.copytree(FIX, d)
    rec = json.loads((d / "a5.json").read_text(encoding="utf-8"))
    if case == "manifest":
        rec["manifest_sha256"] = "0" * 64
    elif case == "field":
        del rec["commit"]
    elif case == "branch":
        del rec["branches"]["devalle"]
    elif case == "column":
        t = (d / "a5_ceni_po.csv").read_text(encoding="utf-8").replace("vmax", "vmaxx", 1)
        (d / "a5_ceni_po.csv").write_text(t, encoding="utf-8")
    else:
        df = pd.read_csv(d / "a5_ceni_po.csv")
        if case == "nan":
            df.loc[2, "amplitude_v"] = np.nan
        else:
            df.loc[2, "direction"] = "sideways"
        df.to_csv(d / "a5_ceni_po.csv", index=False)
    (d / "a5.json").write_text(json.dumps(rec), encoding="utf-8")
    with pytest.raises(J.JuliaOutputError):
        J.load_a5(d)


def test_build_a5_on_fixture():
    arrays, flags = a5.build_a5(J.load_a5(FIX), A4_CENI_MS, A4_ETA_H)
    assert flags["criticality_ceni"]["supercritical"] and flags["criticality_devalle"]["supercritical"]
    assert flags["criticality_ceni"]["n_folds_of_cycles"] == 0
    assert flags["hopf_vs_a4"]["match"]
    assert flags["criticality_ceni"]["up_branch_stable_fraction"] == 1.0
    ref = flags["A_ref"]["value"]
    assert np.isfinite(ref) and arrays["A_ref"][0] == ref and 1.0 < ref < 20.0
    assert np.isfinite(flags["points"]["ceni_4.95ms"]["amplitude_v"])
    assert np.isfinite(flags["points"]["ceni_8.0ms"]["frequency_hz"])
    assert arrays["ceni_tau_d_ms"].max() <= 10.0 + 1e-9


def _branch(params, amps, direction="up", stable=True):
    return pd.DataFrame({"direction": direction, "param": params, "vmax": amps, "vmin": 0 * np.asarray(amps),
                         "amplitude_v": amps, "period_tau": 5.0, "frequency_hz": 20.0, "stable": stable})


def test_at_param_interpolates_and_is_nan_outside():
    po = _branch([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert a5.at_param(po, 2.5, "amplitude_v") == pytest.approx(2.5)
    assert np.isnan(a5.at_param(po, 3.5, "amplitude_v"))


def test_criticality_flags_subcritical_and_folds():
    pH = 1.0
    sup = _branch(np.linspace(1.0, 2.0, 20), np.sqrt(np.linspace(0, 1, 20)))
    assert a5.criticality(sup, pH, "SuperCritical", [])["supercritical"]
    sub = _branch(np.linspace(0.8, 1.0, 20), np.linspace(0.1, 0.5, 20))      # cycles below the Hopf
    c = a5.criticality(sub, pH, "SuperCritical", [])
    assert c["cycles_below_hopf"] and not c["supercritical"]
    fold = {"direction": "up", "type": "fold", "param": 1.5, "step": 9}
    assert not a5.criticality(sup, pH, "SuperCritical", [fold])["supercritical"]
    turn = {"direction": "down", "type": "fold", "param": 1.0004, "step": 7}  # turn-around at the Hopf: not a fold of cycles
    assert a5.criticality(sup, pH, "SuperCritical", [turn])["supercritical"]
    assert not a5.criticality(sup, pH, "SubCritical", [])["supercritical"]
