"""A3 analysis driver (MS4 step 4d) on two toy stored runs in tmp_path; nothing integrates."""
import importlib.util
import json

import numpy as np
import pandas as pd

from mprsurge import config as C


def _drv():
    spec = importlib.util.spec_from_file_location("run_A3", C.repo_root() / "scripts" / "run_A3.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _toy(d, name, T, with_jump):
    t = np.arange(0, 3000.0)                         # ms, 1 ms grid
    eta = -6.0 + 3.0 * t / t[-1]
    r = np.where((t > 1500) & with_jump, 5.0, 0.1) + 0.0 * t
    v = np.where(t > 1500, np.exp(-(t - 1500) / 1e6) * np.sin(2 * np.pi * 60 * (t - 1500) * 1e-3), 0.0)
    np.savez(d / f"{name}.npz", t_ms=t, r=r, v=v, eta=eta)
    (d / f"{name}.json").write_text(json.dumps({"status": "ok", "wall_time_s": 1.5,
                                                "config": {"path": {"T_ramp_s": T}}}))


def test_two_toy_runs_give_two_rows(tmp_path):
    _toy(tmp_path, "S2_0000_a", 1.0, True)
    _toy(tmp_path, "S2_0001_b", 2.0, False)
    out = tmp_path / "a3.parquet"
    assert _drv().main(tmp_path, out) == 0
    df = pd.read_parquet(out)
    assert len(df) == 2 and list(df["T_ramp_s"]) == [1.0, 2.0]
    assert df["ring_class"].tolist()[1] == "no_jump"
    for col in ("t_jump_s", "eta_jump", "offset", "offset_steps", "rate", "se", "cycles_fit", "ring_class",
                "t_jump_s_f03", "t_jump_s_f07", "offset_steps_f03", "wall_time_s"):
        assert col in df.columns
