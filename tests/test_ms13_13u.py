"""MS13 13u (DL-723, DL-724): tests of scripts/ms13_make_tags.py, the 13 annotated local tags fig-<ID>-v1.

The real-repository tests read only git objects (docs/ms13_journal_final_hashes.txt, docs/decision_log.md and the tag criteria-frozen at HEAD) and do not depend on whether the
fig-* tags exist yet. The creation tests run in a temporary git repository; they never touch the project's tags.
"""
import hashlib
import importlib.util
import re
import subprocess

import pytest

from mprsurge import config as C

ROOT = C.repo_root()
IDS = "F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5".split()


def _load():
    spec = importlib.util.spec_from_file_location("ms13_make_tags", ROOT / "scripts/ms13_make_tags.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T = _load()


def _head():
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, check=True).stdout.decode().strip()


def _show(rev_path):
    return subprocess.run(["git", "show", rev_path], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8")


@pytest.fixture(scope="module")
def real():
    head = _head()
    plan = T.make_plan(ROOT, head)
    lst = T.parse_hash_list(_show(f"{head}:docs/ms13_journal_final_hashes.txt"))
    return {"head": head, "plan": plan, "list": lst, "log": _show(f"{head}:docs/decision_log.md")}


def test_u1_the_13_tag_names_are_fig_id_v1_for_the_13_journal_figures(real):
    names = [n for n, _ in real["plan"]]
    assert names == [f"fig-{i}-v1" for i in IDS]
    assert len(set(names)) == 13
    assert "fig-F4-v1" not in names and "fig-F5-v1" in names and "fig-F5c-v1" in names and "fig-F4a-v1" in names and "fig-F4b-v1" in names
    assert set(real["list"]) == set(IDS)


def test_u2_every_message_equals_the_hash_list_section_line_for_line(real):
    for (name, msg), fid in zip(real["plan"], IDS):
        e = real["list"][fid]
        d = T.parse_message(msg)
        assert d["name"] == name and d["fid"] == fid
        assert d["section"] == e["heading"]
        assert d["commit"] == e["commit"] and re.fullmatch(r"[0-9a-f]{40}", d["commit"])
        assert d["digest"] == e["digest"] and re.fullmatch(r"[0-9a-f]{64}", d["digest"])
        assert d["files"] == e["lines"], fid
        assert len(d["files"]) == (7 if fid in {"FS2", "FS3", "FS4", "FS5"} else 8)
        assert d["venue"] == "Peer Community Journal"


def test_u3_no_hash_in_any_message_is_absent_from_the_list_and_every_listed_hash_is_in_its_message(real):
    all_list = set(re.findall(r"[0-9a-f]{64}", _show(f"{real['head']}:docs/ms13_journal_final_hashes.txt")))
    for (name, msg), fid in zip(real["plan"], IDS):
        in_msg = set(re.findall(r"[0-9a-f]{64}", msg))
        crit = T.criteria_info(ROOT)["sha256"]
        assert in_msg - {crit} <= all_list, name
        for h, _, p in real["list"][fid]["files"]:
            assert h in in_msg, (name, p)
        assert real["list"][fid]["digest"] in in_msg


def test_u4_criteria_and_decision_log_range_values(real):
    crit = T.criteria_info(ROOT)
    assert crit["commit"] == "dd8330c5eaacd63d21e7b7969430988d00862769"
    assert crit["sha256"] == "c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05"
    last = max(int(n) for n in re.findall(r"^## DL-(\d+)\b", real["log"], re.M))
    for name, msg in real["plan"]:
        d = T.parse_message(msg)
        assert d["dl"] == f"DL-698 to DL-{last}"
        assert d["criteria_tag"] == f"criteria-frozen (commit {crit['commit']})"
        assert d["criteria_sha"] == crit["sha256"]
        assert "git-ignored" in msg and "audit copies and are not tagged" in msg


def test_u5_the_list_has_100_journal_file_lines_and_the_message_lines_total_100(real):
    assert sum(len(e["files"]) for e in real["list"].values()) == 100
    assert sum(len(T.parse_message(m)["files"]) for _, m in real["plan"]) == 100


# ---- creation in a temporary repository ------------------------------------------------------------------------------------------------------------------------------------

def _g(root, *args, check=True):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True)
    if check:
        assert r.returncode == 0, r.stderr.decode()
    return r.stdout.decode("utf-8")


@pytest.fixture()
def tmp_repo(tmp_path, monkeypatch):
    for k, v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@example.org"), ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@example.org")):
        monkeypatch.setenv(k, v)
    r = tmp_path / "repo"
    r.mkdir()
    _g(r, "init", "-q")
    (r / ".gitignore").write_text("figures/\n", encoding="utf-8", newline="\n")
    (r / "docs").mkdir()
    (r / "docs/decision_log.md").write_text("## DL-700  a\n\n## DL-731  b\n", encoding="utf-8", newline="\n")
    (r / "README.md").write_text("x\n", encoding="utf-8", newline="\n")
    _g(r, "add", "-A")
    _g(r, "commit", "-q", "-m", "c1")
    c1 = _g(r, "rev-parse", "HEAD").strip()
    _g(r, "tag", "-a", "criteria-frozen", "-m", f"criteria-frozen: test.\n    SHA-256 of the LF text of configs/x.yaml (as committed in {c1}): {'ab' * 32} (1 bytes).")
    out = ["# header"]
    for i in IDS:
        out += ["", f"## {i} (journal main version; draft audit copy: {i[:2] if i.startswith('FS') else i[:2]})", f"built from commit: {c1}", f"drawn-data digest: {hashlib.sha256(i.encode()).hexdigest()}"]
        for k, ext in (("png", "png"), ("caption short", "txt")):
            p = r / "figures" / "journal" / i / f"{i}_journal.{ext}"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(f"{i} {k}".encode())
            out.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {k:18s} figures/journal/{i}/{i}_journal.{ext}")
    out += ["", "## draft files differing from the manifest: 0"]
    (r / "docs/ms13_journal_final_hashes.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    _g(r, "add", "-A")
    _g(r, "commit", "-q", "-m", "c2")
    return r


def _plan(r):
    target = _g(r, "rev-parse", "HEAD").strip()
    return target, T.make_plan(r, target)


def test_u6_create_makes_13_annotated_tags_at_one_commit_and_verify_passes(tmp_repo):
    r = tmp_repo
    target, plan = _plan(r)
    assert T.preconditions(r, target, check_gate=False) == []
    made = T.create(r, target, plan)
    assert made == [f"fig-{i}-v1" for i in IDS]
    assert sorted(_g(r, "tag", "-l", "fig-*").split()) == sorted(made)
    for n in made:
        assert _g(r, "cat-file", "-t", n).strip() == "tag"
        assert _g(r, "rev-parse", f"{n}^{{commit}}").strip() == target
    rows = T.verify(r, target, plan)
    assert len(rows) == 13 and all(all(x[1:]) for x in rows)
    assert _g(r, "tag", "-l", "criteria-frozen").strip() == "criteria-frozen"


def test_u7_preconditions_refuse_existing_fig_tags_a_dirty_tree_a_changed_file_and_a_wrong_target(tmp_repo):
    r = tmp_repo
    target, plan = _plan(r)
    assert T.preconditions(r, target, check_gate=False) == []
    (r / "README.md").write_text("changed\n", encoding="utf-8", newline="\n")
    assert any("not clean" in p for p in T.preconditions(r, target, check_gate=False))
    _g(r, "checkout", "--", "README.md")
    (r / "figures/journal/F1/F1_journal.png").write_bytes(b"other")
    assert any("F1" in p and "differs" in p for p in T.preconditions(r, target, check_gate=False))
    (r / "figures/journal/F1/F1_journal.png").write_bytes(b"F1 png")
    assert T.preconditions(r, target, check_gate=False) == []
    assert any("not HEAD" in p for p in T.preconditions(r, _g(r, "rev-parse", "HEAD~1").strip(), check_gate=False))
    T.create(r, target, plan[:1])
    assert any("fig-* tags already exist" in p for p in T.preconditions(r, target, check_gate=False))


def test_u8_create_stops_and_names_the_tags_made_when_one_tag_exists_and_never_moves_it(tmp_repo):
    r = tmp_repo
    target, plan = _plan(r)
    first = _g(r, "rev-parse", "HEAD~1").strip()
    _g(r, "tag", "fig-F3-v1", first)
    with pytest.raises(RuntimeError) as e:
        T.create(r, target, plan)
    assert "fig-F3-v1" in str(e.value) and "fig-F1-v1" in str(e.value) and "fig-F2-v1" in str(e.value)
    assert _g(r, "rev-parse", "fig-F3-v1^{commit}").strip() == first
    assert "fig-F4a-v1" not in _g(r, "tag", "-l", "fig-*").split()


def test_u9_verify_reports_a_message_that_differs(tmp_repo):
    r = tmp_repo
    target, plan = _plan(r)
    T.create(r, target, plan)
    bad = [(n, m.replace("Venue: Peer Community Journal", "Venue: other")) if n == "fig-F2-v1" else (n, m) for n, m in plan]
    rows = T.verify(r, target, bad)
    assert [x[0] for x in rows if not all(x[1:])] == ["fig-F2-v1"]
