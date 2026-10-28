#!/usr/bin/env bash
#SBATCH -J ap42-token-cpu
#SBATCH -p hpcai
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:0
#SBATCH -t 00:05:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
Q=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments
B=$Q/h200-dynamic-tokenizer-20261028
mkdir -p "$Q/runs/$SLURM_JOB_ID"
srun --exact --gres=gpu:0 bash "$B/native-container.sh" /scratch/enroot-images/sglang-harbor.sqsh \
 "/scratch:/scratch,$Q:$Q" python3 -B "$B/probe.py"
