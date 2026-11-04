#!/bin/bash
#SBATCH --job-name=tu-iris-prep40r
#SBATCH --partition=iris
#SBATCH --account=rdmaworkshop
#SBATCH --qos=low
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH --gpus=0
#SBATCH --nodes=1
#SBATCH --ntasks=56
#SBATCH --time=02:00:00
#SBATCH --output=%j.out
#SBATCH --error=%j.err
set -euo pipefail
ROOT=${SLURM_SUBMIT_DIR:?}
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset LD_PRELOAD LD_AUDIT
test -z "${LD_PRELOAD:-}"
test -z "${LD_AUDIT:-}"
mkdir -p "$ROOT/runs"
{ date -u; hostname; lscpu; } > "$ROOT/runs/${SLURM_JOB_ID:?}-hardware.txt"
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
  printf 'LD_PRELOAD=%s\nLD_AUDIT=%s\n' "${LD_PRELOAD:-<unset>}" "${LD_AUDIT:-<unset>}"
  env | sort | grep -E '^(FI_(OFI_RXM_USE_SRX|PROVIDER|PROVIDER_PATH|LOG_LEVEL)|MPICH_RANK_REORDER_METHOD|MPICH_RANK_REORDER_FILE|MPICH_RANK_ORDER|MPICH_SMP_SINGLE_COPY_MODE|PALS_CPU_BIND|UCX_NET_DEVICES|UCX_TLS|FOAM_CONFIG_MODE|FOAM_APPBIN|FOAM_LIBBIN|WM_PROJECT_VERSION|WM_PRECISION_OPTION|OMP_NUM_THREADS|OPENBLAS_NUM_THREADS|MKL_NUM_THREADS)=' || true
} > "$ROOT/runs/${SLURM_JOB_ID}-runtime-environment.txt"
timeout --signal=TERM --kill-after=5s 7190s python3 "$ROOT/run.py"
