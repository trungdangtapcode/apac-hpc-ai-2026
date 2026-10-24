#!/usr/bin/env bash
#SBATCH -J ap42-d5r2-h200-ready
#SBATCH -p hpcai
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:5
#SBATCH --cpus-per-task=40
#SBATCH -t 00:17:00
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
R=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments
B=$R/dp5-h200-readiness-r2-20261024
OUT=$R/runs/$SLURM_JOB_ID
PRIVATE_HOME=$R/home/$SLURM_JOB_ID/d5
cd "$B"
sha256sum --check SHA256SUMS
python3 -B "$B/prepare_check.py"
mkdir -p "$OUT" "$PRIVATE_HOME"
python3 -B "$B/preflight-assets.py" >"$OUT/asset-preflight.json"
cp -a "$B" "$OUT/submitted-payload"
cp "$B/SHA256SUMS" "$OUT/submitted-manifest.sha256"
printf 'SLURM_JOB_ID=%s\nSTART_UTC=%s\n' "$SLURM_JOB_ID" "$(date -u +%FT%TZ)" >"$OUT/job-context.txt"
srun --exact -N1 -n1 --gres=gpu:5 --cpus-per-task=40 --cpu-bind=cores \
  --container-image=/scratch/enroot-images/sglang-harbor.sqsh \
  --container-mounts="$PRIVATE_HOME:/home/apacsc42,$R:$R:ro,$OUT:$OUT,/scratch/models:/scratch/models:ro" \
  env HOME=/home/apacsc42 D5_BUNDLE="$B" D5_OUTPUT_DIR="$OUT" \
  bash "$B/worker.sh"
python3 -B "$B/headcheck.py" --out "$OUT" >"$OUT/independent-headcheck.json"
