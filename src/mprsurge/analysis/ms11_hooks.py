"""MS11 11d: recompute hooks for the 26 carried checks of MS8 to MS10 (rulings 2d and 13, DL-358, DL-369; the A11 rule recompute_and_compare, DL-336).

Analysis only: each hook reads STORED data only, through a `Context` (the same object scripts/run_A11.py builds), applies the stored evaluator or the plain definition of the
check, and returns the recomputed verdict WORD in the vocabulary of the logged word (MEETS, DOES NOT MEET, NOT JUDGED, REPORTED, FAIL, PASS, FAILED, NOT EVALUABLE, NOT INSIDE,
OPEN, PASSED WITH DEPARTURES, ...). A11 compares it with the logged verdict (`ms11_eval.assemble_rows`); a difference is flagged in the note column, never resolved. A recomputed
word with no entry in `a11_logged_verdict_map` gives status NOT EVALUABLE with the word kept and flagged (never silently mapped).

At 11d the hooks are written and tested on SYNTHETIC fixtures only (tests/test_ms11_hooks.py). `RealContext` reads the stored files; it has NOT been run on any real record. The real
recompute runs at the A11 evaluation step (the reviewer's instruction).

Independence is not claimed. Every hook shares at least the criteria loader (the frozen thresholds are read through the same gate) and, wherever a class enters, the frozen classifier
(the class tables were written by surge_metrics.classify_mode_d / classify_mode_n; the MS8 table also by the a7 pieces). The MS8 hooks call the SAME evaluator functions (`rb_eval`) that
made the logged verdicts; the MS10 hooks call the same `ms10_eval` functions and read the records with the Table 2.1 metrics path that calls the 9i function
(ms9_9i.j_exit_static_path); the MS9 hooks re-derive the verdict from the stored class tables by the plain definitions (M9-14, RB4), written anew here, but they read the class
column written by the frozen classifier. The independent recomputations of 8g, 9j and 10g (scripts/recompute_*.py, scripts/ms10_independent_check.py) are separate code paths and are not used here.
"""
from __future__ import annotations

import collections
import csv
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .. import config as C
from . import surge_metrics as M

SHARE_LOADER = "criteria loader"
SHARE_CLASSIFIER = "frozen classifier (class column)"
SHARE_EVALUATOR = "the original evaluator function (same code)"
SHARE_9I = "9i function (ms9_9i.j_exit_static_path via ms10_eval.table21_fields)"
SHARE_A7 = "a7 pieces that wrote the A7 table"

# The departure register of G6 (DL-208, docs/ms8_close.md, docs/ms8_g6_evidence.md section F): which non-MEETS component each logged departure covers. This is the reviewer's logged
# ruling, applied mechanically; it is not recomputed and it is not a judgement of the hook that the departures are acceptable.
G6_DEPARTURE_COVERS = {
    "RB3/a_inrange_runs": "G6-D1",
    "RB3/a_headline": "gate departure 3 (DL-163, RB3(a) not judged at the headline)",
    "RB6/solver_onset_headline": "G6-D2",
    "RB3/b_classifier_onset": "G6-D3",
}
G6_COMPONENTS = ("RB3/a_inrange_runs", "RB3/a_headline", "RB3/b_raw_crossing", "RB3/b_classifier_onset", "RB6/heun_headline", "RB6/solver_class_headline", "RB6/solver_onset_headline")


class HookError(Exception):
    pass


@dataclass(frozen=True)
class Hook:
    key: str                    # "<rb_id>/<check_id>" as in configs/ms11/ms11_eval.yaml a11_logged
    origin: str                 # MS8, MS9, MS10 or frozen criteria
    reads: str                  # what is read (stored files)
    shares: tuple               # components shared with the original evaluation
    fn: Callable = field(compare=False, repr=False, default=None)


STATUS_WORDS_LONGEST_FIRST = ("DOES NOT MEET", "NOT JUDGED", "NOT INSIDE", "NOT EVALUABLE", "UNDETERMINED", "INCOMPLETE", "REPORTED", "MEETS", "PASS", "FAIL")


def head_word(s: str) -> str:
    """The verdict word at the start of an rb_eval or ms10_eval status string ('REPORTED per path and per T_ramp (ruling 6)' -> 'REPORTED', 'NOT INSIDE (limitation; ...)' ->
    'NOT INSIDE'). A string that starts with no known word is cut at the first '(' and returned as it is, so the A11 map refuses it rather than a guess."""
    t = str(s).strip()
    for w in STATUS_WORDS_LONGEST_FIRST:
        if t == w or t.startswith(w + " ") or t.startswith(w + "("):
            return w
    return re.split(r"\s*\(", t, maxsplit=1)[0].strip()


# --- the context: the only way a hook sees data ----------------------------------------------------------------------------

class Context:
    """Data accessors. RealContext reads the stored files; tests subclass it with synthetic data. Each accessor is called by the hooks that need it and cached by the caller."""

    def ms8(self) -> dict:                 # {"df": DataFrame (A7 table), "fv": rb_eval.frozen_values}
        raise NotImplementedError

    def s16(self) -> dict:                 # {"rows": [{"run", "group" ("oat"|"lhs"), "class", "status"}], "nominal_class": str}
        raise NotImplementedError

    def subgrid(self) -> list:             # [{"i", "j", "seed", "class", "det"}]
        raise NotImplementedError

    def map1_classes(self) -> list:        # [class per map-1 cell]
        raise NotImplementedError

    def nc1(self) -> list:                 # [{"family", "class", "supplementary", "status"}]
        raise NotImplementedError

    def ms10(self) -> dict:                # the evaluate_ms10 result keys: rb1_headline, rb1_cells, N_sweep, rb1, sigma_check, rb8
        raise NotImplementedError

    def frozen(self) -> dict:              # {"rb4_oat_max", "rb4_oat_n", "rb4_lhs_n", "rb4_lhs_min_frac", "rb2_subgrid_min", "g5_min_frac", "rb8_m4_value"}
        raise NotImplementedError


def frozen_hook_leaves(crit: dict) -> dict:
    """The thresholds the MS9 and RB8 hooks use, from the frozen criteria dict (blob of the tag after the gate; never typed here)."""
    R = crit["robustness"]
    return {"rb4_oat_max": int(R["RB4"]["one_at_a_time_max_class_changes"]["value"]), "rb4_oat_n": int(R["RB4"]["one_at_a_time_runs"]["value"]),
            "rb4_lhs_n": int(R["RB4"]["latin_hypercube_points"]["value"]), "rb4_lhs_min_frac": float(R["RB4"]["latin_hypercube_min_class_unchanged"]["value"]),
            "rb2_subgrid_min": float(R["RB2"]["noisy_subgrid_agreement_min"]["value"]),
            "g5_min_frac": float(crit["gates"]["G5"]["surge_class_min_fraction_of_map1_cells"]["value"]),
            "rb8_m4_value": R["RB8"]["M4_criteria"]["value"]}


# --- MS8: the stored evaluator on the A7 table -------------------------------------------------------------------------------

def _rb_eval():
    from . import rb_eval
    return rb_eval


def _ms8_cache(ctx, name, fn):
    store = ctx.__dict__.setdefault("_hook_cache", {})
    if name not in store:
        d = ctx.ms8()
        store[name] = fn(d["df"], d["fv"])
    return store[name]


def _rb3a(ctx):
    return _ms8_cache(ctx, "rb3a", _rb_eval().rb3a)


def _rb3b(ctx):
    return _ms8_cache(ctx, "rb3b", _rb_eval().rb3b)


def _rb3c(ctx):
    return _ms8_cache(ctx, "rb3c", _rb_eval().rb3c)


def _rb3d(ctx):
    return _ms8_cache(ctx, "rb3d", _rb_eval().rb3d)


def _rb5(ctx):
    return _ms8_cache(ctx, "rb5", _rb_eval().rb5)


def _rb6h(ctx):
    return _ms8_cache(ctx, "rb6h", _rb_eval().rb6_heun)


def _rb6s(ctx):
    return _ms8_cache(ctx, "rb6s", _rb_eval().rb6_solvers)


def h_rb3a_inrange(ctx):
    r = _rb3a(ctx)["primary"]
    return {"word": r["status"], "detail": f"{r['n_within_one_step']} of {r['n_judged']} testable in-range runs within one A4 step"}


def h_rb3a_headline(ctx):
    h = _rb3a(ctx)["headline"]
    if h["in_range"]:
        return {"word": "MEETS" if (h["match_err_steps"] or 0.0) <= 1.0 else "DOES NOT MEET", "detail": "the headline lies inside the RB3(a) range: judged"}
    return {"word": head_word(h["status"]), "detail": f"headline not in range (match error {h['match_err_steps']} steps)"}


def h_rb3b_raw(ctx):
    return {"word": head_word(_rb3b(ctx)["status_by_onset"]["cross"]), "detail": "raw first crossing (primary reading, 8f2 ruling 1)"}


def h_rb3b_class(ctx):
    return {"word": head_word(_rb3b(ctx)["status_by_onset"]["class"]), "detail": "classifier onset (alternative reading kept beside the primary)"}


def h_rb3c(ctx):
    r = _rb3c(ctx)["primary"]
    return {"word": r["status"], "detail": f"P2 linear classes {r['classes']} against the headline class"}


def h_rb3d(ctx):
    return {"word": head_word(_rb3d(ctx)["status"]), "detail": "per path, no pooled verdict"}


def h_rb5_class(ctx):
    d = _rb5(ctx)["delta0_headline"]
    return {"word": d["status"], "detail": f"class unchanged over the delta0 ladder: {d['class_unchanged']}"}


def h_rb5_delay(ctx):
    rows = _rb5(ctx)["delta0_headline"]["ladder"]
    ok = all("delay_eta_shift_vs_1e-6" in r for r in rows)
    return {"word": "REPORTED" if ok else "NOT EVALUABLE", "detail": "delay shifts against the 1e-6 member are computed and reported, not tested"}


def h_rb5_start(ctx):
    return {"word": head_word(_rb5(ctx)["start_distance_P1_linear"]["status"]), "detail": "per T_ramp, no pooled verdict"}


def h_rb6_heun(ctx):
    r = _rb6h(ctx)["primary"]
    return {"word": r["status"], "detail": f"onset reading {r['onset']}; relative change against the bound"}


def h_rb6_solver_class(ctx):
    d = _rb6s(ctx)["dop853_vs_radau"]
    return {"word": "MEETS" if d["class_agree"] else "DOES NOT MEET", "detail": f"{d['dop853_headline_cls']} against {d['radau_cls']}"}


def h_rb6_solver_onset(ctx):
    d = _rb6s(ctx)["dop853_vs_radau"]
    b = d["bound_ms"]
    ok = abs(d["onset_diff_ms_class"]) <= b and abs(d["onset_diff_ms_cross"]) <= b
    return {"word": "MEETS" if ok else "DOES NOT MEET",
            "detail": f"onset difference {d['onset_diff_ms_class']:.3f} ms (classifier) and {d['onset_diff_ms_cross']:.3f} ms (raw crossing) against {b} ms"}


def h_rb6_rtol(ctx):
    return {"word": head_word(_rb6s(ctx)["rtol_1e-10_vs_1e-12"]["status"]), "detail": "reported against rtol, not a pass test"}


def h_g6(ctx, others: dict):
    """G6 (Table 11.2): RB3(a), RB3(b) and RB6 pass at the headline; RB3(d) and RB5 are reported. The word is PASSED if every gating component MEETS, PASSED WITH DEPARTURES if every
    component that does not MEET is covered by a logged departure of the register (G6_DEPARTURE_COVERS: the reviewer's ruling, DL-208), NOT PASSED otherwise."""
    bad = {k: others[k]["word"] for k in G6_COMPONENTS if others[k]["word"] != "MEETS"}
    uncovered = {k: w for k, w in bad.items() if k not in G6_DEPARTURE_COVERS}
    if not bad:
        word = "PASSED"
    elif uncovered:
        word = "NOT PASSED"
    else:
        word = "PASSED WITH DEPARTURES"
    covered = sorted({G6_DEPARTURE_COVERS[k] for k in bad if k in G6_DEPARTURE_COVERS})
    return {"word": word, "detail": f"components not MEETS: {bad or 'none'}; covered by departures {covered or 'none'}; uncovered {uncovered or 'none'} "
                                    "(the departures are the reviewer's ruling, DL-208; applied, not recomputed)"}


# --- MS9: the stored class tables ----------------------------------------------------------------------------------------------

def h_rb2_subgrid(ctx):
    """D24 (M9-14): per subgrid cell the modal raw class of the seeds against the deterministic class (Table 2.1 correspondence), a tie counts as disagreement; the cell fraction
    against the frozen minimum (203 of 225 at 0.90)."""
    f = ctx.frozen()
    by, det = collections.defaultdict(list), {}
    for r in ctx.subgrid():
        by[(r["i"], r["j"])].append(r["class"])
        det[(r["i"], r["j"])] = r["det"]
    n_ok = 0
    for c, cl in by.items():
        cnt = collections.Counter(cl)
        top = max(cnt.values())
        modal = [k for k, v in cnt.items() if v == top]
        n_ok += (len(modal) == 1) and M.classes_agree(det[c], modal[0])
    n = len(by)
    need = math.ceil(f["rb2_subgrid_min"] * n - 1e-12)
    return {"word": "PASS" if n and n_ok >= need else "FAILED", "detail": f"{n_ok} of {n} cells agree ({100 * n_ok / n:.1f} percent), {need} needed" if n else "no cells"}


def _rb4(ctx):
    f, s = ctx.frozen(), ctx.s16()
    oat = [r for r in s["rows"] if r["group"] == "oat"]
    lhs = [r for r in s["rows"] if r["group"] == "lhs"]
    changed = lambda r: r["class"] == M.FAILED or r["status"] != "ok" or r["class"] != s["nominal_class"]
    n_oat_changed, n_lhs_unchanged = sum(changed(r) for r in oat), sum(not changed(r) for r in lhs)
    need = math.ceil(f["rb4_lhs_min_frac"] * f["rb4_lhs_n"] - 1e-12)
    ok = len(oat) == f["rb4_oat_n"] and n_oat_changed <= f["rb4_oat_max"] and len(lhs) == f["rb4_lhs_n"] and n_lhs_unchanged >= need
    return ok, f"{n_oat_changed} of {len(oat)} one-at-a-time runs changed (at most {f['rb4_oat_max']}); {n_lhs_unchanged} of {len(lhs)} hypercube points unchanged ({need} needed)"


def h_rb4(ctx):
    ok, detail = _rb4(ctx)
    return {"word": "PASS" if ok else "FAIL", "detail": detail}


def h_g5(ctx):
    """G5 (Table 11.2): a surge class in at least the frozen fraction of map-1 cells and RB4 passes. Mode D, so the surge class is D-tr."""
    f = ctx.frozen()
    cl = ctx.map1_classes()
    n_s = sum(M.is_surge_class(c) for c in cl)
    need = math.ceil(f["g5_min_frac"] * len(cl) - 1e-12)
    rb4_ok, _ = _rb4(ctx)
    ok = bool(cl) and n_s >= need and rb4_ok
    return {"word": "PASSED, continue" if ok else "NOT PASSED", "detail": f"{n_s} of {len(cl)} map-1 cells in a surge class ({need} needed); RB4 {'passes' if rb4_ok else 'does not pass'}"}


def h_g7(ctx):
    """G7 (Table 11.2): NC1 has no surge class at every T_ramp. The pre-registered NC1 families (mean field, cells, network); the supplementary mode-N runs feed no gate."""
    rows = [r for r in ctx.nc1() if r["family"] in ("NC1", "NC1_cells", "NC1_net") and not r["supplementary"]]
    surge = [r for r in rows if M.is_surge_class(r["class"])]
    return {"word": "NOT PASSED" if surge else ("PASSED" if rows else "NOT EVALUABLE"),
            "detail": f"{len(surge)} of {len(rows)} NC1 runs in a surge class ({collections.Counter(r['class'] for r in surge) or 'none'})"}


# --- MS10: the stored evaluator on the S8 to S10 records ---------------------------------------------------------------------------

def h_rb1_headline(T):
    def fn(ctx):
        p = ctx.ms10()["rb1_headline"][T]
        return {"word": p["verdict"], "detail": f"T_ramp {T:g} s: {p.get('pass_count', 'n/a')} of {p['seeds_expected']} seeds pass"}
    return fn


def h_rb1_cells(ctx):
    c = ctx.ms10()["rb1_cells"]
    return {"word": c["verdict"], "detail": f"{c['n_agree']} of {c['n_cells']} cells agree ({c['need']} needed)"}


def h_rb1_n_rule(ctx):
    p = ctx.ms10()["N_sweep"]["no_worse"].get("pass")
    return {"word": "INCOMPLETE" if p is None else ("PASS" if p else "FAIL"), "detail": "N rule at 60 s (no worse with N)"}


def h_rb1_overall(ctx):
    return {"word": ctx.ms10()["rb1"]["verdict"], "detail": f"parts {ctx.ms10()['rb1']['parts']}"}


def h_rb8_het(ctx):
    r = ctx.ms10()["rb8"]
    return {"word": r["verdict"], "detail": r.get("reason", "")}


def h_sigma(ctx):
    r = ctx.ms10()["sigma_check"]
    word = head_word(r["verdict"])
    return {"word": word, "detail": f"mean-field baseline std {r.get('mf_baseline_std')} against the network range [{r.get('network_min')}, {r.get('network_max')}]"}


def h_rb8_m4(ctx):
    v = ctx.frozen()["rb8_m4_value"]
    return {"word": "OPEN" if v is None else "NOT EVALUABLE", "detail": "the frozen leaf RB8.M4_criteria has no value (F-23, deferred; MS12)" if v is None else "the M4 criteria now have a value; no evaluator is wired"}


# --- the registry: 26 hooks, one per row of a11_logged ----------------------------------------------------------------------------------

_MS8_SHARES = (SHARE_LOADER, SHARE_CLASSIFIER, SHARE_EVALUATOR, SHARE_A7)
_MS9_SHARES = (SHARE_LOADER, SHARE_CLASSIFIER)
_MS10_SHARES = (SHARE_LOADER, SHARE_CLASSIFIER, SHARE_EVALUATOR, SHARE_9I)
A7_TABLE = "results/A7/a7_ramp_metrics.parquet"

HOOKS: dict = {h.key: h for h in [
    Hook("RB3/a_inrange_runs", "MS8", A7_TABLE + " -> rb_eval.rb3a", _MS8_SHARES, h_rb3a_inrange),
    Hook("RB3/a_headline", "MS8", A7_TABLE + " -> rb_eval.rb3a", _MS8_SHARES, h_rb3a_headline),
    Hook("RB3/b_raw_crossing", "MS8", A7_TABLE + " -> rb_eval.rb3b", _MS8_SHARES, h_rb3b_raw),
    Hook("RB3/b_classifier_onset", "MS8", A7_TABLE + " -> rb_eval.rb3b", _MS8_SHARES, h_rb3b_class),
    Hook("RB3/c_T_ramp_56_to_316", "MS8", A7_TABLE + " -> rb_eval.rb3c", _MS8_SHARES, h_rb3c),
    Hook("RB3/d_profile", "MS8", A7_TABLE + " -> rb_eval.rb3d", _MS8_SHARES, h_rb3d),
    Hook("RB5/delta0_headline_class", "MS8", A7_TABLE + " -> rb_eval.rb5", _MS8_SHARES, h_rb5_class),
    Hook("RB5/delta0_headline_delay", "MS8", A7_TABLE + " -> rb_eval.rb5", _MS8_SHARES, h_rb5_delay),
    Hook("RB5/start_distance", "MS8", A7_TABLE + " -> rb_eval.rb5", _MS8_SHARES, h_rb5_start),
    Hook("RB6/heun_headline", "MS8", A7_TABLE + " -> rb_eval.rb6_heun", _MS8_SHARES, h_rb6_heun),
    Hook("RB6/solver_class_headline", "MS8", A7_TABLE + " -> rb_eval.rb6_solvers", _MS8_SHARES, h_rb6_solver_class),
    Hook("RB6/solver_onset_headline", "MS8", A7_TABLE + " -> rb_eval.rb6_solvers", _MS8_SHARES, h_rb6_solver_onset),
    Hook("RB6/rtol_headline", "MS8", A7_TABLE + " -> rb_eval.rb6_solvers", _MS8_SHARES, h_rb6_rtol),
    Hook("G6/gate", "MS8", "the seven MS8 component hooks above + the departure register (DL-208)", _MS8_SHARES + ("the reviewer's departure ruling (applied, not recomputed)",), None),
    Hook("RB2/noisy_subgrid_agreement", "MS9", "results/ms9/9f/subgrid_classes.csv (per-run classes) by the M9-14 definition", _MS9_SHARES, h_rb2_subgrid),
    Hook("RB4/parameter_perturbation", "MS9", "results/ms9/9d/s16_classes.csv + configs/ms9/runlists/runlist_S16.csv + the S5 headline class", _MS9_SHARES, h_rb4),
    Hook("G5/gate", "MS9", "results/ms9/9e/map1_classes.csv + the RB4 hook", _MS9_SHARES, h_g5),
    Hook("G7/gate", "MS9", "results/ms9/nc1_classes.csv", _MS9_SHARES, h_g7),
    Hook("RB1/headline_10s", "MS10", "results/S8, S9, S10 (+ C2) records -> ms10_eval.rb1_headline", _MS10_SHARES, h_rb1_headline(10.0)),
    Hook("RB1/headline_120s", "MS10", "results/S8, S9, S10 (+ C2) records -> ms10_eval.rb1_headline", _MS10_SHARES, h_rb1_headline(120.0)),
    Hook("RB1/cells_30s", "MS10", "results/S8 records -> ms10_eval.rb1_cells", _MS10_SHARES, h_rb1_cells),
    Hook("RB1/n_rule_60s", "MS10", "results/S9 records -> ms10_eval.n_sweep", _MS10_SHARES, h_rb1_n_rule),
    Hook("RB1/overall", "MS10", "ms10_eval.rb1_overall over the three parts", _MS10_SHARES, h_rb1_overall),
    Hook("RB8/heterogeneity", "MS10", "results/S10 records -> ms10_eval.rb8", _MS10_SHARES, h_rb8_het),
    Hook("sigma_check/S8_baseline_std", "MS10", "results/S8 headline records -> ms10_eval.sigma_check", _MS10_SHARES, h_sigma),
    Hook("RB8/m4_adaptation", "frozen criteria", "the RB8.M4_criteria leaf of the tag blob", (SHARE_LOADER,), h_rb8_m4),
]}
# the key of the sigma row in a11_logged is sigma_check/S8_baseline_std (rb_id sigma_check)


def run_hooks(ctx: Context, ch: dict, only=None) -> dict:
    """{key: {"word", "status", "reads", "shares", "detail"}} for every hook (or the keys in `only`). The status is the A11 status word of the recomputed word through the same
    a11_logged_verdict_map as the logged words; a recomputed word with no entry gives NOT EVALUABLE with the word kept and flagged. An exception in a hook propagates (nothing is skipped)."""
    from . import ms11_eval as E
    out: dict = {}
    keys = [k for k in HOOKS if only is None or k in only]
    order = [k for k in keys if k != "G6/gate"] + (["G6/gate"] if "G6/gate" in keys else [])
    for k in order:
        h = HOOKS[k]
        r = g6_inputs_hook(ctx, out) if k == "G6/gate" else h.fn(ctx)
        try:
            status = E.map_logged(r["word"], ch)
            detail = r.get("detail", "")
        except E.UnmappedVerdict:
            status, detail = E.NE, (r.get("detail", "") + "; " if r.get("detail") else "") + f"recomputed word {r['word']!r} has no entry in a11_logged_verdict_map"
        out[k] = {"word": r["word"], "status": status, "reads": h.reads, "shares": list(h.shares), "detail": detail}
    return out


def g6_inputs_hook(ctx, done: dict) -> dict:
    """G6 needs the seven component words; they are taken from the hooks already run (all seven are MS8 hooks and run first)."""
    missing = [k for k in G6_COMPONENTS if k not in done]
    if missing:
        raise HookError(f"G6/gate needs the component hooks {missing}")
    return h_g6(ctx, done)


def registered_keys() -> list:
    return list(HOOKS)


def check_registry(logged: list) -> None:
    """The 26 hooks and the 26 carried rows of a11_logged are the same set; a row without a hook, or a hook without a row, stops A11 (nothing is silently carried)."""
    rows = {f"{e['rb_id']}/{e['check_id']}" for e in logged}
    if rows != set(HOOKS):
        raise HookError(f"a11_logged rows without a hook: {sorted(rows - set(HOOKS))}; hooks without a row: {sorted(set(HOOKS) - rows)}")


# --- the real context (written now, NOT run on real records at 11d) -------------------------------------------------------------------------

class RealContext(Context):
    """Reads the stored files under `root` (the repository root by default; `results_root` redirects the `results/` prefix, used by the fabricated-record test). Opens nothing at construction."""

    def __init__(self, root=None, results_root=None):
        self.root = Path(root) if root else C.repo_root()
        self.results_root = Path(results_root) if results_root else self.root / "results"
        self._cache: dict = {}

    def res(self, rel: str) -> Path:
        rel = str(rel).replace("\\", "/")
        return self.results_root / rel[len("results/"):] if rel.startswith("results/") else self.root / rel

    def _once(self, name, fn):
        if name not in self._cache:
            self._cache[name] = fn()
        return self._cache[name]

    @staticmethod
    def _csv(path) -> list:
        with Path(path).open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def ms8(self):
        def load():
            import pandas as pd
            from . import a7 as A7
            rb = _rb_eval()
            fi, _ = A7.frozen_inputs(self.root)                  # criteria gate first
            fv = rb.frozen_values(self.root)
            df = pd.read_parquet(self.res(A7_TABLE))
            if set(df.criteria_sha256) != {fi["criteria_sha256"]}:
                raise HookError("the A7 table was written under a different frozen file")
            return {"df": df, "fv": fv}
        return self._once("ms8", load)

    def frozen(self):
        def load():
            from .. import criteria as CR
            crit, _ = CR.load_frozen_criteria(self.root)
            return frozen_hook_leaves(crit)
        return self._once("frozen", load)

    def s16(self):
        def load():
            meta = {r["name"]: r for r in self._csv(self.root / "configs/ms9/runlists/runlist_S16.csv")}
            rows = []
            for r in self._csv(self.res("results/ms9/9d/s16_classes.csv")):
                m = meta[r["run"]]
                rows.append({"run": r["run"], "group": "oat" if m["family"] == "S16_oat" else "lhs", "class": r["class"], "status": r["status"]})
            head = self._csv(self.res("results/ms9/9d/s5_headline_classes.csv"))
            sel = [h for h in head if h["path_name"] == "path_hypoxia" and abs(float(h["T_ramp_s"]) - 120.0) < 1e-9 and h["mode"] == "D"]
            if len(sel) != 1:
                raise HookError(f"expected one S5 P2 linear 120 s mode-D headline row, found {len(sel)}")
            return {"rows": rows, "nominal_class": sel[0]["class"]}
        return self._once("s16", load)

    def subgrid(self):
        return self._once("subgrid", lambda: [{"i": int(r["i"]), "j": int(r["j"]), "seed": int(r["seed"]), "class": r["class"], "det": r["det"]}
                                              for r in self._csv(self.res("results/ms9/9f/subgrid_classes.csv"))])

    def map1_classes(self):
        return self._once("map1", lambda: [r["class"] for r in self._csv(self.res("results/ms9/9e/map1_classes.csv"))])

    def nc1(self):
        return self._once("nc1", lambda: [{"family": r["family"], "class": r["class"], "supplementary": str(r["supplementary"]).lower() == "true", "status": r["status"]}
                                          for r in self._csv(self.res("results/ms9/nc1_classes.csv"))])

    def ms10(self):
        def load():
            from . import a7 as A7
            from . import ms10_eval as E10
            from . import ms10_runlist as RL10
            fi, gate = A7.frozen_inputs(self.root)
            fr = E10.frozen_rb1()
            ch = E10.load_choices()
            lists = ("S8", "S9", "S10", "C2_S8", "C2_S9", "C2_S10")
            by = E10.read_lists(lists, fi, table21=True)
            refs = E10.mf_references(fi)
            controls = [r for n in RL10.CONTROL_LISTS for r in by[n]]
            s8h = [r for r in by["S8"] if r["name"].startswith("S8_head")]
            s8c = [r for r in by["S8"] if r["name"].startswith("S8_cells")]
            res = {"rb1_headline": E10.rb1_headline(s8h, refs, controls, ch, fr), "rb1_cells": E10.rb1_cells(s8c, refs, controls, E10.stored_120s_classes(), fr),
                   "N_sweep": E10.n_sweep(by["S9"], refs.get(("head", 60.0)), controls, ch, fr, metrics=True)}
            res["rb1"] = E10.rb1_overall(res["rb1_headline"], res["rb1_cells"], res["N_sweep"])
            res["sigma_check"] = E10.sigma_check(s8h, ch)
            res["rb8"] = E10.rb8(by["S10"], controls, refs.get(("head", 60.0)), ch, fr)
            return res
        return self._once("ms10", load)
