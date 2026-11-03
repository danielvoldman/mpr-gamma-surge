"""MS13 13q: tests of the independent recomputation (scripts/ms13_independent.py, scripts/ms13_independent_compare.py; docs/ms13_independent_plan.md section 5).
Exact comparisons throughout. They read the stored results under results/ (git-ignored) and skip if those are absent; nothing under results/ is written or altered
(the altered-value test works on a temporary copy of five small stored files)."""
import ast
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from mprsurge import config as C

ROOT = C.repo_root()
RES = ROOT / "results"
F5_FILES = ("A9/a9_regime_map_v2.parquet", "A9/a9_subgrid_agreement.parquet", "ms10/eval/ms10_eval.json", "ms10/10g/record_classes.tsv", "A11/a11_robustness.csv", "S8/S8_head/S8_head_0003_7dfd3c05b40c.json")
pytestmark = pytest.mark.skipif(not all((RES / p).is_file() for p in F5_FILES), reason="stored inputs under results/ are absent")
FORBIDDEN = ("figures", "figprov", "claim_labels", "captions", "nordlie", "style")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    if str(ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ind():
    return _load("ms13_independent")


@pytest.fixture(scope="module")
def cmpmod(ind):
    return _load("ms13_independent_compare")


def test_static_imports_of_the_module_name_no_figure_code():
    tree = ast.parse((ROOT / "scripts" / "ms13_independent.py").read_text(encoding="utf-8"))
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names += [(node.module or "") + "." + a.name for a in node.names] + [node.module or ""]
    bad = [n for n in names if n.startswith("mprsurge.plotting") or any(f in n.split(".") for f in FORBIDDEN)]
    assert bad == [], bad


def test_dynamic_import_graph_has_no_figure_code():
    code = ("import sys; sys.path.insert(0, r'%s'); import ms13_independent, json; "
            "bad = sorted(m for m in sys.modules if m.startswith('mprsurge.plotting') or m.split('.')[-1] in %r); print(json.dumps(bad))") % (str(ROOT / "scripts"), FORBIDDEN)
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, cwd=str(ROOT), env={**os.environ, "PYTHONPATH": str(ROOT / "src")}, check=True)
    assert out.stdout.strip().splitlines()[-1] == "[]", out.stdout


def _snapshot(path: Path):
    snap = {}
    for dp, _dn, fn in os.walk(path):
        for f in fn:
            p = Path(dp) / f
            st = p.stat()
            snap[str(p)] = (st.st_size, st.st_mtime_ns)
    return snap


def test_compute_writes_nothing(ind):
    before, docs_before = _snapshot(RES), _snapshot(ROOT / "docs")
    rows = ind.compute()
    assert len(rows) > 400
    assert _snapshot(RES) == before
    assert _snapshot(ROOT / "docs") == docs_before


def test_f5_counts_are_reproduced(ind):
    byid = {r["id"]: r["value"] for r in ind.compute(figures=["F5"])}
    assert (byid["F5.map1_surge"], byid["F5.map1_none"], byid["F5.map1_cells"]) == (760, 140, 900)
    assert (byid["F5.map2_surge"], byid["F5.map2_cells"], byid["F5.map2_none"]) == (296, 325, 29)
    assert (byid["F5.d24_agree"], byid["F5.sub_n"], byid["F5.d24_categories"], byid["F5.p1_agree"]) == (97, 225, 118, 173)


def test_altered_stored_value_in_a_temporary_copy_is_reported_not_equal(ind, cmpmod, tmp_path):
    import pandas as pd
    for rel in F5_FILES:
        dst = tmp_path / "results" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RES / rel, dst)
    a9 = pd.read_parquet(tmp_path / "results" / F5_FILES[0])
    i = a9.index[(a9["map"].astype(str) == "1") & (a9["class"] == "D-tr")][0]
    a9.loc[i, "class"] = "D-none"                                  # one stored class word altered, in the copy only
    a9.to_parquet(tmp_path / "results" / F5_FILES[0])
    rows = ind.compute(root=tmp_path, figures=["F5"], series_res=RES)       # the 52 large S9 series are read from the real results (read only)
    by = {r["id"]: r for r in rows}
    assert by["F5.map1_surge"]["value"] == 759 and by["F5.map1_none"]["value"] == 141
    res = cmpmod.compare(rows, cmpmod.drawn_sets(["F5"]))
    eq = {r["id"]: r["equal"] for r in res}
    assert sorted(i for i, e in eq.items() if e == "no") == ["F5.map1_none", "F5.map1_pct", "F5.map1_surge"]
    assert eq["F5.map2_surge"] == "yes"
    assert [i for i, e in eq.items() if e == "unresolved"] == []


def test_real_comparison_has_no_disagreement(ind, cmpmod):
    rows = ind.compute()
    figs = sorted({r["figure"] for r in rows}, key=ind.FIGURES.index)
    res = cmpmod.compare(rows, cmpmod.drawn_sets(figs))
    assert [r["id"] for r in res if r["equal"] in ("no", "unresolved")] == []
    assert {r["figure"] for r in res} == set(ind.FIGURES)


def test_printed_digit_rule(cmpmod):
    p = cmpmod.printed_same
    assert p(84.44444, "84.4") and not p(84.46, "84.4") and p(760, "760") and not p(759, "760")
    assert p(1.2258e-08, "1.2e-8") and not p(1.3e-08, "1.2e-8") and p("S-sus", "S-sus") and p([120.0], "120")
    assert cmpmod.same(float("nan"), float("nan"), None) and not cmpmod.same(1.0, 1.0 + 1e-9, None) and cmpmod.same(1.0, 1.0 + 1e-13, ("rel", 1e-12))
