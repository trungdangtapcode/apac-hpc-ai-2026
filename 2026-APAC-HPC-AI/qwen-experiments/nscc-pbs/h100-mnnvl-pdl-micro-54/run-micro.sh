#!/bin/bash
set -euo pipefail
cache=/tmp/ap42-mnnvl-micro
mkdir -p "$cache/flashinfer" "$cache/triton" "$cache/inductor" "$cache/torch-extensions"
export FLASHINFER_WORKSPACE_BASE=$cache/flashinfer
export TRITON_CACHE_DIR=$cache/triton
export TORCHINDUCTOR_CACHE_DIR=$cache/inductor
export TORCH_EXTENSIONS_DIR=$cache/torch-extensions
export OMP_NUM_THREADS=1
export GLOO_SOCKET_IFNAME=lo
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec python3 -m torch.distributed.run --standalone --nnodes=1 --nproc-per-node=8 \
  "$script_dir/bench.py" --out "$1"
