"""MS13 13j (DL-477): the claim-limit label table is defined once in docs/claim_limit_labels.md; the module the captions use equals it. Exact comparisons."""
from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS as CL

ROOT = C.repo_root()


def _table():
    rows = {}
    for ln in (ROOT / "docs" / "claim_limit_labels.md").read_text(encoding="utf-8").splitlines():
        if ln.startswith("| ") and not ln.startswith("| Label"):
            c = [x.strip() for x in ln.strip("|").split(" | ")]
            rows[c[0]] = (c[3], tuple(x.strip() for x in c[4].split(",")))
    return rows


def test_module_equals_the_table_exactly():
    assert _table() == CL


def test_every_id_a_figure_prints_is_defined_in_the_table():
    for ids in (FG.FS4_CLAIM_LIMITS, FG.FS5_CLAIM_LIMITS):
        assert set(ids) <= set(CL)


def test_each_short_form_is_a_verbatim_line_of_the_plan_section_5_table_with_sigma_ascii():
    plan = (ROOT / "docs" / "ms13_plan.md").read_text(encoding="utf-8").replace("σ", "sigma")
    for label, (short, dls) in CL.items():
        assert short in plan, label
        assert dls and all(d.startswith("DL-") for d in dls), label


def test_table_text_is_lf():
    assert b"\r" not in (ROOT / "docs" / "claim_limit_labels.md").read_bytes()
