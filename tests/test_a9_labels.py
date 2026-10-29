"""MS13 13k (DL-482): the A9 failure labels printed in F6 are defined once in docs/claim_limit_labels.md (second table); the module equals it and each source wording is
verbatim in its source (docs/plan.md for a to f, the decision log for g and h). Exact comparisons."""
from mprsurge import config as C
from mprsurge.plotting import figures as FG
from mprsurge.plotting.claim_labels import A9_LABELS

ROOT = C.repo_root()


def _rows():
    rows = {}
    for ln in (ROOT / "docs" / "claim_limit_labels.md").read_text(encoding="utf-8").splitlines():
        if ln.startswith("| Label (") and ln.endswith("|"):
            c = [x.strip() for x in ln.strip("|").split(" | ")]
            rows[c[0][len("Label ("):-1]] = (c[1], c[2], c[3], tuple(x.strip() for x in c[4].split(",")))
    return rows


def test_module_equals_the_second_table_exactly():
    rows = _rows()
    assert sorted(rows) == list("abcdefgh")
    assert {k: (v[2], v[3]) for k, v in rows.items()} == A9_LABELS


def test_each_source_wording_is_verbatim_in_its_source():
    plan = (ROOT / "docs" / "plan.md").read_text(encoding="utf-8")
    log = (ROOT / "docs" / "decision_log.md").read_text(encoding="utf-8")
    for k, (src, wording, short, dls) in _rows().items():
        assert wording in (plan if k in "abcdef" else log), k
        assert dls and all(d.startswith("DL-") for d in dls)


def test_label_c_short_form_is_the_end_of_the_ms9_e_3_short_form_and_f6_prints_the_listed_short_forms():
    from mprsurge.plotting.claim_labels import CLAIM_LIMIT_LABELS as CL
    assert A9_LABELS["c"][0] == "a flag, not a demonstrated cause" and CL["MS9(e)-3"][0] == "label (c) is " + A9_LABELS["c"][0]
    assert FG.F6_LABEL_WORDS == {k: v[0] for k, v in A9_LABELS.items()}
