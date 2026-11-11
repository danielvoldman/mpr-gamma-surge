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

MS15a step 22 (DL-751 G2, close item 86): the --zips mode writes a SECOND package, one zip per figure (13 zips, 100 files inside) plus
7 unzipped top-level files (20 files in all), to C:\\dev\\_zenodo_data_package_zips. The old mode above is unchanged.

    build:   .venv\\Scripts\\python.exe scripts\\ms15a_make_data_package.py --zips [--dest ...]
             (builds the whole package twice into two scratch folders, compares every file by SHA-256, STOPS if they differ,
              otherwise copies the first build to the destination; the destination and both scratch folders must not exist)
    verify:  .venv\\Scripts\\python.exe scripts\\ms15a_make_data_package.py --zips --verify [--dest ...]

Zips are deterministic: entries sorted by path, date 1980-01-01 00:00:00 on every entry, deflate level 6, no extra field, no comment,
external attributes 0, create_system 0, no directory entries, forward slashes. A deflate stream depends on the zlib version: equal bytes
are shown for two builds on one machine, not claimed for another (UNVERIFIED). Each entry has the path the hash list gives the file.
"""
import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import zipfile
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


README_ZIPS = """# mpr-gamma-surge: data record (figure files, source data, hash list)

## What this record is

The files of the 13 journal figures of the project mpr-gamma-surge (a computational study of the dying-brain gamma surge with an exact mean-field (MPR) neural mass model and a spiking-network check): the images, the captions, the alt texts, the supplement sheets and the source data of each figure, and the list of their SHA-256 hashes. It is a DATA record. It holds no code and none of the simulation results: the folder `results/` of the project (about 32.6 GB in 32,070 files) is not part of it.

The code is at {repo}, tag `release-v1.0` (licence MIT). The software has its own archive record; this record does not replace it.

## The 13 figures

F1, F2, F3, F4a, F4b, F5, F5c, F6 and the supplementary figures FS1, FS2, FS3, FS4, FS5. F4a and F4b are two files made from one draft figure F4, and F5 and F5c two files made from one draft figure F5 (in the journal export only). FS6 was not produced. The eleven draft figures (audit copies) are not in this record.

## How the files are packed

The figure files are in 13 zip files, one per figure: `F1_journal_files.zip`, `F2_journal_files.zip`, and so on up to `FS5_journal_files.zip` (`<ID>_journal_files.zip`). Each zip holds the files of its figure (8 for F1, F2, F3, F4a, F4b, F5, F5c, F6 and FS1; 7 for FS2 to FS5, which have one caption; 100 files in all):

- `<ID>_journal.png` and `<ID>_journal.tiff`: the image (main files).
- `<ID>_journal.pdf`: the image as a PDF (extra).
- `<ID>_journal_caption.txt`: the short caption; `<ID>_journal_caption_full.txt`: the full caption (F1 to F6 and FS1 only; for FS2 to FS5 `<ID>_journal_caption.txt` is the one caption).
- `<ID>_alt_text.txt`: the alt text.
- `<ID>_supplement.md`: the supplement sheet (tables, parameters, the full list of checks).
- `<ID>_source_data.csv`: the values drawn in the figure. The F1 file is large (28,821,335 bytes); it is inside `F1_journal_files.zip`, as written (the file is the one the hash list names; only its container is a zip).

Inside a zip every file has the path that `docs/ms13_journal_final_hashes.txt` gives it: `figures/journal/F1/F1_journal.png`, and for alt text, supplement and source data `figures/journal/supplement/F1_alt_text.txt` and so on. After unzipping, every path of the hash list for these figures exists. A zip has no folder entries, no comment and one fixed time stamp on all its entries; the entries are sorted by path.

Files outside the zips (unzipped, in this folder): `docs/ms13_journal_final_hashes.txt` (the hash list), `docs/figure_map.md` (which file is which figure), `LICENSE-DATA.md`, `CITATION.cff`, this file, `MANIFEST.sha256` and `MANIFEST_inner.sha256`.

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

1. The files of this folder. `MANIFEST.sha256` lists the SHA-256 of every file of this folder except itself (the 13 zips and the unzipped files; format `<sha256><two spaces><path>`). In PowerShell from this folder:

       Get-Content MANIFEST.sha256 | ForEach-Object {{ $h, $p = $_ -split '  ', 2; if ((Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() -ne $h) {{ "DIFFERENT: $p" }} }}

2. The files inside the zips. Unzip every zip into one folder, then compare the SHA-256 of each unzipped file with the hash list `docs/ms13_journal_final_hashes.txt`, which gives the hash beside the path (`figures/journal/...`) of each file. In PowerShell from this folder:

       Get-ChildItem *_journal_files.zip | ForEach-Object {{ Expand-Archive -LiteralPath $_.FullName -DestinationPath unzipped }}

   `MANIFEST_inner.sha256` lists the same hashes for the 100 files inside the zips, one line per file, in the form `<sha256><two spaces><zip name>:<path in the zip>`. It equals the 100 figure lines of the hash list (the hash list has further lines for the eleven draft figures, which are not part of this record). To compare the unzipped files with it:

       Get-Content MANIFEST_inner.sha256 | ForEach-Object {{ $h, $r = $_ -split '  ', 2; $p = ($r -split ':', 2)[1]; if ((Get-FileHash -Algorithm SHA256 -LiteralPath "unzipped/$p").Hash.ToLower() -ne $h) {{ "DIFFERENT: $p" }} }}

The hash of each file in this record equals the hash in the hash list.

## What the figures claim, and what they do not

- The surge result is stated for the mean field only; there is no claim of robustness to finite-size fluctuations and no claim of class or peak-frequency agreement between the network and the mean field.
- Muscle artifact cannot be ruled out as a source of the gamma-band signal: the study is a model and nothing here tests that reading against recordings.
- No causal, clinical or consciousness claim is made.
- Several defaults and wordings are marked UNVERIFIED in the captions and the supplement sheets.
- Failures that the study produced are shown as failures in the figures and captions: network against mean field FAIL (headline path at 10 s 0 of 3 seeds and at 120 s 0 of 3 seeds, 3 of 3 needed; the 4 map cells at 30 s 1 of 4, 3 of 4 needed); headline class kept in 7 of 10 noisy seeds (8 of 10 needed); onset prediction on the testable in-range runs 0 of 6; delay under a noise floor (classifier-onset reading); the two solvers disagree on the headline onset by 181 ms (1 ms allowed); network peak frequency when the step is halved; spectral peak 49.0 Hz against cycle frequency 44.609 Hz, a difference of 4.391 Hz against 0.5 Hz; negative-control gate NOT PASSED; noisy subgrid FAILED (97 of 225 cells agree, 43.1 percent; 203 of 225 needed); the sigma check FAIL.

This record states no DOI, no publication date and nothing about any journal decision.
"""

# ---- the --zips mode (MS15a 22, DL-751 G2) ---------------------------------------------------------------------------------------------------
ZIP_DEST = Path(r"C:\dev\_zenodo_data_package_zips")
ZIP_SCRATCH = (Path(r"C:\dev\_zenodo_zips_scratch_a"), Path(r"C:\dev\_zenodo_zips_scratch_b"))
ZIP_DATE = (1980, 1, 1, 0, 0, 0)        # the ZIP minimum
ZIP_LEVEL = 6                           # deflate
INNER = "MANIFEST_inner.sha256"
ZIP_TOP = DOC_FILES + ["DATA_README.md", "MANIFEST.sha256", INNER]      # the unzipped top-level files (7)


class Stop(Exception):
    pass


def zip_name(fid):
    return f"{fid}_journal_files.zip"


def figure_groups(ents):
    """{figure ID: [(sha, kind, project path, package path)] sorted by project path}, IDs sorted by name."""
    g = {}
    for e in ents:
        g.setdefault(e[3].split("/")[0], []).append(e)
    return {k: sorted(v, key=lambda e: e[2]) for k, v in sorted(g.items())}


def zip_expected_names(ents):
    return [zip_name(f) for f in figure_groups(ents)] + ZIP_TOP


def write_zip(path, members):
    """members: [(entry name, bytes)] in the order to write (sorted by the caller). Deterministic: see the module docstring."""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=ZIP_LEVEL) as zf:
        for name, data in members:
            zi = zipfile.ZipInfo(name, ZIP_DATE)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 0
            zi.external_attr = 0
            zi.extra = b""
            zi.comment = b""
            zf.writestr(zi, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=ZIP_LEVEL)


def zip_members_hashes(path):
    """[(entry name, sha256 of the member read back)] in the order of the zip; raises Stop on a bad CRC."""
    out = []
    with zipfile.ZipFile(path) as zf:
        if zf.testzip() is not None:
            raise Stop(f"{path.name}: bad member {zf.testzip()}")
        for zi in zf.infolist():
            out.append((zi.filename, hashlib.sha256(zf.read(zi)).hexdigest()))
    return out


def inner_manifest_text(dest, ents):
    lines = []
    for fid in figure_groups(ents):
        zn = zip_name(fid)
        for name, h in sorted(zip_members_hashes(dest / zn)):
            lines.append(f"{h}  {zn}:{name}")
    return "\n".join(lines) + "\n"


def zips_manifest_text(dest, ents):
    names = [n for n in zip_expected_names(ents) if n != "MANIFEST.sha256"]
    return "\n".join(f"{sha(dest / n)}  {n}" for n in sorted(names)) + "\n"


def make_zip_package(dest):
    """Writes the whole zips package to dest (must not exist). Raises Stop on any difference from the hash list or the repository."""
    if dest.exists():
        raise Stop(f"{dest} exists; nothing written")
    ents = journal_entries()
    if len(ents) != 100:
        raise Stop(f"{len(ents)} journal entries in the hash list (100 expected)")
    for e in ents:
        src = ROOT / e[2]
        if not src.is_file() or sha(src) != e[0]:
            raise Stop(f"{e[2]} missing or differs from the hash list")
    for d in DOC_FILES:
        if sha(ROOT / d) != git_blob(d):
            raise Stop(f"working copy of {d} differs from its blob at HEAD")
    dest.mkdir(parents=True)
    for fid, grp in figure_groups(ents).items():
        members = []
        for e in grp:                                   # sorted by project path
            data = (ROOT / e[2]).read_bytes()
            if hashlib.sha256(data).hexdigest() != e[0]:
                raise Stop(f"{e[2]} read differs from the hash list")
            members.append((e[2], data))
        write_zip(dest / zip_name(fid), members)
        back = zip_members_hashes(dest / zip_name(fid))
        if back != [(e[2], e[0]) for e in grp]:
            raise Stop(f"{zip_name(fid)}: a member read back differs from the hash list")
    for d in DOC_FILES:
        t = dest / d
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / d, t)
        if sha(t) != sha(ROOT / d):
            raise Stop(f"copy of {d} differs from the repository file")
    (dest / "DATA_README.md").write_bytes(README_ZIPS.format(repo=REPO_URL).encode("utf-8"))
    (dest / INNER).write_bytes(inner_manifest_text(dest, ents).encode("utf-8"))
    (dest / "MANIFEST.sha256").write_bytes(zips_manifest_text(dest, ents).encode("utf-8"))


def tree_hashes(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob("*")) if p.is_file()}


def build_zips(dest, scratch=ZIP_SCRATCH):
    for d in (dest, *scratch):
        if d.exists():
            print(f"STOP: {d} exists; nothing written")
            return 2
    try:
        for s in scratch:
            make_zip_package(s)
        a, b = (tree_hashes(s) for s in scratch)
        if a != b:
            diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
            print(f"STOP: the two builds differ in {diff}; {dest} is not written")
            return 2
        print(f"the two builds are byte-identical: {len(a)} files, full SHA-256 of every file equal")
        shutil.copytree(scratch[0], dest)
        if tree_hashes(dest) != a:
            print("STOP: the copy to the destination differs from the first build")
            return 2
    except Stop as e:
        print(f"STOP: {e}")
        return 2
    return report_zips(dest)


def report_zips(dest):
    files = sorted(p for p in dest.rglob("*") if p.is_file())
    tot = sum(p.stat().st_size for p in files)
    print(f"files: {len(files)}; total size: {tot} bytes ({tot / 1e6:.1f} MB; {tot / 2**20:.1f} MiB)")
    for p in files:
        if p.suffix == ".zip":
            print(f"  {p.name}: {p.stat().st_size} bytes, SHA-256 {sha(p)}")
    print(f"MANIFEST.sha256 SHA-256: {sha(dest / 'MANIFEST.sha256')}")
    print(f"{INNER} SHA-256: {sha(dest / INNER)}")
    print(f"DATA_README.md SHA-256: {sha(dest / 'DATA_README.md')}")
    print("Zenodo limits of 100 files and 50 GB per record: UNVERIFIED (not in the plan or the repository); "
          f"{len(files)} files is {'within' if len(files) <= 100 else 'ABOVE'} 100 and {tot / 1e9:.3f} GB is "
          f"{'within' if tot <= 50e9 else 'ABOVE'} 50 GB if those figures are right")
    return 0


def verify_zips(dest):
    bad = []
    if not dest.is_dir():
        print(f"STOP: {dest} does not exist")
        return 2
    ents = journal_entries()
    groups = figure_groups(ents)
    names = zip_expected_names(ents)
    have = sorted(p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file())
    if have != sorted(names):
        bad.append(f"file set differs: extra={sorted(set(have) - set(names))} missing={sorted(set(names) - set(have))}")
    if len(have) >= 100:
        bad.append(f"{len(have)} files (below 100 wanted)")
    # 1. MANIFEST.sha256: every top-level file and every zip, hash matches, equals a fresh manifest
    mp = dest / "MANIFEST.sha256"
    man = dict((ln.partition("  ")[2], ln.partition("  ")[0]) for ln in mp.read_text(encoding="utf-8").splitlines()) if mp.is_file() else {}
    want = [n for n in names if n != "MANIFEST.sha256"]
    if sorted(man) != sorted(want):
        bad.append("MANIFEST.sha256 names differ from the expected file set")
    for n in want:
        if n in man and (dest / n).is_file() and sha(dest / n) != man[n]:
            bad.append(f"MANIFEST hash differs: {n}")
    # 2. the zips: entry properties, names, and every member equals the hash list and the repository file
    inner = set()
    for fid, grp in groups.items():
        zp = dest / zip_name(fid)
        if not zp.is_file():
            continue
        with zipfile.ZipFile(zp) as zf:
            infos = zf.infolist()
            nm = [zi.filename for zi in infos]
            if nm != sorted(nm) or len(nm) != len(set(nm)):
                bad.append(f"{zp.name}: entries not sorted or duplicated")
            if nm != [e[2] for e in grp]:
                bad.append(f"{zp.name}: entry names differ from the hash list")
            if zf.comment != b"":
                bad.append(f"{zp.name}: has a comment")
            for zi in infos:
                if (zi.date_time != ZIP_DATE or zi.compress_type != zipfile.ZIP_DEFLATED or zi.extra != b"" or zi.comment != b""
                        or zi.external_attr != 0 or zi.create_system != 0 or zi.filename.endswith("/") or "\\" in zi.filename):
                    bad.append(f"{zp.name}: entry {zi.filename} has other properties than the fixed ones")
        for (n, h), e in zip(zip_members_hashes(zp), grp):
            inner.add((h, e[2]))
            if n == e[2] and (h != e[0] or sha(ROOT / e[2]) != e[0]):
                bad.append(f"differs from the hash list or its source: {zp.name}:{n}")
    # 3. MANIFEST_inner.sha256 equals a fresh one and equals the hash list for the 100 files
    ip = dest / INNER
    if ip.is_file():
        if all((dest / zip_name(f)).is_file() for f in groups) and ip.read_bytes() != inner_manifest_text(dest, ents).encode("utf-8"):
            bad.append(f"{INNER} differs from a fresh list of the zip members")
        rows = {(ln.partition("  ")[0], ln.partition("  ")[2].split(":", 1)[1]) for ln in ip.read_text(encoding="utf-8").splitlines()}
        if rows != {(e[0], e[2]) for e in ents} or len(rows) != 100:
            bad.append(f"{INNER} does not equal the hash list for the 100 figure files")
    else:
        bad.append(f"{INNER} missing")
    # 4. documents equal the repository working copy and the blob at HEAD
    for d in DOC_FILES:
        if (dest / d).is_file() and not (sha(dest / d) == sha(ROOT / d) == git_blob(d)):
            bad.append(f"differs from the repository: {d}")
    # 5. README: the text of this script; no DOI, date or decision wording
    rd = (dest / "DATA_README.md").read_text(encoding="utf-8") if (dest / "DATA_README.md").is_file() else ""
    if rd.encode("utf-8") != README_ZIPS.format(repo=REPO_URL).encode("utf-8"):
        bad.append("DATA_README.md differs from the text of this script")
    for pat, what in [(r"10\.\d{4,9}/", "DOI pattern"), (r"(?i)doi\.org|\bDOI:", "DOI marker"), (r"\d{4}-\d{2}-\d{2}", "ISO date"),
                      (r"(?i)\baccepted\b|\bpublished on\b|\bpeer.reviewed\b", "publication or decision wording")]:
        if re.search(pat, rd):
            bad.append(f"DATA_README.md has a {what}")
    # 6. figure counts
    cnt = sorted(len(g) for g in groups.values())
    if cnt != [7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8] or len(groups) != 13:
        bad.append(f"per-figure file counts unexpected: {cnt}")
    for b in bad:
        print("PROBLEM:", b)
    print(f"verify (zips): {len(have)} files, {len(bad)} problem(s)")
    if not bad:
        report_zips(dest)
    return 1 if bad else 0


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
    ap.add_argument("--dest", default=None)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--zips", action="store_true", help="the second package: one zip per figure (MS15a 22, DL-751 G2)")
    a = ap.parse_args()
    if a.zips:
        dest = Path(a.dest) if a.dest else ZIP_DEST
        try:
            return verify_zips(dest) if a.verify else build_zips(dest)
        except Stop as e:
            print(f"STOP: {e}")
            return 2
    dest = Path(a.dest) if a.dest else DEST
    return verify(dest) if a.verify else build(dest)


if __name__ == "__main__":
    sys.exit(main())
