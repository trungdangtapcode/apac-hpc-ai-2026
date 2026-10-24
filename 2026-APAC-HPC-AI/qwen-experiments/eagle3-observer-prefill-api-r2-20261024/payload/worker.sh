#!/bin/bash
set -euo pipefail
export SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT=600
export SGLANG_DISAGGREGATION_WAITING_TIMEOUT=600
name=$1
port=$2
model=$3
tp=$4
shift 4
role=${name%%-*}
[[ "$name" == prefill-0 && "$role" == prefill && "$tp" == 4 ]]
export QWEN_ROLE_NAME="$name"
UCX_IB=$(for d in /sys/class/infiniband/*; do
  [ "$(cat "$d/ports/1/link_layer" 2>/dev/null)" = InfiniBand ] || continue
  [ "$(cat "$d/ports/1/state" 2>/dev/null)" = "4: ACTIVE" ] || continue
  echo "$(basename "$d"):1"
done | paste -sd,)
[ -n "$UCX_IB" ] || { echo "FATAL: no active IB on $(hostname)"; exit 1; }
export UCX_NET_DEVICES=$UCX_IB UCX_POSIX_USE_PROC_LINK=n
export TRITON_CACHE_DIR=/tmp/sglang-$name/triton TORCHINDUCTOR_CACHE_DIR=/tmp/sglang-$name/inductor
mkdir -p "$TRITON_CACHE_DIR" "$TORCHINDUCTOR_CACHE_DIR"
echo "$name host=$(hostname) ib=$UCX_IB gpu=$CUDA_VISIBLE_DEVICES tp=$tp"

python3 - <<'PATCHCHECK'
import hashlib,os
from pathlib import Path
p=Path('/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py')
actual=hashlib.sha256(p.read_bytes()).hexdigest()
assert actual==os.environ['QWEN_NIXL_PATCH_SHA256'], 'NIXL source hash mismatch'
print('NIXL_PATCH_VERIFIED',actual,flush=True)
PATCHCHECK

python3 - <<'HPCCHECK'
import torch,hpc
assert torch.cuda.device_count()==4
assert torch.cuda.get_device_capability()[0]==9
assert 'H100' in torch.cuda.get_device_name().upper()
assert hasattr(hpc,'fuse_moe_blockwise')
print('HPC_OPS_PREFLIGHT_PASSED',torch.cuda.get_device_name(),flush=True)
HPCCHECK

export SGLANG_ENABLE_TORCH_INFERENCE_MODE=0
python3 - <<'MODECHECK'
import hashlib,os,torch
from pathlib import Path
from sglang.srt.utils.common import DynamicGradMode,_ENABLE_TORCH_INFERENCE_MODE
expected_sources={'/sgl-workspace/sglang/python/sglang/srt/utils/common.py':'e1fc22ba7508205a32188dd1cb5b43201973468cb495ae492f8b523d28b3b446','/sgl-workspace/sglang/python/sglang/srt/managers/scheduler.py':'1d4a7683e32f0862cf5b03be33e5ec23f9d112e59546d391e28fa222fcd1619b'}
for p,h in expected_sources.items(): assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
assert not _ENABLE_TORCH_INFERENCE_MODE and not torch.is_inference_mode_enabled()
with DynamicGradMode(): assert not torch.is_inference_mode_enabled() and not torch.is_grad_enabled()
print('DYNAMIC_GRAD_MODE_PREFLIGHT_PASSED inference_mode=False',flush=True)
MODECHECK

draft=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/drafts/nebius-eagle3-qwen235b-ff0f0c09
python3 "$QWEN_BUNDLE/verify-draft.py" "$draft"
extra=(--chunked-prefill-size 4096 --weight-loader-prefetch-checkpoints
       --moe-runner-backend hpc_ops --cuda-graph-backend-prefill disabled)
extra+=(--speculative-algorithm EAGLE3 --speculative-draft-model-path "$draft"
        --speculative-num-steps 2 --speculative-eagle-topk 1 --speculative-num-draft-tokens 3
        --speculative-draft-attention-backend flashinfer --dtype bfloat16
        --speculative-draft-model-quantization unquant)

# Load the metadata observer in the serving Python process only after all preflight imports.
export PYTHONPATH="$QWEN_BUNDLE/pd-observer${PYTHONPATH:+:$PYTHONPATH}"
echo "PD_OBSERVER_PREFLIGHT_READY role=$name"
python3 -m sglang.launch_server \
  --model-path "$model" --served-model-name qwen --trust-remote-code \
  --context-length 8192 --tp-size "$tp" --mem-fraction-static 0.90 \
  --disaggregation-mode "$role" --disaggregation-transfer-backend nixl \
  "${extra[@]}" "$@" --host 0.0.0.0 --port "$port" &
server_pid=$!
cleanup() {
  trap - EXIT TERM INT
  kill -TERM "$server_pid" 2>/dev/null || :
  local end=$((SECONDS+8))
  while kill -0 "$server_pid" 2>/dev/null && (( SECONDS<end )); do sleep 1; done
  kill -KILL "$server_pid" 2>/dev/null || :
  wait "$server_pid" 2>/dev/null || :
}
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
wait "$server_pid"
