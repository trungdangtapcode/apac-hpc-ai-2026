#!/bin/bash
#SBATCH -J ap42-s10-prefill-tp8ep2-equal-n56
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --exclusive
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-tp8ep2-equal-n56
export QWEN_PREFILL_EP=2
export QWEN_PAIR_TIMEOUT=480
export QWEN_TUNE_NS=56
export QWEN_DIAGNOSTIC_PROFILE=0
export QWEN_NIXL_PATCH_SHA256=e979738ef1681b793b09e3b81d2d4e4563535c1a354bf2e7ac76da14f73c856c
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
exec bash "$QWEN_BUNDLE/topology-job.sh"
