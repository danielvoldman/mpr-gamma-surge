# MS11 launch instructions (11d, DL-374; written before any MS11 run; nothing is launched by Claude Code)

Written for: the reviewer, who launches every MS11 list in PowerShell. Nothing here has been run: no list, no evaluator on a real record, no hook on a real record. Predictions are from the 11a timing samples (DL-334, 10 concurrent copies, per-run median) and, for MS11_RB9D, from the headline timing cell; the five lists are frozen (hashes in `configs/ms11/ms11_list_hashes.yaml`, DL-370).

## 1. Lists, hashes, predicted time

| Order | List | Runs | Workers | Predicted wall | What fixes the time | Raw disk estimate | List SHA-256 |
|---|---|---|---|---|---|---|---|
| 1 | MS11_S11 | 120 | 10 | 31.5 s (sum 315 s, longest 6.4 s) | sum / 10 | 1,235 MB | 51e74769...672d |
| 2 | MS11_CTRL | 30 | 10 | 8.2 s (sum 82 s, longest 2.7 s) | sum / 10 | 321 MB | c9cedaac...9537 |
| 3 | MS11_RB9D | 2 | 2 | 223 s = 3.7 min (tau 8 ms, 20,625 tau; the tau 12 ms run 149 s) | the longer run | 21 MB | 4ed2bb07...ada0 |
| 4 | MS11_S13_MF | 68 | 10 | 604 s = 10.1 min | the longest run (rtol 1e-12 at 316.2278 s) | 960 MB | b7be5147...320a |
| 5 | MS11_S13_NET | 18 | 10 | 691 s = 11.5 min | the longest run (dt 1e-4, V_p 200; 5.7 min alone) | 34 MB | 9bc9283c...702f |

Sequential total about 26 min (S11 and CTRL together 40 s). Launch rule 9.2: S11 plus controls 40 s against 1.5 x 40 min (0.02 x); S13 as a whole (MS8 recorded 26.3 min plus the MS11 remainder 14.2 min) 40.6 min = 0.68 x the 1 h row. No run is predicted to run over one hour (the Radau run at 316.2278 s was cut, DL-337); any run found over one hour is flagged and launched by the reviewer, never by Claude Code. The raw disk estimates are the launcher's refusal rule (8 float64 arrays at 1 kHz, uncompressed, for the simulated time of each run); for network records the MS10 estimate (0.24 GB) was below the 450.9 MB actually written (a factor of about 1.9, UNVERIFIED sizes), so the 34 MB network figure here is probably low; it is small against the free space either way.

MS11_RB9D is the post hoc list of RB9(d) (Reading A, DL-367): two mean-field runs at tau 8 and 12 ms, deterministic, no seed key; reported only. Two workers are enough (one run each); `--workers 10` is also accepted and changes nothing.

## 2. Recommended order, and why

Smallest first, so a pipeline problem shows up in seconds and not after the long lists: MS11_S11 (and MS11_CTRL), MS11_RB9D, MS11_S13_MF, MS11_S13_NET. The lists are independent (each its own journal directory); a killed launch is resumed by running the same command again (complete runs are skipped). Look at `manifest.csv` and `run.log` of each launch (last line "finished: n ok") before starting the next.

## 3. Commands (PowerShell, from the repository root)

Dry runs first (list only: run count, list SHA-256 against the frozen one, disk estimate and the refusal reasons a real launch would meet; nothing is simulated or written):

```powershell
.venv\Scripts\python.exe scripts/run_ms11_list.py --list MS11_S11 --dry-run
.venv\Scripts\python.exe scripts/run_ms11_list.py --list MS11_CTRL --dry-run
.venv\Scripts\python.exe scripts/run_ms11_list.py --list MS11_RB9D --dry-run
.venv\Scripts\python.exe scripts/run_ms11_list.py --list MS11_S13_MF --dry-run
.venv\Scripts\python.exe scripts/run_ms11_list.py --list MS11_S13_NET --dry-run
```

Launches:

```powershell
.venv\Scripts\python.exe scripts/run_ms11_list.py --list MS11_S11 --workers 10 --journal-dir results/ms11/launch_s11
.venv\Scripts\python.exe scripts/run_ms11_list.py --list MS11_CTRL --workers 10 --journal-dir results/ms11/launch_ctrl
.venv\Scripts\python.exe scripts/run_ms11_list.py --list MS11_RB9D --workers 2 --journal-dir results/ms11/launch_rb9d
.venv\Scripts\python.exe scripts/run_ms11_list.py --list MS11_S13_MF --workers 10 --journal-dir results/ms11/launch_s13_mf
.venv\Scripts\python.exe scripts/run_ms11_list.py --list MS11_S13_NET --workers 10 --journal-dir results/ms11/launch_s13_net
```

(S11 and CTRL may also go in one pool, `--list MS11_S11 --list MS11_CTRL --journal-dir results/ms11/launch_s11_ctrl`, about 40 s; the per-list form above is the one the predictions are for.) Use the venv python as written: plain `python` resolves to 3.12.

## 4. Free disk now

Measured at the time of writing this file: **71.0 GB free** on the drive of the repository (MS10 close, R33: 153 GB; 10e log: 81.4 GB; the 11d pre-check `df` showed 67 GiB = 71 GB, the same figure; so free space is about 82 GB lower than at the MS10 close, cause not recorded, UNVERIFIED). The five lists need at most 2.57 GB raw (below); the launcher refuses a real launch if the free space is below the estimate of the lists it is given. Measure again immediately before each launch; free space has changed between sessions without a record of why.

## 5. Pre-launch reminders

1. `git status` must be clean and HEAD must be the commit that holds the frozen lists (11d commit or a descendant): every record stores the git dirty flag and the evaluators refuse a record whose flag is not exactly false. Commit nothing and edit no file while a launch runs.
2. Run the `--dry-run` of the list you are about to launch and read the last lines: "a real launch would be ALLOWED". Any REFUSED reason stops the launch; do not work around it.
3. No pytest, no other heavy job, and no timing run during a launch (10 workers use all the cores; the timing samples assume 10 concurrent copies of the run alone). Keep the machine awake (power plan: no sleep) for the length of the launch.
4. Network runs go through this launcher only; the memory peak seen in the 11a timing was 2.78 GB over all python processes (a lower bound, UNVERIFIED).
5. One journal directory per launch; do not reuse a journal directory for another list. A restart uses the same command and the same journal directory.
6. Do not evaluate and do not run `scripts/run_A11.py` on the results until the reviewer says so: the A11 evaluation step (with the recompute hooks of the 26 carried checks) is a separate step, and the first thing it does is the record check (clean, listed, hash, name, criteria SHA-256) of every record.
7. The results folders are git-ignored outputs; never edit results/ or figures/ by hand.
8. Report back for each list: the last line of `run.log`, the count of ok/failed/timeout in `manifest.csv`, the wall time against the prediction above, and the free disk after the launch. A failed or timed-out run is reported, never rerun silently, and never replaced.
9. If any single run is still going after one hour, stop and tell the reviewer; the plan's rule is that such a run is launched by the reviewer in PowerShell (none is predicted).
