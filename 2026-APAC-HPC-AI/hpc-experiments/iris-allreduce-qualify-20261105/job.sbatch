#!/bin/bash
#SBATCH --job-name=tu-iris-allred
#SBATCH --partition=iris
#SBATCH --account=rdmaworkshop
#SBATCH --qos=low
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH --gpus=0
#SBATCH --nodes=1
#SBATCH --ntasks=56
#SBATCH --time=00:05:00
#SBATCH --output=%j.out
#SBATCH --error=%j.err
set -euo pipefail
ROOT=${SLURM_SUBMIT_DIR:?}
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset LD_PRELOAD LD_AUDIT
module load gcc/11
module load hpcx/2.50
export FOAM_CONFIG_MODE=o
set +euo pipefail
source /global/exafs/groups/rdmaworkshop/2026hpcai-openfoam/builds/iris-gcc11-hpcx250-opt/OpenFOAM-v2512/etc/bashrc
set -euo pipefail
: "${FOAM_APPBIN:?}"
{
  date -u
  hostname
  module list 2>&1
  printf 'FOAM_CONFIG_MODE=%s\nOMP_NUM_THREADS=%s\nOPENBLAS_NUM_THREADS=%s\nMKL_NUM_THREADS=%s\n' "$FOAM_CONFIG_MODE" "$OMP_NUM_THREADS" "$OPENBLAS_NUM_THREADS" "$MKL_NUM_THREADS"
  printf 'FOAM_APPBIN=%s\nWM_PROJECT_VERSION=%s\n' "$FOAM_APPBIN" "${WM_PROJECT_VERSION:-unknown}"
} > "$ROOT/runtime-environment.txt"
# The parent limits each MPI process to 30 seconds; reserve the remaining time for setup and cleanup.
sha256sum -c "$ROOT/payload-sha256.txt" > "$ROOT/payload-before.log"
timeout --signal=TERM --kill-after=5s 240s python3 "$ROOT/run.py"

sha256sum -c "$ROOT/payload-sha256.txt" > "$ROOT/payload-after.log"
