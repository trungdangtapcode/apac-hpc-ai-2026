#!/bin/bash
set -euo pipefail
policy=$1
shift
python3 "$QWEN_BUNDLE/router-preflight.py" "$policy"
exec python3 -m sglang_router.launch_router --pd-disaggregation --prefill-policy "$policy" "$@"
