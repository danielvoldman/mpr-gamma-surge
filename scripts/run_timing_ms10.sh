#!/bin/bash
# MS10 10a network timing (DL-273 to DL-276), the MS5 5f method (run_timing_5f.sh): each cell alone (3 repeats) and under 6, 8 and 10
# concurrent copies (3 batches, per-run median pooled over all copies, DL-102), for N = 1e3, 3e3, 1e4 and 3e4 (cells net_1e3, net_3e3,
# net_1e4, net_3e4: P2 at ref_devalle, T_ramp 10 s, 2,950 tau incl. the 2 s discard, forward Euler dt 1e-3 tau). Run from the repository
# root on a clean git tree (nothing may be written inside the repository except results/timing/ms10/, which is git-ignored). Not a result
# run: nothing is classified and no result-family record is written. Total python working set polled every 0.5 s per cell into
# logs/mem_<cell>_w<n>.csv (a lower bound on the true peak, UNVERIFIED, as DL-142).
cd "$(dirname "$0")/.." || exit 1
P=.venv/Scripts/python.exe
D=results/timing/ms10
mkdir -p $D/logs
git status --porcelain > $D/logs/git_status_before.txt
git rev-parse HEAD > $D/logs/git_head.txt
$P -m pip freeze > $D/logs/pip_freeze.txt 2>&1
powershell -NoProfile -Command "Get-CimInstance Win32_PerfFormattedData_PerfProc_Process | Where-Object { \$_.Name -ne '_Total' -and \$_.Name -ne 'Idle' } | Sort-Object PercentProcessorTime -Descending | Select-Object -First 15 Name,IDProcess,PercentProcessorTime,WorkingSet | Format-Table -AutoSize | Out-String -Width 200" > $D/logs/machine_state_before.txt 2>&1
powercfg /getactivescheme >> $D/logs/machine_state_before.txt 2>&1
for c in net_1e3 net_3e3 net_1e4 net_3e4; do
  $P scripts/time_one_run.py --cell $c --repeat 3 --out-dir $D > $D/logs/alone_$c.log 2>&1
done
for c in net_1e3 net_3e3 net_1e4 net_3e4; do
  for n in 6 8 10; do
    L=3600
    [ $c = net_3e4 ] && L=7200
    mkdir -p $D/$c
    rm -f $D/logs/stop_${c}_w$n
    powershell -NoProfile -Command "\$mx=0; while(-not (Test-Path '$D/logs/stop_${c}_w$n')){ \$s=(Get-Process python -ErrorAction SilentlyContinue | Measure-Object WorkingSet64 -Sum).Sum; if(\$s -gt \$mx){\$mx=\$s}; Set-Content -Path '$D/logs/mem_${c}_w$n.csv' -Value \$mx; Start-Sleep -Milliseconds 500 }" &
    $P scripts/time_one_run.py --cell $c --workers $n --repeat 3 --limit-s $L --out-dir $D/$c > $D/logs/w${n}_$c.log 2>&1
    touch $D/logs/stop_${c}_w$n
    wait
  done
done
echo done > $D/logs/ALL_DONE_10A
