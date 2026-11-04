"""MS13 13t (DL-545 J15, DL-546; DL-554 R1, R2): the one verification command for the journal export.

  .venv/Scripts/python.exe scripts/ms13_verify_export.py [F1 F3 F5 F5c] [--dir figures/journal]

For every figure it redraws the journal figure object (reads results/ only, writes nothing) and checks it together with the exported files in --dir: the collision checker (A,
plotting/collide.py), the PDF checks (B), and the J1 to J14 tests: size and shape within the config, no text below the minimum size, fonts embedded and none Type 3, line width,
colour maps, non-colour distinction, panel letters in order, file names, every draft FAIL line of the strip present in the caption, the drawn-data digest equal to the draft's,
the draft files byte-identical to docs/ms13_figure_manifest.csv, no draft, decision-log or provenance text on the image, the supplement lists every strip row, caption sentence 1
names the main failure, text contrast, red-green pairs, the greyscale lightness report, the main PNG (600 dpi) and TIFF (600 dpi, LZW, RGB) at 6.3 x 8.0 in at most, no SVG, WMF or
EMF, and the file sizes (a PDF above 5 MB, a PNG or TIFF above 10 MB are flagged). 13t-1d (DL-571): F5c is the second journal file of the F5 build (draft panels (f) to (i); its draft files, digest and manifest rows are
those of F5); new rows: margins (at least 0.10 in of white on all four sides of the PNG, T5), label-title gap (at least 0.05 in between an x-axis label and the next panel's title, T6),
paragraphs (the seven labelled paragraphs of the journal caption, T8), caption words (no plan, milestone, table number, DL number, step ID or code name, T8), arrays (the per-array digests of the
drawn data equal the draft's; for F5 together with F5c the union of the array names equals the draft's, T1) and, when F5 and F5c are both checked, the row F5+F5c. It prints a table figure x check with PASS / FAIL (and MANUAL for the colour-vision check, which the
user does with an online simulator, R2) and exits non-zero on any FAIL (a MANUAL row never does). The collision allow-list entries that were used are printed with their reasons.
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
from mprsurge.plotting import jcaption as JCAP
from mprsurge.plotting import jchecks as JC
from mprsurge.plotting import jshort as JSH
from mprsurge.plotting import plain as PL
from mprsurge.plotting import journal as J
from mprsurge.plotting import style as S

PILOT = ("F1", "F3", "F5", "F5c")
DRAFT_ID = {"F1": "F1", "F3": "F3", "F5": "F5", "F5c": "F5"}              # the figure whose draft files, digest and manifest rows a journal file is checked against
CHECKS = ("A collisions", "B pdf", "size+shape", "text>=8pt", "fonts", "line width", "cmaps", "non-colour", "letters", "file names", "FAIL lines", "digest", "arrays", "drafts identical",
          "image text", "image IDs", "plain words", "powers of ten", "minus signs", "red titles", "supplement", "sentence 1", "paragraphs", "caption words", "full caption", "key terms", "short caption", "short limits", "definitions", "failed count", "short numbers",
          "margins", "label-title gap", "contrast", "red-green", "greyscale", "cvd", "png+tiff", "no svg/wmf/emf", "file sizes")
MAIN_FAILURES = {"F1": FG.F1_MAIN_FAILURES, "F3": FG.F3_MAIN_FAILURES, "F5": FG.F5_MAIN_FAILURES, "F5c": FG.F5C_MAIN_FAILURES}
STRIP = {"F1": FG.f1_strip_lines, "F3": FG.strip_lines, "F5": FG.f5_strip_lines, "F5c": FG.f5c_strip_lines}
MIN_MARGIN_IN, MIN_LABEL_GAP_IN = 0.10, 0.05                                # DL-571 T5, T6
CLAIM_IDS = {"F1": (FG.F1_CLAIM_LIMITS, None), "F3": (FG.F3_CLAIM_LIMITS, None), "F5": (FG.F5_CLAIM_LIMITS, FG.F5_NOT_APPLICABLE), "F5c": (FG.F5_CLAIM_LIMITS, FG.F5_NOT_APPLICABLE)}
SHORT_MAIN = {"F1": ("does not reproduce it",), "F3": ("frequency check",), "F5": ("holds for the noise-free mean field only",),
              "F5c": ("step-halving check", "do not reproduce the mean field")}               # plain words of the main failure(s) that sentence 1 of the short caption holds (DL-582 U3 a, DL-593 V6)
CHECK_TOKEN = {("RB1", "headline_10s"): "network against mean field", ("RB1", "headline_120s"): "network against mean field", ("RB1", "cells_30s"): "network against mean field",
               ("RB2", "noisy_subgrid_agreement"): "90 percent rule", ("RB6", "network_fpk_halving_dt"): "step-halving check", ("RB9", "b_spectral_vs_cycle_headline"): "frequency check"}
SHORT_CHECKS = {f: sorted(JSH.SHORT_NAMED[f]) for f in PILOT}      # DL-593 V7: only the failed checks whose result is drawn are named in a short caption
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
    cap_path, prov_path = out / f"{fid}_journal_caption_full.txt", out / f"{fid}_journal_provenance.json"           # the FULL caption (DL-582 U3 b); the short one is read below
    short_path = out / f"{fid}_journal_caption.txt"
    missing = [p for p in (pdf, png, cap_path, short_path, prov_path, sup / f"{fid}_supplement.md", sup / f"{fid}_source_data.csv", sup / f"{fid}_alt_text.txt") if not p.is_file()]
    if missing:
        return {c: ("FAIL", f"missing {missing[0].name}") for c in CHECKS}, info
    cap = cap_path.read_text(encoding="utf-8")
    short = short_path.read_text(encoding="utf-8").strip()
    prov = json.loads(prov_path.read_text(encoding="utf-8"))
    did = DRAFT_ID[fid]
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
        okz = (W <= cfg["page"]["main_width_in"] + 1e-9 and H <= cfg["page"]["main_max_height_in"] + 1e-9 and mb is not None and abs(mb[2] / 72.0 - W) < 0.02 and abs(mb[3] / 72.0 - H) < 0.02
               and (wpx, hpx) == (round(W * cfg["output"]["png_dpi"]), round(H * cfg["output"]["png_dpi"])))
        res["size+shape"] = ("PASS" if okz else "FAIL", f"{W:.3f} x {H:.3f} in (page max {cfg['page']['main_width_in']} x {cfg['page']['main_max_height_in']}); png {wpx} x {hpx} px at {cfg['output']['png_dpi']} dpi")
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
        srows = FG.strip_rows_of(fid, d)
        # 13t-1d (DL-571 T8): the journal caption holds the plain form of every strip row (JCAP.failed_line), and the supplement holds the ruled (verbatim) line
        absent = [ln for ln, r in zip(lines, srows) if JCAP.failed_line(r) not in cap or ln not in sup_text]
        res["FAIL lines"] = ("PASS" if not absent else "FAIL", f"{len(lines) - len(absent)} of {len(lines)} strip lines in the caption (plain) and the supplement (ruled)" + (f"; absent: {absent[0][:50]}" if absent else ""))
        # digest
        draft_dig = (root / "figures" / did / f"{did}_drawn_data_sha256.txt").read_text(encoding="utf-8").strip()
        mine = prov.get("journal", {}).get("drawn_data_sha256")
        recomputed = FG.drawn_data_sha256(d)
        res["digest"] = ("PASS" if mine == draft_dig == recomputed else "FAIL", f"{recomputed[:12]}... export {str(mine)[:12]} draft {draft_dig[:12]}")
        # per-array digests (DL-571 T1): the arrays this file draws, each with the digest of the draft's data; for F5 and F5c the union of both files is checked in main()
        arr_now = FG.array_digests(d)
        arr_rec = prov.get("journal", {}).get("array_digests", {})
        keys = FG.journal_keys(fid, d)
        arr_ok = bool(arr_rec) and set(arr_rec) == set(keys) and all(arr_rec[k] == arr_now[k] for k in keys)
        info["arrays"] = {k: arr_rec.get(k) for k in keys}
        info["draft_arrays"] = arr_now
        res["arrays"] = ("PASS" if arr_ok else "FAIL", f"{len(keys)} of the {len(arr_now)} arrays of the draft data, per-array digests equal" if arr_ok else "per-array digests missing or different")
        # draft files identical to the manifest
        rows = [(f, h) for (fg, f), h in manifest.items() if fg == did and f.startswith(f"figures/{did}/")]
        changed = [f for f, h in rows if not (root / f).is_file() or sha256_file(root / f) != h]
        res["drafts identical"] = ("PASS" if rows and not changed else "FAIL", f"{len(rows)} draft files, {len(changed)} differ from the manifest")
        # image text
        it = JC.image_text_violations(fig)
        res["image text"] = ("PASS" if not it else "FAIL", f"{len(it)} texts with draft, DL or provenance wording" + (f": {it[0]}" if it else ""))
        # image IDs, minus signs, red titles (DL-581 U1, U2; DL-582 U6 a)
        ids_on = JC.image_id_violations(fig)
        res["image IDs"] = ("PASS" if not ids_on else "FAIL", f"{len(ids_on)} image texts with a check, gate, rule or step ID" + (f": {ids_on[0]}" if ids_on else ""))
        pw = JC.plain_word_violations(fig)
        res["plain words"] = ("PASS" if not pw else "FAIL", f"{len(pw)} image texts with stored, headline, companion, mode D, f_pk, P-1 or path time" + (f": {pw[0]}" if pw else ""))
        en = JC.e_notation_violations(fig)
        res["powers of ten"] = ("PASS" if not en else "FAIL", f"{len(en)} image texts with 1e3, 3e3, 1e4, 3e4 or 1e5 notation" + (f": {en[0]}" if en else ""))
        hy = JC.tick_hyphens(fig)
        res["minus signs"] = ("PASS" if not hy else "FAIL", f"{len(hy)} tick labels with a hyphen-minus instead of U+2212" + (f": {hy[0]}" if hy else ""))
        reds = JC.red_titles(fig)
        tmap = JCAP.TITLE_MAP[fid]
        plain_all = [x[1] for x in tmap]
        unmapped = [s for _, s in reds if not any(p in s for p in plain_all)]
        not_in_cap = [p for p in plain_all if f"is shown in the title of" not in cap or f"as '{p}'" not in cap or p not in sup_text]
        evidence = []
        if fid == "F3":
            marks = [a for a in fig.findobj(lambda a: a.get_gid() == "frequency mark")]
            diff = [a for a in fig.findobj(lambda a: a.get_gid() == "frequency mark difference")]
            labs = " ".join(a.get_text() for a in fig.findobj(lambda a: a.get_gid() == "frequency mark label"))
            if len(marks) != 2 or len(diff) != 1 or "cycle frequency at the headline" not in labs or "spectral peak at the headline" not in labs or "differ by 4.391 Hz; allowed 0.5 Hz" not in diff[0].get_text():
                evidence.append("F3 frequency marks, labels or difference text missing")
        if fid == "F5c":
            lines = [a.get_text() for a in fig.findobj(lambda a: a.get_gid() == "step-halving line")]
            if not lines or " ".join(" ".join(lines).split()) != FG.F5CJ_B_LINE:
                evidence.append("F5c (b) step-halving line missing")
        okr = bool(reds) and not unmapped and not not_in_cap and not evidence
        res["red titles"] = ("PASS" if okr else "FAIL", f"{len(reds)} red titles, each a plain title of the map; each in the full caption ('shown in the title as') and the supplement table" if okr
                             else f"unmapped {unmapped[:1]}; not in caption or table {not_in_cap[:1]}; {evidence}")
        # supplement
        need = [f"{x['rb_id']} {x['check_id']}" for x in FG.strip_rows_of(fid, d)]
        lack = [n for n in need if n not in sup_text]
        res["supplement"] = ("PASS" if not lack else "FAIL", f"{len(need) - len(lack)} of {len(need)} strip rows in the supplement")
        # sentence 1
        first_par = cap.split("\n\n")[0]
        s1 = first_par[len(fid) + 2:].split(". ")[0] if first_par.startswith(f"{fid}. ") else ""
        miss = [m for m in MAIN_FAILURES[fid] if m not in s1]
        res["sentence 1"] = ("PASS" if not miss else "FAIL", f"main failure(s) in sentence 1: {len(MAIN_FAILURES[fid]) - len(miss)} of {len(MAIN_FAILURES[fid])}")
        # paragraphs and words (DL-571 T8)
        paras = cap.rstrip("\n").split("\n\n")
        want = ["Panels.", "Key and abbreviations.", "Classifier and spectrogram settings.", "Parameters.", "Failed checks.", "Limits."]
        starts_ok = len(paras) == 7 and first_par.startswith(f"{fid}. ") and all(paras[i + 1].startswith(w + " ") for i, w in enumerate(want))
        res["paragraphs"] = ("PASS" if starts_ok else "FAIL", f"{len(paras)} paragraphs; labels " + ", ".join(w.rstrip(".") for w in want if any(x.startswith(w + " ") for x in paras)))
        bad_words = sorted({m.group(0) for m in JCAP.FORBIDDEN.finditer(cap)})
        res["caption words"] = ("PASS" if not bad_words else "FAIL", f"{len(bad_words)} forbidden words or codes" + (f": {bad_words[:5]}" if bad_words else ""))
        # the full caption (DL-582 U3 b, e): in the supplement; every ruled claim limit (plain sentence) in it; the Key keeps only terms that the caption uses (U5)
        ids_, na_ = CLAIM_IDS[fid]
        norm = lambda s: " ".join(s.split())
        lim_missing = [i for i in ids_ if norm(PL.plain_limit_text((i,), na_)) not in norm(cap)]
        in_sup = norm(cap) in norm(sup_text)
        res["full caption"] = ("PASS" if in_sup and not lim_missing else "FAIL", f"in the supplement: {in_sup}; {len(ids_) - len(lim_missing)} of {len(ids_)} ruled claim limits in the full caption" + (f"; missing {lim_missing[:2]}" if lim_missing else ""))
        unused = JCAP.key_unused_terms(cap)
        res["key terms"] = ("PASS" if not unused else "FAIL", f"{len(unused)} Key entries whose term the caption does not use" + (f": {unused[:3]}" if unused else ""))
        # the SHORT caption (DL-582 U3 a, U5): words, order, plain words, failed checks, limits
        limit = J.caption_limit(cfg, fid)
        sbad = sorted({m.group(0) for m in JCAP.FORBIDDEN.finditer(short)} | {m.group(0) for m in JSH.ID_PATTERN.finditer(short)} | set(re.findall(r"\bstored\b", short)))
        first_sentence = short[len(fid) + 2:].split(". ")[0]
        miss_main = [m for m in SHORT_MAIN[fid] if m not in first_sentence]
        miss_chk = [CHECK_TOKEN[k] for k in SHORT_CHECKS[fid] if CHECK_TOKEN[k] not in short]
        ptr_ok = short.endswith(JSH.POINTER.format(fid=fid))
        red_ok = "red title" in short.lower()
        enot = re.findall(r"(?<![\w.+-])(?:1e3|3e3|1e4|3e4)\b", short + " " + cap)
        n_words = JSH.words(short)
        okshort = (n_words <= limit and not sbad and not miss_main and not miss_chk and ptr_ok and red_ok and not enot and short.startswith(f"{fid}. ") and "\n" not in short)
        res["short caption"] = ("PASS" if okshort else "FAIL", f"{n_words} words (limit {limit}); " + (f"forbidden {sbad[:3]}; " if sbad else "") + (f"main failure missing {miss_main}; " if miss_main else "")
                                + (f"failed checks missing {miss_chk[:3]}; " if miss_chk else "") + ("" if ptr_ok else "pointer sentence missing; ") + ("" if red_ok else "red-title sentence missing; ")
                                + (f"e-notation of N in a caption {enot[:2]}; " if enot else "") + "order, plain words and the pointer to the supplement checked")
        # short limits: the clauses of the figure (a distinctive phrase each), with numbers that are in the full caption
        lim_miss = JSH.limits_missing(fid, short)
        res["short limits"] = ("PASS" if not lim_miss else "FAIL", f"{len(JSH.SHORT_LIMIT_IDS[fid]) - len(lim_miss)} of {len(JSH.SHORT_LIMIT_IDS[fid])} limit clauses in the short caption" + (f"; missing {lim_miss}" if lim_miss else ""))
        # V5: every technical term defined where first used; V7: the count of the other failed checks equals the full caption's; V8: numbers of the short caption are in the full caption
        und = JSH.undefined_terms(short)
        res["definitions"] = ("PASS" if not und else "FAIL", f"{len(JSH.DEFS)} terms checked; first use of each term used has its plain definition next to it" + (f"; undefined: {und[:4]}" if und else ""))
        n_full = JSH.further_count(fid, cap)
        m_ = re.search(r"(\d+) further failed checks? of the project|No further failed check", short)
        n_short = (int(m_.group(1)) if m_ and m_.group(1) else 0) if m_ else None
        res["failed count"] = ("PASS" if n_short == n_full else "FAIL", f"{n_short} further failed checks in the short caption; {n_full} computed from the full caption (failed rows named in the full caption {len(JSH.failed_in_full(cap))}, named in the short {len(JSH.SHORT_NAMED[fid])})")
        nn = JSH.numbers_not_in_full(short, cap)
        res["short numbers"] = ("PASS" if not nn else "FAIL", "every number of the short caption is in the full caption" if not nn else f"numbers not in the full caption: {nn[:5]}")
        # margins and label-title gaps (DL-571 T5, T6)
        mv = JC.margin_violations(png, MIN_MARGIN_IN)
        mm = JC.margins_in(png)
        res["margins"] = ("PASS" if not mv else "FAIL", "white margins left {left:.3f} right {right:.3f} top {top:.3f} bottom {bottom:.3f} in (minimum {m} in)".format(m=MIN_MARGIN_IN, **mm))
        info["margins"] = mm
        lg = JC.label_title_gaps(fig, MIN_LABEL_GAP_IN)
        res["label-title gap"] = ("PASS" if not lg else "FAIL", f"{len(lg)} x labels closer than {MIN_LABEL_GAP_IN} in to the next panel's title" + (f": {lg[0]}" if lg else ""))
        # contrast, red-green, greyscale
        cb = JC.text_contrast(fig, cfg["colour"]["min_text_contrast"], SCHEMATIC_FACES)
        res["contrast"] = ("PASS" if not cb else "FAIL", f"{len(cb)} texts below {cfg['colour']['min_text_contrast']}:1" + (f": {cb[0]}" if cb else ""))
        rg = JC.red_green_pairs(fig, cfg["colour"]["min_lightness_difference"])
        res["red-green"] = ("PASS" if not rg else "FAIL", f"{len(rg)} red-green pairs of similar lightness" + (f": {rg[0]}" if rg else ""))
        close = JC.close_in_lightness(fig, cfg["colour"]["min_lightness_difference"])
        info["close"] = close
        res["greyscale"] = ("PASS" if not nc else "FAIL", f"{len(close)} series-colour pairs closer than L* {cfg['colour']['min_lightness_difference']} (each also differs in a non-colour attribute)")
        res["cvd"] = ("MANUAL", "user checks the final PNGs with an online simulator; UNVERIFIED (no package installed, nothing home-made; DL-554 R2)")
        # exports: the main files (PNG and TIFF at 600 dpi), the forbidden formats, the sizes
        tif = out / f"{fid}_journal.tiff"
        pdpi = cfg["output"]["png_dpi"]
        im_png = Image.open(png)
        png_dpi = tuple(round(x) for x in im_png.info.get("dpi", (0, 0)))
        if tif.is_file():
            t = JC.tiff_report(tif)
            okt = (t["mode"] == "RGB" and t["dpi"] == (cfg["output"]["tiff_dpi"],) * 2 and str(t["compression"]).lower() in ("tiff_lzw", "lzw") and t["size"] == (wpx, hpx)
                   and png_dpi == (pdpi, pdpi))
            res["png+tiff"] = ("PASS" if okt else "FAIL", f"PNG {wpx} x {hpx} px {png_dpi} dpi; TIFF {t['size'][0]} x {t['size'][1]} px, {t['mode']}, {t['dpi']} dpi, {t['compression']}")
        else:
            res["png+tiff"] = ("FAIL", "TIFF missing")
        fb = JC.forbidden_format_files(base, cfg["output"]["forbidden_formats"])
        res["no svg/wmf/emf"] = ("PASS" if not fb else "FAIL", f"{len(fb)} files with a forbidden extension" + (f": {fb[0]}" if fb else ""))
        big = []
        if pdf.stat().st_size / 1e6 > cfg["output"]["pdf_size_flag_mb"]:
            big.append(f"PDF {pdf.stat().st_size / 1e6:.1f} MB")
        for f_ in (png, tif):
            if f_.is_file() and f_.stat().st_size / 1e6 > cfg["output"]["raster_size_flag_mb"]:
                big.append(f"{f_.suffix[1:].upper()} {f_.stat().st_size / 1e6:.1f} MB")
        res["file sizes"] = ("PASS" if not big else "FAIL", f"{pdf.stat().st_size / 1024:.0f} KB PDF, {png.stat().st_size / 1024:.0f} KB PNG, {(tif.stat().st_size / 1024) if tif.is_file() else 0:.0f} KB TIFF"
                             + (f"; FLAGGED: {', '.join(big)}" if big else ""))
        info["bytes"] = {"pdf": pdf.stat().st_size, "png": png.stat().st_size, "tiff": tif.stat().st_size if tif.is_file() else None}
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
    union = None
    if "F5" in a.ids and "F5c" in a.ids:
        # DL-571 T1: the two journal builds together draw exactly the arrays of the draft F5, with equal per-array digests
        names = set(infos["F5"].get("arrays", {})) | set(infos["F5c"].get("arrays", {}))
        draft = infos["F5"].get("draft_arrays", {})
        both = {**infos["F5"].get("arrays", {}), **infos["F5c"].get("arrays", {})}
        union = names == set(draft) and all(both[k] == draft[k] for k in names)
        print(f"F5+F5c arrays: union of {len(names)} array names {'equals' if names == set(draft) else 'DIFFERS FROM'} the draft's {len(draft)}; per-array digests {'equal' if union else 'NOT all equal'}")
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
    n_fail = sum(1 for f in a.ids for c in CHECKS if table[f][c][0] == "FAIL") + (1 if union is False else 0)
    print(f"\n{n_fail} FAIL, {sum(1 for f in a.ids for c in CHECKS if table[f][c][0] == 'MANUAL')} MANUAL (no exit-code effect)")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
