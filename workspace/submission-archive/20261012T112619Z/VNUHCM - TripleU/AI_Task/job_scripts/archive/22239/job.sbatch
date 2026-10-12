#!/bin/bash
#SBATCH -J ap42-P4-TP2_D12-TP2-EP2
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/12-P4-TP2_D12-TP2-EP2
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
exec bash "$QWEN_BUNDLE/topology-job.sh"
