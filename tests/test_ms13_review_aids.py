"""MS13 13n: tests of scripts/ms13_check_hashes.py and scripts/ms13_audit.py (DL-493).

Every test works on temporary copies (tmp_path); the real figures, scripts, log and manifest are only read. Exact comparisons: a hash, a count or a string is equal or it is not.
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


H = _load("ms13_check_hashes")
A = _load("ms13_audit")


def _tree_digest(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def _cp(src_rel: str, dst_root: Path):
    d = dst_root / src_rel
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / src_rel, d)


# ---- hash checker ------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture()
def hroot(tmp_path):
    for _, rel in H.expected_files():
        _cp(rel, tmp_path)
    _cp(H.LOG, tmp_path)
    _cp(H.MANIFEST, tmp_path)
    return tmp_path


def _check(root):
    return H.check(root, (root / H.LOG).read_bytes().decode("utf-8"), H.read_manifest(root / H.MANIFEST))


def test_manifest_lists_every_expected_file_once_and_has_the_columns():
    rows = H.read_manifest(ROOT / H.MANIFEST)
    assert tuple(rows[0].keys()) == H.COLUMNS
    assert [(r["figure"], r["file"]) for r in rows] == H.expected_files()
    assert len(rows) == len(H.FIGURES) * 9 + len(H.SHARED)
    assert all(len(r["sha256"]) == 64 for r in rows)


def test_the_real_files_match_the_manifest_and_the_log_is_checked_without_a_write(hroot):
    before = _tree_digest(hroot)
    assert _check(hroot) == []
    assert H.main(["--root", str(hroot)]) == 0
    assert _tree_digest(hroot) == before                                       # check mode writes nothing


def test_checker_detects_a_changed_byte(hroot):
    p = hroot / "figures/F5/F5_caption.txt"
    b = bytearray(p.read_bytes())
    b[0] ^= 1
    p.write_bytes(bytes(b))
    problems = _check(hroot)
    assert len(problems) == 1 and problems[0].startswith("CHANGED figures/F5/F5_caption.txt")
    assert H.main(["--root", str(hroot)]) == 1


def test_checker_detects_an_unlogged_hash(hroot):
    p = hroot / "figures/F6/F6.png"
    p.write_bytes(p.read_bytes() + b"x")                                       # a new file whose hash the log does not carry
    rows = H.read_manifest(hroot / H.MANIFEST)
    for r in rows:
        if r["file"] == "figures/F6/F6.png":
            r["sha256"] = H.sha256_file(p)                                     # manifest follows the file, the log does not
    problems = H.check(hroot, (hroot / H.LOG).read_bytes().decode("utf-8"), rows)
    assert len(problems) == 1 and problems[0].startswith("NOT-LAST-LOGGED figures/F6/F6.png")


def test_checker_detects_a_file_without_any_logged_hash(hroot):
    log = hroot / H.LOG
    log.write_bytes(log.read_bytes().replace(b"FS3_params.csv", b"FS3_paramz.csv"))          # the log no longer names the file
    problems = _check(hroot)
    assert [p.split(":")[0] for p in problems] == ["UNLOGGED figures/FS3/FS3_params.csv"]


def test_checker_detects_a_missing_file(hroot):
    (hroot / "scripts/fig_FS2.py").unlink()
    problems = _check(hroot)
    assert problems == ["MISSING scripts/fig_FS2.py"]


def test_checker_detects_a_file_the_manifest_does_not_list(hroot):
    (hroot / "figures/F1/stray.txt").write_text("x", encoding="utf-8")
    assert _check(hroot) == ["UNLISTED figures/F1/stray.txt: not in the manifest"]


def test_write_manifest_changes_only_the_manifest_and_reproduces_it(hroot):
    before = _tree_digest(hroot)
    assert H.main(["--root", str(hroot), "--write-manifest"]) == 0
    after = _tree_digest(hroot)
    assert {k for k in after if after[k] != before.get(k)} <= {H.MANIFEST}
    assert after[H.MANIFEST] == before[H.MANIFEST]                             # the committed manifest is what the script writes now


def test_log_parser_reads_working_and_first_hash_only():
    log = "## DL-001 x\nfigures/F9/F9.pdf working " + "a" * 64 + " (LF-normalised " + "b" * 64 + ")\n## DL-002 y\nF9.pdf " + "c" * 64 + "\n"
    e = H.parse_log(log)
    assert H.logged_hashes(e, "figures/F9/F9.pdf") == [(1, "a" * 64), (2, "c" * 64)]
    assert H.last_logged(e, "figures/F9/F9.pdf") == (2, "c" * 64)
    assert H.logged_hashes(e, "figures/FS9/FS9.pdf") == []                      # FS9.pdf is not F9.pdf


# ---- audit -------------------------------------------------------------------------------------------------------------------------------------

FIG = "FS3"


@pytest.fixture()
def aroot(tmp_path):
    prov = json.loads((ROOT / f"figures/{FIG}/{FIG}_provenance.json").read_text(encoding="utf-8"))
    rels = [f"figures/{FIG}/{FIG}_provenance.json", f"figures/{FIG}/{FIG}_caption.txt", f"tests/test_fig_{FIG}.py", A.FIGURES_PY, "docs/claim_limit_labels.md",
            "docs/ms13_plan.md", "results/A11/a11_robustness.csv"] + [i["path"] for i in prov["inputs"]]
    rels += [o["path"] for o in prov["outputs"]] + [prov["script"]["path"]] + [m["path"] for m in prov["modules"]] + list(prov["configs"])
    for rel in sorted(set(rels)):
        _cp(rel, tmp_path)
    return tmp_path


def _flags(root):
    text, res = A.run(root, None, figs=(FIG,))
    return res[0]["flags"], res[0], text


def test_audit_reads_a_figure_and_writes_only_its_output_file(aroot):
    before = _tree_digest(aroot)
    out = aroot / "docs/ms13_audit.md"
    text, res = A.run(aroot, out, figs=(FIG,))
    after = _tree_digest(aroot)
    assert {k for k in after if after[k] != before.get(k)} == {"docs/ms13_audit.md"}
    assert f"## {FIG}" in text and res[0]["n_inputs"] == len(json.loads((aroot / f"figures/{FIG}/{FIG}_provenance.json").read_text(encoding="utf-8"))["inputs"])


def test_audit_detects_a_literal_colour_in_the_drawing_code(aroot):
    base, _, _ = _flags(aroot)
    p = aroot / A.FIGURES_PY
    p.write_text(p.read_text(encoding="utf-8") + "\n\ndef _draw_FS3(d, draft):\n    import matplotlib.pyplot as plt\n    plt.plot([0], [0], color=\"#123456\", marker=\"o\", ms=5)\n", encoding="utf-8")
    flags, r, _ = _flags(aroot)
    new = [f for f in flags if f not in base]
    assert any("hex colour" not in f and "color='#123456'" in f for f in new) and any("marker='o'" in f for f in new) and any("ms=5" in f for f in new)


def test_audit_detects_a_claim_limit_id_missing_from_the_label_table(aroot):
    base, _, _ = _flags(aroot)
    p = aroot / f"figures/{FIG}/{FIG}_provenance.json"
    rec = json.loads(p.read_text(encoding="utf-8"))
    rec["claim_limits"].append("XX-C99")
    p.write_text(json.dumps(rec), encoding="utf-8")
    flags, r, _ = _flags(aroot)
    assert r["undefined"] == ["XX-C99"]
    assert f"{FIG}: claim-limit ID XX-C99 is not defined in docs/claim_limit_labels.md" in flags and "XX-C99" not in " ".join(base)


def test_audit_detects_a_changed_input(aroot):
    base, r0, _ = _flags(aroot)
    assert r0["input_diffs"] == []
    prov = json.loads((aroot / f"figures/{FIG}/{FIG}_provenance.json").read_text(encoding="utf-8"))
    victim = prov["inputs"][0]["path"]
    p = aroot / victim
    p.write_bytes(p.read_bytes() + b"\n")
    flags, r, _ = _flags(aroot)
    assert r["input_diffs"] == [(victim, "CHANGED")]
    assert f"{FIG}: input {victim} CHANGED against the provenance" in flags


def test_audit_detects_a_caption_string_its_test_requires(aroot):
    base, r0, _ = _flags(aroot)
    assert r0["required_missing"] == [] and len(r0["required"]["in"]) >= 5            # 13p (DL-505 T34): 5 since T27 (DL-501); removing one is still flagged below
    p = aroot / f"figures/{FIG}/{FIG}_caption.txt"
    p.write_text(p.read_text(encoding="utf-8").replace("NOT EVALUABLE", "n.e."), encoding="utf-8")
    flags, r, _ = _flags(aroot)
    assert r["required_missing"] == ["NOT EVALUABLE"]


def test_audit_reads_the_plan_table_and_the_label_table():
    labels = A.load_label_table(ROOT)
    assert "MS11-C7" in labels and "RB2 FAIL (plan label)" in labels and len(labels) == 35          # 13o (DL-496 T10): three plan labels added (DL-495)
    rows = A.load_plan_table(ROOT, labels)
    by = {r["id"]: r for r in rows if r["id"]}
    assert by["MS11-C7"]["figures"] == list(A.FIGURES) and by["MS12-C1"]["figures"] == ["F1", "F2", "F3", "F4", "F5", "F6"]
    assert by["MS9(e)-1"]["figures"] == ["F1", "F5", "F6", "FS3"] and by["DL-163-D1"]["figures"] == ["F1", "F4", "F5", "F6", "FS5"]
    assert A.canonical_id("RB1 FAIL (DL-319, DL-320)", labels) == "RB1 FAIL (plan label)"          # 13o (DL-496 T11): the table now has this plan label
