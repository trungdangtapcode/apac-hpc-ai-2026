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
  python3 "$QWEN_BUNDLE/phase-marker.py" "$ART" benchmark_start "$PHASE" "$N"
  timeout --signal=TERM --kill-after=15s 360s aiperf profile \
    --url "http://${HOST}" --endpoint-type chat --endpoint /v1/chat/completions \
    --model qwen --tokenizer "$TOKENIZER" --streaming \
    -H 'Accept: text/event-stream' \
    --concurrency "$N" --workers-max "$N" --api-key NOT_USED \
    --warmup-duration "$WARM" --benchmark-duration "$DURATION" --benchmark-grace-period "${QWEN_GRACE:-30}" \
    --synthetic-input-tokens-mean 4000 --synthetic-input-tokens-stddev 0 \
    --output-tokens-mean 200 --output-tokens-stddev 0 \
    --extra-inputs min_tokens:200 --extra-inputs max_tokens:200 \
    --extra-inputs ignore_eos:true --extra-inputs temperature:0.0 \
    --extra-inputs repetition_penalty:1.0 \
    --num-dataset-entries 12800 --random-seed 2026 \
    --cache-bust first_turn_prefix \
    --goodput 'time_to_first_token:3000 inter_token_latency:20' \
    --ui simple --artifact-dir "$RUN/artifacts" >"$RUN/client.log" 2>&1 || {
      client_status=$?
      printf 'AIPERF_CLIENT_FAILED exit=%s walltime_limit_s=360\n' "$client_status" >&2
      if [[ $client_status == 124 || $client_status == 137 ]]; then
        touch "$RUN/client-walltime-limit-exceeded.txt"
      fi
      return "$client_status"
    }
  python3 "$ART/summarize.py" "$ART" >"$ART/summary.json"
  python3 "$QWEN_BUNDLE/phase-marker.py" "$ART" benchmark_end "$PHASE" "$N"
  echo "DONE $PHASE N=$N at $(date -Iseconds)"
}

for N in ${QWEN_TUNE_NS:-48}; do
  if (( $(date +%s)+240 > ${QWEN_BENCHMARK_DEADLINE:-0} )); then
    echo "FULL_POINT_DEFERRED: insufficient time before N=$N"
    printf '%s\n' "$N" >>"$ART/deferred-ns.txt"
    continue
  fi
  run_benchmark "$N" screen 20 40
  if ! python3 - "$ART/summary.json" "$N" <<'GATE'
import json,sys
rows=[r for r in json.load(open(sys.argv[1])) if r['phase']=='screen' and r['concurrency']==int(sys.argv[2])]
assert len(rows)==1
r=rows[0]
sys.exit(0 if r['sla_pass'] and r['cancelled_requests']==0 and r['errors']==0 and r['requests']>0 else 1)
GATE
  then
    echo "STOP_LOAD_INCREASE: N=$N did not pass the latency/error gate"
    printf '%s\n' "$N" >"$ART/stop-increase-n.txt"
    break
  fi
done
if [[ ${QWEN_DIAGNOSTIC_PROFILE:-0} == 1 ]]; then
  if (( $(date +%s)+210 < ${QWEN_BENCHMARK_DEADLINE:-0} )); then
    timeout 180 python3 "$QWEN_BUNDLE/profile-serving.py" "${HOST%:8000}" "$ART" >"$ART/diagnostic-profile.log" 2>&1 || {
      echo "DIAGNOSTIC_PROFILE_FAILED: inspect separate log; measured exports remain preserved"
      touch "$ART/diagnostic-profile-failed.txt"
    }
  else
    touch "$ART/diagnostic-profile-deferred.txt"
  fi
fi

if (( $(date +%s)+100 < ${QWEN_BENCHMARK_DEADLINE:-0} )); then
  timeout 90 python3 "$QWEN_BUNDLE/output-smoke.py" "$HOST" "$ART" >"$ART/output-smoke.log" 2>&1 || touch "$ART/output-smoke-failed.txt"
else
  touch "$ART/output-smoke-deferred.txt"
fi

# Separate post-measurement diagnostic; not included in ranked AIPerf exports.
if (( $(date +%s)+110 < ${QWEN_BENCHMARK_DEADLINE:-0} )); then
  timeout 100 python3 "$QWEN_BUNDLE/long-context-check.py" "$HOST" "$ART" >"$ART/long-context-check.log" 2>&1 || touch "$ART/long-context-check-failed.txt"
else
  touch "$ART/long-context-check-deferred.txt"
fi
