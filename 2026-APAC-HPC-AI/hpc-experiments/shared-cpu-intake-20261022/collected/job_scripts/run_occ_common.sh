#!/bin/bash
# OpenFOAM's supported site RunFunctions references optional FOAM_* variables
# before defining them, so nounset is incompatible with this module.
set -eo pipefail

# Required environment variables are set by the PBS wrappers.
: "${NODES:?}"
: "${NPROCS:?}"
: "${END_TIME:?}"
: "${DECOMP_METHOD:=scotch}"
: "${HIER_SHAPE:=16 8 4}"

BASE_DIR="${BASE_DIR:-$HOME/scratch/apac2026/hpc}"
# This directory is materialized from the organizer's immutable GitLab
# snapshot (commit 84c26243).  Keeping it separate from earlier mirrors
# prevents accidental use of non-Basic custom smoothers.
CASE_TEMPLATE="${CASE_TEMPLATE:-$BASE_DIR/case-template-official}"
MESH_DIR="${MESH_DIR:-$BASE_DIR/shared/polyMesh}"
RUN_ID="${PBS_JOBID%%.*}"
RUN_DIR="$BASE_DIR/runs/${NODES}n-${DECOMP_METHOD}-${RUN_ID}"

# Restore the NSCC programming environment, including cray-pals (mpirun),
# then load the official competition module exactly as documented.
. /app/apps/resetmodule || true
module load openfoam/2512
export FI_OFI_RXM_USE_SRX=0
export OMP_NUM_THREADS=1

mkdir -p "$RUN_DIR"
cp -a "$CASE_TEMPLATE/." "$RUN_DIR/"
rm -f "$RUN_DIR/constant/polyMesh"
ln -s "$MESH_DIR" "$RUN_DIR/constant/polyMesh"
cd "$RUN_DIR"

sed -Ei "s/^[[:space:]]*nCores[[:space:]]+[^;]+;/nCores              ${NPROCS};/" system/include/caseDefinition
sed -Ei "s/^[[:space:]]*decompositionMethod[[:space:]]+[^;]+;/decompositionMethod ${DECOMP_METHOD};/" system/include/caseDefinition
sed -Ei "s/^[[:space:]]*nHierarchical[[:space:]]+\([^;]+;/nHierarchical       (${HIER_SHAPE});/" system/include/caseDefinition
sed -Ei "s/^[[:space:]]*endTime[[:space:]]+[^;]+;/endTime           ${END_TIME};/" system/controlDict.noWrite

cp system/controlDict.noWrite system/controlDict
cp system/fvSolution.fixedIter system/fvSolution
mkdir -p logFiles

{
  echo "team=VNUHCM-TripleU"
  echo "job_id=$PBS_JOBID"
  echo "timestamp=$(date -Is)"
  echo "nodes=$NODES"
  echo "ranks=$NPROCS"
  echo "end_time=$END_TIME"
  echo "decomposition=$DECOMP_METHOD"
  echo "hierarchical_shape=$HIER_SHAPE"
  echo "FI_OFI_RXM_USE_SRX=$FI_OFI_RXM_USE_SRX"
  echo "host=$(hostname)"
  module list 2>&1
  env | grep -E '^(WM_|FOAM_|MPICH_|FI_)' | sort
} > logFiles/00_environment.log

run_and_check() {
  local label="$1"
  shift
  set +e
  "$@" > "logFiles/${label}.log" 2>&1
  local rc=$?
  set -e
  if ! grep -q '^End$' "logFiles/${label}.log"; then
    echo "ERROR: ${label} did not reach End (rc=${rc})" >&2
    exit 1
  fi
}

run_and_check 10_decomposePar decomposePar -constant
. "$WM_PROJECT_DIR/bin/tools/RunFunctions"
restore0Dir -processor
run_and_check 20_renumberMesh mpirun -np "$NPROCS" renumberMesh -constant -overwrite -parallel
run_and_check 30_potentialFoam mpirun -np "$NPROCS" potentialFoam -initialiseUBCs -parallel
run_and_check 40_applyBoundaryLayer mpirun -np "$NPROCS" applyBoundaryLayer -ybl 0.0450244 -parallel

SOLVER_LOG="logFiles/50_simpleFoam.$(date +%Y%m%d-%H%M%S).log"
set +e
mpirun -np "$NPROCS" simpleFoam -parallel > "$SOLVER_LOG" 2>&1
solver_rc=$?
set -e
if ! grep -q '^End$' "$SOLVER_LOG"; then
  echo "ERROR: simpleFoam did not reach End (rc=${solver_rc})" >&2
  exit 1
fi

{
  grep 'Average wall-clock time per time step' "$SOLVER_LOG" | tail -1
  find postProcessing -name coefficient.dat -type f -print -exec tail -1 {} \; 2>/dev/null || true
  echo "run_dir=$RUN_DIR"
} | tee logFiles/99_summary.log
