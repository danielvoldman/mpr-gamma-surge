"""7h draft criteria file (DL-156): complete, labelled, still a draft. Reads configs only; no run, no results/ dependence."""
import re

import pytest
import yaml

from mprsurge import config as C

STATUSES = {"logged", "UNVERIFIED", "open"}


@pytest.fixture(scope="module")
def crit():
    return yaml.safe_load((C.repo_root() / "configs/robustness_criteria.yaml").read_text(encoding="utf8"))


def _leaves(node, path=()):
    """Every mapping that carries a `status` key, with its path."""
    if isinstance(node, dict):
        if "status" in node:
            yield path, node
        else:
            for k, v in node.items():
                yield from _leaves(v, path + (k,))


def test_draft_not_frozen(crit):
    m = crit["meta"]
    assert m["draft"] is True and m["frozen"] is False
    assert m["freeze_sha256"] is None and m["freeze_tag"] is None


def test_every_table_7_2_row_and_gate_present(crit):
    assert set(crit["robustness"]) == {f"RB{i}" for i in range(1, 11)}
    assert set(crit["gates"]) == {"G5", "G6", "G7"}


def test_every_leaf_carries_a_known_status(crit):
    leaves = list(_leaves(crit))
    assert len(leaves) > 80
    for path, leaf in leaves:
        assert leaf["status"] in STATUSES, path
        assert leaf.get("source") or leaf["status"] == "open", path


def test_open_values_name_a_sheet_row_and_hold_no_number(crit):
    for path, leaf in _leaves(crit):
        if leaf["status"] == "open":
            assert leaf.get("sheet"), path
            assert leaf.get("value") is None or isinstance(leaf["value"], str), path


def test_unverified_values_say_where_they_come_from(crit):
    for path, leaf in _leaves(crit):
        if leaf["status"] == "UNVERIFIED":
            assert leaf.get("source"), path


def test_plan_numbers_unchanged(crit):
    r, g = crit["robustness"], crit["gates"]
    assert r["RB1"]["f_pk_rel_tol"]["value"] == 0.05
    assert r["RB2"]["noisy_subgrid_agreement_min"]["value"] == 0.90
    assert r["RB4"]["one_at_a_time_runs"]["value"] == 14 and r["RB4"]["one_at_a_time_max_class_changes"]["value"] == 2
    assert r["RB4"]["latin_hypercube_points"]["value"] == 64 and r["RB4"]["latin_hypercube_min_class_unchanged"]["value"] == 0.80
    assert r["RB6"]["heun_delay_change_max"]["value"] == 0.05
    assert r["RB9"]["c_band_30_120_max_cell_class_change"]["value"] == 0.05
    assert r["RB10"]["max_map_cell_class_change"]["value"] == 0.10
    assert g["G5"]["surge_class_min_fraction_of_map1_cells"]["value"] == 0.03
    assert r["RB3"]["c_T_ramp_s"]["value"] == [56.23, 100.0, 177.8, 316.2]


def test_d43_values_agree_with_s13_and_a4_grid(crit):
    s13 = yaml.safe_load((C.repo_root() / "configs/S13.yaml").read_text(encoding="utf8"))["ruled_by_owner_7g"]
    d = crit["d43_and_numerics"]
    assert d["sigma_floor_levels"]["value"] == s13["d43_floor_levels_sigma_floor"]
    assert d["solver_floor_noise_free_v"]["value"] == s13["solver_floor_noise_free_v"]
    assert d["a4_eta_bar_grid_step"]["value"] == s13["a4_eta_bar_grid_step"]
    assert crit["robustness"]["RB6"]["heun_dt_ladder_tau"]["value"] == s13["heun_dt_ladder_tau"]
    assert d["std_v_over_sigma_at_start"]["value"] == s13["d43_std_v_over_sigma_at_start_state"]


def test_classifier_defaults_agree_with_base_yaml(crit):
    base = yaml.safe_load((C.repo_root() / "configs/base.yaml").read_text(encoding="utf8"))
    a, c = base["analysis"], crit["classifier"]
    assert c["band_primary_hz"]["value"] == a["band_primary_hz"]
    assert c["total_band_hz"]["value"] == a["total_band_hz"]
    assert c["rel_factor"]["value"] == a["rel_factor"] and c["abs_factor"]["value"] == a["abs_factor"]
    assert c["amin_factor"]["value"] == a["amin_factor"] and c["min_cycles"]["value"] == a["min_cycles"]
    assert c["collapse_r_frac"]["value"] == a["collapse_r_frac"]
    assert c["sigma"]["value"] == base["noise"]["sigma"]


def test_a_ref_threshold_is_a_tenth_of_a_ref(crit):
    a = crit["classifier"]["a_ref"]
    assert abs(a["threshold_abs"]["value"] - 0.1 * a["value"]) < 1e-5
    assert "5.5114" not in str(a["value"])        # the literal peak-to-peak is an alternate only


def test_d8_choice_a_with_known_limitation(crit):
    d8 = crit["classifier"]["d8_estimator"]
    assert d8["choice"] == "A"
    assert "DL-137" in d8["known_limitation"]["source"] and "DL-155" in d8["known_limitation"]["source"]
    assert re.search(r"2 SE", d8["value"])


def test_no_config_points_at_the_draft_yet():
    """Repointing is a sheet row (H-2): run_a4 reads the K tolerances from robustness.criteria_file (A4 keeps replication.yaml);
    S5 inherits null from base.yaml."""
    a4 = yaml.safe_load((C.repo_root() / "configs/A4.yaml").read_text(encoding="utf8"))
    assert a4["robustness"]["criteria_file"] == "configs/replication.yaml"
    for p in sorted((C.repo_root() / "configs").glob("*.yaml")):
        if p.name != "robustness_criteria.yaml":
            assert "criteria_file: configs/robustness_criteria.yaml" not in p.read_text(encoding="utf8"), p.name


def test_open_rows_after_dl158_only_m4_is_open(crit):
    """After the 7h rulings (DL-157) only three leaves are still open: the RB1 'not larger' tolerance, the RB4 Latin hypercube spawn
    key, and the M4 criteria (deferred by ruling). Each is open because no source or ruling gives it; no number was invented."""
    assert crit["meta"]["decision_log_through"] == "DL-158"
    opened = {".".join(path) for path, leaf in _leaves(crit) if leaf["status"] == "open"}
    assert opened == {"robustness.RB8.M4_criteria"}
    for path, leaf in _leaves(crit):
        if ".".join(path) in opened:
            assert leaf["value"] is None or isinstance(leaf["value"], str)


def test_rulings_o10_o11_o12_and_gate_wording_recorded(crit):
    c = crit["classifier"]["mode_n_conventions"]
    assert set(c) == {k for k in c if k[0] == "O"} and len(c) == 16
    assert "share a flagged window" in c["O10_episode_and_s_plus"]["value"]
    assert "outside G" in c["O11_s_abs_broadband"]["value"] and "no new threshold" in c["O11_s_abs_broadband"]["value"]
    assert "not a criterion" in c["O12_post_surge_rate"]["value"]
    assert "documented xfail" in crit["classifier"]["d8_estimator"]["gate_wording"]["value"]
    assert crit["meta"]["frozen"] is False and crit["meta"]["freeze_sha256"] is None


def _key_prefixes_in_repo():
    """Every spawn key (or prefix) used by a config or written literally in src/, scripts/ or tests/ (calibration keys
    [0] to [9] included, as the runner gives seed index s the key [s])."""
    root = C.repo_root()
    keys = set()
    for p in sorted((root / "configs").rglob("*.yaml")):
        d = yaml.safe_load(p.read_text(encoding="utf8")) or {}
        k = (d.get("seeds") or {}).get("spawn_key") if isinstance(d, dict) else None
        if k:
            keys.add(tuple(k))
    pat = re.compile(r"(?:spawn_key\s*=\s*|rng_for\s*)\(\s*(\d+(?:\s*,\s*\d+)*)")
    for sub in ("src", "scripts", "tests"):
        for p in (root / sub).rglob("*.py"):
            if p.name == "test_criteria_draft.py":
                continue
            for m in pat.finditer(p.read_text(encoding="utf8")):
                keys.add(tuple(int(x) for x in m.group(1).replace(" ", "").split(",")))
    return keys


def test_latin_hypercube_spawn_key_collides_with_no_key_in_the_repo(crit):
    seed = crit["robustness"]["RB4"]["latin_hypercube_seed"]["value"]
    assert seed["root_seed"] == 20261008 and seed["spawn_key_prefix"] == [7, 9]
    used = _key_prefixes_in_repo()
    calibration = {(s,) for s in range(10)}      # the runner's seed index keys; [7, 4, s] already sits under [7] (DL-141)
    assert (7, 4) in used and (7, 6, 1) in used and (7, 8, 5, 1) in used       # the scan sees the known keys
    mine = [tuple(seed["spawn_key_prefix"]), (7, 9, 0)] + [(7, 9, 1, k) for k in range(64)]
    for m in mine:
        assert m not in calibration
        for u in used:
            n = min(len(m), len(u))
            assert m[:n] != u[:n], (m, u)                       # equal, or one a prefix of the other, would share a stream
