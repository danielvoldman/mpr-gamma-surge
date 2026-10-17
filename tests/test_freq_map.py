"""A6 (MS6 6f): julia_io.load_a6 and analysis.freq_map on synthetic slices; no Julia needed."""
import json

import numpy as np
import pandas as pd
import pytest

from mprsurge import config as C
from mprsurge.analysis import freq_map as F
from mprsurge.analysis.continuation import julia_io as J


def _b(param, f, amp=None):
    param = np.asarray(param, float)
    return {"param": param, "frequency_hz": np.asarray(f, float),
            "amplitude_v": np.ones_like(param) if amp is None else np.asarray(amp, float)}


def test_a6_config_resolves():
    cfg = C.resolve_config("configs/A6.yaml")
    assert cfg["run"]["kind"] == "a6" and cfg["output"]["dir"] == "results/A6"


def test_crossings_known_contour():
    eta = np.linspace(0, 8, 41)
    assert F.crossings(eta, 10 + 5 * eta, 25.0) == pytest.approx([3.0])
    assert F.crossings(eta, 10 + 5 * eta, 100.0) == []            # level above the branch
    assert len(F.crossings(eta, 20 + 10 * np.sin(eta), 20.0)) >= 2   # non-monotone: all crossings listed


def test_contour_over_a_synthetic_plane():
    eta = np.linspace(0, 8, 81)
    slices = {td: _b(eta, 5 + 4 * td + 5 * eta) for td in (1.0, 2.0, 3.0)}   # f = 25 at eta = (20 - 4 td) / 5
    c = F.contour(slices)
    assert c["c25"] == pytest.approx([3.2, 2.4, 1.6])
    assert np.isnan(c["c100"]).all() and c["c25_count"].tolist() == [1, 1, 1]
    assert c["other"].tolist() == [1.0, 2.0, 3.0]


def test_rel_change_and_freq_at():
    assert F.rel_change([10.0, 12.0, 11.0]) == pytest.approx(2 / 11)
    assert np.isnan(F.rel_change([10.0, np.nan]))
    b = _b([1.0, 2.0], [10.0, 20.0])
    assert F.freq_at(b, 1.5) == pytest.approx(15.0) and np.isnan(F.freq_at(b, 2.5))


def test_k10_line_and_band():
    b = _b(np.linspace(0.4, 5.0, 50), 30 - 4 * np.linspace(0.4, 5.0, 50))
    line = F.k10_tau_line(b)
    assert line["monotone_decreasing"] and line["interval_ms"] == pytest.approx([4.0, 50.0])
    assert F.k10_band(line["freq_min"], line["freq_max"]) and not F.k10_band(2.0, 20.0)
    assert not F.k10_tau_line(_b([0.4, 1.0, 2.0], [10.0, 12.0, 11.0]))["monotone_decreasing"]


def test_k10_j_dependence_three_readouts():
    lin = {9.5: {"J": [-40.0, -5.0], "freq_hz": [10.0, 20.0], "unstable": [False, True]}}
    kb = {-40.0: _b([0.1, 1.0], [15.0, 15.0], [1.0, 2.0]), -5.0: _b([0.9, 1.0], [15.3, 15.3], [3.0, 3.0])}
    r = F.k10_j_dependence(kb, lin, (9.5,))["9.5"]
    assert r["linear_all"]["rel_change"] == pytest.approx(10 / 15) and not r["linear_all"]["pass"]
    assert np.isnan(r["linear_unstable"]["rel_change"]) and r["linear_unstable"]["n_J"] == 1   # one point: undefined
    assert r["cycle"]["rel_change"] == pytest.approx(0.3 / 15.15) and r["cycle"]["pass"]
    assert r["cycle_amp_v"][0] == pytest.approx(1.0 + (2.0 - 1.0) * (0.95 - 0.1) / 0.9)


def test_linear_points_reproduce_dl115():
    r = F.linear_points(F.K10_J_VALUES, (8.0,), 1.0, 0.05)[8.0]
    assert F.rel_change(r["freq_hz"]) == pytest.approx(0.134, abs=0.001)       # DL-115: 13.4 percent at 8 ms


def _julia(tmp_path, with_k10=True):
    """Synthetic Julia output with every slice build_a6 needs; frequency = 20 + 6 (eta - hopf)."""
    slices, rows = [], []

    def add(sid, group, base, lens_hi, hopf, p0=None, n=30):
        p = np.linspace(hopf, lens_hi, n)
        for x in p:
            rows.append([sid, x, 1.0, -1.0, 2.0, 5.0, 20 + 6 * (x - hopf), True])
        slices.append({"id": sid, "group": group, "status": "ok", "error": "", "base_parameters": base, "hopf_param": hopf,
                       "hopf_type": "SuperCritical", "n_hopf_points": 1, "hopf_params_all": [hopf], "n_po": n,
                       "po_special_points": [], "wall_s": 1.0, "hopf_frequency_hz": 20.0, "po_param_max": lens_hi})
    for D in (0.05, 0.1, 0.3):
        for t in (1.0, 5.0, 50.0):
            add(f"e_{D}_{t}", "eta_tau", {"eta": 0, "J": -21.0, "Delta": D, "td": t / 10}, 8.0, 2.9)
    for Jv in (-40.0, -21.0, -5.0):
        add(f"j_{Jv}", "eta_J", {"eta": 0, "J": Jv, "Delta": 0.3, "td": 0.5}, 8.0, 2.9)
    for Jv in F.K10_J_VALUES:
        add(f"k_{Jv}", "k10", {"eta": 1.0, "J": Jv, "Delta": 0.05, "td": 0.3}, 5.0, 0.41, n=60)
    rec = {"commit": "0" * 40, "dirty": False, "julia_version": "1.10", "bifurcationkit_version": "0.8.7",
           "manifest_sha256": J.sha256_file(J.manifest_path()), "periodic_orbit_method": "x", "equations": "x",
           "slices": slices, "timings_s": {"total": 1.0}, "written_utc": "now"}
    (tmp_path / "a6.json").write_text(json.dumps(rec), encoding="utf-8")
    pd.DataFrame(rows, columns=J.A6_PO_COLUMNS).to_csv(tmp_path / "a6_po.csv", index=False)
    return tmp_path


def test_load_and_build_on_synthetic(tmp_path):
    out = J.load_a6(_julia(tmp_path))
    assert len(out["slices"]) == 9 + 3 + 5
    arrays, summ = F.build_a6(out, 2.8960461989737856)
    assert np.isclose(arrays["eta_tau_D0.3_c25"], 2.9 + 5 / 6).all()          # f = 25 at hopf + 5/6
    assert arrays["eta_tau_D0.3_c100_count"].sum() == 0 and np.isnan(arrays["eta_J_c100"]).all()
    d = summ["devalle"]
    assert d["f_at_eta_4"] == pytest.approx(20 + 6 * (4 - 2.9)) and d["eta4_in_band"] and d["whole_region_ge_25"] is False
    k = summ["k10"]
    assert set(k["J_dependence"]) == {"8.0", "20.0", "40.0"} and k["blocking"] is False
    assert k["J_dependence"]["8.0"]["cycle"]["rel_change"] == pytest.approx(0.0, abs=1e-12)   # same synthetic branch at every J
    assert k["sub_checks"]["J_cycle_8ms"] is True
    assert arrays["po_slice_index"].max() == len(out["slices"]) - 1


@pytest.mark.parametrize("case", ["manifest", "field", "column", "nan", "slice", "count"])
def test_bad_a6_output_is_rejected(tmp_path, case):
    d = _julia(tmp_path)
    rec = json.loads((d / "a6.json").read_text(encoding="utf-8"))
    df = pd.read_csv(d / "a6_po.csv")
    if case == "manifest":
        rec["manifest_sha256"] = "0" * 64
    elif case == "field":
        del rec["slices"][0]["hopf_type"]
    elif case == "column":
        df = df.rename(columns={"vmax": "vmaxx"})
    elif case == "nan":
        df.loc[3, "frequency_hz"] = np.nan
    elif case == "slice":
        df.loc[3, "slice"] = "nope"
    else:
        rec["slices"][0]["n_po"] += 1
    (d / "a6.json").write_text(json.dumps(rec), encoding="utf-8")
    df.to_csv(d / "a6_po.csv", index=False)
    with pytest.raises(J.JuliaOutputError):
        J.load_a6(d)
