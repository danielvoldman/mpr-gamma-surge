"""S3 mean-field config, task and readouts (MS5 step 5d, DL-116). Toy runs are short and go to tmp_path."""
import json

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import run as R
from mprsurge.analysis import s3


def cells(cfg):
    return {c["cfg"]["model"]["tau_d_ms"]: c for c in R.build_plan(cfg).cells}


def test_kind_and_cells():
    assert "s3" in C.RUN_KINDS and R.TASKS["s3"] == "mprsurge.simulate_mf:run_s3"
    ce, de = cells("configs/S3_ceni.yaml"), cells("configs/S3.yaml")
    assert sorted(ce) == [3.0, 4.95, 8.0] and sorted(de) == [5.0, 50.0]
    for c in [*ce.values(), *de.values()]:
        m, p, d, s = c["cfg"]["model"], c["cfg"]["path"], c["cfg"]["durations"], c["cfg"]["solver"]
        assert c["cfg"]["run"]["kind"] == "s3" and p["name"] == "I_step" and p["I_amp"] == 0.0 and p["t_on_s"] == 0.0
        assert d["hold_s"] == 10.0 and (s["method"], s["rtol"], s["atol"], s["max_step_tau"]) == ("DOP853", 1e-10, 1e-12, 0.05)
    assert (ce[3.0]["cfg"]["model"]["eta_bar"], ce[3.0]["cfg"]["model"]["J"], ce[3.0]["cfg"]["model"]["Delta"]) == (1.0, -20.0, 0.05)
    assert (de[5.0]["cfg"]["model"]["eta_bar"], de[5.0]["cfg"]["model"]["J"], de[5.0]["cfg"]["model"]["Delta"]) == (4.0, -21.0, 0.3)


def test_hash_changes_with_a_parameter():
    base = cells("configs/S3.yaml")[5.0]["hash12"]
    assert R.build_plan("configs/S3.yaml", ["model.Delta=0.31"]).cells[0]["hash12"] != base
    assert len({c["hash12"] for c in R.build_plan("configs/S3_ceni.yaml").cells}) == 3


def test_toy_run_writes_record_and_both_starts(tmp_path):
    out = ["--set", f"output.dir={(tmp_path / 'o').as_posix()}", "--set", "durations.hold_s=0.5", "--workers", "1"]
    assert R.main(["--config", "configs/S3_ceni.yaml", *out]) == 0
    assert R.main(["--config", "configs/S3.yaml", *out]) == 0
    recs = sorted((tmp_path / "o").rglob("*_0000_*.json"))
    flags = {r.parent.name: json.loads(r.read_text())["flags"]["start"] for r in recs}
    assert set(flags) == {"ceni", "devalle"}
    assert flags["devalle"] == "devalle_fig3" and flags["ceni"].startswith("fixed_point_")


def test_readouts_on_synthetic_signals():
    t = np.arange(0, 10000.0, 1.0)
    sine = 1.0 + 0.5 * np.sin(2 * np.pi * 36.0 * t / 1e3)
    e = s3.evaluate_cell(t, sine, sine, 1e-6)
    assert e["f_fft_hz"] == pytest.approx(36.0, abs=0.3) and e["f_cross_hz"] == pytest.approx(36.0, abs=0.3)
    assert e["hold_dev"] < 0.02 and e["grown"] and not e["decays"]
    growing = 1e-3 + (t / 1e4) ** 2 * np.sin(2 * np.pi * 20.0 * t / 1e3)
    assert s3.evaluate_cell(t, growing, growing, 1e-6)["hold_dev"] > 0.02
    flat = np.full_like(t, 2.0)
    f = s3.evaluate_cell(t, flat, flat, 1e-6)
    assert f["decays"] and not f["grown"] and np.isnan(f["f_fft_hz"])
