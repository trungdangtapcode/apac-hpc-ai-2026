#!/bin/bash
#SBATCH -J ap42-fp8-workbind
#SBATCH -p hpcai
#SBATCH -N 1
#SBATCH --gres=gpu:8
#SBATCH --cpus-per-task=64
#SBATCH --exclusive
#SBATCH -t 00:10:00
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
ROOT=$SLURM_SUBMIT_DIR
BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s25-fp8-workbind
ART=$ROOT/runs/$SLURM_JOB_ID
private_home=$ROOT/home/$SLURM_JOB_ID/fp8-micro
mkdir -p "$ART/submitted" "$ART/micro" "$private_home"
chmod 700 "$private_home"
cp "$BUNDLE"/* "$ART/submitted/"
cd "$ART/submitted"
sha256sum --check SHA256SUMS
srun --exact -N1 -n1 --gres=gpu:8 --cpus-per-task=64 --container-image=/scratch/enroot-images/sglang-harbor.sqsh --container-workdir=/work --container-mounts="$ART:/work,$private_home:$HOME" bash /work/submitted/run-micro.sh /work/micro
