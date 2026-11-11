"""MS15a step 21 (F4): build and verify the Zenodo DATA package OUTSIDE the repository (DL-747 F4).

The package holds the 100 journal figure files named by docs/ms13_journal_final_hashes.txt (a folder per figure),
that hash list, docs/figure_map.md, LICENSE-DATA.md, CITATION.cff, DATA_README.md and MANIFEST.sha256. It leaves out the
EPS extras, figures/journal/export_manifest.csv, the _review folder, the provenance records, the params tables, the
drawn-data digest files and the eleven draft figures (none is named in the hash list's journal sections). Nothing is
uploaded, nothing is added to git, no network command is run. The 28 MB F1 source-data CSV is NOT zipped (reason in
DATA_README.md and DL-748).

    build:   .venv\\Scripts\\python.exe scripts\\ms15a_make_data_package.py [--dest C:\\dev\\_zenodo_data_package]
             (stops if the destination exists; every figure file is hashed against the hash list before and after the copy;
              every document file is compared with the repository working copy AND with its blob at HEAD)
    verify:  .venv\\Scripts\\python.exe scripts\\ms15a_make_data_package.py --verify [--dest ...]
             (reads only: file set, MANIFEST.sha256, hash list, repository files, README checks; exit 0 only if all hold)
"""
import argparse
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = Path(r"C:\dev\_zenodo_data_package")
HASH_LIST = "docs/ms13_journal_final_hashes.txt"
DOC_FILES = [HASH_LIST, "docs/figure_map.md", "LICENSE-DATA.md", "CITATION.cff"]   # package path = repository path
GENERATED = ["DATA_README.md", "MANIFEST.sha256"]
LINE = re.compile(r"^([0-9a-f]{64})\s+(.*?)\s+(figures/\S+)$")
REPO_URL = "https://github.com/danielvoldman/mpr-gamma-surge"

README = """# mpr-gamma-surge: data record (figure files, source data, hash list)

## What this record is

The files of the 13 journal figures of the project mpr-gamma-surge (a computational study of the dying-brain gamma surge with an exact mean-field (MPR) neural mass model and a spiking-network check): the images, the captions, the alt texts, the supplement sheets and the source data of each figure, and the list of their SHA-256 hashes. It is a DATA record. It holds no code and none of the simulation results: the folder `results/` of the project (about 32.6 GB in 32,070 files) is not part of it.

The code is at {repo}, tag `release-v1.0` (licence MIT). The software has its own archive record; this record does not replace it.

## The 13 figures

F1, F2, F3, F4a, F4b, F5, F5c, F6 and the supplementary figures FS1, FS2, FS3, FS4, FS5. F4a and F4b are two files made from one draft figure F4, and F5 and F5c two files made from one draft figure F5 (in the journal export only). FS6 was not produced. The eleven draft figures (audit copies) are not in this record.

Each figure has its own folder (`F1/` and so on) with these files (8 for F1, F2, F3, F4a, F4b, F5, F5c, F6 and FS1; 7 for FS2 to FS5, which have one caption):

- `<ID>_journal.png` and `<ID>_journal.tiff`: the image (main files).
- `<ID>_journal.pdf`: the image as a PDF (extra).
- `<ID>_journal_caption.txt`: the short caption; `<ID>_journal_caption_full.txt`: the full caption (F1 to F6 and FS1 only; for FS2 to FS5 `<ID>_journal_caption.txt` is the one caption).
- `<ID>_alt_text.txt`: the alt text.
- `<ID>_supplement.md`: the supplement sheet (tables, parameters, the full list of checks).
- `<ID>_source_data.csv`: the values drawn in the figure. The F1 file is large (28,821,335 bytes) and is provided as written, not zipped (zipping would add a file that is not in the hash list).

Other files: `docs/ms13_journal_final_hashes.txt` (the hash list), `docs/figure_map.md` (which file is which figure), `LICENSE-DATA.md`, `CITATION.cff` and `MANIFEST.sha256`.

The provenance records of the figures (which name the commit they were built from), the parameter tables, the EPS extras and the review folder of the project are not part of this record.

## Two lines in the documents are out of date

`docs/ms13_journal_final_hashes.txt` and `docs/figure_map.md` were written before the tags were created and say that the tags `fig-<ID>-v2` are "planned" and "not created". They exist now (13 tags `fig-<ID>-v2` and `release-v1.0`, all at one commit of the repository). The files are given unchanged because their hashes are named in the tag `release-v1.0`.

## Licence

Data, figures, captions, supplement sheets and text: CC-BY 4.0 (`LICENSE-DATA.md`). The full legal text of CC-BY 4.0 is not yet in that file (it is to be added from https://creativecommons.org/licenses/by/4.0/legalcode); the notice and the link are. The code is MIT.

## Author, funding, conflicts of interest

- Author: Daniel Voldman, Independent Researcher, daniel.voldman@proton.me, ORCID https://orcid.org/0009-0005-3409-8944.
- Funding: No funding received.
- Conflict of interest: The author declares no conflicts of interest.

`CITATION.cff` in this record is the citation file of the software repository (it describes the software, not this data record). It has no version, no release date and no DOI.

## How to check the files (SHA-256)

Every file listed in `MANIFEST.sha256` (all files except `MANIFEST.sha256` itself; format `<sha256><two spaces><path>`) can be checked in PowerShell from this folder:

    Get-Content MANIFEST.sha256 | ForEach-Object {{ $h, $p = $_ -split '  ', 2; if ((Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() -ne $h) {{ "DIFFERENT: $p" }} }}

The hashes of the figure files are also in `docs/ms13_journal_final_hashes.txt`, which lists them under the paths of the project (`figures/journal/F1/F1_journal.png`, and for alt text, supplement and source data `figures/journal/supplement/F1_alt_text.txt` and so on). The package path of a file is the project path without `figures/journal/` and with the supplement files moved into their figure folder: `figures/journal/supplement/F1_alt_text.txt` is `F1/F1_alt_text.txt`. The hash of each file in this record equals the hash in that list.

## What the figures claim, and what they do not

- The surge result is stated for the mean field only; there is no claim of robustness to finite-size fluctuations and no claim of class or peak-frequency agreement between the network and the mean field.
- Muscle artifact cannot be ruled out as a source of the gamma-band signal: the study is a model and nothing here tests that reading against recordings.
- No causal, clinical or consciousness claim is made.
- Several defaults and wordings are marked UNVERIFIED in the captions and the supplement sheets.
- Failures that the study produced are shown as failures in the figures and captions: network against mean field FAIL (headline path at 10 s 0 of 3 seeds and at 120 s 0 of 3 seeds, 3 of 3 needed; the 4 map cells at 30 s 1 of 4, 3 of 4 needed); headline class kept in 7 of 10 noisy seeds (8 of 10 needed); onset prediction on the testable in-range runs 0 of 6; delay under a noise floor (classifier-onset reading); the two solvers disagree on the headline onset by 181 ms (1 ms allowed); network peak frequency when the step is halved; spectral peak 49.0 Hz against cycle frequency 44.609 Hz, a difference of 4.391 Hz against 0.5 Hz; negative-control gate NOT PASSED; noisy subgrid FAILED (97 of 225 cells agree, 43.1 percent; 203 of 225 needed); the sigma check FAIL.

This record states no DOI, no publication date and nothing about any journal decision.
"""


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git_blob(rel):
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"STOP: no blob HEAD:{rel}")
    return hashlib.sha256(r.stdout).hexdigest()


def journal_entries():
    """(sha, kind, project path, package path) of the journal sections of the hash list (100 files)."""
    out = []
    for ln in (ROOT / HASH_LIST).read_text(encoding="utf-8").splitlines():
        m = LINE.match(ln)
        if not m or not m.group(3).startswith("figures/journal/"):
            continue
        proj = m.group(3)
        rest = proj[len("figures/journal/"):]
        if rest.startswith("supplement/"):
            name = rest[len("supplement/"):]
            pkg = f"{name.split('_')[0]}/{name}"
        else:
            pkg = rest
        out.append((m.group(1), m.group(2).strip(), proj, pkg))
    return out


def expected_files():
    ents = journal_entries()
    pk = [e[3] for e in ents]
    if len(pk) != len(set(pk)):
        raise SystemExit("STOP: duplicate package path")
    return ents, pk + DOC_FILES + GENERATED


def manifest_text(dest, names):
    lines = [f"{sha(dest / n)}  {n}" for n in sorted(names) if n != "MANIFEST.sha256"]
    return "\n".join(lines) + "\n"


def build(dest):
    if dest.exists():
        print(f"STOP: {dest} exists; nothing written")
        return 2
    ents, names = expected_files()
    if len(ents) != 100:
        print(f"STOP: {len(ents)} journal entries in the hash list (100 expected)")
        return 2
    for e in ents:
        src = ROOT / e[2]
        if not src.is_file() or sha(src) != e[0]:
            print(f"STOP: {e[2]} missing or differs from the hash list")
            return 2
    for d in DOC_FILES:
        if sha(ROOT / d) != git_blob(d):
            print(f"STOP: working copy of {d} differs from its blob at HEAD")
            return 2
    dest.mkdir(parents=True)
    for e in ents:
        t = dest / e[3]
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / e[2], t)
        if sha(t) != e[0]:
            print(f"STOP: copy of {e[2]} differs from the hash list")
            return 2
    for d in DOC_FILES:
        t = dest / d
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / d, t)
        if sha(t) != sha(ROOT / d):
            print(f"STOP: copy of {d} differs from the repository file")
            return 2
    (dest / "DATA_README.md").write_bytes(README.format(repo=REPO_URL).encode("utf-8"))
    (dest / "MANIFEST.sha256").write_bytes(manifest_text(dest, names).encode("utf-8"))
    return report(dest)


def report(dest):
    files = sorted(p for p in dest.rglob("*") if p.is_file())
    tot = sum(p.stat().st_size for p in files)
    print(f"files: {len(files)}; total size: {tot} bytes ({tot / 1e6:.1f} MB; {tot / 2**20:.1f} MiB)")
    print(f"MANIFEST.sha256 SHA-256: {sha(dest / 'MANIFEST.sha256')}")
    print(f"DATA_README.md SHA-256: {sha(dest / 'DATA_README.md')}")
    print("Zenodo limits of 100 files and 50 GB per record: UNVERIFIED (not in the plan or the repository); "
          f"{len(files)} files is {'within' if len(files) <= 100 else 'ABOVE'} 100 and {tot / 1e9:.3f} GB is "
          f"{'within' if tot <= 50e9 else 'ABOVE'} 50 GB if those figures are right")
    return 0


def verify(dest):
    bad = []
    if not dest.is_dir():
        print(f"STOP: {dest} does not exist")
        return 2
    ents, names = expected_files()
    have = sorted(p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file())
    if have != sorted(names):
        bad.append(f"file set differs: extra={sorted(set(have) - set(names))} missing={sorted(set(names) - set(have))}")
    # 1. every file equals the MANIFEST
    mf = (dest / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines() if (dest / "MANIFEST.sha256").is_file() else []
    man = {}
    for ln in mf:
        h, _, p = ln.partition("  ")
        man[p] = h
    for n in names:
        if n == "MANIFEST.sha256":
            continue
        if n not in man:
            bad.append(f"not in MANIFEST: {n}")
        elif (dest / n).is_file() and sha(dest / n) != man[n]:
            bad.append(f"MANIFEST hash differs: {n}")
    if set(man) != set(n for n in names if n != "MANIFEST.sha256"):
        bad.append("MANIFEST names differ from the expected file set")
    if (dest / "MANIFEST.sha256").is_file() and (dest / "MANIFEST.sha256").read_bytes() != manifest_text(dest, names).encode("utf-8"):
        bad.append("MANIFEST.sha256 differs from a fresh manifest of the files")
    # 2. every figure file equals the hash list AND the repository file
    for e in ents:
        p = dest / e[3]
        if p.is_file() and (sha(p) != e[0] or sha(ROOT / e[2]) != e[0]):
            bad.append(f"differs from the hash list or its source: {e[3]}")
    # 3. documents equal the repository working copy and the blob at HEAD
    for d in DOC_FILES:
        if (dest / d).is_file() and not (sha(dest / d) == sha(ROOT / d) == git_blob(d)):
            bad.append(f"differs from the repository: {d}")
    # 4. README: no DOI, no date, no journal-decision wording
    rd = (dest / "DATA_README.md").read_text(encoding="utf-8") if (dest / "DATA_README.md").is_file() else ""
    if rd.encode("utf-8") != README.format(repo=REPO_URL).encode("utf-8"):
        bad.append("DATA_README.md differs from the text of this script")
    for pat, what in [(r"10\.\d{4,9}/", "DOI pattern"), (r"(?i)doi\.org|\bDOI:", "DOI marker"), (r"\d{4}-\d{2}-\d{2}", "ISO date"),
                      (r"(?i)\baccepted\b|\bpublished on\b|\bpeer.reviewed\b", "publication or decision wording")]:
        if re.search(pat, rd):
            bad.append(f"DATA_README.md has a {what}")
    # 5. the figure file counts
    n = {}
    for e in ents:
        n.setdefault(e[3].split("/")[0], 0)
        n[e[3].split("/")[0]] += 1
    if sorted(n.values()) != [7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8] or len(n) != 13:
        bad.append(f"per-figure file counts unexpected: {n}")
    for b in bad:
        print("PROBLEM:", b)
    print(f"verify: {len(have)} files, {len(bad)} problem(s)")
    if not bad:
        report(dest)
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default=str(DEST))
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    return verify(Path(a.dest)) if a.verify else build(Path(a.dest))


if __name__ == "__main__":
    sys.exit(main())
