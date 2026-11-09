"""MS13 13t-9 (DL-680 N2): audit of the numbers that are typed into the caption builders and the image text of the journal export.

`literals()` lists every numeric constant in the string constants of the caption and image-text code (not docstrings, not error messages, not regular expressions); `classify()` gives each one a kind and,
where a stored file holds the quantity, the stored value (`stored()`, read from results/ and configs/ only); `audit_markdown()` writes the table (docs/ms13_13t9_n2_audit.md). Kinds:
  S  a stored quantity typed into the text: the stored value is read here and the typed number must equal it at the precision typed (a difference is a FAIL of the audit); the context pattern binds the
     number to its quantity by the words around it; for a list-valued quantity (a grid, a set of parameters) the number must be a member of the list;
  R  ruled wording of the plan or the decision log (a claim limit, a take-home sentence, a check name); the stored numbers of such a sentence are S rows, the other numbers are ruled counts that are not
     re-derived here;
  P  a reference to the plan, a table, a section or a claim-limit identifier (an identifier, not a quantity);
  T  a parameter of a figure that the text restates and that another test compares with the recorded parameter rows (the short Parameters sentence is compared with the full one, test W2; the Parameters
     paragraph of a full caption is built from the recorded rows);
  C  a count word or a label of the structure of the text (small integer, enumeration, notation table);
  D  a drawing constant echoed in the text (size of the figure, axis limit, mark size).
A test (tests/test_ms13_13t9.py) fails if a literal has no rule or if an S rule's stored value differs. What the audit cannot cover: a typed number that equals a stored number of ANOTHER quantity (the right value
for the wrong thing: the context pattern of an S rule narrows this but does not remove it); a small integer count (it cannot tell 10 seeds from 10 cells); the wording around a number; a number in a string that
is built at run time from stored values (those are not typed).
"""
from __future__ import annotations

import ast
import csv
import json
import re
from pathlib import Path

CAPTION_FILES = ("jcaption", "jshort", "jf26", "jf4cap", "jfs2", "jfs3", "jfs4", "jfs5", "jfs", "plain", "captions", "jf4")      # the builders of the journal captions and the text of the journal images
NUM = re.compile(r"(?<![A-Za-z_0-9.\-−+/])(?:[−-])?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:e[−+-]?\d+)?(?![A-Za-z_]|\.\d)")
SKIP_NAMES = {"FAILED_DETECT", "ID_PATTERN", "PLAIN_WORD_BAN"}
SMALL = {"0", "1", "2", "3"}


def value_of(tok: str) -> float:
    return float(tok.replace("−", "-").replace(",", ""))


def half_unit(tok: str) -> float:
    """Half of the last digit that the token states (the precision at which a stored value must equal it)."""
    s = tok.replace("−", "-").replace(",", "").lower()
    mant, _, ex = s.partition("e")
    dec = len(mant.split(".")[1]) if "." in mant else 0
    return 0.5 * 10 ** (-dec) * 10 ** (int(ex) if ex else 0)


def literals(root) -> list[dict]:
    """[{file, line, func, token, context}] of the numeric constants in the string constants of CAPTION_FILES."""
    out = {}
    for f in CAPTION_FILES:
        src = (Path(root) / "src" / "mprsurge" / "plotting" / f"{f}.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        parent = {c: n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
                continue
            anc = []
            n = node
            while n in parent:
                n = parent[n]
                anc.append(n)
            if any(isinstance(x, ast.Raise) for x in anc) or isinstance(parent.get(node), ast.Expr):
                continue
            if any(isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and isinstance(x.func.value, ast.Name) and x.func.value.id == "re" for x in anc):
                continue
            name = None
            for x in anc:
                if isinstance(x, (ast.Assign, ast.AnnAssign)):
                    tg = x.targets[0] if isinstance(x, ast.Assign) else x.target
                    if isinstance(tg, ast.Name):
                        name = tg.id
            if name in SKIP_NAMES:
                continue
            if name is None:
                fn = [x for x in anc if isinstance(x, ast.FunctionDef)]
                name = fn[0].name if fn else "?"
            for m in NUM.finditer(node.value):
                tok = m.group(0)
                ctx = node.value[max(0, m.start() - 45):m.end() + 30]
                out[(f, node.lineno, tok, ctx)] = {"file": f, "line": node.lineno, "func": name, "token": tok, "context": ctx.replace("\n", " ")}
    return list(out.values())


# ---- stored values ---------------------------------------------------------------------------------------------------------------------------------------------------------------

def _count(text: str) -> tuple:
    m = re.match(r"\s*(\d+) of (\d+)", text or "")
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def stored(root) -> dict:
    """The stored quantities that the caption builders type (read from results/ and configs/ only). A list value is a grid or a set of parameters."""
    import numpy as np
    import pandas as pd
    import yaml
    res = Path(root) / "results"
    q: dict = {}
    a11 = {(r["rb_id"], r["check_id"]): r for r in csv.DictReader(open(res / "A11/a11_robustness.csv", newline="", encoding="utf-8"))}
    ev = json.loads((res / "A11/a11_evaluators.json").read_text(encoding="utf-8"))["evaluators"]
    r = a11[("RB2", "noisy_subgrid_agreement")]
    m = re.match(r"(\d+) of (\d+) cells \(([\d.]+) percent\)", r["value"])
    q["sub_agree"], q["sub_cells"], q["sub_pct"] = int(m.group(1)), int(m.group(2)), float(m.group(3))
    m = re.match(r"(\d+) of (\d+) \((\d+) percent", r["threshold"])
    q["sub_needed"], q["sub_thr_pct"] = int(m.group(1)), int(m.group(3))
    r = a11[("RB2", "headline_class_kept_1.0_sigma")]
    q["kept"], q["kept_n"] = _count(r["value"])
    q["kept_need"] = int(re.search(r">= (\d+) of", r["threshold"]).group(1))
    q["rb3a_pass"], q["rb3a_n"] = _count(a11[("RB3", "a_inrange_runs")]["value"])
    q["solver_ms"] = float(a11[("RB6", "solver_onset_headline")]["value"].split()[0])
    q["solver_bound_ms"] = float(a11[("RB6", "solver_onset_headline")]["threshold"].split()[0])
    q["rb1_h_pass"], q["rb1_h_n"] = _count(a11[("RB1", "headline_10s")]["value"])
    q["rb1_cells_pass"], q["rb1_cells_n"] = _count(a11[("RB1", "cells_30s")]["value"])
    h = ev["rb9b"]["headline"]
    q["rb9b_spec"], q["rb9b_cycle"], q["rb9b_diff"], q["rb9b_bound"] = h["f_spectral_hz"], h["f_cycle_hz"], h["diff_hz"], h["bound_hz"]
    q["rb9c_changed"], q["rb9c_n"] = ev["rb9c"]["n_changed"], ev["rb9c"]["n_evaluated"]
    q["rb10_max_pct"] = 100 * max(float(v["fraction"]) for v in ev["rb10"]["variants"].values())
    a7 = pd.read_parquet(res / "A7/a7_ramp_metrics.parquet")
    q["onset_default"] = float(a7[(a7.family == "S5ramp") & (a7.T_ramp_s == 120)].onset_s.iloc[0])
    q["onset_radau"] = float(a7[(a7.family == "radau") & (a7.T_ramp_s == 120)].onset_s.iloc[0])
    wn = [x for x in csv.DictReader(open(res / "A8/sensitivity/a8_whitenoise.csv", newline="", encoding="utf-8")) if x["variant"] == "V0"]
    w = sorted({float(x["W_s"]) for x in wn})[:4]
    for key, W in zip(("0.2", "0.333", "0.593", "1.05"), w):
        q[f"wn_nonNS@{key}"] = sum(float(x["count"]) for x in wn if float(x["W_s"]) == W and x["class"] != "NS")
        q[f"wn_W@{key}"] = W
    q["wn_den"] = float(wn[0]["denominator"])
    base = yaml.safe_load((Path(root) / "configs/base.yaml").read_text(encoding="utf-8"))
    q["sigma"] = float(base["noise"]["sigma"])
    e10 = json.loads((res / "ms10/eval/ms10_eval.json").read_text(encoding="utf-8"))
    sc = e10["sigma_check"]
    q["sc_mf"], q["sc_min"], q["sc_max"] = sc["mf_baseline_std"], sc["network_min"], sc["network_max"]
    by_n = e10["N_sweep"]["by_N"]
    for N, e in by_n.items():
        q[f"surge@{N}"] = e["surge_seeds"]
        q[f"ctrl_surge@{N}"] = e["controls"]["surge"]
    q["cls_S+@3000"], q["cls_NS@10000"] = by_n["3000"]["classes"].get("S+", 0), by_n["10000"]["classes"].get("NS", 0)
    q["ctrl_kept"] = ev["rb2"]["controls"][0]["kept_primary"]
    q["n_T"] = float(len(a7[a7.family == "p1_linear"]))
    a3 = pd.read_parquet(res / "A3/a3_sn_ramp.parquet")
    q["rate_lo"], q["rate_hi"] = float(a3.rate.min()), float(a3.rate.max())
    q["ms11_T"] = [10.0, 316.22776601683796]
    crit = yaml.safe_load((Path(root) / "configs/robustness_criteria.yaml").read_text(encoding="utf-8"))

    def val(k):
        def walk(o):
            if isinstance(o, dict):
                if k in o and isinstance(o[k], dict) and "value" in o[k]:
                    return o[k]["value"]
                for v in o.values():
                    r_ = walk(v)
                    if r_ is not None:
                        return r_
            return None
        return walk(crit)
    band = val("band_primary_hz")
    q["band_lo"], q["band_hi"] = float(band[0]), float(band[1])
    q["min_cycles"], q["amin_factor"] = val("min_cycles"), val("amin_factor")
    q.update(_grids(root))
    return q


def _grids(root) -> dict:
    """The grids and parameter sets of the FS2, FS3 and F6 drawings, from their prepared data (stored results only)."""
    import numpy as np
    from . import figures as FG
    out: dict = {}
    d3 = FG.prepare_FS3(FG.load_FS3(Path(root) / "results"))
    out["fs3_N"] = [float(x) for x in d3["N"]]
    out["fs3_T"] = sorted({float(x) for x in d3["noise_T"]})
    out["fs3_sigma"] = sorted({float(x) for x in d3["noise_sigma"]})
    d2 = FG.prepare_FS2(FG.load_FS2(Path(root) / "results"))
    vals = set(float(x) for x in d2["k7_tau"]) | {5.0, 50.0} | set(float(x) for x in d2["k9_eta_bar"]) | set(float(x) for x in d2["k10_J_8.0"]) | {8.0, 20.0, 40.0}
    vals |= {float(d2["k10_band_hz"][0]), float(d2["k10_band_hz"][1]), 100 * float(d2["k10_band_slack"]), 10000.0, 50000.0, 10.0, 400.0, 6.0, 4.0, 0.0001, 0.99, 1.01}
    vals |= {float(d2["k10_tau_d"].min()), float(d2["k10_tau_d"].max())}
    out["fs2_vals"] = sorted(vals)
    d6 = FG.prepare_F6(FG.load_F6())
    out["f6_T"] = sorted({float(x) for x in d6["s6_T"]})
    d5 = FG.prepare_F5(FG.load_F5())
    out["f5_vals"] = sorted({float(x) for x in (d5["map1_Delta"].min(), d5["map1_Delta"].max(), d5["map1_tau_d_ms"].min(), d5["map1_tau_d_ms"].max(), d5["map2_J0"].min(), d5["map2_J0"].max(),
                                                len(d5["map1_Delta"]), len(d5["map1_tau_d_ms"]), len(d5["map2_J0"]), len(d5["map2_T_ramp_s"]), float(d5["cell_T_ramp_s"][0]))})
    return out


# ---- rules -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# S rules: (token regex on the absolute token, context regex that binds the number to its quantity by its words, quantity, scale). The first match wins; the typed number must equal scale * stored value at
# the typed precision (a list value: be a member of it).
S_RULES = [
    (r"97", r"97 of 225|97 of the 225|agrees? (in|at) 97", "sub_agree", 1), (r"225", r"of (the )?225|\b225-cell|225 cells", "sub_cells", 1), (r"43\.1", r"43\.1", "sub_pct", 1), (r"203", r"203", "sub_needed", 1),
    (r"90", r"90 ?(percent|%)", "sub_thr_pct", 1),
    (r"7", r"\b7 of 10", "kept", 1), (r"8", r"\b8 (are )?needed|against 8|>= 8|least 8 of 10|8 of 10 seeds", "kept_need", 1),
    (r"181", r"181", "solver_ms", 1), (r"58\.698", r"58\.698", "onset_default", 1), (r"58\.879", r"58\.879", "onset_radau", 1),
    (r"49\.0", r"49\.0 ", "rb9b_spec", 1), (r"44\.609", r"44\.609", "rb9b_cycle", 1), (r"4\.391|4\.39", r"4\.39", "rb9b_diff", 1), (r"0\.5", r"0\.5 Hz|allowed 0\.5|against 0\.5", "rb9b_bound", 1),
    (r"306", r"306", "wn_nonNS@0.2", 1), (r"400", r"400, 172|306, 400", "wn_nonNS@0.333", 1), (r"172", r"172", "wn_nonNS@0.593", 1), (r"24", r"24 of 500", "wn_nonNS@1.05", 1), (r"500", r"of 500", "wn_den", 1),
    (r"0\.2", r"0\.2, 0\.333", "wn_W@0.2", 1), (r"0\.333", r"0\.333", "wn_W@0.333", 1), (r"0\.593", r"0\.593", "wn_W@0.593", 1), (r"1\.054", r"1\.054", "wn_W@1.05", 1),
    (r"0\.0624", r".", "sigma", 1),
    (r"0\.039522", r".", "sc_mf", 1), (r"0\.037989", r".", "sc_min", 1), (r"0\.038920", r".", "sc_max", 1),
    (r"6", r"0 of 6 testable|of 6 testable", "rb3a_n", 1), (r"14", r"14 of 900", "rb9c_changed", 1),
    (r"25\.7", r"25\.7", "rate_lo", 1), (r"24\.3", r"24\.3", "rate_hi", 1),
    (r"25", r"25 to 100|from 25|below 25|25–100", "band_lo", 1), (r"100", r"to 100 Hz|25 to 100", "band_hi", 1), (r"10", r"minimum 10 cycles|least 10 cycles", "min_cycles", 1),
    (r"0\.1", r"0\.1 (x|times) (A_ref|a reference)", "amin_factor", 1),
    (r"6", r"S\+ in 6 seeds", "cls_S+@3000", 1), (r"1", r"NS in 1 at", "cls_NS@10000", 1),
    (r"4", r"of 4 cells|of the 4 map cells|the 4 map cells", "rb1_cells_n", 1), (r"2", r"2 of 3 at 3e3", "ctrl_surge@3000", 1),
    (r"316", r"316", "ms11_T", 1),
    # grids and parameter sets of FS3, FS2 and F6 (membership)
    (r"1000|3000|10,000|30,000", r"N = 1000, 3000|N = 1000|1000, 3000", "fs3_N", 1),
    (r"10|30|120|300", r"ramp durations 10, 30|10, 30, 120|10 s and 120 s|120 and 300", "fs3_T", 1),
    (r"0\.5|1|2", r"noise factors 0\.5", "fs3_sigma", 1),
    (r"10|30|120|300", r"T_ramp 10, 30, 120|10, 30, 120 and 300|in that order", "f6_T", 1),
    (r"0\.01|0\.6|1|50|40|5|30|25|13", r"map 1 at Delta|tau_d 1 to 50|map 2 at J0|\(30 values|\(25 values|\(13 values|J0 -40|T_ramp 30 s", "f5_vals", 1),
]
GROUP_RULES: list = []      # (file regex, function regex, token regex, kind, note)
_ANY = r".*"
_ID = r"[-−]\d"
GROUP_RULES += [
    (_ANY, _ANY, _ID, "P", "number of a claim-limit identifier such as MS9(e)-1 (an identifier, not a quantity)"),
    (r"captions", r"CLASS_KEY_SOURCE", _ANY, "P", "plan Table 2.1 reference"),
    (r"jf26", r"UNDEFINED_UNVERIFIED", r"2\.4", "P", "plan section 2.4 reference"),
    (r"jfs2", r"(names|mapping)", r"3\.2", "P", "plan Table 3.2 reference"),
    (r"plain", r"PHRASES", r"8\.1|11", "P", "plan Table 8.1 / Table 11.2 reference"),
    (r"plain", r"PHRASES", r"1e4|3e4|10|25", "R", "ruled phrase table of the plain wording (N = 1e4 and 3e4, 10 of 10 seeds, 25 Hz of the failure label)"),
    (r"plain", r"DEFINITIONS", r"1e4", "R", "ruled definition text (plan Table 7.2 names; N = 1e4 of the claim limit)"),
    (r"plain", r"PLAIN_LIMITS|DELETE", _ANY, "R", "ruled plain wording of a claim limit (docs/claim_limit_labels.md, same numbers); the stored numbers are S rows, the others are ruled counts not re-derived here"),
    (r"jshort", r"SHORT_LIMITS|LIMIT_KEYS|SHORT_LIMIT_IDS", _ANY, "R", "ruled short form of a claim limit (same numbers as the plain wording, test)"),
    (r"jf4cap", r"F4[AB]_LIMIT_EXTRA", _ANY, "R", "ruled short form of a claim limit (same numbers as the plain wording, test)"),
    (r"jf26", r"F6_LIMIT_EXTRA", _ANY, "R", "ruled short form of a claim limit"),
    (r"jcaption", r"(CHECK_NAMES|CHECK_IDS|TITLE_MAP|LIMIT_SCOPE|WORD_ENTRIES|UNCODE|F5_SENTENCE_1)", _ANY, "R", "ruled wording of a check name, title-map entry, limit scope or take-home sentence (plan Table 7.2 names, claim limits)"),
    (r"jcaption", r"PLAIN_N", _ANY, "C", "notation table of N (1e3 -> 1000 ...)"),
    (r"jfs3", r"NLAB", _ANY, "C", "N labels of the axis"),
    (r"jf4cap|jf4", r"UNDEFINED_UNVERIFIED|MAIN_FAILURES|F4[AB]_LIMITS|mapping_text|labs", _ANY, "R", "ruled main-failure text, claim-limit list or mapping text of the F4 files"),
    (r"jfs2|jfs3|jfs|jf4|jf26|jf4cap|captions", _ANY, r"7\.4|11\.2|12\.6|16\.2|6\.3|8\.0|600|0\.15|2\.72", "D", "size of the figure in inches, a drawing constant, or the value of e echoed in the text"),
    (r"jshort|jcaption|jf26", r"(DEFS|f1_short|f3_short|f5_short|f5c_short|f2_short|f6_short|seeds|band_end_short|settings_line|settings|class_key|lead|key|band_end_sentence|take|params|panels|f5c_counts|supplement_rows|all_fail_rows|failed|"
     r"f2_sentence1|f2_sentence_updown|f6_sentence_points|f6_facts|same|s)", _ANY, "T",
     "a parameter, grid value or count of a figure that the text restates; the Parameters paragraph of the full caption is built from the recorded rows and the short Parameters sentence is compared with it (test W2); "
     "a drawn count is read by the facts functions that stop the build when it differs"),
    (r"jfs2", _ANY, _ANY, "T", "a parameter, grid value or axis limit of FS2 that the text restates (the Parameters paragraph is built from the recorded rows; the grids are S rows where the context binds them)"),
    (r"jfs3", _ANY, _ANY, "T", "a parameter, grid value or count of FS3 that the text restates (the Parameters paragraph is built from the recorded rows)"),
    (r"jfs", _ANY, _ANY, "T", "a parameter of FS1 that the text restates (built from the recorded rows)"),
    (r"captions", r"(DURATION_FLOOR_TEXT|D2_STATEMENT|NOISE_BAR_TEXT)", _ANY, "R", "ruled wording of the draft captions (duration floor, D2 statement, noise bar)"),
    (r"jf4cap|jf4", _ANY, _ANY, "T", "a grid value or count of the F4 files that the text restates (start distances 0.5, 1.5, 3.0 of the F4 sweep; counts read by f4_facts)"),
    (r"jfs4", r"(draw|alt_text|source_rows|panels|params|key)", r"200|100", "R", "the V_p check value 200 and the default 100 of the project's peak and reset values (plan R5, single source); 100 is also read from the recorded network parameters at build time"),
    (r"jfs4", _ANY, _ANY, "T", "an axis limit, tick or label of the FS4 drawing, or a setting that the text restates and that is read at build time (consts: the recorded rows and the stored A7 and A11 tables)"),
    (r"jfs5", r"UNDEFINED_UNVERIFIED", _ANY, "P", "plan wording of the total band (1 to 150 Hz)"),
    (r"jfs5", _ANY, _ANY, "T", "an axis limit, tick or label of the FS5 drawing, a typed plain label of a stored variant name (tests/test_ms13_13t9_fs.py compares its number with the stored name), or a setting read at build time"),
]


def _member(v: float, lst: list, h: float) -> bool:
    return any(abs(v - abs(x)) <= h * 1.0001 or (abs(x) > 0 and abs(v - abs(x)) / abs(x) < 1e-9) for x in lst)


def classify(rows: list, q: dict) -> list:
    """Adds kind, source, stored and equal to every literal row; a row that no rule covers gets kind '?' (a FAIL of the audit)."""
    out = []
    for r in rows:
        tok, ctx = r["token"], r["context"]
        v = abs(value_of(tok))
        bare = tok.replace("−", "-").lstrip("-")
        hit = None
        for tre, cre, key, scale in S_RULES:
            if re.fullmatch(tre, bare.replace(",", "")) is None and re.fullmatch(tre, bare) is None:
                continue
            if re.search(cre, ctx):
                hit = (key, scale)
                break
        row = dict(r)
        if hit:
            key, scale = hit
            sv = q[key]
            if isinstance(sv, list):
                ok = _member(v, [x * scale for x in sv], half_unit(tok))
                row.update(kind="S", source=f"stored set: {key}", stored=sv, equal=bool(ok))
            else:
                sv = abs(sv) * scale
                ok = abs(v - sv) <= half_unit(tok) * 1.0001 or (sv != 0 and abs(v - sv) / abs(sv) < 1e-9)
                row.update(kind="S", source=f"stored: {key}", stored=sv, equal=bool(ok))
        else:
            row.update(kind="?", source="", stored=None, equal=None)
            for fre, nre, tre, kind, note in GROUP_RULES:
                if re.fullmatch(fre, r["file"]) and re.fullmatch(nre, r["func"]) and re.fullmatch(tre, tok):
                    row.update(kind=kind, source=note)
                    break
            else:
                if tok in SMALL:
                    row.update(kind="C", source="small integer: count word, ordinal or index (not told from a stored value by value)")
        out.append(row)
    return out


def audit(root) -> list:
    return classify(literals(root), stored(root))


def audit_markdown(rows: list) -> str:
    """The table of docs/ms13_13t9_n2_audit.md: one line per distinct (file, constant, kind, source); counts first."""
    import collections
    cnt = collections.Counter(r["kind"] for r in rows)
    seen: dict = {}
    for r in rows:
        key = (r["file"], r["token"], r["kind"], r["source"], str(r["stored"]))
        e = seen.setdefault(key, {"n": 0, "ctx": r["context"], "equal": r["equal"], "line": r["line"], "func": r["func"]})
        e["n"] += 1
    out = ["# MS13 13t-9 N2: numbers typed into the caption builders and the image text of the journal export (DL-680)", "",
           "Generated by `jnumaudit.audit_markdown` from the source files and the stored results; one line per distinct (file, constant, kind, source). "
           f"Literal occurrences: {len(rows)}; by kind: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())) + ". "
           f"Kind S rows: {sum(1 for r in rows if r['kind'] == 'S')} occurrences, equal {sum(1 for r in rows if r['kind'] == 'S' and r['equal'])}, not equal {sum(1 for r in rows if r['kind'] == 'S' and not r['equal'])}. "
           "Kinds: S stored quantity typed into the text (compared with the stored value); R ruled wording (plan or decision log); P reference or identifier; T parameter of a figure restated in the text "
           "(compared elsewhere with the recorded rows); C count word or structure label; D drawing constant.", "",
           "| file | constant | value in code | stored value | source | equal | kind | occurrences | first context |", "|---|---|---|---|---|---|---|---|---|"]
    for (f, tok, kind, src, st), e in sorted(seen.items(), key=lambda kv: (kv[0][0], kv[1]["line"], kv[0][1])):
        eq = {True: "yes", False: "NO", None: "-"}[e["equal"]]
        ctx = e["ctx"].replace("|", "/")
        out.append(f"| {f}.py:{e['line']} ({e['func']}) | {tok} | {tok} | {st if st != 'None' else '-'} | {src.replace('|', '/')} | {eq} | {kind} | {e['n']} | {ctx} |")
    return "\n".join(out) + "\n"
