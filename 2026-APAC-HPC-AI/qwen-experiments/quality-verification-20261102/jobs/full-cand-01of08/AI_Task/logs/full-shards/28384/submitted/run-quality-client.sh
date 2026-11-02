#!/usr/bin/env bash
set -euo pipefail
BASE=$1
ART=$2
JOB_START=$3
STUDY=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102
python3 - <<'VERSIONS' >"$ART/quality-client-versions.json"
import os,sys,json
from importlib.metadata import version
print(json.dumps({'python':sys.version,'transformers':version('transformers'),'tokenizers':version('tokenizers'),'phase':'full-quality-shard','shard_index':int(os.environ['TRIPLEU_QUALITY_SHARD_INDEX']),'shard_count':int(os.environ['TRIPLEU_QUALITY_SHARD_COUNT']),'concurrency':int(os.environ['TRIPLEU_QUALITY_CONCURRENCY'])},indent=2))
VERSIONS
python3 "$STUDY/client/quality_client.py" run \
  --corpus "$STUDY/prepared-4k/compiled-corpus.jsonl" \
  --prepare-manifest "$STUDY/prepared-4k/prepare-manifest.json" \
  --shard-index "$TRIPLEU_QUALITY_SHARD_INDEX" --shard-count "$TRIPLEU_QUALITY_SHARD_COUNT" \
  --base-url "$BASE" --model qwen --out "$ART/evaluation" \
  --concurrency "${TRIPLEU_QUALITY_CONCURRENCY:-64}" --timeout 120 --deadline-margin 10 --deadline-epoch "$((JOB_START+950))" \
  >"$ART/quality-client.log" 2>&1
echo "FULL_SHARD_CLIENT_COMPLETE index=${TRIPLEU_QUALITY_SHARD_INDEX}/${TRIPLEU_QUALITY_SHARD_COUNT} concurrency=${TRIPLEU_QUALITY_CONCURRENCY}"
