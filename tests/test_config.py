"""Configuration system (plan 10.3, Table 10.1; DL-054, DL-055, DL-057, DL-065)."""
import copy
import warnings

import pytest

from mprsurge import config as C
from mprsurge.params import PARAM_META, make_param_table, param_table_markdown


def resolve(run=None, *sets):
    return C.resolve_config(run, list(sets))


# --- base, types, unknown keys -------------------------------------------------

def test_base_resolves_to_ref_devalle():
    cfg = resolve()
    m = cfg["model"]
    assert (m["type"], m["eta_bar"], m["J"], m["Delta"], m["tau_d_ms"]) == ("M3", 4.0, -21.0, 0.3, 5.0)
    assert cfg["solver"]["rtol"] == 1e-10 and isinstance(cfg["solver"]["rtol"], float)
    assert cfg["seeds"]["root_seed"] == 20261008


def test_resolves_from_repo_root_not_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert resolve()["model"]["ref_point"] == "ref_devalle"


def test_unknown_key_and_section_raise():
    with pytest.raises(C.ConfigError, match="unknown key"):
        resolve({"model": {"nonsense": 1}})
    with pytest.raises(C.ConfigError, match="unknown section"):
        resolve({"bogus": {"a": 1}})
    with pytest.raises(C.ConfigError, match="unknown key"):
        resolve(None, "solver.rtl=1e-12")


def test_string_float_is_cast():
    # PyYAML (YAML 1.1) reads 1e-12 as a string; the schema casts it
    cfg = resolve(None, "solver.rtol=1e-12")
    assert cfg["solver"]["rtol"] == 1e-12 and isinstance(cfg["solver"]["rtol"], float)
    assert resolve({"solver": {"atol": "1e-14"}})["solver"]["atol"] == 1e-14


def test_bad_types_are_rejected():
    for sets in (["solver.rtol=abc"], ["solver.rtol=true"], ["network.N=1.5"],
                 ["network.exclude_refractory=maybe"], ["model.type=M9"],
                 ["solver.rtol=-1"], ["analysis.band_primary_hz=[100, 25]"]):
        with pytest.raises(C.ConfigError):
            resolve(None, *sets)
    with pytest.raises(C.ConfigError, match="null is not allowed"):
        resolve({"solver": {"rtol": None}})


def test_int_cast_from_float_string():
    assert resolve(None, "network.N=1e4")["network"]["N"] == 10000


def test_overrides_are_recorded():
    cfg = resolve(None, "solver.rtol=1e-12", "model.J=-20")
    rec = cfg["_resolved_from"]
    assert rec["overrides"] == {"solver.rtol": "1e-12", "model.J": -20}
    assert rec["base"] == "configs/base.yaml" and rec["run_file"] is None


def test_derived_keys_cannot_be_set():
    for k in ("path.eps=1", "path.eta_path_status=A4"):
        with pytest.raises(C.ConfigError, match="derived"):
            resolve(None, k)


# --- ref_point (DL-054) -----------------------------------------------------------

def test_explicit_override_wins_over_ref_point():
    cfg = resolve({"model": {"ref_point": "ref_mpr", "J": 14.0}})
    assert cfg["model"]["J"] == 14.0 and cfg["model"]["eta_bar"] == -5.0
    cfg = resolve({"model": {"ref_point": "ref_mpr"}}, "model.Delta=0.5")
    assert cfg["model"]["Delta"] == 0.5


def test_ref_point_replaces_base_values():
    m = resolve({"model": {"ref_point": "ref_mpr"}})["model"]
    assert (m["type"], m["eta_bar"], m["J"], m["Delta"], m["tau_d_ms"]) == ("M2", -5.0, 15.0, 1.0, None)


def test_ref_ceni_needs_explicit_tau_d_in_d11_range():
    with pytest.raises(C.ConfigError, match="tau_d_ms"):
        resolve({"model": {"ref_point": "ref_ceni"}})
    for bad in (0.5, 50.5):
        with pytest.raises(C.ConfigError, match="D11 range"):
            resolve({"model": {"ref_point": "ref_ceni", "tau_d_ms": bad}})
    for td in (3.0, 4.95, 8.0):  # the S3 set: no warning
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            m = resolve({"model": {"ref_point": "ref_ceni", "tau_d_ms": td}})["model"]
        assert (m["eta_bar"], m["J"], m["Delta"], m["tau_d_ms"]) == (1.0, -20.0, 0.05, td)


def test_ref_ceni_outside_s3_set_warns_not_errors():
    for td in (1.0, 6.0, 50.0):  # K10/A6 need values up to 50 ms
        with pytest.warns(UserWarning, match="DL-066"):
            m = resolve({"model": {"ref_point": "ref_ceni", "tau_d_ms": td}})["model"]
        assert m["tau_d_ms"] == td


def test_ref_point_null_keeps_base_values():
    m = resolve({"model": {"ref_point": None, "J": -30.0}})["model"]
    assert m["J"] == -30.0 and m["eta_bar"] == 4.0


# --- eta path (D12, DL-065) ----------------------------------------------------------

def test_eta_path_unresolved_by_default():
    p = resolve()["path"]
    assert p["eta_start"] is None and p["eta_peak"] is None and p["eps"] is None
    assert p["eta_path_status"] == "unresolved"
    with pytest.raises(C.ConfigError, match="unresolved"):
        C.require_eta_path(resolve())


def test_eta_path_from_eta_H_follows_d12():
    # fixture values only: arbitrary numbers to test the formulas, not Hopf values
    p = resolve(None, "path.eta_H=1.0")["path"]
    assert (p["eta_start"], p["eta_peak"], p["eta_path_status"]) == (-0.5, 4.0, "A4")
    p = resolve(None, "path.eta_H=3.0")["path"]
    assert (p["eta_start"], p["eta_peak"]) == (1.5, 5.0)
    C.require_eta_path(resolve(None, "path.eta_H=3.0"))


def test_explicit_eta_path_is_provisional_and_gives_eps():
    cfg = resolve(None, "path.eta_start=0", "path.eta_peak=6", "path.T_ramp_s=60")
    p = cfg["path"]
    assert p["eta_path_status"] == "provisional"
    assert p["eps"] == pytest.approx(6.0 / 6000.0, rel=1e-12)  # 60 s = 6000 tau
    C.require_eta_path(cfg)


def test_explicit_eta_path_on_m2_is_explicit_not_provisional():
    cfg = resolve({"model": {"ref_point": "ref_mpr"}}, "path.eta_start=-6", "path.eta_peak=2")
    assert cfg["path"]["eta_path_status"] == "explicit"
    C.require_eta_path(cfg)
    m3 = resolve(None, "path.eta_start=-6", "path.eta_peak=2")
    assert m3["path"]["eta_path_status"] == "provisional"
    assert C.config_hash(cfg) != C.config_hash(m3)


def test_eta_path_inconsistent_inputs_raise():
    with pytest.raises(C.ConfigError, match="together"):
        resolve(None, "path.eta_start=0")
    with pytest.raises(C.ConfigError, match="not both"):
        resolve(None, "path.eta_H=1", "path.eta_start=0", "path.eta_peak=5")


# --- hash (10.3, DL-057) ------------------------------------------------------------------

def test_hash_is_sha256_and_short_hash_is_12_hex():
    h = C.config_hash(resolve())
    assert len(h) == 64 and int(h, 16) >= 0
    assert C.short_hash(h) == h[:12] and len(C.short_hash(h)) == 12


def test_hash_independent_of_key_order():
    a = {"model": {"J": -20.0, "Delta": 0.2}, "solver": {"rtol": 1e-9, "atol": 1e-11}}
    b = {"solver": {"atol": 1e-11, "rtol": 1e-9}, "model": {"Delta": 0.2, "J": -20.0}}
    assert C.config_hash(resolve(a)) == C.config_hash(resolve(b))


def test_hash_independent_of_workers_paths_and_analysis():
    h0 = C.config_hash(resolve())
    for s in ("run.workers=6", "output.dir=elsewhere/out", "run.id=S5",
              "replication.tolerances_file=configs/x.yaml", "run.wall_limit_s=100",
              "analysis.rel_factor=4", "seeds.n_seeds=3", "sweep.x_name=J"):
        assert C.config_hash(resolve(None, s)) == h0, s


def test_hash_changes_with_integration_inputs():
    h0 = C.config_hash(resolve())
    for s in ("model.J=-20", "solver.rtol=1e-8", "path.T_ramp_s=60", "noise.dt_tau=5e-4",
              "durations.hold_s=11", "seeds.root_seed=1", "run.kind=mf_noisy",
              "path.eta_start=0", "network.N=1000"):
        extra = ["path.eta_peak=5"] if s == "path.eta_start=0" else []
        assert C.config_hash(resolve(None, s, *extra)) != h0, s


def test_hash_includes_spawn_key_and_path_status():
    cfg = resolve()
    cfg2 = copy.deepcopy(cfg)
    cfg2["seeds"]["spawn_key"] = [3]
    assert C.config_hash(cfg) != C.config_hash(cfg2)
    prov = resolve(None, "path.eta_start=0", "path.eta_peak=5")
    a4 = resolve(None, "path.eta_H=2", "path.eta_start=null")
    assert prov["path"]["eta_start"] == 0.0
    assert C.config_hash(prov) != C.config_hash(a4)


def test_canonical_json_is_stable():
    assert C.canonical_json({"b": 1, "a": [1.5, None]}) == '{"a":[1.5,null],"b":1}'


# --- parameter table (DL-059) ---------------------------------------------------------------

def test_param_table_lists_every_resolved_key():
    cfg = resolve()
    rows = make_param_table(cfg)
    keys = {r["key"] for r in rows}
    expected = {f"{s}.{k}" for s, body in C.SCHEMA.items() for k in body}
    assert keys == expected
    assert all(set(r) == {"name", "key", "value", "units", "status"} for r in rows)
    assert expected <= set(PARAM_META)
    md = param_table_markdown(rows)
    assert md.startswith("| Name | Key |") and "model.tau_ms" in md
