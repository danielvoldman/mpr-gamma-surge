"""scripts/run_ms10_list.py (MS10 10c, 10e): the refusals of a real launch. Nothing is launched: build_jobs and the pool are replaced by a tripwire."""
import importlib.util
from pathlib import Path

import pytest

from mprsurge import provenance as P
from mprsurge import run as R
from mprsurge.analysis import ms10_runlist as RL

ROOT = Path(__file__).resolve().parents[1]


class Launched(Exception):
    pass


def _launcher(monkeypatch, dirty: bool, draft: bool):
    spec = importlib.util.spec_from_file_location("run_ms10_list", ROOT / "scripts" / "run_ms10_list.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    def tripwire(*a, **k):
        raise Launched("the launcher reached job building")
    monkeypatch.setattr(mod, "build_jobs", tripwire)
    monkeypatch.setattr(R, "run_jobs", tripwire)
    monkeypatch.setattr(RL, "is_draft", lambda: draft)
    monkeypatch.setattr(P, "environment_info", lambda with_julia=True: {"git": {"dirty": dirty, "commit": "x"}})
    return mod


ARGS = ["--list", "S10", "--workers", "1", "--journal-dir", "results/ms10/launch_test_never_written"]


def test_the_launcher_refuses_on_a_dirty_tree(monkeypatch, capsys):
    mod = _launcher(monkeypatch, dirty=True, draft=False)
    assert mod.main(ARGS) == 3
    assert "dirty" in capsys.readouterr().err
    assert not (ROOT / "results/ms10/launch_test_never_written").exists()


def test_the_launcher_refuses_a_list_whose_data_files_are_not_frozen(monkeypatch, capsys):
    mod = _launcher(monkeypatch, dirty=False, draft=True)
    assert mod.main(ARGS) == 4
    assert "DRAFT" in capsys.readouterr().err


def test_the_launcher_needs_a_journal_dir_and_only_a_clean_frozen_tree_reaches_job_building(monkeypatch, capsys):
    mod = _launcher(monkeypatch, dirty=False, draft=False)
    assert mod.main(["--list", "S10"]) == 2
    with pytest.raises(Launched):
        mod.main(ARGS)


def test_the_dry_run_is_list_only_and_needs_neither_a_clean_tree_nor_a_journal(monkeypatch, capsys):
    mod = _launcher(monkeypatch, dirty=True, draft=False)
    assert mod.main(["--list", "S10", "--dry-run"]) == 0
    assert "list SHA-256 79f72a123467ccb0e79c327b7f82b0bd599dc5277cb37dc94466d0409eea94f3" in capsys.readouterr().out
