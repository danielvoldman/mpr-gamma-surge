"""MS13 13t-10 (DL-690 O2): list every sentence of the journal captions with a claim of the kind largest, smallest, at most, at least, up to, N to M, all, none, every, only, N of M, increases, decreases
(reads figures/journal/<ID>/<ID>_journal_caption.txt and _caption_full.txt; prints the count and one line figure|caption|claims|sentence; writes nothing)."""
import re, glob, os, sys
ids="F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5".split()
pat=re.compile(r"\b(largest|smallest|at most|at least|up to|from [-\d.e]+ to [-\d.e]+|\d[\d.e+-]* to \d[\d.e+-]*|all|none|every|only|\d+ of \d+|increases?|decreases?|rises?|falls?|highest|lowest|most|least|never|always|both|each|no [a-z]+ )\b",re.I)
out=[]
for i in ids:
    for suf in ("_journal_caption.txt","_journal_caption_full.txt"):
        p=f"figures/journal/{i}/{i}{suf}"
        if not os.path.exists(p): continue
        t=open(p,encoding="utf-8").read()
        for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])",t):
            m=pat.findall(s)
            if m: out.append((i,suf[9:-4] or 'short',sorted(set(x if isinstance(x,str) else x[0] for x in m)),s.strip()))
print(len(out))
for o in out: print("|".join([o[0],o[1],",".join(o[2])[:60],o[3]]))
