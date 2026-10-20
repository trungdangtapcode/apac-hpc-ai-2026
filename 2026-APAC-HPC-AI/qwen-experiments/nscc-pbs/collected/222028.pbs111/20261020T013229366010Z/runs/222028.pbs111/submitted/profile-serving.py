"""Collect bounded CPU and GPU traces after the performance measurement has finished."""
import concurrent.futures
import json
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
import sys

host, art_arg = sys.argv[1:]
art = Path(art_arg)
out = art / 'diagnostic-profile'
out.mkdir(exist_ok=True)
rows = []
lock = threading.Lock()
stop = threading.Event()
deadline = time.monotonic() + 35

def post(url, body, timeout=90):
    request = urllib.request.Request(url, json.dumps(body).encode(),
                                     {'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)

# This is a diagnostic prompt, not the official benchmark dataset or seed.
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(json.loads((art/'config.json').read_text())['model'],
                                         local_files_only=True)
paragraph = ('Explain how a distributed inference service transfers context between '
             'servers, balances requests and keeps latency predictable. ')
tokens = tokenizer.encode(paragraph * 350, add_special_tokens=False)
assert len(tokens) >= 3970
prompt = tokenizer.decode(tokens[:3970])

def traffic(worker):
    sequence = 0
    while not stop.is_set() and time.monotonic() < deadline:
        begin = time.monotonic()
        record = {'worker': worker, 'sequence': sequence}
        try:
            body = {'model': 'qwen', 'messages': [{'role': 'user', 'content':
                    f'Diagnostic request {worker}/{sequence}. {prompt}'}],
                    'min_tokens': 200, 'max_tokens': 200, 'ignore_eos': True,
                    'temperature': 0.0, 'stream': False}
            result = post(f'http://{host}:8000/v1/chat/completions', body)
            record.update(ok=True, response=result)
        except Exception as error:
            record.update(ok=False, error=str(error))
        record['elapsed_s'] = time.monotonic() - begin
        with lock:
            rows.append(record)
        sequence += 1

control = []
try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=48) as pool:
        futures = [pool.submit(traffic, i) for i in range(48)]
        # Allow diagnostic traffic to reach sustained decode before tracing.
        time.sleep(7)
        endpoints = [line.split('\t') for line in (art/'endpoints.tsv').read_text().splitlines()]
        for name, url, bootstrap in endpoints:
            directory = out/name
            directory.mkdir(exist_ok=True)
            request = {'output_dir': str(directory), 'num_steps': 32 if name.startswith('decode') else 4,
                       'activities': ['CPU', 'GPU'], 'with_stack': False, 'record_shapes': False,
                       'profile_id': name, 'profile_prefix': 'qwen-tuning-'}
            try:
                response = post(url+'/start_profile', request, timeout=60)
                control.append({'worker': name, 'request': request, 'response': response})
            except Exception as error:
                control.append({'worker': name, 'error': str(error)})
        for future in futures:
            future.result()
        for name, url, bootstrap in endpoints:
            try:
                control.append({'worker': name, 'stop': post(url+'/stop_profile', {}, timeout=60)})
            except Exception as error:
                # A step-bounded profile may already have stopped automatically.
                control.append({'worker': name, 'stop_error': str(error)})
finally:
    stop.set()
    (out/'requests.json').write_text(json.dumps(rows, indent=2)+'\n')
    (out/'profile-control.json').write_text(json.dumps(control, indent=2)+'\n')
    (out/'protocol.json').write_text(json.dumps({
        'kind': 'diagnostic-only', 'activities': ['CPU', 'GPU'], 'concurrency': 48, 'duration_s': 35,
        'input_tokens_before_template_approx': 3980, 'output_tokens': 200,
        'position': 'After all official-duration benchmarks; not scored or ranked',
        'trace_steps': {'prefill': 4, 'decode': 32},
        'output_quality_check': 'Not MMLU-Pro/GPQA or organiser accuracy validation'}, indent=2)+'\n')
print(json.dumps({'diagnostic_requests': len(rows), 'control': control}), flush=True)
