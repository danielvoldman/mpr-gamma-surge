"""Seeds, run records, atomic writes, skip-if-done (plan 6.6, 10.4, Table 10.1; DL-056)."""
import json
import re

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import provenance as P


@pytest.fixture(scope="module")
def env():
    return P.environment_info()


def make_record(cfg, env, **kw):
    return P.make_run_record(cfg, env, name=kw.pop("name", "T_0000_x"),
                             status=kw.pop("status", "ok"), **kw)


# --- seeds -----------------------------------------------------------------------

def test_seed_children_have_spawn_keys_and_rebuild_exactly():
    kids = P.seed_sequence(20261008, 4)
    assert [k.spawn_key for k in kids] == [(0,), (1,), (2,), (3,)]
    rebuilt = P.seed_from_key(20261008, (2,))
    a = np.random.default_rng(kids[2]).random(5)
    b = np.random.default_rng(rebuilt).random(5)
    assert np.array_equal(a, b)
    c = np.random.default_rng(kids[3]).random(5)
    assert not np.array_equal(a, c)


# --- hashing and atomic writes ------------------------------------------------------

def test_sha256_file_known_value(tmp_path):
    f = tmp_path / "abc.txt"
    f.write_bytes(b"abc")
    assert P.sha256_file(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_atomic_write_replaces_and_leaves_no_tmp(tmp_path):
    f = tmp_path / "sub" / "x.json"
    P.atomic_write_json(f, {"a": 1})
    P.atomic_write_json(f, {"a": 2})
    assert json.loads(f.read_text()) == {"a": 2}
    assert [p.name for p in f.parent.iterdir()] == ["x.json"]


def test_atomic_save_npz_roundtrip(tmp_path):
    f = tmp_path / "r.npz"
    P.atomic_save_npz(f, {"v": np.arange(4.0)})
    with np.load(f) as z:
        assert np.array_equal(z["v"], np.arange(4.0))


def test_replace_is_retried_on_permission_error(tmp_path, monkeypatch):
    real, calls = P.os.replace, {"n": 0}

    def flaky(src, dst):
        calls["n"] += 1
        if calls["n"] < 3:
            raise PermissionError("locked")
        return real(src, dst)

    monkeypatch.setattr(P.os, "replace", flaky)
    f = tmp_path / "x.txt"
    P.atomic_write_text(f, "ok", delay_s=0.001)
    assert f.read_text() == "ok" and calls["n"] == 3


def test_replace_gives_up_and_cleans_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(P.os, "replace", lambda s, d: (_ for _ in ()).throw(PermissionError("x")))
    with pytest.raises(PermissionError):
        P.atomic_write_text(tmp_path / "x.txt", "ok", attempts=3, delay_s=0.001)
    assert list(tmp_path.iterdir()) == []


# --- records -------------------------------------------------------------------------

def test_git_info_in_repo():
    g = P.git_info()
    assert re.fullmatch(r"[0-9a-f]{40}", g["commit"])
    assert isinstance(g["tags"], list) and isinstance(g["dirty"], bool)
    assert g["branch"]


def test_run_record_has_all_fields(env):
    cfg = C.resolve_config()
    rec = make_record(cfg, env, wall_time_s=1.5, warnings=["w"], flags={"retried_with_radau": False})
    assert set(P.RECORD_FIELDS) <= set(rec)
    assert rec["config_hash"] == C.config_hash(cfg) and rec["config_hash12"] == rec["config_hash"][:12]
    assert rec["config"]["_resolved_from"]["overrides"] == {}
    assert rec["seed"] == {"root_seed": 20261008, "spawn_key": None}
    assert re.fullmatch(r"[0-9a-f]{40}", rec["git"]["commit"])
    assert rec["python"]["version"].startswith("3.11") and rec["packages"]["numpy"]
    assert set(rec["julia"]) == {"version", "bifurcationkit"}
    assert rec["os"] and rec["cpu"]["count"] and rec["solver"]["method"] == "DOP853"
    assert rec["solver"]["noise"]["scheme"] == "Heun"
    json.dumps(rec, allow_nan=False)  # serialisable, no NaN


def test_overrides_reach_the_record(env):
    cfg = C.resolve_config(None, ["solver.rtol=1e-12"])
    assert make_record(cfg, env)["config"]["_resolved_from"]["overrides"] == {"solver.rtol": "1e-12"}


def test_status_values(env):
    cfg = C.resolve_config()
    for s in ("ok", "failed", "timeout"):
        assert make_record(cfg, env, status=s)["status"] == s
    with pytest.raises(ValueError):
        make_record(cfg, env, status="dry_run")           # only with dry_run=True
    assert make_record(cfg, env, status="dry_run", dry_run=True)["dry_run"] is True
    with pytest.raises(ValueError):
        make_record(cfg, env, status="ok", dry_run=True)


def test_criteria_hash_recorded(env, tmp_path):
    f = tmp_path / "crit.yaml"
    f.write_text("a: 1\n")
    cfg = C.resolve_config(None, [f"robustness.criteria_file={f.as_posix()}"])
    assert make_record(cfg, env)["criteria_sha256"] == P.sha256_file(f)


# --- skip-if-done ----------------------------------------------------------------------

def write_result(out, cfg, env, name="T_0000", status="ok"):
    h12 = C.short_hash(C.config_hash(cfg))
    stem = f"{name}_{h12}"
    outputs = {}
    if status == "ok":
        P.atomic_save_npz(out / f"{stem}.npz", {"v": np.arange(3.0)})
        outputs = {f"{stem}.npz": P.sha256_file(out / f"{stem}.npz")}
    P.write_run_record(make_record(cfg, env, name=stem, status=status, outputs=outputs),
                       out / f"{stem}.json")
    return stem


def test_find_complete_cases(tmp_path, env):
    cfg = C.resolve_config()
    assert P.find_complete(tmp_path, cfg) is None
    stem = write_result(tmp_path, cfg, env)
    assert P.find_complete(tmp_path, cfg) == tmp_path / f"{stem}.json"
    other = C.resolve_config(None, ["model.J=-20"])
    assert P.find_complete(tmp_path, other) is None


def test_failed_timeout_and_dry_records_are_not_complete(tmp_path, env):
    cfg = C.resolve_config()
    for status in ("failed", "timeout"):
        write_result(tmp_path, cfg, env, status=status)
        assert P.find_complete(tmp_path, cfg) is None
    h12 = C.short_hash(C.config_hash(cfg))
    P.write_run_record(make_record(cfg, env, status="dry_run", dry_run=True),
                       tmp_path / f"T_{h12}.dry.json")
    assert P.find_complete(tmp_path, cfg) is None


def test_altered_or_missing_output_is_not_complete(tmp_path, env):
    cfg = C.resolve_config()
    stem = write_result(tmp_path, cfg, env)
    (tmp_path / f"{stem}.npz").write_bytes(b"tampered")
    assert P.find_complete(tmp_path, cfg) is None
    (tmp_path / f"{stem}.npz").unlink()
    assert P.find_complete(tmp_path, cfg) is None


def test_full_hash_mismatch_with_same_hash12_raises(tmp_path, env):
    cfg = C.resolve_config()
    stem = write_result(tmp_path, cfg, env)
    path = tmp_path / f"{stem}.json"
    rec = P.read_run_record(path)
    rec["config_hash"] = rec["config_hash12"] + "0" * 52
    path.write_text(json.dumps(rec))
    with pytest.raises(P.ProvenanceError):
        P.find_complete(tmp_path, cfg)
