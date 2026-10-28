"""MS13 13d: tests of the first figure (F3, untagged draft) and of plan 13a rows 9 to 12. They read the stored results under results/ (git-ignored)
and skip if those are absent. Builds go to a temporary directory, never to figures/. Tolerances: every comparison is exact (SHA-256, set equality,
exact messages) except row 9's array comparison (rel 1e-12, plan section 8 row 9) and the quoted maximum frequency (abs 0.05 Hz, 73.7 against the
stored 73.692...)."""
import ast
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

from mprsurge import config as C
from mprsurge.plotting import figprov as F
from mprsurge.plotting import figures as FG

ROOT = C.repo_root()
RES = ROOT / "results"
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in FG.F3_INPUTS), reason="stored F3 inputs under results/ are absent")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("figs") / "F3"
    return FG.make_F3(out_dir=out), out


def test_row9_drawn_data_hash_is_equal_across_two_runs_of_the_data_step():
    # data step run twice in one process (not the plotting): exact SHA-256 of the drawn data, and every array equal at rel 1e-12
    a, b = FG.prepare_F3(FG.load_F3()), FG.prepare_F3(FG.load_F3())
    assert FG.drawn_data_sha256(a) == FG.drawn_data_sha256(b)
    assert sorted(a) == sorted(b)
    for k in a:
        if isinstance(a[k], np.ndarray):
            np.testing.assert_allclose(a[k], b[k], rtol=1e-12, atol=0, equal_nan=True)
    c = dict(a)
    c["f_max_hz"] = a["f_max_hz"] * (1 + 1e-9)
    assert FG.drawn_data_sha256(c) != FG.drawn_data_sha256(a)                  # the hash does see a changed value


def test_row10_make_FS6_is_refused_citing_ms12_c1_and_no_fig_FS6_script():
    with pytest.raises(F.FigureRefused, match="MS12-C1"):
        FG.make_FS6()
    assert not (ROOT / "scripts" / "fig_FS6.py").exists()


def test_row11_claim_limit_ids_appear_in_the_provenance_claim_limits(built):
    res, out = built
    prov = json.loads((out / "F3_provenance.json").read_text(encoding="utf-8"))
    assert set(prov["claim_limits"]) == set(FG.F3_PROPOSED_CLAIM_LIMITS)           # exact set equality
    caption = (out / "F3_caption.txt").read_text(encoding="utf-8")
    assert all(i in caption for i in FG.F3_PROPOSED_CLAIM_LIMITS)
    assert caption.startswith("F3. PROPOSED, not ruled:")                          # the take-home message is marked as a proposal
    assert prov["draft"] is True and prov["figure_id"] == "F3" and prov["criteria_sha256"] == F.K.verify_frozen_criteria()["sha256"]


def test_row12_readiness_registry_equals_the_declared_inputs_of_fig_F3():
    reg = _load(ROOT / "scripts" / "ms13_inputs.py", "ms13_inputs_for_test")
    script = _load(ROOT / "scripts" / "fig_F3.py", "fig_F3_for_test")
    registry = {e["path"] for e in reg.INPUTS["F3"]}
    assert all(e["kind"] == "file" for e in reg.INPUTS["F3"])
    assert registry == set(script.DECLARED_INPUTS) == set(FG.F3_INPUTS)           # exact set equality


def test_data_step_opens_only_paths_under_results_and_the_script_opens_nothing_itself():
    opened = []
    active = [False]

    def hook(event, args):
        if active[0] and event == "open":
            opened.append((str(args[0]), args[1]))

    sys.addaudithook(hook)
    active[0] = True
    try:
        FG.prepare_F3(FG.load_F3())
    finally:
        active[0] = False
    assert opened, "the audit hook saw no open"
    res = RES.resolve()
    for path, mode in opened:
        assert Path(path).resolve().is_relative_to(res), path                      # exact: every opened path is under results/
        assert not set(str(mode or "r")) & set("wax+"), (path, mode)               # and none is opened for writing
    tree = ast.parse((ROOT / "scripts" / "fig_F3.py").read_text(encoding="utf-8"))
    names = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not names & {"open", "load", "read_text", "read_csv", "read_parquet", "savez", "write_text"}      # the script only calls make_F3


def test_proposed_take_home_numbers_agree_with_the_stored_a6_arrays():
    d = FG.prepare_F3(FG.load_F3())
    first = {D: float(d[f"D{D}_tau_d_ms"][d[f"D{D}_c25_count"] > 0][0]) for D in FG.DELTAS}
    assert first == {"0.05": 3.0, "0.1": 5.0, "0.3": 13.0}                         # DL-131: 25 Hz contour from tau_d 3, 5, 13 ms
    assert list(d["D0.3_tau_d_ms"][d["D0.3_c25_count"] > 0]) == [13.0, 22.0, 36.0]
    assert d["c100_total_crossings"] == 0
    assert d["f_max_hz"] == pytest.approx(73.7, abs=0.05)
    assert [(r["rb_id"], r["check_id"], r["status"]) for r in d["strip"]] == [("RB9", "b_spectral_vs_cycle_headline", "FAIL")]


def test_build_hashes_and_params_agree_with_the_provenance(built):
    res, out = built
    prov = out / "F3_provenance.json"
    assert F.verify_figure_provenance(prov) == []                                  # exact SHA-256 of every recorded file
    assert F.check_params_against_provenance(out / "F3_params.csv", prov) == []
    text = (out / "F3_nordlie.md").read_text(encoding="utf-8")
    conn = text.split("## Connectivity", 1)[1].split("## ", 1)[0]
    assert "model.J" in conn                                                       # J sits under Connectivity (13d fix)
    assert (out / "F3.pdf").stat().st_size > 0 and (out / "F3.png").stat().st_size > 0
