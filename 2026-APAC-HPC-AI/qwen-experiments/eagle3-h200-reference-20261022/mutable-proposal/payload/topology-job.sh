#!/usr/bin/env bash
set -euo pipefail
ROOT=$SLURM_SUBMIT_DIR
BUNDLE=$QWEN_BUNDLE
ART=$ROOT/runs/$SLURM_JOB_ID
export QWEN_ARTDIR=$ART
SGLANG=${QWEN_IMAGE_PATH:-/scratch/enroot-images/sglang-harbor.sqsh}
MODEL=/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8
T0=${QWEN_JOB_START_EPOCH:-$(date +%s)}
STARTUP_DEADLINE=$((T0+600))
WARMUP_DEADLINE=$((STARTUP_DEADLINE+120))
CLIENT_DEADLINE=$((WARMUP_DEADLINE+210))
CHECK_DEADLINE=$((CLIENT_DEADLINE+20))
TEARDOWN_DEADLINE=$((CHECK_DEADLINE+40))
HARD_STOP=$((T0+1020))
export QWEN_EXPERIMENT_ID QWEN_CLIENT_DEADLINE_EPOCH=$CLIENT_DEADLINE
mkdir -p "$ART"
cp -a "$BUNDLE" "$ART/submitted-payload"
printf 'job=%s\nexperiment_id=%s\nstarted_epoch=%s\nstartup_deadline_epoch=%s\nwarmup_deadline_epoch=%s\nclient_deadline_epoch=%s\ncheck_deadline_epoch=%s\nhard_stop_epoch=%s\n' \
  "$SLURM_JOB_ID" "$QWEN_EXPERIMENT_ID" "$T0" "$STARTUP_DEADLINE" "$WARMUP_DEADLINE" "$CLIENT_DEADLINE" "$CHECK_DEADLINE" "$HARD_STOP" >"$ART/deadlines.txt"
NODES=($(scontrol show hostnames "$SLURM_JOB_NODELIST"))
[[ ${#NODES[@]} == 2 ]] || { echo 'FATAL: expected exactly two nodes' >&2; exit 1; }
IPS=()
for host in "${NODES[@]}"; do IPS+=("$(getent ahostsv4 "$host" | awk 'NR==1 {print $1}')"); done
[[ -n ${IPS[0]} && -n ${IPS[1]} ]] || { echo 'FATAL: failed to resolve node addresses' >&2; exit 1; }
pids=()
cleanup() {
  local result=$?
  local cleanup_deadline
  trap - EXIT
  cleanup_deadline=$(($(date +%s)+40))
  (( cleanup_deadline > TEARDOWN_DEADLINE )) && cleanup_deadline=$TEARDOWN_DEADLINE
  (( cleanup_deadline > HARD_STOP )) && cleanup_deadline=$HARD_STOP
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || :; done
  while (( $(date +%s) < cleanup_deadline )); do
    live=0
    for pid in "${pids[@]}"; do
      if [[ -r /proc/$pid/stat ]] && [[ $(awk '{print $3}' "/proc/$pid/stat") != Z ]]; then live=1; fi
    done
    (( live == 0 )) && break
    sleep 1
  done
  for pid in "${pids[@]}"; do kill -9 "$pid" 2>/dev/null || :; done
  wait || :
  if (( $(date +%s) > cleanup_deadline )); then echo 'FATAL: bounded teardown deadline exceeded' >&2; result=1; fi
  if (( $(date +%s) >= HARD_STOP )); then echo 'FATAL: absolute 1020-second hard stop reached' >&2; result=1; fi
  exit "$result"
}
step_alive() {
  local pid=$1
  [[ -r /proc/$pid/stat ]] && [[ $(awk '{print $3}' "/proc/$pid/stat") != Z ]]
}
trap cleanup EXIT
mounts() { echo "/scratch:/scratch,$ROOT/home/$SLURM_JOB_ID/$1:$HOME,$ROOT,$BUNDLE/nixl-conn.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py:ro"; }
: >"$ART/endpoints.tsv"
expected_placement=$'prefill-0\t0\t4\t30100\t9000\nprefill-1\t0\t4\t30101\t9001\ndecode-0\t1\t8\t30200\t0'
actual_placement=$(cat "$BUNDLE/placement.tsv")
[[ "$actual_placement" == "$expected_placement" ]] || {
  echo 'FATAL: placement differs from the reviewed two-prefill TP4 / one-decode TP8 layout' >&2; exit 1;
}
router_args=()
while read -r name node tp port bootstrap; do
  [[ "$node" =~ ^[01]$ && "$tp" =~ ^[48]$ ]] || { echo "FATAL: invalid placement row $name" >&2; exit 1; }
  role=${name%%-*}; nccl_port=$((20000+port-30100))
  if [[ $role == prefill ]]; then
    extra=(--disaggregation-bootstrap-port "$bootstrap")
    router_args+=(--prefill "http://${IPS[$node]}:$port" "$bootstrap")
  elif [[ $role == decode ]]; then
    extra=(--ep-size "$tp" --max-running-requests 256)
    router_args+=(--decode "http://${IPS[$node]}:$port")
  else echo "FATAL: unknown role $role" >&2; exit 1; fi
  printf '%s\t%s\t%s\n' "$name" "http://${IPS[$node]}:$port" "$bootstrap" >>"$ART/endpoints.tsv"
  mkdir -p "$ROOT/home/$SLURM_JOB_ID/$name"
  srun --exact -N1 -n1 -w "${NODES[$node]}" --cpu-bind=cores --gres="gpu:$tp" --cpus-per-task="$((tp*8))" \
    --container-image="$SGLANG" --container-mounts="$(mounts "$name")" \
    env QWEN_NIXL_PATCH_SHA256="$QWEN_NIXL_PATCH_SHA256" QWEN_ARTDIR="$ART" QWEN_BUNDLE="$BUNDLE" \
    QWEN_EXPERIMENT_ID="$QWEN_EXPERIMENT_ID" QWEN_CLIENT_DEADLINE_EPOCH="$CLIENT_DEADLINE" QWEN_IMAGE_PATH="$SGLANG" \
    QWEN_TELEMETRY_MAX_S="$((TEARDOWN_DEADLINE-$(date +%s)))" \
    bash "$BUNDLE/worker.sh" "$name" "$port" "$MODEL" "$tp" --nccl-port "$nccl_port" "${extra[@]}" \
    >"$ART/$name.log" 2>&1 &
  pids+=("$!")
done <"$BUNDLE/placement.tsv"
[[ $(wc -l <"$ART/endpoints.tsv") == 3 ]] || { echo 'FATAL: expected two prefill and one decode worker' >&2; exit 1; }
wait_http() {
  local url=$1
  while (( $(date +%s) < STARTUP_DEADLINE )); do
    for pid in "${pids[@]}"; do step_alive "$pid" || { echo "FATAL: worker/router step $pid exited" >&2; return 1; }; done
    curl -sf --max-time 2 -o /dev/null "$url" && return 0
    sleep 2
  done
  echo "FATAL: shared 600-second startup deadline expired at $url" >&2; return 1
}
while IFS=$'\t' read -r name url bootstrap; do
  wait_http "$url/health"
  python3 "$BUNDLE/check-kv-ranks.py" "$ART/$name.log" "$name"
  python3 "$BUNDLE/phase-marker.py" "$ART" worker_ready "$name" "$(date +%s)"
done <"$ART/endpoints.tsv"
mkdir -p "$ROOT/home/$SLURM_JOB_ID/router"
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts router)" \
  env QWEN_EXPERIMENT_ID="$QWEN_EXPERIMENT_ID" QWEN_CLIENT_DEADLINE_EPOCH="$CLIENT_DEADLINE" QWEN_IMAGE_PATH="$SGLANG" \
  python3 -m sglang_router.launch_router --pd-disaggregation --prefill-policy round_robin "${router_args[@]}" \
    --host 0.0.0.0 --port 8000 --prometheus-port 29000 >"$ART/router.log" 2>&1 &
pids+=("$!")
wait_http "http://${IPS[0]}:8000/health"
(( $(date +%s) < STARTUP_DEADLINE )) || { echo 'FATAL: startup exceeded 600 seconds' >&2; exit 1; }
echo "ALL_WORKERS_READY at=$(date +%s)"
python3 "$BUNDLE/phase-marker.py" "$ART" all_workers_ready "$(date +%s)"
mkdir -p "$ROOT/home/$SLURM_JOB_ID/pair-warmup"
set +e
timeout --signal=TERM --kill-after=5s 120 srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts pair-warmup)" \
  env QWEN_EXPERIMENT_ID="$QWEN_EXPERIMENT_ID" QWEN_CLIENT_DEADLINE_EPOCH="$CLIENT_DEADLINE" QWEN_IMAGE_PATH="$SGLANG" QWEN_WARMUP_DEADLINE_EPOCH="$WARMUP_DEADLINE" \
    python3 "$BUNDLE/warm-topology.py" "${IPS[0]}" "$ART" >"$ART/pair-warmup.log" 2>&1
warm_status=$?
set -e
if (( warm_status != 0 )) || ! grep -q '^ALL 2 P/D paths semantically initialized ' "$ART/pair-warmup.log"; then
  echo "FATAL: semantic pair warmup failed status=$warm_status" >&2; exit 1
fi
(( $(date +%s) < CLIENT_DEADLINE )) || { echo 'FATAL: no client budget remains after warmup' >&2; exit 1; }
echo "ALL_PAIRS_WARM at=$(date +%s)"
python3 "$BUNDLE/phase-marker.py" "$ART" all_pairs_warm "$(date +%s)"
python3 "$BUNDLE/phase-marker.py" "$ART" target_reference_start "$(date +%s)"
set +e
timeout --signal=TERM --kill-after=5s 210 srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts token-client)" \
  env QWEN_EXPERIMENT_ID="$QWEN_EXPERIMENT_ID" QWEN_CLIENT_DEADLINE_EPOCH="$CLIENT_DEADLINE" QWEN_IMAGE_PATH="$SGLANG" \
  python3 "$BUNDLE/token-control.py" "${IPS[0]}:8000" "$MODEL" "$ART" >"$ART/token-client.log" 2>&1
client_status=$?
set -e
python3 "$BUNDLE/phase-marker.py" "$ART" target_reference_end "$(date +%s)" "client_status=$client_status"
set +e
check_timeout=$((CHECK_DEADLINE-$(date +%s)))
if (( check_timeout > 0 )); then
  timeout --signal=TERM --kill-after=2s "$check_timeout" \
    python3 "$BUNDLE/check-token-result.py" "$ART/target-reference.json" >"$ART/head-result-check.log" 2>&1
  check_status=$?
else
  echo 'FATAL: no head-check budget remains' >"$ART/head-result-check.log"
  check_status=124
fi
set -e
if (( client_status != 0 || check_status != 0 )); then
  echo "FATAL: token reference rejected client_status=$client_status head_check_status=$check_status" >&2
  exit 1
fi
(( $(date +%s) < CHECK_DEADLINE )) || { echo 'FATAL: result checks exceeded 20-second allocation' >&2; exit 1; }
(( $(date +%s) < HARD_STOP )) || { echo 'FATAL: hard stop exceeded 1020 seconds' >&2; exit 1; }
echo "TOKEN_REFERENCE_PASS at=$(date +%s)"
