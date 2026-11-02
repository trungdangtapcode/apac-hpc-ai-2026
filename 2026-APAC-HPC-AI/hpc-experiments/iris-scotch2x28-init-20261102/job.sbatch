#!/bin/bash
#SBATCH -J tu-iris-sc228
#SBATCH -p iris
#SBATCH -A rdmaworkshop
#SBATCH --qos=low
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH --gpus=0
#SBATCH -N 1
#SBATCH -n 56
#SBATCH -t 00:30:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
ROOT=${SLURM_SUBMIT_DIR:?}
cd "$ROOT"
sha256sum -c payload-sha256.txt
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset LD_PRELOAD LD_AUDIT
{ date -u; hostname; lscpu; } > "$ROOT/runs/${SLURM_JOB_ID:?}-hardware.txt"
module load gcc/11
module load hpcx/2.50
export FOAM_CONFIG_MODE=o
set +euo pipefail
source /global/exafs/groups/rdmaworkshop/2026hpcai-openfoam/builds/iris-gcc11-hpcx250-opt/OpenFOAM-v2512/etc/bashrc
set -euo pipefail
: "${FOAM_APPBIN:?}" "${WM_PROJECT_DIR:?}"
timeout --signal=TERM --kill-after=15s 1740s python3 "$ROOT/init.py"
