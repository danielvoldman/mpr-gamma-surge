#!/bin/bash
# MS9 9a timing-gate sample (DL-210), the MS8 8a method (run_timing_ms8.sh): each cell as 10 concurrent copies x 1 batch, per-run medians.
# Cells: map 1 at Delta 0.01 and Delta 0.6 (configs/timing/delta_0.01.yaml, delta_0.6.yaml, tau_d 5 ms), one map-2 cell, one P3 run, one
# noisy-subgrid seed run (mode N, 120 s), one S16 run, one NC1 mean-field run and one NC1 network run (N = 1e4, 120 s). Run from the
# repository root on a clean git tree. Writes only results/timing/ms9/ (git-ignored). Not a result run: nothing is classified, no run
# record of a result family is written. Peak total working set of all python processes is polled every 0.5 s into logs/mem_<cell>.csv
# (a lower bound on the true peak, UNVERIFIED, as DL-142).
cd "$(dirname "$0")/.." || exit 1
P=.venv/Scripts/python.exe
D=results/timing/ms9
mkdir -p $D/logs
git status --porcelain > $D/logs/git_status_before.txt
git rev-parse HEAD > $D/logs/git_head.txt
$P -m pip freeze > $D/logs/pip_freeze.txt 2>&1
powershell -NoProfile -Command "Get-CimInstance Win32_PerfFormattedData_PerfProc_Process | Where-Object { \$_.Name -ne '_Total' -and \$_.Name -ne 'Idle' } | Sort-Object PercentProcessorTime -Descending | Select-Object -First 15 Name,IDProcess,PercentProcessorTime,WorkingSet | Format-Table -AutoSize | Out-String -Width 200" > $D/logs/machine_state_before.txt 2>&1
powercfg /getactivescheme >> $D/logs/machine_state_before.txt 2>&1
for cell in delta_0.01 delta_0.6 ms9_map2_j-40_t316 ms9_p3_t120 ms9_noisy_t120 ms9_s16_jt1p1 ms9_nc1_t120 ms9_nc1_net_t120; do
  extra=""
  [ "$cell" = "ms9_noisy_t120" ] && extra="--set seeds.spawn_key=[0]"
  rm -f $D/logs/stop_$cell
  powershell -NoProfile -Command "\$mx=0; while(-not (Test-Path '$D/logs/stop_$cell')){ \$s=(Get-Process python -ErrorAction SilentlyContinue | Measure-Object WorkingSet64 -Sum).Sum; if(\$s -gt \$mx){\$mx=\$s}; Set-Content -Path '$D/logs/mem_$cell.csv' -Value \$mx; Start-Sleep -Milliseconds 500 }" &
  $P scripts/time_one_run.py --cell $cell --workers 10 --repeat 1 --limit-s 3600 --out-dir $D/$cell $extra > $D/logs/w10_$cell.log 2>&1
  touch $D/logs/stop_$cell
  wait
done
echo done > $D/logs/ALL_DONE_9A
