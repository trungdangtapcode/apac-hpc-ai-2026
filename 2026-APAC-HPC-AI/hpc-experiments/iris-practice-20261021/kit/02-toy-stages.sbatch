#!/bin/bash
# Toy motorBike, not the 65M Allrun. 65M jobs cite:
# https://develop.openfoam.com/committees/hpc/-/blob/develop/incompressible/simpleFoam/occDrivAerStaticMesh/Allrun
# Touch: toy case. One small mesh, two splits, five stages each. You do not mesh.
# Not a score. The contest quantity is average wall-clock time per time step.
# Pass = both splits finish; each simpleFoam log has End. Print ClockTime = and Average if present.
# The two toy times are not a contest.
#SBATCH -J of-toy-stages
#SBATCH -p iris
#SBATCH -N 1
#SBATCH -n 4
#SBATCH -t 00:05:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail

SHARED=/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam
BUILD="$SHARED/builds/iris-gcc11-hpcx250-opt"
BASHRC="$BUILD/OpenFOAM-v2512/etc/bashrc"
TOY_SRC="$SHARED/toy-motorBike"
ROOT="${SLURM_SUBMIT_DIR:?}"
WORK="$(cd "$ROOT/.." && pwd)"
RUN="$WORK/runs/${SLURM_JOB_ID:?}"
RANKS=${SLURM_NTASKS:?}
mkdir -p "$ROOT/runs" "$RUN"

echo "[$(date -Iseconds)] job=${SLURM_JOB_ID} WORK=$WORK ranks=$RANKS"
test -d "$TOY_SRC"
test -r "$BASHRC"

# Group v2512. etc/bashrc uses unbound vars and `return 1` for missing optional paths.
module load gcc/11
module load hpcx/2.50
export FOAM_CONFIG_MODE=o
set +euo pipefail
# shellcheck disable=SC1090
source "$BASHRC"
set -euo pipefail
[[ -n "${FOAM_APPBIN:-}" ]]

# Compute node. 01 SIGILLs these ELFs on login. Dump them here. -help may be exit 1.
set +e
set -x
simpleFoam -help
foamHasLibrary -help
foamHasLibrary -verbose -detail libscotchDecomp.so
set +x
set -e

set +u
# shellcheck disable=SC1091
source "${WM_PROJECT_DIR:?}/bin/tools/RunFunctions"
set -u

# Two folders, two splits, one serial polyMesh. Mix processor* and you cannot tell them apart.
# Allmesh rebuilds the mesh. Skip it. You already have polyMesh.
H="$RUN/hierarchical"
S="$RUN/scotch"
rm -rf "$H" "$S"
cp -a "$TOY_SRC" "$H"
cp -a "$TOY_SRC" "$S"
chmod -R u+w "$H" "$S"
# Working copies only. Group toy-motorBike stays as shipped.
for d in "$H" "$S"; do
  rm -f "$d/README.md" "$d/Allmesh" "$d/Allrun" "$d/run-toy.sh" "$d/timed.sh"
done

# Hierarchical: xyz box. Default here is (4 1 1), four slabs.
cd "$H"
# Changing the rank count invalidates the split. nCores must equal #SBATCH -n.
# A new rank count needs a new directory (see LADDER.md).
sed -i "s/^nCores .*/nCores              $RANKS;/" system/include/caseDefinition
# How long simpleFoam runs is this job's setting, not the split.
# This copy lives under runs/<jobid>. Case ships two controlDicts; noWrite is the short run.
cp system/controlDict.noWrite system/controlDict
cp system/fvSolution.fixedIter system/fvSolution
grep -E '^(nCores|decompositionMethod|nHierarchical)' system/include/caseDefinition
mkdir -p logFiles
# In: serial constant/polyMesh. Out: processor0 .. processor3 (xyz slabs).
decomposePar -constant > logFiles/decomposePar.log 2>&1
ls -d processor*
# Out: processor*/0/ from 0.orig/.
restore0Dir -processor > logFiles/restore0Dir.log 2>&1
# `--` ends Open MPI 5 options. `-parallel` makes OpenFOAM read processor*.
# Out: overwrite processor*/constant/polyMesh (reorder cells).
mpirun -np "$RANKS" -- renumberMesh -constant -overwrite -parallel > logFiles/renumberMesh.log 2>&1
# Out: processor*/0/U. 65M prep then runs applyBoundaryLayer. This toy does not.
mpirun -np "$RANKS" -- potentialFoam -initialiseUBCs -parallel > logFiles/potentialFoam.log 2>&1
# Out: time dirs under processor*/ and postProcessing/.
mpirun -np "$RANKS" -- simpleFoam -parallel > logFiles/simpleFoam.log 2>&1
cat > SPLIT <<EOF
method=hierarchical
nCores=$RANKS
nHierarchical=(4 1 1)
EOF

# Scotch: also 4 ranks, cut the cell graph. Ignores nHierarchical.
cd "$S"
sed -i "s/^nCores .*/nCores              $RANKS;/" system/include/caseDefinition
sed -i 's/^decompositionMethod .*/decompositionMethod scotch;/' system/include/caseDefinition
# decomposeParDict still expands $nHierarchical inside hierarchicalCoeffs even
# when method is scotch. Keep the variable. Do not comment it out (FOAM IO error).
# The live method is the decompositionMethod line. SPLIT.method must match that.
sed -i '/^nHierarchical /i // Not the scotch cut. Required so decomposeParDict $nHierarchical expands.' system/include/caseDefinition
cp system/controlDict.noWrite system/controlDict
cp system/fvSolution.fixedIter system/fvSolution
grep -E '^(nCores|decompositionMethod|nHierarchical)' system/include/caseDefinition
mkdir -p logFiles
# Still 4 processor* folders. The cells inside them are grouped by the graph, not by xyz.
decomposePar -constant > logFiles/decomposePar.log 2>&1
ls -d processor*
restore0Dir -processor > logFiles/restore0Dir.log 2>&1
mpirun -np "$RANKS" -- renumberMesh -constant -overwrite -parallel > logFiles/renumberMesh.log 2>&1
mpirun -np "$RANKS" -- potentialFoam -initialiseUBCs -parallel > logFiles/potentialFoam.log 2>&1
mpirun -np "$RANKS" -- simpleFoam -parallel > logFiles/simpleFoam.log 2>&1
cat > SPLIT <<EOF
method=scotch
nCores=$RANKS
nHierarchical=unused
EOF

# Both logs need ^End. Toy may lack the 65M Average FO; print it if present.
test -s "$H/logFiles/simpleFoam.log"
grep -q '^End' "$H/logFiles/simpleFoam.log"
line="$(grep -E 'ClockTime[[:space:]]*=' "$H/logFiles/simpleFoam.log" | tail -n 1)"
[[ -n "$line" ]]
clock="$(printf '%s\n' "$line" | grep -oE 'ClockTime[[:space:]]*=[[:space:]]*[0-9.]+[[:space:]]*s')"
[[ -n "$clock" ]]
echo "hierarchical $clock"
if grep -q -F 'Average wall-clock time per time step =' "$H/logFiles/simpleFoam.log"; then
  grep -F 'Average wall-clock time per time step =' "$H/logFiles/simpleFoam.log" | tail -n 1
fi

test -s "$S/logFiles/simpleFoam.log"
grep -q '^End' "$S/logFiles/simpleFoam.log"
line="$(grep -E 'ClockTime[[:space:]]*=' "$S/logFiles/simpleFoam.log" | tail -n 1)"
[[ -n "$line" ]]
clock="$(printf '%s\n' "$line" | grep -oE 'ClockTime[[:space:]]*=[[:space:]]*[0-9.]+[[:space:]]*s')"
[[ -n "$clock" ]]
echo "scotch $clock"
if grep -q -F 'Average wall-clock time per time step =' "$S/logFiles/simpleFoam.log"; then
  grep -F 'Average wall-clock time per time step =' "$S/logFiles/simpleFoam.log" | tail -n 1
fi

for d in "$H" "$S"; do
  echo "--- $d/SPLIT ---"
  cat "$d/SPLIT"
  split_m="$(awk -F= '/^method=/{print $2}' "$d/SPLIT")"
  # Drop a trailing // comment, then spaces and ;. 65M ships a comment on this line.
  case_m="$(sed -n 's/^decompositionMethod[[:space:]]*//p' "$d/system/include/caseDefinition" | sed 's|[[:space:]]*//.*||' | tr -d ' ;')"
  [[ "$split_m" == "$case_m" ]] || {
    echo "SPLIT method=$split_m but the case method is $case_m in $d" >&2
    echo "This folder does not match that cut. Use a folder made for this method, or make a new folder for this cut." >&2
    exit 1
  }
done

echo "02-toy-stages: PASS"
