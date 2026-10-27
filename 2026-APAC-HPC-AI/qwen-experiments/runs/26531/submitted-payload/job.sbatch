#!/bin/bash
# Prospective unranked S59/S60 matched fast-default performance arm; no official quality claim.
#SBATCH -J ap42-s80-local
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --exclusive
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_JOB_START_EPOCH=$(date +%s)
export ENROOT_DATA_PATH="/tmp/apacsc42-enroot-${SLURM_JOB_ID}"
srun --exact -N2 -n2 --ntasks-per-node=1 --gres=gpu:0 --cpus-per-task=1 bash -c '
  set -euo pipefail
  umask 077
  path=${ENROOT_DATA_PATH:?}
  [[ ! -L "$path" ]] || exit 1
  if [[ -e "$path" ]]; then
    [[ -d "$path" && $(stat -c %u "$path") == $(id -u) ]] || exit 1
  else
    mkdir -m 700 "$path"
  fi
  read -r block_size free_blocks < <(stat -f -c "%S %a" "$path")
  (( block_size * free_blocks >= 256 * 1024 * 1024 * 1024 )) || { echo "FATAL: insufficient local NVMe for container roots" >&2; exit 1; }
  printf "ENROOT_LOCAL_STORAGE_READY host=%s path=%s free_bytes=%s\n" "$(hostname)" "$path" "$((block_size*free_blocks))"
'

export QWEN_RESOURCE_MONITOR=1
export QWEN_PREFILL_POLICY=round_robin
export QWEN_IMAGE_PATH=/scratch/enroot-images/sglang-harbor.sqsh
export QWEN_BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-11/s80-h200-local-enroot-control
export QWEN_EXPERIMENT_ID="s80-h200-local-enroot-control-${SLURM_JOB_ID}-$(cat /proc/sys/kernel/random/uuid)"
export QWEN_NIXL_PATCH_SHA256=45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8
export QWEN_HAS_DRAFT=0
export QWEN_DRAFT_PATH=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09
export QWEN_DRAFT_FULL_VERIFICATION="$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID/draft-full-verification.json"
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
mkdir -p "$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID"
python3 -B "$QWEN_BUNDLE/check-client-image.py" >"$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID/client-image-preflight.json"
python3 -B "$QWEN_BUNDLE/preflight-assets.py" >"$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID/asset-preflight.json"
exec bash topology-job.sh
