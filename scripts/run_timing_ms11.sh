#!/bin/bash
# MS11 11a timing-gate samples (DL-334), the MS8 8a method (run_timing_ms8.sh): each sample cell of configs/timing/ms11/ as 10 concurrent copies x 1 batch
# (per-run median pooled over the copies, DL-102), the network dt 1e-4 cell also alone (the longest single run is judged alone, DL-103). Run from the
# repository root on a clean git tree; writes only results/timing/ms11/ (git-ignored). TIMING SAMPLES ONLY: not a result run, in no pre-registered run list,
# nothing is classified and no result-family record is written. Radau at T_ramp 316 s is NOT sampled (it would run for over an hour): the 120 s rate of DL-178 is used.
# Total python working set polled every 0.5 s per cell into logs/mem_<cell>.csv (a lower bound on the true peak, UNVERIFIED, as DL-142).
cd "$(dirname "$0")/.." || exit 1
P=.venv/Scripts/python.exe
D=results/timing/ms11
mkdir -p $D/logs
git status --porcelain > $D/logs/git_status_before.txt
git rev-parse HEAD > $D/logs/git_head.txt
$P -m pip freeze > $D/logs/pip_freeze.txt 2>&1
powershell -NoProfile -Command "Get-CimInstance Win32_PerfFormattedData_PerfProc_Process | Where-Object { \$_.Name -ne '_Total' -and \$_.Name -ne 'Idle' } | Sort-Object PercentProcessorTime -Descending | Select-Object -First 15 Name,IDProcess,PercentProcessorTime,WorkingSet | Format-Table -AutoSize | Out-String -Width 200" > $D/logs/machine_state_before.txt 2>&1
powercfg /getactivescheme >> $D/logs/machine_state_before.txt 2>&1
for cell in ms11_s11_t10 ms11_s11_t30 ms11_s11_t120_sf0p5 ms11_s11_t120_sf2 ms11_s11_t300 ms11_floorc_l2_dt1e-3_t316 ms11_floorc_l2_dt1e-4_t316 \
            ms11_dop_1e-10_t316 ms11_dop_1e-12_t316 ms11_net_vp200 ms11_net_dt5e-4 ms11_net_dt2p5e-4 ms11_net_dt1e-4 ms11_net_vp200_dt1e-4; do
  extra=""
  case $cell in ms11_floorc*|ms11_s11_*) extra="--set seeds.spawn_key=[0]";; esac
  rm -f $D/logs/stop_$cell
  powershell -NoProfile -Command "\$mx=0; while(-not (Test-Path '$D/logs/stop_$cell')){ \$s=(Get-Process python -ErrorAction SilentlyContinue | Measure-Object WorkingSet64 -Sum).Sum; if(\$s -gt \$mx){\$mx=\$s}; Set-Content -Path '$D/logs/mem_$cell.csv' -Value \$mx; Start-Sleep -Milliseconds 500 }" &
  $P scripts/time_one_run.py --cell $cell --workers 10 --repeat 1 --limit-s 3600 --out-dir $D/$cell $extra > $D/logs/w10_$cell.log 2>&1
  touch $D/logs/stop_$cell
  wait
done
$P scripts/time_one_run.py --cell ms11_net_dt1e-4 --repeat 1 --limit-s 3600 --out-dir $D > $D/logs/alone_ms11_net_dt1e-4.log 2>&1
$P -m mprsurge.analysis.ms11_counts --out $D/prediction_11a.txt > $D/logs/prediction.log 2>&1
echo done > $D/logs/ALL_DONE_11A
