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
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/server_args.py').read_bytes()).hexdigest()=='79d9bbb61b429574e31e7a7e319831fcd129a83a475e6ffe2b7e8a5e8eb06b0f', 'Pinned polling source mismatch'
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/managers/scheduler.py').read_bytes()).hexdigest()=='1d4a7683e32f0862cf5b03be33e5ec23f9d112e59546d391e28fa222fcd1619b', 'Pinned polling source mismatch'
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/disaggregation/decode.py').read_bytes()).hexdigest()=='7d7d715013d5a72c1505f9a3a784f87a48938d8d52db6938102865cbd63e954b', 'Pinned polling source mismatch'
print('TRANSFER_POLL_SOURCE_VERIFIED',flush=True)
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/disaggregation/prefill.py').read_bytes()).hexdigest()=='9fd0c9debefae5f4c675a79ad7b62c1a7fe1dc92aeac6cdda12d527e20189af3', 'Pinned cache lifecycle source mismatch'
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/mem_cache/base_prefix_cache.py').read_bytes()).hexdigest()=='9132289aba80c583b596bbaa1af8668a1a14a37f3b382bb91ee41574b5bda53b', 'Pinned cache lifecycle source mismatch'
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/mem_cache/chunk_cache.py').read_bytes()).hexdigest()=='4819830a78b66d94427e235d20883561cb2a965764407184452eeef56f38b549', 'Pinned cache lifecycle source mismatch'
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/mem_cache/common.py').read_bytes()).hexdigest()=='58fe6b674f784c832be6ba2d41c0d7b1f849416acee103d60af438fc0d39fdee', 'Pinned cache lifecycle source mismatch'
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/mem_cache/kv_cache_builder.py').read_bytes()).hexdigest()=='81680be337f7014f5af0bad2e4c4db8166d4a5206ec93ba92e2ed2a0331a97ba', 'Pinned cache lifecycle source mismatch'
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/mem_cache/kv_cache_configurator.py').read_bytes()).hexdigest()=='a99b6e25efcd7c56a72c215fcd98ba7fe70bd53a37e8e4b8cec6205d3c45bdaf', 'Pinned cache lifecycle source mismatch'
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/mem_cache/radix_cache.py').read_bytes()).hexdigest()=='08f04dce327949a48b2f6296cf7e10df59c914eae19df7614e3158242d62f4a6', 'Pinned cache lifecycle source mismatch'
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/mem_cache/registry.py').read_bytes()).hexdigest()=='c2fcca2efdd9ed3a56b947073c004e6e37e84b3c57810a070aee568a326df4dc', 'Pinned cache lifecycle source mismatch'
assert hashlib.sha256(Path('/sgl-workspace/sglang/python/sglang/srt/server_args.py').read_bytes()).hexdigest()=='79d9bbb61b429574e31e7a7e319831fcd129a83a475e6ffe2b7e8a5e8eb06b0f', 'Pinned cache lifecycle source mismatch'
print('CACHE_LIFECYCLE_SOURCE_VERIFIED',flush=True)
PATCHCHECK
export QWEN_ROLE_NAME="$name"
extra=()
if [[ $role == prefill ]]; then
  python3 - <<'PREFILL_HPC_CHECK'
import torch, hpc
assert torch.cuda.get_device_capability()[0] == 9, 'Hopper GPU required'
assert hasattr(hpc, 'fuse_moe_blockwise'), 'Missing HPC-Ops FP8 kernel'
print('PREFILL_HPC_OPS_PREFLIGHT_PASSED', torch.cuda.get_device_name(), flush=True)
PREFILL_HPC_CHECK
  extra=(--chunked-prefill-size 8192 --moe-runner-backend hpc_ops --cuda-graph-backend-prefill breakable)
else
  python3 - <<'HPCCHECK'
import torch, hpc
assert torch.cuda.get_device_capability()[0] == 9, 'Hopper GPU required'
assert hasattr(hpc, 'fuse_moe_blockwise'), 'Missing HPC-Ops FP8 kernel'
print('HPC_OPS_PREFLIGHT_PASSED', torch.cuda.get_device_name(), flush=True)
HPCCHECK
  extra=(--disaggregation-decode-polling-interval 1 --cuda-graph-backend-prefill disabled --cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 --flashinfer-allreduce-fusion-backend mnnvl --decode-attention-backend flashinfer --moe-runner-backend hpc_ops)
fi
if [[ ${QWEN_HAS_DRAFT:-0} == 1 ]]; then
  draft=${QWEN_DRAFT_PATH:-/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09}
  python3 "$QWEN_BUNDLE/draft-fingerprint.py" "$draft" "$QWEN_DRAFT_FULL_VERIFICATION"
  extra+=(--speculative-algorithm EAGLE3 --speculative-draft-model-path "$draft" --speculative-num-steps 2 --speculative-eagle-topk 1 --speculative-num-draft-tokens 3 --speculative-draft-attention-backend flashinfer --speculative-draft-model-quantization unquant)
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
exec python3 -m sglang.launch_server \
  --model-path "$model" --served-model-name qwen --trust-remote-code \
  --context-length 8192 --tp-size "$tp" --mem-fraction-static 0.90 \
  --disaggregation-mode "$role" --disaggregation-transfer-backend nixl \
  --dtype bfloat16 "${telemetry_flags[@]}" "${extra[@]}" "$@" --host 0.0.0.0 --port "$port"
