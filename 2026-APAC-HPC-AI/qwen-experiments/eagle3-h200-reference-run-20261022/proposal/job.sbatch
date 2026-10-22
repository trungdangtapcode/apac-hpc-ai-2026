#!/bin/bash
# Draft only. Root review and fresh target/image identity checks required before freeze.
#SBATCH -J ap42-eagle3-h200-target-reference
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
export QWEN_RESOURCE_MONITOR=1
export QWEN_IMAGE_PATH=/scratch/enroot-images/sglang-harbor.sqsh
export QWEN_BUNDLE="$SLURM_SUBMIT_DIR/mutable-proposal/payload"
export QWEN_EXPERIMENT_ID="eagle3-h200-reference-${SLURM_JOB_ID}-$(cat /proc/sys/kernel/random/uuid)"
export QWEN_NIXL_PATCH_SHA256=912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f
cd "$QWEN_BUNDLE"
sha256sum --check SOURCE_SHA256SUMS
exec bash topology-job.sh
