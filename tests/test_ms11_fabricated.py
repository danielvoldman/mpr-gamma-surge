"""MS11 11d: the REAL-DATA PATH of scripts/run_A11.py tested on FABRICATED records (DL-373). Code path only: the records are made up (tests/fabricate_ms11.py), live in pytest's
temporary folder (never under results/), carry the label "fabricated", are deleted with the folder and are never evaluated as results. No stored MS8 to MS10 record is read."""
import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

import fabricate_ms11 as FAB
from mprsurge import provenance as P
from mprsurge.analysis import a7 as A7
from mprsurge.analysis import ms10_eval as E10
from mprsurge.analysis import ms11_eval as E
from mprsurge.analysis import ms11_eval_choices as EC
from mprsurge.analysis import ms11_hooks as HK
from mprsurge.analysis import ms11_runlist as RL

ROOT = Path(__file__).resolve().parents[1]


def _load_script():
    spec = importlib.util.spec_from_file_location("run_A11", ROOT / "scripts/run_A11.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def fab(tmp_path_factory):
    """One fabricated tree for the module (the series are the only made-up part)."""
    root = tmp_path_factory.mktemp("fabricated_results")
    res = root / "results"
    info = FAB.build_all(res)
    return res, info


@pytest.mark.slow
def test_the_fabricated_tree_is_outside_the_repository_results_folder_and_labelled(fab):
    res, info = fab
    assert (ROOT / "results").resolve() not in res.resolve().parents and res.resolve() != (ROOT / "results").resolve()
    assert info["lists"] == {"MS11_S11": 120, "MS11_CTRL": 30, "MS11_S13_MF": 68, "MS11_S13_NET": 18, "MS11_RB9D": 2}
    rec = json.loads(next((res / "RB9D/RB9D").glob("*.json")).read_text(encoding="utf-8"))
    assert FAB.FABRICATED in rec["message"] and rec["flags"] == {"fabricated": True}


@pytest.mark.slow
def test_every_fabricated_record_has_the_real_layout_eight_float64_arrays_at_1_khz(fab):
    res, _ = fab
    z = np.load(next((res / "S13/ms11/S13_rtol").glob("*.npz")))
    assert sorted(z.files) == sorted(FAB.ARRAYS) and all(z[k].dtype == np.float64 for k in z.files)
    assert z["t_ms"][0] == 0.0 and z["t_ms"][1] - z["t_ms"][0] == pytest.approx(1.0)
    rec = json.loads(next((res / "S13/ms11/S13_rtol").glob("*.json")).read_text(encoding="utf-8"))
    for k in ("config", "config_hash", "config_hash12", "criteria_sha256", "dry_run", "flags", "git", "name", "status", "wall_time_s", "outputs", "inputs", "seed", "solver", "warnings"):
        assert k in rec, k


@pytest.mark.slow
def test_record_lookup_by_run_id_and_hash_reads_every_listed_record_and_refuses_a_wrong_hash_or_a_dirty_flag(fab, tmp_path):
    res, _ = fab
    fi, _ = A7.frozen_inputs()
    by = E.read_lists(fi, results_root=res)
    assert {n: len(v) for n, v in by.items()} == RL.EXPECTED_COUNTS
    assert not any(r.get("missing") for v in by.values() for r in v)
    rows = E.redirect_rows(RL.expand("MS11_RB9D"), res)
    assert [r["tau_ms"] for r in by["MS11_RB9D"]] == [8.0, 12.0] and by["MS11_RB9D"][0]["name"] == rows[0]["name"]
    rec = E.read_record(rows[0], fi)                                       # lookup by the listed name; the hash and name are checked against the frozen row
    assert rec["class"] in ("D-tr", "D-none", "D-sus") and not rec.get("missing")
    p = Path(rows[0]["out_dir"]) / f"{rows[0]['name']}.json"
    good = p.read_text(encoding="utf-8")
    try:
        d = json.loads(good)
        d["config_hash"] = "0" * 64
        p.write_text(json.dumps(d), encoding="utf-8")
        with pytest.raises(E10.EvalRefused, match="config hash"):
            E.read_record(rows[0], fi)
        d = json.loads(good)
        d["git"]["dirty"] = True
        p.write_text(json.dumps(d), encoding="utf-8")
        with pytest.raises(E10.EvalRefused, match="dirty"):
            E.read_record(rows[0], fi)
    finally:
        p.write_text(good, encoding="utf-8")
    assert E.read_record(rows[0], fi)["class"] == rec["class"]


def test_a_missing_record_is_reported_missing_and_a_stray_record_is_refused(tmp_path):
    res = tmp_path / "results"
    FAB.list_records(res, lists=("MS11_RB9D", "MS11_CTRL"), skip={"MS11_RB9D": 1})
    fi, _ = A7.frozen_inputs()
    by = E.read_lists(fi, names=("MS11_RB9D", "MS11_CTRL"), results_root=res)
    assert [bool(r.get("missing")) for r in by["MS11_RB9D"]] == [False, True] and len(by["MS11_CTRL"]) == 30
    rows = E.redirect_rows(RL.expand("MS11_RB9D"), res)
    FAB.write_record(rows[1]["cfg"], Path(rows[1]["out_dir"]), "RB9D_0099_stray", np.random.default_rng(0))
    with pytest.raises(E10.EvalRefused, match="not rows of the frozen lists"):
        E.read_lists(fi, names=("MS11_RB9D",), results_root=res)


@pytest.mark.slow
def test_the_s5_grid_members_the_p5_records_and_the_headline_are_found_by_name_and_classified(fab):
    res, info = fab
    fi, _ = A7.frozen_inputs()
    for T, name in (("10", FAB.S5_GRID["10"]), ("316", FAB.S5_GRID["316"])):
        r = E.classify_stored(res / f"S5/ramp/p2_linear/{name}.json", fi)
        assert r["T_ramp_s"] == pytest.approx(10.0 if T == "10" else 316.22776601683796) and r["delta0"] == 1e-6 and r["rtol"] == 1e-10
    h = E.classify_stored(res / f"S5/ramp/S5ramp/{FAB.HEADLINE}.json", fi, with_v=True)
    assert h["T_ramp_s"] == 120.0 and h["class"] == info["tables"]["headline_class"] and len(h["v"]) == 165001
    assert "J_exit_run" in h and "eta_onset" in h


@pytest.mark.slow
def test_the_map_loaders_read_the_csv_layouts_and_the_records_beside_them(fab):
    res, info = fab
    fi, _ = A7.frozen_inputs()
    cells = E.load_map_cells(res / "ms9/9e/map1_classes.csv", res / "S7/S7_map1", "map1", fi["a_ref"], fi, "D")
    assert len(cells) == info["tables"]["map1"] and cells[0]["fs"] == 1000.0 and cells[0]["W_s"] == pytest.approx(2.0) and len(cells[0]["load"]()) == 165001
    sub = E.load_map_cells(res / "ms9/9f/subgrid_classes.csv", res / "S7/S7_subgrid", "subgrid", fi["a_ref"], fi, "N")
    assert len(sub) == info["tables"]["subgrid"]
    ep = E.episode_of(cells[0], fi)
    assert ep is None or set(ep) == {"onset_s", "end_s", "f_pk_hz"}


@pytest.mark.slow
def test_the_rb9d_layout_gives_a_reported_row_beside_the_headline(fab):
    res, _ = fab
    fi, _ = A7.frozen_inputs()
    by = E.read_lists(fi, names=("MS11_RB9D",), results_root=res)
    head = E.classify_stored(res / f"S5/ramp/S5ramp/{FAB.HEADLINE}.json", fi)
    ch = EC.load_choices()
    r = E.rb9d({x["tau_ms"]: x for x in by["MS11_RB9D"]}, head, ch)
    assert r["status"] == "REPORTED" and [x["tau_ms"] for x in r["rows"]] == [8.0, 12.0]
    assert all(k in r["rows"][0] for k in E.RB9D_FIELDS) and r["headline_10ms"]["tau_ms"] == 10.0


@pytest.mark.slow
def test_run_a11_end_to_end_on_the_fabricated_tree_writes_the_table_and_marks_the_rows(fab, tmp_path, monkeypatch):
    res, _ = fab
    mod = _load_script()
    monkeypatch.setattr(P, "git_info", lambda: {"commit": "fabricated", "branch": "test", "tags": [], "dirty": False})
    out = tmp_path / "A11"
    rc = mod.main(["--results-root", str(res), "--out", str(out), "--no-hooks"])
    assert rc == 0
    rows = list(csv.DictReader((out / "a11_robustness.csv").open(encoding="utf-8")))
    assert len(rows) >= 26 + 15
    by = {(r["rb_id"], r["check_id"]): r for r in rows}
    d = by[("RB9", "d_tau_pm20")]
    assert d["pass_or_fail"] == "REPORTED" and d["label"] == "post hoc" and "tau 8 ms" in d["value"]
    assert by[("RB9", "a_dimensional_vs_nondimensional")]["pass_or_fail"] == "PASS"
    assert by[("G6", "gate")]["pass_or_fail"] == "PASS" and "G6-D1" in by[("G6", "gate")]["note"]
    assert all(r["pass_or_fail"] in E.STATUS_WORDS for r in rows)
    carried = [r for r in rows if f"{r['rb_id']}/{r['check_id']}" in HK.HOOKS]
    assert len(carried) == 26 and all("not recomputed" in r["note"] for r in carried)           # --no-hooks: carried as logged
    ev = json.loads((out / "a11_evaluators.json").read_text(encoding="utf-8"))
    assert ev["missing_records"] == {n: 0 for n in RL.ALL_LISTS}
    assert (ROOT / "results").resolve() not in out.resolve().parents


@pytest.mark.slow
def test_run_a11_with_a_missing_rb9d_record_marks_the_row_not_evaluable(tmp_path, monkeypatch):
    res = tmp_path / "results"
    FAB.build_all(res, skip={"MS11_RB9D": 1})
    mod = _load_script()
    monkeypatch.setattr(P, "git_info", lambda: {"commit": "fabricated", "branch": "test", "tags": [], "dirty": False})
    assert mod.main(["--results-root", str(res), "--out", str(tmp_path / "A11"), "--no-hooks"]) == 0
    rows = list(csv.DictReader((tmp_path / "A11/a11_robustness.csv").open(encoding="utf-8")))
    assert next(r for r in rows if r["check_id"] == "d_tau_pm20")["pass_or_fail"] == "NOT EVALUABLE"
    assert json.loads((tmp_path / "A11/a11_evaluators.json").read_text(encoding="utf-8"))["missing_records"]["MS11_RB9D"] == 1


@pytest.mark.slow
def test_the_real_context_ms9_loaders_read_the_stored_csv_layouts_and_the_ms8_parquet_gate(fab, tmp_path):
    """RealContext on fabricated CSVs in the real layout (headers copied from the stored tables) and a fabricated A7 parquet table."""
    import pandas as pd
    from test_ms11_hooks import FV, ms8_df
    res = tmp_path / "results"
    ctx = HK.RealContext(root=ROOT, results_root=res)
    hl_cols = list(csv.DictReader((fab[0] / "ms9/9d/s5_headline_classes.csv").open(encoding="utf-8")).__next__())
    runlist = list(csv.DictReader((ROOT / "configs/ms9/runlists/runlist_S16.csv").open(encoding="utf-8")))
    d = res / "ms9/9d"
    d.mkdir(parents=True)
    with (d / "s16_classes.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=hl_cols, lineterminator="\n")
        w.writeheader()
        for r in runlist:
            w.writerow({**{c: "" for c in hl_cols}, "run": r["name"], "class": "D-tr", "status": "ok"})
    with (d / "s5_headline_classes.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=hl_cols, lineterminator="\n")
        w.writeheader()
        w.writerow({**{c: "" for c in hl_cols}, "run": FAB.HEADLINE, "class": "D-tr", "path_name": "path_hypoxia", "T_ramp_s": "120.0", "mode": "D", "status": "ok"})
    s = ctx.s16()
    assert sum(r["group"] == "oat" for r in s["rows"]) == 14 and sum(r["group"] == "lhs" for r in s["rows"]) == 64 and s["nominal_class"] == "D-tr"
    (res / "ms9/9e").mkdir(parents=True)
    (res / "ms9/9f").mkdir(parents=True)
    (res / "ms9/9e/map1_classes.csv").write_text("run,i,j,class\n" + "".join(f"r{k},{k},0,D-tr\n" for k in range(900)), encoding="utf-8")
    (res / "ms9/9f/subgrid_classes.csv").write_text("run,i,j,seed,class,det,W_s,git_commit,git_dirty,agree\n"
                                                    + "".join(f"r{k},{k // 10},0,{k % 10},S+,D-tr,2.0,x,False,True\n" for k in range(2250)), encoding="utf-8")
    (res / "ms9/nc1_classes.csv").write_text("family,class,supplementary,status\nNC1,D-none,False,ok\nNC1_net,S+,False,ok\nNC1_supp,S-rel,True,ok\n", encoding="utf-8")
    assert len(ctx.map1_classes()) == 900 and len(ctx.subgrid()) == 2250 and [r["supplementary"] for r in ctx.nc1()] == [False, False, True]
    (res / "A7").mkdir()
    fi, _ = A7.frozen_inputs()
    df = ms8_df()
    df["criteria_sha256"] = fi["criteria_sha256"]
    df.to_parquet(res / "A7/a7_ramp_metrics.parquet")
    got = ctx.ms8()
    assert len(got["df"]) == len(df) and got["fv"]["criteria_sha256"] == fi["criteria_sha256"]
    ctx2 = HK.RealContext(root=ROOT, results_root=res)
    ctx2._cache.clear()
    df["criteria_sha256"] = "not the frozen file"
    df.to_parquet(res / "A7/a7_ramp_metrics.parquet")
    with pytest.raises(HK.HookError, match="different frozen file"):
        ctx2.ms8()
    # the ten MS8, MS9 and frozen-leaf hooks run through the real context on these fabricated tables (the table values are made up: only the path is tested)
    df["criteria_sha256"] = fi["criteria_sha256"]
    df.to_parquet(res / "A7/a7_ramp_metrics.parquet")
    ctx3 = HK.RealContext(root=ROOT, results_root=res)
    only = [k for k, h in HK.HOOKS.items() if h.origin in ("MS8", "MS9", "frozen criteria")]
    out = HK.run_hooks(ctx3, EC.load_choices(), only=only)
    assert len(out) == len(only) == 19 and out["RB8/m4_adaptation"]["word"] == "OPEN" and out["G6/gate"]["word"] == "PASSED WITH DEPARTURES"
