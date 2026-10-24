#!/bin/bash
# One-GPU native FP8 KV compatibility primitive; no model and no performance claim.
# The submit controller and final package manifest are maintained by the parent.
#SBATCH -J ap42-fp8kv-h200-primitive
#SBATCH -p hpcai
#SBATCH -N 1
#SBATCH -t 00:10:00
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail

ROOT=$SLURM_SUBMIT_DIR
BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-kv-h200-primitive-20261023
ART=$BUNDLE/runs/$SLURM_JOB_ID
PRIVATE_HOME=$ROOT/home/$SLURM_JOB_ID/fp8-kv-primitive
IMAGE=/scratch/enroot-images/sglang-harbor.sqsh
(cd "$BUNDLE" && sha256sum --check SHA256SUMS)
mkdir -p "$ART" "$PRIVATE_HOME"
chmod 700 "$PRIVATE_HOME"

[[ -r "$IMAGE" ]] || { echo "FATAL: pinned image missing: $IMAGE" >&2; exit 1; }
[[ -r "$BUNDLE/primitive.py" ]] || { echo "FATAL: primitive payload missing" >&2; exit 1; }
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export QWEN_FP8KV_ARTIFACT_DIR=$ART

# Bound the container stage to 480 s, leaving two minutes inside the 600 s job
# for Slurm/container teardown and output flush. The assigned CUDA mask is passed
# through unchanged; the Python preflight requires exactly one visible H200.
timeout --signal=TERM --kill-after=10s 480s \
  srun --exact -N1 -n1 --gres=gpu:1 --cpus-per-task=4 \
    --container-image="$IMAGE" \
    --container-workdir=/work \
    --container-mounts="$BUNDLE:/bundle:ro,$ART:/work,$PRIVATE_HOME:$HOME" \
    python3 -B /bundle/primitive.py --output /work/result.json
