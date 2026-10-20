set -euo pipefail
export SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT=600
export SGLANG_DISAGGREGATION_WAITING_TIMEOUT=600
name=$1
port=$2
model=$3
tp=$4
shift 4
role=${name%%-*}
UCX_IB=$(for d in /sys/class/infiniband/*; do
  [ "$(cat "$d/ports/1/link_layer" 2>/dev/null)" = InfiniBand ] || continue
  [ "$(cat "$d/ports/1/state" 2>/dev/null)" = "4: ACTIVE" ] || continue
  echo "$(basename "$d"):1"
done | paste -sd,)
[ -n "$UCX_IB" ] || { echo "FATAL: no active IB on $(hostname)"; exit 1; }
export UCX_NET_DEVICES=$UCX_IB
export UCX_POSIX_USE_PROC_LINK=n
export TRITON_CACHE_DIR=/tmp/sglang-$name/triton
export TORCHINDUCTOR_CACHE_DIR=/tmp/sglang-$name/inductor
mkdir -p "$TRITON_CACHE_DIR" "$TORCHINDUCTOR_CACHE_DIR"
echo "$name host=$(hostname) ib=$UCX_IB gpu=$CUDA_VISIBLE_DEVICES tp=$tp"
python3 - <<'PATCHCHECK'
import hashlib,os
from pathlib import Path
path=Path('/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py')
actual=hashlib.sha256(path.read_bytes()).hexdigest()
assert actual==os.environ['QWEN_NIXL_PATCH_SHA256'], 'NIXL patch mount/hash mismatch'
print('NIXL_PATCH_VERIFIED',actual,flush=True)
PATCHCHECK
extra=()
if [[ $role == prefill ]]; then
  python3 - <<'HPCCHECK'
import torch, hpc
assert torch.cuda.get_device_capability()[0] == 9, 'Hopper GPU required'
assert hasattr(hpc, 'fuse_moe_blockwise'), 'Missing HPC-Ops FP8 kernel'
print('HPC_OPS_PREFLIGHT_PASSED', torch.cuda.get_device_name(), flush=True)
HPCCHECK
  extra=(--chunked-prefill-size 8192 --weight-loader-prefetch-checkpoints --moe-runner-backend hpc_ops)
else
  python3 - <<'HPCCHECK'
import torch, hpc
assert torch.cuda.get_device_capability()[0] == 9, 'Hopper GPU required'
assert hasattr(hpc, 'fuse_moe_blockwise'), 'Missing HPC-Ops FP8 kernel'
print('HPC_OPS_PREFLIGHT_PASSED', torch.cuda.get_device_name(), flush=True)
HPCCHECK
  extra=(--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 --flashinfer-allreduce-fusion-backend mnnvl --decode-attention-backend flashinfer --moe-runner-backend hpc_ops)
fi
# Set before importing the server's DynamicGradMode decorator.
export SGLANG_ENABLE_TORCH_INFERENCE_MODE=0
if [[ $role == decode ]]; then
  export SGLANG_ENABLE_TORCH_INFERENCE_MODE=0
fi
python3 - <<'MODECHECK'
import hashlib, os, torch
from pathlib import Path
from sglang.srt.utils.common import DynamicGradMode, _ENABLE_TORCH_INFERENCE_MODE
expected_sources = {'/sgl-workspace/sglang/python/sglang/srt/utils/common.py': 'e1fc22ba7508205a32188dd1cb5b43201973468cb495ae492f8b523d28b3b446', '/sgl-workspace/sglang/python/sglang/srt/managers/scheduler.py': '1d4a7683e32f0862cf5b03be33e5ec23f9d112e59546d391e28fa222fcd1619b'}
for filename, expected_hash in expected_sources.items():
    assert hashlib.sha256(Path(filename).read_bytes()).hexdigest() == expected_hash
expected = os.environ['SGLANG_ENABLE_TORCH_INFERENCE_MODE'] == '1'
assert _ENABLE_TORCH_INFERENCE_MODE == expected
assert not torch.is_inference_mode_enabled()
with DynamicGradMode():
    assert torch.is_inference_mode_enabled() == expected
    assert not torch.is_grad_enabled()
print('DYNAMIC_GRAD_MODE_PREFLIGHT_PASSED', 'inference_mode=' + str(expected), flush=True)
MODECHECK
telemetry_flags=()
if [[ ${QWEN_RESOURCE_MONITOR:-0} == 1 ]]; then
  telemetry_flags=(--enable-metrics)
  mkdir -p "$QWEN_ARTDIR/resource-telemetry"
  python3 "$QWEN_BUNDLE/resource-sampler.py" --out "$QWEN_ARTDIR/resource-telemetry" \
    --role "$name" --port "$port" --parent "$$" --gpus "${CUDA_VISIBLE_DEVICES:-}" \
    --interval 5 --duration "$QWEN_TELEMETRY_MAX_S" \
    >"$QWEN_ARTDIR/resource-telemetry/$name-sampler.log" 2>&1 &
fi
exec python3 -m sglang.launch_server \
  --model-path "$model" --served-model-name qwen --trust-remote-code \
  --context-length 8192 --tp-size "$tp" --mem-fraction-static 0.90 \
  --disaggregation-mode "$role" --disaggregation-transfer-backend nixl \
  "${telemetry_flags[@]}" "${extra[@]}" "$@" --host 0.0.0.0 --port "$port"
