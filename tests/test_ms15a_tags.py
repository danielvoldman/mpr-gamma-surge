"""MS15a 20 (DL-744, DL-745): tests of scripts/ms13_make_tags.py for the v2 tags and release-v1.0.

The real-repository tests read only git objects (docs/ms13_journal_final_hashes.txt, docs/decision_log.md and the tag criteria-frozen at HEAD) and never create a tag; one test
checks that the tag list is the same before and after. The creation and refusal tests run in a temporary git repository. tests/test_ms13_13u.py (the v1 tests) is not changed.
"""
import hashlib
import importlib.util
import json
import re
import subprocess

import pytest

from mprsurge import config as C

ROOT = C.repo_root()
IDS = "F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5".split()
RELEASE_SENTENCE = ("The figure provenance names R; release-v1.0 differs from R only in documents, the figure map, the hash list "
                    "and helper scripts for tagging and hash lists.")


def _load():
    spec = importlib.util.spec_from_file_location("ms13_make_tags_v2", ROOT / "scripts/ms13_make_tags.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T = _load()


def _git(root, *args, check=True):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True)
    if check:
        assert r.returncode == 0, r.stderr.decode()
    return r.stdout.decode("utf-8")


def _tags(root):
    return sorted(_git(root, "tag", "-l").split())


@pytest.fixture(scope="module")
def real():
    head = _git(ROOT, "rev-parse", "HEAD").strip()
    return {"head": head,
            "list": T.parse_hash_list(_git(ROOT, "show", f"{head}:docs/ms13_journal_final_hashes.txt")),
            "blob": subprocess.run(["git", "show", f"{head}:docs/ms13_journal_final_hashes.txt"], cwd=ROOT, capture_output=True, check=True).stdout,
            "log": _git(ROOT, "show", f"{head}:docs/decision_log.md"),
            "v2": T.make_plan(ROOT, head, 2),
            "v1": T.make_plan(ROOT, head, 1),
            "release": T.release_message(ROOT, head)}


def test_v2_1_the_13_names_are_fig_id_v2_and_not_the_v1_names(real):
    names = [n for n, _ in real["v2"]]
    assert names == [f"fig-{i}-v2" for i in IDS]
    assert len(set(names)) == 13 and not set(names) & {n for n, _ in real["v1"]}
    assert T.RELEASE_TAG == "release-v1.0"


def test_v2_2_every_v2_message_equals_the_hash_list_and_names_its_v1_tag_and_r(real):
    r = T.build_commit_of_list(real["list"])
    assert re.fullmatch(r"[0-9a-f]{40}", r)
    last = max(int(n) for n in re.findall(r"^## DL-(\d+)\b", real["log"], re.M))
    for (name, msg), fid in zip(real["v2"], IDS):
        e = real["list"][fid]
        d = T.parse_message(msg)
        assert d["name"] == name == f"fig-{fid}-v2" and d["fid"] == fid
        assert d["files"] == e["lines"] and len(d["files"]) == (7 if fid in {"FS2", "FS3", "FS4", "FS5"} else 8)
        assert d["commit"] == e["commit"] == r and d["digest"] == e["digest"]
        assert d["venue"] == "Peer Community Journal" and d["section"] == e["heading"]
        assert d["dl"] == f"DL-698 to DL-{last}"
        assert d["supersedes"] == f"fig-{fid}-v1 (local only, not published)"
        assert d["provenance"] == f"draft false, built from R = {r}"
        assert d["criteria_sha"] == "c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05"
    assert sum(len(T.parse_message(m)["files"]) for _, m in real["v2"]) == 100


def test_v2_3_a_v2_message_is_the_v1_message_plus_the_two_new_lines(real):
    for (n2, m2), (n1, m1), fid in zip(real["v2"], real["v1"], IDS):
        stripped = "\n".join(line for line in m2.splitlines() if not line.startswith(("supersedes ", "provenance: ")))
        assert stripped.replace(n2, n1, 1) + "\n" == m1
        assert "supersedes" not in m1 and "provenance:" not in m1
    assert T.build_message("F1", real["list"]["F1"], T.criteria_info(ROOT), 744) == T.build_message("F1", real["list"]["F1"], T.criteria_info(ROOT), 744, 1)


def test_v2_4_the_release_message_values_come_from_the_files(real):
    msg = real["release"]
    head = real["head"]
    lines = msg.splitlines()
    assert lines[0].startswith("release-v1.0: ")
    assert "Author: Daniel Voldman (ORCID https://orcid.org/0009-0005-3409-8944)" in lines
    assert "Licences: MIT (code); CC-BY 4.0 (data, figures and text)" in lines
    assert "Figure tags (13): " + " ".join(f"fig-{i}-v2" for i in IDS) in lines
    assert f"Hash list: docs/ms13_journal_final_hashes.txt SHA-256 {hashlib.sha256(real['blob']).hexdigest()}" in lines
    r = T.build_commit_of_list(real["list"])
    assert f"R (build commit named in the figure provenance records): {r}" in lines
    assert f"T (the commit this tag and the 13 figure tags point to): {head}" in lines and r != head
    crit = T.criteria_info(ROOT)
    assert f"Criteria tag: criteria-frozen (commit {crit['commit']})" in lines and f"Criteria SHA-256: {crit['sha256']}" in lines
    assert lines[-1] == RELEASE_SENTENCE and msg.count(RELEASE_SENTENCE) == 1


def test_v2_5_the_release_message_has_no_doi_no_manuscript_and_no_version_claim(real):
    msg = real["release"]
    assert not re.search(r"\bdoi\b|10\.\d{4,}/|zenodo\.org", msg, re.I)
    assert "manuscript" not in msg.lower() and "submission" not in msg.lower()
    bare = re.sub(r"fig-\w+-v2|release-v1\.0", "", msg)
    assert not re.search(r"\bv\d|version", bare, re.I)
    assert not re.search(r"\b20\d\d-\d\d-\d\d\b", msg)


def test_v2_6_reading_the_plans_creates_no_tag_in_the_real_repository(real):
    before = _tags(ROOT)
    T.make_plan(ROOT, real["head"], 2)
    T.release_message(ROOT, real["head"])
    T.preconditions(ROOT, real["head"], check_gate=False, check_files=False, version=2, release=True)
    assert _tags(ROOT) == before


def test_v2_7_release_option_needs_version_v2():
    assert T.main(["--release"]) == 2


# ---- temporary repository ---------------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture()
def tmp_repo(tmp_path, monkeypatch):
    for k, v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@example.org"), ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@example.org")):
        monkeypatch.setenv(k, v)
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q")
    (r / ".gitignore").write_text("figures/\n", encoding="utf-8", newline="\n")
    (r / "docs").mkdir()
    (r / "docs/decision_log.md").write_text("## DL-700  a\n\n## DL-744  b\n", encoding="utf-8", newline="\n")
    (r / "README.md").write_text("x\n", encoding="utf-8", newline="\n")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "c1")
    c1 = _git(r, "rev-parse", "HEAD").strip()
    _git(r, "tag", "-a", "criteria-frozen", "-m", f"criteria-frozen: test.\n    SHA-256 of the LF text of configs/x.yaml (as committed in {c1}): {'ab' * 32} (1 bytes).")
    out = ["# header"]
    for i in IDS:
        out += ["", f"## {i} (journal main version; draft audit copy: {i[:2]})", f"built from commit: {c1}", f"drawn-data digest: {hashlib.sha256(i.encode()).hexdigest()}"]
        for k, ext in (("png", "png"), ("caption short", "txt")):
            p = r / "figures" / "journal" / i / f"{i}_journal.{ext}"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(f"{i} {k}".encode())
            out.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {k:18s} figures/journal/{i}/{i}_journal.{ext}")
        (r / "figures" / "journal" / i / f"{i}_journal_provenance.json").write_text(json.dumps({"draft": False, "git": {"dirty": False, "commit": c1}}), encoding="utf-8")
    out += ["", "## draft files differing from the manifest: 0"]
    (r / "docs/ms13_journal_final_hashes.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "c2")
    target = _git(r, "rev-parse", "HEAD").strip()
    T.create(r, target, T.make_plan(r, target, 1))  # the v1 tags exist first, as in the real repository
    return r, target, c1


def _pre(r, target, **kw):
    return T.preconditions(r, target, check_gate=False, version=2, release=True, **kw)


def _plan14(r, target):
    return T.make_plan(r, target, 2) + [(T.RELEASE_TAG, T.release_message(r, target))]


def test_v2_8_create_makes_14_annotated_tags_at_one_commit_and_verify_passes_and_v1_is_untouched(tmp_repo):
    r, target, c1 = tmp_repo
    v1_before = {i: _git(r, "rev-parse", f"fig-{i}-v1").strip() for i in IDS}
    assert _pre(r, target) == []
    plan = _plan14(r, target)
    made = T.create(r, target, plan)
    assert made == [f"fig-{i}-v2" for i in IDS] + ["release-v1.0"]
    for n in made:
        assert _git(r, "cat-file", "-t", n).strip() == "tag"
        assert _git(r, "rev-parse", f"{n}^{{commit}}").strip() == target
    rows = T.verify(r, target, plan)
    assert len(rows) == 14 and all(all(x[1:]) for x in rows)
    assert {i: _git(r, "rev-parse", f"fig-{i}-v1").strip() for i in IDS} == v1_before
    assert len(_tags(r)) == 1 + 13 + 13 + 1  # criteria-frozen, 13 v1, 13 v2, release-v1.0
    assert _git(r, "tag", "-l", "criteria-frozen").strip() == "criteria-frozen"


def test_v2_9_refusals(tmp_repo):
    r, target, c1 = tmp_repo
    assert _pre(r, target) == []
    # dirty tree
    (r / "README.md").write_text("changed\n", encoding="utf-8", newline="\n")
    assert any("not clean" in p for p in _pre(r, target))
    _git(r, "checkout", "--", "README.md")
    # a figure file that differs from the list
    f = r / "figures/journal/F1/F1_journal.png"
    f.write_bytes(b"other")
    assert any("F1" in p and "differs" in p for p in _pre(r, target))
    f.write_bytes(b"F1 png")
    assert _pre(r, target) == []
    # HEAD is not the target
    assert any("not HEAD" in p for p in _pre(r, _git(r, "rev-parse", "HEAD~1").strip()))
    # a missing v1 tag
    _git(r, "tag", "-d", "fig-F2-v1")
    assert any("superseded do not exist" in p and "fig-F2-v1" in p for p in _pre(r, target))
    _git(r, "tag", "fig-F2-v1", c1)
    assert _pre(r, target) == []
    # an existing v2 tag and an existing release tag
    T.create(r, target, T.make_plan(r, target, 2)[:1])
    assert any("fig-*-v2 tags already exist" in p for p in _pre(r, target))
    _git(r, "tag", "release-v1.0", c1)
    assert any("release-v1.0 already exists" in p for p in _pre(r, target))


def test_v2_10_provenance_must_say_draft_false_dirty_false_and_the_build_commit(tmp_repo):
    r, target, c1 = tmp_repo
    p = r / "figures/journal/F3/F3_journal_provenance.json"
    p.write_text(json.dumps({"draft": True, "git": {"dirty": False, "commit": c1}}), encoding="utf-8")
    assert any("F3" in x and "draft=True" in x for x in _pre(r, target))
    p.write_text(json.dumps({"draft": False, "git": {"dirty": True, "commit": c1}}), encoding="utf-8")
    assert any("F3" in x and "dirty=True" in x for x in _pre(r, target))
    p.write_text(json.dumps({"draft": False, "git": {"dirty": False, "commit": target}}), encoding="utf-8")
    assert any("F3" in x and "commit=" in x for x in _pre(r, target))
    p.unlink()
    assert any("F3" in x and "provenance record missing" in x for x in _pre(r, target))
    p.write_text(json.dumps({"draft": False, "git": {"dirty": False, "commit": c1}}), encoding="utf-8")
    assert _pre(r, target) == []


def test_v2_11_the_13_sections_must_name_one_build_commit(tmp_repo):
    r, target, c1 = tmp_repo
    lst = T.parse_hash_list(_git(r, "show", f"{target}:docs/ms13_journal_final_hashes.txt"))
    assert T.build_commit_of_list(lst) == c1
    lst["F2"]["commit"] = target
    with pytest.raises(RuntimeError):
        T.build_commit_of_list(lst)
