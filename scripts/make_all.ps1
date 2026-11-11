# scripts/make_all.ps1 -- pipeline driver (plan section 10.1, line 1065: "pipeline in milestone order").
#
# Written in sub-step 18 (MS15a, DL-736 C4 (g)). It has been checked ONLY for PowerShell syntax (read-only parse). It has NOT been run.
#
# USAGE (from any folder):   .\scripts\make_all.ps1 -Stage replication
#                            .\scripts\make_all.ps1 -Stage figures
#
# WHAT THE PLAN SAYS (docs/plan.md, quoted):
#   L1065  "make_all.ps1             pipeline in milestone order"
#   L1064  "check_clean_tree.py      blocks tagged builds from a dirty tree"
#   L1200  "Numba cache: make_all.ps1 clears the Numba cache files (*.nbi, *.nbc) before every tagged run and records this in provenance"
#   L1272  "Run scripts\make_all.ps1 -Stage replication; every G0 row passes."   (checklist 10.8, item 3)
#   Table 11.1 names the milestone steps (MS2: A1, A2, S1, A0 rows; MS5: A4, S3; MS13: the figures).
#
# WHAT IS FROM THE PLAN AND WHAT IS INFERRED (each step below is marked [plan] or [inferred]):
#   [plan]     the script name, the parameter -Stage with the value "replication", the clearing of *.nbi and *.nbc files,
#              the clean-tree check (L1064), the names of the steps (S1, A1, A2, A0, A4, S3 in Table 11.1; figures in MS13).
#   [inferred] which command runs a named step (taken from the docstrings of the existing drivers in scripts/), the order inside a stage,
#              applying the clean-tree check to every stage, the value "figures" of -Stage, and the exact set of steps of "replication".
#              UNVERIFIED: that this set is exactly "every G0 row"; the exit code of run_A4.py and run_S3.py may not encode the K7 to K11 verdicts.
#   NOT WRITTEN (the plan does not list the commands; nothing is invented): the steps of the other milestones (MS3, MS4, MS6 to MS12 and the
#              run lists scripts\run_ms8_list.py, run_ms9_list.py, run_ms10_list.py, run_ms11_list.py), the network cells of S3 (--network), the Julia
#              steps (A5, A6), and the recording of the cleared cache in provenance (provenance.py has the field numba_cache_cleared, but no
#              runner option sets it; that needs a change under src/ and is not made here). -Stage all therefore stops with an error.
#   The release tag, the figure tags and any push are NOT made by this script.
#
# Stops on the first error. Prints each step. No path outside the repository is used: the repository folder is the parent of this script's folder.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('replication', 'figures', 'all')]
    [string]$Stage
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot            # this script lives in <repo>\scripts
$Py = Join-Path $RepoRoot '.venv\Scripts\python.exe'    # plan L1147: calling .venv\Scripts\python.exe directly avoids activation
$script:StepNo = 0

function Invoke-Step {
    param([string]$Name, [string]$Origin, [scriptblock]$Action)
    $script:StepNo++
    Write-Host ("== step {0}: {1}  [{2}]" -f $script:StepNo, $Name, $Origin)
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw ("step {0} ({1}) failed with exit code {2}; stopping" -f $script:StepNo, $Name, $LASTEXITCODE)
    }
}

function Clear-NumbaCache {
    # plan L1200: clear the *.nbi and *.nbc files before a tagged run (numba writes them next to the source, in __pycache__ folders)
    $files = @(Get-ChildItem -Path (Join-Path $RepoRoot 'src') -Recurse -File -Include '*.nbi', '*.nbc' -ErrorAction SilentlyContinue)
    foreach ($f in $files) { Remove-Item -LiteralPath $f.FullName -Force }
    Write-Host ("   numba cache files removed: {0}" -f $files.Count)
    $global:LASTEXITCODE = 0
}

if (-not (Test-Path -LiteralPath $Py)) { throw "interpreter not found: $Py (create the environment as in README.md)" }
Push-Location $RepoRoot
try {
    if ($Stage -eq 'all') {
        throw "-Stage all is not written: the plan names no commands for the milestones other than replication and the figures (see the header of this script)"
    }

    Invoke-Step 'clean tree check (scripts\check_clean_tree.py)' 'plan L1064; applied here: inferred' { & $Py 'scripts\check_clean_tree.py' }
    Invoke-Step 'clear the numba cache (*.nbi, *.nbc)' 'plan L1200' { Clear-NumbaCache }

    if ($Stage -eq 'replication') {
        # MS2 (Table 11.1: "A1, A2, S1 (K1-K3, K4-MF, K5)")
        Invoke-Step 'S1 through the runner (configs\S1.yaml)' 'step name: plan; command: inferred from the docstring of scripts\run_A2.py' { & $Py -m mprsurge.run --config 'configs\S1.yaml' }
        Invoke-Step 'A1 (scripts\run_A1.py)' 'step name: plan; command: inferred' { & $Py 'scripts\run_A1.py' }
        Invoke-Step 'A2 (scripts\run_A2.py)' 'step name: plan; command: inferred' { & $Py 'scripts\run_A2.py' }
        # MS5 (Table 11.1: "A4, S3 (K7-K11)"); mean-field cells only: the network cells (run_S3.py --network) are not sourced and not run
        Invoke-Step 'A4 (scripts\run_A4.py)' 'step name: plan; command: inferred' { & $Py 'scripts\run_A4.py' }
        Invoke-Step 'S3 mean-field cells (scripts\run_S3.py)' 'step name: plan; command: inferred; network cells not included' { & $Py 'scripts\run_S3.py' }
        # the G0 table: plan L1272 "every G0 row passes"; run_A0.py exits 1 if any row fails (its docstring)
        Invoke-Step 'A0 replication table (scripts\run_A0.py)' 'plan L1272 (every G0 row passes); command: inferred' { & $Py 'scripts\run_A0.py' }
    }
    elseif ($Stage -eq 'figures') {
        # MS13 (Table 11.1: "Figures F1-FS6 with provenance"); the journal export of the 13 figures, from results\ only (no simulation)
        # NOTE: --release is a release build (provenance draft = false): the figures stage must be run on a clean tree; see docs\ms15_draft_flag_notes.md.
        Invoke-Step 'journal figures (scripts\fig_journal.py, 13 IDs)' 'step name: plan (MS13); stage value and command: inferred' {
            & $Py 'scripts\fig_journal.py' '--release' 'F1' 'F2' 'F3' 'F4a' 'F4b' 'F5' 'F5c' 'F6' 'FS1' 'FS2' 'FS3' 'FS4' 'FS5'
        }
    }
    Write-Host ("== stage {0} finished: {1} steps, no error" -f $Stage, $script:StepNo)
}
finally {
    Pop-Location
}
