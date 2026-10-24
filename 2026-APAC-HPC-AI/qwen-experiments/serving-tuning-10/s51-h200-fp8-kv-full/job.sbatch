#!/bin/bash
# Draft matched KV-cache screen; requires root review before submission.
#SBATCH -J ap42-s51-h200-fp8-kv-full
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --exclusive
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_JOB_START_EPOCH=$(date +%s)
export QWEN_RESOURCE_MONITOR=1
export QWEN_TUNE_NS=64
export QWEN_FULL_PROTOCOL=1
export QWEN_FULL_CONTROL_ARTIFACT=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/25875
export QWEN_KV_CACHE_DTYPE=fp8_e4m3
export QWEN_DIAGNOSTIC_PROFILE=0
export QWEN_IMAGE_PATH=/scratch/enroot-images/sglang-harbor.sqsh
export QWEN_BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s51-h200-fp8-kv-full
export QWEN_EXPERIMENT_ID="h200-kv-${SLURM_JOB_ID}-$(cat /proc/sys/kernel/random/uuid)"
export QWEN_NIXL_PATCH_SHA256=912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
mkdir -p "$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID"
set +e
python3 -B "$QWEN_BUNDLE/guard-full-pair.py" --role candidate --out "$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID/full-pair-guard.json" --control-artifact "${QWEN_FULL_CONTROL_ARTIFACT:-}"
GUARD_STATUS=$?
set -e
(( GUARD_STATUS == 0 )) || { echo "FATAL: conditional full-pair CPU gate failed" >&2; exit "$GUARD_STATUS"; }
if ! python3 - "$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID/full-pair-guard.json" <<'PYGUARD'
import json,sys
raise SystemExit(0 if json.load(open(sys.argv[1])).get('status') == 'PROCEED' else 1)
PYGUARD
then
  echo "SKIPPED_GUARD_FALSE_OR_UNKNOWN: no model workers started"
  exit 0
fi
mkdir -p "$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID"
python3 -B "$QWEN_BUNDLE/preflight-assets.py" >"$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID/asset-preflight.json"
python3 -B "$QWEN_BUNDLE/preflight-fp8-kv.py" --model /scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8 --out "$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID/kv-scale-provenance.json" >"$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID/kv-scale-provenance.stdout.json"
exec bash topology-job.sh
