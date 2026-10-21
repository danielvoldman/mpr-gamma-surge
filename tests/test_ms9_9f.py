"""MS9 9f: the D24 cell rule of scripts/report_ms9_9f.py on synthetic seed classes (M9-14: modal class, a tie is a disagreement)."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("report_ms9_9f", ROOT / "scripts" / "report_ms9_9f.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


def test_surge_subclasses_correspond_to_d_tr():
    assert all(R.corresponds("D-tr", c) for c in ("S+", "S-rel", "S-abs"))
    assert not R.corresponds("D-tr", "NS") and not R.corresponds("D-tr", "S-sus")
    assert R.corresponds("D-sus", "S-sus") and R.corresponds("D-none", "NS") and not R.corresponds("D-none", "S+")


def test_modal_class_agrees():
    r = R.cell_agreement("D-tr", ["S+"] * 6 + ["NS"] * 4)
    assert r["cell_agrees"] and not r["tie"] and r["n_seed_agree"] == 6 and not r["ge8"]


def test_tie_is_disagreement():
    r = R.cell_agreement("D-none", ["NS"] * 5 + ["S+"] * 5)
    assert r["tie"] and not r["cell_agrees"] and r["n_seed_agree"] == 5


def test_split_surge_subclasses_modal_raw_vs_category():
    seeds = ["S+"] * 3 + ["S-rel"] * 3 + ["S-abs"] * 2 + ["NS"] * 2
    r = R.cell_agreement("D-tr", seeds)
    assert r["tie"] and not r["cell_agrees"] and r["cat_agrees"] and r["n_seed_agree"] == 8 and r["ge8"]
