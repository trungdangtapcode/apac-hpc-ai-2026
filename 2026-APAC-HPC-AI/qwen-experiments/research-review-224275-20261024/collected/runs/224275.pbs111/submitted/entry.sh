#!/bin/bash
set -euo pipefail
bundle=$1
art=$2
experiment_id=$3
job_id=$4
[[ -n "$experiment_id" && "$experiment_id" == "$QWEN_EXPERIMENT_ID" ]]
[[ "$job_id" == "$QWEN_PBS_JOB_ID" ]]
[[ "$experiment_id" =~ ^ap42-observer-prefill-[A-Za-z0-9_.-]+-[a-f0-9]{32}$ ]]
export HOME=/tmp/ap42-observer-prefill-home
export XDG_CACHE_HOME="$HOME/.cache" HF_HOME="$HOME/.cache/huggingface"
mkdir -p "$HOME" "$XDG_CACHE_HOME" "$HF_HOME"

python3 - "$bundle" <<'CHECK'
import hashlib,json,os,sys,torch
from pathlib import Path
bundle=Path(sys.argv[1])
expected=json.loads((bundle/'expected-source.json').read_text())
for path,digest in expected.items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest, f'native source mismatch: {path}'
assert torch.cuda.device_count()==4
visible=os.environ['CUDA_VISIBLE_DEVICES'].split(',')
assert len(visible)==4
names=[torch.cuda.get_device_name(i) for i in range(4)]
assert all(torch.cuda.get_device_capability(i)[0]==9 for i in range(4))
assert all('H100' in name.upper() for name in names),names
print('NATIVE_GRAPH_SOURCE_VERIFIED',json.dumps(expected,sort_keys=True),flush=True)
print('H100_RUNTIME_VERIFIED',json.dumps(names),flush=True)
CHECK

export QWEN_BUNDLE="$bundle" QWEN_ARTDIR="$art" QWEN_ROLE_NAME=prefill-0
export QWEN_NIXL_PATCH_SHA256=912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f
exec /bin/bash "$bundle/worker.sh" prefill-0 30100 \
  /scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8 4 \
  --nccl-port 20000 --disaggregation-bootstrap-port 8998 \
  --cuda-graph-backend-prefill disabled
