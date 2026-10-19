"""8h (DL-207): O12 post-surge file rows carry reason codes for every missing value; J0 flag; both windows kept."""
import importlib.util
from pathlib import Path

import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "write_o12_post_surge.py"


def _load():
    spec = importlib.util.spec_from_file_location("write_o12_post_surge", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run(**kw):
    x = {"run_id": "a", "profile": "linear", "T_ramp_s": 1.0, "mode": "N", "seed": 3, "cls": "S+", "episode": True, "terminated": True, "r0": 0.08,
         "J_exit_run": -5.0, "J_exit_static": -2.5, "exit_delay": -2.5, "r_mean_1s": 0.6, "r_mean_5s": 0.61}
    x.update(kw)
    return x


def test_defined_run_has_both_windows_and_no_reasons():
    m = _load()
    r = m.build_row(_run(), -21.0)
    assert r["r_post_1s"] == 0.6 and r["r_post_5s"] == 0.61 and not r["flag_no_J_exit_run"] and not r["flag_J_exit_run_at_J0"]
    assert r["reason_r_post_1s"] == "" and r["reason_no_J_exit_run"] == ""


def test_exit_at_j0_is_flagged_not_dropped():
    m = _load()
    assert m.build_row(_run(J_exit_run=-21.0), -21.0)["flag_J_exit_run_at_J0"]


def test_missing_values_get_reason_codes():
    m = _load()
    none = dict(J_exit_run=None, J_exit_static=None, exit_delay=None, r_mean_1s=None, r_mean_5s=None)
    assert m.build_row(_run(episode=False, terminated=None, **none), -21.0)["reason_no_J_exit_run"] == "no_episode"
    assert m.build_row(_run(terminated=False, **none), -21.0)["reason_no_J_exit_run"] == "episode_unterminated_at_run_end"
    r = m.build_row(_run(r_mean_5s=None), -21.0)
    assert r["reason_r_post_5s"] == "window_extends_past_run_end" and r["r_post_5s"] != r["r_post_5s"]
    df = pd.DataFrame([m.build_row(_run(episode=False, terminated=None, **none), -21.0), m.build_row(_run(J_exit_static=None, exit_delay=None), -21.0)],
                      columns=m.COLUMNS)
    assert m.check_reasons(df) == []
