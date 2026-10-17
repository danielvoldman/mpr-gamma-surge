"""7f sensitivity part (DL-146): variants, synthetic set, reachability table, white-noise counts. Synthetic arrays only."""
import numpy as np

from mprsurge import config as C
from mprsurge.analysis import a8_sensitivity as S

A_REF = 2.176222


def test_variants_are_the_plan_list():
    assert set(S.VARIANTS) == {"V0", "band_30_120", "factors_1.5", "factors_4", "amin_0.05", "amin_0.2", "window_x0.5",
                               "window_x2", "cycles_5", "cycles_20"}
    assert S.spec("V0") == S.DEFAULT and S.spec("band_30_120")["band"] == (30.0, 120.0)
    assert S.window_of(120.0, 2.0) == (4.0, 2.0) and S.window_of(1.0, 0.5) == (0.1, 0.05)


def test_synthetic_set_is_seeded_and_covers_both_modes():
    a, b = S.synthetic_cases(), S.synthetic_cases()
    assert [c[0] for c in a] == [c[0] for c in b] and all(np.array_equal(x[2], y[2]) for x, y in zip(a, b))
    assert {c[1] for c in a} == {"N", "D"} and len({c[0] for c in a}) == len(a)


def test_classify_mode_d_amplitude_ladder_moves_with_amin():
    cases = {c[0]: c for c in S.synthetic_cases()}
    cid, mode, v, t_on, Ts = cases["D_burst40_amp0.15"]
    base = S.classify(v, mode, t_on, Ts[0], A_REF, "V0")
    low = S.classify(v, mode, t_on, Ts[0], A_REF, "amin_0.05")
    high = S.classify(v, mode, t_on, Ts[0], A_REF, "amin_0.2")
    assert base["cls"] == "D-none" and low["cls"] == "D-tr" and high["cls"] == "D-none"      # 0.15 between 0.109 and 0.218


def test_classify_reports_not_run_when_window_exceeds_record():
    v = np.random.default_rng(1).standard_normal(2000)
    r = S.classify(v, "D", 0.0, 120.0, A_REF, "window_x2")
    assert r["cls"] == "not_run"


def test_mode_n_strong_burst_survives_factor_4_and_weak_one_does_not():
    cases = {c[0]: c for c in S.synthetic_cases()}
    _, mode, v, t_on, Ts = cases["N_burst40_ratio6.0"]
    assert S.classify(v, mode, t_on, 120.0, A_REF, "factors_4")["cls"] != "NS"
    _, mode, v, t_on, Ts = cases["N_null"]
    assert S.classify(v, mode, t_on, 120.0, A_REF, "V0")["cls"] == "NS"


def test_reach_table_counts_cells_and_records_per_w():
    rows = [{"index": 0, "W_s": 2.0, "rho": 0.4}, {"index": 0, "W_s": 2.0, "rho": 0.55},
            {"index": 1, "W_s": 2.0, "rho": 0.8}, {"index": 1, "W_s": 2.0, "rho": 0.9},
            {"index": 2, "W_s": 0.2, "rho": 0.3}]
    t = {(r["W_s"], round(r["level"], 3)): r for r in S.reach_table(rows)}
    r = t[(2.0, 0.5)]
    assert r["n_cells"] == 2 and r["cells_mean_ge"] == 1 and r["cells_any_seed_ge"] == 2 and r["records_ge"] == 3
    assert t[(0.2, 0.25)]["records_ge"] == 1 and t[(0.2, 0.5)]["records_ge"] == 0
    assert {round(lv, 3) for lv in S.LEVELS} == {0.25, 0.333, 0.5, 0.667, 0.75}


def test_rho_variant_white_noise_and_window_multiplier():
    v = np.random.default_rng(2).standard_normal(5001)
    r1 = S.rho_variant(v, 120.0, S.DEFAULT["band"], 1.0)
    r2 = S.rho_variant(v, 120.0, S.DEFAULT["band"], 2.0)
    assert r1["n_windows"] == 4 and r2["n_windows"] == 1 and r2["W_s"] == 4.0
    assert abs(r1["rho"] - 0.5) < 0.05


def test_white_noise_counts_sum_to_draws_and_are_deterministic():
    a = S.whitenoise_classes(120.0, "V0", A_REF, 3)
    assert sum(a.values()) == 3 and a == S.whitenoise_classes(120.0, "V0", A_REF, 3)
    assert np.array_equal(S.white_record(0), S.white_record(0)) and not np.array_equal(S.white_record(0), S.white_record(1))


def test_run_kind_registered():
    assert "a8sens" in C.RUN_KINDS
