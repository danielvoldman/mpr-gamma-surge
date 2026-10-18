#!/bin/bash
# MS8 8d re-time (DL-177), the 8a method (run_timing_ms8.sh): each cell as 10 concurrent copies, one batch per cell (Radau: 3 batches).
# Cells: the coupled D43 floor group (four Heun rungs, level l = 2), the finest rung at l = 0, Radau rtol 1e-10 at T_ramp 10 s,
# the noise-free DOP853 run at 120 s. Run from the repository root on a clean tree. Writes only results/timing/ms8d/ (git-ignored).
cd "$(dirname "$0")/.." || exit 1
P=.venv/Scripts/python.exe
D=results/timing/ms8d
mkdir -p $D/logs
git status --porcelain > $D/logs/git_status_before.txt
git rev-parse HEAD > $D/logs/git_head.txt
powershell -NoProfile -Command "Get-CimInstance Win32_PerfFormattedData_PerfProc_Process | Where-Object { \$_.Name -ne '_Total' -and \$_.Name -ne 'Idle' } | Sort-Object PercentProcessorTime -Descending | Select-Object -First 15 Name,IDProcess,PercentProcessorTime,WorkingSet | Format-Table -AutoSize | Out-String -Width 200" > $D/logs/machine_state_before.txt 2>&1
powercfg /getactivescheme >> $D/logs/machine_state_before.txt 2>&1
for spec in ms8_floorc_l2_dt1e-3:1 ms8_floorc_l2_dt5e-4:1 ms8_floorc_l2_dt2.5e-4:1 ms8_floorc_l2_dt1e-4:1 ms8_floorc_l0_dt1e-4:1 ms8_dop_1e-10_t120:1 ms8_radau_1e-10_t10:3; do
  cell=${spec%%:*}; rep=${spec##*:}
  extra=""
  case $cell in ms8_floorc*) extra="--set seeds.spawn_key=[0]";; esac
  rm -f $D/logs/stop_$cell
  powershell -NoProfile -Command "\$mx=0; while(-not (Test-Path '$D/logs/stop_$cell')){ \$s=(Get-Process python -ErrorAction SilentlyContinue | Measure-Object WorkingSet64 -Sum).Sum; if(\$s -gt \$mx){\$mx=\$s}; Set-Content -Path '$D/logs/mem_$cell.csv' -Value \$mx; Start-Sleep -Milliseconds 500 }" &
  $P scripts/time_one_run.py --cell $cell --workers 10 --repeat $rep --limit-s 3600 --out-dir $D/$cell $extra > $D/logs/w10_$cell.log 2>&1
  touch $D/logs/stop_$cell
  wait
done
echo done > $D/logs/ALL_DONE_8D
