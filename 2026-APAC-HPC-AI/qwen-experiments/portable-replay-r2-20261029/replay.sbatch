#!/usr/bin/env bash
#SBATCH -J ap42-portable-r2
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --exclusive
#SBATCH --propagate=NONE
#SBATCH -o /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/%j.out
#SBATCH -e /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/%j.err
set -euo pipefail
Q=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments
D=$Q/portable-replay-r2-20261029
B="$D/VNUHCM - TripleU/AI_Task/job_scripts"
A="$Q/runs/$SLURM_JOB_ID"
mkdir -p "$A"
export APAC_PORTABLE_ALLOCATION_START=$(date +%s)
printf 'PORTABLE_REPLAY_ALLOCATION_START epoch=%s\n' "$APAC_PORTABLE_ALLOCATION_START"
[[ "$SLURM_SUBMIT_DIR" == "$B" ]] || { echo 'Unexpected submission directory'; exit 1; }
python3 - "$D" "$B" <<'PY'
import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1]);b=Path(sys.argv[2])
p=json.loads((root.parent/'runs/26988/storage-proof.json').read_text())
assert p['state']=='PORTABLE_PYXIS_CAPACITY_READY'
f=json.loads((root/'FROZEN_SUBMISSION.json').read_text())
for name,wanted in f['file_sha256'].items():assert hashlib.sha256((b/name).read_bytes()).hexdigest()==wanted,name
print('FROZEN_PORTABLE_ENTRY_HASHES_VERIFIED')
PY
# Recheck the allocated nodes; an earlier CPU-only check is not a live guarantee.
timeout --signal=TERM --kill-after=5s 30 srun --exact -N2 -n2 --ntasks-per-node=1 \
  --cpus-per-task=2 --gres=gpu:0 python3 "$Q/submission-replay-20261028/storage-preflight.py" >"$A/storage-nodes.jsonl"
python3 - "$A" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);rows=[json.loads(x) for x in (p/'storage-nodes.jsonl').read_text().splitlines() if x.strip()]
assert len(rows)==2 and {x['rank'] for x in rows}=={0,1}
state='LIVE_CAPACITY_READY' if all(x['capacity_ok'] for x in rows) else 'LIVE_CAPACITY_BLOCKED'
(p/'storage-proof.json').write_text(json.dumps({'state':state,'nodes':rows},indent=2)+'\n')
assert state=='LIVE_CAPACITY_READY','Do not start model extraction after blocked capacity guard'
PY
printf 'UNCHANGED_PACKAGED_ENTRY_BEGIN epoch=%s\n' "$(date +%s)"
# The entry below is byte-identical to the published package. Its own clock
# starts here; the scheduler still enforces the complete 17-minute allocation.
cd "$B"
exec bash "$B/submit.sbatch"
