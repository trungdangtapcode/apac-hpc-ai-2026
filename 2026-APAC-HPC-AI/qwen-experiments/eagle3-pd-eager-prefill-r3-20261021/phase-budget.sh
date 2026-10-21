#!/usr/bin/env bash
# Bound pair initialization while retaining 360 seconds for client launch,
# locality capture, actual token checks and the separately reserved cleanup.
qwen_pair_timeout() {
  local deadline=$1 now=$2 remaining
  remaining=$((deadline-now-360))
  ((remaining>0)) || return 1
  ((remaining<=480)) || remaining=480
  printf '%s\n' "$remaining"
}
