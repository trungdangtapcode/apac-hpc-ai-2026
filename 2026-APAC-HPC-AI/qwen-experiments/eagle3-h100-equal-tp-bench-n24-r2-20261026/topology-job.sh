#!/usr/bin/env bash
set -euo pipefail

ROOT=${SLURM_SUBMIT_DIR:?PBS artifact root is required}
BUNDLE=${QWEN_BUNDLE:?bundle path required}
ART=$ROOT/runs/${SLURM_JOB_ID:?job ID required}
SGLANG=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/sglang-harbor.sqsh
MODEL=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8
T0=${QWEN_ALLOCATION_T0:?allocation T0 is required}
mkdir -p "$ART"
cp "$BUNDLE/config.json" "$BUNDLE/placement.tsv" "$ART/"
export QWEN_ARTDIR=$ART QWEN_BUNDLE=$BUNDLE

NODES=($(scontrol show hostnames "$SLURM_JOB_NODELIST"))
(( ${#NODES[@]} == 1 )) || { echo 'FATAL: expected exactly one PBS node' >&2; exit 1; }
IPS=()
for host in "${NODES[@]}"; do IPS+=("$(getent ahostsv4 "$host" | awk 'NR==1 {ip=$1} END {print ip}')"); done

deadlines=$(python3 "$BUNDLE/phase-controller.py" deadlines "$T0")
python3 "$BUNDLE/phase-marker.py" "$ART" controller_t0 "$T0" "$deadlines" 1720 1800
PIDS=()
cleanup() {
  local code=$? start deadline
  trap - EXIT INT TERM
  start=$(date +%s)
  deadline=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" teardown "$start") || deadline=$((T0+1720))
  python3 "$BUNDLE/phase-marker.py" "$ART" teardown_start "$start" "$deadline" || :
  for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null || :; done
  while (( $(date +%s) < deadline )); do
    local alive=0
    for pid in "${PIDS[@]}"; do kill -0 "$pid" 2>/dev/null && alive=1; done
    (( alive )) || break
    sleep 1
  done
  for pid in "${PIDS[@]}"; do kill -9 "$pid" 2>/dev/null || :; done
  wait || :
  python3 "$BUNDLE/phase-marker.py" "$ART" teardown_end "$(date +%s)" "$code" || :
  return "$code"
}
trap cleanup EXIT INT TERM

mounts() {
  local patch_mount=""
  local role=$1
  mkdir -p "$ROOT/home/$SLURM_JOB_ID/$role/.cache"
  if [[ $role == prefill-* || $role == decode-* ]]; then
    patch_mount=",$BUNDLE/nixl-conn.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py:ro"
  fi
  echo "/scratch:/scratch,$ROOT/home/$SLURM_JOB_ID/$role:$HOME,$ROOT:$ROOT$patch_mount"
}

startup_deadline=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" startup "$T0")
python3 "$BUNDLE/phase-marker.py" "$ART" startup_start "$T0" "$startup_deadline"
: > "$ART/endpoints.tsv"
router_args=()
workers=0
while IFS=$'\t' read -r name node tp port bootstrap; do
  [[ $node == 0 && $tp == 4 ]] || { echo "FATAL: invalid frozen placement row: $name $node $tp" >&2; exit 2; }
  role=${name%%-*}
  nccl_port=$((20000 + port - 30100))
  if [[ $role == prefill ]]; then
    extra=(--disaggregation-bootstrap-port "$bootstrap")
    router_args+=(--prefill "http://${IPS[0]}:$port" "$bootstrap")
  elif [[ $role == decode ]]; then
    extra=(--ep-size 4 --max-running-requests 256)
    router_args+=(--decode "http://${IPS[0]}:$port")
  else
    echo "FATAL: unknown role $role" >&2; exit 2
  fi
  printf '%s\thttp://%s:%s\t%s\n' "$name" "${IPS[0]}" "$port" "$bootstrap" >> "$ART/endpoints.tsv"
  srun --exact -N1 -n1 -w "${NODES[0]}" --gres="gpu:$tp" --cpus-per-task="$((tp*8))" \
    --container-image="$SGLANG" --container-mounts="$(mounts "$name")" \
    bash "$BUNDLE/worker.sh" "$name" "$port" "$MODEL" "$tp" --nccl-port "$nccl_port" "${extra[@]}" \
    >"$ART/$name.log" 2>&1 &
  PIDS+=("$!")
  ((workers+=1))
done < "$BUNDLE/placement.tsv"
[[ $workers == 2 ]] || { echo "FATAL: expected one P4 and one D4 worker, saw $workers" >&2; exit 2; }

wait_http() {
  local url=$1 deadline=$2
  while ! curl -sf --max-time 2 -o /dev/null "$url"; do
    for pid in "${PIDS[@]}"; do kill -0 "$pid" 2>/dev/null || { echo "FATAL: role task $pid exited before readiness" >&2; return 1; }; done
    (( $(date +%s) < deadline )) || { echo "FATAL: readiness deadline expired for $url" >&2; return 1; }
    sleep 2
  done
}
while IFS=$'\t' read -r name url bootstrap; do
  wait_http "$url/health" "$startup_deadline"
  python3 "$BUNDLE/phase-marker.py" "$ART" worker_ready "$name" "$(date +%s)"
done < "$ART/endpoints.tsv"

srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts router)" \
  bash "$BUNDLE/router-with-preflight.sh" round_robin "${router_args[@]}" \
  --host 0.0.0.0 --port 8000 --prometheus-port 29000 >"$ART/router.log" 2>&1 &
PIDS+=("$!")
wait_http "http://${IPS[0]}:8000/health" "$startup_deadline"
python3 "$BUNDLE/metadata-gate.py" pre-warmup "$ART" > "$ART/pre-warmup-gate.json"
python3 "$BUNDLE/phase-marker.py" "$ART" startup_end "$(date +%s)" "$startup_deadline"

semantic_start=$(date +%s)
semantic_deadline=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" semantic "$semantic_start")
semantic_remaining=$(python3 "$BUNDLE/phase-controller.py" remaining "$T0" semantic "$semantic_start" "$(date +%s)")
(( semantic_remaining > 0 )) || { echo 'FATAL: semantic phase has no remaining time' >&2; exit 1; }
export QWEN_SEMANTIC_DEADLINE_EPOCH=$semantic_deadline
python3 "$BUNDLE/phase-marker.py" "$ART" semantic_start "$semantic_start" "$semantic_deadline"
timeout --signal=TERM --kill-after=10s "${semantic_remaining}s" \
  python3 "$BUNDLE/semantic_probe.py" > "$ART/semantic-client.log" 2>&1
python3 "$BUNDLE/phase-marker.py" "$ART" semantic_end "$(date +%s)" "$semantic_deadline"
python3 "$BUNDLE/metadata-gate.py" post-semantic "$ART" --experiment-id "$QWEN_EXPERIMENT_ID" \
  > "$ART/post-semantic-gate.json"
echo 'ONE_EQUAL_TP_SINGLE_NODE_SEMANTIC_PD_PASS (no output-ID or score claim)' | tee "$ART/CONTROLLER_PASS.txt"

score_start=$(date +%s)
score_deadline=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" scoring "$score_start")
score_remaining=$(python3 "$BUNDLE/phase-controller.py" remaining "$T0" scoring "$score_start" "$(date +%s)")
(( score_remaining >= 260 )) || { echo 'FATAL: insufficient reserved time for the complete N24 AIPerf measurement' >&2; exit 1; }
python3 "$BUNDLE/phase-marker.py" "$ART" score_start "$score_start" "$score_deadline"
AIPERF=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/aiperf.sqsh
timeout --signal=TERM --kill-after=5s "${score_remaining}s" bash -c 'source "$QWEN_BUNDLE/pbs-shim.sh"; srun "$@"' _ --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=8 \
  --container-image="$AIPERF" --container-mounts="/scratch:/scratch,$ROOT:$ROOT" \
  env QWEN_TUNE_NS=24 QWEN_DIAGNOSTIC_PROFILE=0 QWEN_BUNDLE="$BUNDLE" \
    QWEN_BENCHMARK_DEADLINE="$score_deadline" QWEN_GRACE=30 \
    bash "$BUNDLE/benchmark.sh" "${IPS[0]}:8000" "$MODEL" "$ART"
python3 "$BUNDLE/check-benchmark.py" score "$ART" > "$ART/benchmark-gate.json"
python3 "$BUNDLE/phase-marker.py" "$ART" score_end "$(date +%s)" "$score_deadline"

quality_start=$(date +%s)
quality_deadline=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" quality "$quality_start")
quality_remaining=$(python3 "$BUNDLE/phase-controller.py" remaining "$T0" quality "$quality_start" "$(date +%s)")
(( quality_remaining >= 220 )) || { echo 'FATAL: insufficient time for output and retrieval checks' >&2; exit 1; }
python3 "$BUNDLE/phase-marker.py" "$ART" quality_start "$quality_start" "$quality_deadline"
set +e
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/aiperf.sqsh --container-mounts="/scratch:/scratch,$ROOT:$ROOT" \
  timeout --signal=TERM --kill-after=5s 200s python3 "$BUNDLE/output-smoke.py" "${IPS[0]}:8000" "$ART" > "$ART/output-smoke.log" 2>&1 & smoke_pid=$!
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/aiperf.sqsh --container-mounts="/scratch:/scratch,$ROOT:$ROOT" \
  timeout --signal=TERM --kill-after=5s 200s python3 "$BUNDLE/long-context-check.py" "${IPS[0]}:8000" "$ART" > "$ART/long-context-check.log" 2>&1 & retrieval_pid=$!
wait "$smoke_pid"; smoke_status=$?
wait "$retrieval_pid"; retrieval_status=$?
set -e
(( smoke_status == 0 && retrieval_status == 0 )) || { echo "FATAL: post-score smoke/retrieval failed: $smoke_status/$retrieval_status" >&2; exit 1; }
python3 "$BUNDLE/check-benchmark.py" full "$ART" > "$ART/full-local-acceptance.json"
python3 "$BUNDLE/phase-marker.py" "$ART" quality_end "$(date +%s)" "$quality_deadline"
echo 'N24_FULL_WORKLOAD_AND_LOCAL_OUTPUT_GATES_PASS; official accuracy UNKNOWN' | tee "$ART/ACCEPTANCE.txt"
