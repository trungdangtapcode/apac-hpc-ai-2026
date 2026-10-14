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
  extra=(--chunked-prefill-size 4096)
else
  extra=(--cuda-graph-max-bs-decode 64 --moe-runner-backend deep_gemm)
fi
exec python3 -m sglang.launch_server \
  --model-path "$model" --served-model-name qwen --trust-remote-code \
  --context-length 8192 --tp-size "$tp" --mem-fraction-static 0.90 \
  --disaggregation-mode "$role" --disaggregation-transfer-backend nixl \
  "${extra[@]}" "$@" --host 0.0.0.0 --port "$port"
