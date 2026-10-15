#!/bin/bash -l
set -euo pipefail
BUNDLE=$1
ART=$2
NODE=$(hostname -s)
exec >"$ART/$NODE.log" 2>&1
hostname
date -u +%FT%TZ
printf 'CUDA_VISIBLE_DEVICES=%s\n' "${CUDA_VISIBLE_DEVICES:-unset}"
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total --format=csv,noheader
nvidia-smi topo -m
for nic in /sys/class/infiniband/*; do
  [[ -d $nic ]] || continue
  printf '%s ' "$(basename "$nic")"
  cat "$nic/ports/1/link_layer" "$nic/ports/1/state"
done
module load singularity/4.1.5
singularity --version
# Full exclusive nodes: use node-local ordinals rather than UUIDs inherited
# from the first PBS node through pbsdsh.
export SINGULARITYENV_CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export SINGULARITYENV_PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export SINGULARITYENV_LD_LIBRARY_PATH=/.singularity.d/libs:/usr/local/cuda/lib64:/usr/local/lib
export SINGULARITYENV_PYTHONNOUSERSITE=1
timeout 180 singularity exec --nv --cleanenv --no-home --bind /scratch,/app \
  /app/apps/containers/pytorch/pytorch-nvidia-24.10-py3.sqsh \
  /usr/bin/env PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  LD_LIBRARY_PATH=/.singularity.d/libs:/usr/local/nvidia/lib64:/usr/local/nvidia/lib:/usr/local/cuda/lib64:/usr/local/lib \
  CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 PYTHONNOUSERSITE=1 \
  python3 "$BUNDLE/probe-torch.py" "$ART/$NODE.gpu.json"
