#!/usr/bin/env bash
#SBATCH -J ap42-cmpobs
#SBATCH -p hpcai
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1
#SBATCH -t 00:04:00
#SBATCH -o /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-compile-observer-probe-20261029/slurm-%j.out
#SBATCH -e /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-compile-observer-probe-20261029/slurm-%j.err
set -euo pipefail
Q=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments
D=$Q/h200-compile-observer-probe-20261029
NATIVE=$Q/h200-kv-page-primitive-r2-20261028/native-container.sh
cd "$D"
sha256sum --check SHA256SUMS
python3 - "$D/provenance.json" <<'NATIVEPROOF'
from pathlib import Path
import hashlib,json,sys
p=json.loads(Path(sys.argv[1]).read_text())
for key in ('immutable_container_launcher','immutable_enroot_exec_rc'):
    item=p[key]
    assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256'], key
print('NATIVE_LAUNCHER_AND_RC_HASHES_VERIFIED',flush=True)
NATIVEPROOF
mkdir -p "$D/runtime"
export QWEN_PROBE_OUT="$D/runtime/observer-${SLURM_JOB_ID}.json"
JOB_START_EPOCH=$(date +%s)
export QWEN_PROBE_DEADLINE_EPOCH=$((JOB_START_EPOCH + 205))
srun --exact --ntasks=1 --cpus-per-task=4 --gres=gpu:1 \
  timeout --signal=TERM --kill-after=20s 205s \
  bash "$NATIVE" /scratch/enroot-images/sglang-harbor.sqsh \
  "/scratch:/scratch,$Q:$Q" \
  env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  SGLANG_TORCH_COMPILE_MODE=max-autotune-no-cudagraphs \
  python3 -B "$D/probe.py"
