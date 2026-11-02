#!/usr/bin/env python3
"""Exercise readiness failure modes on local HTTP fixtures; never launch serving."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import tempfile
import threading
import time

D = Path(__file__).resolve().parent
OLD = D.parent / 'final-portable-acceptance-20261102/delivery/VNUHCM - TripleU/AI_Task/job_scripts'
B = D / 'delivery/VNUHCM - TripleU/AI_Task/job_scripts'
valid = json.dumps({'object': 'list', 'data': [{'id': 'qwen'}]}).encode()
wrong = json.dumps({'data': [{'id': 'another-model'}]}).encode()


def exercise(case):
    name, responses, age, live, expected = case
    with tempfile.TemporaryDirectory(prefix='gateway-fixture-') as temp:
        output = Path(temp) / 'models.json'
        observed = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                status, body = responses[min(len(observed), len(responses)-1)]
                observed.append({'path': self.path, 'status': status, 'output_exists_before_success': output.exists()})
                self.send_response(status)
                self.end_headers()
                self.wfile.write(body)
            def log_message(self, *unused):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            source = str(D / 'gateway_function.sh')
            epoch = int(time.time()) - age
            script = f'set -euo pipefail\nsource "$1"\nJOB_START_EPOCH={epoch}\npids=($$)\n'
            if not live:
                script += 'pids=(999999999)\n'
            script += 'wait_gateway_models "$2" "$3"\n'
            result = subprocess.run(['bash', '-c', script, 'fixture', source,
                                     f'http://127.0.0.1:{server.server_port}/v1/models', str(output)],
                                    text=True, capture_output=True, timeout=20)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
        assert (result.returncode == 0) == expected, (name, result.stdout, result.stderr)
        assert not any(row['output_exists_before_success'] for row in observed), name
        if expected:
            assert json.loads(output.read_text())['data'][0]['id'] == 'qwen'
            assert len(observed) == len(responses)
        else:
            assert not output.exists()
        if age >= 600 or not live:
            assert not observed, (name, observed)
        return {'name': name, 'passed': True, 'returncode': result.returncode, 'requests': len(observed),
                'stdout': result.stdout, 'stderr': result.stderr}


cases = [
    ('503-empty-malformed-wrong-model-then-ready', [(503,b'not ready'),(200,b''),(200,b'bad json'),(200,wrong),(200,valid)], 0, True, True),
    ('persistent-503-times-out', [(503,b'not ready')], 598, True, False),
    ('wrong-model-times-out', [(200,wrong)], 598, True, False),
    ('expired-job-start-deadline-fails-without-network', [(200,valid)], 601, True, False),
    ('dead-worker-fails-without-network', [(200,valid)], 0, False, False),
]
with ThreadPoolExecutor(max_workers=5) as pool:
    results = list(pool.map(exercise, cases))
changed = []
for original in OLD.rglob('*'):
    if not original.is_file():
        continue
    relative = original.relative_to(OLD)
    if original.read_bytes() != (B / relative).read_bytes():
        changed.append(str(relative))
assert sorted(changed) == ['SHA256SUMS', 'deploy-and-benchmark.sh'], changed
for name in ['submit.sbatch','official-benchmark.sh','worker.sh','warm-topology.py','warmup_semantic.py','score-gate.py','summarize.py','artifact_paths.py','config.json','environment.json','nixl-conn.py']:
    assert (B / name).read_bytes() == (OLD / name).read_bytes(), name
syntax = subprocess.run(['bash','-n',str(B/'deploy-and-benchmark.sh')],capture_output=True,text=True)
assert syntax.returncode == 0, syntax.stderr
setup = subprocess.run(['bash','setup.sh','--check'],cwd=B,capture_output=True,text=True,timeout=90)
(D/'setup-check.log').write_text(setup.stdout + setup.stderr)
assert setup.returncode == 0
result = {'passed': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'cases':results,
          'only_changed_payload_files':changed, 'official_command_and_semantic_output_gates_byte_identical':True,
          'original_job_start_plus_600s_deadline_retained':True,
          'scope':'Local HTTP/readiness fixtures and setup only; not real router activation, GPU serving, throughput or official quality.'}
(D/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'local_cases':len(results),'changed_payload_files':changed}))
