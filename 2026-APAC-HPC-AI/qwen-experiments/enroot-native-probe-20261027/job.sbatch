#!/bin/bash
#SBATCH -J ap42-enroot-native
#SBATCH -p hpcai
#SBATCH -N 1
#SBATCH --nodelist=g1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH -t 00:04:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
srun --exact bash /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/enroot-native-probe-20261027/probe.sh
