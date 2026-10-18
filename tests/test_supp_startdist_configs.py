"""8f4 (DL-194): the supplementary configs are the headline config with only path.start_distance set (M-7)."""
import math

from mprsurge import config as C
from mprsurge import run as R

HEAD_H12 = "240de3ef73be"


def _strip(cfg):
    cfg = {k: v for k, v in cfg.items() if k != "_resolved_from"}
    return cfg


def test_headline_hash_unchanged():
    assert R.build_plan("configs/S5_ramp.yaml").cells[0]["hash12"] == HEAD_H12


def test_only_start_distance_differs():
    head = R.build_plan("configs/S5_ramp.yaml").cells[0]["cfg"]
    for f, d in (("d0p5", 0.5), ("d3", 3.0)):
        c = R.build_plan(f"configs/ms8/supp_startdist_headline_{f}.yaml").cells[0]
        cfg = c["cfg"]
        assert c["hash12"] != HEAD_H12
        assert cfg["path"]["start_distance"] == d
        assert math.isclose(cfg["path"]["eta_H"] - cfg["path"]["eta_start"], d, abs_tol=1e-12)
        diff = {k for k in cfg["path"] if cfg["path"][k] != head["path"].get(k)}
        assert diff <= {"start_distance", "eta_start", "eps", "status"}
        for sec in cfg:
            if sec not in ("path", "run", "_resolved_from"):
                assert cfg[sec] == head[sec], sec
