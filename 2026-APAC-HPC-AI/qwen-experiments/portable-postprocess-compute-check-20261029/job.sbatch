#!/usr/bin/env bash
#SBATCH -J ap42-reader-alias
#SBATCH -p hpcai
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:0
#SBATCH -t 00:02:00
#SBATCH -o /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/%j.out
#SBATCH -e /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/%j.err
set -euo pipefail
D=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/portable-postprocess-compute-check-20261029
cd "$D"
sha256sum --check SHA256SUMS
srun --exact --gres=gpu:0 -n1 --cpus-per-task=2 python3 -B "$D/check.py"
