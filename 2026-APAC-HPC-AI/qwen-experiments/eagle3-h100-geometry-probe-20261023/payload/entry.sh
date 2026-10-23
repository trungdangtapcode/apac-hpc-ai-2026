#!/bin/bash
set -euo pipefail
bundle=$1
art=$2
experiment_id=$3
job_id=$4
[[ -n "$experiment_id" && "$experiment_id" == "$QWEN_EXPERIMENT_ID" ]]
[[ "$job_id" == "$QWEN_PBS_JOB_ID" ]]
[[ "$experiment_id" =~ ^ap42-e3-h100-geometry-[A-Za-z0-9_.-]+-[a-f0-9]{32}$ ]]
python3 - "$art/experiment-context.json" "$experiment_id" "$job_id" <<'CONTEXT'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
context = json.loads(path.read_text())
assert context["experiment_id"] == sys.argv[2]
assert context["pbs_job_id"] == sys.argv[3]
CONTEXT
export HOME=/tmp/ap42-h100-geometry-home
export XDG_CACHE_HOME="$HOME/.cache"
export HF_HOME="$HOME/.cache/huggingface"
mkdir -p "$HOME" "$XDG_CACHE_HOME" "$HF_HOME"

python3 - "$bundle" <<'CHECK'
import hashlib
import json
import os
import sys
import torch
from pathlib import Path

bundle = Path(sys.argv[1])
expected = json.loads((bundle / "expected-source.json").read_text())
for path, digest in expected.items():
    actual = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    assert actual == digest, f"Native graph source mismatch: {path}"
assert torch.cuda.device_count() == 4
visible = os.environ["CUDA_VISIBLE_DEVICES"].split(",")
assert len(visible) == 4
names = [torch.cuda.get_device_name(i) for i in range(4)]
assert all(torch.cuda.get_device_capability(i)[0] == 9 for i in range(4))
assert all("H100" in name.upper() for name in names), f"Expected four H100 GPUs, found {names}"
print("NATIVE_GRAPH_SOURCE_VERIFIED", json.dumps(expected, sort_keys=True), flush=True)
print("H100_RUNTIME_VERIFIED", json.dumps(names), flush=True)
CHECK

export QWEN_BUNDLE="$bundle" QWEN_ARTDIR="$art"
export QWEN_RESOURCE_MONITOR=1 QWEN_TELEMETRY_MAX_S=1200
export QWEN_NIXL_PATCH_SHA256=45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8
export QWEN_ROLE_NAME=prefill-0
# QWEN_EXPERIMENT_ID is injected explicitly by the clean-environment container launcher.
exec bash "$bundle/worker.sh" prefill-0 30100 \
  /scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8 4 \
  --nccl-port 20000 --disaggregation-bootstrap-port 8998 \
  --cuda-graph-backend-prefill disabled
