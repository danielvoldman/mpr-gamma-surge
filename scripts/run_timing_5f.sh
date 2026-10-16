#!/bin/bash
# MS5 5f network timing (docs/ms5_plan.md, plan 9.2 steps 1 to 3). Run from the repository root in the clean machine state
# (docs: DL-104 "Machine state"). Output next to the DL-104 clean timings: results/timing/clean/<cell>.json (alone, 3 repeats)
# and results/timing/clean/<cell>/workers_<n>.json (n concurrent copies x 3 batches, pooled per-run median, DL-102).
# Cells: net_1e4 alone and at 6, 8, 10 copies; net_3e4 alone and at 10; net_1e3 alone and at 10 (net_1e3 is ours, for S9's N = 1e3, 3e3).
# Per-run limit 3600 s (D-6); net_3e4 under 10 copies 7200 s (R5-rate expectation ~10 min, but the kernel rate is UNVERIFIED and
# a 10x slower kernel would put the loaded run at ~3500 s, DL-104 convention for p5_1000).
cd "$(dirname "$0")/.." || exit 1
P=.venv/Scripts/python.exe
D=results/timing/clean
mkdir -p $D/logs
for c in net_1e4 net_3e4 net_1e3; do
  $P scripts/time_one_run.py --cell $c --repeat 3 --out-dir $D > $D/logs/alone_$c.log 2>&1
done
for spec in net_1e3:10 net_1e4:10 net_1e4:8 net_1e4:6 net_3e4:10; do
  c=${spec%%:*}; n=${spec##*:}; L=3600
  [ $c = net_3e4 ] && L=7200
  mkdir -p $D/$c
  $P scripts/time_one_run.py --cell $c --workers $n --repeat 3 --limit-s $L --out-dir $D/$c > $D/logs/w${n}_$c.log 2>&1
done
$P -m mprsurge.analysis.timing --predict --workers 10 --results-dir results/timing/clean --alone-dir results/timing/clean \
  --out results/timing/clean/prediction_5f.txt > $D/logs/predict_5f.log 2>&1
echo done > $D/logs/ALL_DONE_5F
