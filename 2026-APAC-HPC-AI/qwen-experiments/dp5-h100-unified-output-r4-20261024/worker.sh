#!/usr/bin/env bash
set -euo pipefail

# Invoked only by the root-reviewed Slurm controller inside the pinned Pyxis
# image. Output diagnostics run only after independent startup readiness.
BUNDLE=${D5_BUNDLE:?D5_BUNDLE must point to the reviewed candidate}
MODEL=${D5_MODEL_DIR:-/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8}
OUT=${D5_OUTPUT_DIR:?D5_OUTPUT_DIR is required}
PORT=${D5_PORT:-30150}
HOME=${HOME:?controller must mount a private HOME}
export HOME
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"
mkdir -p "$XDG_CACHE_HOME" "$OUT" "$OUT/observer"

cd "$BUNDLE"
sha256sum --check SHA256SUMS
python3 "$BUNDLE/prepare_check.py"
python3 "$BUNDLE/source_preflight.py" | tee "$OUT/source-preflight.json"
python3 "$BUNDLE/asset_preflight.py" "$MODEL" | tee "$OUT/model-header-preflight.json"

visible=${CUDA_VISIBLE_DEVICES:-}
[[ -n "$visible" ]] || { echo "FATAL: scheduler did not assign CUDA_VISIBLE_DEVICES" >&2; exit 2; }
[[ $(awk -F, '{print NF}' <<<"$visible") == 5 ]] || {
  echo "FATAL: expected exactly five assigned GPUs, got '$visible'" >&2; exit 2;
}
[[ ${SLURM_JOB_NUM_NODES:-1} == 1 ]] || {
  echo "FATAL: D5 requires a one-node allocation" >&2; exit 2;
}
printf 'HOST=%s\nCUDA_VISIBLE_DEVICES=%s\nHOME=%s\n' "$(hostname -f)" "$visible" "$HOME" | tee "$OUT/launch-context.txt"
python3 "$BUNDLE/device_preflight.py" | tee "$OUT/devices.json"

server_args=(
  --model-path "$MODEL"
  --host 127.0.0.1
  --port "$PORT"
  --dtype bfloat16
  --kv-cache-dtype bfloat16
  --tp-size 5
  --dp-size 5
  --enable-dp-attention
  --enable-dp-lm-head
  --ep-size 5
  --moe-dp-size 1
  --ep-num-redundant-experts 2
  --ep-dispatch-algorithm dynamic
  --moe-a2a-backend none
  --moe-runner-backend hpc_ops
  --page-size 64
  --served-model-name qwen
  --enable-metrics
  --cuda-graph-backend-prefill disabled
  --cuda-graph-max-bs-decode 4
  --trust-remote-code
)
{ printf 'SERVER_ARGV='; printf ' %q' "${server_args[@]}"; printf '\n'; } | tee "$OUT/server-argv.txt"
python3 "$BUNDLE/phase-marker.py" "$OUT" worker_preflight_complete
python3 "$BUNDLE/resource-sampler.py" --out "$OUT/resource-telemetry" --role unified --port "$PORT" --parent "$$" --gpus "$visible" --interval 5 --duration 950 >"$OUT/resource-sampler.log" 2>&1 &
sampler_pid=$!
python3 "$BUNDLE/phase-marker.py" "$OUT" server_startup_begin
export D5_OBSERVER_DIR="$OUT/observer"
export PYTHONPATH="$BUNDLE/observer${PYTHONPATH:+:$PYTHONPATH}"
timeout --signal=TERM --kill-after=10s 900s \
  python3 -m sglang.launch_server "${server_args[@]}" \
  >"$OUT/server.log" 2>&1 &
server_pid=$!
cleanup() {
  rc=$?
  trap - EXIT
  if [[ -n ${sampler_pid:-} ]]; then kill -TERM "$sampler_pid" 2>/dev/null || true; wait "$sampler_pid" 2>/dev/null || true; fi
  kill -TERM "$server_pid" 2>/dev/null || true
  wait "$server_pid" 2>/dev/null || true
  exit "$rc"
}
trap cleanup EXIT
deadline=$((SECONDS+660))
while (( SECONDS < deadline )); do
  health_code=$(curl --silent --max-time 3 --write-out '%{http_code}' "http://127.0.0.1:$PORT/health" \
      -o "$OUT/health.json") || health_code=000
  if [[ $health_code == 200 ]]; then
    printf 'HEALTH_HTTP=200\nHEALTH_READY_UTC=%s\n' "$(date -u +%FT%TZ)" | tee "$OUT/health-status.txt"
    python3 "$BUNDLE/phase-marker.py" "$OUT" native_health_ready
    python3 "$BUNDLE/headcheck.py" --out "$OUT"
    python3 "$BUNDLE/phase-marker.py" "$OUT" readiness_pass
    python3 "$BUNDLE/phase-marker.py" "$OUT" smoke_begin
    timeout --signal=TERM --kill-after=2s 60s python3 "$BUNDLE/output-smoke.py" "127.0.0.1:$PORT" "$OUT" | tee "$OUT/output-smoke.stdout.json"
    python3 "$BUNDLE/phase-marker.py" "$OUT" smoke_end
    python3 "$BUNDLE/phase-marker.py" "$OUT" retrieval_begin
    timeout --signal=TERM --kill-after=2s 90s python3 "$BUNDLE/long-context-check.py" "127.0.0.1:$PORT" "$OUT" "$MODEL" | tee "$OUT/long-context-check.stdout.json"
    python3 "$BUNDLE/phase-marker.py" "$OUT" retrieval_end
    python3 "$BUNDLE/output-diagnostics.py" "$OUT"
    python3 "$BUNDLE/phase-marker.py" "$OUT" diagnostics_recorded
    kill -TERM "$sampler_pid" 2>/dev/null || true
    wait "$sampler_pid" 2>/dev/null || true
    exit 0
  fi
  if ! kill -0 "$server_pid" 2>/dev/null; then
    echo "FATAL: server exited before native health readiness" >&2
    tail -n 100 "$OUT/server.log" >&2
    exit 1
  fi
  sleep 3
done
echo "FATAL: 660-second startup health deadline expired" >&2
tail -n 100 "$OUT/server.log" >&2
exit 124
