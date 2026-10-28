"""MS13 13c: write the colour-difference report of the style table (report only, no pass line; docs/ms13_conventions.md section 2).

  .venv/Scripts/python.exe scripts/report_style_colours.py [--out figures/style]

Writes colour_report.csv (every pair of keys, CIE76 dE in normal vision, simulated deuteranopia, protanopia and greyscale) and colour_report.txt
(the smallest differences per family and view) into figures/style (git-ignored). Reads nothing from results/, simulates nothing, builds no figure.
"""
import argparse

from mprsurge.config import repo_root
from mprsurge.plotting import style


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(repo_root() / "figures" / "style"))
    a = ap.parse_args(argv)
    csv_path, txt_path = style.write_colour_report(a.out)
    print(txt_path.read_text(encoding="utf-8"), end="")
    print(f"written: {csv_path}\nwritten: {txt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
