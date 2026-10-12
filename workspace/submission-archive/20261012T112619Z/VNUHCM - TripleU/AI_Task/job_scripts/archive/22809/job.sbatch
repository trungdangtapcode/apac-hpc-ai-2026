#!/bin/bash
#SBATCH -J ap42-fix-11-sweep
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/11-P8-TP8-EP2_D8-TP8-EP8-a5-sweep
export QWEN_PREFILL_EP=2
export QWEN_PAIR_TIMEOUT=480
export QWEN_SWEEP_NS='16 32 40 48'
export QWEN_NIXL_PATCH_SHA256=e979738ef1681b793b09e3b81d2d4e4563535c1a354bf2e7ac76da14f73c856c
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
exec bash "$QWEN_BUNDLE/topology-job.sh"
