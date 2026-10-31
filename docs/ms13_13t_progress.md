# MS13 13t progress (survives a context compaction)

If the context is compacted or restarted: read `docs/ms13_figure_rules.md`, this file, `docs/ms13_export_checklist.json`, `git log --oneline` and the last 8 decision-log entries, then continue.

Numbering (DL-544): the journal export is 13t (two parts: 13t-1 design, shared code, collision checks and the F1, F3, F5 pilot; 13t-2 the other eight); tags are 13u (only when the user says "tag"); the evidence sheet, full suite and MS13 close document are 13v.

| sub-step | what was done | commit | next |
|---|---|---|---|
| 13t-1 step 1 | pre-checks passed (see DL-544); fast suite at the start 1192 passed, 24 deselected, 9 xfailed, exit 0; rulings logged (DL-544, DL-545); rules file, checklist and this file written | the commit that adds them | step 2: config, journal mode, scripts, checker, verifier |
| 13t-1 step 2 | config, journal.py, collide.py, jchecks.py, figures.py journal mode (F1, F3, F5), style.py constants, captions.py journal_extras, fig_journal.py, ms13_verify_export.py, tests/test_ms13_13t.py (45 tests); DL-547 | bfd2ad7 | looks at the PNGs |
| 13t-1 steps 5 to 7 | PNG looks and corrections (DL-548, DL-549), builds from clean commits, independent comparison 500/458/0/0/42 | b7fd19f, 424cfcd | independent review |
| 13t-1 step 8 | independent subagent review triaged (DL-550); last layout fix (F5 right margin); recorded build from d481588, verify exit 0; manifest rows of figures.py and style.py rewritten (DL-551); fast suite | d481588 | the user looks at the pilot; then 13t-2 (F2, F4, F6, FS1 to FS5); no tag |

Open for the reviewer (DL-547 (5), DL-550): the allow-list entries; the F1 strip membership (RB6 solver row); whether F5 (a) and (g) carry FAIL in the title; CVD simulation (no installed package; the hand-written matrices in style.py are not used); the manifest rows rewritten in DL-551.
