#!/bin/bash
#SBATCH -J ap42-enroot-audit
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH --nodelist=g1,g4
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:0
#SBATCH -t 00:02:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
srun --label bash /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/enroot-space-20261027/audit.sh
