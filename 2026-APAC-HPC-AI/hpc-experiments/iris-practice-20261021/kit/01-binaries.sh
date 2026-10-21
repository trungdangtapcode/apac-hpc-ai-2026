#!/usr/bin/env bash
# Touch: group v2512 after gcc/11 + hpcx/2.50 + the v2512 bashrc; dump foamEtcFile and wmake -build-info; solvers exist.
# Not a score. The contest quantity is average wall-clock time per time step.
#
# Pass = module loads and the solvers exist. Tool dumps are printout, not a fingerprint gate.
# Run on the login node. Do not sbatch this: Iris allocates whole nodes.
# Login CPUs are not Iris: simpleFoam and foamHasLibrary SIGILL here, even -help.
# Do not srun -p iris from this script (that takes a whole 56-core node). 02 prints those ELFs.
set -euo pipefail

BUILD=/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam/builds/iris-gcc11-hpcx250-opt
BASHRC="$BUILD/OpenFOAM-v2512/etc/bashrc"

echo "[$(date -Iseconds)] user=$(whoami) host=$(hostname)"
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

# -help exits 1 on wmake -build-info. Dump is for eyes, not the pass gate.
set +e
set -x
foamEtcFile -help-full
foamEtcFile -show-api
foamEtcFile -show-patch
foamEtcFile -show-build
foamEtcFile -list
wmake -build-info -help
wmake -build-info -query
set +x
set -e

test -x "$FOAM_APPBIN/simpleFoam"
test -x "$FOAM_APPBIN/potentialFoam"
test -x "$FOAM_APPBIN/decomposePar"
test -x "$FOAM_APPBIN/renumberMesh"
test -e "$FOAM_LIBBIN/libscotchDecomp.so"
echo "01-binaries: PASS"
