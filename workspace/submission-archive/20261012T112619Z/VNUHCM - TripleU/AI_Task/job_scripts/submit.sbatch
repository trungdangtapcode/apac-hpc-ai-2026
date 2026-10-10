#!/bin/bash
#SBATCH --job-name=TripleU-Qwen-Basic
#SBATCH --partition=hpcai
#SBATCH --nodes=2
#SBATCH --time=00:17:00
#SBATCH --gres=gpu:8
#SBATCH --propagate=NONE
#SBATCH --output=../logs/slurm/%j.out
#SBATCH --error=../logs/slurm/%j.err
set -euo pipefail

# Submit from AI_Task/job_scripts, or pass that directory using sbatch --chdir.
# SLURM_SUBMIT_DIR is used because Slurm executes a spooled copy of this file.
TASK_SCRIPTS=$SLURM_SUBMIT_DIR
test -f "$TASK_SCRIPTS/deploy-and-benchmark.sh"
cd "$TASK_SCRIPTS"
sha256sum --check SHA256SUMS
export TRIPLEU_CONCURRENCY=40
exec bash "$TASK_SCRIPTS/deploy-and-benchmark.sh"
