#!/bin/bash
#PBS -N TripleU-DrivAer-2n-r208
#PBS -P qw53
#PBS -q normalsr
#PBS -l ncpus=208
#PBS -l mem=380GB
#PBS -l walltime=00:25:00
#PBS -l storage=scratch/qw53
#PBS -j oe
set -eo pipefail
module load OpenFOAM/2512
SCRIPT_DIR="${PBS_O_WORKDIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
NODE_MODE=2node
END_TIME=80
VARIANT=scotch_r208
CONFIG="${SCRIPT_DIR}/variants/${VARIANT}.conf"
export SCRIPT_DIR NODE_MODE END_TIME VARIANT CONFIG
source "${SCRIPT_DIR}/run_official_case.sh"
