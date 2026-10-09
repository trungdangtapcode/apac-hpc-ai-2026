#!/usr/bin/env bash
# Official benchmark CLIENT step only. Deploy the gateway earlier in the same job.
# Run inside the AIPerf environment; preserve an output directory per run.
set -euo pipefail
if [[ $# -ne 3 ]]; then
  echo 'Usage: bash official-aiperf.sh GATEWAY_HOST:PORT SERVED_MODEL_ID CONCURRENCY' >&2
  exit 2
fi
HOST=$1
MODEL=$2
N=$3
if ! [[ "$N" =~ ^[1-9][0-9]*$ ]]; then
  echo 'CONCURRENCY must be a positive integer' >&2
  exit 2
fi
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
  --ui simple
