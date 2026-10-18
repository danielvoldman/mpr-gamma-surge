"""8g (DL-203): the independent recomputation script does not use the modules it checks."""
import importlib.util
import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "recompute_ms8_independent.py"


def _load():
    spec = importlib.util.spec_from_file_location("recompute_ms8_independent", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_imports_neither_rb_eval_nor_rb_tables_nor_a7():
    src = SCRIPT.read_text(encoding="utf-8")
    imports = "\n".join(l for l in src.splitlines() if re.match(r"\s*(from|import)\s", l))
    for banned in ("rb_eval", "rb_tables", "a7", "rb_diag"):
        assert not re.search(rf"\b{banned}\b", imports), banned


def test_median_exclude_drops_missing_and_counts_them():
    m = _load()
    med, miss = m.median_exclude([1.0, None, 3.0, float("nan"), 2.0])
    assert med == 2.0 and miss == 2
    med, miss = m.median_exclude([None, None])
    assert med != med and miss == 2


def test_near_matches_grid_values_at_the_s5_tolerance():
    m = _load()
    assert m.near(56.234, 56.23) and not m.near(100.0, 177.8)
