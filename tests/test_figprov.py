"""MS13 13b: figure infrastructure only (provenance and params writer, check_clean_tree). No real figure; the stand-in script, records and
repository below exist only in these tests. Tolerances: every comparison is exact (SHA-256, set equality, exit codes, exact messages); JSON
floats round-trip exactly (rel 0)."""
import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from mprsurge import config as C
from mprsurge.plotting import figprov as F

ROOT = C.repo_root()
FROZEN = "c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05"
FORBIDDEN = ("mprsurge.simulate_mf", "mprsurge.qif_network", "mprsurge.run", "mprsurge.timing_run", "mprsurge.models")


def _forbidden(src: str, pkg="mprsurge.plotting") -> set:
    """Imported names that resolve into a simulation or run module (relative imports resolved against pkg)."""
    bad = set()
    for n in ast.walk(ast.parse(src)):
        names = []
        if isinstance(n, ast.Import):
            names = [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            base = n.module or ""
            if n.level:
                parts = pkg.split(".")[: len(pkg.split(".")) - (n.level - 1)]
                base = ".".join(parts + ([n.module] if n.module else []))
            names = [base] + [f"{base}.{a.name}" for a in n.names]
        bad |= {m for m in names for f in FORBIDDEN if m == f or m.startswith(f + ".")}
    return bad


def test_figure_code_imports_no_simulation_or_run_module():
    # exact: the forbidden-import set of every figure module and script is empty; the detector itself finds a planted import
    assert _forbidden("from .. import run\nimport mprsurge.simulate_mf") == {"mprsurge.run", "mprsurge.simulate_mf"}
    files = sorted((ROOT / "src/mprsurge/plotting").glob("*.py")) + sorted((ROOT / "scripts").glob("fig_*.py")) + [ROOT / "scripts/check_clean_tree.py"]
    assert any(f.name == "figprov.py" for f in files)
    for f in files:
        assert _forbidden(f.read_text(encoding="utf-8")) == set(), f
    code = ("import sys, mprsurge.plotting.figprov; "
            "print([m for m in sys.modules if m in %r or m.startswith('mprsurge.models')])" % (FORBIDDEN,))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0 and out.stdout.strip() == "[]", out.stdout + out.stderr         # transitive imports too


def _record(path: Path, name="stand_in_0000_aaaaaaaaaaaa", n=1) -> Path:
    r = {"name": name, "status": "ok", "config_hash12": "aaaaaaaaaaaa", "seed": {"root_seed": 7, "spawn_key": [0, n]},
         "git": {"commit": "0" * 40, "dirty": False}, "criteria_sha256": None,
         "solver": {"method": "DOP853", "rtol": 1e-10}, "config": {"solver": {"method": "DOP853", "rtol": 1e-10}, "network": {"N": 10000}}}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(r), encoding="utf-8")
    return path


@pytest.fixture
def stand_in(tmp_path):
    res = tmp_path / "results"
    rec = _record(res / "A0" / "rec.json")
    (res / "A0" / "table.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    script = tmp_path / "fig_STAND.py"
    script.write_text("# stand-in\n", encoding="utf-8")
    fig = tmp_path / "out" / "F3.pdf"
    fig.parent.mkdir()
    fig.write_bytes(b"%PDF stand-in")
    rows = [{"panel": "a", "section": "", "name": "rtol", "key": "solver.rtol", "value": 1e-10, "units": "", "status": "",
             "source_run_id": "stand_in_0000_aaaaaaaaaaaa", "source_config_hash12": "aaaaaaaaaaaa"},
            {"panel": "a", "section": "", "name": "N", "key": "network.N", "value": 10000, "units": "", "status": "",
             "source_run_id": "stand_in_0000_aaaaaaaaaaaa", "source_config_hash12": "aaaaaaaaaaaa"}]
    return dict(res=res, rec=rec, script=script, fig=fig, rows=rows, out=tmp_path / "figures" / "F3")


def _build(s, **kw):
    args = dict(script=s["script"], inputs=[s["rec"], s["res"] / "A0" / "table.csv"], outputs=[s["fig"]], params_rows=s["rows"],
                input_tables=[{"path": s["res"] / "A0" / "table.csv", "rows": 1}], claim_limits=["G6-D1"], out_dir=s["out"], root=ROOT)
    args.update(kw)
    return F.write_figure_provenance("F3", **args)


def _tree(p: Path):
    return sorted((str(q.relative_to(p)), q.read_bytes()) for q in p.rglob("*") if q.is_file())


def test_writer_writes_nothing_under_results_and_refuses_results_as_target(stand_in):
    before = _tree(stand_in["res"])
    _build(stand_in)
    assert _tree(stand_in["res"]) == before                                  # exact: byte-identical listing
    with pytest.raises(F.FigureError, match="never written under results"):
        F.write_figure_provenance("F3", script=stand_in["script"], inputs=[stand_in["rec"]], out_dir=ROOT / "results" / "zz_no", root=ROOT)
    assert not (ROOT / "results" / "zz_no").exists()


def test_provenance_fields_complete(stand_in):
    prov = _build(stand_in)
    on_disk = json.loads((stand_in["out"] / "F3_provenance.json").read_text(encoding="utf-8"))
    assert set(on_disk) == set(F.PROVENANCE_FIELDS) == set(prov)                 # exact set equality
    for k in ("git", "python", "packages", "julia", "cpu", "configs"):
        assert isinstance(on_disk[k], dict)
    for k in ("modules", "inputs", "input_tables", "claim_limits", "outputs", "warnings"):
        assert isinstance(on_disk[k], list)
    assert on_disk["criteria_sha256"] == FROZEN and on_disk["criteria_tag"] == "criteria-frozen"
    assert on_disk["criteria_commit"] == "dd8330c5eaacd63d21e7b7969430988d00862769"
    assert on_disk["git"]["commit"] and on_disk["os"] and on_disk["created_utc"] and on_disk["draft"] is True      # untagged = draft
    assert all(set(F.INPUT_FIELDS) <= set(i) for i in on_disk["inputs"])
    rec = on_disk["inputs"][0]
    assert set(F.RECORD_INPUT_FIELDS) <= set(rec) and rec["run_id"] == "stand_in_0000_aaaaaaaaaaaa"
    assert on_disk["seeds"] == {"inputs": [{"run_id": rec["run_id"], "root_seed": 7, "spawn_key": [0, 1]}], "figure_script": None}
    assert on_disk["numerical_settings"][0]["network"] == {"N": 10000}
    assert on_disk["claim_limits"] == ["G6-D1"] and on_disk["status"] == "ok" and on_disk["numba_cache_cleared"] is None


def test_recorded_hashes_match_stored_files_and_a_changed_byte_is_found(stand_in):
    _build(stand_in)
    pp = stand_in["out"] / "F3_provenance.json"
    assert F.verify_figure_provenance(pp, ROOT) == []                            # exact
    outs = {Path(o["path"]).name for o in json.loads(pp.read_text())["outputs"]}
    assert outs == {"F3.pdf", "F3_params.csv"}
    stand_in["fig"].write_bytes(b"%PDF stand-in!")
    assert [p.startswith("sha256 differs") for p in F.verify_figure_provenance(pp, ROOT)] == [True]
    stand_in["fig"].unlink()
    assert F.verify_figure_provenance(pp, ROOT)[0].startswith("missing")


def test_params_csv_matches_provenance_and_a_changed_value_is_found(stand_in):
    _build(stand_in)
    pp, cp = stand_in["out"] / "F3_provenance.json", stand_in["out"] / "F3_params.csv"
    assert F.check_params_against_provenance(cp, pp, ROOT) == []                 # exact; floats equal after the JSON round trip
    assert cp.read_text().splitlines()[0] == ",".join(F.PARAMS_COLUMNS)
    rec = json.loads(stand_in["rec"].read_text())
    rec["config"]["solver"]["rtol"] = 1e-9
    stand_in["rec"].write_text(json.dumps(rec))
    assert len(F.check_params_against_provenance(cp, pp, ROOT)) == 1


def test_varied_flag_is_true_only_where_values_differ(stand_in):
    rows = stand_in["rows"] + [dict(stand_in["rows"][0], value=1e-9)]
    _build(stand_in, params_rows=rows)
    lines = (stand_in["out"] / "F3_params.csv").read_text().splitlines()[1:]
    assert [ln.rsplit(",", 1)[1] for ln in lines] == ["True", "False", "True"]


def test_missing_input_gives_a_clear_error_and_writes_nothing(stand_in):
    gone = stand_in["res"] / "A0" / "not_there.npz"
    with pytest.raises(F.MissingInputError) as e:
        _build(stand_in, inputs=[stand_in["rec"], gone])
    assert str(gone) in str(e.value)                                              # exact: the path is in the message
    assert not stand_in["out"].exists()                                           # no figure files, no blank panel
    with pytest.raises(F.MissingInputError, match="not_there_script"):
        _build(stand_in, script=stand_in["res"] / "not_there_script.py")


def test_fs6_is_refused(stand_in):
    with pytest.raises(F.FigureRefused, match="MS12-C1"):
        F.write_figure_provenance("FS6", script=stand_in["script"], inputs=[stand_in["rec"]], out_dir=stand_in["out"], root=ROOT)
    with pytest.raises(F.FigureRefused, match="MS12-C1"):
        F.write_params_csv(stand_in["out"] / "FS6_params.csv", [], "FS6")
    assert not stand_in["out"].exists() and not (ROOT / "scripts" / "fig_FS6.py").exists()
    with pytest.raises(F.FigureError, match="unknown figure id"):
        F.require_buildable("F9")


def test_tagged_build_refuses_a_dirty_tree_and_untagged_is_draft(stand_in, monkeypatch):
    monkeypatch.setattr(F, "dirty_lines", lambda root=None: ["?? stray.txt"])
    with pytest.raises(F.DirtyTreeError):
        _build(stand_in, tag_build=True)
    assert not stand_in["out"].exists()
    assert _build(stand_in)["draft"] is True
    monkeypatch.setattr(F, "dirty_lines", lambda root=None: [])
    assert _build(stand_in, tag_build=True)["draft"] is False


def _git(repo, *a):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True)


def _load_script():
    spec = importlib.util.spec_from_file_location("check_clean_tree", ROOT / "scripts" / "check_clean_tree.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_check_clean_tree_refuses_modified_and_untracked_and_accepts_clean(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "a.txt").write_text("one\n")
    (repo / ".gitignore").write_text("results/\nfigures/\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "x")
    m = _load_script()
    snap = lambda: sorted((str(q.relative_to(repo)), q.read_bytes()) for q in repo.rglob("*")
                          if q.is_file() and ".git" not in q.parts and q.relative_to(repo).parts[0] not in ("results", "figures"))
    before = snap()
    assert m.main(["--root", str(repo)]) == 0                                     # exact exit codes: clean 0
    (repo / "results").mkdir()
    (repo / "results" / "x.json").write_text("{}")
    (repo / "figures").mkdir()
    (repo / "figures" / "y.pdf").write_text("p")
    assert m.main(["--root", str(repo)]) == 0                                     # git-ignored outputs do not make the tree dirty
    (repo / "a.txt").write_text("two\n")
    assert m.main(["--root", str(repo)]) == 1 and " M a.txt" in capsys.readouterr().out      # modified tracked file: 1
    (repo / "a.txt").write_text("one\n")
    assert m.main(["--root", str(repo)]) == 0
    (repo / "stray.txt").write_text("s")
    assert m.main(["--root", str(repo)]) == 1 and "?? stray.txt" in capsys.readouterr().out  # untracked file: 1
    (repo / "stray.txt").unlink()
    assert m.main(["--root", str(repo)]) == 0
    assert snap() == before                                                       # the check wrote nothing
