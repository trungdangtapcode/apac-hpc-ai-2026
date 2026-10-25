#!/bin/bash
# 65M flags follow official Allrun (not its 512-rank / 4000-step example):
# https://develop.openfoam.com/committees/hpc/-/blob/develop/incompressible/simpleFoam/occDrivAerStaticMesh/Allrun
# Touch: 65M init on an existing N56 scotch cut. These tools need -parallel.
# Rank count must equal the processor* folders. One process cannot do this step.
# Writes READY. Not a score. This job does not run the solver.
# Pass = READY stamp after applyBoundaryLayer. Run 13.1 first.
# Same folder as 13.1.
#SBATCH -J of-sc-init-n56
#SBATCH -p iris
#SBATCH -N 1
#SBATCH -n 56
#SBATCH -t 00:20:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail

SHARED=/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam
BUILD="$SHARED/builds/iris-gcc11-hpcx250-opt"
BASHRC="$BUILD/OpenFOAM-v2512/etc/bashrc"

ROOT="${SLURM_SUBMIT_DIR:?}"
WORK="$(cd "$ROOT/.." && pwd)"
RANKS=${SLURM_NTASKS:?}
# This path is the N56 scotch split only. Another method or factors needs another directory.
ART="$WORK/artifacts/ready-N56-scotch"
mkdir -p "$ROOT/runs"

echo "[$(date -Iseconds)] job=${SLURM_JOB_ID} WORK=$WORK ranks=$RANKS"
test -r "$BASHRC"

# This job does not cut. Missing cut or wrong rank count: stop and say so.
[[ -f "$ART/READY" ]] && { echo "This cut is already here: $ART"; cat "$ART/READY"; echo "13.2-init-65M-N56-scotch: PASS"; exit 0; }
[[ -d "$ART/processor0" && -d "$ART/processor55" ]] || {
  echo "No processor folders in $ART" >&2
  echo "This folder does not match that cut. Use a folder made for this method, or make a new folder for this cut." >&2
  exit 1
}
case_n="$(sed -n 's/^nCores[[:space:]]*//p' "$ART/system/include/caseDefinition" | tr -d ' ;')"
[[ "$case_n" == "$RANKS" ]] || {
  echo "case nCores=$case_n but this job has $RANKS ranks" >&2
  echo "This folder does not match that cut. Use a folder made for this method, or make a new folder for this cut." >&2
  exit 1
}
# Drop a trailing // comment, then spaces and ;. 65M ships a comment on this line.
case_m="$(sed -n 's/^decompositionMethod[[:space:]]*//p' "$ART/system/include/caseDefinition" | sed 's|[[:space:]]*//.*||' | tr -d ' ;')"
[[ "$case_m" == "scotch" ]] || {
  echo "case method=$case_m but this job is scotch in $ART" >&2
  echo "This folder does not match that cut. Use a folder made for this method, or make a new folder for this cut." >&2
  exit 1
}

module load gcc/11
module load hpcx/2.50
export FOAM_CONFIG_MODE=o
# OpenFOAM etc/bashrc uses unbound vars and `return 1` for missing optional paths.
set +euo pipefail
# shellcheck disable=SC1090
source "$BASHRC"
set -euo pipefail
[[ -n "${FOAM_APPBIN:-}" ]]
set +u
# shellcheck disable=SC1091
source "${WM_PROJECT_DIR:?}/bin/tools/RunFunctions"
set -u

cd "$ART"
mkdir -p logFiles
# `--` ends Open MPI 5 options. `-parallel` makes OpenFOAM read processor*.
# Rank count must equal the processor* folders. Wrong count is a FOAM FATAL.
# Out: overwrite processor*/constant/polyMesh (reorder cells).
mpirun -np "$RANKS" -- renumberMesh -constant -overwrite -parallel > logFiles/renumberMesh.log 2>&1
# Out: processor*/0/U.
mpirun -np "$RANKS" -- potentialFoam -initialiseUBCs -parallel > logFiles/potentialFoam.log 2>&1
# Out: processor*/0/ with a boundary layer. -ybl 0.0450244 is Allrun's value; do not change it.
mpirun -np "$RANKS" -- applyBoundaryLayer -ybl 0.0450244 -parallel > logFiles/applyBoundaryLayer.log 2>&1

# Stamp so the next job checks this folder first and refuses the wrong cut.
# The cut is still the processor* folders.
cat > "$ART/READY" <<'EOF'
N=56
method=scotch
nHierarchical=unused
mesh=occDrivAer-65M
stages=decomposePar restore0Dir renumberMesh potentialFoam applyBoundaryLayer
EOF

echo "13.2-init-65M-N56-scotch: PASS"
