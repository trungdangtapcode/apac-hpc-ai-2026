#!/usr/bin/env bash
set -euo pipefail
ROOT=$SLURM_SUBMIT_DIR
BUNDLE=$QWEN_BUNDLE
ART=$ROOT/runs/$SLURM_JOB_ID
export QWEN_ARTDIR="$ART"
SGLANG=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/sglang-harbor.sqsh
AIPERF=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/aiperf.sqsh
MODEL=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8
mkdir -p "$ART"
cp -r "$BUNDLE" "$ART/submitted"
cp "$BUNDLE/benchmark.sh" "$BUNDLE/summarize.py" "$BUNDLE/worker.sh" "$ART/"
cp "$BUNDLE/config.json" "$ART/config.json"
NODES=($(scontrol show hostnames "$SLURM_JOB_NODELIST"))
IPS=()
for host in "${NODES[@]}"; do
  IPS+=("$(getent ahostsv4 "$host" | awk 'NR==1 {ip=$1} END {print ip}')")
done
pids=()
cleanup() {
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || :; done
  wait || :
}
trap cleanup EXIT
mounts() {
  local patch_mount=""
  mkdir -p "$ROOT/home/$SLURM_JOB_ID/$1"
  case "$1" in
    prefill-*|decode-*)
      if [[ -f "$BUNDLE/nixl-conn.py" ]]; then
        patch_mount=",$BUNDLE/nixl-conn.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py:ro"
      fi
      ;;
  esac
  echo "/scratch:/scratch,$ROOT/home/$SLURM_JOB_ID/$1:$HOME,$ROOT:$ROOT$patch_mount"
}
# Bounded startup-cost intervention on both allocated nodes, before workers.
mkdir -p "$ART/startup-prefetch"
for node in 0 1; do
  srun --overlap -N1 -n1 -w "${NODES[$node]}" --gres=gpu:0 --cpus-per-task=4 \
    --container-image="$SGLANG" --container-mounts="$(mounts prefetch-node$node)" \
    timeout --signal=TERM --kill-after=10s 150s python3 "$BUNDLE/prefetch-weights.py" \
      --mode "$QWEN_NODE_PREFETCH" --model "$MODEL" --out "$ART/startup-prefetch/node-$node.json" \
    >"$ART/startup-prefetch/node-$node.log" 2>&1 &
  pids+=("$!")
done
for pid in "${pids[@]}"; do wait "$pid"; done
pids=()
echo "START job=$SLURM_JOB_ID nodes=${NODES[*]} at $(date -Iseconds)"
cat "$BUNDLE/config.json"
: >"$ART/endpoints.tsv"
router_args=()
while read -r name node tp port bootstrap; do
  role=${name%%-*}
  # Distinct rendezvous ports avoid races in automatic ephemeral-port selection.
  nccl_port=$((20000+port-30100))
  if [[ $role == prefill ]]; then
    extra=(--disaggregation-bootstrap-port "$bootstrap")
    if [[ ${QWEN_PREFILL_EP:-1} != 1 ]]; then extra+=(--ep-size "$QWEN_PREFILL_EP"); fi
    router_args+=(--prefill "http://${IPS[$node]}:$port" "$bootstrap")
  else
    extra=(--ep-size "$tp" --max-running-requests 256)
    router_args+=(--decode "http://${IPS[$node]}:$port")
  fi
  printf '%s\t%s\t%s\n' "$name" "http://${IPS[$node]}:$port" "$bootstrap" >>"$ART/endpoints.tsv"
  srun --exact -N1 -n1 -w "${NODES[$node]}" --gres="gpu:$tp" --cpus-per-task="$((tp*8))" \
    --container-image="$SGLANG" --container-mounts="$(mounts "$name")" \
    bash "$ART/worker.sh" "$name" "$port" "$MODEL" "$tp" --nccl-port "$nccl_port" "${extra[@]}" \
    >"$ART/$name.log" 2>&1 &
  pids+=("$!")
done <"$BUNDLE/placement.tsv"
wait_http() {
  # Workers share one absolute startup deadline; do not renew per endpoint.
  local url=$1 deadline=${2:-1050}
  while ! curl -sf --max-time 2 -o /dev/null "$url"; do
    for pid in "${pids[@]}"; do
      if ! kill -0 "$pid" 2>/dev/null; then
        echo "FATAL: worker/router step $pid exited before readiness" >&2; return 1
      fi
    done
    if (( SECONDS>=deadline )); then echo "FATAL: readiness timeout $url" >&2; return 1; fi
    sleep 2
  done
}
while read -r name url bootstrap; do wait_http "$url/health"; echo "READY $name after ${SECONDS}s"; done <"$ART/endpoints.tsv"
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts router)" \
  bash "$QWEN_BUNDLE/router-with-preflight.sh" round_robin "${router_args[@]}" \
    --host 0.0.0.0 --port 8000 --prometheus-port 29000 >"$ART/router.log" 2>&1 &
pids+=("$!")
wait_http "http://${IPS[0]}:8000/health" "$((SECONDS+120))"
echo "ALL_WORKERS_READY after ${SECONDS}s"
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts pair-warmup)" \
  env QWEN_PAIR_TIMEOUT="${QWEN_PAIR_TIMEOUT:-360}" QWEN_PAIR_PARALLELISM="${QWEN_PAIR_PARALLELISM:-8}" \
    python3 "$BUNDLE/warm-topology.py" "${IPS[0]}" "$ART" >"$ART/pair-warmup.log" 2>&1
echo "ALL_PAIRS_WARM after ${SECONDS}s"
python3 "$BUNDLE/request-worker-locality.py" "$ART" "$BUNDLE/placement.tsv" \
  >"$ART/worker-locality-request.log" 2>&1
echo "WORKER_LOCALITY_CAPTURE_DONE after ${SECONDS}s"
# Keep time for Slurm step cleanup; skip confirmation explicitly if too little remains.
deadline=$(($(date +%s)+1200-SECONDS-40))
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts token-client)" \
  env QWEN_SWEEP_NS="${QWEN_SWEEP_NS:-16 32 40 48}" QWEN_TUNE_NS="${QWEN_TUNE_NS:-48}" QWEN_DIAGNOSTIC_PROFILE="${QWEN_DIAGNOSTIC_PROFILE:-0}" QWEN_BUNDLE="$BUNDLE" \
    QWEN_BENCHMARK_DEADLINE="$deadline" QWEN_GRACE=30 \
    bash "$BUNDLE/token-client.sh" "${IPS[0]}:8000" "$MODEL" "$ART"
python3 "$BUNDLE/check-token-result.py" "$ART/token-control.json"
echo "TOKEN_DIAGNOSTIC_COMPLETE after ${SECONDS}s at $(date -Iseconds)"
