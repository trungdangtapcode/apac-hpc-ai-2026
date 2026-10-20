#!/bin/bash
set -euo pipefail
ulimit -c 0
out=$1
bundle=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
mkdir -p "$out"
pids=()
cleanup() {
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || :; done
  wait || :
}
trap cleanup EXIT
stage_start=$SECONDS
# Test every provider and a captured call on one GPU before the full screen.
mkdir -p "$out/preflight"
python3 - "$bundle/config.json" "$out/preflight/config.json" <<'CONFIG'
import json,sys
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text())
c.update(experiment='unranked-one-rank-provider-preflight',batch_tokens=[54],operations_per_graph=1,replays_per_sample=1,samples=1,python_budget_s=170)
Path(sys.argv[2]).write_text(json.dumps(c,indent=2)+'\n')
CONFIG
timeout --signal=TERM --kill-after=10s 210s python3 "$bundle/bench.py" --rank 0 --out "$out/preflight" --config "$out/preflight/config.json" > "$out/preflight/stdout" 2> "$out/preflight/stderr"
python3 - "$out/preflight/rank-0.json" <<'CHECK'
import json,sys
x=json.load(open(sys.argv[1]))
assert x.get('completed') and x.get('input_integrity_passed') and len(x['cases'])==6
print('UNRANKED_PROVIDER_PREFLIGHT_PASSED')
CHECK
remaining=$((540-(SECONDS-stage_start)))
(( remaining>=120 )) || { echo 'INSUFFICIENT_TIME_AFTER_PREFLIGHT'; exit 1; }
nvidia-smi --query-gpu=index,uuid,name,driver_version,clocks.sm,clocks.mem,power.draw,memory.used --format=csv > "$out/gpu-before.csv"
for rank in 0 1 2 3 4 5 6 7; do
  timeout --signal=TERM --kill-after=10s "$remaining"s python3 "$bundle/bench.py" --rank "$rank" --out "$out" --config "$bundle/config.json" > "$out/rank-$rank.stdout" 2> "$out/rank-$rank.stderr" &
  pids+=("$!")
done
failed=0
for pid in "${pids[@]}"; do wait "$pid" || failed=1; done
nvidia-smi --query-gpu=index,uuid,name,driver_version,clocks.sm,clocks.mem,power.draw,memory.used --format=csv > "$out/gpu-after.csv"
exit "$failed"
