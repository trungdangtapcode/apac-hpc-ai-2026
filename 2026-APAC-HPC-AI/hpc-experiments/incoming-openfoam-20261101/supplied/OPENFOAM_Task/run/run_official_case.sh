#!/bin/bash
set -eo pipefail

VARIANT="${VARIANT:-scotch}"
CONFIG="${CONFIG:-${SCRIPT_DIR}/variants/${VARIANT}.conf}"
if [ ! -f "${CONFIG}" ]; then
    echo "Missing variant config: ${CONFIG}" >&2
    exit 2
fi
# shellcheck disable=SC1090
source "${CONFIG}"

ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE="/scratch/qw53/tl1237/TripleU-official/case/occDrivAerStaticMesh"
NPROCS="${PBS_NCPUS:-48}"
RUN_ID="${PBS_JOBID:-local-$(date +%Y%m%d-%H%M%S)}"
RUN_ID="${RUN_ID//[^A-Za-z0-9_.-]/_}"
OUT="${ROOT}/output/${NODE_MODE}/${VARIANT}_${RUN_ID}"
WORK="/scratch/qw53/tl1237/TripleU-official/runs/${VARIANT}_${RUN_ID}/case"
mkdir -p "${OUT}" "$(dirname "${WORK}")"

# Keep a live job-level stream in the workspace in addition to the
# phase-specific OpenFOAM logs below.
exec > >(tee -a "${OUT}/job.out") 2> >(tee -a "${OUT}/job.err" >&2)
echo "job_id=${PBS_JOBID:-local}"
echo "node_mode=${NODE_MODE} variant=${VARIANT} mpi_ranks=${NPROCS}"
echo "started=$(date -Is)"

START_EPOCH="$(date +%s)"
date -Is > "${OUT}/started_at.txt"
cp -a "${SOURCE}" "${WORK}"
cd "${WORK}"

cp system/controlDict.noWrite system/controlDict
# Allow variant-specific fvSolution (Bonus tier)
_FVSOL="system/fvSolution.${FVSOLUTION_VARIANT:-fixedIter}"
if [ ! -f "${_FVSOL}" ]; then
    echo "WARNING: ${_FVSOL} not found, falling back to fixedIter" >&2
    _FVSOL="system/fvSolution.fixedIter"
fi
cp "${_FVSOL}" system/fvSolution
sed -i "s/^[[:space:]]*nCores[[:space:]].*/nCores              ${NPROCS};/" \
    system/include/caseDefinition
sed -i "s/^[[:space:]]*decompositionMethod[[:space:]].*/decompositionMethod ${DECOMPOSITION_METHOD};/" \
    system/include/caseDefinition
if [ -n "${HIERARCHICAL_COEFFS}" ]; then
    sed -i "s/^[[:space:]]*nHierarchical[[:space:]].*/nHierarchical       ${HIERARCHICAL_COEFFS};/" \
        system/include/caseDefinition
fi
foamDictionary system/controlDict -entry endTime -set "${END_TIME}" \
    > "${OUT}/control-config.log"
cp system/include/caseDefinition "${OUT}/caseDefinition"
cp system/decomposeParDict "${OUT}/decomposeParDict"
cp system/controlDict "${OUT}/controlDict"
cp "${CONFIG}" "${OUT}/variant.conf"

source "${WM_PROJECT_DIR}/bin/tools/RunFunctions"

# Optional MPI/UCX tuning from variant config
MPI_EXTRA_FLAGS="${MPI_EXTRA_FLAGS:-}"
if [ -n "${UCX_TLS:-}" ]; then
    export UCX_TLS
fi
if [ -n "${UCX_MEMTYPE_CACHE:-}" ]; then
    export UCX_MEMTYPE_CACHE
fi

decomposePar -constant > "${OUT}/10_decomposePar.log" 2>&1
restore0Dir -processor > "${OUT}/15_restore0Dir.log" 2>&1
# shellcheck disable=SC2086
mpirun -np "${NPROCS}" ${MPI_EXTRA_FLAGS} renumberMesh -constant -overwrite -parallel \
    > "${OUT}/20_renumberMesh.log" 2>&1
# shellcheck disable=SC2086
mpirun -np "${NPROCS}" ${MPI_EXTRA_FLAGS} potentialFoam -initialiseUBCs -parallel \
    > "${OUT}/30_potentialFoam.log" 2>&1
# shellcheck disable=SC2086
mpirun -np "${NPROCS}" ${MPI_EXTRA_FLAGS} applyBoundaryLayer -ybl 0.0450244 -parallel \
    > "${OUT}/40_applyBoundaryLayer.log" 2>&1
# Optional OpenFOAM extra flags (e.g. -fileHandler collated)
OF_EXTRA_FLAGS="${OF_EXTRA_FLAGS:-}"

# shellcheck disable=SC2086
mpirun -np "${NPROCS}" ${MPI_EXTRA_FLAGS} simpleFoam -parallel ${OF_EXTRA_FLAGS} \
    > "${OUT}/50_simpleFoam.log" 2>&1

echo "solver_finished=$(date -Is)"
COEFF_PATH="$(find postProcessing/forceCoeffsAll -type f -name coefficient.dat \
    -print -quit 2>/dev/null || true)"
COEFF=""
if [ -n "${COEFF_PATH}" ]; then
    cp "${COEFF_PATH}" "${OUT}/coefficient.dat"
    COEFF="${OUT}/coefficient.dat"
fi
END_EPOCH="$(date +%s)"
{
    printf 'case=occDrivAerStaticMesh\nnode_mode=%s\nvariant=%s\npbs_job_id=%s\n' \
        "${NODE_MODE}" "${VARIANT}" "${PBS_JOBID:-local}"
    printf 'mpi_ranks=%s\ndecomposition=%s\nendTime=%s\nprecision=double\n' \
        "${NPROCS}" "${DECOMPOSITION_METHOD}" "${END_TIME}"
    printf 'exit_status=0\nwall_seconds=%s\ncoefficient_file=%s\n' \
        "$((END_EPOCH - START_EPOCH))" "${COEFF:-none}"
    grep -h 'Average wall-clock time per time step' "${OUT}/50_simpleFoam.log" \
        | tail -1 || true
    grep -h 'Cd' "${OUT}/coefficient.dat" | tail -1 || true
} > "${OUT}/summary.log"
date -Is > "${OUT}/finished_at.txt"
