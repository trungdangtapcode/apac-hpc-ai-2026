#!/bin/bash
#SBATCH --job-name=tu-numaqual
#SBATCH --account=rdmaworkshop
#SBATCH --partition=iris
#SBATCH --qos=low
#SBATCH --nodes=1
#SBATCH --ntasks=56
#SBATCH --gpus=0
#SBATCH --exclusive
#SBATCH --time=00:10:00
#SBATCH --output=%j.out
#SBATCH --error=%j.err
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
mkdir -p runs
exec timeout --signal=TERM --kill-after=10s 570s python3 qualify.py
