wait_gateway_models() {
  local url=$1 output=$2 deadline=$((JOB_START_EPOCH+600))
  local pending="${output}.pending.$$"
  while (( $(date +%s) < deadline )); do
    for pid in "${pids[@]}"; do
      if ! kill -0 "$pid" 2>/dev/null; then
        rm -f "$pending"
        echo "FATAL: worker/router step $pid exited before model registration" >&2
        return 1
      fi
    done
    if curl -sf --max-time 2 "$url" -o "$pending" &&
      python3 - "$pending" <<'MODEL_READY'
import json,sys
try:
    data=json.loads(open(sys.argv[1]).read())
    models=data.get('data') if isinstance(data,dict) else None
    valid=isinstance(models,list) and any(isinstance(row,dict) and row.get('id')=='qwen' for row in models)
except (OSError,ValueError):
    valid=False
sys.exit(0 if valid else 1)
MODEL_READY
    then
      if (( $(date +%s) >= deadline )); then break; fi
      mv "$pending" "$output"
      echo "GATEWAY_MODEL_READY after ${SECONDS}s"
      return 0
    fi
    sleep 2
  done
  rm -f "$pending"
  echo "FATAL: gateway model registration exceeded job-start readiness deadline" >&2
  return 1
}
