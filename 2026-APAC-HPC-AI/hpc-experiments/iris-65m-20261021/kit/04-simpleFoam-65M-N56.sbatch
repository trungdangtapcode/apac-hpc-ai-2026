#!/bin/bash
# 65M flags follow official Allrun (not its 512-rank / 4000-step example):
# https://develop.openfoam.com/committees/hpc/-/blob/develop/incompressible/simpleFoam/occDrivAerStaticMesh/Allrun
# Touch: simpleFoam only, 40 steps, 56 ranks, from ready-N56-h742.
# Not a score. The contest quantity is average wall-clock time per time step.
# Pass = End and the Average line. This job does not cut.
#SBATCH -J of-foam-n56
#SBATCH -p iris
#SBATCH -N 1
#SBATCH -n 56
#SBATCH -t 00:40:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail

SHARED=/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam
BUILD="$SHARED/builds/iris-gcc11-hpcx250-opt"
BASHRC="$BUILD/OpenFOAM-v2512/etc/bashrc"
ROOT="${SLURM_SUBMIT_DIR:?}"
WORK="$(cd "$ROOT/.." && pwd)"
RANKS=${SLURM_NTASKS:?}
# This path is the N56 hierarchical split only. Another method or factors needs another directory.
# h742 is nHierarchical (7 4 2), not a hash. 7*4*2=56.
ART="$WORK/artifacts/ready-N56-h742"
SOLVE="$WORK/runs/${SLURM_JOB_ID:?}"
ITERS=40
mkdir -p "$ROOT/runs" "$SOLVE"

echo "[$(date -Iseconds)] job=${SLURM_JOB_ID} WORK=$WORK ranks=$RANKS iters=$ITERS"
test -r "$BASHRC"

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

# This job does not cut. Missing prep, wrong rank count, or wrong method: stop and say so.
[[ -f "$ART/READY" ]] || {
  echo "No READY stamp in $ART" >&2
  echo "This folder does not match that cut. Use a folder made for this method, or make a new folder for this cut." >&2
  exit 1
}
ready_n="$(awk -F= '/^N=/{print $2}' "$ART/READY")"
ready_m="$(awk -F= '/^method=/{print $2}' "$ART/READY")"
ready_h="$(awk -F= '/^nHierarchical=/{print $2}' "$ART/READY")"
[[ "$ready_n" == "$RANKS" ]] || {
  echo "READY N=$ready_n but this job has $RANKS ranks" >&2
  echo "This folder does not match that cut. Use a folder made for this method, or make a new folder for this cut." >&2
  exit 1
}
# Drop a trailing // comment, then spaces and ;. 65M ships a comment on this line.
case_m="$(sed -n 's/^decompositionMethod[[:space:]]*//p' "$ART/system/include/caseDefinition" | sed 's|[[:space:]]*//.*||' | tr -d ' ;')"
[[ -n "$ready_m" && "$ready_m" == "$case_m" && "$ready_m" == "hierarchical" ]] || {
  echo "READY method=$ready_m but the case method is $case_m in $ART" >&2
  echo "This folder does not match that cut. Use a folder made for this method, or make a new folder for this cut." >&2
  exit 1
}
case_h="$(sed -n 's/^nHierarchical[[:space:]]*//p' "$ART/system/include/caseDefinition" | sed 's|[[:space:]]*//.*||')"
case_h_n="$(printf '%s' "$case_h" | tr -d ' ;')"
ready_h_n="$(printf '%s' "$ready_h" | tr -d ' ;')"
[[ "$case_h_n" == "$ready_h_n" ]] || {
  echo "READY nHierarchical=$ready_h but the case is $case_h in $ART" >&2
  echo "This folder does not match that cut. Use a folder made for this method, or make a new folder for this cut." >&2
  exit 1
}
# Solver step count and logs go in this job folder. The cut is not rewritten.
# In: processor* linked from the cut. Out: this job's system/ and logFiles/.
cp -a "$ART/system" "$SOLVE/system"
ln -sfn "$ART/constant" "$SOLVE/constant"
for p in "$ART"/processor*; do
  ln -sfn "$p" "$SOLVE/$(basename "$p")"
done
cd "$SOLVE"
# noWrite ships startFrom latestTime. startTime makes 40/80/150 mean that many steps from time 0, not a leftover later time. The cut's controlDict is not rewritten.
foamDictionary system/controlDict -entry startFrom -set startTime >/dev/null
foamDictionary system/controlDict -entry endTime -set "$ITERS" >/dev/null
mkdir -p logFiles
# `--` ends Open MPI 5 options. `-parallel` makes OpenFOAM read processor*.
# Out: logFiles/simpleFoam.log.
mpirun -np "$RANKS" -- simpleFoam -parallel > logFiles/simpleFoam.log 2>&1

# End means the solver finished.
# Contest reading: Average wall-clock time per time step (from step 2 on).
test -s logFiles/simpleFoam.log
grep -q '^End' logFiles/simpleFoam.log
avg="$(grep -F 'Average wall-clock time per time step =' logFiles/simpleFoam.log | tail -n 1)"
[[ -n "$avg" ]]
echo "$avg"
echo "04-simpleFoam-65M-N56: PASS"
