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
timeout 180 singularity exec --nv --bind /scratch,/app \
  /app/apps/containers/pytorch/pytorch-nvidia-24.10-py3.sqsh \
  python3 "$BUNDLE/probe-torch.py" "$ART/$NODE.gpu.json"
