#!/bin/bash
#SBATCH -J ap42-map8-probe
#SBATCH -p hpcai
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:8
#SBATCH -t 00:04:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
Q=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments
S=$Q/native-gpu-map-r2-20261027
A=$Q/runs/$SLURM_JOB_ID
mkdir -p "$A"
for role in 0 1; do
 srun --exact -N1 -n1 --gres=gpu:4 --cpus-per-task=8 \
  bash "$S/native-container.sh" /scratch/enroot-images/sglang-harbor.sqsh "$Q:$Q:ro" \
  python3 "$S/probe.py" >"$A/split-$role.log" 2>&1 &
 pids[$role]=$!
done
for pid in "${pids[@]}"; do wait "$pid"; done
python3 - "$A" <<'PY'
from pathlib import Path
import json,sys
root=Path(sys.argv[1]);sets=[]
for role in [0,1]:
 rows=[]
 for line in (root/f'split-{role}.log').read_text().splitlines():
  try:row=json.loads(line)
  except ValueError:continue
  if row.get('state')=='SPLIT_FOUR_GPU_TENSOR_PASS':rows.append(row)
 assert len(rows)==1 and len(rows[0]['uuids'])==4
 sets.append(set(rows[0]['uuids']))
assert not sets[0]&sets[1] and len(sets[0]|sets[1])==8
proof={'state':'NATIVE_SPLIT_EIGHT_GPU_PASS','unique_gpu_count':8,'role0_uuids':sorted(sets[0]),'role1_uuids':sorted(sets[1])}
(root/'split-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
PY
