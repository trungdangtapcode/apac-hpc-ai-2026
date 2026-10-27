#!/usr/bin/env bash
#SBATCH -J ap42-rc-clean
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:0
#SBATCH -t 00:05:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
Q=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments
B=$Q/native-runtime-r3-20261027
A=$Q/runs/$SLURM_JOB_ID
mkdir -p "$A"
srun --exact -N2 -n2 --ntasks-per-node=1 --gres=gpu:0 python3 "$B/cleanup-node.py" >"$A/cleanup-before.jsonl" 2>&1
node=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n1)
srun --exact -N1 -n1 -w "$node" --gres=gpu:0 bash "$B/native-container.sh" /scratch/enroot-images/aiperf.sqsh "$Q:$Q:ro" \
 env QWEN_ENTRYPOINT_PROBE=direct_exec bash -c 'set -e; python3 -c '\''import os; assert os.environ["QWEN_ENTRYPOINT_PROBE"]=="direct_exec"; assert os.environ.get("CUDA_VISIBLE_DEVICES")==""; print("NATIVE_ENV_ARGV_PASS")'\''; aiperf --version; echo AIPERF_ENTRYPOINT_OVERRIDE_PASS' >"$A/aiperf-entrypoint.log" 2>&1
grep -qx AIPERF_ENTRYPOINT_OVERRIDE_PASS "$A/aiperf-entrypoint.log"
srun --exact -N2 -n2 --ntasks-per-node=1 --gres=gpu:0 python3 "$B/cleanup-node.py" >"$A/cleanup-after.jsonl" 2>&1
python3 - "$A" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);(p/'runtime-proof.json').write_text(json.dumps({'state':'AIPERF_ENTRYPOINT_AND_TERMINAL_ROOT_CLEANUP_PASS','job':p.name})+'\n')
PY
