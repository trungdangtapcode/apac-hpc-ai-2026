#!/bin/bash
#SBATCH --job-name=tu-iris-rankfile
#SBATCH --partition=iris
#SBATCH --account=rdmaworkshop
#SBATCH --qos=low
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH --gpus=0
#SBATCH --nodes=1
#SBATCH --ntasks=56
#SBATCH --time=00:05:00
#SBATCH --output=runs/%j.out
#SBATCH --error=runs/%j.err
set -euo pipefail
ROOT=${SLURM_SUBMIT_DIR:?}
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset LD_PRELOAD LD_AUDIT FOAM_FILEHANDLER
: "${SLURM_JOB_ID:?}"
mkdir -p "$ROOT/runs"
module load gcc/11
module load hpcx/2.50
{
  date -u
  hostname
  lscpu
  module list 2>&1
  printf 'mpirun=%s\n' "$(command -v mpirun)"
  mpirun --version 2>&1
  printf 'python=%s\n' "$(command -v python3)"
} > "$ROOT/runs/${SLURM_JOB_ID}-module-environment.txt"
timeout --signal=TERM --kill-after=10s 240s python3 "$ROOT/run_probes.py"
