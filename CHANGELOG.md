# Changelog

The plan (docs/plan.md, line 1023) asks for one entry per release tag. The tag `release-v1.0` exists (annotated, commit 33b7575721184b90571c2bbaffc4a9a0b1607a77, the commit that holds the first version of this text). The section "release-v1.0" lists what that tag contains (up to MS15a part 2b); the section "Unreleased" lists what was added after it. No date is given and no version beyond the tag name; no DOI is assigned.

## release-v1.0

### Added

- MS13 figures: the 13 journal figures F1, F2, F3, F4a, F4b, F5, F5c, F6, FS1, FS2, FS3, FS4 and FS5 (PNG and TIFF at 600 dpi, PDF, captions, alt text, supplement sheets, source data, provenance records), built from stored results; the eleven drafts are audit copies. The files are git-ignored; their SHA-256 hashes are in `docs/ms13_journal_final_hashes.txt` and `docs/figure_map.md`. FS6 is not produced (user ruling of 2026-11-09, `docs/ms13_close.md`).
- 13 annotated local tags `fig-<ID>-v1` for the 13 journal figures (all at commit e6666cb2e8120a1619527c5ee7fce01e1beedb55; tag messages hold the file hashes). Not pushed.
- MS14: `docs/search_log.md` with the plan's Table E.1 and items 1 to 7 recorded as "Not done natively on Nov 10; general web-search pre-check only". MS14 was closed by user ruling as a departure from the plan; its limits are in `docs/ms13_close.md` section (7).
- MS15a, part 1 (the release files; user rulings of 2026-11-10 in `docs/ms15_scope_notes.md`): `LICENSE` (MIT), `LICENSE-DATA.md` (CC-BY 4.0 notice; the legal text is still to be added), `CITATION.cff`, `.zenodo.json`, `scripts/make_all.ps1` (written and not run), `docs/figure_map.md`, `scripts/ms15a_write_figure_map.py`, `docs/ms15_draft_flag_notes.md`, `tests/test_ms15a_release.py`, a full `README.md`.

- MS15a, part 2a (user ruling of 2026-11-10, 18:21, option B of `docs/ms15_draft_flag_notes.md`; `docs/decision_log.md` DL-738 to DL-743): `scripts/fig_journal.py --release` (alias `--tag`: clean-tree check first, provenance `draft = false` on a clean tree), the supplement text follows the draft flag, and the 13 journal figures were rebuilt once from the clean commit 90b177acc694de0b9756542f236977d782f185e1 (every provenance record: `draft = false`, `dirty = false`, that commit). PNG, TIFF and PDF are byte-identical to the first build; supplements and provenance records are new. `tests/test_ms15a_draft_flag.py`. The `fig-<ID>-v2` tags and `release-v1.0` follow in sub-step 20 (next entry).

- MS15a, part 2b (sub-step 20; user ruling of 2026-11-10, 18:21, "defaults"; `docs/decision_log.md` DL-744 and DL-745): `scripts/ms13_make_tags.py --version v2 --release` and `tests/test_ms15a_tags.py`; created at commit T: 13 annotated local tags `fig-<ID>-v2` (the files of the rebuild from R = 90b177acc694de0b9756542f236977d782f185e1; each message holds the full SHA-256 of every file, "supersedes fig-<ID>-v1 (local only, not published)" and "provenance: draft false, built from R") and the annotated tag `release-v1.0`, all at T. The figure provenance names R; release-v1.0 differs from R only in documents, the figure map, the hash list and helper scripts for tagging and hash lists. The `fig-<ID>-v1` tags are superseded, stay local and are not pushed. The remote https://github.com/danielvoldman/mpr-gamma-surge (private) received `master`, the 13 v2 tags, `release-v1.0`, `criteria-frozen`, `env-v1`, `replication-pass` and `tolerances-frozen`, by name and never with `--tags`.

### Changed

- `README.md`: the MS0 skeleton is replaced by the setup block of the plan plus the claim limits, the failures shown in the figures, the environment, the numerical defaults, the figure rebuild, the tags, the licences, how to cite and the author lines.
- `CHANGELOG.md`: written without a byte-order mark and with LF line endings.

## Unreleased

### Added

- MS15a, part 3 (sub-step 21; `docs/decision_log.md` DL-747 and DL-748): `docs/ms15a_push_record.md` (the user's push output) and `scripts/ms15a_check_push_record.py` (compares it with the local tags: master and the 18 pushed tags are equal), `docs/ms15a_clean_machine_notes.md` (checklist 10.8, read-only), `scripts/ms15a_make_data_package.py` (builds and verifies the data package for a Zenodo record outside the repository), `tests/test_ms15a_release_state.py`. The 24 slow tests were run once and passed. `master` and 18 tags (13 `fig-<ID>-v2`, `release-v1.0`, `criteria-frozen`, `env-v1`, `replication-pass`, `tolerances-frozen`) are on the remote; the 13 `fig-<ID>-v1` tags are not.
- MS15a, part 4 (sub-step 22; `docs/decision_log.md` DL-751 to DL-753): `scripts\make_all.ps1 -Stage figures` passes `--release` to `scripts/fig_journal.py` (not run); the `--zips` mode of `scripts/ms15a_make_data_package.py` and `tests/test_ms15a_zip_package.py` (the data package as one deterministic zip per figure plus seven unzipped files, built outside the repository).

### Changed

- `README.md` and `CHANGELOG.md` (sub-step 25; `docs/decision_log.md` DL-755 and DL-756): lines that were stale after the tags and the push are corrected (the remote and the v2 tags exist, Julia is used by A5 and A6, the last full fast suite is the one of DL-754, the figure build time follows the 13 provenance records); this file is split into a section named by the tag `release-v1.0` and an Unreleased section.

### Known gaps

- Nothing archived; no version beyond the tag name and no DOI assigned. The older commits (689 on `master` before sub-step 20; the ruling of 2026-11-10 says 686, a difference of 3 not explained, UNVERIFIED) and the 16 older annotated tags keep the placeholder identity "Your Name <you@example.com>"; the commits and the three older annotated tags `env-v1`, `tolerances-frozen` and `criteria-frozen` are on the remote since the user's push (`docs/ms15a_push_record.md`), and so is the lightweight `replication-pass`; the 13 `fig-<ID>-v1` tags (13 of the 16 older annotated tags) are local only.
- The 13 journal provenance records say `draft = false` since the rebuild of MS15a 19; the eleven drafts stay `draft = true` (audit copies, by ruling); the meaning of "release commit" in plan section 10.8 item 6 is UNVERIFIED (`docs/ms15_draft_flag_notes.md`).
- Checklist 10.8 has not been run on a clean machine (a stand-in on the development PC is not a clean machine; `docs/ms15a_clean_machine_notes.md`); `mprsurge.run` has no `--from-record` option; the data package has not been uploaded. The package to upload is the one built from `scripts/ms15a_make_data_package.py --zips` (20 files, one zip per figure; within the unverified Zenodo limit of 100 files); the first package of 106 files is superseded.
- Manuscript and submission (MS15b) are outside the repository and not done.
