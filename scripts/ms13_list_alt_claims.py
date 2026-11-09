"""MS13 13t-11 (DL-699 P2): list the claims of the ALT TEXTS of the 13 journal figures (read-only; writes nothing unless --md is given).

For every alt-text sentence (figures/journal/supplement/<ID>_alt_text.txt): the numbers, and the claim words (largest, smallest, at most, at least, up to, N to M, all, none, only, N of M, increases, decreases, ...).
A number is 'shared' when the same figure's short or full caption (figures/journal/<ID>/<ID>_journal_caption*.txt) contains the same token (the caption numbers are audited by the N2 audit, the O2 audit and the independent
comparison); it is 'alt only' otherwise and must be read against the stored data by hand. Output: one line  figure | kind | token(s) | sentence.   Usage: python scripts/ms13_list_alt_claims.py [--md out.md]"""
import re, sys, os, glob
IDS = "F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5".split()
NUM = re.compile(r"(?<![\w.])[-−+]?\d[\d,]*\.?\d*(?:e[-+]?\d+)?(?![\w])")
CLAIM = re.compile(r"\b(largest|smallest|at most|at least|up to|from [-−\d.e]+ to [-−\d.e]+|all|none|every|only|\d+ of \d+|increases?|decreases?|rises?|rising|falls?|falling|grows?|highest|lowest|most|least|never|always|both|each|between|below|above|no [a-z]+|negative|positive|equal|same|identical|symmetric|monotone|nearly|about)\b", re.I)


def caption_tokens(i):
    t = ""
    for p in glob.glob(f"figures/journal/{i}/{i}_journal_caption*.txt"):
        t += open(p, encoding="utf-8").read() + "\n"
    return set(NUM.findall(t)), t


def rows():
    out = []
    for i in IDS:
        alt = open(f"figures/journal/supplement/{i}_alt_text.txt", encoding="utf-8").read()
        cap_nums, _ = caption_tokens(i)
        for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])|\n+", alt):
            s = s.strip()
            if not s:
                continue
            nums = NUM.findall(s)
            cl = sorted({m if isinstance(m, str) else m[0] for m in CLAIM.findall(s)} - {"about", "between", "same", "equal", "both", "each", "no"})
            shared = [x for x in nums if x in cap_nums]
            only = [x for x in nums if x not in cap_nums]
            out.append((i, nums, shared, only, cl, s))
    return out


def main():
    r = rows()
    lines = []
    for i, nums, shared, only, cl, s in r:
        if nums or cl:
            lines.append(f"{i} | nums {len(nums)} (shared {len(shared)}, alt-only {','.join(only) or '-'}) | claim words {','.join(cl) or '-'} | {s}")
    print(len(lines), "sentences with a number or a claim word;", sum(len(x[1]) for x in r), "number tokens;", sum(len(x[3]) for x in r), "alt-only tokens")
    for ln in lines:
        print(ln)
    if "--md" in sys.argv:
        open(sys.argv[sys.argv.index("--md") + 1], "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
