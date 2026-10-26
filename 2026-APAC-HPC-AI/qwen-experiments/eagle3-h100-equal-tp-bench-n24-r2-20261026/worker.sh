#!/usr/bin/env bash
set -euo pipefail
export SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT=600
export SGLANG_DISAGGREGATION_WAITING_TIMEOUT=600
name=$1
export QWEN_ROLE_NAME="$name"
port=$2
model=$3
tp=$4
shift 4
[[ $tp == 4 ]] || { echo 'FATAL: both P and D workers require TP4' >&2; exit 2; }
role=${name%%-*}
[[ $name == prefill-0 || $name == decode-0 ]] || { echo "FATAL: unexpected worker $name" >&2; exit 2; }
if [[ $role == prefill ]]; then expected_gpu_ids='0,1,2,3'; else expected_gpu_ids='4,5,6,7'; fi
[[ ${QWEN_ASSIGNED_GPU_INDICES:-} == "$expected_gpu_ids" ]] || {
  echo "FATAL: $name expected PBS GPU indices $expected_gpu_ids, got ${QWEN_ASSIGNED_GPU_INDICES:-missing}" >&2; exit 2;
}
mkdir -p "$QWEN_ARTDIR" "$QWEN_ARTDIR/observer"
python3 "$QWEN_BUNDLE/device_preflight.py"
UCX_IB=$(for d in /sys/class/infiniband/*; do
  [ "$(cat "$d/ports/1/link_layer" 2>/dev/null)" = InfiniBand ] || continue
  [ "$(cat "$d/ports/1/state" 2>/dev/null)" = "4: ACTIVE" ] || continue
  echo "$(basename "$d"):1"
done | paste -sd,)
[ -n "$UCX_IB" ] || { echo "FATAL: no active IB on $(hostname)"; exit 1; }
export UCX_NET_DEVICES=$UCX_IB UCX_POSIX_USE_PROC_LINK=n
export TRITON_CACHE_DIR="/tmp/sglang-$name/triton" TORCHINDUCTOR_CACHE_DIR="/tmp/sglang-$name/inductor"
mkdir -p "$TRITON_CACHE_DIR" "$TORCHINDUCTOR_CACHE_DIR"
echo "$name host=$(hostname) ib=$UCX_IB gpu=$CUDA_VISIBLE_DEVICES tp=$tp"
python3 - <<'PATCHCHECK'
import hashlib,os
from pathlib import Path
actual=hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py').read_bytes()).hexdigest()
assert actual==os.environ['QWEN_NIXL_PATCH_SHA256'], 'NIXL patch mount/hash mismatch'
print('NIXL_PATCH_VERIFIED',actual,flush=True)
PATCHCHECK
python3 "$QWEN_BUNDLE/capture-worker-locality.py" --root "$$" --role "$name" \
  --artifact "$QWEN_ARTDIR" --timeout 900 >"$QWEN_ARTDIR/$name-locality.log" 2>&1 &
echo "WORKER_LOCALITY_OBSERVER pid=$! role=$name"
python3 - <<'HPCCHECK'
import torch, hpc
assert torch.cuda.get_device_capability()[0] == 9, 'Hopper GPU required'
assert hasattr(hpc, 'fuse_moe_blockwise'), 'Missing HPC-Ops FP8 kernel'
print('HPC_OPS_PREFLIGHT_PASSED', torch.cuda.get_device_name(), flush=True)
HPCCHECK
export SGLANG_ENABLE_TORCH_INFERENCE_MODE=0
python3 - <<'MODECHECK'
import hashlib, os, torch
from pathlib import Path
from sglang.srt.utils.common import DynamicGradMode, _ENABLE_TORCH_INFERENCE_MODE
expected_sources = {
 '/sgl-workspace/sglang/python/sglang/srt/utils/common.py': 'e1fc22ba7508205a32188dd1cb5b43201973468cb495ae492f8b523d28b3b446',
 '/sgl-workspace/sglang/python/sglang/srt/managers/scheduler.py': '1d4a7683e32f0862cf5b03be33e5ec23f9d112e59546d391e28fa222fcd1619b'}
for filename, expected_hash in expected_sources.items():
 assert hashlib.sha256(Path(filename).read_bytes()).hexdigest()==expected_hash
assert os.environ.get('SGLANG_ENABLE_TORCH_INFERENCE_MODE','0')=='0'
assert _ENABLE_TORCH_INFERENCE_MODE is False and not torch.is_inference_mode_enabled()
with DynamicGradMode(): assert not torch.is_inference_mode_enabled() and not torch.is_grad_enabled()
print('DYNAMIC_GRAD_MODE_PREFLIGHT_PASSED inference_mode=false',flush=True)
MODECHECK
extra=()
if [[ $role == prefill ]]; then
  extra=(--chunked-prefill-size 4096 --weight-loader-prefetch-checkpoints
         --moe-runner-backend hpc_ops --cuda-graph-backend-prefill disabled)
else
  graph_bs=(); for i in $(seq 1 64); do graph_bs+=("$i"); done
  extra=(--ep-size 4 --max-running-requests 256 --cuda-graph-backend-prefill disabled
         --cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode "${graph_bs[@]}"
         --flashinfer-allreduce-fusion-backend mnnvl --decode-attention-backend flashinfer
         --moe-runner-backend hpc_ops)
fi
telemetry_flags=()
if [[ ${QWEN_RESOURCE_MONITOR:-0} == 1 ]]; then
  telemetry_flags=(--enable-metrics)
  mkdir -p "$QWEN_ARTDIR/resource-telemetry"
  python3 "$QWEN_BUNDLE/resource-sampler.py" --out "$QWEN_ARTDIR/resource-telemetry" \
    --role "$name" --port "$port" --parent "$$" --gpus "${CUDA_VISIBLE_DEVICES:-}" \
    --interval 5 --duration "$QWEN_TELEMETRY_MAX_S" \
    >"$QWEN_ARTDIR/resource-telemetry/$name-sampler.log" 2>&1 &
fi
draft=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/drafts/nebius-eagle3-qwen235b-ff0f0c09
python3 "$QWEN_BUNDLE/verify-draft.py" "$draft"
export PYTHONPATH="$QWEN_BUNDLE/pd-observer${PYTHONPATH:+:$PYTHONPATH}"
echo "PD_OBSERVER_PYTHONPATH_READY role=$name"
extra+=(--speculative-algorithm EAGLE3 --speculative-draft-model-path "$draft"
        --speculative-num-steps 2 --speculative-eagle-topk 1 --speculative-num-draft-tokens 3
        --speculative-draft-attention-backend flashinfer --dtype bfloat16
        --speculative-draft-model-quantization unquant)
export D5_OBSERVER_DIR="$QWEN_ARTDIR/observer"
exec python3 -m sglang.launch_server --model-path "$model" --served-model-name qwen --trust-remote-code \
  --context-length 8192 --tp-size 4 --mem-fraction-static 0.90 \
  --disaggregation-mode "$role" --disaggregation-transfer-backend nixl \
  "${telemetry_flags[@]}" "${extra[@]}" "$@" --host 0.0.0.0 --port "$port"
