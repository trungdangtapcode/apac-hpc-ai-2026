#!/bin/bash
#SBATCH -J tu-iris-hs150
#SBATCH -p iris
#SBATCH -A rdmaworkshop
#SBATCH -N 1
#SBATCH -n 56
#SBATCH --qos=low
#SBATCH --mem=0
#SBATCH --exclusive
#SBATCH -t 02:30:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
START_EPOCH=$(date +%s)
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

SHARED=/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam
BUILD="$SHARED/builds/iris-gcc11-hpcx250-opt"
BASHRC="$BUILD/OpenFOAM-v2512/etc/bashrc"
ROOT="${SLURM_SUBMIT_DIR:?}"
WORK="$(cd "$ROOT/.." && pwd)"
RUNROOT="$WORK/RUNS/${SLURM_JOB_ID:?}"
RANKS=${SLURM_NTASKS:?}
INTERNAL_DEADLINE=8700
SOLVER_CAP=3900
RESERVE=300
mkdir -p "$ROOT/runs"
[[ "$RANKS" == 56 ]]
[[ "${SLURM_CPUS_ON_NODE:?}" == 56 ]]
[[ "${SLURM_JOB_NUM_NODES:-${SLURM_NNODES:-0}}" == 1 ]]
[[ ! -e "$RUNROOT" ]] || { echo "Refusing existing RUNS destination: $RUNROOT" >&2; exit 20; }
[[ -r "$BASHRC" ]]

module load gcc/11
module load hpcx/2.50
export FOAM_CONFIG_MODE=o
set +euo pipefail
source "$BASHRC"
set -euo pipefail
[[ -n "${FOAM_APPBIN:-}" ]]

mkdir -p "$RUNROOT"
date -u +%FT%TZ > "$RUNROOT/start.utc"
hostname -f > "$RUNROOT/hostname.txt"
lscpu > "$RUNROOT/lscpu.txt"
env | sort | grep -E '^(SLURM_JOB_ID|SLURM_JOB_NUM_NODES|SLURM_CPUS_ON_NODE|SLURM_NTASKS|OMP_NUM_THREADS|OPENBLAS_NUM_THREADS|MKL_NUM_THREADS|UCX_TLS)=' > "$RUNROOT/launch-environment.txt" || true
printf 'job=%s rank_count=%s internal_deadline=%s solver_cap=%s reserve=%s\n' "$SLURM_JOB_ID" "$RANKS" "$INTERNAL_DEADLINE" "$SOLVER_CAP" "$RESERVE" > "$RUNROOT/admission.txt"

H_SRC=/global/exafs/users/rdmaworkshop30/apac2026/tripleu-hpc-20261021T1121/artifacts/ready-N56-h742
S_SRC=/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch56-20261025T063431Z/artifacts/ready-N56-scotch
source "$ROOT/lib/common.sh"
bounded 30 payload_source_check bash -c 'cd "$1" && sha256sum -c payload-sha256.txt' _ "$ROOT" > "$RUNROOT/payload-before.txt"
verify_source "$H_SRC" hierarchical
verify_source "$S_SRC" scotch
run_arm H "$H_SRC" hierarchical
run_arm S "$S_SRC" scotch
bounded 30 payload_source_check bash -c 'cd "$1" && sha256sum -c payload-sha256.txt' _ "$ROOT" > "$RUNROOT/payload-after.txt"
echo MATCHED_PAIR_COMPLETE
