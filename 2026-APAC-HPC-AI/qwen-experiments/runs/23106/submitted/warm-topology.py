"""Initialize every P/D KV path through temporary single-pair gateways."""
import itertools
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

host, art = sys.argv[1], Path(sys.argv[2])
workers = [line.split() for line in (art/'endpoints.tsv').read_text().splitlines()]
p_workers = [r for r in workers if r[0].startswith('prefill-')]
d_workers = [r for r in workers if r[0].startswith('decode-')]
logdir = art/'pair-warmup'
logdir.mkdir(exist_ok=True)
processes, logs, pairs = [], [], []

def warm(pair):
    i, p, d = pair
    url = f'http://{host}:{8110+i}'
    deadline = time.monotonic()+120
    while True:
        if processes[i].poll() is not None:
            raise RuntimeError(f'Pair router {i} exited')
        try:
            with urllib.request.urlopen(url+'/health', timeout=2) as r:
                if r.status == 200: break
        except Exception:
            if time.monotonic()>=deadline: raise RuntimeError(f'Pair router {i} not ready')
            time.sleep(1)
    body = {'model':'qwen','messages':[{'role':'user','content':
            f"KV connection setup for pair P{p[0].split('-')[1]} D{d[0].split('-')[1]}. Please say hello."}],
            'max_tokens':8,'temperature':0}
    request = urllib.request.Request(url+'/v1/chat/completions', json.dumps(body).encode(),
                                    {'Content-Type':'application/json'})
    start = time.monotonic()
    deadline = start+120
    while True:
        try:
            with urllib.request.urlopen(request, timeout=int(os.environ.get('QWEN_PAIR_TIMEOUT','360'))) as r:
                data = json.loads(r.read())
                if r.status!=200 or not data.get('choices'): raise RuntimeError(data)
                print(f'{p[0]}/{d[0]} OK {time.monotonic()-start:.2f}s', flush=True)
                return
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors='replace')
            unregistered = any(s in detail.lower() for s in
                ('no prefill workers','no decode workers','no healthy workers'))
            if error.code!=503 or not unregistered or time.monotonic()>=deadline:
                raise RuntimeError(f'Pair {i} HTTP {error.code}: {detail[:500]}') from error
            print(f'Pair {i} waiting for worker registration', flush=True)
            time.sleep(2)

try:
    for i, (p, d) in enumerate(itertools.product(p_workers, d_workers)):
        log = (logdir/f'router-{p[0]}-{d[0]}.log').open('w')
        logs.append(log)
        processes.append(subprocess.Popen([
            sys.executable,'-m','sglang_router.launch_router','--pd-disaggregation',
            '--prefill',p[1],p[2],'--decode',d[1],
            '--host','0.0.0.0','--port',str(8110+i),'--prometheus-port',str(29110+i)],
            stdout=log, stderr=subprocess.STDOUT))
        pairs.append((i,p,d))
    with ThreadPoolExecutor(max_workers=int(os.environ.get('QWEN_PAIR_PARALLELISM','8'))) as pool:
        list(pool.map(warm, pairs))
    print(f'ALL {len(pairs)} P/D paths initialized', flush=True)
finally:
    for process in processes:
        if process.poll() is None: process.terminate()
    for process in processes:
        try: process.wait(timeout=10)
        except subprocess.TimeoutExpired: process.kill(); process.wait()
    for log in logs: log.close()
