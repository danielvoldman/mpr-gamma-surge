# Changelog

The plan (docs/plan.md, line 1023) asks for one entry per release tag. No release tag exists yet, so everything below is "Unreleased". No date and no version is given for it because none exists.

## Unreleased

### Added

- MS13 figures: the 13 journal figures F1, F2, F3, F4a, F4b, F5, F5c, F6, FS1, FS2, FS3, FS4 and FS5 (PNG and TIFF at 600 dpi, PDF, captions, alt text, supplement sheets, source data, provenance records), built from stored results; the eleven drafts are audit copies. The files are git-ignored; their SHA-256 hashes are in `docs/ms13_journal_final_hashes.txt` and `docs/figure_map.md`. FS6 is not produced (user ruling of 2026-11-09, `docs/ms13_close.md`).
- 13 annotated local tags `fig-<ID>-v1` for the 13 journal figures (all at commit e6666cb2e8120a1619527c5ee7fce01e1beedb55; tag messages hold the file hashes). Not pushed.
- MS14: `docs/search_log.md` with the plan's Table E.1 and items 1 to 7 recorded as "Not done natively on Nov 10; general web-search pre-check only". MS14 was closed by user ruling as a departure from the plan; its limits are in `docs/ms13_close.md` section (7).
- MS15a, part 1 (the release files; user rulings of 2026-11-10 in `docs/ms15_scope_notes.md`): `LICENSE` (MIT), `LICENSE-DATA.md` (CC-BY 4.0 notice; the legal text is still to be added), `CITATION.cff`, `.zenodo.json`, `scripts/make_all.ps1` (written and not run), `docs/figure_map.md`, `scripts/ms15a_write_figure_map.py`, `docs/ms15_draft_flag_notes.md`, `tests/test_ms15a_release.py`, a full `README.md`.

### Changed

- `README.md`: the MS0 skeleton is replaced by the setup block of the plan plus the claim limits, the failures shown in the figures, the environment, the numerical defaults, the figure rebuild, the tags, the licences, how to cite and the author lines.
- `CHANGELOG.md`: written without a byte-order mark and with LF line endings.

### Known gaps

- No `release-v1.0` tag; nothing archived; no version, DOI or remote assigned.
- The 13 journal provenance records say `draft = true` (plan section 10.8 item 6); see `docs/ms15_draft_flag_notes.md`.
- Checklist 10.8 has not been run on a clean machine; the 24 slow tests are not recorded as run at the current commit; `mprsurge.run` has no `--from-record` option.
- Manuscript and submission (MS15b) are outside the repository and not done.
