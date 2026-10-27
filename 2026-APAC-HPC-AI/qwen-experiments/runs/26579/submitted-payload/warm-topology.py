#!/usr/bin/env python3
"""Warm all P/D routes, requiring independently replayable semantic receipts."""
import hashlib
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
endpoints = art / "endpoints.tsv"
receipt_dir = art / "pair-warmup-receipts"
experiment_id = os.environ["QWEN_EXPERIMENT_ID"]
run_token = hashlib.sha256(experiment_id.encode()).hexdigest()[:32]
art.mkdir(parents=True, exist_ok=True)
(art / "pair-warmup-context.json").write_text(json.dumps({
    "experiment_id": experiment_id, "run_token_derivation": "sha256(experiment_id)[:32]",
    "authentication_material": "none", "endpoint_inventory_sha256": inventory(endpoints)[0]
}, indent=2) + "\n")
receipt_dir.mkdir(exist_ok=False)
failed_responses = art / "pair-warmup-failed-responses.jsonl"
_, pairs, rows = inventory(endpoints)
expected = {r["name"] for r in rows.values()}
if expected != {"prefill-0", "prefill-1", "decode-0"} or len(pairs) != 2:
    raise ValueError(f"unexpected target-only worker inventory: {sorted(expected)}")
processes, logs = [], []
pair_dir = art / "pair-warmup"
pair_dir.mkdir(exist_ok=False)
deadline = min(time.time() + 120, float(os.environ["QWEN_WARMUP_DEADLINE_EPOCH"]))

try:
    for i, pair in enumerate(pairs):
        p, d = rows[pair["prefill"]], rows[pair["decode"]]
        log = (pair_dir / f'router-{p["name"]}-{d["name"]}.log').open("x")
        logs.append(log)
        processes.append(subprocess.Popen([
            sys.executable, "-m", "sglang_router.launch_router", "--pd-disaggregation",
            "--prefill", p["url"], p["bootstrap"], "--decode", d["url"],
            "--host", "0.0.0.0", "--port", str(8110+i), "--prometheus-port", str(29110+i)],
            stdout=log, stderr=subprocess.STDOUT))

    def warm(item):
        i, pair = item
        p, d = rows[pair["prefill"]], rows[pair["decode"]]
        url = f"http://{host}:{8110+i}"
        while time.time() < deadline:
            if processes[i].poll() is not None:
                raise RuntimeError(f"pair router {i} exited before readiness")
            try:
                with urllib.request.urlopen(url + "/health", timeout=2) as response:
                    if response.status == 200: break
            except Exception:
                time.sleep(1)
        else:
            raise TimeoutError(f"pair router {i} did not become ready before absolute warmup deadline")
        pi, di = p["name"].split("-", 1)[1], d["name"].split("-", 1)[1]
        body = {"model": "qwen", "messages": [{"role": "user", "content":
                f"KV connection setup for pair P{pi} D{di}. Please say hello."}],
                "max_tokens": 8, "temperature": 0}
        request = urllib.request.Request(url + "/v1/chat/completions", json.dumps(body).encode(),
                                         {"Content-Type": "application/json"})
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(request, timeout=max(1, min(30, int(deadline-time.time())))) as response:
                    raw = response.read(1024 * 1024 + 1)
                    if len(raw) > 1024 * 1024:
                        raise ValueError("pair warmup response exceeded 1 MiB")
                    data = json.loads(raw)
                    try:
                        receipt = write_receipt(receipt_dir, endpoints, run_token, pair, response.status, data)
                    except Exception as error:
                        with failed_responses.open("a") as stream:
                            stream.write(json.dumps({"pair_id": pair["pair_id"], "http_status": response.status,
                                "body": data, "semantic_error": str(error)}, sort_keys=True) + "\n")
                        raise
                    print(f'{pair["prefill"]}/{pair["decode"]} semantic PASS completion_tokens={receipt["completion_tokens"]}', flush=True)
                    return
            except urllib.error.HTTPError as error:
                body = error.read(64 * 1024).decode(errors="replace")
                with failed_responses.open("a") as stream:
                    stream.write(json.dumps({"pair_id": pair["pair_id"], "http_status": error.code,
                                             "body_prefix": body}, sort_keys=True) + "\n")
                retryable = error.code == 503 and any(text in body.lower() for text in
                    ("no prefill workers", "no decode workers", "no healthy workers"))
                if not retryable:
                    raise RuntimeError(f"pair {i} unexpected HTTP {error.code}: {body[:500]}") from error
                time.sleep(min(2, max(0, deadline-time.time())))
            except Exception as error:
                raise
        raise TimeoutError(f"pair {i} semantic request exceeded absolute warmup deadline")

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(warm, enumerate(pairs)))
    checked = check(receipt_dir, endpoints, run_token)
    if checked["pair_count"] != 2 or checked["inventory_sha256"] != inventory(endpoints)[0]:
        raise ValueError("semantic receipt count or inventory mismatch")
    print(f'ALL {checked["pair_count"]} P/D paths semantically initialized experiment_id={experiment_id}', flush=True)
finally:
    for process in processes:
        if process.poll() is None: process.terminate()
    for process in processes:
        try: process.wait(timeout=10)
        except subprocess.TimeoutExpired: process.kill(); process.wait()
    for log in logs: log.close()
