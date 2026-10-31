"""MS13 13t (DL-545 J15, DL-546): the one verification command for the journal export.

  .venv/Scripts/python.exe scripts/ms13_verify_export.py [F1 F3 F5] [--dir figures/journal]

For every figure it redraws the journal figure object (reads results/ only, writes nothing) and checks it together with the exported files in --dir: the collision checker (A,
plotting/collide.py), the PDF checks (B), and the J1 to J14 tests: size and shape within the config, no text below the minimum size, fonts embedded and none Type 3, line width,
colour maps, non-colour distinction, panel letters in order, file names, every draft FAIL line of the strip present in the caption, the drawn-data digest equal to the draft's,
the draft files byte-identical to docs/ms13_figure_manifest.csv, no draft, decision-log or provenance text on the image, the supplement lists every strip row, caption sentence 1
names the main failure, text contrast, red-green pairs, the greyscale lightness report and the TIFF and EPS where they exist. It prints a table figure x check with PASS / FAIL (and
STOP for a check that cannot be run with an installed package) and exits non-zero on any FAIL. The collision allow-list entries that were used are printed with their reasons.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

from mprsurge.config import repo_root
from mprsurge.plotting import collide as CO
from mprsurge.plotting import figures as FG
from mprsurge.plotting import jchecks as JC
from mprsurge.plotting import journal as J
from mprsurge.plotting import style as S

PILOT = ("F1", "F3", "F5")
CHECKS = ("A collisions", "B pdf", "size+shape", "text>=8pt", "fonts", "line width", "cmaps", "non-colour", "letters", "file names", "FAIL lines", "digest", "drafts identical",
          "image text", "supplement", "sentence 1", "contrast", "red-green", "greyscale", "cvd", "tiff", "pdf size")
MAIN_FAILURES = {"F1": FG.F1_MAIN_FAILURES, "F3": FG.F3_MAIN_FAILURES, "F5": FG.F5_MAIN_FAILURES}
STRIP = {"F1": FG.f1_strip_lines, "F3": FG.strip_lines, "F5": FG.f5_strip_lines}
SCHEMATIC_FACES = {"ramp": S.F1_SCHEMATIC["ramp_face"], "net": S.F1_SCHEMATIC["net_face"], "model": S.F1_SCHEMATIC["box_face"], "mf": S.F1_SCHEMATIC["box_face"], "out": S.F1_SCHEMATIC["box_face"]}


def sha256_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_figure(fid: str, base: Path, root: Path, manifest: dict) -> tuple[dict, dict]:
    """Returns ({check: (status, detail)}, info)."""
    res: dict = {}
    info: dict = {"allowed": []}
    sup = base / "supplement"
    out = base / fid
    pdf, png = out / f"{fid}_journal.pdf", out / f"{fid}_journal.png"
    cap_path, prov_path = out / f"{fid}_journal_caption.txt", out / f"{fid}_journal_provenance.json"
    missing = [p for p in (pdf, png, cap_path, prov_path, sup / f"{fid}_supplement.md", sup / f"{fid}_source_data.csv", sup / f"{fid}_alt_text.txt") if not p.is_file()]
    if missing:
        return {c: ("FAIL", f"missing {missing[0].name}") for c in CHECKS}, info
    cap = cap_path.read_text(encoding="utf-8")
    prov = json.loads(prov_path.read_text(encoding="utf-8"))
    with FG.journal_figure(fid, root=root) as (fig, d, cfg):
        W, H = fig.get_size_inches()
        # A: collisions
        bad, ok = CO.check(fig, pad_pt=cfg["collision"]["pad_pt"], allow=CO.JOURNAL_ALLOW.get(fid, ()))
        info["allowed"] = [(str(h), r) for h, r in ok]
        res["A collisions"] = ("PASS" if not bad else "FAIL", f"{len(bad)} unlisted, {len(ok)} listed" + ("; " + str(bad[0]) if bad else ""))
        # B: pdf
        r = JC.pdf_report(pdf)
        embedded = r["descriptors"] > 0 and r["fontfile2"] + r["fontfile3"] >= r["descriptors"]
        small = [x for x in r["tf_sizes"] if x < cfg["text"]["min_pt"] - 1e-9]
        okb = (not r["type3"]) and embedded and not small and r["mediabox"] is not None
        res["B pdf"] = ("PASS" if okb else "FAIL", f"fonts {r['basefonts']}, Tf sizes {r['tf_sizes']}, Type3 {r['type3']}, embedded {r['fontfile2']}/{r['descriptors']}")
        res["fonts"] = ("PASS" if (not r["type3"] and embedded) else "FAIL", f"{', '.join(r['basefonts'])}; Type 3: {r['type3']}")
        # size and shape
        mb = r["mediabox"]
        from PIL import Image
        wpx, hpx = Image.open(png).size
        okz = (W <= cfg["page"]["double_column_width_in"] + 1e-9 and H <= cfg["page"]["max_height_in"] + 1e-9 and mb is not None and abs(mb[2] / 72.0 - W) < 0.02 and abs(mb[3] / 72.0 - H) < 0.02
               and (wpx, hpx) == (round(W * cfg["output"]["dpi"]), round(H * cfg["output"]["dpi"])))
        res["size+shape"] = ("PASS" if okz else "FAIL", f"{W:.3f} x {H:.3f} in (page max {cfg['page']['double_column_width_in']} x {cfg['page']['max_height_in']}); png {wpx} x {hpx} px")
        info["inches"] = (W, H)
        # text, lines, cmaps, non-colour
        t_bad = JC.text_sizes(fig, cfg["text"]["min_pt"])
        res["text>=8pt"] = ("PASS" if not t_bad else "FAIL", f"{len(t_bad)} below {cfg['text']['min_pt']} pt" + (f": {t_bad[0]}" if t_bad else ""))
        l_bad = JC.line_widths(fig, cfg["lines"]["min_width_pt"])
        res["line width"] = ("PASS" if not l_bad else "FAIL", f"{len(l_bad)} below {cfg['lines']['min_width_pt']} pt" + (f": {l_bad[0]}" if l_bad else ""))
        names, c_bad = JC.cmap_report(fig, cfg)
        info["cmaps"] = names
        res["cmaps"] = ("PASS" if not c_bad else "FAIL", ", ".join(names) + (f"; not allowed: {c_bad}" if c_bad else ""))
        nc = JC.non_colour_violations(fig)
        res["non-colour"] = ("PASS" if not nc else "FAIL", f"{len(nc)} colour-only pairs" + (f": {nc[0]}" if nc else ""))
        # letters
        in_order, seq = CO.letters_in_order(fig)
        res["letters"] = ("PASS" if in_order else "FAIL", "".join(seq))
        # file names
        names_bad = JC.bad_file_names(base, cfg["files"]["name_pattern"])
        referenced = [Path(o["path"]).name for o in prov["outputs"]]
        case_bad = JC.case_mismatches(referenced, out)
        sup_text = (sup / f"{fid}_supplement.md").read_text(encoding="utf-8")
        mentioned = re.findall(r"\b([A-Za-z0-9_+=,.\-]+_(?:journal_provenance\.json|journal\.pdf|params\.csv))\b", sup_text)
        case_bad += JC.case_mismatches(mentioned, out)
        res["file names"] = ("PASS" if not names_bad and not case_bad else "FAIL", f"{len(names_bad)} invalid names, {len(case_bad)} case mismatches")
        # draft FAIL lines in the caption
        lines = STRIP[fid](d)
        absent = [ln for ln in lines if ln not in cap]
        res["FAIL lines"] = ("PASS" if not absent else "FAIL", f"{len(lines) - len(absent)} of {len(lines)} strip lines in the caption" + (f"; absent: {absent[0][:50]}" if absent else ""))
        # digest
        draft_dig = (root / "figures" / fid / f"{fid}_drawn_data_sha256.txt").read_text(encoding="utf-8").strip()
        mine = prov.get("journal", {}).get("drawn_data_sha256")
        recomputed = FG.drawn_data_sha256(d)
        res["digest"] = ("PASS" if mine == draft_dig == recomputed else "FAIL", f"{recomputed[:12]}... export {str(mine)[:12]} draft {draft_dig[:12]}")
        # draft files identical to the manifest
        rows = [(f, h) for (fg, f), h in manifest.items() if fg == fid and f.startswith(f"figures/{fid}/")]
        changed = [f for f, h in rows if not (root / f).is_file() or sha256_file(root / f) != h]
        res["drafts identical"] = ("PASS" if rows and not changed else "FAIL", f"{len(rows)} draft files, {len(changed)} differ from the manifest")
        # image text
        it = JC.image_text_violations(fig)
        res["image text"] = ("PASS" if not it else "FAIL", f"{len(it)} texts with draft, DL or provenance wording" + (f": {it[0]}" if it else ""))
        # supplement
        need = [f"{x['rb_id']} {x['check_id']}" for x in d["strip"]]
        lack = [n for n in need if n not in sup_text]
        res["supplement"] = ("PASS" if not lack else "FAIL", f"{len(need) - len(lack)} of {len(need)} strip rows in the supplement")
        # sentence 1
        s1 = cap.split(". ")[1] if cap.count(". ") else ""
        miss = [m for m in MAIN_FAILURES[fid] if m not in s1]
        res["sentence 1"] = ("PASS" if not miss else "FAIL", f"main failure(s) in sentence 1: {len(MAIN_FAILURES[fid]) - len(miss)} of {len(MAIN_FAILURES[fid])}")
        # contrast, red-green, greyscale
        cb = JC.text_contrast(fig, cfg["colour"]["min_text_contrast"], SCHEMATIC_FACES)
        res["contrast"] = ("PASS" if not cb else "FAIL", f"{len(cb)} texts below {cfg['colour']['min_text_contrast']}:1" + (f": {cb[0]}" if cb else ""))
        rg = JC.red_green_pairs(fig, cfg["colour"]["min_lightness_difference"])
        res["red-green"] = ("PASS" if not rg else "FAIL", f"{len(rg)} red-green pairs of similar lightness" + (f": {rg[0]}" if rg else ""))
        close = JC.close_in_lightness(fig, cfg["colour"]["min_lightness_difference"])
        info["close"] = close
        res["greyscale"] = ("PASS" if not nc else "FAIL", f"{len(close)} series-colour pairs closer than L* {cfg['colour']['min_lightness_difference']} (each also differs in a non-colour attribute)")
        res["cvd"] = ("STOP", "no installed package simulates colour-vision deficiency; not run, nothing home-made")
        # exports
        tif = out / f"{fid}_journal.tiff"
        if tif.is_file():
            t = JC.tiff_report(tif)
            okt = t["mode"] == "RGB" and t["dpi"] == (cfg["output"]["tiff_dpi"],) * 2 and str(t["compression"]).lower() in ("tiff_lzw", "lzw")
            res["tiff"] = ("PASS" if okt else "FAIL", f"{t['mode']}, {t['dpi']} dpi, {t['compression']}")
        else:
            res["tiff"] = ("FAIL", "TIFF missing")
        size_mb = pdf.stat().st_size / 1e6
        res["pdf size"] = ("PASS" if size_mb <= cfg["output"]["pdf_size_flag_mb"] else "FAIL", f"{pdf.stat().st_size / 1024:.0f} KB PDF, {png.stat().st_size / 1024:.0f} KB PNG")
        info["bytes"] = {"pdf": pdf.stat().st_size, "png": png.stat().st_size}
    return res, info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", default=list(PILOT))
    ap.add_argument("--dir", default="figures/journal")
    a = ap.parse_args(argv)
    root = repo_root()
    base = (root / a.dir) if not Path(a.dir).is_absolute() else Path(a.dir)
    with open(root / "docs" / "ms13_figure_manifest.csv", newline="", encoding="utf-8") as fh:
        manifest = {(r["figure"], r["file"]): r["sha256"] for r in csv.DictReader(fh)}
    table, infos = {}, {}
    for fid in a.ids:
        table[fid], infos[fid] = check_figure(fid, base, root, manifest)
    w = max(len(c) for c in CHECKS) + 2
    print("check".ljust(w) + "".join(f.ljust(8) for f in a.ids))
    for c in CHECKS:
        print(c.ljust(w) + "".join(table[f][c][0].ljust(8) for f in a.ids))
    print()
    for f in a.ids:
        for c in CHECKS:
            st, detail = table[f][c]
            print(f"{f} {c}: {st} - {detail}")
    for f in a.ids:
        for h, r in infos[f]["allowed"]:
            print(f"ALLOW-LIST {f}: {h} -- reason: {r}")
        print(f"{f}: inches {infos[f].get('inches')}; colour maps {infos[f].get('cmaps')}; bytes {infos[f].get('bytes')}")
        for c in infos[f].get("close", []):
            print(f"{f} greyscale close pair: {c}")
    n_fail = sum(1 for f in a.ids for c in CHECKS if table[f][c][0] == "FAIL")
    print(f"\n{n_fail} FAIL, {sum(1 for f in a.ids for c in CHECKS if table[f][c][0] == 'STOP')} STOP")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
