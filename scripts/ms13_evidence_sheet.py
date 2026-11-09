"""MS13 13v (DL-703 V5, DL-708): write docs/ms13_evidence_sheet.md, one section per journal figure, from stored files. Nothing is typed in by hand except the fixed text of the closing sections.

  .venv/Scripts/python.exe scripts/ms13_evidence_sheet.py --verify V.txt --compare C.txt --junit J.xml

Reads (read only): docs/ms13_journal_final_hashes.txt (paths, full SHA-256 of PNG, TIFF, PDF, captions, alt text, supplement, source data, build commit, drawn-data digest, the eleven draft files),
the draft digest files figures/<draft>/<draft>_drawn_data_sha256.txt, the output of scripts/ms13_verify_export.py (V.txt) and scripts/ms13_independent_compare.py (C.txt) of this step,
docs/ms13_independent_results.csv (draft rows per draft figure), the captions (the paragraphs 'Failed checks.' and 'Limits.' are copied word for word), the audit tables docs/ms13_13t11_alt_table.md (P2)
and docs/ms13_13t10_o2_table.md (O2), the JUnit file of the figure tests (status of the audit tests), docs/ms13_export_checklist.json (status counts) and `git tag -l`.
The hashes are copied from the final hash list, never recomputed here; tests/test_ms13_13v.py compares them again with the files on disk. A value the files do not give is written UNVERIFIED.
"""
import argparse
import collections
import csv
import json
import re
import subprocess
import xml.etree.ElementTree as ET

from mprsurge.config import repo_root

IDS = "F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5".split()
DRAFT = {"F4a": "F4", "F4b": "F4", "F5c": "F5"}
OPEN = {
    "F1": ["44 (accepted by the user: S-sus has no recorded reason)", "49", "56", "40 (draft label only; the journal text is correct)"],
    "F2": ["46 (accepted by the user: journal captions follow the data; the draft stays)", "49", "56"],
    "F3": ["49", "55 (EPS extra differs between builds)", "56"],
    "F4a": ["49", "56", "57 (UNVERIFIED reading of the duration floor)"],
    "F4b": ["49", "50 (legend scope)", "52 (caption at 650 of 650 words)", "56", "57 (UNVERIFIED reading of the duration floor)"],
    "F5": ["49", "51 (N written 1e3 in the alt text)", "55", "56"],
    "F5c": ["48 (accepted by the user: control durations are in the source data)", "49", "51", "55", "56", "57 (UNVERIFIED reading of the duration floor)"],
    "F6": ["49", "56"],
    "FS1": ["49", "54 (the STOP of DL-646, not resolved)", "55", "56"],
    "FS2": ["49", "56"],
    "FS3": ["49", "56"],
    "FS4": ["49", "56"],
    "FS5": ["49", "53 (answered in 13v: no 'not run' cell in (a); the caption was corrected)", "56"],
}
CASE_ALL = ["45 (accepted by the user: the full captions carry what the short captions leave out)"]


def paragraphs(text: str):
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def table_rows(path, header_start):
    rows, on = [], False
    for ln in open(path, encoding="utf-8"):
        if ln.startswith(header_start):
            on = True
            continue
        if on:
            if not ln.startswith("|"):
                if rows:
                    break
                continue
            if set(ln.strip()) <= set("|- "):
                continue
            rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", required=True)
    ap.add_argument("--compare", required=True)
    ap.add_argument("--junit", required=True)
    ap.add_argument("--out", default="docs/ms13_evidence_sheet.md")
    a = ap.parse_args(argv)
    root = repo_root()
    # final hash list
    sections, cur, drafts = {}, None, []
    in_drafts = False
    for ln in (root / "docs/ms13_journal_final_hashes.txt").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (F\d[a-c]?|FS\d) \(journal main version", ln)
        if m:
            cur, in_drafts = m.group(1), False
            sections[cur] = {"files": [], "commit": None, "digest": None}
            continue
        if ln.startswith("## The eleven draft files"):
            cur, in_drafts = None, True
            continue
        if ln.startswith("## ") and in_drafts:
            in_drafts = False
        if cur and ln.startswith("built from commit:"):
            sections[cur]["commit"] = ln.split(":", 1)[1].strip()
        elif cur and ln.startswith("drawn-data digest:"):
            sections[cur]["digest"] = ln.split(":", 1)[1].strip()
        elif cur:
            m = re.match(r"^([0-9a-f]{64})  (.+?)\s{2,}(\S+)$", ln)
            if m:
                sections[cur]["files"].append(m.groups())
        elif in_drafts:
            m = re.match(r"^([0-9a-f]{40,64})\s+(\S+)\s+(\S+)$", ln)
            if m:
                drafts.append(m.groups())
    assert sorted(sections) == sorted(IDS), sorted(sections)
    vlines = open(a.verify, encoding="utf-8").read().splitlines()
    comp = {}
    for ln in open(a.compare, encoding="utf-8"):
        m = re.match(r"^(JOURNAL|SHORT) rows (\w+): (\d+) quantities searched in the \w+ (?:journal|short) caption, (\d+) equal, (\d+) not equal, (\d+) unresolved", ln)
        if m:
            comp[(m.group(1), m.group(2))] = tuple(int(x) for x in m.groups()[2:])
    draft_rows = collections.defaultdict(collections.Counter)
    with open(root / "docs/ms13_independent_results.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            draft_rows[r["figure"]][r["equal"]] += 1
    jun = {}
    for tc in ET.parse(a.junit).getroot().iter("testcase"):
        bad = any(c.tag in ("failure", "error") for c in tc)
        sk = any(c.tag == "skipped" for c in tc)
        jun[tc.get("name")] = "failed" if bad else ("skipped" if sk else "passed")
    p2 = table_rows(root / "docs/ms13_13t11_alt_table.md", "| figure | panel | claim | value in the alt text")
    o2 = table_rows(root / "docs/ms13_13t10_o2_table.md", "| figure | claim | value in text")
    tags = subprocess.run(["git", "tag", "-l"], capture_output=True, text=True, cwd=root, check=True).stdout.split()
    figtags = [t for t in tags if t.startswith("fig-")]
    ck = json.loads((root / "docs/ms13_export_checklist.json").read_text(encoding="utf-8"))
    ckc = collections.Counter(i["status"] for i in ck["items"])
    out = ["# MS13 evidence sheet (13v, DL-703 V5, DL-708)", "",
           "Written for: the owner and reviewer who close MS13, and the author of the paper. Written by scripts/ms13_evidence_sheet.py from stored files: the hashes are copied from docs/ms13_journal_final_hashes.txt "
           "(tests/test_ms13_13v.py compares them again with the files on disk); counts come from the output of scripts/ms13_verify_export.py and scripts/ms13_independent_compare.py run on the committed build in 13v "
           "(read only, no rebuild); the captions' failed-check and limit paragraphs are copied word for word. A value that no file gives is written UNVERIFIED. Nothing is tagged, pushed or uploaded.", "",
           "Build commit of every journal figure: " + ", ".join(sorted({s['commit'] for s in sections.values()})) + ". Later commits are documentation, the audit module, and in 13v the wording fix of the FS5 caption (DL-705, DL-706; "
           "FS5 caption and supplement only; the PNG, TIFF and PDF are unchanged).", ""]
    for fid in IDS:
        s = sections[fid]
        d = DRAFT.get(fid, fid)
        vf = [ln for ln in vlines if ln.startswith(fid + " ")]
        cv = collections.Counter(re.match(r"^\S+ .+?: (PASS|FAIL|MANUAL)\b", ln).group(1) for ln in vf if re.match(r"^\S+ .+?: (PASS|FAIL|MANUAL)\b", ln))
        dg = [ln for ln in vf if ln.startswith(fid + " digest:")]
        ar = [ln for ln in vf if ln.startswith(fid + " arrays:")]
        ddig = (root / f"figures/{d}/{d}_drawn_data_sha256.txt").read_text(encoding="utf-8").split()[0]
        out += [f"## {fid}", "", f"Draft audit copy: {d} (figures/{d}/); the journal files are the main versions.", "", "| file | path | SHA-256 (full) |", "|---|---|---|"]
        out += [f"| {lab} | {path} | {h} |" for h, lab, path in s["files"]]
        out += ["", f"- Build commit: {s['commit']}.",
                f"- Drawn-data digest of the journal figure: {s['digest']}; draft {d}: {ddig}; equal: {'yes' if s['digest'] == ddig else 'NO'}. Verifier: {dg[0].split(': ', 1)[1] if dg else 'UNVERIFIED (no line)'}; {ar[0].split(': ', 1)[1] if ar else 'UNVERIFIED (no arrays line)'}.",
                f"- Independent comparison (this run): journal caption {comp.get(('JOURNAL', fid), 'UNVERIFIED')} and short caption {comp.get(('SHORT', fid), 'UNVERIFIED')} as (quantities, equal, not equal, unresolved); "
                f"draft rows of {d} (shared by the parts of a split figure): equal {draft_rows[d].get('yes', 0)}, other {sum(v for k, v in draft_rows[d].items() if k != 'yes')} (rows without a comparison are not counted as equal).",
                f"- Verifier rows for {fid} (this run): {cv.get('PASS', 0)} PASS, {cv.get('FAIL', 0)} FAIL, {cv.get('MANUAL', 0)} MANUAL (the MANUAL row is the colour-vision check of the user)."]
        capfile = next((p for h, lab, p in s["files"] if lab.startswith("caption full") or lab.startswith("caption (single)")), None)
        txt = (root / capfile).read_text(encoding="utf-8")
        fp = [p for p in paragraphs(txt) if p.startswith("Failed checks.") or p.startswith("Limits.")]
        out += ["", f"Failed checks shown and claim limits kept (word for word from {capfile}):", ""]
        out += ["> " + p.replace("\n", " ") for p in fp] or ["> UNVERIFIED (no such paragraph found)"]
        p2f = [r for r in p2 if r and r[0] == fid]
        o2f = [r for r in o2 if r and r[0] == fid]
        out += ["", "Audits that cover it:",
                f"- N2 numbers typed into the builders (docs/ms13_13t9_n2_audit.md; by file, not by figure): test test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value {jun.get('test_n2_every_typed_number_has_a_rule_and_every_stored_number_equals_the_stored_value', 'UNVERIFIED')} in this run.",
                f"- O2 superlatives and ranges (docs/ms13_13t10_o2_table.md): {len(o2f)} stored-value claims listed for {fid}, {sum(1 for r in o2f if r[-1] == 'yes')} equal; test test_o2_every_constant_in_a_superlative_range_or_bound_is_stored_ruled_or_reviewed_with_* {[v for k, v in jun.items() if k.startswith('test_o2_every_constant')] or 'UNVERIFIED'} in this run.",
                f"- P2 alt text (docs/ms13_13t11_alt_table.md): {len(p2f)} executable checks for {fid}, {sum(1 for r in p2f if r[-1] == 'yes')} equal; test test_p2_every_alt_text_claim_equals_the_source_data {jun.get('test_p2_every_alt_text_claim_equals_the_source_data', 'UNVERIFIED')} in this run.",
                "- Verifier rows: see the count above; the full table is printed by scripts/ms13_verify_export.py.",
                "", "Open close items that touch it (docs/ms13_close_items.md, section L): " + "; ".join(CASE_ALL + OPEN[fid]) + ".", ""]
    out += ["## Tags", ""]
    if figtags:
        out += ["Tags made: " + ", ".join(figtags) + "."]
    else:
        out += ["none made; 13u makes them when the user says tag, journal files as main versions, drafts as audit copies. Tags that exist in the repository: " + ", ".join(tags) + " (none of them is a figure tag)."]
    out += ["", "## Drafts", "", "The eleven draft files (audit copies; byte-identical to docs/ms13_figure_manifest.csv; copied from docs/ms13_journal_final_hashes.txt). The pre-check of 13v (scripts/ms13_check_hashes.py: 104 manifest rows, 0 problems) and the verifier (7 draft files per figure, 0 differ) were run on them.", "",
            "| hash | draft | path |", "|---|---|---|"]
    out += [f"| {h} | {fig} | {p} |" for h, fig, p in drafts]
    out += ["", "## What this evidence does not show", "",
            "- The colour-vision check of the 13 final PNGs: MANUAL, the user's task; the verifier row reads MANUAL for every figure (R2).",
            "- Muscle artifact cannot be ruled out as a source of the gamma-band signal: the study is a model, and nothing here tests that reading against recordings.",
            f"- Checklist status after the 13v re-check (docs/ms13_export_checklist.json, docs/ms13_13v_checklist_recheck.md): {dict(ckc)}. Items marked 'not re-verified' were not proven again in 13v (a human look, a review record, or no item-specific check was found); their earlier passing status rests on the recorded evidence of the 13t steps only. G2b-fs1-test-point carries the unresolved STOP of DL-646.",
            "- The 'name-matched tests' class of re-verified items is weaker than a verifier row: a test named for the ruling code passed, but whether it covers the whole claim of the item was not checked item by item.",
            "- UNVERIFIED glosses and defaults remain as marked in the captions and the close items (for example item 57, the layout limits of the journal export, the PCJ figure rules, the colour-vision reading); none was sourced in 13v.",
            "- The panel-by-panel image content was not looked at again in 13v (no figure was built or opened); the visual reviews of 13t are recorded in docs/ms13_13t*_review.md.",
            "- The EPS extras differ between builds (item 55); they are not part of the hash list.", ""]
    (root / a.out).write_text("\n".join(out), encoding="utf-8", newline="\n")
    print("wrote", a.out, len(out), "lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
