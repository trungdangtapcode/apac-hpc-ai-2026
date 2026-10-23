#!/bin/bash
set -euo pipefail
rank=$1
bundle=$2
art=$3
exchange=$4
private_tmp=''
container_status=null
cleanup_task_tmp() {
  local status=$?
  trap - EXIT
  local cleanup_status=0 deleted=false
  if [[ -n "$private_tmp" && -d "$private_tmp" ]]; then
    timeout --signal=TERM --kill-after=1s 2s rm -rf -- "$private_tmp" || cleanup_status=$?
    if (( cleanup_status == 0 )); then deleted=true; else status=1; fi
  fi
  if ! timeout --signal=TERM --kill-after=1s 3s python3 -c '
import json,os,socket,sys,time
from pathlib import Path
p=Path(sys.argv[1]);tmp=p.with_suffix(".tmp")
v=dict(schema="node-exit-v1",rank=int(sys.argv[2]),host=socket.gethostname(),container_returncode=json.loads(sys.argv[3]),cleanup_returncode=int(sys.argv[4]),cleanup_deleted=json.loads(sys.argv[5]),final_returncode=int(sys.argv[6]),recorded_epoch_s=time.time())
tmp.write_text(json.dumps(v,indent=2)+"\n");tmp.replace(p)
' "$art/rank${rank}-node-exit.json" "$rank" "$container_status" "$cleanup_status" "$deleted" "$status"; then
    status=1
  fi
  printf 'NODE_EXIT rank=%s container=%s cleanup=%s final=%s\n' "$rank" "$container_status" "$cleanup_status" "$status"
  exit "$status"
}
trap cleanup_task_tmp EXIT
# Nonlogin shells avoid account logout hooks; bootstrap only the required module.
if ! declare -F module >/dev/null; then
  source /cm/local/apps/environment-modules/4.5.3/init/bash
fi
module load singularity/4.1.5
image=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/sglang-harbor.sqsh
allocation_gpu=${CUDA_VISIBLE_DEVICES:?PBS must supply a task GPU allocation mask}
[[ "$allocation_gpu" != *,* && "$allocation_gpu" != *" "* ]]
private_tmp=$(mktemp -d "${TMPDIR:-/tmp}/ap42-exit-boundary.XXXXXXXX")
printf 'TASK_START utc=%s host=%s rank=%s allocated_gpu=%s\n' "$(date -u +%FT%TZ)" "$(hostname)" "$rank" "$allocation_gpu"
t0=$(python3 -c 'import json,sys; print(int(json.load(open(sys.argv[1]))["t0_epoch_s"]))' "$exchange/component-start.json")
remaining=$(( t0 + 535 - $(date +%s) ))
(( remaining > 0 )) || { echo 'T0+535 reached before container launch' >&2; exit 1; }
set +e
timeout --signal=TERM --kill-after=2s "${remaining}s" singularity exec --nv --cleanenv --no-home \
  --bind "/scratch:/scratch,$private_tmp:/tmp,$bundle/nixl-conn.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py:ro" \
  "$image" /usr/bin/env \
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  LD_LIBRARY_PATH=/.singularity.d/libs:/usr/local/nvidia/lib64:/usr/local/nvidia/lib:/usr/local/cuda/lib64:/usr/local/lib \
  CUDA_VISIBLE_DEVICES="$allocation_gpu" \
  OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
  TOKIO_WORKER_THREADS=1 RAYON_NUM_THREADS=1 \
  HOME=/tmp/ap42-home HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  NIXL_LOG_LEVEL=INFO UCX_LOG_LEVEL=info \
  bash "$bundle/entry.sh" "$rank" "$art" "$exchange"
container_status=$?
set -e
exit "$container_status"
