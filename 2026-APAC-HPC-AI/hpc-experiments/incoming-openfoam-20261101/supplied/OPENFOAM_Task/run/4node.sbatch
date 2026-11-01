#!/bin/bash
#PBS -N TripleU-DrivAer-4n-numa
#PBS -P qw53
#PBS -q normalsr
#PBS -l ncpus=416
#PBS -l mem=760GB
#PBS -l walltime=00:35:00
#PBS -l storage=scratch/qw53
#PBS -j oe
set -eo pipefail
module load OpenFOAM/2512
SCRIPT_DIR="${PBS_O_WORKDIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
NODE_MODE=4node
END_TIME=150
VARIANT=scotch_r416_numa
CONFIG="${SCRIPT_DIR}/variants/${VARIANT}.conf"
export SCRIPT_DIR NODE_MODE END_TIME VARIANT CONFIG
source "${SCRIPT_DIR}/run_official_case.sh"
