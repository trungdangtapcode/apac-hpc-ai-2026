#!/bin/bash
set -euo pipefail
bundle=$1; art=$2
export HOME=/tmp/ap42-home XDG_CACHE_HOME=/tmp/ap42-home/.cache HF_HOME=/tmp/ap42-home/.cache/huggingface
mkdir -p "$HOME" "$XDG_CACHE_HOME" "$HF_HOME"
python3 - "$bundle" <<'CHECK'
import hashlib,json,sys,os,torch
from pathlib import Path
for name,wanted in json.loads((Path(sys.argv[1])/'expected-source.json').read_text()).items():
 assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==wanted,'Native graph source mismatch'
assert torch.cuda.device_count()==4
assert len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))==4
assert all(torch.cuda.get_device_capability(i)[0]==9 for i in range(4))
print('SOURCE_AND_FOUR_HOPPER_DEVICES_VERIFIED',flush=True)
CHECK
export QWEN_BUNDLE="$bundle" QWEN_ARTDIR="$art" QWEN_RESOURCE_MONITOR=1 QWEN_TELEMETRY_MAX_S=1200
export QWEN_NIXL_PATCH_SHA256=912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f
exec bash "$bundle/worker.sh" prefill-0 30100 /scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8 4 \
 --nccl-port 20000 --disaggregation-bootstrap-port 8998 --cuda-graph-backend-prefill disabled
