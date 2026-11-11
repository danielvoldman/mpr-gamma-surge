"""MS15a 22 (DL-751 G2, close item 86): the Zenodo data package as one zip per figure (scripts/ms15a_make_data_package.py --zips).

The build tests write the package twice into pytest temporary folders (outside the repository) and read figures/ and the repository documents;
nothing in the repository is written, no tag is created, no network command is run. They skip with a message when figures/ does not hold the
100 journal files (a fresh clone: figures/ is git-ignored). The tests of the final folder skip with a message when it does not exist.
"""
import hashlib
import importlib.util
import re
import zipfile
from pathlib import Path

import pytest

from mprsurge import config as C

ROOT = C.repo_root()
FINAL = Path(r"C:\dev\_zenodo_data_package_zips")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PKGM = _load("ms15a_make_data_package_zips_t", "scripts/ms15a_make_data_package.py")
ENTS = PKGM.journal_entries()
HAVE_FIGURES = len(ENTS) == 100 and all((ROOT / e[2]).is_file() for e in ENTS)

need_figures = pytest.mark.skipif(not HAVE_FIGURES, reason="the 100 journal figure files are not in figures/ (git-ignored; a fresh clone): no package can be built")
need_final = pytest.mark.skipif(not FINAL.is_dir(), reason=f"{FINAL} does not exist (build it with scripts/ms15a_make_data_package.py --zips)")


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def builds(tmp_path_factory):
    base = tmp_path_factory.mktemp("zips")
    a, b = base / "a", base / "b"
    PKGM.make_zip_package(a)
    PKGM.make_zip_package(b)
    return a, b


def _check_no_doi_version_date(t):
    assert not re.search(r"10\.\d{4,9}/", t)
    assert not re.search(r"(?i)doi\.org|\bdoi\s*[:=]", t)
    s = t.replace("release-v1.0", "")
    assert not re.search(r"(?i)(?<![\w-])version\s*[:=]?\s*v?\d+\.\d+", s), "a version string"
    assert not re.search(r"\bv\d+\.\d+\.\d+\b", s), "a semantic version"
    assert not re.search(r"\d{4}-\d{2}-\d{2}", t), "a date"


@need_figures
def test_the_two_builds_are_byte_identical(builds):
    a, b = builds
    ha, hb = PKGM.tree_hashes(a), PKGM.tree_hashes(b)
    assert ha == hb and len(ha) == 20                       # 13 zips + 7 unzipped top-level files
    assert sorted(ha) == sorted(PKGM.zip_expected_names(ENTS))


@need_figures
def test_the_file_count_is_below_100_and_the_size_is_known(builds):
    a, _ = builds
    files = [p for p in a.rglob("*") if p.is_file()]
    assert len(files) == 20 < 100
    assert sum(p.stat().st_size for p in files) < 50e9      # the 50 GB limit is UNVERIFIED; the sum is about 79 MB


@need_figures
def test_zip_entries_are_sorted_with_the_fixed_date_deflate_and_no_extra(builds):
    a, _ = builds
    zips = sorted(a.glob("*_journal_files.zip"))
    assert len(zips) == 13
    for zp in zips:
        with zipfile.ZipFile(zp) as zf:
            infos = zf.infolist()
            names = [zi.filename for zi in infos]
            assert names == sorted(names) and len(names) == len(set(names)) and names
            assert zf.comment == b""
            for zi in infos:
                assert zi.date_time == (1980, 1, 1, 0, 0, 0), (zp.name, zi.filename)
                assert zi.compress_type == zipfile.ZIP_DEFLATED
                assert zi.extra == b"" and zi.comment == b"" and zi.external_attr == 0 and zi.create_system == 0
                assert not zi.filename.endswith("/") and "\\" not in zi.filename and zi.filename.startswith("figures/journal/")


@need_figures
def test_every_zip_member_equals_the_hash_list_and_its_source(builds):
    a, _ = builds
    for fid, grp in PKGM.figure_groups(ENTS).items():
        with zipfile.ZipFile(a / PKGM.zip_name(fid)) as zf:
            assert zf.namelist() == [e[2] for e in grp]      # the same relative paths as in the hash list
            for e in grp:
                data = zf.read(e[2])
                assert hashlib.sha256(data).hexdigest() == e[0] == _sha(ROOT / e[2])


@need_figures
def test_inner_manifest_equals_the_hash_list_for_the_100_figure_files(builds):
    a, _ = builds
    lines = (a / PKGM.INNER).read_text(encoding="utf-8").splitlines()
    assert len(lines) == 100
    rows = [(ln.partition("  ")[0], ln.partition("  ")[2]) for ln in lines]
    assert all(re.fullmatch(r"[0-9a-f]{64}", h) and re.fullmatch(r"F\w+_journal_files\.zip:figures/journal/\S+", r) for h, r in rows)
    got = {(h, r.split(":", 1)[1]) for h, r in rows}
    assert got == {(e[0], e[2]) for e in ENTS}
    listed = {(m.group(1), m.group(3)) for ln in (ROOT / "docs/ms13_journal_final_hashes.txt").read_text(encoding="utf-8").splitlines()
              if (m := PKGM.LINE.match(ln)) and m.group(3).startswith("figures/journal/")}
    assert got == listed                                    # an independent read of the hash list text


@need_figures
def test_every_top_level_file_and_every_zip_is_in_the_manifest_with_the_right_hash(builds):
    a, _ = builds
    man = {}
    for ln in (a / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        h, _, p = ln.partition("  ")
        man[p] = h
    have = sorted(p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file())
    assert sorted(man) == [h for h in have if h != "MANIFEST.sha256"]
    assert len(man) == 19
    for p, h in man.items():
        assert _sha(a / p) == h, p
    assert PKGM.INNER in man and all(f"{f}_journal_files.zip" in man for f in PKGM.figure_groups(ENTS))


@need_figures
def test_documents_in_the_package_equal_the_repository(builds):
    a, _ = builds
    for d in PKGM.DOC_FILES:
        assert _sha(a / d) == _sha(ROOT / d), d


@need_figures
def test_the_zips_readme_has_no_doi_version_or_date_and_says_how_to_check(builds):
    a, _ = builds
    t = (a / "DATA_README.md").read_text(encoding="utf-8")
    assert t.encode("utf-8") == PKGM.README_ZIPS.format(repo=PKGM.REPO_URL).encode("utf-8")
    _check_no_doi_version_date(t)
    assert "13 zip files" in t and "MANIFEST_inner.sha256" in t and "Expand-Archive" in t
    assert "Muscle artifact cannot be ruled out" in t and "No causal, clinical or consciousness claim is made." in t
    assert "planned" in t and "not created" in t            # the stale lines stay in the hashed documents and the README says so (G3)
    assert "no DOI, no publication date and nothing about any journal decision" in t


@need_figures
def test_the_verify_mode_accepts_a_fresh_build_and_rejects_a_changed_one(builds, tmp_path):
    a, _ = builds
    assert PKGM.verify_zips(a) == 0
    import shutil
    c = tmp_path / "c"
    shutil.copytree(a, c)
    (c / "LICENSE-DATA.md").write_bytes(b"changed")
    assert PKGM.verify_zips(c) == 1


def test_the_old_mode_text_is_unchanged_and_still_has_no_zip_wording():
    assert "not zipped" in PKGM.README and "13 zip files" not in PKGM.README
    assert PKGM.DEST == Path(r"C:\dev\_zenodo_data_package")


# ---- the final folder (outside the repository) ------------------------------------------------------------------------------------------------
@need_final
def test_the_final_folder_verifies_and_has_20_files():
    assert PKGM.verify_zips(FINAL) == 0
    assert len([p for p in FINAL.rglob("*") if p.is_file()]) == 20


@need_final
def test_the_final_folder_readme_has_no_doi_version_or_date():
    _check_no_doi_version_date((FINAL / "DATA_README.md").read_text(encoding="utf-8"))
