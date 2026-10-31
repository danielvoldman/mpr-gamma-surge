# MS13 13t progress (survives a context compaction)

If the context is compacted or restarted: read `docs/ms13_figure_rules.md`, this file, `docs/ms13_export_checklist.json`, `git log --oneline` and the last 8 decision-log entries, then continue.

Numbering (DL-544): the journal export is 13t (two parts: 13t-1 design, shared code, collision checks and the F1, F3, F5 pilot; 13t-2 the other eight); tags are 13u (only when the user says "tag"); the evidence sheet, full suite and MS13 close document are 13v.

| sub-step | what was done | commit | next |
|---|---|---|---|
| 13t-1 step 1 | pre-checks passed (see DL-544); fast suite at the start 1192 passed, 24 deselected, 9 xfailed, exit 0; rulings logged (DL-544, DL-545); rules file, checklist and this file written | the commit that adds them | step 2: config, journal mode, scripts, checker, verifier |
