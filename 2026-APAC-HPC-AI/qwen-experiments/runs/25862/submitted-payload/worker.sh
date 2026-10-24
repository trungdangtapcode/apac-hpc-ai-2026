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
export QWEN_ROLE_NAME="$name"
extra=()
if [[ $role == prefill ]]; then
  extra=(--chunked-prefill-size 8192 --moe-runner-backend deep_gemm --cuda-graph-backend-prefill disabled)
else
  python3 - <<'HPCCHECK'
import torch, hpc
assert torch.cuda.get_device_capability()[0] == 9, 'Hopper GPU required'
assert hasattr(hpc, 'fuse_moe_blockwise'), 'Missing HPC-Ops FP8 kernel'
print('HPC_OPS_PREFLIGHT_PASSED', torch.cuda.get_device_name(), flush=True)
HPCCHECK
  extra=(--cuda-graph-backend-prefill disabled --cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 --flashinfer-allreduce-fusion-backend mnnvl --decode-attention-backend flashinfer --moe-runner-backend hpc_ops)
fi
draft=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09
python3 "$QWEN_BUNDLE/draft-fingerprint.py" "$draft" "$QWEN_DRAFT_FULL_VERIFICATION"
extra+=(--speculative-algorithm EAGLE3 --speculative-draft-model-path "$draft" --speculative-num-steps 2 --speculative-eagle-topk 1 --speculative-num-draft-tokens 3 --speculative-draft-attention-backend flashinfer --dtype bfloat16 --speculative-draft-model-quantization unquant)
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
  --enable-deterministic-inference "${telemetry_flags[@]}" "${extra[@]}" "$@" --host 0.0.0.0 --port "$port"
