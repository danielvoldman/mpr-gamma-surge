"""MS9 9d: RB4 bookkeeping of scripts/report_ms9_9d.py on synthetic class rows (the pre-registered thresholds 2 and 52)."""
import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("report_ms9_9d", ROOT / "scripts" / "report_ms9_9d.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


def _rows(change_oat=0, change_lhs=0, fail_lhs=0):
    names = [r["name"] for r in csv.DictReader(open(ROOT / "configs/ms9/runlists/runlist_S16.csv"))]
    rows = []
    for n in names:
        rows.append({"run": n, "class": "D-tr", "status": "ok"})
    oat = [r for r in rows if "_oat_" in r["run"]]
    lhs = [r for r in rows if "_lhs_" in r["run"]]
    for r in oat[:change_oat] + lhs[:change_lhs]:
        r["class"] = "D-none"
    for r in lhs[change_lhs:change_lhs + fail_lhs]:
        r["class"], r["status"] = "failed", "failed"
    return rows


def test_counts_and_thresholds():
    res, rows = R.rb4(_rows(), "D-tr")
    assert (res["n_oat"], res["n_lhs"], res["oat_changed"], res["lhs_unchanged"], res["rb4_pass"]) == (14, 64, 0, 64, True)
    res, _ = R.rb4(_rows(change_oat=2, change_lhs=12), "D-tr")
    assert res["oat_pass"] and res["lhs_pass"] and res["lhs_unchanged"] == 52
    res, _ = R.rb4(_rows(change_oat=3), "D-tr")
    assert not res["oat_pass"]
    res, _ = R.rb4(_rows(change_lhs=11, fail_lhs=2), "D-tr")      # failed counts as changed: 51 unchanged
    assert res["lhs_unchanged"] == 51 and res["lhs_failed"] == 2 and not res["lhs_pass"]


def test_each_oat_run_changes_one_parameter_both_directions():
    _, rows = R.rb4(_rows(), "D-tr")
    oat = [r for r in rows if r["group"] == "oat"]
    assert sorted((r["parameter"], r["direction"]) for r in oat) == sorted((p, d) for p in R.PARAM_KEYS for d in ("+10%", "-10%"))
