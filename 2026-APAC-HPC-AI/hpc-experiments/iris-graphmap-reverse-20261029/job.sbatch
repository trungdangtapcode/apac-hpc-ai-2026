#!/usr/bin/env bash
# Conditional native zyx graph-placement short screen; intentionally non-scored.
#SBATCH --job-name=tu-iris-gmap14r
#SBATCH --partition=iris
#SBATCH --account=rdmaworkshop
#SBATCH --qos=low
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH --gpus=0
#SBATCH --nodes=1
#SBATCH --ntasks=56
#SBATCH --time=00:50:00
#SBATCH --output=runs/%j.out
#SBATCH --error=runs/%j.err
set -euo pipefail
umask 077
ROOT=${SLURM_SUBMIT_DIR:?}
JOB=${SLURM_JOB_ID:?}
test -d "$ROOT/runs"
(cd "$ROOT" && sha256sum --check payload-sha256.txt)
module load gcc/11
module load hpcx/2.50
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
unset LD_PRELOAD LD_AUDIT
test -z "${LD_PRELOAD:-}"
test -z "${LD_AUDIT:-}"
export FOAM_CONFIG_MODE=o
set +euo pipefail
source /global/exafs/groups/rdmaworkshop/2026hpcai-openfoam/builds/iris-gcc11-hpcx250-opt/OpenFOAM-v2512/etc/bashrc
set -euo pipefail
: "${FOAM_APPBIN:?}"
{
    printf 'SLURM_JOB_ID=%s\n' "$JOB"
    printf 'SLURM_JOB_NODELIST=%s\n' "${SLURM_JOB_NODELIST:-<unset>}"
    printf 'SLURM_JOB_NUM_NODES=%s\n' "${SLURM_JOB_NUM_NODES:-<unset>}"
    printf 'SLURM_NTASKS=%s\n' "${SLURM_NTASKS:-<unset>}"
    printf 'SLURM_CPUS_ON_NODE=%s\n' "${SLURM_CPUS_ON_NODE:-<unset>}"
    printf 'SLURM_JOB_PARTITION=%s\n' "${SLURM_JOB_PARTITION:-<unset>}"
    printf 'SLURM_JOB_QOS=%s\n' "${SLURM_JOB_QOS:-<unset>}"
    date -u +'%Y-%m-%dT%H:%M:%SZ'
    hostname -f
    module list 2>&1
    mpirun --version
    mpicc --showme:command
    printf 'FOAM_CONFIG_MODE=%s\nFOAM_APPBIN=%s\nFOAM_LIBBIN=%s\nWM_PROJECT_VERSION=%s\nWM_PRECISION_OPTION=%s\n' \
        "$FOAM_CONFIG_MODE" "${FOAM_APPBIN:-<unset>}" "${FOAM_LIBBIN:-<unset>}" "${WM_PROJECT_VERSION:-<unset>}" "${WM_PRECISION_OPTION:-<unset>}"
    printf 'OMP_NUM_THREADS=%s\nOPENBLAS_NUM_THREADS=%s\nMKL_NUM_THREADS=%s\n' "$OMP_NUM_THREADS" "$OPENBLAS_NUM_THREADS" "$MKL_NUM_THREADS"
    printf 'LD_PRELOAD=%s\nLD_AUDIT=%s\n' "${LD_PRELOAD:-<unset>}" "${LD_AUDIT:-<unset>}"
} > "$ROOT/runs/$JOB-batch-runtime.txt"
cd "$ROOT"
timeout --signal=TERM --kill-after=15s 2970s python3 run.py
