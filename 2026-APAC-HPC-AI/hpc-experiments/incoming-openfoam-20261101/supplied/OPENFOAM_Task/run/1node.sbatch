#!/bin/bash
#PBS -N TripleU-DrivAer-1n-numa
#PBS -P qw53
#PBS -q normalsr
#PBS -l ncpus=104
#PBS -l mem=190GB
#PBS -l walltime=00:25:00
#PBS -l storage=scratch/qw53
#PBS -j oe
set -eo pipefail
module load OpenFOAM/2512
SCRIPT_DIR="${PBS_O_WORKDIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
NODE_MODE=1node
END_TIME=40
VARIANT=scotch_r104_numa
CONFIG="${SCRIPT_DIR}/variants/${VARIANT}.conf"
export SCRIPT_DIR NODE_MODE END_TIME VARIANT CONFIG
source "${SCRIPT_DIR}/run_official_case.sh"
