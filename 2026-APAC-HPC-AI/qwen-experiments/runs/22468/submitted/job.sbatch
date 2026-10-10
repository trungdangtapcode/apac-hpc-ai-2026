#!/bin/bash
#SBATCH -J ap42-fix-10-sweep
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/10-P8-TP8-EP2_D8-TP2-EP2-a1-sweep
export QWEN_PREFILL_EP=2
export QWEN_PAIR_TIMEOUT=360
export QWEN_SWEEP_NS='16 32 40 48'
export QWEN_NIXL_PATCH_SHA256=912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
exec bash "$QWEN_BUNDLE/topology-job.sh"
