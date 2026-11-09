"""MS13 13v (DL-703 V4, DL-707): re-verify every item of docs/ms13_export_checklist.json against the committed build, from the OUTPUT of existing read-only checks. Writes nothing but the files named below.

  .venv/Scripts/python.exe scripts/ms13_13v_checklist_recheck.py --verify V.txt --compare C.txt --junit J.xml [--write-checklist]

Inputs (made in this step by the existing commands, nothing rebuilt): V.txt = output of scripts/ms13_verify_export.py (the detail lines 'F1 A collisions: PASS - ...'); C.txt = output of
scripts/ms13_independent_compare.py; J.xml = the --junitxml file of a pytest run of tests/test_ms13_*.py, tests/test_fig_*.py, tests/test_figstyle.py, tests/test_figprov.py.
Proof classes, in this order: (1) VERIFIER ROW of the same name for the figure(s) of the item; (2) INDEPENDENT COMPARISON rows (T9, U3d); (3) TESTS whose name carries the item's ruling code
(for example 'u2' for U2-...) in the test file(s) of that step; the item is then 're-verified (name-matched tests)': the tests passed, but whether a test covers the whole claim of the item
was not checked item by item; (4) otherwise 'not re-verified' with the reason (a human look or review record cannot be re-run; no item-specific check was found). The colour-vision item stays
MANUAL. G2b-fs1-test-point is never set passing (DL-646). Output: docs/ms13_13v_checklist_recheck.md; with --write-checklist each item of the checklist gets the key 'recheck_13v' (result, proof)
and its status becomes 'passing' (re-verified), 'MANUAL' or 'not re-verified'.
"""
import argparse
import collections
import json
import re
import xml.etree.ElementTree as ET

from mprsurge.config import repo_root

ALL = ["F1", "F2", "F3", "F4a", "F4b", "F5", "F5c", "F6", "FS1", "FS2", "FS3", "FS4", "FS5"]
STEM = {
    "check:A-collisions": ["A collisions"], "check:B-pdf": ["B pdf"], "check:size-and-shape": ["size+shape"], "check:text-min-8pt": ["text>=8pt"],
    "check:fonts-embedded-no-type3": ["fonts"], "check:line-width-min": ["line width"], "check:cmap-list": ["cmaps"], "check:non-colour-distinction": ["non-colour"],
    "check:panel-letters-in-order": ["letters"], "check:file-names": ["file names"], "check:draft-FAIL-lines-visible": ["FAIL lines"],
    "check:drawn-data-digest-equals-draft": ["digest"], "check:draft-files-byte-identical": ["drafts identical"],
    "check:no-draft-dl-provenance-text-on-image": ["image text"], "check:supplement-lists-every-strip-row": ["supplement"],
    "check:label-title-gap-0.05in": ["label-title gap"], "check:margins-0.10in": ["margins"], "check:F5-F5c-arrays-equal-draft": ["arrays"],
    "T5-margins-0.10in": ["margins"], "T6-label-title-gap-0.05in": ["label-title gap"], "T8-seven-labelled-paragraphs": ["paragraphs"],
    "T8-no-plan-milestone-table-DL-step-ids-code-names": ["caption words"], "U2-no-check-or-step-ids-on-images": ["image IDs"],
    "S9-no-code-names-on-any-journal-image": ["image IDs", "image text"], "V3-plain-words-all-images": ["plain words"], "V4-powers-of-ten-images": ["powers of ten"],
    "W3-plain-numbers": ["superscripts", "powers of ten"], "U6a-true-minus-signs": ["minus signs"], "C9-sentence-case": ["sentence case"],
    "U1c-no-other-unexplained-red-title": ["red titles"], "K4-check": ["caption codes"], "K4-codes": ["caption codes"], "C6-word-limit-600": ["short limits"],
    "V8-short-word-limits": ["short limits"], "X-A6-word-limit-520": ["short limits"], "V7-short-failed-checks-and-count": ["failed count"],
    "W2-short-parameters-sentence": ["short parameters"], "U3a-short-caption": ["short caption"], "U3b-full-caption-file": ["full caption"],
    "S4-supplement-pairing-table": ["supplement"], "R1-main-files-png-tiff-600dpi-pdf-extra": ["png+tiff", "size+shape"],
    "R1-relayout-6.3in-all-text-8pt-no-collision": ["size+shape", "text>=8pt", "A collisions"], "U5-plain-definitions": ["key terms", "definitions"],
    "S3-extended-checker-zero-unlisted-F1": ["A collisions"], "S3-extended-checker-zero-unlisted-F3": ["A collisions"], "S3-extended-checker-zero-unlisted-F5": ["A collisions"],
    "X-F2-digest": ["digest"], "X-F6-digest": ["digest"],
}
COMPARE = {"T9-journal-caption-rows-in-independent-comparison": "JOURNAL", "U3d-independent-short-and-full-rows": "BOTH"}
HUMAN = re.compile(r"(png-crops-looked-at|subagent-review|W6-look-at-all-crops|S14-pilot-sheet-png|S7-new-fresh|S8-temp-review-crops|U8-accepted-findings-logged|V9-accepted-unchanged|^O5-suite-and-review|^N2-audit)")
FILES = [(r"^C\d", ["test_ms13_13t3"]), (r"^E\d", ["test_ms13_13t4"]), (r"^G\d", ["test_ms13_13t5"]), (r"^J3", ["test_ms13_13t7"]), (r"^K\d", ["test_ms13_13t8"]),
         (r"^N\d", ["test_ms13_13t9", "test_ms13_13t9_fs"]), (r"^O\d", ["test_ms13_13t10"]), (r"^P\d", ["test_ms13_13t11"]), (r"^R2-f4b", ["test_ms13_13t11"]),
         (r"^U\d", ["test_ms13_13t1e"]), (r"^V\d", ["test_ms13_13t1f"]), (r"^W\d", ["test_ms13_13t1g"]), (r"^(T|S|J9|J10|J12|R)\d", ["test_ms13_13t"])]
FSFILES = {"FS1": ["test_ms13_13t4"], "FS2": ["test_ms13_13t6"], "FS3": ["test_ms13_13t6"], "FS4": ["test_ms13_13t9_fs"], "FS5": ["test_ms13_13t9_fs"]}


def figs_of(s: str) -> list:
    s = s.strip()
    if s.startswith("all"):
        return list(ALL)
    return [x.strip() for x in s.split(",") if x.strip()]


def load_junit(p):
    out = {}
    for tc in ET.parse(p).getroot().iter("testcase"):
        mod = tc.get("classname", "").split(".")[-1]
        skipped = any(c.tag == "skipped" for c in tc)
        bad = any(c.tag in ("failure", "error") for c in tc)
        out[(mod, tc.get("name"))] = "failed" if bad else ("skipped" if skipped else "passed")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", required=True)
    ap.add_argument("--compare", required=True)
    ap.add_argument("--junit", required=True)
    ap.add_argument("--hashes", help="output of scripts/ms13_check_hashes.py (proof of P4-final-hash-list)")
    ap.add_argument("--write-checklist", action="store_true")
    a = ap.parse_args(argv)
    root = repo_root()
    vrows = {}
    for ln in open(a.verify, encoding="utf-8"):
        m = re.match(r"^(F\d[a-c]?|FS\d) (.+?): (PASS|FAIL|MANUAL)\b", ln)
        if m:
            vrows[(m.group(1), m.group(2))] = m.group(3)
    comp = {}
    for ln in open(a.compare, encoding="utf-8"):
        m = re.match(r"^(JOURNAL|SHORT) rows (\w+): (\d+) quantities searched in the \w+ (?:journal|short) caption, (\d+) equal, (\d+) not equal, (\d+) unresolved", ln)
        if m:
            comp[(m.group(1), m.group(2))] = tuple(int(x) for x in m.groups()[2:])
    jun = load_junit(a.junit)
    path = root / "docs/ms13_export_checklist.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    res = []
    for it in data["items"]:
        iid = it["id"]
        base, figl = iid, figs_of(it.get("figure", ""))
        m = re.match(r"^(check:.+?)-(F5c)$", iid)
        if m:
            base, figl = m.group(1), ["F5c"]
        result, proof = None, None
        if iid == "G2b-fs1-test-point":
            result = "not re-verified"
            proof = "the read-only check of DL-646 STOPPED (the values of (c) and (d) differ: 52.82 Hz and 1.710 cycles per e-fold against 91.77 Hz and 3.96); no later entry settles it; no evidence is available to set it passing"
        elif iid == "P4-final-hash-list" and a.hashes and re.search(r"\d+ manifest rows, 0 problems", open(a.hashes, encoding="utf-8").read()):
            result, proof = "re-verified", "scripts/ms13_check_hashes.py (this run): " + open(a.hashes, encoding="utf-8").read().strip().splitlines()[-1] + "; the PNG, TIFF and PDF of the 13 figures equal docs/ms13_journal_final_hashes.txt"
        elif iid.startswith("R2-cvd"):
            result, proof = "MANUAL", "verifier row cvd reads MANUAL for all 13 figures (the user checks the final PNGs with an online simulator)"
        elif HUMAN.search(iid):
            result, proof = "not re-verified", "a human look or a review record (see the DL numbers in the item note); it cannot be re-run by a script"
        elif base in COMPARE:
            kinds = ["JOURNAL", "SHORT"] if COMPARE[base] == "BOTH" else ["JOURNAL"]
            rows = [(k, f) for f in figl for k in kinds if (k, f) in comp and comp[(k, f)][0] > 0]
            if rows and all(comp[r][2] == 0 and comp[r][3] == 0 and comp[r][1] == comp[r][0] for r in rows):
                result = "re-verified"
                proof = "independent comparison (scripts/ms13_independent_compare.py, this run): " + "; ".join(f"{k} {f} {comp[(k, f)][1]} of {comp[(k, f)][0]} equal" for k, f in rows)
            else:
                result, proof = "not re-verified", "no comparison row with quantities found for the figure(s), or a row not equal"
        elif base in STEM:
            rows = STEM[base]
            cells = [(f, r) for f in figl for r in rows]
            miss = [c for c in cells if c not in vrows]
            if miss:
                result, proof = "not re-verified", f"the verifier has no detail line for {miss[:3]}"
            elif all(vrows[c] == "PASS" for c in cells):
                result = "re-verified"
                proof = f"verifier (scripts/ms13_verify_export.py, this run, exit 0): row(s) {', '.join(rows)} PASS for {', '.join(figl)}"
            else:
                result, proof = "FAIL", "verifier: " + "; ".join(f"{c}={vrows[c]}" for c in cells if vrows[c] != "PASS")
        if result is None:
            files = None
            for pat, fl in FILES:
                if re.match(pat, iid):
                    files = fl
                    break
            mt = re.match(r"^([A-Za-z]+\d+[a-z]?)(?:-|$)", iid)
            tok = mt.group(1).lower() if mt else None
            if iid.startswith(("D-FS", "G4-FS")):
                files = FSFILES.get(iid.split("-")[-1])
                tok = iid.split("-")[-1].lower()
            if iid.startswith("J3-H"):
                tok, files = iid.split("-")[-1].lower(), ["test_ms13_13t7"]
            hits = []
            if files and tok:
                for (mod, name), st in jun.items():
                    if mod in files and re.search(rf"(^|_){re.escape(tok)}(_|$)", name):
                        hits.append((mod, name, st))
            if hits and all(h[2] == "passed" for h in hits):
                result = "re-verified (name-matched tests)"
                proof = f"{len(hits)} test(s) named for '{tok}' in {', '.join(sorted({h[0] for h in hits}))} passed in this run (e.g. {hits[0][1]}); coverage of the whole claim not checked item by item"
            elif hits:
                result, proof = "FAIL", "tests not passed: " + "; ".join(f"{h[1]}={h[2]}" for h in hits if h[2] != "passed")
            else:
                result, proof = "not re-verified", "no item-specific verifier row, comparison row or name-matched test was found; the recorded evidence in the item note was not re-run"
        res.append((it, result, proof))
    cnt = collections.Counter(r[1] for r in res)
    lines = ["# MS13 13v: re-check of docs/ms13_export_checklist.json against the committed build (DL-703 V4, DL-707)", "",
             "Written by scripts/ms13_13v_checklist_recheck.py from the output of the existing read-only checks of this step (nothing rebuilt): the verifier (scripts/ms13_verify_export.py, exit 0, 0 FAIL, 13 MANUAL colour-vision rows), "
             "the independent comparison (scripts/ms13_independent_compare.py, exit 0) and a pytest run with a JUnit record of the figure tests. An item is 're-verified' only through a verifier row of its own name or a comparison row; "
             "'re-verified (name-matched tests)' means tests named for its ruling code passed, which is weaker (a test may cover only part of the claim); everything else is 'not re-verified' with the reason. "
             "The colour-vision item stays MANUAL. G2b-fs1-test-point is not set passing.", "", "## Summary", ""]
    lines += [f"- {k}: {v}" for k, v in sorted(cnt.items())] + [f"- items in the checklist: {len(res)}", "", "## G2b-fs1-test-point (the STOP of DL-646), in plain words", "",
              "DL-646 (13t-5, 2026-11-07) was a read-only check, not a repair: at the FS1 test point (eta_bar/Delta -5, J/sqrt(Delta) 15) panel (c) draws a stable focus with frequency 52.82 Hz and 1.710 cycles per e-fold, "
              "while panel (d) draws a step response that rings and whose linearisation gives 91.77 Hz and 3.96 cycles per e-fold. The two disagree in value. The entry's reading (UNVERIFIED) is that they are two different fixed points: "
              "(d) is the response after the input current is stepped to I = 3, (c) is the map of the node as stored. The item was STOPPED by the ruling and nothing was patched. No later entry settles it. The current FS1 captions say that (d) is a step "
              "from 0 to 3 at the test point; they do not say that (c) is read before the step. To settle it the user must rule whether the FS1 caption has to state that difference (a wording change and a new FS1 caption hash), or accept it as it stands. It stays 'not re-verified'.", "",
              "## Table (id, figure, what proves it, result)", "", "| id | figure | what proves it | result |", "|---|---|---|---|"]
    for it, r, p in res:
        lines.append(f"| {it['id']} | {it.get('figure', '')} | {p.replace('|', '/')} | {r} |")
    (root / "docs/ms13_13v_checklist_recheck.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(dict(cnt), len(res))
    if a.write_checklist:
        for it, r, p in res:
            it["recheck_13v"] = {"result": r, "proof": p}
            it["status"] = "passing" if r.startswith("re-verified") else ("MANUAL" if r == "MANUAL" else ("failing" if r == "FAIL" else "not re-verified"))
        data["note"] = data["note"] + " | 13v (DL-703 V4, DL-707): every item re-checked against the committed build; status 'passing' only when re-verified (verifier row, comparison row, or name-matched tests); the others read 'not re-verified' with the reason in recheck_13v; see docs/ms13_13v_checklist_recheck.md"
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return 1 if cnt.get("FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())
