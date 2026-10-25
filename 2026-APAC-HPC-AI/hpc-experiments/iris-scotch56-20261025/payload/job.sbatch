#!/bin/bash
# 65M flags follow official Allrun (not its 512-rank / 4000-step example):
# https://develop.openfoam.com/committees/hpc/-/blob/develop/incompressible/simpleFoam/occDrivAerStaticMesh/Allrun
# Touch: 65M scotch cut only. decomposePar is one process; this job asks for 1 task.
# The split is still 56 folders. nCores is 56, not SLURM_NTASKS. No READY.
# Not a score. This job does not run the solver.
# Pass = processor0 and processor55 exist. Then run 13.2.
# Same folder as 13.2. There is no 13 one-shot; 03/06/08 are the hierarchical weld.
#SBATCH -J tu-iris-s56-cut
#SBATCH -p iris
#SBATCH -A rdmaworkshop
#SBATCH --qos=low
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 00:40:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail

SHARED=/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam
BUILD="$SHARED/builds/iris-gcc11-hpcx250-opt"
BASHRC="$BUILD/OpenFOAM-v2512/etc/bashrc"

CASE_SRC="${SLURM_SUBMIT_DIR:?}/payload-case"
MESH_SRC="$SHARED/occDrivAer/polyMesh"
ROOT="${SLURM_SUBMIT_DIR:?}"
WORK="$(cd "$ROOT/.." && pwd)"
# This job asks for 1 process. The split is still 56 folders.
# nCores is 56, not SLURM_NTASKS.
SPLIT_N=56
# This path is the N56 scotch split only. Another method or factors needs another directory.
ART="$WORK/artifacts/ready-N56-scotch"
mkdir -p "$ROOT/runs"

echo "[$(date -Iseconds)] job=${SLURM_JOB_ID} WORK=$WORK tasks=${SLURM_NTASKS:?} split=$SPLIT_N"
test -d "$MESH_SRC"
test -r "$BASHRC"

# Never resume, overwrite or delete a previous intent's processor tree.
test ! -e "$ART" && test ! -L "$ART"
mkdir -p "$ART"
python3 "$ROOT/verify-payload.py" "$ROOT" > "$ROOT/runs/${SLURM_JOB_ID}-source-before.json"
{ date -u; hostname; lscpu; } > "$ROOT/runs/${SLURM_JOB_ID}-hardware.log"
timeout --signal=TERM --kill-after=15s 180s python3 "$ROOT/validate-cut.py" --mesh "$MESH_SRC" --expected "$ROOT/expected-mesh.json" --mesh-only --output "$ROOT/runs/${SLURM_JOB_ID}-mesh-before.json"
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

cp -a "$CASE_SRC/." "$ART/"
chmod -R u+w "$ART"
# Working copy only. Group occDrivAer/case stays as shipped.
rm -f "$ART/Allrun" "$ART/Allmesh"
test ! -e "$ART/constant/polyMesh" && test ! -L "$ART/constant/polyMesh"
# Group polyMesh stays put. This folder only links it.
ln -s "$MESH_SRC" "$ART/constant/polyMesh"
cd "$ART"
cp system/controlDict.noWrite system/controlDict
cp system/fvSolution.fixedIter system/fvSolution
sed -i "s/^nCores .*/nCores              $SPLIT_N;/" system/include/caseDefinition
# Keep nHierarchical so decomposeParDict $nHierarchical expands. Do not comment it out (FOAM IO error).
sed -i 's/^nHierarchical .*/nHierarchical       (7 4 2);/' system/include/caseDefinition
sed -i 's/^decompositionMethod .*/decompositionMethod scotch;/' system/include/caseDefinition
# Not the scotch cut. Required so decomposeParDict $nHierarchical expands.
sed -i '/^nHierarchical /i // Not the scotch cut. Required so decomposeParDict $nHierarchical expands.' system/include/caseDefinition

mkdir -p logFiles

# One process. Asking for 56 tasks does not make decomposePar faster.
# In: serial constant/polyMesh. Out: processor0 .. processor55 (graph cut, not xyz slabs).
/usr/bin/time -v -o logFiles/decomposePar.resource.txt timeout --signal=TERM --kill-after=15s 1800s decomposePar -constant > logFiles/decomposePar.log 2>&1
# Out: processor*/0/ from 0.orig/.
timeout --signal=TERM --kill-after=15s 90s bash -ec '. "$WM_PROJECT_DIR/bin/tools/RunFunctions"; restore0Dir -processor' > logFiles/restore0Dir.log 2>&1

# 56 ranks: processor0 and processor55 must both exist.
test -d processor0
test -d processor55

timeout --signal=TERM --kill-after=15s 60s python3 "$ROOT/validate-cut.py" --case "$ART" --output "$ROOT/runs/${SLURM_JOB_ID}-cut-validation.json"
python3 "$ROOT/verify-payload.py" "$ROOT" > "$ROOT/runs/${SLURM_JOB_ID}-source-after.json"
echo "TRIPLEU_IRIS_SCOTCH56_CUT_NATIVE_PASS"
