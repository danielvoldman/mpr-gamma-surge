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
from mprsurge.plotting import jf26 as JF26
from mprsurge.plotting import jf4 as JF4
from mprsurge.plotting import jchecks as JC
from mprsurge.plotting import jshort as JSH
from mprsurge.plotting import plain as PL
from mprsurge.plotting import journal as J
from mprsurge.plotting import style as S

PILOT = ("F1", "F2", "F3", "F4a", "F4b", "F5", "F5c", "F6")            # 13t-1: F1, F3, F5, F5c; 13t-2 (DL-616): F2 and F6
FS_SINGLE = ("FS2", "FS3", "FS4")                                       # 13t-6 (DL-651 H1, H2): stand-alone supplement files with ONE caption (<ID>_journal_caption.txt); FS3 to FS5 are added when they are done
FS_FIGS = ("FS1",) + FS_SINGLE                                          # 13t-4 (DL-636 E5, DL-637): the supplementary figures that are exported (FS2 and FS3 are added when they are done)
ALL_FIGS = PILOT + FS_FIGS
DRAFT_ID = {"F1": "F1", "F2": "F2", "F3": "F3", "F5": "F5", "F5c": "F5", "F4a": "F4", "F4b": "F4", "F6": "F6", "FS1": "FS1", "FS2": "FS2", "FS3": "FS3", "FS4": "FS4"}              # the figure whose draft files, digest and manifest rows a journal file is checked against
CHECKS = ("A collisions", "B pdf", "size+shape", "text>=8pt", "fonts", "line width", "cmaps", "non-colour", "letters", "file names", "FAIL lines", "digest", "arrays", "drafts identical",
          "image text", "image IDs", "plain words", "powers of ten", "minus signs", "sentence case", "red titles", "caption codes", "supplement", "sentence 1", "paragraphs", "caption words", "full caption", "key terms", "short caption", "short limits", "definitions", "failed count", "short numbers", "short parameters", "supplement FAILs", "superscripts",
          "margins", "label-title gap", "contrast", "red-green", "greyscale", "cvd", "png+tiff", "no svg/wmf/emf", "file sizes")
MAIN_FAILURES = {"F1": FG.F1_MAIN_FAILURES, "F2": ("lies close to the mean-field branch",),      # 13t-4 (DL-636 E1): the journal sentence 1 of F2 follows the data; the draft constant FG.F2_MAIN_FAILURES is unchanged
                  "F3": FG.F3_MAIN_FAILURES, "F5": FG.F5_MAIN_FAILURES, "F5c": FG.F5C_MAIN_FAILURES, "F4a": JF4.MAIN_FAILURES["F4a"], "F4b": JF4.MAIN_FAILURES["F4b"], "F6": FG.F6_MAIN_FAILURES, "FS1": ("passes only on our own reading", "was not run"), "FS2": ("does not reproduce the published Hopf point", "a failed check"), "FS3": ("noise check failed", "a failed check"), "FS4": ("numerical checks of the main example", "failed in two places")}
STRIP = {"F1": FG.f1_strip_lines, "F2": FG.strip_lines, "F3": FG.strip_lines, "F5": FG.f5_strip_lines, "F5c": FG.f5c_strip_lines, "F4a": lambda d: JF4.strip_lines_of("F4a", d), "F4b": lambda d: JF4.strip_lines_of("F4b", d), "F6": FG.f6_strip_lines, "FS1": lambda d: [], "FS2": lambda d: [], "FS3": FG.fs3_strip_lines, "FS4": FG.fs4_strip_lines}
MIN_MARGIN_IN, MIN_LABEL_GAP_IN = 0.10, 0.05                                # DL-571 T5, T6
CLAIM_IDS = {"F1": (FG.F1_CLAIM_LIMITS, None), "F2": (FG.F2_CLAIM_LIMITS, None), "F3": (FG.F3_CLAIM_LIMITS, None), "F5": (FG.F5_CLAIM_LIMITS, FG.F5_NOT_APPLICABLE), "F5c": (FG.F5_CLAIM_LIMITS, FG.F5_NOT_APPLICABLE), "F4a": (JF4.F4A_LIMITS, None), "F4b": (JF4.F4B_LIMITS, None),
             "F6": (FG.F6_CLAIM_LIMITS, FG.F6_NOT_APPLICABLE), "FS1": (FG.FS1_CLAIM_LIMITS, None), "FS2": (FG.FS2_CLAIM_LIMITS, None), "FS3": (FG.FS3_CLAIM_LIMITS, None), "FS4": (FG.FS4_CLAIM_LIMITS, None)}
NA_TEXT = {"F6": PL.NOT_APPLICABLE_PLAIN_F6}                          # the plain reason of a not-applicable limit, where it is not the F5 one (DL-616)
SHORT_MAIN = {"F1": ("does not reproduce it",), "F2": ("lies close to the mean-field branch",), "F6": ("negative-control check failed",), "FS1": ("passes only on our own reading", "was not run"), "F3": ("frequency check",), "F5": ("holds for the noise-free mean field only",),
              "F5c": ("step-halving check", "do not reproduce the mean field"),
              "F4a": ("does not follow the entry-exit prediction", "the two numerical solvers differ"), "F4b": ("noise-robustness checks failed",)}               # plain words of the main failure(s) that sentence 1 of the short caption holds (DL-582 U3 a, DL-593 V6)
CHECK_TOKEN = {("RB1", "headline_10s"): "network against mean field", ("RB1", "headline_120s"): "network against mean field", ("RB1", "cells_30s"): "network against mean field",
               ("RB2", "noisy_subgrid_agreement"): "90 percent rule", ("RB6", "network_fpk_halving_dt"): "step-halving check", ("RB9", "b_spectral_vs_cycle_headline"): "frequency check",
               ("G7", "gate"): "negative-control check", ("RB1", "overall"): "network against mean field",
               ("RB3", "a_inrange_runs"): "within one step of the prediction", ("RB3", "b_classifier_onset"): "classifier-onset reading", ("RB6", "solver_onset_headline"): "two numerical solvers differ",
               ("RB2", "headline_class_kept_1.0_sigma"): "in 7 of 10 noisy seeds"}
REASON_OTHER = "other (not a stored coincidence, a ruled size or a reference line)"
STRICT_ALLOW = ("F2", "F4a", "F4b", "F6", "FS1", "FS2", "FS3", "FS4", "FS5")


def reason_class(reason: str) -> str:
    """DL-628 C7: the class of an allow-list reason: a value on a reference line, ruled mark sizes (with stored positions), stored coincident positions, else other (a STOP for F2, F6 and the FS figures)."""
    r = reason.lower()
    if "reference line" in r or "stored value on the line" in r:
        return "value on a reference line"
    if "ruled mark" in r:
        return "stored coincident positions and ruled mark sizes"
    if "stored" in r or "recorded" in r:
        return "stored coincident positions"
    return REASON_OTHER


SHORT_CHECKS = {f: sorted(JSH.SHORT_NAMED[f]) for f in ALL_FIGS}      # DL-593 V7: only the failed checks whose result is drawn are named in a short caption
SCHEMATIC_FACES = {"ramp": S.F1_SCHEMATIC["ramp_face"], "net": S.F1_SCHEMATIC["net_face"], "model": S.F1_SCHEMATIC["box_face"], "mf": S.F1_SCHEMATIC["box_face"], "out": S.F1_SCHEMATIC["box_face"]}


def sha256_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _strip_rows(fid, d):
    """13t-7 (DL-663): FS2 has no stored status row and its drawn data have no 'strip' entry."""
    return [] if (fid in FS_SINGLE and "strip" not in d) else FG.strip_rows_of(fid, d)


def check_figure(fid: str, base: Path, root: Path, manifest: dict) -> tuple[dict, dict]:
    """Returns ({check: (status, detail)}, info)."""
    res: dict = {}
    info: dict = {"allowed": []}
    sup = base / "supplement"
    out = base / fid
    pdf, png = out / f"{fid}_journal.pdf", out / f"{fid}_journal.png"
    single = fid in FS_SINGLE
    cap_path, prov_path = out / (f"{fid}_journal_caption.txt" if single else f"{fid}_journal_caption_full.txt"), out / f"{fid}_journal_provenance.json"           # the FULL caption (DL-582 U3 b); the short one is read below
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
        classes: dict = {}
        for _, r_ in ok:
            classes[reason_class(r_)] = classes.get(reason_class(r_), 0) + 1
        info["allowed_classes"] = classes
        legib = classes.get(REASON_OTHER, 0) if fid in STRICT_ALLOW else 0               # DL-628 C7: an entry of F2, F6 or an FS figure whose reason is not a stored coincidence, a ruled size or a reference line is a STOP
        res["A collisions"] = ("PASS" if not bad and not legib else "FAIL", f"{len(bad)} unlisted, {len(ok)} listed ({', '.join(f'{k} {v}' for k, v in sorted(classes.items()))})" + ("; " + str(bad[0]) if bad else "")
                               + (f"; {legib} listed hits whose reason is not a stored coincidence, a ruled size or a reference line" if legib else ""))
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
        hmax = J.height_limit(cfg, fid)                                                       # 13t-4 (DL-636 E5): the per-figure height limit of the FS profile, else the main page maximum
        okz = (W <= J.width_limit(cfg, fid) + 1e-9 and H <= hmax + 1e-9 and mb is not None and abs(mb[2] / 72.0 - W) < 0.02 and abs(mb[3] / 72.0 - H) < 0.02
               and (wpx, hpx) == (round(W * cfg["output"]["png_dpi"]), round(H * cfg["output"]["png_dpi"])))
        res["size+shape"] = ("PASS" if okz else "FAIL", f"{W:.3f} x {H:.3f} in (limit {J.width_limit(cfg, fid)} x {hmax}); png {wpx} x {hpx} px at {cfg['output']['png_dpi']} dpi")
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
        srows = _strip_rows(fid, d)
        # 13t-1d (DL-571 T8): the journal caption holds the plain form of every strip row (JCAP.failed_line), and the supplement holds the ruled (verbatim) line
        plain_line = (lambda r: JCAP.uncode(JCAP.failed_line(r), fid)) if fid in JCAP.UNCODE_FIGS else JCAP.failed_line          # 13t-8b (K4): the FS2 and FS3 captions hold the plain wording of the check names
        absent = [ln for ln, r in zip(lines, srows) if plain_line(r) not in cap or ln not in sup_text]
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
        lc = J.lowercase_starts(fig)
        res["sentence case"] = ("PASS" if not lc else "FAIL", f"{len(lc)} image labels start with a lower-case word that is not an exception (DL-628 C9)" + (f": {lc[0]!r}" if lc else ""))
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
            if len(marks) != 2 or len(diff) != 1 or "cycle frequency, main example" not in labs.lower() or "spectral peak, main example" not in labs.lower() or "differ by 4.391 hz; allowed 0.5 hz" not in diff[0].get_text().lower():
                evidence.append("F3 frequency marks, labels or difference text missing")
        if fid == "F5c":
            lines = [a.get_text() for a in fig.findobj(lambda a: a.get_gid() == "step-halving line")]
            if not lines or " ".join(" ".join(lines).split()).lower() != FG.F5CJ_B_LINE.lower():
                evidence.append("F5c (b) step-halving line missing")
        if fid == "F2":
            notes_ = [a.get_text() for a in fig.findobj(lambda a: a.get_gid() == "panel note")]
            if len(reds) != 1 or not reds[0][1].startswith("(c)"):
                evidence.append("F2 must have exactly one red title, on (c)")
            if not any(" ".join(n_.split()).lower() == FG.F2J_NOTE_C.replace(chr(10), " ").lower() for n_ in notes_):
                evidence.append("F2 (c) note missing")
            if "have no red title" not in short or "have no red title" not in cap or JF26.F2_RED_NOTE not in short or JF26.F2_RED_NOTE not in cap:
                evidence.append("F2 caption lacks the red-title note or the sentence that (a) and (b) have no red title")
        if fid == "F6":
            mk = [a for a in fig.findobj(lambda a: a.get_gid() == "class mark network run")]
            nt = [a.get_text() for a in fig.findobj(lambda a: a.get_gid() == "panel note")]
            if len(mk) != 1 or "S+" not in nt:
                evidence.append("F6 (c) network-run mark or its S+ note missing")
        no_red = fid in FS_FIGS and not tmap and not reds                                       # 13t-4: FS1 has no failed row and so no red title (a red title would be a fault here)
        okr = (bool(reds) or no_red) and not unmapped and not not_in_cap and not evidence
        res["red titles"] = ("PASS" if okr else "FAIL", ("no red title (no failed row concerns this figure)" if no_red else f"{len(reds)} red titles, each a plain title of the map; each in the full caption ('shown in the title as') and the supplement table") if okr
                             else f"unmapped {unmapped[:1]}; not in caption or table {not_in_cap[:1]}; {evidence}")
        # 13t-8b (DL-668 K4, DL-671 L1): codes of checks, gates and rules: a FAIL in every SHORT caption and in the FS2 and FS3 captions; the FULL captions are reported as information only
        scope_text = cap if fid in FS_SINGLE else short
        code_fail = JSH.code_hits(scope_text)
        info["full_codes"] = [] if fid in FS_SINGLE else JSH.code_hits(cap)
        res["caption codes"] = ("PASS" if not code_fail else "FAIL", (f"{'the caption' if fid in FS_SINGLE else 'the short caption'} holds no check, gate or rule code; the full caption holds {len(info['full_codes'])} (information only)" if not code_fail
                                                                       else f"codes in {'the caption' if fid in FS_SINGLE else 'the short caption'}: {code_fail[:6]}"))
        # supplement
        need = [f"{x['rb_id']} {x['check_id']}" for x in _strip_rows(fid, d)]
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
        lim_text = (lambda i: JCAP.uncode(PL.plain_limit_text((i,), na_, NA_TEXT.get(fid)), fid)) if fid in JCAP.UNCODE_FIGS else (lambda i: PL.plain_limit_text((i,), na_, NA_TEXT.get(fid)))       # 13t-8b (K4): FS2 and FS3 hold the plain wording of the codes
        lim_missing = [i for i in ids_ if norm(JCAP.plain_n(lim_text(i))) not in norm(cap)]
        in_sup = norm(cap) in norm(sup_text)
        res["full caption"] = ("PASS" if in_sup and not lim_missing else "FAIL", f"in the supplement: {in_sup}; {len(ids_) - len(lim_missing)} of {len(ids_)} ruled claim limits in the full caption" + (f"; missing {lim_missing[:2]}" if lim_missing else ""))
        unused = JCAP.key_unused_terms(cap)
        res["key terms"] = ("PASS" if not unused else "FAIL", f"{len(unused)} Key entries whose term the caption does not use" + (f": {unused[:3]}" if unused else ""))
        # the SHORT caption (DL-582 U3 a, U5): words, order, plain words, failed checks, limits
        if single:
            na = ("PASS", "one caption only (DL-651 H2): the short-caption check does not apply")
            for k_ in ("short caption", "short limits", "failed count", "short numbers", "short parameters"):
                res[k_] = na
            und = JSH.undefined_terms(cap)
            res["definitions"] = ("PASS" if not und else "FAIL", f"{len(JSH.DEFS)} terms checked in the one caption; first use of each term used has its plain definition next to it" + (f"; undefined: {und[:4]}" if und else ""))
            res["caption words"] = ("PASS" if not bad_words else "FAIL", f"{len(bad_words)} forbidden words or codes; {len(cap.split())} words (no limit, DL-651 H2)" + (f": {bad_words[:5]}" if bad_words else ""))
        if not single:
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
            m_ = re.search(r"(\d+) further failed checks? of the project|No other failed check is about this figure", short)          # DL-604 W4(e): the F3 wording
            n_short = (int(m_.group(1)) if m_ and m_.group(1) else 0) if m_ else None
            res["failed count"] = ("PASS" if n_short == n_full else "FAIL", f"{n_short} further failed checks in the short caption; {n_full} computed from the full caption (failed rows named in the full caption {len(JSH.failed_in_full(cap))}, named in the short {len(JSH.SHORT_NAMED[fid])})")
            nn = JSH.numbers_not_in_full(short, cap)
            res["short numbers"] = ("PASS" if not nn else "FAIL", "every number of the short caption is in the full caption" if not nn else f"numbers not in the full caption: {nn[:5]}")
            # DL-603 W2: the one 'Parameters:' sentence takes its numbers from the Parameters and settings paragraphs of the full caption; F3 says that no classifier or spectrogram is used
            pm = JSH.parameters_numbers_missing(short, cap)
            f3_ok = fid != "F3" or ("no classifier" in JSH.parameters_sentence(short) and "is used" in JSH.parameters_sentence(short))
            res["short parameters"] = ("PASS" if not pm and f3_ok else "FAIL", "every number of the short Parameters sentence is in the Parameters or settings paragraph of the full caption" if not pm and f3_ok
                                       else f"numbers not in the full caption's Parameters or settings paragraphs: {pm[:5]}" + ("" if f3_ok else "; F3 must say that no classifier or spectrogram is used"))
        # DL-604 W4(e): the F3 short caption points to the supplement for the project's other failed checks, so the F3 supplement must hold every FAIL row of the stored A11 table
        with open(root / "results" / "A11" / "a11_robustness.csv", newline="", encoding="utf-8") as fh_:
            a11_rows = list(csv.DictReader(fh_))
        n_fail_rows = sum(1 for r_ in a11_rows if r_.get("pass_or_fail") == "FAIL")
        fm = JC.fail_rows_missing(sup_text, a11_rows) if fid in ("F3", "F2", "F6") else []
        res["supplement FAILs"] = ("PASS" if not fm else "FAIL", (f"all {n_fail_rows} FAIL rows of the stored A11 table are in the supplement" if fid in ("F3", "F2", "F6") else "not required for this figure (only the F3, F2 and F6 short captions refer to the list)") if not fm else f"missing FAIL rows {fm[:4]}")
        # DL-604 W3: no superscript glyph and no mathtext superscript on the image
        sp = JC.superscript_violations(fig)
        res["superscripts"] = ("PASS" if not sp else "FAIL", f"{len(sp)} image texts with a Unicode superscript or a mathtext superscript" + (f": {sp[0]}" if sp else ""))
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
    ap.add_argument("ids", nargs="*", default=list(ALL_FIGS))
    ap.add_argument("--dir", default="figures/journal")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")                      # symbols such as Delta in the details (13t-4)
    root = repo_root()
    base = (root / a.dir) if not Path(a.dir).is_absolute() else Path(a.dir)
    with open(root / "docs" / "ms13_figure_manifest.csv", newline="", encoding="utf-8") as fh:
        manifest = {(r["figure"], r["file"]): r["sha256"] for r in csv.DictReader(fh)}
    table, infos = {}, {}
    for fid in a.ids:
        table[fid], infos[fid] = check_figure(fid, base, root, manifest)
    union = None
    for first, second in (("F5", "F5c"), ("F4a", "F4b")):                   # 13t-8b: F4a and F4b are the two journal files of the draft F4 (DL-667 K2)
        if first in a.ids and second in a.ids:
            # DL-571 T1: the two journal builds together draw exactly the arrays of the draft figure, with equal per-array digests
            names = set(infos[first].get("arrays", {})) | set(infos[second].get("arrays", {}))
            draft = infos[first].get("draft_arrays", {})
            both = {**infos[first].get("arrays", {}), **infos[second].get("arrays", {})}
            ok_u = names == set(draft) and all(both[k] == draft[k] for k in names)
            union = ok_u if union is None else (union and ok_u)
            print(f"{first}+{second} arrays: union of {len(names)} array names {'equals' if names == set(draft) else 'DIFFERS FROM'} the draft's {len(draft)}; per-array digests {'equal' if ok_u else 'NOT all equal'}")
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
        print(f"INFO {f} full-caption codes (L1: information only): {infos[f].get('full_codes')}")
    for f in a.ids:
        print(f"ALLOW-LIST {f} by reason class: {infos[f].get('allowed_classes')}")
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
