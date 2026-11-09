"""MS13 13t-11 (DL-699 R5): list the text drawn on the 13 journal images that holds a claim word (smallest, largest, at most, at least, up to, N to M, all, none, only, N of M, increases, decreases, ...) or a number.
Read-only: the figure is drawn in memory from the stored results as ms13_verify_export.py does (FG.journal_figure), nothing is written except to stdout.
Usage: python scripts/ms13_list_image_claims.py [ID ...]   -> lines  figure | text"""
import re
import sys

import matplotlib.text as mtext

from mprsurge.config import repo_root
from mprsurge.plotting import figures as FG

IDS = "F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5".split()
CLAIM = re.compile(r"\b(largest|smallest|at most|at least|up to|from|all|none|every|only|\d+ of \d+|increases?|decreases?|rises?|falls?|highest|lowest|most|least|never|always|below|above|and more|range|max|min|floor|pinned|identical|same|equal|coincide|overlap)\b", re.I)
NUM = re.compile(r"\d")


def main(argv):
    ids = argv or IDS
    root = repo_root()
    for fid in ids:
        seen = set()
        with FG.journal_figure(fid, root=root) as (fig, d, cfg):
            for t in fig.findobj(mtext.Text):
                s = t.get_text().strip()
                if not s or not t.get_visible() or s in seen:
                    continue
                seen.add(s)
                if CLAIM.search(s) or (NUM.search(s) and len(s) > 12):
                    print(f"{fid} | " + s.replace("\n", " / "))


if __name__ == "__main__":
    main(sys.argv[1:])
