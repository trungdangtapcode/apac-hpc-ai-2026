#!/usr/bin/env bash
set -euo pipefail
export PATH=/home/apacsc42/.local/bin:/usr/local/bin:/usr/bin:/bin
APAC_WAKE_ROOT=/home/apacsc42/workspace/research-autopilot
cd "$APAC_WAKE_ROOT"
mkdir -p runs
exec 9>"$APAC_WAKE_ROOT/wake.lock"
flock -n 9 || exit 0
if [[ -f PAUSED ]]; then exit 0; fi
if [[ -f cooldown-until ]]; then
  read -r APAC_WAKE_COOLDOWN <cooldown-until
  if (( $(date +%s) < APAC_WAKE_COOLDOWN )); then exit 0; fi
fi
if [[ $(date -u +%F) > 2026-11-15 ]]; then exit 0; fi
APAC_WAKE_STAMP=$(date -u +%Y%m%dT%H%M%SZ)
# Avoid spending a model turn on an unchanged pending queue every30minutes.
if ! python3 snapshot.py >"runs/$APAC_WAKE_STAMP.snapshot.json"; then
  exit 0
fi
APAC_WAKE_EXIT=0
timeout --signal=TERM --kill-after=30s 20m \
  /home/apacsc42/.local/bin/codex exec \
  --skip-git-repo-check --sandbox danger-full-access -c approval_policy='"never"' \
  -C /home/apacsc42 --json -o "$APAC_WAKE_ROOT/runs/$APAC_WAKE_STAMP.final.md" \
  - <prompt.txt >"runs/$APAC_WAKE_STAMP.jsonl" 2>"runs/$APAC_WAKE_STAMP.stderr" || APAC_WAKE_EXIT=$?
printf '%s exit=%s\n' "$APAC_WAKE_STAMP" "$APAC_WAKE_EXIT" >> wake.log
if [[ $APAC_WAKE_EXIT -ne 0 ]]; then
  # Retry at the next scheduled check even if the scheduler state is unchanged.
  rm -f "$APAC_WAKE_ROOT/last-wake.json"
  if rg -q 'hit your usage limit|rate_limit_exceeded' "runs/$APAC_WAKE_STAMP.jsonl"; then
    echo "$(( $(date +%s)+1800 ))" >cooldown-until
  fi
  printf '\nAutopilot run %s failed/timed out (exit %s); see runs/.\n' \
    "$APAC_WAKE_STAMP" "$APAC_WAKE_EXIT" >> LATEST.md
fi
