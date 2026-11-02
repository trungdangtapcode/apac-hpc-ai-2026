#!/usr/bin/env bash
set -euo pipefail
: "${SLURM_JOB_ID:?Submit submit.sbatch through Slurm}"
: "${SLURM_SUBMIT_DIR:?Missing Slurm submission directory}"
TASK_SCRIPTS=$SLURM_SUBMIT_DIR
TASK_ROOT=$(cd "$TASK_SCRIPTS/.." && pwd)
STUDY=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102
OLD_PROTOCOL=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/mmlu-pro-local-quality-20261024
ART="$TASK_ROOT/logs/reruns/$SLURM_JOB_ID"
SGLANG=${TRIPLEU_SGLANG_IMAGE:-/scratch/enroot-images/sglang-harbor.sqsh}
AIPERF=${TRIPLEU_AIPERF_IMAGE:-/scratch/enroot-images/aiperf.sqsh}
MODEL=${TRIPLEU_MODEL_PATH:-/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8}
mkdir -p "$ART"
(cd "$STUDY" && sha256sum --check frozen-pilot/SHA256SUMS) >"$ART/frozen-inputs-check.log"
JOB_START_EPOCH=${TRIPLEU_JOB_START_EPOCH:?submit.sbatch must set the immutable job-start epoch}
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
  local local_home="$TASK_ROOT/logs/.runtime-home/$SLURM_JOB_ID/$1"
  mkdir -p "$local_home"
  local patch_mount=""
  case "$1" in
    prefill-*|decode-*)
      patch_mount=",$TASK_SCRIPTS/nixl-conn.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py:ro"
      ;;
  esac
  printf '%s' "/scratch:/scratch,$local_home:$HOME,$TASK_ROOT:$TASK_ROOT,$STUDY:$STUDY,$OLD_PROTOCOL:$OLD_PROTOCOL:ro$patch_mount"
}
echo "START job=$SLURM_JOB_ID nodes=${NODES[*]} at $(date -Iseconds)"
cat "$ART/config.json"
printf 'sglang_image=%s\naiperf_image=%s\nmodel=%s\n' "$SGLANG" "$AIPERF" "$MODEL" >"$ART/runtime-paths.txt"
: >"$ART/endpoints.tsv"
router_args=()
while read -r name node tp port bootstrap; do
  role=${name%%-*}
  nccl_port=$((20000+port-30100))
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
    bash "$TASK_SCRIPTS/worker.sh" "$name" "$port" "$MODEL" "$tp" --nccl-port "$nccl_port" "${extra[@]}" \
    >"$ART/$name.log" 2>&1 &
  pids+=("$!")
done <"$TASK_SCRIPTS/placement.tsv"
wait_http() {
  local url=$1 deadline=$((JOB_START_EPOCH+600))
  while ! curl -sf --max-time 2 -o /dev/null "$url"; do
    for pid in "${pids[@]}"; do
      if ! kill -0 "$pid" 2>/dev/null; then
        echo "FATAL: worker/router step $pid exited before readiness" >&2; return 1
      fi
    done
    if (( $(date +%s)>=deadline )); then echo "FATAL: readiness timeout $url" >&2; return 1; fi
    sleep 2
  done
}
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

while read -r name url bootstrap; do wait_http "$url/health"; echo "READY $name after ${SECONDS}s"; done <"$ART/endpoints.tsv"
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts router)" \
  python3 -m sglang_router.launch_router --pd-disaggregation --prefill-policy round_robin "${router_args[@]}" \
    --host 0.0.0.0 --port 8000 --prometheus-port 29000 >"$ART/router.log" 2>&1 &
pids+=("$!")
wait_http "http://${IPS[0]}:8000/health"
wait_gateway_models "http://${IPS[0]}:8000/v1/models" "$ART/gateway-models.json"
echo "ALL_WORKERS_READY after ${SECONDS}s"
# Two independent semantic P/D warmups must pass before official scoring.
# The absolute deadline is measured from job start, leaving four minutes for
# the official workload and cleanup inside the 17-minute allocation.
WARMUP_DEADLINE=$(( JOB_START_EPOCH + 780 ))
EXPERIMENT_ID="tripleu-n64-${SLURM_JOB_ID}-$(date +%s)-$$"
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts pair-warmup)" \
  env QWEN_EXPERIMENT_ID="$EXPERIMENT_ID" QWEN_WARMUP_DEADLINE_EPOCH="$WARMUP_DEADLINE" \
  python3 "$TASK_SCRIPTS/warm-topology.py" "${IPS[0]}" "$ART" >"$ART/pair-warmup.log" 2>&1
python3 "$TASK_SCRIPTS/warmup_semantic.py" --check --endpoints "$ART/endpoints.tsv" \
  --receipt-dir "$ART/pair-warmup-receipts" \
  --run-token "$(python3 -c 'import hashlib,sys; print(hashlib.sha256(sys.argv[1].encode()).hexdigest()[:32])' "$EXPERIMENT_ID")" \
  >"$ART/pair-warmup-validation.json"
(( $(date +%s) - JOB_START_EPOCH <= 780 )) || { echo 'FATAL: semantic warmup exceeded the job-start deadline' >&2; exit 1; }
echo "ALL_PAIRS_SEMANTICALLY_WARM after ${SECONDS}s"
# Independent accuracy experiment: frozen paired MMLU-Pro pilot, not AIPerf scoring.
echo "QUALITY_PILOT_BEGIN after ${SECONDS}s"
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$AIPERF" --container-mounts="$(mounts quality-client)" \
  bash "$TASK_SCRIPTS/run-quality-client.sh" "http://${IPS[0]}:8000/v1" "$ART" "$JOB_START_EPOCH"
python3 "$STUDY/review_run_gate.py" "$ART/evaluation" >"$ART/measurement-validity.json"
echo "QUALITY_PILOT_COMPLETE after ${SECONDS}s at $(date -Iseconds)"
