#!/usr/bin/env bash
set -euo pipefail
bundle=$1
art=$2
draft=$3
mkdir -p "$HOME" "$XDG_CACHE_HOME" "$TORCH_EXTENSIONS_DIR" "$CUDA_CACHE_PATH"
python3 "$bundle/dtype-probe.py" --draft "$draft" --target /scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8 --out "$art/dtype-probe.json" >"$art/dtype-probe.log" 2>&1
