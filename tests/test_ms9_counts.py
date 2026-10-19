"""MS9 9a: run counts from the plan wording, the sample cells and the D36 arithmetic (DL-210). Nothing integrates."""
import pytest

from mprsurge.analysis import ms8_counts as M8
from mprsurge.analysis import ms9_counts as M
from mprsurge.analysis import timing as T
from mprsurge.units import s_to_tau


def test_default_counts_by_plan_wording():
    f = M.all_runs()
    assert len(f["S6"]) == 3 * 4 + 4 + 4 == 20
    assert len(f["S7_map1"]) == 900 and len(f["S7_map2"]) == 25 * 13 and len(f["S7_noisy"]) == 15 * 15 * 10
    assert len(f["S16"]) == 14 + 64 and len(f["S12_net"]) == 1
    assert len(f["S12"]) == 13 + 13 + 13 + 5                          # NC1, NC2 (I_amp 1), NC3 at 13 T_ramp; NC1 at 5 cells at 120 s
    assert len(M.s12_runs({"nc1_map_cells_T_ramp": "grid13", "nc2_amplitudes": "all_three"})) == 13 + 39 + 13 + 65
    assert len(M.s11_runs()) == 120


def test_work_matches_table_9_1():
    f = M.all_runs()
    assert sum(r["tau"] for r in f["S7_map1"]) == pytest.approx(900 * 16500.0)               # Table 9.1: 3.0e8 steps at 20 per tau = 1.5e7 tau
    assert sum(r["tau"] for r in f["S7_map2"]) == pytest.approx(7.62375e6, rel=1e-5)         # Table 9.1: 1.5e8 steps = 7.5e6 tau
    assert sum(r["tau"] / r["dt_tau"] for r in f["S7_noisy"]) == pytest.approx(3.7575e10)    # Table 9.1: 3.8e10 Heun steps
    assert sum(r["tau"] for r in f["S6"]) == pytest.approx(3.175e5)                          # five 4-run families of 635 kept-seconds each
    assert sum(r["tau"] / r["dt_tau"] for r in M.s11_runs()) == pytest.approx(1.929e9, rel=1e-3)


def test_arithmetic_of_the_gates():
    assert M.g5_min_cells(900) == 27 and M.lhs_pass_count(64) == 52
    idx = M.subgrid_indices()
    assert len(idx) == 15 and idx[0] == 0 and idx[-1] == 29 and list(idx[1:] - idx[:-1]).count(3) == 1


@pytest.mark.parametrize("cell", M.SAMPLE_CELLS)
def test_sample_cells_resolve_and_have_the_intended_duration(cell):
    cfg = T.resolve_cell("configs/S5.yaml", cell)
    tau = T.tau_simulated(cfg)
    want = {"ms9_p3_t120": 16500.0, "ms9_s16_jt1p1": 17700.0, "ms9_nc1_t120": 13500.0, "ms9_nc1_net_t120": 13700.0, "ms9_noisy_t120": 16700.0,
            "delta_0.01": 16500.0, "delta_0.6": 16500.0, "ms9_map2_j-40_t316": s_to_tau(M8.run_integrated_s("path_hypoxia", 316.22776601683796))}[cell]
    assert tau == pytest.approx(want)
    assert cfg["run"]["kind"] == {"ms9_noisy_t120": "mf_noisy", "ms9_nc1_net_t120": "network"}.get(cell, "mf")


def test_the_nc1_proxy_falls_by_the_p2_amount():
    cfg = T.resolve_cell("configs/S5.yaml", "ms9_nc1_t120")
    p = cfg["path"]
    assert p["eta_start"] - p["eta_peak"] == pytest.approx(3.5)                  # eta_peak - eta_start of the headline P2 path
