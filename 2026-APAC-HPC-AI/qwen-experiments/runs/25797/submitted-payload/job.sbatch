#!/bin/bash
# Derived EAGLE3 exact-output diagnostic; no score or speedup claim.
#SBATCH -J ap42-s43-h200-eagle3-geometry-repair
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
export QWEN_BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s43-h200-eagle3-geometry-repair
export QWEN_EXPERIMENT_ID="eagle3-h200-geometry-repair-${SLURM_JOB_ID}-$(cat /proc/sys/kernel/random/uuid)"
export QWEN_NIXL_PATCH_SHA256=45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
mkdir -p "$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID"
python3 -B "$QWEN_BUNDLE/preflight-assets.py" >"$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID/asset-preflight.json"
exec bash topology-job.sh
