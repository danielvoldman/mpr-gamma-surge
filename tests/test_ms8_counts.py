"""MS8 8a: run counts from the plan wording, the 9.2 arithmetic, the sample cells and the proposed seed keys (DL-166, DL-167).
Nothing integrates."""
import pytest

from mprsurge import config as C
from mprsurge.analysis import ms8_counts as M
from mprsurge.analysis import timing as T
from mprsurge.units import s_to_tau

from test_criteria_draft import _key_prefixes_in_repo


def test_t_ramp_grid_is_the_13_values_of_s2():
    g = M.t_ramp_grid()
    assert len(g) == 13 and g[0] == pytest.approx(1.0) and g[-1] == pytest.approx(1000.0) and g[8] == pytest.approx(100.0)
    assert g.sum() == pytest.approx(2283.6007, rel=1e-6)


@pytest.mark.parametrize("path,profile", [(p, pr) for p in M.PATHS for pr in M.PROFILES])
def test_duration_formulas_equal_make_path(path, profile):
    """5 + k T_ramp + 10 s with k = 1, 1.25, 2 (CP14) against ramps.make_path for the sample cells' resolved configs."""
    cell = {"path_eta": "p1", "path_hypoxia": "p2", "path_updown": "p5"}[path] + ("_lin" if profile == "linear" else "_sig") + "_t56"
    cfg = T.resolve_cell("configs/S5.yaml", "ms8_" + cell)
    assert (cfg["path"]["name"], cfg["path"]["profile"]) == (path, profile)
    assert T.tau_simulated(cfg) == pytest.approx(s_to_tau(M.run_integrated_s(path, cfg["path"]["T_ramp_s"])))


def test_default_counts_by_plan_wording():
    d = M.s5_mode_d_runs()
    s = M.summarise(d)
    assert s["S5_grid"]["runs"] == 3 * 13 * 2 and s["S5_start_distance"]["runs"] == 2 * 13 and s["S5_headline"]["runs"] == 1
    assert s["S5_grid"]["tau"] == pytest.approx(2058060.6, rel=1e-6)
    assert s["S5_headline"]["tau"] == pytest.approx(16500.0)
    n = M.s5_mode_n_runs()
    assert len(n) == 13 * 10
    # Table 9.1 counts 3.1e9 Heun steps for S2, S5, S6 together: 10 seeds x 13 T_ramp of P2 give 3.08e9 (arithmetic, ours)
    assert sum(M.heun_steps(r) for r in n) == pytest.approx(3.0755e9, rel=1e-4)
    s13 = M.summarise(M.s13_headline_runs())
    assert (s13["S13_rtol"]["runs"], s13["S13_delta0"]["runs"], s13["S13_radau"]["runs"], s13["S13_floor"]["runs"]) == (2, 2, 1, 3 * 4 * 10)


@pytest.mark.parametrize("opts,expect", [
    ({"noise_seeds_T_ramp": "headline_only"}, 10), ({"noise_seeds_T_ramp": "grid_both_profiles"}, 260)])
def test_noise_seed_readings(opts, expect):
    assert len(M.s5_mode_n_runs(opts)) == expect


def test_start_distance_and_floor_readings():
    assert M.summarise(M.s5_mode_d_runs({"start_distance_T_ramp": "headline_only"}))["S5_start_distance"]["runs"] == 2
    assert M.summarise(M.s5_mode_d_runs({"start_distance_profiles": "both"}))["S5_start_distance"]["runs"] == 52
    assert M.summarise(M.s13_headline_runs({"floor_design": "two_part"}))["S13_floor"]["runs"] == 3 * 10 + 3 * 10
    for k, v in M.OPTIONS.items():
        assert M.DEFAULTS[k] == v[0]


def test_sample_cells_resolve_and_stay_outside_the_cell_list():
    files = sorted(p.stem for p in (C.repo_root() / "configs" / "timing" / "ms8").glob("*.yaml"))
    assert files == sorted(M.SAMPLE_CELLS) and not set(files) & set(T.CELLS)
    for c in M.SAMPLE_CELLS:
        cfg = T.resolve_cell("configs/S5.yaml", c)
        assert cfg["path"]["eta_path_status"] == "A4"
    fine = T.resolve_cell("configs/S5.yaml", M.FLOOR_FINE_CELL)
    assert fine["run"]["kind"] == "mf_noisy" and fine["noise"]["dt_tau"] == 1.0e-4 and fine["noise"]["sigma"] == M.FLOOR_LEVELS[1]
    assert [T.resolve_cell("configs/S5.yaml", c)["solver"]["rtol"] for c in M.RTOL_CELLS.values()] == list(M.RTOL_CELLS)


def _cells(rate=0.01):
    cells = {}
    for name in M.SAMPLE_CELLS + M.EARLIER_CELLS:
        cfg = T.resolve_cell("configs/S5.yaml", name)
        tau = T.tau_simulated(cfg)
        cells[name] = {"wall_s": rate * tau, "tau": tau}
    return cells


def test_prediction_arithmetic():
    cells = _cells(0.01)
    rows = {r["id"]: r for r in M.predict(cells, 10)}
    d, s5 = M.s5_mode_d_runs(), rows["ms8_s5"]
    mf = sum(r["tau"] for r in d) * 0.01
    hn = sum(M.heun_steps(r) for r in M.s5_mode_n_runs()) * (0.01 * 16700 / (16700 / 1e-3))
    assert s5["sum_s"] == pytest.approx(mf + hn) and s5["prediction_s"] >= s5["sum_s"] / 10
    assert s5["longest_run_s"] == pytest.approx(201500 * 0.01)           # P5 at 1000 s, the longest run
    assert s5["verdict"] in ("PASS", "FAIL") and s5["limit_s"] == pytest.approx(1.5 * 0.95 * 3600)
    # a slower sample cell for P5 sigmoid is picked over the earlier cell
    cells["ms8_p5_sig_t56"]["wall_s"] *= 3
    assert M.slowest(cells, M.RATE_CELLS[("path_updown", "sigmoid")]) == "ms8_p5_sig_t56"


def test_part_over_one_hour_is_flagged():
    cells = _cells(0.01)
    cells["p5_1000"]["wall_s"] *= 100                 # absurdly slow P5 rate
    row = [r for r in M.predict(cells, 10) if r["id"] == "ms8_s5"][0]
    assert row["parts_over_one_hour"] and row["verdict"] == "FAIL"


def test_disk_and_memory_arithmetic():
    runs = M.s5_mode_d_runs()
    dk = M.disk_estimate(runs, 0.5)
    assert dk["files"] == 105 and dk["raw_bytes"] == pytest.approx(sum(M.kept_samples(r) for r in runs) * 64) and dk["bytes"] == dk["raw_bytes"] / 2
    me = M.memory_estimate(runs, 10, 200.0)
    assert me["largest_run_samples"] == 2015001 and me["per_run_peak_bytes"] == pytest.approx(2015001 * 200.0)


# --- seed keys (DL-166) ---------------------------------------------------------------------------

def test_proposed_ms8_seed_keys_collide_with_no_key_in_the_repo():
    """DL-141 convention: first element = milestone. No equal and no prefix relation with any key used by a config or written
    literally in src/scripts/tests (including [7, 9] and the calibration keys [0] to [9], compared by equality only)."""
    mine = M.proposed_seed_keys()
    assert len(mine) == 10 + 3 * 10 and len(set(mine)) == len(mine)
    used = _key_prefixes_in_repo()
    assert (7, 4) in used and (7, 6, 1) in used and (7, 8, 5, 1) in used
    calibration = {(s,) for s in range(10)}
    for m in mine:
        assert m[0] == 8 and len(m) >= 2 and m not in calibration
        for u in used:
            if len(u) == 1:
                continue                                  # runner seed index keys [s]: [7, ...] and [8, ...] sit under them by convention
            n = min(len(m), len(u))
            assert m[:n] != u[:n], (m, u)
    # the proposal's own prefixes are not each other's prefix, and [7, 9] (F-19) is not touched
    pre = list(M.SEED_KEY_PREFIXES.values())
    assert all(a[: min(len(a), len(b))] != b[: min(len(a), len(b))] for i, a in enumerate(pre) for b in pre[i + 1:])
    assert all(k[:2] != (7, 9) for k in mine)


def test_no_key_starting_with_8_is_used_outside_the_proposal():
    """A later literal use of an MS8 key that is not under a proposed prefix would be a new, unproposed key."""
    pre = set(M.SEED_KEY_PREFIXES.values())
    for u in _key_prefixes_in_repo():
        if len(u) >= 2 and u[0] == 8:
            assert any(u[: len(p)] == p for p in pre), u
