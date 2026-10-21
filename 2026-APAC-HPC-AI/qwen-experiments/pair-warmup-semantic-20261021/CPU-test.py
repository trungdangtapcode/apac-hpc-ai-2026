#!/usr/bin/env python3
"""Focused stdlib adversarial tests; no server, GPU, or scheduler required."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import warmup_semantic as gate

TOKEN = "0123456789abcdef0123456789abcdef"
GOOD = {"choices": [{"message": {"role": "assistant", "content": "hello"}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7}}


def expect_error(fn, contains=None):
    try: fn()
    except (ValueError, FileExistsError, json.JSONDecodeError) as exc:
        if contains and contains not in str(exc): raise AssertionError(str(exc))
    else: raise AssertionError("expected rejection")


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        endpoints = root / "endpoints.tsv"
        endpoints.write_text("prefill-0\thttp://10.0.0.1:3000\t9000\nprefill-1\thttp://10.0.0.2:3000\t9001\ndecode-0\thttp://10.0.0.3:4000\t9100\n")
        digest, pairs, _ = gate.inventory(endpoints)
        assert len(pairs) == 2 and digest
        duplicate = root / "duplicate.tsv"
        duplicate.write_text(endpoints.read_text() + "decode-0\thttp://10.0.0.4:4000\t9101\n")
        expect_error(lambda: gate.inventory(duplicate), "duplicate")

        expect_error(lambda: gate.validate_response(500, GOOD), "200")
        empty = json.loads(json.dumps(GOOD)); empty["choices"][0]["message"]["content"] = " \n"
        expect_error(lambda: gate.validate_response(200, empty), "nonempty")
        bad_usage = json.loads(json.dumps(GOOD)); bad_usage["usage"]["total_tokens"] = 99
        expect_error(lambda: gate.validate_response(200, bad_usage), "inconsistent")
        too_many = json.loads(json.dumps(GOOD)); too_many["usage"]["completion_tokens"] = 9; too_many["usage"]["total_tokens"] = 14
        expect_error(lambda: gate.validate_response(200, too_many), "invalid")

        receipts = root / "receipts"; receipts.mkdir()
        for pair in pairs:
            gate.write_receipt(receipts, endpoints, TOKEN, pair, 200, GOOD)
        assert gate.check(receipts, endpoints, TOKEN)["pair_count"] == 2
        first = receipts / f'receipt-{pairs[0]["pair_id"]}.json'
        duplicate_receipt = receipts / f'receipt-copy-{pairs[0]["pair_id"]}.json'
        duplicate_receipt.write_text(first.read_text())
        expect_error(lambda: gate.check(receipts, endpoints, TOKEN), "duplicate")
        duplicate_receipt.unlink()
        expect_error(lambda: gate.write_receipt(receipts, endpoints, TOKEN, pairs[0], 200, GOOD), "already exists")

        # Recompute semantic evidence from the retained raw JSON, not receipt counts alone.
        body_path = receipts / f'response-{pairs[0]["pair_id"]}.json'
        original = body_path.read_text()
        body = json.loads(original); body["body"]["choices"][0]["message"]["content"] = "edited"
        body_path.write_text(json.dumps(body))
        expect_error(lambda: gate.check(receipts, endpoints, TOKEN), "hash")
        body_path.write_text(original)
        original_receipt = first.read_text()
        obj = json.loads(original_receipt); obj["assistant_chars"] = 99; first.write_text(json.dumps(obj))
        expect_error(lambda: gate.check(receipts, endpoints, TOKEN), "evidence")
        first.write_text(original_receipt)

        # Stale tokens and well-formed but wrong routes must fail closed.
        obj = json.loads(first.read_text()); obj["run_token"] = "f" * 32; first.write_text(json.dumps(obj))
        expect_error(lambda: gate.check(receipts, endpoints, TOKEN), "stale")
        obj["run_token"] = TOKEN; obj["decode"] = "decode-9"; first.write_text(json.dumps(obj))
        expect_error(lambda: gate.check(receipts, endpoints, TOKEN), "route")

        # A remote log may lie; absent receipts still prevent a head-side pass.
        for p in receipts.glob("*.json"): p.unlink()
        (root / "pair-warmup.log").write_text("ALL_PAIRS_WARM\n")
        cp = subprocess.run([sys.executable, str(HERE / "warmup_semantic.py"), "--check",
                             "--endpoints", str(endpoints), "--receipt-dir", str(receipts),
                             "--run-token", TOKEN], text=True, capture_output=True)
        assert cp.returncode != 0 and "missing" in cp.stderr and "ALL_PAIRS_WARM" not in cp.stdout

        # Inventory changes invalidate otherwise valid receipts.
        for pair in pairs: gate.write_receipt(receipts, endpoints, TOKEN, pair, 200, GOOD)
        endpoints.write_text(endpoints.read_text().replace("10.0.0.1", "10.0.0.8"))
        expect_error(lambda: gate.check(receipts, endpoints, TOKEN), "inventory")
    print("PASS: semantic response, route uniqueness, atomic receipts, token/inventory binding, and false-marker rejection")


if __name__ == "__main__": main()
