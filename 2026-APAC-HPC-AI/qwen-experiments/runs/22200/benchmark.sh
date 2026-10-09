#!/usr/bin/env bash
set -euo pipefail
HOST=$1
TOKENIZER=Qwen/Qwen3-235B-A22B-Instruct-2507
ART=$3
mkdir -p "$ART"
export HF_HUB_CACHE="$(dirname "$(dirname "$ART")")/hf-cache"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
python3 - <<'PYMETA' >"$ART/client-versions.txt"
from importlib.metadata import version
for p in ('aiperf','transformers','tokenizers'):
    try: print(p, version(p))
    except Exception as e: print(p, str(e))
PYMETA
python3 - <<'PYCHECK' >"$ART/tokenizer-preflight.log" 2>&1
from aiperf.common.tokenizer import Tokenizer
t = Tokenizer.from_pretrained('Qwen/Qwen3-235B-A22B-Instruct-2507')
print('AIPerf tokenizer OK:',len(t.encode('Hello world')),flush=True)
PYCHECK
# Few non-benchmark warm-up requests through gateway; no benchmark data/seed.
python3 - "$HOST" <<'PYWARM' >"$ART/connection-warmup.log" 2>&1
import json,sys,urllib.request,time
from concurrent.futures import ThreadPoolExecutor
url='http://'+sys.argv[1]+'/v1/chat/completions'
def call(i):
    body={'model':'qwen','messages':[{'role':'user','content':f'Connection warm-up {i}. Please say hello.'}], 'max_tokens':8,'temperature':0}
    t=time.monotonic()
    req=urllib.request.Request(url,json.dumps(body).encode(),{'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=120) as r: print(i,r.status,round(time.monotonic()-t,2),r.read()[:160],flush=True)
    except Exception as e: print(i,type(e).__name__,str(e),flush=True)
with ThreadPoolExecutor(max_workers=4) as ex:
    list(ex.map(call,range(8)))
PYWARM
run_benchmark() {
  N=$1
  PHASE=$2
  WARM=$3
  DURATION=$4
  RUN="$ART/${PHASE}/n${N}"
  mkdir -p "$RUN"
  cd "$RUN"
  echo "START $PHASE N=$N at $(date -Iseconds)"
  aiperf profile \
    --url "http://${HOST}" --endpoint-type chat --endpoint /v1/chat/completions \
    --model qwen --tokenizer "$TOKENIZER" --streaming \
    -H 'Accept: text/event-stream' \
    --concurrency "$N" --workers-max "$N" --api-key NOT_USED \
    --warmup-duration "$WARM" --benchmark-duration "$DURATION" --benchmark-grace-period 30 \
    --synthetic-input-tokens-mean 4000 --synthetic-input-tokens-stddev 0 \
    --output-tokens-mean 200 --output-tokens-stddev 0 \
    --extra-inputs min_tokens:200 --extra-inputs max_tokens:200 \
    --extra-inputs ignore_eos:true --extra-inputs temperature:0.0 \
    --extra-inputs repetition_penalty:1.0 \
    --num-dataset-entries 12800 --random-seed 2026 \
    --cache-bust first_turn_prefix \
    --goodput 'time_to_first_token:3000 inter_token_latency:20' \
    --ui simple --artifact-dir "$RUN/artifacts" >"$RUN/client.log" 2>&1
  python3 "$ART/summarize.py" "$ART" >"$ART/summary.json"
  echo "DONE $PHASE N=$N at $(date -Iseconds)"
}
if [[ ${QWEN_CONFIRM_ONLY:-0} == 1 ]]; then
  run_benchmark "${QWEN_CONFIRM_N:-32}" confirm 60 120
  exit 0
fi
for N in ${QWEN_SWEEP_NS:-16 32 64}; do
  run_benchmark "$N" sweep 15 30
done
BEST=$(python3 - "$ART/summary.json" <<'PYBEST'
import json,sys
rows=[r for r in json.load(open(sys.argv[1])) if r['sla_pass'] and r['good_output_tokens_s'] is not None]
if rows:print(max(rows,key=lambda r:r['good_output_tokens_s'])['concurrency'])
PYBEST
)
if [[ -n "$BEST" ]]; then
  run_benchmark "$BEST" confirm 60 120
else
  echo "No passing SLA point in sweep; no full-length confirmation."
fi
