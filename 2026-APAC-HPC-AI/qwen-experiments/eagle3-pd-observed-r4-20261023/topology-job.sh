#!/usr/bin/env bash
set -euo pipefail

ROOT=$SLURM_SUBMIT_DIR
BUNDLE=$QWEN_BUNDLE
ART=$ROOT/runs/$SLURM_JOB_ID
SGLANG=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/sglang-harbor.sqsh
MODEL=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8
DRAFT=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/drafts/nebius-eagle3-qwen235b-ff0f0c09
mkdir -p "$ART"
export QWEN_ARTDIR=$ART QWEN_BUNDLE=$BUNDLE QWEN_EXPERIMENT_ID=eagle3-pd-observed-r4-20261023

T0=${QWEN_ALLOCATION_T0:?batch T0 is required}
DEADLINES=$(python3 "$BUNDLE/phase-controller.py" deadlines "$T0")
STARTUP_DEADLINE=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" startup "$T0")
export QWEN_T0=$T0
python3 "$BUNDLE/phase-marker.py" "$ART" controller_t0 "$T0" "$DEADLINES" 1530 1800
cp "$BUNDLE/config.json" "$BUNDLE/placement.tsv" "$BUNDLE/prepared-corpus.json" "$ART/"
cp "$BUNDLE/target-reference.json" "$ART/target-reference.json"

NODES=($(scontrol show hostnames "$SLURM_JOB_NODELIST"))
(( ${#NODES[@]} == 2 )) || { echo 'FATAL: expected two PBS nodes' >&2; exit 1; }
IPS=()
for host in "${NODES[@]}"; do
  IPS+=("$(getent ahostsv4 "$host" | awk 'NR==1 {ip=$1} END {print ip}')")
done
PIDS=()
cleanup() {
  local code=$?
  local teardown_start teardown_deadline
  teardown_start=$(date +%s)
  teardown_deadline=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" teardown "$teardown_start") || teardown_deadline=$((T0+1530))
  python3 "$BUNDLE/phase-marker.py" "$ART" teardown_start "$teardown_start" "$teardown_deadline" || :
  for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null || :; done
  while (( $(date +%s) < teardown_deadline )); do
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
  mkdir -p "$ROOT/home/$SLURM_JOB_ID/$1"
  if [[ $1 == prefill-* || $1 == decode-* ]]; then
    patch_mount=",$BUNDLE/nixl-conn.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py:ro"
  fi
  echo "/scratch:/scratch,$ROOT/home/$SLURM_JOB_ID/$1:$HOME,$ROOT:$ROOT$patch_mount"
}

phase_remaining() {
  local start_var=${1^^}_START
  python3 "$BUNDLE/phase-controller.py" remaining "$T0" "$1" "${!start_var}" "$(date +%s)"
}
require_phase_time() {
  local phase=$1 rem
  rem=$(phase_remaining "$phase")
  (( rem > 0 )) || { echo "FATAL: $phase absolute phase deadline expired" >&2; return 1; }
  printf '%s\n' "$rem"
}

STARTUP_START=$T0
python3 "$BUNDLE/phase-marker.py" "$ART" startup_start "$T0" "$STARTUP_DEADLINE"
: >"$ART/endpoints.tsv"
router_args=()
while IFS=$'\t' read -r name node tp port bootstrap; do
  role=${name%%-*}
  nccl_port=$((20000+port-30100))
  if [[ $role == prefill ]]; then
    extra=(--disaggregation-bootstrap-port "$bootstrap")
    router_args+=(--prefill "http://${IPS[$node]}:$port" "$bootstrap")
  elif [[ $role == decode ]]; then
    extra=(--ep-size "$tp" --max-running-requests 256)
    router_args+=(--decode "http://${IPS[$node]}:$port")
  else
    echo "FATAL: unknown role $role" >&2; exit 1
  fi
  printf '%s\t%s\t%s\n' "$name" "http://${IPS[$node]}:$port" "$bootstrap" >>"$ART/endpoints.tsv"
  srun --exact -N1 -n1 -w "${NODES[$node]}" --gres="gpu:$tp" --cpus-per-task="$((tp*8))" \
    --container-image="$SGLANG" --container-mounts="$(mounts "$name")" \
    bash "$BUNDLE/worker.sh" "$name" "$port" "$MODEL" "$tp" --nccl-port "$nccl_port" "${extra[@]}" \
    >"$ART/$name.log" 2>&1 &
  PIDS+=("$!")
done <"$BUNDLE/placement.tsv"
[[ $(wc -l <"$ART/endpoints.tsv") == 3 ]] || { echo 'FATAL: expected two P and one D worker' >&2; exit 1; }

wait_http() {
  local url=$1 deadline=$2
  while ! curl -sf --max-time 2 -o /dev/null "$url"; do
    for pid in "${PIDS[@]}"; do
      kill -0 "$pid" 2>/dev/null || { echo "FATAL: task $pid exited before readiness" >&2; return 1; }
    done
    (( $(date +%s) < deadline )) || { echo "FATAL: startup deadline expired for $url" >&2; return 1; }
    sleep 2
  done
}
while IFS=$'\t' read -r name url bootstrap; do
  wait_http "$url/health" "$STARTUP_DEADLINE"
  python3 "$BUNDLE/phase-marker.py" "$ART" worker_ready "$name" "$(date +%s)"
done <"$ART/endpoints.tsv"
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts router)" \
  bash "$BUNDLE/router-with-preflight.sh" round_robin "${router_args[@]}" \
  --host 0.0.0.0 --port 8000 --prometheus-port 29000 >"$ART/router.log" 2>&1 &
PIDS+=("$!")
wait_http "http://${IPS[0]}:8000/health" "$STARTUP_DEADLINE"
python3 "$BUNDLE/phase-marker.py" "$ART" startup_end "$(date +%s)" "$STARTUP_DEADLINE"

WARMUP_START=$(date +%s)
WARMUP_DEADLINE=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" warmup "$WARMUP_START")
export QWEN_WARMUP_DEADLINE_EPOCH=$WARMUP_DEADLINE
warmup_remaining=$(require_phase_time warmup)
python3 "$BUNDLE/phase-marker.py" "$ART" warmup_start "$(date +%s)" "$WARMUP_DEADLINE"
python3 "$BUNDLE/observer-gate.py" pre-warmup "$ART" >"$ART/pre-warmup-gate.json"
timeout --signal=TERM --kill-after=10s "${warmup_remaining}s" /bin/bash -c 'srun "$@"' qwen-pair-warmup \
  --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts pair-warmup)" \
  env QWEN_EXPERIMENT_ID="$QWEN_EXPERIMENT_ID" QWEN_WARMUP_DEADLINE_EPOCH="$WARMUP_DEADLINE" \
    python3 "$BUNDLE/warm-topology.py" "${IPS[0]}" "$ART" \
  >"$ART/pair-warmup.log" 2>&1
# This replays semantic receipts and per-method observations; the helper's stdout marker is insufficient.
python3 "$BUNDLE/observer-gate.py" after-warmup "$ART" --experiment-id "$QWEN_EXPERIMENT_ID" \
  >"$ART/after-warmup-gate.json"
python3 "$BUNDLE/phase-marker.py" "$ART" warmup_end "$(date +%s)" "$WARMUP_DEADLINE"

CLIENT_START=$(date +%s)
CLIENT_DEADLINE=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" client "$CLIENT_START")
client_remaining=$(require_phase_time client)
python3 "$BUNDLE/phase-marker.py" "$ART" client_start "$(date +%s)" "$CLIENT_DEADLINE"
timeout --signal=TERM --kill-after=10s "${client_remaining}s" \
  /bin/bash -c 'srun "$@"' qwen-token-client --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
    --container-image="$SGLANG" --container-mounts="$(mounts token-client)" \
    env QWEN_EXPERIMENT_ID="$QWEN_EXPERIMENT_ID" QWEN_BUNDLE="$BUNDLE" QWEN_BENCHMARK_DEADLINE="$CLIENT_DEADLINE" \
      bash "$BUNDLE/token-client.sh" "${IPS[0]}:8000" "$MODEL" "$ART"
python3 "$BUNDLE/phase-marker.py" "$ART" client_end "$(date +%s)" "$CLIENT_DEADLINE"

HEAD_START=$(date +%s)
HEAD_DEADLINE=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" head "$HEAD_START")
require_phase_time head >/dev/null
python3 "$BUNDLE/phase-marker.py" "$ART" head_gate_start "$(date +%s)" "$HEAD_DEADLINE"
python3 "$BUNDLE/check-token-result.py" "$ART/token-control.json" >"$ART/head-token-gate.log" 2>&1
python3 "$BUNDLE/observer-gate.py" after-warmup "$ART" --experiment-id "$QWEN_EXPERIMENT_ID" \
  >"$ART/head-observer-gate.json"
python3 "$BUNDLE/phase-marker.py" "$ART" correctness_candidate_pass "$(date +%s)" 'exact-1600-ID-reference-match'
python3 "$BUNDLE/phase-marker.py" "$ART" head_gate_end "$(date +%s)" "$HEAD_DEADLINE"
echo 'EAGLE3_EXACT_ID_CORRECTNESS_PASS (unranked; no AIPerf score)' | tee "$ART/CONTROLLER_PASS.txt"
