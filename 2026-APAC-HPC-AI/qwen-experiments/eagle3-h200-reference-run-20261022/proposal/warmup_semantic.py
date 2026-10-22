#!/usr/bin/env python3
"""Stdlib-only inventory, semantic gate, and atomic receipts for P/D warmup."""
import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

SCHEMA = "pair-warmup-semantic-v1"
TOKEN_RE = re.compile(r"^[0-9a-f]{32}$")


def inventory(path):
    rows = []
    names = set()
    for n, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) != 3 or not all(c.strip() for c in cols):
            raise ValueError(f"endpoints.tsv line {n}: expected three nonempty tab fields")
        name, url, bootstrap = (c.strip() for c in cols)
        role = "prefill" if name.startswith("prefill-") else "decode" if name.startswith("decode-") else None
        if role is None or name in names or not url.startswith("http://"):
            raise ValueError(f"endpoints.tsv line {n}: invalid or duplicate endpoint")
        names.add(name)
        rows.append({"name": name, "role": role, "url": url, "bootstrap": bootstrap})
    rows.sort(key=lambda r: (r["role"], r["name"]))
    ps = [r for r in rows if r["role"] == "prefill"]
    ds = [r for r in rows if r["role"] == "decode"]
    if not ps or not ds:
        raise ValueError("endpoint inventory must contain prefill and decode workers")
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    pairs = []
    for p in ps:
        for d in ds:
            pid = hashlib.sha256(f'{p["name"]}\0{d["name"]}'.encode()).hexdigest()
            pairs.append({"pair_id": pid, "prefill": p["name"], "decode": d["name"]})
    return digest, pairs, {r["name"]: r for r in rows}


def validate_response(status, data):
    if status != 200:
        raise ValueError(f"warmup HTTP status must be 200, got {status}")
    if not isinstance(data, dict):
        raise ValueError("response JSON must be an object")
    choices = data.get("choices")
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
        raise ValueError("response must contain a choice")
    message = choices[0].get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if (not isinstance(message, dict) or message.get("role") != "assistant"
            or not isinstance(content, str) or not content.strip()):
        raise ValueError("assistant content must be nonempty text")
    usage = data.get("usage")
    if not isinstance(usage, dict):
        raise ValueError("usage must be an object")
    pt, ct, total = (usage.get(k) for k in ("prompt_tokens", "completion_tokens", "total_tokens"))
    if any(type(v) is not int for v in (pt, ct, total)) or pt < 0 or not 0 < ct <= 8 or total != pt + ct:
        raise ValueError("usage token counts are invalid or inconsistent")
    return {"assistant_chars": len(content), "assistant_sha256": hashlib.sha256(content.encode()).hexdigest(),
            "prompt_tokens": pt, "completion_tokens": ct, "total_tokens": total}


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(value, f, sort_keys=True, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
        raise


def write_receipt(receipt_dir, endpoints, run_token, pair, status, data):
    if not TOKEN_RE.fullmatch(run_token):
        raise ValueError("run token must be 32 lowercase hex characters")
    inv_hash, pairs, _ = inventory(endpoints)
    if pair not in pairs:
        raise ValueError("pair is not in endpoint inventory")
    metrics = validate_response(status, data)
    response = {"http_status": status, "body": data}
    response_bytes = json.dumps(response, sort_keys=True, separators=(",", ":")).encode()
    receipt = {"schema": SCHEMA, "inventory_sha256": inv_hash, "run_token": run_token,
               **pair, "http_status": status, **metrics,
               "response_sha256": hashlib.sha256(response_bytes).hexdigest()}
    path = Path(receipt_dir) / f'receipt-{pair["pair_id"]}.json'
    if path.exists():
        raise FileExistsError(f"receipt already exists: {path.name}")
    response_path = path.with_name(f'response-{pair["pair_id"]}.json')
    if response_path.exists():
        raise FileExistsError(f"response already exists: {response_path.name}")
    atomic_json(response_path, response)
    atomic_json(path, receipt)
    return receipt


def check(receipt_dir, endpoints, run_token):
    if not TOKEN_RE.fullmatch(run_token):
        raise ValueError("run token must be 32 lowercase hex characters")
    inv_hash, pairs, _ = inventory(endpoints)
    directory = Path(receipt_dir)
    expected = {p["pair_id"]: p for p in pairs}
    actual = {}
    for path in sorted(directory.glob("receipt-*.json")):
        obj = json.loads(path.read_text())
        if not isinstance(obj, dict) or obj.get("schema") != SCHEMA:
            raise ValueError(f"invalid receipt schema: {path.name}")
        pid = obj.get("pair_id")
        if pid not in expected or pid in actual:
            raise ValueError(f"unexpected or duplicate receipt: {path.name}")
        if path.name != f"receipt-{pid}.json" or any(obj.get(k) != v for k, v in expected[pid].items()):
            raise ValueError(f"receipt route mismatch: {path.name}")
        if obj.get("run_token") != run_token or obj.get("inventory_sha256") != inv_hash:
            raise ValueError(f"stale token or inventory mismatch: {path.name}")
        if obj.get("http_status") != 200 or type(obj.get("completion_tokens")) is not int or not 0 < obj["completion_tokens"] <= 8:
            raise ValueError(f"invalid semantic receipt: {path.name}")
        if type(obj.get("assistant_chars")) is not int or obj["assistant_chars"] <= 0 or not re.fullmatch(r"[0-9a-f]{64}", str(obj.get("assistant_sha256", ""))):
            raise ValueError(f"invalid assistant evidence: {path.name}")
        pt, ct, total = (obj.get(k) for k in ("prompt_tokens", "completion_tokens", "total_tokens"))
        if type(pt) is not int or type(ct) is not int or type(total) is not int or pt < 0 or total != pt + ct:
            raise ValueError(f"inconsistent usage receipt: {path.name}")
        response = json.loads((directory / f"response-{pid}.json").read_text())
        response_bytes = json.dumps(response, sort_keys=True, separators=(",", ":")).encode()
        if obj.get("response_sha256") != hashlib.sha256(response_bytes).hexdigest():
            raise ValueError(f"response hash mismatch: {path.name}")
        replay = validate_response(response.get("http_status"), response.get("body"))
        if any(obj.get(k) != v for k, v in replay.items()):
            raise ValueError(f"response evidence differs from receipt: {path.name}")
        actual[pid] = obj
    missing = sorted(set(expected) - set(actual))
    if missing:
        raise ValueError(f"missing {len(missing)} pair receipt(s)")
    return {"schema": SCHEMA, "inventory_sha256": inv_hash, "pair_count": len(actual), "run_token": run_token}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--endpoints", required=True)
    ap.add_argument("--receipt-dir", required=True)
    ap.add_argument("--run-token", required=True)
    args = ap.parse_args()
    if not args.check:
        ap.error("--check is required")
    result = check(args.receipt_dir, args.endpoints, args.run_token)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
