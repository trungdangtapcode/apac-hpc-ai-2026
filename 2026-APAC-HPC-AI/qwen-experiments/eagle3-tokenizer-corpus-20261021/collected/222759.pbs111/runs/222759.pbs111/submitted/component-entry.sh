#!/usr/bin/env bash
set -euo pipefail
bundle=$1
art=$2
model=$3
mkdir -p "$HOME" "$XDG_CACHE_HOME" "$TORCH_EXTENSIONS_DIR" "$CUDA_CACHE_PATH"
python3 "$bundle/tokenizer-probe.py" --model "$model" --out "$art/tokenizer-corpus.json" >"$art/tokenizer-probe.log" 2>&1
