#!/bin/bash
#SBATCH --job-name=qfc04
#SBATCH --partition=hpcai
#SBATCH --nodes=2
#SBATCH --time=00:17:00
#SBATCH --gres=gpu:8
#SBATCH --exclusive
#SBATCH --propagate=NONE
#SBATCH --output=../logs/full-shards-slurm/%j.out
#SBATCH --error=../logs/full-shards-slurm/%j.err
set -euo pipefail
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export TRIPLEU_JOB_START_EPOCH=$(date +%s)
# Run setup.sh first, then submit from AI_Task/job_scripts (or use --chdir).
TASK_SCRIPTS=${SLURM_SUBMIT_DIR:?Submit this script through Slurm}
cd "$TASK_SCRIPTS"
sha256sum --check SHA256SUMS
export TRIPLEU_QUALITY_CONCURRENCY=64
export TRIPLEU_QUALITY_SHARD_INDEX=4
export TRIPLEU_QUALITY_SHARD_COUNT=8
export QWEN_NIXL_PATCH_SHA256=912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f
exec bash "$TASK_SCRIPTS/deploy-quality.sh"
