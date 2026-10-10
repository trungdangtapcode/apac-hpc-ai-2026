#!/usr/bin/env bash
set -euo pipefail
: "${SLURM_JOB_ID:?Submit submit.sbatch through Slurm}"
: "${SLURM_SUBMIT_DIR:?Missing Slurm submission directory}"
TASK_SCRIPTS=$SLURM_SUBMIT_DIR
TASK_ROOT=$(cd "$TASK_SCRIPTS/.." && pwd)
ART="$TASK_ROOT/logs/reruns/$SLURM_JOB_ID"
SGLANG=${TRIPLEU_SGLANG_IMAGE:-/scratch/enroot-images/sglang-harbor.sqsh}
AIPERF=${TRIPLEU_AIPERF_IMAGE:-/scratch/enroot-images/aiperf.sqsh}
MODEL=${TRIPLEU_MODEL_PATH:-/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8}
mkdir -p "$ART"
cp -r "$TASK_SCRIPTS" "$ART/submitted"
cp "$TASK_SCRIPTS/config.json" "$ART/config.json"
mapfile -t NODES < <(scontrol show hostnames "$SLURM_JOB_NODELIST")
[[ ${#NODES[@]} == 2 ]] || { echo 'Exactly two nodes are required' >&2; exit 1; }
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
  local local_home="$TASK_ROOT/.runtime-home/$SLURM_JOB_ID/$1"
  mkdir -p "$local_home"
  printf '%s' "/scratch:/scratch,$local_home:$HOME,$TASK_ROOT:$TASK_ROOT"
}
echo "START job=$SLURM_JOB_ID nodes=${NODES[*]} at $(date -Iseconds)"
cat "$ART/config.json"
printf 'sglang_image=%s\naiperf_image=%s\nmodel=%s\n' "$SGLANG" "$AIPERF" "$MODEL" >"$ART/runtime-paths.txt"
: >"$ART/endpoints.tsv"
router_args=()
while read -r name node tp port bootstrap; do
  role=${name%%-*}
  if [[ $role == prefill ]]; then
    extra=(--disaggregation-bootstrap-port "$bootstrap")
    router_args+=(--prefill "http://${IPS[$node]}:$port" "$bootstrap")
  else
    extra=(--ep-size "$tp" --max-running-requests 256)
    router_args+=(--decode "http://${IPS[$node]}:$port")
  fi
  printf '%s\t%s\t%s\n' "$name" "http://${IPS[$node]}:$port" "$bootstrap" >>"$ART/endpoints.tsv"
  srun --exact -N1 -n1 -w "${NODES[$node]}" --gres="gpu:$tp" --cpus-per-task="$((tp*8))" \
    --container-image="$SGLANG" --container-mounts="$(mounts "$name")" \
    bash "$TASK_SCRIPTS/worker.sh" "$name" "$port" "$MODEL" "$tp" "${extra[@]}" \
    >"$ART/$name.log" 2>&1 &
  pids+=("$!")
done <"$TASK_SCRIPTS/placement.tsv"
wait_http() {
  local url=$1 deadline=$((SECONDS+600))
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
  python3 -m sglang_router.launch_router --pd-disaggregation "${router_args[@]}" \
    --host 0.0.0.0 --port 8000 --prometheus-port 29000 >"$ART/router.log" 2>&1 &
pids+=("$!")
wait_http "http://${IPS[0]}:8000/health"
curl -fsS "http://${IPS[0]}:8000/v1/models" >"$ART/gateway-models.json"
echo "ALL_WORKERS_READY after ${SECONDS}s"
# These are short, separate setup prompts, not the official dataset or seed.
# Every scored request still traverses the main gateway and a prefill/decode pair.
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts pair-warmup)" \
  env QWEN_PAIR_TIMEOUT=360 python3 "$TASK_SCRIPTS/warm-topology.py" "${IPS[0]}" "$ART" >"$ART/pair-warmup.log" 2>&1
echo "ALL_PAIRS_WARM after ${SECONDS}s"
# No parameter sweep in the declared job: run N40 once with the locked command.
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$AIPERF" --container-mounts="$(mounts aiperf)" \
  bash "$TASK_SCRIPTS/official-benchmark.sh" "${IPS[0]}:8000" "$ART" "$TASK_SCRIPTS"
python3 "$TASK_SCRIPTS/summarize.py" "$ART" >"$ART/summary.json"
echo "OFFICIAL_COMMAND_COMPLETE after ${SECONDS}s at $(date -Iseconds)"
