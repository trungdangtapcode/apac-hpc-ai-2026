#!/usr/bin/env python3
"""Run serial then concurrent semantic P/D warmups with isolated receipts."""
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
base_id = os.environ["QWEN_EXPERIMENT_ID"]
_, pairs, rows = inventory(endpoints)
expected = {r["name"] for r in rows.values()}
if expected != {"prefill-0", "prefill-1", "decode-0"} or len(pairs) != 2:
    raise ValueError(f"unexpected target-only worker inventory: {sorted(expected)}")
phase_root = art / "pair-warmup"
phase_root.mkdir(exist_ok=True)


def run_phase(phase, concurrent):
    experiment_id = f"{base_id}-{phase}"
    run_token = hashlib.sha256(experiment_id.encode()).hexdigest()[:32]
    phase_dir = phase_root / phase
    phase_dir.mkdir(exist_ok=False)
    receipt_dir = art / "pair-warmup-receipts" / phase
    receipt_dir.mkdir(parents=True, exist_ok=False)
    inv_hash, _, _ = inventory(endpoints)
    (phase_dir / "context.json").write_text(json.dumps({
        "phase": phase, "experiment_id": experiment_id,
        "run_token_derivation": "sha256(experiment_id)[:32]",
        "endpoint_inventory_sha256": inv_hash,
        "authentication_material": "none"
    }, indent=2) + "\n")
    deadline = min(time.time() + 90, float(os.environ[f"QWEN_{phase.upper()}_DEADLINE_EPOCH"]))
    processes, logs = [], []
    for i, pair in enumerate(pairs):
        p, d = rows[pair["prefill"]], rows[pair["decode"]]
        log = (phase_dir / f'router-{p["name"]}-{d["name"]}.log').open("x")
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
                raise RuntimeError(f"{phase} router {i} exited before readiness")
            try:
                with urllib.request.urlopen(url + "/health", timeout=2) as response:
                    if response.status == 200:
                        break
            except Exception:
                time.sleep(1)
        else:
            raise TimeoutError(f"{phase} router {i} did not become ready")
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
                        raise ValueError("warmup response exceeded 1 MiB")
                    receipt = write_receipt(receipt_dir, endpoints, run_token, pair,
                                            response.status, json.loads(raw))
                    print(f'{phase} {pair["prefill"]}/{pair["decode"]} PASS completion_tokens={receipt["completion_tokens"]}', flush=True)
                    return
            except urllib.error.HTTPError as error:
                body = error.read(64 * 1024).decode(errors="replace")
                with (phase_dir / "failed-responses.jsonl").open("a") as stream:
                    stream.write(json.dumps({"phase": phase, "pair_id": pair["pair_id"],
                                             "http_status": error.code, "body_prefix": body}, sort_keys=True) + "\n")
                retryable = error.code == 503 and any(text in body.lower() for text in
                    ("no prefill workers", "no decode workers", "no healthy workers"))
                if not retryable:
                    raise RuntimeError(f"{phase} pair {i} unexpected HTTP {error.code}: {body[:500]}") from error
                time.sleep(min(2, max(0, deadline-time.time())))
        raise TimeoutError(f"{phase} pair {i} exceeded its absolute deadline")

    try:
        errors = []
        if concurrent:
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(warm, item) for item in enumerate(pairs)]
                for future in futures:
                    try:
                        future.result()
                    except Exception as error:
                        errors.append(f"{type(error).__name__}: {error}")
        else:
            for item in enumerate(pairs):
                try:
                    warm(item)
                except Exception as error:
                    errors.append(f"{type(error).__name__}: {error}")
        if errors:
            raise RuntimeError(f"{phase} phase had {len(errors)} failed route(s): " + " | ".join(errors))
        checked = check(receipt_dir, endpoints, run_token)
        if checked.get("pair_count") != 2 or checked.get("inventory_sha256") != inv_hash:
            raise ValueError(f"{phase} receipts failed independent replay")
        (phase_dir / "receipt-check.json").write_text(json.dumps(checked, indent=2, sort_keys=True) + "\n")
        print(f'{phase.upper()}_BOTH_PD_PATHS_PASS run_token_sha256={hashlib.sha256(run_token.encode()).hexdigest()}', flush=True)
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
        for log in logs:
            log.close()

phase = sys.argv[3]
if phase not in {"serial", "concurrent"}:
    raise ValueError("phase must be serial or concurrent")
run_phase(phase, concurrent=(phase == "concurrent"))
