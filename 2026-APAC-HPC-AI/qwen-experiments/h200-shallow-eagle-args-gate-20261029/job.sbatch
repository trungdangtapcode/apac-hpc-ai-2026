#!/usr/bin/env bash
#SBATCH -J ap42-eagle12-args
#SBATCH -p hpcai
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH -t 00:04:00
#SBATCH -o /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/%j.out
#SBATCH -e /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/%j.err
set -euo pipefail
Q=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments
D=$Q/h200-shallow-eagle-args-gate-20261029
cd "$D"
sha256sum --check SHA256SUMS
mkdir -p "$Q/runs/$SLURM_JOB_ID"
srun --exact --gres=gpu:1 --cpus-per-task=8 bash "$Q/h200-kv-page-primitive-r2-20261028/native-container.sh" \
 /scratch/enroot-images/sglang-harbor.sqsh "/scratch:/scratch,$Q:$Q" \
 env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python3 -B "$D/probe.py"
