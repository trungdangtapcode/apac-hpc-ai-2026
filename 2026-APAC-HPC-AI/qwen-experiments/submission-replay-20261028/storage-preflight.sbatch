#!/usr/bin/env bash
#SBATCH -J ap42-pack-disk
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:0
#SBATCH -t 00:02:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
Q=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments
mkdir -p "$Q/runs/$SLURM_JOB_ID"
srun --exact -N2 -n2 --ntasks-per-node=1 --gres=gpu:0 python3 "$Q/submission-replay-20261028/storage-preflight.py" >"$Q/runs/$SLURM_JOB_ID/storage-nodes.jsonl"
python3 - "$Q/runs/$SLURM_JOB_ID" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1]);rows=[json.loads(x) for x in (p/'storage-nodes.jsonl').read_text().splitlines() if x.strip()]
assert len(rows)==2 and {r['rank'] for r in rows}=={0,1}
state='PORTABLE_PYXIS_CAPACITY_READY' if all(r['capacity_ok'] for r in rows) else 'PORTABLE_PYXIS_CAPACITY_BLOCKED'
(p/'storage-proof.json').write_text(json.dumps({'state':state,'nodes':rows},indent=2)+'\n');print(state)
PY
