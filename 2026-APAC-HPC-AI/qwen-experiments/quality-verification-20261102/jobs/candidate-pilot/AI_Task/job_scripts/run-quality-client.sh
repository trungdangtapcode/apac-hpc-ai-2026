#!/usr/bin/env bash
set -euo pipefail
BASE=$1
ART=$2
JOB_START=$3
STUDY=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102
python3 - <<'VERSIONS' >"$ART/quality-client-versions.json"
import sys,json
from importlib.metadata import version
print(json.dumps({'python':sys.version,'transformers':version('transformers'),'tokenizers':version('tokenizers')},indent=2))
VERSIONS
python3 "$STUDY/client/quality_client.py" run \
  --corpus "$STUDY/prepared-4k/compiled-corpus.jsonl" \
  --prepare-manifest "$STUDY/prepared-4k/prepare-manifest.json" \
  --ids-file "$STUDY/prepared-4k/pilot-ids.json" \
  --base-url "$BASE" --model qwen --out "$ART/evaluation" \
  --concurrency "${TRIPLEU_QUALITY_CONCURRENCY:-16}" --timeout 120 --deadline-margin 10 --deadline-epoch "$((JOB_START+950))" \
  >"$ART/quality-client.log" 2>&1
