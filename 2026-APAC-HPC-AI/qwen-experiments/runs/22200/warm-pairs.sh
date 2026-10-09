#!/usr/bin/env bash
# Run in the SGLang container after all workers are healthy.
# Temporary gateways each expose exactly one P/D pair, so all 8 paths are covered.
set -euo pipefail
P_HOST=$1
D_HOST=$2
ART=$3
pids=()
cleanup() {
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || :; done
  wait || :
}
trap cleanup EXIT
mkdir -p "$ART/pair-warmup"
for ((p=0;p<${QWEN_PREFILL_WORKERS:-4};p++)); do
  for d in 0 1; do
    port=$((8110+p*2+d))
    python3 -m sglang_router.launch_router --pd-disaggregation \
      --prefill "http://${P_HOST}:$((30100+p))" "$((9000+p))" \
      --decode "http://${D_HOST}:$((30200+d))" \
      --host 0.0.0.0 --port "$port" --prometheus-port "$((29110+p*2+d))" \
      >"$ART/pair-warmup/router-p${p}-d${d}.log" 2>&1 &
    pids+=("$!")
  done
done
python3 - "$P_HOST" <<'PY'
import json, os, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
host=sys.argv[1]
prefill_workers=int(os.environ.get('QWEN_PREFILL_WORKERS','4'))
def warm(pair):
    p,d=pair
    url=f'http://{host}:{8110+p*2+d}'
    deadline=time.monotonic()+120
    while True:
        try:
            with urllib.request.urlopen(url+'/health',timeout=2) as r:
                if r.status==200:break
        except Exception:
            if time.monotonic()>deadline:raise RuntimeError(f'Gateway P{p}/D{d} not ready')
            time.sleep(1)
    body={'model':'qwen','messages':[{'role':'user','content':f'KV connection setup for pair P{p} D{d}. Please say hello.'}], 'max_tokens':8,'temperature':0}
    req=urllib.request.Request(url+'/v1/chat/completions',json.dumps(body).encode(),{'Content-Type':'application/json'})
    start=time.monotonic()
    # /health can succeed while router workers are still registered asynchronously.
    # Retry only the explicit "no workers" 503: this request was never forwarded.
    deadline=start+120
    while True:
        try:
            with urllib.request.urlopen(req,timeout=180) as r:
                data=json.loads(r.read())
                assert r.status==200 and data.get('choices'),data
                print(f'P{p}/D{d} OK in {time.monotonic()-start:.2f}s',flush=True)
                return
        except urllib.error.HTTPError as error:
            detail=error.read().decode(errors='replace')
            not_registered=any(s in detail.lower() for s in ('no prefill workers','no decode workers','no healthy workers'))
            if error.code!=503 or not not_registered or time.monotonic()>=deadline:
                raise RuntimeError(f'P{p}/D{d} HTTP {error.code}: {detail[:500]}') from error
            print(f'P{p}/D{d} waiting for router worker registration',flush=True)
            time.sleep(2)
with ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(warm,[(p,d) for p in range(prefill_workers) for d in range(2)]))
PY
