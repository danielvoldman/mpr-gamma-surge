"""MS15a 19 (DL-738 D3, DL-739): the DRAFT flag of the journal export. A journal build with the release option from a clean tree records draft = false; without it, or on a
dirty tree, never. The supplement text follows the flag. Stand-ins only: no figure is built here, no result file is read, no tag is made. Every comparison is exact
(booleans, strings, exit codes); no tolerance is involved."""
import importlib.util
import inspect
import json
import types
from pathlib import Path

import pytest

from mprsurge import config as C
from mprsurge.plotting import figprov as F
from mprsurge.plotting import figures as FG
from mprsurge.plotting import journal as J

ROOT = C.repo_root()


def _load_fig_journal():
    spec = importlib.util.spec_from_file_location("fig_journal_under_test", ROOT / "scripts" / "fig_journal.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def script(monkeypatch):
    """fig_journal with make_F6, the clean-tree check and the manifest writer replaced by recorders; returns (module, calls)."""
    m = _load_fig_journal()
    calls: list = []

    def fake_make(*, mode, root, tag_build=False):
        calls.append(("make", mode, tag_build))
        return {"timing_s": {"total_s": 0.0}, "drawn_sha256": "0" * 64, "prov": {"draft": not tag_build, "git": {}}, "paths": []}

    monkeypatch.setattr(FG, "make_F6", fake_make)
    monkeypatch.setattr(m.journal, "write_export_manifest", lambda base: calls.append(("manifest",)) or "manifest")
    return m, calls


def _fake_subprocess(calls, returncode):
    def run(cmd, *a, **k):
        calls.append(("check", Path(cmd[1]).name))
        return types.SimpleNamespace(returncode=returncode)
    return types.SimpleNamespace(run=run)


def test_journal_script_default_is_a_draft_build_without_a_tree_check(script, monkeypatch, capsys):
    m, calls = script
    monkeypatch.setattr(m, "subprocess", _fake_subprocess(calls, 0))
    assert m.main(["F6"]) == 0
    assert calls == [("make", "journal", False), ("manifest",)]                      # exact: tag_build False, no check_clean_tree call
    assert json.loads(capsys.readouterr().out.split("export manifest:")[0])["draft"] is True


@pytest.mark.parametrize("option", ["--release", "--tag"])
def test_journal_script_release_checks_the_tree_first_and_passes_tag_build(script, monkeypatch, capsys, option):
    m, calls = script
    monkeypatch.setattr(m, "subprocess", _fake_subprocess(calls, 0))
    assert m.main([option, "F6"]) == 0
    assert calls == [("check", "check_clean_tree.py"), ("make", "journal", True), ("manifest",)]      # exact order: the check, then the build with tag_build True
    assert json.loads(capsys.readouterr().out.split("export manifest:")[0])["draft"] is False


def test_journal_script_release_on_a_dirty_tree_builds_nothing(script, monkeypatch):
    m, calls = script
    monkeypatch.setattr(m, "subprocess", _fake_subprocess(calls, 1))
    assert m.main(["--release", "F6"]) == 1                                          # exact: the exit code of the check is returned
    assert calls == [("check", "check_clean_tree.py")]                               # no make call, no manifest


def _record(path: Path) -> Path:
    r = {"name": "stand_in_0000_aaaaaaaaaaaa", "status": "ok", "config_hash12": "aaaaaaaaaaaa", "seed": {"root_seed": 7, "spawn_key": [0, 1]},
         "git": {"commit": "0" * 40, "dirty": False}, "criteria_sha256": None,
         "solver": {"method": "DOP853", "rtol": 1e-10}, "config": {"solver": {"method": "DOP853", "rtol": 1e-10}, "network": {"N": 10000}}}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(r), encoding="utf-8")
    return path


@pytest.mark.parametrize("dirty, tag_build, draft", [(False, False, True), (True, False, True), (False, True, False)])
def test_provenance_draft_is_false_only_for_a_clean_tagged_build(tmp_path, monkeypatch, dirty, tag_build, draft):
    monkeypatch.setattr(F, "dirty_lines", lambda root=None: ["?? stray.txt"] if dirty else [])
    rec = _record(tmp_path / "results" / "A0" / "rec.json")
    scr = tmp_path / "fig_STAND.py"
    scr.write_text("# stand-in\n", encoding="utf-8")
    out = tmp_path / "figures" / "F3"
    prov = F.write_figure_provenance("F3", script=scr, inputs=[rec], params_rows=[], out_dir=out, root=ROOT, tag_build=tag_build)
    assert prov["draft"] is draft and prov["git"]["dirty"] is dirty
    assert json.loads((out / "F3_provenance.json").read_text(encoding="utf-8"))["draft"] is draft


def test_provenance_dirty_tree_with_tag_build_raises_and_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(F, "dirty_lines", lambda root=None: [" M src/x.py"])
    rec = _record(tmp_path / "results" / "A0" / "rec.json")
    scr = tmp_path / "fig_STAND.py"
    scr.write_text("# stand-in\n", encoding="utf-8")
    out = tmp_path / "figures" / "F3"
    with pytest.raises(F.DirtyTreeError):
        F.write_figure_provenance("F3", script=scr, inputs=[rec], params_rows=[], out_dir=out, root=ROOT, tag_build=True)
    assert not out.exists()                                                          # exact: nothing written, so a dirty tree can never record draft = false


def _supplement_first_line(tmp_path, **kw) -> str:
    p = tmp_path / "F9_supplement.md"
    J.write_supplement(p, "F9", strip_rows=[], strip_heading="h", footer="f", provenance_text="p", pointers=[], parameter_table="t", **kw)
    return p.read_text(encoding="utf-8").splitlines()[0]


def test_supplement_first_line_follows_the_flag(tmp_path):
    assert _supplement_first_line(tmp_path, draft=False) == "# F9 supplement sheet (journal export; draft = false)"
    assert _supplement_first_line(tmp_path, draft=True) == "# F9 supplement sheet (journal export; draft = true)"
    assert _supplement_first_line(tmp_path) == "# F9 supplement sheet (journal export; draft = true)"      # the default is the old text, byte for byte


def test_build_kind_wording():
    assert J.build_kind(True) == "untagged"                                          # the old word, so a draft build writes the old text
    assert J.build_kind(False) == "release build, tags placed after the build"


def test_journal_tail_has_no_fixed_draft_or_untagged_text():
    tail = inspect.getsource(FG._journal_tail)
    assert "untagged" not in tail and "draft=prov" in tail and "build_kind(" in tail
    assert "draft = true" not in inspect.getsource(J.write_supplement)
