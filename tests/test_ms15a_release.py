"""MS15a (sub-step 18, DL-736 C7): the release files exist and say what the user ruled on 2026-11-10.

Reads files only (and `git tag -l`, read-only). Nothing is written, run or tagged. UNVERIFIED items stay UNVERIFIED: the CFF and Zenodo schemas are not
checked (no validator, no internet); the files are parsed as YAML and JSON only.
"""
import importlib.util
import json
import re
import subprocess
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
FIGURES = ["F1", "F2", "F3", "F4a", "F4b", "F5", "F5c", "F6", "FS1", "FS2", "FS3", "FS4", "FS5"]


def _text(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _tags() -> list[str]:
    out = subprocess.run(["git", "tag", "-l"], cwd=REPO, capture_output=True, text=True, check=True)
    return sorted(out.stdout.split())


TAGS_AT_IMPORT = _tags()


def test_license_is_mit_with_holder_and_year():
    t = _text("LICENSE")
    assert t.startswith("MIT License\n")
    assert "Copyright (c) 2026 Daniel Voldman" in t
    assert "Permission is hereby granted, free of charge, to any person obtaining a copy" in t
    assert 'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND' in t


def test_citation_cff_parses_and_has_author_orcid_email_license():
    c = yaml.safe_load(_text("CITATION.cff"))
    assert c["cff-version"] == "1.2.0"
    assert c["type"] == "software"
    a = c["authors"][0]
    assert a["family-names"] == "Voldman" and a["given-names"] == "Daniel"
    assert a["email"] == "daniel.voldman@proton.me"
    assert a["affiliation"] == "Independent Researcher"
    assert a["orcid"] == "https://orcid.org/0009-0005-3409-8944"
    assert c["license"] == "MIT"


def test_citation_cff_has_no_doi_or_version_key():
    c = yaml.safe_load(_text("CITATION.cff"))
    assert "doi" not in c and "version" not in c
    assert "date-released" not in c            # not yet assigned (a comment in the file says so)


def test_zenodo_json_agrees_with_citation_cff():
    z = json.loads(_text(".zenodo.json"))
    c = yaml.safe_load(_text("CITATION.cff"))
    a = c["authors"][0]
    cr = z["creators"][0]
    assert cr["name"] == f"{a['family-names']}, {a['given-names']}"
    assert a["orcid"].endswith("/" + cr["orcid"])
    assert cr["affiliation"] == a["affiliation"]
    assert z["upload_type"] == "software" and z["license"] == "mit"
    assert z["title"] == c["title"]
    assert "doi" not in z and "version" not in z


def test_license_data_names_cc_by_4():
    t = _text("LICENSE-DATA.md")
    assert "CC-BY 4.0" in t
    assert "https://creativecommons.org/licenses/by/4.0/" in t
    assert "Daniel Voldman" in t
    assert "UNVERIFIED" in t                   # the legal text is not reproduced; the file says so


def test_readme_has_licence_citation_and_claim_limits_and_no_placeholder():
    t = _text("README.md")
    assert "## Licence" in t and "## How to cite" in t
    assert "CITATION.cff" in t and "LICENSE-DATA.md" in t
    assert "Claim limits" in t
    assert "Muscle artifact cannot be ruled out" in t
    assert "To be filled" not in t
    assert "No funding received." in t
    assert "The author declares no conflicts of interest." in t


def test_make_all_exists_and_has_no_absolute_path():
    p = REPO / "scripts" / "make_all.ps1"
    assert p.is_file()
    t = p.read_text(encoding="ascii")
    assert not re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]", t), "a drive-letter path"
    assert "\\\\" not in t, "a UNC path (two backslashes)"
    assert "/Users/" not in t and "\\Users\\" not in t
    assert "$PSScriptRoot" in t                # the repository folder comes from the script's own folder


def _load_figure_map_script():
    spec = importlib.util.spec_from_file_location("ms15a_write_figure_map", REPO / "scripts" / "ms15a_write_figure_map.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_figure_map_lists_exactly_the_13_figures_with_hashes_of_the_hash_list():
    m = _load_figure_map_script()
    order, info, drafts = m.parse_hash_list(_text("docs/ms13_journal_final_hashes.txt"))
    assert order == FIGURES
    t = _text("docs/figure_map.md")
    sec1 = t.split("## 1. The 13 journal figures", 1)[1].split("## 2.", 1)[0]
    rows1 = [r for r in sec1.splitlines() if r.startswith("| ") and not r.startswith("| ---") and not r.startswith("| Journal figure")]
    assert [r.split("|")[1].strip() for r in rows1] == FIGURES
    sec2 = t.split("## 2. Journal files with full SHA-256", 1)[1].split("## 3.", 1)[0]
    rows2 = [[c.strip().strip("`") for c in r.strip().strip("|").split("|")] for r in sec2.splitlines()
             if r.startswith("| ") and not r.startswith("| ---") and not r.startswith("| Figure")]
    expected = [[fid, kind, path, sha] for fid in order for kind, path, sha in info[fid]["files"]]
    assert rows2 == expected                   # every hash equals the hash list; none is retyped
    assert len(rows2) == 100 and len(drafts) == 77      # 100 journal files (FS2 to FS5 have one caption) and 77 draft files: 177 in all
    raw = _text("docs/ms13_journal_final_hashes.txt")
    assert all(f"{r[3]}  " in raw and r[2] in raw for r in rows2)       # an independent look: each hash and path is in the hash list text
    sec3 = t.split("## 3. Drawn-data digests", 1)[1].split("## 4.", 1)[0]
    digests = re.findall(r"^\| (\S+) \| `([0-9a-f]{64})` \|$", sec3, re.M)
    assert digests == [(fid, info[fid]["digest"]) for fid in order]
    sec4 = t.split("## 4. The eleven draft figures", 1)[1]
    rows4 = re.findall(r"^\| (\S+) \| `([^`]+)` \| `([0-9a-f]{64})` \|$", sec4, re.M)
    assert rows4 == [(fig, path, sha) for fig, path, sha in drafts]


def test_draft_hashes_of_the_hash_list_equal_the_manifest():
    m = _load_figure_map_script()
    _, _, drafts = m.parse_hash_list(_text("docs/ms13_journal_final_hashes.txt"))
    manifest = {}
    for line in _text("docs/ms13_figure_manifest.csv").splitlines()[1:]:
        fig, path, sha, _dl = line.split(",")
        manifest[path] = sha
    assert drafts and all(manifest.get(path) == sha for _, path, sha in drafts)


def test_this_module_created_no_tag():
    assert _tags() == TAGS_AT_IMPORT            # `git tag -l` is read only; no test of this file creates, moves or deletes a tag
