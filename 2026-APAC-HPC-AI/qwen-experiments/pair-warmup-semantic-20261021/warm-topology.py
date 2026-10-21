#!/usr/bin/env python3
"""Prospective semantic P/D warmup; emits success only after all receipts validate."""
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

from warmup_semantic import check, inventory, write_receipt

host, art = sys.argv[1], Path(sys.argv[2])
run_token = os.environ["QWEN_PAIR_RUN_TOKEN"]
endpoints = art / "endpoints.tsv"
receipt_dir = art / "pair-warmup-receipts"
_, pairs, rows = inventory(endpoints)
processes, logs = [], []


def warm(item):
    i, pair = item
    p, d = rows[pair["prefill"]], rows[pair["decode"]]
    url = f"http://{host}:{8110+i}"
    deadline = time.monotonic() + 120
    while True:
        if processes[i].poll() is not None:
            raise RuntimeError(f"Pair router {i} exited before health")
        try:
            with urllib.request.urlopen(url + "/health", timeout=2) as response:
                if response.status == 200: break
        except Exception:
            if time.monotonic() >= deadline: raise RuntimeError(f"Pair router {i} not ready")
            time.sleep(1)
    pi, di = p["name"].split("-", 1)[1], d["name"].split("-", 1)[1]
    body = {"model": "qwen", "messages": [{"role": "user", "content":
            f"KV connection setup for pair P{pi} D{di}. Please say hello."}],
            "max_tokens": 8, "temperature": 0}
    request = urllib.request.Request(url + "/v1/chat/completions", json.dumps(body).encode(),
                                     {"Content-Type": "application/json"})
    deadline = time.monotonic() + 120
    while True:
        try:
            with urllib.request.urlopen(request, timeout=int(os.environ.get("QWEN_PAIR_TIMEOUT", "360"))) as response:
                status = response.status
                data = json.loads(response.read())
            receipt = write_receipt(receipt_dir, endpoints, run_token, pair, status, data)
            print(f'{pair["prefill"]}/{pair["decode"]} semantic PASS completion_tokens={receipt["completion_tokens"]}', flush=True)
            return
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")
            unregistered = any(s in detail.lower() for s in
                ("no prefill workers", "no decode workers", "no healthy workers"))
            if error.code != 503 or not unregistered or time.monotonic() >= deadline:
                raise RuntimeError(f"Pair {i} HTTP {error.code}: {detail[:500]}") from error
            print(f"Pair {i} waiting for worker registration", flush=True)
            time.sleep(2)

try:
    receipt_dir.mkdir(exist_ok=False)
    (art / "pair-warmup").mkdir(exist_ok=True)
    for i, pair in enumerate(pairs):
        p, d = rows[pair["prefill"]], rows[pair["decode"]]
        log = (art / "pair-warmup" / f'router-{p["name"]}-{d["name"]}.log').open("w")
        logs.append(log)
        processes.append(subprocess.Popen([
            sys.executable, "-m", "sglang_router.launch_router", "--pd-disaggregation",
            "--prefill", p["url"], p["bootstrap"], "--decode", d["url"],
            "--host", "0.0.0.0", "--port", str(8110+i), "--prometheus-port", str(29110+i)],
            stdout=log, stderr=subprocess.STDOUT))
    with ThreadPoolExecutor(max_workers=int(os.environ.get("QWEN_PAIR_PARALLELISM", "8"))) as pool:
        list(pool.map(warm, enumerate(pairs)))
    checked = check(receipt_dir, endpoints, run_token)
    print(f'ALL {checked["pair_count"]} P/D paths semantically initialized', flush=True)
finally:
    for process in processes:
        if process.poll() is None: process.terminate()
    for process in processes:
        try: process.wait(timeout=10)
        except subprocess.TimeoutExpired: process.kill(); process.wait()
    for log in logs: log.close()
