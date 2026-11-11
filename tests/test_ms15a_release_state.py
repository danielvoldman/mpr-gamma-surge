"""MS15a 21 (DL-747, DL-748): tests of the release state after the push (the user's ls-remote record against the local tag objects),
of the Zenodo data package outside the repository, and of the README texts.

Read-only: no tag is created, no network command is run, nothing is written (the package is only read). The tests that need the local tags or the
package outside the repository skip with a message when those are absent (for example in a fresh clone, where tags exist only if fetched and the
package folder does not).
"""
import hashlib
import importlib.util
import re
import subprocess
from pathlib import Path

import pytest

from mprsurge import config as C

ROOT = C.repo_root()
PKG = Path(r"C:\dev\_zenodo_data_package")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CHK = _load("ms15a_check_push_record_t", "scripts/ms15a_check_push_record.py")
PKGM = _load("ms15a_make_data_package_t", "scripts/ms15a_make_data_package.py")


def _tags_present():
    r = subprocess.run(["git", "tag", "-l"], cwd=ROOT, capture_output=True, text=True)
    have = set(r.stdout.split())
    return all(t in have for t in CHK.PUSHED)


need_tags = pytest.mark.skipif(not _tags_present(), reason="the 18 pushed tags are not in this repository (a fresh clone without the tags): no comparison possible")
need_pkg = pytest.mark.skipif(not PKG.is_dir(), reason=f"{PKG} does not exist (build it with scripts/ms15a_make_data_package.py)")


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---- the push record -------------------------------------------------------------------------------------------------------------------------
def test_the_push_record_has_the_users_header_and_the_unverified_visibility_line():
    t = (ROOT / "docs/ms15a_push_record.md").read_text(encoding="utf-8")
    assert "Pasted by the user in chat on 2026-11-10 at 20:43 local time (America/Toronto)" in t
    assert "the permission check denied them to Claude Code" in t
    assert "UNVERIFIED" in t and "private" in t


def test_the_push_record_parses_to_master_and_the_eighteen_tags():
    refs = CHK.parse(ROOT / "docs/ms15a_push_record.md")
    assert "refs/heads/master" in refs
    names = {r[len("refs/tags/"):].removesuffix("^{}") for r in refs if r.startswith("refs/tags/")}
    assert names == set(CHK.PUSHED) and len(names) == 18
    assert not [r for r in refs if re.match(r"refs/tags/fig-.*-v1", r)]          # the v1 tags are not on the remote


@need_tags
def test_the_push_record_equals_the_local_tag_objects():
    refs = CHK.parse(ROOT / "docs/ms15a_push_record.md")
    assert refs["refs/heads/master"] == CHK.T
    for t in CHK.PUSHED:
        _, obj = CHK.git("rev-parse", "--verify", "-q", f"refs/tags/{t}")
        _, typ = CHK.git("cat-file", "-t", f"refs/tags/{t}")
        _, peeled = CHK.git("rev-parse", f"refs/tags/{t}^{{commit}}")
        assert refs[f"refs/tags/{t}"] == obj, t
        if t in CHK.LIGHT:
            assert typ == "commit" and f"refs/tags/{t}^{{}}" not in refs
        else:
            assert typ == "tag", t
            assert refs[f"refs/tags/{t}^{{}}"] == peeled, t
            if t in CHK.V2 or t == "release-v1.0":
                assert peeled == CHK.T, t


@need_tags
def test_the_checker_script_exits_zero_on_the_committed_record():
    r = subprocess.run([str(ROOT / ".venv/Scripts/python.exe"), str(ROOT / "scripts/ms15a_check_push_record.py")], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]
    assert " NO" not in r.stdout.replace("remote ref set", "")


# ---- the data package (outside the repository) ----------------------------------------------------------------------------------------------
@need_pkg
def test_the_package_manifest_equals_the_files_in_the_package():
    have = sorted(p.relative_to(PKG).as_posix() for p in PKG.rglob("*") if p.is_file())
    man = {}
    for ln in (PKG / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        h, _, p = ln.partition("  ")
        man[p] = h
    assert sorted(man) == [h for h in have if h != "MANIFEST.sha256"]
    for p, h in man.items():
        assert _sha(PKG / p) == h, p
    assert len(man) == 105 and len(have) == 106


@need_pkg
def test_every_package_file_equals_its_source_by_sha256():
    ents = PKGM.journal_entries()
    assert len(ents) == 100
    for h, _kind, proj, pkg in ents:
        assert _sha(PKG / pkg) == h, pkg
        assert _sha(ROOT / proj) == h, proj
    for d in PKGM.DOC_FILES:
        assert _sha(PKG / d) == _sha(ROOT / d), d


@need_pkg
def test_no_file_in_the_package_is_outside_the_hash_lists_names():
    ents = PKGM.journal_entries()
    allowed = {e[3] for e in ents} | set(PKGM.DOC_FILES) | set(PKGM.GENERATED)
    have = {p.relative_to(PKG).as_posix() for p in PKG.rglob("*") if p.is_file()}
    assert have == allowed
    assert not [h for h in have if h.endswith((".eps", ".json")) or h.startswith("_review") or "export_manifest" in h]


@need_pkg
def test_the_data_readme_has_no_doi_version_or_date():
    t = (PKG / "DATA_README.md").read_text(encoding="utf-8")
    assert t.encode("utf-8") == PKGM.README.format(repo=PKGM.REPO_URL).encode("utf-8")
    _no_doi_version_date(t)


def test_the_package_script_verify_mode_is_consistent_with_the_package():
    if not PKG.is_dir():
        pytest.skip(f"{PKG} does not exist")
    assert PKGM.verify(PKG) == 0


# ---- the README texts ----------------------------------------------------------------------------------------------------------------------
def _no_doi_version_date(t):
    assert not re.search(r"10\.\d{4,9}/", t)
    assert not re.search(r"(?i)doi\.org|\bdoi\s*[:=]", t)
    s = t.replace("release-v1.0", "")
    assert not re.search(r"(?i)(?<![\w-])version\s*[:=]?\s*v?\d+\.\d+", s), "a version string"
    assert not re.search(r"\bv\d+\.\d+\.\d+\b", s), "a semantic version"
    assert not re.search(r"\d{4}-\d{2}-\d{2}", t), "a date"


def test_the_repository_readme_and_changelog_have_no_doi_or_release_version_or_date():
    for f in ("README.md", "CHANGELOG.md"):
        t = (ROOT / f).read_text(encoding="utf-8")
        assert not re.search(r"10\.\d{4,9}/", t), f
        assert not re.search(r"(?i)doi\.org|\bdoi\s*[:=]", t), f
        s = t.replace("release-v1.0", "")
        assert not re.search(r"(?i)(?<![\w-])version\s*[:=]\s*v?\d+\.\d+", s), f
        assert not re.search(r"\bv\d+\.\d+\.\d+\b", s), f


def test_the_citation_file_has_no_doi_version_or_release_date_key():
    keys = [ln.split(":")[0] for ln in (ROOT / "CITATION.cff").read_text(encoding="utf-8").splitlines() if ln and not ln.startswith((" ", "#", "-"))]
    for k in ("doi", "version", "date-released"):
        assert k not in keys
