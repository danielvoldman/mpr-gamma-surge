"""MS13 13t-1c (DL-563 S14): a side-by-side sheet of the final F1, F3, F5 and F5c journal PNGs (13t-1d, DL-571 T1: F5c is the second file of the F5 build).

  .venv/Scripts/python.exe scripts/ms13_pilot_sheet.py        # reads figures/journal/F1,F3,F5,F5c/<ID>_journal.png; writes figures/journal/_review/pilot_sheet.png (git-ignored)

The PNGs are 6.3 in wide, at most 8.0 in high, at 600 dpi; the sheet shows each at its final size at 200 dpi, side by side with a gap of 0.2 in, so that all four can be looked at together.
It reads only the exported PNG files and writes nothing else.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
IDS = ("F1", "F2", "F3", "F5", "F5c", "F6", "FS1")        # 13t-2 (DL-616): all six; 13t-4 (DL-637): FS1 too
SHEET_DPI = 200
GAP_IN = 0.2


def main() -> int:
    ims = []
    for fid in IDS:
        p = ROOT / "figures" / "journal" / fid / f"{fid}_journal.png"
        if not p.is_file():
            print(f"missing {p}")
            return 1
        im = Image.open(p).convert("RGB")
        dpi = im.info.get("dpi", (600, 600))[0] or 600
        k = SHEET_DPI / float(dpi)
        ims.append(im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS))
    gap = round(GAP_IN * SHEET_DPI)
    top = 36
    w = sum(i.width for i in ims) + gap * (len(ims) + 1)
    h = max(i.height for i in ims) + top + gap
    sheet = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(sheet)
    x = gap
    for fid, im in zip(IDS, ims):
        sheet.paste(im, (x, top))
        draw.rectangle([x - 1, top - 1, x + im.width, top + im.height], outline=(190, 190, 190))
        draw.text((x, 10), f"{fid} journal PNG, final size {im.width / SHEET_DPI:.1f} x {im.height / SHEET_DPI:.1f} in, shown at {SHEET_DPI} dpi", fill=(60, 60, 60))
        x += im.width + gap
    out = ROOT / "figures" / "journal" / "_review"
    out.mkdir(parents=True, exist_ok=True)
    sheet.save(out / "pilot_sheet.png", dpi=(SHEET_DPI, SHEET_DPI))
    print(f"wrote {out / 'pilot_sheet.png'} ({w} x {h} px)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
