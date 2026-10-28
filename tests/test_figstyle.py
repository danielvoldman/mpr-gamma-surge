"""MS13 13c: style table, colour report, caption helper, Nordlie stage 2, tagged-build criteria check. No figure is built and nothing is simulated;
stand-in records and a temporary git repository exist only in these tests. Tolerances: every comparison is exact (set equality, string equality,
exception type and message) except the white-point sanity check of the colour conversion (abs 1e-2 in L*, a, b; a self-check of the constants, not
a pass line for any colour). The colour-difference report has NO pass line (UNVERIFIED criterion, docs/ms13_conventions.md section 11)."""
import csv
import hashlib
import json
import math
import shutil
import subprocess

import pytest

from mprsurge import config as C
from mprsurge import criteria as K
from mprsurge.analysis import ms11_eval
from mprsurge.plotting import captions as CAP
from mprsurge.plotting import figprov as F
from mprsurge.plotting import nordlie as N
from mprsurge.plotting import style as S

ROOT = C.repo_root()


def test_style_table_has_a_unique_marker_for_every_key():
    # exact: the key set equals the plan/code class set plus the named paths, controls and sources; markers are unique over ALL keys, (marker, linestyle)
    # pairs are unique, colours are unique (no two keys share a colour)
    assert set(S.keys("class")) == set(ms11_eval.CATEGORY)                          # class names come from the code (plan Table 2.1)
    assert set(S.keys("class")) == {"S+", "S-rel", "S-abs", "S-sus", "NS", "D-tr", "D-sus", "D-none"}
    assert {"P1", "P2", "P3", "P4a", "P4b", "P5"} <= set(S.keys("path")) and set(S.keys("control")) == {"NC1", "NC2", "NC3"}
    assert set(S.keys("source")) == {"mean_field", "network_agree", "network_disagree", "noise"}
    all_styles = list(S.STYLE.values())
    markers = [s.marker for s in all_styles]
    assert len(set(markers)) == len(markers), sorted(m for m in markers if markers.count(m) > 1)
    pairs = [(s.marker, s.linestyle) for s in all_styles]
    assert len(set(pairs)) == len(pairs)
    colours = [s.colour.lower() for s in all_styles]
    assert len(set(colours)) == len(colours)
    assert all(s.key == k for k, s in S.STYLE.items())
    assert S.get("S+") is S.STYLE["S+"]
    with pytest.raises(S.StyleError, match="no style for key"):
        S.get("S-unknown")


def test_colour_difference_report_is_written_and_has_no_pass_line(tmp_path):
    # report only: asserts that the files exist with every pair and every view as a finite number; asserts nothing about how large a difference is
    assert S.lab_of("#ffffff") == pytest.approx((100.0, 0.0, 0.0), abs=1e-2)         # self-check of the conversion constants
    assert S.lab_of("#000000") == pytest.approx((0.0, 0.0, 0.0), abs=1e-2)
    c, t = S.write_colour_report(tmp_path / "style")
    assert c.is_file() and t.is_file()
    with open(c, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    n = len(S.STYLE)
    assert tuple(rows[0]) == S.REPORT_COLUMNS and len(rows) == n * (n - 1) // 2
    assert {frozenset((r["key_a"], r["key_b"])) for r in rows} == {frozenset((a, b)) for a in S.STYLE for b in S.STYLE if a < b}
    assert all(math.isfinite(float(r[f"dE76_{v}"])) for r in rows for v in S.VIEWS)
    text = t.read_text(encoding="utf-8")
    assert "REPORT ONLY" in text and all(v in text for v in ("deuteranopia", "protanopia", "greyscale"))
    assert "pass" in text.lower() and "fail" not in text.lower()


ROWS = [
    {"panel": "a", "section": "", "name": "rtol", "key": "solver.rtol", "value": 1e-10, "units": "", "status": "",
     "source_run_id": "stand_in_0000_aaaaaaaaaaaa", "source_config_hash12": "aaaaaaaaaaaa"},
    {"panel": "a", "section": "", "name": "N", "key": "network.N", "value": 10000, "units": "", "status": "UNVERIFIED",
     "source_run_id": "stand_in_0000_aaaaaaaaaaaa", "source_config_hash12": "aaaaaaaaaaaa"},
    {"panel": "b", "section": "", "name": "a|b \\ c", "key": "foo.bar", "value": None, "units": "ms", "status": "",
     "source_run_id": "stand_in_0000_aaaaaaaaaaaa", "source_config_hash12": "aaaaaaaaaaaa"},
    {"panel": "b", "section": "Custom", "name": "rtol", "key": "solver.rtol", "value": 1e-10, "units": "", "status": "",
     "source_run_id": "stand_in_0000_aaaaaaaaaaaa", "source_config_hash12": "aaaaaaaaaaaa"},
]
SPEC = {"band_primary_hz": [25, 100], "taper": "hann", "window_s": 2.0}


def _record(path, config):
    r = {"name": "stand_in_0000_aaaaaaaaaaaa", "status": "ok", "config_hash12": "aaaaaaaaaaaa", "seed": {"root_seed": 7, "spawn_key": [0, 1]},
         "git": {"commit": "0" * 40, "dirty": False}, "criteria_sha256": None, "solver": {"method": "DOP853", "rtol": 1e-10}, "config": config}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(r), encoding="utf-8")
    return path


CONFIG = {"solver": {"method": "DOP853", "rtol": 1e-10}, "network": {"N": 10000}, "foo": {"bar": None}}


def test_caption_raises_on_a_missing_take_home_message():
    ok = dict(claim_limit_ids=["G6-D1"], params_rows=ROWS)
    for bad in (None, "", "   ", 3):
        with pytest.raises(CAP.CaptionError, match="take_home"):
            CAP.build_caption("F3", take_home=bad, **ok)
    with pytest.raises(CAP.CaptionError, match="take_home"):
        CAP.build_caption("F3", claim_limit_ids=["G6-D1"])                               
    assert CAP.build_caption("F3", take_home="A message.", **ok).text.startswith("F3. A message.")


def test_caption_raises_on_a_missing_claim_limit_list():
    ok = dict(take_home="A message.", params_rows=ROWS)
    for bad in (None, [], (), "G6-D1", [""], ["G6-D1", " "]):
        with pytest.raises(CAP.CaptionError, match="claim_limit_ids"):
            CAP.build_caption("F3", claim_limit_ids=bad, **ok)
    cap = CAP.build_caption("F3", claim_limit_ids=["G6-D1", "MS12-C1"], **ok)             # prints exactly the IDs it is given, none added
    assert cap.claim_limits == ("G6-D1", "MS12-C1") and "Claim limits: G6-D1, MS12-C1." in cap.text


def test_caption_values_equal_params_csv_values(tmp_path):
    out = tmp_path / "F3_params.csv"
    F.write_params_csv(out, [dict(r) for r in ROWS], "F3")
    with open(out, newline="", encoding="utf-8") as fh:
        csv_rows = list(csv.DictReader(fh))
    expected, seen = [], set()                                                           # independent of the helper: built from the csv text itself
    for r in csv_rows:
        item = (r["panel"], r["key"], r["value"])
        if item not in seen:
            seen.add(item)
            expected.append(f"[{r['panel']}] {r['key']}={r['value']}")
    cap = CAP.build_caption("F3", take_home="A message.", claim_limit_ids=["G6-D1"], params_rows=ROWS, spectrogram=SPEC, symbol_keys=["S+", "NC1"])
    assert cap.parameter_string == "; ".join(expected)
    assert cap.spectrogram_string == 'band_primary_hz=[25, 100]; taper="hann"; window_s=2.0'
    assert f"Parameters: {cap.parameter_string}." in cap.text and f"Spectrogram: {cap.spectrogram_string}." in cap.text
    assert "Symbols: S+ = circle; NC1 = plus." in cap.text
    with pytest.raises(S.StyleError):
        CAP.build_caption("F3", take_home="A message.", claim_limit_ids=["G6-D1"], symbol_keys=["nope"])


def test_nordlie_stage2_reproduces_every_params_csv_row(tmp_path):
    rec = _record(tmp_path / "results" / "rec.json", CONFIG)
    script = tmp_path / "fig_STAND.py"
    script.write_text("# stand-in\n", encoding="utf-8")
    out = tmp_path / "figures" / "F3"
    F.write_figure_provenance("F3", script=script, inputs=[rec], params_rows=[dict(r) for r in ROWS], out_dir=out, root=ROOT)
    params, prov = out / "F3_params.csv", out / "F3_provenance.json"
    stage1 = N.read_params_csv(params)
    assert len(stage1) == len(ROWS)
    digest = N.write_nordlie(params, prov, out / "F3_nordlie.md", root=ROOT)
    text = (out / "F3_nordlie.md").read_text(encoding="utf-8")
    assert hashlib.sha256(text.encode("utf-8")).hexdigest() == digest
    assert "stand_in_0000_aaaaaaaaaaaa aaaaaaaaaaaa" in text and F.P.sha256_file(prov) in text                # linked by run ID, config hash and provenance
    back = N.parse_nordlie(text)
    key = lambda r: tuple(r[c] for c in F.PARAMS_COLUMNS)
    want = [{**r, "section": N.section_of(r)} for r in stage1]
    assert sorted(map(key, back)) == sorted(map(key, want))                              # every row, every column, exact (section filled by the mapping)
    assert {r["key"]: r["section"] for r in back if r["panel"] == "a"} == {"solver.rtol": N.SECTION_ORDER[4], "network.N": "Populations"}
    assert [r["section"] for r in back if r["key"] == "foo.bar"] == [N.UNASSIGNED_SECTION]
    assert [r["section"] for r in back if r["panel"] == "b" and r["key"] == "solver.rtol"] == ["Custom"]      # a section set in stage 1 is kept
    assert [r["name"] for r in back if r["key"] == "foo.bar"] == ["a|b \\ c"]                                # escaping round trip
    bad = params.read_text(encoding="utf-8").replace("10000", "20000")
    (out / "bad_params.csv").write_text(bad, encoding="utf-8")
    with pytest.raises(N.NordlieError, match="does not agree"):
        N.render_nordlie(out / "bad_params.csv", prov, root=ROOT)


def _git(repo, *a):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True)


def test_tagged_build_verifies_frozen_criteria_through_the_loader_and_fails_on_a_changed_hash(tmp_path):
    # a temporary repository holds a COPY of the criteria file; the real file and tag are never touched
    repo = tmp_path / "repo"
    (repo / "configs").mkdir(parents=True)
    crit = repo / "configs" / "robustness_criteria.yaml"
    crit.write_bytes(K.lf_bytes((ROOT / "configs" / "robustness_criteria.yaml").read_bytes()))
    (repo / ".gitignore").write_text("results/\nfigures/\n")
    sha = hashlib.sha256(crit.read_bytes()).hexdigest()
    assert sha == K.verify_frozen_criteria(ROOT)["sha256"]                               # the copy is the frozen text
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "x")
    _git(repo, "tag", "-a", "criteria-frozen", "-m", f"criteria frozen (test copy)\n\nSHA-256 of the LF text of configs/robustness_criteria.yaml (test): {sha}\n")
    rec = _record(tmp_path / "outside" / "rec.json", CONFIG)
    script = tmp_path / "outside" / "fig_STAND.py"
    script.write_text("# stand-in\n", encoding="utf-8")
    build = lambda: F.write_figure_provenance("F3", script=script, inputs=[rec], params_rows=[dict(r) for r in ROWS], root=repo, tag_build=True)
    prov = build()                                                                       # unchanged copy, clean tree: verified through the loader
    assert prov["criteria_sha256"] == sha and prov["draft"] is False and prov["criteria_tag"] == "criteria-frozen"
    shutil.rmtree(repo / "figures")
    crit.write_bytes(crit.read_bytes() + b"# changed\n")                                 # changed hash, uncommitted
    with pytest.raises(K.CriteriaError, match="SHA-256 mismatch"):
        build()
    assert not (repo / "figures").exists()
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "change criteria")                                   # changed hash, committed: tree clean, hash still fails
    with pytest.raises(K.CriteriaError, match="SHA-256 mismatch"):
        build()
    assert not (repo / "figures").exists()
    assert K.verify_frozen_criteria(ROOT)["sha256"] == "c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05"
