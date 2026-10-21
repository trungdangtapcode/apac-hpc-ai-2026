"""Exercise the actual pinned PD gateway with explicitly synthetic workers.

No model, KV transfer or inference occurs. This checks /generate forwarding
and response preservation before a costly full-target correctness pilot.
"""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import socket
import subprocess
import threading
import time
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    received = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *unused):
            pass

        def reply(self, body):
            raw = json.dumps(body).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            self.reply(dict(model_path='qwen', served_model_name='qwen',
                            is_generation=True, model_type='qwen3_moe',
                            max_total_num_tokens=8192))

        def do_POST(self):
            size = int(self.headers.get('Content-Length', '0'))
            assert 0 < size < 65536
            body = json.loads(self.rfile.read(size))
            received.append(dict(role=self.server.role, path=self.path, body=body))
            assert self.path == '/generate'
            meta = dict(finish_reason=dict(type='stop'), completion_tokens=2, prompt_tokens=2)
            if body.get('return_logprob') is True:
                if self.server.role == 'prefill':
                    meta.update(input_token_logprobs=[[-.1, 1, None]], output_token_logprobs=[])
                else:
                    meta.update(input_token_logprobs=[[-.2, 2, None]],
                                output_token_logprobs=[[-.3, 3, None], [-.4, 4, None]])
            self.reply(dict(text='SYNTHETIC_ECHO', meta_info=meta))

    servers = []
    for role in ['prefill', 'decode']:
        server = HTTPServer(('127.0.0.1', 0), Handler)
        server.role = role
        threading.Thread(target=server.serve_forever, daemon=True).start()
        servers.append(server)
    with socket.socket() as reserve:
        reserve.bind(('127.0.0.1', 0))
        gateway_port = reserve.getsockname()[1]
    command = ['python3', '-m', 'sglang_router.launch_router', '--pd-disaggregation',
               '--prefill-policy', 'round_robin',
               '--prefill', f'http://127.0.0.1:{servers[0].server_port}', '19999',
               '--decode', f'http://127.0.0.1:{servers[1].server_port}',
               '--host', '127.0.0.1', '--port', str(gateway_port),
               '--disable-health-check', '--disable-circuit-breaker',
               '--worker-startup-timeout-secs', '30']
    result = dict(scope='Actual native gateway, synthetic workers only; no model or KV transfer',
                  command=command, passed=False, received=received)
    process = None
    try:
        with (args.out / 'native-router.log').open('wb') as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                       env={**os.environ, 'TOKIO_WORKER_THREADS': '1',
                                            'RAYON_NUM_THREADS': '1'})
            deadline = time.monotonic() + 55
            while True:
                if process.poll() is not None:
                    raise RuntimeError(f'Native gateway exited {process.returncode}')
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{gateway_port}/health', timeout=1):
                        break
                except Exception:
                    if time.monotonic() >= deadline:
                        raise RuntimeError('Native gateway readiness deadline')
                    time.sleep(.5)
            body = dict(input_ids=[1, 2], sampling_params=dict(temperature=0.0, max_new_tokens=2),
                        stream=False, return_logprob=True, logprob_start_len=0)
            request = urllib.request.Request(f'http://127.0.0.1:{gateway_port}/generate',
                                             json.dumps(body).encode(),
                                             {'Content-Type': 'application/json'})
            with urllib.request.urlopen(request, timeout=15) as response:
                result['response'] = json.load(response)
            result['request_fields_forwarded'] = all(
                any(row['role'] == role and row['path'] == '/generate'
                    and row['body'].get('return_logprob') is True
                    and row['body'].get('input_ids') == [1, 2] for row in received)
                for role in ['prefill', 'decode'])
            meta = result['response'].get('meta_info', {})
            input_ids = [entry[1] for entry in meta.get('input_token_logprobs', [])]
            output_ids = [entry[1] for entry in meta.get('output_token_logprobs', [])]
            result['merged_input_ids'] = input_ids
            result['output_ids'] = output_ids
            result['response_ids_preserved'] = input_ids == [1, 2] and output_ids == [3, 4]
            result['passed'] = result['request_fields_forwarded'] and result['response_ids_preserved']
    except Exception as error:
        result['failure'] = dict(type=type(error).__name__, message=str(error))
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        for server in servers:
            server.shutdown()
            server.server_close()
        (args.out / 'gateway-echo.json').write_text(json.dumps(result, indent=2) + '\n')
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
