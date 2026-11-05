#!/bin/bash
# Derivative of the reviewed Iris Scotch cut-only payload; only the partition
# count changes from 48 to 40. This stage never marks a case READY or runs a solver.
#SBATCH -J tu-iris-s40-cut
#SBATCH -p iris
#SBATCH -A rdmaworkshop
#SBATCH --qos=low
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH --gpus=0
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
SPLIT_N=40
ART="$WORK/artifacts/cut-N40-scotch"
mkdir -p "$ROOT/runs"

echo "[$(date -Iseconds)] job=${SLURM_JOB_ID} WORK=$WORK tasks=${SLURM_NTASKS:?} split=$SPLIT_N"
test "$SLURM_NTASKS" = 1
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
# OpenFOAM etc/bashrc may reference optional unset variables or return 1.
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
rm -f "$ART/Allrun" "$ART/Allmesh"
test ! -e "$ART/constant/polyMesh" && test ! -L "$ART/constant/polyMesh"
ln -s "$MESH_SRC" "$ART/constant/polyMesh"
cd "$ART"
cp system/controlDict.noWrite system/controlDict
cp system/fvSolution.fixedIter system/fvSolution
sed -i "s/^nCores .*/nCores              $SPLIT_N;/" system/include/caseDefinition
# Keep this expansion present in decomposeParDict even though Scotch is active.
sed -i 's/^nHierarchical .*/nHierarchical       (7 4 2);/' system/include/caseDefinition
sed -i 's/^decompositionMethod .*/decompositionMethod scotch;/' system/include/caseDefinition
sed -i '/^nHierarchical /i // Not the scotch cut. Required so decomposeParDict $nHierarchical expands.' system/include/caseDefinition
mkdir -p logFiles
# Serial decomposePar makes exactly 40 Scotch domains from the existing serial mesh.
/usr/bin/time -v -o logFiles/decomposePar.resource.txt timeout --signal=TERM --kill-after=15s 1800s decomposePar -constant > logFiles/decomposePar.log 2>&1
timeout --signal=TERM --kill-after=15s 90s bash -ec '. "$WM_PROJECT_DIR/bin/tools/RunFunctions"; restore0Dir -processor' > logFiles/restore0Dir.log 2>&1
timeout --signal=TERM --kill-after=15s 60s python3 "$ROOT/validate-cut.py" --case "$ART" --output "$ROOT/runs/${SLURM_JOB_ID}-cut-validation.json"
python3 "$ROOT/verify-payload.py" "$ROOT" > "$ROOT/runs/${SLURM_JOB_ID}-source-after.json"
echo "TRIPLEU_IRIS_SCOTCH40_CUT_NATIVE_PASS"
