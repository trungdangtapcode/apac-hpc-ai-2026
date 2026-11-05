#!/bin/bash
#SBATCH --job-name=tu-iris-rank40r
#SBATCH --partition=iris
#SBATCH --account=rdmaworkshop
#SBATCH --qos=low
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH --gpus=0
#SBATCH --nodes=1
#SBATCH --ntasks=56
#SBATCH --time=02:30:00
#SBATCH --output=runs/%j.out
#SBATCH --error=runs/%j.err
set -euo pipefail
ROOT=${SLURM_SUBMIT_DIR:?}
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset LD_PRELOAD LD_AUDIT FOAM_FILEHANDLER
: "${SLURM_JOB_ID:?}"
mkdir -p "$ROOT/runs"
{
  date -u
  hostname
  lscpu
} > "$ROOT/runs/${SLURM_JOB_ID}-hardware.txt"
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
  printf 'FOAM_CONFIG_MODE=%s\nWM_PROJECT_VERSION=%s\nWM_PRECISION_OPTION=%s\n' "$FOAM_CONFIG_MODE" "${WM_PROJECT_VERSION:-unknown}" "${WM_PRECISION_OPTION:-unknown}"
  printf 'FOAM_FILEHANDLER=%s\nOMP_NUM_THREADS=%s\nOPENBLAS_NUM_THREADS=%s\nMKL_NUM_THREADS=%s\n' "${FOAM_FILEHANDLER:-<unset>}" "$OMP_NUM_THREADS" "$OPENBLAS_NUM_THREADS" "$MKL_NUM_THREADS"
  printf 'LD_PRELOAD=%s\nLD_AUDIT=%s\n' "${LD_PRELOAD:-<unset>}" "${LD_AUDIT:-<unset>}"
} > "$ROOT/runs/${SLURM_JOB_ID}-runtime-environment.txt"
timeout --signal=TERM --kill-after=10s 8940s python3 "$ROOT/run.py"
