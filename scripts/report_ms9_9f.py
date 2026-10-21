"""MS9 9f report: map 2 + noisy-subgrid completion, map-2 classes and A9 labels, D24 subgrid agreement, and a stored-record diagnostic of the
unlabelled map-1 cells (DL-237 to DL-240). Analysis only: integrates nothing, adds no label, feeds no gate.

  report_ms9_9f.py [--out-dir results/ms9/9f]

Part 1 completion from the journal and the stored records (counts, wall, restarts, commit and git.dirty of every record).
Part 2 map 2 (J0 25 x T_ramp 13, Delta 0.3, tau_d 5 ms): classes, text grid, A9 labels (M9-12 as logged, A4 tables of the map-1 axes), A9 check.
Part 3 D24 (M9-14): modal class of the 10 seeds per subgrid cell against the map-1 deterministic class (Table 2.1 correspondence), a tie counts
        as disagreement; per-run agreement; cells with >= 8 of 10 seeds agreeing; breakdown by deterministic class; disagreeing cells.
Part 4 diagnostic on the STORED map-1 records and A4 only, for the unlabelled non-surge cells and the isolated interior D-none cells: A4 Hopf
        frequency, time inside the oscillatory region, max envelope / A_ref (G band 25 to 100 Hz as the classifier, and the total band 1 to 150 Hz),
        the spectral peak of v after t_on, and the classifier clause that left the cell D-none (re-running the frozen classifier, same arguments).
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from mprsurge import config as C
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import a9 as A9
from mprsurge.analysis import ms9_classify as MCL
from mprsurge.analysis import ms9_runlist as RL
from mprsurge.analysis import surge_metrics as M

SYM = {"D-tr": "T", "D-sus": "s", "D-none": ".", "failed": "F"}
ISOLATED = [(2, 20), (3, 18), (3, 20), (11, 14)]
MIN_AGREE_FRACTION = 0.90
SEEDS = 10


def sha(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def journal(path) -> dict:
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    log = Path(path).with_name("run.log").read_text(encoding="utf-8").splitlines()
    return {"rows": rows, "launch_lines": sum("runs from" in x for x in log),
            "finished": [x.split("INFO ")[-1] for x in log if "finished:" in x]}


def corresponds(det: str, noisy: str) -> bool:
    return M.classes_agree(det, noisy)


def cell_agreement(det: str, seed_classes: list[str]) -> dict:
    """D24 rule of M9-14 for one cell: modal class of the seeds (a tie for the top count = disagreement), plus the >= 8 of 10 count."""
    cnt = collections.Counter(seed_classes)
    top = max(cnt.values())
    modal = [k for k, v in cnt.items() if v == top]
    tie = len(modal) > 1
    n_agree = sum(corresponds(det, c) for c in seed_classes)
    # sensitivity (reading ours, reported beside): mode of the Table 2.1 categories instead of the raw classes
    cat = collections.Counter(("surge" if M.is_surge_class(c) else c) for c in seed_classes)
    ctop = max(cat.values())
    cmodal = [k for k, v in cat.items() if v == ctop]
    return {"counts": dict(sorted(cnt.items())), "modal": None if tie else modal[0], "tie": tie,
            "cell_agrees": (not tie) and corresponds(det, modal[0]), "n_seed_agree": n_agree, "ge8": n_agree >= 8,
            "cat_agrees": len(cmodal) == 1 and ((cmodal[0] == "surge" and det == "D-tr") or (cmodal[0] == "S-sus" and det == "D-sus")
                                                or (cmodal[0] == "NS" and det == "D-none"))}


def load_records(root, lists, fi, d_axis, t_axis, ij_of=None):
    """Classify every stored record under root; one dict per record with the record's cfg fields and the frozen class."""
    out, git = [], collections.Counter()
    for jp in MCL.record_files(root):
        rec = json.loads(jp.read_text(encoding="utf-8"))
        git[(rec["git"]["commit"], rec["git"]["dirty"], rec["status"])] += 1
        out.append((jp, rec))
    return out, git


def print_grid(title, grid, n_rows, n_cols, row_lab, col_head, sym):
    print(title)
    print("      " + col_head)
    for i in range(n_rows):
        print(f"{i:2d}    " + "".join(sym.get(grid.get((i, j), ""), "?") for j in range(n_cols)) + f"   {row_lab(i)}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="report_ms9_9f")
    ap.add_argument("--out-dir", default="results/ms9/9f")
    ap.add_argument("--journal", default="results/ms9/launch_map2_subgrid/manifest.csv")
    ap.add_argument("--map1-csv", default="results/ms9/9e/map1_classes.csv")
    args = ap.parse_args(argv)
    root = C.repo_root()
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    fi, gate = A7.frozen_inputs()
    h, thr, a_ref = fi["grid_step"], fi["threshold"], fi["a_ref"]
    print(f"criteria gate ok: tag {gate['tag']}, threshold {thr:.6f}, A_ref {a_ref:.6f}")
    print(f"9e map1_classes.csv sha256 {sha(root / args.map1_csv)}")

    # ---- part 1: completion ------------------------------------------------------------------------------------------------
    jr = journal(root / args.journal)
    rows = jr["rows"]
    st = collections.Counter(r["status"] for r in rows)
    expected = {r["name"] for n in ("S7_map2", "S7_subgrid") for r in RL.expand(n)}
    names = [r["name"] for r in rows]
    print(f"\nPART 1 completion: journal rows {len(rows)}, unique names {len(set(names))}, status {dict(st)}; expected {len(expected)} "
          f"(325 + 2250); missing from journal {len(expected - set(names))}; not expected {len(set(names) - expected)}")
    print(f"launch lines in run.log ('runs from'): {jr['launch_lines']} (restarts {max(jr['launch_lines'] - 1, 0)}); finished: {jr['finished']}")
    wall = float(jr["finished"][-1].split("wall")[-1].strip().rstrip("s")) if jr["finished"] else float("nan")
    print(f"total wall {wall:.1f} s = {wall / 3600:.2f} h against 2.60 h predicted (limit 3.3 h)")
    print(f"sum of per-run wall (journal) {sum(float(r['wall_time_s']) for r in rows):.0f} s")

    cells1 = [c for c in RL.load_cells() if c["kind"] == "map1"]
    d_axis = sorted({c["Delta"] for c in cells1})
    t_axis = sorted({c["tau_d_ms"] for c in cells1})
    ij1 = {(round(c["Delta"], 12), round(c["tau_d_ms"], 12)): tuple(c["ij"]) for c in cells1}

    m2, git2 = load_records(root / "results/S7/S7_map2", None, fi, d_axis, t_axis)
    sg, gitg = load_records(root / "results/S7/S7_subgrid", None, fi, d_axis, t_axis)
    print(f"records on disk: map 2 {len(m2)}, subgrid {len(sg)}; (commit, git.dirty, status) counts: map 2 {dict(git2)}; subgrid {dict(gitg)}")
    disk = {jp.stem for jp, _ in m2} | {jp.stem for jp, _ in sg}
    print(f"expected names without a record on disk: {len(expected - disk)}; records not in the run lists: {len(disk - expected)}")
    nonok = [jp.stem for jp, rec in m2 + sg if rec["status"] != "ok"]
    if len(rows) != 2575 or st.get("ok", 0) != 2575 or nonok or expected - disk:
        print("STOP: a run failed or is missing; no rerun, no further analysis", nonok[:10])
        return 4

    # ---- part 2: map 2 ----------------------------------------------------------------------------------------------------
    j_axis = sorted({float(rec["config"]["path"]["J0"]) for _, rec in m2})
    T_axis = sorted({float(rec["config"]["path"]["T_ramp_s"]) for _, rec in m2})
    print(f"\nPART 2 map 2: J0 axis {len(j_axis)} ({j_axis[0]:g}..{j_axis[-1]:g}), T_ramp axis {len(T_axis)} ({T_axis[0]:g}..{T_axis[-1]:g} s)")
    r2 = []
    for jp, rec in m2:
        cfg = rec["config"]
        J0, T = float(cfg["path"]["J0"]), float(cfg["path"]["T_ramp_s"])
        D, td, tau = cfg["model"]["Delta"], cfg["model"]["tau_d_ms"], cfg["model"]["tau_ms"]
        inside, t_in = A9.path_region(cfg, h)
        r = MCL.classify_record(jp, fi, inside_a4_region=inside)
        lab = A9.labels(r["class"], r["label_f"], A9.hopf_point(J0, D, td, tau), A9.delta_max(J0, td, d_axis, tau),
                        A9.taud_interval(J0, D, t_axis, tau), D, td, t_in)
        hp = A9.hopf_point(J0, D, td, tau)
        r2.append({"run": jp.stem, "i": j_axis.index(J0), "k": T_axis.index(T), "J0": J0, "T_ramp_s": T, "Delta": D, "tau_d_ms": td,
                   "git_commit": rec["git"]["commit"], "git_dirty": rec["git"]["dirty"], "class": r["class"], "surge": r["surge"],
                   "inside_a4_region": inside, "time_inside_s": t_in, "hopf_f_hz": "" if hp is None else hp["f_hz"],
                   "labels_all": "".join(lab["all"]), "label_primary": lab["primary"] or "", "label_f": r["label_f"],
                   "onset_s": r["onset_s"], "f_pk_hz": r["f_pk_hz"], "reason": r["reason"]})
    r2.sort(key=lambda r: (r["i"], r["k"]))
    with open(out_dir / "map2_classes.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(r2[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(r2)
    cnt = collections.Counter(r["class"] for r in r2)
    print("class counts:", {k: cnt.get(k, 0) for k in ("D-tr", "D-sus", "D-none", "failed")}, "other:", {k: v for k, v in cnt.items() if k not in SYM})
    grid = {(r["i"], r["k"]): r["class"] for r in r2}
    print_grid("\nclass grid (rows: J0 index ascending downwards, -40 to -5; columns: T_ramp index 0..12, 1 to 1000 s log); T = D-tr, s = D-sus, . = D-none, F = failed",
               grid, len(j_axis), len(T_axis), lambda i: f"J0={j_axis[i]:.4f}", "".join(f"{k % 10}" for k in range(len(T_axis))), SYM)
    print("T_ramp axis:", ", ".join(f"{T:.4g}" for T in T_axis))
    print("D-tr per T_ramp column:", {k: sum(1 for r in r2 if r["k"] == k and r["class"] == "D-tr") for k in range(len(T_axis))})
    print("D-tr per J0 row:", {i: sum(1 for r in r2 if r["i"] == i and r["class"] == "D-tr") for i in range(len(j_axis))})
    non = [r for r in r2 if not r["surge"]]
    lgrid = {(r["i"], r["k"]): ("-" if r["surge"] else (r["label_primary"] or "?")) for r in r2}
    print_grid("\nA9 primary label grid (- = surge class, ? = unlabelled)", lgrid, len(j_axis), len(T_axis), lambda i: f"J0={j_axis[i]:.4f}",
               "".join(f"{k % 10}" for k in range(len(T_axis))), {c: c for c in "abcdef-?"})
    prim = collections.Counter(r["label_primary"] or "none" for r in non)
    anyc = collections.Counter(ch for r in non for ch in r["labels_all"])
    print(f"A9 labels over {len(non)} non-surge cells: primary {dict(sorted(prim.items()))}; any {dict(sorted(anyc.items()))}")
    print("combinations:", dict(collections.Counter(r["labels_all"] or "none" for r in non).most_common()))
    print("Hopf frequency (Hz) per J0 row at Delta 0.3, tau_d 5 ms:", {i: (None if r2[i * len(T_axis)]["hopf_f_hz"] == "" else round(r2[i * len(T_axis)]["hopf_f_hz"], 1)) for i in range(len(j_axis))})
    art = [r for r in r2 if r["surge"] and r["inside_a4_region"] is not True]
    print(f"A9 check: surge-class cells {len([r for r in r2 if r['surge']])}; without Re lambda > 0 along the path: {len(art)}", [(r["i"], r["k"]) for r in art])

    # ---- part 3: D24 ------------------------------------------------------------------------------------------------------
    print("\nPART 3 D24 (subgrid, mode N, Table 2.1 correspondence)")
    det = {}
    with open(root / args.map1_csv, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            det[(int(r["i"]), int(r["j"]))] = r["class"]
    rg = []
    for jp, rec in sg:
        cfg = rec["config"]
        ij = ij1[(round(cfg["model"]["Delta"], 12), round(cfg["model"]["tau_d_ms"], 12))]
        r = MCL.classify_record(jp, fi)
        rg.append({"run": jp.stem, "i": ij[0], "j": ij[1], "seed": r["seed"], "class": r["class"], "det": det[ij], "W_s": r["W_s"],
                   "git_commit": rec["git"]["commit"], "git_dirty": rec["git"]["dirty"], "agree": corresponds(det[ij], r["class"])})
    rg.sort(key=lambda r: (r["i"], r["j"], r["seed"]))
    with open(out_dir / "subgrid_classes.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rg[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rg)
    runs_by_cell = collections.defaultdict(list)
    for r in rg:
        runs_by_cell[(r["i"], r["j"])].append(r)
    print("subgrid cells", len(runs_by_cell), "seeds per cell", dict(collections.Counter(len(v) for v in runs_by_cell.values())))
    print("class counts over", len(rg), "runs:", dict(sorted(collections.Counter(r["class"] for r in rg).items())))
    excluded = [c for c in runs_by_cell if det[c] == "failed"]
    res = {c: cell_agreement(det[c], [r["class"] for r in v]) for c, v in runs_by_cell.items() if c not in excluded}
    n = len(res)
    n_ok = sum(v["cell_agrees"] for v in res.values())
    need = int(np.ceil(MIN_AGREE_FRACTION * n))
    print(f"deterministic failed cells excluded: {excluded}")
    print(f"AGREEMENT (modal class, tie = disagreement): {n_ok} of {n} cells = {100 * n_ok / n:.2f}%; 90% needs at least {need} of {n}")
    print(f"  ties: {sum(v['tie'] for v in res.values())}; sensitivity, mode of the Table 2.1 categories (surge / S-sus / NS), reading ours: "
          f"{sum(v['cat_agrees'] for v in res.values())} of {n}")
    pr = sum(r["agree"] for r in rg)
    print(f"per-run agreement: {pr} of {len(rg)} = {100 * pr / len(rg):.2f}%")
    print(f"cells with >= 8 of 10 seeds agreeing: {sum(v['ge8'] for v in res.values())} of {n}")
    for d in ("D-tr", "D-sus", "D-none"):
        cs = [c for c in res if det[c] == d]
        if cs:
            print(f"  det {d}: {len(cs)} cells; cell agreement {sum(res[c]['cell_agrees'] for c in cs)}; >= 8 of 10: {sum(res[c]['ge8'] for c in cs)}; "
                  f"per-run {sum(r['agree'] for c in cs for r in runs_by_cell[c])} of {10 * len(cs)}")
    dis = sorted(c for c in res if not res[c]["cell_agrees"])
    print(f"disagreeing cells ({len(dis)}): (i, j) det | seed class counts | modal")
    for c in dis:
        print(f"  {c} {det[c]} | {res[c]['counts']} | {'tie' if res[c]['tie'] else res[c]['modal']}")
    with open(out_dir / "subgrid_cells.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["i", "j", "det", "modal", "tie", "cell_agrees", "n_seed_agree", "counts"])
        for c in sorted(res):
            v = res[c]
            w.writerow([c[0], c[1], det[c], v["modal"] or "", v["tie"], v["cell_agrees"], v["n_seed_agree"], json.dumps(v["counts"])])

    # ---- part 4: diagnostic of stored map-1 records ----------------------------------------------------------------------
    print("\nPART 4 diagnostic (stored map-1 records and A4 only; no simulation, no new label)")
    m1 = {}
    with open(root / args.map1_csv, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            m1[(int(r["i"]), int(r["j"]))] = r
    unl = sorted(c for c, r in m1.items() if r["class"] != "D-tr" and r["label_primary"] == "")
    iso_cells = ISOLATED
    todo = sorted(set(unl) | set(iso_cells))
    print(f"unlabelled non-surge cells {len(unl)}; isolated cells {iso_cells}; examined {len(todo)}")
    recdir = root / "results/S7/S7_map1"
    diag = []
    for c in todo:
        r = m1[c]
        jp = recdir / (r["run"] + ".json")
        rec = json.loads(jp.read_text(encoding="utf-8"))
        cfg = rec["config"]
        with np.load(jp.with_suffix(".npz")) as z:
            v = z["v"]
        fs = MCL.fs_of(cfg)
        t_on = cfg["path"]["t_on_s"]
        i_on = int(round(t_on * fs))
        inside, t_in = A9.path_region(cfg, h)
        res_c = M.classify_mode_d(v, fs, t_on, float(cfg["path"]["T_ramp_s"]), thr, inside_a4_region=inside)
        envG = M.envelope(v, fs, M.G_BAND)[i_on:]
        envT = M.envelope(v, fs, M.TOTAL_BAND)[i_on:]
        x = np.asarray(v[i_on:], float)
        x = x - x.mean()
        spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
        fr = np.fft.rfftfreq(len(x), 1 / fs)
        sel = fr >= 1.0
        fpk = float(fr[sel][np.argmax(spec[sel])])
        D, td, J0, tau = cfg["model"]["Delta"], cfg["model"]["tau_d_ms"], float(cfg["path"]["J0"]), cfg["model"]["tau_ms"]
        hp = A9.hopf_point(J0, D, td, tau)
        # the clause: threshold (envelope never reaches), 10-cycle minimum (reaches, no run of 10 cycles), D8 (damped), band G (peak outside G)
        why = res_c.reason
        clause = {"envelope never reaches the threshold": "threshold", "no run of the minimum cycles": "10-cycle minimum",
                  "damped (D8)": "damped (D8)"}.get(why, "other: " + why)
        band_g = not (M.G_BAND[0] <= fpk <= M.G_BAND[1])
        diag.append({"i": c[0], "j": c[1], "Delta": D, "tau_d_ms": td, "isolated": c in iso_cells, "class": res_c.cls, "clause": clause,
                     "hopf_f_hz": "" if hp is None else hp["f_hz"], "time_inside_s": t_in, "inside": inside,
                     "maxenv_G_over_Aref": float(envG.max() / a_ref), "maxenv_total_over_Aref": float(envT.max() / a_ref),
                     "thr_over_Aref": thr / a_ref, "v_peak_hz": fpk, "peak_outside_G": band_g, "labels_csv": r["labels_all"],
                     "primary_csv": r["label_primary"], "label_f_csv": r["label_f"], "csv_class": r["class"]})
    with open(out_dir / "map1_unlabelled_diag.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(diag[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(diag)
    print("check: re-run classifier class equals the stored class for", sum(d["class"] == d["csv_class"] for d in diag), "of", len(diag), "cells")
    print(f"reference: threshold / A_ref = {thr / a_ref:.3f}")

    def line(d):
        f = "none" if d["hopf_f_hz"] == "" else f"{d['hopf_f_hz']:.1f}"
        return (f"  ({d['i']:2d},{d['j']:2d}) Delta {d['Delta']:.4f} tau_d {d['tau_d_ms']:7.3f} ms | A4 f {f:>6s} Hz | inside {d['time_inside_s']:7.2f} s "
                f"| max env G/A_ref {d['maxenv_G_over_Aref']:.4f} (total band {d['maxenv_total_over_Aref']:.4f}) | v peak {d['v_peak_hz']:.1f} Hz "
                f"| labels '{d['labels_csv']}'")

    unl_d = [d for d in diag if (d["i"], d["j"]) in unl]
    print(f"\nunlabelled cells ({len(unl_d)}) grouped by classifier clause:")
    for cl in sorted({d["clause"] for d in unl_d}):
        g = [d for d in unl_d if d["clause"] == cl]
        print(f" clause: {cl} ({len(g)} cells); peak outside G in {sum(d['peak_outside_G'] for d in g)}; inside region (Re lambda > 0) in {sum(d['inside'] for d in g)}")
        for d in g:
            print(line(d))
    print("\nisolated interior D-none cells:")
    for d in diag:
        if d["isolated"]:
            print(line(d) + f" | primary '{d['primary_csv']}' | label_f {d['label_f_csv']} | clause: {d['clause']}")
    print(f"\nwritten {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
