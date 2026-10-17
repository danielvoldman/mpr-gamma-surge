#!/bin/bash
# MS8 8a timing-gate sample (DL-167): the ten MS8 sample cells (configs/timing/ms8/), each as 10 concurrent copies x 1 batch,
# then the size probe, then the prediction. Run from the repository root on a clean git tree. Writes only results/timing/ms8/
# (git-ignored). Not an S5 or S13 result run: nothing is classified, no run record of a result family is written.
# Peak total working set of all python processes is polled every 0.5 s by a PowerShell loop into logs/mem_<cell>.csv (a lower
# bound on the true peak, UNVERIFIED, as DL-142).
cd "$(dirname "$0")/.." || exit 1
P=.venv/Scripts/python.exe
D=results/timing/ms8
mkdir -p $D/logs
git status --porcelain > $D/logs/git_status_before.txt
git rev-parse HEAD > $D/logs/git_head.txt
powershell -NoProfile -Command "Get-CimInstance Win32_PerfFormattedData_PerfProc_Process | Where-Object { \$_.Name -ne '_Total' -and \$_.Name -ne 'Idle' } | Sort-Object PercentProcessorTime -Descending | Select-Object -First 15 Name,IDProcess,PercentProcessorTime,WorkingSet | Format-Table -AutoSize | Out-String -Width 200" > $D/logs/machine_state_before.txt 2>&1
powercfg /getactivescheme >> $D/logs/machine_state_before.txt 2>&1
for cell in ms8_floor_dt1e-4 ms8_dop_1e-8_t10 ms8_dop_1e-10_t10 ms8_dop_1e-12_t10 ms8_p1_lin_t56 ms8_p1_sig_t56 ms8_p2_lin_t56 ms8_p2_sig_t56 ms8_p5_lin_t56 ms8_p5_sig_t56; do
  extra=""
  [ "$cell" = "ms8_floor_dt1e-4" ] && extra="--set seeds.spawn_key=[0]"
  rm -f $D/logs/stop_$cell
  powershell -NoProfile -Command "\$mx=0; while(-not (Test-Path '$D/logs/stop_$cell')){ \$s=(Get-Process python -ErrorAction SilentlyContinue | Measure-Object WorkingSet64 -Sum).Sum; if(\$s -gt \$mx){\$mx=\$s}; Set-Content -Path '$D/logs/mem_$cell.csv' -Value \$mx; Start-Sleep -Milliseconds 500 }" &
  $P scripts/time_one_run.py --cell $cell --workers 10 --repeat 1 --limit-s 3600 --out-dir $D/$cell $extra > $D/logs/w10_$cell.log 2>&1
  touch $D/logs/stop_$cell
  wait
done
$P scripts/probe_ms8_size.py > $D/logs/size_probe.log 2>&1
echo done > $D/logs/ALL_DONE_8A
