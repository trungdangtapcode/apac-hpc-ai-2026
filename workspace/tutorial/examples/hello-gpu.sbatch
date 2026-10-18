#!/bin/bash
#SBATCH --job-name=learn-gpu
#SBATCH --partition=hpcai
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --time=00:05:00
#SBATCH --propagate=NONE
#SBATCH --output=runs/%j.out
#SBATCH --error=runs/%j.err

# Submit from ~/workspace/tutorial with: sbatch examples/hello-gpu.sbatch
set -euo pipefail

TUTORIAL_DIR="${SLURM_SUBMIT_DIR}"
IMAGE=/scratch/enroot-images/sglang-harbor.sqsh
CONTAINER_HOME="${TUTORIAL_DIR}/container-home"
mkdir -p "${CONTAINER_HOME}"
test -r "${IMAGE}"
test -f "${TUTORIAL_DIR}/examples/hello_gpu.py"

echo "Job ID: ${SLURM_JOB_ID}"
echo "Allocated nodes: ${SLURM_JOB_NODELIST}"
echo "Batch script host: $(hostname)"

# srun starts a task on the allocated compute node, inside the BTC image.
# Mount the tutorial at a simple fixed path inside the container.
srun --container-image="${IMAGE}" \
  --container-mounts="/scratch:/scratch,${CONTAINER_HOME}:${HOME},${TUTORIAL_DIR}:/tutorial" \
  bash -c 'set -euo pipefail
    hostname
    nvidia-smi
    python3 /tutorial/examples/hello_gpu.py
  '

echo "Finished successfully."
