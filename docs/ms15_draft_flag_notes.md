# The DRAFT flag of the figure provenance records (MS15a, sub-step 18, DL-736 C5; read-only finding)

Written for: the user (owner), who decides part 2 of MS15a. Nothing was edited, rebuilt or tagged to write this: no provenance record, no figure, no flag logic, no tag. Every statement about what a change would do is an inference from reading the code and is marked UNVERIFIED (no build was run). The plan (`docs/plan.md`) is read-only.

## 1. What the plan says (word for word, with plan line numbers)

> L1284: 1.  Every provenance file names the release commit and none is marked DRAFT.
>
> L1236: **Tags.** All annotated:
>
> L1246: - fig-\<ID\>-v\<k\>, for each figure build (inputs and hashes in the message);
>
> L1248: - release-v1.0.
>
> L1182: - the git commit, branch, tags and a dirty flag;
>
> L1200: - Numba cache: make_all.ps1 clears the Numba cache files (\*.nbi, \*.nbc) before every tagged run and records this in provenance; ...

The plan has no other sentence with the word DRAFT (searched: line 1284 is the only hit). It does not define "DRAFT", "release commit" or "provenance file". The repository's own rule is in `docs/ms13_conventions.md` line 56: "A build without `--tag` may run on a dirty tree and is marked `draft`; a tagged build refuses a dirty tree."

## 2. What sets `draft` (read from the code)

- `src/mprsurge/plotting/figprov.py` line 177 (in `write_figure_provenance`): `"draft": dirty or not tag_build`. So `draft` is false only if the build was called with `tag_build=True` AND the git tree was clean (`dirty_lines(root)` empty). With `tag_build=True` and a dirty tree the build stops (`DirtyTreeError`, `figprov.py` lines 169 to 170).
- The draft scripts `scripts/fig_F1.py` to `scripts/fig_FS5.py` have a `--tag` option (`ap.add_argument("--tag", ...)`; they run the clean-tree check first and pass `tag_build=a.tag`). Without `--tag` the build is an untagged DRAFT.
- `scripts/fig_journal.py` (the script that built the 13 journal figures) has NO `--tag` option and calls `figures.make_<ID>(mode="journal", root=root)`; `tag_build` keeps its default `False`. Its docstring says: "The build is an untagged DRAFT (provenance draft = true). No tag is created". So on this code a journal build is a DRAFT even on a clean tree. This is why all 13 journal records say `draft = true` although `git.dirty = false` (read from the 13 records: draft true, dirty false, tags [], status ok, build commit 5e90575 or, for FS1, f5d3f0d).
- The journal builders do carry `tag_build` into `write_figure_provenance` (`prov_kw` contains `tag_build=tag_build` in `make_F3`, `make_F1`, ...; `jf4.build`, `jfs2.build` to `jfs5.build` take a `tag_build` argument), so the machinery exists; only the call in `fig_journal.py` does not use it (reading; UNVERIFIED because not run).
- No condition on a tag, a config option or a release marker clears the flag. `git.tags` (tags pointing at HEAD at build time, `provenance.git_info`) is recorded but is not read by the flag.
- The 11 draft figures (`figures/F1` to `figures/FS5`) say `draft = true` too (commit 4e68752, dirty false); they were built without `--tag`.

## 3. What else in the record or the files is tied to it

- In the provenance record: `git.commit` (HEAD at build), `git.branch`, `git.tags`, `git.dirty`, `build`, `status`, `numba_cache_cleared` (always `null` in the figure records: nothing sets it; the plan's L1200 says make_all.ps1 records it), `created_utc`, `wall_time_s`, and the SHA-256 of the script, modules, configs, inputs and outputs.
- In the journal supplement (`figures/journal/supplement/<ID>_supplement.md`): `figures.py` line 854 writes the sentence "Journal export of <ID> (draft = {true|false}, untagged), commit <hash>, git dirty = ..." (the word "untagged" is a fixed string, not read from the flag), and the Nordlie table of the supplement carries "provenance file SHA-256" (`nordlie.py` line 99). DL-714 W1 found exactly these two lines differing when FS5 was rebuilt at another commit: "commit 5e9057563c6c24fbac16b99000e547d08ef9a31a" against "commit af5193d32d788f0d72b1dfff40f3383283e56d47", and the provenance-file hash (c0105081... against 30dc19ef...); with those two values masked the two supplements were byte-equal, and the PNG, TIFF, PDF, caption, alt text and source data were equal.
- The journal images carry no DRAFT mark (the journal export has no footer); the draft images (figures/F1 and so on) do carry the "DRAFT" footer, which disappears with `--tag` (`_style_text(fig, FOOTER if draft else "")`), so a tagged rebuild of the drafts changes their pixels and their hashes (inference; UNVERIFIED).
- Documents that hold the journal hashes: `docs/ms13_journal_final_hashes.txt` (8 files per figure, the build commit, the drawn-data digest), the 13 tag messages of `fig-<ID>-v1` (100 file and hash lines in all), `docs/figure_map.md` (generated), the decision log, and tests that read the hash list. `docs/ms13_figure_manifest.csv` and `scripts/ms13_check_hashes.py` concern the eleven drafts.
- Run records (`results/<ID>/*.json`, 32,070 files) have no `draft` key; they name their own commits and some say `dirty = true` (for example the A4 dry record, commit f92a691). They cannot name one release commit.

## 4. What clearing the flag costs (all inferences; UNVERIFIED; nothing was run)

1. A change of code, not only a clean tree: `scripts/fig_journal.py` needs a `--tag` option that runs the clean-tree check and passes `tag_build=True`; the fixed word "untagged" in the supplement sentence would then be wrong and has to follow the flag (`figures.py` line 854). Existing tests assert draft behaviour (`tests/test_fig_F1.py` to `tests/test_fig_FS5.py` contain the word draft; what each asserts was not read in detail); they would have to be read, and a change under `scripts/` or `src/` brings the full fast suite and an entry in the decision log.
2. Editing the 13 provenance records by hand is not honest and not possible without breaking the chain: the records hold output hashes, and the supplement embeds the record's hash; CLAUDE.md also says `results/` and `figures/` are never edited by hand. A rebuild at the release commit is the only way to get a record that names that commit and says `draft = false` (reading).
3. A rebuild from one clean commit changes: the 13 provenance records (flag, commit, script and module hashes, times); the 13 supplements (commit line, "draft = false" text, provenance hash); therefore the 13 supplement hashes in `docs/ms13_journal_final_hashes.txt`, in `docs/figure_map.md` and in new tag messages. Expected unchanged (equal drawn-data digests; PNG, TIFF, PDF, captions, alt texts, source data): shown only for FS5 (DL-714); for the other 12 not tested (UNVERIFIED). The EPS extras differ between any two builds (close item 55) and are not in the hash list.
4. The 13 `fig-<ID>-v1` tags cannot describe the new files (a tag message is fixed at creation; the supplement hashes change). The plan names `fig-<ID>-v<k>`: new tags `fig-<ID>-v2`; the v1 tags stay (nothing is moved or deleted). The v1 tags carry the tagger "Your Name <you@example.com>"; v2 tags would carry the configured identity.
5. Cost in time: the 13 builds took 85.4 s in all in the recorded build (figure build only); the checks (verifier, independent comparison, hash check, tests) are the larger part; the fast suite took 1405.18 s (DL-726).
6. An ordering problem (reading; UNVERIFIED): `figures/` is git-ignored, so a provenance record is not in any commit; it can name the commit it was built at. But the new hash list is a committed document, so a commit that comes after the build must hold it; the commit the record names is then one commit before the commit that holds the hash list and that the `fig-<ID>-v2` tags would point to (the same pattern as v1: build commit 5e90575, tag commit e6666cb). Whether "the release commit" of item 6 means the build commit, the tagged commit, or `release-v1.0` is not defined in the plan.
7. "Every provenance file" is ambiguous: it could mean the 13 journal records only, or also the 11 draft records (draft = true, commit 4e68752), or all run records. The drafts are audit copies; rebuilding them with `--tag` would change their DRAFT-footer pixels and break their equality with `docs/ms13_figure_manifest.csv`.

## 5. Options and a proposed part 2 (for the user to rule; none is started)

Options for checklist item 6, no recommendation on the science:

- A. Accept as built. The release notes say that the 13 journal records say `draft = true` and name the build commit 5e90575 (FS1 f5d3f0d); item 6 is then NOT met, a departure from the plan by user ruling. Cost: none; nothing changes; the v1 tags stay the figure tags.
- B. Rebuild the 13 journal figures from one clean release commit (the proposal below). Cost: items 1 to 6 of section 4.
- C. Mixed: B for the 13 journal figures; the 11 drafts are declared audit copies outside the release (stated in the release notes), so they stay `draft = true`.

Proposed part 2 if B or C is ruled (UNVERIFIED order; each step committed before the next; the full fast suite before every commit that touches `scripts/` or `src/`):

1. Rulings: A, B or C; what "release commit" means (the build commit that gets `release-v1.0`, or the later documents commit); `fig-<ID>-v2` naming; the GitHub address and public or private (needed for the remote and for any push); whether the slow tests run before the release tag (close item 76).
2. Log the rulings first. Then a small code change: `--tag` in `scripts/fig_journal.py` and the supplement sentence following the flag; tests updated only as ruled; full fast suite.
3. Finish every other release file and document (README, CHANGELOG, figure_map, close documents) and commit them, so that the release commit is the last commit that changes the code or the configs. Clean tree.
4. Build the 13 journal figures with `--tag` from that commit (about 85 s); compare each PNG, TIFF, PDF, caption, alt text and source-data hash with `docs/ms13_journal_final_hashes.txt` and report every difference; a difference in a file other than the supplement is a STOP (rule 12 of `docs/ms13_figure_rules.md`).
5. Re-run `scripts/ms13_verify_export.py` and `scripts/ms13_independent_compare.py`; write the new hash list (`scripts/ms13_write_final_hashes.py`) and regenerate `docs/figure_map.md`; commit.
6. With the user's word "tag": create `fig-<ID>-v2` for the 13 figures (`scripts/ms13_make_tags.py` has a constant `VERSION` and `tag_name(fid, version)` but no command-line option for the version, and its docstring says v1: whether v2 needs a code change is UNVERIFIED, to be read) and `release-v1.0`; nothing is moved or deleted; no push until the user gives the remote.
7. Then the clean-machine run of checklist 10.8 (the user) and the archive deposit (the user's Zenodo account).
