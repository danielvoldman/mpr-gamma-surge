"""MS13 13v (DL-703, DL-708): tests of the evidence sheet, the final hash list, the FS5 'not run' fix, the checklist re-check and the close documents.

They read the recorded journal build under figures/journal/ and the stored results under results/, and skip if those are absent. Nothing is built.
"""
import csv
import hashlib
import json
import re

import pytest

from mprsurge import config as C
from mprsurge.plotting import jfs5

ROOT = C.repo_root()
HASHES = ROOT / "docs/ms13_journal_final_hashes.txt"
SHEET = ROOT / "docs/ms13_evidence_sheet.md"
CLOSE = ROOT / "docs/ms13_close.md"
RECHECK = ROOT / "docs/ms13_13v_checklist_recheck.md"
CHECK = ROOT / "docs/ms13_export_checklist.json"
ITEMS = ROOT / "docs/ms13_close_items.md"
A8 = ROOT / "results/A8/a8_sensitivity.csv"
IDS = "F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5".split()
have_build = (ROOT / "figures/journal/F1/F1_journal.png").is_file() and (ROOT / "figures/journal/supplement/FS5_supplement.md").is_file()

LINE = re.compile(r"^([0-9a-f]{64})  (.+?)\s{2,}(\S+)$")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def hash_list():
    out = {}
    for ln in HASHES.read_text(encoding="utf-8").splitlines():
        m = LINE.match(ln)
        if m and m.group(3).startswith("figures/journal/"):
            out[m.group(3)] = m.group(1)
    return out


def test_the_final_hash_list_lists_all_13_figures_with_nine_files_or_eight():
    lst = hash_list()
    for fid in IDS:
        mine = [p for p in lst if f"/{fid}/" in p or p.split("/")[-1].startswith(f"{fid}_")]
        assert any(p.endswith(f"{fid}_journal.png") for p in mine) and any(p.endswith(f"{fid}_journal.tiff") for p in mine) and any(p.endswith(f"{fid}_journal.pdf") for p in mine), fid
        assert any(p.endswith(f"{fid}_alt_text.txt") for p in mine) and any(p.endswith(f"{fid}_source_data.csv") for p in mine), fid


@pytest.mark.skipif(not have_build, reason="recorded journal build absent")
def test_every_hash_of_the_final_list_equals_its_file_on_disk():
    bad = [(p, h) for p, h in hash_list().items() if sha(ROOT / p) != h]
    assert not bad, bad


@pytest.mark.skipif(not (have_build and SHEET.is_file()), reason="recorded build or evidence sheet absent")
def test_the_evidence_sheet_hashes_equal_the_final_list_and_the_files_on_disk():
    lst = hash_list()
    seen = {}
    for ln in SHEET.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (.+?) \| (figures/journal/\S+) \| ([0-9a-f]{64}) \|$", ln)
        if m:
            seen[m.group(2)] = m.group(3)
    assert set(seen) == set(lst), (sorted(set(lst) - set(seen))[:3], sorted(set(seen) - set(lst))[:3])
    for p, h in seen.items():
        assert h == lst[p], p
        assert h == sha(ROOT / p), p
    for fid in IDS:
        assert re.search(rf"^## {fid}$", SHEET.read_text(encoding="utf-8"), re.M), fid
    txt = SHEET.read_text(encoding="utf-8")
    for sec in ("## Tags", "## Drafts", "## What this evidence does not show"):
        assert sec in txt


@pytest.mark.skipif(not SHEET.is_file(), reason="evidence sheet absent")
def test_the_evidence_sheet_says_that_no_figure_tag_exists_and_lists_eleven_drafts():
    txt = SHEET.read_text(encoding="utf-8")
    # 13u (DL-725): the sheet is committed before the 13 tags are made; it names them, says what a tag holds, and does not claim more than that
    tags_sec = txt.split("## Tags", 1)[1].split("## Drafts", 1)[0]
    for i in "F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5".split():
        assert f"fig-{i}-v1" in tags_sec, i
    assert "committed BEFORE the tags were created" in tags_sec and "NOT in a tagged tree" in tags_sec and "Peer Community Journal" in tags_sec
    assert "the drafts are audit copies and are not tagged" in tags_sec
    drafts = re.findall(r"^\| [0-9a-f]{40,64} \| (F\d|FS\d) \| (figures/\S+) \|$", txt, re.M)
    assert len({d for d, _ in drafts}) == 11
    for _, p in drafts:
        assert (ROOT / p).is_file(), p


def test_not_run_clause_is_pure_and_keeps_the_old_text_when_a_cell_is_not_run():
    new = jfs5.not_run_clause(390, 0, 71)
    assert "all 390 cells hold a class and none is 'not run'" in new and "71 records" in new and "are in (c), marked *" in new
    assert "does not fit" not in new
    old = jfs5.not_run_clause(390, 3, 71)
    assert "'not run' where the variant's window does not fit" in old and "3 cells" in old


@pytest.mark.skipif(not A8.is_file(), reason="stored A8 table absent")
def test_the_stored_table_has_no_not_run_cell_in_fs5_a_and_71_records_in_c():
    rows = list(csv.DictReader(open(A8, newline="", encoding="utf-8")))
    nr = [r for r in rows if r["cls"] == "not_run"]
    assert len(nr) == 71
    assert not [r for r in nr if r["dataset"] == "synthetic"]
    assert {(r["dataset"], r["mode"], r["variant"]) for r in nr} == {("stored_S4_devalle", "D", "window_x2")}


@pytest.mark.skipif(not have_build, reason="recorded journal build absent")
def test_the_fs5_caption_and_supplement_carry_the_corrected_clause_and_not_the_old_one():
    old = "and 'not run' where the variant's window does not fit"
    for p in ("figures/journal/FS5/FS5_journal_caption.txt", "figures/journal/supplement/FS5_supplement.md"):
        t = (ROOT / p).read_text(encoding="utf-8")
        assert old not in t, p
        assert "none is 'not run'" in t, p
    cap = (ROOT / "figures/journal/FS5/FS5_journal_caption.txt").read_text(encoding="utf-8")
    assert "are counted as not run, not as unchanged" in cap          # the (c) sentence is true and stays


@pytest.mark.skipif(not RECHECK.is_file(), reason="re-check table absent")
def test_the_recheck_table_has_every_checklist_item_and_no_unproven_passing_item():
    data = json.loads(CHECK.read_text(encoding="utf-8"))
    txt = RECHECK.read_text(encoding="utf-8")
    for it in data["items"]:
        assert f"| {it['id']} |" in txt, it["id"]
        rc = it["recheck_13v"]
        if it["status"] == "passing":
            assert rc["result"].startswith("re-verified") and rc["proof"], it["id"]
        else:
            assert it["status"] in ("MANUAL", "not re-verified", "failing"), it["id"]
    g2b = [i for i in data["items"] if i["id"] == "G2b-fs1-test-point"]
    assert g2b and all(i["status"] == "not re-verified" for i in g2b)
    cvd = [i for i in data["items"] if i["id"].startswith("R2-cvd")]
    assert cvd and all(i["status"] == "MANUAL" for i in cvd)
    assert not [i for i in data["items"] if i["status"] == "failing"]


def test_the_close_items_mark_44_45_46_48_accepted_and_49_to_57_open():
    t = ITEMS.read_text(encoding="utf-8")
    sec = t[t.index("## L. Status at the end of 13v"):]
    for n in (44, 45, 46, 48):
        assert re.search(rf"^{n}\. ACCEPTED", sec, re.M), n
    for n in range(49, 58):
        assert re.search(rf"^{n}\. OPEN", sec, re.M), n
    assert "has no recorded reason in the stored results" in sec and "UNVERIFIED" in sec


@pytest.mark.skipif(not CLOSE.is_file(), reason="close document absent")
def test_the_close_document_names_every_failure_and_the_user_tasks():
    t = CLOSE.read_text(encoding="utf-8")
    for needle in ("RB1 FAIL", "RB2 FAIL", "RB3(a)", "RB3(b)", "RB6 solver FAIL", "181 ms", "RB6 network f_pk FAIL", "RB9(b) FAIL", "4.391 Hz", "0.5 Hz", "G7 NOT PASSED",
                   "D24 noisy subgrid FAILED", "97 of 225", "43.1 percent", "203", "sigma check", "colour-vision", "backup folder", "tag decision", "Zenodo", "UNVERIFIED", "13u", "MS14", "MS15"):
        assert needle in t, needle
    for n in (44, 45, 46, 48, 49, 57):
        assert re.search(rf"\b{n}\b", t), n
