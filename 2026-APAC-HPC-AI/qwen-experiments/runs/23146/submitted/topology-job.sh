#!/usr/bin/env bash
set -euo pipefail
ROOT=$SLURM_SUBMIT_DIR
BUNDLE=$QWEN_BUNDLE
ART=$ROOT/runs/$SLURM_JOB_ID
SGLANG=/scratch/enroot-images/sglang-harbor.sqsh
AIPERF=/scratch/enroot-images/aiperf.sqsh
MODEL=/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8
mkdir -p "$ART"
cp -r "$BUNDLE" "$ART/submitted"
cp "$BUNDLE/worker.sh" "$ART/"
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
echo "START job=$SLURM_JOB_ID nodes=${NODES[*]} at $(date -Iseconds)"
cat "$BUNDLE/config.json"
: >"$ART/endpoints.tsv"
router_args=()
while read -r name node tp port bootstrap; do
  role=${name%%-*}
  # Distinct rendezvous ports avoid races in automatic ephemeral-port selection.
  nccl_port=$((20000+port-30100))
  if [[ $tp == 4 ]]; then extra=(--ep-size 1); else extra=(--ep-size 8); fi
  printf '%s\t%s\t%s\n' "$name" "http://${IPS[$node]}:$port" "$bootstrap" >>"$ART/endpoints.tsv"
  srun --exact -N1 -n1 -w "${NODES[$node]}" --gres="gpu:$tp" --cpus-per-task="$((tp*8))" \
    --container-image="$SGLANG" --container-mounts="$(mounts "$name")" \
    bash "$ART/worker.sh" "$name" "$port" "$MODEL" "$tp" --nccl-port "$nccl_port" "${extra[@]}" \
    >"$ART/$name.log" 2>&1 &
  pids+=("$!")
done <"$BUNDLE/placement.tsv"
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

remaining=$((1020-SECONDS-40))
if ((remaining<120)); then echo "FATAL: insufficient time for output diagnostics" >&2; exit 1; fi
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts diagnostic-client)" \
  timeout "$remaining" python3 "$BUNDLE/output-diagnostic.py" \
  --endpoints "${IPS[0]}:30100" "${IPS[0]}:30101" "${IPS[1]}:30200" \
  --smoke-source "$BUNDLE/output-smoke.py" --output "$ART" >"$ART/output-diagnostic.log" 2>&1
echo "OUTPUT_DIAGNOSTIC_COMPLETE after ${SECONDS}s at $(date -Iseconds)"
