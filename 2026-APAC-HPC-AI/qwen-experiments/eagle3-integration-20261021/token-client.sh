#!/usr/bin/env bash
set -euo pipefail
python3 "$QWEN_BUNDLE/phase-marker.py" "$3" token_diagnostic_start unranked 1
remaining=$((QWEN_BENCHMARK_DEADLINE-$(date +%s)))
((remaining>=120)) || { echo 'Insufficient diagnostic time'; exit 1; }
((remaining<=240)) || remaining=240
timeout --signal=TERM --kill-after=10s "$remaining" python3 "$QWEN_BUNDLE/token-control.py" "$1" "$2" "$3" >"$3/token-control.log" 2>&1
python3 "$QWEN_BUNDLE/phase-marker.py" "$3" token_diagnostic_end unranked 1
