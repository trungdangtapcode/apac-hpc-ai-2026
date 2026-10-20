#!/bin/bash
set -euo pipefail
out=$1
bundle=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
mkdir -p "$out"
pids=()
cleanup() {
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || :; done
  wait || :
}
trap cleanup EXIT
nvidia-smi --query-gpu=index,uuid,name,driver_version,clocks.sm,clocks.mem,power.draw,memory.used --format=csv > "$out/gpu-before.csv"
for rank in 0 1 2 3 4 5 6 7; do
  timeout --signal=TERM --kill-after=10s 540s python3 "$bundle/bench.py" --rank "$rank" --out "$out" --config "$bundle/config.json" > "$out/rank-$rank.stdout" 2> "$out/rank-$rank.stderr" &
  pids+=("$!")
done
failed=0
for pid in "${pids[@]}"; do wait "$pid" || failed=1; done
nvidia-smi --query-gpu=index,uuid,name,driver_version,clocks.sm,clocks.mem,power.draw,memory.used --format=csv > "$out/gpu-after.csv"
exit "$failed"
