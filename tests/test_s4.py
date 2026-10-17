"""S4 sweep config, task and step readouts (MS6 step 6c, DL-127). Toy runs are short and go to tmp_path."""
import json

import numpy as np
import yaml

from mprsurge import config as C
from mprsurge import run as R
from mprsurge.analysis import s4
from mprsurge.simulate_mf import s4_values

ETA_H = yaml.safe_load((C.repo_root() / "configs" / "path_A4.yaml").read_text())["path"]["eta_H"]
HOPF_CENI_MS = 4.120858   # A4, docs/decision_log.md DL-115 (4.1209 ms)


def cell(cfgf, sets=()):
    return R.build_plan(cfgf, list(sets)).cells[0]


def test_kind_registered():
    assert "s4" in C.RUN_KINDS and R.TASKS["s4"] == "mprsurge.simulate_mf:run_s4"


def test_devalle_grid_from_a4_not_typed():
    c = cell("configs/S4.yaml", [f"path.eta_H={ETA_H!r}"])
    v = s4_values(c["cfg"])
    assert v.size == 61 and np.isclose(v[0], ETA_H - 2) and np.isclose(v[-1], ETA_H + 4)
    assert np.allclose(np.diff(v), 0.1) and np.isclose(v[20], ETA_H)
    assert c["cfg"]["s4"]["step_s"] == 2.0 and c["cfg"]["s4"]["read_s"] == 1.0   # 1 s discarded
    assert "eta_H" not in open(C.repo_root() / "configs" / "S4.yaml").read().split("path:")[1].split("\n")[0]


def test_ceni_grid_meets_owner_ruling():
    v = s4_values(cell("configs/S4_ceni.yaml")["cfg"])
    rel = v - HOPF_CENI_MS
    assert (rel < 0).sum() >= 2                                    # stable side
    assert ((rel >= 0.1) & (rel <= 1.0)).sum() >= 6                # inside the K7 fit window
    assert 1 <= (rel > 1.0).sum() <= 2                             # above the window
    assert np.all(np.diff(v) > 0)


def test_hash_changes_with_grid():
    h = cell("configs/S4_ceni.yaml")["hash12"]
    assert cell("configs/S4_ceni.yaml", ["s4.step_s=61"])["hash12"] != h
    assert cell("configs/S4_ceni.yaml", ["s4.values=[3.8,4.0]"])["hash12"] != h


def test_toy_sweep_runs_and_carries_state(tmp_path):
    out = ["--set", f"output.dir={(tmp_path / 'o').as_posix()}", "--set", "s4.values=[3.8,6.5]",
           "--set", "s4.step_s=8", "--set", "s4.read_s=4", "--workers", "1"]
    assert R.main(["--config", "configs/S4_ceni.yaml", *out]) == 0
    rec = next((tmp_path / "o").rglob("ceni_0000_*.json"))
    assert json.loads(rec.read_text())["flags"]["n_steps"] == 4
    z = np.load(next((tmp_path / "o").rglob("ceni_0000_*.npz")))
    assert list(z["step_param"]) == [3.8, 6.5, 6.5, 3.8] and list(z["step_up"]) == [1, 1, 0, 0]
    k, v = z["step"], z["v"]
    assert np.ptp(v[k == 0]) < 1e-3                                # stable side: nothing grows
    first_of_step2 = v[k == 2][0]
    assert abs(first_of_step2 - v[k == 1][-1]) < 0.5               # state carried over, not restarted
    tab = s4.step_table({n: z[n] for n in z.files}, 4.0, 1e-6)
    assert tab["decays"][0] and tab["v_ptp"][1] > 0.1


def test_step_table_and_pairs_on_synthetic_series():
    n, per = 4, 100
    t = np.arange(n * per) * 10.0                                  # ms, dt 10 ms
    k = np.repeat(np.arange(n), per)
    amp = np.array([0.0, 2.0, 2.0, 0.5])[k]
    v = amp * np.sin(2 * np.pi * 5.0 * t * 1e-3)                   # 5 Hz
    arr = {"t_ms": t, "r": v, "v": v, "step": k, "step_param": np.array([1.0, 2.0, 2.0, 1.0]),
           "step_up": np.array([1, 1, 0, 0])}
    tab = s4.step_table(arr, 0.5, 1e-6)
    assert np.allclose(tab["f_fft_hz"][1], 5.0, atol=0.3) and abs(tab["v_ptp"][1] - 4.0) < 0.2
    assert tab["decays"][0] and not tab["decays"][1]
    pr = s4.branch_pairs(tab)
    assert np.allclose(pr["param"], [1.0, 2.0]) and np.isclose(pr["v_ptp_down"][1], tab["v_ptp"][2])
    assert pr["v_ptp_down"][0] > 0 and pr["v_ptp_up"][0] == 0.0
