"""MS13 13n: cross-figure audit of the eleven figure drafts (DL-493). Writes docs/ms13_audit.md and nothing else.

  .venv/Scripts/python.exe scripts/ms13_audit.py

Reads figures/ (outputs and provenance JSONs), the figure scripts and tests (as text, never run), src/mprsurge/plotting/figures.py and style.py (as text, parsed with
ast; not imported), docs/claim_limit_labels.md, docs/ms13_plan.md (section 5) and the stored inputs the provenance names. It simulates and builds nothing. It reports
inconsistencies and fixes none; 'listed' in the plan's section 5 table is not 'decided'.

Per figure: ID, draft flag, dirty flag, commit; number of inputs and every input re-hashed against the provenance; outputs, script, modules and configs re-hashed
against the provenance (a changed module or script is build-code drift, informational); claim-limit IDs of the provenance, defined or not in the label table; claim limits
that section 5 lists for the figure and the figure does not carry (a plan label is also looked for in plain words in the caption: a heuristic); the strip rows
(the figure's declared strip, resolved against the stored A11 table); caption length; the caption strings that the figure's own caption tests require (read from
tests/test_fig_<ID>.py with ast) and whether they are present; the style keys used (names reached from _draw_<ID>, prepare_<ID>, load_<ID> and make_<ID> through
the module's own call graph); literal colours, colormaps, hatches, markers and sizes in those functions (must be none); whether each claim label has the same definition in
every caption that prints it.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

FIGURES = ("F1", "F2", "F3", "F4", "F5", "F6", "FS1", "FS2", "FS3", "FS4", "FS5")
OUT = "docs/ms13_audit.md"
FIGURES_PY = "src/mprsurge/plotting/figures.py"
STYLE_CALLS = {"get", "figure_colour", "figure_hatch", "diagram_mark", "contour_mark"}
COLOUR_KW = {"color", "c", "facecolor", "edgecolor", "fc", "ec", "mfc", "mec", "markerfacecolor", "markeredgecolor", "labelcolor", "textcolor", "facecolors", "edgecolors"}
SIZE_KW = {"ms", "markersize", "s"}
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
NL = chr(10)


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ---- stored tables -----------------------------------------------------------------------------------------------------------------------------

def load_label_table(root: Path) -> dict[str, dict]:
    """label -> {short, dls, figures} from the first table of docs/claim_limit_labels.md (header 'Label')."""
    out, on = {}, False
    for line in (root / "docs/claim_limit_labels.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| Label |"):
            on = True
            continue
        if on and not line.startswith("|"):
            break
        if on and not line.startswith("|---"):
            c = [x.strip() for x in line.strip().strip("|").split(" | ")]
            if len(c) >= 6:
                out[c[0]] = {"source": c[1], "wording": c[2], "short": c[3], "dls": tuple(x.strip() for x in c[4].split(",")), "figures": c[5]}
    return out


def canonical_id(first_col: str, labels) -> str | None:
    s = first_col.strip()
    m = re.match(r"MS9 \(e\)-(\d)", s)
    if m:
        return f"MS9(e)-{m.group(1)}"
    m = re.match(r"DL-163 departure (\d)", s)
    if m:
        return f"DL-163-D{m.group(1)}"
    m = re.match(r"(G6-D\d|G4-C\d|MS1[12]-C\d)", s)
    if m:
        return m.group(1)
    m = re.match(r"(RB\d(?:\(b\))? FAIL|G7 not passed|D24 failed)", s)
    if m:
        t = m.group(1)
        return t + " (plan label)" if t + " (plan label)" in labels else t
    return None


def figures_of(text: str) -> list[str]:
    t = text.lower()
    if t.startswith("none"):
        return []
    if "f1 to f6" in t:
        return ["F1", "F2", "F3", "F4", "F5", "F6"]
    if t.startswith("every figure"):
        return list(FIGURES)
    return [f for f in re.findall(r"\bFS?\d\b", text) if f in FIGURES]


def load_plan_table(root: Path, labels) -> list[dict]:
    """Rows of the claim-limit table in section 5 of docs/ms13_plan.md: {id, row, figures}."""
    rows, on = [], False
    for line in (root / "docs/ms13_plan.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## 5."):
            on = True
        elif line.startswith("## 6."):
            break
        elif on and line.startswith("|") and not line.startswith("|---") and not line.startswith("| Claim limit"):
            c = [x.strip() for x in line.strip().strip("|").split(" | ")]
            if len(c) >= 3:
                rows.append({"id": canonical_id(c[0], labels), "row": c[0], "figures": figures_of(c[-1]), "figures_text": c[-1]})
    return rows


def a11_table(root: Path) -> list[dict]:
    with open(root / "results/A11/a11_robustness.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---- figures.py (ast) --------------------------------------------------------------------------------------------------------------------------

class Module:
    def __init__(self, root: Path):
        self.src = (root / FIGURES_PY).read_text(encoding="utf-8")
        self.tree = ast.parse(self.src)
        self.funcs = {n.name: n for n in self.tree.body if isinstance(n, ast.FunctionDef)}
        self.consts = {}
        for n in self.tree.body:
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                try:
                    self.consts[n.targets[0].id] = ast.literal_eval(n.value)
                except (ValueError, SyntaxError):
                    pass

    def reached(self, fig: str) -> list[str]:
        todo = [f"{p}_{fig}" for p in ("_draw", "prepare", "load", "make")]
        seen = []
        while todo:
            n = todo.pop()
            if n in seen or n not in self.funcs:
                continue
            seen.append(n)
            for node in ast.walk(self.funcs[n]):
                if isinstance(node, ast.Name) and node.id in self.funcs:
                    todo.append(node.id)
        return sorted(seen)

    def style_keys(self, names) -> list[str]:
        keys = set()
        for n in names:
            for node in ast.walk(self.funcs[n]):
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "S":
                    keys.add(node.attr)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "S" \
                        and node.func.attr in STYLE_CALLS and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    keys.add(f"{node.func.attr}({node.args[0].value!r})")
                if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name) and node.value.value.id == "S" \
                        and isinstance(node.slice, ast.Constant):
                    keys.add(f"{node.value.attr}[{node.slice.value!r}]")
        return sorted(keys)

    def literals(self, names) -> list[str]:
        """Literal colours, colormaps, hatches, markers and sizes in the drawing code (must be none)."""
        out = []
        for n in names:
            kw_values = set()
            for node in ast.walk(self.funcs[n]):
                if isinstance(node, ast.Call):
                    for kw in node.keywords:
                        v = kw.value
                        if kw.arg in COLOUR_KW and isinstance(v, ast.Constant) and isinstance(v.value, str) and v.value.lower() != "none":
                            out.append(f"{n}:{node.lineno} {kw.arg}={v.value!r}")
                            kw_values.add(id(v))
                        elif kw.arg in COLOUR_KW and isinstance(v, (ast.Tuple, ast.List)) and v.elts and all(isinstance(e, ast.Constant) for e in v.elts):
                            out.append(f"{n}:{node.lineno} {kw.arg}=<literal tuple>")
                        elif kw.arg == "cmap" and isinstance(v, ast.Constant) and isinstance(v.value, str):
                            out.append(f"{n}:{node.lineno} cmap={v.value!r}")
                        elif kw.arg == "hatch" and isinstance(v, ast.Constant) and isinstance(v.value, str):
                            out.append(f"{n}:{node.lineno} hatch={v.value!r}")
                        elif kw.arg == "marker" and isinstance(v, ast.Constant) and isinstance(v.value, str):
                            out.append(f"{n}:{node.lineno} marker={v.value!r}")
                        elif kw.arg in SIZE_KW and isinstance(v, ast.Constant) and isinstance(v.value, (int, float)):
                            out.append(f"{n}:{node.lineno} {kw.arg}={v.value!r}")
            for node in ast.walk(self.funcs[n]):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and HEX.fullmatch(node.value) and id(node) not in kw_values:
                    out.append(f"{n}:{node.lineno} hex colour {node.value}")
        return sorted(set(out))

    def strip_spec(self, fig: str):
        """('rows', [(rb, check)...]) for an explicit strip, ('rb', [rb...]) for FAIL rows of listed RB ids, or None."""
        if f"{fig}_STRIP" in self.consts:
            return "rows", [tuple(x) for x in self.consts[f"{fig}_STRIP"]]
        if f"{fig}_STRIP_RB" in self.consts:
            return "rb", list(self.consts[f"{fig}_STRIP_RB"])
        if fig == "F3" and "F3" in self.consts.get("FIGURE_RB", {}):
            return "rb", list(self.consts["FIGURE_RB"]["F3"])
        return None

    def claim_limits(self, fig: str):
        return self.consts.get(f"{fig}_CLAIM_LIMITS")


def required_caption_strings(test_src: str) -> dict[str, list[str]]:
    """{'in': [...], 'not in': [...], 'startswith': [...]} string literals that the caption tests assert (ast; a For over a tuple of strings is followed)."""
    tree = ast.parse(test_src)
    res = {"in": [], "not in": [], "startswith": []}
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and "caption" in n.name]:
        loops = {}
        for node in ast.walk(fn):
            if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and isinstance(node.iter, (ast.Tuple, ast.List)):
                loops[node.target.id] = [e.value for e in node.iter.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        for node in ast.walk(fn):
            if isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], (ast.In, ast.NotIn)):
                c = node.comparators[0]
                is_cap = (isinstance(c, ast.Name) and c.id == "caption") or (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and isinstance(c.func.value, ast.Name)
                                                                              and c.func.value.id == "caption")
                if not is_cap:
                    continue
                key = "in" if isinstance(node.ops[0], ast.In) else "not in"
                lower = isinstance(c, ast.Call)
                if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                    res[key].append(("L:" if lower else "") + node.left.value)
                elif isinstance(node.left, ast.Name) and node.left.id in loops:
                    res[key] += [("L:" if lower else "") + s for s in loops[node.left.id]]
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "startswith" and isinstance(node.func.value, ast.Name) \
                    and node.func.value.id == "caption" and node.args and isinstance(node.args[0], ast.Constant):
                res["startswith"].append(node.args[0].value)
    return {k: list(dict.fromkeys(v)) for k, v in res.items()}


# ---- per-figure audit --------------------------------------------------------------------------------------------------------------------------

def plain_words(label: str, caption: str) -> bool:
    """Heuristic: a plan label (no entry of its own, or a plan label) in plain words in the caption."""
    core = label.replace(" (plan label)", "")
    if core.endswith(" FAIL") or core.endswith(" failed"):
        pre = core.rsplit(" ", 1)[0]
        return re.search(re.escape(pre) + r"\W+(?:\w+\W+){0,3}?FAIL(?:ED|S)?", caption, re.I) is not None
    if core.endswith("not passed"):
        pre = core.split(" ")[0]
        return re.search(re.escape(pre) + r"\W+(?:\w+\W+){0,3}?(?:NOT PASSED|FAIL)", caption, re.I) is not None
    return core.lower() in caption.lower()


def input_path(root: Path, p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else root / q


def audit_figure(root: Path, fig: str, mod: Module, labels, plan_rows, a11) -> dict:
    d = root / "figures" / fig
    prov = json.loads((d / f"{fig}_provenance.json").read_text(encoding="utf-8"))
    caption = (d / f"{fig}_caption.txt").read_text(encoding="utf-8")
    r = {"fig": fig, "flags": []}
    flag = r["flags"].append
    r["draft"], r["dirty"], r["commit"] = prov.get("draft"), prov.get("git", {}).get("dirty"), prov.get("git", {}).get("commit", "")
    if r["dirty"]:
        flag(f"{fig}: provenance dirty flag is true")
    if not r["draft"]:
        flag(f"{fig}: provenance draft flag is false (all figures are untagged drafts)")
    # inputs
    ins = prov.get("inputs", [])
    r["n_inputs"] = len(ins)
    diff = []
    for i in ins:
        p = input_path(root, i["path"])
        if not p.is_file():
            diff.append((i["path"], "MISSING"))
        elif sha256_file(p) != i["sha256"]:
            diff.append((i["path"], "CHANGED"))
    r["input_diffs"] = diff
    for p, why in diff:
        flag(f"{fig}: input {p} {why} against the provenance")
    # outputs, script, modules, configs
    drift = []
    for o in prov.get("outputs", []):
        p = input_path(root, o["path"])
        if not p.is_file() or sha256_file(p) != o["sha256"]:
            flag(f"{fig}: recorded output {o['path']} differs from the provenance")
    s = prov.get("script", {})
    for kind, items in (("script", [s] if s else []), ("module", prov.get("modules", [])), ("config", [{"path": k, "sha256": v} for k, v in prov.get("configs", {}).items()])):
        for i in items:
            p = input_path(root, i["path"])
            if not p.is_file() or sha256_file(p) != i["sha256"]:
                drift.append(f"{kind} {i['path']}")
    r["drift"] = drift
    # claim limits
    ids = list(prov.get("claim_limits", []))
    r["claim_limits"] = ids
    r["undefined"] = [i for i in ids if i not in labels]
    for i in r["undefined"]:
        flag(f"{fig}: claim-limit ID {i} is not defined in docs/claim_limit_labels.md")
    declared = mod.claim_limits(fig)
    if declared is not None and list(declared) != ids:
        flag(f"{fig}: provenance claim limits differ from {fig}_CLAIM_LIMITS in figures.py")
    r["not_carried"], r["carried_unlisted"] = [], []
    listed = set()
    for row in plan_rows:
        if fig in row["figures"] and row["id"]:
            listed.add(row["id"])
            if row["id"] not in ids:
                pw = plain_words(row["id"], caption)
                r["not_carried"].append((row["id"], "plain words in caption" if pw else "not in caption"))
    for i in ids:
        if i not in listed:
            r["carried_unlisted"].append(i)
    # strip
    spec = mod.strip_spec(fig)
    strip = []
    if spec is None:
        r["strip"] = None
    else:
        kind, items = spec
        if kind == "rows":
            for rb, ck in items:
                row = [x for x in a11 if x["rb_id"] == rb and x["check_id"] == ck]
                strip.append((rb, ck, row[0]["pass_or_fail"] if row else "NO ROW IN THE A11 TABLE"))
                if not row:
                    flag(f"{fig}: strip row {rb} {ck} is not in the stored A11 table")
        else:
            strip = [(x["rb_id"], x["check_id"], x["pass_or_fail"]) for x in a11 if x["rb_id"] in items and x["pass_or_fail"] == "FAIL"]
        r["strip"] = (kind, items, strip)
    # caption
    r["caption_chars"], r["caption_words"] = len(caption), len(caption.split())
    tsrc = (root / f"tests/test_fig_{fig}.py").read_text(encoding="utf-8")
    req = required_caption_strings(tsrc)
    cl = caption.lower()
    r["required"] = req
    r["required_missing"] = [s for s in req["in"] if (s[2:].lower() not in cl if s.startswith("L:") else s not in caption)]
    r["forbidden_present"] = [s for s in req["not in"] if (s[2:].lower() in cl if s.startswith("L:") else s in caption)]
    r["startswith_missing"] = [s for s in req["startswith"] if not caption.startswith(s)]
    for s in r["required_missing"]:
        flag(f"{fig}: caption lacks a string its own test requires: {s!r}")
    for s in r["forbidden_present"]:
        flag(f"{fig}: caption has a string its own test forbids: {s!r}")
    generic = []
    if re.search(r"(?=[0-9a-f]*[a-f])[0-9a-f]{12,}", caption):
        generic.append("a 12+ hex run")
    if "hash" in cl or re.search(r"\bsha(256)?\b", cl):
        generic.append("'hash' or 'sha'")
    if "Provenance" in caption or f"{fig}_" in caption:
        generic.append("'Provenance' or the figure file prefix")
    r["generic"] = generic
    for g in generic:
        flag(f"{fig}: caption contains {g}")
    # style keys and literals
    names = mod.reached(fig)
    r["functions"] = names
    r["style_keys"] = mod.style_keys(names)
    r["literals"] = mod.literals(names)
    for lit in r["literals"]:
        flag(f"{fig}: literal in drawing code: {lit}")
    # label definitions
    r["label_defs"], r["label_bad"] = {}, []
    for lab, e in labels.items():
        expect = f"{lab}: {e['short']} ({', '.join(e['dls'])})"
        if f"{lab}: " in caption:
            ok = expect in caption
            r["label_defs"][lab] = ok
            if not ok:
                r["label_bad"].append(lab)
                flag(f"{fig}: label {lab} is printed with a definition that differs from docs/claim_limit_labels.md")
    seg = caption.split("Claim limits: ", 1)[1] if "Claim limits: " in caption else ""
    with_defs = [lab for lab in labels if f"{lab}: " in seg]
    r["limit_style"] = "definitions" if with_defs else "ids only"
    in_caption = with_defs if with_defs else [x.strip() for x in seg.split(".")[0].split(",") if x.strip()]
    r["caption_labels"] = in_caption
    if set(in_caption) != set(ids):
        flag(f"{fig}: labels printed under 'Claim limits:' {sorted(set(in_caption) ^ set(ids))} differ from the provenance claim limits")
    return r


def render(results: list[dict], mod: Module, labels, plan_rows) -> str:
    L = ["# MS13 cross-figure audit (13n, DL-493)", "",
         "Generated by `scripts/ms13_audit.py` (read-only on figures/, provenance JSONs, scripts, tests, the label table and the stored inputs). It reports; it fixes nothing. "
         "'Listed' in the plan's section 5 table is not 'decided'. Heuristics are named as such. Regenerate with the script; do not edit by hand.", "",
         "## Summary", "", "| Fig | draft | dirty | commit | inputs | input diffs | claim limits | undefined | listed, not carried | carried, not listed | caption chars | missing caption strings | literals | flags |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        L.append(f"| {r['fig']} | {r['draft']} | {r['dirty']} | {r['commit'][:7]} | {r['n_inputs']} | {len(r['input_diffs'])} | {len(r['claim_limits'])} | {len(r['undefined'])} | "
                 f"{len(r['not_carried'])} | {len(r['carried_unlisted'])} | {r['caption_chars']} | {len(r['required_missing'])} | {len(r['literals'])} | {len(r['flags'])} |")
    L += ["", "## Flags (inconsistencies; none is fixed here)", ""]
    allf = [f for r in results for f in r["flags"]]
    L += [f"- {f}" for f in allf] if allf else ["- none"]
    drift = [r for r in results if r["drift"]]
    L += ["", "## Build-code drift (informational: script, module or config now differs from the hash in the provenance)", ""]
    L += [f"- {r['fig']}: {len(r['drift'])} file(s): " + "; ".join(r["drift"]) for r in drift] if drift else ["- none"]
    L += ["", "## Plan section 5 rows without a figure (listed only)", ""]
    for row in plan_rows:
        if not row["figures"]:
            L.append(f"- {row['row']}: figures column {row['figures_text']!r}")
    unmapped = [row["row"] for row in plan_rows if row["id"] is None]
    L += ["", "Plan rows whose first column could not be mapped to a label ID: " + (", ".join(unmapped) if unmapped else "none")]
    nolabel = sorted({row["id"] for row in plan_rows if row["id"] and row["id"] not in labels})
    L += ["", "Plan rows with no entry in docs/claim_limit_labels.md: " + (", ".join(nolabel) if nolabel else "none")]
    for r in results:
        L += ["", f"## {r['fig']}", "",
              f"- draft {r['draft']}; dirty {r['dirty']}; build commit {r['commit']}",
              f"- inputs: {r['n_inputs']} registered in the provenance; re-hashed; differences: " + (", ".join(f"{p} {w}" for p, w in r["input_diffs"]) if r["input_diffs"] else "none"),
              "- build-code drift: " + ("; ".join(r["drift"]) if r["drift"] else "none"),
              f"- claim limits in the provenance ({len(r['claim_limits'])}): " + ", ".join(r["claim_limits"]),
              "- not defined in docs/claim_limit_labels.md: " + (", ".join(r["undefined"]) if r["undefined"] else "none"),
              "- listed by plan section 5 for this figure, not carried: " + ("; ".join(f"{i} ({w})" for i, w in r["not_carried"]) if r["not_carried"] else "none"),
              "- carried, not listed by plan section 5 for this figure: " + (", ".join(r["carried_unlisted"]) if r["carried_unlisted"] else "none")]
        if r["strip"] is None:
            L.append("- strip rows: no strip declaration in figures.py")
        else:
            kind, items, strip = r["strip"]
            L.append(f"- strip declaration ({'explicit rows' if kind == 'rows' else 'FAIL rows of RB ids'}): {items}; resolved against the stored A11 table ({len(strip)}): "
                     + ("; ".join(f"{a} {b} {c}" for a, b, c in strip) if strip else "none"))
        L += [f"- caption: {r['caption_chars']} characters, {r['caption_words']} words",
              f"- caption strings required by tests/test_fig_{r['fig']}.py: {len(r['required']['in'])} 'in', {len(r['required']['not in'])} 'not in', "
              f"{len(r['required']['startswith'])} 'startswith'; missing: " + (", ".join(repr(s) for s in r["required_missing"]) if r["required_missing"] else "none"),
              "  - required (in): " + "; ".join(repr(s) for s in r["required"]["in"]),
              f"- claim-limit sentence style: {r['limit_style']}",
              "- generic caption checks (no hash, no 12-hex run, no provenance wording): " + ("; ".join(r["generic"]) if r["generic"] else "pass"),
              f"- functions reached ({len(r['functions'])}): " + ", ".join(r["functions"]),
              f"- style keys used ({len(r['style_keys'])}): " + ", ".join(r["style_keys"]),
              "- literal colours, colormaps, hatches, markers, sizes in those functions: " + ("; ".join(r["literals"]) if r["literals"] else "none"),
              "- claim labels printed with their definition: " + ", ".join(f"{k} ({'same as the table' if v else 'DIFFERENT'})" for k, v in r["label_defs"].items())]
    L += ["", "## Same label, same definition in every caption", ""]
    per = {}
    for r in results:
        for lab, ok in r["label_defs"].items():
            per.setdefault(lab, []).append((r["fig"], ok))
    for lab in sorted(per):
        L.append(f"- {lab}: " + ", ".join(f"{f}{'' if ok else ' (DIFFERENT)'}" for f, ok in per[lab]) + f"; one definition in the table: {labels[lab]['short']!r} ({', '.join(labels[lab]['dls'])})")
    return NL.join(L) + NL


def run(root: Path, out: Path | None = None, figs=FIGURES) -> tuple[str, list[dict]]:
    labels = load_label_table(root)
    plan_rows = load_plan_table(root, labels)
    mod = Module(root)
    a11 = a11_table(root)
    results = [audit_figure(root, fig, mod, labels, plan_rows, a11) for fig in figs]
    styles = {r["limit_style"] for r in results}
    if len(styles) > 1:
        for r in results:
            if r["limit_style"] == "ids only":
                r["flags"].append(f"{r['fig']}: 'Claim limits:' prints the IDs without the table definitions (other captions print ID, short form and DL numbers)")
    text = render(results, mod, labels, plan_rows)
    if out is not None:
        with open(out, "w", newline="", encoding="utf-8") as f:
            f.write(text)
    return text, results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    root = Path(a.root) if a.root else Path(__file__).resolve().parents[1]
    out = Path(a.out) if a.out else root / OUT
    text, results = run(root, out)
    n = sum(len(r["flags"]) for r in results)
    print(f"{len(results)} figures audited, {n} flags; written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
