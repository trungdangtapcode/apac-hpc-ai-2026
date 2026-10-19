#!/usr/bin/env bash
set -euo pipefail
bash "$QWEN_BUNDLE/benchmark.sh" "$@"
export HF_HUB_CACHE="$(dirname "$(dirname "$3")")/hf-cache"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
if (( $(date +%s)+110 < ${QWEN_BENCHMARK_DEADLINE:-0} )); then
  timeout 100 python3 "$QWEN_BUNDLE/long-context-check.py" "$1" "$3" >"$3/long-context-check.log" 2>&1 || touch "$3/long-context-check-failed.txt"
else
  touch "$3/long-context-check-deferred.txt"
fi
