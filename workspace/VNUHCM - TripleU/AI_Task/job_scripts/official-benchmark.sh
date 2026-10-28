#!/usr/bin/env bash
set -euo pipefail
HOST=$1
ART=$2
TASK_SCRIPTS=$3
N=${TRIPLEU_CONCURRENCY:-64}
MODEL=qwen
RUN="$ART/official/n${N}"
mkdir -p "$RUN"
export HF_HUB_CACHE="$TASK_SCRIPTS/hf-cache"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
python3 - <<'VERSIONS' >"$ART/client-versions.txt"
from importlib.metadata import version
for package in ('aiperf','transformers','tokenizers'):
    print(package, version(package))
VERSIONS
python3 - <<'TOKENIZER' >"$ART/tokenizer-preflight.log" 2>&1
from aiperf.common.tokenizer import Tokenizer
t=Tokenizer.from_pretrained('Qwen/Qwen3-235B-A22B-Instruct-2507')
print('AIPerf tokenizer OK:', len(t.encode('Hello world')), flush=True)
TOKENIZER
cd "$RUN"
echo "START official N=$N at $(date -Iseconds)"
# Exact official client command from Task Rules. The working directory controls
# the default artifact location; no extra benchmark flags are added.
aiperf profile \
  --url "http://${HOST}" \
  --endpoint-type chat \
  --endpoint /v1/chat/completions \
  --model "${MODEL}" \
  --tokenizer Qwen/Qwen3-235B-A22B-Instruct-2507 \
  --streaming \
  -H 'Accept: text/event-stream' \
  --concurrency "${N}" \
  --workers-max "${N}" \
  --api-key NOT_USED \
  --warmup-duration 60 \
  --benchmark-duration 120 \
  --benchmark-grace-period 30 \
  --synthetic-input-tokens-mean 4000 \
  --synthetic-input-tokens-stddev 0 \
  --output-tokens-mean 200 \
  --output-tokens-stddev 0 \
  --extra-inputs min_tokens:200 \
  --extra-inputs max_tokens:200 \
  --extra-inputs ignore_eos:true \
  --extra-inputs temperature:0.0 \
  --extra-inputs repetition_penalty:1.0 \
  --num-dataset-entries 12800 \
  --random-seed 2026 \
  --cache-bust first_turn_prefix \
  --goodput "time_to_first_token:3000 inter_token_latency:20" \
  --ui simple >"$RUN/client.log" 2>&1
echo "DONE official N=$N at $(date -Iseconds)"
