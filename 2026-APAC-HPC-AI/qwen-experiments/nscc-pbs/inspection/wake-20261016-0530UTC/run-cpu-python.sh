#!/bin/bash
set -eu
export PYTHONHOME=/tmp/ap42-token-suite-aiperf-20261016/usr/local
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 RAYON_NUM_THREADS=2
export TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
exec /tmp/ap42-token-suite-aiperf-20261016/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 \
  --library-path /tmp/ap42-token-suite-aiperf-20261016/usr/local/lib:/tmp/ap42-token-suite-aiperf-20261016/usr/lib/x86_64-linux-gnu \
  /tmp/ap42-token-suite-aiperf-20261016/usr/local/bin/python3 "$@"
