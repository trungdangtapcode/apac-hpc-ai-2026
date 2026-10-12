#!/bin/bash
#SBATCH -J ap42-fix-02-confirm
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/02-P8-TP2_D8-TP4-EP4-a2-confirm
export QWEN_PREFILL_EP=1
export QWEN_PAIR_TIMEOUT=480
export QWEN_SWEEP_NS=48
export QWEN_CONFIRM_ONLY=1
export QWEN_CONFIRM_N=48
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
exec bash "$QWEN_BUNDLE/topology-job.sh"
