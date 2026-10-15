"""A0 (MS2 step 2e, DL-091): refusals, hash coverage, row logic and the csv. Fast; reads results/ for the real inputs."""
import shutil

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import replication as RP


def test_a0_kind_hash_covers_frozen_hash_and_upstream_results(upstream_results, tmp_path, monkeypatch):
    assert "a0" in C.RUN_KINDS
    cfg = C.resolve_config(C.repo_root() / "configs/A0.yaml", {})
    view = C.hash_view(cfg)["a0"]
    assert view["frozen_sha256"] == RP.FROZEN_SHA256 and set(view["upstream_sha256"]) == set(RP.UPSTREAM)
    assert all(len(v) == 64 for v in view["upstream_sha256"].values())
    h = C.config_hash(cfg)
    copies = {n: tmp_path / f"{n}.npz" for n in RP.UPSTREAM}
    for n, f in copies.items():
        f.write_bytes(RP.upstream_npz(n).read_bytes())
    monkeypatch.setattr(RP, "upstream_npz", lambda n: copies[n])
    assert C.config_hash(cfg) == h
    for f in copies.values():
        f.write_bytes(f.read_bytes() + b"\0")
        assert C.config_hash(cfg) != h
        f.write_bytes(f.read_bytes()[:-1])
    monkeypatch.setattr(RP, "FROZEN_SHA256", "0" * 64)
    assert C.config_hash(cfg) != h
    assert "a0" not in C.hash_view(C.resolve_config(C.repo_root() / "configs/A2.yaml", {}))


def test_a0_refuses_a_replication_yaml_that_differs_from_the_frozen_hash(upstream_results, monkeypatch):
    cfg = C.resolve_config(C.repo_root() / "configs/A0.yaml", {})
    monkeypatch.setattr(RP, "FROZEN_SHA256", "0" * 64)
    with pytest.raises(P.ProvenanceError, match="frozen"):
        RP.run_a0(cfg)


@pytest.mark.parametrize("victim", ["A1", "A2", "S1_K4", "S1_K5"])
def test_a0_refuses_an_upstream_file_that_differs_from_its_run_record(upstream_results, tmp_path, monkeypatch, victim):
    for d in ("A1", "A2", "S1"):
        shutil.copytree(C.repo_root() / "results" / d, tmp_path / d)
    real = RP._plan
    monkeypatch.setattr(RP, "_plan", lambda path, sets: real(path, [*sets, f"output.dir={tmp_path.as_posix()}"]))
    for n in RP.UPSTREAM:
        RP.verified_upstream(n)                                    # the copies are intact
    npz, _ = RP.verified_upstream(victim)
    npz.write_bytes(npz.read_bytes() + b"\0")
    with pytest.raises(P.ProvenanceError, match="does not match its run record"):
        RP.verified_upstream(victim)


def test_k5_check_passes_a_periodic_burst_train_and_fails_a_missing_burst_or_drift():
    t = np.arange(0, 280.0001, 0.1)
    r = 0.5 + 0.4 * np.sin(2 * np.pi * (t - 7.0) / 40.0)
    assert RP.k5_check(t, r, 0.5, 40.0, 2, 5, 0.1)["pass"]
    r2 = r.copy()
    r2[(t >= 160) & (t < 190)] = 0.0                               # one burst missing in a checked period
    assert not RP.k5_check(t, r2, 0.5, 40.0, 2, 5, 0.1)["pass"]
    r3 = 0.5 + 0.4 * np.sin(2 * np.pi * (t - 7.0) / 40.3)
    assert not RP.k5_check(t, r3, 0.5, 40.0, 2, 5, 0.1)["pass"]    # period 40.3 against 40 +- 0.1


def test_a0_csv_has_one_row_per_target_with_the_columns_and_unverified_flags(a0_result):
    plan = R.build_plan("configs/A0.yaml")
    rec = P.find_complete(plan.out_dir, plan.cells[0]["cfg"])
    assert rec is not None, "run scripts/run_A0.py"
    with np.load(rec.with_suffix(".npz")) as z:
        text = RP.csv_text({k: z[k] for k in z.files})
    lines = text.splitlines()
    assert lines[0] == "target,measured,tolerance,pass,source_results,unverified" and len(lines) == 6
    assert [l.split(",")[0] for l in lines[1:]] == ["K1", "K2", "K3", "K4-MF", "K5"]
    assert set(RP.UNVERIFIED) == {"K1", "K2", "K3", "K4-MF", "K5"} and all(RP.UNVERIFIED.values())
    assert "DL-082" in text and "DL-089" in text and "DL-085" in text


def test_k5_forcing_must_match_the_yaml(upstream_results):
    import yaml
    rep = yaml.safe_load((C.repo_root() / "configs/replication.yaml").read_text(encoding="utf-8"))
    _, rec = RP.verified_upstream("S1_K5")
    path = {**rec["config"]["path"], "tau_ms": rec["config"]["model"]["tau_ms"]}
    RP.check_k5_forcing(rep["K5"], path)
    for key, val in (("I_amp", 2.0), ("I_period_s", 0.5), ("name", "I_step")):
        with pytest.raises(P.ProvenanceError, match="K5"):
            RP.check_k5_forcing(rep["K5"], {**path, key: val})
