"""MS13 13b: refuse a build from a dirty tree (docs/ms13_conventions.md section 10; M13-14 (i)).

  .venv/Scripts/python.exe scripts/check_clean_tree.py [--root PATH]

Exit 0 if `git status --porcelain` is empty; exit 1 and print the offending lines (modified and untracked files; results/ and figures/ are
git-ignored) otherwise. Prints HEAD, branch and the tags at HEAD. Writes nothing. Called first by every figure script with --tag.
"""
import argparse
import sys

from mprsurge.plotting.figprov import dirty_lines
from mprsurge.provenance import git_info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None, help="repository to check (default: this repository)")
    a = ap.parse_args(argv)
    lines = dirty_lines(a.root)
    if a.root is None:
        g = git_info()
        print(f"HEAD {g['commit']}  branch {g['branch']}  tags at HEAD {g['tags']}")
    if lines:
        print(f"DIRTY: {len(lines)} path(s) from git status --porcelain:")
        for ln in lines:
            print("  " + ln)
        return 1
    print("clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
