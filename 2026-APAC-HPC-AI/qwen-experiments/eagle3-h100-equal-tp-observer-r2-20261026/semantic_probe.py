#!/usr/bin/env python3
"""Send exactly one end-to-end P/D semantic request and replay its receipt."""
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

from warmup_semantic import check, inventory, write_receipt

art = Path(os.environ["QWEN_ARTDIR"])
endpoints = art / "endpoints.tsv"
experiment_id = os.environ["QWEN_EXPERIMENT_ID"]
token = hashlib.sha256(f"{experiment_id}-single-semantic".encode()).hexdigest()[:32]
inv_hash, pairs, roles = inventory(endpoints)
if len(roles) != 2 or len(pairs) != 1:
    raise SystemExit("FATAL: semantic probe requires exactly one P/D route")
pair = pairs[0]
root = art / "pair-warmup/single"
receipts = art / "pair-warmup-receipts/single"
root.mkdir(parents=True, exist_ok=False)
receipts.mkdir(parents=True, exist_ok=False)
(root / "context.json").write_text(json.dumps({
    "phase": "single-semantic", "experiment_id": experiment_id,
    "run_token_derivation": "sha256(experiment_id + '-single-semantic')[:32]",
    "endpoint_inventory_sha256": inv_hash, "authentication_material": "none",
    "pair": pair,
}, sort_keys=True, indent=2) + "\n")
deadline = int(os.environ["QWEN_SEMANTIC_DEADLINE_EPOCH"])
url = "http://127.0.0.1:8000/v1/chat/completions"
body = {"model": "qwen", "messages": [{"role": "user", "content":
        "Verify one local P-to-D EAGLE3 semantic transfer. Reply with a short greeting."}],
        "max_tokens": 8, "temperature": 0}
request = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
while time.time() < deadline:
    try:
        with urllib.request.urlopen(request, timeout=max(1, min(120, deadline - int(time.time())))) as response:
            raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise ValueError("semantic response exceeded 1 MiB")
            data = json.loads(raw)
            receipt = write_receipt(receipts, endpoints, token, pair, response.status, data)
            replay = check(receipts, endpoints, token)
            (root / "receipt-check.json").write_text(json.dumps(replay, sort_keys=True, indent=2) + "\n")
            (root / "semantic-pass.json").write_text(json.dumps({
                "status": "PASS", "receipt": receipt, "receipt_replay": replay,
                "scope": "one semantic response only; no output-ID comparison or quality score",
            }, sort_keys=True, indent=2) + "\n")
            print("ONE_SEMANTIC_PD_REQUEST_PASS", json.dumps(replay, sort_keys=True), flush=True)
            break
    except urllib.error.HTTPError as exc:
        text = exc.read(64 * 1024).decode(errors="replace")
        (root / "failed-response.json").write_text(json.dumps({"http_status": exc.code,
            "body_prefix": text, "phase": "single-semantic"}, sort_keys=True, indent=2) + "\n")
        retryable = exc.code == 503 and any(x in text.lower() for x in
                    ("no prefill workers", "no decode workers", "no healthy workers"))
        if not retryable:
            raise SystemExit(f"FATAL: semantic request returned HTTP {exc.code}: {text[:500]}") from exc
        time.sleep(min(2, max(0, deadline - time.time())))
else:
    raise SystemExit("FATAL: single semantic request exceeded its absolute deadline")
