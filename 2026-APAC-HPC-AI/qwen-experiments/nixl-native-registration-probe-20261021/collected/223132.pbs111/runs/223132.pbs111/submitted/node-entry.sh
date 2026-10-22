#!/bin/bash -l
set -euo pipefail
rank=$1
bundle=$2
art=$3
exchange=$4
module load singularity/4.1.5
image=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/sglang-harbor.sqsh
allocation_gpu=${CUDA_VISIBLE_DEVICES:?PBS must supply a task GPU allocation mask}
[[ "$allocation_gpu" != *,* && "$allocation_gpu" != *" "* ]]
private_tmp=$(mktemp -d "${TMPDIR:-/tmp}/ap42-native-kv.XXXXXXXX")
printf 'TASK_START utc=%s host=%s rank=%s allocated_gpu=%s\n' "$(date -u +%FT%TZ)" "$(hostname)" "$rank" "$allocation_gpu"
# Preserve the allocated UUID/index: do not replace a partial-node assignment
# with a hard-coded physical GPU index. The probe verifies exactly one device.
timeout --signal=TERM --kill-after=10s 510s singularity exec --nv --cleanenv --no-home \
  --bind "/scratch:/scratch,$private_tmp:/tmp,$bundle/nixl-conn.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py:ro" \
  "$image" /usr/bin/env \
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  LD_LIBRARY_PATH=/.singularity.d/libs:/usr/local/nvidia/lib64:/usr/local/nvidia/lib:/usr/local/cuda/lib64:/usr/local/lib \
  CUDA_VISIBLE_DEVICES="$allocation_gpu" \
  OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
  TOKIO_WORKER_THREADS=1 RAYON_NUM_THREADS=1 \
  HOME=/tmp/ap42-home HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  NIXL_LOG_LEVEL=DEBUG UCX_LOG_LEVEL=info \
  bash "$bundle/entry.sh" "$rank" "$art" "$exchange"
