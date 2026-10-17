#!/bin/bash
# MS5 5i headline re-time on the A4 path (docs/ms5_plan.md; DL-122). Run from the repository root in the clean machine state
# (DL-104 "Machine state"). The DL-104/118 results in results/timing/clean/ are NOT touched: they are copied to
# results/timing/a4/ and the headline is re-timed there (alone, 3 repeats; 10 concurrent copies x 3 batches, DL-102 to DL-105),
# then the 9.2 prediction is re-run on that directory. The other cells keep their clean-state timings: their eta paths
# differ from the provisional ones by < 1e-6 (DL-115, DL-122), so they are not re-timed.
cd "$(dirname "$0")/.." || exit 1
P=.venv/Scripts/python.exe
C=results/timing/clean
D=results/timing/a4
mkdir -p $D/logs $D/headline
for f in $C/*.json; do cp -n "$f" $D/; done
for d in $C/*/; do n=$(basename "$d"); [ "$n" = logs ] && continue; mkdir -p "$D/$n"; cp -n "$d"*.json "$D/$n/" 2>/dev/null; done
rm -f $D/headline.json $D/headline/workers_10.json
$P scripts/time_one_run.py --cell headline --repeat 3 --out-dir $D > $D/logs/alone_headline.log 2>&1
$P scripts/time_one_run.py --cell headline --workers 10 --repeat 3 --limit-s 3600 --out-dir $D/headline > $D/logs/w10_headline.log 2>&1
$P -m mprsurge.analysis.timing --predict --workers 10 --results-dir $D --alone-dir $D --out $D/prediction_5i.txt > $D/logs/predict_5i.log 2>&1
echo done > $D/logs/ALL_DONE_5I
