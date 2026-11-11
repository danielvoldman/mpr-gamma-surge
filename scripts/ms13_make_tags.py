"""MS13 13u (DL-723, DL-724): make the 13 annotated local tags fig-<ID>-v1 of the journal figures. Local only: no push, no upload, no signing.

  python scripts/ms13_make_tags.py                 DRY RUN (default): print the 13 names, the target commit, every message and the preconditions; create nothing
  python scripts/ms13_make_tags.py --create        make the 13 tags, all at the target commit, only if every precondition holds
  python scripts/ms13_make_tags.py --verify        read-only check of the 13 tags that exist
  --target REV                                     the commit the tags point to (default HEAD)
  --version v1|v2                                  which tag family (default v1; v2 = MS15a 20, DL-744, DL-745: the figures rebuilt from R with draft false)
  --release                                        only with --version v2: also the tag release-v1.0 (14 tags in one scripted run)

Every value of a tag message is taken from docs/ms13_journal_final_hashes.txt (the file/hash lines are copied verbatim) or from the tag criteria-frozen and the decision log.
The figure files are git-ignored outputs (figures/): they are not in a tagged tree. The hash list docs/ms13_journal_final_hashes.txt is. An existing tag is never deleted or moved.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HASH_LIST = "docs/ms13_journal_final_hashes.txt"
DECISION_LOG = "docs/decision_log.md"
IDS = "F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5".split()
VERSION = 1
RELEASE_TAG = "release-v1.0"
AUTHOR_LINE = "Author: Daniel Voldman (ORCID https://orcid.org/0009-0005-3409-8944)"
LICENCE_LINE = "Licences: MIT (code); CC-BY 4.0 (data, figures and text)"
RELEASE_SENTENCE = ("The figure provenance names R; release-v1.0 differs from R only in documents, the figure map, the hash list "
                    "and helper scripts for tagging and hash lists.")
VENUE = "Peer Community Journal"
CRITERIA_TAG = "criteria-frozen"
DL_FIRST = 698
FILE_LINE = re.compile(r"^([0-9a-f]{64})  (.+?)\s+(figures/\S+)$")
SECTION = re.compile(r"^## (F[S]?\d[a-c]?) \((journal main version; draft audit copy: [^)]+)\)$")
NOTE = ("Note: figures/ is git-ignored, so these files are not in the tagged tree; the same hash lines are in " + HASH_LIST + " of the tagged tree. "
        "Journal files are the main versions; the drafts are audit copies and are not tagged.")


def tag_name(fid: str, version: int = VERSION) -> str:
    return f"fig-{fid}-v{version}"


def git(root, *args, stdin=None):
    return subprocess.run(["git", *args], cwd=root, input=stdin, capture_output=True)


def git_text(root, *args) -> str:
    r = git(root, *args)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout.decode("utf-8")


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def parse_hash_list(text: str) -> dict:
    """{id: {'heading', 'commit', 'digest', 'lines': [raw file/hash lines], 'files': [(sha, label, path)]}} for the journal sections only."""
    out, cur = {}, None
    for line in text.splitlines():
        m = SECTION.match(line)
        if m:
            cur = out[m.group(1)] = {"heading": f"{m.group(1)} ({m.group(2)})", "commit": None, "digest": None, "lines": [], "files": []}
            continue
        if line.startswith("## "):
            cur = None
            continue
        if cur is None:
            continue
        if line.startswith("built from commit: "):
            cur["commit"] = line.split(": ", 1)[1].strip()
        elif line.startswith("drawn-data digest: "):
            cur["digest"] = line.split(": ", 1)[1].strip()
        else:
            m = FILE_LINE.match(line)
            if m:
                cur["lines"].append(line)
                cur["files"].append((m.group(1), m.group(2), m.group(3)))
    return out


def last_dl(log_text: str) -> int:
    nums = [int(n) for n in re.findall(r"^## DL-(\d+)\b", log_text, re.M)]
    return max(nums)


def criteria_info(root) -> dict:
    commit = git_text(root, "rev-parse", f"{CRITERIA_TAG}^{{commit}}").strip()
    msg = git_text(root, "tag", "-l", "--format=%(contents)", CRITERIA_TAG)
    m = re.search(r"as committed in ([0-9a-f]{40})\): ([0-9a-f]{64})", msg)
    if not m:
        raise RuntimeError(f"cannot read the criteria SHA-256 from the message of tag {CRITERIA_TAG}")
    if m.group(1) != commit:
        raise RuntimeError(f"tag {CRITERIA_TAG}: commit in its message {m.group(1)} differs from the tag commit {commit}")
    return {"commit": commit, "sha256": m.group(2)}


def build_message(fid: str, entry: dict, crit: dict, dl_last: int, version: int = VERSION) -> str:
    out = [f"{tag_name(fid, version)}: journal figure {fid}",
           f"Section of the hash list: {entry['heading']}",
           f"Venue: {VENUE}",
           f"Build commit: {entry['commit']}",
           f"Drawn-data digest: {entry['digest']}",
           f"Criteria tag: {CRITERIA_TAG} (commit {crit['commit']})",
           f"Criteria SHA-256: {crit['sha256']}",
           f"Decision log: DL-{DL_FIRST} to DL-{dl_last}"]
    if version >= 2:
        out += [f"supersedes {tag_name(fid, 1)} (local only, not published)",
                f"provenance: draft false, built from R = {entry['commit']}"]
    out += ["Files (full SHA-256, kind, path; lines copied from " + HASH_LIST + "):"]
    out += entry["lines"]
    out.append(NOTE)
    return "\n".join(out) + "\n"


def parse_message(msg: str) -> dict:
    d = {"files": []}
    for line in msg.splitlines():
        if FILE_LINE.match(line):
            d["files"].append(line)
        else:
            for key, pre in (("name", None), ("section", "Section of the hash list: "), ("venue", "Venue: "), ("commit", "Build commit: "), ("digest", "Drawn-data digest: "),
                             ("criteria_tag", "Criteria tag: "), ("criteria_sha", "Criteria SHA-256: "), ("dl", "Decision log: "),
                             ("supersedes", "supersedes "), ("provenance", "provenance: ")):
                if pre and line.startswith(pre):
                    d[key] = line[len(pre):]
            if line.startswith("fig-") and ": journal figure " in line:
                d["name"] = line.split(":", 1)[0]
                d["fid"] = line.rsplit(" ", 1)[1]
    return d


def make_plan(root, target: str, version: int = VERSION) -> list:
    """[(name, message)] for the 13 figures, from the hash list and the log at the target commit."""
    lst = parse_hash_list(git_text(root, "show", f"{target}:{HASH_LIST}"))
    missing = [i for i in IDS if i not in lst]
    extra = [i for i in lst if i not in IDS]
    if missing or extra:
        raise RuntimeError(f"hash list sections differ from the 13 figures: missing {missing}, extra {extra}")
    crit = criteria_info(root)
    dl = last_dl(git_text(root, "show", f"{target}:{DECISION_LOG}"))
    return [(tag_name(i, version), build_message(i, lst[i], crit, dl, version)) for i in IDS]


def build_commit_of_list(lst: dict) -> str:
    """R: the one build commit named in all 13 sections of the hash list (refuse if they differ)."""
    commits = {e["commit"] for e in lst.values()}
    if len(commits) != 1 or None in commits:
        raise RuntimeError(f"the 13 sections of the hash list do not name one build commit: {sorted(map(str, commits))}")
    return commits.pop()


def release_message(root, target: str) -> str:
    """The message of release-v1.0: every value read from the files at the target (the hash list blob, the tag criteria-frozen, the log)."""
    lst = parse_hash_list(git_text(root, "show", f"{target}:{HASH_LIST}"))
    blob = git(root, "show", f"{target}:{HASH_LIST}").stdout
    crit = criteria_info(root)
    r = build_commit_of_list(lst)
    out = [f"{RELEASE_TAG}: release of the journal figures and the code of mpr-gamma-surge",
           AUTHOR_LINE,
           LICENCE_LINE,
           "Figure tags (13): " + " ".join(tag_name(i, 2) for i in IDS),
           f"Hash list: {HASH_LIST} SHA-256 {hashlib.sha256(blob).hexdigest()}",
           f"R (build commit named in the figure provenance records): {r}",
           f"T (the commit this tag and the 13 figure tags point to): {target}",
           f"Criteria tag: {CRITERIA_TAG} (commit {crit['commit']})",
           f"Criteria SHA-256: {crit['sha256']}",
           RELEASE_SENTENCE]
    return "\n".join(out) + "\n"


def provenance_problems(root, lst: dict) -> list:
    """The message of a v2 tag says 'draft false, built from R': read the 13 provenance records and refuse if they do not say so."""
    problems = []
    for fid, e in lst.items():
        p = Path(root) / f"figures/journal/{fid}/{fid}_journal_provenance.json"
        if not p.is_file():
            problems.append(f"{fid}: provenance record missing {p.name}")
            continue
        rec = json.loads(p.read_text(encoding="utf-8"))
        g = rec.get("git") or {}
        if rec.get("draft") is not False or g.get("dirty") is not False or g.get("commit") != e["commit"]:
            problems.append(f"{fid}: provenance says draft={rec.get('draft')}, dirty={g.get('dirty')}, commit={g.get('commit')}; expected false, false, {e['commit']}")
    return problems


def preconditions(root, target: str, check_gate=True, check_files=True, version: int = VERSION, release: bool = False) -> list:
    """Problems found (empty list = every precondition holds)."""
    root = Path(root)
    problems = []
    head = git_text(root, "rev-parse", "HEAD").strip()
    if head != target:
        problems.append(f"target {target} is not HEAD {head}")
    st = git_text(root, "status", "--porcelain").strip()
    if st:
        problems.append("working tree is not clean: " + st.replace("\n", "; ")[:300])
    if version == 1:
        have = git_text(root, "tag", "-l", "fig-*").split()
        if have:
            problems.append("fig-* tags already exist: " + ", ".join(have))
    else:
        have = git_text(root, "tag", "-l", f"fig-*-v{version}").split()
        if have:
            problems.append(f"fig-*-v{version} tags already exist: " + ", ".join(have))
        missing = [tag_name(i, 1) for i in IDS if not git_text(root, "tag", "-l", tag_name(i, 1)).strip()]
        if missing:
            problems.append("tags named as superseded do not exist: " + ", ".join(missing))
    if release:
        if version < 2:
            problems.append("--release needs --version v2")
        if git_text(root, "tag", "-l", RELEASE_TAG).strip():
            problems.append(f"tag {RELEASE_TAG} already exists")
    blob = git(root, "show", f"{target}:{HASH_LIST}").stdout
    work = (root / HASH_LIST).read_bytes()
    if blob != work:
        problems.append(f"{HASH_LIST}: working copy differs from its blob at the target")
    if check_gate:
        try:
            sys.path.insert(0, str(root / "src"))
            from mprsurge import criteria
            criteria.verify_frozen_criteria(root)
        except Exception as e:  # report, do not hide
            problems.append(f"criteria gate: {e}")
    if check_files:
        for fid, e in parse_hash_list(work.decode("utf-8")).items():
            for h, label, path in e["files"]:
                p = root / path
                if not p.is_file():
                    problems.append(f"{fid}: file missing {path}")
                elif sha_file(p) != h:
                    problems.append(f"{fid}: SHA-256 of {path} differs from the hash list")
        if version >= 2:
            problems += provenance_problems(root, parse_hash_list(work.decode("utf-8")))
    return problems


def create(root, target: str, plan: list) -> list:
    """Create the tags (annotated, no force, no signing). Return the names created; raise after listing them if one fails."""
    made = []
    for name, msg in plan:
        r = git(root, "tag", "-a", "--cleanup=verbatim", "-F", "-", name, target, stdin=msg.encode("utf-8"))
        if r.returncode != 0:
            raise RuntimeError(f"tag {name} FAILED: {r.stderr.decode('utf-8', 'replace').strip()}; created before it: {made}")
        made.append(name)
    return made


def tag_message(root, name: str) -> str:
    raw = git_text(root, "cat-file", "tag", name)
    return raw.split("\n\n", 1)[1]


def verify(root, target: str, plan: list) -> list:
    """Rows (name, annotated, target_ok, message_ok, list_in_tree_ok, files_ok). A plan entry after the 13 figures is the release tag: its files_ok covers every file of the list."""
    root = Path(root)
    work = (root / HASH_LIST).read_bytes()
    rows = []
    for (name, msg), fid in zip(plan, IDS + [None] * (len(plan) - len(IDS))):
        typ = git(root, "cat-file", "-t", name).stdout.decode().strip()
        tgt = git(root, "rev-parse", f"{name}^{{commit}}").stdout.decode().strip()
        try:
            got = tag_message(root, name)
        except Exception:
            got = None
        in_tree = git(root, "show", f"{name}:{HASH_LIST}").stdout == work
        entries = parse_hash_list(work.decode("utf-8"))
        chosen = entries.values() if fid is None else [entries[fid]]
        files_ok = all((root / p).is_file() and sha_file(root / p) == h for e in chosen for h, _, p in e["files"])
        rows.append((name, typ == "tag", tgt == target, got is not None and got.rstrip("\n") == msg.rstrip("\n"), in_tree, files_ok))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--create", action="store_true")
    g.add_argument("--verify", action="store_true")
    ap.add_argument("--target", default="HEAD")
    ap.add_argument("--version", choices=["v1", "v2"], default="v1")
    ap.add_argument("--release", action="store_true")
    a = ap.parse_args(argv)
    version = int(a.version[1:])
    if a.release and version < 2:
        print("--release needs --version v2")
        return 2
    target = git_text(ROOT, "rev-parse", f"{a.target}^{{commit}}").strip()
    plan = make_plan(ROOT, target, version)
    if a.release:
        plan.append((RELEASE_TAG, release_message(ROOT, target)))
    if a.verify:
        rows = verify(ROOT, target, plan)
        print(f"target {target}")
        print("tag | annotated | target equal | message equal | hash list in tag tree equal | files on disk equal")
        for r in rows:
            print(" | ".join([r[0]] + ["yes" if x else "NO" for x in r[1:]]))
        return 0 if all(all(r[1:]) for r in rows) else 1
    problems = preconditions(ROOT, target, version=version, release=a.release)
    print(f"{'CREATE' if a.create else 'DRY RUN'}: {len(plan)} tags at target commit {target}")
    print("names:", " ".join(n for n, _ in plan))
    for name, msg in plan:
        print(f"\n=== {name} -> {target}\n{msg}", end="")
    print(f"\nPRECONDITIONS: {'all hold' if not problems else str(len(problems)) + ' problem(s)'}")
    for p in problems:
        print("  PROBLEM:", p)
    if not a.create:
        print("dry run: nothing created")
        return 1 if problems else 0
    if problems:
        print("NOT CREATED: a precondition does not hold")
        return 1
    try:
        made = create(ROOT, target, plan)
    except RuntimeError as e:
        print("STOP:", e)
        print("tags that exist now:", git_text(ROOT, "tag", "-l", "fig-*", RELEASE_TAG).split())
        return 2
    print("created:", ", ".join(made))
    return 0


if __name__ == "__main__":
    sys.exit(main())
