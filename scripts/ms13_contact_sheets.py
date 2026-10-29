"""MS13 13n: contact sheets of the recorded figure PNGs for the reviewer (DL-493).

  .venv/Scripts/python.exe scripts/ms13_contact_sheets.py

Reads figures/<ID>/<ID>.png (never modified) and writes figures/_review/contact_sheet_1.png to _3.png (git-ignored review aids, not figure outputs). Each recorded PNG is
scaled by 0.5 (lanczos); one title per figure; four, four and three figures side by side. Nothing is drawn into a figure and no figure is rebuilt.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SHEETS = (("F1", "F2", "F3", "F4"), ("F5", "F6", "FS1", "FS2"), ("FS3", "FS4", "FS5"))
SCALE = 0.5
GAP, TITLE_H, MARGIN = 24, 56, 24


def font(size):
    import matplotlib
    return ImageFont.truetype(str(Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans.ttf"), size)


def build(root: Path):
    out = root / "figures" / "_review"
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for k, ids in enumerate(SHEETS, 1):
        ims = []
        for i in ids:
            im = Image.open(root / "figures" / i / f"{i}.png").convert("RGB")
            ims.append((i, im.resize((round(im.width * SCALE), round(im.height * SCALE)), Image.LANCZOS)))
        w = MARGIN * 2 + sum(im.width for _, im in ims) + GAP * (len(ims) - 1)
        h = MARGIN * 2 + TITLE_H + max(im.height for _, im in ims)
        sheet = Image.new("RGB", (w, h), "white")
        d = ImageDraw.Draw(sheet)
        x = MARGIN
        for i, im in ims:
            d.text((x, MARGIN), f"{i}  (draft, untagged; recorded PNG at 50 percent)", fill="black", font=font(26))
            sheet.paste(im, (x, MARGIN + TITLE_H))
            d.rectangle((x - 1, MARGIN + TITLE_H - 1, x + im.width, MARGIN + TITLE_H + im.height), outline="grey")
            x += im.width + GAP
        p = out / f"contact_sheet_{k}.png"
        sheet.save(p)
        paths.append((p, sheet.size))
    return paths


if __name__ == "__main__":
    for p, size in build(Path(__file__).resolve().parents[1]):
        print(p, size)
