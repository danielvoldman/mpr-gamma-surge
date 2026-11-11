"""MS15a step 21 (F1): compare the user's `git ls-remote --heads --tags origin` output, saved word for word in
docs/ms15a_push_record.md, with the local repository. Reads the record and local git objects only: no network
command, no write, no tag or ref change. The record is the user's output, not a check made by Claude Code.

Rules (DL-747 F1): master equals T; every pushed tag has a remote tag-object id equal to `git rev-parse <tag>` locally
(annotated tags) and a peeled value equal to the local peeled commit; the lightweight tag replication-pass has no
peeled line and equals the local object; the fig-<ID>-v1 tags are absent from the remote; the remote holds exactly
master and the 18 named tags. Exit 0 only if every row is equal.

Usage: .venv\\Scripts\\python.exe scripts\\ms15a_check_push_record.py [--record docs/ms15a_push_record.md]
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = "33b7575721184b90571c2bbaffc4a9a0b1607a77"
IDS = ["F1", "F2", "F3", "F4a", "F4b", "F5", "F5c", "F6", "FS1", "FS2", "FS3", "FS4", "FS5"]
V2 = [f"fig-{i}-v2" for i in IDS]
OLD = ["criteria-frozen", "env-v1", "tolerances-frozen"]
LIGHT = ["replication-pass"]
PUSHED = V2 + ["release-v1.0"] + OLD + LIGHT      # the 18 names of the user's push command
LINE = re.compile(r"^([0-9a-f]{40})\s+(refs/\S+)$")


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout.strip()


def parse(record):
    refs = {}
    text = Path(record).read_text(encoding="utf-8")
    for ln in text.splitlines():
        m = LINE.match(ln.rstrip())
        if m:
            refs[m.group(2)] = m.group(1)
    return refs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", default=str(ROOT / "docs/ms15a_push_record.md"))
    a = ap.parse_args()
    refs = parse(a.record)
    rows = []

    def row(name, what, remote, local):
        rows.append((name, what, remote or "-", local or "-", "YES" if remote and remote == local else "NO"))

    row("master", "branch = T", refs.get("refs/heads/master"), T)
    for t in PUSHED:
        annotated = t not in LIGHT
        rc, obj = git("rev-parse", "--verify", "-q", f"refs/tags/{t}")
        rc2, typ = git("cat-file", "-t", f"refs/tags/{t}")
        rc3, peeled = git("rev-parse", f"refs/tags/{t}^{{commit}}")
        if annotated:
            row(t, "tag object (annotated)" if typ == "tag" else f"tag object (local type {typ}: NOT annotated)",
                refs.get(f"refs/tags/{t}"), obj)
            want = T if (t in V2 or t == "release-v1.0") else peeled
            row(t, "peeled commit" + (" = T" if want == T else " = local peeled"), refs.get(f"refs/tags/{t}^{{}}"), want)
        else:
            row(t, "lightweight: object" + ("" if typ == "commit" else f" (local type {typ})"),
                refs.get(f"refs/tags/{t}"), obj)
            if f"refs/tags/{t}^{{}}" in refs:
                rows.append((t, "no peeled line expected", refs[f"refs/tags/{t}^{{}}"], "-", "NO"))
    # v1 fig tags must be absent from the remote; nothing else may be there
    v1 = [r for r in refs if re.match(r"refs/tags/fig-.*-v1(\^\{\})?$", r)]
    rows.append(("fig-<ID>-v1 (13 local tags)", "absent from the remote", ",".join(v1) or "absent", "absent",
                 "YES" if not v1 else "NO"))
    expect = {"refs/heads/master"}
    for t in PUSHED:
        expect.add(f"refs/tags/{t}")
        if t not in LIGHT:
            expect.add(f"refs/tags/{t}^{{}}")
    extra = sorted(set(refs) - expect)
    missing = sorted(expect - set(refs))
    rows.append(("remote ref set", "exactly master + 18 tags (+ peeled lines)",
                 f"{len(refs)} lines; extra={extra}; missing={missing}", f"{len(expect)} lines expected",
                 "YES" if not extra and not missing else "NO"))
    print("name | what | remote | local | equal")
    for r in rows:
        print(" | ".join(str(r[i]) for i in range(5)))
    n_ok = sum(1 for r in rows if r[4] == "YES")
    n_all = len(rows)
    annotated_new = [t for t in PUSHED if t not in LIGHT]
    print(f"\nrows equal: {n_ok} of {n_all}")
    print(f"annotated tags compared by object id and by peeled value: {len(annotated_new)} "
          f"({len(V2) + 1} new + {len(OLD)} older); lightweight: {len(LIGHT)}")
    rc, n = git("rev-list", "--count", "origin/master..master")
    print(f"local master ahead of origin/master by {n} commit(s) (origin/master is the local remote-tracking ref set by the user's push; no fetch)")
    return 0 if n_ok == n_all else 1


if __name__ == "__main__":
    sys.exit(main())
