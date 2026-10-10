#!/bin/bash
#SBATCH -J ap42-fix-04-sweep
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/04-P8-TP4_D8-TP8-EP8-a1-sweep
export QWEN_PREFILL_EP=1
export QWEN_PAIR_TIMEOUT=360
export QWEN_SWEEP_NS='16 32 40 48'
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
exec bash "$QWEN_BUNDLE/topology-job.sh"
